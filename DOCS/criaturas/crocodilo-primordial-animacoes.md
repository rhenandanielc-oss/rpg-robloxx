# Crocodilo Primordial — inventário de animações e plano de cobertura

Ficha principal: `DOCS/criaturas/crocodilo-primordial.md`. Pasta de trabalho: `BLENDER/Criaturas/Crocodilo_Primordial_Ref/`.
Pedido de origem: `DOCS/pedidos/2026-11-03-crocodilo-primordial-modelo-referencia.md` + complemento (auditoria, faltantes, poderes).
Atualizado em 04/11/2026 (Lote 4). **Nada aqui é regra oficial de combate.** Durações são visuais e provisórias.

## 1. Inventário por clipe (estado real em 03/11/2026)

Legenda de status: **atual revisado** · **histórico, não adaptado** · **faltante** · **proposta** · **depende de decisão**.

### 1.1 Modelo atual (Meshy, LOW 19.012 tris, rig v2 de 28 ossos)
Fonte: `scripts/anim_crocodilo.py` (procedural, IK assado em FK). Ação em `CR_Crocodilo_Anim.blend` (`Croc_<Clipe>`), JSON em `clipes/Crocodilo_<Clipe>.json`, mesma geração (Lote 1).

| Clipe | Duração | Quadros | Laço | Ação | JSON | Render Lote 1 | Status |
|---|---:|---:|---|---|---|---|---|
| Repouso | 4,0 s | 120 | sim | sim | sim | `review/L1_clipes/` (34, cabeça) | atual revisado |
| Andar | 1,5 s | 45 | sim | sim | sim | lado, patas, topo (chão quadriculado, deslocamento 1,85 studs/s) | atual revisado |
| Corrida | 0,533 s | 16 | sim | sim | sim | lado, patas (deslocamento 8,75 studs/s) | atual revisado |
| Nado | 2,0 s | 60 | sim | sim | sim | lado, topo (água de teste) | atual revisado (física/flutuação **não** testadas) |
| Mordida | 1,0 s | 31 | não | sim | sim | 34, cabeça, câmera lenta | atual revisado (ataque básico, fora dos slots) |
| Ameaca | 2,0 s | 61 | não | sim | sim | 34, cabeça, câmera lenta | atual revisado (sem som/poder) |

Versão atual: **L1b** (03/11/2026): Corrida com o laço corrigido (passo das dianteiras sob o ombro) e boca sem lascas/franjas. Evidências em `review/L1b/`. Malha 18.993 tris.

Velocidades 1,85 e 8,75 studs/s são **sincronização da animação** (pé apoiado parado no chão), não balanceamento aprovado.

### 1.1b Lote 2 — locomoção, transições e água (03/11/2026, aguardando aprovação)
Mesma fonte e mesmo rig (L1b). Versão anterior preservada em `versao_L1b/`. Evidências em `review/L2/clipes/` (folhas `FOLHA_*`, GIFs de 3 ciclos para laços, normal + lento para transições). Dados para o jogo: bloco `sincronizacao` dentro de cada JSON e `clipes/emendas_transicoes.json`.

| Clipe | Duração | Quadros | Laço | Sincronização (técnica, não balanceamento) | QA (IK / escorregão do pé no mundo) | Status |
|---|---:|---:|---|---|---|---|
| VirarEsquerda | 1,5 s | 45 | sim | giro +13,3°/s em torno do pivô y −4,19 (centro entre as patas) | 0 / 0 (sola 0,119; L2b) | atual (proposta de revisão) |
| VirarDireita | 1,5 s | 45 | sim | giro −13,3°/s | 0 / 0 (sola 0,135; L2b — antes 0,0058 / 0,175) | atual |
| Arrancada (Repouso→Corrida) | 1,4 s | 43 | não | deslocamento por quadro no JSON (0 → 8,75) | 0 / 0 | atual |
| Frenagem (Corrida→Repouso) | 1,6 s | 49 | não | 8,75 → 0 + passos de acomodação | 0 / 0 | atual |
| RepousoParaAndar | 1,4 s | 43 | não | 0 → 1,85 | 0 / 0 | atual |
| AndarParaRepouso | 1,8 s | 55 | não | 1,85 → 0 + acomodação | 0 / 0 | atual |
| AndarParaCorrida | 1,1 s | 34 | não | 1,85 → 8,75 | 0 / 0 | atual |
| CorridaParaAndar | 1,1 s | 34 | não | 8,75 → 1,85 | 0,013 / 0 | atual |
| NadoParado | 3,0 s | 90 | sim | — | 0 / — | atual |
| Nado (= NadoCruzeiro) | 2,0 s | 60 | sim | — | 0 / — | atual (do Lote 1, sem duplicata) |
| CurvaAquaticaEsquerda/Direita | 2,0 s | 60 | sim | ±25°/s **proposto** | 0 / — | atual |
| Mergulho / Emersao | 1,5 s | 46 | não | profundidade é do jogo (o clipe só arfa o corpo) | 0 / — | atual (sem cavaleiro) |
| EntradaAgua | 2,2 s | 67 | não | mantém 1,85 (L2b); inclinação e profundidade pelo jogo; recolhe patas | 0 / 0 | atual (L2b) |
| SaidaAgua | 2,4 s | 73 | não | patas ao chão → 0 → 1,85; inclinação e profundidade pelo jogo (L2b) | 0 / 0 | atual (L2b) |
| NadoRapido | — | — | — | — | — | **não feito** (proposta só se houver necessidade) |

**L2b (03/11/2026):** VirarDireita/Esquerda e EntradaAgua/SaidaAgua corrigidas na origem; cena de margem com água só visual (`scripts/cena_agua.py`); evidências em `review/L2b/`. Detalhes na ficha principal. Lote 2 aguardando avaliação.

Emendas com os laços (maior diferença de ângulo entre ossos, quadro de entrada sugerido) em `clipes/emendas_transicoes.json`: as que saem do Andar ficam entre 1,4° e 3,3°; as que chegam a um laço ficam entre 8° e 21°, e o jogo deve entrar no quadro indicado com crossfade curto.

### 1.1c Lote 3 — reações e vida (03/11/2026, conferido pela supervisão; aprovação formal pendente)
Lote 2 (com as correções L2b) aprovado pelo usuário em 03/11/2026 ("Aprovo, Lote 3"). Versão L2b preservada em `versao_L2b/`. Mesma fonte, mesmo rig/GLB (sem reexportar). Todos com patas plantadas (pé não escorrega); a boca acompanha a cabeça (a Mandibula é filha do Pescoco2). Eventos são só **marcadores visuais** no bloco `sincronizacao` do JSON, não regra.

| Clipe | Duração | Quadros | Laço | De → para | Eventos (s) | Status |
|---|---:|---:|---|---|---|---|
| ReacaoGolpe | 0,8 s | 25 | não | Repouso → Repouso | impacto 0 | atual (golpe de frente; variações laterais = proposta) |
| Morte (incapacitação visual) | 2,4 s | 73 | não | Repouso → fica no último quadro | patas_cedem 0,25 · impacto_chao 0,75 | atual (só visual; sem regra de morte) |
| Comer | 3,0 s | 91 | não | Repouso → Repouso | abocanha 0,62 · engole 1,25 · engole2 1,95 | atual |
| Deitar | 2,0 s | 61 | não | Repouso → DescansoDeitado | barriga_no_chao 1,7 | atual |
| DescansoDeitado | 6,0 s | 180 | sim | — | — | atual (respiração; queixo no chão) |
| Levantar | 1,8 s | 55 | não | DescansoDeitado → Repouso | — | atual |
| Observar | 4,0 s | 121 | não | Repouso → Repouso | — | atual (varre esquerda/direita) |
| Alerta | 2,5 s | 76 | não | Repouso → Repouso | vira_para_estimulo 0,18 | atual (ergue o corpo e segura; laço de alerta = proposta) |
| GuardarNinho | — | — | — | — | — | **proposta** (não feito) |

Evidências em `review/L3/` (folhas, GIFs normal e lento, QA). Detalhes e números na ficha principal.

### 1.1d Lote 4 — montaria, só apresentação (04/11/2026, aprovado pelo usuário)
Versão L3 preservada em `versao_L3/`. Rig e GLB **não mudaram** (md5 iguais); os 29 JSON anteriores estão **idênticos**. Cavaleiro = manequim de **teste** com proporções aproximadas do R15 em bloco (5,2 studs; não é rig R15 validado). Sela = volume **PROPOSTA** de teste, sem acabamento. Lado do teste: esquerdo (+X), escolhido só para o teste, não é regra.

| Movimento | Situação | Duração | Laço | Observação |
|---|---|---:|---|---|
| Montar | **variante nova** (clipe do crocodilo) | 4,0 s (121 q) | não | baixa 0,20, rola 1,5° para o lado do apoio, olha para o cavaleiro, amortece ao sentar; termina no Repouso (0,4°) |
| Desmontar | **variante nova** (clipe do crocodilo) | 3,6 s (109 q) | não | não é o Montar invertido: perna D volta pela garupa, desce encostado no flanco e solta perto do chão |
| MontadoRepouso | **reutiliza** Repouso | 4,0 s | sim | cavaleiro preso ao osso Coluna1; deriva 0 |
| MontadoAndar / MontadoCorrida | **reutiliza** Andar / Corrida | 1,5 / 1,07 s | sim | sem variante: o dorso não deforma a ponto de exigir |
| MontadoVirarE/D | **reutiliza** VirarEsquerda/Direita | 1,5 s | sim | giro de sincronização do clipe |
| NadoParado, Nado, CurvaAquáticaE/D montados | **reutiliza** | 3,0 / 2,0 s | sim | tronco do cavaleiro 2,5 acima da água de teste |
| EntradaAgua / SaidaAgua montados | **reutiliza** | — | não | cena de margem de teste; só superfície |
| Mergulho / Emersão montados | **não testado (fora do escopo)** | — | — | mergulho com cavaleiro continua pendente |

Cavaleiro (demonstração, não publicado): ações `DEMO_Cav_Montar`, `DEMO_Cav_Desmontar`, `DEMO_Cav_Sentado` em `CR_Crocodilo_Montaria_Teste.blend`. Evidências e números em `review/L4/` e na ficha principal.

### 1.1e Lote 5 — sela definitiva e os dois lados (05/11/2026, aprovado pelo usuário em 06/11)
| Movimento | Situação | Duração | Laço | Observação |
|---|---|---:|---|---|
| MontarDireita | **variante nova** (espelho do Montar) | 4,0 s (121 q) | não | rola/olha para −X; cavaleiro sobe pelo cotovelo D |
| DesmontarDireita | **variante nova** (espelho do Desmontar) | 3,6 s (109 q) | não | desce em y −4,1, afastado do joelho traseiro D |
| Montar / Desmontar | sem mudança (lado esquerdo) | — | — | JSON idênticos |
| Montado* (reutilizados) | reconferidos com a sela definitiva | — | sim | deriva 0 |

Sela: `CR_Croc_Sela` (`scripts/sela_crocodilo.py`), pesada na pele do crocodilo. Cavaleiro: ações `DEMO_Cav_MontarDireita` / `DEMO_Cav_DesmontarDireita` em `CR_Crocodilo_Montaria_L5.blend`. Números na ficha principal e em `review/L5/RESUMO_L5.txt`.

### 1.2 Históricos (outros rigs — NÃO transplantar sem retarget e inspeção)
| Arquivo | Rig | Ações | Status |
|---|---|---|---|
| `BLENDER/Criaturas/Crocodilo_Primordial.blend` (C1, 26/10) | 23 ossos | Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar, Natacao, Submersao, MordidaDeAgarrao, GiroPredatorio, CaudaDeMare (11) | histórico, não adaptado |
| `BLENDER/Criaturas/Blockouts/Crocodilo_Primordial/Crocodilo_Primordial_final_v5.blend` (V5, 27/10) | 24 ossos | Repouso, Andar, Corrida, VirarE/D, Arrancada, Frenagem, ReacaoGolpe, AtaqueBasico, Morte, Comer, DeitarDescanso, Descanso, LevantarDescanso, Montar, Desmontar, MontadoRepouso/Andar/Corrida/VirarE/VirarD, GuardarNinho, Alerta, Ameaca, NadoCruzeiro, Mergulho, Emersao, MordidaDeAgarrao, GiroPredatorio, Submersao, CaudaDeMare (31) | histórico, não adaptado (auditoria numérica 30/1, sem aprovação artística) |

Os 31 históricos **não** são 31 clipes prontos do modelo atual: a malha, as proporções e o esqueleto são outros. Servem de lista de cobertura e de referência de tempo.

## 2. Plano dos próximos lotes (aguardam aprovação, um por vez)
| Lote | Clipes | Observação |
|---|---|---|
| 2 — locomoção e transições (**aprovado 03/11**) | VirarEsquerda/Direita (com passos), Arrancada, Frenagem, Repouso↔Andar↔Corrida, EntradaAgua, SaidaAgua, NadoParado, NadoCruzeiro (= Nado atual), CurvaAquaticaE/D, Mergulho, Emersao | NadoRapido só se houver necessidade demonstrada (proposta) |
| 3 — reações e vida | ReacaoGolpe, Morte (incapacitação visual), Comer, Deitar, DescansoDeitado (laço), Levantar, Observar, Alerta | feito 03/11; conferido pela supervisão antes do Lote 4; GuardarNinho só como proposta visual; sem IA/reprodução |
| 4 — montaria (apresentação) | Montar, Desmontar; conferir reaproveitamento dos clipes com cavaleiro de teste | **aprovado 04/11**; nenhum Montado* novo (reutilização bastou); sem mergulho com jogador, oxigênio, câmera, sela definitiva |
| 5 — sela definitiva e dois lados | sela no Blender; MontarDireita, DesmontarDireita | **aprovado 06/11**; depois: textura/atlas e GLB da sela; mergulho montado pendente |

## 3. Poderes — especificação para revisão (NÃO implementar antes da aprovação)
**[OFICIAL 30/10]** Um elemento natural, ≥ 1 passiva, ≥ 3 ativas. **[PENDENTE]** Elemento, passiva e kit final do Crocodilo. As quatro habilidades da Etapa 15.1 são **referência histórica**; abaixo, só cobertura de animação proposta. Ataque básico (Mordida) fica fora dos slots.

| Referência | Meio | Fases (pose inicial → final) | Duração visual provisória | Marcadores de sincronização futuros |
|---|---|---|---|---|
| Mordida de Agarrão | terra/água | Entrada/bote (antecipação 0,3 s → contato) → Captura (fecha, 0,1 s) → Sustentação em laço (sacudidas da cabeça, alvo fictício) → Soltura/recuperação | ~0,5 + laço + 0,5 s | `contato`, `captura`, `soltura`; cancelável em qualquer fase (interrupção = evento do jogo) |
| Giro Predatório | água (terra: pendente) | Antecipação (recolhe patas, curva a cauda) → giro longitudinal contínuo (sem inversão de sentido; quantidade de voltas pendente) → recuperação | ~1,5 s por volta | `inicio_giro`, `volta_completa`, `fim` |
| Submersão | água; terra = postura baixa de camuflagem em lama/vegetação (nunca invisibilidade) | Mergulho → espera submersa (laço) → aproximação → emersão | compartilha Mergulho/Emersao do Lote 2 | `submerso`, `emerge` (linha d'água) |
| Cauda de Maré | água; variante seca (proposta) | Preparação do corpo (torção, cauda armada) → varredura → recuperação; sentido E/D (proposta) | ~1,2 s | `impacto_cauda`, ponto para onda local futura (VFX não define elemento) |

Para cada um: interrupção possível em qualquer quadro; transições compartilhadas com Repouso/Nado em vez de clipes completos repetidos. Duração visual **não** é duração de controle, dano ou recarga.

### Decisões necessárias do usuário
1. **Elemento natural único** do Crocodilo (a lista antiga Água/Terra/Natureza é histórico; fusões antigas não valem).
2. **Passiva** (nenhuma definida) e **lista final de ativas** (≥ 3).
3. **Conflito do agarrão PvP** no RPG_02: "só empurrões" × "agarrão mais longo, interrompível por aliados". A animação com alvo de teste não decide a regra.
4. Giro Predatório: número de voltas; vale em terra?
5. Cauda de Maré: variante em terra seca? sentido E/D?

### VFX/sons (só pontos de sincronização, nada criado)
Mandíbula (`fecha`), impacto do bote, batida/varredura da cauda, linha d'água (entra/sai). Bolhas, respingos e sedimentos precisam de orçamento para celular; não usar partículas para mascarar animação.
