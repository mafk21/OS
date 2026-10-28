# JARVIS Private Web Call

JARVIS can ring a paired phone or browser over the internet without a telephone number or per-minute carrier fee. The call portal is a Progressive Web App hosted on Vercel Hobby with Supabase persistence and standards-based Web Push.

## What it does

- rings paired devices with a persistent Web Push notification;
- lets the user answer or decline;
- speaks JARVIS messages using the device speech engine;
- accepts spoken replies through browser speech recognition, with typed fallback;
- supports immediate calls, configured important alerts, and restart-safe scheduled calls through the host OS scheduler;
- supports call status, follow-up messages, and explicit call ending.

This is an internet voice conversation, not a PSTN/mobile-number call. Browser speech recognition support varies. Push delivery depends on the device/browser notification settings and the free hosting service remaining within its quota.

## Setup

1. Open the deployed call portal on the device that should ring.
2. Enter the private pairing code generated during deployment.
3. Select **Enable Calls** and grant notification permission.
4. On iPhone/iPad, add the site to the Home Screen and enable notifications for the installed web app. Android and desktop Chrome/Edge can register directly.
5. Keep `config/web_call.json` private. It contains the sender credential and is ignored by Git.

Use JARVIS commands such as:

- “Call me and tell me the report is finished.”
- “Call me tomorrow at 8:30 AM and remind me to leave.”
- “Check whether I answered the last call.”

## Permission policy

Calls are allowed only when explicitly requested, for user-configured important alerts, or for user-created schedules. Proactive alert calls must pass Soul quiet-hours, snooze, interruption-budget, and confirmation rules. The call tool does not grant itself broader initiative.

## Security

- Supabase tables have RLS enabled and grant no browser role direct access.
- Server-side access uses a sensitive service credential stored only in Vercel environment variables.
- Device registration requires a high-entropy pairing code.
- JARVIS sender operations require a separate high-entropy bearer secret.
- Credentials are compared in constant time and are never committed.
- Call message bodies are bounded to 2,000 characters.
- Dead push subscriptions are removed after provider 404/410 responses.

To revoke all devices, rotate `PAIRING_CODE`. To revoke JARVIS send access, rotate `CALL_SECRET` in Vercel and the local ignored config. Individual call records can be removed from the `jarvis_call_*` tables.

## Free-tier limits

The site uses free Vercel Hobby and the connected Supabase project. It does not incur telephone charges, but it is subject to each provider’s free-tier quotas and policies. It deliberately makes no claim of unlimited or permanent free hosting.
