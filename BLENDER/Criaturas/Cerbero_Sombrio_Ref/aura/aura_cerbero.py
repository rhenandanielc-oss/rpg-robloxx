"""Aura permanente do Cerbero Sombrio - A1 (18/11): PREVIA da aura de base para aprovar o visual (REFERENCIAS_PODERES v6.2 §5.1/§5.9h).
Metodo dos lobos (Lobo_Artico_Ref/boreal/boreal_fx_r8.py): linhas desenhadas como FITAS finas projetadas na pele (pose de
repouso), que depois de aprovadas viram mascara de emissao assada na UV (como no r7/r8 do Lobo Artico). Nesta etapa as fitas
r2: assadas na UV da pele ja nesta etapa (fitas soltas quebravam no pelo).
  * linhas contínuas e finas (~1,2% da altura) em roxo-sombra e vermelho-brasa: dorso, flanco, pernas, cauda, os 3 pescocos e o
    alto de cada cranio; rosto limpo (nada em olhos, focinho e orelhas);
  * pulso lento (1,8 s) correndo da cabeca para a cauda; cada cabeca com o PROPRIO pulso, defasado;
  * olhos em brasa discreta; Pelagem Infernal: brasa fraca nas pontas do pelo (borda).
Valores = [A TESTAR]. Uso: blender -b -t 4 ../rig/clipes_L3/CR_Cerbero_Anim.blend -P aura_cerbero.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, json
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.render.threads_mode = "FIXED"; sc.render.threads = 4
rig = bpy.data.objects["Cerbero_Rig"]
for pb in rig.pose.bones:
    for c in pb.constraints: c.mute = True
if rig.animation_data: rig.animation_data.action = None
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
CAB, CORPO = bpy.data.objects["Cerbero_Cabecas"], bpy.data.objects["Cerbero_Corpo"]
def bvh_de(objs):
    dg = bpy.context.evaluated_depsgraph_get(); bm = bmesh.new()
    for o in objs:
        me = o.evaluated_get(dg).to_mesh(); tmp = bmesh.new(); tmp.from_mesh(me); tmp.transform(o.matrix_world)
        m2 = bpy.data.meshes.new("tmp"); tmp.to_mesh(m2); tmp.free(); bm.from_mesh(m2); bpy.data.meshes.remove(m2); o.evaluated_get(dg).to_mesh_clear()
    t = BVHTree.FromBMesh(bm); bm.free(); return t
BVH = bvh_de([CAB, CORPO])
def osso(n): b = rig.data.bones[n]; return b.head_local.copy(), b.tail_local.copy()
H = 19.6; LARG = 0.008 * H; FOLGA = 0.10                     # r3: linhas mais finas (referencia: finas e discretas)
def suavizar(p, n=2, it=3):
    p = [v.copy() for v in p]
    for _ in range(it):
        q = [v.copy() for v in p]
        for i in range(1, len(p) - 1):
            a, b = max(0, i - n), min(len(p), i + n + 1); q[i] = sum((p[k] for k in range(a, b)), V()) / (b - a)
        p = q
    return p
def spline(cp, passo=0.25):
    P = [V((0, y, z)) for y, z in cp]; P = [P[0]] + P + [P[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]; n = max(2, int((p2 - p1).length / passo))
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-2]); return [(v.y, v.z) for v in out]
def trechos(res, minimo=4):
    out, cur = [], []
    for p in res:
        if p is None:
            if len(cur) >= minimo: out.append(cur)
            cur = []
        else: cur.append(p)
    if len(cur) >= minimo: out.append(cur)
    return [suavizar(t) for t in out]
X0 = -0.045 * 12.7                                           # meio do corpo em x (o modelo e um pouco deslocado)
def projetar_lado(yz, lado):
    """perfil (y, z) -> pele vista do lado (lado +1 = +X = D, -1 = E), pegando a primeira superficie do corpo"""
    res = []
    for y, z in yz:
        hit, nrm, i_, d = BVH.ray_cast(V((X0 + lado * 30, y, z)), V((-lado, 0, 0)), 60)
        res.append(hit + nrm * FOLGA if hit is not None and (hit.x - X0) * lado > 0.8 else None)
    return trechos(res)
def ao_longo(pontos, dir_fora, passo=0.25, alcance=4.0):
    """amostra a cadeia de pontos (eixo do osso) e projeta na pele a partir de fora (dir_fora: vetor ou funcao(P, T))"""
    am = []
    for a, b in zip(pontos, pontos[1:]):
        k = max(2, int((b - a).length / passo)); am += [a.lerp(b, j / k) for j in range(k)]
    am.append(pontos[-1]); res = []
    for i, P in enumerate(am):
        T = (am[min(i + 1, len(am) - 1)] - am[max(i - 1, 0)]).normalized()
        d = dir_fora(P, T) if callable(dir_fora) else dir_fora
        d = (d - T * d.dot(T)).normalized(); hit, nrm, i_, dd = BVH.ray_cast(P + d * alcance, -d, alcance)
        res.append(hit + nrm * FOLGA if hit is not None else None)
    return trechos(res)
LINHAS = []                                                   # (pontos, cor 0=roxo 1=vermelho, grupo de pulso, u0, u1)
y_omb, y_quad = osso("BracoE")[0].y, osso("CoxaE")[0].y
for lado in (1, -1):                                          # perfil do tronco (frente = -Y); z em studs
    dorso = spline([(y_omb + 1.0, 12.4), (y_omb + 4.0, 11.9), (0.0, 11.6), (y_quad - 1.5, 11.8), (y_quad + 1.2, 11.2), (y_quad + 2.6, 10.2)])
    flanco = spline([(y_omb + 0.8, 10.2), (y_omb + 3.0, 9.0), (0.0, 8.6), (y_quad - 2.0, 8.9), (y_quad, 9.6), (y_quad + 1.4, 8.6), (y_quad + 1.0, 6.8)])
    for t in projetar_lado(dorso, lado): LINHAS.append((t, 0.0, "corpo", 0.15, 0.85))
    for t in projetar_lado(flanco, lado): LINHAS.append((t, 1.0, "corpo", 0.20, 0.95))
    sd = "D" if lado > 0 else "E"; fora = V((lado, -0.35, 0))
    for cadeia, cor in ((["Braco", "Antebraco", "Mao"], 1.0), (["Coxa", "Canela", "Pe"], 0.0)):
        pts = [osso(n + sd)[0] for n in cadeia] + [osso(cadeia[-1] + sd)[1]]
        for t in ao_longo(pts, fora): LINHAS.append((t, cor, "corpo", 0.35, 1.0))
pts = [osso("Cauda1")[0]] + [osso(n)[1] for n in ("Cauda1", "Cauda2", "Cauda3")]
for t in ao_longo(pts, V((0, 0, 1)), alcance=3.0): LINHAS.append((t, 0.0, "corpo", 0.85, 1.0))
for k in "CED":                                               # pescocos: alto e lado de fora; cranio: do pescoco ate entre as orelhas
    hb, tb = osso("Cabeca" + k); f = (tb - hb); f.z = 0; f.normalize(); s = f.cross(V((0, 0, 1))).normalized()
    # r3: linha do ALTO do pescoco subindo ate a nuca (para atras das orelhas: rosto limpo) + linha do lado de FORA do pescoco
    # r4: o osso Cabeca comeca na altura dos olhos -> as linhas param 1,3 stud ATRAS dele (rosto limpo: nada na testa nem nos olhos)
    fim = hb - f * 1.3
    cad = [osso("Pescoco%s1" % k)[0], osso("Pescoco%s1" % k)[1], fim.lerp(osso("Pescoco%s1" % k)[1], 0.5), fim]
    for t in ao_longo(cad, lambda P, T: V((0, 0, 1)) - f * 0.3, alcance=9.0): LINHAS.append((t, 1.0, k, 0.0, 0.6))
    fora = s if (s.x > 0) == (k == "D") else -s
    lados = (s, -s) if k == "C" else (fora,)
    for sl in lados:
        for t in ao_longo(cad, sl + V((0, 0, 0.25)), alcance=9.0): LINHAS.append((t, 0.0, k, 0.05, 0.55))
print("LINHAS", len(LINHAS), "pontos", sum(len(l[0]) for l in LINHAS), flush=True)

def fita(pl, largura):
    vs, fs, n = [], [], len(pl)
    for i, p in enumerate(pl):
        T = (pl[min(i + 1, n - 1)] - pl[max(i - 1, 0)]).normalized()
        loc, nrm, idx, dist = BVH.find_nearest(p); N = nrm if nrm is not None else V((0, 0, 1))
        W = T.cross(N).normalized(); afina = min(1.0, i / 4.0, (n - 1 - i) / 4.0); w = largura * (0.35 + 0.65 * afina) / 2
        vs += [p + W * w, p - W * w]
        if i: k_ = 2 * i; fs.append((k_ - 2, k_ - 1, k_ + 1, k_))
    return vs, fs
GRUPOS = {"corpo": 0, "C": 1, "E": 2, "D": 3}
me = bpy.data.meshes.new("Aura_Linhas"); bm = bmesh.new()
lu = bm.verts.layers.float.new("u"); lc = bm.verts.layers.float.new("cor"); lg = bm.verts.layers.float.new("grupo")
for pts, cor, grupo, u0, u1 in LINHAS:
    vs, fs = fita(pts, LARG); vv = []
    for i, v in enumerate(vs):
        bv = bm.verts.new(v); u = u0 + (u1 - u0) * (i // 2) / max(1, len(pts) - 1)
        bv[lu] = u; bv[lc] = cor; bv[lg] = GRUPOS[grupo]; vv.append(bv)
    for f_ in fs:
        try: bm.faces.new([vv[j] for j in f_])
        except ValueError: pass
bm.normal_update(); bm.to_mesh(me); bm.free()
AURA = bpy.data.objects.new("Aura_Linhas", me); sc.collection.objects.link(AURA)
for nm in ("u", "cor", "grupo"):                               # atributos de ponto acessiveis no material
    pass
# A1 r2: as fitas soltas quebravam e sumiam no pelo irregular -> as linhas sao ASSADAS na UV da pele (metodo aprovado no Lobo
# Artico r7/r8). Duas imagens por malha: _AuraMascara (onde ha linha) e _AuraDados (R = u ao longo da linha, G = grupo/3 para a
# fase da cabeca, B = cor 0 roxo / 1 brasa). A pele calcula o pulso a partir delas.
def cor_lin(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)
ROXO, BRASA = cor_lin("8a2be2"), cor_lin("ff4a1c")
RES = 1024
mf = bpy.data.materials.new("Bake_Fita"); mf.use_nodes = True; nf = mf.node_tree; nf.nodes.clear()
of = nf.nodes.new("ShaderNodeOutputMaterial"); ef = nf.nodes.new("ShaderNodeEmission"); ef.inputs["Strength"].default_value = 1.0
cmb = nf.nodes.new("ShaderNodeCombineColor")
for i_, nm in enumerate(("u", "grupo", "cor")):
    a_ = nf.nodes.new("ShaderNodeAttribute"); a_.attribute_name = nm
    if nm == "grupo":
        d_ = nf.nodes.new("ShaderNodeMath"); d_.operation = "DIVIDE"; d_.inputs[1].default_value = 3.0
        nf.links.new(a_.outputs["Fac"], d_.inputs[0]); nf.links.new(d_.outputs[0], cmb.inputs[i_])
    else: nf.links.new(a_.outputs["Fac"], cmb.inputs[i_])
nf.links.new(cmb.outputs[0], ef.inputs["Color"]); nf.links.new(ef.outputs[0], of.inputs[0])
AURA.data.materials.append(mf)
mb = bpy.data.materials.new("Bake_Branco"); mb.use_nodes = True; nb = mb.node_tree; nb.nodes.clear()
ob_ = nb.nodes.new("ShaderNodeOutputMaterial"); eb = nb.nodes.new("ShaderNodeEmission"); eb.inputs["Color"].default_value = (1, 1, 1, 1)
nb.links.new(eb.outputs[0], ob_.inputs[0])
sc.render.engine = "CYCLES"; sc.cycles.samples = 2; sc.cycles.device = "CPU"
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.45; bk.max_ray_distance = 0.9; bk.margin = 3
IMGS = {}
def assar(pele, sufixo):
    imgs = {}
    for tipo, mat_f in (("Mascara", mb), ("Dados", mf)):
        AURA.data.materials[0] = mat_f
        img = bpy.data.images.new("T_Cerbero_%s_Aura%s" % (sufixo, tipo), RES, RES, alpha=False); img.generated_color = (0, 0, 0, 1)
        img.colorspace_settings.name = "Non-Color"
        for m in pele.data.materials:
            n_ = m.node_tree.nodes.new("ShaderNodeTexImage"); n_.image = img; n_.name = "bake_" + tipo
            for x in m.node_tree.nodes: x.select = False
            n_.select = True; m.node_tree.nodes.active = n_
        for o in sc.objects: o.select_set(False)
        AURA.select_set(True); pele.select_set(True); bpy.context.view_layer.objects.active = pele
        bpy.ops.object.bake(type="EMIT")
        img.filepath_raw = os.path.join(OUT, img.name + ".png"); img.file_format = "PNG"; img.save(); imgs[tipo] = img
        for m in pele.data.materials: m.node_tree.nodes.remove(m.node_tree.nodes["bake_" + tipo])
    return imgs
IMGS["Corpo"] = assar(CORPO, "Corpo"); IMGS["Cabecas"] = assar(CAB, "Cabecas")
import numpy as np
for k, d in IMGS.items():
    px = np.array(d["Mascara"].pixels[:], dtype=np.float32).reshape(RES, RES, 4)
    print("MASCARA", k, "pixels com linha", int((px[..., 0] > 0.5).sum()), flush=True)
AURA.hide_render = True; AURA.hide_set(True)
# ------------------------------------------------------------------ pele: pulso lento da aura + olhos em brasa + pontas do pelo
def no(nt, tipo, **kw):
    n_ = nt.nodes.new(tipo)
    for k, v in kw.items(): setattr(n_, k, v)
    return n_
def op(nt, oper, a, b=None):
    n_ = nt.nodes.new("ShaderNodeMath"); n_.operation = oper
    for i_, x in enumerate((a, b)):
        if x is None: continue
        if isinstance(x, (int, float)): n_.inputs[i_].default_value = x
        else: nt.links.new(x, n_.inputs[i_])
    return n_.outputs[0]
def aura_na_pele(pele, chave, olhos):
    for m in pele.data.materials:
        nt = m.node_tree; b_ = nt.nodes["Principled BSDF"]
        tex = next(x for x in nt.nodes if x.type == "TEX_IMAGE" and x.image and x.image.name.endswith("_Cor"))
        tm = no(nt, "ShaderNodeTexImage", image=IMGS[chave]["Mascara"]); td = no(nt, "ShaderNodeTexImage", image=IMGS[chave]["Dados"])
        sd = no(nt, "ShaderNodeSeparateColor"); nt.links.new(td.outputs["Color"], sd.inputs[0])
        tv = no(nt, "ShaderNodeValue", name="tempo").outputs[0]
        fase = op(nt, "MULTIPLY", sd.outputs[1], 0.93)                     # G = grupo/3 -> 0 corpo, 0,31 C, 0,62 E, 0,93 D
        arg = op(nt, "SUBTRACT", op(nt, "SUBTRACT", op(nt, "DIVIDE", tv, 1.8), op(nt, "MULTIPLY", sd.outputs[0], 0.9)), fase)
        pulso = op(nt, "ADD", 0.45, op(nt, "MULTIPLY", op(nt, "SINE", op(nt, "MULTIPLY", arg, 2 * math.pi)), 0.40))
        linha = op(nt, "MULTIPLY", op(nt, "MULTIPLY", tm.outputs["Color"], pulso), no(nt, "ShaderNodeValue", name="forca_linha").outputs[0])
        nt.nodes["forca_linha"].outputs[0].default_value = 4.0                  # r3: mais discreto
        mixc = no(nt, "ShaderNodeMix", data_type="RGBA"); mixc.inputs["A"].default_value = ROXO; mixc.inputs["B"].default_value = BRASA
        nt.links.new(sd.outputs[2], mixc.inputs["Factor"])
        # olhos (vermelho saturado da textura) em brasa discreta; Pelagem Infernal: borda bem fraca
        sep = no(nt, "ShaderNodeSeparateColor"); nt.links.new(tex.outputs["Color"], sep.inputs[0])
        sat = op(nt, "SUBTRACT", sep.outputs[0], op(nt, "MAXIMUM", sep.outputs[1], sep.outputs[2]))
        olho = no(nt, "ShaderNodeMapRange"); olho.inputs["From Min"].default_value = 0.22; olho.inputs["From Max"].default_value = 0.40
        nt.links.new(sat, olho.inputs["Value"])
        fr = no(nt, "ShaderNodeLayerWeight"); fr.inputs["Blend"].default_value = 0.08
        borda = op(nt, "MULTIPLY", op(nt, "POWER", fr.outputs["Facing"], 4.0), 0.25)
        brasa = op(nt, "ADD", op(nt, "MULTIPLY", olho.outputs[0], 2.5 if olhos else 0.8), borda)
        # emissao = linha * cor da linha + brasa * cor brasa
        e1 = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); e1.inputs["Factor"].default_value = 1.0
        nt.links.new(mixc.outputs["Result"], e1.inputs["A"]); cl = no(nt, "ShaderNodeCombineColor")
        for i_ in range(3): nt.links.new(linha, cl.inputs[i_])
        nt.links.new(cl.outputs[0], e1.inputs["B"])
        e2 = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); e2.inputs["Factor"].default_value = 1.0
        e2.inputs["A"].default_value = BRASA; cb_ = no(nt, "ShaderNodeCombineColor")
        for i_ in range(3): nt.links.new(brasa, cb_.inputs[i_])
        nt.links.new(cb_.outputs[0], e2.inputs["B"])
        soma = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="ADD"); soma.inputs["Factor"].default_value = 1.0
        nt.links.new(e1.outputs["Result"], soma.inputs["A"]); nt.links.new(e2.outputs["Result"], soma.inputs["B"])
        nt.links.new(soma.outputs["Result"], b_.inputs["Emission Color"]); b_.inputs["Emission Strength"].default_value = 1.0
aura_na_pele(CORPO, "Corpo", False); aura_na_pele(CAB, "Cabecas", True)
sc.render.engine = "BLENDER_EEVEE"
rig.data.pose_position = "POSE"
for pb in rig.pose.bones:
    for c in pb.constraints: c.mute = True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_Aura_A1.blend"))
json.dump({"linhas": len(LINHAS), "tris": sum(len(p.vertices) - 2 for p in AURA.data.polygons), "largura": round(LARG, 3),
           "pulso_s": 1.8, "fases": {"corpo": 0, "C": 0.31, "E": 0.62, "D": 0.93}, "cores": {"roxo": "#8a2be2", "brasa": "#ff4a1c"}},
          open(os.path.join(OUT, "aura_A1.json"), "w"), indent=1)
print("AURA_A1_OK", flush=True)
