# Urso Silvestre v2: correção visual completa (03/11/2026)

**Situação:** aguarda aprovação visual do usuário.
- Ainda não há rig final, animações de produção nem Roblox Studio.
- A v1 reprovada continua intacta em `../` (scripts `criar_urso_corpo.py`, `pelo_urso.py`, `low_urso.py`, `review/r01..r08_low`, `low/`). O painel reprovado foi gerado de `review/r07` + `review/r08_low` (`review/PRANCHA_APROVACAO_r08.png`).

## Caminho escolhido
- Primeiro tentei corrigir só por código (`corpo_v2.py`, revisão `review/c01`): cabeça reconstruída em volumes, órbitas com pálpebras, orelhas em concha, lábios, gengivas e dentição. A anatomia melhorou, mas ficou longe da referência.
- Com autorização do usuário, usei o **Meshy** (créditos dele, chave só na variável de ambiente `MESHY_API_KEY`):
  1. **Image to Image** (nano-banana-2, **6 créditos**): a partir da referência, gerou o mesmo urso em pose neutra, boca fechada e fundo neutro, em 3 vistas. Saída em `meshy/imagem/` (`limpa_0..2.png` = vistas sem sobras nas bordas).
  2. **Multi-Image to 3D** (meshy-7.1, textura 4K + PBR, **30 créditos**): malha bruta de 6,5 milhões de tris. Saída em `meshy/modelo/` (GLB/FBX e texturas 4K).
  - **Total gasto: 36 créditos.** Saldo antes: 625.
- No Blender (`meshy/importar_meshy.py`): orientação com frente = −Y, pés em Z = 0 e escala com a corcova a **9,0 studs** (oficial: 8–10).

## Malha de jogo (`meshy/meshy_low.py` → `low/`)
Etapas:
1. Remesh por voxel (0,032) para fechar a malha. A malha do Meshy vem em lascas soltas: decimar direto rasga tudo (`review/m01_24k`).
2. Redução com mais densidade na cabeça.
3. Boca recortada pela linha dos lábios, medida por raio na malha. A cavidade fica recuada para não romper a parede dos lábios.
4. Peças da boca: gengivas, incisivos, caninos fortes, pré-molares, molar e língua. Os dentes de cima ficam dentro da largura da mandíbula, e o atributo `mand` marca a parte de baixo.
5. UV nova e bake de cor e normal (Cycles), da malha bruta para a de jogo. Cabeça e corpo têm texturas separadas. O interior da boca é pintado à parte e os pixels sem bake recebem a cor vizinha.

| MeshPart (`low/CR_Urso_Silvestre_v2_LOW.glb`) | Tris | Material | Texturas |
|---|---|---|---|
| Urso_Cabeca | 11.321 | M_Urso_Cabeca | cor 1024 + normal 1024 |
| Urso_Corpo_Frente | 10.265 | M_Urso_Corpo | cor 1024 + normal 1024 (compartilhadas) |
| Urso_Corpo_Tras | 10.226 | M_Urso_Corpo | (as mesmas) |
| Urso_Boca | 4.712 | M_Urso_Boca | cor 256 |
| **Total** | **36.524** | 3 materiais | 5 imagens, sem transparência |

- **Medidas:** ombro 8,96; comprimento 12,37; largura 6,57; pés em Z ≈ 0.
- **Validação por reimportação no Blender:** `GLB_VALIDO` (4 malhas ≤ 20k, com UV e 1 material cada).
- **Sem cartões com alfa:** pelo, casca, cipós e samambaias são geometria + textura assada. Isso elimina o custo de transparência da v1, que tinha cerca de 29k tris em cartões com alfa.
- **LOD (proposta):**
  - LOD0 = 38,8k;
  - o próximo nível pode ser gerado com o mesmo script e `alvo=16000`, usando as mesmas texturas;
  - longe, a RenderFidelity automática do Roblox reduz as MeshParts.
  - Desempenho com várias instâncias, PC e celular: **não medido** (só no Studio, numa etapa autorizada).

## Arquivos para revisão
- `meshy/modelo/CR_Urso_meshy_bruto.blend`: malha original do Meshy, orientada e escalada. Texturas 4K em `meshy/modelo/T_meshy_*.png`.
- `low/CR_Urso_v2_LOW.blend`: malha de jogo + a original oculta (fonte do bake). Texturas em `low/T_Urso_*.png`.
- Pranchas em `review/PRANCHAS_v2/`:
  1. referência × v1 × v2;
  2. corpo inteiro;
  3. cabeça + volumes sem cor (argila);
  4. boca fechada e aberta;
  5. patas, garras e dorso;
  6. original × jogo.
- Renders em `review/final_low/`, gerados com `render_v2.py`, `perfil=meshy`.

## Testes feitos (só no Blender)
- Boca aberta 36° e fechada, e pose **estática** de teste com cabeça erguida 30° + boca aberta 38°. Foi deformação direta por pesos procedurais: **não é rig nem animação**.
- Reimportação do GLB.
- Nada no Roblox Studio, em PC ou em celular.

## Diferenças restantes e limitações
- **Tronco:** mais compacto que na referência (comprimento/ombro ≈ 1,38). A referência é exagerada pela grande-angular. Dá para alongar o meio do tronco se o usuário quiser.
- **Perda de detalhe na malha de jogo:**
  - as mechas finas da silhueta viram volume com textura;
  - as garras ficam facetadas;
  - uma ponta de garra saiu escura no bake.
- **Boca aberta:**
  - as paredes internas das laterais ficaram irregulares;
  - os dentes estão menores e mais discretos que os da referência, que ruge com caninos enormes.
- **Boca fechada:** ainda aparece um ponto claro de dente no sulco do lábio, visto de perto.
- **Olhos:** vêm pintados na malha do Meshy (íris âmbar, pálpebras esculpidas), não são globos separados.
- **A "cabeça sem pelagem longa"** é mostrada em argila. No Meshy o pelo é parte da malha, não dá para separar.
- **Musgo e samambaias:** seguem o desenho gerado pelo Meshy, sem controle peça a peça.

## Ajuste da boca e dos dentes (03/11/2026, pedido do usuário: "Boca e dentes")
- **Recorte antes da redução:** a boca agora é recortada na malha densa do voxel, ANTES da redução. Lábios e interior ganham mais densidade, e as paredes internas saem mais lisas.
- **Dentição maior:**
  - caninos com raio 0,062 e comprimento-alvo de 0,18 em cima e 0,15 embaixo, curvos para dentro;
  - incisivos e pré-molares maiores;
  - raízes enterradas em gengivas mais grossas.
- **Boca fechada:** cada dente é testado com raios a partir da ponta e do meio. Se algum raio escapa sem bater na pele, o dente encurta (até 60%) ou recua. Os caninos de cima ficaram com 0,162; os incisivos, com cerca de 0,04.
- A cavidade de trás ficou mais estreita, para não romper a parede lateral da mandíbula.
- **Resultado:** `review/PRANCHAS_v2/07_boca_ajustada.png`. Malha de jogo regerada: 36.524 tris, `GLB_VALIDO`.
- **Restante:**
  - ainda aparece um ponto rosado no vão da frente, com a boca fechada e vista bem de perto;
  - a parede interna perto da comissura continua com alguns triângulos escuros;
  - os caninos são menores que os da pintura da referência. Ficaram do tamanho máximo que cabe escondido com a boca fechada.

## Rig (03/11/2026, aprovado pelo usuário: "Aprovado, seguir ao rig") — pasta `rig/`
- `rig_urso.py` (blender -b ../low/CR_Urso_v2_LOW.blend) → `rig/CR_Urso_v2_Rig.blend`. Texturas em `../low/`.
- **31 ossos com nomes do jogo** (não renomear no Studio):
  - tronco e cabeça: Raiz, Pelve, Coluna1–3, Pescoco, Pescoco2, Cabeca, Mandibula, OrelhaE/D, Cauda1–2;
  - patas dianteiras: EscapulaE/D, BracoE/D, AntebracoE/D, MaoE/D, DedosE/D;
  - patas traseiras: CoxaE/D, CanelaE/D, PeE/D, DedosPeE/D.
  - Raiz fica no chão (Z = 0) e não deforma.
- **Marcos** medidos na malha: centro dos pés, eixo de cada pata por fatias de altura, linha dos lábios e orelhas.
- **Pesos:**
  - heat num proxy fechado (voxel 0,10), transferido para a pele. Na pele real o heat falha: boca recortada e o osso Raiz fora da malha;
  - mandíbula pela linha dos lábios; orelhas por distância da base;
  - barriga e peito entre as patas passam para a coluna;
  - suavização; máximo de 4 influências por vértice;
  - peças da boca rígidas (atributo `mand`).
- **Poses extremas de TESTE** (`poses_teste.py`): deformação real pelo esqueleto, estática, não são clipes. Corpo apoiado no chão em todas. Resultado em `rig/poses_final/poses_medidas.txt` e na prancha `review/PRANCHAS_v2/08_rig_poses_teste.png`.

| Pose | z mín. | esticamento p99 | arestas > 3× |
|---|---|---|---|
| repouso | −0,001 | 1,00 | 0 |
| erguer-se nas patas traseiras | 0,000 | 2,25 | 105 (forro interno do fundo da boca) |
| passada longa | 0,000 | 1,49 | 5 (franja sob o peito) |
| cabeça baixa e de lado | 0,000 | 1,91 | 169 (forro interno do fundo da boca) |
| torção do tronco | 0,000 | 1,22 | 0 |
| mandíbula aberta 38° | 0,000 | 1,37 | 75 (forro interno do fundo da boca) |

- **Exportação** (`exportar_urso.py`) → `rig/export/CR_Urso_Silvestre_v2_Rig.glb` (8,6 MB), sem animações.
  - Reimportado no Blender: 31 ossos, todos com grupo; 4 malhas skinned (11.318 / 10.211 / 10.280 / 4.712 tris); até 4 influências por vértice; texturas 1024; caixa z 0,00–8,97. Resultado: `VALIDO`.
  - O Raiz ganhou um triângulo degenerado invisível com 100% de peso, porque o Roblox descarta osso sem peso.
- **Pendente:**
  - clipes de animação (próxima etapa, com aprovação);
  - IK/controle de apoio das patas para animar;
  - forro interno do fundo da boca: estica ao abrir, quase invisível;
  - Studio: importação manual pelo usuário e teste em Play. Não feito.

## Clipes de animação (03/11/2026, autorizado: "Sim, fazer os clipes") — `rig/anim_urso.py`
- **Como são feitos:**
  - procedurais e NO LUGAR: o jogo move o modelo;
  - IK nas 4 patas com alvos no mundo e polos calculados no repouso;
  - assados em FK na ação `Urso_<clipe>` (`rig/CR_Urso_v2_Anim.blend`) e em JSON (`rig/clipes/Urso_<clipe>.json`).
  - O JSON segue o formato dos clipes do Crocodilo e dos dragões: `matrix_basis` por osso e por quadro (quaternion xyzw + translação), para `montar_kfs_json.luau`.
- **18 clipes:**
  - parado e locomoção: Repouso (respiração), Observar, Andar, Corrida, Arrancada, Frenagem, VirarE, VirarD;
  - posturas: Sentar, LevantarSentado, Deitar, LevantarDeitado, Comer;
  - ações: Rugir, Ameaca (ergue-se rugindo e volta ao apoio), GolpePata, Mordida, ReacaoImpacto.
  - São clipes visuais: não definem habilidade, dano nem mecânica.
- **Peso de urso:**
  - andar em sequência lateral, com rolamento da pelve e da coluna e escápulas acompanhando a pata;
  - galope rotatório, com flexão e extensão da coluna;
  - antecipação → ação → recuperação nos ataques;
  - impacto ao voltar ao apoio na Ameaca;
  - corpo levemente agachado na locomoção. Em pé, as pernas de urso ficam quase retas, e isso deixa o IK sem alcance e com estalos.
- **QA** (`rig/clipes/manifesto_clipes.json` e `rig/qa_clipes.py`):
  - JSON sem valores inválidos, quaternions normalizados, emenda dos loops dentro do passo normal: `QA_CLIPES OK`;
  - o escorregão do pé apoiado é medido só com 2 quadros seguidos em apoio.

| Clipe | Loop | Vel. (studs/s, PROPOSTA) | Erro IK máx. | Escorregão pé | z mín. malha |
|---|---|---|---|---|---|
| Andar | sim | 3,23 | 0,021 | 0,25 studs/s (~8%) | −0,078 |
| Corrida | sim | 17,23 (RPG_02 propõe 18, não aprovado) | 0,122 | 0,002 | −0,076 |
| Arrancada | não | — | 0,206 | — | −0,152 |
| Virar E/D | sim | — | 0,000 | — | −0,07 |
| Sentar / Levantar | não | — | 0,000 | — | −0,124 |
| Deitar / Levantar | não | — | 0,001 | — | −0,402 (cotovelos e joelhos encostam no chão) |
| demais | — | — | ≤ 0,001 | — | −0,001 a −0,063 |

- **Revisão:**
  - GIFs em `rig/clipes_render/gif/Urso_<clipe>.gif`, cada um com velocidade normal e lenta (1/3) lado a lado, chão em xadrez para ver o escorregão;
  - tiras de quadros em `review/PRANCHAS_v2/09_clipes_locomocao_34.png` e `10_clipes_acoes_34.png`.
- **Limitações:**
  - garras e solas descem até ~0,08 abaixo do chão quando a perna muda de ângulo (sola com peso parcial do antebraço/canela);
  - a Arrancada tem erro de IK de 0,2 na transição para o galope;
  - o Sentar fica menos ereto que um urso real (as patas dianteiras não alcançariam o chão);
  - VirarE/D supõem que o jogo gira o modelo a ~60°/s.
- **Não feito:** Studio. É preciso montar a árvore de Poses do urso, porque a ponte usa um clipe molde (ver `montar_kfs_json.luau`), e publicar os clipes como Animation pela conta do usuário. Também não feito: teste em Play, PC e celular.

## Revisão de apoio e deformação dos clipes (03/11/2026, autorizada; APROVADA visualmente pelo usuário em 03/11/2026: "Aprovados")
- **Escopo:** só Blender e só arquivos do Urso. Sem Studio, sem publicar animações, sem commit.
- **Cópia anterior preservada:** `rig/antes_revisao/`, com Rig/Anim.blend, scripts, clipes, export, GIFs e `SHA256.txt`. Ela não foi sobrescrita. A comparação usa essa cópia.
- **Velocidades e giro da simulação são PARÂMETROS TÉCNICOS**, não regras do jogo:
  - Andar 3,23 studs/s;
  - Corrida 16,8 studs/s (antes 17,23: a passada do galope ficou mais curta e mais baixa para o IK alcançar);
  - Virar ±60°/s;
  - Arrancada e Frenagem com o perfil v(t) do manifesto (`v_perfil_PARAMETRO`).
  - O comportamento no Roblox continua pendente.
- **O que mudou:**
  - **Pesos** (`rig_urso.py`):
    - sola → pata em degradê (dedos e garras inalterados, articulação preservada);
    - suavização da fração Mandíbula/Cabeça no interior da boca;
    - degradê na base das orelhas;
    - suavização Cabeça/Pescoço.
    - O GLB foi reexportado e reimportado: 31 ossos, ≤ 4 influências, texturas ≤ 1024, `VALIDO`.
  - **Clipes** (`anim_urso.py`):
    - pé apoiado amarrado ao deslocamento integrado S(t) (`passo_var`);
    - Virar com pé em arco no pivô e contra-giro da sola;
    - balanço com altura mínima pelo deslocamento no mundo;
    - Arrancada terminando igual ao quadro 0 da Corrida;
    - Frenagem com perfil próprio;
    - Sentar e Deitar com passos das dianteiras (em vez de deslizar) e calcanhar levantado;
    - Ameaça: alvo do IK seguindo a pata em FK e pouso travado no toque.
- **QA** (`rig/qa_urso.py`): no mundo, com o deslocamento simulado; deriva por intervalo de apoio (sola a ≤ 0,02 do chão), chão por região, picos de aceleração angular e transições. Resultados em `rig/qa_revisao/qa_antes.json`, `qa_depois.json` e `tabela_antes_depois.md`.
  - **Deriva máx. no mundo (antes → depois):**
    - Andar 0,087 → 0,042;
    - Corrida 0,378 → 0,030;
    - Arrancada 3,21 → 0,029;
    - Frenagem 0,95 → 0,026;
    - VirarE/D 4,5 → 0,041/0,045;
    - Sentar 1,27 → 0,024;
    - Deitar 2,35 → 0,026.
  - **Chão:**
    - garras ≤ 0,002 em todos os clipes (antes até 0,125);
    - solas ≤ 0,016 (antes até 0,217);
    - cotovelos no Deitar 0,244 → 0;
    - joelhos 0.
  - **Tronco:** Deitar 0,402 → 0,100. É a franja de pelo da barriga do Meshy. O critério do tronco foi relaxado de 0,03 para 0,10 só neste clipe, e isso precisa da avaliação visual.
  - **Picos:** foram conferidos quadro a quadro (`rig/qa_revisao/picos/`): decolagem da Ameaça (q13), pousos do galope (Corrida, Arrancada) e Frenagem (q4–5). Não há estalo visível; são impactos ou ações intencionais e não foram suavizados.
- **Limitações:**
  - **Transições por mistura linear de FK de 0,25 s afundam a pata:**
    - Repouso→Virar 0,08;
    - Andar→Virar 0,14 (0,17–0,19 com a fase sincronizada);
    - Corrida→Andar 0,145;
    - Andar→Corrida 0,067.
    - No Roblox, recomenda-se IK de pé em tempo de execução ou transições curtas com a fase sincronizada; isso não foi testado.
  - **Boca:** arestas externas > 3x do repouso. São arestas curtas no topo do crânio, nos cantos dos lábios e na garganta:
    - Rugir 49 (antes 135);
    - Ameaça 30 (antes 138);
    - Mordida 61;
    - Reação 84.
    - Os closes (`rig/qa_revisao/boca/_boca.png`) não mostram rasgo. O interior tem faixas escuras de sombra e de esticamento leve da malha interna.

## Piloto no Roblox Studio: importação + Repouso, Andar e Rugir (04/11/2026, autorizado; APROVADO pelo usuário em 04/11/2026: "Aprovado")
- **Place:** `rpg_roblox` (PlaceId 114230639394991), aberto numa janela própria do Studio. Reserva em `DOCS/estado/studio-em-uso.md` das 12:42 às 13:16, depois liberada.
  - A outra janela (`Teste-animacoes_CR`, dos dragões) não foi tocada.
  - Neste place **não existe urso provisório**: só marcadores do mapa (`Reserva_CavernaUrso_*`, `Ninho_Urso_*`, `Caverna_Urso_*`/`SpawnUrsoGigante`). Nenhum deles foi alterado.
- **Importação** (Import 3D manual, feita pelo usuário) de `rig/export/CR_Urso_Silvestre_v2_Rig.glb`.
  - Chegou como `Workspace.Scene`: 4 MeshParts com `HasSkinnedMesh=true`, cada uma com Motor6D para a `RootPart`.
  - Ossos: 31, sem duplicados, todos em `RootPart > Raiz`. Há `AnimationController` (sem Animator) e `InitialPoses`.
  - Texturas: `SurfaceAppearance` (cor + normal) em Cabeça e Corpo; `TextureID` na Boca.
  - Altura da malha 8,97 (ombro). Frente para −Z. 1 unidade = 1 stud.
  - Veio **desancorado**. Ancorei só a `RootPart` da cópia de teste.
- **Isolamento** (só objetos do urso):
  - `Workspace.Teste_Urso_v2`, com a plataforma 120×120 a y=2000, a grade de 2 studs e o modelo `Urso_Silvestre_v2_Piloto`, pivô (0, 2000, 0);
  - `ServerStorage.Urso_v2_Piloto`, com `Dados_Clipes` (3 StringValues), `AdaptadorUrso`, `TestePlayUrso` e `Animacoes` (3 KeyframeSequences).
- **Eixos:** o importador gira o modelo 180° em Y. Studio = (−x, z, y) do Blender. Como os clipes são locais a cada osso, isso não os afeta.
  - Medido com poses conhecidas, aplicando os quadros direto nos ossos: erro máximo de **0,0015 stud** (Andar q9, Rugir q28, Repouso q0, 10 ossos cada, translações da Raiz incluídas).
  - Em Play, pelo Animator, o erro máximo foi **0,0021 stud**. O cliente mostra a mesma pose do servidor.
- **Clipes:** `HttpEnabled=false` neste place, e não alterei.
  - Por isso os JSON foram compactados (`studio/empacotar_clipes.py`, inteiros ×10⁴) e enviados como StringValues.
  - Erro de compactação 0,00005. Somas por canal iguais às do Python.
  - O adaptador próprio (`studio/AdaptadorUrso.luau`) monta a árvore de Poses a partir da hierarquia real dos ossos do urso (`RootPart` > `Raiz` > …, 32 poses por quadro, nenhuma faltando). Não usa a ponte compartilhada nem clipe molde de outra criatura.
  - **Correção no adaptador:** os loops do urso não repetem o último quadro. Por isso entra um keyframe final igual ao quadro 0, e as durações ficam iguais ao Blender: Repouso 4,0 s, Andar 1,2 s, Rugir 2,4 s.
- **Play (PC, Studio):**
  - `AnimationClipProvider:RegisterAnimationClip` funcionou, com id temporário só no Studio. **Nada publicado.**
  - Repouso, Andar e Rugir tocaram isolados.
  - Taxa de tempo: 0,98–1,00 na velocidade normal e 0,327–0,334 em 1/3.
  - O Rugir termina sozinho aos 2,4 s.
  - `parar()` desliga a conexão, para as faixas e devolve o pivô ao início. Conferido.
  - Com streaming ligado, foi preciso levar o personagem até a plataforma e pedir streaming em volta dela, só durante o Play.
- **Andar com deslocamento a 3,23 studs/s** (parâmetro técnico, não oficial):
  - sentido correto (−Z, para onde a cabeça aponta);
  - com o deslocamento por relógio (`os.clock`), a pata apoiada derivava **0,08–0,18** por apoio;
  - amarrado ao tempo da faixa (versão final do `TestePlayUrso`), a deriva fica entre **0,003 e 0,049** conforme a execução. A tolerância proposta é 0,05; no Blender, a deriva do osso é 0,003–0,012.
  - A diferença restante nas patas dianteiras não foi explicada: não vem da ordem `Stepped`/`PreAnimation`.
- **Capturas:** `rig/qa_revisao/piloto_studio/` e a prancha `review/PRANCHAS_v2/13_piloto_studio_blender_x_roblox.png`, com Blender × Studio nas mesmas câmeras e a referência.
  - As poses batem. No Studio a cor sai mais quente e saturada, por causa da iluminação do place.
- **Salvo pelo usuário** (04/11/2026): o place `rpg_roblox` agora guarda `Workspace.Teste_Urso_v2` e `ServerStorage.Urso_v2_Piloto`.
- **Pendências:**
  - mistura entre clipes afunda a pata (até cerca de 0,19 nos testes do Blender);
  - franja da barriga no Deitar (0,10);
  - nada testado no celular nem com várias instâncias;
  - publicação das animações fora do escopo.

## Lote 2 no Studio: Corrida, Arrancada, Frenagem, VirarE e VirarD (04/11/2026, autorizado; AGUARDANDO AVALIAÇÃO)
- **Reserva e place:** Studio reservado das 14:51 às 15:21 e liberado. Place `rpg_roblox` (PlaceId 114230639394991). A janela dos dragões não foi tocada.
- **Piloto preservado:** o mesmo modelo `Workspace.Teste_Urso_v2.Urso_Silvestre_v2_Piloto`, sem nova importação. Repouso, Andar e Rugir não foram mexidos (somas e KeyframeSequences conferidas).
  - Regressão em Play com o módulo novo:
    - Repouso: 4,0 s, em loop;
    - Rugir: 2,4 s;
    - Andar a 3,23: deriva de 0,015 (limiar 0,01) e 0,049 (limiar 0,04), igual ao piloto.
- **Dados:** `HttpEnabled` continua desligado.
  - `studio/empacotar_clipes.py --acrescentar --compacto`:
    - só acrescenta ou substitui os 5 clipes;
    - omite os canais iguais ao padrão;
    - leva no cabeçalho a lista dos 31 ossos;
    - grava `Perfis_<clipe>` com v, giro e v(t) do manifesto.
  - Envio em 2 partes (`envio_lote2_a.luau`, `_b.luau`). Tamanhos e somas por canal iguais aos do Python nos 8 clipes.
- **Adaptador** (`AdaptadorUrso`): passou a preencher os canais omitidos. Gera 31 ossos, 32 poses por quadro, nenhuma faltando.

| Clipe | Duração | Loop | Keyframes | Prioridade |
|---|---|---|---|---|
| Corrida | 0,4667 s | sim | 15 (com fechamento) | Movement |
| Arrancada | 1,7667 s | não | 54 | Movement |
| Frenagem | 1,5 s | não | 46 | Movement |
| VirarE | 1,2 s | sim | 37 (com fechamento) | Movement |
| VirarD | 1,2 s | sim | 37 (com fechamento) | Movement |

- **Teste** (`TestePlayUrso`; a versão do piloto ficou guardada em `ServerStorage.Urso_v2_Piloto.Anteriores`):
  - deslocamento e giro amarrados ao tempo da faixa;
  - giro em torno da cabeça da Raiz, como no Blender;
  - perfil v(t) integrado pelo trapézio, como no `qa_urso.py`;
  - parâmetros técnicos, não oficiais: Corrida 16,8 studs/s, Virar ±60°/s, v(t) do manifesto.
- **Poses conhecidas em Play** (22 quadros, incluindo os extremos): erro de **≤ 0,0029 stud** em relação ao Blender. O último quadro da Arrancada, lido 0,5 ms antes do fim, deu 0,0087.
  - O cliente mostra a mesma pose do servidor depois da replicação (PeE idêntico) e o mesmo giro (18,00°).
- **Velocidade de reprodução:** taxa do tempo da faixa entre 0,94 e 0,98 em 1×, e entre 0,319 e 0,332 em 1/3.
- **Sentido:**
  - Corrida e Arrancada avançam em −Z: 16,2 e 15,7 studs;
  - Frenagem: 7,98 studs;
  - VirarE gira para a esquerda (+146° em 2,4 s); VirarD gira para a direita (−147°).
- **Apoio** (métrica de **osso**: punho/tornozelo e dedos, que aproximam a garra; não é a sola deformada do Blender, que o Studio não lê):
  - **Teste determinístico**, quadro a quadro, sem relógio: igual ao Blender.
    - VirarE ≤ 0,003;
    - Arrancada MaoD 0,0726 (Blender 0,0725), PeD 0,079 (0,078).
  - **Ao vivo, apoio firme** (osso a ≤ 0,01 do mínimo):

| Clipe | 1× | 1/3 |
|---|---|---|
| Corrida | 0,003 | 0,004 |
| Arrancada | 0,003–0,004 | 0,002 |
| Frenagem | 0,042 | 0,006–0,007 |
| VirarE | 0,018–0,020 | 0,014–0,017 |
| VirarD | 0,003–0,025 | 0,008–0,021 |

  - **Com limiar 0,04:** até 0,185, porque inclui o rolamento intencional da pata (o calcanhar sobe com os dedos apoiados). O teste determinístico a 90 Hz reproduz esses valores (VirarE 0,14, Corrida 0,095).
- **Sequência Arrancada → Corrida → Frenagem** (`TestePlayUrso.sequencia(2, 0,1)`), com mistura de 0,1 s:
  - Arrancada → Corrida entra em fase: a Corrida em `Length − 0,1`, porque o último quadro da Arrancada é igual ao quadro 0 da Corrida;
  - Corrida → Frenagem: a Frenagem entra no mesmo tempo da Corrida, logo após a volta do loop.
  - 4 ensaios: cerca de 4,2 s e 38,3–39,4 studs.
    - v contínua: 0 → 16,8 → cerca de 16,7 → 0, com variação ≤ 1,8 studs/s por passo;
    - osso mais rápido: 19,0–20,0 studs/s (Arrancada sozinha chega a 19,7);
    - deriva no apoio firme: 0,007 / 0,018 / 0,037 / 0,143. O último ocorreu com a troca disparada atrasada (verificação no ritmo do `task.wait`).
- **Defeitos encontrados e corrigidos, todos no teste do urso e não nos clipes:**
  - transitório na 1ª amostra de cada ensaio;
  - faixa parada informa `WeightCurrent = 1`;
  - Corrida entrando fora de fase (osso a 28,7 studs/s);
  - Frenagem entrando fora de fase (pata escorregava 0,23);
  - avanço contado na entrada da faixa (salto do pivô de 1,43);
  - faixa em cache não voltava ao tempo 0.
- **Capturas:** `rig/qa_revisao/lote2_studio/` e a prancha `review/PRANCHAS_v2/14_lote2_blender_x_roblox.png` (Blender × Studio nas mesmas câmeras, mais a referência).
- **Não salvo:** as mudanças do laboratório só existem na sessão aberta até o usuário salvar. São elas: os 10 StringValues novos em `Dados_Clipes`, as 5 KeyframeSequences, os 2 módulos atualizados e `Anteriores`.
- **Pendências:**
  - a troca A→C ainda depende do momento em que o ensaio a detecta (resultado de 0,007 a 0,143);
  - outras transições (Andar↔Virar, Corrida→Andar) e o Deitar continuam como registrado antes;
  - nada testado no celular nem com várias instâncias;
  - publicação das animações fora do escopo.

## Lote 3 no Studio: os 10 clipes restantes (04/11/2026, autorizado; AGUARDANDO AVALIAÇÃO)
- **Detalhes completos:** `rig/qa_revisao/lote3_studio/resultados_lote3.md`.
- **Reserva:** Studio reservado das 16:56 às 17:26 e liberado. O usuário autorizou o uso simultâneo, só no `rpg_roblox`, com o Dragão Sombrio no Teste-animacoes. A janela dos dragões não foi tocada.
- **M0:** o lote 2 estava **salvo** no place (place reaberto, com os 8 clipes e os módulos presentes). Não houve nova importação.
- **Dados:**
  - os 10 clipes foram enviados em 3 partes, só acrescentando (`envio_lote3_a/b/c.luau`);
  - tamanhos e somas por canal iguais aos do Python; erro de 0,00005;
  - 31 ossos e 32 poses (`RootPart` > `Raiz`), nenhuma faltando.
- **Fechamento de loop:** só o Comer recebeu o keyframe de fechamento (73 keyframes, 2,4 s). As ações únicas não receberam.
- **Prioridades:**
  - Action: Observar, Sentar, Levantar, Deitar, Comer;
  - Action2: Ameaça, GolpePata, Mordida;
  - Action3: ReaçãoImpacto, que deve se sobrepor às demais.
  - Os 8 clipes anteriores não foram alterados.
- **Play/PC:**
  - **Poses:** 33 quadros conhecidos com erro de ≤ 0,0025 stud. O cliente é igual ao servidor depois da replicação, com as 4 malhas com skin.
  - **Repetições:** 3 por ação única e 3 ciclos do Comer, em 1× e em 1/3. Razão de tempo 0,97–1,00 em 1× e 0,330–0,333 em 1/3.
  - **Execução:** todos os ensaios começaram e terminaram limpos.
  - **Apoio** (métrica de **osso**, não de pele):
    - deriva no apoio firme de ≤ 0,003 nas posturas e ≤ 0,048 na Ameaça;
    - com limiar de 0,04, chega a 0,094 no GolpePata, contra 0,034–0,041 no Blender pela mesma métrica.
  - **Velocidade de osso:** igual à do Blender (±15%), sem estalo.
- **Sequências:** 7 de 8 OK, com mistura de 0,1 s e pose terminal sustentada por congelamento da faixa no passo.
  - **Repouso→Comer→Repouso: PENDENTE.** A pata dianteira esquerda desliza 0,6 stud, porque o Comer começa com ela à frente e não tem passo de entrada. A mistura de 0,3/0,5 s não resolve. A correção é no clipe, no Blender, e precisa de autorização.
- **Boca** (closes da Ameaça, da Mordida e do Comer, Blender × Studio):
  - não há rasgo nem dente atravessando a pele, nesta distância de câmera;
  - persistem as faixas escuras no interior da boca, já registradas antes.
  - Não houve close no nível de vértice.
- **Deitar:** no close baixo, a franja da barriga encosta no chão em cartões de pelo, com a massa do corpo acima. No Blender a franja chega a −0,10. Não está resolvido: o Studio não mede pele.
- **Teste corrigido** (só `TestePlayUrso`):
  - `parar()` zera os `Transform`, porque o Animator mantém a última pose;
  - o encadeador congela no `Stepped`.
  - As versões anteriores ficaram em `Urso_v2_Piloto.Anteriores`.
- **Regressão:** Repouso, Andar e Rugir OK; o lote 2 foi preservado.
- **Pranchas:** `review/PRANCHAS_v2/15` e `16`. GIFs normal/lento do Blender em `qa_revisao/lote3_studio/gif_blender/`. Não há vídeo do Studio.
- **Salvo pelo usuário em 04/11 (informado, junto com o r2 do Sentar; não conferido reabrindo o place).** Estavam na sessão:
  - 20 StringValues novos em `Dados_Clipes`;
  - 10 KeyframeSequences em `Animacoes`;
  - o `TestePlayUrso` novo;
  - `Anteriores.TestePlayUrso_lote3_antes_correcao`.
- **Pendências:**
  - transição do Comer;
  - franja do Deitar (pele);
  - faixas escuras da boca;
  - Arrancada→Corrida (0,143);
  - outras transições;
  - celular, várias instâncias e publicação.

## Sentado mais apoiado no chão (04/11, só Blender)
Pedido do usuário: "deixe ele mais sentado no chão". A mudança foi só em `rig/anim_urso.py` (dicionário `SENTADO`; os valores antigos ficaram comentados). O LevantarSentado é o mesmo clipe ao contrário.
- **Novos valores:**
  - raiz (0, 1,4, −2,48);
  - pelve −43°;
  - coluna 13°/15°/7°;
  - recuo das dianteiras 1,6;
  - passo à frente das traseiras 0,9;
  - cauda −30°.
  - As dianteiras recuam mais tarde (0,38–0,72 e 0,62–0,94), depois que o corpo já desceu. Assim o IK não estica no meio do passo.
- **Quadro final, antes → depois:**
  - garupa: +0,09 acima do chão → −0,03 (o pelo encosta);
  - coxa: 1,41 → 0,63;
  - tronco: 35° → 46°;
  - erro de IK: 0,0005 → 0,0001;
  - todas as patas firmes.
- **QA:**
  - `qa_clipes`: OK nos 18 clipes;
  - `qa_urso` em Sentar/LevantarSentado: sola com deriva ≤ 0,016, garra a 0,001, tronco 0,031 abaixo do chão (contato da garupa, pelo);
  - emendas Repouso↔Sentar: 2,9°, iguais às de antes.
  - Os outros 16 JSON ficaram idênticos byte a byte.
- **Prancha:** `review/PRANCHAS_v2/17_sentado_antes_depois.png`. Relatório do QA: `rig/qa_revisao/qa_sentado_depois.json`.
- **Studio NÃO atualizado:** os KFS Sentar/LevantarSentado do laboratório são da versão anterior. Reenviar exige autorização.
- **r2 (04/11, pedido do usuário "encoste mais no chão, a bunda"):**
  - **Mudanças:**
    - raiz z −2,48 → −2,64;
    - pelve −43° → −40° (a traseira desce);
    - coluna 12°/14°/7°;
    - pé traseiro quase plano (calcanhar 0,16 / −4°), o que fecha o vão sob a garupa;
    - cauda −30° → −15°, para não entrar no chão.
  - **Massa da garupa** (percentil 5 dos vértices da Pelve): 0,19 → −0,03. A garupa assenta no chão; o pelo afunda até 0,24.
  - **QA:**
    - `qa_clipes` OK;
    - `qa_urso`: sola com deriva ≤ 0,023, sem sola abaixo do chão; garra 0,001;
    - emendas com o Repouso iguais (2,9°); erro de IK 0,0002.
    - Os outros 16 clipes ficaram idênticos.
  - **Prancha:** `review/PRANCHAS_v2/18_sentado_r2_garupa_no_chao.png`. O Studio continua com a versão antiga.
- **r2 no Studio (04/11, autorizado: "Sim, reenviar ao Studio"):**
  - **Ambiente:** place `rpg_roblox`, laboratório `ServerStorage.Urso_v2_Piloto`. O Studio foi reservado das 18:23 até o fim e liberado; a janela Teste-animacoes não foi tocada.
  - **Backup:** KFS, dados e perfis antigos em `Anteriores.Sentar_antes_r2`.
  - **Envio:** `rig/studio/envio_sentar_r2.luau`, só acrescentando. Dados de 4722/4759 bytes; somas por canal iguais às do Python (diferença ≤ 0,0005 em 43 quadros, arredondamento de 1e-4).
  - **KFS:** remontados com o `AdaptadorUrso`. 43 keyframes cada, 1333 poses, nenhuma faltando, prioridade Action, sem loop.
  - **Poses (Edit, `Bone.Transform`):** Sentar q17/q42 e Levantar q25/q42 contra o Blender, com erro máximo de 0,0008 stud.
  - **Play/PC, sequência Repouso→Sentar→(pose sustentada 6 s)→LevantarSentado→Repouso, mistura 0,1 s:**
    - todas as trocas OK;
    - deriva das patas: ≤ 0,002 com limiar 0,01 e ≤ 0,011 com limiar 0,04;
    - pelve mínima a 0,897 do chão, igual ao Blender (0,8970).
  - **Capturas (cliente):** `rig/qa_revisao/sentado_r2_studio/` (lado e trás baixo). A garupa assenta no chão.
    - Na vista de trás aparece uma peça escura entre as coxas, provavelmente o lado de dentro do pelo/cauda. Fica para avaliar.
    - **Inspeção da peça escura (04/11, só leitura, Blender):**
      - **O que é:** a face de baixo da garupa e da base da cauda, na própria malha `Urso_Corpo_Tras` (ossos Pelve/Cauda1/Cauda2). 83% das normais apontam para baixo.
      - No repouso essa face fica escondida, a cerca de 2,9 de altura; com o urso sentado ela chega ao chão.
      - **Por que fica escura:** a textura é normal (brilho 0,215 contra 0,239 da malha; 3 de 264 vértices com texel quase preto). Ela escurece porque recebe só luz ambiente, entre a sombra do próprio corpo e o chão.
      - Não é buraco, peça solta nem malha de outra criatura.
      - **Prancha:** `rig/qa_revisao/sentado_r2_studio/peca_escura_inspecao.png`.
      - **Nada foi alterado.** Possíveis ajustes, só com aprovação: clarear um pouco essa área na textura assada, ou mudar levemente a cauda ou a altura da garupa no Sentar.
    - **Textura clareada (04/11, pedido do usuário "Clarear a textura"; só Blender):**
      - **Máscara** (`rig/mascara_garupa.py`): faces da `Urso_Corpo_Tras` (Pelve/Cauda) baixas e viradas para baixo no Sentar **e** também viradas para baixo no Repouso, para a parte de trás da garupa do urso em pé não mudar. São 258 faces, 0,16% da textura.
      - **Clareamento** (`rig/clarear_garupa.py`, sempre a partir do backup): brilho ×1,35, mesmo matiz, saturação −20% na máscara, borda suave (dilata 5 px + desfoque de 4 px). Brilho da região: 0,201 → 0,253.
      - **Arquivo alterado:** `low/T_Urso_Corpo_Cor.png`, usado pelos .blend de LOW, Rig e Anim. Backup em `low/T_Urso_Corpo_Cor_antes_clarear.png`.
      - **Renders:** no Sentar de trás, 0,35–0,4% dos pixels mudam; no Repouso, 0,7% (máximo 22/255), sem diferença visível. Prancha: `review/PRANCHAS_v2/19_garupa_clareada.png`.
      - A tentativa anterior (×1,45, puxada para o marrom, máscara sem o filtro do repouso) deixou uma mancha alaranjada e clareou a garupa em pé. Foi descartada.
      - **Pendente:**
        - os GLB (`low/…LOW.glb`, `rig/export/…Rig.glb`) ainda têm a textura antiga e precisam ser reexportados;
        - no Studio, a `SurfaceAppearance` do corpo precisa da textura nova (reimportação/envio da imagem). Isso exige autorização;
        - o efeito na luz do Roblox não foi conferido.
    - **Aplicado no Studio (04/11 19:05–19:10, autorizado: "Aplique"):**
      - GLB do rig reexportado com a textura nova (`rig/export/…Rig.glb`, `VALIDO`). O GLB antigo foi guardado fora do repo.
      - Textura enviada como `rbxassetid://139654277617353` e aplicada no `ColorMap` das duas `SurfaceAppearance` do corpo. O id anterior ficou em `Anteriores.Textura_Corpo_antes_clarear` (`rbxassetid://112678621580764`).
      - **Resultado em Play/PC, captura do cliente de trás:** quase sem mudança. O brilho da região foi de 53,0 para 53,5 em 255. Captura: `rig/qa_revisao/sentado_r2_studio/studio_play_Sentar_r2_42_tras_baixo_clareada.jpg`.
      - **Diagnóstico:**
        - pintei só no cliente a malha `Urso_Corpo_Tras` de vermelho (descartado ao parar o Play) e confirmei que a peça é dela;
        - um raio da câmera do Studio projetado no Blender mostrou que a peça é a **parede interna entre as coxas** (virilha), quase vertical. Ela não é a face de baixo que a máscara cobriu;
        - a textura ali tem brilho normal (cerca de 0,21, contra 0,233 de média). O escuro vem da sombra entre as pernas.
      - **Tentativa descartada:** clarear também essas faces (×1,8, `--virilha`) mudava a parte de trás da coxa no Repouso (2% dos pixels, até 59/255). A textura voltou à versão enviada (×1,35, idêntica byte a byte).
      - **Conclusão:** só com textura não dá para tirar essa sombra sem mudar o urso em pé. As saídas seriam afastar levemente as coxas ou a cauda no Sentar, ou aceitar a sombra.
      - **Salvar o place** para manter o `ColorMap` novo. Se preferir voltar ao antigo, basta repor o id anterior.
  - **Salvo:** o usuário informou em 04/11 que salvou o place ("Pronto"). Não conferi reabrindo o place.

## Requisito futuro: pelo ao vento (registrado em 04/11/2026; NÃO IMPLEMENTADO)
**Orientação do usuário:** o pelo do Urso Silvestre deve se mover de forma sutil e natural com o vento, preservando a aparência aprovada.

**Estado:** apenas registrado. Não há solução técnica escolhida, implementação ou teste. O modelo, o rig e os 18 clipes não foram alterados por este registro.

**Ponto de partida (fatos da v2):**
- A pelagem está integrada à malha: pelo, cascas, cipós e samambaias são geometria + textura assada, sem cartões com alfa (ver "Validação" acima).
- O jogo usa 4 malhas skinned, 31 ossos e até 4 influências por vértice.
- Não existem hoje mechas separadas nem ossos de pelo. Por isso não se pode prometer movimento independente de cada fio.
- A solução precisa ser estudada e validada no Roblox.

**Objetivo da futura implementação:**
- movimento discreto só das mechas mais expostas, acompanhando a direção e a intensidade do vento;
- corpo, rosto, boca e patas estáveis;
- cascas firmes, sem ondular junto com o pelo;
- compatível com os 18 clipes, sem prejudicar deformações nem apoio no chão;
- desempenho adequado em PC e celular, inclusive com várias criaturas ao mesmo tempo.

**Antes de implementar (etapa própria, com aprovação específica):** apresentar uma proposta técnica que diga:
- se será preciso separar partes da malha (mechas expostas), acrescentar ossos de pelo ou ajustar pesos;
- como preservar o rig de 31 ossos, os nomes dos ossos (o skin do Roblox liga por nome) e os 18 clipes já validados;
- onde o movimento roda (cliente/servidor), como ele liga ao vento do bioma e qual é o custo estimado.

As opções serão comparadas na proposta. Nenhuma está decidida.

**Demonstração futura:**
- modelo sem vento e com vento em intensidades diferentes, lado a lado;
- fidelidade à referência `REFERENCIAS/floresta-ancestral/urso-silvestre/urso-silvestre-referencia.png`;
- custo de desempenho registrado (PC e celular, uma e várias criaturas).

**Studio:** só em etapa autorizada, respeitando a reserva em `DOCS/estado/studio-em-uso.md`.

### Proposta técnica (04/11/2026, AGUARDANDO APROVAÇÃO; nada implementado)
O usuário pediu "também o vento" junto com a textura. Pelo requisito acima, primeiro vem a proposta.

**Recomendada — A: ossos de pelo só para as mechas expostas, balanço procedural no cliente.**
1. **Blender:**
   - acrescentar de 8 a 12 ossos curtos `Pelo*` filhos dos ossos atuais: crista do dorso (Coluna1–3), juba do pescoço/ombro (Pescoco, Escapulas), franja da barriga e da garupa (Coluna2, Pelve);
   - pesar neles só as pontas das mechas (peso gradual, base 0, ponta ~0,6), tirando o peso do osso pai na mesma proporção;
   - rosto, boca, patas e placas de casca ficam fora (peso 0 nos `Pelo*`); as cascas são selecionadas pela cor ou região da textura;
   - manter ≤ 4 influências por vértice e não renomear nenhum dos 31 ossos atuais.
2. **Clipes:** os 18 clipes não citam os `Pelo*`, então esses ossos ficam na pose de descanso enquanto o clipe toca. Os clipes não mudam. Rodar de novo `qa_urso`/`qa_clipes` para provar que a deformação e o apoio são os mesmos (o peso só sai das pontas do pelo).
3. **Roblox:**
   - reexportar e reimportar o GLB, o que gera MeshIds novos. As KeyframeSequences continuam valendo porque se ligam por nome de osso;
   - um LocalScript do cliente soma ao `Bone.Transform` dos `Pelo*`, depois da animação, um pequeno giro (seno com fase por osso + ruído) na direção de `Workspace.GlobalWind`, com amplitude proporcional à intensidade.
4. **Desempenho:**
   - só no cliente; desliga além de cerca de 60 studs e fora da tela;
   - atualização a cada 2 quadros e menos ossos em celular ou na qualidade gráfica baixa;
   - medir o tempo por quadro com 1 e com 10 ursos, no PC e no celular.
5. **Riscos:**
   - conferir o limite de ossos por malha do Roblox (31 + 12 = 43);
   - a reimportação exige autorização e novo teste dos clipes no Studio;
   - o pelo é geometria assada: o efeito será de mechas ondulando em bloco, não de fios soltos.

**Alternativas (não recomendadas):**
- **B:** recortar as mechas em malhas separadas presas aos ossos. Cria costuras visíveis, mais peças e mais custo.
- **C:** balançar ossos existentes (Coluna, Pescoço). Move o corpo inteiro, o que viola "corpo estável".

**Demonstração prevista:**
- no Blender: vento 0 / fraco / forte lado a lado, mais a prancha de pesos;
- no Studio: o mesmo em Play, com a medição de desempenho.
- Tudo depende de aprovação específica de cada etapa (Blender, depois Studio).

### Opção A no Blender (04/11/2026, autorizada: "Sim, opção A no Blender"; AGUARDANDO AVALIAÇÃO; Roblox NÃO testado)
- **Variante separada:** `rig/vento/CR_Urso_v2_Rig_Vento.blend`, gerada por `rig/vento/adicionar_pelo.py` a partir do `CR_Urso_v2_Rig.blend`. O original não foi alterado (mesmo md5 antes e depois).
- **Ossos:** 14 ossos `Pelo<Região><Pai>`, totalizando 45. Os 31 ossos atuais mantêm nomes, posições e hierarquia.
  - Regiões: dorso (crista e lombo), ombro e barriga.
  - Pais: Coluna1/2/3, Pelve, EscapulaE/D, BracoE/D e CoxaE/D.
  - Detalhes em `rig/vento/CR_Urso_v2_Rig_Vento_pelo.json`.
- **Mechas:** escolhidas pelo relevo da malha (deslocamento em relação à malha suavizada por Taubin). 446 vértices de ponta se movem.
  - Rosto, boca, orelhas e patas (antebraço/mão/dedos, canela/pé/dedos) ficam com peso 0.
- **Regra de peso exata:**
  - o osso de pelo só herda peso do **próprio pai**;
  - quase todos os vértices já tinham 4 influências; nesses, o `Pelo*` assume todo o peso do pai, e só nas pontas.
  - Com o `Pelo*` parado, a matriz dele é a do pai, então a malha fica idêntica.
- **Tentativas descartadas (medidas):**
  - tirar peso de todos os ossos;
  - liberar vaga movendo a menor influência, o que mudava a malha até 0,58 stud no Deitar/Comer.
- **`anim_urso.py`:** uma linha nova faz o `Pelo*` contar como a região do pai na calibração do Deitar. Sem ela, os vértices `Pelo*` eram lidos como "pata" pelo prefixo "Pe". Com o rig original o resultado é byte a byte igual (os 18 JSON foram regenerados e comparados).
- **QA (Blender):**
  - os 18 clipes assados na variante têm os 31 canais idênticos aos atuais; os `Pelo*` ficam em identidade em todos os quadros;
  - malha deformada sem vento × original, a cada 6 quadros de todos os clipes: diferença **0,0000** e chão **0,0000**;
  - GLB `rig/vento/export/CR_Urso_Silvestre_v2_Rig_Vento.glb`: `VALIDO`, 45 ossos, ≤ 4 influências, as mesmas 4 malhas e tris.
- **Balanço** (`rig/vento/balanco_vento.py`; a mesma fórmula servirá para o script do cliente no Roblox):
  - giro em torno de cross(direção do osso, vento), ang = 9° × I × (0,55 + 0,30·sen + 0,15·sen harmônico), 0,9 Hz, fase pela posição ao longo do vento;
  - deslocamento máximo de vértice: fraco (I=0,4) 0,09 stud; forte (I=1) 0,23 stud;
  - rosto, patas e boca: 0.
  - Parâmetros de teste, não regra do jogo.
- **Demonstração:** `rig/vento/demo/vento_0_fraco_forte.gif` (sem/fraco/forte lado a lado, Repouso) e a prancha `review/PRANCHAS_v2/20_pelo_vento_blender.png` com o mapa de onde mexe.
- **Limitações:**
  - as placas de casca grandes ficam firmes, mas bordas finas de placa e pontas de samambaia também se movem um pouco. Não há classificação de casca por cor nesta malha;
  - a gradação dentro da mecha é limitada (os vértices com 4 influências seguem o `Pelo*` com todo o peso do pai);
  - a juba do pescoço quase não entrou, porque o grupo ficou com menos de 40 vértices.
- **Não feito:**
  - Roblox: reimportação, script do cliente, `GlobalWind`, desempenho em PC/celular e com vários ursos;
  - verificar se o Animator do Roblox respeita o `Transform` dos ossos sem pose na KeyframeSequence.
  - Nada foi publicado.

## Poderes do Urso — Etapa 0 (M0) e Etapa 1: Golpe Colossal (04/11/2026; Blender feito, Studio AGUARDANDO reserva)
**Decisões aprovadas pelo usuário (04/11):**
- **Golpe Colossal:** bate no chão; rachaduras e terremoto; dano a jogadores próximos elegíveis.
- **Rugido Protetor:** velocidade, defesa e regeneração ao urso e ao treinador.
- **Carga Selvagem:** corre até o alvo; ao acertar um jogador, derruba e atordoa temporariamente.
- **Fortaleza Viva:** escudo em área para o urso e o treinador, com resistência própria.
- Elemento, passiva e todos os números continuam **[PENDENTE]**. Nada de Natureza por causa da vegetação, nem fusões.
- Observação: a ficha oficial antiga da Carga fala em "empurrão e quebra de formação"; a decisão nova (queda + atordoamento) foi do usuário em 04/11. O RPG_01 diz "efeitos de controle PvP curtos e resistência temporária a repetições".

**M0 (somente leitura, 19:36, Studio reservado e liberado):**
- **`rpg_roblox`:** 18 KFS do urso; modelo com 31 ossos (9,97 de altura, pivô (0, 2000, 0), olhando para −Z); `ColorMap` clareado; `Anteriores` com 4 backups.
- **Não há sistema de combate, PvP, alianças, energia, atordoamento nem sons do urso no place.** `ServerScriptService` só tem `Bootstrap`, `Data` (DataService) e `Services` (moeda/inventário/concessões). O combate (`Combate_Dragao`, `PvPAtivo`, `ZonaSegura`, `AliadoDe`) existe só no `src/` dos dragões e no outro place. Não foi usado nem alterado.
- Não existe nenhum áudio do urso: rugido, esforço, impacto, ativação e quebra estão todos **faltando**.
- Os arquivos oficiais ATUALIZADO estão na pasta do repositório (não em Downloads direto).

**Clipe (`rig/poderes/`, sem tocar nos 18 aprovados):**
- **`poderes/clipes_poderes.py` + `anim_urso.py`:**
  - `anim_urso.py` só carrega `clipes_poderes.py` com `URSO_PODERES=1`;
  - `URSO_ANIM_SAIDA` salva em `poderes/CR_Urso_v2_Anim_Poderes.blend`;
  - o `CR_Urso_v2_Anim.blend` e o `clipes/manifesto_clipes.json` principais ficaram iguais (md5 conferido).
- **`GolpeColossal`:** 2,3 s, 70 quadros, sem loop. Sequência:
  - preparação (peso para trás);
  - ergue o tronco (pelve −26°) e as duas dianteiras recolhidas junto ao peito;
  - descida acelerada;
  - **contato das duas patas no quadro 33 = 1,10 s** (medido no osso: z 1,044, igual ao repouso; marcado em `eventos.impacto_s`);
  - absorção (afunda 0,38, coluna e cabeça cedem);
  - recuperação com um passo de cada pata (sem deslizar).
- **QA:**
  - IK 0,0005; deriva da sola ≤ 0,019; chão −0,018;
  - boca no nível do Rugir/Ameaça aprovados;
  - 3 picos de aceleração só no quadro do impacto (esperado). Antes estavam a 1150°/s no antebraço; a absorção foi suavizada.
- **Prancha:** `poderes/review/prancha_golpe_colossal.png` (referência, modelo aprovado e quadros-chave), mais GIFs normal e lento (1/3) do Blender.
- Limitação: no quadro 27 a cabeça sai do enquadramento da prancha (só câmera).

**Studio (arquivos prontos, NÃO instalados; Studio ocupado pelo Dragão Sombrio às 19:41):**
- **`studio/poderes/PoderesUrso_Servidor.luau`** (servidor):
  - dono, estado, recarga, energia, ponto de impacto, alvos, dano e trava por ataque (`UltimoAtaqueUrso = id`);
  - o dano sai no instante do contato, lido do `TimePosition` da faixa, também em velocidade lenta;
  - interrompido antes do contato = sem dano e sem efeito;
  - pedido do cliente só do dono.
- **`studio/poderes/EfeitosUrso_Cliente.luau`** (cliente):
  - rachaduras em segmentos posicionados por raycast para baixo, a partir de +2 do chão (não pega teto nem outro andar). Param em parede ou degrau acima de 1,2;
  - não tocam Terrain nem colisão (`CanCollide/CanQuery/CanTouch` falsos) e somem em 4 s;
  - poeira; tremor local de câmera ≤ 0,30, 0,45 s, até 40 studs;
  - qualidade baixa só reduz o visual;
  - gancho de som `SOM_IMPACTO`, vazio.
- **`instalar_golpe_colossal.luau`** (gerado por `gerar_instalador.py`): dados + KFS (Action2, atributo `ImpactoS`) + os 2 ModuleScripts. Nenhum script roda sozinho.
- **`teste_golpe_colossal.luau`:** bateria em Play com cenário temporário:
  - bonecos perto, longe, atrás de parede, numa plataforma +6 e em grupo;
  - spam de 10 pedidos; interrupção; lento a 1/3; sem energia; incapacitado.

**Parâmetros de LABORATÓRIO (provisórios, não aprovados):**
- recarga 8 s; energia 20 (atributo `EnergiaLab`);
- raio 14 studs, horizontal, a partir do chão do impacto;
- altura máxima ±4; dano fixo 40; janela de acerto 0,10 s.

**Propostas (aguardando decisão):**
- **Raio:** círculo horizontal centrado entre as patas, de 12 a 16 studs.
- **Diferença de altura:** ±4, para o terremoto não subir em plataformas nem descer andares.
- **Obstáculos:** linha de visada do chão +1,5 até o centro do alvo; qualquer parede bloqueia.
- **Seleção de alvos:** um acerto por modelo e por ataque, sem limite de alvos.
- **Dano:**
  - opção A, fixo;
  - opção B, queda linear até 50% na borda;
  - integração futura com a fórmula oficial de PvP (fator 0,33 e defesa) quando existir.
- **Elegibilidade:**
  - bonecos `AlvoTesteUrso`;
  - jogadores só com o `PvPAtivo` de laboratório;
  - nunca o dono, quem tem `AliadoDe`, quem está em `ZonaSegura` ou em raid. A integração oficial está **pendente**.

**Studio, instalação e testes (04/11, 20:06–20:12; uso simultâneo autorizado pelo usuário: "Usar rpg_roblox já"):**
- **Instalado (Edit, NÃO salvo):**
  - `Dados_Clipes.Urso_GolpeColossal` (7478 bytes; somas por canal iguais às do Python, ≤ 0,001);
  - KFS `Animacoes.Urso_GolpeColossal` (70 keyframes, 2170 poses, nenhuma faltando, Action2, `ImpactoS = 1,10`);
  - `Urso_v2_Piloto.Poderes.PoderesUrso_Servidor` e `ReplicatedStorage.Urso_v2_Lab.EfeitosUrso_Cliente`.
  - Nenhum script roda sozinho. Os 18 KFS anteriores continuam lá. O cenário de teste existia só no Play.
- **Resultados em Play/PC** (servidor, com o cliente conferido):

| Teste | Resultado |
|---|---|
| Contato | dano em `TimePosition` 1,108, ou 1,28 s reais com a mistura de entrada; ponto no chão entre as patas (0,01; 2000,035; −2,27) |
| Alcance | boneco a ~8 do impacto: dano 40; boneco a 19,7: fora do raio |
| Parede | boneco atrás da parede: bloqueado (`obstaculo(Parede)`); nenhuma rachadura do outro lado |
| Altura | boneco numa plataforma +6: bloqueado (`altura(6,0)`) |
| Vários alvos | 3 bonecos com 1 acerto cada (vida 100 → 60, sem dano duplo por várias partes) |
| Dono | o personagem do dono foi excluído (`dono`). Com `PvPAtivo` desligado, outros jogadores também |
| Spam | 10 pedidos no mesmo quadro: 1 aceito e 9 `ocupado`; pedido depois do fim, dentro da recarga: `recarga` |
| Interrupção | interrompido a 0,6 s: eventos `inicio, interrompido`, nenhum dano e nenhum efeito |
| Lento (1/3) | contato em `TimePosition` 1,101 (mesmo tempo de clipe), 3,45 s reais, dano 1× |
| Recusas | sem energia: `energia`; incapacitado: `incapacitado` |
| Pedido do cliente | dono: aceito (efeito recebido); outro dono: `recusado nao_dono` |
| Rachaduras | 54 peças rentes ao chão (y 2000,020–2000,055, chão em 2000,0); 0 peças depois de 4,5 s; nenhuma no golpe interrompido |

- **Capturas:** `rig/poderes/review/studio_golpe_colossal_frente.jpg` e `_tras.jpg`.
- **Não testado:**
  - celular, emulação e vários ursos ao mesmo tempo;
  - jogador real como alvo com PvP;
  - terreno irregular e encosta; andares com teto;
  - som (não existe).
- O tremor de câmera foi ligado, mas não medido em captura.
- **Visual das rachaduras:** traços escuros finos. É provisório e pode melhorar com textura própria, quando houver.

**Golpe Colossal v2 (04/11, pedido do usuário: "antes do urso bater no chão ele deve dar um rugido … rachaduras com maior alcance e mais reais … levantar e descer com tudo"):**
- **Clipe** (`poderes/clipes_poderes.py`; v1 em `Anteriores.GolpeColossal_v1` no Studio e descrita acima): 3,2 s, 97 quadros.
  - ergue bem mais (pelve −40°, patas a 6,2 de altura, recolhidas no peito);
  - **ruge no alto** de 1,00 a ~1,8 s: boca a 40°, cabeça trazida para a frente (o rugido lê de frente, perto da pose da referência), tremor de 11 Hz;
  - **desaba em 0,2 s com aceleração** e as duas patas tocam o chão no **quadro 58 = 1,933 s** (osso z 1,044, igual ao repouso);
  - absorção mais funda e recuperação com passos.
  - Eventos no JSON e no KFS: `RugidoS = 1,0`, `ImpactoS = 1,9333`.
  - QA: IK 0,0005; deriva da sola ≤ 0,029; chão −0,02; picos só no quadro do contato.
  - Os 18 clipes aprovados continuam iguais (md5).
- **Rachaduras v2** (`EfeitosUrso_Cliente.luau`):
  - alcance de 90% do raio do golpe;
  - 8 fendas irregulares que crescem do centro para fora (45 studs/s), afinam até a ponta e ramificam (30%);
  - fenda escura com borda levantada na cor do chão (lida do raycast);
  - afundamento central, 9 placas de chão inclinadas e 14 pedras que saltam e assentam (só visual);
  - poeira ao longo das fendas.
  - Placas e pedras também respeitam parede. Duração de 6 s, com 1,5 s de fade.
  - Qualidade baixa: 5 fendas / 5 placas / 6 pedras.
- **Servidor:** evento `rugido` para som/efeito em `RugidoS`. O dano continua só no contato.
- **Studio (20:29–20:38, mesmo esquema de uso simultâneo; NÃO salvo):**
  - dados (9765 bytes) e KFS (97 keyframes, 3007 poses).
  - Uma linha de canal (PeD|3) chegou errada no primeiro envio, por erro de cópia meu. Foi detectada pela soma por canal e corrigida: −0,0188 contra −0,0184 no Python.
  - Os módulos foram atualizados (servidor por patch com âncoras).
- **Resultados em Play/PC:**
  - **Golpe:** contato em `TimePosition` 1,933; 3 bonecos atingidos (perto e grupo); os de longe, atrás da parede e na plataforma não foram atingidos;
  - **Rugido:** evento de rugido recebido no cliente;
  - **Rachaduras:**
    - **285–290 peças, alcance de 11,2–11,5 studs** (antes, cerca de 4);
    - rentes ao chão (y +0,065 a +0,083), nenhuma além da parede, 0 peças depois de 6,5 s;
  - **Interrupções:** interrompido durante o rugido = `inicio, interrompido` (sem dano nem rachadura);
  - **Lento (1/3):** contato em 1,950, 5,95 s reais.
- **Pranchas e capturas:** `poderes/review/prancha_golpe_colossal_v2.png` (referência, modelo aprovado e resultado), GIFs `golpe_colossal_v2_normal/lento`, `studio_gc_v2_rugido/rachaduras/floresta_capim.jpg`.
- **Achado:** num chão de capim real da Floresta (teste só no Play, urso levado para (40, 42,7, 0)), **o capim do cliente cobre as rachaduras quase por completo**. Possíveis saídas, só com aprovação:
  - abaixar ou esconder o capim no raio durante o efeito, o que mexe no sistema de capim do bioma (arquivo compartilhado);
  - fendas e placas mais altas;
  - mais poeira e pedras acima do capim.
- **Desempenho:** cerca de 290 peças por golpe no PC, sem medição de FPS; celular não testado. Possível redução: uma peça por segmento nas pontas.

**Rachaduras v3 (04/11, pedido do usuário: "Rachaduras mais altas"; Studio 20:43–20:53, NÃO salvo):**
- **Medição:** o capim da Floresta não é feito de peças; é a grama do próprio terreno, sem peças para medir.
  - Calibrei com peças vermelhas de 0,5 / 1 / 1,5 / 2 / 3 studs no capim (`poderes/review/studio_calibracao_capim.jpg`): **o capim cobre até cerca de 2 studs**; só as de 2 e 3 aparecem.
- **Mudança** (`EfeitosUrso_Cliente.luau`; Studio conferido por soma de bytes: 14414 bytes, soma 156300, igual ao repositório):
  - **terra levantada:** dos dois lados de cada fenda, placas de solo inclinadas para fora, na cor de terra exposta (marrom 96/74/52, com 20% da cor do chão);
  - **altura conforme o chão:** até **2,4 studs sobre Terrain Grass/LeafyGrass** e **0,8 nos demais chãos**, sempre baixando do centro para a ponta;
  - placas centrais maiores e mais inclinadas, pedras maiores, poeira mais alta.
- **Resultado (Play/PC):**
  - **chão liso** (laboratório): lê como terra rachada com bordas levantadas, alcance de cerca de 11 studs (`studio_gc_v3_chao_liso.jpg`);
  - **capim real**: com 2,4 (e até 2,8 em teste), a terra levantada **aparece só perto do centro**; ao longo das fendas o capim denso ainda esconde a maior parte (`studio_gc_v3_capim.jpg`).
  - Com 2,4 studs num chão liso, vira um amontoado de placas (testado e descartado; por isso a altura conforme o chão).
  - Até 445 peças por golpe no capim; cerca de 300 no chão liso.
- **Conclusão:** sem mexer no capim, as fendas inteiras não aparecem no capim alto.
- **Opções (decisão do usuário):**
  - aceitar a leitura atual no capim (centro levantado + poeira + pedras);
  - mais poeira e pedras acima do capim ao longo das fendas;
  - estudar como o capim do bioma é desenhado, para escondê-lo localmente durante o efeito. É o sistema compartilhado do bioma/terreno, então exige autorização, e pode não ser possível sem editar o terreno, o que está proibido.
- **Prancha:** `poderes/review/prancha_rachaduras_v3.png`.

**Erupções v4 (04/11, pedido do usuário: "Mais poeira e pedras"; Studio 20:59–21:02, NÃO salvo):**
- **Mudança** (`EfeitosUrso_Cliente.luau`; Studio conferido por soma de bytes: 17977 bytes, soma 443387, igual ao repositório):
  - ao longo das fendas, a cada 3 segmentos, um ponto de **erupção** no ritmo em que a fenda cresce;
  - até **14 erupções** espaçadas no mínimo 2,2 studs (6 em qualidade baixa), fendas principais primeiro;
  - cada erupção tem uma **coluna de poeira** que sobe acima do capim (10 partículas, de 1,6 a 5,5 de tamanho, 1,2 a 2,2 s) e **3 pedras arremessadas** de 2,5 a 4,5 studs de altura (2 em qualidade baixa), que caem perto, com checagem de parede, e somem com o resto;
  - a poeira fraca que existia ao longo das fendas foi substituída pelas erupções.
- **Resultado (Play/PC):**
  - **capim da Floresta:** 578 peças, 14 erupções, chão `Grass`, 0 peças depois de 6,6 s. Cerca de 0,6 s depois do contato a nuvem de poeira e as pedras voando aparecem bem acima do capim (`studio_gc_v4_capim.jpg`). Isso resolve a leitura do terremoto no capim;
  - **chão liso:** terra rachada, poeira e pedras (`studio_gc_v4_chao_liso.jpg`).
  - Prancha: `poderes/review/prancha_golpe_colossal_v4.png`.
- **Limitações:**
  - as pedras são blocos simples (sem malha de pedra própria);
  - até cerca de 580 peças por golpe no capim (mais as partículas), sem medição de FPS; celular não testado;
  - a captura precisa ser feita ~0,5–1 s depois do contato (antes disso a poeira ainda está baixa).

**Rachaduras v5 (04/11, pedido do usuário: "aumente mais, e não só a frente, mas sim em volta dele, 3x mais … em volta de todo seu corpo"; Studio 21:29–21:37, NÃO salvo):**
- **Mudança** (`EfeitosUrso_Cliente.luau`; Studio conferido por soma de bytes: 20370 bytes, soma 635136, igual ao repositório):
  - **fendas do corpo:** 14 fendas saindo do **contorno inteiro do corpo** (elipse 3,8 × 7,2 em volta do pivô do urso, apontando para fora), mais 6 fendas curtas do ponto das patas;
  - **alcance:** 2,45 × o raio do golpe (~34 studs com raio 14, cerca de **3× a v4**);
  - **menos peças longe:** o passo do segmento cresce com a distância (+0,075 por stud) e só há ramificação de 1º nível (16%);
  - **erupções:** até 32 erupções de poeira e pedras, espaçadas ≥ 3,5 studs, em volta do corpo todo; tremor de câmera até 90 studs.
- **Defeito encontrado e corrigido:**
  - **Sintoma:** na 1ª versão um lado ficava sem fendas.
  - **Causa:** o `Debris` do Roblox guarda no máximo cerca de 1000 itens e apaga os mais antigos. Com cerca de 2300 peças, só 967 apareciam.
  - **Correção:** as peças agora são removidas por `task.delay` próprio (o `Debris` ficou só para os poucos Attachments de poeira e som).
- **Resultado (Play/PC):**
  - **chão liso:** cerca de 1090–1180 peças, **12 de 12 setores em volta do corpo**, alcance de **38,8 studs** do pivô, 32 erupções, 0 peças depois de 6,7 s (`studio_gc_v5_chao_liso.jpg`);
  - **Floresta:** as fendas param nos troncos e nos colisores das árvores (regra de parede); poeira e pedras aparecem no capim (`studio_gc_v5_floresta.jpg`).
  - Prancha: `poderes/review/prancha_golpe_colossal_v5.png`.
- **Atenção / decisão pendente:**
  - **o raio de DANO continua 14 (LAB)**: o visual agora vai até cerca de 34–39 studs. O jogador pode achar que a área de dano é a das rachaduras. Opções: ampliar o dano para o mesmo raio ou manter o dano no raio menor;
  - **desempenho:** cerca de 1100–1200 peças por golpe, sem medição de FPS; celular não testado (em qualidade baixa: 4+8 fendas, 12 erupções).

**Raio de dano ampliado (04/11, pedido do usuário: "amplie o raio"; Studio 21:38–21:40, NÃO salvo):**
- **Servidor** (`PoderesUrso_Servidor.luau`): `raio = 38` (LAB, provisório), medido do **centro do corpo** (pivô do urso, na altura do chão do impacto), não mais do ponto das patas (antes 14). A linha de visada também sai do centro do corpo (+1,5).
  - Diferença de altura ±4, um acerto por modelo e por ataque e a elegibilidade continuam iguais.
- **Cliente:** `alcance = 0,87` do raio, a partir do contorno do corpo (~33 studs), para o visual acompanhar o dano.
- Os dois módulos no Studio foram conferidos por soma de bytes (servidor 10330/862426, cliente 20439/641820).
- **Teste (Play/PC), contato em 1,933:**

| Alvo | Resultado |
|---|---|
| Frente a 30 | acerto |
| **Trás a 30** | acerto |
| Lado a 36 | acerto |
| Perto a 8 | acerto |
| Longe a 42 | `fora_raio(42,0)` |
| Atrás de parede a 25 | `obstaculo(Parede)` |
| Plataforma +6 | `altura(6,0)` |
| Dono | excluído |

  - Vida 100 → 60 nos atingidos, sem dano duplo.
  - Captura: `poderes/review/studio_gc_raio38_alvos.jpg`.
- **Para decisão de balanceamento:** raio de 38 é muito grande para dano em área num PvP com meta de 105–150 s. É número de laboratório, não aprovado.

**Alcance 2× (04/11, pedido do usuário: "aumente 2x mais o alcance"; Studio 21:56–22:00, NÃO salvo):**
- **Servidor:** `raio = 76` (LAB), medido do centro do corpo (era 38).
- **Cliente:**
  - fendas acompanham o raio (fração 0,87 a partir do contorno), com cerca de 66 studs;
  - o passo cresce 0,10 por stud;
  - 44 erupções espaçadas ≥ 5,5;
  - tremor de câmera até 160 studs.
- Os dois módulos foram conferidos no Studio por soma de bytes (servidor 10381/866227, cliente 20566/652057).
- **Teste (Play/PC):**
  - **dano**, com chão temporário de 220 studs só no Play: frente 40, trás 60, lado 72 e perto 10 atingidos; 82 `fora_raio`; dono excluído;
  - **visual na Floresta** (campo aberto em (−75, 44,6, −50)): **1671 peças, alcance de 67,6 studs, 12/12 setores, 44 erupções**; as fendas param nos troncos.
  - Captura: `poderes/review/studio_gc_raio76_floresta_topo.jpg`.
- **Atenção:**
  - **raio de 76 é enorme** (maior que muitos campos de batalha): é número de laboratório e precisa de revisão de balanceamento antes de qualquer uso real;
  - **desempenho:** cerca de 1700 peças por golpe no PC, sem FPS medido; celular não testado (qualidade baixa reduz).

## Poderes do Urso — Etapa 2: Rugido Protetor (04/11/2026; Golpe Colossal APROVADO pelo usuário: "Aprovar e seguir")
**Decisão aprovada:** o rugido concede velocidade, defesa e regeneração ao **urso e ao treinador**. Não vale para outros aliados. Todos os números são **LAB (provisórios)**.

**Clipe `RugidoProtetor`** (`poderes/clipes_poderes.py`), 3,0 s, 91 quadros, sem loop:
- **inspira e o peito expande** pela coluna (até 0,85 s), sem tirar as patas do chão;
- **ruge de frente** de 0,70 s a ~2,35 s: pescoço estica para a frente, focinho para cima, boca a 46°, tremor de 10 Hz e varredura lenta da cabeça de ±14° de um lado ao outro;
- **recupera** e assenta;
- eventos: `RugidoS = 0,70` (som) e `EfeitoS = 1,00` (pico, quando o servidor aplica os bônus).
- Não reaproveita o rugido de dragão nem o `Rugir` aprovado.
- **QA:** IK 0,0022; deriva da sola ≤ 0,002; chão −0,004; boca no nível dos clipes aprovados; 1 pico.
  - Duas versões descartadas: a 1ª tinha IK de 1,27 (o peito erguia os ombros e as patas não alcançavam o chão); outra tinha a cabeça para baixo e a boca escondida.
- Os 18 clipes aprovados e o Golpe Colossal ficaram iguais (md5 do Anim principal conferido).

**Servidor** (`PoderesUrso_Servidor.luau`, bloco em `studio/poderes/bloco_rugido_srv.luau`):
- recarga e estado próprios, separados do Golpe;
- **velocidade:** treinador recebe `WalkSpeed + delta`, e o delta guardado é devolvido exatamente no fim; urso recebe o atributo `VelocidadeBonus_RugidoProtetor` (o urso ainda não tem sistema de movimento);
- **defesa:** atributo `DefesaBonus_RugidoProtetor` mais `M.danoComDefesa` (soma dos `DefesaBonus_*`, teto de 60%). **PENDENTE:** nenhum sistema de dano do place lê isso ainda;
- **regeneração gradual:** ticks de 0,5 s, % da vida máxima por segundo, nunca acima do máximo, nunca em quem tem vida 0. O urso usa os atributos `Vida/VidaMax` (LAB 600);
- **renovação:** sem acúmulo;
- **remoção:** por expiração, morte, urso incapacitado, personagem removido ou saída do jogador. Remove só os modificadores deste poder.
- **Cliente:** onda dourado-esverdeada no pico, mais uma aura discreta (anel nos pés e faíscas) só em quem recebeu o bônus. Sai no "fim" (segurança: duração + 2 s). Gancho `SOM_RUGIDO_PROTETOR`, vazio.

**Parâmetros LAB:**
- duração 10 s, recarga 20 s, energia 30;
- alcance urso → treinador 40 studs (no instante do efeito);
- velocidade +20%, defesa 25%, regeneração 2% da vida máxima por segundo.

**Studio (22:07–22:14, uso simultâneo; NÃO salvo):**
- dados (9230 bytes, soma igual à do Python) e KFS (91 keyframes, 2821 poses, Action2);
- módulos inseridos por âncora e conferidos por soma de bytes: servidor 17698/479577, cliente 24701/994956, iguais ao repositório.
- **Resultados em Play/PC:**

| Teste | Resultado |
|---|---|
| Aplicação | efeito em `TimePosition` 1,033; urso e treinador `aplicado`; WalkSpeed 96 → 115,2 (+20%); defesa 0,25 nos dois; `danoComDefesa(100)` = 75 |
| Regeneração em 5 s | treinador 50 → 67,5 (o 1,2 s extra do teste de teto entrou no intervalo); urso 300 → 361,9 |
| Teto de vida | 99,5 → 100,00/100 |
| Expiração | `expirou`; com outro sistema somando +5 durante o efeito, WalkSpeed terminou em 101 (base + 5): só o delta do rugido saiu; atributos removidos |
| Renovação | 2º rugido com o efeito ativo: `rp_renovado`, WalkSpeed continuou 115,2 (sem acumular) |
| Treinador a 60 studs | urso `aplicado`, treinador `fora_alcance(60,1)`, WalkSpeed sem mudança |
| Interrupção antes do pico | `rp_inicio, rp_interrompido`, sem bônus |
| Spam | 10 pedidos: 1 aceito e 9 `ocupado`; bônus aplicado uma vez só |
| Urso incapacitado | bônus do urso removido (`incapacitado`) |
| Morte do treinador | removido (`morte`) |
| Personagem removido | removido (`removido`) |
| Visual | onda e aura apareceram e sumiram ao expirar |

- **Observações:**
  - a velocidade-base do personagem no place é 96, não o padrão 16 do Roblox (há algo no place que muda isso); o +20% foi calculado sobre o valor atual;
  - **`PlayerRemoving` (desconexão real) não foi testado:** só há 1 jogador no Studio. Foi testada a remoção do personagem.
- **Pranchas:** `poderes/review/prancha_rugido_protetor.png` (referência, modelo aprovado e resultado, mais capturas do Studio), `rugido_protetor_normal.gif` (Blender), `studio_rp_*.jpg`.

**Propostas (aguardando decisão):**
- **Magnitude:** velocidade +15 a 20%, defesa 20 a 25%, regeneração 1,5 a 2%/s.
- **Duração:** 8 a 10 s; recarga de 18 a 25 s.
- **Alcance urso ↔ treinador:** 30 a 40 studs, medido só no instante do rugido (o bônus continua se o treinador se afastar depois); alternativa: perder o bônus se ficar a mais de 60.
- **Renovação:** renova a duração, nunca soma.
- **Cancelamento:** o próprio jogador não cancela; ao urso ser atordoado antes do pico, não aplica.
- **Morte e desconexão:** remove na hora; ao renascer não volta.

**Pendências:**
- sons (rugido protetor);
- integração da defesa com o combate oficial;
- velocidade real do urso (quando houver locomoção/IA);
- teste de desconexão com 2 jogadores;
- celular;
- o anel da aura talvez esteja forte demais (Neon a 0,55); dá para deixar mais sutil.

**Efeitos v2 do Rugido Protetor (04/11, pedido do usuário: "partículas, algum efeito especial que sai do treinador e do urso, e algum efeito especial na hora do rugido"; Studio 22:21–22:27, NÃO salvo):**
- **Cliente** (`EfeitosUrso_Cliente.luau`, bloco `bloco_rugido_cli.luau`; Studio conferido por soma de bytes: 31810/577450, igual ao repositório).
- **Cores âmbar/douradas neutras:** o elemento continua [PENDENTE]; sem folhas nem raízes.
- **No rugido:**
  - **ondas de som:** 9 discos de luz translúcidos (0,78) que saem da boca a cada 0,16 s, avançam 16 studs e crescem até 11;
  - **sopro** de partículas para a frente;
  - **clarão** na cabeça, que diminui em 1,5 s;
  - **poeira** levantando em volta das patas.
- **No pico:** onda no chão mais uma **coluna de 90 partículas douradas** que sobe de cada alvo (urso e treinador).
- **Bônus ativo:**
  - **6 focos em volta do corpo**, girando devagar em espiral, de onde sobem brasas douradas e um véu de energia leve. Ficam fora da malha (de dentro do urso nada aparecia, testado);
  - brilho (PointLight) e anel fino nos pés.
  - Tudo sai no "fim" do bônus.
- **Qualidade baixa:** metade dos focos, das ondas e das partículas.
- **Testado em Play/PC** (laboratório e Floresta): os efeitos aparecem e somem.
  - As ondas de som cobriam o treinador com transparência 0,55; subi para 0,78.
- **Clipe:** `poderes/review/clipe_rugido_protetor_efeitos.gif`. Prancha: `prancha_rugido_protetor_efeitos.png`.
- **Pendente:** som; FPS e celular não medidos.

**Efeitos v3 (azul) do Rugido Protetor (04/11, pedido do usuário: "aura saindo do rugido do urso ... aura azul em volta dos dois, não um redondo em volta deles"; Studio 22:29–22:40, NÃO salvo):**
- **Só o cliente mudou:** `rig/studio/poderes/EfeitosUrso_Cliente.luau` (33099 bytes; a soma confere com o Studio). O servidor não mudou.
- **Rugido:**
  - 9 ondas azuis em disco Neon saem da boca, com transparência 0,72 e alcance de 16 studs;
  - sopro na boca, clarão na cabeça e poeira nos pés.
- **Efeito (1,0 s):** nuvem de energia azul, sem disco no chão.
- **Aura ativa (urso e treinador), sem anel nem círculo no chão:**
  - um Highlight azul acompanha o contorno do corpo (Fill 0,76, contorno pulsando, Occluded);
  - 6 focos de faíscas e fumaça azul giram em volta do corpo (attachments no Terrain);
  - uma PointLight azul.
- **Testado em Play/PC (Floresta):**
  - o buff foi aplicado aos dois (WalkSpeed +19,2) e expirou normalmente;
  - aura visível nos dois.
- **Duração:** durante as capturas foi usada temporariamente uma duração LAB maior e depois devolvida para 10 s / recarga 20 s.
- **Clipe:** `poderes/review/clipe_rugido_protetor_azul.gif`. Quadros: `rugido_protetor_azul_rugido_floresta.png`, `rugido_protetor_azul_aura_floresta.png`.
- **Pendente:** som; FPS e celular não medidos; o place não está salvo.

**Rugido Protetor APROVADO pelo usuário (04/11: "Aprovar e seguir")** — com o visual v3 azul. Os números continuam LAB.

**Etapa 3 — Carga Selvagem: PROPOSTA (04/11, aguardando aprovação; nada implementado)**
- **Base oficial:** "avanço pesado de curto/médio alcance com empurrão e quebra de formação".
- **Pedido do usuário:** o urso corre até o alvo, derruba o jogador e aplica atordoamento temporário.
- A proposta completa está na resposta do chat de 04/11. Pontos principais:
  - alvo travado validado pelo servidor; sem alvo, carga reta;
  - trajeto por varredura (Blockcast) a cada passo, sem Touched e sem teleporte;
  - curva limitada; perde o alvo por ângulo, distância ou parede;
  - queda: FallingDown no cliente do alvo + trava do servidor com prazo;
  - imunidade a nova queda depois de levantar;
  - dano, empurrão e lançamento ficam PENDENTES.

**Carga Selvagem — proposta APROVADA (04/11: "Aprovar proposta"). Passo 1: clipes no Blender (sem Studio)**
- **Três clipes novos** em `rig/poderes/clipes_poderes.py` (no lugar; o servidor move o urso):
  - `CargaInicio`, 1,04 s: abaixa e joga o peso para trás por 0,36 s, depois acelera em 2 ciclos. O último quadro é o quadro 0 da corrida;
  - `CargaCorrida`, loop de 0,34 s: galope pesado com cabeça baixa, ombros à frente e corpo mais baixo, a ~29,4 studs/s sem escorregar (parâmetro técnico);
  - `CargaImpacto`, 1,6 s: ombrada com o evento `impacto_s` = 0,10 s, freada curta, peso nas traseiras, sacode a cabeça e volta ao repouso;
  - sem acerto, o jogo usa a `Frenagem` aprovada.
- **Velocidade:** a proposta dizia ≈50 studs/s. A patas presas, o clipe aguenta ~29 studs/s. Acima disso as patas escorregam, ou o clipe tem de tocar mais rápido. A decisão fica para o teste no Studio.
- **Gerados juntos** com GolpeColossal e RugidoProtetor no `CR_Urso_v2_Anim_Poderes.blend`. Os JSONs desses dois saíram idênticos byte a byte.
  - Erro: uma primeira execução partiu do `CR_Urso_v2_Anim.blend` em vez do `Rig` (IK duplicado, erro de 1,5). Foi refeita a partir do `Rig`.
- **QA** (`poderes/qa_carga_selvagem.json`):
  - IK ≤ 0,0005;
  - deriva da sola ≤ 0,06, exceto PeD na CargaCorrida (0,18);
  - chão: sola até −0,027 e garra até −0,004;
  - picos de aceleração nas pernas, normais no galope rápido a 30 qps.
- `qa_urso.py` agora também simula a CargaCorrida com a velocidade do manifesto.

**CargaImpacto v2, ombrada mais forte (04/11, pedido do usuário: "Sim, mais forte"; só Blender)**
- **v1:** contato aos 0,10 s, raiz −0,55, torção de 10°. Estava sutil.
- **Novo tempo:** contato aos **0,20 s** (evento `impacto_s` 0,20, quadro 6). O clipe passa a ter 1,7 s.
- **Sequência:**
  - **armação:** ombro e cabeça recuam e torcem para o lado oposto;
  - **disparo:** em 0,06 s o tronco vai à frente com o **ombro direito na ponta** (raiz −1,1, torção de 18° na Coluna3 e 9° na Coluna2, pescoço −24° e cabeça baixa);
  - **tranco:** recuo curto logo depois do contato;
  - **fim:** freia, senta o peso, sacode a cabeça e volta ao repouso.
- **Passo da MaoD:** a pata dianteira direita (lado do ombro que bate) dá um passo de 1,4 junto com a ombrada (`PASSO_OMB`).
  - Sem o passo, o IK errava 0,69. Com passo de 1,0, errava 0,16.
- **QA:**
  - IK ≤ 0,0005 e deriva da sola ≤ 0,026;
  - chão: sola −0,028 e garra −0,005;
  - boca: arestas esticadas 11 por dentro e 123 por fora, contra 0/71 da v1. Vem da torção do pescoço; nos renders a boca não mostra rasgo. Conferir no Studio.
- **Arquivos:** os 5 clipes de poderes foram regerados juntos; GolpeColossal e RugidoProtetor saíram idênticos.
- **Review** (`poderes/review/`):
  - novos: `carga_impacto_v2_normal.gif`, `carga_impacto_v2_lento_1-4.gif`, `prancha_carga_impacto_v2_frente.png` e `carga_impacto_antes_depois.png`;
  - v1 renomeada para `*_v1_*`.
- `render_clipes.py` ganhou a câmera `cam=frente`.

**Carga Selvagem — passo 2: Studio (servidor + cliente) e testes (04/11, 23:10–23:55, place rpg_roblox, NÃO salvo)**
- **Clipes no Studio:** `Dados_Clipes` (Urso_CargaInicio/Corrida/Impacto + Perfis_*).
  - Os textos conferem byte a byte com o repositório (5268/431683, 2544/214725, 7731/606116).
  - KFS em `Urso_v2_Piloto.Animacoes`, prioridade Action2. A CargaCorrida é loop; a CargaImpacto tem `ImpactoS` 0,2.
- **Servidor** (`rig/studio/poderes/bloco_carga_srv.luau`, inserido em `PoderesUrso_Servidor`, 34430 bytes / soma 849889, igual no Studio):
  - `M.LAB.CargaSelvagem`: recarga 12, energia 25, alvo entre 8 e 45, curva 90°/s, cone ±35°, perde o alvo a 55, faixa de impacto 3,5;
  - atordoamento 1,5 + levantar 0,6, imunidade 6, dano 0 (PENDENTE), velocidade 29,41 × `escalaVel` 1,0;
  - `M.cargaSelvagem(urso, quem, alvo)`, `M.derrubar` e `M.soltarQueda`;
  - o pedido `Pedido("CargaSelvagem", urso, alvo)` só vale para o dono.
  - A velocidade vem do perfil de cada clipe (Inicio/Impacto/Frenagem × escala).
  - Paredes e degraus: Blockcast e raycast com `RespectCanCollide`, então arbustos sem colisão não contam.
- **Cliente** (`bloco_carga_cli.luau`, inserido em `EfeitosUrso_Cliente`, 40169 / 269652, igual no Studio):
  - poeira nas patas, estouro de poeira e pedras com tremor no impacto e na parede, estrelas de atordoamento;
  - queda local do jogador derrubado (PlatformStand + giro do tombo; GettingUp ao levantar).
- **Backup** dos dois módulos de antes: `ServerStorage.Urso_v2_Piloto.Anteriores.Poderes_antes_Carga`.
- **Testes em Play/PC (Floresta), todos com o registro do servidor:**
  - **T1 alvo parado a 25:**
    - travado → contato previsto → derrubado (d 0,7);
    - UpVector do boneco 1,00 → −0,19 (caído) por 1,5 s, WalkSpeed 16→0→16 e JumpPower 50→0→50;
    - levantou, imune por 6 s.
  - **T2 imunidade:** a segunda carga logo depois resultou em `imune`, sem queda.
  - **T3 alvo móvel** (anda para o lado): o urso virou 33,7° e derrubou.
  - **T3c alvo rápido** (45 studs/s): perseguido com curva limitada, não alcançado; erro em 45 studs + freada.
  - **T3b fuga atrás de um morro:** perdeu o alvo por `sem_visada` (morro de Terrain, conferido por raycast).
  - **T4 parede:** parou com o peito exatamente na face da parede (pivô −65,5, face −71, frente 5,5), estouro de poeira e ReacaoImpacto.
  - **T5 sem alvo:** erro em 45,2 studs. A Frenagem anda mais 13,7, total 58,9.
  - **T6 dois bonecos em fila:** só o primeiro (que entrou na frente) caiu.
  - **T8 morte na queda:** liberado com motivo `morte`.
  - **T7 spam:** a segunda carga e o Golpe durante a carga deram `ocupado`; depois do fim, `recarga` (12 s).
  - **T12 sem energia:** `energia`.
  - **T9 validação do alvo:** alvo a 5 deu `alvo_perto_demais` (recusa sem custo); alvo a 68° do cone deu carga reta.
  - **T11 interrupção:** `interrompido`, e o urso para na hora.
  - **T10 jogador como alvo** (dono trocado e PvPAtivo só durante o teste, depois restaurados):
    - FireClient da queda: estado PlatformStanding, UpVector 0,10;
    - WalkSpeed 96→0→96 exato; levantou (Running).
- **Bugs achados e corrigidos nos testes:**
  - **(a)** arbusto sem colisão contava como parede e tapava a visada → `RespectCanCollide`;
  - **(b)** parede depois do contato cortava o clipe do impacto → no impacto o urso só para;
  - **(c)** antes de instalar: "desviou" se repetiria a cada quadro → marca `conferiu`.
- **Capturas** (`poderes/review/`): `studio_cs_1..4.jpg`, `prancha_carga_selvagem_studio.png` e `clipe_carga_selvagem_studio.gif`.
- **Limitações:**
  - no capim alto da Floresta, a poeira e o boneco caído ficam bem escondidos (o capim é do cliente e cobre a altura das patas);
  - desconexão real e duas pessoas de verdade não testadas (o jogador alvo foi simulado trocando o dono);
  - celular e FPS não medidos; sem som;
  - dano, empurrão e lançamento continuam PENDENTES;
  - o place NÃO foi salvo pelo assistente.

**Carga Selvagem: vídeo real do Play (05/11, pedido do usuário: "Não consegue fazer um vídeo de verdade?"; Studio rpg_roblox, só Play, nenhum script mudado)**
- Gravação da janela do Studio a ~29 quadros/s (PrintWindow, Python/PIL), codificada em MP4 H.264 pelo Blender 5.2. Nada foi instalado.
- `poderes/review/carga_selvagem_studio_video_frente.mp4`: 7 s, 1738×802, de frente, velocidade real.
- `poderes/review/carga_selvagem_studio_video_frente_lento.mp4`: a mesma tomada a 12 quadros/s (~0,4×).
- `poderes/review/carga_selvagem_studio_video_lado.mp4`: de lado, velocidade real.
- Cena: boneco R15 parado a 26 studs. Só no Play, a recarga LAB ficou em 0.
- Visto no vídeo: antecipação, corrida, ombrada, estouro de poeira, estrelinhas, boneco caído no capim e levantando.
- Limitações:
  - não há empurrão (pendente), então o boneco cai no lugar e fica em parte atrás do urso no plano lateral;
  - sem som;
  - PC apenas.

**Carga Selvagem v3: cabeça baixa, ombro exposto, ombro sobe no impacto (05/11)**
- Pedido do usuário: "na corrida, ele abaixe sua cabeça e deixe seu ombro mais exposto na direção do alvo, e ao colidir suba o ombro no alvo e o alvo se for pequeno, deve voar um pouco mais longe".
- Só Blender; o Studio ainda tem a v2.
- **Corrida e Início:**
  - tronco torcido com o ombro direito apontado ao alvo (Coluna3 Z 12°, Coluna2 Z 6°);
  - cabeça baixa (Pescoço X 30°, antes 12°), recolhida para o lado oposto (pescoço −17° em Z).
  - Acima de 12° de torção, o IK da corrida erra (0,08 a 0,15).
- **Impacto:**
  - no contato o peito empina (Pelve −5°, Coluna3 −10°, Coluna2 −5°) e o ombro rola para cima (+6°);
  - a dianteira direita sobe junto (1,6 stud); a esquerda dá um passo curto e segura o peso;
  - a cabeça quase não sobe.
- **Parâmetros** (env, LAB): `TORS_CAR`, `CAB_BAIXA`, `LEV_*`, `MD_H`, `ME_H/ME_X/ME_T`, `PA_*`, `OMB_Z`.
- **QA:**
  - IK ≤ 0,0005 nos 3 clipes; com a pata direita plantada, o IK errava 1,3;
  - deriva igual à v2;
  - chão: sola −0,028;
  - boca: 11/140;
  - picos de aceleração: 22 contra 33 da 1ª tentativa.
- GolpeColossal e RugidoProtetor saíram idênticos (`cmp`).
- **Backup da v2:** `poderes/antes_carga_v3/`.
- **Vídeos** (lado a lado v2 × v3), em `poderes/review/`: `carga_v3_blender_antes_depois_{frente,34}.mp4` e `_lento.mp4`.
- **Pendente:**
  - lançar alvos pequenos mais longe (lógica do servidor, números a aprovar);
  - enviar a v3 ao Studio.

**Carga v3b: arrancada que racha o chão + v3 no Studio (05/11; Studio rpg_roblox, NÃO salvo)**
- Pedido do usuário: "ao ativar a habilidade o urso empurra o chão, fazendo-o rachar e sai correndo".
- **Blender** (`CargaInicio`):
  - agacha mais fundo nas traseiras;
  - em 0,34 s empurra o chão: o corpo dispara à frente, a frente sobe 6° e a cabeça afunda;
  - evento `empurrao_s` 0,34 (quadro 10);
  - IK ≤ 0,0005;
  - CargaCorrida e CargaImpacto são idênticas à v3 (`cmp`). Backup em `poderes/antes_carga_v3b/`.
- **Studio:**
  - `Dados_Clipes` dos 3 clipes v3 conferidos por soma: Início 5830/477244, Corrida 2745/230941, Impacto 7837/615761;
  - KFS refeitos; `Urso_CargaInicio` tem `EmpurraoS` 0,34;
  - backup em `Anteriores/Poderes_antes_Arrancada`: módulos, KFS e dados da v2.
- **Servidor** (`PoderesUrso_Servidor` 34897/887965, igual ao repositório):
  - na fase início, ao atingir `EmpurraoS` (ou o tempo equivalente), envia `{tipo=CargaSelvagem, fase=arrancada, dir}`.
  - **Bug antigo corrigido:** no 1º uso da sessão o clipe ainda carrega e `Length` vale 0. Por isso o servidor pulava a preparação e ia direto para a corrida, e o impacto e a freada podiam acabar na hora.
  - A troca de fase agora exige `Length > 0`.
- **Cliente** (`EfeitosUrso_Cliente` 45012/655225, igual):
  - `rachaArrancada`: em cada pata traseira, 4 fendas para trás e para os lados (8–13 studs);
  - terra levantada até 2,6 no capim;
  - 9 torrões de terra chutados para trás em arco;
  - poeira na cor de terra, jogada para trás e para cima;
  - tremor curto;
  - tudo some em 5,5 s; nada colide.
  - v1 (fendas de 5–9, poeira na cor do chão) sumia no capim e a poeira saía verde.
- **Teste em Play** (PC, Floresta, 1º uso da sessão):
  - eventos início → arrancada (+0,40 s) → impacto (+1,32 s) → fim;
  - 313 peças de efeito;
  - boneco derrubado.
- **Vídeos:** `poderes/review/carga_v3_arrancada_studio.mp4` e `_lento.mp4`.
- **Pendente:**
  - lançamento dos alvos pequenos, aguardando aprovação dos números;
  - som da arrancada (`SOM_CARGA_ARRANCADA` vazio);
  - celular e FPS não medidos;
  - o place NÃO foi salvo.

**Carga Selvagem: lançamento de alvos pequenos (05/11, aprovado pelo usuário: "Aprovar lançamento"; Studio rpg_roblox, NÃO salvo)**
- **Servidor** (`PoderesUrso_Servidor` 37513/100275, igual ao repositório).
  - Valores em `M.LAB.CargaSelvagem` (LAB):
    - `alturaPequeno` 6,5: alvo com altura do modelo até 6,5 (personagem R15 ~5,5) é lançado; alvo maior só cai no lugar;
    - `lancDist` 12: distância horizontal do arco;
    - `lancAlt` 3,5: altura do arco.
  - Velocidade de arco pela gravidade real: física, sem teleporte.
  - `distSegura`: o servidor confere o trajeto em passos de 2 studs. Para 1 stud antes de parede ou de barranco (sem chão, ou queda maior que 6).
  - NPC: o servidor vira dono da física e aplica o voo. Jogador: o servidor manda `lanc` no evento "Queda"/"cair" e o cliente do próprio jogador aplica.
  - **NoCollisionConstraint** entre as partes do urso e as do alvo enquanto ele estiver derrubado; removidas no `soltar`.
    - Sem isso, o corpo sólido e ancorado do urso ficava por cima do alvo na ombrada e segurava o voo: voo de 3,9 e subida de 0,1.
    - Não usa grupo de colisão (sistema compartilhado).
  - `M.derrubar(mod, dir, id, urso)` ganhou o parâmetro `urso`.
- **Cliente** (`EfeitosUrso_Cliente` 45087/661756, igual): aplica `d.lanc` (Vector3) no "cair".
- **Testes em Play** (PC, Floresta, trecho plano P2 = (−45, 42,9, −40)):

  | Teste | Resultado |
  |---|---|
  | Pequeno | lançamento 11; voo horizontal 14,2 (arco mais rolamento); subiu 3,1; levantou com WalkSpeed 16 de volta |
  | Grande (escala 2,2, altura 12) | sem lançamento; caiu; WalkSpeed 35,2 de volta |
  | Parede 9 studs atrás do alvo | lançamento cortado para 7; parou 1 stud antes da face |
  | Jogador como alvo (dono trocado e PvP só no teste, restaurados) | lançamento 11; voo 13,4; subiu 3,1; PlatformStanding > GettingUp > Running; WalkSpeed 96 de volta |
  | Jogador com o cliente de efeitos desligado (falha do cliente) | sem voo; o servidor liberou no prazo e devolveu o WalkSpeed |
  | Restrições de sem-colisão | 20 criadas, 0 depois de levantar |

- **No ponto antigo de teste** (perto das raízes de uma árvore grande), o servidor cortou o voo para 3, e as raízes seguraram o boneco. O comportamento está correto.
- **Vídeos:** `poderes/review/carga_v3_lancamento_studio.mp4` e `_lento.mp4`, gravados a ~23 quadros/s.
- **Pendente:**
  - dano ainda 0;
  - som;
  - celular e FPS não medidos;
  - não testado com 2 jogadores reais nem com rede lenta: o voo do jogador depende do cliente dele, e só a distância é validada;
  - o place NÃO foi salvo.

**Etapa 4 — Fortaleza Viva: PROPOSTA (05/11, aguardando decisão do usuário; nada implementado)**
- **Aprovado** (pedido de 04/11): escudo em área para o urso e o treinador, com resistência própria. Não é bônus de defesa e não transfere dano para o HP do urso.
- **Ficha histórica:** "proteção de área com movimento lento".
- **Proposta (decisões pendentes, números LAB):**
  1. **Área:** acompanha o urso, que anda devagar (−50% de velocidade). Durante o escudo não usa Carga nem Golpe. Alternativa: área fixa no ponto de ativação.
  2. **Formato:** cúpula baixa de raio 12 studs, centrada no urso. Protege quem da dupla estiver dentro no instante do golpe. Sair da área deixa de proteger; não é preciso estar junto ao ativar.
  3. **Reserva:** uma reserva compartilhada de 300 pontos (LAB). Qualquer golpe em qualquer um dos dois gasta dela. Alternativa: reservas separadas.
  4. **O que bloqueia:** dano de qualquer tipo que venha de fora da cúpula (atacante ou ponto de origem fora). Golpe dado de dentro passa normal.
     - Controle (queda/lançamento) vindo de fora: proposta bloquear também; a decidir.
  5. **Quando quebra:** o golpe que quebra gasta o que resta, e o excedente passa ao alvo normalmente. Nada vai para o HP do urso.
  6. **Tempo:** dura 8 s ou até quebrar; recarga de 25 s a partir do fim; energia 35. Reaplicar com o escudo ativo é recusado: não acumula nem renova. A regeneração do Rugido não recarrega a reserva.
- **Integração:**
  - função de laboratório `M.danoRecebido(alvo, dano, origemPos)`, que aplica escudo, depois defesa, depois HP;
  - ligar ao combate oficial exige mexer em arquivo compartilhado: pendente, pedir autorização.
- **Animação:** `FortalezaInicio` (planta as quatro patas, abaixa, rugido grave curto), `FortalezaAndar` (loop lento e pesado) e `FortalezaFim`. Clipes novos; os 18 aprovados ficam intactos.
- **Visual:** NÃO uma bolha redonda (pedido do Rugido). Opções:
  - (A) parede baixa de energia translúcida saindo do chão no contorno, que trinca conforme a reserva cai e estilhaça na quebra;
  - (B) aura no contorno dos corpos da dupla, mais um anel discreto no chão marcando a área.
  - Cor sem elemento (pendente).
- **Testes planejados:**
  - urso/treinador dentro e fora;
  - consumo pelos dois e golpes simultâneos;
  - quebra com excedente, expiração e reuso;
  - desconexão, morte e limpeza;
  - regeneração sem recarregar.

**Fortaleza Viva: decisões do USUÁRIO (05/11)**
- Respostas:
  - "Aprovo todas, menos o 4, quem estiver dentro do escudo pode receber dano, porém defesa de 75%";
  - item 4: "Só golpe vindo de dentro";
  - visual: "A: parede de energia".
- **Aprovado (números LAB):**
  1. a área acompanha o urso, com −50% de velocidade; sem Carga nem Golpe durante o escudo;
  2. raio 12; protege quem da dupla está dentro no instante do golpe;
  3. reserva compartilhada de 300;
  4. golpe de FORA da cúpula: o escudo absorve tudo e gasta a reserva. Golpe de atacante DENTRO da cúpula: passa, com 75% menos dano, sem gastar a reserva;
  5. na quebra, o excedente do golpe que quebrou passa ao alvo, sem ir para o HP do urso;
  6. 8 s ou até quebrar; recarga de 25 s a partir do fim; energia 35; sem reaplicar nem renovar enquanto está ativo; a regeneração não recarrega.
- **Visual A:** parede baixa de energia translúcida no contorno, que trinca conforme a reserva cai e estilhaça na quebra.
- **Ainda pendente:** controle (queda/lançamento) vindo de fora, porque o item 4 da proposta foi substituído. Até decidir, o controle NÃO é bloqueado.

**Fortaleza Viva — passo 1: clipes no Blender (05/11; Studio não tocado)**
- 4 clipes novos em `poderes/clipes_poderes.py`; os 18 aprovados e os 5 de poderes saíram idênticos (`cmp`):
  - `FortalezaInicio` (1,6 s): as patas dão um passo para fora (dianteiras 0,35, traseiras 0,18); o corpo abaixa até −0,58; rugido grave curto (boca 38°). Evento `ativar_s` 0,80 (quadro 24), quando o servidor liga o escudo;
  - `FortalezaParado` (loop de 3 s): postura firmada respirando;
  - `FortalezaAndar` (loop de 1,8 s): andar lento e pesado, base larga, ginga 3,5; a ~1,59 studs/s sem escorregar (o Andar é 3,23, ou seja −51%);
  - `FortalezaFim` (0,9 s): fecha a base e volta à altura normal.
- **Postura:** pelve +4°, coluna +3/+5°, pescoço +14°, cabeça +4°, orelhas −30°.
- **Backup:** `poderes/antes_fortaleza/`.
- **QA:**
  - IK ≤ 0,0005;
  - deriva da sola ≤ 0,003 nos parados; 0,055 no andar (traseiras);
  - chão −0,024;
  - boca 9/65 no rugido;
  - 0 picos.
- `qa_urso.py` simula `FortalezaAndar` com a velocidade do manifesto.
- **Vídeos:** `poderes/review/fortaleza_viva_blender.mp4` e `_lento.mp4`, de frente e em 3/4.

**Fortaleza Viva — completa no Studio (05/11; pedido do usuário: "ruja com a cabeça mais erguida e o corpo mais firme, e ao rugir partículas devem sair de si, formando o escudo. Complete a habilidade"; Studio rpg_roblox, NÃO salvo)**
- **Blender, `FortalezaInicio` v2:**
  - no rugido: pescoço −30°, Pescoco2 −8°, cabeça −12°, peito (Coluna3) −6°;
  - o tremor caiu de 1,2° para 0,5°; o corpo não afunda no rugido;
  - IK 0,0003;
  - 1 pico (mandíbula abrindo);
  - os outros 8 clipes de poderes ficaram idênticos;
  - backup da v1 em `poderes/antes_fortaleza/v1/`.
- **Studio:**
  - `Dados_Clipes` dos 4 clipes conferidos por soma: Início 5251/406391, Parado 6187/443120, Andar 7485/603860, Fim 3416/273926; Perfis: Andar v=1,59;
  - KFS feitos; Início com `AtivarS` 0,8; Parado e Andar em loop;
  - backup dos módulos em `Anteriores/Poderes_antes_Fortaleza`.
- **Servidor** (`bloco_fortaleza_srv.luau` → `PoderesUrso_Servidor` 45458/764972, igual ao repositório):
  - `M.LAB.FortalezaViva`: recarga 25, energia 35, duração 8, raio 12, altura ±10, reserva 300, `defesaDentro` 0,75, lentidão 0,5;
  - `M.fortalezaViva`: liga em `AtivarS`. No 1º uso espera o clipe carregar; segurança de 2 s;
  - depois do Início, toca o loop Parado e libera `e.acao`, mas Golpe e Carga recusam com "fortaleza"; reaplicar dá "fortaleza_ativa";
  - fim por expirou, quebrou, incapacitado ou removido; toca `FortalezaFim`; a recarga conta a partir do fim;
  - atributos `Fortaleza_Reserva`, `Fortaleza_Ate`, `VelocidadeBonus_FortalezaViva` = −0,5;
  - `M.danoRecebido(alvo, dano, origemPos)`, nesta ordem:
    - protegido dentro e golpe de fora (ou sem origem): a reserva absorve; na quebra o excedente passa;
    - golpe de dentro: −75%;
    - depois a defesa `DefesaBonus_*` (Rugido) e por fim a vida (Humanoid ou atributo `Vida` do urso).
- **Cliente** (`bloco_fortaleza_cli.luau` → `EfeitosUrso_Cliente` 54457/414900, igual):
  - no ativar: estouro de 60 partículas do peito, e 28 fagulhas voam em arco do peito até a base de cada painel; cada painel cresce do chão quando a sua fagulha chega;
  - parede de 28 painéis ForceField âmbar (16 em qualidade baixa), 4,5 de altura, colada no chão por raycast, acompanhando o urso;
  - golpe: o painel mais perto pisca; trincas aparecem abaixo de 2/3 e de 1/3 da reserva;
  - quebra: cacos voam para fora, estouro de partículas e tremor curto;
  - fim: a parede desce e some.
- **Testes em Play** (PC, Floresta, P2):

  | Teste | Resultado |
  |---|---|
  | T1 ativação | reserva 300, velocidade −0,5 |
  | T2 de fora no urso, 100 | 0 aplicado, reserva 200 |
  | T3 de fora no treinador dentro, 50 | 0, reserva 150 |
  | T4 de dentro no treinador, 40 | 10 aplicado, reserva intacta |
  | T4b sem origem, 10 | absorvido |
  | T5 treinador fora da área, 30 | 30 |
  | T6 dois golpes no mesmo quadro (120 + 70, com reserva 140) | quebrou; excedente 50 × defesa do Rugido 25% = 37,5 no urso; depois da quebra, dano normal (7,5 com o Rugido) |
  | T7 Carga e Golpe durante | "fortaleza"; reaplicar dá "fortaleza_ativa" |
  | T8 expiração | 8,9 s do início (ativa em 0,8, mais 8); depois "recarga" |
  | T9 Rugido durante | vida 400 → 418, reserva 140 → 140 (não recarrega) |
  | T10 trincas (4 × 70) | eventos golpe 230/160/90/20 no cliente |
  | T11 incapacitado | fim "incapacitado" |
  | T12 personagem do treinador removido | o urso continua protegido |
  | T13 sem energia | "energia" |
  | Limpeza no cliente | 0 paredes e 0 peças depois |

- **Vídeos:** `poderes/review/fortaleza_viva_studio.mp4` e `_lento.mp4` (ativar com partículas → andar lento com a parede acompanhando → 5 golpes de fora, trincas e quebra).
- **Pendente:**
  - ligar o combate oficial a `M.danoRecebido` (arquivo compartilhado, pedir autorização);
  - controle vindo de fora (decisão);
  - o urso não tem sistema de movimento no place: no teste foi movido à mão com `FortalezaAndar` a 1,59 studs/s;
  - som;
  - desconexão real e 2 jogadores reais;
  - celular e FPS (são 28 painéis movidos por quadro);
  - o place NÃO foi salvo.

**Fortaleza Viva v2: DOMO (05/11; Studio rpg_roblox, NÃO salvo)**
- Pedido do usuário: "escudo em volta de todo o corpo, até no ar; ao algo atingir, animação de trincado e de retenção, com som de retenção; 50% maior; pode ser amarelo; as partículas devem formar o escudo gradualmente; 3-5 s para se formar".
- **Servidor** (`PoderesUrso_Servidor` 46820/873219, igual ao repositório; backup em `Anteriores/Poderes_antes_Domo` e `rig/studio/poderes/antes_domo/`):
  - área = meia esfera de raio **18** (era um cilindro de 12 × 10) em volta do pivô; quem está até 3 abaixo do pivô conta como dentro;
  - `formacao` 4 s: a reserva cresce de 0 a 300; o golpe durante a formação gasta o que já formou e não quebra;
  - a duração de 8 s começa quando o domo termina de se formar; evento `formado`;
  - o golpe só avisa o cliente se absorveu algo; manda `pos` (origem) e `alvoPos`.
- **Cliente** (`EfeitosUrso_Cliente` 57587/670474, igual):
  - domo de 6 anéis com 36 × cos(φ) placas ForceField amarelas (~160; 20 × cos em qualidade baixa), soldadas a uma raiz que segue o urso;
  - **formação gradual:** partículas saem do peito durante 4 s, e uma fagulha por placa voa em arco; as placas aparecem de baixo para cima, em espiral, quando a fagulha chega;
  - **golpe = retenção:** onda de 1 a 11 studs na superfície, placas vizinhas brilham, partículas presas na superfície e som de retenção;
  - **trincas:** 6 por golpe, crescem do ponto em 0,22 s, ficam no domo e são mais longas quanto menor a reserva;
  - **quebra:** cacos para fora, estouro de partículas, tremor e som; **fim:** o domo apaga.
- **Som (PROVISÓRIO):** o projeto não tem áudio do urso. Usa sons que já vêm com o Roblox:
  - retenção: `rbxasset://sounds/impact_water.mp3` a 0,55×;
  - quebra: `impact_explosion_03.mp3` a 0,7×.
  - Não testei se o som toca de fato: a gravação não pega áudio.
- **Testes em Play** (PC):

  | Teste | Resultado |
  |---|---|
  | F1 aos 1 s de formação | reserva 76; golpe de 100 de fora: 76 absorvidos, 24 passaram, sem quebrar |
  | F2 aos 2 s | 75 |
  | F3 formado aos 4,0 s | 224 (300 − 76) |
  | F4 golpe de 30 studs acima | absorvido |
  | F5 atacante no ar dentro do domo | −75% |
  | F6 treinador no ar fora do domo | dano inteiro |
  | F7 golpe de 260 com reserva 174 | quebrou; 86 passaram |
  | F8 tempos | ativa em 0,8 s, formado em 4,8 s, fim em 12,9 s |

- **Vídeos:** `poderes/review/fortaleza_viva_domo_studio.mp4` e `_lento.mp4`. Mostram a formação gradual, golpes do chão e do ar (retenção e trincas no ponto certo) e a quebra.
- **Pendente:**
  - som definitivo;
  - ligar ao combate oficial;
  - controle vindo de fora;
  - celular e FPS (~160 placas, soldadas: 1 CFrame por quadro);
  - o place NÃO foi salvo.

**Fortaleza Viva v3: DOMO DE LINHAS (05/11; só o cliente mudou; Studio rpg_roblox, NÃO salvo)**
- Pedido do usuário: "algo mais como linhas, que vão se formando em volta do urso, e a rachadura 100% no escudo; no vídeo, por o escudo não ser reto, a rachadura fica pra fora".
- **Cliente** (`EfeitosUrso_Cliente` 60562/896359, igual ao repositório; backup em `Anteriores/Poderes_antes_Linhas` e `rig/studio/poderes/antes_linhas/`):
  - **Domo = malha de linhas amarelas Neon** sobre a esfera de raio 18:
    - anel da base, 14 meridianos (8 em qualidade baixa) e paralelos a 20/40/60/75°;
    - trechos de 7,5°, 334 no total, soldados a uma raiz que segue o urso;
    - mais uma película ForceField esférica bem translúcida (0,8).
  - **Formação de 4 s:**
    - o anel da base gira em volta do urso (0–22%);
    - os meridianos sobem da base ao topo (15–75%);
    - os paralelos fecham de baixo para cima (40–91%);
    - cada trecho acende quando a "cabeça" da linha passa, e as fagulhas voam do peito até a cabeça da linha;
    - a película aparece no fim (70–100%).
  - **Trincas sobre a superfície:** cada trinca anda pela esfera em trechos de 0,45 stud reprojetados no raio + 0,06, com desvios, e acende do ponto para fora.
    - Medido em Play: as 228 peças de trinca ficaram todas a 18,059 do centro, com a esfera em 18,00 (na v2 ficavam tangentes e saíam da curva).
  - **Retenção:** um anel de luz se abre SOBRE a esfera (20 trechos reprojetados, ângulo de 2° a 22° em 0,5 s); linhas vizinhas brilham; a película pisca; partículas; som provisório.
  - Bug corrigido antes do teste: a limpeza dos anéis de retenção usava o campo errado.
- **Servidor:** sem mudanças (46820/873219).
- **Teste em Play** (PC):
  - eventos inicio, ativou, formado, 4 golpes absorvidos, quebrou;
  - linhas acesas ao longo da formação: 2, 55, 132, 278, 329 e 334 de 334;
  - 0 peças restantes depois da quebra.
- **Vídeos:** `poderes/review/fortaleza_viva_linhas_studio.mp4` e `_lento.mp4`.
- **Pendente:**
  - FPS e celular (334 trechos soldados, 1 CFrame por quadro; as trincas acumulam até ~230 peças antes da quebra);
  - som definitivo;
  - o place NÃO foi salvo.

**Fortaleza Viva: reserva dobrada (05/11)**
- Pedido do usuário: "quero o dobro de resistência, depois conversamos sobre valores".
- `M.LAB.FortalezaViva.reserva` passou de 300 para **600** (LAB). `PoderesUrso_Servidor` 46859/876001, igual ao repositório.
- **Play:** o domo formou com 600 e quebrou no 9º golpe de 70; o excedente de 30 foi para a vida do urso (600 → 570).
- Valores a conversar depois.
- **As quatro ativas do pedido estão prontas no laboratório** (Golpe Colossal, Rugido Protetor, Carga Selvagem, Fortaleza Viva).
- **A passiva continua PENDENTE:** não há passiva oficial. As opções vão ao usuário como proposta.

**PASSIVAS: Fúria do Protetor + Faro do Protetor (05/11; escolha do usuário: "Fúria do protetor, porém 30% de velocidade. Faro do protetor"; Studio rpg_roblox, NÃO salvo)**
- O usuário não falou da força: mantive os 15% da proposta.
- Duas passivas; números LAB, ainda a conversar.
- **Servidor** (`bloco_passivas_srv.luau` → `PoderesUrso_Servidor` 54228/505623, igual ao repositório; backup em `Anteriores/Poderes_antes_Passivas` e `rig/studio/poderes/antes_passivas/`):
  - **Fúria do Protetor:**
    - gatilho: vida do treinador ≤ 30% (HealthChanged no servidor), com o treinador a até 20 studs do urso;
    - efeito por 6 s: `VelocidadeBonus_FuriaProtetor` 0,30 e `ForcaBonus_FuriaProtetor` 0,15;
    - a força entra no dano do Golpe Colossal via `M.forcaMult`;
    - recarga de 30 s; não renova; termina por expiração, incapacitação ou remoção;
    - `M.velocidadeBonus(urso)` soma os `VelocidadeBonus_*` com teto de 0,5.
  - **Faro do Protetor** (a cada 0,5 s):
    - procura, a até 25 studs do urso, inimigos escondidos: invisível (`PassoInvisivel` ativo, só leitura), `Furtivo`, ou sem linha de visada da cabeça do treinador;
    - marca só para o treinador por 3 s; recarga de 15 s; sopro no focinho do urso para todos;
    - inimigos considerados: outros jogadores (com PvP), alvos de teste e modelos com `PassoInvisivel`.
  - Ursos considerados: tag `UrsoLab`, posta no piloto `Teste_Urso_v2.Urso_Silvestre_v2_Piloto`.
- **Cliente** (`EfeitosUrso_Cliente` 66035/340546, igual):
  - Fúria: Highlight vermelho-alaranjado que pulsa, com brasas e vapor;
  - Faro: Highlight amarelo AlwaysOnTop mais um marcador redondo acima do alvo (aparece mesmo invisível), só no cliente do treinador.
- **Testes em Play** (PC):

  | Teste | Resultado |
  |---|---|
  | U1 treinador a 40 com 25% | sem fúria |
  | U2 treinador perto com 25% | fúria; velocidade 0,30, força 1,15 |
  | U3 Golpe durante a fúria | 40 → 46 (× 1,15) |
  | U4 teto | 0,30 + 0,20 (Rugido) + 0,30 (bônus de teste) = 0,80 → 0,50 |
  | U5 nova queda na recarga | não disparou |
  | U6 fim aos 6 s | atributos limpos |
  | F1 alvo visível | nada |
  | F2 atrás de parede | marcado (sem visada) |
  | F3 na recarga | nada |
  | F4 invisível | marcado aos +15,1 s |
  | F5 furtivo a 40 | fora do raio |
  | F6 furtivo a 14 | marcado |
  | Limpeza no cliente | 0 Highlights e 0 marcadores depois |

  - Bug corrigido: o alvo invisível vinha duplicado (tag + atributo); agora a lista não repete.
- **Vídeo:** `poderes/review/passivas_furia_faro_studio.mp4`.
- **Pendente:**
  - o urso não tem sistema de movimento (o bônus de velocidade fica no atributo);
  - integrar o Faro com as regras oficiais de inimigo/aliança e de furtividade (arquivos compartilhados);
  - som;
  - o place NÃO foi salvo.

**Fúria do Protetor: aura v2 (05/11; pedido do usuário com imagem: "deixe a aura mais parecido com isto"; só o cliente; Studio rpg_roblox, NÃO salvo)**
- **Referência:** urso escuro envolto em fios de energia dourada e laranja que correm para trás, brasas e olhos acesos.
- **Cliente** (`EfeitosUrso_Cliente` 74010/985628, igual ao repositório; backup em `Anteriores/Poderes_antes_FuriaV2`):
  - **olhos acesos:** 2 esferas Neon (0,17) presas ao osso `Cabeca`, com faísca para trás e luz pequena;
    - posição medida no repouso em espaço do pivô: (±0,62; 7,34; −5,30), conferida com marcadores temporários (removidos);
  - **corpo escurecido:** Highlight com preenchimento marrom-escuro a 0,45 e contorno dourado que pulsa;
  - **30 rastros de luz** (Trail; 12 em qualidade baixa) que deslizam da cabeça até a garupa por fora do corpo:
    - seguem o caminho Cabeça → Pescoço2 → Coluna3/2/1 → Pelve, com meia largura e altura por trecho;
    - cobrem dorso e flancos (±1,55 rad), ondulam e recomeçam em lugar sorteado;
  - faíscas finas (`fire_sparks_main`) e brasas.
- **1ª tentativa recusada antes de mostrar:** o corpo ficou laranja (a luz do peito e o preenchimento claro tingiam) e os fios pareciam estrelinhas soltas. A luz do peito saiu.
- **Prancha:** `poderes/review/prancha_furia_aura_v2.png` (referência ao lado do Studio).
- **Vídeo:** `poderes/review/furia_protetor_aura_v2_studio.mp4`.
- **Limites:**
  - de dia a floresta tira parte do brilho; a referência é noturna;
  - a pelagem verde e a casca do urso ficam escurecidas, não pretas;
  - FPS e celular não medidos (30 Trails, 6 emissores);
  - o place NÃO foi salvo.

**Fúria do Protetor: olhos v3 (05/11; pedido do usuário com imagem de anime: "o olho total amarelo, não uma bola na frente, e uma linha meio saindo do olho para trás"; só o cliente; Studio rpg_roblox, NÃO salvo)**
- **Olhos:** cada olho é uma elipse amarela Neon (Part + SpecialMesh Sphere, 0,22 × 0,13 × 0,04) colada sobre o olho do modelo, com luz pequena.
  - Posição e normal medidas no Edit com marcadores, de frente e de 3/4 (espaço do pivô, olho direito): pos (0,52; 7,33; −5,37), normal (0,62; 0,12; −0,77); o esquerdo é espelhado.
  - Ficam presas ao osso `Cabeca` e acompanham as animações.
  - Nota técnica: Part com Shape = Ball é sempre uma esfera do menor eixo; por isso a 1ª tentativa virava um ponto. Usei SpecialMesh.
- **Linha do olho:** Beam curvo (Bézier pelos eixos dos attachments) que sai do canto de fora do olho, abre para trás e sobe em direção à orelha.
  - Afina de 0,11 para 0,012 e tremula (largura e ponta).
  - Valores em `M.OLHO_FURIA`: linhaFim (0,5; 0,95; 1,2), tang0 (0,85; −0,05; 0,5), tang1 (0; 0,85; 0,5), curvas 0,55/0,5.
- Saíram as esferas e as faíscas antigas dos olhos.
- `EfeitosUrso_Cliente` 76056/148348, igual ao repositório. Backup em `Anteriores/Poderes_antes_OlhosV3`.
- **Prancha:** `poderes/review/prancha_furia_olhos_v3.png`.
- **Pendente:**
  - conferir com o urso em movimento (cabeça girando); a posição do olho foi medida no repouso;
  - o place NÃO foi salvo.

**Fúria: olhos v3b (05/11)**
- Pedido do usuário: "de lado ainda parece uma bola na frente do olho".
- Causa: a elipse da v3 era fina (0,04) e ficava na frente do olho. Vista de lado, sobressaía.
- Agora:
  - um elipsoide de 0,24 × 0,15 × 0,16 **embutido** no globo do olho: pos (0,55; 7,28; −5,13), normal (0,75; 0,12; −0,65);
  - só a parte que sai do olho aparece, então o olho todo parece aceso.
- Conferido no Edit de frente, de 3/4 e de lado, e no Play de lado.
- `EfeitosUrso_Cliente` 76148/155781, igual ao repositório.
- **Prancha:** `poderes/review/prancha_furia_olhos_v3b.png`.
- **Não testado:** o urso andando. O piloto não tem Animator no servidor fora do sistema de poderes, então a cabeça parada foi o que deu para conferir.

**Fúria do Protetor: visual APROVADO (05/11; o usuário respondeu "Aprovar")**
- Aprovados: aura v2d e olhos v3b.
- Pendentes: valores, som, celular/FPS e o place não salvo.

**SONS dos poderes (05/11; pedido do usuário: "Fazer os sons"; origem escolhida: "Biblioteca grátis Roblox"; só o cliente; Studio rpg_roblox, NÃO salvo)**
- **Origem:** Creator Store, só bibliotecas licenciadas e públicas (ProSoundEffects e APM, "Courtesy of …"). Nada comprado, nada publicado.
  - Os IDs são referenciados por `SoundId`, sem inserir modelos no place.
  - Os 8 sons carregaram no Play (`IsLoaded`).
- **Mapa** (`EfeitosUrso_Cliente`; tabela {id, vel, vol, atraso}):

  | Poder / momento | Som | ID | Velocidade |
  |---|---|---|---|
  | Golpe Colossal, rugido | Lion Roar Growl Exhale Low Rumble 1 | 9116300504 | 0,78× |
  | Golpe Colossal, impacto | Shale Break 12 | 9119042093 | 0,8× |
  | Rugido Protetor | Lion Roar | 9116300504 | 0,86× |
  | Carga, arrancada | Shale Break Low End Crackling Rock 3 | 9119049891 | 0,9× |
  | Carga, impacto | Body Fall Heavy Rustle 2 | 9113470802 | 0,85× |
  | Fortaleza, início | Lion Roar, atraso 0,62 s (rugido do clipe aos 0,7 s) | 9116300504 | 0,72× |
  | Fortaleza, ativar/formação | Beautiful Shimmer (APM, 6,1 s) | 1841209502 | 0,9× |
  | Fortaleza, retenção | embutido `rbxasset://sounds/impact_water.mp3` (não achei som de energia licenciado melhor) | — | 0,55× |
  | Fortaleza, quebra | Glass Breaks 11 | 9114592102 | 0,8× |
  | Fúria do Protetor | Tiger Snarl 6 | 9120050567 | 0,78× |

- **Código:**
  - `som()` aceita tabela, toca 3D no ponto (RollOff 10–140) e respeita `atraso`; exportado como `M.som`;
  - `somFV` usa `M.som`;
  - backup em `Anteriores/Poderes_antes_Sons` e `rig/studio/poderes/antes_sons/`.
- `EfeitosUrso_Cliente` 77731/278047, igual ao repositório.
- **Teste em Play:** cada som tocou junto com o seu evento do servidor (log com horários).
- **Limites:**
  - não existe áudio gravado de urso: o rugido é de leão, mais grave;
  - eu NÃO consigo ouvir; a avaliação do som é do usuário;
  - Faro do Protetor sem som (sopro);
  - o place NÃO foi salvo.


### Sons v2 + boca sincronizada (06/11/2026; Studio rpg_roblox, Play; AGUARDANDO AVALIAÇÃO do usuário)
Pedido: "Arrume a boca, pois ha rugidos que ele da sem estar com a boca aberta, quero que sincronize tudo. Os sons tambem estao ruins [...] quero mais relaxantes e mais fantasia realista."
- Causa medida: o rugido de leão (desacelerado para 0,72–0,86×) durava ~7 s, mas a boca do clipe só fica aberta 0,5–1,4 s; a Fúria não tinha boca.
- `som(id, pos, urso)` aceita `inicio` (trecho do arquivo), `dur` (corte com fade), `entra`/`sai` (fades) e `boca` (graus).
- Os rugidos tocam só o trecho forte, na janela de boca aberta do clipe: Golpe 0,78 s; Rugido Protetor 1,5 s; Fortaleza 0,62 s; Fúria 1,3 s.
- `M.bocaSom`, no cliente, abre a `Mandibula` pelo volume real do som (PlaybackLoudness/160 × graus). Soma ao clipe e nunca fecha mais que ele. Roda em RenderPriority.Last.
- Corrigido no teste: a boca ficava presa aberta (41°) depois do som, porque o repouso não reescreve o osso. Agora guarda a base e devolve a pose.
- Sons trocados (Pro Sound Effects, Creator Store), todos mais baixos:
  - formação do escudo: Shimmer (o som de "notificação") → Magic Wind Airy Whooshy Wind 4 (9116432106), vol 0,45, entrada de 0,8 s;
  - retenção: impact_water → Boom Impact Deep Distant Thumping (9125403425), vol 0,4;
  - quebra: vidro → Boom Thump Rattling Light Crunch (9113551773), vol 0,6;
  - volumes reduzidos: impacto do Golpe 0,7, arrancada 0,65, impacto da Carga 0,8.
- Teste no Play (log por quadro do cliente: ângulo da mandíbula × volume do som):
  - Golpe, Rugido Protetor e Fortaleza: 0 quadros de boca fechada (<10°) durante o rugido. Boca máxima 42°, 48° e 40°.
  - Fúria: a boca abre até 26° seguindo o rosnado e fecha no fim.
  - A mandíbula volta a 0° depois de todos.
- Vídeo: `rig/poderes/review/boca_sincronizada_rugidos_studio.mp4`, só imagem (a captura não grava áudio).
- Arquivos: `EfeitosUrso_Cliente.luau` (81404/568585 = Studio) e `bloco_*_cli.luau`. Backups em `antes_sons_v2/` e `ServerStorage.Urso_v2_Piloto.Anteriores.Poderes_antes_sonsv2`.
- Limites:
  - eu não ouço; a avaliação do som é do usuário;
  - a boca abre ~0,4 s antes do som (inspiração do clipe);
  - celular não testado;
  - o place NÃO foi salvo.

### Olhos da Fúria fora do lugar (06/11/2026; Studio rpg_roblox, Play; AGUARDANDO AVALIAÇÃO)
Pedido (com imagem): "Os olhos amarelos sairam do lugar."
- Causa medida: a Fúria atualizava os olhos no `RenderStepped`, antes da pose final do quadro (Animator). O olho usava a pose do quadro anterior.
  - Parado, o atraso não aparece.
  - Na Carga, o olho chegava a **2,3 studs** atrás da cabeça.
  - Além disso, no 1º quadro o olho nascia na origem do mundo.
- Correções em `EfeitosUrso_Cliente.luau` e `bloco_passivas_cli.luau`:
  - a atualização da Fúria (olhos, rastros, brasas) agora roda em `BindToRenderStep`, `RenderPriority.Last + 1`, depois da boca; o `tirarFuria` desliga isso (`Unbind`);
  - o olho já nasce no lugar certo (`p.CFrame` na criação);
  - a posição de referência da cabeça agora é a de repouso (cadeia de `Bone.CFrame`), igual à medição feita no Edit.
- Teste no Play (erro = distância entre o olho e o ponto certo na cabeça animada, a cada quadro):
  - Fúria + Carga: 157 quadros, erro máximo **0,0000** stud (antes: 2,28);
  - Fúria iniciada no meio do Rugido Protetor: erro máximo 0,12 stud. Esse teste foi feito antes da mudança de prioridade.
- Evidência em `rig/poderes/review/`: `furia_olhos_fixos_carga_studio.mp4` e `prancha_furia_olhos_fixos.jpg`.
- Studio = local: 82341/646307.
- Backups: `antes_olhos_pos/` e `ServerStorage.Urso_v2_Piloto.Anteriores.Poderes_antes_olhospos`.
- Limites:
  - celular não testado;
  - o place NÃO foi salvo.

## Montaria — M1: sela reforçada (09/11/2026; só Blender; APROVADA pelo usuário em 09/11: "Aprovar e seguir"; Roblox não testado)
Pedido: "quero que faca a animacao de subida, a montaria no urso e animacao de descida, e sua sela tambem, baseando-se no visual de seus itens para fazer a sela."
Oficial na ficha: o urso monta desde Adulto, com "sela reforçada". Feito primeiro a sela; subida, montado e descida vêm depois da aprovação, porque dependem dela.
- Método: o mesmo da sela aprovada do Leão Solar (que veio da do Crocodilo). Campo de alturas do dorso por raios, manta, aba, assento moldado, cilha por raios em volta da barriga e pesos copiados da pele. Nada do urso foi alterado.
- Visual "dos itens do urso":
  - arção reforçado de **Madeira Ancestral** (cabeça e patilha como placas de casca, com cintas de ferro);
  - alça de galho com cordão de **Tendão de Cervo** enrolado (lembra os cipós);
  - folhas de couro curtido na borda da manta (como as folhas do corpo);
  - adorno de folha de madeira com gota de **Resina Viva** na frente do arção e nas argolas da cilha.
- Demais materiais:
  - assento, aba, cilha e solas de **Couro de Javali**;
  - manta de **Pele de Cervo**;
  - **Ferro** nas argolas e cintas.
  - Madeira Ancestral e Resina Viva são regionais oficiais. Os nomes animais são nomes de trabalho (DOCS/fauna). O tom oliva das folhas é proposta.
- Medidas (`rig/montaria/m0_dorso.json`): corcova em y −3 a −1 (z ≈ 8,7); o dorso desce para trás (8,1 → 7,2); largura ±2,5.
  - Assento logo atrás da corcova: quadril do cavaleiro em (0; 0,85; 9,32).
  - Cilha em y 0,25: em y −0,45 os raios batiam na pata da frente.
- O pé não alcança um estribo pendurado: o dorso é largo e alto, e a perna do R15 mede ~1,7. Por isso o pé pousa no topo da manta onde a perna mede 1,61, com sola de couro e alça de ferro. O cavaleiro fica de pernas bem abertas.
- Sela: 11,1 mil tris, 7 materiais, presa a `Urso_Rig` (pesos da pele, sem cabeça, pescoço nem cauda). O cavaleiro de teste fica preso a `Coluna2`.
- Arquivos:
  - scripts: `rig/montaria/m0_medir_dorso.py`, `m1_sela_urso.py` e `m1_render_sela.py`;
  - cena: `rig/montaria/CR_Urso_v2_M1_sela.blend`. O `CR_Urso_v2_Anim.blend` não foi alterado;
  - renders: `rig/montaria/review_r3/`;
  - prancha: `review/montaria/prancha_sela_urso_r3.jpg`.
- Pendentes:
  - QA de folga nos clipes (sela × pele);
  - textura de jogo e GLB;
  - subida, montado e descida;
  - Studio.

## Montaria — M2: subida, montado e descida (09/11/2026; só Blender; APROVADA pelo usuário em 09/11: "Aprovar"; Roblox não testado)
Sela M1 aprovada pelo usuário ("Aprovar e seguir"), com a proposta de o urso deitar para o cavaleiro subir.
- **Clipes do urso** (`rig/montaria/clipes_montaria.py`, carregado por `anim_urso.py` só com `URSO_MONTARIA=1`; os 18 clipes aprovados não mudam):
  - `Montar_E/D` (6,4 s): olha para o cavaleiro, deita (pose do Deitar aprovado; `DEITADO_Z` calibrado −1,686), absorve o peso da subida e levanta com ele.
  - `Desmontar_E/D` (6,2 s): deita com o cavaleiro, ele desce e o urso levanta.
  - Erro de IK ≤ 0,0005; malha mínima −0,15 (a mesma do Deitar).
  - Lado E = x+.
  - Saída: `rig/montaria/CR_Urso_v2_Anim_Montaria.blend` e os JSON em `rig/montaria/clipes/`.
  - Mudança em `anim_urso.py`: só o gancho `URSO_MONTARIA` e a calibração do deitado também para Montar/Desmontar.
- **Cavaleiro de teste** (`m2_demo_montaria.py`, adaptado do Leão; manequim R15 aproximado, não é rig R15 validado):
  - **Subida:**
    - dois passos até o lado; espera o urso deitar;
    - o pé da frente sobe por fora e por cima até o **cotovelo** da pata dianteira (degrau a ~2,8);
    - as mãos agarram a aba, e a da frente passa para a alça de galho;
    - a perna de trás passa pela garupa, ele senta (3,8 s) e o urso levanta com ele.
  - **Descida:** como a do Leão, com alturas relativas ao assento do urso deitado.
  - Deitado, o assento fica a ~7,6. Por isso não se sobe pelo chão.
- **QA** (`m2_qa.json`; folga negativa = a caixa de 1 stud do manequim entra):
  - **Subida E:** pior −0,23 (coxa/canela que sobe, 2 quadros em 2,45–2,5 s, nas folhas do lado E; a malha do Meshy é assimétrica).
  - **Subida D:** pior −0,10.
  - **Descida E/D:** pior −0,14 (antebraço na aba ao deslizar).
  - Os pés nunca afundam no chão (sola ≥ 0,03).
- **Montado** (`m2_montado.py` → `m2_montado.json`; cavaleiro preso a `Coluna2`) nos clipes aprovados Repouso, Observar, Andar, Corrida, Arrancada, Frenagem, VirarE/D e Rugir:
  - pior contato contra o urso: canela −0,18 (galope, nas folhas do dorso);
  - contra a sela: mãos −0,09/−0,11 (segurando a alça).
- **Evidência:**
  - vídeos em `rig/montaria/review_m2/`: `{Montar,Desmontar}_{E,D}_{lado,34,tras_34}.mp4` e `_lento`, mais `Montado_repouso_andar_corrida_virar.mp4`;
  - cena: `rig/montaria/CR_Urso_v2_M2_montaria.blend`.
- **Pendências:**
  - avaliação do usuário;
  - montado com a animação real do jogador R15 e câmera (Studio, com autorização);
  - textura e GLB da sela;
  - envio dos clipes ao Studio.

## Montaria — M3: textura de jogo e GLB da sela (09/11/2026; só Blender; o usuário seguiu para o Studio: "Autorizar Studio")
A montaria (M2) foi aprovada pelo usuário ("Aprovar"). Esta etapa é o próximo passo proposto: textura e arquivo para o Roblox.
- Script `rig/montaria/m3_textura_glb.py`, adaptado do `s1_07` do Leão (aprovado):
  1. UV de jogo única;
  2. bake Cycles 1024 px dos 7 materiais, gerando:
     - cor (por EMIT: o DIFFUSE deixa o ferro preto);
     - normal (tangente);
     - metal/rugosidade empacotados no padrão glTF (G = rugosidade, B = metal);
  3. material único `M_Urso_Sela_Jogo`;
  4. pesos limitados a 4 por vértice e normalizados.
- Correção r2 da UV:
  - Com margem 0,012, as milhares de ilhas pequenas usavam só ~11% da imagem. Ferro, resina e cordão ficavam com 1–9 px por face, a cor vizinha vazava e apareciam listras escuras no galho.
  - Agora a densidade é igual em todas as ilhas e a margem é 0,003: cerca de 3,4× mais pixels por peça, e as listras sumiram.
- Saída em `rig/export/sela/`:
  - `Urso_Silvestre_Sela.glb` (2,5 MB): só a sela + armadura `Urso_Rig`, sem animação, texturas embutidas;
  - os PNG `T_Urso_Sela_{Cor,Normal,MetalRug}`;
  - `Urso_Silvestre_Sela_Jogo.blend`;
  - `sela_jogo_info.json` e `validacao_glb.json`.
- Validação ao reimportar (`m3_validar_glb.py`):
  - 11.084 tris; 31 ossos com os nomes do urso; no máximo 4 influências; 0 vértices sem peso;
  - texturas de 1024 px; z da sela de 1,87 a 9,95 no repouso;
  - a "Icosphere" é o formato de osso que o importador cria.
- Comparação procedural × textura de jogo: `review/montaria/prancha_sela_urso_textura_jogo.jpg`.
- Pendente: Studio (import da sela no `Teste_Urso_v2`, clipes Montar/Desmontar, animação do jogador e câmera). Só com autorização e reserva.

## Montaria — M4: teste no Studio (09/11/2026; autorizado: "Autorizar Studio"; place rpg_roblox; base das etapas M5 e M6, aprovadas)
- **Levado só o lado E** (urso + cavaleiro), para manter o envio enxuto. O lado D está validado no Blender e não foi testado no Studio.
- **Urso:**
  - `Urso_Montar_E` e `Urso_Desmontar_E`, reamostrados a 15 qps (`rig/montaria/clipes15/`, o Roblox interpola), enviados como StringValue em `Dados_Clipes`;
  - somas iguais às do arquivo local: 9891/760091 e 9631/739460. Corrigidos no Studio 2 erros de 1 caractere da transcrição, localizados pela soma por linha;
  - KeyframeSequences em `ServerStorage.Urso_v2_Piloto.Animacoes`, com 97/94 keyframes e 0 ossos faltando.
- **Cavaleiro:**
  - `rig/montaria/m4_exportar_cavaleiro.py` exporta, do Blender, a rotação de cada parte do R15 + a posição do LowerTorso, no espaço da RootPart do urso (Studio = (−x, z, y) do Blender);
  - `Cav_Montar_E` 10217/818239, `Cav_Desmontar_E` 8916/688094 e `Cav_Sentado` 1271/105264: somas iguais às locais;
  - módulo `ServerStorage.Urso_v2_Piloto.Montaria.CavaleiroR15` (cópia em `rig/studio/CavaleiroR15.luau`) converte os dados em KeyframeSequence de um R15 real;
  - funciona com Motor6D e com AnimationConstraint: Transform = (Part0·A0)⁻¹·(Part1·A1). O R15 novo usa AnimationConstraint;
  - R15 de teste `Workspace.Teste_Urso_v2.TESTE_Cavaleiro_R15` (HumanoidDescription padrão; HRP ancorada na RootPart do urso).
- **Sela:**
  - importada pelo usuário (Import 3D). O original está guardado em `ServerStorage.Urso_v2_Piloto.Anteriores.Sela_importada_09_11`;
  - **lição:** ligar a pele da sela aos ossos do urso pelo nome deformou errado: o Raiz da sela veio girado 180° no import. Ossos de mesmo nome no MESMO Model fizeram a pele do urso usar os ossos da sela, e o urso deformou;
  - **solução de teste:** a sela fica no Model separado `Workspace.Teste_Urso_v2.Urso_Sela_Teste`, com Motor6D na RootPart do urso, e no cliente cada um dos 18 ossos dela copia o osso de mesmo nome do urso (`rig/studio/montaria_teste_play.luau`).
- **Play** (servidor toca urso + cavaleiro juntos; o cliente gruda a sela e, montado, prende a HRP do cavaleiro à Coluna2):
  - sequência: subida 6,4 s → montado em Andar 3,6 s e Corrida 2,8 s → descida 6,2 s; os tempos registrados bateram;
  - desvio sela × urso: máx. **0,0003** stud;
  - visual: o urso deita, o R15 sobe pelo cotovelo e senta na sela, acompanha andar e corrida, e desce pelo lado.
- **Vídeo:** `rig/montaria/review_m4/Studio_montaria_urso_E_subida_montado_descida.mp4`.
- **Limitações:**
  - **Boneco ao fim da descida:** quando o clipe termina, o R15 de teste volta à pose de repouso dentro do urso (não há pose de fechamento). No jogo, o controle do jogador assume nesse ponto.
  - **Proporções:** as do manequim do Blender são aproximadas do R15, então os contatos podem diferir um pouco.
  - **Sela no jogo:** precisa de solução definitiva. Opções: reimportar com os ossos alinhados, ou manter a cópia de ossos num sistema oficial. O sistema de montaria (entrada, câmera, servidor) é compartilhado e exige autorização.
  - **Ainda não testado:** celular; lado D no Studio.
  - **Place:** NÃO foi salvo.

## Montaria — M5: cavaleiro se move com a física (09/11/2026; Studio rpg_roblox, Play; APROVADA pelo usuário em 09/11: "Aprovar")
Pedido: "Quero que o jogador tambem se mova junto aos movimentos, como as leis da fisica."
- **Módulo** `ReplicatedStorage.Urso_v2_Lab.InerciaCavaleiro` (cópia em `rig/studio/InerciaCavaleiro.luau`; soma 5313/427872 igual nos dois): só visual, no CLIENTE, e não passa pelo servidor. Modelo físico:
  - **tronco:** pêndulo amortecido. O quadril vai preso ao assento (osso Coluna2 do urso) e o tronco é uma massa 1,6 stud acima, com mola e amortecimento (2,2 Hz, ζ 0,55). Quando a sela acelera, freia, galopa, sobe, desce ou inclina, o tronco fica para trás e volta;
  - **cabeça:** 2ª massa sobre o tronco (3,0 Hz, ζ 0,40);
  - **mola vertical** (3,0 Hz): o corpo absorve a subida e a descida da sela. Isso dobra o tronco para a frente (40°/stud, até 9°) e acena a cabeça;
  - a rotação extra é somada às juntas Waist e Neck depois do Animator. Funciona com Motor6D e com AnimationConstraint;
  - limite suave (tanh): tronco até 14°, cabeça até 12°;
  - teleporte (PivotTo) não conta como aceleração: as massas vão junto;
  - peso pelo atributo `InerciaPeso`: 0 enquanto sobe e desce, 1 sentado.
- **Ajustes durante o teste:**
  - r1: as trocas de clipe do laboratório teleportam o urso e geravam picos de 100°. Corrigido;
  - r2: o tronco batia em 24° no galope. A mola ficou mais firme e entrou a mola vertical;
  - r3: limite suave.
- **Medições finais** (graus, máximo por fase):

  | Fase | Tronco | Cabeça | Dobra vertical |
  |---|---|---|---|
  | Urso levantando com o cavaleiro | 1,8 | 3,7 | 2,3 |
  | Andar | 2,3 | 5,9 | 1,1 |
  | Arrancada | 13,7 | 12 | 9,0 |
  | Galope | 13,9 | 12 | 5,2 |
  | Frenagem | 13,5 | 12 | 6,6 |
  | Parado | 1,5 | 1,5 | 0,2 |
  | Urso deitando | 2,0 | 5,3 | 2,7 |

  - Direções conferidas nos quadros: na arrancada o tronco vai para trás, na frenagem vai para a frente, e no galope balança no ritmo.
- **Vídeos** em `rig/montaria/review_m4/`: `Studio_montaria_urso_fisica_cavaleiro.mp4` (sequência inteira) e `Studio_montaria_urso_fisica_galope_lento.mp4` (andar → frenagem a 8 qps).
- **Limitações:**
  - braços e pernas seguem o tronco (as mãos não ficam presas na alça);
  - números são de LAB;
  - celular não testado (o custo é de 2 pêndulos por cavaleiro visível);
  - integração no sistema de montaria oficial pendente de autorização;
  - o place NÃO foi salvo.

## Montaria — M6: lado D no Studio (09/11/2026; pedido "Lado D no Studio"; APROVADA pelo usuário em 09/11: "Aprovar")
- **Clipes do urso (15 qps):** `Urso_Montar_D` e `Urso_Desmontar_D` diferem do lado E em só 28 linhas (pescoço, cabeça, rolagem da coluna e o ajuste das patas). Por isso o Studio montou o D a partir do E já enviado, trocando só essas linhas. Somas iguais às locais: 9893/760247 e 9627/738646.
- **Cavaleiro D:** `m4_exportar_cavaleiro.py` agora também exporta `DEMO_Cav_Montar_D`/`DEMO_Cav_Desmontar_D` (o E saiu idêntico ao anterior: 10217/818239). Envio inteiro, com o antebraço copiado no Studio.
  - Somas: `Cav_Montar_D` 10221/818539 e `Cav_Desmontar_D` 8914/688931.
  - 1 erro de 1 caractere da transcrição foi corrigido, localizado pela soma por linha.
- **KeyframeSequences:** urso em `Animacoes` (97/94 keyframes, 0 ossos faltando); cavaleiro em `Montaria`.
- **Play pelo lado D** (câmera em +X do Studio = lado D), com a física do cavaleiro (M5) e a sela seguindo o urso:
  - sequência: subida → andar → arrancada → galope → frenagem → descida; os tempos registrados bateram;
  - sela × urso: desvio máx. **0,0001**;
  - física por fase (tronco/cabeça/dobra, graus):

    | Fase | Tronco | Cabeça | Dobra |
    |---|---|---|---|
    | Urso levantando | 3,1 | 6,0 | 2,9 |
    | Andar | 3,5 | 7,5 | 3,8 |
    | Arrancada | 13,5 | 12 | 9,0 |
    | Galope | 13,9 | 12 | 6,6 |
    | Frenagem | 13,9 | 12 | 8,5 |
    | Urso deitando | 2,8 | 5,4 | 3,5 |

  - visual: o R15 sobe pelo cotovelo do lado D, senta, acompanha os movimentos e desce pelo lado D.
- **Vídeo:** `rig/montaria/review_m4/Studio_montaria_urso_D_subida_fisica_descida.mp4`, cortado no fim da descida.
- **Limitações:** as mesmas do lado E.
  - Ao fim do clipe, o R15 de teste volta à pose de repouso.
  - A sela no jogo depende da solução definitiva.
  - O sistema de montaria oficial precisa de autorização.
  - Celular não testado.
  - O place NÃO foi salvo.

## Montaria — M7: sela definitiva e convenção do importador (10/11/2026; pedido "Sim, sela definitiva"; decisão do usuário: "Sim, migrar" → M8)
- **Causa encontrada (em 3 passos):**
  1. A sela só tinha peso em 13 dos 31 ossos. O `m7_sela_definitiva.py` agora dá um triângulo degenerado (peso 100%) a cada osso sem peso, como faz o `exportar_urso.py`: v2 com 31/31 ossos (`m7_comparar_ossos_glb.py`: matrizes idênticas às do urso no glTF).
  2. Com uma malha só, o Import 3D pendura os ossos na própria MeshPart. A v3 leva uma 2ª malha mínima (`Urso_Sela_Ancora`, 1 triângulo degenerado no Raiz) e chega com RootPart e ossos nela, igual ao urso.
  3. Ainda assim, os ossos da v3 ficaram 180° em relação aos do piloto. O usuário importou de novo o mesmo `CR_Urso_Silvestre_v2_Rig.glb` hoje:

     | Comparação | Pior giro |
     |---|---|
     | sela v3 × urso importado hoje | 0,03° |
     | urso importado hoje × piloto de 04/11 | 180° |

     **O Import 3D mudou a convenção dos ossos desde 04/11:** cada osso = antigo × giro de 180° no eixo Y do próprio osso.
- **Sela v3 no urso novo** (`Workspace.TESTE_Urso_Import_10_11`, teste): a pele usa os ossos do urso pelo nome, **sem script**. Ela fica no dorso em repouso e acompanha deitar/levantar, andar e correr (Play gravado).
- **Consequência:** as animações do urso (feitas e validadas no piloto, convenção antiga) saem com X e Z invertidos num urso importado hoje (deitado, ele "flutuava").
  - Conversão testada: em cada osso, quaternion (x, y, z, w) → (−x, y, −z, w) e translação (x, y, z) → (−x, y, −z).
  - Com o `Urso_Montar_E` convertido, o urso novo deita no chão (Raiz −2,05) com a sela certa.
- **Estado no place** (NÃO salvo):
  - o piloto continua com a sela de teste (`Urso_Sela_Teste`, cópia de ossos);
  - existe o urso de teste novo `TESTE_Urso_Import_10_11` com a sela v3 integrada, em (0, 2000, 30);
  - backups dos imports em `ServerStorage.Urso_v2_Piloto.Anteriores`: `Sela_v2_importada_10_11` e `Sela_v3_importada_10_11`.
- **Arquivos:**
  - `rig/export/sela/Urso_Silvestre_Sela_v3.glb` (definitivo para imports atuais);
  - `rig/montaria/m7_sela_definitiva.py` e `m7_comparar_ossos_glb.py`.
- **Decisão pendente do usuário:**
  - (A) migrar o laboratório para o urso importado hoje: sela v3 sem script e conversão das animações no `AdaptadorUrso` (vale também para qualquer import futuro);
  - (B) manter o piloto antigo com a sela por cópia de ossos.

## Montaria — M8: laboratório migrado para o urso importado hoje (10/11/2026; decisão "Sim, migrar"; APROVADA pelo usuário em 10/11: "Aprovar")
- **`AdaptadorUrso`** (repo = Studio, 5913/482248; backup `Anteriores.AdaptadorUrso_antes_convencao`):
  - `M.convencaoNova(modelo)` detecta a convenção pelo Raiz em repouso (RightVector.X < 0 = nova);
  - `M.cframe(..., nova)` converte: q (−x, y, −z, w) e t (−x, y, −z);
  - `montar` e `aplicarQuadro` usam a conversão sozinhos;
  - os dados dos clipes não mudaram.
- **Conferência antes da troca:** em 31 clipes, 4 quadros cada (3.844 ossos), o urso novo com conversão ficou igual ao piloto antigo sem conversão. Diferença máx. **0,0001 stud**.
- **Troca no place:**
  - o piloto de 04/11 foi para `Anteriores.Urso_Piloto_import_04_11`;
  - a sela por cópia de ossos foi para `Anteriores.Urso_Sela_Teste_M4_copia_ossos`;
  - o urso importado hoje virou `Workspace.Teste_Urso_v2.Urso_Silvestre_v2_Piloto`, no mesmo pivô, RootPart ancorada, com a **sela v3 integrada**: MeshPart no próprio modelo, pele nos ossos do urso, Motor6D na RootPart, **sem script**;
  - as 31 KeyframeSequences de `Animacoes` foram remontadas com a conversão, em 3 lotes. A pasta antiga ficou em `Anteriores.Animacoes_import_04_11`.
  - **Lição:** no Edit, `require` devolve o módulo em cache. A 1ª remontagem saiu sem conversão; foi refeita com `require(modulo:Clone())`.
- **Cliente** (`EfeitosUrso_Cliente`, repo = Studio, 82673/671857; backup `Anteriores.EfeitosUrso_Cliente_antes_convencao`): a boca sincronizada usa o sinal da convenção (o X local da Mandíbula inverte no urso novo).
- **Play:**
  - Golpe Colossal funcionou, com a boca abrindo até 41,9° no sentido certo;
  - montaria lado E com o cavaleiro R15 e a física (galope 13,9°): urso deita no chão, sela acompanha, cavaleiro sobe, anda, corre e desce;
  - nenhum erro do urso no console. O aviso "Invalid mesh collision data: Urso_Sela_Ancora" vem do backup do import (triângulo sem área).
- **Vídeo:** `rig/montaria/review_m4/Studio_urso_migrado_sela_v3_sem_script.mp4`.
- **Limitações:**
  - no começo da gravação, durante o Golpe, o boneco de teste aparece parado no ar: ele não estava montado. É do teste;
  - os outros poderes (Fortaleza, Carga, Rugido, Fúria) não foram regravados um a um; as animações deles passaram na conferência numérica;
  - celular não testado;
  - o place NÃO foi salvo.

## Poderes no urso migrado (10/11/2026; pedido "Sim, regravar"; AGUARDANDO AVALIAÇÃO)
- **Play** no `rpg_roblox`, no urso importado em 10/11, com a sela v3 integrada e os clipes convertidos pelo `AdaptadorUrso`:

  | Poder | Resultado | Boca (graus, positivo = abre) |
  |---|---|---|
  | Rugido Protetor | `true`; aura aparece | até 48,4 |
  | Fortaleza Viva | `true`; domo de linhas se forma em volta do urso | até 40,4 no rugido |
  | Carga Selvagem | `true`; o chão racha, o urso arranca e bate no alvo | — |
  | Fúria do Protetor | `true`; corpo escurecido, aura | até 26,0 no rosnado |

  - A boca nunca fecha além do clipe (mínimo 0,0) em nenhum dos poderes.
- **Carga recusada na 1ª tentativa:** é a regra do poder (sem Carga enquanto a Fortaleza está ativa, 4 s de formação + 8 s). Eu disparei aos 9,8 s; gravada de novo depois.
- **Console:** nenhum erro do urso. O aviso da `Urso_Sela_Ancora` é do backup do import.
- **Vídeo:** `rig/poderes/review/poderes_urso_migrado_studio.mp4` (Rugido → Fortaleza → Carga → Fúria). Câmera fixa em 3/4; a captura não grava áudio.
- **Limitações:**
  - Golpe Colossal já testado na migração (M8);
  - o alvo da Carga é uma Part fixa: a carga sai reta, sem travar num modelo;
  - celular não testado;
  - o place NÃO foi salvo.


## Escudo da Fortaleza Viva v4b: bolha em vez de jaula (10/11/2026; pedido "arrume este escudo, pois parece mais uma jaula"; APROVADO pelo usuário em 10/11: "Aprovar")
- **O que mudou** (só o visual no cliente, `rig/studio/poderes/EfeitosUrso_Cliente.luau` e `poderes/bloco_fortaleza_cli.luau`; regras do servidor intactas):
  - menos linhas: 8 meridianos (6 na qualidade baixa), paralelos 0/35/65°, passo de 10°, espessura 0,09. São ~152 partes; antes eram ~350;
  - as linhas só desenham o domo enquanto ele se forma. 0,4 s depois de formado, elas viram veios quase invisíveis (transparência 0,96);
  - o visual principal agora é a película dourada (transparência 0,5) com borda suave de `Highlight` (preenchimento 0,82, contorno 0,2);
  - num golpe, as linhas reacendem por um instante e as trincas (6 por golpe) aparecem na bolha. No fim, a borda some junto com a película.
- **Teste:** Play no `rpg_roblox`, laboratório `Teste_Urso_v2`, efeito no cliente (`fortalezaEfx`: ativar → golpe → fim). Fontes iguais no Studio e no local (soma 83977/782318); compila.
- **Evidência:** `rig/poderes/review/prancha_escudo_fortaleza_v4b.jpg` (bolha formada; golpe com trincas). Só capturas leves, sem vídeo, para não pesar no PC.
- **Backup no Studio:** `ServerStorage.Urso_v2_Piloto.Anteriores.EfeitosUrso_Cliente_antes_escudo_v4`.
- **Limitações:**
  - celular não testado (a qualidade baixa usa 6 meridianos);
  - sons do escudo não reavaliados;
  - o place NÃO foi salvo.
