"""Correcao de CONTATO COM O CHAO dos clipes do Sombrio (cauda e cabeca atravessando o chao), sem mexer no gerador
compartilhado. O Sombrio tem cauda e cabeca mais grossas que as do Glacial (mesmos clipes do gerador): nos clipes de
atencao, rugido, descanso e sentado a malha da cauda chegava a -3,5 studs e, no sono, a cabeca inteira ficava abaixo do
chao (osso head a -2,2 studs; pecas da cabeca a -5,9).
v2 (03/11): a v1 levantava a cauda inteira a partir do contato (gancho para cima). Agora:
- CAUDA "deita no chao": osso a osso da base para a ponta, cada segmento vai para a altura ORIGINAL ou para o chao, o que
  for maior (o que estava no alto continua no alto; o que entrava no chao passa a apoiar nele). Medida rapida pelos ossos:
  altura do segmento menos o raio inferior da malha daquele osso (medido no repouso).
- CABECA (v3): a base do pescoco (spine_2) ergue a cabeca inteira e o osso head volta a atitude original, ate a malha da cabeca e das pecas presas nela tocar o chao (limite 40 graus).
A correcao e amostrada, interpolada, suavizada e, nos lacos, fechada (fim = inicio). So ossos de cauda e pescoco mudam.
Uso: blender -b rig_com_clipes.blend -P corrigir_contato_sombrio.py -- <saida.blend> <Clipe:cauda|cabeca|ambos,...> [passo]"""
import bpy, sys, math
from mathutils import Quaternion, Vector
from mathutils.geometry import intersect_point_line
a = sys.argv[sys.argv.index("--") + 1:]; SAIDA = a[0]; ITENS = [x.split(":") for x in a[1].split(",")]; PASSO = int(a[2]) if len(a) > 2 else 3
FOLGA = 0.004                                  # unidades do rig (~0,07 stud)
sc = bpy.context.scene; A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
gi = {g.index: g.name for g in M.vertex_groups}
DONO = [gi[max(v.groups, key=lambda g: g.weight).group] if v.groups else "" for v in M.data.vertices]
CAUDA = ["tail_1", "tail_2", "tail_3", "tail_4", "tail_5", "tail_6", "tail_tip"]
PESCO = ["spine_2", "head"]                     # v3: base do pescoco + compensacao da cabeca
IDX_CAB = [i for i, d in enumerate(DONO) if d.startswith(("head", "mouth", "horn"))]
# raio INFERIOR da malha de cada osso da cauda (repouso): quanto a malha desce abaixo do segmento do osso
A.animation_data.action = None
for pb in A.pose.bones: pb.matrix_basis.identity()
bpy.context.view_layer.update()
RAIO = {}
for n in CAUDA:
    bn = A.data.bones[n]; h, t = A.matrix_world @ bn.head_local, A.matrix_world @ bn.tail_local; r = 0.0
    for i, d in enumerate(DONO):
        if d != n: continue
        p = M.matrix_world @ M.data.vertices[i].co; q, fr = intersect_point_line(p, h, t); fr = max(0.0, min(1.0, fr))
        r = max(r, (h.lerp(t, fr)).z - p.z)
    RAIO[n] = r
def z_seg(n):
    """altura mais baixa da malha do segmento n (aproximada pelo osso)"""
    pb = A.pose.bones[n]; h, t = A.matrix_world @ pb.head, A.matrix_world @ pb.tail
    return min(h.z, t.z) - RAIO[n]
def girar(n, graus):
    pb = A.pose.bones[n]; pb.rotation_quaternion = pb.rotation_quaternion @ Quaternion((1, 0, 0), math.radians(graus)); bpy.context.view_layer.update()
SINAL = {}
def sinal(n, filho):
    """+1 se girar n em +X sobe o segmento filho"""
    if n in SINAL: return SINAL[n]
    z0 = z_seg(filho); girar(n, 3); z1 = z_seg(filho); girar(n, -3)
    SINAL[n] = 1.0 if z1 > z0 else -1.0; return SINAL[n]
def malha_min(idxs):
    dg = bpy.context.evaluated_depsgraph_get(); me = M.evaluated_get(dg).to_mesh(); mw = M.matrix_world
    z = min((mw @ me.vertices[i].co).z for i in idxs); M.evaluated_get(dg).to_mesh_clear(); return z
def corrigir_cauda(zorig):
    ang = {}
    for k in range(len(CAUDA) - 1):
        pai, filho = CAUDA[k], CAUDA[k + 1]; alvo = max(zorig[filho], -FOLGA * 0.5)
        if abs(z_seg(filho) - alvo) < 0.0015: continue
        s = sinal(pai, filho); lo, hi = -35.0, 35.0; base = A.pose.bones[pai].rotation_quaternion.copy()
        def zcom(g):
            A.pose.bones[pai].rotation_quaternion = base @ Quaternion((1, 0, 0), math.radians(g * s)); bpy.context.view_layer.update(); return z_seg(filho)
        for _ in range(16):                          # bissecao: o z do filho cresce com g
            mid = (lo + hi) / 2
            if zcom(mid) < alvo: lo = mid
            else: hi = mid
        zcom(hi); ang[pai] = hi * s                  # filho volta a altura original ou apoia no chao
    return ang
def corrigir_cabeca():
    """v3: ergue a cabeca INTEIRA (giro da base do pescoco, spine_2) e devolve a atitude original da cabeca (giro
    contrario no osso head): inclinar so o focinho enterrava o leque de espinhos de tras do cranio"""
    ang = {}
    hb = A.pose.bones["head"]
    def dir_cab(): return ((A.matrix_world @ hb.tail) - (A.matrix_world @ hb.head)).normalized()
    alvo_dir = dir_cab()
    if "spine_2" not in SINAL:
        z0 = (A.matrix_world @ hb.head).z; girar("spine_2", 3); z1 = (A.matrix_world @ hb.head).z; girar("spine_2", -3)
        SINAL["spine_2"] = 1.0 if z1 > z0 else -1.0
    for _ in range(30):
        z = malha_min(IDX_CAB)
        if z >= -FOLGA or abs(ang.get("spine_2", 0)) >= 40: break
        passo = min(4.0, max(0.6, -z * 250)) * SINAL["spine_2"]
        girar("spine_2", passo); ang["spine_2"] = ang.get("spine_2", 0) + passo
        for _ in range(12):                              # head volta a apontar para onde apontava
            d0 = dir_cab().angle(alvo_dir)
            if d0 < math.radians(0.5): break
            girar("head", 1.0); d1 = dir_cab().angle(alvo_dir)
            if d1 < d0: ang["head"] = ang.get("head", 0) + 1.0; continue
            girar("head", -2.0); d2 = dir_cab().angle(alvo_dir)
            if d2 < d0: ang["head"] = ang.get("head", 0) - 1.0; continue
            girar("head", 1.0); break
    return ang
log = []
for nome, modo in ITENS:
    act = bpy.data.actions["Silverwing_" + nome]; A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range); loop = act.get("loop", True) is not False
    ossos = CAUDA + PESCO; orig = {}
    for f in range(f0, f1 + 1):
        sc.frame_set(f); orig[f] = {n: A.pose.bones[n].matrix_basis.to_quaternion() for n in ossos}
    amostras = list(range(f0, f1 + 1, PASSO))
    if amostras[-1] != f1: amostras.append(f1)
    corr = {}
    for f in amostras:
        sc.frame_set(f)
        for n in ossos: A.pose.bones[n].rotation_mode = "QUATERNION"; A.pose.bones[n].rotation_quaternion = orig[f][n]
        bpy.context.view_layer.update()
        c = {}
        if modo in ("cabeca", "ambos"): c.update(corrigir_cabeca())
        if modo in ("cauda", "ambos"):
            zorig = {n: z_seg(n) for n in CAUDA}; c.update(corrigir_cauda(zorig))
        corr[f] = c
    if loop: corr[f1] = dict(corr[f0])
    def ang_em(f, n):
        for x, y in zip(amostras, amostras[1:]):
            if x <= f <= y:
                t = (f - x) / max(1, y - x); return corr[x].get(n, 0) * (1 - t) + corr[y].get(n, 0) * t
        return corr[amostras[-1]].get(n, 0)
    final = {}
    for n in ossos:
        bruto = [ang_em(f, n) for f in range(f0, f1 + 1)]; R = PASSO
        final[n] = [sum(bruto[max(0, i - R):i + R + 1]) / len(bruto[max(0, i - R):i + R + 1]) for i in range(len(bruto))]
        if loop: final[n][-1] = final[n][0]
    mexidos = [n for n in ossos if any(abs(x) > 0.05 for x in final[n])]
    for f in range(f0, f1 + 1):
        for n in mexidos:
            pb = A.pose.bones[n]; pb.rotation_mode = "QUATERNION"
            pb.rotation_quaternion = orig[f][n] @ Quaternion((1, 0, 0), math.radians(final[n][f - f0]))
            pb.keyframe_insert("rotation_quaternion", frame=f, group=n)
    mx = {n: round(max(final[n], key=abs), 1) for n in mexidos}
    log.append((nome, mx)); print("CORRIGIDO", nome, modo, "graus (pico) por osso", mx)
A.animation_data.action = None
for x in bpy.data.actions: x.use_fake_user = True
bpy.ops.wm.save_as_mainfile(filepath=SAIDA); print("CONTATO_OK", len(log))
