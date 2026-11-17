# IA piloto da fauna da Floresta Ancestral (16/11/2026)

Piloto de IA no servidor para Cervo-do-Bosque, Javali Silvestre e Coruja-da-Floresta. Roda **só na cena isolada** `Workspace.Teste_FaunaFloresta` (y=2600) do rpg_roblox, com um exemplar de cada espécie. Não está integrado ao mapa.

Status: fluxos **[PROPOSTA]** e todos os números **[A TESTAR]**. A regra oficial diz só "comportamento próprio por espécie, dentro de fuga/defesa/ataque/perseguição curta/retorno ao habitat". Não há dano, hitbox, coleta, spawn, recompensa nem persistência neste lote.

## Arquivos (fonte = esta pasta; o Studio tem cópia idêntica, conferida por hash em 16/11)

| Arquivo | Papel |
|---|---|
| `Config.luau` | Perfis por espécie: clipes por estado, velocidades dos clipes, raios de percepção, corpo, fuga, investida, voo. |
| `Controlador.luau` | Controlador **compartilhado**: um fio por animal, `mudar()` com cancelamento por token, transições com perfil de velocidade, fluxos das três espécies. |
| `Percepcao.luau` | Alvo = jogador vivo ou alvo de teste. Lê a cada 0,25 s, com linha de visão e histerese (entra no alerta em `raioAlerta`, sai acima de `raioSairAlerta`). Só troca de alvo se o novo estiver 25% mais perto. |
| `Movimento.luau` | Único lugar que move o modelo (`PivotTo`, uma vez por quadro). Chão por raycast, obstáculo por spherecast, desvio de ±30/60/90°, limites da área e Pathfinding só quando a linha direta está bloqueada (recálculo limitado a 1 por segundo). |
| `Anim.luau` | Monta os KeyframeSequence pelo `AdaptadorFauna` e registra com `AnimationClipProvider` (id temporário, só no Studio). Falha de clipe vai para `Anim.falhas` e para um `warn`. |
| `Perfis.luau` | `v_perfil` dos JSON aprovados (gerado por `gerar_perfis.py`; não editar à mão). |
| `Cena.luau` | Cena de teste: chão de 260×220, marcas a cada 20 studs, poleiros A, B e C (seguro), rotas aéreas explícitas, posições iniciais. Tem `construir`/`desfazer`/`posicionar`. |
| `Roteiro.luau` | Roteiros de teste reproduzíveis com alvos falsos (tag `AlvoFaunaTeste`, só com `DEBUG`) e amostragem a 10 Hz. |
| `IA_FaunaFloresta_Servidor.server.luau` | Liga a IA. Sai logo se o atributo `Ativo` for false. Roteiros pelo atributo `Comando`; o resultado vai em JSON para `Resultado_<nome>`. |
| `../ia_fauna.project.json` → `../IA_FaunaFloresta.rbxm` | Pacote para Insert from File: `rojo build studio/ia_fauna.project.json -o studio/IA_FaunaFloresta.rbxm`. |

## Clipes por estado (base aprovada; velocidade = manifesto × escala 3)

| Espécie | Estado | Clipe (lote/versão) | Deslocamento |
|---|---|---|---|
| Cervo | Repouso / Alerta | Repouso, Alerta (`clipes_r2`) | parado |
| Cervo | Fuga | Arrancada → Corrida (`clipes_r2`, corrida r2) | Arrancada: curva própria [A TESTAR] (10 quadros parado, depois sobe até a Corrida); Corrida 14,53 studs/s |
| Cervo | Desacelerar | CorridaParaTrote → TroteParaAndar (`clipes_r2`) | curva linear suave entre as marchas [A TESTAR] |
| Cervo | Retorno | Andar (`clipes_r2`) | 2,13 studs/s |
| Javali | Repouso / Alerta / Desiste | Repouso (`clipes_LA`), Alerta, AlertaParaRepouso (`clipes_LC`) | parado / `v_perfil` |
| Javali | Encarar | VirarE / VirarD (`clipes_LA`) | 1,33 studs/s girando |
| Javali | Ameaça | Ameaca (`clipes_LD_r2`) | `v_perfil` |
| Javali | Investida | Investida (`clipes_LD_r2`) → Corrida (`clipes_LB`) | `v_perfil` até 8,4 studs/s; direção fixa |
| Javali | Recuperação | RecuperacaoInvestida (`clipes_LD_r2`) | `v_perfil` até 0 |
| Javali | Retorno | ParadoParaAndar → Andar → AndarParaParado (`clipes_LA`) | `v_perfil` / 1,33 studs/s |
| Coruja | Pousada / Alerta | Repouso, OlharE / OlharD (`clipes_LA_r2`) | parado |
| Coruja | Decolagem | VirarNoLugarE/D (`clipes_LA_r2`, 60°/s) → FugaDecolando (`clipes_LD`) | `v_perfil` |
| Coruja | Voo | BaterAsas → BaterParaPlanar → Planar (`clipes_LB`) | 9,0 / 10,8 studs/s; subida 4,5 e descida 3,0 studs/s |
| Coruja | Pouso | Pousar (`clipes_LB`) | `v_perfil` de 3,6 até 0; começa no ponto que o perfil leva até o topo do poleiro |

Não há falha de carga: 87 clipes disponíveis, e `Anim.falhas` ficou vazio em todos os Plays. Os lotes A e B da coruja foram gerados no rig r3, sem pálpebras, então nesses clipes elas ficam abertas.

## Fluxos [PROPOSTA]

- **Cervo:** Repouso → Alerta (alvo visível a até 38 studs; mínimo 0,8 s) → Fuga (alvo a até 26).
  - A rota de fuga sai de 16 direções. Afasta-se da ameaça, exige 10 studs livres e fica dentro da área. É recalculada a cada 0,4 s, ou na hora se surgir obstáculo à frente.
  - A fuga termina a 60 studs da ameaça, aos 9 s, ou 2,5 s depois de perder o alvo. Depois: Desacelerar → Retorno andando.
  - Se o alvo voltar a até 26 studs, foge de novo.
  - Se ficar preso por mais de 0,4 s, para de correr (não corre no lugar).
- **Javali:** Repouso → Alerta (até 30 studs) → Encarar → Ameaça (até 24 studs, **uma vez** por aproximação) → Vigiar.
  - Investe só se o alvo continuar a até 18 studs, sem recarga pendente (6 s) e com a linha livre.
  - Na investida a direção é fixada no início. Termina por distância (alvo + 5, até 22 studs), por tempo (2,6 s), por obstáculo ou pela borda da área. Depois: Recuperação → Retorno.
  - Linha bloqueada: Desiste e rechecha a cada 1 s, sem repetir a ameaça.
  - Alvo fora por 2 s: AlertaParaRepouso.
  - É só visual: sem dano nem hitbox.
- **Coruja:** Pousada → Alerta (até 30 studs, em 3D) → com o alvo a até 18: escolhe o poleiro alternativo. A ordem é A↔B; o seguro C fica por último.
  - Antes de decolar confere a rota explícita: segmentos livres (spherecast de raio 1,4), folga de 4 studs sobre o chão, poleiro sem alvo a menos de 5 studs e sem nada sobre o topo.
  - Sem rota: reavalia a cada 1,5 s; após 3 tentativas fica em `AlertaPousada`.
  - Voo: gira no lugar → FugaDecolando → BaterAsas → Planar pelos pontos da rota → chega exata (0,15 stud) ao ponto de início do pouso → Pousar → Repouso.
  - Nunca usa navegação terrestre.

## Testes (rpg_roblox, Play, 16/11; servidor a 29–41 fps com outros 3 Studios abertos)

| Roteiro | Resultado |
|---|---|
| `cervo_aprox` | Repouso → Alerta (35) → Fuga → Desacelerar (fugiu 38 studs em 1,8 s) → Retorno → Repouso. Velocidade medida no Retorno: 2,13 studs/s, igual à do clipe Andar. |
| `cervo_recua` | Alerta → "alvo recuou" → Repouso, sem fuga. |
| `cervo_perda` | Alvo some 1 s depois de a fuga começar → desacelera → retorna → Repouso. |
| `cervo_obstaculo` | **1ª rodada: atravessou o muro** (o passo não checava colisão) e travou na quina, andando no lugar. Corrigido. Na 2ª rodada fugiu contornando o muro, retornou por Pathfinding (caminho de 11 pontos) e chegou ao Repouso. |
| `cervo_dois` | Alerta no Jogador2 → troca para o Jogador1, mais perto → foge → retorna → Repouso. |
| `javali_aprox` | **1ª rodada: repetia a Ameaça sem fim** (distância 3D de 18,03 contra limite de 18, e sem estado de vigília). Corrigido. Na 2ª rodada: Alerta (29) → Encarar → Ameaça (17,4) → Vigiar → Investida (16) → Recuperação (encerrada por tempo, após 18,2 studs) → Retorno → Repouso. |
| `javali_recua` | Ameaça (20,1) → Vigiar → "alvo recuou" → Repouso. |
| `javali_obstaculo` | Tronco baixo na linha → "rota bloqueada a 5,6" → não investe → o alvo sai → Repouso. |
| `javali_dois` | Escolhe o Jogador1, mais perto → ciclo completo. |
| `coruja_aprox` | Pousada A → Alerta → Decolagem → Voo → Pouso em B, alinhada a 0,2°. Erro de contato antes do encaixe final: **1ª rodada 1,20 stud**; corrigido (chegada exata ao ponto de pouso) para **0,34 stud**. |
| `coruja_recua` | Alerta → "alvo recuou" → Pousada, sem decolar. |
| `coruja_bloqueio` | Galho sobre B → escolhe o seguro C → pousa (erro de 0,42 stud). |
| `todos` | Os três juntos com dois jogadores: coruja A→B (erro de 0,44), cervo foge do Jogador2 e retorna, javali ameaça e desiste. Percepção de ~4 leituras/s por animal; 0 cálculos de caminho (linha livre). |

Evidências em `review/` (fora do git):
- `review/v1/IA_FaunaFloresta_piloto_v1.mp4`: 7 tomadas em câmera fixa, com o título e o estado sobre cada animal.
- `review/v1/prancha_1..7.jpg`: 6 quadros por tomada.
- `review/v1/ficha_vs_studio.jpg`: os modelos em ação ao lado das fichas de `REFERENCIAS/floresta-ancestral/`.
- Captura bruta em `review/cap1/` (PrintWindow, 20 qps).

**Comparação com as fichas:**
- Identidade e postura conferem nos três: silhueta, pelagem, galhada, presas e tufos.
- Coruja: no Repouso as primárias aparecem abertas em leque nas laterais, enquanto a ficha mostra a asa justa ao corpo. É o clipe Repouso aprovado; fica para revisão.

**Não testado:**
- celular;
- jogadores reais;
- respawn de jogador real;
- remoção do NPC durante o Play: o código trata, `vivo()` encerra o fio, mas não houve teste dedicado.

## 17/11: curvas andando e Chifrada (pedido do usuário)

O usuário viu no vídeo v1 o javali dando "um 180 sem se mexer" e pediu realidade nos três animais e uma chifrada no acerto da investida.

**Causa:** `Movimento.passo` girava até 110 graus/s mesmo com velocidade zero. O javali girava parado no começo do ParadoParaAndar (a velocidade do perfil começa em 0) e no Encarar. O cervo girava parado nos 10 quadros de susto da Arrancada.

**Correções:**
- **Giro ligado à passada:** o raio mínimo de curva vem do clipe VirarE aprovado (velocidade ÷ giro): cervo 4,9 studs, javali 3,05 studs. Acima disso o raio cresce com a velocidade (`tauGiro`). Sem velocidade não há giro.
- **Retorno:** usa VirarE/VirarD (curva andando, 25 graus/s) quando a curva pedida passa de 12 graus, e Andar abaixo de 5 graus.
- **Javali:**
  - Encarar vira andando em arco (VirarE/D × 1,6) e acompanha o alvo durante o Vigiar.
  - Só investe alinhado (até 15 graus). A investida segue a própria frente e não gira.
  - Depois da recuperação sai andando reto e volta em arco.
- **Coruja:**
  - Sem velocidade não gira no ar.
  - Planando, curva acima de 15 graus usa PlanarCurvaE/D (asas inclinadas).
  - No galho continua girando com o clipe VirarNoLugar, que dá os passos a 60 graus/s, como no manifesto.
- **Personagens contam como obstáculo** para o corpo (`passo`/`passoDesvio`), então o animal desvia e não atravessa ninguém. Os alvos de teste ficaram sólidos.
- **Manobra quando travado:** numa quina onde o raio de curva não cabe, o animal vira dando passos com VirarE/D até a frente livrar, por no máximo 4 s. O caminho por Pathfinding ficou mais largo (raio do agente = 0,7 × raioGiro).
- **Chifrada:**
  - Clipe novo do lote E (`Javali_Silvestre_Ref/rig/clipes_javali_le.py`), parcial: só pescoço, cabeça e orelhas, prioridade Action2.
  - Toca por cima da RecuperacaoInvestida (`Anim:sobre`).
  - Dispara por contato quando faltam 1,5 stud entre a ponta do focinho (cantos das malhas visíveis) e a superfície do alvo.
  - O raio fixo falhou nos dois testes: com 5,5 o focinho entrava ~1 stud no alvo, e com 6,5 o javali parava longe.
  - Atributo `UltimaChifrada` no modelo. Só visual: sem dano.

**Testes (Play no rpg_roblox, 17/11):**

| Roteiro | Resultado |
|---|---|
| `javali_aprox` | Encarar → Ameaça → Vigiar → Investida → **acerto** → Recuperação → Retorno → Repouso. 0 giros sem deslocamento (antes: 180 graus). Curva mais fechada: raio 2,8 studs. A Chifrada toca (Action2, peso 1) com o pescoço subindo ~16 graus. Folga focinho→alvo no pico do golpe: **0,00 stud**; a freada termina 0,5 stud dentro. |
| `javali_lado` (novo) | O alvo chega pelo lado: Encarar andando em arco por 2,5 s → Ameaça → Investida → acerto → Retorno. 0 giros sem deslocamento. |
| `cervo_aprox` | Fuga em arco (raio mínimo 4,6) → Desacelerar → Retorno com curvas → Repouso. 0 giros sem deslocamento. |
| `cervo_obstaculo` | 1ª rodada: **travou na quina** (o raio de curva não cabia no caminho rente ao muro). Corrigido com caminho largo + manobra. 2ª rodada: contornou com manobras curtas (~10 s na quina) e chegou ao Repouso, mas depois do limite de 45 s do roteiro. |
| `coruja_aprox` | A → B, pouso com erro de 0,35 stud. Único giro sem deslocamento: ~30 graus no galho, com o clipe de passos. |
| `todos` | Os três juntos com dois jogadores: tudo volta a estado seguro. Giro sem deslocamento só da coruja no galho (33 graus). Servidor a 26 fps com outros Studios abertos. |

**Evidências:**
- `review/v3/IA_FaunaFloresta_curvas_chifrada_v3.mp4`: 4 tomadas. As do javali foram gravadas depois da última correção; as do cervo e da coruja vêm de antes das mudanças de obstáculo/manobra, que não afetam esses roteiros.
- `review/v3/chifrada_no_contato.jpg`.
- Capturas brutas em `review/cap2`, `review/cap4`.

**Limitações:**
- Falta um clipe de giro no lugar (pivô nas patas traseiras) para cervo e javali. A manobra usa o clipe de curva andando sem deslocar, e as patas podem escorregar um pouco.
- A freada empurra 0,5 stud para dentro do alvo (não há empurrão no jogador; é só visual).
- Celular e jogadores reais não testados.

## Rollback e instalação

- **Desligar sem apagar:** atributo `Ativo = false` na pasta `IA_FaunaFloresta`. É o estado atual, deixado assim depois dos testes.
- **Religar:** `Ativo = true`; a IA liga no próximo Play.
- **Remover tudo:** apagar `Workspace.Teste_FaunaFloresta.IA_FaunaFloresta` e `Workspace.Teste_FaunaFloresta.Cena_IA`. Depois, rodar `Cena.desfazer` ou devolver o `Chao` para 80×60 (o tamanho original fica no atributo `TamanhoOriginal`).
- **Instalar de novo:** Insert from File de `studio/IA_FaunaFloresta.rbxm` dentro de `Workspace.Teste_FaunaFloresta`. Depende de `ReplicatedStorage.FaunaFloresta`, que vem de `../FaunaFloresta.rbxm`.
- **Rodar um roteiro em Play (servidor):** `workspace.Teste_FaunaFloresta.IA_FaunaFloresta:SetAttribute("Comando", "cervo_aprox")`. O resultado sai em `Resultado_cervo_aprox`, em JSON.
- **Disparo de roteiros:** o MCP roda numa VM separada e não vê o `_G` do jogo. Por isso os roteiros são disparados pelo atributo `Comando`.

## 17/11: sons licenciados (módulo `Sons`)

- **O que toca:** o servidor cria um Sound posicional na cabeça do animal (RollOff InverseTapered 10 a 140 studs). Cada Sound é destruído ao terminar. Os áudios são todos licenciados (Pro Sound Effects, Creator Store), e a lista de ids fica em `Sons.luau`.
  - Cervo: bufo de alerta, bufo de fuga e resfôlego em repouso.
  - Javali: grunhido em repouso, alerta, ameaça, guincho grave na investida, baque + grunhido no acerto da chifrada, grunhido curto no retorno.
  - Coruja: piado em repouso, asas baixas na decolagem e no pouso. Fica quieta no alerta.
- **Ganchos no Controlador:**
  - `Sons.estado` é chamado em `mudar`.
  - `Sons.evento("chifrada")` é chamado no acerto.
  - `Sons.iniciarVida` é chamado em `iniciar`.
  - Todos rodam em `pcall`: se o módulo faltar, a IA continua.
- **Hashes no Studio:** Controlador 1092796326, Sons 1589142976. Backup do Controlador anterior: `Backup_IA_antes_1711.Controlador_antes_sons`.
- **Teste em Play (rpg_roblox, 17/11):** com os roteiros `todos` e `javali_aprox`, 24 sons tocaram, todos com `IsLoaded = true` e `IsPlaying = true`.
  - A ordem do javali foi alerta → ameaça → investida → chifrada + voz no acerto → retorno.
  - Depois do teste ficaram 0 Sounds na cena e não houve erro da fauna no console.
- **Limitações:**
  - Ninguém ouviu ainda: volumes, tons e trechos estão [A TESTAR], de ouvido, pelo usuário.
  - Sem som de cascos/passos: não há take licenciado adequado.

### 17/11: Sons r2 — javali mais natural e contínuo

Pedido do usuário: o javali deve soar "mais natural e contínuo, que acabe devagar".

- **Fades:** todo som entra com fade-in e sai com fade-out longo (até 1,4 s no javali). Cada animal tem um canal de voz: uma voz nova esmaece a anterior em vez de cortá-la.
- **Takes longos e graves:** são todos "Pitched Down Growls". Não existe take de javali selvagem licenciado.
  - Repouso: sorteio entre Pig Grunts 13, 14 e 15.
  - Alerta: Pig Grunts 12.
  - Ameaça e investida: Pig Grunts 8, "Deep Menacing".
  - O guincho de porco doméstico da r1 saiu.
- **Camada contínua:** rosnado grave em laço, com volume 0,32, durante Alerta, Encarar, Ameaça e Vigiar. Entra em 1 s e some em 1,6 s.
- **Teste em Play:** no roteiro `javali_aprox`, todos os Sounds saíram com volume 0,000 (esmaecidos) e todos carregaram.
- **Estado:** hash do Sons 1815937609. A r1 ficou em `Backup_IA_antes_1711.Sons_r1` e em `scratchpad/Sons_r1.luau`. Falta o usuário ouvir.
- **APROVADO pelo usuário em 17/11** depois de ver e ouvir o javali em Play: Sons r2 é a base atual. O `IA_FaunaFloresta.rbxm` foi recompilado.

### 17/11: Sons r3 — cervo e coruja

- **Cervo:** os bufos continuam curtos (cerca de 0,75 s), com sorteio entre 2 takes e uma entrada leve. Só a cauda esmaece: em takes sem `dur`, o fade fica limitado a 45% da duração.
- **Coruja:** o piado sorteia entre os 6 takes "Owl Hooting Reverberant Dry". Toca uns 4,5 s e esmaece em 1,6 s. As asas ganharam fade-in e fade-out.
- **Teste em Play:** com a câmera no animal, todos os Sounds carregaram e saíram com volume 0,00 (esmaecidos).
- **Estado:** hash do Sons 1428836852. A r2 ficou em `Backup_IA_antes_1711.Sons_r2`. Aguarda o usuário ouvir.
- **APROVADO pelo usuário em 17/11** (cervo e coruja r3). Todos os sons do piloto estão aprovados. O `IA_FaunaFloresta.rbxm` foi recompilado.
