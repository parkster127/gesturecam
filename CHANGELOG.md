# Changelog

All notable changes to GestureCam will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial open-source release
- MIT License
- Comprehensive documentation (README, ARCHITECTURE, CONTRIBUTING)
- Multi-gesture support (thumbs up/down, peace sign, pinch, wink)
- Face mesh detection with 468 landmarks
- Automatic face framing with multiple modes
- Virtual camera output for OBS integration
- Dual UI: Native desktop (Dear PyGui) + Web (NiceGUI)
- AirCanvas drawing application
- Attendance system with facial recognition
- Performance benchmark tool
- Configuration system with JSON persistence
- Comprehensive test suite

### Changed
- Refactored camera abstraction layer
- Improved gesture recognition accuracy
- Enhanced zoom smoothing algorithm
- Optimized frame processing pipeline

### Fixed
- Camera initialization issues on macOS
- Virtual camera connection stability
- Memory leak in continuous operation
- Gesture detection under low light conditions

## [0.1.0] - 2024-XX-XX

### Added
- Initial prototype
- Hand gesture detection using MediaPipe
- Face mesh detection
- Basic zoom control
- Native UI with Dear PyGui
- Web UI with NiceGUI
- OBS virtual camera integration
- Multiple framing modes
- Calibration profiles
- Debug overlay
- Configuration management

---

## Version Classification

- **Major**: Breaking changes, API modifications
- **Minor**: New features, backward-compatible
- **Patch**: Bug fixes, documentation updates