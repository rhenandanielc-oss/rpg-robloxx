"""v23: MAPA SO LEITURA do leque de triangulos-agulha na prega coxa D x ventre (repouso), por LOD.
Agulha = face com aresta maior > A_MIN e proporcao (aresta maior / altura relativa a ela) > P_MIN.
Regiao igual ao diag_flanco_v22 (x < 0,4; -2,5 < y < 3,0; z < 4,2). Agrupa as agulhas em componentes (por aresta) e
descreve cada leque: faces, vertices, centro, caixa, comprimento maximo, proporcao, quantas faces/vizinhos o anel tem,
pesos dominantes dos vertices e as ilhas UV envolvidas.
Uso: blender -b <anim.blend> -P agulhas_v23.py -- <saida_json> [A_MIN] [P_MIN]"""
import bpy, bmesh, sys, os, json
from mathutils import Vector as V
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); A_MIN = float(a[1]) if len(a) > 1 else 0.35; P_MIN = float(a[2]) if len(a) > 2 else 6.0
ARM = bpy.data.objects["LoboArtico_Rig"]; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
def regiao(p): return p.x < 0.4 and -2.5 < p.y < 3.0 and p.z < 4.2
def prop(f):
    ls = [e.calc_length() for e in f.edges]; m = max(ls); h = 2 * f.calc_area() / m if m > 0 else 0
    return m, (m / h if h > 1e-9 else 999)
R = {"A_MIN": A_MIN, "P_MIN": P_MIN}
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}
    bm = bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); uvl = bm.loops.layers.uv.active
    cl = bm.faces.layers.int.get("classe_cauda")
    ag = [f for f in bm.faces if regiao(f.calc_center_median()) and (lambda m, p: m > A_MIN and p > P_MIN)(*prop(f))]
    S = set(ag); comps = []; vis = set()
    for f in ag:
        if f in vis: continue
        st = [f]; c = []; vis.add(f)
        while st:
            x = st.pop(); c.append(x)
            for e in x.edges:
                for g in e.link_faces:
                    if g in S and g not in vis: vis.add(g); st.append(g)
        comps.append(c)
    D = []
    for c in sorted(comps, key=len, reverse=True):
        vs = {v for f in c for v in f.verts}; ce = sum((v.co for v in vs), V()) / len(vs)
        mn = [min(v.co[i] for v in vs) for i in range(3)]; mx = [max(v.co[i] for v in vs) for i in range(3)]
        ws = {}
        for v in vs:
            for g in me.vertices[v.index].groups:
                ws[gn[g.group]] = ws.get(gn[g.group], 0) + g.weight / len(vs)
        D.append({"faces": [f.index for f in c], "n": len(c), "verts": sorted(v.index for v in vs), "centro": [round(x, 3) for x in ce],
                  "min": [round(x, 3) for x in mn], "max": [round(x, 3) for x in mx], "aresta_max": round(max(prop(f)[0] for f in c), 3),
                  "prop_max": round(max(prop(f)[1] for f in c), 1), "valencia_max": max(len(v.link_edges) for v in vs),
                  "pesos": {k: round(x, 2) for k, x in sorted(ws.items(), key=lambda t: -t[1]) if x > 0.05},
                  "classe": sorted({f[cl] for f in c}) if cl else None, "n_lados": sorted({len(f.verts) for f in c})})
    R[L] = {"faces_total": len(bm.faces), "tris": sum(len(f.verts) - 2 for f in bm.faces), "agulhas": len(ag), "leques": D}
    print("AG", L, len(ag), [(d["n"], d["centro"], d["aresta_max"], d["prop_max"]) for d in D], flush=True); bm.free()
json.dump(R, open(OUT, "w"), indent=1); print("AGULHAS_OK")
