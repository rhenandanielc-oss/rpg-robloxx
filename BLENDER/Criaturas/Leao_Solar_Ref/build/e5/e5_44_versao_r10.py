"""Cria Leao_Solar_Ref_E5_clipes_r10.blend a partir do r9: troca os clipes atuais pelos regerados (Fase C r2: palpebra com sinal
corrigido + piscadas em todos; vida r2 por referencia do usuario). Os historicos (_v1/_r2/_r3) ficam; o r9 continua como backup.
Uso: blender -b Leao_Solar_Ref_E5_clipes_r9.blend -P e5_44_versao_r10.py -- <saida.blend> <fonte1.blend>[:Acao1,Acao2] <fonte2.blend>[:...] ..."""
import bpy, sys
A = sys.argv[sys.argv.index("--") + 1:]; SAIDA = A[0]; trocadas = []
for spec in A[1:]:
    caminho, _, filtro = spec.partition("::")
    with bpy.data.libraries.load(caminho) as (src, dst):
        nomes = [n for n in src.actions if not filtro or n in filtro.split(",")]
        dst.actions = list(nomes)   # copia: a lista passada vira lista de Action apos o load
    trocadas += nomes
    for nova in dst.actions:
        base = [n for n in nomes if nova.name == n or nova.name.startswith(n + ".")][0]
        if nova.name != base:
            velha = bpy.data.actions[base]
            for ob in bpy.data.objects:
                if ob.animation_data and ob.animation_data.action == velha: ob.animation_data.action = None
            bpy.data.actions.remove(velha); nova.name = base
        nova.use_fake_user = True
print("TROCADAS", len(trocadas)); print("ACOES", len(bpy.data.actions), sorted(a.name for a in bpy.data.actions))
bpy.ops.wm.save_as_mainfile(filepath=SAIDA)
