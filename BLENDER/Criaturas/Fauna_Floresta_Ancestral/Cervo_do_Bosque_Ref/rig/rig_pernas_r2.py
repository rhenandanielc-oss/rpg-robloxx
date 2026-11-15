"""Rig r2 do Cervo-do-Bosque (12/11/2026, pedido do usuario: "as pernas fazem curva pra tras e pra frente").
Causa medida: o heat espalhou os pesos ao longo dos ossos finos da perna (canela dianteira com 30-40% de Antebraco/Quartela
em todo o comprimento; canela traseira com ~20% de Perna) -> ao dobrar, o osso inteiro entorta em arco (banana).
Correcao: abaixo do cotovelo / da soldra, cada vertice da perna pertence ao SEGMENTO onde se projeta (antebraco, canela,
quartela; perna/gamba, canela, quartela) e so mistura numa faixa estreita (+-BANDA) em volta de cada articulacao.
Perto do topo da regiao mistura com os pesos antigos (sem degrau com o corpo). Ossos, nomes e acoes NAO mudam.
Uso: blender -b rig/CR_Cervo_Rig.blend -P rig/rig_pernas_r2.py -- <saida.blend>"""
import bpy, sys, os, math
from mathutils import Vector as V
SAIDA = os.path.abspath(sys.argv[sys.argv.index("--") + 1])
BANDA = 0.022                                         # meia-largura da dobra na articulacao (u)
RAIO = 0.075                                          # distancia maxima do vertice ao eixo da perna
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
arm = bpy.data.objects["Cervo_Rig"]; B = arm.data.bones; O = bpy.data.objects["Cervo_Corpo"]; me = O.data
CADEIAS = {"E_d": ("AntebracoE", "CanelaE", "QuartelaE"), "D_d": ("AntebracoD", "CanelaD", "QuartelaD"),
           "E_t": ("PernaE", "CanelaTrasE", "QuartelaTrasE"), "D_t": ("PernaD", "CanelaTrasD", "QuartelaTrasD")}
def grupo(nm): return O.vertex_groups.get(nm) or O.vertex_groups.new(name=nm)
GN = {g.index: g.name for g in O.vertex_groups}
mudados = {}
for nome, ossos in CADEIAS.items():
    pts = [B[ossos[0]].head_local.copy()] + [B[o].tail_local.copy() for o in ossos]      # topo, j1, j2, ponta
    seg_L = [(pts[i + 1] - pts[i]).length for i in range(3)]; S = [0, seg_L[0], seg_L[0] + seg_L[1], sum(seg_L)]
    sx = 1 if pts[0].x > 0 else -1
    z_topo = pts[0].z - (0.03 if nome.endswith("_d") else 0.08)      # abaixo do cotovelo / da soldra (gamba perto do flanco)
    n = 0
    for v in me.vertices:
        p = v.co
        if p.z > z_topo or (p.x * sx) < 0.02: continue
        best = None
        for i in range(3):                                            # projecao no segmento mais proximo
            a, b = pts[i], pts[i + 1]; ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            d = (p - (a + ab * t)).length
            if best is None or d < best[0]: best = (d, i, t)
        d, i, t = best
        if d > RAIO: continue
        s = S[i] + t * seg_L[i]
        w = [0.0, 0.0, 0.0]                                           # pesos por segmento com dobra so perto das juntas
        for k in range(3):
            ini = 1.0 if k == 0 else suave((s - (S[k] - BANDA)) / (2 * BANDA))
            fim = 1.0 if k == 2 else 1 - suave((s - (S[k + 1] - BANDA)) / (2 * BANDA))
            w[k] = ini * fim
        tot = sum(w) or 1.0; w = [x / tot for x in w]
        mix = suave((z_topo - p.z) / 0.06)                            # perto do topo: mistura com os pesos antigos
        antigos = {GN[g.group]: g.weight for g in v.groups}
        for g in list(v.groups): O.vertex_groups[g.group].remove([v.index])
        novos = {nm: (1 - mix) * antigos.get(nm, 0.0) for nm in antigos}
        for k, nm in enumerate(ossos): novos[nm] = novos.get(nm, 0.0) + mix * w[k]
        tot = sum(novos.values()) or 1.0
        for nm, x in sorted(novos.items(), key=lambda q: -q[1])[:4]:
            if x / tot > 1e-4: grupo(nm).add([v.index], x / tot, "REPLACE")
        n += 1
    mudados[nome] = n
print("PERNAS_R2 vertices refeitos", mudados)
# GARGANTA (13/11): a cabeca rigida terminava numa linha fixa (y = nariz + 0,24) e a garganta logo atras era 100% Pescoco;
# com a cabeca muito dobrada (coçar, sacudir, beber) essa aresta esticava ate 20x. Transicao gradual Cabeca -> Pescoco2 ->
# Pescoco na garganta (abaixo da linha da nuca), igual nas duas malhas (costura continua igual).
import numpy as _np
NY = min(min(v.co.y for v in o_.data.vertices) for o_ in (bpy.data.objects["Cervo_Cabeca"], O))
Y0, Y1 = NY + 0.17, NY + 0.36
gar = {}
for o_ in (bpy.data.objects["Cervo_Cabeca"], O):
    GN_ = {g.index: g.name for g in o_.vertex_groups}; n_ = 0
    def gp(nm): return o_.vertex_groups.get(nm) or o_.vertex_groups.new(name=nm)
    for v in o_.data.vertices:
        p = v.co
        if not (Y0 < p.y < Y1 and p.z < 1.34 and abs(p.x) < 0.13): continue
        gz = suave((1.34 - p.z) / 0.22)                                # acima: volta aos pesos antigos aos poucos (sem borda)
        dom = {GN_[g.group]: g.weight for g in v.groups}
        if sum(w for nm, w in dom.items() if nm in ("Cabeca", "Pescoco", "Pescoco2")) < 0.6: continue
        f = suave((p.y - Y0) / (Y1 - Y0))
        alvo_ = {"Cabeca": (1 - f) ** 2, "Pescoco2": 2 * f * (1 - f), "Pescoco": f * f}
        novos = {nm: (1 - gz) * w for nm, w in dom.items()}
        for nm, w in alvo_.items(): novos[nm] = novos.get(nm, 0.0) + gz * w
        tot = sum(novos.values()) or 1.0
        for g in list(v.groups): o_.vertex_groups[g.group].remove([v.index])
        for nm, w in sorted(novos.items(), key=lambda q: -q[1])[:4]:
            if w / tot > 1e-4: gp(nm).add([v.index], w / tot, "REPLACE")
        n_ += 1
    gar[o_.name] = n_
print("GARGANTA vertices refeitos", gar)
bpy.ops.wm.save_as_mainfile(filepath=SAIDA); print("RIG_R2_OK", SAIDA)
