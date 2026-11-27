"""v51: video da CORRECAO DO APOIO na partida em curva (reaproveita montar_videos_v46). ANTES = v50 (rolamento do pe girava com o
corpo e arrastava a sola), DEPOIS = v51 (rolamento no rumo em que a pata pousou). Mesma trajetoria e mesmo giro (87 graus em 2,4 s).
Uso: python montar_videos_v51.py <dir_quadros> <dir_saida>"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import montar_videos_v46 as MV
MV.NOME_V["close_E"] = "close patas esq (segue)"; MV.NOME_V["close_D"] = "close patas dir (segue)"
MV.ROT_ANTES = "ANTES  v50  (traseira esq. desliza 0,071)"; MV.ROT_DEPOIS = "DEPOIS  v51  (apoio firme na partida)"
MV.NOTA_ANTES = "   (v50: o rolamento do pe girava junto com o corpo e arrastava a sola; v51: fica no rumo em que a pata pousou)"
P = []
for v in ("perfil_E", "c34", "topo", "close_E"):
    P.append(MV.montar("e_" + v, "Partida em curva a ESQUERDA - v50 x v51 (velocidade normal)", "partida_curva_E", [[("ANTES", v), ("V46B", v)]]))
for v in ("close_E", "perfil_E"):
    P.append(MV.montar("e_lento_" + v, "Partida em curva a ESQUERDA - camera lenta", "partida_curva_E", [[("ANTES", v), ("V46B", v)]], lento=True))
for v in ("perfil_D", "topo", "close_D"):
    P.append(MV.montar("d_" + v, "Partida em curva a DIREITA - v50 x v51 (velocidade normal)", "partida_curva_D", [[("ANTES", v), ("V46B", v)]]))
P.append(MV.montar("d_lento_close_D", "Partida em curva a DIREITA - camera lenta", "partida_curva_D", [[("ANTES", "close_D"), ("V46B", "close_D")]], lento=True))
MV.juntar("video_v51_apoio_partida_curva", P)
