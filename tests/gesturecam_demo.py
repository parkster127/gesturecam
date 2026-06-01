#!/usr/bin/env python3
"""
GestureCam - Demo Mejorado con Face Mesh + Gestos de Manos

Control de cámara virtual con gestos:
- 👍 Thumbs UP = Zoom IN
- 👎 Thumbs DOWN = Zoom OUT
- ✋ Palma abierta = HOLD (pausar zoom)
- 👆 Índice arriba/abajo = Zoom fino
- 🤏 Pinch (pulgar + índice) = Zoom continuo
- 👐 Dos manos = Zoom con separación

Framing inteligente con Face Mesh:
- Tracking de cara con 468 landmarks
- Auto-framing basado en posición facial
- Detección de ojos para mejor centrado
"""

import cv2
import numpy as np
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesturecam.vision.hands import HandTracker
from gesturecam.vision.face import FaceTracker
from gesturecam.vision.gestures import GestureRecognizer
from gesturecam.core.zoom import ZoomController
from gesturecam.core.framing import FramingController


class GestureCamDemo:
    """
    Sistema completo de control de cámara con gestos y Face Mesh
    """

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index

        # Inicializar trackers
        print("Inicializando sistema...")
        self.hand_tracker = HandTracker(detection_confidence=0.5, max_hands=2)
        self.face_tracker = FaceTracker(
            use_face_mesh=True,  # ✨ MEJORA: Usar Face Mesh con 468 landmarks
            calibration_file="calibration_profile.json",
        )
        self.gesture_recognizer = GestureRecognizer()

        # Controladores
        self.zoom_controller = ZoomController(
            min_zoom=1.0,
            max_zoom=3.0,
            smoothing_factor=0.15,  # Suavizado mejorado
        )
        self.framing_controller = FramingController(smoothing_factor=0.1)

        # Estado
        self.mode = "auto"  # auto, manual
        self.show_debug = True
        self.show_landmarks = True

        # Estadísticas
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()

        # Pinch zoom state
        self.pinch_baseline = None
        self.pinch_zoom_baseline = None

        print("✅ Sistema inicializado")

    def process_gestures(self, hands):
        """Procesar gestos de manos para control de zoom"""
        if not hands:
            return

        # Gestos de zoom (thumbs, índice, etc.)
        gesture = self.gesture_recognizer.get_zoom_gesture(hands)

        if gesture["action"] == "zoom_in":
            new_zoom = self.zoom_controller.target_zoom + gesture["value"]
            self.zoom_controller.set_target_zoom(new_zoom)

        elif gesture["action"] == "zoom_out":
            new_zoom = self.zoom_controller.target_zoom - gesture["value"]
            self.zoom_controller.set_target_zoom(new_zoom)

        elif gesture["action"] == "hold":
            # Mantener zoom actual (no hacer nada)
            pass

        # Pinch zoom (continuo)
        pinch_dist = self.gesture_recognizer.check_pinch_zoom(hands)
        if pinch_dist is not None:
            if self.pinch_baseline is None:
                # Iniciar pinch
                self.pinch_baseline = pinch_dist
                self.pinch_zoom_baseline = self.zoom_controller.current_zoom
            else:
                # Calcular zoom basado en cambio de distancia
                ratio = pinch_dist / self.pinch_baseline
                new_zoom = self.pinch_zoom_baseline * ratio
                self.zoom_controller.set_target_zoom(new_zoom)
        else:
            # Reset pinch
            self.pinch_baseline = None
            self.pinch_zoom_baseline = None

        # Zoom con dos manos
        if len(hands) >= 2:
            two_hand_dist = self.gesture_recognizer.check_two_hand_zoom(hands)
            if two_hand_dist:
                # Normalizar a zoom (200px = zoom 1.0, 400px = zoom 2.0, etc.)
                zoom_from_hands = two_hand_dist / 200.0
                zoom_from_hands = np.clip(zoom_from_hands, 1.0, 3.0)
                self.zoom_controller.set_target_zoom(zoom_from_hands)

    def process_face_tracking(self, frame, face_data):
        """
        Procesar tracking facial para auto-framing

        Con Face Mesh mejorado, ahora tenemos:
        - 468 landmarks faciales
        - Detección precisa de ojos
        - Mejor centro de masa facial
        """
        if not face_data:
            return

        bbox, metrics = face_data

        if bbox is None:
            return

        h, w = frame.shape[:2]

        # Si usamos Face Mesh, tenemos métricas detalladas
        if hasattr(metrics, "detected") and metrics.detected:
            # Usar centro facial preciso de Face Mesh
            center_x = metrics.center[0] / w
            center_y = metrics.center[1] / h

            # Ajustar centro basado en ojos (mejor composición)
            # Los ojos deben estar en el tercio superior del frame
            if metrics.left_eye and metrics.right_eye:
                eye_center_y = (
                    metrics.left_eye.center[1] + metrics.right_eye.center[1]
                ) / 2
                # Offset: queremos que los ojos estén en y=0.33 del frame
                center_y = (
                    eye_center_y / h
                ) + 0.17  # +0.17 para que ojos queden en 1/3
        else:
            # Fallback a bbox simple
            x, y, bw, bh = bbox
            center_x = (x + bw / 2) / w
            center_y = (y + bh / 2) / h

        # Actualizar framing
        self.framing_controller.target_center_x = center_x
        self.framing_controller.target_center_y = center_y

        # Aplicar suavizado
        cx, cy = self.framing_controller.step()
        self.zoom_controller.set_zoom_center(cx, cy)

    def draw_ui(self, frame, hands, face_data):
        """Dibujar interfaz de usuario con información"""
        display = frame.copy()
        h, w = display.shape[:2]

        # Panel superior - Estado
        panel_h = 160
        overlay = np.zeros((panel_h, w, 3), dtype=np.uint8)
        overlay[:] = (40, 40, 40)

        # Info de zoom
        zoom_text = f"Zoom: {self.zoom_controller.current_zoom:.2f}x"
        cv2.putText(
            overlay, zoom_text, (20, 35), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2
        )

        # Centro de zoom
        center_text = f"Centro: ({self.zoom_controller.center_x:.2f}, {self.zoom_controller.center_y:.2f})"
        cv2.putText(
            overlay,
            center_text,
            (20, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        # FPS
        cv2.putText(
            overlay,
            f"FPS: {self.fps:.1f}",
            (20, 90),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (150, 150, 150),
            1,
        )

        # Modo
        mode_text = f"Modo: {self.mode.upper()}"
        cv2.putText(
            overlay,
            mode_text,
            (20, 115),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (150, 255, 150),
            1,
        )

        # Gestos detectados
        gesture_info = "Gesto: "
        if hands:
            gesture = self.gesture_recognizer.get_zoom_gesture(hands)
            if gesture["action"] != "none":
                gesture_info += gesture["action"].replace("_", " ").upper()
                color = (0, 255, 0)
            else:
                gesture_info += "Esperando..."
                color = (100, 100, 100)

            cv2.putText(
                overlay,
                gesture_info,
                (20, 140),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1,
            )

        # Info de detección
        detection_info = []
        if hands:
            detection_info.append(f"{len(hands)} mano(s)")

        bbox, metrics = face_data if face_data else (None, None)
        if bbox:
            if hasattr(metrics, "detected") and metrics.detected:
                detection_info.append("Face Mesh ✓")
            else:
                detection_info.append("Face bbox")

        if detection_info:
            info_text = " | ".join(detection_info)
            cv2.putText(
                overlay,
                info_text,
                (w - 300, 35),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (150, 150, 255),
                1,
            )

        # Controles
        controls_y = panel_h - 55
        cv2.putText(
            overlay,
            "Controles:",
            (w - 250, controls_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (100, 100, 100),
            1,
        )
        cv2.putText(
            overlay,
            "Q: Salir | D: Debug | L: Landmarks",
            (w - 250, controls_y + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (100, 100, 100),
            1,
        )

        # Combinar overlay
        display[0:panel_h] = cv2.addWeighted(display[0:panel_h], 0.3, overlay, 0.7, 0)

        # Dibujar landmarks de manos
        if hands and self.show_landmarks:
            for hand in hands:
                # Dibujar landmarks de mano
                for lm in hand["lmList"]:
                    cv2.circle(display, (lm[0], lm[1]), 3, (0, 255, 0), -1)

                # Centro de mano
                cx, cy = hand["center"]
                cv2.circle(display, (cx, cy), 8, (255, 0, 255), 2)

        # Dibujar face tracking
        if face_data and self.show_landmarks:
            bbox, metrics = face_data

            if hasattr(metrics, "detected") and metrics.detected:
                # Dibujar con Face Mesh mejorado
                if self.show_debug:
                    display = self.face_tracker.draw_debug(
                        display,
                        metrics,
                        show_mesh=False,
                        show_eyes=True,
                        show_iris=True,
                        show_metrics=False,
                        show_pose=False,
                    )
            elif bbox:
                # Dibujar bbox básico
                x, y, bw, bh = bbox
                cv2.rectangle(display, (x, y), (x + bw, y + bh), (255, 0, 0), 2)

        # Indicador de centro de zoom
        zoom_center_x = int(self.zoom_controller.center_x * w)
        zoom_center_y = int(self.zoom_controller.center_y * h)
        cv2.drawMarker(
            display,
            (zoom_center_x, zoom_center_y),
            (0, 255, 255),
            cv2.MARKER_CROSS,
            20,
            2,
        )

        return display

    def run(self):
        """Ejecutar demo"""
        print("\n" + "=" * 70)
        print("GESTURECAM - Control de Cámara con Gestos + Face Mesh")
        print("=" * 70)
        print("\n📷 Gestos disponibles:")
        print("  👍 Thumbs UP → Zoom IN")
        print("  👎 Thumbs DOWN → Zoom OUT")
        print("  ✋ Palma abierta → Pausar zoom")
        print("  👆 Índice arriba/abajo → Zoom fino")
        print("  🤏 Pinch (pulgar+índice) → Zoom continuo")
        print("  👐 Dos manos separadas → Zoom con distancia")
        print("\n⌨️  Controles:")
        print("  Q → Salir")
        print("  D → Toggle debug overlay")
        print("  L → Toggle landmarks")
        print("  M → Cambiar modo (auto/manual)")
        print("\n✨ Mejoras con Face Mesh:")
        print("  • 468 landmarks faciales (vs bbox simple)")
        print("  • Tracking preciso de ojos")
        print("  • Auto-framing inteligente")
        print("  • Centro de masa facial real")
        print("=" * 70 + "\n")

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("❌ Error: No se pudo abrir la cámara")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        print("Sistema iniciado. Muestra tus gestos a la cámara...\n")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                self.frame_count += 1

                # Detectar manos
                hands = self.hand_tracker.detect_hands(frame)

                # Detectar cara con Face Mesh mejorado
                face_data = self.face_tracker.detect_face(frame)

                # Procesar gestos
                self.process_gestures(hands)

                # Procesar tracking facial (auto-framing)
                if self.mode == "auto":
                    self.process_face_tracking(frame, face_data)

                # Actualizar zoom
                self.zoom_controller.step()

                # Aplicar zoom
                zoomed_frame = self.zoom_controller.apply_zoom(frame)

                # Dibujar UI
                display = self.draw_ui(zoomed_frame, hands, face_data)

                # Calcular FPS
                if self.frame_count % 10 == 0:
                    current_time = time.time()
                    elapsed = current_time - self.last_fps_time
                    self.fps = 10 / elapsed if elapsed > 0 else 0
                    self.last_fps_time = current_time

                cv2.imshow("GestureCam - Demo Mejorado", display)

                # Input
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("d"):
                    self.show_debug = not self.show_debug
                    print(f"Debug: {'ON' if self.show_debug else 'OFF'}")
                elif key == ord("l"):
                    self.show_landmarks = not self.show_landmarks
                    print(f"Landmarks: {'ON' if self.show_landmarks else 'OFF'}")
                elif key == ord("m"):
                    self.mode = "manual" if self.mode == "auto" else "auto"
                    print(f"Modo: {self.mode.upper()}")

        except KeyboardInterrupt:
            print("\nInterrumpido por usuario")

        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("\n✅ Demo finalizado")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="GestureCam Demo Mejorado")
    parser.add_argument("--camera", "-c", type=int, default=0, help="Índice de cámara")
    args = parser.parse_args()

    demo = GestureCamDemo(camera_index=args.camera)
    demo.run()


if __name__ == "__main__":
    main()
