"""
actions/cloud_integrations.py — Direct background APIs for connected user accounts.

Executes real, zero-browser background API requests for every optional account
the user connected during first-run setup (or later in HUD -> Integrations):
  • Email / Gmail  (Gmail REST API v1 OR IMAP/SMTP App Password)
  • Google Drive   (Drive REST API v3: list, search, upload, download/export)
  • Google Calendar(Calendar REST API v3: upcoming events, natural quickAdd)
  • Notion         (Notion REST API 2022-06-28: search, read, create/append page)
  • Slack          (Slack Web API + Incoming Webhooks: channels, history, send)
  • Discord        (Discord Webhooks + Bot REST API v10: send, read channel)
  • Trello         (Trello REST API: boards, lists, create card)

Services the user chose to skip/ignore return a clear, polite message without
crashing, and work identically across both the Male and Female interface editions.
"""

from __future__ import annotations

import urllib.parse
from typing import Any

import memory.accounts as ac


def _notion_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }


def _notion_search(query: str = "") -> str:
    rec = ac.get_account("notion")
    if not rec or not rec.get("token") or rec.get("ignored"):
        return "Notion is not connected (skipped/ignored). Connect a Notion token in HUD -> Integrations."
    body: dict[str, Any] = {"page_size": 10}
    if query.strip():
        body["query"] = query.strip()
    res = ac._http_json(
        "https://api.notion.com/v1/search",
        method="POST",
        headers=_notion_headers(rec["token"]),
        payload=body,
    )
    items = res.get("results") or []
    if not items:
        return f"No Notion pages or databases matched '{query}'."
    lines = [f"Notion results ({len(items)}):"]
    for it in items:
        obj = it.get("object", "page")
        pid = it.get("id", "")
        title = ""
        if obj == "database":
            t_arr = it.get("title") or []
            title = "".join(x.get("plain_text", "") for x in t_arr)
        else:
            props = it.get("properties") or {}
            for pv in props.values():
                if isinstance(pv, dict) and pv.get("type") == "title":
                    title = "".join(x.get("plain_text", "") for x in (pv.get("title") or []))
                    break
        lines.append(f"  • [{obj}] {title or '(Untitled)'} — id={pid} {it.get('url', '')}")
    return "\n".join(lines)


def _notion_read(page_id: str) -> str:
    rec = ac.get_account("notion")
    if not rec or not rec.get("token") or rec.get("ignored"):
        return "Notion is not connected. Add your Notion token in HUD -> Integrations."
    pid = page_id.strip().replace("-", "")
    if not pid:
        return "Provide 'page_id' to read a Notion page."
    res = ac._http_json(
        f"https://api.notion.com/v1/blocks/{pid}/children?page_size=50",
        headers=_notion_headers(rec["token"]),
    )
    lines = []
    for blk in res.get("results") or []:
        btype = blk.get("type", "")
        bdata = blk.get(btype) if isinstance(blk.get(btype), dict) else {}
        rt = bdata.get("rich_text") or []
        txt = "".join(x.get("plain_text", "") for x in rt).strip()
        if txt:
            lines.append(f"- {txt}" if "list_item" in btype else txt)
    return "\n".join(lines) if lines else "Notion page has no readable text blocks."


def _notion_create_or_append(title: str, content: str, page_id: str = "") -> str:
    rec = ac.get_account("notion")
    if not rec or not rec.get("token") or rec.get("ignored"):
        return "Notion is not connected. Add your Notion token in HUD -> Integrations."
    target_parent = (page_id or rec.get("parent_page_id") or "").strip()
    paragraphs = [
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": chunk[:1900]}}]
            },
        }
        for chunk in (content or title or "").split("\n\n")
        if chunk.strip()
    ]
    if not target_parent:
        # Search first accessible page to use as parent if none provided
        sr = ac._http_json(
            "https://api.notion.com/v1/search",
            method="POST",
            headers=_notion_headers(rec["token"]),
            payload={"page_size": 1, "filter": {"property": "object", "value": "page"}},
        )
        results = sr.get("results") or []
        if not results:
            return "Share at least one Notion page with your Notion integration first, or pass 'page_id'."
        target_parent = results[0]["id"]

    if title.strip():
        created = ac._http_json(
            "https://api.notion.com/v1/pages",
            method="POST",
            headers=_notion_headers(rec["token"]),
            payload={
                "parent": {"page_id": target_parent},
                "properties": {
                    "title": {"title": [{"text": {"content": title.strip()}}]}
                },
                "children": paragraphs[:20],
            },
        )
        return f"Created Notion page '{title}': {created.get('url', created.get('id', ''))}"

    ac._http_json(
        f"https://api.notion.com/v1/blocks/{target_parent}/children",
        method="PATCH",
        headers=_notion_headers(rec["token"]),
        payload={"children": paragraphs[:20]},
    )
    return f"Appended {len(paragraphs)} block(s) to Notion page {target_parent}."


def _slack_action(action: str, params: dict) -> str:
    rec = ac.get_account("slack")
    if not rec or rec.get("ignored") or not (rec.get("token") or rec.get("webhook_url")):
        return "Slack is not connected (skipped/ignored). Connect Slack in HUD -> Integrations."
    tok = str(rec.get("token") or "").strip()
    wh = str(rec.get("webhook_url") or "").strip()
    channel = str(params.get("channel") or rec.get("default_channel") or "").strip()
    text = str(params.get("body") or params.get("content") or params.get("text") or "").strip()

    if action == "slack_send":
        if not text:
            return "Provide message 'body' or 'text' to send to Slack."
        if wh and not channel:
            ac._http_json(wh, method="POST", payload={"text": text})
            return "Sent message to Slack via webhook."
        if not tok:
            if wh:
                ac._http_json(wh, method="POST", payload={"text": text})
                return "Sent message to Slack via webhook."
            return "Slack bot/user token required to target a specific channel."
        if not channel:
            return "Provide Slack 'channel' (name or ID) or set a default channel in Integrations."
        # Resolve #channel-name to ID if needed
        ch_id = channel.lstrip("#")
        if not (ch_id.startswith("C") or ch_id.startswith("D") or ch_id.startswith("G")):
            clist = ac._http_json(
                "https://slack.com/api/conversations.list?types=public_channel,private_channel&limit=200",
                headers={"Authorization": f"Bearer {tok}"},
            )
            for c in clist.get("channels") or []:
                if c.get("name", "").lower() == ch_id.lower():
                    ch_id = c["id"]
                    break
        res = ac._http_json(
            "https://slack.com/api/chat.postMessage",
            method="POST",
            headers={"Authorization": f"Bearer {tok}"},
            payload={"channel": ch_id, "text": text},
        )
        if not res.get("ok"):
            return f"Slack error: {res.get('error', 'unknown')}"
        return f"Posted to Slack ({channel})."

    if not tok:
        return "Listing or reading Slack channels requires a Slack Bot/User Token (xoxb-...)."

    if action == "slack_channels":
        res = ac._http_json(
            "https://slack.com/api/conversations.list?types=public_channel,private_channel&limit=40",
            headers={"Authorization": f"Bearer {tok}"},
        )
        if not res.get("ok"):
            return f"Slack error: {res.get('error', 'unknown')}"
        chs = res.get("channels") or []
        return "Slack channels:\n" + "\n".join(
            f"  • #{c.get('name')} ({c.get('id')})" for c in chs[:25]
        )

    if action == "slack_history":
        if not channel:
            return "Specify Slack 'channel' ID or name."
        q = urllib.parse.urlencode({"channel": channel, "limit": 10})
        res = ac._http_json(
            f"https://slack.com/api/conversations.history?{q}",
            headers={"Authorization": f"Bearer {tok}"},
        )
        if not res.get("ok"):
            return f"Slack error: {res.get('error', 'unknown')}"
        msgs = res.get("messages") or []
        return "Recent Slack messages:\n" + "\n".join(
            f"  • {m.get('user', 'bot')}: {m.get('text', '')[:160]}" for m in msgs
        )
    return f"Unknown Slack action: {action}"


def _discord_action(action: str, params: dict) -> str:
    rec = ac.get_account("discord")
    if not rec or rec.get("ignored") or not (rec.get("token") or rec.get("webhook_url")):
        return "Discord is not connected (skipped/ignored). Connect Discord in HUD -> Integrations."
    tok = str(rec.get("token") or "").strip()
    wh = str(rec.get("webhook_url") or "").strip()
    ch_id = str(params.get("channel") or rec.get("channel_id") or "").strip()
    text = str(params.get("body") or params.get("content") or params.get("text") or "").strip()

    if action == "discord_send":
        if not text:
            return "Provide message 'body' or 'text' to send to Discord."
        if wh and not ch_id:
            ac._http_json(
                wh,
                method="POST",
                headers={"User-Agent": "JARVIS-OS/1.0"},
                payload={"content": text[:1990]},
            )
            return "Sent message to Discord via webhook."
        if tok and ch_id:
            ac._http_json(
                f"https://discord.com/api/v10/channels/{ch_id}/messages",
                method="POST",
                headers={
                    "Authorization": f"Bot {tok}",
                    "User-Agent": "JARVIS-OS/1.0",
                },
                payload={"content": text[:1990]},
            )
            return f"Sent message to Discord channel {ch_id}."
        if wh:
            ac._http_json(
                wh,
                method="POST",
                headers={"User-Agent": "JARVIS-OS/1.0"},
                payload={"content": text[:1990]},
            )
            return "Sent message to Discord via webhook."
        return "Provide Discord 'channel' ID (with Bot Token) or configure a Discord Webhook URL."

    if action == "discord_read":
        if not (tok and ch_id):
            return "Reading Discord messages requires a Bot Token and 'channel' ID."
        msgs = ac._http_json(
            f"https://discord.com/api/v10/channels/{ch_id}/messages?limit=10",
            headers={
                "Authorization": f"Bot {tok}",
                "User-Agent": "JARVIS-OS/1.0",
            },
        )
        if not isinstance(msgs, list) or not msgs:
            return "No recent Discord messages found."
        return "Recent Discord messages:\n" + "\n".join(
            f"  • {(m.get('author') or {}).get('username', 'user')}: {m.get('content', '')[:160]}"
            for m in msgs
        )
    return f"Unknown Discord action: {action}"


def _trello_action(action: str, params: dict) -> str:
    rec = ac.get_account("trello")
    if not rec or rec.get("ignored") or not (rec.get("api_key") and rec.get("token")):
        return "Trello is not connected (skipped/ignored). Connect Trello in HUD -> Integrations."
    auth = urllib.parse.urlencode({"key": rec["api_key"], "token": rec["token"]})
    if action == "trello_boards":
        boards = ac._http_json(f"https://api.trello.com/1/members/me/boards?fields=name,url&{auth}")
        if not boards:
            return "No Trello boards found."
        return "Trello boards:\n" + "\n".join(
            f"  • {b.get('name')} (id={b.get('id')}) {b.get('url', '')}" for b in boards[:15]
        )
    if action == "trello_create_card":
        list_id = str(params.get("list_id") or "").strip()
        title = str(params.get("title") or "").strip()
        desc = str(params.get("body") or params.get("description") or "").strip()
        if not list_id or not title:
            return "Provide Trello 'list_id' and card 'title'."
        q = urllib.parse.urlencode(
            {"key": rec["api_key"], "token": rec["token"], "idList": list_id, "name": title, "desc": desc}
        )
        card = ac._http_json(f"https://api.trello.com/1/cards?{q}", method="POST")
        return f"Created Trello card '{title}': {card.get('shortUrl', card.get('id', ''))}"
    return f"Unknown Trello action: {action}"


def _linear_action(action: str, params: dict) -> str:
    rec = ac.get_account("linear")
    tok = (rec or {}).get("token") or (rec or {}).get("api_key") or ""
    if not rec or rec.get("ignored") or not tok:
        return "Linear is not connected (skipped/ignored). Connect Linear in HUD -> Integrations."
    headers = {"Authorization": tok, "Content-Type": "application/json"}
    if action == "linear_issues":
        q = (
            '{"query":"{ issues(first: 12) { nodes { identifier title state { name } url } } }"}'
        )
        res = ac._http_json(
            "https://api.linear.app/graphql",
            method="POST",
            headers=headers,
            raw_body=q.encode("utf-8"),
        )
        nodes = (((res.get("data") or {}).get("issues") or {}).get("nodes")) or []
        if not nodes:
            return "No Linear issues found."
        return "Linear issues:\n" + "\n".join(
            f"  • [{n.get('identifier')}] {n.get('title')} ({(n.get('state') or {}).get('name', '')}) {n.get('url', '')}"
            for n in nodes
        )
    if action == "linear_create_issue":
        title = str(params.get("title") or "").strip()
        desc = str(params.get("body") or params.get("content") or "").strip()
        team_id = str(params.get("team_id") or rec.get("team_id") or "").strip()
        if not title or not team_id:
            return "Provide Linear issue 'title' and 'team_id'."
        gql = {
            "query": (
                "mutation($input: IssueCreateInput!) { "
                "issueCreate(input: $input) { success issue { identifier title url } } }"
            ),
            "variables": {"input": {"teamId": team_id, "title": title, "description": desc}},
        }
        res = ac._http_json(
            "https://api.linear.app/graphql", method="POST", headers=headers, payload=gql
        )
        iss = (((res.get("data") or {}).get("issueCreate") or {}).get("issue")) or {}
        return f"Created Linear issue [{iss.get('identifier', 'NEW')}] {title}: {iss.get('url', '')}"
    return f"Unknown Linear action: {action}"


def _outlook_action(action: str, params: dict) -> str:
    rec = ac.get_account("outlook")
    tok = (rec or {}).get("token") or ""
    if not rec or rec.get("ignored") or not tok:
        return "Microsoft Outlook / Graph is not connected. Add a Graph Bearer token in HUD -> Integrations."
    headers = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
    if action == "outlook_unread":
        res = ac._http_json(
            "https://graph.microsoft.com/v1.0/me/mailFolders/inbox/messages?$filter=isRead%20eq%20false&$top=10",
            headers=headers,
        )
        msgs = res.get("value") or []
        if not msgs:
            return "No unread Outlook messages."
        return "Unread Outlook messages:\n" + "\n".join(
            f"  • {m.get('subject', '(No subject)')} — from {(((m.get('from') or {}).get('emailAddress')) or {}).get('address', '')}"
            for m in msgs
        )
    if action == "outlook_calendar":
        res = ac._http_json(
            "https://graph.microsoft.com/v1.0/me/events?$top=10",
            headers=headers,
        )
        evs = res.get("value") or []
        if not evs:
            return "No upcoming Outlook Calendar events."
        return "Outlook Calendar events:\n" + "\n".join(
            f"  • {e.get('subject', '(Untitled)')} @ {(e.get('start') or {}).get('dateTime', '')}"
            for e in evs
        )
    if action == "outlook_send":
        to_addr = str(params.get("to") or "").strip()
        subj = str(params.get("subject") or "").strip()
        body = str(params.get("body") or params.get("content") or "").strip()
        if not to_addr or not subj:
            return "Provide 'to' and 'subject' for outlook_send."
        payload = {
            "message": {
                "subject": subj,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": to_addr}}],
            }
        }
        ac._http_json(
            "https://graph.microsoft.com/v1.0/me/sendMail",
            method="POST",
            headers=headers,
            payload=payload,
        )
        return f"Sent Outlook email to {to_addr}: '{subj}'."
    return f"Unknown Outlook action: {action}"


def _dropbox_action(action: str, params: dict) -> str:
    rec = ac.get_account("dropbox")
    tok = (rec or {}).get("token") or ""
    if not rec or rec.get("ignored") or not tok:
        return "Dropbox is not connected. Add a Dropbox access token in HUD -> Integrations."
    headers = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json"}
    if action == "dropbox_list":
        res = ac._http_json(
            "https://api.dropboxapi.com/2/files/list_folder",
            method="POST",
            headers=headers,
            payload={"path": str(params.get("query") or ""), "limit": 20},
        )
        entries = res.get("entries") or []
        if not entries:
            return "Dropbox folder is empty."
        return "Dropbox files:\n" + "\n".join(
            f"  • [{e.get('.tag', 'file')}] {e.get('name')} ({e.get('path_display', '')})"
            for e in entries
        )
    if action == "dropbox_search":
        q = str(params.get("query") or "").strip()
        if not q:
            return "Provide 'query' for dropbox_search."
        res = ac._http_json(
            "https://api.dropboxapi.com/2/files/search_v2",
            method="POST",
            headers=headers,
            payload={"query": q},
        )
        matches = res.get("matches") or []
        if not matches:
            return f"No Dropbox files matched '{q}'."
        return "Dropbox search results:\n" + "\n".join(
            f"  • {(((m.get('metadata') or {}).get('metadata')) or {}).get('path_display', '')}"
            for m in matches[:15]
        )
    return f"Unknown Dropbox action: {action}"


def _hubspot_action(action: str, _params: dict) -> str:
    rec = ac.get_account("hubspot")
    tok = (rec or {}).get("token") or (rec or {}).get("api_key") or ""
    if not rec or rec.get("ignored") or not tok:
        return "HubSpot is not connected. Add a HubSpot Private App token in HUD -> Integrations."
    headers = {"Authorization": f"Bearer {tok}"}
    if action == "hubspot_contacts":
        res = ac._http_json(
            "https://api.hubapi.com/crm/v3/objects/contacts?limit=12&properties=firstname,lastname,email",
            headers=headers,
        )
        rows = res.get("results") or []
        if not rows:
            return "No HubSpot contacts found."
        return "HubSpot contacts:\n" + "\n".join(
            f"  • {(r.get('properties') or {}).get('firstname', '')} {(r.get('properties') or {}).get('lastname', '')} <{(r.get('properties') or {}).get('email', '')}>"
            for r in rows
        )
    if action == "hubspot_deals":
        res = ac._http_json(
            "https://api.hubapi.com/crm/v3/objects/deals?limit=12&properties=dealname,amount,dealstage",
            headers=headers,
        )
        rows = res.get("results") or []
        if not rows:
            return "No HubSpot deals found."
        return "HubSpot deals:\n" + "\n".join(
            f"  • {(r.get('properties') or {}).get('dealname', '(Deal)')} — amount={(r.get('properties') or {}).get('amount', '0')} stage={(r.get('properties') or {}).get('dealstage', '')}"
            for r in rows
        )
    return f"Unknown HubSpot action: {action}"


def _calendly_action(action: str, _params: dict) -> str:
    rec = ac.get_account("calendly")
    tok = (rec or {}).get("token") or ""
    if not rec or rec.get("ignored") or not tok:
        return "Calendly is not connected. Add a Calendly Personal Access Token in HUD -> Integrations."
    headers = {"Authorization": f"Bearer {tok}"}
    if action == "calendly_events":
        me = ac._http_json("https://api.calendly.com/users/me", headers=headers)
        user_uri = ((me.get("resource") or {}).get("uri")) or ""
        q = urllib.parse.urlencode({"user": user_uri, "status": "active", "count": 10})
        evs = ac._http_json(f"https://api.calendly.com/scheduled_events?{q}", headers=headers)
        items = evs.get("collection") or []
        if not items:
            return "No active Calendly scheduled events."
        return "Calendly scheduled events:\n" + "\n".join(
            f"  • {e.get('name', 'Meeting')} @ {e.get('start_time', '')}" for e in items
        )
    return f"Unknown Calendly action: {action}"


def cloud_integrations(parameters: dict, player=None, **_kwargs) -> str:
    params = parameters or {}
    action = str(params.get("action") or "status").strip().lower()

    try:
        if action == "status":
            s = ac.get_integrations_status_summary()
            lines = ["Connected & Optional Integrations:"]
            for svc, info in s["services"].items():
                state = (
                    f"✓ CONNECTED ({info['email']})"
                    if info["connected"] and info["email"]
                    else "✓ CONNECTED"
                    if info["connected"]
                    else "— IGNORED"
                    if info["ignored"]
                    else "○ NOT CONFIGURED"
                )
                lines.append(f"  • {svc}: {state}")
            out = "\n".join(lines)
            if player:
                player.show_content("INTEGRATIONS", out)
            return out

        if action in ("email_unread", "email_search"):
            q = "is:unread" if action == "email_unread" else str(params.get("query") or "is:unread")
            msgs = ac.email_search_messages(q, max_results=int(params.get("limit") or 8))
            if not msgs:
                return f"No emails matched '{q}'."
            lines = [f"Emails ({len(msgs)}):"]
            for m in msgs:
                lines.append(
                    f"  • {m['subject']} — From: {m['from']} ({m['date']})\n"
                    f"    {m['snippet']}"
                )
            out = "\n".join(lines)
            if player:
                player.show_content("EMAIL", out)
            return out

        if action == "email_send":
            to = str(params.get("to") or "").strip()
            subj = str(params.get("subject") or "").strip()
            body = str(params.get("body") or params.get("content") or "").strip()
            attach = str(params.get("file_path") or "").strip()
            if not to:
                return "Specify recipient 'to' email address."
            return ac.email_send_message(to, subj, body, attachment_path=attach)

        if action in ("drive_list", "drive_search"):
            q = str(params.get("query") or "").strip()
            files = ac.drive_list_files(q, max_results=int(params.get("limit") or 12))
            if not files:
                return "No matching files found in Google Drive."
            lines = [f"Google Drive files ({len(files)}):"]
            for f in files:
                lines.append(
                    f"  • {f.get('name')} [id={f.get('id')}] ({f.get('mimeType', '')}) "
                    f"{f.get('webViewLink', '')}"
                )
            out = "\n".join(lines)
            if player:
                player.show_content("GOOGLE DRIVE", out)
            return out

        if action == "drive_upload":
            fp = str(params.get("file_path") or "").strip()
            if not fp:
                return "Provide local 'file_path' to upload to Google Drive."
            up = ac.drive_upload_file(fp, folder_id=str(params.get("folder_id") or ""))
            return f"Uploaded '{up.get('name')}' to Google Drive: {up.get('webViewLink', up.get('id', ''))}"

        if action == "drive_download":
            fid = str(params.get("file_id") or "").strip()
            dest = str(params.get("destination") or "downloads").strip()
            if not fid:
                return "Provide Google Drive 'file_id' to download."
            saved = ac.drive_download_file(fid, destination=dest)
            return f"Downloaded from Google Drive to: {saved}"

        if action == "calendar_list":
            evs = ac.calendar_events_today(max_results=int(params.get("limit") or 10))
            if not evs:
                return "No upcoming Google Calendar events found (or Calendar not connected)."
            lines = ["Upcoming Google Calendar events:"]
            for ev in evs:
                lines.append(f"  • {ev['title']} @ {ev['start']}")
            out = "\n".join(lines)
            if player:
                player.show_content("CALENDAR", out)
            return out

        if action == "calendar_add":
            title = str(params.get("title") or "").strip()
            when = str(params.get("when") or "").strip()
            phrase = f"{title} {when}".strip()
            if not phrase:
                return "Provide event 'title' and 'when'."
            ev = ac.calendar_quick_add(phrase)
            return f"Added Google Calendar event '{ev.get('summary', title)}': {ev.get('htmlLink', 'scheduled')}"

        if action == "notion_search":
            return _notion_search(str(params.get("query") or ""))
        if action == "notion_read":
            return _notion_read(str(params.get("page_id") or ""))
        if action in ("notion_create_page", "notion_append"):
            return _notion_create_or_append(
                title=str(params.get("title") or "") if action == "notion_create_page" else "",
                content=str(params.get("body") or params.get("content") or ""),
                page_id=str(params.get("page_id") or ""),
            )

        if action.startswith("slack_"):
            return _slack_action(action, params)

        if action.startswith("discord_"):
            return _discord_action(action, params)

        if action.startswith("trello_"):
            return _trello_action(action, params)

        if action.startswith("linear_"):
            return _linear_action(action, params)

        if action.startswith("outlook_"):
            return _outlook_action(action, params)

        if action.startswith("dropbox_"):
            return _dropbox_action(action, params)

        if action.startswith("hubspot_"):
            return _hubspot_action(action, params)

        if action.startswith("calendly_"):
            return _calendly_action(action, params)

        return (
            f"Unknown action '{action}'. Available: status, email_unread, email_search, "
            "email_send, drive_list, drive_search, drive_upload, drive_download, "
            "calendar_list, calendar_add, notion_search, notion_read, notion_create_page, "
            "notion_append, slack_send, slack_channels, slack_history, discord_send, "
            "discord_read, trello_boards, trello_create_card, linear_issues, linear_create_issue, "
            "outlook_unread, outlook_calendar, outlook_send, dropbox_list, dropbox_search, "
            "hubspot_contacts, hubspot_deals, calendly_events."
        )
    except Exception as exc:
        return f"Integration error ({action}): {exc}"


TOOL = {
    "name": "cloud_integrations",
    "description": (
        "Direct background API access to the user's connected cloud & messaging accounts "
        "(Email/Gmail, Google Drive, Google Calendar, Notion, Slack, Discord, Trello). "
        "Works identically in Male and Female editions without opening a browser. "
        "Actions: status, email_unread, email_search, email_send, drive_list, drive_search, "
        "drive_upload, drive_download, calendar_list, calendar_add, notion_search, notion_read, "
        "notion_create_page, notion_append, slack_send, slack_channels, slack_history, "
        "discord_send, discord_read, trello_boards, trello_create_card."
    ),
    "behavior": "NON_BLOCKING",
    "scheduling": "WHEN_IDLE",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "action": {
                "type": "STRING",
                "description": (
                    "status | email_unread | email_search | email_send | "
                    "drive_list | drive_search | drive_upload | drive_download | "
                    "calendar_list | calendar_add | notion_search | notion_read | "
                    "notion_create_page | notion_append | slack_send | slack_channels | "
                    "slack_history | discord_send | discord_read | trello_boards | trello_create_card"
                ),
            },
            "query": {"type": "STRING", "description": "Search query for email, Drive, or Notion"},
            "to": {"type": "STRING", "description": "Recipient email address for email_send"},
            "subject": {"type": "STRING", "description": "Email subject"},
            "title": {"type": "STRING", "description": "Event, Notion page, or Trello card title"},
            "body": {"type": "STRING", "description": "Message, email, or page body content"},
            "content": {"type": "STRING", "description": "Alias for body"},
            "when": {"type": "STRING", "description": "Date/time phrase for calendar_add (e.g. 'tomorrow at 3pm')"},
            "file_path": {"type": "STRING", "description": "Local file path for drive_upload or email attachment"},
            "file_id": {"type": "STRING", "description": "Google Drive file ID for drive_download"},
            "folder_id": {"type": "STRING", "description": "Optional Google Drive destination folder ID"},
            "destination": {"type": "STRING", "description": "Local folder for drive_download (default: 'downloads')"},
            "page_id": {"type": "STRING", "description": "Notion page ID"},
            "channel": {"type": "STRING", "description": "Slack channel (#name or ID) or Discord channel ID"},
            "list_id": {"type": "STRING", "description": "Trello list ID for trello_create_card"},
            "limit": {"type": "INTEGER", "description": "Maximum items to return"},
        },
        "required": ["action"],
    },
    "handler": cloud_integrations,
}
