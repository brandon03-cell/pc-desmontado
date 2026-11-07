import { useMemo } from 'react'
import * as THREE from 'three'
import { PARTS, type PartNode } from './parts'

/**
 * Piezas PROVISIONALES generadas a partir de PARTS[].nodes[].approx.
 * Mismos nombres de nodo de primer nivel que el GLB real, con origen en el centro de la caja `approx`.
 */

const metal = (color: string, rough = 0.45, metalness = 0.85) =>
  new THREE.MeshStandardMaterial({ color, roughness: rough, metalness })
const plastic = (color: string, rough = 0.55) =>
  new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0.1 })
const glow = (color: string, intensity = 4) =>
  new THREE.MeshStandardMaterial({
    color: '#000000',
    emissive: new THREE.Color(color),
    emissiveIntensity: intensity,
    toneMapped: false,
  })

const M = {
  case: metal('#1b1e27', 0.5, 0.7),
  glass: new THREE.MeshPhysicalMaterial({
    color: '#7f90ad',
    roughness: 0.05,
    metalness: 0,
    transparent: true,
    opacity: 0.1,
    depthWrite: false,
    side: THREE.DoubleSide,
  }),
  fan: plastic('#15171d'),
  gpu: metal('#262a35', 0.35, 0.8),
  cooler: metal('#8a93a6', 0.3, 0.95),
  cpu: metal('#c0c6d2', 0.3, 0.9),
  paste: plastic('#7d808a', 0.3),
  ram: plastic('#10131a', 0.4),
  ssd: plastic('#0f1118', 0.4),
  heatsink: metal('#566074', 0.35, 0.9),
  psu: metal('#14161c', 0.5, 0.6),
  board: plastic('#10321f', 0.45),
  cable: plastic('#0b0c10', 0.7),
  cyan: glow('#35e0ff'),
  violet: glow('#a06bff'),
}

type V3 = [number, number, number]

const mesh = (geo: THREE.BufferGeometry, mat: THREE.Material, pos: V3 = [0, 0, 0]) => {
  const m = new THREE.Mesh(geo, mat)
  m.position.set(...pos)
  m.castShadow = true
  m.receiveShadow = true
  return m
}
const box = (w: number, h: number, d: number) => new THREE.BoxGeometry(w, h, d)

function buildNode(node: PartNode): THREE.Group {
  const g = new THREE.Group()
  g.name = node.name
  const [cx, cy, cz] = node.approx.center
  const [sx, sy, sz] = node.approx.size
  g.position.set(cx, cy, cz)
  const base = (mat: THREE.Material) => g.add(mesh(box(sx, sy, sz), mat))

  switch (node.name) {
    case 'GlassPanel': {
      const m = mesh(box(sx, sy, sz), M.glass)
      m.castShadow = false
      g.add(m)
      break
    }
    case 'FanFront1':
    case 'FanFront2':
    case 'FanFront3':
    case 'FanRear': {
      base(M.fan)
      const ring = mesh(new THREE.TorusGeometry(sx * 0.4, 0.003, 12, 48), M.cyan, [0, 0, sz / 2 + 0.001])
      ring.castShadow = false
      g.add(ring)
      const hub = mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.008, 24), M.fan, [0, 0, sz / 2])
      hub.rotation.x = Math.PI / 2
      g.add(hub)
      break
    }
    case 'GPU': {
      base(M.gpu)
      g.add(mesh(box(sx * 0.96, 0.003, sz * 0.9), M.violet, [0, sy / 2 + 0.0015, 0]))
      for (const z of [-0.07, 0.07]) {
        const f = mesh(new THREE.TorusGeometry(0.028, 0.0025, 10, 32), M.cyan, [-sx / 2 - 0.001, 0, z])
        f.rotation.y = Math.PI / 2
        f.castShadow = false
        g.add(f)
      }
      break
    }
    case 'CPUCooler': {
      base(M.cooler)
      const ring = mesh(new THREE.TorusGeometry(0.045, 0.003, 10, 32), M.violet, [-sx / 2 - 0.001, 0, 0])
      ring.rotation.y = Math.PI / 2
      ring.castShadow = false
      g.add(ring)
      break
    }
    case 'ThermalPaste':
      base(M.paste)
      break
    case 'CPU':
      base(M.cpu)
      break
    case 'RAM1':
    case 'RAM2':
    case 'RAM3':
    case 'RAM4':
      base(M.ram)
      g.add(mesh(box(sx * 0.95, 0.012, sz * 1.05), M.cyan, [0, sy / 2 - 0.006, 0]))
      break
    case 'SSDHeatsink':
      base(M.heatsink)
      break
    case 'SSD':
      base(M.ssd)
      break
    case 'CablePCIe':
    case 'Cable24Pin':
      base(M.cable)
      break
    case 'PSU':
      base(M.psu)
      break
    case 'Motherboard':
      // El `approx` incluye componentes; la placa es una plancha fina en el lado +X
      g.add(mesh(box(0.004, sy, sz), M.board, [0.0175, 0, 0]))
      break
    case 'Case': {
      // chasis abierto por el lado -X (cristal) y por delante
      const t = 0.004
      g.add(mesh(box(sx, t, sz), M.case, [0, -sy / 2 + t / 2, 0])) // suelo
      g.add(mesh(box(sx, t, sz), M.case, [0, sy / 2 - t / 2, 0])) // techo
      g.add(mesh(box(t, sy, sz), M.case, [sx / 2 - t / 2, 0, 0])) // bandeja
      for (const x of [-1, 1])
        for (const z of [-1, 1])
          g.add(mesh(box(0.01, sy, 0.01), M.case, [(x * (sx - 0.01)) / 2, 0, (z * (sz - 0.01)) / 2]))
      break
    }
    default:
      base(M.case)
  }
  return g
}

export function buildPlaceholderRoot(): THREE.Group {
  const root = new THREE.Group()
  root.name = 'PlaceholderRoot'
  PARTS.forEach((p) => p.nodes.forEach((n) => root.add(buildNode(n))))
  return root
}

export function usePlaceholderRoot() {
  return useMemo(() => buildPlaceholderRoot(), [])
}
