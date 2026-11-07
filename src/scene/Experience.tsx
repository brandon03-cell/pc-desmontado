import { Suspense, useEffect, useState, useSyncExternalStore } from 'react'
import { Canvas } from '@react-three/fiber'
import { ContactShadows, Environment, Lightformer, PerformanceMonitor } from '@react-three/drei'
import { NoToneMapping } from 'three'
import { PCModel, GLB_URL } from './PCModel'
import { CameraRig } from './CameraRig'
import { Effects } from './Effects'
import { modeStore } from './animationState'
import { useAssetProbe } from './useAssetProbe'
import { HERO_CAM } from './choreography'

const HDRI_URL = '/hdri/studio_1k.hdr'

const query = '(pointer: coarse), (max-width: 767px)'
const subscribeMobile = (cb: () => void) => {
  const mq = window.matchMedia(query)
  mq.addEventListener('change', cb)
  return () => mq.removeEventListener('change', cb)
}
const useIsMobile = () =>
  useSyncExternalStore(
    subscribeMobile,
    () => window.matchMedia(query).matches,
    () => false,
  )

/** Estudio procedural (sin red) cuando todavía no existe el HDRI real. */
function ProceduralStudio() {
  return (
    <Environment resolution={256} environmentIntensity={0.9}>
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
  const mobile = useIsMobile()
  const glb = useAssetProbe(GLB_URL, import.meta.env.VITE_USE_PLACEHOLDERS ? 'no' : undefined)
  const hdri = useAssetProbe(HDRI_URL)
  const maxDpr = mobile ? 1.5 : 2
  const [dpr, setDpr] = useState(() => Math.min(window.devicePixelRatio || 1, maxDpr))
  const resolved = glb !== 'checking' && hdri !== 'checking'
  const mode = glb === 'yes' ? 'glb' : 'placeholder'

  useEffect(() => {
    if (resolved) modeStore.set(mode)
  }, [resolved, mode])

  if (!resolved) return null

  return (
    <Canvas
      dpr={Math.min(dpr, maxDpr)}
      shadows
      camera={{ fov: 32, near: 0.05, far: 30, position: HERO_CAM.pos }}
      gl={{ antialias: false, powerPreference: 'high-performance', toneMapping: NoToneMapping }}
    >
      <color attach="background" args={['#090b11']} />
      <PerformanceMonitor
        onDecline={() => setDpr((d) => Math.max(1, d - 0.25))}
        onIncline={() => setDpr((d) => Math.min(maxDpr, d + 0.25))}
      />
      <Suspense fallback={null}>
        {hdri === 'yes' ? <Environment files={HDRI_URL} environmentIntensity={0.9} /> : <ProceduralStudio />}
        <directionalLight
          position={[0.8, 1.8, 1.2]}
          intensity={1.4}
          castShadow={!mobile}
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
        <directionalLight position={[-1.2, 0.6, -1.4]} intensity={0.6} color="#8fa8ff" />
        <PCModel mode={mode} />
        <ContactShadows
          position={[0, 0.001, 0]}
          opacity={0.65}
          scale={2.4}
          blur={2.6}
          far={0.6}
          resolution={mobile ? 256 : 512}
        />
        <CameraRig />
        <Effects mobile={mobile} />
      </Suspense>
    </Canvas>
  )
}
