import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { ALL_NODE_NAMES } from './parts'
import { NODES } from './choreography'
import { nodeAnim, readyStore, sceneState, type NodeAnim } from './animationState'
import { usePlaceholderRoot } from './Placeholders'

export const GLB_URL = '/models/pc.glb'
export const GLB_MOBILE_URL = '/models/pc-mobile.glb'

interface RigItem {
  obj: THREE.Object3D
  /** transform `assembled` leído al cargar */
  p0: THREE.Vector3
  q0: THREE.Quaternion
  anim: NodeAnim
  /** Si gira alrededor del origen de otro nodo: ese origen (espacio del padre) */
  pivot?: THREE.Vector3
}

/**
 * Aspas que giran. `rps` = vueltas/s con el PC montado; `dir` = sentido.
 * Una pieza "tiene corriente" si ella y la fuente están en su sitio: si no, frena hasta pararse.
 */
const ROTORS: { name: string; part: string; axis: 'y' | 'z'; rps: number; dir: 1 | -1 }[] = [
  { name: 'FanFront1_Rotor', part: 'FanFront1', axis: 'z', rps: 2.1, dir: -1 },
  { name: 'FanFront2_Rotor', part: 'FanFront2', axis: 'z', rps: 2.1, dir: -1 },
  { name: 'FanFront3_Rotor', part: 'FanFront3', axis: 'z', rps: 2.1, dir: -1 },
  { name: 'FanRear_Rotor', part: 'FanRear', axis: 'z', rps: 2.1, dir: -1 },
  { name: 'CPUCooler_Rotor', part: 'CPUCooler', axis: 'z', rps: 2.5, dir: -1 },
  // GPU: giro tranquilo (carga baja); el central en sentido contrario, como en las tarjetas reales
  { name: 'GPU_Fan1_Rotor', part: 'GPU', axis: 'y', rps: 1.2, dir: 1 },
  { name: 'GPU_Fan2_Rotor', part: 'GPU', axis: 'y', rps: 1.2, dir: -1 },
  { name: 'GPU_Fan3_Rotor', part: 'GPU', axis: 'y', rps: 1.2, dir: 1 },
  { name: 'PSU_Fan_Rotor', part: 'PSU', axis: 'y', rps: 1.4, dir: 1 },
]

interface RotorItem {
  obj: THREE.Object3D
  q0: THREE.Quaternion
  axis: THREE.Vector3
  part: NodeAnim
  rps: number
  dir: number
}

const _e = new THREE.Euler()
const _q = new THREE.Quaternion()
const _qd = new THREE.Quaternion()
const _v = new THREE.Vector3()
const TWO_PI = Math.PI * 2
const AXIS = { y: new THREE.Vector3(0, 1, 0), z: new THREE.Vector3(0, 0, 1) }

const isHome = (a: NodeAnim) =>
  Math.abs(a.x) + Math.abs(a.y) + Math.abs(a.z) < 1e-4 && Math.abs(a.rx) + Math.abs(a.ry) + Math.abs(a.rz) < 1e-4

/**
 * Cristal templado ahumado de escritorio: transmisión real (reflejos del HDRI a plena intensidad y
 * el interior atenuado por el tinte), en vez de alpha blending, que atenúa también los reflejos.
 */
function smokedGlass(src: THREE.MeshStandardMaterial) {
  return new THREE.MeshPhysicalMaterial({
    name: src.name,
    color: '#a7afb9',
    metalness: 0,
    roughness: 0.05,
    transmission: 1,
    thickness: 0.004,
    ior: 1.5,
    envMapIntensity: 1.5,
    side: THREE.FrontSide,
    depthWrite: false,
  })
}

/** Ajustes de materiales en runtime (los del GLB vienen de Blender). `hq`: escritorio. */
function tuneMaterials(root: THREE.Object3D, hq: boolean) {
  root.traverse((o) => {
    const mesh = o as THREE.Mesh
    if (!mesh.isMesh) return
    mesh.castShadow = true
    mesh.receiveShadow = true
    const mats = Array.isArray(mesh.material) ? mesh.material : [mesh.material]
    for (const m of mats as THREE.MeshStandardMaterial[]) {
      if (m.name === 'M_Glass_Tempered') {
        // Cristal: sin escribir profundidad (no tapa el interior ni el AO), dibujado al final
        if (hq) mesh.material = smokedGlass(m)
        else {
          m.depthWrite = false
          m.side = THREE.FrontSide
          m.envMapIntensity = 1.6
          m.roughness = 0.03
        }
        mesh.renderOrder = 10
        mesh.castShadow = false
        mesh.receiveShadow = false
      } else if (m.name === 'M_Mesh_Hex') {
        // Malla perforada (MASK): que no proyecte una sombra opaca sobre el interior
        mesh.castShadow = false
      }
    }
  })
}

/** Amplitud (rad) del vaivén del hero: ±50° */
const HERO_SWING = (50 * Math.PI) / 180

/** Aplica los offsets animados sobre `assembled` + giro lento del hero + aspas. Idéntico para GLB y placeholders. */
function Rig({ root, hq }: { root: THREE.Object3D; hq: boolean }) {
  const group = useRef<THREE.Group>(null)
  const spin = useRef(0)
  const heroPhase = useRef(0)
  /** Velocidad (rad/s) y ángulo de cada rotor */
  const rotorSpin = useRef<{ speed: number; angle: number }[]>([])

  const items = useMemo<RigItem[]>(() => {
    const out: RigItem[] = []
    const missing: string[] = []
    for (const name of ALL_NODE_NAMES) {
      const obj = root.getObjectByName(name)
      const anim = nodeAnim.get(name)
      if (!obj || !anim) {
        missing.push(name)
        continue
      }
      out.push({ obj, p0: obj.position.clone(), q0: obj.quaternion.clone(), anim })
    }
    for (const it of out) {
      const pv = NODES[it.obj.name]?.pivot
      const pvObj = pv ? out.find((o) => o.obj.name === pv) : undefined
      if (pvObj) it.pivot = pvObj.p0.clone()
    }
    if (missing.length) console.warn(`[PCModel] Faltan nodos en el modelo: ${missing.join(', ')}`)
    else if (import.meta.env.DEV) console.info(`[PCModel] ${out.length}/${ALL_NODE_NAMES.length} nodos encontrados`)
    tuneMaterials(root, hq)
    return out
  }, [root, hq])

  const rotors = useMemo<RotorItem[]>(() => {
    const out: RotorItem[] = []
    for (const r of ROTORS) {
      const obj = root.getObjectByName(r.name)
      const part = nodeAnim.get(r.part)
      if (!obj || !part) continue
      out.push({ obj, q0: obj.quaternion.clone(), axis: AXIS[r.axis], part, rps: r.rps, dir: r.dir })
    }
    return out
  }, [root])

  useEffect(() => {
    const id = requestAnimationFrame(() => readyStore.set(true))
    return () => cancelAnimationFrame(id)
  }, [])

  useFrame((_, rawDt) => {
    const dt = Math.min(rawDt, 0.1)
    for (const it of items) {
      const a = it.anim
      _e.set(a.rx, a.ry, a.rz)
      _q.setFromEuler(_e)
      it.obj.position.set(it.p0.x + a.x, it.p0.y + a.y, it.p0.z + a.z)
      if (it.pivot) {
        // Giro rígido alrededor del pivote: p = pv + Q·(p0 - pv) + a, con Q = q0·qe·q0⁻¹
        _qd.copy(it.q0).invert().premultiply(_q).premultiply(it.q0)
        _v.copy(it.p0).sub(it.pivot)
        it.obj.position.sub(_v)
        it.obj.position.add(_v.applyQuaternion(_qd))
      }
      it.obj.quaternion.copy(it.q0).multiply(_q)
    }

    // Aspas: aceleran / frenan con suavidad según tengan corriente
    const psu = nodeAnim.get('PSU')
    const mains = !psu || isHome(psu)
    rotors.forEach((r, k) => {
      const st = (rotorSpin.current[k] ??= { speed: 0, angle: 0 })
      const target = mains && isHome(r.part) && !sceneState.reducedMotion ? r.rps * TWO_PI : 0
      // Frenado más lento que el arranque (inercia de las aspas)
      st.speed = THREE.MathUtils.damp(st.speed, target, target > st.speed ? 1.6 : 0.9, dt)
      if (st.speed < 0.01 && target === 0) st.speed = 0
      st.angle = (st.angle + st.speed * r.dir * dt) % TWO_PI
      r.obj.quaternion.copy(r.q0).multiply(_q.setFromAxisAngle(r.axis, st.angle))
    })

    // Hero: vaivén lento (±50°) alrededor de la vista 3/4 del cristal, con velocidad de seno
    // (más lento en los extremos). Al empezar el scroll se amortigua a 0 (vista del cristal).
    const g = group.current
    if (!g) return
    const active = sceneState.t < 0.01 && !sceneState.reducedMotion
    if (active) heroPhase.current += dt * 0.28
    const target = active ? HERO_SWING * Math.sin(heroPhase.current) : 0
    spin.current = THREE.MathUtils.damp(spin.current, target, active ? 3 : 4, dt)
    g.rotation.y = spin.current
  })

  return (
    <group ref={group}>
      <primitive object={root} />
    </group>
  )
}

function GLBModel({ url, hq }: { url: string; hq: boolean }) {
  // drei registra el MeshoptDecoder por defecto; el GLB no usa Draco
  const { scene } = useGLTF(url, false, true)
  return <Rig root={scene} hq={hq} />
}

function PlaceholderModel() {
  const root = usePlaceholderRoot()
  return <Rig root={root} hq={false} />
}

export function PCModel({ mode, mobile }: { mode: 'glb' | 'placeholder'; mobile: boolean }) {
  return mode === 'glb' ? <GLBModel url={mobile ? GLB_MOBILE_URL : GLB_URL} hq={!mobile} /> : <PlaceholderModel />
}
