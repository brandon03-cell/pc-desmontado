import { useEffect, useState } from 'react'

export type Probe = 'checking' | 'yes' | 'no'

/**
 * Comprueba si un asset existe de verdad (el dev server de Vite devuelve index.html con 200
 * para rutas inexistentes, así que además se descarta text/html).
 */
export function useAssetProbe(url: string, force?: 'yes' | 'no'): Probe {
  const [state, setState] = useState<Probe>(force ?? 'checking')
  useEffect(() => {
    if (force) return
    let alive = true
    fetch(url, { method: 'HEAD' })
      .then((r) => {
        const type = r.headers.get('content-type') ?? ''
        if (alive) setState(r.ok && !type.includes('text/html') ? 'yes' : 'no')
      })
      .catch(() => alive && setState('no'))
    return () => {
      alive = false
    }
  }, [url, force])
  return state
}
