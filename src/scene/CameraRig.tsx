import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import type { PerspectiveCamera } from 'three'
import { camState } from './animationState'

/** Aplica el estado de cámara escrito por la timeline (sin React por frame). */
export function CameraRig() {
  // Último encuadre aplicado (Infinity: el primer frame siempre lo aplica)
  const last = useRef({ w: 0, h: 0, sx: Infinity, sy: Infinity })
  useFrame(({ camera, size }) => {
    const c = camState
    const { width: w, height: h } = size
    // En pantallas estrechas se aleja la cámara para que quepa la pieza (dolly por aspecto)
    const k = Math.min(2.4, Math.max(1, 1.2 / (w / h))) * c.dolly
    camera.position.set(c.tx + (c.px - c.tx) * k, c.ty + (c.py - c.ty) * k, c.tz + (c.pz - c.tz) * k)
    camera.lookAt(c.tx, c.ty, c.tz)

    // Desplaza el encuadre para dejar sitio al panel de texto (solo si ha cambiado)
    const l = last.current
    const changed = l.w !== w || l.h !== h || Math.abs(l.sx - c.shiftX) >= 1e-4 || Math.abs(l.sy - c.shiftY) >= 1e-4
    if (!changed) return
    Object.assign(l, { w, h, sx: c.shiftX, sy: c.shiftY })
    const cam = camera as PerspectiveCamera
    if (c.shiftX === 0 && c.shiftY === 0) cam.clearViewOffset()
    else cam.setViewOffset(w, h, c.shiftX * w, c.shiftY * h, w, h)
  })
  return null
}
