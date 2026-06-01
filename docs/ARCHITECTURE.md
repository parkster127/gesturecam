# GestureCam Architecture

## System Overview

GestureCam is a modular computer vision platform that transforms webcam input into a controllable virtual camera output. The system uses a pipeline architecture where each stage is responsible for a specific transformation.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Application Layer                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Native UI    │  │ Web UI       │  │ Attendance System│  │
│  │ (Dear PyGui) │  │ (NiceGUI)    │  │ (Face Rec)       │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         Core Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Pipeline     │  │ Zoom Engine  │  │ Framing Engine   │  │
│  │ Orchestrator │  │              │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       Vision Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Hand Detector│  │ Face Mesh    │  │ Gesture Engine   │  │
│  │ (MediaPipe)  │  │ (468 pts)    │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Hardware Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Camera Source│  │ Virtual Cam  │  │ Calibration Data │  │
│  │ (OpenCV)     │  │ (OBS/Teams)  │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Camera Layer (`gesturecam/camera/`)

**Purpose**: Abstract camera input/output operations

**Key Classes**:

```python
class CameraOperator:
    """Main camera controller managing source and virtual camera."""

    def get_frame(self) -> np.ndarray:
        """Get frame from physical camera."""

    def send_frame(self, frame: np.ndarray):
        """Send processed frame to virtual camera."""
```

**Responsibilities**:
- Camera source enumeration and selection
- Frame capture at specified FPS
- Virtual camera output (OBS integration)
- Camera property management (exposure, focus, etc.)

**Flow**:
```
Physical Camera → Frame Capture → Processing → Virtual Camera Output
```

### 2. Vision Layer (`gesturecam/vision/`)

**Purpose**: Computer vision detection using MediaPipe

**Components**:

#### Hand Detection (`hands.py`)

```python
class HandDetector:
    """Detect and track hand landmarks using MediaPipe."""

    def detect(self, frame: np.ndarray) -> List[HandResult]:
        """
        Returns:
            List of HandResult with 21 landmarks per hand
        """
```

**Features**:
- Multi-hand detection (up to 2 hands)
- 21-point hand landmark extraction
- Real-time tracking at 30+ FPS
- Confidence filtering

#### Face Mesh (`face_mesh.py`)

```python
class FaceMeshDetector:
    """Detect detailed face mesh with 468 landmarks."""

    def detect(self, frame: np.ndarray) -> FaceResult:
        """
        Returns:
            FaceResult with 468 landmarks + bounding box
        """
```

**Features**:
- 468-point face mesh
- Iris detection (478 landmarks total)
- Face bounding box calculation
- Eye blink detection (EAR threshold)
- Mouth open detection (MAR threshold)

#### Gesture Recognition (`gestures.py`)

```python
class GestureRecognizer:
    """Recognize hand gestures from landmarks."""

    def recognize(self, landmarks: list) -> Optional[Gesture]:
        """
        Recognized gestures:
        - Thumbs Up/Down
        - Peace Sign
        - Pinch (2 hands)
        - Wink (via face mesh)
        """
```

**Gesture Detection Logic**:

```python
# Thumbs Up Detection
def is_thumbs_up(landmarks) -> bool:
    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]
    other_fingers_up = all(
        landmarks[i].y < landmarks[i-2].y
        for i in [8, 12, 16, 20]
    )
    return thumb_tip.y < thumb_ip.y and other_fingers_up

# Pinch Detection
def detect_pinch(landmarks_a, landmarks_b) -> Optional[float]:
    distance = euclidean(
        landmarks_a[8],  # Index tip
        landmarks_b[8]   # Index tip (other hand)
    )
    return distance if 30 < distance < 150 else None
```

### 3. Core Layer (`gesturecam/core/`)

**Purpose**: Core computer vision logic and transformation

#### Pipeline (`pipeline.py`)

```python
class Pipeline:
    """Main processing pipeline orchestrating all stages."""

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process frame through all stages."""
        # 1. Detect hands
        # 2. Detect face
        # 3. Recognize gestures
        # 4. Apply transformations
        # 5. Return processed frame
```

**Processing Stages**:

```python
Raw Frame
    ↓
[Stage 1] Hand Detection → Hand Landmarks
    ↓
[Stage 2] Face Detection → Face Mesh + Bounding Box
    ↓
[Stage 3] Gesture Recognition → Gesture Events
    ↓
[Stage 4] Action Dispatch → Zoom/Pan/Framing commands
    ↓
[Stage 5] Transformations → Apply zoom/pan/crop
    ↓
Output Frame
```

#### Zoom Engine (`zoom.py`)

```python
class ZoomEngine:
    """Smooth zoom with exponential smoothing."""

    def set_zoom(self, target_zoom: float):
        """Set target zoom level (smoothed)."""

    def apply(self, frame: np.ndarray, zoom: float) -> np.ndarray:
        """Apply zoom to frame."""
```

**Zoom Smoothing Algorithm**:

```python
# Exponential moving average
current_zoom = (current_zoom * (1 - smoothing)) + (target_zoom * smoothing)
# smoothing = 0.1 means 10% new value, 90% old value
```

**Zoom Implementation**:

```python
def apply_zoom(frame, zoom_level):
    h, w = frame.shape[:2]
    new_h, new_w = int(h / zoom_level), int(w / zoom_level)

    # Calculate crop region (centered)
    y1 = (h - new_h) // 2
    y2 = y1 + new_h
    x1 = (w - new_w) // 2
    x2 = x1 + new_w

    # Crop and resize back
    cropped = frame[y1:y2, x1:x2]
    return cv2.resize(cropped, (w, h))
```

#### Framing Engine (`framing.py`)

```python
class FramingEngine:
    """Automatic face framing and tracking."""

    def frame_face(self, face_bbox: BBox) -> Transform:
        """Calculate transform to frame face."""
        # Calculate pan to center face
        # Calculate zoom based on face size
        # Return transformation matrix
```

**Framing Modes**:

| Mode | Behavior | Zoom Level |
|------|----------|-----------|
| Manual | No auto-tracking | User-controlled |
| Face Follow | Track face with smoothing | 1.0x - 1.5x |
| Headshot | Frame on head area | 1.5x - 2.0x |
| Shirt-Up | Frame from chest up | 1.0x - 1.2x |

**Framing Algorithm**:

```python
def calculate_framing(face_bbox, frame_size):
    # Calculate face center
    face_center = (
        (face_bbox.x1 + face_bbox.x2) / 2,
        (face_bbox.y1 + face_bbox.y2) / 2
    )

    # Calculate offset from frame center
    frame_center = (frame_size[0] / 2, frame_size[1] / 2)
    offset = (
        frame_center[0] - face_center[0],
        frame_center[1] - face_center[1]
    )

    # Smooth movement
    offset = apply_smoothing(offset)

    return offset
```

### 4. UI Layer (`gesturecam/ui/`)

**Purpose**: User interfaces for interaction

#### Native UI (`native_ui.py`)

```python
class NativeUI:
    """Dear PyGui-based desktop application."""

    def render(self):
        """Render UI components."""
        # Camera preview
        # Control buttons
        # Zoom slider
        # Settings panel
```

**Features**:
- Real-time camera preview
- Gesture control overlay
- Zoom slider (1.0x - 3.0x)
- Framing mode selector
- Settings panel
- Debug overlay

#### Web UI (`web_ui.py`)

```python
class WebUI:
    """NiceGUI-based web application."""

    async def run(self):
        """Run web server on localhost:8080."""
```

**Features**:
- Browser-based interface
- Mobile-friendly
- WebSocket for real-time updates
- Remote camera control

### 5. Interaction Layer (`gesturecam/interactions/`)

**Purpose**: Handle gesture interactions and drawing

#### Drawing (`drawing.py`)

```python
class DrawingEngine:
    """AirCanvas drawing using hand gestures."""

    def draw(self, gesture: Gesture, position: tuple):
        """Draw based on gesture and hand position."""
```

## Data Flow

### Frame Processing Flow

```python
# 1. Capture Frame
raw_frame = camera_operator.get_frame()

# 2. Detect Hands
hand_results = hand_detector.detect(raw_frame)

# 3. Detect Face Mesh
face_result = face_mesh_detector.detect(raw_frame)

# 4. Recognize Gestures
gestures = [
    gesture_recognize.recognize(hand.landmarks)
    for hand in hand_results
]

# 5. Dispatch Actions
for gesture in gestures:
    action_dispatcher.dispatch(gesture)

# 6. Apply Transformations
transformed_frame = apply_transformations(
    raw_frame,
    zoom_level,
    pan_offset,
    framing_mode
)

# 7. Send to Virtual Camera
camera_operator.send_frame(transformed_frame)

# 8. Update UI
ui.update_frame(transformed_frame)
ui.update_overlay(gestures, face_result)
```

### Gesture Event Flow

```python
User makes gesture
    ↓
MediaPipe detects landmarks
    ↓
GestureRecognizer classifies gesture
    ↓
GestureEvent emitted
    ↓
ActionDispatcher receives event
    ↓
Target component updated (ZoomEngine, FramingEngine, etc.)
    ↓
Change reflected in next frame
```

## Configuration System

**Location**: `gesturecam/config.py`

```python
@dataclass
class Config:
    # Camera Settings
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 1280
    CAMERA_HEIGHT: int = 720
    FPS: int = 30

    # Detection Confidence
    HAND_DETECTION_CONFIDENCE: float = 0.5
    FACE_DETECTION_CONFIDENCE: float = 0.5

    # Zoom Settings
    MIN_ZOOM: float = 1.0
    MAX_ZOOM: float = 3.0
    ZOOM_SMOOTHING: float = 0.1

    # Framing
    FRAMING_SMOOTHING: float = 0.1

    # Virtual Camera
    VIRTUAL_CAM_ENABLED: bool = True
```

**Configuration Loading**:

```python
# Load from ~/.gesturecam/config.json
config = Config.from_file("~/.gesturecam/config.json")

# Override with environment variables
config.CAMERA_INDEX = int(os.getenv("GESTURECAM_CAMERA_INDEX", 0))
```

## Performance Optimizations

### 1. Zero-Copy Operations

```python
# Use NumPy views instead of copies
def crop_center(frame, zoom):
    h, w = frame.shape[:2]
    new_h, new_w = int(h / zoom), int(w / zoom)
    y1 = (h - new_h) // 2
    return frame[y1:y1+new_h, (w-new_w)//2:(w+new_w)//2]  # View, not copy
```

### 2. Model Caching

```python
# MediaPipe models cached in memory
class HandDetector:
    def __init__(self):
        self._model = None  # Lazy load once

    def _get_model(self):
        if self._model is None:
            self._model = mp.solutions.hands.Hands(...)
        return self._model
```

### 3. Parallel Processing

```python
# Hand and face detection run in parallel
with ThreadPoolExecutor() as executor:
    hand_future = executor.submit(hand_detector.detect, frame)
    face_future = executor.submit(face_detector.detect, frame)

    hands = hand_future.result()
    face = face_future.result()
```

### 4. Frame Skipping

```python
# Process every Nth frame for non-critical operations
frame_counter = 0
while True:
    frame = get_frame()
    process_frame(frame)  # Every frame

    frame_counter += 1
    if frame_counter % 3 == 0:
        update_analytics()  # Every 3rd frame
```

## Extensibility

### Adding a New Gesture

```python
# 1. Define gesture detection logic
def detect_fist(landmarks):
    """Detect if hand is in fist position."""
    # All fingertips below finger PIP joints
    return all(
        landmarks[tip].y > landmarks[pip].y
        for tip, pip in [(8,6), (12,10), (16,14), (20,18)]
    )

# 2. Add to gesture recognizer
class GestureRecognizer:
    GESTURES = {
        "fist": detect_fist,
        "thumbs_up": is_thumbs_up,
        # ...
    }

# 3. Map gesture to action
def dispatch_gesture(gesture):
    actions = {
        "fist": "pause_tracking",
        "thumbs_up": "zoom_in",
        # ...
    }
    return actions.get(gesture)
```

### Adding a New Framing Mode

```python
# 1. Define framing logic
def framing_torso(face_bbox, frame_size):
    """Frame from torso up."""
    # Calculate offset to center upper body
    pass

# 2. Register mode
FramingEngine.MODES = {
    "manual": framing_manual,
    "face_follow": framing_face_follow,
    "headshot": framing_headshot,
    "torso": framing_torso,  # New mode
}
```

## Testing Strategy

### Unit Tests

```python
def test_gesture_recognition():
    landmarks = [...]  # Mock landmarks
    gesture = recognize_gesture(landmarks)
    assert gesture == "thumbs_up"

def test_zoom_smoothing():
    zoom_engine = ZoomEngine()
    zoom_engine.set_zoom(2.0)
    assert zoom_engine.current_zoom == 1.1  # 90% old, 10% new
```

### Integration Tests

```python
def test_pipeline_integration():
    pipeline = Pipeline()
    frame = cv2.imread("test_frame.jpg")
    result = pipeline.process_frame(frame)
    assert result.shape == (720, 1280, 3)
```

### Performance Tests

```python
def test_fps_benchmark():
    pipeline = Pipeline()
    start = time.time()
    for _ in range(100):
        pipeline.process_frame(test_frame)
    fps = 100 / (time.time() - start)
    assert fps > 25  # Minimum acceptable FPS
```

## Future Architecture Improvements

1. **Plugin System**: Allow dynamic gesture loading
2. **Configurable Pipeline**: User-defined processing stages
3. **Distributed Processing**: Offload heavy computation to GPU/cloud
4. **Machine Learning Optimization**: Learn optimal zoom/framing per user
5. **Gesture Personalization**: Train custom gesture models

---

This architecture document provides a comprehensive overview of GestureCam's system design, components, and data flow.