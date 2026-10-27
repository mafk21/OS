"""Guards against mounting a disconnected reference demo as the actual desktop HUD."""
import hashlib
import json
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]/'apex_ui'

class ReferenceInterfaceTests(unittest.TestCase):
    def test_upstream_renderers_are_retained_as_reference_material(self):
        reference=ROOT/'components/reference'
        manifest=json.loads((reference/'upstream.json').read_text())
        for name,digest in manifest['sha256'].items():
            if name=='ApexWorld.tsx':continue
            with self.subTest(component=name):
                self.assertEqual(hashlib.sha256((reference/name).read_bytes()).hexdigest(),digest)

    def test_desktop_route_uses_actual_persona_hud_not_blue_demo(self):
        page=(ROOT/'app/page.tsx').read_text()
        for token in ('@/components/ApexWorld','@/components/ApexOverviewPanel','<JarvisProvider>','<JarvisHudOverlays />','<DualMonitorConsole />','backgroundMode'):
            self.assertIn(token,page)
        self.assertNotIn('ApexReferenceWorld',page)
        self.assertNotIn('/reference/',page)
        self.assertFalse((ROOT/'components/ApexReferenceWorld.tsx').exists())

    def test_persona_selects_matching_avatar_on_shared_dark_stage(self):
        world=(ROOT/'components/ApexWorld.tsx').read_text()
        self.assertIn('const isMale = activePersona === "male";',world)
        self.assertIn('const HumanoidFigure = isMale ? ApexMaleHumanoid : ApexFemaleHumanoid;',world)
        for token in ('<HumanoidFigure','state={orbState}','trace={trace}','reducedMotion={reduced}','pulseSignal={humanoidPulse}','onToggleConstellation='):
            self.assertIn(token,world)
        self.assertIn('background: isMale ? "#02050a" : "#08030a"',world)
        self.assertNotIn('<ApexHeroOrb',world)

    def test_static_export_assets_resolve_and_has_no_demo_switch(self):
        static=ROOT/'static_hud';html=(static/'index.html').read_text()
        self.assertNotIn('HUMAN · FEMALE',html)
        self.assertNotIn('View on GitHub',html)
        assets=re.findall(r'(?:src|href)="(/_next/[^"?]+)',html)
        self.assertTrue(assets)
        for asset in assets:
            with self.subTest(asset=asset):self.assertTrue((static/asset.lstrip('/')).is_file())
