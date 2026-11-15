# Javali Silvestre (Ref): fauna de recurso da Floresta Ancestral

É um animal selvagem de recurso e **não é domesticável**. A referência está em `REFERENCIAS/floresta-ancestral/javali-silvestre/javali-silvestre-referencia.png`, e a ficha da fauna em `DOCS/fauna/floresta-ancestral.md`.

## m1: Meshy (13/11/2026, autorizado pelo usuário, 36 créditos)

O pipeline é o mesmo do Cervo-do-Bosque (`../Cervo_do_Bosque_Ref/meshy/`).

1. **Image to Image** (nano-banana-2, 3 vistas neutras, 6 créditos). Comandos:
   - `python -I meshy/meshy_javali.py imagem <ref> meshy`;
   - limpar as bordas: `meshy/imagem/limpa_0..2.png`.
   - Tarefa: 01a1d642-1f65-718c-af33-b7fa286680c8.
2. **Multi-Image to 3D** (meshy-7.1, textura 4K PBR, 30 créditos). Comando:
   - `python -I meshy/meshy_javali.py 3d meshy meshy/imagem/limpa_0.png meshy/imagem/limpa_1.png meshy/imagem/limpa_2.png`.
   - Tarefa: 01a1d643-0dea-7024-9499-f762cf5de8ef.
   - Saída: `meshy/modelo/CR_Javali_meshy.glb/.fbx` e `T_meshy_*.png`.
3. **Importação:**
   - Comando: `blender -b --factory-startup -P meshy/importar_meshy_javali.py -- meshy/modelo/CR_Javali_meshy.glb meshy/modelo`.
   - O focinho fica em −Y.
   - Escala: o meio do dorso fica a **0,75 u** (percentil 92, para ignorar as cerdas da crista). Isso é uma **PROPOSTA**; o porte oficial está pendente.
   - Gera `meshy/modelo/CR_Javali_meshy_bruto.blend`, os renders `m1_A_*` (argila) e `m1_B_*` (textura) e `m1_metricas.json`.
4. **Prancha:** `python meshy/prancha_javali.py meshy/modelo` gera `meshy/modelo/m1_prancha.png`.

### Medidas (m1 bruto)

| Medida | Valor |
|---|---|
| Comprimento | 1,47 u |
| Largura | 0,45 u |
| Altura máxima (ponta da crista) | 0,85 u |
| Triângulos | **5,64 M** |
| Material | 1 |

Com 5,64 M de triângulos, a malha bruta está muito acima de um orçamento de jogo. Ela serve só como fonte de bake.

### Comparação com a referência

**Fiel à referência:**
- corpo compacto, com o peito fundo e o ombro mais alto que o quadril;
- crista de cerdas alta da nuca ao dorso;
- presas curvas de marfim para cima e para fora;
- disco do focinho, orelhas pequenas eretas e bochechas claras;
- cascos escuros com os dedos acessórios.

**Diferenças:**
- a cauda é mais longa e fina e fica afastada do corpo (na referência ela é curta, com tufo, e cai junto à anca);
- a pelagem é mais escura e tem menos reflexo ferrugem;
- as pernas são um pouco mais altas.

## Próximos passos (cada um com aprovação)

1. Malha de jogo LOW, ~10–12k triângulos, com UV e bake de 1024, seguindo `low_v2` do cervo.
2. Rig com nomes do jogo.
3. Lotes de clipes, com o gerador do cervo adaptado.

O Studio não foi testado.

## low_v1: malha de jogo (13/11, autorizada: "Sim, malha de jogo")

Script `meshy/meshy_low_javali.py`, adaptado do cervo. Comando:
`blender -b meshy/modelo/CR_Javali_meshy_bruto.blend -P meshy/meshy_low_javali.py -- low_v1 ycab=0.42`

Etapas:
1. **Voxel 0,004.**
2. **Remoção de ilhas soltas.** Saem 283 fragmentos de cerda da crista (0,5% dos vértices).
3. **Redução para 10.000 triângulos.** Focinho e presas ficam mais densos, e as articulações são reforçadas.
4. **Separação em duas peças:**
   - Cabeça: y < focinho + 0,42 e z > 0,20.
   - Corpo: o resto.
   - Na v1, o corte em focinho + 0,46 e sem o limite de z levava as pontas dos cascos dianteiros para a cabeça.
5. **UV e bake de 1024** (cor, normal, rugosidade). Gera o GLB e `prancha_low.png` (via `python low_prancha.py low_v1`).

Resultado:

| Peça | Triângulos | Material |
|---|---|---|
| Cabeça | 3.357 | `M_Javali_Cabeca` |
| Corpo | 6.643 | `M_Javali_Corpo` |

A crista, as presas e o rosto foram preservados. O orçamento é uma **PROPOSTA**.

## Rig piloto (13/11): poses estáticas, sem clipes

Script `rig/rig_javali.py`. Comando:
`blender -b low_v1/CR_Javali_Silvestre_LOW.blend -P rig/rig_javali.py -- rig`

### Ossos

São 30 ossos, 29 deles deformam. Os nomes são os mesmos do cervo; as poses do cervo **não** são reaproveitadas.
- Coluna: Raiz, Pelve, Coluna1–3.
- Pescoço e cabeça: Pescoco, Pescoco2 (curtos), Cabeca, Orelha E/D.
- Cauda: Cauda1–2.
- Pernas dianteiras: Escapula, Braco, Antebraco, Canela, Quartela.
- Pernas traseiras: Coxa, Perna, CanelaTras, QuartelaTras.
- Sem Mandibula: a boca da fauna é fechada, e as presas são rígidas na Cabeca.

### Juntas

- **Alturas** (anatomia de suíno):

  | Junta | Altura |
  |---|---|
  | Carpo | 0,145 |
  | Cotovelo | 0,27 |
  | Ombro | 0,42 |
  | Jarrete | 0,20 |
  | Soldra | 0,36 |
  | Quadril | 0,56 |

- **Cascos:** cada pata usa o seu, medido na malha. O Meshy deixou a traseira D cerca de 6 cm à frente da E.

### Pesos

- **Heat no proxy voxel:** usa voxel de **0,012**. Com 0,008 o proxy ficava com 7 ilhas e o heat falhava em todos os ossos.
- **Cabeça rígida** a partir de y < focinho + 0,27.
- **Orelhas:** pesos manuais.
- **Pernas por segmento:** cada vértice da perna pertence ao segmento onde se projeta (lição do cervo r2).
- **Garganta:** transição gradual entre Cabeca e Pescoco.
- **Costura:** 107 de 107 vértices de borda iguais nas duas peças.
- **Limites:** no máximo 4 influências; nenhum vértice sem peso; nenhum osso sem vértice.

### Provas

Arquivos `rig/prova_*.png`, `rig/prancha_rig.png` (via `python rig/prancha_rig.py rig`) e `rig/rig_relatorio.json`. O chão é quadriculado de 10 cm.

| Pose | Ponto mais baixo da malha |
|---|---|
| apoio | 0,0 cm |
| passada | −0,2 cm |
| giro | −0,1 cm |
| reacao | 0,0 cm |
| focinho_baixo | 0,0 cm |

- **focinho_baixo:** o pescoço gira 40° (com Pescoco2 a ½ e Cabeca a ¼ desse ângulo). O ponto mais baixo da cabeça fica a 2,0 cm do chão, e as presas não atravessam o chão.
- **Reabertura verificada:** 30 ossos; as 2 malhas com Armature e 29 grupos; as 6 texturas ligadas.

**Pendências:**
- A cauda continua longa (diferença do m1).
- As poses são estáticas: o avanço e os apoios só serão medidos nos clipes.

## Catálogo de animações (pedido do usuário, 13/11)

O catálogo completo tem os lotes:
- **A:** Repouso, Andar, VirarE/D, ParadoParaAndar, AndarParaParado.
- **B:** Trote, Corrida, transições, Arrancada, Frenagem.
- **C:** Farejar, Fuçar, Alerta, AlertaParaRepouso.
- **D:** Ameaca, Investida, RecuperacaoInvestida, ReacaoImpacto, Derrota, Derrotado. Este lote depende de decisões de jogo.

Pela regra do catálogo, o rig piloto vem antes de qualquer lote, e **o lote A só começa depois da aprovação deste rig**.

O comportamento defensivo da espécie ("territorial, investe quando acuado") continua como [PROPOSTA].

## Lote A: base de locomoção (13/11, autorizado: "Aprovar e fazer lote A")

### Ferramentas

- **Gerador:** `rig/clipes_javali.py`. Comando:
  `blender -b rig/CR_Javali_Rig_r2.blend -P rig/clipes_javali.py -- rig/clipes_LA`
  - O mecanismo vem do cervo: IK das 4 patas no boleto, casco apoiado preso a S(t), QA e JSON por clipe.
  - As poses e os parâmetros são próprios do javali.
- **Render:** `rig/render_javali.py` (câmeras fixas) e `rig/prancha_clipes.py` (GIF e prancha).

### Rig r2: só pesos

Script `rig/rig_pesos_r2.py`; o rig piloto aprovado continua em `CR_Javali_Rig.blend`.

- **Problema:** a pele da barriga e da axila esticava até 4,7× ao balançar as dianteiras. O heat vazou pela barriga fina: vértices do meio da barriga tinham 22% de CoxaD, a 30 cm da coxa.
- **Correção:**
  1. Limpeza por distância: o peso de cada osso de perna só vale perto do próprio osso, e o excedente vai para a coluna.
  2. Suavização guiada por medição: as arestas que passam de 2× nos quadros dos clipes são suavizadas, em 12 rodadas.
- **Resultado:** pior estiramento de 2,7× no Andar e 3,1–3,3× nas curvas. Fica na virilha, por dentro das coxas. O cervo foi aprovado com 2,9–3,2×.
- **Tentativa descartada:** a correção por regiões fixas só mudou o degrau de lugar (7,5×).

### Parâmetros do Andar

Todos são **PROPOSTA**, ou seja, parâmetro técnico e não regra do jogo.

| Parâmetro | Valor |
|---|---|
| Ciclo | 0,9 s |
| Passada | 0,26 u |
| Apoio | 65% |
| Altura do casco | 4,5 cm |
| Velocidade | 0,444 u/s |
| Avanço por ciclo | 0,40 u |
| Giro nas curvas | 25°/s (raio ~1 u) |

- Quatro tempos, em sequência lateral: TrasE, E, TrasD, D.
- O apoio das dianteiras fica 3,5 cm à frente do repouso. Sem isso, a pata chegava reta no fim do apoio e o antebraço saltava 40° num quadro.
- O alcance é limitado a 96,5% da cadeia.

### Clipes

O arquivo é `rig/clipes_LA/Javali_Clipes_LA.blend` (6 ações; reabertura verificada). O JSON está em `rig/clipes_LA/json/`, e o manifesto em `rig/clipes_LA/manifesto_clipes.json`.

| Clipe | Duração | Laço | Entrada → saída | Maior giro entre quadros |
|---|---|---|---|---|
| Repouso | 8,0 s | sim | laço; cabeça baixa, 4 respirações, orelhas e cauda | 18,9° (cauda espantando mosca) |
| Andar | 7,2 s (8 ciclos) | sim | laço | 23,8° (casco saindo do chão) |
| VirarE | 7,2 s | sim | laço, troca com o Andar no q0 | 25,1° |
| VirarD | 7,2 s | sim | laço, troca com o Andar no q0 | 25,3° |
| ParadoParaAndar | 2,2 s (67 quadros) | não | Repouso q0 → Andar q0; avança 0,60 u | 25,5° |
| AndarParaParado | 2,53 s (77 quadros) | não | Andar q0 → Repouso q0; avança 0,30 u | 21,8° |

- **ParadoParaAndar:** 0,4 s de preparo, com o peso indo para a diagonal que fica, e depois a rampa de 1 ciclo.
- **AndarParaParado:** a pata que já está no ar pousa normalmente, a desaceleração dura 1 ciclo, o último passo encurta e o clipe termina com os quatro cascos apoiados.

### QA

| Medida | Resultado |
|---|---|
| Emendas (laço, entrada e saída) | 0,0° |
| Erro de IK | ≤ 0,4 cm |
| Escorregão do casco apoiado (gerador) | ≤ 0,4 cm (curvas); 0,02 cm (Andar) |
| Casco no chão | z mínimo 0,02 cm, sem atravessar |

### Renders

Os renders ficam em `rig/clipes_LA/render/<rotulo>/`: GIF lateral fixo e 3/4 fixo, prancha e `medidas.json`.

- **Cena:** câmeras fixas, piso quadriculado de 10 cm e postes a cada 0,25 u. O avanço vem de um **controlador de demonstração externo**, que integra a velocidade gravada; a ação em si é no lugar.
- **Andar** (3 ciclos): 0,400 u/ciclo e deriva do casco apoiado de 0,02 cm.
- **Curvas:** 0,378 u/ciclo, com deriva de 1,3 cm (VirarE) e 0,95 cm (VirarD). A deriva é medida no boleto e inclui o limite de alcance.
- **Cadeias** `ParadoParaAndar+Andar@1` e `Andar+AndarParaParado+Repouso@1`: a troca de clipe tem o mesmo giro de um quadro normal do Andar (18–23°).
- **Quadros PNG:** foram para o scratchpad para não pesar a pasta; dá para regenerá-los com o render.

## Lote B: aceleração e corrida (13/11, autorizado: "Aprovar e fazer B")

### Ferramentas e rig

- **Módulo do lote B:** `rig/clipes_javali_lb.py`. Só é carregado com `JAVALI_LB=1`; sem a variável, o lote A continua idêntico. Comando:
  `JAVALI_LB=1 JAVALI_ANIM_ARQ=Javali_Clipes_LB.blend blender -b rig/CR_Javali_Rig_r3.blend -P rig/clipes_javali.py -- rig/clipes_LB Trote,Corrida,AndarParaTrote,TroteParaAndar,TroteParaCorrida,CorridaParaTrote,Arrancada,Frenagem`
- **Rig r3** (`rig/CR_Javali_Rig_r3.blend`): só pesos, gerado pelo mesmo `rig_pesos_r2.py` com as poses dos lotes A e B na medição. Muda duas coisas:
  - Abaixo de 0,12 a pata não tem mais peso de tronco. O esporão atrás do casco dianteiro tinha 19% de Coluna3, vindo do heat, e afundava 6 mm no apoio do galope.
  - Nessa mesma faixa, o peso cortado pela limpeza por distância vai para o osso de perna mais próximo, e não para a coluna. Mandar tudo para a perna mais próxima em qualquer altura piorou a barriga (4,5×) e foi descartado.
- **Lote A regerado a partir do r3:** o manifesto ficou igual, com diferença só na segunda casa decimal do maior giro. Os renders do A foram refeitos.
- **QA novo no gerador:**
  - `apoios_limitados_pelo_alcance`: conta os cascos apoiados que o IK teve de puxar para dentro do alcance, o que tira o casco do chão.
  - `maior_giro_entre_quadros`: detecta estalo de IK.

### Parâmetros

Todos são **PROPOSTA**.

| Marcha | Ciclo | Passada | Apoio | Velocidade | Observação |
|---|---|---|---|---|---|
| Trote | 14 quadros (0,467 s) | 0,26 u | 42% | 1,33 u/s | pares diagonais |
| Corrida | 10 quadros (0,333 s) | 0,28 u | 30% | 2,8 u/s | galope rotatório compacto, fase aérea curta |

- **Por que a passada é curta:** a perna do javali é curta. Com passada de 0,36–0,40 u, a dianteira deixava o chão esticada além do alcance (1,04×). Afastar só o centro do apoio (−8 cm) fez o joelho dobrar para o lado errado (giro de 182°).
- **Corrida:** o centro do apoio das dianteiras fica 4,5 cm à frente, e a extensão extra da pata acontece só no fim do balanço (lição do cervo r2).
- **Postura:** cabeça baixa e à frente, cauda meio erguida, coluna com flexão curta.

### Clipes

O arquivo é `rig/clipes_LB/Javali_Clipes_LB.blend` (8 ações; reabertura verificada). O JSON está em `rig/clipes_LB/json/`, e o manifesto em `rig/clipes_LB/manifesto_clipes.json`.

| Clipe | Duração | Entrada → saída | Desloc. | Maior giro/quadro | Apoio puxado |
|---|---|---|---|---|---|
| Trote | 2,8 s (6 ciclos, laço) | laço | — | 32,9° | 0 |
| Corrida | 2,0 s (6 ciclos, laço) | laço | — | 44,7° | 0 |
| AndarParaTrote | 2,3 s | Andar q0 → Trote q0 | 2,37 u | 32,9° | 0 |
| TroteParaAndar | 2,3 s | Trote q0 → Andar q0 | 1,48 u | 32,5° | 2 |
| TroteParaCorrida | 1,47 s | Trote q0 → Corrida q0 | 3,47 u | 46,2° | 0 |
| CorridaParaTrote | 1,7 s | Corrida q0 → Trote q0 | 2,93 u | 44,3° | 1 |
| Arrancada | 1,63 s | Repouso q0 → Corrida q0 | 2,33 u | 45,0° | 0 |
| Frenagem | 2,53 s | Corrida q0 → Repouso q0 | 2,12 u | 44,7° | 0 |

- **Arrancada:** 0,3 s carregando as traseiras (a garupa desce sem levantar os ombros) e depois 3 ciclos de aceleração.
- **Frenagem:** a pata que já está no ar pousa normalmente, a desaceleração dura 0,85 s com o peso nas dianteiras, e o clipe assenta nos quatro cascos.
- **Maior giro por quadro:** é a dobra rápida do casco no galope. A corrida aprovada do cervo chegava a 86,5°.

### QA (gerador)

| Medida | Resultado |
|---|---|
| Emendas (laço, entrada e saída) | 0,0° em todos |
| Erro de IK | 0 |
| Escorregão do casco apoiado | ≤ 0,37 cm |
| Casco no chão | z mínimo 0,02 cm, sem atravessar |

### Renders

Os renders ficam em `rig/clipes_LB/render/<rotulo>/`: GIF lateral fixo e 3/4 fixo, prancha e medidas. O avanço vem do controlador de demonstração externo.

| Rótulo | Avanço | Deriva do casco apoiado | Pele | Pior estiramento |
|---|---|---|---|---|
| Trote (3 ciclos) | 0,619 u/ciclo | 0 | nunca abaixo do chão | 3,35× |
| Corrida (3 ciclos, atravessa a cena) | 0,933 u/ciclo, 2,7 u em 1 s | 0 | nunca abaixo do chão | 2,92× |
| Cadeias de transição | — | ≤ 0,37 cm | nunca abaixo do chão | até 3,69× (TroteParaCorrida, virilha) |

- **Cadeias renderizadas:** AndarParaTrote, TroteParaAndar, TroteParaCorrida, CorridaParaTrote, Repouso+Arrancada+Corrida e Corrida+Frenagem+Repouso.
- **Troca de clipe:** o giro na emenda fica dentro do giro normal de um quadro da marcha (18–45°).
- **Quadros PNG:** ficam no scratchpad.

## Lote C: vida selvagem (13/11, pedido: "Siga com o C")

### Ferramentas

- **Módulo do lote C:** `rig/clipes_javali_lc.py`. Só é carregado com `JAVALI_LC=1`. Comando:
  `JAVALI_LC=1 JAVALI_ANIM_ARQ=Javali_Clipes_LC.blend blender -b rig/CR_Javali_Rig_r4.blend -P rig/clipes_javali.py -- rig/clipes_LC Farejar,Fucar,Alerta,AlertaParaRepouso`
- **Focinho ao chão (novo no gerador):** `ext["focinho"] = (altura alvo, fator)`.
  - O gerador abaixa o pescoço até o ponto mais baixo da cabeça (disco do focinho ou ponta da presa) ficar na altura pedida, buscando o ângulo por bisseção. O extra é dividido 60/30/10 entre Pescoco, Pescoco2 e Cabeca.
  - Quando o ponto mais baixo troca entre o focinho e a presa, o pescoço saltava até 14,6° num quadro. Para evitar isso, o ângulo é calculado em duas passadas e filtrado pelo lado seguro: mínimo numa janela de ±4 quadros, depois média de ±2. O resultado nunca abaixa a cabeça além do valor exato.
- **QA novo:** `cabeca_z_min_cm`, o ponto mais baixo da cabeça no clipe.
- **Rig r4** (`rig/CR_Javali_Rig_r4.blend`): só pesos, com as poses de cabeça baixa na medição (`rig_pesos_r2.py`, 40 rodadas).
  - O pescoço, que esticava até 12×, ficou em cerca de 4×.
  - Os lotes A e B foram regerados com o r4: os manifestos ficaram iguais, e a pele mediu igual ou melhor.
  - Os GIFs de A e B continuam os do r3; a diferença na pele é mínima.

### Clipes

O arquivo é `rig/clipes_LC/Javali_Clipes_LC.blend`, com JSON em `rig/clipes_LC/json/` e o manifesto ao lado. Durações e amplitudes são PROPOSTA.

| Clipe | Duração | Entrada → saída | O que faz | Cabeça mín. |
|---|---|---|---|---|
| Farejar | 4,4 s | Repouso q0 → Repouso q0 | focinho a ~4 cm do chão, 3 buscas curtas para os lados com fungadas, volta; cascos plantados | 4,1 cm |
| Fucar | 5,4 s | Repouso q0 → Repouso q0 | focinho encosta no chão; 4 empurrões (tronco à frente, disco do focinho gira para cima, garupa firma), cauda abana; volta | 0,4 cm |
| Alerta | 1,4 s | Repouso q0 → AlertaFim | cabeça sobe rápido (0,35 s), passa um pouco e assenta; orelhas para a frente, cauda tensa; o último quadro serve de pose mantida | 20,4 cm |
| AlertaParaRepouso | 1,6 s | AlertaFim → Repouso q0 | solta o ar e relaxa pescoço e orelhas | — |

O Fucar não é laço: tem entrada, empurrões e saída.

### QA

| Medida | Resultado |
|---|---|
| Emendas | 0,0° |
| Erro de IK | 0 |
| Escorregão do casco | 0 |
| Maior giro entre quadros | ≤ 3,3° |
| Focinho e presas | nunca abaixo do chão |

### Renders

Os renders ficam em `rig/clipes_LC/render/cadeia_*/`: GIF lateral fixo e 3/4 fixo, prancha e medidas.

| Cadeia | Pior estiramento | Arestas > 2× por quadro |
|---|---|---|
| Repouso + Farejar + Repouso | 3,58× | 21 |
| Repouso + Fucar + Repouso | 4,03× | 49 |
| Repouso + Alerta + AlertaParaRepouso + Repouso | 1,61× | 0 |

Nas três cadeias, a pele nunca fica abaixo do chão e a deriva dos cascos é 0.

Pendente: o estiramento de cerca de 4× na nuca e na mandíbula com a cabeça no chão. É limite do rig de pescoço curto (dois ossos de pescoço).

**13/11: lote C APROVADO pelo usuário** ("Aprovar o lote C"). Lotes A, B e C aprovados no Blender (18 clipes, rig r4). Próximo: lote D (defesa/derrota, sujeito a decisão de jogo), só com autorização. Studio não testado.

## Lote D: defesa e derrota, ESTUDO (13/11, pedido: "Fazer o lote D")

O comportamento defensivo ("territorial, investe quando acuado") é **[PROPOSTA]**. Não há dano, alcance, hitbox, duração de estado, loot nem regra de coleta.

### Ferramentas

- **Módulo do lote D:** `rig/clipes_javali_ld.py`, carregado com `JAVALI_LD=1` (liga também os lotes B e C). Comando:
  `JAVALI_LD=1 JAVALI_ANIM_ARQ=Javali_Clipes_LD.blend blender -b rig/CR_Javali_Rig_r4.blend -P rig/clipes_javali.py -- rig/clipes_LD Ameaca,Investida,RecuperacaoInvestida,ReacaoImpacto,Derrota,Derrotado`
- **Recursos novos no gerador:**
  - `ext["fk_pernas"]`: pernas soltas em FK sobre a pose do Repouso q0; o IK fica desligado no quadro.
  - `ext["assentar"]`: o ponto mais baixo do corpo encosta no chão.
  - `ext["nivelar"]`: a inclinação da raiz é resolvida por bisseção para que traseiras e dianteiras toquem o chão juntas.
  - `ext["cabeca_chao"]`: a cabeça desce até apoiar, girando o pescoço para o lado do chão.
  - QA: `maior_extensao_cascos_u_quadro`.

### Clipes

O arquivo é `rig/clipes_LD/Javali_Clipes_LD.blend`, com JSON e manifesto. Números são PROPOSTA.

| Clipe | Duração | Entrada → saída | O que faz |
|---|---|---|---|
| Ameaca | 1,8 s | Repouso q0 → AmeacaFim | cabeça baixa com as presas à frente; pateia 2× com a dianteira D (raspa 6 cm para trás); peso nas dianteiras; orelhas para trás; cauda erguida. Antecipação legível |
| Investida | 1,2 s | AmeacaFim → InvestidaFim | empurrão de 0,2 s com as traseiras e galope de cabeça baixa (até 2,8 u/s); avança 2,15 u. **Maior extensão: q30 (1,06 u entre cascos)**, referência para a futura integração, sem hitbox |
| RecuperacaoInvestida | 2,43 s | InvestidaFim → AlertaFim | freia com o peso nas dianteiras, ergue o focinho e reassenta os cascos; avança 1,98 u; termina na pose do Alerta |
| ReacaoImpacto | 1,2 s | Repouso q0 → Repouso q0 | tronco e pescoço contraem; a dianteira E recua um passo e volta ao lugar |
| Derrota | 2,6 s | Repouso q0 → DerrotaFim | as traseiras cedem com a garupa descendo (traseiras e dianteiras tocam o chão juntas), depois as dianteiras dobram, ele tomba sobre o flanco E (84°) com um pequeno quique, e a cabeça apoia por último |
| Derrotado | 1,0 s (laço parado) | DerrotaFim | pose final mantida |

### QA

| Medida | Resultado |
|---|---|
| Emendas | 0,0°; na entrada da Investida, 0,1° |
| Escorregão dos cascos apoiados | ≤ 0,24 cm |
| Maior giro entre quadros | 16° na patada da Ameaça; 45° no galope da Investida, como na Corrida; ≤ 6° na Derrota |
| Derrotado | tronco 0,0 cm, pernas 0,24 cm e cabeça 0,4 cm do chão; nada flutua nem atravessa |

### Renders

Os renders ficam em `rig/clipes_LD/render/cadeia_*/`.

| Cadeia | Resultado |
|---|---|
| Repouso → Ameaca → Investida → Recuperacao → AlertaParaRepouso → Repouso | 4,13 u; pele mín. −0,08 cm, num quadro só |
| Repouso → ReacaoImpacto → Repouso | pele nunca abaixo do chão; estiramento 1,98× |
| Repouso → Derrota → Derrotado | pele nunca abaixo do chão; estiramento 2,57× |

### Ajustes medidos durante o lote

- **Pernas deitadas:** com o giro lateral −14/−24°, o tronco ficava 6 cm no ar, escorado nas pernas. Com −4/−16°, tronco, pernas e cabeça ficam apoiados.
- **Queda:** a inclinação manual da garupa deixava as traseiras 8,7 cm no ar ou tirava as dianteiras do chão. Foi trocada pela inclinação resolvida por quadro.
- **Recuperação:** a absorção mais forte afundava o boleto 3 mm e foi reduzida.

## Lote D r2: refino de peso (13/11, pedido "refino de peso no lote D")

### Arquivos

- O r1 continua intacto e reproduzível em `rig/clipes_LD/`.
- O r2 está em `rig/clipes_LD_r2/Javali_Clipes_LD_r2.blend` (6 ações; reabertura verificada), com JSON e manifesto.
- Módulo `rig/clipes_javali_ld_r2.py`: com `JAVALI_LD_R2=1` ele sobrescreve só os clipes refinados. Comando:
  `JAVALI_LD=1 JAVALI_LD_R2=1 JAVALI_ANIM_ARQ=Javali_Clipes_LD_r2.blend blender -b rig/CR_Javali_Rig_r4.blend -P rig/clipes_javali.py -- rig/clipes_LD_r2 Ameaca,Investida,RecuperacaoInvestida,ReacaoImpacto,Derrota,Derrotado`
- Comparação em `rig/clipes_LD_r2/comparacao/`:
  - `antes_depois_<cadeia>_<vista>.gif`: r1 em cima e r2 embaixo, câmera fixa igual (`JAVALI_CAM_FIX` no render) e 30 qps;
  - `giro_<clipe>.png` e `vel_*.png`;
  - `comparacao_r1_r2.json`, com o giro por quadro e a distância por fase;
  - `medidas_*.json` e `prancha_referencia_r1_r2.png`.
  - Gerada por `rig/comparar_ld_r2.py`.

### O que mudou

| Clipe | Diagnóstico no r1 | Correção no r2 | Resultado |
|---|---|---|---|
| RecuperacaoInvestida | mantinha 2,8 u/s por 12 quadros: 1,12 u antes de frear, 1,98 u no total (a investida tem 2,15 u). Parecia uma segunda corrida, e depois ficava 1,3 s quase parada | freia desde o q2 (0,45 s), com passos que encurtam; a pata que já estava no ar pousa como na Investida; ombros recebem o peso; traseiras se recolhem 5 cm sob o corpo; o resto assenta e volta ao Alerta | 0,18 u até frear, 0,45 u freando, parado no q13 (0,43 s), 1,27 s assentando. **Total 0,63 u em 1,73 s.** Cadeia: 2,78 u (antes 4,13), deslocamento contado uma vez só |
| Ameaca | duas patadas idênticas, com inversão seca (16,1°/quadro em AntebracoD, q21 e q33) | a patada vira um gesto contínuo (ergue e estende, toca, raspa arrastando, ergue e volta); a 2ª é menor e mais curta; o peso sai da pata antes de cada patada e a cabeça acompanha a raspada | pico de 10,0° (q15) |
| ReacaoImpacto | o corpo recuava e voltava sozinho, numa mola, antes do passo de recuperação (q20 já de volta) | o empurrão leva o corpo e o mantém atrás; a dianteira E recua junto e segura o peso; ele se recompõe com a pata voltando | escorregão 0; o pico de 13,2° é a orelha no golpe |
| Derrota | o tombo desacelerava antes do chão, e o flanco pousava sem peso | o tombo acelera até o impacto, com quique curto e amortecido; cabeça e cauda sacodem no choque | pico de 6,6° na Raiz (q46, o impacto); tronco, pernas e cabeça continuam apoiados |
| Investida | o pico de 44,9° no q26 é a dobra rápida do casco no galope, igual à Corrida aprovada | mantida (ver `antes_depois_investida_lado_fixo.gif`) | igual ao r1 |

### Erros encontrados e corrigidos durante o r2

- Na Reação, o limite t = 0,70 fazia a pata pular 5 cm "apoiada".
- Na Recuperação, passos mínimos com o centro de apoio mudando deslizavam até 4 cm; agora a pata dá o passo de verdade.
- A pata que estava no ar no q0 mudava o pouso e causava emenda de 2,8°.
- A absorção mais forte fazia o boleto afundar 1,1 mm.

### QA do r2

| Medida | Resultado |
|---|---|
| Emendas (todas) | 0,0°; na entrada da Investida, 0,1°, igual ao r1 |
| Escorregão dos cascos apoiados (gerador) | ≤ 0,03 cm (r1: 0,24 cm) |
| Deriva na cadeia renderizada | 0,06 cm (r1: 0,23 cm) |
| Penetração no chão | um quadro de 0,5 mm na Recuperação (atrás do boleto dianteiro E); no r1 eram 0,8 mm |
| Estiramento máximo da pele | igual ao r1 (2,69× / 2,06× / 2,57×) |

### Pendências

- A deformação de cerca de 4× na nuca e na mandíbula no Fucar fica para tratar separadamente.
- O r2 aguarda a revisão visual do usuário.

**13/11: lote D r2 APROVADO pelo usuário** ("Aprovar o lote D r2"). Base oficial do lote D: `rig/clipes_LD_r2/` (o r1 em `rig/clipes_LD/` fica só como histórico). Javali completo no Blender: lotes A, B, C e D r2 = 24 clipes, rig r4. Pendentes: deformação ~4× da nuca no Fucar; Studio (com autorização); commit.

**14/11: commit 087628f** (84 arquivos: scripts, JSON dos clipes, manifestos/medidas, LEIA-ME; GIFs e binários fora do git). Push feito 14/11 (junto com a9d0fb0 da Wyvern).
