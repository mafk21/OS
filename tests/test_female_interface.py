"""The female edition must use the existing male animation engine, not a substitute."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'apex_ui'

class FemaleInterfaceTests(unittest.TestCase):
    def test_same_animation_component_not_separate_sculpture(self):
        s=(ROOT/'components/ApexFemaleHumanoid.tsx').read_text()
        self.assertIn('import ApexMaleHumanoid',s)
        self.assertIn('appearance="female"',s)
        self.assertIn('trace={trace} reducedMotion={reducedMotion}',s)
        for rejected in ('SphereGeometry','sculpture()', 'ShaderMaterial','Canvas'):
            self.assertNotIn(rejected,s)

    def test_appearance_caches_are_isolated(self):
        s=(ROOT/'components/ApexMaleHumanoid.tsx').read_text()
        for token in ('cachedAssetsPromises.get(appearance)', 'cachedAssetsPromises.delete(appearance)', '`${appearance}:${tier}`', 'cachedParticleTiers.get(cacheKey)'):
            self.assertIn(token,s)
        self.assertIn('appearance = "male"',s)
        self.assertIn('loadDecodedAssets(appearance)',s)

    def test_assets_and_palette_are_female_specific(self):
        s=(ROOT/'components/ApexMaleHumanoid.tsx').read_text()
        self.assertIn('/hologram/female_portrait.png',s)
        self.assertIn('/hologram/female_depth.png',s)
        self.assertIn('uniform float uFemale;',s)
        for name in ('female_portrait.png','female_depth.png'):
            public=ROOT/'public/hologram'/name
            self.assertTrue(public.exists())
            self.assertEqual(public.read_bytes(),(ROOT/'static_hud/hologram'/name).read_bytes())

    def test_visual_switch_preserves_voice_and_trace_wiring(self):
        s=(ROOT/'components/ApexReferenceWorld.tsx').read_text()
        self.assertIn('localStorage.setItem("apex.figure"',s)
        self.assertNotIn('choosePersona(',s)
        self.assertNotIn('setVoice(',s)
        world=(ROOT/'components/reference/ApexWorld.tsx').read_text()
        self.assertIn('trace={liveTrace as',world)
        self.assertIn('reducedMotion={reduced}',world)
        self.assertIn('femaleState={connected ? orbState : undefined}',s)
        self.assertIn('state={femaleState ?? orbState}',world)
        self.assertIn('pulseSignal={femalePulse}',world)
