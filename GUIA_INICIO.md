# 🚀 Guía Definitiva de Inicio - Vectores AI Suite (GestureCam)

Este documento contiene las instrucciones detalladas paso a paso para inicializar, configurar y ejecutar el proyecto **Vectores AI Suite (GestureCam)** en tu máquina macOS. Explicado desde cero hasta tener el sistema completamente funcional.

---

## 🛠️ Fase 1: Requisitos Previos

Antes de comenzar, asegúrate de tener en tu sistema:
- **Python 3.10 o superior** (El proyecto está diseñado para funcionar fluidamente en versiones recientes de Python).
- Controlador de paquetes `pip` (Incluido por defecto con Python).
- Conexión a internet para descargar las librerías necesarias y los modelos locales de Inteligencia Artificial (MediaPipe).
- *(Opcional)* Tener **OBS Studio** instalado si planeas usar la función de retransmisión por cámara virtual (`pyvirtualcam`).

---

## 💻 Fase 2: Configuración del Entorno de Desarrollo (Recomendado)

Para evitar conflictos de versiones con otras librerías de Python en tu Mac, es una **Mejor Práctica** utilizar un Entorno Virtual (Virtual Environment).

1. **Abrir la terminal** y navegar a la carpeta raíz del proyecto:
   ```bash
   cd /Users/martin/Dev/Vectores/gesture_cam
   ```

2. **Crear el Entorno Virtual** (esto creará una carpeta oculta a simple vista o explícita llamada `venv` donde residirán los binarios):
   ```bash
   python3 -m venv venv
   ```

3. **Activar el Entorno Virtual**:
   - Ejecuta el siguiente comando para activarlo (en macOS/Linux):
     ```bash
     source venv/bin/activate
     ```
   *(Nota de éxito: Notarás que el inicio del texto prompt de tu terminal cambia para decir, por ejemplo, `(venv) user@mac...`, indicando que el entorno está encendido y protegido).*

---

## 📦 Fase 3: Instalación de Dependencias

Una vez que el entorno virtual está encendido, debes instalar todas las bibliotecas requeridas para usar la Inteligencia Artificial y la cámara cruzando scripts de python.

1. **Asegúrate de tener pip actualizado**:
   ```bash
   pip install --upgrade pip
   ```

2. **Instalar las dependencias base incluidas en el archivo `requirements.txt`**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Esto instala utilidades gráficas, matemáticas y de visión computacional).*

3. **Instalar dependencias visuales de Interfaz Gráfica (UI)**:
   El proyecto usa DearPyGui y NiceGUI, herramientas de renderizado nativo muy rápidas. Es vital agregarlas:
   ```bash
   pip install dearpygui nicegui
   ```

---

## 🚦 Fase 4: Ejecutar la Aplicación Principal

El proyecto cuenta con un potente **Launcher Principal** o "Centro de Comando" (archivo `main.py`) que agrupa todas las herramientas de la suite de software en un menú interactivo.

1. Verifica que aún estás en la ruta raíz del proyecto y con tu entorno virtual activo:
   ```bash
   python3 main.py
   ```

2. En tu terminal se limpiará la pantalla y verás el siguiente selector modo CLI:
   ```text
   ============================================================
      V E C T O R E S   A I   C A M   S U I T E
   ============================================================
   v2.0 - Hybrid Architecture

   SELECCIONA UN MODO:
     [1] 🎥 AI Camera (Auto-Framing & Zoom)
     [2] 🎨 AirCanvas (Gestos y Arte)
     [3] 👤 Attendance System (Registro)
     [4] ⚡ Benchmark (Test de Rendimiento)
     [Q] Salir

   Opción > 
   ```

3. **Inicia el sistema deseado**:
   - Presiona **`1` y luego Enter** para arrancar el programa de **Cámara IA**, que tiene soporte nativo de Zoom por encuadre y gestos con las manos.
   - Presiona **`2` y luego Enter** para usar tu dedo como marcador virtual (AirCanvas).
   - Presiona **`3` y luego Enter** para operar el detector de rostros de asistencia.
   - Presiona **`4` y luego Enter** para simular estrés y probar qué tan rápida es la detección IA en los chips M de tu Mac.

---

## ⚠️ Resolución de Problemas Comunes (F.A.Q.)

- **Problema**: Aparece el error `"No module named cv2"` o `"No module named mediapipe"`.
  - **Solución**: El entorno virtual está apagado. Recuerda ejecutar el comando `source venv/bin/activate`. Si el error persiste, los paquetes no instalaron correctamente. Ejecuta `pip install opencv-python mediapipe pyvirtualcam` de nuevo.

- **Problema**: La cámara de Mac se enciende (led verde) pero la ventana emergente de Python se queda "congelada" o se cierra rápido.
  - **Solución**: Necesitas dar permisos de grabación. Ve en tu Mac a: *Ajustes del Sistema > Privacidad y seguridad > Cámara* y permite que la "Terminal" (o el editor de código que uses como VS Code) pueda usar tu cámara.

- **Problema**: La app tarda muchísimo la primera vez.
  - **Solución**: El sistema descarga en silencio los archivos de IA la primera vez (modelos MediaPipe a la carpeta `~/.gesturecam/`). Demorará menos de un minuto según tu conexión a internet para calibrar este AI model en memoria. Dale tiempo sin cerrarlo prematuramente.
