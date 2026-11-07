import { Bloom, EffectComposer, ToneMapping } from '@react-three/postprocessing'
import { ToneMappingMode } from 'postprocessing'

/**
 * Postprocesado. Bloom solo en emisivos (umbral alto) y AgX como único tone mapping.
 * Antialiasing por MSAA del composer.
 * N8AO y SMAA lanzan `Cannot read properties of undefined (reading 'length')` (texture.mipmaps)
 * con three 0.187 + postprocessing 6.39: desactivados hasta que las libs se actualicen.
 * Para probarlos: <N8AO aoRadius={0.08} distanceFalloff={0.6} intensity={2.2} quality="medium" halfRes /> antes de Bloom.
 */
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
    <EffectComposer multisampling={4}>
      <Bloom luminanceThreshold={0.9} luminanceSmoothing={0.15} intensity={1} mipmapBlur radius={0.7} />
      <ToneMapping mode={ToneMappingMode.AGX} />
    </EffectComposer>
  )
}

