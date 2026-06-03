"""
GestureCam Configuration System
Handles all application settings with persistence and validation.
"""

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Literal

logger = logging.getLogger(__name__)

FramingMode = Literal["manual", "face_follow", "headshot", "shirt_up"]
VirtualCamBackend = Literal["obs", "v4l2", "unitycapture"]
Resolution = Literal["720p", "1080p", "1440p", "4k"]

RESOLUTIONS = {
    "720p": (1280, 720),
    "1080p": (1920, 1080),
    "1440p": (2560, 1440),
    "4k": (3840, 2160),
}


@dataclass
class CameraSettings:
    """Camera input settings."""

    device_index: int = 0
    device_name: str = ""
    resolution: Resolution = "1080p"
    fps: int = 30
    mirror: bool = True  # Flip horizontally for selfie view


@dataclass
class ZoomSettings:
    """Zoom control settings."""

    min_zoom: float = 1.0
    max_zoom: float = 3.0
    smoothing: float = 0.15  # 0.0 = instant, 1.0 = very slow
    default_zoom: float = 1.0


@dataclass
class FramingSettings:
    """Auto-framing settings."""

    default_mode: FramingMode = "face_follow"
    smoothing: float = 0.08  # Lower = smoother tracking
    face_padding: float = 0.3  # Extra space around face (0.0 - 1.0)


@dataclass
class GestureSettings:
    """Gesture recognition settings."""

    enabled: bool = True
    two_hand_enabled: bool = True
    detection_confidence: float = 0.5
    tracking_confidence: float = 0.5
    show_overlay: bool = False
    zoom_speed_slow: float = 0.02
    zoom_speed_fast: float = 0.03
    gesture_cooldown: float = 0.5
    thumbs_up_enabled: bool = True
    thumbs_down_enabled: bool = True
    pinch_enabled: bool = True
    peace_enabled: bool = True
    wink_enabled: bool = True


PRESET_PROFILES = {
    "Default": {},
    "Streaming": {
        "camera": {"resolution": "1080p", "fps": 30},
        "zoom": {"min_zoom": 1.0, "max_zoom": 3.0, "smoothing": 0.10},
        "framing": {"default_mode": "face_follow", "smoothing": 0.08},
        "gestures": {"enabled": True, "detection_confidence": 0.6},
    },
    "Meeting": {
        "camera": {"resolution": "720p", "fps": 30},
        "zoom": {"min_zoom": 1.0, "max_zoom": 2.0, "smoothing": 0.15},
        "framing": {"default_mode": "shirt_up", "smoothing": 0.10},
        "gestures": {"enabled": True, "detection_confidence": 0.5},
    },
    "Podcast": {
        "camera": {"resolution": "1080p", "fps": 24},
        "zoom": {"min_zoom": 1.0, "max_zoom": 2.5, "smoothing": 0.20},
        "framing": {"default_mode": "headshot", "smoothing": 0.05},
        "gestures": {"enabled": False},
    },
}


@dataclass
class OutputSettings:
    """Virtual camera output settings."""

    enabled: bool = True
    backend: VirtualCamBackend = "obs"
    device_name: str = "GestureCam"


@dataclass
class UISettings:
    """User interface settings."""

    language: str = "en"
    theme: str = "dark"
    start_minimized: bool = False
    minimize_to_tray: bool = True
    start_with_system: bool = False
    show_preview: bool = True
    preview_size: str = "medium"  # small, medium, large


@dataclass
class AppSettings:
    """Main application settings container."""

    camera: CameraSettings = field(default_factory=CameraSettings)
    zoom: ZoomSettings = field(default_factory=ZoomSettings)
    framing: FramingSettings = field(default_factory=FramingSettings)
    gestures: GestureSettings = field(default_factory=GestureSettings)
    output: OutputSettings = field(default_factory=OutputSettings)
    ui: UISettings = field(default_factory=UISettings)
    version: str = "1.0.0"
    first_run: bool = True


class SettingsManager:
    """
    Manages application settings with persistence.
    Settings are stored in JSON format in the user's config directory.
    """

    APP_NAME = "GestureCam"
    SETTINGS_FILE = "settings.json"

    def __init__(self, config_dir: Path | None = None):
        self.config_dir = config_dir or self._get_default_config_dir()
        self.settings_path = self.config_dir / self.SETTINGS_FILE
        self.settings = AppSettings()
        self._load()

    def _get_default_config_dir(self) -> Path:
        """Get platform-specific config directory."""
        if os.name == "nt":  # Windows
            base = Path(os.environ.get("APPDATA", "~"))
        elif os.name == "posix":
            if "darwin" in os.uname().sysname.lower():  # macOS
                base = Path.home() / "Library" / "Application Support"
            else:  # Linux
                base = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config"))
        else:
            base = Path.home()

        config_dir = base.expanduser() / self.APP_NAME
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir

    def _load(self) -> None:
        """Load settings from disk."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, encoding="utf-8") as f:
                    data = json.load(f)
                self.settings = self._dict_to_settings(data)
                logger.info(f"Settings loaded from {self.settings_path}")
            except Exception as e:
                logger.warning(f"Failed to load settings: {e}. Using defaults.")
                self.settings = AppSettings()
        else:
            logger.info("No settings file found. Using defaults.")
            self.settings = AppSettings()

    def save(self) -> None:
        """Save settings to disk."""
        try:
            data = self._settings_to_dict(self.settings)
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info(f"Settings saved to {self.settings_path}")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def reset(self) -> None:
        """Reset all settings to defaults."""
        self.settings = AppSettings()
        self.save()
        logger.info("Settings reset to defaults")

    def apply_profile(self, profile_name: str) -> None:
        """Apply a preset profile by name."""
        if profile_name not in PRESET_PROFILES:
            logger.warning(f"Unknown profile: {profile_name}")
            return
        self.settings = AppSettings()
        overrides = PRESET_PROFILES[profile_name]
        if "camera" in overrides:
            for k, v in overrides["camera"].items():
                setattr(self.settings.camera, k, v)
        if "zoom" in overrides:
            for k, v in overrides["zoom"].items():
                setattr(self.settings.zoom, k, v)
        if "framing" in overrides:
            for k, v in overrides["framing"].items():
                setattr(self.settings.framing, k, v)
        if "gestures" in overrides:
            for k, v in overrides["gestures"].items():
                setattr(self.settings.gestures, k, v)
        if "output" in overrides:
            for k, v in overrides["output"].items():
                setattr(self.settings.output, k, v)
        self.save()
        logger.info(f"Applied profile: {profile_name}")

    def _settings_to_dict(self, settings: AppSettings) -> dict:
        """Convert settings dataclass to dictionary."""
        return {
            "camera": asdict(settings.camera),
            "zoom": asdict(settings.zoom),
            "framing": asdict(settings.framing),
            "gestures": asdict(settings.gestures),
            "output": asdict(settings.output),
            "ui": asdict(settings.ui),
            "version": settings.version,
            "first_run": settings.first_run,
        }

    def _dict_to_settings(self, data: dict) -> AppSettings:
        """Convert dictionary to settings dataclass."""
        return AppSettings(
            camera=CameraSettings(**data.get("camera", {})),
            zoom=ZoomSettings(**data.get("zoom", {})),
            framing=FramingSettings(**data.get("framing", {})),
            gestures=GestureSettings(**data.get("gestures", {})),
            output=OutputSettings(**data.get("output", {})),
            ui=UISettings(**data.get("ui", {})),
            version=data.get("version", "1.0.0"),
            first_run=data.get("first_run", True),
        )

    # Convenience accessors
    @property
    def camera(self) -> CameraSettings:
        return self.settings.camera

    @property
    def zoom(self) -> ZoomSettings:
        return self.settings.zoom

    @property
    def framing(self) -> FramingSettings:
        return self.settings.framing

    @property
    def gestures(self) -> GestureSettings:
        return self.settings.gestures

    @property
    def output(self) -> OutputSettings:
        return self.settings.output

    @property
    def ui(self) -> UISettings:
        return self.settings.ui

    def get_resolution_tuple(self) -> tuple[int, int]:
        """Get camera resolution as (width, height) tuple."""
        return RESOLUTIONS.get(self.camera.resolution, (1920, 1080))

    def mark_first_run_complete(self) -> None:
        """Mark that onboarding has been completed."""
        self.settings.first_run = False
        self.save()


_settings_manager: SettingsManager | None = None


def get_settings() -> SettingsManager:
    """Get the global settings manager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager


def reset_settings_manager():
    """Reset the global settings manager (for testing)."""
    global _settings_manager
    _settings_manager = None
