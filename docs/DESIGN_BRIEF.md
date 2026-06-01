# 🎨 GestureCam Design Brief for Stitch

> **Proyecto**: GestureCam - Virtual Camera with Gesture Control  
> **Cliente**: Martin @ Vectores  
> **Diseñador**: Stitch @ Google  
> **Fecha**: Enero 2026

---

## 📋 Resumen del Proyecto

GestureCam es una aplicación **gratuita y open source** que permite controlar el zoom y encuadre de cualquier webcam usando gestos de la mano. El objetivo es democratizar las funciones de cámaras profesionales para streamers, trabajadores remotos y creadores de contenido.

### Deliverables Requeridos

| Entregable     | Prioridad | Descripción                             |
| -------------- | --------- | --------------------------------------- |
| Landing Page   | P0        | Página web responsive para descargas    |
| Desktop App UI | P0        | Interfaz de la aplicación macOS/Windows |
| Gesture Icons  | P0        | Set de 6 iconos de gestos               |
| App Icon       | P0        | Icono para macOS, Windows, dock         |
| Logo           | P0        | Wordmark + Symbol                       |
| Mobile App UI  | P2        | App companion iOS/Android (futuro)      |

---

## 🎯 Brand Personality

### Core Values

- **Accesible**: Gratis, fácil de usar, sin barreras
- **Moderno**: Tecnología AI accesible a todos
- **Profesional**: Output de calidad broadcast
- **Amigable**: Gestos naturales, no intimidante

### Voz de Marca

- Casual pero profesional
- Técnico pero accesible
- Entusiasta sin ser exagerado
- Empoderador ("tú puedes hacerlo")

### Taglines Opcionales

- "Control your camera with a simple 👍"
- "Your webcam, now with superpowers"
- "Professional framing. Zero hardware."
- "Zoom with your hands, not your wallet"

---

## 🎨 Dirección Visual

### Mood Board Keywords

- Clean / Minimalist
- Dark Mode First
- Subtle Gradients
- Glassmorphism touches
- Micro-animations
- Tech-forward pero humano

### Inspiración Visual

**Apps que admiramos:**

- **Linear** - Dashboard limpio, dark mode elegante
- **Raycast** - Developer-focused, minimalista
- **Loom** - Recording UI simple y friendly
- **Arc Browser** - Bold, colorful, moderno
- **Figma** - Productividad sin ruido visual

**Landing Pages:**

- linear.app
- raycast.com
- framer.com
- vercel.com

---

## 🎨 Paleta de Colores (Sugerida)

### Primary Palette (Dark Mode)

```
Background:     #0A0A0F    (Near black)
Surface:        #16161D    (Card backgrounds)
Surface Hover:  #1E1E28    (Interactive states)
Border:         #2A2A35    (Subtle borders)
```

### Accent Colors

```
Primary:        #6366F1    (Indigo - Main actions)
Secondary:      #22D3EE    (Cyan - Detection highlights)
Success:        #10B981    (Green - Zoom in, active)
Warning:        #FBBF24    (Amber - Hold, pause)
Danger:         #EF4444    (Red - Zoom out, errors)
```

### Text Colors

```
Primary Text:   #FAFAFA    (White-ish)
Secondary:      #A1A1AA    (Gray)
Muted:          #71717A    (Dimmed)
```

### Gesture Color Coding

| Gesto         | Color              | Significado        |
| ------------- | ------------------ | ------------------ |
| 👍 Zoom In    | `#10B981` (Green)  | Acercar, positivo  |
| 👎 Zoom Out   | `#F97316` (Orange) | Alejar, retroceder |
| 🖐️ Hold       | `#FBBF24` (Amber)  | Pausar, esperar    |
| ☝️ Point Up   | `#22D3EE` (Cyan)   | Dirección arriba   |
| 👇 Point Down | `#8B5CF6` (Purple) | Dirección abajo    |
| ✊ Neutral    | `#71717A` (Gray)   | Sin acción         |

---

## 🔤 Tipografía

### Primaria: Inter

- Headlines: Inter Bold (700)
- Body: Inter Regular (400)
- Subtext: Inter Medium (500)

### Alternativa: SF Pro

Para macOS, usar SF Pro si es posible para integración nativa.

### Monospace: JetBrains Mono

Para stats, debug info, código.

### Escala Tipográfica

| Uso     | Size | Weight   |
| ------- | ---- | -------- |
| Display | 48px | Bold     |
| H1      | 32px | Bold     |
| H2      | 24px | Semibold |
| H3      | 18px | Semibold |
| Body    | 16px | Regular  |
| Small   | 14px | Regular  |
| Caption | 12px | Medium   |

---

## 📱 Pantallas a Diseñar

### 1. LANDING PAGE

#### 1.1 Hero Section

- Headline grande con emoji integrado
- Subheadline explicativo
- 2 CTAs: Download Mac / Download Windows
- Video/GIF demo del producto en acción
- Trust badges: "100% Free", "Open Source", "No Cloud"

#### 1.2 Features Section

- Grid de 6 features con iconos
- Gesture Control, Auto-Framing, Privacy, Virtual Camera, Real-time, Free

#### 1.3 Demo Section

- Video interactivo mostrando gestos
- Hover sobre iconos de gestos para ver en acción
- Split screen: Input (gestos) → Output (resultado)

#### 1.4 Use Cases

- Carousel o grid de casos de uso
- Streamers, Remote Workers, Educators, Creators
- Con ilustraciones o fotos + quotes

#### 1.5 Download Section

- Iconos grandes de macOS y Windows
- Información de requisitos
- Link a GitHub

#### 1.6 Footer

- Logo, links, social, copyright

---

### 2. DESKTOP APP

#### 2.1 Main Dashboard

```
┌─────────────────────────────────────────────┐
│  Logo                    [−] [□] [✕]       │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │                                     │   │
│  │         CAMERA PREVIEW              │   │
│  │                                     │   │
│  │    Zoom: 1.5x    Mode: FACE_FOLLOW │   │
│  │    Gesture: ZOOM IN 👍              │   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [Manual] [Face] [Headshot] [Shirt-Up]     │
│     ○       ●        ○          ○          │
│                                             │
│  ─────── Zoom: [━━━━━━━●━━] 1.5x ────────  │
│                                             │
│  [● Status: Active]        [⚙ Settings]   │
│                                             │
└─────────────────────────────────────────────┘
```

**Elementos clave:**

- Window controls nativos (traffic lights macOS)
- Preview de cámara dominante (70% del espacio)
- Overlay semitransparente con info
- Mode selector como toggle buttons
- Barra de zoom visual
- Status indicator

#### 2.2 Settings Panel

- Slide-in panel o modal
- Secciones colapsables
- Sliders para valores numéricos
- Dropdowns para selección
- Toggles para on/off

**Secciones:**

1. Camera (selección, resolución, FPS)
2. Zoom (máximo, suavizado, sensibilidad)
3. Framing (suavizado, modo default)
4. Gestures (toggles de features)
5. Output (virtual camera config)
6. General (startup, tray, updates)

#### 2.3 Gesture Guide Modal

- Pantalla educativa
- Grid de gestos con animaciones
- Tips de uso
- Botón "Practicar" que muestra preview

#### 2.4 Onboarding (3 steps)

- Step 1: Welcome + permisos de cámara
- Step 2: Selección de cámara
- Step 3: Tutorial rápido de gestos

#### 2.5 System Tray Menu

- Status (Active/Paused)
- Quick toggle modos
- Open app
- Settings
- Quit

---

### 3. MOBILE APP (P2)

#### 3.1 Home Screen

- Preview de cámara full screen
- Overlay con controles
- Indicador de conexión al desktop

#### 3.2 Connection Screen

- QR code para parear con desktop
- Lista de dispositivos disponibles
- Manual IP input

#### 3.3 Settings

- Versión simplificada de desktop
- Solo ajustes esenciales

---

## 🖼️ Assets Requeridos

### Logo

- Wordmark: "GestureCam"
- Symbol: Icono que represente mano + cámara
- Versiones: Light, Dark, Monochrome
- Formatos: SVG, PNG (@1x, @2x, @3x)

**Concepto sugerido:**

- Mano estilizada con ojo/lens de cámara
- O: Letra G formada por dedos
- O: Viewfinder con mano dentro

### App Icons

- macOS: 1024x1024, rounded rectangle
- Windows: 256x256, ICO format
- iOS: 1024x1024, square
- Android: 512x512, adaptive icon

### Gesture Icons Set

6 iconos de gestos:

1. 👍 Thumbs Up
2. 👎 Thumbs Down
3. ☝️ Point Up
4. 👇 Point Down
5. 🖐️ Open Palm
6. ✊ Fist

**Estilo:**

- Outline o Duo-tone
- Consistentes en peso de línea
- Reconocibles a 24x24px
- Con variantes de color por acción

### UI Icons

- Settings gear
- Camera
- User/Face
- Checkmark
- Close/X
- Minimize/Maximize
- Play/Pause
- Reset/Refresh
- Info/Help

### Social/Marketing

- Open Graph image (1200x630)
- Twitter card (1200x600)
- GitHub social preview (1280x640)
- App Store screenshots (varios sizes)

---

## 🎬 Animaciones

### Micro-interactions

1. **Gesture Detection Pulse**
   - Cuando se detecta un gesto, pulse suave en el indicador
   - Duration: 300ms
   - Easing: ease-out

2. **Zoom Level Animation**
   - Barra de zoom con animación spring
   - Número cambia con interpolación suave

3. **Mode Switch**
   - Transición crossfade entre modos
   - Duration: 200ms

4. **Button Hover/Press**
   - Scale sutil (1.02x) en hover
   - Opacity change en press

### Page Transitions (Landing)

1. **Scroll-triggered animations**
   - Fade in + slide up para secciones
   - Stagger para grids de features

2. **Hero animation**
   - Título aparece con typewriter o fade
   - Demo video auto-play on viewport

---

## 📐 Grid & Spacing

### Desktop App

- 8px base unit
- 16px standard padding
- 24px section spacing
- 4px border radius (subtle)
- 8px border radius (cards)
- 12px border radius (buttons)

### Landing Page

- 12-column grid
- Max-width: 1200px
- Gutters: 24px
- Section padding: 80px (desktop), 48px (mobile)

---

## 🔗 Recursos Adicionales

### Figma Community

- [Inter Font](https://www.figma.com/community/file/882640509573915972)
- [Phosphor Icons](https://www.figma.com/community/file/903830135544202908)
- [Lucide Icons](https://www.figma.com/community/file/1006630214587819248)

### Unsplash Collections

- Remote work / Work from home
- Streaming / Content creation
- Hands / Gestures

### Lottie Animations

- Hand gestures
- Success checkmarks
- Loading states

---

## 📅 Timeline Sugerido

| Fase          | Duración | Entregables                   |
| ------------- | -------- | ----------------------------- |
| Discovery     | 2-3 días | Moodboard, style tiles        |
| Wireframes    | 2-3 días | Lo-fi de todas las pantallas  |
| Visual Design | 5-7 días | Hi-fi mockups                 |
| Components    | 2-3 días | Design system, tokens         |
| Prototypes    | 2-3 días | Flows interactivos            |
| Assets        | 2 días   | Icons, illustrations, exports |

**Total estimado**: 2-3 semanas

---

## 💬 Preguntas para Stitch

1. ¿Prefieres empezar por landing o por app?
2. ¿Tienes preferencia de herramienta? (Figma assumed)
3. ¿Necesitas acceso al código/demo en vivo?
4. ¿Hay restricciones de assets (fotos, ilustraciones)?
5. ¿Qué nivel de detalle en prototipos?

---

## 📞 Contacto

**Martin**  
Email: martin@vectores.dev  
Discord: @martin_vectores

**Disponibilidad para feedback:**

- Lunes a Viernes, 9am - 6pm (hora México)
- Async feedback via Figma comments
- Calls semanales de sync

---

_Este documento es un punto de partida. Estoy abierto a sugerencias y cambios basados en tu expertise de diseño. ¡Gracias por ayudarnos a hacer GestureCam increíble!_ ✨
