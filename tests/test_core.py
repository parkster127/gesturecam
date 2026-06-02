import unittest

import numpy as np

from gesturecam.core.framing import FramingController
from gesturecam.core.zoom import ZoomController


class TestCoreLogic(unittest.TestCase):

    def test_zoom_logic(self):
        controller = ZoomController(min_zoom=1.0, max_zoom=3.0, smoothing_factor=1.0) # 1.0 = instant

        # Test basic limits
        controller.update_zoom_level(0.5)
        controller.step()
        self.assertEqual(controller.current_zoom, 1.0)

        controller.update_zoom_level(5.0)
        controller.step()
        self.assertEqual(controller.current_zoom, 3.0)

        # Test smoothing
        controller = ZoomController(smoothing_factor=0.5)
        controller.current_zoom = 1.0
        controller.update_zoom_level(3.0)
        controller.step() # Should move halfway to 3.0 -> 2.0
        self.assertAlmostEqual(controller.current_zoom, 2.0)

        # Test Apply Zoom (Crop)
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        controller.current_zoom = 2.0
        controller.set_zoom_center(0.5, 0.5)
        out = controller.apply_zoom(img)
        self.assertEqual(out.shape, (100, 100, 3))

    def test_framing_logic(self):
        framing = FramingController(smoothing_factor=1.0)

        # Test Face Follow
        framing.set_mode("face_follow")
        # Face at center of 1000x1000 image: 450, 450, 100, 100 -> Center 500,500
        framing.update_face_target((450, 450, 100, 100), 1000, 1000)
        framing.step()
        self.assertAlmostEqual(framing.current_center_x, 0.5)
        self.assertAlmostEqual(framing.current_center_y, 0.5)

        # Face at top-left: 0, 0, 100, 100 -> Center 50, 50 -> 0.05, 0.05
        framing.update_face_target((0, 0, 100, 100), 1000, 1000)
        framing.step()
        self.assertAlmostEqual(framing.current_center_x, 0.05)
        self.assertAlmostEqual(framing.current_center_y, 0.05)

if __name__ == '__main__':
    unittest.main()
