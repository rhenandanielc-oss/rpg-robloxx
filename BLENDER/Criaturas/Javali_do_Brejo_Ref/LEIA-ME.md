# Javali-do-Brejo (Ref): piloto de variante sobre a base do Javali Silvestre

Fauna de recurso do Pântano Nebuloso (**não domesticável**). Ficha da fauna: `DOCS/fauna/pantano-nebuloso.md`.
Piloto de 14/11/2026: medir quanto a base compartilhada poupa. Um lote só: variante visual + rig da base + um ciclo de Andar.
**v4 APROVADA pelo usuário em 14/11/2026** ("Aprovar v4"): é a base visual atual do Javali-do-Brejo. Studio não usado. Sem regras novas de comportamento, loot ou dano.

## Fontes (somente leitura; cópias em `fonte/`)

- `fonte/CR_Javali_Rig_r4.blend` = cópia de `Javali_Silvestre_Ref/rig/CR_Javali_Rig_r4.blend`.
- `fonte/Javali_Clipes_LA.blend` = cópia de `Javali_Silvestre_Ref/rig/clipes_LA/Javali_Clipes_LA.blend`. Tem a mesma malha e os mesmos pesos do r4, mais as 6 ações do lote A. **É o arquivo de partida do script.**
- `fonte/T_Javali_*.png` = cópias das texturas `low_v1` da base.
- **Referência:** `REFERENCIAS/floresta-ancestral/javali-silvestre/javali-silvestre-referencia.png` (anatomia da base).
  **Não existe ficha própria** em `REFERENCIAS/pantano-nebuloso/javali-do-brejo/`, então a direção visual é **PROVISÓRIA**.

## Variante v4 (atual)

Comando: `blender -b --factory-startup fonte/Javali_Clipes_LA.blend -P scripts/variante_brejo.py -- . v4`

O script gera `CR_JavaliBrejo_v4.blend`, `texturas/T_JavaliBrejo_*` e `relatorio_variante_v4.json`.

**O que muda.** Os parâmetros estão no topo do script e todos são PROPOSTA visual.
- **Forma.** Só posições de vértice: a topologia, os pesos, os ossos e a costura são os mesmos da base.
  - **Crista:** 40% mais alta na linha média (da nuca ao meio do dorso), mais estreita (cerdas agrupadas) e em tufos suaves a cada 10 cm. Continua baixa (2,2 cm) até a garupa.
  - **Focinho:** a ponte entre os olhos e as presas alonga 6,5 cm; a frente (presas e disco) se move rígida e cai 5°. O disco fica 10% maior.
  - **Deslocamento máximo:** 7,4 cm. Foram movidos 254 vértices do corpo e 726 da cabeça.
  - **Costura cabeça/corpo:** 107 de 107 pares continuam iguais.
- **Material.** O procedural fica guardado como `M_JavaliBrejo_*_Fonte` (fake user), e a cor e a rugosidade são assadas em 1024.
  - **Pelo:** frio e escuro (saturação 0,45, valor 0,70 e menos vermelho).
  - **Crista:** estrias escuras verticais (cerdas agrupadas).
  - **Lama marrom-oliva localizada:** nas patas (até 19–30 cm, com borda irregular), no baixo-ventre e no queixo. Fica molhada (rugosidade 0,45) com crosta seca mais clara na borda.
  - **Presas:** continuam em marfim, protegidas da lama.
  - **Normal:** a mesma da base (cópia).
- **Arquivo final:** `JavaliBrejo_Rig` (30 ossos, 29 deformam), `JavaliBrejo_Corpo` (6.643 triângulos), `JavaliBrejo_Cabeca` (3.357) e 2 materiais de jogo. Tem só a ação `JavaliBrejo_Andar`.

**Histórico (descartado, em `pranchas/historico/`):**
- **v1:** "Cor" casava com "Corpo", o que trocou as imagens do corpo; e os picos da crista viravam lâminas.
- **v2:** a lama escura sumia no pelo escuro.
- **v3:** a lama continuava tímida.

## Pranchas

`scripts/render_vistas.py` + `scripts/prancha_comparar.py`. Usam as mesmas câmeras para a base e a variante, com o rig em pose de descanso.
- `pranchas/v4_comparacao_argila.png`: **antes** do acabamento (só forma).
- `pranchas/v4_comparacao_textura.png`: **depois** do acabamento.

Cada prancha mostra perfil, três quartos, frente, rosto (perfil e 3/4), vista de baixo (ventre e patas), miniatura de 96 px e a referência da base.

## Andar (transferido sem alteração)

- **Ação:** `JavaliBrejo_Andar` é a mesma `Javali_Andar` do lote A aprovado, sem nenhuma mudança: o esqueleto e os nomes são iguais e a nova malha não exigiu correção.
- **Render:** `JAVALI_PFX=JavaliBrejo blender -b CR_JavaliBrejo_v4.blend -P scripts/render_andar.py -- andar Andar:2.7 Andar 1 0.9` (cópia do render da base, só com o prefixo de nome parametrizado).
- **Medidas extras:** `scripts/medir_andar.py`, rodado na base e na variante.
- **Saídas:**
  - `andar/Andar/Andar_prancha.png`, `Andar_lado_fixo.gif` e `Andar_34_fixo.gif`;
  - `andar/Andar/JavaliBrejo_Andar_3ciclos.mp4` (lateral e 3/4 fixas, 2× em velocidade real e 1× em meia velocidade; codificado pelo próprio Blender);
  - `andar/extremos_prancha.png`;
  - `andar/medidas_extra_*.json`.
- **Quadros PNG:** ficam no scratchpad da sessão e podem ser regenerados com o render.

| Medida | Base | Brejo v4 |
|---|---|---|
| Duração do clipe (laço) | 7,2 s (216 q) | igual |
| Ciclo | 0,9 s (27 q) | igual |
| Ordem de pouso | TrasE → D → TrasD → E (sequência lateral) | igual |
| Intervalo entre pousos | 7, 7, 7, 6 q (quatro tempos) | igual |
| Apoio por pata | 63–67% | igual |
| Avanço por ciclo | 0,40 u | 0,40 u (3 ciclos = 1,185 u em 2,7 s) |
| Velocidade | 0,444 u/s | igual |
| Maior deriva de casco apoiado | 0,02 cm | 0,02 cm |
| Pele abaixo do chão | não (mínimo 0,02 cm) | não (mínimo 0,02 cm) |
| Cabeça mais baixa | 22,65 cm | 21,2 cm (focinho caído) |
| Triângulos cabeça × corpo se cruzando | 0 | 0 |
| Auto-interseção do corpo (média de pares por quadro) | 7,4 | 8,6 |
| Emenda do laço (último → primeiro) | 23,5° | igual |
| Estiramento máximo nas poses extremas | ombro 1,89×; quadril e jarrete 2,15×; pescoço 1,21×; cabeça 1,47× | iguais (pescoço 1,16–1,21×) |

**Leituras:**
- **Auto-interseção:** o aumento (+1,2 por quadro) vem todo do dorso. São triângulos de cerda da crista mais alta se cruzando entre si, coisa que a malha do Meshy já tinha. Pernas e tronco ficaram iguais.
- **Emenda:** o giro de 23,5° está dentro do maior giro normal de um quadro (23,8°, o casco saindo do chão).
- **Deslocamento:** a ação fica **no lugar**. A Raiz só oscila: x ±0,3 cm, z de −1,9 a −1,1 cm, y 0. O avanço vem de `velocidade_PROPOSTA` (0,444 u/s), gravada na ação e aplicada pelo controlador. No render isso é feito por `arm.matrix_world`; no jogo, pelo movimento do modelo.

## Lote A completo (14/11, pedido: "Transferir outros clipes"; APROVADO 14/11: "Aprovar e fazer B")

Um lote por vez, como no catálogo da base. O v4 aprovado continua intacto, e os clipes foram para um arquivo novo.

- **Comando:** `blender -b CR_JavaliBrejo_v4.blend -P scripts/transferir_clipes.py -- fonte/Javali_Clipes_LA.blend Repouso,VirarE,VirarD,ParadoParaAndar,AndarParaParado CR_JavaliBrejo_v4_LA.blend`
- **Arquivo:** `CR_JavaliBrejo_v4_LA.blend`, com as 6 ações do lote A (Andar, Repouso, VirarE, VirarD, ParadoParaAndar, AndarParaParado). Reabertura conferida: 10k triângulos, 30 ossos e as imagens encontradas.
- **Ações:** anexadas da cópia em `fonte/` sem mexer nas curvas. Mantêm as propriedades da base (apoios, velocidade, `v_perfil`, laço).
- **Renders:** `scripts/render_andar.py` com as mesmas cadeias da base. Saídas em `clipes_LA/<rotulo>/`: GIF lateral e 3/4, prancha e `medidas.json`.
- **Vídeo:** `clipes_LA/JavaliBrejo_LoteA.mp4`, com os 5 clipes em sequência, em velocidade real.
- **Medição:** `scripts/medir_clipes.py` (todos os quadros, base e variante) e `scripts/comparar_clipes.py`, que gera `clipes_LA/comparacao.json`.

| Clipe | Pose igual à base | Avanço / deriva do casco (base = brejo) | Cabeça mín. base → brejo | Cabeça × corpo | Auto-interseção média base → brejo |
|---|---|---|---|---|---|
| Repouso (8 s, laço) | sim, dif. 0,0 | parado / 0 | 18,7 → 16,6 cm | 0 | 5,0 → 6,0 |
| VirarE (laço) | sim | 0,378 u/ciclo / 1,3 cm | 21,5 → 20,0 cm | 3 → 3 (já existia na base) | 21,8 → 22,8 |
| VirarD (laço) | sim | 0,378 u/ciclo / 0,95 cm | 21,7 → 20,2 cm | 0 | 30,3 → 32,9 |
| ParadoParaAndar + Andar | sim | 1,00 u / 0,53 cm; salto na troca 18,3° | 20,4 → 18,5 cm | 0 | 6,6 → 7,6 |
| Andar + AndarParaParado + Repouso | sim | 0,70 u / 0,03 cm; trocas 23,5° e 0,2° | 20,4 → 18,5 cm | 0 | 6,0 → 7,1 |

- **Na variante:**
  - a pele nunca fica abaixo do chão (mínimo de 0,01–0,02 cm);
  - o estiramento é igual ao da base, com máximo de 3,13× no quadril/jarrete do VirarD, por dentro da coxa, como já acontecia na base;
  - os triângulos de cabeça × corpo que se cruzam no VirarE são os mesmos 3 da base.
- **Diferenças da variante:** a cabeça fica 1,5–2,1 cm mais baixa (focinho mais longo e caído), e a auto-interseção do dorso sobe de +1 a +2,6 pares por quadro (cerdas da crista).
- **Atenção para o lote C:** o Fuçar da base encosta o focinho a 0,4 cm do chão, e o focinho da variante desce ~2 cm a mais. Esse clipe vai precisar de ajuste (cabeça ao chão recalculada), não de cópia direta.
- **Quadros PNG:** ficam no scratchpad. Os GIFs pesam (o `clipes_LA` tem 171 MB, como na base).

## Lote B: corrida (14/11, pedido: "Aprovar e fazer B"; APROVADO 14/11: "Aprovar e fazer C")

- **Fonte:** cópia `fonte/Javali_Clipes_LB.blend`, com os mesmos pesos r4 da base do lote A (conferido por hash dos pesos).
- **Comando:** `blender -b CR_JavaliBrejo_v4_LA.blend -P scripts/transferir_clipes.py -- fonte/Javali_Clipes_LB.blend Trote,Corrida,AndarParaTrote,TroteParaAndar,TroteParaCorrida,CorridaParaTrote,Arrancada,Frenagem CR_JavaliBrejo_v4_LB.blend`
- **Arquivo:** `CR_JavaliBrejo_v4_LB.blend`, com os **14 clipes de A e B**. Reaberto e conferido; as imagens são encontradas. O `_LA` continua igual.
- **Renders:** as mesmas 8 cadeias da base, em `clipes_LB/<rotulo>/` (GIF, prancha e medidas). Vídeo: `clipes_LB/JavaliBrejo_LoteB.mp4`. Comparação: `clipes_LB/comparacao.json`.

| Clipe / cadeia | Pose igual à base | Avanço (base = brejo) | Maior deriva de casco apoiado | Cabeça mín. base → brejo |
|---|---|---|---|---|
| Trote (laço) | sim, dif. 0,0 | 0,619 u/ciclo (1,33 u/s) | 0 | 19,9 → 18,2 cm |
| Corrida (laço) | sim | 0,933 u/ciclo (2,8 u/s) | 0 | 11,9 → 9,8 cm |
| Andar → AndarParaTrote → Trote | sim | 4,01 u | 0,03 cm | 19,9 → 18,2 cm |
| Trote → TroteParaAndar → Andar | sim | 2,50 u | 0,33 cm | 20,0 → 18,3 cm |
| Trote → TroteParaCorrida → Corrida | sim | 5,96 u | 0,04 cm | 11,9 → 9,8 cm |
| Corrida → CorridaParaTrote → Trote | sim | 5,10 u | 0,28 cm | 12,2 → 10,2 cm |
| Repouso → Arrancada → Corrida | sim | 4,20 u | 0,02 cm | 11,9 → 9,8 cm |
| Corrida → Frenagem → Repouso | sim | 3,06 u | 0,37 cm | 11,9 → 9,8 cm |

- **Pele:** nunca abaixo do chão.
- **Cabeça × corpo:** 0 cruzamentos em todos os clipes.
- **Estiramento:** igual ao da base, ou até menor no corpo da variante. O máximo é 3,65× na virilha, no TroteParaCorrida (base 3,69×).
- **Saltos nas trocas de clipe:** iguais aos da base (18–45°, o giro normal de um quadro da marcha).
- **Auto-interseção do corpo:** +1 par por quadro em todos os clipes (cerdas da crista).
- **Cabeça:** a mais baixa fica a 9,8 cm na corrida, 2 cm abaixo da base; continua longe do chão.

## Lote C: vida (14/11, pedido: "Aprovar e fazer C"; APROVADO 14/11: "Aprovar e fazer D")

**Arquivo:** `CR_JavaliBrejo_v4_LC.blend`, com os **18 clipes de A, B e C**. Reaberto e conferido. Os arquivos `_LA` e `_LB` continuam iguais.

- **Alerta e AlertaParaRepouso:** copiados da base (`fonte/Javali_Clipes_LC.blend`) sem mudança.
- **Farejar e Fuçar: REGERADOS.** A cópia direta foi descartada porque o focinho mais longo da variante atravessava o chão: −1,17 cm no Farejar e −5,86 cm no Fuçar.
  1. **Preparo da malha:** `scripts/preparar_gerador.py` monta `gerador/CR_JavaliBrejo_gerador.blend`. É o `fonte/CR_Javali_Rig_r4.blend`, com os nomes `Javali_*` que o gerador espera, mas com as posições de vértice da v4.
  2. **Geração:** roda a cópia **sem alteração** do gerador da base (`scripts/gerador_base/clipes_javali.py` + `clipes_javali_lc.py`). Comando:
     `JAVALI_LC=1 JAVALI_ANIM_ARQ=JavaliBrejo_Clipes_LC.blend blender -b gerador/CR_JavaliBrejo_gerador.blend -P scripts/gerador_base/clipes_javali.py -- clipes_LC/gerado Farejar,Fucar,Alerta,AlertaParaRepouso`
  3. **Saída:** `clipes_LC/gerado/` (`.blend`, JSON por clipe e manifesto). O gerador mede a cabeça real e abaixa o pescoço por bisseção até a altura pedida.
  4. **Controle:** o mesmo gerador rodado na malha da base reproduz os 4 clipes aprovados **exatamente** (diferença 0,0). Comparação feita por `scripts/comparar_acoes.py`.
  5. **Variante × base:** mudam só **Pescoço, Pescoço2 e Cabeça** no Farejar e no Fuçar. Alerta e AlertaParaRepouso saem idênticos.
- **Renders:** as mesmas 3 cadeias da base, em `clipes_LC/cadeia_*/`. Vídeo: `clipes_LC/JavaliBrejo_LoteC.mp4`.
- **Close do focinho:** `clipes_LC/focinho_prancha.png`, comparando base, cópia direta e regerado no quadro mais baixo, sobre quadriculado de 1 cm (`scripts/render_focinho.py`).

| Clipe | Cabeça mín. base / cópia direta / regerado | Triângulos cabeça × corpo (base → brejo) | Pescoço estica (base → brejo) | Cabeça estica (base → brejo) |
|---|---|---|---|---|
| Farejar | 4,08 / **−1,17** / 3,51 cm | 53 → 0 | 2,44 → 1,95× | 3,58 → 3,03× |
| Fuçar | 0,40 / **−5,86** / 0,40 cm | 267 → 0 | 2,71 → 2,00× | 4,03 → 2,98× |
| Alerta | 20,4 / 18,5 / 18,5 cm | 0 → 0 | 1,34 → 1,29× | igual |
| AlertaParaRepouso | 20,4 / 18,5 / 18,5 cm | 0 → 0 | 1,34 → 1,29× | igual |

- **Saltos nas trocas, deriva dos cascos e pele no chão:** iguais aos da base. Cascos plantados (deriva 0), pele no mínimo a 0,02 cm.
- **Auto-interseção:** +1 par por quadro (cerdas da crista).
- **Achado na base (Javali Silvestre, aprovada):** com a cabeça baixa, o Farejar e o Fuçar têm triângulos da cabeça cruzando o corpo (até 53 e 267 pares, queixo/presas contra o peito). Na variante isso não acontece, porque o focinho mais longo pede menos dobra do pescoço. **Não mexi na base.**

## Lote D: defesa e derrota, ESTUDO sem dano nem hitbox (14/11, pedido: "Aprovar e fazer D"; APROVADO 15/11: "Aprovar lote D")

**Arquivo:** `CR_JavaliBrejo_v4_LD.blend`, com os **24 clipes de A, B, C e D**. Reaberto e conferido: 24 ações, 10k triângulos, imagens encontradas. É o repertório completo, igual ao da base. Os arquivos `_LA`, `_LB` e `_LC` continuam iguais.

- **Fonte aprovada:** o D r2 da base (`fonte/Javali_Clipes_LD_r2.blend`).
- **Geração:** o lote inteiro foi gerado de novo pela cópia do gerador da base (com os módulos `clipes_javali_lb/ld/ld_r2.py` copiados sem alteração) sobre a malha da variante. Comando:
  `JAVALI_LD=1 JAVALI_LD_R2=1 JAVALI_ANIM_ARQ=JavaliBrejo_Clipes_LD.blend blender -b gerador/CR_JavaliBrejo_gerador.blend -P scripts/gerador_base/clipes_javali.py -- clipes_LD/gerado Ameaca,Investida,RecuperacaoInvestida,ReacaoImpacto,Derrota,Derrotado`
- **Controle:** o mesmo gerador na malha da base reproduz o D r2 aprovado **exatamente** (diferença 0,0 nos 6 clipes).
- **Variante × base:**
  - **Ameaça, Investida, RecuperaçãoInvestida e ReaçãoImpacto:** saem **idênticos** (diferença 0,0).
  - **Derrota e Derrotado:** mudam só Pescoço, Pescoço2 e Cabeça, com diferença pequena (máx. 0,013 por componente). É a cabeça apoiada no chão sendo recalculada.
- **Saídas:**
  - renders das 3 cadeias da base em `clipes_LD/cadeia_*/`;
  - vídeo `clipes_LD/JavaliBrejo_LoteD.mp4`;
  - close da cabeça em `clipes_LD/focinho_prancha.png`;
  - comparação em `clipes_LD/comparacao.json`.

| Clipe | Cabeça mín. base / cópia direta / regerado | Pescoço estica (base → brejo) |
|---|---|---|
| Ameaça | 12,6 / 8,4 / 8,4 cm | 1,89 → 1,79× |
| Investida | 5,9 / 2,0 / 2,0 cm | 1,83 → 1,73× |
| RecuperaçãoInvestida | 7,8 / 4,3 / 4,3 cm | 1,65 → 1,58× |
| ReaçãoImpacto | 20,4 / 18,5 / 18,5 cm | 1,34 → 1,29× |
| Derrota | 0,40 / **−1,22** / 0,40 cm | 1,80 → 1,70× |
| Derrotado | 0,40 / **−1,22** / 0,40 cm | 1,80 → 1,69× |

- **Cabeça × corpo:** 0 cruzamentos em todos os clipes, na base e no brejo.
- **Cascos:** a maior deriva é 0,06 cm (cadeia da Investida).
- **Saltos nas trocas:** iguais aos da base.
- **Auto-interseção:** +1 par por quadro. Na Derrota ela já era alta na base (83,5 por quadro), com as pernas dobradas umas contra as outras.
- **Herdado da base:** a RecuperaçãoInvestida tem a pele 0,05 cm abaixo do chão (−0,5 mm), igual na base aprovada. Não foi corrigido.
- **Investida:** a cabeça desce mais que na base (2,0 cm), porque o focinho é mais longo e caído, mas não toca o chão.

## Tempo aproximado (14/11)

| Etapa | Tempo |
|---|---|
| M0 e inspeção dos `.blend` | ~6 min |
| Variante v1→v4 (script, bake e 4 rodadas de prancha) | ~9 min |
| Andar (render, medidas, closes, GIF e vídeo) | ~5 min |
| Reabertura e organização | ~2 min |

Para comparação, a base (Meshy, LOW, rig piloto, pesos r2–r4 e lote A) levou o dia 13/11 inteiro.

## Lições para repetir no próximo bioma

1. Mexer só em posições de vértice em zonas rígidas (cabeça) ou de coluna (crista). Assim os pesos e a costura continuam válidos e a animação passa sem retoque. Conferir os pares da costura antes e depois.
2. Procurar imagens pelo **sufixo exato** (`_Cor`, `_Rugosidade`, `_Normal`): "Cor" casa com "Corpo".
3. O `.blend` da base guardou `bake.use_selected_to_active=True` (do bake do bruto). Desligar antes de assar, senão aparece "No valid selected objects".
4. A sujeira precisa contrastar com a pelagem: lama escura em pelo escuro não aparece.
5. Em crista low-poly, picos agudos viram lâminas. Usar altura com ondulação suave e deixar a "cerda agrupada" na textura.
6. Medir penetrações e estiramento na base e na variante, no mesmo clipe, para isolar o que a variante introduz.

## Pendências

- **Ficha visual própria:** a direção da v4 foi aprovada visualmente em 14/11; ainda não existe ficha em `REFERENCIAS/pantano-nebuloso/javali-do-brejo/`.
- **Porte:** oficial pendente. A escala continua a da base (dorso a ~0,75 u, PROPOSTA).
- **Orçamento:** 10k triângulos, 2 materiais e 6 mapas de 1024 por animal. Com vários animais em celular, propor LOD (~3–4k) e atlas de 1 material. Não foi feito.
- **Desempenho em jogo:** exige teste posterior no Studio, com autorização.
- **Outros clipes:** só o Andar foi transferido. Os demais (Repouso, curvas, lotes B–D) dependem de autorização.
