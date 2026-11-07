import { useRef, useState } from 'react'
import { useFrame } from '@react-three/fiber'
import { ContactShadows } from '@react-three/drei'
import { sceneState } from './animationState'

/** ¿Se ha movido algo desde la última llamada? (t de la timeline o giro del hero) */
function useMoved() {
  const last = useRef({ t: NaN, spin: NaN })
  return () => {
    const l = last.current
    const moved = Number.isNaN(l.t) || Math.abs(sceneState.t - l.t) > 1e-4 || Math.abs(sceneState.spin - l.spin) > 1e-4
    l.t = sceneState.t
    l.spin = sceneState.spin
    return moved
  }
}

/** Mapa de sombras de la luz: solo se regenera cuando cambia t o el giro (autoUpdate desactivado). */
export function ShadowMapUpdater() {
  const moved = useMoved()
  const frames = useRef(0)
  useFrame(({ gl }) => {
    gl.shadowMap.autoUpdate = false
    // Los primeros frames siempre (el modelo y los materiales se compilan al cargar)
    if (moved() || frames.current++ < 10) gl.shadowMap.needsUpdate = true
  })
  return null
}

/**
 * ContactShadows renderiza cada frame por defecto. Con `frames={1}` solo lo hace tras cada render de
 * React del componente: se fuerza uno (≤ 8/s) cuando algo se ha movido, y siempre uno final al parar.
 */
export function ContactShadowsOnDemand({ resolution }: { resolution: number }) {
  const moved = useMoved()
  const [, setTick] = useState(0)
  const dirty = useRef(true)
  const lastBump = useRef(0)
  useFrame(({ clock }) => {
    if (moved()) dirty.current = true
    if (dirty.current && clock.elapsedTime - lastBump.current > 0.125) {
      dirty.current = false
      lastBump.current = clock.elapsedTime
      setTick((n) => n + 1)
    }
  })
  return (
    <ContactShadows
      position={[0, 0.001, 0]}
      opacity={0.65}
      scale={2.4}
      blur={2.6}
      far={0.6}
      resolution={resolution}
      frames={1}
    />
  )
}
