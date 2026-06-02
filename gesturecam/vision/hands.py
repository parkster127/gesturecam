import logging
import os

import cv2


class HandTracker:
    def __init__(self, detection_confidence=0.5, max_hands=2, model_path=None):
        self.mock_mode = False
        self.hand_landmarker = None
        self.max_hands = max_hands

        # Find model path
        if model_path is None:
            # Try common locations
            possible_paths = [
                os.path.expanduser("~/.gesturecam/hand_landmarker.task"),
                os.path.join(
                    os.path.dirname(__file__), "..", "..", "models", "hand_landmarker.task"
                ),
                os.path.join(os.getcwd(), "models", "hand_landmarker.task"),
                "/Users/martin/Dev/Vectores/gesture_cam/models/hand_landmarker.task",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break

        try:
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision as mp_vision

            if model_path and os.path.exists(model_path):
                base_options = mp_python.BaseOptions(model_asset_path=model_path)
                options = mp_vision.HandLandmarkerOptions(
                    base_options=base_options,
                    running_mode=mp_vision.RunningMode.IMAGE,
                    num_hands=max_hands,
                    min_hand_detection_confidence=detection_confidence,
                    min_tracking_confidence=0.5,
                )
                self.hand_landmarker = mp_vision.HandLandmarker.create_from_options(options)
                logging.info(f"MediaPipe HandLandmarker loaded from {model_path}")
            else:
                raise FileNotFoundError(f"Hand model not found. Tried: {possible_paths}")

        except Exception as e:
            logging.warning(f"MediaPipe Hands not found/working: {e}. Using MOCK mode.")
            self.mock_mode = True

    def detect_hands(self, frame):
        """
        Detects hands.
        Returns list of dicts: {'lmList': [[x,y,z], ...], 'center': (cx, cy), 'bbox': (x,y,w,h)}
        """
        if self.mock_mode:
            return self._mock_detect(frame)

        import mediapipe as mp

        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        # Detect hands
        result = self.hand_landmarker.detect(mp_image)

        hands_list = []
        h, w, c = frame.shape

        if result.hand_landmarks:
            for hand_lms in result.hand_landmarks:
                lm_list = []
                x_list = []
                y_list = []

                for lm in hand_lms:
                    px, py = int(lm.x * w), int(lm.y * h)
                    lm_list.append([px, py, lm.z])
                    x_list.append(px)
                    y_list.append(py)

                # Calculate center (approx)
                if x_list and y_list:
                    cx, cy = int(sum(x_list) / len(x_list)), int(sum(y_list) / len(y_list))

                    hands_list.append(
                        {
                            "lmList": lm_list,
                            "center": (cx, cy),
                            "bbox": (
                                min(x_list),
                                min(y_list),
                                max(x_list) - min(x_list),
                                max(y_list) - min(y_list),
                            ),
                        }
                    )

        return hands_list

    def _mock_detect(self, frame):
        # Return a fake hand moving in a circle or just static for testing pipeline
        # For simplicity: No hands by default unless we implement a complex mock
        return []
