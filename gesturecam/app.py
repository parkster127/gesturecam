"""
GestureCam Application Controller
Orchestrates all components and manages application state.
"""

import logging
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum

from gesturecam.settings import get_settings, SettingsManager
from gesturecam.i18n import get_i18n, t, set_language
from gesturecam.constants import (
    APP_NAME, APP_VERSION, 
    FRAMING_MODES, GESTURES,
    IS_MACOS, IS_WINDOWS
)

logger = logging.getLogger(__name__)


class AppState(Enum):
    """Application lifecycle states."""
    INITIALIZING = "initializing"
    ONBOARDING = "onboarding"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTDOWN = "shutdown"


@dataclass
class CameraStatus:
    """Real-time camera status information."""
    connected: bool = False
    device_name: str = ""
    resolution: tuple = (0, 0)
    fps: int = 0
    latency_ms: float = 0.0


@dataclass
class GestureStatus:
    """Real-time gesture detection status."""
    action: str = "none"  # zoom_in, zoom_out, hold, none
    detected_gesture: str = ""  # thumbs_up, thumbs_down, etc.
    confidence: float = 0.0
    hands_detected: int = 0


@dataclass
class ZoomStatus:
    """Real-time zoom status."""
    current_level: float = 1.0
    target_level: float = 1.0
    center_x: float = 0.5
    center_y: float = 0.5


class AppController:
    """
    Main application controller.
    Manages state, coordinates components, and provides callbacks for UI updates.
    """
    
    def __init__(self):
        self.settings: SettingsManager = get_settings()
        self.i18n = get_i18n()
        
        self.state: AppState = AppState.INITIALIZING
        self.onboarding_step: int = 1
        self.total_onboarding_steps: int = 3
        
        self.camera_status = CameraStatus()
        self.gesture_status = GestureStatus()
        self.zoom_status = ZoomStatus()
        
        self.current_mode: str = self.settings.framing.default_mode
        self.virtual_cam_active: bool = False
        
        self._on_state_change: Optional[Callable] = None
        self._on_camera_update: Optional[Callable] = None
        self._on_gesture_update: Optional[Callable] = None
        self._on_zoom_update: Optional[Callable] = None
        self._on_mode_change: Optional[Callable] = None
        
        self._pipeline = None  # initialized in _initialize_components
        
        logger.info(f"{APP_NAME} v{APP_VERSION} controller initialized")
    
    # === Lifecycle Methods ===
    
    def initialize(self) -> bool:
        """
        Initialize all components.
        Returns True if successful, False otherwise.
        """
        try:
            self._set_state(AppState.INITIALIZING)
            
            set_language(self.settings.ui.language)
            
            if self.settings.settings.first_run:
                self._set_state(AppState.ONBOARDING)
                return True
            
            if self._initialize_components():
                self._set_state(AppState.READY)
                return True
            else:
                self._set_state(AppState.ERROR)
                return False
                
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self._set_state(AppState.ERROR)
            return False
    
    def _initialize_components(self) -> bool:
        """Initialize core processing components."""
        try:
            from gesturecam.core.pipeline import GestureCamPipeline  # avoid circular import
            from gesturecam.config import Config
            
            config = Config()
            config.CAMERA_INDEX = self.settings.camera.device_index
            config.ZOOM_SMOOTHING = self.settings.zoom.smoothing
            config.FRAMING_SMOOTHING = self.settings.framing.smoothing
            config.MAX_ZOOM = self.settings.zoom.max_zoom
            config.HAND_DETECTION_CONFIDENCE = self.settings.gestures.detection_confidence
            
            # self._pipeline = GestureCamPipeline(config)  # not started yet
            
            logger.info("Core components initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    def start(self) -> bool:
        """Start the camera and processing pipeline."""
        if self.state not in [AppState.READY, AppState.PAUSED]:
            logger.warning(f"Cannot start from state: {self.state}")
            return False
        
        try:
            self._set_state(AppState.RUNNING)
            self.virtual_cam_active = True
            logger.info("Virtual camera started")
            return True
        except Exception as e:
            logger.error(f"Failed to start: {e}")
            self._set_state(AppState.ERROR)
            return False
    
    def stop(self) -> None:
        """Stop the camera and processing pipeline."""
        self.virtual_cam_active = False
        self._set_state(AppState.PAUSED)
        logger.info("Virtual camera stopped")
    
    def shutdown(self) -> None:
        """Clean shutdown of all components."""
        self._set_state(AppState.SHUTDOWN)
        self.virtual_cam_active = False
        if self._pipeline:
            self._pipeline.cleanup()
        self.settings.save()
        logger.info("Application shutdown complete")
    
    # === Onboarding ===
    
    def complete_onboarding_step(self) -> bool:
        """
        Advance to next onboarding step.
        Returns True if onboarding is complete.
        """
        if self.state != AppState.ONBOARDING:
            return False
        
        self.onboarding_step += 1
        
        if self.onboarding_step > self.total_onboarding_steps:
            self.settings.mark_first_run_complete()
            self._initialize_components()
            self._set_state(AppState.READY)
            return True
        
        self._notify_state_change()
        return False
    
    def go_back_onboarding(self) -> bool:
        """Go back to previous onboarding step."""
        if self.state != AppState.ONBOARDING or self.onboarding_step <= 1:
            return False
        
        self.onboarding_step -= 1
        self._notify_state_change()
        return True
    
    # === Mode Control ===
    
    def set_framing_mode(self, mode: str) -> bool:
        """Change the framing mode."""
        if mode not in FRAMING_MODES:
            logger.warning(f"Invalid framing mode: {mode}")
            return False
        
        self.current_mode = mode
        logger.info(f"Framing mode changed to: {mode}")
        
        if self._on_mode_change:
            self._on_mode_change(mode)
        
        return True
    
    def get_framing_modes(self) -> list:
        """Get list of available framing modes with translations."""
        return [
            {
                "id": mode_id,
                "name": t(f"modes.{mode_id}"),
                "description": t(f"modes.{mode_id}_desc"),
                "icon": info["icon"],
                "active": mode_id == self.current_mode,
            }
            for mode_id, info in FRAMING_MODES.items()
        ]
    
    # === Zoom Control ===
    
    def set_zoom(self, level: float) -> None:
        """Set target zoom level."""
        min_zoom = self.settings.zoom.min_zoom
        max_zoom = self.settings.zoom.max_zoom
        
        self.zoom_status.target_level = max(min_zoom, min(max_zoom, level))
        
        if self._on_zoom_update:
            self._on_zoom_update(self.zoom_status)
    
    def reset_zoom(self) -> None:
        """Reset zoom to 1.0x."""
        self.set_zoom(1.0)
    
    def zoom_in(self, amount: float = 0.1) -> None:
        """Increase zoom by amount."""
        self.set_zoom(self.zoom_status.target_level + amount)
    
    def zoom_out(self, amount: float = 0.1) -> None:
        """Decrease zoom by amount."""
        self.set_zoom(self.zoom_status.target_level - amount)
    
    # === Virtual Camera ===
    
    def toggle_virtual_camera(self) -> bool:
        """Toggle virtual camera on/off."""
        if self.virtual_cam_active:
            self.stop()
            return False
        else:
            return self.start()
    
    def is_virtual_camera_active(self) -> bool:
        """Check if virtual camera is active."""
        return self.virtual_cam_active
    
    # === Settings ===
    
    def get_available_cameras(self) -> list:
        """Get list of available cameras."""
        # TODO: Implement actual camera enumeration
        return [
            {"index": 0, "name": "MacBook Pro Camera"},
            {"index": 1, "name": "iPhone Continuity Camera"},
        ]
    
    def update_settings(self, **kwargs) -> None:
        """Update settings and save."""
        for key, value in kwargs.items():
            if hasattr(self.settings.settings, key):
                setattr(self.settings.settings, key, value)
        
        self.settings.save()
    
    # === UI Callbacks ===
    
    def on_state_change(self, callback: Callable) -> None:
        """Register callback for state changes."""
        self._on_state_change = callback
    
    def on_camera_update(self, callback: Callable) -> None:
        """Register callback for camera status updates."""
        self._on_camera_update = callback
    
    def on_gesture_update(self, callback: Callable) -> None:
        """Register callback for gesture detection updates."""
        self._on_gesture_update = callback
    
    def on_zoom_update(self, callback: Callable) -> None:
        """Register callback for zoom level updates."""
        self._on_zoom_update = callback
    
    def on_mode_change(self, callback: Callable) -> None:
        """Register callback for framing mode changes."""
        self._on_mode_change = callback
    
    # === Internal Methods ===
    
    def _set_state(self, state: AppState) -> None:
        """Update application state and notify listeners."""
        old_state = self.state
        self.state = state
        logger.debug(f"State changed: {old_state} -> {state}")
        self._notify_state_change()
    
    def _notify_state_change(self) -> None:
        """Notify UI of state change."""
        if self._on_state_change:
            self._on_state_change(self.state, self.onboarding_step)
    
    # === Status Getters ===
    
    def get_status_text(self) -> str:
        """Get current status as displayable text."""
        if self.state == AppState.RUNNING:
            return t("dashboard.status.active")
        elif self.state == AppState.PAUSED:
            return t("dashboard.status.paused")
        elif self.state == AppState.ERROR:
            return t("dashboard.status.error")
        elif not self.camera_status.connected:
            return t("dashboard.status.no_camera")
        return ""
    
    def get_gesture_display(self) -> dict:
        """Get current gesture info for display."""
        action = self.gesture_status.action
        return {
            "action": action,
            "text": t(f"gestures.{action}") if action != "none" else t("gestures.none"),
            "icon": GESTURES.get(self.gesture_status.detected_gesture, {}).get("icon", ""),
        }
    
    def get_zoom_display(self) -> str:
        """Get zoom level formatted for display."""
        return t("dashboard.zoom_level", level=f"{self.zoom_status.current_level:.1f}")
    
    def get_mode_display(self) -> str:
        """Get current mode formatted for display."""
        return t("dashboard.mode", mode=t(f"modes.{self.current_mode}"))


# Global controller instance (singleton)
_controller: Optional[AppController] = None


def get_controller() -> AppController:
    """Get the global app controller instance."""
    global _controller
    if _controller is None:
        _controller = AppController()
    return _controller
