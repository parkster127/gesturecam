# 🖐️ GestureCam - Features

> **Control your camera with a simple gesture.** Professional virtual camera software with AI-powered zoom control and auto-framing.

---

## ✨ Core Features

### 👍 Gesture-Controlled Zoom

Control zoom level with simple hand gestures—no clicking, no scrolling.

| Gesture        | Action              |
| -------------- | ------------------- |
| 👍 Thumbs Up   | Zoom In             |
| 👎 Thumbs Down | Zoom Out / Reset    |
| 🖐️ Open Palm   | Hold current zoom   |
| ✊ Fist        | Neutral (no action) |

**Technical Details:**

- Sub-20ms gesture recognition latency
- Works with one or two hands
- Adjustable sensitivity and detection confidence
- Gestures processed 100% locally on-device

---

### 🎯 Intelligent Auto-Framing

Professional framing modes that keep you perfectly composed—automatically.

| Mode            | Description                                | Best For                 |
| --------------- | ------------------------------------------ | ------------------------ |
| **Manual**      | Full manual control                        | Custom compositions      |
| **Face Follow** | Camera smoothly follows your face          | Movement, standing desks |
| **Headshot**    | Professional head framing (rule of thirds) | Interviews, podcasts     |
| **Shirt-Up**    | Shows from chest up                        | Presentations, tutorials |

**Technical Details:**

- Smooth EMA-based tracking (no jitter)
- Adjustable tracking speed
- Works with any face angle
- Maintains framing during zoom

---

### 📷 Virtual Camera Output

GestureCam creates a virtual camera that works with any app—OBS, Zoom, Meet, Teams, and more.

**Supported Platforms:**

- ✅ macOS (OBS Virtual Camera)
- ✅ Windows (OBS / Unity Capture)
- ✅ Linux (v4l2loopback)

**Output Options:**

- 720p, 1080p, 1440p, 4K resolutions
- 24, 30, 60 FPS
- Custom device name
- Hardware-accelerated processing

---

## 🔒 Privacy First

**100% Local Processing.** No cloud. No servers. Your video never leaves your device.

| Feature            | Status                             |
| ------------------ | ---------------------------------- |
| Local AI inference | ✅ MediaPipe on-device             |
| Cloud upload       | ❌ Never                           |
| Data collection    | ❌ None                            |
| Telemetry          | 📊 Anonymous usage only (optional) |

---

## 📱 Camera Compatibility

Works with any camera your OS can see:

- **Built-in webcams** (MacBook, laptop cameras)
- **iPhone Continuity Camera** (use your iPhone as a webcam)
- **USB webcams** (Logitech, Razer, Elgato, etc.)
- **Capture cards** (HDMI cameras, DSLRs via capture)
- **Virtual cameras** (OBS output, NDI sources)

**Pro Tip:** Use your iPhone as input → GestureCam processes → Virtual Camera to OBS. Best quality setup! 📸

---

## 🎨 Interface

### Desktop Application

- Native macOS, Windows, and Linux apps
- Dark mode optimized UI
- Real-time camera preview
- On-screen gesture indicator
- Zoom level HUD
- Status bar with latency monitoring

### Keyboard Shortcuts

| Shortcut            | Action                |
| ------------------- | --------------------- |
| `Ctrl+Shift+C`      | Toggle virtual camera |
| `Ctrl+Shift+G`      | Toggle gestures       |
| `Ctrl+0`            | Reset zoom            |
| `Ctrl+=` / `Ctrl+-` | Zoom in/out           |
| `Ctrl+1-4`          | Switch framing modes  |
| `Ctrl+,`            | Open settings         |

---

## ⚡ Performance

| Metric           | Value                    |
| ---------------- | ------------------------ |
| Gesture latency  | < 20ms                   |
| Tracking latency | < 15ms                   |
| CPU usage        | ~5-10% (optimized)       |
| GPU acceleration | ✅ Apple Silicon, NVIDIA |
| Memory footprint | ~200MB                   |

---

## 🌍 Languages

- 🇺🇸 English
- 🇪🇸 Español

---

## 🔧 Technical Stack

| Component        | Technology          |
| ---------------- | ------------------- |
| Hand detection   | MediaPipe Hands     |
| Face detection   | MediaPipe BlazeFace |
| Video processing | OpenCV              |
| Desktop app      | PyWebView + Python  |
| UI               | HTML/CSS/Tailwind   |
| Virtual camera   | pyvirtualcam        |

---

## 📋 System Requirements

**Minimum:**

- macOS 12+ / Windows 10 / Linux (Ubuntu 20.04+)
- 4GB RAM
- Any webcam

**Recommended:**

- macOS 14+ with Apple Silicon
- 8GB RAM
- 1080p webcam or iPhone Continuity Camera
- OBS Virtual Camera plugin installed

---

## 🚀 Use Cases

### Content Creators

- Stream with dynamic zoom reactions
- Hands-free camera control while gaming
- Professional framing without a cameraman

### Remote Workers

- Look professional in every video call
- Automatic framing in standup meetings
- Gesture controls for presentations

### Educators & Presenters

- Zoom in on materials naturally
- Keep face in frame while writing
- Engage audience with dynamic framing

### Podcasters & Interviewers

- Consistent professional framing
- React naturally with gesture zoom
- Multi-camera switching ready

---

## 💎 Coming Soon

- [ ] Multi-person tracking
- [ ] Custom gesture mappings
- [ ] Scene presets
- [ ] Keyboard shortcuts overlay
- [ ] iOS/Android companion app
- [ ] Stream Deck integration

---

<p align="center">
  <strong>GestureCam</strong><br>
  <em>Control your camera. With a gesture.</em>
</p>
