"""
Drawing Module - Handle drawing interactions with hand gestures
"""

from typing import Optional, Tuple, List
import numpy as np


class DrawingState:
    """Estado del sistema de dibujo"""

    def __init__(self):
        self.is_drawing = False
        self.last_point: Optional[Tuple[int, int]] = None
        self.current_color = (255, 100, 255)  # Magenta por defecto
        self.current_radius = 20
        self.mode = "circle"  # circle, mandala, sphere
        self.mandala_symmetry = 8

    def reset(self):
        """Resetear estado"""
        self.is_drawing = False
        self.last_point = None


class GestureDrawingController:
    """
    Controlador de dibujo basado en gestos de manos

    Interpreta gestos y los convierte en acciones de dibujo.
    """

    def __init__(self):
        self.state = DrawingState()
        self.colors_palette = [
            (255, 100, 255),  # Magenta
            (100, 255, 255),  # Cyan
            (255, 255, 100),  # Amarillo
            (100, 255, 100),  # Verde
            (255, 100, 100),  # Rojo
            (100, 100, 255),  # Azul
        ]
        self.color_index = 0
        self.stroke_width = 2  # Grosor de línea para modo paz

    def next_color(self):
        """Cambiar al siguiente color"""
        self.color_index = (self.color_index + 1) % len(self.colors_palette)
        self.state.current_color = self.colors_palette[self.color_index]

    def random_color(self):
        """Generar color aleatorio para auto-cambio"""
        import random

        self.color_index = random.randint(0, len(self.colors_palette) - 1)
        self.state.current_color = self.colors_palette[self.color_index]

    def set_mode(self, mode: str):
        """Cambiar modo de dibujo"""
        if mode in ["circle", "mandala", "sphere"]:
            self.state.mode = mode
            self.state.reset()

    def process_hand(self, hand_data: dict) -> dict:
        """
        Procesar datos de mano y generar comando de dibujo

        Args:
            hand_data: Dict con 'lmList', 'center', 'bbox'

        Returns:
            Dict con comando de dibujo
        """
        lm_list = hand_data.get("lmList", [])
        if len(lm_list) < 21:
            return {"action": "none"}

        # Detectar si el índice está levantado (modo dibujo)
        index_tip = lm_list[8]  # Punta del índice
        index_pip = lm_list[6]  # Segunda articulación del índice
        thumb_tip = lm_list[4]

        # Otros dedos
        middle_tip = lm_list[12]
        middle_pip = lm_list[10]
        ring_tip = lm_list[16]
        ring_pip = lm_list[14]
        pinky_tip = lm_list[20]
        pinky_pip = lm_list[18]

        # Detectar dedos levantados
        index_up = index_tip[1] < index_pip[1] - 20
        middle_up = middle_tip[1] < middle_pip[1] - 20
        ring_up = ring_tip[1] < ring_pip[1]
        pinky_up = pinky_tip[1] < pinky_pip[1]

        fingers_up_count = sum([index_up, middle_up, ring_up, pinky_up])

        # GESTO 1: Solo índice levantado = dibujar
        if index_up and not middle_up and not ring_up and not pinky_up:
            # Modo dibujo
            point = (index_tip[0], index_tip[1])

            if not self.state.is_drawing:
                # Iniciar trazo
                self.state.is_drawing = True
                self.state.last_point = point
                return {
                    "action": "start_drawing",
                    "point": point,
                    "mode": self.state.mode,
                    "color": self.state.current_color,
                    "radius": self.state.current_radius,
                    "symmetry": self.state.mandala_symmetry,
                }
            else:
                # Continuar trazo
                result = {
                    "action": "continue_drawing",
                    "point": point,
                    "last_point": self.state.last_point,
                    "mode": self.state.mode,
                    "color": self.state.current_color,
                    "radius": self.state.current_radius,
                }
                self.state.last_point = point
                return result
        else:
            # No está dibujando
            if self.state.is_drawing:
                # Finalizar trazo
                self.state.is_drawing = False
                self.state.last_point = None
                return {"action": "end_drawing"}

            # Detectar otros gestos

            # GESTO 2: Signo de la paz (2 dedos: índice + medio) = cambiar modo/stroke
            if index_up and middle_up and not ring_up and not pinky_up:
                return {"action": "peace_sign"}

            # GESTO 3: Palma abierta (4 dedos arriba) = limpiar canvas
            if fingers_up_count >= 3:  # Al menos 3 dedos arriba
                return {"action": "clear"}

        return {"action": "none"}
