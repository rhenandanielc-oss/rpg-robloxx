# Criaturas oficiais: blockouts, lobos, produção V5

Voltar ao índice: [[PROJECT-STATE]]

## OPERAÇÃO C1 — CRIAÇÃO DAS CRIATURAS OFICIAIS (2026-10-26, tarde; usuário ausente, execução autônoma das etapas seguras)
**Catálogo:** `ServerStorage.Biblioteca_Criaturas.Catalogo` registra 13 espécies, 16 formas e 48 padrões (RPG_02), com medidas, elementos, locomoção, montaria e 4 habilidades por forma. Os nomes das habilidades usadas nas animações foram conferidos contra o catálogo. A matriz completa está em `DOCS/CRIATURAS-C1-MATRIZ.md`.

**Prontas no Studio (testadas em Play/PC):**
- **Lobo Ancestral** (6,57 de ombro) e **Lobo Ártico** (6,6 de ombro) em `Biblioteca_Criaturas.Modelos`.
- Rig Motor6D com erro de montagem ~0,003, 13 animações e 3 padrões por tingimento.
- Atributo `Estado` = Testes aprovados.
- 12 lobos animados não mudaram o FPS de forma mensurável.
- 0 scripts ativos na Biblioteca.

**Feitas no Blender 5.2 (linha de comando), validadas por reimportação, com importação manual no Studio PENDENTE:**
- **Dragão das Montanhas, Dragão Glacial, Dragão Sombrio:** 45 ossos, 15 animações, de 16,5 mil a 18,4 mil tris, 21 de ombro.
- **Wyvern:** 38 ossos, 18 animações, 14,1 mil tris, 11 de ombro e 38 de envergadura.
- **Serpente Marinha:** 15 ossos, 10 animações, 39 de comprimento.
- **Leviatã Jovem:** 22 ossos, 11 animações, 69,7 de comprimento.
- **Crocodilo Primordial:** 23 ossos, 11 animações, 6,2 de ombro e 25,7 de comprimento.
- **Basilisco:** 23 ossos, 10 animações, ~8,3 de ombro.
- **Lagarto Cristalino:** 23 ossos, 10 animações, 19,9 de comprimento.
- **Escorpião Colossal:** 42 ossos, 9 animações, 22,9 de comprimento.
- Cada forma tem GLB + FBX + `.blend`, uma textura de cor 2048 por padrão (3) e uma normal 2048. Ficam em `BLENDER/Criaturas/`, com o passo a passo em `LEIA-ME-IMPORTACAO.md` e os scripts em `scripts/`.
- Glacial e Sombrio foram reexportados com o nome correto da malha (antes ainda se chamava "Dragao_das_Montanhas").
- Habilidades viraram **apenas animações**: sem efeitos, sem dano, sem IA.

**Provisórias, reprovadas ou não iniciadas:**
- **Urso Silvestre** provisório: 3ª geração do gerador do Studio, estilizada, 9,14 de ombro, no `Laboratorio_Criaturas`.
- **Cérbero Sombrio:** **provisório no Studio**, em `Laboratorio_Criaturas.Cerbero_Sombrio_PROVISORIO`, aguardando aprovação da aparência.
  - Montado a partir de um clone do Lobo Ancestral aprovado: tronco ×1,4, patas mais grossas, 2 pescoços/cabeças laterais em juntas Motor6D próprias (±35°).
  - Escala 14,0 de ombro (oficial 12–16).
  - 13 animações; MordidasTriplices com as cabeças em sequência (medido: centro → esquerda → direita).
  - 3 padrões oficiais tingidos.
  - Play/PC: patas sem afundar; FPS 49,5 com e 49,7 sem o Cérbero (sem custo mensurável; o nível geral está baixo pela memória do Studio).
  - O rascunho anterior do Blender foi reprovado e ficou em `BLENDER/Criaturas/_Provisorios`.
- **Correção no pipeline:** o Animator multiplica as translações por `Model:GetScale()`, e o `PipelineQuadrupede` aplicava a escala de novo.
  - Efeito: o Cérbero deitava 13 studs abaixo do chão; o Lobo Ártico flutuava 0,3 deitado.
  - Pipeline corrigido.
  - Animações do Lobo Ártico regeneradas: barriga deitada a 0,10, locomoção inalterada, medido em Play.
- **Leão Solar** e **Búfalo Colossal:** não iniciados (o leão do gerador foi reprovado por ser caricato).
- Gerações reprovadas do Studio (11) estão em `Proto_Restore.Retirados_C1`, com o atributo `Motivo`.

**Capturas:** `SCREENSHOTS/C1_Criaturas/` — lobos (frente, lateral, escala, Play andando, deitado e uivando, 3 padrões), urso provisório, folhas do Blender (dragão em vistas e poses, 3 formas, 9 padrões, Wyvern, aquáticos, répteis, Escorpião, Cérbero rascunho) e os reprovados.

**Snapshot:** `Documents/RPG_Roblox/BACKUPS/RPG_BKP_2026-10-26_C1_criaturas.rbxl` (autosave das 15:24, 166,3 MB, hash conferido).

**Impedimentos (exigem o usuário):**
1. A integração não importa arquivos locais: GLB/FBX entram pelo **Import 3D** manual.
2. Para o jogo publicado, as animações precisam ser publicadas (Animation Editor → Publish).
3. O salvamento na nuvem continua falhando por tamanho; a exportação de `Proto_Restore` aguarda autorização.

**Não feito nesta operação:**
- integração com habitats e ninhos. A **conferência somente leitura** foi feita (ver a matriz):
  - as cavernas e câmaras comportam os dragões; o Covil Vigia fica apertado;
  - nas plataformas de pouso e nos ninhos de Wyvern, a cauda sobra;
  - os valores provisórios da Tundra divergem dos modelos;
  - nada foi alterado no mapa (decisão do usuário);
- IA, combate, montaria e progressão;
- teste no celular e em multiplayer.

## OPERAÇÃO CREATURE BLOCKOUT — SILHUETAS DAS 16 FORMAS (2026-10-26, noite; autorização autônoma do usuário)
**Ferramentas:**
- Blender 5.2, com headless para builds e renders. O Blender aberto foi comandado pelo socket do add-on blender-mcp (porta 9876), porque as ferramentas MCP do Blender não carregam nesta sessão do Code.
- Skills instaladas em `~/.claude/skills` (23), lidas do disco: `blender-image-to-3d` (gates de silhueta, `world_gate`, `review_render`) e `blender-workflow-recipes`.

**Resultado:** biblioteca `BLENDER/Criaturas/Blockouts/CR_Blockouts_Biblioteca.blend` (`CREATURES/BLOCKOUTS/<Especie>`).
- 16 formas, 41 objetos de malha; o maior tem 18.000 tris (limite do MeshPart: 20.000).
- Mais um arquivo de trabalho por forma e os scripts que regeneram tudo.
- **Construídos: 16. Reaproveitados: 0.** Os 10 modelos Blender da C1 foram reprovados contra as referências (magros, de patas altas, "lagartos") e continuam intactos.
- Formas com silhueta própria por diferença documentada: os 2 Lobos e os 3 Dragões. Os padrões (48) são só de cor.

**Gates de silhueta (world_gate, escala real):**
- Leão v2: 0,821. Corrige a v1 reprovada pelo usuário (cabeça grande, juba oval, peito estreito, patas finas, cauda artificial).
- Lobo Ancestral 0,836; Lobo Ártico 0,841; Urso 0,802; Búfalo 0,799 (referência em perspectiva).
- As outras 11 têm comparação visual: as silhuetas oficiais estão em pose, em perspectiva ou na água/rochas.
- Nenhuma atingiu a meta de 0,85 da skill (o Leão passou por ela em 0,856 e voltou a 0,821 por escolha anatômica; a face precisava projetar).

**Medidas:** todas dentro das faixas oficiais. Os valores sem documento estão marcados como provisórios (ver `Blockouts/LEIA-ME-BLOCKOUTS.md`).

**Capturas:** `SCREENSHOTS/Blockouts_2026_10_26/`, com 16 folhas (silhueta oficial, gate, frente, lateral, 3/4, 128 px), a visão geral e o contato dos reprovados.

**Não feito (fora do escopo):** texturas, pelagem, materiais, rig, animação, importação no Roblox, testes no jogo. O mapa e os biomas não foram alterados.

## CRIATURAS — REFINAMENTO + FINALIZAÇÃO + RIG + ANIMAÇÕES (2026-10-26, noite; "refine, termine o desenho e a animação, não me pergunte nada")
**Pedido:** a análise (`DOCS/CRIATURAS-REFINAMENTO-ANALISE.md`) e o plano (`DOCS/CRIATURAS-RIG-ANIMACOES-PLANO.md`) foram executados em cima dos blockouts aprovados. A cópia da fase de silhuetas foi preservada.

**Feito no Blender:**
- **Refinamento:** 16 formas com marcos ósseos, patas e cabeças por família e estruturas por espécie. IoU da silhueta mantido em 0,795–0,833.
- **Finalização:** materiais por papel, cor-base = padrão oficial 1, contra-sombreamento por cor de vértice, ≤ 18.000 tris por objeto.
- **Rig:** 10 famílias, 22–48 ossos.
- **Animações:** **495** (pacote base, montaria, territorial, voo, nado e as 4 habilidades oficiais de cada forma).
- **Exportação:** 16 GLB em `BLENDER/Criaturas/Blockouts/_Export/`, **validados por reimportação**: 1 esqueleto, ≤ 4 influências, ações conferidas.

**Detalhes e limitações:** `BLENDER/Criaturas/Blockouts/LEIA-ME-FINAL.md`. Capturas em `SCREENSHOTS/Criaturas_Final_2026_10_26/`.

**Não feito:**
- importação no Roblox (manual) e publicação das animações;
- teste no celular e em multiplayer;
- texturas assadas, LODs e colisores.

**Qualidade:** protótipo jogável. As animações são procedurais e algumas formas (Basilisco, Lagarto, Cérbero, Wyvern) ainda pedem ajuste anatômico.

## OPERAÇÃO CRIATURAS V2 (2026-10-27)
**Feito (Blender, verificado):**
- Anatomia:
  - Basilisco e Lagarto: cabeças reptilianas e membros.
  - Lagarto: cristais integrados.
  - Cérbero: cabeças escalonadas e maciças.
  - Wyvern: peito e coxas.
- Texturas assadas (cor + normal) nos 16 modelos.
- Pesos por regiões. Corrigido o bug dos dedos das asas dos voadores.
- Correção de contato dos pés.
- 507 ações auditadas por métrica: 224 aprovadas, 246 com ajustes, 37 para refazer.
- Custo por criatura e hitboxes em `review/<Especie>/final.json`.
- 16 GLB reexportados e validados por reimportação.
- Detalhes: `BLENDER/Criaturas/Blockouts/LEIA-ME-V2.md`.

**Não feito:** testes no Roblox e publicação de animações.
- A integração não importa GLB local.
- **O Studio abriu uma versão antiga do place (PlaceVersion 394) sem o trabalho de M7+, C1 e LOD_Distancia.** Nada foi alterado nela.
- Versão completa: `Documents/RPG_Roblox/BACKUPS/RPG_BKP_2026-10-26_C1_criaturas.rbxl`.

**Qualidade:** formas ainda lisas; animações procedurais. Não atende plenamente ao critério "não parecer manequim".

## Lobo Ancestral V3: piloto de refinamento (27/10/2026, em revisão, não finalizado)
- **Escopo:** só o Lobo Ancestral. As outras 15 criaturas não foram alteradas. A V3 usa arquivos próprios (`_v3`): `Lobo_Ancestral_refinado_v3.blend`, `Lobo_Ancestral_final_v3.blend`, `_Export/Lobo_Ancestral_v3.glb`, `review/Lobo_Ancestral/final_v3.json`.
- **Referências:** painel oficial do GitHub (`03_CREATURES/01-lobos-urso-leao.png`) e a silhueta de postura enviada pelo usuário.
- **Modelo:** `build/lobo_v3.py`.
  - Postura refeita: cabeça alta, pescoço a ~55°, tórax fundo e estreito, barriga recolhida, posteriores sob o corpo, cauda caída.
  - Peito e ombros menores. Músculos da coxa e da panturrilha reorientados (antes estavam girados ao contrário).
  - Antebraço mais grosso.
  - Cabeça: stop, arcada de predador, olhos âmbar amendoados, focinho afinando, orelhas triangulares.
- **Pelagem:** objeto separado com ~1.050 mechas de geometria (9 tris cada), 22 folhas de musgo e um atlas de 512×256. Os pesos são copiados da pele (`pesar_pelagem`).
- **Rig:** esqueleto `canideo_v3`, com os mesmos nomes de ossos e o mesmo número de animações (28).
- **Animação:** salto refeito em fases. Na corrida, o ombro passou a usar o úmero.
- **Custo:** 24.466 tris (corpo 12.000, pelagem 9.698, garras 2.432, olhos 336); GLB de 2,0 MB. Cada objeto fica abaixo de 20 mil tris.
- **Auditoria automática V3:** 8 Aprovada, 12 Pequenos ajustes, 8 Refazer.
  - Refazer: Corrida, MontadoCorrida, Arrancada, Deitar, Descanso, Levantar, Salto, Investida.
  - O salto continua "Refazer" na métrica (esticamento p99 de 3,4).
  - Nenhuma animação foi aprovada visualmente.
- **Problemas visuais ainda abertos:**
  - as mechas parecem penas ou escamas;
  - o focinho está volumoso de frente;
  - a máscara clara do rosto não aparece;
  - a vista frontal está estreita demais;
  - na Corrida os membros ficam embolados.
- **Incidente:** uma execução do pipeline sem a variável `CR_SUFIXO` regenerou `Lobo_Ancestral_final.blend` e `_Export/Lobo_Ancestral.glb` da V2 a partir da mesma entrada. O resultado é equivalente (6/16/6, 16.768 tris), mas os arquivos foram reescritos.
- **Bug corrigido nas capturas:** as capturas de pose de descanso da V2 saíram com a última animação auditada aplicada (cabeça baixa). `render_v3.py` agora zera a pose antes de capturar.
- **Roblox:** nada importado nem testado.

### Lobo Ancestral V4 (27/10/2026, aguardando aprovação)
- Ajustes sobre a V3 em `build/lobo_v4.py`. Arquivos: `_refinado_v4.blend`, `_final_v4.blend`, `_Export/Lobo_Ancestral_v4.glb`, `review/Lobo_Ancestral/final_v4.json`. A V3 foi preservada; as outras 15 criaturas não foram alteradas.
- **Pescoço:** ~45°, mais curto. A cabeça desceu 0,7 stud e o rig acompanhou.
- **Pelagem:** tufos de 2–3 fios finos que se abrem, direcionados pelo crescimento do pelo, no lugar das placas.
- **Transição do corpo:** flanco e prega do joelho; coxa menos esférica.
- **Rosto:** máscara creme, trufa e lábios escuros, contorno dos olhos; focinho e masseter mais finos.
- **Cauda:** pincel mais cheio no meio, com ponta escura.
- **Custo:** 30.456 tris (corpo 12.000, pelagem 15.688, garras 2.432, olhos 336); GLB de 2,5 MB. A pelagem pesa mais que na V3 (9.698).
- **Auditoria automática:** igual à V3 (8 / 12 / 8). As animações não foram alteradas, só regeneradas no novo rig.
- **Limitações abertas:**
  - a vista frontal está estreita;
  - os antebraços e canelas estão lisos;
  - as orelhas têm facetas visíveis;
  - nada foi testado no Roblox.

### Lobo Ancestral V5 (27/10/2026, aguardando aprovação; não considerada aprovada)
- **Referências consultadas:**
  - painel oficial `03_CREATURES/01-lobos-urso-leao.png`: corpo, cabeça, pelagem, patas, silhueta com humano e paleta;
  - RPG_02 §5 e §10: 5,5–7 studs no ombro, "esguio/atlético", padrões Cinza da Floresta e Marrom Selvagem.
- **Conflitos informados:**
  - "corpo robusto" (pedido V5) × "esguio/atlético" (RPG_02). Segui o painel: atlético, com o volume vindo da pelagem.
  - A silhueta do painel sugere cernelha acima de 7 studs; mantive 6,5 (oficial).
  - Não há vista frontal na referência.
- **Arquivos:** `build/lobo_v5.py` (V4 preservada). `_refinado_v5.blend`, `_final_v5.blend`, `_Export/Lobo_Ancestral_v5.glb`, `review/Lobo_Ancestral/final_v5.json`.
- **Alterações:**
  - Peito, ombros (deltoide), pescoço, coxas e crânio maiores.
  - Metacarpo e metatarso mais grossos; patas maiores, garras mais longas, dedo vestigial.
  - Olhos reposicionados na nova superfície, com pupila.
- **Pelagem:**
  - ~1.320 tufos de 2–3 fios, divididos em dois MeshParts: frente com 11.128 tris e trás com 10.852.
  - 20 samambaias e folhas.
  - Relevo de pelo assado na textura do corpo (normal + oclusão) a partir de ~26 mil fios de alta, que não são exportados.
  - Paleta das amostras do painel.
- **Custo:** 36.908 tris; GLB de 3,1 MB.
- **Auditoria automática:** 8 / 11 / 9. GuardarNinho passou a Refazer. Nenhuma animação aprovada visualmente.
- **Pendências:**
  - patas finas na vista frontal;
  - máscara creme do rosto pouco visível sobre a base escura;
  - pupila com brilho cinza;
  - fios largos no close;
  - custo maior que o da V4;
  - nada foi testado no Roblox.
- **Ajuste da V5 pedido pelo usuário (27/10):**
  - Cor cinzenta: base Cinza da Floresta; o creme virou cinza-claro.
  - Pelagem no corpo todo, inclusive pernas inteiras e cabeça.
  - Pernas mais grossas.
  - 24 tufos de vegetação: 159 folhas com pecíolo, nervura e dobra, em 3 verdes, mais 12 samambaias.
  - Corrigido um defeito do fio, cuja ponta terminava dentro da pele e deixava flancos e pernas aparentemente lisos.
- **Custo:** 48.129 tris. Pelagem em 3 MeshParts (frente 13,6 mil, trás 12,8 mil, pernas 6,8 mil); GLB de 3,8 MB. O custo é alto e um LOD por distância é necessário antes do uso em matilhas.
- **Auditoria:** 8 / 11 / 9.
- **Pelagem mais densa e com aspecto de casca (27/10):**
  - Densidade +40% e mechas 15% mais longas.
  - Nas regiões do corpo, as mechas viram tiras 35% mais largas.
  - O atlas ganhou fibras, fendas escuras e manchas de líquen.
  - Pelagem em 4 MeshParts: pescoço 10,5 mil, tronco 9,9 mil, trás 11,8 mil e pernas 7,7 mil tris.
- **Custo:** total de 54.832 tris; GLB de 4,3 MB. É alto: precisa de LOD antes de uso em matilha.
- **Pendências:**
  - o efeito de casca ainda é sutil (tom cinza-claro);
  - pelos espetados na testa;
  - nada foi testado no Roblox.
- **Correção de forma (27/10):** removido o caroço perto da cauda.
  - Os isquiotibiais eram uma esfera solta e havia calombos da tuberosidade isquiática e da crista ilíaca. Agora há nádega e raiz da cauda fundidas à garupa, e a suavização ficou mais forte.
  - Removida a "alça" diagonal do ombro (tubo da escápula e espinha); entraram trapézio e escápula achatada.
  - Verificado em render do corpo sem pelo (`review/Lobo_Ancestral/corpo_*.png`).
  - Custo: 54.642 tris; auditoria 8 / 11 / 9.
- **Lobo Ancestral, ajuste final pedido (27/10):**
  - Cabeça 12% maior (transformação `M_CAB` no `lobo_v5.py`; rig e máscara acompanham).
  - Juba perto da cabeça mais curta.
  - Pelo claro mais discreto e raro nas pernas, mais deitado no peito e no antebraço.
  - 10 ossos secundários `Pelo_*` (juba E/D, peito, nuca, ventre E/D, bochechas E/D, coxas E/D), sem uso no corpo.
  - As pontas dos tufos seguem esses ossos (12.759 vértices) e o balanço está gravado nas 28 animações (`balanco()` no pipeline).
  - 42 ossos; 54.125 tris; auditoria 8 / 14 / 6.
  - O custo de FPS do balanço não foi medido; isso exige o Studio.

## Master Prompt — Grupo 1: Lobo Ártico (27/10/2026, aguardando aprovação de anatomia)
- **Arquivos:** `build/lobo_artico.py` reaproveita a técnica do `lobo_v5` por importação, sem alterar o Ancestral. `Lobo_Artico_refinado_v5.blend`, `Lobo_Artico_final_v5.blend`, `_Export/Lobo_Artico_v5.glb`. A V2 está preservada.
- **Modelo:**
  - massas 8–12% maiores que no Ancestral;
  - patas de neve largas;
  - pelagem branca e cinza 30% mais longa e ~8% mais densa, sem vegetação;
  - olhos azul-gelo.
- **Rig e animações:** rig canino com ossos de pelo (42), 28 animações. Auditoria 8 / 14 / 6.
- **Custo:** 55.896 tris (corpo 12 mil, pelagem 41 mil em 4 MeshParts); GLB de 4,8 MB.
- **Prancha:** `review/Lobo_Artico/Prancha_Lobo_Artico_v5.png`.
- **Diferenças ainda abertas frente à referência:**
  - a referência é mais horizontal, maciça e comprida, com cabeça mais baixa e juba mais volumosa;
  - na face, os pelos estão espetados demais;
  - as orelhas não têm pelo;
  - o custo de tris é alto.
- **Pelagem volumosa nos dois lobos (27/10):**
  - Subpelo: a superfície do corpo é inflada pela espessura do pelo em cada região, com mechas alongadas no sentido do crescimento (`volume_pelo` em `lobo_v5.py`; fator 1,4 no Ártico).
  - Por cima, mechas grossas de seção arredondada (`mecha`), em menor número; nenhuma no rosto.
  - A modelagem foi feita no Blender aberto (MCP). O pipeline de bake, rig e animações rodou em segundo plano: no Blender aberto, os operadores perdem o contexto da janela depois de carregar outro arquivo. Os resultados foram abertos na janela para inspeção.
  - Ancestral: 62.596 tris, auditoria 7 / 12 / 9.
  - Ártico: 66.118 tris, auditoria 7 / 12 / 9.
  - **Defeitos vistos:**
    - no Ártico, um grupo de mechas sobe em crista acima da cabeça;
    - algumas mechas ainda lembram penas sob luz clara;
    - o custo subiu (precisa de LOD).
- **Mechas macias (27/10):**
  - Ponta arredondada, metade da elevação, leque fechado, nenhuma mecha crescendo para cima, bochecha só na parte baixa.
  - Os espetos sumiram, mas as mechas opacas agora lembram penas sobrepostas.
  - No Ártico persiste uma mecha longa saindo da nuca, atrás da cabeça.
  - Ancestral: 68.088 tris. Ártico: 73.578 tris.
  - **Conclusão técnica:** com geometria opaca, a pelagem alterna entre "espetada" e "penas". Pelo realista com bordas suaves em tempo real costuma usar cartões com transparência (alpha). O Roblox aceita SurfaceAppearance com AlphaMode = Transparency, mas a ordenação e o custo precisam ser validados no Studio. Decisão pendente com o usuário.
- **Cartões de pelo com transparência (27/10), teste aprovado pelo usuário:**
  - `CARTOES=True` no `lobo_v5.py`: faixas curvas e afiladas sobre o subpelo, com um atlas 1024² de tufos (4 variantes × 2 cores, cerca de 110–170 fios desenhados por tufo, alpha recortando a forma).
  - Material DITHERED, sem culling de face traseira.
  - Folhas, samambaias e orelhas ficaram num objeto opaco separado (`PelagemFolhas`).
  - O rosto passou a ter pelo (região `cabeca`) e o colar facial ficou mais longo. A crista da nuca foi removida (nuca curta e voltada para baixo).
  - Ancestral: 35.851 tris (antes 68 mil). Ártico: 32.454 tris. Texturas de 12,6 MB; auditoria 7 / 12 / 9.
  - **No Roblox (não testado):** confirmar se o Import 3D cria SurfaceAppearance com AlphaMode = Transparency e ligar DoubleSided nos MeshParts de pelagem. Verificar artefatos de ordenação e o custo de FPS.
  - **Defeitos vistos no Ártico:** calombo sob a mandíbula (subpelo da bochecha) e orelhas lisas.

## Produção autônoma V5 das 15 criaturas (27/10/2026): concluída tecnicamente, aguardando avaliação
- Relatório completo em `BLENDER/Criaturas/Blockouts/RELATORIO-PRODUCAO-V5.md`.
- O Lobo Ancestral não foi alterado.
- **Ártico:** `lobo_artico.py` com pelo nas orelhas e sem o calombo da mandíbula.
- **Demais 14:** `revest.py` aplica pelo (subpelo e cartões com alpha) ou placas sobrepostas, guiado pelo esqueleto de cada espécie. O pipeline usa `CR_SUFIXO=_v5`, e a lógica dos lobos ficou isolada na flag `LOBO`.
- Os 15 GLB `_Export/<Esp>_v5.glb` foram validados por reimportação no Blender (`review/validacao_glb_v5.json`): esqueleto, ações e imagens presentes, nenhuma malha acima de 20 mil. Custo entre 29,8 e 77,6 mil tris.
- Pranchas comparativas em `review/<Esp>/Prancha_<Esp>_v5.png`.
- **Estados:**
  - anatomia = silhueta V2 (sem nova escultura);
  - animações = regeneradas pelo código V2 e auditadas apenas numericamente;
  - Roblox = não testado;
  - criador = não aprovado.

