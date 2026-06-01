"""
GestureCam Main Window Manager
Creates and manages the native desktop window using PyWebView.
"""

import logging
from pathlib import Path
from typing import Optional

from gesturecam.constants import (
    APP_NAME, 
    WINDOW_DEFAULT_WIDTH, 
    WINDOW_DEFAULT_HEIGHT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
)
from gesturecam.settings import get_settings
from gesturecam.ui.api import GestureCamAPI

logger = logging.getLogger(__name__)

# Check if webview is available
try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False
    logger.warning("pywebview not installed. Desktop UI will not be available.")


class GestureCamWindow:
    """
    Main window manager for the GestureCam desktop application.
    Uses PyWebView to render HTML/CSS/JS in a native window.
    """
    
    def __init__(self):
        self._window = None
        self._api = GestureCamAPI()
        self._settings = get_settings()
        self._screens_dir = self._get_screens_dir()
        
        logger.info(f"Window manager initialized. Screens dir: {self._screens_dir}")
    
    def _get_screens_dir(self) -> Path:
        """Get the directory containing HTML screen files."""
        # In development, use docs/assets/screens
        project_root = Path(__file__).parent.parent.parent
        screens_dir = project_root / "docs" / "assets" / "screens"
        
        if screens_dir.exists():
            return screens_dir
        
        # Fallback to package directory
        package_screens = Path(__file__).parent / "screens"
        if package_screens.exists():
            return package_screens
        
        raise FileNotFoundError(f"Screens directory not found. Tried: {screens_dir}")
    
    def _get_screen_path(self, screen_name: str) -> str:
        """Get the full path to a screen HTML file."""
        html_file = self._screens_dir / screen_name
        if html_file.exists():
            return str(html_file)
        raise FileNotFoundError(f"Screen not found: {screen_name}")
    
    def _get_initial_screen(self) -> str:
        """Determine which screen to show first."""
        if self._settings.settings.first_run:
            return "onboarding_step1_privacy.html"
        return "main_dashboard.html"
    
    def run(self) -> None:
        """
        Start the application and show the main window.
        This blocks until the window is closed.
        """
        if not WEBVIEW_AVAILABLE:
            logger.error("Cannot run: pywebview is not installed")
            print("❌ Error: pywebview is not installed.")
            print("   Install it with: pip install pywebview")
            return
        
        try:
            initial_screen = self._get_initial_screen()
            initial_path = self._get_screen_path(initial_screen)
            
            logger.info(f"Starting window with: {initial_screen}")
            
            # Create the window
            self._window = webview.create_window(
                title=APP_NAME,
                url=initial_path,
                width=WINDOW_DEFAULT_WIDTH,
                height=WINDOW_DEFAULT_HEIGHT,
                min_size=(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT),
                js_api=self._api,
                resizable=True,
                frameless=False,  # Use native title bar
                easy_drag=False,
                background_color='#101122',
            )
            
            # Set window reference in API
            self._api.set_window(self._window)
            
            # Register event handlers
            self._window.events.loaded += self._on_loaded
            self._window.events.closing += self._on_closing
            
            # Start the webview event loop
            # SECURITY: debug=False prevents DevTools access
            webview.start(
                debug=False,  # DISABLED - no DevTools in production
                private_mode=False,  # Allow localStorage
            )
            
        except Exception as e:
            logger.error(f"Failed to start window: {e}")
            raise
    
    def _on_loaded(self):
        """Called when the HTML page is loaded."""
        logger.info("Window loaded")
        
        # Inject the bridge initialization script
        if self._window:
            self._window.evaluate_js("""
                console.log('GestureCam UI loaded');
                
                // Create global api reference for easier access
                window.api = window.pywebview.api;
                
                // Initialize the app
                if (window.api) {
                    window.api.initialize().then(result => {
                        console.log('App initialized:', result);
                        // Dispatch event for UI to react
                        window.dispatchEvent(new CustomEvent('gesturecam:ready', { detail: result }));
                    });
                }
            """)
    
    def _on_closing(self):
        """Called when the window is being closed."""
        logger.info("Window closing")
        from gesturecam.app import get_controller
        get_controller().shutdown()
    
    def navigate_to(self, screen_name: str) -> None:
        """Navigate to a different screen."""
        if self._window:
            try:
                screen_path = self._get_screen_path(screen_name)
                self._window.load_url(screen_path)
                logger.info(f"Navigated to: {screen_name}")
            except FileNotFoundError as e:
                logger.error(f"Navigation failed: {e}")
    
    def show_settings(self) -> None:
        """Show the settings panel."""
        self.navigate_to("settings_panel.html")
    
    def show_dashboard(self) -> None:
        """Show the main dashboard."""
        self.navigate_to("main_dashboard.html")
    
    def show_onboarding(self, step: int = 1) -> None:
        """Show a specific onboarding step."""
        screens = {
            1: "onboarding_step1_privacy.html",
            2: "onboarding_step2_camera.html",
            3: "onboarding_step3_gestures.html",
        }
        if step in screens:
            self.navigate_to(screens[step])


def run_app():
    """Main entry point for the desktop application."""
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    print(f"""
╔═══════════════════════════════════════════════╗
║                                               ║
║   🖐️  GestureCam Desktop Application          ║
║                                               ║
║   Control your camera with a simple 👍        ║
║                                               ║
╚═══════════════════════════════════════════════╝
""")
    
    try:
        window = GestureCamWindow()
        window.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    run_app()
