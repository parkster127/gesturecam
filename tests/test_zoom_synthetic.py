#!/usr/bin/env python3
"""
Script de prueba del zoom SIN cámara.
Usa un video sintético para verificar la lógica de zoom.
"""

import os
import sys

import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gesturecam.core.zoom import ZoomController


def create_test_pattern(width=640, height=480):
    """Crea un patrón visual para probar zoom."""
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Grid
    for x in range(0, width, 50):
        cv2.line(frame, (x, 0), (x, height), (50, 50, 50), 1)
    for y in range(0, height, 50):
        cv2.line(frame, (0, y), (width, y), (50, 50, 50), 1)

    # Center crosshair
    cv2.line(frame, (width//2, 0), (width//2, height), (0, 255, 0), 2)
    cv2.line(frame, (0, height//2), (width, height//2), (0, 255, 0), 2)

    # Corner markers
    corner_size = 30
    corners = [(0, 0), (width, 0), (0, height), (width, height)]
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    for (x, y), color in zip(corners, colors, strict=False):
        cv2.rectangle(frame, (max(0, x-corner_size), max(0, y-corner_size)),
                      (min(width, x+corner_size), min(height, y+corner_size)), color, -1)

    # Center circle
    cv2.circle(frame, (width//2, height//2), 50, (255, 255, 255), 2)
    cv2.circle(frame, (width//2, height//2), 5, (255, 255, 255), -1)

    # Quarter markers
    cv2.circle(frame, (width//4, height//4), 20, (100, 100, 255), 2)
    cv2.circle(frame, (3*width//4, height//4), 20, (255, 100, 100), 2)
    cv2.circle(frame, (width//4, 3*height//4), 20, (100, 255, 100), 2)
    cv2.circle(frame, (3*width//4, 3*height//4), 20, (255, 100, 255), 2)

    return frame


def run_zoom_test():
    """Prueba interactiva de zoom sin cámara."""
    print("\n" + "="*60)
    print("🔍 GestureCam - Test de Zoom (Sin Cámara)")
    print("="*60)
    print("\nControles:")
    print("  '+' / '=': Aumentar zoom")
    print("  '-' / '_': Disminuir zoom")
    print("  'w/a/s/d': Mover centro de zoom")
    print("  'r': Reset zoom y centro")
    print("  'q': Salir")
    print("\n")

    width, height = 640, 480
    base_frame = create_test_pattern(width, height)

    zoom_ctrl = ZoomController(min_zoom=1.0, max_zoom=4.0, smoothing_factor=0.2)

    cv2.namedWindow("Zoom Test", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Zoom Test", 1000, 500)

    while True:
        # Step zoom
        current_zoom = zoom_ctrl.step()

        # Apply zoom
        zoomed = zoom_ctrl.apply_zoom(base_frame)

        # Create side-by-side view
        original_labeled = base_frame.copy()
        zoomed_labeled = zoomed.copy()

        # Labels
        cv2.putText(original_labeled, "Original", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(zoomed_labeled, f"Zoom: {current_zoom:.2f}x", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(zoomed_labeled, f"Center: ({zoom_ctrl.center_x:.2f}, {zoom_ctrl.center_y:.2f})", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        # Draw zoom center indicator on original
        cx_px = int(zoom_ctrl.center_x * width)
        cy_px = int(zoom_ctrl.center_y * height)
        cv2.circle(original_labeled, (cx_px, cy_px), 15, (0, 165, 255), 3)
        cv2.line(original_labeled, (cx_px - 20, cy_px), (cx_px + 20, cy_px), (0, 165, 255), 2)
        cv2.line(original_labeled, (cx_px, cy_px - 20), (cx_px, cy_px + 20), (0, 165, 255), 2)

        # Draw zoom box indicator
        if current_zoom > 1.0:
            box_w = width / current_zoom
            box_h = height / current_zoom
            box_x = (zoom_ctrl.center_x * width) - (box_w / 2)
            box_y = (zoom_ctrl.center_y * height) - (box_h / 2)
            box_x = max(0, min(box_x, width - box_w))
            box_y = max(0, min(box_y, height - box_h))
            cv2.rectangle(original_labeled,
                         (int(box_x), int(box_y)),
                         (int(box_x + box_w), int(box_y + box_h)),
                         (0, 165, 255), 2)

        combined = np.hstack([original_labeled, zoomed_labeled])
        cv2.imshow("Zoom Test", combined)

        key = cv2.waitKey(30) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            zoom_ctrl.set_target_zoom(1.0)
            zoom_ctrl.set_zoom_center(0.5, 0.5)
            print("🔄 Reset!")
        elif key == ord('+') or key == ord('='):
            new_zoom = min(zoom_ctrl.target_zoom + 0.3, zoom_ctrl.max_zoom)
            zoom_ctrl.set_target_zoom(new_zoom)
            print(f"➕ Zoom: {new_zoom:.2f}x")
        elif key == ord('-') or key == ord('_'):
            new_zoom = max(zoom_ctrl.target_zoom - 0.3, zoom_ctrl.min_zoom)
            zoom_ctrl.set_target_zoom(new_zoom)
            print(f"➖ Zoom: {new_zoom:.2f}x")
        elif key == ord('w'):
            zoom_ctrl.set_zoom_center(zoom_ctrl.center_x, max(0.1, zoom_ctrl.center_y - 0.05))
            print(f"⬆️ Center: ({zoom_ctrl.center_x:.2f}, {zoom_ctrl.center_y:.2f})")
        elif key == ord('s'):
            zoom_ctrl.set_zoom_center(zoom_ctrl.center_x, min(0.9, zoom_ctrl.center_y + 0.05))
            print(f"⬇️ Center: ({zoom_ctrl.center_x:.2f}, {zoom_ctrl.center_y:.2f})")
        elif key == ord('a'):
            zoom_ctrl.set_zoom_center(max(0.1, zoom_ctrl.center_x - 0.05), zoom_ctrl.center_y)
            print(f"⬅️ Center: ({zoom_ctrl.center_x:.2f}, {zoom_ctrl.center_y:.2f})")
        elif key == ord('d'):
            zoom_ctrl.set_zoom_center(min(0.9, zoom_ctrl.center_x + 0.05), zoom_ctrl.center_y)
            print(f"➡️ Center: ({zoom_ctrl.center_x:.2f}, {zoom_ctrl.center_y:.2f})")

    cv2.destroyAllWindows()
    print("✅ Test completado!")


if __name__ == "__main__":
    run_zoom_test()
