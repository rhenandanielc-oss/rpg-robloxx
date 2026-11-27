"""v49: video das CURVAS DE TROTE E CORRIDA (reaproveita montar_videos_v46). ANTES = o Controle hoje: a marcha reta com o pivo girando.
Uso: python montar_videos_v49.py <dir_quadros> <dir_saida>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar_videos_v46 as MV
MV.ROT_ANTES = "ANTES  marcha reta + pivo girando"; MV.ROT_DEPOIS = "DEPOIS  v49  curva com passos"
MV.NOTA_ANTES = "   (antes: o Controle girava o pivo sobre o trote/corrida reto)"
P = []
for v in ("topo", "c34", "perfil_D"):
    P.append(MV.montar("tr_" + v, "TROTE em curva fechada a direita (45 -> 90 graus/s) - antes x depois", "trote_fechada_D", [[("ANTES", v), ("V46B", v)]]))
P.append(MV.montar("tr_lento", "TROTE - detalhe", "trote_fechada_D", [[("ANTES", "perfil_D"), ("V46B", "perfil_D")]], lento=True))
for v in ("topo", "c34", "perfil_E"):
    P.append(MV.montar("co_" + v, "CORRIDA em curva aberta a esquerda (60 graus/s) - antes x depois", "corrida_aberta_E", [[("ANTES", v), ("V46B", v)]]))
P.append(MV.montar("co_lento", "CORRIDA - detalhe", "corrida_aberta_E", [[("ANTES", "perfil_E"), ("V46B", "perfil_E")]], lento=True))
MV.juntar("video_v49_trote_corrida", P)
