"""Furia roxa (20/11) - pedido do usuario: "a Furia muda a cor dos poderes para roxo, tanto do Sol Infernal quanto da Investida".
Decisoes do usuario (20/11): SO durante a Furia (8 s); fogo ROXO com nucleo branco-lilas e bordas roxo-escuro; SO a cor (numeros
aprovados iguais); rastro da Investida roxo; aura do corpo = estado sustentado da Furia r4 (violeta). [PROPOSTA] a cor e decidida
no lancamento (um Sol lancado aos 7,9 s de Furia voa roxo ate o fim).
NAO altera os aprovados: le o fonte de fx_bola_infernal_r3b.py (Sol Infernal) ou fx_investida_r5.py (Investida) e executa uma
COPIA com um gancho antes de cada render que:
  * troca a cor de EMISSAO dos materiais do poder (criados pelo script) por uma rampa violeta guiada pela luminancia da cor de fogo
    original (brasa -> roxo escuro, vermelho -> violeta, laranja -> violeta claro, amarelo -> branco-lilas): mesma forma e brilho;
  * luzes pontuais do poder ficam violeta;
  * pele, chamas da aura e bocas ficam no estado sustentado da Furia r4 (fx_vio_* = 1, chamas violeta = 1).
SIMULACAO DE BLENDER; no Roblox seria uma variante de cor dos efeitos escolhida pelo servidor no lancamento (nao testado).
Uso: blender -b -t 2 CR_Cerbero_Fogo_A3.blend -P fx_furia_roxo.py -- <saida> poder=sol|investida [args do script base] [vistas=a,b]
"""
import bpy, sys, os, re
ARGS = sys.argv[sys.argv.index("--") + 1:]
PODER = next((a.split("=")[1] for a in ARGS if a.startswith("poder=")), "sol")
_VSO = next((a.split("=")[1].split(",") for a in ARGS if a.startswith("vistas=")), None)
AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = {"sol": "fx_bola_infernal_r3b.py", "investida": "fx_investida_r5.py"}[PODER]
_MATS_ANTES = set(m.name for m in bpy.data.materials)
_LUZES_ANTES = set(l.name for l in bpy.data.lights)

def _lin(hx):
    c = [int(hx[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c) + (1.0,)
R_ESC, R_MED, R_CLA, R_NUC = _lin("1e0033"), _lin("6a1bd6"), _lin("a65cff"), _lin("efe2ff")
# posicoes = luminancia das cores da rampa de fogo (brasa 5a0a00, vermelho c42200, laranja ff6a00, amarelo ffe07a)
RAMPA_ROXA = ((0.0, (0, 0, 0, 1)), (0.02, R_ESC), (0.12, R_MED), (0.36, R_CLA), (0.70, R_NUC))
EXCLUI = re.compile(r"(?i)alvo|chao|jog|vida|barra|fundo|criat|simples|fumaca|contorno|linha|faixa_sombra|vento")

def _lum(c): return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def _cor_roxa(l):
    for (p0, c0), (p1, c1) in zip(RAMPA_ROXA, RAMPA_ROXA[1:]):
        if l <= p1:
            k = (l - p0) / (p1 - p0); return tuple(c0[i] + (c1[i] - c0[i]) * k for i in range(3)) + (1.0,)
    return R_NUC
def _troca(nt, entrada):
    """liga a entrada de cor (Emission Color) a uma rampa roxa guiada pela luminancia da cor original"""
    if entrada.is_linked:
        src = entrada.links[0].from_socket
        bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(src, bw.inputs[0])
        cr = nt.nodes.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
        el[0].position, el[0].color = RAMPA_ROXA[0]; el[1].position, el[1].color = RAMPA_ROXA[-1]
        for p, c in RAMPA_ROXA[1:-1]:
            e = el.new(p); e.color = c
        nt.links.new(bw.outputs[0], cr.inputs[0]); nt.links.new(cr.outputs[0], entrada); return 1
    c = entrada.default_value
    if max(c[0], c[1], c[2]) > 0.0 and c[0] > c[2]:            # so cores quentes (fogo); branco/cinza ficam
        entrada.default_value = _cor_roxa(_lum(c)); return 1
    return 0
RELATO_ROXO = {"materiais": [], "luzes": []}
_FEITOS = set()
def _ROXO_PRE():
    # roda antes de CADA render: secoes posteriores criam materiais novos e refazem as chaves da aura (impacto voltava ao laranja)
    g = globals()
    for m in bpy.data.materials:
        if m.name in _FEITOS or m.name in _MATS_ANTES or EXCLUI.search(m.name) or not m.use_nodes or not m.node_tree: continue
        _FEITOS.add(m.name)
        nt = m.node_tree; n_ = 0
        for nd in list(nt.nodes):
            if nd.type == "EMISSION": n_ += _troca(nt, nd.inputs["Color"])
            elif nd.type == "BSDF_PRINCIPLED": n_ += _troca(nt, nd.inputs["Emission Color"])
        if n_: RELATO_ROXO["materiais"].append(m.name)
    for l in bpy.data.lights:
        if l.name in _LUZES_ANTES or l.name in _FEITOS or l.type != "POINT": continue
        _FEITOS.add(l.name)
        l.color = (0.62, 0.36, 1.0); RELATO_ROXO["luzes"].append(l.name)
    # aura no estado sustentado da Furia r4 (violeta em tudo); tira as chaves que voltariam ao laranja
    mats = list(g.get("MATS_PELE", [])) + ([g["MAT_BOCA"]] if "MAT_BOCA" in g else [])
    for m in mats:
        nt = m.node_tree
        for nome, v in (("fx_vio_C", 1.0), ("fx_vio_E", 1.0), ("fx_vio_D", 1.0), ("fx_vio_frente", 1.5), ("fx_vio_global", 1.0)):
            if nome not in nt.nodes: continue
            ad = nt.animation_data
            if ad and ad.action:
                for fc in [fc for fc in _fcurves(ad.action) if fc.data_path == 'nodes["%s"].outputs[0].default_value' % nome]:
                    _remove_fc(ad.action, fc)
            nt.nodes[nome].outputs[0].default_value = v
    for o in g.get("CHAMAS", []):
        if o.animation_data and o.animation_data.action:
            for fc in [fc for fc in _fcurves(o.animation_data.action) if fc.data_path == '["violeta"]']: _remove_fc(o.animation_data.action, fc)
        o["violeta"] = 1.0
    RELATO_ROXO["aura"] = "estado sustentado da Furia r4 (fx_vio_* = 1; chamas violeta = 1)"
def _fcurves(act):
    try: return list(act.fcurves)
    except AttributeError:                                     # acoes em camadas (Blender 5.x)
        out = []
        for ly in act.layers:
            for st in ly.strips:
                for cb in st.channelbags: out += list(cb.fcurves)
        return out
def _remove_fc(act, fc):
    try: act.fcurves.remove(fc); return
    except Exception: pass
    for ly in act.layers:
        for st in ly.strips:
            for cb in st.channelbags:
                if fc in list(cb.fcurves): cb.fcurves.remove(fc); return

src = open(os.path.join(AQUI, BASE), encoding="utf-8").read()
n_r = src.count("bpy.ops.render.render(")
src = src.replace("bpy.ops.render.render(", "_ROXO_PRE(); bpy.ops.render.render(")
src = src.replace("    for v in vistas:\n        vista(v)", "    for v in [x for x in vistas if _VSO is None or x in _VSO]:\n        vista(v)")
src = src.replace("        for v in vistas:\n            vista(v); sc.render.filepath",
                  "        for v in [x for x in vistas if _VSO is None or x in _VSO]:\n            vista(v); sc.render.filepath")
src = re.sub(r'"CR_Cerbero_FX_([A-Za-z]+)', r'"CR_Cerbero_FX_Roxo_\1', src)
print("ROXO_BASE", BASE, "renders ganchados:", n_r, flush=True)
g = dict(globals()); g["__file__"] = os.path.join(AQUI, BASE); g["__name__"] = "__main__"
g.update(_ROXO_PRE=_ROXO_PRE, _VSO=_VSO, _fcurves=_fcurves, _remove_fc=_remove_fc)
_ROXO_G = g
_orig = _ROXO_PRE
def _ROXO_PRE_WRAP():
    # o gancho precisa ver os globais do script base (MATS_PELE, MAT_BOCA, CHAMAS)
    globals().update({k: v for k, v in _ROXO_G.items() if k in ("MATS_PELE", "MAT_BOCA", "CHAMAS")})
    _orig()
g["_ROXO_PRE"] = _ROXO_PRE_WRAP
exec(compile(src, os.path.join(AQUI, BASE), "exec"), g)
print("ROXO_FIM", RELATO_ROXO, flush=True)
