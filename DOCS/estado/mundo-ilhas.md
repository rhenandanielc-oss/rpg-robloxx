# Mundo: Ilhas flutuantes (M9)

Voltar ao índice: [[PROJECT-STATE]]

## OPERAÇÃO M9 — ILHAS FLUTUANTES EXPLORÁVEIS (2026-10-26)
**Base documental:** RPG_01 prevê nas Montanhas Altas "ilhas flutuantes pontuais para criaturas voadoras repousarem e serem exploradas". Para a Tundra os documentos não citam ilhas → **nenhuma ilha na Tundra**; nenhuma em outros biomas. Não é bioma; sem templos, santuários, pontes nem IA de criaturas.
**Backup:** `Proto_Restore/Backup_M9_Ilhas` (TerrainRegion da caixa de cada ilha antes da escultura, com `Canto`; regravar = colar backup + esculpir, idempotente). Gerador `Proto_Restore/IlhasFlutuantes` (forma por lóbulos com ruído angular; topo com relevo, cume, anel de rochas de abrigo e pousos aplainados; base irregular em quilha com sulcos de fratura e espigões pendentes; nunca encosta na montanha: folga mínima de 25 sobre o terreno).
**Ilhas (`workspace.Montanhas_Altas.Ilhas_Flutuantes`):**
| Ilha | Centro / topo | Terreno | Vegetação | Função e marcadores | Acesso (atributo `Acesso`) |
|---|---|---|---|---|---|
| Ilha dos Ventos Altos (principal) | (−4.380, −1.250), topo ~812, base ~569 | 247.253 células, 3 lóbulos | 14 pinheiros (0,32–0,5), 30 arbustos, 40 capins, 12 flores | Pouso do Dragão das Montanhas (r 40, campo aberto), pouso/acesso da Wyvern, abrigo entre rochas, mirante, aproximação aérea leste | **Acessível mediante habilidade futura (voo)**: a escalada a pé pelo flanco travou em y≈416 no teste em Play. |
| Ilha do Bosque Suspenso | (−4.040, −360), topo ~560 | 69.636 células | 20 pinheiros, 14 arbustos, 25 capins, 8 flores | Campo de pouso, crista de pouso e abrigo, descanso | **Acessível agora (a pé + salto curto)** — ver teste. |
| Terraço de Pedra | (−4.300, −2.300), topo ~1.080 | 49.456 células, rochoso com neve | 5 arbustos, 10 capins | Pouso e decolagem (r 45), ninho elegível da Wyvern (regra oficial: poucos ninhos, rotação 30–60 min), observação sul | **Reservada para criaturas voadoras** |
Ninho elegível só no Terraço (não em todas as ilhas). Nuvens locais leves: 2 emissores por ilha, abaixo do topo (Ventos Altos 722, Bosque 480, Terraço 985). Vegetação e marcadores em modelos `Persistent`.
**Teste de acesso (Play, servidor, sem teleporte no trecho testado):** personagem seguiu os pontos do pathfinding desde a Vila (−3.350, 207, −760) até (−4.205, 532, −336) em 426 s (travou 33 vezes — rota íngreme), seguiu até o ponto de salto (−4.200, 571, −397) e saltou para leste, parando em (−4.089, 565, −385), sobre a ilha (coluna sólida 564→456, ar abaixo). Os pontos altos alcançáveis a pé a partir da Vila foram ~617, 584 e 573 — por isso a ilha 2 foi movida para junto do último. As capturas usaram teleporte só para posicionar câmera/personagem.
**Auditoria pós-construção (Edit):** vegetação das ilhas 178/178 apoiada (0 flutuando, 0 enterrada); topo sem furos em 13.302 colunas; espessura mínima 8 na borda (28 no Terraço); vão mínimo de 24 até o terreno e 0 pontos de contato com a montanha.
**Defeito encontrado e corrigido:** o topo do Terraço ficava branco (neblina): o `Montanhas_Neblina` lançava raios de 1.400 que não alcançavam o chão sob a ilha e empilhava 13 bancos de névoa sobre ela → ilhas excluídas e raio de 3.000 (0 bancos no topo depois; capturas antes/depois).
**Desempenho (Play/PC):** topo do Terraço 57,1 FPS (pior quadro 63 ms); topo da principal 56,7 FPS (64 ms); memória total do Studio em Play ~20,06 GB (Studio aberto há muitas horas com Edit+Play; não atribuído às ilhas); 260.100 instâncias no cliente. Carregamento das ilhas não medido separadamente.
**Limitação visual:** a neblina das Montanhas (densidade 0,5 — identidade do bioma, não alterada) apaga as ilhas a partir de ~600–700 studs; de perto e de média distância a silhueta lê bem.
**Mapa:** `SCREENSHOTS/Mapa_Resumo_Mundo.png` com marcadores aéreos discretos das 3 ilhas (altitude do topo e acesso) + cópia em `SCREENSHOTS/M9_Ilhas_Flutuantes/Mapa_Resumo_Mundo_M9.png`; versão anterior `Mapa_Resumo_Mundo_M8.png`.
**Capturas:** `SCREENSHOTS/M9_Ilhas_Flutuantes` (13): vista do vale, lateral, base rochosa suspensa, topos, Bosque Suspenso, Terraço, área de pouso, composição com nuvens, vista de montanha, panorama do mirante.
**Não verificado:** celular, multiplayer, impostores/streaming no servidor publicado, Blender MCP (não usado; vegetação clonada das Montanhas).

