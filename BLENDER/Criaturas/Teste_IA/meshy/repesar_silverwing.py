"""Recalcula os pesos FINAIS do zero no descanso atual (pose do molde, asas abertas), depois do repose feito com pesos
suaves. Usa exatamente o mesmo bloco de pesos do montar_silverwing.py (bind + regioes geodesicas + raiz da asa), lido
do proprio arquivo para nao haver duas versoes. Uso: blender -b arq.blend -P repesar_silverwing.py"""
import bpy, sys, os, json, math, re
from mathutils import Vector, Matrix
from collections import Counter
sys.path.insert(0, r"C:\Users\Rhenan\.claude\skills\blender-character-rigging\scripts")
import bind_mesh
A = bpy.data.objects["Silverwing_Rig"]; M = bpy.data.objects["Silverwing"]
_a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
if _a:                                             # troca a malha pela refeita na pose nova (mesmas coordenadas do rig)
    bpy.data.objects.remove(M)
    _antes = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=_a[0])
    M = [o for o in bpy.data.objects if o not in _antes and o.type == "MESH"][0]; M.name = "Silverwing"; M.data.name = "Silverwing"
    for o in [o for o in bpy.data.objects if o not in _antes and o is not M]: bpy.data.objects.remove(o)
    print("MALHA_TROCADA", len(M.data.vertices), "verts")
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "montar_silverwing.py"), encoding="utf8").read()
ini = src.index("# 3b) asas:"); fim = src.index('print("PESOS_ASA vertices"')
bloco = src[ini:fim]
for o in bpy.data.objects: o.select_set(False)
M.vertex_groups.clear()
for m in [m for m in M.modifiers if m.type == "ARMATURE"]: M.modifiers.remove(m)
rel = bind_mesh.run(armature=A.name, meshes=[M.name], method="auto", limit=4, clean=0.01)
print("PESOS_NOVOS", json.dumps(rel))
g = {"bpy": bpy, "A": A, "M": M, "Vector": Vector, "Matrix": Matrix, "Counter": Counter, "math": math, "os": os}
exec(bloco, g)
gi = {x.index: x.name for x in M.vertex_groups}
print("REGIOES", Counter(g["REGV"]).most_common())
mx = max(len([x for x in v.groups if x.weight > 1e-4]) for v in M.data.vertices)
print("MAX_INFLUENCIAS", mx, "sem_peso", sum(1 for v in M.data.vertices if not len(v.groups)))
if not any(m.type == "ARMATURE" for m in M.modifiers):
    mo = M.modifiers.new("Armature", "ARMATURE"); mo.object = A
bpy.ops.wm.save_mainfile()
print("REPESAR_OK")
