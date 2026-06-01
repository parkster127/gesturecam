"""
GestureCam Configuration System
Handles all application settings with persistence and validation.
"""

import json
import os
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, Literal
from pathlib import Path

logger = logging.getLogger(__name__)

# Type definitions
FramingMode = Literal["manual", "face_follow", "headshot", "shirt_up"]
VirtualCamBackend = Literal["obs", "v4l2", "unitycapture"]
Resolution = Literal["720p", "1080p", "1440p", "4k"]

# Resolution mapping
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
    show_overlay: bool = False  # Show detection landmarks
    zoom_speed_slow: float = 0.02  # Thumbs up/down
    zoom_speed_fast: float = 0.03  # Index pointing


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
    
    # Metadata
    version: str = "1.0.0"
    first_run: bool = True


class SettingsManager:
    """
    Manages application settings with persistence.
    Settings are stored in JSON format in the user's config directory.
    """
    
    APP_NAME = "GestureCam"
    SETTINGS_FILE = "settings.json"
    
    def __init__(self, config_dir: Optional[Path] = None):
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
                with open(self.settings_path, "r", encoding="utf-8") as f:
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


# Global settings instance (singleton pattern)
_settings_manager: Optional[SettingsManager] = None


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
