import math


class GestureRecognizer:
    def __init__(self, pinch_threshold_lower=30, pinch_threshold_upper=150):
        self.pinch_lower = pinch_threshold_lower
        self.pinch_upper = pinch_threshold_upper
        self.last_pinch_dist = None
        self.is_pinching = False
        self.last_index_y = None
        self.zoom_locked = False

    def _count_fingers_up(self, hand):
        """
        Cuenta cuántos dedos están levantados.
        Returns: int (0-5)
        """
        lm_list = hand.get("lmList", [])
        if len(lm_list) < 21:
            return 0

        fingers = []

        # Thumb: comparar x (horizontal) - indice 4 vs 3
        thumb_tip_x = lm_list[4][0]
        thumb_ip_x = lm_list[3][0]
        # Determinamos orientación por posición relativa del pulgar al meñique
        pinky_mcp_x = lm_list[17][0]
        if thumb_tip_x < pinky_mcp_x:  # Mano derecha (imagen espejo)
            fingers.append(thumb_tip_x < thumb_ip_x)
        else:  # Mano izquierda
            fingers.append(thumb_tip_x > thumb_ip_x)

        # Otros dedos: tip.y < pip.y significa que está arriba
        # Index finger (tip: 8, pip: 6)
        fingers.append(lm_list[8][1] < lm_list[6][1])
        # Middle finger (tip: 12, pip: 10)
        fingers.append(lm_list[12][1] < lm_list[10][1])
        # Ring finger (tip: 16, pip: 14)
        fingers.append(lm_list[16][1] < lm_list[14][1])
        # Pinky (tip: 20, pip: 18)
        fingers.append(lm_list[20][1] < lm_list[18][1])

        return sum(fingers)

    def check_thumbs_up(self, hand):
        """
        Detecta si la mano está haciendo thumbs up (👍).
        Returns: True si es thumbs up
        """
        lm_list = hand.get("lmList", [])
        if len(lm_list) < 21:
            return False

        # Pulgar debe estar arriba (tip.y < base.y significativamente)
        thumb_tip_y = lm_list[4][1]
        thumb_mcp_y = lm_list[2][1]

        # Otros dedos deben estar cerrados (tip.y > pip.y)
        index_closed = lm_list[8][1] > lm_list[6][1]
        middle_closed = lm_list[12][1] > lm_list[10][1]
        ring_closed = lm_list[16][1] > lm_list[14][1]
        pinky_closed = lm_list[20][1] > lm_list[18][1]

        thumb_up = thumb_tip_y < thumb_mcp_y - 30  # Pulgar significativamente arriba
        fingers_closed = index_closed and middle_closed and ring_closed and pinky_closed

        return thumb_up and fingers_closed

    def check_thumbs_down(self, hand):
        """
        Detecta si la mano está haciendo thumbs down (👎).
        Returns: True si es thumbs down
        """
        lm_list = hand.get("lmList", [])
        if len(lm_list) < 21:
            return False

        # Pulgar debe estar abajo (tip.y > base.y significativamente)
        thumb_tip_y = lm_list[4][1]
        thumb_mcp_y = lm_list[2][1]

        # Otros dedos deben estar cerrados
        index_closed = lm_list[8][1] > lm_list[6][1]
        middle_closed = lm_list[12][1] > lm_list[10][1]
        ring_closed = lm_list[16][1] > lm_list[14][1]
        pinky_closed = lm_list[20][1] > lm_list[18][1]

        thumb_down = thumb_tip_y > thumb_mcp_y + 30  # Pulgar significativamente abajo
        fingers_closed = index_closed and middle_closed and ring_closed and pinky_closed

        return thumb_down and fingers_closed

    def check_open_palm(self, hand):
        """
        Detecta palma abierta (5 dedos) - usado para "pausar" zoom.
        """
        return self._count_fingers_up(hand) == 5

    def check_fist(self, hand):
        """
        Detecta puño cerrado (0 dedos).
        """
        return self._count_fingers_up(hand) == 0

    def check_index_pointing(self, hand):
        """
        Detecta dedo índice apuntando (solo índice levantado).
        Returns: 'up', 'down', 'neutral', o None si no es el gesto
        """
        lm_list = hand.get("lmList", [])
        if len(lm_list) < 21:
            return None

        # Solo índice levantado
        index_up = lm_list[8][1] < lm_list[6][1]
        middle_closed = lm_list[12][1] > lm_list[10][1]
        ring_closed = lm_list[16][1] > lm_list[14][1]
        pinky_closed = lm_list[20][1] > lm_list[18][1]

        if not (index_up and middle_closed and ring_closed and pinky_closed):
            return None

        # Determinar dirección por posición vertical del índice
        index_tip_y = lm_list[8][1]
        index_mcp_y = lm_list[5][1]  # Base del índice

        diff = index_tip_y - index_mcp_y

        if diff < -50:  # Apuntando hacia arriba
            return "up"
        elif diff > 50:  # Apuntando hacia abajo
            return "down"
        else:
            return "neutral"

    def get_zoom_gesture(self, hands):
        """
        Detecta el gesto de zoom más apropiado.
        Returns: dict con 'action' y 'value'
            action: 'zoom_in', 'zoom_out', 'hold', 'none'
            value: intensidad del zoom (0.0-1.0)
        """
        if not hands:
            self.last_index_y = None
            return {"action": "none", "value": 0}

        hand = hands[0]

        # Prioridad 1: Palma abierta = HOLD/PAUSE
        if self.check_open_palm(hand):
            return {"action": "hold", "value": 0}

        # Prioridad 2: Thumbs up = Zoom IN gradual
        if self.check_thumbs_up(hand):
            return {"action": "zoom_in", "value": 0.02}  # Incremento suave

        # Prioridad 3: Thumbs down = Zoom OUT gradual
        if self.check_thumbs_down(hand):
            return {"action": "zoom_out", "value": 0.02}  # Decremento suave

        # Prioridad 4: Index pointing = control direccional
        pointing = self.check_index_pointing(hand)
        if pointing == "up":
            return {"action": "zoom_in", "value": 0.03}
        elif pointing == "down":
            return {"action": "zoom_out", "value": 0.03}

        return {"action": "none", "value": 0}

    def check_pinch_zoom(self, hands):
        """
        Checks for pinch gesture on the first hand (Right or Left).
        Returns:
            factor: float or None.
                    If tracking pinch, returns current normalized distance (0-1 approx).
                    If not pinching, returns None.
        """
        if not hands:
            self.is_pinching = False
            return None

        # Priority to right hand? Or just first hand.
        hand = hands[0]

        # Check fingers up: Index(1) and Thumb(0) should be active, others mostly down?
        # Actually, simpler is just distance check.
        # But we need a state "Pinching" to lock the zoom action.

        lm_list = hand["lmList"]  # List of [x, y, z]
        # Thumb tip: 4, Index tip: 8
        x1, y1 = lm_list[4][0], lm_list[4][1]
        x2, y2 = lm_list[8][0], lm_list[8][1]

        dist = math.hypot(x2 - x1, y2 - y1)

        # Continuous pinch distance mapping
        return dist

    def check_two_hand_zoom(self, hands):
        """
        Checks if two hands are present and "ready" (e.g., both palms open or specific sign).
        Returns distance between centers.
        """
        if len(hands) < 2:
            return None

        # Get centers
        c1 = hands[0]["center"]  # (x, y)
        c2 = hands[1]["center"]

        dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
        return dist

    def detect_swipe(self, hands):
        # Implementation for later (v0.3/0.4)
        pass
