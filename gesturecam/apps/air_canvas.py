#!/usr/bin/env python3
"""
AirCanvas - Pintar en el Aire con Gestos

Aplicación interactiva que permite:
- Dibujar círculos con el dedo índice
- Generar mandalas con simetría radial y efecto neón
- Crear esferas 3D que rotan
- Cambio automático de color en cada trazo
- Cambiar modos y limpiar con gestos

Gestos:
👆 Solo índice levantado = Dibujar (color aleatorio automático)
✌️ Signo de la paz (2 dedos) = Cambiar modo
✋ Palma abierta = Limpiar canvas
1️⃣ Presiona '1' = Modo Círculos
2️⃣ Presiona '2' = Modo Mandala (con efecto neón)
3️⃣ Presiona '3' = Modo Esfera 3D
"""

import os
import sys
import time

import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from gesturecam.effects.geometry import GeometryRenderer
from gesturecam.interactions.drawing import GestureDrawingController
from gesturecam.vision.hands import HandTracker


class AirCanvas:
    """Aplicación principal de dibujo en el aire"""

    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index

        # Inicializar componentes
        print("Inicializando AirCanvas...")
        self.hand_tracker = HandTracker(detection_confidence=0.7, max_hands=1)
        self.drawing_controller = GestureDrawingController()

        # Dimensiones del canvas
        self.width = 1280
        self.height = 720

        self.renderer = GeometryRenderer(self.width, self.height)

        # Estado
        self.show_video = True
        self.show_help = True
        self.fps = 0
        self.frame_count = 0
        self.last_fps_time = time.time()

        # Cooldowns para evitar acciones repetidas
        self.last_color_change = 0
        self.last_clear = 0
        self.last_mode_change = 0
        self.last_peace_sign = 0

        # Auto color change
        self.auto_color_change = True  # Cambiar color automáticamente

        print("✅ AirCanvas inicializado")

    def draw_ui(self, frame: np.ndarray) -> np.ndarray:
        """Dibujar interfaz de usuario"""
        display = frame.copy()
        h, w = display.shape[:2]

        # Panel superior
        panel_h = 100
        overlay = np.zeros((panel_h, w, 3), dtype=np.uint8)
        overlay[:] = (30, 30, 30)

        # Modo actual
        mode_text = f"Modo: {self.drawing_controller.state.mode.upper()}"
        mode_color = self.drawing_controller.state.current_color
        cv2.putText(overlay, mode_text, (20, 35), cv2.FONT_HERSHEY_DUPLEX, 1.0, mode_color, 2)

        # Color actual (preview)
        color_preview_x = 20
        color_preview_y = 55
        cv2.circle(
            overlay,
            (color_preview_x + 15, color_preview_y + 15),
            12,
            self.drawing_controller.state.current_color,
            -1,
        )
        cv2.putText(
            overlay,
            "Color",
            (color_preview_x + 35, color_preview_y + 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        # Simetría (para mandalas)
        if self.drawing_controller.state.mode == "mandala":
            sym_text = f"Simetria: {self.drawing_controller.state.mandala_symmetry}x"
            cv2.putText(
                overlay,
                sym_text,
                (150, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (150, 150, 150),
                1,
            )

        # FPS
        cv2.putText(
            overlay,
            f"FPS: {self.fps:.1f}",
            (w - 120, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (100, 255, 100),
            1,
        )

        # Instrucciones
        if self.show_help:
            help_y = panel_h + 30
            instructions = [
                "Gestos:",
                "  Indice solo = Dibujar",
                "  Paz (2 dedos) = Cambiar modo",
                "  Palma abierta = Limpiar",
                "",
                "Teclado:",
                "  1/2/3 = Modo (circulo/mandala/esfera)",
                "  +/- = Simetria mandala",
                "  V = Toggle video",
                "  H = Toggle ayuda",
                "  Q = Salir",
            ]

            for i, line in enumerate(instructions):
                cv2.putText(
                    display,
                    line,
                    (20, help_y + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (200, 200, 200),
                    1,
                )

        # Combinar overlay
        display[0:panel_h] = cv2.addWeighted(display[0:panel_h], 0.3, overlay, 0.7, 0)

        # Indicador de estado de dibujo
        if self.drawing_controller.state.is_drawing:
            status_text = f"Dibujando {self.drawing_controller.state.mode}..."
            cv2.putText(
                display,
                status_text,
                (w // 2 - 100, h - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                self.drawing_controller.state.current_color,
                2,
            )

        return display

    def process_drawing_command(self, command: dict):
        """Procesar comando de dibujo"""
        action = command.get("action")

        if action == "start_drawing":
            # Auto-cambiar color en cada trazo nuevo
            if self.auto_color_change:
                self.drawing_controller.random_color()

            mode = command["mode"]
            point = command["point"]
            color = command["color"]

            if mode == "circle":
                # Crear círculo
                self.renderer.add_circle(
                    point[0],
                    point[1],
                    radius=command["radius"],
                    color=color,
                    thickness=2,
                )

            elif mode == "mandala":
                # Iniciar mandala
                center_x, center_y = self.width // 2, self.height // 2
                self.renderer.start_mandala(
                    center_x, center_y, symmetry=command["symmetry"], color=color
                )
                self.renderer.add_mandala_point(point[0], point[1])

            elif mode == "sphere":
                # Crear esfera 3D
                self.renderer.add_sphere(point[0], point[1], radius=80, color=color)

        elif action == "continue_drawing":
            mode = command["mode"]
            point = command["point"]

            if mode == "circle":
                # Agregar más círculos en el trail
                self.renderer.add_circle(
                    point[0],
                    point[1],
                    radius=command["radius"],
                    color=command["color"],
                    thickness=2,
                )

            elif mode == "mandala":
                # Agregar punto al mandala
                self.renderer.add_mandala_point(point[0], point[1])

        elif action == "end_drawing":
            # Finalizar mandala si estaba en proceso
            self.renderer.finish_mandala()

        elif action == "peace_sign":
            # Signo de la paz: cambiar modo
            current_time = time.time()
            if current_time - self.last_peace_sign > 0.5:  # Cooldown 0.5s
                modes = ["circle", "mandala", "sphere"]
                current_idx = modes.index(self.drawing_controller.state.mode)
                next_idx = (current_idx + 1) % len(modes)
                self.drawing_controller.set_mode(modes[next_idx])
                self.last_peace_sign = current_time
                print(f"✌️ Modo cambiado a: {modes[next_idx].upper()}")

        elif action == "clear":
            current_time = time.time()
            if current_time - self.last_clear > 1.0:  # Cooldown 1s
                self.renderer.clear_all()
                self.last_clear = current_time
                print("✋ Canvas limpiado")

    def run(self):
        """Ejecutar aplicación"""
        print("\n" + "=" * 70)
        print("AIRCANVAS - Pintar en el Aire")
        print("=" * 70)
        print("\n✨ Modos disponibles:")
        print("  1. Círculos - Dibuja círculos al mover el dedo")
        print("  2. Mandala - Genera patrones con simetría radial (EFECTO NEÓN)")
        print("  3. Esfera 3D - Crea esferas que rotan en 3D")
        print("\n👆 Gestos:")
        print("  Índice solo = Dibujar (color aleatorio en cada trazo)")
        print("  ✌️ Paz (2 dedos) = Cambiar modo automáticamente")
        print("  ✋ Palma abierta = Limpiar canvas")
        print("\n⌨️  Controles:")
        print("  1/2/3 = Cambiar modo")
        print("  +/- = Ajustar simetría (mandalas)")
        print("  V = Mostrar/ocultar video")
        print("  H = Mostrar/ocultar ayuda")
        print("  Q = Salir")
        print("=" * 70 + "\n")

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("❌ Error: No se pudo abrir la cámara")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        print("Sistema iniciado. ¡Empieza a dibujar!\n")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                self.frame_count += 1

                # Detectar manos
                hands = self.hand_tracker.detect_hands(frame)

                # Procesar gestos si hay mano
                if hands:
                    hand = hands[0]
                    command = self.drawing_controller.process_hand(hand)
                    self.process_drawing_command(command)
                else:
                    # Sin manos, finalizar dibujo si estaba activo
                    if self.drawing_controller.state.is_drawing:
                        self.drawing_controller.state.reset()
                        self.renderer.finish_mandala()

                # Actualizar geometrías
                self.renderer.update()

                # Renderizar
                if self.show_video:
                    canvas = self.renderer.render(background=frame)
                else:
                    canvas = self.renderer.render()

                # Dibujar UI
                display = self.draw_ui(canvas)

                # Calcular FPS
                if self.frame_count % 10 == 0:
                    current_time = time.time()
                    elapsed = current_time - self.last_fps_time
                    self.fps = 10 / elapsed if elapsed > 0 else 0
                    self.last_fps_time = current_time

                cv2.imshow("AirCanvas - Pintar en el Aire", display)

                # Input de teclado
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break

                elif key == ord("1"):
                    self.drawing_controller.set_mode("circle")
                    print("Modo: CÍRCULOS")

                elif key == ord("2"):
                    self.drawing_controller.set_mode("mandala")
                    print("Modo: MANDALA")

                elif key == ord("3"):
                    self.drawing_controller.set_mode("sphere")
                    print("Modo: ESFERA 3D")

                elif key == ord("+") or key == ord("="):
                    self.drawing_controller.state.mandala_symmetry += 1
                    print(f"Simetría: {self.drawing_controller.state.mandala_symmetry}x")

                elif key == ord("-"):
                    self.drawing_controller.state.mandala_symmetry = max(
                        2, self.drawing_controller.state.mandala_symmetry - 1
                    )
                    print(f"Simetría: {self.drawing_controller.state.mandala_symmetry}x")

                elif key == ord("v"):
                    self.show_video = not self.show_video
                    print(f"Video: {'ON' if self.show_video else 'OFF'}")

                elif key == ord("h"):
                    self.show_help = not self.show_help

        except KeyboardInterrupt:
            print("\nInterrumpido por usuario")

        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("\n✅ AirCanvas finalizado")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="AirCanvas - Pintar en el Aire")
    parser.add_argument("--camera", "-c", type=int, default=0, help="Índice de cámara")
    args = parser.parse_args()

    app = AirCanvas(camera_index=args.camera)
    app.run()


if __name__ == "__main__":
    main()
