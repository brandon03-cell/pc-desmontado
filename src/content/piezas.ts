import type { PiezaContenido } from './types'

export const PIEZAS: PiezaContenido[] = [
  {
    id: 'glass',
    paso: '01',
    titulo: 'Panel de cristal',
    etiqueta: 'Cristal templado',
    queEs:
      'Una lámina de cristal templado de 4 mm que cierra el lateral de la caja. El templado la hace mucho más resistente a golpes que el cristal normal, pero no irrompible.',
    paraQue:
      'Deja ver el interior sin renunciar a proteger los componentes del polvo y de los golpes. Es, sobre todo, un escaparate.',
    queBuscar: [
      'Fijación con tornillos de mano o bisagra, para abrirla sin herramientas.',
      'Espesor de 4 mm o más: se nota menos vibración y más solidez.',
      'Tratamiento tintado u oscuro si prefieres menos reflejos.',
      'Maneja el cristal con cuidado: un golpe seco en el canto puede astillarlo.',
    ],
    datos: [
      { valor: '4', unidad: 'mm', texto: 'de espesor' },
      { valor: '1', texto: 'panel lateral' },
    ],
  },
  {
    id: 'fans',
    paso: '02',
    titulo: 'Ventiladores de caja',
    etiqueta: 'Flujo de aire',
    queEs:
      'Cuatro ventiladores de 120 mm: tres frontales que introducen aire fresco, con anillo ARGB, y uno trasero que expulsa el aire caliente.',
    paraQue:
      'Crean una corriente de aire que atraviesa la caja de delante hacia atrás. Así los componentes se refrigeran y trabajan a menos temperatura y con menos ruido.',
    queBuscar: [
      'Rodamiento hidrodinámico o magnético: duran más y suenan menos que el básico.',
      'Presión estática alta si hay malla, filtros o radiadores delante.',
      'Control PWM de 4 pines para regular la velocidad desde la placa.',
      'Más aire entrante que saliente evita acumular polvo en la caja.',
    ],
    datos: [
      { valor: '4', texto: 'ventiladores en total' },
      { valor: '120', unidad: 'mm', texto: 'de diámetro' },
      { valor: '3 + 1', texto: 'entrada y salida' },
    ],
  },
  {
    id: 'gpu',
    paso: '03',
    titulo: 'Tarjeta gráfica',
    etiqueta: 'GPU',
    queEs:
      'Un procesador especializado en cálculo paralelo, con su propia memoria y refrigeración, montado en una tarjeta de unos 30 cm. Esta lleva 16 GB de GDDR7 y tres ventiladores.',
    paraQue:
      'Genera las imágenes de los juegos, el vídeo y los gráficos 3D. También acelera tareas de inteligencia artificial y de renderizado.',
    queBuscar: [
      'Longitud y grosor frente a la holgura real de tu caja.',
      'VRAM suficiente: 16 GB para 1440p y 4K actuales.',
      'Consumo y conector: 12V-2x6 con fuente ATX 3.1 adecuada.',
      'Ranura PCIe x16 libre y backplate rígido contra la flexión.',
    ],
    datos: [
      { valor: '16', unidad: 'GB', texto: 'memoria GDDR7' },
      { valor: '300', unidad: 'W', texto: 'consumo aproximado' },
      { valor: '30', unidad: 'cm', texto: 'de longitud' },
    ],
  },
  {
    id: 'cooler',
    paso: '04',
    titulo: 'Disipador de CPU',
    etiqueta: 'Torre de aire',
    queEs:
      'Una torre de aletas de aluminio atravesada por 6 heatpipes de cobre, con un ventilador de 120 mm. La base toca el procesador a través de una fina capa de pasta térmica.',
    paraQue:
      'Los heatpipes llevan el calor del procesador hasta las aletas, y el ventilador lo disipa en el aire. La pasta térmica rellena las microimperfecciones entre ambas superficies.',
    queBuscar: [
      'Altura frente al espacio de la caja: las torres suelen medir 150-165 mm.',
      'Compatibilidad con el socket y holgura sobre los módulos de RAM.',
      'Capacidad de disipación (TDP) superior al consumo de tu CPU.',
      'Base de cobre pulida y pasta térmica incluida en el paquete.',
    ],
    datos: [
      { valor: '6', texto: 'heatpipes de cobre' },
      { valor: '120', unidad: 'mm', texto: 'ventilador' },
      { valor: '160', unidad: 'mm', texto: 'altura aproximada' },
    ],
  },
  {
    id: 'cpu',
    paso: '05',
    titulo: 'Procesador',
    etiqueta: 'CPU',
    queEs:
      'El chip que ejecuta las instrucciones del sistema. Este tiene 16 núcleos y 32 hilos, y se instala en un socket AM5 de la placa.',
    paraQue:
      'Coordina el sistema y hace los cálculos de programas, juegos y tareas pesadas como compilar o editar vídeo. Más núcleos ayudan en cargas paralelas; en juegos pesa más la velocidad por núcleo.',
    queBuscar: [
      'Socket compatible con tu placa y versión de BIOS actualizada.',
      'Equilibrio entre núcleos, frecuencia y caché según el uso real.',
      'Consumo máximo, para dimensionar disipador y VRM de la placa.',
      'Pasta térmica: un grano del tamaño de un guisante en el centro basta.',
    ],
    datos: [
      { valor: '16', texto: 'núcleos' },
      { valor: '32', texto: 'hilos' },
      { valor: 'AM5', texto: 'tipo de socket' },
    ],
  },
  {
    id: 'ram',
    paso: '06',
    titulo: 'Memoria RAM',
    etiqueta: 'DDR5',
    queEs:
      'Cuatro módulos DDR5 de 16 GB que suman 64 GB, a 6000 MT/s y latencia CL30, con disipador. Es una memoria rápida pero volátil: pierde los datos al apagar.',
    paraQue:
      'Guarda los programas y datos que la CPU usa en cada momento. Con más capacidad cabe más trabajo abierto a la vez sin recurrir al SSD.',
    queBuscar: [
      'Dos módulos en dual channel rinden mejor que uno solo.',
      'Perfil EXPO o XMP para alcanzar la velocidad anunciada.',
      'Con cuatro módulos, la frecuencia estable puede ser menor que con dos.',
      'Altura del disipador compatible con el ventilador de la torre.',
    ],
    datos: [
      { valor: '64', unidad: 'GB', texto: '4 módulos de 16 GB' },
      { valor: '6000', unidad: 'MT/s', texto: 'velocidad' },
      { valor: 'CL30', texto: 'latencia' },
    ],
  },
  {
    id: 'ssd',
    paso: '07',
    titulo: 'Almacenamiento SSD',
    etiqueta: 'NVMe M.2',
    queEs:
      'Una unidad de estado sólido NVMe en formato M.2 2280 de 2 TB. Va clavada directamente en la placa, bajo un disipador, y se conecta por PCIe.',
    paraQue:
      'Guarda el sistema, los programas y tus archivos. Arranca y carga en segundos, muy por encima de un disco duro mecánico.',
    queBuscar: [
      'Formato 2280 y ranura M.2 compatible con PCIe 4.0 o 5.0.',
      'Caché DRAM y buena resistencia (TBW) si escribes mucho.',
      'Disipador, sobre todo en PCIe 5.0, que se calienta bastante.',
      'Capacidad: 1 TB es el mínimo cómodo; 2 TB da margen.',
    ],
    datos: [
      { valor: '2', unidad: 'TB', texto: 'de capacidad' },
      { valor: '2280', texto: 'formato M.2' },
      { valor: '5000+', unidad: 'MB/s', texto: 'lectura secuencial' },
    ],
  },
  {
    id: 'psu',
    paso: '08',
    titulo: 'Fuente de alimentación',
    etiqueta: 'PSU',
    queEs:
      'Convierte la corriente alterna de la red en las tensiones continuas que usa el PC. Esta es de 850 W, certificación 80 PLUS Gold, ATX 3.1 y totalmente modular.',
    paraQue:
      'Alimenta toda la máquina. El cable de 24 pines lleva la energía a la placa y el 12V-2x6 a la GPU, que puede recibir hasta 600 W por él.',
    queBuscar: [
      'Potencia con margen: unos 200 W por encima del consumo de CPU y GPU.',
      'ATX 3.1 y conector 12V-2x6 nativo, sin adaptadores.',
      'Certificación 80 PLUS Gold o superior y garantía larga.',
      'Modular, con cables suficientes y longitud adecuada a tu caja.',
    ],
    datos: [
      { valor: '850', unidad: 'W', texto: 'potencia nominal' },
      { valor: 'Gold', texto: 'eficiencia 80 PLUS' },
      { valor: '600', unidad: 'W', texto: 'máx. del 12V-2x6' },
    ],
  },
  {
    id: 'motherboard',
    paso: '09',
    titulo: 'Placa base',
    etiqueta: 'ATX',
    queEs:
      'La placa de circuito principal, en formato ATX de 305 × 244 mm. Aloja el socket, los slots DIMM, la ranura PCIe x16, las ranuras M.2 y los conectores. Los disipadores cubren el VRM.',
    paraQue:
      'Conecta todos los componentes y reparte la energía entre ellos. El VRM adapta la tensión de la fuente a la que necesita el procesador.',
    queBuscar: [
      'Socket y chipset compatibles con tu CPU y con la RAM elegida.',
      'VRM robusto con buenos disipadores si usas CPU potente.',
      'Número de ranuras M.2, PCIe y puertos USB según tus necesidades.',
      'Tamaño ATX, micro-ATX o mini-ITX acorde con la caja.',
    ],
    datos: [
      { valor: '305 × 244', unidad: 'mm', texto: 'formato ATX' },
      { valor: '4', texto: 'slots DIMM' },
      { valor: 'x16', texto: 'ranura gráfica PCIe' },
    ],
  },
  {
    id: 'case',
    paso: '10',
    titulo: 'Caja',
    etiqueta: 'Mid-tower',
    queEs:
      'Una torre media de acero con frontal de malla, cubierta para la fuente y espacio para ordenar los cables por la parte trasera de la bandeja.',
    paraQue:
      'Sostiene y protege todas las piezas, guía el flujo de aire y esconde el cableado. Su diseño decide qué tamaño de componentes caben y cuánto se calientan.',
    queBuscar: [
      'Longitud máxima de GPU y altura máxima de disipador permitidas.',
      'Frontal de malla y filtros de polvo extraíbles.',
      'Espacio tras la bandeja y orificios para una buena gestión de cables.',
      'Formatos de placa admitidos y soporte para radiadores, si los quieres.',
    ],
    datos: [
      { valor: '460', unidad: 'mm', texto: 'de fondo' },
      { valor: '480', unidad: 'mm', texto: 'de alto' },
      { valor: 'Acero', texto: 'estructura principal' },
    ],
  },
]

export const HERO = {
  titulo: 'Dentro de un PC',
  subtitulo:
    'Diez piezas, una máquina: desmontamos un ordenador de sobremesa para ver qué hace cada componente y por qué importa.',
  cta: 'Haz scroll para desmontarlo',
}

export const EXPLOSIONADA = {
  titulo: 'Vista explosionada',
  texto:
    'Todas las piezas separadas, en el orden en que se montan. Cada una cumple una función, pero ninguna trabaja sola.',
}

export const REMONTAJE = {
  titulo: 'Volvemos a montarlo',
  texto:
    'Cada componente regresa a su sitio, desde la caja hasta el cristal. Así se convierte un montón de piezas en un ordenador.',
}

export const FINAL = {
  titulo: 'Diez piezas, una máquina',
  texto:
    'Un PC es la suma de componentes que se complementan: potencia, memoria, almacenamiento, energía y refrigeración. Entender qué hace cada uno te ayuda a elegir mejor y a no gastar de más.',
  ctaPrimario: 'Volver a empezar',
  ctaSecundario: 'Ver las piezas',
}
