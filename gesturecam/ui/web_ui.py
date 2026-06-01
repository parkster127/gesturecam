"""
GestureCam Web UI - NiceGUI + Tailwind
Beautiful web interface with Python backend
"""

from nicegui import ui, app
import cv2
import numpy as np
import base64
import threading
import time
import asyncio
from dataclasses import dataclass
from enum import Enum
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


class FramingMode(Enum):
    MANUAL = "manual"
    FACE_FOLLOW = "face_follow"
    HEADSHOT = "headshot"
    SHIRT_UP = "shirt_up"


@dataclass
class AppState:
    zoom_level: float = 1.0
    framing_mode: FramingMode = FramingMode.FACE_FOLLOW
    is_mirrored: bool = True
    show_overlay: bool = True
    current_gesture: str = "None"
    camera_active: bool = False


# Global state
state = AppState()
cap = None
hand_detector = None
face_detector = None
frame_original = None
frame_processed = None
frame_lock = threading.Lock()


def encode_frame(frame):
    """Convert OpenCV frame to base64 for web display"""
    if frame is None:
        return ""
    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return 'data:image/jpeg;base64,' + base64.b64encode(buffer).decode()


def init_camera():
    """Initialize camera"""
    global cap
    for idx in range(5):
        test_cap = cv2.VideoCapture(idx)
        if test_cap.isOpened():
            ret, frame = test_cap.read()
            if ret and frame is not None:
                cap = test_cap
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                logger.info(f"Camera opened at index {idx}")
                return True
            test_cap.release()
    return False


def init_mediapipe():
    """Initialize MediaPipe detectors"""
    global hand_detector, face_detector
    
    try:
        import mediapipe as mp
        from mediapipe.tasks import python as mp_tasks
        from mediapipe.tasks.python import vision as mp_vision
        import urllib.request
        
        models_dir = os.path.expanduser("~/.gesturecam")
        os.makedirs(models_dir, exist_ok=True)
        
        hand_path = os.path.join(models_dir, "hand_landmarker.task")
        face_path = os.path.join(models_dir, "face_landmarker.task")
        
        # Download models if needed
        for path, url, name in [
            (hand_path, "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task", "hand"),
            (face_path, "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task", "face"),
        ]:
            if not os.path.exists(path):
                logger.info(f"Downloading {name} model...")
                urllib.request.urlretrieve(url, path)
        
        # Init detectors
        hand_detector = mp_vision.HandLandmarker.create_from_options(
            mp_vision.HandLandmarkerOptions(
                base_options=mp_tasks.BaseOptions(model_asset_path=hand_path),
                running_mode=mp_vision.RunningMode.IMAGE,
                num_hands=2,
                min_hand_detection_confidence=0.5,
            )
        )
        
        face_detector = mp_vision.FaceLandmarker.create_from_options(
            mp_vision.FaceLandmarkerOptions(
                base_options=mp_tasks.BaseOptions(model_asset_path=face_path),
                running_mode=mp_vision.RunningMode.IMAGE,
                num_faces=1,
                output_face_blendshapes=True,
            )
        )
        
        logger.info("MediaPipe initialized")
        return True
    except Exception as e:
        logger.error(f"MediaPipe init failed: {e}")
        return False


def detect_gesture(landmarks):
    """Detect thumb gestures"""
    THUMB_TIP, THUMB_IP = 4, 3
    INDEX_TIP, INDEX_PIP = 8, 6
    MIDDLE_TIP, MIDDLE_PIP = 12, 10
    RING_TIP, RING_PIP = 16, 14
    PINKY_TIP, PINKY_PIP = 20, 18
    
    thumb_up = landmarks[THUMB_TIP].y < landmarks[THUMB_IP].y - 0.05
    thumb_down = landmarks[THUMB_TIP].y > landmarks[THUMB_IP].y + 0.05
    fingers_closed = all([
        landmarks[tip].y > landmarks[pip].y
        for tip, pip in [(INDEX_TIP, INDEX_PIP), (MIDDLE_TIP, MIDDLE_PIP),
                        (RING_TIP, RING_PIP), (PINKY_TIP, PINKY_PIP)]
    ])
    
    if thumb_up and fingers_closed:
        return "👍 Zoom In"
    elif thumb_down and fingers_closed:
        return "👎 Zoom Out"
    return None


def detect_wink(blendshapes):
    """Detect wink gesture"""
    if not blendshapes:
        return None
    left, right = 0, 0
    for bs in blendshapes[0]:
        if bs.category_name == "eyeBlinkLeft":
            left = bs.score
        elif bs.category_name == "eyeBlinkRight":
            right = bs.score
    
    diff = abs(left - right)
    if diff > 0.2:
        if left > 0.35 and right < 0.2:
            return "left"
        elif right > 0.35 and left < 0.2:
            return "right"
    return None


def process_frame():
    """Process a single frame with MediaPipe"""
    global frame_original, frame_processed, state
    import mediapipe as mp
    
    if cap is None or not cap.isOpened():
        return
    
    ret, frame = cap.read()
    if not ret:
        return
    
    h, w = frame.shape[:2]
    gesture = "None"
    face_center = None
    
    # Mirror
    if state.is_mirrored:
        frame = cv2.flip(frame, 1)
    
    original = frame.copy()
    
    # MediaPipe processing
    if hand_detector or face_detector:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        
        # Face detection
        if face_detector:
            try:
                results = face_detector.detect(mp_image)
                if results.face_landmarks:
                    landmarks = results.face_landmarks[0]
                    xs = [lm.x * w for lm in landmarks]
                    ys = [lm.y * h for lm in landmarks]
                    face_center = (int(sum(xs)/len(xs)), int(sum(ys)/len(ys)))
                    
                    if state.show_overlay:
                        x1, x2 = int(min(xs)), int(max(xs))
                        y1, y2 = int(min(ys)), int(max(ys))
                        cv2.rectangle(original, (x1, y1), (x2, y2), (99, 102, 242), 2)
                
                wink = detect_wink(results.face_blendshapes)
                if wink:
                    gesture = f"😉 Wink [{wink}]"
            except:
                pass
        
        # Hand detection
        if hand_detector:
            try:
                results = hand_detector.detect(mp_image)
                if results.hand_landmarks:
                    for i, landmarks in enumerate(results.hand_landmarks):
                        if state.show_overlay:
                            color = (242, 103, 100) if i == 0 else (100, 242, 150)
                            for lm in landmarks:
                                pt = (int(lm.x * w), int(lm.y * h))
                                cv2.circle(original, pt, 4, color, -1)
                        
                        g = detect_gesture(landmarks)
                        if g:
                            gesture = g
                            if "In" in g:
                                state.zoom_level = min(3.0, state.zoom_level + 0.02)
                            elif "Out" in g:
                                state.zoom_level = max(1.0, state.zoom_level - 0.02)
            except:
                pass
    
    state.current_gesture = gesture
    
    # Create zoomed/framed version
    zh, zw = int(h / state.zoom_level), int(w / state.zoom_level)
    cx, cy = w // 2, h // 2
    
    if face_center and state.framing_mode != FramingMode.MANUAL:
        fx, fy = face_center
        if state.framing_mode == FramingMode.FACE_FOLLOW:
            cx = int(cx * 0.7 + fx * 0.3)
            cy = int(cy * 0.7 + fy * 0.3)
        elif state.framing_mode == FramingMode.HEADSHOT:
            cx, cy = fx, max(zh//2, fy - int(h*0.05))
        elif state.framing_mode == FramingMode.SHIRT_UP:
            cx, cy = fx, min(h - zh//2, fy + int(h*0.15))
    
    x1 = max(0, min(w - zw, cx - zw // 2))
    y1 = max(0, min(h - zh, cy - zh // 2))
    
    processed = frame[y1:y1+zh, x1:x1+zw]
    if processed.size > 0:
        processed = cv2.resize(processed, (w, h))
    else:
        processed = frame.copy()
    
    with frame_lock:
        frame_original = original
        frame_processed = processed


# Background thread for video processing
def video_thread():
    while state.camera_active:
        process_frame()
        time.sleep(0.033)  # ~30 FPS


def start_video():
    state.camera_active = True
    thread = threading.Thread(target=video_thread, daemon=True)
    thread.start()


# ============================================================================
# WEB UI
# ============================================================================

def create_ui():
    """Create the NiceGUI interface"""
    
    # Custom CSS
    ui.add_head_html('''
    <style>
        body { background: #0a0a12 !important; }
        .video-container { 
            border-radius: 16px; 
            overflow: hidden;
            background: #000;
        }
        .ring-primary { box-shadow: 0 0 0 3px rgba(99, 102, 242, 0.5); }
        .btn-mode {
            transition: all 0.2s;
        }
        .btn-mode:hover {
            transform: translateY(-2px);
        }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    ''')
    
    # Main container
    with ui.column().classes('w-full min-h-screen p-6 gap-6').style('font-family: Inter, sans-serif'):
        
        # Header
        with ui.row().classes('w-full items-center gap-4'):
            ui.label('GestureCam').classes('text-2xl font-bold text-indigo-400')
            ui.space()
            gesture_label = ui.label('Gesture: None').classes('text-green-400')
        
        # Video row
        with ui.row().classes('justify-center gap-6 w-full'):
            # Original
            with ui.column().classes('items-center gap-2'):
                ui.label('ORIGINAL').classes('text-gray-400 text-sm font-semibold')
                original_img = ui.interactive_image().classes(
                    'video-container w-[480px] h-[270px] object-cover'
                ).style('border: 2px solid #2a2a3a')
            
            # Processed
            with ui.column().classes('items-center gap-2'):
                with ui.row().classes('items-center gap-4'):
                    ui.label('PROCESSED').classes('text-indigo-400 text-sm font-semibold')
                    zoom_label = ui.label('1.0x').classes('text-indigo-400 font-bold')
                processed_img = ui.interactive_image().classes(
                    'video-container ring-primary w-[480px] h-[270px] object-cover'
                ).style('border: 3px solid #6366f2')
        
        # Controls row
        with ui.row().classes('justify-center gap-4'):
            def toggle_mirror():
                state.is_mirrored = not state.is_mirrored
                mirror_btn.text = '↔️ ON' if state.is_mirrored else '↔️ Mirror'
            
            mirror_btn = ui.button('↔️ ON', on_click=toggle_mirror).classes(
                'bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg'
            )
            
            def toggle_overlay():
                state.show_overlay = not state.show_overlay
                overlay_btn.text = '👁️ ON' if state.show_overlay else '👁️ Overlay'
            
            overlay_btn = ui.button('👁️ ON', on_click=toggle_overlay).classes(
                'bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg'
            )
        
        # Framing modes
        ui.label('Framing Modes').classes('text-gray-400 text-sm font-semibold mt-4')
        
        with ui.row().classes('justify-center gap-3'):
            mode_buttons = {}
            
            def set_mode(mode: FramingMode):
                state.framing_mode = mode
                for m, btn in mode_buttons.items():
                    if m == mode:
                        btn.classes(remove='bg-gray-800', add='bg-indigo-600')
                    else:
                        btn.classes(remove='bg-indigo-600', add='bg-gray-800')
            
            for mode, label in [
                (FramingMode.MANUAL, 'Manual'),
                (FramingMode.FACE_FOLLOW, 'Face Follow'),
                (FramingMode.HEADSHOT, 'Headshot'),
                (FramingMode.SHIRT_UP, 'Shirt-Up'),
            ]:
                is_active = mode == state.framing_mode
                btn = ui.button(label, on_click=lambda m=mode: set_mode(m)).classes(
                    f'btn-mode {"bg-indigo-600" if is_active else "bg-gray-800"} hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-medium'
                )
                mode_buttons[mode] = btn
        
        ui.space()
        
        # Status bar
        with ui.row().classes('w-full justify-center items-center gap-4 text-gray-400 text-sm'):
            ui.label('● Camera Active').classes('text-green-400')
            ui.label('|')
            latency_label = ui.label('Latency: 0ms')
    
    # Timer to update frames
    async def update_frames():
        with frame_lock:
            if frame_original is not None:
                original_img.set_source(encode_frame(frame_original))
            if frame_processed is not None:
                processed_img.set_source(encode_frame(frame_processed))
        
        gesture_label.text = f'Gesture: {state.current_gesture}'
        zoom_label.text = f'{state.zoom_level:.1f}x'
    
    ui.timer(0.05, update_frames)


def run():
    """Main entry point"""
    logger.info("Starting GestureCam Web UI...")
    
    # Init camera and MediaPipe
    if not init_camera():
        logger.error("Failed to open camera")
        return
    
    init_mediapipe()
    start_video()
    
    # Create and run UI
    create_ui()
    ui.run(title='GestureCam', port=8080, reload=False)


if __name__ == '__main__':
    run()
