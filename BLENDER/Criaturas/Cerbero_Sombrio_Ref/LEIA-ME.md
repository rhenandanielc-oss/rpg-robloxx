# Cérbero Sombrio (Ref): modelo novo via Meshy

Criatura domesticável das Terras Corrompidas. A ficha está em `DOCS/criaturas/cerbero-sombrio.md` e o pedido em `DOCS/pedidos/2026-11-17-cerbero-sombrio-meshy.md`. A referência aprovada para a geração é `DOCS/pedidos/2026-11-17-cerbero-sombrio-referencia.png`.

As versões antigas (`Blockouts/Cerbero_Sombrio/*`, V2 e V5) continuam intactas. A V5 tem 29,8 mil tris e rig de 40 ossos, mas está longe da referência. O esqueleto dela serve só de guia de nomes e cadeias para o rig novo.

## m1: Meshy (17/11/2026, autorizado: "aprovo", 36 créditos; saldo antes: 376, depois: ~340)

1. **Image to Image** (nano-banana-2, 6 créditos; tarefa 01a1ea4c-4e2d-7625-b252-58e581239c47).
   - Comando: `python -I meshy/meshy_cerbero.py imagem <ref> meshy`
   - Saídas em `meshy/imagem/cerbero_neutro_0..2.png`: frente (0), costas (1) e perfil (2).
   - **O perfil (2) veio quebrado e foi descartado:** está cortado e sem as cabeças.
2. **Multi-Image to 3D** com a frente e as costas (meshy-7.1, textura 4K PBR, 30 créditos; tarefa 01a1ea4c-e2d9-77b8-a375-9255cc7fe2a2).
   - Saídas em `meshy/modelo/`: `CR_Cerbero_meshy.glb/.fbx` e `T_meshy_*.png`.
3. **Conferência** (Blender em segundo plano, Workbench com textura). Gera `meshy/modelo/CR_Cerbero_meshy_bruto.blend`, os renders `m1_*.png` e `m1_prancha.png`.
   - A prancha mostra referência | 3/4 na linha de cima e frente | perfil na de baixo.

### Medidas (m1 bruto)
| Medida | Valor |
|---|---|
| Triângulos | **1,38 M** (1 malha) |
| Materiais | 1 (textura 4K: cor, normal, rugosidade, metal) |
| Caixa | 1,03 (X, largura) × 1,90 (Y, comprimento) × 1,55 (Z, altura) u |
| Frente | **−Y**, a mesma convenção dos outros modelos |
| Cernelha estimada | ~1,1–1,2 u. Para 14 studs de ombro, a escala seria ×12 e a altura total ~19 studs. **PROPOSTA**; o oficial é 12–16 de ombro |

### Comparação com a referência
**Fiel:**
- três cabeças, com a do meio mais alta e as laterais voltadas para fora;
- bocas fechadas com linha da mandíbula visível;
- olhos vermelhos;
- placas nos ombros e no dorso, com fissuras vermelhas só na textura;
- quatro patas plantadas, com garras;
- corpo musculoso e cauda peluda.

**Adaptações e riscos:**
- **Pescoços fundidos numa juba única**, sem vão entre eles. As cadeias do rig vão depender dos pesos; testar a deformação cedo.
- **Placas do dorso** vão da cernelha até o meio das costas, onde fica a sela. Reduzir ou afastar na malha de jogo, ou encaixar a sela por cima.
- **Ponta da cauda** em cone pontudo, um pouco estranho.
- **Boca sem interior.** É preciso construir boca, dentes e língua nas três cabeças, como foi feito no Leão e no Urso.
- A malha bruta é pesada demais para o Roblox. É preciso uma malha de jogo LOW, com cerca de 15–20 mil tris de proposta, e mapas assados.

## low_v2: malha de jogo (17/11, autorizada: "Aceito, seguir LOW")

- Script: `meshy/meshy_low_cerbero.py`, adaptado da coruja e rodado com 4 threads.
- Comando: `blender -b -t 4 meshy/modelo/CR_Cerbero_meshy_bruto.blend -P meshy/meshy_low_cerbero.py -- low_v2 wc=0.85 wp=0.92 fator=1.0`
- Processo: patas no chão (z=0); remesh voxel 0,005 (705 mil tris); 40 vértices soltos removidos; redução com pesos por região; Cabeças e Corpo separados; UV + bake Cycles (cor, normal, rugosidade) da malha bruta.
- `low_v1` (pesos 0,45/0,75 e fator 3) foi descartada: deixou 13,8 mil tris nas cabeças e só 4,2 mil no corpo, pouco para dobrar as pernas.

| MeshPart (`low_v2/CR_Cerbero_Sombrio_LOW.glb`) | Tris | Material | Texturas |
|---|---|---|---|
| Cerbero_Cabecas (3 cabeças + juba do pescoço) | 10.229 | M_Cerbero_Cabecas | 1024: cor, normal, rugosidade |
| Cerbero_Corpo | 7.771 | M_Cerbero_Corpo | 1024: cor, normal, rugosidade |
| **Total** | **18.000** | 2 | orçamento **PROPOSTA** |

- Medidas (escala de trabalho do Meshy): 1,90 de comprimento × 1,03 de largura × 1,54 de altura. Patas em z=0.
- Revisão: `low_v2/low_v2_prancha.png` mostra bruta × jogo em 3/4, a frente e o arame das cabeças. Os renders separados são `low_bruto_*` e `low_jogo_*`.
- A silhueta, as placas, os olhos e as fissuras foram mantidos. Não aparecem furos nem ilhas soltas.
- **Ainda não feito (próximas etapas):**
  - interior das três bocas;
  - placas do dorso na área da sela;
  - ponta da cauda em cone;
  - escala final (cernelha ~1,1 u → ×12,7 para 14 studs, PROPOSTA).

## low_v3d: bocas das três cabeças + cauda (17/11, autorizada: "Aprovo, seguir")

- Script: `meshy/meshy_low_cerbero_v3.py`. Comando:
  `blender -b -t 4 meshy/modelo/CR_Cerbero_meshy_bruto.blend -P meshy/meshy_low_cerbero_v3.py -- low_v3d`
- O método é o da boca do Urso v2, aplicado num referencial próprio de cada cabeça. Os eixos são frente f, lado s = f × z e altura z.
  - A ponta de cada focinho vem da sonda. Desde a v3b, o focinho é **recentrado**: o meio entre as bochechas, em 3 pontos, corrige T e f. A cabeça E estava 4 cm fora do eixo.
  - **Linha dos lábios:** foi lida nos renders laterais e refinada na malha. Em 13 pontos, o sulco é a menor largura lateral, e a linha é suavizada.
  - **Recorte:** fenda fina até a comissura, mais 2 cavidades elipsoides, num só booleano EXACT sobre a malha densa (voxel), antes da redução. Lábios e interior têm peso 0,35 na redução.
  - **Malha `Cerbero_Bocas`:** gengivas, 6 dentes por quadrante (incisivos, canino forte, pré-molares e molar) e língua.
    - Os dentes são encurtados ou recuados até ficarem escondidos com a boca fechada.
    - Pontos de gengiva visíveis com a boca fechada são retirados.
    - Atributos para o rig: `mand` (1 = mandíbula) e `cabeca` (0 = C, 1 = E, 2 = D).
  - **Interior da boca:** pintado à parte nas texturas das cabeças (escuro perto dos lábios, vermelho escuro no fundo, normal plana).
- **Cauda:** o cone da ponta foi puxado para dentro (raio 0,12) e suavizado (30 iterações). A ponta ficou arredondada.

| MeshPart (`low_v3d/CR_Cerbero_Sombrio_LOW.glb`) | Tris | Material | Texturas |
|---|---|---|---|
| Cerbero_Cabecas | 11.486 | M_Cerbero_Cabecas | 1024: cor, normal, rugosidade |
| Cerbero_Corpo | 6.514 | M_Cerbero_Corpo | 1024: cor, normal, rugosidade |
| Cerbero_Bocas (3 bocas, 84 peças) | 3.052 | M_Cerbero_Bocas | cor 256 |
| **Total** | **21.052** | 3 | orçamento **PROPOSTA** |

- **Revisão:**
  - `low_v3d/v3d_prancha_bocas.png`: E, C e D fechadas em cima e abertas a 26° embaixo. A abertura é um giro procedural só para revisão; não é rig, e a pose aberta não é salva.
  - `low_v3d/v3d_prancha_geral.png`: 3/4, perfil, cauda e o dorso visto de cima (a bruta).
- **Histórico das rodadas:**
  - **v3:** E deslocada; a cavidade furava a bochecha e a língua aparecia.
  - **v3b:** gengiva e incisivos apareciam na frente com a boca fechada.
  - **v3c:** sumiram os dentes de baixo de E e D, porque o filtro de visibilidade foi aplicado ao arco inteiro.
  - **v3d:** filtro só na gengiva.
  - As pastas v1, v3, v3b e v3c foram apagadas (~430 MB); os scripts reproduzem qualquer uma delas.
- **Pendências:**
  - **Placas do dorso NÃO alteradas.** São uma armadura única e lisa, da cernelha até a garupa (ver vista de cima). **DECIDIDO pelo usuário em 17/11: "Sela por cima".** A armadura fica como está, e a sela futura se encaixa sobre ela, atrás dos pescoços.
  - Com a boca fechada, ainda aparece de perto um ponto mínimo de dente (E) ou de vermelho (C) na frente.
  - Dentes sem subdivisão ficam facetados quando a boca abre bem de perto (troca por custo).
  - Escala final ainda não aplicada (cernelha ~1,1 u → ×12,7 para 14 studs, PROPOSTA).
  - Nada testado no Roblox.

## Rig (17/11, autorizado: "Sim, fazer o rig") — pasta `rig/`

- `rig/rig_cerbero.py` (adaptado de `Urso_Silvestre_Ref/v2/rig/rig_urso.py`):
  - Comando: `blender -b -t 4 ../low_v3d/CR_Cerbero_Sombrio_LOW.blend -P rig_cerbero.py -- .`
  - Gera `rig/CR_Cerbero_Rig.blend`.
- **Escala de jogo aplicada:** ×12,7, cernelha ~14 studs, altura total 19,6 e comprimento 24,1. É **PROPOSTA**; o oficial é 12–16 de ombro.
- **38 ossos, já com os nomes do jogo** (não renomear no Studio):
  - Raiz (no chão, não deforma), Pelve, Coluna1–3;
  - cadeias das cabeças: PescocoC1/C2, CabecaC, MandibulaC; PescocoE1/E2, CabecaE, MandibulaE; PescocoD1/D2, CabecaD, MandibulaD;
  - dianteiras: EscapulaE/D, BracoE/D, AntebracoE/D, MaoE/D, DedosE/D;
  - traseiras (digitigradas: joelho para a frente, jarrete para trás): CoxaE/D, CanelaE/D, PeE/D, DedosPeE/D;
  - cauda: Cauda1–3.
  - Convenção de lado: **E = −X**, igual às cabeças. A frente é −Y.
- **Pesos:**
  - heat num proxy fechado (voxel 0,15 stud), transferido para a pele;
  - crânio e mandíbula de uma cabeça não vazam para as outras (11 pesos removidos);
  - crânio × mandíbula pela mesma linha dos lábios da v3d, com transição suavizada atrás da comissura;
  - nuca (crânio/pescoço) suavizada;
  - barriga entre as patas passa para a coluna; sola segue Mao/Pe;
  - máximo de 4 influências por vértice;
  - peças da boca rígidas pelos atributos `mand`/`cabeca`.
- **Poses de TESTE** (`rig/poses_cerbero.py`, saída em `rig/poses_r2/`): deformação real pelo esqueleto. São estáticas e **não são clipes**.

| Pose | z mín. | esticamento p99 | arestas > 3× |
|---|---|---|---|
| repouso | −0,002 | 1,00 | 0 |
| 3 bocas abertas 32° | 0,000 | 2,09 | 79 (frente do lábio da cabeça C) |
| cabeças em alvos diferentes (E para fora e para cima, D baixa, C vira e morde) | 0,000 | 1,53 | 19 (mesmo ponto da C) |
| cabeças juntas à frente | 0,000 | 1,19 | 0 |
| passada longa | 0,000 | 1,16 | 0 |
| agachar (teste do sinal das dianteiras: esticou à frente) | 0,000 | 1,14 | 0 |
| torção do tronco | 0,000 | 1,09 | 0 |

- **Prancha:** `rig/poses_r2/rig_prancha.png` (a pasta `poses_r1` foi substituída pela r2). Mostra os ossos de lado e de frente em raio-x, as bocas C e E abertas, as cabeças em alvos diferentes e a passada.
- **Exportação** (`rig/exportar_cerbero.py`, adaptado do urso) → `rig/export/CR_Cerbero_Sombrio_Rig.glb` (9,6 MB), sem animações.
  - Reimportado no Blender: 38 ossos, todos com grupo.
  - 3 malhas skinned: Cabeças 11.486, Corpo 6.515 e Bocas 3.052 tris.
  - Até 4 influências por vértice; texturas 1024/256; caixa z 0,00–19,63.
  - Resultado: **`VALIDO`**. O Raiz ganhou o triângulo degenerado com 100% de peso.
- **Pendências:**
  - **Frente do lábio da cabeça C:** algumas arestas esticam (até 14×) ao abrir a boca. Nas imagens não aparece rasgo, mas é preciso conferir de frente e de perto.
  - Orelhas sem osso (rígidas no crânio).
  - IK/apoio das patas: fica para os clipes.
  - Sela: área prevista atrás dos pescoços, por cima da armadura. Não modelada.
  - Studio: importação e teste em Play não feitos.

### Rig r2 (17/11): frente do lábio da cabeça C
- **Problema:** na frente, a fenda da boca não cortou a malha da cabeça C. Ao abrir a boca, uma tira de pele (15 faces) ficava presa entre os lábios e esticava até 196×.
- **Correções em `rig_cerbero.py`:**
  - nos dois lábios, o lado (crânio ou mandíbula) é decidido também pela normal da superfície, porque a fenda é fina demais para usar só a altura;
  - as faces-ponte da zona dos lábios que ligam os dois lados são retiradas (15, todas na C). A cabeça passou de 11.486 para 11.471 tris.
- **Poses r2:** nenhuma aresta acima de 3× em nenhuma pose.
  - 3 bocas abertas: p99 1,08 e pior aresta 2,2×.
  - Cabeças em alvos diferentes: p99 1,32.
  - Vista de frente da boca C aberta: `poses_r2/labioC_frente_aberta.png`.
- **GLB reexportado:** `rig/export/CR_Cerbero_Sombrio_Rig.glb` (9,6 MB) → **`VALIDO`**.

## Piloto de animações (17/11, pedido `DOCS/pedidos/2026-11-17-cerbero-sombrio-animacoes.md`) — **ACEITO pelo usuário em 17/11 ("Aceito o piloto")**

- **Scripts:**
  - `rig/anim_cerbero.py` (adaptado do `anim_urso.py`): clipes procedurais NO LUGAR, com IK nas 4 patas, assados em FK e gravados em JSON (formato da ponte JSON → KeyframeSequence).
    - Comando: `blender -b -t 4 CR_Cerbero_Rig.blend -P anim_cerbero.py -- clipes_piloto`
  - `rig/render_piloto.py`: vídeos e quadros de contato; com `lobo`, só os quadros do Lobo Ártico, em leitura.
  - `rig/conferir_json.py`: reimportação dos JSON.
- **Saídas em `rig/clipes_piloto/`:**
  - `CR_Cerbero_Anim.blend`, com as ações `Cerbero_*` e marcadores da Mordida;
  - `Cerbero_<clipe>.json` (38 ossos, quaternion + translação local por quadro);
  - `manifesto_clipes.json` e `conferencia_json.txt`.
- **Referência de ritmo:** Lobo Ártico anim_v41 (Andar 36 q, Corrida 15 q). O Cérbero usa Andar 36 q e Corrida 16 q (mais pesado).
- **Peso de cão grande:**
  - o peito afunda logo após cada pouso dianteiro e as escápulas acompanham a pata;
  - as cabeças oscilam com atraso próprio (C 0, E +0,07, D −0,06 do ciclo) e amplitude menor nas laterais; o crânio compensa o pescoço e o olhar fica estável.

| Clipe | Quadros / duração | Loop | Velocidade (PARÂMETRO) | Erro IK máx | Escorregão máx | Pata z mín | Malha fora das patas z mín | Eventos |
|---|---|---|---|---|---|---|---|---|
| Repouso | 180 / 6,0 s | sim | 0 | 0 | 0 | −0,002 | 2,22 | — |
| Andar | 36 / 1,2 s | sim | 4,84 studs/s | 0,0003 | 0 | −0,002 | 1,99 | — |
| Corrida (galope) | 16 / 0,533 s | sim | 22,3 studs/s | 0,0009 | 0,008 stud/s | −0,002 | 1,77 | — |
| Mordida (cabeça C) | 34 / 1,1 s | não | 0 | 0 | 0 | −0,002 | 2,20 | antecipação 0,00 · bote 0,30 · **contato 0,42** · recuperação 0,55 · fim 1,10 s |

- **Descrição dos clipes:**
  - **Repouso:** respiração com período de 3 s e reações desencontradas. A E boceja (0,2–0,9 s), a C vira de leve (0,8–2,4 s), a E olha para fora (2,2–3,9 s) e a D fareja para baixo (3,8–5,6 s).
  - **Mordida:** um ataque básico; só a C morde. A E e a D se afastam um pouco, para as mandíbulas não colidirem, e reagem atrasadas.
- **Conferência por reimportação dos JSON:**
  - 38 ossos por clipe, nenhum faltando; diferença JSON × ação ≤ 0,0004 stud;
  - salto do último para o primeiro quadro: Repouso 0,009; Andar 0,44 e Corrida 0,78, equivalentes a um passo de quadro da pata em balanço (contínuo).
- **Revisão em `rig/revisao_piloto/`:**
  - vídeos a 30 fps em velocidade normal, com loops repetidos: `Cerbero_Repouso_34.mp4`, `Cerbero_Andar_lado/34.mp4`, `Cerbero_Corrida_lado/34.mp4`, `Cerbero_Mordida_cab/34.mp4`;
  - pranchas de quadros de contato: `prancha_andar_cerbero_x_lobo.png` e `prancha_corrida_cerbero_x_lobo.png` (Cérbero em cima, Lobo Ártico embaixo, mesmo enquadramento relativo), `prancha_mordida_repouso.png`.
- **Ajuste desta rodada:**
  - na r1, Andar (passada 4,2) e Corrida (5,4) passavam do alcance da perna: erro IK 0,10 e 0,39, e a pata escorregava até 11,8 studs/s;
  - na r2 as passadas ficaram em 3,6 e 4,4, e o corpo do galope desceu.
- **Pendências:**
  - Studio não testado;
  - desempenho com várias criaturas (PC e celular) não medido: 38 ossos e 21 mil tris por Cérbero;
  - aura e efeitos ficam para a etapa própria;
  - **divergência a sinalizar:** a REFERENCIAS_PODERES v6.2 lista vários elementos, mas a atualização oficial de 30/10 fixa um só. Nada elemental foi configurado;
  - orelhas rígidas;
  - velocidades são parâmetros técnicos.

## Lote 2A — locomoção e transições (17/11, após "Aceito o piloto") — **ACEITO em 17/11 ("Aceito, seguir 2B")**

- **Script:** mesmo `rig/anim_cerbero.py`; as funções novas estão no bloco "LOTE 2A".
  - Comando: `blender -b -t 4 CR_Cerbero_Rig.blend -P anim_cerbero.py -- clipes_L2A`
- **Base atual:** `rig/clipes_L2A/`, com os 10 clipes (os 4 do piloto mais os 6 novos), o `.blend` com as ações, os JSON, o manifesto e a conferência dos JSON.
  - `rig/clipes_piloto/` fica como histórico do piloto aceito.

| Clipe | Quadros / duração | Loop | Velocidade (PARÂMETRO) | Erro IK máx (no chão) | Escorregão máx | Pata z mín | Eventos |
|---|---|---|---|---|---|---|---|
| Trote (diagonal) | 18 / 0,60 s | sim | 11,9 studs/s | 0,0006 | 0 | −0,002 | — |
| Partida | 60 / 1,97 s | não | 0 → 22,3 (perfil) | 0,0009 | 0,027 stud/s | −0,002 | agachar 0 · primeira passada 0,37 · **encaixa na Corrida 1,97** |
| Freada | 46 / 1,50 s | não | 22,3 → 0 | 0,0008 | 0,032 stud/s | −0,002 | começa na Corrida 0 · parada 0,95 · fim em Repouso 1,50 |
| VirarE / VirarD (no lugar) | 36 / 1,2 s | sim | giro 30°/s | 0,0001 | 0 | −0,002 | — |
| Salto | 46 / 1,50 s | não | 0 | 0,0008 (no ar: 0,70, pernas soltas) | 0,022 stud/s | −0,002 | agachar 0 · decolagem 0,42 · ápice 0,70 · pouso 0,98 · recuperação 1,10 · fim 1,50 |

- **Encaixes conferidos nos JSON** (diferença de rotação < 0,1° em todos os ossos):
  - fim da Partida = quadro 0 da Corrida;
  - quadro 0 da Freada = quadro 0 da Corrida;
  - fim da Freada = quadro 0 do Repouso;
  - Salto começa e termina no Repouso.
- **Correção na Corrida do piloto:**
  - a guinada das cabeças e a boca entreaberta usavam meio período e não fechavam o loop (salto de até ~7° na mandíbula ao repetir);
  - agora usam o período da passada. Patas, tronco e QA não mudaram.
- **Salto:**
  - a subida da Raiz (arco de 2,6 studs) é VISUAL; a altura real do salto é da física do jogo, e os eventos marcam as fases;
  - no ar, as dianteiras se estendem à frente e as traseiras se recolhem; o erro de IK no ar não conta, porque as pernas estão soltas.
- **Viradas:** 30°/s, como o lobo (36° por ciclo de 1,2 s). Com 60°/s, as dianteiras, a ~6,5 studs do pivô, passavam do alcance da perna. A cabeça do lado da curva lidera.
- **Rodadas:**
  - **r1:** Trote (passada 3,8) com erro IK 0,11; Partida e Freada arrastavam a pata em balanço (1,6–1,9 stud/s); Viradas a 60°/s com erro 0,27.
  - **r2:** passada do Trote 3,2; pata que se move no mundo sempre sai do chão; giro 30°/s; no Salto, recolher a pata já conta como voo.
- **Revisão em `rig/revisao_L2A/`:**
  - vídeos MP4 a 30 fps: Trote, Corrida, Partida, Freada, VirarE/D (de cima e 3/4), Salto (de lado e 3/4);
  - pranchas Cérbero × Lobo Ártico: Trote, Partida (lobo: Arrancada), Freada (lobo: Frenagem);
  - `prancha_viradas_salto.png`: viradas de cima, 4 quadros cada, e o Salto.
- **Ainda não feito:**
  - lote 2B de vida: Alerta, Observar, Reação ao golpe, Deitar, Descanso e Levantar;
  - Studio;
  - desempenho com várias criaturas.

## Lote 2B — vida (17/11, após "Aceito, seguir 2B") — **ACEITO pelo usuário ("Aceito o 2B"); deitado em "esfinge" mantido**

- **Script:** mesmo `rig/anim_cerbero.py`, bloco "LOTE 2B".
  - Comando: `blender -b -t 4 CR_Cerbero_Rig.blend -P anim_cerbero.py -- clipes_L2B`
- **Base atual:** `rig/clipes_L2B/`, com os **16 clipes** (piloto + 2A + 2B), o `.blend` com as ações e marcadores, os JSON, o manifesto e a conferência.
  - Os 16 JSON foram reimportados e batem com as ações: 38 ossos, diferença ≤ 0,0005.
  - Piloto e 2A saem idênticos aos aceitos.

| Clipe | Quadros / duração | Loop | Erro IK máx | Escorregão máx | Pata z mín | Malha fora das patas z mín | Eventos |
|---|---|---|---|---|---|---|---|
| Alerta | 73 / 2,4 s | não (Repouso → Repouso) | 0 | 0 | −0,002 | 2,22 | mira 0,05 · segura 0,6 · volta 1,85 · fim 2,4 |
| Observar (Vigília orienta o olhar) | 133 / 4,4 s | não (Repouso → Repouso) | 0 | 0 | −0,002 | 2,21 | — |
| ReacaoGolpe (frente-esquerda) | 31 / 1,0 s | não | 0 | 0 | −0,002 | 2,13 | impacto 0 · recuperação 0,22 · fim 1,0 |
| Deitar | 79 / 2,6 s | não (Repouso → Descanso) | 0,001 | 0,26* | −0,08 | −0,14 | passo das dianteiras 0,15 · traseiras dobram 0,55 · peito no chão 2,25 · fim 2,6 |
| Descanso | 180 / 6,0 s | sim | 0,0004 | 0 | −0,08 | −0,18 | — |
| Levantar | 67 / 2,2 s | não (Descanso → Repouso) | 0,001 | 0,35* | −0,08 | −0,14 | dianteiras empurram 0 · traseiras sobem 0,55 · passo 1,25 · fim 2,2 |

\* A pata dianteira sobe 0,2 stud de propósito ao deitar (malha grossa da pata). A conferência conta essa subida lenta como movimento; não há arrasto horizontal.

- **Descrição dos clipes:**
  - **Alerta:** as três cabeças sobem e miram em sequência (C → D → E), com farejo curto, peso à frente e cauda alta.
  - **Observar:** E e D varrem setores opostos com tempos diferentes; a C fareja no meio.
  - **ReacaoGolpe:** tronco recua e torce; as cabeças sacodem com atraso (a E mais forte) e rosnam curto.
  - **Descanso:** respiração profunda; C erguida vigiando, E de queixo apoiado, D cochila e acorda no meio do ciclo; uma lambida curta da E.
- **Deitar e Levantar (as transições que a V5 mandava refazer):**
  - deitado esternal; o osso Mao/Pe gira em torno da ponta (o apoio não escorrega) e os dedos giram ao contrário, ficando planos no chão;
  - as dianteiras dão um passo à frente e saem do chão; as traseiras deitam o metatarso até o jarrete tocar o chão;
  - a descida do corpo é calibrada pela malha: **Raiz −5,30**, corpo a −0,10 do chão;
  - no Levantar, as dianteiras empurram primeiro e as traseiras depois.
- **Encaixes conferidos nos JSON** (< 0,1°): Repouso → Deitar → Descanso → Levantar → Repouso; Alerta, Observar e ReacaoGolpe começam e/ou terminam no Repouso.
- **Rodadas:**
  - **r1:** a calibração estava com a lógica invertida (corpo 2,8 abaixo do chão) e os dedos giravam junto (−0,6).
  - **r2:** a calibração passou a usar só o corpo; osso da pata a 66° (84° enterrava o antebraço grosso) com subida de 0,2.
  - **r3:** encaixe das cabeças Deitar/Levantar com a pose do Descanso; x lateral do osso da pata mantido (a pata dianteira girava 12° no 1º quadro).
- **Revisão em `rig/revisao_L2B/`:**
  - vídeos MP4: Alerta, Observar, ReacaoGolpe, Deitar (de lado e 3/4), Descanso, Levantar (de lado e 3/4);
  - `prancha_deitar_cerbero_x_lobo.png` e `prancha_levantar_cerbero_x_lobo.png` (lobo: Deitar e LevantarDeitado);
  - `prancha_vida.png`: linhas Alerta, Observar, ReacaoGolpe, Descanso + Descanso do lobo.
- **Diferença visível em relação ao lobo:** o Cérbero deita mais alto, em "esfinge", com as traseiras dobradas sob o corpo. O lobo deita mais baixo e de quadril de lado. Se preferir mais baixo e de lado, posso ajustar.
- **Pendências:**
  - montaria: lote separado, depois da sela e do encaixe adulto;
  - poderes: lote 3, com a divergência elemental a decidir;
  - Studio;
  - desempenho com várias criaturas.

## Lote 3 — poderes (v6.2) + ataques básicos em movimento (18/11) — **ACEITO pelo usuário ("Aceito o lote 3"); base atual = `rig/clipes_L3/` (26 clipes)**

- **Pedidos:** `lote 3 de animações de poderes` (colado pelo usuário) e o pedido do próprio usuário: "o Cérbero, em vez de atacar parado, possa atacar andando", para haver PvP de verdade.
- **Script:** mesmo `rig/anim_cerbero.py`, bloco "LOTE 3". O backup do gerador aceito no 2B ficou no scratchpad da sessão.
  - Comando: `blender -b -t 4 CR_Cerbero_Rig.blend -P anim_cerbero.py -- clipes_L3`
- **Versão própria:** `rig/clipes_L3/`, com os 16 aceitos (idênticos: diferença 0 nos JSON contra o L2B), os 10 novos e 7 prévias (só para render, sem JSON).
  - `rig/clipes_L2B/` continua intacto.

### Ataques em CAMADA (atacar andando, trotando ou correndo)
- O clipe de camada só mexe nos ossos do ataque (a "máscara"). No jogo, toca com prioridade **Action** por cima de Andar/Trote/Corrida, e as pernas e o tronco seguem a locomoção.
- O JSON da camada traz:
  - `ossos` só da máscara;
  - `camada: true`, `mascara` e `prioridade_sugerida: "Action"`;
  - `pais_peso0`: ossos pais que a ponte precisa criar com peso 0 para montar a árvore de Poses.
- **Integração no Studio PENDENTE:** o `AdaptadorUrso` lê osso por osso, mas é preciso conferir a árvore de Poses com peso 0 e a prioridade.

| Clipe (camada) | Máscara | Duração | Eventos |
|---|---|---|---|
| MordidaC / MordidaE / MordidaD | Pescoco{K}1-2, Cabeca{K}, Mandibula{K} (uma cabeça) | 0,8 s | contato 0,30 |
| GarraE / GarraD | Escapula, Braco, Antebraco, Mao, Dedos de um lado | 0,75 s | contato 0,32 |
| ChamasTriplices | as 3 cadeias de cabeça (12 ossos) | 1,6 s | preparo 0 · **disparo_E 0,45 · disparo_C 0,70 · disparo_D 0,95** · recuperação 1,10 |
| FuriaRugido | 3 cadeias | 1,6 s | rugido_C 0,15 · rugido_E 0,40 · rugido_D 0,65 · entra_furia 1,6 |
| FuriaLoop (loop) | 3 cadeias | 2,0 s | contato_C 0,30 · contato_E 0,95 · contato_D 1,55 |
| FuriaSaida | 3 cadeias | 0,8 s | fim 0,8 |

- **Garra:**
  - parte da pose da perna no Repouso (com IK) e desliga o IK só daquela perna durante o clipe;
  - a pata fica sempre um pouco erguida (r2: antes, as garras desciam 0,16 abaixo do chão, e 0,39 por cima do Trote).
- **Chamas Tríplices:**
  - as laterais giram para a frente para mirar; cada cabeça abre bem a boca só no seu disparo;
  - cadência E → C → D a cada **0,25 s** (referência, [A TESTAR]);
  - `eventos_info` diz a cabeça, o osso da boca e a mandíbula de cada disparo;
  - `ponto_boca_local_Cabeca` dá o ponto da boca no espaço local de cada osso Cabeca{K}, para o projétil e o VFX.
- **Fúria:** Rugido (uma cabeça por vez) → FuriaLoop (cabeças baixas rosnando, mordidas desencontradas) → FuriaSaida.
  - Encaixes conferidos: fim do Rugido = loop q0; o loop fecha; Saída q0 = loop q0. Diferenças < 0,01°.

### Investida Sombria (corpo inteiro, NO LUGAR)
- Compressão nos apoios (0–0,30 s) → impulso de 0,5 s (rampa de velocidade em 0,22 s; corpo estica; cabeças avançam baixas) → galope.
- O último quadro é o quadro 0 da Corrida (< 0,01°).
- O deslocamento (impulso de ~12 studs e +40% de velocidade por 4 s) é do jogo.
- Eventos: compressão 0 · impulso 0,30 · fim_impulso / passa_corrida 0,80 · encaixa_corrida 1,367.
- QA: IK 0,0009 e escorregão 0,25 stud/s (r1: 0,50; rampa alongada); pata z mín −0,002.

### QA geral (manifesto `clipes_L3/manifesto_clipes.json`)
- **Folga mínima entre as cabeças** (pontos de crânio, mandíbula e pescoço de cabeças diferentes): Repouso 3,07; clipes novos de 2,96 (Chamas) a 3,56.
  - Nenhum toque entre dentes, lábios ou pescoços de cabeças diferentes.
- **Prévias por cima da locomoção** (mesma medida do chão da base): Mordida C andando, Mordida E correndo, Garra E andando, Garra D trotando, Chamas paradas e andando, Fúria completa andando.
  - Escorregão 0–0,008 stud/s, IK ≤ 0,001, patas ≥ −0,002.
- **Reimportação dos 26 JSON:** diferença JSON × ação ≤ 0,0005; camadas com 4, 5 ou 12 ossos.

### Revisão em `rig/revisao_L3/`
- Vídeos MP4 a 30 fps: as 7 prévias, a Investida (de lado e 3/4) e as Chamas de frente.
- Pranchas:
  - `prancha_chamas.png`: referência + preparo e os 3 disparos;
  - `prancha_furia.png`: rugidos e contatos do loop, com a referência;
  - `prancha_investida.png`;
  - `prancha_ataques_basicos.png`: Mordidas C/E/D e Garras.

### Pendências
- **Elemento único e adoção do kit v6.2 no catálogo:** a decidir pelo usuário. Nada elemental foi configurado.
- Aura e efeitos do §5.9h: próxima etapa (os pontos de sincronização já estão nos eventos).
- Vigília das Três Cabeças e Pelagem Infernal: etapa das passivas.
- Studio: importar as camadas e conferir prioridade e peso 0 dos pais.
- Desempenho com várias criaturas (PC e celular) ainda não medido: 38 ossos, 21 mil tris, 26 clipes.
