# Arquitectura — PC desmontado

## Experiencia (secciones de scroll)
| # | Sección | Qué pasa en 3D |
|---|---------|----------------|
| 0 | Hero | PC montado girando lento. Título + CTA "haz scroll". |
| 1 | Panel de cristal | El cristal se separa hacia -X y se aparta. |
| 2 | Ventiladores | Se sueltan hacia dentro (sin atravesar la malla frontal / trasera) y salen por el lateral (-X). |
| 3 | GPU | Primero se desconecta el cable 16 pines (CablePCIe), luego la GPU sale hacia -X. |
| 4 | Disipador CPU | La torre se levanta hacia -X: queda a la vista la pasta térmica sobre el CPU. |
| 5 | CPU | El CPU (con su pasta) sale del socket. |
| 6 | RAM | Los 4 módulos salen hacia -X escalonados. |
| 7 | SSD M.2 | Se levanta el disipador del M.2 y luego el SSD. |
| 8 | PSU | Se desconectan el 24 pines y el EPS; la fuente sale por detrás (-Z) bajo la cubierta. |
| 9 | Placa base | La placa sale de la caja. |
| 10 | Caja vacía | Solo queda el chasis. |
| 11 | Vista explosionada | Cámara se aleja: todas las piezas flotan alrededor. |
| 12 | Remontaje | Al seguir bajando, todo vuelve a su sitio. |
| 13 | Cierre | Resumen + CTA. |

Scroll hacia arriba = reversa exacta (una única timeline de GSAP con `scrub`).

## Principio de animación
- Animación por código. Cada nodo del GLB tiene:
  - `assembled`: su transform original (leído del GLB al cargar).
  - Trayectoria de salida en `choreography.ts` (offsets relativos a `assembled`):
    `lift` (desenchufar en la dirección de montaje: casi todo -X, perpendicular a la placa; la PSU
    -Z por detrás bajo la cubierta) → `via` (fuera de la caja por el lateral abierto, sin atravesar
    nada) → viaje en arco (primero sube, luego se desplaza) hasta quedar **aparcada** en
    `exploded + parkHeight`, muy por encima, fuera de los primeros planos.
  - `exploded`: sitio flotante en la vista explosionada, escrito en coordenadas de la cámara
    'explode' (u derecha, y altura, d profundidad) con el helper `at()`.
- Cada pieza se desenchufa y queda junto a su sitio mientras su panel es visible; se aleja al
  empezar el paso siguiente. En el paso 'explode' todas bajan a la vez de su aparcamiento a su
  sitio alrededor de la caja.
- Remontaje: todas deshacen su trayectoria (exploded → via → lift → assembled) en orden inverso.
- `pivot`: un nodo puede girar alrededor del origen de otro (la pasta térmica gira con el CPU).
- Rotores `*_Rotor`: giran mientras su pieza y la fuente están montadas; frenan con inercia al
  desmontarlas y arrancan de nuevo al remontar.
- Cámara: keyframes por paso (posición + target, `mobileDolly` opcional) en `choreography.ts`,
  interpolados por la misma timeline.
- Nada de estado React por frame: la timeline escribe en objetos mutables/refs y `useFrame` aplica.
- Depuración (solo `npm run dev`): `window.__pc.scrollToT(t)` salta al instante `t` de la timeline.

## Stack
Vite + React + TS · three / @react-three/fiber / drei · @react-three/postprocessing (Bloom
selectivo en emisivos RGB, ToneMapping AgX, N8AO en escritorio) · GSAP ScrollTrigger · Lenis.

N8AO va a resolución completa: con `halfRes` falla en three r187 (`reading 'length'`), porque la
render target MRT de n8ao 2.0.1 sobrescribe `texture` con el array `textures` y three lee
`renderTarget.texture.mipmaps`.

## Assets
- `public/models/pc.glb` — exportado desde `blender/pc.blend` con `blender/scripts/export_glb.py`,
  optimizado con `tools/optimize-glb.mjs` (meshopt + texturas WebP). Presupuesto < 15 MB total.
- `public/hdri/studio_1k.hdr` — HDRI de estudio CC0 (Poly Haven).
- Materiales emisivos de RGB llevan `emissiveIntensity` > 1 para bloom selectivo (luminanceThreshold).

## Calidad adaptativa
- Escritorio: `pc.glb`, DPR hasta 2, N8AO, bloom, cristal con transmisión, sombras de contacto.
- Móvil / GPU débil: `pc-mobile.glb` (texturas 1024), DPR 1–1.5, sin N8AO, cristal alpha, bloom
  más barato, paneles como bottom sheet.
- `PerformanceMonitor` de drei baja el DPR si cae el framerate.
