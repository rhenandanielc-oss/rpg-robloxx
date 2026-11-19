"""Efeitos dos PODERES sobre a aura de fogo A3 aprovada (18/11) - PREVIA no Blender (§5.9h adaptado ao fogo aprovado).
Base: copia de aura/CR_Cerbero_Fogo_A3.blend (A3 intacta). Sincronizado pelos eventos dos clipes (rig/clipes_L3/manifesto):
  * Chamas Triplices (Prev_Chamas_Repouso; disparos E 0,65 / C 0,90 / D 1,15 s no previo): a cabeca acende antes do disparo,
    o fogo do pescoco dela reforca no disparo, a boca brilha e sai um projetil de fogo da boca (ponto_boca do manifesto).
  * Investida Sombria (Investida -> Corrida): no impulso as chamas e as linguas da pele esticam para tras e o fogo fica mais
    forte, olhos clareiam; boost de 4 s com fogo forte; faixa de sombra com brasas no chao por 3 s; vento quente rente ao corpo.
  * Furia das Tres Cabecas / Rugido Infernal (Prev_Furia_Andar): cada cabeca explode em fogo no seu rugido (uma por vez),
    3 ondas de fogo correm da cabeca a cauda, olhos em brasa clara, faixas de vento quente em volta do tronco, fade no ultimo 1,5 s.
Depois de cada efeito volta a aura de repouso. Valores [A TESTAR]; paleta de fogo aprovada (o roxo da v6.2 nao entra).
Uso: blender -b -t 4 CR_Cerbero_Fogo_A3.blend -P fx_poderes.py -- <saida_dir> [so=chamas,investida,furia] [video=1]"""
import bpy, bmesh, sys, os, math, json
from mathutils import Vector as V, Matrix
ARGS = sys.argv[sys.argv.index("--") + 1:]
OUT = os.path.abspath(ARGS[0]); os.makedirs(OUT, exist_ok=True)
SO = next((a.split("=")[1].split(",") for a in ARGS if a.startswith("so=")), ["chamas", "investida", "furia"])
VIDEO = "video=0" not in ARGS
sc = bpy.context.scene; sc.render.fps = 30; sc.render.threads_mode = "FIXED"; sc.render.threads = 4; FPS = 30
rig = bpy.data.objects["Cerbero_Rig"]; PB = rig.pose.bones; BD = rig.data.bones
CAB, CORPO, BOCA = (bpy.data.objects[n] for n in ("Cerbero_Cabecas", "Cerbero_Corpo", "Cerbero_Bocas"))
CHAMAS = [o for o in bpy.data.objects if "rot_repouso" in o.keys()]
ALVO = bpy.data.objects["AlvoCamera"]
MANI = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "..", "rig", "clipes_L3", "manifesto_clipes.json"), encoding="utf-8"))
PONTO_BOCA = MANI["ChamasTriplices"]["ponto_boca_local_Cabeca"]
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
    cr = no(nt, "ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0, 0, 0, 1); el[1].position, el[1].color = 1.0, C_AMAR
    for pos, c in ((0.18, C_BRASA), (0.45, C_VERM), (0.72, C_LAR), (0.90, C_LAR)):
        e = el.new(pos); e.color = c
    nt.links.new(fator, cr.inputs[0]); return cr.outputs[0]
def val(nt, nome, v0):
    n_ = nt.nodes.get(nome) or no(nt, "ShaderNodeValue", name=nome); n_.outputs[0].default_value = v0; return n_.outputs[0]
# ------------------------------------------------------------------ atributos: cabeca dominante (0 corpo, 1 C, 2 E, 3 D) e u ao longo do corpo
def atributos(o):
    nomes = {g.index: g.name for g in o.vertex_groups}; me = o.data
    ac = me.attributes.get("cab_id") or me.attributes.new("cab_id", "FLOAT", "POINT"); au = me.attributes.get("u_corpo") or me.attributes.new("u_corpo", "FLOAT", "POINT")
    cs, us = [], []
    for v in me.vertices:
        soma = {"C": 0.0, "E": 0.0, "D": 0.0}
        for g in v.groups:
            nm = nomes.get(g.group, "")
            for k in "CED":
                if nm in ("Pescoco%s1" % k, "Pescoco%s2" % k, "Cabeca" + k, "Mandibula" + k): soma[k] += g.weight
        k = max(soma, key=soma.get); cs.append({"C": 1.0, "E": 2.0, "D": 3.0}[k] if soma[k] > 0.4 else 0.0)
        us.append(min(1.0, max(0.0, (v.co.y + 12.1) / 24.2)))
    ac.data.foreach_set("value", cs); au.data.foreach_set("value", us)
atributos(CORPO); atributos(CAB)
# ------------------------------------------------------------------ pele: aura A3 + controles (intensidade, cabeca, onda, esticar, olhos)
def pele_fx(o, olhos):
    for m in o.data.materials:
        nt = m.node_tree; b_ = nt.nodes["Principled BSDF"]
        tex = next(x for x in nt.nodes if x.type == "TEX_IMAGE" and x.image and x.image.name.endswith("_Cor"))
        tv = nt.nodes["tempo"].outputs[0]; w = no(nt, "ShaderNodeAttribute", attribute_name="fogo").outputs["Fac"]
        cab = no(nt, "ShaderNodeAttribute", attribute_name="cab_id").outputs["Fac"]; u = no(nt, "ShaderNodeAttribute", attribute_name="u_corpo").outputs["Fac"]
        estica = val(nt, "fx_estica", 0.0)
        tc = no(nt, "ShaderNodeTexCoord"); mp = no(nt, "ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.75, 0.75, 0.07)
        nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
        # investida: as linguas da pele correm para tras (+Y) e esticam (escala menor em Y)
        des = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", tv, op(nt, "MULTIPLY", estica, -2.5)), des.inputs["Y"])
        nt.links.new(op(nt, "MULTIPLY", tv, -0.45), des.inputs["Z"])
        esc = no(nt, "ShaderNodeCombineXYZ"); esc.inputs["X"].default_value = 1.0; esc.inputs["Z"].default_value = 1.0
        nt.links.new(op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", estica, 0.75)), esc.inputs["Y"])
        vm = no(nt, "ShaderNodeVectorMath", operation="MULTIPLY"); nt.links.new(mp.outputs[0], vm.inputs[0]); nt.links.new(esc.outputs[0], vm.inputs[1])
        vs = no(nt, "ShaderNodeVectorMath", operation="ADD"); nt.links.new(vm.outputs[0], vs.inputs[0]); nt.links.new(des.outputs[0], vs.inputs[1])
        nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 3.2; nz.inputs["Detail"].default_value = 4.0
        nz.inputs["Distortion"].default_value = 0.9; nt.links.new(vs.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "MULTIPLY", tv, 0.45), nz.inputs["W"])
        lingua = no(nt, "ShaderNodeMapRange"); lingua.inputs["From Min"].default_value = 0.40; lingua.inputs["From Max"].default_value = 0.72
        nt.links.new(nz.outputs["Fac"], lingua.inputs["Value"])
        lum = no(nt, "ShaderNodeRGBToBW"); nt.links.new(tex.outputs["Color"], lum.inputs[0])
        fio = no(nt, "ShaderNodeMapRange"); fio.inputs["From Min"].default_value = 0.012; fio.inputs["From Max"].default_value = 0.09
        nt.links.new(lum.outputs[0], fio.inputs["Value"])
        placa = no(nt, "ShaderNodeMapRange"); placa.inputs["From Min"].default_value = 0.10; placa.inputs["From Max"].default_value = 0.17
        nt.links.new(lum.outputs[0], placa.inputs["Value"])
        w2 = op(nt, "MULTIPLY", w, op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", placa.outputs[0], 0.85)))
        # multiplicador do poder: intensidade geral x (1 + reforco da cabeca do vertice) x (1 + onda ao longo do corpo)
        def igual(x): return op(nt, "COMPARE", cab, x)
        reforco = op(nt, "ADD", op(nt, "ADD", op(nt, "MULTIPLY", igual(1.0), val(nt, "fx_cab_C", 0.0)), op(nt, "MULTIPLY", igual(2.0), val(nt, "fx_cab_E", 0.0))),
                     op(nt, "MULTIPLY", igual(3.0), val(nt, "fx_cab_D", 0.0)))
        dist = op(nt, "DIVIDE", op(nt, "SUBTRACT", u, val(nt, "fx_onda_pos", -1.0)), 0.07)
        onda = op(nt, "MULTIPLY", op(nt, "EXPONENT", op(nt, "MULTIPLY", op(nt, "MULTIPLY", dist, dist), -1.0)), val(nt, "fx_onda_amp", 0.0))
        mult = op(nt, "MULTIPLY", op(nt, "MULTIPLY", val(nt, "fx_intens", 1.0), op(nt, "ADD", 1.0, reforco)), op(nt, "ADD", 1.0, onda))
        calor = op(nt, "MULTIPLY", op(nt, "MULTIPLY", w2, op(nt, "ADD", 0.30, op(nt, "MULTIPLY", fio.outputs[0], 0.70))), lingua.outputs[0])
        calor = op(nt, "MINIMUM", op(nt, "MULTIPLY", op(nt, "MULTIPLY", calor, 1.9), mult), 1.0)
        forca = op(nt, "MULTIPLY", op(nt, "MULTIPLY", calor, 3.6), op(nt, "MINIMUM", op(nt, "MAXIMUM", 1.0, op(nt, "MULTIPLY", mult, 0.6)), 1.45))   # r2: sem estourar em branco
        cor = rampa(nt, calor)
        sep = no(nt, "ShaderNodeSeparateColor"); nt.links.new(tex.outputs["Color"], sep.inputs[0])
        sat = op(nt, "SUBTRACT", sep.outputs[0], op(nt, "MAXIMUM", sep.outputs[1], sep.outputs[2]))
        ol = no(nt, "ShaderNodeMapRange"); ol.inputs["From Min"].default_value = 0.20; ol.inputs["From Max"].default_value = 0.36
        nt.links.new(sat, ol.inputs["Value"]); kol = op(nt, "MULTIPLY", op(nt, "MULTIPLY", ol.outputs[0], 10.0 if olhos else 2.0), val(nt, "fx_olhos", 1.0))
        e1 = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); e1.inputs["Factor"].default_value = 1.0
        nt.links.new(cor, e1.inputs["A"]); c1 = no(nt, "ShaderNodeCombineColor")
        for i_ in range(3): nt.links.new(forca, c1.inputs[i_])
        nt.links.new(c1.outputs[0], e1.inputs["B"])
        # olhos: brasa clara (mistura para amarelo quando fx_olhos > 1)
        cor_olho = no(nt, "ShaderNodeMix", data_type="RGBA"); cor_olho.inputs["A"].default_value = C_LAR; cor_olho.inputs["B"].default_value = C_AMAR
        nt.links.new(op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "SUBTRACT", val(nt, "fx_olhos", 1.0), 1.0), 0.0), 1.0), cor_olho.inputs["Factor"])
        e2 = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="MULTIPLY"); e2.inputs["Factor"].default_value = 1.0
        nt.links.new(cor_olho.outputs["Result"], e2.inputs["A"]); c2 = no(nt, "ShaderNodeCombineColor")
        for i_ in range(3): nt.links.new(kol, c2.inputs[i_])
        nt.links.new(c2.outputs[0], e2.inputs["B"])
        sm = no(nt, "ShaderNodeMix", data_type="RGBA", blend_type="ADD"); sm.inputs["Factor"].default_value = 1.0
        nt.links.new(e1.outputs["Result"], sm.inputs["A"]); nt.links.new(e2.outputs["Result"], sm.inputs["B"])
        nt.links.new(sm.outputs["Result"], b_.inputs["Emission Color"])
pele_fx(CORPO, False); pele_fx(CAB, True)
for m in BOCA.data.materials:                                 # boca: brilho por cabeca (gengiva/lingua; dentes visiveis)
    nt = m.node_tree; b_ = nt.nodes["Principled BSDF"]; at = no(nt, "ShaderNodeAttribute", attribute_name="papel")
    sep = no(nt, "ShaderNodeSeparateColor"); nt.links.new(at.outputs["Color"], sep.inputs[0])
    verm = op(nt, "MAXIMUM", op(nt, "SUBTRACT", op(nt, "SUBTRACT", sep.outputs[0], sep.outputs[1]), 0.15), 0.0)
    ci = no(nt, "ShaderNodeAttribute", attribute_name="cabeca").outputs["Fac"]
    def igual(x): return op(nt, "COMPARE", ci, x)
    reforco = op(nt, "ADD", op(nt, "ADD", op(nt, "MULTIPLY", igual(0.0), val(nt, "fx_boca_C", 0.0)), op(nt, "MULTIPLY", igual(1.0), val(nt, "fx_boca_E", 0.0))),
                 op(nt, "MULTIPLY", igual(2.0), val(nt, "fx_boca_D", 0.0)))
    b_.inputs["Emission Color"].default_value = C_LAR
    nt.links.new(op(nt, "MULTIPLY", op(nt, "MULTIPLY", verm, 25.0), op(nt, "ADD", 1.0, op(nt, "MULTIPLY", reforco, 3.0))), b_.inputs["Emission Strength"])
# chamas: brilho por objeto (propriedade "brilho", lida no material)
mc = CHAMAS[0].data.materials[0]; ntc = mc.node_tree
emc = next(n_ for n_ in ntc.nodes if n_.type == "EMISSION"); lk = emc.inputs["Strength"].links[0]; src = lk.from_socket
ab = no(ntc, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="brilho")
ntc.links.new(op(ntc, "MULTIPLY", src, op(ntc, "MAXIMUM", ab.outputs["Fac"], 0.0)), emc.inputs["Strength"])
CAB_DE = {}
for o in CHAMAS:
    o["brilho"] = 1.0; o["esc0"] = tuple(o.scale)
    pai = o.parent_bone; CAB_DE[o.name] = next((k for k in "CED" if pai.startswith("Pescoco" + k)), None)
# ------------------------------------------------------------------ objetos novos: projeteis, faixa no chao, vento quente
def mat_fogo_radial(nome):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = no(nt, "ShaderNodeOutputMaterial"); em = no(nt, "ShaderNodeEmission"); tr = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0])
    dx = op(nt, "SUBTRACT", sp.outputs["X"], 0.5); dy = op(nt, "SUBTRACT", sp.outputs["Y"], 0.5)
    r = op(nt, "SQRT", op(nt, "ADD", op(nt, "MULTIPLY", dx, dx), op(nt, "MULTIPLY", dy, dy)))
    nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 4.0
    nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], nz.inputs["Vector"]); nt.links.new(op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 3.0), nz.inputs["W"])
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", op(nt, "ADD", 0.30, op(nt, "MULTIPLY", nz.outputs["Fac"], 0.25)), r), 6.0), 0.0), 1.0)
    nt.links.new(rampa(nt, d), em.inputs["Color"]); nt.links.new(op(nt, "MULTIPLY", d, 5.0), em.inputs["Strength"]); nt.links.new(d, mx.inputs[0])
    try: m.surface_render_method = "BLENDED"
    except Exception: pass
    return m
M_PROJ = mat_fogo_radial("M_Projetil_Fogo")
def plano(nome, larg, alt, mat):
    me = bpy.data.meshes.new(nome); bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    vs = [bm.verts.new((-larg / 2, 0, -alt / 2)), bm.verts.new((larg / 2, 0, -alt / 2)), bm.verts.new((larg / 2, 0, alt / 2)), bm.verts.new((-larg / 2, 0, alt / 2))]
    f_ = bm.faces.new(vs)
    for lp, uvv in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uvv
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(nome, me); sc.collection.objects.link(o); o.data.materials.append(mat); return o
PROJ = {}
for k in "CED":
    o = plano("Projetil_" + k, 3.2, 3.2, M_PROJ); c = o.constraints.new("DAMPED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"
    o.scale = (0, 0, 0); PROJ[k] = o
    rastro = plano("Rastro_" + k, 2.2, 2.2, M_PROJ); rastro.parent = o; c = rastro.constraints.new("DAMPED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"
    rastro.location = (0, 0, 0)
# faixa de sombra com brasas no chao (Investida): corre para tras com o chao, some em 3 s
mf = bpy.data.materials.new("M_Faixa_Sombra"); mf.use_nodes = True; nt = mf.node_tree; nt.nodes.clear()
out = no(nt, "ShaderNodeOutputMaterial"); pr = no(nt, "ShaderNodeBsdfPrincipled"); tr = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(pr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
pr.inputs["Base Color"].default_value = (0.01, 0.005, 0.008, 1); pr.inputs["Roughness"].default_value = 1.0
sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0])
idade = sp.outputs["Y"]                                       # 0 = sob o corpo, 1 = 3 s atras
borda = op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.5, op(nt, "ABSOLUTE", op(nt, "SUBTRACT", sp.outputs["X"], 0.5))), 4.0)
alfa = op(nt, "MULTIPLY", op(nt, "MULTIPLY", op(nt, "MINIMUM", borda, 1.0), op(nt, "SUBTRACT", 1.0, idade)), val(nt, "fx_faixa", 0.0))
vec = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", sp.outputs["X"], 3.0), vec.inputs["X"])
nt.links.new(op(nt, "SUBTRACT", op(nt, "MULTIPLY", idade, 40.0), op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 0.0)), vec.inputs["Y"])
nzf = no(nt, "ShaderNodeTexNoise"); nzf.inputs["Scale"].default_value = 2.0; nt.links.new(vec.outputs[0], nzf.inputs["Vector"])
brasas = op(nt, "MULTIPLY", op(nt, "MAXIMUM", op(nt, "SUBTRACT", nzf.outputs["Fac"], 0.62), 0.0), op(nt, "MULTIPLY", op(nt, "SUBTRACT", 1.0, idade), 30.0))
pr.inputs["Emission Color"].default_value = C_LAR; nt.links.new(op(nt, "MULTIPLY", brasas, val(nt, "fx_faixa", 0.0)), pr.inputs["Emission Strength"])
nt.links.new(op(nt, "MINIMUM", op(nt, "MULTIPLY", alfa, 0.85), 1.0), mx.inputs[0])
try: mf.surface_render_method = "BLENDED"
except Exception: pass
me = bpy.data.meshes.new("Faixa"); bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); L = 67.0     # 22,3 studs/s x 3 s
vs = [bm.verts.new((-1.6, -2, 0.04)), bm.verts.new((1.6, -2, 0.04)), bm.verts.new((1.6, -2 + L, 0.04)), bm.verts.new((-1.6, -2 + L, 0.04))]
f_ = bm.faces.new(vs)
for lp, uvv in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uvv
bm.to_mesh(me); bm.free(); FAIXA = bpy.data.objects.new("Faixa_Sombra", me); sc.collection.objects.link(FAIXA); FAIXA.data.materials.append(mf)
# vento quente: faixas finas translucidas em volta do tronco (presas a Coluna2), girando
mv = bpy.data.materials.new("M_Vento_Quente"); mv.use_nodes = True; nt = mv.node_tree; nt.nodes.clear()
out = no(nt, "ShaderNodeOutputMaterial"); em = no(nt, "ShaderNodeEmission"); tr = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0])
fase = op(nt, "FRACT", op(nt, "SUBTRACT", sp.outputs["X"], op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 0.6)))
risco = op(nt, "MULTIPLY", op(nt, "POWER", op(nt, "SINE", op(nt, "MULTIPLY", fase, math.pi)), 6.0), op(nt, "SINE", op(nt, "MULTIPLY", sp.outputs["Y"], math.pi)))
em.inputs["Color"].default_value = lin("ffb27a"); nt.links.new(op(nt, "MULTIPLY", risco, 1.5), em.inputs["Strength"])
nt.links.new(op(nt, "MULTIPLY", op(nt, "MULTIPLY", risco, 0.45), val(nt, "fx_vento", 0.0)), mx.inputs[0])
try: mv.surface_render_method = "BLENDED"
except Exception: pass
VENTOS = []
c2 = BD["Coluna2"].head_local
for i_, (zr, rx, ry, inc) in enumerate(((0.0, 4.6, 9.5, 0.10), (1.6, 4.2, 8.8, -0.12), (-1.4, 4.9, 9.0, 0.05))):
    me = bpy.data.meshes.new("Vento"); bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); N = 48; anel = []
    for j in range(N + 1):
        a = 2 * math.pi * j / N; p = V((rx * math.cos(a), ry * math.sin(a), zr + inc * ry * math.sin(a)))
        anel.append((bm.verts.new(p + V((0, 0, -0.18))), bm.verts.new(p + V((0, 0, 0.18)))))
    for j in range(N):
        f_ = bm.faces.new((anel[j][0], anel[j + 1][0], anel[j + 1][1], anel[j][1]))
        for lp, uvv in zip(f_.loops, ((j / N, 0), ((j + 1) / N, 0), ((j + 1) / N, 1), (j / N, 1))): lp[uvl].uv = uvv
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new("VentoQuente_%d" % i_, me); sc.collection.objects.link(o); o.data.materials.append(mv)
    o.parent = rig; o.parent_type = "BONE"; o.parent_bone = "Coluna2"; o.matrix_world = Matrix.Translation(c2 + V((0, 0, 1.0))); VENTOS.append(o)
# ------------------------------------------------------------------ cena, camera e utilitarios de chave
for o in list(sc.objects):
    if o.type in ("CAMERA", "LIGHT") or o.name.startswith(("IK_", "Polo_")): o.hide_render = True
w = bpy.data.worlds.new("Noite"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.045, 0.06, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
for nome, en, rot, cor in (("Lua", 1.2, (0.9, 0, -0.7), (0.75, 0.75, 0.9)), ("Contra", 0.8, (2.2, 0, 2.6), (0.9, 0.5, 0.45))):
    l = bpy.data.lights.new(nome, "SUN"); l.energy = en; l.color = cor; lo = bpy.data.objects.new(nome, l); sc.collection.objects.link(lo); lo.rotation_euler = rot
bpy.ops.mesh.primitive_plane_add(size=400); ch = bpy.context.object; mch = bpy.data.materials.new("Chao"); mch.use_nodes = True
mch.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.06, 0.055, 0.06, 1); ch.data.materials.append(mch)
sc.render.engine = "BLENDER_EEVEE"; sc.eevee.taa_render_samples = 16; sc.view_settings.view_transform = "Standard"
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam); sc.camera = cam
VISTAS = {"34": ((-30, -32, 19), (0, -1, 9), 50), "cab": ((-6, -34, 17), (0, -8, 14.5), 50), "lado": ((-48, 2, 9), (0, 4, 8.5), 50)}
def vista(n):
    pos, alvo, lente = VISTAS[n]; cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente; ALVO.location = pos
MATS_PELE = [m for o in (CORPO, CAB) for m in o.data.materials]; MAT_BOCA = BOCA.data.materials[0]
TODOS_MATS = [m for m in bpy.data.materials if m.use_nodes and m.node_tree and "tempo" in m.node_tree.nodes]
def limpar_chaves():
    for m in bpy.data.materials:
        if m.node_tree and m.node_tree.animation_data: m.node_tree.animation_data_clear()
    for o in CHAMAS + list(PROJ.values()) + [FAIXA] + VENTOS:
        if o.animation_data: o.animation_data_clear()
def k_val(mats, nome, f, v):
    for m in mats:
        n_ = m.node_tree.nodes.get(nome)
        if n_: n_.outputs[0].default_value = v; n_.outputs[0].keyframe_insert("default_value", frame=f)
def curva(mats, nome, pontos):
    for f, v in pontos: k_val(mats, nome, f, v)
def k_obj(o, prop, f, v):
    if prop == "brilho": o["brilho"] = v; o.keyframe_insert('["brilho"]', frame=f)
    elif prop == "scale": o.scale = v; o.keyframe_insert("scale", frame=f)
    elif prop == "location": o.location = v; o.keyframe_insert("location", frame=f)
    elif prop == "rotation_euler": o.rotation_euler = v; o.keyframe_insert("rotation_euler", frame=f)
def tempo_linear(f0, f1):
    for m in TODOS_MATS:
        s_ = m.node_tree.nodes["tempo"].outputs[0]; s_.default_value = 0.0; s_.keyframe_insert("default_value", frame=f0)
        s_.default_value = (f1 - f0) / FPS; s_.keyframe_insert("default_value", frame=f1)
    for m in TODOS_MATS:
        a = m.node_tree.animation_data.action
        for fc in (getattr(a, "fcurves", None) or [fc for ly in a.layers for st in ly.strips for cb in st.channelbags for fc in cb.fcurves]):
            if "tempo" in fc.data_path:
                for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
def nla(partes):
    if not rig.animation_data: rig.animation_data_create()
    rig.animation_data.action = None
    for tr in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(tr)
    tr = rig.animation_data.nla_tracks.new(); f = 1
    for nome, rep in partes:
        a = bpy.data.actions["Cerbero_" + nome]; n = int(a.frame_range[1] - a.frame_range[0]) + 1
        st = tr.strips.new(nome, f, a); st.repeat = rep; f += n * rep
    return f - 1
def F(t): return 1 + int(round(t * FPS))
def rot_mix(o, k):
    r0, r1 = V(o["rot_repouso"]), V(o["rot_andar"]); return tuple(r0 + (r1 - r0) * k)
def boca_mundo(k, f):
    sc.frame_set(f); pb = PB["Cabeca" + k]; M = rig.matrix_world @ pb.matrix
    return M @ V(PONTO_BOCA[k]), (M.to_3x3() @ V((0, 1, 0))).normalized()
for pb in PB:
    for c in pb.constraints: c.mute = True
RELATO = {}
def render(nome_fx, fim, vistas, quadros):
    sc.frame_start, sc.frame_end = 1, fim; sc.render.image_settings.media_type = "IMAGE"; sc.render.image_settings.file_format = "PNG"
    sc.render.resolution_x, sc.render.resolution_y = 820, 580
    for v in vistas:
        vista(v)
        for rot, t in quadros:
            sc.frame_set(F(t)); sc.render.filepath = os.path.join(OUT, "%s_%s_%s.png" % (nome_fx, v, rot)); bpy.ops.render.render(write_still=True)
    if VIDEO:
        sc.render.image_settings.media_type = "VIDEO"; sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"; sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
        sc.render.resolution_x, sc.render.resolution_y = 640, 450
        for v in vistas:
            vista(v); sc.render.filepath = os.path.join(OUT, "FX_%s_%s.mp4" % (nome_fx, v)); bpy.ops.render.render(animation=True)
    print("RENDER", nome_fx, flush=True)
def repouso_base(fim):
    """estado de repouso em todos os controles (a aura A3 normal)"""
    for nome, v in (("fx_intens", 1.0), ("fx_cab_C", 0.0), ("fx_cab_E", 0.0), ("fx_cab_D", 0.0), ("fx_onda_amp", 0.0), ("fx_onda_pos", -1.0),
                    ("fx_estica", 0.0), ("fx_olhos", 1.0)):
        k_val(MATS_PELE, nome, 1, v)
    for nome in ("fx_boca_C", "fx_boca_E", "fx_boca_D"): k_val([MAT_BOCA], nome, 1, 0.0)
    k_val([FAIXA.data.materials[0]], "fx_faixa", 1, 0.0); k_val([VENTOS[0].data.materials[0]], "fx_vento", 1, 0.0)
    for o in CHAMAS: k_obj(o, "brilho", 1, 1.0); k_obj(o, "scale", 1, o["esc0"])
    for o in PROJ.values(): k_obj(o, "scale", 1, (0, 0, 0))
# ------------------------------------------------------------------ CHAMAS TRIPLICES
if "chamas" in SO:
    limpar_chaves(); fim = F(2.4); nla([("Prev_Chamas_Repouso", 1), ("Repouso", 1)]); tempo_linear(1, fim); repouso_base(fim)
    for o in CHAMAS: o.rotation_euler = o["rot_repouso"]
    t0 = 0.2                                                     # a camada comeca em 0,2 s no previo
    for k in "ECD":
        td = t0 + MANI["ChamasTriplices"]["eventos_s"]["disparo_" + k]
        curva(MATS_PELE, "fx_cab_" + k, [(F(td - 0.30), 0.0), (F(td - 0.08), 0.9), (F(td), 1.4), (F(td + 0.25), 0.5), (F(td + 0.55), 0.0)])
        curva([MAT_BOCA], "fx_boca_" + k, [(F(td - 0.12), 0.0), (F(td), 2.5), (F(td + 0.3), 0.0)])
        for o in CHAMAS:
            if CAB_DE[o.name] == k:
                k_obj(o, "brilho", F(td - 0.30), 1.0); k_obj(o, "brilho", F(td), 1.9); k_obj(o, "brilho", F(td + 0.5), 1.0)
                e0 = V(o["esc0"]); k_obj(o, "scale", F(td - 0.30), tuple(e0)); k_obj(o, "scale", F(td), tuple(e0 * 1.45)); k_obj(o, "scale", F(td + 0.5), tuple(e0))
        p0, fr = boca_mundo(k, F(td)); p0 = p0 + fr * 2.2; pj = PROJ[k]          # r2: nasce a frente da boca (dentro dela aparecia furado)
        k_obj(pj, "scale", F(td) - 1, (0, 0, 0)); k_obj(pj, "scale", F(td), (1, 1, 1)); k_obj(pj, "scale", F(td + 0.55), (1, 1, 1)); k_obj(pj, "scale", F(td + 0.62), (0, 0, 0))
        k_obj(pj, "location", F(td), tuple(p0)); k_obj(pj, "location", F(td + 0.6), tuple(p0 + fr * 30.0))
        for fc in (getattr(pj.animation_data.action, "fcurves", None) or []):
            for kp in fc.keyframe_points: kp.interpolation = "LINEAR"
    RELATO["chamas"] = {"disparos_s_no_previo": {k: round(t0 + MANI["ChamasTriplices"]["eventos_s"]["disparo_" + k], 2) for k in "ECD"}, "projetil_alcance": 30, "projetil_duracao_s": 0.6}
    render("Chamas", fim, ["cab", "34"], [("repouso", 0.1), ("E", 0.65), ("C", 0.90), ("D", 1.15), ("volta", 2.3)])
# ------------------------------------------------------------------ INVESTIDA SOMBRIA
if "investida" in SO:
    limpar_chaves(); fim = nla([("Investida", 1), ("Corrida", 6)]); tempo_linear(1, fim); repouso_base(fim)
    ti, tf, tb = 0.30, 0.80, 0.30 + 4.0
    curva(MATS_PELE, "fx_estica", [(F(ti - 0.05), 0.0), (F(ti + 0.08), 1.0), (F(tf), 1.0), (F(tf + 0.3), 0.55), (F(tb), 0.55), (F(tb + 0.3), 0.0)])
    curva(MATS_PELE, "fx_intens", [(F(ti - 0.05), 1.0), (F(ti + 0.08), 1.35), (F(tf), 1.35), (F(tf + 0.3), 1.18), (F(tb), 1.18), (F(tb + 0.3), 1.0)])
    curva(MATS_PELE, "fx_olhos", [(F(ti - 0.05), 1.0), (F(ti + 0.1), 2.0), (F(tb), 2.0), (F(tb + 0.3), 1.0)])
    curva([FAIXA.data.materials[0]], "fx_faixa", [(F(ti), 0.0), (F(ti + 0.1), 1.0), (F(tb), 1.0), (F(tb + 3.0), 0.0)])
    curva([VENTOS[0].data.materials[0]], "fx_vento", [(F(ti), 0.0), (F(ti + 0.15), 1.0), (F(tb), 0.8), (F(tb + 0.3), 0.0)])
    for o in CHAMAS:
        k_obj(o, "rotation_euler", F(ti - 0.05), rot_mix(o, 0.0)); k_obj(o, "rotation_euler", F(ti + 0.1), rot_mix(o, 1.7))
        k_obj(o, "rotation_euler", F(tf + 0.2), rot_mix(o, 1.1)); k_obj(o, "rotation_euler", F(tb), rot_mix(o, 1.1)); k_obj(o, "rotation_euler", F(tb + 0.3), rot_mix(o, 1.0))
        e0 = V(o["esc0"]); k_obj(o, "scale", F(ti - 0.05), tuple(e0)); k_obj(o, "scale", F(ti + 0.1), tuple(V((e0.x * 0.8, e0.y, e0.z * 1.5))))
        k_obj(o, "scale", F(tf + 0.2), tuple(e0 * 1.15)); k_obj(o, "brilho", F(ti - 0.05), 1.0); k_obj(o, "brilho", F(ti + 0.1), 1.5); k_obj(o, "brilho", F(tf + 0.3), 1.2)
    RELATO["investida"] = {"impulso_s": [ti, tf], "boost_s": [ti, tb], "faixa_some_s": tb + 3.0, "faixa_comprimento_studs": 67, "previa_s": round(fim / FPS, 2)}
    render("Investida", fim, ["lado", "34"], [("repouso", 0.1), ("compressao", 0.22), ("impulso", 0.55), ("boost", 1.8), ("boost_fim", 4.3)])
# ------------------------------------------------------------------ FURIA / RUGIDO INFERNAL
if "furia" in SO:
    limpar_chaves(); fim = F(4.8); nla([("Prev_Furia_Andar", 1)]); tempo_linear(1, fim); repouso_base(fim)
    for o in CHAMAS: o.rotation_euler = o["rot_andar"]
    rug = MANI["FuriaRugido"]["eventos_s"]; fade0, fade1 = 3.3, 4.8                   # buff do previo; fade no ultimo 1,5 s
    for k in "CED":
        tr_ = rug["rugido_" + k]
        curva(MATS_PELE, "fx_cab_" + k, [(F(tr_ - 0.05), 0.0), (F(tr_ + 0.12), 1.6), (F(tr_ + 0.6), 0.5), (F(fade0), 0.5), (F(fade1), 0.0)])
        curva([MAT_BOCA], "fx_boca_" + k, [(F(tr_), 0.0), (F(tr_ + 0.1), 3.0), (F(tr_ + 0.7), 0.6), (F(fade0), 0.6), (F(fade1), 0.0)])
        for o in CHAMAS:
            if CAB_DE[o.name] == k:
                e0 = V(o["esc0"]); k_obj(o, "brilho", F(tr_ - 0.05), 1.0); k_obj(o, "brilho", F(tr_ + 0.12), 2.0); k_obj(o, "brilho", F(tr_ + 0.7), 1.3)
                k_obj(o, "brilho", F(fade0), 1.3); k_obj(o, "brilho", F(fade1), 1.0)
                k_obj(o, "scale", F(tr_ - 0.05), tuple(e0)); k_obj(o, "scale", F(tr_ + 0.12), tuple(e0 * 1.7)); k_obj(o, "scale", F(tr_ + 0.7), tuple(e0 * 1.25))
                k_obj(o, "scale", F(fade0), tuple(e0 * 1.25)); k_obj(o, "scale", F(fade1), tuple(e0))
    pts = [(1, -1.0)]
    for k in "CED":                                              # 3 ondas: uma por cabeca, da cabeca a cauda em 0,8 s
        tr_ = rug["rugido_" + k]; pts += [(F(tr_ + 0.05), -0.05), (F(tr_ + 0.85), 1.05)]
    curva(MATS_PELE, "fx_onda_pos", pts)
    curva(MATS_PELE, "fx_onda_amp", [(F(0.1), 0.0), (F(0.2), 0.9), (F(1.55), 0.9), (F(1.7), 0.0)])
    curva(MATS_PELE, "fx_intens", [(F(0.1), 1.0), (F(0.8), 1.2), (F(fade0), 1.2), (F(fade1), 1.0)])
    curva(MATS_PELE, "fx_olhos", [(F(0.1), 1.0), (F(0.3), 2.0), (F(fade0), 2.0), (F(fade1), 1.0)])
    curva([VENTOS[0].data.materials[0]], "fx_vento", [(F(0.1), 0.0), (F(0.6), 1.0), (F(fade0), 1.0), (F(fade1), 0.0)])
    RELATO["furia"] = {"rugidos_s": {k: rug["rugido_" + k] for k in "CED"}, "ondas": 3, "fade_s": [fade0, fade1], "previa_s": 4.8,
                       "inimigos_afetados": "linhas cinza/apagadas: nao ha inimigo na previa (fica para a integracao)"}
    render("Furia", fim, ["cab", "34"], [("repouso", 0.05), ("rugido_C", 0.27), ("rugido_E", 0.52), ("rugido_D", 0.77), ("furia", 2.4), ("fade", 4.4)])
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_FX_Poderes.blend"))
json.dump(RELATO, open(os.path.join(OUT, "fx_poderes.json"), "w"), indent=1, ensure_ascii=False)
print("FX_OK", json.dumps(RELATO, ensure_ascii=False), flush=True)
