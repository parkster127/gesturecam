#!/usr/bin/env python3
"""
Analizador de Logs de Asistencia

Genera reportes y visualizaciones de las sesiones de asistencia.
"""

import glob
import json
import os
from datetime import datetime, timedelta


def load_session(filepath: str) -> dict:
    """Cargar sesión desde JSON"""
    with open(filepath) as f:
        return json.load(f)


def analyze_session(session: dict) -> dict:
    """Analizar sesión y generar métricas"""

    start = datetime.fromisoformat(session["start_time"])
    end = (
        datetime.fromisoformat(session["end_time"])
        if session["end_time"]
        else datetime.now()
    )
    duration = (end - start).total_seconds()

    # Contar eventos por tipo
    event_counts = {}
    for event in session["events"]:
        etype = event["event_type"]
        event_counts[etype] = event_counts.get(etype, 0) + 1

    # Calcular tiempo presente
    time_present = 0
    last_entry = None
    for event in session["events"]:
        if event["event_type"] == "entry":
            last_entry = datetime.fromisoformat(event["timestamp"])
        elif event["event_type"] == "exit" and last_entry:
            exit_time = datetime.fromisoformat(event["timestamp"])
            time_present += (exit_time - last_entry).total_seconds()
            last_entry = None

    # Si todavía está presente al final
    if last_entry:
        time_present += (end - last_entry).total_seconds()

    presence_rate = (time_present / duration * 100) if duration > 0 else 0

    # Evaluación de atención
    attention_grade = (
        "Excelente"
        if session["avg_attention_score"] >= 80
        else "Buena"
        if session["avg_attention_score"] >= 60
        else "Regular"
        if session["avg_attention_score"] >= 40
        else "Deficiente"
    )

    return {
        "session_id": session["session_id"],
        "start_time": session["start_time"],
        "end_time": session["end_time"],
        "duration_seconds": duration,
        "duration_formatted": str(timedelta(seconds=int(duration))),
        "frames_total": session["total_frames"],
        "frames_detected": session["frames_detected"],
        "detection_rate": session["frames_detected"] / session["total_frames"] * 100
        if session["total_frames"] > 0
        else 0,
        "time_present_seconds": time_present,
        "presence_rate": presence_rate,
        "blink_count": session["blink_count"],
        "drowsy_count": session["drowsy_count"],
        "attention_alerts": session["attention_alerts"],
        "avg_ear": session["avg_ear"],
        "avg_attention_score": session["avg_attention_score"],
        "attention_grade": attention_grade,
        "event_counts": event_counts,
        "total_events": len(session["events"]),
    }


def generate_report(sessions: list[dict]):
    """Generar reporte de múltiples sesiones"""

    print("\n" + "=" * 80)
    print("REPORTE DE ASISTENCIA")
    print("=" * 80)
    print(f"\nTotal de sesiones: {len(sessions)}")

    for i, session in enumerate(sessions, 1):
        analysis = analyze_session(session)

        print(f"\n{'-' * 80}")
        print(f"SESIÓN {i}: {analysis['session_id']}")
        print(f"{'-' * 80}")

        print("\n📅 Información General:")
        print(f"   Inicio:         {analysis['start_time']}")
        print(f"   Fin:            {analysis['end_time']}")
        print(f"   Duración:       {analysis['duration_formatted']}")

        print("\n👤 Presencia:")
        print(f"   Tasa de detección:  {analysis['detection_rate']:.1f}%")
        print(f"   Tasa de presencia:  {analysis['presence_rate']:.1f}%")
        print(
            f"   Tiempo presente:    {timedelta(seconds=int(analysis['time_present_seconds']))}"
        )

        print("\n👁️  Métricas de Atención:")
        print(f"   EAR promedio:       {analysis['avg_ear']:.3f}")
        print(f"   Atención promedio:  {analysis['avg_attention_score']:.1f}%")
        print(f"   Evaluación:         {analysis['attention_grade']}")

        print("\n⚠️  Alertas:")
        print(f"   Parpadeos:          {analysis['blink_count']}")
        print(f"   Somnolencia:        {analysis['drowsy_count']}")
        print(f"   Baja atención:      {analysis['attention_alerts']}")

        print("\n📊 Eventos registrados:")
        for event_type, count in analysis["event_counts"].items():
            print(f"   {event_type:15s}  {count}")

        # Recomendaciones
        print("\n💡 Recomendaciones:")
        if analysis["avg_attention_score"] < 60:
            print("   ⚠️  Atención baja - considerar pausas más frecuentes")
        if analysis["drowsy_count"] > 5:
            print("   ⚠️  Múltiples alertas de somnolencia - verificar condiciones")
        if analysis["presence_rate"] < 80:
            print("   ⚠️  Presencia intermitente - verificar setup de cámara")
        if analysis["avg_attention_score"] >= 80 and analysis["drowsy_count"] == 0:
            print("   ✅ Sesión excelente - buena atención sostenida")

    # Resumen general
    if len(sessions) > 1:
        total_duration = sum(analyze_session(s)["duration_seconds"] for s in sessions)
        avg_attention = sum(
            analyze_session(s)["avg_attention_score"] for s in sessions
        ) / len(sessions)
        total_drowsy = sum(s["drowsy_count"] for s in sessions)

        print(f"\n{'=' * 80}")
        print("RESUMEN GENERAL")
        print(f"{'=' * 80}")
        print(f"Tiempo total:           {timedelta(seconds=int(total_duration))}")
        print(f"Atención promedio:      {avg_attention:.1f}%")
        print(f"Total alertas somnolencia: {total_drowsy}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analizar logs de asistencia")
    parser.add_argument(
        "--dir", "-d", type=str, default="attendance_logs", help="Directorio de logs"
    )
    parser.add_argument("--session", "-s", type=str, help="Analizar sesión específica")

    args = parser.parse_args()

    # Cargar sesiones
    if args.session:
        # Sesión específica
        filepath = os.path.join(args.dir, args.session)
        if not filepath.endswith(".json"):
            filepath += ".json"

        if not os.path.exists(filepath):
            print(f"ERROR: No se encontró {filepath}")
            return

        sessions = [load_session(filepath)]
    else:
        # Todas las sesiones
        pattern = os.path.join(args.dir, "*.json")
        files = glob.glob(pattern)

        if not files:
            print(f"No se encontraron sesiones en {args.dir}")
            print("\nPara crear una sesión, ejecuta:")
            print("  python tests/attendance_system.py --duration 1")
            return

        sessions = [load_session(f) for f in sorted(files)]

    # Generar reporte
    generate_report(sessions)

    print(f"\n{'=' * 80}\n")


if __name__ == "__main__":
    main()
