import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import type { PerspectiveCamera } from 'three'
import { camState } from './animationState'

/** Aplica el estado de cámara escrito por la timeline (sin React por frame). */
export function CameraRig() {
  const last = useRef({ w: 0, h: 0, sx: NaN, sy: NaN })
  useFrame(({ camera, size }) => {
    const c = camState
    // En pantallas estrechas se aleja la cámara para que quepa la pieza (dolly por aspecto)
    const k = Math.min(2.4, Math.max(1, 1.2 / (size.width / size.height))) * c.dolly
    camera.position.set(c.tx + (c.px - c.tx) * k, c.ty + (c.py - c.ty) * k, c.tz + (c.pz - c.tz) * k)
    camera.lookAt(c.tx, c.ty, c.tz)
    // Desplaza el encuadre para dejar sitio al panel de texto
    const l = last.current
    if (l.w !== size.width || l.h !== size.height || !(Math.abs(l.sx - c.shiftX) < 1e-4) || !(Math.abs(l.sy - c.shiftY) < 1e-4)) {
      l.w = size.width
      l.h = size.height
      l.sx = c.shiftX
      l.sy = c.shiftY
      const cam = camera as PerspectiveCamera
      if (c.shiftX === 0 && c.shiftY === 0) cam.clearViewOffset()
      else
        cam.setViewOffset(size.width, size.height, c.shiftX * size.width, c.shiftY * size.height, size.width, size.height)
    }
  })
  return null
}
