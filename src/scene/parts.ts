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
 * El origen de cada nodo está en su punto de montaje lógico (p. ej. la GPU en su conector PCIe).
 * Hijos animables: "<Pieza>_Rotor" (FanFront1_Rotor…, FanRear_Rotor, CPUCooler_Rotor,
 * GPU_Fan1..3_Rotor, PSU_Fan_Rotor) son las aspas; giran sobre su eje local: Z para los
 * ventiladores de caja y del disipador, Y para los de la GPU y la PSU.
 * `approx` es la caja aproximada (centro y tamaño, en coordenadas three) para placeholders
 * mientras no exista el GLB definitivo.
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
    nodes: [{ name: 'GlassPanel', approx: { center: [-0.117, 0.245, 0], size: [0.004, 0.46, 0.45] } }],
  },
  {
    id: 'fans',
    nodes: [
      { name: 'FanFront1', approx: { center: [-0.01, 0.14, 0.2], size: [0.12, 0.12, 0.025] } },
      { name: 'FanFront2', approx: { center: [-0.01, 0.265, 0.2], size: [0.12, 0.12, 0.025] } },
      { name: 'FanFront3', approx: { center: [-0.01, 0.39, 0.2], size: [0.12, 0.12, 0.025] } },
      { name: 'FanRear', approx: { center: [-0.024, 0.367, -0.2115], size: [0.12, 0.12, 0.025] } },
    ],
  },
  {
    id: 'gpu',
    nodes: [
      { name: 'CablePCIe', approx: { center: [-0.06, 0.2, -0.05], size: [0.03, 0.12, 0.03] } },
      { name: 'GPU', approx: { center: [0.015, 0.251, -0.066], size: [0.14, 0.068, 0.305] } },
    ],
  },
  {
    id: 'cooler',
    nodes: [{ name: 'CPUCooler', approx: { center: [0, 0.367, -0.094], size: [0.16, 0.13, 0.1] } }],
  },
  {
    id: 'cpu',
    nodes: [
      // La pasta térmica va pegada al CPU y sale con él
      { name: 'ThermalPaste', approx: { center: [0.077, 0.367, -0.094], size: [0.001, 0.03, 0.03] } },
      { name: 'CPU', approx: { center: [0.081, 0.367, -0.094], size: [0.006, 0.04, 0.04] } },
    ],
  },
  {
    id: 'ram',
    nodes: [
      { name: 'RAM1', approx: { center: [0.064, 0.367, -0.042], size: [0.042, 0.133, 0.007] } },
      { name: 'RAM2', approx: { center: [0.064, 0.367, -0.032], size: [0.042, 0.133, 0.007] } },
      { name: 'RAM3', approx: { center: [0.064, 0.367, -0.019], size: [0.042, 0.133, 0.007] } },
      { name: 'RAM4', approx: { center: [0.064, 0.367, -0.009], size: [0.042, 0.133, 0.007] } },
    ],
  },
  {
    id: 'ssd',
    nodes: [
      { name: 'SSDHeatsink', approx: { center: [0.078, 0.305, -0.077], size: [0.008, 0.024, 0.082] } },
      { name: 'SSD', approx: { center: [0.082, 0.305, -0.077], size: [0.004, 0.022, 0.08] } },
    ],
  },
  {
    id: 'psu',
    nodes: [
      { name: 'Cable24Pin', approx: { center: [0.07, 0.33, 0.03], size: [0.03, 0.06, 0.04] } },
      { name: 'CableEPS', approx: { center: [0.06, 0.45, -0.17], size: [0.03, 0.03, 0.02] } },
      { name: 'PSU', approx: { center: [0, 0.058, -0.14], size: [0.15, 0.086, 0.16] } },
    ],
  },
  {
    id: 'motherboard',
    nodes: [{ name: 'Motherboard', approx: { center: [0.07, 0.2925, -0.09], size: [0.04, 0.305, 0.244] } }],
  },
  {
    id: 'case',
    nodes: [{ name: 'Case', approx: { center: [0, 0.24, 0], size: [0.23, 0.48, 0.46] } }],
  },
]

export const ALL_NODE_NAMES = PARTS.flatMap((p) => p.nodes.map((n) => n.name))
