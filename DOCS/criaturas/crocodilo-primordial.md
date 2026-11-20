# Crocodilo Primordial — ficha do subchat

Criatura **domesticável** do **Pântano Nebuloso**. Espécie-base **Crocodilo** (forma regional única: Crocodilo Primordial). A outra domesticável do bioma é o **Basilisco** (subchat próprio).

Fontes: `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO` (§0, §1, §2, Etapa 15.1, §10, §12, §13, §15, §18.2, §19.2) e `RPG_01` (só cita o Crocodilo no catálogo). A **ATUALIZAÇÃO OFICIAL de 30/10/2026** prevalece sobre o que vem depois no documento.

Regras de convivência: `DOCS/ORGANIZACAO-CHATS.md`. Studio um chat por vez (`DOCS/estado/studio-em-uso.md`).

Ficha criada em 03/11/2026, só com leitura. Nada foi alterado no Studio nem em `src/`.

## 1. Identidade

| Item | Valor | Status |
|---|---|---|
| Bioma / habitat | Pântano Nebuloso; margens, lagos e canais | [OFICIAL] |
| Anatomia | Crocodiliano **quadrúpede gigantesco**, corpo baixo, escamas grossas, cauda musculosa | [OFICIAL] |
| Locomoção | **Anfíbio**: caminha em terra normalmente e se desloca na água | [OFICIAL] |
| Especialidade | **Agarrões, emboscadas aquáticas (submersas) e combate próximo** | [OFICIAL] |
| Porte adulto | **5–7 studs até os ombros**; **~24–32 studs de comprimento total** (inclui cauda). Não confundir as duas medidas | [OFICIAL] |
| Estágios | Ovo, Bebê, Jovem, Pré-adulto, Adulto, Ancião (regra geral) | [OFICIAL] |
| Tamanho por estágio | — | [PENDENTE] |
| Montaria | A partir do **Adulto**, sela para locomoção em **terra E água** (ambas aprovadas na Etapa 15.1) | [OFICIAL] |
| Mergulho com cavaleiro | **Não definido** — nem aprovado nem proibido. Faltam respiração, câmera, profundidade, oxigênio/segurança e interações; diferenciar de Serpente/Leviatã (que têm mergulho montado aprovado) | [PENDENTE] |
| Capacete aquático do cavaleiro | **Ideia do usuário (17/11):** para montar no crocodilo, o cavaleiro deve usar um **capacete aquático**. Só registrado; o usuário vai detalhar depois (item, obtenção, respiração e se vale para toda montaria ou só para o mergulho). Nada implementado | [ANOTADO — A DEFINIR] |
| Velocidade relativa terra × água | — | [PENDENTE] |
| Padrões visuais | **Verde Pantanal**, **Marrom Aluvial**, **Negro de Rio**. Só cosméticos: não definem elemento nem raridade | [OFICIAL] |
| Cores exatas, evolução estética por estágio, adornos por raridade | — | [PENDENTE] |
| Pistas de aproximação | Lentidão em terra seca; trilhas de bolhas e ondulações que revelam a aproximação | [PROPOSTA] |
| Painel de referência | `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/03-basilisco-crocodilo-escorpiao-lagarto.png` | referência visual |

Papel ecológico em relação aos vizinhos:
- **[OFICIAL]** Leviatã = ofensiva oceânica; Serpente Marinha = perseguição/constrição aquática; **Crocodilo = emboscada de margens e rios** (agarrões, emboscada anfíbia, com patas).
- **[PROPOSTA]** Basilisco domina terra/água rasa; Crocodilo tende a dominar canais e água mais profunda. Precisa de margem e cobertura; fraco contra alvos aéreos; pouca perseguição prolongada em terra seca e aberta.

## 2. Elemento e habilidades

### Kit oficial — **[OFICIAL — decisão do usuário 20/11/2026]**
- **Elemento único: ÁGUA.**
  - Pela matriz oficial (RPG_02 §3), é forte contra Terra e Sombra e fraco contra Natureza e Luz.
- **Ativas (4):**
  1. Mordida de Agarrão;
  2. Giro de Emboscada;
  3. Submersão;
  4. Cauda de Maré.
  - A **Mordida esmagadora** é a finalização própria do crocodilo e fica **fora dos slots**, como os ataques básicos.
- **Passivas (2):** Escamas Grossas e Sentido de Vibração.
- **Visual do elemento:** **natural, sem brilho**: água e lama de verdade (respingos, ondas, espuma, gotas), sem energia mágica brilhante.
- **Números:** continuam **PROVISÓRIOS**, para balancear depois.
- O que cada poder já faz está descrito no protótipo, abaixo e na seção 5.
- **[OFICIAL — decisão do usuário 20/11/2026, depois do vídeo do kit Água]**
  - **"Giro de Emboscada" passa a ser só "Emboscada", sem giro** ("não quero que o crocodilo gire"). É um **bote saltando**: o crocodilo explode para fora da água com o corpo reto e a boca aberta, faz um salto curto e baixo para a frente, cai com peso e morde/derruba quem estiver na frente.
  - **Cauda de Maré com onda real:** o golpe da cauda levanta uma onda que se espalha pela água; quem ela alcança leva dano e é empurrado para fora. Quem a cauda toca direto leva o golpe cheio.
  - **Em terra**, a Cauda de Maré mantém a mesma mecânica com uma **onda de lama**: menor, mais curta, com dano e empurrão menores.
  - **Visual:** **onda 3D** (parede de água que cresce e avança) com **crista de espuma**, borrifos e gotas caindo; sem anéis desenhados e sem brilho.
  - Números: PROVISÓRIOS.
  - **20/11 — implementado no piloto e testado em Play. Aguarda avaliação.**
    - **Clipes novos** (`anim_crocodilo.py`):
      - `EmboscadaSaida` (0,6 s, evento impulso 0,33): sai reto e abre a boca;
      - `EmboscadaVoo` (laço de 0,5 s): corpo reto, boca aberta, dianteiras para a frente e traseiras para trás;
      - `EmboscadaPouso` (1,0 s, evento morde 0,07): a boca fecha de estalo e as patas plantam.
      - QA: IK ≤ 0,015. A pata chega 0,5 abaixo do chão no pouso, contra 0,29 no antigo.
      - Substituem GiroSaida, RolarDaMorte em laço e GiroPouso.
    - **Servidor** (`PoderesTeste`):
      - `M.emboscada` (o `giroEmboscada` continua como nome interno);
      - salto de 12, altura 3, voo de 0,55 s;
      - mordida no pouso a até 4,5 da superfície do corpo, num ponto 15,5 à frente do pivô (a ponta do focinho);
      - dano de Água; derruba pelo contrato de porte.
      - O atributo de efeito `Giro` virou `NoAr`.
    - **Onda real** (`ondaReal`):
      - a frente da onda cresce de 0,8 até o raio (água 14 em 0,9 s; lama 8 em 0,6 s);
      - cada alvo alcançado é atingido uma vez, com dano de Água (água 12, lama 8);
      - o alvo é empurrado para fora deslizando por 0,45 s (água 7, lama 4, menos para quem é pego mais longe);
      - quem a cauda acerta direto não leva a onda.
      - Números provisórios, em `Cauda.onda_*`.
    - **Cliente** (`CrocodiloFX_Cliente`):
      - `onda3D`: anel de 26 segmentos 3D (14 no celular), de água turva semitransparente (em terra, lama), que sobe, avança e tomba para a frente, com espuma fina na crista e borrifos que caem. Usa o mesmo raio e a mesma duração do servidor.
      - Emboscada: a água explode na saída (respingo + onda pequena); no pouso, respingo + onda na água, ou lama em terra.
      - A ponta da cauda levanta água ou lama durante a varrida.
      - Saíram os anéis desenhados da Cauda e da Emboscada. Nada brilha.
    - **Testes (Play):**
      - **Cauda na água:** a onda alcançou os alvos a 7,1 e 9,2 do centro (dano 12; empurrados 6,1 e 5,8); os alvos a mais de 14 não foram atingidos.
      - **Cauda em terra:** a onda de lama alcançou um alvo a 7,4 (dano 8; empurrado 2,8).
      - **Emboscada no raso:**
        - `NoAr` liga e desliga;
        - mordida de 24 na presa da frente, que caiu por 3,45 s; a presa a 9 de lado não foi atingida;
        - inclinação lateral depois do pouso: 0,0° (sem giro).
    - **Evidências:** vídeo `review/emboscada_onda_2011/Crocodilo_Emboscada_OndaReal.mp4` e prancha dos clipes `review/kit_agua_2011/prancha_emboscada_blender.jpg`.
    - **No place:** backup `ServerStorage.Crocodilo_ANTES_EmboscadaOnda`; place local salvo.
    - **r2 (usuário 20/11: "a onda deve chegar mais longe, e a água subir mais"):**
      - alcance: água 14 → **20** (1,2 s); lama 8 → **10** (0,7 s);
      - altura da parede de água até ~4,4 (antes ~2,4); lama até 1,4;
      - respingo do centro maior.
      - Teste: a onda alcançou alvos a 7,1, 9,2, **17,5 e 19,8** (dano 12; empurrados 6,4 → 4,5); os alvos mais longe não foram atingidos. Lama: 7,4 e 8,9.
      - Vídeo `review/onda_r2_2011/Crocodilo_Onda_r2.mp4`. Aguarda avaliação.
    - **r3 (usuário 20/11: "na terra, alcance mais longe"):**
      - onda de lama 10 → **15** (0,9 s); dano e empurrão iguais (8 e 4).
      - Teste: alcançou alvos a 7,4, 8,9 e **13,6** (empurrados 3,5 → 2,9); os alvos mais longe não foram atingidos.
      - Vídeo `review/onda_r3_2011/Crocodilo_OndaLama_r3.mp4`. Aguarda avaliação.
    - **r4 (usuário 20/11: "aumente o alcance da cauda de maré em terra"; escolheu "onda de lama até 20"):**
      - lama 15 → **20** (1,1 s), igual ao alcance na água; dano e empurrão continuam menores que os da água (8 e 4).
      - Teste (2 rodadas): alcançou alvos a 7,4–8,9 e 14,6 (empurrados 3,7 → 3,2); o alvo a ~20,6 da superfície e os mais longe não foram atingidos.
      - Vídeo `review/onda_r4_2011/Crocodilo_OndaLama_20.mp4`, de perto e de cima. **APROVADO pelo usuário em 20/11** ("Aprovar"). É a versão final da onda: água 20, lama 20.
    - **Limitação:** a onda é um anel de peças 3D, sem deformar a água do terreno. Na água funda o crocodilo fica quase todo submerso e aparece pouco na tomada.
- **20/11 — aplicado no piloto (Crocodilo-testes). Testado em Play. Aguarda avaliação.**
  - **Config:** `ConfigPoderes_Teste.Elemento = "Agua"`.
  - **Dano marcado como Água** por `ferir()` no `PoderesTeste`: grava `UltimoDanoElemento = "Agua"` e `UltimoDanoPoder` no alvo e depois aplica o dano.
    - Vale para a Mordida de Agarrão, o Giro de Emboscada e a Cauda de Maré.
    - A Submersão não causa dano; o bote dela é a Mordida de Agarrão.
    - A finalização continua física.
    - O sistema de vantagem e fraqueza entre elementos ainda não existe no jogo, então a marca só registra.
  - **Efeitos visuais** (`CrocodiloFX_Cliente`), sem brilho:
    - saiu o contorno verde (Highlight) do corpo no Giro;
    - saiu a esfera verde de campo de força das Escamas;
    - as gotas escorrendo ficaram sem emissão de luz (`LightEmission` 0).
  - **Novo `respingo()`:** gotas de água que sobem e caem pela gravidade, iluminadas pelo sol, sem emissão.
    - Aparece ao sair da água no Giro, no pouso na água, no impacto da Cauda na água e no golpe que as Escamas reduzem (borrifo curto).
  - **Testes:**
    - agarrão: `Agua` / `MordidaAgarrao`, vida 78;
    - cauda em terra: `Agua` / `CaudaDeMare`, dano 20;
    - cauda na água: funciona;
    - giro no raso: `Agua` / `GiroEmboscada`, dano 24;
    - Escamas: dano 20 → 17, com 3 respingos no cliente.
  - **Vídeo:** `review/kit_agua_2011/Crocodilo_KitAgua_Natural.mp4`.
  - **No place:** backup `ServerStorage.Crocodilo_ANTES_KitAgua`; place local salvo.
  - **Achado fora desta tarefa:** na emboscada da Submersão, o bote no boneco do canal errou por altura ("fora do vão 3,87"): a boca submersa fica abaixo do alvo na superfície. A pegada real ainda não sobe a cabeça até o alvo na água. A corrigir numa próxima etapa.
  - **20/11 — CORRIGIDO (usuário: "Sim, corrigir"). Testado em Play. APROVADO pelo usuário em 20/11 ("Aprovar e commitar").**
    - Na pegada na água, o corpo agora também **sobe** até a presa, não só se ajusta na horizontal. São passos curtos (≤1,2 por quadro), até `Agarrao.subir_agua` = 5. Isso fica em `pegarEm` e só vale na água; em terra nada muda.
    - **Testes (Submersão → emboscada):**
      - Boneco do canal: o desvio vertical caiu de 3,87 para 0,03–0,10, com o corpo subindo 3,7–4,1. O boneco é grosso demais (5,5 > vão 1,52), então leva **só a mordida** (dano 10), como manda a regra.
      - Presa pequena boiando (espessura 1,13): **presa pela cabeça**. O corpo subiu 4,0, os dentes cravaram 0,39, ficou presa por 3,51 s e foi solta pelo marcador.
    - **Sem vídeo:** a tomada ficou tapada por um poste da arena e a captura caiu para ~8 qps. A evidência são os registros acima.
    - **No place:** backup `ServerStorage.Crocodilo_ANTES_BoteAgua`; place local salvo.

### Elemento
- **[OFICIAL — 30/10/2026]** Cada criatura tem **um único elemento natural**. Não há 2º/3º elemento, alternância nem fusão elemental no sistema atual.
- **[OFICIAL — usuário 20/11/2026]** O elemento único do Crocodilo Primordial é **Água** (ver "Kit oficial" acima).
  - A lista da Etapa 15.1 "Água, Terra, Natureza" (nasce com uma e desbloqueia até mais duas) é histórico superado.

### Habilidades
- **[OFICIAL — 30/10/2026]** Cada criatura tem no mínimo **1 passiva + 3 ativas**; nomes, efeitos e quantidades são aprovados criatura por criatura. Ataques básicos físicos não ocupam slots.
- **Lista da Etapa 15.1** (era OFICIAL; após 30/10 vale como referência anterior; a lista final está **[PENDENTE]**):
  1. **Mordida de Agarrão** — mordida que agarra. PvE: agarrões prolongados. PvP: **[OFICIAL 19/11] prende por mais tempo, interrompível por aliados** (ver seção abaixo). [PROPOSTA] dano inicial, sinais de antecipação, esquiva por ângulo/distância.
     - **[ANOTADO — A DEFINIR, usuário 17/11] Depois de neutralizar:** quando o crocodilo agarra e balança (rola) até neutralizar o oponente, ele pode escolher entre **(a) soltar o corpo e comer** ou **(b) continuar andando com o corpo na boca para mais longe, para evitar roubos**. Clipes já existentes que podem servir: SegurarPresa/SegurarPresaAgua, ArrastarPresa, SoltarPresa, Comer. Nada implementado.
       - **Quem decide (usuário 17/11):** quando o crocodilo está **selvagem**, ou **tem dono mas está andando sozinho pelo mundo**, **ele mesmo decide**: verifica se há **oponente próximo**; se houver, **leva o corpo embora para outro lugar**; se não houver, **come**.
       - **O que é roubo (usuário 17/11):** outro animal — **controlado pela IA ou montado por um jogador** — chegar e **pegar o corpo para comer**.
       - Ainda a definir: raio de "oponente próximo", para onde leva (distância/abrigo), tempo de comer, o que acontece com o crocodilo montado (o cavaleiro decide?) e a regra em PvP.
  2. **Giro Predatório** — rotação de corpo e cauda, especialmente eficaz na água. [PROPOSTA] redemoinho local que desloca inimigos.
     - **[DECISÃO DO USUÁRIO 19/11/2026]** **Removido o Rolar da Morte como poder** (o giro com o alvo preso na boca, encadeado no agarrão). **Fica o Giro de Emboscada** (sai da água girando e cai em terra). O clipe `RolarDaMorte` continua existindo porque o Giro de Emboscada o usa no voo; o `M.giro()` do protótipo deve ser desativado (pendente, Studio não alterado).
  3. **Submersão** — [OFICIAL] mergulho e aproximação furtiva na água; **fora da água vira postura de camuflagem em lama e vegetação, não desaparecimento mágico total**. [PROPOSTA] bolhas/ondulações/folhas mexidas denunciam.
  4. **Cauda de Maré** — golpe poderoso de cauda que desloca inimigos; aproveita a água para gerar ondas locais. [PROPOSTA] em solo seco, varredura lateral.
- **Passivas:**
  - **Escamas Grossas** — −15% de dano físico; 70% da velocidade fora da água (referência v6.2; protótipo testado).
  - **Sentido de Vibração** — **[DECISÃO DO USUÁRIO 19/11/2026: nova passiva, no lugar do Rolar da Morte]**. Na água ou na margem, o crocodilo percebe criaturas que se mexem por perto pelas ondulações/vibração, mesmo sem vê-las; ajuda a emboscada. Só informação, sem dano. **[PROPOSTA de números, a aprovar]:** raio 40 studs na água / 20 em terra a até 10 studs da margem; só detecta quem está se movendo (parado não vibra); mostra ao dono do crocodilo uma marca discreta de ondulação na direção (sem atravessar paredes de terreno).
    - **19/11 — protótipo no Crocodilo-testes, APROVADO ("Aprovar e commitar", 19/11):** `Vibracao` no `ConfigPoderes_Teste` (raio 40 água / 20 margem, margem 10, só quem se move entre 1,5 e 60 studs/s — acima de 60 é teletransporte e é ignorado) e laço do servidor a cada 0,25 s no `PoderesTeste` (mede a água real, distância da cabeça, terreno sólido bloqueia); manda as posições só ao dono (`DonoUserId`), e o novo `VibracaoCrocodilo_Cliente` desenha um anel fino que abre e some. O `M.giro()` (Rolar da Morte) agora recusa ("removido"; `Giro.ativo = false`). Backups `ServerStorage.*_ANTES_Vibracao_2026-11-19`; place salvo; local = Studio (hash, 3 scripts).
    - Testes (Play): Rolar da Morte → "removido". Água: andando a 15–16 da cabeça → percebido (3,0–6,2 studs/s); parado a 25 → não; andando a ~55 → não (fora do raio). Margem: 5 e 19 da cabeça → percebido (raio 20). Terra longe da água → nada. Teletransporte para dentro do raio e parado → nada (antes do ajuste dava falso positivo de 616 studs/s). Cliente do dono: 9 anéis em 4 s de movimento, nenhum parado. Vídeo `review/pvp_1911/Crocodilo_SentidoVibracao.mp4` (8,2 s).
    - Observação: o anel é bem discreto (como pedido na proposta); no vídeo aparece pouco. Não testado: vários jogadores, celular, desempenho com muitos crocodilos (cada um faz ~9 raios por leitura).
- **[PROPOSTA — histórico, superada]** Transformações por afinidade (Água/Terra/Natureza) e as seis fusões direcionais (Corrente de Cipós, Manguezal Vivo, Couraça Enraizada, Armadilha das Margens etc.) contrariam a regra de elemento único. Não implementar.

### Agarrão contra jogadores (PvP) — **[OFICIAL — usuário 19/11/2026: Versão B]**
**Decisão do usuário (19/11/2026, "B: prende, aliados soltam"):** no PvP o agarrão **prende de verdade e segura por mais tempo, e os aliados da vítima podem interromper**. A Versão A ("só empurra") fica descartada. Continuam **[PENDENTE]**: duração no PvP, resistência a controle repetido (§18.2), como os aliados soltam (dano mínimo, golpe específico ou quebra de postura) e contrajogo da própria vítima. Histórico do conflito abaixo.

#### Números do agarrão PvP — **APROVADOS pelo usuário em 19/11/2026 ("Aprovo") [A TESTAR]** (valores de partida; balanceamento final depois, como nos demais kits)
Base: referência v6.2 §4 (agarrão 2,5 s, 4/s, alcance 9, cone 60°, recarga 10 s, energia 25), porte §0d (Crocodilo adulto 24–32 de comprimento ÷ 2,5 = **grande**), limites globais (controle PvP curto, resistência a repetição, mínimo de 4 s entre atordoamentos no mesmo alvo) e o padrão já definido das outras pegadas (Pinças do Escorpião, Espiral da Serpente: efeito muda com o tamanho do alvo).

| Item | Proposta |
|---|---|
| Duração PvP | **2,5 s** (PvE continua 3,5 s) |
| Por porte do alvo | pequeno/médio/grande: **preso e imobilizado**; **colossal** (dragões, Leviatã): morde um membro, **50% de lentidão**, não salta nem decola, 1,5 s |
| Giro encadeado (Rolar da Morte) | usa o tempo que resta da pegada: **agarrão + giro ≤ 2,5 s no total** (o giro não renova a pegada) |
| Dano | contato 0,5× a mordida (10) + 4/s (≈ 20 no total), igual ao protótipo |
| Aliados soltam | dano somado no crocodilo durante a pegada **≥ 8% da vida dele** (950 → 76; Escamas contam) **ou** 1 golpe pesado (atordoa/derruba). Ao soltar assim, o crocodilo fica **0,6 s de boca aberta** (vulnerável, sem nova pegada) |
| Contrajogo da vítima | esquivar na antecipação (sinal de ~0,35 s antes do bote); presa, cada golpe dela na cabeça do crocodilo tira **0,3 s** da pegada (máx. −1,0 s) |
| Resistência a repetição | depois de solta, a vítima fica **8 s imune a qualquer agarrão** (de qualquer crocodilo); outro controle (atordoar, derrubar, prender) recebido nos **4 s** seguintes dura **50%** |
| Idade do crocodilo | duração × Força da idade (§0c): Jovem 55%, Pré-adulto 80%, Adulto 100%, Ancião 110% (2,75 s) |
| Água | no PvP **não arrasta a vítima para o fundo** (fica na superfície); emboscada submersa continua valendo para iniciar |
| Depois de neutralizar (PvP) | criatura de jogador **não é comida nem levada**: sai da luta e vai ao refúgio (regra geral do contrato por porte); comer/levar o corpo fica só para presas e selvagens |

**Respostas do usuário (19/11/2026) [OFICIAL]:**
- **Só criaturas:** o agarrão não pega o humano a pé.
- **Vítima montada:** antes da mordida do crocodilo, **o cavaleiro pula rapidamente** da montaria (não é agarrado junto; só a criatura é presa).
- **O cavaleiro que pulou conta como aliado** (usuário 19/11, "Sim, conta"): os golpes dele somam para soltar a criatura, como os de qualquer aliado.
- Ainda a definir: para onde ele pula e se o pulo tem tempo mínimo de aviso.
- **19/11 — protótipo (só bonecos), APROVADO com o "Ok" de 19/11:** `pularCavaleiro` no `PoderesTeste` (convenção de teste: ObjectValue `Cavaleiro` na montaria). Na mordida em criatura de jogador montada, o cavaleiro sai da sela 0,10 s depois do início e pula em 0,30 s, **7 studs para longe do crocodilo** [PROPOSTA de direção/tempo, `AgarraoPvP.pulo_*`]; chega ao chão 0,05 s antes do contato (0,42 × 0,47 s), não é agarrado. Os golpes dele soltam a criatura como aliado (3 × 40 com Escamas → 102 ≥ 76). Criatura que não é de jogador: sem reação. Não testado: jogador real, câmera do cavaleiro, pulo sobre água (cai na altura do fundo + 2,5, a revisar). Vídeo: `review/pvp_1911/Crocodilo_AgarraoPvP_Cavaleiro.mp4` (20 s, 2 tomadas: cavaleiro pula e solta a criatura como aliado; sem aliado a pegada solta sozinha em 2,5 s).
- **19/11 — teste com jogador e outra criatura (só em Play, nada salvo no place):** o jogador do Play (R15) montado no crocodilo antigo em escala de Jovem (0,65 = porte médio, PvP) como criatura-vítima. Pulo aos 0,12–0,17 s, contato 0,46–0,80 s; o jogador corre até a cabeça e dá socos (KFS de soco só de teste); o servidor só aceita o soco a até 8 studs da cabeça. Rodada A: 3 socos a 5,7–5,8 studs → "ALIADO Yxx_Winner SOLTOU a presa" (102 ≥ 76) aos 2,2 s do contato. Rodada B: chegou em 0,95–1,6 s e só deu 2 socos antes do prazo (68 < 76, solta pelo prazo). Rodada C: ficou preso num boneco de teste a 13,9 studs → socos recusados pelo alcance, solta pelo prazo. Vídeo `review/pvp_1911/Crocodilo_AgarraoPvP_Jogador.mp4` (14,6 s, 2 tomadas).
- **Achados para decisão:** (1) com o pulo de 7 studs para longe + 2,5 s de pegada, **um cavaleiro sozinho mal consegue soltar** a própria criatura (às vezes 3 socos, às vezes 2) → **decisão do usuário 19/11: "pular mais perto"**; (2) a criatura presa é segurada pelo pivô, então um corpo grande (21 studs) gira inteiro junto com a mandíbula — fica estranho; para criaturas médias/grandes a pegada visual precisa de um ponto de mordida no corpo (pescoço/pata) em vez do centro.
- **19/11 — pulo mais perto (usuário), APROVADO ("Ok", 19/11):** o cavaleiro agora cai **ao lado da cabeça do crocodilo** (5 de lado, 1,5 atrás do focinho; `AgarraoPvP.pulo_lado/pulo_recuo`, substitui `pulo_dist`), do lado em que estava. Backups `ServerStorage.*_ANTES_PuloPerto_2026-11-19`; place salvo; local = Studio (hash). Teste com o jogador (5 rodadas iguais): cai aos 0,40 s a 4,4–4,5 da cabeça, socos aos 0,63/1,20/1,77 s a 4,3–5,3 studs, **solta a criatura em 1,3 s após a mordida** (102 ≥ 76), sem precisar correr. Vídeo `review/pvp_1911/Crocodilo_AgarraoPvP_PuloPerto.mp4` (9,3 s, 2 tomadas, captura a ~23 qps). Consequência: sozinho, o cavaleiro agora sempre solta antes do prazo (1,3 de 2,5 s) — se ficar fácil demais, ajustar o limite (8%) ou o dano do soco.
- **19/11 — opção "Soltar aliado" (usuário), APROVADA ("Ok", 19/11):**
  - **[PENDENTE — depende das armas, usuário 19/11]:** depois que existirem espadas e as outras armas do jogador, **só será possível soltar o aliado golpeando com uma arma** (sem soco de mão vazia). O soco atual é só de teste; ao integrar, trocar `animSoco`/`soco_dano` pelo ataque e dano reais da arma equipada e não mostrar (ou recusar) a opção para quem estiver sem arma. quando o crocodilo agarra a criatura de um jogador, os aliados dela (o cavaleiro que pulou e quem estiver no atributo `Aliados`, a até 60 studs) recebem o botão **"Soltar aliado [E]"** (clique/toque no celular, tecla E, botão X do controle; `SoltarAliado_Cliente` em StarterPlayerScripts, só mostra e pede). Ao escolher, o **servidor** valida (é aliado, pegada ativa; senão recusa e registra) e leva o personagem andando de verdade (`Humanoid:MoveTo`) até o lado da cabeça do crocodilo; perto, vira para a cabeça e golpeia a cada 0,55 s; cada golpe só conta a até 8 studs da cabeça no impacto (dano de teste 40, `AgarraoPvP.soco_*`). O botão some quando a criatura é solta ou a pegada acaba. Backups `ServerStorage.*_ANTES_SoltarAliado_2026-11-19`; place salvo; local = Studio (hash, 3 scripts). O cavaleiro não golpeia mais sozinho: só se escolher.
  - Testes (jogador R15 no Play): pedido sem pegada → recusado. Montado: botão em 0,42 s (no contato), escolhido 0,15–0,35 s depois, 3 golpes a 4,9–5,2 studs → solta (102 ≥ 76) aos ~2,2 s; botão some sozinho. Aliado a pé a 26 studs: corre 1,75 s, 1 golpe a 5,9–6,0 antes do prazo → solta pelo prazo (longe demais para salvar sozinho). Vídeo `review/pvp_1911/Crocodilo_SoltarAliado.mp4` (11 s, 2 tomadas, botão visível).
  - Não testado: jogador real clicando (o teste aciona o mesmo pedido que o botão manda), vários jogadores, celular de verdade, combate real do jogador (o soco é animação de teste).
- **19/11 — PONTO DE MORDIDA (resolve o achado 2), APROVADO (19/11):** alvo com mais de 6 studs (`Agarrao.rigido_max`) não é mais segurado pelo centro: no contato o servidor escolhe o **osso da vítima mais perto dos dentes** (ex.: `CoxaE`; sem ossos, o ponto da caixa mais perto) e só esse ponto segue a ponta dos dentes. O corpo **fica em pé** (sem inclinar, na altura do contato) e **vira aos poucos (2,5 rad/s, `giro_corpo`) para ficar atrás da mordida**, como se fosse arrastado; ao soltar, fica onde está, em pé. Alvos pequenos (bonecos, 5,5 studs) continuam presos rígidos na boca como antes. Backups `ServerStorage.*_ANTES_PontoMordida_2026-11-19`; place salvo; local = Studio (hash).
  - Teste em Play (crocodilo jovem ×0,65, 21 studs, agarrão + Giro): "PONTO DE MORDIDA: CoxaE (2,6 dos dentes)"; inclinação máxima 0,00°, variação de altura 0,000, o corpo girou 64° para ficar atrás; solto em pé no prazo (2,97 s). Boneco pequeno: modo rígido, igual antes. Vídeo `review/pvp_1911/Crocodilo_PontoDeMordida.mp4` (11,2 s, 2 tomadas: lado e de cima).
  - Limitação: o corpo da vítima é rígido (sem animação de ser arrastada/debater-se); no Giro o crocodilo rola mas a vítima continua em pé — pede clipes de reação da vítima quando existirem.

**19/11/2026 — protótipo no Crocodilo-testes (só bonecos). Implementado e testado em Play; APROVADO pelo usuário em 19/11/2026 ("Aprovar").**
- `ConfigPoderes_Teste.AgarraoPvP` com os números aprovados; `PoderesTeste`: boneco com `PvP=true` simula a criatura de um jogador, `Porte` muda o efeito; imunidade 8 s e redução de controle 4 s em atributos do alvo; solta por aliado (`receberGolpe(..., {pesado})`), corte da vítima (`{deVitima}`), boca aberta 0,6 s, giro dentro do prazo, Idade do crocodilo, derrotado → `Refugio` (simulado). Backups `ServerStorage.*_ANTES_PvP_2026-11-19`. Place salvo.
- Resultados: pegada 2,53 s; giro encadeado termina em 2,54 s no total; aliado solta no 3º golpe (102 ≥ 76) e a nova pegada é recusada por 0,6 s; golpe pesado solta na hora; vítima corta até −1,0 s (1,55 s); colossal só lentidão 1,52 s; PvE continua 3,5 s; Jovem 1,38 s; derrubada do Giro de Emboscada cai para 0,75 s logo depois de solto; reagarrar imune = só mordida.
- Lição: prazo contado pelo `dt` da simulação (com o servidor a 4–7 fps o clipe atrasava e o relógio real vencia antes). Evidência: `review/pvp_1911/testes_agarrao_pvp_play.txt`.
- Não testado: jogadores reais, celular, montado, humano a pé, refúgio real.

O próprio RPG_02 se contradizia (resolvido em 19/11):
- **Versão A — "PvP só empurra":** ficha da Etapa 15.1, catálogo §2, tabela de habilidades, comparação ecológica, tabela de balanceamento, tabela §10 e o texto "a decisão 7 foi opção C, não A". Diz: agarrões prolongados só no PvE; no PvP, efeitos de agarrão viram **empurrões, sem prender nem arrastar, mesmo com interrupção por aliados**.
- **Versão B — "agarrão PvP mais longo, interrompível por aliados":** §12 (correção de consistência), §13 item 2 e §18.2. Diz que "só empurra" **foi um erro de auditoria** e que a escolha do usuário na Etapa 15.1 foi agarrão PvP mais longo, porém interrompível por aliados.
- Em ambas: **PvE pode ter agarrão prolongado**; durações, resistência a controle repetido e contrajogo estão **[PENDENTE]**. A regra global (§18.2) exige resistência a controle repetido e interrupção por aliados.

## 3. Atributos (Etapa 24)
- **[OFICIAL — 24.1]** 6 atributos: Vida, Defesa, Força, Velocidade, Energia, Poder Elemental. Comparação entre Adultos nível 100. Velocidade e manobra analisadas separadamente em terra, água e ar. Vantagem ambiental ~10–15%; raridade 1–5%.
- **[PROPOSTA — 24.2, NÃO APROVADA]** Números do Crocodilo Primordial:
  - escala 1–5: Vida 4, Defesa 4, Força 4, Velocidade 5 (no meio favorável), Energia 3, Poder Elemental 3;
  - valores absolutos: 5.350 HP, Defesa 160, Força 190, Energia 120, Poder Elemental 120;
  - velocidade: terra 16 studs/s (manobra 1), água 43 studs/s (manobra 5), sem voo.
- **[SIMULAÇÃO ILUSTRATIVA, NÃO OFICIAL]** §19.2: duelo Crocodilo Primordial × Basilisco ≈ 111,5 s.

## 4. Mundo e habitat (segundo os registros do mapa)
- `DOCS/estado/mundo-pantano.md` (M3/M3b, 22/10): marcadores em `Pantano_Nebuloso/Habitats/Crocodilo_Primordial` (V2, **sem IA**):
  - 11 Territórios (um por sistema de água funda ≥8, com área, profundidade máx., raio e população sugerida);
  - 7 Tocas_Submersas (poços-toca de 28–54 de profundidade, `M.POCOS` do `PantanoGen`);
  - 10 Corredores (197 pontos ao longo dos canais fundos);
  - 8 Emboscadas_Travessia (água funda junto de cada travessia);
  - 14 Descanso_Margem (margem seca, >30 da trilha);
  - 4 LocalNinhoElegivel **inativos** (>60 da trilha).
  - Versão antiga em `Retirados_Pantano`. M3d baixou 216 marcadores aquáticos para dentro da água.
- Hidrografia: canais 16–38 de profundidade, prateleira rasa nas bordas (emboscada), Lago Profundo até ~50.
- **[OFICIAL]** Ninhos reaparecem em 30–60 min; quantidade por jogador é [PROPOSTA].
- **Conferir no Studio** se os marcadores continuam lá antes de usar (não conferido nesta sessão).

## 5. O que já existe

### Roblox Studio (segundo os registros; não conferido nesta sessão)
- `ServerStorage.Biblioteca_Criaturas.Catalogo` registra a forma (medidas, elementos históricos, locomoção, montaria, 4 habilidades) — `DOCS/estado/criaturas-gerais.md`, 26/10.
- **Nenhum modelo do Crocodilo foi importado nem testado no Studio.**
- Atenção: o PILOTO de 27/10 registrou um place antigo aberto (PlaceVersion 394) sem `Biblioteca_Criaturas`. Conferir qual place está aberto antes de qualquer trabalho.

### Blender
Três gerações, nenhuma aprovada artisticamente pelo criador:
1. **C1 (26/10)** — `BLENDER/Criaturas/Crocodilo_Primordial.blend/.glb/.fbx` + `_Cor_Verde_Pantanal`, `_Cor_Marrom_Aluvial`, `_Cor_Negro_de_Rio`, `_Normal` (.png). 23 ossos, 8.520 tris, 6,2 de ombro e 25,7 de comprimento (dentro do oficial). 11 animações: Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar, Natacao + MordidaDeAgarrao, GiroPredatorio, Submersao, CaudaDeMare. Script: `BLENDER/Criaturas/scripts/repteis_crocodilo_basilisco_lagarto.py`.
2. **V2 refinada (27/10)** — `BLENDER/Criaturas/Blockouts/Crocodilo_Primordial/` (`_blockout`, `_refinado`, `_final` .blend) e `_Export/Crocodilo_Primordial.glb`. Script `build/build_Crocodilo_Primordial.py` (+ `esqueletos.py`, `pipeline_final.py`). 24 ossos, 31 animações, 28.718 tris. Crânio largo e plano, mandíbula pesada com dentes, olhos/narinas no topo, osteodermos em escudos, crista dupla na cauda, patas com cotovelo para fora. Medida do blockout: ombro ~5,8, comprimento 30,6.
   - Auditoria numérica `AUDITORIA-ANIMACOES-V2.csv`: 30 aprovadas, 1 "pequenos ajustes" (**GuardarNinho**). Inclui locomoção, Arrancada/Frenagem, ReacaoGolpe, AtaqueBasico, Morte, Comer, Descanso (3), Montar/Desmontar, Montado* (5), Alerta, Ameaca, **NadoCruzeiro, Mergulho, Emersao** e as 4 habilidades.
3. **V5 (27/10)** — `_refinado_v5.blend`, `_final_v5.blend`, `_Export/Crocodilo_Primordial_v5.glb` (5,0 MB). Revestimento de placas (`build/revest.py`), osteodermos maiores. 56.198 tris (maior malha 15.998), 24 ossos, animações 30/1/0. **Falta cavidade da boca, dentes e língua** para rugido/ameaça. Anatomia ainda é a silhueta V2.
- Renders `review/Crocodilo_Primordial/` são citados no relatório V5, mas **não foram encontrados** no repositório.

### Código (`src/`)
- Nada específico do Crocodilo: sem IA, combate, montaria, nado nem sons. A IA, os sons e a montaria existentes são dos dragões e são arquivos compartilhados (`Cerebro`, `EstadosDragao`, `ConfigCombate`, `SonsConfig`…).

### Modelo adulto fiel à referência (03/11/2026, aguardando aprovação visual)
- Referência escolhida pelo usuário: `REFERENCIAS/pantano-nebuloso/crocodilo-primordial/crocodilo-primordial-referencia-principal.png` (cópia sem alteração, SHA-256 `dc5df015…888f`).
- Pasta própria: `BLENDER/Criaturas/Crocodilo_Primordial_Ref/` (`asset-brief.md`, `scripts/`, `review/`, `meshy/`). Nada anterior foi alterado.
- **Base A — procedural** (`scripts/criar_crocodilo.py` → `CR_Crocodilo_Ref.blend`): seções elípticas + voxel, boca cortada (fenda, cavidade, garganta), dentes/gengivas/língua/olhos/cristas/garras. 8 rodadas (R1–R8). 30,2 de comprimento, ombro 6,63. Corpo ~500 mil tris (alta). Fica longe da referência no rosto e na pele.
- **Base B — Meshy 7.1 image-to-3D** (`scripts/meshy_img3d.py`, 1 tarefa, **30 créditos**; `normalizar_meshy.py` → `CR_Crocodilo_Meshy.blend`): muito mais fiel no rosto, olho, dentes, cristas e escamas. Boca aberta como a referência, com palato, língua e gengivas.
  - Escala: com 29,5 de comprimento, ombro da pele ≈ 4,7–4,9, **abaixo do mínimo oficial de 5**. Com 32 (máximo oficial), ombro ≈ 5,1. Corpo mais esguio que a referência.
  - Defeitos: textura rosada na parte de baixo da mandíbula; ventre e mandíbula mais claros (creme) que o ocre da referência; garras fundidas aos dedos; 692 mil tris; malha dividida por costuras de UV (432 ilhas).
- Prancha: `review/PRANCHA_comparativa_A_procedural_x_B_meshy.png`.
- Não testado no Roblox nem no celular.

**03/11/2026 (tarde) — usuário escolheu a base B (Meshy).** Feito (só Blender, sem Studio):
- Escala oficial: comprimento **32,0** (máximo da faixa), ombro da pele ≈ **5,3–5,5** (5,73 com cristas), largura 10,1. `CR_Crocodilo_Meshy_v2.blend` (o v1 com 29,5 foi preservado).
- Cor: máscara por geometria na HIGH — ventre/flanco baixo creme → ocre terroso; faixa rosada sob a mandíbula removida; saturação +15%, valor −7%. Dentes, garras e boca fora da máscara.
- LOW: `CR_Crocodilo_LOW.blend` — **19.000 tris / 9.487 verts, 1 malha, 1 material** (cabe num MeshPart ≤ 20k). Costuras soldadas antes do Decimate, UV nova. Bake HIGH→LOW: cor, normal (tangente), rugosidade em `tex/` 2048 (mestre) e 1024 (Roblox). Memória estimada a 1024: ~4 MB por mapa sem compressão (~12 MB os 3, +⅓ com mipmaps); comprimido na GPU ~0,7–1,3 MB por mapa.
- Rig de TESTE (`CR_Crocodilo_LOW_rigteste.blend`, 27 ossos: Raiz, Pelve, Coluna, Pescoco, Pescoco2, Cabeca, Mandibula, Cauda1–8, 4 patas × 3): pesos heat + mandíbula por disputa geodésica crânio×queixo. Dobradiça medida y −10,26 / z 3,92; boca do Meshy aberta ~14°.
  - Cauda: flexão lateral e vertical limpas.
  - Mandíbula: fecha bem até **80%**; a 100% os dentes de baixo atravessam o focinho (o Meshy não tem encaixes). Aberta +14°: faixa esticada e um dente de cima puxado no canto da boca → corrigir com pesos manuais no rig final.
- Prancha: `review/m3/prancha_m3.png` (cor/escala) e `review/rig4/PRANCHA_rig_teste.png` (rig).
- Diferenças que continuam frente à referência: corpo mais esguio e baixo (patas mais curtas); ventre ainda um pouco mais claro; garras fundidas aos dedos; cristas na região do ombro vão atrapalhar a sela.
- [PROPOSTA] LOD: deixar `RenderFidelity` automático do Roblox ou exportar LOD1 ~8k e LOD2 ~3k para distância.

**03/11/2026 (noite) — visual aprovado pelo usuário ("Aprovo, seguir"): rig final, 6 clipes e GLB (só Blender).**
- `scripts/rig_final.py` → `CR_Crocodilo_Rig.blend`: 28 ossos com nomes do jogo (Raiz, Pelve, Coluna1–2, Pescoco, Pescoco2, Cabeca, Mandibula, Cauda1–8, BracoE/D, AntebracoE/D, MaoE/D, CoxaE/D, CanelaE/D, PeE/D). Articulações de cada pata medidas na própria malha. As traseiras do Meshy estão desencontradas (pose de passo da referência); **a malha não foi reposicionada** (lição do Silverwing).
  - Pesos: heat + mandíbula por disputa geodésica crânio×queixo com linha lateral do lábio + voto de maioria; suavização só atrás do canto; ≤ 4 influências.
  - IK de 2 ossos por pata só para animar (polo por busca numérica, desvio no repouso 0,0003); os clipes são gravados em FK.
- `scripts/anim_crocodilo.py` → `CR_Crocodilo_Anim.blend` + `clipes/Crocodilo_<Clipe>.json` (mesmo formato dos dragões para `montar_kfs_json.luau`) + `clipes/manifesto_clipes.json`:
  - Repouso (4 s, laço; boca 80% fechada, respiração, cauda lenta); Andar (1,5 s, laço, pares diagonais, **1,85 studs/s**); Corrida (16 quadros, laço, **8,75 studs/s**); Nado (2 s, laço, patas recolhidas, cauda em onda); Mordida (1 s, antecipação → bote → recuperação); Ameaça (2 s, corpo e cabeça erguidos, boca aberta com tremor).
  - QA numérico: erro de IK ≤ 0,005; escorregão do pé apoiado ≤ 0,06 studs/s (corrida) e 0 (andar); ponta do pé no chão.
  - A traseira direita tem a base 0,6 stud para dentro em todos os clipes (no Meshy está aberta e quase esticada).
  - Limites da boca: fecha no máximo **80%** (a 100% os dentes de baixo atravessam o focinho); abre no máximo **+4°** além da boca do Meshy (~14°, a abertura da referência). Mais que isso estica dentes.
- `scripts/exportar_croc.py` → `export/CR_Crocodilo_Primordial.glb` (7,0 MB): 1 malha 19.000 tris, 28 ossos (todos com peso), texturas 1024, sem animação. Reimportado no Blender: 1 malha, 28 juntas, 4 influências, 32,0 × 10,1 × 5,7.
- Pranchas: `review/clipes4/PRANCHA_boca_v3.png` (estado atual da boca), `review/clipes2/PRANCHA_patas.png`, `review/clipes2/PRANCHA_topo.png`, GIFs em `review/clipes2/`.
- **Defeitos conhecidos:** 1 dente grande de cima ainda estica como fio quando a boca abre além do repouso; uma pontinha de dente fica sob o queixo no estalo da Mordida. A tentativa automática de corrigir contatos dente-arcada piorou (jogava a ponta do focinho na mandíbula) e ficou desligada (`CONTATOS = False`). Correção dirigida por vértice pendente.
- **Não testado no Roblox/celular.** Importação do GLB (Import 3D) é passo manual; KeyframeSequence só toca no Studio; publicar animações exige a conta do usuário. Unidade: 1 unidade Blender = 1 stud (conferir escala na importação).

**03/11/2026 — correção do dente (pedido do usuário "Sim, corrigir dente").** Diagnóstico com `scripts/diag_esticadas.py` (arestas que esticam com a mandíbula girada):
- Causa: entre palato e assoalho, por dentro dos dentes, o Meshy fez uma parede contínua (bochecha interna) que liga as arcadas; e os caninos esquerdos de cima e de baixo se tocam ponta com ponta.
- Correções em `rig_final.py`: (1) membrana interna com peso em degradê do assoalho ao palato; (2) suavização local (bola de 0,3) onde ainda esticava; (3) canino de baixo esquerdo todo com a mandíbula e **encurtado para 55%** a partir da base (a ponta para dentro do canino de cima ao fechar); a ponta do canino de cima volta para o crânio.
- Em `anim_crocodilo.py`: fecha no máximo **65%** (a boca descansa entreaberta, como crocodilos reais) e **não abre além da boca do Meshy** (`ABRE_MAX = 0`, que é a abertura da referência).
- Testado e descartado: trocar dono por contato (cascata, focinho ia para a mandíbula); bolas inteiras para um lado (até 7,7×); inclinar o canino para fora (fica enterrado na lateral do focinho).
- Resultado: na abertura máxima dos clipes nenhuma aresta estica (1,00×); fechada 65%, máximo 1,8× em arestas minúsculas. Prancha: `review/clipes9/PRANCHA_boca_corrigida.png`. GLB reexportado (19.000 tris, 28 ossos).
- Diferença visível frente ao Meshy: canino de baixo esquerdo mais curto, ligado ao de cima por uma ponte fina na boca aberta.
- **Superado pelo Lote 1** (abaixo): os limites 65%/0° escondiam o defeito.

**03/11/2026 — Lote 1 do complemento (boca funcional + revisão dos 6 clipes). Aguardando aprovação.**
- Baseline preservado: `baseline_L0/` (rig, anim, JSON, GLB e scripts anteriores).
- Diagnóstico: `scripts/cortes_boca.py` → `review/cortes_L0.png`. Na frente as arcadas já eram cascas separadas, ligadas só por pontas de dente; de y −12,75 até o canto (−10,8), colunas de tecido do Meshy ligam as arcadas por dentro.
- Correção na origem (`scripts/rig_final_v2.py` → `CR_Crocodilo_Rig.blend`): rasgo da malha entre faces de donos diferentes na frente (contatos de dente) e no meio das colunas internas do canto; furinhos tampados com UV do vizinho e normais refeitas; degradê só no canto anatômico. Removidos os remendos da v1 (membrana, bolas, canino encurtado). Malha: 19.012 tris (12 de tampas), 1 malha, 1 material, texturas 1024.
- Resultado: **fecha 100%** com os dentes de cima por fora, sem furar o focinho; **abre +12°** além da boca do Meshy sem fios. Prancha antes/depois: `review/L1_boca/ANTES_DEPOIS_boca.png` (fechada/meia/repouso/aberta × esquerda/direita/frente).
- Clipes (`scripts/anim_crocodilo.py`): boca 100%/+12°; pé dobra na saída/pouso sem entrar no chão; Repouso com cauda mais calma; Nado com patas encostadas apontando para trás e cabeça estabilizada.
- Exportador: o osso Raiz recebe só 2% num vértice (antes 100% → puxão).
- Evidências: `review/L1_clipes/` (FOLHA_* e GIFs de 3 ciclos; Mordida e Ameaça também em câmera lenta). Chão quadriculado de 1 stud com deslocamento na velocidade do clipe; água de teste no Nado (não é física).
- QA (`scripts/qa_clipes_json.py`): 28 ossos iguais no JSON e no GLB reimportado, erro de norma ≤ 0,000007, laços sem salto exceto a Corrida (último→primeiro quadro da mão 26° contra passo máximo de 17°, ciclo de 16 quadros).
- Pendências: 2–3 lasquinhas minúsculas e franjas finas no fundo da boca só visíveis bem aberta; dedos não são ossos (pé é bloco único); Roblox/celular/física não testados.
- Inventário completo e especificação dos poderes: `DOCS/criaturas/crocodilo-primordial-animacoes.md`.

**03/11/2026 — correções finais do Lote 1 (versão L1b). Aguardando aprovação; Lote 2 não iniciado.**
- Versão do Lote 1 preservada em `versao_L1/` (além de `baseline_L0/`).
- **Corrida:** diagnóstico com `scripts/diag_ciclo.py` (posição e rotação no mundo, quadro a quadro, incluindo o retorno último→primeiro). O salto vinha do IK: o pouso da dianteira caía no ponto mais à frente com a pata quase esticada, e o antebraço girava 26,7° num quadro. Correção: passo das dianteiras centrado 0,3 stud mais para trás (sob o ombro), mesma passada (2,1), mesma duração (16 quadros) e mesma velocidade de sincronização (8,75 studs/s). Retorno agora abaixo do maior passo interno em todos os ossos (antebraço esquerdo 12,9° contra 15,6°; braço 9,9° contra 15,0°); no JSON a mão passou de +8,98° para −4,06°; escorregão do pé 0. Tabelas por osso dos seis clipes: `review/diag_ciclo_<Clipe>.txt`.
- **Boca:** causas achadas com `scripts/diag_bordas.py` e `scripts/pixel_face.py` (raio da câmera até a face):
  - lasca escura = uma tampa de 8 lados (face 19000) atravessando a ponta do canino de cima esquerdo;
  - franjas = 4 laços abertos deixados pelo rasgo das colunas do canto.
  - Correção em `rig_final_v2.py`: rasgo da frente separa também os vértices das pontas; os furos da frente são fechados juntando a borda num ponto; as faces mistas das colunas do canto saem e todo laço aberto do canto recebe um leque com UV de tecido do palato. O dono (crânio/mandíbula) passou a viajar numa camada da malha, porque juntar vértices renumera índices.
  - Testados e descartados: encolher os toquinhos (textura em listras), tampa com UV do vizinho (atravessa ilhas da UV).
- Mantido: fecha 100% e abre +12°. Malha final 18.993 tris, 28 ossos, 1 material, texturas 1024; bordas abertas na cabeça: 2 arestas na ponta de um canino.
- Evidências: `review/L1b/` — `boca/GRADE_L1_antes.png` × `boca/GRADE_L1b_depois.png`; `clipes/` (folhas e GIFs de 3 ciclos; Corrida, Mordida e Ameaça também em câmera lenta); `glb/GRADE_glb_json.png` (GLB reimportado + quadros dos JSON); `PRANCHA_ref_x_L1b.png`.
- GLB reimportado: 28 ossos, raiz "Raiz", 1 material, 28 grupos, modificador Armature; poses dos JSON reproduzidas. **Roblox, celular e física continuam sem teste.**

**03/11/2026 — Lote 2 (locomoção, transições e água). Aguardando aprovação; Lote 3 não iniciado.**
- Versão L1b preservada em `versao_L1b/`. Rig e GLB **não mudaram** (só animação): `export/CR_Crocodilo_Primordial.glb` continua válido; 21 JSON em `clipes/`, todos com os 28 ossos do GLB.
- 15 clipes novos em `scripts/anim_crocodilo.py`: VirarEsquerda/Direita (laço), Arrancada, Frenagem, RepousoParaAndar, AndarParaRepouso, AndarParaCorrida, CorridaParaAndar, NadoParado (laço), CurvaAquaticaEsquerda/Direita (laço), Mergulho, Emersao, EntradaAgua, SaidaAgua. Nado = NadoCruzeiro (sem duplicata). NadoRapido não feito (proposta).
- Técnica: planejador de passos (pé fixo no mundo, pouso meio passo à frente do neutro, levanta ao chegar ao limite de alcance de cada pata, passos de acomodação ao parar, estado inicial igual ao do laço de origem); viradas com o pé apoiado girando em torno do pivô; na água os alvos dos pés acompanham o corpo.
- QA: IK ≤ 0,04 e escorregão no mundo ≤ 0,06 studs/s em todos; laços fecham sem salto; tabelas em `review/qa_json_L2.txt` e `review/diag_ciclo_<Clipe>.txt`; emendas em `clipes/emendas_transicoes.json`.
- Evidências: `review/L2/clipes/` (22 folhas, 36 GIFs) e resumos `review/L2/RESUMO_terra.png`, `RESUMO_agua.png`.
- Limitações: na entrada/saída da água não há margem nem água no render de teste (o corpo aparece afundando no chão); a profundidade do mergulho é do jogo; velocidades/giros são sincronização técnica; curvas aquáticas com giro só proposto (25°/s).

**03/11/2026 — pendências do Lote 2 (versão L2b). Lote 2 aguardando avaliação; Lote 3 não iniciado.**
- Versão L2 preservada em `versao_L2/`. Rig e GLB **não mudaram**. Só 4 JSON mudaram (EntradaAgua, SaidaAgua, VirarDireita, VirarEsquerda); os outros 17 estão idênticos à L2.
- **VirarDireita, divergência:** o "0,002/0,06" do relatório L2 vinha de uma rodada parcial anterior; o manifesto (0,0058/0,175) era o real. Medido de novo (`scripts/qa_pe_mundo.py`): osso MaoE 0,175 studs/s no fim do apoio e sola 0,473; a VirarEsquerda também escorregava na sola (0,263) porque o pé não contra-girava. Correção na origem: o pé apoiado gira junto com o corpo (guinada = ângulo de apoio) e as dianteiras ficam 0,25 para dentro. Agora IK 0, osso 0, sola 0,135 (D) e 0,119 (E), resíduo da deformação da pele do tornozelo; laço fecha com excedente ≤ 0,01°.
- **EntradaAgua/SaidaAgua:** cena de teste `scripts/cena_agua.py` (margem 10°, fundo submerso, plano de água; **água só visual, não é física do Roblox**). Problemas achados e corrigidos: a entrada desacelerava até 0 e nivelava o corpo em cima da rampa (rabo/quadril penetrando até 4,7); havia um salto oculto da Raiz (−0,35) e arfagens internas que brigavam com a inclinação do terreno. Agora a entrada mantém a passada, a inclinação vem do terreno (jogo) e a profundidade também. Penetração máxima nas sequências Andar→EntradaAgua→Nado, Nado→SaidaAgua→Andar e terra: 0,18 (garras).
- Emendas: EntradaAgua começo×Andar 1,4°, fim×Nado 10,1°; SaidaAgua começo×Nado 6,5°, fim×Andar 13,3° (crossfade no jogo).
- Evidências: `review/L2b/` — `seq/` (folhas e GIFs lado/3-4, normal e lento, `medidas_*.json`), `virar/` (topo e patas, 3 ciclos), `virar_antes/`, `COMPARA_VirarDireita_antes_depois.png`, `RESUMO_L2b.png`; QA em `review/qa_json_L2b.txt`.
- Pendências achadas (fora do escopo): Mergulho termina e Emersao começa com a Raiz em −0,35 (salto de 0,35 se emendar com o Nado; proposta: profundidade pelo jogo); sola do Andar 0,19 e da Corrida 1,0 studs/s no fim do apoio (osso em 0). Roblox, celular e física sem teste.
- **Lote 2 (com L2b) aprovado pelo usuário em 03/11/2026** ("Aprovo, Lote 3").

**03/11/2026 — Lote 3 (reações e vida). Aguardando aprovação; Lote 4 não iniciado.**
- Versão L2b preservada em `versao_L2b/`. Rig e GLB **não mudaram**; 29 JSON em `clipes/` (28 ossos, iguais ao GLB); os 21 anteriores estão idênticos à L2b.
- 8 clipes novos: ReacaoGolpe (0,8 s), Morte/incapacitação visual (2,4 s, fica no último quadro), Comer (3,0 s), Deitar (2,0 s), DescansoDeitado (6,0 s, laço), Levantar (1,8 s), Observar (4,0 s), Alerta (2,5 s). GuardarNinho continua proposta.
- Técnica: patas plantadas (IK 0, pé não escorrega); Deitar desce a frente primeiro e depois o quadril, abre as dianteiras 0,35 com um passo curto (o cotovelo D entrava 0,05 no chão) e pousa o queixo; Levantar faz o inverso e devolve as patas sob o ombro. Transições saem/chegam no quadro 0 do Repouso (emenda 0,4°) e do DescansoDeitado (0,5°). Eventos visuais no bloco `sincronizacao` (ex.: Comer abocanha 0,62 s, engole 1,25 s).
- Correção achada no render: a Mandibula é filha do Pescoco2 (não da Cabeca); girar só a Cabeca cruzava os dentes. Nos clipes do Lote 3 a mandíbula gira junto (`soma_cab`); clipes anteriores não foram mexidos.
- QA de contato com o chão (malha deformada, `scripts/qa_malha_chao.py`, z = 0): corpo ≥ 0,04, cauda ≥ 0,13, cabeça/focinho ≥ −0,003 (queixo apoiado), pernas ≥ 0,009. Pés: −0,21 a −0,23 na ponta da traseira D, **igual ao Repouso aprovado (−0,21) e ao Andar (−0,27)** — pendência antiga da malha, não do Lote 3.
- Evidências: `review/L3/` — `clipes/` (folhas e GIFs lado/3-4 normal e lento; cabeça para ReacaoGolpe, Comer, Observar, Alerta, Morte; patas para Deitar/Levantar/Descanso, 3 ciclos), `PRANCHA_ref_x_L3.png`, `qa_chao_L3.txt/.json`, `qa_transicoes_L3.txt`, `qa_json_L3.txt`, `geracao_L3.txt`.
- Limites: Morte é só visual (sem regra de morte, ragdoll ou física); ReacaoGolpe só de frente; Alerta não tem laço (proposta); Roblox, celular e FPS sem teste.

**04/11/2026 — Lote 4 (montaria, só apresentação no Blender). Aprovado pelo usuário em 04/11/2026 ("Aprovar Lote 4").**
- A aprovação vale para a apresentação no Blender. Sela, lado de montar, mergulho montado e a integração no Roblox continuam pendentes.
- Versão L3 preservada em `versao_L3/` (Anim.blend, clipes, scripts, md5 do GLB/rig). Rig e GLB **não mudaram**; agora 31 JSON (28 ossos, iguais ao GLB); os 29 anteriores estão idênticos.
- Encaixe (`scripts/encaixe_l4.py`, `scripts/manequim_r15.py`): manequim de teste com proporções aproximadas do R15 em bloco (altura 5,2, quadril 2,0) — **não é rig R15 validado**. O dorso fica a ~5,5 studs (acima da cabeça do manequim em pé). As cristas grandes do ombro ficam em y −7 a −9; o assento foi posto em y −4,6 (perto do pivô de giro, y −4,2), atrás delas, e o volume `TESTE_Sela_PROPOSTA` (2,4 × 2,3, 0,22 de espessura, preso ao osso Coluna1) cobre as cristas menores do dorso. Sem a sela o manequim apoia direto nas pontas das cristas. Nada da criatura foi reduzido ou deformado.
- Montar (4,0 s) e Desmontar (3,6 s): clipes do crocodilo (baixa 0,20 com patas plantadas, IK 0; rola 1,5° para o lado do apoio; cabeça acompanha; amortece ao sentar). Cavaleiro de demonstração: chega pela esquerda, mãos espalmadas no flanco, pé E no cotovelo, pé D atrás do cotovelo, mãos na borda do dorso, perna D passa por cima da garupa e senta; Desmontar faz outro caminho (perna D volta pela garupa, desce de frente para o flanco segurando a borda e solta perto do chão). Emenda com o Repouso 0,4°; maior passo do quadril na sequência inteira 0,23 stud por quadro (sem teleporte).
- Folgas medidas (caixa do manequim × pele, negativa = entra): corpo e membros ≥ −0,18 em 5 de 121 quadros (Montar) e ≥ −0,15 em 4 de 109 quadros (Desmontar); mãos/pés de apoio até −0,26 em quadros de troca de apoio. Sentado: −0,06 (canela no dorso) e −0,13 no volume da sela. Reutilização: Repouso, Andar, Corrida, VirarE/D, NadoParado, Nado, CurvaAquáticaE/D em 3 ciclos com o cavaleiro preso ao osso — deriva 0, nenhuma parte abaixo de −0,07 da pele; nenhuma variante Montado* foi necessária.
- Água de teste (só superfície): no nado o quadril fica 2,1 acima da linha d'água e a base do tronco 2,5; na entrada pela margem o tronco fica ≥ 1,57 e o pé toca a água (−0,02); na saída o tronco fica ≥ 1,97. **Não é teste de respiração, flutuação nem física do Roblox.** Mergulho/Emersão montados não foram feitos.
- Evidências: `review/L4/` — `PRANCHA_ref_x_L3_x_L4.png`, `PRANCHA_encaixe_L4.png`, `encaixe/`, `demo/` (Montar/Desmontar em lado, 3/4, frente, topo, subida e flanco; GIF normal e lento), `seq/` (Repouso → Montar → montado → Desmontar → Repouso), `reuso/` (GIFs de 3 ciclos), `agua/` (entrada/saída), `RESUMO_L4.txt`, `qa_demo_L4.json`, `qa_transicoes_L4.txt`, `qa_json_L4.txt`, `qa_chao_L4.txt`. Cena: `CR_Crocodilo_Montaria_Teste.blend`.
- Limites: manequim em caixas de 1 stud (membros R15 reais são mais finos, e a animação final do personagem será outra); sela e lado de montar não são definição; sem controles, câmera, física, autoridade do servidor, regra de queda em combate; Roblox, celular e FPS sem teste. Herdados e não corrigidos: ponta do pé traseiro D −0,21 (Repouso), cotovelo D a −0,005 do chão na pose baixa, resíduos de sola e da Raiz na emenda Mergulho/Emersao↔Nado (L2b), reação a golpe só frontal.

**04/11/2026 — correção: dentes rangendo/colidindo com o crocodilo em movimento (pedido do usuário).**
- **Correção aprovada pelo usuário em 04/11/2026** ("Aprovar correção"). Lote 4 (montaria) aprovado em seguida, no mesmo dia.
- Causa: a Mandibula é filha do Pescoco2, não da Cabeca. Em todos os clipes a cabeça girava (até 2° no Repouso, 7,3° nas viradas) e a mandíbula ficava para trás: os dentes raspavam de lado (até 7,3°, VirarE/D), o queixo deslizava até 0,65 stud em relação à cabeça e Arrancada, Mergulho e Mordida fechavam até 5° além do fechado (arcadas cruzando). O ajuste do Lote 3 (`soma_cab`) só cobria parte dos clipes novos.
- Correção em `scripts/anim_crocodilo.py` (`mandibula_segue_cabeca`): na amostragem de cada quadro a mandíbula recebe o mesmo giro da cabeça em torno do pivô da cabeça (mordida rígida); abrir/fechar vale em relação à cabeça e nunca passa do fechado aprovado (100%). Rig, malha e GLB **não mudaram**.
- Medição (`scripts/qa_boca_relativa.py`, `review/boca_mov/qa_boca_antes.txt` × `qa_boca_depois.txt`): nos 31 clipes o desvio lateral caiu para ≤ 0,07° (resíduo da pose de descanso), o deslizamento do queixo para 0,000 e nenhum clipe fecha além do fechado.
- Regressão: nos 31 JSON só o canal da Mandibula mudou (quadros e sincronização iguais); 28 ossos iguais ao GLB; emendas com os mesmos ângulos; contato do focinho com o chão igual ou melhor (Deitar/Descanso/Levantar −0,003 → +0,019). Mergulho continua com o focinho abaixo de z 0, como antes (é clipe de água). A cena `CR_Crocodilo_Montaria_Teste.blend` foi regenerada sem mudança nas medidas do cavaleiro.
- Efeito visível: com a boca fechada os dentes de cima ficam por fora, como no estado "fechada 100%" aprovado no Lote 1. Na Mordida/Ameaça a abertura agora é exatamente a da mandíbula (máx. +12°), sem o giro extra da cabeça. Versão anterior em `versao_L4/`. Prancha: `review/boca_mov/PRANCHA_boca_antes_depois.png`; GIFs de cabeça em `review/boca_mov/antes|depois/`. Roblox não testado.

**05/11/2026 — Lote 5 (montaria): sela definitiva e subida/descida pelos dois lados. Aprovado pelo usuário em 06/11/2026 ("Aprovar Lote 5").**
- A aprovação vale para a forma da sela e os clipes no Blender. Textura em atlas, GLB da sela, integração no Roblox e mergulho montado continuam pendentes.
- Decisões do usuário (05/11): sela definitiva no Blender; o jogador sobe e desce **pelos dois lados**; mergulho montado **continua pendente**.
- Sela (`scripts/sela_crocodilo.py`, malha `CR_Croc_Sela`, 5.824 tris, 2.934 vértices): manta de tecido verde-musgo com debrum ocre (passa lisa por cima das cristas no meio e cai como pano na borda), aba de couro escuro, assento de couro com cabeça (frente) e patilha (atrás), alça de bronze na cabeça para a mão, cilha de couro em volta da barriga em y −3,95 com argolas de bronze nos dois lados, e **apoios de pé** de couro com alça de bronze nos dois lados. Não há estribo pendurado: o dorso é largo e as pernas do R15 são curtas, então o estribo ficaria solto no ar sem cavaleiro. O corpo do Meshy não é simétrico: o apoio direito é mais alto (0,48 contra 0,21). Pesos copiados da pele (média suave, até 4 ossos, incluindo as patas, porque a pele do ombro se mexe com elas). Rig, malha do crocodilo, escala e GLB **não mudaram**. Cena: `CR_Crocodilo_Sela.blend`.
- Folga sela × pele, quadro a quadro, nos 33 clipes (`scripts/qa_sela_clipes.py`): em terra ≥ −0,04 em todos. Nos clipes de água a cilha chega a −0,11/−0,13 (Nado, CurvaAquáticaE/D, Emersão) sob a pata dianteira recolhida; EntradaAgua −0,07, SaidaAgua −0,08. Cilha mais atrás (y −3,8) batia na coxa traseira direita.
- Clipes novos: `MontarDireita` (4,0 s) e `DesmontarDireita` (3,6 s), espelhos de Montar/Desmontar (rolagem, olhar e cauda para −X). Montar/Desmontar continuam sendo o lado esquerdo, sem mudança. Agora 33 JSON; os 31 anteriores estão **idênticos** (md5 em `versao_L4b/md5_clipes.txt`); no manifesto só entraram as 2 linhas novas.
- Cavaleiro de demonstração (`scripts/demo_montaria_l5.py`; base: demo do Lote 4 sem reescrever trajetórias): o lado direito é calculado num mundo espelhado em X e devolvido ao mundo real com esquerda↔direita trocados; os apoios são medidos na pele e na sela reais. Ajustes do lado direito: pontos do braço 0,3 para dentro (a pata dianteira D é mais fechada), descida em y −4,1 e 0,6 mais longe do corpo (o joelho traseiro D abre até x 4,1). Mãos apoiadas na manta usam a normal da pele.
- Folgas (manequim × pele; apoio = mãos/pés): Montar E corpo −0,18 / apoio −0,26 (iguais ao Lote 4); Desmontar E −0,15 / −0,25; MontarDireita −0,15 / −0,30 (1 quadro de pé de apoio no cotovelo); DesmontarDireita −0,11 / −0,03. Cavaleiro × sela: sentado −0,13 (coxa na lateral do assento), até −0,20 quando a perna passa sobre a sela. Reutilização (Repouso, Andar, Corrida, VirarE/D, NadoParado, Nado, CurvaAquáticaE/D, 3 ciclos): deriva 0, corpo ≥ −0,12 da pele, ≥ −0,15 da sela. Sequências Repouso → Montar → montado → Desmontar → Repouso dos dois lados: maior passo do quadril 0,23 stud por quadro.
- Evidências: `review/L5/` — `PRANCHA_sela_forma.png`, `PRANCHA_dois_lados.png`, `forma/`, `demo/` (folhas e GIFs dos 4 clipes), `seq/`, `reuso/`, `qa3/`, `qa_sela_clipes.txt`, `qa_demo_L5.json`, `RESUMO_L5.txt`. Cena: `CR_Crocodilo_Montaria_L5.blend`. Versão aprovada do Lote 4 em `versao_L4b/`.
- Limites: sela com materiais procedurais do Blender (5 materiais) — falta assar textura em um atlas e exportar o GLB da sela para o Roblox (só após aprovação da forma); manequim em caixas (R15 real é mais fino); sem controles, câmera, física, regra de lado no jogo; Roblox, celular e FPS sem teste; mergulho montado pendente.

**06/11/2026 — Lote 5b: textura em atlas e GLB da sela (só Blender). Aprovado pelo usuário em 06/11/2026 ("Aprovar e commitar").**
- `scripts/exportar_sela.py` (sobre `CR_Crocodilo_Sela.blend`): UV novo em atlas único (margem ~4 px) e os 5 materiais procedurais assados em 4 mapas 1024 num material só (`M_Sela_Atlas`): `tex/CR_Sela_cor_1024.png`, `_normal_1024`, `_rugosidade_1024`, `_metal_1024`. A cor é assada pela emissão (o passe difuso do Cycles deixava o bronze preto).
- `export/CR_Crocodilo_Sela.glb` (2,0 MB): só o esqueleto do crocodilo (mesmos 28 ossos, rig sem mudança) + a malha da sela (5.824 tris), sem animação. O GLB do crocodilo **não mudou** (md5 conferido).
- Conferência por reimportação: 1 malha no arquivo (a "Icosphere" que aparece é o desenho de osso criado pelo importador do Blender), 28 juntas, até 4 influências, ossos com peso: Pelve, Coluna1/2, Pescoço, BraçoE/D, CoxaE/D, Cauda1; medidas 5,74 × 3,39 × 5,84. Numa pose de teste (Pelve, Coluna1, Coluna2 e BraçoE girados) a sela reimportada fica a no máximo 0,000002 da original.
- No jogo: a sela entra como MeshPart DENTRO do modelo do crocodilo e usa os ossos dele (o Roblox liga a pele pelo nome do osso); os ossos que a sela não usa somem ao importar o GLB da sela, sem efeito. Importação (Import 3D) é manual; **Roblox não testado**.
- Evidências: `review/L5/PRANCHA_atlas.png` (procedural × atlas), `review/L5/atlas/`, `export/CR_Crocodilo_Sela_conferencia.json`. Cena de revisão: `CR_Crocodilo_Sela_Atlas.blend`.

**06/11/2026 — Lote 5c: materiais da sela pelos do Pântano Nebuloso (pedido do usuário). Aprovado pelo usuário em 06/11/2026 ("Aprovar e commitar").**
- Motivo: a sela aprovada usava materiais genéricos (bronze, que não é material básico, e manta de feltro tingido), fora da regra de materiais por bioma/fauna (RPG_01 25.3.1, 25.10, 25.22.7; base de peças em `DOCS/equipamentos/sela-dragoes.md`, que é [PROPOSTA] e feita para os dragões).
- Agora: assento, aba, cilha e apoios em couro de **Javali-do-Brejo** (escuro, lamacento); manta trançada de **Fibra de Mangue** (material estrutural oficial do bioma); argolas e alças dos pés em **ferro** escurecido com ferrugem (sem bronze); borda do arção em madeira de **Mangue Cinzento** na cabeça e na patilha; alça da mão em couro trançado com **tendão de Javali-do-Brejo**. Os nomes da fauna (Couro/Tendão de Javali-do-Brejo) são [PROPOSTA] da ficha de fauna.
- Adorno regional: Pena de Garça foi testada e **retirada** (as penas pareciam presas/espinhos saindo da sela). Fica [PENDENTE]; o material especial (Essência do Brejo) não tem visual definido.
- Forma, encaixe e pesos iguais aos do Lote 5. Peças novas só na borda de madeira (6.156 tris no GLB, antes 5.824). Medições refeitas iguais: sela × pele nos 33 clipes (terra ≥ −0,04; cilha −0,11/−0,13 nos clipes de água, como antes) e cavaleiro dos dois lados com os mesmos números do Lote 5.
- Atlas e GLB refeitos: `export/CR_Crocodilo_Sela.glb` (2,3 MB, 28 ossos, 1 malha, até 4 influências, pose de teste com diferença ≤ 0,000002); GLB do crocodilo sem mudança (md5). Versão anterior (aprovada) em `versao_L5b/`.
- Evidências: `review/L5c/PRANCHA_atual_x_pantano.png`, `review/L5c/forma/`, `review/L5c/atlas/`, `qa_sela_clipes.txt`, `qa_demo_L5c.json`. Roblox não testado.

**11/11/2026 — Lote R1 (comportamento real): postura de crocodilo de verdade. Aprovado pelo usuário em 11/11/2026 ("Aprovar e commitar").**
- Base: `DOCS/criaturas/crocodilo-primordial-referencias-reais.md` (pesquisa com fontes). Versão anterior preservada em `versao_L5c/` (clipes, Anim.blend, cena de montaria, script, md5).
- **Cauda arrastando** (`cauda_no_chao` em `scripts/anim_crocodilo.py`): na caminhada alta real a base da cauda sai do chão e a metade de trás vai encostada. Antes a cauda inteira ficava suspensa a 0,8–1,2 do chão. Agora, em todos os clipes de terra, Cauda4 a Cauda8 levam a pele ao chão e a Cauda3 desce até a metade; a onda lateral continua (a cauda varre o chão). Na água fica desligado; em EntradaAgua/SaidaAgua acompanha a troca das patas. Medido: cauda a 0,001–0,017 do chão em todos os 30 clipes de terra (encosta, não atravessa).
- Só os canais Cauda3–8 mudaram nos clipes de terra (quadros, sincronização e demais ossos iguais); Nado, CurvaAquáticaE/D, Mergulho e Emersão estão **idênticos** (md5). Emendas com os mesmos ângulos (diferença ≤ 0,1°), dentes iguais (lateral ≤ 0,07°, deslize ≤ 0,07), sela × pele igual ao Lote 5c, cavaleiro dos dois lados igual.
- **DeitadoBocaAberta** (novo, laço 6 s): *gaping* ao sol/calor — a mandíbula fica no chão e o **crânio sobe** a abertura máxima aprovada (+26°); queixo a 0,021 do chão. Emenda com DescansoDeitado por cruzamento curto.
- **NadoParado** refeito e **CurvaLentaEsquerda/Direita** (novos, 3 s, giro proposto 12°/s): devagar, patas abertas guiando; as traseiras remam alternadas (puxada para trás aberta, volta recolhida), na curva a traseira de fora rema mais forte e a dianteira de dentro segura. As CurvaAquática rápidas continuam com as patas recolhidas (correto para nado rápido). IK 0.
- Repouso padrão: o real fica deitado de barriga em terra. Os clipes já existem (Deitar → DescansoDeitado/DeitadoBocaAberta → Levantar); o "Repouso em pé" fica como pose de alerta/transição. **Quem escolhe deitar é a IA** (não existe ainda) — anotado para quando for feita.
- Agora 36 JSON. Evidências: `review/R1/` (antes × depois, `qa_chao_R1.txt`, `qa_transicoes_R1.txt`, `qa_sela_clipes.txt`, `qa_demo_R1.json`, `geracao_R1.txt`). Roblox não testado.

**11/11/2026 — Lote R2 (comportamento real): caça. Aprovado pelo usuário em 11/11/2026 ("Aprovar e commitar"). Só animação.**
- 8 clipes novos em `scripts/anim_crocodilo.py` (44 JSON; os 36 anteriores **idênticos**, md5 em `versao_R1/`):
  - **Espreita** (laço 6 s, água): imóvel, patas abertas e soltas, cabeça nivelada; o jogo deixa só olhos, narinas e cristas fora d'água.
  - **AproximacaoSubmersa** (laço 3 s, água): patas coladas, cauda em onda longa e baixa, corpo e cabeça estáveis (silencioso).
  - **BoteAquatico** (1,6 s, água): afunda e encolhe a cauda → chicotada lança o corpo para cima/frente (até 1,5 de altura e 1,2 à frente no clipe) com a **cabeça virada de lado** e a boca toda aberta → fecha de estalo no alto (0,62 s) → volta para a água segurando.
  - **MordidaLateralEsquerda/Direita** (1,0 s, terra): vira para o lado oposto e abre, varre a cabeça de lado e fecha no meio da varrida.
  - **ArrastarPresa** (laço 1,8 s): anda de ré (ciclo do Andar invertido, 0,79 studs/s para trás), cabeça baixa, boca travada, dois puxões de cabeça por ciclo; cauda arrasta.
  - **Engolir** (2,2 s): ergue a cabeça e dá dois trancos para trás com a boca entreaberta (o pedaço escorrega).
  - **RolarDaMorte** (laço 1,2 s = 1 volta): gira o corpo inteiro no eixo longo (eixo no meio do tronco, não na sola), patas coladas, cauda dobrada de lado, boca travada. **Só animação**: agarrão, dano, regra PvP e se vira habilidade continuam decisão do criador.
- QA: IK 0 nos 8; terra com cauda a 0,016–0,017 do chão e focinho ≥ 1,3 (mordidas), pés iguais ao Andar (−0,25, pendência antiga); dentes sem cruzar (lateral ≤ 0,07°, deslize 0). Alturas de água nos renders são **de teste**.
- Evidências: `review/R2/` (folhas e GIFs por clipe, `qa_chao_R2.txt`, `geracao_R2.txt`). Roblox não testado.

**11/11/2026 — Lote R3 (comportamento real): sinais. Aprovado pelo usuário em 11/11/2026 ("Aprovar e commitar"). Só animação.**
- 3 clipes novos (47 JSON; os 44 anteriores **idênticos**, md5 em `versao_R2/`):
  - **AmeacaInflada** (2,6 s, terra): ergue-se alto nas patas, arqueia o tronco, cabeça alta de boca toda aberta (sibilo, tremor), cauda chicoteando; termina com **bote curto** de estalo (0,45 à frente) e volta ao Repouso. O rig não tem canal de escala (JSON = rotação + posição): o "inflar" aparece pela postura.
  - **BatidaDeCabeca** (2,6 s, água): postura cabeça-e-cauda-para-fora (HOTA), ergue a cabeça de boca entreaberta e bate a parte de baixo na superfície fechando de estalo (evento em 1,2 s para som/respingo), quica e relaxa.
  - **Bramido** (4,0 s, água): HOTA com o dorso arqueado; **vibração** do tronco de 0,8 a 2,1 s (no jogo: gotas "dançando" sobre o dorso como VFX, desempenho a medir) e depois brame de boca meio aberta com a cabeça subindo.
- QA: IK ≤ 0,013 (o bote curto foi limitado a 0,45 porque 0,8 esticava a traseira E plantada, IK 0,14); AmeacaInflada com cauda a 0,015 do chão e pés iguais ao Repouso; dentes sem cruzar (lateral ≤ 0,07°, deslize 0).
- Evidências: `review/R3/` (folhas, GIFs normal e lento, `qa_chao_R3.txt`, `geracao_R3.txt`). Roblox não testado.

**11/11/2026 — Lote R4 (comportamento real): margem. Aprovado pelo usuário em 11/11/2026 ("Aprovar e commitar"). Só animação.**
- 2 clipes novos (49 JSON; os 47 anteriores **idênticos**, md5 em `versao_R3/`):
  - **FugaDeBarriga** (laço 0,8 s, 3,64 studs/s): barriga raspando o chão (0,011), patas bem abertas para os lados empurrando em pares diagonais rápidos, tronco em S forte, cabeça baixa; a cauda arrasta varrendo. Pé apoiado sem escorregar (0,0).
  - **EscorregarBarranco** (laço 1,2 s): de barriga (0,016 do chão), patas arrastadas para trás com a sola para cima (não fincam), cauda varrendo forte de lado a lado; a descida pela rampa é do jogo.
- QA: IK 0; cauda a 0,016 do chão; dentes sem cruzar (lateral 0,04°, deslize 0). Pés da Fuga −0,23, igual à pendência antiga do Andar.
- Com o R4, o plano de comportamento real (R1–R4) está completo. Evidências: `review/R4/`. Roblox não testado.

**15/11/2026 — Piloto no Studio (place de teste RBX Crocodilo = `Documents/RPG_Roblox/BACKUPS/Crocodilo-testes.rbxl`, local) + protótipos de poderes [PROPOSTA]. Entregue; animações APROVADAS pelo usuário 15/11 (vídeo review/video_1511/Crocodilo_50_animacoes_Studio.mp4). Poderes seguem [PROPOSTA].**
- Place confirmado pelo usuário. Cópia antes de mexer: `Crocodilo-testes_ANTES_import_2026-11-15.rbxl`. A pedido do usuário ("limpe o backup para ficar sem lags") saíram os backups do ServerStorage (~1,13 M instâncias); as animações dos dragões foram para `ServerStorage.Dragoes_Fora_do_Teste` e os 4 scripts de servidor dos dragões ficaram desligados (atributo `DesligadoPeloTesteCrocodilo`) — reversível; o Play com 4,5 M instâncias travava o Studio.
- Import 3D (manual, usuário): `Workspace.Teste_Crocodilo.Crocodilo_Primordial` — 28 ossos com nomes e hierarquia do Blender, 1 MeshPart com SurfaceAppearance (cor, normal, rugosidade, metal), AnimationController; 10,1 × 5,7 × 32,0 studs (altura no ombro ~5,7, comprimento 32,0: dentro de 5–7 e 24–32, no limite superior).
- Convenção dos ossos **medida**: "giro180y" (6 poses × 3 pontos, erro 0,0014 stud; sem conversão 9,42). Adaptador próprio `studio/AdaptadorCrocodilo.luau` (sem a ponte dos dragões), dados por `studio/Crocodilo_Piloto.rbxmx` (empacotador `studio/empacotar_clipes_croc.py`).
- **49 + 1 clipes** montados como KeyframeSequence (sem osso faltando; eventos viraram KeyframeMarker) e **tocados em Play** pelo Animator (id temporário do Studio, sem publicar): duração exata e pose igual ao Blender (laços ≤ 0,04°; transições ≤ 2,1° por amostrar a 0,004 s do fim). Inventário: `review/studio_1511/inventario_49_play.txt`.
- Atenções do pedido: emenda Nado↔Mergulho/Emersão na raiz 0,00° e 0,000 stud; Corrida sem escorregão (ponta do pé 0,056); **RolarDaMorte corrigido (r2)**: o polo do IK ficava no mundo e torcia a pata dianteira E até 28°/quadro na volta do laço — pernas agora presas ao corpo (≤ 0,34°). Só esse JSON mudou (md5 em `versao_R4/`).
- **Clipe novo `CaudaDeMare`** (1,5 s, água; evento `impacto_cauda` 0,56 s) — protótipo de poder; IK 0,089 nas patas boiando (torção da pelve, sem efeito visível).
- **Protótipos [PROPOSTA]** (`studio/PoderesTeste.luau` + `ConfigPoderes_Teste.luau`, valores provisórios, só bonecos `BonecoTeste`, servidor decide alvo/alcance/estado/efeitos/cancelamento): Mordida de Agarrão (terra: MordidaLateral do lado do alvo; água: desce + BoteAquatico; **sustentação provisória = ArrastarPresa — falta clipe próprio de sustentação/recuperação**), Giro Predatório (RolarDaMorte, efeito no fim de cada volta), Submersão (água: Mergulho→Espreita/Aproximação→Emersão, sempre visível; terra: Deitar→Descanso→Levantar), Cauda de Maré (varredura + empurrão no raio). Testados em Play: acerto, erro de alcance, cancelamento, alvo removido (4 instantes), crocodilo removido, reativação — `review/studio_1511/testes_poderes_play.txt`.
- **Continuam decisões do criador:** elemento, passiva, kit final, regra do agarrão PvP (protótipo bloqueado a bonecos), mergulho montado. Não testado: rede com vários jogadores, celular, desempenho com várias criaturas. Nada publicado; rpg_roblox e mapa intocados.

**16/11/2026 — P2: clipes de segurar e soltar a presa (protótipo do agarrão, só Blender). APROVADO no Blender pelo usuário em 16/11 (53 clipes).**
- Motivo: no protótipo do agarrão a sustentação usava `ArrastarPresa` (anda de ré). Crocodilo real segurando: mandíbula travada, corpo firme nas 4 patas, puxões curtos para trás, rajada de sacudidas laterais da cabeça e reajuste rápido da mordida; ao soltar abre a boca e dá um tranco da cabeça para trás.
- **`SegurarPresa`** (laço 2,0 s, terra; de MordidaLateralE/D, para SoltarPresa/RolarDaMorte), **`SoltarPresa`** (1,0 s; evento `solta` 0,12 s; do quadro 0 do SegurarPresa ao Repouso), **`SegurarPresaAgua`** (laço 2,0 s, boiando; de BoteAquatico, para RolarDaMorte/NadoParado).
- QA: IK 0,000; pés sem escorregar; boca fecha_alem 0,00° / lateral 0,07° / desloca 0,000 (igual MordidaLateral); malha × chão: pés −0,23 (igual ao Repouso), cabeça ≥ 1,45, focinho ≥ 1,60. Os 50 clipes antigos regenerados saíram **idênticos byte a byte**. Total: 53 JSON. Backup do gerador: `versao_P1/`.
- Renders: `review/p2/render/`. Studio não testado (precisa liberação para trocar ArrastarPresa por SegurarPresa no PoderesTeste). Duração do agarrão e regra PvP continuam decisão do criador.
- Uso previsto: o marcador `solta` (0,12 s) do SoltarPresa sincroniza a liberação do boneco no fim normal do agarrão; no cancelamento e na remoção do crocodilo a liberação é imediata pelo servidor (a validar no Studio).

**16/11/2026 — P2 no Studio (RBX Crocodilo, autorizado). APROVADO pelo usuário em 16/11.**
- Instalados os 3 KFS (53 animações no place); marcador `solta` do SoltarPresa caiu em 0,133 s (quadro 4; o JSON pede 0,12).
- `PoderesTeste`: sustentação = `SegurarPresa` (terra) / `SegurarPresaAgua` (água) no lugar de ArrastarPresa; fim normal toca `SoltarPresa` e o marcador libera o boneco (dano para no início do SoltarPresa); cancelar, alvo removido e crocodilo removido soltam na hora; Giro só encadeia durante a sustentação. Backup no place: `ServerStorage.PoderesTeste_ANTES_P2_2026-11-16`; cópia local antiga em `versao_P1/`.
- Testes em Play (todos ok, sem erro no console): terra e água com soltura no marcador (0,13 s após o início do SoltarPresa), cancelar na sustentação e no SoltarPresa, alvo removido, crocodilo removido (sustentação e soltura), fora do alcance, reativação imediata, Giro encadeado e Giro bloqueado na soltura. Evidência: `review/studio_1611/testes_P2_play.txt`. Place salvo (arquivo local).
- **Sustentação do agarrão: 3,5 s** (decisão do usuário 16/11, "por enquanto"; era 2,5 de teste). Aplicada no `ConfigPoderes_Teste` (place e `studio/`) e testada em Play: terra 3,52 s e água 3,50 s segurando, soltura no marcador nos dois.
- Não verificado: aparência do SoltarPresa na água (é clipe de terra tocado boiando); vários jogadores; celular. Duração do agarrão e regra PvP continuam pendentes.

**16/11/2026 — P3: vídeo dos 4 poderes + correção de altura na água (RBX Crocodilo). Entregue, aguardando avaliação.**
- Vídeo r1 (50 s, tempo real) dos protótipos: agarrão terra/água, Giro encadeado, Submersão água/terra, Cauda de Maré. Ele mostrou que no agarrão na água o crocodilo afundava 2,4 de uma vez (todo submerso segurando) e voltava num salto.
- Correção no `PoderesTeste`: mudança de altura sempre suave (`moverPivo`); agarrão na água desce só à altura de espreita (0,85, `Agarrao.profundidade_agua`) e sobe durante o SoltarPresa; cancelar/remoções voltam em 0,4 s; Giro encadeado mantém a altura. Maior salto por quadro: 2,4 → 0,07. Boneco de teste na água agora na linha d'água (presa na margem). Evidência: `review/studio_1611/testes_P3_play.txt`; vídeo r2: `review/video_poderes_1611/Crocodilo_4_poderes_Studio_r2.mp4`.
- Na água a presa presa fica pendurada abaixo da mandíbula (arrastada para dentro d'água, como o crocodilo real); ao soltar volta ao fundo de teste.

**16/11/2026 — P4 etapa 1: Submersão com água real (RBX Crocodilo). Entregue, aguardando avaliação.**
- Diagnóstico: a arena antiga tinha só uma placa de vidro em y 4,3 sobre o chão (nenhuma água de terreno), e a Submersão só trocava a pose no lugar.
- Canal novo `Workspace.Teste_Crocodilo.Canal`: água de terreno de 14, raso de 3 nas duas pontas, fundo de lodo, marcos de 10 em 10 e régua de nível.
- `PoderesTeste`: o servidor mede superfície e fundo; espreita com olhos/narinas na superfície → mergulho em 0,5 s → deslocamento real no mundo (10 studs/s de teste, 5 de energia/s) checando a profundidade à frente → emerge adiante. Raso (< 8,2) e sem água: recusa clara, sem atravessar o fundo. Terra: postura baixa separada.
- Efeitos no cliente (`CrocodiloFX_Cliente`, prévia): ondulação na entrada/saída, rastro e poucas bolhas.
- Testes em Play: fundo, beira, raso, sem água, cancelar, crocodilo removido (3x), reativação, ocupado, terra — ok. Evidência: `review/P4_1611/submersao/` (vídeo, pranchas, antes/depois, `testes_submersao_play.txt`).
- Pendente nesta tarefa: Giro de Emboscada, Agarrão, Cauda de Maré, Escamas Grossas e olhos (a malha não tem ossos de olho/pálpebra: 28 ossos, olho faz parte da malha única).

**16/11/2026 — P4b: Submersão corrigida + Giro de Emboscada + Cauda de Maré terra/água + Escamas Grossas (RBX Crocodilo). Entregue, aguardando avaliação.**
- Pedido do usuário: montado afunda mais; mais fundo; subir rápido e pegar o alvo com naturalidade; errou = continua nadando.
- Submersão: topo 4,0 abaixo da superfície (era 1,5), montado +3,5; canal com 19,6 de fundo. Emboscada: presa à frente → sobe em 0,3 s, investe pela ponta dos dentes e dá o bote (acerto a 4,65 → SegurarPresaAgua 3,5 s → SoltarPresa); errou → segue nadando e vira na beira.
- Giro de Emboscada: clipes novos `GiroSaida`/`GiroPouso` + RolarDaMorte r2 no ar; janela de 1,5 s após emergir (2,0×, +50% em distraído), raso 1,2×, senão recusa; pouso na praia derruba no raio 12.
- Cauda de Maré: clipe novo `CaudaDeMareTerra`; acerto pela trajetória real da cauda; cobertura medida ~73° × 360° propostos (decisão de design).
- Escamas Grossas: −15% (100 → 85) em terra e água; pulso curto nas escamas.
- 56 clipes (53 + GiroSaida, GiroPouso, CaudaDeMareTerra); os 53 anteriores idênticos byte a byte.
- Olhos: malha única sem ossos de olho/pálpebra → etapa própria (rig + novo Import 3D).
- Evidência: `review/P4_1611/testes_P4b_poderes_play.txt`, vídeos em `review/P4_1611/`.
- 17/11: usuário respondeu "Ok" à proposta de seguir para os olhos (P4b sem novos ajustes pedidos).

**17/11/2026 — O1: olhos (só Blender). APROVADO ("Aprovar e levar", 17/11).**
- Antes: olho só pintado na textura (~0,25 × 0,14 stud), sem geometria nem osso; cabeça do Meshy levemente assimétrica (olho E x 0,94, D x −0,56).
- `scripts/olhos_crocodilo.py` → `CR_Crocodilo_Rig_Olhos.blend` (cópia; `CR_Crocodilo_Rig.blend` intacto, cópia em `versao_O0/`):
  - globo ocular (calota, sai 0,055 da pele) preso a `OlhoE/OlhoD`; o olhar gira o globo (testado ±20°, sem mostrar a borda);
  - pálpebras superior/inferior com borda em amêndoa, presas a `PalpebraSupE/InfE/SupD/InfD` (filhos de Cabeca). Fechar = Sup −22°, Inf +17° no X do osso;
  - íris âmbar com pupila vertical pintada na área livre da UV (texturas novas `tex/*_olhos_2048.png`; originais intactas); pele das pálpebras com UV contínua da pele vizinha.
  - Malha 19.877 tris (+884, limite 20.000), 34 ossos (28 originais sem mudança de nome, posição ou peso).
- Pele em volta dos olhos 98–100% no osso Cabeca → o olho acompanha a cabeça em todos os clipes.
- Clipes: os 56 de corpo **não gravam** ossos de olho (regenerados com o rig novo: 56 idênticos byte a byte). 3 clipes novos só de pálpebras, para tocar por cima: `Piscar` (0,30 s), `PiscarLento` (0,70 s), `FecharOlhosAgua` (0,80 s: fecha em 0,07, segura, reabre em 0,45). Olhar fica para script do jogo. Total 59 clipes.
- Demo (só revisão): piscadas irregulares, olho vira antes da cabeça e volta conforme ela chega, fixação com micro-sacadas, fechamento ao entrar na água. Evidência: `review/O1_1711/` (`PRANCHA_antes_x_O1.png`, `demo_olhos_O1.gif`, `folha_demo.png`).
- Usuário: "Aprovar e levar" (17/11).

**17/11/2026 — O1 no Studio (Crocodilo-testes). APROVADO pelo usuário em 17/11/2026 ("Aprovar").**
- `export/CR_Crocodilo_Primordial_Olhos.glb` (34 ossos, 19.877 tris, texturas 1024) importado pelo usuário; modelo trocado (antigo em `ServerStorage.Crocodilo_Primordial_ANTES_O1_2026-11-17`), posição idêntica; 59 KFS remontados (antigos em `Animacoes_ANTES_O1`). Backup do place: `BACKUPS/Crocodilo-testes_ANTES_O1_2026-11-17.rbxl`.
- `AdaptadorCrocodilo`: osso que o clipe não grava não entra na pose (clipe de corpo não trava os olhos; Piscar não trava o corpo).
- `OlhosCrocodilo_Cliente` (LocalScript, só visual) [PROPOSTA]: piscada irregular (2,5–7 s, às vezes dupla), olhar no alvo (atributo `AlvoOlhar` do servidor ou boneco/jogador mais perto no campo de visão) com micro-sacadas e olhadas de lado sem alvo, olho guia a cabeça, fecha ao `Submerso`.
- Lição: o Animator devolve ao repouso, a cada quadro, os ossos sem clipe → ajustar `Bone.Transform` em `RunService.PreSimulation` (no RenderStepped era zerado).
- Testes em Play: corpo igual ao Blender (0,028°); 5 piscadas em 12 s, fecha 22°; olho segue o alvo com erro 0,5–1,4° antes da cabeça virar; alvo à frente = os dois olhos convergem (cone 110°, sem alternar); mergulho fecha em 0,07 s e reabre até 0,82 s.
- Evidência: `review/O1_1711/Crocodilo_O1_Olhos_Studio.mp4`, `folha_video_studio.jpg`, `testes_O1_studio_play.txt`.
- Não testado: celular, vários jogadores, câmera montada. No ângulo de jogo o olho quase não aparece (é pequeno).

**19/11/2026 — O2: olhar definido pelo servidor nos poderes (Crocodilo-testes). APROVADO pelo usuário em 19/11/2026 ("Aprovar").**
- `studio/PoderesTeste.luau`: `olharPara` / `seguirOlhar` (atributo `AlvoOlhar`, 10 Hz) — Emboscada: fixa a presa no instante da detecção; Agarrão: alvo do bote e, depois, o preso; Giro (encadeado): o preso; Giro de Emboscada: ponto de pouso (chão + 1). `cancelar` limpa o atributo (o cliente volta a escolher sozinho). Só visual; dano, alcance e decisões inalterados.
- Aplicado por patch com âncoras únicas, compilação conferida; backup `ServerStorage.PoderesTeste_ANTES_O2_2026-11-19`. Place salvo. O arquivo local foi igualado ao do Studio (33.676 bytes).
- Testes em Play (servidor): emboscada no canal → `AlvoOlhar` na presa aos 4,1 s (detecção), segue o boneco no bote, no contato e nos 3,5 s de sustentação, volta a nil no fim; agarrão em terra + Giro encadeado → alvo preso o tempo todo, nil no fim; Giro de Emboscada (raso, z −522) → (−300, 22, −550) = centro do pouso desde o início, nil no fim (8,35 s).
- Cliente: com o preso na boca o alvo fica a 58–105° do eixo de cada olho; os dois globos giram até o limite de 22° na direção dele (o crocodilo não consegue "olhar" para dentro da própria boca) — comportamento esperado.
- Não testado: vídeo, celular, vários jogadores.

**20/11/2026 — Regras do Lobo Ancestral adotadas no crocodilo (usuário: "verifique as regras que passei ao lobo ancestral, e faça da mesma maneira"). APROVADO ("Aprovar e commitar", 20/11).**
- Fonte: chat do Lobo Ancestral (pedido de 19/11 "golpes por porte, queda e finalização" + última mensagem "arrume a finalização e a hitbox... bata diretamente no oponente... ao finalizar, puxe... morda e estrangule; isso para o lobo, para outras criaturas seria outra finalização") e o contrato `BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/kit/CONTRATO-CONTROLE-PORTE.md` (linha do crocodilo: comprimento 28 → 11,2 = grande, Força 60, "não somar agarrão e queda").
- **Finalização do crocodilo = MORDIDA ESMAGADORA** (escolha do usuário 20/11): sibilo anunciado 0,9 s → aproxima andando → prende a cabeça/pescoço do caído → aperta sacudindo 1,8 s → selvagem morre; criatura de jogador é retirada (refúgio simulado, Vida mantida); humano nunca. Cancela sem dano se o alvo levantar antes de ser preso, for removido, ou se o crocodilo for ferido. **Preso na boca o alvo não consegue levantar** (a queda dura até o desfecho).
- **Hitbox de contato:** agarrão/bote medidos dos dentes até a **superfície** do corpo (cápsulas nos ossos; sem ossos, caixa das partes), tolerância 1,5; Cauda de Maré precisa tocar o corpo (1,0); impacto do Giro de Emboscada até a superfície. Antes: alcance 6,5 até o **centro**.
- **Controle por porte** (`ConfigPoderes_Teste.Controle`, [A TESTAR]): rolagem por golpe válido (base × impacto × porte relativo × Força relativa), lentidão/claudicação/queda (`Caido`/`CaidoAte`, nunca `Incapacitado` numa queda recuperável), ≥ 4 s de pé entre quedas, colossal metade, PvP x0,5 e imunidade. Giro de Emboscada derruba sempre (v6.2) com duração 1,5 × porte; Cauda de Maré impacto 1,2 (só lento/manca); agarrão não derruba.
- **IA:** uma decisão por queda: FINALIZAR / POUPAR / APROVEITA, com motivo (`DecisaoQueda`); crocodilo de dono nunca finaliza sozinho; alvo > 35% = aproveita; própria vida < 30%, alvo longe ou outro inimigo a < 25 = poupa.
- Backups `ServerStorage.*_ANTES_RegrasLobo_2026-11-20`; place salvo; local = Studio (hash).
- **Testes (Play):** mordida em boneco a 3,6 e 7,8 da superfície → erra (antes acertava pelo centro); encostado → acerta (0,00). Cauda acerta a 0,80 da superfície e rola lento. Frequência da Cauda (400 sorteios): pequeno M42/L58, médio M34/L66, grande (Leão sim.) M24/L57, colossal (Dragão sim.) M6/L11 (nada 83%). Giro de Emboscada: queda 1,50 s; alvo forte → APROVEITA; alvo 30% → FINALIZAR → **cancela (alvo levantou)**. Com queda-base de 3 s: selvagem morre (Boneco e crocodilo jovem, mordido no **Pescoco**); criatura de jogador RETIRADA (Vida 30 mantida); crocodilo ferido no aperto → solta sem dano; alvo levanta no sibilo → cancela; humano e alvo forte → recusados. Vídeo `review/regras_lobo_2011/Crocodilo_MordidaEsmagadora.mp4` (8,5 s).
- **20/11 r2 — Mordida esmagadora corrigida (usuário: "não faz sentido o crocodilo girar; morda, segure a criatura de maneira correta, o seu corpo e não o vento, e para finalizar mexa a boca para cravar mais os dentes"). Aguarda avaliação.**
  - **Clipe novo `MordidaEsmagadora`** (Blender, `scripts/anim_crocodilo.py`; 1,8 s, 55 quadros, IK 0, pés sem escorregar): parte da pose de segurar, **abaixa a cabeça até o corpo da presa** (Pescoço +7°, Pescoço2 +3°, Cabeça +3°) e dá **2 re-mordidas** (a boca abre um pouco e trava mais fundo, a cabeça pressiona e torce de leve, o tronco empurra para a frente); eventos `crava1` 0,49 s e `crava2` 1,24 s. **O corpo fica parado** (sem girar). Montado no Studio (61 clipes; Dados_Clipes atualizado).
  - **Servidor:** removido o giro do corpo; aproxima (de ré com `ArrastarPresa` quando a presa ficou sob o pescoço) até os dentes ficarem sobre o corpo na altura do ponto mordido; **prende o corpo** (o ponto mordido fica nos dentes, como no agarrão); toca SegurarPresa → MordidaEsmagadora; dano 5 em cada cravada; ao terminar, larga o corpo onde caiu. Backups `ServerStorage.*_ANTES_MordidaR2_2026-11-20`; place salvo; local = Studio (hash).
  - **Teste (Play):** antes os dentes ficavam **1,4 stud acima do corpo** (mordendo o ar). Agora: dentes a **0,05 e 0,06** da superfície nas cravadas (mediana 0,09 enquanto preso); **giro do corpo 0°**; presa selvagem morre no fim. Vídeo `review/regras_lobo_2011/Crocodilo_MordidaEsmagadora_r2.mp4` (aberto + de perto).
  - Limitações: a presa caída não tem animação própria (fica no Repouso); a tomada de perto ficou com o corpo do crocodilo grande no quadro.
- **Achados para decisão:** (1) a queda do Giro de Emboscada (1,5 s, v6.2) é mais curta que sibilo + aproximação (~1,4 s + 1,8 s de aperto), então a finalização natural depois do Giro não acontece — o mesmo achado do Lobo no PvP. **→ Decisão do usuário 20/11: queda do Giro de Emboscada = 3 s** (`GiroEmboscada.derruba = 3.0`; backup `ConfigPoderes_Teste_ANTES_QuedaGiro3s_2026-11-20`). A aproximação também foi corrigida: depois do Giro o alvo fica sob o pescoço, então o corpo agora recua/avança até a ponta dos dentes chegar ao ponto (antes só andava para a frente e se afastava). Teste: selvagem fraco → Giro → queda 3,0 s → FINALIZAR → prendeu aos 4,23 s → morreu aos 6,02 s; alvo forte → APROVEITA; **criatura de jogador (PvP) → queda 1,5 s (x0,5 do contrato) → cancela "alvo levantou"** — igual ao Lobo (em PvP só finaliza se já estiver em posição); (2) contra alvos pequenos/médios a Cauda sempre causa algum efeito (crocodilo grande e Força 60) — números [A TESTAR]; (3) a vítima caída não tem animação de caída/morte própria (o crocodilo jovem continua no Repouso); (4) no protótipo "PvP" = atributo da vítima; no contrato do Lobo, ataque de selvagem é PvE — alinhar.

**20/11/2026 — Encaixe real da presa na boca, ETAPA 1 (pedido "quero REALISMO... agarre o alvo na boca, simetricamente, o corpo encaixe certinho; se não couber, só morde"). Em andamento; nada ligado ao PoderesTeste ainda.**
- **Vídeo r2 revisto** (folhas `review/regras_lobo_2011/q30b`, `q30c`): os dentes encostavam no pescoço do crocodilo jovem, mas o pescoço medido tem **3,1 de espessura** (raios) e a boca só abre **1,52** de vão: a r2 era geometricamente impossível (não era encaixe; era "dente encostado").
- **Referencial e capacidade da boca** (`scripts/medir_boca.py` → `boca_medidas.json`, malha 1:1 com o Studio): dobradiça (osso Mandibula), F/U/R do crânio (osso Cabeca); folga interna entre as arcadas por profundidade d (2,5–5,5 a partir da dobradiça; ponta em 5,74) e abertura α (0 = fechada … 25,57° = máximo do rig). **Folga máxima ~1,3–1,5 na metade da frente** (d 4,0–5,5); < 0,7 no fundo.
- **Abertura variável sem atravessar o corpo:** 6 poses novas (Blender) `SegurarPresa`, `SegurarPresaAgua`, `MordidaEsmagadora` em `_Boca0` (α 0) e `_Boca1` (α 25,57), idênticas no corpo (diferença só na Mandibula, 25,57° exatos). No Studio, tocadas juntas com pesos (1−w, w): **medido linear** — w 0/0,25/0,5/0,75/1 → mandíbula −8,0/−1,7/4,8/11,2/17,5° em relação ao crânio (faixa 25,5°). Assim a boca fecha só até a espessura da presa. Re-mordidas: abre 6° e crava 1,5° além do contato.
- **`studio/EncaixeBoca.luau`** (novo módulo no place): seção da presa por raios na própria colisão (espessura ao longo de U e extensão ao longo de F), candidatos nos segmentos osso→pai (sem olhos/raiz; sem ossos = caixa), decisão cabe/não cabe com motivo, profundidade e abertura de contato, e desenho de diagnóstico (eixos, vão, pegada). Medido (Play): crocodilo escala 0,4 → cabe na canela (1,21); 0,55 → antebraço (1,27); 0,65 → cauda (1,28; pescoço/canela 2,0+ não cabem); 1,0 → ponta da cauda (1,18; canela 3,1 não cabe); boneco em pé 5,5 → não cabe; boneco deitado 1,42 de espessura mas 2,92 de extensão → não entra. Imagem `review/encaixe_2011/diag_boca_r2_x_encaixe.jpg`.
- **Achado que bloqueia a etapa 2:** o centro da boca fica a **2,4–3,0 do chão** na pose de segurar (3,1–3,3 em repouso); as partes mordíveis de uma presa **caída** ficam a 0,3–1,0 do chão — para fechar a boca nelas a arcada de baixo teria de entrar no chão. Precisa de poses novas (cabeça baixa e/ou mordida de lado, cabeça girada como o crocodilo real) antes de ligar o encaixe ao agarrão e à finalização.

**20/11/2026 — Encaixe real da presa, ETAPA 2 (usuário: "Mordida de lado"). Ligado ao agarrão e à Mordida esmagadora; testado em Play. Aguarda avaliação.**
- **Poses de mordida de lado** (Blender, `scripts/anim_crocodilo.py`): `SegurarLadoE/D` e `EsmagarLadoE/D`, cada uma em `_Boca0/_Boca1` (8 clipes; 75 no manifesto). A cabeça gira ~79° pelo pescoço e desce; o vão fica na horizontal. Medido em Play, com a boca aberta: o centro do vão fica a **1,8 (E) / 1,4 (D)** do chão, contra 2,3 na pose normal. O lado E leva a boca para +X local (convenção giro180y).
- **Pegada real** (`studio/PoderesTeste.luau`, `pegar`/`fixarPegada`), no fecha_boca do agarrão e na finalização:
  1. Escolhe a região que cabe mais perto do centro do vão. A distância é medida em 3D a partir de um ponto fixo no corpo (`EncaixeBoca.CENTRO_LOCAL`/`CENTRO_LADO_E/D`). Região baixa (≤ 1,9 do chão) é medida com o eixo da mordida de lado.
  2. Põe a pose (normal / de lado / água) com a boca aberta.
  3. Ajusta o corpo do crocodilo para o centro do vão chegar na região. O limite é o deslocamento líquido: agarrão 1,5, finalização 3,0. A boca morde onde alcança: desliza no plano mediano e centraliza a espessura.
  4. Mede de novo no referencial real da boca.
  5. Resultado:
     - cabe → fecha até as arcadas encostarem (pesos do par) e prende a presa ao vão;
     - não cabe → **só a mordida de contato** (dano 10, sem prender nem esmagar);
     - fora do plano/alcance → **erra**.
  6. Se a região que cabe está fora de alcance, tenta a mais perto.
  7. Enquanto segura, revalida a cada 0,5 s (espessura × vão na faixa ocupada → penetração; solta se não couber mais) e registra a deriva.
- **Finalização:** escolhe a região preferindo Pescoço/Cabeça e se aproxima pondo o centro do vão da pose escolhida na região. Toca o par `MordidaEsmagadora`/`EsmagarLado` na abertura de contato. Só dá dano numa cravada se houver corpo entre as arcadas; se não couber, só morde e cancela. A presa selvagem toca a própria Morte (presa com esqueleto); a queda toca DescansoDeitado e o levantar toca Levantar (os bonecos de teste não têm esqueleto: tombam como antes).
- **`EncaixeBoca`:** a extensão agora é separada em trás (lado da dobradiça, que precisa entrar na faixa útil) e frente (pode sair pela ponta). Assim um focinho comprido de presa grande cabe.
- **Testes em Play** (presas de teste com partes e Humanoid, `studio/TesteEncaixe.luau`):

  | Caso | Situação | Resultado | Medidas |
  |---|---|---|---|
  | 1 | Filhote (tronco 1,0) | **CAPTURA** pelo tronco | α 22,8°, d 4,30; corrigiu 0,7; penetração máx **−0,01**; deriva 0,000 |
  | 2 | No limite (1,25) | CAPTURA | α 23,5°; penetração 0,00 |
  | 2b | Passa do limite (1,6 > vão 1,52) | **SÓ MORDIDA** | — |
  | 3 | Presa grande, focinho 0,95 | CAPTURA pelo focinho | extensão 6,9, o resto fica para fora da ponta |
  | 4 | Búfalo (3,0) | SÓ MORDIDA | — |
  | 5 | Oblíquo a 3,8 de lado / sob o pescoço | **ERRA** ("fora de alcance") | — |
  | 5c | Deitado com o pescoço 0,9 em pé | **MORDIDA DE LADO** (ladoE) | desvio lateral 0,03, vão 0,02 |
  | 6 | Água (filhote nadando) | CAPTURA em SegurarPresaAgua | — |
  | F1 | Finalização, pescoço 0,9 | CAPTURA de lado (ladoD), 2 cravadas, morre | penetração **0,08** nas cravadas |
  | F2 | Finalização, pescoço 2,2 | SÓ MORDIDA, vida 30→20, sem morte | — |

  Regressões:
  - PvP solta no prazo de 2,50 s, com imunidade de 8 s;
  - `cancelar` no meio solta na hora (a presa não se move depois);
  - presa removida → cancela;
  - a sustentação de 3,5 s foi mantida.
- **Vídeo** `review/encaixe_2011/Crocodilo_Encaixe_Presa_r1.mp4` (~93 s, 30 qps):
  - tomadas: presa inteira, frente, lado e perto do caso que cabe; frente e lado do que não cabe; presa grande pelo focinho; finalização geral, perto e "não cabe"; água sob a superfície;
  - repete em câmera lenta 0,5× a tomada de perto da pegada e a da finalização.
- **Imagens:** comparação `antes_depois_r2_x_encaixe.jpg` (r2 × agarrão e finalização novos), folhas em `pranchas/` e `still_cabe_lado.jpg` (presa semitransparente entre as arcadas).
- **No place:** `EncaixeBoca`, `PoderesTeste`, `ConfigPoderes_Teste` (`altura_lado`, `corrigir_*`, `revalidar`) e `TesteEncaixe` foram instalados. Backup em `ServerStorage.Crocodilo_ANTES_Encaixe2`; place local salvo; local = Studio (hash).
- **Limitações:**
  - A deriva é 0 por construção: a presa é presa ao referencial da boca, por isso esse número não prova nada visualmente.
  - Uma presa grande presa pelo focinho é levantada até ~0,5 (o crocodilo não abaixa a cabeça por IK).
  - Presas muito baixas (< ~1,2 de altura deitadas) ficam abaixo do vão da mordida de lado → erra.
  - Nos testes foram usados blocos de teste, não criaturas reais.
  - A tomada geral da finalização ficou mal enquadrada (a câmera ficou atrás do corpo do crocodilo).

**20/11/2026 — Encaixe r2: dentes cravados + arremesso.** O usuário aprovou a mordida da etapa 2 e pediu "enfincar mais os dentes" e "jogar a criatura presa mais pra longe". Respostas às perguntas:
- os dentes cravam ~0,4;
- a sacudida é de lado e a presa voa ~8 studs;
- a presa cai e levanta;
- no PvP o arremesso é mais curto.

Testado em Play. **APROVADO pelo usuário em 20/11.**
- **Dentes cravados** (`EncaixeBoca.avaliar(..., crava)`, `Agarrao.cravar = 0.4`):
  - as arcadas fecham até `espessura − 0,4`, com o corpo no centro do vão, então os dois lados cravam por igual;
  - medido: penetração 0,39–0,40 no agarrão (filhote, deitado, água) e 0,48 na finalização. Antes era −0,01 a 0,00.
  - A abertura de contato fica registrada em `alfaContato`, por exemplo 22,8° contato → 17,0° cravado.
- **Arremesso** (`PoderesTeste`: `arremessar`/`lancar`, `CFG.Arremesso`):
  1. O crocodilo dá uma sacudida de lado: o corpo e a cabeça giram 20° em 0,22 s, acelerando, com a presa ainda presa.
  2. Ele solta no pico. A sustentação continua em 3,5 s no total, porque a sacudida começa 0,22 s antes.
  3. A presa voa em arco (2,5 de altura, 0,7 s) até 8 studs, mais para o lado que para a frente, dando uma cambalhota.
  4. Ela fica caída 1,5 s, sem dano na queda, e levanta.
  - O lado segue a pose: lado E/D na mordida de lado; na boca normal é sorteado.
  - **PvP:** metade (4 studs, arco 1,2), sem cambalhota e sem queda. Solta aos 2,52 s do contato, com 8 s de imunidade.
  - **Água:** só solta, como antes (`Arremesso.agua = false`).
  - **Presa com física** (não ancorada): recebe velocidade balística no servidor. Isso não foi testado, porque os testes usaram só bonecos ancorados.
- **Testes (Play):**
  - filhote: cravou 0,39 e voou 8,0;
  - queda: levantou após 1,50 s;
  - PvP: 4,0, sem queda, imune;
  - deitado com mordida de lado: cravou 0,40 e voou 8,0 para E;
  - finalização F1: 2 cravadas, morte, penetração 0,48;
  - água: SoltarPresa sem arremesso.
- **Vídeo** em `review/encaixe_r2_2011/`: perto dos dentes, arremesso visto de cima, mordida de lado e PvP, com câmera lenta 0,35× das 3 primeiras tomadas.
- **No place:** backup `ServerStorage.Crocodilo_ANTES_Encaixe_r2`, módulos com hash conferido.
- **Limitação:** a sacudida é um giro do corpo inteiro em volta do pivô, não um clipe próprio de cabeça e pescoço. Um clipe `ArremessarPresa` E/D no Blender deixaria o movimento mais natural. **Resolvido no r3, abaixo.**

**20/11/2026 — Arremesso r3: clipes `ArremessarPresaE/D`.** Pedido do usuário: "Fazer os clipes". Escolhas dele: "Arma e chicoteia" e "corpo gira pouco, ~6°". Testado em Play. **APROVADO pelo usuário em 20/11.**
- **Clipe** (`scripts/anim_crocodilo.py`, `_arremessar`):
  - dura 1,0 s, em par `_Boca0`/`_Boca1`, com a boca na abertura da pegada até soltar;
  - parte do quadro 0 do SegurarPresa;
  - **arma:** a cabeça vai ~15° para o lado oposto, com o focinho um pouco baixo;
  - **chicoteia:** ~35° para o lado do arremesso, erguendo o focinho; o tronco da frente acompanha e a cauda contrapesa;
  - evento **solta em 0,44 s**: a boca abre 12° além do encaixe;
  - depois volta ao Repouso.
  - QA: IK 0,000, pé sem deslizar. Revisão no Blender: `review/arremesso_r3/prancha_clipe_E.jpg`.
  - **Sinal:** com lado +1 no Blender, a boca ia para −X local do jogo (medido em Play). Por isso o nome segue o jogo: `ArremessarPresaE` lança para +X, como `SegurarLadoE`.
- **Jogo** (`PoderesTeste`):
  1. O clipe começa 0,44 s antes do fim da sustentação, então o total continua 3,5 s.
  2. O corpo gira só `giro_clipe` = 6° durante a chicotada (0,30 → 0,44 s).
  3. No evento "solta", a presa é solta e lançada.
  4. O próprio clipe volta ao Repouso, sem tocar o SoltarPresa.
  - Sem o clipe no place, o código volta ao giro de 20° do r2.
- **Testes (Play):**
  - deitado: chicotada +3,47 em X, pousa em X 13,2, Caido;
  - filhote: E +3,22 / D −3,62, pousa a ~10,5 do eixo, Caido;
  - PvP: D −3,21, pousa a −6,5, sem queda, solta aos 2,50 s;
  - sustentação PvE: 3,07 s + 0,43 s = 3,50 s;
  - água: SoltarPresa, sem arremesso.
- **Vídeo:** `review/arremesso_r3/Crocodilo_ArremessarPresa_r3.mp4`, com frente, de cima, mordida de lado e PvP, e câmera lenta 0,35× das 3 primeiras tomadas. Captura a 15 qps e codificação em prioridade baixa.
- **No place:** backup `ServerStorage.Crocodilo_ANTES_Arremesso_r3`; 4 KFS em `Animacoes` com o marcador `solta`; place local salvo.

## 6. Pendências
1. **Decisões do criador:**
   - ~~conflito do agarrão PvP~~ **decidido 19/11: Versão B** (prende, aliados soltam); números aprovados e protótipo com bonecos/jogador feitos;
   - **Soltar aliado só com armas** (usuário 19/11): depende da criação das espadas etc.; hoje o golpe é soco de teste;
   - elemento único;
   - lista final de passivas e ativas e seus efeitos;
   - **mergulho com cavaleiro** (sim/não; respiração, câmera, profundidade, segurança);
   - velocidades em terra e água; números (24.2 é só proposta);
   - duração do agarrão PvE: **3,5 s por enquanto** (usuário 16/11); tamanho máximo de presa;
   - cores dos 3 padrões; tamanhos por estágio;
   - **capacete aquático** exigido para montar (anotado 17/11, detalhar depois);
   - **depois do agarrão que neutraliza:** selvagem/sem cavaleiro decide sozinho: oponente próximo → leva o corpo embora; senão → come; roubo = outro animal (IA ou montado) pegar o corpo para comer (17/11). Faltam raio, destino, tempo de comer e o caso montado.
2. **Modelo:** escolher a base (V2 ou V5) e revisar contra o painel 03; boca/dentes/língua; custo da V5 (56 mil tris) precisa de LOD.
3. **Estágios:** só existe o Adulto. Faltam Bebê, Jovem, Pré-adulto, Ancião e ovo.
4. **Roblox:** importar (Import 3D manual), conferir escala, pés no chão, superfície da água (corpo meio submerso), SurfaceAppearance e FPS. Publicar animações exige a conta do usuário.
5. **Animações:** auditadas só numericamente. GuardarNinho com ajustes. Seguir `padrao-movimento-criaturas` (cauda em onda base→ponta, ondulação lateral no nado, antecipação→contato→recuperação nos ataques).
6. **Sistemas (não iniciados):** IA selvagem (território, emboscada submersa, toca, descanso na margem), companheiro domesticado, montaria anfíbia (troca terra↔água), sons (rugido grave, sibilo, batida de mandíbula, respingos), VFX (bolhas, ondulações, ondas da cauda). Tudo com validação no servidor; agarrão com autoridade do servidor e regra PvP/PvE separada.

## 7. Próximos passos sugeridos (aguardam aprovação)
1. ~~Pedir a decisão do agarrão PvP~~ (decidido 19/11: Versão B). Próximo: proposta de números do agarrão PvP (duração, resistência a controle repetido, como os aliados soltam) para aprovação; depois elemento único + kit (passiva + ativas).
2. **Revisar V2 × V5** com prancha lado a lado com o painel 03 (só leitura e renders no Blender) e listar correções (boca, mandíbula, patas espalhadas, osteodermos).
3. **Teste de importação num place vazio local** (sem tocar no mapa): escala 5–7 de ombro, nado na linha d'água, Mergulho/Emersão.
4. **Só depois:** clipes refinados, sons, IA selvagem e montaria terra/água. Um sistema por vez; mergulho montado só depois de definido pelo criador.
