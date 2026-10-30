# TASKS — checklist de execução (não de intenções)

## Convenções
- `[ ]` não iniciado / não validado.
- `[~]` em andamento (convenção textual, não marcador GitHub padrão; prefira `[ ]` com nota).
- `[x]` somente com implementação, evidência, teste e aprovação do escopo.
- O planejamento está aprovado em diversos aspectos, mas **NENHUMA tarefa abaixo foi comprovadamente implementada neste Studio**.

## M0 — Inspeção sem alterações (PRIMEIRA TAREFA A AUTORIZAR)
- [ ] M0.1 Confirmar projeto correto, caminho, ID e ambiente Roblox Studio.
- [ ] M0.2 Inventariar Workspace/Terrain, biomas, água, iluminação, vegetação e pontos de interesse.
- [ ] M0.3 Inventariar scripts, serviços, pastas, remotes, models e dados persistentes.
- [ ] M0.4 Verificar erros e desempenho sem criar ou modificar objetos.
- [ ] M0.5 Relatar diferenças entre Studio e documentos e recomendar primeiro bloco seguro.

## M1 — Dados e estrutura
- [x] M1.1 Aprovar arquitetura de dados e salvamento. (Aprovada em 2026-10-19; ver `DOCS/M1.1-DATA-ARCHITECTURE.md`. Backup `RPG_BKP_2026-10-19_pre-M1.rbxl` confirmado pelo usuário.)
- [x] M1.2a Perfil, sessão, moeda de jogo, inventário (40 espaços) e concessões idempotentes. (Aprovado pelo usuário em 2026-10-19 após análise; 31/31 testes com DataStore falso e playtest sem erros do projeto. Multi-servidor e DataStore real NÃO testados; ver PROJECT-STATE.md.)
- [ ] M1.2b Persistência de criaturas (depende do catálogo do M3.1).
- [x] M1.3 Implementar proteção básica contra duplicações e operações inconsistentes. (Validado pelo usuário em 2026-10-19; V1–V5 implementadas, 47/47 testes com DataStore falso. Multi-servidor e DataStore real NÃO testados; ver PROJECT-STATE.md.)

## M2 — Mundo e ambiente
- [ ] M2.0 Protótipo isolado Floresta Ancestral (X 1200–1600, Z −200–200; descartável). A terreno: implementado, aguardando avaliação. B vegetação (3–5 árvores de amostra), C água, D ambientação: não iniciados. Não conta como M2.2–M2.4.
- [ ] M2.1 Validar topologia/escala e oito regiões no projeto existente.
- [ ] M2.2 Construir macroterreno regional aprovado, por lotes reversíveis.
- [ ] M2.3 Água, transições ambientais e caminhos de exploração.
- [ ] M2.4 Vegetação regional, árvores com vento otimizado, clima e iluminação.
- [ ] M2.5 Vilas, ruínas, instalações e entradas físicas de dungeons. (Nota: Fase B do primeiro terço da Floresta Ancestral construída e testada em Play em 2026-10-20: vila, 2 travessias, ruína, altar, acampamento, 2 mirantes, placas, integração do núcleo — aguardando avaliação; interiores, entradas de dungeons e demais regiões NÃO feitos; não marcado [x].)
- [ ] M2.6 Testes de desempenho desktop e mobile.
- (Nota 2026-10-22: **Montanhas Altas** — 2º bioma — construído a oeste da floresta, X −5800…−380 × Z −3500…1800, regiões M0–M7 com relevo, rios, lagos, cachoeira, vila, 10 cavernas, santuário, trilhas e marcadores. Testado em Play só no Studio/PC: 9/9 trechos de pathfinding, 10/10 cavernas a pé, FPS 58–59. Sem caminhada contínua completa, sem teste em celular, 1 rota sem caminho, aguardando avaliação do usuário. Nenhum item marcado [x]. Detalhes em PROJECT-STATE.md.)
- (Nota 2026-10-22 — M2-REFINO FINAL: relevo V2 no estilo da referência visual, Cachoeira dos Três Degraus, ambiente regional, 12 cavernas V2, 21 rotas sobre terreno real, vegetação V2. Play/PC: 21/21 rotas, 11/11 cavernas a pé, caminhadas reais por trechos. FPS real e celular não medidos. Aguardando avaliação; nada marcado [x].)
- (Nota 2026-10-22 — Montanhas V3 NATUREZA: picos colossais em hierarquia, transição contínua floresta→montanhas, rios ao nível das margens até o mar, estruturas artificiais retiradas (reserva), covil natural do dragão no Cume do Vento, vegetação por altitude, vento por altitude. Play/PC: 18/19 trilhas, 11/11 cavernas, 4/4 vaus a pé. FPS real/celular não medidos. Nada marcado [x].)
- (Nota 2026-10-22 — Montanhas V4 refino: ligação sem areia, pinheiros novos 3x mais altos (2.276), vento por altitude, subida natural ao covil testada a pé até o topo, rios rasos/fundos, música/ambiente/neblina por bioma. Pathfinding da subida falha; nada marcado [x].)
- (Nota 2026-10-22 — Atmosfera V5: perfis de luz/neblina/nuvens por bioma, playlists calmas por bioma + ambiências, nuvens nos picos, pinheiral mais claro e menos denso (1.636). Testado em Play/PC; música escolhida sem audição — validar. Nada marcado [x].)
- (Nota 2026-10-22 — Correções V6: mar de nuvens no pico, 74 buracos tapados, rios 2x (montanhas e floresta) e no nível da terra, pinheiros realistas PBR com vento, trilhas principais + marcos da escalada, floresta ensolarada. Testado em Play/PC. Nada marcado [x].)
- (Nota 2026-10-22 — V7: chão verde único nas Montanhas (sem manchas de seixo/lama/terra/arenito), 20 mil flores/capins, clareiras de terra da floresta viraram grama, troncos caídos/pedras grandes/monólitos/acampamentos retirados para reserva. Play/PC sem erros; FPS/celular não medidos. Nada marcado [x].)
- (Nota 2026-10-22 — V7b: 10.055 placas de manchas retiradas de todos os biomas, chão em um só tom de grama no mapa todo, raios de sol entre as copas e manchas de sol no chão da floresta. Play/PC sem erros; FPS/celular não medidos. Nada marcado [x].)
- (Nota 2026-10-22 — V7c: árvores/raízes flutuando corrigidas, sem areia e sem chão branco, pedra lisa, pedras soltas retiradas, 17 pontes alargadas 3x + 18 novas, ninho gigante no Cume do Vento, 11 pousos de dragão/wyvern, 11 tocas de urso nas cavernas. Pathfinding 18/18 nas pontes novas. FPS/celular não medidos. Nada marcado [x].)
- (Nota 2026-10-22 — V7d: neblina aparente nas Montanhas (atmosfera + bancos de névoa locais), 7 picos elevados naturalmente sem plataformas, ninhos em ombros/nichos naturais, rios 5x mais fundos (mediana ~70). Play/PC sem erros; FPS/celular não medidos. Nada marcado [x].)
- (Nota 2026-10-22 — V8 habitats (RPG_01/RPG_02): ursos retirados das Montanhas (cavernas preservadas e reclassificadas), ninho do Cume do Vento reposicionado + poleiro, 3 cavernas paramétricas de dragão, nichos dos picos restaurados por suavização, 5 ninhos de Wyvern na escala oficial, marcadores de voo/ninho/território para a fase de criaturas (sem IA). Play/PC: 11/11 cavernas, escalada 43/43. FPS/celular não medidos. Nada marcado [x].)
- (Nota 2026-10-22 — V9 floresta: pedras/arcos/troncos retirados, 16 pontes antigas refeitas + 4 novas (72/72 pontas em terra), 206 ilhotas removidas, margens sem faixa de terra, trilhas repintadas contínuas, 41 placas de direção, raios só sob as copas. Play/PC 0 erros; FPS/celular não medidos. Nada marcado [x].)

- (Nota 2026-10-22 — M3 ambiental: **Pântano Nebuloso** construído a leste da Floresta (terra x≈3.850–8.250, z≈−2.000–2.000): 8 regiões, rios/canais/lagos com foz no mar, 1.108 árvores de família própria, 6.039 plantas, 14 trilhas, 5 travessias, ruínas afundadas, Árvore-Mãe no Coração, habitats de Basilisco e Crocodilo Primordial (marcadores), clima/música/névoa próprios. Play/PC: 0 erros, áudio 8/8, travessias 5/5, pathfinding 128/134. FPS do Studio 14–15 em todos os biomas (não representativo); celular não testado. Nada marcado [x].)
- (Nota 2026-10-22 — M3b correções: raios de sol só na floresta e estendidos ao céu, rios/riachos do pântano fundos (16–38, poços-toca até 54) com lama rasa preservada, árvores flutuantes corrigidas + 380 mangues de folha lisa, névoa densa interna + véu externo, 3 pontes largas novas/refeitas (0 trechos de trilha sobre água funda sem estrutura), marcadores estratégicos do Crocodilo Primordial (11 territórios, 7 tocas, 10 corredores), placas da floresta 39→13 com Pântano, 25 paredes invisíveis que bloqueavam floresta↔pântano retiradas. Play/PC: 0 erros do projeto, pathfinding 7/7, caminhada pela costura 3/3. FPS/celular não medidos. Nada marcado [x].)
- (Nota 2026-10-22 — M3c: árvores/raízes flutuantes medidas por raios sob as raízes e corrigidas (0 restantes em 6.511 árvores), Mangue_2 deitado trocado, 500 árvores secas trocadas por Freixos, paredes d'água eliminadas (12.733 voxels), lago elevado da vila removido, sobreposições da vila resolvidas, divisas/fendas/degraus suavizados, rios rasos do pântano 5× mais fundos com passagens elevadas nas trilhas. Play/PC: 0 erros, pathfinding pântano 84/84; PathfindingService falha em zonas da floresta onde se anda normalmente (pendente). Nada marcado [x].)
- (Nota 2026-10-22 — M3d: árvores assentadas pela base geométrica do tronco (6.510), água do pântano em nível único (fim das faixas de pedra), 781 montículos e ilhotas vazias removidos, galhos secos do pântano trocados por mangues, ninhos submersos realocados. Play/PC: 0 erros, pântano 84/84. Nada marcado [x].)
- (Nota 2026-10-23 — M4 ambiental: **Planícies Douradas** construídas ao sul da costa da Floresta/Montanhas (terra x≈−3.900…2.550, z≈costa…6.250): 8 regiões, Rio Dourado + 3 afluentes + 3 lagos ligados ao mar, 5 vaus, capim dourado 3D com ondas de vento no cliente, material de capim próprio, 289 acácias/olmos + Acácia Monumental, 14 trilhas, 7 POIs, habitats de Leão Solar e Búfalo Colossal (marcadores), clima e música próprios. Play/PC: 0 erros, pathfinding 66/66, caminhadas reais 47/47, FPS 58 no Studio. Celular não testado; sem backup novo. Nada marcado [x].)
- (Nota 2026-10-23 — M4.1 refino das Planícies: capim refeito com malhas PBR de lâminas finas (24 variações, altura máx. 4,5 < personagem), solo campestre com manchas verdes e cascalho nas margens, relevo ondulado aditivo, 92 árvores retiradas das áreas secas + 18 ribeirinhas + 3 acácias monumentais, atmosfera sem névoa azulada, vento em ondas medido (1,6° médio, não sincronizado). Play/PC: 0 erros, 66/66, FPS 57–58. Place não salvo pela integração; cópia reversível em `Backup_Planicies_M4`. Nada marcado [x].)
- (Nota 2026-10-23 — M4.2: poças soltas eliminadas (piso mínimo da terra), divisões da costa corrigidas (costa suavizada no gerador), afluentes 3× mais largos e 4× mais fundos (medido: ~72 × 44), mar aberto estendido sem parede d'água, trilhas recalculadas. Play/PC: 0 erros, 67/68, FPS 57. Nada marcado [x].)
- (Nota 2026-10-23 — M4.3: pop-in da vegetação corrigido — árvores/POIs das Planícies em streaming Persistent (193/193 no cliente), capim em 3 camadas perto/médio/longe até ~600 studs, transições Grass↔LeafyGrass pontilhadas, atmosfera mais quente. Play/PC: 0 erros, FPS 54–56. Terreno além de ~1.200 studs depende de `StreamingTargetRadius` (manual). Celular não testado. Nada marcado [x].)
- (Nota 2026-10-23 — M4.4: habitats ecológicos de Búfalo Colossal (4 manadas) e Leão Solar (4 bandos) nas Planícies — pastagens, descanso, filhotes, água, rotas, fuga, carga, mirantes, sombra, caça, emboscadas, aproximação + 64 cenas de interação; API `ServerStorage/Ecologia/EcologiaFauna`. Pathfinding agente grande 79/79, caminhadas 6/6. Sem IA/animais. Nada marcado [x].)
- (Nota 2026-10-23 — M5 ambiental: **Tundra Congelada** ao norte da Floresta/Pântano (terra x≈−2300…4900, z≈−2350…−7050) ligada por istmos à Floresta e às Montanhas; 8 regiões T0–T7, lago congelado + Rio do Degelo até o mar + 4 riachos congelados, 13 picos, glaciar, desfiladeiro, planalto, 2 cavernas exploráveis, 2.470 árvores Persistent, 15 trilhas, habitats de Lobo Ártico e Dragão Glacial (oficiais) + fauna provisória, clima/neve/vento/música próprios. Play/PC: 87/87 trechos, caminhadas reais 8/8 (cavernas e istmos), árvores 2.470/2.470 no cliente, FPS 57–59. Celular não testado; place não salvo pela integração. Nada marcado [x].)
- (Nota 2026-10-23 — M5.1 Tundra: árvores corrigidas (pivô na base; 0 flutuando/enterradas) + 104 em bosques (2.572); faixa de terra no rio removida (883 colunas); 2 tocas de Lobos baixas acessíveis a pé; 3 covis de Dragão Glacial altos com plataforma de pouso em contraforte natural (dimensões do dragão PROVISÓRIAS); ecologia por altitude; nevasca branca com vento e som + véu de névoa visto de fora. Play/PC: tocas e covis percorridos, FPS 57–58, 4 biomas intactos (só transições intencionais). Celular não testado; place não salvo pela integração. Nada marcado [x].)
- (Nota 2026-10-23 — M6: **Deserto de Cristal** a sudeste (x≈2.900–8.300, z≈2.500–7.400), ligado às Planícies por istmo; 8 regiões D0–D7 (dunas, cânions com mesa, oásis com nascente, campos de cristal, gargantas, cavernas cristalinas, cratera monumental), 2 rios até o mar + 2 leitos secos, 90 aglomerados de cristal, 118 árvores, 6 trilhas, 4 sistemas de cavernas, habitats oficiais de Escorpião Colossal e Lagarto Cristalino, tempestade de areia ocasional, música/sons licenciados. Play/PC: pathfinding 37/37, caminhadas reais 3/3, FPS 57–58. Celular não testado; salvar com Ctrl+S. Nada marcado [x].)
- (Nota 2026-10-26 — M7.1/M7.2: a M7 não estava salva no place; Costas Selvagens reconstruídas já refinadas: costa irregular com enseadas/pontais, falésias com ravinas, ilhas com identidade (atol, tômbolo, arco), oceano em 4 zonas com paredões e fossa, recifes/kelp/gorgônias, 5 cavernas (2 novas submersas/arco), habitats oficiais por zona, visão subaquática por profundidade. Play/PC FPS 49–57. Incidente de 5.318 modelos movidos foi revertido. Celular não testado. Nada marcado [x].)
- (Nota 2026-10-26 — M7.3: pilares marinhos esculpidos em 3D (erosão, entalhe, estratos), praias com berma/dunas/areia compactada, rios com barranco e praia fluvial, 13 formações submersas + 2 arcos (recife e abismo), Poço Azul e Crista das Sentinelas, árvores segmentadas com vento na copa, auditoria de ar sob água/vazio sob a plataforma. Play/PC FPS ~58. Nada marcado [x].)
- (Nota 2026-10-26 — M8: Terras Corrompidas construídas ao sul (8 regiões T0–T7, ligadas por terra às Planícies, Deserto e Costas), 4 cavernas, habitats do Cérbero Sombrio e Dragão Sombrio (marcadores, sem IA), clima/som próprios, 5 trilhas; auditoria dos 8 biomas (448 flutuantes, 76 enterrados, 86 colunas de água sobre ar corrigidos); mapa de 8 biomas. Celular/multiplayer não testados. Nada marcado [x].)
- (Nota 2026-10-26 — operação "M8.1" do usuário (≠ tarefa M8.1 de QA abaixo): auditoria global dos 8 biomas — 66 paredes invisíveis da Floresta retiradas, 48 marcadores de cavernas das Montanhas e ~280 marcadores dentro da rocha corrigidos, 4 ninhos de aves desenterrados, costuras (Costas x=8.000, Terras x≈2.320) e 6 furos sem fundo preenchidos (lago x 3.040–3.600 e fenda x 7.984), música nas junções, aglomerados das Terras em Persistent. Varredura de furos em grade 16: 0 internos. Celular/multiplayer não testados. Nada marcado [x].)
- (Nota 2026-10-26 — auditoria de erros: 0 erros de script/console, testes M1 47/47, tour 8 biomas ok; backdoor de modelo gratuito achado e isolado (palmeira PalmD em ServerStorage); novo `LOD_Distancia` no cliente (+25–50% FPS nos testes A/B, desligável por `workspace.LOD_Ativo`); 1 árvore e 1 capim dentro d'água retirados, 1 luz e 3 itens soltos corrigidos. Celular/multiplayer não testados. Nada marcado [x].)
- (Nota 2026-10-27 — Criaturas V2 no Blender: texturas assadas, pesos por regiões, anatomia de 4 espécies, auditoria de 507 ações (224 A / 246 P / 37 R). Testes no Roblox bloqueados: importação manual e Studio com versão antiga do place. Nada marcado [x].)
- (Nota 2026-10-26 — Criaturas refinadas, finalizadas, com rig e animadas no Blender: 16 GLB validados por reimportação, 495 animações (base, montaria, territorial, voo, nado, habilidades). Falta importar e testar no Roblox (manual). Nada marcado [x]. Ver `BLENDER/Criaturas/Blockouts/LEIA-ME-FINAL.md`.)
- (Nota 2026-10-26 — Operação Creature Blockout: biblioteca de silhuetas das 16 formas oficiais em `BLENDER/Criaturas/Blockouts` (16 construídas, 0 reaproveitadas). Gates world_gate: Leão 0,821, Lobos 0,836/0,841, Urso 0,802, Búfalo 0,799; as demais com comparação visual. Aguarda avaliação do usuário antes do refinamento. Nada marcado [x].)
- (Nota 2026-10-26 — Operação C1 (criaturas oficiais, sem IA/combate):
  - Catálogo das 13 espécies / 16 formas / 48 padrões em `Biblioteca_Criaturas.Catalogo`.
  - Lobo Ancestral e Lobo Ártico prontos no Studio (rig Motor6D, 13 animações, 3 padrões, testados em Play/PC).
  - 10 formas feitas no Blender (3 Dragões, Wyvern, Serpente Marinha, Leviatã Jovem, Crocodilo Primordial, Basilisco, Lagarto Cristalino, Escorpião Colossal): GLB/FBX com esqueleto, animações e 3 padrões, validados por reimportação no Blender. **Ainda falta importá-los manualmente no Studio e validar lá.**
  - Urso provisório (estilizado); Cérbero provisório no Studio (base do lobo + 3 cabeças, 13 animações testadas, aparência aguardando aprovação); Leão e Búfalo não iniciados.
  - Celular/multiplayer não testados. Nada marcado [x]. Ver `DOCS/CRIATURAS-C1-MATRIZ.md`.)
- (Nota 2026-10-26 — M9: 3 ilhas flutuantes só nas Montanhas Altas (RPG_01; Tundra sem base documental) — Ventos Altos (voo futuro), Bosque Suspenso (acessível a pé + salto, testado em Play) e Terraço de Pedra (só voadores, único ninho elegível de Wyvern); auditoria 0 flutuantes/0 contatos; FPS ~57. Celular/multiplayer não testados. Nada marcado [x].)
- (Nota 2026-10-25 — M7: **Costas Selvagens** a leste do Deserto/Pântano (continente x≈8.000–12.000, ilhas, Abismo Azul até x 17.000), 8 regiões C0–C7, canal/estuário/rio com vaus, 3 cavernas marinhas, 1.682 árvores + 2.225 arbustos, habitats oficiais de Serpente Marinha e Leviatã Jovem, chuva ocasional e visão subaquática por profundidade; auditoria dos 7 biomas (árvores, terreno, água, cavernas). Play/PC: trilhas 25/25, cavernas 14/14, acesso por terra 10/10, FPS 55–58. Celular não testado. Nada marcado [x].)
- (Nota 2026-10-25 — gruta de gelo cristalina (M6.5/M6.6) e clima quente do deserto ("M6.3" do usuário): só iluminação/atmosfera no cliente, por região; Play/PC testado nos 5 biomas vizinhos. Celular não testado. Nada marcado [x].)
- (Nota 2026-10-25 — operações de bioma "M6.1/M6.2" (≠ tarefas M6.1/M6.2 de chefes abaixo): deserto refinado no gerador (megadunas variadas, gargantas em barbatanas, ravinas, cânions variáveis, oásis com beira úmida, cristais com base de rocha, cavernas com paredes curvas e colunas em ampulheta, tempestade com chegada/pico/dissipação); falhas de terreno varridas no mapa todo (349 vãos preenchidos, 19 lâminas removidas, 0 costuras); Gruta do Gelo Azul com 68 formações (malhas IA do Roblox, não Blender) e luz azul. Play/PC: trilhas 125/125, rotas 10/10, FPS 48–60. Celular não testado. Nada marcado [x].)
- (Nota 2026-10-23 — M5.2b: canais finos e bordas retas de água alisados em 68 áreas (módulo CostaSuave), bolsões/lajes/grama submersa corrigidos (ReparoAgua), 3 pontes com água restaurada, fundo da água escondido por turbidez perto+longe, rasteira da Tundra até 320 studs (FPS 58). Celular não testado. Nada marcado [x].)
- (Nota 2026-10-23 — M5.2: correção de terra/água em todo o mundo (sulcos, ilhotas, buracos, leito em quadrados); névoa da Tundra mais densa + véu sobre o mar; névoa/tempestade baixa nas cavernas; árvores de todos os biomas Persistent (FPS caiu para 43–57 — medir no celular); rios da Tundra largos e fundos (Degelo alargado + Pinheiral e Desfiladeiro novos, vaus nas trilhas, rotas aquáticas marcadas); visão subaquática por bioma/profundidade; 287 árvores de margem corrigidas. Nada marcado [x].)
- (Nota 2026-10-23 — M5.1b: véu da Tundra opaco visto de fora (54 bancos, 3 camadas, altura pelo terreno, desliga perto do jogador — corrige o "bloco branco" na borda); mapa-resumo do mundo em `SCREENSHOTS/Mapa_Resumo_Mundo.png` com passagens por terra medidas. Celular não testado. Nada marcado [x].)

## M3 — Criaturas e combate
- [ ] M3.1 Reconciliar fichas oficiais do documento RPG_02.
- [ ] M3.2 Combate misto, elementos, habilidades e testes PvE/PvP.
- [ ] M3.3 Evolução, crescimento, companhia e persistência.
- [ ] M3.4 Criaturas premium, probabilidades do ovo e Serpente Abissal.

## M4 — Inventário e economia
- [ ] M4.1 Inventário, materiais, coleta e crafting.
- [ ] M4.2 Auditar e configurar as 75 receitas e variantes regionais iniciais.
- [ ] M4.3 Aprimoramentos, comércio, taxas e proteção de recursos.

## M5 — Missões e história
- [ ] M5.1 Diário, pistas e progresso individual/cooperativo.
- [ ] M5.2 Implementar 48 missões principais e campanha central.
- [ ] M5.3 Auditoria de spoilers sobre origem da entidade.

## M6 — Chefes e dungeons
- [ ] M6.1 Grupos 1–4, instâncias, retorno, checkpoints e ressuscitação individual.
- [ ] M6.2 Chefes obrigatórios, contadores Lendários e recompensas.
- [ ] M6.3 Oficiais, dungeon final e sequência narrativa protegida.

## M7 — Loja e monetização
- [ ] M7.1 Aprovar cadastros, tipos de compra e políticas antes de ativar loja.
- [ ] M7.2 Concessão persistente e idempotente dos 10 produtos.
- [ ] M7.3 Divulgação e elegibilidade das chances reais do ovo, sem duplicação nos 3 primeiros.
- [ ] M7.4 Testes de restauração, falha de compra e anti-pay-to-win.

## M8 — QA e publicação
- [ ] M8.1 Testar regressões de todos os sistemas.
- [ ] M8.2 Validar acessibilidade, desempenho e persistência.
- [ ] M8.3 Alfa fechado, beta e correções.
- [ ] M8.4 Autorizar lançamento público após critérios aprovados.
