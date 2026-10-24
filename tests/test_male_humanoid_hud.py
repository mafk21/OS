from __future__ import annotations

from pathlib import Path
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
    wave_zone = (ny >= 0.30) & (ny <= 0.65) & (np.abs(nx - 0.5) >= 0.24) & (bright > 0.10)
    assert int(dep[..., 1][wave_zone].max()) == 0

    # Verify outer border vignette cleanly fades to pure black (#000000) so no hard rectangle edge appears
    assert float(bright[0, :].max()) < 0.01
    assert float(bright[-1, :].max()) < 0.02
    assert float(bright[:, 0].max()) < 0.01
    assert float(bright[:, -1].max()) < 0.01


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
