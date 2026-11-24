"""v46b: REIMPORTACAO dos clipes de curva pela rota do Studio (JSON da ponte -> acoes), para auditar o que o jogo recebe.
Le studio/json_v46b/LoboArtico_<acao>.json (quaternions/translacoes arredondados a 5 casas = o que vira KeyframeSequence),
reconstroi cada acao com os valores do JSON e salva numa COPIA (<dir>/CR_LoboArtico_Anim.blend + curvas_v46b.json); depois
compara com a acao original (maior diferenca de rotacao por osso e de posicao da ponta dos dedos).
Uso: blender -b anim_v46b/CR_LoboArtico_Anim.blend -P reimportar_json_v46b.py -- anim_v46b_reimport"""
import bpy, sys, os, json, shutil, math
from mathutils import Quaternion, Vector as V
OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); os.makedirs(OUT, exist_ok=True); SRC = os.path.dirname(bpy.data.filepath)
for f in os.listdir(SRC):
    if f.endswith((".png", ".json")): shutil.copy(os.path.join(SRC, f), os.path.join(OUT, f))
for im in bpy.data.images:
    fp = bpy.path.abspath(im.filepath)
    if fp and os.path.dirname(fp) == SRC: im.filepath = os.path.join(OUT, os.path.basename(fp))
JD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "studio", os.environ.get("JSON_DIR_V46", "json_v46b"))
ARM = bpy.data.objects["LoboArtico_Rig"]; P = ARM.pose.bones; sc = bpy.context.scene
DED = ("Dedos_E", "Dedos_D", "DedosPe_E", "DedosPe_D")
def usar(ac):
    ARM.animation_data.action = ac
    if len(ac.slots): ARM.animation_data.action_slot = ac.slots[0]
for pb in P: pb.rotation_mode = "QUATERNION"
REL = {}
for arq in sorted(os.listdir(JD)):
    if not arq.startswith("LoboArtico_"): continue
    d = json.load(open(os.path.join(JD, arq))); nome = d["nome"][len("LoboArtico_"):]; n = d["quadros"]
    orig = bpy.data.actions[nome]; usar(orig); ref = []
    for q in range(n):
        sc.frame_set(q); ref.append(({pb.name: pb.matrix.to_quaternion() for pb in P}, {k: (ARM.matrix_world @ P[k].tail).copy() for k in DED}))
    orig.name = nome + "_orig"; ac = bpy.data.actions.new(nome); ac.use_fake_user = True; usar(ac)
    for q in range(n):
        for pb in P:
            c = d["ossos"][pb.name][q * 7:(q + 1) * 7]
            pb.rotation_quaternion = Quaternion((c[3], c[0], c[1], c[2])); pb.location = V((c[4], c[5], c[6]))
            pb.keyframe_insert("rotation_quaternion", frame=q, group=pb.name)
            if pb.name == "Quadril": pb.keyframe_insert("location", frame=q, group=pb.name)
    ac.frame_range = (0, n - 1); dr, dp = 0.0, 0.0
    for q in range(n):
        sc.frame_set(q)
        for pb in P: dr = max(dr, math.degrees(pb.matrix.to_quaternion().rotation_difference(ref[q][0][pb.name]).angle))
        for k in DED: dp = max(dp, ((ARM.matrix_world @ P[k].tail) - ref[q][1][k]).length)
    REL[nome] = {"quadros": n, "laco": d["loop"], "rot_max_graus": round(dr, 5), "ponta_dedos_max": round(dp, 6)}
    print("REIMP", nome, n, "rot", round(dr, 5), "dedos", round(dp, 6), flush=True)
ARM.animation_data.action = bpy.data.actions["Repouso"]
json.dump(REL, open(os.path.join(OUT, "reimport_v46b.json"), "w"), indent=1)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "CR_LoboArtico_Anim.blend")); print("REIMP_V46B_OK", flush=True)
