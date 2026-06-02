"""Face mesh detection with 468 landmarks, EAR/MAR analysis and head pose estimation."""

import cv2
import numpy as np
import logging
from dataclasses import dataclass, field
from typing import Optional, List, Tuple, Dict
import math


# MediaPipe Face Mesh landmark indices (key points)
class FaceMeshIndices:
    """Reference indices for MediaPipe Face Mesh 468 landmarks"""

    # Eye landmarks (6 points per eye for EAR calculation)
    LEFT_EYE = [362, 385, 387, 263, 373, 380]
    RIGHT_EYE = [33, 160, 158, 133, 153, 144]

    # Iris centers (requires refined landmarks)
    LEFT_IRIS = [468, 469, 470, 471, 472]  # 468 is center
    RIGHT_IRIS = [473, 474, 475, 476, 477]  # 473 is center

    # Eyebrow landmarks
    LEFT_EYEBROW = [276, 283, 282, 295, 285]
    RIGHT_EYEBROW = [46, 53, 52, 65, 55]

    # Lips/mouth landmarks
    UPPER_LIP = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
    LOWER_LIP = [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
    MOUTH_OUTER = [
        61,
        146,
        91,
        181,
        84,
        17,
        314,
        405,
        321,
        375,
        291,
        409,
        270,
        269,
        267,
        0,
        37,
        39,
        40,
        185,
    ]

    # Face contour
    FACE_OVAL = [
        10,
        338,
        297,
        332,
        284,
        251,
        389,
        356,
        454,
        323,
        361,
        288,
        397,
        365,
        379,
        378,
        400,
        377,
        152,
        148,
        176,
        149,
        150,
        136,
        172,
        58,
        132,
        93,
        234,
        127,
        162,
        21,
        54,
        103,
        67,
        109,
    ]

    # Nose landmarks
    NOSE_TIP = 1
    NOSE_BRIDGE = [6, 197, 195, 5]

    # Key reference points for head pose
    NOSE_TIP_IDX = 1
    CHIN = 152
    LEFT_EYE_LEFT = 263
    RIGHT_EYE_RIGHT = 33
    LEFT_MOUTH = 287
    RIGHT_MOUTH = 57


@dataclass
class EyeMetrics:
    """Data class for eye analysis metrics"""

    ear: float = 0.0  # Eye Aspect Ratio
    is_open: bool = True
    center: Tuple[float, float] = (0.0, 0.0)
    iris_center: Optional[Tuple[float, float]] = None
    gaze_direction: Optional[Tuple[float, float]] = None  # Normalized gaze vector
    landmarks: List[Tuple[float, float]] = field(default_factory=list)


@dataclass
class FaceMetrics:
    """Comprehensive face analysis metrics for data science"""

    # Detection status
    detected: bool = False
    confidence: float = 0.0

    # Bounding box (x, y, w, h)
    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)

    # Face center
    center: Tuple[float, float] = (0.0, 0.0)

    # Head pose (in degrees)
    pitch: float = 0.0  # Nodding up/down
    yaw: float = 0.0  # Turning left/right
    roll: float = 0.0  # Tilting head

    # Eye metrics
    left_eye: EyeMetrics = field(default_factory=EyeMetrics)
    right_eye: EyeMetrics = field(default_factory=EyeMetrics)
    avg_ear: float = 0.0  # Average EAR for blink detection

    # Mouth metrics
    mar: float = 0.0  # Mouth Aspect Ratio
    is_mouth_open: bool = False

    # All 468 landmarks as numpy array for advanced analysis
    landmarks_array: Optional[np.ndarray] = None

    # Feature vector for ML/analysis (normalized)
    feature_vector: Optional[np.ndarray] = None


class FaceMeshTracker:
    """
    Advanced face tracking with full landmark detection.
    Optimized for data science analysis and debugging.
    """

    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
        refine_landmarks: bool = True,  # Enables iris detection
        max_faces: int = 1,
        static_image_mode: bool = False,
    ):
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self.refine_landmarks = refine_landmarks
        self.max_faces = max_faces
        self.static_image_mode = static_image_mode

        self.mock_mode = False
        self.face_mesh = None

        # Thresholds (adjustable)
        self.ear_threshold = 0.21  # Below this = eye closed
        self.mar_threshold = 0.5  # Above this = mouth open

        # Historical data for analysis
        self.history_size = 30  # frames
        self.ear_history: List[float] = []
        self.mar_history: List[float] = []
        self.pose_history: List[Tuple[float, float, float]] = []

        self._initialize_mediapipe()

    def _initialize_mediapipe(self):
        """Initialize MediaPipe Face Mesh"""
        import os
        try:
            import mediapipe as mp
            from mediapipe.tasks import python as mp_python
            from mediapipe.tasks.python import vision as mp_vision

            model_path = os.path.expanduser('~/.gesturecam/face_landmarker.task')
            if not os.path.exists(model_path):
                import urllib.request
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
                urllib.request.urlretrieve(url, model_path)

            base_options = mp_python.BaseOptions(model_asset_path=model_path)
            options = mp_vision.FaceLandmarkerOptions(
                base_options=base_options,
                running_mode=mp_vision.RunningMode.IMAGE,
                num_faces=self.max_faces,
                output_face_blendshapes=self.refine_landmarks,
                min_face_detection_confidence=self.min_detection_confidence,
                min_face_presence_confidence=self.min_tracking_confidence,
                min_tracking_confidence=self.min_tracking_confidence
            )

            self.face_mesh = mp_vision.FaceLandmarker.create_from_options(options)

            logging.info(
                f"MediaPipe FaceLandmarker Task initialized (refine_landmarks={self.refine_landmarks})"
            )

        except Exception as e:
            logging.warning(
                f"Failed to initialize MediaPipe FaceLandmarker: {e}. Using mock mode."
            )
            self.mock_mode = True

    def _calculate_ear(self, eye_landmarks: List[Tuple[float, float]]) -> float:
        """
        Calculate Eye Aspect Ratio (EAR).

        EAR = (||p2-p6|| + ||p3-p5||) / (2 * ||p1-p4||)
        """
        if len(eye_landmarks) < 6:
            return 0.0

        # Vertical distances
        v1 = math.dist(eye_landmarks[1], eye_landmarks[5])  # p2-p6
        v2 = math.dist(eye_landmarks[2], eye_landmarks[4])  # p3-p5

        # Horizontal distance
        h = math.dist(eye_landmarks[0], eye_landmarks[3])  # p1-p4

        if h == 0:
            return 0.0

        ear = (v1 + v2) / (2.0 * h)
        return ear

    def _calculate_mar(self, landmarks: np.ndarray) -> float:
        """
        Calculate Mouth Aspect Ratio (MAR).

        Uses vertical mouth opening divided by horizontal width.
        """
        # Upper lip center (index 13)
        # Lower lip center (index 14)
        # Mouth corners (61 and 291)

        upper = landmarks[13]
        lower = landmarks[14]
        left_corner = landmarks[61]
        right_corner = landmarks[291]

        vertical = math.dist(upper, lower)
        horizontal = math.dist(left_corner, right_corner)

        if horizontal == 0:
            return 0.0

        return vertical / horizontal

    def _estimate_head_pose(
        self, landmarks: np.ndarray, frame_shape: Tuple[int, int]
    ) -> Tuple[float, float, float]:
        """
        Estimate head pose (pitch, yaw, roll) from face landmarks.

        Uses solvePnP with a standard 3D face model.

        Returns: (pitch, yaw, roll) in degrees
        """
        h, w = frame_shape[:2]

        # 2D image points (selected landmarks)
        image_points = np.array(
            [
                landmarks[FaceMeshIndices.NOSE_TIP_IDX],  # Nose tip
                landmarks[FaceMeshIndices.CHIN],  # Chin
                landmarks[FaceMeshIndices.LEFT_EYE_LEFT],  # Left eye left corner
                landmarks[FaceMeshIndices.RIGHT_EYE_RIGHT],  # Right eye right corner
                landmarks[FaceMeshIndices.LEFT_MOUTH],  # Left mouth corner
                landmarks[FaceMeshIndices.RIGHT_MOUTH],  # Right mouth corner
            ],
            dtype=np.float64,
        )

        # 3D model points (standard face model)
        model_points = np.array(
            [
                (0.0, 0.0, 0.0),  # Nose tip
                (0.0, -330.0, -65.0),  # Chin
                (-225.0, 170.0, -135.0),  # Left eye left corner
                (225.0, 170.0, -135.0),  # Right eye right corner
                (-150.0, -150.0, -125.0),  # Left Mouth corner
                (150.0, -150.0, -125.0),  # Right mouth corner
            ],
            dtype=np.float64,
        )

        # Camera matrix (approximate)
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array(
            [[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]],
            dtype=np.float64,
        )

        dist_coeffs = np.zeros((4, 1))

        try:
            success, rotation_vector, translation_vector = cv2.solvePnP(
                model_points,
                image_points,
                camera_matrix,
                dist_coeffs,
                flags=cv2.SOLVEPNP_ITERATIVE,
            )

            if not success:
                return 0.0, 0.0, 0.0

            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

            # Get Euler angles
            proj_matrix = np.hstack((rotation_matrix, translation_vector))
            _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(proj_matrix)

            pitch = euler_angles[0][0]
            yaw = euler_angles[1][0]
            roll = euler_angles[2][0]

            return pitch, yaw, roll

        except Exception as e:
            logging.debug(f"Head pose estimation failed: {e}")
            return 0.0, 0.0, 0.0

    def _extract_eye_landmarks(
        self, landmarks: np.ndarray, indices: List[int]
    ) -> List[Tuple[float, float]]:
        """Extract eye landmark coordinates"""
        return [(landmarks[i][0], landmarks[i][1]) for i in indices]

    def _get_eye_center(
        self, eye_landmarks: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """Calculate center of eye from landmarks"""
        if not eye_landmarks:
            return (0.0, 0.0)
        x = sum(p[0] for p in eye_landmarks) / len(eye_landmarks)
        y = sum(p[1] for p in eye_landmarks) / len(eye_landmarks)
        return (x, y)

    def _get_iris_center(
        self, landmarks: np.ndarray, iris_indices: List[int]
    ) -> Optional[Tuple[float, float]]:
        """Get iris center (requires refine_landmarks=True)"""
        if not self.refine_landmarks:
            return None
        try:
            center_idx = iris_indices[0]  # First index is the center
            return (landmarks[center_idx][0], landmarks[center_idx][1])
        except IndexError:
            return None

    def _compute_gaze_direction(
        self,
        eye_center: Tuple[float, float],
        iris_center: Optional[Tuple[float, float]],
    ) -> Optional[Tuple[float, float]]:
        """
        Compute normalized gaze direction vector.

        Returns: (dx, dy) normalized vector, or None if iris not detected
        """
        if iris_center is None:
            return None

        dx = iris_center[0] - eye_center[0]
        dy = iris_center[1] - eye_center[1]

        magnitude = math.sqrt(dx**2 + dy**2)
        if magnitude == 0:
            return (0.0, 0.0)

        return (dx / magnitude, dy / magnitude)

    def _create_feature_vector(self, metrics: FaceMetrics) -> np.ndarray:
        """Normalized feature vector from face metrics."""
        features = [
            metrics.left_eye.ear,
            metrics.right_eye.ear,
            metrics.avg_ear,
            metrics.mar,
            metrics.pitch / 90.0,  # Normalize to [-1, 1]
            metrics.yaw / 90.0,
            metrics.roll / 90.0,
            1.0 if metrics.left_eye.is_open else 0.0,
            1.0 if metrics.right_eye.is_open else 0.0,
            1.0 if metrics.is_mouth_open else 0.0,
        ]

        # Add gaze if available
        if metrics.left_eye.gaze_direction:
            features.extend(list(metrics.left_eye.gaze_direction))
        else:
            features.extend([0.0, 0.0])

        if metrics.right_eye.gaze_direction:
            features.extend(list(metrics.right_eye.gaze_direction))
        else:
            features.extend([0.0, 0.0])

        return np.array(features, dtype=np.float32)

    def _update_history(self, metrics: FaceMetrics):
        """Update historical data for trend analysis"""
        self.ear_history.append(metrics.avg_ear)
        self.mar_history.append(metrics.mar)
        self.pose_history.append((metrics.pitch, metrics.yaw, metrics.roll))

        if len(self.ear_history) > self.history_size:
            self.ear_history.pop(0)
        if len(self.mar_history) > self.history_size:
            self.mar_history.pop(0)
        if len(self.pose_history) > self.history_size:
            self.pose_history.pop(0)

    def detect(self, frame: np.ndarray) -> FaceMetrics:
        """
        Detect face and extract all metrics.

        Args:
            frame: BGR image from OpenCV

        Returns:
            FaceMetrics object with all analysis data
        """
        if self.mock_mode:
            return FaceMetrics()

        metrics = FaceMetrics()
        h, w, _ = frame.shape

        import mediapipe as mp
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        results = self.face_mesh.detect(mp_image)

        if not results.face_landmarks:
            return metrics

        # Process first face (primary)
        face_landmarks = results.face_landmarks[0]

        # Convert to numpy array with pixel coordinates
        landmarks = np.array(
            [
                [lm.x * w, lm.y * h, lm.z * w]  # z is also scaled by width
                for lm in face_landmarks
            ]
        )

        metrics.detected = True
        metrics.landmarks_array = landmarks

        # Calculate bounding box from face oval
        face_oval_points = landmarks[FaceMeshIndices.FACE_OVAL]
        x_min = int(np.min(face_oval_points[:, 0]))
        y_min = int(np.min(face_oval_points[:, 1]))
        x_max = int(np.max(face_oval_points[:, 0]))
        y_max = int(np.max(face_oval_points[:, 1]))
        metrics.bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
        metrics.center = ((x_min + x_max) / 2, (y_min + y_max) / 2)

        # Extract eye landmarks
        left_eye_lms = self._extract_eye_landmarks(landmarks, FaceMeshIndices.LEFT_EYE)
        right_eye_lms = self._extract_eye_landmarks(
            landmarks, FaceMeshIndices.RIGHT_EYE
        )

        # Calculate EAR for each eye
        left_ear = self._calculate_ear(left_eye_lms)
        right_ear = self._calculate_ear(right_eye_lms)
        metrics.avg_ear = (left_ear + right_ear) / 2.0

        # Eye centers
        left_eye_center = self._get_eye_center(left_eye_lms)
        right_eye_center = self._get_eye_center(right_eye_lms)

        # Iris centers (if refine_landmarks enabled)
        left_iris = (
            self._get_iris_center(landmarks, FaceMeshIndices.LEFT_IRIS)
            if len(landmarks) > 468
            else None
        )
        right_iris = (
            self._get_iris_center(landmarks, FaceMeshIndices.RIGHT_IRIS)
            if len(landmarks) > 468
            else None
        )

        # Gaze direction
        left_gaze = self._compute_gaze_direction(left_eye_center, left_iris)
        right_gaze = self._compute_gaze_direction(right_eye_center, right_iris)

        # Populate eye metrics
        metrics.left_eye = EyeMetrics(
            ear=left_ear,
            is_open=left_ear > self.ear_threshold,
            center=left_eye_center,
            iris_center=left_iris,
            gaze_direction=left_gaze,
            landmarks=left_eye_lms,
        )

        metrics.right_eye = EyeMetrics(
            ear=right_ear,
            is_open=right_ear > self.ear_threshold,
            center=right_eye_center,
            iris_center=right_iris,
            gaze_direction=right_gaze,
            landmarks=right_eye_lms,
        )

        # Mouth aspect ratio
        metrics.mar = self._calculate_mar(landmarks)
        metrics.is_mouth_open = metrics.mar > self.mar_threshold

        # Head pose estimation
        pitch, yaw, roll = self._estimate_head_pose(landmarks, frame.shape)
        metrics.pitch = pitch
        metrics.yaw = yaw
        metrics.roll = roll

        # Create feature vector
        metrics.feature_vector = self._create_feature_vector(metrics)

        # Update history for analysis
        self._update_history(metrics)

        return metrics

    def get_statistics(self) -> Dict:
        """
        Get statistical analysis of recent detections.

        Returns dict with:
        - ear_mean, ear_std: Eye openness statistics
        - mar_mean, mar_std: Mouth openness statistics
        - blink_count_estimate: Estimated blinks in history
        - head_movement: Average head movement magnitude
        """
        stats = {
            "ear_mean": 0.0,
            "ear_std": 0.0,
            "mar_mean": 0.0,
            "mar_std": 0.0,
            "blink_count_estimate": 0,
            "head_movement": 0.0,
            "samples": len(self.ear_history),
        }

        if not self.ear_history:
            return stats

        ear_arr = np.array(self.ear_history)
        mar_arr = np.array(self.mar_history)

        stats["ear_mean"] = float(np.mean(ear_arr))
        stats["ear_std"] = float(np.std(ear_arr))
        stats["mar_mean"] = float(np.mean(mar_arr))
        stats["mar_std"] = float(np.std(mar_arr))

        blinks = 0
        prev_open = True
        for ear in self.ear_history:
            currently_open = ear > self.ear_threshold
            if prev_open and not currently_open:
                blinks += 1
            prev_open = currently_open
        stats["blink_count_estimate"] = blinks

        # Head movement (average change in pose)
        if len(self.pose_history) > 1:
            movements = []
            for i in range(1, len(self.pose_history)):
                prev = self.pose_history[i - 1]
                curr = self.pose_history[i]
                movement = math.sqrt(
                    (curr[0] - prev[0]) ** 2
                    + (curr[1] - prev[1]) ** 2
                    + (curr[2] - prev[2]) ** 2
                )
                movements.append(movement)
            stats["head_movement"] = float(np.mean(movements))

        return stats

    def draw_debug_overlay(
        self,
        frame: np.ndarray,
        metrics: FaceMetrics,
        show_mesh: bool = True,
        show_eyes: bool = True,
        show_iris: bool = True,
        show_metrics: bool = True,
        show_pose: bool = True,
    ) -> np.ndarray:
        """
        Draw comprehensive debug visualization on frame.

        Args:
            frame: BGR image
            metrics: FaceMetrics from detect()
            show_*: Toggle different overlay elements

        Returns:
            Frame with debug overlay
        """
        if not metrics.detected:
            cv2.putText(
                frame,
                "No face detected",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2,
            )
            return frame

        debug_frame = frame.copy()

        # Draw face mesh
        if show_mesh and metrics.landmarks_array is not None:
            # Draw face oval
            for idx in FaceMeshIndices.FACE_OVAL:
                pt = tuple(metrics.landmarks_array[idx][:2].astype(int))
                cv2.circle(debug_frame, pt, 1, (200, 200, 200), -1)

        # Draw eyes
        if show_eyes:
            # Left eye (green)
            for pt in metrics.left_eye.landmarks:
                cv2.circle(debug_frame, (int(pt[0]), int(pt[1])), 2, (0, 255, 0), -1)

            # Right eye (blue)
            for pt in metrics.right_eye.landmarks:
                cv2.circle(debug_frame, (int(pt[0]), int(pt[1])), 2, (255, 0, 0), -1)

            # Eye centers
            cv2.circle(
                debug_frame,
                (int(metrics.left_eye.center[0]), int(metrics.left_eye.center[1])),
                4,
                (0, 255, 255),
                -1,
            )
            cv2.circle(
                debug_frame,
                (int(metrics.right_eye.center[0]), int(metrics.right_eye.center[1])),
                4,
                (0, 255, 255),
                -1,
            )

        # Draw iris
        if show_iris:
            if metrics.left_eye.iris_center:
                cv2.circle(
                    debug_frame,
                    (
                        int(metrics.left_eye.iris_center[0]),
                        int(metrics.left_eye.iris_center[1]),
                    ),
                    3,
                    (255, 0, 255),
                    -1,
                )
            if metrics.right_eye.iris_center:
                cv2.circle(
                    debug_frame,
                    (
                        int(metrics.right_eye.iris_center[0]),
                        int(metrics.right_eye.iris_center[1]),
                    ),
                    3,
                    (255, 0, 255),
                    -1,
                )

            # Draw gaze direction
            if metrics.left_eye.gaze_direction and metrics.left_eye.iris_center:
                gx, gy = metrics.left_eye.gaze_direction
                ix, iy = metrics.left_eye.iris_center
                cv2.arrowedLine(
                    debug_frame,
                    (int(ix), int(iy)),
                    (int(ix + gx * 30), int(iy + gy * 30)),
                    (255, 0, 255),
                    2,
                )

        # Draw metrics overlay
        if show_metrics:
            y_offset = 30
            metrics_text = [
                f"L-EAR: {metrics.left_eye.ear:.3f} {'OPEN' if metrics.left_eye.is_open else 'CLOSED'}",
                f"R-EAR: {metrics.right_eye.ear:.3f} {'OPEN' if metrics.right_eye.is_open else 'CLOSED'}",
                f"AVG-EAR: {metrics.avg_ear:.3f}",
                f"MAR: {metrics.mar:.3f} {'OPEN' if metrics.is_mouth_open else 'CLOSED'}",
            ]

            for text in metrics_text:
                cv2.putText(
                    debug_frame,
                    text,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
                y_offset += 20

        # Draw head pose
        if show_pose:
            y_offset = frame.shape[0] - 80
            pose_text = [
                f"Pitch: {metrics.pitch:.1f}",
                f"Yaw: {metrics.yaw:.1f}",
                f"Roll: {metrics.roll:.1f}",
            ]

            for text in pose_text:
                cv2.putText(
                    debug_frame,
                    text,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 0),
                    1,
                )
                y_offset += 20

        # Draw bounding box
        x, y, w, h = metrics.bbox
        cv2.rectangle(debug_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return debug_frame

    def close(self):
        """Release resources"""
        if self.face_mesh:
            self.face_mesh.close()
