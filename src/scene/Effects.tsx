import { Bloom, EffectComposer, N8AO, SMAA, ToneMapping } from '@react-three/postprocessing'
import { ToneMappingMode } from 'postprocessing'

/** Postprocesado. Bloom solo en emisivos (umbral alto) y AgX como único tone mapping. */
export function Effects({ mobile }: { mobile: boolean }) {
  if (mobile) {
    return (
      <EffectComposer multisampling={4}>
        <Bloom luminanceThreshold={0.9} luminanceSmoothing={0.15} intensity={0.8} mipmapBlur radius={0.6} />
        <ToneMapping mode={ToneMappingMode.AGX} />
      </EffectComposer>
    )
  }
  return (
    <EffectComposer multisampling={0}>
      <N8AO aoRadius={0.08} distanceFalloff={0.6} intensity={2.2} quality="medium" halfRes />
      <Bloom luminanceThreshold={0.9} luminanceSmoothing={0.15} intensity={1} mipmapBlur radius={0.7} />
      <ToneMapping mode={ToneMappingMode.AGX} />
      <SMAA />
    </EffectComposer>
  )
}
