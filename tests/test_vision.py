import unittest
import numpy as np
from gesturecam.vision.hands import HandTracker
from gesturecam.vision.face import FaceTracker
from gesturecam.vision.gestures import GestureRecognizer

class TestVisionWrappers(unittest.TestCase):
    
    def test_instantiation(self):
        # Just check if we can instantiate without errors (dependencies loaded)
        ht = HandTracker()
        ft = FaceTracker()
        gr = GestureRecognizer()
        
        self.assertIsNotNone(ht)
        self.assertIsNotNone(ft)
        self.assertIsNotNone(gr)

    def test_gesture_logic_mock(self):
        gr = GestureRecognizer()
        
        # Mock hand data structure from cvzone
        # lmList is usually [ [x,y,z], ... ]
        # Index 4 is thumb, 8 is index
        mock_hand = {
            "lmList": [[0,0,0]] * 21,
            "center": (100, 100)
        }
        # Set specific coords
        mock_hand["lmList"][4] = [100, 100, 0]
        mock_hand["lmList"][8] = [130, 140, 0] # dist = 50
        
        dist = gr.check_pinch_zoom([mock_hand])
        self.assertEqual(int(dist), 50) # 30^2 + 40^2 = 50^2

        # Two hands
        mock_hand2 = {
            "lmList": [[0,0,0]] * 21,
            "center": (200, 200)
        }
        dist_2h = gr.check_two_hand_zoom([mock_hand, mock_hand2])
        # dist between 100,100 and 200,200 = sqrt(20000) ~ 141.4
        self.assertAlmostEqual(dist_2h, 141.42, places=1)

if __name__ == '__main__':
    unittest.main()
