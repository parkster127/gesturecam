import cv2
import numpy as np


class ZoomController:
    def __init__(self, min_zoom=1.0, max_zoom=3.0, smoothing_factor=0.1):
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.smoothing_factor = smoothing_factor
        self.current_zoom = 1.0
        self.target_zoom = 1.0
        self.center_x = 0.5
        self.center_y = 0.5

    def update_zoom_level(self, raw_factor):
        self.target_zoom = np.clip(raw_factor, self.min_zoom, self.max_zoom)

    def set_target_zoom(self, zoom):
        self.target_zoom = np.clip(zoom, self.min_zoom, self.max_zoom)

    def set_zoom_center(self, x, y):
        """Sets the normalized center point (0.0-1.0) for the zoom."""
        self.center_x = np.clip(x, 0.0, 1.0)
        self.center_y = np.clip(y, 0.0, 1.0)

    def step(self):
        """Applies smoothing step."""
        diff = self.target_zoom - self.current_zoom
        self.current_zoom += diff * self.smoothing_factor
        return self.current_zoom

    def apply_zoom(self, frame):
        """
        Crops and resizes the frame based on current_zoom and center_x/y.
        """
        h, w, _ = frame.shape
        new_w = w / self.current_zoom
        new_h = h / self.current_zoom

        top_left_x = (self.center_x * w) - (new_w / 2)
        top_left_y = (self.center_y * h) - (new_h / 2)

        top_left_x = np.clip(top_left_x, 0, w - new_w)
        top_left_y = np.clip(top_left_y, 0, h - new_h)

        x1 = int(top_left_x)
        y1 = int(top_left_y)
        x2 = int(x1 + new_w)
        y2 = int(y1 + new_h)

        cropped = frame[y1:y2, x1:x2]
        resized = cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

        return resized
