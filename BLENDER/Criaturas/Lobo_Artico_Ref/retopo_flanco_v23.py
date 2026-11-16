"""v23: RETOPOLOGIA LOCAL da prega coxa DIREITA x ventre (autorizada 10/11), nos 3 LODs. anim_v21 so lido; saida <dir>.
Causa (8.24): leque de triangulos-agulha do Meshy na prega (pele continua, sem fusao). Os pesos da v22 NAO sao base.
Passos por LOD (pose de repouso, sem acao):
1. NUCLEO = agulhas (aresta maior > A_MIN e proporcao > P_MIN) dentro da caixa da prega; REMENDO = faces a distancia
   geodesica < R_REM do nucleo, so pele (classe_cauda = lado_tampa = 0) e longe da pata E. Faces cujos 3 vertices estao no
   remendo entram tambem (sem furos). A borda do remendo fica FIXA (vertices e arestas): o resto da malha nao muda.
2. REMALHA isotropica dentro do remendo (Botsch-Kobbelt), alvo Lt = mediana das arestas do anel em volta:
   dividir arestas > 4/3 Lt; colapsar < 4/5 Lt (condicao de ligacao, sem virar face, sem criar aresta > 4/3 Lt);
   girar arestas pelo criterio de Delaunay (so se a aresta nova fica colada na superficie original: |meio - sup| < TOL_GIRO
   x Lt e as faces novas nao viram); relaxar tangencialmente e PROJETAR na superficie ORIGINAL do proprio LOD (faces do
   remendo + 2 aneis), com teste de normal (nao pula para o outro lado da prega). Volume/silhueta: todos os vertices novos
   ficam na superficie de repouso original; mede-se o desvio original -> nova.
3. UV: o atlas do Meshy tem ~4 faces por ilha (LOW 5080 ilhas), entao nao da para remalhar dentro das ilhas. O remendo do
   LOW ganha ILHA PROPRIA (LSCM, sem dobras) num retangulo LIVRE do atlas (livre em todos os LODs, margem 3 px), na mesma
   densidade do corpo (~20 px/stud). Texels pintados por TRANSFERENCIA da superficie de origem: texel -> ponto 3D na face
   nova -> ponto mais proximo na superficie ORIGINAL do remendo (com teste de normal) -> UV original -> amostra
   (cor, rugosidade, emissao; normal map convertido do espaco tangente da face de origem para o da face nova).
   LOD1/LOD2: mesma ilha e mesma textura (UV = UV do ponto mais proximo no remendo novo do LOW): correspondencia visual.
4. PESOS dos vertices novos = pesos ORIGINAIS (v21) do proprio LOD interpolados no ponto de origem (baricentrico),
   <= 4 influencias, soma 1. (Faixa gradeada opcional depois: pesos_flanco_v23.py.)
5. CARTOES de pelo com raiz no remendo: raiz levada ao ponto mais proximo da pele nova (translacao rigida do cartao) e
   pesos da pele nova no ponto da raiz.
Geometria fora do remendo, rig, repouso, acoes e outras pecas iguais. Relatorio: <dir>/retopo_flanco_v23.json.
Uso: blender -b anim_v21/CR_LoboArtico_Anim.blend -P retopo_flanco_v23.py -- <dir_saida>"""
import bpy, bmesh, sys, os, json, shutil, heapq, math, statistics
import numpy as np
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.interpolate import poly_3d_calc
A_ = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(A_[0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
A_MIN, P_MIN = 0.35, 6.0
CAIXA = ((-0.95, 0.2), (-0.35, 0.95), (2.4, 3.1))                     # prega coxa D x ventre (repouso)
R_REM = {"LOW": float(os.environ.get("R_REM_LOW", 0.28)), "LOD1": float(os.environ.get("R_REM_LOD1", 0.55)), "LOD2": float(os.environ.get("R_REM_LOD2", 0.9))}
P_LIMPA = float(os.environ.get("P_LIMPA", 4.0)); ITER, TOL_GIRO, LAMB = int(os.environ.get("ITER", 8)), 0.15, 0.5
FAT_LT = {"LOW": float(os.environ.get("FAT_LT_LOW", 1.0)), "LOD1": 1.0, "LOD2": 1.0}
MARGEM = 2
REL = {"parametros": {"A_MIN": A_MIN, "P_MIN": P_MIN, "CAIXA": CAIXA, "R_REM": R_REM, "ITER": ITER, "TOL_GIRO": TOL_GIRO, "FAT_LT": FAT_LT}}
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp)); im.reload()
ARM = bpy.data.objects["LoboArtico_Rig"]; AC = ARM.animation_data.action; SL = ARM.animation_data.action_slot; ARM.animation_data.action = None
for pb in ARM.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update(); OSS = {b.name for b in ARM.data.bones}
PATA_E = ("Coxa_E", "Tibia_E")

def na_caixa(p): return all(CAIXA[i][0] < p[i] < CAIXA[i][1] for i in range(3))
def prop(f):
    ls = [e.calc_length() for e in f.edges]; m = max(ls); h = 2 * f.calc_area() / m if m > 0 else 0
    return m, (m / h if h > 1e-9 else 999.0)
def agulha(f): m, p = prop(f); return m > A_MIN and p > P_MIN
def estat_faces(fs):
    ps = [prop(f) for f in fs]
    return {"faces": len(fs), "agulhas(>%.2f,>%g)" % (A_MIN, P_MIN): sum(1 for m, p in ps if m > A_MIN and p > P_MIN),
            "proporcao>4": sum(1 for m, p in ps if p > 4), "proporcao_max": round(max(p for m, p in ps), 1), "aresta_max": round(max(m for m, p in ps), 3),
            "angulo_min_graus": round(min(min_ang(f) for f in fs), 1)}
def min_ang(f):
    vs = [v.co for v in f.verts]; r = 180.0
    for i in range(3):
        a, b, c = vs[i], vs[(i + 1) % 3], vs[(i + 2) % 3]; u, w = b - a, c - a
        if u.length > 1e-9 and w.length > 1e-9: r = min(r, math.degrees(u.angle(w)))
    return r

# ---------------------------------------------------------------- atlas: retangulo livre em TODOS os LODs
mat = bpy.data.objects["LOW_Corpo"].data.materials[0]
IM = {k: n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image for k in ("_cor", "_normal", "_rugosidade", "_emissao") if k in n.image.name}
ARR = {}
for k, im in IM.items():
    a = np.empty(im.size[0] * im.size[1] * 4, np.float32); im.pixels.foreach_get(a); ARR[k] = a.reshape(im.size[1], im.size[0], 4)
H, W = ARR["_cor"].shape[:2]; ORIG = {k: v.copy() for k, v in ARR.items()}
def raster(tri, cb, e_px=1.5):
    xs = [u[0] * W for u in tri]; ys = [u[1] * H for u in tri]
    x0, x1 = max(0, int(min(xs)) - 1), min(W - 1, int(max(xs)) + 1); y0, y1 = max(0, int(min(ys)) - 1), min(H - 1, int(max(ys)) + 1)
    (ax, ay), (bx, by), (cx, cy) = zip(xs, ys); den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
    if abs(den) < 1e-12: return
    X, Y = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
    l1 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den; l2 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den; l3 = 1 - l1 - l2
    e = e_px / max(1.0, abs(den) ** 0.5)
    cb(y0, x0, (l1 > -e) & (l2 > -e) & (l3 > -e), (l1, l2, l3))
oc = np.zeros((H, W), bool)
for L in ("LOW", "LOD1", "LOD2"):
    me = bpy.data.objects[L + "_Corpo"].data; uv = me.uv_layers.active.data
    for p in me.polygons:
        li = list(p.loop_indices)
        for k in range(1, len(li) - 1):
            def marca(y0, x0, m, _): oc[y0:y0 + m.shape[0], x0:x0 + m.shape[1]] |= m
            raster([uv[li[0]].uv[:], uv[li[k]].uv[:], uv[li[k + 1]].uv[:]], marca)
dl = oc.copy()
for dy in range(-3, 4):
    for dx in range(-3, 4): dl |= np.roll(np.roll(oc, dy, 0), dx, 1)
II = np.zeros((H + 1, W + 1), np.int64); II[1:, 1:] = dl.cumsum(0).cumsum(1)
def livre(x, y, w, h): return II[y + h, x + w] - II[y, x + w] - II[y + h, x] + II[y, x] == 0

# ---------------------------------------------------------------- utilidades de malha
def ilha_borda(bm, rem):
    return {v for f in rem for v in f.verts if any(g not in rem for g in v.link_faces)}
def interior(e, rem): return len(e.link_faces) == 2 and all(f in rem for f in e.link_faces)

def retopo(L):
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; gn = {g.index: g.name for g in o.vertex_groups}
    bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    cl = bm.faces.layers.int.get("classe_cauda"); la = bm.faces.layers.int.get("lado_tampa"); dfl = bm.verts.layers.deform.verify(); uvl = bm.loops.layers.uv.active
    REM = bm.faces.layers.int.new("retopo_v23")
    def wv(v): return {gn[k]: x for k, x in v[dfl].items() if gn.get(k) in OSS}
    nucleo = [f for f in bm.faces if na_caixa(f.calc_center_median()) and agulha(f) and f[cl] == 0 and f[la] == 0]
    assert nucleo, L
    ok = lambda f: f[cl] == 0 and f[la] == 0 and all(sum(wv(v).get(k, 0) for k in PATA_E) < 0.1 for v in f.verts)
    d = {}; h = []
    for f in nucleo:
        for v in f.verts: d[v] = 0.0; heapq.heappush(h, (0.0, v.index))
    while h:
        dd, i = heapq.heappop(h); v = bm.verts[i]
        if dd > d.get(v, 1e9): continue
        for e in v.link_edges:
            u = e.other_vert(v); nd = dd + e.calc_length()
            if nd < R_REM[L] and nd < d.get(u, 1e9) and any(ok(f) for f in u.link_faces): d[u] = nd; heapq.heappush(h, (nd, u.index))
    rem = {f for f in bm.faces if ok(f) and all(v in d for v in f.verts)} | set(nucleo)
    # sem furos: componentes do complemento cercadas pelo remendo entram (as pequenas)
    viz = {g for f in rem for v in f.verts for g in v.link_faces if g not in rem}
    for g in sorted(viz, key=lambda g: g.index):
        if ok(g) and sum(1 for e in g.edges if any(x in rem for x in e.link_faces)) >= 2: rem.add(g)
    # um so componente (o maior)
    comp = []; vis = set()
    for f in rem:
        if f in vis: continue
        st = [f]; c = []; vis.add(f)
        while st:
            x = st.pop(); c.append(x)
            for e in x.edges:
                for g in e.link_faces:
                    if g in rem and g not in vis: vis.add(g); st.append(g)
        comp.append(c)
    rem = set(max(comp, key=len))
    for f in rem: f[REM] = 1
    antes = estat_faces(list(rem)); area_antes = sum(f.calc_area() for f in rem)
    # superficie ORIGINAL (remendo + 2 aneis) para projecao, UV de origem e pesos de origem
    srcf = set(rem)
    for _ in range(2): srcf |= {g for f in list(srcf) for v in f.verts for g in v.link_faces if ok(g)}
    srcf = list(srcf)
    SP = [v.co.copy() for v in bm.verts]; SF = [[v.index for v in f.verts] for f in srcf]
    SW = {v.index: wv(v) for f in srcf for v in f.verts}
    bm.normal_update(); SN = [[v.normal.copy() for v in f.verts] for f in srcf]; SUV = [[l[uvl].uv.copy() for l in f.loops] for f in srcf]
    SRM = [f in rem for f in srcf]
    bvh_src = BVHTree.FromPolygons(SP, SF)
    remf = [k for k in range(len(srcf)) if SRM[k]]; bvh_rem = BVHTree.FromPolygons(SP, [SF[k] for k in remf])
    borda_v = ilha_borda(bm, rem)
    anel = [e.calc_length() for f in bm.faces if f not in rem and any(v in borda_v for v in f.verts) for e in f.edges]
    Lt = statistics.median(anel) * FAT_LT[L]; lo, hi = 0.8 * Lt, 4.0 / 3.0 * Lt
    def projetar(p, n):
        loc, nr, fi, dist = bvh_src.find_nearest(p)
        if loc is not None and (n is None or nr.dot(n) > 0.3): return loc, fi
        for r in (0.6, 0.3):                          # procura so ate onde a normal concorda
            best = None
            for (lc, nr2, fi2, ds) in bvh_src.find_nearest_range(p, max(dist * 3, Lt) * r / 0.3):
                if (n is None or nr2.dot(n) > 0.3) and (best is None or ds < best[2]): best = (lc, fi2, ds)
            if best: return best[0], best[1]
        return loc, fi
    def remendo(): return [f for f in bm.faces if f[REM]]
    def arestas():                                     # ordem deterministica (indices), sem conjuntos de BMesh
        bm.edges.index_update(); vis = set(); r = []
        for f in remendo():
            for e in f.edges:
                if e.index not in vis: vis.add(e.index); r.append(e)
        return r
    def fixos():
        return {v for f in remendo() for v in f.verts if any(not g[REM] for g in v.link_faces) or v.is_boundary}
    n_div = n_col = n_gir = 0
    for it in range(ITER):
        # 1. dividir
        fx = fixos(); es = [e for e in arestas() if e.calc_length() > hi and all(g[REM] for g in e.link_faces) and len(e.link_faces) == 2]
        if es:
            r = bmesh.ops.subdivide_edges(bm, edges=es, cuts=1, use_grid_fill=False)
            novas = [f for f in bm.faces if f[REM] and len(f.verts) > 3]
            bmesh.ops.triangulate(bm, faces=novas, quad_method="BEAUTY", ngon_method="BEAUTY"); n_div += len(es)
        # 2. colapsar
        fx = fixos(); bm.normal_update()
        for e in sorted(arestas(), key=lambda e: (round(e.calc_length(), 9), e.index)):
            if not e.is_valid or e.calc_length() >= lo or not all(g[REM] for g in e.link_faces) or len(e.link_faces) != 2: continue
            a, b = e.verts
            if a in fx and b in fx: continue
            if b in fx: a, b = b, a                            # a fica (fixo ou ponto medio)
            alvo = a.co.copy() if a in fx else (a.co + b.co) / 2
            na = {x.other_vert(a) for x in a.link_edges}; nb = {x.other_vert(b) for x in b.link_edges}
            if len(na & nb) != 2: continue
            if any((alvo - u.co).length > hi for u in (na | nb) - {a, b}): continue
            bom = True
            for vv in (a, b):
                for f in vv.link_faces:
                    if a in f.verts and b in f.verts: continue
                    ps = [alvo if x in (a, b) else x.co for x in f.verts]; n1 = (ps[1] - ps[0]).cross(ps[2] - ps[0])
                    if n1.length < 1e-10 or n1.normalized().dot(f.normal) < 0.5: bom = False; break
                if not bom: break
            if not bom: continue
            bmesh.ops.pointmerge(bm, verts=[a, b], merge_co=alvo); n_col += 1
            fx = fixos()
        # 3. girar (Delaunay + fidelidade a superficie)
        bm.normal_update()
        for e in arestas():
            if not e.is_valid or len(e.link_faces) != 2 or not all(g[REM] for g in e.link_faces): continue
            f1, f2 = e.link_faces
            if len(f1.verts) != 3 or len(f2.verts) != 3: continue
            a, b = e.verts; c = next(v for v in f1.verts if v not in (a, b)); dv = next(v for v in f2.verts if v not in (a, b))
            if c == dv or any(x.other_vert(c) == dv for x in c.link_edges): continue
            ang = lambda p, q, r: (q.co - p.co).angle(r.co - p.co) if (q.co - p.co).length > 1e-9 and (r.co - p.co).length > 1e-9 else 0
            if ang(c, a, b) + ang(dv, a, b) <= math.pi + 1e-3: continue
            meio = (c.co + dv.co) / 2; loc, _, _, ds = bvh_src.find_nearest(meio)
            if loc is None or ds > TOL_GIRO * Lt: continue
            nm = (f1.normal + f2.normal).normalized(); bom = True
            for t in ((c, dv, a), (dv, c, b)):
                n1 = (t[1].co - t[0].co).cross(t[2].co - t[0].co)
                if n1.length < 1e-10 or abs(n1.normalized().dot(nm)) < 0.6: bom = False
            if not bom: continue
            ne = bmesh.utils.edge_rotate(e, True)
            if ne:
                n_gir += 1
                for g in ne.link_faces:
                    g.normal_update()
                    if g.normal.dot(nm) < 0: bom = False
                if not bom: bmesh.utils.edge_rotate(ne, True); n_gir -= 1
        # 4. relaxar + projetar
        bm.normal_update(); fx = fixos(); vs = {v for f in remendo() for v in f.verts} - fx
        nov = {}
        for v in vs:
            nbr = [x.other_vert(v).co for x in v.link_edges]; c = sum(nbr, V()) / len(nbr); dlt = c - v.co; n = v.normal
            p = v.co + LAMB * (dlt - n * dlt.dot(n)); nov[v] = projetar(p, n)[0]
        for v, p in nov.items(): v.co = p
    # 5. LIMPEZA dirigida: triangulos com proporcao > P_LIMPA -> girar a aresta maior (se melhora o menor angulo e fica
    #    colada na superficie) ou dividir a aresta maior (se interior e > Lt) ou colapsar a menor; depois relaxa/projeta
    n_limpa = 0
    for rodada in range(6):
        bm.normal_update(); bm.faces.index_update(); fx = fixos(); mudou = False
        ruins = sorted((f for f in remendo() if len(f.verts) == 3 and prop(f)[1] > P_LIMPA), key=lambda f: (-prop(f)[1], f.index))
        for f in ruins:
            if not f.is_valid or prop(f)[1] <= P_LIMPA: continue
            es_ = sorted(f.edges, key=lambda e: -e.calc_length()); e = es_[0]
            if len(e.link_faces) == 2 and all(g[REM] for g in e.link_faces):
                f1, f2 = e.link_faces; a, b = e.verts
                c = next((v for v in f1.verts if v not in (a, b)), None); dv = next((v for v in f2.verts if v not in (a, b)), None)
                if c and dv and c != dv and not any(x.other_vert(c) == dv for x in c.link_edges):
                    def mang(t):
                        r = 180
                        for i in range(3):
                            p, q, w = t[i].co, t[(i + 1) % 3].co, t[(i + 2) % 3].co
                            if (q - p).length > 1e-9 and (w - p).length > 1e-9: r = min(r, math.degrees((q - p).angle(w - p)))
                        return r
                    antes_a = min(min_ang(f1), min_ang(f2)); depois_a = min(mang((c, dv, a)), mang((dv, c, b)))
                    meio = (c.co + dv.co) / 2; loc, _, _, ds = bvh_src.find_nearest(meio); nm = (f1.normal + f2.normal).normalized()
                    sinal = all(((t[1].co - t[0].co).cross(t[2].co - t[0].co)).normalized().dot(nm) > 0.3 for t in ((c, dv, a), (dv, c, b)) if ((t[1].co - t[0].co).cross(t[2].co - t[0].co)).length > 1e-10)
                    if depois_a > antes_a + 1 and ds < TOL_GIRO * Lt and sinal:
                        ne = bmesh.utils.edge_rotate(e, True)
                        if ne: n_limpa += 1; mudou = True; continue
                if e.calc_length() > Lt:
                    bmesh.ops.subdivide_edges(bm, edges=[e], cuts=1, use_grid_fill=False)
                    bmesh.ops.triangulate(bm, faces=[g for g in bm.faces if g[REM] and len(g.verts) > 3], quad_method="BEAUTY", ngon_method="BEAUTY")
                    n_limpa += 1; mudou = True; continue
            e = es_[-1]
            if len(e.link_faces) == 2 and all(g[REM] for g in e.link_faces):
                a, b = e.verts
                if not (a in fx and b in fx):
                    if b in fx: a, b = b, a
                    alvo = a.co.copy() if a in fx else (a.co + b.co) / 2
                    na = {x.other_vert(a) for x in a.link_edges}; nb = {x.other_vert(b) for x in b.link_edges}
                    if len(na & nb) == 2:
                        bom = True
                        for vv in (a, b):
                            for g in vv.link_faces:
                                if a in g.verts and b in g.verts: continue
                                ps = [alvo if x in (a, b) else x.co for x in g.verts]; n1 = (ps[1] - ps[0]).cross(ps[2] - ps[0])
                                if n1.length < 1e-10 or n1.normalized().dot(g.normal) < 0.5: bom = False
                        if bom: bmesh.ops.pointmerge(bm, verts=[a, b], merge_co=alvo); n_limpa += 1; mudou = True; fx = fixos()
        bm.normal_update(); fx = fixos(); vs = [v for v in {v.index: v for f in remendo() for v in f.verts}.values() if v not in fx]; nov = {}
        for v in vs:
            nbr = [x.other_vert(v).co for x in v.link_edges]; c = sum(nbr, V()) / len(nbr); dlt = c - v.co; n = v.normal
            nov[v] = projetar(v.co + LAMB * (dlt - n * dlt.dot(n)), n)[0]
        for v, p in nov.items(): v.co = p
        if not mudou: break
    bm.normal_update(); rem2 = remendo(); depois = estat_faces(rem2)
    fxb = fixos(); depois["ruins_restantes_(prop>%g)" % P_LIMPA] = [[round(prop(f)[1], 1), sum(1 for v in f.verts if v in fxb)] for f in rem2 if prop(f)[1] > P_LIMPA]
    # desvio de forma: pontos da superficie ORIGINAL do remendo -> superficie nova (e o contrario)
    NV = [v.co.copy() for v in bm.verts]; bm.verts.index_update(); bm.verts.ensure_lookup_table(); NVi = [v.co.copy() for v in bm.verts]
    bvh_new = BVHTree.FromPolygons(NVi, [[v.index for v in f.verts] for f in rem2])
    amos = []
    for k in remf:
        ps = [SP[i] for i in SF[k]]
        for b1, b2 in ((1 / 3, 1 / 3), (0.6, 0.2), (0.2, 0.6), (0.2, 0.2)):
            amos.append(ps[0] * b1 + ps[1] * b2 + ps[2] * (1 - b1 - b2))
    dev = [bvh_new.find_nearest(p)[3] for p in amos]; dev2 = [bvh_rem.find_nearest(v.co)[3] for f in rem2 for v in f.verts]
    # pesos (v21 do proprio LOD) e fonte de cada vertice novo
    fonte = {}
    for f in rem2:
        for v in f.verts:
            if v in fonte: continue
            loc, fi = projetar(v.co, v.normal); bc = poly_3d_calc([SP[i] for i in SF[fi]], loc); w = {}
            for i, b in zip(SF[fi], bc):
                for k, x in SW[i].items(): w[k] = w.get(k, 0) + x * b
            fonte[v] = (fi, loc, w)
    gi = {g.name: g.index for g in o.vertex_groups}; n_inf = []
    for v, (fi, loc, w) in fonte.items():
        if any(not g[REM] for g in v.link_faces): continue          # borda: pesos originais intactos
        w = dict(sorted(((k, x) for k, x in w.items() if x > 1e-4), key=lambda t: -t[1])[:4]); s = sum(w.values())
        for k in list(v[dfl].keys()): del v[dfl][k]
        for k, x in w.items(): v[dfl][gi[k]] = x / s
        n_inf.append(len(w))
    REL_L = {"Lt": round(Lt, 4), "remendo_antes": antes, "remendo_depois": depois, "area_antes": round(area_antes, 4), "area_depois": round(sum(f.calc_area() for f in rem2), 4),
             "tris_corpo_antes": len(me.polygons), "divisoes": n_div, "colapsos": n_col, "giros": n_gir, "limpeza": n_limpa,
             "desvio_sup_original_para_nova_max": round(max(dev), 4), "desvio_medio": round(sum(dev) / len(dev), 4),
             "desvio_vertices_novos_para_original_max": round(max(dev2), 4), "vertices_borda_fixos": len(borda_v)}
    RES_SRC[L] = bvh_src
    return o, bm, rem2, REM, fonte, (SP, SF, SUV, SN, srcf, remf), REL_L

def frame_tbn(ps, uvs, n):
    """base tangente com a normal SUAVE interpolada n (como o MikkTSpace: T do gradiente UV ortogonalizada contra n)."""
    e1, e2 = ps[1] - ps[0], ps[2] - ps[0]; d1, d2 = uvs[1] - uvs[0], uvs[2] - uvs[0]; r = d1.x * d2.y - d2.x * d1.y; n = n.normalized()
    if abs(r) < 1e-14: t = (e1 - n * n.dot(e1)).normalized(); return t, n.cross(t), n
    t = (e1 * d2.y - e2 * d1.y) / r; b = (e2 * d1.x - e1 * d2.x) / r
    t = (t - n * n.dot(t)).normalized(); sgn = 1.0 if n.cross(t).dot(b) >= 0 else -1.0
    return t, n.cross(t) * sgn, n
def frame_tb(ps, uvs):
    e1, e2 = ps[1] - ps[0], ps[2] - ps[0]; d1, d2 = uvs[1] - uvs[0], uvs[2] - uvs[0]; r = d1.x * d2.y - d2.x * d1.y
    n = e1.cross(e2).normalized()
    if abs(r) < 1e-14: t = e1.normalized(); return t, n.cross(t), n
    t = (e1 * d2.y - e2 * d1.y) / r; b = (e2 * d1.x - e1 * d2.x) / r
    t = (t - n * n.dot(t)).normalized(); sgn = 1.0 if n.cross(t).dot(b) >= 0 else -1.0
    return t, n.cross(t) * sgn, n

def lscm(vids, tris, P):
    """LSCM (Levy 2002): vids = vertices, tris = triangulos (indices em vids), P = posicoes. Retorna uv (n x 2)."""
    n = len(vids); idx = {v: i for i, v in enumerate(vids)}
    pa, pb = max(((a, b) for a in vids[::3] for b in vids[::3]), key=lambda t: (P[t[0]] - P[t[1]]).length)
    rows_r = []; rows_i = []
    for t in tris:
        p0, p1, p2 = (P[vids[k]] for k in t); x = (p1 - p0).normalized(); nn = (p1 - p0).cross(p2 - p0); dT = nn.length
        if dT < 1e-12: continue
        y = nn.normalized().cross(x); q = [(0.0, 0.0), ((p1 - p0).length, 0.0), ((p2 - p0).dot(x), (p2 - p0).dot(y))]
        Ws = [complex(q[2][0] - q[1][0], q[2][1] - q[1][1]), complex(q[0][0] - q[2][0], q[0][1] - q[2][1]), complex(q[1][0] - q[0][0], q[1][1] - q[0][1])]
        s = 1 / math.sqrt(dT); rr = np.zeros(2 * n); ri = np.zeros(2 * n)
        for k, wk in zip(t, Ws):
            a, b = wk.real * s, wk.imag * s; j = k
            rr[j] += a; rr[n + j] -= b; ri[j] += b; ri[n + j] += a
        rows_r.append(rr); rows_i.append(ri)
    M = np.array(rows_r + rows_i); fixo = {idx[pa]: (0.0, 0.0), idx[pb]: ((P[pa] - P[pb]).length, 0.0)}
    livres = [j for j in range(2 * n) if (j % n) not in fixo]; bvec = np.zeros(M.shape[0])
    for j, (u, v) in fixo.items(): bvec -= M[:, j] * u + M[:, n + j] * v
    sol = np.linalg.lstsq(M[:, livres], bvec, rcond=None)[0]; X = np.zeros(2 * n)
    for j, (u, v) in fixo.items(): X[j], X[n + j] = u, v
    X[livres] = sol
    return np.stack([X[:n], X[n:]], 1)

def amostra(k, u, v):
    x = min(max(u * W - 0.5, 0), W - 1.001); y = min(max(v * H - 0.5, 0), H - 1.001); x0, y0 = int(x), int(y); fx, fy = x - x0, y - y0
    A = ORIG[k]; return (A[y0, x0] * (1 - fx) * (1 - fy) + A[y0, x0 + 1] * fx * (1 - fy) + A[y0 + 1, x0] * (1 - fx) * fy + A[y0 + 1, x0 + 1] * fx * fy)

# ---------------------------------------------------------------- por LOD: retopo + ilha UV propria + texels da superficie de origem DO LOD
RES = {}; RES_SRC = {}; DENS = {"LOW": 20.3, "LOD1": 17.1, "LOD2": 14.0}      # px/stud medidos no atlas (v21)
def alocar(w, h):
    for y in range(0, H - h):
        for x in range(0, W - w):
            if livre(x, y, w, h): return (x, y, w, h)
    return None
for LL in ("LOW", "LOD1", "LOD2"):
  o, bm, rem, REM, fonte, SRCD, R = retopo(LL); SP, SF, SUV, SN, srcf, remf = SRCD
  bm.verts.index_update(); vids = sorted({v.index for f in rem for v in f.verts}); bm.verts.ensure_lookup_table()
  P = {v.index: v.co.copy() for v in bm.verts}; loc_id = {v: i for i, v in enumerate(vids)}
  tris = [[loc_id[v.index] for v in f.verts] for f in rem]
  UV = lscm(vids, tris, P)
  # dobra (faces invertidas no UV)?
  inv = 0
  for t in tris:
      a, b, c = UV[t[0]], UV[t[1]], UV[t[2]]
      if (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]) < 0: inv += 1
  if inv > len(tris) / 2: UV[:, 1] *= -1; inv = len(tris) - inv
  # PCA -> eixo longo na largura; escala para a densidade do corpo
  c0 = UV.mean(0); _, _, vt = np.linalg.svd(UV - c0); UV = (UV - c0) @ vt.T
  if np.linalg.det(vt) < 0: UV[:, 1] *= -1
  A3 = sum(f.calc_area() for f in rem); A2 = sum(abs((UV[t[1]][0] - UV[t[0]][0]) * (UV[t[2]][1] - UV[t[0]][1]) - (UV[t[1]][1] - UV[t[0]][1]) * (UV[t[2]][0] - UV[t[0]][0])) / 2 for t in tris)
  mn, mx = UV.min(0), UV.max(0); ext = mx - mn; esc_dens = DENS[LL] / math.sqrt(A2 / A3)   # px por unidade LSCM na densidade do corpo deste LOD
  RET = None; fat = 1.0
  while RET is None and fat > 0.55:
      esc = esc_dens * fat; RET = alocar(int(math.ceil(ext[0] * esc)) + 2 * MARGEM + 1, int(math.ceil(ext[1] * esc)) + 2 * MARGEM + 1); fat -= 0.05
  assert RET, "sem retangulo livre no atlas para " + LL
  x0r, y0r, wr, hr = RET; dl[max(0, y0r - 3):y0r + hr + 3, max(0, x0r - 3):x0r + wr + 3] = True; II[1:, 1:] = dl.cumsum(0).cumsum(1)
  UVpx = (UV - mn) * esc + np.array([x0r + MARGEM, y0r + MARGEM])
  R["uv"] = {"faces_invertidas_no_uv": inv, "densidade_px_por_stud": round(esc * math.sqrt(A2 / A3), 2), "densidade_corpo_deste_LOD": DENS[LL], "retangulo_atlas_px": list(RET), "ilha_px": [round(float(x), 1) for x in ext * esc]}
  # estiramento do UV (razao de valores singulares por face)
  est = []
  for t in tris:
      p0, p1, p2 = (P[vids[k]] for k in t); x = (p1 - p0).normalized(); nn = (p1 - p0).cross(p2 - p0)
      if nn.length < 1e-12: continue
      y = nn.normalized().cross(x); Q = np.array([[(p1 - p0).length, (p2 - p0).dot(x)], [0, (p2 - p0).dot(y)]])
      U2 = np.array([UVpx[t[1]] - UVpx[t[0]], UVpx[t[2]] - UVpx[t[0]]]).T; J = U2 @ np.linalg.inv(Q); s = np.linalg.svd(J, compute_uv=False); est.append(s[0] / max(s[1], 1e-9))
  R["uv"]["estiramento_max_sv"] = round(max(est), 2); R["uv"]["estiramento_mediano"] = round(statistics.median(est), 3)
  for f in rem:
      for l in f.loops:
          u = UVpx[loc_id[l.vert.index]]; l[bm.loops.layers.uv.active].uv = (u[0] / W, u[1] / H)
  # texels: ponto 3D na face nova -> superficie ORIGINAL do remendo -> UV original -> amostra
  bvh_orig_rem = BVHTree.FromPolygons(SP, [SF[k] for k in remf]); uvl = bm.loops.layers.uv.active
  cheio = np.zeros((H, W), bool); n_tex = 0; rej = 0   # so este retangulo
  for f in rem:
      ps = [v.co.copy() for v in f.verts]; us = [l[uvl].uv.copy() for l in f.loops]; tn, bn, nn = frame_tb(ps, us); vn = [v.normal.copy() for v in f.verts]
      def pinta(y0, x0, m, bc):
          global n_tex, rej
          l1, l2, l3 = bc
          for (yy, xx) in zip(*np.nonzero(m)):
              Y, X = y0 + yy, x0 + xx
              if not (x0r <= X < x0r + wr and y0r <= Y < y0r + hr): continue
              b = np.clip([l1[yy, xx], l2[yy, xx], l3[yy, xx]], 0, 1); b = b / b.sum(); p3 = ps[0] * b[0] + ps[1] * b[1] + ps[2] * b[2]
              loc, nr, fi, ds = bvh_orig_rem.find_nearest(p3)
              if nr.dot(nn) < 0.3:
                  cand = [c for c in bvh_orig_rem.find_nearest_range(p3, max(ds * 3, 0.1)) if c[1].dot(nn) > 0.3]
                  if cand: loc, nr, fi, ds = min(cand, key=lambda c: c[3])
                  else: rej += 1
              k = remf[fi]; sp = [SP[i] for i in SF[k]]; bc2 = poly_3d_calc(sp, loc); su = sum((SUV[k][j] * bc2[j] for j in range(3)), V((0, 0)))
              for key in ARR:
                  s = amostra(key, su.x, su.y)
                  if key == "_normal":
                      ts, bs, ns = frame_tbn(sp, SUV[k], sum((SN[k][j] * bc2[j] for j in range(3)), V())); q = s[:3] * 2 - 1; nob = ts * q[0] + bs * q[1] + ns * q[2]
                      tq, bq, nq = frame_tbn(ps, us, vn[0] * b[0] + vn[1] * b[1] + vn[2] * b[2])
                      q2 = np.array([nob.dot(tq), nob.dot(bq), nob.dot(nq)]); q2 = q2 / max(np.linalg.norm(q2), 1e-9); s = np.array([*(q2 * 0.5 + 0.5), 1.0], np.float32)
                  ARR[key][Y, X] = s
              cheio[Y, X] = True; n_tex += 1
      raster([u[:] for u in us], pinta, e_px=1.0)
  # sangria: resto do retangulo copia o texel cheio mais proximo
  ys, xs = np.nonzero(cheio); pts = np.stack([ys, xs], 1)
  for Y in range(y0r, y0r + hr):
      for X in range(x0r, x0r + wr):
          if not cheio[Y, X]:
              j = int(np.argmin((pts[:, 0] - Y) ** 2 + (pts[:, 1] - X) ** 2))
              for key in ARR: ARR[key][Y, X] = ARR[key][pts[j, 0], pts[j, 1]]
  R["uv"]["texels_transferidos"] = n_tex; R["uv"]["texels_sem_origem_com_normal_compativel"] = rej
  R["tris_corpo_depois"] = len(bm.faces); bm.to_mesh(o.data); o.data.update(); bm.free(); RES[LL] = (o, R)
for k, im in IM.items():
    im.pixels.foreach_set(ARR[k].ravel()); im.filepath_raw = bpy.path.abspath(im.filepath); im.file_format = "PNG"; im.save()

# ---------------------------------------------------------------- cartoes de pelo com raiz no remendo
for L in ("LOW", "LOD1"):
    o, R = RES[L]; po = bpy.data.objects.get(L + "_Pelagem")
    if not po: continue
    me = o.data; gn = {g.index: g.name for g in o.vertex_groups}; at = me.attributes["retopo_v23"].data
    pos = [v.co.copy() for v in me.vertices]; fac = [list(p.vertices) for p in me.polygons]; bvh = BVHTree.FromPolygons(pos, fac)
    WC = [{gn[g.group]: g.weight for g in v.groups if gn[g.group] in OSS} for v in me.vertices]
    pb_ = bmesh.new(); pb_.from_mesh(po.data); pb_.verts.ensure_lookup_table(); dfl = pb_.verts.layers.deform.verify(); gi = {g.name: g.index for g in po.vertex_groups}
    vis = set(); n_c = 0; desl = []
    for v0 in pb_.verts:
        if v0.index in vis: continue
        st, cc = [v0], []; vis.add(v0.index)
        while st:
            x = st.pop(); cc.append(x)
            for e in x.link_edges:
                u = e.other_vert(x)
                if u.index not in vis: vis.add(u.index); st.append(u)
        raiz = min(cc, key=lambda x: bvh.find_nearest(x.co)[3]); loc, _, fi, dist0 = bvh.find_nearest(raiz.co)
        if not at[fi].value: continue
        # raiz -> pele nova: mantem a mesma distancia da raiz a pele que tinha antes (medida na superficie ORIGINAL)
        d_old = RES_SRC[L].find_nearest(raiz.co)[3] if L in RES_SRC else dist0
        t = (loc - raiz.co) * (1 - d_old / max(dist0, 1e-9)) if dist0 > d_old else V()
        for x in cc: x.co += t
        desl.append(t.length)
        bc = poly_3d_calc([pos[i] for i in fac[fi]], loc); w = {}
        for i, b in zip(fac[fi], bc):
            for k, xw in WC[i].items(): w[k] = w.get(k, 0) + xw * b
        w = dict(sorted(((k, x) for k, x in w.items() if x > 1e-4), key=lambda t: -t[1])[:4]); s = sum(w.values())
        for x in cc:
            for k in list(x[dfl].keys()): del x[dfl][k]
            for k, xw in w.items():
                if k not in gi: gi[k] = po.vertex_groups.new(name=k).index
                x[dfl][gi[k]] = xw / s
        n_c += 1
    pb_.to_mesh(po.data); po.data.update(); pb_.free()
    R["cartoes_reposicionados_repesados"] = n_c; R["cartoes_translacao_max"] = round(max(desl, default=0), 4)
REL.update({L: R for L, (o, R) in RES.items()})
for L, (o, R) in RES.items(): print("V23 retopo", L, json.dumps(R), flush=True)
json.dump(REL, open(os.path.join(OUT, "retopo_flanco_v23.json"), "w"), indent=1, default=float)
ARM.animation_data.action = AC
if SL: ARM.animation_data.action_slot = SL
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("RETOPO_V23_OK", flush=True)
