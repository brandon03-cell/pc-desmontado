import { useEffect } from 'react'
import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import { sceneState } from '../scene/animationState'

gsap.registerPlugin(ScrollTrigger)

let lenis: Lenis | null = null

export const getLenis = () => lenis

/** Scroll suave a una posición (px). Respeta prefers-reduced-motion. */
export function scrollToY(y: number, duration = 1.8) {
  if (lenis) lenis.scrollTo(y, { duration, lock: false })
  else window.scrollTo({ top: y, behavior: sceneState.reducedMotion ? 'auto' : 'smooth' })
}

/** Lenis integrado con ScrollTrigger y el ticker de GSAP. */
export function useLenis() {
  useEffect(() => {
    if (sceneState.reducedMotion) return
    const instance = new Lenis({ lerp: 0.1, smoothWheel: true })
    lenis = instance
    const onTick = (time: number) => instance.raf(time * 1000)
    instance.on('scroll', ScrollTrigger.update)
    gsap.ticker.add(onTick)
    gsap.ticker.lagSmoothing(0)
    return () => {
      gsap.ticker.remove(onTick)
      instance.destroy()
      lenis = null
    }
  }, [])
}
