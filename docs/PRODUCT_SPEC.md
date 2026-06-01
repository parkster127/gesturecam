# GestureCam - Product Specification Document

> **Cámara virtual inteligente con control por gestos**  
> Software gratuito para democratizar el zoom y framing profesional

---

## 🎯 Resumen Ejecutivo

**GestureCam** es una aplicación de escritorio gratuita que transforma cualquier webcam básica en una cámara profesional con capacidades de zoom y seguimiento automático, controlada completamente mediante gestos de la mano.

### Problema que Resuelve

- Las webcams de laptops no tienen zoom óptico
- Las cámaras profesionales con tracking cuestan $200-500+ USD
- Los streamers y trabajadores remotos necesitan encuadres profesionales
- No existe una solución gratuita y accesible para este problema

### Solución

Una aplicación de software que usa IA (MediaPipe) para detectar gestos de la mano y aplicar zoom digital + seguimiento facial en tiempo real, emitiendo el resultado como una cámara virtual compatible con cualquier aplicación (Zoom, Meet, Teams, OBS, etc).

---

## 👥 Target Audience

| Segmento             | Descripción                              | Pain Point                                      |
| -------------------- | ---------------------------------------- | ----------------------------------------------- |
| **Streamers**        | Creadores de contenido en Twitch/YouTube | Necesitan encuadres dinámicos sin hardware caro |
| **Remote Workers**   | Profesionales en home office             | Mejorar presencia en videollamadas              |
| **Educators**        | Profesores y tutores online              | Acercarse a la cámara para demos sin moverse    |
| **Content Creators** | TikTokers, podcasters, YouTubers         | Efectos de cámara profesionales gratis          |
| **Developers**       | Grabando screencasts y tutoriales        | Zoom dinámico para explicar código              |

---

## ✨ Core Features

### 1. 🎥 Virtual Camera Output

- Crea una cámara virtual que aparece en todas las apps
- Compatible con: Zoom, Google Meet, Microsoft Teams, OBS, Discord, etc.
- Resolución configurable: 720p, 1080p

### 2. 🖐️ Gesture Control

| Gesto               | Acción                  | Icono         |
| ------------------- | ----------------------- | ------------- |
| 👍 Thumbs Up        | Zoom In (acercar)       | ![thumb_up]   |
| 👎 Thumbs Down      | Zoom Out (alejar)       | ![thumb_down] |
| ☝️ Index Point Up   | Zoom In rápido          | ![point_up]   |
| 👇 Index Point Down | Zoom Out rápido         | ![point_down] |
| 🖐️ Open Palm        | Hold/Pausar zoom        | ![palm]       |
| ✊ Fist             | Modo neutro (no afecta) | ![fist]       |

### 3. 👤 Auto-Framing Modes

| Modo            | Descripción                    | Uso Ideal                     |
| --------------- | ------------------------------ | ----------------------------- |
| **Manual**      | Sin seguimiento automático     | Control total del usuario     |
| **Face Follow** | La cámara sigue tu cara        | Videollamadas, presentaciones |
| **Headshot**    | Encuadre profesional de cabeza | Podcasts, entrevistas         |
| **Shirt-Up**    | De camisa hacia arriba         | Tutoriales, demos             |

### 4. ⚡ Real-time Processing

- Procesamiento local (sin envío de datos a la nube)
- Latencia < 50ms
- Optimizado para CPU (no requiere GPU dedicada)

---

## 🖥️ Application Screens

### Screen 1: Main Dashboard (Pantalla Principal)

```
┌─────────────────────────────────────────────────────────────────┐
│  [GestureCam Logo]                              [─] [□] [✕]    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │                    CAMERA PREVIEW                       │   │
│  │                                                         │   │
│  │              [Tu imagen de webcam aquí]                 │   │
│  │                                                         │   │
│  │        ┌──────────────────────────────────┐            │   │
│  │        │  Gesture: ZOOM IN 👍             │            │   │
│  │        │  Zoom: 1.8x                      │            │   │
│  │        │  Mode: FACE_FOLLOW               │            │   │
│  │        └──────────────────────────────────┘            │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Manual  │  │  Face    │  │ Headshot │  │ Shirt-Up │       │
│  │    ○     │  │  Follow  │  │    ○     │  │    ○     │       │
│  │          │  │    ●     │  │          │  │          │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Status: ● Active    Virtual Camera: GestureCam        │   │
│  │  [▶ Start Virtual Camera]              [⚙ Settings]    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Elementos:**

- **Camera Preview**: Vista en vivo de la cámara con overlay de información
- **Mode Selector**: 4 botones para cambiar modo de encuadre
- **Status Bar**: Estado de la cámara virtual y botones de acción
- **Gesture Indicator**: Muestra el gesto detectado en tiempo real
- **Zoom Level**: Barra o número indicando nivel de zoom actual

---

### Screen 2: Settings / Configuración

```
┌─────────────────────────────────────────────────────────────────┐
│  [←] Configuración                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ─── CÁMARA ───────────────────────────────────────────────    │
│                                                                 │
│  Seleccionar Cámara:  [MacBook Pro Camera        ▼]           │
│  Resolución:          [1080p (1920x1080)         ▼]           │
│  FPS:                 [30                        ▼]           │
│                                                                 │
│  ─── ZOOM ─────────────────────────────────────────────────    │
│                                                                 │
│  Zoom Máximo:         [──────●──────] 3.0x                     │
│  Suavizado:           [────●────────] 0.15                     │
│  Sensibilidad Gestos: [──────●──────] Media                    │
│                                                                 │
│  ─── ENCUADRE ─────────────────────────────────────────────    │
│                                                                 │
│  Suavizado Seguimiento: [────●────────] 0.08                   │
│  Modo por defecto:      [Face Follow           ▼]              │
│                                                                 │
│  ─── GESTOS ───────────────────────────────────────────────    │
│                                                                 │
│  ☑ Habilitar gestos de zoom                                    │
│  ☑ Habilitar control por 2 manos                               │
│  ☐ Invertir dirección de zoom                                  │
│  ☐ Mostrar overlay de detección                                │
│                                                                 │
│  ─── SALIDA ───────────────────────────────────────────────    │
│                                                                 │
│  Backend Virtual:     [OBS Virtual Camera      ▼]              │
│  ☑ Iniciar con el sistema                                      │
│  ☑ Minimizar a bandeja del sistema                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [Restaurar Valores]                    [Guardar]       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Secciones:**

1. **Cámara**: Selección de dispositivo y resolución
2. **Zoom**: Límites y sensibilidad
3. **Encuadre**: Configuración del auto-framing
4. **Gestos**: Habilitar/deshabilitar funciones
5. **Salida**: Configuración de cámara virtual

---

### Screen 3: Gesture Guide / Guía de Gestos

```
┌─────────────────────────────────────────────────────────────────┐
│  [←] Guía de Gestos                                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Aprende a controlar GestureCam con tus manos                  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │   👍          👎          ☝️          👇          🖐️    │   │
│  │  Zoom In   Zoom Out   Zoom In+  Zoom Out+   HOLD      │   │
│  │                                                         │   │
│  │  [Animación mostrando cada gesto en acción]            │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ─── INSTRUCCIONES ────────────────────────────────────────    │
│                                                                 │
│  1. Asegúrate de tener buena iluminación                       │
│  2. Mantén tu mano visible dentro del cuadro                   │
│  3. Los gestos se detectan con una sola mano                   │
│  4. Usa la palma abierta para "congelar" el zoom               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  [Practicar Gestos]                    [Entendido ✓]    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Screen 4: Onboarding / Primera Vez

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                       [GestureCam Logo]                         │
│                                                                 │
│        "Tu webcam, ahora con superpoderes" ✨                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │     Step 1 of 3: Permisos de Cámara                     │   │
│  │                                                         │   │
│  │     [Ilustración de cámara con check]                   │   │
│  │                                                         │   │
│  │     GestureCam necesita acceso a tu cámara              │   │
│  │     para aplicar el zoom y tracking.                    │   │
│  │                                                         │   │
│  │     🔒 Todo se procesa localmente.                      │   │
│  │        Nunca enviamos video a internet.                 │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                    ○ ● ○                                        │
│                                                                 │
│           [Permitir Acceso a Cámara →]                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Pasos del Onboarding:**

1. Permisos de cámara
2. Selección de cámara por defecto
3. Tutorial rápido de gestos (con preview en vivo)

---

## 🌐 Landing Page Structure

### Hero Section

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  [Logo] GestureCam                        [Download] [GitHub]   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│          control your camera                                    │
│          with a simple 👍                                       │
│                                                                 │
│  Zoom, pan, and auto-frame your webcam using hand gestures.    │
│  No expensive hardware needed. 100% free and open source.      │
│                                                                 │
│  [Download for Mac ↓]   [Download for Windows ↓]               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │          [Hero Video/GIF showing app in action]         │   │
│  │          Persona haciendo thumbs up → zoom in           │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Features Section

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                      Why GestureCam?                            │
│                                                                 │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │  🖐️ Gesture   │ │  👤 Auto      │ │  🔒 Privacy   │         │
│  │    Control    │ │    Framing    │ │    First     │         │
│  │               │ │               │ │               │         │
│  │ Control zoom  │ │ Your camera   │ │ 100% local    │         │
│  │ with natural  │ │ follows your  │ │ processing.   │         │
│  │ hand gestures │ │ face smoothly │ │ Zero cloud.   │         │
│  └───────────────┘ └───────────────┘ └───────────────┘         │
│                                                                 │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐         │
│  │  🎥 Virtual   │ │  ⚡ Real-time │ │  💸 100%      │         │
│  │    Camera     │ │    Fast       │ │    Free      │         │
│  │               │ │               │ │               │         │
│  │ Works with    │ │ <50ms latency │ │ No premium,  │         │
│  │ Zoom, Meet,   │ │ No GPU needed │ │ no ads, no   │         │
│  │ OBS, Discord  │ │ CPU optimized │ │ catch. Ever. │         │
│  └───────────────┘ └───────────────┘ └───────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Demo Section

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                    See it in action                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                         │   │
│  │   [Video demo: Split screen]                            │   │
│  │   Left: Person doing gestures                           │   │
│  │   Right: Resulting zoomed/framed output                 │   │
│  │                                                         │   │
│  │   Interactive: Hover over gesture icons to see          │   │
│  │   what they do in the video preview                     │   │
│  │                                                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│       👍         👎         🖐️         ☝️         👇            │
│     Zoom In   Zoom Out    Hold    Point Up  Point Down        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Use Cases Section

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                 Perfect for everyone                            │
│                                                                 │
│  [Carousel or grid of use cases with images]                   │
│                                                                 │
│  🎮 Streamers        📹 Content Creators                        │
│  💼 Remote Workers   🎓 Educators                               │
│  🎙️ Podcasters       👨‍💻 Developers                              │
│                                                                 │
│  Each with a quote and mini screenshot                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Download Section

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                   Get GestureCam Now                            │
│                        It's free!                               │
│                                                                 │
│  ┌─────────────────┐           ┌─────────────────┐             │
│  │                 │           │                 │             │
│  │  [Apple Logo]   │           │ [Windows Logo]  │             │
│  │                 │           │                 │             │
│  │  Download for   │           │  Download for   │             │
│  │  macOS          │           │  Windows        │             │
│  │                 │           │                 │             │
│  │  Requires 10.15+│           │  Requires Win10+│             │
│  │                 │           │                 │             │
│  └─────────────────┘           └─────────────────┘             │
│                                                                 │
│            Also available on [GitHub] (open source)             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Footer

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  GestureCam                                                     │
│                                                                 │
│  Made with ❤️ by Vectores                                       │
│                                                                 │
│  [GitHub]  [Twitter]  [Discord]                                 │
│                                                                 │
│  © 2026 GestureCam. Open Source under MIT License.             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📱 Mobile App Considerations

### iOS/Android Version

Para la versión móvil, el enfoque cambia ligeramente:

**Funcionalidad Principal:**

- Usar el teléfono como webcam HD mejorada para la computadora
- Control de zoom/pan desde la app del teléfono
- Transmitir video procesado vía WiFi o USB

**Pantallas Mobile:**

1. **Home**: Preview de cámara con controles on-screen
2. **Connect**: QR code para conectar con desktop companion
3. **Settings**: Configuración simplificada
4. **Gestures**: Los mismos gestos pero detectados frontalmente

```
┌─────────────────────┐
│ ▓▓▓▓▓▓▓▓▓▓▓  12:00 │
├─────────────────────┤
│                     │
│  ┌───────────────┐  │
│  │               │  │
│  │   CAMERA      │  │
│  │   PREVIEW     │  │
│  │               │  │
│  │  Zoom: 1.5x   │  │
│  │  Mode: Face   │  │
│  │               │  │
│  └───────────────┘  │
│                     │
│  [−]  [● REC]  [+]  │
│                     │
│  ┌────┐ ┌────┐     │
│  │Face│ │Head│     │
│  │ ●  │ │ ○  │     │
│  └────┘ └────┘     │
│                     │
│  [📶 Connected to   │
│   MacBook Pro]      │
│                     │
├─────────────────────┤
│  🏠    📷    ⚙️    │
└─────────────────────┘
```

---

## 🎨 Design Guidelines

### Color Palette

| Color      | Hex       | Uso                           |
| ---------- | --------- | ----------------------------- |
| Primary    | `#6366F1` | Botones activos, accents      |
| Secondary  | `#22D3EE` | Highlights, gestos detectados |
| Success    | `#10B981` | Zoom in, estados activos      |
| Warning    | `#F59E0B` | Hold, pausas                  |
| Error      | `#EF4444` | Zoom out (opcional), errores  |
| Background | `#0F172A` | Fondo principal (dark mode)   |
| Surface    | `#1E293B` | Cards, paneles                |
| Text       | `#F8FAFC` | Texto principal               |
| Muted      | `#64748B` | Texto secundario              |

### Typography

- **Headlines**: Inter Bold / SF Pro Display Bold
- **Body**: Inter Regular / SF Pro Text Regular
- **Monospace**: JetBrains Mono (para stats/debug)

### Iconography

- Style: Outlined / Duo-tone
- Gesture icons: Custom illustrations showing hands
- UI icons: Lucide Icons or Phosphor Icons

### Motion

- Smooth transitions (200-300ms)
- Zoom indicator: spring animation
- Gesture detection: pulse effect when recognized

---

## 🔧 Technical Requirements

### Desktop App Stack

- **Framework**: Electron + React (or Tauri + React for lighter build)
- **Backend**: Python con MediaPipe
- **Virtual Camera**: pyvirtualcam / OBS Virtual Camera
- **Build**: electron-builder para distribución

### Performance Targets

- CPU Usage: < 15% en idle, < 30% activo
- Memory: < 200MB
- Latency: < 50ms end-to-end
- Startup: < 3 segundos

### Platforms

| Platform              | Priority | Status        |
| --------------------- | -------- | ------------- |
| macOS (Apple Silicon) | P0       | ✅ Funcional  |
| macOS (Intel)         | P0       | 🔜 Por probar |
| Windows 10/11         | P1       | 🔜 Pendiente  |
| Linux                 | P2       | 🔜 Pendiente  |
| iOS                   | P3       | 📋 Planeado   |
| Android               | P3       | 📋 Planeado   |

---

## 📋 Deliverables for Designer

### Lo que necesitamos de Stitch:

1. **Landing Page Design**
   - Hero section con video/animación
   - Features grid
   - Demo section interactiva
   - Download CTAs
   - Responsive (desktop, tablet, mobile)

2. **Desktop App UI**
   - Main dashboard
   - Settings panel
   - Gesture guide modal
   - Onboarding flow (3 steps)
   - System tray menu

3. **Mobile App UI** (opcional/P2)
   - Home screen
   - Connection screen
   - Settings
   - Gesture tutorial

4. **Assets**
   - Logo (light/dark)
   - Gesture icons set
   - App icons (macOS, Windows, iOS, Android)
   - Social preview images

5. **Motion/Interaction**
   - Gesture detection animation
   - Zoom level indicator animation
   - Mode switch transitions

---

## 📝 Inspiration References

### Apps with similar UX goals:

- **Loom** - Simple recording interface
- **mmhmm** - Virtual camera effects
- **Camo** - iPhone as webcam
- **Reincubate Camo** - Premium webcam software
- **Snap Camera** - Lens filters (discontinued)

### Landing pages we like:

- Linear.app - Clean, dark mode, animated
- Raycast.com - Developer-focused simplicity
- Arc.net - Bold and modern
- Framer.com - Smooth animations

---

## 🚀 Next Steps

1. [ ] Review this document with Stitch
2. [ ] Define scope for v1.0 (MVP)
3. [ ] Create wireframes in Figma
4. [ ] Design system (components, tokens)
5. [ ] High-fidelity mockups
6. [ ] Prototypes for key flows
7. [ ] Asset export and handoff

---

**Document Version**: 1.0  
**Last Updated**: January 20, 2026  
**Author**: Martin @ Vectores  
**Designer**: Stitch @ Google
