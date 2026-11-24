"""(v44 = copia da v27 para as viradas CURTAS: VirarCurtoEsquerda/Direita e viradas_curtas_v44.json.)
(v27 = copia da v26 lendo viradas_v27.json / export_clipes_v27.json; resto igual.)
v26: auditoria MUNDIAL das viradas, com ROTACAO: posicao mundial = BASE (rumo/posicao acumulados das acoes anteriores) @
T(t) @ Rz(psi(t)) @ posicao deformada local (T e psi por quadro de viradas_v27.json). Usar so o deslocamento retilineo dos lotes
anteriores daria resultado errado.
Sequencias (sem quadros duplicados; o ultimo quadro de cada virada = Repouso q0 = 1o da proxima):
- ida_volta_E: Repouso q230..239 | VirarEsquerda q0..q(n-1) | VirarDireita q0..q(n-1) | Repouso q0..q10
- ida_volta_D: Repouso q230..239 | VirarDireita | VirarEsquerda | Repouso q0..q10
Apoio por quadro: Repouso = 4 patas; viradas = cronograma do gerador; uma fase atravessa as emendas. Pontos FIXOS: vertices da
pata que tocam o chao (<= 0,03 do mais baixo) no MEIO do apoio, contados enquanto < 0,06 do chao do meio; deslize = maior
deslocamento HORIZONTAL MUNDIAL em relacao ao meio (captura pata que pivota contra o chao: pontos longe do centro da pata andam);
afundamento/flutuacao = altura minima da pata na fase - minima no repouso. Emendas: pose (duplicados) e 2a diferenca mundial.
Rumo: psi e T nas emendas (continuidade) e rumo final de cada sequencia.
Modo GLB: --glb <dir_export> <dir_blend_fonte> (importa a 30 qps numa cena limpa e roda pelo esqueleto importado).
Uso: blender -b <anim.blend> -P auditar_viradas_v26.py -- <saida_json> [LOW,LOD1,LOD2] [--glb <dir> <fonte>]"""
import bpy, sys, os, json, math
from mathutils import Vector as V, Matrix
a = sys.argv[sys.argv.index("--") + 1:]; OUT = os.path.abspath(a[0]); NIV = a[1].split(",") if len(a) > 1 and not a[1].startswith("--") else ["LOW", "LOD1", "LOD2"]
GLB = a[a.index("--glb") + 1] if "--glb" in a else None; SRC = os.path.abspath(a[a.index("--glb") + 2]) if GLB else os.path.dirname(bpy.data.filepath)
VJ = json.load(open(os.path.join(SRC, "viradas_curtas_v44.json"))); PIV = json.load(open(os.path.join(SRC, "rig_pivos.json"))); FPS = 30
N = {k: v["quadros"] for k, v in VJ["acoes"].items()}
def Mt(acao, q):
    if acao == "Repouso": return Matrix.Identity(4)
    A = VJ["acoes"][acao]; ps = math.radians(A["psi_graus_por_quadro"][q]); T = A["T_por_quadro"][q]
    return Matrix.Translation(V((T[0], T[1], 0))) @ Matrix.Rotation(ps, 4, "Z")
SEQ = {"ida_volta_E": ["VirarCurtoEsquerda", "VirarCurtoDireita"], "ida_volta_D": ["VirarCurtoDireita", "VirarCurtoEsquerda"]}
def linha(ordem):
    LT = [("Repouso", q, Matrix.Identity(4)) for q in range(230, 240)]; base = Matrix.Identity(4)
    for ac_ in ordem:
        for q in range(N[ac_]): LT.append((ac_, q, base @ Mt(ac_, q)))
        base = base @ Mt(ac_, N[ac_])
    LT += [("Repouso", q, base) for q in range(0, 11)]; return LT, base
def apoio(acao, k, q): return True if acao == "Repouso" else VJ["acoes"][acao]["apoio_por_quadro"][k][q]
R = {"metodo": __doc__.split("Uso:")[0], "unidade": "stud", "tolerancia_deslize": 0.03, "sequencias": {}, "niveis": {}}
for nm, ordem in SEQ.items():
    LT, base = linha(ordem); f = base.to_3x3() @ V((0, -1, 0))
    R["sequencias"][nm] = {"linha": ["%s q%d" % (e[0], e[1]) for e in LT], "rumo_final_graus": round(math.degrees(math.atan2(f.x, -f.y)), 4), "posicao_final": [round(x, 4) for x in base.translation]}
for L in NIV:
    if GLB:
        bpy.ops.wm.read_factory_settings(use_empty=True); bpy.context.scene.render.fps = FPS
        ops = bpy.ops.import_scene.gltf.get_rna_type().properties.keys(); EXP = json.load(open(os.path.join(GLB, "export_clipes_v27.json")))
        bpy.ops.import_scene.gltf(filepath=os.path.join(GLB, EXP["lods"][L]["arquivo"]), **({"bone_heuristic": "BLENDER"} if "bone_heuristic" in ops else {}))
        A = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"][0]
        if A.animation_data is None: A.animation_data_create()
        ACS = {n: next(x for x in bpy.data.actions if x.name == n or x.name.startswith(n)) for n in ("Repouso", "VirarCurtoEsquerda", "VirarCurtoDireita")}
    else:
        A = bpy.data.objects["LoboArtico_Rig"]; ACS = {n: bpy.data.actions[n] for n in ("Repouso", "VirarCurtoEsquerda", "VirarCurtoDireita")}
    sc = bpy.context.scene; C = bpy.data.objects[L + "_Corpo"]; Mw = C.matrix_world.copy(); P0 = [Mw @ v.co for v in C.data.vertices]
    patas = {k: [i for i, p in enumerate(P0) if p.z < 0.5 and math.hypot(p.x - xy[0], p.y - xy[1]) < 0.8] for k, xy in zip(("DE", "DD", "TE", "TD"), PIV["pose_neutra"]["patas_xy_depois"])}
    zr = {k: min(P0[i].z for i in ids) for k, ids in patas.items()}; cache = {}
    def pose(acao, q):
        if (acao, q) not in cache:
            acn = ACS[acao]; A.animation_data.action = acn
            if len(acn.slots): A.animation_data.action_slot = acn.slots[0]
            sc.frame_set(int(round(acn.frame_range[0])) + q); dg = bpy.context.evaluated_depsgraph_get(); e = C.evaluated_get(dg); m = e.to_mesh()
            cache[(acao, q)] = [Mw @ v.co for v in m.vertices]; e.to_mesh_clear()
        return cache[(acao, q)]
    RL = R["niveis"][L] = {}
    for nm, ordem in SEQ.items():
        LT, _ = linha(ordem); PW = [[e[2] @ p for p in pose(e[0], e[1])] for e in LT]; RS = RL[nm] = {"apoios": {}, "emendas": {}, "duplicados": {}}
        for k, ids in patas.items():
            segs, cur = [], []
            for i, e in enumerate(LT):
                if apoio(e[0], k, e[1]): cur.append(i)
                elif cur: segs.append(cur); cur = []
            if cur: segs.append(cur)
            fs = []
            for sg in segs:
                im = sg[len(sg) // 2]; zm = min(PW[im][i].z for i in ids); pts = [i for i in ids if PW[im][i].z < zm + 0.03]; ref = {i: PW[im][i] for i in pts}; mx = 0.0; qp = None
                for j in sg:
                    for i in pts:
                        p_ = PW[j][i]
                        if p_.z < zm + 0.06:
                            d = (p_ - ref[i]).to_2d().length
                            if d > mx: mx, qp = d, j
                alt = min(min(PW[j][i].z for i in ids) - zr[k] for j in sg)
                fs.append({"inicio": "%s q%d" % LT[sg[0]][:2], "fim": "%s q%d" % LT[sg[-1]][:2], "quadros": len(sg), "acoes": sorted({LT[j][0] for j in sg}),
                           "deslize": round(mx, 5), "quadro_pior": "%s q%d" % LT[qp][:2] if qp is not None else None, "afundamento": round(-min(alt, 0.0), 4), "flutuacao": round(max(alt, 0.0), 4), "pontos": len(pts)})
            RS["apoios"][k] = fs
            pv = [f for f in fs if any(x.startswith("Virar") for x in f["acoes"])]; pf = max(pv, key=lambda f: f["deslize"])
            print("VIR", L, nm, k, "fases", len(pv), "pior", pf["deslize"], pf["inicio"], "->", pf["fim"], "afund", max(f["afundamento"] for f in pv), "flut", max(f["flutuacao"] for f in pv), flush=True)
        amo = list(range(0, len(P0), 7))
        def ac2(j): return max(((PW[j + 1][i] - PW[j][i]) - (PW[j][i] - PW[j - 1][i])).length for i in amo)
        for j in range(1, len(LT) - 1):
            if LT[j][0] != LT[j - 1][0]:
                viz = [ac2(i) for i in range(max(1, j - 12), min(len(LT) - 1, j + 12)) if i not in (j - 1, j)]
                RS["emendas"]["%s->%s" % (LT[j - 1][0], LT[j][0])] = {"aceleracao_na_emenda": round(max(ac2(j - 1), ac2(j)), 5), "aceleracao_max_vizinha": round(max(viz), 5)}
        for ac_ in ordem:
            RS["duplicados"]["Repouso q0 x %s q0" % ac_] = round(max((p - q_).length for p, q_ in zip(pose("Repouso", 0), pose(ac_, 0))), 6)
            RS["duplicados"]["%s fim x Repouso q0" % ac_] = round(max((p - q_).length for p, q_ in zip(pose(ac_, N[ac_]), pose("Repouso", 0))), 6)
        print("VIR", L, nm, "emendas", json.dumps(RS["emendas"]), "duplicados", json.dumps(RS["duplicados"]), flush=True)
json.dump(R, open(OUT, "w"), indent=1); print("AUD_VIRADAS_V27_OK", flush=True)
