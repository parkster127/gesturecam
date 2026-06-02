#!/usr/bin/env python3
"""
Script de prueba interactivo para GestureCam.
Muestra una ventana de preview con detección de gestos, zoom y face tracking.

Controles:
- Pinch con pulgar e índice: controla el zoom
- Dos manos: zoom con distancia entre manos
- '1': Modo Manual (sin seguimiento)
- '2': Modo Face Follow (la cámara sigue tu cara)
- '3': Modo Headshot (encuadre para headshot)
- '4': Modo Shirt-Up (encuadre desde camisa hacia arriba)
- 'r': Reset zoom a 1.0
- '+'/'-': Zoom manual para testing
- 'q': Salir
"""

import logging
import os
import sys

import cv2
import numpy as np

# Añadir el directorio padre al path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesturecam.camera.sources import CameraSource
from gesturecam.config import Config
from gesturecam.core.framing import FramingController
from gesturecam.core.zoom import ZoomController
from gesturecam.vision.face import FaceTracker
from gesturecam.vision.gestures import GestureRecognizer
from gesturecam.vision.hands import HandTracker


def draw_debug_overlay(frame, hands, face_bbox, zoom_level, gesture_action="none", framing_mode="manual"):
    """Dibuja información de debug en el frame."""
    h, w = frame.shape[:2]

    # Dibuja info del zoom
    cv2.putText(frame, f"Zoom: {zoom_level:.2f}x", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Dibuja modo de framing
    mode_colors = {
        "manual": (150, 150, 150),
        "face_follow": (0, 255, 255),
        "headshot": (255, 100, 100),
        "shirt_up": (100, 255, 100)
    }
    mode_color = mode_colors.get(framing_mode, (255, 255, 255))
    cv2.putText(frame, f"Mode: {framing_mode.upper()}", (10, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, mode_color, 2)

    # Dibuja gesto detectado
    gesture_info = {
        "none": ("---", (150, 150, 150)),
        "zoom_in": ("ZOOM IN", (0, 255, 0)),
        "zoom_out": ("ZOOM OUT", (0, 100, 255)),
        "hold": ("HOLD", (255, 255, 0))
    }
    gesture_text, gesture_color = gesture_info.get(gesture_action, ("???", (255, 255, 255)))
    cv2.putText(frame, f"Gesture: {gesture_text}", (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, gesture_color, 2)

    # Dibuja instrucciones
    instructions = [
        "GESTURES:",
        "  Thumbs UP = Zoom In",
        "  Thumbs DOWN = Zoom Out",
        "  Open Palm = HOLD",
        "  Index Point = Zoom",
        "KEYS: 1-4 modes | r reset | q quit"
    ]
    y_offset = h - 140
    for inst in instructions:
        cv2.putText(frame, inst, (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)
        y_offset += 20

    # Dibuja las manos detectadas
    for i, hand in enumerate(hands):
        # Dibuja landmarks
        lm_list = hand.get("lmList", [])
        for lm in lm_list:
            cv2.circle(frame, (int(lm[0]), int(lm[1])), 3, (0, 255, 255), -1)

        # Dibuja center
        center = hand.get("center")
        if center:
            cv2.circle(frame, center, 10, (255, 0, 255), -1)
            cv2.putText(frame, f"Hand {i+1}", (center[0] + 15, center[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

        # Dibuja línea entre pulgar e índice para visualizar pinch
        if len(lm_list) > 8:
            thumb_tip = (int(lm_list[4][0]), int(lm_list[4][1]))
            index_tip = (int(lm_list[8][0]), int(lm_list[8][1]))
            cv2.line(frame, thumb_tip, index_tip, (0, 165, 255), 3)
            # Círculo en el punto medio
            mid_x = (thumb_tip[0] + index_tip[0]) // 2
            mid_y = (thumb_tip[1] + index_tip[1]) // 2
            cv2.circle(frame, (mid_x, mid_y), 8, (0, 165, 255), -1)

    # Dibuja face bbox si existe
    if face_bbox is not None:
        x, y, bw, bh = face_bbox
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), (0, 255, 0), 2)
        cv2.putText(frame, "Face", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Dibuja línea de dos manos si hay 2 manos
    if len(hands) >= 2:
        c1 = hands[0].get("center")
        c2 = hands[1].get("center")
        if c1 and c2:
            cv2.line(frame, c1, c2, (255, 0, 0), 2)
            dist = np.sqrt((c1[0]-c2[0])**2 + (c1[1]-c2[1])**2)
            mid = ((c1[0]+c2[0])//2, (c1[1]+c2[1])//2)
            cv2.putText(frame, f"2-Hand: {dist:.0f}px", mid,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    return frame


def run_live_test():
    """Ejecuta el test interactivo con la cámara."""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    config = Config()
    config.CAMERA_INDEX = 0  # Cámara por defecto
    config.ZOOM_SMOOTHING = 0.15  # Un poco más suave
    config.FRAMING_SMOOTHING = 0.08  # Seguimiento suave de cara

    print("\n" + "="*60)
    print("🎥 GestureCam - Test en Vivo con Face Tracking")
    print("="*60)
    print("\nInicializando componentes...")

    # Inicializar componentes
    source = CameraSource(config.CAMERA_INDEX)
    w, h = source.get_resolution()

    if w == 0 or h == 0:
        print("❌ Error: No se pudo abrir la cámara")
        return

    print(f"✅ Cámara abierta: {w}x{h}")

    hand_tracker = HandTracker(
        detection_confidence=config.HAND_DETECTION_CONFIDENCE,
        max_hands=config.MAX_HANDS
    )
    print(f"✅ Hand Tracker: {'Mock Mode' if hand_tracker.mock_mode else 'MediaPipe Activo'}")

    face_tracker = FaceTracker(
        min_detection_confidence=config.FACE_DETECTION_CONFIDENCE
    )
    print("✅ Face Tracker inicializado")

    gesture_recognizer = GestureRecognizer(
        pinch_threshold_lower=config.PINCH_THRESHOLD_LOWER,
        pinch_threshold_upper=config.PINCH_THRESHOLD_UPPER
    )

    zoom_ctrl = ZoomController(
        min_zoom=config.MIN_ZOOM,
        max_zoom=config.MAX_ZOOM,
        smoothing_factor=config.ZOOM_SMOOTHING
    )

    framing_ctrl = FramingController(
        smoothing_factor=config.FRAMING_SMOOTHING
    )

    # Activar face tracking por defecto
    framing_ctrl.set_mode("face_follow")

    print("\n✅ Todos los componentes inicializados")
    print("📍 Modo inicial: FACE_FOLLOW (presiona 1-4 para cambiar)")
    print("🚀 Iniciando preview... (presiona 'q' para salir)\n")

    cv2.namedWindow("GestureCam Test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("GestureCam Test", 960, 540)

    frame_count = 0

    while True:
        ret, frame = source.read()
        if not ret:
            print("❌ Error leyendo frame")
            break

        frame_count += 1

        # Flip horizontal para efecto espejo
        frame = cv2.flip(frame, 1)

        # 1. Detección
        hands = hand_tracker.detect_hands(frame)
        face_bbox, _ = face_tracker.detect_face(frame)

        # 2. Lógica de gestos - NUEVO SISTEMA MÁS CONTROLABLE
        zoom_gesture = gesture_recognizer.get_zoom_gesture(hands)
        gesture_action = zoom_gesture['action']
        gesture_value = zoom_gesture['value']

        if gesture_action == 'zoom_in':
            new_zoom = min(zoom_ctrl.target_zoom + gesture_value, config.MAX_ZOOM)
            zoom_ctrl.set_target_zoom(new_zoom)
        elif gesture_action == 'zoom_out':
            new_zoom = max(zoom_ctrl.target_zoom - gesture_value, config.MIN_ZOOM)
            zoom_ctrl.set_target_zoom(new_zoom)
        elif gesture_action == 'hold':
            # Mantener zoom actual (no hacer nada)
            pass

        # Two hand zoom (mantener como opción secundaria)
        two_hand_dist = gesture_recognizer.check_two_hand_zoom(hands)
        if two_hand_dist is not None and len(hands) >= 2:
            base_dist = 300.0  # Aumentado para menos sensibilidad
            target = max(1.0, min(two_hand_dist / base_dist, config.MAX_ZOOM))
            zoom_ctrl.update_zoom_level(target)

        # 3. Update state
        framing_ctrl.update_face_target(face_bbox, w, h)
        curr_zoom = zoom_ctrl.step()
        cx, cy = framing_ctrl.step()
        zoom_ctrl.set_zoom_center(cx, cy)

        # 4. Crear frame original para mostrar detección
        debug_frame = frame.copy()
        debug_frame = draw_debug_overlay(debug_frame, hands, face_bbox, curr_zoom, gesture_action, framing_ctrl.mode)

        # 5. Aplicar zoom
        zoomed_frame = zoom_ctrl.apply_zoom(frame)

        # 6. Mostrar ambos: Original con debug | Zoomed
        # Resize para que quepan lado a lado
        h_frame, w_frame = frame.shape[:2]
        display_h = 540
        display_w = int(w_frame * display_h / h_frame)

        debug_resized = cv2.resize(debug_frame, (display_w, display_h))
        zoomed_resized = cv2.resize(zoomed_frame, (display_w, display_h))

        # Concatenar horizontalmente
        combined = np.hstack([debug_resized, zoomed_resized])

        # Añadir etiquetas
        cv2.putText(combined, "Detection", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(combined, "Zoomed Output", (display_w + 10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        cv2.imshow("GestureCam Test", combined)

        # Handle keys
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n👋 Saliendo...")
            break
        elif key == ord('r'):
            zoom_ctrl.set_target_zoom(1.0)
            print("🔄 Zoom reset a 1.0x")
        elif key == ord('+') or key == ord('='):
            new_zoom = min(zoom_ctrl.target_zoom + 0.2, config.MAX_ZOOM)
            zoom_ctrl.set_target_zoom(new_zoom)
            print(f"➕ Zoom manual: {new_zoom:.2f}x")
        elif key == ord('-') or key == ord('_'):
            new_zoom = max(zoom_ctrl.target_zoom - 0.2, config.MIN_ZOOM)
            zoom_ctrl.set_target_zoom(new_zoom)
            print(f"➖ Zoom manual: {new_zoom:.2f}x")
        elif key == ord('1'):
            framing_ctrl.set_mode("manual")
            print("📍 Modo: MANUAL (sin seguimiento)")
        elif key == ord('2'):
            framing_ctrl.set_mode("face_follow")
            print("📍 Modo: FACE_FOLLOW (sigue tu cara)")
        elif key == ord('3'):
            framing_ctrl.set_mode("headshot")
            print("📍 Modo: HEADSHOT (encuadre de cabeza)")
        elif key == ord('4'):
            framing_ctrl.set_mode("shirt_up")
            print("📍 Modo: SHIRT_UP (desde camisa hacia arriba)")

    # Cleanup
    source.release()
    cv2.destroyAllWindows()
    print(f"\n📊 Frames procesados: {frame_count}")
    print("✅ Test completado")


if __name__ == "__main__":
    run_live_test()
