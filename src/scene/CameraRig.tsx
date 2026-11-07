import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import type { PerspectiveCamera } from 'three'
import { camState } from './animationState'

/** Aplica el estado de cámara escrito por la timeline (sin React por frame). */
export function CameraRig() {
  const lastKey = useRef('')
  useFrame(({ camera, size }) => {
    const c = camState
    camera.position.set(c.px, c.py, c.pz)
    camera.lookAt(c.tx, c.ty, c.tz)
    // Desplaza el encuadre para dejar sitio al panel de texto
    const key = `${size.width}x${size.height}:${c.shiftX.toFixed(4)}:${c.shiftY.toFixed(4)}`
    if (key !== lastKey.current) {
      lastKey.current = key
      const cam = camera as PerspectiveCamera
      if (c.shiftX === 0 && c.shiftY === 0) cam.clearViewOffset()
      else
        cam.setViewOffset(size.width, size.height, c.shiftX * size.width, c.shiftY * size.height, size.width, size.height)
    }
  })
  return null
}
