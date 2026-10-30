# Dragão: IA, combate elemental e montaria (até 29/10)

Voltar ao índice: [[PROJECT-STATE]]

## IA selvagem e territorial do Dragão das Montanhas (2026-10-28/29) — ambiente de teste
**Onde:** `Teste-animacoes.rbxl` (place de teste aberto pelo usuário). O mapa e o place principal não foram tocados; no principal houve só leitura.
- Ninhos reais do mapa não testados: o place principal só tem pastas de território e os ninhos estão inativos.
- Laboratório de relevo `Laboratorio_IA`: pico com ninho no topo, caverna com túnel/câmara e ninho, lago, carcaça de teste, poleiro, rochas de observação e dois invasores de teste com a tag `Invasor_Teste`. Recriável por `V14/ia/montar_laboratorio.luau`.

**Código** (`V14/ia/`, instalado em `ServerScriptService.IA_Dragao` + script `IA_Dragao_Servidor`):
- `Config` (valores de calibração, não oficiais).
- `Territorio`:
  - registro um ninho = um guardião (segunda atribuição dá erro — testado);
  - ProximityPrompt de coleta: o início da coleta sempre alerta; a conclusão é validada no servidor e trava antes de qualquer yield;
  - ovo marcado Coletado, ninho Ativo=false, evento `OvoColetado`;
  - nenhum RemoteEvent.
- `Locomotor`:
  - PivotTo casado com os clipes (andar 4,8 / correr ~17 / voo 34 / voo rápido 55 studs/s; giros por clipe);
  - chão por raycast medido a partir do corpo (funciona sob teto), inclinação pela rampa, bloqueio por parede/rampa;
  - Pathfinding com alternativa em linha reta checada;
  - voo com Decolagem/Voo/Voo_Rapido/Planeio/Subida/Descida/Curva_Aerea/Pouso, altitude pelo relevo e desvio por spherecast;
  - não voa sem céu livre; pousa no último ponto de céu livre antes de cavernas.
- `Cerebro`:
  - 21 estados com prioridade: Idle, Observation, Wander, Patrol, Fly, Glide, SearchFood, Eat, SearchWater, Drink, Rest, Sleep, ReturnHome, Investigate*, Alert, ReturnToNest, DefendNest, ChaseIntruder, Attack, Recover, Incapacitated (*Investigate está declarado mas sem tarefa própria);
  - cada tarefa tem geração própria (a defesa cancela qualquer rotina na hora);
  - tempo mínimo por estado e pausa "Idle" quando a tarefa falha cedo (anti-alternância);
  - percepção a cada 0,25 s com jogadores perto e 1 s sem;
  - depuração por `ServerStorage.IA_Debug` (BindableFunction, só servidor).

**Testes no Play (todos com sucesso, salvo a nota):**
1. Dormindo no ninho + jogador **furtivo**: a 180 studs nada (raio furtivo 138); a 120 → Alert; a 60 → DefendNest.
2. Voando a 266 studs do ninho + invasor no pico → ReturnToNest voando → DefendNest em **6,2 s**.
3. Coleta: início alerta; 1ª coleta ok, **2ª recusada** ("indisponivel"); ovo Coletado, ninho inativo.
4. Fuga do coletor → ChaseIntruder → perseguição encerrada no limite (fugitivo a 464 do ninho, limite 330) → Recover. O ovo ausente não é tratado como presente (Recover usa Observação em vez de inspeção).
5. **Caverna**: voo até a entrada, pouso, entrada a pé pelo túnel e defesa (26 s a partir de ~480 studs). Com 2 invasores, priorizou o da zona crítica; ataques a cada 3 s.
6. Invasores somem → Recover → rotina (Wander/Patrol/Idle).
7. Sede alta dentro da caverna → sai a pé pela entrada, voa ~900 studs até o lago, pousa na margem e bebe; a sede zera.
8. Incapacitado em pleno voo → pouso de emergência e deita; ao recuperar → Recover.
9. Desempenho: servidor 60 Hz (pior quadro 18–19 ms) com 2 guardiões ativos; um 3º guardião para o mesmo ninho foi recusado.

**Defeitos achados e corrigidos durante os testes:**
- tarefa cancelada sobrescrevendo o estado;
- caverna: voava até a entrada sem pousar e tentava andar no ar (loop "sem caminho"); depois, falha de pathfinding no túnel; depois, leitura de chão acertando o topo da montanha;
- laboratório além da borda do Baseplate (sem chão na boca do túnel);
- alternância rápida de tarefas dentro da caverna;
- altura inicial errada quando o dragão nasce dentro da caverna.

**Pendentes:**
- **Combate**: não há sistema de dano nem clipes de ataque (Fase 4 não feita). "Attack" dispara `IA_Eventos.AtaqueSolicitado` + intimidação.
- Integração do ovo com inventário/incubadora: só o evento `OvoColetado`. Reaparecimento dos ninhos (30–60 min, oficial) não implementado.
- Regra de incapacitação do guardião selvagem: [PENDENTE] no documento; aqui ele só deita até o atributo ser limpo.
- Testes no mapa real das Montanhas Altas (ninhos do pico central e das cavernas reais) não feitos.
- StreamingEnabled: o modelo do dragão não chega ao cliente longe do jogador. No teste foi usado ModelStreamingMode=Persistent; definir a estratégia para o jogo.
- Voo montado não feito. Raios e velocidades a calibrar.
- O place de teste precisa ser salvo (Ctrl+S).

## Combate elemental do Dragão das Montanhas (2026-10-29) — PROTÓTIPO em Teste-animacoes.rbxl
**Regras oficiais seguidas (Doc 02):**
- 4 habilidades: Sopro, Arremetida, Tempestade de Asas, Domínio.
- Montanhas = Fogo/Terra/Raio/Ar; 1 elemento nato + até 2 desbloqueados (o 4º é recusado — testado).
- Recarga compartilhada por habilidade: trocar de elemento não reinicia — testado.
- Domínio é um amplificador temporário; o multiplicador ficou em 1,0 porque nenhuma vantagem mecânica foi aprovada.
- Dano, energia, recargas e alcances estão no documento como [PENDENTE]. Todos os números de `ConfigCombate` estão marcados `NAO_APROVADO`.
- Sem paralisia, empurrão, atordoamento, fusões ou dano no rugido.

**Animações (Blender, `v14_fase4.py`):** 11 clipes com marcadores de acerto:
- Ataque_Mordida, Ataque_Garra_E/D, Ataque_Cauda, Rugido_Combate;
- Sopro_Inicio/Loop/Fim, Arremetida, Tempestade_Asas, Dominio.
- Variantes "_Camada" (só tórax, pescoço, cabeça e mandíbula, Pose.Weight 0 no resto) para usar em voo — verificado: o corpo segue no clipe de Voo.
- Prévias: `V14/anim/fase4/previas/prancha4.png`.

**Código** (`V14/combate/`):
- Servidor `ServerScriptService.Combate_Dragao` (ConfigCombate, Nucleo) e `Combate_Dragao_Servidor`:
  - validação (elemento, energia, recarga, ocupado, incapacitado) e acerto calculado no servidor;
  - cone, projétil, descarga e esfera, com linha de visão pelo terreno, no instante dos marcadores (com tempo de reserva);
  - dano por `Humanoid:TakeDamage`; dragão de jogador só fere jogadores com `Workspace.PvPAtivo`, nunca o dono.
- Cliente `ReplicatedStorage.Combate_Dragoes.VFXCombate` + `VFXCombate_Cliente`, efeitos por elemento:
  - Fogo: chamas, fumaça, brasas e luz;
  - Terra: rochas com rastro, poeira, detritos, rachaduras temporárias em peças (o Terrain não é alterado) e onda de choque;
  - Raio: arco ramificado contínuo de brilho constante, sem estroboscopia, mais clarão único no impacto;
  - Ar: vórtice, anéis de pressão orientados e poeira.
  - Também: rastro e impacto da Arremetida; anel e partículas da Tempestade; aura do Domínio (fissuras mais acesas, arcos espaçados, poeira mineral, vento); reação do alvo com Highlight e tremor curto só para quem foi atingido.
  - LOD por distância e nível gráfico, no máximo 6 luzes, emissores do sopro reaproveitados.
- Integração com a IA: `AtaqueSolicitado` → escolha automática:
  - Domínio no início do confronto, Tempestade contra grupos;
  - mordida/garra se ao alcance da boca; cauda atrás; sopro a média distância; arremetida a longa.

**Testes no Play (todos com sucesso):**
- Os 4 sopros, de perto e em voo, com captura de cada um (`V14/combate/capturas/`).
- Tempestade (Fogo) e Domínio (Raio).
- Arremetida: 85 studs, alvos atingidos uma vez cada, para diante de terreno. Mergulho em voo: altura 46 → 14.
- Cauda acerta só atrás; mordida não acerta alvo fora do alcance da boca.
- Segurança via RemoteEvent `Pedido`: pedido de quem não é dono, habilidade inventada com "dano" forjado, elemento proibido e instância falsa foram todos ignorados.
- 3 dragões com Tempestade e Sopro simultâneos: servidor a 60 Hz (pior quadro 19 ms); cliente 59,8 FPS medido logo depois (não durante).
- IA defendendo o ninho do pico contra o jogador: Domínio → garras acertando (−14 cada).

**Defeitos corrigidos nesta etapa:**
- direção do sopro (saía para cima);
- arco de raio invisível (era curto demais);
- Ar fraco e anéis deitados;
- IA voando até o ninho no pico chegava abaixo do topo e pousava DENTRO da montanha (agora só chega acima do relevo e sobe a 24 studs/s);
- invasor ficava embaixo do peito, fora do alcance (agora o dragão se posiciona com a boca para o invasor).

**Pendentes:**
- Aprovação de todos os números.
- Sem sons: não há áudio licenciado; os pontos de sincronia existem.
- A aura do Domínio de Raio ficou discreta demais na captura.
- Reação animada dos alvos (só destaque visual); defesa/esquiva não existem (não há sistema).
- Combate com vários jogadores reais não testado (só NPCs e um jogador).
- Arremetida aérea sem clipe próprio de mergulho (usa a camada).
- Fusões não implementadas (pendentes).
- **Salvar o Teste-animacoes.rbxl.**

## Atualização oficial do Dragão das Montanhas + fogo realista + montaria (2026-10-29) — PROTÓTIPO em Teste-animacoes.rbxl
### 1. Atualização oficial (autorizada pelo usuário)
- Montanhas = **Fogo/Terra/Ar** (Raio removido só desta forma; `elementosGlobais` mantém Raio).
- Habilidades: **Sopro, Arremetida, Tempestade, Ruptura Vulcânica**. O Domínio saiu da forma; o código fica para outras formas.
- Bloqueio por forma: `temHabilidade`/`habilidadesForma`.
- `elementos()` filtra pela forma antes do limite de 3.
- **Migração não destrutiva** (`auditarDados`):
  - Raio/Domínio antigos ficam inativos, sem apagar nem converter, e são marcados em `MigracaoPendente`;
  - nenhum elemento é concedido;
  - um nascido com Raio fica sem Sopro, mas com Ruptura.
- Não existem dados salvos de criaturas no projeto (sem DataStore): migração real pendente quando o salvamento existir.
- **Animação `Ruptura_Vulcanica`** (`v14_fase4.py`, 3,6 s):
  - marcadores RupturePrepare 0,0 / RuptureImpact 1,4 / RuptureEruption 1,65 / RuptureEnd 3,4;
  - importada em `ReplicatedStorage.Animacoes_Dragao_V14`;
  - as demais animações não foram alteradas.
  - Obs.: o `Dragao_V14_Anim_Fase4.blend` e o `relatorio_fase4.json` foram regenerados só com este clipe; os JSON dos outros clipes continuam intactos.
- **Servidor (`Nucleo._Ruptura`)**:
  - exige solo: atributo NoAr falso, raycast sob as patas dianteiras e apoio traseiro;
  - onda de choque de raio 22 no impacto; pilares em 3 anéis (18/30/42) num leque de 240° à frente;
  - os pilares saem 0,25 s após o golpe (janela de esquiva) e cada alvo é atingido 1 vez por uso;
  - reação de lançamento: o servidor aplica nos NPCs; nos jogadores, só o cliente do atingido;
  - pilares só em solo firme (normal > 0,8, ±9 do nível) e a mais de 16 studs do ovo;
  - zonas seguras: tag `ZonaSegura` (vale para todo o combate).
- **IA**: usa a Ruptura com alvo no leque, no solo e com no mínimo 1,6× a recarga entre usos.
- Valores de dano, recarga, energia e lançamento: todos NAO_APROVADO.

### 2. Fogo e projéteis realistas
- Flipbooks próprios (`V14/vfx/gerar_flipbooks.py`, 8×8, sem licença de terceiros) enviados ao Roblox:
  - fogo `rbxassetid://81072138040568`;
  - fumaça `rbxassetid://114973539727313`;
  - lava `rbxassetid://76516973198217`.
- **Sopro de Fogo**: labareda com cor embutida, jato quente na boca, fumaça escura que recebe luz e brasas.
- **Projétil de Terra**: rocha de magma (CrackedLava + cascas de basalto) em arco, com rastro de calor, fumaça e respingos.
- **Impacto de Terra**: lava, lascas de basalto e fissuras que esfriam (sem cubos/linhas retas).
- **Pilares da Ruptura**: lascas de basalto inclinadas, núcleo de magma, pico quebrado de cunhas e estilhaços (sem cilindro/bloco único); depois afundam e viram poeira.
- Tremor de câmera moderado, que diminui com a distância (160 studs).

### 3. Montaria (`V14/montaria/`)
**Arquivos instalados:**
- `Montaria_Dragao_Servidor` (SSS);
- `Montaria_Dragoes.ConfigMontaria` (RS);
- `Montaria_Cliente` (StarterPlayerScripts);
- `Teste_Montaria_Dono` (SSS, **só teste**: dá a posse do `Dragao_Montanhas_Jogador`, cópia de teste do V14 com Estagio=Adulto e nato Terra).

**Servidor (autoritativo):**
- O cliente envia só a intenção (UnreliableRemoteEvent, ~15 Hz, valores limitados).
- Reaproveita o `Locomotor` e o `EstadosDragao` (que ganhou `PastaAnimacoes`).
- Validações: dono, estágio (ovo/bebê/jovem não montam; pré-adulto só no chão), missão `VooDesbloqueado`, guardião nunca, um controlador por dragão.

**Ciclo da montaria:**
- Subida: Montaria_Abaixar → arco do personagem → Weld na sela (pose de repouso do osso Coluna2) → Levantar.
- Chão: aceleração e freio graduais, Correr_Frenagem, giro no lugar (Giro_E/D), A/D ou câmera, rampa/parede bloqueiam.
- Voo:
  - rumo pela câmera com taxa limitada (42°/s, 28°/s em velocidade alta) e inclinação até 32°;
  - subir e descer, clipes Voo/Voo_Rapido/Curva_Aerea/Subida/Descida;
  - planeio com perda de altura e velocidade;
  - sobe sozinho diante de parede, com folga do relevo.
- Pouso: exige chão firme e livre (spherecast), clipe Pouso.
- Desmontar: só no chão e parado, em local livre (GetPartBoundsInBox).
- Desconexão ou morte no ar: o dragão plana e pousa sozinho antes de liberar.
- Incapacitado: bloqueia habilidades, plana, pousa e trava o movimento.

**Cliente:**
- Teclas: WASD, Shift correr, Espaço decolar/subir, Ctrl descer, G planar, F pousar, X desmontar, 1–4 habilidades, Z elemento.
- Também: gamepad e botões de toque (ContextActionService).
- Câmera com alvo suavizado no pivô (as asas não sacodem a imagem), zoom 40–140 e FOV que abre com a velocidade.
- HUD: estado, voo liberado/bloqueado, elemento, energia, recargas (atributos `RecargaFim_*`) e avisos.
- O cavaleiro segue o osso do dorso no visual de todos os clientes.

### Testes no Play (sucesso)
- Elementos: nascidos Fogo/Terra/Ar; desbloqueio progressivo até 3; Raio ignorado; nato Raio sem Sopro.
- Ruptura:
  - recusada no ar (montado);
  - Domínio recusado (“não pertence à forma”);
  - dano −24 só nos alvos próximos, 1 vez cada; alvo a 71 e alvo atrás intactos.
- IA no ninho:
  - Ruptura usada e repetida só após 25,8 s;
  - garras/mordida entre os usos;
  - nenhum pilar sobre o ovo.
- Montaria, recusas: guardião, outro dono, ovo/bebê/jovem, longe demais, voo sem missão, desmontar no ar.
- Montaria, movimento:
  - teclado real: W/Shift a 17 studs/s, Espaço decolou, Sopro no ar com HUD de recarga, F pousou, Ruptura montado, X desmontou;
  - câmera e HUD restaurados após desmontar;
  - encosta: a pé parou na rampa; em voo subiu com folga ≥ 13.
- Falhas simuladas:
  - desconexão a 82 de altura → pousou e liberou em 7,6 s;
  - incapacitação a 70 → pousou em 6,6 s, habilidades bloqueadas.
- Desempenho:
  - voo rápido montado: servidor 60 Hz (pior quadro 18 ms), cliente 60 FPS (pior 19 ms);
  - durante a Ruptura: cliente 60 FPS, até 300 objetos de VFX.

**Bug corrigido (IA):** `Locomotor._girarPara` com direção nula gerava NaN e jogava o guardião a y = −1e6. A causa era a regra “chegar acima do relevo” quando o dragão ficava exatamente sobre o destino.

### Pendentes
- Números de combate e de montaria (NAO_APROVADO).
- ProximityPrompt “Montar” (tecla E): a tecla simulada pela ferramenta não acionou; a montagem foi testada pelo mesmo evento do servidor. **Testar o E manualmente.**
- Não testado: multijogador real (Team Test com 2+ clientes / observadores), celular/gamepad reais.
- Ausentes:
  - sons (sem áudio licenciado);
  - animação própria do personagem subindo (usa arco + sentar);
  - Raio para outras espécies (Glacial/Sombrio sem documento/modelo);
  - DataStore de criaturas.
- Desempenho no servidor: o `filtroMundo`/`alvosValidos` percorre o Workspace (aceitável no laboratório; otimizar no mapa principal).
- **Salvar o Teste-animacoes.rbxl (Ctrl+S).**

## Correção crítica + refinamento (2026-10-29, sessão 2) — Teste-animacoes.rbxl
### Fase 1 — Montaria travada (CAUSA REAL, reproduzida no Play)
- **Causa:** em `passoChao`, a marca `M.bloqueado` só era reavaliada com `vel > 0,3`, mas o bloqueio zerava a velocidade a cada quadro. Depois de qualquer rampa, parede ou "sem chão", o dragão ficava parado para sempre, mesmo virado para o lado livre.
- **Reprodução:** encosta → virar → W por 4 s = vel 0. Depois da correção, o mesmo teste deu vel 4,8.
- **Correção:**
  - o obstáculo passa a ser testado pela INTENÇÃO (sentido pedido) e pelo rumo atual, a cada 0,15 s, mesmo parado;
  - aviso "Caminho bloqueado (motivo)".
- **Retorno ao jogador:** os avisos de recusa ficavam dentro da interface da montaria, que só aparece depois de montar. Agora ficam numa tela sempre ligada.
- **Testes com teclas reais (OK):**
  - montar, andar, correr, curva correndo, frear, girar parado, desmontar;
  - remontar após habilidade e após comportamento automático.
- **Voo de desenvolvimento:**
  - `ServerStorage.ConfigDev_Montaria` (não replica) com `ativo`, `userIds = {4975569556}` e `placeIdsProducao = {114230639394991}`;
  - só vale com `RunService:IsStudio()`;
  - testado: decolou com `VooDesbloqueado = false`; a missão oficial não foi tocada; o HUD mostra "liberado (DEV - teste)".
- **Câmera:** o alvo estava 14 studs acima do pivô, dentro do tronco, e a oclusão colava a câmera no corpo. Agora o alvo fica acima do dorso (42, +14 no ar); distância 70 (45–150).

### Fase 2 — Locomoção
**Corrida:**
- Antes era um "bound": pares de patas juntos (fases 0/0,1 e 0,5/0,6), apoio de 42%, suspensão de 0,9 e gangorra de 3,5–5°.
- Agora é um galope transversal pesado:
  - fases TE 0 / TD 0,2 / DE 0,48 / DD 0,68, apoio 50%, T = 1,1 s;
  - suspensão 0,18, gangorra 1,6–2,4°;
  - ombro 9° e quadril 8° independentes, onda lateral da coluna;
  - cauda como contrapeso, dedos com impulsão no fim do apoio, pé com pico de elevação no início do balanço.
- Prévia comparativa: `V14/combate/capturas_v3/comparacao_correr.png`.

**Andar e derivados** (Andar_Lento/Inicio/Parada, Curvas, Giros):
- ombro 8°, quadril 7°, rolagem 2,2°, cauda 20 e onda lateral;
- elevação das patas 2,0/1,8.

**Voo (9 clipes):**
- `patas_recolhidas` era uma pose fixa. Agora:
  - dianteiras flexionam no impulso de cada batida e traseiras arrastam com atraso;
  - punhos e dedos relaxam e firmam; na curva, o lado interno recolhe mais;
  - cauda com mais amplitude, servindo de leme na curva.
- Planeio: pernas aerodinâmicas com correções lentas, curvatura da membrana variando e pescoço compensando a inclinação.
- Backup dos JSON anteriores em `V14/anim/anterior_2026-10-29/`.

### Fase 3 — Habilidades
**Sopro:**
- Alcance de teste (NAO_APROVADO): Fogo 110 (era 75), Terra 120 (era 95), Ar 95 (era 60).
- Cones: Fogo 12° (era 22°), Ar 18° (era 34°), casados com a largura visual.
- A velocidade das partículas é calculada a partir do alcance do servidor (d = v/arrasto·(1−e^(−arrasto·vida))): o jato termina onde a hitbox termina.
- Fogo:
  - chamas secundárias volumosas;
  - impacto contínuo onde o jato toca o mundo;
  - fissuras do corpo acendem durante o sopro.
- Ar: anéis de pressão até o fim do alcance e poeira no impacto.
- **Teste:** o Fogo causou dano a 100 studs; o Ar alcançou 85.

**Tempestade de Asas (reconstruída):**
- Terrestre (3,4 s): firma/agacha → Impulso (1,1) → o corpo SOBE DE VERDADE (`elevacao` 11; medido 11,6) → Batida única (1,75) → paira → LandingImpact (2,95).
- Aérea: `Tempestade_Asas_Ar` (2,4 s), sem decolagem; a Raiz tem peso 0, então altura e balanço vêm do clipe de voo.
- Dano só no marcador Batida, uma vez por alvo. Teste: NPCs dentro de 78 levaram −16 e os de fora, nada.
- Atributo `CorpoElevado`: montaria e Locomotor não disputam o movimento durante a elevação.
- Efeitos: ar puxado para as asas, poeira e rastros nas pontas das asas no impulso, coluna de ar que desce ao chão, anel translúcido e variantes Fogo/Terra/Ar.

**Ruptura Vulcânica:**
- Antes: leque a partir das patas dianteiras, com pilares sob a cabeça e o pescoço.
- Agora: 360° em volta do CENTRO DO CORPO (anéis 24/36/48).
- Cada posição é rejeitada se:
  - estiver a menos de folga de qualquer segmento osso-pai→filho na pose atual (tronco, pescoço, cabeça, cauda, pernas, asas);
  - cair dentro dos polígonos das membranas;
  - não tiver chão firme (normal > 0,7, ±12 de nível);
  - tiver teto em cima ou parede entre o centro e o pilar;
  - estiver perto de um ovo ou dentro de `EstruturaProtegida`.
- Resultado no atributo `UltimaRuptura`:
  - plano: 16 pilares, 7 rejeitados por corpo;
  - pico do ninho (IA): 8 pilares, 9 por solo, 6 por corpo.

### Fase 4 — Integração (Play)
- Montado:
  - corrida com a câmera nova;
  - voo em curva com o corpo inclinado;
  - Tempestade aérea, pouso com F, desmontar com X.
- IA: comportamento natural (Observation/Wander/Rest), pivô normal; defesa do ninho com Ruptura e garras.
- Desempenho: servidor 60 Hz (pior quadro 19 ms) com os 2 dragões e a Ruptura.

### Pendentes
- **Não testado:**
  - 2 jogadores reais: a ferramenta só abre 1 cliente;
  - qualidade gráfica reduzida;
  - celular.
- **Não feito:**
  - som (sem áudio licenciado);
  - a animação do Sopro em si não foi refeita (só VFX e alcance);
  - o anel da Tempestade ainda é uma peça Neon (melhorar com malha/textura de anel).
- Todos os números continuam NAO_APROVADO.
- **Salvar o place (Ctrl+S).**

