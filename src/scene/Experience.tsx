import { Suspense, useEffect, useState } from 'react'
import { Canvas } from '@react-three/fiber'
import { Environment, Lightformer, PerformanceMonitor, useGLTF, useProgress } from '@react-three/drei'
import { NoToneMapping } from 'three'
import { PCModel } from './PCModel'
import { ContactShadowsOnDemand, ShadowMapUpdater } from './Shadows'
import { HDRI_URL, glbUrlFor, isMobileNow, useIsLowPower, useIsMobile } from './device'
import { CameraRig } from './CameraRig'
import { Effects } from './Effects'
import { modeStore, progressStore } from './animationState'
import { useAssetProbe } from './useAssetProbe'
import { HERO_CAM } from './choreography'

// Producción: sin sondeo HEAD; el GLB adecuado se pide cuanto antes
if (import.meta.env.PROD && !import.meta.env.VITE_USE_PLACEHOLDERS) useGLTF.preload(glbUrlFor(isMobileNow()), false, true)

/** Estudio procedural (sin red) cuando todavía no existe el HDRI real. */
function ProceduralStudio() {
  return (
    <Environment resolution={256} environmentIntensity={0.4}>
      <Lightformer form="rect" intensity={3} position={[0, 3, 2]} scale={[6, 3, 1]} rotation-x={Math.PI / 2.4} />
      <Lightformer
        form="rect"
        intensity={2}
        position={[-4, 1.5, 1]}
        scale={[3, 3, 1]}
        rotation-y={Math.PI / 2}
        color="#bcd8ff"
      />
      <Lightformer
        form="rect"
        intensity={1.6}
        position={[4, 1, -1]}
        scale={[3, 3, 1]}
        rotation-y={-Math.PI / 2}
        color="#d6c6ff"
      />
      <Lightformer form="rect" intensity={1.2} position={[0, 1, -4]} scale={[6, 2, 1]} />
    </Environment>
  )
}

export default function Experience() {
  if (import.meta.env.DEV && new URLSearchParams(location.search).has('nowebgl')) {
    throw new Error('WebGL simulado como no disponible (?nowebgl)')
  }
  const mobile = useIsMobile()
  const lowPower = useIsLowPower()
  const PROD = import.meta.env.PROD
  // Dev: sondeo HEAD de la URL que se va a usar (Vite sirve index.html con 200 en rutas inexistentes → placeholders).
  // Prod: se asume que existen; si fallan, el ErrorBoundary de App muestra el aviso.
  const glb = useAssetProbe(glbUrlFor(mobile), import.meta.env.VITE_USE_PLACEHOLDERS ? 'no' : PROD ? 'yes' : undefined)
  const hdri = useAssetProbe(HDRI_URL, PROD ? 'yes' : undefined)
  const maxDpr = lowPower ? 1.5 : 1.75
  const [dpr, setDpr] = useState(() => Math.min(window.devicePixelRatio || 1, maxDpr))
  const resolved = glb !== 'checking' && hdri !== 'checking'
  const mode = glb === 'yes' ? 'glb' : 'placeholder'

  const { progress } = useProgress()
  useEffect(() => progressStore.set(progress), [progress])

  useEffect(() => {
    if (resolved) modeStore.set(mode)
  }, [resolved, mode])

  if (!resolved) return null

  return (
    <Canvas
      dpr={Math.min(dpr, maxDpr)}
      shadows="percentage"
      camera={{ fov: 32, near: 0.05, far: 30, position: HERO_CAM.pos }}
      gl={{ antialias: false, powerPreference: 'high-performance', toneMapping: NoToneMapping }}
    >
      <color attach="background" args={['#090b11']} />
      <PerformanceMonitor
        flipflops={3}
        onFallback={() => setDpr(1)}
        onDecline={() => setDpr((d) => Math.max(1, d - 0.25))}
        onIncline={() => setDpr((d) => Math.min(maxDpr, d + 0.25))}
      />
      <Suspense fallback={null}>
        {hdri === 'yes' ? <Environment files={HDRI_URL} environmentIntensity={0.4} /> : <ProceduralStudio />}
        <directionalLight
          position={[0.8, 1.8, 1.2]}
          intensity={1.1}
          castShadow={!lowPower}
          shadow-mapSize={[2048, 2048]}
          shadow-camera-left={-0.7}
          shadow-camera-right={0.7}
          shadow-camera-top={0.9}
          shadow-camera-bottom={-0.5}
          shadow-camera-near={0.1}
          shadow-camera-far={5}
          shadow-bias={-0.0004}
          shadow-normalBias={0.002}
        />
        {/* Relleno suave desde el lado del cristal: que el interior negro no quede empastado */}
        <directionalLight position={[-1.6, 0.7, 0.4]} intensity={0.55} color="#e6edff" />
        {/* Rim frío desde atrás */}
        <directionalLight position={[-1.2, 0.6, -1.4]} intensity={0.7} color="#8fa8ff" />
        <PCModel mode={mode} mobile={mobile} lowPower={lowPower} />
        <ContactShadowsOnDemand resolution={lowPower ? 256 : 512} />
        {!lowPower && <ShadowMapUpdater />}
        <CameraRig />
        <Effects mobile={lowPower} />
      </Suspense>
    </Canvas>
  )
}
