"""Regressao: compara as chaves das acoes do .blend aberto com as de mesmo nome em outro .blend (maior diferenca por canal). So leitura.
Uso: blender -b <referencia.blend> -P e5_42_comparar_acoes.py -- <outro.blend> <Acao1,Acao2,...>"""
import bpy, sys
A = sys.argv[sys.argv.index("--") + 1:]; OUTRO = A[0]; NOMES = A[1].split(",")
REFS = {n: bpy.data.actions[n] for n in NOMES if n in bpy.data.actions}
with bpy.data.libraries.load(OUTRO) as (src, dst): ped = [n for n in src.actions if n in NOMES]; dst.actions = list(ped)
novas = dict(zip(ped, dst.actions))                                          # copias anexadas (o Blender renomeia para .001)
def curvas(act):
    out = {}
    for cb in [c for l in act.layers for s in l.strips for c in s.channelbags] if hasattr(act, "layers") and act.layers else []:
        for fc in cb.fcurves: out[(fc.data_path, fc.array_index)] = [k.co[1] for k in fc.keyframe_points]
    if not out:
        for fc in act.fcurves: out[(fc.data_path, fc.array_index)] = [k.co[1] for k in fc.keyframe_points]
    return out
for n in NOMES:
    ref = REFS[n]; nv = novas.get(n)
    if nv is None: print("REGRESSAO", n, "ausente"); continue
    c0, c1 = curvas(ref), curvas(nv); pior = (0.0, None)
    for k in c0:
        if k not in c1 or len(c0[k]) != len(c1[k]): pior = (9e9, k); break
        d = max(abs(a - b) for a, b in zip(c0[k], c1[k])); pior = max(pior, (d, k), key=lambda x: x[0])
    print("REGRESSAO", n, "canais", len(c0), "/", len(c1), "maior_diferenca %.6f" % pior[0], pior[1])
