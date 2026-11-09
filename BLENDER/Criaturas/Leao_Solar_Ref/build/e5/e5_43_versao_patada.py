"""Cria Leao_Solar_Ref_E5_clipes_r2.blend: copia do E5_clipes com as Patadas r2; as da versao 1 ficam como Leao_Patada_{D,E}_v1.
Uso: blender -b Leao_Solar_Ref_E5_clipes.blend -P e5_43_versao_patada.py -- <gerado.blend> <saida.blend> [sufixo_antigas=_v1] [acoes=Leao_Patada_D,Leao_Patada_E]"""
import bpy, sys
A = sys.argv[sys.argv.index("--") + 1:]; SUF = A[2] if len(A) > 2 else "_v1"
NOMES = A[3].split(",") if len(A) > 3 else ["Leao_Patada_D", "Leao_Patada_E"]
for n in NOMES:
    if n in bpy.data.actions: bpy.data.actions[n].name = n + SUF; bpy.data.actions[n + SUF].use_fake_user = True   # acao nova: so acrescenta
with bpy.data.libraries.load(A[0]) as (src, dst): dst.actions = list(NOMES)
for a in dst.actions: a.use_fake_user = True
print("ACOES", sorted(a.name for a in bpy.data.actions)); bpy.ops.wm.save_as_mainfile(filepath=A[1])
