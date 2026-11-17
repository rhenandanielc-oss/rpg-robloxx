# Lobo Ancestral — 3D fiel à referência → rig, animações e Roblox

**Chat executor: Lobo Ancestral (Floresta Ancestral).**

Quero produzir o Lobo Ancestral da imagem anexada, primeiro no Blender e depois no Roblox Studio com animações naturais, seguindo o processo já documentado. Faça por etapas; não considere os protótipos antigos arte final.

## 1. Inspecionar e estabelecer a base
Leia `CLAUDE.md`, `MASTER-PROMPT.md`, o índice `PROJECT-STATE.md`, a parte pertinente de `TASKS.md`, `DOCS/ORGANIZACAO-CHATS.md`, `DOCS/criaturas/lobo-ancestral.md`, `DOCS/estado/criaturas-gerais.md`, `BLENDER/Criaturas/Blockouts/PILOTO-ROBLOX-LOBO.md` e o pipeline pertinente de `DOCS/estado/dragao-2026-10-30.md`. Confira arquivos reais: há versões anteriores em `BLENDER/Criaturas/Blockouts/`, mas a V5 não teve anatomia aprovada nem teste no Roblox. Reaproveite somente o que servir à nova referência e explique a escolha.

A imagem principal é o anexo deste pedido, também disponível em `C:/Users/Rhenan/AppData/Local/Temp/codex-clipboard-ab69690c-b1c6-46c0-ad4f-e3d11e7c33ae.png`. Preserve-a em `REFERENCIAS/floresta-ancestral/lobo-ancestral/lobo-ancestral-referencia.png` antes de trabalhar. Esse destino ainda não existe: se o anexo e o arquivo temporário estiverem inacessíveis, peça a imagem; não substitua por outra. Consulte os documentos oficiais RPG_01/RPG_02 ATUALIZADO em Downloads; a atualização de 30/10/2026 prevalece.

## 2. Primeiro: modelo 3D
Produza um **Adulto**, com 5,5–7 studs até os ombros: lobo esguio, atlético e imponente, focinho canino definido, orelhas altas, olhos âmbar, máscara e peito creme, dorso cinza-escuro, flancos castanhos, juba volumosa em mechas e cauda longa e muito peluda. Reproduza o desenho das marcas verdes discretas do peito/ombro como aparência visual; isso não define elemento, habilidade ou efeito de combate. Preserve a identidade da imagem com anatomia funcional: quatro patas digitígradas, articulações corretas, volume sob o pelo e cauda que não arraste. Não copie distorções de perspectiva.

Priorize silhueta, cabeça, proporções, distribuição de cores e fluxo do pelo. Use geometria para os volumes principais e cartões de pelo apenas onde funcionarem no Roblox, controlando transparência e sobreposição. Nada de substituir a pelagem por espinhos ou blocos. Prepare malha otimizada, UVs e texturas compatíveis, registrando triângulos, materiais e resoluções; justifique adaptações e planeje LOD para várias criaturas em PC/celular. Preserve originais e trabalhe em arquivos próprios versionados.

Entregue renders frontal, lateral, traseiro e três-quartos, incluindo **comparação lado a lado com a imagem em cada etapa visual**. Liste diferenças restantes. **Pare para minha aprovação do 3D antes de avançar ao rig final/importação.**

## 3. Depois da aprovação: rig, animações e Studio
Prepare pele deformável e rig quadrúpede com coluna, pescoço, cabeça, mandíbula, orelhas e cauda; pelo acompanha sem atravessar o corpo. Valide deformações em poses extremas. Use o pipeline documentado que realmente funcionar para este rig, sem copiar cegamente o dos dragões.

Refine os clipes existentes pertinentes: repouso/respiração, observar, andar, trotar, correr, parar/virar, saltar/aterrissar, sentar/levantar, deitar/levantar, uivar, rosnar, mordidas/garras e reação a impacto. São clipes visuais; não implemente habilidades históricas como regras oficiais. Exija apoio das patas sem deslizamento, passadas coordenadas, transferência de peso, loops e transições suaves. Confira visualmente em velocidade normal e lenta; contagem de ações não prova qualidade.

Valide exportação por reimportação, esqueleto, texturas e clipes. Antes de qualquer acesso ao Studio, confira e reserve `DOCS/estado/studio-em-uso.md`; se ocupado, aguarde. Comece com M0 somente leitura para confirmar o RPG e a versão correta do place. Importe numa área de teste isolada, preservando o modelo anterior e o mapa. Se houver etapa manual ou publicação de animações pela minha conta, indique exatamente o necessário, sem declarar concluído.

Teste em Play escala, contato com o chão, materiais/alpha, deformação, reprodução e transições; compare capturas lado a lado com a referência. Meça desempenho com várias instâncias e registre quantidade, ambiente e resultados. Diferencie PC, emulação e celular real; teste não feito permanece pendente.

## Limites e entrega
Não altere Lobo Ártico, Cérbero, dragões, bases compartilhadas como `lobo_base.py`/`lobo_v5.py`, sistemas globais ou terreno. Mudança compartilhada exige combinar comigo. Sem IA, combate, domesticação, montaria funcional, novos estágios, elemento ou balanceamento nesta tarefa. Sem instalação, serviço pago, commit ou push sem autorização. Registre mudanças e evidências nas notas pertinentes, libere o Studio ao terminar e responda no formato obrigatório de `CLAUDE.md`, com limitações reais e próximo passo aguardando aprovação.
