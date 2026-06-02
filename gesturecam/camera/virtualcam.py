try:
    import pyvirtualcam
except ImportError:
    pyvirtualcam = None

import logging


class VirtualCamera:
    def __init__(self, width, height, fps=30, backend="v4l2"):
        self.width = width
        self.height = height
        self.fps = fps
        self.cam = None
        self.mock_mode = False

        if pyvirtualcam is None:
            logging.warning("pyvirtualcam library not installed. Virtual Camera disabled.")
            self.mock_mode = True
            return

        try:
            self.cam = pyvirtualcam.Camera(
                width=width,
                height=height,
                fps=fps,
                backend=backend,
                fmt=pyvirtualcam.PixelFormat.BGR,
            )
            logging.info(f"Virtual Camera started: {width}x{height} @ {fps}fps")
        except Exception as e:
            logging.warning(
                f"Could not start Virtual Camera: {e}. Output will not be sent to virtual device."
            )
            self.mock_mode = True

    def send(self, frame):
        if self.mock_mode:
            return

        if self.cam:
            self.cam.send(frame)
            self.cam.sleep_until_next_frame()

    def close(self):
        if self.cam:
            self.cam.close()
