"""Frontend-source fidelity and production asset checks; no hardware required."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / "apex_ui"


class ReferenceInterfaceTests(unittest.TestCase):
    def test_renderers_are_byte_identical_to_pinned_upstream(self):
        reference = ROOT / "components/reference"
        manifest = json.loads((reference / "upstream.json").read_text())
        self.assertEqual(manifest["commit"], "a8732fad1078a809cadfa810cb0d89cf4445dbed")
        for name, digest in manifest["sha256"].items():
            if name == "ApexWorld.tsx":
                continue  # Transport-only callbacks are intentionally adapted.
            with self.subTest(component=name):
                self.assertEqual(hashlib.sha256((reference / name).read_bytes()).hexdigest(), digest)

    def test_default_route_uses_reference_without_custom_avatar_or_console(self):
        page = (ROOT / "app/page.tsx").read_text()
        self.assertIn('@/components/reference/ApexOverviewPanel', page)
        self.assertIn('<ApexReferenceWorld />', page)
        self.assertIn('<JarvisProvider>', page)
        self.assertIn('<JarvisHudOverlays referenceLayout />', page)
        self.assertNotIn('ApexMaleHumanoid', page)
        self.assertNotIn('DualMonitorConsole', page)

    def test_live_transport_and_on_demand_controls_remain_wired(self):
        adapter = (ROOT / "components/ApexReferenceWorld.tsx").read_text()
        self.assertIn('liveTrace={connected ? trace : undefined}', adapter)
        self.assertIn('onTap={tapOrb}', adapter)
        self.assertIn('orbState === "listening" ? "idle" : orbState', adapter)
        self.assertIn('window.removeEventListener("keydown", onKey)', adapter)
        overlays = (ROOT / "components/JarvisHudOverlays.tsx").read_text()
        self.assertIn('(!referenceLayout || consoleOpen || settingsOpen)', overlays)
        self.assertIn('(!referenceLayout || consoleOpen)', overlays)
        for element in ('{confirm && (', '<HudVideoModal />', '<HudSocialModal />', '{setupOpen && ('):
            self.assertIn(element, overlays)

    def test_production_html_and_local_assets_are_present(self):
        static = ROOT / "static_hud"
        html = (static / "index.html").read_text()
        self.assertIn('Apex core - tap to energize', html)
        self.assertIn('View on GitHub', html)
        self.assertNotIn('apex-male-humanoid', html)
        assets = re.findall(r'(?:src|href)="(/_next/[^"?]+)', html)
        self.assertTrue(assets)
        for asset in assets:
            with self.subTest(asset=asset):
                self.assertTrue((static / asset.lstrip('/')).is_file())


if __name__ == '__main__':
    unittest.main()
