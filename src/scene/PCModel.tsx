import { useEffect, useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import { useGLTF } from '@react-three/drei'
import * as THREE from 'three'
import { ALL_NODE_NAMES } from './parts'
import { nodeAnim, readyStore, sceneState, type NodeAnim } from './animationState'
import { usePlaceholderRoot } from './Placeholders'

export const GLB_URL = '/models/pc.glb'

interface RigItem {
  obj: THREE.Object3D
  /** transform `assembled` leído al cargar */
  p0: THREE.Vector3
  q0: THREE.Quaternion
  anim: NodeAnim
}

const _e = new THREE.Euler()
const _q = new THREE.Quaternion()
const TWO_PI = Math.PI * 2

/** Aplica los offsets animados sobre `assembled` + giro lento del hero. Idéntico para GLB y placeholders. */
function Rig({ root }: { root: THREE.Object3D }) {
  const group = useRef<THREE.Group>(null)
  const spin = useRef(0)

  const items = useMemo<RigItem[]>(() => {
    const out: RigItem[] = []
    for (const name of ALL_NODE_NAMES) {
      const obj = root.getObjectByName(name)
      const anim = nodeAnim.get(name)
      if (!obj || !anim) {
        console.warn(`[PCModel] Falta el nodo "${name}" en el modelo`)
        continue
      }
      out.push({ obj, p0: obj.position.clone(), q0: obj.quaternion.clone(), anim })
    }
    root.traverse((o) => {
      if ((o as THREE.Mesh).isMesh) {
        o.castShadow = true
        o.receiveShadow = true
      }
    })
    return out
  }, [root])

  useEffect(() => {
    const id = requestAnimationFrame(() => readyStore.set(true))
    return () => cancelAnimationFrame(id)
  }, [])

  useFrame((_, dt) => {
    for (const it of items) {
      const a = it.anim
      it.obj.position.set(it.p0.x + a.x, it.p0.y + a.y, it.p0.z + a.z)
      _e.set(a.rx, a.ry, a.rz)
      it.obj.quaternion.copy(it.q0).multiply(_q.setFromEuler(_e))
    }
    // Giro del hero: solo al inicio; al empezar el scroll se amortigua a la vuelta entera más cercana
    const g = group.current
    if (!g) return
    const active = sceneState.t < 0.01 && !sceneState.reducedMotion
    if (active) spin.current += dt * 0.2
    else spin.current = THREE.MathUtils.damp(spin.current, Math.round(spin.current / TWO_PI) * TWO_PI, 4, dt)
    g.rotation.y = spin.current
  })

  return (
    <group ref={group}>
      <primitive object={root} />
    </group>
  )
}

function GLBModel() {
  const { scene } = useGLTF(GLB_URL)
  return <Rig root={scene} />
}

function PlaceholderModel() {
  const root = usePlaceholderRoot()
  return <Rig root={root} />
}

export function PCModel({ mode }: { mode: 'glb' | 'placeholder' }) {
  return mode === 'glb' ? <GLBModel /> : <PlaceholderModel />
}
