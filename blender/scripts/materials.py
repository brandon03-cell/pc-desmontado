"""Biblioteca de materiales PBR (compatibles con glTF)."""
from lib import mat


def build():
    M = {}
    # Caja: acero con pintura en polvo negra
    M["steel"] = mat("M_Steel_Powder", (0.018, 0.018, 0.02), 0.0, 0.55, normal_tex="powder_normal.png", normal_strength=0.25)
    M["steel_in"] = mat("M_Steel_Interior", (0.012, 0.012, 0.014), 0.0, 0.6, normal_tex="powder_normal.png", normal_strength=0.25)
    M["mesh"] = mat("M_Mesh_Hex", (0.02, 0.02, 0.022), 0.0, 0.5, alpha_clip_tex="hexmesh.png")
    M["glass"] = mat("M_Glass_Tempered", (0.05, 0.055, 0.06), 0.0, 0.02, alpha=0.16, ior=1.52, specular=0.6)
    M["frit"] = mat("M_Glass_Frit", (0.008, 0.008, 0.009), 0.0, 0.08, coat=1.0)
    M["rubber"] = mat("M_Rubber", (0.012, 0.012, 0.012), 0.0, 0.85)
    M["slot_cover"] = mat("M_Steel_Slot", (0.02, 0.02, 0.022), 0.2, 0.45)
    M["screw"] = mat("M_Screw_Black", (0.03, 0.03, 0.032), 0.8, 0.35)
    M["screw_silver"] = mat("M_Screw_Silver", (0.75, 0.75, 0.76), 1.0, 0.3)
    # Plásticos
    M["plastic"] = mat("M_Plastic_Black", (0.016, 0.016, 0.018), 0.0, 0.62)
    M["plastic_gloss"] = mat("M_Plastic_Black_Gloss", (0.012, 0.012, 0.014), 0.0, 0.18)
    M["plastic_grey"] = mat("M_Plastic_Grey", (0.11, 0.11, 0.115), 0.0, 0.5)
    M["plastic_dimm"] = mat("M_Plastic_DIMM", (0.035, 0.035, 0.04), 0.0, 0.45)
    M["fan_frame"] = mat("M_Fan_Frame", (0.02, 0.02, 0.022), 0.0, 0.5)
    M["fan_blade_rgb"] = mat("M_Fan_Blade_Frost", (0.8, 0.82, 0.86), 0.0, 0.42, emission=(0.35, 0.3, 0.9), emission_strength=0.35)
    M["fan_blade_black"] = mat("M_Fan_Blade_Black", (0.025, 0.025, 0.028), 0.0, 0.45)
    M["rgb"] = mat("M_RGB_Ring", (0.9, 0.9, 0.95), 0.0, 0.3, emission_tex="rgb_ring.png", emission_strength=6.0)
    M["rgb_white"] = mat("M_RGB_White", (0.9, 0.9, 0.95), 0.0, 0.3, emission=(0.75, 0.85, 1.0), emission_strength=4.0)
    # Metales
    M["alu"] = mat("M_Alu_Brushed", (0.9, 0.91, 0.92), 1.0, 0.3, mr_tex="brushed_mr.png", normal_tex="brushed_normal.png", normal_strength=0.35)
    M["alu_dark"] = mat("M_Alu_Gunmetal", (0.2, 0.205, 0.215), 1.0, 0.36, mr_tex="brushed_mr.png", normal_tex="brushed_normal.png", normal_strength=0.3)
    M["alu_black"] = mat("M_Alu_Black_Anod", (0.03, 0.03, 0.033), 1.0, 0.42)
    M["fins"] = mat("M_Alu_Fins", (0.88, 0.89, 0.9), 1.0, 0.26)
    M["copper"] = mat("M_Copper", (0.955, 0.638, 0.538), 1.0, 0.22)
    M["nickel"] = mat("M_Nickel", (0.82, 0.8, 0.76), 1.0, 0.18)
    M["gold"] = mat("M_Gold_Contacts", (1.0, 0.77, 0.34), 1.0, 0.22)
    M["tin"] = mat("M_Tin", (0.78, 0.78, 0.8), 1.0, 0.32)
    M["steel_bare"] = mat("M_Steel_Bare", (0.62, 0.62, 0.64), 1.0, 0.35)
    # Electrónica
    M["pcb_mb"] = mat("M_PCB_Motherboard", (1, 1, 1), 0.0, 0.45, albedo_tex="mb_albedo.png", mr_tex="mb_mr.png", normal_tex="mb_normal.png", normal_strength=0.6)
    M["pcb"] = mat("M_PCB_Black", (0.02, 0.022, 0.024), 0.0, 0.4)
    M["pcb_edge"] = mat("M_PCB_Edge", (0.16, 0.15, 0.1), 0.0, 0.6)
    M["chip"] = mat("M_Chip_Epoxy", (0.025, 0.025, 0.027), 0.0, 0.32)
    M["choke"] = mat("M_Choke", (0.06, 0.06, 0.065), 0.25, 0.55)
    M["cap"] = mat("M_Capacitor_Alu", (0.42, 0.43, 0.45), 1.0, 0.5)
    M["cap_sleeve"] = mat("M_Capacitor_Sleeve", (0.03, 0.03, 0.035), 0.0, 0.3)
    M["led_white"] = mat("M_LED_White", (0.9, 0.9, 0.9), 0.0, 0.3, emission=(0.8, 0.9, 1.0), emission_strength=3.0)
    M["ram_pcb"] = mat("M_PCB_Green", (0.03, 0.18, 0.08), 0.0, 0.35)
    # Etiquetas / decals
    M["ram_label"] = mat("M_Label_RAM", (1, 1, 1), 0.6, 0.38, albedo_tex="ram_label.png")
    M["ssd_label"] = mat("M_Label_SSD", (1, 1, 1), 0.0, 0.5, albedo_tex="ssd_label.png")
    M["psu_label"] = mat("M_Label_PSU", (1, 1, 1), 0.0, 0.55, albedo_tex="psu_label.png")
    M["ihs"] = mat("M_IHS", (1, 1, 1), 1.0, 0.25, albedo_tex="ihs_albedo.png", mr_tex="ihs_mr.png")
    M["backplate"] = mat("M_GPU_Backplate", (1, 1, 1), 1.0, 0.35, albedo_tex="gpu_backplate_albedo.png", mr_tex="gpu_backplate_mr.png")
    M["gpu_logo"] = mat("M_GPU_EdgeLogo", (0.02, 0.02, 0.02), 0.0, 0.3, emission_tex="gpu_edge_logo.png", emission_strength=3.0)
    M["chipset_logo"] = mat("M_Chipset_Logo", (1, 1, 1), 0.7, 0.35, albedo_tex="chipset_logo.png")
    M["paste"] = mat("M_ThermalPaste", (0.34, 0.35, 0.36), 0.35, 0.3)
    M["sleeve"] = mat("M_Cable_Sleeve", (0.018, 0.018, 0.02), 0.0, 0.55)
    M["connector"] = mat("M_Connector_Nylon", (0.02, 0.02, 0.022), 0.0, 0.5)
    return M
