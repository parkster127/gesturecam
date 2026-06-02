"""
GestureCam JavaScript API Bridge
Exposes Python functions to JavaScript in the WebView.
"""

import logging

from gesturecam.app import get_controller
from gesturecam.constants import APP_VERSION, GESTURES
from gesturecam.i18n import get_i18n, set_language, t
from gesturecam.settings import get_settings

logger = logging.getLogger(__name__)


class GestureCamAPI:
    """
    Python API exposed to JavaScript via PyWebView.
    All methods here can be called from JS: pywebview.api.method_name()
    """

    def __init__(self, window=None):
        self._window = window
        self._controller = get_controller()
        self._settings = get_settings()
        logger.info("GestureCam API initialized")

    def set_window(self, window):
        """Set the webview window reference."""
        self._window = window

    # === App Lifecycle ===

    def initialize(self) -> dict:
        """
        Initialize the application.
        Called when the UI first loads.
        """
        success = self._controller.initialize()
        return {
            "success": success,
            "state": self._controller.state.value,
            "firstRun": self._settings.settings.first_run,
            "version": APP_VERSION,
        }

    def get_app_state(self) -> dict:
        """Get current application state."""
        return {
            "state": self._controller.state.value,
            "onboardingStep": self._controller.onboarding_step,
            "totalOnboardingSteps": self._controller.total_onboarding_steps,
            "virtualCameraActive": self._controller.virtual_cam_active,
            "currentMode": self._controller.current_mode,
        }

    # === Onboarding ===

    def complete_onboarding_step(self) -> dict:
        """Advance to next onboarding step."""
        is_complete = self._controller.complete_onboarding_step()
        return {
            "complete": is_complete,
            "currentStep": self._controller.onboarding_step,
            "state": self._controller.state.value,
        }

    def go_back_onboarding(self) -> dict:
        """Go back in onboarding."""
        success = self._controller.go_back_onboarding()
        return {
            "success": success,
            "currentStep": self._controller.onboarding_step,
        }

    # === Framing Modes ===

    def get_framing_modes(self) -> list:
        """Get all framing modes with translations."""
        return self._controller.get_framing_modes()

    def set_framing_mode(self, mode: str) -> dict:
        """Set the active framing mode."""
        success = self._controller.set_framing_mode(mode)
        return {
            "success": success,
            "currentMode": self._controller.current_mode,
        }

    # === Zoom Control ===

    def get_zoom_level(self) -> dict:
        """Get current zoom status."""
        return {
            "current": self._controller.zoom_status.current_level,
            "target": self._controller.zoom_status.target_level,
            "min": self._settings.zoom.min_zoom,
            "max": self._settings.zoom.max_zoom,
        }

    def set_zoom(self, level: float) -> dict:
        """Set target zoom level."""
        self._controller.set_zoom(level)
        return self.get_zoom_level()

    def reset_zoom(self) -> dict:
        """Reset zoom to 1.0."""
        self._controller.reset_zoom()
        return self.get_zoom_level()

    def zoom_in(self) -> dict:
        """Zoom in by default amount."""
        self._controller.zoom_in(0.2)
        return self.get_zoom_level()

    def zoom_out(self) -> dict:
        """Zoom out by default amount."""
        self._controller.zoom_out(0.2)
        return self.get_zoom_level()

    # === Virtual Camera ===

    def toggle_virtual_camera(self) -> dict:
        """Toggle virtual camera on/off."""
        is_active = self._controller.toggle_virtual_camera()
        return {
            "active": is_active,
            "state": self._controller.state.value,
        }

    def start_virtual_camera(self) -> dict:
        """Start the virtual camera."""
        success = self._controller.start()
        return {
            "success": success,
            "active": self._controller.virtual_cam_active,
        }

    def stop_virtual_camera(self) -> dict:
        """Stop the virtual camera."""
        self._controller.stop()
        return {
            "active": False,
        }

    # === Gesture Status ===

    def get_gesture_status(self) -> dict:
        """Get current gesture detection status."""
        return {
            "action": self._controller.gesture_status.action,
            "gesture": self._controller.gesture_status.detected_gesture,
            "confidence": self._controller.gesture_status.confidence,
            "handsDetected": self._controller.gesture_status.hands_detected,
        }

    def get_gestures(self) -> dict:
        """Get all available gestures."""
        return GESTURES

    # === Camera ===

    def _detect_real_cameras(self) -> list:
        """
        Detect real cameras connected to the system using OpenCV.
        Returns list of available camera devices.
        """
        cameras = []

        try:
            # On macOS, try to get camera names via system APIs
            import platform

            import cv2

            if platform.system() == "Darwin":
                # macOS-specific camera detection
                try:
                    import subprocess

                    result = subprocess.run(
                        ["system_profiler", "SPCameraDataType", "-json"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        import json

                        data = json.loads(result.stdout)
                        camera_data = data.get("SPCameraDataType", [])
                        for idx, cam in enumerate(camera_data):
                            cameras.append(
                                {
                                    "index": idx,
                                    "name": cam.get("_name", f"Camera {idx}"),
                                    "model": cam.get("spcamera_model-id", "Unknown"),
                                    "unique_id": cam.get("spcamera_unique-id", ""),
                                }
                            )
                except Exception as e:
                    logger.debug(f"macOS camera detection failed: {e}")

            # Fallback: probe camera indices with OpenCV
            if not cameras:
                for idx in range(5):  # Check first 5 indices
                    cap = cv2.VideoCapture(idx)
                    if cap.isOpened():
                        # Get camera properties
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30

                        cameras.append(
                            {
                                "index": idx,
                                "name": f"Camera {idx}" if idx > 0 else "Built-in Camera",
                                "resolution": f"{width}x{height}",
                                "fps": fps,
                            }
                        )
                        cap.release()
                    else:
                        break  # No more cameras

        except ImportError:
            logger.warning("OpenCV not available for camera detection")
        except Exception as e:
            logger.error(f"Camera detection failed: {e}")

        # Always return at least a placeholder if no cameras found
        if not cameras:
            cameras = [{"index": 0, "name": "No camera detected", "resolution": "N/A"}]

        return cameras

    def get_available_cameras(self) -> list:
        """Get list of available cameras (real detection)."""
        return self._detect_real_cameras()

    def get_camera_status(self) -> dict:
        """Get current camera status."""
        return {
            "connected": self._controller.camera_status.connected,
            "deviceName": self._controller.camera_status.device_name,
            "resolution": self._controller.camera_status.resolution,
            "fps": self._controller.camera_status.fps,
            "latencyMs": self._controller.camera_status.latency_ms,
        }

    def get_resolutions(self) -> list:
        """Get available resolution presets."""
        return [
            {"id": "720p", "label": "720p (HD)", "width": 1280, "height": 720},
            {"id": "1080p", "label": "1080p (Full HD)", "width": 1920, "height": 1080},
            {"id": "1440p", "label": "1440p (2K)", "width": 2560, "height": 1440},
            {"id": "4k", "label": "4K (Ultra HD)", "width": 3840, "height": 2160},
        ]

    def select_camera(self, index: int) -> dict:
        """Select a camera by index."""
        self._settings.settings.camera.device_index = index
        self._settings.save()
        logger.info(f"Camera selected: index {index}")
        return {"success": True, "selectedIndex": index}

    # === Settings ===

    def get_settings(self) -> dict:
        """Get all settings."""
        s = self._settings.settings
        return {
            "camera": {
                "deviceIndex": s.camera.device_index,
                "deviceName": s.camera.device_name,
                "resolution": s.camera.resolution,
                "fps": s.camera.fps,
                "mirror": s.camera.mirror,
            },
            "zoom": {
                "minZoom": s.zoom.min_zoom,
                "maxZoom": s.zoom.max_zoom,
                "smoothing": s.zoom.smoothing,
                "defaultZoom": s.zoom.default_zoom,
            },
            "framing": {
                "defaultMode": s.framing.default_mode,
                "smoothing": s.framing.smoothing,
                "facePadding": s.framing.face_padding,
            },
            "gestures": {
                "enabled": s.gestures.enabled,
                "twoHandEnabled": s.gestures.two_hand_enabled,
                "detectionConfidence": s.gestures.detection_confidence,
                "showOverlay": s.gestures.show_overlay,
            },
            "output": {
                "enabled": s.output.enabled,
                "backend": s.output.backend,
                "deviceName": s.output.device_name,
            },
            "ui": {
                "language": s.ui.language,
                "theme": s.ui.theme,
                "startMinimized": s.ui.start_minimized,
                "startWithSystem": s.ui.start_with_system,
                "minimizeToTray": s.ui.minimize_to_tray,
            },
        }

    def update_settings(self, section: str, key: str, value) -> dict:
        """Update a specific setting."""
        try:
            settings_obj = self._settings.settings
            section_obj = getattr(settings_obj, section, None)
            if section_obj and hasattr(section_obj, key):
                setattr(section_obj, key, value)
                self._settings.save()
                logger.info(f"Setting updated: {section}.{key} = {value}")
                return {"success": True}
            return {"success": False, "error": "Invalid setting path"}
        except Exception as e:
            logger.error(f"Failed to update setting: {e}")
            return {"success": False, "error": str(e)}

    def reset_settings(self) -> dict:
        """Reset all settings to defaults."""
        self._settings.reset()
        return {"success": True}

    def save_settings(self) -> dict:
        """Save current settings."""
        self._settings.save()
        return {"success": True}

    # === i18n ===

    def get_translations(self) -> dict:
        """Get all translations for current language."""
        i18n = get_i18n()
        return i18n.translations if i18n.translations else i18n.fallback

    def translate(self, key: str, **kwargs) -> str:
        """Translate a single key."""
        return t(key, **kwargs)

    def set_language(self, lang: str) -> dict:
        """Change application language."""
        set_language(lang)
        self._settings.settings.ui.language = lang
        self._settings.save()
        return {"success": True, "language": lang}

    def get_available_languages(self) -> dict:
        """Get available languages."""
        return get_i18n().get_available_languages()

    # === Window Control ===

    def minimize_window(self):
        """Minimize the window."""
        if self._window:
            self._window.minimize()

    def close_window(self):
        """Close the application."""
        if self._window:
            self._window.destroy()

    def navigate_to(self, screen: str) -> dict:
        """
        Navigate to a different screen.
        Used for loading different HTML pages.
        """
        screens = {
            "onboarding_step1": "onboarding_step1_privacy.html",
            "onboarding_step2": "onboarding_step2_camera.html",
            "onboarding_step3": "onboarding_step3_gestures.html",
            "dashboard": "main_dashboard.html",
            "settings": "settings_panel.html",
        }

        if screen not in screens:
            return {"success": False, "error": "Unknown screen"}

        if self._window:
            # Load the new HTML file
            html_file = screens[screen]
            # This will be handled by the window manager
            return {"success": True, "screen": screen, "file": html_file}

        return {"success": False, "error": "No window reference"}
