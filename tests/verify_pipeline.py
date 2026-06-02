#!/usr/bin/env python3
"""
Verificación de Pipeline Desacoplado - Vectores AI Cam
Prueba la arquitectura "Hybrid Engine" (Video Thread + AI Worker).
"""

import argparse
import os
import sys

import cv2

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # gesture_cam root
sys.path.insert(0, parent_dir)

try:
    from gesturecam.core.pipeline import GestureCamPipeline
except ImportError as e:
    print(f"Error importando gesturecam: {e}")
    print(f"Buscando en: {sys.path[0]}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Test GestureCam Performance Pipeline")
    parser.add_argument(
        "--lite", action="store_true", help="Activar modo Lite (simulación i3)"
    )
    args = parser.parse_args()

    print(f"🚀 Iniciando Pipeline (Lite Mode: {args.lite})...")
    print("Presiona 'Q' para salir.")

    # Inicializar Pipeline
    pipeline = GestureCamPipeline(lite_mode=args.lite)

    try:
        while True:
            debug_frame, output_frame = pipeline.step()

            if debug_frame is None:
                break

            # Mostrar ventanas
            cv2.imshow(
                "Vectores Cam - INPUT (Debug)", cv2.resize(debug_frame, (640, 360))
            )
            cv2.imshow("Vectores Cam - SALIDA VIRTUAL", output_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    except KeyboardInterrupt:
        pass
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        print("\n✅ Pipeline finalizado correctamente.")


if __name__ == "__main__":
    main()
