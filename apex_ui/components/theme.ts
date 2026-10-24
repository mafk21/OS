export type PersonaMode = "male" | "female";

export type PersonaTheme = {
  id: PersonaMode;
  label: string;
  shortLabel: string;
  badge: string;
  subtitle: string;
  defaultVoice: string;
  voiceHint: string;
  primary: string;
  primaryBright: string;
  primarySoftBg: string;
  primaryBorder: string;
  filamentLine: string;
  filamentDot: string;
  filamentTextRgb: string;
  secondary: string;
  secondaryBright: string;
  secondarySoftBg: string;
  toolNode: string;
  ringLine: string;
  pcbDot: string;
  fieldMesh: string;
  fieldDot: string;
  mesh: string;
  spoke: string;
  spokeHot: string;
  mote: string;
  moteHot: string;
  coLink: string;
  worldBg: string;
  pageBg: string;
  panelBg: string;
  drawerBg: string;
  barBg: string;
  inputBg: string;
  tileBg: string;
  orbGlowRgb: string;
  orbGlow2Rgb: string;
  femaleMix: number; // 0 = male cyan/gold shader, 1 = female rose/orchid shader
};

export const PERSONA_THEMES: Record<PersonaMode, PersonaTheme> = {
  male: {
    id: "male",
    label: "MALE EDITION",
    shortLabel: "MALE",
    badge: "CYAN · STARK GOLD",
    subtitle: "Electric cyan particle core, warm gold orbital rings & deep baritone voice.",
    defaultVoice: "Charon",
    voiceHint: "Charon · Deep & Calm",
    primary: "#00e5ff",
    primaryBright: "#c8f7ff",
    primarySoftBg: "rgba(0, 229, 255, 0.08)",
    primaryBorder: "rgba(0, 229, 255, 0.28)",
    filamentLine: "#a5f3fc",
    filamentDot: "#e0fbff",
    filamentTextRgb: "165, 243, 252",
    secondary: "#f5a623",
    secondaryBright: "#ffd080",
    secondarySoftBg: "rgba(245, 166, 35, 0.09)",
    toolNode: "#7f9bb3",
    ringLine: "#1b5f78",
    pcbDot: "#37d6ef",
    fieldMesh: "#143f4f",
    fieldDot: "#2bd0e6",
    mesh: "#1a5468",
    spoke: "#22566b",
    spokeHot: "#33eaff",
    mote: "#5fe0f2",
    moteHot: "#bff6ff",
    coLink: "#5eead4",
    worldBg:
      "radial-gradient(ellipse 95% 88% at 50% 42%, #122c43 0%, #0c1d30 38%, #07111f 72%, #050b14 100%)",
    pageBg: "#04080f",
    panelBg: "rgba(5, 11, 22, 0.96)",
    drawerBg: "rgba(4, 9, 18, 0.88)",
    barBg: "rgba(4, 10, 20, 0.74)",
    inputBg: "rgba(10, 20, 36, 0.92)",
    tileBg: "rgba(6, 14, 26, 0.78)",
    orbGlowRgb: "13, 210, 255",
    orbGlow2Rgb: "13, 170, 228",
    femaleMix: 0,
  },
  female: {
    id: "female",
    label: "FEMALE EDITION",
    shortLabel: "FEMALE",
    badge: "ROSE · ORCHID AMETHYST",
    subtitle: "Luminous rose-magenta particle core, orchid-violet rings & natural female voice.",
    defaultVoice: "Aoede",
    voiceHint: "Aoede · Warm & Articulate",
    primary: "#ff4db8",
    primaryBright: "#ffd6f3",
    primarySoftBg: "rgba(255, 77, 184, 0.09)",
    primaryBorder: "rgba(255, 77, 184, 0.30)",
    filamentLine: "#fbcfe8",
    filamentDot: "#fff0f8",
    filamentTextRgb: "251, 207, 232",
    secondary: "#c084fc",
    secondaryBright: "#f3d4ff",
    secondarySoftBg: "rgba(192, 132, 252, 0.10)",
    toolNode: "#b39ddb",
    ringLine: "#69275c",
    pcbDot: "#ff73cb",
    fieldMesh: "#4a1d46",
    fieldDot: "#e879f9",
    mesh: "#5c2657",
    spoke: "#6b2c63",
    spokeHot: "#ff7ce5",
    mote: "#ff8ee3",
    moteHot: "#ffe0f7",
    coLink: "#e879f9",
    worldBg:
      "radial-gradient(ellipse 95% 88% at 50% 42%, #2d1236 0%, #1d0b28 38%, #11061a 72%, #07030d 100%)",
    pageBg: "#07030d",
    panelBg: "rgba(16, 6, 24, 0.96)",
    drawerBg: "rgba(14, 5, 22, 0.88)",
    barBg: "rgba(15, 6, 24, 0.76)",
    inputBg: "rgba(26, 10, 38, 0.92)",
    tileBg: "rgba(20, 8, 30, 0.78)",
    orbGlowRgb: "255, 77, 184",
    orbGlow2Rgb: "192, 132, 252",
    femaleMix: 1,
  },
};
