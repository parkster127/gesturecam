"""
GestureCam Application Constants
Central location for all application-wide constants.
"""

from pathlib import Path

# Application Info
APP_NAME = "GestureCam"
APP_ID = "dev.vectores.gesturecam"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Virtual camera with gesture control for zoom and auto-framing"
APP_AUTHOR = "Vectores"
APP_WEBSITE = "https://gesturecam.app"
APP_GITHUB = "https://github.com/vectores/gesture_cam"
APP_LICENSE = "MIT"
APP_COPYRIGHT = "© 2026 Vectores"

# Paths
ROOT_DIR = Path(__file__).parent.parent
MODELS_DIR = ROOT_DIR / "models"
ASSETS_DIR = ROOT_DIR / "assets"

# Model Files
HAND_MODEL_FILE = "hand_landmarker.task"
FACE_MODEL_FILE = "blaze_face_short_range.tflite"

# Camera Defaults
DEFAULT_CAMERA_INDEX = 0
DEFAULT_RESOLUTION = (1920, 1080)
DEFAULT_FPS = 30

# Zoom Constraints
MIN_ZOOM = 1.0
MAX_ZOOM = 5.0
DEFAULT_ZOOM = 1.0
ZOOM_STEP = 0.1

# Gesture Detection
HAND_DETECTION_CONFIDENCE = 0.5
HAND_TRACKING_CONFIDENCE = 0.5
FACE_DETECTION_CONFIDENCE = 0.5
MAX_HANDS = 2

# Smoothing Defaults
DEFAULT_ZOOM_SMOOTHING = 0.15
DEFAULT_FRAMING_SMOOTHING = 0.08

# Gesture Speeds
GESTURE_ZOOM_SLOW = 0.02  # Thumbs up/down
GESTURE_ZOOM_FAST = 0.03  # Index pointing
GESTURE_ZOOM_TWO_HAND_BASE = 300.0  # Base distance for 1.0x zoom

# Virtual Camera
VIRTUAL_CAM_NAME = "GestureCam"
VIRTUAL_CAM_BACKENDS = {
    "macos": "obs",
    "windows": "obs",  # or "unitycapture"
    "linux": "v4l2",
}

# UI Constants
WINDOW_MIN_WIDTH = 900
WINDOW_MIN_HEIGHT = 700
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 850
PREVIEW_ASPECT_RATIO = 16 / 9

# Colors (for overlay/debug)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_BLUE = (255, 0, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_CYAN = (255, 255, 0)
COLOR_MAGENTA = (255, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)

# Gesture Colors (BGR for OpenCV)
GESTURE_COLORS = {
    "zoom_in": (0, 200, 0),      # Green
    "zoom_out": (0, 100, 255),   # Orange
    "hold": (0, 200, 255),       # Yellow
    "neutral": (128, 128, 128),  # Gray
    "none": (100, 100, 100),     # Dark gray
}

# Framing Mode Icons (for UI)
FRAMING_MODES = {
    "manual": {
        "name": "Manual",
        "icon": "hand",
        "description": "No automatic tracking. Full manual control.",
    },
    "face_follow": {
        "name": "Face Follow",
        "icon": "face",
        "description": "Camera smoothly follows your face.",
    },
    "headshot": {
        "name": "Headshot",
        "icon": "portrait",
        "description": "Professional head framing for interviews.",
    },
    "shirt_up": {
        "name": "Shirt-Up",
        "icon": "person",
        "description": "Shows from chest up. Great for presentations.",
    },
}

# Gesture Definitions (for UI)
GESTURES = {
    "thumbs_up": {
        "name": "Thumbs Up",
        "action": "zoom_in",
        "icon": "👍",
        "color": "green",
    },
    "thumbs_down": {
        "name": "Thumbs Down",
        "action": "zoom_out",
        "icon": "👎",
        "color": "orange",
    },
    "point_up": {
        "name": "Point Up",
        "action": "zoom_in_fast",
        "icon": "☝️",
        "color": "cyan",
    },
    "point_down": {
        "name": "Point Down",
        "action": "zoom_out_fast",
        "icon": "👇",
        "color": "purple",
    },
    "open_palm": {
        "name": "Open Palm",
        "action": "hold",
        "icon": "🖐️",
        "color": "yellow",
    },
    "fist": {
        "name": "Fist",
        "action": "neutral",
        "icon": "✊",
        "color": "gray",
    },
}

# Resolution Presets
RESOLUTION_PRESETS = {
    "720p": {"width": 1280, "height": 720, "label": "720p (HD)"},
    "1080p": {"width": 1920, "height": 1080, "label": "1080p (Full HD)"},
    "1440p": {"width": 2560, "height": 1440, "label": "1440p (2K)"},
    "4k": {"width": 3840, "height": 2160, "label": "4K (Ultra HD)"},
}

# FPS Presets
FPS_PRESETS = [24, 30, 60]

# Keyboard Shortcuts
SHORTCUTS = {
    "toggle_camera": "Ctrl+Shift+C",
    "toggle_gestures": "Ctrl+Shift+G",
    "reset_zoom": "Ctrl+0",
    "zoom_in": "Ctrl+=",
    "zoom_out": "Ctrl+-",
    "mode_manual": "Ctrl+1",
    "mode_face_follow": "Ctrl+2",
    "mode_headshot": "Ctrl+3",
    "mode_shirt_up": "Ctrl+4",
    "settings": "Ctrl+,",
    "quit": "Ctrl+Q",
}

# Platform Detection
import platform

PLATFORM = platform.system().lower()
IS_MACOS = PLATFORM == "darwin"
IS_WINDOWS = PLATFORM == "windows"
IS_LINUX = PLATFORM == "linux"

# Get appropriate virtual cam backend
def get_default_backend() -> str:
    """Get the default virtual camera backend for the current platform."""
    if IS_MACOS:
        return "obs"
    elif IS_WINDOWS:
        return "obs"
    elif IS_LINUX:
        return "v4l2"
    return "obs"
