#!/usr/bin/env python3
"""
Face Vector Data Analysis Script

Analyzes exported data from the face vector analyzer.
Provides statistical insights and visualizations for understanding
your face detection patterns.

Usage:
    python -m tests.analyze_exported_data [--file history_XXXXXX.csv]
"""

import glob
import os
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Find latest export file
def find_latest_export(directory="analysis_output"):
    """Find the most recent exported CSV file"""
    pattern = os.path.join(directory, "history_*.csv")
    files = glob.glob(pattern)
    if not files:
        return None
    return max(files, key=os.path.getctime)


def load_feature_vectors(directory="analysis_output"):
    """Load the most recent feature vector file"""
    pattern = os.path.join(directory, "features_*.npy")
    files = glob.glob(pattern)
    if not files:
        return None
    latest = max(files, key=os.path.getctime)
    return np.load(latest)


def analyze_eye_patterns(df: pd.DataFrame) -> dict:
    """Analyze eye detection patterns"""
    results = {
        "total_frames": len(df),
        "detected_frames": df["detected"].sum(),
        "detection_rate": df["detected"].mean() * 100,
    }

    # Filter to detected frames only
    detected = df[df["detected"]]

    if len(detected) == 0:
        return results

    # EAR statistics
    results["ear_stats"] = {
        "left_mean": detected["left_ear"].mean(),
        "left_std": detected["left_ear"].std(),
        "right_mean": detected["right_ear"].mean(),
        "right_std": detected["right_ear"].std(),
        "avg_mean": detected["avg_ear"].mean(),
        "avg_std": detected["avg_ear"].std(),
        "left_right_correlation": detected["left_ear"].corr(detected["right_ear"]),
    }

    # Eye openness patterns
    results["eye_openness"] = {
        "left_open_rate": detected["left_eye_open"].mean() * 100,
        "right_open_rate": detected["right_eye_open"].mean() * 100,
        "both_open_rate": (
            (detected["left_eye_open"]) & (detected["right_eye_open"])
        ).mean()
        * 100,
        "both_closed_rate": (
            (~detected["left_eye_open"]) & (~detected["right_eye_open"])
        ).mean()
        * 100,
    }

    # Estimate blink count (EAR drops below threshold)
    threshold = 0.21
    blinks = 0
    prev_open = True
    for ear in detected["avg_ear"]:
        currently_open = ear > threshold
        if prev_open and not currently_open:
            blinks += 1
        prev_open = currently_open
    results["estimated_blinks"] = blinks

    return results


def analyze_head_pose(df: pd.DataFrame) -> dict:
    """Analyze head pose patterns"""
    detected = df[df["detected"]]

    if len(detected) == 0:
        return {}

    results = {
        "pitch": {
            "mean": detected["pitch"].mean(),
            "std": detected["pitch"].std(),
            "min": detected["pitch"].min(),
            "max": detected["pitch"].max(),
        },
        "yaw": {
            "mean": detected["yaw"].mean(),
            "std": detected["yaw"].std(),
            "min": detected["yaw"].min(),
            "max": detected["yaw"].max(),
        },
        "roll": {
            "mean": detected["roll"].mean(),
            "std": detected["roll"].std(),
            "min": detected["roll"].min(),
            "max": detected["roll"].max(),
        },
    }

    # Head stability score (lower std = more stable)
    stability = 100 - min(
        100,
        (results["pitch"]["std"] + results["yaw"]["std"] + results["roll"]["std"]) * 2,
    )
    results["stability_score"] = max(0, stability)

    return results


def analyze_detection_quality(df: pd.DataFrame) -> dict:
    """Analyze overall detection quality"""
    detected = df[df["detected"]]

    if len(detected) == 0:
        return {"quality_score": 0, "issues": ["No faces detected"]}

    issues = []
    score = 100

    # Check detection rate
    detection_rate = df["detected"].mean()
    if detection_rate < 0.9:
        score -= 20
        issues.append(f"Low detection rate ({detection_rate * 100:.1f}%)")

    # Check EAR variance
    ear_std = detected["avg_ear"].std()
    if ear_std < 0.02:
        score -= 15
        issues.append("Very low EAR variance - may indicate detection issues")

    # Check head pose variance
    pose_variance = (
        detected["pitch"].std() + detected["yaw"].std() + detected["roll"].std()
    )
    if pose_variance > 30:
        score -= 10
        issues.append("High head movement - may affect tracking accuracy")

    # Check for asymmetry
    ear_diff = abs(detected["left_ear"].mean() - detected["right_ear"].mean())
    if ear_diff > 0.05:
        issues.append(f"Eye asymmetry detected (diff: {ear_diff:.3f})")

    return {
        "quality_score": max(0, score),
        "issues": issues if issues else ["No significant issues detected"],
    }


def plot_ear_timeline(df: pd.DataFrame, output_path: str = None):
    """Plot EAR over time"""
    detected = df[df["detected"]].copy()

    if len(detected) == 0:
        print("No data to plot")
        return

    # Create frame index
    detected["frame"] = range(len(detected))

    fig, axes = plt.subplots(2, 1, figsize=(14, 8))

    # EAR over time
    ax1 = axes[0]
    ax1.plot(detected["frame"], detected["left_ear"], "g-", alpha=0.7, label="Left EAR")
    ax1.plot(
        detected["frame"], detected["right_ear"], "b-", alpha=0.7, label="Right EAR"
    )
    ax1.plot(
        detected["frame"], detected["avg_ear"], "r-", linewidth=2, label="Average EAR"
    )
    ax1.axhline(y=0.21, color="orange", linestyle="--", label="Blink Threshold")
    ax1.set_xlabel("Frame")
    ax1.set_ylabel("Eye Aspect Ratio (EAR)")
    ax1.set_title("Eye Aspect Ratio Over Time")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # EAR distribution
    ax2 = axes[1]
    ax2.hist(detected["left_ear"], bins=50, alpha=0.5, label="Left EAR", color="green")
    ax2.hist(detected["right_ear"], bins=50, alpha=0.5, label="Right EAR", color="blue")
    ax2.axvline(x=0.21, color="orange", linestyle="--", label="Blink Threshold")
    ax2.set_xlabel("EAR Value")
    ax2.set_ylabel("Frequency")
    ax2.set_title("EAR Distribution")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Saved plot to {output_path}")
    else:
        plt.show()


def plot_head_pose(df: pd.DataFrame, output_path: str = None):
    """Plot head pose analysis"""
    detected = df[df["detected"]].copy()

    if len(detected) == 0:
        print("No data to plot")
        return

    detected["frame"] = range(len(detected))

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Pose over time
    ax1 = axes[0, 0]
    ax1.plot(detected["frame"], detected["pitch"], "r-", alpha=0.7, label="Pitch")
    ax1.plot(detected["frame"], detected["yaw"], "g-", alpha=0.7, label="Yaw")
    ax1.plot(detected["frame"], detected["roll"], "b-", alpha=0.7, label="Roll")
    ax1.set_xlabel("Frame")
    ax1.set_ylabel("Angle (degrees)")
    ax1.set_title("Head Pose Over Time")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Pitch vs Yaw scatter
    ax2 = axes[0, 1]
    ax2.scatter(
        detected["yaw"],
        detected["pitch"],
        c=detected["frame"],
        cmap="viridis",
        alpha=0.5,
        s=5,
    )
    ax2.set_xlabel("Yaw (degrees)")
    ax2.set_ylabel("Pitch (degrees)")
    ax2.set_title("Head Pose Distribution (color = time)")
    ax2.axhline(y=0, color="gray", linestyle="-", alpha=0.3)
    ax2.axvline(x=0, color="gray", linestyle="-", alpha=0.3)
    ax2.grid(True, alpha=0.3)

    # Pose distributions
    ax3 = axes[1, 0]
    ax3.hist(detected["pitch"], bins=50, alpha=0.5, label="Pitch", color="red")
    ax3.hist(detected["yaw"], bins=50, alpha=0.5, label="Yaw", color="green")
    ax3.hist(detected["roll"], bins=50, alpha=0.5, label="Roll", color="blue")
    ax3.set_xlabel("Angle (degrees)")
    ax3.set_ylabel("Frequency")
    ax3.set_title("Head Pose Distributions")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    # Face position heatmap
    ax4 = axes[1, 1]
    if "center_x" in detected.columns and "center_y" in detected.columns:
        hb = ax4.hexbin(
            detected["center_x"], detected["center_y"], gridsize=30, cmap="YlOrRd"
        )
        ax4.set_xlabel("X Position")
        ax4.set_ylabel("Y Position")
        ax4.set_title("Face Position Heatmap")
        ax4.invert_yaxis()  # Image coordinates
        plt.colorbar(hb, ax=ax4, label="Count")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Saved plot to {output_path}")
    else:
        plt.show()


def generate_report(df: pd.DataFrame) -> str:
    """Generate a text report of the analysis"""
    eye_analysis = analyze_eye_patterns(df)
    pose_analysis = analyze_head_pose(df)
    quality = analyze_detection_quality(df)

    report = []
    report.append("=" * 60)
    report.append("FACE VECTOR ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    report.append("\n\n--- DETECTION SUMMARY ---")
    report.append(f"Total frames analyzed: {eye_analysis['total_frames']}")
    report.append(f"Frames with detection: {eye_analysis['detected_frames']}")
    report.append(f"Detection rate: {eye_analysis['detection_rate']:.1f}%")

    if "ear_stats" in eye_analysis:
        report.append("\n\n--- EYE ANALYSIS ---")
        stats = eye_analysis["ear_stats"]
        report.append(
            f"Left EAR:  Mean={stats['left_mean']:.3f}, Std={stats['left_std']:.3f}"
        )
        report.append(
            f"Right EAR: Mean={stats['right_mean']:.3f}, Std={stats['right_std']:.3f}"
        )
        report.append(
            f"Average EAR: Mean={stats['avg_mean']:.3f}, Std={stats['avg_std']:.3f}"
        )
        report.append(f"Left-Right Correlation: {stats['left_right_correlation']:.3f}")

        openness = eye_analysis["eye_openness"]
        report.append("\nEye Openness:")
        report.append(f"  Left eye open: {openness['left_open_rate']:.1f}%")
        report.append(f"  Right eye open: {openness['right_open_rate']:.1f}%")
        report.append(f"  Both eyes open: {openness['both_open_rate']:.1f}%")
        report.append(f"  Estimated blinks: {eye_analysis['estimated_blinks']}")

    if pose_analysis:
        report.append("\n\n--- HEAD POSE ANALYSIS ---")
        for axis in ["pitch", "yaw", "roll"]:
            stats = pose_analysis[axis]
            report.append(
                f"{axis.capitalize()}: Mean={stats['mean']:.1f}, Std={stats['std']:.1f}, Range=[{stats['min']:.1f}, {stats['max']:.1f}]"
            )
        report.append(
            f"\nHead Stability Score: {pose_analysis['stability_score']:.1f}/100"
        )

    report.append("\n\n--- QUALITY ASSESSMENT ---")
    report.append(f"Overall Quality Score: {quality['quality_score']}/100")
    report.append("Issues/Notes:")
    for issue in quality["issues"]:
        report.append(f"  - {issue}")

    report.append("\n\n--- RECOMMENDATIONS ---")
    if quality["quality_score"] >= 80:
        report.append("  Detection quality is good!")
    else:
        report.append("  Consider the following improvements:")
        if eye_analysis.get("detection_rate", 0) < 90:
            report.append("  - Improve lighting conditions")
            report.append("  - Position camera at eye level")
            report.append("  - Ensure face is fully visible")
        if "ear_stats" in eye_analysis and eye_analysis["ear_stats"]["avg_std"] < 0.02:
            report.append("  - Run calibration tool to set personal thresholds")

    report.append("\n" + "=" * 60)

    return "\n".join(report)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze exported face vector data")
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="CSV file to analyze (uses latest if not specified)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="analysis_output",
        help="Output directory for plots",
    )
    parser.add_argument("--no-plot", action="store_true", help="Skip generating plots")
    args = parser.parse_args()

    # Find file to analyze
    if args.file:
        csv_path = args.file
    else:
        csv_path = find_latest_export()

    if not csv_path or not os.path.exists(csv_path):
        print(
            "No export file found. Run analyze_face_vectors.py first to collect data."
        )
        print("Looking in: analysis_output/history_*.csv")
        return

    print(f"Analyzing: {csv_path}")

    # Load data
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} frames")

    # Generate and print report
    report = generate_report(df)
    print(report)

    # Save report
    report_path = os.path.join(args.output, "analysis_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")

    # Generate plots
    if not args.no_plot:
        try:
            print("\nGenerating plots...")
            plot_ear_timeline(df, os.path.join(args.output, "ear_analysis.png"))
            plot_head_pose(df, os.path.join(args.output, "pose_analysis.png"))
            print("Plots saved!")
        except Exception as e:
            print(f"Could not generate plots: {e}")
            print("Install matplotlib: pip install matplotlib")


if __name__ == "__main__":
    main()
