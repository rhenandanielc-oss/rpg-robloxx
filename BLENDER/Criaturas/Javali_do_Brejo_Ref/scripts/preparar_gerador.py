"""Prepara o .blend de entrada do GERADOR da base (scripts/gerador_base/, copia sem alteracao de Javali_Silvestre_Ref/rig/clipes_javali*.py)
com a malha do Javali-do-Brejo: abre fonte/CR_Javali_Rig_r4.blend (nomes Javali_* que o gerador espera) e troca so as
POSICOES dos vertices de corpo e cabeca pelas da variante (mesma topologia). Pesos, ossos e rig ficam os da base r4.
Uso: blender -b fonte/CR_Javali_Rig_r4.blend -P scripts/preparar_gerador.py -- CR_JavaliBrejo_v4.blend gerador/CR_JavaliBrejo_gerador.blend"""
import bpy, sys, os
import numpy as np
A = sys.argv[sys.argv.index("--") + 1:]; VAR, SAIDA = os.path.abspath(A[0]), os.path.abspath(A[1])
with bpy.data.libraries.load(VAR, link=False) as (src, dst):
    dst.meshes = ["JavaliBrejo_Corpo", "JavaliBrejo_Cabeca"]
for nome, me in zip(("Javali_Corpo", "Javali_Cabeca"), dst.meshes):
    o = bpy.data.objects[nome]; assert len(o.data.vertices) == len(me.vertices), nome
    c = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", c); o.data.vertices.foreach_set("co", c); o.data.update()
    bpy.data.meshes.remove(me); print("TROCADO", nome, len(o.data.vertices))
bpy.ops.wm.save_as_mainfile(filepath=SAIDA, relative_remap=True); print("GERADOR_OK", SAIDA)
