"""v50: video da PARTIDA EM CURVA rapida (reaproveita montar_videos_v46). ANTES = a partida em curva da v48 (instalada no jogo);
DEPOIS = v50 (giro forte nos primeiros passos, centro do giro um pouco atras do meio do corpo).
Uso: python montar_videos_v50.py <dir_quadros> <dir_saida>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar_videos_v46 as MV
MV.NOME_V["close_E"] = "close patas esq (segue)"
MV.ROT_ANTES = "ANTES  v48  partida em curva (54 graus em 2,4 s)"; MV.ROT_DEPOIS = "DEPOIS  v50  virada forte no comeco (87 graus)"
MV.NOTA_ANTES = "   (antes: a partida em curva girava devagar, so 30 graus/s no fim)"
P = []
for c, t in (("partida_curva_E", "esquerda"), ("partida_curva_D", "direita")):
    for v in ("topo", "c34"):
        P.append(MV.montar("pc%s_%s" % (c[-1], v), "Partindo parado ja em curva a %s - antes x depois" % t, c, [[("ANTES", v), ("V46B", v)]]))
P.append(MV.montar("pcE_lento", "Partida em curva a esquerda - detalhe das patas", "partida_curva_E", [[("ANTES", "close_E"), ("V46B", "close_E")]], lento=True))
MV.juntar("video_v50_partida_curva", P)
