# Wyvern — base Ashwing Drake Lite (em avaliação)

**Base:** "Ashwing Drake Lite" da Literock Studios, versão gratuita. O zip original está em `Downloads\Ashwing_Drake_Lite_v1.0.0.zip`. O usuário a adotou em 03/11/2026 como base da Wyvern.

**Licença, em resumo:**
- uso livre no jogo, inclusive comercial, e modificação permitida;
- **proibido redistribuir ou reenviar o asset sozinho**, mesmo modificado;
- proibido usar como dado de treino de IA e proibido reivindicar autoria;
- crédito opcional: "Ashwing Drake by Literock Studios".

Por isso:
- os binários (`origem/*.glb`, `*.blend`, `texturas/*.png`) ficam fora do git, pelo `.gitignore` atual;
- não publicar o modelo na Creator Store nem como modelo público.

## Etapas (scripts em `build/`, Blender 5.2 em linha de comando)

| Etapa | Script | Resultado |
|---|---|---|
| Medidas | `00_medir.py` | Original em metros: cernelha 2,0 m, envergadura 12 m, 61 ossos, 6 clipes, shape keys `fold_corrective_L/R` |
| E1 proporção | `01_proporcao.py -- glb saida 10 36.5 0.8` | ×5,006 m→stud. Asas a 0,639 (escala uniforme no `upperarm`), cauda a 0,8 sem afinar. Medido: cernelha 10,0; envergadura 40,2 no repouso e 36,3 no voo; comprimento 39,5–41. Os clipes acompanham a escala |
| E2 ferrão | `02_ferrao.py -- saida 5.5 110` | Ponta em losango remodelada: bulbo de glândula + gancho curvo de 5,5 studs e 110°. São os mesmos 226 vértices, com a mesma UV, e o gancho pesa 100% em `tail_10` |
| E3 padrões | `03_padroes.py -- saida pasta_tex` | Albedo recolorido por mapa de gradiente, com máscaras por região na UV (membrana, corpo, ferrão) e manchas por ruído 3D. Gera 3 PNG 2048 (`texturas/Wyvern_Cor_*`) e define Verde Musgo como padrão do material |
| E4 transição do ferrão | `04_transicao_ferrao.py -- Wyvern_E1.blend saida` (sobre o E3) | Junção cauda–bulbo–gancho refeita num tubo analítico liso: mesmos 280 vértices, UV, material, ossos e texturas; mesma curva (5,5 studs, 110°); bulbo 2,0× (era 2,1×). Detalhes abaixo |
| M0/QA do ferrão | `04a_diagnostico_ferrao.py`, `04c_qa_ferrao.py` | Medidas por fatia, diedros, pesos, UV; QA estático e nos ciclos idle/walk/fly completos, com o mesmo método para E1, E3 e E4 (`review/e4/qa/qa_*.json`) |
| Revisão | `90_revisao.py`, `91_montagem.py`, `04b_closes.py`, `04d_video.py` | Folhas em `review/` com câmera de escala fixa e humano de 5,5 studs; closes do ferrão com câmera fixa no osso tail_10 (idêntica entre versões); vídeos dos ciclos E3 \| E4 |

Arquivos de trabalho: `Wyvern_E1.blend` → `Wyvern_E2.blend` → `Wyvern_E3.blend` → `Wyvern_E4.blend` → `Wyvern_E6.blend`. `Wyvern_E5_tentativa_reprovada.blend` é só evidência da tentativa de 04/11, não é base. **`Wyvern_E6.blend` é o atual: o ferrão foi APROVADO pelo usuário em 05/11/2026** (ajuste local de topologia autorizado em 04/11). O lote 1 de clipes (locomoção e voo) está em `Wyvern_E7_clipes_L1.blend`, em avaliação. Exportação e Studio continuam pendentes. E1, E2 e E3 continuam intactos.

## E4 — correção da transição cauda–bulbo–gancho (04/11/2026)

**Causas medidas no M0** (`04a_diagnostico_ferrao.py`, closes com arame em `review/e4/diag/`):
1. A ponta original do Ashwing não tem anéis de vértices: várias fatias de 0,25 têm só 1 a 3 vértices, e 86 vértices estão concentrados na ponta. O `02_ferrao.py` normalizava cada fatia pela largura dela, o que jogava vértices para direções erradas e gerava as espículas e calombos.
2. O raio do bulbo era só C0 no pico (t = 0,22), porque o afinamento começava com derivada diferente de zero. A mistura com a cauda tinha só 0,04 × 5,5 = 0,22 stud. Isso causava a dobra.
3. O modelo tem normais personalizadas do glTF e `sharp_edge`/`sharp_face` na ponta original. Elas não foram recalculadas no E2, e o resultado eram facetas claras no sombreado.
4. O peso de `tail_10` saltava de 0 para 1 entre vértices vizinhos (y ≈ 25,26–25,8), exatamente sobre o bulbo e a articulação tail_09/tail_10 (25,29). Isso causava pinçamento ao dobrar.
5. Há uma espícula fina original do Ashwing em y ≈ 22,7, com diedros de ~175° e 8 faces já dobradas no E1. No E3 ela parece um calombo do bulbo.

**Correção:**
- Cada vértice recebe um ângulo em torno do centro LOCAL da seção original (E1) e é recolocado num tubo liso com o mesmo eixo curvo do E2. O raio é C1 (bulbo smootherstep → afinamento cos^1,25, ponta com raio mínimo de 0,022), com leve variação radial monotônica.
- A mistura com a cauda original passa a 0,75 stud.
- Na zona de entrada (22,3–23,36), o raio fica limitado a 1,08× o envelope.
- Pesos tail_09→tail_10 em rampa suave de 24,7 a 26,3.
- Normais lisas por posição soldada (as costuras de UV duplicam vértices), só na região e com entrada suave.
- Relaxamento guloso só do ângulo para desdobrar faces (o comprimento fica fixo, então o gradiente de veneno não desliza).
- Sem subdivisão, sem vértice, osso ou material novo. Shape keys preservadas (deslocamento nulo na região).

**Métricas** (mesmo método e pose; região y ≥ 22,3 com 280 vértices e 291 triângulos; `review/e4/qa/`):

| | E1 (Ashwing escalado) | E3 (antes) | E4 (depois) |
|---|---|---|---|
| Triângulos / vértices / ossos | 11.992 / 9.152 / 61 | 11.992 / 9.152 / 61 | 11.992 / 9.152 / 61 |
| Materiais / imagens de padrão | 1 / – | 1 (`Wyvern`) / 3 | 1 (`Wyvern`) / 3 |
| Dimensões em repouso X×Y×Z | 40,19 × 39,48 × 19,84 | 40,19 × 37,63 × 19,84 | 40,19 × 37,52 × 19,84 |
| Dimensões no idle f0 | 13,03 × 40,52 × 16,13 | 13,03 × 39,08 × 16,13 | 13,03 × 38,95 × 16,13 |
| Autointerseções em repouso | 0 | 75 | **0** |
| Triângulos degenerados (< 1e-4) | 0 | 0 | 0 |
| Faces dobradas | 12 (8 da espícula original) | 33 | 16 (8 da espícula original) |
| Diedros > 90° / diedro médio | 17 / 22,3° | 65 / 48,7° | 23 / 28,9° |
| Estiramento UV p05/p50/p95 | 0,37/1,10/2,49 | 0,25/0,99/3,08 | 0,33/1,18/3,51 |
| Bordas abertas reais | 10 | 10 | 10 (originais do Ashwing) |
| idle: estiramento máx / área mín / interseções máx | 1,21 / 0,20 / 3 | 1,30 / 0,55 / 76 | 1,22 / 0,76 / 2 |
| walk: idem | 1,32 / 0,14 / 8 | 1,45 / 0,51 / 77 | 1,32 / 0,65 / 2 |
| fly: idem | 1,15 / 0,79 / 6 | 1,30 / 0,66 / 81 | 1,15 / 0,75 / 7 |

**Evidências:**
- `review/E4_closes_antes_depois.png`: closes lateral, superior e 3/4; E3 em cima, E4 embaixo.
- `review/E4_closes_arame.png`: os mesmos closes com arame.
- `review/E4_corpo_antes_depois.png`: corpo inteiro de lado e em 3/4, mais o close lateral.
- `review/E4_padroes.png`: E3 × E4 nos 3 padrões, mais o corpo do E4.
- `review/E4_ciclo_{idle_loop,walk_loop,fly_loop}.mp4`: em cima 3/4, embaixo lado; esquerda E3, direita E4. Os quadros soltos estão em `review/e4/ciclos/`.
- `review/E4_ciclos_folha.png`: quadros do walk (0, 10, 18), do fly (0, 7, 14) e do idle (0, 23, 48); em cada célula, E3 à esquerda e E4 à direita.

## Verificação local do E4, caso a caso (04/11/2026)

**Método** (`build/05a_verificar_ferrao.py`, aplicado do mesmo jeito em E1, E4 e na tentativa E5; resultados em `review/e5/qa/verif_*.json`):
- todos os frames de idle_loop (0–72), walk_loop (0–25) e fly_loop (0–19);
- vértices soldados por distância (1e-3);
- para cada interseção: segmento, profundidade e visibilidade, medida com 26 raios externos;
- para cada face dobrada: se o verso aparece de fora;
- para cada borda aberta: posição e laço a que pertence.

O `04c_qa_ferrao.py` antigo contava interseções só em frames pares e tratava como interseção triângulos que se tocam numa costura deslocada. As contagens 2/2/7 e "16 dobradas" do relatório do E4 eram contagens brutas.

**E4, casos reais** (imagens marcadas: `review/E5_casos_juncao.png`, `review/E5_casos_ponta.png` e os quadros soltos em `review/e5/marcados/`, com rótulo de versão, pose e vista):

| Caso | Onde | Classe | Visível? | Origem |
|---|---|---|---|---|
| Interseções idle / walk | região toda | 0 reais (28–35 adjacentes de costura + 1–5 rasantes por frame = falsos positivos) | não | E1 tinha 2 reais visíveis no walk em y≈25,6–25,8 (0,054 de profundidade) — o E4 eliminou |
| 2 interseções no fly | aba da junção, y≈22,80–22,82, frames 4–10 | reais, profundidade 0,003–0,010 | sim, mínima | herdado (E1 idêntico) |
| Aba dobrada da junção | y 22,69–22,84, 8 triângulos (6, 133–136, 139, 143, 144) | dobra real | **sim**: o verso das 134, 139 e 143 aparece por baixo | herdado (E1 idêntico) |
| Anel de borda | y≈22,67, 11 arestas, laço fechado | emenda em T geometricamente fechada | não (nenhum verso aparece pelo anel) | herdado |
| Fenda na ponta do gancho | y≈27,1–27,3, 9 arestas em 4 cadeias + faces 91, 271, 286 | borda aberta real (a "lâmina" do losango original não é fechada) | **sim**: fresta de ~0,4 stud no lado interno do gancho, com o verso aparecendo | herdado (E1 tem a mesma fenda na ponta do losango) |
| Faces 60, 218 (y≈25,5) | meio do bulbo | dobradas, verso nunca visível | não | herdado |
| Face 232 (y≈26,3) | gancho | faceta íngreme (99°), só a frente aparece | não como dobra | E4 |
| Faces 260, 277 (y≈27,2) | ponta | dobradas minúsculas (área < 0,008), verso não aparece | não | E4/E1 |

**Tentativa E5, reprovada** (`Wyvern_E5_tentativa_reprovada.blend`; `04_transicao_ferrao.py` com as opções `juncao_tubo fenda`, partindo do E4):
- Levar a zona da junção ao tubo e pôr os lábios da fenda no mesmo ângulo e raio **piorou** o resultado:
  - a aba continuou saindo para fora;
  - surgiram interseções reais visíveis de até 0,10 stud na ponta, em todos os frames.
- Conclusão: com a topologia atual, mover vértices não fecha a fenda nem elimina a aba. Por isso parei, conforme o pedido.
- Sem as opções, o script reproduz o E4 exatamente (diferença 0,0).

**Proposta, não autorizada, aguardando o usuário: ajuste local de topologia.**
1. Ponta: soldar os lábios da fenda (cerca de 5 vértices a menos, 0 triângulos novos; UV mantida, os dois lados têm a cor do veneno) ou ligar as bordas com cerca de 8–12 triângulos.
2. Junção: dissolver os 8 triângulos da aba e soldar os vértices dela ao anel (cerca de 8 triângulos a menos). Isso também elimina as 2 interseções do fly.

Custo estimado: ±20 triângulos sobre 11.992 (0,2%), sem osso ou material novo, e com a textura atual. Observação, a confirmar na exportação: no Roblox as faces têm um lado só por padrão, então a fenda tende a aparecer como furo vazado em vez do verso escuro. **Não testado.**

## E6 — ajuste local de topologia (autorizado pelo usuário em 04/11/2026)

Feito por `build/06_topologia_ferrao.py -- saida`, partindo do E4, só com y ≥ 22,3:
1. Soldei as duplicatas de costura de UV dentro da região (dist 1e-4). A UV fica guardada por canto e não muda.
2. **Aba da junção:** apaguei as 8 faces dobradas e fechei o buraco com 8 triângulos sobre os vértices já existentes.
3. **Ponta:** a "fenda" eram 12 abas soltas, triângulos presos por arestas compartilhadas por mais de 2 faces, mais um triângulo preso a um único vértice. Apaguei as abas, e não sobrou nenhuma borda aberta.
4. As faces novas receberam UV copiada dos cantos vizinhos. Não há vértice novo.
5. **Pesos da junção:** a camada da cauda (tail_08) sobrepõe a da ponta (tail_09) no dorso, em y ≈ 22,4–23,3, com pesos desencontrados entre as camadas. Isso causava as 2 penetrações do fly. Troquei por uma rampa única tail_08 → tail_09 de 22,3 a 23,1, que se aplica a 19 vértices.
6. Normais lisas só na região, como no E4.

O "anel de 11 bordas" em 22,5–22,9 que aparecia no E1/E4 **não é borda da malha**. Ele vem do corte da região de análise, porque triângulos longos da cauda atravessam y = 22,3. Na malha inteira, a região tem 0 bordas abertas.

**Fora da região (y < 22,3) nada mudou:** 8.872 vértices, com diferença máxima de posição 0,0 e de peso 0.

| | E4 | E6 |
|---|---|---|
| Triângulos / vértices / ossos / materiais | 11.992 / 9.152 / 61 / 1 | **11.980** / 9.018 (solda de costura) / 61 / 1 |
| Padrões / shape keys | 3 / Basis + 2 correctives | iguais |
| Dimensões (repouso e idle f0) | 40,19 × 37,52 × 19,84 / 13,03 × 38,95 × 16,13 | iguais |
| Bordas abertas reais / arestas com mais de 2 faces na região | 9 (fenda) / 11 | **0 / 0** |
| Faces dobradas / com verso visível de fora | 16 / 6 | 5 / **0** |
| Penetrações reais em idle / walk / fly (todos os frames) | 0 / 0 / 2 (f4–10) | **0 / 0 / 0** |
| Diedros > 90° / médio | 23 / 28,9° | 20 / 26,8° |
| Estiramento UV p05/p50/p95 | 0,33/1,18/3,51 | 0,26/1,21/3,58 |
| idle: estiramento máx / compressão mín / área mín | 1,22 / 0,79 / 0,76 | 1,07 / 0,93 / 0,86 |
| walk: idem | 1,32 / 0,69 / 0,65 | 1,10 / 0,90 / 0,80 |
| fly: idem | 1,15 / 0,86 / 0,75 | 1,08 / 0,92 / 0,89 |

As 5 faces dobradas que restam nunca mostram o verso de fora:
- 60 e 216 em y ≈ 25,5, herdadas;
- 230 em 26,3, uma faceta íngreme de 99°;
- 256 e 266 em 27,2, minúsculas.

Nos ciclos sobram só toques adjacentes e rasantes, de 2 a 3 por frame, sem penetração.

**Evidências** (com rótulo de versão, pose e vista em cada quadro):
- `review/E6_marcados_juncao.png`, `review/E6_marcados_ponta.png`: casos marcados, com a mesma câmera fixa para E4 e E6;
- `review/E6_closes_antes_depois.png`, `review/E6_closes_arame.png`, `review/E6_corpo_antes_depois.png`, `review/E6_padroes.png`;
- `review/E6_ciclo_{idle_loop,walk_loop,fly_loop}.mp4`: em cima 3/4, embaixo lado; esquerda E4, direita E6;
- `review/E6_ciclos_folha.png`;
- medições em `review/e6/qa/verif_E6.json` e `qa_E6.json`.

## Lote 1 de clipes: locomoção e voo (05/11/2026, aprovado)

Arquivo: `Wyvern_E7_clipes_L1.blend`, que é o E6 com 7 actions novas. A malha e o rig são os do E6, sem mudança.
- Script: `build/07_clipes_lote1.py -- saida manifesto`, partindo do E6.
- Revisão: `07b_revisao_clipes.py` (quadros), `07c_qa_clipes.py` (QA) e `07d_video_seq.py` (MP4).

Os clipes **derivam dos 6 clipes do próprio Ashwing** (mesmo estilo e rig), com camadas procedurais. Têm chaves a 30 Hz, como os originais, e as shape keys `fold_corrective` no slot KEY.

| Clipe | Como foi feito | Duração |
|---|---|---|
| Corrida (loop) | walk_loop com fase própria para cada perna: balanço reparametrizado pela distância angular, 70% uniforme. Desvio da pose média ×1,15, tronco inclinado, quique, cauda em onda | 0,72 s |
| VirarEsquerda / VirarDireita (loop) | walk_loop com coluna, pescoço, cabeça e cauda em arco; tronco inclinado para dentro | 1,07 s |
| Planeio (loop) | quadro do fly_loop com asas horizontais (0,225 s) sustentado, com oscilação lenta de asa, cauda e pescoço | 2,4 s |
| CurvaAereaEsquerda / Direita (loop) | Planeio com rolagem de 24° para dentro, cabeça na curva, cauda como leme e asa de dentro um pouco baixa | 2,4 s |
| Pouso (único) | takeoff invertido (desce com deslocamento da raiz, de 26,5 a 0). No ar, as batidas do fly_loop perdem força até a frenagem (flare). Toque no chão em 1,2 s, cauda erguida, asas do flare até o idle | 2,54 s |

**QA** (`review/l1/qa_L1.json`): todas as amostras de 30 Hz, com o mesmo método nos 6 clipes originais como linha de base.

| | Linha de base | Lote 1 |
|---|---|---|
| Salto máximo por amostra | walk 66° (do próprio Ashwing), takeoff 47° | Corrida 70°, Viradas 66°, Pouso 39°, voo 0,2° |
| z mínimo da malha | walk −0,06, takeoff −0,14 | Corrida −0,01, Viradas −0,06, Pouso −0,05 |
| Pé apoiado (velocidade / desvio) | walk 9,9 / 2,1 studs/s | Corrida 16,8 / 0,5 studs/s; Viradas 9,9 / 2,1 |
| Autointerseções reais (máx.) | walk 998, fly 265, takeoff 891 | Corrida 1.021, Viradas 1.011–1.028, Planeio 243, Curvas 245–246, Pouso 783 |

Sobre a tabela:
- **Autointerseções:** a malha do Ashwing já tem cerca de 770 delas até no idle, nos dedos e escoras da asa dobrada e na coxa dentro do corpo. O critério usado é não piorar em relação à linha de base.
- **Emenda dos loops:** é exata, porque o último quadro é igual ao primeiro. O valor "emenda" do QA da Corrida é artefato de amostragem (0,8 quadro contra o passo real de 0,82).
- **Curvas aéreas:** z < 0 na ponta da asa em rolagem não é contato. Os clipes de voo são feitos no lugar, como o fly_loop.
- **Velocidades:** são **PROPOSTA** visual e não definem mecânica.

**Evidências** (rótulo com clipe, quadro e vista; câmera fixa; humano de 5,5 studs; grade no chão a cada 4 studs):
- `review/L1_folha_terra.png`, `review/L1_folha_ar.png`, `review/L1_folha_pouso.png`;
- `review/L1_<Clipe>.mp4`, com a vista lateral em cima e a 3/4 embaixo.

**Ainda não feito (no lote 1):**
- ferroada, reação, morte, comer, descanso (feitos no lote 2); pairar, empoleirar, montaria e ninho;
- habilidades, que aguardam a decisão do elemento e do kit;
- exportação, JSON e Studio.

## Lote 2 de clipes: ferrão, reações e vida em terra (05/11/2026, em avaliação)

Arquivo: `Wyvern_E7_clipes_L2.blend` = lote 1 + 9 actions novas. Malha e rig do E6, sem mudança.
- Script: `build/08_clipes_lote2.py -- 08_base.py saida manifesto`, partindo de `Wyvern_E7_clipes_L1.blend`.
- `build/08_base.py`: funções comuns (as do lote 1 + cinemática direta própria, IK de perna por mínimos quadrados, z mínimo da malha por região para encostar partes no chão por bisseção).
- `07b_revisao_clipes.py` ganhou argumentos opcionais (quadros fixos, centro e escala da câmera). Lote 2 renderizado com centro (0, 7, 12) e ortho 50.

| Clipe | Como foi feito | Duração |
|---|---|---|
| FerraoAtaque (único) | idle + cauda em arco sobre o dorso (estilo escorpião, 215° no total) em 0,40 s; golpe em 0,16 s: o arco se lança à frente e a ponta desce adiante da cabeça, passando acima dos chifres e um pouco para o lado L; peito avança, cabeça sai para o lado R; volta ao idle | 1,5 s |
| Alerta (loop) = "Observar, ferrão erguido" | idle com peito e pescoço altos, cabeça varrendo os lados, cauda "pronta" (sobe atrás e a ponta curva à frente), ponta inquieta | 3,0 s |
| Ameaca (único) | roar do Ashwing + cauda pronta e ponta tremendo | 2,0 s |
| ReacaoGolpe (único) | tranco em 0,07 s: peito para trás, cabeça sacode, boca abre, asas sobem um pouco, cauda reage; volta em 0,75 s | 0,75 s |
| Morte (único, pose final parada) | tranco → pernas cedem (IK) → cai de barriga; asas abrem subindo e depois caem abertas até a ponta tocar o chão; pescoço desaba de lado, cabeça quica uma vez; boca entreaberta | 2,7 s |
| Comer (loop) | agacha 1,5 stud com pés fixos (IK), coluna e pescoço baixos até a cabeça no chão; 2 mordidas + puxão com sacudida por ciclo | 3,0 s |
| Deitar / Deitado (loop) / Levantar | conjunto do Descanso: barriga no chão (raiz −4,25), pernas dobradas por IK (joelho à frente, jarrete e pé chapados no chão); antebraço mais dobrado para a garra do polegar não afundar; pescoço estendido para baixo e cabeça nivelada apoiada; Deitado respira; Levantar ergue a cabeça primeiro | 2,0 / 4,0 / 1,6 s |

Os parâmetros calibrados (ângulos de pescoço, cabeça, antebraço, asas, juntas da perna) ficam em `review/l2/manifesto_L2.json` (`_calibracao`).

**QA** (`review/l2/qa_L2.json`, todas as amostras de 30 Hz; linha de base idle_loop e roar no mesmo arquivo):

| | Linha de base | Lote 2 |
|---|---|---|
| Emenda dos loops | idle 0° | Alerta, Comer, Deitado 0° |
| Salto máximo por amostra | roar 20,6° (dedo da asa), idle 0,5° | Ameaca 20,6° (o do roar), Morte 11,4°, ReacaoGolpe 8,2°, Comer 7,5°, Ferrão 7,4°, Levantar 7,4°, Deitar 4,2° |
| z mínimo da malha | idle −0,02, roar −0,08 | −0,02 em todos, exceto Deitado −0,03, Ameaca −0,08 (do roar) e Comer −0,14 (ponta da mandíbula na mordida e calcanhar no agachamento) |
| Autointerseções reais (máx.) | idle 799 | em pé 772–814; **deitado 1.141–1.156** |

- **Deitado:** as ~370 interseções a mais vêm da perna dobrada (canela na coxa e na barriga), escondidas sob o corpo nas vistas lateral e 3/4. Não foi corrigido: exigiria correctives ou pesos novos na perna.
- Nos clipes que deitam, os dedos avançam ~2,5 studs (o pé se acomoda sob o corpo). O pé apoiado se move por isso, e não por escorregar na locomoção.
- Ângulos e tempos são **PROPOSTA** visual. Não definem dano, alcance, janelas de reação nem a toxina do ferrão.

**Evidências** (rótulo com clipe, quadro e vista; câmera fixa; humano de 5,5 studs):
- `review/L2_folha_ferrao.png`, `review/L2_folha_reacoes.png`, `review/L2_folha_descanso.png`;
- `review/L2_<Clipe>.mp4` (15 fps; lateral em cima, 3/4 embaixo).

**Ainda não feito:** Start/Stop, GuardaNinho, PairarCurto, Empoleirar, VooBatido próprio, montaria (7), habilidades (aguardam elemento e kit), exportação, JSON e Studio.

## Descanso v2: Deitar / Deitado / Levantar corrigidos (05/11/2026; ACEITO pelo usuário em 06/11/2026 com o residual da prega)

Arquivo: `Wyvern_E7_clipes_L2b.blend` = `Wyvern_E7_clipes_L2.blend` (preservado) com **só** estas 3 actions regravadas.
- Script próprio: `build/09_descanso_v2.py` (usa `08_base.py` sem alteração; não regrava o lote). Parâmetros escolhidos por busca medindo as interseções da malha: joelho 1,5 e jarrete 2,8 para fora do quadril, recuo do corpo 2,6, queda 4,25 (barriga no chão, como na v1), descida 0,3 s depois do recuo. Pescoço, cabeça, asas e cauda: ângulos da v1 (`manifesto_L2.json`), cauda 0,3° mais alta.
- Diagnóstico: `build/09a_diag_descanso.py` (todos os quadros a 30 Hz; interseções reais classificadas por par de ossos e visibilidade por raios vindos de cima do chão; trajetória dos pés; emendas). Renders: `build/09b_render_diag.py` (marcas vermelhas nas interseções com perna, closes das pernas, vista de baixo com arame, modo sequência). Não-interferência: `build/09d_comparar_actions.py`.

**M0 (v1) — causas encontradas** (`review/d2/diag_antes.json`):
1. Pé carregado deslizando: os dedos avançavam ~2,4 studs com o pé no chão (até 2,4–3,0 studs/s no Deitar/Levantar). Com o quadril onde está, a perna só dobra se os pés forem à frente.
2. Penetrações: joelho entrando na lateral da barriga (coxa×spine_02, até 0,71 visível) e canela na coxa junto ao jarrete (0,54).
3. Emendas: Levantar terminava num quadro do idle diferente do 0 (ponta da cauda saltava 9,3 studs); respiração do Deitado não valia zero no início (0,17).

**Correção:**
- pés **plantados**: a ponta dos dedos fica no ponto do idle; quem se move é o corpo, que senta **para trás** 2,6 studs sobre os pés (como uma ave) e volta no Levantar;
- perna **aberta** (coxa gira no eixo da frente): o joelho sai da barriga;
- transição por **interpolação dos ângulos** da perna (dobra natural) + IK só para manter o dedo plantado;
- Levantar termina no quadro 0 do idle; respiração só ergue dorso/cabeça e vale zero em t = 0.

| (todos os quadros) | v1 | v2 |
|---|---|---|
| Velocidade máx. do pé apoiado | 2,4–3,0 studs/s | 0,19–0,32 studs/s |
| Emendas idle→Deitar→Deitado→(loop)→Levantar→idle | até 9,3 studs / 8,4° | 0 / 0° (as cinco) |
| z mínimo da malha | −0,032 | −0,022 (= idle) |
| Penetração da perna, máx. (Deitar / Deitado / Levantar) | 0,87 / 0,72 / 0,84 | 0,47 / 0,37 / 0,47 |
| Idem, só casos visíveis | 0,71 / 0,72 / 0,76 | 0,46 / 0,33 / 0,45 |
| Casos visíveis com perna, máx. por quadro | 157 / 157 / 156 | 143 / 142 / 145 (idle: 35) |

- **Preservação:** as 19 outras actions são idênticas por hash dos keyframes (`review/d2/actions_L2_vs_L2b.json`, `actions_L1_vs_L2b.json`); malha (9.018 vértices, 11.980 faces), pesos, 61 ossos, material, 5 imagens e shape keys idênticos ao L2.
- **Não resolvido (residual visível):** a dobra **canela × coxa** (e canela × flanco) continua cruzando a malha em até ~0,46 stud de perto, nas vistas laterais/close (`review/D2_*_antes_depois.png`). É volume de malha: a coxa e a canela do Ashwing são grossas demais para dobrar tanto sem se tocar, e nenhuma pose testada (busca com queda 3,25–4,25, joelho 0–2,4, jarrete 0–2,8, peito, tempos) eliminou isso com a barriga no chão.
- **Proposta (não executada, precisa de autorização):** ajuste **local de pesos** na prega posterior da coxa e anterior da canela (os dois lados), para a pele da prega acompanhar a dobra em vez de se cruzar. Shape keys corretivas não servem para o Roblox, que, pelo que sei (a confirmar), não toca shape keys em malha com esqueleto fora do rosto. Impacto: todos os clipes que dobram a perna precisariam ser revalidados (walk, Corrida, Viradas, takeoff, Pouso, Comer, Morte e o descanso).

**Evidências:** `review/D2_deitado_antes_depois.png`, `review/D2_deitar_antes_depois.png`, `review/D2_levantar_antes_depois.png` (v1 à esquerda, v2 à direita; mesma câmera, instante equivalente); `review/D2_conjunto_{lado,frente,tres4,perna_L}.mp4` (Deitar → Deitado ×2 → Levantar; v1 em cima, v2 embaixo; 15 fps; a v1 termina antes e segura o último quadro).

## Pesos locais das pregas (W1, 05/11/2026): tentativa NÃO aplicada

Autorizado: ajustar só pesos das pregas das pernas. Resultado: **os pesos não resolvem**; nenhuma versão nova foi gravada (o L2b segue como base). As tentativas existem só como cópias de rascunho fora do repositório.
- M0: `build/10a_m0_prega.py` → `review/w1/m0_descanso_L2b.json` (todos os quadros de Deitar/Deitado/Levantar; 693 vértices envolvidos, 287 com profundidade ≥ 0,05). Pares visíveis piores: coxa × spine_02 (barriga/flanco) 0,46; canela × spine_02/spine_01 (flanco) 0,43; canela × coxa (joelho) 0,35–0,37; canela × pé (jarrete) 0,27–0,29. Os vértices ficam a ~1–1,9 do joelho, ~1 do jarrete e ~1,6–3 do quadril (repouso).
- Estrutura: 61 grupos (todos ossos), máx. 4 influências, pesos normalizados, Armature sem preservar volume.
- Tentativa: `build/10b_pesos_prega.py` — seleção reproduzível (vértices do M0 soldados pelas costuras + 2–3 anéis, só vértices que já usam ossos da perna [+ pelve/spine_01/02 na variante "flanco"]), suavização laplaciana dos pesos só dentro dela, máscara 1→0 até a borda, 4 influências, normalizado; diferença fora da seleção = 0. Avaliação por skinning linear próprio (erro vs Blender 4e-6).

| Deitado (vis. máx.) / Deitar / Levantar | L2b | A: 406 vértices, só perna | B: 598 vértices, com flanco |
|---|---|---|---|
| Penetração visível máx. | 0,33 / 0,44 / 0,44 | 0,34 / 0,43 / 0,48 | 0,34 / 0,41 / 0,47 |
| Deslocamento máx. no idle (efeito colateral) | — | 0,19 | 0,95 |
| Idem walk / Corrida / takeoff / Morte | — | 0,27 / 0,21 / 0,26 / 0,31 | 1,53 / 1,70 / 1,23 / 1,74 |

Outras variantes da busca (`review/w1/busca1.json`: mais iterações) pioraram o descanso (até 0,64). Efeitos por clipe: `review/w1/efeitos_A.json`, `efeitos_B.json` (todos os clipes existentes, passo 4 quadros, antes × depois).
- **Causa:** o contato é de **volume ao longo da canela** (encostada na coxa e no flanco quando a perna dobra ~160°), não uma prega de pele junto à articulação; com skinning linear, misturar pesos só arrasta a pele de um osso para o outro sem abrir espaço. A variante B até reduz alguns contatos em transição, mas muda o corpo **em pé** em até ~1 stud (regressão).
- **Linha de base encontrada (não causada aqui):** com o mesmo método, os clipes originais do Ashwing já têm contato visível de perna: walk_loop 1,07, VirarDireita 1,12 (derivada do walk), Corrida 0,78, Morte 0,89, takeoff/Pouso 0,34, Comer 0,40 (Comer z mín. −0,135 inalterado).
- Evidências: `review/W1_deitado_L2b_pesoA_pesoB.png` (closes das duas pernas com textura e em cinza neutro, vista de baixo com arame; marcas = interseções) e `review/W1_transicoes_L2b_pesoA_pesoB.png` (Deitar f38,4 e Levantar f16,8).
- **Alternativas (aguardam decisão):**
  1. *Pose:* descanso "sentado sobre os jarretes" (quadril ~1 stud mais alto, peito apoiado) — só keyframes dos 3 clipes; a busca mostrou menos contato, mas não zero, e a barriga não encosta atrás.
  2. *Malha (muda o E6 aprovado):* afinar localmente a parte de trás da coxa e a frente da canela no repouso para os volumes caberem dobrados — exige reaprovar o modelo e revalidar todos os clipes.
  3. *Rig:* 1–2 ossos auxiliares por perna (ex.: músculo da coxa que se afasta na dobra) — aumenta o rig (61 → 63–65) e exige pesos novos e teste no Roblox.
  4. *Aceitar o residual* do L2b, que já é menor que o contato pré-existente da caminhada original.

## Pose sentada sobre os jarretes (S1, 05/11/2026): testada, NÃO adotada

Alternativa 1 escolhida pelo usuário. Script `build/11_descanso_sentado.py` (derivado do 09; parte do L2b; só as 3 actions; recalibra peito, cauda, pescoço/cabeça, antebraço e ombro na malha). Nenhuma versão oficial foi gravada: o L2b segue como base. Candidatos só em rascunho; manifestos em `review/s1/`.
- **Peito até o chão** (quadril mais alto 2,8–3,6 com a coluna inclinada 15–30° até a barriga dianteira tocar): a barriga desce **sobre os joelhos** — surgem contatos novos coxa/canela × spine_02 (até 0,95–1,06 visível) e as asas afundam até −0,98. Pior que o L2b.
- **Peito pouco inclinado** (0–8°, quadril 3,2–3,6): o contato visível cai para **0,30–0,31** (L2b: 0,33), mas a barriga fica **1,0–1,5 stud acima do chão** — lê como agachado, não deitado — e a prega canela × coxa continua visível.
- Medição: mesma função do L2b (interseções reais com perna, visibilidade por raios de cima do chão), pose Deitado calibrada.
- Evidência: `review/S1_deitado_L2b_sentados.png` (L2b | sentado_baixo: q 4,25, peito automático 15° | sentado_alto: q 3,2, peito 8°; lado, frente, 3/4 e closes das duas pernas, marcas = interseções).
- **Conclusão:** com esta malha e este rig, nenhuma pose de descanso com a barriga no chão evita a prega canela × coxa/flanco; pesos (W1) também não. Restam: afinar a malha (muda o E6), ossos auxiliares (rig 61 → 63–65) ou aceitar o residual do L2b.

## Afinar a malha da perna (M1, 05/11/2026): candidato NÃO adotado

Alternativa escolhida pelo usuário. Script `build/12_afinar_perna.py` (parte do L2b; só posições da malha; topologia, UV, pesos, ossos e actions intactos; Basis e as 2 shape keys recebem o mesmo delta; normais customizadas recalculadas só nos vértices movidos, demais com diferença ≤ 0,0005; nenhum vértice fora da perna é movido).
- **Método 1 (descartado):** empurrar cada vértice para fora da superfície que ele cruza (6 iterações). Oscila e dobra a pele sobre ela mesma (coxa×coxa, canela×canela até 1,75): `review/m1/afinar_t1.json`.
- **Método 2 (radial suave):** cada vértice de coxa/canela/pé recua em direção ao eixo do próprio osso, só no lado voltado (na pose Deitado) para a canela, a coxa ou o corpo, com proximidade de 3–4,5 studs e suavização. Busca: `review/m1/busca_radial.json`, `busca_radial2.json`.

| Penetração visível máx. (Deitar / Deitado / Levantar) | L2b | K 0,35 | K 0,5 (alcance 4,5) | K 0,65 |
|---|---|---|---|---|
| | 0,46 / 0,33 / 0,45 | 0,41 / 0,33 / 0,40 | 0,39 / 0,32 / 0,39 | 0,41 / 0,35 / 0,42 |
| Deslocamento máx. da malha | — | 0,34 | 0,57 (médio 0,07; 1.195 vértices) | 0,74 |

- **K 0,5** (gravado só como candidato em `Wyvern_E8_perna_afinada_CANDIDATO.blend`, não é base): silhueta em pé quase igual; contatos da perna no idle caem de 40 para 8 marcas (0,16 → 0,05); no descanso as marcas caem ~10–35%, mas a prega continua visível (Deitado 0,37 → 0,41 no render de marcas). Demais clipes NÃO revalidados (candidato não adotado).
- **Causa do residual:** o pior par restante é coxa × flanco (spine_01/02) junto ao quadril e canela × flanco: é a pele contínua da articulação do quadril, dobrada além de 90°. Afinar só a perna não desfaz essa prega; mexer no flanco muda a silhueta do corpo.
- Evidência: `review/M1_perna_afinada_L2b.png` (L2b | afinada; idle e Deitado; lado/frente e closes das pernas em cinza neutro e com textura; marcas = interseções).
- **Conclusão das quatro frentes (pose, pesos, pose sentada, malha da perna):** nenhuma elimina a prega canela/coxa × flanco com a barriga no chão. Restam: ossos auxiliares (rig 61 → 63–65), afinar também o flanco (muda o corpo), ou aceitar o L2b.

## Comer corrigido (06/11/2026; APROVADO pelo usuário em 06/11/2026)

Arquivo: `Wyvern_E7_clipes_L2c.blend` = `Wyvern_E7_clipes_L2b.blend` (preservado) com **só** o Comer regravado. Script próprio `build/13_comer_v2.py` (usa `08_base.py` sem alterar); M0 `build/13a_m0_comer.py`.
- **M0 (L2b):** a cabeça e a mandíbula **não** afundavam (z mín. da cabeça 0,22). Afundavam o **pé esquerdo** (até −0,136, em 55 de 91 quadros: o agachamento prendia só a bola e a ponta do pé e a IK girava o pé, chapando o jarrete) e a **ponta da cauda** (até −0,057 no balanço mais baixo). `review/c1/m0_Comer_L2b.json`; idle como base: `m0_idle_loop_L2b.json` (−0,022).
- **Correção:** coxa (2 eixos) + canela levam o jarrete exatamente ao ponto do idle e o pé/dedo recebem a orientação de mundo do idle — o pé fica idêntico ao do idle e só coxa/canela absorvem o agachamento de 1,5; base da cauda +0,25°. Pescoço, cabeça, asas, mordida, puxão e tempo (3,0 s, loop) = v1.

| Comer | L2b | L2c |
|---|---|---|
| z mínimo da malha | −0,136 (pé E) | −0,022 (= idle) |
| Quadros abaixo de −0,03 | 55 de 91 | 0 |
| Cauda (mín.) | −0,057 | +0,053 |
| Emenda do loop / salto máx. | 0° / 7,5° | 0° / 7,5° |
| Pé apoiado | 0,01 studs/s | 0,00 studs/s |
| Contato visível da perna (máx.) | 0,40 (jarrete: canela × pé) | 0,39 (joelho: canela × coxa) |

- **Troca registrada:** com o pé como no idle, a dobra do agachamento fica toda no joelho; a prega canela × coxa (mesma família aceita no descanso) aparece no close do joelho com profundidade igual à do jarrete na v1. Não é piora de profundidade, mas é visível de perto.
- **Preservação:** as outras 21 actions idênticas por hash (`review/c1/actions_L2b_vs_L2c.json`); malha, pesos, 61 ossos, material e shape keys idênticos.
- **Evidências:** `review/C1_comer_antes_depois.png` (f19,2 = pior quadro da v1 e f43,2; lado, 3/4, pés com textura e em cinza, joelho; L2b à esquerda), `review/C1_comer_{lado,frente,tres4,pe_L,joelho_L}.mp4` (2 ciclos; L2b em cima, L2c embaixo), QA `review/c1/qa_Comer_L2b.json` / `qa_Comer_L2c.json`, contatos `review/c1/diag_Comer_*.json`.

## Lote 3 de clipes: transições, voo e ninho (06/11/2026; APROVADO em 06/11/2026 junto com o L3b)

Arquivo: `Wyvern_E7_clipes_L3.blend` = base aprovada `Wyvern_E7_clipes_L2c.blend` + 6 actions novas (as 22 anteriores idênticas por hash: `review/l3/actions_L2c_vs_L3.json`; malha/pesos/61 ossos/material/shape keys idênticos).
- Script: `build/14_clipes_lote3.py -- 08_base.py saida manifesto`; emendas: `build/14b_emendas.py`. Fontes: idle_loop, fly_loop (Ashwing) e a Corrida do lote 1.

| Clipe | Como foi feito | Duração |
|---|---|---|
| Arrancada (único) | idle → Corrida com impulso (peito mergulha, cauda contrapeso); termina exatamente no quadro 0 da Corrida | 0,72 s |
| Frenagem (único) | Corrida → idle, peso para trás e asas abrindo um pouco; termina exatamente no quadro 0 do idle | 0,9 s |
| VooBatido (loop) | fly_loop 18% mais rápido, asas 15% mais amplas, corpo 5° à frente | 0,68 s |
| PairarCurto (loop) | batidas do fly_loop com o corpo empinado 30° (pivô na pelve, o corpo não desloca), pernas penduradas à frente, cauda como leme, sobe a cada batida | 1,0 s |
| Empoleirado (loop) | agachado 0,6 com pés iguais ao idle, balanço lateral; asas meio abertas compensam (sobe a do lado que cai); cauda contrapeso | 3,0 s |
| GuardaNinho (loop) | agachado 1,2, asas abertas e baixas cobrindo o ninho (calibradas ≥ 0,75 do chão), cabeça baixa varrendo, um sibilo por ciclo, cauda curvada com ferrão meio armado | 6,0 s |

- Pés no chão: agachamentos com jarrete no ponto do idle e pé na orientação do idle (como o Comer aprovado); nas misturas apoio × balanço da Arrancada/Frenagem, o pé que passaria do chão é erguido por IK só o déficit.
- **Emendas** (`review/l3/emendas_L3.json`): idle→Arrancada, Arrancada→Corrida, Corrida→Frenagem e Frenagem→idle = 0° / 0 studs. Loops fecham exatamente (último quadro = primeiro).

**QA** (`review/l3/qa_L3.json` e `qa_L3_guarda.json`; linha de base fly_loop e Corrida no mesmo arquivo):

| | Linha de base | Lote 3 |
|---|---|---|
| z mínimo (terra) | idle −0,022; Corrida −0,009 | Arrancada −0,042; Frenagem −0,024; Empoleirado −0,022; GuardaNinho −0,022 |
| Salto máx. por amostra | Corrida 70°, walk 66° | Arrancada 60°, Frenagem 65° (balanço da perna); voo ≤ 15°; Empoleirado 0,5°; GuardaNinho 4° |
| Autointerseções (máx.) | Corrida 1.021, fly 265, idle 799 | Arrancada 961, Frenagem 874, VooBatido 277, PairarCurto 300, Empoleirado 800, GuardaNinho 376 |

- "Emenda" de 2° no VooBatido é artefato de amostragem (como os 22° da Corrida aprovada): o laço é exato.
- Voo feito no lugar, na altura do fly_loop: no PairarCurto a ponta da asa/cauda passa até −5,7 abaixo do plano z=0 no corpo empinado; não é contato.
- Velocidades, ângulos e tempos são **PROPOSTA** visual.
- **Evidências:** `review/L3_folha_terra.png`, `review/L3_folha_ar.png`, `review/L3_folha_ninho.png`; `review/L3_<Clipe>.mp4` (lateral em cima, 3/4 embaixo; loops curtos repetidos 3×).
- **Ainda não feito:** Rasante e GuinadaEvasiva/AtaqueAéreo (ficam com as habilidades, que aguardam elemento e kit), montaria (7), exportação, JSON e Studio.

## Subida, Descida e Mergulho em voo (06/11/2026; APROVADO pelo usuário em 06/11/2026)

Base dos clipes até a montaria: `Wyvern_E7_clipes_L3b.blend` (31 actions: 6 originais + lote 1 + lote 2 + lote 3 + subida/descida/mergulho). L2c e L3 ficam como histórico.

Arquivo: `Wyvern_E7_clipes_L3b.blend` = `Wyvern_E7_clipes_L3.blend` (preservado) + 3 loops. Script `build/15_subida_descida.py`. As 28 actions anteriores idênticas por hash (`review/l3b/actions_L3_vs_L3b.json`); malha/pesos/ossos idênticos. Inclinação com pivô na pelve (o corpo não desloca em relação aos outros clipes de voo, feitos no lugar).

| Clipe | Como foi feito | Duração |
|---|---|---|
| Subida (loop) | batidas do fly_loop 10% mais rápidas e 20% mais amplas, nariz 22° para cima, cabeça acompanhando, pernas recolhidas, cauda alinhada | 0,73 s |
| Descida (loop) | Planeio com nariz 15° para baixo, asas recuadas 12° e em V leve, cabeça olhando à frente, pernas recolhidas | 2,4 s |
| Mergulho (loop) | nariz 45° para baixo, asas meio fechadas (55% para a dobra do idle) e recuadas, tremor no vento, cauda reta, pernas recolhidas | 1,2 s |

- QA (`review/l3b/qa_L3b.json`, base fly_loop e Planeio): loops exatos ("emenda" de 4,7° da Subida é artefato de amostragem); salto ≤ 14° (fly 11°); autointerseções Subida 274 (fly 265), Descida 213 (Planeio 245), Mergulho 429 (asas meio dobradas; o idle com asas dobradas tem ~800). Voo no lugar: z < 0 da ponta da asa/cauda não é contato.
- Evidências: `review/L3b_folha_subida_descida.png`; `review/L3b_{Subida,Descida,Mergulho}.mp4` (lateral em cima, 3/4 embaixo).

## Montaria: 7 clipes da criatura (06/11/2026; APROVADO pelo usuário em 06/11/2026)

**Base atual dos clipes: `Wyvern_E7_clipes_L4.blend`** (38 actions). L3b fica como histórico.

Arquivo: `Wyvern_E7_clipes_L4.blend` = base aprovada `Wyvern_E7_clipes_L3b.blend` (preservada) + 7 actions. Script `build/16_montaria.py`; estabilidade do dorso: `build/16b_sela.py`. As 31 actions anteriores idênticas por hash (`review/l4/actions_L3b_vs_L4.json`); malha/pesos/61 ossos/material/shape keys idênticos. Animações do cavaleiro R15, sela, encaixe (Attachment) e regras de montaria **não** fazem parte desta etapa.

| Clipe | Como foi feito | Duração |
|---|---|---|
| RideIdle / RideWalk / RideRun / RideVirarEsquerda / RideVirarDireita (loops) | idle_loop / walk_loop / Corrida / Viradas com o **dorso estabilizado**: a rotação do osso da sela (spine_02, entre os ombros) é puxada para a média do ciclo (fica 35% do desvio) por contra-rotação em spine_01; pernas, raiz e pés intactos; cabeça um pouco mais alta | 3,0 / 1,07 / 0,72 / 1,07 / 1,07 s |
| Mount (único) | idle → agacha 2,2 (pés como no idle), peito baixa, asas sobem e abrem para liberar os flancos (simétrico: serve dos dois lados), segura ~0,8 s, levanta; termina exatamente no quadro 0 do RideIdle | 2,4 s |
| Dismount (único) | RideIdle → agacha e abre as asas → idle; termina exatamente no quadro 0 do idle | 2,0 s |

**Medições:**
- Sela (`review/l4/sela_L4.json`), desvio angular máximo do dorso em relação à média do ciclo: idle 1,5° → RideIdle 0,19°; walk 4,5° → 1,55°; Corrida 5,1° → 2,1°; Viradas 4,5° → 1,55°. A faixa vertical do ponto da sela fica igual à do clipe de origem (0,3–0,5 stud), porque vem das pernas, que não foram alteradas.
- Emendas (`review/l4/emendas_L4.json`): idle→Mount, Mount→RideIdle, RideIdle→Dismount, Dismount→idle = 0° / 0 stud.
- QA (`review/l4/qa_L4.json`): loops exatos; pés e saltos idênticos aos clipes de origem (walk 66°, Corrida 70°; a "emenda" de 22° do RideRun é o mesmo artefato de amostragem da Corrida aprovada); z mín. −0,06 (= walk) nos clipes de passo, −0,022 (= idle) nos demais; Mount/Dismount até 1.328 autointerseções (agachamento fundo + asas erguidas; mesma família de prega do joelho aceita no descanso).
- Evidências: `review/L4_folha_montar.png`, `review/L4_folha_ride.png`; `review/L4_<Clipe>.mp4` (lateral em cima, 3/4 embaixo).

## Demonstração do cavaleiro: subir, descer e montado (09/11/2026; APROVADA pelo usuário em 09/11/2026 — meio deitado, cabeça erguida, segurando no dorso, com física)

**Demonstração, não é a animação final do jogador.** Manequim de caixas com proporções de R15 (~5,5 studs; azul = corpo, laranja = mãos/pés). Script `build/17_demo_cavaleiro.py` (`medir` / `render`), usando `Wyvern_E7_clipes_L4.blend` **sem alterar** (o manequim não é salvo no .blend). Sela, lado oficial de entrada e regras de montaria continuam indefinidos.
- **Assento:** preso ao osso da sela (`spine_02`), acompanha o dorso nos clipes. Busca por posição (atrás das asas), altura sobre a pele (0,6–1,2 = espaço de uma futura sela), abertura das coxas (45–70°) e dobra do joelho (55–115°), avaliada no pior quadro de RideIdle + todos os quadros de RideWalk e RideRun. Escolha: y = 1.5, **1.2 stud acima da pele**, coxas 60°, joelho 115° (pernas dobradas para trás, estilo jóquei).
- **Montar_E / Montar_D** (com o clipe Mount): em pé ao lado do flanco → agacha → salto em curva por cima do flanco até o assento com a Wyvern agachada (t 0,8–1,25 s) → preso ao osso enquanto ela levanta. **Desmontar_E / Desmontar_D** (com o Dismount): preso → salta em curva para o lado → aterrissa agachado → em pé. Os dois lados são espelhados.
- **Sentado:** RideIdle, RideWalk, RideRun, RideVirarEsquerda, RideVirarDireita.

| Sequência | Folga mín. do corpo do manequim | Mãos/pés (apoio) | Distância mín. às asas | Quadros do corpo < −0,05 |
|---|---|---|---|---|
| Montar_E | -0.30 (BracoInf_D, t 0.93 s) | -0.67 | 0.93 | 2 de 37 |
| Montar_D | -0.19 (BracoInf_E, t 0.93 s) | -0.56 | 1.20 | 2 de 37 |
| Desmontar_E | -0.24 (BracoInf_D, t 0.80 s) | -0.64 | 1.04 | 2 de 31 |
| Desmontar_D | -0.19 (BracoInf_E, t 0.80 s) | -0.59 | 1.24 | 2 de 31 |
| Sentado_RideIdle | 0.33 (Canela_E, t 0.73 s) | -0.04 | 1.21 | 0 de 46 |
| Sentado_RideWalk | 0.29 (Canela_E, t 0.80 s) | -0.14 | 0.96 | 0 de 17 |
| Sentado_RideRun | 0.38 (Canela_E, t 0.40 s) | -0.04 | 0.95 | 0 de 11 |
| Sentado_RideVirarEsquerda | 0.12 (Canela_E, t 0.80 s) | -0.33 | 0.86 | 0 de 17 |
| Sentado_RideVirarDireita | 0.15 (Canela_D, t 0.13 s) | -0.29 | 0.93 | 0 de 17 |

- Folga = distância de pontos das caixas à pele, negativa se o ponto está dentro (voto de 6 raios); asas por distância sem sinal.
- **Montado: o corpo do manequim nunca entra na Wyvern**; só os pés encostam no flanco (como em estribos).
- **Subida/descida:** no início/fim do salto o antebraço do lado da subida apoia no flanco e entra até ~0,3 stud por 2 quadros; mãos e pés tocam a pele no apoio (esperado num salto apoiado).
- Evidências: `review/C2_folha_montar_E.png`, `review/C2_folha_sentado.png`; `review/C2_cav_<Sequência>.mp4` (lateral em cima, 3/4 embaixo); medições `review/c2/folgas_cavaleiro.json`; trajetórias das caixas por quadro `review/c2/trajetorias_cavaleiro.json` (referência para a futura animação R15).

- **Pegada no dragão (09/11/2026, pedido do usuário; substitui a alça provisória, removida):** o cavaleiro fica **meio deitado para a frente** (tronco 60°), **cabeça erguida olhando à frente** (pescoço compensa a inclinação; rosto 8° abaixo do horizonte) e **segura com as duas mãos no dorso da Wyvern**, 2.6 stud à frente do assento, a 0,7 de cada lado do eixo. O ponto de cada mão **acompanha a pele** (triângulo da pele sob a mão, coordenadas baricêntricas); a cada quadro os braços (e o tronco ±3°) são reajustados por busca. Erro máximo mão × ponto de pegada: **0.203 stud**.
- **Física (pedido do usuário):** a aceleração do assento em cada quadro (segunda diferença da posição, no espaço do assento) move o tronco por **mola amortecida** (2.2 Hz, amortecimento 0.45): subida do dorso comprime (tronco cai à frente), arranque à frente joga para trás, puxão lateral rola o tronco para fora; atraso e assentamento vêm da mola (nos loops, 3 voltas para o regime e o último quadro = primeiro). A aterrissagem no Montar dá um impulso de compressão. A **cabeça estabiliza o olhar**: compensa 80% da inclinação/rolagem do assento e do tronco. Amplitudes (tronco à frente/trás, rolagem): RideIdle [0.21, 0.0]; RideWalk [4.65, 2.42]; RideRun [8.0, 6.18]; Viradas [4.73, 2.4]; Montar [2.47, 0.0]; Desmontar [4.37, 0.0] (graus).

| Sequência | Folga mín. do corpo | Quadros do corpo < −0,05 | Distância mín. às asas |
|---|---|---|---|
| Montar_E | -0.30 (BracoInf_D) | 2 de 37 | 0.88 |
| Montar_D | -0.19 (BracoInf_E) | 2 de 37 | 0.88 |
| Desmontar_E | -0.24 (BracoInf_D) | 2 de 31 | 0.89 |
| Desmontar_D | -0.19 (BracoInf_E) | 2 de 31 | 0.89 |
| Sentado_RideIdle | 0.10 (BracoInf_E) | 0 de 46 | 0.87 |
| Sentado_RideWalk | -0.01 (BracoInf_D) | 0 de 17 | 0.83 |
| Sentado_RideRun | -0.31 (BracoInf_E) | 2 de 11 | 0.75 |
| Sentado_RideVirarEsquerda | -0.06 (BracoInf_D) | 1 de 17 | 0.78 |
| Sentado_RideVirarDireita | -0.07 (BracoInf_E) | 1 de 17 | 0.86 |
- Montado parado: nada do corpo entra na Wyvern. No passo/corrida/viradas o **antebraço** encosta no dorso em 1–2 quadros por ciclo (até −0,31 na corrida): contato de apoio de quem está agarrado.
- Evidências: `review/C2_folha_pegada.png` (close que acompanha o cavaleiro), `review/C2_folha_montar_E.png`, `review/C2_folha_sentado.png`, `review/C2_cav_*.mp4` e `C2_cav_{Montar_E,Sentado_RideRun,Sentado_RideWalk}_close.mp4`.

## Sela da Wyvern: só o assento (09/11/2026; APROVADA pelo usuário — materiais seguem [PROPOSTA] até regra oficial)

Arquivo: `Wyvern_S1_sela.blend` = `Wyvern_E7_clipes_L4.blend` (preservado) + objeto `Wyvern_Sela` (filho do rig, modificador Armature). Script `build/18_sela_wyvern.py` (método das selas aprovadas do Leão e do Crocodilo); QA `build/18b_qa_sela.py`. Nada da Wyvern foi alterado.
- **Peças:** manta que veste o dorso (com debrum), aba, **assento** moldado (cabeça baixa na frente, porque o cavaleiro se debruça e segura no dorso; patilha atrás), **cinta em volta da base da cauda** (atrás das pernas: na frente das coxas a cilha bateria nas pernas e nas asas) com 2 argolas. **Sem alça** (decisão do usuário: o cavaleiro segura no dorso).
- **Posição:** sob o quadril do cavaleiro da demonstração aprovada (assento preso a `spine_02`); assento 0.27 mais alto para encostar no cavaleiro. Manta na largura do dorso e terminando antes da dobra da base da cauda.
- **Materiais [PROPOSTA]** (Montanhas Altas): Couro (básico) no assento, aba e cinta; **Pele de Íbex** na manta; **Tendão de Íbex** no debrum e na costura; **Ferro Montanhês** nas argolas. Sem material dracônico (o elemento da Wyvern não foi decidido).
- **Malha:** 4224 triângulos, 2148 vértices, 4 materiais; pesos copiados da pele só de `root`, `pelvis`, `spine_01..03` e `tail_01` (asas, pernas, pescoço e o resto da cauda não mexem a sela), até 4 influências.
- **QA em todas as 38 actions** (`review/s2/qa_sela.json`; passo 2,4 quadros, clipes de montaria a cada 1,6):
  - sela dentro da pele: pior **-0.068** fora da ferroada (a cinta nas curvas aéreas); na **FerraoAtaque**, no auge do golpe, **-0.136** no fundo do assento (a base da cauda dobra para cima sob a sela);
  - pele dentro da sela: no máximo **0.039**;
  - cavaleiro da demonstração × sela: quadril do cavaleiro 0,44–0,61 acima do assento no RideIdle/Walk/Run (sentado e encostado, descontada a coxa); caixas do manequim dentro da sela até 0,19 nas viradas e na subida/descida (coxa na borda do assento quando o tronco rola).
- **Correções durante o trabalho:** a manta escorria pelos lados (onde o raio não achava pele, o mapa de alturas caía; agora os buracos herdam o vizinho e a manta tem a largura do dorso); o assento ficava baixo (cavaleiro flutuando ~0,3); a borda de trás da manta entrava 0,6 na pele na ferroada (encurtada).
- **Evidências:** `review/S2_folha_sela.png` (RideIdle lado/3/4/cima, corrida, ferroada, deitado, planeio, Mount), `review/S2_folha_sela_cavaleiro.png`, `review/S2_sela_cav_*.mp4` (cavaleiro da demo sentado na sela).
- **Textura de jogo e GLB (09/11/2026, APROVADOS pelo usuário em 10/11/2026):** `build/18c_textura_glb_sela.py` (adaptado do script aprovado do Leão, `s1_07_textura_glb.py`): UV única, bake Cycles **1024** (cor, normal tangente OpenGL, rugosidade, metal → empacotado em metal/rugosidade glTF G=rug, B=metal), material único `M_Wyvern_Sela_Jogo`, pesos ≤ 4 influências normalizados. Saída em `export/sela/` (fora do git): `Wyvern_Sela.glb` (1,56 MB, só sela + 61 ossos do rig, sem animação, texturas embutidas), PNGs `T_Wyvern_Sela_{Cor,Normal,MetalRug}.png` e `Wyvern_Sela_Jogo.blend`.
  - Validação por reimportação (`build/18d_validar_glb_sela.py` → `review/s2/valida_glb_sela.json`): **4224 triângulos**, **61 ossos** (= rig), máx. **3 influências** por vértice (soma 1,0), 3 texturas embutidas, **desvio de posição em repouso 0.0** contra a sela original (3427 vértices no GLB por duplicação nas costuras, 2148 no original).
  - Comparação procedural × jogo (mesma câmera): `review/S2_sela_procedural_x_jogo.png` — iguais à vista.
  - Os ossos mantêm os nomes do rig do Ashwing; a renomeação para o jogo segue a exportação da própria Wyvern (pendente). O GLB não contém a malha do Ashwing.
- **Pendentes:** teste no Roblox/Studio (com a exportação da Wyvern).

## Lote 5 de clipes: realismo / vida parada (12/11/2026, APROVADO pelo usuário 12/11 após Farejar v3) [PROPOSTA]

Arquivo: `Wyvern_E7_clipes_L5.blend` = `Wyvern_E7_clipes_L4.blend` (preservado) + 7 actions = **45 actions**. Script `build/19_clipes_lote5.py` (usa `08_base.py`). As 38 actions anteriores são idênticas por hash (`review/l5/actions_L4_vs_L5.json`); malha, pesos e rig não foram tocados. Ângulos e tempos são proposta visual; nada de regra de jogo.

| Clipe | s | O que faz |
|---|---|---|
| SacudirCorpo | 3,0 | sacode como cão molhado (~4 Hz): onda cabeça → tronco (rola) → cauda; asas tremem por último |
| AlisarAsaEsquerda / AlisarAsaDireita | 6,0 | estende a asa para o lado e passa o focinho no braço/membrana com mordiscadas |
| Espreguicar | 6,0 | abre as asas devagar e para cima, peito à frente, pescoço alongado, cauda sobe, tremor e bocejo |
| Farejar | 6,0 | abaixa o focinho até perto do chão à frente e cheira no centro, à esquerda e à direita; boca fechada (mandíbula +18°, porque no repouso do modelo a boca já fica entreaberta), sem fungadas, só um balanço suave da cabeça para os lados (ajuste do usuário 12/11) |
| OlharVolta | 6,0 | corpo parado; só pescoço/cabeça viram à esquerda (inclina a cabeça), à direita e voltam |
| DecolagemPenhasco | 2,4 | agacha na borda, lança-se de bico para baixo com as pernas para trás, abre as asas e termina no quadro 0 do Planeio |

- Todos começam no quadro 0 do idle; os seis de chão também terminam nele (duração múltipla do idle de 3 s). Emendas idle↔clipe e Decolagem→Planeio: **0°** (`review/l5/emendas_L5.json`).
- Pescoço/cabeça guiados por IK do focinho (`breath_socket`) com **modos distribuídos** (curvar, curva em S, virar, cabeça), para a curva ficar única e suave. O IK osso a osso foi descartado: dava zigue-zague e saltos de 30°.
- Pés: inclinar o corpo ANTES de agachar (o agachamento replanta jarrete e pé no ponto do idle); na Decolagem os pés soltam a borda aos poucos (0,85 → 1,1 s) e o corpo sobe o que faltar no impulso.
- **QA** (`review/l5/qa_L5.json`): z mínimo da malha **-0.022** em todos os clipes de chão (= idle), pés apoiados parados (0,0 stud/s); maior salto por amostra: SacudirCorpo 12.79° (cabeça, sacudida de 4 Hz), DecolagemPenhasco 12.9° (coxa, chute do impulso), demais ≤ 6.22°; autointerseções reais 783–813 (idle = 799: a prega já aceita).
- A Decolagem é no lugar, como os outros clipes de voo: a queda e o deslocamento ficam com o jogo. Depois do impulso as pernas ficam acima do chão do quadro (o penhasco não está modelado).
- **Evidências:** `review/L5_folha_vida.png`, `review/L5_folha_decolagem.png`, `review/L5_<Clipe>.mp4` (lateral em cima, 3/4 embaixo).
- **Pendentes:** aprovação do usuário; Roblox/Studio não testado (exportação da Wyvern pendente, com conversão da convenção nova do Import 3D).

## Lote 6 de clipes: realismo 2 (12/11/2026, APROVADO pelo usuário 12/11) [PROPOSTA]

Arquivo: `Wyvern_E7_clipes_L6.blend` = `Wyvern_E7_clipes_L5.blend` (preservado) + 4 actions = **49 actions**. Script `build/20_clipes_lote6.py` (usa `08_base.py`; modo `lab:<pasta>` renderiza poses soltas para escolher parâmetros). As 45 actions anteriores são idênticas por hash (`review/l6/actions_L5_vs_L6.json`). Ângulos e tempos são proposta visual; nada de regra de jogo.

| Clipe | s | O que faz |
|---|---|---|
| AsasEscudo | 6,0 | encolhe, recolhe a cabeça e cruza as asas dobradas à frente do peito (capa); tremor leve; volta |
| SecarAsas | 6,0 | abre as asas ao sol (como corvo-marinho), duas batidas lentas, sacode a membrana, fecha |
| AgarrarPresa | 6,0 | pisa 2,5 studs à frente com a pata direita (prende a presa) e entra na postura do Comer (aprovado): morde e puxa a ~11 studs à frente; solta e volta. Presa não modelada (a presa entre a pata e a boca mede ~6 studs) |
| AndarQuatroApoios | 1,6 (loop) | anda apoiando o pulso/polegar das asas no chão (como morcego/pterossauro): pernas do walk_loop em câmera lenta (6,7 st/s na esteira), corpo inclinado 24° na pelve, asas por IK com a parte mais baixa da asa no chão durante o apoio |

- Emendas idle↔clipe e a costura do loop: **0°** (`review/l6/emendas_L6.json`).
- **QA** (`review/l6/qa_L6.json`): z mínimo −0,022 (= idle) nos três de 6 s; AndarQuatroApoios −0,06 (igual ao walk_loop); pés de apoio parados nos três de 6 s; no andar os pés e os pulsos recuam juntos a 6,9 st/s (esteira, como o walk_loop a 9,9). Maior salto por amostra: AsasEscudo 4,1°, SecarAsas 7,7°, AgarrarPresa 7,5°, AndarQuatroApoios 46° na coxa (o walk_loop aprovado tem 66° na mesma fase).
- Lições: a perna do andar inclinado parte da orientação de MUNDO da coxa do walk_loop (IK direto torcia a coxa em 150–180°); dois quadros do andar ficam na pose de partida (jarrete a 0,16 do alvo); a pata do AgarrarPresa parte da solução do quadro anterior; o modelo é assimétrico (a junta da asa D apoia ~0,7 mais baixa que a E), por isso a altura do apoio é calibrada por lado; asas por cima da pose aberta do voo não servem como escudo (esticam para os lados).
- AsasEscudo tem mais autointerseções (até 1266, idle = 799) porque as asas dobradas se cruzam à frente do peito.
- **Evidências:** `review/L6_<Clipe>.mp4` (lateral em cima, 3/4 embaixo), `review/l6/folha_*.png`, laboratório em `review/l6/lab1..lab5/`.

## Limitações conhecidas

- (Até o E4.) O ferrão vem de uma malha de pouca resolução, com triângulos longos e irregulares. No E4 a transição ficou contínua, mas ainda se vê facetamento low-poly de perto. Restam 8 faces dobradas pequenas na ponta do gancho, as 8 da espícula original e algumas interseções internas nos ciclos (2 a 7, no nível do E1). O estiramento p95 da UV na região subiu um pouco (3,08 → 3,51), porque o bulbo tem mais área que o losango original. **No E6** a fenda e a aba foram eliminadas e as penetrações zeraram. Fica o facetamento de malha leve, e as 8 faces novas da junção usam UV copiada dos vizinhos.
- Os olhos não foram recoloridos (o painel mostra olhos amarelos).
- A normal e a metal/rugosidade continuam as originais.
- Os 6 clipes originais (idle, walk, roar, bite, takeoff, fly), o lote 1 (7, aprovado) e o lote 2 (9; descanso do `Wyvern_E7_clipes_L2b.blend` aceito em 06/11/2026 com a prega residual coxa/canela × flanco de até ~0,46 stud de perto; Comer refeito e aprovado em `Wyvern_E7_clipes_L2c.blend`).
- Base dos lotes 1–2: `Wyvern_E7_clipes_L2c.blend`; base de todos os clipes até a montaria: `Wyvern_E7_clipes_L3b.blend`; **atual: `Wyvern_E7_clipes_L4.blend`** (lote 1 + lote 2 com descanso L2b e Comer corrigido; aprovada em 06/11/2026). L2/L2b ficam como histórico. `Wyvern_E8_perna_afinada_CANDIDATO.blend` NÃO é base (teste M1).
- Os scripts de revisão anteriores (até o 05b) trocavam só a action do rig, e as shape keys ficavam com os valores do "bite". Isso não afeta a região do ferrão, onde as correctives valem zero. Foi corrigido em 05/11 (slot KEY).
- O comprimento (~40) ainda passa dos ninhos de ~35. É uma pendência do usuário.
- Nada foi exportado para o Roblox nem testado no Studio.

## Exportação e Studio (12/11/2026)

- `build/21_exportar_wyvern.py` → `export/jogo/Wyvern.glb` (corpo E6 + sela S1, 61 ossos, texturas 1024; ossos-chave com nomes do jogo — ver o MAPA no script). `build/22_exportar_clipes_wyvern.py` → JSON dos 49 clipes do L6 (`CONVENCAO_ROBLOX=giro180y` é a que vale no import atual; conferido no Studio).
- No Studio (Teste-animacoes): `ReplicatedStorage.Animacoes_Wyvern` (49 KFS + Apelidos), `Wyvern` (montável) e `Wyvern_Guardiao` (IA, `Laboratorio_IA.Ninho_Wyvern`).
- Árvore de Poses: `Keyframe > Pose "RootPart" > root > …` — a primeira Pose é a peça e não anima; o deslocamento do corpo deste rig está no osso `root`.
- `takeoff`/`Pouso` no jogo com a raiz limitada a 1,7 (o jogo faz a subida/descida).
- Capturas: `review/studio/`. Detalhes e limitações: diário `DOCS/estado/dragao-2026-10-30.md` (DX).
