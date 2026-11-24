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

## Versionamento (18/11)
- Commit local `d8cb10a`: 83 arquivos, 5,7 MB (scripts, JSON dos clipes, manifestos, docs). `.blend`, `.glb`, `.fbx` e imagens ficam fora pelo `.gitignore`.
- **Push adiado pelo usuário.** O `main` local também tem 3 commits dos lobos, de outros chats; não enviar sem novo OK.

## Aura permanente A1 — prévia do visual (18/11) — aguarda aprovação

- Referência: REFERENCIAS_PODERES v6.2 §5.1 e §5.9h. Valores [A TESTAR].
- **Script:** `aura/aura_cerbero.py` (sobre `rig/clipes_L3/CR_Cerbero_Anim.blend`); prévia com `aura/render_aura.py`. Saída: `aura/CR_Cerbero_Aura_A1.blend` e `aura/previa_A1/`.
- **Método do Lobo Ártico r7/r8:**
  - as linhas são desenhadas como fitas na pose de repouso e **assadas na UV da pele**;
  - são duas imagens por malha (1024): `T_Cerbero_{Corpo,Cabecas}_AuraMascara` (onde há linha) e `_AuraDados` (R = posição ao longo da linha, G = cabeça/fase, B = cor);
  - na r1 as fitas soltas quebravam e sumiam no pelo; por isso foram trocadas.
- **Linhas:**
  - finas (0,8% da altura, ~0,16 stud), 16 trechos;
  - roxo-sombra `#8a2be2` no dorso, nas pernas traseiras, na cauda e nos lados dos pescoços;
  - vermelho-brasa `#ff4a1c` no flanco, nas pernas dianteiras e no alto dos pescoços;
  - **rosto limpo:** as linhas das cabeças param 1,3 stud atrás do osso Cabeca, na nuca (r3 e r4 corrigiram linhas que iam para a testa e os olhos).
- **Pulso:** lento, 1,8 s, da cabeça para a cauda. Cada cabeça tem a própria fase: corpo 0, C 0,31, E 0,62, D 0,93.
- **Olhos:** brasa discreta (vermelho da textura).
- **Pelagem Infernal:** borda muito fraca, quase imperceptível. Na r1 era forte demais e deixava o corpo laranja.
- **Revisão:** `aura/previa_A1/prancha_aura_A1.png` (3/4 e cabeças em 4 momentos do pulso) e vídeos `Aura_Repouso_cab.mp4`, `Aura_Andar_34.mp4`, `Aura_Andar_lado.mp4`, em luz noturna das Terras Corrompidas.
- **Pendências:**
  - os pescoços ficam com pouca linha, porque a juba esconde;
  - **no Roblox:** a fase própria de cada cabeça exige separar `Cerbero_Cabecas` em 3 MeshParts (EmissiveStrength por peça) ou aceitar um pulso único nas três cabeças. **Decisão a combinar.**
  - efeitos dos poderes sobre a aura (Chamas, Investida, Fúria e Vigília) ficam para a próxima etapa, já com os eventos marcados nos clipes.

## Aura de FOGO A2 (18/11) — pedido do usuário: "algo como fogo, como na referência" — aguarda direção

- **Referência do usuário:** `aura/ref/referencia_fogo_usuario_18-11.webp`, com chamas laranja e amarelas subindo da juba, dos pescoços, do dorso e da cauda, labaredas no pelo e olhos e bocas incandescentes.
  - Imagem com marca d'água do pngtree: só referência visual, **não** é arquivo do jogo.
  - **Diverge da v6.2 §5.1/§5.9h** (linhas discretas roxo/brasa; fora do corpo, só vento). Vale a direção do usuário. A A1 de linhas continua em `aura/CR_Cerbero_Aura_A1.blend`.
- **Script:** `aura/fogo_cerbero.py`; prévia com `aura/render_aura.py` (agora em vista Standard). Saída: `aura/CR_Cerbero_Fogo_A2.blend`, `aura/aura_A2.json`, `aura/previa_A2/`.
- **Pele:**
  - regiões de fogo (juba, peito, dorso, cauda e traseira das pernas) assadas na UV como máscara suave: `T_Cerbero_{Corpo,Cabecas}_FogoMascara`;
  - o shader acende os **fios do pelo** (luminância da textura) com cintilação subindo;
  - olhos incandescentes; gengiva e língua em brasa.
- **Chamas por cima:** 37 línguas de fogo (dois planos cruzados) presas aos ossos dos pescoços, das colunas e da cauda. São a prévia dos ParticleEmitters do Roblox; posições e ossos estão no `aura_A2.json`.
- **Rodadas:**
  - **r1:** cores lavadas e pele em manchas chapadas;
  - **r2:** fios do pelo, cores saturadas e chamas curvas;
  - **r3:** base das chamas suavizada e afundada na juba.
- **Revisão:** `aura/previa_A2/prancha_fogo_A2.png` (referência × 3/4 × cabeças) e vídeos `Aura_Andar_34.mp4`, `Aura_Andar_lado.mp4`, `Aura_Repouso_cab.mp4`.
- **Diferença para a referência:** lá o fogo cobre quase o corpo todo (juba inteira, peito, flancos, pernas e cauda em chamas, com tufos ondulados soltos). Aqui ele fica concentrado na juba, no dorso e na cauda.
  - Cobrir como a referência custa mais partículas, o que importa no celular (§5.10: ~150 partículas por efeito).
  - **Decisão do usuário:** manter ou aumentar a cobertura.

## Aura de FOGO A3 (18/11) — pedido "corrigir a aura de fogo A2" — **APROVADA pelo usuário ("Aprovo a A3"); é a aura permanente oficial do visual**

- **Base:** cópia de `aura/CR_Cerbero_Fogo_A2.blend` (A2 e A1 intactas), com as chamas da A2 retiradas.
- **Script:** `aura/fogo_A3.py`. Saída: `aura/CR_Cerbero_Fogo_A3.blend`, `aura/aura_A3.json`, `aura/previa_A3/`.
- **Pele (a cobertura vem primeiro do material):**
  - atributo de vértice `fogo` pelas regiões do rig: juba e nuca das 3 cabeças, parando atrás dos olhos; peito, ombros, dorso, flancos (barriga mais escura pela normal) e cauda; filetes só na face EXTERNA das pernas;
  - o shader acende línguas finas e altas no pelo, cintilando e subindo;
  - rampa: brasa na base → vermelho → laranja → amarelo-claro só no mais quente;
  - placas mais claras são atenuadas (r2), e os olhos ficam em brasa;
  - boca acesa por dentro (gengiva e língua, vindas da A2); os dentes continuam visíveis.
- **Chamas por cima:** só onde a silhueta pede. São 49 línguas ÚNICAS que giram no próprio eixo para olhar a câmera, como o ParticleEmitter do Roblox (sem o aspecto de planos cruzados):
  - juba 33, dorso 10 (nas bordas: a sela vai por cima), ombros 2, ponta da cauda 4;
  - pontas curvas e irregulares, cada uma com ritmo e altura próprios e raiz suave no pelo;
  - em Repouso sobem e ondulam; ao andar, inclinam para trás (rotação `rot_andar` em cada chama).
- **Rodadas:**
  - **r1:** pele em manchas de lava, placas acesas e chamas pequenas;
  - **r2:** línguas finas e altas, placas atenuadas e chamas maiores (ficaram com cara de vela);
  - **r3:** borda macia, pontas mais curvas e amarelo só no ponto mais quente.
- **Revisão:**
  - `aura/previa_A3/prancha_ref_A2_A3.png`: referência | A2 | A3, mesma câmera e mesma luz para A2 e A3, em 3/4 e nas cabeças;
  - vídeos `Aura_Repouso_34.mp4`, `Aura_Repouso_lado.mp4`, `Aura_Andar_34.mp4`, `Aura_Andar_lado.mp4`;
  - quadros `aura_{34,cab,lado}_q*.png`.
- **Estimativa para o Roblox** (de prévia, [A TESTAR]; **não é medição**):

| Plataforma | Emissores | Taxa por emissor | Vida | Partículas vivas |
|---|---|---|---|---|
| PC | 49 | 6/s | 0,8 s | ~235 |
| Celular (metade) | 25 | 4/s | 0,7 s | ~70 |

  - No PC, passa da meta da §5.10 (~150 por efeito). Opções: taxa 4/s (~157) ou ~32 emissores.
  - Desempenho real só medindo no Roblox.
- **Pendências:**
  - a placa do ombro ainda recebe parte do fogo;
  - as chamas do dorso são menores que na referência (por causa da sela);
  - quando os poderes ativarem (§5.9h), a aura de repouso precisa baixar de intensidade para eles continuarem legíveis.

## Efeitos dos PODERES sobre a aura A3 (18/11) — prévia no Blender — aguarda aprovação

- **Script:** `aura/fx_poderes.py`. Base: cópia de `aura/CR_Cerbero_Fogo_A3.blend` (A3 intacta). Saída: `aura/fx_poderes/` (`CR_Cerbero_FX_Poderes.blend`, `fx_poderes.json`, vídeos e quadros).
- **Sincronia:** pelos eventos dos clipes aceitos (`rig/clipes_L3/manifesto_clipes.json`).
- **Paleta:** a de fogo aprovada. O roxo da v6.2 §5.9h não entra, pela direção do usuário.
- **Valores:** [A TESTAR].
- **Controles novos:**
  - **Pele:** intensidade geral, reforço por cabeça (atributo `cab_id`), onda ao longo do corpo (atributo `u_corpo`), "esticar" para trás e olhos.
  - **Boca:** brilho por cabeça (atributo `cabeca`).
  - **Chamas:** brilho e tamanho por objeto.
  - **Objetos novos:** projéteis de fogo virados para a câmera, faixa de sombra com brasas no chão e 3 faixas de vento quente presas a Coluna2.

| Poder | Prévia (clipe) | O que acontece |
|---|---|---|
| **Chamas Tríplices** | Prev_Chamas_Repouso (2,4 s) | Cada cabeça acende antes do disparo (E 0,65 · C 0,90 · D 1,15 s); o fogo do pescoço dela reforça no disparo; a boca brilha (dentes visíveis); o projétil nasce 2,2 studs à frente da boca (`ponto_boca`) e anda 30 studs em 0,6 s |
| **Investida Sombria** | Investida → Corrida ×6 (4,6 s) | Impulso 0,30–0,80: as línguas da pele correm e esticam para trás, as chamas deitam para trás e alongam, o fogo fica mais forte e os olhos em brasa clara. Boost até 4,3 s com fogo forte. Faixa de sombra com brasas no chão (67 studs = 3 s a 22,3 studs/s), sumindo até 7,3 s. Vento quente rente ao corpo |
| **Fúria / Rugido Infernal** | Prev_Furia_Andar (4,8 s) | Cada cabeça explode em fogo no seu rugido (C 0,15 · E 0,40 · D 0,65 s); 3 ondas de fogo correm da cabeça à cauda; olhos em brasa clara; vento quente girando no tronco; fade de 3,3 a 4,8 s (último 1,5 s), voltando à aura de repouso |

- **Rodadas:**
  - **r1:** cabeças e peito estouravam em branco; o projétil nascia dentro da boca e aparecia furado;
  - **r2:** brilho limitado (×1,45), picos menores e o projétil nasce à frente da boca.
- **Revisão:**
  - `aura/fx_poderes/prancha_chamas.png`: repouso, E, C, D e volta, de frente e em 3/4;
  - `prancha_investida.png`: repouso, compressão, impulso, boost e fim, de lado e em 3/4;
  - `prancha_furia.png`: repouso, rugido C/E/D, fúria e fade;
  - vídeos `FX_*`.
- **Pendências:**
  - inimigos afetados pela Fúria (linhas cinza e apagadas): não há inimigo na prévia, fica para a integração;
  - Vigília (pupilas por 1 s) ainda não foi feita;
  - os projéteis andam em linha reta (a perseguição do alvo é do jogo);
  - no Roblox: projéteis e faixa viram partículas, Beam ou Decal; o vento vira Beams; desempenho a medir.

## Revisão r3 das três habilidades (18/11) — pedido "revisão das três habilidades no Blender" — aguarda aceite

- **Base de comparação:** a r2 (`aura/fx_poderes/`). A A3, os clipes aceitos (`rig/clipes_L3`, 26 clipes, intactos) e a r2 foram preservados.
- **Scripts:**
  - `aura/fx_poderes_r3.py` (cópia de revisão do `fx_poderes.py`), sobre `aura/CR_Cerbero_Fogo_A3.blend`. Saída em `aura/fx_poderes_r3/`.
  - Clipe novo `InvestidaR3` em `rig/anim_cerbero.py`, gerado em `rig/clipes_L3r/` (27 clipes; os 26 aceitos saem com diferença 0).

### Chamas Tríplices r3
- **Projétil novo:**
  - núcleo quente (laranja-amarelo, sem estourar);
  - corpo de chama girando (ruído em coordenadas giradas pelo tempo);
  - cauda curta presa à trajetória, que gira no próprio eixo para a câmera e dissipa;
  - impacto breve: anel que abre em 0,27 s.
- Nasce 2,2 studs à frente da boca de cada cabeça. Cadência de 0,25 s mantida. Velocidade de prévia: 40 studs/s [A TESTAR].
- **Alvos de prévia** (o projétil acerta a superfície do poste, raio de acerto 1,6):

| Tentativa | Cabeça | Alvo | Distância medida (lançamento → impacto) | Voo | Resultado |
|---|---|---|---|---|---|
| 1 | E | 10 studs | 9,33 | 0,23 s | acertou |
| 2 | C | 20 studs | 18,67 | 0,47 s | acertou |
| 3 | D | 30 studs (limite) | 29,33 | 0,73 s | acertou |

- **Curva — SIMULAÇÃO DE BLENDER** (v6.2: giro máximo de 180°/s, vida 2 s, até 30 studs). A trajetória teleguiada funcional fica para o Studio.

| Tentativa | Cabeça | Alvo | Resultado |
|---|---|---|---|
| 4 | C | móvel, atravessando a frente a 10 studs/s | **acertou** (0,47 s, 18,7 studs percorridos) |
| 5 | E | lateral a 75°, a 13 studs | **não alcança:** dissipou no limite de 30 studs |
| 6 | D | sem alvo | segue reto e dissipa a 30,7 studs (comportamento documentado) |

  - Na tentativa 5, com 180°/s a 40 studs/s, o raio de curva é de ~12,7 studs: um alvo a 75° e 13 studs fica dentro dessa curva. É um diagnóstico para calibrar giro e velocidade no Studio.
- **Revisão:**
  - `antes_depois_chamas.png`: referência | r2 | r3 de frente, e a câmera aberta com os 3 alvos;
  - `curva_simulacao.png`;
  - vídeos `FX_Chamas_r3_aberta.mp4`, `FX_Chamas_r3_cab.mp4`, `FX_Chamas_curva_SIMULACAO_aberta.mp4`.

### Fúria das Três Cabeças r3 (laranja → violeta)
- No rugido de cada cabeça (C 0,15 · E 0,40 · D 0,65 s), o fogo daquela cabeça e as chamas dela passam para violeta: `#1e0033` → `#6a1bd6` → `#a65cff` → núcleo `#e7d2ff`.
- O violeta corre pelo corpo atrás de uma frente que cada rugido empurra (36% → 70% → 106% do comprimento). As chamas do dorso e da cauda mudam quando a frente passa por elas.
- Na fúria sustentada as chamas ficam violeta e legíveis; as mordidas desencontradas e os focinhos continuam visíveis.
- No último 1,5 s (3,3 → 4,8 s), tudo volta gradualmente ao laranja.
- O violeta caracteriza o estado visual; a **decisão de elemento continua em aberto**.
- **Revisão:**
  - `antes_depois_furia.png`: referência | r2 (rugido, fúria, fade) | r3 (normal, ativação C, ativação D, sustentada, 3/4 sustentada, retorno, fim), na mesma luz;
  - vídeos `FX_Furia_r3_cab.mp4`, `FX_Furia_r3_34.mp4`.

### Investida Sombria r3 (clipe `InvestidaR3`, 1,467 s, 45 quadros)
- Patas fincando: dedos agarram o chão em 0,18 s.
- Peito comprimindo fundo entre as dianteiras (corpo −1,05).
- Cabeças baixando com atraso (C 0 · E 0,05 · D 0,09 s).
- Extensão marcada no impulso (0,40 → 0,90 s), pela garupa, com cabeças e cauda em linha.
- Recuperação da passada até o quadro 0 da Corrida.
- O deslocamento continua sendo do jogo (clipe NO LUGAR).
- **QA:** IK 0,0009; escorregão 0,30 stud/s (a aceita tinha 0,25); patas z ≥ −0,002; fim = Corrida q0 (< 0,01°); JSON reimportado e conferido.
- **Problemas encontrados e corrigidos:**
  - **r1:** a extensão pela coluna erguia a frente: IK 1,58 e escorregão de 11,7 stud/s;
  - **r1:** dedos fincados a 14° enterravam 0,26 no chão;
  - **r2:** escápulas e recuo do corpo ainda deixavam IK 1,03; a extensão passou para a garupa;
  - **r3:** com o impulso em 0,38 s a duração não fechava em quadro inteiro e havia um salto de 7° no encaixe (passou para 0,40 s);
  - **r3:** a mandíbula substituía a boca do galope e quebrava o encaixe; agora soma.
  - Interseções entre cabeças: nenhuma (folga mínima de 3,54).
- **Prévias:**
  - **saindo parado:** Repouso 0,5 s → InvestidaR3 → Corrida;
  - **saindo em movimento:** Trote → InvestidaR3 com mistura de 5 quadros → Corrida, com **mudança de direção simulada** de 35° entre 3,0 e 3,8 s. A faixa no chão e o vento giram junto.
  - **fogo:** acompanha a aceleração (as línguas esticam, as chamas deitam), faixa de sombra por 3 s e vento rente.
- **Revisão:**
  - `antes_depois_investida.png`: r2 | r3 parado (compressão, patas fincadas, extensão, passagem à corrida, encaixe) | r3 em movimento (trote, compressão, extensão, virada, fim do boost);
  - vídeos `FX_Investida_r3_parado_{lado,34}.mp4` e `FX_Investida_r3_movimento_{lado,34}.mp4`.

### Custo estimado dos VFX (prévia; NÃO é medição — medir no Roblox com várias criaturas)

| Efeito | No Roblox (proposta) | PC | Celular |
|---|---|---|---|
| Aura A3 (base) | máscara de emissão + ~49 emissores | ~235 partículas (acima da meta de 150: reduzir taxa ou emissores) | ~70 |
| Chamas Tríplices | 3 projéteis (ParticleEmitter + Trail curto) + 3 impactos (rajada de ~10) | ~3×20 + 30 por disparo, por 0,8 s | metade |
| Investida | faixa (Decal ou Beam com brasas, ~30 partículas) + 3 Beams de vento; aura reforçada | ~30 + aura | 15 + aura reduzida |
| Fúria | troca de cor (tint ou mistura de textura, sem partículas extras) + 3 Beams de vento | aura ×1,0–1,2 | igual à base |

- **Ainda exige teste:**
  - várias criaturas ao mesmo tempo (18 jogadores + companheiros);
  - custo do tint violeta no SurfaceAppearance;
  - Trails nos projéteis;
  - colisão e alcance real;
  - mira teleguiada;
  - inimigos afetados pela Fúria (linhas cinza);
  - Vigília.

## r4 — Rugido Infernal e projéteis (18/11, pedido "r4 do Rugido Infernal e dos projéteis") — AGUARDA REVISÃO

Etapa de Blender. Desempenho e trajetória funcional continuam pendentes no Roblox. A A3, a InvestidaR3, os clipes aceitos e os arquivos compartilhados ficaram intactos; os 27 clipes da `clipes_L3r` saem idênticos (diferença 0) em `rig/clipes_L3r4`.

### Fúria — Rugido separado das mordidas
- **Diagnóstico r3:** no `Prev_Furia_Andar` o loop de mordidas entrava em 1,6 s, depois do rugido, como planejado. Mas os três rugidos se sobrepunham (C 0,15 / E 0,40 / D 0,65 s, janelas de 0,75 s), a cabeça D ainda rugia enquanto o corpo já misturava para a postura de fúria (a partir de 1,05 s), a mandíbula chegava a 505°/s e o pescoço a 169°/s, lendo como bote e não como rugido.
- **Clipes novos** (o `FuriaRugido` aceito fica intacto):
  - `FuriaRugidoR4`: corpo inteiro, 2,9 s, 88 quadros. Apoios firmes (patas paradas), peito expandindo com inspiração em cada rugido, peso para trás e cauda erguida. Cada cabeça, uma por vez (C 0,10 → E 0,80 → D 1,50 s), ergue pescoço e focinho, abre a mandíbula a 56° com sustentação e fecha com controle. As laterais viram 12–14° para a frente para a boca ficar legível.
  - `FuriaRugidoR4Camada`: as mesmas cabeças em camada, para usar andando [PROPOSTA].
  - `Prev_FuriaR4`: Rugido → FuriaLoop (2 voltas, entra em 2,9 s) → FuriaSaida.
- **Eventos (s):**
  - C: rugido 0,26 / boca máxima 0,52 / fecha 0,90 / fechada 1,18;
  - E: rugido 0,96 / boca máxima 1,22 / fecha 1,60 / fechada 1,88;
  - D: rugido 1,66 / boca máxima 1,92 / fecha 2,30 / fechada 2,58;
  - entra na fúria em 2,90.
- **Conferência:**
  - IK 0, escorregão 0, patas a −0,002, folga entre cabeças 2,69;
  - emenda fim → FuriaLoop q0 e corpo → Repouso q0 = 0,0°; início → Repouso q0 = 0,34° (respiração das cabeças, coberta por mistura curta);
  - mandíbula 263–320°/s e pescoço 71–93°/s (r3: 505 e 169).
- **Corrigido no caminho:** antecipação e pulso do peito começavam antes de t=0 (4,6° no início); a abertura de 46° e o focinho a 13° liam pouco de frente (passaram a 56° e 18°); a câmera de perfil cortava as cabeças.
- **Som PROVISÓRIO** (sintetizado, não oficial), em `aura/som_rugido_r4.py` → `aura/fx_poderes_r4/som/`: três rugidos (C 68 Hz, E 82 Hz, D 58 Hz) com sopro de fogo, presos aos eventos `rugido_K`, e estalos nas 6 mordidas do loop.
- **Violeta:** cada cabeça passa de laranja a violeta entre `rugido_K` e `boca_max_K` (junto com o som); a onda corre pelo corpo durante a sustentação; volta gradual ao laranja no último 1,5 s (6,2 → 7,7). A boca acende em cada mordida do loop.
- **Vídeos:**
  - sem VFX: `rig/clipes_L3r4/render_r4/Cerbero_{FuriaRugidoR4,Prev_FuriaR4}_{cabf,perfilcab}.mp4` + `folha_rugido_r4.png`;
  - com VFX: `aura/fx_poderes_r4/FX_Furia_r4_{cab,perfilcab}.mp4`;
  - com VFX e som: `..._SOM.mp4` (áudio AAC confirmado).

### Chamas Tríplices — projétil com volume
- **Projétil r4** (o r3 continua no arquivo para comparação):
  - **Língua:** chama alongada no sentido do voo, de bordas rasgadas, que some quando fica de quina.
  - **Bola:** massa irregular por ruído de posição. A primeira versão, por ruído radial, lia como estrela.
  - **Camadas:** duas massas atrás da frente, para dar volume de frente.
  - **Núcleo:** pequeno e quente.
  - **Cauda:** 10 sopros que ficam na trajetória, sobem e envelhecem laranja → vermelho em 0,27 s, por isso seguem a curva.
- **Acúmulo e saída:** acúmulo na boca nos 9 quadros antes do disparo, seguindo a cabeça. A saída fica 1,3 stud à frente dos lábios, e a língua só se estende para trás conforme o projétil se afasta, sem atravessar o focinho.
- **Impacto:** 7 línguas verticais na superfície do alvo mais um estouro irregular, ~0,33 s, sem anel. **Dissipação** no limite: encolhe e avermelha em 6 quadros.
- **Testes** a 40 studs/s [A TESTAR], tempos de disparo da r3:
  - E @10 → acertou (9,33);
  - C @20 → acertou (20,0);
  - D @30 → acertou (29,33);
  - curva **SIMULAÇÃO DE BLENDER**: alvo móvel acertou (18,67 studs); lateral 75° a 13 studs não alcançou e dissipou a 30,67 (raio de curva ~12,7 studs); sem alvo, dissipou a 30,67.
- **Comparação** r3 × r4 (frente, perfil, 3/4; mesmo voo de 0,3 s, câmera a 9 studs, 50 mm, mesma luz): `antes_depois_chamas_r4.png`, `Comparacao_*.png`.
- **Vídeos:** `FX_Chamas_r4_{aberta,jogo,distante}.mp4` e `FX_Chamas_r4_curva_SIMULACAO_{aberta,jogo}.mp4`.

### Custo estimado (prévia, NÃO é medição)

| Efeito | PC | Celular |
|---|---|---|
| Chamas r4, pico de 3 projéteis | ~3 Trails + ~6 billboards + ~45 partículas (cauda 30/s, acúmulo, impactos) + PointLight curta | ~3 Trails + ~6 billboards + ~22 partículas (cauda 15/s, impacto com 4 línguas, sem luz) |
| Chamas r3 (referência) | ~12 partículas no pico | metade |
| Fúria r4 | troca de cor + 3 Beams de vento; som de 3 rugidos (~1 s cada) | igual |

### Pendências
- **Câmera de jogo:** de trás, o corpo esconde o disparo nos primeiros quadros; ver no Roblox com a câmera real.
- **Retorno ao laranja:** a mistura passa por um tom rosado.
- **Som:** é provisório.
- **Elemento único:** decisão em aberto.
- **Rugido em corpo inteiro (parado):** [PROPOSTA], a decidir (variante em camada disponível).

### r4b (18/11) — pedido do usuário: "Projeteis maiores, e esse som no rugido nao"
- **Som do rugido REPROVADO:**
  - os vídeos `FX_Furia_r4_*_SOM.mp4` e os `.wav` foram apagados;
  - `aura/som_rugido_r4.py` ficou marcado como reprovado;
  - a Fúria segue nos vídeos sem trilha (`FX_Furia_r4_{cab,perfilcab}.mp4`);
  - o som definitivo continua pendente.
- **Projétil maior:**
  - `aura/fx_poderes_r4b.py` (cópia da r4; a r4 fica intacta) aplica `ESC_PROJ = 1,7` [A TESTAR] em língua, massa, camadas, núcleo, sopros, acúmulo e impacto;
  - a saída passa para 2,2 studs à frente dos lábios, sem atravessar o focinho;
  - só o visual mudou: o raio de acerto, a velocidade e os tempos são os mesmos.
- **Testes iguais à r4:** 10, 20 e 30 studs acertaram; alvo móvel acertou; lateral 75° e sem alvo dissipam a 30,67 studs.
- **Saída:** `aura/fx_poderes_r4b/`, com prancha `antes_depois_chamas_r4b.png` e vídeos `FX_Chamas_r4_{aberta,jogo,distante}.mp4` e `FX_Chamas_r4_curva_SIMULACAO_{aberta,jogo}.mp4`.
- **Custo:** o número de partículas não muda, mas a área na tela cresce cerca de 2,9× (overdraw). No celular, medir no Roblox e, se pesar, reduzir a cauda para 15/s.

## Bola Infernal (18/11) — poder novo do usuário, SUBSTITUI as Chamas Tríplices — AGUARDA REVISÃO
- **Decisão do usuário (18/11):** "eles formam uma bola de fogo gigante que segue o alvo, procure fazer brilhante e real", "para substituir esse poder de projeteis". Nome **PROVISÓRIO**. Os arquivos das Chamas (r3, r4, r4b e o clipe `ChamasTriplices`) ficam guardados, sem uso previsto.
- **Clipe `BolaInfernal`:**
  - camada das cabeças, 2,2 s, 67 quadros; serve andando e correndo;
  - as três cabeças convergem (laterais 22–24°), abrem as bocas e sustentam a carga com esforço; dão um bote juntas no lançamento e recuam;
  - eventos: converge 0,0; carga_inicio 0,35; carga_max 1,20; disparo 1,30; recuperação 1,55; fim 2,2;
  - gerado em `rig/clipes_L3r5`; os 29 clipes anteriores saem idênticos;
  - prévias `Prev_Bola_Repouso` e `Prev_Bola_Andar`, ambas sem erro de IK nem escorregão; folga entre cabeças 2,93.
- **VFX:** `aura/fx_bola_infernal.py` sobre a A3, saída em `aura/fx_bola_infernal/`. Tudo em camadas reproduzíveis no Roblox:
  - **Carga:** um jato de fogo por boca alimenta a bola, que cresce à frente das três bocas sem tocar nos focinhos. Bocas, pele das cabeças e olhos acendem, e a luz laranja cresce.
  - **Bola:** raio visual de 3,4 studs, diâmetro ~6,8. Núcleo quente, massa em 3 camadas girando com gradiente de temperatura e cauda contínua de cometa.
  - **Voo:** línguas que se soltam da superfície, fumaça escura atrás e luz pontual laranja que ilumina a criatura e o chão.
  - **Impacto:** clarão, massa que abre, fogo no chão em anel, coluna de fumaça e marca de brasa que apaga em ~2 s.
  - Glare no compositor só na prévia; no Roblox, Bloom do Lighting.
- **Voo teleguiado — SIMULAÇÃO DE BLENDER.** Velocidade 26 studs/s, curva 150°/s, vida 2,5 s e alcance 40, tudo [A TESTAR]:
  - alvo parado a 28 studs: acertou (0,87 s de voo);
  - alvo móvel a 8 studs/s: acertou (0,80 s);
  - alvo lateral a 60°, 18 studs: acertou (0,67 s).
  - A perseguição real fica para o Studio.
- **Custo estimado (prévia, não é medição):**
  - **PC:** pico de ~45 partículas, 4 Billboards e 1 PointLight; explosão em rajada com Decal da marca.
  - **Celular:** ~20 partículas, 3 Billboards e luz sem sombra.
  - **Comparação:** custo parecido com os 3 projéteis da r4b, com uma luz a mais.
- **Vídeos:**
  - `FX_Bola_parado_{aberta,bola34,jogo,distante}.mp4`;
  - `FX_Bola_movel_SIMULACAO_{aberta,jogo}.mp4`;
  - `FX_Bola_lateral_SIMULACAO_aberta.mp4`;
  - sem VFX: `rig/clipes_L3r5/render_bola/Cerbero_Prev_Bola_{Repouso,Andar}_*.mp4`.
- **Prancha:** `prancha_bola_infernal.png`.
- **Pendências:**
  - nome definitivo;
  - números (dano, recarga, raio de acerto, velocidade);
  - se a bola atravessa obstáculos;
  - som;
  - câmera de jogo de trás (o corpo esconde a carga);
  - teste no Roblox.

## Bola Infernal r2 (18/11) — "mais brilhante, maior, as três cabeças rugindo formam uma bola gigante" — AGUARDA REVISÃO
- **Clipe `BolaInfernalR2`** (corpo inteiro, 4,3 s) + `BolaInfernalR2Camada` (só cabeças, para usar andando [PROPOSTA]) em `rig/clipes_L3r6/` (34 clipes; os 30 da L3r5 saem idênticos).
  - Eventos: ergue 0,0 · rugido 0,40 · carga 0,50 → 3,00 · preparo 3,00 · disparo 3,35 · recuperação 3,55.
  - Cabeças sobem e olham para a bola, bocas abertas a 58° rugindo com vibração, preparo, arremesso juntas para baixo/frente, boca fecha com controle.
  - QA: deslize 0, pata mín. −0,002, IK 0,036 (corpo inteiro; o tronco inclina no arremesso), folga entre cabeças 2,21 (menor que nos outros clipes, sem tocar).
- **Efeitos** `aura/fx_bola_infernal_r2.py` → `aura/fx_bola_infernal_r2/` (r1 intacta):
  - bola com raio 6,5 e massa 35% maior, formando ACIMA e à frente das cabeças;
  - crescimento rápido no começo, halo de brilho, PointLight ~6× mais forte, glare mais forte;
  - 48 riscos de energia convergindo em espiral; fluxo de fogo contínuo de cada boca até a bola;
  - explosão proporcional, sem anel escuro (a bola incha no ponto); fumaça do rastro mais atrás.
- **Voo SIMULADO** a 22 studs/s, curva 110°/s, vida 3,2 s, alcance 50 [A TESTAR]:
  - parado a 34 studs no chão: acertou em 1,67 s;
  - móvel a 8 studs/s: acertou em 2,10 s;
  - lateral a 60°, 24 studs: acertou em 1,43 s.
- A câmera de jogo (atrás) agora vê a carga, porque a bola fica acima das cabeças.
- **Custo estimado**, a medir no Roblox:
  - PC: ~70 partículas no pico (riscos 48 em ciclo + fluxo 30) + 5 Billboards + 1 luz;
  - celular: ~30 partículas, sem halo e luz sem sombra.
- **Pendências:**
  - de trás, no voo, a fumaça ainda escurece um pouco a bola;
  - nome, números, som e decisão entre corpo inteiro ou camada;
  - Studio.

## Bola Infernal r3 (19/11) — "maior, redondo e brilhante, com aspectos de fogo" — AGUARDA REVISÃO
- `aura/fx_bola_infernal_r3.py` → `aura/fx_bola_infernal_r3/` (r1/r2 intactas); clipe igual ao da r2 (`BolaInfernalR2`, rig/clipes_L3r6).
- **Esfera de verdade** de raio 10 (diâmetro ~20 studs):
  - superfície de fogo com ruído 4D em movimento, centro branco-amarelo e borda laranja-vermelha;
  - labaredas curtas na borda (3 Billboards), halo e PointLight 140 k (clarão 380 k);
  - SEM cauda de cometa: a bola fica redonda o tempo todo.
- **Voo SIMULADO** mais lento e pesado: 16 studs/s, curva 80°/s, vida 4,5 s, alcance 60 [A TESTAR].
  - parado a 45 studs: acertou em 2,80 s;
  - móvel a 8 studs/s: acertou em 3,73 s;
  - lateral a 60°, 32 studs: acertou em 2,33 s.
- **Roblox (proposta):** esfera = Part bola Neon/emissiva com textura de fogo + 3 Billboards de labareda + halo + PointLight; o resto igual à r2.
- **Render em PC compartilhado:** o EEVEE disputa a GPU com o Roblox Studio (~10 s/quadro e tela travando).
  - Modo `leve` no script: só os vídeos pedidos, 2 threads, prioridade Ociosa, 8 amostras, 480×338 e pausa de 0,6 s por quadro.
  - Resultado: 2 vídeos em ~7 min sem travar.

### r3 ACEITA pelo usuário (19/11) "porém mais rápido" → r3b — VELOCIDADE APROVADA 19/11
- `aura/fx_bola_infernal_r3b.py` → `aura/fx_bola_infernal_r3b/`. Visual = r3; voo 30 studs/s, curva 130°/s, vida 2,6 s, alcance 70 [A TESTAR].
- **Simulação:**
  - parado a 45 studs: acertou em 1,50 s (era 2,80);
  - móvel a 8 studs/s: acertou em 1,60 s (era 3,73);
  - lateral a 60°, 32 studs: acertou em 1,27 s (era 2,33).
- Carga (3,35 s até o disparo) sem mudança. Vídeos no modo leve.

### Nome oficial (19/11): **Sol Infernal**
- Decisão do usuário; "Bola Infernal" era provisório.
- Os arquivos e clipes mantêm os nomes técnicos `BolaInfernal*` / `fx_bola_infernal*` (renomear só na integração ao Studio, se for o caso).
- Números APROVADOS 19/11 (ver `DOCS/criaturas/cerbero-sombrio.md`): 1,8× + explosão 12 studs 1,0×, queimadura 3 s, 30 studs/s, curva 130°/s, alcance 50, acerto 8, recarga 14 s, energia 35.

## Teste em alvo — Investida r3 e Fúria r4 (19/11, pedido "teste em um alvo de criatura ou jogador") — AGUARDA REVISÃO
- `aura/fx_teste_alvo.py` → `aura/fx_teste_alvo/`. Cabeçalho da r4b, Investida da r3 e bloco da Fúria r4b, sem alterá-los. Render leve: 2 threads, prioridade Ociosa, 8 amostras, pausa entre quadros.
- **Investida contra jogador** (bloco de avatar R6 de ~5,5 studs, a 9 studs do focinho):
  - impulso de 12 studs em 0,5 s (0,9 → 1,4 s) e contato em 1,23 s, com dano 1,0× = 17;
  - alvo pequeno: o Cérbero ATRAVESSA, e o jogador é empurrado de lado e cai (visual; a física é do jogo);
  - depois segue a corrida com o rastro de sombra.
- **Fúria contra criatura de teste** (quadrúpede de blocos com a cabeça a 12,5 studs, na altura das bocas). Com um avatar de 5,5 studs as mordidas passavam por cima da cabeça dele.
  - Rugido: a partir de 0,52 s o alvo fica cinza/apagado e anda 15% mais devagar (16 → 13,6 studs/s); cada rugido renova os 4 s, e o efeito vai até 5,9 s.
  - 6 mordidas do FuriaLoop (3,2 a 6,45 s) de 20,4 cada (17 × 1,2), com barra ILUSTRATIVA de 200 → 77,6 PV.
- **Achado de design:** o Cérbero morde na altura de ~12,5 studs. Contra um jogador a pé as mordidas precisam de hitbox mais baixa ou de uma variante de mordida para baixo. Decisão do usuário.

## Investida r5 (19/11) — rastro novo e reação ao tamanho do alvo — APROVADA pelo usuário 20/11 ("Aprovo os dois")
Pedido do usuário "Investida Sombria — rastro e reação ao tamanho do alvo". Tudo é SIMULAÇÃO VISUAL no Blender: deslocamento, colisão, parada e dano ficam no jogo (servidor) e nada disso foi testado no Roblox.

### Clipes novos
Em `rig/clipes_L3r7` (35 clipes; os 33 anteriores saem idênticos; InvestidaR3 intacta).

- **`InvestidaSobre` (2,67 s, velocidade de prévia 22,3):** começa e termina no quadro 0 da Corrida e entra depois da InvestidaR3.
  - Dianteiras decolam em 0,42 s, dobram logo e ficam no alto; a frente sobe primeiro (nariz −18°).
  - Traseiras empurram em 0,67 s. Suspensão de 0,93 s com o corpo subindo 5 studs; o nariz desce no pouso.
  - Traseiras pousam em 1,60 s e dianteiras em 1,82 s.
  - QA: escorregão 0,008, patas z ≥ −0,002, folga entre cabeças 3,44.
  - IK 0,058 com a pata dianteira dobrada no ar (não aparece).
- **`InvestidaImpacto` (1,9 s):** termina no contato.
  - Freia em 0,3 s com absorção nas dianteiras (peito afunda, escápulas comprimem e o corpo segue 0,45 stud por inércia).
  - Preparo em 0,18 s. Mordidas C 0,46 · E 0,52 · D 0,58 s, segurando e sacudindo até 0,86 s.
  - Passo de ajuste das 4 patas e Repouso q0 no fim.
  - QA: IK 0,0009, escorregão 0,14, folga entre cabeças 2,91.

### Medidas reais
Métrica da prévia: cernelha = topo do dorso no meio do tronco (Coluna2), sem chamas; comprimento = bbox.

| | Cernelha | Comprimento | Largura | Altura total |
|---|---|---|---|---|
| Cérbero | 13,72 | 24,15 (bbox) | 13,05 | 19,19 (bbox) |
| Alvo com metade do porte | 6,86 (topo real 7,18) | 12,07 | 3,62 no caminho | — |
| Alvo maior (1,4×) | 19,21 | 33,81 | 10,14 | — |

### Resultados
- **Passagem por cima:**
  - pior folga corpo/alvo = **−0,18 stud**, no quadro 80: o pelo do peito raspa a borda de trás do alvo na decolagem;
  - dianteiras decolam a 5,1 studs do alvo e traseiras pousam a 8,3 studs dele;
  - golpe da passagem (flash) em 2,53 s.
- **Parada no alvo maior:**
  - bocas além da superfície: C 0,18 · E 0,03 · D 0,00 stud;
  - alturas das bocas: C 18,05 · E 16,04 · D 13,16 (três pontos diferentes do flanco);
  - o alvo balança de leve, sem ser empurrado.
- **Problemas encontrados e corrigidos (rodadas):**
  - rastro aparecendo à frente do Cérbero (a emissão não respeitava o nascimento);
  - QA de escorregão falso (o "no_ar" juntava apoios de antes e depois do salto);
  - traseira caindo de 4 studs no pouso;
  - medida da cernelha errada (8,6);
  - limite de "pata no chão" abaixo da altura do osso em repouso (0,57);
  - janela entre apoios curta (4,8 → 11,1 → 17,1 studs, com a suspensão mais longa);
  - canela traseira e antebraço dianteiro raspando o alvo (patamar de recolhimento, frente subindo antes, margem de pouso);
  - bocas desiguais: abaixar o pescoço desce a boca, não avança. C e E sobem e recuam até o plano da D, medido boca a boca.

### Rastro r5
A faixa antiga presa ao corpo foi desligada.
- Fita rente ao chão projetada no terreno por raio (+0,04 na normal), nascendo com o deslocamento real da prévia (UV v = instante de passagem).
- Bordas irregulares que se desfazem por trecho em 3 s [A TESTAR], com veios de fogo ondulados no sentido da passagem (referência do usuário) e brasas discretas.
- Línguas de fogo baixas em cada toque real das patas.
- Terreno ondulado testado em `Rastro_terreno_*`.
- **Custo estimado:**
  - PC: ~30 segmentos vivos (Decal/Beam), brasas 20/s e ~4 línguas;
  - celular: ~17 segmentos, brasas 8/s e línguas só nas dianteiras;
  - raycast por segmento.

### Pendências
- Proposta de dano em `DOCS/criaturas/cerbero-sombrio.md` [PROPOSTA].
- Reação a alvos entre metade e o tamanho do Cérbero (inclusive iguais) fica A DEFINIR pelo usuário.
- Confirmar a métrica de tamanho (cernelha + comprimento).
- A câmera de frente termina com o Cérbero muito perto.
- Salto com 0,93 s no ar e 5 studs de subida [A TESTAR na física do Roblox].
- Integração no Studio só com autorização (`DOCS/estado/studio-em-uso.md`).

## Vigília das Três Cabeças (passiva, Sombra) — prévia 20/11 — **APROVADA pelo usuário 20/11** ("Aprovo a passiva")
- Regra OFICIAL (v6.2 §4h/§5.9h): visão de 360°; enxerga criaturas INVISÍVEIS a até 15 studs; −50% no tempo de atordoamento. Visual pedido: as pupilas das três cabeças brilham por 1 s na detecção e o contorno da criatura aparece SÓ para o dono.
- `aura/fx_vigilia.py` → `aura/fx_vigilia/` (base fx_teste_alvo, intacto). Render leve.
- **Cena:** uma criatura em emboscada (blocos 12 × 5,5 studs) vem da frente-esquerda.
  - Ela cruza os 15 studs em 2,0 s, chega a 9 studs e recua; sai do raio em 4,57 s.
  - O Alerta (lote 2B) entra em 2,0 s só como orientação do olhar.
- **Pupilas:** 6 brilhos (billboards) presos aos ossos Cabeca C/E/D, acesos de 2,0 a 3,0 s, mais o realce de olhos da pele.
  - A posição foi achada por raio na geometria da cabeça: a textura só marca a BOCA em vermelho.
  - No Roblox: Billboard/Attachment por olho, sem PointLight.
- **Contorno (só o dono):** casca invertida laranja + preenchimento translúcido, de 2,0 a 4,57 s.
  - No Roblox: Highlight criado só no cliente do dono, com DepthMode AlwaysOnTop [PROPOSTA].
  - Os outros jogadores não veem nada (vídeo "outros").
- **Pendências:**
  - visual dos −50% de atordoamento (não pedido);
  - cor das pupilas e do contorno é PROPOSTA (paleta de fogo aprovada; violeta como alternativa de Sombra);
  - detecção e alcance são do servidor/cliente no Roblox (não testados).
- **20/11 — APROVADA pelo usuário** ("Aprovo a passiva"): prévia da Vigília como entregue (pupilas 1 s, contorno laranja-fogo só para o dono, nada para os outros). Cor laranja-fogo mantida. Simulação de Blender; detecção real [A TESTAR] no Roblox.

## Fúria roxa (20/11) — poderes em fogo roxo DURANTE a Fúria — **APROVADA pelo usuário 20/11**
- **Pedido do usuário:** "a Fúria muda a cor dos poderes para roxo, tanto do Sol Infernal quanto da Investida".
- **Decisões do usuário (20/11):**
  - o roxo vale só durante a Fúria (8 s); fora dela, os poderes ficam no laranja aprovado;
  - fogo roxo de núcleo branco-lilás e bordas roxo-escuro;
  - só a cor muda; os números aprovados continuam iguais;
  - o rastro da Investida fica roxo;
  - a aura do corpo segue o estado sustentado da Fúria r4 (violeta).
- **[PROPOSTA]:** a cor é decidida no lançamento. Um Sol Infernal lançado aos 7,9 s de Fúria voa roxo até o fim.
- **Script:** `aura/fx_furia_roxo.py`.
  - Os scripts aprovados (`fx_bola_infernal_r3b.py`, `fx_investida_r5.py`) **não foram alterados**.
  - O script executa uma cópia do fonte com um gancho que roda antes de cada render. O gancho faz três coisas:
    - troca a cor de emissão dos materiais do poder por uma rampa violeta guiada pela luminância da cor de fogo original. A forma e o brilho continuam os mesmos.
    - deixa violeta a luz da bola (`Luz_Bola`).
    - coloca pele, chamas da aura e bocas em violeta total.
- **Uso:** `-- <saida> poder=sol|investida [args do base] [vistas=...]`.
- **Saída:** `aura/fx_furia_roxo/`, com:
  - `prancha_furia_roxo.png`, com o laranja aprovado em cima e o roxo embaixo;
  - os vídeos `FX_Bola_parado_{jogo,aberta}.mp4`, `FX_Investida_sobre_34.mp4` e `FX_Investida_impacto_34tras.mp4`.
- **Materiais trocados:**
  - Sol Infernal: esfera, halo, massa, línguas, núcleo, faíscas e impacto;
  - Investida: `M_Rastro_r5` e as chamas do impacto.
- **Mantidos:** a fumaça (escura), os alvos e o vento quente da Investida (finos riscos laranja rente ao corpo; podem ficar roxos se o usuário quiser).
- **Correção durante a revisão:** no impacto, a aura voltava ao laranja, porque essa parte refaz as chaves do corpo. O gancho passou a rodar antes de cada render.
- **Observação:** o rastro roxo lê um pouco mais escuro que o laranja no chão escuro, o que é natural do roxo. Se o usuário pedir, dá para reforçar o brilho só do rastro.
- **Escopo:** é só uma simulação no Blender. No Roblox, seria uma variante de cor dos VFX, escolhida pelo servidor no lançamento. Não foi testada.
- **20/11 — APROVADA pelo usuário**, com uma correção pedida: "as partículas geradas no final da explosão do Sol ainda estão laranjas".
  - Causa: as brasas da marca queimada no chão (`M_Marca`) estavam fora da troca de cor.
  - Correção: `M_Marca` entrou na troca. Os vídeos do Sol foram refeitos.
  - A versão anterior está em `fx_furia_roxo/r1_marca_laranja/`. A comparação está em `fx_furia_roxo/marca_antes_depois.png`.
  - Rastro e vento quente ficaram como estão (o usuário não pediu ajuste). A regra "cor decidida no lançamento" continua [PROPOSTA].

## Studio — 1ª ida (20/11, autorizada: "quero levar ao Studio") — modelo + animações; AGUARDA REVISÃO do vídeo
- **Place:** `Documents/RPG_Roblox/BACKUPS/Cerbero-testes.rbxl` (local), confirmado pelo usuário. Antes de mexer: cópia `Cerbero-testes_ANTES_import_2026-11-20.rbxl`. Place SALVO no fim.
- **Limpeza (reversível):**
  - 6 dragões do Workspace e 4 pastas de animação do ReplicatedStorage (~3,4 M instâncias) foram para `ServerStorage.Dragoes_Fora_do_Teste`. Cada um guarda o atributo `OrigemPai`.
  - 12 scripts dos dragões foram desligados, com o atributo `DesligadoPeloTesteCerbero`.
  - Os backups antigos do ServerStorage (~1,1 M) continuam lá, sem mudança. O Play rodou sem travar.
- **Import 3D (usuário):** `rig/export/CR_Cerbero_Sombrio_Rig.glb` → `Workspace.Teste_Cerbero.Cerbero_Sombrio` (posição 0, 0, 60; Raiz no chão; partes ancoradas).
  - Peças: RootPart + 3 MeshParts (Cabeças e Corpo com SurfaceAppearance; Bocas sem SurfaceAppearance, como no GLB) + AnimationController.
  - 38 ossos; caixa 13,05 × 20,63 × 24,13 studs (igual ao Blender).
- **Convenção dos ossos MEDIDA:** `giro180y`, com 6 poses e 45 pontos (cabeça do osso em relação à Raiz).
  - 44 pontos com erro ≤ 0,002 stud. A exceção (0,45) é a MordidaE comparada sozinha: é um clipe de camada e não leva o pescoço.
  - Sem conversão, o erro chega a ~16 studs.
  - Atributo `Convencao = giro180y` gravado no modelo.
  - Frente do modelo no RootPart = −Z.
- **Pacote:** `studio/Cerbero_Piloto.rbxmx` (usuário: Insert from File) = 34 clipes de `rig/clipes_L3r7` + 25 listas de eventos + `AdaptadorCerbero` (cópia do adaptador do Crocodilo, só nomes trocados).
  - Gerado por `studio/gerar_rbxmx_cerbero.py` + `studio/empacotar_clipes_cerbero.py`; os eventos vêm do `manifesto_clipes.json`.
- **KFS:** 34 em `ServerStorage.Cerbero_Piloto.Animacoes`, com prioridades:
  - Movement: Repouso, Andar, Trote, Corrida, Descanso;
  - Action2: camadas (MordidaC/E/D, GarraE/D, BolaInfernalR2Camada, FuriaRugidoR4Camada);
  - Action: o resto.
  - Eventos viraram KeyframeMarkers.
- **Play (sem publicar; AnimationClipProvider):** `TestePlayCerbero.verificar` tocou os 34 clipes.
  - Duração igual à esperada em todos.
  - Pose tocada × esperada: posição 0,0000; ângulo ≤ 0,21° (≤ 2,05° nas investidas, que são rápidas: interpolação na amostra).
  - Mordidas C/E/D tocadas em camada SOBRE o Andar (atacar em movimento).
- **Vídeos:**
  - `studio/video_2011/Cerbero_Studio_parte1_locomocao_mordidas_furia.mp4` (Repouso, Andar, Trote, Corrida, 3 mordidas andando, Alerta, Fúria r4);
  - `..._parte2_sol_investida_descanso.mp4` (Sol Infernal, Investida impacto e por cima, Deitar, Descanso, Levantar);
  - `prancha_studio.png`.
  - A câmera fixa precisou de BindToRenderStep, porque o plugin devolvia o tipo de câmera para Custom.
- **Fora desta etapa (próximas):** aura A3, VFX dos poderes (Sol Infernal, Investida, Fúria roxa), Vigília, controle/montaria e IA. Também falta medir FPS com a aura.
- **Celular:** não testado. Animações publicadas: não (só ids temporários do Studio).

## Studio — aura de fogo A3 (20/11, autorizada: "Aprovo, seguir p/ aura") — AGUARDA REVISÃO do vídeo
- **Decisões do usuário (20/11):**
  - 49 chamas com taxa 4/s no PC (~157 partículas vivas); no celular, metade;
  - pele com máscara de emissão + cor de fogo;
  - pulso único nas 3 cabeças (separar as cabeças fica para depois).
- **Chamas:**
  - 49 Bones-âncora `AuraA3_NN_<zona>` sob os ossos do `aura_A3.json`; posições do Blender convertidas para o modelo como (−x, z, y) a partir da Raiz.
  - Cada âncora tem um ParticleEmitter "Chama":
    - textura `rbxasset://textures/particles/fire_main.dds`;
    - cor amarelo → laranja → vermelho → brasa;
    - LightEmission 0,75; Brightness 1,3;
    - vida 0,6–0,9 s, sobe com aceleração ~1,6× a altura da chama;
    - LockedToPart falso (inclina para trás ao andar);
    - atributo `TaxaPC`.
  - r1 estourava em branco na juba (sobreposição aditiva) → cor mais saturada e brilho menor.
  - As chamas do dorso ficam em boa parte sob as placas da armadura (como na A3, por causa da sela).
- **Pele:**
  - `aura/assar_aura_roblox.py` gera `T_Cerbero_{Corpo,Cabecas}_{Cor_Fogo,EmissivaMascara}.png` por rasterização das UVs com numpy (o bake do Cycles recusava o objeto em modo de fundo).
  - **r1** (`aura/roblox_A3/r1_cheia/`): acendia a região de fogo inteira → no Studio o corpo ficou laranja (cor) ou com um véu marrom (só máscara). REPROVADA pelo teste.
  - **r2:** línguas de fogo por ruído 3D na posição do vértice em studs (contínuo nas costuras), esticadas na vertical; placas da armadura atenuadas; tinta só nas línguas.
    - Prévia × A3: `aura/roblox_A3/previa_r2_x_A3.png` (`aura/previa_textura_roblox.py`).
- **Envio das texturas:** o plugin não lê IDs do Asset Manager, e o envio pela Open Cloud foi bloqueado pela proteção de permissões. Solução igual aos outros animais:
  - um GLB "portador" (`aura/glb_texturas_A3.py` → `roblox_A3/Cerbero_Texturas_A3_r2.glb`, 4 quadrados), importado pelo usuário com o Import 3D;
  - os IDs foram lidos dos MeshParts e os quadrados apagados.
  - IDs r2: Corpo cor `84850549410429`, máscara `104676656601430`; Cabeças cor `104169233442387`, máscara `112800307865115` (gravados como atributos na SurfaceAppearance, junto com `ColorMapOriginal`).
  - As imagens r1 e as do Bulk Import ficaram sem uso na conta do usuário.
- **Cliente:** `studio/AuraCerbero_Cliente.luau` (LocalScript em StarterPlayerScripts):
  - EmissiveStrength com pulso de 1,8 s + cintilação, 2,2–3,1 (medido em Play);
  - celular: 25 chamas;
  - LOD: acima de 90 studs, taxa pela metade; acima de 160, chamas desligadas.
  - Correção: com StreamingEnabled o Model chegava antes das peças e o registro ficava vazio → o script registra de novo enquanto faltar peça; o modelo ganhou `ModelStreamingMode = Atomic`.
- **Play:**
  - FPS do cliente 15,0 no Studio (o Studio deste PC roda ~15 fps; não é medição de jogo) com 49 emissores;
  - vídeo `studio/video_2011/Cerbero_Studio_aura_A3_dia_noite.mp4` (Repouso, Andar, Corrida, Fúria r4, depois noite) + `prancha_aura_studio.png`.
  - A noite foi só no Play (ClockTime 0,5); o place continua com 14,5.
- **Pendências:**
  - as chamas aparecem pouco à luz do dia (o brilho da pele domina);
  - celular: não testado (só a regra no script);
  - FPS real com várias criaturas: não medido;
  - as 3 cabeças pulsam juntas.
- **r3 (20/11) — pedido do usuário: "parecem mais pintura no corpo do que uma aura, quero mais fogo. Porém não tanto"** — AGUARDA REVISÃO
  - Backup do modelo r2: `ServerStorage.Cerbero_ANTES_AuraR3_2026-11-20`.
  - **Pele:** volta à cor ORIGINAL do pelo (a tinta laranja da r2 sai da ColorMap; o atributo `AuraA3_Cor` continua guardado). A máscara r2 fica só como brasa discreta: EmissiveStrength 1,6 ± 0,7 (pulso) ± 0,3 (cintilação), tinta (255,100,25).
  - **Chamas:**
    - tamanho ×1,4, Brightness 1,4, LightEmission 0,55;
    - com 2,2 e 0,9 estouravam em branco com o Bloom do place;
    - chamas do dorso e dos ombros subiram 1,4 stud para sair de baixo das placas.
  - **Brasas:** 8 emissores "Brasa" (`sparkles_main`, 4/s, vida 0,9–1,5 s) nos ossos Coluna1–3, Pelve, Pescoços C/E/D1 e Cauda2.
  - **Orçamento estimado:** ~157 + ~38 ≈ 195 partículas no PC; no celular, metade. O cliente agora trata "Brasa" como "Chama" (celular/LOD).
  - **Vídeo:** `studio/video_2011/Cerbero_Studio_aura_A3_r3_dia_noite.mp4` + `prancha_aura_r3_studio.png`.
  - Celular e FPS com várias criaturas: não medidos.
- **r4 (20/11) — pedido do usuário: "quero um brilho mais intenso"** — AGUARDA REVISÃO
  - **Chamas:** Brightness 2,6, LightEmission 0,8; a cor começa em laranja (255,150,40) em vez de amarelo-claro, para não estourar em branco com o Bloom.
  - **Brasas:** Brightness 5.
  - **Pele:** EmissiveStrength 2,4 ± 1,0 (pulso) ± 0,4.
  - **Vídeo:** `studio/video_2011/Cerbero_Studio_aura_A3_r4_dia_noite.mp4` + `prancha_aura_r4_studio.png`.
  - **Nota do teste:** se o script do cliente for desligado com a câmera longe, as chamas ficam desligadas pelo LOD. É só um artefato do ensaio.
- **r5 (20/11) — pedido do usuário: "não quero seu corpo alaranjado, somente o fogo"** — AGUARDA REVISÃO
  - **Pele:** cor ORIGINAL, sem máscara de emissão (EmissiveMaskContent vazio) e EmissiveStrength 0.
  - **Script do cliente:** BASE/AMPL/CINT = 0 (o pulso não acende mais a pele); continua cuidando do celular e do LOD das chamas e brasas.
  - **Fogo:** as 49 chamas e as 8 brasas da r4 continuam iguais.
  - As texturas assadas (r1/r2) e os IDs ficam guardados (atributos `AuraA3_Cor`/`AuraA3_Mascara`), sem uso.
  - **Evidência:** `studio/video_2011/aura_r5_dia.jpg`, `aura_r5_noite.jpg` (Play).
- **r6 (20/11) — pedido do usuário: "mais fogo"** — AGUARDA REVISÃO
  - **Chamas existentes:** taxa 4 → 6/s, tamanho ×1,3 (atributo `Escala_r6`).
  - **12 chamas novas** (`AuraExtra_NN_<osso>`, cópias da Chama r4): linha das costas e lados (Coluna1–3), quadril (Pelve) e base da cauda (Cauda1), acima do pelo e das placas.
  - **Total:** 61 chamas + 8 brasas = 69 emissores; estimativa ~330 partículas vivas no PC (acima da meta ~150 da §5.10, por pedido do usuário); celular metade (LOD do cliente).
  - **Pele:** continua natural, sem brilho (r5).
  - **FPS do cliente no Studio:** 59,8 com 69 emissores (uma criatura; Studio, não é medição de jogo).
  - **Evidência:** `studio/video_2011/aura_r6_dia.jpg`, `aura_r6_noite.jpg`, `Cerbero_Studio_aura_r6_dia_noite.mp4`.

## Aura de FOGO A4 (20/11, Blender) — pedido "fogo mais realista, brilhante e impactante" — APROVADA 20/11 (dorso r4 + vídeos); Roblox pendente
- **Base:** cópia de revisão de `aura/CR_Cerbero_Fogo_A3.blend`; a A3 aceita, o rig, os clipes e o Studio ficaram intactos.
- **Arquivos:**
  - script `aura/fogo_A4.py` → `aura/A4/CR_Cerbero_Fogo_A4.blend` + `aura/A4/aura_A4.json`;
  - render `aura/render_A4.py`, o mesmo script para a A3 e a A4: luz noite/dia, vistas 34/lado/frente/cab, modo `ultra`.
- **Leitura do pedido junto com a decisão anterior do usuário (r5: "corpo não alaranjado, somente o fogo"):**
  - a pintura da pele da A3 ficou ×0,03 (quase nula); o pelo continua escuro e visível entre as chamas;
  - a integração vem de 9 luzes pontuais locais presas aos ossos, com cintilação.
- **Distribuição:**
  - 120 pontos amostrados na superfície, pelo peso `fogo` da A3 × manchas de intensidade (ruído de baixa frequência);
  - distância mínima entre bases de 1,15 stud (0,9 nas pernas);
  - rosto limpo (só atrás dos olhos), sem chamas em mãos, pés e mandíbulas;
  - por zona: juba 46, dorso 20, pernas 16, peito 10, quadril 10, cauda 10, ombros 8.
  - Cada ponto tem a língua principal e uma "filha" (divisão), presas ao osso de maior peso: são 240 línguas.
- **Ciclo de vida no shader** (fase e período próprios, 0,75–1,35 s):
  - nasce, cresce e divide;
  - a base sobe um pouco no fim e a língua some;
  - a cada ciclo muda de posição lateral e de altura (ruído por ciclo), sem repetição sincronizada.
- **Movimento:**
  - turbulência e balanço largo, com pontas curvas e estrias;
  - correndo: inclinação para trás e estiramento pela propriedade de cena `inclina`, com a metade traseira atrasada 0,25 s (`inclina_atraso`).
- **Brilho:**
  - núcleo amarelo só no centro do terço de baixo; laranja vivo; vermelho na base;
  - força de emissão 5,5 × calor^1,2 (a A3 tinha 2,4);
  - view Standard.
- **Fúria:** a propriedade `violeta` troca a rampa das chamas e a cor das luzes, com o mesmo movimento.
- **Rodadas no Blender:**
  - r1: gotas de vela, duras;
  - r2: fiapos fracos demais;
  - r3: meio-termo; base firme (sobe 0,32 em vez de 0,62); pele ×0,03.
- **Evidências** (`aura/A4/`), renderizadas em modo ULTRALEVE porque o lote normal travou o PC do usuário:
  - pranchas: `prancha_ref_A3_A4_34.png` (referência × A3 × A4, noite e dia, mesma luz e câmera), `prancha_A3_A4_vistas_noite.png` (perfil, frente, cabeças, corrida) e `prancha_A4_furia.png`;
  - vídeos em `videos/` (15 qps, velocidade normal, 3 s): `A4_Repouso_noite_{34,cab}`, `A4_Corrida_noite_{34,cab}` e `A4_Repouso_furia_noite_34`;
  - quadros soltos em `comparacao/`; os q20/q81 e as vistas de dia além da 34 vieram do lote normal interrompido, em resolução maior.
- **Estimativa para o Roblox** [A TESTAR]:
  - PC: 120 emissores a 3/s, vida 0,9 s → ~324 partículas, mais 1 PointLight por criatura (não 9);
  - celular: 60 emissores a 2/s → ~96 partículas, sem luz;
  - a língua "filha" vira variação de tamanho e rotação da mesma partícula.
- **Pendências e limites:**
  - no perfil, as chamas do dorso ainda formam uma fileira parecida com espinhos; falta quebrar mais o espaçamento na linha das costas;
  - os núcleos da juba chegam perto do branco à noite;
  - os flancos e as pernas ainda têm pouca chama, comparados com a referência;
  - vídeos curtos (3 s) por causa do modo ultraleve;
  - desempenho real só medindo no Roblox (o Studio está com a aura r6, não com a A4).
- **A4 r4 (20/11) — pedido do usuário: "ajustar o dorso"** — APROVADA pelo usuário 20/11 ("Aprovo a r4")
  - **Mudanças no `fogo_A4.py`:**
    - peso 0,30 na crista das costas (normal para cima) → menos chamas em fila no topo, mais nos lados e flancos;
    - distância mínima sorteada de 1,1 a 2,0 stud;
    - alturas sorteadas ×0,6/0,85/1,0/1,25;
    - largura ×0,85–1,3;
    - cada chama do dorso pende para um lado;
    - a língua "filha" sai para qualquer lado.
  - A r3 está guardada em `aura/A4/r3_antes_dorso/` (script e quadros).
  - Como a semente aleatória mudou, os pontos das outras zonas também foram sorteados de novo, com as mesmas contagens.
  - **Evidência:** `aura/A4/prancha_dorso_r3_r4.png` (antes × depois: perfil, 3/4 e corrida, noite, mesma câmera); quadros em `aura/A4/r4_dorso/`; render ultraleve.
  - **Resultado:** a fileira de espinhos sumiu; o fogo do dorso agora tem alturas e inclinações variadas e chega aos flancos.
  - **Resto:** uma língua fina e vermelha aparece solta acima do dorso em um quadro (fim de ciclo, quando a base sobe). Os vídeos da A4 ainda são da r3.
  - **Vídeos r4 (20/11):** refeitos em `aura/A4/videos/` (5 vídeos, 3 s, 15 qps), os da r3 guardados em `aura/A4/r3_antes_dorso/videos/`. Render no modo `lento` (pedido do usuário: o mais leve possível): 1 thread, 1 núcleo, prioridade ociosa, 4 s de pausa por quadro, um vídeo por vez (`so=<clipe>:<vista>`). **APROVADOS pelo usuário 20/11.**

## Aura A4 no Studio (Cerbero-testes.rbxl) — 20/11 a 23/11 — r3 APROVADA pelo usuário 24/11
- **Decisões do usuário:** cerca de 90 chamas; inclinar pela velocidade; sem luzes; Fúria por atributo com teste.
- **Backups:** `ServerStorage.Cerbero_ANTES_A4_2026-11-20` (modelo r6) e `ServerStorage.AuraCerbero_Cliente_r6_2026-11-20` (script). Arquivo r6 em `studio/r6_antes_A4/`.
- **Chamas:** `studio/criar_aura_A4.luau` com os dados de `studio/aura_A4_sitios.lua`.
  - São 90 sítios da A4, escolhidos por zona para cobrir bem cada uma: juba 34, ombro 6, peito 8, dorso 15, quadril 8, cauda 7, perna 12. Cada chama é um ParticleEmitter "Chama" num Bone `AuraA4_NN_<zona>` filho do osso.
  - Textura `fire_main` com VelocityParallel e Squash negativo, para línguas finas. Cor: núcleo claro, depois laranja e vermelho. Brilho 2,4. Taxa 4/s.
  - Dorso e quadril com inclinação própria de ±22°. As 8 brasas foram mantidas.
  - **r2 (vista no Play):** chamas do corpo afastadas 1 stud do osso, porque sumiam dentro da malha; peito, ombro e perna ×1,4. Subir o ZOffset foi rejeitado: as chamas do outro lado apareciam através do corpo, com cara de pintura.
- **Script `AuraCerbero_Cliente` (A4):**
  - inclina as chamas para trás pela velocidade horizontal (atraso de 0,25 s, cheio a 30 studs/s, atualização a 15 Hz);
  - atributo `Furia` deixa chamas e brasas violeta;
  - celular com metade das chamas; LOD 90/160 studs; pele sem brilho.
- **Teste em Play (23/11):**
  - 98 emissores ligados, cerca de 290 partículas vivas (estimativa por taxa × vida);
  - Fúria violeta OK;
  - corrida a 26 studs/s com o fogo inclinado para trás OK;
  - sem erros do script da aura no console.
  - Evidências em `studio/video_2011/A4/` (`prancha_A4_studio.jpg`, `A4_corrida_studio_bruto.mp4`).
  - Celular e FPS não medidos. A foto da r6 na prancha não tem a mesma câmera.
- **Place local salvo** depois da r2.
- **r3 (23/11) — pedido do usuário: "o fogo não acompanha o corpo, fica para trás conforme o animal corre":**
  - Causa: as partículas ficavam soltas no mundo, então a criatura corria e deixava o fogo para trás; a inclinação forte (0,8) piorava.
  - Correção: chamas e brasas presas ao corpo (`LockedToPart = true`); inclinação reduzida para 0,35.
  - Play: corrida a 26 studs/s com o fogo acompanhando o corpo e pendendo de leve para trás. Vídeo `studio/video_2011/A4/A4r3_corrida_presa.mp4`. Place local salvo.
