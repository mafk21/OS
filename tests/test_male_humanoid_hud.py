from __future__ import annotations

import math
from pathlib import Path
import re
import subprocess

from fastapi.testclient import TestClient
import numpy as np
from PIL import Image

from core.apex_bridge import ApexHudBridge

REPO_ROOT = Path(__file__).resolve().parents[1]
PORTRAIT_PUB = REPO_ROOT / "apex_ui" / "public" / "hologram" / "male_portrait.png"
DEPTH_PUB = REPO_ROOT / "apex_ui" / "public" / "hologram" / "male_depth.png"
PORTRAIT_STATIC = REPO_ROOT / "apex_ui" / "static_hud" / "hologram" / "male_portrait.png"
DEPTH_STATIC = REPO_ROOT / "apex_ui" / "static_hud" / "hologram" / "male_depth.png"


def test_male_humanoid_assets_and_300k_particle_calibration() -> None:
    assert PORTRAIT_PUB.exists(), "male_portrait.png missing in apex_ui/public/hologram"
    assert DEPTH_PUB.exists(), "male_depth.png missing in apex_ui/public/hologram"
    assert PORTRAIT_STATIC.exists(), "male_portrait.png missing in exported static_hud/hologram"
    assert DEPTH_STATIC.exists(), "male_depth.png missing in exported static_hud/hologram"

    portrait = Image.open(PORTRAIT_PUB).convert("RGB")
    depth = Image.open(DEPTH_PUB).convert("RGBA")
    assert portrait.size == depth.size == (1020, 634)

    rgb = np.asarray(portrait, dtype=np.float32) / 255.0
    dep = np.asarray(depth, dtype=np.uint8)

    # Channel A must stay 255 everywhere so browser Canvas 2D getImageData never premultiplies RGB
    assert int(dep[..., 3].min()) == 255

    # Active particle count in HIGH tier (~300,000 dots)
    bright = rgb.max(axis=2)
    region = dep[..., 2].astype(np.float32) / 255.0
    min_b = np.where(region > 0.85, 0.095, 0.044)
    active_dots = int((bright >= min_b).sum())
    assert 275_000 <= active_dots <= 325_000, f"Expected ~300k dots, got {active_dots}"

    # Verify both electric-cyan rim particles and warm golden-amber core particles exist richly
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cyan_dots = int(((b > r * 1.15) & (np.maximum(g, b) > 0.28)).sum())
    warm_dots = int(((r > b * 1.25) & (r > 0.35)).sum())
    assert cyan_dots > 30_000
    assert warm_dots > 12_000

    # Verify outer living wave backdrop never inherits head-turn skinning weight
    h, w = bright.shape
    yy, xx = np.mgrid[0:h, 0:w]
    nx = xx / (w - 1.0)
    ny = yy / (h - 1.0)
    wave_zone = (ny >= 0.30) & (ny <= 0.65) & (np.abs(nx - 0.5) >= 0.28) & (bright > 0.10)
    assert int(dep[..., 1][wave_zone].max()) == 0

    # Verify C2 quintic skinning field has zero sharp pixel cliff anywhere (< 0.02/px)
    lat_u = np.clip(1.0 - (np.abs(nx - 0.5) - 0.145) / (0.275 - 0.145), 0.0, 1.0)
    lat_w = lat_u * lat_u * lat_u * (lat_u * (lat_u * 6.0 - 15.0) + 10.0)
    cerv_u = np.clip(1.0 - (ny - 0.565) / (0.775 - 0.565), 0.0, 1.0)
    cerv_w = cerv_u * cerv_u * cerv_u * (cerv_u * (cerv_u * 6.0 - 15.0) + 10.0)
    c2_skin = lat_w * cerv_w
    gy, gx = np.gradient(c2_skin)
    assert float(np.hypot(gx, gy).max()) < 0.02

    # Verify outer border vignette cleanly fades to pure black (#000000) so no hard rectangle edge appears
    assert float(bright[0, :].max()) < 0.01
    assert float(bright[-1, :].max()) < 0.02
    assert float(bright[:, 0].max()) < 0.01
    assert float(bright[:, -1].max()) < 0.01


def test_male_humanoid_mouse_gaze_directions_and_smooth_physics() -> None:
    src = (REPO_ROOT / "apex_ui" / "components" / "ApexMaleHumanoid.tsx").read_text(encoding="utf-8")

    # 1. Single-pass GPU draw call + SRGB LUT + critically-damped 2nd-order spring physics
    assert src.count("<points ") == 1, "Must fuse core + halo into a single GPU <points> draw call"
    assert "criticallyDampedSpring" in src
    assert "SRGB_TO_LINEAR" in src
    assert "THREE.CustomBlending" in src
    assert "lastMoveAt" not in src, "Cursor gaze must never time out while pointer remains in window"

    # 2. Capture-phase window mouse/pointer/touch tracking so overlay stopPropagation never blocks gaze
    assert 'window.addEventListener("pointermove", onPointerOrMouseMove' in src
    assert 'window.addEventListener("mousemove", onPointerOrMouseMove' in src
    assert 'window.addEventListener("touchmove", onTouchMove' in src
    assert "capture: true" in src

    # 3. Extract constants directly from ApexMaleHumanoid.tsx and verify all 4 cardinal + 4 diagonal directions
    def extract_const(name: str) -> float:
        m = re.search(rf"const\s+{name}\s*=\s*([-+]?[0-9]*\.?[0-9]+)", src)
        assert m, f"Missing constant {name}"
        return float(m.group(1))

    eye_x = extract_const("EYE_SCREEN_X")
    eye_y = extract_const("EYE_SCREEN_Y")
    max_yaw = extract_const("MAX_HEAD_YAW")
    max_pitch_up = extract_const("MAX_HEAD_PITCH_UP")
    max_pitch_down = extract_const("MAX_HEAD_PITCH_DOWN")
    y_pivot = extract_const("Y_PIVOT")
    z_pivot = extract_const("Z_PIVOT")
    cam_y = extract_const("CAM_Y")
    cam_z = extract_const("CAM_Z")

    # Ensure pitch uses POSITIVE gy (never inverted `-ptr.y`)
    assert "-ptr.y" not in src
    assert "gy >= 0 ? gy * MAX_HEAD_PITCH_DOWN : gy * MAX_HEAD_PITCH_UP" in src
    # Ensure vertex shader pitch matches r2 = vec3(r1.x, r1.y * cp - r1.z * sp, r1.y * sp + r1.z * cp)
    assert "vec3 r2 = vec3(r1.x, r1.y * cp - r1.z * sp, r1.y * sp + r1.z * cp);" in src

    vw, vh = 1280.0, 800.0
    # Anatomical nose tip in world space (in front of cervical pivot: z > z_pivot, y > y_pivot)
    nose_world = (0.0, 0.54, 0.66)

    def project_nose_screen_xy(client_x: float, client_y: float) -> tuple[float, float, float]:
        nx = max(-1.0, min(1.0, (client_x - eye_x * vw) / (0.5 * vw)))
        dy = client_y - eye_y * vh
        ny = max(-1.0, min(1.0, dy / (0.35 * vh if dy < 0 else 0.56 * vh)))
        gx = math.copysign(abs(nx) ** 0.86, nx) if nx != 0 else 0.0
        gy = math.copysign(abs(ny) ** 0.86, ny) if ny != 0 else 0.0

        yaw = gx * max_yaw
        pitch = gy * max_pitch_down if gy >= 0 else gy * max_pitch_up
        roll = -yaw * 0.085

        rx = nose_world[0]
        ry = nose_world[1] - y_pivot
        rz = nose_world[2] - z_pivot

        cy, sy = math.cos(yaw), math.sin(yaw)
        cp, sp = math.cos(pitch), math.sin(pitch)
        cr, sr = math.cos(roll), math.sin(roll)

        r1x = rx * cy + rz * sy
        r1z = -rx * sy + rz * cy
        r2y = ry * cp - r1z * sp
        r2z = ry * sp + r1z * cp
        r3x = r1x * cr - r2y * sr
        r3y = r1x * sr + r2y * cr

        wx = r3x
        wy = r3y + y_pivot
        wz = r2z + z_pivot

        f = 1.0 / math.tan(math.radians(19.0))
        aspect = vw / vh
        sx = (((wx * (f / aspect)) / (cam_z - wz)) * 0.5 + 0.5) * vw
        sy_scr = (0.5 - (((wy - cam_y) * f) / (cam_z - wz)) * 0.5) * vh
        return sx, sy_scr, wz

    cx0, cy0, _ = project_nose_screen_xy(eye_x * vw, eye_y * vh)

    # Cardinal checks (screen Y grows downward, screen X grows rightward):
    # 1) Mouse DOWN -> nose screen Y MUST increase (nod DOWN), never go up!
    _, down_y, _ = project_nose_screen_xy(eye_x * vw, vh * 0.90)
    assert down_y > cy0 + 18.0, f"Mouse DOWN must move head DOWN (+screenY), got {down_y} vs {cy0}"

    # 2) Mouse UP -> nose screen Y MUST decrease (tilt UP)!
    _, up_y, _ = project_nose_screen_xy(eye_x * vw, vh * 0.05)
    assert up_y < cy0 - 14.0, f"Mouse UP must move head UP (-screenY), got {up_y} vs {cy0}"

    # 3) Mouse RIGHT -> nose screen X MUST increase (turn RIGHT)!
    right_x, _, _ = project_nose_screen_xy(vw * 0.92, eye_y * vh)
    assert right_x > cx0 + 25.0, f"Mouse RIGHT must move head RIGHT (+screenX), got {right_x} vs {cx0}"

    # 4) Mouse LEFT -> nose screen X MUST decrease (turn LEFT)!
    left_x, _, _ = project_nose_screen_xy(vw * 0.08, eye_y * vh)
    assert left_x < cx0 - 25.0, f"Mouse LEFT must move head LEFT (-screenX), got {left_x} vs {cx0}"

    # 5) All 4 diagonals simultaneously follow both X and Y!
    ul_x, ul_y, _ = project_nose_screen_xy(vw * 0.10, vh * 0.08)
    ur_x, ur_y, _ = project_nose_screen_xy(vw * 0.90, vh * 0.08)
    dl_x, dl_y, _ = project_nose_screen_xy(vw * 0.10, vh * 0.88)
    dr_x, dr_y, _ = project_nose_screen_xy(vw * 0.90, vh * 0.88)
    assert ul_x < cx0 and ul_y < cy0
    assert ur_x > cx0 and ur_y < cy0
    assert dl_x < cx0 and dl_y > cy0
    assert dr_x > cx0 and dr_y > cy0


def test_female_orb_components_strictly_untouched() -> None:
    female_files = [
        "apex_ui/components/ApexHeroOrb.tsx",
        "apex_ui/components/ApexCore3D.jsx",
    ]
    res = subprocess.run(
        ["git", "diff", "--name-only", "HEAD", "--", *female_files],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=True,
    )
    assert res.stdout.strip() == "", f"Female orb components must remain untouched: {res.stdout}"

    world_src = (REPO_ROOT / "apex_ui" / "components" / "ApexWorld.tsx").read_text(encoding="utf-8")
    assert "ApexMaleHumanoid" in world_src
    assert "ApexHeroOrb" in world_src
    assert 'activePersona === "male"' in world_src


def test_male_humanoid_shader_and_bridge_serving(tmp_path: Path, monkeypatch) -> None:
    import memory.config_manager as cfg_mgr

    monkeypatch.setattr(cfg_mgr, "CONFIG_DIR", tmp_path)
    monkeypatch.setattr(cfg_mgr, "CONFIG_FILE", tmp_path / "api_keys.json")

    humanoid_src = (REPO_ROOT / "apex_ui" / "components" / "ApexMaleHumanoid.tsx").read_text(
        encoding="utf-8"
    )
    for required in (
        "/hologram/male_portrait.png",
        "/hologram/male_depth.png",
        "uAssemblyProgress",
        "uShockwaveActive",
        "uTransitionProgress",
        "uVoice",
        "REBIRTH",
        "useJarvisAudioLevel",
    ):
        assert required in humanoid_src, f"Missing {required} in ApexMaleHumanoid.tsx"

    bridge = ApexHudBridge(ui_ref=None)
    app = bridge._build_app()
    with TestClient(app) as client:
        r_index = client.get("/")
        assert r_index.status_code == 200
        assert "text/html" in r_index.headers.get("content-type", "")

        r_portrait = client.get("/hologram/male_portrait.png")
        assert r_portrait.status_code == 200
        assert r_portrait.headers.get("content-type", "").startswith("image/png")
        assert len(r_portrait.content) > 50_000

        r_depth = client.get("/hologram/male_depth.png")
        assert r_depth.status_code == 200
        assert r_depth.headers.get("content-type", "").startswith("image/png")
        assert len(r_depth.content) > 10_000

        r_boot = client.get("/api/hud/bootstrap")
        assert r_boot.status_code == 200
        boot = r_boot.json()
        assert boot["persona"] in ("male", "female")

        # Verify switching between Male (Figure of Light) and Female (Untouched Orb) works end-to-end
        r_female = client.post(
            "/api/hud/action",
            json={"action": "set_persona", "persona": "female"},
        )
        assert r_female.status_code == 200
        assert client.get("/api/hud/bootstrap").json()["persona"] == "female"

        r_male = client.post(
            "/api/hud/action",
            json={"action": "set_persona", "persona": "male"},
        )
        assert r_male.status_code == 200
        assert client.get("/api/hud/bootstrap").json()["persona"] == "male"
