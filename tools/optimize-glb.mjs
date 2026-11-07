// Pipeline de optimizacion del GLB (conserva jerarquia, nombres y mallas compartidas).
// Uso: npm run assets:optimize
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { dedup, prune, weld, reorder, quantize, meshopt, textureCompress } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import sharp from 'sharp';
import { statSync, mkdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const INPUT = resolve(ROOT, 'assets-src/pc_raw.glb');
const OUT_DIR = resolve(ROOT, 'public/models');
const MAX_DESKTOP_BYTES = 15 * 1024 * 1024;
const REQUIRED = ['Case', 'GlassPanel', 'FanFront1', 'FanFront2', 'FanFront3', 'FanRear', 'GPU', 'CablePCIe',
  'CPUCooler', 'CPU', 'ThermalPaste', 'RAM1', 'RAM2', 'RAM3', 'RAM4', 'SSD', 'SSDHeatsink', 'PSU',
  'Cable24Pin', 'CableEPS', 'Motherboard'];
const VARIANTS = [
  { name: 'desktop', file: 'pc.glb', maxTex: 2048 },
  { name: 'mobile', file: 'pc-mobile.glb', maxTex: 1024 },
];

await MeshoptEncoder.ready;
await MeshoptDecoder.ready;
const io = new NodeIO()
  .registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });

const mb = (b) => (b / 1048576).toFixed(2) + ' MB';
const warnings = [];

async function build({ maxTex, file }) {
  const doc = await io.read(INPUT);
  const resize = [maxTex, maxTex];
  const tc = (slots, quality) =>
    textureCompress({ encoder: sharp, targetFormat: 'webp', resize, slots, quality });

  await doc.transform(
    dedup(),
    // keepLeaves: no borra nodos vacios (ni con nombre); keepExtras conserva userData
    prune({ keepLeaves: true, keepExtras: true }),
    weld(),
    reorder({ encoder: MeshoptEncoder }),
    // Defaults conservadores: pos 14 bit, normal 8 bit, texcoord 12 bit. Volumen por malla
    // (las mallas compartidas siguen siendo la misma malla; el nodo lleva la dequantizacion).
    quantize(),
    // Normal maps: calidad alta para evitar bandas
    tc(/^normalTexture$/, 92),
    // Metal-rugosidad y oclusion
    tc(/^(metallicRoughness|occlusion)Texture$/, 85),
    // Color y emisivas
    tc(/^(baseColor|emissive)Texture$/, 82),
    meshopt({ encoder: MeshoptEncoder, level: 'medium' }),
  );

  mkdirSync(OUT_DIR, { recursive: true });
  const out = resolve(OUT_DIR, file);
  await io.write(out, doc);
  return out;
}

function stats(doc) {
  let tris = 0;
  for (const mesh of doc.getRoot().listMeshes())
    for (const prim of mesh.listPrimitives()) {
      const idx = prim.getIndices();
      const pos = prim.getAttribute('POSITION');
      const n = idx ? idx.getCount() : pos ? pos.getCount() : 0;
      const mode = prim.getMode();
      if (mode === 4) tris += n / 3;
      else if (mode === 5 || mode === 6) tris += Math.max(0, n - 2);
    }
  // triangulos instanciados (por nodo) = lo que realmente se dibuja
  let drawn = 0;
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh();
    if (!mesh) continue;
    for (const prim of mesh.listPrimitives()) {
      const idx = prim.getIndices();
      const n = idx ? idx.getCount() : prim.getAttribute('POSITION').getCount();
      drawn += prim.getMode() === 4 ? n / 3 : 0;
    }
  }
  return { tris, drawn };
}

function report(label, inSize, outPath, doc) {
  const root = doc.getRoot();
  const scene = root.listScenes()[0];
  const tops = scene.listChildren();
  const normalTex = new Set(root.listMaterials().map((m) => m.getNormalTexture()).filter(Boolean));
  console.log(`\n=== ${label} ===`);
  console.log(`Entrada: ${mb(inSize)}  ->  Salida: ${mb(statSync(outPath).size)}  (${outPath})`);
  console.log('Nodos de primer nivel:');
  for (const n of tops) {
    const kids = n.listChildren().map((c) => c.getName());
    console.log(`  - ${n.getName()}${n.getMesh() ? ` [mesh:${n.getMesh().getName()}]` : ''}${kids.length ? ` -> hijos: ${kids.join(', ')}` : ''}`);
  }
  const { tris, drawn } = stats(doc);
  console.log(`Mallas: ${root.listMeshes().length} | Nodos totales: ${root.listNodes().length} | Materiales: ${root.listMaterials().length}`);
  console.log(`Texturas: ${root.listTextures().length}`);
  for (const t of root.listTextures()) {
    const [w, h] = t.getSize() ?? [0, 0];
    console.log(`  - ${t.getName() || t.getURI() || '(sin nombre)'}: ${w}x${h} ${t.getMimeType()}${normalTex.has(t) ? ' (normal)' : ''}`);
  }
  console.log(`Triangulos: ${Math.round(tris)} unicos en mallas, ${Math.round(drawn)} dibujados (con instancias)`);
  return { tops: tops.map((n) => n.getName()), tris };
}

const inSize = statSync(INPUT).size;
let failed = false;

{
  const src = await io.read(INPUT);
  const s = stats(src);
  console.log(`Entrada ${INPUT}: ${mb(inSize)}, ${src.getRoot().listMeshes().length} mallas, ${Math.round(s.tris)} tris unicos / ${Math.round(s.drawn)} dibujados`);
  const inNames = new Set(src.getRoot().listScenes()[0].listChildren().map((n) => n.getName()));
  var inputNodeNames = new Set(src.getRoot().listNodes().map((n) => n.getName()));
  var inputMeshCount = src.getRoot().listMeshes().length;
}

for (const v of VARIANTS) {
  const out = await build(v);
  // Re-lectura con decoder para verificar que el archivo es valido y conserva nombres
  const re = await io.read(out);
  const { tops } = report(`${v.name} (texturas max ${v.maxTex}px)`, inSize, out, re);
  const outNames = new Set(re.getRoot().listNodes().map((n) => n.getName()));
  const lost = [...inputNodeNames].filter((n) => !outNames.has(n));
  if (lost.length) { warnings.push(`${v.name}: nodos perdidos: ${lost.join(', ')}`); failed = true; }
  if (re.getRoot().listMeshes().length > inputMeshCount) warnings.push(`${v.name}: mas mallas que en la entrada (se perdio el compartido?)`);
  const missing = REQUIRED.filter((n) => !tops.includes(n));
  if (missing.length) { console.error(`FALTAN nodos de primer nivel (${v.name}): ${missing.join(', ')}`); failed = true; }
  if (v.name === 'desktop' && statSync(out).size > MAX_DESKTOP_BYTES) {
    console.error(`El GLB de escritorio supera 15 MB (${mb(statSync(out).size)})`); failed = true;
  }
  console.log(`Re-lectura OK (NodeIO + MeshoptDecoder), nombres conservados: ${lost.length === 0}`);
}

if (warnings.length) console.warn('\nAdvertencias:\n' + warnings.map((w) => '  ! ' + w).join('\n'));
process.exit(failed ? 1 : 0);
