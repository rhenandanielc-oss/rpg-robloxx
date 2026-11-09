"""S1 r4 (06/11): a sela passa a ter como foco os dois materiais REGIONAIS OFICIAIS das Planicies (pedido do usuario):
 - Couro das Planicies (estrutural): alem de assento/aba/cilha/apoios, agora tambem a MANTA (tom claro, acabamento de camurca)
   e a ALCA da mao (pegador de couro; antes Chifre Leve, que e so [PROPOSTA]). A Pele de Antilope sai da sela.
 - Ambar Solar (especial): adorno solar da cabeca 35% maior; pedras novas na traseira do assento (patilha) e em cada apoio de pe;
   continuam as pedras das argolas da cilha. Sem emissao nem efeito.
Trabalha sobre a sela r3 (com a folga medida) sem reconstruir: so materiais e pecas rigidas novas por cima. Pesos das pecas
novas = do vertice mais proximo da sela. Uso: blender -b Leao_Solar_Ref_S1r3_sela.blend -P s1_06_materiais_regionais.py -- <saida.blend>"""
import bpy, bmesh, sys, os, math
import numpy as np
from mathutils import Vector as V
from mathutils.kdtree import KDTree
RAIZ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, RAIZ)
import s1_01_sela_leao as sl
A = sys.argv[sys.argv.index("--") + 1:]
sela = bpy.data.objects[sl.NOME]; me = sela.data; PL = list(sela["pecas"])
vp = [PL[d.value] for d in me.attributes["peca"].data]; co = [v.co.copy() for v in me.vertices]
mats = [m.name for m in me.materials]
def idx(nome):
    if nome not in mats: me.materials.append(bpy.data.materials.get(nome) or sl._material(nome, *COR[nome])); mats.append(nome)
    return mats.index(nome)
COR = {"M_Sela_CouroPlanicies_Manta": ((0.36, 0.21, 0.10), 0.85, 0.0)}
# --- manta e alca -> Couro das Planicies
i_couro = mats.index("M_Sela_CouroPlanicies"); i_manta = idx("M_Sela_CouroPlanicies_Manta"); i_chifre = mats.index("M_Sela_ChifreLeve")
for p in me.polygons:
    pc = vp[p.vertices[0]]
    if pc == "manta": p.material_index = i_manta
    elif pc == "alca_chifre": p.material_index = i_couro
# --- adorno solar maior (ambar + guarnicao + raios em volta do centro da pedra da cabeca)
yh = sl.ASSENTO["yc"] - 0.80 * sl.ASSENTO["ay"]
cab = [i for i, (p, c) in enumerate(zip(vp, co)) if p in ("ambar", "ferro") and abs(c.x - sl.XC) < 0.45 and abs(c.y - (yh - 0.20)) < 0.35 and c.z > 11.5]
amb = [i for i in cab if vp[i] == "ambar"]; cen = sum((co[i] for i in amb), V()) / max(len(amb), 1)
for i in cab: me.vertices[i].co = cen + (co[i] - cen) * 1.35
# --- pedras novas de Ambar Solar: traseira do assento (patilha) e alto de cada alca dos apoios de pe
kd = KDTree(len(co))
for i, c in enumerate(co): kd.insert(c, i)
kd.balance()
assento = [i for i, p in enumerate(vp) if p == "assento"]
# alto da patilha (traseira do assento): o vertice mais alto da metade de tras; a pedra vai na face de tras, logo abaixo do topo
# (na borda de baixo ela ficava colada na manta e perto da pele: entrava 0,15 no galope)
tras_ = [i for i in assento if abs(co[i].x - sl.XC) < 0.25 and co[i].y > sl.ASSENTO["yc"] + 0.3]
topo_p = max((co[i] for i in tras_), key=lambda c: c.z)
face = [co[i] for i in tras_ if abs(co[i].z - (topo_p.z - 0.15)) < 0.08]; yb = max(c.y for c in face) if face else topo_p.y + 0.1
pt = V((sl.XC, yb + 0.01, topo_p.z - 0.15))
novas = [(pt, V((0, 1, 0.35)).normalized(), 0.16, 0.09, "patilha")]
for s in (1, -1):
    fer = [i for i, p in enumerate(vp) if p == "ferro" and s * (co[i].x - sl.XC) > 1.4 and co[i].z < 11.8 and abs(co[i].y - (-0.6)) < 0.8]
    if fer:
        topo = max((co[i] for i in fer), key=lambda c: c.z); novas.append((topo + V((0, 0, 0.04)), V((s * 0.5, -0.2, 1)).normalized(), 0.10, 0.06, "apoio_pe"))
bm = bmesh.new(); bm.from_mesh(me); i_amb = mats.index("M_Sela_AmbarSolar"); i_fer = mats.index("M_Sela_Ferro")
lay = bm.verts.layers.int.get("peca"); PLn = list(PL)
for nome in ("ambar",):
    if nome not in PLn: PLn.append(nome)
novos_v = []
for c, n, r, h, onde in novas:
    for vs_, fs_, mt in ((sl._cabochao(c, n, r, h, 14, 4)) + (i_amb,), (sl._tubo([c + (n.orthogonal().normalized() * math.cos(2 * math.pi * k / 16) + n.cross(n.orthogonal().normalized()) * math.sin(2 * math.pi * k / 16)) * (r + 0.03) for k in range(16)], 0.025, 5, fechado=True)) + (i_fer,)):
        bv = [bm.verts.new(p) for p in vs_]
        for v in bv: v[lay] = PLn.index("ambar" if mt == i_amb else "ferro"); novos_v.append((v, c))
        for f in fs_:
            try: bm.faces.new([bv[k] for k in f]).material_index = mt
            except ValueError: pass
bm.to_mesh(me); bm.free(); me.update(); sela["pecas"] = PLn
# pesos das pecas novas: do vertice original mais proximo da ancora (rigidas)
n0 = len(co); dv = me.vertices
for vi in range(n0, len(dv)):
    _, j, _ = kd.find(dv[vi].co); src = dv[j]
    for g in src.groups: sela.vertex_groups[g.group].add([vi], g.weight, "REPLACE")
bpy.context.view_layer.objects.active = sela                               # Chifre Leve fora da sela (slot sem uso removido, indices remapeados)
for o_ in bpy.context.selected_objects: o_.select_set(False)
sela.select_set(True); bpy.ops.object.material_slot_remove_unused()
for p in me.polygons: p.use_smooth = True
sela["etapa"] = "S1 r4 sela felina: foco em Couro das Planicies e Ambar Solar (proposta)"
tris = sum(len(p.vertices) - 2 for p in me.polygons)
print("MATERIAIS", [m.name for m in me.materials], "tris", tris, "vertices", len(me.vertices), "pedras_novas", [x[4] for x in novas], "adorno", len(cab))
bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A[0])); print("MATERIAIS_OK")
