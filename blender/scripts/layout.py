"""Cotas compartidas (mm) entre el generador de texturas y el modelado en Blender.

Placa base ATX 244 (u) x 305 (v) mm.
  u: desde el borde trasero (I/O) hacia el frente de la caja.
  v: desde el borde superior hacia abajo.
En Blender (Z arriba, frente = -Y, cristal = -X):
  x = MB_X - h/1000      (h = altura sobre la placa, mm, hacia el cristal)
  y = MB_Y0 - u/1000
  z = MB_Z0 - v/1000
"""

MB_W = 244.0
MB_H = 305.0
MB_X = 0.085      # cara de componentes de la placa (los componentes crecen hacia -X)
MB_T = 1.6        # grosor PCB (mm)
MB_Y0 = 0.212     # borde trasero
MB_Z0 = 0.445     # borde superior

# Rectángulos (u0, v0, u1, v1) en mm
IO_SHROUD = (0.0, 4.0, 30.0, 162.0)
VRM_TOP = (52.0, 11.0, 150.0, 34.0)
VRM_REAR = (31.0, 11.0, 51.0, 128.0)
EPS = [(34.0, 1.5, 52.0, 9.5), (56.0, 1.5, 74.0, 9.5)]
SOCKET_C = (118.0, 78.0)
SOCKET_FRAME = (88.0, 42.0, 148.0, 114.0)
CPU_SIZE = 40.0
DIMM_U = [170.0, 180.0, 194.0, 204.0]
DIMM_V = (10.0, 147.0)   # largo de la ranura con pestañas
DIMM_W = 6.4
ATX24 = (228.0, 84.0, 240.0, 136.0)
CPU_FAN_HDR = (152.0, 4.0, 162.0, 7.5)
M2_CONN = (60.0, 135.0, 66.0, 159.0)
M2_SSD = (66.0, 136.0, 146.0, 158.0)
M2_HEATSINK = (57.0, 132.5, 154.0, 161.5)
PCIE1 = (42.0, 168.0, 131.0, 175.0)    # x16 reforzado (GPU)
PCIE_X1 = (42.0, 228.0, 67.0, 234.0)
PCIE2 = (42.0, 252.0, 131.0, 259.0)
CHIPSET_HS = (160.0, 186.0, 230.0, 246.0)
M2_2_HS = (66.0, 268.0, 156.0, 293.0)
M2_3_HS = (40.0, 181.0, 128.0, 222.0)
# Cabeceras inferiores (u inicial, nº columnas) y su función
BOTTOM_HDRS = [(152.0, 5, "fpanel"), (166.0, 10, "usb3"), (194.0, 5, "audio"), (210.0, 4, "sysfan"), (226.0, 5, "argb")]
SATA = (229.0, 196.0, 242.0, 246.0)
FRONT_HDR = (150.0, 296.0, 238.0, 303.0)
AUDIO = (4.0, 258.0, 44.0, 302.0)
CMOS = (140.0, 214.0)  # centro, d=20
HOLES = [(6.5, 10.0), (6.5, 165.0), (6.5, 288.0), (163.0, 10.0), (163.0, 165.0),
         (163.0, 288.0), (237.5, 10.0), (237.5, 165.0), (237.5, 288.0)]

# Fases del VRM: chokes (centro u, v) alrededor del socket
VRM_CHOKES_TOP = [(64.0 + i * 8.6, 38.3) for i in range(10)]
VRM_CHOKES_REAR = [(55.5, 48.0 + i * 9.0) for i in range(8)]

BRAND = "AXON"
MODEL = "X870E STRATOS"


def mb_to_world(u, v, h=0.0):
    return (MB_X - h / 1000.0, MB_Y0 - u / 1000.0, MB_Z0 - v / 1000.0)
