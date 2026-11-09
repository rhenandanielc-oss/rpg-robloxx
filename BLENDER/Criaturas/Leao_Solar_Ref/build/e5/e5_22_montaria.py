# S2 (06/11): clipes de MONTARIA do leao (so movimento). Decisao do usuario: o leao agacha e o cavaleiro sobe; dois lados.
# Carregado por exec() dentro de e5_20_clipes.py, depois da Fase B (usa base_foco, janela, pulso, rampa, R, MARCHA, CLIPES...).
# Lado E = x- (patas DE/TE; a malha do leao esta ~0,45 para +X da coluna), lado D = x+. Tempos (s), alinhados com o cavaleiro
# de teste (build/s2/s2_02_demo_montaria.py): 0,2 olha para o cavaleiro; 0,5-1,3 agacha nivelado, baixando o lado da subida;
# 1,45 o cavaleiro salta (pe no flanco, maos na aba e na alca, atras da juba); 1,9 puxa o corpo; 2,55 senta; 3,0-3,9 levanta
# com o cavaleiro; 4,0 repouso. (Subir pelo cotovelo, como no Crocodilo, atravessava o ombro e a juba larga do leao.)
MONT_AG = 2.6                                          # agachamento (studs); 2,9 no bote leva o peito ao chao com o quadril recuado
def c_montar(lado):
    sg = -1 if lado == "E" else 1
    def f(t, fase):
        c = base_foco(t, fase); ag = janela(t, 0.5, 3.95, 0.8, 0.95); olha = janela(t, 0.15, 2.9, 0.45, 0.7)
        pisa = janela(t, 1.45, 1.85, 0.06, 0.3); puxa = janela(t, 1.85, 2.4, 0.12, 0.3); senta = janela(t, 2.5, 3.05, 0.08, 0.35)
        c.update(z=-MONT_AG * ag - 0.10 * pisa - 0.06 * puxa - 0.14 * senta, roll=sg * R(3.5) * ag + sg * R(1.0) * pisa,
                 col1=R(2) * ag, col2=R(-2) * ag, pesc=R(6) * ag, pesc_yaw=sg * R(16) * olha, cab_yaw=sg * R(22) * olha, cab_pitch=R(3) * ag,
                 orelha=(R(-10) * olha, R(-10) * olha), cauda_base=R(4) + R(3) * ag, cauda_amp=R(3), cauda_f=1 / 3.2)
        return c
    return f
CLIPES.update({
    "Montar_E": dict(dur=4.6, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_montar("E")),
    "Montar_D": dict(dur=4.6, loop=False, pose_repouso=True, marcha=lambda t: MARCHA["parado"], vel=lambda t: 0.0, rumo=lambda t: 0.0, corpo=c_montar("D")),
})
