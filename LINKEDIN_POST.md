## POST LINKEDIN - GestureCam Open Source

---

Acabo de liberar GestureCam como proyecto open source.

GestureCam es una plataforma de vision por computadora que transforma tu webcam en una camara virtual inteligente controlada por gestos de mano y expresiones faciales. Construido con MediaPipe y OpenCV, se integra directamente con OBS Studio, Zoom, Microsoft Teams y cualquier plataforma de videoconferencia.

Que hace:

- Reconocimiento de gestos en tiempo real: thumbs up/down para zoom, peace sign para pausar, pinch de dos manos para zoom suave
- Face mesh con 468 puntos de referencia para auto-framing inteligente
- Deteccion de parpadeo para acciones rapidas
- Salida de camara virtual compatible con OBS
- Modo AirCanvas para dibujar en el aire con las manos
- Sistema de asistencia con reconocimiento facial
- Dos interfaces: desktop nativo y web

Stack: Python, MediaPipe, OpenCV, NumPy, Dear PyGui, NiceGUI

~8,600 lineas de codigo, arquitectura modular con separacion clara entre capas: camara, vision, core, UI.

Licencia MIT. Disponible en github.com/parkster127/gesturecam

Estamos aplicando al programa Codex for Open Source de OpenAI para llevar GestureCam al siguiente nivel: optimizacion de gestos con ML, entrenamiento de gestos personalizados, control inteligente de camara y comprension de escenas.

Si te interesa la vision por computadora, los gestos o simplemente quieres contribuir a un proyecto open source, te invito a explorar el repo.

#OpenSource #ComputerVision #MediaPipe #Python #MachineLearning #GestureRecognition #VirtualCamera #OBS

---

NOTA: Antes de publicar, asegurate de:
1. Haber creado el repo en github.com/parkster127/gesturecam
2. Haber hecho push del codigo
3. Verificar que el README se ve bien en GitHub
4. Agregar topics/tags al repo: computer-vision, gesture-recognition, mediapipe, opencv