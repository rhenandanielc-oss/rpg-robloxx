"""Bola Infernal (18/11) - ideia do usuario: "eles formam uma bola de fogo gigante que segue o alvo, brilhante e real",
SUBSTITUI o poder de projeteis (Chamas Triplices). Usa a base de efeitos da r4b (aura A3, pele, bocas). Previa de Blender.
Uso: blender -b -t 4 CR_Cerbero_Fogo_A3.blend -P fx_bola_infernal.py -- <saida> [video=0]
Base herdada: r4b (18/11) - pedido do usuario: "Projeteis maiores, e esse som no rugido nao". Projetil x ESC_PROJ (1,7 [A TESTAR])
em todas as partes (lingua, massa, camadas, nucleo, sopros, acumulo, impacto); saida mais a frente da boca; SEM o som
provisorio (reprovado). Base: r4 (fx_poderes_r4.py fica intacto).
r4 (18/11) - Rugido Infernal e projeteis (pedido "r4 do Rugido Infernal e dos projeteis"). Copia de revisao da r3
(fx_poderes_r3.py fica intacto). Muda:
  Furia: previa Prev_FuriaR4 (rig/clipes_L3r4): Rugido separado (C -> E -> D, uma abertura por vez, corpo inteiro com apoios
    firmes) e SO DEPOIS o FuriaLoop (mordidas desencontradas); violeta e SOM (provisorio, sintetizado) presos aos eventos de
    cada rugido; volta gradual ao laranja no ultimo 1,5 s; videos de frente e perfil com e sem som.
  Chamas: projetil com volume (lingua alongada no voo + silhueta irregular + nucleo pequeno + camadas de cauda que seguem a
    curva), acumulo na boca antes do disparo, saida a frente dos labios (nao atravessa o focinho), impacto = linguas de fogo na
    superficie com dissipacao rapida (sem anel); comparacao r3 x r4 de frente/perfil/3/4 com luz e distancia iguais; alvos
    10/20/30, curva simulada, camera aberta, camera de jogo e vista distante. Valores [A TESTAR].
Uso: blender -b -t 4 CR_Cerbero_Fogo_A3.blend -P fx_poderes_r4.py -- <saida> [so=comparacao,chamas,curva,furia] [video=0]
Base (r3): r3 (18/11) - REVISAO das tres habilidades (pedido do usuario). Base de comparacao: a r2 (fx_poderes.py). Muda:
  Chamas: projetil novo (nucleo quente, corpo de chama girando, cauda curta na trajetoria, impacto breve), alvos a 10/20/30
  studs e teste de CURVA (SIMULACAO DE BLENDER: 180 graus/s, 40 studs/s [A TESTAR]); Furia: laranja -> VIOLETA por cabeca e em
  ondas pelo corpo, volta ao laranja no ultimo 1,5 s; Investida: clipe InvestidaR3 (mais acao), saindo parado e em movimento,
  com mudanca de direcao simulada. Uso: blender -b -t 4 CR_Cerbero_Fogo_A3.blend -P fx_poderes_r3.py -- <saida> [so=...]
Efeitos dos PODERES sobre a aura de fogo A3 aprovada (18/11) - PREVIA no Blender (§5.9h adaptado ao fogo aprovado).
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
SO = next((a.split("=")[1].split(",") for a in ARGS if a.startswith("so=")), ["bola"])
VIDEO = "video=0" not in ARGS
sc = bpy.context.scene; sc.render.fps = 30; sc.render.threads_mode = "FIXED"; sc.render.threads = 4; FPS = 30
rig = bpy.data.objects["Cerbero_Rig"]; PB = rig.pose.bones; BD = rig.data.bones
CAB, CORPO, BOCA = (bpy.data.objects[n] for n in ("Cerbero_Cabecas", "Cerbero_Corpo", "Cerbero_Bocas"))
CHAMAS = [o for o in bpy.data.objects if "rot_repouso" in o.keys()]
ALVO = bpy.data.objects["AlvoCamera"]
MANI = json.load(open(os.path.join(os.path.dirname(bpy.data.filepath), "..", "rig", "clipes_L3", "manifesto_clipes.json"), encoding="utf-8"))
PONTO_BOCA = MANI["ChamasTriplices"]["ponto_boca_local_Cabeca"]
L3R = os.path.join(os.path.dirname(bpy.data.filepath), "..", "rig", "clipes_L3r")
MANI_R = json.load(open(os.path.join(L3R, "manifesto_clipes.json"), encoding="utf-8"))
with bpy.data.libraries.load(os.path.join(L3R, "CR_Cerbero_Anim.blend")) as (src, dst): dst.actions = ["Cerbero_InvestidaR3"]
L3R4 = os.path.join(os.path.dirname(bpy.data.filepath), "..", "rig", "clipes_L3r4")      # r4: Rugido separado
MANI4 = json.load(open(os.path.join(L3R4, "manifesto_clipes.json"), encoding="utf-8"))
with bpy.data.libraries.load(os.path.join(L3R4, "CR_Cerbero_Anim.blend")) as (src, dst): dst.actions = ["Cerbero_Prev_FuriaR4"]
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
VIO_ESC, VIO_MED, VIO_CLA, VIO_NUC = lin("1e0033"), lin("6a1bd6"), lin("a65cff"), lin("e7d2ff")
def rampa_vio(nt, fator):
    cr = no(nt, "ShaderNodeValToRGB"); el = cr.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0, 0, 0, 1); el[1].position, el[1].color = 1.0, VIO_NUC
    for pos, c in ((0.18, VIO_ESC), (0.45, VIO_MED), (0.72, VIO_CLA), (0.90, VIO_CLA)):
        e = el.new(pos); e.color = c
    nt.links.new(fator, cr.inputs[0]); return cr.outputs[0]
def mistura_cor(nt, a, b, fator):
    m_ = no(nt, "ShaderNodeMix", data_type="RGBA"); nt.links.new(a, m_.inputs["A"]); nt.links.new(b, m_.inputs["B"])
    nt.links.new(fator, m_.inputs["Factor"]); return m_.outputs["Result"]
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
        # r3 Furia: violeta por cabeca (cab_id) e no corpo atras de uma FRENTE que corre da cabeca a cauda (u_corpo)
        vio_cab = op(nt, "ADD", op(nt, "ADD", op(nt, "MULTIPLY", igual(1.0), val(nt, "fx_vio_C", 0.0)), op(nt, "MULTIPLY", igual(2.0), val(nt, "fx_vio_E", 0.0))),
                     op(nt, "MULTIPLY", igual(3.0), val(nt, "fx_vio_D", 0.0)))
        frente = no(nt, "ShaderNodeMapRange"); frente.inputs["From Min"].default_value = -0.04; frente.inputs["From Max"].default_value = 0.04
        nt.links.new(op(nt, "SUBTRACT", val(nt, "fx_vio_frente", -0.2), u), frente.inputs["Value"])
        vio_corpo = op(nt, "MULTIPLY", igual(0.0), frente.outputs[0])
        vio = op(nt, "MULTIPLY", op(nt, "MINIMUM", op(nt, "ADD", vio_cab, vio_corpo), 1.0), val(nt, "fx_vio_global", 1.0))
        cor = mistura_cor(nt, rampa(nt, calor), rampa_vio(nt, calor), vio)
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
    vio_b = op(nt, "MULTIPLY", op(nt, "ADD", op(nt, "ADD", op(nt, "MULTIPLY", igual(0.0), val(nt, "fx_vio_C", 0.0)), op(nt, "MULTIPLY", igual(1.0), val(nt, "fx_vio_E", 0.0))),
                 op(nt, "MULTIPLY", igual(2.0), val(nt, "fx_vio_D", 0.0))), val(nt, "fx_vio_global", 1.0))
    cb_ = no(nt, "ShaderNodeMix", data_type="RGBA"); cb_.inputs["A"].default_value = C_LAR; cb_.inputs["B"].default_value = VIO_CLA
    nt.links.new(vio_b, cb_.inputs["Factor"]); nt.links.new(cb_.outputs["Result"], b_.inputs["Emission Color"])
    nt.links.new(op(nt, "MULTIPLY", op(nt, "MULTIPLY", verm, 25.0), op(nt, "ADD", 1.0, op(nt, "MULTIPLY", reforco, 3.0))), b_.inputs["Emission Strength"])
# chamas: brilho por objeto (propriedade "brilho", lida no material)
mc = CHAMAS[0].data.materials[0]; ntc = mc.node_tree
emc = next(n_ for n_ in ntc.nodes if n_.type == "EMISSION"); lk = emc.inputs["Strength"].links[0]; src = lk.from_socket
ab = no(ntc, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="brilho")
ntc.links.new(op(ntc, "MULTIPLY", src, op(ntc, "MAXIMUM", ab.outputs["Fac"], 0.0)), emc.inputs["Strength"])
cr_lar = emc.inputs["Color"].links[0].from_node; calor_c = cr_lar.inputs[0].links[0].from_socket    # r3: chama tambem vira violeta
av = no(ntc, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="violeta")
ntc.links.new(mistura_cor(ntc, cr_lar.outputs[0], rampa_vio(ntc, calor_c), av.outputs["Fac"]), emc.inputs["Color"])
CAB_DE = {}
for o in CHAMAS:
    o["brilho"] = 1.0; o["violeta"] = 0.0; o["esc0"] = tuple(o.scale)
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
def plano(nome, larg, alt, mat):
    me = bpy.data.meshes.new(nome); bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
    vs = [bm.verts.new((-larg / 2, 0, -alt / 2)), bm.verts.new((larg / 2, 0, -alt / 2)), bm.verts.new((larg / 2, 0, alt / 2)), bm.verts.new((-larg / 2, 0, alt / 2))]
    f_ = bm.faces.new(vs)
    for lp, uvv in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uvv
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(nome, me); sc.collection.objects.link(o); o.data.materials.append(mat); return o
def mat_base(nome):
    m = bpy.data.materials.new(nome); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = no(nt, "ShaderNodeOutputMaterial"); em = no(nt, "ShaderNodeEmission"); tr = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    try: m.surface_render_method = "BLENDED"
    except Exception: pass
    sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0])
    return m, nt, em, mx, sp
def mat_nucleo():
    m, nt, em, mx, sp = mat_base("M_Proj_Nucleo")
    dx = op(nt, "SUBTRACT", sp.outputs["X"], 0.5); dy = op(nt, "SUBTRACT", sp.outputs["Y"], 0.5); r = op(nt, "SQRT", op(nt, "ADD", op(nt, "MULTIPLY", dx, dx), op(nt, "MULTIPLY", dy, dy)))
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.5, r), 2.4), 0.0), 1.0)
    nt.links.new(rampa(nt, op(nt, "ADD", 0.45, op(nt, "MULTIPLY", d, 0.5))), em.inputs["Color"]); nt.links.new(op(nt, "MULTIPLY", d, 3.0), em.inputs["Strength"])
    nt.links.new(d, mx.inputs[0]); return m
def mat_corpo():
    """corpo da chama girando em volta do nucleo (ruido em coordenadas giradas pelo tempo)"""
    m, nt, em, mx, sp = mat_base("M_Proj_Corpo")
    uv = no(nt, "ShaderNodeTexCoord").outputs["UV"]; cen = no(nt, "ShaderNodeVectorMath", operation="SUBTRACT"); nt.links.new(uv, cen.inputs[0]); cen.inputs[1].default_value = (0.5, 0.5, 0)
    gira = no(nt, "ShaderNodeVectorRotate", rotation_type="Z_AXIS"); nt.links.new(cen.outputs[0], gira.inputs["Vector"])
    nt.links.new(op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 7.0), gira.inputs["Angle"])
    r = no(nt, "ShaderNodeVectorMath", operation="LENGTH"); nt.links.new(cen.outputs[0], r.inputs[0])
    nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 3.5; nz.inputs["Detail"].default_value = 3.0; nz.inputs["Distortion"].default_value = 0.8
    nt.links.new(gira.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 2.0), nz.inputs["W"])
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", op(nt, "ADD", 0.28, op(nt, "MULTIPLY", nz.outputs["Fac"], 0.26)), r.outputs["Value"]), 5.0), 0.0), 1.0)
    nt.links.new(rampa(nt, op(nt, "MULTIPLY", d, 0.85)), em.inputs["Color"]); nt.links.new(op(nt, "MULTIPLY", d, 2.4), em.inputs["Strength"])
    nt.links.new(op(nt, "MINIMUM", op(nt, "MULTIPLY", d, 1.3), 1.0), mx.inputs[0]); return m
def mat_cauda():
    """cauda curta: mais forte junto ao projetil (v = 0), dissipa para tras (v = 1), com ruido que corre"""
    m, nt, em, mx, sp = mat_base("M_Proj_Cauda")
    u, v = sp.outputs["X"], sp.outputs["Y"]
    larg = op(nt, "MULTIPLY", op(nt, "SUBTRACT", 1.0, v), 0.5); dx = op(nt, "ABSOLUTE", op(nt, "SUBTRACT", u, 0.5))
    vec = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", u, 2.0), vec.inputs["X"]); nt.links.new(op(nt, "ADD", op(nt, "MULTIPLY", v, 2.5), op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 4.0)), vec.inputs["Y"])
    nz = no(nt, "ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 3.0; nt.links.new(vec.outputs[0], nz.inputs["Vector"])
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "MULTIPLY", op(nt, "SUBTRACT", larg, dx), 5.0), op(nt, "ADD", 0.3, nz.outputs["Fac"])), 0.0), 1.0)
    d = op(nt, "MULTIPLY", d, op(nt, "POWER", op(nt, "SUBTRACT", 1.0, v), 1.4))
    nt.links.new(rampa(nt, op(nt, "MULTIPLY", d, 0.8)), em.inputs["Color"]); nt.links.new(op(nt, "MULTIPLY", d, 2.0), em.inputs["Strength"])
    nt.links.new(op(nt, "MINIMUM", op(nt, "MULTIPLY", d, 1.2), 1.0), mx.inputs[0]); return m
def mat_impacto():
    """impacto breve: anel de fogo que abre e some (propriedade 'abre' 0 -> 1 do objeto)"""
    m, nt, em, mx, sp = mat_base("M_Proj_Impacto")
    dx = op(nt, "SUBTRACT", sp.outputs["X"], 0.5); dy = op(nt, "SUBTRACT", sp.outputs["Y"], 0.5); r = op(nt, "SQRT", op(nt, "ADD", op(nt, "MULTIPLY", dx, dx), op(nt, "MULTIPLY", dy, dy)))
    ab_ = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="abre").outputs["Fac"]
    raio = op(nt, "ADD", 0.08, op(nt, "MULTIPLY", ab_, 0.36)); anel = op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", op(nt, "ABSOLUTE", op(nt, "SUBTRACT", r, raio)), 9.0))
    nucleo = op(nt, "MULTIPLY", op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", r, 5.0)), op(nt, "SUBTRACT", 1.0, ab_))
    d = op(nt, "MULTIPLY", op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MAXIMUM", anel, nucleo), 0.0), 1.0), op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", ab_, ab_)))
    nt.links.new(rampa(nt, op(nt, "ADD", 0.4, op(nt, "MULTIPLY", d, 0.5))), em.inputs["Color"]); nt.links.new(op(nt, "MULTIPLY", d, 3.0), em.inputs["Strength"])
    nt.links.new(op(nt, "MINIMUM", d, 1.0), mx.inputs[0]); return m
M_NUC, M_COR, M_CAU, M_IMP = mat_nucleo(), mat_corpo(), mat_cauda(), mat_impacto()
def cauda_mesh(nome):
    me = bpy.data.meshes.new(nome); bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); L_, W_ = 4.2, 1.5
    vs = [bm.verts.new((-W_ / 2, 0, 0)), bm.verts.new((W_ / 2, 0, 0)), bm.verts.new((W_ / 4, -L_, 0)), bm.verts.new((-W_ / 4, -L_, 0))]
    f_ = bm.faces.new(vs)
    for lp, uvv in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uvv
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(nome, me); sc.collection.objects.link(o); o.data.materials.append(M_CAU); return o
def criar_proj(nome):
    pai = bpy.data.objects.new(nome, None); sc.collection.objects.link(pai); pai.rotation_mode = "QUATERNION"; pai.scale = (0, 0, 0)
    for nm, tam, mat in (("Corpo", 3.0, M_COR), ("Nucleo", 1.3, M_NUC)):
        o = plano(nome + "_" + nm, tam, tam, mat); o.parent = pai; c = o.constraints.new("DAMPED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"
    ca = cauda_mesh(nome + "_Cauda"); ca.parent = pai                      # cauda ao longo de -Y local (= para tras da trajetoria)
    c = ca.constraints.new("LOCKED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_Z"; c.lock_axis = "LOCK_Y"
    imp = plano(nome + "_Impacto", 6.0, 6.0, M_IMP); imp["abre"] = 0.0; imp.scale = (0, 0, 0)
    c = imp.constraints.new("DAMPED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"
    return {"pai": pai, "imp": imp}
PROJ = {k: criar_proj("Projetil_" + k) for k in "CED"}
def simular(p0, d0, alvo_em, vel=40.0, giro=math.pi, vida=2.0, alcance=30.0, raio_acerto=1.6):
    """SIMULACAO DE BLENDER do projetil (v6.2: curva max 180 graus/s, vida 2 s, ate 30 studs; velocidade [A TESTAR])"""
    dt = 1.0 / FPS; p = V(p0); d = V(d0).normalized(); pts = [(p.copy(), d.copy())]; perc = 0.0; t = 0.0
    while True:
        t += dt; alvo = alvo_em(t)
        if alvo is not None:
            quer = (alvo - p).normalized(); ang = d.angle(quer) if d.length and quer.length else 0.0
            if ang > 1e-6:
                eixo = d.cross(quer)
                if eixo.length < 1e-6: eixo = V((0, 0, 1))
                d = (Matrix.Rotation(min(ang, giro * dt), 3, eixo.normalized()) @ d).normalized()
        p = p + d * vel * dt; perc += vel * dt; pts.append((p.copy(), d.copy()))
        if alvo is not None and (alvo - p).length < raio_acerto: return pts, {"resultado": "acertou", "tempo_s": round(t, 3), "percorrido_studs": round(perc, 2), "ponto": p}
        if perc >= alcance or t >= vida: return pts, {"resultado": "dissipou no limite", "tempo_s": round(t, 3), "percorrido_studs": round(perc, 2), "ponto": p}
def animar_proj(pr, f0, pts, info):
    pai, imp = pr["pai"], pr["imp"]
    k_obj(pai, "scale", f0 - 1, (0, 0, 0))
    for i, (p, d) in enumerate(pts):
        pai.location = p; pai.rotation_quaternion = d.to_track_quat("Y", "Z"); pai.keyframe_insert("location", frame=f0 + i); pai.keyframe_insert("rotation_quaternion", frame=f0 + i)
        if i == 0: pai.scale = (1, 1, 1); pai.keyframe_insert("scale", frame=f0)
    fh = f0 + len(pts) - 1; pai.scale = (1, 1, 1); pai.keyframe_insert("scale", frame=fh); pai.scale = (0, 0, 0); pai.keyframe_insert("scale", frame=fh + 1)
    imp.location = info["ponto"]; imp.keyframe_insert("location", frame=fh)
    k_obj(imp, "scale", fh - 1, (0, 0, 0)); k_obj(imp, "scale", fh, (1, 1, 1)); k_obj(imp, "scale", fh + 8, (1, 1, 1)); k_obj(imp, "scale", fh + 9, (0, 0, 0))
    imp["abre"] = 0.0; imp.keyframe_insert('["abre"]', frame=fh); imp["abre"] = 1.0; imp.keyframe_insert('["abre"]', frame=fh + 8)
    return fh
# ================================================================== r4: PROJETIL COM VOLUME (substitui a "bolinha" da r3)
# Partes: Lingua (chama alongada na direcao do voo, de frente para a camera em volta do eixo do voo), Bola (silhueta irregular
# com linguas, vista de frente), Nucleo pequeno e quente, CAMADAS de cauda (sopros que ficam na trajetoria e envelhecem
# laranja -> vermelho -> somem, entao acompanham a curva), ACUMULO na boca antes do disparo e IMPACTO = expansao curta de chamas
# na superficie (linguas verticais + estouro irregular), sem anel. Propriedades de objeto: "idade" (0 novo -> 1 velho), "semente".
def mat_r4_lingua(nome="M_R4_Lingua"):
    m, nt, em, mx, sp = mat_base(nome)
    u, v = sp.outputs["X"], sp.outputs["Y"]
    ida = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="idade").outputs["Fac"]
    sem = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="semente").outputs["Fac"]
    vec = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", u, 1.7), vec.inputs["X"])
    nt.links.new(op(nt, "ADD", op(nt, "MULTIPLY", v, 2.6), op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 6.0)), vec.inputs["Y"]); nt.links.new(sem, vec.inputs["Z"])
    nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 2.4; nz.inputs["Detail"].default_value = 4.0
    nz.inputs["Distortion"].default_value = 0.6; nt.links.new(vec.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 1.7), nz.inputs["W"])
    frente = op(nt, "SQRT", op(nt, "MINIMUM", op(nt, "MULTIPLY", v, 7.0), 1.0))                  # ponta da frente arredondada
    larg = op(nt, "MULTIPLY", op(nt, "MULTIPLY", op(nt, "POWER", op(nt, "SUBTRACT", 1.0, v), 0.8), frente), 0.46)
    rasgo = op(nt, "MULTIPLY", op(nt, "SUBTRACT", nz.outputs["Fac"], 0.5), op(nt, "ADD", 0.16, op(nt, "MULTIPLY", v, 0.34)))   # borda irregular, mais rasgada atras
    dx = op(nt, "ADD", op(nt, "ABSOLUTE", op(nt, "SUBTRACT", u, 0.5)), rasgo)
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", larg, dx), 7.0), 0.0), 1.0)
    calor = op(nt, "MULTIPLY", op(nt, "MULTIPLY", d, op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", v, 0.62))), op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", ida, 0.55)))
    nt.links.new(rampa(nt, op(nt, "MULTIPLY", calor, 0.95)), em.inputs["Color"])
    nt.links.new(op(nt, "MULTIPLY", calor, 3.0), em.inputs["Strength"])
    lw = no(nt, "ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.5             # some quando o cartao fica de quina (vista de frente)
    quina = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.93, lw.outputs["Facing"]), 5.0), 0.0), 1.0)
    alfa = op(nt, "MULTIPLY", op(nt, "MINIMUM", op(nt, "MULTIPLY", d, 1.5), 1.0), op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", ida, ida)))
    nt.links.new(op(nt, "MULTIPLY", alfa, quina), mx.inputs[0])
    return m
def mat_r4_bola(nome="M_R4_Bola"):
    """massa de fogo irregular (sem simetria radial): ruido na POSICAO do cartao, linguas subindo (+v), bordas laranja/vermelho"""
    m, nt, em, mx, sp = mat_base(nome)
    ida = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="idade").outputs["Fac"]
    sem = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="semente").outputs["Fac"]
    cx = op(nt, "SUBTRACT", sp.outputs["X"], 0.5); cy = op(nt, "SUBTRACT", sp.outputs["Y"], 0.5)
    r = op(nt, "SQRT", op(nt, "ADD", op(nt, "MULTIPLY", cx, cx), op(nt, "MULTIPLY", cy, cy)))
    vec = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", cx, 2.3), vec.inputs["X"])
    nt.links.new(op(nt, "SUBTRACT", op(nt, "MULTIPLY", cy, 1.7), op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 2.6)), vec.inputs["Y"]); nt.links.new(sem, vec.inputs["Z"])
    nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 2.1; nz.inputs["Detail"].default_value = 6.0
    nz.inputs["Roughness"].default_value = 0.6; nz.inputs["Distortion"].default_value = 1.1
    nt.links.new(vec.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "ADD", op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 1.9), sem), nz.inputs["W"])
    rr = op(nt, "SUBTRACT", op(nt, "SUBTRACT", r, op(nt, "MULTIPLY", op(nt, "SUBTRACT", nz.outputs["Fac"], 0.42), 0.55)), op(nt, "MULTIPLY", cy, 0.10))
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.29, rr), 4.2), 0.0), 1.0)
    calor = op(nt, "MULTIPLY", op(nt, "POWER", d, 1.6), op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", ida, 0.6)))
    nt.links.new(rampa(nt, op(nt, "MULTIPLY", calor, 0.88)), em.inputs["Color"]); nt.links.new(op(nt, "MULTIPLY", calor, 2.6), em.inputs["Strength"])
    nt.links.new(op(nt, "MULTIPLY", op(nt, "MINIMUM", op(nt, "MULTIPLY", d, 1.3), 1.0), op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", ida, ida))), mx.inputs[0])
    return m
def mat_r4_nucleo():
    m, nt, em, mx, sp = mat_base("M_R4_Nucleo")
    dx = op(nt, "SUBTRACT", sp.outputs["X"], 0.5); dy = op(nt, "SUBTRACT", sp.outputs["Y"], 0.5); r = op(nt, "SQRT", op(nt, "ADD", op(nt, "MULTIPLY", dx, dx), op(nt, "MULTIPLY", dy, dy)))
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.5, r), 2.2), 0.0), 1.0)
    nt.links.new(rampa(nt, op(nt, "ADD", 0.62, op(nt, "MULTIPLY", d, 0.33))), em.inputs["Color"]); nt.links.new(op(nt, "MULTIPLY", d, 2.6), em.inputs["Strength"])
    nt.links.new(d, mx.inputs[0]); return m
M4_LIN, M4_BOLA, M4_NUC = mat_r4_lingua(), mat_r4_bola(), mat_r4_nucleo()
def lingua_mesh(nome, comp, larg, eixo="Y"):
    """plano da chama alongada: frente (v = 0) na origem, cauda (v = 1) a -comp em Y (projetil) ou a +comp em Z (lingua de impacto)"""
    me = bpy.data.meshes.new(nome); bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); f0 = 0.35 * larg
    if eixo == "Y": pts = [(-larg / 2, f0, 0), (larg / 2, f0, 0), (larg / 2, -comp, 0), (-larg / 2, -comp, 0)]
    else: pts = [(-larg / 2, 0, -f0), (larg / 2, 0, -f0), (larg / 2, 0, comp), (-larg / 2, 0, comp)]
    f_ = bm.faces.new([bm.verts.new(p) for p in pts])
    for lp, uvv in zip(f_.loops, ((0, 0), (1, 0), (1, 1), (0, 1))): lp[uvl].uv = uvv
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(nome, me); sc.collection.objects.link(o); o.data.materials.append(M4_LIN); return o
def bill(nome, tam, mat, sem):
    o = plano(nome, tam, tam, mat); o["idade"] = 0.0; o["semente"] = sem; c = o.constraints.new("DAMPED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"; return o
N_SOPRO, N_LING_IMP = 10, 7
ESC_PROJ = 1.7                                                # r4b: projetil maior (so visual; o raio de acerto nao muda) [A TESTAR]
R4_OBJS = []
def criar_proj_r4(nome, k):
    sem0 = {"C": 1.3, "E": 4.7, "D": 8.1}[k]
    pai = bpy.data.objects.new(nome, None); sc.collection.objects.link(pai); pai.rotation_mode = "QUATERNION"; pai.scale = (0, 0, 0)
    lin_ = lingua_mesh(nome + "_Lingua", 3.6 * ESC_PROJ, 1.9 * ESC_PROJ); lin_.parent = pai; lin_["idade"] = 0.0; lin_["semente"] = sem0
    c = lin_.constraints.new("LOCKED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_Z"; c.lock_axis = "LOCK_Y"
    bola = bill(nome + "_Bola", 2.9 * ESC_PROJ, M4_BOLA, sem0 + 0.4); bola.parent = pai
    camadas = []
    for i_, (yy, tam) in enumerate(((-0.9, 2.5), (-1.8, 2.1))):                  # massa em camadas atras da frente (volume de frente)
        o = bill(nome + "_Camada%d" % i_, tam * ESC_PROJ, M4_BOLA, sem0 + 5.3 + i_); o.parent = pai; o.location = (0.15 * (1 - 2 * i_) * ESC_PROJ, yy * ESC_PROJ, 0.1 * ESC_PROJ); camadas.append(o)
    nuc = plano(nome + "_Nucleo", 0.75 * ESC_PROJ, 0.75 * ESC_PROJ, M4_NUC); nuc.parent = pai; c = nuc.constraints.new("DAMPED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"
    sopros = [bill(nome + "_Sopro%d" % i, 1.5 * ESC_PROJ, M4_BOLA, sem0 + 0.9 * i + 2.0) for i in range(N_SOPRO)]
    acum = [bill(nome + "_Acumulo%d" % i, 1.0 * ESC_PROJ, M4_BOLA, sem0 + 11 + i) for i in range(3)]
    linguas = []
    for i in range(N_LING_IMP):
        o = lingua_mesh(nome + "_ImpLingua%d" % i, 2.8 * ESC_PROJ, 1.25 * ESC_PROJ, eixo="Z"); o["idade"] = 0.0; o["semente"] = sem0 + 20 + i
        c = o.constraints.new("LOCKED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"; c.lock_axis = "LOCK_Z"; linguas.append(o)
    estouro = bill(nome + "_Estouro", 2.6 * ESC_PROJ, M4_BOLA, sem0 + 30)
    pr = {"pai": pai, "lingua": lin_, "bola": bola, "nucleo": nuc, "camadas": camadas, "sopros": sopros, "acum": acum, "linguas": linguas, "estouro": estouro}
    for o in [lin_, bola, nuc] + camadas + sopros + acum + linguas + [estouro]:
        if o.parent is None: o.scale = (0, 0, 0)
        R4_OBJS.append(o)
    R4_OBJS.append(pai); return pr
PROJ4 = {k: criar_proj_r4("ProjR4_" + k, k) for k in "CED"}
def k_prop(o, nome, f, v): o[nome] = v; o.keyframe_insert('["%s"]' % nome, frame=f)
def zerar_r4(pr, f):
    k_obj(pr["pai"], "scale", f, (0, 0, 0))
    for o in pr["sopros"] + pr["acum"] + pr["linguas"] + [pr["estouro"]]: k_obj(o, "scale", f, (0, 0, 0))
def animar_proj_r4(pr, k, f0, pts, info, acerto=True, centro_alvo=None):
    """acumulo na boca (8 quadros antes do disparo) -> voo com lingua que cresce do ponto de saida (nao atravessa o focinho) e
    sopros que ficam na trajetoria -> impacto (linguas na superficie + estouro) OU dissipacao no limite"""
    pai, lin_, bola, nuc = pr["pai"], pr["lingua"], pr["bola"], pr["nucleo"]
    # ACUMULO: tres chamas pequenas a frente dos labios, crescendo e girando; seguem a cabeca quadro a quadro
    for j, o in enumerate(pr["acum"]):
        k_obj(o, "scale", f0 - 9, (0, 0, 0)); k_prop(o, "idade", f0 - 9, 0.5)
        for q in range(f0 - 8, f0 + 1):
            p, fr = boca_mundo(k, q); prog = (q - (f0 - 9)) / 9.0
            lat = fr.cross(V((0, 0, 1))).normalized(); ang = 2.1 * j + 0.9 * (q - f0)
            o.location = p + fr * (1.05 + 0.2 * prog) * ESC_PROJ + (lat * math.cos(ang) + V((0, 0, 1)) * math.sin(ang)) * 0.22 * ESC_PROJ * (1 - 0.6 * prog)
            o.keyframe_insert("location", frame=q); k_obj(o, "scale", q, tuple(V((1, 1, 1)) * (0.45 + 1.35 * prog)))
        k_prop(o, "idade", f0, 0.0); k_obj(o, "scale", f0 + 1, (0, 0, 0))
    # VOO
    p_ini = pts[0][0]; k_obj(pai, "scale", f0 - 1, (0, 0, 0)); fim_voo = f0 + len(pts) - 1
    for i, (p, d) in enumerate(pts):
        f = f0 + i; pai.location = p; pai.rotation_quaternion = d.to_track_quat("Y", "Z")
        pai.keyframe_insert("location", frame=f); pai.keyframe_insert("rotation_quaternion", frame=f)
        cresce = min(1.0, 0.15 + (p - p_ini).length / (3.6 * ESC_PROJ))                         # a lingua so se estende para tras depois de sair da boca
        k_obj(lin_, "scale", f, (1.0, cresce, 1.0))
        if i == 0: k_obj(pai, "scale", f, (1, 1, 1))
    k_obj(pai, "scale", fim_voo, (1, 1, 1))
    # SOPROS: um a cada 2 quadros, ficam onde nasceram (acompanham a curva), sobem um pouco, crescem e envelhecem em 8 quadros
    for i in range(0, len(pts), 2):
        o = pr["sopros"][(i // 2) % N_SOPRO]; f = f0 + i; p, d = pts[i]; up = V((0, 0, 1))
        lat = d.cross(up).normalized() if d.cross(up).length > 1e-6 else V((1, 0, 0))
        jit = lat * (0.25 * math.sin(i * 1.7)) + up * (0.2 * math.cos(i * 2.3))
        k_obj(o, "scale", f - 1, (0, 0, 0)); k_obj(o, "location", f, tuple(p - d * 0.6 * ESC_PROJ + jit * ESC_PROJ)); k_obj(o, "scale", f, (0.8, 0.8, 0.8)); k_prop(o, "idade", f, 0.05)
        k_obj(o, "location", f + 8, tuple(p - d * 0.6 * ESC_PROJ + jit * ESC_PROJ + up * 0.5 * ESC_PROJ)); k_obj(o, "scale", f + 4, (1.15, 1.15, 1.15)); k_obj(o, "scale", f + 8, (0.55, 0.55, 0.55))
        k_prop(o, "idade", f + 8, 1.0); k_obj(o, "scale", f + 9, (0, 0, 0))
    if acerto:                                                    # IMPACTO na superficie do alvo: linguas verticais + estouro, ~0,33 s
        k_obj(pai, "scale", fim_voo + 1, (0, 0, 0))
        ph = info["ponto"]; c_ = centro_alvo if centro_alvo is not None else ph
        n_ = V((ph.x - c_.x, ph.y - c_.y, 0)); n_ = n_.normalized() if n_.length > 1e-6 else -pts[-1][1]
        tg = n_.cross(V((0, 0, 1))).normalized()
        for j, o in enumerate(pr["linguas"]):
            off = (j - (N_LING_IMP - 1) / 2) * 0.42 * ESC_PROJ; alt = 1.0 - abs(off / ESC_PROJ) * 0.45 + 0.25 * math.sin(j * 2.9)
            base = ph + n_ * 0.12 + V((0, 0, (-0.7 - 0.15 * abs(off / ESC_PROJ)) * ESC_PROJ))
            k_obj(o, "scale", fim_voo, (0, 0, 0)); k_obj(o, "location", fim_voo, tuple(base + tg * off * 0.6)); k_prop(o, "idade", fim_voo, 0.0)
            k_obj(o, "scale", fim_voo + 3, (alt, alt, alt)); k_obj(o, "location", fim_voo + 3, tuple(base + tg * off))
            k_obj(o, "scale", fim_voo + 6, (alt * 1.1, alt * 1.1, alt * 1.25)); k_prop(o, "idade", fim_voo + 4, 0.25)
            k_obj(o, "location", fim_voo + 10, tuple(base + tg * off * 1.35 + V((0, 0, 0.9 * ESC_PROJ)))); k_obj(o, "scale", fim_voo + 10, (alt * 0.4, alt * 0.4, alt * 0.6))
            k_prop(o, "idade", fim_voo + 10, 1.0); k_obj(o, "scale", fim_voo + 11, (0, 0, 0))
        e = pr["estouro"]; k_obj(e, "scale", fim_voo - 1, (0, 0, 0)); k_obj(e, "location", fim_voo, tuple(ph + n_ * 0.3 * ESC_PROJ)); k_prop(e, "idade", fim_voo, 0.0)
        k_obj(e, "scale", fim_voo, (0.8, 0.8, 0.8)); k_obj(e, "scale", fim_voo + 4, (1.5, 1.5, 1.5)); k_prop(e, "idade", fim_voo + 4, 0.45)
        k_obj(e, "scale", fim_voo + 8, (1.7, 1.7, 1.7)); k_prop(e, "idade", fim_voo + 8, 1.0); k_obj(e, "scale", fim_voo + 9, (0, 0, 0))
    else:                                                         # DISSIPACAO no limite: encolhe e avermelha em 6 quadros
        for o in [lin_, bola, nuc] + pr["camadas"]: k_prop(o, "idade", fim_voo - 6, 0.0); k_prop(o, "idade", fim_voo, 1.0)
        k_obj(pai, "scale", fim_voo - 6, (1, 1, 1)); k_obj(pai, "scale", fim_voo, (0.35, 0.35, 0.35)); k_obj(pai, "scale", fim_voo + 1, (0, 0, 0))
    return fim_voo

mal = bpy.data.materials.new("M_Alvo"); mal.use_nodes = True; mal.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.35, 0.33, 0.3, 1)
mal.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = (0.9, 0.9, 0.95, 1); mal.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.15
ALVOS = []
def alvo_poste(nome, centro):
    bpy.ops.mesh.primitive_cylinder_add(radius=0.9, depth=centro.z + 1.4, vertices=16, location=(centro.x, centro.y, (centro.z + 1.4) / 2))
    o = bpy.context.object; o.name = nome; o.data.materials.append(mal); ALVOS.append(o); return o
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
FAIXA.parent = rig                                            # r3: gira junto na mudanca de direcao
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
VISTAS = {"aberta": ((-58, -26, 24), (2, -26, 8), 30),     # r4: lateral alta (boca ate 30 studs no quadro)
           "aberta_r3": ((-22, -60, 40), (4, -14, 6), 30),     # frente-alto: cabecas e os 3 alvos em quadro
           "34": ((-30, -32, 19), (0, -1, 9), 50), "perfilcab": ((-46, -13, 17), (0, -13, 13), 45),
           "jogo": ((9, 38, 44), (0, -26, 4), 34),            # r4: camera de jogo (atras e acima do Cerbero, olhando os alvos)
           "distante": ((-62, -58, 18), (0, -18, 8), 45),     # r4: observador a ~80 studs (distancia de jogo)
           "cab": ((-6, -34, 17), (0, -8, 14.5), 50), "lado": ((-48, 2, 9), (0, 4, 8.5), 50)}
def vista(n):
    pos, alvo, lente = VISTAS[n]; cam.location = pos; cam.rotation_euler = (V(alvo) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = lente; ALVO.location = pos
MATS_PELE = [m for o in (CORPO, CAB) for m in o.data.materials]; MAT_BOCA = BOCA.data.materials[0]
TODOS_MATS = [m for m in bpy.data.materials if m.use_nodes and m.node_tree and "tempo" in m.node_tree.nodes]
def limpar_chaves():
    for m in bpy.data.materials:
        if m.node_tree and m.node_tree.animation_data: m.node_tree.animation_data_clear()
    for o in CHAMAS + [p_["pai"] for p_ in PROJ.values()] + [p_["imp"] for p_ in PROJ.values()] + [FAIXA, rig] + VENTOS + ALVOS + R4_OBJS:
        if o.animation_data: o.animation_data_clear()
    rig.rotation_euler = (0, 0, 0)
    for o in ALVOS: bpy.data.objects.remove(o)
    ALVOS.clear()
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
    elif prop == "violeta": o["violeta"] = v; o.keyframe_insert('["violeta"]', frame=f)
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
    """r3: (nome, repeticoes[, ate_quadro]) em sequencia; ate_quadro corta o trecho (ex.: meio segundo de Repouso)"""
    if not rig.animation_data: rig.animation_data_create()
    rig.animation_data.action = None
    for tr in list(rig.animation_data.nla_tracks): rig.animation_data.nla_tracks.remove(tr)
    tr = rig.animation_data.nla_tracks.new(); f = 1
    for parte in partes:
        nome, rep_ = parte[0], parte[1]; a = bpy.data.actions["Cerbero_" + nome]; n = int(a.frame_range[1] - a.frame_range[0]) + 1
        st = tr.strips.new(nome + str(f), f, a)
        if len(parte) > 2: st.action_frame_end = a.frame_range[0] + parte[2] - 1; n = parte[2]; st.frame_end = f + n - 1
        else: st.repeat = rep_
        f += n * (1 if len(parte) > 2 else rep_)
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
def render(nome_fx, fim, vistas, quadros, videos=None):
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
        for v in (videos or vistas):
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
    for p_ in PROJ.values(): k_obj(p_["pai"], "scale", 1, (0, 0, 0)); k_obj(p_["imp"], "scale", 1, (0, 0, 0))
    for pr in PROJ4.values():
        zerar_r4(pr, 1)
        for o in [pr["lingua"], pr["bola"], pr["nucleo"]] + pr["camadas"] + pr["sopros"] + pr["acum"] + pr["linguas"] + [pr["estouro"]]: k_prop(o, "idade", 1, 0.0)
    for nome, v in (("fx_vio_C", 0.0), ("fx_vio_E", 0.0), ("fx_vio_D", 0.0), ("fx_vio_frente", -0.2), ("fx_vio_global", 1.0)): k_val(MATS_PELE + [MAT_BOCA], nome, 1, v)
    for o in CHAMAS: k_obj(o, "violeta", 1, 0.0)
# ================================================================== BOLA INFERNAL (18/11; ideia do usuario, SUBSTITUI as Chamas Triplices)
# As tres cabecas convergem (clipe BolaInfernal, rig/clipes_L3r5) e cada boca solta um jato que alimenta UMA bola de fogo gigante a
# frente delas; no disparo a bola parte e SEGUE O ALVO (SIMULACAO DE BLENDER; teleguiada de verdade so no Studio). Tudo em camadas
# que o Roblox reproduz: nucleo (Billboard), massa em 3 camadas girando (Billboards), linguas soltando para tras e fumaca
# (ParticleEmitters), luz pontual laranja (PointLight) e explosao no impacto. Valores [A TESTAR].
L3R5 = os.path.join(os.path.dirname(bpy.data.filepath), "..", "rig", "clipes_L3r5")
MANI5 = json.load(open(os.path.join(L3R5, "manifesto_clipes.json"), encoding="utf-8"))
with bpy.data.libraries.load(os.path.join(L3R5, "CR_Cerbero_Anim.blend")) as (src, dst): dst.actions = ["Cerbero_Prev_Bola_Repouso"]
EVB = MANI5["BolaInfernal"]["eventos_s"]; T0B = 0.2                     # a camada comeca em 0,2 s no previo
R_BOLA = 3.4                                                          # raio visual (diametro ~6,8 studs) [A TESTAR]
VEL_BOLA, GIRO_BOLA, VIDA_BOLA, ALC_BOLA = 26.0, math.radians(150), 2.5, 40.0      # [A TESTAR]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def janela(t, a, b, sub=0.2, des=0.2): return suave((t - a) / sub) * (1 - suave((t - (b - des)) / des))
def mat_massa(nome):
    """massa de fogo turbulenta: ruido de posicao girando (propriedade 'giro'), gradiente de temperatura nucleo -> borda"""
    m, nt, em, mx, sp = mat_base(nome)
    ida = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="idade").outputs["Fac"]
    sem = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="semente").outputs["Fac"]
    gir = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="giro").outputs["Fac"]
    bri = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="brilho_b").outputs["Fac"]
    uv = no(nt, "ShaderNodeTexCoord").outputs["UV"]; cen = no(nt, "ShaderNodeVectorMath", operation="SUBTRACT"); nt.links.new(uv, cen.inputs[0]); cen.inputs[1].default_value = (0.5, 0.5, 0)
    rot = no(nt, "ShaderNodeVectorRotate", rotation_type="Z_AXIS"); nt.links.new(cen.outputs[0], rot.inputs["Vector"])
    nt.links.new(op(nt, "MULTIPLY", val(nt, "tempo", 0.0), gir), rot.inputs["Angle"])
    r = no(nt, "ShaderNodeVectorMath", operation="LENGTH"); nt.links.new(cen.outputs[0], r.inputs[0])
    esc = no(nt, "ShaderNodeVectorMath", operation="SCALE"); nt.links.new(rot.outputs[0], esc.inputs[0]); esc.inputs["Scale"].default_value = 2.4
    nz = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz.inputs["Scale"].default_value = 2.2; nz.inputs["Detail"].default_value = 7.0
    nz.inputs["Roughness"].default_value = 0.62; nz.inputs["Distortion"].default_value = 1.3
    ad = no(nt, "ShaderNodeVectorMath", operation="ADD"); nt.links.new(esc.outputs[0], ad.inputs[0])
    cs = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(sem, cs.inputs["X"]); nt.links.new(op(nt, "MULTIPLY", sem, 0.6), cs.inputs["Y"])
    nt.links.new(cs.outputs[0], ad.inputs[1]); nt.links.new(ad.outputs[0], nz.inputs["Vector"]); nt.links.new(op(nt, "ADD", op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 1.6), sem), nz.inputs["W"])
    nz2 = no(nt, "ShaderNodeTexNoise", noise_dimensions="4D"); nz2.inputs["Scale"].default_value = 7.0; nz2.inputs["Detail"].default_value = 3.0
    nt.links.new(ad.outputs[0], nz2.inputs["Vector"]); nt.links.new(op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 3.5), nz2.inputs["W"])
    rr = op(nt, "SUBTRACT", r.outputs["Value"], op(nt, "ADD", op(nt, "MULTIPLY", op(nt, "SUBTRACT", nz.outputs["Fac"], 0.45), 0.38),
                                                    op(nt, "MULTIPLY", op(nt, "SUBTRACT", nz2.outputs["Fac"], 0.5), 0.10)))
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.43, rr), 3.0), 0.0), 1.0)
    # temperatura: alta no centro do cartao, cai na borda; veios mais frios dentro (ruido fino) -> leitura de fogo real, nao disco
    temp = op(nt, "MULTIPLY", op(nt, "MULTIPLY", op(nt, "POWER", d, 1.25), op(nt, "ADD", 0.72, op(nt, "MULTIPLY", nz2.outputs["Fac"], 0.42))),
              op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", ida, 0.65)))
    nt.links.new(rampa(nt, op(nt, "MINIMUM", temp, 0.97)), em.inputs["Color"])
    nt.links.new(op(nt, "MULTIPLY", op(nt, "MULTIPLY", temp, 3.4), bri), em.inputs["Strength"])
    nt.links.new(op(nt, "MULTIPLY", op(nt, "MINIMUM", op(nt, "MULTIPLY", d, 1.25), 1.0), op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", ida, ida))), mx.inputs[0])
    return m
def mat_fumaca():
    m = bpy.data.materials.new("M_Bola_Fumaca"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = no(nt, "ShaderNodeOutputMaterial"); pr = no(nt, "ShaderNodeBsdfPrincipled"); tr = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(pr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    pr.inputs["Base Color"].default_value = (0.045, 0.04, 0.04, 1); pr.inputs["Roughness"].default_value = 1.0
    ida = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="idade").outputs["Fac"]
    sem = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="semente").outputs["Fac"]
    sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0])
    cx = op(nt, "SUBTRACT", sp.outputs["X"], 0.5); cy = op(nt, "SUBTRACT", sp.outputs["Y"], 0.5); r = op(nt, "SQRT", op(nt, "ADD", op(nt, "MULTIPLY", cx, cx), op(nt, "MULTIPLY", cy, cy)))
    v = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", cx, 2.0), v.inputs["X"]); nt.links.new(op(nt, "SUBTRACT", op(nt, "MULTIPLY", cy, 2.0), op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 0.8)), v.inputs["Y"]); nt.links.new(sem, v.inputs["Z"])
    nz = no(nt, "ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5; nz.inputs["Detail"].default_value = 5.0; nt.links.new(v.outputs[0], nz.inputs["Vector"])
    d = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.42, op(nt, "SUBTRACT", r, op(nt, "MULTIPLY", op(nt, "SUBTRACT", nz.outputs["Fac"], 0.5), 0.5))), 3.0), 0.0), 1.0)
    alfa = op(nt, "MULTIPLY", op(nt, "MULTIPLY", d, 0.62), op(nt, "SUBTRACT", 1.0, ida))
    nt.links.new(alfa, mx.inputs[0])
    try: m.surface_render_method = "BLENDED"
    except Exception: pass
    return m
M_MASSA, M_FUMACA = mat_massa("M_Bola_Massa"), mat_fumaca()
def bill_b(nome, tam, mat, sem, giro=0.0):
    o = plano(nome, tam, tam, mat); o["idade"] = 0.0; o["semente"] = sem; o["giro"] = giro; o["brilho_b"] = 1.0
    c = o.constraints.new("DAMPED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"; return o
D = 2 * R_BOLA
BOLA = bpy.data.objects.new("BolaInfernal", None); sc.collection.objects.link(BOLA); BOLA.scale = (0, 0, 0); BOLA.rotation_mode = "QUATERNION"
B_PARTES = []
for i_, (tam, sem, giro, off) in enumerate(((D * 1.30, 3.1, 0.9, (0.15, 0.25, 0.1)), (D * 1.12, 7.7, -1.3, (-0.2, -0.1, -0.15)), (D * 0.95, 12.4, 1.8, (0.05, 0.0, 0.2)))):
    o = bill_b("Bola_Massa%d" % i_, tam, M_MASSA, sem, giro); o.parent = BOLA; o.location = off; B_PARTES.append(o)
B_NUC = plano("Bola_Nucleo", D * 0.55, D * 0.55, M4_NUC); B_NUC.parent = BOLA; c = B_NUC.constraints.new("DAMPED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"
B_CAUDA = lingua_mesh("Bola_Cauda", D * 2.6, D * 1.05); B_CAUDA.parent = BOLA; B_CAUDA.location = (0, -R_BOLA * 0.25, 0)   # cauda continua (cometa)
B_CAUDA["idade"] = 0.0; B_CAUDA["semente"] = 33.3; c = B_CAUDA.constraints.new("LOCKED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_Z"; c.lock_axis = "LOCK_Y"
B_LUZ_D = bpy.data.lights.new("Luz_Bola", "POINT"); B_LUZ_D.color = (1.0, 0.48, 0.14); B_LUZ_D.shadow_soft_size = R_BOLA * 0.8; B_LUZ_D.energy = 0.0
B_LUZ = bpy.data.objects.new("Luz_Bola", B_LUZ_D); sc.collection.objects.link(B_LUZ)
N_LING_B, N_FUM_B = 24, 18
B_LING = [bill_b("Bola_Lingua%d" % i, D * 0.36, M_MASSA, 20 + i * 1.3, 1.5 if i % 2 else -1.5) for i in range(N_LING_B)]
B_FUM = [bill_b("Bola_Fumaca%d" % i, D * 0.9, M_FUMACA, 40 + i * 1.7) for i in range(N_FUM_B)]
B_JATO = {k: lingua_mesh("Bola_Jato_" + k, 10.0, 1.6) for k in "CED"}            # jato de cada boca ate a bola (carga)
for k, o in B_JATO.items():
    o["idade"] = 0.0; o["semente"] = {"C": 2.2, "E": 5.5, "D": 9.9}[k]; o.rotation_mode = "QUATERNION"
    c = o.constraints.new("LOCKED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_Z"; c.lock_axis = "LOCK_Y"
N_EXP = 6; N_CHAO = 12; N_FUM_EXP = 10
B_EXP = [bill_b("Exp_Massa%d" % i, D * 1.4, M_MASSA, 60 + i * 2.1, 0.8 if i % 2 else -0.8) for i in range(N_EXP)]
B_CHAO = []
for i in range(N_CHAO):
    B_CHAO.append(bill_b("Exp_Chao%d" % i, D * 0.6, M_MASSA, 80 + i * 1.3, 1.0 if i % 2 else -1.0))   # fogo irregular no chao (nao cones)
B_FUM_EXP = [bill_b("Exp_Fumaca%d" % i, D * 1.3, M_FUMACA, 100 + i * 1.9) for i in range(N_FUM_EXP)]
# marca queimada no chao (brilho de brasa que apaga em ~2 s)
mq = bpy.data.materials.new("M_Marca"); mq.use_nodes = True; nt = mq.node_tree; nt.nodes.clear()
out = no(nt, "ShaderNodeOutputMaterial"); pr_ = no(nt, "ShaderNodeBsdfPrincipled"); tr = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(pr_.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
pr_.inputs["Base Color"].default_value = (0.01, 0.008, 0.007, 1); pr_.inputs["Roughness"].default_value = 1.0; pr_.inputs["Emission Color"].default_value = C_LAR
sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0])
cx = op(nt, "SUBTRACT", sp.outputs["X"], 0.5); cy = op(nt, "SUBTRACT", sp.outputs["Y"], 0.5); rq = op(nt, "SQRT", op(nt, "ADD", op(nt, "MULTIPLY", cx, cx), op(nt, "MULTIPLY", cy, cy)))
nzq = no(nt, "ShaderNodeTexNoise"); nzq.inputs["Scale"].default_value = 6.0; nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], nzq.inputs["Vector"])
dq = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.45, op(nt, "ADD", rq, op(nt, "MULTIPLY", nzq.outputs["Fac"], 0.12))), 4.0), 0.0), 1.0)
brasa_q = op(nt, "MULTIPLY", op(nt, "MAXIMUM", op(nt, "SUBTRACT", nzq.outputs["Fac"], 0.55), 0.0), op(nt, "MULTIPLY", dq, 40.0))
nt.links.new(op(nt, "MULTIPLY", brasa_q, val(nt, "fx_marca", 0.0)), pr_.inputs["Emission Strength"])
nt.links.new(op(nt, "MULTIPLY", op(nt, "MULTIPLY", dq, 0.9), op(nt, "MINIMUM", op(nt, "MULTIPLY", val(nt, "fx_marca", 0.0), 3.0), 1.0)), mx.inputs[0])
try: mq.surface_render_method = "BLENDED"
except Exception: pass
MARCA = plano("Exp_Marca", 14.0, 14.0, mq); MARCA.rotation_euler = (math.pi / 2, 0, 0)
B_TODOS = [BOLA, B_LUZ, MARCA, B_CAUDA] + B_PARTES + [B_NUC] + B_LING + B_FUM + list(B_JATO.values()) + B_EXP + B_CHAO + B_FUM_EXP
TODOS_MATS[:] = [m for m in bpy.data.materials if m.use_nodes and m.node_tree and "tempo" in m.node_tree.nodes]
VISTAS.update({"bola34": ((-30, -40, 22), (0, -14, 14), 50), "formacao": ((-12, -36, 18), (0, -9, 15), 42)})
def zerar_bola():
    for o in B_TODOS:
        if o.animation_data: o.animation_data_clear()
    if B_LUZ_D.animation_data: B_LUZ_D.animation_data_clear()
    for o in [BOLA] + B_LING + B_FUM + list(B_JATO.values()) + B_EXP + B_CHAO + B_FUM_EXP: k_obj(o, "scale", 1, (0, 0, 0))
    B_LUZ_D.energy = 0.0; B_LUZ_D.keyframe_insert("energy", frame=1); k_val([mq], "fx_marca", 1, 0.0)
def centro_carga(f):
    """ponto de formacao: media das bocas + a frente (horizontal) R_BOLA*1.15; a bola nao toca nos focinhos"""
    ps, fs = zip(*(boca_mundo(k, f) for k in "CED")); m_ = sum(ps, V()) / 3; fr = sum(fs, V()); fr = V((fr.x, fr.y, 0)).normalized()
    return m_ + fr * R_BOLA * 1.15, fr, ps
def bola_lancar(nome, alvo_em, centro_alvo_fn=None, fim_s=5.0):
    """carga (jatos das tres bocas, bola cresce) -> disparo -> voo teleguiado (SIMULACAO) -> explosao ou dissipacao"""
    limpar_chaves(); zerar_bola(); fim = F(fim_s); nla([("Prev_Bola_Repouso", 1), ("Repouso", 1)]); tempo_linear(1, fim); repouso_base(fim)
    for o in CHAMAS: o.rotation_euler = o["rot_repouso"]
    tc0, tcm, tdp = T0B + EVB["carga_inicio"], T0B + EVB["carga_max"], T0B + EVB["disparo"]
    # pele/olhos/bocas acendem na carga (as tres cabecas juntas)
    for k in "CED":
        curva(MATS_PELE, "fx_cab_" + k, [(F(tc0 - 0.1), 0.0), (F(tcm), 1.3), (F(tdp + 0.15), 0.4), (F(tdp + 0.6), 0.0)])
        curva([MAT_BOCA], "fx_boca_" + k, [(F(tc0 - 0.05), 0.0), (F(tc0 + 0.2), 2.6), (F(tdp), 3.0), (F(tdp + 0.25), 0.0)])
    curva(MATS_PELE, "fx_olhos", [(F(tc0), 1.0), (F(tcm), 2.0), (F(tdp + 0.5), 1.0)])
    # CARGA: quadro a quadro (a bola segue as cabecas enquanto cresce)
    fa, fb = F(tc0), F(tdp)
    for f in range(fa, fb + 1):
        c_, fr, ps = centro_carga(f); u = (f - fa) / (fb - fa); cres = suave(u * 1.15) * (1 + 0.05 * math.sin(f * 1.9))
        BOLA.location = c_; BOLA.keyframe_insert("location", frame=f); k_obj(BOLA, "scale", f, (cres,) * 3)
        BOLA.rotation_quaternion = fr.to_track_quat("Y", "Z"); BOLA.keyframe_insert("rotation_quaternion", frame=f); k_obj(B_CAUDA, "scale", f, (0, 0, 0))
        B_LUZ.location = c_; B_LUZ.keyframe_insert("location", frame=f); B_LUZ_D.energy = 9000.0 * cres; B_LUZ_D.keyframe_insert("energy", frame=f)
        for k, p in zip("CED", ps):
            o = B_JATO[k]; dv = c_ - p; o.location = c_; o.rotation_quaternion = dv.normalized().to_track_quat("Y", "Z"); o.keyframe_insert("location", frame=f)
            o.keyframe_insert("rotation_quaternion", frame=f); jato = janela(u, 0.0, 1.02, 0.18, 0.12)
            k_obj(o, "scale", f, (0.7 + 0.5 * cres, max(0.01, (dv.length - R_BOLA * 0.2) / 10.0) * jato, 1.0))
    k_obj(BOLA, "scale", fa - 1, (0, 0, 0))
    for o in B_JATO.values(): k_obj(o, "scale", fa - 1, (0, 0, 0)); k_obj(o, "scale", fb + 1, (0, 0, 0))
    # VOO teleguiado
    c0, fr0, _ = centro_carga(fb)
    pts, info = simular(c0, fr0, lambda t: alvo_em(tdp + t), vel=VEL_BOLA, giro=GIRO_BOLA, vida=VIDA_BOLA, alcance=ALC_BOLA, raio_acerto=R_BOLA + 0.9)
    for i, (p, d) in enumerate(pts[1:], 1):
        f = fb + i; BOLA.location = p; BOLA.keyframe_insert("location", frame=f); BOLA.rotation_quaternion = d.to_track_quat("Y", "Z"); BOLA.keyframe_insert("rotation_quaternion", frame=f)
        k_obj(B_CAUDA, "scale", f, (min(1.0, 0.4 + i / 8.0), min(1.0, 0.1 + i / 8.0), 1)); B_LUZ.location = p; B_LUZ.keyframe_insert("location", frame=f)
        k_obj(BOLA, "scale", f, ((1 + 0.04 * math.sin(f * 2.3)),) * 3); B_LUZ_D.energy = 10000.0 * (1 + 0.15 * math.sin(f * 3.1)); B_LUZ_D.keyframe_insert("energy", frame=f)
    fh = fb + len(pts) - 1
    # linguas soltando da superficie e ficando para tras; fumaca atras do fogo (carga: poucas; voo: continuas)
    li = fu = 0
    for i, (p, d) in enumerate(pts):
        f = fb + i; up = V((0, 0, 1)); lat = d.cross(up).normalized() if d.cross(up).length > 1e-6 else V((1, 0, 0))
        a = 2.399 * i; sup = (lat * math.cos(a) + up * math.sin(a)) * R_BOLA * 0.45
        o = B_LING[li % N_LING_B]; li += 1
        k_obj(o, "scale", f - 1, (0, 0, 0)); k_obj(o, "location", f, tuple(p + sup - d * R_BOLA * 0.5)); k_obj(o, "scale", f, (0.8,) * 3); k_prop(o, "idade", f, 0.0)
        k_obj(o, "location", f + 10, tuple(p + sup * 0.7 - d * R_BOLA * 1.1 + up * 0.6)); k_obj(o, "scale", f + 5, (1.15,) * 3); k_obj(o, "scale", f + 10, (0.45,) * 3)
        k_prop(o, "idade", f + 10, 1.0); k_obj(o, "scale", f + 11, (0, 0, 0))
        if i % 2 == 0:
            o = B_FUM[fu % N_FUM_B]; fu += 1; pf = p - d * R_BOLA * 1.1 + up * 0.5
            k_obj(o, "scale", f - 1, (0, 0, 0)); k_obj(o, "location", f, tuple(pf)); k_obj(o, "scale", f, (0.6,) * 3); k_prop(o, "idade", f, 0.0)
            k_obj(o, "location", f + 24, tuple(pf + up * 3.5)); k_obj(o, "scale", f + 24, (1.5,) * 3); k_prop(o, "idade", f + 24, 1.0); k_obj(o, "scale", f + 25, (0, 0, 0))
    k_obj(BOLA, "scale", fh, (1, 1, 1))
    acerto = info["resultado"] == "acertou"
    if acerto:                                                  # EXPLOSAO: massa que abre, linguas no chao, fumaca subindo, clarao, marca
        ph = info["ponto"]; k_obj(BOLA, "scale", fh + 1, (0, 0, 0))
        B_LUZ_D.energy = 26000.0; B_LUZ_D.keyframe_insert("energy", frame=fh + 1); B_LUZ_D.energy = 6000.0; B_LUZ_D.keyframe_insert("energy", frame=fh + 10)
        B_LUZ_D.energy = 0.0; B_LUZ_D.keyframe_insert("energy", frame=fh + 30)
        for j, o in enumerate(B_EXP):
            a = 2 * math.pi * j / N_EXP; dd = V((math.cos(a), math.sin(a), 0.6 + 0.3 * math.sin(j))) * R_BOLA * 0.35
            k_obj(o, "scale", fh, (0, 0, 0)); k_obj(o, "location", fh, tuple(ph)); k_obj(o, "scale", fh + 1, (0.9,) * 3); k_prop(o, "idade", fh + 1, 0.0)
            k_obj(o, "location", fh + 9, tuple(ph + dd * 2.2 + V((0, 0, 1.5)))); k_obj(o, "scale", fh + 6, (1.8,) * 3); k_prop(o, "idade", fh + 6, 0.3)
            k_obj(o, "scale", fh + 14, (2.0,) * 3); k_prop(o, "idade", fh + 14, 1.0); k_obj(o, "scale", fh + 15, (0, 0, 0))
        chao = V((ph.x, ph.y, 0.0))
        for j, o in enumerate(B_CHAO):
            a = 2 * math.pi * j / N_CHAO + 0.2 * math.sin(j); alt = 0.8 + 0.35 * math.sin(j * 2.7)
            k_obj(o, "scale", fh, (0, 0, 0)); k_obj(o, "location", fh, tuple(chao + V((math.cos(a), math.sin(a), 0)) * 1.5 + V((0, 0, 1.2)))); k_prop(o, "idade", fh, 0.0)
            k_obj(o, "location", fh + 8, tuple(chao + V((math.cos(a), math.sin(a), 0)) * 6.5 + V((0, 0, 1.4)))); k_obj(o, "scale", fh + 4, (alt,) * 3)
            k_obj(o, "scale", fh + 12, (alt * 0.8, alt * 0.8, alt * 1.2)); k_prop(o, "idade", fh + 10, 0.5)
            k_obj(o, "location", fh + 20, tuple(chao + V((math.cos(a), math.sin(a), 0)) * 8.0 + V((0, 0, 1.0)))); k_obj(o, "scale", fh + 20, (0.3,) * 3)
            k_prop(o, "idade", fh + 20, 1.0); k_obj(o, "scale", fh + 21, (0, 0, 0))
        for j, o in enumerate(B_FUM_EXP):
            a = 2 * math.pi * j / N_FUM_EXP; f0 = fh + 4 + j
            k_obj(o, "scale", f0 - 1, (0, 0, 0)); k_obj(o, "location", f0, tuple(ph + V((math.cos(a), math.sin(a), 0)) * 2.0)); k_obj(o, "scale", f0, (0.6,) * 3)
            k_prop(o, "idade", f0, 0.0); k_obj(o, "location", f0 + 40, tuple(ph + V((math.cos(a) * 3.5, math.sin(a) * 3.5, 9.0)))); k_obj(o, "scale", f0 + 40, (1.8,) * 3)
            k_prop(o, "idade", f0 + 40, 1.0); k_obj(o, "scale", f0 + 41, (0, 0, 0))
        MARCA.location = (ph.x, ph.y, 0.05); MARCA.keyframe_insert("location", frame=fh)
        curva([mq], "fx_marca", [(fh, 0.0), (fh + 3, 1.0), (fh + 60, 0.0)])
    else:                                                       # dissipa no limite: encolhe, avermelha, fumaca segue
        for o in B_PARTES + [B_NUC]: k_prop(o, "idade", fh - 8, 0.0); k_prop(o, "idade", fh, 1.0)
        k_obj(BOLA, "scale", fh - 8, (1, 1, 1)); k_obj(BOLA, "scale", fh, (0.3,) * 3); k_obj(BOLA, "scale", fh + 1, (0, 0, 0))
        B_LUZ_D.energy = 10000.0; B_LUZ_D.keyframe_insert("energy", frame=fh - 8); B_LUZ_D.energy = 0.0; B_LUZ_D.keyframe_insert("energy", frame=fh + 1)
    for o in B_PARTES + [B_NUC]:
        if not acerto: continue
        k_prop(o, "idade", fb, 0.0)
    return fim, {"resultado": info["resultado"], "voo_s": info["tempo_s"], "percorrido_studs": info["percorrido_studs"],
                 "disparo_s": round(tdp, 2), "fim_voo_s": round((fh - 1) / FPS, 2)}, (fb, fh)
def brilho_comp():
    """glare suave no compositor (so para a previa; no Roblox = Bloom do Lighting)"""
    try:
        ng = bpy.data.node_groups.new("Comp_Bola", "CompositorNodeTree"); sc.compositing_node_group = ng
        rl = ng.nodes.new("CompositorNodeRLayers"); gl = ng.nodes.new("CompositorNodeGlare"); go = ng.nodes.new("NodeGroupOutput")
        ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        for nm, v in (("Type", "Fog Glow"), ("Quality", "Medium")):
            if nm in gl.inputs:
                try: gl.inputs[nm].default_value = v
                except Exception: pass
        for nm, v in (("Threshold", 1.0), ("Strength", 0.35), ("Size", 0.6)):
            if nm in gl.inputs: gl.inputs[nm].default_value = v
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"]); ng.links.new(gl.outputs["Image"], go.inputs[0]); return True
    except Exception as e:
        print("GLARE_FALHOU", e, flush=True); return False
RELATO["glare_previa"] = brilho_comp()
CUSTO_BOLA = {"PC": {"bola": "1 Billboard nucleo + 3 Billboards de massa + 1 PointLight", "voo": "linguas 30/s x 0,37 s (~11) + fumaca 15/s x 0,8 s (~12)",
                     "explosao": "6 massa + 12 linguas no chao + 10 fumaca (rajada, ~1,5 s) + clarao da luz + Decal da marca", "pico": "~45 particulas + 4 Billboards + 1 luz"},
              "celular": {"proposta": "2 camadas de massa, linguas 15/s, fumaca 6/s, explosao 6+3, sem sombra da luz", "pico": "~20 particulas + 3 Billboards + 1 luz sem sombra"},
              "comparacao": "substitui 3 projeteis da r4b (~45 particulas no pico): custo parecido, uma fonte de luz a mais",
              "nota": "ESTIMATIVA a partir da previa; medir no Roblox (PC e celular, varias criaturas)"}
ALVOS_B = {}
if "bola" in SO:
    fr_ref = centro_carga(F(T0B + EVB["disparo"]))
    c_ini, fr, _ = fr_ref; lat = V((-fr.y, fr.x, 0)); testes = []
    # 1) alvo parado a ~28 studs a frente
    alvo1 = c_ini + fr * 28; alvo1.z = c_ini.z
    fim, rel, _ = bola_lancar("parado", lambda t: alvo1); alvo_poste("Alvo_Parado", alvo1); testes.append({"teste": "alvo parado a 28 studs", **rel})
    render("Bola_parado", fim, ["formacao", "aberta", "bola34", "jogo", "distante"],
           [("carga_inicio", T0B + EVB["carga_inicio"] + 0.1), ("carga_meio", T0B + 0.85), ("carga_max", T0B + EVB["carga_max"]), ("disparo", T0B + EVB["disparo"] + 0.1),
            ("voo", T0B + EVB["disparo"] + 0.5), ("impacto", rel["fim_voo_s"] + 0.15), ("explosao", rel["fim_voo_s"] + 0.45), ("fumaca", rel["fim_voo_s"] + 1.3)],
           videos=["aberta", "bola34", "jogo", "distante"])
    # 2) alvo movel atravessando a frente a 8 studs/s
    ini = c_ini + fr * 24 - lat * 10; ini.z = c_ini.z
    mov_fn = lambda t: ini + lat * 8.0 * t
    fim, rel, _ = bola_lancar("movel", mov_fn); mov = alvo_poste("Alvo_Movel", ini)
    for i in range(0, fim):
        t = i / FPS; mov.location = (mov_fn(t)).to_tuple(); mov.location.z = (ini.z + 1.4) / 2; mov.keyframe_insert("location", frame=1 + i)
    testes.append({"teste": "alvo movel lateral 8 studs/s (SIMULACAO)", **rel})
    render("Bola_movel_SIMULACAO", fim, ["aberta"], [("voo", T0B + EVB["disparo"] + 0.4), ("curva", T0B + EVB["disparo"] + 0.8), ("impacto", rel["fim_voo_s"] + 0.15)],
           videos=["aberta", "jogo"])
    # 3) alvo lateral 60 graus a 18 studs
    lado = Matrix.Rotation(math.radians(60), 3, "Z") @ fr; alvo3 = c_ini + lado * 18; alvo3.z = c_ini.z
    fim, rel, _ = bola_lancar("lateral", lambda t: alvo3); alvo_poste("Alvo_Lateral", alvo3); testes.append({"teste": "alvo lateral 60 graus a 18 studs (SIMULACAO)", **rel})
    render("Bola_lateral_SIMULACAO", fim, ["aberta"], [("voo", T0B + EVB["disparo"] + 0.4), ("curva", T0B + EVB["disparo"] + 0.8), ("fim", rel["fim_voo_s"] + 0.15)],
           videos=["aberta"])
    RELATO["bola"] = {"raio_visual_studs": R_BOLA, "vel_studs_s_A_TESTAR": VEL_BOLA, "giro_graus_s_A_TESTAR": 150, "vida_s": VIDA_BOLA, "alcance_studs_A_TESTAR": ALC_BOLA,
                      "raio_acerto_previa": R_BOLA + 0.9, "testes": testes, "custo_estimado": CUSTO_BOLA}
    print("BOLA_TESTES", testes, flush=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_FX_BolaInfernal.blend"))
json.dump(RELATO, open(os.path.join(OUT, "fx_bola_infernal.json"), "w"), indent=1, ensure_ascii=False, default=str)
print("FX_OK", json.dumps(RELATO, ensure_ascii=False, default=str), flush=True)
