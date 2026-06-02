#!/usr/bin/env python3
"""Personal face calibration tool. Usage: python -m tests.calibrate_face"""

import cv2
import numpy as np
import json
import os
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesturecam.vision.face_mesh import FaceMeshTracker


class PersonalCalibrator:
    """Calibrate face detection for your specific face"""

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.tracker = FaceMeshTracker(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True,
        )

        self.calibration_data = {
            "eyes_open_ear": [],
            "eyes_closed_ear": [],
            "neutral_pose": {"pitch": [], "yaw": [], "roll": []},
            "recommended_thresholds": {},
        }

        self.output_path = "calibration_profile.json"

    def _collect_samples(self, cap, message: str, duration: float = 3.0) -> list:
        """Collect EAR samples for a duration"""
        samples = []
        start_time = time.time()

        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            metrics = self.tracker.detect(frame)

            elapsed = time.time() - start_time
            progress = int((elapsed / duration) * 100)

            # Draw UI
            display = frame.copy()
            cv2.rectangle(display, (0, 0), (frame.shape[1], 100), (0, 0, 0), -1)
            cv2.putText(
                display,
                message,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                display,
                f"Progress: {progress}%",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                1,
            )

            # Progress bar
            bar_width = int((elapsed / duration) * (frame.shape[1] - 40))
            cv2.rectangle(display, (20, 90), (20 + bar_width, 95), (0, 255, 0), -1)

            if metrics.detected:
                samples.append(metrics.avg_ear)

                # Draw face feedback
                x, y, w, h = metrics.bbox
                cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(
                    display,
                    f"EAR: {metrics.avg_ear:.3f}",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    display,
                    "Face not detected - move closer",
                    (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Calibration", display)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                return samples

        return samples

    def run(self):
        """Run calibration wizard"""
        print("\n" + "=" * 60)
        print("PERSONAL FACE CALIBRATION WIZARD")
        print("=" * 60)
        print("\nThis will calibrate detection thresholds for YOUR face.")
        print("Please follow the on-screen instructions.\n")

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("Error: Could not open camera")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        try:
            # Step 1: Eyes open baseline
            print("STEP 1: Keep your eyes OPEN naturally")
            print("        Look at the camera for 3 seconds...")
            self._countdown(cap, 3)

            open_samples = self._collect_samples(
                cap, "Keep eyes OPEN - looking at camera", 3.0
            )

            if len(open_samples) < 10:
                print("Not enough samples. Please ensure your face is visible.")
                return

            self.calibration_data["eyes_open_ear"] = open_samples
            open_mean = np.mean(open_samples)
            open_std = np.std(open_samples)
            print(f"   Eyes open EAR: {open_mean:.3f} (+/- {open_std:.3f})")

            # Step 2: Eyes closed
            print("\nSTEP 2: CLOSE your eyes for 3 seconds")
            self._countdown(cap, 3)

            closed_samples = self._collect_samples(cap, "Keep eyes CLOSED", 3.0)

            if len(closed_samples) < 10:
                print("Not enough samples. Please try again.")
                return

            self.calibration_data["eyes_closed_ear"] = closed_samples
            closed_mean = np.mean(closed_samples)
            closed_std = np.std(closed_samples)
            print(f"   Eyes closed EAR: {closed_mean:.3f} (+/- {closed_std:.3f})")

            # Step 3: Neutral pose
            print("\nSTEP 3: Look directly at the camera (neutral pose)")
            self._countdown(cap, 3)

            pose_samples = self._collect_pose_samples(cap, 3.0)
            self.calibration_data["neutral_pose"] = pose_samples

            # Calculate optimal threshold
            # Threshold should be between closed and open, but closer to closed
            threshold = closed_mean + (open_mean - closed_mean) * 0.3

            # Ensure threshold is reasonable
            threshold = max(0.15, min(threshold, 0.35))

            self.calibration_data["recommended_thresholds"] = {
                "ear_threshold": round(threshold, 3),
                "ear_open_baseline": round(open_mean, 3),
                "ear_closed_baseline": round(closed_mean, 3),
                "ear_difference": round(open_mean - closed_mean, 3),
                "detection_quality": "good"
                if (open_mean - closed_mean) > 0.1
                else "marginal",
            }

            # Save calibration
            with open(self.output_path, "w") as f:
                json.dump(self.calibration_data, f, indent=2, default=float)

            # Show results
            self._show_results(cap)

            print("\n" + "=" * 60)
            print("CALIBRATION COMPLETE")
            print("=" * 60)
            print(f"\nResults saved to: {self.output_path}")
            print(f"\nRecommended EAR threshold: {threshold:.3f}")
            print(f"Your eye open baseline: {open_mean:.3f}")
            print(f"Your eye closed baseline: {closed_mean:.3f}")
            print(
                f"Detection quality: {self.calibration_data['recommended_thresholds']['detection_quality']}"
            )

            if (open_mean - closed_mean) < 0.08:
                print("\n[WARNING] Low EAR difference detected!")
                print("This could indicate:")
                print("  - Poor lighting conditions")
                print("  - Camera angle issues")
                print("  - Natural eye shape characteristics")
                print("\nTry improving lighting or adjusting camera position.")

        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.tracker.close()

    def _countdown(self, cap, seconds: int):
        """Show countdown before starting collection"""
        for i in range(seconds, 0, -1):
            start = time.time()
            while time.time() - start < 1.0:
                ret, frame = cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    display = frame.copy()
                    cv2.rectangle(display, (0, 0), (frame.shape[1], 100), (0, 0, 0), -1)
                    cv2.putText(
                        display,
                        f"Get ready... {i}",
                        (20, 60),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.5,
                        (0, 255, 255),
                        3,
                    )
                    cv2.imshow("Calibration", display)
                    cv2.waitKey(1)

    def _collect_pose_samples(self, cap, duration: float) -> dict:
        """Collect head pose samples"""
        samples = {"pitch": [], "yaw": [], "roll": []}
        start_time = time.time()

        while time.time() - start_time < duration:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            metrics = self.tracker.detect(frame)

            if metrics.detected:
                samples["pitch"].append(metrics.pitch)
                samples["yaw"].append(metrics.yaw)
                samples["roll"].append(metrics.roll)

            # Simple display
            display = frame.copy()
            cv2.rectangle(display, (0, 0), (frame.shape[1], 60), (0, 0, 0), -1)
            cv2.putText(
                display,
                "Look directly at camera (neutral)",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
            )
            cv2.imshow("Calibration", display)
            cv2.waitKey(1)

        return samples

    def _show_results(self, cap):
        """Show live preview with calibrated threshold"""
        threshold = self.calibration_data["recommended_thresholds"]["ear_threshold"]
        self.tracker.ear_threshold = threshold

        print("\nShowing live preview with your calibrated threshold...")
        print("Press any key to finish.")

        start = time.time()
        while time.time() - start < 5.0:  # Show for 5 seconds
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            metrics = self.tracker.detect(frame)

            display = self.tracker.draw_debug_overlay(
                frame,
                metrics,
                show_mesh=False,
                show_eyes=True,
                show_iris=True,
                show_metrics=True,
                show_pose=True,
            )

            # Add calibration info
            cv2.rectangle(display, (0, 0), (400, 30), (0, 100, 0), -1)
            cv2.putText(
                display,
                f"Calibrated threshold: {threshold:.3f}",
                (10, 22),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )

            cv2.imshow("Calibration", display)
            if cv2.waitKey(1) & 0xFF != 255:
                break


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Personal Face Calibration")
    parser.add_argument("--camera", "-c", type=int, default=0, help="Camera index")
    args = parser.parse_args()

    calibrator = PersonalCalibrator(camera_index=args.camera)
    calibrator.run()


if __name__ == "__main__":
    main()
