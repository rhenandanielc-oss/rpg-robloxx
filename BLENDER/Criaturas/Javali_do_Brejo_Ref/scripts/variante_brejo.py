"""Javali-do-Brejo v1: variante visual da base Javali Silvestre (malha low_v1 + rig r4 + Andar do lote A).
Direcao PROVISORIA (sem ficha propria em REFERENCIAS/pantano-nebuloso/javali-do-brejo/): tons frios e escuros,
lama localizada em patas, ventre e queixo, cerdas da crista agrupadas em tufos, crista estendida ate a garupa
e focinho mais longo/levemente caido. So mexe em POSICOES de vertices (mesma topologia, mesmos pesos e ossos).
Cor e rugosidade novas sao ASSADAS (Cycles, Emit) de um material procedural guardado como *_Fonte (fake user).
Uso: blender -b fonte/Javali_Clipes_LA.blend -P scripts/variante_brejo.py -- <pasta_variante> [v1]"""
import bpy, sys, os, json, math, shutil
import numpy as np

A = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A[0]); VER = A[1] if len(A) > 1 else "v1"
TEX = os.path.join(OUT, "texturas"); os.makedirs(TEX, exist_ok=True)
FONTE = os.path.join(OUT, "fonte")
P = {   # parametros da variante (todos PROPOSTA visual, nao regra de jogo)
    "crista_altura_extra": 0.40, "crista_tufo": 0.18, "crista_tufo_periodo": 0.10, "crista_aperto_x": 0.25,
    "crista_garupa_altura": 0.022, "focinho_avanco": 0.065, "focinho_queda_graus": 5.0, "disco_escala": 1.10,
    "lama_molhada": (0.11, 0.092, 0.058), "lama_crosta": (0.30, 0.255, 0.175), "lama_rugosidade": (0.45, 0.88),
    "lama_pata_z": (0.19, 0.30), "lama_ventre_z": (0.46, 0.34),
}
REL = {"versao": VER, "parametros_PROPOSTA": P}

# ---- 1. so o Andar; nomes proprios ------------------------------------------------------------------------------
for a in list(bpy.data.actions):
    if a.name != "Javali_Andar": bpy.data.actions.remove(a)
act = bpy.data.actions["Javali_Andar"]; act.name = "JavaliBrejo_Andar"; act.use_fake_user = True
arm = bpy.data.objects["Javali_Rig"]; arm.name = "JavaliBrejo_Rig"; arm.data.name = "JavaliBrejo_Rig"
corpo = bpy.data.objects["Javali_Corpo"]; corpo.name = "JavaliBrejo_Corpo"; corpo.data.name = "JavaliBrejo_Corpo"
cab = bpy.data.objects["Javali_Cabeca"]; cab.name = "JavaliBrejo_Cabeca"; cab.data.name = "JavaliBrejo_Cabeca"
arm.animation_data_create(); arm.animation_data.action = None
MALHAS = [corpo, cab]

# ---- 2. forma: crista em tufos + garupa, focinho ---------------------------------------------------------------
def co_de(o): c = np.empty(len(o.data.vertices) * 3); o.data.vertices.foreach_get("co", c); return c.reshape(-1, 3)
C0 = {o.name: co_de(o) for o in MALHAS}
todos = np.vstack(list(C0.values()))
lado = todos[(np.abs(todos[:, 0]) > 0.09) & (np.abs(todos[:, 0]) < 0.13)]          # topo da pele nos flancos (sem crista)
yb = np.arange(-0.46, 0.50, 0.03); zs_b = []
for y in yb:
    s = lado[(lado[:, 1] >= y - 0.03) & (lado[:, 1] < y + 0.03)]; zs_b.append(s[:, 2].max() if len(s) else np.nan)
zs_b = np.array(zs_b); ok = ~np.isnan(zs_b); zs_b = np.interp(yb, yb[ok], zs_b[ok])
zs_b = np.convolve(np.pad(zs_b, 2, mode="edge"), np.ones(5) / 5, mode="valid")    # suaviza
def ss(e0, e1, x): t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

def forma(c, cabeca):
    c = c.copy(); x, y, z = c[:, 0], c[:, 1], c[:, 2]
    zs = np.interp(y, yb, zs_b); h = z - zs
    tufo = np.cos(2 * np.pi * (y + 0.30) / P["crista_tufo_periodo"])                   # -1..1, tufos suaves (v1 com picos = laminas)
    # crista: so na linha media, atras das orelhas, ate o meio do dorso; mais alta e mais estreita (cerdas agrupadas)
    d = np.clip(h / 0.06, 0, 1) * ss(0.10, 0.05, np.abs(x)) * ss(-0.42, -0.36, y) * (1 - ss(0.30, 0.42, y))
    z2 = z + d * h * (P["crista_altura_extra"] + P["crista_tufo"] * tufo)
    x2 = x * (1 - P["crista_aperto_x"] * d)
    # crista continua baixa ate a garupa (fileira de cerdas molhadas), sem picos
    r = ss(0.075, 0.02, np.abs(x)) * ss(0.0, 0.12, y) * (1 - ss(0.34, 0.46, y)) * ss(zs - 0.035, zs - 0.005, z)
    z2 = z2 + r * P["crista_garupa_altura"]
    if cabeca:   # focinho: ponte alongada entre olhos e presas; parte da frente (presas, disco) move RIGIDA
        t = ss(-0.53, -0.61, y)
        y2 = y - P["focinho_avanco"] * t
        a = math.radians(P["focinho_queda_graus"]) * t                                  # cai em torno da ponte
        py, pz = -0.57, 0.40
        yy, zz = y2 - py, z2 - pz
        y3 = py + yy * np.cos(a) - zz * np.sin(a)                                         # rotacao no plano YZ (frente = -Y):
        z3 = pz + zz * np.cos(a) + yy * np.sin(a)                                         # ponta (yy < 0) desce
        disc = ss(-0.69, -0.74, y)                                                        # disco do focinho maior
        cx, cz = 0.0, 0.36
        x2 = cx + (x2 - cx) * (1 + (P["disco_escala"] - 1) * disc)
        z3 = cz + (z3 - cz) * (1 + (P["disco_escala"] - 1) * disc)
        y2, z2 = y3, z3
    else:
        y2 = y
    return np.stack([x2, y2, z2], 1)

for o in MALHAS:
    c1 = forma(C0[o.name], o is cab); o.data.vertices.foreach_set("co", c1.ravel()); o.data.update()
    dd = np.linalg.norm(c1 - C0[o.name], axis=1)
    REL.setdefault("forma", {})[o.name] = {"vertices_movidos_>1mm": int((dd > 0.001).sum()), "desloc_max_cm": round(float(dd.max()) * 100, 2)}
# costura cabeca/corpo: pares que coincidiam antes continuam coincidindo?
from mathutils.kdtree import KDTree
kd = KDTree(len(C0[corpo.name]))
for i, p in enumerate(C0[corpo.name]): kd.insert(p, i)
kd.balance(); par = []
for j, p in enumerate(C0[cab.name]):
    _, i, dist = kd.find(p)
    if dist < 1e-5: par.append((i, j))
C1c, C1h = co_de(corpo), co_de(cab)
REL["costura"] = {"pares": len(par), "pares_iguais_depois": int(sum(np.linalg.norm(C1c[i] - C1h[j]) < 1e-5 for i, j in par))}

# ---- 3. material procedural (fonte) e bake ---------------------------------------------------------------------
sc = bpy.context.scene; sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 1
bk = sc.render.bake; bk.use_selected_to_active = False; bk.use_cage = False; bk.target = "IMAGE_TEXTURES"   # o .blend da base guardou selected_to_active (bake do bruto)
arm.data.pose_position = "REST"; bpy.context.view_layer.update()

def img_de(mat, chave):
    for n in mat.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image and n.image.name.endswith("_" + chave): return n.image   # "Cor" tambem casa com "Corpo"
def fonte_mat(o, base, cabeca):
    m = bpy.data.materials.new(base.name.replace("Javali", "JavaliBrejo") + "_Fonte"); m.use_nodes = True; m.use_fake_user = True
    nt = m.node_tree; N = nt.nodes; L = nt.links; N.clear()
    def nd(t, **kw):
        n = N.new(t)
        for k, v in kw.items(): setattr(n, k, v)
        return n
    def mr(sock, a, b, c, d, interp="SMOOTHSTEP"):
        n = nd("ShaderNodeMapRange", interpolation_type=interp); L.new(sock, n.inputs[0])
        n.inputs[1].default_value, n.inputs[2].default_value, n.inputs[3].default_value, n.inputs[4].default_value = a, b, c, d; return n.outputs[0]
    def math_(op, s0, v1=None, s1=None, clamp=True):
        n = nd("ShaderNodeMath", operation=op, use_clamp=clamp); L.new(s0, n.inputs[0])
        if s1 is not None: L.new(s1, n.inputs[1])
        elif v1 is not None: n.inputs[1].default_value = v1
        return n.outputs[0]
    def mix(fac, a, b, blend="MIX"):
        n = nd("ShaderNodeMix", data_type="RGBA", blend_type=blend, clamp_result=True)
        if isinstance(fac, float): n.inputs[0].default_value = fac
        else: L.new(fac, n.inputs[0])
        for k, s in ((6, a), (7, b)):
            if isinstance(s, tuple): n.inputs[k].default_value = s
            else: L.new(s, n.inputs[k])
        return n.outputs[2]
    tc = nd("ShaderNodeTexCoord"); sep = nd("ShaderNodeSeparateXYZ"); L.new(tc.outputs["Object"], sep.inputs[0])
    X, Y, Z = sep.outputs
    geo = nd("ShaderNodeNewGeometry"); sn = nd("ShaderNodeSeparateXYZ"); L.new(geo.outputs["Normal"], sn.inputs[0])
    tcor = nd("ShaderNodeTexImage", image=img_de(base, "Cor")); L.new(tc.outputs["UV"], tcor.inputs[0])
    trug = nd("ShaderNodeTexImage", image=img_de(base, "Rugosidade")); L.new(tc.outputs["UV"], trug.inputs[0])
    # tom frio e escuro
    hsv = nd("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = 0.45; hsv.inputs["Value"].default_value = 0.70
    L.new(tcor.outputs["Color"], hsv.inputs["Color"])
    frio = mix(1.0, hsv.outputs[0], (0.80, 0.92, 1.0, 1), "MULTIPLY")
    # cerdas agrupadas: estrias escuras verticais na crista
    ns = nd("ShaderNodeTexNoise"); ns.inputs["Scale"].default_value = 1.0; ns.inputs["Detail"].default_value = 2.0
    mp = nd("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (70, 45, 6); L.new(tc.outputs["Object"], mp.inputs[0]); L.new(mp.outputs[0], ns.inputs["Vector"])
    crista = math_("MULTIPLY", mr(Z, 0.66, 0.74, 0, 1), s1=mr(math_("ABSOLUTE", X), 0.10, 0.05, 0, 1))
    estria = math_("MULTIPLY", crista, s1=mr(ns.outputs["Fac"], 0.45, 0.60, 0, 0.55))
    cor = mix(estria, frio, (0.02, 0.022, 0.022, 1))
    # lama localizada: patas (borda irregular), ventre, queixo
    nl = nd("ShaderNodeTexNoise"); nl.inputs["Scale"].default_value = 9.0; nl.inputs["Detail"].default_value = 4.0
    L.new(tc.outputs["Object"], nl.inputs["Vector"])
    zr = math_("ADD", Z, s1=math_("MULTIPLY", math_("SUBTRACT", nl.outputs["Fac"], 0.5, clamp=False), 0.10, clamp=False), clamp=False)
    pata = mr(zr, *P["lama_pata_z"], 1, 0)
    ventre = math_("MULTIPLY", mr(sn.outputs[2], 0.05, -0.45, 0, 1), s1=mr(zr, *P["lama_ventre_z"], 0, 1))
    queixo = math_("MULTIPLY", mr(Y, -0.62, -0.70, 0, 1), s1=mr(Z, 0.345, 0.315, 0, 1)) if cabeca else None
    lama = math_("MAXIMUM", pata, s1=ventre)
    if queixo is not None: lama = math_("MAXIMUM", lama, s1=math_("MULTIPLY", queixo, 0.7))
    if cabeca:   # presas de marfim nao recebem lama
        bw = nd("ShaderNodeRGBToBW"); L.new(tcor.outputs["Color"], bw.inputs[0]); presa = mr(bw.outputs[0], 0.50, 0.64, 0, 1)
        lama = math_("MULTIPLY", lama, s1=mr(presa, 0, 1, 1, 0))
    crosta = math_("MULTIPLY", math_("MULTIPLY", lama, s1=mr(lama, 0.0, 0.6, 1.0, 0.0)), s1=mr(nl.outputs["Fac"], 0.45, 0.62, 0, 1))
    lama_cor = mix(crosta, (*P["lama_molhada"], 1), (*P["lama_crosta"], 1))       # marrom-oliva: contrasta com o pelo frio
    bwb = nd("ShaderNodeRGBToBW"); L.new(tcor.outputs["Color"], bwb.inputs[0])
    lama_cor = mix(0.35, lama_cor, mix(1.0, lama_cor, bwb.outputs[0], "MULTIPLY"))   # guarda um pouco do pelo
    cor = mix(math_("MULTIPLY", lama, 0.92), cor, lama_cor)
    if cabeca:   # marfim levemente manchado, sem perder a leitura das presas
        cor = mix(presa, cor, mix(1.0, tcor.outputs["Color"], (0.93, 0.90, 0.82, 1), "MULTIPLY"))
    rug_lama = mr(crosta, 0, 1, *P["lama_rugosidade"])
    rug = nd("ShaderNodeMix", data_type="FLOAT", clamp_result=True); L.new(lama, rug.inputs[0]); L.new(trug.outputs["Color"], rug.inputs[2]); L.new(rug_lama, rug.inputs[3])
    em = nd("ShaderNodeEmission"); out = nd("ShaderNodeOutputMaterial")
    L.new(cor, em.inputs["Color"]); L.new(em.outputs[0], out.inputs["Surface"])
    m["_cor_sock"] = 0
    return m, em, cor, rug.outputs[0], tcor, trug

REL["bake"] = {}
for o, cabeca in ((corpo, False), (cab, True)):
    base = o.data.materials[0]; parte = "Cabeca" if cabeca else "Corpo"
    m, em, cor, rug, tcor, trug = fonte_mat(o, base, cabeca)
    o.data.materials[0] = m
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    o.select_set(True); bpy.context.view_layer.objects.active = o
    saidas = {}
    for canal, sock, nc in (("Cor", cor, False), ("Rugosidade", rug, True)):
        im = bpy.data.images.new(f"T_JavaliBrejo_{parte}_{canal}", 1024, 1024, alpha=False)
        if nc: im.colorspace_settings.name = "Non-Color"
        tn = m.node_tree.nodes.new("ShaderNodeTexImage"); tn.image = im; m.node_tree.nodes.active = tn
        m.node_tree.links.new(sock, em.inputs["Color"])
        bpy.ops.object.bake(type="EMIT", margin=8, use_clear=True)
        p = os.path.join(TEX, im.name + ".png"); im.filepath_raw = p; im.file_format = "PNG"; im.save()
        im.filepath = p; m.node_tree.nodes.remove(tn); saidas[canal] = im
    m.node_tree.links.new(cor, em.inputs["Color"])
    # normal: a mesma da base (copia propria)
    nsrc = img_de(base, "Normal"); np_ = os.path.join(TEX, f"T_JavaliBrejo_{parte}_Normal.png")
    shutil.copyfile(os.path.join(FONTE, os.path.basename(nsrc.filepath)), np_)
    nimg = bpy.data.images.load(np_); nimg.colorspace_settings.name = "Non-Color"; nimg.name = f"T_JavaliBrejo_{parte}_Normal"
    # material final = copia do material da base com as imagens trocadas
    fin = base.copy(); fin.name = f"M_JavaliBrejo_{parte}"
    for n in fin.node_tree.nodes:
        if n.type == "TEX_IMAGE" and n.image:
            for chave, im in (("Cor", saidas["Cor"]), ("Rugosidade", saidas["Rugosidade"]), ("Normal", nimg)):
                if n.image.name.endswith("_" + chave): n.image = im; break
    o.data.materials[0] = fin
    # as texturas da base ficam ligadas so ao material _Fonte, a partir das copias em fonte/
    for t in (tcor, trug):
        t.image.filepath = os.path.join(FONTE, os.path.basename(t.image.filepath))
    REL["bake"][parte] = {k: os.path.relpath(v.filepath, OUT) for k, v in saidas.items()} | {"Normal": os.path.relpath(np_, OUT)}
    bpy.data.materials.remove(base)

arm.data.pose_position = "POSE"; arm.animation_data.action = act; sc.frame_set(1)
sc.render.engine = "BLENDER_EEVEE"
for o in list(bpy.data.objects):
    if o.type in ("CAMERA", "LIGHT"): bpy.data.objects.remove(o)
# imagens sem uso
for im in list(bpy.data.images):
    if im.users == 0: bpy.data.images.remove(im)
REL["tris"] = {o.name: sum(len(p.vertices) - 2 for p in o.data.polygons) for o in MALHAS}
REL["materiais"] = [o.data.materials[0].name for o in MALHAS]
REL["ossos"] = len(arm.data.bones)
dst = os.path.join(OUT, f"CR_JavaliBrejo_{VER}.blend")
bpy.ops.wm.save_as_mainfile(filepath=dst, relative_remap=True)
bpy.ops.file.make_paths_relative(); bpy.ops.wm.save_mainfile()
json.dump(REL, open(os.path.join(OUT, f"relatorio_variante_{VER}.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("VARIANTE", json.dumps(REL, ensure_ascii=False))
