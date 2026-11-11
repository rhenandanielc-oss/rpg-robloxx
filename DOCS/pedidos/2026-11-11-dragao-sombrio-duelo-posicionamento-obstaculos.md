# Duelo Glacial × Sombrio — posicionamento e obstáculos

Destino: chat Claude **Dragão Sombrio (Sombra)**, grupo Terras Corrompidas. Revisão aprovada pelo usuário em 11/11/2026.

## Objetivo

Refine a escolha de posições e a navegação entre obstáculos no duelo isolado. Cada deslocamento deve servir a uma ação clara: recuperar visão, abrir ângulo de ataque, manter distância útil ou recuar. Aplique a revisão em BLENDER/Criaturas/Teste_IA/V14/ia/teste_duelo_decisao.luau e nos artefatos do teste.

Comece em leitura. Consulte CLAUDE.md, DOCS/ORGANIZACAO-CHATS.md, o pedido 2026-11-11-dragao-sombrio-duelo-ia-glacial.md e a seção DH de DOCS/estado/dragao-2026-10-30.md. Use como base o vídeo e o resumo duelo_decisao_v1 em BLENDER/Criaturas/Teste_IA/dragao_sombra/review/combate/. O vídeo tem trechos longos de separação aérea e um contorno pouco decidido entre 2:50 e 3:00. O relatório registra até sete golpes abortados por desalinhamento por rodada e asas fora da cápsula de colisão. Esses pontos guiam o teste.

## Comportamento esperado

- Antes de preparar um golpe, selecione uma posição alcançável que combine faixa do ataque, visão, altura e espaço para virar. O Sombrio busca um flanco utilizável. O Glacial procura manter uma faixa de controle com uma saída livre. Se o rival fechar o ângulo ou se esconder, reavalie o ataque e a rota.
- Quando uma rocha bloquear a visão, use o último ponto onde o rival foi visto. Compare contorno pela esquerda, pela direita e, em voo, passagem por cima quando houver folga para subir e recuperar. Verifique a passagem inteira e a posição de chegada. Considere a largura do corpo e das asas, a cauda na curva e o raio de giro. Uma rota livre para o focinho pode ser estreita demais para a criatura.
- Escolha um lado com objetivo verificável, como recuperar a linha de visão fora do alcance imediato do rival. Mantenha a rota enquanto houver progresso. Se ela fechar ou parar de avançar, tente uma alternativa segura. Se as alternativas falharem, recue para espaço livre ou encerre a busca pelo limite aprovado. Evite alternar esquerda e direita a cada atualização.
- Exemplo: diante de um paredão, o Sombrio segue por uma borda com cobertura e só arma o golpe ao recuperar visão e alinhar o corpo. O Glacial pode vigiar uma saída e ajustar a distância para evitar ficar prensado contra o obstáculo. Em passagem estreita, ambos preferem abrir espaço ou contornar.
- Reserve espaço também entre os dragões em combate próximo, sobretudo durante viradas, decolagem e asas abertas. Teste a folga visual e evite correções bruscas de posição. Preserve a recuperação após golpes e os limites de investigação e perseguição já definidos.

## Teste e aceite

Repita com condições equivalentes à versão anterior em espaço aberto e no cenário da rocha que bloqueia a visão. Acrescente uma passagem estreita com saída bloqueada e um obstáculo que possa ser contornado por cima. Inverta lados iniciais para detectar preferência fixa. Preserve os parâmetros atuais de dano, vida, recarga e energia durante a comparação.

Registre tempo para recuperar visão, ataques iniciados e abortados por desalinhamento, rota escolhida, motivo de troca e desfecho do reposicionamento. Mostre menos abortos por desalinhamento nas rodadas comparáveis e pelo menos um contorno com ataque válido ou recuo claro. Confira que nenhum ataque atravessa o obstáculo e que corpo, asas e cauda têm folga nas passagens demonstradas. O risco principal é oscilar entre rotas ou aumentar o custo de navegação. Meça o tempo do teste antes e depois e limite consultas por dragão para PC e celular. Declare plataformas ainda sem teste.

Grave o antes/depois em Play, com câmera próxima o bastante para ver o rival, a rocha e as asas. Compare cada etapa visual com a versão anterior e as imagens reais BLENDER/Criaturas/Teste_IA/dragao_sombra/ref/ref_sombrio.png e BLENDER/Criaturas/Teste_IA/dragao_gelo/ref/ref_glacial.png. Na inspeção atual, REFERENCIAS/ não contém imagens próprias dos dois dragões. Se houver novas imagens, cite seus caminhos reais. Adapte poses e trajetos ao rig e aos limites do Roblox.

Use Teste-animacoes e a reserva por instância em DOCS/estado/studio-em-uso.md. Preserve reservas de outros chats e libere a sua ao terminar. Trabalhe em segundo plano conforme CLAUDE.md. Restrinja as mudanças ao duelo de teste e preserve o mapa, os guardiões do jogo, outros chats e os módulos compartilhados. Respeite as regras oficiais vigentes. Entregue o relatório no formato de CLAUDE.md, com vídeos, métricas, limitações, arquivos afetados e próximo passo para aprovação.
