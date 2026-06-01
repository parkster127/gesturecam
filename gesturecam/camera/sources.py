import cv2
import time
import logging

class CameraSource:
    def __init__(self, source):
        """
        source: int (device index) or str (filepath/url)
        """
        self.source = source
        self.cap = cv2.VideoCapture(source)
        
        if not self.cap.isOpened():
            logging.error(f"Failed to open camera source: {source}")
            # If basic source fails, maybe try to be resilient? 
            # But usually we want to fail hard here or let upper layer handle it.
        else:
            logging.info(f"Opened camera source: {source}")

    def read(self):
        """
        Returns (ret, frame)
        """
        return self.cap.read()

    def get_resolution(self):
        w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return w, h

    def release(self):
        self.cap.release()
