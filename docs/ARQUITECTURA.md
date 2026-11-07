# Arquitectura — PC desmontado

## Experiencia (secciones de scroll)
| # | Sección | Qué pasa en 3D |
|---|---------|----------------|
| 0 | Hero | PC montado girando lento. Título + CTA "haz scroll". |
| 1 | Panel de cristal | El cristal se separa hacia -X y se aparta. |
| 2 | Ventiladores | 3 frontales salen hacia +Z escalonados, el trasero hacia -Z. |
| 3 | GPU | Primero se desconecta el cable 16 pines (CablePCIe), luego la GPU sale hacia -X. |
| 4 | Disipador CPU | La torre se levanta hacia -X: queda a la vista la pasta térmica sobre el CPU. |
| 5 | CPU | El CPU (con su pasta) sale del socket. |
| 6 | RAM | Los 4 módulos salen hacia -X escalonados. |
| 7 | SSD M.2 | Se levanta el disipador del M.2 y luego el SSD. |
| 8 | PSU | Se desconecta el cable 24 pines y la fuente sale hacia atrás/abajo. |
| 9 | Placa base | La placa sale de la caja. |
| 10 | Caja vacía | Solo queda el chasis. |
| 11 | Vista explosionada | Cámara se aleja: todas las piezas flotan alrededor. |
| 12 | Remontaje | Al seguir bajando, todo vuelve a su sitio. |
| 13 | Cierre | Resumen + CTA. |

Scroll hacia arriba = reversa exacta (una única timeline de GSAP con `scrub`).

## Principio de animación
- Animación por código. Cada nodo del GLB tiene:
  - `assembled`: su transform original (leído del GLB al cargar).
  - `exploded`: posición/rotación "flotando" en la vista explosionada (definida en `choreography.ts`
    como offset relativo a `assembled`).
- Al quitar una pieza en su paso, se mueve de `assembled` a `exploded` (con una trayectoria de
  salida: primero un pequeño despegue en la dirección de montaje, luego al sitio de flote).
- Las piezas quitadas siguen flotando (fuera del encuadre de la cámara de primer plano). Al final
  la cámara se aleja y se ven todas: la vista explosionada sale "gratis" y coherente.
- Remontaje: todas vuelven a `assembled` con stagger.
- Cámara: keyframes por paso (posición + target) en `choreography.ts`, interpolados por la misma
  timeline.
- Nada de estado React por frame: la timeline escribe en objetos mutables/refs y `useFrame` aplica.

## Stack
Vite + React + TS · three / @react-three/fiber / drei · @react-three/postprocessing (Bloom
selectivo en emisivos RGB, ToneMapping AgX, N8AO en escritorio) · GSAP ScrollTrigger · Lenis.

## Assets
- `public/models/pc.glb` — exportado desde `blender/pc.blend` con `blender/scripts/export_glb.py`,
  optimizado con `tools/optimize-glb.mjs` (meshopt + texturas WebP). Presupuesto < 15 MB total.
- `public/hdri/studio_1k.hdr` — HDRI de estudio CC0 (Poly Haven).
- Materiales emisivos de RGB llevan `emissiveIntensity` > 1 para bloom selectivo (luminanceThreshold).

## Calidad adaptativa
- Escritorio: DPR hasta 2, N8AO, bloom, sombras de contacto.
- Móvil / GPU débil: DPR 1–1.5, sin N8AO, bloom más barato, paneles como bottom sheet.
- `PerformanceMonitor` de drei baja el DPR si cae el framerate.
