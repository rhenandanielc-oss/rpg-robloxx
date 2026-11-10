# Dragão Sombrio — revisão da descida e postura com referências de Dragon Adventures

Destino: Claude **Dragão Sombrio (Sombra)**, grupo **Terras Corrompidas**.
Data: 10/11/2026.

## Pedido atual e autorização
O usuário assistiu à descida jogável e pediu uma melhoria grande, tomando Dragon Adventures como inspiração. Relato explícito: “o rabo pra cima a cabeça pra cima e o corpo pra baixo”. Corrija a composição corporal e a fluidez da manobra inteira, não apenas velocidade ou VFX. Esta revisão está autorizada para o Sombrio e para as integrações mínimas necessárias da sua montaria. Preserve a intenção já aprovada: asas recolhidas ao redor do corpo na queda, focinho para baixo, descida rápida e frenagem com batidas e vento no chão.

Trabalhe uma fatia por vez: primeiro diagnóstico + poses e transições corrigidas em demonstração curta; em seguida validar a mesma revisão no controle real do jogador, dentro deste pedido. Não encerrar com outra demonstração coreografada sem integração. Não expandir para outras criaturas/formas.

## Estado e evidência realmente inspecionada
Leia CLAUDE.md, DOCS/ORGANIZACAO-CHATS.md, MASTER-PROMPT.md, PROJECT-STATE.md, tarefa pertinente em TASKS.md, ficha DOCS/criaturas/dragao-sombrio.md e seção CY/entradas posteriores de DOCS/estado/dragao-2026-10-30.md. Leia também DOCS/pedidos/2026-11-10-dragao-sombrio-mergulho-jogavel-vento.md; este pedido complementa e corrige os critérios visuais anteriores.

CY registra versão jogável na tecla V, Sombrio apenas, com testes de teclado em Play, terreno/plataforma/obstáculo/água, cancelamento e medição desktop. Há limites conhecidos: patas traseiras soltas; morte seguida de pouso automático com salto de posição; celular/multiplayer/latência não testados. Parâmetros são NAO_APROVADO. Esses testes não equivalem a aprovação da estética.

O supervisor inspecionou a prancha comparativa e amostrou o vídeo real em 12 pontos (não uma análise quadro a quadro completa):
- BLENDER/Criaturas/Teste_IA/dragao_sombra/review/mergulho_jogavel/mergulho_picado_jogavel_v1.mp4 (53,7 s, 20 fps);
- mesma pasta: comparacao_ref_v11_v1.jpg e variantes_asas_F1_G1_G2.jpg;
- prancha de amostras gerada só para inspeção: DOCS/pedidos/inspecao-mergulho-prancha.jpg; quadros individuais inspecao-mergulho-0.jpg a -11.jpg na mesma pasta.

Na recuperação, os quadros próximos de 37,6 s, 43,0 s e 48,3 s mostram cauda muito elevada, pescoço/cabeça levantados e tronco ainda inclinado, com asas abrindo a silhueta. Outros quadros (5,4 s e 51,0 s) mostram cauda ocupando grande parte do enquadramento do cavaleiro. A amostragem revela o defeito; localizar no vídeo completo os intervalos exatos de cada fase e a causa antes de editar. Confirmar versão exibida se houver vídeo mais novo.

“Cabeça abaixo do quadril em 68/68 amostras” avalia parte da queda, mas NÃO demonstra alinhamento do corpo nem qualidade da frenagem. Não usar essa métrica isolada para declarar a animação correta.

## Referências externas encontradas e limites da pesquisa
O usuário pediu procurar referências de Dragon Adventures. Foram localizadas as fontes abaixo; são links reais, mas as mídias externas NÃO foram reproduzidas pelo supervisor: abertura direta de algumas páginas/YouTube falhou. Portanto, não afirmar que houve análise visual dos seus quadros nem inventar timestamps. Abra as mídias disponíveis no seu ambiente e identifique o que realmente conseguiu assistir; se indisponíveis, registre e continue a correção comprovada no nosso vídeo, sem inventar movimentos atribuídos ao outro jogo.

1. **Dragonpedia, galeria de animações do jogo** — https://dragon-adventures.fandom.com/wiki/Dragonpedia
A página indexada descreve seleção e reprodução de animações do dragão. É caminho de referência para visualizar poses no jogo. Se o usuário já tiver captura acessível em seu chat, use-a prioritariamente. Não abrir Roblox ou trocar o place dos dragões para jogar Dragon Adventures sem autorização específica; não gastar Robux nem comprar criatura.

2. **Numine, galeria / Development** — https://dragon-adventures.fandom.com/wiki/Numine
A galeria indexada lista Fly animation e Rigged model. Candidato para comparação de articulação de um dragão alado; não é prova de uma sequência de mergulho específica. Só citar detalhes de dobra/timing se a mídia efetivamente mostrar isso. A forma e os materiais do Sombrio permanecem próprios.

3. **Amaris** — https://dragon-adventures.fandom.com/wiki/Amaris
O texto indexado informa giro durante o mergulho. Isso demonstra que Dragon Adventures tem atuações específicas por espécie; NÃO copiar giro/cambalhota nem adotar o corpo serpentino do Amaris como referência anatômica para o Sombrio. Não há pedido de barrel roll nesta tarefa.

4. **Showcase de Fulong, autoria da postagem AnnaBanana101, 06/11/2024** — https://dragon-adventures.fandom.com/f/p/4400000000002261123/r/4400000000011191106
Vídeo vinculado pela postagem: https://www.youtube.com/watch?v=BRD-XlXy_FQ
Título indicado na postagem: The Fulong Redesign Is Amazing!! É referência candidata de atuação corporal, não referência validada de mergulho: o comentário da postagem inclusive questiona a ausência do movimento de mergulho. Não usar como evidência de que uma descida específica existe nesse vídeo sem assistir.

5. **Gyrocopter / galeria com item Dive animation** — https://dragon-adventures.fandom.com/wiki/Gyrocopter
Há uma mídia explicitamente listada como Dive animation; só serve para investigar a continuidade de uma animação específica. É criatura mecânica com rotores, inadequada para copiar anatomia/asa do Sombrio. O vento tipo helicóptero já foi pedido pelo usuário, mas NÃO adicionar hélices ou transformar o Sombrio nesse modelo.

O princípio de direção proposto para nossa revisão é sensação de criatura inteira orientada ao deslocamento, poses legíveis e transições contínuas. Isso é especificação deste prompt, NÃO descrição confirmada de todas as animações do Dragon Adventures. Escolha no máximo duas referências úteis e efetivamente assistidas; entregue URL, espécie, timestamps/quadros, o detalhe observado e como foi adaptado. Não preencher referência com artigos genéricos de códigos/troca/breeding ou com descrição de marketing. Não extrair assets/rigs/animações proprietários; produzir movimento próprio baseado em observação.

## Diagnóstico obrigatório das poses estranhas
Inspecione separadamente e depois em composição:
- inclinação/rotação do modelo raiz e trajetória real;
- pose local de coluna, pescoço, cabeça e cada segmento de cauda;
- Mergulho_Picado, Mergulho_Saida e Pairar_AFK, pesos, prioridades e curvas de transição;
- contribuição de MovimentoVivo_Cliente, olhar automático e compensações procedurais;
- movimento/compensação do cavaleiro e seguimento da câmera.

Hipóteses a testar, NÃO causas já provadas: Mergulho_Saida reaproveitado com extensão excessiva do pescoço/cauda; Pairar somado antes de o root terminar a recuperação; rotação aplicada duas vezes ou no eixo errado; ossos voltando à postura de voo comum enquanto o tronco permanece apontando para baixo; cauda preservando curva local incompatível com o pitch global. O código atual atribui prioridade Action ao Mergulho_Saida e combina a frenagem com Pairar: inspecionar essa composição, não assumir que ajustar MP.pitchFreio resolve todos os ossos.

Faça ablação: reproduza o mesmo trecho com root isolado, clipe isolado, misturador e movimento secundário reintroduzidos um a um. Registre qual camada gera o U/quebra de postura. Corrija a origem; não esconda com câmera, partículas ou velocidade maior.

## Direção detalhada para o movimento revisado
### 1. Entrada e recolhimento
Manter continuidade do vetor de movimento atual. Antecipação curta e decidida, sem obrigar o corpo a ficar em pé como cavalo empinado antes de cair. Recolher patas junto ao ventre e asas ao longo/ao redor do tronco em sequência de ombro, cotovelo, punho e dedos. A asa deve ficar pequena na silhueta, sem virar lança vertical, tenda lateral ou membrana atravessando sela.

O diário diz que F1 foi mantida porque G1/G2 apenas abriam a asa ao variar um parâmetro. Isso não esgota as soluções: estudar a cadeia completa e a deformação da membrana. Se o rig/malha não comportar enrolamento literal, buscar recolhimento compacto plausível e mostrar limite, em vez de aceitar uma postura aberta como concluída. Não alterar anatomia/esqueleto compartilhado ou pesos amplos sem apresentar a necessidade ao usuário; tentar primeiro poses/clipes próprios e ajustes isolados.

### 2. Picado estabelecido
Silhueta longitudinal: focinho → pescoço → peito → quadril → cauda formam uma continuidade orientada à trajetória. Focinho aponta para baixo; cabeça não olha para o horizonte quando o corpo cai de cabeça. Pescoço pode ter curvatura orgânica, mas sem dobra quebrada na base. Cauda segue atrás do quadril, alinhada aproximadamente ao eixo do corpo, ponta com atraso suave; sem gancho, bandeira ou chicote constante.

A cauda estar mais ALTA no mundo que a cabeça durante queda vertical é normal. O defeito a eliminar é a cauda dobrada “para cima” em relação ao tronco, especialmente quando cabeça e cauda arqueiam juntas e o peito fica pendurado entre elas. Não corrigir isso simplesmente impondo cauda.Y < corpo.Y, que inverteria a anatomia na queda.

Patas traseiras flexionadas e recolhidas, dianteiras compactas; não correr no ar nem deixar pernas balançarem. Cavaleiro acompanha a inclinação, postura compacta, contato coerente com sela. Não forçar cabeça do cavaleiro e cabeça do dragão a olhar para cima durante o picado.

### 3. Preparação do freio
Abrir as asas progressivamente antes de precisar da sustentação máxima; corpo começa a recuperar orientação em uma curva contínua. Pescoço/cabeça acompanham essa recuperação; cauda responde com atraso AMORTECIDO e amplitude limitada. Não trocar de pose abruptamente de “bala” para “pairar de peito erguido”.

Se usar Mergulho_Saida existente, revisar se sua pose é adequada a esta descida vertical; criar uma saída própria do Sombrio se necessário. Não acelerar Pairar como substituto automático de uma animação de frenagem. A batida precisa de preparação, golpe potente e recuperação compatíveis com a massa e a velocidade.

### 4. Frenagem e nivelamento
Abrir/bater asas enquanto desacelera, nivelando tronco progressivamente. Ao final do freio, cabeça, peito, quadril e cauda recompõem uma linha de voo estável, sem cabeça erguida e cauda vertical com tronco pendurado. A cabeça só pode iniciar olhar à frente com transição anatômica coerente, sem pescoço de cisne exagerado.

Não usar interpolação independente de cada parte sem coerência temporal. O root não pode inclinar para um lado enquanto coluna/pescoço/cauda compensam exageradamente para o outro. Evitar overshoot de mola, tremor e transição que alterna clipes a cada quadro.

### 5. Voo baixo e vento
Preservar o vento solicitado, sincronizado às batidas e à proximidade real do piso. Dispersão radial discreta, poeira só onde plausível e spray na água se já suportado. Não usar efeito para esconder a pose. Retorno ao voo baixo deve manter inércia e controle do jogador, sem parada seca seguida de salto ou subida automática exagerada.

## Arquivos e fronteiras
Principais: src/ServerScriptService/Montaria_Dragao_Servidor.server.luau (PATCH_MERGULHO_PICADO); src/ReplicatedStorage/Montaria_Dragoes/ConfigMontaria.luau; src/StarterPlayer/StarterPlayerScripts/Montaria_Cliente.client.luau e MovimentoVivo_Cliente.client.luau; AnimCavaleiro.luau; VentoMergulho_Cliente (localizar caminho real). Clipes/rigs próprios em BLENDER/Criaturas/Teste_IA/dragao_sombra/ e JSON Sombrio_Mergulho_Picado; gerador compartilhado BLENDER/Criaturas/Teste_IA/meshy/anim_silverwing.py apenas no trecho necessário, preservando alterações pendentes.

Não alterar combate/poderes, dano, passivas, sela, montar/desmontar, outras criaturas, mapa ou comportamento de Fogo/Glacial. Novo ajuste deve atuar somente no Sombrio; não regerar todos os clipes de todas as formas. Se houver conflito de edição simultânea em compartilhado, coordenar antes. Sem commit/push, instalação, compra ou publicação.

Referência de identidade existente: BLENDER/Criaturas/Teste_IA/dragao_sombra/ref/ref_sombrio.png. Não foi localizada referência própria em REFERENCIAS/ nas inspeções anteriores; verificar se mudou e citar somente imagens reais. As imagens/vídeos de movimento encontrados na internet são referências externas, não arquivos locais fictícios. Comparar lado a lado com imagem da criatura, versão jogável v1 e referência externa que realmente conseguir abrir, em cada etapa. Se inacessível, registrar qual comparação faltou; nunca declarar fidelidade só pelo texto de uma página.

## Testes e critérios de aceite
Primeiro entregar prancha lateral de 8 poses: voo → recolhimento inicial → final do recolhimento → queda → abertura inicial → primeira batida de freio → nivelamento → voo baixo. Incluir linhas simples dos eixos do tronco e cadeia de pescoço/cauda e setas de velocidade. A prancha deve expor, não ocultar, deformações.

Depois vídeo curto real em Play, teclado V e cancelamento, de perfil e câmera de cavaleiro, tempo real + trecho lento. Mostrar 3 manobras repetidas a partir de alturas/velocidades diferentes; nenhuma fica com cabeça e cauda arqueadas juntas contra um tronco pendurado. Três quadros bonitos não bastam: conferir transições inteiras.

Quantificar com fase e instante: pitch raiz, eixo peito–quadril, eixo focinho–pescoço, tangentes da cauda, pesos dos clipes e distância real ao piso. Usar medidas para explicar defeitos; limites angulares de teste são experimentais, não regras oficiais de jogo. Observar frente local da cabeça versus vetor de velocidade no picado, sem usar métrica de altura como único aceite.

Preservar testes anteriores de parada segura, rampa, plataforma e obstáculo, porque alterar pose altera volume e ponto mais baixo do corpo. Confirmar que nova asa/pata/cauda não atravessa a superfície durante abertura. Sem teleporte, salto, NaN, aceleração ilimitada ou regressão no controle/cancelamento. Separar defeito pré-existente de pouso após morte de qualquer regressão introduzida; não ampliar para refazer toda a montaria.

Desempenho PC/celular: reaproveitar estruturas, limitar atualização/VFX, medir desktop antes/depois sob mesmo cenário. Testar multiplayer/latência/celular quando possível e declarar o que não foi testado; ausência de erros e 60 FPS no Studio não aprovam celular.

Studio: confirmar instância Teste-animacoes, placeId documentado 101211272245630. Ler/reservar DOCS/estado/studio-em-uso.md por instância/place; outra janela de rpg_roblox/Baseplate não bloqueia automaticamente, mas a mesma instância só pode ter um chat. Não apagar reserva alheia. Backup recuperável antes de aplicar e liberar sua reserva no fim; confirmar estado de salvamento.

Seguir regras oficiais e atualização de 30/10/2026 nos documentos RPG_01_Mundo_e_Sistemas_ATUALIZADO.docx e RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO.docx em C:/Users/Rhenan/Downloads/. Não confundir com Dragon Ranch. O pedido atual aprova revisão do movimento, não novas regras de dano/custos/poderes.

## Relatório obrigatório
Formato CLAUDE.md: tarefa autorizada e objetivo; inspeção; alterações reais; testes/evidências; riscos/pendências; arquivos atualizados e estado para próxima sessão; próximo passo aguardando aprovação. Acrescentar diagnóstico comprovado de cada postura ruim, camada responsável, referências efetivamente assistidas com timestamps e comparação antes/depois, limitações do rig, controles e salvamento/src versus Studio. Não chamar a revisão de aprovada: apresentar ao usuário para avaliação visual.
