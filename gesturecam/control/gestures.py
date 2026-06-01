"""
Gesture Control Module
Handles hand gestures for controlling the camera (Zoom, Lock, Mode).
"""

import cv2
import numpy as np
import mediapipe as mp
import math
import time


class GestureController:
    """
    Detects hand gestures to control camera parameters.
    """

    def __init__(self, min_detection_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=0.5,
        )

        self.last_zoom_dist = None
        self.is_locked = False
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5  # Seconds

    def detect(self, frame: np.ndarray):
        """
        Process frame and return control commands.
        Returns: dict with 'action', 'value'
        """
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        command = {"action": "none"}

        if not results.multi_hand_landmarks:
            self.last_zoom_dist = None  # Reset pinch tracking
            return command

        hand_landmarks = results.multi_hand_landmarks[0]
        lm = hand_landmarks.landmark

        # Convert key landmarks to pixel coords
        thumb_tip = (int(lm[4].x * w), int(lm[4].y * h))
        index_tip = (int(lm[8].x * w), int(lm[8].y * h))
        middle_tip = (int(lm[12].x * w), int(lm[12].y * h))
        ring_tip = (int(lm[16].x * w), int(lm[16].y * h))
        pinky_tip = (int(lm[20].x * w), int(lm[20].y * h))
        wrist = (int(lm[0].x * w), int(lm[0].y * h))

        # --- GESTURE 1: OPEN PALM (STOP/LOCK) ---
        # All fingers extended and separated
        # Simple check: Tips are higher than PIP joints (assuming hand is up)
        # Better check: Distance from wrist to tips is large

        # Check if 4 fingers are open (Index, Middle, Ring, Pinky)
        fingers_open = 0
        if lm[8].y < lm[6].y:
            fingers_open += 1
        if lm[12].y < lm[10].y:
            fingers_open += 1
        if lm[16].y < lm[14].y:
            fingers_open += 1
        if lm[20].y < lm[18].y:
            fingers_open += 1

        # Check thumb extended (x distance from wrist)
        thumb_open = abs(lm[4].x - lm[2].x) > 0.05

        if fingers_open == 4 and thumb_open:
            if time.time() - self.last_gesture_time > self.gesture_cooldown:
                self.is_locked = not self.is_locked
                self.last_gesture_time = time.time()
                return {"action": "toggle_lock", "value": self.is_locked}

        # --- GESTURE 2: PINCH (ZOOM CONTROL) ---
        # Thumb and Index close together?
        pinch_dist = math.hypot(
            thumb_tip[0] - index_tip[0], thumb_tip[1] - index_tip[1]
        )

        # Normalize distance by hand size (wrist to middle finger mcp)
        # hand_size = math.hypot(wrist[0] - lm[9].x*w, wrist[1] - lm[9].y*h)
        # normalized_pinch = pinch_dist / hand_size if hand_size > 0 else 0

        # Simple Pinch Logic:
        # If pinch is held (distance < 40px), track Y movement for zoom
        if pinch_dist < 60:  # Pinch threshold
            # Draw visual feedback
            cv2.line(frame, thumb_tip, index_tip, (0, 255, 0), 3)

            # Map Y position to Zoom Level
            # Top of screen (y=0) = Zoom 3.0x
            # Bottom of screen (y=h) = Zoom 1.0x
            zoom_level = 1.0 + (1.0 - (thumb_tip[1] / h)) * 2.0  # Range 1.0 to 3.0

            return {"action": "set_zoom", "value": zoom_level}

        return command
