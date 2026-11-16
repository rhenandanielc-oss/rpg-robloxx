# Kit do Lobo Ancestral - Hab_Investida sincronizada com a Corrida v30 (15/11/2026, para o import no Studio).
# Carregado por exec() em anim_lobo.py DEPOIS da marcha v30, quando LOBO_KIT=1 e LOBO_MARCHA30=1.
# A Investida v28 (habilidades/clipes_kit.py, clipes_kit28/) usava o galope transverso v28; a Corrida v30 e rotatoria
# (GALOPE29, marcha29). Aqui so troca o galope-base e a velocidade; fases, marcadores, curva de avanco, carga, mordida,
# freada e passos de volta continuam os da v28 (mesmo codigo). Os clipes v28 ficam intactos em clipes_kit28/.
_GAL = marcha29(**GALOPE29)
VEL_INV = vel29(GALOPE29)                                              # 21,43 studs/s (= Corrida v30)
_TAB_INV = []                                                          # recalcula a tabela das patas com o galope novo
