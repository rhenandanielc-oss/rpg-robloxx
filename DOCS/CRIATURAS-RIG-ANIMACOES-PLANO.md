# Plano de rigs e animações das criaturas (proposta, 26/10/2026)

**Estado:** este documento é só **plano**.
- Nenhum rig ou animação foi criado.
- A **pré-condição não está cumprida:** o refinamento anatômico (`DOCS/CRIATURAS-REFINAMENTO-ANALISE.md`) aguarda aprovação, e a finalização visual depende dele.
- Fazer o rig em cima dos blockouts atuais obrigaria a refazer pesos e animações depois.

**Fontes:**
- Painéis `REFERENCES/03_CREATURES`: pose, peso e atitude de cada espécie.
- RPG_02: locomoção, montaria e habilidades oficiais.
- `Catalogo`: as **16 formas são montáveis no estágio Adulto**.

## Ordem das fases (dependências)
1. **Refinamento anatômico:** aguarda sua aprovação.
2. **Finalização visual:**
   - volumes finais e detalhes secundários/terciários;
   - separação de materiais (pele, pelo, escama, garra, osso/corno, membrana, cristal);
   - cores base neutras;
   - topologia limpa para deformar.
3. **Rig + pacote base de animações**, família por família.
4. **Animações especiais:** voo, nado, montaria, ninho e as 4 habilidades oficiais de cada espécie.

## Rigs por família (estrutura óssea; um rig-base por família, proporções próprias por forma)

| Família | Formas | Cadeias | Ossos (estimado) | Observações |
|---|---|---|---|---|
| Canídeos | Lobo Ancestral, Lobo Ártico | raiz, quadril, 4 vértebras, peito, 3 pescoço, cabeça, mandíbula, 2 orelhas, 4 membros × (escápula/coxa, braço, antebraço/canela, metacarpo/metatarso, pata), 6 cauda | ~42 | Ártico = mesmo rig, outra escala/pesos |
| Cérbero | Cérbero Sombrio | rig canino + **3 cadeias de pescoço/cabeça/mandíbula** saindo de um peito comum | ~58 | Cabeças com controle independente ("reações a inimigos diferentes", RPG_02) e camada que as coordena |
| Felino | Leão Solar | como o canino, com escápula mais móvel, ombro e coluna flexíveis, cauda longa com tufo e **ossos de juba** secundários | ~48 | Juba balança por ossos, não por física |
| Pesados plantígrado | Urso Silvestre | coluna curta, corcova, membros plantígrados (pé inteiro), garras | ~40 | Pode se erguer em 2 patas (ameaça) |
| Pesados ungulado | Búfalo Colossal | coluna com corcova, pescoço baixo, cascos, chifres fixos na cabeça, barba e capa com 2–4 ossos de balanço | ~40 | Carga com a cabeça baixa |
| Reptilianos terrestres | Crocodilo, Basilisco, Lagarto | coluna longa (6–8), 4 membros espalhados/semi-eretos com rotação no ombro/quadril, cauda longa (8–10), mandíbula | ~45–50 | Crocodilo com ondulação lateral; Basilisco com cristas fixas; Lagarto com cristais rígidos |
| Artrópode | Escorpião Colossal | prossoma, 6 mesossoma, 5 metassoma + telson, 2 quelíceras, 2 pedipalpos (3 + dedo móvel), **8 pernas × 4 segmentos** | ~60 | Segmentos rígidos: cada placa ligada a um só osso (sem deformação mole) |
| Aquáticos | Serpente Marinha, Leviatã | Serpente: cadeia de 24–30 vértebras + cabeça/mandíbula + nadadeiras/cristas. Leviatã: coluna 14–16, cabeça/mandíbula, 4 nadadeiras × 3 ossos, cauda 8 | ~35 / ~40 | Nado por onda que percorre a coluna |
| Dragões | Montanhas, Glacial, Sombrio | quadrúpede (~44) + **2 asas × (úmero, antebraço, punho, 4 dedos × 3)** + pescoço 6–8 + cauda 10–12 + mandíbula | ~90 | Um rig para as 3 formas, com proporções e pesos por forma |
| Wyvern | Wyvern | bípede: pernas de 4 segmentos, **asa-braço** (úmero, antebraço, punho com garra, 3 dedos × 3), pescoço 6, cauda 10 + ferrão | ~70 | Locomoção terrestre apoiada nas pernas (e no punho das asas, se aprovado) |

## Limitações do Roblox (a confirmar no Studio)
- **Pele deformável (bones):** até 4 influências por vértice. Os blockouts e os modelos da C1 já foram feitos assim.
- **Desempenho:** o número de ossos por modelo afeta o desempenho. Um rig de ~90 ossos para os Dragões exige teste no celular, e pode ser preciso reduzir dedos de asa ou vértebras.
- **Publicação:** cada animação é um KeyframeSequence que precisa ser **publicado** (Animation Editor → Publish, manual). Animações procedurais (cauda, juba, olhar das 3 cabeças) podem ser feitas por script no cliente para economizar clipes.
- **Montaria:** a sela e o encaixe do personagem R15 são um Attachment no osso do dorso. As animações do cavaleiro (R15) são separadas das da criatura.
- **Física:** sem tecido nem física de pelo. Juba, barba e membranas balançam por ossos secundários animados.

## Animações (contagem proposta)
**Pacote base (todas as 16):** 12 clipes.
- Idle (respirando);
- Walk, Run;
- VirarE, VirarD;
- Start (arrancada), Stop (frenagem);
- HitReaction, AtaqueBásico, Morte/Incapacitação;
- Comer, Descanso (deitar + deitado em loop + levantar = 1 conjunto).

**Montaria (todas as 16, montáveis no Adulto):** 7.
- Mount, Dismount, RideIdle, RideWalk, RideRun, RideVirarE, RideVirarD.

**Territorial/ninho:** 3, nas espécies com ninho ou covil documentado (Dragões, Wyvern, Lobos, Urso, Escorpião, Lagarto, Serpente, Leviatã).
- GuardaNinho, Alerta, Ameaça.

**Voo (Dragões ×3, Wyvern):** 8.
- Decolagem, Pouso, Planeio, VooBatido, PairarCurto, AtaqueAéreo, Empoleirar, CurvaAérea.

**Aquáticas (Serpente, Leviatã; parcial no Crocodilo):** 6.
- NadoParado, NadoCruzeiro, NadoRápido, NadoSuperfície, Mergulho, Emersão.
- O Crocodilo usa NadoCruzeiro, Submersão e Emersão: 3.

**Habilidades oficiais:** 4 por espécie, como animação, sem dano nem efeito final.

| Família / forma | Base | Montaria | Ninho | Voo | Aquáticas | Habilidades | Total por forma |
|---|---|---|---|---|---|---|---|
| Lobo Ancestral / Lobo Ártico | 12 | 7 | 3 | – | – | 4 | 26 cada |
| Cérbero | 12 + 2 coordenação de cabeças | 7 | – | – | – | 4 | 25 |
| Leão | 12 | 7 | – | – | – | 4 | 23 |
| Urso | 12 + 1 erguer-se | 7 | 3 | – | – | 4 | 27 |
| Búfalo | 12 | 7 | – | – | – | 4 | 23 |
| Crocodilo | 12 | 7 | – | – | 3 | 4 | 26 |
| Basilisco | 12 | 7 | – | – | – | 4 | 23 |
| Lagarto | 12 + 1 escalada | 7 | 3 | – | – | 4 | 27 |
| Escorpião | 12 | 7 | 3 | – | – | 4 | 26 |
| Serpente Marinha | 12 (deslize em terra no lugar de walk/run) | 7 | 3 | – | 6 | 4 | 32 |
| Leviatã | 12 (idem) | 7 | 3 | – | 6 | 4 | 32 |
| Wyvern | 12 | 7 | 3 | 8 | – | 4 | 34 |
| Dragões (×3) | 12 | 7 | 3 | 8 | – | 4 | 34 cada |

**Total:** ~465 clipes no catálogo completo. O reaproveitamento abaixo reduz isso a **~260 clipes animados de fato**.

## Reaproveitamento (sem matar a individualidade)
- **Mesmo rig, retime e ajuste por forma:**
  - Lobo Ártico a partir do Ancestral: mais pesado, passo mais curto e firme.
  - Dragão Glacial e Sombrio a partir das Montanhas: Glacial mais preciso, Sombrio mais baixo e agressivo.
- **Compartilhado na família, com ajuste de amplitude:**
  - ciclos de montaria (RideWalk/RideRun derivam de Walk/Run, com estabilização do dorso);
  - Start/Stop/Virar dos quadrúpedes.
- **Procedural no cliente** (sem clipe): balanço de cauda/juba/barba, respiração extra, olhar das cabeças (Cérbero: cada cabeça pode olhar um alvo diferente) e inclinação do corpo nas curvas.
- **Nunca reaproveitar entre famílias diferentes.** Exemplos: canino ≠ felino ≠ plantígrado ≠ ungulado; Dragão ≠ Wyvern.

## Identidade de movimento (pelos painéis e pelo RPG_02)
- **Leão:** passo amplo e confiante, cabeça alta, ombros "rolando".
- **Lobo Ancestral:** trote leve, cabeça baixa no rastreio.
- **Lobo Ártico:** passo firme, mais peso nas patas dianteiras.
- **Urso:** balanço lateral da massa, passo plantígrado, ergue-se para ameaçar.
- **Búfalo:** inércia (acelera devagar, carga reta), cabeça baixa no impacto.
- **Cérbero:** cabeças independentes com atraso entre si, postura baixa de ataque.
- **Crocodilo:** high walk curto e pesado, ou barriga no chão; giro mortal.
- **Basilisco:** postura alta de domínio, pausas e olhar fixo.
- **Lagarto:** passos precisos e estáveis, escalada.
- **Escorpião:** ondas de patas alternadas (tetrápode), pinças à frente, cauda armada.
- **Serpente:** onda sinuosa.
- **Leviatã:** ondulação lenta e enorme.
- **Wyvern:** rápida, guinadas e rasante.
- **Dragões:**
  - Montanhas: pesado e nobre, batida de asa ampla;
  - Glacial: controlado, planeio longo;
  - Sombrio: ataque em mergulho, postura baixa.

## Pontos que precisam de aprovação
1. **Aprovar o refinamento anatômico** (`DOCS/CRIATURAS-REFINAMENTO-ANALISE.md`). É a pré-condição de tudo.
2. Confirmar se o Wyvern também se **apoia nos punhos** das asas em terra (o RPG_02 marca como proposta).
3. Confirmar o escopo de clipes: pacote completo (~465 no catálogo) ou só base + montaria nesta etapa.
4. O limite de ossos dos Dragões (~90) depende de teste no celular.
