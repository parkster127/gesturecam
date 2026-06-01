import numpy as np

class FramingController:
    def __init__(self, smoothing_factor=0.1):
        self.smoothing_factor = smoothing_factor
        self.target_center_x = 0.5
        self.target_center_y = 0.5
        self.current_center_x = 0.5
        self.current_center_y = 0.5
        self.mode = "manual" # manual, face_follow, headshot, shirt_up

    def update_face_target(self, face_bbox, frame_width, frame_height):
        """
        Updates target center based on face bounding box.
        face_bbox: (x, y, w, h)
        """
        if face_bbox is None:
            return

        x, y, w, h = face_bbox
        
        if self.mode == "face_follow":
            self.target_center_x = (x + w / 2) / frame_width
            self.target_center_y = (y + h / 2) / frame_height
            
        elif self.mode == "headshot":
            # Center on face, but maybe slightly higher to include shoulders?
            # Actually, standard headshot is face centered or slightly above center.
            self.target_center_x = (x + w / 2) / frame_width
            self.target_center_y = (y + h / 3) / frame_height # framing higher
            
        elif self.mode == "shirt_up":
            # Include chest. Target center should be lower on the body, 
            # meaning the camera frame moves down relative to face, 
            # so the face is higher up in the frame?
            # No, 'shirt up' usually means "from shirt upwards".
            # So we want the bottom of the frame to be around the chest/shirt.
            # We target the center such that the face is in the top third.
            self.target_center_x = (x + w / 2) / frame_width
            self.target_center_y = (y + h / 2) / frame_height # Standard center
            
        # Clamp targets
        self.target_center_x = np.clip(self.target_center_x, 0.0, 1.0)
        self.target_center_y = np.clip(self.target_center_y, 0.0, 1.0)

    def step(self):
        """Applies smoothing to the center point."""
        if self.mode == "manual":
            # In manual mode, we don't auto-update, but we might smooth user inputs if set elsewhere
            return self.current_center_x, self.current_center_y

        diff_x = self.target_center_x - self.current_center_x
        diff_y = self.target_center_y - self.current_center_y
        
        self.current_center_x += diff_x * self.smoothing_factor
        self.current_center_y += diff_y * self.smoothing_factor
        
        return self.current_center_x, self.current_center_y

    def set_mode(self, mode):
        if mode in ["manual", "face_follow", "headshot", "shirt_up"]:
            self.mode = mode
