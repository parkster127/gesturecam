"""
Geometry Generator - Create circles, mandalas, and geometric patterns
"""

import numpy as np
import cv2
from typing import List, Tuple, Optional
import math


class Circle:
    """Representa un círculo en el canvas"""

    def __init__(
        self,
        x: int,
        y: int,
        radius: int,
        color: Tuple[int, int, int],
        thickness: int = 2,
        z: float = 0.0,
    ):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.thickness = thickness
        self.z = z  # Profundidad para efecto 3D
        self.age = 0  # Frames desde creación
        self.alpha = 1.0  # Transparencia

    def update(self, fade_rate: float = 0.01):
        """Actualizar círculo (para efectos de fade)"""
        self.age += 1
        self.alpha = max(0, self.alpha - fade_rate)

    def draw(self, canvas: np.ndarray, scale: float = 1.0):
        """Dibujar círculo en canvas"""
        if self.alpha <= 0:
            return

        # Aplicar escala por profundidad (efecto 3D)
        apparent_radius = int(self.radius * scale * (1.0 + self.z * 0.5))

        # Color con alpha
        color = tuple(int(c * self.alpha) for c in self.color)

        if self.thickness < 0:
            # Círculo relleno
            cv2.circle(canvas, (self.x, self.y), apparent_radius, color, -1)
        else:
            cv2.circle(canvas, (self.x, self.y), apparent_radius, color, self.thickness)


class Mandala:
    """Generador de mandalas con simetria radial."""

    def __init__(
        self,
        center_x: int,
        center_y: int,
        symmetry: int = 8,
        color: Tuple[int, int, int] = (255, 100, 255),
    ):
        self.center_x = center_x
        self.center_y = center_y
        self.symmetry = symmetry  # Número de repeticiones radiales
        self.color = color
        self.points: List[Tuple[int, int]] = []  # Puntos del patrón original
        self.age = 0
        self.alpha = 1.0

    def add_point(self, x: int, y: int):
        """Agregar un punto al patrón"""
        self.points.append((x, y))

    def clear(self):
        """Limpiar todos los puntos"""
        self.points.clear()

    def _rotate_point(self, x: int, y: int, angle_rad: float) -> Tuple[int, int]:
        """Rotar un punto alrededor del centro"""
        # Trasladar al origen
        tx = x - self.center_x
        ty = y - self.center_y

        # Rotar
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        rx = tx * cos_a - ty * sin_a
        ry = tx * sin_a + ty * cos_a

        # Trasladar de vuelta
        return (int(rx + self.center_x), int(ry + self.center_y))

    def update(self, fade_rate: float = 0.005):
        """Actualizar mandala"""
        self.age += 1
        self.alpha = max(0, self.alpha - fade_rate)

    def draw(self, canvas: np.ndarray, thickness: int = 2, glow: bool = True):
        """Dibujar mandala con simetría radial y efecto neón"""
        if len(self.points) < 2 or self.alpha <= 0:
            return

        # Calcular ángulo entre cada repetición
        angle_step = 2 * math.pi / self.symmetry

        # Color con alpha
        color = tuple(int(c * self.alpha) for c in self.color)

        # Dibujar cada repetición radial
        for i in range(self.symmetry):
            angle = i * angle_step

            # Rotar todos los puntos
            rotated_points = [self._rotate_point(x, y, angle) for x, y in self.points]

            # Dibujar líneas conectando los puntos
            for j in range(len(rotated_points) - 1):
                pt1 = rotated_points[j]
                pt2 = rotated_points[j + 1]

                # Efecto neón: dibujar múltiples capas con diferente grosor
                if glow:
                    # Glow exterior (más grueso, más transparente)
                    glow_color = tuple(int(c * self.alpha * 0.3) for c in self.color)
                    cv2.line(canvas, pt1, pt2, glow_color, thickness + 8)

                    # Glow medio
                    glow_color = tuple(int(c * self.alpha * 0.5) for c in self.color)
                    cv2.line(canvas, pt1, pt2, glow_color, thickness + 4)

                # Línea principal (brillante)
                cv2.line(canvas, pt1, pt2, color, thickness)


class Sphere3D:
    """Esfera 3D que genera mandalas proyectados en 2D."""

    def __init__(
        self,
        center_x: int,
        center_y: int,
        radius: int = 100,
        color: Tuple[int, int, int] = (100, 255, 255),
    ):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.rotation_x = 0.0  # Rotación en eje X
        self.rotation_y = 0.0  # Rotación en eje Y
        self.rotation_z = 0.0  # Rotación en eje Z
        self.points_3d: List[Tuple[float, float, float]] = []  # Puntos en 3D
        self.age = 0
        self.alpha = 1.0
        self.auto_rotate = True

        # Generar puntos de la esfera (fibonacci sphere)
        self._generate_sphere_points(num_points=500)

    def _generate_sphere_points(self, num_points: int = 500):
        """Generar puntos distribuidos uniformemente en la esfera"""
        self.points_3d.clear()

        phi = math.pi * (3.0 - math.sqrt(5.0))  # Golden angle

        for i in range(num_points):
            y = 1 - (i / float(num_points - 1)) * 2  # y from 1 to -1
            radius_at_y = math.sqrt(1 - y * y)

            theta = phi * i

            x = math.cos(theta) * radius_at_y
            z = math.sin(theta) * radius_at_y

            self.points_3d.append((x, y, z))

    def _rotate_3d_point(
        self, x: float, y: float, z: float
    ) -> Tuple[float, float, float]:
        """Aplicar rotaciones 3D a un punto"""
        # Rotación en X
        cos_x, sin_x = math.cos(self.rotation_x), math.sin(self.rotation_x)
        y1 = y * cos_x - z * sin_x
        z1 = y * sin_x + z * cos_x
        y, z = y1, z1

        # Rotación en Y
        cos_y, sin_y = math.cos(self.rotation_y), math.sin(self.rotation_y)
        x1 = x * cos_y + z * sin_y
        z1 = -x * sin_y + z * cos_y
        x, z = x1, z1

        # Rotación en Z
        cos_z, sin_z = math.cos(self.rotation_z), math.sin(self.rotation_z)
        x1 = x * cos_z - y * sin_z
        y1 = x * sin_z + y * cos_z
        x, y = x1, y1

        return (x, y, z)

    def _project_to_2d(self, x: float, y: float, z: float) -> Tuple[int, int, float]:
        """
        Proyección perspectiva 3D -> 2D

        Returns: (screen_x, screen_y, depth)
        """
        # Distancia de la cámara
        camera_distance = 3.0

        # Proyección perspectiva
        if z + camera_distance != 0:
            scale = camera_distance / (z + camera_distance)
        else:
            scale = 1.0

        screen_x = int(x * self.radius * scale + self.center_x)
        screen_y = int(y * self.radius * scale + self.center_y)

        return (screen_x, screen_y, z)

    def update(self, rotation_speed: float = 0.02):
        """Actualizar esfera (auto-rotación)"""
        self.age += 1

        if self.auto_rotate:
            self.rotation_x += rotation_speed * 0.7
            self.rotation_y += rotation_speed * 1.0
            self.rotation_z += rotation_speed * 0.5

    def draw(self, canvas: np.ndarray, draw_lines: bool = True):
        """Dibujar esfera 3D proyectada en 2D"""
        if self.alpha <= 0:
            return

        # Proyectar todos los puntos
        projected_points = []
        for x, y, z in self.points_3d:
            # Rotar punto
            rx, ry, rz = self._rotate_3d_point(x, y, z)

            # Proyectar a 2D
            sx, sy, depth = self._project_to_2d(rx, ry, rz)

            projected_points.append((sx, sy, depth))

        # Ordenar por profundidad (pintar lejanos primero)
        projected_points.sort(key=lambda p: p[2])

        # Dibujar puntos
        for sx, sy, depth in projected_points:
            # Color basado en profundidad (más brillante = más cerca)
            brightness = (depth + 1.0) / 2.0  # Normalizar de [-1,1] a [0,1]
            color = tuple(int(c * brightness * self.alpha) for c in self.color)

            # Tamaño basado en profundidad
            size = int(2 + brightness * 3)

            cv2.circle(canvas, (sx, sy), size, color, -1)

        # Conectar puntos cercanos para efecto de malla (opcional)
        if draw_lines and len(projected_points) > 1:
            threshold = 50  # Distancia máxima para conectar puntos
            for i in range(
                0, len(projected_points), 5
            ):  # Solo cada 5 puntos para no saturar
                px, py, pz = projected_points[i]
                for j in range(i + 1, min(i + 10, len(projected_points))):
                    qx, qy, qz = projected_points[j]
                    dist = math.sqrt((px - qx) ** 2 + (py - qy) ** 2)
                    if dist < threshold:
                        brightness = ((pz + qz) / 2.0 + 1.0) / 2.0
                        color = tuple(
                            int(c * brightness * self.alpha * 0.3) for c in self.color
                        )
                        cv2.line(canvas, (px, py), (qx, qy), color, 1)


class GeometryRenderer:
    """
    Renderer para todas las geometrías

    Mantiene una lista de objetos geométricos y los renderiza en orden.
    """

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.circles: List[Circle] = []
        self.mandalas: List[Mandala] = []
        self.spheres: List[Sphere3D] = []
        self.current_mandala: Optional[Mandala] = None

    def add_circle(
        self,
        x: int,
        y: int,
        radius: int,
        color: Tuple[int, int, int],
        thickness: int = 2,
        z: float = 0.0,
    ):
        """Agregar un círculo"""
        circle = Circle(x, y, radius, color, thickness, z)
        self.circles.append(circle)

    def start_mandala(
        self,
        center_x: int,
        center_y: int,
        symmetry: int = 8,
        color: Tuple[int, int, int] = (255, 100, 255),
    ):
        """Iniciar un nuevo mandala"""
        self.current_mandala = Mandala(center_x, center_y, symmetry, color)

    def add_mandala_point(self, x: int, y: int):
        """Agregar punto al mandala actual"""
        if self.current_mandala:
            self.current_mandala.add_point(x, y)

    def finish_mandala(self):
        """Finalizar mandala actual"""
        if self.current_mandala and len(self.current_mandala.points) > 0:
            self.mandalas.append(self.current_mandala)
            self.current_mandala = None

    def add_sphere(
        self,
        center_x: int,
        center_y: int,
        radius: int = 100,
        color: Tuple[int, int, int] = (100, 255, 255),
    ):
        """Agregar una esfera 3D"""
        sphere = Sphere3D(center_x, center_y, radius, color)
        self.spheres.append(sphere)

    def update(self):
        """Actualizar todos los objetos"""
        # Actualizar círculos
        self.circles = [c for c in self.circles if c.alpha > 0]
        for circle in self.circles:
            circle.update()

        # Actualizar mandalas
        self.mandalas = [m for m in self.mandalas if m.alpha > 0]
        for mandala in self.mandalas:
            mandala.update()

        # Actualizar esferas
        for sphere in self.spheres:
            sphere.update()

    def clear_all(self):
        """Limpiar todos los objetos"""
        self.circles.clear()
        self.mandalas.clear()
        self.spheres.clear()
        self.current_mandala = None

    def render(self, background: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Renderizar todos los objetos

        Returns: Canvas con todos los objetos dibujados
        """
        # Crear canvas
        if background is not None:
            canvas = background.copy()
        else:
            canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Dibujar en orden: esferas -> mandalas -> círculos -> mandala actual

        # Esferas (fondo)
        for sphere in self.spheres:
            sphere.draw(canvas, draw_lines=True)

        # Mandalas finalizados (con efecto neón)
        for mandala in self.mandalas:
            mandala.draw(canvas, thickness=2, glow=True)

        # Círculos
        for circle in self.circles:
            circle.draw(canvas)

        # Mandala actual (en proceso, con más brillo)
        if self.current_mandala:
            self.current_mandala.draw(canvas, thickness=3, glow=True)

        return canvas
