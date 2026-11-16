"""v8: corrige na ORIGEM (LOD0) a dobra dos cantos da boca da v7 (low_v7/ preservada). Depois: lod_rosto_v7.py sobre a saida.
Causa (diag_canto_v8.py em review/v8_final/antes_v7): na comissura, o grupo Mandibula da v5 (BFS em duas frentes) poe
vertices de peso 1,0 / 0,5 / 0,0 a 0,005-0,017 stud uns dos outros. Toda a abertura do canto cai numa faixa de tecido
quase sem largura: arestas de 0,005 viram 0,2 (razao ~38x) e dezenas de faces viram (dobram) no maximo.
Correcao (pesos e lascas, so na zona da comissura):
- zona: vertices a menos de R_ZONA do canto K (media da pele com peso 0,2-0,8 junto a linha da boca), mesmo componente
  da pele (dentes/lingua sao pecas soltas e nao entram);
- fixos (condicao de contorno): tudo fora da zona; as bordas funcionais do corte dos labios (vertices de pele que tocam
  a faixa "labio") a mais de R_LIVRE de K: o labio de cima continua 0 e o de baixo 1;
- livres: o resto da zona recebe o peso HARMONICO (media dos vizinhos ponderada por 1/comprimento da aresta, iterada):
  vertices quase coincidentes ficam com pesos quase iguais e a transicao 0 -> 1 se espalha pela faixa de pele/mucosa
  que existe em volta do canto (bochecha e comissura), sem salto comprimido;
- mistura suave com o peso original por mascara: a frente do canto so vale na faixa da linha da boca (BANDA abaixo, BANDA_CIMA acima) (o corpo
  da mandibula continua ~1 e o focinho de cima ~0); atras do canto vale toda a bochecha; some antes da borda da zona.
Topologia: so funde as lascas (< L_LASCA) de pele na zona do canto. Nao muda o resto das posicoes, UV, labios cortados, olhos, nariz nem corpo. Remove o Protecao_LOD antigo (lod_rosto_v7
recria a partir dos pesos novos).
Uso: blender -b low_v7/CR_LoboArtico_LOW.blend -P canto_v8.py -- <saida_dir>"""
import bpy, bmesh, sys, os, json, math, shutil
from mathutils import Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True)
SRC = os.path.dirname(bpy.data.filepath); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json")))
BA, BB = PIV["mandibula"]["linha_boca"]; CANTO = PIV["mandibula"]["canto_y"]
R_ZONA, R_LIVRE, BANDA, BANDA_CIMA, ITER = 0.32, 0.08, 0.16, 0.09, 4000
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
for im in bpy.data.images:                                              # texturas: copias proprias da v8
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.exists(fp) and os.path.dirname(fp) != OUT:
        dst = os.path.join(OUT, os.path.basename(fp)); shutil.copy(fp, dst); im.filepath = dst; im.reload()
cab = bpy.data.objects["LOW_Cabeca"]
g = cab.vertex_groups.get("Protecao_LOD")
if g: cab.vertex_groups.remove(g)
GM = cab.vertex_groups["Mandibula"].index
bm = bmesh.new(); bm.from_mesh(cab.data); uv = bm.loops.layers.uv.active; dl = bm.verts.layers.deform.active; bm.verts.ensure_lookup_table()
def e_pele(f): return f.loops[0][uv].uv.x < 0.90
def e_labio(f): u = f.loops[0][uv].uv; return 0.955 < u.x < 0.965 and 0.02 <= u.y < 0.08
# topologia local: lascas da comissura (arestas < L_LASCA so de pele, longe da juncao com a faixa do labio) sao fundidas;
# elas empilham faces quase degeneradas que viram ao abrir (o 'acordeao' do canto)
L_LASCA = 0.006
def cantos_k(bm):
    w0 = {v.index: v[dl].get(GM, 0.0) for v in bm.verts}; ks = {}
    for lado, s in (("E", 1), ("D", -1)):
        vs = [v for v in bm.verts if v.co.x * s > 0.1 and v.co.y < CANTO + 0.3 and abs(v.co.z - (BA + BB * v.co.y)) < 0.15
              and 0.2 < w0[v.index] < 0.8 and v.link_faces and all(e_pele(f) for f in v.link_faces)]
        ks[lado] = sum((v.co for v in vs), V()) / len(vs)
    return ks
KS = cantos_k(bm); n_lasca = 0
for _ in range(4):
    las = [e for e in bm.edges if e.calc_length() < L_LASCA and e.link_faces and all(e_pele(f) for f in e.link_faces)
           and not any(e_labio(f) for v in e.verts for f in v.link_faces) and not any(v.is_boundary for v in e.verts)
           and min((e.verts[0].co - k).length for k in KS.values()) < 0.25]
    usados, sel = set(), []
    for e in las:
        if e.verts[0] in usados or e.verts[1] in usados: continue
        usados.update(e.verts); sel.append(e)
    if not sel: break
    bmesh.ops.collapse(bm, edges=sel, uvs=True); n_lasca += len(sel)
bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=[e for e in bm.edges if min((e.verts[0].co - k).length for k in KS.values()) < 0.3])
bm.verts.ensure_lookup_table(); bm.faces.ensure_lookup_table(); print("V8 lascas fundidas", n_lasca, flush=True)
W = {v.index: v[dl].get(GM, 0.0) for v in bm.verts}
# componente da pele (o que toca a costura); pecas soltas ficam de fora
CP, CN = V(PIV["costura"]["ponto"]), V(PIV["costura"]["normal"])
sem = [v for v in bm.verts if v.is_boundary and abs((v.co - CP).dot(CN)) < 0.03]; comp = set(v.index for v in sem); pilha = list(sem)
while pilha:
    v = pilha.pop()
    for e in v.link_edges:
        u = e.other_vert(v)
        if u.index not in comp: comp.add(u.index); pilha.append(u)
REL = {}
for lado, s in (("E", 1), ("D", -1)):
    vs = [v for v in bm.verts if v.co.x * s > 0.1 and v.co.y < CANTO + 0.3 and abs(v.co.z - (BA + BB * v.co.y)) < 0.15
          and 0.2 < W[v.index] < 0.8 and v.link_faces and all(e_pele(f) for f in v.link_faces)]
    K = sum((v.co for v in vs), V()) / len(vs)
    zona = [v for v in bm.verts if v.index in comp and (v.co - K).length < R_ZONA]
    borda_labio = {v.index for v in zona if any(e_labio(f) for f in v.link_faces) and any(e_pele(f) for f in v.link_faces)}
    livres = [v for v in zona if not (v.index in borda_labio and (v.co - K).length >= R_LIVRE)]   # labios funcionais fixos
    viz = {v.index: [(e.other_vert(v).index, 1.0 / max(e.calc_length(), 1e-4)) for e in v.link_edges] for v in livres}
    antes = {v.index: W[v.index] for v in livres}; H = dict(W)
    for it in range(ITER):                                              # Gauss-Seidel do peso harmonico
        dmax = 0.0
        for v in livres:
            num = sum(H[j] * k for j, k in viz[v.index]); den = sum(k for _, k in viz[v.index]); n = num / den
            dmax = max(dmax, abs(n - H[v.index])); H[v.index] = n
        if dmax < 1e-6: break
    def mascara(v):                                                     # 1 = peso harmonico, 0 = peso original (suave)
        dz = v.co.z - (BA + BB * v.co.y); tras = suave((v.co.y - (K.y - 0.10)) / 0.10)
        larg = BANDA if dz < 0 else BANDA_CIMA                           # acima da linha a faixa e estreita: labio de cima estavel
        faixa = tras + (1 - tras) * suave(1 - abs(dz) / larg)            # a frente do canto: so a faixa da comissura
        return faixa * suave((R_ZONA - (v.co - K).length) / 0.10)       # e some antes da borda da zona
    for v in livres: W[v.index] = antes[v.index] + mascara(v) * (H[v.index] - antes[v.index])
    mud = [abs(W[i] - antes[i]) for i in antes]
    REL[lado] = {"canto_K": [round(x, 4) for x in K], "vertices_zona": len(zona), "livres": len(livres), "bordas_labio_fixas": len(zona) - len(livres),
                 "iteracoes": it + 1, "mudanca_media": round(sum(mud) / len(mud), 4), "mudanca_max": round(max(mud), 4)}
    print("V8 canto", lado, REL[lado], flush=True)
for v in bm.verts:
    w = W[v.index]
    if w > 1e-4: v[dl][GM] = min(1.0, w)
    elif GM in v[dl]: del v[dl][GM]
bm.to_mesh(cab.data); bm.free(); cab.data.update()
PIV["canto_v8"] = dict(REL, R_ZONA=R_ZONA, R_LIVRE=R_LIVRE, BANDA=BANDA, BANDA_CIMA=BANDA_CIMA, lascas_fundidas=n_lasca, L_LASCA=L_LASCA, nota="peso Mandibula harmonico (1/comprimento) na zona da comissura; labios funcionais fixos fora de R_LIVRE")
json.dump(PIV, open(os.path.join(OUT, "rig_pivos.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_LOW.blend")); print("V8_OK", flush=True)
