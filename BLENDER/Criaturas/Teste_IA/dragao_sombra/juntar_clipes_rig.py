"""Junta ao rig de jogo atual (sem clipes) TODAS as acoes Silverwing_* de outro rig do mesmo esqueleto (mesmos 100 ossos,
repouso identico) e salva um rig completo -- para auditar/renderizar os clipes na malha atual.
Uso: blender -b rig_sem_clipes.blend -P juntar_clipes_rig.py -- <rig_com_clipes.blend> <saida.blend>"""
import bpy, sys
fonte, saida = sys.argv[sys.argv.index("--") + 1:][:2]
with bpy.data.libraries.load(fonte) as (src, dst): dst.actions = [n for n in src.actions if n.startswith("Silverwing_")]
for a in bpy.data.actions: a.use_fake_user = True
A = bpy.data.objects["Silverwing_Rig"]
if not A.animation_data: A.animation_data_create()
bpy.ops.wm.save_as_mainfile(filepath=saida); print("JUNTAR_OK", len(bpy.data.actions))
