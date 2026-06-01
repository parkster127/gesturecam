"""
Pipeline Core - Orchestrator of Threads for High Performance

Architecture:
- Video Thread: Captures frames at max FPS.
- AI Worker Thread: Processes frames asynchronously.
- Main Loop: Renders frames and smooths camera movement using stale AI data if needed.
"""

import threading
import time
import cv2
import numpy as np
from queue import Queue, Empty
import logging
from typing import Optional, Dict, Tuple

# Imports locales
from gesturecam.vision.face_mesh import FaceMeshTracker, FaceMetrics
from gesturecam.camera.operator import CameraOperator, CameraMode
from gesturecam.control.gestures import GestureController


class VisionWorker(threading.Thread):
    """
    Worker thread that runs the heavy AI inference.
    It drops frames if it can't keep up, ensuring latest data is always fresh.
    """

    def __init__(self, model_complexity=1, downscale_factor=0.5):
        super().__init__()
        self.daemon = True
        self.running = False
        self.latest_frame = None
        self.latest_result: Optional[FaceMetrics] = None
        self.frame_lock = threading.Lock()
        self.result_lock = threading.Lock()
        self.new_frame_event = threading.Event()

        self.model_complexity = model_complexity
        self.downscale_factor = downscale_factor  # 0.5 = processing at half resolution

        # Performance metrics
        self.fps = 0
        self.frame_count = 0
        self.last_time = time.time()

    def update_frame(self, frame: np.ndarray):
        """Update the frame for the AI to process"""
        with self.frame_lock:
            self.latest_frame = frame.copy()  # Copy to avoid race conditions
        self.new_frame_event.set()

    def get_result(self) -> Optional[FaceMetrics]:
        """Get the latest AI result safely"""
        with self.result_lock:
            return self.latest_result

    def run(self):
        print(
            f"👁️ AI Worker started (Scale: {self.downscale_factor}, Model: {self.model_complexity})"
        )

        # Initialize MediaPipe inside the thread
        tracker = FaceMeshTracker(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=(self.model_complexity > 0),
        )

        self.running = True

        while self.running:
            # Wait for new frame
            if not self.new_frame_event.wait(timeout=1.0):
                continue

            self.new_frame_event.clear()

            # Get frame safely
            with self.frame_lock:
                if self.latest_frame is None:
                    continue
                # Downscale for performance
                h, w = self.latest_frame.shape[:2]
                small_w = int(w * self.downscale_factor)
                small_h = int(h * self.downscale_factor)
                frame_to_process = cv2.resize(self.latest_frame, (small_w, small_h))

            # --- INFERENCE ---
            metrics = tracker.detect(frame_to_process)

            # Rescale coordinates back to original size
            if metrics.detected and metrics.landmarks_array is not None:
                scale = 1.0 / self.downscale_factor

                # Scale landmarks
                metrics.landmarks_array = metrics.landmarks_array * scale

                # Scale bbox
                bx, by, bw, bh = metrics.bbox
                metrics.bbox = (
                    int(bx * scale),
                    int(by * scale),
                    int(bw * scale),
                    int(bh * scale),
                )

                # Scale center
                cx, cy = metrics.center
                metrics.center = (cx * scale, cy * scale)

                # Scale eyes (complex objects, simplifying just center for now)
                # Note: Deep copy scaling would be needed for full eye mesh analysis
                # For auto-framing, center/bbox is enough.

            # Update result safely
            with self.result_lock:
                self.latest_result = metrics

            # FPS Calculation
            self.frame_count += 1
            if time.time() - self.last_time > 1.0:
                self.fps = self.frame_count / (time.time() - self.last_time)
                self.frame_count = 0
                self.last_time = time.time()


class GestureCamPipeline:
    """
    Main Application Pipeline.
    Orchestrates Video I/O, AI Worker, and Camera Operator.
    """

    def __init__(self, source=0, width=1280, height=720, lite_mode=False):
        self.width = width
        self.height = height
        self.lite_mode = lite_mode

        # Video Capture
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # AI Worker (The Eye)
        # Lite Mode: 0.25 scale (320p), Simple Model
        # Normal Mode: 0.5 scale (640p), Complex Model
        scale = 0.25 if lite_mode else 0.5
        complexity = 0 if lite_mode else 1

        self.vision_worker = VisionWorker(
            model_complexity=complexity, downscale_factor=scale
        )
        self.vision_worker.start()

        # Camera Operator (The Cameraman)
        self.cameraman = CameraOperator(width, height)
        self.cameraman.set_mode(CameraMode.SMART_ZOOM)  # Default to smart mode

        # Gesture Controller (The Hands)
        self.gesture_ctrl = GestureController()

        self.running = True

        # Stats
        self.render_fps = 0
        self.last_render_time = time.time()
        self.render_frames = 0

    def step(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Process a single frame loop.
        Returns: (debug_frame, virtual_cam_frame)
        """
        ret, frame = self.cap.read()
        if not ret:
            return None, None

        frame = cv2.flip(frame, 1)  # Mirror

        # 1. Send to AI (Non-blocking)
        self.vision_worker.update_frame(frame)

        # 1.5 Process Gestures (On main thread for now, light enough)
        # Only process every 3rd frame to save CPU
        if self.render_frames % 3 == 0:
            command = self.gesture_ctrl.detect(frame)
            action = command.get("action")

            if action == "toggle_lock":
                is_locked = command["value"]
                self.cameraman.is_tracking = not is_locked
                print(f"✋ CAMERA LOCK: {is_locked}")

            elif action == "set_zoom":
                zoom_val = command["value"]
                # Override to Manual Mode temporarily
                if self.cameraman.mode != CameraMode.MANUAL:
                    self.cameraman.set_mode(CameraMode.MANUAL)

                self.cameraman.set_manual_zoom(zoom_val)

        # 2. Get latest AI result (Instant, might be old)
        metrics = self.vision_worker.get_result()

        # 3. Update Cameraman (Physics-based smoothing handles old data gracefully)
        if metrics and metrics.detected:
            self.cameraman.update_target(metrics.bbox, metrics.center)

        # 4. Generate Output (Virtual Camera View)
        output_frame = self.cameraman.crop_frame(frame)

        # 5. Debug Stats
        self.render_frames += 1
        if time.time() - self.last_render_time > 1.0:
            self.render_fps = self.render_frames / (time.time() - self.last_render_time)
            self.render_frames = 0
            self.last_render_time = time.time()

        # Draw Debug Info on original frame
        debug_frame = frame.copy()
        vx, vy, vw, vh = self.cameraman.process()
        cv2.rectangle(debug_frame, (vx, vy), (vx + vw, vy + vh), (0, 255, 0), 2)

        # OSD
        cv2.putText(
            debug_frame,
            f"VID FPS: {self.render_fps:.1f}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )
        cv2.putText(
            debug_frame,
            f"AI FPS:  {self.vision_worker.fps:.1f}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )
        cv2.putText(
            debug_frame,
            f"MODE:    {'LITE (i3)' if self.lite_mode else 'FULL'}",
            (20, 100),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

        return debug_frame, output_frame

    def stop(self):
        self.running = False
        self.vision_worker.running = False
        self.cap.release()
