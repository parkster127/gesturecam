# Sistema de Asistencia con Detección Facial

## 🎯 Aplicaciones Principales

### 1. **Asistencia Escolar/Laboral**
```bash
# Clase de 2 horas
python tests/attendance_system.py --session clase_matematicas --duration 120

# Turno de trabajo de 8 horas
python tests/attendance_system.py --session turno_noche --duration 480
```

**Características:**
- ✅ Verifica presencia continua
- ✅ Detecta ausencias temporales
- ✅ Monitorea atención
- ✅ Cuenta parpadeos (indicador de cansancio)
- ✅ Genera logs con timestamps

**Casos de uso:**
- Clases online
- Trabajo remoto
- Capacitaciones virtuales
- Exámenes supervisados

---

### 2. **Detección de Fatiga en Conductores**
```bash
# Monitoreo de conductor
python tests/attendance_system.py --session conductor_001 --duration 240
```

**Alertas automáticas:**
- 🚨 **SOMNOLENCIA**: EAR < 0.18 por varios frames
- ⚠️ **BAJA ATENCIÓN**: Score < 50%
- 👁️ **Parpadeos frecuentes**: > 30 por minuto

**Métricas monitoreadas:**
- EAR promedio (Eye Aspect Ratio)
- Frecuencia de parpadeo
- Duración de ojos cerrados
- Score de atención en tiempo real

**Integración posible:**
```python
# En tu sistema de alertas
if system.is_drowsy:
    # Activar alarma sonora
    trigger_alarm()
    
    # Vibrar asiento
    activate_seat_vibration()
    
    # Registrar evento
    log_safety_event("DROWSINESS_DETECTED")
```

---

### 3. **Control de Acceso sin Contacto**
```bash
# Monitoreo de entrada
python tests/attendance_system.py --session entrada_principal
```

**Funcionalidades:**
- ✅ Detección automática de entrada/salida
- ✅ Registro con timestamp
- ✅ Verificación de "vida" (liveness detection via parpadeo)
- ✅ Logs de acceso

**Flujo:**
1. Usuario se acerca a cámara
2. Sistema detecta cara → Evento "entry"
3. Verifica que es persona real (parpadeo)
4. Registra acceso
5. Usuario se aleja → Evento "exit"

---

### 4. **Supervisión de Exámenes (Proctoring)**
```bash
# Examen de 1 hora
python tests/attendance_system.py --session examen_final --duration 60
```

**Detecta:**
- ❌ Ausencias de la cámara
- ❌ Múltiples personas (future feature)
- ❌ Mirar fuera de pantalla (gaze tracking)
- ⚠️ Movimientos sospechosos

**Reporte automático:**
- Tasa de presencia
- Alertas de ausencia
- Eventos sospechosos
- Timeline completo

---

## 📊 Estructura de Datos

### Sesión de Asistencia
```json
{
  "session_id": "clase_matematicas_20260125_150000",
  "start_time": "2026-01-25T15:00:00",
  "end_time": "2026-01-25T17:00:00",
  "total_duration": 7200.0,
  
  "total_frames": 216000,
  "frames_detected": 212000,
  "blink_count": 145,
  "drowsy_count": 2,
  "attention_alerts": 5,
  
  "avg_ear": 0.269,
  "avg_attention_score": 78.5,
  
  "events": [
    {
      "timestamp": "2026-01-25T15:00:01",
      "event_type": "entry",
      "confidence": 1.0,
      "ear_avg": 0.270,
      "attention_score": 100.0,
      "notes": "Usuario detectado"
    },
    {
      "timestamp": "2026-01-25T15:23:15",
      "event_type": "drowsy",
      "confidence": 1.0,
      "ear_avg": 0.165,
      "attention_score": 45.0,
      "notes": "Somnolencia detectada"
    }
  ]
}
```

---

## 🚀 Guía de Uso Rápida

### 1. Ejecutar Sistema

```bash
# Sesión de 5 minutos para prueba
cd tests
python3 attendance_system.py --session demo --duration 5
```

**Controles en vivo:**
- `q` - Finalizar sesión
- `s` - Guardar screenshot
- `r` - Resetear estadísticas

### 2. Analizar Resultados

```bash
# Ver todas las sesiones
python3 analyze_attendance.py

# Ver sesión específica
python3 analyze_attendance.py --session demo_20260125_150000
```

### 3. Interpretar Resultados

**Score de Atención (0-100):**
- **80-100**: Excelente - totalmente atento
- **60-79**: Buena - atención normal
- **40-59**: Regular - atención intermitente
- **0-39**: Deficiente - muy distraído/dormido

**EAR (Eye Aspect Ratio):**
- **> 0.25**: Ojos bien abiertos, alerta
- **0.21-0.25**: Normal
- **0.18-0.21**: Cansancio leve
- **< 0.18**: Somnolencia

---

## 💡 Ejemplos de Integración

### Integración con Base de Datos

```python
from attendance_system import AttendanceSystem
import sqlite3

system = AttendanceSystem(session_name="clase_001")
system.start_session()

# Conectar a DB
conn = sqlite3.connect('attendance.db')
cursor = conn.cursor()

# Cuando detectas entrada
cursor.execute("""
    INSERT INTO attendance 
    (session_id, user_id, entry_time, attention_score)
    VALUES (?, ?, ?, ?)
""", (system.session.session_id, "user_123", 
      datetime.now(), system.current_attention_score))

conn.commit()
```

### API REST

```python
from flask import Flask, jsonify
from attendance_system import AttendanceSystem

app = Flask(__name__)
system = AttendanceSystem()

@app.route('/api/start_session', methods=['POST'])
def start():
    session_id = system.start_session()
    return jsonify({"session_id": session_id})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "is_present": system.is_present,
        "attention_score": system.current_attention_score,
        "is_drowsy": system.is_drowsy,
        "blink_count": system.session.blink_count
    })

@app.route('/api/end_session', methods=['POST'])
def end():
    system.end_session()
    return jsonify({"status": "session_ended"})
```

### Alertas en Tiempo Real

```python
import requests

def on_drowsiness_detected(metrics):
    """Callback cuando se detecta somnolencia"""
    
    # Enviar notificación push
    requests.post('https://api.pushover.net/1/messages.json', data={
        'token': 'YOUR_TOKEN',
        'user': 'USER_KEY',
        'message': f'Alerta: Somnolencia detectada. EAR: {metrics.avg_ear:.3f}'
    })
    
    # Enviar email
    send_email(
        to='supervisor@empresa.com',
        subject='Alerta de Somnolencia',
        body=f'Conductor muestra signos de fatiga a las {datetime.now()}'
    )
    
    # Activar señal física
    activate_buzzer()
```

---

## 🔬 Casos de Uso Avanzados

### 1. Análisis de Productividad

```python
# Correlacionar atención con hora del día
sessions = load_all_sessions()
morning = [s for s in sessions if is_morning(s['start_time'])]
afternoon = [s for s in sessions if is_afternoon(s['start_time'])]

morning_attention = np.mean([s['avg_attention_score'] for s in morning])
afternoon_attention = np.mean([s['avg_attention_score'] for s in afternoon])

print(f"Atención mañana: {morning_attention:.1f}%")
print(f"Atención tarde: {afternoon_attention:.1f}%")
```

### 2. Detección de Patrones

```python
# Identificar horas de mayor fatiga
events = []
for session in sessions:
    for event in session['events']:
        if event['event_type'] == 'drowsy':
            hour = datetime.fromisoformat(event['timestamp']).hour
            events.append(hour)

# Visualizar
plt.hist(events, bins=24)
plt.xlabel('Hora del día')
plt.ylabel('Eventos de somnolencia')
plt.title('Patrón de Fatiga por Hora')
plt.show()
```

### 3. Sistema Multi-Cámara

```python
# Múltiples cámaras en aula
systems = [
    AttendanceSystem(camera_index=0, session_name="estudiante_1"),
    AttendanceSystem(camera_index=1, session_name="estudiante_2"),
    AttendanceSystem(camera_index=2, session_name="estudiante_3"),
]

# Procesar en paralelo
import threading

for system in systems:
    thread = threading.Thread(target=system.run, args=(60,))
    thread.start()
```

---

## 📈 Métricas y KPIs

### KPIs Principales

1. **Tasa de Presencia**: % de tiempo detectado
2. **Score de Atención Promedio**: Indicador de concentración
3. **Frecuencia de Parpadeo**: Normal ~15-20/min
4. **Eventos de Somnolencia**: Alertas críticas
5. **EAR Promedio**: Nivel de apertura ocular

### Benchmarks

| Escenario | Atención Objetivo | EAR Mínimo | Alertas Max |
|-----------|------------------|------------|-------------|
| Clase/Conferencia | > 70% | > 0.21 | < 3/hora |
| Examen | > 85% | > 0.23 | 0 |
| Conducción | > 90% | > 0.22 | 0 |
| Trabajo Oficina | > 65% | > 0.20 | < 5/hora |

---

## 🛡️ Consideraciones de Privacidad

### Buenas Prácticas

✅ **Notificar a usuarios** que serán monitoreados  
✅ **Almacenar solo métricas**, no video  
✅ **Encriptar logs** de asistencia  
✅ **Política de retención** (ej: 30 días)  
✅ **Acceso limitado** a datos sensibles  

### Configuración de Privacidad

```python
# No guardar frames
SAVE_FRAMES = False

# Anonimizar datos
ANONYMIZE_SESSIONS = True

# Encriptar logs
ENCRYPT_LOGS = True

# Auto-eliminar después de N días
LOG_RETENTION_DAYS = 30
```

---

## 🎓 Conclusión

Este sistema aprovecha tus **vectores faciales** para crear un **sistema de asistencia completo y robusto** que puede:

1. ✅ Verificar presencia física
2. ✅ Medir nivel de atención
3. ✅ Detectar fatiga/somnolencia
4. ✅ Generar reportes automáticos
5. ✅ Alertar en tiempo real
6. ✅ Integrarse con otros sistemas

**Tus vectores faciales (EAR, landmarks, gaze) son la base** que permite todas estas funcionalidades avanzadas.
