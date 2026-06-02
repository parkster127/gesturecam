#!/usr/bin/env python3
"""
🌮 CHUY DETECTOR 3000 🌮
Aplicación épica para detectar si la persona frente a la cámara es EL CHUY.

Uso:
1. Primero ejecuta con --register para registrar a El Chuy.
2. Luego ejecuta normal para detectar.
"""

import json
import math
import os
import sys

import cv2
import numpy as np

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gesturecam.vision.face_mesh import FaceMeshTracker

# Archivo donde guardamos el embedding de El Chuy
CHUY_DATA_FILE = os.path.join(os.path.dirname(__file__), "chuy_data.json")


class ChuyDetector:
    def __init__(self):
        self.tracker = FaceMeshTracker(min_detection_confidence=0.7)
        self.chuy_embedding = None
        self.threshold = 0.75  # Similitud mínima para ser El Chuy
        self.load_chuy_data()

        # Animación
        self.animation_frame = 0
        self.last_result = None
        self.result_start_time = 0

    def load_chuy_data(self):
        """Cargar el embedding de El Chuy si existe"""
        if os.path.exists(CHUY_DATA_FILE):
            with open(CHUY_DATA_FILE) as f:
                data = json.load(f)
                self.chuy_embedding = np.array(data["embedding"])
                print(f"✅ Datos de El Chuy cargados ({len(self.chuy_embedding)} dimensiones)")
        else:
            print("⚠️ El Chuy no está registrado. Ejecuta con --register primero.")

    def save_chuy_data(self, embedding):
        """Guardar el embedding de El Chuy"""
        with open(CHUY_DATA_FILE, "w") as f:
            json.dump({"embedding": embedding.tolist(), "name": "El Chuy"}, f)
        print("✅ El Chuy ha sido registrado exitosamente!")

    def extract_embedding(self, landmarks):
        """Extraer un vector de características de los landmarks"""
        if landmarks is None or len(landmarks) < 468:
            return None

        # Normalizar landmarks relativos al centro de la cara
        center = np.mean(landmarks[:, :2], axis=0)
        normalized = landmarks[:, :2] - center

        # Escalar por el tamaño de la cara
        scale = np.max(np.abs(normalized))
        if scale > 0:
            normalized = normalized / scale

        # Aplanar a un vector 1D
        return normalized.flatten()

    def cosine_similarity(self, a, b):
        """Calcular similitud de coseno entre dos vectores"""
        if a is None or b is None:
            return 0
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0
        return dot / (norm_a * norm_b)

    def register_chuy(self):
        """Modo de registro: Capturar la cara de El Chuy"""
        print("\n" + "=" * 50)
        print("🌮 REGISTRO DE EL CHUY 🌮")
        print("=" * 50)
        print("Instrucciones:")
        print("  1. Pon a El Chuy frente a la cámara")
        print("  2. Presiona [ESPACIO] para capturar")
        print("  3. Se tomarán 5 fotos desde diferentes ángulos")
        print("  4. Presiona [Q] para cancelar")
        print("=" * 50 + "\n")

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        embeddings = []
        target_samples = 5

        while len(embeddings) < target_samples:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            display = frame.copy()

            # Detectar cara
            metrics = self.tracker.detect(frame)

            # UI
            cv2.putText(
                display,
                f"REGISTRANDO A EL CHUY ({len(embeddings)}/{target_samples})",
                (20, 50),
                cv2.FONT_HERSHEY_DUPLEX,
                1.2,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                display,
                "Presiona [ESPACIO] para capturar",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

            if metrics.detected:
                # Dibujar rectángulo verde
                x, y, w, h = metrics.bbox
                cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 3)
                cv2.putText(
                    display,
                    "CARA DETECTADA - LISTO!",
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    display,
                    "Buscando cara de El Chuy...",
                    (20, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Registro de El Chuy", display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord(" ") and metrics.detected:
                # Capturar embedding
                emb = self.extract_embedding(metrics.landmarks_array)
                if emb is not None:
                    embeddings.append(emb)
                    print(f"📸 Captura {len(embeddings)}/{target_samples}")
                    # Flash visual
                    cv2.rectangle(display, (0, 0), (1280, 720), (0, 255, 0), 50)
                    cv2.imshow("Registro de El Chuy", display)
                    cv2.waitKey(200)

        cap.release()
        cv2.destroyAllWindows()

        if len(embeddings) >= 3:
            # Promediar los embeddings
            avg_embedding = np.mean(embeddings, axis=0)
            self.save_chuy_data(avg_embedding)
            self.chuy_embedding = avg_embedding
            return True
        else:
            print("❌ No se capturaron suficientes muestras.")
            return False

    def draw_epic_text(self, frame, is_chuy, similarity):
        """Dibujar texto épico con efectos"""
        h, w = frame.shape[:2]
        self.animation_frame += 1

        # Efecto de pulso
        pulse = abs(math.sin(self.animation_frame * 0.1)) * 0.3 + 0.7

        if is_chuy:
            # ¡ES EL CHUY! - Texto verde épico
            text = "ES EL CHUY!!!"

            # Tamaño animado
            scale = 2.5 + math.sin(self.animation_frame * 0.15) * 0.3

            # Color verde brillante con variación
            g = int(200 + 55 * pulse)
            color = (0, g, 0)

            # Sombra
            cv2.putText(
                frame,
                text,
                (w // 2 - 280 + 5, h // 2 + 5),
                cv2.FONT_HERSHEY_DUPLEX,
                scale,
                (0, 50, 0),
                8,
            )

            # Texto principal
            cv2.putText(
                frame,
                text,
                (w // 2 - 280, h // 2),
                cv2.FONT_HERSHEY_DUPLEX,
                scale,
                color,
                6,
            )

            # Emojis simulados con texto
            cv2.putText(
                frame,
                "< < <",
                (w // 2 - 350, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 255),
                3,
            )
            cv2.putText(
                frame,
                "> > >",
                (w // 2 + 250, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.5,
                (0, 255, 255),
                3,
            )

            # Porcentaje de match
            cv2.putText(
                frame,
                f"MATCH: {similarity * 100:.1f}%",
                (w // 2 - 100, h // 2 + 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (100, 255, 100),
                2,
            )

            # Borde verde
            cv2.rectangle(frame, (10, 10), (w - 10, h - 10), (0, 255, 0), 8)

        else:
            # NO ES EL CHUY - Texto rojo
            text = "NO ES EL CHUY"

            scale = 2.0
            color = (0, 0, 255)

            # Sombra
            cv2.putText(
                frame,
                text,
                (w // 2 - 250 + 3, h // 2 + 3),
                cv2.FONT_HERSHEY_DUPLEX,
                scale,
                (0, 0, 100),
                6,
            )

            # Texto principal
            cv2.putText(
                frame,
                text,
                (w // 2 - 250, h // 2),
                cv2.FONT_HERSHEY_DUPLEX,
                scale,
                color,
                4,
            )

            # Cara triste
            cv2.putText(
                frame,
                ":(",
                (w // 2 - 30, h // 2 + 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                2.0,
                (0, 0, 255),
                4,
            )

            # Borde rojo
            cv2.rectangle(frame, (10, 10), (w - 10, h - 10), (0, 0, 255), 5)

    def run(self):
        """Modo detección: ¿Es El Chuy?"""
        if self.chuy_embedding is None:
            print("❌ Primero debes registrar a El Chuy con: --register")
            return

        print("\n" + "=" * 50)
        print("🌮 CHUY DETECTOR 3000 - ACTIVO 🌮")
        print("=" * 50)
        print("Buscando a El Chuy...")
        print("Presiona [Q] para salir")
        print("=" * 50 + "\n")

        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            display = frame.copy()

            # Detectar cara
            metrics = self.tracker.detect(frame)

            is_chuy = False
            similarity = 0

            if metrics.detected:
                # Extraer embedding actual
                current_emb = self.extract_embedding(metrics.landmarks_array)

                if current_emb is not None:
                    # Comparar con El Chuy
                    similarity = self.cosine_similarity(current_emb, self.chuy_embedding)
                    is_chuy = similarity > self.threshold

                # Dibujar bbox
                x, y, w, h = metrics.bbox
                color = (0, 255, 0) if is_chuy else (0, 0, 255)
                cv2.rectangle(display, (x, y), (x + w, y + h), color, 3)

            # Dibujar resultado épico
            if metrics.detected:
                self.draw_epic_text(display, is_chuy, similarity)
            else:
                cv2.putText(
                    display,
                    "Buscando caras...",
                    (20, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (200, 200, 200),
                    2,
                )

            cv2.imshow("CHUY DETECTOR 3000", display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


def show_start_screen():
    """Mostrar pantalla de inicio con menú visual"""
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    selected = None
    animation_frame = 0

    # Verificar si El Chuy ya está registrado
    chuy_registered = os.path.exists(CHUY_DATA_FILE)

    while selected is None:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        # Oscurecer el fondo
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (1280, 720), (0, 0, 0), -1)
        frame = cv2.addWeighted(frame, 0.3, overlay, 0.7, 0)

        h, w = frame.shape[:2]
        animation_frame += 1

        # Título animado
        pulse = abs(math.sin(animation_frame * 0.05)) * 0.2 + 0.8
        title_color = (0, int(255 * pulse), int(255 * pulse))

        cv2.putText(
            frame,
            "CHUY DETECTOR 3000",
            (w // 2 - 320, 120),
            cv2.FONT_HERSHEY_DUPLEX,
            2.0,
            (0, 50, 50),
            8,
        )
        cv2.putText(
            frame,
            "CHUY DETECTOR 3000",
            (w // 2 - 320, 120),
            cv2.FONT_HERSHEY_DUPLEX,
            2.0,
            title_color,
            4,
        )

        # Taco emoji simulado
        cv2.putText(
            frame,
            "{ }",
            (w // 2 - 380, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 200, 255),
            3,
        )
        cv2.putText(
            frame,
            "{ }",
            (w // 2 + 300, 125),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 200, 255),
            3,
        )

        # Estado de registro
        if chuy_registered:
            cv2.putText(
                frame,
                "Estado: El Chuy esta registrado",
                (w // 2 - 200, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )
        else:
            cv2.putText(
                frame,
                "Estado: El Chuy NO esta registrado",
                (w // 2 - 220, 180),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2,
            )

        # Botones
        btn_y = 300
        btn_h = 80
        btn_w = 500
        btn_x = w // 2 - btn_w // 2

        # Botón 1: Registrar
        cv2.rectangle(frame, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (50, 50, 50), -1)
        cv2.rectangle(frame, (btn_x, btn_y), (btn_x + btn_w, btn_y + btn_h), (0, 255, 255), 3)
        cv2.putText(
            frame,
            "[1] REGISTRAR A EL CHUY",
            (btn_x + 80, btn_y + 52),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 255),
            2,
        )

        # Botón 2: Detectar
        btn_y2 = btn_y + btn_h + 30
        btn_color = (0, 255, 0) if chuy_registered else (100, 100, 100)
        cv2.rectangle(frame, (btn_x, btn_y2), (btn_x + btn_w, btn_y2 + btn_h), (50, 50, 50), -1)
        cv2.rectangle(frame, (btn_x, btn_y2), (btn_x + btn_w, btn_y2 + btn_h), btn_color, 3)
        cv2.putText(
            frame,
            "[2] DETECTAR (Es El Chuy?)",
            (btn_x + 60, btn_y2 + 52),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            btn_color,
            2,
        )

        if not chuy_registered:
            cv2.putText(
                frame,
                "(Primero registra a El Chuy)",
                (btn_x + 100, btn_y2 + btn_h + 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (150, 150, 150),
                1,
            )

        # Botón 3: Salir
        btn_y3 = btn_y2 + btn_h + 50
        cv2.rectangle(frame, (btn_x, btn_y3), (btn_x + btn_w, btn_y3 + btn_h), (50, 50, 50), -1)
        cv2.rectangle(frame, (btn_x, btn_y3), (btn_x + btn_w, btn_y3 + btn_h), (0, 0, 255), 3)
        cv2.putText(
            frame,
            "[Q] SALIR",
            (btn_x + 180, btn_y3 + 52),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2,
        )

        # Instrucciones
        cv2.putText(
            frame,
            "Presiona 1, 2 o Q para seleccionar",
            (w // 2 - 220, h - 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (200, 200, 200),
            2,
        )

        cv2.imshow("CHUY DETECTOR 3000", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("1"):
            selected = "register"
        elif key == ord("2") and chuy_registered:
            selected = "detect"
        elif key == ord("q"):
            selected = "quit"

    cap.release()
    return selected


def main():
    print("\n" + "=" * 50)
    print("🌮 CHUY DETECTOR 3000 🌮")
    print("=" * 50)

    # Mostrar pantalla de inicio
    choice = show_start_screen()

    if choice == "quit":
        print("👋 Hasta luego!")
        cv2.destroyAllWindows()
        return

    detector = ChuyDetector()

    if choice == "register":
        detector.register_chuy()
        # Después de registrar, preguntar si quiere detectar
        print("\n¿Quieres probar la detección ahora? Ejecuta de nuevo el programa.")
    elif choice == "detect":
        detector.run()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
