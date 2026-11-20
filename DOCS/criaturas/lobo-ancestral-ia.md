# Lobo Ancestral: IA estratégica (protótipo, 19/11/2026)

Status:
- Protótipo **só** no place isolado Testes-loboancestral (salvo como v48). Não integrado ao jogo principal.
- Todos os números são [PROPOSTA]/[A TESTAR].
- Aguardando avaliação do usuário.

## Arquivos (só do Lobo)
- **`BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/kit/LoboIA.luau`** (novo; checksum atual 67436365): ModuleScript filho de `ServerScriptService.LoboAncestral_Kit.LoboKit_Servidor`.
- **`kit/LoboKit_Servidor.luau`** (checksum 461176496):
  - entrega ao módulo as funções do kit (alvos, proteções, superfície, chão, ações);
  - publica o golpe em curso no atributo `EmAtaque`, a mesma convenção do combate dos dragões;
  - o guardião antigo (`IA_Guardiao`) continua valendo para lobos sem `ia.v2`;
  - comandos novos no gancho de teste: `clonarIA2`, `iaInfo`, `setVida`, `setEnergia`, `vel`;
  - **bug corrigido:** desde a r8, um alvo que estava na pasta Alvos e também era percebido entrava duas vezes por quadro na estimativa de velocidade. A segunda passada valia zero, então a velocidade medida caía para cerca de 45%. Isso afetava a ameaça "aproximando" e a antecipação do Salto.
- **`kit/ConfigKitLobo.luau`** (checksum 743064509): bloco `IA_Lobo`. Os gatilhos de ameaça e a coleira continuam os de `IA_Guardiao` já documentados (22 / 45 / 3 studs/s; coleira 25 + 22).
- **Backup no Studio:** `ServerStorage.LoboKit_Servidor_r8_antes_IA2` (servidor e config r8).

## Como funciona
Princípios adaptados da IA dos dragões (Cerebro, Locomotor, Combate_Dragao_Servidor e o duelo tático de teste de 09/11), sem voo, sem as distâncias dos dragões e sem regras de ninho.

1. **Percepção e ameaça.** Usa a percepção do kit: raio, parede bloqueia, vegetação não. Cada alvo tem uma memória com nível, motivo, última posição e hora.
   - **Níveis:**
     - nível 1 = observado até 45 (só Alerta: encara e rosna, sem atacar);
     - nível 2 = perto (≤ 22) ou aproximando (≥ 3 studs/s);
     - nível 3 = atacou o lobo.
   - **Esquecimento:** em 8 s sem ver; ao morrer; ao ficar protegido (dono, aliado, zona segura, PvP); ou ao sair da coleira, medida até a superfície do alvo.
   - **Investigação:** quem sumiu deixa uma investigação da última posição.
   - **Troca de alvo** com histerese.
   - **Entre lobos [PROPOSTA]:** um lobo sem dono ignora outro lobo sem dono, a menos que seja atacado por ele. Não há regra de alcateia.
2. **Plano.** Planos com tempo mínimo de 1,2 s. Esquivar, Recuar e Desistir interrompem na hora.
   - **Calmo:** no posto, alterna Observar, Farejar e OlharTras.
   - **Alerta:** VirarE/D e Rosnar.
   - **Investigar:** FarejarAndando até a última posição, depois Farejar.
   - **Perseguir:** Corrida ou Trote, com previsão de até 0,8 s.
   - **Pressionar:** Trote, depois Andar com Mordida/Garra andando (r7). Se fica colado e fora do cone, sai em arco e volta de frente. Depois de 3 golpes seguidos, rodeia.
   - **Flanquear:** arco pelo lado livre, quando encarado depois de 2 golpes trocados.
   - **Esquivar:** quando há ataque anunciado (`EmAtaque`, ou estado de outro lobo do kit) de frente e a até 12. Usa Salto sem alvo se a direção estiver a até 45° da frente; senão, trota para longe girando em movimento.
   - **Recuar:** com vida abaixo de 35% ou energia abaixo de 18. Se uma esquiva interrompe, o recuo é retomado.
   - **Recuperar:** ronda andando por no mínimo 2,5 s até ter energia 55. Defende se o alvo encostar.
   - **Desistir / Retorno:** com vida abaixo de 12%, alvo inválido, protegido, perdido ou fora da coleira. Trota de volta ao posto, depois Calmo.
3. **Locomoção.** O modelo é ancorado e movido por PivotTo na velocidade de cada clipe: Andar 3,02, Trote 7,67, Corrida 21,43, FarejarAndando 1,61.
   - **Direção:** sempre para a frente. O giro é limitado por marcha (Trote 110°/s, Corrida 75°/s) e, em curva fechada, o passo e a passada do clipe desaceleram juntos.
   - **Giro no lugar:** em calma, giro grande parado usa VirarE/D. Andar usa a mistura reta + curva aprovada.
   - **Obstáculos:** sondas à frente (±35°, ±70°, ±105°, mantendo o lado que funcionou). O corpo do próprio alvo é obstáculo a até 5 studs, então o lobo encosta o focinho mas não atravessa. Separação de 7 studs entre lobos.
   - **Desnível:** sobe até 2,5 por passo. Desce até 8, o desnível do Salto, com queda suave. Passo além disso é recusado.
4. **Execução.** Os golpes passam pelas mesmas ações do jogador (podeUsar, energia, recarga, alcance até a superfície, linha de visão, proteções no impacto).
   - **Escolha** por condições reais, com peso, penalidade de repetição e variação pequena, registrada no log. Recusa vira bloqueio de 2 s.
   - **Investida** só com corredor livre: blockcast + chão firme.
   - **Uivo** só quando o bônus serve: alvo fugindo, vida em queda ou início do combate a distância.
5. **Frequência de decisão.** 0,2 s em ação; 0,5 s em calma; 1,5 s sem jogador a até 200 studs.

Logs: `[IA]` (planos e decisões com motivo, vida, energia e recargas), `[IA_BLOQUEIO]` (por que não atacou), `[HABILIDADE]`, `[PROTECAO]`.

## Testes (Play, 19/11; alvos = réplicas de ensaio, não criaturas reais)

| Caso | Resultado | Evidência |
|---|---|---|
| Calmo → alvo se aproxima → ameaça → Perseguir, Uivo, Salto, Investida, Mordida/Garra andando | funciona | ensaio 1, log |
| Flanquear, reposicionar em arco, ritmo (rodeia depois de 3 golpes) | funciona | ensaios 1, 5, 9 |
| Ataque anunciado (aviso 1 s, cone 70°, alcance 9) → Esquivar | funciona (parcial) | ensaio 2: em 6 golpes, 3 erraram por esquiva de movimento, 2 caíram na esquiva passiva do kit, 1 acertou |
| Vida baixa → Recuar → Recuperar → retomar; recuo retomado depois de esquiva | funciona | ensaio 3 |
| Alvo em zona segura → Desistir → posto → Calmo | funciona | ensaio 4 |
| Alvo grande (10×10×18): golpes até a superfície | funciona | ensaio 5 |
| Mureta de 3 (degrau) no caminho → desvio; Salto por cima | funciona | ensaio 5 ("caminho bloqueado (desnivel)") |
| Energia insuficiente → bloqueios por energia → Recuar → Recuperar | funciona | ensaio 6 |
| Alvo some atrás de parede alta → 8 s → Investigar → reencontrou e voltou a lutar | funciona | ensaio 7 |
| Alvo morto → Desistir → posto | funciona | ensaio 8 |
| Dois lobos com IA + alvo móvel em círculo; fuga para fora da coleira → os dois desistem | funciona | ensaio 9 |
| Parede criada sobre o lobo / degrau alto | falha corrigida e reensaiada | o vídeo (ensaio 7) mostra o lobo em cima da parede de 20 (a suavização deixava subir). Depois da correção: Y 0 ("passo recusado: degrau 20"); começando em cima de um bloco de 4, desce normalmente |
| Lobo do dono (seguir o jogador) | inalterado | o código do seguir não mudou |
| Criatura real, PvP, multiplayer, celular, várias cópias com carga real | não testado | sem criatura real neste place; um só jogador |

## Limitações e pendências
- **Esquiva:** fraca contra golpes rápidos. Sem clipe de salto para trás ou de lado, ela depende do Salto (que só sai a até 45° da frente) ou de trotar para longe.
- **Lobo selvagem × jogador:** pela regra copiada do Nucleo, o jogador só é alvo com PvP ligado. Atacar jogadores fora do PvP precisa de uma regra sua.
- **Comportamentos sem regra ou sem recursos:** alcateia/matilha, proteção do dono, caça, presas, loot, sono, filhotes, ovos e patrulha não foram implementados.
- **Integração ao Nucleo:** a proposta do contrato de criatura (§12 do relatório de compatibilidade) continua pendente.
- **Ruído no log:** depois que o alvo morre com uma investigação antiga pendente, o lobo passa por Investigar por cerca de 2 s antes de desistir.
- **Glitch não reproduzido:** num teste curto, logo depois de uma parede ser criada sobre o lobo, o alvo foi "esquecido por coleira" por 1,3 s e voltou.

## Duelo Lobo × Lobo com a IA (19/11, place v48)
- **Montagem:**
  - dois Lobos com a IA estratégica, cada um no seu posto, 40 studs um do outro;
  - vida 220 em cada um, ajustada só no teste para chegar ao recuo;
  - pela regra [PROPOSTA], lobo selvagem só briga com outro lobo se for atacado. Por isso o teste começa com uma **provocação explícita**: A causa 1 de dano em B pelo contrato `ReceberDano`.
- **Correção feita por causa do primeiro duelo:**
  - **Problema:** os dois "esqueciam" o rival no meio da luta ("sumiu há 8 s" com o outro a 4 studs). A permissão de atacar outro lobo expirava 6 s depois do último golpe recebido.
  - **Correção:** quem atacou o lobo vira ameaça **pessoal** ("rival em luta"), como a ameaça pessoal do Cerebro dos dragões. A luta continua enquanto o rival estiver à vista e dentro da coleira.
  - **Junto:** a separação entre lobos passou a medir pelo meio do corpo (o pivô fica na traseira).
  - Módulo `LoboIA.luau`, checksum 565018233.
- **Resultado (72 s de luta, tempo real), funciona:**
  - B revida a provocação com Salto, A responde;
  - os dois usam Mordida, Garra, Investida, Salto e Uivo: A 4/6/4/3/4, B 9/4/3/3/4 (Mordida, Garra, Investida, Salto, Uivo);
  - esquivas pelo golpe anunciado do outro: A 8, B 7;
  - flancos de lados opostos;
  - A recua com vida baixa (33%) e recupera;
  - cada lobo desiste quando o rival sai da sua coleira e volta à luta se for atacado de novo.
  - Sem "esquecimento" falso.
  - Terminou no tempo, sem vencedor (A 118/220, B 141/220). O resultado não mede equilíbrio: os dois têm o mesmo kit e o mesmo valor.
- **Limites:**
  - às vezes os corpos ficam muito próximos na luta corpo a corpo (a distância até a superfície chegou a 0);
  - lobos sem dono não fazem rodízio nem formam alcateia, porque não há regra para isso;
  - lobo do dono contra lobo selvagem com a IA não foi testado nesta rodada (o duelo da r8 usou o lobo do dono guiado pelo gancho).
- **Evidências:** `studio/review/Lobo_IA_duelo_lobos.mp4` (86 s) e `ia_duelo_lobos_prancha.jpg`.

## Duelo mais móvel + esquiva visível (19/11, place v55; aguardando avaliação)
Pedido do usuário: corrigir a luta Lobo × Lobo, que ainda parecia parada, e fazer a esquiva parecer um **pequeno teleporte lateral**, com **faixas visíveis**.

**Medição do problema (v48, mesmo duelo).** O tempo imóvel com alvo válido vinha quase todo de pausas **em habilidade** (por lobo, 12–16 s em 72 s):
- Uivo parado de 2,6 s, usado até 4 vezes;
- Mordida/Garra **paradas**, 9 no total;
- preparação da Investida e do Salto.

Imóvel "livre" (falha de locomoção) era só 0,5–2,3 s. Nenhuma esquiva tinha reação visual: as passivas evitavam o dano sem nada aparecer.

**Mudanças (só arquivos do Lobo):**
- **`LoboIA.luau`** (checksum 95477265):
  - **Pressão em ciclos** em vez de estacionar na faixa de alcance:
    - *Entrar:* arco curto de um lado; a reta final chega **de frente**, parando 0,4 fora do contato; Mordida/Garra **andando**, começando até 1 stud antes enquanto anda. O kit valida alcance e cone no contato.
    - *Abrir:* depois de 2 golpes, ou colado sem golpe, ou desalinhado, sai trotando em arco de 65° e cerca de 9 studs.
    - *Reentrar:* só com distância ≥ 8. Troca de lado quando o alvo encara o lado atual ou quando o lado está bloqueado.
  - Golpe básico **parado** fica proibido na pressão, no flanco e na perseguição.
  - Uivo no máximo uma vez por alvo, salvo quando o alvo foge.
  - Esquiva ativa usa primeiro o deslocamento do servidor; com bloqueio, cai no trote antigo.
  - **Separação dura:** um passo que aproximaria o meio do corpo a menos de 4,5 do meio de outro lobo é cancelado.
- **`LoboKit_Servidor.luau`** (checksum 763452581): `K.esquivaDesloc`, um deslocamento lateral de 5 studs em 0,12 s. O servidor valida:
  - o trajeto, com raios na traseira, no meio e na frente do corpo;
  - o chão sob as patas de trás e da frente (borda/desnível até 2,5);
  - corpo de outra criatura no destino;
  - zona segura e território;
  - e prefere o lado para onde o atacante não olha.
  - **Uso:** a esquiva passiva sorteada mantém a chance e o resultado de dano atuais e ganha a reação visível; a ativa da IA sai da linha do golpe.
  - **Sem lado seguro:** reação curta no lugar, com motivo no log `[ESQUIVA]`.
  - **Proteções:** intervalo de 0,7 s evita deslocamento duplo; durante o deslocamento nenhuma habilidade começa e a locomoção espera.
  - **Gancho de teste:** `esquiva`.
  - **Não cria:** habilidade, invulnerabilidade nem bônus.
- **`LoboKit_Cliente.luau`** (checksum 27766693): evento `Esquiva`.
  - **Silhueta residual** na saída: cópia local na pose do instante (ossos copiados), em ForceField verde, some em cerca de 0,35 s.
  - **Faixas verdes de ar** (o mesmo vento aprovado) desenhadas pelo próprio deslocamento, somem em cerca de 0,3 s.
  - Bloqueio: duas rajadas curtas em volta do corpo.
  - Nada fica no corpo nem cobre pelo ou rosto. Só desenha com a câmera a até 150 studs; no celular, metade das faixas.
- **`ConfigKitLobo.luau`** (checksum 895946222): `EsquivaVisual` e `IA_Lobo.pressao`/`corpoMin`, todos [A TESTAR].
- **Backup no Studio:** `ServerStorage.Backup_KitLobo_IA_v48_2026-11-19`.

**Métricas (duelo padrão: mesmos lobos, vida 220, postos, provocação e 72 s; por lobo A / B).**

A contagem dos golpes foi corrigida durante a tarefa:
- o log do kit guarda só 400 linhas;
- várias linhas compartilham o mesmo carimbo de tempo;
- a linha de acerto contém o nome dos dois lobos.

Por isso, os valores "antes" abaixo são da medição v48 refeita com a contagem certa.

| Métrica | Antes (v48) | Depois |
|---|---|---|
| Tempo imóvel com alvo válido | 22% / 34% (outra medição v48: 28% / 25%) | 21% / 21% |
| Desse tempo: imóvel "livre" / em habilidade | 0,7 / 13,3 s e 2,3 / 16,4 s | 1,6 / 10,6 s e 0,8 / 9,7 s |
| Golpes básicos parados / andando | 4 / 7 e 5 / 9 | 0 / 12 e 0 / 7 |
| Deslocamento | 390 / 344 studs | 459 / 437 studs |
| Precisão (acertos / tentativas) | 8/16 e 8/17 (48%) | 11/18 e 6/13 (55%) |
| Sobreposição (meio a meio < 3,5) / distância mínima | 0,0 s / 3,8 | 0,0 s / 4,5 |
| Esquivas com reação visível | 0 | 11 deslocamentos + 7 reações no lugar, com motivo |

**Testes específicos (Play):**

| Caso | Resultado |
|---|---|
| Esquiva livre | funciona (5,0 studs, 0,12 s) |
| Parede de um lado | funciona (vai para o outro lado) |
| Paredes dos dois lados | funciona (reação no lugar, "parede / parede") |
| Borda de um lado (plataforma de 10) | funciona (fica na plataforma) |
| Plataforma estreita | funciona (reação no lugar, "desnível 10 / 10") |
| Outro lobo dos dois lados / de um lado | funciona (reação no lugar / lado livre) |
| Zona segura de um lado | funciona (evita a zona) |
| Borda do território (IA) | funciona (vai para dentro) |
| Esquiva ativa (IA) e passiva (sorteio) no duelo | funciona; coincidência ativa + passiva = reação no lugar ("deslocamento recente"), sem deslocamento duplo |
| Ataque durante a marcha / alvo móvel | funciona (todos os básicos andando contra o rival em movimento) |
| Silhueta no cliente | funciona (60 ossos, pose copiada, malha em ForceField) |
| Custo com 6 lobos esquivando juntos | funciona: quadro do cliente igual à base (66,7 ms; Studio em segundo plano a cerca de 15 qps); efeito do Lobo com pico de 0,05 ms; 18/18 deslocamentos; servidor a 60/s |
| Celular, multiplayer, criatura real, PvP | não testado |

**Problemas encontrados e corrigidos durante a tarefa:**
- A primeira versão da pressão perdia acertos: chegava em arco de 25° e ficava fora do cone. A reta final de frente e o início antecipado do golpe resolveram.
- A reta final ainda deixava os corpos se sobreporem por 2,1 s. A parada fora do contato e a separação dura resolveram.

**Limites:**
- Parte do tempo imóvel continua sendo pausa intencional de habilidade (Uivo parado, preparação da Investida e do Salto).
- A esquiva ativa não escapa de golpes muito rápidos; nesses casos a passiva continua decidindo.
- A silhueta é uma cópia local do modelo por esquiva; com muitos lobos perto, vale observar o custo no celular.
- Números [A TESTAR].

**Evidências:**
- `studio/review/Lobo_duelo_movel_esquiva_antes_depois.mp4`: antes × depois lado a lado em tempo real, esquiva em câmera lenta 0,25× e cartão de métricas. O lado "antes" do vídeo é a 1ª medição v48.
- `duelo_movel_antes_depois_prancha.jpg`.
- `esquiva_referencia_x_studio.jpg`.

## Refino de ritmo e posicionamento (19/11, place v64; aguardando avaliação)
Pedido: luta mais móvel e estratégica sem perder acertos, esquivas visíveis preservadas e corpos sem se espremer. Só no place isolado.

**Medição nova (`DueloIA2_TEMP`, temporário e removido).** Duelo padrão: mesmos postos, vida 220, provocação e 72 s. Por lobo, mede:
- imóvel "livre" (espera da IA) separado da pausa de clipe, por estado (Uivo, Investida, Salto, giro VirarE/D);
- giro em volta do rival e variação de distância;
- básicos andando/parados, contatos/tentativas;
- esquivas deslocadas/bloqueadas com motivo;
- **folga entre silhuetas**: cápsula da anca ao focinho, raio 1,0. A medida meio a meio do corpo, usada antes, deixava o focinho atravessar sem registrar.

**Mudanças (só arquivos do Lobo):**
- **`LoboIA.luau`** (checksum 818476994):
  - **Separação pela silhueta:** cápsula anca→focinho (ponta a cerca de 6,6 do pivô). Encostar (folga até −0,15) é permitido; passo que entra mais que isso é cancelado.
  - **Saída do contato:** o lobo vira no lugar com o clipe VirarE/D aprovado (patas giram junto), para o lado que afasta o focinho, e a decisão abre espaço.
  - **Sonda do corpo do alvo** só na direção do alvo. Antes ela travava também as saídas, o que deu um impasse encostado de cerca de 40 s numa versão intermediária.
  - **Uivo:** uma vez por rival em cada combate, só com espaço (≥ 14) e com o rival sem avançar. Era a maior pausa da v55.
  - **Depois da Investida:** sai com o plano "abrir".
  - **Estilo próprio de cada lobo**, sorteado uma vez e registrado no log: arco, ângulo/raio de saída, golpes por entrada e lado inicial. Evita decisões espelhadas, sem coordenação entre os rivais.
  - **Testado e descartado:** chegar pelo lado do rival (`retaLado` 30, r5). A precisão caiu para 35% e o giro também; ficou desligado (`retaLado` = 0).
- **`LoboKit_Servidor.luau`** (checksum 351409668): a esquiva tenta, em ordem, laterais, depois **diagonais se afastando do atacante**, depois **laterais curtas (3,5)**. O log lista o motivo de cada candidato recusado.
- **`ConfigKitLobo.luau`** (checksum 973254730): `capsula`, `folgaCorpo`/`folgaTol`/`folgaPiso`, `virarContatoIntervalo`, `estiloVar`, `uivo.fugaDist`/`avancoMax`/`distSegura` 14, `pressao.retaLado`, `EsquivaVisual.diagonal`/`distCurta`. Todos [A TESTAR].
- **Backup no Studio:** `ServerStorage.Backup_KitLobo_v55_2026-11-19`.

**Resultados: mediana de 3 duelos × 2 lobos (72 s).**

| Métrica | v55 (3 duelos) | r6 (3 duelos) | Situação |
|---|---|---|---|
| Tempo imóvel com alvo válido | 20,5% | 17% | funciona (menor) |
| Imóvel "livre" (espera da IA) | 1,85 s | 1,3 s | funciona |
| Uivo parado | 5,4 s | 1,6 s | funciona (clipe intacto, menos usos) |
| Giro VirarE/D para sair do contato | 0 | 3,0 s | pausa exigida pelo clipe (2,4 s por giro de 90°) |
| Giro em volta do rival | 2.005° | 1.900° | **falha** (não aumentou) |
| Variação de distância | 300 | 249 | **falha** (não aumentou) |
| Precisão (contatos/tentativas, por duelo) | 48% (47–61%) | 42% (35–47%) | **parcial**: um pouco menor |
| Básicos parados | 0 | 0 | funciona |
| Esquivas deslocadas / no lugar | 42 / 13 | 44 / 10 | funciona: em r6 nenhuma no lugar por falta de espaço (só durante clipe de habilidade ou anti-duplo) |
| Folga mínima entre silhuetas | −0,7 a −1,6 | −0,7 a −0,9 | **parcial**: a locomoção da IA não cruza mais (r3/r4: −0,04 a −0,15); o restante tem origem não isolada (hipótese: pouso do Salto/Investida do kit) |
| Travamentos (> 1 s parado livre) | 0 | 0 | funciona (o impasse da versão intermediária foi corrigido) |

**Regressão (Play):**

| Caso | Resultado |
|---|---|
| Esquiva livre | funciona |
| Parede de um lado | funciona |
| Corredor com paredes dos dois lados | funciona (reação no lugar; os 6 candidatos recusados, com motivo) |
| Borda de um lado | funciona |
| Plataforma estreita | funciona (reação no lugar, "desnível 10" × 6) |
| Outro lobo dos dois lados / de um lado | funciona (reação no lugar / lado livre) |
| Zona segura de um lado | funciona |
| Alvo móvel atacando com aviso | funciona (básicos andando, acertos, esquiva) |
| Vida baixa | funciona (Recuar → Recuperar) |
| Energia baixa | funciona (Recuar) |
| Erros de script | nenhum |
| Celular, multiplayer, criatura real, PvP | não testado |

**Limites:**
- A "mudança de posição útil" (giro e variação de distância) não aumentou; a variação de distância caiu.
- A precisão ficou 6 pontos abaixo na mediana; a faixa por duelo se sobrepõe à da v55.
- Sair do contato custa um giro de clipe de 2,4 s; preservado, porque é o clipe correto, sem patinação.
- Ainda há sobreposição de silhuetas fora da locomoção da IA, sem origem confirmada.
- Números [A TESTAR].

**Evidências:**
- `studio/review/Lobo_duelo_ritmo_v55_x_r6.mp4`: v55 × r6 lado a lado em tempo real, mesma câmera; esquiva em câmera lenta (efeito visual inalterado nesta rodada); cartão de métricas.
- `duelo_ritmo_v55_x_r6_prancha.jpg`.
- `duelo_ritmo_referencia_x_studio.jpg`.

## Correção de precisão e posição: r7 (19/11, place v66; aguardando avaliação)
Pedido "Sim, corrigir", sobre as duas falhas da r6: mudança de posição útil e precisão.

**Causas encontradas:**
- O lobo abria espaço ("colado e desalinhado"/"silhueta encostada") ou virava no lugar **antes do dente chegar**: o golpe básico em curso era interrompido.
- Os arcos de entrada e saída eram curtos (25° / 65°, raio 9) e geravam pouco giro em volta do rival.

**Mudanças:**
- **`LoboIA.luau`** (checksum 67436365): golpe básico em curso, até o contato (`esperaContato`), não é interrompido por abrir espaço nem por giro no lugar.
- **`ConfigKitLobo.luau`** (checksum 982673050):
  - `pressao.arco` 25 → 35;
  - `abrirAng` 65 → 90;
  - `abrirRaio` 9 → 11;
  - `antecipa` 1,0 → 0,6.
  - Todos [A TESTAR].
- **Medição:** passou a registrar o estado de cada lobo quando as silhuetas se cruzam além de 0,15.

**Resultados:** mediana de 3 duelos × 2 lobos. As taxas são por segundo de combate, porque a r7 passou mais tempo fora de combate: os arcos maiores levam o rival para fora da coleira e o combate termina.

| Métrica | v55 | r6 | r7 | Situação |
|---|---|---|---|---|
| Tempo imóvel com alvo válido | 20,5% | 17% | 18% | funciona |
| Giro em volta do rival | 34,8°/s | — | 43,7°/s (+26%) | funciona |
| Variação de distância | 5,25/s | — | 5,8/s (+10%) | funciona |
| Precisão por duelo | 48% (47–61%) | 42% | 45% (42–57%) | comparável (−3 pontos na mediana, faixas sobrepostas) |
| Uivo parado | 5,4 s | 1,6 s | 1,6 s | funciona |
| Giro no lugar (clipe VirarE/D) | 0 | 3,0 s | 2,6 s | pausa exigida pelo clipe |
| Básicos parados | 0 | 0 | 0 | funciona |
| Corpos cruzando > 0,15 | em todos os duelos | — | 0 s em 2 duelos, 0,3 s em 1 (com os dois lobos em locomoção da IA) | **parcial** |
| Esquivas no lugar por falta de espaço | algumas | 0 | 0 | funciona |

**Regressão:** alvo móvel atacando, vida baixa (Recuar → Recuperar) e energia baixa (Recuar), sem erros de script. O código da esquiva não mudou; os 8 casos (parede, borda, corpo, zona) continuam válidos pela rodada anterior.

**Limites:**
- **Tempo em combate menor:** 30–42 s em alguns lobos, contra 45–62 s na v55. O motivo é a desistência por coleira; os totais absolutos caem.
- **Cruzamento restante:** 0,3 s num duelo, durante locomoção. A hipótese, não confirmada, é o giro VirarE/D aplicado no fim do clipe ou o trajeto da esquiva em diagonal.
- **Não testado:** celular, multiplayer, criatura real e PvP.

**Evidências:**
- `studio/review/Lobo_duelo_v55_x_r7.mp4`: v55 × r7 lado a lado em tempo real, mesma câmera; esquiva em câmera lenta (visual inalterado); cartão de métricas.
- `duelo_v55_x_r7_prancha.jpg`.
- `duelo_r7_referencia_x_studio.jpg`.

## Golpes por porte, queda e decisão de finalizar (19/11, place v75; aguardando avaliação)
Protótipo isolado no kit do Lobo, no place Testes-loboancestral (73543092389791). O contrato e o plano de adoção pelas outras domesticáveis estão em `studio/kit/CONTRATO-CONTROLE-PORTE.md`. Nenhuma outra espécie foi alterada.

**Regras oficiais usadas** (v6.2 §0b–0d):
- porte = ombro (ou comprimento ÷ 2,5) × tamanho da idade;
- classes: P < 3, M 3–8, G 8–16, C ≥ 16;
- lentidão de no máximo 60%;
- ≥ 4 s entre atordoamentos;
- colossal sofre metade da duração;
- Força resiste a derrubada.

O resto é [PROPOSTA]/[A TESTAR] em `ConfigKitLobo.Controle`.

**O que foi implementado:**
- **Controle depois de acerto válido com dano > 0:** uma rolagem por golpe, no servidor.
  - Chance = base × impacto do golpe × porte relativo × Força relativa.
  - Impacto: Mordida 1,0, Garra 0,8, Salto 1,6, Investida 2,0.
  - Queda só com Salto/Investida; claudicação só com impacto ≥ 1.
  - Log com porte, medida, idade, Força, chances e resultado.
- **Estados novos** (sem usar `Incapacitado` na queda):
  - `LentidaoControle`/`Mancando` (25% / 45%);
  - `Caido`/`CaidoAte`, com 3,0 s base, Impacto → Deitado → LevantarDeitado em velocidade 1,5;
  - quem cai perde a habilidade ou o golpe em curso (sem dano atrasado) e não esquiva.
- **Finalização anunciada** (`K.finalizar`):
  - rosnado de 0,9 s e mordida de contato; condições conferidas a cada quadro e no contato;
  - cancela sem dano em qualquer falha;
  - selvagem morre (sem loot/respawn); criatura de jogador é retirada (`RetiradaDeCombate` + `Incapacitado`, Vida mantida, refúgio só simulado); humano nunca.
- **IA:** uma decisão por queda, com o motivo no log.
  - Alvo com Vida > 35%: APROVEITA (golpes normais).
  - Alvo enfraquecido: FINALIZAR ou POUPAR, pesando dono, luta prévia, outros inimigos, própria Vida/energia, fuga do alvo, distância, tempo até levantar, linha de visão, proteção e coleira.
  - POUPAR: rosna e não morde quem está no chão.
- **Proteção nova no kit:** a criatura de outro jogador só é alvo do lobo de um dono com `PvPAtivo`.
- **Comandos de teste:** `porte`, `simControle`, `derrubar`, `finalizar`, `forcarControle`, `ultimaFinalizacao`, `ultimoControle`, `estadoLobo`; atributo `DecisaoQueda`.

**Correções feitas durante os testes:**
1. O primeiro Salto derrubava e já finalizava um lobo com 55% de Vida. Agora só finaliza com o alvo ≤ 35%.
2. A redução de PvP valia também contra um selvagem. Agora vale só entre jogadores.
3. Os 4 s contavam do início da queda, e o lobo era derrubado de novo enquanto levantava. Agora contam do fim do levantar.
4. O cone do anúncio oscilava com o corpo caindo e cancelava no mesmo quadro. Agora há histerese de +30° e +1 stud.
5. Perto e de lado, o lobo não girava. Agora segue andando até ficar de frente; cone de 120°.
6. A queda de 2,4 s não dava tempo de abordar. Passou a 3,0 s.

**Matriz** (Play no Studio, PC):

| Caso | Resultado | Situação |
|---|---|---|
| Frequência por porte (2000 sorteios) | proporcional; ver tabela abaixo | funciona |
| Lobo atacante maior/menor | Dragão→Lobo, Investida: queda 77%; Filhote→Lobo: 7% | funciona |
| Golpe esquivado ou protegido | dano 0 → nenhuma rolagem | funciona |
| Duelo natural 90 s (Vida 220) | 3 quedas, todas levantaram; APROVEITA (alvo forte) | funciona |
| Finalizar (decisão natural) | B 32–35% derrubado → anúncio → morte (D2 e clipe 1) | funciona |
| Poupar (decisão natural) | própria Vida 24–27%; alvo já fugindo; não chega a tempo | funciona |
| Recuperação do poupado | LevantarDeitado, volta à luta | funciona |
| Cancelamento: alvo levanta / lobo derrubado / alvo removido / zona segura / obstáculo | cancela sem dano; sem atributo preso | funciona |
| Confiabilidade da finalização forçada (início a 13 studs) | 4/4 concluídas | funciona |
| Confiabilidade com início a 9 studs (corpos sobrepostos) | 1–2/4; abandono "não chega antes de levantar" | parcial (artefato do arranjo) |
| PvP desligado / aliado do dono | sem dano e sem controle | funciona |
| PvP ligado, 4 mordidas com queda forçada | 1,5 s → 0,75 s → imune → imune; dano normal | funciona |
| Ordem de finalizar do dono em PvP | cancela "alvo levantou", porque a queda de 1,5 s é curta demais | **falha de ritmo** ([A TESTAR]) |
| Criatura de jogador finalizada (PvE ou PvP com queda longa) | RETIRADA, Vida mantida, sem morte | funciona (refúgio simulado) |
| Humano / fauna de recurso | nunca finalizável; sem controle | funciona |
| Anti-repetição (60 s com toda colisão forçada a queda) | nenhuma queda antes de 4 s de pé; 1 negada virou claudicação | funciona |
| Lobo do dono decidindo sozinho | código: nunca finaliza ("sem finalização automática") | **não testado** (sem IA no lobo do dono) |
| Visual do poupar | o lobo rosna parado sobre o corpo e não recua até 8 studs | **falha visual** |
| Queda visual | Impacto + transição para Deitado (0,25 s); sem clipe próprio de tombo | parcial |
| Celular, multiplayer, PvP real, refúgio real, outras espécies | — | não testado |

**Frequência por porte** (atacante Lobo Adulto, médio, Força 20; Q queda, M manca, L lento; % por golpe):

| Alvo | Mordida | Salto | Investida |
|---|---|---|---|
| pequeno (Filhote 2,5) | M28 L58 | Q48 M46 L6 | Q63 M38 |
| médio (Lobo Adulto) | M15 L31 | Q24 M22 L49 | Q31 M29 L40 |
| grande (Leão sim. 11,5/F38) | M4 L8 | Q8 M6 L14 | Q8 M9 L17 |
| grande (Urso sim. 9/F65) | M2 L6 | Q5 M4 L10 | Q7 M6 L12 |
| colossal (Búfalo sim. 16, imune a queda) | M1 L2 | M2 L4 | M2 L4 |
| colossal (Dragão sim. 21/F100) | M1 L2 | Q2 M1 L3 | Q2 M2 L3 |

**Durações e tempos:**
- **Queda** (base 3,0 s, × porte): P 3,45 / M 3,0 / G 2,4 / C 1,5. PvP: 1,5 → 0,75 → imune 8 s.
- **Fuga:** queda + levantar ≈ 4,5 s no médio.
- **Finalização:** anúncio + bote ≈ 1,4 s.

Os portes "sim." são lobos do kit com atributos de porte; não são as criaturas reais.

**Evidências** (`studio/review/`):
- `Lobo_queda_finalizar_poupar.mp4`: 4 clipes em tempo real — finalizar natural, poupar natural, cancelamento, criatura de jogador retirada — mais cartões de frequência e resultados;
- `queda_escolha_desfecho_prancha.jpg`;
- `queda_referencia_x_studio.jpg`.

**Checksums instalados = locais:**
- servidor 460254360;
- IA 278147678;
- config 360000508;
- cliente 27766693 (inalterado).

**Backup:** `ServerStorage.Backup_KitLobo_v66_2026-11-19`.

**Rig, textura e desempenho:**
- Nenhum clipe, rig ou textura novos.
- O custo extra é uma rolagem por golpe, atributos e `task.delay`; nada por quadro, exceto o laço do anúncio (≤ 1,4 s, só durante a finalização).
- Celular não medido.

**Pendências:**
- Poupar: recuar visivelmente até 8 studs.
- Clipe de tombo próprio (opcional).
- Ritmo da finalização em PvP.
- Lobo do dono com ordem explícita.
- Integração do refúgio.
- Adoção pelas outras espécies nos chats delas.

## Hitbox de contato e finalização própria do Lobo (20/11, place v81; aguardando avaliação)
Pedido: "ele bate de longe; quero que bata diretamente no oponente". Ao finalizar, o lobo deve puxar o caído, morder e estrangular; as outras criaturas terão outra finalização.

**Causa do "bate de longe":**
- O alcance era medido da **anca** do lobo (pivô) até a **caixa fixa da malha** do alvo, de 3,7 × 8,5 × 13,4 studs, que inclui cauda e pelagem e não acompanha a animação.
- A Mordida contava a 7 studs da anca; a Investida parava a ~8 studs na caixa; o Salto acertava a 8,5 studs.
- Com o alvo deitado, a caixa continuava no lugar do corpo em pé.

**Mudanças:**
- **Corpo real** (`ConfigKitLobo.Hitbox`, [A TESTAR]):
  - cápsulas nos ossos que acompanham a animação: tronco, pescoço, cabeça e patas; cauda e pelos ficam de fora;
  - outras criaturas com ossos usam osso → pai com raio genérico; sem ossos, continua a caixa das partes.
  - `pontoProximo` passou a usar esse corpo, o que vale também para a IA, a coleira e o pouso do Salto.
- **Golpe pelo ponto de ataque:**
  - Mordida: focinho (Mandíbula + 0,9) a ≤ 1,0 do corpo no quadro de contato;
  - Garra: patas dianteiras ≤ 1,0;
  - Salto: focinho ou patas ≤ 1,5 ao pousar;
  - Investida: criaturas saem do blockcast; morde com o focinho ≤ 1,0; peito encostado ou alvo protegido param sem dano.
  - Erros são registrados com a distância.
- **IA:** só ataca se a boca ou pata vai tocar (bote ~0,6 + velocidade de aproximação × 0,45 s).
- **Finalização do Lobo** (`Controle.estilo`; as outras espécies definem a sua):
  1. rosna (0,9 s);
  2. morde o pescoço (até 3 studs);
  3. **puxa** o caído até a boca (até 3,5 studs, nunca através de parede);
  4. a cabeça desce pelo clipe **Comer** e congela na altura do pescoço;
  5. **estrangula** por 2 s, sacudindo ±7° com trancos de 0,35 para trás, com o corpo preso acompanhando a boca;
  6. desfecho.
  - **Interrompível:** se o lobo for ferido, solta; também se for derrubado, se o alvo ficar protegido ou for removido, ou sem linha de visão.
  - A queda fica prolongada enquanto estrangula; se cancelar, o alvo levanta.
- **Correções:**
  - a finalização não começa durante um giro no lugar (o giro aplicava 90° no fim e virava o lobo de costas);
  - é uma decisão por queda até o alvo levantar (antes, a queda prolongada gerava uma segunda finalização);
  - a abordagem mira o pescoço.

**Matriz** (Play no Studio, PC):

| Caso | Resultado | Situação |
|---|---|---|
| Mordida a distâncias conhecidas | acerta com o focinho a −1,17 / −0,28 / −0,23 / 0,35 do corpo; erra a 1,63 | funciona |
| Garra | acerta com a pata a 0,48; erra a 1,09 e 1,84 | funciona |
| Salto com alvo | pousa com o focinho a 0,08 e acerta | funciona |
| Investida | morde com o focinho a 0,94 e 0,68; sem alcance, termina sem dano | funciona |
| Finalização (puxar + estrangular) | 3/4 concluídas; 1 abandonou ("não chega antes de levantar"); boca no pescoço −0,9 durante 2 s | funciona |
| Finalização natural no vídeo | rosna → morde → puxa 1,8 → estrangula 2 s → morte | funciona |
| Interrupção por dano durante o estrangulamento | solta, sem dano final; o caído levanta e a luta volta | funciona |
| Duelo IA × IA 45 s | 2 acertos em 8 tentativas (antes ~45%); recuo e esquiva do rival durante o bote agora escapam | **regressão de ritmo** (pendente) |
| Criatura de jogador / PvP / humano | regras de 19/11 inalteradas; a finalização nova leva ao mesmo desfecho | não retestado nesta rodada |
| Celular / multiplayer | — | não testado |

**Evidências:**
- `studio/review/Lobo_hitbox_finalizacao_estrangular.mp4`: hitbox (erro × acerto), finalização natural, interrupção e cartão de medições.

**Checksums instalados = locais:**
- servidor 823682829;
- IA 879012181;
- config 482109497;
- cliente 27766693.

**Backup:** `ServerStorage.Backup_KitLobo_v75_2026-11-19`.

**Rig, textura e desempenho:**
- Nenhum clipe novo: reaproveita Rosnar, Mordida e Comer.
- Custo: cápsulas calculadas só nos golpes (8 segmentos) e o laço do estrangulamento (≤ 2,4 s).
- Celular não medido.

## Finalização corrigida: mordida no flanco (20/11, place v91; aguardando avaliação)
Correção do usuário: o Lobo vai ao meio do corpo do caído, na lateral da barriga, morde e sacode a **própria** cabeça. Não puxa, não estrangula e não sacode o corpo do alvo. A sequência da v81 (pescoço → puxar → Comer congelado → estrangular) foi substituída. A regra geral de queda/finalização das outras espécies não mudou.

**Clipe próprio `Hab_MordidaFlanco`** (`habilidades/clipes_finalizacao.py`, `LOBO_FINAL=1`):
- **Fonte:** `rig18/_rigreto.blend`. Validação: a `Mordida` regenerada no mesmo rig é igual à aprovada (diferença 0,00001).
- **Saída:** blend `rig18/Lobo_Ancestral_Anim_Finalizacao.blend`; JSON em `habilidades/clipes_fin/`; pacote `studio/dados/Hab_MordidaFlanco.txt` (15.963 bytes).
- **Quadro a quadro** (2,6 s):

  | Tempo | Ação |
  |---|---|
  | 0–0,42 s | entrada: peito desce, dianteiras abrem e firmam, pescoço desce, boca abre |
  | 0,50 s (`Contato`) | fecha a boca |
  | 0,62–1,80 s | 3 sacudidas curtas da cabeça (torção no eixo do focinho ±12°, pescoço acompanha), com peso para trás; ombros absorvem (peito/coluna −1,5°), orelhas para trás, cauda reage pouco |
  | 1,85 s (`Solta`) | solta |
  | 2,6 s | repouso |

- **Ajuste do pescoço:** `cara_no_chao` com o queixo a 0,55 (o mesmo mecanismo do Comer aprovado).
- **Corte 1 recusado na conferência:** focinho a 1,68 de altura (acima do flanco, sem tocar) e deriva da boca de 0,64.
- **Conferência no Blender** (`habilidades/qa_mordida_flanco.py`, com um 2º lobo deitado de lado):
  - focinho no contato a 0,48 de altura; flanco do alvo vai de 0,05 a 1,28;
  - boca a 0,15–0,39 do corpo durante a mordida;
  - deriva da boca 0,25;
  - deriva das 4 patas 0,0; IK 0,0003.
  - Renders de cima, rasante, lado e três quartos em `review/fin_r2/`.
- **No Studio:** focinho 5,06 à frente do pivô no contato (0,74 de altura); deriva ≤ 0,1 nas sacudidas; patas fixas.

**Lógica** (`LoboKit_Servidor` / `LoboIA` / `ConfigKitLobo.Controle.estilo`):
- **Ponto da mordida:**
  - meio do tronco (Pelve–Peito) + raio do tronco (1,3 × escala) para o lado da barriga, onde estão as patas;
  - deitado sobre o peito (patas sob o corpo), o lado onde o lobo já está;
  - lado com parede, sem chão ou fora do território: tenta o outro; nenhum livre: cancela com motivo.
- **Caminho:**
  - vai direto, trotando;
  - do outro lado do corpo, contorna além da cabeça ou da cauda reais (pontas medidas nos ossos);
  - na finalização, a cápsula do caído (calculada como se ele estivesse em pé) aceita sobreposição até −1,2, porque a barriga real fica dentro dela.
- **Encaixe durante o rosnado** (0,9 s): ≤ 1,5 studs e ≤ 135°.
  - O cone passa a valer depois do encaixe.
  - Se estiver de costas (> 135°) e houver tempo, vira no lugar com o clipe `VirarE/D` (com passos).
- **Contato:**
  - no `Contato`, o focinho precisa estar a ≤ 0,9 da superfície do **tronco**; senão cancela ("sem encaixe");
  - durante as sacudidas, ≤ 1,3; senão cancela ("perdeu o contato");
  - o alvo não é movido (`MordidoPor` só sinaliza);
  - a queda é prolongada enquanto ele morde.
- **Cancelamentos** (soltam sem dano tardio): lobo ferido, lobo interrompido, alvo levantou, protegido, removido, sem linha de visão, fora do alcance/cone.
- **Desfechos inalterados:** selvagem morre; criatura de jogador é retirada.
- **[A TESTAR]:** alvo já enfraquecido (Vida ≤ 35%) leva **+2,5 s** para levantar (queda de 5,5 s no médio). Com 3,0 s a abordagem pelo flanco não cabia.

**Matriz** (Play no Studio, PC; lobos do kit):

| Caso | Resultado | Situação |
|---|---|---|
| F1 finalização natural (luta comum) | mordeu o flanco; boca→barriga 0,06–0,19; alvo moveu 0,00; patas ≤ 0,002 | funciona |
| F2 caído virado (outro lado) | mordeu (−0,10 a 0,03); alvo 0,00; patas ≤ 0,002 | funciona |
| F3 alvo pequeno (escala 0,65) | mordeu (−0,15 a −0,03) | funciona |
| F4 alvo grande (escala 1,35) | natural: poupou (alvo recuando); forçado: abandonou ("não chega antes de levantar", a 5,6) | **falha** (abordagem lenta) |
| Barriga para o chão (deitado sobre o peito) | detectado; usa o flanco do lado do lobo | funciona |
| F5 parede no flanco do lobo | detectou ("lado da barriga: parede") e foi ao outro; abandonou por tempo | parcial |
| F6 paredes nos dois flancos | "nenhum flanco livre" e cancelou | funciona |
| F7 interrupção (lobo ferido) | soltou, sem dano; caído levantou | funciona |
| F8 alvo levanta durante a mordida | "alvo levantou (durante a mordida)", sem dano | funciona |
| F9 criatura de jogador simulada | RETIRADA, Vida 140 mantida | funciona |
| Caso focinho com focinho, queda logo diante da cabeça | antes da r9: abandonava sempre; depois, F1 concluiu | funciona com o encaixe de 135° |
| Duelo de regressão 45 s | **1 acerto em 7** tentativas (v81: 2 em 8); 2 erros logo após esquiva | sem melhora |
| Celular / multiplayer / PvP real / refúgio real | — | não testado |

**Diferenças para a referência:**
- A referência é um retrato do lobo em pé, sem a ação; a comparação serve para proporção e postura.
- Na mordida o lobo baixa o peito com as dianteiras abertas; a silhueta se mantém (crina, cauda baixa).
- Não há efeito visual (sem sangue nem partículas), por escolha.

**Evidências** (`studio/review/`):
- `Lobo_finalizacao_flanco_v81_x_correcao.mp4`: lado a lado alinhado na queda, trecho lento (0,4×), interrupção, vistas do Blender e cartão de medições;
- `mordida_flanco_prancha.jpg`;
- `mordida_flanco_referencia_x_studio.jpg`;
- conferência do Blender: `review/fin_r2/` e `habilidades/log_qa_fin_r2*.txt`.

**Checksums instalados = locais:**
- servidor 360861230;
- IA 661571352;
- config 725406791;
- clipe 746336459.

**Backup:** `ServerStorage.Backup_KitLobo_v81_2026-11-20`.

**Limites:**
- O encaixe gira até 135° no rosnado e as patas deslizam nesse giro (falta um clipe curto de giro no lugar).
- Alvo grande e caminho longo (parede) não chegam a tempo.
- Ritmo do duelo pendente.
- Desempenho:
  - +1 clipe de 16 KB;
  - cálculo de flanco só na decisão;
  - durante a mordida, uma distância por quadro (≤ 1,4 s);
  - celular não medido.

## Queda lateral para a finalização (20/11, place v99; aguardando avaliação)
Pedido do usuário (`DOCS/pedidos/2026-11-20-lobo-ancestral-queda-lateral-finalizacao.md`): o lobo derrubado caía em Impacto → Deitado (sobre o peito), e a mordida na barriga não convencia. Agora ele tomba **de lado**, com o flanco e parte da barriga para cima, como um canídeo derrubado. A regra de queda (chances, durações, PvP, intervalo de 4 s) **não mudou**.

**Clipes próprios** (`habilidades/clipes_queda_lateral.py`, `LOBO_QUEDA=1`; os clipes de descanso Deitar/Deitado/LevantarDeitado não são mais usados na queda):

| Clipe | Duração | O que faz |
|---|---|---|
| `QuedaLadoE` / `QuedaLadoD` | 1,1 s | tropeço (0,18) → as patas de baixo cedem e o tronco rola (0,52) → ombro e quadril tocam o chão (0,78) → pequeno quique (0,90) → cabeça e cauda pousam por último (1,1) |
| `CaidoLadoE` / `CaidoLadoD` | 4,0 s (laço) | de lado (rolagem 80°), patas relaxadas para o lado da barriga (as de cima sobre as de baixo), bochecha e cauda no chão, olhos semicerrados, respiração discreta |
| `LevantarLadoE` / `LevantarLadoD` | 1,9 s (no jogo 1,27 s, `levantarVel` 1,5) | patas sob o corpo (0,45) → rola para o peito (0,95) → apoia as quatro (1,25) → agachado (1,55) → de pé (1,9); a altura só sobe depois que começa a rolar (sem "quique") |
| `Hab_MordidaFlancoLado` | 2,6 s | mesma mordida do `Hab_MordidaFlanco` aprovado (mesmo ritmo, marcadores e sacudidas da própria cabeça), com o queixo a 1,30 (meio da barriga lateral) e menos agachamento. O clipe aprovado continua igual (JSON idêntico) e é usado quando o alvo não está de lado |

**Conferência no Blender** (`habilidades/render_queda.py`, `habilidades/qa_mordida_flanco_lateral.py`; folhas em `review/queda_r3/` e `review/fin_lateral_r1/`):
- IK ≤ 0,063; patas sem flutuar (bola a 0,14 do lado de baixo e 0,62 por cima da outra pata).
- Malha fora das patas: queda e caído −0,17 (pelo da pata comprimido); levantar −0,37 (almofada da mão ao apoiar).
- A cauda enterrava até 0,95 entre as chaves. A r3 resolve a cauda osso a osso nos dois eixos (com o tronco rolado, X vira lateral e Z vira vertical), cria uma trilha própria da cauda a cada 1/7,5 s e devolve a cauda de pé nas emendas. Pior pelo da cauda agora −0,15.
- O quadril e o ombro de baixo atravessavam 0,9 ao rolar para o peito. Agora a raiz sobe o necessário entre as chaves, suavizado.
- Mordida lateral contra `CaidoLado` (os dois lados):
  - boca a 0,14–0,34 da pele do tronco;
  - posição 0,49–0,54 entre peito e pelve (meio da barriga, não o pescoço nem o chão);
  - pernas do alvo a ≥ 0,115 da boca;
  - deriva da boca 0,25; patas do atacante 0,0.

**Lógica** (`LoboKit_Servidor` / `LoboIA` / `ConfigKitLobo.Controle`):
- **Lado da queda (`K.escolherLadoQueda`):**
  - Preferido: cair para longe do golpe, com a barriga voltada para quem bateu.
  - Na escala do alvo, confere o espaço das pernas (4,0) do lado da barriga e das costas (1,8) do lado oposto: paredes e corpos por raio horizontal; chão e desnível (> 1,6) por raio para baixo.
  - Bloqueado: o outro lado. Nenhum livre: o de mais espaço, com `LIMITACAO` no log.
  - Atributo `CaidoLado` = "E" ou "D". Uma nova queda antes de levantar mantém o lado e só prolonga, sem repetir o tombo.
  - `barrigaE = 1`: caído sobre E, a barriga aponta para +RightVector do modelo (medido no Studio).
- **Tronco para a mordida (`K.troncoAlvo`):**
  - Deitado de lado, a coluna fica na borda de cima. A cápsula vai para o centro real do tronco: 0,156 × (Peito–Pelve) para o lado das patas, com raio 0,272 × (Peito–Pelve). As frações foram medidas no Blender, então valem para qualquer escala.
  - Em pé, ou deitado sobre o peito: igual à v91.
- **IA:**
  - Com o alvo de lado, a barriga fica a 0,43 × (Peito–Pelve) da coluna, do lado das patas.
  - As costas são recusadas ("costas (deitado de lado...)").
  - O focinho para a 5,46 do pivô (clipe lateral) [A TESTAR].
  - O contorno pela cabeça ou cauda usa o raio real.
- **Desfecho selvagem:** fica `CaidoLado` parado (velocidade 0). Criatura de jogador: retirada, como antes.
- **Correção junto:** o levantar terminava na hora quando a faixa recém-carregada tinha `Length` 0. Agora a duração vem do clipe (quadros/fps).

**Matriz** (Play no Studio, PC; lobos do kit, clone selvagem como alvo, IA estratégica atacando):

| Caso | Resultado | Situação |
|---|---|---|
| Lado da queda: atacante a +X / −X | cai sobre E / D; barriga para o atacante (cos 0,94 durante todo o caído) | funciona |
| F1 lado E | finalizou; boca→barriga 0,14–0,36; alvo moveu 0,00 | funciona |
| F2 lado D | finalizou; 0,08–0,11; alvo 0,00 | funciona |
| F3 porte pequeno (escala 0,65) | finalizou; 0,44–0,52 (boca um pouco alta para o alvo pequeno) | funciona |
| F4 porte grande (escala 1,35) | finalizou; 0,08–0,17 (na v91 abandonava por tempo) | funciona |
| F5 parede do lado das pernas | caiu para o outro lado ("pernas batem em QL_Parede"); a IA contornou e finalizou (0,08–0,11) | funciona |
| Degrau de 2,5 do lado da barriga | caiu para o outro lado | funciona |
| Paredes dos dois lados / borda de plataforma | `LIMITACAO: nenhum lado livre` → lado de mais espaço (o corpo pode encostar na parede ou passar da borda) | limitação registrada |
| F7 lobo ferido durante a mordida | soltou, sem dano; o alvo levantou | funciona |
| F8 alvo levanta durante a mordida | cancelou, sem dano | funciona |
| F9 criatura de jogador | `RetiradaDeCombate` + `Incapacitado`, Vida mantida | funciona |
| F10 alvo forte (72%) | APROVEITA, sem finalizar | funciona |
| Poupar (outro inimigo a < 25) | Vigiar; retoma quando o alvo levanta | funciona |
| Nova queda com o alvo já caído | mantém o lado, só prolonga | funciona (corrigido no teste) |
| PvP (alvo de outro dono) | queda de 1,5 s (metade), como antes | inalterado |
| Celular / multiplayer / terreno inclinado de verdade / refúgio real | — | não testado |

**Diferenças para a referência:** a referência é o lobo em pé. A comparação (`studio/review/queda_lateral_referencia_x_blender_x_studio.jpg`) serve para proporção, crina, cauda e cores; a pose caída é própria.

**Evidências** (`studio/review/`):
- `Lobo_queda_lateral_finalizacao.mp4`, 59 s: queda E e D em tempo real e lenta, levantar, mordida na barriga dos dois lados, vista rasante, folhas do Blender, prancha e cartão de resultados.
- Folhas do Blender em `review/queda_r3/` e `review/fin_lateral_r1/`; logs `habilidades/log_clipes_queda.txt` e `log_qa_fin_lateral_*.txt`.

**Checksums instalados = locais:**

| Item | Hash |
|---|---|
| servidor | 816707368 |
| IA | 184618218 |
| config | 11223891 |
| cliente | 27766693 (inalterado) |
| QuedaLadoE | 428997739 |
| CaidoLadoE | 903944130 |
| LevantarLadoE | 373411009 |
| QuedaLadoD | 546714798 |
| CaidoLadoD | 27917410 |
| LevantarLadoD | 470988846 |
| Hab_MordidaFlancoLado | 576376045 |
| Hab_MordidaFlanco | 746336459 (inalterado) |

Dados: 55 → 62 clipes. Backup: `ServerStorage.Backup_KitLobo_v91_2026-11-20`.

**Limites:**
- O clipe é plano: em encosta real o corpo deitado não acompanha o terreno (só conferimos desnível e chão nos dois lados).
- Com paredes dos dois lados, ou na borda, usa o lado de mais espaço e pode encostar.
- No alvo pequeno a boca fica 0,4–0,5 acima da barriga (dentro do limite de 0,9).
- O pelo da almofada afunda até 0,37 num instante do levantar.
- O focinho a 5,46 está [A TESTAR].
- Duelo de regressão não refeito (lógica de golpes inalterada).
- Desempenho: +7 clipes (~96 KB). A escolha de lado faz 4 a 6 raios só no momento da queda. Celular não medido.

### r4: patas mais separadas ao cair (20/11, place v102; aguardando avaliação)
Pedido do usuário: "Separe mais as patas ao cair". Só os 6 clipes de queda mudaram. `Hab_MordidaFlancoLado`, kit, IA e config ficaram iguais (hashes conferidos).
- **Caído** (`_pes_laterais` em `habilidades/clipes_queda_lateral.py`):
  - As mãos vão para a frente e os pés para trás (`LOBO_Q_ABRE_Y` 0,80).
  - O par de cima vai ainda mais longe que o de baixo (`LOBO_Q_TESOURA` 0,60) e desce para 0,42 (`LOBO_Q_PE_CIMA_AB`), sem ficar empilhado.
  - As traseiras abrem 55% disso (`LOBO_Q_TRAS`); com 100%, o jarrete não alcançava e o IK errava 0,15.
  - A perna **gira** em vez de esticar: o alcance relaxado é mantido.
  - Distância entre mão e pé: de 4,9 para 5,7 (par de baixo) e 6,5 (par de cima).
- **Queda:** as patas de baixo cedem menos para baixo do corpo (0,85 → 0,50) e o apoio abre no tropeço.
- **Blender:**
  - IK ≤ 0,026 (r3: 0,063).
  - Malha fora das patas: −0,19 no caído e na queda, −0,37 no levantar (igual à r3).
  - A métrica `patas_dist` mede 0,003 no levantar porque compara o X das patas E/D, que ficam empilhadas de lado; as patas estão separadas em Y/Z.
  - Folha: `review/queda_r4/folha_patas_r3_x_r4.jpg`.
- **Studio** (Play, PC):
  - Lado E: finalizou, boca→barriga −0,08 a −0,05, alvo moveu 0,00.
  - Lado D: finalizou, −0,03 a −0,01, alvo 0,00.
  - Queda sem atacante, vista da barriga: patas abertas, levanta sem salto de pose (`studio/review/queda_lateral_r4_patas_studio.jpg`, `queda_lateral_r4_finalizacao_D_studio.jpg`).
- **Atenção:**
  - Numa tentativa do lado D, a IA abandonou a finalização ("silhueta entraria em Lobo_Clone", ficou de costas e não chegou a tempo). A repetição finalizou normalmente. Causa não isolada; pode ser o atacante colado no alvo no início.
  - Nesta rodada a boca entra 0,01–0,08 na cápsula da barriga (na r3 ficava 0,08–0,36 fora).
  - Porte pequeno/grande, parede, poupar e PvP não foram refeitos: a lógica não mudou, só os clipes.
- **Backup:** os clipes r3 estão em `ServerStorage.Backup_QuedaLado_r3_2026-11-20` e localmente em `habilidades/clipes_queda_r3/` e `habilidades/clipes_queda_lateral_r3.py`.
- **Captura:** com StreamingEnabled, os lobos de teste só aparecem no cliente com `ReplicationFocus` numa peça na cena (o personagem estava longe).

## Evidências (`BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/review/`)
- `Lobo_IA_estrategica_ensaios.mp4` (3 min 43 s, tempo real, captura do Play com painel de plano, vida e energia):
  - ensaios 1–4;
  - ensaios 5–8, gravados antes da correção do degrau;
  - ensaio 9.
- `ia_ensaios_prancha.jpg`.
- `ia_lobo_referencia_x_studio.jpg`: referência × Lobo no Studio.
