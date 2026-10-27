"use client";

import ApexMaleHumanoid from "./ApexMaleHumanoid";
import type { OrbState } from "./ApexHeroOrb";
import type { TraceEvent } from "./JarvisBridge";

/** Same renderer, rig, physics, assembly, audio and controls as the male edition. */
export default function ApexFemaleHumanoid({ state, trace = null, reducedMotion = false, pulseSignal = 0, constellationVisible = false, onToggleConstellation }: {
  state: OrbState;
  trace?: TraceEvent | null;
  reducedMotion?: boolean;
  pulseSignal?: number;
  constellationVisible?: boolean;
  onToggleConstellation?: () => void;
}) {
  return <ApexMaleHumanoid key="female" appearance="female" state={state}
    trace={trace} reducedMotion={reducedMotion} pulseSignal={pulseSignal} constellationVisible={constellationVisible} onToggleConstellation={onToggleConstellation} />;
}
