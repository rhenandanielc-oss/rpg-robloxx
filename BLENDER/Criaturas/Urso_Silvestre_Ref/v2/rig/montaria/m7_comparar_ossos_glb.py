"""Montaria M7 (10/11/2026): compara o esqueleto de dois GLB (reimportados numa cena vazia): ossos, pais, pesos e a
matriz de repouso de cada osso (matrix_local), para garantir que a sela usa o MESMO esqueleto do urso no Roblox.
So leitura. Uso: blender -b --factory-startup -P m7_comparar_ossos_glb.py -- <urso.glb> <sela.glb>"""
import bpy, sys
A = sys.argv[sys.argv.index("--") + 1:]
def ler(caminho):
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    bpy.ops.import_scene.gltf(filepath=caminho)
    arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
    pesos = set()
    for m in [o for o in bpy.data.objects if o.type == "MESH" and o.vertex_groups]:
        nomes = {g.index: g.name for g in m.vertex_groups}
        for v in m.data.vertices:
            for g in v.groups:
                if g.weight > 1e-4: pesos.add(nomes[g.group])
    return {b.name: (b.parent.name if b.parent else None, (arm.matrix_world @ b.matrix_local).copy()) for b in arm.data.bones}, pesos
U, pu = ler(A[0]); S, ps = ler(A[1])
print("OSSOS urso", len(U), "sela", len(S), "| com peso: urso", len(pu), "sela", len(ps))
print("SEM_PESO_NA_SELA (o Roblox descarta):", sorted(set(S) - ps))
pior = 0.0
for n, (pai, m) in U.items():
    if n not in S: print("FALTA_NA_SELA", n); continue
    pai2, m2 = S[n]
    d = max(abs(m[i][j] - m2[i][j]) for i in range(4) for j in range(4)); pior = max(pior, d)
    if pai != pai2 or d > 1e-4: print("DIFERENTE", n, "pai", pai, pai2, "dif_matriz", round(d, 5))
print("PIOR_DIF_MATRIZ", round(pior, 6))
