"""Genera las texturas procedurales del PC (PIL + numpy).

Uso: python tools/gen_textures.py
Salida: assets-src/textures/*.png
"""
import math
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "blender", "scripts"))
import layout as L  # noqa: E402

OUT = os.path.join(ROOT, "assets-src", "textures")
os.makedirs(OUT, exist_ok=True)
FONTS = r"C:\Windows\Fonts"
rng = random.Random(42)
nrng = np.random.default_rng(42)


def font(name, px):
    return ImageFont.truetype(os.path.join(FONTS, name), max(6, int(px)))


def save(img, name):
    p = os.path.join(OUT, name)
    img.save(p, optimize=True)
    print("ok", name, img.size)


def height_to_normal(h, strength=2.0):
    """h: float array 0..1 -> normal map RGB (OpenGL / glTF, +Y arriba)."""
    gy, gx = np.gradient(h.astype(np.float32))
    nx = -gx * strength
    ny = gy * strength  # glTF: Y+ hacia arriba en la textura
    nz = np.ones_like(nx)
    ln = np.sqrt(nx * nx + ny * ny + nz * nz)
    n = np.stack([nx / ln, ny / ln, nz / ln], -1)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8), "RGB")


# ---------------------------------------------------------------- Placa base
def motherboard():
    PX = 8.4  # px por mm
    W, H = int(L.MB_W * PX), int(L.MB_H * PX)
    W, H = 2048, 2560
    sx, sy = W / L.MB_W, H / L.MB_H

    def R(r):
        return (r[0] * sx, r[1] * sy, r[2] * sx, r[3] * sy)

    def P(u, v):
        return (u * sx, v * sy)

    base = np.full((H, W, 3), (17, 19, 21), np.float32)
    base += nrng.normal(0, 1.2, (H, W, 1))
    alb = Image.fromarray(base.clip(0, 255).astype(np.uint8), "RGB")
    d = ImageDraw.Draw(alb)
    hgt = Image.new("L", (W, H), 0)
    dh = ImageDraw.Draw(hgt)
    rough = Image.new("L", (W, H), 120)   # máscara de soldadura semibrillante
    dr = ImageDraw.Draw(rough)
    metal = Image.new("L", (W, H), 0)
    dm = ImageDraw.Draw(metal)

    # Planos de masa (zonas ligeramente distintas)
    for _ in range(14):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        w, h = rng.uniform(150, 600), rng.uniform(150, 600)
        d.rectangle((x0, y0, x0 + w, y0 + h), fill=(20, 22, 25))
        dh.rectangle((x0, y0, x0 + w, y0 + h), fill=40)

    # Pistas: segmentos en 0/45/90 grados, en haces paralelos
    trace_col = (27, 30, 33)
    for _ in range(420):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        n = rng.randint(2, 9)
        gap = rng.choice([7, 9, 11])
        segs = []
        cx, cy = x, y
        for _s in range(rng.randint(2, 5)):
            ang = rng.choice([0, 45, 90, 135, 180, 225, 270, 315])
            ln = rng.uniform(40, 340)
            nx = cx + math.cos(math.radians(ang)) * ln
            ny = cy + math.sin(math.radians(ang)) * ln
            segs.append((cx, cy, nx, ny, ang))
            cx, cy = nx, ny
        wdt = rng.choice([2, 2, 3, 4])
        for k in range(n):
            off = (k - n / 2) * gap
            for (ax, ay, bx, by, ang) in segs:
                px_, py_ = -math.sin(math.radians(ang)) * off, math.cos(math.radians(ang)) * off
                d.line((ax + px_, ay + py_, bx + px_, by + py_), fill=trace_col, width=wdt)
                dh.line((ax + px_, ay + py_, bx + px_, by + py_), fill=110, width=wdt)
        # vía al final del haz
        vx, vy = cx, cy
        d.ellipse((vx - 6, vy - 6, vx + 6, vy + 6), fill=(120, 96, 52))
        d.ellipse((vx - 2.5, vy - 2.5, vx + 2.5, vy + 2.5), fill=(8, 8, 8))
        dm.ellipse((vx - 6, vy - 6, vx + 6, vy + 6), fill=255)

    # Vías sueltas
    for _ in range(1600):
        vx, vy = rng.uniform(0, W), rng.uniform(0, H)
        d.ellipse((vx - 4, vy - 4, vx + 4, vy + 4), fill=(110, 92, 55))
        d.ellipse((vx - 1.5, vy - 1.5, vx + 1.5, vy + 1.5), fill=(6, 6, 6))
        dm.ellipse((vx - 4, vy - 4, vx + 4, vy + 4), fill=200)

    # SMD pequeños pintados (resistencias/condensadores 0402/0603)
    def smd(x, y, horiz=True, s=1.0):
        w, h = (14 * s, 7 * s) if horiz else (7 * s, 14 * s)
        d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=rng.choice([(40, 32, 26), (58, 50, 40), (24, 24, 26)]))
        if horiz:
            d.rectangle((x - w / 2, y - h / 2, x - w / 2 + 3 * s, y + h / 2), fill=(170, 170, 172))
            d.rectangle((x + w / 2 - 3 * s, y - h / 2, x + w / 2, y + h / 2), fill=(170, 170, 172))
        else:
            d.rectangle((x - w / 2, y - h / 2, x + w / 2, y - h / 2 + 3 * s), fill=(170, 170, 172))
            d.rectangle((x - w / 2, y + h / 2 - 3 * s, x + w / 2, y + h / 2), fill=(170, 170, 172))
        dh.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=200)
        dm.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=90)

    for _ in range(140):
        cx, cy = rng.uniform(40, W - 40), rng.uniform(40, H - 40)
        horiz = rng.random() < 0.5
        for k in range(rng.randint(3, 14)):
            if horiz:
                smd(cx + k * 22, cy, rng.random() < 0.5)
            else:
                smd(cx, cy + k * 22, rng.random() < 0.5)

    # Serigrafía
    silk = (226, 226, 220)
    ws = Image.new("L", (W, H), 0)
    dws = ImageDraw.Draw(ws)

    def silk_rect(r, w=3):
        x0, y0, x1, y1 = R(r)
        d.rectangle((x0, y0, x1, y1), outline=silk, width=w)
        dws.rectangle((x0, y0, x1, y1), outline=255, width=w)

    def silk_text(u, v, txt, size_mm=2.2, f="arialbd.ttf", anchor="lm", rot=0):
        fn = font(f, size_mm * sy)
        if rot == 0:
            d.text(P(u, v), txt, fill=silk, font=fn, anchor=anchor)
            dws.text(P(u, v), txt, fill=255, font=fn, anchor=anchor)
        else:
            bb = fn.getbbox(txt)
            tw, th = bb[2] - bb[0] + 8, bb[3] - bb[1] + 8
            t = Image.new("L", (tw, th), 0)
            ImageDraw.Draw(t).text((4 - bb[0], 4 - bb[1]), txt, fill=255, font=fn)
            t = t.rotate(rot, expand=True)
            x, y = P(u, v)
            x, y = int(x - t.width / 2), int(y - t.height / 2)
            alb.paste(Image.new("RGB", t.size, silk), (x, y), t)
            ws.paste(255, (x, y), t)

    # Contornos de componentes
    silk_rect(L.SOCKET_FRAME, 4)
    for u in L.DIMM_U:
        silk_rect((u - L.DIMM_W / 2 - 1, L.DIMM_V[0] - 1, u + L.DIMM_W / 2 + 1, L.DIMM_V[1] + 1))
    for r in (L.PCIE1, L.PCIE2, L.PCIE_X1, L.ATX24, L.M2_HEATSINK, L.CHIPSET_HS, L.SATA, L.M2_2_HS, L.FRONT_HDR, L.AUDIO):
        silk_rect((r[0] - 1, r[1] - 1, r[2] + 1, r[3] + 1))
    for r in L.EPS:
        silk_rect((r[0] - 1, r[1] - 0.5, r[2] + 1, r[3] + 1))

    for i, u in enumerate(L.DIMM_U):
        silk_text(u, L.DIMM_V[1] + 4, ["DDR5_A1", "DDR5_A2", "DDR5_B1", "DDR5_B2"][i], 1.9, anchor="mm", rot=90)
    silk_text(L.PCIE1[2] + 4, (L.PCIE1[1] + L.PCIE1[3]) / 2, "PCIEX16_1", 2.4)
    silk_text(L.PCIE2[2] + 4, (L.PCIE2[1] + L.PCIE2[3]) / 2, "PCIEX16_2", 2.4)
    silk_text(L.PCIE_X1[2] + 4, (L.PCIE_X1[1] + L.PCIE_X1[3]) / 2, "PCIEX1_1", 2.2)
    silk_text(L.M2_HEATSINK[0], L.M2_HEATSINK[3] + 3.2, "M.2_1 (SOCKET 3)  PCIe 5.0 x4", 2.0)
    silk_text(L.ATX24[0] - 3, (L.ATX24[1] + L.ATX24[3]) / 2, "ATX_24P", 2.2, anchor="mm", rot=90)
    silk_text(L.EPS[0][0], L.EPS[0][3] + 2.8, "EPS_12V1", 1.9)
    silk_text(L.EPS[1][0], L.EPS[1][3] + 2.8, "EPS_12V2", 1.9)
    silk_text(L.CPU_FAN_HDR[0], L.CPU_FAN_HDR[3] + 2.8, "CPU_FAN", 1.8)
    silk_text(L.SATA[0] - 3, (L.SATA[1] + L.SATA[3]) / 2, "SATA6G_1234", 1.9, anchor="mm", rot=90)
    silk_text(L.FRONT_HDR[0], L.FRONT_HDR[1] - 2.5, "F_PANEL   USB3_2   F_AUDIO   SYS_FAN2", 1.8)
    silk_text(L.SOCKET_FRAME[0], L.SOCKET_FRAME[3] + 3, "SOCKET AM5", 2.2)
    silk_text(L.CHIPSET_HS[0], L.CHIPSET_HS[3] + 3.4, "BIOS_FLBK    CLR_CMOS", 1.8)
    silk_text(176, 262, L.BRAND, 7.0, f="bahnschrift.ttf", anchor="mm")
    silk_text(176, 270.5, L.MODEL, 2.6, f="bahnschrift.ttf", anchor="mm")
    silk_text(80, 300, "REV 1.02   MADE IN TAIWAN   94V-0   E359012", 1.6, f="consola.ttf")
    # Cotas de fases VRM
    for i, (u, v) in enumerate(L.VRM_CHOKES_TOP):
        silk_text(u, v + 6.2, f"PL{i + 1}", 1.3, f="consola.ttf", anchor="mm")
    # Marcadores de orientación del socket (triángulo)
    sx0, sy0 = P(L.SOCKET_FRAME[0] + 2, L.SOCKET_FRAME[3] - 2)
    d.polygon([(sx0, sy0), (sx0 + 30, sy0), (sx0, sy0 - 30)], fill=silk)
    dws.polygon([(sx0, sy0), (sx0 + 30, sy0), (sx0, sy0 - 30)], fill=255)

    # Agujeros de montaje (anillo estañado + agujero)
    for (u, v) in L.HOLES:
        x, y = P(u, v)
        r1, r2 = 3.6 * sx, 1.7 * sx
        d.ellipse((x - r1, y - r1, x + r1, y + r1), fill=(178, 176, 170))
        d.ellipse((x - r2, y - r2, x + r2, y + r2), fill=(4, 4, 4))
        dm.ellipse((x - r1, y - r1, x + r1, y + r1), fill=255)
        dr.ellipse((x - r1, y - r1, x + r1, y + r1), fill=80)

    # Pads del socket AM5 (bajo el CPU se ve el LGA: dorado)
    cu, cv = L.SOCKET_C
    x0, y0 = P(cu - 21, cv - 21)
    x1, y1 = P(cu + 21, cv + 21)
    d.rectangle((x0, y0, x1, y1), fill=(30, 30, 32))
    step = 1.05
    for i in range(40):
        for j in range(40):
            if 14 <= i <= 25 and 14 <= j <= 25:
                continue
            px_, py_ = P(cu - 20.5 + i * step, cv - 20.5 + j * step)
            d.rectangle((px_ - 2.2, py_ - 2.2, px_ + 2.2, py_ + 2.2), fill=(196, 160, 82))
            dm.rectangle((px_ - 2.2, py_ - 2.2, px_ + 2.2, py_ + 2.2), fill=255)

    alb_np = np.asarray(alb).astype(np.float32)
    save(alb, "mb_albedo.png")

    # Rugosidad/metal: glTF -> G = rough, B = metal
    ws_np = np.asarray(ws).astype(np.float32) / 255
    rough_np = np.asarray(rough).astype(np.float32) / 255
    rough_np = np.maximum(rough_np, ws_np * 0.75)
    metal_np = np.asarray(metal).astype(np.float32) / 255
    rough_np = np.where(metal_np > 0.5, 0.3, rough_np)
    mr = np.stack([np.ones_like(rough_np), rough_np, metal_np], -1)
    save(Image.fromarray((mr * 255).astype(np.uint8), "RGB"), "mb_mr.png")

    h = np.asarray(hgt.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    h = h + ws_np * 0.35
    save(height_to_normal(h, 3.0), "mb_normal.png")


# ---------------------------------------------------------------- Metal cepillado
def brushed():
    S = 1024
    a = nrng.normal(0, 1, (S, S)).astype(np.float32)
    # Rayas: ruido estirado en X (muy suavizado horizontal)
    img = Image.fromarray(((a * 0.5 + 0.5).clip(0, 1) * 255).astype(np.uint8), "L")
    img = img.resize((S // 64, S), Image.BILINEAR).resize((S, S), Image.BICUBIC)
    streak = np.asarray(img).astype(np.float32) / 255
    fine = nrng.normal(0, 1, (S, S)).astype(np.float32)
    fimg = Image.fromarray(((fine * 0.5 + 0.5).clip(0, 1) * 255).astype(np.uint8), "L")
    fimg = fimg.resize((S // 16, S), Image.BILINEAR).resize((S, S), Image.BICUBIC)
    f2 = np.asarray(fimg).astype(np.float32) / 255
    s = 0.6 * streak + 0.4 * f2
    # Hacer tileable mezclando con versión desplazada
    s = 0.5 * s + 0.5 * np.roll(s, S // 2, axis=0)
    s = 0.5 * s + 0.5 * np.roll(s, S // 2, axis=1)
    s = (s - s.min()) / (s.max() - s.min())
    save(height_to_normal(s, 1.4), "brushed_normal.png")
    rough = 0.22 + 0.16 * s
    mr = np.stack([np.ones_like(rough), rough, np.ones_like(rough)], -1)
    save(Image.fromarray((mr * 255).astype(np.uint8), "RGB"), "brushed_mr.png")


def powdercoat():
    S = 512
    a = nrng.normal(0, 1, (S, S)).astype(np.float32)
    img = Image.fromarray(((a * 0.5 + 0.5).clip(0, 1) * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(1.0))
    h = np.asarray(img).astype(np.float32) / 255
    save(height_to_normal(h, 2.0), "powder_normal.png")


# ---------------------------------------------------------------- Malla hexagonal (alpha)
def hexmesh():
    S = 512
    img = Image.new("L", (S, S), 255)
    d = ImageDraw.Draw(img)
    # agujeros hexagonales, 4 columnas x 7 filas aprox. por baldosa
    r = S / 16.0
    dx = r * math.sqrt(3) * 1.08
    dy = r * 1.5 * 1.08
    cols, rows = int(S / dx) + 2, int(S / dy) + 2
    dx, dy = S / round(S / dx), S / (2 * round(S / (2 * dy)))
    for j in range(-1, int(S / dy) + 2):
        for i in range(-1, int(S / dx) + 2):
            cx = i * dx + (dx / 2 if j % 2 else 0)
            cy = j * dy
            pts = [(cx + r * 0.86 * math.cos(math.radians(60 * k + 30)), cy + r * 0.86 * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            d.polygon(pts, fill=0)
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    rgba = Image.merge("RGBA", (Image.new("L", (S, S), 12), Image.new("L", (S, S), 12), Image.new("L", (S, S), 13), img))
    save(rgba, "hexmesh.png")


# ---------------------------------------------------------------- Anillo RGB
def rgb_ring():
    W, H = 1024, 8
    cols = [(0, 220, 255), (90, 80, 255), (210, 40, 255), (255, 40, 140), (90, 80, 255), (0, 220, 255)]
    img = Image.new("RGB", (W, H))
    px = img.load()
    for x in range(W):
        t = x / W * (len(cols) - 1)
        i = int(t)
        f = t - i
        a, b = cols[i], cols[min(i + 1, len(cols) - 1)]
        c = tuple(int(a[k] + (b[k] - a[k]) * f) for k in range(3))
        for y in range(H):
            px[x, y] = c
    save(img, "rgb_ring.png")


# ---------------------------------------------------------------- Etiquetas
def label_ram():
    W, H = 1024, 256  # cara del disipador 120 x 30 mm aprox
    img = Image.new("RGB", (W, H), (34, 35, 38))
    d = ImageDraw.Draw(img)
    # bandas diagonales en relieve
    for k in range(-10, 30):
        x = k * 60
        d.polygon([(x, H), (x + 30, H), (x + 30 + H * 0.6, 0), (x + H * 0.6, 0)], fill=(40, 41, 45))
    d.rectangle((0, 0, W, 10), fill=(60, 62, 66))
    d.text((60, H / 2 - 18), "AXON", fill=(235, 235, 235), font=font("bahnschrift.ttf", 70), anchor="lm")
    d.text((290, H / 2 - 22), "VELOCITY  DDR5", fill=(200, 200, 205), font=font("bahnschrift.ttf", 40), anchor="lm")
    d.text((290, H / 2 + 26), "6000 MT/s  ·  CL30  ·  16 GB  ·  1.35 V", fill=(150, 152, 158), font=font("bahnschrift.ttf", 26), anchor="lm")
    save(img, "ram_label.png")


def label_ssd():
    W, H = 1024, 282  # 80 x 22 mm
    img = Image.new("RGB", (W, H), (22, 22, 24))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), outline=(60, 60, 64), width=4)
    d.text((40, 70), "AXON", fill=(240, 240, 240), font=font("bahnschrift.ttf", 70), anchor="lm")
    d.text((260, 70), "NV5  PRO", fill=(0, 200, 240), font=font("bahnschrift.ttf", 56), anchor="lm")
    d.text((40, 150), "2 TB  ·  NVMe 2.0  ·  PCIe 5.0 x4  ·  M.2 2280", fill=(190, 190, 195), font=font("bahnschrift.ttf", 32), anchor="lm")
    d.text((40, 215), "S/N 4X1N2026KM08  ·  MODEL AX-NV5P-2T0", fill=(120, 120, 126), font=font("consola.ttf", 24), anchor="lm")
    # QR falso / datamatrix
    for i in range(14):
        for j in range(14):
            if rng.random() < 0.5 or i in (0, 13) or j in (0, 13):
                d.rectangle((880 + i * 8, 120 + j * 8, 887 + i * 8, 127 + j * 8), fill=(220, 220, 220))
    save(img, "ssd_label.png")


def label_psu():
    W, H = 1024, 552  # cara lateral 160 x 86 mm
    img = Image.new("RGB", (W, H), (20, 20, 22))
    d = ImageDraw.Draw(img)
    d.rectangle((30, 30, W - 30, H - 30), fill=(28, 28, 31), outline=(70, 70, 75), width=3)
    d.text((70, 95), "AXON", fill=(240, 240, 240), font=font("bahnschrift.ttf", 76), anchor="lm")
    d.text((320, 95), "VOLT 850G", fill=(210, 210, 214), font=font("bahnschrift.ttf", 60), anchor="lm")
    d.text((70, 160), "850 W  ·  ATX 3.1  ·  PCIe 5.1  ·  FULLY MODULAR", fill=(160, 160, 166), font=font("bahnschrift.ttf", 28), anchor="lm")
    # tabla de salidas
    cols = ["DC OUTPUT", "+3.3V", "+5V", "+12V", "-12V", "+5Vsb"]
    vals = ["MAX LOAD", "20A", "20A", "70.8A", "0.3A", "3A"]
    x0, y0, cw, rh = 70, 210, 140, 52
    for i, (c, v) in enumerate(zip(cols, vals)):
        d.rectangle((x0 + i * cw, y0, x0 + (i + 1) * cw, y0 + rh), outline=(110, 110, 116), width=2)
        d.rectangle((x0 + i * cw, y0 + rh, x0 + (i + 1) * cw, y0 + 2 * rh), outline=(110, 110, 116), width=2)
        d.text((x0 + i * cw + cw / 2, y0 + rh / 2), c, fill=(200, 200, 204), font=font("arialbd.ttf", 20), anchor="mm")
        d.text((x0 + i * cw + cw / 2, y0 + rh * 1.5), v, fill=(200, 200, 204), font=font("arial.ttf", 22), anchor="mm")
    d.text((70, 360), "AC INPUT 100-240V~ 12-6A 50/60Hz", fill=(140, 140, 146), font=font("consola.ttf", 24), anchor="lm")
    # sello 80 PLUS Gold genérico
    cx, cy = W - 150, 420
    d.ellipse((cx - 70, cy - 70, cx + 70, cy + 70), fill=(196, 160, 70))
    d.ellipse((cx - 58, cy - 58, cx + 58, cy + 58), fill=(28, 28, 31))
    d.text((cx, cy - 12), "80", fill=(196, 160, 70), font=font("bahnschrift.ttf", 48), anchor="mm")
    d.text((cx, cy + 28), "GOLD", fill=(196, 160, 70), font=font("bahnschrift.ttf", 22), anchor="mm")
    for i, s in enumerate(["CE", "FC", "UL", "RoHS"]):
        d.text((70 + i * 90, 450), s, fill=(120, 120, 126), font=font("arialbd.ttf", 34), anchor="lm")
    save(img, "psu_label.png")


def ihs():
    S = 512  # 40 x 40 mm, la parte superior del IHS
    alb = Image.new("RGB", (S, S), (200, 200, 204))
    d = ImageDraw.Draw(alb)
    rough = Image.new("L", (S, S), 60)
    dr = ImageDraw.Draw(rough)
    # cepillado circular leve
    for r in range(4, 360, 3):
        c = 196 + rng.randint(-4, 4)
        d.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), outline=(c, c, c + 3))
    lines = [("AXON", 58, "bahnschrift.ttf"), ("NÚCLEO 9  9950", 30, "bahnschrift.ttf"), ("16C / 32T  ·  5.7 GHz", 24, "bahnschrift.ttf"),
             ("AX-9950-0170", 20, "consola.ttf"), ("2026 · DIFFUSED IN TAIWAN", 18, "consola.ttf")]
    y = 150
    for t, sz, f in lines:
        d.text((S / 2, y), t, fill=(150, 150, 156), font=font(f, sz), anchor="mm")
        dr.text((S / 2, y), t, fill=150, font=font(f, sz), anchor="mm")
        y += sz + 22
    # triángulo pin 1
    d.polygon([(30, S - 30), (70, S - 30), (30, S - 70)], fill=(160, 160, 166))
    save(alb, "ihs_albedo.png")
    r = np.asarray(rough).astype(np.float32) / 255
    mr = np.stack([np.ones_like(r), r, np.ones_like(r)], -1)
    save(Image.fromarray((mr * 255).astype(np.uint8), "RGB"), "ihs_mr.png")


def gpu_backplate():
    W, H = 2048, 816  # 305 x 121 mm
    alb = Image.new("RGB", (W, H), (58, 60, 64))
    d = ImageDraw.Draw(alb)
    mr = Image.new("RGB", (W, H), (255, 90, 255))   # metal anodizado
    dm = ImageDraw.Draw(mr)
    # franjas de diseño (pintura negra mate, dieléctrica)
    def paint(poly):
        d.polygon(poly, fill=(14, 14, 15))
        dm.polygon(poly, fill=(255, 150, 0))
    paint([(0, 0), (W * 0.36, 0), (W * 0.30, H), (0, H)])
    paint([(W * 0.39, 0), (W * 0.41, 0), (W * 0.35, H), (W * 0.33, H)])
    d.text((W * 0.15, H * 0.5), "AXON", fill=(220, 220, 224), font=font("bahnschrift.ttf", 150), anchor="mm")
    dm.text((W * 0.15, H * 0.5), "AXON", fill=(255, 120, 0), font=font("bahnschrift.ttf", 150), anchor="mm")
    d.text((W * 0.15, H * 0.5 + 120), "FORGE  90", fill=(150, 150, 156), font=font("bahnschrift.ttf", 54), anchor="mm")
    # líneas finas grabadas
    for k in range(8):
        y = H * 0.12 + k * 12
        d.line((W * 0.45, y, W * 0.78, y), fill=(74, 76, 80), width=3)
    save(alb, "gpu_backplate_albedo.png")
    save(mr, "gpu_backplate_mr.png")


def gpu_edge_logo():
    W, H = 1024, 128
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((W / 2, H / 2), "A X O N   ·   F O R G E", fill=(255, 255, 255), font=font("bahnschrift.ttf", 70), anchor="mm")
    save(img, "gpu_edge_logo.png")


def chipset_logo():
    S = 512
    img = Image.new("RGB", (S, S), (40, 42, 46))
    d = ImageDraw.Draw(img)
    for k in range(-20, 40):
        x = k * 22
        d.line((x, S, x + S, 0), fill=(46, 48, 52), width=8)
    d.text((S / 2, S / 2 - 30), "AXON", fill=(230, 230, 232), font=font("bahnschrift.ttf", 110), anchor="mm")
    d.text((S / 2, S / 2 + 60), "STRATOS", fill=(0, 200, 240), font=font("bahnschrift.ttf", 44), anchor="mm")
    save(img, "chipset_logo.png")


if __name__ == "__main__":
    motherboard()
    brushed()
    powdercoat()
    hexmesh()
    rgb_ring()
    label_ram()
    label_ssd()
    label_psu()
    ihs()
    gpu_backplate()
    gpu_edge_logo()
    chipset_logo()
