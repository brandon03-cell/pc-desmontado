# PC desmontado

Web en español con una experiencia de scroll 3D que desmonta, pieza a pieza, un PC de sobremesa
modelado con proporciones reales. Al bajar, cada componente se separa (vista explosionada) y aparece
un panel con qué es, para qué sirve y qué mirar al comprarlo; al final todas las piezas flotan y,
si sigues bajando, el PC se vuelve a montar. Hacia arriba, todo va en reversa.

## Arrancar

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # build de producción en dist/
npm run preview    # sirve dist/
```

## Stack
- Vite + React + TypeScript
- three.js · @react-three/fiber · @react-three/drei · @react-three/postprocessing (bloom, AgX)
- GSAP ScrollTrigger (una única timeline con `scrub`) + Lenis (scroll suave)
- Modelo: Blender 5.2 modelado 100 % por scripts → GLB → gltf-transform (meshopt + WebP)

## Estructura
```
blender/scripts/   Modelado procedural (un script por pieza) + materiales PBR + export GLB
blender/pc.blend   Escena de Blender generada por los scripts
blender/renders/   Renders de revisión
tools/             gen_textures.py (texturas PIL) · optimize-glb.mjs (meshopt + WebP)
assets-src/        Texturas fuente y HDRI 2k
public/models/     pc.glb (escritorio) y pc-mobile.glb (texturas a 1024)
src/scene/         parts.ts (contrato de nodos), choreography.ts (coreografía), escena R3F
src/scroll/        Timeline GSAP + Lenis
src/ui/            Loader, hero, paneles, navegación, cierre
src/content/       Textos de cada pieza
docs/              Arquitectura y capturas
```

## Regenerar el modelo
1. Texturas: `python tools/gen_textures.py`
2. En Blender (con `blender/pc.blend` abierto), consola de Python:
   ```python
   exec(open(r"blender/scripts/run.py").read()); build()          # todas las piezas
   exec(open(r"blender/scripts/export_glb.py").read()); export()  # → assets-src/pc_raw.glb
   ```
3. `npm run assets:optimize` → `public/models/pc.glb` y `pc-mobile.glb`

Las cotas compartidas de la placa (socket, DIMM, PCIe, M.2…) viven en `blender/scripts/layout.py`
y las usan tanto el modelado como la serigrafía generada, para que coincidan al milímetro.

## Afinar la coreografía
Todo está en `src/scene/choreography.ts`: cámara por paso, despegue (`lift`) y posición flotante
(`exploded`) de cada nodo, y tiempos (`TIMING`).

## Créditos
Ver [CREDITS.md](CREDITS.md).
