"""
Camera Operator Module - The "Cameraman Agent"

Responsabilidad:
Recibir métricas de detección (dónde está la cara) y calcular el encuadre óptimo (viewport).
Implementa suavizado (smoothing) para simular un operador de cámara humano.
"""

import numpy as np
import cv2
import time
from typing import Tuple, Optional, Dict
from dataclasses import dataclass


class CameraMode:
    MANUAL = "manual"  # Zoom manual fijo
    FOLLOW = "follow"  # Auto-Framing X/Y, Zoom fijo
    SMART_ZOOM = "smart"  # Auto-Framing + Auto-Zoom (Distancia constante)
    CINEMATIC = "cinema"  # Movimientos ultra lentos y suaves


@dataclass
class ViewportState:
    """Estado actual del encuadre (Viewport)"""

    x: float
    y: float
    width: float
    height: float
    zoom_level: float = 1.0


class CameraOperator:
    """
    Agente Camarógrafo Inteligente.
    Calcula el recorte (crop) de la imagen para mantener al sujeto encuadrado.
    """

    def __init__(self, source_width: int, source_height: int):
        self.source_width = source_width
        self.source_height = source_height
        self.aspect_ratio = source_width / source_height

        # Modo actual
        self.mode = CameraMode.FOLLOW

        # Estado actual y objetivo (para suavizado)
        self.current_viewport = ViewportState(0, 0, source_width, source_height)
        self.target_viewport = ViewportState(0, 0, source_width, source_height)

        # Configuración de comportamiento (Personalidad del camarógrafo)
        self.smoothing_factor = 0.10  # Por defecto
        self.dead_zone = 0.05  # Por defecto

        self.headroom = 0.3  # Espacio arriba de la cabeza
        self.min_zoom = 1.0  # Zoom mínimo
        self.max_zoom = 3.0  # Zoom máximo permitido

        # Zoom manual objetivo
        self.manual_zoom = 1.0

        # Smart Zoom Target
        # Porcentaje ideal de altura que debe ocupar la cara (0.4 = 40%)
        self.target_face_ratio = 0.45

        self.is_tracking = True
        self.last_face_center = None
        self.last_face_size = None

        # Hysteresis state for Smart Zoom
        self.last_valid_zoom = 1.0
        self.zoom_stable_counter = 0

    def set_mode(self, mode: str):
        """Cambiar modo de operación"""
        self.mode = mode

        # Ajustar personalidad según el modo
        if mode == CameraMode.CINEMATIC:
            self.smoothing_factor = 0.03  # Extremadamente lento
            self.dead_zone = 0.10  # Ignorar mucho movimiento
        elif mode == CameraMode.SMART_ZOOM:
            self.smoothing_factor = 0.05  # Más suave para evitar mareos con zoom
            self.dead_zone = 0.05
        else:
            self.smoothing_factor = 0.15  # Normal (rápido)
            self.dead_zone = 0.03

        print(f"🎥 CAMERA MODE: {mode.upper()} (Smooth: {self.smoothing_factor})")

    def update_target(
        self, face_bbox: Tuple[int, int, int, int], face_center: Tuple[float, float]
    ):
        """
        Actualizar el objetivo basado en la nueva posición de la cara.
        """
        if not self.is_tracking or face_bbox is None:
            return

        fx, fy, fw, fh = face_bbox
        cx, cy = face_center

        # --- 1. CALCULAR ZOOM OBJETIVO ---
        target_zoom = self.target_viewport.zoom_level  # Default to current

        if self.mode == CameraMode.SMART_ZOOM:
            # Calcular zoom ideal crudo
            if fh > 10:
                ideal_zoom = (self.source_height * self.target_face_ratio) / fh
                ideal_zoom = max(self.min_zoom, min(ideal_zoom, self.max_zoom))

                # APLICAR HYSTERESIS (Anti-Jitter de Zoom)
                # Solo cambiar el zoom si la diferencia es significativa (> 8%)
                zoom_diff = (
                    abs(ideal_zoom - self.last_valid_zoom) / self.last_valid_zoom
                )

                if zoom_diff > 0.08:
                    self.last_valid_zoom = ideal_zoom
                    target_zoom = ideal_zoom
                else:
                    # Mantener el zoom anterior para evitar "respiración"
                    target_zoom = self.last_valid_zoom

        elif self.mode == CameraMode.MANUAL or self.mode == CameraMode.FOLLOW:
            # En manual/follow usamos el valor manual establecido
            target_zoom = self.manual_zoom

        # Calcular dimensiones del viewport basado en el zoom objetivo
        current_h = self.source_height / target_zoom
        current_w = self.source_width / target_zoom

        # --- 2. CALCULAR POSICIÓN (Centrado) ---
        target_center_x = cx
        target_center_y = cy - (current_h * 0.10)  # 10% arriba para headroom

        # --- 3. APLICAR DEAD ZONE (Posición) ---
        if self.last_face_center:
            # Distancia euclidiana
            dist = np.sqrt(
                (cx - self.last_face_center[0]) ** 2
                + (cy - self.last_face_center[1]) ** 2
            )
            relative_dist = dist / self.source_width

            # Si el movimiento es menor a la zona muerta, NO actualizamos el CENTRO
            # PERO si el zoom cambió drásticamente, sí debemos actualizar el centro para re-encuadrar
            zoom_changed = abs(target_zoom - self.target_viewport.zoom_level) > 0.01

            if relative_dist < self.dead_zone and not zoom_changed:
                return

        self.last_face_center = (cx, cy)
        self.last_face_size = fh

        # --- 4. CALCULAR VIEWPORT ---
        new_x = target_center_x - (current_w / 2)
        new_y = target_center_y - (current_h / 2)

        # Clamping
        new_x = max(0, min(new_x, self.source_width - current_w))
        new_y = max(0, min(new_y, self.source_height - current_h))

        self.target_viewport.x = new_x
        self.target_viewport.y = new_y
        self.target_viewport.width = current_w
        self.target_viewport.height = current_h
        self.target_viewport.zoom_level = target_zoom

    def set_manual_zoom(self, zoom_level: float):
        """Ajustar nivel de zoom manual"""
        self.manual_zoom = max(self.min_zoom, min(zoom_level, self.max_zoom))

    def process(self) -> Tuple[int, int, int, int]:
        """Calcula el frame suavizado"""
        # Interpolación Lineal (LERP)
        factor = self.smoothing_factor

        self.current_viewport.x += (
            self.target_viewport.x - self.current_viewport.x
        ) * factor
        self.current_viewport.y += (
            self.target_viewport.y - self.current_viewport.y
        ) * factor
        self.current_viewport.width += (
            self.target_viewport.width - self.current_viewport.width
        ) * factor
        self.current_viewport.height += (
            self.target_viewport.height - self.current_viewport.height
        ) * factor

        return (
            int(self.current_viewport.x),
            int(self.current_viewport.y),
            int(self.current_viewport.width),
            int(self.current_viewport.height),
        )

    def crop_frame(self, frame: np.ndarray) -> np.ndarray:
        """Generar salida final"""
        x, y, w, h = self.process()

        w = max(1, w)
        h = max(1, h)

        crop = frame[y : y + h, x : x + w]

        if crop.size == 0:
            return frame

        return cv2.resize(
            crop,
            (self.source_width, self.source_height),
            interpolation=cv2.INTER_LINEAR,
        )
