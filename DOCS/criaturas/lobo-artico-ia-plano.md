# Lobo Ártico selvagem — diagnóstico da IA (r1e), correção local r2c e plano de comportamentos (19/11/2026)

Pedido: "Lobo Ártico — corrigir a IA e aproximar o comportamento de lobos reais".

Esta rodada autoriza **revisão e correção local**. Nada foi instalado nem testado no rpg_roblox. Sem commit.

Legenda:
- **[CÓDIGO LOCAL]** existe só nos arquivos;
- **[INSTALADO]** está no place;
- **[TESTADO]** tem prova em Play;
- **[SIMULADO]** passou só no modelo 2D local (não é o Roblox).

## 1. Fontes lidas

- **Regras do projeto:** CLAUDE.md, DOCS/ORGANIZACAO-CHATS.md, lobo-artico.md §8.77–8.78, REFERENCIAS_PODERES_E_EFEITOS.md (§0, §0b, §1, §3) e ESTATISTICAS_POR_IDADE.md.
- **RPG_01/RPG_02:** os arquivos `..._ATUALIZADO.docx` citados em ORGANIZACAO-CHATS **não estão em Downloads**. Li `RPG_01_Mundo_e_Sistemas.docx` e `RPG_02_...docx` (22/10). As regras abaixo vêm dessa versão. **Conferir com a ATUALIZADA quando ela estiver disponível.**
- **Vídeo:** `review/rpg_ia/video_ia_alcateias.mp4` e os quadros brutos `review/rpg_ia/defesa/`, vistos diretamente. A sobreposição foi confirmada: o jogador fica dentro do corpo do Guardião e o lobo continua andando por cima dele.
- **Comportamento real** (lido e resumido por agente; só paráfrase):
  - [C] https://wolf.org/wolf-info/basic-wolf-info/biology-and-behavior/communication/
  - [E1] https://wolf.org/wolf-info/wolf-ethogram/
  - [E2] https://wolf.org/wolf-info/wolf-ethogram/wolf-ethogram-t-z/
  - [N] https://www.nps.gov/articles/life-of-a-wolf.htm
  - [W] https://wdfw.wa.gov/species-habitats/species/canis-lupus
- **Filmagens reais com minutagem: NÃO verificadas nesta rodada.** Não registro links de vídeo nem minutagens sem tê-los assistido; isso fica pendente (§7).

### 1.1 Regras oficiais relevantes (RPG_01 §8, versão de 22/10)

- "Populações selvagens moderadas em grupos adequados ao habitat; comportamentos de caça, descanso, alimentação, patrulha e territorialidade. **Nem todo grupo possui um ninho.**"
- **Quantidade de ninhos com ovos varia com o número de jogadores.** As faixas 1–3: 2 … 15–18: 6 são [PROPOSTA].
- Reaparecimento em 30–60 min; **novos ninhos distantes da localização anterior**, em habitats coerentes.
- Achados por pistas naturais, sem coordenada.
- **Guardiões SEMPRE percebem a coleta do ovo. A defesa é coordenada, com perseguição limitada territorialmente.**
- O primeiro a concluir a coleta ganha; **guardiões selvagens adultos** não podem ser capturados diretamente.
- Elemento inicial influenciado pelos guardiões (dentro do conjunto autorizado).

### 1.2 Conflitos da implementação atual (r2 do spawner) com essas regras

| # | Implementação atual | Regra | Situação |
|---|---|---|---|
| R1 | Ovo nas 3 tocas, sempre | "Nem todo grupo possui ninho"; quantidade conforme jogadores | **CONFLITO** — decidir com o usuário |
| R2 | Ovo reaparece na mesma toca | "Novos ninhos distantes da localização anterior" | **CONFLITO** |
| R3 | Guardião é Pré-adulto | Guardiões "adultos" | **A CONFIRMAR**: a regra fala dos adultos não capturáveis; não diz que só adultos guardam |
| R4 | Alerta a 40 do ovo + coleta | "Sempre percebem a coleta" | ok (o `PromptButtonHoldBegan` marca o coletor) |
| R5 | Coleira 75 do ovo | Perseguição limitada territorialmente | ok em parte (achado 4 deixa escapar) |
| R6 | Nenhum item entregue | Primeiro a concluir ganha | depende de inventário (fora do escopo) |

## 2. Diagnóstico dos 10 achados (r1e, `IA_LoboArtico.server.luau`)

| # | Achado | Prova (linha na r1e) | Na r2c |
|---|---|---|---|
| 1 | Dentro de 9,5 (do PIVÔ, nas ancas) manda andar para o alvo → atravessa | 252–255; vídeo `defesa` | **corrigido** [CÓDIGO LOCAL][SIMULADO] |
| 2 | Perder vida culpa o jogador mais perto a 30 | 186–190 | plano §4.5 (precisa do agressor validado pelo dano) |
| 3 | Percepção sem linha de visão; alvo compartilhado sem revalidar vida | 156–166, 177–182 | plano §4.3 |
| 4 | Perseguição continua além da coleira se o alvo estiver perto do lobo; um membro apaga o alvo de todos | 284, 287 | plano §4.6 |
| 5 | NoPath vira linha reta; cadeia da toca com agente raio 1/altura 3 não prova passagem do adulto | 85, 108–118 | **corrigido em parte**: linha reta só com Spherecast livre; Blockcast do corpo da idade limita a cadeia [CÓDIGO LOCAL, não testado] |
| 6 | 3 travamentos devolvem `true` (= chegada) → dorme/fareja no lugar errado | 94, 228 | **corrigido**: devolve `"falhou"` e a rotina é abandonada [CÓDIGO LOCAL] |
| 7 | Esperas bloqueantes; callback atrasado pode voltar pose antiga | 67, 237, 250, 262 | **em parte**: token de geração nas poses; Uivo não trava a IA. Despertar (2,8 s) e nocaute (60 s) seguem bloqueantes → plano §4.8 |
| 8 | Alerta = Defender direto; aviso do Líder = Uivo Boreal com bônus | 249, 279–285 | plano §4.4 |
| 9 | Caçar = ir à zona e farejar; não há presa | 213, 230 | plano §4.2 (depende da fauna da Tundra) |
| 10 | Tamanho 3, papéis fixos, nocaute 60 s, raios = propostas; Pré-adulto guardião; ovo sem item | spawner r2 | decisões do usuário (§6) |

## 3. Primeira entrega — correção local r2c

**Arquivos:**
- `studio/selvagem/IA_LoboArtico.server.luau` r2c (cópia da r1e: `IA_LoboArtico_r1e.server.luau`);
- `studio/Controle_Servidor.server.luau` r7 (cópia da r6b: `Controle_Servidor_r6b.server.luau`).

**Interface nova:** `IA_Olhar(direção)` (BindableEvent na pasta do lobo).
- **Consumidor único:** `IA_LoboArtico`. Só vale sem jogador no controle, então o lobo de ensaio não muda.
- Abaixo de 60° gira 60°/s no lugar; acima usa o clipe aprovado VirarEsquerda/VirarDireita. Não há giro instantâneo.

### A. Contato

- **Medida:** distância do FOCINHO (6,2 × Escala, o mesmo valor do Kit) ao centro do alvo. O alcance da mordida é o do Kit (3,5 × Escala + 1,5).
- **Mordida:** só a ≤ 30° da frente; o cone do Kit é de 37,5°. Intervalo de 0,5 s, igual ao do Kit. Dano, recarga e alcance não mudaram.
- **Histerese do contato:** entra a ≤ 3,2 e sai a > 4,6 (× Escala). Em contato o lobo **para e só se orienta**.
- **Aproximação:** entre o contato e 8 × Escala aproxima andando (morde andando se alcançar). Se o alvo anda (velocidade > 2,5), acompanha em trote.
- **Perseguição:** além disso, trote; corrida acima de 25 × Escala.

### B. Alvo sob o tronco ou colado no focinho

- O lobo reposiciona para uma **estação**: entre 8 pontos a (6,2 × Escala + 1,0 + 0,8 × Escala) do alvo, o de menor custo (virar agora + andar + virar no fim).
- Rota que passa por cima do alvo é penalizada.
- A estação fica fixa por até 8 s, ou até o alvo andar mais de 3.
- Repulsão de membros da alcateia a menos de 3,5 × Escala.

### C. Caminho

- `irPara`/`irParaFora` devolvem `"chegou"`, `"andando"` ou `"falhou"`.
- NoPath só vira linha reta se um Spherecast (raio 0,9 × Escala, a 2,2 × Escala do chão) está livre.
- A falha grava `IA_Falha` com motivo e posição.
- **Rotina:** a falha faz abandonar a rotina; na Patrulha, pula o ponto.
- **Defesa:** a falha faz o lobo voltar ao posto, 6 studs do ovo na direção da ameaça, e encarar a ameaça.

### D. Toca por porte

- A cadeia da toca é conferida com Blockcast de uma caixa do corpo da idade (2,0 × 4,0 × Escala) entre pontos seguidos.
- O 1º trecho bloqueado vira o limite (`IA_CadeiaBloqueio`, `IA_CadeiaLimite`), e destinos além dele param no último ponto válido.
- **Não testado:** precisa de Play. Se a geometria impedir um porte, o ponto será documentado antes de qualquer mudança no mapa ou no tamanho.

### E. Callbacks e espera do Uivo

- Token de geração: o `task.delay` de uma pose antiga não toca mais depois de troca de pose, ameaça ou remoção do lobo.
- O Uivo de aviso não trava a IA (antes eram 6,9 s de `task.wait`).

### Testes locais (feitos)

**`conferir_blocos_luau.py`** (blocos abertos × fechados, sem compilador):
- OK em IA r2c, IA r1e, spawner, Controle r7/r6b, Kit r14 e Uivo r7;
- a r1e, que já compilava no Studio, também passa.

**`simular_contato_r2.py`** (modelo 2D da decisão + cinemática simplificada; **não é o Roblox**):

| Cenário | r1e: tempo dentro do corpo / acertos | r2c: tempo dentro / acertos |
|---|---|---|
| Alvo parado a 20 | 6,97 s / 3 | **0 s / 20** |
| Alvo andando de lado (4/s) | 0 s / 19 | 0 s / 13 |
| Alvo foge correndo (16/s) | 0,47 s / 2 | 0 s / 2 |
| Alvo recuando devagar | 6,83 s / 12 | **0 s / 15** |
| Alvo colado sob o tronco (começa dentro) | 3,77 s / 3 | 0,97 s / 1 (tempo para sair de baixo) |
| Alvo 4 studs atrás do lobo | 2,27 s / 2 | 0 s / 2 (1º acerto só aos 12,5 s: o clipe Virar faz 90° em 3,1 s) |
| Pré-adulto (0,85), alvo parado | 3,47 s / 6 | **0 s / 19** |

**Limites do modelo:** sem terreno, sem colisão com paredes, sem latência de rede, e o jogador não reage.

### Aceite em Play (precisa de autorização da etapa)

- Aproximação sem sobreposição visível e mordida sincronizada ao contato.
- Caminho bloqueado tratado (`IA_Falha`) e transições sem travamento.
- Cenários: alvo parado, andando, correndo, colado, recuando e atrás de parede; dois jogadores; alvo morto ou desconectado; 3 membros; entrada estreita; retorno à toca.

## 4. Plano dos comportamentos seguintes (para aprovação)

### 4.1 Matriz gatilho → percepção → postura/ação → interrupção → saída → teste

Os clipes **existentes** estão em `ReplicatedStorage.Animacoes_LoboArtico`:
- **Locomoção:** Repouso, Andar, Trote, Corrida, Arrancada, Frenagem, VirarE/D e as transições de marcha;
- **Vida:**
  - Deitar, Descanso, Adormecer, Dormindo, Despertar, LevantarDeitado;
  - Sentar, Sentado, LevantarSentado;
  - Farejar/Farejando/PararFarejar, Comer/Comendo/PararComer, Beber/Bebendo/PararBeber;
  - Uivar/Uivando/PararUivar, Sacudir;
- **Ataque e kit:** Mordida1/2 (+_Corrida), Piscar, Cometa×3, Avalanche×2.

**AUSENTES**, que seriam lote novo de clipes no Blender:
- Alerta (congela, orelhas eretas, olhar fixo);
- Rosnar/ameaça (lábio arregaçado, pelos do dorso eriçados, cauda alta, pernas rígidas);
- Latido / latido-uivo (bark-howl);
- Giro rápido de confronto ("whirl");
- Recuar (andar de ré);
- Postura de cauda (alta/baixa como camada);
- Saudação e submissão social;
- Marcação de cheiro;
- Espreita, perseguição de presa e salto de captura;
- "Agarrar e sacudir".

| Comportamento | Gatilho | Percepção | Postura/ação (clipes) | Interrupção | Saída | Teste |
|---|---|---|---|---|---|---|
| Patrulha/viagem | rotina | — | Andar/Trote pela rota, pausas com Farejar; um lobo atrás do outro com distância individual ([N]: o líder costuma ir à frente) | ameaça, dano | fim da rota ou falha → próxima rotina | 3 membros sem fila de clones nem colisão; pausas naturais |
| Atenção | jogador **visível** (raycast à cabeça) a < raio | linha de visão + memória da última posição (8–15 s) | parar, olhar (IA_Olhar), Piscar; **falta clipe de Alerta** | some de vista, ameaça maior | volta à rotina | jogador atrás de parede não dispara |
| Investigação | atenção persistente sem ameaça | mesma + rastro/pegada (se existir sistema) | aproxima-recua, Farejar, circular | ameaça | volta | não ataca quem só passa longe |
| Aviso/ameaça | intruso perto da toca/ovo | visão + distância à toca | parar entre intruso e toca; **rosnar/latido-uivo** ([C]/[W]: perto da toca o lobo late-uiva, mantém posição e segue de longe até a pessoa sair); 1 indivíduo uiva, não todos | intruso avança, ataca ou começa a coleta | intruso sai: segue de longe, depois volta | aviso antes de atacar; nem todos uivam |
| Defesa do ovo | **coleta iniciada** (oficial: sempre percebida) ou dano validado | evento do servidor | 1 fica no ovo (responsável), os outros interceptam; mordida com contato r2c | alvo morto/desconectado, fora da coleira | limpa o alvo, volta ao posto | 2 jogadores: só o coletor/agressor é alvo |
| Retaliação | dano com agressor **validado** pelo servidor | evento de dano com quem causou | igual à defesa | idem | memória expira (15–30 s) | inocente próximo não é punido |
| Caça | fome/rotina [PROPOSTA] + presa da fauna da Tundra | visão/odor da presa | espreita → perseguição → mordida; **depende da Lebre/Cabra (outro chat)** | ameaça | presa capturada/escapou | contrato com a fauna (`Criatura`, `PresaPequena`) |
| Descanso/sono | rotina; mais no meio do dia e na madrugada ([C]/[N]: mais ativos ao entardecer e à noite; uivos à tarde e de manhã cedo) | — | Deitar → Descanso/Dormindo; despertar por ruído/ameaça | ameaça → Despertar sem bloquear a IA | rotina | ameaça durante o sono cancela a pose |
| Retirada | vida baixa ou fora do território | — | recuar para a toca | — | recupera | não prende o jogador na memória |

### 4.2 Movimento

- Aceleração e frenagem pelos clipes de transição que já existem (Arrancada, Frenagem, Trote↔Andar).
- Viradas em curva com o giro andando.
- Distância individual entre membros (repulsão já na r2c) e trilha atrás do líder com deslocamento lateral.
- Pausas naturais na rota (farejar, olhar).
- **Giro de combate rápido:** o clipe Virar (90° em 3,1 s) é lento para confronto. Proposta: clipe novo "giro de confronto" ou tocar Virar mais rápido só em combate (decisão visual).

### 4.3 Percepção

- Visão por raycast olhos → cabeça do jogador (paredes bloqueiam), cone frontal largo e raio menor atrás.
- Memória da última posição por tempo limitado.
- **Som e odor só se o sistema existir ou for aprovado.** Medir distância não é ouvir nem farejar através de parede.

### 4.4 Escalada

- Atenção → investigação → aviso → defesa, cada etapa com tempo mínimo.
- A coleta do ovo e o dano validado pulam direto para defesa: regra oficial e contexto.
- **O aviso não precisa ser o Uivo Boreal (poder com bônus).** Proposta: latido/rosnado sem efeito de poder, se houver clipe/som. Usar o poder só em combate: **decisão do usuário**.

### 4.5 Atribuição do agressor

- Precisa de um evento de dano com a origem (quem causou), validado no servidor.
- Hoje o `Kit_Servidor.ReceberDano` não recebe a origem; outros sistemas de dano do jogo podem não usar essa função. **Sistema compartilhado → aprovar o contrato.**
- Sem origem confiável: **investigar** (Atenção), nunca punir o mais próximo.

### 4.6 Coordenação, retirada e limpeza

- **Alvo compartilhado:**
  - guardar UserId, e não o nome;
  - revalidar vida e conexão a cada tick;
  - só quem criou ou o tempo de expiração limpa o alvo.
- **Coleira:** sair da coleira sempre encerra a perseguição; a exceção "perto do lobo" sai.
- **Responsável pelo ovo:** um membro fica sempre (quantidade, papéis e distâncias = [PROPOSTA][A TESTAR]).
- **Limpeza segura:** morte ou desconexão do alvo, caminho inviável e fim da ameaça limpam o estado.

### 4.7 Companheiro domesticado

- Não existe contrato para o Ártico.
- O Lobo Ancestral tem `kit/CONTRATO-CONTROLE-PORTE.md`, o atributo `Criatura` e o `acaoIA` no `LoboKit_Servidor`.
- **Proposta:** levantar esses contratos (aliados, agressor, ordens oficiais "atacar/defender/seguir/recuar/manter posição/usar habilidade" do RPG_01 §9) antes de implementar.

### 4.8 Bloqueios restantes

- Despertar/levantar (2,8 s) e nocaute (60 s) usam `task.wait`.
- **Proposta:** máquina de estados com prazos (sem esperar), checando a geração e a remoção do lobo.

## 5. Desempenho (a medir na integração)

- Custo do `ComputeAsync` por lobo (repath 2,5 s) e frequência dos ticks: 0,3 s ativo e 2 s dormente.
- 3 alcateias × 3 lobos em PC.
- Celular só emulado.

## 6. Decisões do usuário (não inventar)

1. **Ovos:** em quantas tocas, quantos conforme jogadores, e reaparecer em outra toca (regras R1/R2).
2. **Guardião:** só adulto ou Pré-adulto pode guardar (R3).
3. **Alcateia:** tamanho e papéis (hoje 3: Líder, Guardião, Membro).
4. **Nocaute:** vida 0 do selvagem (hoje deita 60 s e se recupera) [PROPOSTA]; morte e captura são proibidas pela regra.
5. **Aviso:** com o Uivo Boreal (poder) ou com vocalização sem efeito.
6. **Dano em jogador:** hoje mordida 10 (Adulto) / 8 (Pré-adulto), que já derruba em ~15 s com 2 lobos.
7. **Lote novo de clipes:** Alerta, Rosnar, Latido-uivo, Giro de confronto, Recuar, camadas de cauda.

## 7. Pendente desta rodada

- **Filmagens reais:** links e minutagens verificadas de lobos em toca, aviso e defesa. Precisa assistir; não foi feito.
- **Comparação visual:** com `REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png`. Esta entrega não muda visual nem clipes; a comparação lado a lado volta nas etapas visuais.
- **Instalação e Play da r2c no rpg_roblox:** precisa de autorização, reserva e confirmação do place.

## 8. Teste autorizado no rpg_roblox (20/11/2026: "Autorizo o teste")

**Preparação:**
- Place confirmado: rpg_roblox, placeId 114230639394991, Studio reaberto.
- Reserva feita em `studio-em-uso.md`.
- Instalado só em `ServerStorage.LoboArtico_Selvagem_Modelo` (IA, Controle) e em `Workspace.Teste_LoboArtico.Controle_Servidor`.
- Antes de instalar: a fonte do place foi conferida igual à r1e/r6b, as novas compiladas no `loadstring`, e o backup ficou em `ServerStorage.LoboArtico_Backups.Antes_IA_r2c_20_11`.
- Medidor e painel de diagnóstico criados **só durante o Play**. Para medir dano, a regeneração e a vida do jogador foram mudadas só no Play.

### Revisões feitas durante o teste (todas com cópia local)

| Rev. | Achado em Play | Correção |
|---|---|---|
| r2c→r2d | A cadeia da toca ficava "bloqueada" porque usava a altura dos marcadores | caixa medida do CHÃO real, até a altura da cabeça (6,0 × Escala) |
| r2e | Girar no lugar (clipe Virar 3,1 s) contava como travamento → "travado 3x" → desistia de alvo andando | virar não é travar; perseguição direta em linha livre (sem recalcular o Pathfinding a cada tick) |
| r2e | Corrida pela velocidade total piorou o alvo circulando | corrida só se o alvo FOGE (velocidade radial) ou está longe |
| r2f | Na boca da toca o lobo "perseguia" para dentro (os pontos da cadeia ficam a céu aberto) | "dentro" exige teto |
| r2g | Trotando, passava ao lado do alvo | alvo a < 15 e > 50° de lado → para e vira |
| r2h | Uivo pedido perto: a Frenagem levava o corpo para cima do jogador | uivo de aviso só a > 25 do focinho |
| r2i | Beiral de rocha na boca da toca contava como "dentro" | "dentro" também exige índice > 3 na cadeia; perto (< 20) segue direto |
| r2j | Rótulo `IA_Contato` velho depois de sair da defesa | limpo fora da defesa (**instalado, não testado em Play**) |

### Resultados em Play (medidor no servidor, amostra a cada 0,1 s)

| Cenário | Versão | Jogador dentro do corpo | Contato / mordidas | Observação |
|---|---|---|---|---|
| A — alvo parado a 14, campo aberto | r2d | **0,0 s** | contato 21 s; **38 acertos (380 de dano)** | aproximou 1,4 s e parou a 3,2 do focinho |
| A — alvo parado a 27 do ovo, dentro da toca | r2d | 0,0 s | nenhum | adultos param no limite da toca ("encara") — ver §8.1 |
| B — alvo andando em círculo (r 12, 8/s) | r2c → r2e | 0,2 → 0,0 s | 4 acertos | travamento falso corrigido; ainda fraco: o giro aprovado (90° em 3,1 s) não acompanha alvo circulando |
| C — alvo foge a 16/s | r2e | 0,0 s | 0 | corre (20,4/s) e não alcança em 10 s; esperado |
| C' — alvo sai: volta à rotina | r1e/r2d | — | — | em 12 s voltou a Patrulhar/Guardar (nesse teste o alvo da alcateia foi limpo à mão) |
| A na boca da toca, alvo parado a 28 | r2g | 6,5 s (o uivo freando) | contato no fim | corrigido na r2h |
| idem | r2i | 0,0 s | nenhum | alvo fora da coleira e a > 22: o lobo alterna defesa/rotina (achado 4) |

**Evidências:**
- vídeo de diagnóstico normal e lento: `review/rpg_ia_r2/video_diagnostico_r2.mp4`;
- quadros: `review/rpg_ia_r2/contato*`.

### 8.1 Geometria real da toca da Floresta (medida em Play; mapa NÃO alterado)

- **Túnel de entrada:** teto **5,8–6,1** acima do chão em (−1378…−1381, −3910); ~7,6 em (−1404, −3915). Largura ≥ 12.
- **Descanso → Abrigo:** teto **5,7** em (−1506, −3943) e **5,9** em (−1538, −3954). Largura ≥ 10.
- **Lobo Adulto em pé:** cabeça a 6,1 e base das orelhas a 7,0 acima do chão; coluna a 4,6. Com 6,0 de altura da cabeça, a cadeia bloqueia o Adulto no túnel e o Pré-adulto (0,85) mais adiante.
- **Até a r1e:** os lobos atravessavam o teto com a cabeça. O Controle não colide; só segue o chão.
- **Opções (decisão do usuário; não fiz nenhuma):**
  - (a) alargar o teto da toca nesses trechos (mudança de terreno da Tundra);
  - (b) clipe novo de passagem agachada (cabeça baixa) para túneis;
  - (c) os adultos dormem e guardam na entrada/câmara de descanso, e só filhote/pré-adulto vão ao abrigo do ovo;
  - (d) aceitar a cabeça atravessando a rocha.

### Aceite desta etapa

- **Cumprido:**
  - aproximação sem sobreposição visível no contato frontal (A: 0 s, 38 acertos);
  - mordida sincronizada ao contato;
  - caminho bloqueado tratado como falha explícita (`IA_Falha`; abandono controlado);
  - transições sem travar a IA (uivo não bloqueia; poses antigas não voltam).
- **Não cumprido:**
  - alvo circulando de perto: precisa de giro de confronto rápido, que é clipe ausente;
  - entrada na toca para adultos: geometria (§8.1);
  - saída e histerese da ameaça (achado 4).
- **Não testado:**
  - dois jogadores (o Play solo do Studio tem 1 jogador; exige Team Test);
  - alvo morto ou desconectado;
  - alvo atrás de parede (percepção sem linha de visão é o achado 3);
  - custo de Pathfinding medido;
  - celular.

## 9. r3 local — ameaça antes do ataque e distância de confronto (20/11/2026)

O pedido de 20/11 diz que o lobo chega perto demais e passa direto ao ataque. Esta rodada é **local**: nada foi instalado no Studio, nada foi commitado.

**Causa, conferida na r2j:**
- Na r2j não existia aviso nenhum. Um jogador a até 40 do abrigo entrava direto em `defender()`.
- O único "aviso" era o Uivo Boreal, que é poder com bônus e só tocava a mais de 25 do focinho.
- A distância de 3,2 do focinho é a de **morder**, não a de confronto. Por isso o jogador via o lobo vir até ele e morder.
- Esta causa foi deduzida lendo o código e o vídeo r2. O relato novo **não foi reproduzido** em Play nesta rodada, porque o Play não estava autorizado.

### 9.1 Fontes do comportamento real

Lidas em 20/11 no International Wolf Center (paráfrase):

**Etograma** ([wolf.org/wolf-info/wolf-ethogram](https://wolf.org/wolf-info/wolf-ethogram/) e as páginas A-G, H-P, R-S, T-Z):
- A ameaça é uma **sequência de avisos** antes da agressão: olhar fixo (*Stare*), rosnado (*Growl*), focinho arregaçado mostrando caninos (*Snarl*, *Lip Curl*), pelos do dorso eriçados (*Hackles*) e ficar alto (*Stand Tall*).
- Encarar frente a frente com postura tensa (*Face Off*) vem com cauda T1–T2 (alta ou na linha do dorso). Orelhas: *Ears Pricked*, em pé e para a frente.
- O ataque real é **raro**. Agressão vocal e olhar são mais comuns que contato físico.
- **Whirl**: giro rápido em círculo ou meio círculo, para confrontar. **Lunge** e **Snap**: avanço curto e mordida com pouco ou nenhum contato.
- **Escape/Leave**: sair da situação.

**Comunicação** ([página de comunicação](https://wolf.org/wolf-info/basic-wolf-info/biology-and-behavior/communication/)):
- **Latido** e **rosnado** são avisos. O latido ou o latido-uivo pode mostrar agressão em defesa da alcateia ou do território, e a mãe late para os filhotes ao perceber perigo.
- O **uivo defensivo** reúne a alcateia e protege filhotes e carcaças. Fica longe do intruso; não é aviso de perto.

**Consequências para o jogo:**
- O aviso de perto é **corpo + rosnado/latido**, e não o Uivo Boreal.
- O ataque vem depois da insistência.
- Recuar encerra o confronto.

**Filmagens com minutagem verificada: NÃO feitas.**
- As páginas lidas não têm vídeo.
- Não assisti a nenhum vídeo, então não cito minutagem.
- Sobra a página de vídeos do próprio IWC, <https://wolf.org/meet-our-wolves/wolfvideos/>, ainda não lida.

### 9.2 Estados (pasta da alcateia: atributo `Tensao`)

| Nível | Entra quando (padrão) | O que cada papel faz | Sai |
|---|---|---|---|
| Calmo | — | rotina (Dormir/Patrulhar/Caçar/Guardar) | — |
| Atenção | intruso **visto** a ≤ 48 do abrigo ou ≤ 30×e do focinho de algum membro | todos param e encaram; o Guardião volta ao lado do ovo; clipe `Alerta` se existir | 4 s sem gatilho → Calmo |
| Ameaça | intruso a ≤ 34 do abrigo ou ≤ 16×e de um focinho, depois de ≥ 1 s de Atenção (ou de imediato se já estiver na zona crítica, ≤ 20) | Líder vai a um posto **entre o intruso e a toca** (entrada, ou abrigo se o intruso está dentro), parado de frente, com o focinho a ≥ 11×e da superfície do intruso; Membro no flanco (7×e ao lado, 2×e atrás); Guardião a 4 do ovo; clipe `Ameaca` se existir; `IA_Vocal = rosnado` no Líder (gancho de som) | recuo para além de 34+6 e 4 s → Atenção |
| Defesa | depois de **≥ 2 s de aviso**: avançou ≥ 5 para a toca a partir do ponto mais distante (dentro de 34); ou ficou 3 s na zona crítica; ou encostou (≤ 2,5×e do focinho). **Imediata:** coleta do ovo (oficial) ou dano com autoria validada | contato da r2 (focinho, cone 30°, histerese) + parada pelo volume do alvo e pela frenagem; o Guardião só sai do ovo para alvo a < 26 do abrigo; Uivo Boreal (poder) só aqui e só de longe | alvo morto ou desconectado; 3 s além da coleira + 8; memória de 20 s sem ser visto → Atenção → Calmo |
| Desengajar | volta de qualquer nível a Calmo | a rotina recomeça por **Guardar** (volta ao posto andando) | — |

- **Coordenador.** Um coordenador por alcateia decide o nível e é o **único** que limpa o alvo; a ordem é Líder, depois Membro, depois Guardião vivo.
  - Isso corrige o achado 4. Na r2j qualquer lobo apagava `AlvoJogador` ao sair da coleira, e a defesa alternava com a rotina.
  - Qualquer lobo, o spawner (coleta) ou o evento de dano pode **definir** o alvo.
- **Alvo por UserId.** O alvo é revalidado a cada tick: vivo, conectado e dentro do prazo.
- **Percepção.**
  - Raycast dos olhos à cabeça, com cone de ±125° (atrás não vê).
  - Memória de 8 s da última posição; morto ou desconectado sai da memória.
  - Na Defesa, alvo fora de vista por mais de 2 s → o lobo vai aonde o viu.
  - A coleta é sempre percebida (oficial), então o coletor é seguido por 20 s sem precisar de visão.
- **Dano e autoria.**
  - A autoria só vem do evento `IA_DanoRecebido` do **Kit r15**.
  - `ReceberDano(valor, elemento, origem?)` valida a origem: jogador conectado e vivo a ≤ 120 studs, ou criatura com `DonoUserId`.
  - Dano sem autoria vira **Atenção** na direção da origem (investigar). O jogador mais próximo não é mais punido (achado 2).
  - O lobo selvagem **só morde o alvo travado pela IA**, então o inocente ao lado não é mordido.
  - Alcance, cone, dano e recarga do Kit **não mudaram**.
- **Escala.** As distâncias até o lobo multiplicam por `Escala` (porte da idade). Os raios do território (48/34/20/75) são medidos do abrigo e não escalam.

Todos os números são **[PROPOSTA][A TESTAR]**, em `CFG.ameaca` da IA r3.

### 9.3 Simulação local (`studio/selvagem/simular_ameaca_r3.py`; prancha `review/rpg_ia_r3/prancha_simulacao_r3.png`)

Modelo 2D, **não é o Roblox**. Usa a cinemática da r2 (Virar 90° em 3,1 s) e 3 lobos: Líder e Membro Adultos, Guardião 0,85.

**Simplificações:**
- a toca é aberta (abrigo como âncora);
- a visão é uma chave liga/desliga;
- não há `separar()` na Defesa;
- a coleta e o dano são injetados.

**A simulação achou 3 defeitos na 1ª versão da r3, já corrigidos:**
- a insistência contava os passos dados antes do fim do aviso: quem parava logo depois do aviso era atacado;
- o alvo morto continuava na memória e reabria a defesa em ciclo;
- o desconectado reaparecia (erro do roteiro da simulação).

| Cenário | Níveis | Aviso antes da defesa | Menor focinho→jogador antes da defesa | Dentro do corpo | Resultado |
|---|---|---|---|---|---|
| 1 aproximação lenta até 30 e para | Calmo→Atenção (7,5 s)→Ameaça (12,0 s) | sem defesa | 15,3 | 0 | fica em aviso enquanto ele fica |
| 2 para na zona de aviso (25) por 30 s | →Atenção→Ameaça | sem defesa | 11,1 | 0 | segura o aviso; não ataca |
| 3 recua antes do ataque | Atenção→Ameaça→Atenção→Calmo | sem defesa | 10,1 | 0 | encerra sozinho |
| 4 insiste depois do aviso | Atenção→Ameaça→**Defesa (insistiu)** | **3,6 s** | 8,3 | 1,5 s (ele atravessa o bando andando) | ataque só após aviso |
| 5 dano validado a 40 | Atenção→Defesa (dano) | imediato | 29,8 | 0 | defesa imediata |
| 6 coleta (jogador corre a 10/s até o ovo) | Ameaça→Defesa (encostou) | 2,1 s | −0,4 | **5,1 s** | ver limitações |
| 7 dois jogadores, só B agride | Ameaça→Defesa (dano de B) | 3,0 | 15,2 | 0 | só B é mordido (no Kit, só o alvo travado) |
| 8 parede: intruso a 22 sem visão | fica Calmo | — | — | 0 | não dispara através de parede |
| 9 alvo morre | Defesa→Atenção (8,1 s)→Calmo (12,3 s) | — | — | 0 | sem ciclo |
| 10 alvo desconecta | Defesa→Atenção→Calmo | — | — | 0 | idem |
| 11 sai do território | Defesa→Atenção (14,1 s)→Ameaça→Atenção→Calmo (25,5 s) | — | — | 0 | volta sem limpeza manual; os lobos na borda ainda o encaram |
| 12 alvo circulando (r 10, 6/s) depois de dano | Defesa | — | — | 0 | 85 acertos (modelo); ver §8: giro real lento |
| 13 aparece a 3 do focinho | Ameaça→Defesa (encostou) em 2,1 s | 2,1 | 1,8 | 0 | aviso curto mesmo de perto |

**Aceite (modelo):**
- **Cumprido:**
  - aviso de ≥ 2 s antes de qualquer agressão por aproximação;
  - recuar encerra o confronto sem ataque;
  - nenhum dano fora do alcance (o Kit continua decidindo);
  - sem ciclo nas saídas;
  - postos separados na Ameaça: aglomeração 0 s, salvo 6 s na volta do cenário 11.
- **Não cumprido no modelo:**
  - jogador que corre para dentro do bando (cenários 4 e 6) fica dentro do corpo; o lobo não recua (clipe `Recuar` ausente) e o Controle não colide;
  - sinal de ameaça **visível**: os clipes ainda não existem.

### 9.4 Contrato dos clipes que faltam (precisa de aprovação antes de animar ou ampliar o Controle)

Ossos existentes, rig v11 + pálpebras:
- Raiz, Quadril, Coluna1–3, Pescoco1–2, Cabeca, Mandibula;
- Orelha_E/D, Palpebra_Sup/Inf_E/D, Cauda1–4;
- membros dianteiros: Escapula, Umero, Antebraco, Metacarpo, Dedos (_E/_D);
- membros traseiros: Coxa, Tibia, Metatarso, DedosPe (_E/_D).

**Não existem** ossos de lábio nem de pelo do dorso.

| Clipe | Tipo | Ossos | Como deve parecer (referência real) | Controle |
|---|---|---|---|---|
| `Alerta` | pose em laço, 0,3 s de entrada | Pescoco1–2, Cabeca, Orelha_E/D (Ears Pricked), Cauda1–4 (T2), Palpebra (olho aberto), Coluna (corpo parado e tenso) | congela, cabeça alta e orelhas para a frente; olhar fixo (*Stare*) | não precisa: a IA toca em Action, parado |
| `Ameaca` (rosnar) | entrada 0,5 s + laço + saída | os de `Alerta` + Mandibula (entreaberta) + Coluna1–3/Quadril (*Stand Tall*, peso à frente, pernas rígidas) + Cauda T1–T2 rígida; **lábio arregaçado e pelo eriçado precisam de ossos novos**: `Labio_Sup_E/D` (sobe acima do canino) e `Pelo_Nuca`/`Pelo_Dorso` (escala Y) | *Snarl/Lip Curl* + *Hackles* + *Stand Tall*; sem exagero teatral | não precisa (parado) |
| `GiroConfronto_E/D` | clipe com deslocamento, 90° em ~0,7 s | Raiz (giro), patas (passos curtos), Coluna, Cabeca (lidera o giro) | *Whirl*: rápido e firme | **sim**: curva no `Mov.Curvas` como o Virar, mais o pedido da IA no confronto |
| `Recuar` | laço de ré, 2–3 passos | patas, Quadril, Coluna; cabeça baixa encarando | recuo sem virar as costas | **sim**: marcha nova de ré e a IA usa quando o alvo está colado |
| `AvancoMordida` (opcional) | curto, 0,6–0,9×e para a frente e volta | Raiz, patas dianteiras, Pescoco/Cabeca/Mandibula | *Lunge/Snap* | **sim**: deslocamento curto e limitado, nunca permanente |
| `Latido` (som + clipe curto) | 0,4 s | Mandibula, Cabeca, Pescoco | aviso vocal; sem efeito de poder | som: não há asset aprovado |

**Precedente no projeto:** o Urso tem `AmeacaReal` e `InvestidaFalsa` oficiais desde 12/11. Use o mesmo padrão de entrada, laço e saída, e o perfil v(t) da investida.

### 9.5 Pendências e limitações (não resolvidas nesta rodada)

- **Integração e Play:** a r3, o Kit r15 e o spawner r3 **não foram instalados nem testados no Studio**.
  - Não houve vídeo novo, nem limpo nem de diagnóstico, e nem antes/depois em perfil e três-quartos.
  - Também não houve medida de desempenho com as 3 alcateias.
  - Celular não foi testado.
- **Sinal visível de ameaça:** sem os clipes da §9.4, a Ameaça aparece só como parar, encarar e se posicionar.
- **Giro lento no confronto:** o Virar aprovado leva 3,1 s por 90°.
- **Toca baixa para o Adulto:** §8.1, decisão pendente.
- **Dois jogadores:** só modelados; o Play solo não tem dois.
- **Um intruso por vez:** o nível da alcateia acompanha um intruso só (o mais próximo do abrigo). Um segundo intruso é tratado depois.
- **Outros sistemas de dano:** os que não passam pela `ReceberDano` com `origem` contam como "sem autoria" (investigar). Ligá-los é contrato com sistemas compartilhados.

### 9.6 Teste autorizado no rpg_roblox (20/11/2026, "Autorizo o teste")

**Preparação:**
- Reserva em `studio-em-uso.md`, feita depois que o chat Performance/Ferramentas liberou o place.
- M0 confirmou no place as versões IA r2j, Kit r14, Controle r7 e spawner r2.
- `instalar_r3.luau`: só instala se as fontes forem as esperadas e as novas compilarem; backup em `ServerStorage.LoboArtico_Backups.Antes_IA_r3_20_11` (3 scripts).
- Instalado: IA **r3i** e Kit **r15** só no `LoboArtico_Selvagem_Modelo`; spawner **r3** no ServerScriptService. O lobo de ensaio (`Teste_LoboArtico`) não foi tocado.
- Ensaio pelo módulo temporário `ServerStorage.R3_TesteTemporario`, **apagado no fim**.
- O place não foi salvo nem publicado por mim.

**Revisões feitas durante o Play** (cada uma com cópia `_r3x` em `studio/selvagem/`):

| Rev. | Achado em Play | Correção |
|---|---|---|
| r3b | os membros da alcateia são **Folders** (não Models): nenhum coordenador | `membros()` aceita Folder |
| r3b | toca da Floresta: **272 studs** da entrada ao ovo; raios medidos do abrigo só disparavam lá dentro | raios até a **toca inteira** (cadeia entrada→túnel→abrigo) |
| r3c | o túnel inteiro (180 studs) virava "zona crítica" | zona crítica, insistência e recuo medidos até o **núcleo** (descanso→abrigo); longe da toca o lobo **firma posição** onde está |
| r3d | o lobo escalava com o jogador a 160 studs no túnel | o relógio do aviso só começa com o intruso a ≤ 35×Escala de um focinho (aviso **visível**) |
| r3e | posto em linha reta caía **em cima do teto** de rocha do túnel | intruso no caminho da toca → posto é um ponto da cadeia, a distância de confronto; Membro logo atrás |
| r3f | quem viu o aviso a 30 e seguiu andando era atacado em 3,5 s | `avisoMin` 2→3 s; `insistencia` 5→8 studs |
| r3g | jogador parado **na entrada**: posto em cima dele, parada a 8,7 | posto da cadeia também na entrada; parada da Ameaça desconta a frenagem |
| r3h | na defesa, perto da boca da toca, o Pathfinding desviava (Membro "perseguia" até 106) e o lobo de costas perdia o alvo colado | visto há pouco e < 35×Escala → segue direto; < 8×Escala percebe em qualquer direção (sem parede) |
| r3i | todos longe (lobos dormentes): coordenador parado, alcateia presa em Atenção | ao dormir, o coordenador volta a Calmo e limpa o alvo |

**Resultados em Play** (medidor no servidor, amostra a cada 0,1 s, alcateia da Floresta, 1 jogador):

| Cenário | Versão | Sequência medida | Distância e contato | Resultado |
|---|---|---|---|---|
| chega de fora, **vê o aviso, para e recua** | r3g | Atenção (focinho a 35–98) → Ameaça (24–83) → recuo → Atenção → Calmo → Guardar | jogador parou a 23,6–32,6 do focinho; Líder no posto a 15,7–19,6; 0 s dentro do corpo | **sem ataque**; volta à rotina em 4–12 s após o recuo |
| chega e **insiste** (anda para o lobo depois do aviso) | r3h | Atenção (52) → Ameaça (28,7) → Líder no posto (16,2) → "confronto: segura a posição" (11,0) → Defesa "insistiu após o aviso" | **6,4 s de aviso** antes da defesa; contato 1,1–2,9 do focinho; **210 de dano em 12 s** (mordidas do Kit) | ataque só após aviso |
| dano **sem autoria** (`ReceberDano` sem origem) | r3h | Atenção → Ameaça (pela distância) | `InvestigarPos` gravado; **AlvoId nulo** | jogador a 12 do focinho **não** foi atacado |
| dano **com autoria** (origem = jogador) | r3h | Defesa "dano" na hora → saiu do território (15,9 s) → Calmo (27,9 s) | — | defesa imediata; volta sem limpeza manual |
| **coleta** (mesmos atributos que o spawner r3 grava) | r3i | Defesa "coleta do ovo" na hora → saiu → Calmo (20,2 s) | — | defesa imediata, sem aviso (oficial) |
| alvo **morre** | r3h | Defesa → Atenção "alvo morto" no mesmo tick | — | sem ciclo; ficava preso em Atenção com todos longe → r3i corrigiu ("todos longe" → Calmo, testado) |
| saída do território | r3g/r3h | Defesa → "alvo saiu do território" → Calmo | — | sem limpeza manual (no r2j foi preciso limpar à mão) |
| desempenho (3 alcateias; 1 tensa, 2 dormentes) | r3i | quadro médio do servidor 17,9 ms dormente × 17,2 ms em Ameaça (≈58 Hz) | — | sem custo visível no Studio; **celular não testado** |

**Evidências** (`BLENDER/Criaturas/Lobo_Artico_Ref/review/rpg_ia_r3/`):
- `video_r3_limpo.mp4`: aproxima → aviso → para → recua → retorno, normal + lento 0,5×, sem diagnóstico.
- `video_r3_diagnostico.mp4`: insiste → ataque, normal + lento.
  - A legenda vem do **registro do servidor** (nível, motivo, estado de cada lobo e distância do focinho), com deslocamento de ±0,5 s.
  - O gravador do Studio não captura a interface (BillboardGui), por isso a legenda.
  - O registro termina em 17,65 s; o resto do vídeo segue em Defesa.
- Brutos: `bruto_recua_limpo.mp4`, `bruto_insiste_diag.mp4`.
- Folhas de quadros: `folha_*.jpg`.
- Montagem: `studio/selvagem/montar_videos_r3.py`.

**Aceite em Play:**
- **Cumprido:**
  - aviso visível antes de qualquer agressão por aproximação (6,4 s no teste de insistência);
  - recuar encerra o confronto sem ataque;
  - mordida só no alcance do Kit (contato 1,1–2,9; alcance 5,0);
  - coleta e dano validado com defesa imediata;
  - dano sem autoria não pune o jogador próximo;
  - morte, saída do território e jogadores longe voltam a Calmo sem limpeza manual;
  - sem alternância Defesa/rotina (achado 4).
- **Não cumprido / limitações:**
  - **A Ameaça ainda é só postura parada e encarando:** faltam os clipes `Alerta`/`Ameaca` (§9.4). No vídeo o lobo parece "parado olhando", não rosnando.
  - **Depois da mordida o lobo ainda sai para reposicionar** (r2 B) e às vezes encosta no jogador (Membro a 0,6 por instantes). Falta o clipe `Recuar`.
  - **Adultos não entram no túnel** (teto, §8.1): ficam na boca da toca ou a ~76 dela; o Guardião fica "guarda o ovo" longe do ovo.
  - **Jogador parado na boca da toca** é avisado sem fim (a zona crítica é o núcleo, a ~200 studs). **Decisão sua:** contar a própria toca como zona crítica?
- **Não testado:**
  - dois jogadores (Play solo);
  - desconexão real;
  - parede entre o lobo e o jogador (só a visão foi verificada; o cenário com parede ficou na simulação);
  - alvo circulando;
  - celular;
  - Pré-adulto e Filhote como intrusos ou com outro porte (só o Pré-adulto Guardião estava presente);
  - comparação antes/depois em perfil (só três-quartos gravado).

## 10. Lobo solitário e viradas naturais: rodada local (20/11/2026)

Pedido de 20/11: o lobo fica **sozinho** (decisão do usuário) e, parado, deve virar com passos, não com o corpo girando sobre as patas. **Rodada só local:** nada foi instalado, nenhum NPC foi migrado no place, sem commit.

**Interpretação da quantidade (para o usuário conferir):** um lobo por território/toca existente.
- As 3 regiões continuam: Floresta, Maciço e Campos. Ficam 3 lobos no total, contra 9 antes.
- Quantos ninhos têm ovo continua sujeito às regras próprias (RPG_01 §8). O spawner ainda põe 1 ovo por toca, como antes [PROPOSTA].

### 10.1 Lobo solitário (IA r4 + spawner r4; cópias `_r3i` e `_Servidor_r3`)

**IA r4:**
- Papel novo **`Solitario`**: é o coordenador de si mesmo e adverte (gancho `IA_Vocal`). Pode usar o Uivo Boreal só já em defesa e de longe, como o Líder.
- Não tem as restrições de Guardião (ficar no ovo) nem o flanco do Membro: o mesmo lobo percebe, ameaça, protege, persegue e volta.
- Os papéis antigos continuam lidos, então um spawner r3 com 3 membros ainda funciona.

**Spawner r4:**
- `CFG.membros = {{"Solitario","Adulto"}}` [PROPOSTA: idade Adulto].
- **Idempotente:** reusa a pasta da alcateia e só mexe em lobos marcados com `SistemaIA = "LoboArtico_Selvagem"` ou com `AlcateiaPasta` igual ao da pasta.
- Se já houver lobos (reinício do script ou grupo da r3), mantém **um** (prefere Solitário, depois Líder) e move os **excedentes** para `ServerStorage.LoboArtico_Backups.Excedentes_Solitario`, com os scripts desligados, sem destruir.
- O mantido recebe o papel Solitário e só a IA dele reinicia.
- O ovo é refeito; se ainda estava coletado, continua oculto até `ReapareceEm`.
- Outras criaturas, o lobo de ensaio e os habitats não são tocados.
- Pastas e atributos usados pelas integrações ficam como estavam: `Criaturas_IA.Lobos_Articos.<Alcateia>`, `Papel`, `Alcateia`, `AlcateiaPasta`, `Tensao`, `AlvoId` e `IA_LoboArtico_Eventos`.

**Testes desta rodada:** selene sem erro novo e blocos balanceados. **Spawn, migração e defesa sozinho NÃO foram testados em Play:** precisam de aprovação da etapa.

### 10.2 Giro natural

**Diagnóstico (Controle r7):**
- Parado, com desvio entre 4° e 60°, o ramo `IA_Olhar` girava o **pivô** a 60°/s por `PivotTo` com o Repouso tocando. As patas plantadas giravam junto com o corpo (o "shift lock").
- Acima de 60° já usava o Virar de 90° com a curva do próprio clipe, sincronizada pelo `TimePosition`, sem reiniciar no meio.

**Fontes** (pesquisa de 20/11; não há estudo medindo lobo ou cão girando parado):
- Molkov et al. 2026, bioRxiv, [PMC12871115](https://pmc.ncbi.nlm.nih.gov/articles/PMC12871115/), modelo computacional:
  - em baixa velocidade o tronco curva entre a frente e a traseira;
  - os membros anteriores conduzem;
  - a pata apoiada fica fixa no mundo até levantar (premissa do modelo).
- Moreno & Biewener, resumos da SICB, cabras ([1](https://sicb.org/?p=29313), [2](https://sicb.org/?p=28264)): a cintura escapular gira antes da pélvica, e os membros de fora empurram mais.
- Muybridge 1887, Prancha 713, "Dog; turning around" ([NGA](https://www.nga.gov/artworks/220468-plate-number-713-dog-turning-around-etc-setter-kate)): referência real de cão girando. A página bloqueou o acesso e os quadros não foram vistos.
- **Filmagens com minutagem verificada: nenhuma.**
- O gerador das viradas (v27) já segue essas regras: cabeça e pescoço antecipam, coluna curva, pata plantada fixa no mundo, passos em ordem.

**Clipe novo em CÓPIA** (`anim_v44b/`; biblioteca e `anim_v43r5` intactas): `VirarCurtoEsquerda` e `VirarCurtoDireita`.
- 45° em 1,53 s (46 quadros), 2 ciclos de passo, gerado pelo mesmo gerador aprovado (`viradas_curtas_v44.py`).
- Depois recebe a mesma correção das pernas retas da v31, só nesses clipes (`pernas_retas_curtas_v44.py`).
- **Medido (Blender, LOW e LOD1, sequência ida e volta):**
  - deslize máximo por apoio **0,017 stud** (critério ≤ 0,03);
  - afundamento ≤ 0,0002;
  - emenda com o Repouso **0,000001** (antes da correção v31: 0,066);
  - erro de IK 0.
- Curvas de rumo para o jogo em `studio/Movimento_LoboArtico_v44.lua`, gerado por `gerar_movimento_v44.py`; o `Movimento_LoboArtico.lua` original ficou igual ao commit.

**Controle r8** (cópia `_r7`):
- **Zona morta:** parado, desvio até **35°** não gira o corpo (40° no 1 s depois de um giro). A cabeça cobriria esse desvio pelo atributo `OlharAlvo`, mas a cabeça no cliente **ainda não foi feita**.
- **Giro preciso:** com a IA pedindo precisão (`IA_Olhar(dir, true)`, contato de mordida, cone 30°) a zona é 20°/30°.
- **Anti-tremor:** a direção do alvo é suavizada (0,4 s) e o desvio precisa persistir 0,3 s.
- **Faixas de giro:**
  - 35–60°: `VirarCurto` (45° com passos);
  - acima de 60°: `Virar` (90°);
  - os dois seguem a curva do clipe e não reiniciam no meio.
- **Sem o clipe curto instalado:** cai no giro antigo (r7), marcado em `CtrlGiroLegado`.

**Simulação local** (`studio/simular_giro_r8.py`, modelo 1D do rumo, não é o Roblox):

| Cenário | r7: graus sem passos / inversões | r8c (zonas finais): graus sem passos / giros com passos / inversões / erro máx. (últimos 5 s) |
|---|---|---|
| alvo à frente (5°) | 1 / 0 | 0 / 0 / 0 / 5° |
| ao lado (90°) | 0 / 0 | 0 / 1 / 0 / 0° |
| atrás (180°) | 0 / 0 | 0 / 2 / 0 / 1° |
| alvo a 35° | 31 / 0 | 0 / 0 / 0 / 35° (cabeça) |
| oscilação ±12° em torno de 0 | **316 / 20** | 0 / 0 / 0 / 12° |
| oscilação ±12° em torno de 30 | **346 / 20** | 0 / 1 / 0 / 27° |
| alvo circulando a 34°/s | **683** / 0 | 0 / 6 / 0 / **180°** (fica para trás) |
| alvo circulando a 11°/s | 225 / 0 | 0 / 5 / 0 / 44° |

- Antes da r8c, a r8 com zona de 20° tremia: alvo oscilando em torno de 30° gerava 10 giros e 9 inversões. Daí a zona larga, com a cabeça cobrindo, e a persistência.

**Evidência visual** (`review/v44_viradas_curtas/`):
- `video_virada_curta_4vistas.mp4`: topo com grade de 0,5 stud e rastro colorido dos apoios, perfil, frente e três-quartos; normal + lento 0,5×.
- `video_virada_antes_depois.mp4`: ANTES r7, o pivô gira sobre o Repouso e os apoios deixam arcos no chão; DEPOIS v44, passos; normal + lento.
- `prancha_referencia_virada.jpg`: referência ao lado da virada e do repouso de perfil.
- `aud_viradas_curtas_v44b.json`: medida por apoio.

**Pendências e limitações:**
- **Alvo circulando rápido:** os clipes giram a ~29°/s (45° em 1,53 s; 90° em 3,1 s), então um alvo a 34°/s deixa o lobo para trás. Opções:
  - clipe de giro de confronto mais rápido (contrato §9.4);
  - o lobo reposicionar andando em arco.
  - Fica para decisão.
- **Cabeça acompanhando (`OlharAlvo` no cliente):** não feita. Sem ela, um desvio de até 35° fica sem nenhuma reação visível.
- **Não testado:**
  - no Studio, nem em Play;
  - com idades (a curva escala com `Escala`; visual por idade não conferido);
  - custo em PC e celular;
  - alvo sob o tronco, recuo e volta ao posto com o Controle r8.
- **A virada curta não passou pelas correções v33/v34** (patas no balanço, convergência). A v34 tem peso 0 nas viradas; a v33 trata as viradas no balanço, o que pode deixar a pata girar no ar mais que nos clipes aprovados: conferir no vídeo.
- **Instalação** dos clipes (KFS) e do `Movimento_LoboArtico_v44` no place: precisa de aprovação.

### 10.3 Montagem e teste no rpg_roblox (20/11/2026, "Pode montar e testar")

**Preparação:**
- Reserva em `studio-em-uso.md`.
- M0 confirmou no place: IA r3i, Kit r15, Controle r7 (modelo selvagem), spawner r3, `Movimento_LoboArtico` v41 (15.463 bytes, igual ao local) e 45 clipes.
- `selvagem/instalar_r4.luau` (tudo-ou-nada; backup `ServerStorage.LoboArtico_Backups.Antes_r4_20_11`, 4 itens) instalou:
  - **IA r4 e Controle r8** só no modelo selvagem; o lobo de ensaio continua com o r7;
  - spawner r4;
  - `Movimento_LoboArtico` v44, que só acrescenta as curvas VirarCurto;
  - KeyframeSequences `VirarCurtoEsquerda`/`Direita` (`montar_kfs_lobo_v44.luau` + `json_v44`; 47 quadros, prioridade Movement).
- **Correção feita durante o Play: Controle r8b.** No modo preciso, um alvo a 25° fazia o lobo ir e voltar; agora só gira se o erro depois do giro ficar ≥ 5° menor. Cópia `_r8`.
- O módulo temporário de ensaio foi apagado. O place não foi salvo nem publicado por mim.

**Resultados em Play:**

| Teste | Resultado |
|---|---|
| Spawn | **1 lobo `Solitario` por território** (Floresta, Maciço, Campos), cada um com seu ovo |
| Reinício do spawner | continua 1 por território, sem duplicar |
| Migração: grupo legado de 3 injetado na Floresta (Líder + Guardião + Solitário) | volta a 1; os 2 excedentes vão para `ServerStorage.LoboArtico_Backups.Excedentes_Solitario` (só durante o Play) |
| Outras instâncias | o lobo de ensaio `Teste_LoboArtico` ficou intacto |
| Defesa sozinho no túnel | Atenção → Ameaça; o jogador parou a 25,2; lobo a 18,8; recuo → Atenção |
| Encontro longe da toca (lobo caçando) | Atenção a 27,5 → Ameaça a 13,7 → **2 viradas de 90° com passos** → recuo → Calmo → volta ao posto; sem ataque |
| Insistência | "encostou no lobo após o aviso" depois de **9,1 s** de aviso; **80 de dano em 10 s**; focinho a 3,1, fora do corpo |
| Giro (IA desligada, direções mandadas ao Controle) | **0,0° girados sem clipe em todos os casos** |
| — alvo ao lado (90°) | 1 Virar ou 2 VirarCurto; erro final 0° |
| — alvo atrás (180°) | 2 Virar; o segundo ainda girando ao fim da janela de 9,5 s |
| — oscilação ±12° em torno de 30° | 1 VirarCurto; erro final 13,5°, sem ir e voltar |
| — modo preciso 25°/35°/40°/−40° | 1 VirarCurto, sem voltar; erro 20°/10°/5°/5° (cone de mordida 30°) |
| — alvo circulando a 11°/s | acompanha; erro 28,8° |
| — alvo circulando a 34°/s | **fica para trás**: erro 179° (limite dos clipes, ~29°/s) |
| Desempenho, 3 lobos | quadro médio do servidor 17,2 ms (máx. 49) com o lobo em defesa; 17,4 ms com todos dormentes |

**Evidências** (`review/rpg_r4/`):
- `video_r4_viradas_play.mp4`: três-quartos, topo e perfil, com trecho lento 0,5×.
- `video_r4_solitario_play.mp4`: percebe, ameaça, recua e volta; depois insiste e defesa; com trecho lento.
- Brutos `bruto_*.mp4` e `folha_viradas.jpg`.
- **Limitações dos vídeos:**
  - no Play, o lobo branco na neve fica pequeno na vista de topo;
  - o deslize das patas foi medido **no Blender**, não no Play (o gravador do Studio só dá imagem).
- **Lição:** o Studio apaga as gravações da pasta temporária quando o Play para. As primeiras tomadas se perderam e foram refeitas; agora cada arquivo é copiado na hora.

**Aceite:**
- **Cumprido:**
  - um lobo por território, idempotente, com migração e backup;
  - defesa independente preservada (aviso, recuo, insistência, mordida);
  - viradas sempre com passos (0° sem clipe), sem tremor nem ir e voltar;
  - dano, alcance e recarga do Kit inalterados.
- **Não cumprido:**
  - alvo circulando rápido;
  - cabeça acompanhando (cliente).
- **Não testado:**
  - idades diferentes do Adulto;
  - celular;
  - dois jogadores;
  - clipe curto com as correções v33/v34.

## 11. Ameaça visível e sonora: decisões do usuário (20/11/2026)

**Pedido do usuário:** "ele não faz nada para ameaçar, deve rosnar ou rugir, e o jogador chega perto dele e ele não faz nada".

**Respostas (questionar-antes, 20/11):**

| Tema | Decisão |
|---|---|
| Postura | animação nova de **rosnar com os ossos atuais**: cabeça baixa à frente, boca entreaberta tremendo, orelhas em pé, corpo rígido e alto, cauda erguida; sem ossos de lábio por enquanto |
| Som | **rosnado grave em laço** durante a ameaça + **latido curto** quando o jogador avança; sons da biblioteca licenciada do Roblox (como a fauna da Floresta); rugido descartado (pouco natural para lobo) |
| Jogador muito perto (~10 studs) depois do aviso | **investida de aviso** (bote curto sem morder, como a InvestidaFalsa do Urso); se ele continuar perto por ~2 s, ataca de verdade |
| Teste | primeiro no **Blender**, com vídeo para aprovação; depois instalar e testar em Play no rpg_roblox |

Números (distâncias e tempos) = [PROPOSTA][A TESTAR].

### 11.1 Primeira entrega: clipes no Blender, em cópia (20/11/2026, "Pode seguir")

**Poses** (`pose_ameaca_v45.py`; `review/v45_ameaca/pose/`):
- **rosnar:** alto e rígido, peso à frente, cabeça baixa à frente (focinho 14° abaixo do horizonte), boca entreaberta, orelhas para a frente, cauda na linha do dorso (+30°).
- **investida:** peito avança 0,5 e baixa sobre as patas plantadas, boca aberta.
- O sinal de "erguer a cauda" é positivo: com −35° ela chegava ao chão (0,01). Corrigido.

**Clipes** (`gen_ameaca_v45.py` sobre a `anim_v44b`, saída `anim_v45/`; ações anteriores intactas):

| Clipe | Duração | O que faz |
|---|---|---|
| `AmeacaEntrar` | 0,5 s | do repouso para a postura de rosnar |
| `Ameaca` | 3 s, em laço | mandíbula tremendo ~6 Hz (rosnado), respiração e micro movimento da cabeça |
| `AmeacaSair` | 0,6 s | volta ao repouso |
| `InvestidaAviso` | 1,0 s | repouso → bote → mordida no ar no pico (marcador `Pico` a 0,3 s) → repouso |

As patas ficam plantadas em todos os clipes.

**Medido** (`auditar_ameaca_v45.py`, LOW e LOD1):
- deslize máximo **0,020 stud** (critério ≤ 0,03);
- emendas 1e-6 (repouso, laço, entrar/sair, investida);
- chão: patas comprimem até 0,04 na investida.

**Vídeo:** `review/v45_ameaca/video_ameaca_v45_4vistas.mp4` (perfil, frente, três-quartos e topo com grade; normal + lento). Prancha com a referência em `prancha_ameaca_referencia.jpg`.

**Sons candidatos** (Pro Sound Effects, licença da biblioteca do Roblox; ainda não ouvidos):

| Uso | Candidato |
|---|---|
| Rosnado em laço | `Wolf Growls 3 (SFX)` 9120788992 (3,0 s) |
| Rosnado em laço | `Wolf Growl 7 (SFX)` 9120788662 (4,2 s) |
| Rosnado em laço | `Wolf Growls 1 (SFX)` 9120789017 (5,2 s) |
| Explosão na investida | `Wolf Snarl 1 (SFX)` 9120790555 (2,0 s) |
| Explosão na investida | `Wolf Snarl 2 (SFX)` 9120790847 (2,0 s) |
| Latido curto | `Coyotes Gruff Barking 8 (SFX)` 9113955372 (0,8 s): não há latido de lobo na biblioteca; é o canídeo mais próximo |
| Latido curto | `Coyotes Gruff Barking 13 (SFX)` 9113956187 (0,9 s) |

**Ainda não feito:** instalação, IA (investida a ~10 studs; ataque depois de ~2 s perto) e Play. Aguarda aprovação.

**r2 (20/11, pedido do usuário: "não quero sua boca tremendo tanto"):**
- O laço `Ameaca` ficou **sem tremor rápido**: a boca só acompanha a respiração do rosnado (±0,8°, 2 vezes em 3 s).
- A r1 tinha 2,5° a 6 Hz; a cópia está em `gen_ameaca_v45_r1.py`.
- Medidas iguais: deslize 0,020, emendas 4e-6.
- Vídeo: `review/v45_ameaca/video_ameaca_v45_r2_4vistas.mp4`.

### 11.2 Montagem e teste no rpg_roblox (20/11/2026, "Aprovar e montar")

**Instalado** (`selvagem/instalar_r5.luau`; backup `ServerStorage.LoboArtico_Backups.Antes_r5_20_11`; lobo de ensaio não tocado):
- **IA r5** no modelo selvagem (cópia `_r4`).
- **KeyframeSequences** `AmeacaEntrar`, `Ameaca` (laço), `AmeacaSair` e `InvestidaAviso`, todas com prioridade Action (`montar_kfs_lobo_v45.luau` + `json_v45`).

**Comportamento da IA r5** (números [PROPOSTA][A TESTAR]):
- **Na Ameaça:** toca `AmeacaEntrar` → `Ameaca` em laço, com o **rosnado** em laço (Wolf Growls 3, 9120788992) no RootPart do lobo. O som é 3D (some a ~90 studs) e fica mais agudo nos filhotes.
- **Intruso avançando** (focinho → intruso cai mais de 1 stud entre ticks): **latido** curto (Coyotes Gruff Barking 8, 9113955372), no máximo 1 a cada 3 s.
- **Intruso a ≤ 10 × Escala do focinho:** **InvestidaAviso** com **snarl** no pico (Wolf Snarl 1, 9120790555), sem dano; recarga de 4 s.
- **Intruso continua a ≤ 10 por 1 s (investida) + 2 s:** **Defesa**, com o motivo "ficou perto após a investida". O rosnado continua na defesa.
- **Saída:** recuar ou ficar calmo encerra a ameaça (`AmeacaSair`) e o rosnado.

**Play (lobo da Floresta):**

| Teste | Resultado |
|---|---|
| Parado a ~24 | rosnado tocando, postura de ameaça |
| Avançou | latido em 3,7–4,6 s; investida a 9,1–9,2 do focinho, com o snarl 0,3 s depois |
| Recuou depois da investida | sem ataque; o lobo segue ameaçando enquanto o jogador está na área da toca |
| Ficou perto | Defesa **3,2 s depois da investida**; 60 de dano em 10 s (mordidas do Kit) |

- O lobo perde tempo virando: 12 de 40 amostras estavam no clipe `VirarDireita` (90° em 3,1 s). É a pendência do giro rápido.

**Evidências:**
- `review/rpg_r5/video_r5_ameaca_play.mp4`, com trecho lento.
- Brutos `bruto_investida_*.mp4` e `folha_r5.jpg`.
- **O vídeo não tem som:** o gravador do Studio não capta áudio. O som só foi confirmado pelo registro (`IsPlaying`) e precisa ser ouvido em Play.

**Limitações:**
- No vídeo o lobo aparece pequeno; a postura se vê melhor no vídeo do Blender.
- Os sons foram escolhidos por padrão (não foram ouvidos por mim).
- Não testados: idades e celular.

### 11.3 "Quero algo mais agressivo": decisões do usuário (20/11/2026)

**Marcado pelo usuário: as 4 opções.**
- **Postura mais feroz:** cabeça mais baixa e esticada, boca bem aberta, corpo agachado de quem vai saltar, orelhas para trás.
- **Investida mais forte:** bote mais longo e rápido, avançando alguns passos antes de voltar, com mordida no ar visível.
- **Ataca mais cedo:** investida a ~15 studs; ataque se o jogador ficar ~1 s.
- **Som mais feroz:** rosnado mais alto e raivoso (snarls), latido mais frequente.

**Ataque depois do aviso:** "como hoje". Dano, alcance e recarga do Kit continuam os aprovados, e a perseguição continua igual.

**Feito, local (r3 dos clipes + IA r6; nada instalado ainda):**
- **Poses r3** (`review/v45_ameaca/pose_r3/`):
  - rosnar: agachado 0,38, peito à frente 0,28, pescoço +28°, focinho 24° abaixo do horizonte, boca 26°, orelhas para trás (−16°), cauda +24°;
  - investida: avanço de 0,60, boca 34°.
  - Com avanço de 0,75 o deslize passava do limite (0,0316); por isso 0,60.
- **Clipes** em `anim_v45r3/` (`gen_ameaca_v45r3.py`; a r2 está em `anim_v45_r2/`):
  - bote mais rápido (pico a 0,23 s) e mordida no ar de 32°;
  - deslize 0,025 (≤ 0,03), emendas 5e-6, patas comprimem até 0,056.
- **IA r6** (cópia `_r5`):
  - a ~15 × Escala do focinho o lobo faz uma **carga real**: trota com passos (clipes de locomoção) até ~5 × Escala ou 1,6 s, para e dá o bote (`InvestidaAviso`) sem morder;
  - se o jogador continua perto 1 s depois do bote, Defesa;
  - rosnado trocado por Wolf Growl 8 (9120788636, "angry snarl"), volume 1,0;
  - Wolf Snarl 2 (9120790847) no início da carga e Snarl 1 no bote;
  - latido a cada 1,5 s.
  - Depois da carga o lobo **fica de frente**, rosnando: não volta de ré (falta o clipe de recuo).
- **Vídeo:** `review/v45_ameaca/video_ameaca_r3_4vistas.mp4`. Antes/depois: `prancha_r2_r3.jpg`.

### 11.4 Montagem e teste da versão mais agressiva (20/11/2026, "Aprovar e montar")

**Instalado:**
- **IA r6d** e **clipes r3** (`json_v45r3`, `montar_kfs_lobo_v45r3.luau`), via `instalar_r6.luau`.
- Backup em `ServerStorage.LoboArtico_Backups.Antes_r6_20_11`.
- O place não foi salvo.

**Correções feitas durante o Play** (cópias `_r6`, `_r6b`, `_r6c` em `studio/selvagem/`):

| Revisão | Achado | Correção |
|---|---|---|
| r6b | em trote a carga andava ~3 studs em 1,6 s | **corre** (Arrancada → Corrida) e para descontando a frenagem, até 5 × Escala do focinho; máximo 2 s |
| r6c | com o posto inalcançável (limite do túnel) o lobo ficava "indo ao posto" **sem ameaçar** | se em 2 s não chega 1 stud mais perto, firma onde está e ameaça dali |
| r6d | a própria carga levava o focinho ao jogador e disparou "encostou no lobo" 0,4 s depois do bote | durante a carga e até 1 s depois do bote (`CargaAte`) "encostou" não conta; só "ficou perto após a investida" escala |

**Play:**

| Cenário | Resultado |
|---|---|
| Rosnado | tocando no posto |
| Jogador avança | latido; **carga correndo** a partir de 14,4–14,9 do focinho: o lobo avança 6,5–11,9 studs e dá o bote a 4,3–8,3; snarl na carga e no bote |
| Recua logo após o bote (r6d) | **sem ataque** (dano 0); o lobo deu outra carga enquanto o jogador se afastava (expulsando) e voltou ao posto |
| Fica perto (r6, 1ª tomada) | Defesa ~2,4 s depois do bote (regra de 1 s após o clipe de 1 s) |

**Evidências:** `review/rpg_r6/video_r6_agressivo_play.mp4`. O gravador do Studio **não capta som**.

**Limites:**
- A segunda carga contra quem já está recuando pode parecer insistente demais. Para ajustar, dá para aumentar a recarga de 4 s ou não dar carga em quem se afasta.
- A virada lenta ainda atrasa a defesa.
- Não testados: idades e celular.

## 12. Giro sem shift lock, pernas que não congelam e patas no chão (20/11/2026)

**Pedido do usuário:** "arrume todas as partes onde o lobo ainda aparece virando sem física, como se estivesse no shift lock, e uma parte que ele aparece andando com as pernas paradas; quero que todas as criaturas, jogadores e criaturas selvagens pisem no chão".

**Escolhas do usuário:**
- o Lobo Ártico é corrigido aqui;
- o sistema geral de pé no chão (jogadores e todas as criaturas) fica numa sessão separada (`pes-no-chao`);
- teste direto no rpg_roblox.

**Causas encontradas:**
1. As poses da IA (ameaça, investida, vida) têm prioridade Action e pegam o corpo inteiro. Tocando enquanto o Controle andava ou virava, **congelavam as pernas**: o corpo girava ou deslizava pela curva do clipe com as pernas paradas. É o "shift lock" e o "andar com as pernas paradas".
2. Sem chão à frente (toca estreita), o Controle ainda **girava o pivô no lugar** (resto da r6b).
3. O Controle só colava o pivô no chão: o corpo não inclinava com o terreno e as patas flutuavam ou afundavam.

**Correções** (cópias `Controle_Servidor_r8b`, `IA_LoboArtico_r6d`):

| Revisão | O que muda |
|---|---|
| IA r7 | a pose não começa com o Controle em Laco/Clipe; se ele começar a andar ou virar, a pose para em 0,15 s e a IA retoma quando ele para; o bote da carga espera a frenagem terminar; o atributo `IA_Pose` informa a pose ao Controle |
| Controle r9 | sem chão à frente, vira pelos clipes de passos (`giroPara`); **inclinação** frente/trás e lado/lado pelas amostras de chão sob as patas (suave 0,15 s, máximo 25°), aplicada em torno do meio das patas, sobre o pivô só com rumo; **patas no chão:** parado e em pose de pé, um `IKControl` por pata (Umero/Coxa → Dedos/DedosPe) com alvo no chão sob a posição de repouso da ponta, avaliado no cliente |

**Instalado no rpg_roblox** (backup `ServerStorage.LoboArtico_Backups.Antes_r7_20_11`):
- IA r7 e Controle r9 no modelo selvagem;
- Controle r9 também no lobo de ensaio `Teste_LoboArtico` (backup `Controle_Servidor_ensaio_r7`).

**Play:**
- Jogador andando em volta do lobo por 24 s (raio 20), com ameaça, carga e bote: **0 de 1.156 quadros** com pose da IA tocando enquanto o Controle andava ou virava. As viradas foram só por clipe (VirarEsquerda/Direita), e as cargas por Arrancada/Frenagem.
- Inclinação medida de −25° a +5° na saída da toca e em encostas.
- Os 4 IKControl ficam ativos com o lobo parado; o cliente os recebe.
- O lobo de ensaio carrega o r9: 4 IK, sem erro.

**Evidências:** `review/rpg_r9/video_r9_play.mp4` (perfil no terreno e três-quartos com a ameaça girando); brutos e folhas na mesma pasta.

**Limites:**
- O IK das patas só foi checado como ligado/desligado. **A qualidade visual da pata no degrau não foi medida** (a câmera de Play não mostra de perto); falta conferir a dobra do joelho.
- Andando, só a inclinação atua (o IK fica desligado para não brigar com o passo).
- A curva de giro andando (60°/s) segue o Controle de antes.
- Não testados: idades e celular.

## 13. Árvores sólidas na Tundra e lobo contornando troncos (20/11/2026)

**Pedido do usuário:** "como ele entrou dentro da árvore, consegue arrumar as árvores". Escolha: **troncos sólidos só na Tundra**.

**Causa** (M0 no rpg_roblox): todas as malhas das 2.572 árvores de `Workspace.Tundra_Congelada.Vegetacao_Arvores` têm `CanCollide = false` e `CanQuery = false`. Jogador e lobo atravessavam, e o lobo (movido por `PivotTo`) nem as enxergava.

**Correção no mapa** (`studio/selvagem/colisores_arvores_tundra.luau`):
- Em cada árvore, um cilindro **invisível** `Colisor_Tronco` (`CanCollide`/`CanQuery`, sem toque nem sombra, altura 10), dentro do modelo da árvore (o `LOD_Distancia` do cliente o leva junto).
- A copa continua atravessável.
- As malhas não foram alteradas.
- O eixo e o raio vêm de raios horizontais contra a malha:
  - centro refinado em 3 passadas, mediana das distâncias, a 1,2 stud do chão;
  - nas bétulas de vários troncos, varredura em grade a 1,5 do chão real, um colisor por tronco.
- **2.572 colisores:**
  - 2.412 pela medida do tronco;
  - 7 por peça;
  - 153 por varredura;
  - raio mediano 1,8 (de 0,35 a 3,0).
- Reversível: `M.desfazer()` apaga tudo que tem o atributo `CriadoPor`.
- Conferido em captura: os colisores envolvem o tronco (pinheiro, abeto, bétula).

**Correção no lobo** (Controle r10 → r10e; cópia `Controle_Servidor_r9`; backup `ServerStorage.LoboArtico_Backups.Antes_r10_20_11`):
- Um Spherecast do tamanho do corpo (quadril → focinho, raio 0,85 × Escala) enxerga peças sólidas, excluindo terreno, criaturas e jogadores.
- O desvio olha 2 studs à frente, na frente **e na direção desejada**, e escolhe um **ponto de passagem ao lado do tronco**, pelo lado livre (até 2,5 s).
- O avanço só é barrado em contato real.
- De frente para o tronco, o lobo para e vira com o clipe de passos.

**Revisões feitas no Play:**

| Revisão | Achado | Correção |
|---|---|---|
| r10 | o lobo travou encostado e alternou parar/andar 190 vezes | desvio com memória |
| r10b | idem: o bloqueio e o desvio liam distâncias diferentes | desvio olha 2 studs à frente; avanço barrado só em contato |
| r10c → r10d | alvo atrás do tronco: virava para ele, encostava e parava | o desvio também checa a direção desejada |
| r10d → r10e | seguir a tangente fazia **circular** o tronco | ponto de passagem ao lado |

**Play** (lobo de ensaio guiado a atravessar um bosque com 9 troncos, 26 s):

| Versão | Encosto máximo no tronco | Trocas parar/andar | Distância percorrida |
|---|---|---|---|
| r10 | 0,15 | 1.092 | 21 studs |
| **r10e** | **0** | **2** | **78 studs** (velocidade cheia; atravessou o bosque) |

- Jogador andando contra um tronco: parou e contornou (o centro do jogador nunca chegou a menos de 2,09 do eixo; raio do tronco 1,54).
- **Instalado:** Controle r10e no modelo selvagem e no `Teste_LoboArtico`.
- **Vídeo:** `review/rpg_r10/video_r10_bosque.mp4`.

**Limites:**
- **Desempenho** dos 2.572 colisores (peças ancoradas simples) não medido.
- **Celular** não testado.
- **Árvores fora da Tundra** continuam sem colisão (escolha do usuário).
- **Poderes:** Cometa e Avalanche agora encontram troncos nos raycasts deles; o comportamento não foi testado.

## 14. Mudar de direção caminhando em curva (20/11/2026, entrega local em cópia)

**Pedido:** o usuário ainda via a virada como um jogador girando no eixo. O lobo deve **andar enquanto vira**, com o corpo percorrendo uma curva, passos e transferência de peso. A revisão abrange o clipe e a execução pelo controlador.

**Escopo:** só local. Nada foi instalado no rpg_roblox, nada commitado, nenhum serviço pago usado. A pedido do usuário, tudo rodou no modo mais leve: Blender com prioridade Idle, 1 núcleo e 1 thread (`blender_levissimo.ps1`), um processo pesado por vez, montagem de vídeo também em Idle.

### 14.1 Diagnóstico (`diag_virada_v46.py`, anim_v45r3, medido nos ossos)

**Andar aprovado:** ciclo de 1,2 s, apoio de 62%, ordem TE→DE→TD→DD, 3,0 studs/s.

**Controle r10e andando (modo Laco):** o clipe Andar **reto** toca enquanto o pivô gira até 60°/s em volta de si mesmo. Deslize mundial das patas apoiadas, por fase:

| Giro do pivô | DE | DD | TE | TD |
|---|---|---|---|---|
| 60°/s | 2,05 | 1,24 | 1,34 | 1,24 |
| 30°/s | 1,04 | 0,62 | 0,68 | 0,62 |
| 15°/s | 0,52 | 0,31 | 0,34 | 0,31 |
| 0 | 0,00 | 0,005 | 0,006 | 0,006 |

Esse é o "giro de roda": a orientação muda sobre patas que só marcham.

**Viradas parado:**
- VirarCurto gira 45° com o pivô se deslocando só 0,54 stud;
- Virar gira 90° com o pivô se deslocando 1,0 stud.

Ou seja, a orientação gira com a posição praticamente fixa (giro no lugar com passos).

**Outros pontos:**
- O ramo **LEGADO** gira o pivô sem clipe.
- As poses de ameaça ocupam os membros: AmeacaEntrar/InvestidaAviso movem o úmero até 43–51°. Elas já param com o lobo se movendo (IA r7), e o Ameaca em laço quase não mexe as pernas (≤1,9°).

### 14.2 Tentativa 1, descartada: mistura por peso (v46, `gerar_curvas_v46.py`)

Laços AndarCurva (30°/s) e AndarCurvaFechada (50°/s), misturados com o Andar por peso.

| Situação | Deslize |
|---|---|
| Curva constante | 0,007–0,064 |
| Peso fixo em 50% (DD) | 0,07 |
| Rampas | 0,13–0,41 |
| Rampas com o pivô derivado das patas | 0,05–0,26 |

Causa: misturar poses de osso não produz um caminho de pata coerente, e com a taxa de giro mudando no meio do apoio as patas dianteiras e traseiras pedem movimentos de corpo diferentes. Auditorias em `review/v46_curvas/aud_LOW_teste*.json`.

### 14.3 Método adotado: v46b/v46c (`gerar_curvas_v46b.py`)

**Ideia:** "dobrar" o Andar aprovado quadro a quadro.
- Os ossos do corpo são os do Andar mais a curvatura. As correções v31/v33/v34 já estão no Andar e são preservadas.
- Cada pata é a mesma pata do Andar, levada por uma transformação rígida no plano do chão.

**Trajetória genérica:** o pivô segue qualquer perfil de giro ω(t).
- Cada pata apoiada fica **fixa no mundo** no ponto do meio do seu apoio naquela trajetória. A pata de dentro percorre arco menor e a de fora, maior, pela própria geometria do giro.
- No balanço, a pata vai em min-jerk da saída ao próximo toque e já pousa virada para dentro da curva.
- Perna: IK de 2 ossos com o plano de dobra e a torção do quadro do Andar.

**Ajustes medidos, todos [A TESTAR]:**
- **Centro do giro** no meio do corpo (y = −0,95, entre as patas dianteiras e traseiras), não no pivô do rig. Com o giro no pivô, as dianteiras varriam demais e cruzavam (folga −0,13).
- **Corpo abaixa** 0,12·(ω/30)² stud: 0,12 a 30°/s, 0,27 a 45°/s. Sem isso, as dianteiras ficavam sem alcance.
- **Curva fechada a 45°/s**, não 50. A 50 sobrava erro de alcance.
- **IK suave** acima de 97% de extensão ou da extensão do próprio Andar no quadro. A perna de fora chegava ao limite e "desesticava" de uma vez, gerando um pico de aceleração de 0,66 na coxa.

**Corpo na curva** ([PROPOSTA]):
- cabeça e pescoço antecipam 0,15 s (5 / 2,5 / 3,5° a 30°/s);
- coluna em arco (1,5 / 2,5 / 2°);
- cauda compensa para fora (−1,5 a −4°);
- inclina 1,5° para dentro.

**Clipes (16, todos na fase do Andar, em `anim_v46c`):**

| Tipo | Clipes | Giro |
|---|---|---|
| Laço (1 ciclo) | AndarCurvaEsquerda/Direita | 30°/s, 36° por ciclo, raio 5,7 |
| Laço (1 ciclo) | AndarCurvaFechadaEsquerda/Direita | 45°/s, 54° por ciclo, raio 3,8 |
| Transição (2 ciclos; rampa no 1º, o 2º já é o laço) | AndarParaCurva | 54° |
| Transição | CurvaParaAndar | 18° |
| Transição | CurvaParaFechada | 99° |
| Transição | FechadaParaCurva | 81° |
| Correção curta (começa e termina reta, ω = 30·sen²) | CurvaBreve (1 ciclo) | 18° |
| Correção curta | CurvaCurta (2 ciclos) | 36° |

As poses das emendas entre transição e laço são idênticas (0,0°). A troca de clipe acontece no fim do ciclo, sem fade.

**Curva externa por quadro** (avanço, deslocamento lateral e giro) em `curvas_v46b.json` e em `studio/Movimento_LoboArtico_v46b.lua`. O módulo mantém todas as curvas anteriores iguais e acrescenta as 16 novas.

### 14.4 Auditoria mundial (`auditar_curvas_v46.py --seq`, translação + rotação aplicadas à malha, três LODs)

Sequências de clipes:
- aberta E/D;
- fechada E/D (entrada 30→45→saída);
- curva em S (E→D);
- destino atrás (180° em curvas concatenadas);
- correções breve e curta;
- zigue-zague;
- partida parada.

| Medida | LOW | LOD1 | LOD2 |
|---|---|---|---|
| Deslize por apoio nas curvas | 0,007–0,049 | 0,022–0,045 | 0,007–0,043 |
| Mesmo trecho no Andar reto aprovado (referência) | 0,006–0,030 | — | 0,006–0,020 |
| Afundamento máx. | 0,0002 | 0,005 | 0,029 |
| Flutuação máx. | 0,0033 | 0,0001 | 0 |
| Aceleração máx. (quadro²) | 0,406 | 0,313–0,319 | 0,256–0,289 |
| A mesma, no Andar reto | 0,406 | 0,313 | 0,256 |

- **Folga lateral mínima** entre as patas de um par (sem cruzamento): curva aberta 0,91/1,14; fechada 0,51/0,63; correções ≥1,09.
- **Antes, mesmo perfil** (Andar reto + pivô girando): deslize de 0,47–0,91 na curva aberta e de 0,79–1,52 na fechada.
- **Reimportação** pela rota do Studio (JSON da ponte → ações; `reimportar_json_v46b.py`): diferença ≤0,0003 stud na ponta dos dedos. A auditoria sobre o reimportado dá os mesmos números nos três LODs.

**Defeitos residuais:**
- **Acima de 0,03:** nas curvas, DD/TE/TD ficam entre 0,031 e 0,049, principalmente na fechada. O próprio Andar reto já tem DD em 0,030 e o residual do Andar é preservado. Entre 1 e 7 fases por cenário ficam acima de 0,03.
- **Entrada Andar→AndarParaCurva:** perna até 1,8° diferente no primeiro quadro, porque a pata plantada antes da troca já "vê" a rampa. Na malha a aceleração não sobe acima da do Andar.
- **Partida parada:** o fade Repouso→Andar do controlador (já existente; não há clipe RepousoParaAndar) escorrega até 0,79 nas patas que estão no ar no Andar.
- **Não medidos por número:** garganta, cauda/coxa e flanco. Só foram vistos nos vídeos.

### 14.5 Controlador: proposta r11 em cópia (`studio/Controle_Servidor_r11_proposta.server.luau`, NÃO instalada)

**Andar:** o pivô deixa de girar sobre o clipe reto e segue a trajetória do próprio clipe (`Movimento` v46b), como já acontece nas trocas de marcha.

**Decisão a cada fim de clipe**, pelo rumo que falta (a fase do passo continua, nada reinicia a cada tick):

| Nível atual | Condição | Próximo clipe |
|---|---|---|
| reto | <9° | Andar |
| reto | <27° | CurvaBreve |
| reto | <54° | CurvaCurta |
| reto | ≥54° | AndarParaCurva |
| curva | lado trocou ou ≤27° | CurvaParaAndar |
| curva | >140° | CurvaParaFechada |
| curva | caso contrário | AndarCurva |
| fechada | lado trocou ou ≤108° | FechadaParaCurva |
| fechada | caso contrário | AndarCurvaFechada |

**Outras regras:**
- Pedido de Trote/Corrida no meio da curva: termina a curva e só então sobe de marcha.
- Obstáculo: o desvio por ponto de passagem (r10e) vira o rumo desejado. Se não houver chão, ou houver contato, o lobo para e o Parado vira com o clipe de passos.
- Ramo LEGADO: não gira mais o pivô; espera e marca `CtrlGiroSemClipe`.
- Sem os clipes de curva instalados, volta ao comportamento da r10e.
- Selene: igual à r10e (só o aviso antigo de `Instance.new` com pai).

**Simulação da regra** (`sim_controle_r11.py`, curvas exatas):
- Alvo a 40 studs: alinha em 3,6–25 studs andados, passando do rumo no máximo 24°.
- Alvo perto (15 studs a 45–90°): pode orbitar, porque o raio de curva não fecha a tempo. Para alvo perto vale a regra do pedido: reposicionamento curto com passos (VirarCurto/Virar, parado). A IA sabe a distância; o controlador hoje só recebe a direção.

**Não alterados:**
- IA_Olhar (orientação de ameaça e contato com VirarCurto/Virar, parado);
- Trote e Corrida (ainda com o giro antigo);
- a partida parada (fade).

### 14.6 Referência real

**Literatura consultada** (não é filmagem de lobo):
- quadrúpedes em curva lenta controlam a curvatura principalmente dobrando o corpo ([Frontiers in Neurorobotics 2025](https://www.frontiersin.org/articles/10.3389/fnbot.2025.1628368/full));
- os membros de fora produzem mais impulso que os de dentro ([resumo Moreno & Biewener, SICB](https://sicb.org/?p=28264));
- em galgos e guepardos correndo em curva, o membro de dentro fica mais tempo no chão (citado em [PMC11561069](https://pmc.ncbi.nlm.nih.gov/articles/PMC11561069)).

A v46 usa a curvatura do corpo, mas mantém o mesmo tempo de apoio dentro e fora: refinamento possível.

**Filmagem verificável de lobo andando em curva, com minutagem: NÃO obtida.** Não consigo assistir vídeos de sites, e baixar um arquivo exige autorização. Proposta: o usuário indica, ou autoriza baixar, um vídeo (por exemplo, do Wikimedia Commons) para a comparação quadro a quadro.

### 14.7 Evidências (`BLENDER/Criaturas/Lobo_Artico_Ref/review/v46_curvas/`)

**Vídeos** (Workbench, 15 q/s, chão em grade de 1 stud, seta de rumo, trajetória do pivô em laranja, rastros das patas DE azul / DD vermelho / TE verde / TD amarelo):
- `video_v46_antes_depois_aberta_E.mp4`: antes × depois lado a lado em vista superior (câmera fixa), três-quartos (câmera fixa), perfil esquerdo e direito, frente e traseira, mais trechos lentos 0,5×.
- `video_v46_antes_depois_fechada_D.mp4`: lado direito, curva fechada.
- `video_v46_cenarios.mp4`: fechada com close das patas (normal e lento), destino atrás 180°, curva em S, partida parada.

A barra de diagnóstico mostra clipe, quadro, ω e rumo.

**Dados** (`aud_*.json`, `diag_v46.json`, `sim_controle_r11.json`):
- diagnóstico;
- auditorias v46b/v46c por LOD;
- auditoria "antes";
- auditoria do reimportado;
- simulação.

**Limitação dos vídeos:** são vistas de revisão do Blender, sem textura. No topo, o "antes" mostra os riscos das patas arrastando; o "depois", pontos fixos.

### 14.8 Aceite

**Cumprido localmente:**
- o lobo avança e muda de direção em arco, com passos e peso (corpo abaixa e inclina, coluna e cabeça na curva);
- sem rotação do corpo sobre patas fixas;
- sem tranco nas emendas (aceleração igual à do Andar);
- dados e vídeos concordam;
- três LODs auditados;
- exportação/reimportação validada.

**Não cumprido ou não testado:**
- deslize ≤0,03 em todas as fases (residual até 0,049, ver 14.4);
- partida parada com passos (o fade antigo escorrega);
- transição para ameaça/mordida e aceleração/frenagem em curva (são do controlador; só no Studio);
- teste em Play;
- idades;
- celular;
- comparação com filmagem real.

**Próxima etapa, exige autorização expressa:**
- M0 do place e reserva em `studio-em-uso.md`;
- instalar os 16 KeyframeSequences (`json_v46b`), o `Movimento` v46b e o Controle r11 só no modelo selvagem e no lobo de ensaio, com backup;
- teste em Play.

Opcional: clipes de partida/parada (Repouso↔Andar e Repouso→curva) pelo mesmo gerador.

### 14.9 Montagem e teste no rpg_roblox (20–23/11/2026, "Aprovar e instalar")

**Instalação** (Edit; o rpg_roblox estava livre e reservei em `studio-em-uso.md`):
- **M0** conferiu o place igual ao local: Controle r10e nos dois lobos, `Movimento_LoboArtico` v44 (17.984 bytes) e 50 KeyframeSequences.
- **`selvagem/instalar_r11.luau`** (tudo-ou-nada):
  - Controle r11 no modelo selvagem e no `Teste_LoboArtico`;
  - `Movimento_LoboArtico` v46b;
  - backup em `ServerStorage.LoboArtico_Backups.Antes_r11_20_11` (r10e ×2 + Movimento v44).
- **`montar_kfs_lobo_v46b.luau`**: montou os 16 clipes em 4 lotes (total de 66; laços com loop; prioridade Movement).
- **Incidente:** no primeiro Play, o plugin de integração do Studio não carregou (nem no servidor nem no cliente). O usuário parou o Play e reabriu o Studio; a instalação persistiu.

**Correções feitas durante o teste** (cópias `Controle_Servidor_r11a`/`_r11b`):
- **r11b:**
  - decide a curva já no primeiro passo;
  - na decisão, olha cerca de 16 studs à frente;
  - encostado de frente num tronco, vira 45° com passos.
  - Motivo: com o tronco na linha, a r11 encostava e piscava Parado/Andar 737 vezes.
- **r11c:** curvas só com pedido de **andar**; trote e corrida sobem de marcha na hora, como na r10e. Motivo: em Defender, a curva larga afastava o lobo até 20 studs por 8 s.

**Resultados em Play** (lobo de ensaio guiado pelo `IA_Mover`; módulo temporário `R3_TesteTemporario`, apagado no fim):

| Teste | Resultado |
|---|---|
| Andando reto, alvo vira 90° à esquerda | Andar → AndarParaCurva (na virada do ciclo) → laço → CurvaParaAndar → Andar; rumo 0→108° em arco, erro final 2,3°; 0° girados com o pivô parado; 0 bloqueios |
| 180° andando | AndarParaCurva → laço → CurvaParaAndar; parou ao chegar num buraco do chão de ensaio (correto: não anda sem chão) |
| Zigue-zague ±25° | só CurvaBreve/CurvaCurta, rumo oscilando ±18°, 1 troca de modo |
| Tronco na linha (r11b) | curva breve à direita já no primeiro passo; passou o tronco com o pivô a ≥3,8 do eixo (raio 2,2); realinhou e chegou ao alvo (distância 0); 2 trocas de modo |
| Partindo parado com alvo a 90° | ainda vira no lugar com o clipe Virar (90°, passos) e depois anda (regra de partida não mudou) |
| Lobo selvagem com a IA (túnel da Floresta, r11c) | Patrulhar → Atenção → Ameaçar com curvas breves até o posto → pose de ameaça → Defender → mordidas (jogador de 100 a 0); 0° girados com o pivô parado |
| Desempenho | quadro médio do servidor 17,4–20,1 ms (o Studio do Cérbero estava em Play ao mesmo tempo) |

**Deslize no Play** (pelo osso dos dedos, no servidor):
- O método tem um piso de ruído de cerca de 0,08–0,11 stud, por causa de um quadro de defasagem entre a animação e o `PivotTo`.
- No reto, a pata apoiada tem velocidade média igual à do corpo: 2,98 contra 3,00 studs/s.
- **Deslocamento líquido por apoio:**
  - curvas: média de 0,087 (laço) a 0,102 (entrada);
  - Andar reto aprovado na mesma corrida: 0,107.
- Ou seja, no Play a curva escorrega o mesmo que o Andar aprovado.

**Limitações:**
- **Em Defender**, com o jogador ao lado ou atrás a 3–10 studs, a IA pede andar. O lobo faz curvas e duas viradas Virar de 90° (3 s cada), e a primeira mordida veio 8,6 s depois de entrar em Defender (nas rodadas anteriores, com o giro "shift lock", eram cerca de 2,4 s). Proposta: uma virada rápida de combate com passos.
- **Partindo parado** com o alvo acima de 60°, ainda há virada no lugar com passos.
- **Não testados:** idades, celular e dois jogadores.
- **O vídeo** não tem som.

**Evidência:** `review/rpg_r11/video_r11_play.mp4` (câmera seguindo só a posição; curva de 90° e zigue-zague; trecho lento 0,5×). Brutos `bruto_r11_*.mp4` e folhas `folha_*.jpg`.

Place não salvo por mim. Sem commit.

## 15. Virada de combate (24/11/2026, entrega local em cópia)

**Decisões do usuário (24/11, "Pode seguir"):**
- pivô nas patas traseiras;
- 90° em cerca de 1,0 s;
- usada só em ameaça e defesa;
- a mordida emenda no fim da virada.

**Motivo:** no teste da r11c em Defender, a primeira mordida demorou 8,6 s, porque as viradas calmas de 90° levam 3,1 s cada.

**Clipes** (`gerar_virada_combate_v47.py` + correção v31 `pernas_retas_combate_v47.py`; base anim_v46c, saída `anim_v47b`), mesmo gerador aprovado das viradas v27/v44:
- **VirarCombate90Esquerda/Direita:** 1,0 s, 4 ciclos de passo.
- **VirarCombate180Esquerda/Direita:** 1,6 s, 7 ciclos.
- **Centro do giro** 25% à frente do meio das traseiras: as traseiras dão passinhos de até 0,27 de lado e as dianteiras varrem o arco (até 1,06). Com o pivô exatamente nas traseiras, as dianteiras saíam do alcance (erro de IK de 0,65–0,92).
- **Corpo:** agacha 0,18 durante a virada; cabeça e pescoço lideram (18/8/12°, 0,08 s antes); coluna 6°; cauda 12°.
- Parâmetros = [PROPOSTA][A TESTAR].

**Auditoria mundial** (`auditar_virada_combate_v47.py`, Repouso → ida → volta → Repouso, 3 LODs):

| Medida | Resultado |
|---|---|
| Deslize por apoio | 0,0007–0,017 (critério 0,03) |
| Afundamento | ≤0,009 |
| Flutuação | ≤0,0002 |
| Emendas com o Repouso | quadros idênticos (1e-6) e aceleração na emenda 0,03–0,12, contra até 1,28 nos passos rápidos dentro do clipe |
| Erro de alcance (IK) | ≤0,031 |
| Reimportação pelo JSON (`json_v47`) | ≤0,0002 |

**Controlador:** proposta **r11d** em cópia (`Controle_Servidor_r11_proposta`; cópia da r11c em `Controle_Servidor_r11c`), NÃO instalada.
- Com `IA_Estado` em Ameacar ou Defender, um desvio acima de 45° usa VirarCombate90; a partir de 135°, VirarCombate180.
- Andando em combate com o alvo a mais de 60°, o lobo para e faz a virada de combate.
- Fora de combate nada muda.
- A mordida continua com a IA/Kit, logo que o lobo termina de frente.
- Selene igual à r10e; sem erro de sintaxe.

**Também prontos:**
- `Movimento_LoboArtico_v47.lua`: a v46b mais as 4 viradas; as linhas anteriores ficam iguais.
- `montar_kfs_lobo_v47.luau`.

**Vídeo:** `review/v47_combate/video_v47_virada_combate.mp4`.
- Antes (Virar 90, 3,1 s) × depois (combate, 1,0 s) lado a lado em 5 vistas;
- detalhe lento;
- 180° em 4 vistas, mais detalhe lento.

**Falta:**
- instalar e testar no rpg_roblox (exige autorização) e medir o tempo até a 1ª mordida;
- idades e celular.

Sem commit.

### 15.1 Montagem e teste no rpg_roblox (24/11/2026, "Aprovar e instalar")

**Instalação** (Edit; o usuário abriu o place; reserva em `studio-em-uso.md`):
- **M0** conferiu r11c nos dois lobos, `Movimento` v46b, 66 KFS e nenhuma virada de combate.
- **`selvagem/instalar_r11d.luau`** (tudo-ou-nada): backup em `ServerStorage.LoboArtico_Backups.Antes_r11d_24_11` (r11c ×2 + Movimento v46b).
- **`montar_kfs_lobo_v47.luau`**: montou as viradas.

**Teste de defesa no túnel da Floresta** (jogador a 89 → 45 → encostado, 30 s):

| Versão | 1ª mordida depois de entrar em Defender | Observação |
|---|---|---|
| r11c (antes) | 8,6 s | curvas largas e 2 viradas calmas de 90° |
| r11d | 13,2 s | virada fixa de 90° passava do ponto (vai e volta esquerda/direita, 5×) e as curvas curtas passavam ao lado do alvo |
| **r11e** | **0,2 s e 0,5 s** (duas corridas) | 11 mordidas seguidas; 0 viradas calmas; 0° girados com o pivô parado; afastamento máximo 9–11 studs |

**r11e** (correções durante o teste; cópias `Controle_Servidor_r11c`/`_r11d`):
- **Virada mais próxima do desvio:** 45, 90 ou 180°. Foi acrescentada a **VirarCombate45** (0,63 s; mesmo gerador; deslize ≤0,017 nos 3 LODs; emendas 0,30–0,37).
- **Sem vai e volta:** logo depois de uma virada de combate, só vira de novo acima de 90°, e enquanto espera não cai na virada calma.
- **Em combate, andando,** só curva breve ou reto. Acima de 45°, para e vira.

**Demonstração** (lobo de ensaio com `IA_Estado=Defender`, alvo mudando de lado a cada 3,5 s): VirarCombate45 E → 45 D → 45 D → 45 E → 90 E. A suavização da direção (0,4 s) às vezes divide um desvio de 85° em duas viradas de 45°.

**Vídeo:** `review/rpg_r11/video_r11e_combate_play.mp4` (com trecho lento) e o bruto.

**Pendências:**
- **Ainda há algum vai e volta com o jogador colado na cabeça:** a IA mede o ângulo a partir do pivô, perto das traseiras. Proposta: a IA mirar a partir do peito/cabeça (mexe na IA).
- **Suavização da direção em combate:** pode ser menor.
- **Não testados:** idades, celular e dois jogadores.

Place não salvo por mim. Sem commit.

## 16. Rodada "todas as etapas" (26/11/2026, usuário: "prossiga com todas as etapas")

As decisões que dependem do usuário ficaram **pendentes, sem mexer**; a pergunta foi interrompida e o usuário disse "Prossiga":
- ampliar o túnel da toca (mexe no mapa);
- baixar um vídeo real de lobo (download precisa de autorização);
- publicar as animações e salvar o place (conta do usuário).

O resto foi feito, local primeiro e depois no rpg_roblox, com reserva e backup.

### 16.1 Mira da IA a partir do peito + suavização em combate
- **IA r7b** (`posMira()` = pivô + frente × 3,6 × Escala): as 7 orientações para o intruso medem do peito (cópia `IA_LoboArtico_r7`).
- **Controle r11f:** a suavização da direção cai para 0,15 s em combate (antes 0,4 s).
- **Play (túnel):** 1ª mordida 1,2 s depois de entrar em Defender; 11 mordidas; só 2 viradas de combate, ainda na ameaça a 40 studs; nenhum vai e volta com o jogador colado; 0° girados com o pivô parado.

### 16.2 Partida e parada do Andar com passos (anim_v48, `gerar_partida_v48.py`)

Clipes:
- **PartidaAndar:** v 0→3 em 1,2 s, 2 ciclos.
- **PartidaCurvaEsquerda/Direita:** também ω 0→30, emendando no laço AndarCurva.
- **ParadaAndar:** segue 0,4 s na mesma velocidade, freia em 1,2 s, as patas pousam no lugar do Repouso; 3 ciclos.

Método das curvas (Andar dobrado, patas fixas no mundo), agora com velocidade variável:
- a pata que, no Andar, está no ar no instante zero dá o 1º passo saindo do Repouso com velocidade zero;
- as outras ficam plantadas até a 1ª saída do cronograma depois de 0,1 s;
- o pé troca de pose (Repouso↔Andar) em 0,2 s;
- no apoio é preservado o rolamento do pé do Andar (prender o MCP fazia os dedos escorregarem 0,15);
- no ar, a pata segue o caminho do Andar mais um desvio interpolado (o caminho reto no mundo não batia com a emenda: braço 24–32°).

**Auditoria nos 3 LODs** (sequências Repouso → Partida → Andar/curva → Parada → Repouso):

| Medida | Resultado |
|---|---|
| Deslize, retas | 0 fases acima de 0,03 (pior 0,030) |
| Deslize, com curva | só as fases da curva (≤0,040, como o laço já aprovado) |
| Afundamento | ≤0,032 |
| Aceleração máxima | igual à do Andar (0,41 / 0,31 / 0,25) |
| Emendas | idênticas com Repouso e Andar; 1,7° na saída da partida em curva |
| Erro de alcance | ≤0,03 |
| Reimportação do JSON | ≤0,0003 |

**Controlador r12:** fora de combate, pedindo andar:
- desvio menor que 25° → PartidaAndar;
- desvio maior → PartidaCurva E/D, mesmo acima de 60° (antes: virada no lugar).

Andando reto ou em curva curta sem direção, termina o ciclo e faz a ParadaAndar; dentro de uma curva larga ou em combate, para como antes.

**Play:**

| Cenário | Sequência | Observação |
|---|---|---|
| Reto | PartidaAndar → Andar → ParadaAndar (0,1 s após o pedido) → Repouso | — |
| Alvo a 90° | PartidaCurvaEsquerda → laço → CurvaParaAndar → CurvaBreve (correção) → ParadaAndar | rumo final 90° |
| Filhote (0,4) e Ancião (1,1) | o mesmo, na escala | — |

Nos três: 0° girados com o pivô parado e 0 bloqueios. Na patrulha, o lobo selvagem já usa a partida em curva.

**Vídeos:**
- `review/v48_partida/video_v48_partida_parada.mp4` (antes × depois);
- `review/rpg_r12/video_r12_play.mp4`.

### 16.3 Cabeça acompanhando o alvo (`Cabeca_Cliente` r1, Script RunContext=Client)
- Gira Pescoço1/Pescoço2/Cabeça em volta do eixo vertical na direção de `OlharAlvo`: até 45°, divididos 30/30/40%, suavizado em 0,18 s.
- Só com a câmera a menos de 80 studs; volta ao normal sem alvo. Visual apenas.
- O Controle r12 apaga `OlharAlvo` quando a IA para de pedir a orientação.
- **Play:** alvo a 30° de cada lado com o corpo parado; a cabeça acompanha (vídeo, 0–6 s).

### 16.4 Testes
- **Idades:** Filhote e Ancião, na partida, curva e parada, sem bloqueio.
- **Desempenho:** servidor 17,4–17,9 ms por quadro; cliente `RenderCPUFrameTime` médio 14,8 ms (máximo 25,6) no ensaio, com o Studio do Crocodilo em Play ao mesmo tempo.
- **Celular:** não medido em aparelho real.
- **Poderes × troncos** (leitura do `Kit_Servidor`, sem Play): o Cometa e a Avalanche usam raios que agora batem no `Colisor_Tronco`; param no tronco em vez de atravessar a árvore, e a linha de visão do alvo também é bloqueada. Não foi testado com jogador controlando.
- **Dois jogadores:** não testado.

### 16.5 Pendências
- **Decisões do usuário:** toca (ampliar ou não), vídeo real (baixar ou não) e publicação (guia em `DOCS/criaturas/lobo-artico-publicar-animacoes.md`).
- **Ainda não feitos:**
  - trote e corrida em curva com passos;
  - alvo circulando muito rápido;
  - partida e parada saindo do trote.

Sem commit.

## 17. Rodada "próximo passo" (26/11/2026)

Decisões do usuário (26/11): ampliar o túnel da toca; pode baixar um vídeo real; o usuário publica depois; trote/corrida com a mesma técnica, primeiro no Blender com vídeo para aprovação e depois no rpg_roblox.

### 17.1 Vídeo real de lobo
- "Close opnamen wolf – Stichting Natuurbeelden" (Wikimedia Commons, CC BY-SA 3.0 NL, Enting Films / Sound and Vision), 19,6 MB, guardado só em `%TEMP%` (fora do git).
- Viradas em 0:24–0:26 e 1:33–1:37: o lobo vira andando com passos, sem girar no lugar; ~90° em cerca de 1 s.
- Comparação: `review/v49_ref_real/comparacao_real_x_nosso.jpg`.

### 17.2 Curvas de trote e corrida (anim_v49, `gerar_curvas_marcha_v49.py`)
- Mesma técnica do Andar (clipe aprovado dobrado, patas fixas no mundo). Trote 45/90°/s (baixar 0,10); Corrida 60/120°/s (baixar 0,16).
- 16 clipes por marcha (`<G>Curva`, `<G>CurvaFechada`, `<G>ParaCurva`, `<G>CurvaParaReto`, `<G>CurvaParaFechada`, `<G>FechadaParaCurva`, `<G>CurvaBreve`, `<G>CurvaCurta`, E/D).
- Auditoria nos 3 LODs: 0 fases acima de 0,03 de deslize (pior 0,023). Aceleração do trote igual à do reto; corrida à direita 1,42 contra 1,09 do reto (resíduo).
- Vídeo antes × depois: `review/v49_trote_corrida/video_v49_trote_corrida.mp4` — **aguarda aprovação**.
- Vídeo **APROVADO** pelo usuário (26/11, "Aprovar e instalar").
- **Instalado no rpg_roblox (26/11):** 32 KFS (`montar_kfs_lobo_v49.luau`, prioridade Movement, laços `<G>Curva`/`<G>CurvaFechada`), Controle r13 (modelo selvagem + Teste_LoboArtico) e `Movimento_LoboArtico` v49; backup `ServerStorage.LoboArtico_Backups.Antes_r13_26_11`.
- **Play (Teste_LoboArtico, módulo temporário `selvagem/teste_r13_modulo.luau`, apagado depois):**
  - Trote reto → alvo a 90° à direita: TroteParaCurva → TroteCurva → TroteCurvaParaReto → Trote (+ CurvaBreve de correção); 0° girados com o pivô parado, 0 bloqueios.
  - Corrida reta → 90° à direita: CorridaParaCurva → CorridaCurva → CorridaCurvaParaReto; ~110° em 1,8 s correndo; 0° parado, 0 bloqueios.
  - Corrida → esquerda: CorridaParaCurvaEsquerda → CorridaCurvaEsquerda (o ensaio terminou no meio da curva pelo tempo).
  - Servidor 17,4–17,6 ms por quadro; nenhum erro do Controle no console.
  - Limites: a medição de deslize das patas no Play pegou poucas fases (a pista acaba em ~150 studs; corrida bate na borda), então vale a auditoria do Blender; Filhote/Ancião, combate em trote e celular não testados nesta rodada.

### 17.3 Túnel da toca (rpg_roblox, terreno)
- Backup antes de mexer: `ServerStorage.LoboArtico_Backups.Toca_Terreno_<Alcateia>_26_11` (original) e `..._cadeia_26_11` (cadeia inteira, após a 1ª escavação). Restaurar primeiro "cadeia", depois o original (`PasteRegion` no atributo `CantoVoxel`).
- Teto escavado em Floresta, Maciço e Campos; 7 pontos de teto fino no Maciço foram pulados para não abrir buraco.
- Verificação por caixa varrida (simulando a IA): com tolerância de degrau 1,8, Floresta 53/53 e Campos 40/40 passam (Adulto e Ancião). Com a tolerância atual (1,0) os degraus do piso ainda bloqueiam.
- Maciço para no trecho 49→50: um ressalto de rocha (Slate) de 2,4 studs no piso em (-1048, 95,8, -5118). Escavar o teto não resolve; seria preciso rebaixar o piso ali.
- Correção do diagnóstico: no Maciço o bloqueio do trecho 49 não era o piso, era a **parede lateral** do túnel (voxels a 4 studs do caminho; `FillBlock` não os alcançava). Usuário: "Prossiga" (26/11).
- **Feito (26/11):**
  - **IA r7c** (`selvagem/IA_LoboArtico.server.luau`, cópia `_r7b`, instalador `selvagem/instalar_r7c.luau`): a conferência do túnel tolera degrau de `degrauToca` 1,8 × Escala (mínimo 1,0). Instalada no modelo `ServerStorage.LoboArtico_Selvagem_Modelo`; backup `Antes_r7c_26_11`.
  - Paredes alargadas voxel a voxel (`WriteVoxels`), só quando o voxel de trás continua sólido e o teto acima tem 3 studs ou mais:
    - Maciço: 9 voxels (trechos 49–50; backup `Toca_Terreno_Alcateia_Macico_parede49_26_11`);
    - Campos: 4 voxels perto da entrada (backup `Toca_Terreno_Alcateia_Campos_caminhoPlay_26_11`).
- **Play (caminho recalculado pela IA, como ela faz):**

  | Toca | Filhote | Adulto | Ancião |
  |---|---|---|---|
  | Floresta | 32/53 (degrau do piso) | 53/53 | 53/53 |
  | Maciço | 68/169 | 75/169, cristal `Cristais_Gelo_Largo` | 29/169 |
  | Campos | 40/40 | 6/40 (caminho mudou depois de alargar) | 6/40 |

- **Problema de fundo:** o Pathfinding da IA calcula um caminho diferente a cada Play (e depois de cada mudança no terreno); alargar um ponto muda o caminho. No Maciço o caminho atravessa os cristais de gelo da gruta (`Formacoes_Gelo_Gruta.Salao_das_Colunas`, mapa da Tundra; não mexi).
- Onde não cabe, a IA já para no limite do túnel e defende dali (r2 D / r6c); nada quebra.
- **Não testado:** andar pelo túnel com o lobo de teste. Fora da arena, o `Teste_LoboArtico` vai para (0, -1000000, 0) logo depois de ser colocado na toca.
- **Proposta:** gravar uma cadeia FIXA por toca (pontos medidos e aprovados) em vez de recalcular por Pathfinding, e alargar só ao longo dela; decidir com o dono do mapa se o lobo pode passar pelos cristais do Maciço.

Sem commit.
