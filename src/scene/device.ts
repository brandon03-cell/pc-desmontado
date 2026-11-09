import { useSyncExternalStore } from 'react'

/**
 * Definición única de "móvil" (alineada con el CSS: @media (max-width: 767px)).
 *  - `mobile`  : layout / encuadre de cámara / GLB ligero (pc-mobile.glb) / paneles bottom sheet.
 *  - `lowPower`: calidad gráfica reducida (sin N8AO, sin sombras, cristal alpha, DPR ≤ 1.5, sin
 *                backdrop-filter). Es `mobile` o puntero táctil (tabletas), aunque tengan layout de escritorio.
 */
export const MOBILE_QUERY = '(max-width: 767px)'
/** Móvil O puntero táctil (la coma en una media query equivale a "o") */
const LOW_POWER_QUERY = `${MOBILE_QUERY}, (pointer: coarse)`

export const isMobileNow = () => typeof window !== 'undefined' && window.matchMedia(MOBILE_QUERY).matches

/** Hook que devuelve si `query` se cumple, y re-renderiza cuando cambia. */
function mediaHook(query: string) {
  const subscribe = (cb: () => void) => {
    const mq = window.matchMedia(query)
    mq.addEventListener('change', cb)
    return () => mq.removeEventListener('change', cb)
  }
  const get = () => window.matchMedia(query).matches
  return () => useSyncExternalStore(subscribe, get, () => false)
}

export const useIsMobile = mediaHook(MOBILE_QUERY)
export const useIsLowPower = mediaHook(LOW_POWER_QUERY)

export const HDRI_URL = '/hdri/studio_1k.hdr'
export const glbUrlFor = (mobile: boolean) => (mobile ? '/models/pc-mobile.glb' : '/models/pc.glb')

/** En producción: empieza a descargar el GLB adecuado y el HDRI en cuanto carga la app (antes del chunk 3D). */
export function warmAssets() {
  if (!import.meta.env.PROD || typeof document === 'undefined') return
  for (const href of [glbUrlFor(isMobileNow()), HDRI_URL]) {
    const l = document.createElement('link')
    l.rel = 'preload'
    l.as = 'fetch'
    l.crossOrigin = 'anonymous'
    l.href = href
    document.head.appendChild(l)
  }
}
