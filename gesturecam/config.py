from dataclasses import dataclass


@dataclass
class Config:
    # Camera Settings
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 1280
    CAMERA_HEIGHT: int = 720
    FPS: int = 30

    # Hand Tracking
    HAND_DETECTION_CONFIDENCE: float = 0.5
    HAND_TRACKING_CONFIDENCE: float = 0.5
    MAX_HANDS: int = 2

    # Face Tracking
    FACE_DETECTION_CONFIDENCE: float = 0.5
    USE_FACE_MESH: bool = True
    FACE_MESH_REFINE_LANDMARKS: bool = True  # 478 landmarks with iris

    EAR_THRESHOLD: float = 0.21
    MAR_THRESHOLD: float = 0.5

    CALIBRATION_FILE: str = "calibration_profile.json"

    # Zoom Settings
    MIN_ZOOM: float = 1.0
    MAX_ZOOM: float = 3.0
    ZOOM_SMOOTHING: float = 0.1  # 1.0 = no smoothing

    # Gesture Settings
    PINCH_THRESHOLD_LOWER: int = 30
    PINCH_THRESHOLD_UPPER: int = 150

    # Framing
    FRAMING_SMOOTHING: float = 0.1

    # Virtual Camera
    VIRTUAL_CAM_ENABLED: bool = True
    VIRTUAL_CAM_BACKEND: str = (
        "v4l2"  # 'v4l2' for Linux, 'obs' for Windows/OBS plugin if applicable
    )

    # Debug/Analysis
    DEBUG_OVERLAY: bool = False  # Show debug visualization
    SAVE_ANALYSIS_DATA: bool = False  # Save face vectors for analysis
