"""
GestureCam Internationalization (i18n) System
Provides translation support for multiple languages.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Default language
DEFAULT_LANGUAGE = "en"

# Supported languages
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Español",
    # Future: Add more languages
    # "fr": "Français",
    # "de": "Deutsch",
    # "pt": "Português",
    # "ja": "日本語",
    # "zh": "中文",
}


class I18n:
    """
    Internationalization manager.
    Loads and provides access to translated strings.
    """

    def __init__(self, language: str = DEFAULT_LANGUAGE):
        self.language = language
        self.translations: dict = {}
        self.fallback: dict = {}
        self._load_translations()

    def _get_translations_dir(self) -> Path:
        """Get the directory containing translation files."""
        return Path(__file__).parent / "locales"

    def _load_translations(self) -> None:
        """Load translation files."""
        translations_dir = self._get_translations_dir()

        # Always load English as fallback
        fallback_path = translations_dir / "en.json"
        if fallback_path.exists():
            with open(fallback_path, encoding="utf-8") as f:
                self.fallback = json.load(f)
        else:
            # Use embedded English translations
            self.fallback = ENGLISH_TRANSLATIONS

        # Load requested language
        if self.language != "en":
            lang_path = translations_dir / f"{self.language}.json"
            if lang_path.exists():
                with open(lang_path, encoding="utf-8") as f:
                    self.translations = json.load(f)
                logger.info(f"Loaded translations for: {self.language}")
            else:
                logger.warning(f"Translations not found for: {self.language}. Using English.")
                self.translations = {}
        else:
            self.translations = self.fallback

    def set_language(self, language: str) -> None:
        """Change the current language."""
        if language in SUPPORTED_LANGUAGES:
            self.language = language
            self._load_translations()
        else:
            logger.warning(f"Unsupported language: {language}")

    def t(self, key: str, **kwargs) -> str:
        """
        Get translated string by key.
        Supports nested keys with dot notation: "settings.camera.title"
        Supports variable interpolation: t("hello", name="World") -> "Hello, World!"

        Args:
            key: Translation key (supports dot notation for nested keys)
            **kwargs: Variables to interpolate into the string

        Returns:
            Translated string, or the key itself if not found
        """
        # Try current language first
        value = self._get_nested(self.translations, key)

        # Fall back to English
        if value is None:
            value = self._get_nested(self.fallback, key)

        # If still not found, return the key
        if value is None:
            logger.warning(f"Translation not found: {key}")
            return key

        # Interpolate variables
        if kwargs:
            try:
                value = value.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Missing interpolation variable in '{key}': {e}")

        return value

    def _get_nested(self, data: dict, key: str) -> str | None:
        """Get a nested value from a dictionary using dot notation."""
        keys = key.split(".")
        current = data

        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return None

        return current if isinstance(current, str) else None

    def get_language_name(self, code: str = None) -> str:
        """Get the display name for a language code."""
        code = code or self.language
        return SUPPORTED_LANGUAGES.get(code, code)

    def get_available_languages(self) -> dict:
        """Get all available languages."""
        return SUPPORTED_LANGUAGES.copy()


# Embedded English translations (always available, no file needed)
ENGLISH_TRANSLATIONS = {
    "app": {
        "name": "GestureCam",
        "tagline": "Control your camera with a simple 👍",
        "version": "Version {version}",
    },
    "common": {
        "save": "Save",
        "cancel": "Cancel",
        "reset": "Reset",
        "close": "Close",
        "back": "Back",
        "next": "Next",
        "done": "Done",
        "enable": "Enable",
        "disable": "Disable",
        "on": "On",
        "off": "Off",
        "yes": "Yes",
        "no": "No",
        "ok": "OK",
        "error": "Error",
        "warning": "Warning",
        "info": "Info",
        "success": "Success",
        "loading": "Loading...",
        "retry": "Retry",
    },
    "menu": {
        "file": "File",
        "edit": "Edit",
        "view": "View",
        "help": "Help",
        "settings": "Settings",
        "quit": "Quit",
        "about": "About GestureCam",
        "check_updates": "Check for Updates",
        "documentation": "Documentation",
        "report_bug": "Report a Bug",
    },
    "dashboard": {
        "title": "GestureCam",
        "preview": "Camera Preview",
        "zoom_level": "Zoom: {level}x",
        "mode": "Mode: {mode}",
        "gesture": "Gesture: {gesture}",
        "status": {
            "active": "Active",
            "paused": "Paused",
            "error": "Error",
            "no_camera": "No Camera",
        },
        "start_camera": "Start Virtual Camera",
        "stop_camera": "Stop Virtual Camera",
    },
    "modes": {
        "manual": "Manual",
        "face_follow": "Face Follow",
        "headshot": "Headshot",
        "shirt_up": "Shirt-Up",
        "manual_desc": "No automatic tracking. Full manual control.",
        "face_follow_desc": "Camera smoothly follows your face.",
        "headshot_desc": "Professional head framing for interviews.",
        "shirt_up_desc": "Shows from chest up. Great for presentations.",
    },
    "gestures": {
        "title": "Gesture Control",
        "guide_title": "Gesture Control Guide",
        "zoom_in": "Zoom In",
        "zoom_out": "Zoom Out",
        "zoom_in_fast": "Zoom In Fast",
        "zoom_out_fast": "Zoom Out Fast",
        "hold": "Hold/Pause",
        "neutral": "Neutral",
        "none": "None detected",
        "tips_title": "Tips for Best Performance",
        "tip_lighting": "Ensure good, even lighting in your environment for accurate gesture detection.",
        "tip_visible": "Keep your hands clearly visible within the camera's frame and avoid rapid movements.",
        "tip_practice": "Practice each gesture a few times to get comfortable with the detection.",
    },
    "settings": {
        "title": "Settings",
        "camera": {
            "title": "Camera",
            "device": "Camera Selection",
            "device_desc": "Select the webcam to use",
            "resolution": "Resolution",
            "resolution_desc": "Video resolution for capture",
            "fps": "Frame Rate (FPS)",
            "mirror": "Mirror Image",
            "mirror_desc": "Flip video horizontally (selfie mode)",
        },
        "zoom": {
            "title": "Zoom",
            "max_zoom": "Maximum Zoom",
            "max_zoom_desc": "Maximum zoom level (1.0x - 5.0x)",
            "smoothing": "Smoothing",
            "smoothing_desc": "How smoothly the zoom transitions (0 = instant, 1 = very slow)",
        },
        "framing": {
            "title": "Framing",
            "default_mode": "Default Mode",
            "default_mode_desc": "Framing mode to use when app starts",
            "smoothing": "Tracking Smoothness",
            "smoothing_desc": "How smoothly the camera follows your face",
        },
        "gestures": {
            "title": "Gestures",
            "enabled": "Enable Gestures",
            "enabled_desc": "Control zoom with hand gestures",
            "two_hand": "Two-Hand Control",
            "two_hand_desc": "Use distance between two hands for zoom",
            "show_overlay": "Show Detection Overlay",
            "show_overlay_desc": "Display hand landmarks on preview",
            "sensitivity": "Sensitivity",
            "sensitivity_desc": "How responsive gesture detection should be",
        },
        "output": {
            "title": "Output",
            "backend": "Virtual Camera Backend",
            "backend_desc": "Technology used for virtual camera",
            "device_name": "Device Name",
            "device_name_desc": "Name shown in other applications",
        },
        "general": {
            "title": "General",
            "language": "Language",
            "language_desc": "Application language",
            "theme": "Theme",
            "theme_desc": "Color scheme for the interface",
            "theme_dark": "Dark",
            "theme_light": "Light",
            "theme_system": "System",
            "start_minimized": "Start Minimized",
            "start_minimized_desc": "Start app in system tray",
            "start_with_system": "Start with System",
            "start_with_system_desc": "Launch when you log in",
            "minimize_to_tray": "Minimize to Tray",
            "minimize_to_tray_desc": "Keep running when window is closed",
        },
        "reset_defaults": "Reset to Defaults",
        "reset_confirm": "Are you sure you want to reset all settings to their default values?",
    },
    "onboarding": {
        "welcome": {
            "title": "Control your camera with a simple 👍",
            "subtitle": "Zoom, pan, and auto-frame your webcam using hand gestures. No expensive hardware needed.",
            "get_started": "Get Started",
        },
        "camera_permission": {
            "title": "Camera Access",
            "subtitle": "GestureCam needs access to your camera to apply zoom and tracking effects.",
            "privacy_note": "🔒 Everything is processed locally. We never send video data to the internet.",
            "grant_access": "Grant Camera Access",
        },
        "select_camera": {
            "title": "Select Your Camera",
            "subtitle": "Choose the webcam you want to use with GestureCam.",
            "no_cameras": "No cameras detected. Please connect a webcam.",
        },
        "ready": {
            "title": "You're All Set! 🎉",
            "subtitle": "GestureCam is ready to use. Try these gestures to control your camera:",
            "start_using": "Start Using GestureCam",
        },
        "step_indicator": "Step {current} of {total}",
    },
    "tray": {
        "show": "Show GestureCam",
        "hide": "Hide",
        "toggle_camera": "Toggle Virtual Camera",
        "quit": "Quit",
    },
    "errors": {
        "camera_not_found": "Camera not found. Please check your connection.",
        "camera_in_use": "Camera is in use by another application.",
        "virtual_cam_failed": "Failed to start virtual camera. Please check if OBS Virtual Camera is installed.",
        "gesture_model_failed": "Failed to load gesture recognition model.",
        "settings_save_failed": "Failed to save settings.",
        "unknown": "An unexpected error occurred.",
    },
    "about": {
        "title": "About GestureCam",
        "description": "Virtual camera with gesture control for zoom and auto-framing.",
        "version": "Version {version}",
        "copyright": "© 2026 Vectores. Open Source under MIT License.",
        "website": "Website",
        "github": "GitHub",
        "made_with": "Made with ❤️ by Vectores",
    },
}


# Global i18n instance (singleton)
_i18n: I18n | None = None


def get_i18n() -> I18n:
    """Get the global i18n instance."""
    global _i18n
    if _i18n is None:
        _i18n = I18n()
    return _i18n


def t(key: str, **kwargs) -> str:
    """
    Shortcut for getting translated strings.

    Usage:
        from gesturecam.i18n import t
        print(t("dashboard.title"))
        print(t("dashboard.zoom_level", level=1.5))
    """
    return get_i18n().t(key, **kwargs)


def set_language(language: str) -> None:
    """Change the application language."""
    get_i18n().set_language(language)
