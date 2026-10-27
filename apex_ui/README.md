## JARVIS interface integration

The main screen uses the actual upstream APEX-UI components pinned at
`a8732fad1078a809cadfa810cb0d89cf4445dbed`, under `components/reference/`.
The orb, particle simulation, graph, backdrop, overview, status bar and CSS
are upstream copies, not a humanoid replacement or visual approximation.
`upstream.json` records source hashes; only `reference/ApexWorld.tsx` has a
small transport adapter (controlled state/trace and control-opening callbacks).
The original persona/orb designs remain available; the male humanoid renderer now
also accepts the female asset/palette variant.

- Connected: existing JARVIS state and traces drive the reference visuals.
  Upstream has three visual states; listening maps to its idle appearance.
- Disconnected/design preview: upstream's click-to-cycle animation remains.
  This does not run assistant actions or represent a live voice session.
- Right-click the orb or press **Ctrl+Enter** to open existing typing/system
  controls. Escape closes the command console. No permanent custom toolbar
  or command box is added to the reference layout.
- Existing confirmation, onboarding, social, video and settings dialogs remain
  available when requested. Backend, models, voice settings and safety policies
  are unchanged. The upstream agent descriptions are interface copy, not new
  backend agent implementations.
- The existing Python bridge supplies `/api/weather` in the desktop app.
  A static design-only preview has no weather API or voice connection.
- Run `npm ci && npm run build` here to rebuild the checked-in `static_hud/`
  served by the Python desktop bridge; no Node runtime is needed on the desktop.

Upstream license and community attribution remain in `LICENSE` and `CREDITS.md`.

---

# APEX-UI

An animated **autonomous-agent orb + reasoning-graph** interface — the front-end of
[Apex](https://reznikov-engineering.com/apex), released open source.

Tap the orb to cycle its state (idle → thinking → speaking); the reasoning web reacts,
agent nodes orbit the core, and clicking any node opens an overview card. The orb ring,
agent graph and status bar are **hand-written SVG / CSS**; the cyan particle core is a
small `react-three-fiber` scene (skipped under `prefers-reduced-motion`); and the WebGL
shader backdrop + the overview lamp panel are **MIT community components from
[21st.dev](https://21st.dev/community/components)** (see [CREDITS](./CREDITS.md)).

> ⚠ **The Apex Humanoid is NOT part of this repo.** The particle-figure face of Apex
> (assembly, states, voice-driven energy) lives in a separate repository with its own
> access - what you see here is the orb + reasoning-graph interface only.

> Built with Next.js 15 + React 19. Runtime deps: `lucide-react` (icons) and
> `three` / `@react-three/fiber` / `@react-three/postprocessing` (the particle core) —
> all MIT-licensed.

## Live demo

**[apex-ui-xi.vercel.app](https://apex-ui-xi.vercel.app)** - the same code, running.
Tap the orb.

## Run it yourself

```bash
npm install
npm run dev
# open http://localhost:3000
```

Then `npm run build` for a production build, or deploy to Vercel in one click.

## What's inside

| Piece | What it does |
|-------|--------------|
| `ApexOrb` | The golden ring frame, waveform and orbit dots (pure SVG) |
| `ApexCore3D` | The cyan particle core (`react-three-fiber` + bloom) |
| `ApexHeroOrb` | Stacks the SVG ring + the particle core, scaled to fit |
| `ReasoningWeb` | The agent constellation — circuit traces, orbit rings, 18-node roster |
| `OrbStatusBar` | The equalizer + STANDBY cluster along the bottom |
| `ShaderBackground` | Animated WebGL "plasma waves" backdrop (MIT component from 21st.dev — see CREDITS) |
| `ApexWorld` | Composes the above; owns the tap-state cycle and the agent overview cards |
| `ApexOverviewPanel` | Top-left HUD: live clock, weather, and social links |
| `app/api/weather` | Keyless [open-meteo](https://open-meteo.com) proxy for the panel's weather |

## Customise

- **Social links** → edit `TILES` in `components/ApexOverviewPanel.tsx`.
- **Weather** → auto-detects the **visitor's** city on Vercel (geo headers); edit `FALLBACK` in `app/api/weather/route.ts` to change the off-Vercel / localhost default.
- **Agents & copy** → the `ROSTER` and `INFO` maps in `components/ApexWorld.tsx`.
- **Backdrop** → the shader in `components/ShaderBackground.jsx`; its opacity/tint are set where `<ShaderBackground>` is used in `ApexWorld.tsx`.

## Accessibility

The decorative SVG graph is mirrored by a real, keyboard-navigable agent list
(`.visually-hidden`), the orb and every control are focusable, and the whole thing
respects `prefers-reduced-motion`.

## Not included (on purpose)

This repo is the **UI only**. The production Apex page also has a spoken-voice layer and a
"story" narrative — those are personal recordings and private copy, so they are intentionally
left out. The orb stays fully interactive without them.

## License

Code is released under the **[MIT License](./LICENSE)** — use it, fork it, ship it.

The **name "Apex" and the Reznikov Engineering branding are not part of this license.**
If you build on this, please use your own product name and branding.

---

Made by [Ruben Mouradian — Reznikov Engineering](https://reznikov-engineering.com).
If you use it, a link back is appreciated (not required).

## Female counterpart — approved portrait, shared male animation engine

The female edition now uses the exact image approved and uploaded by the user,
normalized with padding to the existing 1020×634 asset canvas (no face redraw).
`female_depth.png` preserves the existing male sculpture's depth/rig channel format,
with a small jaw taper aligned to the approved frontal pose. This is portrait-derived
volumetric particle geometry, not a separately modeled or photorealistic avatar.

`ApexFemaleHumanoid` delegates directly to `ApexMaleHumanoid` with
`appearance="female"`. Assembly/reassembly, shockwave, gaze and head/torso springs,
voice energy, thinking/mood/trace pulses, breathing, orbit/zoom/reset, quality fallback,
sound toggle and reduced-motion behavior therefore run through the same implementation.
Only portrait/depth inputs and the pink/lavender/peach effect palette differ. Male is
the default appearance and keeps its original assets and palette. Asset and geometry
caches are keyed by appearance so switching cannot reuse the other figure's data.

The rejected procedural mask renderer is removed. HUMAN · FEMALE / APEX · ORB
still switches only the visual choice, without changing voice/persona settings.
The full-viewport figure framing now matches the male HUD rather than the old small
central canvas. The surrounding reference layout and graph stay intact.

Validation: `node check-female-geometry.cjs` exercises the real shared builder,
checks finite attributes and verifies appearance cache isolation. Run
`python -m unittest discover -s tests -p 'test_*interface.py'` from the repo root
for shared-engine, asset/export, trace, layout and visual-preference guards.
