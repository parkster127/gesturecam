#!/usr/bin/env python3
"""
Benchmark de Rendimiento - Vectores AI Cam
Mide el rendimiento del pipeline de visión actual.
"""

import cv2
import time
import numpy as np
import sys
import os
import psutil  # Para medir CPU/RAM

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Debug path
print(f"Python path: {sys.path[0]}")

try:
    from gesturecam.vision.face_mesh import FaceMeshTracker
except ImportError as e:
    print(f"Error importando gesturecam: {e}")
    print(
        "Verifica que estás ejecutando el script desde la raíz del proyecto o que la estructura de carpetas es correcta."
    )
    sys.exit(1)


def run_benchmark(duration_sec=10, resolution=(1280, 720), model_complexity=1):
    print(
        f"\n🚀 Iniciando Benchmark ({duration_sec}s) @ {resolution[0]}x{resolution[1]}"
    )
    print(f"⚙️  Model Complexity: {model_complexity}")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Error: No se detecta cámara.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    # Inicializar Tracker
    tracker = FaceMeshTracker(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        refine_landmarks=True,  # Iris tracking (pesado)
    )

    # Variables de medición
    frame_times = []
    inference_times = []
    start_time = time.time()
    frames = 0

    process = psutil.Process(os.getpid())
    cpu_usage = []

    print("Capturando datos... (Muévete frente a la cámara)")

    while True:
        loop_start = time.time()

        # 1. Capture
        ret, frame = cap.read()
        if not ret:
            break

        # 2. Inference
        inf_start = time.time()
        tracker.detect(frame)
        inf_end = time.time()

        # 3. CPU Measure
        if frames % 5 == 0:
            cpu_usage.append(process.cpu_percent())

        loop_end = time.time()

        inference_times.append((inf_end - inf_start) * 1000)  # ms
        frame_times.append((loop_end - loop_start) * 1000)  # ms

        frames += 1
        if (time.time() - start_time) > duration_sec:
            break

    cap.release()

    # Análisis de resultados
    avg_fps = frames / (time.time() - start_time)
    avg_inf = np.mean(inference_times)
    p95_inf = np.percentile(inference_times, 95)
    avg_cpu = np.mean(cpu_usage)

    print("\n📊 RESULTADOS DEL BENCHMARK")
    print("============================")
    print(f"FPS Promedio:       {avg_fps:.2f}")
    print(f"Tiempo Inferencia:  {avg_inf:.2f} ms (Promedio)")
    print(f"Tiempo Inferencia:  {p95_inf:.2f} ms (95% peor caso)")
    print(f"Uso CPU (Python):   {avg_cpu:.1f}%")
    print(f"Total Frames:       {frames}")

    # Estimación i3 (Factor conservador: M4 es ~5x más rápido que un i3 viejo en ML)
    print("\n🔮 ESTIMACIÓN PARA INTEL i3 (Doble Núcleo / 4 Hilos)")
    print(f"FPS Estimados:      {avg_fps / 4:.2f} - {avg_fps / 3:.2f}")
    print(f"Latencia Estimada:  {avg_inf * 3.5:.2f} ms")

    if (avg_fps / 3.5) < 15:
        print("\n⚠️  ADVERTENCIA: Rendimiento crítico en i3. Se requiere optimización.")
    else:
        print("\n✅  ESTADO: Viable, pero la optimización mejorará la suavidad.")


if __name__ == "__main__":
    # Instalar psutil si falta
    try:
        import psutil
    except ImportError:
        print("Instalando dependencia para benchmark...")
        os.system(f"{sys.executable} -m pip install psutil")
        import psutil

    run_benchmark()
