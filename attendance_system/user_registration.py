#!/usr/bin/env python3
"""
Sistema de Registro de Usuarios con Reconocimiento Facial

Crea "huellas faciales" (embeddings) para identificar usuarios automáticamente.
"""

import json
import os
import sys
from datetime import datetime

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesturecam.vision.face_mesh import FaceMeshTracker


class FaceEmbeddingExtractor:
    """
    Extrae embeddings (vectores únicos) de rostros para reconocimiento.

    Usa los 468 landmarks de Face Mesh para crear una "huella facial" única.
    """

    def __init__(self):
        self.tracker = FaceMeshTracker(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True,
        )

        # Índices de landmarks clave para embedding
        # Usamos puntos estables que no cambian con expresiones
        self.key_landmarks = [
            # Contorno facial
            10,
            338,
            297,
            332,
            284,
            251,
            389,
            356,
            454,
            323,
            # Ojos
            33,
            133,
            263,
            362,
            # Nariz
            1,
            4,
            5,
            6,
            # Boca (puntos externos estables)
            61,
            291,
            0,
            17,
            # Cejas
            70,
            63,
            105,
            66,
            107,
            336,
            296,
            334,
            293,
            300,
        ]

    def extract_embedding(self, frame: np.ndarray) -> np.ndarray | None:
        """
        Extrae embedding de 128 dimensiones del rostro en el frame.

        Returns:
            Vector de 128 dimensiones normalizado, o None si no hay cara
        """
        metrics = self.tracker.detect(frame)

        if not metrics.detected or metrics.landmarks_array is None:
            return None

        landmarks = metrics.landmarks_array
        h, w = frame.shape[:2]

        # Normalizar landmarks por tamaño de cara
        x_coords = landmarks[:, 0]
        y_coords = landmarks[:, 1]

        # Bounding box de la cara
        face_width = np.max(x_coords) - np.min(x_coords)
        face_height = np.max(y_coords) - np.min(y_coords)
        center_x = np.mean(x_coords)
        center_y = np.mean(y_coords)

        # Normalizar cada landmark respecto al centro y tamaño de cara
        normalized_landmarks = []
        for idx in self.key_landmarks:
            if idx < len(landmarks):
                lm = landmarks[idx]
                # Normalizar a rango [-1, 1]
                norm_x = (lm[0] - center_x) / (face_width / 2)
                norm_y = (lm[1] - center_y) / (face_height / 2)
                normalized_landmarks.extend([norm_x, norm_y])

        # Agregar métricas adicionales
        embedding_components = (
            normalized_landmarks
            + [
                metrics.avg_ear,  # Forma de ojos
                metrics.mar,  # Forma de boca
                face_width / face_height,  # Aspect ratio de cara
                # Distancias entre puntos clave
                np.linalg.norm(landmarks[33][:2] - landmarks[263][:2])
                / face_width,  # Ancho entre ojos
            ]
        )

        # Pad o truncar a 128 dimensiones
        embedding = np.array(embedding_components[:128])
        if len(embedding) < 128:
            embedding = np.pad(embedding, (0, 128 - len(embedding)))

        # Normalizar L2
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding.astype(np.float32)

    def close(self):
        """Liberar recursos"""
        self.tracker.close()


class UserDatabase:
    """
    Base de datos de usuarios registrados con sus embeddings faciales.
    """

    def __init__(self, db_path: str = "users_database.json"):
        self.db_path = db_path
        self.users = {}  # {user_id: {name, embeddings, metadata}}
        self.load()

    def load(self):
        """Cargar base de datos desde disco"""
        if os.path.exists(self.db_path):
            with open(self.db_path) as f:
                data = json.load(f)
                # Convertir embeddings de lista a numpy array
                for _user_id, user_data in data.items():
                    user_data["embeddings"] = [
                        np.array(emb, dtype=np.float32)
                        for emb in user_data["embeddings"]
                    ]
                self.users = data
                print(f"Base de datos cargada: {len(self.users)} usuarios")

    def save(self):
        """Guardar base de datos a disco"""
        # Convertir numpy arrays a listas para JSON
        data = {}
        for user_id, user_data in self.users.items():
            data[user_id] = {
                "name": user_data["name"],
                "embeddings": [emb.tolist() for emb in user_data["embeddings"]],
                "metadata": user_data["metadata"],
            }

        with open(self.db_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Base de datos guardada: {self.db_path}")

    def add_user(
        self,
        user_id: str,
        name: str,
        embeddings: list[np.ndarray],
        metadata: dict | None = None,
    ):
        """Agregar o actualizar usuario"""
        self.users[user_id] = {
            "name": name,
            "embeddings": embeddings,
            "metadata": metadata or {},
        }
        self.save()

    def get_user(self, user_id: str) -> dict | None:
        """Obtener datos de usuario"""
        return self.users.get(user_id)

    def list_users(self) -> list[dict]:
        """Listar todos los usuarios"""
        return [
            {"id": uid, "name": data["name"], "num_embeddings": len(data["embeddings"])}
            for uid, data in self.users.items()
        ]

    def delete_user(self, user_id: str):
        """Eliminar usuario"""
        if user_id in self.users:
            del self.users[user_id]
            self.save()
            return True
        return False


class FaceRecognizer:
    """
    Reconocimiento facial usando embeddings.
    """

    def __init__(self, database: UserDatabase, similarity_threshold: float = 0.6):
        self.database = database
        self.similarity_threshold = similarity_threshold

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calcular similitud coseno entre dos embeddings"""
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def recognize(
        self, embedding: np.ndarray
    ) -> tuple[str | None, str | None, float]:
        """
        Reconocer usuario por embedding.

        Returns:
            (user_id, name, confidence)
        """
        best_match_id = None
        best_match_name = None
        best_similarity = 0.0

        for user_id, user_data in self.database.users.items():
            # Comparar con todos los embeddings del usuario
            similarities = [
                self.cosine_similarity(embedding, user_emb)
                for user_emb in user_data["embeddings"]
            ]

            # Tomar el máximo
            max_sim = max(similarities) if similarities else 0.0

            if max_sim > best_similarity:
                best_similarity = max_sim
                best_match_id = user_id
                best_match_name = user_data["name"]

        # Verificar umbral
        if best_similarity >= self.similarity_threshold:
            return best_match_id, best_match_name, best_similarity
        else:
            return None, None, best_similarity


def register_new_user(camera_index: int = 0):
    """
    Proceso de registro de nuevo usuario.
    """
    print("\n" + "=" * 60)
    print("REGISTRO DE NUEVO USUARIO")
    print("=" * 60)

    # Solicitar datos del usuario
    name = input("\nIngresa tu nombre completo: ").strip()
    if not name:
        print("Error: El nombre no puede estar vacío")
        return

    user_id = name.lower().replace(" ", "_")

    # Verificar si ya existe
    db = UserDatabase()
    if db.get_user(user_id):
        overwrite = input(f"El usuario '{name}' ya existe. ¿Sobrescribir? (s/n): ")
        if overwrite.lower() != "s":
            print("Registro cancelado")
            return

    print(f"\nUsuario: {name}")
    print(f"ID: {user_id}")
    print("\nVamos a capturar tu rostro desde diferentes ángulos.")
    print("Esto mejora la precisión del reconocimiento.\n")

    input("Presiona ENTER cuando estés listo...")

    # Inicializar
    extractor = FaceEmbeddingExtractor()
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    embeddings = []
    instructions = [
        "Mira directo a la cámara",
        "Gira ligeramente a la IZQUIERDA",
        "Gira ligeramente a la DERECHA",
        "Inclina la cabeza ARRIBA",
        "Inclina la cabeza ABAJO",
    ]

    current_step = 0
    frames_captured = 0
    embeddings_per_pose = 3

    print("\nCapturando rostro...")
    print("Presiona ESPACIO para capturar, Q para salir\n")

    try:
        while current_step < len(instructions):
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            display = frame.copy()
            h, w = display.shape[:2]

            # Instrucción actual
            instruction = instructions[current_step]
            progress = f"{current_step + 1}/{len(instructions)}"

            # Panel de instrucciones
            cv2.rectangle(display, (0, 0), (w, 100), (40, 40, 40), -1)
            cv2.putText(
                display,
                f"Paso {progress}: {instruction}",
                (20, 40),
                cv2.FONT_HERSHEY_DUPLEX,
                0.8,
                (0, 255, 255),
                2,
            )
            cv2.putText(
                display,
                f"Capturas: {frames_captured}/{embeddings_per_pose}",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )

            # Detectar cara
            metrics = extractor.tracker.detect(frame)

            if metrics.detected:
                # Dibujar cara
                display = extractor.tracker.draw_debug_overlay(
                    display,
                    metrics,
                    show_mesh=True,
                    show_eyes=True,
                    show_iris=False,
                    show_metrics=False,
                    show_pose=False,
                )

                cv2.putText(
                    display,
                    "Rostro detectado - Presiona ESPACIO",
                    (20, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    display,
                    "No se detecta rostro",
                    (20, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            cv2.imshow("Registro de Usuario", display)

            key = cv2.waitKey(1) & 0xFF

            if key == ord(" "):  # Espacio
                if metrics.detected:
                    # Extraer embedding
                    embedding = extractor.extract_embedding(frame)
                    if embedding is not None:
                        embeddings.append(embedding)
                        frames_captured += 1
                        print(
                            f"  ✓ Captura {frames_captured}/{embeddings_per_pose} para '{instruction}'"
                        )

                        if frames_captured >= embeddings_per_pose:
                            current_step += 1
                            frames_captured = 0
                else:
                    print("  ✗ No se detectó rostro, intenta de nuevo")

            elif key == ord("q"):
                print("\nRegistro cancelado")
                cap.release()
                cv2.destroyAllWindows()
                extractor.close()
                return

    except KeyboardInterrupt:
        print("\nRegistro interrumpido")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        extractor.close()

    # Guardar usuario
    if len(embeddings) >= 5:
        db.add_user(
            user_id=user_id,
            name=name,
            embeddings=embeddings,
            metadata={
                "registered_at": datetime.now().isoformat(),
                "num_samples": len(embeddings),
            },
        )

        print(f"\n{'=' * 60}")
        print("✅ USUARIO REGISTRADO EXITOSAMENTE")
        print(f"{'=' * 60}")
        print(f"Nombre: {name}")
        print(f"ID: {user_id}")
        print(f"Muestras capturadas: {len(embeddings)}")
        print(
            "\nAhora puedes usar el sistema de asistencia y serás reconocido automáticamente."
        )
    else:
        print(f"\n✗ Error: Se necesitan al menos 5 muestras (tienes {len(embeddings)})")


def test_recognition(camera_index: int = 0):
    """
    Probar reconocimiento facial en tiempo real.
    """
    print("\n" + "=" * 60)
    print("TEST DE RECONOCIMIENTO FACIAL")
    print("=" * 60)

    db = UserDatabase()
    if not db.users:
        print("\n⚠️  No hay usuarios registrados.")
        print("Ejecuta: python user_registration.py --register")
        return

    print(f"\nUsuarios en base de datos: {len(db.users)}")
    for user in db.list_users():
        print(
            f"  • {user['name']} (ID: {user['id']}, {user['num_embeddings']} muestras)"
        )

    print("\nIniciando reconocimiento...")
    input("Presiona ENTER para continuar...")

    extractor = FaceEmbeddingExtractor()
    recognizer = FaceRecognizer(db, similarity_threshold=0.6)

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("\nMira a la cámara. Presiona Q para salir.\n")

    last_recognition = None

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            display = frame.copy()
            h, w = display.shape[:2]

            # Extraer embedding
            embedding = extractor.extract_embedding(frame)

            # Panel superior
            cv2.rectangle(display, (0, 0), (w, 100), (40, 40, 40), -1)

            if embedding is not None:
                # Reconocer
                user_id, name, confidence = recognizer.recognize(embedding)

                if user_id:
                    # Reconocido
                    color = (0, 255, 0)
                    text = f"✓ {name}"
                    conf_text = f"Confianza: {confidence * 100:.1f}%"

                    if last_recognition != user_id:
                        print(
                            f"  ✓ Reconocido: {name} (confianza: {confidence * 100:.1f}%)"
                        )
                        last_recognition = user_id
                else:
                    # No reconocido
                    color = (0, 165, 255)
                    text = "Desconocido"
                    conf_text = f"Máxima similitud: {confidence * 100:.1f}%"

                    if last_recognition != "unknown":
                        print(
                            f"  ? Usuario desconocido (similitud máx: {confidence * 100:.1f}%)"
                        )
                        last_recognition = "unknown"

                cv2.putText(
                    display, text, (20, 45), cv2.FONT_HERSHEY_DUPLEX, 1.2, color, 2
                )
                cv2.putText(
                    display,
                    conf_text,
                    (20, 75),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (200, 200, 200),
                    1,
                )
            else:
                cv2.putText(
                    display,
                    "No se detecta rostro",
                    (20, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2,
                )
                last_recognition = None

            cv2.imshow("Test de Reconocimiento", display)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    except KeyboardInterrupt:
        print("\nTest interrumpido")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        extractor.close()


def list_users():
    """Listar usuarios registrados"""
    db = UserDatabase()

    if not db.users:
        print("\n⚠️  No hay usuarios registrados.")
        return

    print("\n" + "=" * 60)
    print(f"USUARIOS REGISTRADOS ({len(db.users)})")
    print("=" * 60)

    for user in db.list_users():
        user_data = db.get_user(user["id"])
        print(f"\n📋 {user['name']}")
        print(f"   ID: {user['id']}")
        print(f"   Muestras: {user['num_embeddings']}")
        print(f"   Registrado: {user_data['metadata'].get('registered_at', 'N/A')}")


def delete_user_interactive():
    """Eliminar usuario interactivamente"""
    db = UserDatabase()

    if not db.users:
        print("\n⚠️  No hay usuarios registrados.")
        return

    list_users()

    user_id = input("\nIngresa el ID del usuario a eliminar: ").strip()

    if db.get_user(user_id):
        confirm = input(
            f"¿Confirmar eliminación de '{db.get_user(user_id)['name']}'? (s/n): "
        )
        if confirm.lower() == "s":
            db.delete_user(user_id)
            print("✓ Usuario eliminado")
    else:
        print("✗ Usuario no encontrado")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Sistema de Registro de Usuarios")
    parser.add_argument(
        "--register", "-r", action="store_true", help="Registrar nuevo usuario"
    )
    parser.add_argument(
        "--test", "-t", action="store_true", help="Probar reconocimiento facial"
    )
    parser.add_argument("--list", "-l", action="store_true", help="Listar usuarios")
    parser.add_argument("--delete", "-d", action="store_true", help="Eliminar usuario")
    parser.add_argument("--camera", "-c", type=int, default=0, help="Índice de cámara")

    args = parser.parse_args()

    if args.register:
        register_new_user(args.camera)
    elif args.test:
        test_recognition(args.camera)
    elif args.list:
        list_users()
    elif args.delete:
        delete_user_interactive()
    else:
        # Menú interactivo
        while True:
            print("\n" + "=" * 60)
            print("SISTEMA DE REGISTRO DE USUARIOS")
            print("=" * 60)
            print("\n1. Registrar nuevo usuario")
            print("2. Probar reconocimiento")
            print("3. Listar usuarios")
            print("4. Eliminar usuario")
            print("5. Salir")

            choice = input("\nSelecciona una opción: ").strip()

            if choice == "1":
                register_new_user(args.camera)
            elif choice == "2":
                test_recognition(args.camera)
            elif choice == "3":
                list_users()
            elif choice == "4":
                delete_user_interactive()
            elif choice == "5":
                break


if __name__ == "__main__":
    main()
