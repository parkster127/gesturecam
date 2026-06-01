"""
AI Camera Application Module
This is the "Smart Camera" mode of the software.
"""

import cv2
import time
from gesturecam.core.pipeline import GestureCamPipeline
from gesturecam.camera.operator import CameraMode


class AICameraApp:
    def __init__(self, source=0, lite_mode=False):
        self.pipeline = GestureCamPipeline(source=source, lite_mode=lite_mode)
        self.window_name = "Vectores AI Camera"
        self.show_debug = True

    def run(self):
        print(f"🚀 Iniciando {self.window_name}...")
        print("Controles:")
        print("  [Q] Salir")
        print("  [D] Toggle Debug View")
        print("  [1] Modo Manual")
        print("  [2] Modo Follow")
        print("  [3] Modo Smart Zoom (Recomendado)")
        print("  [4] Modo Cinematic")

        try:
            while True:
                debug_frame, output_frame = self.pipeline.step()

                if debug_frame is None:
                    print("⚠️ No video input")
                    break

                # Mostrar salida principal (Clean Feed)
                cv2.imshow(self.window_name, output_frame)

                # Mostrar debug si está activo
                if self.show_debug:
                    cv2.imshow(
                        f"{self.window_name} - Debug",
                        cv2.resize(debug_frame, (640, 360)),
                    )
                elif (
                    cv2.getWindowProperty(
                        f"{self.window_name} - Debug", cv2.WND_PROP_VISIBLE
                    )
                    >= 1
                ):
                    cv2.destroyWindow(f"{self.window_name} - Debug")

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                elif key == ord("d"):
                    self.show_debug = not self.show_debug
                elif key == ord("1"):
                    self.pipeline.cameraman.set_mode(CameraMode.MANUAL)
                elif key == ord("2"):
                    self.pipeline.cameraman.set_mode(CameraMode.FOLLOW)
                elif key == ord("3"):
                    self.pipeline.cameraman.set_mode(CameraMode.SMART_ZOOM)
                elif key == ord("4"):
                    self.pipeline.cameraman.set_mode(CameraMode.CINEMATIC)

        except KeyboardInterrupt:
            pass
        finally:
            self.pipeline.stop()
            cv2.destroyAllWindows()
            print("✅ Aplicación finalizada.")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--lite", action="store_true", help="Modo bajo rendimiento (i3)"
    )
    parser.add_argument("--src", type=int, default=0, help="Índice de cámara")
    args = parser.parse_args()

    app = AICameraApp(source=args.src, lite_mode=args.lite)
    app.run()


if __name__ == "__main__":
    main()
