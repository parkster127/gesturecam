#!/usr/bin/env python3
"""
VECTORES AI SUITE - Launcher Principal
Centro de comando para todas las aplicaciones de visión artificial.
"""

import sys
import os
import time


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_banner():
    print("=" * 60)
    print("   V E C T O R E S   A I   C A M   S U I T E")
    print("=" * 60)
    print("v2.0 - Hybrid Architecture")
    print("")


def run_ai_camera():
    print("\n🎥 Iniciando AI Camera Mode (Native UI)...")
    # Importar dentro de la función para no cargar dependencias innecesarias
    from gesturecam.ui.native_ui import run_demo

    run_demo()


def run_air_canvas():
    print("\n🎨 Iniciando AirCanvas Mode...")
    # Hack temporal para que AirCanvas encuentre sus rutas relativas si las usa
    # Idealmente AirCanvas debería ser refactorizado como clase App también
    from gesturecam.apps.air_canvas import main as run_canvas

    run_canvas()


def run_attendance():
    print("\n👤 Iniciando Sistema de Asistencia...")
    attendance_script = os.path.join(
        os.path.dirname(__file__), "attendance_system", "attendance_system.py"
    )
    if os.path.exists(attendance_script):
        os.system(f"{sys.executable} {attendance_script} --session demo")
    else:
        print(f"❌ No se encuentra el script: {attendance_script}")
        time.sleep(2)


def main():
    while True:
        clear_screen()
        show_banner()
        print("SELECCIONA UN MODO:")
        print("  [1] 🎥 AI Camera (Auto-Framing & Zoom)")
        print("  [2] 🎨 AirCanvas (Gestos y Arte)")
        print("  [3] 👤 Attendance System (Registro)")
        print("  [4] ⚡ Benchmark (Test de Rendimiento)")
        print("  [Q] Salir")
        print("")

        choice = input("Opción > ").upper()

        if choice == "1":
            run_ai_camera()
        elif choice == "2":
            run_air_canvas()
        elif choice == "3":
            run_attendance()
        elif choice == "4":
            os.system(f"{sys.executable} tests/benchmark_performance.py")
            input("\nPresiona Enter para volver...")
        elif choice == "Q":
            print("\n¡Hasta luego! 👋")
            break
        else:
            print("Opción no válida.")
            time.sleep(1)


if __name__ == "__main__":
    # Asegurar que el directorio actual está en path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main()
