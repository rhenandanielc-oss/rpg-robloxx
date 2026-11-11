# IA dos dragões — duelo de teste entre Glacial e Sombrio

Cole no chat Claude **Dragão Sombrio (Sombra)**, grupo Terras Corrompidas. Decisões do usuário em 11/11/2026.

## Primeira etapa aprovada

Faça um duelo de IA entre Dragão Glacial e Dragão Sombrio no ambiente de teste. Use a montagem existente como ponto de partida. O objetivo é verificar se os dois tomam decisões diferentes e coerentes diante do mesmo adversário, alternando ataque, esquiva, voo, recuo e perseguição conforme a situação. Esta etapa é um teste isolado. A integração da IA ao jogo e a extensão ao Dragão das Montanhas ficam para etapas futuras.

Comece com inspeção somente leitura de CLAUDE.md, DOCS/ORGANIZACAO-CHATS.md, PROJECT-STATE.md e DOCS/estado/dragao-2026-10-30.md (CX, DE e DF, além dos registros mais novos). A seção CX registra duelos simulados com poucos acertos e pouca fuga/perseguição em algumas rodadas. DE/DF registram os testes dos guardiões junto aos ninhos, com correção do filtro de chão do próprio ninho. Não confunda essas evidências com validação de combate entre dragões no jogo.

Use BLENDER/Criaturas/Teste_IA/V14/ia/teste_duelo_tatico.luau ou a versão de teste mais recente confirmada. Inspecione em leitura Cerebro, Locomotor, ConfigCombate e Nucleo para reaproveitar os comportamentos, ataques, estados e clipes já disponíveis. Concentre as mudanças no script de teste e em seus artefatos. Preserve os sistemas compartilhados e as outras criaturas. Use os kits atuais confirmados, com Glacial de Gelo e Sombrio de Sombra. Parâmetros de teste ficam identificados como experimentais.

## Decisões de combate

- **Ritmo.** Aproximação, ameaça quando fizer sentido, ataque, recuperação e reposicionamento. Use a recuperação para dar oportunidade de resposta. Evite rugir antes de cada golpe ou alternar estados sem executar a ação. Mantenha compromisso suficiente para uma manobra produzir efeito, com interrupção diante de ameaça ou obstáculo real.
- **Escolha de golpe.** Considere distância, ângulo, linha de visão, diferença de altura, posição do adversário, recurso disponível e recarga. Exemplo: mordida ou garra quando o adversário está próximo e à frente, cauda se ele entrou pelo flanco ou por trás dentro do alcance, sopro se houver linha livre e distância útil. Em grupo, considere área quando houver alvos agrupados. No 1×1, use área somente quando a posição e o kit justificarem. Use as Marcas conforme as regras atuais do kit, sem exigir uma sequência fixa de habilidades.
- **Voo.** Decole para reposicionar, perseguir ou escapar de terreno ruim. Sopre no ar, faça rasante ou mergulhe somente com trajetória livre e espaço para recuperação. Preserve batidas, inclinação e transições coerentes, com cabeça, tronco e cauda acompanhando o movimento. Se a manobra específica não estiver disponível para aquela forma, use o movimento de voo que já existe e relate a limitação.
- **Esquiva.** Responda a um golpe forte perceptível, considerando tempo de reação, espaço para desvio e intervalo entre esquivas. Um golpe já em andamento pode acertar. Exemplo: ao perceber um sopro sendo preparado, o Sombrio pode sair da linha de tiro se houver espaço lateral. O Glacial pode manter a posição quando uma esquiva o colocaria contra uma parede.
- **Recuo e perseguição.** Quando ferido ou em posição ruim, recue para ganhar espaço e tente voltar se recuperar uma abertura. O rival pode perseguir se ainda tiver visão e espaço. Ao perder visão, investigue o último ponto visto por tempo limitado. Sem reencontro, abandone a perseguição e retome a patrulha. Use limites de teste para impedir fuga, perseguição ou voo em círculos indefinidamente.
- **Seleção de alvo.** Quando houver vários inimigos, priorize quem ameaça o ninho ou oferece maior perigo imediato. Mantenha o alvo por tempo suficiente para executar uma ação, com troca justificada por nova ameaça. No duelo 1×1, registre que a seleção entre vários inimigos não foi exercitada.
- **Dificuldade.** Guardiões variam mais o posicionamento e aproveitam melhor aberturas. A diferença é de decisão. Preserve alcance, recarga e regras de acerto da base usada.
- **Personalidade.** Compartilhe a lógica básica. O **Sombrio** procura flancos e ângulos de emboscada, usa marcas e muda de posição sob pressão. O **Glacial** controla o espaço, segura rotas de aproximação e pune entradas expostas. Exemplo: o Glacial mantém uma faixa útil para seu kit, o Sombrio sai dessa linha antes de voltar por outro ângulo e o Glacial responde à nova posição. O estilo futuro de **Montanhas** será pressão frontal e investidas para abrir espaço.

## Direção aprovada para etapas futuras

- **Rotina selvagem.** Caçar fauna disponível, descansar e patrulhar o ninho. Respeite habitats, trajetos e regras da fauna já definida. A caça depende da fauna existente e fica fora deste duelo.
- **Jogadores e território.** Observar de longe, intimidar quando o jogador avançar, atacar se houver invasão do ninho ou agressão. Perseguir dentro do território. Investigar o último ponto visto se perder o alvo e voltar ao ninho ou à patrulha se a busca falhar ou atingir o limite.
- **Encontro entre selvagens.** Primeiro observar e intimidar. A luta pode começar após agressão ou invasão de território. Para a rodada isolada, use uma provocação inicial explícita e deixe as decisões seguintes a cargo da IA.
- **Domesticados.** Modos de seguir, ficar, defender e atacar o alvo indicado. O duelo é entre selvagens. Os comandos entram em etapa própria.

## Evidência e aceite do duelo

Rode três cenários curtos com condições iniciais diferentes. Use um encontro equilibrado, um adversário em altura diferente e um cenário com um dos dragões ferido que favoreça recuo. Inverta quem começa em desvantagem quando repetir. Mostre ao menos um ciclo legível de ameaça, ataque, recuperação e reposicionamento. Exercite esquiva com tempo de reação, recuo e perseguição com limite, ataque acertado e ataque evitado, e voo com saída segura. Se um comportamento não ocorrer naturalmente, faça um cenário específico para testá-lo e identifique a condição inicial. O vencedor pode variar. O teste não precisa garantir uma sequência de eventos em toda rodada.

Registre fase, motivo de cada decisão relevante, ataques executados, acertos confirmados pelo teste, distância entre corpos, recuperação e obstáculos. Confira sobreposição de malhas, travamento em voo, repetição excessiva de clipes e ataques sem linha de visão. Se vida ou dano forem simulados, diga quais partes são reais e quais foram simuladas. Registre os limites de desempenho em PC e celular, incluindo dispositivos e condições que ficaram sem teste.

Compare a cada etapa visual com os vídeos anteriores de duelo e com as imagens reais BLENDER/Criaturas/Teste_IA/dragao_sombra/ref/ref_sombrio.png e BLENDER/Criaturas/Teste_IA/dragao_gelo/ref/ref_glacial.png. Confira se surgiram imagens das formas em REFERENCIAS/ e cite os caminhos reais. Mostre antes/depois em enquadramento e distância comparáveis. Se houver limitação de rig, colisão ou desempenho do Roblox, adapte e registre o motivo.

Use Teste-animacoes e confirme a instância antes de acessar. Leia DOCS/estado/studio-em-uso.md, reserve a instância dos dragões se estiver livre e libere sua reserva ao terminar. Preserve reservas de outros places em outras janelas. Remova objetos temporários de teste ao encerrar a sessão. Siga as regras oficiais vigentes e o formato de relatório de CLAUDE.md. Entregue vídeos, resultados, limitações, arquivos afetados e um próximo passo para aprovação.
