"""Auditoria de clipes do Dragao Glacial (certificacao 02/11). Para cada acao "Silverwing_*" do rig:
- patinacao: pe em contato (dedo z < CONTATO) que se move no plano alem da velocidade esperada do chao
  (clipes parados = 0; Andar/Correr = velocidade da esteira V_ESTEIRA em +Y);
- pe abaixo do chao (z minimo dos ossos de dedo) e malha abaixo do chao (z minimo da malha avaliada, amostrada);
- garupa no Sentado: altura do quadril e menor z da malha na regiao do quadril;
- mandibula: angulo maximo de abertura (mouth_lower) por clipe;
- descontinuidade no laco: diferenca entre o 1o e o ultimo quadro (clipes em laco).
Uso: blender -b rig/GL_Dragao_M2M.blend -P auditar_clipes.py -- saida.json [passo_malha]"""
import bpy, sys, json, math
from mathutils import Vector
a = sys.argv[sys.argv.index("--") + 1:]; saida = a[0]; PASSO = int(a[1]) if len(a) > 1 else 4
FONTES = {"Silverwing_Idle", "Silverwing_Walk", "Silverwing_Fly_Flap", "Silverwing_Fly_Glide", "Silverwing_Rest_Pose"}
CONTATO = 0.03
V_ESTEIRA = {"Silverwing_Andar": 0.26 / (0.64 * 0.9), "Silverwing_Correr": None}   # unidades do rig por segundo
sc = bpy.context.scene; FPS = sc.render.fps
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
for m in M.modifiers: m.show_viewport = True
DEDOS = ["front_toes_l", "front_toes_r", "back_toes_l", "back_toes_r"]
PONTAS = ["front_toes_tip_l", "front_toes_tip_r", "back_toes_tip_l", "back_toes_tip_r"]
gi = {g.name: g.index for g in M.vertex_groups}
QUADRIL = set()
for v in M.data.vertices:
    for g in v.groups:
        if g.weight > 0.5 and g.group in (gi.get("hips"), gi.get("tail_1"), gi.get("spine_0")): QUADRIL.add(v.index)
def pos(n): return (A.matrix_world @ A.pose.bones[n].head).copy()
def ang_mand():
    pb = A.pose.bones["mouth_lower"]; q = pb.matrix_basis.to_quaternion()
    return math.degrees(2 * math.acos(min(1, abs(q.w))))
res = {}
acoes = sorted((x for x in bpy.data.actions if x.name.startswith("Silverwing_") and x.name not in FONTES and not x.name.endswith("_Rest")), key=lambda x: x.name)
for act in acoes:
    A.animation_data.action = act; A.animation_data.action_slot = act.slots[0]
    f0, f1 = map(int, act.frame_range)
    traj = {d: [] for d in PONTAS}; zmin_osso = 9; zmin_malha = 9; mand = 0; quad_z = []; quad_malha = 9
    for f in range(f0, f1 + 1):
        sc.frame_set(f)
        for d in PONTAS: traj[d].append(pos(d))
        zmin_osso = min(zmin_osso, min(pos(d).z for d in DEDOS))
        mand = max(mand, ang_mand())
        quad_z.append(pos("hips").z)
        if (f - f0) % PASSO == 0 or f == f1:
            dg = bpy.context.evaluated_depsgraph_get(); ev = M.evaluated_get(dg); me = ev.to_mesh()
            mw = M.matrix_world
            zs = [(mw @ v.co).z for v in me.vertices]
            zmin_malha = min(zmin_malha, min(zs))
            if QUADRIL: quad_malha = min(quad_malha, min(zs[i] for i in QUADRIL))
            ev.to_mesh_clear()
    # patinacao: em cada trecho de contato, deslocamento horizontal descontada a esteira
    v = V_ESTEIRA.get(act.name, 0.0)
    if act.name == "Silverwing_Correr": v = None
    pat = {}
    for d, tr in traj.items():
        pior = 0.0; ini = None
        for i, p in enumerate(tr):
            if p.z < CONTATO:
                if ini is None: ini = i
                if v is not None:
                    esp = tr[ini] + Vector((0, v * (i - ini) / FPS, 0))
                    pior = max(pior, (Vector((p.x, p.y, 0)) - Vector((esp.x, esp.y, 0))).length)
            else: ini = None
        # correr: velocidade do pe no apoio deve ser constante (desvio da media)
        if v is None:
            vs = [(tr[i + 1] - tr[i]).y * FPS for i in range(len(tr) - 1) if tr[i].z < CONTATO and tr[i + 1].z < CONTATO]
            if vs:
                med = sum(vs) / len(vs); pior = max(abs(x - med) for x in vs) / FPS
        pat[d] = round(pior * 17.5, 3)                         # studs
    laco = None
    if act.get("loop", True):
        sc.frame_set(f0); a0 = {b.name: b.matrix_basis.copy() for b in A.pose.bones}
        sc.frame_set(f1); laco = max((a0[b.name].translation - b.matrix_basis.translation).length * 17.5 +
                                   a0[b.name].to_quaternion().rotation_difference(b.matrix_basis.to_quaternion()).angle * 0 for b in A.pose.bones)
        rot_max = max(math.degrees(a0[b.name].to_quaternion().rotation_difference(b.matrix_basis.to_quaternion()).angle) for b in A.pose.bones)
        laco = (round(laco, 3), round(rot_max, 2))
    res[act.name] = dict(quadros=f1 - f0 + 1, loop=bool(act.get("loop", True)), patina_studs=pat,
                         dedo_zmin_studs=round(zmin_osso * 17.5, 3), malha_zmin_studs=round(zmin_malha * 17.5, 3),
                         mandibula_max_graus=round(mand, 1), quadril_z_min_studs=round(min(quad_z) * 17.5, 3),
                         quadril_malha_zmin_studs=round(quad_malha * 17.5, 3), laco_desvio=laco)
    print("AUD", act.name, json.dumps(res[act.name]))
json.dump(res, open(saida, "w", encoding="utf-8"), indent=1)
print("AUD_OK", len(res))
