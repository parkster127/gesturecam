#!/usr/bin/env python3
"""
GestureCam - Virtual Camera with Gesture Control
Main entry point for the desktop application.

Usage:
    python -m gesturecam          # Run the desktop app
    python -m gesturecam --cli    # Run in CLI mode (no GUI)
    python -m gesturecam --help   # Show help

"""

import sys
import argparse
import logging

from gesturecam.constants import APP_NAME, APP_VERSION


def setup_logging(debug: bool = False):
    """Configure logging for the application."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )


def run_cli_mode():
    """Run in CLI mode without GUI (for testing/debugging)."""
    from gesturecam.core.pipeline import GestureCamPipeline
    from gesturecam.config import Config
    
    print(f"\n{APP_NAME} v{APP_VERSION} - CLI Mode")
    print("=" * 40)
    print("Running in preview mode. Press 'q' to quit.\n")
    
    config = Config()
    pipeline = GestureCamPipeline(config)
    pipeline.run()


def run_desktop_app():
    """Run the full desktop application with GUI."""
    try:
        from gesturecam.ui.window import run_app
        run_app()
    except ImportError as e:
        print(f"\n❌ Error: Cannot start desktop app")
        print(f"   Missing dependency: {e}")
        print(f"\n   Install required packages with:")
        print(f"   pip install pywebview")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        prog="gesturecam",
        description=f"{APP_NAME} - Virtual camera with gesture control",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"{APP_NAME} {APP_VERSION}"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in CLI mode without GUI"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run the live camera test"
    )
    
    args = parser.parse_args()
    setup_logging(args.debug)
    
    if args.test:
        import subprocess
        subprocess.run([sys.executable, "tests/test_zoom_live.py"])
    elif args.cli:
        run_cli_mode()
    else:
        run_desktop_app()


if __name__ == "__main__":
    main()
