/**
 * CONTRATO entre el modelo 3D (Blender -> public/models/pc.glb) y la web.
 *
 * Sistema de coordenadas (three.js, Y arriba, metros, escala real):
 *   - Origen: centro del suelo de la caja.
 *   - +Z = frente de la caja (ventiladores frontales), -Z = trasera (I/O, PCIe).
 *   - -X = lado del panel de cristal (lado "bonito"), +X = bandeja de la placa base.
 *   (Blender es Z-up: three(x, y, z) = blender(x, z, -y); el exportador glTF lo convierte.)
 *
 * Cada pieza es un nodo de primer nivel en el GLB con el nombre exacto de `nodes`.
 * En Blender, el origen de cada nodo está en su punto de montaje lógico (p. ej. la GPU en su
 * conector PCIe). OJO: la cuantización de meshopt (tools/optimize-glb.mjs) mueve el origen de los
 * nodos hoja al centro de su caja envolvente. La web solo usa offsets relativos al transform
 * `assembled`, así que no afecta; las rotaciones de la coreografía pivotan sobre ese centro.
 * La lista de nodos también está en blender/scripts/export_glb.py y tools/optimize-glb.mjs.
 * Hijos animables: "<Pieza>_Rotor" (FanFront1_Rotor…, FanRear_Rotor, CPUCooler_Rotor,
 * GPU_Fan1..3_Rotor, PSU_Fan_Rotor) son las aspas; giran sobre su eje local: Z para los
 * ventiladores de caja y del disipador, Y para los de la GPU y la PSU.
 * `approx` es la caja (centro y tamaño, en coordenadas three) medida sobre el GLB real: la usan los
 * placeholders y la coreografía (para colocar cada pieza en la vista explosionada).
 */

export type Vec3 = [number, number, number]

export type PartId =
  | 'glass'
  | 'fans'
  | 'gpu'
  | 'cooler'
  | 'cpu'
  | 'ram'
  | 'ssd'
  | 'psu'
  | 'motherboard'
  | 'case'

export interface PartNode {
  /** Nombre exacto del nodo en el GLB */
  name: string
  approx: { center: Vec3; size: Vec3 }
}

export interface PartDef {
  id: PartId
  /** Nodos que se mueven juntos en este paso (en orden de salida si hay escalonado) */
  nodes: PartNode[]
}

export const PARTS: PartDef[] = [
  {
    id: 'glass',
    nodes: [{ name: 'GlassPanel', approx: { center: [-0.116, 0.246, 0], size: [0.006, 0.462, 0.453] } }],
  },
  {
    id: 'fans',
    nodes: [
      { name: 'FanFront1', approx: { center: [-0.01, 0.14, 0.206], size: [0.12, 0.12, 0.025] } },
      { name: 'FanFront2', approx: { center: [-0.01, 0.265, 0.206], size: [0.12, 0.12, 0.025] } },
      { name: 'FanFront3', approx: { center: [-0.01, 0.39, 0.206], size: [0.12, 0.12, 0.025] } },
      { name: 'FanRear', approx: { center: [-0.024, 0.367, -0.212], size: [0.12, 0.12, 0.025] } },
    ],
  },
  {
    id: 'gpu',
    nodes: [
      { name: 'CablePCIe', approx: { center: [-0.063, 0.186, -0.041], size: [0.046, 0.202, 0.021] } },
      { name: 'GPU', approx: { center: [0.0115, 0.25, -0.072], size: [0.141, 0.068, 0.31] } },
    ],
  },
  {
    id: 'cooler',
    nodes: [{ name: 'CPUCooler', approx: { center: [-0.001, 0.367, -0.0815], size: [0.156, 0.13, 0.075] } }],
  },
  {
    id: 'cpu',
    nodes: [
      // La pasta térmica va pegada al CPU y sale con él
      { name: 'ThermalPaste', approx: { center: [0.0775, 0.366, -0.0935], size: [0.001, 0.032, 0.033] } },
      { name: 'CPU', approx: { center: [0.0805, 0.367, -0.094], size: [0.005, 0.04, 0.04] } },
    ],
  },
  {
    id: 'ram',
    nodes: [
      { name: 'RAM1', approx: { center: [0.0615, 0.3665, -0.0415], size: [0.043, 0.133, 0.007] } },
      { name: 'RAM2', approx: { center: [0.0615, 0.3665, -0.0315], size: [0.043, 0.133, 0.007] } },
      { name: 'RAM3', approx: { center: [0.0615, 0.3665, -0.0175], size: [0.043, 0.133, 0.007] } },
      { name: 'RAM4', approx: { center: [0.0615, 0.3665, -0.0075], size: [0.043, 0.133, 0.007] } },
    ],
  },
  {
    id: 'ssd',
    nodes: [
      { name: 'SSDHeatsink', approx: { center: [0.077, 0.298, -0.1065], size: [0.008, 0.03, 0.097] } },
      { name: 'SSD', approx: { center: [0.081, 0.298, -0.1065], size: [0.002, 0.022, 0.085] } },
    ],
  },
  {
    id: 'psu',
    nodes: [
      { name: 'Cable24Pin', approx: { center: [0.0725, 0.2535, 0.037], size: [0.061, 0.217, 0.048] } },
      { name: 'CableEPS', approx: { center: [0.0755, 0.4475, -0.1875], size: [0.055, 0.029, 0.057] } },
      { name: 'PSU', approx: { center: [0, 0.0595, -0.1485], size: [0.15, 0.085, 0.165] } },
    ],
  },
  {
    id: 'motherboard',
    nodes: [{ name: 'Motherboard', approx: { center: [0.0655, 0.2925, -0.0985], size: [0.049, 0.305, 0.261] } }],
  },
  {
    id: 'case',
    nodes: [{ name: 'Case', approx: { center: [0, 0.2415, -0.0015], size: [0.23, 0.483, 0.463] } }],
  },
]

export const ALL_NODE_NAMES = PARTS.flatMap((p) => p.nodes.map((n) => n.name))
