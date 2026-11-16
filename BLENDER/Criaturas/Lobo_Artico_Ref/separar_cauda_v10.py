"""v10: separa a cauda da coxa/jarrete ESQUERDOS (fusao topologica herdada do Meshy; diag_cauda_v10.py) no corpo dos 3
LODs, sobre o rig v9 (rig_v9/ preservado). Mesmo esqueleto, nomes, hierarquia, repouso, acao e pesos fora da regiao.
Tentativa 1 (descartada, registrada na ficha): tirar a faixa |d_pata - d_cauda| < W e tapar. O buraco de uma faixa tem UMA
borda que passa pelos dois lados, e o preenchimento refazia a ponte; e a distancia aos eixos dos ossos erra o lugar da
ponte (os ossos da cauda ficam no fundo do volume, a linha 'equidistante' caia dentro da propria cauda).
Metodo atual, por LOD (corpo):
1. linha de corte = onde as distancias GEODESICAS (Dijkstra pelas arestas da pele, abaixo da raiz) a sementes certas da
   cauda (dorso da cauda y > 4,1, ponta solta z < 0,95) e da pata E (lado de fora x > 1,3, pe solto z < 0,95) se igualam,
   do lado E (x > -0,15), 0,95 < z < 3,95: a ponte de pele. Sai UMA linha em U (face interna da cauda, fundo em z ~1,2,
   face externa) com as pontas junto a raiz (z ~3,76 e 3,89);
2. cada face da caixa recebe a classe cauda/pata pelo sinal de G (ilhas < 25 faces viram a classe vizinha) e a pele e
   DESCOLADA (split_edges) nas arestas entre as classes: nada e retirado nem dividido, o repouso nao muda (a 1a versao
   inseria vertices sobre a linha exata: +230 tris, estourava os 20k do LOD0);
3. a abertura de cada lado e fechada com tampa PROPRIA (~140/60/24 tris por LOD: preenchimento + subdivisao ate a aresta-alvo + relaxamento com a
   borda fixa); as duas tampas so se tocam na borda (linha de contato) e no fecho junto a raiz; depois cada tampa e
   reprojetada num cilindro em torno do eixo real do seu lado (forma de volume, nao um plano);
3b. a pele da faixa de contato (a menos de 0,15 do outro lado no repouso: escondida na v9) e alisada por lado (lascas),
    no maximo 0,08 por vertice;
4. UV dos vertices das tampas = UV do ponto mais proximo da pele restante do MESMO lado (sem novo bake: textura de pelo);
5. pesos por CONECTIVIDADE abaixo da raiz (z_raiz = min(3,70; pontas do corte - 0,05)): 3 passadas de alisamento dentro de
   cada componente so em x > -0,3 (pata E inteira e metade E da cauda; os componentes alcancam a pata D pelo perineo e
   ela fica como na v9) e DEPOIS no componente da cauda saem os ossos da pata traseira ESQUERDA (o lado D, sem fusao, fica
   como na v9 e serve de controle) e no da pata os da cauda; a remocao
   cresce suave de z_raiz (pesos da v9) ate z_raiz - 0,45 (total); vertices novos copiam o vizinho restante mais
   proximo do mesmo componente; <= 4 influencias;
6. cartoes de pelo da regiao: de novo o peso da pele na raiz (do componente certo).
Uso: blender -b rig_v9/CR_LoboArtico_Rig.blend -P separar_cauda_v10.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math, shutil, heapq
from mathutils import Vector as V
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils.interpolate import poly_3d_calc
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); sc = bpy.context.scene
for im in bpy.data.images:                                              # texturas: copias proprias da v10
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
for f in ("rig_pivos.json", "acao_v9.json"): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
ARM = bpy.data.objects["LoboArtico_Rig"]; B = ARM.data.bones; OSS = [b.name for b in B]
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def dseg(p, h, t):
    ab = t - h; u = max(0.0, min(1.0, (p - h).dot(ab) / ab.length_squared)); return (p - (h + ab * u)).length
PATA_T = ("Coxa", "Tibia", "Metatarso", "DedosPe")
PATA_E = tuple(n + "_E" for n in PATA_T)                             # o lado D (sem fusao) fica como na v9: controle
D_CONTATO, MAX_ALISA = 0.15, 0.08                                # faixa de contato / deslocamento maximo do alisamento
NT_TAMPA_ = {"LOW": 140, "LOD1": 60, "LOD2": 24}               # tris por tampa (orcamento: LOD0 <= 20k)
Z_CORTE, Z_RAIZ0 = 3.95, 3.70     # corte ate 3,95; as pontas do U ficam em ~3,76-3,89
def na_caixa(p): return p.y > 2.0 and p.z < Z_CORTE and p.x > -0.7
def semente_cauda(p): return p.y > 4.1 or (p.z < 0.95 and abs(p.x) < 0.7 and p.y > 3.2)
def semente_pata(p): return p.x > 1.3 or (p.z < 0.95 and p.x > 0.7 and p.y < 3.0)
def dijkstra(vs, semente):
    d = {v: 0.0 for v in vs if semente(v.co)}; h = [(0.0, v.index, v) for v in d]; heapq.heapify(h)
    while h:
        dv, _, v = heapq.heappop(h)
        if dv > d.get(v, 9e9): continue
        for e in v.link_edges:
            u = e.other_vert(v)
            if u not in vs: continue
            nd = dv + e.calc_length()
            if nd < d.get(u, 9e9): d[u] = nd; heapq.heappush(h, (nd, u.index, u))
    return d
REL = {}
for L in ("LOW", "LOD1", "LOD2"):
    o = bpy.data.objects[L + "_Corpo"]; me = o.data; t0 = sum(len(p.vertices) - 2 for p in me.polygons)
    GN = {g.index: g.name for g in o.vertex_groups}; OSS_S = set(OSS)            # indice do grupo != indice do osso
    NT_TAMPA = NT_TAMPA_[L]
    bm = bmesh.new(); bm.from_mesh(me)
    CLS = bm.faces.layers.int.new("classe_cauda"); BOR0 = bm.edges.layers.int.new("borda_antes"); LADO = bm.faces.layers.int.new("lado_tampa")
    uv = bm.loops.layers.uv.active; dl = bm.verts.layers.deform.active   # (criar camadas realoca: antes de pegar elementos)
    W0 = {v: {GN[k]: w for k, w in v[dl].items() if w > 0 and GN[k] in OSS_S} for v in bm.verts}
    reg = {v for v in bm.verts if na_caixa(v.co)}; dT, dL = dijkstra(reg, semente_cauda), dijkstra(reg, semente_pata)
    G = {v: dT.get(v, 9.0) - dL.get(v, 9.0) for v in reg}                # < 0 cauda, > 0 pata
    def caixa_f(c): return c.x > -0.15 and 0.95 < c.z < Z_CORTE and c.y > 2.0
    CL = {}                                                             # classe da face: -1 cauda, +1 pata (soma de G)
    for f in bm.faces:
        if caixa_f(f.calc_center_median()) and all(v in G for v in f.verts): CL[f] = -1 if sum(G[v] for v in f.verts) < 0 else 1
    for _ in range(3):                                                  # ilhas pequenas (< 25 faces) viram a classe vizinha
        vis = set()
        for f in list(CL):
            if f in vis: continue
            pil, comp = [f], []
            while pil:
                g = pil.pop()
                if g in vis: continue
                vis.add(g); comp.append(g)
                for e in g.edges:
                    for h in e.link_faces:
                        if h in CL and CL[h] == CL[g] and h not in vis: pil.append(h)
            if len(comp) < 25:
                for g in comp: CL[g] = -CL[g]
    corte = [e for e in bm.edges if len(e.link_faces) == 2 and all(f in CL for f in e.link_faces) and CL[e.link_faces[0]] != CL[e.link_faces[1]]]
    viz_c = {e for c_ in corte for f in c_.link_faces for e in f.edges if e not in corte}
    L0 = sum(e.calc_length() for e in viz_c) / max(1, len(viz_c))      # aresta tipica da pele junto ao corte
    for f, c_ in CL.items(): f[CLS] = c_                                # camadas: sobrevivem as operacoes (dicts por BMFace nao)
    for e in bm.edges: e[BOR0] = 1 if e.is_boundary else 0
    n_corte = len(corte)
    bmesh.ops.split_edges(bm, edges=corte)                              # descola: nada retirado, nenhuma face nova
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    novos = set()
    def lado_face(f): return f[CLS]
    borda = [e for e in bm.edges if e.is_boundary and not e[BOR0] and e.link_faces and e.link_faces[0][CLS] != 0]   # bordas novas do corte
    orig = set(bm.faces); REL_L = {"arestas_cortadas": n_corte, "faces_cauda": sum(1 for x in CL.values() if x < 0), "faces_pata": sum(1 for x in CL.values() if x > 0)}
    FECHO = {}; PZ = []                                                 # par de pontas -> 2 arestas novas (via vertice no meio)
    for nome, sinal in (("cauda", -1), ("pata", 1)):
        es = [e for e in borda if lado_face(e.link_faces[0]) == sinal]
        grau = {}
        for e in es:
            for v in e.verts: grau[v] = grau.get(v, 0) + 1
        pontas = [v for v, g in grau.items() if g == 1]; fechos = []; n_pontas = len(pontas)
        comps_ = 0; vis_ = set()
        for v0 in grau:
            if v0 in vis_: continue
            comps_ += 1; pil = [v0]
            while pil:
                v = pil.pop()
                if v in vis_: continue
                vis_.add(v); pil += [e.other_vert(v) for e in v.link_edges if e in set(es)]
        while len(pontas) >= 2:                                         # fecha as pontas em pares (mais proximas), sempre por
            a_ = pontas.pop(0); b_ = min(pontas, key=lambda u: (u.co - a_.co).length); pontas.remove(b_)   # arestas proprias
            k = frozenset((a_.index, b_.index))
            if k not in FECHO:
                PZ.extend([a_.co.z, b_.co.z])
                m = bm.verts.new((a_.co + b_.co) / 2); m[dl].clear()
                for kk, ww in a_[dl].items(): m[dl][kk] = ww
                FECHO[k] = [bm.edges.new((a_, m)), bm.edges.new((m, b_))]
            fechos += FECHO[k]
        # poligono montado a mao (o holes_fill recusava o 2o lado no LOD1/LOD2): borda de ponta a ponta + vertice do meio,
        # com o sentido oposto ao da face vizinha na aresta compartilhada (orientacao coerente)
        ses = set(es); res = {"faces": []}
        if n_pontas == 2 and comps_ == 1:
            a_, b_ = [v for v, g in grau.items() if g == 1]; m = next(v for e in FECHO[frozenset((a_.index, b_.index))] for v in e.verts if v not in (a_, b_))
            cad = [a_]; usadas = set()
            while cad[-1] is not b_:
                e = next(e for e in cad[-1].link_edges if e in ses and e not in usadas); usadas.add(e); cad.append(e.other_vert(cad[-1]))
            vs = cad + [m]; e0 = next(iter(usadas)); f0 = e0.link_faces[0]
            l0 = next(l for l in f0.loops if l.edge is e0); dir_viz = (l0.vert, l0.link_loop_next.vert)
            i0 = vs.index(dir_viz[0]); i1 = vs.index(dir_viz[1])
            if (i0 + 1) % len(vs) == i1: vs.reverse()                     # a vizinha ja usa esse sentido: inverte
            nf = bm.faces.new(vs); res["faces"] = [nf]
        A = sum(f.calc_area() for f in res["faces"]); Lt = max(L0, math.sqrt(A / (0.433 * NT_TAMPA)))
        tr = bmesh.ops.triangulate(bm, faces=res["faces"], quad_method="BEAUTY", ngon_method="BEAUTY")
        for f in tr["faces"]: f[LADO] = sinal; f.material_index = 0; f.smooth = True
        for _ in range(12):                                             # subdivide as arestas mais longas ate ~NT_TAMPA tris
            tf_ = [f for f in bm.faces if f[LADO] == sinal]; ts = set(tf_)
            if len(tf_) >= NT_TAMPA: break
            longas = sorted({e for f in tf_ for e in f.edges if e.calc_length() > 1.3 * Lt and len(e.link_faces) == 2 and all(g in ts for g in e.link_faces)}, key=lambda e: -e.calc_length())
            longas = longas[:max(1, (NT_TAMPA - len(tf_)) // 3)]
            if not longas: break
            bmesh.ops.subdivide_edges(bm, edges=longas, cuts=1, use_grid_fill=False)
            bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if f[LADO] == sinal and len(f.verts) > 3])
            mine_ = [f for f in bm.faces if f[LADO] == sinal]
            bmesh.ops.beautify_fill(bm, faces=mine_, edges=list({e for f in mine_ for e in f.edges if len(e.link_faces) == 2 and all(g[LADO] == sinal for g in e.link_faces)}))
        mine = [f for f in bm.faces if f[LADO] == sinal]
        bmesh.ops.beautify_fill(bm, faces=mine, edges=list({e for f in mine for e in f.edges if len(e.link_faces) == 2 and all(g[LADO] == sinal for g in e.link_faces)}))
        REL_L[nome] = {"arestas_borda": len(es), "pontas": n_pontas, "cadeias": comps_, "fechos": len(fechos), "area_tampa": round(A, 4), "aresta_alvo": round(Lt, 4), "faces_tampa": sum(1 for f in bm.faces if f[LADO] == sinal)}
    tf = {f for f in bm.faces if f[LADO] != 0}
    # orientacao coerente: a partir da borda (pele original), cada face da tampa usa o sentido OPOSTO ao da vizinha na
    # aresta compartilhada (triangulos invertidos apareciam como facetas claras/escuras)
    def mesmo_sentido(f, g, e):
        lf = next(l for l in f.loops if l.edge is e); lg = next(l for l in g.loops if l.edge is e); return lf.vert is lg.vert
    bm.faces.index_update(); bm.faces.ensure_lookup_table()             # visitados por INDICE (o objeto Python da face
    tid = {f.index for f in tf}; feitos, fila, virou = set(), [], 0      # muda com normal_flip e o laco nao terminava)
    for fi in sorted(tid):
        f = bm.faces[fi]
        for e in list(f.edges):
            g = next((g for g in e.link_faces if g.index != fi and g.index not in tid), None)
            if g is not None and fi not in feitos:
                if mesmo_sentido(f, g, e): f.normal_flip(); virou += 1
                feitos.add(fi); fila.append(fi); break
    while fila:
        f = bm.faces[fila.pop()]
        for e in list(f.edges):
            for g in list(e.link_faces):
                gi = g.index
                if gi in tid and gi not in feitos and g[LADO] == f[LADO]:
                    if mesmo_sentido(f, g, e): g.normal_flip(); virou += 1
                    feitos.add(gi); fila.append(gi)
    tf = {bm.faces[i] for i in tid}
    REL_L["tampas_faces_reorientadas"] = virou
    fecho_v = {v for es_ in FECHO.values() for e in es_ for v in e.verts}
    vt = {v for f in tf for v in f.verts}; interior = [v for v in vt if all(g in tf for g in v.link_faces) and v not in fecho_v]
    for _ in range(40):
        nov = {v: sum((e.other_vert(v).co for e in v.link_edges), V()) / len(v.link_edges) for v in interior}
        for v, p in nov.items(): v.co = v.co * 0.4 + p * 0.6
    bm.normal_update()
    # componentes abaixo da raiz (por LOD: logo abaixo das pontas do corte; no LOD2 elas ficam mais baixas)
    Z_RAIZ = min(Z_RAIZ0, min(PZ) - 0.05); Z_TOTAL = Z_RAIZ - 0.45
    def flood(seed):
        vis = {seed}; pil = [seed]
        while pil:
            v = pil.pop()
            for e in v.link_edges:
                u = e.other_vert(v)
                if u not in vis and u.co.z < Z_RAIZ and u.co.y > 2.0: vis.add(u); pil.append(u)
        return vis
    ponta = min((v for v in bm.verts if v.co.y > 3.6 and abs(v.co.x) < 0.6 and v.link_faces), key=lambda v: v.co.z)
    pe_E = min((v for v in bm.verts if v.co.x > 0.9 and 1.5 < v.co.y < 2.8 and v.link_faces), key=lambda v: v.co.z)
    CT, CP_ = flood(ponta), flood(pe_E); inter = CT & CP_
    # forma das tampas: o preenchimento sai plano (a area de contato inteira, ~2,9 no LOD0) e virava uma "prancha" ao
    # mover. Cada tampa e reprojetada num cilindro em torno do EIXO REAL do seu lado (pata: ossos Coxa/Tibia/Metatarso_E,
    # centrados no membro; cauda: miolo do componente cauda medido por fatias, pois os ossos ficam no fundo do volume),
    # com o raio interpolado da borda da tampa (1/d^2), 0,96x (fica por dentro); alterna com relaxamento (borda fixa).
    def eixo_cauda():
        pts = []
        for k in range(int((Z_RAIZ - 0.5) / 0.25)):
            zz = 0.5 + 0.25 * k; vs_ = [v.co for v in CT - inter if abs(v.co.z - zz) < 0.12 and v not in vt]
            if len(vs_) > 8: pts.append(sum(vs_, V()) / len(vs_))
        return list(zip(pts, pts[1:]))
    EIXO = {-1: eixo_cauda(), 1: [(B[n + "_E"].head_local.copy(), B[n + "_E"].tail_local.copy()) for n in ("Coxa", "Tibia", "Metatarso")]}
    def no_eixo(p, segs):
        best = None
        for h, t in segs:
            ab = t - h; u = max(0.0, min(1.0, (p - h).dot(ab) / max(ab.length_squared, 1e-9))); q = h + ab * u
            if best is None or (p - q).length < (p - best).length: best = q
        return best
    # pele da faixa de CONTATO (escondida na v9; lascas pontudas do Meshy que ficavam expostas ao separar): alisada por
    # lado, so os vertices a menos de D_CONTATO da superficie do outro lado no repouso (4 passadas, vizinhos do mesmo lado,
    # no maximo MAX_ALISA de deslocamento: 8 passadas livres moviam ate 0,36 / 0,79 no LOD0 / LOD2)
    lado_v = {}
    for f in bm.faces:
        c_ = f[CLS] or f[LADO]
        if c_:
            for v in f.verts: lado_v.setdefault(v, set()).add(c_)
    REL_L["contato_alisado"] = {}
    for sinal in (-1, 1):
        outro_f = [f for f in bm.faces if (f[CLS] or f[LADO]) == -sinal]; bm.verts.ensure_lookup_table()
        bo = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in outro_f])
        cont = [v for v, ls in lado_v.items() if ls == {sinal} and v.co.z < Z_CORTE and bo.find_nearest(v.co)[3] < D_CONTATO and v not in fecho_v]
        cs = set(cont); mx = 0.0; p0 = {v: v.co.copy() for v in cont}
        for _ in range(4):
            nov = {}
            for v in cont:
                vz = [e.other_vert(v) for e in v.link_edges if lado_v.get(e.other_vert(v)) == {sinal}]
                if vz: nov[v] = sum((u.co for u in vz), V()) / len(vz)
            for v, p_ in nov.items():
                v.co = v.co * 0.5 + p_ * 0.5; d_ = v.co - p0[v]
                if d_.length > MAX_ALISA: v.co = p0[v] + d_.normalized() * MAX_ALISA   # sem mudar o volume
        mx = max(((v.co - p0[v]).length for v in cont), default=0.0)
        REL_L["contato_alisado"]["cauda" if sinal < 0 else "pata"] = {"vertices": len(cont), "maior_deslocamento": round(mx, 4)}
    bm.normal_update()
    REL_L["forma_tampa"] = {}
    for sinal in (-1, 1):
        segs = EIXO[sinal]
        if not segs: continue
        cap = [v for v in interior if any(f[LADO] == sinal for f in v.link_faces)]
        borda_t = [v for v in vt if v not in interior and any(f[LADO] == sinal for f in v.link_faces)]
        rb = [(v.co.copy(), (v.co - no_eixo(v.co, segs)).length) for v in borda_t]
        mov = 0.0
        for rodada in range(4):
            for v in cap:
                q = no_eixo(v.co, segs); d = v.co - q
                if d.length < 1e-4: continue
                ws = [(1.0 / max((v.co - pb).length, 0.02) ** 2, r) for pb, r in rb]; r = sum(w * r_ for w, r_ in ws) / sum(w for w, _ in ws)
                alvo = q + d.normalized() * r * 0.96; mov = max(mov, (alvo - v.co).length); v.co = alvo
            for _ in range(6):
                nov = {v: sum((e.other_vert(v).co for e in v.link_edges), V()) / len(v.link_edges) for v in cap}
                for v, p in nov.items(): v.co = v.co * 0.5 + p * 0.5
        REL_L["forma_tampa"]["cauda" if sinal < 0 else "pata"] = {"vertices": len(cap), "maior_deslocamento": round(mov, 4),
                                                                   "raio_borda_min_max": [round(min(r for _, r in rb), 3), round(max(r for _, r in rb), 3)]}
    bm.normal_update()
    for comp in (CT - inter, CP_ - inter):                              # UV das tampas: pele restante do mesmo componente
        ref = [f for f in bm.faces if f not in tf and all(v in comp for v in f.verts)]
        if not ref: continue
        bm.verts.ensure_lookup_table(); bvh = BVHTree.FromPolygons([v.co for v in bm.verts], [[v.index for v in f.verts] for f in ref])
        for f in tf:
            if not all(v in comp for v in f.verts): continue
            for l in f.loops:
                loc, nr, fi, d = bvh.find_nearest(l.vert.co); rf = ref[fi]; bc = poly_3d_calc([v.co for v in rf.verts], loc)
                l[uv].uv = sum((rl[uv].uv * b for rl, b in zip(rf.loops, bc)), V((0, 0)))
    W0 = {v: {GN[k]: w for k, w in v[dl].items() if w > 0 and GN[k] in OSS_S} for v in bm.verts}   # de novo: as operacoes trocam os BMVert
    for comp in (CT - inter, CP_ - inter):
        velhos = [v for v in comp if W0[v] and v not in vt]
        if not velhos: continue
        kd = KDTree(len(velhos))
        for i, v in enumerate(velhos): kd.insert(v.co, i)
        kd.balance()
        for v in comp:
            if not W0[v] or v in interior: W0[v] = dict(W0[velhos[kd.find(v.co)[1]]])
    def limpo(w, tirar):
        d = {k: x for k, x in w.items() if not k.startswith(tirar)}
        if not d: return None
        t = sum(d.values()); return {k: x / t for k, x in d.items()}
    aro = [v for v in vt if v not in interior]; kda = KDTree(len(aro))
    for i, v in enumerate(aro): kda.insert(v.co, i)
    kda.balance()
    regc = {v for v in (CT | CP_) - inter if v.co.x > -0.3}           # pata E inteira + metade E da cauda; os componentes
    for _ in range(3):                                                  # alcancam a pata D pelo perineo: ela fica de fora
        W2 = {}
        for v in regc:
            vz = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in regc and ((e.other_vert(v) in CT) == (v in CT))]
            if not vz: continue
            m = {}
            for u in vz:
                for k, x in W0[u].items(): m[k] = m.get(k, 0) + x / len(vz)
            W2[v] = {k: 0.5 * W0[v].get(k, 0) + 0.5 * m.get(k, 0) for k in set(W0[v]) | set(m)}
        W0.update(W2)
    W1 = dict(W0)
    for comp, tirar, lado_osso in ((CT - inter, PATA_E, "Cauda"), (CP_ - inter, ("Cauda",), PATA_T)):   # cauda perde SO a pata E
        for v in comp:
            f_ = suave((Z_RAIZ - v.co.z) / (Z_RAIZ - Z_TOTAL)); c = limpo(W0[v], tirar)
            if c is None:
                segs = [(n, B[n].head_local, B[n].tail_local) for n in OSS if n.startswith(lado_osso) and (lado_osso == "Cauda" or n.endswith("_E"))]
                c = {min(segs, key=lambda s: dseg(v.co, s[1], s[2]))[0]: 1.0}
            W1[v] = {k: (1 - f_) * W0[v].get(k, 0) + f_ * c.get(k, 0) for k in set(W0[v]) | set(c)}
    gidx = {g.name: g.index for g in o.vertex_groups}
    for v in bm.verts:
        if v not in regc and v not in vt and v not in novos and v[dl]: continue
        it = sorted(((k, x) for k, x in W1[v].items() if x > 1e-4), key=lambda kv: -kv[1])[:4]; t = sum(x for _, x in it)
        for k in list(v[dl].keys()): del v[dl][k]
        for k, x in it:
            if k not in gidx: gidx[k] = o.vertex_groups.new(name=k).index
            v[dl][gidx[k]] = x / t
    sem = sum(1 for v in bm.verts if not v[dl])
    outro = sum(1 for v in CT - inter if v.co.z < Z_TOTAL and any(k.startswith(PATA_E) and x > 1e-4 for k, x in W1[v].items())) + sum(1 for v in CP_ - inter if v.co.z < Z_TOTAL and any(k.startswith("Cauda") and x > 1e-4 for k, x in W1[v].items()))
    bm.to_mesh(me); bm.free(); me.update(); t1 = sum(len(p.vertices) - 2 for p in me.polygons)
    REL_L.update({"faces_tampa": len(tf), "tris_antes_depois": [t0, t1], "vertices_cauda": len(CT), "vertices_pata": len(CP_),
                  "vertices_nos_dois_componentes": len(inter), "vertices_sem_peso": sem, "pesos_do_outro_lado_abaixo_de_z_total": outro,
                  "aresta_media_corte": round(L0, 4), "z_raiz_z_total": [round(Z_RAIZ, 3), round(Z_TOTAL, 3)], "pontas_corte_z": [round(z, 3) for z in PZ]})
    REL[L] = REL_L; print("V10", L, json.dumps(REL_L), flush=True)
    assert t1 <= 19999, (L, t1)
def ilhas(me):
    pai = list(range(len(me.vertices)))
    def r(i):
        while pai[i] != i: pai[i] = pai[pai[i]]; i = pai[i]
        return i
    for e in me.edges:
        x_, y_ = r(e.vertices[0]), r(e.vertices[1])
        if x_ != y_: pai[x_] = y_
    g = {}
    for i in range(len(me.vertices)): g.setdefault(r(i), []).append(i)
    return list(g.values())
for L in ("LOW", "LOD1"):
    c = bpy.data.objects[L + "_Corpo"]; f_ = bpy.data.objects[L + "_Pelagem"]; cm = c.data; gn = {g.index: g.name for g in c.vertex_groups}
    pos = [v.co.copy() for v in cm.vertices]; fac = [list(p.vertices) for p in cm.polygons]; bvh = BVHTree.FromPolygons(pos, fac)
    WC = [{gn[e.group]: e.weight for e in v.groups if gn[e.group] in OSS} for v in cm.vertices]
    fm = f_.data; n_rep = 0
    for il in ilhas(fm):
        raiz = min(il, key=lambda i: bvh.find_nearest(fm.vertices[i].co)[3]); p = fm.vertices[raiz].co
        if not (p.y > 2.0 and p.z < Z_RAIZ0 + 0.3 and p.x > -0.05): continue
        loc, nr, fi, d = bvh.find_nearest(p); bc = poly_3d_calc([pos[i] for i in fac[fi]], loc); w = {}
        for i, b in zip(fac[fi], bc):
            for k, x in WC[i].items(): w[k] = w.get(k, 0) + x * b
        it = sorted(w.items(), key=lambda kv: -kv[1])[:4]; t = sum(x for _, x in it)
        for g in f_.vertex_groups: g.remove(il)
        for k, x in it:
            g = f_.vertex_groups.get(k) or f_.vertex_groups.new(name=k); g.add(il, x / t, "REPLACE")
        n_rep += 1
    REL[L + "_pelagem"] = {"cartoes_repesados": n_rep}; print("V10 pelagem", L, REL[L + "_pelagem"], flush=True)
RJ = json.load(open(os.path.join(SRC, "rig_v9.json"))); RJ["v10_cauda"] = REL
json.dump(RJ, open(os.path.join(OUT, "rig_v10.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Rig.blend")); print("V10_OK", flush=True)
