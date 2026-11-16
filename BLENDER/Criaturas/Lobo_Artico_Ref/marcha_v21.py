"""Funcoes comuns dos clipes de marcha do lote 2 (Trote, Corrida), iguais as do lote 1 (clipes_v12.py: IK analitico de 2
ossos gravado em FK, rolamento em torno do contato dos dedos, altura do balanco que so zera no toque, gravacao SEM acao
atribuida), generalizadas para qualquer cronograma de marcha: G = {T, D, apoio, fases, alturas, rolamento, dobras}.
Importado por clipes_v21.py e alcance_v21.py (nao roda sozinho)."""
import bpy, math
from mathutils import Vector as V, Matrix, Quaternion
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones; B = ARM.data.bones; FPS = 30
X, Y, Z = V((1, 0, 0)), V((0, 1, 0)), V((0, 0, 1))
REST = {b.name: b.matrix_local.copy() for b in B}
PATAS = {"DE": ("Umero_E", "Antebraco_E", "Metacarpo_E", "Dedos_E"), "DD": ("Umero_D", "Antebraco_D", "Metacarpo_D", "Dedos_D"),
         "TE": ("Coxa_E", "Tibia_E", "Metatarso_E", "DedosPe_E"), "TD": ("Coxa_D", "Tibia_D", "Metatarso_D", "DedosPe_D")}
MCP0 = {k: B[c[2]].tail_local.copy() for k, c in PATAS.items()}; CAR0 = {k: B[c[2]].head_local.copy() for k, c in PATAS.items()}
TIP0 = {k: B[c[3]].tail_local.copy() for k, c in PATAS.items()}
def suave(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)
def onda(t, T, f=0.0): return math.sin(2 * math.pi * (t / T + f))
def q_global(n, R): Bm = REST[n].to_3x3(); return (Bm.inverted() @ R @ Bm).to_quaternion()
def ik(k, mcp, phi, phi_dedo):
    sup, inf, pe, dedo = PATAS[k]; bs, bi = B[sup], B[inf]; a, b = bs.length, bi.length
    Rp = Matrix.Rotation(phi, 3, X); T = mcp + Rp @ (CAR0[k] - MCP0[k])
    S = P[sup].head.copy(); Mpai = P[sup].parent.matrix @ B[sup].parent.matrix_local.inverted()
    K0, S0 = bs.tail_local, bs.head_local; d0 = (bi.tail_local - S0).normalized()
    dob = Mpai.to_3x3() @ ((K0 - S0) - d0 * (K0 - S0).dot(d0))
    dv = T - S; d = min(dv.length, (a + b) * 0.9995); dn = dv.normalized()
    al = (a * a - b * b + d * d) / (2 * d); h = math.sqrt(max(a * a - al * al, 0.0)); perp = (dob - dn * dob.dot(dn)).normalized(); K = S + dn * al + perp * h
    for nome, h0, t0 in ((sup, S, K), (inf, K, S + dn * d)):
        yv = (t0 - h0).normalized(); xr = Mpai.to_3x3() @ REST[nome].col[0].to_3d(); xv = (xr - yv * xr.dot(yv)).normalized()
        M = Matrix((xv, yv, xv.cross(yv))).transposed().to_4x4(); M.translation = h0; P[nome].matrix = M; bpy.context.view_layer.update()
    M = (Rp.to_4x4() @ Matrix.Translation(-MCP0[k]) @ REST[pe]); M.translation = P[inf].tail.copy(); P[pe].matrix = M; bpy.context.view_layer.update()
    M = Matrix.Rotation(phi_dedo, 4, X) @ Matrix.Translation(-MCP0[k]) @ REST[dedo]; M.translation = P[pe].tail.copy(); P[dedo].matrix = M
    bpy.context.view_layer.update()
    return (S + dn * d - T).length, d / (a + b)                          # erro do IK (alcance), extensao relativa da perna
def altura_balanco(h, w): return h * math.sin(math.pi * w ** 0.8) ** 1.15
def alvo_pata(k, dy, dz, rolo, dobra):
    mcp = MCP0[k] + V((0, dy, dz)); tv = TIP0[k] - MCP0[k]; C = mcp + 0.7 * tv
    m_ef = C + Matrix.Rotation(rolo, 3, X) @ (mcp - C); nd = (mcp + tv) - m_ef
    phi_dedo_rolo = math.atan2(nd.z, nd.y) - math.atan2(tv.z, tv.y)
    return m_ef, rolo + dobra, phi_dedo_rolo + 0.45 * dobra
def pata_marcha(G, k, t):
    """pata k no tempo t numa marcha G: apoio recua a v = D/T em relacao ao corpo a partir do toque y0 (centro do apoio em
    G['centro'][k]); balanco min-jerk do ponto de saida ao proximo toque, altura que so zera no toque, dobra do carpo/jarrete"""
    T, beta = G["T"], G["apoio"]; S = G["D"] * beta; u = ((t / T) - G["fases"][k]) % 1.0; c = G["centro"][k]
    h = G["altura"][k[0]]; roll = math.radians(G["rolamento_graus"]); dob = math.radians(G["dobra_graus"][k[0]])
    if u < beta:
        s = u / beta; dy = c - S / 2 + S * s; dz = 0.0; rolo = roll * suave((s - G.get("rolo_ini", 0.72)) / (1 - G.get("rolo_ini", 0.72))); dobra = 0.0
    else:
        w = (u - beta) / (1 - beta); m = w * w * w * (10 - 15 * w + 6 * w * w)
        dy = c + S / 2 - S * m; dz = altura_balanco(h, w)
        rolo = roll * (1 - suave((w - 0.2) / 0.4)); dobra = dob * math.sin(math.pi * w) ** 1.5 * (1 - suave((w - 0.7) / 0.3))
    return dy, dz, rolo, dobra
def aplicar_corpo(R, q):
    for pb in P: pb.matrix_basis.identity()
    for n, lst in R.items():
        M = Matrix.Identity(3)
        for e, g in lst: M = Matrix.Rotation(math.radians(g), 3, e) @ M
        P[n].rotation_quaternion = q_global(n, M)
    P["Quadril"].location = REST["Quadril"].to_3x3().inverted() @ q
    bpy.context.view_layer.update()
ERR_PATA = {}
def aplicar_patas(pes):
    err, ext = 0.0, {}; ERR_PATA.clear()
    for k in PATAS:
        m_ef, phi, phd = alvo_pata(k, *pes[k]); e, x = ik(k, m_ef, phi, phd); err = max(err, e); ext[k] = x; ERR_PATA[k] = e
    for k, c in PATAS.items():
        for n in c: P[n].location = (0, 0, 0)
    return err, ext
def gravar(nome, n_quadros, fn):
    """calcula SEM acao atribuida (a acao ativa sobrescreve a pose a cada update do IK) e grava quaternions em todos os quadros"""
    if ARM.animation_data: ARM.animation_data.action = None
    for pb in P: pb.rotation_mode = "QUATERNION"
    VAL, ERR, EXT = [], 0.0, {}
    for qi in range(n_quadros + 1):
        e, ext = fn(qi / FPS); ERR = max(ERR, e)
        for k, x in ext.items(): EXT[k] = max(EXT.get(k, 0.0), x)
        VAL.append({pb.name: (pb.rotation_quaternion.copy(), pb.location.copy()) for pb in P})
    for a_ in [a_ for a_ in bpy.data.actions if a_.name == nome]: bpy.data.actions.remove(a_)
    ac = bpy.data.actions.new(nome); ARM.animation_data_create(); ARM.animation_data.action = ac
    for qi, vals in enumerate(VAL):
        for pb in P:
            pb.rotation_quaternion, pb.location = vals[pb.name]
            pb.keyframe_insert("rotation_quaternion", frame=qi, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=qi, group=pb.name)
    ac.use_fake_user = True; ac.frame_range = (0, n_quadros)
    for pb in P: pb.matrix_basis.identity()
    return ac, ERR, EXT
