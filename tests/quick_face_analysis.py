#!/usr/bin/env python3
"""
Quick Face Analysis - Terminal Only
Analyzes your face vectors and prints results to terminal
"""

import cv2
import numpy as np
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesturecam.vision.face_mesh import FaceMeshTracker


def quick_analysis(num_frames=100, camera_index=0):
    """Quick analysis without GUI"""

    print("\n" + "=" * 60)
    print("QUICK FACE VECTOR ANALYSIS")
    print("=" * 60)
    print(f"\nCapturing {num_frames} frames...")
    print("Make sure your face is visible to the camera!")
    print("Press Ctrl+C to stop early\n")

    tracker = FaceMeshTracker(
        min_detection_confidence=0.5, min_tracking_confidence=0.5, refine_landmarks=True
    )

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("ERROR: Could not open camera")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # Collect data
    ear_left = []
    ear_right = []
    ear_avg = []
    mar_values = []
    pitch_values = []
    yaw_values = []
    roll_values = []
    detected_count = 0

    try:
        for i in range(num_frames):
            ret, frame = cap.read()
            if not ret:
                print(f"Failed to read frame {i}")
                continue

            frame = cv2.flip(frame, 1)
            metrics = tracker.detect(frame)

            if metrics.detected:
                detected_count += 1
                ear_left.append(metrics.left_eye.ear)
                ear_right.append(metrics.right_eye.ear)
                ear_avg.append(metrics.avg_ear)
                mar_values.append(metrics.mar)
                pitch_values.append(metrics.pitch)
                yaw_values.append(metrics.yaw)
                roll_values.append(metrics.roll)

            # Progress indicator
            if (i + 1) % 10 == 0:
                print(
                    f"  Progress: {i + 1}/{num_frames} frames ({detected_count} detected)"
                )

            time.sleep(0.03)  # ~30 FPS

    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        cap.release()
        tracker.close()

    # Analysis
    print("\n" + "=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)

    print(
        f"\nDetection Rate: {detected_count}/{num_frames} ({detected_count / num_frames * 100:.1f}%)"
    )

    if detected_count == 0:
        print("\nNo faces detected!")
        print("Tips:")
        print("  - Improve lighting")
        print("  - Move closer to camera")
        print("  - Ensure face is fully visible")
        return

    # EAR Analysis
    print("\n--- EYE ASPECT RATIO (EAR) ---")
    print(f"Left Eye:")
    print(f"  Mean: {np.mean(ear_left):.4f}")
    print(f"  Std:  {np.std(ear_left):.4f}")
    print(f"  Min:  {np.min(ear_left):.4f}")
    print(f"  Max:  {np.max(ear_left):.4f}")

    print(f"\nRight Eye:")
    print(f"  Mean: {np.mean(ear_right):.4f}")
    print(f"  Std:  {np.std(ear_right):.4f}")
    print(f"  Min:  {np.min(ear_right):.4f}")
    print(f"  Max:  {np.max(ear_right):.4f}")

    print(f"\nAverage EAR:")
    print(f"  Mean: {np.mean(ear_avg):.4f}")
    print(f"  Std:  {np.std(ear_avg):.4f}")

    # Asymmetry
    asymmetry = abs(np.mean(ear_left) - np.mean(ear_right))
    print(f"\nEye Asymmetry: {asymmetry:.4f}")
    if asymmetry > 0.05:
        print("  ⚠️  High asymmetry detected - may indicate:")
        print("      - Uneven lighting")
        print("      - Head tilt")
        print("      - Natural eye differences")
    else:
        print("  ✓ Low asymmetry (good)")

    # Variability
    print(f"\nEAR Variability:")
    if np.std(ear_avg) < 0.02:
        print(f"  ⚠️  Very low ({np.std(ear_avg):.4f}) - detection may be struggling")
        print("      Try:")
        print("      - Better lighting")
        print("      - Different camera angle")
        print("      - Adjust distance to camera")
    elif np.std(ear_avg) > 0.10:
        print(f"  ⚠️  Very high ({np.std(ear_avg):.4f}) - too much movement or blinking")
    else:
        print(f"  ✓ Normal ({np.std(ear_avg):.4f})")

    # Head Pose
    print("\n--- HEAD POSE ---")
    pose_working = not (
        np.all(np.array(pitch_values) == 0) and np.all(np.array(yaw_values) == 0)
    )

    if pose_working:
        print(
            f"Pitch (nodding): {np.mean(pitch_values):.1f}° ± {np.std(pitch_values):.1f}°"
        )
        print(
            f"Yaw (turning):   {np.mean(yaw_values):.1f}° ± {np.std(yaw_values):.1f}°"
        )
        print(
            f"Roll (tilting):  {np.mean(roll_values):.1f}° ± {np.std(roll_values):.1f}°"
        )
    else:
        print("⚠️  Head pose estimation not working")
        print("    This is a known issue with some MediaPipe versions")

    # Recommendations
    print("\n--- RECOMMENDATIONS ---")

    if detected_count / num_frames < 0.8:
        print("❌ Low detection rate")
        print("   → Improve lighting")
        print("   → Position camera at eye level")
        print("   → Ensure face fully visible")

    if np.std(ear_avg) < 0.02:
        print("❌ EAR variation too low for reliable detection")
        print("   → This is likely your lighting/setup issue")
        print("   → Try:")
        print("      1. Add light source in front of you")
        print("      2. Avoid backlighting")
        print("      3. Increase camera resolution")
        print("      4. Try different time of day")
    elif np.mean(ear_avg) < 0.15:
        print("⚠️  Very low EAR values")
        print("   → Eyes may be too small in frame")
        print("   → Move closer to camera")
    elif np.mean(ear_avg) > 0.35:
        print("⚠️  Very high EAR values")
        print("   → Unusual - may indicate detection issues")
    else:
        print("✓ EAR values in normal range")
        print("✓ Detection quality looks good!")

    # Suggest optimal threshold
    if detected_count > 10:
        # Calculate optimal threshold based on distribution
        threshold_suggestion = np.mean(ear_avg) - 2 * np.std(ear_avg)
        threshold_suggestion = max(0.15, min(0.30, threshold_suggestion))

        print(f"\n💡 SUGGESTED EAR THRESHOLD: {threshold_suggestion:.3f}")
        print(f"   (Current default: 0.21)")
        print(f"   Your mean EAR: {np.mean(ear_avg):.3f}")
        print(f"   This threshold is 2 std deviations below your mean")

    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--frames", "-n", type=int, default=100, help="Number of frames to analyze"
    )
    parser.add_argument("--camera", "-c", type=int, default=0, help="Camera index")
    args = parser.parse_args()

    quick_analysis(num_frames=args.frames, camera_index=args.camera)
