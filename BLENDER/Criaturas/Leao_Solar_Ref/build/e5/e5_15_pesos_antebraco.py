"""E5 r3: limpa pesos indevidos no antebraco/punho das dianteiras. A juba do peito, que cai sobre o antebraco, deixou peso do Peito
(ate 0,6) e de ossos Juba_* em vertices abaixo do cotovelo; com a pata erguida (Patada) essa pele ficava presa ao peito e vincava
na parte de tras do punho. Regra: vertice com >= 0,3 de peso na parte baixa da perna (Antebraco, Mao, Punho_Aux, Dedos, Cotovelo_Aux)
perde o peso dos outros ossos abaixo de z 4,4 (repouso), com transicao ate z 5,4 (cotovelo em z 5,2); o peso tirado vai para os
ossos da perna na mesma proporcao. Nao cria influencias (continua <= 4) e nao deixa vertice sem peso.
Uso: blender -b <arquivo.blend> -P e5_15_pesos_antebraco.py -- <saida.blend>"""
import bpy, sys
A = sys.argv[sys.argv.index("--") + 1:]
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]; VG = ob.vertex_groups; GI = {g.index: g.name for g in VG}
Z0, Z1 = 4.4, 5.4; mudados = {"DD": 0, "DE": 0}; tirado = {"DD": 0.0, "DE": 0.0}
JA = bool(ob.data.get("pesos_punho_r3"))                                     # nao e idempotente (a transicao reduziria de novo)
if JA: print("PESOS_PUNHO ja aplicado neste arquivo: nada feito")
for v in ([] if JA else ob.data.vertices):
    for p_ in ("DD", "DE"):
        baixo = {x + "_" + p_ for x in ("Antebraco", "Mao", "Punho_Aux", "Dedos", "Cotovelo_Aux")}
        w = {GI[g.group]: g.weight for g in v.groups}; lb = sum(x for k, x in w.items() if k in baixo)
        fora = {k: x for k, x in w.items() if k not in baixo and x > 0}
        if lb < 0.3 or not fora or v.co.z >= Z1: continue
        f = 1.0 if v.co.z <= Z0 else (Z1 - v.co.z) / (Z1 - Z0)                 # fracao do peso estranho retirada
        tot = sum(w.values()); sai = sum(fora.values()) * f
        for k, x in fora.items():
            nx = x * (1 - f)
            if nx < 1e-4: VG[k].remove([v.index])
            else: VG[k].add([v.index], nx, "REPLACE")
        for k in baixo:
            if k in w: VG[k].add([v.index], w[k] + sai * w[k] / lb, "REPLACE")
        mudados[p_] += 1; tirado[p_] += sai
# verificacao: influencias por vertice e vertices sem peso
mx = max(len([g for g in v.groups if g.weight > 0]) for v in ob.data.vertices); sem = sum(1 for v in ob.data.vertices if not any(g.weight > 0 for g in v.groups))
print("PESOS_PUNHO vertices", mudados, "peso_movido", {k: round(x, 2) for k, x in tirado.items()}, "max_influencias", mx, "sem_peso", sem)
ob.data["pesos_punho_r3"] = 1
bpy.ops.wm.save_as_mainfile(filepath=A[0])
