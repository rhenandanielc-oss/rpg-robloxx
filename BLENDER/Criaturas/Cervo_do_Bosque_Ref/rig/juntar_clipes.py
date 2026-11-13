"""Junta as acoes Cervo_* de varios .blend de clipes no arquivo aberto (rig r2) e salva a base unica.
Uso: blender -b rig/clipes_r2/L1/Cervo_Clipes_L1.blend -P rig/juntar_clipes.py -- <saida.blend> <outro1.blend> [outro2.blend ...]"""
import bpy, sys, os
A = sys.argv[sys.argv.index("--") + 1:]; SAIDA = os.path.abspath(A[0])
for arq in A[1:]:
    with bpy.data.libraries.load(os.path.abspath(arq), link=False) as (src, dst):
        dst.actions = [n for n in src.actions if n.startswith("Cervo_") and n not in bpy.data.actions]
    for a in bpy.data.actions: a.use_fake_user = True
print("ACOES", sorted(a.name for a in bpy.data.actions if a.name.startswith("Cervo_")))
bpy.ops.wm.save_as_mainfile(filepath=SAIDA); print("JUNTAR_OK")
