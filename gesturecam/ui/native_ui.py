"""
GestureCam Native UI - Clean Dashboard
Minimal dark design with gesture controls
"""

import logging
import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum

import cv2
import dearpygui.dearpygui as dpg
import numpy as np

from gesturecam.ui.theme import (
    PRIMARY,
    SUCCESS,
    TEXT_MUTED,
    create_ghost_button_theme,
    create_mode_button_theme,
    create_primary_button_theme,
    create_processed_video_theme,
    create_video_container_theme,
    setup_main_theme,
)

logger = logging.getLogger(__name__)


class FramingMode(Enum):
    MANUAL = "manual"
    FACE_FOLLOW = "face_follow"
    HEADSHOT = "headshot"
    SHIRT_UP = "shirt_up"


@dataclass
class UIState:
    """Current UI state"""

    zoom_level: float = 1.0
    framing_mode: FramingMode = FramingMode.FACE_FOLLOW
    is_mirrored: bool = True
    show_overlay: bool = True
    virtual_camera_active: bool = False
    gestures_paused: bool = False  # Pause gesture detection
    current_gesture: str = "None"
    camera_name: str = "Detecting..."
    latency_ms: float = 0.0


class NativeUI:
    """
    Native Dear PyGui interface for GestureCam.
    Redesigned with centered layout matching HTML dashboard.
    """

    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 720
    VIDEO_WIDTH = 480
    VIDEO_HEIGHT = 270  # 16:9 aspect ratio

    def __init__(self, controller=None):
        self.controller = controller
        self.state = UIState()
        self.running = False

        # Frame buffers
        self.original_frame: np.ndarray | None = None
        self.processed_frame: np.ndarray | None = None
        self._frame_lock = threading.Lock()

        # Callbacks
        self.on_mode_change: Callable | None = None
        self.on_mirror_toggle: Callable | None = None
        self.on_virtual_camera_toggle: Callable | None = None
        self.on_settings_open: Callable | None = None

        # Texture IDs
        self._original_texture = None
        self._processed_texture = None

        # Theme cache
        self._mode_button_themes = {}

    def setup(self):
        """Initialize Dear PyGui context and create window"""
        dpg.create_context()

        # Create textures for video display
        with dpg.texture_registry():
            blank = np.zeros((self.VIDEO_HEIGHT, self.VIDEO_WIDTH, 4), dtype=np.float32)
            self._original_texture = dpg.add_raw_texture(
                self.VIDEO_WIDTH, self.VIDEO_HEIGHT, blank, format=dpg.mvFormat_Float_rgba
            )
            self._processed_texture = dpg.add_raw_texture(
                self.VIDEO_WIDTH, self.VIDEO_HEIGHT, blank, format=dpg.mvFormat_Float_rgba
            )

        # Create themes
        self._video_theme = create_video_container_theme()
        self._processed_theme = create_processed_video_theme()

        # Main window
        with dpg.window(
            label="GestureCam",
            tag="main_window",
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            no_title_bar=False,
            no_resize=False,
        ):

            # Calculate centering spacers
            content_width = (self.VIDEO_WIDTH + 16) * 2 + 40  # 2 videos + gap
            h_spacer = max(10, (self.WINDOW_WIDTH - content_width) // 2)

            # Header bar - just title
            with dpg.child_window(height=40, border=False, tag="header"):
                dpg.add_text("GestureCam", color=PRIMARY)

            # Vertical spacer to center content
            v_spacer = max(10, (self.WINDOW_HEIGHT - 40 - (self.VIDEO_HEIGHT + 36) - 200) // 2)
            dpg.add_spacer(height=v_spacer)

            # === MAIN CONTENT - CENTERED ===
            with dpg.group(horizontal=True):
                # Left spacer for horizontal centering
                dpg.add_spacer(width=h_spacer)

                # Center content
                with dpg.group():
                    # Video row - centered with gap
                    with dpg.group(horizontal=True):
                        # Original Video Container
                        with dpg.child_window(
                            width=self.VIDEO_WIDTH + 16,
                            height=self.VIDEO_HEIGHT + 36,
                            tag="original_container",
                        ):
                            dpg.bind_item_theme("original_container", self._video_theme)
                            dpg.add_text("ORIGINAL", color=TEXT_MUTED)
                            dpg.add_spacer(height=4)
                            dpg.add_image(self._original_texture)

                        # Gap between videos
                        dpg.add_spacer(width=40)

                        # Processed Video Container
                        with dpg.child_window(
                            width=self.VIDEO_WIDTH + 16,
                            height=self.VIDEO_HEIGHT + 36,
                            tag="processed_container",
                        ):
                            dpg.bind_item_theme("processed_container", self._processed_theme)
                            with dpg.group(horizontal=True):
                                dpg.add_text("PROCESSED", color=PRIMARY)
                                dpg.add_spacer(width=20)
                                dpg.add_text("", tag="zoom_display", color=PRIMARY)
                            dpg.add_spacer(height=4)
                            dpg.add_image(self._processed_texture)

                    dpg.add_spacer(height=20)

                    # === QUICK CONTROLS ===
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="<-> Mirror",
                            tag="mirror_btn",
                            callback=self._toggle_mirror,
                            width=100,
                            height=36,
                        )
                        dpg.add_spacer(width=10)
                        dpg.add_button(
                            label="[O] Overlay",
                            tag="overlay_btn",
                            callback=self._toggle_overlay,
                            width=100,
                            height=36,
                        )
                        dpg.add_spacer(width=10)
                        dpg.add_button(
                            label="[P] Pause",
                            tag="pause_btn",
                            callback=self._toggle_pause,
                            width=100,
                            height=36,
                        )
                        dpg.add_spacer(width=30)
                        dpg.add_text("Gesture:", color=TEXT_MUTED)
                        dpg.add_text("", tag="gesture_display", color=SUCCESS)

                    dpg.add_spacer(height=16)

                    # === FRAMING MODES ===
                    dpg.add_text("Framing Modes", color=TEXT_MUTED)
                    dpg.add_spacer(height=8)

                    with dpg.group(horizontal=True):
                        for mode_value, label in [
                            (FramingMode.MANUAL, "Manual"),
                            (FramingMode.FACE_FOLLOW, "Face Follow"),
                            (FramingMode.HEADSHOT, "Headshot"),
                            (FramingMode.SHIRT_UP, "Shirt-Up"),
                        ]:
                            tag = f"btn_{mode_value.value}"
                            dpg.add_button(
                                label=label,
                                tag=tag,
                                callback=lambda s, a, m=mode_value: self._set_mode(m),
                                width=120,
                                height=40,
                            )
                            dpg.add_spacer(width=10)

                    dpg.add_spacer(height=16)

                    # === ZOOM SLIDER ===
                    with dpg.group(horizontal=True):
                        dpg.add_text("Zoom:", color=TEXT_MUTED)
                        dpg.add_spacer(width=10)
                        dpg.add_slider_float(
                            label="",
                            tag="zoom_slider",
                            default_value=1.0,
                            min_value=1.0,
                            max_value=3.0,
                            callback=self._on_zoom_change,
                            width=300,
                        )
                        dpg.add_spacer(width=10)
                        dpg.add_text("1.0x", tag="zoom_value")

                    dpg.add_spacer(height=20)

                    # === STATUS BAR ===
                    with dpg.group(horizontal=True):
                        dpg.add_text("*", tag="status_dot", color=(100, 100, 100))
                        dpg.add_text("", tag="camera_status")
                        dpg.add_spacer(width=30)
                        dpg.add_text("Latency:", color=TEXT_MUTED)
                        dpg.add_text("", tag="latency_display")
                        dpg.add_spacer(width=50)
                        dpg.add_button(
                            label="Settings", callback=self._on_settings_click, width=90, height=36
                        )
                        dpg.add_spacer(width=10)
                        dpg.add_button(
                            label="Start Virtual Camera",
                            callback=self._on_virtual_camera_click,
                            tag="virtual_camera_btn",
                            width=150,
                            height=36,
                        )

                # Right spacer
                dpg.add_spacer(width=20)

        # Apply theme
        setup_main_theme()

        # Setup viewport
        dpg.create_viewport(title="GestureCam", width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)
        dpg.setup_dearpygui()
        dpg.set_primary_window("main_window", True)

        # Update mode buttons
        self._update_mode_buttons()

        logger.info("Native UI initialized (redesigned)")

    def update_frame(self, original: np.ndarray, processed: np.ndarray):
        """Update video frames (called from video thread)"""
        with self._frame_lock:
            self.original_frame = original.copy()
            self.processed_frame = processed.copy()

    def update_state(
        self,
        gesture: str = None,
        zoom: float = None,
        camera_name: str = None,
        latency: float = None,
    ):
        """Update UI state values"""
        if gesture is not None:
            self.state.current_gesture = gesture
        if zoom is not None:
            self.state.zoom_level = zoom
        if camera_name is not None:
            self.state.camera_name = camera_name
        if latency is not None:
            self.state.latency_ms = latency

    def _render_frame(self):
        """Convert and display frames in textures"""
        with self._frame_lock:
            if self.original_frame is not None:
                frame = cv2.resize(self.original_frame, (self.VIDEO_WIDTH, self.VIDEO_HEIGHT))
                if self.state.is_mirrored:
                    frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                frame = frame.astype(np.float32) / 255.0
                dpg.set_value(self._original_texture, frame.flatten())

            if self.processed_frame is not None:
                frame = cv2.resize(self.processed_frame, (self.VIDEO_WIDTH, self.VIDEO_HEIGHT))
                if self.state.is_mirrored:
                    frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                frame = frame.astype(np.float32) / 255.0
                dpg.set_value(self._processed_texture, frame.flatten())

        # Update text displays
        dpg.set_value("gesture_display", self.state.current_gesture)
        dpg.set_value("zoom_display", f"{self.state.zoom_level:.1f}x")
        dpg.set_value("camera_status", f"Camera: {self.state.camera_name}")
        dpg.set_value("latency_display", f"{self.state.latency_ms:.0f}ms")

        # Sync zoom slider with current zoom level (bidirectional)
        if dpg.does_item_exist("zoom_slider"):
            current_slider = dpg.get_value("zoom_slider")
            # Only update if significantly different (to avoid loop)
            if abs(current_slider - self.state.zoom_level) > 0.05:
                dpg.set_value("zoom_slider", self.state.zoom_level)
                dpg.set_value("zoom_value", f"{self.state.zoom_level:.1f}x")

        # Update status dot
        if self.state.camera_name != "Detecting...":
            dpg.configure_item("status_dot", color=SUCCESS)

    def _set_mode(self, mode: FramingMode):
        """Set framing mode"""
        self.state.framing_mode = mode
        self._update_mode_buttons()
        if self.on_mode_change:
            self.on_mode_change(mode.value)

    def _update_mode_buttons(self):
        """Update button themes based on active mode"""
        for mode in FramingMode:
            tag = f"btn_{mode.value}"
            is_active = mode == self.state.framing_mode
            theme = create_mode_button_theme(active=is_active)
            dpg.bind_item_theme(tag, theme)

    def _toggle_mirror(self):
        self.state.is_mirrored = not self.state.is_mirrored
        label = "<-> ON" if self.state.is_mirrored else "<-> Mirror"
        dpg.set_item_label("mirror_btn", label)
        if self.on_mirror_toggle:
            self.on_mirror_toggle(self.state.is_mirrored)

    def _toggle_overlay(self):
        self.state.show_overlay = not self.state.show_overlay
        label = "[O] ON" if self.state.show_overlay else "[O] Overlay"
        dpg.set_item_label("overlay_btn", label)

    def _toggle_pause(self):
        """Toggle gesture detection pause"""
        logger.info(f"Toggle pause called, current: {self.state.gestures_paused}")
        self.state.gestures_paused = not self.state.gestures_paused
        if self.state.gestures_paused:
            dpg.set_item_label("pause_btn", "|| PAUSED")
            dpg.bind_item_theme("pause_btn", create_primary_button_theme())
        else:
            dpg.set_item_label("pause_btn", "[P] Pause")
            dpg.bind_item_theme("pause_btn", create_ghost_button_theme())
        logger.info(f"Pause state now: {self.state.gestures_paused}")

    def _on_zoom_change(self, sender, value):
        """Handle manual zoom slider change"""
        self.state.zoom_level = value
        dpg.set_value("zoom_value", f"{value:.1f}x")
        # Also update the processed video zoom display
        if dpg.does_item_exist("zoom_display"):
            dpg.set_value("zoom_display", f"{value:.1f}x")

    def _on_settings_click(self):
        """Open settings popup"""
        # Create popup if not exists
        if not dpg.does_item_exist("settings_popup"):
            with dpg.window(
                label="Settings",
                tag="settings_popup",
                modal=True,
                show=True,
                width=400,
                height=300,
                pos=(self.WINDOW_WIDTH // 2 - 200, self.WINDOW_HEIGHT // 2 - 150),
                on_close=lambda: dpg.configure_item("settings_popup", show=False),
            ):
                dpg.add_text("Camera Settings", color=PRIMARY)
                dpg.add_spacer(height=16)

                # Detection sensitivity
                dpg.add_text("Detection Sensitivity", color=TEXT_MUTED)
                dpg.add_slider_float(
                    label="Hand",
                    default_value=0.5,
                    min_value=0.1,
                    max_value=1.0,
                    tag="sensitivity_hand",
                    width=250,
                )
                dpg.add_slider_float(
                    label="Face",
                    default_value=0.5,
                    min_value=0.1,
                    max_value=1.0,
                    tag="sensitivity_face",
                    width=250,
                )

                dpg.add_spacer(height=16)

                # Smoothing
                dpg.add_text("Tracking Smoothing", color=TEXT_MUTED)
                dpg.add_slider_float(
                    label="Smoothness",
                    default_value=0.7,
                    min_value=0.0,
                    max_value=1.0,
                    tag="smoothing",
                    width=250,
                )

                dpg.add_spacer(height=20)

                # Close button
                dpg.add_button(
                    label="Close",
                    callback=lambda: dpg.configure_item("settings_popup", show=False),
                    width=100,
                )
        else:
            dpg.configure_item("settings_popup", show=True)

        if self.on_settings_open:
            self.on_settings_open()

    def _on_virtual_camera_click(self):
        self.state.virtual_camera_active = not self.state.virtual_camera_active
        if self.state.virtual_camera_active:
            dpg.set_item_label("virtual_camera_btn", "Stop Virtual Camera")
            # Apply primary theme to show active
            dpg.bind_item_theme("virtual_camera_btn", create_primary_button_theme())
        else:
            dpg.set_item_label("virtual_camera_btn", "Start Virtual Camera")
            # Reset to ghost theme
            dpg.bind_item_theme("virtual_camera_btn", create_ghost_button_theme())
        if self.on_virtual_camera_toggle:
            self.on_virtual_camera_toggle(self.state.virtual_camera_active)

    def run(self):
        """Main UI loop"""
        self.running = True
        dpg.show_viewport()

        while dpg.is_dearpygui_running() and self.running:
            self._render_frame()
            dpg.render_dearpygui_frame()

        self.shutdown()

    def shutdown(self):
        """Clean up resources"""
        self.running = False
        dpg.destroy_context()
        logger.info("Native UI shutdown")


def run_demo():
    """Demo mode - run UI with camera, face detection, and gesture control"""
    import math
    import os
    import urllib.request

    import mediapipe as mp
    from mediapipe.tasks import python as mp_tasks
    from mediapipe.tasks.python import vision as mp_vision

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    ui = NativeUI()
    ui.setup()

    # Camera setup
    cap = None
    camera_index = 0
    for idx in range(5):
        test_cap = cv2.VideoCapture(idx)
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            if ret and frame is not None:
                cap = test_cap
                camera_index = idx
                logger.info(f"Camera opened at index {idx}")
                break
            test_cap.release()

    if cap is None:
        cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Get camera name
    camera_name = f"Camera {camera_index}"
    try:
        import subprocess

        result = subprocess.run(
            ["system_profiler", "SPCameraDataType", "-json"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        import json

        data = json.loads(result.stdout)
        cameras = data.get("SPCameraDataType", [])
        if cameras and camera_index < len(cameras):
            camera_name = cameras[camera_index].get("_name", f"Camera {camera_index}")
    except Exception:
        pass

    ui.update_state(camera_name=camera_name)

    # Download models
    models_dir = os.path.expanduser("~/.gesturecam")
    os.makedirs(models_dir, exist_ok=True)

    hand_model_path = os.path.join(models_dir, "hand_landmarker.task")
    face_model_path = os.path.join(models_dir, "face_landmarker.task")

    for model_path, url, name in [
        (
            hand_model_path,
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
            "hand",
        ),
        (
            face_model_path,
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            "face",
        ),
    ]:
        if not os.path.exists(model_path):
            logger.info(f"Downloading {name} model...")
            try:
                urllib.request.urlretrieve(url, model_path)
            except Exception as e:
                logger.error(f"Failed: {e}")

    # Initialize detectors
    hand_detector = None
    face_detector = None

    try:
        hand_detector = mp_vision.HandLandmarker.create_from_options(
            mp_vision.HandLandmarkerOptions(
                base_options=mp_tasks.BaseOptions(model_asset_path=hand_model_path),
                running_mode=mp_vision.RunningMode.IMAGE,
                num_hands=2,
                min_hand_detection_confidence=0.5,
            )
        )
        logger.info("Hand detector initialized")
    except Exception as e:
        logger.error(f"Hand detector failed: {e}")

    try:
        face_detector = mp_vision.FaceLandmarker.create_from_options(
            mp_vision.FaceLandmarkerOptions(
                base_options=mp_tasks.BaseOptions(model_asset_path=face_model_path),
                running_mode=mp_vision.RunningMode.IMAGE,
                num_faces=1,
                output_face_blendshapes=True,
            )
        )
        logger.info("Face detector initialized")
    except Exception as e:
        logger.error(f"Face detector failed: {e}")

    # State
    zoom_level = 1.0
    target_zoom = 1.0
    wink_zoom_active = False
    wink_cooldown = 0
    last_hand_distance = None

    THUMB_TIP, THUMB_IP = 4, 3
    INDEX_TIP, INDEX_PIP = 8, 6
    MIDDLE_TIP, RING_TIP, PINKY_TIP = 12, 16, 20
    MIDDLE_PIP, RING_PIP, PINKY_PIP = 10, 14, 18

    def detect_peace_sign(landmarks):
        """Detect peace/victory sign (✌️) - index and middle up, others down"""
        index_up = landmarks[INDEX_TIP].y < landmarks[INDEX_PIP].y - 0.03
        middle_up = landmarks[MIDDLE_TIP].y < landmarks[MIDDLE_PIP].y - 0.03
        ring_down = landmarks[RING_TIP].y > landmarks[RING_PIP].y
        pinky_down = landmarks[PINKY_TIP].y > landmarks[PINKY_PIP].y
        thumb_in = abs(landmarks[THUMB_TIP].x - landmarks[THUMB_IP].x) < 0.1

        return index_up and middle_up and ring_down and pinky_down and thumb_in

    def detect_open_palm(landmarks):
        """Detect open palm (🖐️) - all fingers extended"""
        all_up = all(
            landmarks[tip].y < landmarks[pip].y - 0.02
            for tip, pip in [
                (INDEX_TIP, INDEX_PIP),
                (MIDDLE_TIP, MIDDLE_PIP),
                (RING_TIP, RING_PIP),
                (PINKY_TIP, PINKY_PIP),
            ]
        )
        return all_up

    def detect_gesture(landmarks):
        thumb_up = landmarks[THUMB_TIP].y < landmarks[THUMB_IP].y - 0.05
        thumb_down = landmarks[THUMB_TIP].y > landmarks[THUMB_IP].y + 0.05
        fingers_closed = all(
            landmarks[tip].y > landmarks[pip].y
            for tip, pip in [
                (INDEX_TIP, INDEX_PIP),
                (MIDDLE_TIP, MIDDLE_PIP),
                (RING_TIP, RING_PIP),
                (PINKY_TIP, PINKY_PIP),
            ]
        )
        if thumb_up and fingers_closed:
            return "Zoom In [+]"
        elif thumb_down and fingers_closed:
            return "Zoom Out [-]"
        return None

    def detect_wink(blendshapes):
        if not blendshapes:
            return None
        left, right = 0, 0
        for bs in blendshapes[0]:
            if bs.category_name == "eyeBlinkLeft":
                left = bs.score
            elif bs.category_name == "eyeBlinkRight":
                right = bs.score
        diff = abs(left - right)
        if diff > 0.2:
            if left > 0.35 and right < 0.2:
                return "left"
            elif right > 0.35 and left < 0.2:
                return "right"
            elif left > right + 0.25:
                return "left"
            elif right > left + 0.25:
                return "right"
        return None

    def draw_hand(frame, landmarks, h, w, color):
        points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        for i, j in [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (0, 5),
            (5, 6),
            (6, 7),
            (7, 8),
            (5, 9),
            (9, 10),
            (10, 11),
            (11, 12),
            (9, 13),
            (13, 14),
            (14, 15),
            (15, 16),
            (13, 17),
            (17, 18),
            (18, 19),
            (19, 20),
            (0, 17),
        ]:
            cv2.line(frame, points[i], points[j], (255, 255, 255), 2)
        for i, pt in enumerate(points):
            cv2.circle(frame, pt, 5, color if i in [4, 8, 12, 16, 20] else (200, 200, 200), -1)

    def video_thread():
        nonlocal zoom_level, target_zoom, wink_zoom_active, wink_cooldown, last_hand_distance

        current_cx = None
        current_cy = None

        logger.info("Video thread started")

        while ui.running and cap.isOpened():
            start_time = time.time()

            # Sync with manual slider changes
            if abs(ui.state.zoom_level - zoom_level) > 0.05:
                zoom_level = ui.state.zoom_level
                target_zoom = ui.state.zoom_level

            ret, frame = cap.read()
            if not ret:
                time.sleep(0.05)
                continue

            gesture = "None"
            original = frame.copy()
            h, w = frame.shape[:2]
            face_center = None

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

            # Face detection
            if face_detector:
                try:
                    results = face_detector.detect(mp_image)
                    if results.face_landmarks:
                        landmarks = results.face_landmarks[0]
                        xs = [lm.x * w for lm in landmarks]
                        ys = [lm.y * h for lm in landmarks]
                        face_center = (int(sum(xs) / len(xs)), int(sum(ys) / len(ys)))

                        if ui.state.show_overlay:
                            x1, x2 = int(min(xs)), int(max(xs))
                            y1, y2 = int(min(ys)), int(max(ys))
                            cv2.rectangle(original, (x1, y1), (x2, y2), PRIMARY[::-1], 2)

                    if wink_cooldown <= 0:
                        wink = detect_wink(results.face_blendshapes)
                        if wink and not wink_zoom_active:
                            gesture = f"WINK! [{wink}]"
                            wink_zoom_active = True
                            target_zoom = min(2.5, zoom_level + 1.0)
                            wink_cooldown = 30
                except Exception:
                    pass

            if wink_cooldown > 0:
                wink_cooldown -= 1
                if wink_zoom_active and wink_cooldown < 15:
                    target_zoom = max(1.0, target_zoom - 0.1)
                    if target_zoom <= 1.0:
                        wink_zoom_active = False

            # Hand detection
            if hand_detector:
                try:
                    results = hand_detector.detect(mp_image)
                    if results.hand_landmarks:
                        centers = []
                        colors = [(242, 103, 100), (100, 242, 150)]
                        peace_detected = False

                        for i, landmarks in enumerate(results.hand_landmarks):
                            if ui.state.show_overlay:
                                draw_hand(original, landmarks, h, w, colors[i % 2])

                            center = (
                                int(sum(lm.x for lm in landmarks) / 21 * w),
                                int(sum(lm.y for lm in landmarks) / 21 * h),
                            )
                            centers.append(center)

                            # Check for peace sign to toggle pause
                            if detect_peace_sign(landmarks):
                                peace_detected = True

                            # Only detect gesture actions if NOT paused
                            if not ui.state.gestures_paused:
                                g = detect_gesture(landmarks)
                                if g:
                                    gesture = g
                                    if "In" in g:
                                        target_zoom = min(3.0, target_zoom + 0.02)
                                    elif "Out" in g:
                                        target_zoom = max(1.0, target_zoom - 0.02)

                        # Toggle pause on peace sign (with cooldown handled by gesture display)
                        if peace_detected:
                            gesture = "✌️ PAUSE" if not ui.state.gestures_paused else "✌️ RESUME"

                        if len(centers) == 2:
                            dist = math.sqrt(
                                (centers[0][0] - centers[1][0]) ** 2
                                + (centers[0][1] - centers[1][1]) ** 2
                            )
                            if ui.state.show_overlay:
                                cv2.line(original, centers[0], centers[1], (255, 200, 100), 3)
                            # Pinch zoom only if NOT paused
                            if not ui.state.gestures_paused:
                                if last_hand_distance and abs(dist - last_hand_distance) > 5:
                                    delta = (dist - last_hand_distance) * 0.002
                                    target_zoom = max(1.0, min(3.0, target_zoom + delta))
                                    gesture = f"Pinch [{'+' if delta > 0 else '-'}]"
                            last_hand_distance = dist
                        else:
                            last_hand_distance = None
                except Exception:
                    pass

            # Smooth zoom
            zoom_level += (target_zoom - zoom_level) * 0.15
            ui.state.zoom_level = zoom_level

            # Create processed frame with framing mode
            zh, zw = int(h / zoom_level), int(w / zoom_level)

            if current_cx is None:
                current_cx, current_cy = w / 2.0, h / 2.0

            if face_center and ui.state.framing_mode != FramingMode.MANUAL:
                fx, fy = face_center
                if ui.state.framing_mode == FramingMode.FACE_FOLLOW:
                    current_cx = current_cx * 0.7 + fx * 0.3
                    current_cy = current_cy * 0.7 + fy * 0.3
                elif ui.state.framing_mode == FramingMode.HEADSHOT:
                    current_cx = current_cx * 0.7 + fx * 0.3
                    target_yf = max(zh // 2, fy - int(h * 0.05))
                    current_cy = current_cy * 0.7 + target_yf * 0.3
                elif ui.state.framing_mode == FramingMode.SHIRT_UP:
                    current_cx = current_cx * 0.7 + fx * 0.3
                    target_ys = min(h - zh // 2, fy + int(h * 0.15))
                    current_cy = current_cy * 0.7 + target_ys * 0.3

                cx, cy = int(current_cx), int(current_cy)
            else:
                current_cx = current_cx * 0.9 + (w / 2.0) * 0.1
                current_cy = current_cy * 0.9 + (h / 2.0) * 0.1
                cx, cy = int(current_cx), int(current_cy)

            x1 = max(0, min(w - zw, cx - zw // 2))
            y1 = max(0, min(h - zh, cy - zh // 2))

            processed = frame[y1 : y1 + zh, x1 : x1 + zw]
            if processed.size > 0:
                processed = cv2.resize(processed, (w, h))
            else:
                processed = frame.copy()

            latency = (time.time() - start_time) * 1000
            ui.update_frame(original, processed)
            ui.update_state(gesture=gesture, zoom=zoom_level, latency=latency)

            time.sleep(0.016)

        cap.release()
        if hand_detector:
            hand_detector.close()
        if face_detector:
            face_detector.close()
        logger.info("Video thread stopped")

    ui.running = True
    thread = threading.Thread(target=video_thread, daemon=True)
    thread.start()
    ui.run()


if __name__ == "__main__":
    run_demo()
