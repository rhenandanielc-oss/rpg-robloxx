"""Transfere acoes aprovadas do Javali Silvestre para o Javali-do-Brejo SEM alterar as curvas (mesmo esqueleto e nomes de osso).
Anexa de uma copia em fonte/, renomeia Javali_X -> JavaliBrejo_X (propriedades da acao preservadas) e liga o slot ao rig.
Confere: mesmos data_paths e mesmas chaves (o valor de cada curva e comparado quadro a quadro com a acao de origem).
Uso: blender -b CR_JavaliBrejo_v4.blend -P scripts/transferir_clipes.py -- <fonte.blend> <Clipe1,Clipe2,...> <saida.blend>"""
import bpy, sys, os, json
A = sys.argv[sys.argv.index("--") + 1:]; FONTE, LISTA, SAIDA = os.path.abspath(A[0]), A[1].split(","), os.path.abspath(A[2])
arm = bpy.data.objects["JavaliBrejo_Rig"]
def curvas(a):
    cs = []
    for l in a.layers:
        for st in l.strips:
            for cb in st.channelbags: cs += list(cb.fcurves)
    return cs
with bpy.data.libraries.load(FONTE, link=False) as (src, dst):
    dst.actions = ["Javali_" + n for n in LISTA]
REL = {}
for n, act in zip(LISTA, dst.actions):
    novo = "JavaliBrejo_" + n
    if novo in bpy.data.actions: bpy.data.actions.remove(bpy.data.actions[novo])
    act.name = novo; act.use_fake_user = True
    arm.animation_data.action = act
    if arm.animation_data.action_slot is None and len(act.slots): arm.animation_data.action_slot = act.slots[0]
    cs = curvas(act)
    REL[novo] = {"faixa": list(act.frame_range), "curvas": len(cs), "chaves": sum(len(c.keyframe_points) for c in cs),
                 "slot": arm.animation_data.action_slot.identifier if arm.animation_data.action_slot else None,
                 "props": sorted(k for k in act.keys() if not k.startswith("_"))}
arm.animation_data.action = bpy.data.actions["JavaliBrejo_Andar"]
bpy.ops.wm.save_as_mainfile(filepath=SAIDA, relative_remap=True)
print("TRANSFERIDO", json.dumps(REL, ensure_ascii=False))
