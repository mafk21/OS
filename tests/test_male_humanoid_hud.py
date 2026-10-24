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


def test_male_humanoid_3d_sculpt_assets_and_volumetric_depth() -> None:
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

    # Verify true full-volume 3D depth relief (Z in [-2.40 .. +1.60]) — never flat 2D bas-relief!
    h, w, _ = rgb.shape
    wz = (dep[..., 0].astype(np.float32) / 255.0) * 4.00 - 2.40
    nose_z = float(wz[int(0.45 * h), int(0.50 * w)])
    socket_z = float(wz[int(0.376 * h), int(0.452 * w)])
    temple_z = float(wz[int(0.38 * h), int(0.354 * w)])
    chin_z = float(wz[int(0.618 * h), int(0.50 * w)])
    submental_z = float(wz[int(0.680 * h), int(0.50 * w)])

    assert nose_z > 1.40, f"Nose must project strongly in 3D (+Z > 1.40), got {nose_z}"
    assert nose_z - socket_z > 0.50, f"Orbital eye sockets must recess deeply behind nose/brow, got {nose_z - socket_z}"
    assert nose_z - temple_z > 1.35, f"Head front-to-rim 3D depth must exceed 1.35 units, got {nose_z - temple_z}"
    assert chin_z - submental_z > 0.55, f"Chin must overhang cylindrical neck in 3D, got {chin_z - submental_z}"

    # Verify deep-space wave backdrop sits > 2.8 world units behind nose tip & carries 0 head skinning
    yy, xx = np.mgrid[0:h, 0:w]
    nx = xx / (w - 1.0)
    ny = yy / (h - 1.0)
    bright = rgb.max(axis=2)
    wave_zone = (ny >= 0.30) & (ny <= 0.65) & (np.abs(nx - 0.5) >= 0.24) & (bright > 0.10)
    assert int(dep[..., 1][wave_zone].max()) == 0
    wave_mean_z = float(wz[wave_zone].mean())
    assert nose_z - wave_mean_z > 2.80, f"Expected >2.8 units 3D separation between face and waves, got {nose_z - wave_mean_z}"

    # Verify both electric-cyan rim particles and warm golden-amber core particles exist richly
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    cyan_dots = int(((b > r * 1.15) & (np.maximum(g, b) > 0.28)).sum())
    warm_dots = int(((r > b * 1.25) & (r > 0.35)).sum())
    assert cyan_dots > 30_000
    assert warm_dots > 12_000

    # Verify outer border vignette cleanly fades to pure black (#000000)
    assert float(bright[0, :].max()) < 0.01
    assert float(bright[-1, :].max()) < 0.02
    assert float(bright[:, 0].max()) < 0.01
    assert float(bright[:, -1].max()) < 0.01


def test_male_humanoid_3d_camera_parallax_and_mouse_gaze_directions() -> None:
    src = (REPO_ROOT / "apex_ui" / "components" / "ApexMaleHumanoid.tsx").read_text(encoding="utf-8")

    # 1. Single-pass GPU draw call + back-to-front 3D bucket sort + perspective sizeAttenuation + 3D backface occlusion
    assert src.count("<points ") == 1
    assert "sortParticlesBackToFront" in src
    assert "criticallyDampedSpring" in src
    assert "SRGB_TO_LINEAR" in src
    assert "perspAtten" in src, "Must attenuate gl_PointSize by 1 / -mvPosition.z for real 3D perspective"
    assert "backfaceVis" in src, "Must attenuate back-turned shell normals so far side of skull does not ghost over face"
    assert "fresnelRim" in src, "Must compute 3D grazing-angle Fresnel rim lighting"
    assert "camera.position.set(camX, camY, camZ)" in src, "Must orbit actual 3D PerspectiveCamera in world space"
    assert "camera.lookAt(LOOK_TARGET)" in src
    assert "3D ORBIT" in src
    assert "lastMoveAt" not in src

    # 2. Capture-phase window mouse/pointer/touch tracking
    assert 'window.addEventListener("pointermove", onPointerOrMouseMove' in src
    assert 'window.addEventListener("mousemove", onPointerOrMouseMove' in src
    assert 'window.addEventListener("touchmove", onTouchMove' in src
    assert "capture: true" in src

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
    cam_z = extract_const("CAM_Z")

    vw, vh = 1280.0, 800.0
    nose_world = (0.0, 0.54, 1.56)
    wave_world = (0.0, 0.04, -1.45)

    def project_nose_and_wave(client_x: float, client_y: float) -> tuple[float, float, float, float]:
        nx = max(-1.0, min(1.0, (client_x - eye_x * vw) / (0.5 * vw)))
        dy = client_y - eye_y * vh
        ny = max(-1.0, min(1.0, dy / (0.35 * vh if dy < 0 else 0.56 * vh)))
        gx = math.copysign(abs(nx) ** 0.86, nx) if nx != 0 else 0.0
        gy = math.copysign(abs(ny) ** 0.86, ny) if ny != 0 else 0.0

        yaw = gx * max_yaw
        pitch = gy * max_pitch_down if gy >= 0 else gy * max_pitch_up
        roll = -yaw * 0.085

        cam_az = -gx * 0.18
        cam_el = gy * 0.09

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

        n_pt = np.array([r3x, r3y + y_pivot, r2z + z_pivot], dtype=np.float64)
        w_pt = np.array(wave_world, dtype=np.float64)

        tgt = np.array([0.0, 0.04, 0.08], dtype=np.float64)
        cam = tgt + np.array(
            [
                cam_z * math.sin(cam_az) * math.cos(cam_el),
                cam_z * math.sin(cam_el),
                cam_z * math.cos(cam_az) * math.cos(cam_el),
            ],
            dtype=np.float64,
        )
        fwd = tgt - cam
        fwd /= np.linalg.norm(fwd)
        right = np.cross(fwd, np.array([0.0, 1.0, 0.0]))
        right /= np.linalg.norm(right)
        up = np.cross(right, fwd)
        f = 1.0 / math.tan(math.radians(19.0))
        aspect = vw / vh

        def proj(pt: np.ndarray) -> tuple[float, float]:
            d = pt - cam
            vx = float(np.dot(d, right))
            vy = float(np.dot(d, up))
            vz = float(np.dot(d, fwd))
            return (0.5 + 0.5 * (vx * f / aspect) / vz) * vw, (0.5 - 0.5 * (vy * f) / vz) * vh

        nsx, nsy = proj(n_pt)
        wsx, wsy = proj(w_pt)
        return nsx, nsy, wsx, wsy

    cx0, cy0, wx0, wy0 = project_nose_and_wave(eye_x * vw, eye_y * vh)

    # 1) Mouse DOWN -> nose screen Y increases strongly AND deep wave shifts upward (opposing 3D parallax!)
    _, down_ny, _, down_wy = project_nose_and_wave(eye_x * vw, vh * 0.92)
    assert down_ny > cy0 + 80.0
    assert down_wy < wy0 - 10.0

    # 2) Mouse UP -> nose screen Y decreases strongly AND deep wave shifts downward!
    _, up_ny, _, up_wy = project_nose_and_wave(eye_x * vw, vh * 0.05)
    assert up_ny < cy0 - 80.0
    assert up_wy > wy0 + 10.0

    # 3) Mouse RIGHT -> nose turns RIGHT (+screenX) while deep wave glides LEFT (-screenX) (>150px 3D parallax!)
    right_nx, _, right_wx, _ = project_nose_and_wave(vw * 0.94, eye_y * vh)
    assert right_nx > cx0 + 120.0
    assert right_wx < wx0 - 20.0
    assert (right_nx - right_wx) > 150.0

    # 4) Mouse LEFT -> nose turns LEFT (-screenX) while deep wave glides RIGHT (+screenX) (>150px 3D parallax!)
    left_nx, _, left_wx, _ = project_nose_and_wave(vw * 0.06, eye_y * vh)
    assert left_nx < cx0 - 120.0
    assert left_wx > wx0 + 20.0
    assert (left_wx - left_nx) > 150.0


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
