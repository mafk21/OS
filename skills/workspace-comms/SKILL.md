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
   - **Personal Socials (`social_hub`) — Instagram, Snapchat Web, TikTok, X, WhatsApp Web & Reddit**: Use `social_hub` (`action="check_inbox"`, `"read_messages"`, `"send_message"`, `"post"`, `"feed"`, `"connect"`, `"status"`) to check unread DMs/Snaps/notifications, read & reply to conversations (automatically guarded by JARVIS's HUD confirmation banner when policy is `ask`), or control Reels/feeds hands-free.
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
