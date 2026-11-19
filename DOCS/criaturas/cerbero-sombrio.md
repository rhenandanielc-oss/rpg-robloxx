# Cérbero Sombrio — ficha do subchat

Criatura **domesticável** das **Terras Corrompidas**. Espécie-base **Cérbero** (espécie própria, separada do Lobo), com uma única forma regional: **Cérbero Sombrio**. A ficha-base está marcada como **FINALIZADA** no RPG_02.

Fontes: `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO` (topo de 30/10, §0, §2, §8 "Cérbero — Cérbero Sombrio", §10, §11, §12, §15, §18.2, §19.2) e `RPG_01` (só cita o Cérbero no catálogo). A **ATUALIZAÇÃO OFICIAL de 30/10/2026** prevalece sobre o que vem depois no documento.

Regras de convivência: `DOCS/ORGANIZACAO-CHATS.md`. Studio um chat por vez (`DOCS/estado/studio-em-uso.md`). Não confundir com o projeto Dragon Ranch.

Ficha criada em 03/11/2026, só com leitura. Nada foi alterado no Studio nem em `src/`.

## 1. Identidade

| Item | Valor | Status |
|---|---|---|
| Bioma | Terras Corrompidas (divide o bioma com o Dragão Sombrio) | [OFICIAL] |
| Anatomia | Corpo **canino quadrúpede musculoso**, **três cabeças**, **pelagem escura** | [OFICIAL] |
| Papel | **Predador agressivo** que persegue e elimina **UM alvo prioritário**, com pressão coordenada das três cabeças | [OFICIAL] |
| Porte adulto | **12–16 studs de altura até os ombros** (não é comprimento) | [OFICIAL] |
| Comprimento total | Não fixado | [PENDENTE] |
| Tamanho dos filhotes / por estágio | Não fixado | [PENDENTE] |
| Estágios | Ovo, Bebê, Jovem, Pré-adulto, Adulto, Ancião (regra global) | [OFICIAL] |
| Montaria | A partir do **Adulto**, com **sela reforçada atrás dos três pescoços** | [OFICIAL] |
| Toxina | **SEM veneno biológico inato.** Veneno ofensivo só com afinidade Veneno (não tratar como vantagem automática) | [OFICIAL] |
| Uma só criatura | Conta como **UMA criatura ativa**: habilidades, energia e recargas são **compartilhadas** entre as cabeças; o jogador controla uma criatura, não três | [OFICIAL] |
| Cabeças | Cada cabeça **pode reagir/atacar inimigos PRÓXIMOS diferentes**, mantendo o foco no alvo prioritário. Não triplica ataques, energia, recargas nem número de criaturas | [OFICIAL] |
| Fraquezas | **Alto gasto de energia** em ataques combinados; **alcance limitado contra voadores** (pouco antiaéreo) | [OFICIAL] |
| Ataque básico | Fica fora dos slots de habilidade (regra global de 30/10) | [OFICIAL] |
| Padrões visuais | **Negro Carbonizado**, **Cinza Sepulcral**, **Vermelho Sombrio**. Só cosméticos: não definem elemento nem raridade | [OFICIAL] |
| Cores exatas de cada padrão | Não confirmadas | [PENDENTE] |
| Painel de referência | `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/04-bufalo-serpente-marinha-leviata-cerbero.png`, painel 04 ("muscular · corrompido · caçador"): três cabeças de lobo escalonadas (a central mais alta, rugindo), olhos vermelhos brilhantes, pelo negro desgrenhado com **placas/armadura corrompida** e **fissuras vermelhas incandescentes**, garras grandes, ombros enormes. Legendas: *three heads, muscular build, corrupted fur & armor, aggressive hunter, blighted lands*. Paleta: negros, vermelho escuro/vivo, roxo acinzentado | referência visual |

## 2. Elemento e habilidades

### Elemento
- **[OFICIAL — 30/10/2026]** Cada criatura tem **um único elemento natural**. Não há 2º/3º elemento, alternância nem fusão elemental no sistema atual.
- **Histórico (ficha-base, superado no ponto do número de elementos):** "Sombra, Fogo e Veneno; uma afinidade inicial + até duas desbloqueadas por missões".
- **[PENDENTE]** Qual é o elemento único do Cérbero Sombrio. A lista Sombra/Fogo/Veneno é o conjunto **autorizado** histórico; **não presumir** qual dos três (nem "Sombra" só pelo nome da forma — só os três Dragões tiveram o elemento fixado por nome).
- Se o elemento escolhido não for Veneno, o Cérbero **não envenena** (não há toxina biológica).

### Habilidades
- **[OFICIAL — 30/10/2026]** Mínimo **1 passiva + 3 ativas**; nomes, efeitos e quantidades aprovados criatura por criatura. Ataques básicos não ocupam slots.
- **[OFICIAL — ficha-base]** Quatro habilidades com nomes e papéis aprovados (o §0 diz para **não substituir os nomes oficiais por propostas antigas**). Métricas **[PENDENTE]**:
  1. **Mordidas Tríplices** — sequência de mordidas das três cabeças; foco num adversário, com reação possível contra outros próximos. **Não** equivale a três habilidades independentes.
  2. **Rugido Infernal** — intimidação e pressão ofensiva no entorno. Efeitos exatos variam com a afinidade e são propostas.
  3. **Investida Sombria** — avanço agressivo que aproxima o Cérbero do alvo para continuar a caçada. **Não** é teletransporte inevitável.
  4. **Fúria das Três Cabeças** — estado de ofensiva coordenada com **elevado gasto de energia**; não ignora recargas nem multiplica dano de graça.
- **[PENDENTE]** Como as 4 se encaixam no formato de 30/10: quais são ativas, e qual é a **passiva** (nenhuma passiva foi nomeada). Não inventar passiva.
- **[PROPOSTA]** Reações laterais das cabeças com **alcance curto** e dano subordinado ao combo, sem ataques automáticos ilimitados; ataques com **telégrafos e janelas de esquiva**.
- **[PROPOSTA — histórico, superada]** Transformações por elemento (Sombra/Fogo/Veneno) de cada habilidade e as seis fusões direcionais (Sombra+Fogo etc.). Contrariam a regra de elemento único. Não implementar. Podem servir de inspiração visual só depois que o elemento único for escolhido e o usuário aprovar.

### Pendências oficiais da ficha (§8)
- [PENDENTE] Regras de escolha do alvo principal; direção de cada cabeça; custos por combo; animações finais; tamanho dos filhotes; duração de debuffs; valores de ataque, distâncias e IA dos alvos.
- Prioridades declaradas: **acessibilidade visual dos ataques** e **desempenho com várias criaturas em cena**.

## 3. Atributos e combate (todos [PROPOSTA] / ilustrativos)
- **[OFICIAL — 24.1]** 6 atributos: Vida, Defesa, Força, Velocidade, Energia, Poder Elemental. Comparação entre Adultos nível 100.
- **[PROPOSTA — 15.1/24.2, NÃO APROVADA]** Números do Cérbero Sombrio:
  - escala 1–5: Vida 4, Defesa 3, **Força 5**, Velocidade 4, **Energia 2**, Poder Elemental 4;
  - absolutos: 4.600 HP, Defesa 130, Força 205, Energia 105, Poder Elemental 170;
  - velocidade: terra 39 studs/s (manobra 4), água 13 studs/s (manobra 2), sem voo.
- **[SIMULAÇÃO ILUSTRATIVA, NÃO OFICIAL]** §19.2: Cérbero Sombrio × Lobo Ancestral (DPS 110, exposição 31%, cura 5 HP/s, ~103 s).
- **[PENDENTE — §18.2]** Proteger o treinador sem invulnerabilidade: validar a **perseguição do Cérbero**; resistência a controle repetido e interrupção por aliados são obrigatórias.

## 4. Desempenho
- **[PENDENTE — §12]** Produção e performance: 18 jogadores + até 36 companheiros + fauna e boss exigem orçamento de animação/IA, colisões simplificadas, LOD e testes de carga, **"sobretudo com 3 cabeças"**.
- **[PROPOSTA]** Olhar/mira de cada cabeça procedural no cliente (sem clipe), como em `DOCS/CRIATURAS-RIG-ANIMACOES-PLANO.md`; LOD que congele as cabeças laterais à distância.

## 5. Mundo e habitat (segundo os registros do mapa)
- `DOCS/estado/mundo-corrompidas-auditoria.md` (M8, 26/10): marcadores **sem IA** — 3 territórios (planície, garganta, borda da floresta), 2 covis elegíveis (**Covil do Cérbero Leste e Oeste**, nas paredes do cânion) + refúgios (Salão das Raízes; Grande Câmara). Definições das cavernas em `Dados_Montagem/TerrasCavernasDef`.
- Não verificado se os covis comportam um adulto de 14–16 de ombro + cavaleiro. Conferir no Studio antes de usar.
- A IA do Cérbero não existe. Não há regras de ninho específicas dele (só as globais).

## 6. O que já existe no projeto
Nada em `src/`.

**Roblox Studio (registro de 26/10, não reverificado agora):**
- `Laboratorio_Criaturas.Cerbero_Sombrio_PROVISORIO` — clone do Lobo Ancestral aprovado: tronco ×1,4, patas mais grossas, 2 pescoços/cabeças laterais em Motor6D próprios (±35°), 14,0 de ombro.
- 13 animações testadas em Play (MordidasTriplices com as cabeças em sequência centro → esquerda → direita; RugidoInfernal; Observar com as laterais olhando para fora). **Investida Sombria e Fúria das Três Cabeças sem animação.**
- 3 padrões tingidos. Play/PC: patas sem afundar, FPS 49,5 com × 49,7 sem (sem custo mensurável).
- **Aparência aguardando aprovação.** Bug de escala dupla do `PipelineQuadrupede` (deitava 13 studs abaixo) foi corrigido em 26/10.

**Blender (`BLENDER/Criaturas/`):**
- **Rascunho C1 reprovado** (`scripts/cerbero_sombrio_PROVISORIO.py`, `_Provisorios/`): focinho de foca, membros tubulares, dobra no peito. **Não importar.**
- **Blockout** (`Blockouts/Cerbero_Sombrio/Cerbero_Sombrio_blockout.blend`): base canina + 3 cabeças, ombro 14, 27,5 × 17,9; cabeças na mesma altura (falha).
- **V2 (27/10)** `Cerbero_Sombrio_refinado.blend` / `_final.blend` / `_Export/Cerbero_Sombrio.glb` (2,0 MB): raiz única e maciça dos três pescoços, cabeças escalonadas (central mais alta; esquerda baixa; direita baixa e em ataque), crânios largos com rugas. 40 ossos, 28 animações. Ainda "cabeças parecidas com as do lobo" (LEIA-ME-FINAL).
- **V5 (27/10, a mais recente)** `Cerbero_Sombrio_refinado_v5.blend` / `_final_v5.blend` / `_Export/Cerbero_Sombrio_v5.glb` (4,1 MB): pelo curto + cartões de pelo, 29.876 tris (maior malha 14.000), 40 ossos.
  - Auditoria (`Blockouts/AUDITORIA-ANIMACOES-V2.csv`): **7 aprovadas / 17 pequenos ajustes / 4 refazer** (recontado no CSV em 17/11; a 1ª versão desta ficha dizia 6/18 por engano).
    - Refazer: **DeitarDescanso, Descanso, LevantarDescanso, InvestidaSombria**.
    - Aprovadas: Repouso, ReacaoGolpe, AtaqueBasico, MontadoRepouso, Alerta, MordidasTriplices, RugidoInfernal.
  - Build: `Blockouts/build/build_Cerbero_Sombrio.py` (+ `lobo_base.py`, `esqueletos.py`, `revest.py`, `pipeline_final.py`).
  - Faltando (RELATORIO-PRODUCAO-V5): cavidade da boca/dentes/língua para o rugido; **fissuras vermelhas** (material/VFX, não geometria); LOD e colisores.
- **Nada do V2/V5 foi importado nem testado no Roblox.**

## 7. Pendências para decidir com o usuário
1. **Elemento único** (Sombra, Fogo ou Veneno?).
2. **Kit no formato 30/10**: as 4 oficiais viram ativas? Qual é a passiva?
3. Qual base seguir: o provisório do Studio (clone do lobo) ou o V5 do Blender (rig de 40 ossos, ainda com aparência "de lobo")? Ou refazer a cabeça/rosto pelo painel 04.
4. Regra de alvo prioritário e alcance das reações laterais das cabeças (ficha diz [PENDENTE]).
5. Cores exatas dos 3 padrões.

## 9. Pedido Meshy (17/11) — M0
- Pedido: `DOCS/pedidos/2026-11-17-cerbero-sombrio-meshy.md`. Referência proposta salva em `DOCS/pedidos/2026-11-17-cerbero-sombrio-referencia.png` (1536×1024, convertida do WebP enviado pelo usuário). Pedido seguinte (rig/animações): `DOCS/pedidos/2026-11-17-cerbero-sombrio-animacoes.md`, só depois do aceite da malha.
- **V5 conferida no Blender (segundo plano, Workbench):** 29.796 tris, 8 malhas, 4 materiais (Pelo, Pelagem, Garra, Olho), rig de 40 ossos com 3 cadeias Pescoço1-2/Cabeça/Mandíbula (C/E/D), 28 ações. A bbox vai até 21,2 de altura (cabeça central). Visualmente a V5 está longe da referência: massa arredondada, cabeças fundidas no volume da juba, pelo em cartões irregulares. **Não serve de base para a malha nova**; o esqueleto de 40 ossos serve de referência de nomes e cadeias.
- **Referência para Image to 3D — pontos bons:** pose neutra em pé, 4 apoios visíveis, bocas fechadas, cabeça central mais alta e laterais voltadas para fora, placas só nos ombros e no dorso, fissuras pintadas (ficam na textura), fundo liso, sem acessórios.
- **Riscos:** vista 3/4 única (o lado e as patas de trás ficam ocultos e o Meshy vai inventar); os três pescoços somem numa juba única, sem vão entre as cabeças — a separação das cadeias vai depender dos pesos, não da geometria; focinho curto (mais "mastim" do que lobo); a juba alta atrás das cabeças invade a área prevista para a sela.
- Comparação com o painel 04: o painel é de ataque (bocas abertas, brilho forte); a referência nova é a versão neutra, adequada para rig. Mantém três cabeças escalonadas, olhos vermelhos, placas corrompidas e fissuras.
- **m1 gerado em 17/11**, com o "aprovo" do usuário e 36 créditos (saldo antes: 376). Detalhes em `BLENDER/Criaturas/Cerbero_Sombrio_Ref/LEIA-ME.md`.
  - Resultado: 1,38 M tris, 1 material com textura 4K e frente em −Y.
  - Fiel à referência nas cabeças, nas placas, nas bocas fechadas e nos 4 apoios.
  - Riscos: pescoços fundidos na juba, placas do dorso na área da sela, boca sem interior e ponta da cauda em cone.
  - m1 aceito pelo usuário em 17/11 ("Aceito, seguir LOW").
  - **low_v2** (18 mil tris) aprovada.
  - **low_v3d** (17/11) aguarda revisão: 21.052 tris (Cabeças 11,5k + Corpo 6,5k + Bocas 3,1k), três bocas abríveis com dentes, gengiva e língua, e cauda arredondada.
  - As placas do dorso foram mantidas. **Decisão do usuário (17/11): a sela vai por cima da armadura do dorso.**
  - **Rig (17/11):** `BLENDER/Criaturas/Cerbero_Sombrio_Ref/rig/`.
    - 38 ossos; cada cabeça com Pescoco1/2, Cabeca e Mandibula próprios.
    - Escala proposta: ×12,7, ~14 studs de ombro.
    - Poses de teste medidas.
    - GLB `VALIDO` na reimportação.
    - r2: frente do lábio da C corrigida.
  - **Piloto de animações (17/11):** Repouso, Andar, Corrida e Mordida.
    - QA: IK ≤ 0,001, sem escorregar, patas sem atravessar o chão.
    - JSON conferidos por reimportação; vídeos em `rig/revisao_piloto/`.
    - **ACEITO pelo usuário em 17/11.** Studio não testado.
  - **Lote 2A (17/11):** Trote, Partida, Freada, VirarE/D e Salto em `rig/clipes_L2A/`.
    - QA: IK ≤ 0,001 e escorregão ≤ 0,03 stud/s.
    - Encaixes Partida→Corrida→Freada→Repouso conferidos.
    - Loop das cabeças na Corrida corrigido.
    - **ACEITO em 17/11.**
  - **Lote 2B (17/11):** Alerta, Observar, ReacaoGolpe, Deitar, Descanso e Levantar em `rig/clipes_L2B/`, que é a base com os 16 clipes.
    - Deitado esternal calibrado pela malha.
    - Encaixes conferidos.
    - **ACEITO pelo usuário** (deitado em "esfinge" mantido).
  - **Lote 3 (18/11):** `rig/clipes_L3/` com 26 clipes. **ACEITO pelo usuário**; é a base atual.
    - Ataques básicos em CAMADA para atacar em movimento (pedido do usuário): Mordida C/E/D e Garra E/D.
    - Poderes da v6.2: Chamas Tríplices (3 disparos marcados), Fúria (Rugido, loop e saída) e Investida Sombria (encaixa na Corrida).
    - Elemento único e kit oficial seguem pendentes.
  - **Aura permanente de FOGO A3 APROVADA (18/11).**
    - Está em `aura/CR_Cerbero_Fogo_A3.blend`.
    - Fogo na pelagem da juba à cauda, mais 49 chamas viradas para a câmera; segue a referência do usuário, que substitui as linhas discretas da v6.2 §5.9h.
    - Estimativa de partículas: PC ~235 (acima da meta de ~150) e celular ~70. Ainda a medir no Roblox.

## 8. Próximos passos sugeridos (aguardando aprovação)
1. Revisão visual do V5 (render em vistas) contra o painel 04: cabeças de predador distintas do lobo, placas corrompidas, boca aberta com dentes.
2. Refazer os 4 clipes reprovados e ajustar os 18 "pequenos ajustes"; criar Investida Sombria e Fúria das Três Cabeças no padrão de movimento das criaturas.
3. Importar no Studio (com o Studio livre e backup confirmado), validar escala 12–16, pelo, rig e FPS.
4. Só depois das decisões de elemento/kit: VFX das fissuras, sons (rugido de 3 vozes) e IA de caçada com foco prioritário + reações laterais curtas, autoridade no servidor.

### Decisão do usuário (18/11): Bola Infernal substitui as Chamas Tríplices
- **Nova ideia:** as três cabeças formam juntas uma bola de fogo gigante que segue o alvo, "brilhante e real". Ela substitui o poder de projéteis (Chamas Tríplices).
- **Nome "Bola Infernal":** PROVISÓRIO.
- **Números:** dano, recarga, velocidade, curva, alcance e raio de acerto continuam [A TESTAR].
- **Prévia de Blender:** clipe `BolaInfernal` em `BLENDER/Criaturas/Cerbero_Sombrio_Ref/rig/clipes_L3r5`; efeitos em `aura/fx_bola_infernal/`.
- **Studio:** pendente; a perseguição real do alvo será validada lá.
- **18/11, r2 (pedido do usuário: maior, mais brilhante, três cabeças rugindo formam uma bola gigante):** clipe `BolaInfernalR2` (rig/clipes_L3r6) + `aura/fx_bola_infernal_r2.py`. Aguarda revisão.
- **19/11, r3 (pedido: maior, redonda e brilhante com aspecto de fogo):** esfera de raio 10 sem cauda, `aura/fx_bola_infernal_r3.py`. Aguarda revisão.
- **19/11:** r3 ACEITA pelo usuário, "porém mais rápido" → r3b (voo 30 studs/s, curva 130°/s), `aura/fx_bola_infernal_r3b.py`.
- **19/11:** velocidade da r3b APROVADA pelo usuário (30 studs/s, curva 130°/s, ainda a testar no Roblox). Visual oficial da Bola Infernal = r3/r3b.

### [PROPOSTA] 19/11 — nome e números da bola de fogo (aguarda decisão do usuário; NÃO oficial)
Base de comparação: Chamas Tríplices v6.2 (3 × 0,6× = 1,8× total, queimadura leve 3 s, recarga 8 s, energia 22), Mergulho Abissal (explosão 1,7×, recarga 26 s), Carga de Chifres (1,9×, recarga 10 s).
- **Nome:** recomendado **Sol Infernal**. Alternativas: Esfera das Três Chamas, Astro Infernal. Evitar "Coração Infernal" (já é do Dragão das Montanhas).
- **Carga:** 3,35 s até o disparo (clipe aprovado), visível a todos (telegrafada).
  - Pode andar a 60% da velocidade, sem correr nem saltar (versão em camada).
  - Atordoado/derrubado durante a carga → a bola se desfaz sem dano e a recarga fica pela metade.
- **Dano:** 1,8× no alvo atingido + explosão raio 12 studs com 1,0× nos demais (sem acumular no alvo principal) + queimadura leve 3 s.
- **Voo:** 30 studs/s, curva 130°/s (aprovados no Blender), alcance 50 studs (vida ~1,7 s), raio de acerto 8 studs (visual 10).
- **Mira:** alvo travado → mouse → câmera; sem alvo segue reto. Alvo morre/some → segue reto e explode no fim do alcance.
- **Obstáculos:** NÃO atravessa: explode ao tocar terreno ou parede sólida (contra-jogo: se esconder atrás de cobertura).
- **Uma bola só:** não divide alvos entre as cabeças (diferente das Chamas).
- **Recarga 14 s, energia 35** (era 8 s / 22: um golpe maior, mais lento e mais fácil de prever).
- Tudo validado no servidor (dano, acerto, recarga e energia); números [A TESTAR] no Studio, inclusive PvP.
- **19/11 — DECISÃO DO USUÁRIO: o poder se chama "Sol Infernal"** (substitui o nome provisório "Bola Infernal"). Os números acima continuam [PROPOSTA] até aprovação explícita.
- **19/11 — NÚMEROS APROVADOS pelo usuário** para o **Sol Infernal**:
  - **Carga e disparo:** carga de 3,35 s, andando a 60% da velocidade, sem correr nem saltar. Se for interrompida, a bola se desfaz e a recarga cai pela metade.
  - **Dano:** 1,8× no alvo, mais explosão de raio 12 studs com 1,0× nos demais, e queimadura leve por 3 s.
  - **Voo:** 30 studs/s, curva de 130°/s, alcance de 50 studs e raio de acerto de 8 studs.
  - **Mira:** alvo travado, depois mouse, depois câmera. Não atravessa obstáculos. É uma bola só.
  - **Custo:** recarga de 14 s e 35 de energia.
  - **Validação:** autoridade no servidor; valores sujeitos a ajuste de balanceamento no teste do Studio, inclusive PvP.
