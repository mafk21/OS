---
name: meeting-copilot
description: Live lecture or meeting capture to action items — use when recording notes, summarizing a class or call, extracting tasks, or drafting follow-up notes.
---

# Meeting & lecture copilot

Capture live lectures, standups, or meetings and turn raw transcripts into structured summaries, decisions, tasks, and deadline reminders.

## When to use

"Start lecture notes", "take meeting notes", "stop the notes and summarize", "turn these meeting notes into action items", or "send out the meeting recap".

## Procedure

1. **Start capture cleanly**:
   - When the session begins, call `manage_lecture` (`action="start"`, `title="<course or meeting name>"`).
   - As key points or user annotations arrive mid-session, append them with `manage_lecture` (`action="append"`, `text=...`). Check progress anytime via `action="status"`.
2. **Stop & synthesize**:
   - When the user says "stop the notes" or the meeting ends, call `manage_lecture` (`action="stop"`, `summarize=True`).
   - Structure the takeaways into three crisp buckets: **Key Decisions / Concepts**, **Open Questions**, and **Action Items / Homework (Owner + Deadline)**.
3. **Materialize commitments**:
   - Save each concrete homework item or user-owned action item into the Tasks DB via `manage_tasks` (`action="add"`, `title=...`, `due=...`, `priority="high"` for near deadlines).
   - For hard time-bound deadlines, offer or schedule an OS notification via `reminder`.
4. **Distribute if requested**:
   - If the user asks to share the recap, follow the `workspace-comms` pattern (`gws_pack` `workflow="send_meeting_notes"` or `docs_create` + `gmail_send`).

## Pitfalls

- Do not create duplicate tasks if the same action item was mentioned twice in the transcript — deduplicate before calling `manage_tasks`.
- Keep the spoken summary to the 3–5 headline takeaways; full notes belong in the saved note (`manage_notes`) and HUD panel.

## Verification

Lecture session cleanly stopped (`status` inactive)? Summary saved to Notes? Every concrete deadline converted into a deduplicated task?
