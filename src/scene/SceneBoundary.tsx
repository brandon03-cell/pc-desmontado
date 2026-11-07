import { Component, type ReactNode } from 'react'
import { readyStore, sceneFailStore } from './animationState'

/** Si WebGL no está disponible o falla el chunk / GLB / HDRI: la página sigue siendo legible (sin 3D). */
export class SceneBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }
  static getDerivedStateFromError() {
    return { failed: true }
  }
  componentDidCatch(error: unknown) {
    console.error('[Escena 3D] No se ha podido cargar:', error)
    document.documentElement.classList.add('no-3d')
    sceneFailStore.set(true)
    readyStore.set(true)
  }
  render() {
    return this.state.failed ? null : this.props.children
  }
}
