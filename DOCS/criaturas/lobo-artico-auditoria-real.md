# Lobo Ártico: auditoria contra lobos reais (11/11/2026, sobre a `anim_v31`)

**Pedido:** auditar a pose neutra e as 12 ações contra lobos reais, usando filmagens e dados como padrão de movimento e `REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png` como referência de aparência. Foi só pesquisa e auditoria: **nenhuma ação foi alterada**, a `anim_v31/` ficou preservada e o Studio não foi acessado.

**Fontes:**
- Catálogo de filmagens e dados: `DOCS/criaturas/lobo-artico-referencias-reais.md` (pesquisa web, nada baixado).
- Medidas do jogo: `BLENDER/Criaturas/Lobo_Artico_Ref/auditoria_real_v32.py`, com resultado em `review/v32_lobo_real/auditoria_v31.json`.
- Quadros marcados do jogo: `review/v32_lobo_real/revisao/acao_<ação>.png` e `00_pose_neutra.png`.

**Escala usada nas comparações:**
- AO = altura da cernelha do rig = 4,94 stud. Um lobo real tem 66–81 cm na cernelha (IWC), o que dá **1 stud ≈ 0,146 m**.
- CC = focinho até a base da cauda = 9,20 stud.
- Velocidades e durações dos clipes são parâmetros técnicos, não regras de jogo.

## 1. Limites das evidências

- **Comparação lado a lado com o lobo real:** não foi montada.
  - Extrair quadros dos vídeos exigiria baixar material de terceiros (BBC, Nat Geo e outros). Isso precisa de autorização expressa e envolve direitos autorais.
  - Os links estão catalogados. A minutagem e o ângulo de câmera estão **a localizar**: as páginas não informam, e eu não assisti aos vídeos.
- **Dados cinemáticos de lobo:** não existe estudo cinemático publicado (fator de carga, cadência, ângulos).
  - Os números de lobo que temos são velocidade de trote (Mech 1994, Ellesmere: 8,7–10 km/h), porte (IWC), pegadas e registro direto (KORA, Elbroch) e postura (Heptner & Naumov; etograma do IWC).
  - Cadência e passada do trote são **estimativas alométricas** (Heglund & Taylor 1988, que usaram cão): cerca de 2,1 Hz e passada de cerca de 1,2 m (cerca de 1,6 AO).
  - O galope é transverso em velocidade menor e rotatório em velocidade alta (Biancardi & Minetti 2012, com *C. lupus*).
- **Cães, animações e imagens geradas:** excluídos como prova de biomecânica.

## 2. Pose neutra e Repouso

| Item | Jogo (v31) | Lobo real / referência | Tipo | Desvio | Correção proposta | Prioridade |
|---|---|---|---|---|---|---|
| Linha do dorso | Ossos da coluna sobem 11,9° da garupa à cernelha; a malha cai de 6,48 (juba, cernelha) para 5,09 (garupa) | Dorso quase nivelado, cernelha pouco mais alta (Heptner & Naumov) | rig + malha (juba) | Garupa visivelmente baixa no esqueleto; parte da inclinação é a juba, que também aparece na referência | Avaliar 4–6° a menos de queda em Quadril/Coluna1 numa etapa de rig | média (mexe no rig) |
| Cabeça | Base da cabeça 1,11 acima da cernelha; pescoço 22° acima da horizontal | Cabeça no nível do dorso; erguida só em alerta | animação (pose) | Repouso em postura de **alerta**, o que é aceitável; a referência mostra pescoço erguido | Manter no Repouso. Criar depois um "Repouso relaxado" com cabeça no nível do dorso | baixa |
| Cauda | Corda base→ponta 67° abaixo da horizontal; ponta a 0,75 do chão | Neutra T3 ≈ 45° abaixo do dorso (IWC); referência com cauda pendente e cheia | animação/rig | Pendurada mais vertical que o neutro | Erguer cerca de 15–20° (ver a ação 1) | média |
| Patas vistas de frente/trás | Colunas retas (v31); bitola dianteira 2,12 (0,43 AO ≈ 31 cm) e traseira 2,48 (0,50 AO ≈ 36 cm) | Peito estreito, patas sob o corpo; referência com patas pouco afastadas | rig (pose neutra) | Base larga e **assimétrica**: DE 1,16 × DD 0,95 e TE 1,43 × TD 1,05 (lado esquerdo 0,2–0,4 mais aberto) | Simetrizar e estreitar a base no rig (etapa própria) | média-alta (mexe no rig) |
| Peso | 4 patas no chão, oscilação vertical de 0,05 | – | – | Coerente | – | – |

## 3. As 12 ações

As referências citadas estão no catálogo; a minutagem está a localizar em todas.

| Ação | Referência real (catálogo) | Medidas do jogo | Desvio observado | Tipo | Correção proposta | Prioridade |
|---|---|---|---|---|---|---|
| **Andar** | Voyageurs Wolf Project (-euq6eQ_xKo); SloMo Ref arctic walk (XvBgmvLi3E8, origem a confirmar) | Sequência lateral TE→DE→TD→DD ✓; carga 0,62–0,65 ✓; 0,83 Hz; passada 3,6 = 0,73 AO; a traseira pousa 0,6 atrás da marca dianteira | Passo provavelmente **curto** em relação ao corpo; cabeça alta | animação | Alongar a passada (exige rever a velocidade técnica); abaixar um pouco a cabeça | média |
| **Trote** | Yukon (LhLq4B1rj8k, frontal com câmera lenta); Mech 1994 (8,7 km/h); Mech & Boitani ("uma pata à frente da outra") | Diagonal ✓; **registro direto ✓** (a traseira pousa a 0,01–0,11 da marca dianteira); 1,67 Hz (estimativa real ≈ 2,1); passada 4,0 = **0,81 AO** (real ≈ 1,6 AO); **cabeça 0,92–0,97 acima da cernelha**; cauda 67–74°; bitola 2,12/2,48 (sem linha única) | 1) cabeça alta (o lobo trota com a cabeça no nível do dorso); 2) passada com cerca de metade do comprimento real (passos "picados"); 3) patas afastadas, sem convergir para a linha do meio; 4) cauda vertical demais | animação (1, 2, 4); animação + rig (3) | 1+4: abaixar pescoço e cabeça e erguer a cauda (pequena, sem tocar no apoio); 2: passada maior com velocidade técnica proporcional; 3: convergir as patas no apoio | **alta** (1); alta (2, 3) |
| **Corrida** | BBC A Perfect Planet (UQKC5pZ0FG8); Planet Earth (kAHtFtqi_es, aéreo); Mech et al. 2015 (56–64 km/h) | Galope **rotatório** ✓ (TE→TD→DD→DE); 1 suspensão (27% dos quadros); 2,14 Hz; passada 9,5 = 1,9 AO ≈ 1,4 m; dorso dobra 3–11° | Parece galope **lento** (cânter): passada curta para um lobo em perseguição; cabeça 0,28–0,74 acima da cernelha (o real estende a cabeça à frente e baixa); a 2ª suspensão (estendida) não é comprovada em lobo | animação | Passada maior e cabeça estendida à frente; ver a velocidade técnica | média-alta |
| **Arrancada** | BBC (UQKC5pZ0FG8, bIQv3-0-InY): partida em caça | Antecipação com peso atrás e dianteiras em coluna ✓; impulso progressivo ✓; 18 quadros de suspensão | Herda cabeça alta e passada curta; prega/dobra do flanco no galope lento (malha) | animação + malha | Mesma correção da cabeça; malha à parte | média |
| **Frenagem** | BBC (bIQv3-0-InY, neve funda); Wild Yellowstone (yCn9H4A7ZVY) | Senta as traseiras e ergue a cabeça ✓; termina em Repouso | Coerente com a frenagem real (falta conferir o trecho) | – | Conferir o trecho quando houver minutagem | baixa |
| **VirarEsquerda / VirarDireita** | Caçadas BBC/Planet Earth (viradas bruscas); lacuna: virada lenta em perfil/topo | Passos de virada a partir do Repouso. **Corrigido em 11/11:** a cabeça **já conduz** a virada — guinada de 3° no q8, antes do corpo (que começa no q10–12), até 29° (pescoço 19°, peito 9°, cauda −8° para fora), voltando ao centro no fim. A auditoria inicial mediu só a altura da cabeça (constante) e concluiu errado. Plano da perna até 25° (pé colocado de lado, de propósito) | Antecipação curta (cerca de 0,1 s); a real não foi medida (sem minutagem) | animação | **Nenhuma por ora**: aumentar a antecipação sem referência real seria suposição; rever quando houver trecho real | baixa |
| **AndarParaTrote / TroteParaAndar** | Lacuna: transição limpa em perfil não localizada | Mistura suave das marchas ✓; pontas exatas ✓ | Herdam os desvios do Andar e do Trote | animação | Recebem automaticamente as correções das marchas | segue as marchas |
| **TroteParaCorrida / CorridaParaTrote** | Lacuna (idem) | Mistura ✓; v29 aprovada | Herdam o Trote e a Corrida | animação | idem | segue as marchas |
| **Repouso** | NatGeo (PCr65iD8Id4 e outros), referência de aparência | ver §2 | ver §2 | rig/animação | ver §2 | ver §2 |

**Conferência de frente da v31:**
- O arco e a torção artificiais foram eliminados: cotovelo 0 e torção ≤ 5° nas marchas.
- A passada **não ficou rígida em perfil**: carpo e dedos continuam dobrando (até 66–80°).
- Vista de frente, as patas ainda descem em colunas paralelas e afastadas. O lobo real converge as patas para a linha do meio no trote, e é isso que deixa o movimento "fino" visto de frente. É o item 3 do Trote.

**Separação por causa:**
- **rig:** base larga e assimétrica, queda da garupa.
- **animação:** cabeça, cauda, passada e viradas.
- **malha:** dobras do flanco e da axila no galope lento; pelo atravessando.
- **terreno:** a neve funda das filmagens muda a passada (patas mais altas, saltos). Não deve ser copiada para o chão firme do jogo e fica fora desta revisão.

## 4. Ações futuras: referências catalogadas e lacunas

- **Com referência:**
  - deitar e levantar (NatGeo PCr65iD8Id4);
  - uivo (áudio do NPS "Winter Wolves");
  - nadar (Yellowstone Twins 5Kiezfa3YVA);
  - brincar e play bow (Deby Dixon d4_-jn0g7Co; Wolf Hollow, cativeiro);
  - salto (California Wolf Center yRML08DNyWg, cativeiro, câmera lenta);
  - caça e mordida (BBC, Planet Earth; sequência de caça de MacNulty, Mech & Smith 2007);
  - sentar, sacudir e alongar (etograma do IWC, só descrição).
- **Lacunas:**
  - "mousing" (salto em arco sobre a neve) em lobo selvagem;
  - perfil puro em câmera lenta de trote e galope de lobo-ártico;
  - vista traseira do trote;
  - frontal parado em pé;
  - transição de marcha limpa em perfil.

## 5. Primeira correção proposta (pequena, maior impacto): "postura de viagem"

**O quê:** em movimento, abaixar o pescoço e a cabeça e erguer a cauda.
- **Trote:** cabeça no nível do dorso (hoje 0,95 acima) e cauda cerca de 45–50° abaixo da horizontal (hoje cerca de 70°).
- **Andar:** cerca de metade da correção.
- **Corrida:** cabeça estendida à frente e baixa.
- **Repouso:** não muda.

**Por que primeiro:** é a assinatura mais reconhecível do lobo trotando, visível em qualquer ângulo, e não toca nos apoios.

**Impacto antes de fazer:**
- **Rig:** nenhum. Mesmos 37 ossos, nomes, hierarquia, repouso, escala e pivô.
- **Ossos alterados:** só Pescoço1, Pescoço2, Cabeça e Cauda1–4, como ajuste de rotação por ação.
- **Apoios:** inalterados por construção, porque nenhum osso de perna muda. Mesmo assim, reauditar ≤ 0,03 nos 3 LODs.
- **Emendas:** o ajuste segue o peso da mistura já gravado em cada transição (`s_por_quadro`). Na Arrancada e na Frenagem segue a razão v/v_corrida; nas viradas e no Repouso fica 0. Pontas exatas.
- **Malha:** reconferir a garganta, a juba e a cauda × coxa esquerda, que são pontos já frágeis. Pescoço mais baixo pode dobrar mais a garganta, então é preciso medir.
- **Exportação:** as mesmas 12 ações, 3 GLBs, reimportação com auditoria.
- **Versão:** nova pasta `anim_v32/`; a `anim_v31/` fica preservada.

**Depois, em ordem sugerida** (atualizado 11/11: v32 postura e v33 patas aprovadas; viradas já conduzidas pela cabeça):
1. ~~Viradas conduzidas pela cabeça~~ — já existe (ver tabela).
2. Patas convergindo no trote e no galope (mexe no apoio: reauditar).
3. Passada mais longa com velocidade técnica proporcional (refaz marchas e transições).
4. Etapa de rig: base simétrica e mais estreita, queda da garupa.
