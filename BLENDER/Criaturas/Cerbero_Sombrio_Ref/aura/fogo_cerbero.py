"""Aura de FOGO do Cerbero Sombrio - A2 (18/11): pedido do usuario "algo como fogo, como na referencia"
(aura/ref/referencia_fogo_usuario_18-11.webp: chamas laranja/amarelas subindo da juba, pescocos, dorso e cauda; labaredas no
pelo; olhos e bocas incandescentes). DIVERGE da v6.2 §5.1/§5.9h (linhas discretas roxo/brasa, fora do corpo so vento): vale a
referencia do usuario. A A1 (linhas) fica guardada.
Duas camadas, cada uma ja pensada para o Roblox:
  1) PELE: regioes de fogo (juba, peito, dorso, cauda, traseira das pernas) ASSADAS na UV como mascara suave; na previa, o
     shader faz labaredas animadas subindo (no Roblox: EmissiveMask + cintilacao do EmissiveStrength);
  2) CHAMAS POR CIMA: planos cruzados com chama animada, presos aos ossos (previa dos ParticleEmitters que no Roblox ficam em
     Attachments nos mesmos ossos: OssoChama/OffsetOsso no aura_A2.json).
Olhos incandescentes e interior das bocas (gengiva/lingua) em brasa. Valores = [A TESTAR].
Uso: blender -b -t 4 ../rig/clipes_L3/CR_Cerbero_Anim.blend -P fogo_cerbero.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.render.threads_mode = "FIXED"; sc.render.threads = 4; rnd = random.Random(7)
rig = bpy.data.objects["Cerbero_Rig"]
for pb in rig.pose.bones:
    for c in pb.constraints: c.mute = True
if rig.animation_data: rig.animation_data.action = None
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
CAB, CORPO, BOCA = (bpy.data.objects[n] for n in ("Cerbero_Cabecas", "Cerbero_Corpo", "Cerbero_Bocas"))
def bvh_de(objs):
    dg = bpy.context.evaluated_depsgraph_get(); bm = bmesh.new()
    for o in objs:
        me = o.evaluated_get(dg).to_mesh(); tmp = bmesh.new(); tmp.from_mesh(me); tmp.transform(o.matrix_world)
        m2 = bpy.data.meshes.new("tmp"); tmp.to_mesh(m2); tmp.free(); bm.from_mesh(m2); bpy.data.meshes.remove(m2); o.evaluated_get(dg).to_mesh_clear()
    t = BVHTree.FromBMesh(bm); bm.free(); return t
BVH = bvh_de([CAB, CORPO])
def osso(n): b = rig.data.bones[n]; return b.head_local.copy(), b.tail_local.copy()
def suavizar(p, n=2, it=3):
    p = [v.copy() for v in p]
    for _ in range(it):
        q = [v.copy() for v in p]
        for i in range(1, len(p) - 1):
            a, b = max(0, i - n), min(len(p), i + n + 1); q[i] = sum((p[k] for k in range(a, b)), V()) / (b - a)
        p = q
    return p
def ao_longo(pontos, dir_fora, passo=0.3, alcance=9.0):
    am = []
    for a, b in zip(pontos, pontos[1:]):
        k = max(2, int((b - a).length / passo)); am += [a.lerp(b, j / k) for j in range(k)]
    am.append(pontos[-1]); res = []
    for i, P in enumerate(am):
        T = (am[min(i + 1, len(am) - 1)] - am[max(i - 1, 0)]).normalized()
        d = dir_fora(P, T) if callable(dir_fora) else dir_fora; d = (d - T * d.dot(T)).normalized()
        hit, nrm, i_, dd = BVH.ray_cast(P + d * alcance, -d, alcance)
        res.append((hit + nrm * 0.10, nrm) if hit is not None else None)
    out, cur = [], []
    for r in res:
        if r is None:
            if len(cur) >= 4: out.append(cur)
            cur = []
        else: cur.append(r)
    if len(cur) >= 4: out.append(cur)
    return out
X0 = -0.045 * 12.7
# ------------------------------------------------------------------ 1) regioes de fogo na pele (faixas largas -> mascara suave)
FAIXAS = []                                                  # (trecho, largura)
for k in "CED":
    hb, tb = osso("Cabeca" + k); f = tb - hb; f.z = 0; f.normalize(); s = f.cross(V((0, 0, 1))).normalized()
    fim = hb - f * 1.3                                        # rosto limpo: a juba pega fogo ate a nuca
    cad = [osso("Pescoco%s1" % k)[0], osso("Pescoco%s1" % k)[1], fim]
    for d in (V((0, 0, 1)) - f * 0.3, s + V((0, 0, 0.4)), -s + V((0, 0, 0.4))):
        for t in ao_longo(cad, d): FAIXAS.append((t, 2.2))
y_omb, y_quad = osso("BracoE")[0].y, osso("CoxaE")[0].y
dorso = [V((X0, y_omb - 1.0, 12)), V((X0, 0, 11)), V((X0, y_quad + 1.5, 10.5))]
for t in ao_longo(dorso, V((0, 0, 1)), alcance=12): FAIXAS.append((t, 3.0))
peito = [osso("Coluna3")[1] + V((0, -2.0, 0)), V((X0, y_omb - 3.0, 7.0))]
for t in ao_longo(peito, V((0, -1, 0.2)), alcance=12): FAIXAS.append((t, 2.6))
pts = [osso("Cauda1")[0]] + [osso(n)[1] for n in ("Cauda1", "Cauda2", "Cauda3")]
for t in ao_longo(pts, V((0, 0, 1)), alcance=4): FAIXAS.append((t, 2.0))
for sd, lado in (("E", -1), ("D", 1)):
    for cadeia, d in ((["Braco", "Antebraco", "Mao"], V((lado * 0.4, 1, 0))), (["Coxa", "Canela", "Pe"], V((lado * 0.4, 1, 0)))):
        pts = [osso(n + sd)[0] for n in cadeia]
        for t in ao_longo(pts, d): FAIXAS.append((t, 1.0))
print("FAIXAS", len(FAIXAS), flush=True)
me = bpy.data.meshes.new("Fogo_Faixas"); bm = bmesh.new()
for t, larg in FAIXAS:
    pl = suavizar([p for p, n in t]); vv = []
    for i, p in enumerate(pl):
        T = (pl[min(i + 1, len(pl) - 1)] - pl[max(i - 1, 0)]).normalized(); N = t[i][1]
        W = T.cross(N).normalized(); w = larg / 2
        vv += [bm.verts.new(p + W * w), bm.verts.new(p - W * w)]
        if i:
            try: bm.faces.new((vv[-4], vv[-3], vv[-1], vv[-2]))
            except ValueError: pass
bm.normal_update(); bm.to_mesh(me); bm.free()
FX = bpy.data.objects.new("Fogo_Faixas", me); sc.collection.objects.link(FX)
mb = bpy.data.materials.new("Bake_Branco"); mb.use_nodes = True; nb = mb.node_tree; nb.nodes.clear()
eb = nb.nodes.new("ShaderNodeEmission"); eb.inputs["Color"].default_value = (1, 1, 1, 1); ob_ = nb.nodes.new("ShaderNodeOutputMaterial")
nb.links.new(eb.outputs[0], ob_.inputs[0]); FX.data.materials.append(mb)
sc.render.engine = "CYCLES"; sc.cycles.samples = 2; sc.cycles.device = "CPU"
bk = sc.render.bake; bk.use_selected_to_active = True; bk.cage_extrusion = 0.8; bk.max_ray_distance = 1.6; bk.margin = 4
RES = 1024; MASC = {}
def borrar(img, r=6):
    px = np.array(img.pixels[:], dtype=np.float32).reshape(RES, RES, 4); m = px[..., 0]
    for _ in range(r):
        m = (m + np.roll(m, 1, 0) + np.roll(m, -1, 0) + np.roll(m, 1, 1) + np.roll(m, -1, 1)) / 5.0
    px[..., 0] = px[..., 1] = px[..., 2] = np.clip(m * 1.4, 0, 1); img.pixels[:] = px.ravel()
for pele, chave in ((CORPO, "Corpo"), (CAB, "Cabecas")):
    img = bpy.data.images.new("T_Cerbero_%s_FogoMascara" % chave, RES, RES, alpha=False); img.generated_color = (0, 0, 0, 1)
    img.colorspace_settings.name = "Non-Color"
    for m in pele.data.materials:
        n_ = m.node_tree.nodes.new("ShaderNodeTexImage"); n_.image = img; n_.name = "bake_fogo"
        for x in m.node_tree.nodes: x.select = False
        n_.select = True; m.node_tree.nodes.active = n_
    for o in sc.objects: o.select_set(False)
    FX.select_set(True); pele.select_set(True); bpy.context.view_layer.objects.active = pele
    bpy.ops.object.bake(type="EMIT"); borrar(img)
    img.filepath_raw = os.path.join(OUT, img.name + ".png"); img.file_format = "PNG"; img.save(); MASC[chave] = img
    for m in pele.data.materials: m.node_tree.nodes.remove(m.node_tree.nodes["bake_fogo"])
    print("MASCARA_FOGO", chave, round(float(np.array(img.pixels[:]).reshape(-1, 4)[:, 0].mean()), 4), flush=True)
FX.hide_render = True; FX.hide_set(True)
# ------------------------------------------------------------------ cores (linear) e utilitarios de nos
def lin(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)
C_ESC, C_VERM, C_LAR, C_AMAR = lin("3a0600"), lin("c41e00"), lin("ff6a00"), lin("ffd23a")
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
def rampa_fogo(nt, fator):
    cr = no(nt, "ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0, 0, 0, 1); el[1].position, el[1].color = 1.0, C_AMAR
    for pos, c in ((0.25, C_ESC), (0.5, C_VERM), (0.75, C_LAR)):
        e = el.new(pos); e.color = c
    nt.links.new(fator, cr.inputs[0]); return cr.outputs[0]
# ------------------------------------------------------------------ 2) pele: labaredas animadas subindo + olhos/boca incandescentes
def fogo_na_pele(pele, chave, olhos):
    for m in pele.data.materials:
        nt = m.node_tree; b_ = nt.nodes["Principled BSDF"]
        tex = next(x for x in nt.nodes if x.type == "TEX_IMAGE" and x.image and x.image.name.endswith("_Cor"))
        tm = no(nt, "ShaderNodeTexImage", image=MASC[chave]); tv = no(nt, "ShaderNodeValue", name="tempo").outputs[0]
        tc = no(nt, "ShaderNodeTexCoord"); mp = no(nt, "ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (0.45, 0.45, 0.15)              # esticado na vertical: linguas de fogo
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        sobe = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", tv, -0.55), sobe.inputs["Z"])
        soma_v = no(nt, "ShaderNodeVectorMath", operation="ADD"); nt.links.new(mp.outputs[0], soma_v.inputs[0]); nt.links.new(sobe.outputs[0], soma_v.inputs[1])
        nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 3.0; nz.inputs["Detail"].default_value = 3.0
        nz.inputs["Distortion"].default_value = 0.6; nt.links.new(soma_v.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "MULTIPLY", tv, 0.6), nz.inputs["W"])
        # r2: o fogo segue os FIOS do pelo (luminancia da textura) e cintila subindo; antes saia em manchas chapadas
        lum = no(nt, "ShaderNodeRGBToBW"); nt.links.new(tex.outputs["Color"], lum.inputs[0])
        fio = no(nt, "ShaderNodeMapRange"); fio.inputs["From Min"].default_value = 0.015; fio.inputs["From Max"].default_value = 0.10
        nt.links.new(lum.outputs[0], fio.inputs["Value"])
        cint = no(nt, "ShaderNodeMapRange"); cint.inputs["From Min"].default_value = 0.38; cint.inputs["From Max"].default_value = 0.72
        nt.links.new(nz.outputs["Fac"], cint.inputs["Value"])
        chama = op(nt, "MULTIPLY", op(nt, "MULTIPLY", tm.outputs["Color"], fio.outputs[0]), op(nt, "ADD", 0.25, cint.outputs[0]))
        fat = no(nt, "ShaderNodeMapRange"); fat.inputs["From Min"].default_value = 0.05; fat.inputs["From Max"].default_value = 0.85
        nt.links.new(chama, fat.inputs["Value"])
        cor_ch = rampa_fogo(nt, fat.outputs[0])
        forca = op(nt, "MULTIPLY", fat.outputs[0], no(nt, "ShaderNodeValue", name="forca_pele").outputs[0])
        nt.nodes["forca_pele"].outputs[0].default_value = 3.2               # r2: cores saturadas (9 estourava em branco)
        # olhos: vermelho saturado da textura -> amarelo-laranja forte; fissuras do corpo: brasa
        sep = no(nt, "ShaderNodeSeparateColor"); nt.links.new(tex.outputs["Color"], sep.inputs[0])
        sat = op(nt, "SUBTRACT", sep.outputs[0], op(nt, "MAXIMUM", sep.outputs[1], sep.outputs[2]))
        ol = no(nt, "ShaderNodeMapRange"); ol.inputs["From Min"].default_value = 0.20; ol.inputs["From Max"].default_value = 0.36
        nt.links.new(sat, ol.inputs["Value"]); kol = op(nt, "MULTIPLY", ol.outputs[0], 14.0 if olhos else 3.0)
        e1 = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); e1.inputs["Factor"].default_value = 1.0
        nt.links.new(cor_ch, e1.inputs["A"]); c1 = no(nt, "ShaderNodeCombineColor")
        for i_ in range(3): nt.links.new(forca, c1.inputs[i_])
        nt.links.new(c1.outputs[0], e1.inputs["B"])
        e2 = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); e2.inputs["Factor"].default_value = 1.0
        e2.inputs["A"].default_value = C_LAR; c2 = no(nt, "ShaderNodeCombineColor")
        for i_ in range(3): nt.links.new(kol, c2.inputs[i_])
        nt.links.new(c2.outputs[0], e2.inputs["B"])
        sm = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="ADD"); sm.inputs["Factor"].default_value = 1.0
        nt.links.new(e1.outputs["Result"], sm.inputs["A"]); nt.links.new(e2.outputs["Result"], sm.inputs["B"])
        nt.links.new(sm.outputs["Result"], b_.inputs["Emission Color"]); b_.inputs["Emission Strength"].default_value = 1.0
fogo_na_pele(CORPO, "Corpo", False); fogo_na_pele(CAB, "Cabecas", True)
for m in BOCA.data.materials:                                 # interior da boca em brasa (gengiva e lingua; dentes nao)
    nt = m.node_tree; b_ = nt.nodes["Principled BSDF"]; at = no(nt, "ShaderNodeAttribute", attribute_name="papel")
    sep = no(nt, "ShaderNodeSeparateColor"); nt.links.new(at.outputs["Color"], sep.inputs[0])
    vermelho = op(nt, "SUBTRACT", sep.outputs[0], sep.outputs[1]); k_ = op(nt, "MULTIPLY", op(nt, "MAXIMUM", op(nt, "SUBTRACT", vermelho, 0.15), 0.0), 25.0)
    b_.inputs["Emission Color"].default_value = C_LAR; nt.links.new(k_, b_.inputs["Emission Strength"])
# ------------------------------------------------------------------ 3) chamas por cima: planos cruzados presos aos ossos
mc = bpy.data.materials.new("M_Chama"); mc.use_nodes = True; nt = mc.node_tree; nt.nodes.clear()
out = no(nt, "ShaderNodeOutputMaterial"); em = no(nt, "ShaderNodeEmission"); trn = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
nt.links.new(trn.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
tv = no(nt, "ShaderNodeValue", name="tempo").outputs[0]; uv = no(nt, "ShaderNodeTexCoord").outputs["UV"]; sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(uv, sp.inputs[0])
oi = no(nt, "ShaderNodeObjectInfo")
u_c = op(nt, "ABSOLUTE", op(nt, "SUBTRACT", sp.outputs["X"], 0.5)); v_ = sp.outputs["Y"]
# lingua de fogo: larga embaixo, fina em cima, ondulando; ruido sobe com o tempo
vec = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", sp.outputs["X"], 2.0), vec.inputs["X"])
nt.links.new(op(nt, "SUBTRACT", op(nt, "MULTIPLY", v_, 1.6), op(nt, "MULTIPLY", tv, 2.2)), vec.inputs["Y"])
nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 3.2; nz.inputs["Detail"].default_value = 3.0; nz.inputs["Distortion"].default_value = 0.8
nt.links.new(vec.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "ADD", op(nt, "MULTIPLY", oi.outputs["Random"], 10.0), op(nt, "MULTIPLY", tv, 0.8)), nz.inputs["W"])
larg = op(nt, "MULTIPLY", op(nt, "POWER", op(nt, "SUBTRACT", 1.0, v_), 0.8), 0.48)                      # meia largura da lingua por altura
ond = op(nt, "MULTIPLY", op(nt, "SUBTRACT", nz.outputs["Fac"], 0.5), op(nt, "MULTIPLY", v_, 1.1))     # r2: lingua ondula mais no alto
forma = op(nt, "SUBTRACT", larg, op(nt, "ABSOLUTE", op(nt, "SUBTRACT", u_c, ond)))
dens = op(nt, "MULTIPLY", op(nt, "MULTIPLY", forma, 7.0), op(nt, "ADD", 0.4, nz.outputs["Fac"]))
dens = op(nt, "MINIMUM", op(nt, "MAXIMUM", dens, 0.0), 1.0)
dens = op(nt, "MULTIPLY", dens, op(nt, "POWER", op(nt, "MINIMUM", op(nt, "MULTIPLY", v_, 2.6), 1.0), 1.6))   # r3: base bem suave (antes cortava reto)
nt.links.new(rampa_fogo(nt, dens), em.inputs["Color"])
nt.links.new(op(nt, "MULTIPLY", dens, no(nt, "ShaderNodeValue", name="forca_chama").outputs[0]), em.inputs["Strength"])
nt.nodes["forca_chama"].outputs[0].default_value = 2.6
nt.links.new(op(nt, "MINIMUM", op(nt, "MULTIPLY", dens, 1.6), 1.0), mx.inputs[0])
try: mc.surface_render_method = "BLENDED"
except Exception: pass
CHAMAS = []
def chama(base, osso_nome, alt, larg, incl=None):
    if incl is None: incl = V((rnd.uniform(-0.25, 0.25), rnd.uniform(0.2, 0.6), 1))      # r2: inclinacao variada
    """dois planos cruzados (lingua de fogo) presos ao osso; incl = direcao de subida (para tras, como o vento do movimento)"""
    up = incl.normalized(); a = up.orthogonal().normalized(); b_ = up.cross(a).normalized(); bmc = bmesh.new(); uvl = bmc.loops.layers.uv.new()
    for lat in (a, b_):
        vs = [bmc.verts.new(-lat * larg / 2), bmc.verts.new(lat * larg / 2), bmc.verts.new(lat * larg / 2 + up * alt), bmc.verts.new(-lat * larg / 2 + up * alt)]
        f_ = bmc.faces.new(vs)
        for lp, uvv in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uvv
    mm = bpy.data.meshes.new("Chama"); bmc.to_mesh(mm); bmc.free()
    o = bpy.data.objects.new("Chama_%02d" % len(CHAMAS), mm); sc.collection.objects.link(o); o.data.materials.append(mc)
    o.parent = rig; o.parent_type = "BONE"; o.parent_bone = osso_nome; o.matrix_world = Matrix.Translation(base)
    CHAMAS.append({"nome": o.name, "osso": osso_nome, "base": [round(c, 3) for c in base], "altura": alt, "largura": larg})
def topo(P, d=V((0, 0, 1)), alcance=10):
    hit, nrm, i_, dd = BVH.ray_cast(P + d * alcance, -d, alcance); return hit
for k in "CED":                                               # juba: 4 chamas por pescoco + 1 na nuca
    for j, u in enumerate((0.15, 0.4, 0.65, 0.9)):
        a_, b2 = osso("Pescoco%s1" % k)[0], osso("Cabeca" + k)[0]; P = a_.lerp(b2, u)
        p = topo(P + V((rnd.uniform(-0.4, 0.4), rnd.uniform(-0.4, 0.4), 0)))
        if p: chama(p - V((0, 0, 1.0)), "Pescoco%s%d" % (k, 1 if u < 0.5 else 2), rnd.uniform(3.6, 5.4), rnd.uniform(2.4, 3.2))
        if p: chama(p + V((rnd.uniform(-0.8, 0.8), rnd.uniform(-0.5, 0.5), -0.9)), "Pescoco%s%d" % (k, 1 if u < 0.5 else 2), rnd.uniform(2.0, 3.0), rnd.uniform(1.6, 2.2))
for y in np.linspace(y_omb - 0.5, y_quad + 1.0, 6):            # dorso (a sela vai por cima da armadura: chamas nas bordas)
    for lado in (-1, 1):
        p = topo(V((X0 + lado * 1.6, y, 12)))
        if p: chama(p - V((0, 0, 0.7)), "Coluna1" if y > 0 else "Coluna2", rnd.uniform(2.0, 3.0), rnd.uniform(1.2, 1.6))
for nm in ("Cauda1", "Cauda2", "Cauda3"):
    p = topo(osso(nm)[1], alcance=4)
    if p: chama(p - V((0, 0, 0.6)), nm, rnd.uniform(2.4, 3.4), rnd.uniform(1.2, 1.6), V((0, 0.8, 1)))
print("CHAMAS", len(CHAMAS), flush=True)
sc.render.engine = "BLENDER_EEVEE"; rig.data.pose_position = "POSE"
for pb in rig.pose.bones:
    for c in pb.constraints: c.mute = True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_Fogo_A2.blend"))
json.dump({"faixas_de_fogo": len(FAIXAS), "chamas": CHAMAS, "cores": {"escuro": "#3a0600", "vermelho": "#c41e00", "laranja": "#ff6a00", "amarelo": "#ffd23a"},
           "roblox_sugerido": {"pele": "EmissiveMask = T_Cerbero_*_FogoMascara + cintilacao do EmissiveStrength",
                               "chamas": "ParticleEmitter de fogo (flipbook) num Attachment por chama, no osso indicado, %d no total [A TESTAR; celular: metade]" % len(CHAMAS)}},
          open(os.path.join(OUT, "aura_A2.json"), "w"), indent=1, ensure_ascii=False)
print("FOGO_A2_OK", flush=True)
