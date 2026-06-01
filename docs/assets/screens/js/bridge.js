/**
 * GestureCam UI Bridge
 * Shared JavaScript for all screens - handles PyWebView API integration
 */

const GestureCam = {
  api: null,
  isReady: false,

  /**
   * Initialize the bridge - wait for PyWebView API
   */
  init: function (callback) {
    const self = this;

    function waitForApi() {
      if (window.pywebview && window.pywebview.api) {
        self.api = window.pywebview.api;
        self.isReady = true;
        console.log("GestureCam API connected");
        if (callback) callback(self.api);
      } else {
        setTimeout(waitForApi, 100);
      }
    }

    waitForApi();
  },

  /**
   * Navigate to a screen
   */
  navigateTo: function (screen) {
    const screens = {
      onboarding1: "onboarding_step1_privacy.html",
      onboarding2: "onboarding_step2_camera.html",
      onboarding3: "onboarding_step3_gestures.html",
      dashboard: "main_dashboard.html",
      settings: "settings_panel.html",
    };

    const url = screens[screen] || screen;
    window.location.href = url;
  },

  /**
   * Complete current onboarding step and navigate to next
   */
  completeOnboardingStep: function () {
    if (!this.api) {
      // Fallback: just navigate
      const currentStep = this.getCurrentOnboardingStep();
      if (currentStep < 3) {
        this.navigateTo("onboarding" + (currentStep + 1));
      } else {
        this.navigateTo("dashboard");
      }
      return;
    }

    this.api.complete_onboarding_step().then((result) => {
      console.log("Onboarding step completed:", result);
      if (result.complete) {
        this.navigateTo("dashboard");
      } else {
        this.navigateTo("onboarding" + result.currentStep);
      }
    });
  },

  /**
   * Go back to previous onboarding step
   */
  goBackOnboarding: function () {
    if (!this.api) {
      const currentStep = this.getCurrentOnboardingStep();
      if (currentStep > 1) {
        this.navigateTo("onboarding" + (currentStep - 1));
      }
      return;
    }

    this.api.go_back_onboarding().then((result) => {
      if (result.success) {
        this.navigateTo("onboarding" + result.currentStep);
      }
    });
  },

  /**
   * Get current onboarding step from URL
   */
  getCurrentOnboardingStep: function () {
    const url = window.location.href;
    if (url.includes("step1")) return 1;
    if (url.includes("step2")) return 2;
    if (url.includes("step3")) return 3;
    return 0;
  },

  /**
   * Window controls
   */
  minimizeWindow: function () {
    if (this.api) this.api.minimize_window();
  },

  closeWindow: function () {
    if (this.api) this.api.close_window();
  },

  /**
   * Framing modes
   */
  setFramingMode: function (mode) {
    if (this.api) {
      return this.api.set_framing_mode(mode);
    }
    return Promise.resolve({ success: false });
  },

  /**
   * Virtual camera
   */
  toggleVirtualCamera: function () {
    if (this.api) {
      return this.api.toggle_virtual_camera();
    }
    return Promise.resolve({ active: false });
  },

  /**
   * Get app state
   */
  getState: function () {
    if (this.api) {
      return this.api.get_app_state();
    }
    return Promise.resolve({
      state: "ready",
      virtualCameraActive: false,
      currentMode: "face_follow",
    });
  },

  /**
   * Get zoom level
   */
  getZoomLevel: function () {
    if (this.api) {
      return this.api.get_zoom_level();
    }
    return Promise.resolve({ current: 1.0, min: 1.0, max: 3.0 });
  },

  /**
   * Get available cameras
   */
  getAvailableCameras: function () {
    if (this.api) {
      return this.api.get_available_cameras();
    }
    return Promise.resolve([{ index: 0, name: "No camera detected" }]);
  },

  /**
   * Get available resolutions
   */
  getResolutions: function () {
    if (this.api) {
      return this.api.get_resolutions();
    }
    return Promise.resolve([
      { id: "720p", label: "720p (HD)" },
      { id: "1080p", label: "1080p (Full HD)" },
    ]);
  },

  /**
   * Select a camera
   */
  selectCamera: function (index) {
    if (this.api) {
      return this.api.select_camera(index);
    }
    return Promise.resolve({ success: false });
  },

  /**
   * Get settings
   */
  getSettings: function () {
    if (this.api) {
      return this.api.get_settings();
    }
    return Promise.resolve({});
  },

  /**
   * Update a setting
   */
  updateSetting: function (section, key, value) {
    if (this.api) {
      return this.api.update_settings(section, key, value);
    }
    return Promise.resolve({ success: false });
  },

  /**
   * Setup common event handlers
   */
  setupWindowControls: function () {
    const self = this;
    const controls = document.querySelectorAll("header .flex.gap-1 button");

    if (controls.length >= 3) {
      controls[0].addEventListener("click", () => self.minimizeWindow());
      controls[2].addEventListener("click", () => self.closeWindow());
    }
  },
};

// Auto-initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  GestureCam.init(function (api) {
    // Setup window controls
    GestureCam.setupWindowControls();

    // Dispatch ready event
    window.dispatchEvent(
      new CustomEvent("gesturecam:ready", { detail: { api: api } }),
    );
  });
});

// Export for use
window.GestureCam = GestureCam;
