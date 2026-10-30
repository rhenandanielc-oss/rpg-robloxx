"""FINALIZACAO + RIG + ANIMACOES de uma especie (a partir de <Esp>/<Esp>_refinado.blend).
1) Finalizacao: materiais por especie (padrao oficial 1 como base neutra), sombreamento por cor de vertice
   (contra-sombreamento e regioes como a juba), limite de 20.000 tris por objeto (Roblox MeshPart), nomes limpos.
2) Rig: esqueleto da familia (esqueletos.py), pesos por proximidade (1/d^4, ate 4 influencias) com regras por parte:
   partes rigidas (garra, osso, cristal, olho) presas 100% ao osso mais proximo; membranas so aos ossos da asa/nadadeira.
3) Animacoes procedurais por familia (acoes separadas em faixas NLA): pacote base, montaria, territorial, voo,
   nado e as 4 habilidades oficiais (so movimento, sem efeitos/dano).
4) Exporta GLB (todas as acoes) + salva <Esp>_final.blend.
Uso: blender -b --factory-startup -P pipeline_final.py -- <Especie>"""
import bpy, bmesh, sys, os, math, json
import numpy as np
from mathutils import Vector, Matrix, Quaternion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blockout_lib import RAIZ, material_papel
import esqueletos

ESP = sys.argv[sys.argv.index("--") + 1]
SUF = os.environ.get("CR_SUFIXO", "")                                  # "_v3": refinamento do Lobo Ancestral, sem sobrescrever a V2
LOBO = ESP in ("Lobo_Ancestral", "Lobo_Artico")
V3 = SUF in ("_v3", "_v4", "_v5") and LOBO                               # caminho exclusivo dos lobos; demais especies usam revest.py                                       # V3/V4: mesmo caminho do refinamento do Lobo
E = esqueletos.todos()[ESP]
FAM = E.familia

CORES = {   # padrao oficial 1 de cada forma como base neutra (RPG_02 / Catalogo)
    "Lobo_Ancestral": ("Cinza da Floresta", (0.20, 0.19, 0.165)), "Lobo_Artico": ("Branco Polar", (0.72, 0.72, 0.70)),
    "Cerbero_Sombrio": ("Negro Carbonizado", (0.045, 0.04, 0.04)), "Leao_Solar": ("Dourado Solar", (0.50, 0.33, 0.15)),
    "Urso_Silvestre": ("Castanho do Bosque", (0.17, 0.10, 0.055)), "Bufalo_Colossal": ("Castanho Profundo", (0.11, 0.07, 0.04)),
    "Crocodilo_Primordial": ("Verde Pantanal", (0.11, 0.12, 0.075)), "Basilisco": ("Verde Pantanoso", (0.13, 0.16, 0.085)),
    "Lagarto_Cristalino": ("Quartzo Claro", (0.33, 0.29, 0.23)), "Escorpiao_Colossal": ("Negro Obsidiana", (0.05, 0.045, 0.04)),
    "Serpente_Marinha": ("Azul Oceanico", (0.08, 0.17, 0.25)), "Leviata_Jovem": ("Azul Abissal", (0.06, 0.10, 0.16)),
    "Wyvern": ("Verde Musgo", (0.15, 0.18, 0.11)), "Dragao_das_Montanhas": ("Basalto Cinzento", (0.16, 0.155, 0.145)),
    "Dragao_Glacial": ("Branco Glacial", (0.60, 0.66, 0.72)), "Dragao_Sombrio": ("Negro Obsidiana", (0.04, 0.035, 0.045)),
}
# padroes do Bufalo: o catalogo nao lista nomes no script local -> base neutra provisoria
TRIS_MAX = 19500
FPS = 30


# ---------------------------------------------------------------- 1) FINALIZACAO
def finalizar():
    bpy.ops.wm.open_mainfile(filepath=os.path.join(RAIZ, ESP, ESP + "_refinado" + SUF + ".blend"))
    bpy.context.preferences.filepaths.save_version = 0
    col = bpy.data.collections[ESP]
    for o in list(bpy.data.objects):
        if o.name.startswith("REF_"):
            bpy.data.objects.remove(o, do_unlink=True)
    nome_pad, base = CORES[ESP]
    if V3: base = ((0.6, 0.6, 0.59) if ESP == "Lobo_Artico" else (0.13, 0.13, 0.125)) if SUF == "_v5" else (0.19, 0.165, 0.12)   # V5: Cinza da Floresta (padrao oficial 1)   # V5: tons das amostras do painel oficial                                   # Cinza da Floresta puxado ao castanho-oliva do painel oficial
    obs = [o for o in col.objects if o.type == "MESH"]
    for o in obs:
        papel = o.get("papel_material") or ("membrana" if ("Asa" in o.name or "Nadadeira" in o.name) else "osso")
        if papel == "pelagem":                                     # tufos: material proprio (atlas) ja pronto no modelo
            continue
        if o.name.endswith("_Corpo_Blockout"):
            papel = o.get("papel_material", "pelo")
        if papel == "membrana" and len(o.data.polygons) < 2000:   # membrana densa para deformar com os dedos
            sd = o.modifiers.new("Sub", "SUBSURF"); sd.subdivision_type = "SIMPLE"; sd.levels = 2
            dg = bpy.context.evaluated_depsgraph_get()
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); o.data = me
        n = sum(len(p.vertices) - 2 for p in o.data.polygons)
        if n > TRIS_MAX:                                           # orcamento Roblox por MeshPart
            d = o.modifiers.new("Dec", "DECIMATE"); d.ratio = TRIS_MAX / n
            bpy.context.view_layer.objects.active = o
            dg = bpy.context.evaluated_depsgraph_get()
            me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); o.modifiers.clear(); o.data = me
        o.name = o.name.replace("_Blockout", "")
        cor = None
        if o.name.endswith("_Corpo"):
            cor = base + (1,)
        elif papel == "osso" and SUF == "_v5" and ESP in CHIFRES:
            cor = CHIFRES[ESP]                                            # chifres/espinhos na cor das pranchas
        elif papel == "membrana":
            cor = tuple(min(1, c * 1.25 + 0.03) for c in base) + (1,)
        m = material_papel(o, papel, cor)
        m.name = "MAT_%s_%s" % (ESP, papel.capitalize())
        if o.name.endswith("_Corpo"):
            sombrear(o, m)
            texturizar(o, m, papel, 1024)
            if SUF == "_v5" and (LOBO or o.get("fios_assados")):
                assar_fios(o, m)
        elif papel == "membrana":
            texturizar(o, m, papel, 512)
        elif papel == "olho":
            b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            b.inputs["Base Color"].default_value = ((0.24, 0.19, 0.03) if SUF == "_v5" and ESP == "Lobo_Ancestral" else (0.3, 0.55, 0.75) if ESP == "Lobo_Artico" else OLHOS.get(ESP, (0.35, 0.2, 0.05))) + (1,)
            b.inputs["Roughness"].default_value = 0.08
    return col


CHIFRES = {"Bufalo_Colossal": (0.13, 0.11, 0.085, 1), "Dragao_das_Montanhas": (0.07, 0.06, 0.05, 1), "Dragao_Sombrio": (0.04, 0.03, 0.05, 1),
           "Dragao_Glacial": (0.62, 0.72, 0.82, 1), "Wyvern": (0.2, 0.18, 0.12, 1), "Basilisco": (0.1, 0.1, 0.07, 1), "Cerbero_Sombrio": (0.06, 0.05, 0.05, 1),
           "Escorpiao_Colossal": (0.05, 0.04, 0.03, 1), "Crocodilo_Primordial": (0.75, 0.7, 0.6, 1), "Leviata_Jovem": (0.12, 0.14, 0.16, 1), "Serpente_Marinha": (0.6, 0.65, 0.6, 1)}
OLHOS = {"Lobo_Artico": (0.25, 0.45, 0.6), "Dragao_Glacial": (0.35, 0.55, 0.7), "Serpente_Marinha": (0.45, 0.4, 0.12),
         "Leviata_Jovem": (0.4, 0.35, 0.1), "Cerbero_Sombrio": (0.35, 0.08, 0.04), "Dragao_Sombrio": (0.3, 0.1, 0.25)}


def texturizar(o, m, papel, res):
    """Assa a superficie procedural da especie em textura (cor + normal) e troca o material por imagens simples
    (Base Color + Normal Map), o formato que o Import 3D do Roblox converte em SurfaceAppearance."""
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.004)
    bpy.ops.object.mode_set(mode="OBJECT")
    nt = m.node_tree; N, L = nt.nodes, nt.links
    bsdf = next(n for n in N if n.type == "BSDF_PRINCIPLED")
    tc = N.new("ShaderNodeTexCoord")
    cor_in = bsdf.inputs["Base Color"].links[0].from_socket if bsdf.inputs["Base Color"].is_linked else None
    base_rgb = bsdf.inputs["Base Color"].default_value[:]
    var = N.new("ShaderNodeMix"); var.data_type = "RGBA"; var.blend_type = "MULTIPLY"; var.inputs[0].default_value = 1.0
    if cor_in: L.new(cor_in, var.inputs[6])
    else: var.inputs[6].default_value = base_rgb
    ramp = N.new("ShaderNodeValToRGB")
    bump = N.new("ShaderNodeBump")
    if papel == "pelo":                         # mechas: ondas alongadas e distorcidas (direcao aparente) + grao fino
        w = N.new("ShaderNodeTexWave"); w.wave_type = "BANDS"; w.bands_direction = "Z"
        w.inputs["Scale"].default_value = 6.0; w.inputs["Distortion"].default_value = 14.0; w.inputs["Detail"].default_value = 8; w.inputs["Detail Scale"].default_value = 2.5
        L.new(tc.outputs["Object"], w.inputs["Vector"])
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 14; nz.inputs["Detail"].default_value = 8
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        mx = N.new("ShaderNodeMath"); mx.operation = "MULTIPLY_ADD"; L.new(w.outputs["Fac"], mx.inputs[0]); mx.inputs[1].default_value = 0.6
        L.new(nz.outputs["Fac"], mx.inputs[2])
        L.new(mx.outputs[0], ramp.inputs["Fac"]); L.new(mx.outputs[0], bump.inputs["Height"])
        ramp.color_ramp.elements[0].color = (0.84, 0.83, 0.82, 1); ramp.color_ramp.elements[1].color = (1.08, 1.07, 1.05, 1)
        bump.inputs["Strength"].default_value = 0.18; bump.inputs["Distance"].default_value = 0.02
        rough = 0.9
    elif papel in ("escama", "quitina"):        # escamas: celulas de Voronoi com bordas em sulco + variacao sutil
        v = N.new("ShaderNodeTexVoronoi"); v.feature = "DISTANCE_TO_EDGE"
        v.inputs["Scale"].default_value = 2.6 if papel == "escama" else 1.2
        L.new(tc.outputs["Object"], v.inputs["Vector"])
        v2 = N.new("ShaderNodeTexVoronoi"); v2.inputs["Scale"].default_value = 2.6; L.new(tc.outputs["Object"], v2.inputs["Vector"])
        L.new(v2.outputs["Distance"], ramp.inputs["Fac"])
        ramp.color_ramp.elements[0].color = (0.85, 0.85, 0.85, 1); ramp.color_ramp.elements[1].color = (1.1, 1.08, 1.05, 1)
        sm = N.new("ShaderNodeMath"); sm.operation = "SMOOTH_MIN"; L.new(v.outputs["Distance"], sm.inputs[0]); sm.inputs[1].default_value = 0.08; sm.inputs[2].default_value = 0.05
        L.new(sm.outputs[0], bump.inputs["Height"])
        bump.inputs["Strength"].default_value = 0.6; bump.inputs["Distance"].default_value = 0.08
        rough = 0.55 if papel == "escama" else 0.35
    else:                                       # membrana: couro com veias suaves
        nz = N.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3; nz.inputs["Detail"].default_value = 10
        L.new(tc.outputs["Object"], nz.inputs["Vector"])
        L.new(nz.outputs["Fac"], ramp.inputs["Fac"]); L.new(nz.outputs["Fac"], bump.inputs["Height"])
        ramp.color_ramp.elements[0].color = (0.8, 0.78, 0.76, 1); ramp.color_ramp.elements[1].color = (1.1, 1.05, 1.0, 1)
        bump.inputs["Strength"].default_value = 0.3
        rough = 0.65
    L.new(ramp.outputs["Color"], var.inputs[7])
    L.new(var.outputs[2], bsdf.inputs["Base Color"]); L.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough
    sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.samples = 4
    def assar(tipo, cs):
        img = bpy.data.images.new("%s_%s" % (o.name, tipo), res, res, alpha=False); img.colorspace_settings.name = cs
        tn = N.new("ShaderNodeTexImage"); tn.image = img
        for n in N: n.select = False
        tn.select = True; N.active = tn
        if tipo == "Cor": bpy.ops.object.bake(type="DIFFUSE", pass_filter={"COLOR"}, margin=4)
        else: bpy.ops.object.bake(type="NORMAL", margin=4)
        img.pack()
        return tn
    tcor = assar("Cor", "sRGB"); tnor = assar("Normal", "Non-Color")
    for n in list(N):                            # material final simples: imagens -> Principled
        if n not in (tcor, tnor, bsdf) and n.type != "OUTPUT_MATERIAL": N.remove(n)
    nm = N.new("ShaderNodeNormalMap")
    L.new(tcor.outputs["Color"], bsdf.inputs["Base Color"]); L.new(tnor.outputs["Color"], nm.inputs["Color"]); L.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    o.data.color_attributes.clear() if hasattr(o.data.color_attributes, "clear") else None


def mascara_lobo(p, k):
    if SUF in ("_v4", "_v5"):                                     # V5 usa o mesmo referencial de cabeca (DH) da V4
        c = mascara_lobo_v4(p, k)
        if SUF == "_v5" and not c[1] > c[0] * 1.2:                # V5 cinzento: tira o tom creme/castanho (musgo fica verde)
            g = sum(c) / 3; c = [g + (x - g) * 0.15 for x in c]
        return c
    return mascara_lobo_v3(p, k)


def mascara_lobo_v4(p, k):
    """V4: cabeca avaliada no referencial da V3 (lobo_v4.local_cabeca); creme mais marcado; ponta da cauda escura."""
    import lobo_v4, lobo_v5
    x, y, z = p
    q = (lobo_v5 if SUF == "_v5" else lobo_v4).local_cabeca(p)
    if q is not None:
        c = [k, k, k]
        if q.y < -3.3 and q.z < 8.12 and abs(q.x) > 0.1: c = [k * 2.0, k * 1.85, k * 1.55]      # bochecha/labio claros
        if q.y < -3.9 and q.z > 8.25 and abs(q.x) < 0.22: c = [k * 0.75, k * 0.7, k * 0.66]     # cana nasal
        if q.y < -4.88 and q.z > 7.95: c = [0.1, 0.09, 0.085]                                  # trufa
        if q.y < -3.85 and abs(q.z - 7.9) < 0.045 and abs(q.x) > 0.05: c = [0.16, 0.14, 0.13]  # linha dos labios
        for s in (1, -1):
            dd = (q - Vector((s * ((0.32 if ESP == "Lobo_Artico" else 0.29) if SUF == "_v5" else 0.245), -4.19, 8.42))).length
            if dd < 0.13: c = [k * 0.3, k * 0.28, k * 0.26]                                    # contorno dos olhos
            elif dd < 0.2 and q.z < 8.42: c = [k * 1.7, k * 1.6, k * 1.4]                      # mancha clara sob o olho
        return c
    c = [k, k, k]
    if (z < 4.3 and y < 0.9) or (-3.6 < y < -2.0 and z < 6.6 and abs(x) < 0.4):
        c = [k * 1.75, k * 1.62, k * 1.38]                         # garganta, peito, ventre
    if z > 5.45 and -2.2 < y < 2.4:
        c = [k * 0.7, k * 0.68, k * 0.64]                          # sela
        mo = math.sin(3.1 * x + 1.7) * math.sin(2.3 * y + 0.4) * math.sin(2.9 * z + 0.5)
        if ESP == "Lobo_Ancestral" and z > 5.75 and mo > (0.1 if SUF == "_v5" else 0.3): c = [k * 0.62, k * 0.95, k * 0.32] if SUF == "_v5" else [k * 0.58, k * 0.72, k * 0.4]    # musgo
    if y > 3.9 and z < 2.3: c = [k * 0.45, k * 0.42, k * 0.4]       # ponta da cauda
    if z < 1.3: c = [k * 0.75, k * 0.72, k * 0.68]                 # patas
    return c


def mascara_lobo_v3(p, k):
    """Lobo Ancestral V3: sela escura com manchas de musgo, mascara clara (garganta, peito, ventre, bochechas, labio
    superior), trufa e labios negros, contorno escuro dos olhos, dorso das orelhas e frente das patas mais escuros."""
    x, y, z = p
    c = [k, k, k]
    if (z < 4.3 and y < 0.9) or (y < -3.25 and 7.6 < z < 8.15 and abs(x) > 0.12) or (-3.4 < y < -2.0 and z < 6.8 and abs(x) < 0.4):
        c = [k * 1.45, k * 1.38, k * 1.22]                         # creme
    if z > 5.45 and -2.2 < y < 2.4:
        c = [k * 0.7, k * 0.68, k * 0.64]                          # sela
        mo = math.sin(3.1 * x + 1.7) * math.sin(2.3 * y + 0.4) * math.sin(2.9 * z + 0.5)
        if z > 5.75 and mo > 0.25: c = [k * 0.55, k * 0.72, k * 0.36]   # musgo
    if y < -4.88 and z > 7.92: c = [0.12, 0.11, 0.1]                # trufa
    if y < -3.8 and abs(z - 7.9) < 0.05 and abs(x) > 0.06: c = [0.2, 0.18, 0.16]   # linha dos labios
    for s in (1, -1):
        if (Vector(p) - Vector((s * 0.255, -4.2, 8.43))).length < 0.13: c = [k * 0.35, k * 0.32, k * 0.3]
    if y < -3.9 and z > 8.3 and abs(x) < 0.25: c = [k * 0.8, k * 0.75, k * 0.7]   # cana nasal
    if z < 1.3: c = [k * 0.75, k * 0.72, k * 0.68]                 # patas
    return c


def assar_fios(o, m):
    """V5: assa no corpo (selected-to-active) uma malha de alta com ~26 mil fios finos deitados no sentido do pelo:
    o normal map passa a ter o relevo das mechas e a oclusao escurece os sulcos na cor. Tudo vira imagem (GLB)."""
    import lobo_v5, revest
    hp = lobo_v5.fios_alta(o) if LOBO else revest.fios_alta(o, ESP)
    nt = m.node_tree; N = nt.nodes
    tnor = next(n for n in N if n.type == "TEX_IMAGE" and n.image and n.image.name.endswith("_Normal"))
    tcor = next(n for n in N if n.type == "TEX_IMAGE" and n.image and n.image.name.endswith("_Cor"))
    sc = bpy.context.scene; sc.render.engine = "CYCLES"; bk = sc.render.bake
    bk.use_selected_to_active = True; bk.cage_extrusion = 0.12; bk.max_ray_distance = 0.3; bk.margin = 4
    bpy.ops.object.select_all(action="DESELECT"); hp.select_set(True); o.select_set(True); bpy.context.view_layer.objects.active = o
    def assar(tipo, cs, amostras):
        sc.cycles.samples = amostras
        img = bpy.data.images.new("%s_Fios%s" % (o.name, tipo), 1024, 1024, alpha=False); img.colorspace_settings.name = cs
        tn = N.new("ShaderNodeTexImage"); tn.image = img
        for n in N: n.select = False
        tn.select = True; N.active = tn
        bpy.ops.object.bake(type=tipo)
        N.remove(tn)
        return img
    nimg = assar("NORMAL", "Non-Color", 4)
    ao = assar("AO", "Non-Color", 24)
    c = np.array(tcor.image.pixels[:]).reshape(-1, 4); a = np.array(ao.pixels[:]).reshape(-1, 4)[:, :1]
    c[:, :3] *= 0.45 + 0.55 * a
    tcor.image.pixels.foreach_set(c.ravel().astype(np.float32)); tcor.image.pack()
    velho = tnor.image; tnor.image = nimg; nimg.name = velho.name; bpy.data.images.remove(velho); nimg.pack()
    bpy.data.images.remove(ao)
    bk.use_selected_to_active = False
    bpy.data.objects.remove(hp, do_unlink=True)


def sombrear(o, m):
    """Cor de vertice: contra-sombreamento (dorso mais escuro, ventre mais claro) + regioes da especie."""
    me = o.data
    att = me.color_attributes.new("Sombreamento", "FLOAT_COLOR", "POINT")
    zs = [v.co.z for v in me.vertices]; z0, z1 = min(zs), max(zs)
    for v in me.vertices:
        h = (v.co.z - z0) / max(1e-6, z1 - z0)
        k = 1.12 - 0.3 * h + 0.12 * max(0, -v.normal.z)
        c = [k, k, k]
        p = v.co
        if ESP == "Leao_Solar" and p.y < -2.0 and (p.z > 7.8 or (p.y < -6 and p.z > 2.5)) and abs(p.y + 12.0) + abs(p.z - 11.5) > 1.6:
            c = [k * 0.82, k * 0.55, k * 0.38]                  # juba castanho-avermelhada
        if V3:
            c = mascara_lobo(p, k)
        elif ESP in ("Lobo_Ancestral", "Lobo_Artico") and p.z > 5.2 * (1.0 if ESP == "Lobo_Ancestral" else 1.015):
            c = [k * 0.85, k * 0.85, k * 0.85]                  # sela dorsal mais escura
        if ESP == "Bufalo_Colossal" and p.y < 2.5 and p.z > 6:
            c = [k * 0.75, k * 0.62, k * 0.5]                   # capa de pelo
        att.data[v.index].color = (c[0], c[1], c[2], 1.0)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    ca = nt.nodes.new("ShaderNodeVertexColor"); ca.layer_name = "Sombreamento"
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 1.0
    mix.inputs[6].default_value = bsdf.inputs["Base Color"].default_value
    nt.links.new(ca.outputs["Color"], mix.inputs[7]); nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])


# ---------------------------------------------------------------- 2) RIG
def montar_rig(col):
    arm_d = bpy.data.armatures.new(ESP + "_Esqueleto")
    arm = bpy.data.objects.new(ESP + "_Rig", arm_d); col.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    for o in bpy.context.view_layer.objects: o.select_set(False)
    arm.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for nome, a, b, pai in E.ossos:
        eb = arm_d.edit_bones.new(nome); eb.head = Vector(a); eb.tail = Vector(b)
        if (eb.tail - eb.head).length < 1e-3: eb.tail = eb.head + Vector((0, 0, 0.3))
        if pai: eb.parent = arm_d.edit_bones[pai]
        eb.use_deform = nome != "Raiz"
    bpy.ops.object.mode_set(mode="OBJECT")
    segs = {b.name: (np.array(b.head_local), np.array(b.tail_local)) for b in arm_d.bones if b.use_deform}
    for o in sorted([o for o in col.objects if o.type == "MESH"], key=lambda o: 0 if o.name.endswith("_Corpo") else 1):
        pesar(o, arm, segs)
    return arm


def dist_segs(P, segs, nomes):
    D = np.empty((len(P), len(nomes)))
    for j, n in enumerate(nomes):
        a, b = segs[n]; ab = b - a
        t = np.clip(((P - a) @ ab) / max(1e-9, ab @ ab), 0, 1)
        D[:, j] = np.linalg.norm(P - (a + t[:, None] * ab), axis=1)
    return D


def pesar_pelagem(o, arm):
    """Tufos de pelo seguem a pele: cada mecha (ilha) copia os pesos do vertice do corpo mais proximo da sua raiz."""
    from mathutils.kdtree import KDTree
    corpo = next(c for c in arm.children if c.name.endswith("_Corpo"))
    kd = KDTree(len(corpo.data.vertices))
    for v in corpo.data.vertices: kd.insert(corpo.matrix_world @ v.co, v.index)
    kd.balance()
    nomes = {g.index: g.name for g in corpo.vertex_groups}
    o.vertex_groups.clear(); vg = {}
    pelo = [(b.name, arm.matrix_world @ b.head_local) for b in arm.data.bones if b.name.startswith("Pelo_")]
    bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    visto = set()
    for v0 in bm.verts:
        if v0.index in visto: continue
        ilha, pilha = [], [v0]; visto.add(v0.index)
        while pilha:
            v = pilha.pop(); ilha.append(v)
            for e in v.link_edges:
                w = e.other_vert(v)
                if w.index not in visto: visto.add(w.index); pilha.append(w)
        raiz = min(ilha, key=lambda v: kd.find(o.matrix_world @ v.co)[2])
        pr = o.matrix_world @ raiz.co
        _, idx, _ = kd.find(pr)
        sec = min(pelo, key=lambda b: (b[1] - pr).length) if pelo else None
        if sec and (sec[1] - pr).length > 1.0: sec = None
        ext = max((v.co - raiz.co).length for v in ilha) or 1.0
        for v in ilha:                                             # ponta da mecha segue o osso de pelo; raiz segue a pele
            s = 0.75 * (v.co - raiz.co).length / ext if sec else 0.0
            for g in corpo.data.vertices[idx].groups:
                n = nomes[g.group]
                if n not in vg: vg[n] = o.vertex_groups.new(name=n)
                vg[n].add([v.index], g.weight * (1 - s), "REPLACE")
            if s > 0:
                if sec[0] not in vg: vg[sec[0]] = o.vertex_groups.new(name=sec[0])
                vg[sec[0]].add([v.index], s, "REPLACE")
    bm.free()
    o.parent = arm
    m = o.modifiers.new("Armature", "ARMATURE"); m.object = arm


def pesar(o, arm, segs):
    if "Pelagem" in o.name:
        return pesar_pelagem(o, arm)
    segs = {n: s for n, s in segs.items() if not n.startswith("Pelo_")}   # ossos de pelagem nao deformam o corpo
    nomes = list(segs)
    membrana = "Asa" in o.name or "Nadadeira" in o.name
    rigido = not (o.name.endswith("_Corpo") or membrana)
    if membrana:
        cand = [n for n in nomes if n.startswith(("Asa", "Dedo", "Coluna", "PernaT", "Nad", "Cauda", "Cabeca"))] or nomes
    elif o.name.endswith("_Corpo"):
        cand = nomes                                                    # dedos das asas tambem estao fundidos ao corpo
    else:
        cand = nomes
    P = np.array([o.matrix_world @ v.co for v in o.data.vertices])
    D = dist_segs(P, segs, cand)
    o.vertex_groups.clear()
    vg = {n: o.vertex_groups.new(name=n) for n in cand}
    if rigido:                                                      # cada ilha (garra, dente, cristal) rigida no osso mais proximo
        bm = bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
        visto = np.zeros(len(P), bool)
        for v0 in range(len(P)):
            if visto[v0]: continue
            ilha, pilha = [], [bm.verts[v0]]; visto[v0] = True
            while pilha:
                v = pilha.pop(); ilha.append(v.index)
                for e in v.link_edges:
                    w = e.other_vert(v)
                    if not visto[w.index]: visto[w.index] = True; pilha.append(w)
            c = P[ilha].mean(axis=0, keepdims=True)
            j = int(np.argmin(dist_segs(c, segs, cand)[0]))
            vg[cand[j]].add(ilha, 1.0, "REPLACE")
        bm.free()
    else:
        W = 1.0 / (D ** 6 + 1e-4)
        for j, n in enumerate(cand):                                # mandibula so move o que esta ABAIXO da linha da boca
            if n.startswith("Mandibula"):
                a, b = segs[n]
                t = np.clip(((P - a) @ (b - a)) / max(1e-9, (b - a) @ (b - a)), 0, 1)
                zl = a[2] + t * (b[2] - a[2]) + 0.12 * np.linalg.norm(b - a) * 0.25
                W[P[:, 2] > zl, j] = 0.0
            if n.startswith("Cabeca"):
                cab = n; mand = "Mandibula" + n[len("Cabeca"):]
                if mand in segs:
                    a, b = segs[mand]
                    t = np.clip(((P - a) @ (b - a)) / max(1e-9, (b - a) @ (b - a)), 0, 1)
                    zl = a[2] + t * (b[2] - a[2]) - 0.05 * np.linalg.norm(b - a)
                    perto = np.linalg.norm(P - (a + t[:, None] * (b - a)), axis=1) < 0.5 * np.linalg.norm(b - a)
                    W[(P[:, 2] < zl) & perto, j] *= 0.05
        # regioes: cada cadeia de membro/cauda/cabeca e uma regiao; o vertice so recebe ossos da propria regiao,
        # do tronco e do primeiro osso das regioes vizinhas (sem rasgar barriga/virilha)
        def cadeia_de(n):
            for k, pre in enumerate(("PernaDE", "PernaDD", "PernaTE", "PernaTD", "PincaE", "PincaD", "NadDE", "NadDD", "NadTE", "NadTD")):
                if n.startswith(pre): return pre
            if n.startswith(("Pata", "Asa", "Dedo")): return n.split("_")[0][:6] + n.split("_")[0][-1]
            if n.startswith("Cauda") or n == "Ferrao": return "Cauda"
            if n.startswith(("Pescoco", "Cabeca", "Mandibula")):
                return "Cab" + (n[-2:] if n[-2] == "_" else "")
            return "Tronco"
        ch = [cadeia_de(n) for n in cand]
        jmin = np.argmin(D, axis=1)
        reg = []
        for i in range(len(P)):
            j = jmin[i]; r = ch[j]
            hx = segs[cand[j]][0][0]
            if r not in ("Tronco", "Cauda") and not r.startswith("Cab") and abs(hx) > 0.05 and P[i, 0] * np.sign(hx) < 0.4 * abs(hx):
                r = "Tronco"                                            # linha media (barriga, virilha, peito) e do tronco
            reg.append(r)
        primeiro = {}
        for j, n in enumerate(cand):
            primeiro.setdefault(ch[j], j)
        mask = np.zeros_like(W, dtype=bool)
        for i in range(len(P)):
            r = reg[i]
            for j in range(len(cand)):
                if ch[j] == r or ch[j] == "Tronco" or (r == "Tronco" and primeiro[ch[j]] == j):
                    mask[i, j] = True
        ed = np.array([e.vertices[:] for e in o.data.edges])          # suavizacao dos pesos pela malha (transicoes graduais)
        for _ in range(3):                                             # fronteiras entre regioes: faixa de transicao
            m2 = mask.copy()
            np.logical_or.at(m2, ed[:, 0], mask[ed[:, 1]]); np.logical_or.at(m2, ed[:, 1], mask[ed[:, 0]])
            mask = m2
        W = W * mask
        W[W.sum(axis=1) == 0, :] = 1e-6
        W = W / W.sum(axis=1, keepdims=True)
        grau = np.bincount(ed.ravel(), minlength=len(P)).astype(float)[:, None] + 1e-9
        for _ in range(8 if o.name.endswith("_Corpo") else 4):
            S_ = np.zeros_like(W)
            np.add.at(S_, ed[:, 0], W[ed[:, 1]]); np.add.at(S_, ed[:, 1], W[ed[:, 0]])
            W = (0.5 * W + 0.5 * S_ / grau) * mask
        W[W.sum(axis=1) == 0, :] = 1e-6
        W = W / W.sum(axis=1, keepdims=True)
        idx = np.argsort(-W, axis=1)[:, :4]
        for i in range(len(P)):
            w = W[i, idx[i]]; w = w / w.sum()
            for jj, ww in zip(idx[i], w):
                if ww > 0.02: vg[cand[jj]].add([i], float(ww), "REPLACE")
    o.parent = arm
    m = o.modifiers.new("Armature", "ARMATURE"); m.object = arm


# ---------------------------------------------------------------- 3) ANIMACOES
def R(eixo, g):
    return Quaternion(Vector(eixo), math.radians(g))


X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)


class Pose(dict):
    def rot(self, osso, eixo, g):
        if osso and abs(g) > 1e-4:
            self.setdefault(osso, [Quaternion(), None])[0] = R(eixo, g) @ self.get(osso, [Quaternion(), None])[0]
    def loc(self, v):
        self.setdefault("Raiz", [Quaternion(), None])[1] = Vector(v)


S = lambda x: math.sin(2 * math.pi * x)
C = lambda x: math.cos(2 * math.pi * x)
def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def pulso(t, a, b): return math.sin(math.pi * max(0.0, min(1.0, (t - a) / max(1e-6, b - a))))

# parametros de carater por especie (escala do movimento; os painels/RPG_02 definem a atitude)
CAR = {
    "Lobo_Ancestral": dict(amp=1.0, peso=0.7, cab=1.0), "Lobo_Artico": dict(amp=0.9, peso=1.0, cab=0.9),
    "Cerbero_Sombrio": dict(amp=0.85, peso=1.3, cab=1.2), "Leao_Solar": dict(amp=0.9, peso=1.0, cab=0.7),
    "Urso_Silvestre": dict(amp=0.7, peso=1.6, cab=0.8), "Bufalo_Colossal": dict(amp=0.6, peso=1.9, cab=0.6),
    "Crocodilo_Primordial": dict(amp=0.6, peso=1.5, cab=0.5), "Basilisco": dict(amp=0.7, peso=1.3, cab=0.8),
    "Lagarto_Cristalino": dict(amp=0.7, peso=1.2, cab=0.6), "Escorpiao_Colossal": dict(amp=1.0, peso=1.0, cab=1.0),
    "Serpente_Marinha": dict(amp=1.0, peso=0.8, cab=1.0), "Leviata_Jovem": dict(amp=0.6, peso=2.0, cab=0.6),
    "Wyvern": dict(amp=1.1, peso=0.6, cab=1.2), "Dragao_das_Montanhas": dict(amp=0.75, peso=1.6, cab=0.8),
    "Dragao_Glacial": dict(amp=0.8, peso=1.3, cab=0.7), "Dragao_Sombrio": dict(amp=0.85, peso=1.5, cab=1.1),
}[ESP]
H = max([b[2] for n, a, b, p in E.ossos if n.startswith(("Coluna", "Corpo"))] or [3.0])   # altura do dorso (escala dos deslocamentos)
REPTIL = FAM in ("reptil",)
QUAD = FAM in ("canideo", "felino", "plantigrado", "ungulado", "reptil", "dragao")


def respirar(p, t, k=1.0):
    for i, n in enumerate(E.g["coluna"]):
        p.rot(n, X, -0.8 * k * S(t))
    for pc, cab, mand in E.g["cabecas"]:
        if pc: p.rot(pc[0], X, 1.2 * k * S(t + 0.2))


def cauda(p, t, amp=8, lat=True, fase=0.12, levantar=0.0):
    for i, n in enumerate(E.g["cauda"]):
        p.rot(n, Z if lat else X, amp * S(t - fase * i))
        if levantar: p.rot(n, X, -levantar * (1 - i / max(1, len(E.g["cauda"]))))


def marcha(p, t, fases, amp, flex, bob, yaw_col=0.0):
    a = amp * CAR["amp"]
    for m in E.g["membros"]:
        chave = ("F" if m["frente"] else "T") + ("E" if m["lado"] > 0 else "D")
        f = t - fases[chave]
        osso = m["ossos"]
        sw = S(f)
        if REPTIL or FAM == "artropode":
            p.rot(osso[0], Z, -m["lado"] * a * 0.9 * sw)              # remada lateral (membros espalhados)
            p.rot(osso[0], Y, -m["lado"] * flex * 0.6 * max(0, S(f + 0.25)))
        elif V3 and FAM == "canideo" and m["frente"]:                 # protracao no ombro (umero), escapula acompanha pouco
            p.rot(osso[0], X, -0.3 * a * sw); p.rot(osso[1], X, -0.7 * a * sw)
        else:
            p.rot(osso[0], X, -a * sw)
        lift = max(0.0, S(f + 0.25))
        if len(osso) > 2:
            sgn = 1 if m["frente"] else -1
            p.rot(osso[-2] if len(osso) > 3 else osso[1], X, sgn * flex * lift)
            p.rot(osso[-1], X, -sgn * 0.6 * flex * lift)
    p.loc((0, 0, bob * H * (0.5 - 0.5 * C(2 * t)) / CAR["peso"]))
    if yaw_col:
        for i, n in enumerate(E.g["coluna"]):
            p.rot(n, Z, yaw_col * S(t + 0.25 - 0.15 * i))
    for pc, cab, mand in E.g["cabecas"]:
        if pc: p.rot(pc[0], X, 2.0 * CAR["cab"] * S(2 * t + 0.1))


FASES = {"andar": {"TE": 0.0, "FE": 0.25, "TD": 0.5, "FD": 0.75}, "trote": {"FE": 0.0, "TD": 0.0, "FD": 0.5, "TE": 0.5},
         "galope": {"TD": 0.0, "TE": 0.1, "FE": 0.5, "FD": 0.6}, "bipede": {"TE": 0.0, "TD": 0.5, "FE": 0, "FD": 0}}


def asas_dobradas(p, k=1.0):
    for a in E.g["asas"]:
        s = a["lado"]; b = a["braco"]
        p.rot(b[0], Y, s * 40 * k); p.rot(b[0], Z, s * 45 * k)
        p.rot(b[1], Z, s * 55 * k); p.rot(b[1], Y, -s * 25 * k)
        for d in a["dedos"]:
            p.rot(d[0], Z, s * 60 * k)


def batida(p, t, amp=38, dobrar=0.0):
    for a in E.g["asas"]:
        s = a["lado"]; b = a["braco"]
        p.rot(b[0], Y, s * (amp * S(t) - 5))
        p.rot(b[1], Y, s * 0.5 * amp * S(t - 0.08))
        for d in a["dedos"]:
            p.rot(d[0], Y, s * 0.4 * amp * S(t - 0.16)); p.rot(d[0], Z, s * dobrar)


def pernas_recolhidas(p, k=1.0):
    for m in E.g["membros"]:
        o = m["ossos"]
        p.rot(o[0], X, (35 if not m["frente"] else 25) * k)
        if len(o) > 1: p.rot(o[1], X, -40 * k if m["frente"] else 50 * k)


def deitar(p, u):
    """u 0..1: corpo desce e membros dobram sob o tronco."""
    for m in E.g["membros"]:
        o = m["ossos"]
        if REPTIL:
            p.rot(o[0], Y, m["lado"] * 25 * u)
            continue
        if m["frente"]:
            p.rot(o[0], X, -35 * u); p.rot(o[1] if len(o) > 1 else None, X, -35 * u)
            if len(o) > 2: p.rot(o[2], X, 20 * u)
        else:
            p.rot(o[0], X, -28 * u); p.rot(o[1] if len(o) > 1 else None, X, 68 * u)
            if len(o) > 2: p.rot(o[2], X, -38 * u)
    p.loc((0, 0, -(0.3 if not REPTIL else 0.2) * H * u))


JAW = 0.45 if FAM in ("reptil", "marinho4", "serpentino", "dragao", "wyvern") else 0.7   # sem cavidade bucal: abertura contida


def cabeca_alvo(p, pitch=0, yaw=0, jaw=0, lag=0.0):
    jaw *= JAW
    for i, (pc, cab, mand) in enumerate(E.g["cabecas"]):
        f = 1.0 - lag * i
        if pc:
            for n in pc: p.rot(n, X, pitch * f / len(pc)); p.rot(n, Z, yaw * f / len(pc))
        p.rot(cab, X, pitch * 0.3 * f)
        p.rot(mand, X, jaw * f)


def base_pose(clip, t):
    p = Pose()
    fl = 0
    if FAM == "artropode":
        return artropode(clip, t)
    if FAM in ("serpentino", "marinho4"):
        return aquatico(clip, t)
    voador = FAM in ("dragao", "wyvern")
    if voador and clip not in ("Decolagem", "Pouso", "Planeio", "VooBatido", "Pairar", "AtaqueAereo", "CurvaAerea", "AbrirAsas", "RecolherAsas"):
        asas_dobradas(p)
    fases = FASES["bipede"] if FAM == "wyvern" else FASES["andar"]
    if clip == "Repouso":
        respirar(p, t); cauda(p, t, 4)
    elif clip in ("Andar", "MontadoAndar"):
        marcha(p, t, fases, 17, 24, 0.012, 6 if REPTIL else 0); cauda(p, t, 6)
    elif clip in ("Corrida", "MontadoCorrida"):
        fz = FASES["bipede"] if FAM == "wyvern" else (FASES["trote"] if REPTIL else FASES["galope"])
        marcha(p, t, fz, 27, 32, 0.04 if clip == "Corrida" else 0.02, 10 if REPTIL else 0); cauda(p, t, 10, levantar=8)
        for n in E.g["coluna"]: p.rot(n, X, (3 if not REPTIL else 0) * S(t))
    elif clip in ("VirarEsquerda", "VirarDireita", "MontadoVirarE", "MontadoVirarD"):
        s = 1 if clip in ("VirarEsquerda", "MontadoVirarE") else -1
        marcha(p, t, fases, 14, 25, 0.01)
        for n in E.g["coluna"]: p.rot(n, Z, s * 6)
        cabeca_alvo(p, yaw=s * 18); cauda(p, t, 5)
        for n in E.g["cauda"]: p.rot(n, Z, -s * 4)
    elif clip == "Arrancada":
        u = ease(t / 0.35)
        marcha(p, t, FASES["galope"] if not REPTIL else FASES["trote"], 30 * u, 45 * u, 0.03 * u)
        for n in E.g["coluna"]: p.rot(n, X, 6 * (1 - u) * pulso(t, 0, 0.35))
        p.loc((0, 0, -0.08 * H * pulso(t, 0, 0.3)))
    elif clip == "Frenagem":
        u = 1 - ease(t / 0.6)
        marcha(p, t, fases, 28 * u, 40 * u, 0.02 * u)
        for m in E.g["membros"]:
            if m["frente"]: p.rot(m["ossos"][0], X, -18 * pulso(t, 0.1, 0.7))
        for n in E.g["coluna"]: p.rot(n, X, -4 * pulso(t, 0.1, 0.7))
    elif clip == "ReacaoGolpe":
        u = pulso(t, 0, 0.6) * (1 if t < 0.3 else math.exp(-4 * (t - 0.3)))
        for n in E.g["coluna"]: p.rot(n, Z, 7 * u); p.rot(n, X, 4 * u)
        cabeca_alvo(p, pitch=12 * u, yaw=-15 * u, jaw=10 * u)
        p.loc((0, 0.06 * H * u, -0.03 * H * u))
    elif clip == "AtaqueBasico":
        a = pulso(t, 0.15, 0.55)
        cabeca_alvo(p, pitch=-14 * a + 10 * pulso(t, 0, 0.18), jaw=32 * pulso(t, 0.2, 0.5), lag=0.15)
        for n in E.g["coluna"]: p.rot(n, X, 5 * a)
        p.loc((0, -0.08 * H * a, -0.04 * H * a))
        for m in E.g["membros"]:
            if m["frente"] and FAM in ("felino", "plantigrado"): p.rot(m["ossos"][0], X, -35 * a)
        if voador:
            for a2 in E.g["asas"]: p.rot(a2["braco"][0], Y, -a2["lado"] * 25 * a)
    elif clip == "Morte":
        u = ease(t / 0.7)
        p.rot("Quadril", Y, 80 * u)
        p.loc((0, 0, -0.35 * H * u))
        for m in E.g["membros"]: p.rot(m["ossos"][0], X, (20 if m["frente"] else -20) * u)
        cabeca_alvo(p, pitch=20 * u, jaw=15 * u); cauda(p, 0, 0)
    elif clip == "Comer":
        d = ease(t / 0.2) * (1 - ease((t - 0.8) / 0.2))
        cabeca_alvo(p, pitch=45 * d * (0.5 if REPTIL else 1), jaw=14 * d * max(0, S(4 * t)))
        for n in E.g["coluna"]: p.rot(n, X, 4 * d)
        for m in E.g["membros"]:
            if m["frente"] and not REPTIL: p.rot(m["ossos"][0], X, -8 * d)
    elif clip == "DeitarDescanso":
        deitar(p, ease(t)); cabeca_alvo(p, pitch=15 * ease(t))
    elif clip == "Descanso":
        deitar(p, 1.0); respirar(p, t, 1.4); cabeca_alvo(p, pitch=15); cauda(p, t, 2)
    elif clip == "LevantarDescanso":
        deitar(p, 1 - ease(t)); cabeca_alvo(p, pitch=15 * (1 - ease(t)))
    elif clip == "Montar":
        u = pulso(t, 0, 1)
        deitar(p, 0.45 * u); respirar(p, t)
    elif clip == "Desmontar":
        u = pulso(t, 0, 1)
        deitar(p, 0.45 * u); for_cabeca = cabeca_alvo(p, yaw=12 * u)
    elif clip == "MontadoRepouso":
        respirar(p, t, 0.6); cauda(p, t, 3)
    elif clip == "GuardarNinho":
        deitar(p, 0.6); cabeca_alvo(p, yaw=35 * S(t), pitch=-5); respirar(p, t)
    elif clip == "Alerta":
        u = ease(t / 0.3)
        cabeca_alvo(p, pitch=-14 * u, yaw=10 * S(t) * u); cauda(p, t, 3, levantar=10 * u)
        p.loc((0, 0, 0.02 * H * u))
    elif clip == "Ameaca":
        u = pulso(t, 0.05, 0.95)
        if FAM == "plantigrado":                                     # urso ergue-se nas patas traseiras
            p.rot("Quadril", X, -55 * u)
            for m in E.g["membros"]:
                if m["frente"]: p.rot(m["ossos"][0], X, -40 * u)
                else: p.rot(m["ossos"][0], X, 50 * u)
            cabeca_alvo(p, pitch=25 * u, jaw=35 * u)
        else:
            for n in E.g["coluna"]: p.rot(n, X, 5 * u)
            p.loc((0, 0, -0.08 * H * u))
            cabeca_alvo(p, pitch=10 * u, jaw=30 * u * (0.7 + 0.3 * S(6 * t)), lag=0.1)
            cauda(p, t, 4, levantar=15 * u)
            if voador:
                for a in E.g["asas"]:
                    p.rot(a["braco"][0], Y, -a["lado"] * 35 * u); p.rot(a["braco"][0], Z, -a["lado"] * 30 * u)
    elif voador:
        voo(p, clip, t)
    return p


def voo(p, clip, t):
    tuck = {"Planeio": 1, "VooBatido": 1, "Pairar": 0.6, "AtaqueAereo": 1, "CurvaAerea": 1}.get(clip, 0)
    if clip == "Decolagem":
        u = ease(t / 0.35)
        deitar(p, 0.35 * (1 - u) * pulso(t, 0, 0.35))
        batida(p, t * 3, 45 * ease(t / 0.2))
        pernas_recolhidas(p, ease((t - 0.5) / 0.5))
        p.loc((0, 0, H * 1.6 * ease((t - 0.25) / 0.75)))
        for n in E.g["coluna"]: p.rot(n, X, -10 * u)
    elif clip == "Pouso":
        u = ease(t / 0.8)
        batida(p, t * 3, 40 * (1 - 0.5 * u))
        pernas_recolhidas(p, 1 - u)
        p.loc((0, 0, H * 1.2 * (1 - u)))
        deitar(p, 0.3 * pulso(t, 0.75, 1.0))
        for n in E.g["coluna"]: p.rot(n, X, -14 * pulso(t, 0.3, 0.9))
    elif clip == "Planeio":
        pernas_recolhidas(p)
        for a in E.g["asas"]:
            s = a["lado"]; p.rot(a["braco"][0], Y, -s * 4 + s * 2 * S(t)); p.rot(a["braco"][0], X, -3)
        cauda(p, t, 3, lat=False)
    elif clip == "VooBatido":
        pernas_recolhidas(p); batida(p, t * 2, 40)
        p.loc((0, 0, -0.05 * H * S(2 * t))); cauda(p, t * 2, 4, lat=False)
    elif clip == "Pairar":
        pernas_recolhidas(p, 0.6); batida(p, t * 3, 48, dobrar=10)
        for n in E.g["coluna"]: p.rot(n, X, -30)
        p.loc((0, 0, -0.06 * H * S(3 * t)))
    elif clip == "AtaqueAereo":
        a = pulso(t, 0.2, 0.7)
        pernas_recolhidas(p, 1 - a)
        for m in E.g["membros"]:
            if not m["frente"]: p.rot(m["ossos"][0], X, -50 * a)       # garras a frente no rasante
        for x in E.g["asas"]: p.rot(x["braco"][0], Z, x["lado"] * 35 * a)
        for n in E.g["coluna"]: p.rot(n, X, 20 * a)
        cabeca_alvo(p, jaw=30 * a)
        if FAM == "wyvern":
            for i, n in enumerate(E.g["cauda"]): p.rot(n, X, -25 * a)    # ferrao por cima do corpo
    elif clip == "CurvaAerea":
        pernas_recolhidas(p); batida(p, t * 2, 25)
        p.rot("Quadril", Y, 25); cabeca_alvo(p, yaw=15)
        for n in E.g["cauda"]: p.rot(n, Z, -5)
    elif clip in ("AbrirAsas", "RecolherAsas"):
        u = ease(t) if clip == "AbrirAsas" else 1 - ease(t)
        asas_dobradas(p, 1 - u)
        for a in E.g["asas"]: p.rot(a["braco"][0], Y, -a["lado"] * 18 * u * pulso(t, 0.4, 1.0))
        respirar(p, t)
    elif clip == "Empoleirar":
        deitar(p, 0.25); asas_dobradas(p, 0.9)
        cabeca_alvo(p, yaw=25 * S(t), pitch=-8); respirar(p, t)
        for a in E.g["asas"]: p.rot(a["braco"][0], Y, a["lado"] * 6 * S(t))


def aquatico(clip, t):
    p = Pose()
    cad = list(reversed(E.g["coluna"])) + E.g["cauda"]            # cabeca -> ponta da cauda
    n = len(cad)
    ond = {"NadoParado": (4, 0.5), "NadoCruzeiro": (12, 1.0), "NadoRapido": (20, 2.0), "NadoSuperficie": (10, 1.0),
           "Andar": (16, 1.0), "Corrida": (22, 2.0), "Repouso": (3, 0.5), "AtaqueSubaquatico": (14, 1.5), "MontadoAndar": (10, 1.0),
           "MontadoCorrida": (16, 2.0), "MontadoRepouso": (3, 0.5)}
    marinho = FAM == "marinho4"
    if clip in ond:
        amp, vel = ond[clip]
        amp *= CAR["amp"] * (0.5 if marinho else 1.0)
        for i, b in enumerate(cad):
            f = i / max(1, n - 1)
            p.rot(b, Z, amp * (0.3 + 0.7 * f) * S(vel * t - 1.2 * f))
        for nd in E.g["nadadeiras"]:
            s = nd["lado"]; k = 1.0 if nd["frente"] else 0.6
            p.rot(nd["ossos"][0], Y, s * 18 * k * vel * 0.6 * S(vel * t + (0 if nd["frente"] else 0.5)))
            p.rot(nd["ossos"][0], X, 12 * k * C(vel * t))
        if clip == "AtaqueSubaquatico":
            a2 = pulso(t, 0.3, 0.7)
            for b in cad[:4]: p.rot(b, X, -14 * a2)
            cabeca_alvo(p, jaw=40 * a2)
        if clip == "NadoSuperficie":
            for b in cad[:3]: p.rot(b, X, -6)
        cabeca_alvo(p, pitch=3 * S(t))
    elif clip in ("Mergulho", "Emersao"):
        s = 1 if clip == "Mergulho" else -1
        u = pulso(t, 0, 1)
        for i, b in enumerate(cad):
            f = i / max(1, n - 1)
            p.rot(b, X, s * 22 * u * (1 - f) - s * 12 * u * f)
            p.rot(b, Z, 10 * S(t - f))
        p.loc((0, 0, -s * 0.6 * H * (ease(t) if s > 0 else 1 - ease(t))))
    elif clip in ("VirarEsquerda", "VirarDireita", "MontadoVirarE", "MontadoVirarD"):
        s = 1 if "E" in clip[-1:] or clip == "VirarEsquerda" else -1
        for i, b in enumerate(cad):
            f = i / max(1, n - 1)
            p.rot(b, Z, s * 14 * (1 - f) + 8 * S(t - f))
    elif clip in ("AtaqueBasico", "Ameaca", "Alerta", "ReacaoGolpe", "Comer", "Arrancada", "Frenagem", "Morte",
                  "DeitarDescanso", "Descanso", "LevantarDescanso", "Montar", "Desmontar", "GuardarNinho", "Desacelerar"):
        a = pulso(t, 0.1, 0.6)
        if clip == "AtaqueBasico":
            for i, b in enumerate(cad[:4]): p.rot(b, X, 10 * pulso(t, 0, 0.25) - 18 * a)
            cabeca_alvo(p, jaw=35 * a)
        elif clip in ("Ameaca", "Alerta"):
            for b in cad[:4]: p.rot(b, X, -12 * ease(t / 0.3))
            cabeca_alvo(p, jaw=(30 if clip == "Ameaca" else 0) * pulso(t, 0.1, 0.9))
        elif clip == "ReacaoGolpe":
            for i, b in enumerate(cad): p.rot(b, Z, 12 * pulso(t, 0, 0.5) * (1 - i / n))
        elif clip == "Comer":
            for b in cad[:3]: p.rot(b, X, 15 * pulso(t, 0, 1)); cabeca_alvo(p, jaw=20 * max(0, S(4 * t)))
        elif clip == "Morte":
            u = ease(t / 0.8); p.rot("Raiz", Y, 150 * u)
            for i, b in enumerate(cad): p.rot(b, Z, 6 * (1 - u) * S(t - i / n))
        elif clip in ("Arrancada", "Frenagem", "Desacelerar"):
            k = ease(t / 0.4) if clip == "Arrancada" else 1 - ease(t / 0.6)
            for i, b in enumerate(cad): p.rot(b, Z, 18 * k * (0.3 + 0.7 * i / n) * S(2 * t - 1.2 * i / n))
        elif clip in ("DeitarDescanso", "Descanso", "LevantarDescanso", "GuardarNinho"):
            u = {"DeitarDescanso": ease(t), "Descanso": 1.0, "LevantarDescanso": 1 - ease(t), "GuardarNinho": 1.0}[clip]
            for i, b in enumerate(cad[1:]): p.rot(b, Z, 22 * u * (1 if (i // 4) % 2 == 0 else -1))   # enrolar
            if clip == "GuardarNinho": cabeca_alvo(p, yaw=25 * S(t))
        else:
            for b in cad[:3]: p.rot(b, X, 8 * pulso(t, 0, 1))
    return p


def artropode(clip, t):
    p = Pose()
    def patas(t, amp, lift):
        for perna in E.g["pernas_artro"]:
            k, s = perna["indice"], perna["lado"]
            f = t - ((k % 2) * 0.5 + (0.5 if s < 0 else 0)) % 1.0
            o = perna["ossos"]
            p.rot(o[0], Z, -s * amp * S(f))
            p.rot(o[0], Y, -s * lift * max(0, S(f + 0.25)))
    def pincas(abre=0, frente=0, ergue=0):
        for pc in E.g["pincas"]:
            s = pc["lado"]
            p.rot(pc["ossos"][0], Z, -s * frente); p.rot(pc["ossos"][0], X, -ergue)
            p.rot(pc["dedo"], Z, s * abre)
    def cauda_armar(golpe=0, balanco=0):
        for i, n in enumerate(E.g["cauda"]):
            p.rot(n, X, -golpe * (0.3 + 0.7 * i / len(E.g["cauda"]))); p.rot(n, Z, balanco * S(t - 0.1 * i))
    if clip in ("Andar", "MontadoAndar", "VirarEsquerda", "VirarDireita", "MontadoVirarE", "MontadoVirarD"):
        patas(t * 2, 18, 22)
        if "Virar" in clip or "VirarE" in clip or "VirarD" in clip:
            s = 1 if clip.endswith(("Esquerda", "E")) else -1
            p.rot("Corpo", Z, s * 8)
        cauda_armar(0, 3); pincas(5, 5)
    elif clip in ("Corrida", "MontadoCorrida", "Arrancada"):
        patas(t * 3, 24, 28); cauda_armar(0, 4); pincas(0, 12, 8)
    elif clip == "Frenagem":
        patas(t * 2, 18 * (1 - ease(t)), 20 * (1 - ease(t))); pincas(10 * ease(t), 15 * ease(t))
    elif clip in ("Repouso", "MontadoRepouso", "GuardarNinho", "Descanso"):
        cauda_armar(0, 2); pincas(4 * (1 + S(t)), 0)
        if clip in ("GuardarNinho", "Descanso"): p.loc((0, 0, -0.15 * H))
    elif clip in ("AtaqueBasico", "PincasEsmagadoras"):
        a = pulso(t, 0.15, 0.6)
        pincas(abre=30 * pulso(t, 0, 0.3) - 10 * a, frente=25 * a, ergue=10 * a)
    elif clip in ("FerraoPerfurante",):
        a = pulso(t, 0.2, 0.55)
        cauda_armar(golpe=-15 * pulso(t, 0, 0.2) + 40 * a)
    elif clip in ("Ameaca", "Alerta"):
        u = ease(t / 0.3)
        pincas(abre=25 * u, frente=-10 * u, ergue=20 * u); cauda_armar(golpe=-10 * u, balanco=4)
        p.loc((0, 0, 0.08 * H * u))
    elif clip == "ReacaoGolpe":
        u = pulso(t, 0, 0.5); p.rot("Corpo", Z, 8 * u); pincas(15 * u, -10 * u)
    elif clip == "Morte":
        u = ease(t / 0.7); p.rot("Corpo", Y, 160 * u); p.loc((0, 0, 0.1 * H * u))
        for perna in E.g["pernas_artro"]: p.rot(perna["ossos"][1], Y, perna["lado"] * 40 * u)
    elif clip == "Comer":
        pincas(abre=15 * max(0, S(3 * t)), frente=-15 * pulso(t, 0, 1), ergue=-5)
    elif clip in ("DeitarDescanso", "LevantarDescanso", "Montar", "Desmontar"):
        u = ease(t) if clip == "DeitarDescanso" else (1 - ease(t) if clip == "LevantarDescanso" else pulso(t, 0, 1) * 0.6)
        p.loc((0, 0, -0.15 * H * u))
        for perna in E.g["pernas_artro"]: p.rot(perna["ossos"][1], Y, -perna["lado"] * 20 * u)
    elif clip == "EscavacaoDeAreia":
        patas(t * 4, 10, 30); p.loc((0, 0, -0.3 * H * ease(t))); pincas(20, -20, -10)
    elif clip == "NuvemDeAreia":
        patas(t * 4, 26, 10); cauda_armar(0, 10); pincas(10, 10)
    return p


# habilidades oficiais -> molde de movimento (RPG_02 / Catalogo; sem efeitos)
HABS = {
    "Lobo_Ancestral": ["SaltoPredatorio:salto", "Uivo:uivo", "Investida:investida", "InstintoDeCaca:farejar"],
    "Lobo_Artico": ["SaltoPredatorio:salto", "Uivo:uivo", "Investida:investida", "InstintoDeCaca:farejar"],
    "Cerbero_Sombrio": ["MordidasTriplices:mordidas3", "RugidoInfernal:rugido", "InvestidaSombria:investida", "FuriaDasTresCabecas:furia3"],
    "Leao_Solar": ["SaltoSolar:salto", "RugidoDeComando:rugido", "GarraCircular:garra", "FocoDoPredador:espreita"],
    "Urso_Silvestre": ["GolpeColossal:garra", "RugidoProtetor:rugido", "CargaSelvagem:investida", "FortalezaViva:firmar"],
    "Bufalo_Colossal": ["CargaDeChifres:carga", "PisoteioSismico:pisoteio", "GuardaDaManada:firmar", "ImpetoSelvagem:investida"],
    "Crocodilo_Primordial": ["MordidaDeAgarrao:mordida", "GiroPredatorio:giro", "Submersao:submersao", "CaudaDeMare:cauda"],
    "Basilisco": ["OlharAmeacador:olhar", "MordidaToxica:mordida", "EspiralDefensiva:espiral", "Emboscada:salto"],
    "Lagarto_Cristalino": ["EscamasCristalinas:firmar", "GolpeDeCauda:cauda", "DisparoPrismatico:rugido", "Escalada:escalada"],
    "Escorpiao_Colossal": ["FerraoPerfurante:", "PincasEsmagadoras:", "EscavacaoDeAreia:", "NuvemDeAreia:"],
    "Serpente_Marinha": ["EspiralAquatica:espiral", "InvestidaSubmersa:investida_agua", "MordidaProfunda:mordida", "Correnteza:onda"],
    "Leviata_Jovem": ["OndaTitanica:onda", "MergulhoAbissal:mergulho", "RugidoOceanico:rugido", "RupturaDasMares:emersao"],
    "Wyvern": ["RasantePredatorio:rasante", "FerraoVenenoso:ferrao", "GuinadaEvasiva:guinada", "CacadaDosCeus:rasante"],
    "Dragao_das_Montanhas": ["SoproDraconico:sopro", "ArremetidaDraconica:investida", "TempestadeDeAsas:tempestade", "DominioDraconico:dominio"],
    "Dragao_Glacial": ["SoproDraconico:sopro", "ArremetidaDraconica:investida", "TempestadeDeAsas:tempestade", "DominioDraconico:dominio"],
    "Dragao_Sombrio": ["SoproDraconico:sopro", "ArremetidaDraconica:investida", "TempestadeDeAsas:tempestade", "DominioDraconico:dominio"],
}


def salto_canino(p, t, alto):
    """Salto predatorio / investida do Lobo V3, em fases: agachar e carregar nos posteriores -> impulsao (posteriores
    estendem para tras, anteriores alcancam a frente) -> voo (corpo em arco, membros estendidos, cauda como leme)
    -> aterrissagem (anteriores tocam primeiro e absorvem) -> recuperacao. Movimento no lugar (o jogo desloca a raiz)."""
    ag = ease(t / 0.22) * (1 - ease((t - 0.22) / 0.1))                # agachar
    imp = pulso(t, 0.2, 0.42)                                          # impulsao
    voo = pulso(t, 0.3, 0.78) if alto else pulso(t, 0.28, 0.62)
    ate = pulso(t, 0.68, 0.95) if alto else pulso(t, 0.55, 0.85)      # aterrissagem
    k = 1.0 if alto else 0.65
    deitar(p, 0.38 * ag + 0.3 * ate)
    for m in E.g["membros"]:
        o = m["ossos"]
        if m["frente"]:
            p.rot(o[0], X, (-12 * imp - 16 * voo * k + 8 * ate))       # escapula gira pouco (~30% da protracao)
            p.rot(o[1], X, (-25 * imp - 40 * voo * k + 18 * ate))      # umero leva o membro a frente, depois recebe o peso
            p.rot(o[2], X, -12 * voo * k)                              # cotovelo/antebraco estendidos no ar
            p.rot(o[3], X, 25 * voo * k - 20 * ate)                    # pata dobra no ar, abre ao tocar
        else:
            p.rot(o[0], X, 40 * imp * k + 45 * voo * k - 10 * ate)     # coxa empurra e fica estendida para tras
            p.rot(o[1], X, -25 * imp * k)
            p.rot(o[2], X, 35 * imp * k + 25 * voo * k)                # jarrete abre (extensao)
            p.rot(o[3], X, 30 * voo * k)
    subir = pulso(t, 0.3, 0.6) if alto else pulso(t, 0.28, 0.5)
    descer = pulso(t, 0.55, 0.8) if alto else pulso(t, 0.45, 0.65)
    p.rot("Quadril", X, -12 * subir * k + 14 * descer * k)            # nariz sobe na subida, desce na queda
    for n in E.g["coluna"]: p.rot(n, X, -6 * imp + 5 * ag + 4 * ate)  # coluna estende na impulsao, flexiona ao agachar
    p.loc((0, -0.15 * H * voo, (0.5 if alto else 0.12) * H * voo - 0.1 * H * ag))
    cabeca_alvo(p, pitch=10 * ag - 8 * voo + 12 * descer, jaw=(28 if alto else 32) * pulso(t, 0.45, 0.85))
    for i, n in enumerate(E.g["cauda"]):
        p.rot(n, X, (20 * voo - 6 * ag) * (1 - i / 8))                 # cauda sobe e estende no voo (leme)
    return p


def habilidade(molde, clip, t):
    if FAM == "artropode":
        return artropode(clip, t)
    p = Pose()
    if FAM in ("dragao", "wyvern") and molde not in ("rasante", "tempestade", "dominio"):
        asas_dobradas(p)
    a = pulso(t, 0.15, 0.7)
    if V3 and FAM == "canideo" and molde in ("salto", "investida"):
        return salto_canino(p, t, molde == "salto")
    if molde in ("salto", "investida", "carga", "investida_agua"):
        ag = pulso(t, 0, 0.3)
        if FAM in ("serpentino", "marinho4"):
            return aquatico("Arrancada", t)
        deitar(p, 0.3 * ag)
        for m in E.g["membros"]:
            p.rot(m["ossos"][0], X, (-40 if m["frente"] else 30) * a)
        alt = 0.5 if molde == "salto" else 0.08
        p.loc((0, -0.5 * H * a, alt * H * a - 0.1 * H * ag))
        cabeca_alvo(p, pitch=(25 if molde == "carga" else -10) * a, jaw=(0 if molde == "carga" else 25) * a)
    elif molde in ("uivo", "rugido", "sopro"):
        cabeca_alvo(p, pitch=(-35 if molde == "uivo" else -10) * a, jaw=40 * a, lag=0.2)
        for n in E.g["coluna"]: p.rot(n, X, -4 * a)
        if FAM in ("serpentino", "marinho4"):
            for b in list(reversed(E.g["coluna"]))[:3]: p.rot(b, X, -15 * a)
    elif molde in ("farejar", "espreita"):
        d = ease(t / 0.25) * (1 - ease((t - 0.8) / 0.2))
        cabeca_alvo(p, pitch=30 * d, yaw=15 * S(t) * d)
        if molde == "espreita": deitar(p, 0.3 * d); marcha(p, t, FASES["andar"], 8 * d, 10 * d, 0.0)
    elif molde in ("mordida", "mordidas3"):
        cabeca_alvo(p, pitch=-20 * a, jaw=40 * pulso(t, 0.2, 0.5), lag=0.3 if molde == "mordidas3" else 0)
        p.loc((0, -0.12 * H * a, 0))
    elif molde == "furia3":
        for i, (pc, cab, mand) in enumerate(E.g["cabecas"]):
            f = t * 3 - i / 3.0
            if pc: p.rot(pc[0], X, -12 * max(0, S(f))); p.rot(pc[0], Z, 15 * S(f + 0.25))
            p.rot(mand, X, 35 * max(0, S(f)))
    elif molde == "garra":
        for m in E.g["membros"]:
            if m["frente"] and m["lado"] > 0:
                p.rot(m["ossos"][0], X, -70 * a); p.rot(m["ossos"][0], Z, 30 * pulso(t, 0.3, 0.7))
        p.rot("Quadril", X, -10 * a); cabeca_alvo(p, jaw=20 * a)
    elif molde == "firmar":
        u = ease(t / 0.3)
        for m in E.g["membros"]: p.rot(m["ossos"][0], Y, m["lado"] * 8 * u)
        p.loc((0, 0, -0.08 * H * u)); cabeca_alvo(p, pitch=12 * u, jaw=10 * u)
    elif molde == "pisoteio":
        for m in E.g["membros"]:
            if m["frente"]: p.rot(m["ossos"][0], X, -45 * pulso(t, 0.1, 0.45))
        p.rot("Quadril", X, -18 * pulso(t, 0.1, 0.45)); p.loc((0, 0, -0.05 * H * pulso(t, 0.45, 0.6)))
    elif molde == "giro":
        p.rot("Quadril", Y, 360 * ease((t - 0.2) / 0.6)); cabeca_alvo(p, jaw=30 * a)
    elif molde == "submersao":
        p.loc((0, 0, -0.6 * H * ease(t))); cauda(p, t, 8)
    elif molde == "cauda":
        for i, n in enumerate(E.g["cauda"]):
            p.rot(n, Z, 45 * pulso(t, 0.15 + 0.03 * i, 0.6 + 0.03 * i) * (1 if i % 1 == 0 else -1))
        for n in E.g["coluna"]: p.rot(n, Z, -10 * a)
    elif molde == "olhar":
        cabeca_alvo(p, pitch=-15 * a, yaw=0); p.loc((0, 0, 0.05 * H * a))
        for n in E.g["coluna"]: p.rot(n, X, -3 * a)
    elif molde == "espiral":
        if FAM in ("serpentino", "marinho4"):
            return aquatico("Descanso", t)
        for i, n in enumerate(E.g["cauda"]): p.rot(n, Z, 35 * a)
        for n in E.g["coluna"]: p.rot(n, Z, 15 * a)
        cabeca_alvo(p, yaw=-40 * a, jaw=20 * a)
    elif molde == "escalada":
        for n in E.g["coluna"]: p.rot(n, X, -20)
        marcha(p, t, FASES["trote"], 22, 25, 0.0); p.loc((0, 0, 0.3 * H))
    elif molde in ("onda", "emersao", "mergulho"):
        return aquatico({"onda": "NadoRapido", "emersao": "Emersao", "mergulho": "Mergulho"}[molde], t)
    elif molde in ("rasante", "guinada"):
        voo(p, "AtaqueAereo" if molde == "rasante" else "CurvaAerea", t)
        if molde == "guinada": p.rot("Quadril", Y, -70 * pulso(t, 0.1, 0.6))
    elif molde == "ferrao":
        for i, n in enumerate(E.g["cauda"]): p.rot(n, X, (-12 * pulso(t, 0, 0.25) + 30 * a) * (0.3 + 0.7 * i / len(E.g["cauda"])))
    elif molde == "tempestade":
        p.rot("Quadril", X, -25 * a); batida(p, t * 3, 50 * a)
    elif molde == "dominio":
        cabeca_alvo(p, pitch=-25 * a, jaw=30 * a)
        for x in E.g["asas"]: p.rot(x["braco"][0], Y, -x["lado"] * 40 * a); p.rot(x["braco"][0], Z, -x["lado"] * 35 * a)
        p.loc((0, 0, 0.06 * H * a))
    return p


def lista_clips():
    base = ["Repouso", "Andar", "Corrida", "VirarEsquerda", "VirarDireita", "Arrancada", "Frenagem", "ReacaoGolpe",
            "AtaqueBasico", "Morte", "Comer", "DeitarDescanso", "Descanso", "LevantarDescanso"]
    mont = ["Montar", "Desmontar", "MontadoRepouso", "MontadoAndar", "MontadoCorrida", "MontadoVirarE", "MontadoVirarD"]
    terr = ["GuardarNinho", "Alerta", "Ameaca"]
    voo_ = ["Decolagem", "Pouso", "Planeio", "VooBatido", "Pairar", "AtaqueAereo", "Empoleirar", "CurvaAerea"]
    nado = ["NadoParado", "NadoCruzeiro", "NadoRapido", "NadoSuperficie", "Mergulho", "Emersao"]
    clips = base + mont + terr
    if FAM in ("dragao", "wyvern"): clips += voo_ + ["AbrirAsas", "RecolherAsas"]
    if FAM in ("serpentino", "marinho4"): clips += nado + ["AtaqueSubaquatico", "Desacelerar"]
    if ESP == "Crocodilo_Primordial": clips += ["NadoCruzeiro", "Mergulho", "Emersao"]
    return clips


DUR = {"Repouso": 4.0, "Andar": 1.2, "Corrida": 0.7, "VirarEsquerda": 1.2, "VirarDireita": 1.2, "Arrancada": 1.0, "Frenagem": 1.0,
       "ReacaoGolpe": 0.7, "AtaqueBasico": 1.0, "Morte": 2.0, "Comer": 3.0, "DeitarDescanso": 1.6, "Descanso": 5.0,
       "LevantarDescanso": 1.4, "Montar": 1.8, "Desmontar": 1.6, "MontadoRepouso": 4.0, "MontadoAndar": 1.2, "MontadoCorrida": 0.7,
       "MontadoVirarE": 1.2, "MontadoVirarD": 1.2, "GuardarNinho": 5.0, "Alerta": 2.0, "Ameaca": 2.4, "Decolagem": 2.4,
       "Pouso": 2.2, "Planeio": 3.0, "VooBatido": 1.0, "Pairar": 0.8, "AtaqueAereo": 1.6, "Empoleirar": 4.0, "CurvaAerea": 2.0,
       "NadoParado": 4.0, "NadoCruzeiro": 2.0, "NadoRapido": 1.0, "NadoSuperficie": 2.0, "Mergulho": 2.0, "Emersao": 2.0}
LOOP = {"Repouso", "Andar", "Corrida", "VirarEsquerda", "VirarDireita", "Descanso", "MontadoRepouso", "MontadoAndar",
        "MontadoCorrida", "MontadoVirarE", "MontadoVirarD", "GuardarNinho", "Planeio", "VooBatido", "Pairar", "Empoleirar",
        "CurvaAerea", "NadoParado", "NadoCruzeiro", "NadoRapido", "NadoSuperficie"}


# clips com contato obrigatorio com o chao (correcao de altura pelos pes) e os que so nao podem afundar
CHAO = {"Repouso", "Andar", "VirarEsquerda", "VirarDireita", "Arrancada", "Frenagem", "ReacaoGolpe", "AtaqueBasico", "Comer",
        "MontadoRepouso", "MontadoAndar", "MontadoVirarE", "MontadoVirarD", "Alerta", "Montar", "Desmontar", "Empoleirar",
        "AbrirAsas", "RecolherAsas"}
SO_AFUNDAR = {"Corrida", "MontadoCorrida", "Ameaca", "GuardarNinho", "DeitarDescanso", "Descanso", "LevantarDescanso"}
DUR.update({"AbrirAsas": 1.6, "RecolherAsas": 1.4, "AtaqueSubaquatico": 1.2, "Desacelerar": 1.4})


def pes(arm):
    nomes = [m["ossos"][-1] for m in E.g["membros"]] + [p["ossos"][-1] for p in E.g["pernas_artro"]]
    return [arm.pose.bones[n] for n in nomes if n in arm.pose.bones]


def balanco(p, nome, t):
    """Balanco secundario da pelagem (juba, nuca, peito, ventre, bochechas, coxas): oscilacao atrasada em relacao ao
    corpo, amplitude pela intensidade do clipe; ciclos inteiros nos clipes em loop. Custo no jogo: so ossos extras."""
    A = {"Corrida": 13, "MontadoCorrida": 11, "Arrancada": 12, "SaltoPredatorio": 15, "Investida": 13, "Frenagem": 10,
         "ReacaoGolpe": 9, "Andar": 6, "MontadoAndar": 6, "VirarEsquerda": 6, "VirarDireita": 6, "MontadoVirarE": 6,
         "MontadoVirarD": 6, "Uivo": 5, "Ameaca": 5, "Morte": 5}.get(nome, 2.5)
    marcha_ = nome in ("Andar", "Corrida", "MontadoAndar", "MontadoCorrida", "VirarEsquerda", "VirarDireita", "MontadoVirarE", "MontadoVirarD")
    f = 2 if marcha_ else max(1, round(DUR.get(nome, 2.0) / 1.3))
    for i, n in enumerate(E.g["pelo"]):
        lag = 0.12 + 0.06 * (i % 3)
        p.rot(n, X, A * S(f * t - lag))
        p.rot(n, Y, 0.35 * A * S(f * t - lag + 0.25))


def gravar(arm, clips):
    arm.animation_data_create()
    PB = arm.pose.bones
    M = {pb.name: pb.bone.matrix_local.to_3x3() for pb in PB}
    for pb in PB: pb.rotation_mode = "QUATERNION"
    mods = [m for o in arm.children for m in o.modifiers if m.type == "ARMATURE"]
    for m in mods: m.show_viewport = False                        # acelera: so o esqueleto e avaliado
    PES = pes(arm)
    bpy.context.view_layer.update()
    z0 = min(pb.tail.z for pb in PES) if PES else 0.0
    raiz = arm.pose.bones["Raiz"]; Mr = M["Raiz"]
    feitas = []
    for nome, fn in clips:
        peso = CAR["peso"] ** 0.25
        dur = DUR.get(nome, 2.0) * (peso if nome in LOOP else 1.0)
        nfr = max(8, int(dur * FPS))
        act = bpy.data.actions.new(nome); arm.animation_data.action = act
        for fr in list(range(0, nfr + 1, 2)) + ([nfr] if nfr % 2 else []):
            t = fr / nfr
            p = fn(t)
            if E.g.get("pelo"): balanco(p, nome, t)
            for pb in PB:
                q, loc = p.get(pb.name, (Quaternion(), None))
                Mi = M[pb.name]
                pb.rotation_quaternion = (Mi.inverted() @ q.to_matrix() @ Mi).to_quaternion()
                pb.location = (Mi.inverted() @ loc) if loc is not None else Vector()
            if PES and (nome in CHAO or nome in SO_AFUNDAR or nome in HAB_CHAO):
                bpy.context.view_layer.update()
                dz = z0 - min(pb.tail.z for pb in PES)
                if nome in CHAO or dz > 0:
                    w = Vector(p.get("Raiz", (None, None))[1] or Vector()) + Vector((0, 0, dz))
                    raiz.location = Mr.inverted() @ w
            for pb in PB:
                pb.keyframe_insert("rotation_quaternion", frame=fr + 1)
                pb.keyframe_insert("location", frame=fr + 1)
        act.use_fake_user = True
        act["loop"] = nome in LOOP
        tr = arm.animation_data.nla_tracks.new(); tr.name = nome; tr.strips.new(nome, 1, act)
        arm.animation_data.action = None
        feitas.append(nome)
    for m in mods: m.show_viewport = True
    for tr in arm.animation_data.nla_tracks: tr.mute = True
    for pb in PB:
        pb.rotation_quaternion = Quaternion(); pb.location = Vector()
    return feitas


def auditar(arm, col, feitas):
    """Classifica cada acao: deformacao (esticamento de arestas do corpo) e contato com o chao."""
    corpo = next(o for o in col.objects if o.name.endswith("_Corpo"))
    me0 = corpo.data
    E0 = np.array([(me0.vertices[e.vertices[0]].co - me0.vertices[e.vertices[1]].co).length for e in me0.edges]) + 1e-6
    ed = np.array([e.vertices[:] for e in me0.edges])
    PES = pes(arm)
    bpy.context.view_layer.update()
    z0 = min(pb.tail.z for pb in PES) if PES else 0.0
    res = {}
    for nome in feitas:
        act = bpy.data.actions[nome]; arm.animation_data.action = act
        f0, f1 = act.frame_range
        piores, pen = [], 0.0
        for t in (0.25, 0.5, 0.85):
            bpy.context.scene.frame_set(int(f0 + t * (f1 - f0)))
            dg = bpy.context.evaluated_depsgraph_get()
            eo = corpo.evaluated_get(dg); me = eo.to_mesh()
            P = np.array([v.co for v in me.vertices]); eo.to_mesh_clear()
            L = np.linalg.norm(P[ed[:, 0]] - P[ed[:, 1]], axis=1) + 1e-6
            r = np.maximum(L / E0, E0 / L)
            piores.append((float(np.percentile(r, 99)), float((r > 1.8).mean() * 100)))
            if PES and nome in CHAO:
                pen = max(pen, abs(min(pb.tail.z for pb in PES) - z0))
        est = max(x[0] for x in piores); pct = max(x[1] for x in piores)
        if est <= 1.6 and pct <= 0.3 and pen < 0.05 * H: cls = "Aprovada"
        elif est <= 2.2 and pct <= 1.5: cls = "Pequenos ajustes"
        else: cls = "Refazer"
        res[nome] = {"esticamento_p99": round(est, 2), "pct_arestas_acima_1_8": round(pct, 2), "erro_contato_chao": round(pen, 3), "classe": cls}
    arm.animation_data.action = None
    bpy.context.scene.frame_set(1)
    return res


def caixas(arm, col):
    """Hitboxes simplificadas: uma capsula por osso deformante relevante (centro, comprimento, raio) para colisao/dano."""
    corpo = next(o for o in col.objects if o.name.endswith("_Corpo"))
    P = np.array([corpo.matrix_world @ v.co for v in corpo.data.vertices])
    segs = {b.name: (np.array(b.head_local), np.array(b.tail_local)) for b in arm.data.bones if b.use_deform and not b.name.startswith("Pelo_")}
    D = dist_segs(P, segs, list(segs))
    dono = np.argmin(D, axis=1)
    out = []
    for j, n in enumerate(segs):
        sel = D[dono == j, j]
        if len(sel) < 30 or n.startswith(("Dedo", "Mandibula")): continue
        a, b = segs[n]
        out.append({"osso": n, "a": [round(float(x), 2) for x in a], "b": [round(float(x), 2) for x in b], "raio": round(float(np.percentile(sel, 80)), 2)})
    return out


HAB_CHAO = set()
if V3: SO_AFUNDAR.update({"SaltoPredatorio", "Investida"})
col = finalizar()
arm = montar_rig(col)
clips = [(c, (lambda c: (lambda t: base_pose(c, t)))(c)) for c in lista_clips()]
for h in HABS[ESP]:
    nome, molde = h.split(":")
    clips.append((nome, (lambda n, m: (lambda t: habilidade(m, n, t)))(nome, molde)))
    if molde in ("mordida", "mordidas3", "rugido", "uivo", "sopro", "firmar", "olhar", "garra", "furia3", "farejar", "espreita", "cauda") and FAM not in ("serpentino", "marinho4"):
        HAB_CHAO.add(nome); CHAO.add(nome)
for n in [c[0] for c in clips if c[0] not in DUR]:
    DUR[n] = 1.8
feitas = gravar(arm, clips)
aud = auditar(arm, col, feitas)
hit = caixas(arm, col)
bpy.context.scene.render.fps = FPS
dest = os.path.join(RAIZ, ESP, ESP + "_final" + SUF + ".blend")
bpy.ops.wm.save_as_mainfile(filepath=dest)
os.makedirs(os.path.join(RAIZ, "_Export"), exist_ok=True)
for o in bpy.context.view_layer.objects: o.select_set(False)
for o in col.objects: o.select_set(True)
bpy.context.view_layer.objects.active = arm
for tr in arm.animation_data.nla_tracks: tr.mute = False
glb = os.path.join(RAIZ, "_Export", ESP + SUF + ".glb")
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", use_selection=True, export_animations=True,
                          export_animation_mode="ACTIONS", export_skins=True, export_yup=True, export_apply=False,
                          export_image_format="JPEG", export_jpeg_quality=88)
for tr in arm.animation_data.nla_tracks: tr.mute = True
imgs = [i for i in bpy.data.images if i.size[0] > 0]
nkeys = sum(len(fc.keyframe_points) for a in bpy.data.actions for l in a.layers for s in l.strips for cb in s.channelbags for fc in cb.fcurves)
info = {"especie": ESP, "familia": FAM, "ossos": len(arm.data.bones), "animacoes": feitas, "n_animacoes": len(feitas),
        "objetos": {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in col.objects if o.type == "MESH"},
        "tris_total": sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in col.objects if o.type == "MESH"),
        "materiais": len({m.name for o in col.objects if o.type == "MESH" for m in o.data.materials}),
        "texturas": [(i.name, i.size[0]) for i in imgs], "memoria_texturas_MB": round(sum(i.size[0] * i.size[1] * 4 for i in imgs) / 2**20, 1),
        "keyframes_total": nkeys, "glb_KB": int(os.path.getsize(glb) / 1024), "padrao_base": CORES[ESP][0],
        "auditoria": aud, "hitboxes": hit}
with open(os.path.join(RAIZ, "review", ESP, "final" + SUF + ".json"), "w", encoding="utf-8") as f:
    json.dump(info, f, ensure_ascii=False, indent=1)
cl = {}
for v in aud.values(): cl[v["classe"]] = cl.get(v["classe"], 0) + 1
print("FINAL", ESP, "ossos", info["ossos"], "anims", info["n_animacoes"], "tris", info["tris_total"], "tex MB", info["memoria_texturas_MB"], "glb KB", info["glb_KB"], "aud", cl)