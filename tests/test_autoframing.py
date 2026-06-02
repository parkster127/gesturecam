#!/usr/bin/env python3
"""
Test de Auto-Framing Avanzado - Vectores AI Cam
Prueba los nuevos modos inteligentes del camarógrafo.
"""

import os
import sys

import cv2

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gesturecam.camera.operator import CameraMode, CameraOperator
from gesturecam.vision.face_mesh import FaceMeshTracker


def main():
    print("🎥 Iniciando Prueba de Auto-Framing Avanzado...")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: No se detecta cámara.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    ret, frame = cap.read()
    h, w = frame.shape[:2]

    print("👁️ Inicializando Face Mesh...")
    tracker = FaceMeshTracker(min_detection_confidence=0.7)

    print("🎬 Inicializando Operador de Cámara...")
    cameraman = CameraOperator(source_width=w, source_height=h)

    # Iniciar en modo FOLLOW por defecto
    cameraman.set_mode(CameraMode.FOLLOW)
    cameraman.set_manual_zoom(1.2)

    print("\n✅ SISTEMA LISTO")
    print("--------------------------------")
    print("MODOS:")
    print("  [1] MANUAL (Zoom fijo, rápido)")
    print("  [2] FOLLOW (Suave, estándar)")
    print("  [3] SMART ZOOM (Auto-Zoom inteligente)")
    print("  [4] CINEMATIC (Ultra suave)")
    print("\nCONTROLES:")
    print("  [+] Zoom In (Manual)")
    print("  [-] Zoom Out (Manual)")
    print("  [Q] Salir")
    print("--------------------------------\n")

    current_manual_zoom = 1.2

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # 1. Visión
        metrics = tracker.detect(frame)

        # 2. Decisión
        if metrics.detected:
            cameraman.update_target(metrics.bbox, metrics.center)

        # 3. Acción
        output_frame = cameraman.crop_frame(frame)

        # --- DEBUG ---
        debug_frame = frame.copy()
        vx, vy, vw, vh = cameraman.process()

        # Dibujar viewport
        cv2.rectangle(debug_frame, (vx, vy), (vx + vw, vy + vh), (0, 255, 0), 2)

        # Info
        mode_str = cameraman.mode.upper()
        zoom_val = cameraman.target_viewport.zoom_level

        cv2.putText(
            debug_frame,
            f"MODE: {mode_str}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )
        cv2.putText(
            debug_frame,
            f"ZOOM: {zoom_val:.2f}x",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
        )

        if metrics.detected:
            # Dibujar bounding box de la cara
            fx, fy, fw, fh = metrics.bbox
            cv2.rectangle(debug_frame, (fx, fy), (fx + fw, fy + fh), (0, 0, 255), 1)

        cv2.imshow("Vectores Cam - INPUT", cv2.resize(debug_frame, (640, 360)))
        cv2.imshow("Vectores Cam - SALIDA VIRTUAL", output_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("1"):
            cameraman.set_mode(CameraMode.MANUAL)
        elif key == ord("2"):
            cameraman.set_mode(CameraMode.FOLLOW)
        elif key == ord("3"):
            cameraman.set_mode(CameraMode.SMART_ZOOM)
        elif key == ord("4"):
            cameraman.set_mode(CameraMode.CINEMATIC)
        elif key == ord("+") or key == ord("="):
            current_manual_zoom = min(3.0, current_manual_zoom + 0.1)
            cameraman.set_manual_zoom(current_manual_zoom)
        elif key == ord("-"):
            current_manual_zoom = max(1.0, current_manual_zoom - 0.1)
            cameraman.set_manual_zoom(current_manual_zoom)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
