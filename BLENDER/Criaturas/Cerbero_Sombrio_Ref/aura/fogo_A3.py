"""Aura de FOGO A3 (18/11) - pedido "corrigir a aura de fogo A2". Base: copia de aura/CR_Cerbero_Fogo_A2.blend (A2 intacta).
Problemas da A2: labaredas em colunas verticais separadas (planos cruzados), amarelo tomando a chama toda, peito/flancos/patas
escuros. A3:
  1) PELE (cobertura primeiro com material): peso de fogo POR VERTICE ("fogo"), pelas regioes do rig: juba e nucas das 3
     cabecas (parando atras dos olhos), peito, ombros, dorso, flancos (barriga escura), cauda; filetes finos na face EXTERNA das
     pernas. O shader acende os fios do pelo com linguas que sobem e cintilam; rampa brasa (base) -> laranja -> amarelo so nos
     pontos mais quentes. Pelo escuro, focinhos, placas e patas continuam legiveis.
  2) CHAMAS por cima so onde a silhueta pede (juba, dorso, ponta da cauda, ombros): linguas UNICAS viradas para a camera
     (como o ParticleEmitter do Roblox) -> sem aspecto de planos cruzados; curvas e irregulares, alturas e ritmos diferentes;
     em Repouso sobem e ondulam, ao andar inclinam para tras (rotacao "andar" guardada em cada chama).
  3) Olhos em brasa; boca acesa por dentro (gengiva/lingua), dentes visiveis.
Valores = [A TESTAR]. Uso: blender -b -t 4 CR_Cerbero_Fogo_A2.blend -P fogo_A3.py -- <saida_dir>"""
import bpy, bmesh, sys, os, math, json, random
import numpy as np
from mathutils import Vector as V, Matrix
from mathutils.bvhtree import BVHTree
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene; sc.render.threads_mode = "FIXED"; sc.render.threads = 4; rnd = random.Random(11)
rig = bpy.data.objects["Cerbero_Rig"]
for o in [o for o in bpy.data.objects if o.name.startswith("Chama_")]: bpy.data.objects.remove(o)   # chamas da A2 saem
if rig.animation_data:
    rig.animation_data.action = None
    for tr in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(tr)
for pb in rig.pose.bones: pb.matrix_basis.identity()
rig.data.pose_position = "REST"; bpy.context.view_layer.update()
CAB, CORPO, BOCA = (bpy.data.objects[n] for n in ("Cerbero_Cabecas", "Cerbero_Corpo", "Cerbero_Bocas"))
BD = rig.data.bones
def osso(n): b = BD[n]; return b.head_local.copy(), b.tail_local.copy()
X0 = -0.045 * 12.7
# ------------------------------------------------------------------ 1) peso de fogo por vertice
CABS = {}
for k in "CED":
    hb, tb = osso("Cabeca" + k); f = tb - hb; f.z = 0; f.normalize(); CABS[k] = (hb, f)
def peso_fogo(o):
    nomes = {g.index: g.name for g in o.vertex_groups}; me = o.data
    at = me.attributes.get("fogo") or me.attributes.new("fogo", "FLOAT", "POINT"); vals = []
    for v in me.vertices:
        p, n = v.co, v.normal; w = 0.0
        ws = {}
        for g in v.groups:
            nm = nomes.get(g.group, "");
            for chave in ("Pescoco", "Cabeca", "Mandibula", "Coluna3", "Coluna2", "Coluna1", "Pelve", "Cauda", "Escapula", "Braco", "Coxa", "Antebraco", "Canela", "Mao", "Pe", "Dedos"):
                if nm.startswith(chave) and not (chave == "Pe" and nm.startswith(("Pelve", "Pescoco"))):
                    ws[chave] = ws.get(chave, 0.0) + g.weight; break
        juba = ws.get("Pescoco", 0.0) + ws.get("Cabeca", 0.0)
        if ws.get("Cabeca", 0.0) + ws.get("Mandibula", 0.0) > 0.05:          # cabeca: so atras dos olhos (rosto limpo)
            k = min(CABS, key=lambda k_: (p - CABS[k_][0]).length); hb, f = CABS[k]; a = (p - hb).dot(f)
            juba = juba * max(0.0, min(1.0, (-0.6 - a) / 1.2)) if a > -1.8 else juba
            juba *= (1 - min(1.0, ws.get("Mandibula", 0.0) * 3))
        tronco = ws.get("Coluna3", 0) * 1.0 + ws.get("Coluna2", 0) * 0.85 + ws.get("Coluna1", 0) * 0.8 + ws.get("Pelve", 0) * 0.8 + ws.get("Escapula", 0) * 0.9
        cauda = ws.get("Cauda", 0) * 1.0
        perna_alta = (ws.get("Braco", 0) + ws.get("Coxa", 0)) * 0.55
        perna_baixa = (ws.get("Antebraco", 0) + ws.get("Canela", 0)) * 0.35
        w = juba + tronco + cauda
        fora = max(0.0, (p.x - X0) / max(abs(p.x - X0), 1e-6) * n.x)          # face externa (lateral) das pernas
        w += (perna_alta + perna_baixa) * min(1.0, fora * 1.6)
        w *= max(0.15, min(1.0, (n.z + 0.55) / 0.8))                          # barriga/peito por baixo mais escuros
        vals.append(max(0.0, min(1.0, w)))
    at.data.foreach_set("value", vals); return float(np.mean(vals))
print("PESO_FOGO corpo", round(peso_fogo(CORPO), 3), "cabecas", round(peso_fogo(CAB), 3), flush=True)
# ------------------------------------------------------------------ cores e nos
def lin(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)
C_BRASA, C_VERM, C_LAR, C_AMAR = lin("5a0a00"), lin("c42200"), lin("ff6a00"), lin("ffe07a")
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
def rampa(nt, fator):
    """brasa na base, laranja no corpo, amarelo claro SO nos pontos mais quentes"""
    cr = no(nt, "ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0, 0, 0, 1); el[1].position, el[1].color = 1.0, C_AMAR
    for pos, c in ((0.18, C_BRASA), (0.45, C_VERM), (0.72, C_LAR), (0.90, C_LAR)):
        e = el.new(pos); e.color = c
    nt.links.new(fator, cr.inputs[0]); return cr.outputs[0]
# ------------------------------------------------------------------ 2) pele
def fogo_pele(o, olhos):
    for m in o.data.materials:
        nt = m.node_tree; b_ = nt.nodes["Principled BSDF"]
        tex = next(x for x in nt.nodes if x.type == "TEX_IMAGE" and x.image and x.image.name.endswith("_Cor"))
        tv = nt.nodes["tempo"].outputs[0] if "tempo" in nt.nodes else no(nt, "ShaderNodeValue", name="tempo").outputs[0]
        w = no(nt, "ShaderNodeAttribute", attribute_name="fogo").outputs["Fac"]
        tc = no(nt, "ShaderNodeTexCoord"); mp = no(nt, "ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.75, 0.75, 0.07)          # r2: linguas finas e altas (r1 saia em manchas de lava)
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        sobe = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", tv, -0.45), sobe.inputs["Z"])
        vs = no(nt, "ShaderNodeVectorMath", operation="ADD"); nt.links.new(mp.outputs[0], vs.inputs[0]); nt.links.new(sobe.outputs[0], vs.inputs[1])
        nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 3.2; nz.inputs["Detail"].default_value = 4.0
        nz.inputs["Distortion"].default_value = 0.9; nt.links.new(vs.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "MULTIPLY", tv, 0.45), nz.inputs["W"])
        lingua = no(nt, "ShaderNodeMapRange"); lingua.inputs["From Min"].default_value = 0.40; lingua.inputs["From Max"].default_value = 0.72
        nt.links.new(nz.outputs["Fac"], lingua.inputs["Value"])
        lum = no(nt, "ShaderNodeRGBToBW"); nt.links.new(tex.outputs["Color"], lum.inputs[0])
        fio = no(nt, "ShaderNodeMapRange"); fio.inputs["From Min"].default_value = 0.012; fio.inputs["From Max"].default_value = 0.09
        nt.links.new(lum.outputs[0], fio.inputs["Value"])
        placa = no(nt, "ShaderNodeMapRange"); placa.inputs["From Min"].default_value = 0.10; placa.inputs["From Max"].default_value = 0.17
        nt.links.new(lum.outputs[0], placa.inputs["Value"])                                    # r2: placas (mais claras) ficam legiveis
        w2 = op(nt, "MULTIPLY", w, op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", placa.outputs[0], 0.85)))
        calor = op(nt, "MULTIPLY", op(nt, "MULTIPLY", w2, op(nt, "ADD", 0.30, op(nt, "MULTIPLY", fio.outputs[0], 0.70))), lingua.outputs[0])
        calor = op(nt, "MINIMUM", op(nt, "MULTIPLY", calor, 1.9), 1.0)
        cor = rampa(nt, calor); forca = op(nt, "MULTIPLY", calor, 3.6)
        sep = no(nt, "ShaderNodeSeparateColor"); nt.links.new(tex.outputs["Color"], sep.inputs[0])
        sat = op(nt, "SUBTRACT", sep.outputs[0], op(nt, "MAXIMUM", sep.outputs[1], sep.outputs[2]))
        ol = no(nt, "ShaderNodeMapRange"); ol.inputs["From Min"].default_value = 0.20; ol.inputs["From Max"].default_value = 0.36
        nt.links.new(sat, ol.inputs["Value"]); kol = op(nt, "MULTIPLY", ol.outputs[0], 10.0 if olhos else 2.0)
        e1 = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); e1.inputs["Factor"].default_value = 1.0
        nt.links.new(cor, e1.inputs["A"]); c1 = no(nt, "ShaderNodeCombineColor")
        for i_ in range(3): nt.links.new(forca, c1.inputs[i_])
        nt.links.new(c1.outputs[0], e1.inputs["B"])
        e2 = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); e2.inputs["Factor"].default_value = 1.0
        e2.inputs["A"].default_value = C_LAR; c2 = no(nt, "ShaderNodeCombineColor")
        for i_ in range(3): nt.links.new(kol, c2.inputs[i_])
        nt.links.new(c2.outputs[0], e2.inputs["B"])
        sm = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="ADD"); sm.inputs["Factor"].default_value = 1.0
        nt.links.new(e1.outputs["Result"], sm.inputs["A"]); nt.links.new(e2.outputs["Result"], sm.inputs["B"])
        nt.links.new(sm.outputs["Result"], b_.inputs["Emission Color"]); b_.inputs["Emission Strength"].default_value = 1.0
fogo_pele(CORPO, False); fogo_pele(CAB, True)
# boca: a A2 ja acende gengiva/lingua (dentes nao); mantida
# ------------------------------------------------------------------ 3) chamas viradas para a camera, so onde a silhueta pede
def bvh_de(objs):
    dg = bpy.context.evaluated_depsgraph_get(); bm = bmesh.new()
    for o in objs:
        me = o.evaluated_get(dg).to_mesh(); tmp = bmesh.new(); tmp.from_mesh(me); tmp.transform(o.matrix_world)
        m2 = bpy.data.meshes.new("tmp"); tmp.to_mesh(m2); tmp.free(); bm.from_mesh(m2); bpy.data.meshes.remove(m2); o.evaluated_get(dg).to_mesh_clear()
    t = BVHTree.FromBMesh(bm); bm.free(); return t
BVH = bvh_de([CAB, CORPO])
mc = bpy.data.materials.new("M_Chama_A3"); mc.use_nodes = True; nt = mc.node_tree; nt.nodes.clear()
out = no(nt, "ShaderNodeOutputMaterial"); em = no(nt, "ShaderNodeEmission"); trn = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
nt.links.new(trn.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
tv = no(nt, "ShaderNodeValue", name="tempo").outputs[0]; sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0])
rnd_o = no(nt, "ShaderNodeObjectInfo").outputs["Random"]
ritmo = op(nt, "ADD", 0.7, op(nt, "MULTIPLY", rnd_o, 0.8))                          # cada chama no seu ritmo
u_ = sp.outputs["X"]; v_ = sp.outputs["Y"]
vec = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", u_, 1.8), vec.inputs["X"])
nt.links.new(op(nt, "SUBTRACT", op(nt, "MULTIPLY", v_, 1.5), op(nt, "MULTIPLY", tv, op(nt, "MULTIPLY", ritmo, 2.0))), vec.inputs["Y"])
nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 2.6; nz.inputs["Detail"].default_value = 4.0; nz.inputs["Distortion"].default_value = 1.1
nt.links.new(vec.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "ADD", op(nt, "MULTIPLY", rnd_o, 20.0), op(nt, "MULTIPLY", tv, op(nt, "MULTIPLY", ritmo, 0.7))), nz.inputs["W"])
# lingua curva: o eixo da chama ondula para os lados cada vez mais em cima; a ponta se divide em pontas irregulares
curva = op(nt, "MULTIPLY", op(nt, "SUBTRACT", nz.outputs["Fac"], 0.5), op(nt, "MULTIPLY", op(nt, "POWER", v_, 1.1), 1.9))   # r3: pontas mais curvas
dx = op(nt, "ABSOLUTE", op(nt, "SUBTRACT", op(nt, "SUBTRACT", u_, 0.5), curva))
larg = op(nt, "MULTIPLY", op(nt, "POWER", op(nt, "SUBTRACT", 1.0, v_), 0.7), 0.46)
forma = op(nt, "SUBTRACT", larg, dx)
dens = op(nt, "MULTIPLY", op(nt, "MULTIPLY", forma, 4.0), op(nt, "ADD", 0.35, nz.outputs["Fac"]))   # r3: borda macia (8 cortava em bloco)
dens = op(nt, "MINIMUM", op(nt, "MAXIMUM", dens, 0.0), 1.0)
dens = op(nt, "MULTIPLY", dens, op(nt, "POWER", op(nt, "MINIMUM", op(nt, "MULTIPLY", v_, 3.0), 1.0), 1.4))   # raiz que some no pelo
calor = op(nt, "MINIMUM", op(nt, "MULTIPLY", op(nt, "MULTIPLY", dens, op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", v_, 0.6))), 1.05), 1.0)   # r3: amarelo so no ponto mais quente
nt.links.new(rampa(nt, calor), em.inputs["Color"]); nt.links.new(op(nt, "MULTIPLY", calor, 2.4), em.inputs["Strength"])
nt.links.new(op(nt, "MINIMUM", op(nt, "MULTIPLY", dens, 1.2), 1.0), mx.inputs[0])
try: mc.surface_render_method = "BLENDED"
except Exception: pass
ALVO = bpy.data.objects.new("AlvoCamera", None); sc.collection.objects.link(ALVO); ALVO.location = (-30, -32, 19)
CHAMAS = []
def chama(base, osso_nome, alt, larg, incl, zona):
    """lingua unica (plano no X-Z local, para cima = Z) presa ao osso, girando no proprio eixo para olhar a camera"""
    mm = bpy.data.meshes.new("ChamaA3"); bmc = bmesh.new(); uvl = bmc.loops.layers.uv.new()
    vs = [bmc.verts.new((-larg / 2, 0, 0)), bmc.verts.new((larg / 2, 0, 0)), bmc.verts.new((larg / 2, 0, alt)), bmc.verts.new((-larg / 2, 0, alt))]
    f_ = bmc.faces.new(vs)
    for lp, uvv in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uvv
    bmc.to_mesh(mm); bmc.free()
    o = bpy.data.objects.new("ChamaA3_%02d" % len(CHAMAS), mm); sc.collection.objects.link(o); o.data.materials.append(mc)
    o.parent = rig; o.parent_type = "BONE"; o.parent_bone = osso_nome
    def orient(up):
        z = up.normalized(); y = V((0, -1, 0)); x = y.cross(z).normalized(); y = z.cross(x)
        return Matrix.Translation(base) @ Matrix((x, y, z)).transposed().to_4x4()
    o.matrix_world = orient(incl + V((0, 0.85, 0)) * 0.9); bpy.context.view_layer.update(); rot_andar = tuple(o.rotation_euler)   # ao andar: inclina para tras
    o.matrix_world = orient(incl); bpy.context.view_layer.update()
    o["rot_repouso"] = tuple(o.rotation_euler); o["rot_andar"] = rot_andar
    c = o.constraints.new("LOCKED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"; c.lock_axis = "LOCK_Z"
    CHAMAS.append({"nome": o.name, "zona": zona, "osso": osso_nome, "base": [round(x_, 3) for x_ in base], "altura": round(alt, 2), "largura": round(larg, 2)})
def pele(P, d, alcance=10):
    hit, nrm, i_, dd = BVH.ray_cast(P + d.normalized() * alcance, -d.normalized(), alcance); return (hit, nrm) if hit is not None else (None, None)
for k in "CED":                                               # juba: linguas grandes no alto e nos lados do pescoco, ate a nuca
    hb, f = CABS[k]; s = f.cross(V((0, 0, 1))).normalized()
    for u in (0.12, 0.32, 0.52, 0.72, 0.88):
        P = osso("Pescoco%s1" % k)[0].lerp(hb - f * 1.2, u)
        for d, esc in ((V((0, 0, 1)) - f * 0.2, 1.0), (s + V((0, 0, 0.5)), 0.7), (-s + V((0, 0, 0.5)), 0.7)):
            if esc < 1.0 and rnd.random() < 0.35: continue
            hit, nrm = pele(P, d)
            if hit is None: continue
            incl = (nrm * 0.35 + V((0, 0.25, 1))).normalized()
            chama(hit - nrm * 0.25, "Pescoco%s%d" % (k, 1 if u < 0.5 else 2), rnd.uniform(3.8, 6.0) * esc, rnd.uniform(2.2, 3.2) * esc, incl, "juba")
y_omb, y_quad = osso("BracoE")[0].y, osso("CoxaE")[0].y
for y in np.linspace(y_omb + 0.5, y_quad + 0.5, 5):           # dorso: bordas (a sela vai por cima da armadura)
    for lado in (-1, 1):
        hit, nrm = pele(V((X0 + lado * 2.0, y, 10)), V((lado * 0.5, 0, 1)))
        if hit is None: continue
        chama(hit - nrm * 0.25, "Coluna1" if y > 0 else "Coluna2", rnd.uniform(2.4, 3.6), rnd.uniform(1.6, 2.2), (nrm * 0.3 + V((0, 0.3, 1))).normalized(), "dorso")
for lado in (-1, 1):                                          # ombros: pequenas
    hit, nrm = pele(V((X0 + lado * 2.5, y_omb - 0.5, 11.5)), V((lado, 0, 0.6)))
    if hit is not None: chama(hit - nrm * 0.4, "Escapula" + ("E" if lado < 0 else "D"), rnd.uniform(1.4, 2.0), 1.1, (nrm * 0.4 + V((0, 0.3, 1))).normalized(), "ombro")
for nm, alt in (("Cauda2", 3.2), ("Cauda3", 4.8)):            # ponta da cauda: as maiores da traseira
    hit, nrm = pele(osso(nm)[1], V((0, 0, 1)), 4)
    if hit is not None:
        chama(hit - nrm * 0.4, nm, alt, 1.8, V((0, 0.6, 1)).normalized(), "cauda")
        chama(hit - nrm * 0.4 + V((0, 0.4, 0)), nm, alt * 0.7, 1.3, V((0.3, 0.8, 1)).normalized(), "cauda")
print("CHAMAS_A3", len(CHAMAS), {z: sum(1 for c in CHAMAS if c["zona"] == z) for z in ("juba", "dorso", "ombro", "cauda")}, flush=True)
rig.data.pose_position = "POSE"
for pb in rig.pose.bones:
    for c in pb.constraints: c.mute = True
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_Fogo_A3.blend"))
n = len(CHAMAS)
json.dump({"versao": "A3", "chamas": CHAMAS, "pele": "atributo de vertice 'fogo' (regioes do rig) -> no Roblox vira EmissiveMask assada",
           "estimativa_roblox_A_TESTAR": {"pc": {"emissores": n, "taxa_por_emissor": 6, "vida_s": 0.8, "particulas_vivas": round(n * 6 * 0.8)},
                                          "celular": {"emissores": math.ceil(n / 2), "taxa_por_emissor": 4, "vida_s": 0.7, "particulas_vivas": round(math.ceil(n / 2) * 4 * 0.7)},
                                          "observacao": "estimativa de previa; desempenho real so medindo no Roblox (§5.10: ~150 particulas por efeito)"}},
          open(os.path.join(OUT, "aura_A3.json"), "w"), indent=1, ensure_ascii=False)
print("FOGO_A3_OK", flush=True)
