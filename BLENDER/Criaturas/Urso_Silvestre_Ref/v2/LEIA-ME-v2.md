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
- **Não salvo:** o place **não foi salvo** por mim. A importação e os objetos de teste só existem na sessão aberta até o usuário salvar ou descartar.
- **Pendências:**
  - mistura entre clipes afunda a pata (até cerca de 0,19 nos testes do Blender);
  - franja da barriga no Deitar (0,10);
  - nada testado no celular nem com várias instâncias;
  - publicação das animações fora do escopo.
