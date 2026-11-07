import { Bloom, EffectComposer, N8AO, ToneMapping } from '@react-three/postprocessing'
import { ToneMappingMode } from 'postprocessing'

/**
 * Postprocesado. Bloom solo en emisivos (umbral alto: los RGB del GLB llevan
 * KHR_materials_emissive_strength 3-6) y AgX como único tone mapping (el renderer va sin tone mapping).
 * Antialiasing por MSAA del composer.
 *
 * N8AO (solo escritorio), radio en metros a escala real. OJO: `halfRes` NO se puede activar con
 * three ≥ r17x: la render target MRT de n8ao 2.0.1 sobrescribe el getter `texture` para devolver el
 * array `textures`, y WebGLTextures.setupRenderTarget lee `renderTarget.texture.mipmaps.length` →
 * "Cannot read properties of undefined (reading 'length')". A resolución completa no usa esa target.
 */
export function Effects({ mobile }: { mobile: boolean }) {
  if (mobile) {
    return (
      <EffectComposer multisampling={2}>
        <Bloom luminanceThreshold={0.9} luminanceSmoothing={0.15} intensity={0.75} mipmapBlur radius={0.6} />
        <ToneMapping mode={ToneMappingMode.AGX} />
      </EffectComposer>
    )
  }
  return (
    <EffectComposer multisampling={4}>
      <N8AO aoRadius={0.035} distanceFalloff={0.4} intensity={1.8} quality="medium" />
      <Bloom luminanceThreshold={0.9} luminanceSmoothing={0.15} intensity={0.9} mipmapBlur radius={0.7} />
      <ToneMapping mode={ToneMappingMode.AGX} />
    </EffectComposer>
  )
}
