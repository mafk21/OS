"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import * as THREE from "three";
import type { OrbState } from "./ApexHeroOrb";
import { useJarvis, useJarvisAudioLevel, type TraceEvent } from "./JarvisBridge";

const PORTRAIT_URL = "/hologram/male_portrait.png";
const DEPTH_URL = "/hologram/male_depth.png";

const WORLD_W = 7.4;
const CAM_Y = 0.02;
const CAM_Z = 6.85;
const DEPTH_Z_MIN = -1.60;
const DEPTH_Z_SPAN = 3.20;

const Y_PIVOT = -0.68;
const Z_PIVOT = 0.08;
const TORSO_Y_PIVOT = -1.85;

const ASSEMBLY_DURATION_SECONDS = 2.85;
const SHOCKWAVE_DURATION_SECONDS = 2.4;
const MOOD_BLOOM_SECONDS = 0.68;

// Screen-space eye/head reference center (50% X, 38% Y from top of viewport)
const EYE_SCREEN_X = 0.5;
const EYE_SCREEN_Y = 0.38;

const MAX_HEAD_YAW = 0.36; // ~21 deg sleek 3D head turn
const MAX_HEAD_PITCH_UP = 0.26; // ~15 deg 3D chin lift
const MAX_HEAD_PITCH_DOWN = 0.28; // ~16 deg 3D downward nod

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
  idle: { cyan: 0.14, warm: 0.16, zone: 0.06, tone: 0.34, shimmer: 0.20 },
  listening: { cyan: 0.60, warm: 0.11, zone: 0.36, tone: 0.05, shimmer: 0.48 },
  thinking: { cyan: 0.22, warm: 0.62, zone: 0.42, tone: 0.78, shimmer: 0.62 },
  speaking: { cyan: 0.24, warm: 0.52, zone: 0.32, tone: 0.86, shimmer: 0.52 },
};

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
  return Math.sign(clamped) * Math.pow(mag, 0.86);
}

/**
 * O(N) 1024-bin counting sort ordering particles back-to-front by world Z (`wz` ascending)
 * so foreground 3D head/torso naturally occlude deep-space waves & rear-skull shell in one GPU pass.
 */
function sortParticlesBackToFront(raw: HumanoidParticleData): HumanoidParticleData {
  const n = raw.count;
  const BINS = 1024;
  const zMin = -3.0;
  const zInvSpan = (BINS - 1) / 5.6; // covers [-3.0 .. +2.6]
  const counts = new Int32Array(BINS);
  const binOf = new Uint16Array(n);

  const srcPos = raw.positions;
  for (let i = 0; i < n; i++) {
    const z = srcPos[i * 3 + 2];
    let b = ((z - zMin) * zInvSpan) | 0;
    if (b < 0) b = 0;
    else if (b >= BINS) b = BINS - 1;
    binOf[i] = b;
    counts[b] += 1;
  }

  const offsets = new Int32Array(BINS);
  let sum = 0;
  for (let b = 0; b < BINS; b++) {
    offsets[b] = sum;
    sum += counts[b];
  }

  const positions = new Float32Array(n * 3);
  const colors = new Float32Array(n * 3);
  const normals = new Float32Array(n * 3);
  const traits = new Float32Array(n * 4);
  const assemblySource = new Float32Array(n * 3);
  const meta = new Float32Array(n * 3);
  const rig = new Float32Array(n * 2);

  const srcCol = raw.colors;
  const srcNrm = raw.normals;
  const srcTr = raw.traits;
  const srcAsm = raw.assemblySource;
  const srcMeta = raw.meta;
  const srcRig = raw.rig;

  for (let i = 0; i < n; i++) {
    const dst = offsets[binOf[i]]++;
    const s3 = i * 3;
    const d3 = dst * 3;
    positions[d3] = srcPos[s3];
    positions[d3 + 1] = srcPos[s3 + 1];
    positions[d3 + 2] = srcPos[s3 + 2];

    colors[d3] = srcCol[s3];
    colors[d3 + 1] = srcCol[s3 + 1];
    colors[d3 + 2] = srcCol[s3 + 2];

    normals[d3] = srcNrm[s3];
    normals[d3 + 1] = srcNrm[s3 + 1];
    normals[d3 + 2] = srcNrm[s3 + 2];

    assemblySource[d3] = srcAsm[s3];
    assemblySource[d3 + 1] = srcAsm[s3 + 1];
    assemblySource[d3 + 2] = srcAsm[s3 + 2];

    meta[d3] = srcMeta[s3];
    meta[d3 + 1] = srcMeta[s3 + 1];
    meta[d3 + 2] = srcMeta[s3 + 2];

    const s4 = i * 4;
    const d4 = dst * 4;
    traits[d4] = srcTr[s4];
    traits[d4 + 1] = srcTr[s4 + 1];
    traits[d4 + 2] = srcTr[s4 + 2];
    traits[d4 + 3] = srcTr[s4 + 3];

    const s2 = i * 2;
    const d2 = dst * 2;
    rig[d2] = srcRig[s2];
    rig[d2 + 1] = srcRig[s2 + 1];
  }

  return {
    count: n,
    tier: raw.tier,
    worldH: raw.worldH,
    positions,
    colors,
    normals,
    traits,
    assemblySource,
    meta,
    rig,
  };
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
  const count = tier === "high" ? 260000 : tier === "medium" ? 95000 : 42000;
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
    let snx = 0;
    let sny = 0;
    let snz = 1;

    if (isWave) {
      wx = (s1 - 0.5) * WORLD_W;
      const ribbon = Math.floor(s2 * 22) / 22;
      wz = -1.1 - (Math.floor(s2 * 22) % 4) * 0.36 + Math.cos(wx * 1.4 - ribbon * 4.0) * 0.22;
      wy = -0.25 + (ribbon - 0.5) * 1.35 + Math.sin(wx * 1.6 + ribbon * 5.0) * 0.22;
      region = 0.12;
      if (s2 < 0.35) {
        r = 0.95;
        g = 0.62;
        b = 0.2;
        warm = 0.8;
        cyan = 0.1;
      }
    } else if (s1 < 0.56) {
      const band = Math.floor(s2 * 96) / 96;
      const theta = (s3 - 0.5) * Math.PI * 1.85;
      const ny = 0.09 + band * 0.56;
      const rx = 0.96 * Math.sqrt(Math.max(0.04, 1 - Math.pow((ny - 0.35) / 0.28, 2)));
      wx = Math.sin(theta) * rx;
      wy = (0.5 - ny) * worldH;
      wz = Math.cos(theta) * rx * 1.15;
      snx = Math.sin(theta);
      snz = Math.cos(theta);
      skinW = 1;
      region = 0.7;
      const center =
        Math.max(0, Math.cos(theta)) *
        Math.exp(-Math.pow(wx / 0.34, 2)) *
        Math.exp(-Math.pow((ny - 0.42) / 0.18, 2));
      r = THREE.MathUtils.lerp(0.1, 1.0, center);
      g = THREE.MathUtils.lerp(0.84, 0.64, center);
      b = THREE.MathUtils.lerp(1.0, 0.22, center);
      warm = center;
      cyan = 1 - center * 0.8;
      voiceW = center > 0.35 ? 0.85 : 0;
    } else {
      const band = Math.floor(s2 * 64) / 64;
      const ny = 0.62 + band * 0.35;
      const theta = (s3 - 0.5) * Math.PI * 1.7;
      const span = 0.52 + Math.pow((ny - 0.62) / 0.35, 0.78) * 2.25;
      wx = Math.sin(theta) * span;
      wy = (0.5 - ny) * worldH;
      wz = Math.cos(theta) * (0.54 + (ny - 0.62) * 0.85);
      snx = Math.sin(theta);
      snz = Math.cos(theta);
      skinW = Math.max(0, 1 - (ny - 0.62) / 0.15);
      region = 0.4;
      const spine = Math.max(0, Math.cos(theta)) * Math.exp(-Math.pow(wx / 0.22, 2));
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
    normals[p3] = snx;
    normals[p3 + 1] = sny;
    normals[p3 + 2] = snz;
    traits[p4] = Math.abs(snz) < 0.35 ? 0.85 : 0.15;
    traits[p4 + 1] = warm;
    traits[p4 + 2] = cyan;
    traits[p4 + 3] = voiceW;

    const angle = s1 * Math.PI * 2;
    const dist = 2.8 + s2 * 2.6;
    assemblySource[p3] = Math.cos(angle) * dist;
    assemblySource[p3 + 1] = (s3 - 0.5) * worldH * 1.25;
    assemblySource[p3 + 2] = -2.2 + (s2 - 0.5) * 2.8;

    meta[p3] = isWave ? 0.52 + s3 * 0.2 : 0.03 + s1 * 0.48;
    meta[p3 + 1] = Math.min(1, Math.hypot(wx / 3.4, (wy - 0.42) / 2.6));
    meta[p3 + 2] = s3;
    rig[p2] = skinW;
    rig[p2 + 1] = region;
  }

  return sortParticlesBackToFront({
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
  });
}

function buildHumanoidParticles(
  assets: DecodedAssets,
  tier: RenderTier
): HumanoidParticleData {
  const cached = cachedParticleTiers.get(tier);
  if (cached) return cached;

  const { width: W, height: H, portrait, depth } = assets;
  const step = tier === "high" ? 1 : tier === "medium" ? 2 : 3;
  const worldH = WORLD_W * (H / W);

  // 1. Decode 4.0-unit 3D sculptural depth field (`[-2.40 .. +1.60]`) + light 3x3 float smoothing on figure
  const rawDepth = new Float32Array(W * H);
  for (let i = 0, n = W * H; i < n; i++) {
    rawDepth[i] = (depth[i * 4] / 255) * DEPTH_Z_SPAN + DEPTH_Z_MIN;
  }
  const smoothDepth = new Float32Array(W * H);
  for (let y = 0; y < H; y++) {
    const y0 = y > 0 ? y - 1 : 0;
    const y2 = y < H - 1 ? y + 1 : H - 1;
    const r0 = y0 * W;
    const r1 = y * W;
    const r2 = y2 * W;
    for (let x = 0; x < W; x++) {
      const regB = depth[(r1 + x) * 4 + 2] / 255;
      // Preserve crisp random Z on crown sparks (`regB > 0.85`) and wave planes (`regB < 0.24`)
      if (regB < 0.24 || regB > 0.85) {
        smoothDepth[r1 + x] = rawDepth[r1 + x];
        continue;
      }
      const x0 = x > 0 ? x - 1 : 0;
      const x2 = x < W - 1 ? x + 1 : W - 1;
      smoothDepth[r1 + x] =
        (rawDepth[r0 + x0] +
          rawDepth[r0 + x] * 2 +
          rawDepth[r0 + x2] +
          rawDepth[r1 + x0] * 2 +
          rawDepth[r1 + x] * 4 +
          rawDepth[r1 + x2] * 2 +
          rawDepth[r2 + x0] +
          rawDepth[r2 + x] * 2 +
          rawDepth[r2 + x2]) *
        0.0625;
    }
  }

  // Lush volumetric 3D layers:
  // 1) waveBridgeCount: seamless behind-head 3D wave ribbons (`Z ~ -0.96`, `skinW = 0`)
  // 2) internalCoreCount: internal golden 3D cerebral & cervical spinal core strictly inside skull/neck (`r <= 0.34`)
  // 3) emberCount: subtle deep-space floating light motes strictly outside center face
  const waveBridgeCount = tier === "high" ? 20000 : tier === "medium" ? 8000 : 3600;
  const internalCoreCount = tier === "high" ? 12000 : tier === "medium" ? 5000 : 2200;
  const emberCount = tier === "high" ? 950 : tier === "medium" ? 450 : 220;

  const cols = Math.ceil(W / step);
  const rows = Math.ceil(H / step);
  const maxCount = cols * rows + waveBridgeCount + internalCoreCount + emberCount;

  const positions = new Float32Array(maxCount * 3);
  const colors = new Float32Array(maxCount * 3);
  const normals = new Float32Array(maxCount * 3);
  const traits = new Float32Array(maxCount * 4);
  const assemblySource = new Float32Array(maxCount * 3);
  const meta = new Float32Array(maxCount * 3);
  const rig = new Float32Array(maxCount * 2);

  let count = 0;

  const pushParticle = (
    wx: number,
    wy: number,
    wz: number,
    rLin: number,
    gLin: number,
    bLin: number,
    snx: number,
    sny: number,
    snz: number,
    edge: number,
    warm: number,
    cyan: number,
    voiceW: number,
    skinW: number,
    regionClass: number,
    nxHint: number,
    nyHint: number
  ) => {
    const seed = hash01(count * 1.37 + nxHint * 17.3 + nyHint * 31.7);

    let assemblyPhase = 0.02 + seed * 0.12;
    if (regionClass > 0.85) {
      assemblyPhase = 0.48 + seed * 0.2;
    } else if (skinW > 0.55) {
      const headDist = Math.min(
        1,
        Math.hypot((nxHint - 0.5) / 0.16, (nyHint - 0.38) / 0.3)
      );
      assemblyPhase = 0.01 + headDist * 0.16 + seed * 0.08;
    } else if (regionClass > 0.55) {
      assemblyPhase = 0.16 + seed * 0.12;
    } else if (regionClass > 0.25) {
      const shDist = Math.min(1, Math.abs(nxHint - 0.5) / 0.38);
      assemblyPhase = 0.32 + shDist * 0.2 + seed * 0.09;
    } else {
      const waveDist = Math.min(1, Math.max(0, (Math.abs(nxHint - 0.5) - 0.1) / 0.4));
      assemblyPhase = 0.44 + waveDist * 0.22 + seed * 0.08;
    }

    const streamSide = nxHint < 0.5 ? -1 : 1;
    const swirlAngle = seed * Math.PI * 2 + nyHint * 3.4 * streamSide;
    const radialSpread = 1.85 + hash01(count * 2.71 + 3.1) * 2.75;
    const srcX =
      wx * 0.38 +
      Math.cos(swirlAngle) * radialSpread +
      streamSide * (0.8 + hash01(count * 0.91 + 7.4) * 1.25);
    const srcY =
      wy * 0.58 +
      Math.sin(swirlAngle) * (0.9 + hash01(count * 1.83 + 5.2) * 1.35) -
      0.3;
    const srcZ = -2.1 + (hash01(count * 3.19 + 1.7) - 0.35) * 2.6;

    const rxBloom = (nxHint - 0.5) / 0.46;
    const ryBloom = (nyHint - 0.4) / 0.62;
    const radialZone = Math.min(1, Math.hypot(rxBloom, ryBloom));

    const o3 = count * 3;
    const o4 = count * 4;
    const o2 = count * 2;

    positions[o3] = wx;
    positions[o3 + 1] = wy;
    positions[o3 + 2] = wz;

    colors[o3] = rLin;
    colors[o3 + 1] = gLin;
    colors[o3 + 2] = bLin;

    normals[o3] = snx;
    normals[o3 + 1] = sny;
    normals[o3 + 2] = snz;

    traits[o4] = edge;
    traits[o4 + 1] = warm;
    traits[o4 + 2] = cyan;
    traits[o4 + 3] = voiceW;

    assemblySource[o3] = srcX;
    assemblySource[o3 + 1] = srcY;
    assemblySource[o3 + 2] = srcZ;

    meta[o3] = assemblyPhase;
    meta[o3 + 1] = radialZone;
    meta[o3 + 2] = seed;

    rig[o2] = skinW;
    rig[o2 + 1] = regionClass;

    count += 1;
  };

  // --- LAYER A: Sculpted Front 3D Surface + Outer 3D Waves + 3D Crown Sparks ---
  const sampleDepthWorld = (sx: number, sy: number): number => {
    const cx = sx < 0 ? 0 : sx >= W ? W - 1 : sx;
    const cy = sy < 0 ? 0 : sy >= H ? H - 1 : sy;
    return smoothDepth[cy * W + cx];
  };
  const inv2Dx = 1 / (2 * ((step / Math.max(1, W - 1)) * WORLD_W));
  const inv2Dy = 1 / (2 * ((step / Math.max(1, H - 1)) * worldH));

  for (let y = 0; y < H; y += step) {
    const ny = y / (H - 1);
    const wyScreen = (0.5 - ny) * worldH;

    for (let x = 0; x < W; x += step) {
      const pIdx = (y * W + x) * 4;
      const regionClass = depth[pIdx + 2] / 255;
      // Skip flat 2D outer bloom halo pixels (`regionClass ~ 0.02`) so zero flat 2D aura ring exists in 3D!
      if (regionClass < 0.06) continue;

      const r8 = portrait[pIdx];
      const g8 = portrait[pIdx + 1];
      const b8 = portrait[pIdx + 2];
      const max8 = r8 > g8 ? (r8 > b8 ? r8 : b8) : g8 > b8 ? g8 : b8;
      const brightness = max8 / 255;

      const minBright = regionClass > 0.85 ? 0.11 : 0.038;
      if (brightness < minBright) continue;

      const skinWeight = depth[pIdx + 1] / 255;
      const nx = x / (W - 1);
      const wxScreen = (nx - 0.5) * WORLD_W;
      const faceAbsX = Math.abs(nx - 0.5);

      const jitter = (hash01(x * 0.37 + y * 0.73) - 0.5) * 0.022;
      const wz = smoothDepth[y * W + x] + jitter;

      const perspScale = (CAM_Z - wz) / CAM_Z;
      const wx = wxScreen * perspScale;
      const wy = (wyScreen - CAM_Y) * perspScale + CAM_Y;

      let snx = 0;
      let sny = 0;
      let snz = 1;
      if (regionClass >= 0.24 && regionClass <= 0.85) {
        const dzdx = (sampleDepthWorld(x + step, y) - sampleDepthWorld(x - step, y)) * inv2Dx;
        const dzdy = (sampleDepthWorld(x, y - step) - sampleDepthWorld(x, y + step)) * inv2Dy;
        snx = -dzdx;
        sny = -dzdy;
        snz = 1.0;
        const invLen = 1 / (Math.hypot(snx, sny, snz) || 1);
        snx *= invLen;
        sny *= invLen;
        snz *= invLen;
      }

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

      const edgeTrait = snz < 0.52 ? 1.0 : 0.0;

      pushParticle(
        wx,
        wy,
        wz,
        SRGB_TO_LINEAR[r8],
        SRGB_TO_LINEAR[g8],
        SRGB_TO_LINEAR[b8],
        snx,
        sny,
        snz,
        edgeTrait,
        warmRatio,
        cyanRatio,
        voiceWeight,
        skinWeight,
        regionClass,
        nx,
        ny
      );
    }
  }

  // --- LAYER B: Seamless 3D Wave Continuity Behind Head (`ny = 0.33..0.63`, `Z ~ -0.92`, `skinW = 0`) ---
  // Interpolates real left & right wave scanlines from `male_portrait.png` strictly behind the jaw/ears
  // (never near the bald crown `ny < 0.33`!), eliminating any silhouette cutout gap when the head turns.
  for (let i = 0; i < waveBridgeCount; i++) {
    const s1 = hash01(i * 2.13 + 0.61);
    const s2 = hash01(i * 4.67 + 1.83);
    const s3 = hash01(i * 6.31 + 3.07);

    const bRow = Math.min(H - 1, Math.floor((0.33 + s1 * 0.30) * (H - 1)));
    const xLeft = Math.min(W - 1, Math.floor((0.20 + s2 * 0.08) * (W - 1)));
    const xRight = Math.min(W - 1, Math.floor((0.72 + s2 * 0.08) * (W - 1)));
    const pL = (bRow * W + xLeft) * 4;
    const pR = (bRow * W + xRight) * 4;

    const r8 = Math.round((portrait[pL] * (1 - s3) + portrait[pR] * s3) * 0.85);
    const g8 = Math.round((portrait[pL + 1] * (1 - s3) + portrait[pR + 1] * s3) * 0.85);
    const b8 = Math.round((portrait[pL + 2] * (1 - s3) + portrait[pR + 2] * s3) * 0.85);
    const max8 = r8 > g8 ? (r8 > b8 ? r8 : b8) : g8 > b8 ? g8 : b8;
    if (max8 / 255 < 0.05) continue;

    const bNy = bRow / (H - 1);
    const bNx = 0.27 + 0.46 * s3;
    const wz =
      -0.92 +
      0.32 * Math.sin(bNy * 22.0 + bNx * 3.5) +
      0.18 * Math.cos(bNx * 8.5 - bNy * 12.0);
    const perspB = (CAM_Z - wz) / CAM_Z;
    const wx = (bNx - 0.5) * WORLD_W * perspB;
    const wy = ((0.5 - bNy) * worldH - CAM_Y) * perspB + CAM_Y;

    const warmRatio = r8 > b8 * 1.2 ? 0.72 : 0.05;
    const cyanRatio = b8 >= r8 ? 0.78 : 0.1;

    pushParticle(
      wx,
      wy,
      wz,
      SRGB_TO_LINEAR[r8],
      SRGB_TO_LINEAR[g8],
      SRGB_TO_LINEAR[b8],
      0,
      0,
      1,
      0,
      warmRatio,
      cyanRatio,
      0,
      0,
      0.12,
      bNx,
      bNy
    );
  }

  // --- LAYER C: Internal Golden 3D Cerebral & Cervical Spinal Core (`r <= 0.34`, never touches silhouette) ---
  for (let i = 0; i < internalCoreCount; i++) {
    const s1 = hash01(i * 3.11 + 1.41);
    const s2 = hash01(i * 5.23 + 2.71);
    const s3 = hash01(i * 7.09 + 0.33);

    const nyRaw = 0.22 + s1 * 0.70;
    const nyC = Math.round(nyRaw * 108) / 108 + (s3 - 0.5) * 0.0025;
    const isBrain = nyC < 0.55;
    const rad = isBrain ? 0.02 + s2 * 0.32 : 0.015 + s2 * 0.105;
    const ang = s3 * Math.PI * 2;

    const wx = Math.cos(ang) * rad;
    const wy = (0.5 - nyC) * worldH;
    const wz = isBrain
      ? 0.22 + Math.sin(ang) * rad * 0.85
      : 0.12 + Math.sin(ang) * rad * 0.75;

    const tCerv = THREE.MathUtils.clamp((nyC - 0.575) / (0.76 - 0.575), 0, 1);
    const skinW = 1 - tCerv * tCerv * (3 - 2 * tCerv);
    const glow = 0.42 + 0.44 * hash01(i * 1.97 + 4.2);
    const cR = Math.pow(1.0 * glow, 2.2);
    const cG = Math.pow(0.66 * glow, 2.2);
    const cB = Math.pow(0.20 * glow, 2.2);
    const voiceW = isBrain ? 0.48 : 0.62;

    pushParticle(
      wx,
      wy,
      wz,
      cR,
      cG,
      cB,
      0,
      0,
      1,
      0,
      0.92,
      0.06,
      voiceW,
      skinW,
      0.62,
      0.5 + wx / WORLD_W,
      nyC
    );
  }

  // --- LAYER D: Subtle Deep-Space Atmospheric Light Embers (strictly outside face zone) ---
  for (let i = 0; i < emberCount; i++) {
    const s1 = hash01(i * 5.81 + 0.29);
    const s2 = hash01(i * 8.17 + 1.19);
    const s3 = hash01(i * 3.49 + 2.63);

    const wx = (s1 - 0.5) * 6.8;
    const wy = (s2 - 0.5) * 4.0;
    const wz = -1.5 + s3 * 2.9;
    if (Math.abs(wx) < 1.38 && wy > -0.82 && wy < 1.88) continue;

    const isGold = hash01(i * 9.31) < 0.32;
    const fade = 0.30 + 0.42 * hash01(i * 2.47);
    const cR = Math.pow((isGold ? 1.0 : 0.20) * fade, 2.2);
    const cG = Math.pow((isGold ? 0.70 : 0.86) * fade, 2.2);
    const cB = Math.pow((isGold ? 0.25 : 1.0) * fade, 2.2);

    pushParticle(
      wx,
      wy,
      wz,
      cR,
      cG,
      cB,
      0,
      0,
      1,
      0,
      isGold ? 0.72 : 0,
      isGold ? 0.1 : 0.82,
      0,
      0,
      0.92,
      0.5 + wx / WORLD_W,
      0.5 - wy / worldH
    );
  }

  const built = sortParticlesBackToFront({
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
  });

  cachedParticleTiers.set(tier, built);
  return built;
}

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
uniform vec3 uCamPos;
uniform float uYaw;
uniform float uPitch;
uniform float uRoll;
uniform float uTorsoYaw;
uniform float uTorsoPitch;
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

  // 1. Living 3D wave ribbons undulating through X-Y-Z depth (region ~ 0.12)
  float waveMask = 1.0 - smoothstep(0.18, 0.28, region);
  if (waveMask > 0.001 && uEffects > 0.5) {
    float w1 = sin(p.x * 1.45 - uTime * 0.85 + p.z * 1.8) * 0.055;
    float w2 = cos(p.x * 2.75 + uTime * 0.60 - p.y * 1.65) * 0.028;
    p.y += (w1 + w2) * waveMask;
    p.z += sin(p.x * 1.15 + uTime * 0.72 + seed * 2.4) * 0.095 * waveMask;
  }

  // 2. Volumetric 3D crown sparks & foreground holographic dust drift (region > 0.85)
  if (region > 0.85 && uEffects > 0.5) {
    p.y += sin(uTime * 1.25 + seed * 6.2831853) * 0.042 + 0.010;
    p.x += cos(uTime * 0.92 + seed * 9.42477) * 0.028;
    p.z += sin(uTime * 0.84 + seed * 4.71238) * 0.046;
  }

  // 3. 3D Vocal resonance along visage & internal neural core when speaking
  if (voiceTrait > 0.40 && uVoice > 0.01 && uEffects > 0.5) {
    float vocalWave = sin(p.y * 24.0 - uTime * 14.5 + seed * 3.14) * 0.011 * uVoice;
    p.z += vocalWave * 1.65;
    p.y += vocalWave * 0.40;
  }

  // 4. 3D Ribcage breathing + secondary upper-torso 3D rotation
  float bodyWeight = (1.0 - skinW) * smoothstep(0.24, 0.48, region) * (1.0 - smoothstep(0.80, 0.90, region));
  p.y += uChest * bodyWeight;
  p.z += uChest * 0.85 * bodyWeight;

  float torsoVert = smoothstep(${TORSO_Y_PIVOT.toFixed(4)} - 0.35, -0.55, p.y);
  float torsoMask = smoothstep(0.24, 0.36, region) * (1.0 - smoothstep(0.82, 0.90, region));
  float torsoFactor = torsoVert * torsoMask * (1.0 - skinW);
  float ty = uTorsoYaw * torsoFactor;
  float tp = uTorsoPitch * torsoFactor;
  if (abs(ty) + abs(tp) > 0.0002) {
    float cty = cos(ty), sty = sin(ty);
    float ctp = cos(tp), stp = sin(tp);
    vec3 trel = vec3(p.x, p.y - (${TORSO_Y_PIVOT.toFixed(4)}), p.z);
    vec3 tr1 = vec3(trel.x * cty + trel.z * sty, trel.y, -trel.x * sty + trel.z * cty);
    vec3 tr2 = vec3(tr1.x, tr1.y * ctp - tr1.z * stp, tr1.y * stp + tr1.z * ctp);
    p = vec3(tr2.x, tr2.y + (${TORSO_Y_PIVOT.toFixed(4)}), tr2.z);

    vec3 tn1 = vec3(nrm.x * cty + nrm.z * sty, nrm.y, -nrm.x * sty + nrm.z * cty);
    vec3 tn2 = vec3(tn1.x, tn1.y * ctp - tn1.z * stp, tn1.y * stp + tn1.z * ctp);
    nrm = normalize(tn2);
  }

  // 5. True 3D Volumetric Head + Internal Brain + Cervical Spine Rotation
  // Sign convention verified across all 4 quadrants:
  //   uYaw > 0   -> nose turns RIGHT (+X)
  //   uYaw < 0   -> nose turns LEFT (-X)
  //   uPitch > 0 -> nose nods DOWN (-Y), 3D crown tilts forward (+Z)
  //   uPitch < 0 -> nose tilts UP (+Y), chin & submental shelf lift up
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
    // Natural roll around Z
    vec3 r3 = vec3(r2.x * cr - r2.y * sr, r2.x * sr + r2.y * cr, r2.z);

    p = vec3(r3.x, r3.y + (${Y_PIVOT.toFixed(4)}), r3.z + (${Z_PIVOT.toFixed(4)}));

    vec3 n1 = vec3(nrm.x * cy + nrm.z * sy, nrm.y, -nrm.x * sy + nrm.z * cy);
    vec3 n2 = vec3(n1.x, n1.y * cp - n1.z * sp, n1.y * sp + n1.z * cp);
    vec3 n3 = vec3(n2.x * cr - n2.y * sr, n2.x * sr + n2.y * cr, n2.z);
    nrm = normalize(n3);
  }

  // 6. 3D View-Normal Backface Occlusion + Grazing 3D Fresnel Rim + Directional Key/Fill + Aerial Z-Depth
  float isShellSurface = step(0.35, region) * (1.0 - step(0.80, region)) * (1.0 - smoothstep(0.58, 0.64, region) * (1.0 - smoothstep(0.64, 0.67, region)));
  vec3 viewDir = normalize(uCamPos - p);
  float ndotv = dot(nrm, viewDir);

  // Attenuate back-turned shell surfaces so far side of skull never ghosts over front face
  float backfaceVis = mix(1.0, 0.12 + 0.88 * smoothstep(-0.26, 0.22, ndotv), isShellSurface);
  float fresnelRim = isShellSurface * pow(1.0 - clamp(abs(ndotv), 0.0, 1.0), 2.15) * 0.44;

  vec3 keyLight = normalize(vec3(0.32, 0.34, 0.88));
  float lambert = clamp(dot(nrm, keyLight), 0.0, 1.0);
  float depthShade = mix(1.0, 0.76 + 0.36 * lambert, isShellSurface);

  // Aerial Z-perspective: foreground +Z pops crisply, deep -Z waves recede atmospherically into 3D space
  float aerialDepth = clamp(0.52 + 0.56 * smoothstep(-2.45, 1.35, p.z), 0.44, 1.16);

  // 7. Fluid 3D birth assembly from pure darkness
  float birthVisibility = 1.0;
  float assemblyGlow = 0.0;
  if (uAssemblyEnabled > 0.5 && uAssemblyProgress < 1.0) {
    float raw = clamp((uAssemblyProgress - assemblyPhase) / 0.34, 0.0, 1.0);
    float local = smoother(raw);
    birthVisibility = smoothstep(0.0, 0.18, raw);
    assemblyGlow = sin(local * 3.14159265) * 0.52;

    float arc = sin(local * 3.14159265);
    float curvePhase = seed * 6.2831853;
    float swirl = sin(local * 4.7123889 + curvePhase) * pow(1.0 - local, 1.85) * 0.085;

    p = mix(aAssemblySource, p, local);
    p.x += swirl;
    p.y += arc * (0.14 + seed * 0.09);
    p.z += arc * (0.18 + fract(seed * 7.13) * 0.12);
  }

  // 8. 3D Radial spherical shockwave bursting outward from sternum/heart nexus
  float shockProgress = clamp(uShockwaveProgress, 0.0, 1.0);
  vec3 shockOrigin = vec3(0.0, -0.22, 0.25);
  vec3 shockVec = p - shockOrigin;
  float shockRadius = length(shockVec);
  float travel = clamp((shockProgress - 0.05) / 0.82, 0.0, 1.0);
  float waveRadius = mix(0.08, 5.25, travel);
  float ring = 1.0 - smoothstep(0.0, 0.32, abs(shockRadius - waveRadius));
  float waveFade = smoothstep(0.02, 0.12, shockProgress) * (1.0 - smoothstep(0.80, 1.0, shockProgress));
  float coreFlash = (1.0 - smoothstep(0.08, 0.88, shockRadius)) * (1.0 - smoothstep(0.02, 0.24, shockProgress));
  float shockRing = ring * waveFade * uShockwaveActive;
  float shockCore = coreFlash * uShockwaveActive;
  float shockEnergy = max(shockRing, shockCore);

  if (shockRing > 0.001) {
    vec3 dir = shockVec / max(shockRadius, 0.0001);
    p += dir * shockRing * (1.0 - travel) * 0.072;
  }

  // 9. Four moods blooming radially outward from the face over 680ms
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

  // Travelling bio-electric pulses racing outward along wave ribbons & ascending up the golden spine
  float wavePulse = waveMask * pow(0.5 + 0.5 * sin(abs(p.x) * 2.35 - uTime * 2.25 + seed * 1.4), 5.0) * 0.42 * uEffects;
  float spinalPulse =
    warmTrait *
    (1.0 - smoothstep(0.18, 0.48, abs(p.x))) *
    pow(0.5 + 0.5 * sin(p.y * 4.4 - uTime * 2.55), 4.0) *
    (0.32 + uVoice * 0.45) *
    uEffects;

  float cyanEnergy =
    cyanTrait * stateCyan +
    edgeTrait * (0.10 + stateCyan * 0.38) +
    fresnelRim * 0.96 +
    wavePulse * 0.85 +
    moodWave * (1.0 - stateTone) * 0.34 +
    shockRing * (0.45 + travel * 0.30) +
    assemblyGlow * 0.28;

  float warmEnergy =
    warmTrait * stateWarm +
    spinalPulse * 0.92 +
    wavePulse * warmTrait * 0.55 +
    moodWave * stateTone * 0.38 +
    shockCore * 0.72 +
    shockRing * (1.0 - travel) * 0.22;

  float zoneEnergy = (1.0 - radialZone * 0.72) * stateZone;
  float totalEnergy = (cyanEnergy + warmEnergy + voiceEnergy + zoneEnergy + brainPulse * 0.48) * uEffects;

  vec3 electricCyan = vec3(0.20, 0.94, 1.0);
  vec3 moltenAmber = vec3(1.0, 0.66, 0.18);
  vec3 emeraldSignal = vec3(0.38, 1.0, 0.70);
  vec3 synapticViolet = vec3(0.68, 0.48, 1.0);

  float bt = clamp(uBrainTone, 0.0, 1.0);
  vec3 brainColor = bt < 0.5
    ? mix(electricCyan, emeraldSignal, bt * 2.0)
    : mix(synapticViolet, moltenAmber, (bt - 0.5) * 2.0);

  vec3 moodTint = mix(electricCyan, moltenAmber, clamp(stateTone, 0.0, 1.0));

  vec3 lifted = pow(max(color, vec3(0.0)), vec3(0.84)) * depthShade * aerialDepth;
  vec3 boosted =
    lifted * 1.15 +
    electricCyan * (cyanEnergy * 0.18 + fresnelRim * 0.48) +
    moltenAmber * (warmEnergy + voiceEnergy * 1.22) * 0.24 +
    brainColor * brainPulse * 0.16;

  float peak = max(boosted.r, max(boosted.g, boosted.b));
  if (peak > 1.0) {
    boosted /= peak;
  }

  vCoreColor = clamp(boosted, 0.0, 1.0);
  vCoreAlpha = birthVisibility * backfaceVis;

  float gE = clamp(totalEnergy, 0.0, 1.45);
  vec3 glowBase = mix(moodTint, vCoreColor, 0.48);
  vHaloColor =
    mix(glowBase, brainColor, clamp(brainPulse * 0.36, 0.0, 0.45)) *
    (0.64 + gE * 0.82) *
    aerialDepth;
  vHaloAlpha =
    clamp(0.024 + gE * 0.115 + shockEnergy * 0.11 + brainPulse * 0.045, 0.0, 0.24) *
    birthVisibility *
    mix(0.35, 1.0, backfaceVis);

  vec4 mvPosition = modelViewMatrix * vec4(p, 1.0);
  // True 3D perspective sizeAttenuation: closer (+Z) particles scale larger, deep (-Z) particles scale smaller!
  float perspAtten = clamp(${CAM_Z.toFixed(2)} / max(1.8, -mvPosition.z), 0.52, 1.85);

  gl_PointSize =
    uPointSize *
    uDpr *
    perspAtten *
    (1.0 + gE * 0.08 + shockEnergy * 0.16 + voiceEnergy * 0.07);
  gl_Position = projectionMatrix * mvPosition;
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

  float coreMask = exp(-d2 * 22.0) * vCoreAlpha;
  float haloMask = (exp(-d2 * 5.2) - exp(-5.2 * 0.25)) * vHaloAlpha;

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
  dragging: boolean;
  dragAzimuth: number; // interactive 3D orbit azimuth (rad)
  dragElevation: number; // interactive 3D orbit elevation (rad)
  zoomDist: number; // camera 3D distance
};

type PointsCloudProps = {
  data: HumanoidParticleData;
  state: OrbState;
  reducedMotion: boolean;
  turntable: boolean;
  audioLevelRef: React.MutableRefObject<number>;
  pointerRef: React.MutableRefObject<PointerState>;
  assemblyRun: number;
  pulseSeq: number;
  brainEvent: { id: number; tone: number } | null;
  onAssemblyStateChange: (assembling: boolean) => void;
  onShockwaveTrigger: () => void;
  onLowFpsDetected: () => void;
};

const LOOK_TARGET = new THREE.Vector3(0, 0.04, 0.08);

function HumanoidPointCloud({
  data,
  state,
  reducedMotion,
  turntable,
  audioLevelRef,
  pointerRef,
  assemblyRun,
  pulseSeq,
  brainEvent,
  onAssemblyStateChange,
  onShockwaveTrigger,
  onLowFpsDetected,
}: PointsCloudProps) {
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
    camAz: 0,
    camAzVel: 0,
    camEl: 0,
    camElVel: 0,
    camDist: CAM_Z,
    camDistVel: 0,
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
      uCamPos: { value: new THREE.Vector3(0, CAM_Y, CAM_Z) },
      uYaw: { value: 0 },
      uPitch: { value: 0 },
      uRoll: { value: 0 },
      uTorsoYaw: { value: 0 },
      uTorsoPitch: { value: 0 },
      uChest: { value: 0 },
      uAssemblyProgress: { value: reducedMotion ? 1 : 0 },
      uAssemblyEnabled: { value: reducedMotion ? 0 : 1 },
      uShockwaveActive: { value: 0 },
      uShockwaveProgress: { value: 1 },
      uTransitionProgress: { value: 1 },
      uPrevMood: { value: new THREE.Vector4(0.14, 0.16, 0.06, 0.34) },
      uNextMood: { value: new THREE.Vector4(0.14, 0.16, 0.06, 0.34) },
      uMoodShimmer: { value: 0.20 },
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

  useFrame(({ clock, gl, camera, size }, rawDt) => {
    const dt = Math.min(rawDt, 0.05);
    const t = clock.elapsedTime;
    const dpr = gl.getPixelRatio();

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

    const ptr = pointerRef.current;
    const microLifeYaw = Math.sin(t * 0.52) * 0.018 + Math.sin(t * 1.18 + 1.1) * 0.009;
    const microLifePitch = Math.sin(t * 0.68 + 0.4) * 0.014;
    const idleAutonomousYaw = Math.sin(t * 0.46) * 0.095 + Math.sin(t * 1.05 + 1.2) * 0.032;
    const idleAutonomousPitch = Math.sin(t * 0.58 + 0.6) * 0.042;

    let baseYaw = 0;
    let basePitch = 0;
    if (ptr.inside) {
      const gx = shapeGazeAxis(ptr.x);
      const gy = shapeGazeAxis(ptr.y);
      baseYaw = gx * MAX_HEAD_YAW + microLifeYaw;
      // gy > 0 when mouse is BELOW eyes -> positive pitch nods 3D head DOWN toward cursor
      // gy < 0 when mouse is ABOVE eyes -> negative pitch tilts 3D head UP toward cursor
      basePitch =
        (gy >= 0 ? gy * MAX_HEAD_PITCH_DOWN : gy * MAX_HEAD_PITCH_UP) + microLifePitch;
    } else {
      baseYaw = idleAutonomousYaw;
      basePitch = idleAutonomousPitch;
    }

    let stateYawOffset = 0;
    let statePitchOffset = 0;
    let gazeGain = 1.0;

    if (state === "listening") {
      gazeGain = 1.08;
      statePitchOffset = 0.018 + Math.sin(t * 1.45) * 0.008;
    } else if (state === "thinking") {
      gazeGain = 0.90;
      stateYawOffset = Math.sin(t * 0.72) * 0.052;
      statePitchOffset = -0.020 + Math.sin(t * 0.95) * 0.018;
    } else if (state === "speaking") {
      gazeGain = 0.96;
      stateYawOffset = Math.sin(t * 0.88) * 0.025;
      statePitchOffset = Math.sin(t * 1.85) * 0.018;
    }

    let yawTarget = THREE.MathUtils.clamp(
      baseYaw * gazeGain + stateYawOffset,
      -0.42,
      0.42
    );
    let pitchTarget = THREE.MathUtils.clamp(
      basePitch * gazeGain + statePitchOffset,
      -0.30,
      0.32
    );
    let rollTarget = -yawTarget * 0.085 + (state === "listening" ? 0.014 : 0);

    // True 3D Perspective Camera Orbit:
    // - Subtle autonomous 3D figure-8 orbit so scene feels tangibly 3D even with stationary mouse
    // - Cursor-driven opposing 3D perspective parallax (~+-10 deg azimuth, ~+-5 deg elevation)
    // - Plus smooth click-drag 3D inspection orbit (up to +-30 deg) or 3D ORBIT showcase
    const breathAz = Math.sin(t * 0.38) * 0.062 + Math.cos(t * 0.71) * 0.020;
    const breathEl = Math.cos(t * 0.44) * 0.032;
    const cursorCamAz = ptr.inside ? -shapeGazeAxis(ptr.x) * 0.16 + breathAz * 0.45 : breathAz;
    const cursorCamEl = ptr.inside ? shapeGazeAxis(ptr.y) * 0.09 + breathEl * 0.45 : breathEl;
    const turntableAz = turntable ? Math.sin(t * 0.55) * 0.38 : 0;
    const turntableEl = turntable ? Math.cos(t * 0.37) * 0.12 : 0;

    let camAzTarget = THREE.MathUtils.clamp(
      cursorCamAz + ptr.dragAzimuth + turntableAz,
      -0.54,
      0.54
    );
    let camElTarget = THREE.MathUtils.clamp(
      cursorCamEl + ptr.dragElevation + turntableEl,
      -0.34,
      0.34
    );
    const camDistTarget = reducedMotion ? CAM_Z : ptr.zoomDist;

    if (reducedMotion) {
      yawTarget *= 0.3;
      pitchTarget *= 0.3;
      rollTarget = 0;
      camAzTarget *= 0.25;
      camElTarget *= 0.25;
    }

    const sp = springs.current;
    [sp.yaw, sp.yawVel] = criticallyDampedSpring(sp.yaw, sp.yawVel, yawTarget, 10.5, dt);
    [sp.pitch, sp.pitchVel] = criticallyDampedSpring(
      sp.pitch,
      sp.pitchVel,
      pitchTarget,
      10.5,
      dt
    );
    [sp.roll, sp.rollVel] = criticallyDampedSpring(sp.roll, sp.rollVel, rollTarget, 8.5, dt);

    [sp.torsoYaw, sp.torsoYawVel] = criticallyDampedSpring(
      sp.torsoYaw,
      sp.torsoYawVel,
      yawTarget * 0.16,
      5.4,
      dt
    );
    [sp.torsoPitch, sp.torsoPitchVel] = criticallyDampedSpring(
      sp.torsoPitch,
      sp.torsoPitchVel,
      pitchTarget * 0.11,
      5.4,
      dt
    );

    [sp.camAz, sp.camAzVel] = criticallyDampedSpring(
      sp.camAz,
      sp.camAzVel,
      camAzTarget,
      7.2,
      dt
    );
    [sp.camEl, sp.camElVel] = criticallyDampedSpring(
      sp.camEl,
      sp.camElVel,
      camElTarget,
      7.2,
      dt
    );
    [sp.camDist, sp.camDistVel] = criticallyDampedSpring(
      sp.camDist,
      sp.camDistVel,
      camDistTarget,
      8.0,
      dt
    );

    // Update actual Three.js 3D PerspectiveCamera along spherical orbit around LOOK_TARGET
    const cosEl = Math.cos(sp.camEl);
    // Back the camera away on narrow displays instead of cropping the skull.
    const viewDistance = sp.camDist * Math.max(1, Math.min(1.8, 0.9 * size.height / size.width));
    const camX = LOOK_TARGET.x + viewDistance * Math.sin(sp.camAz) * cosEl;
    const camY = LOOK_TARGET.y + viewDistance * Math.sin(sp.camEl);
    const camZ = LOOK_TARGET.z + viewDistance * Math.cos(sp.camAz) * cosEl;
    camera.position.set(camX, camY, camZ);
    camera.lookAt(LOOK_TARGET);

    const tr = moodTransition.current;
    if (tr.progress < 1) {
      tr.progress = Math.min(1, tr.progress + dt / MOOD_BLOOM_SECONDS);
    }
    const shimmer = THREE.MathUtils.lerp(tr.prev.shimmer, tr.next.shimmer, tr.progress);

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

    brainEnvelope.current.activity = Math.max(
      0,
      brainEnvelope.current.activity - dt * (reducedMotion ? 1.6 : 0.78)
    );

    let assemblyProgress = 1;
    let assemblyEnabled = 0;
    if (reducedMotion && assemblyClock.current.completedRun !== assemblyRun) {
      assemblyClock.current.completedRun = assemblyRun;
      onAssemblyStateChange(false);
    }
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

    const chestBreath = reducedMotion ? 0 : Math.sin(t * 1.12) * 0.020;
    const pointSize = data.tier === "high" ? 2.52 : data.tier === "medium" ? 3.65 : 4.75;

    uniforms.uTime.value = t;
    uniforms.uDpr.value = dpr;
    uniforms.uPointSize.value = pointSize;
    uniforms.uCamPos.value.set(camX, camY, camZ);
    uniforms.uYaw.value = sp.yaw;
    uniforms.uPitch.value = sp.pitch;
    uniforms.uRoll.value = sp.roll;
    uniforms.uTorsoYaw.value = sp.torsoYaw;
    uniforms.uTorsoPitch.value = sp.torsoPitch;
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
  const { ready, integrationsReady, personaChosen, setupOpen, integrationsModalOpen, personaModalOpen } = useJarvis();
  const entryAllowed = ready && integrationsReady && personaChosen && !setupOpen && !integrationsModalOpen && !personaModalOpen;
  const audioLevelRef = useRef(0);
  const [qualityMode, setQualityMode] = useState<HumanoidQualityMode>("auto");
  const [autoFallback, setAutoFallback] = useState(false);
  const [particleData, setParticleData] = useState<HumanoidParticleData | null>(null);
  const [assemblyRun, setAssemblyRun] = useState(1);
  const [assembling, setAssembling] = useState(true);
  const [sfxEnabled, setSfxEnabled] = useState(true);
  const [turntable, setTurntable] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [entered, setEntered] = useState(false);
  const [entering, setEntering] = useState(false);
  const [demoState, setDemoState] = useState<OrbState | null>(null);
  const [manualPulse, setManualPulse] = useState(0);

  // Previewing an animation never changes the real assistant/microphone state.
  // A live state change always takes priority, and previews expire automatically.
  useEffect(() => { setDemoState(null); }, [state]);
  useEffect(() => {
    if (!demoState) return;
    const timer = window.setTimeout(() => setDemoState(null), 8000);
    return () => window.clearTimeout(timer);
  }, [demoState]);

  useEffect(() => {
    setMounted(true);
  }, []);

  const sfxEnabledRef = useRef(true);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const audioOutputRef = useRef<GainNode | null>(null);
  const entryButtonRef = useRef<HTMLButtonElement | null>(null);

  useEffect(() => {
    if (mounted && entryAllowed && !entered && particleData) entryButtonRef.current?.focus();
  }, [mounted, entryAllowed, entered, particleData]);

  useEffect(() => {
    if (!mounted || !entryAllowed || entered) return;
    const siblings = Array.from(document.body.children).filter(
      (el): el is HTMLElement => el instanceof HTMLElement && !el.classList.contains("humanoid-entry")
    );
    const previous = siblings.map((el) => el.inert);
    siblings.forEach((el) => { el.inert = true; });
    return () => siblings.forEach((el, i) => { el.inert = previous[i]; });
  }, [mounted, entryAllowed, entered]);
  const pointerRef = useRef<PointerState>({
    x: 0,
    y: 0,
    inside: false,
    dragging: false,
    dragAzimuth: 0,
    dragElevation: 0,
    zoomDist: CAM_Z,
  });

  useEffect(() => {
    sfxEnabledRef.current = sfxEnabled;
    const ctx = audioCtxRef.current;
    if (ctx && audioOutputRef.current) {
      audioOutputRef.current.gain.setTargetAtTime(sfxEnabled ? 1 : 0, ctx.currentTime, 0.025);
    }
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

  // Capture-phase window mouse/pointer/touch gaze + interactive click-drag 3D orbit & wheel zoom
  useEffect(() => {
    let dragLastX = 0;
    let dragLastY = 0;

    const isInteractiveElement = (target: EventTarget | null): boolean => {
      if (!(target instanceof HTMLElement)) return false;
      return Boolean(
        target.closest(
          "button, input, textarea, select, a, [role='button'], [role='dialog'], [contenteditable='true']"
        )
      );
    };

    const updateFromClientXY = (clientX: number, clientY: number) => {
      const w = Math.max(1, window.innerWidth);
      const h = Math.max(1, window.innerHeight);
      const nx = (clientX - EYE_SCREEN_X * w) / (0.5 * w);
      const dy = clientY - EYE_SCREEN_Y * h;
      const ny = dy / (dy < 0 ? 0.35 * h : 0.56 * h);
      pointerRef.current.x = THREE.MathUtils.clamp(nx, -1, 1);
      pointerRef.current.y = THREE.MathUtils.clamp(ny, -1, 1);
      pointerRef.current.inside = true;

      if (pointerRef.current.dragging) {
        const dxPx = clientX - dragLastX;
        const dyPx = clientY - dragLastY;
        dragLastX = clientX;
        dragLastY = clientY;
        pointerRef.current.dragAzimuth = THREE.MathUtils.clamp(
          pointerRef.current.dragAzimuth - (dxPx / w) * 1.6,
          -0.48,
          0.48
        );
        pointerRef.current.dragElevation = THREE.MathUtils.clamp(
          pointerRef.current.dragElevation + (dyPx / h) * 1.1,
          -0.32,
          0.32
        );
      }
    };

    const onPointerDown = (e: PointerEvent) => {
      if (e.button !== 0 || isInteractiveElement(e.target)) return;
      pointerRef.current.dragging = true;
      dragLastX = e.clientX;
      dragLastY = e.clientY;
    };

    const onPointerUp = () => {
      pointerRef.current.dragging = false;
    };

    const onDoubleClick = (e: MouseEvent) => {
      if (isInteractiveElement(e.target)) return;
      pointerRef.current.dragAzimuth = 0;
      pointerRef.current.dragElevation = 0;
      pointerRef.current.zoomDist = CAM_Z;
    };

    const onWheel = (e: WheelEvent) => {
      if (isInteractiveElement(e.target)) return;
      pointerRef.current.zoomDist = THREE.MathUtils.clamp(
        pointerRef.current.zoomDist + e.deltaY * 0.0022,
        5.15,
        8.65
      );
    };

    const onKeyReset = (e: KeyboardEvent) => {
      if (!isInteractiveElement(e.target) && (e.key === "0" || e.key === "Home")) {
        pointerRef.current.dragAzimuth = 0;
        pointerRef.current.dragElevation = 0;
        pointerRef.current.zoomDist = CAM_Z;
      }
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
        pointerRef.current.dragging = false;
      }
    };

    const onWindowBlur = () => {
      pointerRef.current.inside = false;
      pointerRef.current.dragging = false;
    };

    window.addEventListener("pointerdown", onPointerDown, {
      passive: true,
      capture: true,
    });
    window.addEventListener("pointerup", onPointerUp, {
      passive: true,
      capture: true,
    });
    window.addEventListener("pointercancel", onPointerUp, {
      passive: true,
      capture: true,
    });
    window.addEventListener("dblclick", onDoubleClick, {
      passive: true,
      capture: true,
    });
    window.addEventListener("wheel", onWheel, { passive: true });
    window.addEventListener("keydown", onKeyReset);
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
      window.removeEventListener("pointerdown", onPointerDown, true);
      window.removeEventListener("pointerup", onPointerUp, true);
      window.removeEventListener("pointercancel", onPointerUp, true);
      window.removeEventListener("dblclick", onDoubleClick, true);
      window.removeEventListener("wheel", onWheel);
      window.removeEventListener("keydown", onKeyReset);
      window.removeEventListener("pointermove", onPointerOrMouseMove, true);
      window.removeEventListener("mousemove", onPointerOrMouseMove, true);
      window.removeEventListener("mouseover", onPointerOrMouseMove, true);
      window.removeEventListener("touchmove", onTouchMove, true);
      window.removeEventListener("touchstart", onTouchMove, true);
      document.removeEventListener("mouseout", onLeaveViewport);
      window.removeEventListener("blur", onWindowBlur);
    };
  }, []);

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
      const output = ctx.createGain();
      output.gain.value = sfxEnabledRef.current ? 1 : 0;
      output.connect(ctx.destination);
      audioOutputRef.current = output;
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
    master.connect(compressor).connect(audioOutputRef.current ?? ctx.destination);

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
    shimmer.onended = () => {
      sub.disconnect(); subGain.disconnect(); shimmer.disconnect(); shimmerGain.disconnect();
      noise.disconnect(); filter.disconnect(); noiseGain.disconnect();
    };
    // The gain envelope has a longer tail than the sources; it is silent after they stop.
    noise.onended = () => { master.disconnect(); compressor.disconnect(); };
  }, []);

  // ENTER is the only initial audio unlock. Do not start a silent birth on mount.
  const playAssemblySound = useCallback((ctx: AudioContext) => {
    if (!sfxEnabledRef.current || ctx.state !== "running") return;
    const now = ctx.currentTime;
    const duration = ASSEMBLY_DURATION_SECONDS;
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.0001, now);
    gain.gain.exponentialRampToValueAtTime(0.055, now + 0.5);
    gain.gain.exponentialRampToValueAtTime(0.10, now + duration - 0.3);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
    gain.connect(audioOutputRef.current ?? ctx.destination);
    const voices = [98, 147, 196].map((frequency) => {
      const osc = ctx.createOscillator();
      osc.type = "sine";
      osc.frequency.setValueAtTime(frequency * 0.5, now);
      osc.frequency.exponentialRampToValueAtTime(frequency * 2, now + duration);
      osc.connect(gain);
      osc.start(now);
      osc.stop(now + duration);
      return osc;
    });
    voices[voices.length - 1].onended = () => {
      voices.forEach((osc) => osc.disconnect());
      gain.disconnect();
    };
  }, []);

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
    pointerRef.current.dragAzimuth = 0;
    pointerRef.current.dragElevation = 0;
    pointerRef.current.zoomDist = CAM_Z;
    const ctx = await ensureAudioContext();
    if (ctx) playAssemblySound(ctx);
    setAssembling(!reducedMotion);
    setAssemblyRun((r) => r + 1);
  }, [ensureAudioContext, playAssemblySound, reducedMotion]);

  const enterStage = useCallback(async () => {
    if (entering || entered || !particleData) return;
    setEntering(true);
    try {
      // Audio creation/resume occurs inside this user gesture, before the Canvas mounts.
      const ctx = await ensureAudioContext();
      if (ctx) playAssemblySound(ctx);
    } catch {
      // Audio unavailable/denied must never prevent the visual experience.
    } finally {
      setAssembling(!reducedMotion);
      setEntered(true);
      setEntering(false);
    }
  }, [entering, entered, particleData, ensureAudioContext, playAssemblySound, reducedMotion]);

  const cycleQuality = useCallback(() => {
    setQualityMode((prev) =>
      prev === "auto" ? "high" : prev === "high" ? "balanced" : "auto"
    );
  }, []);

  const formattedPts = particleData
    ? `${Math.round(particleData.count / 1000)}K 3D`
    : "LOADING";

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

      {entered && particleData && (
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
              state={demoState ?? state}
              reducedMotion={reducedMotion}
              turntable={turntable}
              audioLevelRef={audioLevelRef}
              pointerRef={pointerRef}
              assemblyRun={assemblyRun}
              pulseSeq={pulseSignal + manualPulse}
              brainEvent={brainEvent}
              onAssemblyStateChange={setAssembling}
              onShockwaveTrigger={playBirthShockwaveSound}
              onLowFpsDetected={() => setAutoFallback(true)}
            />
          </Canvas>
        </div>
      )}

      {mounted && (entered || entryAllowed) && createPortal(
        !entered ? (
          <div className="humanoid-entry" role="dialog" aria-modal="true" aria-labelledby="humanoid-title">
            <div className="humanoid-entry-content">
              <h1 id="humanoid-title">APEX HUMANOID</h1>
              <p>a figure of light that assembles itself</p>
              <button ref={entryButtonRef} type="button" autoFocus onKeyDown={(e) => {
                if (e.key === "Tab") e.preventDefault();
              }} disabled={!particleData || entering} onClick={() => void enterStage()}>
                {entering ? "ENTERING" : particleData ? "ENTER" : "PREPARING LIGHT"}
              </button>
              <small>the click opens the audio - the birth has a sound</small>
            </div>
          </div>
        ) : (
          <div className="humanoid-controls" aria-label="Humanoid visual controls">
            <div className="humanoid-state-row" role="group" aria-label="Preview visual states">
              <span className="humanoid-state-label">{demoState ? "VISUAL PREVIEW" : "LIVE"}</span>
              {(["idle", "listening", "thinking", "speaking"] as OrbState[]).map((mode) => (
                <button key={mode} type="button" aria-pressed={(demoState ?? state) === mode}
                  onClick={() => setDemoState(mode)}>{mode.toUpperCase()}</button>
              ))}
              {demoState && <button type="button" onClick={() => setDemoState(null)}>↩ LIVE</button>}
            </div>
            <div className="humanoid-utility-row" role="group" aria-label="Figure of light settings">
              <span className="humanoid-count" role="status">{assembling ? "ASSEMBLING" : formattedPts}</span>
              <button type="button" disabled={assembling} onClick={() => void triggerRebirth()}>REBIRTH</button>
              <button type="button" disabled={assembling} onClick={() => setManualPulse((n) => n + 1)}>SHOCKWAVE</button>
              <button type="button" aria-pressed={turntable} onClick={() => setTurntable((v) => !v)}>3D ORBIT</button>
              <button type="button" onClick={cycleQuality} title="Cycle automatic, high and balanced particle density">
                {qualityMode === "auto" ? "AUTO" : qualityMode === "high" ? "HIGH" : "BAL"}
              </button>
              <button type="button" aria-pressed={sfxEnabled} onClick={async () => {
                const next = !sfxEnabled;
                setSfxEnabled(next);
                if (next) { try { await ensureAudioContext(); } catch {} }
              }}>{sfxEnabled ? "SFX ON" : "SFX OFF"}</button>
              {onToggleConstellation && <button type="button" aria-pressed={constellationVisible}
                onClick={onToggleConstellation}>{constellationVisible ? "WEB ON" : "PURE"}</button>}
            </div>
            <p className="humanoid-hint">move to look · drag to orbit · scroll to zoom · double-click to reset</p>
          </div>
        ), document.body)}
    </div>
  );
}
