# Coruja-da-Floresta (Ref): fauna de recurso da Floresta Ancestral

É um animal selvagem de recurso e **não é domesticável**. A referência está em `REFERENCIAS/floresta-ancestral/coruja-da-floresta/coruja-da-floresta-referencia.png`, e a ficha em `DOCS/fauna/floresta-ancestral.md` (seção 4).

O comportamento "ave noturna, poleiros altos, recua ou voa" é **[PROPOSTA]**. Continuam **[PENDENTE]**:
- se ela é noturna;
- como o jogador a derrota;
- onde o corpo cai para a coleta;
- a altura dos poleiros.

## m1: Meshy (14/11/2026, autorizado: "PROSSIGA COM A CORUJA", 36 créditos)

O pipeline é o mesmo do cervo e do javali.

1. **Image to Image** (nano-banana-2, 6 créditos; tarefa 01a1dad4-aff1-74ba-bb93-359cb89f5e0a). Comando:
   `python -I meshy/meshy_coruja.py imagem <ref> meshy`
   - Pedido: a **pose de rig com as asas abertas**, para servir tanto ao voo quanto ao pouso. Num modelo gerado com as asas fechadas, as penas saem fundidas ao corpo.
   - **O perfil veio com a asa fechada, contradizendo as outras vistas, e foi descartado.**
   - A frente e as costas foram limpas: fica só a maior figura conectada da imagem, porque havia pedaços da vista vizinha (`meshy/imagem/limpa_1.png` e `limpa_2.png`).
2. **Multi-Image to 3D** com a frente e as costas (meshy-7.1, textura 4K PBR, 30 créditos; tarefa 01a1dad5-c68b-775d-b134-8f96c62463c2). Saída em `meshy/modelo/CR_Coruja_meshy.glb/.fbx` e `T_meshy_*.png`.
3. **Importação:**
   - Comando: `CORUJA_INVERTER=1 blender -b --factory-startup -P meshy/importar_meshy_coruja.py -- meshy/modelo/CR_Coruja_meshy.glb meshy/modelo`
   - A envergadura fica em X e o bico em −Y.
   - A detecção da frente pela cauda confundiu as pontas das asas; por isso este m1 precisa de `CORUJA_INVERTER=1`.
   - **Escala de trabalho: altura de 0,62 u com os tufos (PROPOSTA).**
   - Gera `meshy/modelo/CR_Coruja_meshy_bruto.blend`, os renders `m1_A_*` e `m1_B_*` e `m1_metricas.json`.
4. **Prancha:** `python meshy/prancha_coruja.py meshy/modelo` gera `meshy/modelo/m1_prancha.png`.

### Medidas (m1 bruto)

| Medida | Valor |
|---|---|
| Envergadura | 1,48 u |
| Profundidade | 0,51 u |
| Altura | 0,62 u |
| Triângulos | **1,11 M** |
| Material | 1 |

### Comparação com a referência

**Fiel à referência:**
- tufos altos;
- disco facial claro com borda escura;
- olhos âmbar e bico curvo escuro;
- peito claro com estrias;
- asas e cauda barradas;
- pés emplumados com garras escuras.

**Diferenças:**
- as costas são um pouco mais escuras;
- a cauda está fechada e mais estreita (na referência ela aparece aberta em leque na vista de costas);
- as asas são superfícies inteiras, sem penas soltas, como esperado. O detalhe das penas fica na textura e na normal.

## Próximos passos (cada um com aprovação)

1. Malha de jogo LOW com UV e bake.
2. Rig de ave: asas com braço, antebraço, mão e penas primárias; cauda em leque; pescoço com giro amplo; pernas com garras.
3. Lotes de clipes:
   - pouso: repouso, giro de cabeça, ajeitar as penas;
   - voo: decolar, bater as asas, planar, pousar;
   - reação e derrota.

O Studio não foi testado.

## low_v1: malha de jogo (14/11, autorizada: "Sim, malha de jogo")

Script `meshy/meshy_low_coruja.py`, adaptado do javali. Comando:
`blender -b meshy/modelo/CR_Coruja_meshy_bruto.blend -P meshy/meshy_low_coruja.py -- low_v1 modo=voxel`

### Escolha do método

A malha bruta tem as asas formadas por centenas de lâminas de pena abertas: 74 mil bordas soltas e 895 ilhas. Testei dois caminhos, comparados em `low_v1/prancha_bruto_voxel_direto.png`:

| Método | Resultado |
|---|---|
| **Voxel 0,0035 e redução (escolhido)** | fecha as lâminas sem furar; mantém as pontas das primárias, os tufos e o rosto |
| Redução direta da malha original (descartada) | deixou rachaduras escuras nas asas e no rosto (fendas entre as lâminas) |

### Resultado

| Item | Valor |
|---|---|
| Total | **9.000 triângulos** |
| Cabeça | 3.042 tris (`M_Coruja_Cabeca`) |
| Corpo com as asas | 5.958 tris (`M_Coruja_Corpo`) |
| Regiões | asas 4,5k · cabeça 3,0k · corpo 1,5k |
| Texturas | 1024 (cor, normal, rugosidade) |
| Bake | raio curto (gaiola 0,6 cm, distância 2 cm), por causa das penas sobrepostas |

O orçamento é uma **PROPOSTA**.

## Rig piloto de ave (14/11, autorizado: "Sim, fazer o rig"): poses estáticas, sem clipes

Script `rig/rig_coruja.py`. Comando:
`blender -b low_v1/CR_Coruja_da_Floresta_LOW.blend -P rig/rig_coruja.py -- rig`

Saídas: `rig/CR_Coruja_Rig.blend`, `rig/rig_relatorio.json`, `rig/prova_*.png` e `rig/prancha_rig.png` (via `python rig/prancha_rig.py rig`).

### Ossos

São 30 ossos (29 deformam), com nomes do jogo e sem mandíbula (bico fechado).

| Grupo | Ossos |
|---|---|
| Tronco e cabeça | Raiz, Pelve, Coluna1, Coluna2, Pescoco, Pescoco2, Cabeca, TufoE/D |
| Asa (E/D) | OmbroAsa, BracoAsa (úmero), AntebracoAsa (secundárias), MaoAsa (pulso), Primarias |
| Cauda | Cauda, CaudaLequeE/D |
| Pernas (E/D) | Coxa, Tibia, Tarso, Dedos |

As juntas foram medidas na malha: bordo de ataque da asa, pés, tufos, bico e cauda.

### Pesos geométricos

As asas são lâminas finas, e o heat em proxy de voxel não é confiável nelas. Por isso todos os pesos são geométricos:
- **Asa:** pela posição ao longo da envergadura, com faixas suaves no ombro, cotovelo, pulso e base das primárias.
- **Tronco:** por distância aos ossos.
- **Cabeça:** rígida, com transição na garganta.
- **Tufos:** manuais.
- **Cauda:** pelo lado, para abrir o leque.
- **Pernas:** por segmento.

Resultado: no máximo 4 influências, nenhum vértice sem peso, costura 84/84.

### Asa fechada (pousada) por alvos

Script `rig/dobra_asas.py`, que grava `rig/dobra_asas.json`.

- **Problema:** a asa da malha não é plana (a parte interna cai cerca de 60°, a externa é quase horizontal). Com giros fixos, as penas ficavam para fora, a até 0,38 u do centro.
- **Solução:** cada osso aponta para um alvo de asa fechada (cotovelo atrás, pulso junto ao peito, mão para trás, primárias sobre a cauda). A rolagem de cada osso é buscada para minimizar pena para fora, pena entrando no tronco, pena abaixo do chão e pena acima do ombro (esta última na r2, porque um painel subia).
- **Resultado:** a asa fica a 0,21 u do centro (o corpo tem 0,15 u); o lado D é o espelho exato do E.
- **Atenção:** refazer `dobra_asas.py` se os pesos mudarem. Hoje, refazer o rig dá exatamente a mesma dobra.

### Provas

O chão é quadriculado.

| Pose | Resultado |
|---|---|
| Repouso (T) | ok |
| Asas fechadas | menor z 0,0 cm |
| Batida: asas no alto | no ar (+0,30 u) |
| Batida: asas embaixo | no ar |
| Cabeça virada 120° | ok |
| Cauda em leque (sobe e abre) | menor z 0,0 cm |

O detalhe da asa fechada (perfil, de cima, 3/4 por trás e frente) está em `rig/prova_asas_fechadas_detalhe.png`.

### Pendências

- As pontas das penas da asa fechada ficam um pouco recortadas (efeito do voxel).
- Os pesos vão ser revisados medindo os clipes, como no javali.
- O Studio não foi testado.

**14/11: rig piloto APROVADO pelo usuário** ("Sim, propor clipes"). Catálogo de clipes proposto (A pousada, B voo, C vida/caça, D defesa/derrota); aguarda escolha do primeiro lote.

## Lote A: pousada (14/11, autorizado: "Sim, lote A")

### Ferramentas

- **Gerador:** `rig/clipes_coruja.py`. Comando:
  `blender -b rig/CR_Coruja_Rig.blend -P rig/clipes_coruja.py -- rig/clipes_LA`
  - Pés por IK de 2 ossos (Tibia e Tarso, com o calcanhar dobrando para trás); os Dedos copiam o alvo.
  - Asas partem da ASA FECHADA (`dobra_asas.json`); as outras poses de asa vêm por interpolação pelo caminho curto.
  - Flexão de base de 1 cm (em pé, a perna da coruja fica quase reta).
  - Continuidade de sinal dos quaternions na exportação (q e −q).
- **Render:** `rig/render_coruja.py` (cópia do render do javali, câmeras fixas lateral, 3/4 e frente) e `rig/prancha_clipes.py`.

### Rig r2 (só pesos, no próprio `rig_coruja.py`)

- Pontos do pé no chão (z < 0,035) passam a ter 100% de Dedos; antes, um ponto com 92% de Tarso afundava ao flexionar.
- As laterais da cauda entram na regra da cauda; antes recebiam peso das pernas.
- A dobra das asas foi refeita e saiu idêntica.

### Clipes

O arquivo é `rig/clipes_LA/Coruja_Clipes_LA.blend` (10 ações), com JSON e manifesto. Todos os números são PROPOSTA.

| Clipe | Duração | Entrada → saída | O que faz |
|---|---|---|---|
| Repouso | 8 s, laço | laço | respiração (4×), peso trocando de pé, dois olhares rápidos, tufos e cauda |
| OlharE / OlharD | 2,4 s | Repouso q0 → Repouso q0 | a cabeça gira 150° em 0,32 s, ajusta, segura e volta |
| InclinarCabeca | 2,4 s | Repouso q0 → Repouso q0 | inclina 24° para um lado e 18° para o outro (escuta) |
| AjeitarPenas | 2,2 s | Repouso q0 → Repouso q0 | prepara, sacode o corpo (7 Hz amortecido) soltando as asas, cabeça sacode, assenta |
| EsticarAsaE / D | 3,2 s | Repouso q0 → Repouso q0 | o peso vai para a outra perna; estica a asa para trás e para baixo junto com a perna do mesmo lado; recolhe |
| VirarNoLugarE / D | laço de 2 s | laço | passinhos em arco; 60°/s gravado para o jogo girar o modelo |
| Saltitar | laço de 1 s | laço | 2 pulinhos de 0,09 u (0,18 u/s gravado); agacha, salta com as asas soltas, cauda ergue |

### QA

| Medida | Resultado |
|---|---|
| Emendas | 0,0° em todos |
| Erro de IK | 0 |
| Escorregão dos pés apoiados | 0 (Virar 0,01 cm; Saltitar 0,3 cm) |
| Maior giro entre quadros | ≤ 12,6°; Saltitar 25° (tíbia no salto) |
| Chão, checagem sobre a ação gravada | todos ≤ 0,02 cm abaixo do chão |

### Renders

Os renders ficam em `rig/clipes_LA/render/<rotulo>/`: GIF lateral, 3/4 e frente, prancha e medidas.

- **Saltitar:** 0,09 u por ciclo, deriva de 0,28 cm.
- **"estica_max" de ~7,4×:** compara com o repouso de ASAS ABERTAS do modelo, então inclui a própria dobra da asa. Não é o estiramento do movimento.
- **OlharE/D:** o giro de 150° estica o pescoço (cerca de 940 arestas acima de 2× contra o repouso aberto). Visualmente, a cabeça gira inteira e limpa.

### Pendências

- No Saltitar, o render mede a pele 0,7 cm abaixo do chão, enquanto a checagem sobre a ação gravada dá 0,02 cm. A divergência entre as duas medições ainda não foi resolvida.
- Falta medir o estiramento da pele em relação à pose pousada.
- A asa fechada tem pontas recortadas (efeito do voxel).
- O rig não tem pálpebras (a coruja não pisca).
- O Studio não foi testado.

## Correção: cabeça descolando ao virar (14/11, pedido "corrigir cabeça que descola ao virar")

### Causa confirmada: pivô

Os três ossos do pescoço giravam em eixos verticais 4 a 8 cm atrás do centro real da cabeça (y −0,07, −0,09 e −0,11, contra −0,147, medido por fatias da malha).

- **Deslocamento:** no OlharE e no OlharD (150° em 0,32 s), o centro da cabeça se deslocava **10,4 e 10,7 cm** na horizontal.
- **Estiramento:** a pele do pescoço esticava (726 arestas acima de 2× contra a pose POUSADA, máximo 6,9×), e a cabeça aparecia como um disco solto sobre o corpo.
- **Exportação descartada como causa:** a ação gravada e o JSON não tinham translação nos ossos do pescoço; o defeito estava no rig.
- **Quadros críticos:** q5 (meio do giro), q20 e q58 (extremo) e o retorno.

### Correção na fonte: rig r3 (`rig/r3/`)

Gerado por `CORUJA_R3=1 blender -b low_v1/CR_Coruja_da_Floresta_LOW.blend -P rig/rig_coruja.py -- rig/r3`. A base em `rig/CR_Coruja_Rig.blend` foi preservada.

- **Pivôs no eixo da cabeça:** Pescoco em (0; −0,125; 0,415), Pescoco2 em (0; −0,140; 0,455), Cabeca em (0; −0,147; 0,495).
- **Cabeça rígida:** acima de z 0,445, incluindo rosto, bico, olhos e a lateral do rosto.
- **Faixa de torção curta:** z 0,40 a 0,455, logo abaixo da borda do disco facial, indo de Coluna2 a Pescoco, Pescoco2 e Cabeca.
- **Tronco:** os pesos do tronco não incluem mais o pescoço.
- **Variantes testadas e descartadas:**
  - faixas de 14 cm ou mais altas, com o rosto rígido só na frente: um "cachecol" de penas torcidas cobria o rosto;
  - reduzir o giro para 100–120° com participação do tronco: o cachecol persistia, então **a amplitude de 150° foi preservada**.
- **Dobra das asas:** refeita sobre o r3, saiu **idêntica** à da base (`rig/r3/dobra_asas.json`).
- **Integridade:** costura 84/84, no máximo 4 influências, nenhum vértice sem peso.

### Olhar refinado (`clipes_coruja.py` com CORUJA_R3)

- O giro sai do repouso e desacelera curto em 0,30 s, passa 3% do alvo e assenta em 0,15 s.
- Segue uma pausa com um pequeno ajuste, e o retorno é suave em 0,5 s.
- A divisão do giro é Pescoco 10%, Pescoco2 25% e Cabeca 65%; o tronco compensa 3°.
- Os tufos reagem de forma discreta na parada e no retorno.

### Lote A r2 (`rig/clipes_LA_r2/Coruja_Clipes_LA_r2.blend`)

São os 10 clipes regerados com o r3, com JSON e manifesto. Comando:
`CORUJA_R3=1 CORUJA_DOBRA=rig/r3/dobra_asas.json CORUJA_ANIM_ARQ=Coruja_Clipes_LA_r2.blend blender -b rig/r3/CR_Coruja_Rig.blend -P rig/clipes_coruja.py -- rig/clipes_LA_r2`

### Métricas antes × depois

| Medida | Antes | Depois |
|---|---|---|
| Deslocamento do centro da cabeça, OlharE | 10,4 cm | **1,2 cm** |
| Deslocamento do centro da cabeça, OlharD | 10,7 cm | **0,7 cm** |
| Arestas do pescoço acima de 2× (pose pousada) | 726 | 586 |
| Estiramento máximo | 6,9× | 15× |
| Giro da Cabeca por quadro | rampa de 1,8° a 9,3° | saída de 12,9°, pico de 18,9°, parada curta |

- **Estiramento:** ficou concentrado na faixa curta, sob a borda do disco facial. Visualmente não há fresta.
- **Os 10 clipes:**

  | Medida | Resultado |
  |---|---|
  | Emendas | 0° |
  | Pés | sem escorregar (Saltitar 0,3 cm, como antes) |
  | Chão, sobre a ação gravada | ≤ 0,02 cm |
  | Translação no JSON dos ossos do pescoço | 0 |

### Evidências (`rig/clipes_LA_r2/comparacao/`)

- `antes_depois_OlharE|OlharD_<lado|34|frente>_fixo.gif`: antes em cima e depois embaixo, mesma câmera fixa, 30 qps.
- `prancha_OlharE|OlharD_antes_depois.png`: frente, perfil, 3/4 de trás e close da junção, nos quadros 0, 5, 20, 58 e 71, com a referência ao lado.
- `prancha_outros_antes_depois.png`: InclinarCabeca, AjeitarPenas e Repouso.
- Capturas em `antes/`, `depois/`, `antes_outros/` e `depois_outros/`.
- Scripts `rig/captura_cabeca.py` e `rig/comparar_olhar.py`.

### Pendências

- A divergência do Saltitar continua: o render mede a pele 0,7 cm abaixo do chão, e a checagem sobre a ação gravada mede 0,02 cm.
- O lote A r2 aguarda a revisão visual.

**14/11: lote A r2 APROVADO pelo usuário** ("Aprovar o lote A r2"). Base oficial da coruja: rig `rig/r3/` + clipes `rig/clipes_LA_r2/` (10 clipes de pousada). O rig da base e `clipes_LA/` ficam como histórico. Próximo: lote B (voo), só com autorização.

## Lote B: voo (14/11, autorizado: "Sim, lote B")

Base: rig r3 com a asa fechada do r3.

### Ferramentas

- **Módulo do lote B:** `rig/clipes_coruja_lb.py`, carregado com `CORUJA_LB=1`. Comando:
  `CORUJA_LB=1 CORUJA_R3=1 CORUJA_DOBRA=rig/r3/dobra_asas.json CORUJA_ANIM_ARQ=Coruja_Clipes_LB.blend blender -b rig/r3/CR_Coruja_Rig.blend -P rig/clipes_coruja.py -- rig/clipes_LB BaterAsas,Planar,PlanarCurvaE,PlanarCurvaD,BaterParaPlanar,PlanarParaBater,Decolar,Pousar`
- **Gerador (`clipes_coruja.py`):**
  - Perna recolhida em FK, interpolada osso a osso com a solução do IK do chão, sempre pelo caminho curto (`ext["pernas_fk"]`).
  - Emendas comparadas com o q0 do clipe de origem e do de destino.
  - Exporta `v_perfil` no JSON e na ação.
  - Interpolação de rotação pelo caminho curto também no alvo dos pés.
- **Tentativa descartada:** pés presos ao corpo por IK, com o alvo do joelho acompanhando o corpo. A tíbia girava no próprio eixo (97–133° num quadro), porque com a perna dobrada para trás esse alvo ficava alinhado com a perna.
- **Render:** `render_coruja.py` ganhou `CORUJA_SEM_AVANCO=1` (voo no lugar, para ler a batida) e `CORUJA_CAM_Z/CORUJA_CAM_D` (câmera para o voo).

### Voo

Todos os números são PROPOSTA.

| Elemento | Valor |
|---|---|
| Inclinação do corpo | 52° para a frente |
| Altura do centro do corpo no clipe | 0,55 u |
| Cabeça | nivelada, compensando o corpo |
| Tufos | deitados |
| Pés | recolhidos sob a cauda, com os dedos fechados |
| Batida | ciclo de 0,40 s: descida com a asa estendida, subida com o pulso dobrado; o corpo sobe na descida |
| Velocidade batendo | 3,0 u/s |
| Velocidade planando | 3,6 u/s |
| Curvas | inclinação lateral de 24° e giro de 40°/s |

### Clipes

O arquivo é `rig/clipes_LB/Coruja_Clipes_LB.blend` (8 ações), com JSON e manifesto.

| Clipe | Duração | Entrada → saída | O que faz |
|---|---|---|---|
| BaterAsas | 1,6 s (4 batidas), laço | laço | voo batido |
| Planar | 2,6 s, laço | laço | asa com diedro leve; as primárias ajustam devagar; leque da cauda aberto |
| PlanarCurvaE / D | 2,6 s, laço | laço | curva inclinada; a asa de dentro fica mais baixa e a cabeça entra na curva |
| BaterParaPlanar | 1,0 s | BaterAsas q0 → Planar q0 | a batida morre e o planeio entra |
| PlanarParaBater | 1,2 s | Planar q0 → BaterAsas q0 | fase inteira no fim |
| Decolar | 1,64 s | Repouso q0 → BaterAsas q0 | agacha, as asas abrem antes de sair do chão, explode, as pernas recolhem no ritmo da subida, 3 batidas mais amplas |
| Pousar | 1,9 s | Planar q0 → Repouso q0 | freio: o corpo fica em pé (8°), as asas sobem e avançam, a cauda abre; as pernas descem com as garras à frente; toque aos 0,95 s; absorve, duas batidas curtas de equilíbrio e fecha as asas |

### QA

| Medida | Resultado |
|---|---|
| Emendas (laço, entrada e saída) | 0°; Decolar na saída, 0,23° |
| Maior giro entre quadros, batida | ≤ 21° |
| Maior giro entre quadros, Decolar e Pousar | 26–31° |
| Pés apoiados | Decolar 0,5 cm no impulso; Pousar 0,04 cm |
| Chão, sobre a ação gravada | ≤ 0,01 cm abaixo |
| Voo no lugar | pele sempre ≥ 32 cm do chão |

### Renders

Os renders ficam em `rig/clipes_LB/render/<rotulo>/`, com GIF lateral, 3/4 e frente.

- **No lugar:** BaterAsas, Planar, PlanarCurvaE, PlanarCurvaD e as duas cadeias de transição.
- **Com deslocamento:** `cadeia_Decolar` (Repouso + Decolar + BaterAsas, 4,2 u) e `cadeia_Pousar` (Pousar + Repouso, 2,0 u).

### Pendências

- Asas e rig em voo estão sem medição de estiramento contra uma pose própria.
- A divergência de medição de chão do Saltitar (lote A) continua.
- O Studio não foi testado.

**15/11: lote B APROVADO pelo usuário** ("Aprovar e fazer C"). Base: rig r3 + `clipes_LA_r2` (A) + `clipes_LB` (B).

## Lote C: vida e caça (15/11, autorizado: "Aprovar e fazer C")

### Ferramentas

- **Módulo do lote C:** `rig/clipes_coruja_lc.py`, carregado com `CORUJA_LC=1` (traz o lote B junto). Comando:
  `CORUJA_LC=1 CORUJA_R3=1 CORUJA_DOBRA=rig/r3/dobra_asas.json CORUJA_ANIM_ARQ=Coruja_Clipes_LC.blend blender -b rig/r3/CR_Coruja_Rig.blend -P rig/clipes_coruja.py -- rig/clipes_LC Espreitar,Piar,MergulhoCaca,Comer,Adormecer,Dormindo,Despertar`
- **Gerador:** `ext["asa_q"]` dá orientação explícita por osso da asa, para encadear as poses fechada, aberta, de manto e de sono sem salto. As emendas também passam a comparar com "MantoFim" e "Dormindo q0".

### Clipes

O arquivo é `rig/clipes_LC/Coruja_Clipes_LC.blend` (7 ações), com JSON e manifesto. Comportamento, presa e coleta são PROPOSTA ou pendentes; não há objeto de presa.

| Clipe | Duração | Entrada → saída | O que faz |
|---|---|---|---|
| Espreitar | 3,4 s | Repouso → Repouso | agacha e dá 4 balanços rápidos de cabeça (sobe/desce e de lado), com o olhar fixo; tufos baixam |
| Piar | 2,6 s | Repouso → Repouso | inclina; dois pios (a garganta estica e o bico aponta para baixo); cauda sobe; as asas soltam de leve |
| MergulhoCaca | 1,55 s | Planar q0 → MantoFim | mergulha (o corpo vai a 74°), as asas recolhem pela metade, o corpo levanta e joga as garras, toca aos 0,95 s e cobre a presa com as asas em manto; o corpo se inclina pela coluna; velocidade de até 4,5 u/s, gravada em `v_perfil` |
| Comer | 3,4 s | MantoFim → Repouso q0 | 3 bicadas (bica, puxa e torce), engole, fecha as asas e volta |
| Adormecer | 1,8 s | Repouso → Dormindo q0 | último olhar; a cabeça afunda nos ombros, os tufos deitam e as asas soltam um pouco |
| Dormindo | 6 s, laço | laço | respiração lenta (2 por laço) |
| Despertar | 1,4 s | Dormindo q0 → Repouso | acorda e dá uma sacudidela curta |

### Correções medidas

- No Piar e no sono, a cauda descia até o chão; foi erguida.
- O manto com as asas baixas a 48° enfiava as primárias 9,6 cm no chão; com 22° elas encostam no chão.
- A bicada inclinava o tronco e levava a asa em manto 2,8 cm abaixo do chão; agora a bicada é só do pescoço.
- No Comer, o fechamento direto manto → fechada passava por baixo do chão (e um meio-fechamento também); agora a asa sobe para a horizontal e só então fecha, o mesmo caminho do Pousar.

### QA

| Medida | Resultado |
|---|---|
| Emendas | 0° em todos |
| Pés apoiados | sem escorregar (Mergulho 0,7 cm no toque) |
| Maior giro entre quadros | ≤ 12° (Mergulho 29°, a perna saindo do recolhido) |
| Chão, sobre a ação gravada | ≤ 0,02 cm abaixo em todos |

### Renders

Os renders ficam em `rig/clipes_LC/render/`:
- `cadeia_Espreitar`;
- `cadeia_Piar`;
- `cadeia_Mergulho` (MergulhoCaca + Comer + Repouso, 3,3 u, deriva de 1,2 cm no toque);
- `cadeia_Sono` (Repouso + Adormecer + Dormindo + Despertar + Repouso).

### Pendências

- O sono ficou sutil, como numa coruja pousada real; dá para afundar mais a cabeça se preferir.
- O rig não tem pálpebras, então ela dorme de olhos abertos.
- O Studio não foi testado.

## Pálpebras: rig r4 e lote C r2 (15/11)
Pedido do usuário: "ele dorme com os olhos fechados". O rig r3 não tinha pálpebras.
- `rig/palpebras.py` cria `rig/r4/CR_Coruja_Rig.blend` a partir do r3.
  - Cada olho ganha uma calota esférica (6×14, 154 tris) com centro 2 cm atrás do olho e raio igual à superfície + 4 mm.
  - A cor (UV) vem de um ponto claro do disco facial.
  - A calota fica unida à malha `Coruja_Cabeca`, com o mesmo material (3350 tris).
  - Ossos `PalpebraE` e `PalpebraD` são filhos de `Cabeca`.
  - No repouso a pálpebra fica ABERTA, recolhida 100° para dentro da cabeça. Assim os clipes que não animam esse osso (lotes A e B) continuam de olho aberto.
  - `rig/r4/palpebras.json` guarda o eixo e o ângulo de fechar (+100° no olho E, −100° no D).
  - Correções: normais refeitas (`recalc_face_normals`) para tirar o anel escuro no centro; folga de 4 mm para nenhum vértice aparecer com o olho aberto.
- `clipes_coruja_lc.py`, função `palpebras(r, f)`, ativada com env `CORUJA_PALPEBRAS=rig/r4/palpebras.json`:
  - Adormecer: duas piscadas pesadas (60% e 85%) e depois fecha;
  - Dormindo: olhos fechados no laço todo;
  - Despertar: abre devagar (0,10–0,45 s) e dá uma piscada em 0,62 s.
- Saída em `rig/clipes_LC_r2/` (o lote C r1 foi preservado).
  - Comando: `CORUJA_PALPEBRAS=rig/r4/palpebras.json CORUJA_LC=1 CORUJA_R3=1 CORUJA_DOBRA=rig/r3/dobra_asas.json CORUJA_ANIM_ARQ=Coruja_Clipes_LC.blend blender -b rig/r4/CR_Coruja_Rig.blend -P rig/clipes_coruja.py -- rig/clipes_LC_r2 <clipes>`.
- QA:
  - todas as emendas 0,0°;
  - os ossos do corpo têm os mesmos giros máximos do r1;
  - o maior giro passou a ser das pálpebras (piscada de 0,22 s);
  - chão ≥ −0,02 cm.
- Provas:
  - `rig/clipes_LC_r2/render/prancha_palpebras_close.png` (rosto de frente em Adormecer, Dormindo e Despertar);
  - os quadros em `render/palpebras/` e `render/cadeia_Sono/`.
- **Lote C r2 APROVADO pelo usuário em 15/11** (inclui as pálpebras do rig r4). A base atual da coruja passa a ser o rig r4 + `clipes_LC_r2`.

## Lote D: defesa e derrota, ESTUDO (15/11, pedido: "Fazer lote D")
Sem dano, hitbox ou regra de jogo. Como a coruja é derrotada, onde o corpo cai e se ela foge ou ameaça continuam **[PENDENTE]/[PROPOSTA]**.
- Módulo `rig/clipes_coruja_ld.py`, ativado com `CORUJA_LD=1`; carrega junto os lotes B e C e usa as pálpebras do rig r4. Comando:
  `CORUJA_PALPEBRAS=rig/r4/palpebras.json CORUJA_LD=1 CORUJA_R3=1 CORUJA_DOBRA=rig/r3/dobra_asas.json CORUJA_ANIM_ARQ=Coruja_Clipes_LD.blend blender -b rig/r4/CR_Coruja_Rig.blend -P rig/clipes_coruja.py -- rig/clipes_LD Ameaca,ReacaoImpacto,ReacaoImpactoVoo,FugaDecolando,Derrota,DerrotaEmVoo,Derrotada`

| Clipe | Duração | Emenda | O que faz |
|---|---|---|---|
| Ameaca | 3,0 s | Repouso q0 → Repouso q0 | asas em capa (abre pela horizontal e forma o arco), cauda em leque, tufos deitados, cabeça baixa balançando, dois avanços de silvo |
| ReacaoImpacto | 0,9 s | Repouso q0 → Repouso q0 | golpe de frente: tronco e cabeça vão para trás, asas saltam do corpo, piscada |
| ReacaoImpactoVoo | 0,8 s | BaterAsas q0 → BaterAsas q0 | batida desorganiza, peito levanta, inclina de lado, perde 5 cm de altura e recupera; velocidade cai 45% e volta |
| FugaDecolando | 1,43 s | Repouso q0 → BaterAsas q0 | sobressalto e o Decolar com a fase de chão comprimida pela metade (o tempo volta ao normal suavemente, sem estalo) |
| Derrota | 2,5 s | Repouso q0 → DerrotaFim | golpe, pernas cedem, tomba sobre o lado E girando na borda do pé, quique, cabeça apoia, olhos fecham |
| DerrotaEmVoo | 2,1 s | BaterAsas q0 → DerrotaFim | para de bater, sobe um pouco com o golpe, cai por gravidade (toca em 0,45 s) tombando para o lado; v_perfil vai a 0 |
| Derrotada | 1,0 s (laço parado) | DerrotaFim | deitada sobre o lado E, asa de cima solta sobre o corpo, pernas soltas, olhos fechados |

- Correções desta rodada:
  1. o pé do lado da queda entrava 8,9 cm no chão: o tombo passou a girar sobre a borda do pé E, com as pernas rígidas no corpo;
  2. a asa de baixo raspava a 70°: ganhou uma elevação de 2,6 cm no meio do tombo;
  3. a asa de cima em 0,38 ficava em pé como vela: caiu para 0,12;
  4. a cauda raspava no agachamento;
  5. a Ameaça girava 52° por quadro: a abertura passou de 0,45 s para 0,7 s;
  6. a emenda da Fuga e a translação da DerrotaEmVoo foram ajustadas.
- O script de chão `chao_coruja.py` (no scratchpad) comparava cm com m e escondia penetrações. Já está corrigido; os valores acima são da versão corrigida.
- QA:
  - todas as emendas 0,0°/0,0 cm;
  - chão: −0,02 cm nos clipes de pé; −0,26 cm num dedo no começo do tombo da Derrota; Derrotada +0,03 cm (asa de baixo encosta);
  - maior giro 46° (piscada), 43° no Tarso da Fuga (Decolar: 31°);
  - estica máx 7,44× em todos os clipes do r4, já no repouso (vem do rig r4, não do movimento; p99 ≤ 2,75).
- Renders em `rig/clipes_LD/render/`: pranchas, GIFs e `derrotada_vistas.png`.
- Studio não testado.
- **Lote D APROVADO pelo usuário em 15/11** ("Aprovar lote D"). Coruja completa no Blender: lotes A r2, B, C r2 e D sobre o rig r4. Studio não testado; sem commit.
- **Commit 211cf6d (15/11, autorizado: "Sim, commit")**: scripts, JSON dos clipes, manifestos e LEIA-ME (81 arquivos); sem .blend nem renders; push para origin/main em 15/11.
