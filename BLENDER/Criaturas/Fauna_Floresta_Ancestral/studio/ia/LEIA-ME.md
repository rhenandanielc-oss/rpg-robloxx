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

## 17/11: piloto pequeno no mapa real (Floresta, perto da Vila) [PROPOSTA]

Pedido do usuário: inserir os animais na floresta. Ele escolheu "piloto pequeno" e "perto da Vila Principal".

- **Onde:** `Workspace.Fauna_Floresta_Piloto`, uma pasta própria; nada fora dela foi alterado. Apagar a pasta remove tudo.
  - `IA`: cópia dos módulos (Anim, Config, Controlador, Movimento, Percepcao, Perfis, Sons), mais `CenaFloresta` e o script `IA_FaunaPiloto_Servidor`. Atributos `Ativo` e `Debug=false`.
  - `Animais`: Cervo_1-3, Javali_1-2 e Coruja_1, clonados dos modelos de teste (escala ×3).
- **Local:** a clareira `Exp_Clareiras.Clareira_Combate_13` (2464, ~20, 292), a leste da Vila. É 100% aberta e plana (medido por raycast).
  - Cervos ficam na clareira; javalis na borda do bosque (2441, 330) e (2446, 236).
  - A coruja usa galhos reais medidos no tronco de 3 carvalhos de `Arvores_Medias`:
    - A: Carvalho_A_m588, a 17,9 studs;
    - B: Carvalho_B_m598, a 10,5 studs;
    - C (seguro): Carvalho_C_m569, a 21,8 studs.
- **Correções gerais no Movimento (servem também à cena de teste):**
  - **Vizinhos:** os outros animais não bloqueiam o corpo; o passo se afasta deles. Antes, dois cervos se travavam um ao outro.
  - **Rampas:** rampa de terreno andável (normal com Y ≥ 0,6) não conta mais como parede. Antes, o cervo ficava preso olhando para um barranco.
  - Hash do Movimento: 769002308.
- **Config:** `DEBUG` vem do atributo `Debug` da pasta da IA. A cena de teste continua com o DEBUG ligado.
- **Teste em Play (17/11), com o jogador real andando:**
  - Os 3 cervos se alertam, fogem para o bosque e voltam para casa (≤3 studs).
  - O javali ameaça, investe e acerta a chifrada no terreno real.
  - A coruja decola e pousa no galho B (erro 0,0).
  - Sons tocam em todos.
  - Desempenho, A/B com a mesma câmera: 14,1 fps com os animais e 14,2 sem eles. Os animais não pesam; o fps baixo é da área/PC. Servidor a cerca de 56 fps.
- **Evidência:** `review/piloto_floresta/clareira_cervos.jpg`.
- **Pendências:**
  - quantidades, reaparecimento e porte oficiais;
  - grupos (cada cervo foge sozinho; não há manada);
  - celular;
  - a cena de teste não foi testada de novo depois das correções do Movimento.

## 17/11: IA de vivência na Lagoa_5 (habitats aprovados) [PROPOSTA], números [A TESTAR]

Tarefa: "Floresta Ancestral — IA de vivência dos três animais". O usuário autorizou o Studio, a escala realista (javali ×4,35, cerca de 2,9 studs na cernelha; cervo e coruja continuam ×3) e as 3 margens rasas.

### Onde está

- **Cena:** `Workspace.Fauna_Floresta_Piloto`, com o atributo `Cena = "CenaLagoa"` na pasta `IA`.
  - Animais: Cervo_1, Cervo_2, Javali_1 e Coruja_1.
  - Cervo_3 e Javali_2 ficaram na reserva, em `ServerStorage.Fauna_Floresta_Piloto_Reserva`.
- **Atributos da pasta `IA` (estado entregue):** `Ativo=true`, `Debug=false`, `TempoTeste=1`, `ForcarAgua=false`.
  - Esses dois últimos servem só para teste: `TempoTeste` divide as esperas de repouso (as ações rodam sempre em tempo real) e `ForcarAgua` antecipa a ida da coruja à água.
- **Módulos novos:**
  - `Vivencia.luau` (hash 230818737);
  - `CenaLagoa.luau` (503142123).
- **Módulos alterados** (cópias locais idênticas às do Studio):
  - Config 2139470059;
  - Movimento 1174962988;
  - Controlador 1851626851 (r13);
  - Sons 1246494467;
  - `IA_FaunaPiloto_Servidor` 38817248.
- **A cena de teste NÃO foi sincronizada:** `Teste_FaunaFloresta.IA_FaunaFloresta` continua nas versões antigas (Config 22496449, Movimento 769002308, Controlador 1092796326, Sons 1428836852). O `IA_FaunaFloresta.rbxm` não foi recompilado e não tem a vivência.

### Pontos (coordenadas reais, Lagoa_5; centro da área (1690, 40, -255), tamanho 220×80×230)

| Ponto | Posição | Frente | Observação |
|---|---|---|---|
| Casa Cervo_1 / Cervo_2 | (1628, -275) / (1637, -271) | leste | abrigo no bosque a oeste da lagoa |
| Cervo_ArbustoA | (1653,7, 40,73, -285,6) | (0,92, -0,38) | `Sotobosque/Arbusto_Largo_A_934`; pré-ponto a 10 studs |
| Cervo_ArbustoB | (1635,3, 42,78, -246,9) | (-1, 0) | `Arbusto_Largo_A_885` (o 887 ficava espremido entre a água e o barranco) |
| Cervo_Agua | (1665,9, 37,46, -263,6) | (1,00, 0,09) | margem rasa nova; pré-ponto a 9 |
| Casa Javali_1 | (1673, -186) | | sob carvalhos perto da lagoa, longe da rota dos cervos |
| Javali_Farejar | (1683, 41,02, -197) | (0,6, -0,8) | |
| Javali_Fucar | (1675, 42,0, -179) | (0, 1) | entre as raízes de `Carvalho_C_382` |
| Javali_Agua | (1696,3, 37,31, -226,1) | (0,04, -1,00) | margem rasa nova |
| Coruja: Vigia | (1742,2, 85,44, -279,7) | | galho de vigia, `Freixo_C_m283` |
| Coruja: Abrigo | (1719, 77,13, -319,4) | | poleiro abrigado (dorme), `Carvalho_B_m264` |
| Coruja: Seguro | (1736,2, 84,83, -309,9) | | `Freixo_B_376` |
| Presa_Norte / Presa_Noroeste | (1712, -300) / (1700, -308) | | roedor de TESTE (`Roedor_Teste`), local e removível |
| Coruja_Agua | (1710,4, 37,94, -262,6) | | margem rasa nova, lâmina de cerca de 0,5 |

Os pontos são criados no Play por `CenaLagoa.preparar`, como marcadores invisíveis em `Marcadores_Vivencia.Pontos`.

A margem do cervo ficou cerca de 8 studs ao lado da coordenada citada na pergunta de aprovação: o eixo foi refeito para a boca tocar a água com o corpo na pose do terreno.

### Rotinas

| Espécie | Ciclo |
|---|---|
| Cervo | repouso no abrigo {18–30 s} → arbusto (A ou B, livre/reservado) → Pastar {6–10 s} → água → Beber {5–8 s} → sai da margem → volta para casa |
| Javali | repouso {14–24 s} → Farejar → Fuçar ×2 → água → Beber (clipe novo do lote F, 5,2 s) → sai da margem → volta |
| Coruja | Vigia {10–18 s} olhando → mergulho no roedor de teste → leva a presa ao galho → come → a cada 3 ciclos desce à margem e bebe (clipe novo do lote E, 5,6 s) → Abrigo, cochila {16–26 s} |

Cada ida segue as fases:
- **Seleção** do ponto, com reserva compartilhada.
- **Aproximação:** retorno até um pré-ponto no eixo, depois linha final com perseguição pura, curva mais fechada e giro de 60°/s.
- **Alinhamento:** precisão 0,45 e 14°; se a chegada sair torta, há 1 nova tentativa.
- **Ação:** a pose segue o terreno pela linha dos cascos, e a boca é medida pelos offsets de `Config.boca`.
- **Saída:** `sairDoPonto` depois da água.
- **Retorno.**

Regras gerais:
- Um ponto reservado ou bloqueado leva a outro ponto, com até 2 tentativas e espera de 4–8 s.
- A ameaça tem prioridade: libera a reserva e recomeça do repouso, sem repetir a ação fora do ponto.
- O consumo é só visual.

### Margens rasas (alteração fora da pasta do piloto)

- As 3 prateleiras rasas de terreno da Lagoa_5 (cervo, javali e coruja) foram escritas com `WriteVoxelChannels`.
- O backup dos voxels originais fica em `Marcadores_Vivencia.Backup_Terreno`.
- **Rollback:** para cada região salva, `ReadVoxelChannels` do backup e `WriteVoxelChannels` de volta, removendo `ch.Size` antes de gravar. O erro medido na restauração foi ≤0,004 (quantização).
- Regras medidas:
  - superfície sólida = centro do voxel + 4·SolidOccupancy;
  - superfície da água = centro + 4·(LiquidOccupancy − 0,5);
  - a água não aparece no mesmo voxel do sólido.

### Testes em Play (rpg_roblox, 17/11)

**Cervo:**
- Arbusto A a 0–1° com a boca nas folhas = true; arbusto B a 0–4°, true.
- Água a 4–5°, contato 0,04–0,07; volta e repete.
- O Cervo_2 encontrou a água reservada, foi a outro arbusto e voltou depois.

**Javali:** ciclo completo.
- Farejar: contato 0,23.
- Fuçar: 0,10 a 0°.
- Água: -0,18 a 0°.
- **r13:** depois de beber, sai da margem e volta ao repouso. Antes ficava preso na margem. No teste: bebeu aos 120 s, chegou em casa aos 157 s e começou o 2º ciclo aos 161 s.
- O cervo usou o "desatolando" uma vez e chegou ao repouso.

**Coruja:**
- Garras a 0,00 do roedor; come no galho de vigia.
- Na margem, o bico fica a -0,05 da água; depois dorme no Abrigo. Fez 2 ciclos de caça seguidos.

**Interrupção por jogador:**
- Cervo comendo → Alerta → Fuga → Retorno → recomeça.
- Javali na água → fluxo de ameaça → retoma no repouso.
- Coruja na margem → Alerta → foge para a Vigia → volta a caçar.

**Ponto bloqueado:** um `Bloqueio_Teste` no arbusto A deu "indisponível (obstáculo)" e o cervo foi ao arbusto B. O bloqueio foi removido depois do teste.

**Os 4 juntos:** rodam simultaneamente; o console não teve erro da fauna. O erro `rbxassetid://203785492` não vem da fauna.

**Desempenho:** cliente a 14,3 fps com e sem os animais (o fps baixo é da área/PC); servidor a 56 fps.

### Evidências (`review/vivencia/`, fora do git)

- `v1/IA_FaunaFloresta_vivencia_v1.mp4`: visão geral. Tem 547 MB e precisa ser recodificado menor.
- `v2/IA_FaunaFloresta_contatos_v2.mp4`: closes de água (os 3) e mergulho.
- `v3/IA_FaunaFloresta_contatos_javali_v3.mp4`: o javali bebendo.
- `v5/IA_FaunaFloresta_closes_alimento_v5.mp4`: alimento e galho, com câmeras fixas por ponto.
- `pranchas_ref/{cervo,javali,coruja}_ref_x_vivencia.jpg`: ficha de referência ao lado dos closes.
- Capturas brutas em `cap1..cap5` (cerca de 3 GB) e quadros em `v*/quadros` (cerca de 6 GB), que podem ser apagados depois da revisão.

**Lição da gravação:** o `StreamingEnabled` precisa de `Player.ReplicationFocus = Marcadores_Vivencia.FocoVideo`. Sem isso, o cliente só recebe o terreno grosseiro e nenhum arbusto perto da Lagoa_5, e os closes saem escuros ou em blocos.

### Pendências e limitações

- **Fuçar do javali:** fica escuro (sombra profunda sob as raízes); a evidência visual de alimento é o Farejar.
- **Coruja:** o pouso do mergulho ainda corrige o rumo em até 39° no início.
- **Celular:** não testado.
- **Multiplayer:**
  - a reserva já é por servidor;
  - falta testar 2 jogadores reais interrompendo ao mesmo tempo;
  - falta medir a replicação de 4 animais por PivotTo em rede real;
  - falta testar o streaming com jogadores longe ou perto da lagoa.
- O place não foi salvo pela integração: salvar ou publicar fica com o usuário.

### 18–19/11: revisão r2 (pedido "Sim, corrija")

- **Cervo bebendo, medido no Play:** as quatro quartelas ficam 0,25–0,55 acima do chão (andando no plano: 0,10–0,43) e o corpo inclina −5,4°.
  - Nenhuma pata fica no ar. A impressão vinha da câmera de cima e de frente, somada às dianteiras abertas do clipe Beber aprovado.
  - Nada foi alterado na pose.
- **Cervos travados:** um teste com `TempoTeste=6` deixou os dois cervos ~80 s presos em "caminho falhou".
  - Causa: com raio de agente 2,0, o Pathfinding dá NoPath quando o cervo começa rente ao colisor de um carvalho; com 1,0–1,4 dá certo.
  - Correção: o `retorno` tenta um 3º raio, 1,0 (Controlador, hash 1833224556).
  - Reteste: 0 falhas de caminho nos cervos e no javali.
- **Vigia da coruja:** todos os galhos perto da Lagoa_5 ficam dentro das copas, e do chão a coruja não aparecia. O usuário escolheu (19/11) uma árvore seca nova.
  - Modelo: `BLENDER/Floresta/Arvore_Seca_Vigia/` (`gerar_arvore_seca.py`, GLB, blend, textura própria `casca_seca.png`).
    - Freixo morto de 21 studs (24,4 com raízes e lascas), 786 triângulos, galho horizontal quebrado a 13,5.
    - Importado pelo usuário (Import 3D).
  - No Studio:
    - Fica em `Fauna_Floresta_Piloto.Cenario_Vivencia.Arvore_Seca_Vigia`, com pivô (1724, 47,22, −283), escala 1:1 e galho para −X (lado da lagoa).
    - A MeshPart tem `CollisionFidelity` PreciseConvexDecomposition (a Default não incluía o galho), `CanCollide=false` e `CanQuery=true`.
    - O tronco ganhou um `Colisor` cilíndrico invisível (2,2 × 21).
  - Na CenaLagoa:
    - `S.arvore` aceita `{"@piloto", nome}`.
    - Vigia = (1720,65, 60,98, −282,41), dir (−1, 0,17), com topo na malha visível (o casco de colisão fica 0,14 acima). Hash 777471213.
  - Teste em Play:
    - mergulho com garras a 0,00 do roedor;
    - volta à Vigia nova, com pouso de erro 0,29 stud e 11°;
    - come;
    - desce à margem (bico −0,05);
    - dorme no Abrigo;
    - 2º ciclo: volta à Vigia e come de novo, visível do chão.
  - Evidências: `review/vivencia/r2/coruja_vigia_nova_*.jpg`; prancha `pranchas_ref/coruja_ref_x_vivencia.jpg` refeita.
  - Não foi gravado vídeo r2, para não pesar o PC.
- **Para desfazer a árvore:** apagar `Cenario_Vivencia.Arvore_Seca_Vigia` e voltar a linha `Vigia` da CenaLagoa para o Freixo_C_m283 (85,44).
- **Pendências que seguem:**
  - fuçar escuro;
  - cervos andando em subida sem inclinar o corpo (patas dianteiras chegam 2–3 studs dentro do barranco);
  - o asset 93876471178466 (textura da árvore) foi enviado pela conta do usuário via Import 3D.
- **APROVADO pelo usuário em 19/11:** a vivência r2 (árvore seca de vigia, caminho estreito e postura do cervo medida) é a base atual.
