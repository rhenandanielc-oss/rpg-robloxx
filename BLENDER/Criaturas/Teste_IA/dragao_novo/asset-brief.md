ASSET      CR_DragaoMontanhas (conceito novo, inspirado em ref/conceito_dragao_vermelho.png)
CATEGORY   creature, winged quadruped (4 patas + 2 asas)
VIEWS      conceito_dragao_vermelho.png: conceito em perspectiva, 3/4 frente-esquerda, elevacao ~10 graus, lente ~50 mm;
           sujeito ocupa ~95% da altura; pose SENTADA, asas erguidas. Unica imagem, sem vistas ortograficas:
           serve para silhueta de detalhe e materiais, NAO para medir proporcoes exatas.
SCALE      sem pista de escala; unidade de trabalho: comprimento focinho-cauda ~2,8 u (o jogo aplica ScaleTo,
           como o Silverwing). Ombro ~0,62 u.
PROPORTIONS (estimadas no conceito, tolerancia larga por ser perspectiva)
           - pescoco grosso em S, base ~0,8x a largura do peito
           - cabeca ~0,28 u, ~1/3 do pescoco
           - torax/ventre volumosos (raio ~0,165)
           - coxas traseiras grandes (raio ~0,12), antebracos grossos
           - chifres principais ~1,1x o comprimento da cabeca, varridos para tras e para cima
           - asas grandes: envergadura ~1,6x o comprimento do corpo
           - cauda longa e afinando, ~55% do comprimento total
PARTS      corpo unico (pele; deforma); mandibula (no corpo, osso proprio no rig); membranas E/D (deformam,
           separadas); chifres x4 (rigidos, presos ao cranio); espinhos dorsais (rigidos, presos a cada osso
           da coluna/cauda); babados de espinhos na bochecha (rigidos, cranio/mandibula); garras (rigidas,
           dedos); olhos (rigidos, cranio).
SILHOUETTE chifres marfim longos para tras; crista de espinhos do cranio a cauda; pescoco grosso em S;
           asas grandes com dedos marcados e borda recortada; corpo robusto com coxas fortes.
MATERIALS  escamas vermelhas (rugosidade 0,45-0,6, frestas escuras, escamas maiores no dorso);
           ventre marfim em placas transversais da garganta a ponta da cauda; chifres/garras marfim
           (base mais escura, ponta clara, rugosidade 0,4); membrana vermelho-alaranjada translucida com
           veias; dedos da asa pessego claro; espinhos vermelho escuro; olhos ambar.
ARTICULATION rig de dragao proprio (coluna, pescoco 5+, cauda 8+, mandibula, 4 patas com dedos, asas com
           umero/antebraco/4 dedos + polegar). Animacao completa (andar, correr, voo, ataques).
           ADAPTACOES PARA MOVIMENTO (diferencas deliberadas do conceito):
           - pose neutra: em pe, patas retas, asas abertas (o conceito esta sentado);
           - membrana presa so ao flanco, a frente do quadril (pata traseira livre);
           - espinhos espacados e inclinados para tras (pescoco dobra sem um espinho atravessar o outro);
           - chifres com folga do pescoco com a cabeca erguida 45 graus;
           - ventre em placas so na textura (tronco dobra sem placas rigidas);
           - aneis de geometria em todas as articulacoes (grafo Skin).
INFERRED   costas, lado direito (simetria), parte de baixo das asas, patas traseiras completas, cauda inteira,
           pose em pe (conceito sentado), numero de dedos das patas (4), contagem de chifres atras do cranio.
TARGET     Roblox, GLB; malha de jogo final <= 20k tris com LOD (a versao de conceito e alta resolucao, so
           para aprovacao); camera de jogo 3/4 elevada; ~128 px de altura na distancia tipica.
