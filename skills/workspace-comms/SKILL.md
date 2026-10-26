---
name: workspace-comms
description: Gmail, Docs, Drive, Calendar, and multi-channel messaging workflow — use when triaging email, drafting docs, scheduling meetings, or sending chat messages.
---

# Workspace & omnichannel communications

Coordinate email, documents, calendar events, Drive uploads, and chat channels (WhatsApp, Telegram, Discord, Slack, iMessage) safely and without misaddressed messages.

## When to use

Sending or searching Gmail, creating/writing Google Docs, uploading files to Drive, scheduling Calendar meetings, or sending/broadcasting messages across chat channels.

## Procedure

1. **Resolve people & preferences first**:
   - If the user names a person ("email Sarah", "message Ahmed") without an address/handle, call `recall_memory` (`query="<name>"`) to look up their stored contact details and preferred channel. If still unknown, ask — never guess an email address or handle.
2. **Choose the right channel tool**:
   - **Direct Connected Accounts (`cloud_integrations`) — ALWAYS PREFER FIRST**: Check `[CONNECTED ACCOUNTS]` in context (or `cloud_integrations(action="status")`). When connected, execute silently in the background via `email_unread`, `email_search`, `email_send`, `drive_list`, `drive_search`, `drive_upload`, `drive_download`, `calendar_list`, `calendar_add`, `notion_search`, `notion_read`, `notion_create_page`, `notion_append`, `slack_send`, `slack_channels`, `slack_history`, `discord_send`, `discord_read`, `trello_boards`, or `trello_create_card`.
   - **Google Workspace Browser Fallback (`gws_pack`)**: If Google/Email was skipped/ignored in Integrations, or for live Google Docs editing (`docs_create`, `docs_write`, `gws_open`, `workflow`), use `gws_pack`.
   - **Webhook / Bot Channels (`multi_channel`)**: Check active channels via `multi_channel` (`action="channels"`), then `action="send"` (`channel`, `message`, `recipient`) or `action="broadcast"`.
   - **Personal Socials (`social_hub`) — Instagram, Snapchat Web, TikTok, X, WhatsApp Web & Reddit**: Use `social_hub` (`action="check_inbox"`, `"read_messages"`, `"send_message"`, `"post"`, `"feed"`, `"connect"`, `"status"`) to check unread DMs/Snaps/notifications, read & reply to conversations (Instagram extra confirmation is disabled by the deployment preference; other Ask-mode operations use the HUD gate), or control Reels/feeds hands-free.
     - **Open vs inspect**: “open/show my Instagram chats” means `action="open_inbox"` in the HUD, not `check_inbox` (a background digest). Routine social operations must not open an external desktop browser/app.
     - **Identity**: use an exact Instagram @username from the user's request or stored contacts. Never select a partial/display-name match or a group merely containing that person. Ask for the handle if unresolved.
     - **Connection**: `status` distinguishes saved session credentials from live authentication and login/security challenges. Do not call an account disconnected just because one transport failed; use the existing HUD sign-in/session recovery. Never upgrade ReadOnly/Paused or undo Ignore silently.
     - **Instagram execution**: the Instagram messaging engine runs explicit browser, read-only session resolution, native profile/picker, draft, permission/account, single submission and receipt states. Existing exact one-to-one chats are resolved through GET-only session data before relying on a profile Message button or recipient picker. No undocumented write is used by the native engine. Never fall back to another send after any submission attempt.
     - **No extra Instagram prompt**: `config/social_preferences.json` sets `instagram_confirm_send: false` by explicit user request. Do not ask the user to confirm again. ReadOnly/Paused and sender/recipient checks remain mandatory. An administrator can restore the prompt with that setting or `JARVIS_INSTAGRAM_CONFIRM_SEND=1`.
     - **Execution is not delivery**: only a provider acknowledgment establishes accepted submission, not that the recipient read it. Where confirmation remains enabled, `[CONFIRMATION_PENDING]` means nothing has been sent. Never create another send while one is pending. If delivery is unknown, inspect before retrying; never automatically resend.
     - **Failure reporting**: preserve the exact `[IG:state]` and specific reason in the visible transcript, not merely “recipient timeout” or “system problem”. Do not invent login/security problems. Failures write an allowlisted local `instagram_last_failure.json` under the social-session directory with engine version, state history, an allowlisted page-state enum and structural counts; no cookies, usernames, message bodies, URLs, screenshots or raw DOM. The user should not need hidden console logs.
     - **Blocked page, not missing recipient**: a sparse screen is not proof that an inbox loaded. Report only the observed page classification. Known security/PIN/consent/restriction screens require the corresponding user action or waiting; never bypass them or repeatedly retry. Pre-submission failures surface the same failed browser target in the wide HUD for inspection, without navigating away. Do not instruct the user to reopen a different inbox or supply hidden console logs.
     - **Publishing limits**: text-only Instagram posts are unsupported (posts need media). Do not promise a photo/video publish through this text-only action.
   - **Desktop App Messaging (`send_message`)**: Use for native desktop WhatsApp/Telegram automation when requested.
3. **Draft & confirm outbound messages**:
   - Read-only actions (`gmail_search`, `channels`, `docs_create`) run immediately.
   - Before sending an email (`gmail_send`), chat message (`send_message` / `multi_channel` `send`), or `broadcast` to external recipients, state the **recipient**, **channel**, and **1-line gist** aloud (unless the user already dictated the exact message and said "send it now").
4. **Close the loop**: If a message or meeting creates a commitment ("I'll send the deck Friday"), offer or add a follow-up via `manage_tasks` (`action="add"`) or `reminder`.

## Pitfalls

- Never `broadcast` across all channels unless the user explicitly asked to broadcast everywhere.
- Verify local file existence before calling `gws_pack` (`action="drive_upload"`, `file_path=...`).
- Match the message's language and formality to the recipient, not the internal tool schema.

## Verification

Recipient verified? Right channel selected? Outbound commitment announced clearly before dispatch? Any promised follow-up captured?
