"""Female edition integration guards, without audio or GPU dependencies."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/'apex_ui'

class FemaleInterfaceTests(unittest.TestCase):
    def test_original_volume_not_a_portrait_plane(self):
        s=(ROOT/'components/ApexFemaleHumanoid.tsx').read_text()
        for token in ('new THREE.SphereGeometry', 'g.computeVertexNormals()', 'new THREE.BufferGeometry()', 'new THREE.ShaderMaterial'):
            self.assertIn(token,s)
        self.assertNotIn('TextureLoader',s)
        self.assertNotIn('fetch(',s)

    def test_graphics_and_motion_have_bounded_fallbacks(self):
        s=(ROOT/'components/ApexFemaleHumanoid.tsx').read_text()
        for token in ('GraphicsBoundary','<Fallback/>','prefers-reduced-motion','dpr={[1,1.5]}','frameloop={reduced?"demand":"always"}','geometry.dispose()', 'material.dispose()'):
            self.assertIn(token,s)

    def test_audio_uses_existing_bridge_and_gaze_has_cleanup(self):
        s=(ROOT/'components/ApexFemaleHumanoid.tsx').read_text()
        self.assertIn('useJarvisAudioLevel()',s)
        self.assertIn('state==="speaking"?audio:0',s)
        self.assertIn('window.removeEventListener("pointermove",move)',s)
        self.assertNotIn('getUserMedia',s)

    def test_visual_switch_is_persisted_without_changing_voice(self):
        s=(ROOT/'components/ApexReferenceWorld.tsx').read_text()
        for token in ('localStorage.setItem("apex.figure"', 'aria-pressed={female===value}', 'female={female}'):
            self.assertIn(token,s)
        self.assertNotIn('choosePersona(',s)
        self.assertNotIn('setVoice(',s)
