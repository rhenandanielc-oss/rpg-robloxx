"""copia o atributo qa_juba (mesma malha, mesma ordem de vertices) de um .blend para o arquivo aberto e salva em outro caminho"""
import bpy, sys, numpy as np
A = sys.argv[sys.argv.index("--") + 1:]
ob = [o for o in bpy.data.objects if o.name.startswith("Leao_Solar_E4")][0]
with bpy.data.libraries.load(A[0]) as (src, dst): dst.meshes = list(src.meshes)
m2 = [m for m in dst.meshes if "qa_juba" in m.attributes][0]; v = np.zeros(len(m2.vertices), np.float32); m2.attributes["qa_juba"].data.foreach_get("value", v)
assert len(v) == len(ob.data.vertices)
a = ob.data.attributes.new("qa_juba", "FLOAT", "POINT"); a.data.foreach_set("value", v)
bpy.ops.wm.save_as_mainfile(filepath=A[1], copy=True); print("QA_OK")
