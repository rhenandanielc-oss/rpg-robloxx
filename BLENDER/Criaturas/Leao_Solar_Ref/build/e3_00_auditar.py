"""E3 - auditoria de topologia da malha (le, nao salva): solda as costuras de UV em copia e lista os lacos de bordas
abertas com tamanho, perimetro, centro e regiao; arestas nao-manifold (>2 faces) e vertices nao-manifold.
Uso: blender -b <arquivo.blend> -P e3_00_auditar.py -- <objeto> <saida.json> [sem_solda]"""
import bpy, bmesh, sys, os, json
import numpy as np
from mathutils import Vector
A = sys.argv[sys.argv.index("--") + 1:]; NOME, OUT = A[0], A[1]
REF = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ref")
ms = {n: np.load(os.path.join(REF, n + ".npy")) for n in ("juba_lado", "tufo_lado")}
K = 11.5 / 360
def regiao(c):
    xs = int(np.clip(round(620 - c.y / K), 0, 1216)); ys = int(np.clip(round(592 - c.z / K), 0, 1292))
    if c.y < -12.6 and 10.8 < c.z < 16.8 and abs(c.x) < 2.2: return "rosto/boca"
    if ms["tufo_lado"][ys, xs]: return "tufo"
    if ms["juba_lado"][ys, xs]: return "juba"
    if c.z < 1.4: return "patas"
    if c.z < 7.0 and abs(c.x) > 0.8: return "pernas"
    return "corpo/cauda"
def auditar(me, soldar=True):
    bm = bmesh.new(); bm.from_mesh(me)
    if soldar: bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.edges.ensure_lookup_table()
    abertas = [e for e in bm.edges if e.is_boundary]
    nm_arestas = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    nm_verts = sum(1 for v in bm.verts if not v.is_manifold and not v.is_boundary)
    vistos = set(); lacos = []
    for e in abertas:
        if e.index in vistos: continue
        pilha = [e]; vistos.add(e.index); laco = []
        while pilha:
            a = pilha.pop(); laco.append(a)
            for v in a.verts:
                for b in v.link_edges:
                    if b.is_boundary and b.index not in vistos: vistos.add(b.index); pilha.append(b)
        vs = {v for x in laco for v in x.verts}
        c = sum((v.co for v in vs), Vector()) / len(vs)
        lacos.append({"arestas": len(laco), "perimetro": round(sum(x.calc_length() for x in laco), 3),
                      "centro": [round(t, 2) for t in c], "regiao": regiao(c)})
    res = {"verts": len(bm.verts), "faces": len(bm.faces), "bordas_abertas": len(abertas), "lacos": len(lacos),
           "arestas_nao_manifold": nm_arestas, "verts_nao_manifold": nm_verts,
           "por_regiao": {}, "maiores": sorted(lacos, key=lambda l: -l["perimetro"])[:12]}
    for l in lacos:
        r = res["por_regiao"].setdefault(l["regiao"], {"lacos": 0, "arestas": 0}); r["lacos"] += 1; r["arestas"] += l["arestas"]
    res["tamanhos"] = {k: sum(1 for l in lacos if lo <= l["arestas"] <= hi) for k, (lo, hi) in
                       {"1-4": (1, 4), "5-12": (5, 12), "13-40": (13, 40), ">40": (41, 10 ** 9)}.items()}
    bm.free(); return res, lacos
r, lacos = auditar(bpy.data.objects[NOME].data, soldar=(len(A) < 3 or A[2] != "sem_solda"))
json.dump({"resumo": r, "lacos": lacos}, open(OUT, "w"), indent=1, ensure_ascii=False)
print("AUDIT", json.dumps({k: r[k] for k in ("verts", "faces", "bordas_abertas", "lacos", "arestas_nao_manifold", "verts_nao_manifold", "por_regiao", "tamanhos")}, ensure_ascii=False))
for l in r["maiores"][:8]: print("  LACO", l)
