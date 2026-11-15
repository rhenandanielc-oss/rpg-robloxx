# Cervo-do-Bosque — blockout piloto (fauna de recurso da Floresta Ancestral)

Status (12/11/2026): **blockout entregue para revisão, NÃO aprovado.** Rig, UV, animação, Studio: não iniciados.

Referência: `REFERENCIAS/floresta-ancestral/cervo-do-bosque/cervo-do-bosque-referencia.png`
(SHA-256 `f28c35ce…78aa45`, idêntica ao original do Codex).

## Arquivos
- `cervo_blockout.py` — gera tudo em segundo plano:
  `blender -b --factory-startup --python cervo_blockout.py -- <1|2> blockout`
- `prancha.py` — monta a prancha referência x blockout: `python prancha.py <1|2> blockout`
- `blockout/CR_CervoDoBosque_Blockout_p2.blend` — **arquivo de trabalho atual** (passagem 2).
- `blockout/CR_CervoDoBosque_Blockout_p1.blend` — registro da passagem 1 (material neutro).
- `blockout/prancha_p1.png`, `blockout/prancha_p2.png` — pranchas de revisão.
- `blockout/p2_pequena.png` (leitura de longe), `blockout/p2_arame.png` (distribuição da malha).
- `blockout/p*_metricas.json` — triângulos, dimensões, materiais.

## Como editar (p2.blend)
- Coleção oculta **Fonte_Editavel**:
  - `Cervo_Corpo_Pecas`: cada peça (tronco, pescoço, coxa, canela, casco…) é uma ilha com grupo de vértices próprio. No modo de edição, selecione pelo grupo e mova/escale. A pele é refeita pelos modificadores Remesh (voxel 0,009), Suavizar e Reduzir.
  - `Cervo_Galhada_Skin`: esqueleto de vértices com modificador Skin; mover vértices muda a galhada.
- Visíveis: `Cervo_Corpo` e `Cervo_Galhada` são cópias aplicadas com cores provisórias por região. Depois de editar a fonte, gere de novo pelo script.
- Peças provisórias separadas: `Cervo_Orelha_E/D`, `Cervo_Olho_E/D`, `Cervo_Nariz`, `Plano_Apoio`.

## Revisão r1 (12/11/2026) — aguardando revisão do usuário
- Script: `cervo_r1.py`; o `cervo_blockout.py` (p1/p2) ficou intacto e a passagem 2 está preservada em `blockout/`.
  - Gerar: `blender -b --factory-startup --python cervo_r1.py -- revisao_r1`
  - Pranchas: `python prancha_r1.py A revisao_r1` e `python prancha_r1.py B revisao_r1`
- Arquivo de trabalho atual: `revisao_r1/CR_CervoDoBosque_r1.blend`.
  - A fonte editável continua na coleção `Fonte_Editavel`, com 42 grupos de peça e a galhada em Skin.
  - Cascos fendidos ficam em objeto próprio: `Cervo_Cascos` (2 pinças por pata).
- Passagem A (Workbench neutro): `revisao_r1/r1_prancha_A.png`.
  - Frente e perfil na mesma escala da referência (400 px/u).
  - Miniatura e vista de apoios.
- Passagem B (EEVEE, luz neutra): `revisao_r1/r1_prancha_B.png`.
  - Recortes de cabeça/peito e de dorso/flanco, miniatura e arame.
- Pelagem: textura de cor 1024² **pintada por script** (UV smart project + numpy), em `revisao_r1/r1_Cervo_Pelo_Cor_1k.png`.
  - Variação na direção do pelo, creme no ventre/garganta com borda pelo ruído do pelo.
  - 34 folhas de bordo pintadas no dorso.
- Galhada, orelhas: cor de vértice. Cascos, nariz e olho: cor sólida.
- Só do Blender, sem equivalente direto no Roblox:
  - Sheen (pelo) e Coat (olho);
  - Bump usando a própria textura de cor;
  - cor de vértice (o Roblox não usa).

  No Roblox, isso vira SurfaceAppearance com ColorMap, NormalMap e RoughnessMap, e a galhada precisa de textura assada.

## Revisão r2 (12/11/2026) — boca e olhos, aguardando revisão
- Mesmo script, com versão: `blender -b --factory-startup --python cervo_r1.py -- revisao_r2 r2`.
  - Sem o 2º argumento, gera a r1 de novo; a pasta `revisao_r1/` não foi alterada.
- Pranchas:
  - `python prancha_r1.py <A|B|ROSTO> revisao_r2 r2`
  - Novo: `revisao_r2/r2_prancha_rosto.png` (3/4 e perfil do rosto contra a referência).
- **Boca:** `Cervo_Boca` é uma linha dos lábios encaixada na superfície do focinho por raycast.
  - Vai de um canto ao outro passando pela frente do focinho e sobe no canto.
  - Lábio escuro pintado na textura.
- **Olhos:** `Cervo_Olho_E/D` são globos afundados (só a calota aparece).
  - Íris castanho-escura com raios e anel limbal; pupila horizontal; esclera quase toda escondida (cor de vértice).
  - Córnea brilhante (Coat).
  - `Cervo_Palpebras_E/D`: anel amendoado escuro, mais fino no canto lacrimal.
  - Aro claro, sombra junto da pálpebra e glândula pré-orbital pintados na textura.
- Custo: os olhos com 48×24 segmentos dão 2.208 triângulos cada (a cor depende da densidade). Para o jogo, a proposta é um olho de cerca de 200 triângulos com textura de íris.

## Revisão r3 (12/11/2026) — nariz, aguardando revisão
- Gerar: `blender -b --factory-startup --python cervo_r1.py -- revisao_r3 r3` (a r3 inclui a boca e os olhos da r2).
- Pranchas: `python prancha_r1.py <A|B|ROSTO> revisao_r3 r3`.
- **Nariz (`Cervo_Nariz`):** rinário úmido feito como volume próprio (elipsoide 64×32), embutido na ponta do focinho.
  - O contorno nasce da interseção com a pele, por isso sai liso.
  - Narinas em vírgula (cabeça redonda junto do centro, fenda para fora e para baixo) e sulco central até o lábio afundados no próprio volume; cor de vértice quase preta nas narinas.
  - Material fosco-úmido (rugosidade 0,34, Coat 0,12).
- Descartado: a casca recortada da pele, porque o contorno serrilhava e as narinas furavam até a pele.

## Meshy m1 (12/11/2026) — autorizado pelo usuário, 36 créditos; aguardando revisão
- Script `meshy/meshy_cervo.py`, adaptado do urso v2. A chave vem só de `MESHY_API_KEY`.
  1. **Image to Image** (nano-banana-2, 6 cr): 3 vistas neutras (perfil, frente, costas) em `meshy/imagem/`.
  2. **Multi-Image to 3D** (meshy-7.1, 4K PBR, 30 cr): `meshy/modelo/CR_Cervo_meshy.glb`/`.fbx` + `T_meshy_*.png`.
- `meshy/importar_meshy_cervo.py`:
  - orienta (frente −Y, cascos em Z 0);
  - escala com o meio do dorso a 1,15 u (PROPOSTA);
  - renderiza as mesmas vistas das revisões.
- Resultados:
  - arquivo: `meshy/modelo/CR_Cervo_meshy_bruto.blend`;
  - pranchas: `meshy/modelo/m1_prancha_{A,B,rosto}.png`.
- Bruto: 468.844 triângulos, 1 material, textura 4K. Medidas: comprimento 1,60, largura 0,82 (galhada), altura 1,96 u.
- Falta a malha de jogo: voxel → redução → UV → bake; depois rig.

## Malha de jogo (12/11/2026) — aguardando revisão
- Script `meshy/meshy_low_cervo.py`, adaptado do urso:
  `blender -b meshy/modelo/CR_Cervo_meshy_bruto.blend -P meshy/meshy_low_cervo.py -- low [alvo=12000] [voxel=0.005] [res=1024]`
- Etapas: voxel 0,005 (394k) → redução com mais densidade na cabeça/galhada → 2 malhas com textura própria → bake Cycles (Cor, Normal e Rugosidade, 1024²) → GLB.
- Saída em `low/`:
  - `CR_Cervo_do_Bosque_LOW.blend` (com o bruto oculto, fonte do bake);
  - `CR_Cervo_do_Bosque_LOW.glb` (7,9 MB);
  - `T_Cervo_{Cabeca,Corpo}_{Cor,Normal,Rugosidade}.png`;
  - `prancha_low.png`;
  - `relatorio_low.json`.
- Malhas: `Cervo_Cabeca` 8.768 tris (rosto, orelhas, galhada) + `Cervo_Corpo` 3.229 = **11.997 tris** (orçamento PROPOSTA).
- A boca fica fechada; para fauna não há cavidade nem dentes.
- Pendências:
  - o corpo ficou com poucos triângulos para deformar joelhos e jarretes no rig, e a galhada concentra a maior parte;
  - falta um LOD de distância;
  - Studio não testado.

## Malha de jogo v2 rebalanceada (12/11/2026) — base atual, aguardando revisão
- Mesmo script com pesos calibrados por teste: galhada 0,62, cabeça 0,70, articulações (joelhos/jarretes z 0,38–0,62 e pescoço) 0,65, resto 1,0; fator 3.
  `blender -b meshy/modelo/CR_Cervo_meshy_bruto.blend -P meshy/meshy_low_cervo.py -- low_v2`
- Resultado, com o mesmo total de 12.000 tris:

  | Região | Triângulos |
  |---|---|
  | Galhada | 3.193 |
  | Cabeça | 2.940 |
  | Corpo | 5.867 |

  Por malha: `Cervo_Cabeca` 5.245 + `Cervo_Corpo` 6.755.
- Saída em `low_v2/` (mesma estrutura de `low/`, que ficou preservada como v1), com `prancha_rebalanceada.png`.

## Rig (12/11/2026) — aguardando revisão
- Script `rig/rig_cervo.py`, adaptado do rig ungulado do Búfalo:
  `blender -b low_v2/CR_Cervo_do_Bosque_LOW.blend -P rig/rig_cervo.py -- rig`
- 30 ossos com os nomes do jogo:
  - eixo: Raiz (não deforma), Pelve, Coluna1–3, Pescoco, Pescoco2, Cabeca, Cauda1–2;
  - orelhas: OrelhaE/D;
  - dianteiras: Escapula/Braco/Antebraco/Canela/Quartela E/D;
  - traseiras: Coxa/Perna/CanelaTras/QuartelaTras E/D.
- **Sem Mandibula:** a boca da fauna é fechada, sem cavidade.
- Marcos medidos na malha:
  - cascos por k-means;
  - joelho e jarrete traseiros pela borda da pata em cada altura (o Meshy deixou a traseira E adiantada);
  - dorso pelo topo da garupa;
  - nuca e focinho pelo perfil;
  - orelhas pelo agrupamento lateral abaixo da galhada;
  - cauda pelo tufo.
- Pesos:
  - heat num proxy voxel (0,012) das duas malhas, transferido para cada uma;
  - cabeça e galhada rígidas na Cabeca (acima de z 1,62 tudo é galhada, inclusive os ramos na malha do corpo);
  - orelhas manuais com degradê;
  - abaixo do boleto → Quartela;
  - pesos rígidos reaplicados depois da suavização;
  - costura cabeça/corpo com pesos iguais (198 vértices);
  - máximo 4 influências, normalizado; nenhum osso sem vértice.
- Lições (heat "failed to find solution"):
  - osso da orelha dentro de malha mais fina que o voxel: desligar a deformação dele durante o heat;
  - mover pontas para dentro encurta ossos e também quebra o heat: medir a posição certa em vez de corrigir depois.
- Saída em `rig/`: `CR_Cervo_Rig.blend`, `prancha_rig.png`, `pose_*.png` (pastar, olhar para o lado, passada, alerta: só teste, não são clipes), `rig_relatorio.json`.

## Clipes — lote 1 (12/11/2026): Repouso, Andar, VirarE, VirarD — APROVADO pelo usuário em 12/11 (Blender; Studio pendente)
- Gerador `rig/clipes_cervo.py`, adaptado do gerador aprovado do Búfalo: IK das 4 patas, casco apoiado amarrado ao deslocamento, laços sem emenda, QA.
  `blender -b rig/CR_Cervo_Rig.blend -P rig/clipes_cervo.py -- rig/clipes_L1`
- Render (anda no mundo, chão xadrez de 0,1 u, marca vermelha = apoio):
  `blender -b rig/clipes_L1/Cervo_Clipes_L1.blend -P rig/render_clipes_cervo.py -- rig/clipes_L1/render <clipe> [passo] [repete] [limite]`
- Saída em `rig/clipes_L1/`:
  - `Cervo_Clipes_L1.blend` (ações `Cervo_<clipe>`);
  - `Cervo_<clipe>.json` (ponte para KeyframeSequence no Studio);
  - `manifesto_clipes.json`;
  - `prancha_lote1.png`;
  - `render/<clipe>_{lado,34}.gif`.
- Parâmetros técnicos (PROPOSTA):

  | Clipe | Valores |
  |---|---|
  | Andar | ciclo 1,1 s, passada 0,50 u, apoio 64%, 0,71 u/s; laço de 10 ciclos (orelhas sem repetição mecânica) |
  | Virar | 25°/s |
  | Repouso | 10 s |

- QA (todos os clipes):

  | Critério | Resultado |
  |---|---|
  | Emenda do laço | 0° |
  | Escorregão do casco apoiado | ≤ 3,2 mm |
  | Erro do IK | ≤ 2,3 cm (dianteira esticada no fim do apoio) |
  | Casco em balanço abaixo do chão | nunca |
  | Estiramento da pele | p99 ≤ 1,35×; máx 2,8–3,2× (poucas arestas: contato orelha E/galhada e coxa na passada) |

- Rig ajustado para isso: o voxel fundiu a ponta da orelha E num ramo da galhada. O peso da orelha agora cai perto da galhada inequívoca (z > 1,645) e o giro das orelhas é de 20°. A tentativa de apagar a ponte foi descartada, porque a faixa z 1,62–1,64 é ambígua.

## Clipes — lote 2 (12/11/2026): marchas, fuga e transições — Trote e transições andar↔trote APROVADOS em 13/11; corrida substituída pela r2 (APROVADA 12/11)
- Bloco `rig/clipes_cervo_l2.py`, carregado por `clipes_cervo.py` só com `CERVO_L2=1`; o lote 1 aprovado não muda.
  `CERVO_L2=1 CERVO_ANIM_ARQ=Cervo_Clipes_L2.blend blender -b rig/CR_Cervo_Rig.blend -P rig/clipes_cervo.py -- rig/clipes_L2 <lista>`
- Clipes:
  - Trote: pares diagonais, 1,85 u/s.
  - Corrida de fuga: galope rotatório com fase no ar, 4,84 u/s; cabeça alta, orelhas para trás, cauda branca erguida.
  - Arrancada: 10 quadros de susto + 3 ciclos crescendo; termina no quadro 0 da Corrida.
  - Frenagem: começa no quadro 0 da Corrida e senta nas traseiras.
  - AndarParaTrote, TroteParaAndar, TroteParaCorrida, CorridaParaTrote: classe Transicao do Búfalo L6; começo e fim nos quadros 0 das marchas.
- Velocidades, passadas e durações = PROPOSTA técnica. A fuga segue a PROPOSTA "cervídeos fogem" (a regra oficial só lista fuga/defesa/ataque).
- QA:

  | Critério | Resultado |
  |---|---|
  | Emenda | 0° |
  | Escorregão do casco apoiado | ≤ 5,1 mm |
  | Erro do IK | marchas ≤ 1,1 cm; transições até 3,9 cm (dianteira no limite do alcance no meio da troca) |
  | Estiramento da pele | p99 ≤ 1,39×; máx até 3,8× (poucas arestas, contato orelha/galhada) |

- Saída em `rig/clipes_L2/`: `Cervo_Clipes_L2.blend`, `Cervo_<clipe>.json`, `manifesto_clipes.json`, `prancha_lote2.png`, `render/<clipe>_{lado,34}.gif`.

## Corrida r1 (12/11/2026) — correção de "parece correr no lugar", aguardando revisão
- **Diagnóstico** (câmera lateral FIXA, postes a cada 0,5 u, 3 ciclos, `rig/render_fixo_cervo.py`):
  - A ação é no lugar: a Raiz não avança, a translação só tem z.
  - O deslocamento é aplicado 1× fora dela (no jogo, pelo modelo; no Blender, em `arm.matrix_world`).
  - Na entrega L2 ele estava correto: 1,94 u/ciclo, 4,84 u/s, casco sem deriva no apoio.
  - Causa da impressão: passada de apoio curta (0,62 u) para a velocidade, com pernas varrendo pouco sob o corpo (dianteira 51°, traseira 40°) e tronco sem suspensão. Não era enquadramento nem deslocamento duplo/ausente.
- **Correção** (`rig/clipes_cervo_l2.py`, só com `CERVO_CORRIDA_R1=1`; sem a variável a entrega L2 sai idêntica, diferença 0,0 verificada):
  - mesma velocidade 4,84 u/s;
  - ciclo 0,467 s (14 quadros), passada 0,80 u, apoio 35%;
  - mesma sequência de apoios do galope e fase aérea;
  - alcance no balanço: dianteira 0,18 u, traseira 0,16 u, zero no levantar e no pousar;
  - suspensão do tronco 0,055 u e balanço de 5°.
  - Amplitude da pata: dianteira 51° → 59°, traseira 40° → 58°.
  - Dip das transições com a corrida: 0,03 / 0,045.
- **Resultados** (`rig/corrida_r1/depois/`): `Cervo_Clipes_Corrida_r1.blend` + JSON de Corrida, Arrancada, Frenagem, TroteParaCorrida, CorridaParaTrote. A entrega L2 em `rig/clipes_L2/` não foi tocada; a cópia do gerador da entrega está em `rig/corrida_r1/clipes_cervo_l2_entrega_L2.py`.
- **Comparativos:**
  - `rig/corrida_r1/comparativo_corrida_antes_depois.png`
  - `corrida_antes_depois_lado_fixo.gif`
  - `corrida_{antes,depois}_34_fixo.gif`
  - `<transicao>_depois_lado_fixo.gif`

## Rig r2 + Corrida r2 (12/11/2026) — pernas sem curvar — Corrida r2 APROVADA pelo usuário em 12/11 (Blender; Studio pendente)
- Pedido do usuário: "as pernas dobram para frente e para trás, fazem curva".
- **Causas medidas:**
  1. Pele: o heat espalhou os pesos ao longo da canela. A dianteira tinha 30–40% de Antebraco/Quartela em todo o comprimento e a traseira ~20% de Perna, então a canela entortava em arco.
  2. Movimento (r1): o alcance extra puxava a dianteira para a frente ainda dobrada, e o carpo/cotovelo invertia (10 de 70 quadros).
- **Rig r2** (`rig/rig_pernas_r2.py` → `rig/CR_Cervo_Rig_r2.blend`; o `CR_Cervo_Rig.blend` original foi preservado):
  - abaixo do cotovelo e da soldra, cada vértice segue o segmento onde se projeta (antebraço/gamba, canela, quartela);
  - mistura só a ±0,022 u de cada articulação, e mistura com os pesos antigos no topo;
  - ossos e nomes iguais. O lote 1 regerado com o rig r2 dá ações idênticas (diferença 0,0).
- **Corrida r2** (`CERVO_CORRIDA_R1=1 CERVO_CORRIDA_R2=1` com o rig r2):
  - alcance menor (0,11 / 0,09 u), só no fim do balanço;
  - boleto mais recolhido no começo do balanço;
  - suspensão 0,045 u e balanço de 3°.
- **Resultado:** velocidade, passada, apoios e fase aérea iguais à r1.
- **Saída:** `rig/corrida_r2/` (`Cervo_Clipes_Corrida_r2.blend`, JSON de Corrida/Arrancada/Frenagem/TroteParaCorrida/CorridaParaTrote, `comparativo_pernas_r1_r2.png`, `corrida_r2_{lado,34}_fixo.gif`).

## Base única de clipes (13/11/2026): `rig/clipes_r2/Cervo_Clipes_r2.blend` — TODOS os lotes APROVADOS (Blender)
- Rig r2 (pernas rígidas por segmento + garganta suavizada) + 31 ações `Cervo_*`:
  - lote 1;
  - lote 2 (trote/transições andar↔trote + corrida r2 com arrancada, frenagem e transições trote↔corrida);
  - lote 3A, lote 3B e lote 4.
- JSON de todos os clipes em `rig/clipes_r2/json/` (ponte para KeyframeSequence no Studio).
- Studio/Roblox: NÃO testado; exige autorização e a vez no `DOCS/estado/studio-em-uso.md`.

## Base anterior (12/11/2026): `rig/clipes_r2/Cervo_Clipes_r2.blend` (12 ações; substituída acima)
- Rig r2 + 12 ações:
  - lote 1 (APROVADO): Repouso, Andar, VirarE, VirarD;
  - lote 2 marchas (aguardando revisão): Trote, AndarParaTrote, TroteParaAndar;
  - lote 2 corrida r2 (Corrida APROVADA): Corrida, Arrancada, Frenagem, TroteParaCorrida, CorridaParaTrote.
- Regeradas com o rig r2; as ações são idênticas às entregues (diferença 0,0 em todos os JSON). Só a pele das pernas mudou.
- JSON por clipe em `rig/clipes_r2/{L1,L2_marchas,L2_corrida}/` (ponte para KeyframeSequence no Studio). Juntar: `rig/juntar_clipes.py`.
- Pastas antigas (`clipes_L1`, `clipes_L2`, `corrida_r1`, `corrida_r2`) preservadas como histórico.

## Lote 3, bloco A (13/11/2026): vida no habitat — APROVADO pelo usuário em 13/11 (Blender; Studio pendente)
- Bloco `rig/clipes_cervo_l3.py`, carregado só com `CERVO_L3=1`; os lotes 1 e 2 não mudam.
  `CERVO_L3=1 CERVO_ANIM_ARQ=Cervo_Clipes_L3A.blend blender -b rig/CR_Cervo_Rig_r2.blend -P rig/clipes_cervo.py -- rig/clipes_L3A <lista>`
- Clipes: PastarEntrar/Pastar/PastarSair, BeberEntrar/Beber/BeberSair, Alerta, CocarCabeca, Sacudir. Todos começam e terminam no quadro 0 do Repouso.
- **Limite do modelo** (medido): pescoço+cabeça (~0,74 u) a partir da base do pescoço (z 0,97) não alcançam o chão com as dianteiras retas.
  - Pastar = folhagem baixa, focinho ~0,52 u (cervo de floresta ramoneia).
  - Beber = dianteiras bem abertas (±0,30 u), focinho ~0,18 u.
- **Rig r2 + garganta:** a cabeça rígida terminava numa linha e a garganta era 100% Pescoco, o que esticava até 20× nas poses de cabeça muito dobrada.
  - Agora a garganta faz transição Cabeca → Pescoco2 → Pescoco (`rig_pernas_r2.py`).
  - Picos: coçar 20× → 6,7×, sacudir 16× → 5,4×.
  - O rig anterior ficou em `rig/CR_Cervo_Rig_r2_antes_garganta.blend`.
  - A base `rig/clipes_r2/` foi regerada: ações idênticas (diferença 0,0).
- **QA:** emenda 0°; escorregão do casco ≤ 12,5 mm (entrada/saída do Beber, quando as dianteiras abrem); erro do IK 0; dobras invertidas 0 (Sacudir tem quadros de perna quase reta).
- **Saída** em `rig/clipes_L3A/`: `Cervo_Clipes_L3A.blend`, JSON, `prancha_lote3A.png`, `render/<clipe>_{lado,34}.gif`.
- **Bloco B** (Deitar, Deitado, Levantar): pendente.

## Lote 3, bloco B (13/11/2026): Deitar, Deitado, Levantar — APROVADO pelo usuário em 13/11 (Blender; Studio pendente)
- Bloco `rig/clipes_cervo_l3b.py`, carregado só com `CERVO_L3B=1`.
  - No `clipes_cervo.py` entrou um gancho de dobra, `DOBRA_HOOK`. Sem pata dobrando, o caminho é idêntico: o Andar do lote 1 saiu com diferença 0,0.
- Técnica do Búfalo: poses de pata em FK (cada osso mirado num ponto do chão); a transição é slerp entre a solução do IK em pé e a dobra; o alvo do IK caminha até o boleto dobrado (a dianteira levanta o casco num arco).
- Ordem dos cervídeos:
  - **Deita:** dianteiras primeiro. Ajoelha com carpo e canela no chão; essa dobra é própria, inclinação 18°. Depois dobram as traseiras.
  - **Levanta:** traseiras primeiro, depois as dianteiras.
  - Deitar e Levantar começam/terminam no quadro 0 do Repouso.
- **Deitado:** decúbito esternal, corpo apoiado sobre as patas dobradas, cabeça erguida; laço de 6 s com respiração, orelhas e cauda.
  - Calibração: pele das patas a −3 mm, inclinação de 7,4°.
- **QA:**
  - emenda 0°;
  - casco nunca abaixo do chão (mín 0,2 mm);
  - escorregão do casco apoiado ≤ 0,3 mm;
  - pele no máximo 3 mm abaixo do chão;
  - estiramento p99 ≤ 1,5× (máx ~5×).
- O "carpo invertido" do detector nessas poses é geometria (antebraço inclinado à frente no ajoelhado/deitado), conferido em close: a canela dobra para trás, como no animal real.
- **Saída** em `rig/clipes_L3B/`: `Cervo_Clipes_L3B.blend`, JSON, `prancha_lote3B.png`, `render/<clipe>_{lado,34}.gif`.

## Lote 4 (13/11/2026): reação e derrota — APROVADO pelo usuário em 13/11 (Blender; Studio pendente; DefesaGalhada segue PROPOSTA de regra)
- Bloco `rig/clipes_cervo_l4.py`, carregado só com `CERVO_L4=1` (rodar sem `CERVO_L3B`, porque os dois trocam o `DOBRA_HOOK`).
  - O gerador aceita patas "soltas" (FK sem IK) via `ext["solta"]`.
- **Clipes de pé** (começam e terminam no quadro 0 do Repouso):
  - Susto (1,4 s);
  - ReacaoFrente / ReacaoE / ReacaoD (0,9 s; impacto rápido, recupera devagar);
  - DefesaGalhada (2,2 s: raspa a dianteira, galhada baixa à frente, estocada curta). **PROPOSTA**: a ficha só sugere fuga para o cervo.
- **Derrota** (2,8 s): golpe → dianteiras cedem → tomba para o lado D → cabeça cai por último, pequeno quique.
- **Caído** (2 s, parado): de lado, pernas relaxadas, cabeça girada com a galhada escorando. É a pose para a coleta (OFICIAL: derrota seguida de interação).
- **Calibração do Caído:** flanco no chão, pernas acima do chão (patas de baixo recolhidas 16°), cabeça girada 70° com o pescoço quase reto, cabeça/galhada a 9 mm do chão.
- **QA:**
  - emenda 0°;
  - casco apoiado ≤ 1,5 mm nos clipes de pé;
  - IK ≤ 2 cm;
  - Derrota: no meio da queda, o casco da dianteira D entra até 3,2 cm e a pele até 4,9 cm no chão (pendência).
- **Saída** em `rig/clipes_L4/`: `Cervo_Clipes_L4.blend`, JSON, `prancha_lote4.png`, `closes_derrota_caido.png`, `render/<clipe>_{lado,34}.gif`.

## Escala e convenções
- Frente = −Y, alto = +Z, lado direito do animal = −X. Cascos apoiados em Z = 0.
- Altura no ombro ≈ 1,2 u (PROPOSTA de trabalho, não é porte oficial nem studs).
- Medidas tiradas da vista lateral da referência; a frontal guiou só larguras (ela tem perspectiva).

## Traços registrados para os próximos lotes (não modelados)
- **Javali Silvestre** (`REFERENCIAS/floresta-ancestral/javali-silvestre/`):
  - focinho largo e achatado, com disco nasal grande;
  - crista dorsal de cerdas eriçadas da nuca ao lombo;
  - presas curvas para cima saindo da boca;
  - corpo compacto, pesado na frente; pernas curtas com cascos fendidos e esporões visíveis;
  - cauda fina com tufo; pelagem marrom-escura com mechas ruivas e "costeletas" claras nas bochechas.
- **Coruja-da-Floresta** (`REFERENCIAS/floresta-ancestral/coruja-da-floresta/`):
  - disco facial claro com aro escuro; olhos âmbar grandes; bico escuro curvo;
  - tufos de "orelha" de penas;
  - plumagem marrom com manchas claras no dorso e listras verticais escuras no peito creme;
  - patas emplumadas com garras escuras;
  - asas abertas largas e arredondadas, com rêmiges barradas em faixas claras e escuras; cauda curta barrada.
