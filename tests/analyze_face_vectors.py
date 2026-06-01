#!/usr/bin/env python3
"""
Face Vector Analysis Tool - Data Science Mode

Interactive tool to analyze and understand facial vectors in real-time.
Helps debug detection issues and calibrate thresholds for your specific face.

Usage:
    python -m tests.analyze_face_vectors

Controls:
    q - Quit
    s - Save current frame analysis to CSV
    r - Reset statistics
    d - Toggle debug overlay
    m - Toggle mesh visualization
    e - Export feature vectors (last 100 frames)
"""

import cv2
import numpy as np
import time
import csv
import os
from datetime import datetime
from typing import List, Dict
import sys

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesturecam.vision.face_mesh import FaceMeshTracker, FaceMetrics


class FaceVectorAnalyzer:
    """Interactive analyzer for understanding face vectors"""

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.tracker = FaceMeshTracker(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True,  # Enable iris tracking
        )

        # Data collection
        self.feature_history: List[np.ndarray] = []
        self.metrics_history: List[Dict] = []
        self.max_history = 1000

        # Display settings
        self.show_debug = True
        self.show_mesh = True

        # Output directory
        self.output_dir = "analysis_output"
        os.makedirs(self.output_dir, exist_ok=True)

    def _metrics_to_dict(self, metrics: FaceMetrics) -> Dict:
        """Convert metrics to dictionary for CSV export"""
        return {
            "timestamp": time.time(),
            "detected": metrics.detected,
            "left_ear": metrics.left_eye.ear,
            "right_ear": metrics.right_eye.ear,
            "avg_ear": metrics.avg_ear,
            "left_eye_open": metrics.left_eye.is_open,
            "right_eye_open": metrics.right_eye.is_open,
            "mar": metrics.mar,
            "mouth_open": metrics.is_mouth_open,
            "pitch": metrics.pitch,
            "yaw": metrics.yaw,
            "roll": metrics.roll,
            "center_x": metrics.center[0] if metrics.detected else 0,
            "center_y": metrics.center[1] if metrics.detected else 0,
            "bbox_x": metrics.bbox[0],
            "bbox_y": metrics.bbox[1],
            "bbox_w": metrics.bbox[2],
            "bbox_h": metrics.bbox[3],
        }

    def _draw_analysis_panel(
        self, frame: np.ndarray, metrics: FaceMetrics, fps: float
    ) -> np.ndarray:
        """Draw comprehensive analysis panel"""
        h, w = frame.shape[:2]

        # Create side panel
        panel_width = 300
        panel = np.zeros((h, panel_width, 3), dtype=np.uint8)
        panel[:] = (30, 30, 30)  # Dark gray background

        y = 30
        line_height = 22

        def draw_text(text, color=(255, 255, 255), bold=False):
            nonlocal y
            thickness = 2 if bold else 1
            cv2.putText(
                panel, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness
            )
            y += line_height

        def draw_bar(label, value, max_val=1.0, color=(0, 255, 0)):
            nonlocal y
            cv2.putText(
                panel,
                f"{label}: {value:.3f}",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (200, 200, 200),
                1,
            )
            bar_x = 10
            bar_y = y + 5
            bar_width = 200
            bar_height = 10
            fill_width = int((value / max_val) * bar_width)
            fill_width = max(0, min(fill_width, bar_width))

            cv2.rectangle(
                panel,
                (bar_x, bar_y),
                (bar_x + bar_width, bar_y + bar_height),
                (100, 100, 100),
                -1,
            )
            cv2.rectangle(
                panel,
                (bar_x, bar_y),
                (bar_x + fill_width, bar_y + bar_height),
                color,
                -1,
            )
            y += line_height + 10

        # Header
        draw_text("FACE VECTOR ANALYSIS", (0, 200, 255), bold=True)
        draw_text(f"FPS: {fps:.1f}", (150, 150, 150))
        y += 10

        if not metrics.detected:
            draw_text("NO FACE DETECTED", (0, 0, 255), bold=True)
            draw_text("Move closer to camera", (150, 150, 150))
            draw_text("Ensure good lighting", (150, 150, 150))
        else:
            # Eye Analysis
            draw_text("EYE ANALYSIS", (0, 255, 255), bold=True)

            left_color = (0, 255, 0) if metrics.left_eye.is_open else (0, 0, 255)
            right_color = (0, 255, 0) if metrics.right_eye.is_open else (0, 0, 255)

            draw_bar("Left EAR", metrics.left_eye.ear, 0.5, left_color)
            draw_bar("Right EAR", metrics.right_eye.ear, 0.5, right_color)
            draw_bar("Avg EAR", metrics.avg_ear, 0.5, (255, 255, 0))

            # Threshold indicator
            draw_text(f"  Threshold: {self.tracker.ear_threshold:.3f}", (150, 150, 150))
            y += 10

            # Iris/Gaze
            if metrics.left_eye.iris_center:
                draw_text("GAZE TRACKING", (255, 0, 255), bold=True)
                if metrics.left_eye.gaze_direction:
                    gx, gy = metrics.left_eye.gaze_direction
                    draw_text(f"  L-Gaze: ({gx:.2f}, {gy:.2f})")
                if metrics.right_eye.gaze_direction:
                    gx, gy = metrics.right_eye.gaze_direction
                    draw_text(f"  R-Gaze: ({gx:.2f}, {gy:.2f})")
            else:
                draw_text("Iris: Not detected", (150, 150, 150))
            y += 10

            # Mouth Analysis
            draw_text("MOUTH ANALYSIS", (0, 255, 255), bold=True)
            mouth_color = (0, 255, 0) if not metrics.is_mouth_open else (255, 165, 0)
            draw_bar("MAR", metrics.mar, 1.0, mouth_color)
            y += 10

            # Head Pose
            draw_text("HEAD POSE", (0, 255, 255), bold=True)

            # Pitch (nodding)
            pitch_color = (0, 255, 0) if abs(metrics.pitch) < 15 else (255, 165, 0)
            draw_text(f"  Pitch: {metrics.pitch:+.1f} deg", pitch_color)

            # Yaw (turning)
            yaw_color = (0, 255, 0) if abs(metrics.yaw) < 15 else (255, 165, 0)
            draw_text(f"  Yaw: {metrics.yaw:+.1f} deg", yaw_color)

            # Roll (tilting)
            roll_color = (0, 255, 0) if abs(metrics.roll) < 15 else (255, 165, 0)
            draw_text(f"  Roll: {metrics.roll:+.1f} deg", roll_color)
            y += 10

            # Statistics
            stats = self.tracker.get_statistics()
            if stats["samples"] > 0:
                draw_text("STATISTICS", (0, 255, 255), bold=True)
                draw_text(f"  Samples: {stats['samples']}")
                draw_text(f"  EAR Mean: {stats['ear_mean']:.3f}")
                draw_text(f"  EAR Std: {stats['ear_std']:.3f}")
                draw_text(f"  Blinks: ~{stats['blink_count_estimate']}")
                draw_text(f"  Head Move: {stats['head_movement']:.2f}")

        # Controls at bottom
        y = h - 100
        draw_text("CONTROLS", (100, 100, 100))
        draw_text("  q: Quit", (100, 100, 100))
        draw_text("  s: Save snapshot", (100, 100, 100))
        draw_text("  d: Toggle debug", (100, 100, 100))
        draw_text("  r: Reset stats", (100, 100, 100))

        # Combine frame and panel
        combined = np.hstack([frame, panel])
        return combined

    def save_snapshot(self, frame: np.ndarray, metrics: FaceMetrics):
        """Save current frame and metrics"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save image
        img_path = os.path.join(self.output_dir, f"snapshot_{timestamp}.png")
        cv2.imwrite(img_path, frame)

        # Save metrics
        csv_path = os.path.join(self.output_dir, f"snapshot_{timestamp}.csv")
        data = self._metrics_to_dict(metrics)
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)

        # Save feature vector
        if metrics.feature_vector is not None:
            vec_path = os.path.join(self.output_dir, f"snapshot_{timestamp}_vector.npy")
            np.save(vec_path, metrics.feature_vector)

        print(f"Saved snapshot to {self.output_dir}/snapshot_{timestamp}.*")

    def export_history(self):
        """Export collected data to CSV"""
        if not self.metrics_history:
            print("No data to export")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = os.path.join(self.output_dir, f"history_{timestamp}.csv")

        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.metrics_history[0].keys())
            writer.writeheader()
            writer.writerows(self.metrics_history)

        print(f"Exported {len(self.metrics_history)} frames to {csv_path}")

        # Export feature vectors
        if self.feature_history:
            vectors = np.array(self.feature_history)
            vec_path = os.path.join(self.output_dir, f"features_{timestamp}.npy")
            np.save(vec_path, vectors)
            print(f"Exported feature vectors: {vectors.shape}")

    def run(self):
        """Main analysis loop"""
        print("\n" + "=" * 60)
        print("FACE VECTOR ANALYSIS TOOL")
        print("=" * 60)
        print("\nInitializing camera...")

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        print("Camera ready. Press 'q' to quit.\n")

        frame_times = []

        try:
            while True:
                start_time = time.time()

                ret, frame = cap.read()
                if not ret:
                    print("Failed to read frame")
                    break

                # Flip for mirror effect
                frame = cv2.flip(frame, 1)

                # Detect and analyze
                metrics = self.tracker.detect(frame)

                # Store history
                if metrics.detected:
                    self.metrics_history.append(self._metrics_to_dict(metrics))
                    if metrics.feature_vector is not None:
                        self.feature_history.append(metrics.feature_vector.copy())

                    # Limit history size
                    if len(self.metrics_history) > self.max_history:
                        self.metrics_history.pop(0)
                    if len(self.feature_history) > self.max_history:
                        self.feature_history.pop(0)

                # Calculate FPS
                frame_time = time.time() - start_time
                frame_times.append(frame_time)
                if len(frame_times) > 30:
                    frame_times.pop(0)
                fps = 1.0 / (sum(frame_times) / len(frame_times))

                # Draw debug overlay on frame
                if self.show_debug:
                    display_frame = self.tracker.draw_debug_overlay(
                        frame,
                        metrics,
                        show_mesh=self.show_mesh,
                        show_eyes=True,
                        show_iris=True,
                        show_metrics=False,  # Using side panel instead
                        show_pose=False,
                    )
                else:
                    display_frame = frame.copy()

                # Add analysis panel
                display = self._draw_analysis_panel(display_frame, metrics, fps)

                cv2.imshow("Face Vector Analysis", display)

                # Handle input
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("s"):
                    self.save_snapshot(frame, metrics)
                elif key == ord("r"):
                    self.tracker.ear_history.clear()
                    self.tracker.mar_history.clear()
                    self.tracker.pose_history.clear()
                    self.metrics_history.clear()
                    self.feature_history.clear()
                    print("Statistics reset")
                elif key == ord("d"):
                    self.show_debug = not self.show_debug
                    print(f"Debug overlay: {'ON' if self.show_debug else 'OFF'}")
                elif key == ord("m"):
                    self.show_mesh = not self.show_mesh
                    print(f"Mesh: {'ON' if self.show_mesh else 'OFF'}")
                elif key == ord("e"):
                    self.export_history()

        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.tracker.close()

            # Auto-export if we have data
            if len(self.metrics_history) > 10:
                print("\nAuto-exporting collected data...")
                self.export_history()

            print("\nAnalysis complete.")


def main():
    """Entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Face Vector Analysis Tool")
    parser.add_argument("--camera", "-c", type=int, default=0, help="Camera index")
    args = parser.parse_args()

    analyzer = FaceVectorAnalyzer(camera_index=args.camera)
    analyzer.run()


if __name__ == "__main__":
    main()
