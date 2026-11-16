"""v34: PATAS CONVERGINDO para a linha do meio em movimento (auditoria contra lobos reais: o lobo trota com "uma pata diretamente a
frente da outra" - Mech & Boitani - quase em linha unica; o nosso pisava com a bitola do repouso, 2,12 stud nas dianteiras e 2,48 nas
traseiras). Limite da malha (pernas grossas): cada pata entra no maximo ~0,25 stud antes de as pernas se tocarem (diag_pernas_v27).
Pos-processo sobre a anim_v33, nas 4 patas: o PE inteiro (metacarpo/metatarso + dedos, mesma orientacao) desloca para dentro um valor
D constante em cada APOIO (deslize inalterado por construcao) e muda so no ar (min-jerk entre o D do apoio anterior e o do proximo);
o braco/coxa e refeito com IK de 2 ossos com a dobra no plano frente-tras (como a v31/v33). D = C(membro) x peso da marcha no TOQUE do
apoio: Trote 1, Corrida 'peso_corrida', Andar 0,5; transicoes pela mistura gravada (s_por_quadro); Arrancada/Frenagem pela razao
v/v_corrida (abaixo de 'v_min' = 0, para terminar/comecar no Repouso); Repouso e viradas 0.
Uso: blender -b anim_v33/CR_LoboArtico_Anim.blend -P convergir_v34.py -- <dir_saida>"""
import bpy, sys, os, json, math, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Matrix, Vector as V
import marcha_v21 as M
import marchas_v29 as MV
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1:][0]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
PAR = {"C": {"D": 0.22, "T": 0.20}, "peso": {"Andar": 0.5, "Trote": 1.0, "Corrida": 0.8}, "v_min": 0.25}
if os.environ.get("AJUSTE_V34"): PAR.update(json.loads(os.environ["AJUSTE_V34"]))
ARM = M.ARM; P = M.P; sc = bpy.context.scene
CJ = json.load(open(os.path.join(SRC, "clipes_v21.json"))); G = MV.marchas(CJ)
TJ = {}
for fn in ("marchas_v29.json", "transicoes_v25.json", "viradas_v27.json"):
    for k, v in json.load(open(os.path.join(SRC, fn)))["acoes"].items(): TJ[k] = v
VCOR = json.load(open(os.path.join(SRC, "transicoes_v25.json")))["v_corrida"]
CADEIA = {"DE": ("Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E"), "DD": ("Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D"),
          "TE": ("Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"), "TD": ("Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D")}
def apoio(ac, k, q):
    if ac == "Repouso": return True
    return bool(TJ[ac]["apoio_por_quadro"][k][q]) if ac in TJ else bool(MV.apoio(G, {"acoes": {}}, ac, k, q))
def peso(ac, q):
    if ac in PAR["peso"]: return PAR["peso"][ac]
    if ac in TJ and "origem" in TJ[ac]:
        A = TJ[ac]; s = A["s_por_quadro"][q]; return PAR["peso"][A["origem"]] + (PAR["peso"][A["destino"]] - PAR["peso"][A["origem"]]) * s
    if ac in ("Arrancada", "Frenagem"):
        r = TJ[ac]["v_por_quadro"][q] / VCOR; return 0.0 if r < PAR["v_min"] else PAR["peso"]["Corrida"] * min(1.0, (r - PAR["v_min"]) / (1 - PAR["v_min"])) ** 0.5
    return 0.0
def mj(u): u = max(0.0, min(1.0, u)); return u * u * u * (10 - 15 * u + 6 * u * u)
def deslocamentos(ac, k, n, laco):
    ap = [apoio(ac, k, q) for q in range(n + 1)]; C = PAR["C"][k[0]]
    L = n if laco else n + 1                                          # laco: quadro n = quadro 0
    segs = []; q = 0
    while q < L:
        if ap[q]:
            j = q
            while j + 1 < L and ap[j + 1]: j += 1
            segs.append([q, j]); q = j + 1
        else: q += 1
    if laco and len(segs) > 1 and segs[0][0] == 0 and segs[-1][1] == L - 1:   # apoio que cruza a emenda do laco
        segs[0][0] = segs[-1][0] - L; segs.pop()
    def toque(sg):
        t = sg[0] % L if laco else max(0, sg[0])
        if not laco and sg[0] == 0: t = 0
        return C * peso(ac, t)
    D = [None] * (n + 1)
    for sg in segs:
        dv = toque(sg)
        for q in range(sg[0], sg[1] + 1): D[q % L if laco else q] = dv
    for q in range(L):
        if D[q] is not None: continue
        if not segs: D[q] = C * peso(ac, q); continue
        if laco:
            prev = max((sg for sg in segs if sg[1] % L < q or sg[1] < q), key=lambda sg: sg[1] if sg[1] < q else sg[1] - L, default=None)
            prv = [sg for sg in segs if (sg[1] - q) % L > 0]; a = min(segs, key=lambda sg: (q - sg[1]) % L); b = min(segs, key=lambda sg: (sg[0] - q) % L)
            ta = (q - a[1]) % L; tb = (b[0] - q) % L; u = ta / max(1e-9, ta + tb); D[q] = toque(a) + (toque(b) - toque(a)) * mj(u)
        else:
            a = max((sg for sg in segs if sg[1] < q), key=lambda sg: sg[1], default=None); b = min((sg for sg in segs if sg[0] > q), key=lambda sg: sg[0], default=None)
            if a is None and b is None: D[q] = C * peso(ac, q)
            elif a is None: D[q] = C * peso(ac, 0) + (toque(b) - C * peso(ac, 0)) * mj(q / max(1, b[0]))
            elif b is None: D[q] = toque(a) + (C * peso(ac, n) - toque(a)) * mj((q - a[1]) / max(1, n - a[1]))
            else: D[q] = toque(a) + (toque(b) - toque(a)) * mj((q - a[1]) / max(1, b[0] - a[1]))
    if laco: D[n] = D[0]
    return D, ap
def ik_reto(k, T):
    sup, inf = CADEIA[k][:2]; bs, bi = M.B[sup], M.B[inf]; a_, b_ = bs.length, bi.length
    S = P[sup].head.copy(); Mpai = P[sup].parent.matrix @ M.B[sup].parent.matrix_local.inverted()
    dv = T - S; d = min(dv.length, (a_ + b_) * 0.9995); dn = dv.normalized()
    al = (a_ * a_ - b_ * b_ + d * d) / (2 * d); h = math.sqrt(max(a_ * a_ - al * al, 0.0))
    perp = V((1.0, 0.0, 0.0)).cross(dn).normalized()
    if perp.dot(P[inf].head - S) < 0: perp = -perp
    K = S + dn * al + perp * h
    for nome, h0, t0 in ((sup, S, K), (inf, K, S + dn * d)):
        yv = (t0 - h0).normalized(); xr = Mpai.to_3x3() @ M.REST[nome].col[0].to_3d(); xv = (xr - yv * xr.dot(yv)).normalized()
        Mx = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); Mx.translation = h0; P[nome].matrix = Mx; bpy.context.view_layer.update()
    return (S + dn * d - T).length
OSSOS = [n for c in CADEIA.values() for n in c]; REL = {"parametros": PAR, "acoes": {}}
for pb in P: pb.rotation_mode = "QUATERNION"
for acn in [a for a in bpy.data.actions if not a.name.startswith("Teste")]:
    ac = acn.name; ARM.animation_data.action = acn
    if len(acn.slots): ARM.animation_data.action_slot = acn.slots[0]
    f0, f1 = (int(x) for x in acn.frame_range); n = f1 - f0; laco = ac in ("Andar", "Trote", "Corrida")
    DS = {k: deslocamentos(ac, k, n, laco) for k in CADEIA}
    if max(max(abs(x) for x in DS[k][0]) for k in CADEIA) < 1e-7:
        REL["acoes"][ac] = {"D_max": 0.0}; print("V34", ac, "sem mudanca", flush=True); continue
    NOVOS = []; err = 0.0
    for q in range(n + 1):
        ARM.animation_data.action = acn; sc.frame_set(f0 + q); bpy.context.view_layer.update()
        orig = {nm: P[nm].rotation_quaternion.copy() for nm in OSSOS}; base = {nm: P[nm].matrix.copy() for nm in OSSOS}; ARM.animation_data.action = None
        for nm in OSSOS: P[nm].matrix = base[nm]
        bpy.context.view_layer.update(); r = {}
        for k, (sup, inf, met, ded) in CADEIA.items():
            dlt = DS[k][0][q]; sg = 1.0 if k[1] == "E" else -1.0
            if abs(dlt) > 1e-7:
                W = base[inf].to_translation() + base[inf].col[1].xyz * M.B[inf].length + V((-sg * dlt, 0, 0))
                err = max(err, ik_reto(k, W))
                om = base[met].copy(); om.translation = P[inf].tail; P[met].matrix = om; bpy.context.view_layer.update()
                od = base[ded].copy(); od.translation = P[met].tail; P[ded].matrix = od; bpy.context.view_layer.update()
            for nm in (sup, inf, met, ded):
                qn = P[nm].rotation_quaternion.copy()
                if qn.dot(orig[nm]) < 0: qn = -qn
                r[nm] = qn
        NOVOS.append(r)
    cb = acn.layers[0].strips[0].channelbag(acn.slots[0])
    for nm in OSSOS:
        for i in range(4):
            fc = cb.fcurves.find('pose.bones["%s"].rotation_quaternion' % nm, index=i)
            kp = {int(round(p.co.x)): p for p in fc.keyframe_points}
            for qi, q in enumerate(range(f0, f1 + 1)):
                if q in kp: p = kp[q]; p.co.y = NOVOS[qi][nm][i]; p.handle_left_type = "AUTO_CLAMPED"; p.handle_right_type = "AUTO_CLAMPED"
            fc.update()
    ARM.animation_data.action = None
    for pb in P: pb.matrix_basis.identity()
    REL["acoes"][ac] = {"D_max": {k: round(max(DS[k][0]), 4) for k in CADEIA}, "D_pontas": {k: [round(DS[k][0][0], 4), round(DS[k][0][-1], 4)] for k in CADEIA},
                        "erro_ik_max": round(err, 7), "D_por_quadro": {k: [round(x, 4) for x in DS[k][0]] for k in CADEIA}}
    print("V34", ac, REL["acoes"][ac]["D_max"], "pontas", REL["acoes"][ac]["D_pontas"], "ik", REL["acoes"][ac]["erro_ik_max"], flush=True)
ARM.animation_data.action = bpy.data.actions["Andar"]
json.dump(REL, open(os.path.join(OUT, "convergir_v34.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("CONVERGIR_V34_OK", flush=True)
