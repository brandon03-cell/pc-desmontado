import type { PiezaContenido } from './types'

/** TEMPORAL: textos de relleno hasta que llegue src/content/piezas.ts desde main. */
const rel = (id: PiezaContenido['id'], paso: string, titulo: string, etiqueta: string): PiezaContenido => ({
  id,
  paso,
  titulo,
  etiqueta,
  queEs: `Texto provisional: ${titulo} es un componente esencial del ordenador.`,
  paraQue: 'Texto provisional: aquí se explicará para qué sirve esta pieza dentro del conjunto.',
  queBuscar: ['Criterio de compra uno', 'Criterio de compra dos', 'Criterio de compra tres'],
  datos: [
    { valor: '00', unidad: 'u', texto: 'Dato destacado uno' },
    { valor: '00', unidad: 'u', texto: 'Dato destacado dos' },
  ],
})

export const PIEZAS_STUB: PiezaContenido[] = [
  rel('glass', '01', 'Panel de cristal', 'Cristal templado'),
  rel('fans', '02', 'Ventiladores', 'Refrigeración'),
  rel('gpu', '03', 'Tarjeta gráfica', 'GPU'),
  rel('cooler', '04', 'Disipador de CPU', 'Refrigeración CPU'),
  rel('cpu', '05', 'Procesador', 'CPU'),
  rel('ram', '06', 'Memoria RAM', 'RAM'),
  rel('ssd', '07', 'SSD M.2', 'Almacenamiento'),
  rel('psu', '08', 'Fuente de alimentación', 'PSU'),
  rel('motherboard', '09', 'Placa base', 'Motherboard'),
  rel('case', '10', 'Caja', 'Chasis'),
]
