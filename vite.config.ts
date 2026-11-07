import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    // three.js (~745 kB min) es indivisible y solo se descarga con la escena 3D diferida;
    // el resto de chunks queda por debajo de 500 kB.
    chunkSizeWarningLimit: 750,
    rolldownOptions: {
      output: {
        codeSplitting: {
          groups: [
            { name: 'three', test: /node_modules[/\\]three[/\\]/, priority: 30 },
            { name: 'postfx', test: /node_modules[/\\](postprocessing|n8ao)[/\\]/, priority: 25 },
            {
              name: 'r3f',
              test: /node_modules[/\\](@react-three|three-stdlib|meshline|camera-controls|troika|detect-gpu|zustand|its-fine|react-use-measure|suspend-react|@monogrid)[/\\]/,
              priority: 20,
            },
            { name: 'react', test: /node_modules[/\\](react|react-dom|scheduler)[/\\]/, priority: 40 },
            { name: 'anim', test: /node_modules[/\\](gsap|lenis)[/\\]/, priority: 10 },
          ],
        },
      },
    },
  },
})
