#!/usr/bin/env python3
"""GestureCam - Application launcher."""

import os
import sys
import time


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_banner():
    print("=" * 50)
    print("       G E S T U R E C A M")
    print("=" * 50)
    print("Virtual Camera with Gesture Control")
    print()


def run_ai_camera():
    print("\nStarting AI Camera (Native UI)...")
    from gesturecam.ui.native_ui import run_demo

    run_demo()


def run_air_canvas():
    print("\nStarting AirCanvas...")
    from gesturecam.apps.air_canvas import main as run_canvas

    run_canvas()


def run_attendance():
    print("\nStarting Attendance System...")
    attendance_script = os.path.join(
        os.path.dirname(__file__), "attendance_system", "attendance_system.py"
    )
    if os.path.exists(attendance_script):
        os.system(f"{sys.executable} {attendance_script} --session demo")
    else:
        print(f"Script not found: {attendance_script}")
        time.sleep(2)


def main():
    while True:
        clear_screen()
        show_banner()
        print("Select a mode:")
        print("  [1] AI Camera (Auto-Framing & Zoom)")
        print("  [2] AirCanvas (Gesture Drawing)")
        print("  [3] Attendance System")
        print("  [4] Benchmark")
        print("  [Q] Quit")
        print()

        choice = input("Choice > ").upper()

        if choice == "1":
            run_ai_camera()
        elif choice == "2":
            run_air_canvas()
        elif choice == "3":
            run_attendance()
        elif choice == "4":
            os.system(f"{sys.executable} tests/benchmark_performance.py")
            input("\nPress Enter to continue...")
        elif choice == "Q":
            break
        else:
            print("Invalid option.")
            time.sleep(1)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
