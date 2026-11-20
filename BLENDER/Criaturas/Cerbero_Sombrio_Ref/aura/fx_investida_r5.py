"""Investida r5 (19/11) - pedido "Investida Sombria - rastro e reacao ao tamanho do alvo": rastro novo rente ao chao (fita projetada
no terreno, bordas irregulares, veios de fogo, brasas, linguas baixas nos apoios) e reacao ao porte do alvo (InvestidaSobre /
InvestidaImpacto em rig/clipes_L3r7). Base: fx_teste_alvo.py (intacto). Uso: blender -b -t 2 CR_Cerbero_Fogo_A3.blend -P
fx_investida_r5.py -- <saida> so=sobre,impacto,terreno [video=0]
Teste em ALVO (19/11) - pedido do usuario: "mande o investida e furia, quero que teste em um alvo de criatura ou jogador".
Jogador de teste diante do Cerbero: Investida Sombria (r3) atravessando o jogador e Furia (Rugido r4 + FuriaLoop) com debuff e mordidas.
Cabecalho = fx_poderes_r4b.py (intacto). Uso: blender -b -t 2 CR_Cerbero_Fogo_A3.blend -P fx_teste_alvo.py -- <saida> so=investida_alvo,furia_alvo
r4b (18/11) - pedido do usuario: "Projeteis maiores, e esse som no rugido nao". Projetil x ESC_PROJ (1,7 [A TESTAR])
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
SO = next((a.split("=")[1].split(",") for a in ARGS if a.startswith("so=")), ["comparacao", "chamas", "curva", "furia"])
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
def investida_fx(ti0, fim, virada=None):
    ev = MANI_R["InvestidaR3"]["eventos_s"]; ti, tf, tb = ti0 + ev["impulso"], ti0 + ev["fim_impulso"], ti0 + ev["impulso"] + 4.0
    curva(MATS_PELE, "fx_estica", [(F(ti - 0.05), 0.0), (F(ti + 0.08), 1.0), (F(tf), 1.0), (F(tf + 0.3), 0.55), (F(tb), 0.55), (F(tb + 0.3), 0.0)])
    curva(MATS_PELE, "fx_intens", [(F(ti0 + 0.05), 1.0), (F(ti0 + 0.30), 1.12), (F(ti + 0.08), 1.35), (F(tf), 1.35), (F(tf + 0.3), 1.18), (F(tb), 1.18), (F(tb + 0.3), 1.0)])
    curva(MATS_PELE, "fx_olhos", [(F(ti - 0.05), 1.0), (F(ti + 0.1), 2.0), (F(tb), 2.0), (F(tb + 0.3), 1.0)])
    curva([FAIXA.data.materials[0]], "fx_faixa", [(F(ti), 0.0), (F(ti + 0.1), 1.0), (F(tb), 1.0), (F(tb + 3.0), 0.0)])
    curva([VENTOS[0].data.materials[0]], "fx_vento", [(F(ti), 0.0), (F(ti + 0.15), 1.0), (F(tb), 0.8), (F(tb + 0.3), 0.0)])
    for o in CHAMAS:
        k_obj(o, "rotation_euler", F(ti - 0.05), rot_mix(o, 1.0 if ti0 > 0.6 else 0.0)); k_obj(o, "rotation_euler", F(ti + 0.1), rot_mix(o, 1.8))
        k_obj(o, "rotation_euler", F(tf + 0.2), rot_mix(o, 1.1)); k_obj(o, "rotation_euler", F(tb), rot_mix(o, 1.1)); k_obj(o, "rotation_euler", F(tb + 0.3), rot_mix(o, 1.0))
        e0 = V(o["esc0"]); k_obj(o, "scale", F(ti - 0.05), tuple(e0)); k_obj(o, "scale", F(ti + 0.1), tuple(V((e0.x * 0.8, e0.y, e0.z * 1.5)))); k_obj(o, "scale", F(tf + 0.2), tuple(e0 * 1.15))
        k_obj(o, "brilho", F(ti - 0.05), 1.0); k_obj(o, "brilho", F(ti + 0.1), 1.5); k_obj(o, "brilho", F(tf + 0.3), 1.2)
    if virada:                                               # mudanca de direcao SIMULADA (o jogo gira o modelo)
        t1, t2, ang = virada; k_obj(rig, "rotation_euler", F(t1), (0, 0, 0)); k_obj(rig, "rotation_euler", F(t2), (0, 0, math.radians(ang)))
    return {"impulso_s": [round(ti, 2), round(tf, 2)], "boost_fim_s": round(tb, 2), "faixa_some_s": round(tb + 3.0, 2)}
FURIA_SRC = '''ev = MANI4["FuriaRugidoR4"]["eventos_s"]; pv = MANI4["Prev_FuriaR4"]["eventos_s"]; lp = MANI4["FuriaLoop"]["eventos_s"]
limpar_chaves(); fim = nla([("Prev_FuriaR4", 1)]); tempo_linear(1, fim); repouso_base(fim)
for o in CHAMAS: o.rotation_euler = o["rot_repouso"]
fim_furia = pv["saida"] + 0.8; fade0, fade1 = fim_furia - 1.5, fim_furia            # volta gradual no ultimo 1,5 s
frente = {"C": 0.36, "E": 0.70, "D": 1.06}; pts_f = [(1, -0.2)]
for k in "CED":
    ru, bm_, fe, fc = ev["rugido_" + k], ev["boca_max_" + k], ev["fecha_" + k], ev["fechada_" + k]
    curva(MATS_PELE + [MAT_BOCA], "fx_vio_" + k, [(F(ru), 0.0), (F(bm_), 1.0)])            # violeta acende com a boca abrindo (e com o som)
    curva(MATS_PELE, "fx_cab_" + k, [(F(ru - 0.05), 0.0), (F(bm_), 1.6), (F(fe), 1.5), (F(fc + 0.2), 0.5), (F(fade0), 0.5), (F(fade1), 0.0)])
    curva([MAT_BOCA], "fx_boca_" + k, [(F(ru), 0.0), (F(bm_), 3.0), (F(fe), 2.6), (F(fc), 0.6), (F(fade0), 0.6), (F(fade1), 0.0)])
    pts_f += [(F(bm_), pts_f[-1][1]), (F(fc + 0.1), frente[k])]
    for o in CHAMAS:
        if CAB_DE[o.name] == k:
            e0 = V(o["esc0"]); k_obj(o, "violeta", F(ru), 0.0); k_obj(o, "violeta", F(bm_), 1.0)
            k_obj(o, "brilho", F(ru - 0.05), 1.0); k_obj(o, "brilho", F(bm_), 2.0); k_obj(o, "brilho", F(fe), 1.9); k_obj(o, "brilho", F(fc + 0.2), 1.3)
            k_obj(o, "scale", F(ru - 0.05), tuple(e0)); k_obj(o, "scale", F(bm_), tuple(e0 * 1.7)); k_obj(o, "scale", F(fe), tuple(e0 * 1.6)); k_obj(o, "scale", F(fc + 0.2), tuple(e0 * 1.25))
curva(MATS_PELE, "fx_vio_frente", pts_f)
for o in CHAMAS:                                          # chamas do corpo viram violeta quando a frente passa
    if CAB_DE[o.name] is None:
        u_ = min(1.0, max(0.0, (V(o.matrix_world.translation).y + 12.1) / 24.2)); tpas = None
        for (fa, va), (fb, vb) in zip(pts_f, pts_f[1:]):
            if va <= u_ <= vb and vb > va: tpas = fa + (fb - fa) * (u_ - va) / (vb - va); break
        if tpas: k_obj(o, "violeta", int(tpas) - 2, 0.0); k_obj(o, "violeta", int(tpas) + 3, 1.0)
for o in CHAMAS:
    k_obj(o, "violeta", F(fade0), o["violeta"] if CAB_DE[o.name] else 1.0); k_obj(o, "violeta", F(fade1), 0.0)
    k_obj(o, "brilho", F(fade0), 1.3 if CAB_DE[o.name] else 1.0); k_obj(o, "brilho", F(fade1), 1.0)
    if CAB_DE[o.name]: k_obj(o, "scale", F(fade0), tuple(V(o["esc0"]) * 1.25)); k_obj(o, "scale", F(fade1), o["esc0"])
curva(MATS_PELE + [MAT_BOCA], "fx_vio_global", [(F(fade0), 1.0), (F(fade1), 0.0)])
pts = [(1, -1.0)]
for k in "CED": pts += [(F(ev["boca_max_" + k]), -0.05), (F(ev["fechada_" + k] + 0.1), 1.05)]
curva(MATS_PELE, "fx_onda_pos", pts)
curva(MATS_PELE, "fx_onda_amp", [(F(ev["rugido_C"] - 0.05), 0.0), (F(ev["boca_max_C"]), 0.9), (F(ev["fechada_D"] + 0.1), 0.9), (F(ev["fechada_D"] + 0.3), 0.0)])
curva(MATS_PELE, "fx_intens", [(F(0.1), 1.0), (F(ev["boca_max_C"]), 1.2), (F(fade0), 1.2), (F(fade1), 1.0)])
curva(MATS_PELE, "fx_olhos", [(F(ev["rugido_C"]), 1.0), (F(ev["boca_max_C"]), 2.0), (F(fade0), 2.0), (F(fade1), 1.0)])
curva([VENTOS[0].data.materials[0]], "fx_vento", [(F(ev["rugido_C"]), 0.0), (F(ev["fechada_C"]), 1.0), (F(fade0), 1.0), (F(fade1), 0.0)])
mords = []                                                # mordidas do FuriaLoop: a boca acende no contato (mesmo tempo dos estalos)
for vez in range(2):
    for k in "CED":
        tm = pv["loop"] + 2.0 * vez + lp["contato_" + k]; mords.append(round(tm, 2))
        curva([MAT_BOCA], "fx_boca_" + k, [(F(tm - 0.1), 0.6), (F(tm), 2.4), (F(tm + 0.2), 0.6)])
'''
# ================================================================== TESTE EM ALVO (19/11, pedido "teste em um alvo de criatura ou jogador")
# Jogador de teste (bloco no tamanho de um avatar do Roblox, ~5,5 studs) com barra de vida ILUSTRATIVA (200 PV), lampejo
# vermelho ao levar golpe e tom cinza/apagado quando afetado pelo Rugido Infernal (v6.2 §5.9h). Numeros da v6.2:
#   Investida Sombria: impulso ~12 studs em 0,5 s, 1,0x a 1a criatura atravessada (pequena/media: ATRAVESSA), depois corrida.
#   Furia: Rugido -15% velocidade/-15% dano por 4 s (raio 25); Furia +20% dano por 8 s; mordida basica 17 (v4).
# SIMULACAO DE BLENDER: dano, empurrao e lentidao sao do jogo (servidor); aqui so a leitura visual.
import time as _t
LEVE = True
def _pausa(*_a): _t.sleep(0.5)
bpy.app.handlers.render_post.append(_pausa)
sc.eevee.taa_render_samples = 8
PV_MAX = 200.0; MORD = 17.0
def mat_jogador():
    m = bpy.data.materials.new("M_Jogador"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = no(nt, "ShaderNodeOutputMaterial"); pr = no(nt, "ShaderNodeBsdfPrincipled"); nt.links.new(pr.outputs[0], out.inputs[0])
    cor = no(nt, "ShaderNodeAttribute", attribute_type="OBJECT", attribute_name="cor").outputs["Color"]
    cinza = val(nt, "fx_cinza", 0.0); hit = val(nt, "fx_hit", 0.0)
    mx = no(nt, "ShaderNodeMix", data_type="RGBA"); mx.inputs["B"].default_value = (0.16, 0.16, 0.17, 1)
    nt.links.new(cinza, mx.inputs["Factor"]); nt.links.new(cor, mx.inputs["A"]); nt.links.new(mx.outputs["Result"], pr.inputs["Base Color"])
    pr.inputs["Roughness"].default_value = 0.6; pr.inputs["Emission Color"].default_value = (1.0, 0.12, 0.05, 1)
    nt.links.new(op(nt, "MULTIPLY", hit, 1.6), pr.inputs["Emission Strength"]); return m
M_JOG = mat_jogador()
def caixa(nome, tam, loc, cor, pai):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc); o = bpy.context.object; o.name = nome; o.scale = tam
    o.data.materials.append(M_JOG); o["cor"] = cor; o.parent = pai; return o
JOG = bpy.data.objects.new("Jogador_Teste", None); sc.collection.objects.link(JOG); JOG.rotation_mode = "XYZ"
pele, camisa, calca = (0.85, 0.66, 0.5, 1), (0.12, 0.35, 0.75, 1), (0.15, 0.17, 0.22, 1)
JOG_PARTES = [caixa("J_Torso", (2.0, 1.0, 2.0), (0, 0, 3.0), camisa, JOG), caixa("J_Cabeca", (1.2, 1.2, 1.2), (0, 0, 4.65), pele, JOG),
              caixa("J_BracoE", (0.9, 0.9, 2.0), (-1.45, 0, 3.0), pele, JOG), caixa("J_BracoD", (0.9, 0.9, 2.0), (1.45, 0, 3.0), pele, JOG),
              caixa("J_PernaE", (0.95, 0.95, 2.0), (-0.5, 0, 1.0), calca, JOG), caixa("J_PernaD", (0.95, 0.95, 2.0), (0.5, 0, 1.0), calca, JOG)]
CRI_PARTES = []
def criatura_teste(zb):
    """quadrupede de blocos com a CABECA na altura das bocas do Cerbero (zb); cabeca no +Y local"""
    for o in CRI_PARTES: bpy.data.objects.remove(o)
    CRI_PARTES.clear(); pelo, esc = (0.45, 0.36, 0.28, 1), (0.25, 0.2, 0.16, 1)
    zc = zb - 2.6; hp = zc - 1.8
    CRI_PARTES.extend([caixa("C_Corpo", (3.4, 9.0, 3.6), (0, 0, zc), pelo, JOG), caixa("C_Pescoco", (2.0, 2.6, 2.2), (0, 4.9, zb - 1.2), pelo, JOG),
                       caixa("C_Cabeca", (2.4, 3.0, 2.4), (0, 6.6, zb), esc, JOG), caixa("C_Cauda", (0.8, 3.0, 0.8), (0, -5.8, zc + 0.8), esc, JOG)])
    for i, (x, y) in enumerate(((-1.2, 3.2), (1.2, 3.2), (-1.2, -3.2), (1.2, -3.2))):
        CRI_PARTES.append(caixa("C_Pata%d" % i, (1.1, 1.1, hp), (x, y, hp / 2), pelo, JOG))
    return 6.6 + 1.5                                            # frente da cabeca no Y local
# barra de vida (virada para a camera): fundo escuro + preenchimento verde que encolhe a partir da esquerda
def mat_simples(nome, cor, emi):
    m = bpy.data.materials.new(nome); m.use_nodes = True; p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = cor; p.inputs["Emission Color"].default_value = cor; p.inputs["Emission Strength"].default_value = emi; return m
BARRA = bpy.data.objects.new("Barra_Vida", None); sc.collection.objects.link(BARRA); BARRA.parent = JOG; BARRA.location = (0, 0, 6.3)
c_ = BARRA.constraints.new("DAMPED_TRACK"); c_.target = ALVO; c_.track_axis = "TRACK_NEGATIVE_Y"
fundo = plano("Barra_Fundo", 3.2, 0.42, mat_simples("M_BarraFundo", (0.05, 0.05, 0.05, 1), 0.0)); fundo.parent = BARRA; fundo.location = (0, 0.02, 0)
me = bpy.data.meshes.new("BarraFill"); bm = bmesh.new(); uvl = bm.loops.layers.uv.new()
vs = [bm.verts.new(p) for p in ((0, 0, -0.15), (3.0, 0, -0.15), (3.0, 0, 0.15), (0, 0, 0.15))]; bm.faces.new(vs); bm.to_mesh(me); bm.free()
FILL = bpy.data.objects.new("Barra_Vida_Fill", me); sc.collection.objects.link(FILL); FILL.data.materials.append(mat_simples("M_BarraFill", (0.1, 0.85, 0.2, 1), 1.5))
FILL.parent = BARRA; FILL.location = (-1.5, 0, 0)
M_FILL = FILL.data.materials[0]
def vida(f, pv):
    FILL.scale = (max(0.001, pv / PV_MAX), 1, 1); FILL.keyframe_insert("scale", frame=f)
    k = pv / PV_MAX; c = (0.1 + 0.85 * (1 - k), 0.85 * k + 0.1, 0.15, 1)
    p = M_FILL.node_tree.nodes["Principled BSDF"]
    for nm in ("Base Color", "Emission Color"): p.inputs[nm].default_value = c; p.inputs[nm].keyframe_insert("default_value", frame=f)
def golpe(f, pv_antes, dano):
    """lampejo vermelho + barra cai"""
    k_val([M_JOG], "fx_hit", f - 1, 0.0); k_val([M_JOG], "fx_hit", f, 1.0); k_val([M_JOG], "fx_hit", f + 6, 0.0)
    vida(f, pv_antes); vida(f + 3, pv_antes - dano); return pv_antes - dano
def jog_k(f, loc, rot=(0, 0, 0)):
    JOG.location = loc; JOG.keyframe_insert("location", frame=f); JOG.rotation_euler = rot; JOG.keyframe_insert("rotation_euler", frame=f)
def jog_zerar():
    for o in [JOG, FILL]:
        if o.animation_data: o.animation_data_clear()
    for m in (M_JOG, M_FILL):
        if m.node_tree.animation_data: m.node_tree.animation_data_clear()
    k_val([M_JOG], "fx_hit", 1, 0.0); k_val([M_JOG], "fx_cinza", 1, 0.0); vida(1, PV_MAX)
def boca_y_min(f0, f1):
    return min(min(boca_mundo(k, f)[0].y for k in "CED") for f in range(f0, f1 + 1, 2))
def render_leve(nome_fx, fim, vistas, quadros):
    sc.frame_start, sc.frame_end = 1, fim; sc.render.image_settings.media_type = "IMAGE"; sc.render.image_settings.file_format = "PNG"
    sc.render.resolution_x, sc.render.resolution_y = 640, 450
    for v in vistas:
        vista(v)
        for rot, t in quadros:
            sc.frame_set(F(t)); sc.render.filepath = os.path.join(OUT, "%s_%s_%s.png" % (nome_fx, v, rot)); bpy.ops.render.render(write_still=True)
    if VIDEO:
        sc.render.image_settings.media_type = "VIDEO"; sc.render.image_settings.file_format = "FFMPEG"
        sc.render.ffmpeg.format = "MPEG4"; sc.render.ffmpeg.codec = "H264"; sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
        for v in vistas:
            vista(v); sc.render.filepath = os.path.join(OUT, "FX_%s_%s.mp4" % (nome_fx, v)); bpy.ops.render.render(animation=True)
    print("RENDER", nome_fx, flush=True)
VISTAS.update({"inv_lado": ((-48, -22, 10), (0, -24, 5), 36), "inv_jogo": ((16, 16, 24), (0, -26, 4), 30),
               "fur_34": ((-30, -50, 16), (0, -20, 7), 30), "fur_lado": ((-46, -20, 10), (0, -20, 7), 30)})
RELATO["alvo"] = {"jogador": "bloco ~5,5 studs (avatar R6), barra de vida ILUSTRATIVA de %d PV" % PV_MAX}
# ================================================================== INVESTIDA r5 (19/11): rastro novo + reacao ao tamanho do alvo
# Pedido "Investida Sombria - rastro e reacao ao tamanho do alvo". Clipes novos em rig/clipes_L3r7: InvestidaSobre (alvo com
# METADE do porte: passa POR CIMA) e InvestidaImpacto (alvo MAIOR: termina no contato com mordida das TRES cabecas).
# SIMULACAO VISUAL DE BLENDER: deslocamento, colisao, parada e dano sao do jogo (servidor); nada disso foi testado no Roblox.
import random
L3R7 = os.path.join(os.path.dirname(bpy.data.filepath), "..", "rig", "clipes_L3r7")
MANI7 = json.load(open(os.path.join(L3R7, "manifesto_clipes.json"), encoding="utf-8"))
with bpy.data.libraries.load(os.path.join(L3R7, "CR_Cerbero_Anim.blend")) as (src, dst): dst.actions = ["Cerbero_InvestidaSobre", "Cerbero_InvestidaImpacto"]
for o in JOG_PARTES + [JOG, BARRA, FILL, fundo, FAIXA]: o.hide_render = True        # faixa antiga (presa ao corpo) desligada
LIXO = []
def limpar_secao():
    for o in LIXO:
        for c_ in list(o.children): bpy.data.objects.remove(c_)
        bpy.data.objects.remove(o)
    LIXO.clear()
EVR3, EVS, EVI = MANI_R["InvestidaR3"]["eventos_s"], MANI7["InvestidaSobre"]["eventos_s"], MANI7["InvestidaImpacto"]["eventos_s"]
DUR_R3_, DUR_S, DUR_I = MANI_R["InvestidaR3"]["duracao_s"], MANI7["InvestidaSobre"]["duracao_s"], MANI7["InvestidaImpacto"]["duracao_s"]
T_GAL_ = MANI_R["Corrida"]["duracao_s"] if "Corrida" in MANI_R else 16 / 30; V_C = 22.3; T0 = 0.5
# ------------------------------------------------------------------ medidas do Cerbero (pose de Repouso)
def medir_cerbero():
    limpar_chaves(); nla([("Repouso", 1)]); sc.frame_set(1); dg = bpy.context.evaluated_depsgraph_get()
    vs = []
    for o in (CORPO, CAB):
        me = o.evaluated_get(dg).to_mesh(); M = o.matrix_world; vs += [M @ v.co for v in me.vertices]; o.evaluated_get(dg).to_mesh_clear()
    c2 = rig.matrix_world @ BD["Coluna2"].head_local; dg = bpy.context.evaluated_depsgraph_get()
    me = CORPO.evaluated_get(dg).to_mesh(); M = CORPO.matrix_world
    cern = max((M @ v.co).z for v in me.vertices if abs((M @ v.co).y - c2.y) < 1.0 and abs((M @ v.co).x - c2.x) < 2.0); CORPO.evaluated_get(dg).to_mesh_clear()
    mn = V((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); mx = V((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    return {"cernelha": round(cern, 2), "cernelha_def": "topo do dorso no meio do tronco (Coluna2), sem chamas", "comprimento_bbox": round(mx.y - mn.y, 2), "largura_bbox": round(mx.x - mn.x, 2), "altura_bbox": round(mx.z - mn.z, 2)}
MED = medir_cerbero(); RELATO["medidas_cerbero_studs"] = MED; print("MEDIDAS", MED, flush=True)
# ------------------------------------------------------------------ alvo quadrupede de blocos (atravessado no caminho)
def mat_alvo(nome):
    m = mat_jogador(); m.name = nome; return m
def quadrupede(nome, cern, comp, cor, fr_corpo=0.42):
    """quadrupede de blocos: comprimento no eixo X (atravessado no caminho -Y), dorso na altura da cernelha, cabeca no -X"""
    pai = bpy.data.objects.new(nome, None); sc.collection.objects.link(pai); m = mat_alvo("M_" + nome)
    larg = comp * 0.30; corpo_h = cern * fr_corpo; zc = cern - corpo_h / 2; perna = cern - corpo_h
    pele = (cor[0] * 0.6, cor[1] * 0.6, cor[2] * 0.6, 1)
    def bx(n_, tam, loc, c_):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc); o = bpy.context.object; o.name = n_; o.scale = tam; o.data.materials.append(m); o["cor"] = c_; o.parent = pai; return o
    partes = [bx(nome + "_Corpo", (comp * 0.72, larg, corpo_h), (0, 0, zc), cor),
              bx(nome + "_Pescoco", (comp * 0.14, larg * 0.6, corpo_h * 0.7), (-comp * 0.40, 0, zc + corpo_h * 0.25), cor),
              bx(nome + "_Cabeca", (comp * 0.16, larg * 0.62, corpo_h * 0.62), (-comp * 0.50, 0, zc + corpo_h * 0.30), pele),
              bx(nome + "_Cauda", (comp * 0.16, larg * 0.18, corpo_h * 0.18), (comp * 0.44, 0, zc + corpo_h * 0.25), pele)]
    for i, (x, y) in enumerate(((-0.28, -0.3), (-0.28, 0.3), (0.28, -0.3), (0.28, 0.3))):
        partes.append(bx(nome + "_Pata%d" % i, (larg * 0.30, larg * 0.30, perna), (x * comp, y * larg, perna / 2), pele))
    topo = max(p.location.z + p.scale.z / 2 for p in partes)
    return {"pai": pai, "partes": partes, "mat": m, "topo": topo, "larg": larg, "comp": comp, "cern": cern}
def flash(alvo, f, forte=0.3):
    k_val([alvo["mat"]], "fx_hit", f - 1, 0.0); k_val([alvo["mat"]], "fx_hit", f, forte); k_val([alvo["mat"]], "fx_hit", f + 6, 0.0)
# ------------------------------------------------------------------ RASTRO novo: fita rente ao chao (projetada no terreno)
def mat_rastro():
    """sombra queimada com bordas irregulares que se desfazem por trecho; veios de fogo ondulados (referencia) e brasas que apagam.
    UV: u atravessa a fita (0..1); v = instante de NASCIMENTO (s) -> idade = tempo - v (o trecho nasce com a passagem real)"""
    m = bpy.data.materials.new("M_Rastro_r5"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = no(nt, "ShaderNodeOutputMaterial"); pr = no(nt, "ShaderNodeBsdfPrincipled"); tr = no(nt, "ShaderNodeBsdfTransparent"); mx = no(nt, "ShaderNodeMixShader")
    nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(pr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    pr.inputs["Base Color"].default_value = (0.012, 0.008, 0.009, 1); pr.inputs["Roughness"].default_value = 0.95
    sp = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(no(nt, "ShaderNodeTexCoord").outputs["UV"], sp.inputs[0])
    wpos = no(nt, "ShaderNodeTexCoord").outputs["Object"]
    idade = op(nt, "SUBTRACT", val(nt, "tempo", 0.0), sp.outputs["Y"])
    nasc = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", idade, 25.0), 0.0), 1.0)             # so aparece depois da passagem
    a_n = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "DIVIDE", idade, val(nt, "rastro_dur", 3.0)), 0.0), 1.0)   # idade normalizada
    borda = op(nt, "MULTIPLY", op(nt, "SUBTRACT", 0.5, op(nt, "ABSOLUTE", op(nt, "SUBTRACT", sp.outputs["X"], 0.5))), 2.0)   # 0 borda, 1 centro
    nz = no(nt, "ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 0.45; nz.inputs["Detail"].default_value = 6.0; nz.inputs["Roughness"].default_value = 0.6
    nt.links.new(wpos, nz.inputs["Vector"])
    # mascara: bordas irregulares; com a idade o limiar sobe e a fita se desfaz em manchas (dissipacao gradual por trecho)
    lim = op(nt, "ADD", 0.18, op(nt, "MULTIPLY", a_n, 1.05))
    mascara = op(nt, "MINIMUM", op(nt, "MAXIMUM", op(nt, "MULTIPLY", op(nt, "SUBTRACT", op(nt, "ADD", op(nt, "MULTIPLY", borda, 0.85), op(nt, "MULTIPLY", nz.outputs["Fac"], 0.75)), lim), 4.0), 0.0), 1.0)
    alfa = op(nt, "MULTIPLY", op(nt, "MULTIPLY", mascara, nasc), 0.92)
    # veios de fogo ondulados (alongados no sentido da passagem) + brasas finas; esfriam com a idade
    sx = no(nt, "ShaderNodeSeparateXYZ"); nt.links.new(wpos, sx.inputs[0])
    vv = no(nt, "ShaderNodeCombineXYZ"); nt.links.new(op(nt, "MULTIPLY", sx.outputs["X"], 1.2), vv.inputs["X"]); nt.links.new(op(nt, "MULTIPLY", sx.outputs["Y"], 0.16), vv.inputs["Y"])
    nt.links.new(op(nt, "MULTIPLY", val(nt, "tempo", 0.0), 0.8), vv.inputs["Z"])
    nzv = no(nt, "ShaderNodeTexNoise"); nzv.inputs["Scale"].default_value = 1.4; nzv.inputs["Detail"].default_value = 4.0; nzv.inputs["Distortion"].default_value = 2.2
    nt.links.new(vv.outputs[0], nzv.inputs["Vector"])
    veio = op(nt, "POWER", op(nt, "MAXIMUM", op(nt, "SUBTRACT", 1.0, op(nt, "MULTIPLY", op(nt, "ABSOLUTE", op(nt, "SUBTRACT", nzv.outputs["Fac"], 0.5)), 14.0)), 0.0), 4.0)
    nzb = no(nt, "ShaderNodeTexNoise"); nzb.inputs["Scale"].default_value = 6.0; nzb.inputs["Detail"].default_value = 2.0
    nt.links.new(wpos, nzb.inputs["Vector"])
    brasa = op(nt, "MULTIPLY", op(nt, "MAXIMUM", op(nt, "SUBTRACT", nzb.outputs["Fac"], 0.66), 0.0), 9.0)
    calor = op(nt, "POWER", op(nt, "SUBTRACT", 1.0, a_n), 2.2)
    fogo = op(nt, "MULTIPLY", op(nt, "MULTIPLY", op(nt, "ADD", op(nt, "MULTIPLY", veio, op(nt, "MULTIPLY", op(nt, "SUBTRACT", 1.0, borda), 1.1)), op(nt, "MULTIPLY", brasa, 0.6)), calor), nasc)
    nt.links.new(rampa(nt, op(nt, "MINIMUM", op(nt, "ADD", 0.45, op(nt, "MULTIPLY", fogo, 0.35)), 0.95)), pr.inputs["Emission Color"])
    nt.links.new(op(nt, "MULTIPLY", fogo, 3.2), pr.inputs["Emission Strength"])
    nt.links.new(op(nt, "MINIMUM", op(nt, "ADD", alfa, op(nt, "MULTIPLY", op(nt, "MINIMUM", fogo, 1.0), mascara)), 1.0), mx.inputs[0])
    try: m.surface_render_method = "BLENDED"
    except Exception: pass
    return m
M_RASTRO = mat_rastro()
def chao_z(x, y, alvos_chao):
    """projeta no terreno: raio para baixo so nos objetos de chao; devolve (ponto, normal)"""
    melhor = None
    for g in alvos_chao:
        Mi = g.matrix_world.inverted(); o_ = Mi @ V((x, y, 200.0)); d_ = (Mi.to_3x3() @ V((0, 0, -1))).normalized()
        ok, loc, nrm, idx = g.ray_cast(o_, d_)
        if ok:
            p = g.matrix_world @ loc; n_ = (g.matrix_world.to_3x3().inverted().transposed() @ nrm).normalized()
            if melhor is None or p.z > melhor[0].z: melhor = (p, n_)
    return melhor or (V((x, y, 0.0)), V((0, 0, 1)))
def fita(nome, amostras, larg, alvos_chao, sem=1.0):
    """amostras = [(t_nasc, centro_xy, direcao_xy)]; vertices projetados no chao (+0,04 na normal) -> contato continuo, sem faixa rigida"""
    me = bpy.data.meshes.new(nome); bm = bmesh.new(); uvl = bm.loops.layers.uv.new(); rnd = random.Random(int(sem * 1000))
    linhas = []
    for i, (tn, c, d) in enumerate(amostras):
        lat = V((-d.y, d.x, 0)).normalized(); fila = []
        for j in range(5):
            u = j / 4.0; w = (u - 0.5) * larg * (1 + 0.18 * math.sin(i * 0.9 + sem) + 0.12 * (rnd.random() - 0.5))
            p, n_ = chao_z(c.x + lat.x * w, c.y + lat.y * w, alvos_chao); fila.append((bm.verts.new(p + n_ * 0.04), u, tn))
        linhas.append(fila)
    for a, b in zip(linhas, linhas[1:]):
        for j in range(4):
            f_ = bm.faces.new((a[j][0], a[j + 1][0], b[j + 1][0], b[j][0]))
            for lp, (vv, u, tn) in zip(f_.loops, (a[j], a[j + 1], b[j + 1], b[j])): lp[uvl].uv = (u, tn)
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(nome, me); sc.collection.objects.link(o); o.data.materials.append(M_RASTRO); return o
# linguas de fogo baixas nos apoios das patas (pool)
N_LB = 28
LINGUAS_PE = []
for i in range(N_LB):
    o = lingua_mesh("Rastro_Lingua%d" % i, 2.2, 1.3, eixo="Z"); o["idade"] = 0.0; o["semente"] = 300 + i * 1.37
    c = o.constraints.new("LOCKED_TRACK"); c.target = ALVO; c.track_axis = "TRACK_NEGATIVE_Y"; c.lock_axis = "LOCK_Z"; o.scale = (0, 0, 0); LINGUAS_PE.append(o)
TODOS_MATS[:] = [m for m in bpy.data.materials if m.use_nodes and m.node_tree and "tempo" in m.node_tree.nodes]
CHAO_OBJ = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Plane")]
def apoios_patas(f0, f1):
    """toques reais das patas na previa (fim do osso Mao/Pe abaixo de 0,85: em repouso fica a 0,57) -> [(quadro, ponto)]"""
    toques = []; antes = {}
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for k in ("MaoE", "MaoD", "PeE", "PeD"):
            p = rig.matrix_world @ PB[k].tail; baixo = p.z < 0.85
            if baixo and not antes.get(k, False): toques.append((f, p.copy()))
            antes[k] = baixo
    return toques
def rastro_completo(nome, f_i, f_f, desloc, dur=3.0):
    """fita nascendo com o deslocamento REAL (raiz da previa) + linguas baixas nos apoios; dissipacao por trecho em 'dur' s"""
    am = []
    for f in range(f_i, f_f + 1, 2):
        t = (f - 1) / FPS; y = -desloc(t) + 4.0                    # nasce sob a garupa (por onde o corpo ja passou)
        am.append((t, V((0, y, 0)), V((0, -1, 0))))
    fo = fita(nome, am, 6.2, CHAO_OBJ); k_val([M_RASTRO], "rastro_dur", 1, dur)
    for o in LINGUAS_PE:
        if o.animation_data: o.animation_data_clear()
        k_obj(o, "scale", 1, (0, 0, 0))
    for i, (f, p) in enumerate(apoios_patas(f_i, f_f)):
        o = LINGUAS_PE[i % N_LB]; alt = 0.75 + 0.35 * ((i * 7) % 5) / 4
        k_obj(o, "scale", f - 1, (0, 0, 0)); k_obj(o, "location", f, (p.x, p.y + 0.4, 0.02)); k_prop(o, "idade", f, 0.0)
        k_obj(o, "scale", f, (0.5, 1, 0.3)); k_obj(o, "scale", f + 3, (0.9, 1, alt)); k_prop(o, "idade", f + 3, 0.25)
        k_obj(o, "location", f + 12, (p.x, p.y + 1.2, 0.02)); k_obj(o, "scale", f + 12, (0.6, 1, alt * 0.45)); k_prop(o, "idade", f + 12, 1.0)
        k_obj(o, "scale", f + 13, (0, 0, 0))
    return fo
# ------------------------------------------------------------------ deslocamento do jogo na previa
def desloc_inv(t):
    ti, tf = T0 + EVR3["impulso"], T0 + EVR3["fim_impulso"]
    if t <= ti: return 0.0
    if t <= tf: u = (t - ti) / (tf - ti); return 12.0 * (u * u * (3 - 2 * u))
    return 12.0 + V_C * (t - tf)
def preparar(sequencia, desloc_fn):
    limpar_chaves(); fim = nla(sequencia); tempo_linear(1, fim); repouso_base(fim)
    for o in CHAMAS: o.rotation_euler = o["rot_repouso"]
    rel = investida_fx(T0, fim)
    k_val([FAIXA.data.materials[0]], "fx_faixa", 1, 0.0); k_val([FAIXA.data.materials[0]], "fx_faixa", fim, 0.0)   # faixa antiga desligada
    for f in range(1, fim + 1): rig.location = (0, -desloc_fn((f - 1) / FPS), 0); rig.keyframe_insert("location", frame=f)
    return fim, rel
def folga_sobre(alvo, f0, f1):
    """menor folga vertical entre a malha do Cerbero e o topo do alvo, dentro da area do alvo (quadro a quadro, a cada 2)"""
    px, py = alvo["pai"].location.x, alvo["pai"].location.y; hx, hy = alvo["comp"] / 2, alvo["larg"] / 2 + 0.3
    pior = (99.0, None)
    for f in range(f0, f1 + 1, 2):
        sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
        for o in (CORPO, CAB):
            me = o.evaluated_get(dg).to_mesh(); M = o.matrix_world
            for v in me.vertices:
                p = M @ v.co
                if abs(p.x - px) < hx and abs(p.y - py) < hy:
                    fz = p.z - alvo["topo"]
                    if fz < pior[0]: pior = (fz, f, o.name, round(p.y - py, 2), round(p.z, 2))
            o.evaluated_get(dg).to_mesh_clear()
    return round(pior[0], 2), pior[1:]
VISTAS.update({})
def vistas_alvo(yc, zc=6.0):
    VISTAS.update({"perfil": ((-74, yc + 4, 13), (0, yc + 4, zc), 30), "frente": ((3, yc - 72, 9), (0, yc + 6, zc + 1), 42),
                   "34": ((-40, yc - 36, 17), (0, yc + 2, zc), 30), "34tras": ((-42, yc + 34, 19), (0, yc - 2, zc), 30)})
# ------------------------------------------------------------------ (a) alvo com METADE do porte: passa POR CIMA
if "sobre" in SO:
    seq = [("Repouso", 1, 15), ("InvestidaR3", 1), ("InvestidaSobre", 1), ("Corrida", 3)]
    fim, rel = preparar(seq, desloc_inv)
    t_s0 = T0 + DUR_R3_; t_ap = t_s0 + EVS["apice"]
    t_susp = t_s0 + EVS["suspensao"]; y_dec, y_pou = [], []
    for k in ("MaoE", "MaoD"):                                  # ultimo apoio das dianteiras antes de decolar
        fs = [f for f in range(F(t_s0), F(t_susp)) if (sc.frame_set(f) or True) and (rig.matrix_world @ PB[k].tail).z < 0.85]
        sc.frame_set(fs[-1]); y_dec.append((rig.matrix_world @ PB[k].tail).y)
    for k in ("PeE", "PeD"):                                    # primeiro apoio das traseiras DEPOIS de sair do chao no salto
        no_ar = False
        for f in range(F(t_susp), F(t_s0 + DUR_S)):
            sc.frame_set(f); z_ = (rig.matrix_world @ PB[k].tail).z
            if z_ > 3.0: no_ar = True
            elif no_ar and z_ < 0.85: y_pou.append((rig.matrix_world @ PB[k].tail).y); break
    larg_p = MED["comprimento_bbox"] * 0.5 * 0.30; MARG = float(next((a.split('=')[1] for a in ARGS if a.startswith('marg=')), 8.3))
    y_bar = max(y_pou) + MARG + larg_p / 2                      # r2: logo atras do pouso das traseiras (mais espaco para as dianteiras subirem)
    JANELA = {"decolagem_dianteiras_y": [round(v, 2) for v in y_dec], "pouso_traseiras_y": [round(v, 2) for v in y_pou], "janela_studs": round(min(y_dec) - max(y_pou), 2), "dianteiras_decolam_a_studs_do_alvo": round(min(y_dec) - (max(y_pou) + MARG + larg_p), 2), "traseiras_pousam_a_studs_do_alvo": MARG}
    pequeno = quadrupede("Alvo_Metade", MED["cernelha"] * 0.5, MED["comprimento_bbox"] * 0.5, (0.42, 0.38, 0.30, 1))
    pequeno["pai"].location = (0, y_bar, 0); LIXO.append(pequeno["pai"])
    fo = rastro_completo("Rastro_Sobre", F(T0 + EVR3["impulso"]), fim, desloc_inv); LIXO.append(fo)
    fz, fq = folga_sobre(pequeno, F(t_s0), F(t_s0 + DUR_S))
    # o alvo leva o golpe da passagem (1,0x da v6.2) quando o peito passa sobre ele
    f_hit = next((f for f in range(F(t_s0), fim) if -desloc_inv((f - 1) / FPS) - 8.7 <= y_bar + pequeno["larg"] / 2), F(t_ap))
    flash(pequeno, f_hit)
    RELATO["sobre"] = {**rel, "alvo": {"cernelha": round(pequeno["cern"], 2), "comprimento": round(pequeno["comp"], 2), "largura_no_caminho": round(pequeno["larg"], 2),
                                       "topo_real": round(pequeno["topo"], 2)},
                       "metrica": "cernelha e comprimento (bbox) do Cerbero x 0,5", "folga_min_corpo_sobre_alvo_studs": fz, "quadro_folga_min": fq,
                       "apice_s": round(t_ap, 2), "janela_apoios": JANELA, "golpe_passagem_s": round((f_hit - 1) / FPS, 2), "previa_s": round(fim / FPS, 2)}
    print("SOBRE", RELATO["sobre"], flush=True)
    vistas_alvo(y_bar, pequeno["cern"] * 0.8)
    fim = min(fim, F(t_s0 + DUR_S + 0.35)); sc.frame_end = fim
    render_leve("Investida_sobre", fim, ["perfil", "frente", "34"], [("aproxima", t_s0 - 0.3), ("decola", t_s0 + EVS["suspensao"]), ("apice", t_ap),
                                                                     ("pouso", t_s0 + EVS["pouso_dianteiras"]), ("rastro", (fim - 1) / FPS)])
# ------------------------------------------------------------------ (b) alvo MAIOR que o Cerbero: para no contato e as TRES mordem
if "impacto" in SO:
    limpar_secao()
    seq = [("Repouso", 1, 15), ("InvestidaR3", 1), ("Corrida", 1), ("InvestidaImpacto", 1), ("Repouso", 1, 30)]
    t_i0 = T0 + DUR_R3_ + T_GAL_
    imp_s = [0.0]
    for i in range(1, 400): t_ = i / 600; imp_s.append(imp_s[-1] + V_C * (1 - (lambda x: x * x * (3 - 2 * x))(min(1, t_ / 0.30))) / 600)
    def desloc_imp(t):
        if t <= t_i0: return desloc_inv(t)
        return desloc_inv(t_i0) + imp_s[min(len(imp_s) - 1, int((t - t_i0) * 600))]
    fim, rel = preparar(seq, desloc_imp)
    contatos = {k: t_i0 + EVI["mordida_" + k] for k in "CED"}
    bocas = {k: boca_mundo(k, F(contatos[k]))[0] for k in "CED"}
    y_sup = max(b.y for b in bocas.values())                    # superficie do flanco: a boca que menos avanca encosta; as outras medem a sobra
    grande = quadrupede("Alvo_Maior", MED["cernelha"] * 1.4, MED["comprimento_bbox"] * 1.4, (0.30, 0.33, 0.36, 1), 0.5)
    grande["pai"].location = (0, y_sup - grande["larg"] / 2, 0); LIXO.append(grande["pai"])
    alcance = {k: round(y_sup - b.y, 2) for k, b in bocas.items()}       # >0 = a boca passaria da superficie (atravessa)
    altura_bocas = {k: round(b.z, 2) for k, b in bocas.items()}
    flash(grande, F(t_i0), 0.35)                                 # contato do corpo
    for k in "CED": flash(grande, F(contatos[k]))
    # o alvo grande balanca de leve com o impacto (peso), sem ser empurrado
    pai = grande["pai"]; y0 = pai.location.y
    for f, dy in ((F(t_i0) - 1, 0.0), (F(t_i0) + 3, -0.25), (F(t_i0) + 10, 0.0), (F(contatos["C"]) + 2, -0.15), (F(contatos["D"]) + 8, 0.0)):
        pai.location.y = y0 + dy; pai.keyframe_insert("location", frame=f)
    fo = rastro_completo("Rastro_Impacto", F(T0 + EVR3["impulso"]), fim, desloc_imp); LIXO.append(fo)
    RELATO["impacto"] = {**rel, "alvo": {"cernelha": round(grande["cern"], 2), "comprimento": round(grande["comp"], 2), "largura": round(grande["larg"], 2)},
                         "metrica": "cernelha e comprimento (bbox) do Cerbero x 1,4", "contato_corpo_s": round(t_i0, 2),
                         "mordidas_s": {k: round(v, 2) for k, v in contatos.items()}, "boca_alem_da_superficie_studs": alcance, "altura_das_bocas": altura_bocas,
                         "previa_s": round(fim / FPS, 2)}
    print("IMPACTO", RELATO["impacto"], flush=True)
    vistas_alvo(y_sup + 6, 7.5)
    render_leve("Investida_impacto", fim, ["perfil", "34tras"], [("aproxima", t_i0 - 0.35), ("contato", t_i0 + 0.05), ("absorve", t_i0 + EVI["absorve"]),
                                                             ("mordida_C", contatos["C"]), ("mordida_D", contatos["D"]), ("recupera", t_i0 + EVI["recuperacao"] + 0.3)])
# ------------------------------------------------------------------ rastro em terreno inclinado (demonstracao de projecao, sem o Cerbero)
if "terreno" in SO:
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=60, size=80, location=(300, 0, 0)); tg = bpy.context.object; tg.name = "Terreno_Teste"
    for v in tg.data.vertices:
        x, y = v.co.x, v.co.y; v.co.z = 0.16 * y + 2.2 * math.sin(x * 0.11) * math.cos(y * 0.09) + 1.2 * math.sin(y * 0.23 + 1.0)
    tg.data.materials.append(bpy.data.materials["Chao"])
    am = [((i * 2 / 30.0), V((300 + 3 * math.sin(i * 0.06), 30 - i * 1.48, 0)), V((0.0, -1, 0))) for i in range(41)]
    fo = fita("Rastro_Terreno", am, 6.2, [tg]); k_val([M_RASTRO], "rastro_dur", 1, 3.0)
    for t_ in (1.0, 2.6):
        k_val([M_RASTRO], "tempo", 1, t_); sc.frame_set(1)
        for nm, (pos, alv, le) in (("terreno_34", ((262, 44, 22), (300, 4, 2), 30)), ("terreno_baixo", ((276, -26, 6), (300, 8, 3), 30))):
            cam.location = pos; cam.rotation_euler = (V(alv) - V(pos)).to_track_quat("-Z", "Y").to_euler(); cd.lens = le; ALVO.location = pos
            sc.render.image_settings.media_type = "IMAGE"; sc.render.image_settings.file_format = "PNG"; sc.render.resolution_x, sc.render.resolution_y = 640, 450
            sc.render.filepath = os.path.join(OUT, "Rastro_%s_t%.1f.png" % (nm, t_)); bpy.ops.render.render(write_still=True)
    RELATO["terreno"] = "fita projetada por raio no terreno ondulado (+0,04 na normal); inclinacao media 9 graus"
CUSTO_RASTRO = {"PC": "segmentos de 2,2 studs com Decal/Texture que some por trecho (~30 vivos em 3 s a 22 studs/s) OU Beams com Attachments a cada 2 studs; "
                      "brasas: 1 ParticleEmitter 20/s rente ao chao; linguas nos apoios: ~4 vivas (1 por apoio, 0,4 s)",
                "celular": "segmentos de 4 studs (~17 vivos), brasas 8/s, linguas so nas dianteiras (~2 vivas)",
                "terreno": "raycast para baixo por segmento (1 por 2,2 studs) no servidor ou cliente; Decal alinhado a normal",
                "nota": "ESTIMATIVA da previa; medir no Roblox"}
RELATO["custo_rastro"] = CUSTO_RASTRO
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_Cerbero_FX_Investida_r5.blend"))
json.dump(RELATO, open(os.path.join(OUT, "fx_investida_r5.json"), "w"), indent=1, ensure_ascii=False, default=str)
print("FX_OK", json.dumps(RELATO, ensure_ascii=False, default=str), flush=True)
