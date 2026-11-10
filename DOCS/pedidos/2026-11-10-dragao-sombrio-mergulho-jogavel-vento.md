# Dragão Sombrio — mergulho controlado pelo jogador e frenagem com vento no chão

Destino: chat Claude **Dragão Sombrio (Sombra)**, grupo **Terras Corrompidas**.
Data: 10/11/2026.

## Pedido do usuário e objetivo
O usuário pediu uma movimentação para chegar rapidamente ao chão quando estiver voando alto: o dragão fecha as asas EM TORNO DO PRÓPRIO CORPO, ficando compacto como uma bala de canhão, desce DE FOCINHO PARA O CHÃO e, ao se aproximar, abre e bate as asas para frear, produzindo vento visual rente ao terreno, como o deslocamento de ar de um helicóptero.

Prepare e implemente uma primeira versão JOGÁVEL dessa manobra no Dragão Sombrio, com controle real do jogador, reaproveitando o protótipo existente. Não entregar apenas outra cena automática de duelo. Esta autorização cobre as alterações mínimas necessárias no controle de montaria, clipes próprios do Sombrio e efeito visual de frenagem; mudanças em sistemas compartilhados devem ficar isoladas ao Sombrio e ser descritas no relatório. Não aplicar automaticamente ao Glacial/Fogo, nem transformar o mergulho em poder ofensivo.

## Leitura e estado verificado pelo supervisor
Comece com M0 somente leitura. Leia CLAUDE.md, MASTER-PROMPT.md, PROJECT-STATE.md, tarefa pertinente em TASKS.md, DOCS/ORGANIZACAO-CHATS.md, DOCS/criaturas/dragao-sombrio.md e seção CX/últimas entradas de DOCS/estado/dragao-2026-10-30.md. Confira as alterações locais antes de editar: o gerador meshy/anim_silverwing.py já está modificado, assim como arquivos da sela/exportadores e trabalhos de outros chats. Preserve essas alterações, sem stash/reset/troca de branch.

Atualizações relevantes:
- Commit 8805eb7: asas sem dobra em voo normal, sela do Sombrio e nova montagem pela cauda/frente da asa. A dobra no mergulho é exceção específica pedida pelo usuário, não reversão global da regra.
- Montaria com sela e clipes remontados tem testes documentados; a troca posterior de selas de Fogo/Glacial não comprova todos os testes montados dessas formas.
- Em 09/11, clipe Mergulho_Picado e várias versões da manobra foram testados SOMENTE no script V14/ia/teste_duelo_tatico.luau, não na montaria jogável. O código de produção ainda contém Mergulho_AFK e limites próprios: não confundir existência de clipe com integração.
- Última demo registrada: review/combate/mergulho_fecha_asas_v11.mp4, virada 0,9 s, queda de 170 studs em 1,3–1,5 s, até 139 studs/s; freio a 56–58 studs, recuperação a 9–11 studs. São medidas de demonstração, NÃO parâmetros finais aprovados.
- Defeitos históricos: inclinação com sinal trocado fazia cair de cauda; saltos de posição em versões anteriores; cauda ainda em gancho na v11. Medir em vez de presumir resolvido.

## Fontes e arquivos a inspecionar
Base relativa a BLENDER/Criaturas/Teste_IA/:
- V14/ia/teste_duelo_tatico.luau: referência do protótipo, não controlador de produção para copiar inteiro.
- meshy/anim_silverwing.py: f_mergulho_picado, P_PICADO e EMBOLA. Há variante v2 E3 enrolada e v3 F1 fechada; comparar ambas com o pedido atual. Não selecionar só porque é a mais recente.
- dragao_sombra/rig/SB_Dragao_M2M_v12_asas.blend e JSON Sombrio_Mergulho_Picado: confirmar base atual antes de gerar.
- review/combate/mergulho_de_cabeca_v2.mp4; mergulho_vertical_asas_fechadas_v3.mp4; mergulho_bico_para_baixo_v10.mp4; mergulho_fecha_asas_v11.mp4.
Produção:
- src/ServerScriptService/Montaria_Dragao_Servidor.server.luau;
- src/StarterPlayer/StarterPlayerScripts/Montaria_Cliente.client.luau;
- src/ReplicatedStorage/Montaria_Dragoes/ConfigMontaria.luau e AnimCavaleiro.luau;
- src/ReplicatedStorage/VFX_Dragoes/ConfigAsas.luau e infraestrutura real de efeitos das asas, localizando o consumidor antes de alterar.
- Locomotor, misturador de voo e apelidos reais: localizar os arquivos/objetos exatos e verificar Mergulho_Picado, Mergulho_AFK e Mergulho_Saida.

## Sequência visual e funcional desejada
1. **Acionamento em voo:** jogador solicita a manobra por comando explícito. Inspecionar teclas/botões existentes, escolher ligação sem conflito e informar qual foi usada; incluir botão de toque se compatível com a interface atual. Não disparar automaticamente só porque o jogador olhou para baixo. Servidor valida dono, estado de voo, possibilidade de executar e espaço suficiente.
2. **Fechamento:** recolher patas e asas junto e ao redor do tronco, reduzindo a silhueta de modo legível. Cabeça aponta para a direção da queda; pescoço e cauda acompanham, sem cauda em gancho. “Bala de canhão” descreve compacidade e impulso, não uma esfera literal, giro em cambalhota ou deformação da malha. Evitar asas em V, abertas para os lados ou atravessando sela/cavaleiro.
3. **Queda rápida:** inclinar o corpo de focinho para baixo, quase vertical, e acelerar de forma contínua e limitada. Cabeça deve estar abaixo do quadril na fase estabelecida da queda. Não usar correção por teleporte nem reaproveitar a separação artificial dos dragões do duelo. Manter rumo estável na vertical; permitir cancelamento conforme controles existentes, sem prisão involuntária do jogador.
4. **Frenagem antes do chão:** detectar o terreno/obstáculos reais no caminho e abrir asas a tempo, com transição corporal contínua e batidas fortes de sustentação. Levar em conta distância necessária para desacelerar, velocidade vertical, tempo de abertura e volume da criatura, incluindo cabeça/asa/cavaleiro; não usar apenas altitude fixa do pivô ou coordenada Y do alvo. Em alta velocidade, sondar o percurso entre quadros para evitar atravessar superfícies.
5. **Vento no chão:** durante as batidas próximas à superfície, um fluxo de ar desce e se espalha radialmente rente ao piso, acompanhando cada batida com atraso coerente. Usar rastros/transparências e poeira leve apropriada ao material; nada de disco sólido ou explosão mágica. Evitar levantar rochas grandes, danificar cenário ou criar vento sem superfície próxima. Em água, se houver suporte na etapa, usar ondulação/spray discreto e registrar teste separado. Em piso limpo, vento visual sutil sem poeira de terra inventada.
6. **Recuperação:** finalizar em voo baixo/estável, devolvendo controle fluido. Pode usar pouso normal se o jogador solicitar; não forçar choque de focinho, impacto ofensivo ou pouso automático como nova regra. Não continuar em queda livre quando a manobra termina. Sem necessidade de subir centenas de studs automaticamente como na demo.

## Limites e riscos a resolver nesta etapa
- Trata-se de locomoção, não novo slot de ativa: sem dano de impacto, atordoamento, invulnerabilidade, teleporte ou custo de energia criado por conta própria. Preservar regras atuais de fôlego, energia, missão de voo e montaria.
- Altura insuficiente: recusar o picado e preservar voo seguro em vez de começar uma queda que não possa frear. Testar terreno inclinado, plataforma alta e obstáculos na descida; superfície deve ser detectada onde o dragão efetivamente vai passar.
- Velocidades, acelerações, limiar de entrada e margens de frenagem são parâmetros experimentais identificados, não números oficiais. Rastro do Breu não pode multiplicar a queda sem limite nem invalidar distância de frenagem; considerar a velocidade real ao frear.
- Fazer estado/transições determinísticos: entrada, picado, freio, recuperação/cancelamento. Evitar sobreposição com ataque, pouso ou outra manobra; usar compatibilidade existente e documentar decisões sem redesenhar combate.
- Orientação: o diário mediu pitch negativo = focinho para baixo no eixo usado pelo Locomotor. Conferir no controlador real: medir cabeça/quadril e registrar sinal, não corrigir cegamente todos os cálculos de rampa.
- Cavaleiro mantém contato coerente com sela, mãos/assento e postura adequada à inclinação; câmera não atravessa o corpo nem sofre inversão brusca. Não alterar os clipes de montar/desmontar ou a sela aprovada sem necessidade.
- Se o gerador compartilhado for necessário, modificar somente a função/configuração correspondente e gerar somente os clipes autorizados do Sombrio. Não regerar todos os clipes/formas nem sobrescrever alterações locais existentes; se houver conflito ativo com outro chat, coordenar o trecho antes da edição. Preferir implementação isolada quando viável.

## Referências visuais e comparação
Imagem real da criatura: BLENDER/Criaturas/Teste_IA/dragao_sombra/ref/ref_sombrio.png. Não foi localizada referência própria em REFERENCIAS/ na inspeção atual; informar essa ausência, verificar se o usuário adicionou algo depois e citar somente caminhos existentes. Os vídeos acima são evidência e referência de movimento já produzida; a referência de vento “igual helicóptero” é direção textual do usuário, não licença para acrescentar hélice ou reproduzir uma imagem inexistente.

A CADA etapa visual comparar lado a lado com a referência da criatura e com versão anterior; para movimento, usar vídeos/quadros equivalentes, mesma câmera/escala/iluminação. Mostrar perfil, frente/3/4 e câmera real do jogador: fechamento completo, queda, abertura, batidas e vento. Incluir vídeo em velocidade real e trecho em câmera lenta, sem esconder falhas com câmera distante. Se alguma dobra da referência textual não funcionar no rig/Roblox, adaptar e registrar o motivo, preservando leitura compacta e anatomia animável.

## Studio e escopo
Lugar documentado: **Teste-animacoes**, placeId 101211272245630; confirmar instância e conteúdo no M0 antes de mutar. O usuário esclareceu que outros chats podem usar outros places/instâncias; reserva do Lobo Ancestral em Baseplate isolado não bloqueia automaticamente este place.
Antes de usar Studio, ler DOCS/estado/studio-em-uso.md, identificar instância ocupada e registrar reserva própria por place/instância sem apagar reserva de outro chat. Um chat por vez na MESMA instância. Ao terminar, liberar apenas sua reserva. Backup recuperável identificado antes de patches; não sobrescrever históricos. Salvar ou orientar salvamento com estado factual, sem repetir perda de alterações não salvas.
Preservar outras criaturas, mapa, Fogo/Glacial, poderes e arquivos não necessários. Sem commit, push, instalação, compra, publicação ou novo acesso pago. Seguir documentos oficiais RPG_01_Mundo_e_Sistemas_ATUALIZADO.docx e RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO.docx em C:/Users/Rhenan/Downloads/, com atualização de 30/10/2026 e decisões posteriores do usuário. Não confundir com Dragon Ranch.

## Aceite e testes obrigatórios desta fatia
Entregar a manobra completa no Sombrio montado, controlada pelo jogador, antes de expandir para outro dragão.
- Testar ao menos três alturas, incluindo entrada baixa recusada com segurança, voo alto, movimento horizontal e várias velocidades; demonstrar tempo/altura/velocidade e distância mínima da malha ao solo, sem transformar valores da demo em obrigação.
- Queda estabelecida de cabeça, asas compactas ao redor do tronco, sem sela atravessada ou cauda em gancho; sem posições inválidas, mudanças descontínuas ou atravessar chão.
- Abertura começa a tempo, batidas freiam visivelmente e vento coincide com proximidade do terreno. Testar chão plano, rampa, plataforma elevada e obstáculo na trajetória.
- Testar cancelamento, comando repetido, retomada de voo, interação com Rastro e tentativa durante estado incompatível; morte/remoção/desmontagem quando permitida limpam estado e VFX.
- Gravar teclado/controle real em Play; reprodução no Edit ou script coreografado não comprova jogabilidade. Conferir que voo normal, pouso e outros dragões mantêm comportamento anterior.
- VFX só cliente, movimento validado no servidor, partículas/atualizações limitadas, LOD e limpeza. Medir desempenho no mesmo cenário antes/depois; mencionar explicitamente se celular físico, multiplayer e latência não forem testados. Não prometer aprovação de desempenho com base só em ausência de erros.

## Relatório final
Usar modelo de CLAUDE.md: tarefa autorizada e objetivo; leitura/inspeção; alterações reais; testes/evidências; riscos/pendências; arquivos atualizados e estado para próxima sessão; próximo passo proposto aguardando aprovação. Acrescentar comando de entrada/cancelamento, parâmetros experimentais, links locais dos vídeos, integração real ou pendente, sincronização src/Studio e salvamento. Atualizar registros factuais; não marcar [x] sem implementação + teste + evidência. Não ampliar para outros dragões sem aprovação.
