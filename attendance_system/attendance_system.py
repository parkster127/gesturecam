#!/usr/bin/env python3
"""
Sistema de Asistencia con Detección Facial Avanzada
====================================================

Características:
- Detección de presencia en tiempo real
- Verificación de atención (ojos abiertos)
- Detección de fatiga/somnolencia
- Registro de eventos
- Dashboard de monitoreo

Casos de uso:
1. Asistencia escolar/laboral
2. Monitoreo de conductores
3. Control de acceso
4. Supervisión de exámenes online
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesturecam.vision.face_mesh import FaceMeshTracker, FaceMetrics


@dataclass
class AttendanceEvent:
    """Evento de asistencia"""

    timestamp: str
    event_type: str  # 'entry', 'exit', 'blink', 'drowsy', 'alert'
    confidence: float
    ear_avg: float
    attention_score: float  # 0-100
    notes: str = ""


@dataclass
class AttendanceSession:
    """Sesión de asistencia de un usuario"""

    session_id: str
    start_time: str
    end_time: Optional[str] = None
    total_duration: float = 0.0  # segundos

    # Estadísticas
    total_frames: int = 0
    frames_detected: int = 0
    blink_count: int = 0
    drowsy_count: int = 0
    attention_alerts: int = 0

    # Métricas promedio
    avg_ear: float = 0.0
    avg_attention_score: float = 0.0

    events: List[AttendanceEvent] = None

    def __post_init__(self):
        if self.events is None:
            self.events = []


class AttendanceSystem:
    """
    Sistema de asistencia con detección facial avanzada
    """

    def __init__(
        self,
        camera_index: int = 0,
        session_name: str = "default",
        output_dir: str = "attendance_logs",
    ):
        self.camera_index = camera_index
        self.session_name = session_name
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Face tracker
        self.tracker = FaceMeshTracker(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True,
        )

        # Umbrales configurables
        self.ear_threshold = 0.21  # Por debajo = ojos cerrados
        self.drowsy_threshold = 0.18  # Muy bajo = somnolencia
        self.blink_duration_threshold = 0.4  # segundos
        self.absence_threshold = 3.0  # segundos sin detección = ausente

        # Estado
        self.session: Optional[AttendanceSession] = None
        self.is_running = False
        self.last_detection_time = 0
        self.blink_start_time = None
        self.ear_history = []
        self.attention_history = []

        # Estadísticas en tiempo real
        self.current_attention_score = 100.0
        self.is_present = False
        self.is_drowsy = False

    def start_session(self) -> str:
        """Iniciar nueva sesión de asistencia"""
        session_id = f"{self.session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.session = AttendanceSession(
            session_id=session_id, start_time=datetime.now().isoformat()
        )

        self.is_running = True
        self.is_present = False

        # Log evento de inicio
        self._log_event("session_start", 1.0, 0.0, 100.0, "Sesión iniciada")

        print(f"\n{'=' * 60}")
        print(f"SESIÓN DE ASISTENCIA INICIADA: {session_id}")
        print(f"{'=' * 60}\n")

        return session_id

    def end_session(self):
        """Finalizar sesión y guardar datos"""
        if not self.session:
            return

        self.session.end_time = datetime.now().isoformat()

        # Calcular duración total
        start = datetime.fromisoformat(self.session.start_time)
        end = datetime.fromisoformat(self.session.end_time)
        self.session.total_duration = (end - start).total_seconds()

        # Calcular promedios finales
        if self.ear_history:
            self.session.avg_ear = np.mean(self.ear_history)
        if self.attention_history:
            self.session.avg_attention_score = np.mean(self.attention_history)

        # Log evento final
        self._log_event(
            "session_end",
            1.0,
            self.session.avg_ear,
            self.session.avg_attention_score,
            "Sesión finalizada",
        )

        # Guardar sesión
        self._save_session()

        self.is_running = False

        print(f"\n{'=' * 60}")
        print(f"SESIÓN FINALIZADA")
        print(f"{'=' * 60}")
        self._print_session_summary()

    def _log_event(
        self,
        event_type: str,
        confidence: float,
        ear: float,
        attention: float,
        notes: str = "",
    ):
        """Registrar evento"""
        if not self.session:
            return

        event = AttendanceEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            confidence=confidence,
            ear_avg=ear,
            attention_score=attention,
            notes=notes,
        )

        self.session.events.append(event)

    def _calculate_attention_score(self, metrics: FaceMetrics) -> float:
        """
        Calcular score de atención (0-100)

        Factores:
        - Ojos abiertos: +40
        - EAR alto: +30
        - Sin somnolencia: +30
        """
        score = 0.0

        # Ojos abiertos
        if metrics.left_eye.is_open and metrics.right_eye.is_open:
            score += 40.0
        elif metrics.left_eye.is_open or metrics.right_eye.is_open:
            score += 20.0

        # EAR normalizado (0.15-0.35 -> 0-30)
        ear_score = ((metrics.avg_ear - 0.15) / 0.20) * 30
        score += max(0, min(30, ear_score))

        # No somnolencia
        if metrics.avg_ear > self.drowsy_threshold + 0.05:
            score += 30.0
        elif metrics.avg_ear > self.drowsy_threshold:
            score += 15.0

        return max(0.0, min(100.0, score))

    def _detect_drowsiness(self, metrics: FaceMetrics) -> bool:
        """Detectar somnolencia"""
        # EAR muy bajo por varios frames consecutivos
        if metrics.avg_ear < self.drowsy_threshold:
            # Verificar histórico reciente
            recent = (
                self.ear_history[-10:]
                if len(self.ear_history) >= 10
                else self.ear_history
            )
            if recent and np.mean(recent) < self.drowsy_threshold + 0.02:
                return True
        return False

    def _detect_blink(self, metrics: FaceMetrics, current_time: float) -> bool:
        """Detectar parpadeo"""
        eyes_closed = not metrics.left_eye.is_open and not metrics.right_eye.is_open

        if eyes_closed:
            if self.blink_start_time is None:
                self.blink_start_time = current_time
            return False
        else:
            # Ojos abiertos
            if self.blink_start_time is not None:
                blink_duration = current_time - self.blink_start_time
                self.blink_start_time = None

                # Si el cierre fue corto, es un parpadeo
                if 0.1 < blink_duration < self.blink_duration_threshold:
                    return True

        return False

    def process_frame(self, frame: np.ndarray, current_time: float) -> np.ndarray:
        """Procesar frame y actualizar estado"""
        if not self.is_running:
            return frame

        # Detectar cara
        metrics = self.tracker.detect(frame)

        self.session.total_frames += 1

        if metrics.detected:
            self.session.frames_detected += 1
            self.last_detection_time = current_time

            # Actualizar estado
            was_present = self.is_present
            self.is_present = True

            # Evento de entrada si no estaba presente
            if not was_present:
                self._log_event(
                    "entry", 1.0, metrics.avg_ear, 100.0, "Usuario detectado"
                )

            # Actualizar historiales
            self.ear_history.append(metrics.avg_ear)
            if len(self.ear_history) > 100:
                self.ear_history.pop(0)

            # Calcular atención
            attention = self._calculate_attention_score(metrics)
            self.current_attention_score = attention
            self.attention_history.append(attention)
            if len(self.attention_history) > 100:
                self.attention_history.pop(0)

            # Detectar parpadeo
            if self._detect_blink(metrics, current_time):
                self.session.blink_count += 1
                self._log_event(
                    "blink", 1.0, metrics.avg_ear, attention, "Parpadeo detectado"
                )

            # Detectar somnolencia
            is_drowsy = self._detect_drowsiness(metrics)
            if is_drowsy and not self.is_drowsy:
                self.session.drowsy_count += 1
                self._log_event(
                    "drowsy", 1.0, metrics.avg_ear, attention, "Somnolencia detectada"
                )
            self.is_drowsy = is_drowsy

            # Alerta de baja atención
            if attention < 50 and self.session.total_frames % 30 == 0:
                self.session.attention_alerts += 1
                self._log_event(
                    "low_attention",
                    1.0,
                    metrics.avg_ear,
                    attention,
                    f"Atención baja: {attention:.1f}%",
                )

        else:
            # No detectado
            if (
                self.is_present
                and (current_time - self.last_detection_time) > self.absence_threshold
            ):
                self.is_present = False
                self._log_event("exit", 0.0, 0.0, 0.0, "Usuario ausente")

        # Dibujar overlay
        display = self._draw_overlay(frame, metrics)

        return display

    def _draw_overlay(self, frame: np.ndarray, metrics: FaceMetrics) -> np.ndarray:
        """Dibujar overlay de información"""
        display = frame.copy()
        h, w = frame.shape[:2]

        # Panel superior - Estado
        panel_h = 120
        overlay = np.zeros((panel_h, w, 3), dtype=np.uint8)
        overlay[:] = (40, 40, 40)

        # Estado de presencia
        presence_color = (0, 255, 0) if self.is_present else (0, 0, 255)
        presence_text = "PRESENTE" if self.is_present else "AUSENTE"
        cv2.putText(
            overlay,
            presence_text,
            (20, 35),
            cv2.FONT_HERSHEY_DUPLEX,
            1.0,
            presence_color,
            2,
        )

        # Atención
        attention_color = (
            (0, 255, 0)
            if self.current_attention_score > 70
            else (0, 255, 255)
            if self.current_attention_score > 50
            else (0, 0, 255)
        )
        cv2.putText(
            overlay,
            f"Atencion: {self.current_attention_score:.0f}%",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            attention_color,
            2,
        )

        # Barra de atención
        bar_x, bar_y = 20, 85
        bar_w, bar_h = 200, 20
        cv2.rectangle(
            overlay, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (100, 100, 100), -1
        )
        fill_w = int((self.current_attention_score / 100) * bar_w)
        cv2.rectangle(
            overlay,
            (bar_x, bar_y),
            (bar_x + fill_w, bar_y + bar_h),
            attention_color,
            -1,
        )

        # Estadísticas
        stats_x = w - 280
        cv2.putText(
            overlay,
            f"Sesion: {self.session.session_id[:20]}...",
            (stats_x, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (200, 200, 200),
            1,
        )

        duration = (
            time.time() - datetime.fromisoformat(self.session.start_time).timestamp()
        )
        duration_str = str(timedelta(seconds=int(duration)))
        cv2.putText(
            overlay,
            f"Duracion: {duration_str}",
            (stats_x, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (200, 200, 200),
            1,
        )
        cv2.putText(
            overlay,
            f"Parpadeos: {self.session.blink_count}",
            (stats_x, 65),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (200, 200, 200),
            1,
        )
        cv2.putText(
            overlay,
            f"Alertas: {self.session.drowsy_count}",
            (stats_x, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (200, 200, 200),
            1,
        )

        # Alerta de somnolencia
        if self.is_drowsy:
            cv2.rectangle(
                overlay, (w // 2 - 150, 10), (w // 2 + 150, 50), (0, 0, 255), -1
            )
            cv2.putText(
                overlay,
                "ALERTA: SOMNOLENCIA!",
                (w // 2 - 130, 35),
                cv2.FONT_HERSHEY_DUPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

        # Combinar overlay con frame
        display[0:panel_h] = cv2.addWeighted(display[0:panel_h], 0.3, overlay, 0.7, 0)

        # Dibujar detección facial si está presente
        if metrics.detected:
            display = self.tracker.draw_debug_overlay(
                display,
                metrics,
                show_mesh=False,
                show_eyes=True,
                show_iris=True,
                show_metrics=False,
                show_pose=False,
            )

            # EAR actual
            cv2.putText(
                display,
                f"EAR: {metrics.avg_ear:.3f}",
                (20, panel_h + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )

        return display

    def _save_session(self):
        """Guardar datos de la sesión"""
        filename = os.path.join(self.output_dir, f"{self.session.session_id}.json")

        # Convertir a dict
        data = asdict(self.session)

        with open(filename, "w") as f:
            json.dump(data, f, indent=2, default=str)

        print(f"\nSesión guardada: {filename}")

    def _print_session_summary(self):
        """Imprimir resumen de sesión"""
        print(f"ID: {self.session.session_id}")
        print(f"Duración: {timedelta(seconds=int(self.session.total_duration))}")
        print(f"Frames procesados: {self.session.total_frames}")
        print(
            f"Tasa de detección: {self.session.frames_detected / self.session.total_frames * 100:.1f}%"
        )
        print(f"Parpadeos: {self.session.blink_count}")
        print(f"Alertas de somnolencia: {self.session.drowsy_count}")
        print(f"Alertas de atención: {self.session.attention_alerts}")
        print(f"EAR promedio: {self.session.avg_ear:.3f}")
        print(f"Atención promedio: {self.session.avg_attention_score:.1f}%")
        print(f"Eventos registrados: {len(self.session.events)}")

    def run(self, duration_minutes: Optional[float] = None):
        """
        Ejecutar sistema de asistencia

        Args:
            duration_minutes: Duración en minutos (None = indefinido)
        """
        self.start_session()

        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            print("ERROR: No se pudo abrir la cámara")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        end_time = None
        if duration_minutes:
            end_time = time.time() + (duration_minutes * 60)

        print("\nControles:")
        print("  q - Finalizar sesión")
        print("  s - Guardar snapshot")
        print("  r - Resetear estadísticas de atención")
        print("")

        try:
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)
                current_time = time.time()

                # Procesar frame
                display = self.process_frame(frame, current_time)

                cv2.imshow("Sistema de Asistencia", display)

                # Verificar duración
                if end_time and current_time > end_time:
                    print("\nDuración completada")
                    break

                # Input
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("s"):
                    filename = (
                        f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    )
                    cv2.imwrite(os.path.join(self.output_dir, filename), display)
                    print(f"Snapshot guardado: {filename}")
                elif key == ord("r"):
                    self.attention_history.clear()
                    print("Estadísticas reseteadas")

        except KeyboardInterrupt:
            print("\nInterrumpido por usuario")

        finally:
            self.end_session()
            cap.release()
            cv2.destroyAllWindows()


def main():
    """Punto de entrada"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sistema de Asistencia con Detección Facial"
    )
    parser.add_argument("--camera", "-c", type=int, default=0, help="Índice de cámara")
    parser.add_argument(
        "--session",
        "-s",
        type=str,
        default="clase",
        help="Nombre de sesión (ej: clase, examen, conductor)",
    )
    parser.add_argument("--duration", "-d", type=float, help="Duración en minutos")
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="attendance_logs",
        help="Directorio de salida",
    )

    args = parser.parse_args()

    system = AttendanceSystem(
        camera_index=args.camera, session_name=args.session, output_dir=args.output
    )

    system.run(duration_minutes=args.duration)


if __name__ == "__main__":
    main()
