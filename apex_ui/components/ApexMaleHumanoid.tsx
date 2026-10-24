"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import * as THREE from "three";
import type { OrbState } from "./ApexHeroOrb";
import { useJarvisAudioLevel, type TraceEvent } from "./JarvisBridge";

const PORTRAIT_URL = "/hologram/male_portrait.png";
const DEPTH_URL = "/hologram/male_depth.png";

const WORLD_W = 7.4;
const CAM_Y = 0.02;
const CAM_Z = 6.85;
const Y_PIVOT = -0.74;
const Z_PIVOT = 0.0;
const TORSO_Y_PIVOT = -1.85;

const ASSEMBLY_DURATION_SECONDS = 2.85;
const SHOCKWAVE_DURATION_SECONDS = 2.4;
const MOOD_BLOOM_SECONDS = 0.68;

// Screen-space eye/head reference center (50% X, 38% Y from top of viewport)
const EYE_SCREEN_X = 0.5;
const EYE_SCREEN_Y = 0.38;

const MAX_HEAD_YAW = 0.40; // ~23 deg left/right
const MAX_HEAD_PITCH_UP = 0.26; // ~15 deg up
const MAX_HEAD_PITCH_DOWN = 0.28; // ~16 deg down

export type HumanoidQualityMode = "auto" | "high" | "balanced";
type RenderTier = "high" | "medium" | "low";

type DecodedAssets = {
  width: number;
  height: number;
  portrait: Uint8ClampedArray;
  depth: Uint8ClampedArray;
};

type HumanoidParticleData = {
  count: number;
  tier: RenderTier;
  worldH: number;
  positions: Float32Array;
  colors: Float32Array;
  normals: Float32Array;
  traits: Float32Array; // vec4: [edge, warm, cyan, voiceWeight]
  assemblySource: Float32Array; // vec3
  meta: Float32Array; // vec3: [assemblyPhase, radialZone, seed]
  rig: Float32Array; // vec2: [skinWeight, region]
};

type MoodProfile = {
  cyan: number;
  warm: number;
  zone: number;
  tone: number; // 0 = cool electric cyan, 1 = molten amber-gold
  shimmer: number;
};

const MOOD_PROFILES: Record<OrbState, MoodProfile> = {
  idle: { cyan: 0.13, warm: 0.15, zone: 0.06, tone: 0.34, shimmer: 0.18 },
  listening: { cyan: 0.58, warm: 0.11, zone: 0.36, tone: 0.05, shimmer: 0.48 },
  thinking: { cyan: 0.22, warm: 0.60, zone: 0.42, tone: 0.78, shimmer: 0.62 },
  speaking: { cyan: 0.24, warm: 0.50, zone: 0.32, tone: 0.86, shimmer: 0.52 },
};

// Precomputed 256-entry sRGB -> linear LUT (eliminates 900,000 Math.pow calls on startup)
const SRGB_TO_LINEAR = (() => {
  const lut = new Float32Array(256);
  for (let i = 0; i < 256; i++) {
    const c = i / 255;
    lut[i] = c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  }
  return lut;
})();

let cachedAssetsPromise: Promise<DecodedAssets> | null = null;
const cachedParticleTiers = new Map<RenderTier, HumanoidParticleData>();

function hash01(v: number): number {
  const raw = Math.sin(v * 12.9898 + 0.1234) * 43758.5453;
  return raw - Math.floor(raw);
}

/**
 * Analytical 2nd-order critically-damped spring (zeta = 1.0).
 * Zero jerk on sudden mouse flicks, zero overshoot, frame-rate independent.
 */
function criticallyDampedSpring(
  current: number,
  velocity: number,
  target: number,
  omega: number,
  dt: number
): [number, number] {
  const x = current - target;
  const exp = Math.exp(-omega * dt);
  const temp = (velocity + omega * x) * dt;
  const nextPos = target + (x + temp) * exp;
  const nextVel = (velocity - omega * temp) * exp;
  return [nextPos, nextVel];
}

function shapeGazeAxis(v: number): number {
  const clamped = THREE.MathUtils.clamp(v, -1, 1);
  const mag = Math.abs(clamped);
  // Responsive around center with smooth soft-knee saturation near viewport edges
  return Math.sign(clamped) * Math.pow(mag, 0.86);
}

function loadImageElement(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.decoding = "async";
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error(`Failed to load ${src}`));
    img.src = src;
  });
}

function loadDecodedAssets(): Promise<DecodedAssets> {
  if (cachedAssetsPromise) return cachedAssetsPromise;

  cachedAssetsPromise = Promise.all([
    loadImageElement(PORTRAIT_URL),
    loadImageElement(DEPTH_URL),
  ])
    .then(([portraitImg, depthImg]) => {
      const width = portraitImg.naturalWidth || 1020;
      const height = portraitImg.naturalHeight || 634;

      const c1 = document.createElement("canvas");
      c1.width = width;
      c1.height = height;
      const ctx1 = c1.getContext("2d", { willReadFrequently: true });
      if (!ctx1) throw new Error("Canvas 2D unavailable");
      ctx1.drawImage(portraitImg, 0, 0, width, height);
      const portrait = ctx1.getImageData(0, 0, width, height).data;

      const c2 = document.createElement("canvas");
      c2.width = width;
      c2.height = height;
      const ctx2 = c2.getContext("2d", { willReadFrequently: true });
      if (!ctx2) throw new Error("Canvas 2D unavailable");
      ctx2.drawImage(depthImg, 0, 0, width, height);
      const depth = ctx2.getImageData(0, 0, width, height).data;

      return { width, height, portrait, depth };
    })
    .catch((err) => {
      cachedAssetsPromise = null;
      throw err;
    });

  return cachedAssetsPromise;
}

function buildProceduralFallback(tier: RenderTier): HumanoidParticleData {
  const count = tier === "high" ? 240000 : tier === "medium" ? 80000 : 36000;
  const worldH = 4.6;
  const positions = new Float32Array(count * 3);
  const colors = new Float32Array(count * 3);
  const normals = new Float32Array(count * 3);
  const traits = new Float32Array(count * 4);
  const assemblySource = new Float32Array(count * 3);
  const meta = new Float32Array(count * 3);
  const rig = new Float32Array(count * 2);

  for (let i = 0; i < count; i++) {
    const s1 = hash01(i * 1.13 + 0.7);
    const s2 = hash01(i * 2.41 + 1.9);
    const s3 = hash01(i * 3.77 + 4.3);
    const isWave = i > count * 0.72;
    let wx = 0;
    let wy = 0;
    let wz = 0;
    let skinW = 0;
    let region = 0.7;
    let r = 0.15;
    let g = 0.82;
    let b = 0.98;
    let warm = 0;
    let cyan = 0.85;
    let voiceW = 0;

    if (isWave) {
      wx = (s1 - 0.5) * WORLD_W;
      const ribbon = Math.floor(s2 * 18) / 18;
      wy = -0.35 + (ribbon - 0.5) * 1.35 + Math.sin(wx * 1.6 + ribbon * 5.0) * 0.22;
      wz = -0.38 + Math.cos(wx * 1.4 - ribbon * 4.0) * 0.16;
      region = 0.12;
      if (s2 < 0.35) {
        r = 0.95;
        g = 0.62;
        b = 0.2;
        warm = 0.8;
        cyan = 0.1;
      }
    } else if (s1 < 0.54) {
      const band = Math.floor(s2 * 64) / 64;
      const theta = (s3 - 0.5) * Math.PI;
      const ny = 0.09 + band * 0.56;
      const rx = 0.92 * Math.sqrt(Math.max(0.04, 1 - Math.pow((ny - 0.36) / 0.3, 2)));
      wx = Math.sin(theta) * rx;
      wy = (0.5 - ny) * worldH;
      wz = Math.cos(theta) * rx * 0.76;
      skinW = 1;
      region = 0.7;
      const center = Math.exp(-Math.pow(wx / 0.34, 2)) * Math.exp(-Math.pow((ny - 0.42) / 0.18, 2));
      r = THREE.MathUtils.lerp(0.12, 1.0, center);
      g = THREE.MathUtils.lerp(0.86, 0.64, center);
      b = THREE.MathUtils.lerp(1.0, 0.22, center);
      warm = center;
      cyan = 1 - center * 0.8;
      voiceW = center > 0.35 ? 0.85 : 0;
    } else {
      const band = Math.floor(s2 * 46) / 46;
      const ny = 0.62 + band * 0.35;
      const span = 0.42 + Math.pow((ny - 0.62) / 0.35, 0.72) * 2.35;
      wx = (s3 - 0.5) * 2 * span;
      wy = (0.5 - ny) * worldH;
      wz = Math.sqrt(Math.max(0, 1 - Math.pow(wx / (span + 0.05), 2))) * 0.44;
      skinW = Math.max(0, 1 - (ny - 0.62) / 0.14);
      region = 0.4;
      const spine = Math.exp(-Math.pow(wx / 0.24, 2));
      r = THREE.MathUtils.lerp(0.08, 0.98, spine);
      g = THREE.MathUtils.lerp(0.78, 0.62, spine);
      b = THREE.MathUtils.lerp(0.96, 0.22, spine);
      warm = spine;
      cyan = 1 - spine * 0.75;
      voiceW = spine > 0.4 ? 0.42 : 0;
    }

    const p3 = i * 3;
    const p4 = i * 4;
    const p2 = i * 2;
    positions[p3] = wx;
    positions[p3 + 1] = wy;
    positions[p3 + 2] = wz;
    colors[p3] = r;
    colors[p3 + 1] = g;
    colors[p3 + 2] = b;
    normals[p3] = wx * 0.35;
    normals[p3 + 1] = 0.12;
    normals[p3 + 2] = 0.92;
    traits[p4] = Math.abs(wx) > 0.65 ? 0.8 : 0.15;
    traits[p4 + 1] = warm;
    traits[p4 + 2] = cyan;
    traits[p4 + 3] = voiceW;

    const angle = s1 * Math.PI * 2;
    const dist = 2.8 + s2 * 2.6;
    assemblySource[p3] = Math.cos(angle) * dist;
    assemblySource[p3 + 1] = (s3 - 0.5) * worldH * 1.25;
    assemblySource[p3 + 2] = -1.6 + (s2 - 0.5) * 2.2;

    meta[p3] = isWave ? 0.56 + s3 * 0.18 : 0.04 + s1 * 0.52;
    meta[p3 + 1] = Math.min(1, Math.hypot(wx / 3.4, (wy - 0.42) / 2.6));
    meta[p3 + 2] = s3;
    rig[p2] = skinW;
    rig[p2 + 1] = region;
  }

  return {
    count,
    tier,
    worldH,
    positions,
    colors,
    normals,
    traits,
    assemblySource,
    meta,
    rig,
  };
}

function quintic01(v: number): number {
  const t = v < 0 ? 0 : v > 1 ? 1 : v;
  return t * t * t * (t * (t * 6 - 15) + 10);
}

function buildHumanoidParticles(
  assets: DecodedAssets,
  tier: RenderTier
): HumanoidParticleData {
  const cached = cachedParticleTiers.get(tier);
  if (cached) return cached;

  const { width: W, height: H, portrait, depth } = assets;
  const step = tier === "high" ? 1 : tier === "medium" ? 2 : 3;
  const brightnessThreshold = tier === "high" ? 0.044 : 0.04;
  const worldH = WORLD_W * (H / W);

  // Separable 7-tap binomial Gaussian filter ([1,6,15,20,15,6,1]/64) on depth so z has zero contour cliff
  const rawDepth = new Float32Array(W * H);
  for (let i = 0, n = W * H; i < n; i++) {
    rawDepth[i] = (depth[i * 4] / 255) * 1.75 - 0.8;
  }
  const tmpDepth = new Float32Array(W * H);
  const smoothDepth = new Float32Array(W * H);
  for (let y = 0; y < H; y++) {
    const row = y * W;
    for (let x = 0; x < W; x++) {
      const xm3 = x > 2 ? x - 3 : 0;
      const xm2 = x > 1 ? x - 2 : 0;
      const xm1 = x > 0 ? x - 1 : 0;
      const xp1 = x < W - 1 ? x + 1 : W - 1;
      const xp2 = x < W - 2 ? x + 2 : W - 1;
      const xp3 = x < W - 3 ? x + 3 : W - 1;
      tmpDepth[row + x] =
        (rawDepth[row + xm3] +
          rawDepth[row + xm2] * 6 +
          rawDepth[row + xm1] * 15 +
          rawDepth[row + x] * 20 +
          rawDepth[row + xp1] * 15 +
          rawDepth[row + xp2] * 6 +
          rawDepth[row + xp3]) *
        0.015625;
    }
  }
  for (let y = 0; y < H; y++) {
    const ym3 = (y > 2 ? y - 3 : 0) * W;
    const ym2 = (y > 1 ? y - 2 : 0) * W;
    const ym1 = (y > 0 ? y - 1 : 0) * W;
    const y0 = y * W;
    const yp1 = (y < H - 1 ? y + 1 : H - 1) * W;
    const yp2 = (y < H - 2 ? y + 2 : H - 1) * W;
    const yp3 = (y < H - 3 ? y + 3 : H - 1) * W;
    for (let x = 0; x < W; x++) {
      smoothDepth[y0 + x] =
        (tmpDepth[ym3 + x] +
          tmpDepth[ym2 + x] * 6 +
          tmpDepth[ym1 + x] * 15 +
          tmpDepth[y0 + x] * 20 +
          tmpDepth[yp1 + x] * 15 +
          tmpDepth[yp2 + x] * 6 +
          tmpDepth[yp3 + x]) *
        0.015625;
    }
  }

  const cols = Math.ceil(W / step);
  const rows = Math.ceil(H / step);
  const maxCount = cols * rows;

  const positions = new Float32Array(maxCount * 3);
  const colors = new Float32Array(maxCount * 3);
  const normals = new Float32Array(maxCount * 3);
  const traits = new Float32Array(maxCount * 4);
  const assemblySource = new Float32Array(maxCount * 3);
  const meta = new Float32Array(maxCount * 3);
  const rig = new Float32Array(maxCount * 2);

  const sampleBright = (sx: number, sy: number): number => {
    if (sx < 0 || sy < 0 || sx >= W || sy >= H) return 0;
    const idx = (sy * W + sx) * 4;
    const pr = portrait[idx];
    const pg = portrait[idx + 1];
    const pb = portrait[idx + 2];
    return (pr > pg ? (pr > pb ? pr : pb) : pg > pb ? pg : pb) / 255;
  };

  const sampleDepthWorld = (sx: number, sy: number): number => {
    const cx = sx < 0 ? 0 : sx >= W ? W - 1 : sx;
    const cy = sy < 0 ? 0 : sy >= H ? H - 1 : sy;
    return smoothDepth[cy * W + cx];
  };

  const inv2Dx = 1 / (2 * ((step / Math.max(1, W - 1)) * WORLD_W));
  const inv2Dy = 1 / (2 * ((step / Math.max(1, H - 1)) * worldH));

  let count = 0;

  for (let y = 0; y < H; y += step) {
    const ny = y / (H - 1);
    const wyScreen = (0.5 - ny) * worldH;

    for (let x = 0; x < W; x += step) {
      const pIdx = (y * W + x) * 4;
      const r8 = portrait[pIdx];
      const g8 = portrait[pIdx + 1];
      const b8 = portrait[pIdx + 2];
      const max8 = r8 > g8 ? (r8 > b8 ? r8 : b8) : g8 > b8 ? g8 : b8;
      const brightness = max8 / 255;

      const nx = x / (W - 1);
      const wxScreen = (nx - 0.5) * WORLD_W;
      const faceAbsX = Math.abs(nx - 0.5);

      // Pure C2 quintic anatomical skinning field across (nx, ny):
      // Rigid inside head core (|nx - 0.5| <= 0.145, ny <= 0.565), smoothly feathering across
      // ear aura and cervical neck so adjacent particles NEVER tear or separate at any angle.
      const latW = quintic01(1 - (faceAbsX - 0.145) / (0.275 - 0.145));
      const cervW = quintic01(1 - (ny - 0.565) / (0.775 - 0.565));
      const skinWeight = latW * cervW;

      const regionClass = depth[pIdx + 2] / 255;

      const minBright = regionClass > 0.85 ? 0.095 : brightnessThreshold;
      if (brightness < minBright) continue;

      const seed = hash01(count * 1.37 + x * 0.17 + y * 0.31);
      const wzBase = smoothDepth[y * W + x];
      const microThickness = (seed - 0.5) * 0.016 * (0.35 + skinWeight * 0.65);
      const wz = wzBase + microThickness;

      // Exact camera-ray perspective unprojection so yaw=0, pitch=0 projects 1:1 without contour gaps
      const perspScale = (CAM_Z - wz) / CAM_Z;
      const wx = wxScreen * perspScale;
      const wy = (wyScreen - CAM_Y) * perspScale + CAM_Y;

      // Finite-difference 3D surface normal for depth-shaded head turn
      const zL = sampleDepthWorld(x - step, y);
      const zR = sampleDepthWorld(x + step, y);
      const zU = sampleDepthWorld(x, y - step);
      const zD = sampleDepthWorld(x, y + step);
      const dzdx = (zR - zL) * inv2Dx;
      const dzdy = (zU - zD) * inv2Dy;
      let snx = -dzdx * 0.65;
      let sny = -dzdy * 0.65;
      let snz = 1.0;
      const invLen = 1 / (Math.hypot(snx, sny, snz) || 1);
      snx *= invLen;
      sny *= invLen;
      snz *= invLen;

      const isEdge =
        brightness > 0.11 &&
        (sampleBright(x - step, y) < 0.042 ||
          sampleBright(x + step, y) < 0.042 ||
          sampleBright(x, y - step) < 0.042 ||
          sampleBright(x, y + step) < 0.042);

      const warmRatio =
        r8 > 95 && r8 > b8 * 1.25
          ? Math.min(1, ((r8 - b8 * 0.75) / 205) * (0.55 + brightness * 0.65))
          : 0;
      const cyanRatio =
        b8 > r8 * 1.08 && Math.max(g8, b8) > 70
          ? Math.min(1, ((Math.max(g8, b8) - r8 * 0.65) / 200) * (0.5 + brightness * 0.6))
          : 0;

      let voiceWeight = 0;
      if (
        skinWeight > 0.45 &&
        ny > 0.22 &&
        ny < 0.63 &&
        faceAbsX < 0.095 &&
        (warmRatio > 0.16 || brightness > 0.22)
      ) {
        const centerFalloff = 1 - Math.min(1, faceAbsX / 0.095);
        voiceWeight = 0.58 + 0.42 * centerFalloff * Math.min(1, brightness * 1.25);
      } else if (
        ny >= 0.60 &&
        ny < 0.95 &&
        faceAbsX < 0.115 &&
        (warmRatio > 0.12 || brightness > 0.25)
      ) {
        const spineFalloff = 1 - Math.min(1, faceAbsX / 0.115);
        voiceWeight = 0.16 + 0.36 * spineFalloff * Math.min(1, brightness * 1.2);
      }

      let assemblyPhase = 0.02 + seed * 0.12;
      if (regionClass > 0.85) {
        assemblyPhase = 0.48 + seed * 0.20;
      } else if (skinWeight > 0.55) {
        const headDist = Math.min(1, Math.hypot((nx - 0.5) / 0.16, (ny - 0.38) / 0.30));
        assemblyPhase = 0.01 + headDist * 0.16 + seed * 0.08;
      } else if (regionClass > 0.55) {
        assemblyPhase = 0.20 + ((ny - 0.55) / 0.28) * 0.14 + seed * 0.08;
      } else if (regionClass > 0.25) {
        const shDist = Math.min(1, faceAbsX / 0.38);
        assemblyPhase = 0.32 + shDist * 0.20 + seed * 0.09;
      } else {
        const waveDist = Math.min(1, Math.max(0, (faceAbsX - 0.12) / 0.38));
        assemblyPhase = 0.44 + waveDist * 0.22 + seed * 0.08;
      }

      const streamSide = nx < 0.5 ? -1 : 1;
      const swirlAngle = seed * Math.PI * 2 + ny * 3.4 * streamSide;
      const radialSpread = 1.75 + hash01(count * 2.71 + 3.1) * 2.65;
      const srcX =
        wx * 0.38 +
        Math.cos(swirlAngle) * radialSpread +
        streamSide * (0.78 + hash01(count * 0.91 + 7.4) * 1.25);
      const srcY =
        wy * 0.58 +
        Math.sin(swirlAngle) * (0.88 + hash01(count * 1.83 + 5.2) * 1.35) -
        0.30;
      const srcZ = -1.85 + (hash01(count * 3.19 + 1.7) - 0.35) * 2.2;

      const rxBloom = (nx - 0.5) / 0.46;
      const ryBloom = (ny - 0.40) / 0.62;
      const radialZone = Math.min(1, Math.hypot(rxBloom, ryBloom));

      const o3 = count * 3;
      const o4 = count * 4;
      const o2 = count * 2;

      positions[o3] = wx;
      positions[o3 + 1] = wy;
      positions[o3 + 2] = wz;

      colors[o3] = SRGB_TO_LINEAR[r8];
      colors[o3 + 1] = SRGB_TO_LINEAR[g8];
      colors[o3 + 2] = SRGB_TO_LINEAR[b8];

      normals[o3] = snx;
      normals[o3 + 1] = sny;
      normals[o3 + 2] = snz;

      traits[o4] = isEdge ? 1.0 : 0.0;
      traits[o4 + 1] = warmRatio;
      traits[o4 + 2] = cyanRatio;
      traits[o4 + 3] = voiceWeight;

      assemblySource[o3] = srcX;
      assemblySource[o3 + 1] = srcY;
      assemblySource[o3 + 2] = srcZ;

      meta[o3] = assemblyPhase;
      meta[o3 + 1] = radialZone;
      meta[o3 + 2] = seed;

      rig[o2] = skinWeight;
      rig[o2 + 1] = regionClass;

      count += 1;
    }
  }

  const built: HumanoidParticleData = {
    count,
    tier,
    worldH,
    positions: positions.subarray(0, count * 3),
    colors: colors.subarray(0, count * 3),
    normals: normals.subarray(0, count * 3),
    traits: traits.subarray(0, count * 4),
    assemblySource: assemblySource.subarray(0, count * 3),
    meta: meta.subarray(0, count * 3),
    rig: rig.subarray(0, count * 2),
  };

  cachedParticleTiers.set(tier, built);
  return built;
}

/**
 * Single-pass Premultiplied Dual-Kernel Shader (Src: ONE, Dst: ONE_MINUS_SRC_ALPHA)
 * Renders BOTH crisp pinpoint color core AND volumetric additive halo in ONE draw call
 * (cutting vertex GPU load by 50% while eliminating sub-pixel snapping).
 */
const VERTEX_SHADER = /* glsl */ `
attribute vec3 color;
attribute vec3 aNormal;
attribute vec4 aTraits;         // x: edge, y: warm, z: cyan, w: voiceWeight
attribute vec3 aAssemblySource;
attribute vec3 aMeta;           // x: assemblyPhase, y: radialZone, z: seed
attribute vec2 aRig;            // x: skinWeight, y: regionClass

uniform float uTime;
uniform float uDpr;
uniform float uPointSize;
uniform float uYaw;
uniform float uPitch;
uniform float uRoll;
uniform float uTorsoYaw;
uniform float uTorsoPitch;
uniform float uWaveParallaxX;
uniform float uWaveParallaxY;
uniform float uChest;
uniform float uAssemblyProgress;
uniform float uAssemblyEnabled;
uniform float uShockwaveActive;
uniform float uShockwaveProgress;
uniform float uTransitionProgress;
uniform vec4 uPrevMood;         // x: cyan, y: warm, z: zone, w: tone
uniform vec4 uNextMood;         // x: cyan, y: warm, z: zone, w: tone
uniform float uMoodShimmer;
uniform float uVoice;
uniform float uBrainActivity;
uniform float uBrainTone;
uniform float uEffects;

varying vec3 vCoreColor;
varying vec3 vHaloColor;
varying float vCoreAlpha;
varying float vHaloAlpha;

float smoother(float x) {
  return x * x * x * (x * (x * 6.0 - 15.0) + 10.0);
}

void main() {
  vec3 p = position;
  vec3 nrm = aNormal;

  float edgeTrait = aTraits.x;
  float warmTrait = aTraits.y;
  float cyanTrait = aTraits.z;
  float voiceTrait = aTraits.w;

  float assemblyPhase = aMeta.x;
  float radialZone = aMeta.y;
  float seed = aMeta.z;

  float skinW = aRig.x;
  float region = aRig.y;

  // 1. Living backdrop wave motion + subtle 3D depth parallax (smoothly masked away from head core)
  float waveMask = (1.0 - smoothstep(0.18, 0.30, region)) * (1.0 - skinW);
  if (waveMask > 0.001 && uEffects > 0.5) {
    float w1 = sin(p.x * 1.48 - uTime * 0.82 + p.z * 2.1) * 0.050;
    float w2 = cos(p.x * 2.85 + uTime * 0.58 - p.y * 1.65) * 0.025;
    p.y += (w1 + w2 + uWaveParallaxY * 0.55) * waveMask;
    p.x += (uWaveParallaxX * 0.55) * waveMask;
    p.z += sin(p.x * 1.18 + uTime * 0.70 + seed * 1.5) * 0.072 * waveMask;
  }

  // 2. Crown floating light-sparks drift (region ~ 0.95)
  if (region > 0.85 && uEffects > 0.5) {
    p.y += sin(uTime * 1.35 + seed * 6.2831853) * 0.032 + 0.010;
    p.x += cos(uTime * 1.02 + seed * 9.42477) * 0.016;
    p.z += sin(uTime * 0.90 + seed * 4.71238) * 0.020;
  }

  // 3. Subtle vocal contour resonance on visage when speaking
  if (voiceTrait > 0.55 && uVoice > 0.01 && uEffects > 0.5) {
    float vocalWave = sin(p.y * 25.0 - uTime * 14.5 + seed * 3.14) * 0.0082 * uVoice;
    p.z += vocalWave * 1.55;
    p.y += vocalWave * 0.42;
  }

  // 4. Organic breathing + C2 secondary upper-torso follow-through (zero hard boundary)
  float bodyWeight = (1.0 - skinW) * smoothstep(0.24, 0.48, region) * (1.0 - smoothstep(0.80, 0.92, region));
  p.y += uChest * bodyWeight;
  p.z += uChest * 0.62 * bodyWeight;

  float torsoVert = smoothstep(${TORSO_Y_PIVOT.toFixed(4)} - 0.35, -0.55, p.y);
  float torsoLat = 1.0 - smoothstep(1.95, 3.05, abs(p.x));
  float torsoFactor = torsoVert * torsoLat * (1.0 - skinW);
  float ty = uTorsoYaw * torsoFactor;
  float tp = uTorsoPitch * torsoFactor;
  if (abs(ty) + abs(tp) > 0.0002) {
    float cty = cos(ty), sty = sin(ty);
    float ctp = cos(tp), stp = sin(tp);
    vec3 trel = vec3(p.x, p.y - (${TORSO_Y_PIVOT.toFixed(4)}), p.z);
    vec3 tr1 = vec3(trel.x * cty + trel.z * sty, trel.y, -trel.x * sty + trel.z * cty);
    vec3 tr2 = vec3(tr1.x, tr1.y * ctp - tr1.z * stp, tr1.y * stp + tr1.z * ctp);
    p = vec3(tr2.x, tr2.y + (${TORSO_Y_PIVOT.toFixed(4)}), tr2.z);
  }

  // 5. True 3D depth-shaded head + cervical neck rotation around anatomical spine pivot
  // Sign convention verified across all 4 quadrants:
  //   uYaw > 0   -> nose moves RIGHT (+X)
  //   uYaw < 0   -> nose moves LEFT (-X)
  //   uPitch > 0 -> nose nods DOWN (-Y), crown tilts forward (+Z)
  //   uPitch < 0 -> nose tilts UP (+Y), chin lifts up
  float depthShade = 1.0;
  if (skinW > 0.001) {
    float yaw = uYaw * skinW;
    float pitch = uPitch * skinW;
    float roll = uRoll * skinW;

    float cy = cos(yaw), sy = sin(yaw);
    float cp = cos(pitch), sp = sin(pitch);
    float cr = cos(roll), sr = sin(roll);

    vec3 rel = vec3(p.x, p.y - (${Y_PIVOT.toFixed(4)}), p.z - (${Z_PIVOT.toFixed(4)}));

    // Yaw around Y
    vec3 r1 = vec3(rel.x * cy + rel.z * sy, rel.y, -rel.x * sy + rel.z * cy);
    // Pitch around X
    vec3 r2 = vec3(r1.x, r1.y * cp - r1.z * sp, r1.y * sp + r1.z * cp);
    // Subtle natural roll around Z
    vec3 r3 = vec3(r2.x * cr - r2.y * sr, r2.x * sr + r2.y * cr, r2.z);

    p = vec3(r3.x, r3.y + (${Y_PIVOT.toFixed(4)}), r3.z + (${Z_PIVOT.toFixed(4)}));

    vec3 n1 = vec3(nrm.x * cy + nrm.z * sy, nrm.y, -nrm.x * sy + nrm.z * cy);
    vec3 n2 = vec3(n1.x, n1.y * cp - n1.z * sp, n1.y * sp + n1.z * cp);
    nrm = normalize(n2);

    vec3 keyLight = normalize(vec3(sin(uYaw) * 0.40, -sin(uPitch) * 0.30 + 0.24, 0.88));
    float lambert = clamp(dot(nrm, keyLight), 0.0, 1.0);
    float fresnelRim = pow(1.0 - clamp(abs(nrm.z), 0.0, 1.0), 1.75);
    depthShade = mix(1.0, 0.80 + 0.32 * lambert + 0.22 * fresnelRim, skinW);
  }

  // 6. Fluid birth assembly from pure darkness ("a figure of light that assembles itself")
  float birthVisibility = 1.0;
  float assemblyGlow = 0.0;
  if (uAssemblyEnabled > 0.5 && uAssemblyProgress < 1.0) {
    float raw = clamp((uAssemblyProgress - assemblyPhase) / 0.34, 0.0, 1.0);
    float local = smoother(raw);
    birthVisibility = smoothstep(0.0, 0.18, raw);
    assemblyGlow = sin(local * 3.14159265) * 0.52;

    float arc = sin(local * 3.14159265);
    float curvePhase = seed * 6.2831853;
    float swirl = sin(local * 4.7123889 + curvePhase) * pow(1.0 - local, 1.85) * 0.075;

    p = mix(aAssemblySource, p, local);
    p.x += swirl;
    p.y += arc * (0.14 + seed * 0.09);
    p.z += arc * (0.12 + fract(seed * 7.13) * 0.09);
  }

  // 7. Radial shockwave bursting outward from sternum/heart nexus
  float shockProgress = clamp(uShockwaveProgress, 0.0, 1.0);
  vec2 shockOrigin = vec2(0.0, -0.22);
  vec2 shockVec = p.xy - shockOrigin;
  float shockRadius = length(shockVec);
  float travel = clamp((shockProgress - 0.05) / 0.82, 0.0, 1.0);
  float waveRadius = mix(0.08, 4.95, travel);
  float ring = 1.0 - smoothstep(0.0, 0.28, abs(shockRadius - waveRadius));
  float waveFade = smoothstep(0.02, 0.12, shockProgress) * (1.0 - smoothstep(0.80, 1.0, shockProgress));
  float coreFlash = (1.0 - smoothstep(0.08, 0.82, shockRadius)) * (1.0 - smoothstep(0.02, 0.24, shockProgress));
  float shockRing = ring * waveFade * uShockwaveActive;
  float shockCore = coreFlash * uShockwaveActive;
  float shockEnergy = max(shockRing, shockCore);

  if (shockRing > 0.001) {
    vec2 dir = shockVec / max(shockRadius, 0.0001);
    p.xy += dir * shockRing * (1.0 - travel) * 0.046;
    p.z += shockRing * (1.0 - travel) * 0.080;
  }

  // 8. Four moods blooming radially outward from the face over 680ms
  float localBloom = smoothstep(
    radialZone * 0.58,
    radialZone * 0.58 + 0.42,
    clamp(uTransitionProgress, 0.0, 1.0)
  );
  vec4 mood = mix(uPrevMood, uNextMood, localBloom);
  float stateCyan = mood.x;
  float stateWarm = mood.y;
  float stateZone = mood.z;
  float stateTone = mood.w;

  float neuralFlow = 0.5 + 0.5 * sin(p.y * 4.2 - uTime * 3.6 + seed * 3.14159);
  float moodWave = uMoodShimmer * (0.45 + 0.55 * neuralFlow) * (1.0 - radialZone * 0.55);

  float faceCadence = 0.72 + 0.28 * sin(uTime * 11.2 + p.y * 8.0 + seed * 2.0);
  float coreCadence = 0.76 + 0.24 * sin(uTime * 6.0 - p.y * 4.5);
  float isVisageVoice = step(0.55, voiceTrait);
  float voiceEnergy =
    voiceTrait *
    mix(coreCadence, faceCadence, isVisageVoice) *
    uVoice *
    1.35;

  float brainRhythm = 0.72 + 0.28 * sin(uTime * 6.6 + seed * 6.2831853);
  float brainPulse = uBrainActivity * (0.42 + (1.0 - radialZone) * 0.58) * brainRhythm * uEffects;

  float cyanEnergy =
    cyanTrait * stateCyan +
    edgeTrait * (0.09 + stateCyan * 0.38) +
    moodWave * (1.0 - stateTone) * 0.32 +
    shockRing * (0.42 + travel * 0.28) +
    assemblyGlow * 0.26;

  float warmEnergy =
    warmTrait * stateWarm +
    moodWave * stateTone * 0.36 +
    shockCore * 0.68 +
    shockRing * (1.0 - travel) * 0.20;

  float zoneEnergy = (1.0 - radialZone * 0.72) * stateZone;
  float totalEnergy = (cyanEnergy + warmEnergy + voiceEnergy + zoneEnergy + brainPulse * 0.45) * uEffects;

  vec3 electricCyan = vec3(0.28, 0.93, 1.0);
  vec3 moltenAmber = vec3(1.0, 0.62, 0.16);
  vec3 emeraldSignal = vec3(0.38, 1.0, 0.70);
  vec3 synapticViolet = vec3(0.68, 0.48, 1.0);

  float bt = clamp(uBrainTone, 0.0, 1.0);
  vec3 brainColor = bt < 0.5
    ? mix(electricCyan, emeraldSignal, bt * 2.0)
    : mix(synapticViolet, moltenAmber, (bt - 0.5) * 2.0);

  vec3 moodTint = mix(electricCyan, moltenAmber, clamp(stateTone, 0.0, 1.0));

  // Crisp core color (HDR tone-guarded so 300k dots never clip to flat white)
  vec3 lifted = pow(max(color, vec3(0.0)), vec3(0.88)) * depthShade;
  vec3 boosted =
    lifted * 1.10 +
    electricCyan * cyanEnergy * 0.16 +
    moltenAmber * (warmEnergy + voiceEnergy * 1.15) * 0.21 +
    brainColor * brainPulse * 0.15;

  float peak = max(boosted.r, max(boosted.g, boosted.b));
  if (peak > 1.0) {
    boosted /= peak;
  }

  vCoreColor = clamp(boosted, 0.0, 1.0);
  vCoreAlpha = birthVisibility;

  // Volumetric halo color & energy
  float gE = clamp(totalEnergy, 0.0, 1.35);
  vec3 glowBase = mix(moodTint, vCoreColor, 0.46);
  vHaloColor = mix(glowBase, brainColor, clamp(brainPulse * 0.36, 0.0, 0.45)) * (0.62 + gE * 0.78) * depthShade;
  vHaloAlpha = clamp(0.022 + gE * 0.115 + shockEnergy * 0.10 + brainPulse * 0.04, 0.0, 0.22) * birthVisibility;

  gl_PointSize = uPointSize * uDpr * (1.0 + gE * 0.08 + shockEnergy * 0.16 + voiceEnergy * 0.07);
  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);
}
`;

const FRAGMENT_SHADER = /* glsl */ `
varying vec3 vCoreColor;
varying vec3 vHaloColor;
varying float vCoreAlpha;
varying float vHaloAlpha;

void main() {
  vec2 centered = gl_PointCoord - vec2(0.5);
  float d2 = dot(centered, centered);
  if (d2 > 0.25) discard;

  // Sub-pixel anti-aliased Gaussian pinpoint core + airy additive outer bloom in ONE pass
  float coreMask = exp(-d2 * 22.0) * vCoreAlpha;
  float haloMask = (exp(-d2 * 5.2) - exp(-5.2 * 0.25)) * vHaloAlpha;

  // Premultiplied output with blend (ONE, ONE_MINUS_SRC_ALPHA):
  // - Where coreMask is high, attenuates overlap so colors never saturate to flat white
  // - Where coreMask -> 0 in outer ring, haloMask adds pure additive light!
  vec3 premulRgb = vCoreColor * coreMask + vHaloColor * haloMask * (1.0 - coreMask * 0.55);
  float outAlpha = clamp(coreMask * 0.92, 0.0, 1.0);

  if (outAlpha < 0.008 && haloMask < 0.004) discard;
  gl_FragColor = vec4(premulRgb, outAlpha);
}
`;

type PointerState = {
  x: number; // [-1..+1], +1 = right of head
  y: number; // [-1..+1], +1 = below eyes (mouse down), -1 = above eyes (mouse up)
  inside: boolean;
};

type PointsCloudProps = {
  data: HumanoidParticleData;
  state: OrbState;
  reducedMotion: boolean;
  audioLevelRef: React.MutableRefObject<number>;
  pointerRef: React.MutableRefObject<PointerState>;
  assemblyRun: number;
  pulseSeq: number;
  brainEvent: { id: number; tone: number } | null;
  onAssemblyStateChange: (assembling: boolean) => void;
  onShockwaveTrigger: () => void;
  onLowFpsDetected: () => void;
};

function HumanoidPointCloud({
  data,
  state,
  reducedMotion,
  audioLevelRef,
  pointerRef,
  assemblyRun,
  pulseSeq,
  brainEvent,
  onAssemblyStateChange,
  onShockwaveTrigger,
  onLowFpsDetected,
}: PointsCloudProps) {
  // Critically-damped spring states (pos + vel) for liquid-smooth motion
  const springs = useRef({
    yaw: 0,
    yawVel: 0,
    pitch: 0,
    pitchVel: 0,
    roll: 0,
    rollVel: 0,
    torsoYaw: 0,
    torsoYawVel: 0,
    torsoPitch: 0,
    torsoPitchVel: 0,
    waveX: 0,
    waveXVel: 0,
    waveY: 0,
    waveYVel: 0,
  });

  const voiceEnvelope = useRef(0);
  const brainEnvelope = useRef({ activity: 0, tone: 0.1, seenId: -1 });
  const moodTransition = useRef<{
    targetState: OrbState;
    prev: MoodProfile;
    next: MoodProfile;
    progress: number;
  }>({
    targetState: state,
    prev: { ...MOOD_PROFILES[state] },
    next: { ...MOOD_PROFILES[state] },
    progress: 1,
  });

  const assemblyClock = useRef({
    run: -1,
    startedAt: 0,
    completedRun: -1,
  });

  const shockwaveClock = useRef({
    active: false,
    startedAt: 0,
    seenPulseSeq: pulseSeq,
  });

  const fpsMonitor = useRef({ frames: 0, startedAt: 0, reported: false });

  useEffect(() => {
    const tr = moodTransition.current;
    if (tr.targetState === state) return;
    const blend = THREE.MathUtils.clamp(tr.progress, 0, 1);
    const snapshot: MoodProfile = {
      cyan: THREE.MathUtils.lerp(tr.prev.cyan, tr.next.cyan, blend),
      warm: THREE.MathUtils.lerp(tr.prev.warm, tr.next.warm, blend),
      zone: THREE.MathUtils.lerp(tr.prev.zone, tr.next.zone, blend),
      tone: THREE.MathUtils.lerp(tr.prev.tone, tr.next.tone, blend),
      shimmer: THREE.MathUtils.lerp(tr.prev.shimmer, tr.next.shimmer, blend),
    };
    tr.targetState = state;
    tr.prev = snapshot;
    tr.next = { ...MOOD_PROFILES[state] };
    tr.progress = reducedMotion ? 1 : 0;
  }, [state, reducedMotion]);

  useEffect(() => {
    if (brainEvent && brainEvent.id !== brainEnvelope.current.seenId) {
      brainEnvelope.current.seenId = brainEvent.id;
      brainEnvelope.current.activity = 0.92;
      brainEnvelope.current.tone = brainEvent.tone;
    }
  }, [brainEvent]);

  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(data.positions, 3));
    g.setAttribute("color", new THREE.BufferAttribute(data.colors, 3));
    g.setAttribute("aNormal", new THREE.BufferAttribute(data.normals, 3));
    g.setAttribute("aTraits", new THREE.BufferAttribute(data.traits, 4));
    g.setAttribute("aAssemblySource", new THREE.BufferAttribute(data.assemblySource, 3));
    g.setAttribute("aMeta", new THREE.BufferAttribute(data.meta, 3));
    g.setAttribute("aRig", new THREE.BufferAttribute(data.rig, 2));
    g.computeBoundingSphere();
    return g;
  }, [data]);

  useEffect(() => () => geometry.dispose(), [geometry]);

  const uniforms = useMemo(
    () => ({
      uTime: { value: 0 },
      uDpr: { value: 1 },
      uPointSize: { value: 2.35 },
      uYaw: { value: 0 },
      uPitch: { value: 0 },
      uRoll: { value: 0 },
      uTorsoYaw: { value: 0 },
      uTorsoPitch: { value: 0 },
      uWaveParallaxX: { value: 0 },
      uWaveParallaxY: { value: 0 },
      uChest: { value: 0 },
      uAssemblyProgress: { value: reducedMotion ? 1 : 0 },
      uAssemblyEnabled: { value: reducedMotion ? 0 : 1 },
      uShockwaveActive: { value: 0 },
      uShockwaveProgress: { value: 1 },
      uTransitionProgress: { value: 1 },
      uPrevMood: { value: new THREE.Vector4(0.13, 0.15, 0.06, 0.34) },
      uNextMood: { value: new THREE.Vector4(0.13, 0.15, 0.06, 0.34) },
      uMoodShimmer: { value: 0.18 },
      uVoice: { value: 0 },
      uBrainActivity: { value: 0 },
      uBrainTone: { value: 0.1 },
      uEffects: { value: reducedMotion ? 0.35 : 1 },
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const material = useMemo(
    () =>
      new THREE.ShaderMaterial({
        uniforms,
        vertexShader: VERTEX_SHADER,
        fragmentShader: FRAGMENT_SHADER,
        transparent: true,
        depthWrite: false,
        depthTest: false,
        blending: THREE.CustomBlending,
        blendEquation: THREE.AddEquation,
        blendSrc: THREE.OneFactor,
        blendDst: THREE.OneMinusSrcAlphaFactor,
      }),
    [uniforms]
  );

  useEffect(() => () => material.dispose(), [material]);

  useFrame(({ clock, gl }, rawDt) => {
    const dt = Math.min(rawDt, 0.05);
    const t = clock.elapsedTime;
    const dpr = gl.getPixelRatio();

    // Runtime FPS safeguard for AUTO quality after birth stabilizes
    if (!fpsMonitor.current.reported && t > 3.6) {
      if (fpsMonitor.current.startedAt === 0) {
        fpsMonitor.current.startedAt = t;
        fpsMonitor.current.frames = 0;
      } else {
        fpsMonitor.current.frames += 1;
        const elapsed = t - fpsMonitor.current.startedAt;
        if (elapsed >= 2.2) {
          const measuredFps = fpsMonitor.current.frames / elapsed;
          if (measuredFps < 26) {
            fpsMonitor.current.reported = true;
            onLowFpsDetected();
          } else {
            fpsMonitor.current.startedAt = t;
            fpsMonitor.current.frames = 0;
          }
        }
      }
    }

    // Precision 4-quadrant cursor gaze + subtle organic life
    const ptr = pointerRef.current;
    const microLifeYaw = Math.sin(t * 0.52) * 0.016 + Math.sin(t * 1.18 + 1.1) * 0.008;
    const microLifePitch = Math.sin(t * 0.68 + 0.4) * 0.012;
    const idleAutonomousYaw = Math.sin(t * 0.44) * 0.068 + Math.sin(t * 1.07 + 1.2) * 0.024;
    const idleAutonomousPitch = Math.sin(t * 0.58 + 0.6) * 0.028;

    let baseYaw = 0;
    let basePitch = 0;
    if (ptr.inside) {
      const gx = shapeGazeAxis(ptr.x);
      const gy = shapeGazeAxis(ptr.y);
      baseYaw = gx * MAX_HEAD_YAW + microLifeYaw;
      // gy > 0 when mouse is BELOW eyes -> positive pitch nods head DOWN toward cursor
      // gy < 0 when mouse is ABOVE eyes -> negative pitch tilts head UP toward cursor
      basePitch =
        (gy >= 0 ? gy * MAX_HEAD_PITCH_DOWN : gy * MAX_HEAD_PITCH_UP) + microLifePitch;
    } else {
      baseYaw = idleAutonomousYaw;
      basePitch = idleAutonomousPitch;
    }

    // Subtle state nuances layered cleanly ON TOP of full 2D cursor tracking
    let stateYawOffset = 0;
    let statePitchOffset = 0;
    let gazeGain = 1.0;

    if (state === "listening") {
      gazeGain = 1.08;
      statePitchOffset = 0.018 + Math.sin(t * 1.45) * 0.008;
    } else if (state === "thinking") {
      gazeGain = 0.88;
      stateYawOffset = Math.sin(t * 0.72) * 0.045;
      statePitchOffset = -0.022 + Math.sin(t * 0.95) * 0.016;
    } else if (state === "speaking") {
      gazeGain = 0.96;
      stateYawOffset = Math.sin(t * 0.88) * 0.022;
      statePitchOffset = Math.sin(t * 1.85) * 0.016;
    }

    let yawTarget = THREE.MathUtils.clamp(
      baseYaw * gazeGain + stateYawOffset,
      -0.46,
      0.46
    );
    let pitchTarget = THREE.MathUtils.clamp(
      basePitch * gazeGain + statePitchOffset,
      -0.32,
      0.34
    );
    let rollTarget = -yawTarget * 0.085 + (state === "listening" ? 0.014 : 0);

    if (reducedMotion) {
      yawTarget *= 0.3;
      pitchTarget *= 0.3;
      rollTarget = 0;
    }

    const sp = springs.current;
    // Head spring: responsive, silky critically-damped tracking (omega = 10.5)
    [sp.yaw, sp.yawVel] = criticallyDampedSpring(sp.yaw, sp.yawVel, yawTarget, 10.5, dt);
    [sp.pitch, sp.pitchVel] = criticallyDampedSpring(
      sp.pitch,
      sp.pitchVel,
      pitchTarget,
      10.5,
      dt
    );
    [sp.roll, sp.rollVel] = criticallyDampedSpring(sp.roll, sp.rollVel, rollTarget, 8.5, dt);

    // Secondary follow-through on shoulders/torso (omega = 5.4)
    [sp.torsoYaw, sp.torsoYawVel] = criticallyDampedSpring(
      sp.torsoYaw,
      sp.torsoYawVel,
      yawTarget * 0.15,
      5.4,
      dt
    );
    [sp.torsoPitch, sp.torsoPitchVel] = criticallyDampedSpring(
      sp.torsoPitch,
      sp.torsoPitchVel,
      pitchTarget * 0.10,
      5.4,
      dt
    );

    // Subtle 3D background wave counter-parallax (omega = 4.2)
    const targetWaveX = ptr.inside ? -ptr.x * 0.065 : 0;
    const targetWaveY = ptr.inside ? ptr.y * 0.042 : 0;
    [sp.waveX, sp.waveXVel] = criticallyDampedSpring(sp.waveX, sp.waveXVel, targetWaveX, 4.2, dt);
    [sp.waveY, sp.waveYVel] = criticallyDampedSpring(sp.waveY, sp.waveYVel, targetWaveY, 4.2, dt);

    // 680ms radial face-out mood bloom
    const tr = moodTransition.current;
    if (tr.progress < 1) {
      tr.progress = Math.min(1, tr.progress + dt / MOOD_BLOOM_SECONDS);
    }
    const shimmer = THREE.MathUtils.lerp(tr.prev.shimmer, tr.next.shimmer, tr.progress);

    // Real-time audio level from JARVIS voice stream + natural speech cadence
    const rawLevel = audioLevelRef.current || 0;
    const speakingActive = state === "speaking";
    const targetVoice = speakingActive
      ? Math.max(0.38, Math.min(1, 0.32 + rawLevel * 1.45))
      : rawLevel > 0.08 && state === "listening"
      ? rawLevel * 0.25
      : 0;
    const envSpeed = targetVoice > voiceEnvelope.current ? 15.0 : 6.8;
    voiceEnvelope.current = THREE.MathUtils.lerp(
      voiceEnvelope.current,
      targetVoice,
      1 - Math.exp(-dt * envSpeed)
    );
    const cadence = reducedMotion
      ? 0.78
      : 0.72 +
        Math.pow((Math.sin(t * 5.9) + 1) * 0.5, 1.6) * 0.18 +
        Math.pow((Math.sin(t * 10.4 + 0.8) + 1) * 0.5, 2.1) * 0.10;
    const voiceSignal = voiceEnvelope.current * cadence;

    // Brain trace decay
    brainEnvelope.current.activity = Math.max(
      0,
      brainEnvelope.current.activity - dt * (reducedMotion ? 1.6 : 0.78)
    );

    // Birth assembly lifecycle
    let assemblyProgress = 1;
    let assemblyEnabled = 0;
    if (!reducedMotion) {
      if (assemblyClock.current.run !== assemblyRun) {
        assemblyClock.current.run = assemblyRun;
        assemblyClock.current.startedAt = t;
        assemblyClock.current.completedRun = -1;
        onAssemblyStateChange(true);
      }
      assemblyProgress = THREE.MathUtils.clamp(
        (t - assemblyClock.current.startedAt) / ASSEMBLY_DURATION_SECONDS,
        0,
        1
      );
      assemblyEnabled = 1;

      if (assemblyProgress >= 1 && assemblyClock.current.completedRun !== assemblyRun) {
        assemblyClock.current.completedRun = assemblyRun;
        onAssemblyStateChange(false);
        shockwaveClock.current.active = true;
        shockwaveClock.current.startedAt = t;
        onShockwaveTrigger();
      }
    }

    // Manual tap / rebirth shockwave trigger
    if (shockwaveClock.current.seenPulseSeq !== pulseSeq) {
      shockwaveClock.current.seenPulseSeq = pulseSeq;
      if (!reducedMotion) {
        shockwaveClock.current.active = true;
        shockwaveClock.current.startedAt = t;
        onShockwaveTrigger();
      }
    }

    let shockwaveActive = 0;
    let shockwaveProgress = 1;
    if (shockwaveClock.current.active) {
      shockwaveProgress = THREE.MathUtils.clamp(
        (t - shockwaveClock.current.startedAt) / SHOCKWAVE_DURATION_SECONDS,
        0,
        1
      );
      shockwaveActive = 1;
      if (shockwaveProgress >= 1) {
        shockwaveClock.current.active = false;
        shockwaveActive = 0;
      }
    }

    const chestBreath = reducedMotion ? 0 : Math.sin(t * 1.12) * 0.016;
    // Calibrated sprite diameter (includes soft Gaussian outer halo + ~1.1px crisp core)
    const pointSize = data.tier === "high" ? 2.35 : data.tier === "medium" ? 3.55 : 4.65;

    uniforms.uTime.value = t;
    uniforms.uDpr.value = dpr;
    uniforms.uPointSize.value = pointSize;
    uniforms.uYaw.value = sp.yaw;
    uniforms.uPitch.value = sp.pitch;
    uniforms.uRoll.value = sp.roll;
    uniforms.uTorsoYaw.value = sp.torsoYaw;
    uniforms.uTorsoPitch.value = sp.torsoPitch;
    uniforms.uWaveParallaxX.value = sp.waveX;
    uniforms.uWaveParallaxY.value = sp.waveY;
    uniforms.uChest.value = chestBreath;
    uniforms.uAssemblyProgress.value = assemblyProgress;
    uniforms.uAssemblyEnabled.value = assemblyEnabled;
    uniforms.uShockwaveActive.value = shockwaveActive;
    uniforms.uShockwaveProgress.value = shockwaveProgress;
    uniforms.uTransitionProgress.value = tr.progress;
    uniforms.uPrevMood.value.set(tr.prev.cyan, tr.prev.warm, tr.prev.zone, tr.prev.tone);
    uniforms.uNextMood.value.set(tr.next.cyan, tr.next.warm, tr.next.zone, tr.next.tone);
    uniforms.uMoodShimmer.value = shimmer;
    uniforms.uVoice.value = voiceSignal;
    uniforms.uBrainActivity.value = brainEnvelope.current.activity;
    uniforms.uBrainTone.value = brainEnvelope.current.tone;
    uniforms.uEffects.value = reducedMotion ? 0.35 : 1.0;
  });

  return <points geometry={geometry} material={material} frustumCulled={false} />;
}

function AudioLevelProbe({
  targetRef,
}: {
  targetRef: React.MutableRefObject<number>;
}) {
  const level = useJarvisAudioLevel();
  targetRef.current = level;
  return null;
}

export default function ApexMaleHumanoid({
  state,
  trace,
  reducedMotion = false,
  constellationVisible = true,
  onToggleConstellation,
  pulseSignal = 0,
}: {
  state: OrbState;
  trace: TraceEvent | null;
  reducedMotion?: boolean;
  constellationVisible?: boolean;
  onToggleConstellation?: () => void;
  pulseSignal?: number;
}) {
  const audioLevelRef = useRef(0);
  const [qualityMode, setQualityMode] = useState<HumanoidQualityMode>("auto");
  const [autoFallback, setAutoFallback] = useState(false);
  const [particleData, setParticleData] = useState<HumanoidParticleData | null>(null);
  const [assemblyRun, setAssemblyRun] = useState(1);
  const [assembling, setAssembling] = useState(true);
  const [sfxEnabled, setSfxEnabled] = useState(true);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const sfxEnabledRef = useRef(true);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const pointerRef = useRef<PointerState>({
    x: 0,
    y: 0,
    inside: false,
  });

  useEffect(() => {
    sfxEnabledRef.current = sfxEnabled;
  }, [sfxEnabled]);

  const effectiveTier: RenderTier = useMemo(() => {
    if (qualityMode === "high") return "high";
    if (qualityMode === "balanced") return "medium";
    return autoFallback ? "medium" : "high";
  }, [qualityMode, autoFallback]);

  useEffect(() => {
    let cancelled = false;
    loadDecodedAssets()
      .then((assets) => {
        if (cancelled) return;
        const built = buildHumanoidParticles(assets, effectiveTier);
        setParticleData(built);
      })
      .catch(() => {
        if (cancelled) return;
        setParticleData(buildProceduralFallback(effectiveTier));
      });
    return () => {
      cancelled = true;
    };
  }, [effectiveTier]);

  // Capture-phase window mouse/pointer/touch tracking anchored to the humanoid's eye center
  useEffect(() => {
    const updateFromClientXY = (clientX: number, clientY: number) => {
      const w = Math.max(1, window.innerWidth);
      const h = Math.max(1, window.innerHeight);
      const nx = (clientX - EYE_SCREEN_X * w) / (0.5 * w);
      const dy = clientY - EYE_SCREEN_Y * h;
      const ny = dy / (dy < 0 ? 0.35 * h : 0.56 * h);
      pointerRef.current.x = THREE.MathUtils.clamp(nx, -1, 1);
      pointerRef.current.y = THREE.MathUtils.clamp(ny, -1, 1);
      pointerRef.current.inside = true;
    };

    const onPointerOrMouseMove = (e: MouseEvent | PointerEvent) => {
      updateFromClientXY(e.clientX, e.clientY);
    };

    const onTouchMove = (e: TouchEvent) => {
      if (e.touches && e.touches.length > 0) {
        updateFromClientXY(e.touches[0].clientX, e.touches[0].clientY);
      }
    };

    const onLeaveViewport = (e: MouseEvent) => {
      if (!e.relatedTarget) {
        pointerRef.current.inside = false;
      }
    };

    const onWindowBlur = () => {
      pointerRef.current.inside = false;
    };

    window.addEventListener("pointermove", onPointerOrMouseMove, {
      passive: true,
      capture: true,
    });
    window.addEventListener("mousemove", onPointerOrMouseMove, {
      passive: true,
      capture: true,
    });
    window.addEventListener("mouseover", onPointerOrMouseMove, {
      passive: true,
      capture: true,
    });
    window.addEventListener("touchmove", onTouchMove, {
      passive: true,
      capture: true,
    });
    window.addEventListener("touchstart", onTouchMove, {
      passive: true,
      capture: true,
    });
    document.addEventListener("mouseout", onLeaveViewport, { passive: true });
    window.addEventListener("blur", onWindowBlur);

    return () => {
      window.removeEventListener("pointermove", onPointerOrMouseMove, true);
      window.removeEventListener("mousemove", onPointerOrMouseMove, true);
      window.removeEventListener("mouseover", onPointerOrMouseMove, true);
      window.removeEventListener("touchmove", onTouchMove, true);
      window.removeEventListener("touchstart", onTouchMove, true);
      document.removeEventListener("mouseout", onLeaveViewport);
      window.removeEventListener("blur", onWindowBlur);
    };
  }, []);

  // Synthesized Web Audio birth & shockwave sound ("the birth has a sound")
  const ensureAudioContext = useCallback(async () => {
    if (typeof window === "undefined") return null;
    const Ctor =
      window.AudioContext ||
      (window as Window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
    if (!Ctor) return null;

    let ctx = audioCtxRef.current;
    if (!ctx) {
      ctx = new Ctor();
      audioCtxRef.current = ctx;
    }
    if (ctx.state === "suspended") {
      try {
        await ctx.resume();
      } catch {
        return ctx;
      }
    }
    return ctx;
  }, []);

  const playBirthShockwaveSound = useCallback(() => {
    if (!sfxEnabledRef.current) return;
    const ctx = audioCtxRef.current;
    if (!ctx || ctx.state !== "running") return;

    const now = ctx.currentTime;
    const master = ctx.createGain();
    const compressor = ctx.createDynamicsCompressor();
    compressor.threshold.setValueAtTime(-20, now);
    compressor.ratio.setValueAtTime(8, now);
    master.gain.setValueAtTime(0.0001, now);
    master.gain.exponentialRampToValueAtTime(0.65, now + 0.03);
    master.gain.exponentialRampToValueAtTime(0.0001, now + 2.05);
    master.connect(compressor).connect(ctx.destination);

    const sub = ctx.createOscillator();
    const subGain = ctx.createGain();
    sub.type = "sine";
    sub.frequency.setValueAtTime(78, now);
    sub.frequency.exponentialRampToValueAtTime(38, now + 0.88);
    subGain.gain.setValueAtTime(0.0001, now);
    subGain.gain.exponentialRampToValueAtTime(0.48, now + 0.035);
    subGain.gain.exponentialRampToValueAtTime(0.0001, now + 0.96);
    sub.connect(subGain).connect(master);
    sub.start(now);
    sub.stop(now + 1.0);

    const shimmer = ctx.createOscillator();
    const shimmerGain = ctx.createGain();
    shimmer.type = "triangle";
    shimmer.frequency.setValueAtTime(160, now + 0.06);
    shimmer.frequency.exponentialRampToValueAtTime(640, now + 0.74);
    shimmer.frequency.exponentialRampToValueAtTime(240, now + 1.45);
    shimmerGain.gain.setValueAtTime(0.0001, now + 0.05);
    shimmerGain.gain.exponentialRampToValueAtTime(0.18, now + 0.34);
    shimmerGain.gain.exponentialRampToValueAtTime(0.0001, now + 1.52);
    shimmer.connect(shimmerGain).connect(master);
    shimmer.start(now + 0.05);
    shimmer.stop(now + 1.56);

    const dur = 1.45;
    const buf = ctx.createBuffer(1, Math.ceil(ctx.sampleRate * dur), ctx.sampleRate);
    const ch = buf.getChannelData(0);
    for (let i = 0; i < ch.length; i++) {
      ch[i] = (Math.random() * 2 - 1) * (1 - i / ch.length);
    }
    const noise = ctx.createBufferSource();
    const filter = ctx.createBiquadFilter();
    const noiseGain = ctx.createGain();
    noise.buffer = buf;
    filter.type = "bandpass";
    filter.frequency.setValueAtTime(780, now + 0.12);
    filter.frequency.exponentialRampToValueAtTime(180, now + 1.42);
    filter.Q.setValueAtTime(0.75, now);
    noiseGain.gain.setValueAtTime(0.0001, now + 0.1);
    noiseGain.gain.exponentialRampToValueAtTime(0.2, now + 0.32);
    noiseGain.gain.exponentialRampToValueAtTime(0.0001, now + 1.52);
    noise.connect(filter).connect(noiseGain).connect(master);
    noise.start(now + 0.1);
    noise.stop(now + 1.56);
  }, []);

  useEffect(() => {
    const unlock = () => {
      if (sfxEnabledRef.current) void ensureAudioContext();
    };
    window.addEventListener("pointerdown", unlock, { once: true, capture: true });
    window.addEventListener("keydown", unlock, { once: true, capture: true });
    return () => {
      window.removeEventListener("pointerdown", unlock, true);
      window.removeEventListener("keydown", unlock, true);
    };
  }, [ensureAudioContext]);

  useEffect(
    () => () => {
      const ctx = audioCtxRef.current;
      audioCtxRef.current = null;
      if (ctx && ctx.state !== "closed") {
        void ctx.close();
      }
    },
    []
  );

  const brainEvent = useMemo(() => {
    if (!trace) return null;
    const hasTool = Boolean(trace.tool);
    return {
      id: trace.n,
      tone: hasTool ? 0.82 : 0.24,
    };
  }, [trace]);

  const triggerRebirth = useCallback(async () => {
    const ctx = await ensureAudioContext();
    if (ctx && ctx.state === "running" && sfxEnabledRef.current) {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(196, now);
      osc.frequency.exponentialRampToValueAtTime(392, now + 0.42);
      gain.gain.setValueAtTime(0.0001, now);
      gain.gain.exponentialRampToValueAtTime(0.09, now + 0.05);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.48);
      osc.connect(gain).connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.5);
    }
    setAssemblyRun((r) => r + 1);
  }, [ensureAudioContext]);

  const cycleQuality = useCallback(() => {
    setQualityMode((prev) =>
      prev === "auto" ? "high" : prev === "high" ? "balanced" : "auto"
    );
  }, []);

  const formattedPts = particleData
    ? `${Math.round(particleData.count / 1000)}K PTS`
    : "300K PTS";

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "none",
        overflow: "hidden",
      }}
    >
      <AudioLevelProbe targetRef={audioLevelRef} />
      {/* Subtle atmospheric vignette + ultra-faint holographic scanline veil */}
      <div
        aria-hidden="true"
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(115% 88% at 50% 44%, rgba(0,0,0,0) 42%, rgba(2,6,12,0.52) 78%, rgba(1,4,9,0.88) 100%), repeating-linear-gradient(to bottom, rgba(79,210,255,0.014) 0 1px, transparent 1px 3px)",
          zIndex: 1,
        }}
      />

      {particleData && (
        <div style={{ position: "absolute", inset: 0, zIndex: 2 }}>
          <Canvas
            style={{ width: "100%", height: "100%", display: "block" }}
            camera={{ position: [0, CAM_Y, CAM_Z], fov: 38 }}
            dpr={effectiveTier === "high" ? [1, 1.5] : 1}
            gl={{
              antialias: false,
              alpha: true,
              powerPreference: "high-performance",
              toneMapping: THREE.NoToneMapping,
            }}
            onCreated={({ gl }) => {
              gl.setClearColor(0x000000, 0);
              gl.outputColorSpace = THREE.SRGBColorSpace;
              gl.toneMapping = THREE.NoToneMapping;
            }}
          >
            <HumanoidPointCloud
              data={particleData}
              state={state}
              reducedMotion={reducedMotion}
              audioLevelRef={audioLevelRef}
              pointerRef={pointerRef}
              assemblyRun={assemblyRun}
              pulseSeq={pulseSignal}
              brainEvent={brainEvent}
              onAssemblyStateChange={setAssembling}
              onShockwaveTrigger={playBirthShockwaveSound}
              onLowFpsDetected={() => setAutoFallback(true)}
            />
          </Canvas>
        </div>
      )}

      {/* Compact Male Humanoid Telemetry & Controls Pill (portaled to body so 3D camera transforms never shift it) */}
      {mounted &&
        createPortal(
          <div
            style={{
              position: "fixed",
              left: 16,
              bottom: 18,
              zIndex: 34,
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "5px 8px",
              borderRadius: 999,
              background: "rgba(4, 10, 18, 0.72)",
              border: "1px solid rgba(79, 210, 255, 0.20)",
              backdropFilter: "blur(10px)",
              WebkitBackdropFilter: "blur(10px)",
              pointerEvents: "auto",
              fontFamily: "var(--font-mono)",
              fontSize: 9.5,
              letterSpacing: "0.14em",
              color: "rgba(191, 230, 255, 0.82)",
            }}
          >
            <span
              title="Active GPU particle count"
              style={{
                padding: "2px 6px",
                color: assembling ? "#ffb347" : "#4fd2ff",
                fontWeight: 600,
              }}
            >
              {assembling ? "ASSEMBLING" : formattedPts}
            </span>

            <button
              type="button"
              onClick={() => void triggerRebirth()}
              title="Replay figure-of-light birth assembly & radial shockwave"
              style={{
                appearance: "none",
                border: "1px solid rgba(79, 210, 255, 0.24)",
                background: "rgba(79, 210, 255, 0.08)",
                color: "#d7f1ff",
                borderRadius: 999,
                padding: "3px 8px",
                fontSize: 9,
                letterSpacing: "0.14em",
                fontFamily: "inherit",
                cursor: "pointer",
              }}
            >
              REBIRTH
            </button>

            <button
              type="button"
              onClick={cycleQuality}
              title="Cycle particle density (AUTO 300K / LOCKED 300K / BALANCED)"
              style={{
                appearance: "none",
                border: "1px solid transparent",
                background: "transparent",
                color: "rgba(165, 212, 240, 0.76)",
                borderRadius: 999,
                padding: "3px 6px",
                fontSize: 9,
                letterSpacing: "0.12em",
                fontFamily: "inherit",
                cursor: "pointer",
              }}
            >
              {qualityMode === "auto"
                ? "AUTO"
                : qualityMode === "high"
                ? "300K"
                : "BAL"}
            </button>

            <button
              type="button"
              onClick={async () => {
                const next = !sfxEnabled;
                setSfxEnabled(next);
                if (next) await ensureAudioContext();
              }}
              title="Toggle birth & shockwave sound synthesis"
              style={{
                appearance: "none",
                border: "1px solid transparent",
                background: "transparent",
                color: sfxEnabled ? "#4fd2ff" : "rgba(148, 163, 184, 0.55)",
                borderRadius: 999,
                padding: "3px 6px",
                fontSize: 9,
                letterSpacing: "0.12em",
                fontFamily: "inherit",
                cursor: "pointer",
              }}
            >
              {sfxEnabled ? "SFX ON" : "SFX OFF"}
            </button>

            {onToggleConstellation && (
              <button
                type="button"
                onClick={onToggleConstellation}
                title="Toggle surrounding 18-agent constellation visibility"
                style={{
                  appearance: "none",
                  border: "1px solid transparent",
                  background: "transparent",
                  color: constellationVisible
                    ? "#4fd2ff"
                    : "rgba(148, 163, 184, 0.55)",
                  borderRadius: 999,
                  padding: "3px 6px",
                  fontSize: 9,
                  letterSpacing: "0.12em",
                  fontFamily: "inherit",
                  cursor: "pointer",
                }}
              >
                {constellationVisible ? "WEB ON" : "PURE"}
              </button>
            )}
          </div>,
          document.body
        )}
    </div>
  );
}
