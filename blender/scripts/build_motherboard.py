"""Placa base ATX 305 x 244 mm (objeto Motherboard)."""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

import layout as L
import lib
from lib import cyl, boolean_cut, join, set_origin


def W(u, v, h=0.0):
    return L.mb_to_world(u, v, h)


def mb(name, u0, v0, u1, v1, h0, h1, M, mat_, coll, bevel=0.0, seg=2):
    """Caja en coordenadas de placa (mm). h: altura sobre la placa hacia el cristal."""
    a = W(u0, v0, h0)
    b = W(u1, v1, h1)
    mn = (min(a[0], b[0]), min(a[1], b[1]), min(a[2], b[2]))
    mx = (max(a[0], b[0]), max(a[1], b[1]), max(a[2], b[2]))
    return lib.box_minmax(name, mn, mx, bevel=bevel / 1000.0, seg=seg, mat_=mat_, coll=coll, uv_scale=0.05)


def mbcyl(name, u, v, r, h0, h1, mat_, coll, verts=20, bevel=0.0):
    x0 = W(u, v, h0)
    x1 = W(u, v, h1)
    c = ((x0[0] + x1[0]) / 2, x0[1], x0[2])
    return cyl(name, r / 1000.0, abs(h1 - h0) / 1000.0, c, "X", verts, bevel=bevel / 1000.0, mat_=mat_, coll=coll)


def pcb(M, coll):
    o = mb("mb_pcb", 0, 0, L.MB_W, L.MB_H, -L.MB_T, 0, M, M["pcb_mb"], coll, bevel=0.3, seg=1)
    me = o.data
    uvl = me.uv_layers.active
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            u = (L.MB_Y0 - co.y) * 1000 / L.MB_W
            v = 1.0 - (L.MB_Z0 - co.z) * 1000 / L.MB_H
            uvl.data[li].uv = (u, v)
    # Bordes: material de canto de PCB
    for poly in me.polygons:
        if abs(poly.normal.x) < 0.5:
            poly.material_index = 1
    me.materials.append(M["pcb_edge"])
    return o


def header(name, u, v, cols, rows, M, coll, pitch=2.54, shroud=True, along_u=True):
    """Cabecera de pines (con o sin carcasa)."""
    parts = []
    w = cols * pitch
    hgt = rows * pitch
    du, dv = (w, hgt) if along_u else (hgt, w)
    if shroud:
        parts.append(mb(name + "_sh", u, v, u + du, v + dv, 0, 8.5, M, M["connector"], coll, bevel=0.3))
    else:
        parts.append(mb(name + "_base", u, v, u + du, v + dv, 0, 2.5, M, M["connector"], coll))
    for i in range(cols):
        for j in range(rows):
            pu = u + (i + 0.5) * pitch if along_u else u + (j + 0.5) * pitch
            pv = v + (j + 0.5) * pitch if along_u else v + (i + 0.5) * pitch
            parts.append(mb(name + "_pin", pu - 0.32, pv - 0.32, pu + 0.32, pv + 0.32, 2.5, 8.8 if not shroud else 7.2, M, M["gold"], coll))
    return parts


def power_conn(name, u0, v0, u1, v1, cols, rows, h, M, coll):
    """Conector de alimentación (24p / EPS) con agujeros cuadrados."""
    body = mb(name, u0, v0, u1, v1, 0, h, M, M["connector"], coll, bevel=0.4)
    cuts = []
    pu = (u1 - u0) / cols
    pv = (v1 - v0) / rows
    for i in range(cols):
        for j in range(rows):
            cu = u0 + (i + 0.5) * pu
            cv = v0 + (j + 0.5) * pv
            s = min(pu, pv) * 0.34
            cuts.append(mb("cut", cu - s, cv - s, cu + s, cv + s, h - 6, h + 2, M, None, coll))
    boolean_cut(body, cuts)
    # pestaña de enganche
    lat = mb(name + "_latch", u0 - 1.5, (v0 + v1) / 2 - 2, u0, (v0 + v1) / 2 + 2, 2, h - 1, M, M["connector"], coll)
    return [body, lat]


def build(M, coll):
    lib.clear_collection(coll.name)
    P = [pcb(M, coll)]
    gm, dk = M["alu_dark"], M["alu_black"]

    # ---------------------------------------------------------- I/O trasero + cubierta
    u0, v0, u1, v1 = L.IO_SHROUD
    shroud = mb("io_shroud", u0, v0, u1, v1, 0, 40, M, dk, coll, bevel=1.5, seg=2)
    P.append(shroud)
    P.append(mb("io_shroud_face", u1 - 0.2, v0 + 6, u1 + 0.6, v1 - 6, 6, 36, M, gm, coll, bevel=0.8))
    P.append(mb("io_shroud_rgb", u1 + 0.5, v0 + 12, u1 + 1.0, v1 - 40, 30, 32, M, M["rgb"], coll))
    # escudo I/O integrado + puertos
    P.append(mb("io_shield", -12.8, 5, -12.0, 160, -1.0, 44, M, M["plastic"], coll))
    ports = [  # (v0, v1, h0, h1, tipo)
        (12, 26, 4, 18, "usb"), (12, 26, 22, 36, "usb"), (30, 44, 4, 18, "usb"), (30, 44, 22, 36, "usb"),
        (48, 64, 4, 18, "rj45"), (48, 62, 24, 38, "usb"), (68, 82, 4, 18, "usb"), (68, 82, 22, 36, "usb"),
        (86, 102, 4, 14, "hdmi"), (86, 96, 20, 30, "ant"), (98, 108, 20, 30, "ant"),
        (112, 126, 4, 18, "usb"), (112, 126, 22, 36, "usbc"), (132, 156, 4, 40, "audio"),
    ]
    for (a, b, h0, h1, kind) in ports:
        if kind == "ant":
            P.append(mbcyl("io_ant", -13.5, (a + b) / 2, 3.2, h0, h1, M["gold"], coll, 16))
            continue
        shell = M["tin"] if kind in ("usb", "hdmi", "usbc") else M["plastic"]
        P.append(mb("io_port", -13.2, a, 14, b, h0, h1, M, shell, coll, bevel=0.4))
        P.append(mb("io_port_in", -13.6, a + 1.2, -12.9, b - 1.2, h0 + 1.2, h1 - 1.2, M, M["plastic"] if kind != "rj45" else M["chip"], coll))
        if kind == "usb":
            P.append(mb("io_tongue", -13.8, a + 2.5, -13.0, b - 2.5, (h0 + h1) / 2 - 0.9, (h0 + h1) / 2 + 0.9, M, M["plastic_gloss"], coll))
        if kind == "audio":
            for k in range(3):
                P.append(mbcyl("io_jack", -13.8, 138 + k * 7, 2.6, 8, 12, M["plastic_grey"], coll, 16))
                P.append(mbcyl("io_jack", -13.8, 138 + k * 7, 2.6, 26, 30, M["plastic_grey"], coll, 16))

    # ---------------------------------------------------------- VRM
    def vrm_heatsink(name, r, h_top, along_v):
        u0, v0, u1, v1 = r
        hs = [mb(name, u0, v0, u1, v1, 1.5, h_top - 6, M, gm, coll, bevel=1.2, seg=2)]
        # aletas superiores
        n = 9
        if along_v:
            step = (u1 - u0 - 2) / n
            for k in range(n):
                a = u0 + 1 + k * step
                hs.append(mb(name + "_fin", a, v0 + 1, a + step * 0.55, v1 - 1, h_top - 6.5, h_top, M, gm, coll, bevel=0.4, seg=1))
        else:
            step = (v1 - v0 - 2) / 6
            for k in range(6):
                a = v0 + 1 + k * step
                hs.append(mb(name + "_fin", u0 + 1, a, u1 - 1, a + step * 0.55, h_top - 6.5, h_top, M, gm, coll, bevel=0.4, seg=1))
        hs.append(mb(name + "_pad", u0 + 1, v0 + 1, u1 - 1, v1 - 1, 0, 1.6, M, M["plastic_grey"], coll))
        return hs
    P += vrm_heatsink("vrm_top", L.VRM_TOP, 32, False)
    P += vrm_heatsink("vrm_rear", L.VRM_REAR, 34, True)
    # tapa decorativa en el disipador superior (une ambos)
    P.append(mb("vrm_cap", L.VRM_REAR[0], L.VRM_TOP[1], L.VRM_TOP[0] + 30, L.VRM_TOP[3], 32, 35, M, dk, coll, bevel=1.0))
    for (u, v) in L.VRM_CHOKES_TOP:
        P.append(mb("choke", u - 3.4, v - 3.0, u + 3.4, v + 3.0, 0, 5.0, M, M["choke"], coll, bevel=0.5, seg=1))
    for (u, v) in L.VRM_CHOKES_REAR:
        P.append(mb("choke", u - 3.0, v - 3.4, u + 3.0, v + 3.4, 0, 5.0, M, M["choke"], coll, bevel=0.5, seg=1))
    # condensadores sólidos
    for i in range(2):
        for j in range(6):
            u, v = 66 + i * 7.5, 52 + j * 9
            P.append(mbcyl("cap", u, v, 2.6, 0, 7.5, M["cap_sleeve"], coll, 16, 0.3))
            P.append(mbcyl("cap_top", u, v, 2.3, 7.5, 7.9, M["cap"], coll, 16))
    for i in range(6):
        u, v = 155 + (i % 2) * 6.5, 50 + (i // 2) * 8
        P.append(mbcyl("cap", u, v, 2.6, 0, 7.5, M["cap_sleeve"], coll, 16, 0.3))
        P.append(mbcyl("cap_top", u, v, 2.3, 7.5, 7.9, M["cap"], coll, 16))

    # ---------------------------------------------------------- Conectores de alimentación
    for i, r in enumerate(L.EPS):
        P += power_conn(f"eps{i}", r[0], r[1], r[2], r[3], 4, 2, 12, M, coll)
    a = L.ATX24
    P += power_conn("atx24", a[0], a[1], a[2], a[3], 2, 12, 12, M, coll)
    # LEDs de diagnóstico
    for k, col in enumerate(("led_white", "led_white", "chip", "chip")):
        P.append(mb("qled", 222, 140 + k * 4, 224.5, 142 + k * 4, 0, 1.0, M, M[col], coll))

    # ---------------------------------------------------------- Socket AM5
    cu, cv = L.SOCKET_C
    sock = mb("socket", cu - 25, cv - 25, cu + 25, cv + 25, 0, 2.6, M, M["plastic"], coll, bevel=0.4)
    boolean_cut(sock, [mb("cut", cu - 21.2, cv - 21.2, cu + 21.2, cv + 21.2, -1, 5, M, None, coll)])
    P.append(sock)
    # ILM: marco de acero con ventana; presiona el faldón del IHS y deja salir la meseta
    ilm = mb("ilm", cu - 27, cv - 33, cu + 27, cv + 33, 2.6, 5.7, M, M["steel_bare"], coll, bevel=0.6)
    boolean_cut(ilm, [mb("cut", cu - 18, cv - 18, cu + 18, cv + 18, 0, 7, M, None, coll, bevel=2.0),
                      mb("cut", cu - 20.6, cv - 20.6, cu + 20.6, cv + 20.6, 1.0, 4.45, M, None, coll)])
    P.append(ilm)
    # palanca
    lever = [W(cu - 31, cv + 33, 3.8), W(cu - 31, cv - 30, 3.8), W(cu - 27, cv - 34, 3.8)]
    P.append(lib.poly_tube("lever", lever, 0.0009, M["steel_bare"], coll, bend_r=0.003))
    P.append(mb("lever_tab", cu - 33, cv + 31, cu - 29, cv + 38, 3.0, 5.0, M, M["steel_bare"], coll, bevel=0.6))
    P.append(mb("lever_hook", cu - 32.5, cv - 36, cu - 29, cv - 33, 0, 5.0, M, M["steel_bare"], coll, bevel=0.5))
    for su in (-1, 1):
        for sv in (-1, 1):
            P.append(mbcyl("ilm_screw", cu + su * 23, cv + sv * 29.5, 2.4, 5.7, 6.9, M["screw_silver"], coll, 16, 0.4))
    # orificios de montaje del disipador (estándar AM4/AM5: 54 x 90 mm)
    for su in (-1, 1):
        for sv in (-1, 1):
            P.append(mbcyl("cool_post", cu + su * 27, cv + sv * 45, 3.0, 0, 7.5, M["plastic"], coll, 16, 0.4))

    # ---------------------------------------------------------- DIMM
    for u in L.DIMM_U:
        a, b = L.DIMM_V
        hw = L.DIMM_W / 2
        body = mb("dimm", u - hw, a + 4, u + hw, b, 0, 7.5, M, M["plastic_dimm"], coll, bevel=0.4)
        boolean_cut(body, [mb("cut", u - 0.9, a + 5, u + 0.9, b - 1, 2.5, 9, M, None, coll)])
        P.append(body)
        P.append(mb("dimm_latch", u - hw - 0.4, a, u + hw + 0.4, a + 4.5, 0, 11.5, M, M["plastic_grey"], coll, bevel=0.6))
        P.append(mb("dimm_key", u - 0.9, a + 74, u + 0.9, a + 76, 2.5, 6.5, M, M["plastic_dimm"], coll))

    # ---------------------------------------------------------- PCIe
    def pcie(name, r, armored=True):
        u0, v0, u1, v1 = r
        s = [mb(name, u0, v0, u1, v1, 0, 11, M, M["connector"], coll, bevel=0.4)]
        boolean_cut(s[0], [mb("cut", u0 + 1.5, (v0 + v1) / 2 - 0.8, u1 - 1.5, (v0 + v1) / 2 + 0.8, 3, 12, M, None, coll),
                           mb("cut", u0 + 11, v0 - 1, u0 + 12.6, v1 + 1, 5, 12, M, None, coll)])
        if armored:
            arm = mb(name + "_armor", u0 - 0.6, v0 - 0.6, u1 + 0.6, v1 + 0.6, 2.0, 10.0, M, M["steel_bare"], coll, bevel=0.3)
            boolean_cut(arm, [mb("cut", u0 - 2, v0, u1 + 2, v1, 1, 12, M, None, coll)])
            s.append(arm)
        s.append(mb(name + "_latch", u1, v0 - 0.5, u1 + 7, v1 + 0.5, 0, 9, M, M["plastic_grey"], coll, bevel=0.6))
        return s
    P += pcie("pcie1", L.PCIE1, True)
    P += pcie("pcie2", L.PCIE2, True)
    a = L.PCIE_X1
    x1 = mb("pcie_x1", a[0], a[1], a[2], a[3], 0, 11, M, M["connector"], coll, bevel=0.4)
    boolean_cut(x1, [mb("cut", a[0] + 1.5, (a[1] + a[3]) / 2 - 0.8, a[2] - 1.5, (a[1] + a[3]) / 2 + 0.8, 3, 12, M, None, coll)])
    P.append(x1)

    # ---------------------------------------------------------- M.2 (conector y separador; el SSD y su disipador van aparte)
    a = L.M2_CONN
    P.append(mb("m2_conn", a[0], a[1], a[2], a[3], 0, 4.2, M, M["connector"], coll, bevel=0.3))
    P.append(mbcyl("m2_standoff", L.M2_SSD[2], (L.M2_SSD[1] + L.M2_SSD[3]) / 2, 2.4, 0, 2.8, M["tin"], coll, 12))
    # M.2_2 con disipador fijo
    a = L.M2_2_HS
    P.append(mb("m2b_hs", a[0], a[1], a[2], a[3], 0, 8, M, gm, coll, bevel=1.0))
    for k in range(7):
        P.append(mb("m2b_groove", a[0] + 8 + k * 11, a[1] + 2, a[0] + 9.2 + k * 11, a[3] - 2, 8, 8.4, M, dk, coll))

    # ---------------------------------------------------------- Chipset
    a = L.CHIPSET_HS
    P.append(mb("chipset_hs", a[0], a[1], a[2], a[3], 0, 9, M, gm, coll, bevel=1.5, seg=2))
    logo = lib.plane("chipset_logo", (a[3] - a[1] - 16) / 1000, (a[3] - a[1] - 16) / 1000,
                     W((a[0] + a[2]) / 2, (a[1] + a[3]) / 2, 9.05), "X-", M["chipset_logo"], coll)
    P.append(logo)
    P.append(mb("chipset_rgb", a[0] + 2, a[3] - 1.2, a[2] - 2, a[3] - 0.4, 2, 8, M, M["rgb"], coll))

    # ---------------------------------------------------------- SATA
    a = L.SATA
    for k in range(2):
        v = a[1] + 4 + k * 24
        for j in range(2):
            P.append(mb("sata", a[0], v, a[2], v + 9, j * 6, j * 6 + 5.5, M, M["connector"], coll, bevel=0.3))
            P.append(mb("sata_in", a[2] - 0.1, v + 1.5, a[2] + 0.2, v + 7.5, j * 6 + 1.5, j * 6 + 4, M, M["chip"], coll))
    # ---------------------------------------------------------- cabeceras inferiores y ventilador
    for k, u in enumerate((152, 168, 186, 208, 226)):
        P += header(f"hdr{k}", u, 297.5, 5 if k != 1 else 6, 2, M, coll, shroud=(k in (1, 2)))
    P += header("cpufan", L.CPU_FAN_HDR[0], L.CPU_FAN_HDR[1], 4, 1, M, coll, shroud=False)
    P += header("sysfan1", 2.0, 170.0, 4, 1, M, coll, shroud=False)
    P += header("argb1", 216.0, 4.0, 3, 1, M, coll, shroud=False)

    # ---------------------------------------------------------- Audio
    a = L.AUDIO
    P.append(mb("codec", 16, 270, 26, 280, 0, 1.4, M, M["chip"], coll, bevel=0.2))
    P.append(mb("codec_shield", 12, 266, 30, 284, 0, 2.2, M, M["tin"], coll, bevel=0.3))
    for i, (u, v) in enumerate(((8, 262), (8, 292), (36, 262), (36, 290), (22, 296))):
        P.append(mbcyl("audiocap", u, v, 3.0, 0, 9, M["gold"], coll, 18, 0.4))
        P.append(mbcyl("audiocap_t", u, v, 2.7, 9, 9.3, M["cap"], coll, 18))

    # ---------------------------------------------------------- Chips varios
    chips = [(55, 190, 14, 14, 1.6), (95, 188, 9, 9, 1.2), (78, 238, 6, 5, 1.4), (110, 228, 10, 10, 1.3),
             (182, 160, 7, 7, 1.2), (60, 116, 8, 8, 1.1), (20, 172, 12, 12, 1.4), (198, 264, 6, 9, 1.2)]
    for (u, v, w, h, t) in chips:
        P.append(mb("chip", u - w / 2, v - h / 2, u + w / 2, v + h / 2, 0, t, M, M["chip"], coll, bevel=0.2))
    # MOSFET/drivers del VRM bajo disipadores (asoman)
    P.append(mbcyl("cmos", L.CMOS[0], L.CMOS[1], 10, 0.6, 3.8, M["steel_bare"], coll, 40, 0.5))
    P.append(mb("cmos_holder", L.CMOS[0] - 11.5, L.CMOS[1] - 11.5, L.CMOS[0] + 11.5, L.CMOS[1] + 11.5, 0, 0.8, M, M["connector"], coll))
    # Botones traseros (BIOS flashback, clear CMOS)
    for k in range(2):
        P.append(mb("btn", 166 + k * 14, 250, 172 + k * 14, 254, 0, 3, M, M["plastic_grey"], coll, bevel=0.6))

    # ---------------------------------------------------------- Tornillos de montaje
    hidden = {(6.5, 10.0)}
    for (u, v) in L.HOLES:
        if (u, v) in hidden:
            continue
        P.append(mbcyl("screw", u, v, 3.0, 0, 1.8, M["screw"], coll, 20, 0.5))
        P.append(mb("screw_x", u - 1.5, v - 0.3, u + 1.5, v + 0.3, 1.7, 1.9, M, M["plastic"], coll))
        P.append(mb("screw_x", u - 0.3, v - 1.5, u + 0.3, v + 1.5, 1.7, 1.9, M, M["plastic"], coll))

    # ---------------------------------------------------------- Backplate del socket (cara trasera)
    P.append(mb("backplate", cu - 34, cv - 48, cu + 34, cv + 48, -L.MB_T - 3.0, -L.MB_T, M, M["alu_black"], coll, bevel=1.0))

    mbo = join(P, "Motherboard")
    set_origin(mbo, W(L.MB_W / 2, L.MB_H / 2, -L.MB_T))
    return mbo
