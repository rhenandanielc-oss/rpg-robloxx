"""v48: video da PARTIDA/PARADA com passos (reaproveita montar_videos_v46: paineis rotulados + barra de diagnostico + trechos lentos).
ANTES = o que o Controle fazia: fade do Repouso para o Andar ja na velocidade cheia e fade de volta ao parar.
Uso: python montar_videos_v48.py <dir_quadros> <dir_saida>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar_videos_v46 as MV
MV.NOME_V["close_E"] = "close patas esq (segue)"
MV.ROT_ANTES = "ANTES  fade Repouso->Andar e Andar->Repouso"; MV.ROT_DEPOIS = "DEPOIS  v48  partida e parada com passos"
MV.NOTA_ANTES = "   (antes: o Controle ja saia na velocidade cheia e parava com fade)"
P = []
for v in ("topo", "c34", "perfil_E", "close_E"):
    P.append(MV.montar("pp_" + v, "Partida e parada retas - antes x depois", "partida_parada_reta", [[("ANTES", v), ("V46B", v)]]))
P.append(MV.montar("pp_lento", "Partida e parada retas - detalhe", "partida_parada_reta", [[("ANTES", "close_E"), ("V46B", "close_E")]], lento=True))
P.append(MV.montar("pc", "DEPOIS  partindo parado ja em curva (sem virar no lugar) e parando", "partida_curva_E", [[("V46B", "topo"), ("V46B", "c34")]]))
MV.juntar("video_v48_partida_parada", P)
