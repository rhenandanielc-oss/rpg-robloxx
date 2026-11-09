"""Reimporta o GLB do Lobo Ancestral numa cena vazia e valida: malha/tris/UV/imagens, esqueleto (nomes e quantidade),
pesos (vertices sem peso, no maximo 4 influencias), cada acao (quadros, duracao) e a pose mundial de ossos-chave em
quadros escolhidos contra a referencia gravada na exportacao (tolerancia 0,01 stud). Saida: validacao_glb.json.
Uso: blender -b --factory-startup -P validar_glb_rig.py -- <export_dir>"""
import bpy, sys, os, json
from mathutils import Vector as V
D = os.path.abspath(sys.argv[sys.argv.index("--") + 1]); REF = json.load(open(os.path.join(D, "referencia_export.json")))
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; sc.render.fps = 30
bpy.ops.import_scene.gltf(filepath=os.path.join(D, "Lobo_Ancestral.glb"))
arm = next(o for o in sc.objects if o.type == "ARMATURE"); ms = [o for o in sc.objects if o.type == "MESH"]
r = {"malhas": [], "ossos": [b.name for b in arm.data.bones], "acoes": {}, "pose": {}, "problemas": []}
for o in ms:
    me = o.data; sem = sum(1 for v in me.vertices if not v.groups); mais4 = sum(1 for v in me.vertices if len(v.groups) > 4)
    r["malhas"].append({"nome": o.name, "tris": sum(len(p.vertices) - 2 for p in me.polygons), "uv": len(me.uv_layers),
                        "materiais": [m.name for m in me.materials], "grupos": len(o.vertex_groups), "verts_sem_peso": sem, "verts_mais_4": mais4})
    if sem: r["problemas"].append("%s: %d vertices sem peso" % (o.name, sem))
r["imagens"] = [(i.name, list(i.size)) for i in bpy.data.images]
for a in bpy.data.actions:
    f0, f1 = a.frame_range; r["acoes"][a.name] = {"quadros": int(round(f1 - f0)) + 1, "duracao_s": round((f1 - f0) / 30, 3)}
faltam = [n for n in REF["acoes"] if not any(n in k for k in r["acoes"])]
if faltam: r["problemas"].append("acoes ausentes: %s" % faltam)
if not arm.animation_data: arm.animation_data_create()
for nome, ossos in REF["ref"].items():
    act = next((a for k, a in bpy.data.actions.items() if k.startswith(nome)), None)
    if act is None: continue
    arm.animation_data.action = act
    try: arm.animation_data.action_slot = act.slots[0]
    except Exception: pass
    q = {"Lobo_Andar": 10, "Lobo_Corrida": 5, "Lobo_Uivo": 60, "Lobo_Deitado": 0, "Lobo_Mordida": 14}[nome]
    sc.frame_set(int(act.frame_range[0]) + q)
    err = {}
    for b, p in ossos.items():
        if b not in arm.pose.bones: err[b] = "ausente"; continue
        err[b] = round(((arm.matrix_world @ arm.pose.bones[b].head) - V(p)).length, 4)
    r["pose"][nome] = err
    if any(isinstance(e, str) or e > 0.01 for e in err.values()): r["problemas"].append("pose divergente em %s: %s" % (nome, err))
json.dump(r, open(os.path.join(D, "validacao_glb.json"), "w"), indent=1, ensure_ascii=False)
print("VALIDACAO malhas", r["malhas"]); print("VALIDACAO ossos", len(r["ossos"]), "acoes", len(r["acoes"]), "imagens", r["imagens"])
print("VALIDACAO pose", r["pose"]); print("VALIDACAO problemas", r["problemas"] or "nenhum")
