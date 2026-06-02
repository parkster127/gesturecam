import cv2
import logging
import os
import json
from typing import Optional, Tuple


class FaceTracker:
    """Face detection with optional FaceMesh for 468-landmark tracking."""

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        model_path: Optional[str] = None,
        use_face_mesh: bool = False,
        calibration_file: Optional[str] = None,
    ):
        self.mock_mode = False
        self.face_detector = None
        self.face_mesh_tracker = None
        self.use_face_mesh = use_face_mesh

        self.calibration = self._load_calibration(calibration_file)

        if use_face_mesh:
            self._init_face_mesh(min_detection_confidence)
        else:
            self._init_blaze_face(min_detection_confidence, model_path)

    def _load_calibration(self, calibration_file: Optional[str]) -> dict:
        """Load personal calibration profile"""
        if calibration_file is None:
            possible_paths = [
                "calibration_profile.json",
                os.path.join(
                    os.path.dirname(__file__), "..", "..", "calibration_profile.json"
                ),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    calibration_file = path
                    break

        if calibration_file and os.path.exists(calibration_file):
            try:
                with open(calibration_file, "r") as f:
                    data = json.load(f)
                    logging.info(f"Loaded face calibration from {calibration_file}")
                    return data.get("recommended_thresholds", {})
            except Exception as e:
                logging.warning(f"Failed to load calibration: {e}")

        return {}

    def _init_face_mesh(self, min_detection_confidence: float):
        """Initialize Face Mesh for detailed landmark detection"""
        try:
            from .face_mesh import FaceMeshTracker

            self.face_mesh_tracker = FaceMeshTracker(
                min_detection_confidence=min_detection_confidence,
                min_tracking_confidence=0.5,
                refine_landmarks=True,
            )

            if "ear_threshold" in self.calibration:
                self.face_mesh_tracker.ear_threshold = self.calibration["ear_threshold"]
                logging.info(
                    f"Applied calibrated EAR threshold: {self.calibration['ear_threshold']}"
                )

            logging.info("FaceMesh mode enabled with full landmark detection")

        except Exception as e:
            logging.warning(f"FaceMesh init failed: {e}. Falling back to basic mode.")
            self.use_face_mesh = False
            self._init_blaze_face(min_detection_confidence, None)

    def _init_blaze_face(
        self, min_detection_confidence: float, model_path: Optional[str]
    ):
        """Initialize basic face detection with BlazeFace"""
        if model_path is None:
            possible_paths = [
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "models",
                    "blaze_face_short_range.tflite",
                ),
                os.path.join(os.getcwd(), "models", "blaze_face_short_range.tflite"),
                "/Users/martin/Dev/Vectores/gesture_cam/models/blaze_face_short_range.tflite",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    model_path = path
                    break

        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision as mp_vision

            if model_path and os.path.exists(model_path):
                base_options = mp_python.BaseOptions(model_asset_path=model_path)
                options = mp_vision.FaceDetectorOptions(
                    base_options=base_options,
                    running_mode=mp_vision.RunningMode.IMAGE,
                    min_detection_confidence=min_detection_confidence,
                )
                self.face_detector = mp_vision.FaceDetector.create_from_options(options)
                logging.info(f"MediaPipe FaceDetector loaded from {model_path}")
            else:
                raise FileNotFoundError(
                    f"Face model not found. Tried: {possible_paths}"
                )

        except Exception as e:
            logging.warning(
                f"MediaPipe Face Detection not found/working: {e}. Using MOCK mode."
            )
            self.mock_mode = True

    def detect_face(self, frame):
        """
        Detects faces.
        Returns:
            face_bbox: (x, y, w, h) of the primary face (largest), or None.
            results: Raw mediapipe results, FaceMetrics (if using face_mesh), or None in mock.
        """
        if self.mock_mode:
            return self._mock_detect(frame)

        # Use Face Mesh for detailed detection if enabled
        if self.use_face_mesh and self.face_mesh_tracker is not None:
            return self._detect_with_mesh(frame)

        return self._detect_with_blaze(frame)

    def _detect_with_mesh(self, frame):
        """Detect using Face Mesh (detailed landmarks)"""
        metrics = self.face_mesh_tracker.detect(frame)

        if not metrics.detected:
            return None, metrics

        return metrics.bbox, metrics

    def _detect_with_blaze(self, frame):
        """Detect using BlazeFace (fast bounding box only)"""
        import mediapipe as mp

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

        result = self.face_detector.detect(mp_image)

        primary_face = None
        max_area = 0
        h, w, _ = frame.shape

        if result.detections:
            for detection in result.detections:
                bbox = detection.bounding_box
                x = int(bbox.origin_x)
                y = int(bbox.origin_y)
                w_box = int(bbox.width)
                h_box = int(bbox.height)

                area = w_box * h_box
                if area > max_area:
                    max_area = area
                    primary_face = (x, y, w_box, h_box)

        return primary_face, result

    def detect_detailed(self, frame):
        """
        Detailed face detection with full metrics (requires use_face_mesh=True).

        Returns:
            FaceMetrics object with all landmarks, EAR, MAR, pose, etc.
        """
        if not self.use_face_mesh or self.face_mesh_tracker is None:
            logging.warning("detect_detailed requires use_face_mesh=True")
            return None

        return self.face_mesh_tracker.detect(frame)

    def get_eye_metrics(self, frame):
        """
        Get eye-specific metrics (EAR, gaze direction, etc.)

        Returns tuple: (left_eye_metrics, right_eye_metrics) or (None, None)
        """
        if not self.use_face_mesh or self.face_mesh_tracker is None:
            return None, None

        metrics = self.face_mesh_tracker.detect(frame)
        if not metrics.detected:
            return None, None

        return metrics.left_eye, metrics.right_eye

    def draw_debug(self, frame, metrics=None, **kwargs):
        """
        Draw debug overlay on frame.

        Args:
            frame: BGR image
            metrics: FaceMetrics (optional, will detect if not provided)
            **kwargs: Passed to draw_debug_overlay (show_mesh, show_eyes, etc.)
        """
        if not self.use_face_mesh or self.face_mesh_tracker is None:
            return frame

        if metrics is None:
            metrics = self.face_mesh_tracker.detect(frame)

        return self.face_mesh_tracker.draw_debug_overlay(frame, metrics, **kwargs)

    def _mock_detect(self, frame):
        return None, None

    def close(self):
        """Release resources"""
        if self.face_mesh_tracker:
            self.face_mesh_tracker.close()
