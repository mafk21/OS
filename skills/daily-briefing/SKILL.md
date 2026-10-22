---
name: daily-briefing
description: Executive morning or status briefing — use when asked to brief me, catch me up, plan my day, or summarize today's tasks, calendar, weather, and news.
---

# Daily briefing

Deliver a crisp, high-signal executive briefing tailored to the user's location, open commitments, schedule, and watched topics.

## When to use

"Good morning, brief me", "what does my day look like?", "catch me up", "plan my day", or "status briefing".

## Procedure

1. **Load personal context**: Check known identity facts (city, active projects) in memory; if city or project details are under `[ALSO REMEMBERED]`, call `recall_memory` (`query="city projects"`).
2. **Gather live signals (skip any step the user excluded)**:
   - **Schedule**: Call `calendar_heads_up` (`action="check"`) to surface today's events and upcoming Classroom/deadline items.
   - **Tasks**: Call `manage_tasks` (`action="list"`, `status="open"`, `page=1`) and prioritize `urgent` / `high` / due-today items.
   - **Weather**: If a city is known (or supplied), call `weather_report` (`city=<city>`) for live temperature, conditions, and 3-day outlook.
   - **Headlines**: Call `web_search` (`mode="news"`, `query=<user's watched topics or top world/tech news>`).
3. **Rank & compress**:
   - Lead with time-critical items (meetings within 2 hours, urgent tasks due today, severe weather).
   - Group everything else into **Schedule**, **Top 3 Priorities**, **Weather**, and **2–3 Headlines**.
4. **Deliver**: Keep the spoken briefing under ~45 seconds — crisp operator cadence, concrete numbers and times, zero filler. Offer at most one concrete next action (e.g. starting `focus-mode` on the #1 task).

## Pitfalls

- Do not read out a 20-item task list; name the top 3 open priorities and state the remaining count.
- If `city` is unknown for weather, skip `weather_report` or ask in one short clause rather than guessing a random city.
- Never invent calendar events when `google_calendar` is not connected — report task priorities instead.

## Verification

Before speaking: Did you check open tasks and calendar? Are times and temperatures concrete? Is the spoken summary concise rather than a raw dump of tool outputs?
