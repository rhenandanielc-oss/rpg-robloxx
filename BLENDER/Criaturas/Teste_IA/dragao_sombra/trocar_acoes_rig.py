"""Substitui TODAS as acoes Silverwing_* deste .blend pelas de outro rig do mesmo esqueleto (06/11: os rigs v10/v11 com
boca e sela tinham saido do v9.blend, mais antigo que o v9_ataques, onde estao as correcoes de contato aprovadas em
03/11 -- Sentado, Dormir, Acordar...). Malha, boca, sela e esqueleto ficam; so as acoes mudam.
Uso: blender -b <alvo.blend> -P trocar_acoes_rig.py -- <fonte_das_acoes.blend> <saida.blend>"""
import bpy, sys
fonte, saida = sys.argv[sys.argv.index("--") + 1:][:2]
A = bpy.data.objects["Silverwing_Rig"]
if A.animation_data: A.animation_data.action = None
velhas = [a for a in bpy.data.actions if a.name.startswith("Silverwing_")]
for a in velhas: bpy.data.actions.remove(a)
with bpy.data.libraries.load(fonte) as (src, dst): dst.actions = [n for n in src.actions if n.startswith("Silverwing_")]
for a in bpy.data.actions: a.use_fake_user = True
print("TROCAR_ACOES removidas", len(velhas), "novas", len(dst.actions))
bpy.ops.wm.save_as_mainfile(filepath=saida); print("TROCAR_ACOES_OK", saida)
