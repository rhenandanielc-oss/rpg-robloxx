# Medição de desempenho do rpg_roblox — 20/11/2026

Somente leitura (placeId 114230639394991): contagens em Edit e depois medição em Play. Nada foi alterado nem salvo. Mobile não foi testado.

## Números medidos
| Item | Valor |
|---|---|
| Instâncias no total | 642.702 |
| Workspace | 373.061 (Floresta 152.917, Montanhas 107.752, Pântano 35.963, Corrompidas 30.427, Costas 26.436, Tundra 10.504) |
| ReplicatedStorage (vai para TODO cliente ao entrar) | 109.336, sendo **109.137 em `Animacoes_LoboArtico`** (106.249 Pose, 44 KeyframeSequence) |
| ServerStorage | 160.202, sendo **140.501 em `Urso_v2_Piloto.Animacoes`** |
| MeshPart / Model / Part | 117.963 / 133.600 / 16.079 |
| Malhas diferentes (MeshId) | 453: a repetição é boa, o motor instancia bem |
| SurfaceAppearance | 98.833 cópias, 109 combinações diferentes |
| MeshParts com sombra (CastShadow) | 62.613 |
| Parts com CanTouch ligado | 13.919 |
| Models `Persistent` | 9.739 (Floresta 5.077, Montanhas 2.241, Pântano 1.432, Corrompidas 372, Planícies 198, Tundra 197, Costas 169, Deserto 53) |
| ParticleEmitter / PointLight ativas | 440 / 89, nenhuma luz com sombra |
| Streaming | ligado, Min 64, Target 1024 |
| Pós-efeitos | SunRays, Bloom, DepthOfField, ColorCorrection, Atmosphere |

## Oportunidades, da maior para a menor (PROPOSTA, nada aplicado)
1. **KeyframeSequences no ReplicatedStorage (Lobo Ártico):** 109 mil instâncias são baixadas por cada jogador na entrada. No jogo publicado, publicar os clipes como Animation (1 instância cada) e deixar só os IDs. Ganho previsto: entrada mais rápida e menos memória no cliente, principalmente no celular. Pertence ao chat do Lobo Ártico.
2. **Models `Persistent` (9.739):** ficam carregados em todo cliente, fora do streaming. Já foi a causa de FPS baixo (26/10, LOD_Distancia). Rever quais precisam mesmo ser Persistent; o restante pode ficar `Default`/`Atomic` e deixar o streaming descarregar.
3. **Sombras de vegetação pequena:** 62 mil MeshParts projetam sombra. Desligar `CastShadow` em plantas e folhagem pequenas (manter árvores e rochas) costuma render bastante GPU no celular.
4. **CanTouch em cenário estático:** 13.919 peças. Desligar onde nenhum script usa `Touched` reduz custo de física.
5. **DepthOfField:** é caro em celular. Considerar ligar só no PC ou só em cutscene.
6. **ServerStorage do Urso (140 mil Poses):** não pesa no cliente, mas aumenta o tamanho do place, o salvamento e a memória do servidor. Mesma solução do item 1 quando os clipes forem publicados.

## Medição em Play (20/11, mesma sessão; nada salvo, Play parado ao fim)
Contexto: 4 Studios abertos e a janela sem foco. O FPS do cliente ficou travado em ~14,3 em TODAS as vistas, até olhando o céu (0,5 M triângulos), então esse número é o limite do Studio em segundo plano e não o custo do jogo. **FPS real ainda não medido** (precisa do Studio em foco ou de um cliente publicado). Em Play do Studio, servidor e cliente dividem o mesmo processo, por isso a memória total (8,4 GB) não representa um jogador.

| Vista (câmera do cliente) | Triângulos | Draw calls | Maior parte |
|---|---|---|---|
| Spawn (câmera do jogador) | 6,53 M | 2.267 | Opaco 3,9 M/376; Terreno 461k/1.233; Grama 352k/43; Sombras 1,8 M/603 |
| No chão, olhando o horizonte | 4,82 M | 2.185 | Opaco 2,6 M/531; Terreno 1.069 dc; Sombras 1,5 M/535 |
| No chão, olhando o céu | 0,50 M | 192 | Sombras 417k |
| No alto das Montanhas, olhando o vale | 7,76 M | 1.896 | Opaco 7,27 M/430; Terreno 1.418 dc |

Referência da Roblox: cerca de 0,8 M triângulos e 600 draw calls é onde a maioria dos aparelhos mantém 60 fps. As vistas abertas estão de 6 a 10 vezes acima nos triângulos e cerca de 3 vezes nos draw calls.

| Outros números | Valor |
|---|---|
| Instâncias no cliente (workspace com streaming) | 173.407 |
| Heap Luau do cliente | 49 MB, dos quais **`Floresta_Vento` 37,3 MB** (move CFrame de MeshParts em todo Heartbeat) e `LOD_Distancia` 3,2 MB |
| Heap Luau do servidor | 21,6 MB, dos quais **`FaunaFloresta.AdaptadorFauna` 19,9 MB** (monta KeyframeSequences em cache) |
| Animações carregadas | cliente 1,7 MB (31 clipes); servidor 0,5 MB (8) |
| Áudio no cliente | 9,2 MB |
| Instâncias soltas | cliente 2.382, das quais 2.371 são do LOD_Distancia (modelos guardados de propósito com Parent=nil, não vazamento); servidor 353 (Controle_Servidor/Kit_Servidor do Lobo Ártico 120 cada, Controlador da fauna 70) |
| Servidor | Heartbeat 56,6/s, pior quadro 60 ms; 92 scripts ativos; 10 criaturas com Humanoid/AnimationController |
| Memória por tag no processo | PhysicsParts 1.159 MB, TerrainVoxels 1.140 MB, LuaHeap 1.016 MB, Instances 368 MB, Animation 245 MB |

### Oportunidades acrescentadas pelo Play (PROPOSTA)
7. **Triângulos de longe:** o Opaco chega a 7,3 M vendo o vale. O LOD_Distancia corta só modelos além de 1.800/2.600 studs. Um LOD de malha (versão simples das árvores ao longe, via `RenderFidelity`/malha reduzida) ou raios menores no celular são o maior ganho de GPU.
8. **Draw calls do terreno (1.000 a 1.400):** terreno grande desenhado ao longe. Testar o raio de streaming (Target 1024) menor no celular e conferir água/materiais variados nas bordas.
9. **Sombras (1,5 a 1,8 M triângulos):** confirma o item 3 (CastShadow da vegetação pequena).
10. **Floresta_Vento (37 MB e trabalho por quadro no cliente):** limitar a árvores perto da câmera ou trocar por vento em osso ou WindShake, conforme a regra de vento localizado nas folhas.
11. **AdaptadorFauna (20 MB no servidor):** o cache de clipes do servidor pode ficar só no cliente, ou ser substituído por Animation publicada.
12. **Instâncias soltas do Lobo Ártico (120 + 120):** conferir se são guardadas de propósito ou acumulam com o tempo (medir duas vezes com intervalo).

## A/B "triângulos de longe" (20/11, Play, só no cliente; nada salvo)
Método:
- LOD_Distancia desligado durante o teste;
- 77.531 modelos de topo das 8 pastas de bioma, dos quais 67.770 pequenos (caixa < 32 studs);
- tirados da cena (Parent=nil, só no cliente) além de um raio para árvores e grandes / pequenos;
- ao fim, tudo devolvido, LOD religado e Play parado.

| Vista | Corte (árvores/pequenos) | Triângulos | Draw calls | Opaco |
|---|---|---|---|---|
| Spawn, horizonte | sem corte | 5,21 M | 2.246 | 3,24 M |
| | 2.600 / 1.800 | 3,81 M | 1.759 | 1,83 M |
| | 1.500 / 900 | 3,04 M | 1.715 | 1,07 M |
| | 1.000 / 500 | 2,61 M | 1.637 | 0,68 M |
| | 700 / 350 | 2,42 M | 1.578 | 0,53 M |
| Alto, olhando o vale | sem corte | 43,24 M | 3.311 | 42,43 M |
| | 2.600 / 1.800 | 2,42 M | 1.776 | 1,93 M |
| | 1.500 / 900 | 1,42 M | 1.777 | 0,93 M |
| | 1.000 / 500 | 1,27 M | 1.733 | 0,78 M |
| (LOD real atual) | árvores até ~6.900 no ar limpo | 8,15 M | 3.382 | — |

Leitura:
- O LOD atual já corta de 43 M para 8 M vendo o vale.
- O que sobra vem do raio das árvores escalado pela Atmosphere (até ~6.900 studs no ar limpo), criado em 26/10 para não abrir buracos na fileira distante.
- Um raio fixo de 2.600 daria 2,4 M nessa vista, e 1.500/900 daria 1,4 M.
- No chão, as sombras (1,2 a 1,3 M) e os draw calls (~1.600 a 1.700, a maioria do terreno) quase não mudam com o raio. Esses dois pedem outras medidas (itens 3 e 8).
- Visual de cada raio NÃO avaliado: falta a captura antes/depois.

## Ainda não medido
- FPS real, com o Studio em foco ou num cliente publicado.
- Celular (sem aparelho real).
- MicroProfiler (`rbx-perf-profiling`), para ver o custo de CPU por script.
- Vazamento ao longo do tempo (duas medições espaçadas).

## Decisões do usuário (20/11)
- Triângulos de longe: **raio por aparelho**. O PC mantém o visual de hoje e o celular usa raios menores (PROVISÓRIO: 1.500 para árvores e 900 para pequenos).
- O horizonte do celular esconde o corte com **névoa um pouco mais densa**.
- Aprovação por **vídeo antes/depois** com a mesma câmera (alto das Montanhas e chão) e os números ao lado.

## Execução r1 (20/11) — perfil celular + correção do LOD (PROVISÓRIO, aguarda aprovação)
Aplicado no rpg_roblox, em Edit, nos scripts `StarterPlayerScripts.LOD_Distancia` e `Ambiente_Biomas`. Backup dos dois em `ServerStorage.Backup_Desempenho_20261120` (desativados). Place NÃO salvo nem publicado por este chat.

O que mudou:
1. **Perfil de aparelho** (`perfilCelular()`, nos dois scripts):
   - celular = toque sem teclado;
   - para testes, o atributo `workspace.LOD_Perfil` = "celular" ou "pc" força o perfil.
2. **LOD no celular:** árvores saem além de 1.500 e pequenos além de 900 (ajustáveis por `LOD_RaioCel` e `LOD_RaioPequenoCel`). O PC continua com a regra antiga (1.800 / 2.600 escalado pela névoa).
3. **Névoa no celular:** +0,12 na densidade da Atmosphere, com teto 0,72 (`Nevoa_ExtraCel`), aplicada no fim de `aplicar()` do Ambiente_Biomas.
4. **Defeito corrigido no LOD (vale para PC e celular):**
   - o script só ligava o `DescendantAdded` de cada pasta depois de varrê-la inteira;
   - tudo que chegava pelo streaming durante a varredura longa da Floresta ficava fora do LOD;
   - na entrada do jogo, ~57 mil modelos vazios nunca eram registrados, e reiniciar o script depois do carregamento derrubava a vista de 5,9 M para 2,35 M;
   - agora a escuta é ligada antes da varredura (pastas em paralelo), e um modelo que chega vazio volta para a fila quando as peças chegam (400 por ciclo de 0,4 s).

Medido em Play no Studio (sem foco, então FPS não representa o jogo; celular emulado pelo atributo, sem aparelho real):

| Vista | Antes (LOD original) | PC r1 | Celular r1 |
|---|---|---|---|
| Alto (-1000, 380, 300) olhando a leste | 6,05 M / 1.826 dc | **4,69 M** / 1.767 | **2,35 M** / 1.752 |
| Chão no spawn, horizonte | 4,82 M (1ª medição) | 4,54 M / 2.053 | **3,46 M** / 1.870 |

Visual: no PC, o antes e o depois ficaram iguais (o corte acontece dentro da névoa). No celular, a vista alta fica quase toda em névoa e o chão fica mais enevoado.

Evidência:
- `review/desempenho/LOD_celular_r1_antes_depois.mp4`
- `review/desempenho/LOD_celular_r1_quadros.jpg`

Pendências:
- draw calls continuam em ~1.750 a 2.050 (terreno e sombras);
- picos na entrada não medidos com as 8 varreduras em paralelo, até ~3.200 modelos por quadro (a tentativa de lotes menores não compilou e não foi gravada);
- mobile real não testado.
- Desfazer: copiar as Sources do backup.

**APROVADO pelo usuário em 20/11/2026** (vídeo e prancha r1). Os números de raio e névoa do celular continuam PROVISÓRIOS até o teste em aparelho real. O place ainda não foi salvo por este chat.
