# PROJECT-STATE — estado real verificado do RPG Roblox

**Status:** M0 (inspeção somente leitura) EXECUTADO em 2026-10-19. Studio verificado: projeto vazio (template padrão).
**Última atualização:** 2026-10-19 — resultado do M0
**Versão de referência:** documentos de planejamento RPG_01 e RPG_02.
**Mudanças no Roblox Studio nesta sessão:** NENHUMA (somente leitura; `execute_luau` usado apenas para contagens e `Terrain:ReadVoxels`).

## Estado do Studio — VERIFICADO em 2026-10-19
- Lugar: `rpg_roblox`, placeId 114230639394991, Studio em modo Edit. **VERIFICADO**
- Conexão MCP do Studio: funcional (1 instância listada). A primeira tentativa, com o Studio fechado, retornou lista vazia. **VERIFICADO**
- Workspace: apenas `Terrain`, `Baseplate` (Part 2048×16×2048, com Texture), `SpawnLocation` (com Decal) e `Camera`. 6 descendentes. **VERIFICADO**
- Terrain: 0 voxels não-vazios na amostra central 512×128×512 (resolução 4). Região maior (1024×320×1024) excedeu o limite da API e não foi lida; o restante do mapa não foi amostrado, mas o Workspace não tem outros objetos. **PARCIAL**
- Biomas: nenhum construído. **VERIFICADO** (nenhum objeto/terreno além do template).
- Scripts do usuário: 0 em Workspace, ServerScriptService, ServerStorage, ReplicatedStorage, ReplicatedFirst, StarterGui, StarterPlayer, StarterPack. **VERIFICADO**
- Serviços/pastas: ServerScriptService, ServerStorage, ReplicatedStorage, ReplicatedFirst, StarterGui, StarterPack, SoundService e Teams com 0 descendentes. StarterPlayer tem apenas StarterPlayerScripts e StarterCharacterScripts. Nenhum RemoteEvent, módulo ou dado persistente. **VERIFICADO**
- Lighting: 5 filhos, incluindo Atmosphere e Sky padrão, ClockTime 14.5. Sem configuração de bioma. **VERIFICADO**
- `Workspace.StreamingEnabled = true`. **VERIFICADO**
- Console: sem erros do jogo. Há apenas aviso de `debug.profileEnd()` do plugin MaterialManager (ruído de plugin, não do projeto). **VERIFICADO**
- Performance: NÃO medida. Mapa vazio, sem perfil em PC ou celular. **A VERIFICAR**
- Backup de segurança: estratégia aprovada em 2026-10-19 (`DOCS/BACKUP-STRATEGY.md`, pasta `Documents\RPG_Roblox\BACKUPS`). Backup `RPG_BKP_2026-10-19_pre-M1.rbxl` salvo e conferido pelo usuário (confirmação do usuário; não verificado em disco pelo Claude). Nome com data em formato AAAA-MM-DD, diferente do padrão AAAAMMDD proposto.
- Dimensão alvo (~6144×6144 studs): não confirmada no documento de origem. O Baseplate atual tem 2048×2048. **PENDENTE**

> Não confundir resultados do projeto Dragon Ranch com este RPG. Existem PROJECT-STATE.md de Dragon Ranch em outras pastas; nenhum foi usado.

## Comparação documento × Studio
| Item | Documento | Studio |
|---|---|---|
| 8 biomas, hub, terreno ~6144² | OFICIAL (planejado) | Não iniciado |
| Scripts, remotes, persistência | Planejado (M1) | Não iniciado |
| Criaturas, combate, inventário, missões, dungeons, loja | Planejado (M3–M7) | Não iniciado |
| Lighting/Atmosphere padrão | n/d | Template padrão, sem identidade por bioma |

Conclusão: o Studio coincide com o estado "PREPARAÇÃO"; não há implementação a preservar nem a corrigir.

## Problemas e riscos identificados
1. Nenhum backup definido; criar estratégia antes de qualquer mudança (CLAUDE.md item 6).
2. Dimensão do mundo não confirmada (6144 vs. Baseplate de 2048).
3. Pendências de Game Design em `DOCS/DECISIONS-AND-OPEN-ISSUES.md` seguem abertas (itens 1–8). Não foram alteradas.
4. Sessão de edição colaborativa ativa ("joined live editing session"); coordenar com quem mais edita o lugar.
5. Desempenho mobile ainda não medido.

## M1.2a — CONCLUÍDO e aprovado pelo usuário em 2026-10-19 (limitações abaixo permanecem)
**Objetos criados no Studio (apenas estes; nada removido ou substituído; Workspace e Lighting inalterados: 6 e 5 descendentes):**
- `ServerScriptService`: `Data/{DataService, Migrations}`, `Services/{CurrencyService, InventoryService, GrantService}`, `Bootstrap` (Script).
- `ServerStorage`: `Config/GameConfig`, `Tests/{FakeDataStore, TestRunner}`.
- `ReplicatedStorage`: `Shared/Validators`, `Remotes/ProfileState` (RemoteEvent, servidor→cliente; sem handler `OnServerEvent`).

**Comportamento:** bloqueio de sessão por `sessionId` único dentro do mesmo registro, tomada de bloqueio expirado, escrita só se a sessão ainda for dona (sessão antiga fica somente leitura), cópia da última versão boa, migrações sequenciais sem sobrescrever em caso de erro. Concessão e `grantId` são gravados na mesma escrita; o estado em memória só muda depois da gravação confirmada; falha gera `Pending` e a operação fica preservada (`handle.pending`) para repetição com o mesmo `grantId`. 40 espaços, uma moeda (`gold`).

**Testes (`ServerStorage/Tests/TestRunner`, executado via MCP no modo Edit):** 31 aprovados, 0 falhas, cobrindo: idempotência (inclusive chamadas simultâneas), falha de gravação, sucesso ambíguo e queda, falha de carga, registro corrompido e recuperação por backup, sessões concorrentes, expiração e escrita obsoleta, batimento, release falho, migração (ok, falha, versão futura), argumentos inválidos, moeda insuficiente/estouro, inventário cheio, pilhas, tudo-ou-nada, janela de `grantId`.
**Integração:** playtest curto no Studio com DataStore falso: `Bootstrap` carregou o perfil do jogador (`ProfileLoaded=true`), sem erros do projeto no console (apenas avisos do UIBlox da Roblox).

**Limitações (não declarar como testado):**
- Todos os cenários de múltiplos servidores são SIMULADOS (dois `DataService` sobre o mesmo DataStore falso). Não houve teste com vários servidores reais nem com o DataStore real de Roblox.
- O adaptador `DataService.newRobloxStore` e `UseRealDataStore=true` NÃO foram executados. Acesso às APIs não foi habilitado.
- `BindToClose` com vários jogadores e autosave temporizado não foram testados; só o carregamento no playtest.
- Atomicidade do `UpdateAsync` real é assumida; o falso a reproduz.
- Janela de `grantId` (200, ajustável) é um valor técnico: repetições de um id podado não seriam detectadas.
- Bloqueio depende de relógio (`os.time`) entre servidores; tolerância de 120 s é técnica.
- Remoção/consumo de itens e `tradable` ainda não implementados (M4); `DefaultMaxStack=99` e itens `test_*` são provisórios.
- Backup sem o `Tests` precisa de ajuste: `Bootstrap` usa `Tests/FakeDataStore`.
- Verificação do colaborador: a API não listou colaboradores. A evidência foi o log ("Yxx_Winner joined live editing session") e `Players` com um único usuário. Não foi possível confirmar a ausência de outros editores.
- Os testes passaram de primeira; não foi feito teste de mutação para provar que cada teste falharia com o bug correspondente.

## M1.3 — CONCLUÍDO e validado pelo usuário em 2026-10-19 (limitações e riscos abaixo permanecem)
**Alterado (nenhum objeto criado ou removido; Workspace 6, Lighting 5, SSS 8, SS 5, RS 4 descendentes, iguais a antes):** `Data/DataService`, `Services/GrantService`, `ServerStorage/Config/GameConfig`, `Bootstrap`, `Tests/TestRunner`, `Tests/FakeDataStore` (chave ≤ 50 caracteres e falha após n chamadas, só suporte a testes). `UseRealDataStore=false`.
- **V1:** concessões permanentes (`P:<PurchaseId>`, `E:<tipo>:<userId>:<evento>` ou `opts.permanent`) têm registro durável sem expiração num ledger separado, uma chave `L:<id>` por concessão, em fases retomáveis: reservar → entregar no perfil → confirmar. O perfil guarda o id só até a confirmação (`permGrants`), então não cresce. Concessões comuns mantêm a janela de 200 ids.
- **V2:** a sessão fica insegura após `LockTimeout − LeaseMargin` (90 s) sem escrita confirmada. Nesse caso `Transact` recusa com `SessionLost`, `ReleaseProfile` não escreve, `IsSafe` retorna falso e `onSessionLost` remove o jogador (Bootstrap). Não há recuperação silenciosa.
- **V3:** posse do bloqueio pela identidade da instância (GUID + endereço do objeto), não pelo `JobId`. `JobId` de Studio agora é único.
- **V4:** perfil congelado em profundidade; `handle` é proxy somente leitura; escrita só via `Transact`; leitura via `Read`/`handle.data`.
- **V5:** tamanho serializado do registro inteiro (perfil + backup + bloqueio) verificado antes de gravar. Limite configurável `MaxRecordBytes=3.200.000`. Acima disso: `Rejected/ProfileTooLarge` sem alterar o persistido. Medição: registro com 40 itens + backup = 7.910 bytes.

**Testes:** 47 aprovados, 0 falhas (31 anteriores + T32–T47: 250 concessões e repetição de recibo, conflito, queda entre fases do ledger, ledger indisponível, simultaneidade, validade da sessão, ids de instância repetidos, imutabilidade, limite de tamanho, concorrência com ids diferentes e com release, saída com pedido pendente). Executados no servidor de um playtest do Studio com DataStore FALSO; `Bootstrap` carregou o perfil (`ProfileLoaded=true`), sem erros do projeto no console.
**Observação:** o `require` no modo Edit reaproveita módulos em cache; os 47 testes só rodaram completos no playtest (VM nova).

**SIMULADO (não é verificação real):** todo cenário multi-servidor (dois `DataService` sobre o mesmo store falso), ambiguidade/falha de rede, ledger e latência.
**NÃO verificado:** DataStore real (atomicidade de `UpdateAsync`, throttling, limite de 4 MB e de 50 caracteres de chave reais), adaptador `newRobloxStore`, vários servidores reais e relógio entre eles, `BindToClose` com vários jogadores, autosave temporizado, ProcessReceipt real. Sem teste de mutação: os testes passaram na primeira execução e não foram provados capazes de falhar para cada bug.

**Riscos restantes:** (1) rollback de perfil (restauração de backup) pode perder uma entrega que o ledger já marca como entregue; exige ferramenta de suporte. (2) Ids comuns fora da janela de 200 podem ser reaplicados; compras e recompensas de chefe devem usar ids permanentes. (3) Compra com `Rejected` (ex.: inventário cheio) ainda sem destino (M7). (4) Chamador de compras deve responder `NotProcessedYet` para `Pending`, `SessionLost` e `Error` (contrato só documentado em comentário). (5) Quantidade de chaves no ledger cresce com o número de eventos permanentes (uma chave pequena por evento). (6) Valores técnicos (90 s de validade, 120 s de bloqueio, 3,2 MB, 50 caracteres) não validados contra o DataStore real. (7) V6 (rotação de backup), V7 e V8 não implementados.

## M2.1A — protótipo Floresta Ancestral: TERRENO (2026-10-19) — AGUARDANDO AVALIAÇÃO DO USUÁRIO
Escopo autorizado: só terreno (M2.1B vegetação, M2.1C água, M2.1D ambientação ainda NÃO iniciados). Área X 1200–1600, Z −200–200 (fora do Baseplate, que termina em 1024).
**Backup:** `Documents\RPG_Roblox\BACKUPS\RPG_BKP_2026-10-19_pre-M2b.rbxl`, 107.501 bytes, 18:12 (usuário). Conteúdo só parcialmente verificável (formato comprimido: aparecem `Bootstrap` e `ProfileState`, ausentes no backup antigo). O lugar vivo foi verificado com os scripts M1 (`permGrants` presente). O arquivo antigo foi renomeado pelo usuário e substituído.
**Reversibilidade:** estado original do Terrain lido e verificado: 230.000 voxels (res. 4), todos Air, ocupação 0. Guardado em `ServerStorage/Proto_Restore/TerrainRestore` (`restore()` regrava Air/0 e devolve as 6 cores originais de material).
**Criado:** terreno por script (colinas suaves, clareira central r≈45, trilha de terra ~7 studs de largura, vale seco para o rio futuro, cerca de colinas/rocha com passagens, alturas 5–52); cores de 6 materiais ajustadas; `Workspace/Proto_FlorestaAncestral` com `Proto_Spawn` (clareira, y≈18), `Proto_RespawnRedirect` (só em Play) e `Limites` (4 paredes invisíveis). Nenhuma árvore, água, vento ou alteração de Lighting.
**Medições:** InstanceCount Edit 3.740 → 3.752. Play: spawn em (1396, 21, −3), trilha percorrida da clareira à entrada oeste e ao nordeste, FPS cliente 60,0 (limite de Studio), sem erros do projeto no Output. Sem medição de Play "antes" (InstanceCount em Play 46–49 mil inclui o Studio). M1 intacto: `ProfileLoaded=true`, 47 testes não reexecutados.
**Observações:** a grama decorativa 3D do terreno aparece perto da câmera, sem script. Efeito do `GlobalWind` sobre ela NÃO testado. As capturas são renders de edição (câmera ao nível do jogador), não capturas de Play. Dois pedidos de captura deram timeout.
**Revisão do terreno (2026-10-19, a pedido do usuário):** terreno regerado sobre a mesma área (restauração continua válida). Mudanças: deformação de domínio e tufos de chão de floresta (±3 studs), cerca irregular, 18 afloramentos rochosos com degraus e musgo no topo, degrau rochoso (~9 studs) no vale seco, em x≈1490, como futuro local de queda d'água (sem água), cores de rocha mais escuras e mais musgo/solo úmido. Teste em Play repetido: spawn e trilha OK, FPS 59,7, sem erros do projeto no Output. Capturas de edição: trilha e clareira, vale e degrau, vista geral.
**2ª revisão (referência `01-floresta-ancestral-e-montanhas-altas.png`):** piso de floresta mais úmido e musgoso (grama clara só na clareira, cores mais escuras de solo e rocha), 4 sítios de árvores ancestrais com monte central e cristas radiais de raízes com húmus (≈ (1350,−52), (1455,50), (1335,−5), (1475,−62)), plataforma de ruína em degraus de laje (centro (1440,−60), raio ≈16 com anel de degrau), pedras e seixos na borda da trilha e no leito do vale. Play repetido: spawn e trilha OK, FPS 59,7, 0 erros no log de cliente e de servidor, `ProfileLoaded=true`. Esses sítios e a ruína são só relevo; árvores e pedras de ruína ficam para M2.1B.
**Limitações visuais:** terreno em resolução de 4 studs (rochas pequenas e detalhes finos exigem malhas na etapa seguinte), bordas externas do protótipo são uma laje visível (área isolada), parte da cerca atinge o teto de 68 studs com topo achatado, iluminação ainda é a do template, sem vegetação. Referências em `Downloads\RPG_Referencias_Visuais_GitHub\REFERENCES` consultadas (Floresta Ancestral e direção de arte); serão a base de M2.1B.

## M2.1B — 4 árvores de amostra (2026-10-19) — AGUARDANDO AVALIAÇÃO DO USUÁRIO
Terreno do M2.1A aprovado. Criadas 4 árvores em `Workspace/Proto_FlorestaAncestral/Arvores`, nos sítios de raízes: `Carvalho_Ancestral_01` (1350,−52, H62), `Freixo_Antigo_01` (1455,50, H78), `Carvalho_Jovem_01` (1335,−5, H36), `Freixo_Velho_01` (1475,−62, H70, ramos mortos). Cada uma é um Model com submodelos `Tronco`, `Raizes`, `Galhos`, `Copa` (cada `Cacho` com pivô próprio, preparado para vento), `Cipos`, `Detalhes` (musgo, cogumelos).
**Técnica:** só Parts nativas, sem assets externos: cilindros sobrepostos com cristas de casca, raízes contrafortes baixas que seguem o relevo, galhos em polilinhas, copas de elipsoides achatados, cipos e musgo. Primeira versão apagada e refeita (raízes em "contas" e copas globulares).
**Medições:** 905 / 786 / 512 / 742 partes por árvore, 2.950 no protótipo, só 20 com colisão (base dos troncos). InstanceCount Edit 3.752 → 6.820. Play: 59,8 FPS, 0 erros nos logs de cliente e servidor.
**Avaliação honesta de qualidade:** reconhecível como carvalho e freixo, com raízes e cipos, mas estilizado e longe de `REFERENCES/` (copa de discos separados, casca lisa e escura, sem folhagem densa nem luz filtrada). **Custo inviável para multiplicar:** ~740 partes por árvore × 150 árvores ≈ 110 mil partes. Só serve como árvore "herói" próxima do jogador.
**Caminho recomendado (precisa de autorização, não executado):** malhas com textura de folhas e casca (`generate_mesh` ou criação de malhas/imagens), com instanciamento e LOD, e vento por ossos ou script em poucas árvores próximas. Nenhum vento, água ou iluminação criado nesta etapa.

**Teste de malha IA (M2.1B, 1 árvore, autorizado):** `generate_mesh` (12.000 triângulos pedidos, 2 partes: tronco+raízes e copa), prompt de texto derivado de `REFERENCES/`, sem enviar imagens. A 1ª chamada deu timeout sem inserir nada; a 2ª, assíncrona, concluiu (jobId 2b6aa802…). Resultado em `Proto_FlorestaAncestral/Teste_Malha/Carvalho_Malha_Teste` (1425, solo, 30), 2 MeshParts com textura, colisão desligada. **A ferramenta publicou um asset na conta do usuário: `publishedAssetId` 132065855836209 (e os MeshIds/TextureIds gerados).** Custo/cota: não informado pela ferramenta; número de gerações cobradas não verificável (1 resultado inserido; a chamada com timeout pode ter gerado outro asset invisível).
**Avaliação:** a forma saiu estilizada (tronco torcido com poucas pontas de galho folhosas, ~45 studs, sem copa densa), longe da referência e menos convincente que a copa em massa que a ferramenta não controla. Textura de casca/folha razoável de perto, silhueta cartunesca. Triângulos reais não medidos (API não expõe). Conclusão: `generate_mesh` não atinge o realismo exigido para árvores ancestrais; pode servir para rochas/adereços. Ver caminho alternativo no relatório. Não multiplicado.

**M2.1B, 2ª versão das 4 árvores (pedido do usuário):** reconstruídas com tronco 1,4× mais grosso e canelado (núcleo + 5 lobos torcidos), 7–8 raízes contrafortes ao solo com raízes laterais, 6–10 raízes helicoidais enroladas no tronco, tiras de casca soltas e manchas de madeira exposta nas raízes e na base do tronco, folhas em cartões triangulares (WedgePart) no lugar de esferas, cipos com folhas. Folhagem ao redor em `Proto_FlorestaAncestral/Sotobosque`: 20 samambaias (fronds com folíolos), 16 plantas de folha larga e 520 folhas de serapilheira. Pasta `Arvores` e `Samambaias` substituídas (objetos criados nesta tarefa).
**Medições:** 9.451 partes no protótipo (4 árvores 964–1.481 cada, ~1.900 de folhas adicionadas às copas), 24 com colisão. InstanceCount Edit 13.364; Play 55.688 (inclui Studio). Play: 59,8 FPS (limite de Studio) junto à árvore maior, 0 erros nos logs, `ProfileLoaded=true`. Medição só em Studio no PC, sem mobile.
**Avaliação:** troncos e raízes bem mais volumosos e com raízes enroladas; folhas deixaram de ser bolas e leem como folhas angulares; piso com samambaias e serapilheira. Ainda não iguala `REFERENCES/`: casca peeling aparece como faixas/anéis escuros, folhas são cartões triangulares uniformes, copas ainda pouco densas e escuras contra o sol, raízes têm bandas nas emendas. **Custo inviável para multiplicar** (~1.200 partes por árvore + folhagem): serve como árvores-herói; a floresta densa precisa de malhas instanciadas com textura de folhas (pipeline próprio) ou de aproximações por LOD. Sem vento, água ou luz nesta etapa.

**M2.1B, 3ª versão das 4 árvores (pedido do usuário: mais raízes, tronco mais grosso, raízes enroladas ao máximo, musgo, folhas mais reais):** troncos 1,3× mais grossos que a versão anterior (R0 11,5 / 8,0 / 6,0 / 9,4 studs; conicidade menor) com 6 lobos; 9–12 raízes ao solo com 3 raízes laterais cada; 14–24 raízes grossas e 6–10 "cordas" finas enroladas no tronco por árvore; tiras de casca soltas; mantas de musgo no tronco, nas raízes e nos galhos (1.479); folhas agora em ramitos compostos com folíolos alternados (carvalho: largos; freixo: estreitos), mais cartão de ponta. `Arvores` substituída (objetos desta tarefa). Moss em bola não achatava (Ball vira esfera): trocado por mantas finas de bloco.
**Medições:** partes no protótipo 13.814 (árvores 3.213 / 3.381 / 1.993 / 2.504), 24 com colisão; InstanceCount Edit 17.733. Play: 59,8 FPS, pior quadro 18 ms, 0 erros, `ProfileLoaded=true`, só PC/Studio. Sem teste mobile; 13,8 mil partes é muito para celular.
**Avaliação:** troncos e emaranhado de raízes bem mais próximos da referência em volume; folhas de ramito leem como folhas de verdade, porém ainda são cartões lisos e a copa ficou menos densa que a versão anterior. Musgo em quadrados, raízes com bandas nas emendas, casca solta em tiras retas. Segue abaixo do realismo de `REFERENCES/`. Sem vento, água nem luz.

**M2.1B, copas mais densas e claras (pedido do usuário):** nas 90 copas: folhas existentes 1,3× maiores e mais claras (4.392), +3 ramitos compostos por cacho (+3.780 folhas), núcleos esféricos removidos (180) e folhas agora projetam sombra, o que produz luz salpicada no chão. Resto das árvores inalterado.
**Medições:** 17.414 partes no protótipo, 24 com colisão. Play: 60,0 FPS, pior quadro 18 ms, 0 erros, `ProfileLoaded=true`, só PC/Studio (sem mobile). Custo muito alto para multiplicar: ~4,3 mil partes por árvore-herói.
**Avaliação:** copa visivelmente mais densa, de folhas compostas e com céu visível entre elas; permanece de cartões triangulares lisos, longe do realismo de `REFERENCES/`, e escura quando contra o sol.

**M2.1B, mais galhos + vento (pedido do usuário):** +34 galhos principais (2 níveis, inclusive limbos baixos quase horizontais), ramos secundários e terciários e +285 cachos de folhas compostas nas 4 árvores (partes 17.414 → 29.250), musgo nos galhos. Vento: `Proto_VentoServidor` (Script) varia `Workspace.GlobalWind` em Play (direção ±35°, força ~3–15); `Proto_VentoCliente` (Script, RunContext Client) balança cada cacho (`ProtoCopa`, 375) e cada samambaia/folha larga (`ProtoSamambaia`, 36) inclinando na direção do vento com oscilação e rajadas por posição, e tremula folha a folha a <20 studs; só visual no cliente, tronco/raízes/galhos grossos parados. Alcance: balanço 52 studs, tremular 20, 20 Hz, `BulkMoveTo`.
**Evidência do vento (Play, medido):** `GlobalWind` variou (ex.: 4,5/10,2 → 5,5/8,1); folhas deslocaram até 1,03 studs (média 0,31) com alinhamento cos=0,99 com a direção do vento; custo medido do tick: 3,8 ms por 31 cachos/1.917 partes a 20 Hz (~8% de 1 núcleo); 0 erros nos logs de servidor e cliente. A animação visual em si não foi gravada nem vista (as capturas são estáticas).
**Desempenho (limitação grave):** FPS em Studio oscilou entre 60 e ~15 (quadros fixos de 68 ms, igual com o script de vento desligado, com folhas ou raízes ocultas e em qualquer direção de câmera), o que sugere limitação do Studio/janela e não do vento, mas NÃO foi diagnosticado. 29 mil partes é inviável para celular e arriscado até no PC; precisa de unions/malhas ou LOD antes de multiplicar. Grama do Terrain com `GlobalWind`: não verificada.

**Teste de unions (3 cachos de amostra do `Carvalho_Ancestral_01`, pedido do usuário):** `GeometryService:UnionAsync` (CollisionFidelity Box, RenderFidelity Automatic): 36 folhas → 1 `UnionOperation` ("Folhagem") por cacho em ~0,02 s; cor por folha preservada (`UsePartColor=false`). Folhas originais guardadas em `ServerStorage/Proto_Restore/UniaoBackup` para reverter. Partes no protótipo 29.250 → 29.145. Em Play o vento move as unions (deslocamento máx. 0,40–0,55 studs, a ~43 studs), mas sem tremular por folha (rígidas); cachos não unidos ainda tremulam (0,89). 0 erros no log do cliente.
**Projeção (não aplicada):** unir os 375 cachos: 29.145 → ~11.200 partes (−62%). Perdas: tremular folha a folha; riscos não medidos: tamanho do arquivo do lugar, memória e triângulos por union, aspecto fino das folhas na renderização "Automatic". Nada aplicado além dos 3 cachos.

**Folhas com forma de folha (pedido do usuário, imagem de referência da Floresta Ancestral):** a folha "retângulo/triângulo reto" (1 cunha) foi substituída por um losango dobrado (4 cunhas: 2 por metade, com dobra na nervura central, metades de tons diferentes), construído a partir da posição, orientação e tamanho de cada folha antiga (comprimento ×1,1, largura ×1,5). Para não multiplicar partes, as folhas de cada cacho foram unidas por `GeometryService:UnionAsync` em até 5 `UnionOperation` (nome "Folha", cor por folha preservada) por cacho. Elipse achatada não é possível com Parts (Ball/Cylinder ignoram tamanho não uniforme; Ball some na union).
**Resultado:** 375 cachos convertidos, 1.371 unions totais, partes no protótipo 29.145 → 12.189 (−58%); folhas originais guardadas em `ServerStorage/Proto_Restore/UniaoBackup` (~18 mil Parts, não replicadas ao cliente; aumentam o arquivo do lugar, podem ser apagadas). Algumas folhas isoladas (grupos < 3) foram descartadas na conversão. O vento continua: as unions balançam e tremulam por grupo de folhas (cada union reage como "Folha"), deslocamento medido até 2,6 studs; o tremular folha a folha deixou de existir.
**Medições em Play:** 60,0 FPS (pior quadro 23 ms) junto à árvore maior, 74 cachos no balanço, 0 erros no log de cliente e de servidor, `ProfileLoaded=true`. Só PC/Studio. Triângulos por union não medidos (≈32 por folha), risco para celular.
**Avaliação:** silhueta de folha pontiaguda e dobrada, bem mais próxima de folha que o triângulo reto; ainda poligonal, sem curvatura real, sem textura de nervuras e sem a transparência e o volume das folhas da referência. Samambaias e folhas largas do solo continuam em cunha simples (não convertidas). Para realismo próximo da referência seria preciso malha com textura (pipeline próprio ou generate_mesh de uma folha).

**Samambaias e folhas largas do solo (pedido do usuário):** 36 modelos (20 samambaias + 16 plantas de folha larga), 2.056 folhas em cunha convertidas em losangos dobrados (comprimento ×1,25, largura ×1,6) e unidas em 188 `UnionOperation` ("Folha"; 7 grupos por samambaia, 3 por planta). Nervuras das samambaias mantidas. Originais guardados em `ServerStorage/Proto_Restore/UniaoBackup`. Partes no protótipo 12.189 → 10.321. A serapilheira (520 folhas no chão) NÃO foi convertida.
**Play:** vento move as unions do solo (deslocamento máx. 0,84 studs), 59,8 FPS (pior quadro 22 ms), 0 erros no log de cliente e de servidor, `ProfileLoaded=true`. Só PC/Studio.

**Prints e simulação de ambiente (pedido do usuário):** iluminação TEMPORÁRIA de floresta úmida aplicada só para capturas (ClockTime 16,6, Atmosphere com névoa verde e Glare, SunRays 0,32, Bloom, profundidade de campo, ColorCorrection) e 87 clones temporários de samambaias e folhas largas (Sim_Temp). Tudo REVERTIDO e verificado: Lighting com os valores originais (14,5 h, Brightness 3, Atmosphere 0,3, DOF desligado, 5 filhos) e 10.321 partes no protótipo. Arquivos em `SCREENSHOTS/` (prancha `00_prancha_referencia_vs_roblox.png` + 5 prints). Os prints são renders de edição do Studio, não capturas de Play. `Lighting.Technology` (Future) não foi lido nem alterado.

**Árvores: galhos superiores, coroa em forquilha e raízes circulares (pedido do usuário):** nas 4 árvores foram adicionados galhos no terço alto do tronco (16 / 12 / 12 / 7 + 4–5 galhos de coroa em forquilha no topo; `GalhosSuperiores`) com ramos secundários e 252 cachos novos de folhas em losango dobrado, já como `UnionOperation` ("Folha", tag `ProtoCopa`, vento mantido), para que o tronco alto (`Freixo_Antigo_01`, 78 studs) deixe de terminar em haste reta. Novas raízes circulares enroladas (`RaizesCirculares`): 14/12/8/12 raízes em espiral que sobem em voltas pelo tronco (0,45–0,95 volta, 6–26 studs de altura) mais 2–3 faixas parciais em anel, mais grossas e salientes, com casca soltando e musgo (1.840 segmentos).
**Medições:** partes no protótipo 10.321 → 16.174 (raízes ~1.840 segmentos, galhos e cachos o resto), 24 com colisão. Play: 60,0 FPS (pior quadro 21 ms), vento movendo as unions novas (até 0,45 studs medido a 8 s), 0 erros nos logs de cliente e servidor, `ProfileLoaded=true`. Só PC/Studio, sem mobile.
**Avaliação:** coroa cheia e ramificada no tronco alto, raízes em voltas bem visíveis; segue poligonal, casca lisa e raízes de cilindros com emendas visíveis, ainda não idêntica a `REFERENCES/`. 16 mil partes é inviável para celular e para multiplicar árvores.

**Copa esparsa, raízes no tronco e qualidade por dispositivo (pedido do usuário):**
- **Copa:** ~60% dos cachos acima de 70% da altura removidos nas 4 árvores; adicionados galhos LONGOS superiores (`GalhosLongos`: 14/12/12/6 galhos de 14–40 studs, ângulos para cima) com folhas só no terço externo e esparsas (`Cacho` pequeno, unions de losangos, tag `ProtoCopa`, vento mantido). O tronco alto deixou de ser haste com massa de folhas.
- **Raízes no tronco:** as "raízes circulares" cilíndricas foram refeitas como `UnionOperation` lisas (1 por raiz; `RaizCircular`, `RaizAnel`) e criadas 9/8/5/8 raízes TREPADEIRAS finas (`RaizTrepadeira`, cor mais clara, 1,3–2,6 voltas, sobem 35–68% da altura, por fora dos lobos). Causa do "nada mudou" na versão anterior: 14 raízes largas se fundiam em um cone liso e estavam escondidas por centenas de tiras escuras de casca; removidas as raízes enroladas antigas, as tiras escuras (1.442 nas raízes + as do tronco) e parte do musgo.
- **Qualidade por dispositivo:** `Proto_Qualidade` (Script cliente) com 4 níveis: 1 Baixo (toque sem teclado; oculta ~5.300 das 10.621 partes: serapilheira, casca solta, musgo, cipós, ramitos, raízes extras, metade da vegetação do solo; sem sombras de folha; vento 24 studs a 10 Hz, sem tremular; sem iluminação cinematográfica), 2 Médio (oculta ~610; vento 36/15 Hz; atmosfera leve), 3 Alto (tudo visível, sombras de folha; vento 52/20 Hz com tremular a 20 studs; atmosfera, raios, ClockTime 16,6 só na área), 4 Ultra (vento 75 studs a 30 Hz, tremular a 32; profundidade de campo, bloom, correção de cor). Detecção: `TouchEnabled` sem `KeyboardEnabled` → Baixo; senão `settings().Rendering.QualityLevel`; adaptação por FPS (desce se <30 FPS por 5 s, sobe se >57 por 30 s até o limite detectado); override manual pelo atributo do jogador `ProtoQualidade` (1–4 ou nome). Tudo local ao cliente: Lighting do servidor intacto (Density 0,30 medida).
- **Testado em Play (PC/Studio):** troca de nível por override: partes ocultas 5.337 / 610 / 0 / 0, folhas com sombra 0 / 0 / 2.306 / 2.306, atmosfera, raios, bloom, DOF e ClockTime mudam por nível, 0 erros nos logs; FPS 60 em todos os níveis (sem estresse real). NÃO testado: aparelho móvel real, adaptação por FPS na prática, detecção de `QualityLevel`, efeito visual de cada nível (capturas de Play indisponíveis), custo de triângulos das unions em celular.
- **Partes no protótipo:** 10.621 (1.690 unions). Capturas de edição novas em `SCREENSHOTS/` (09 e 10; a 10 foi tirada com a copa e o ambiente alterados só para diagnóstico, já revertidos).

**Teste de textura gerada (`generate_material`, autorizado pelo usuário após confirmar saldo 0 Robux):** gerado 1 `MaterialVariant` "ProtoCascaMusgosa" (base Wood, padrão Organic, StudsPerTile 10; mapas de cor, normal, metal e rugosidade; 4 assets na conta: 118651852964651, 128081424031826, 106276794762685, 90863902976164; objeto em `MaterialService/AssistantMaterials`). Aplicado SÓ nas 133 partes do tronco (`Nucleo`/`Lobo`) do `Carvalho_Ancestral_01` (Color branco; original guardado nos atributos `OrigColor`/`OrigMat`). Custo/cobrança: não informado pela ferramenta; o usuário deve conferir o histórico de transações.
**Avaliação:** a textura gerou veios de madeira com relevo leve, não a casca fendida com musgo grosso da referência; ganho modesto de detalhe. Vista só em captura de edição com ambiente claro temporário (revertido). Não aplicado às outras árvores. **Revertido a pedido do usuário:** as 133 partes do tronco voltaram a Wood com a cor original e sem `MaterialVariant`; nenhuma parte do protótipo usa mais a textura. O `MaterialVariant` e os 4 assets gerados continuam existindo em `MaterialService/AssistantMaterials` e na conta (não apagados).

**Tronco com cristas verticais e textura de casca velha (pedido do usuário; só `Carvalho_Ancestral_01`):**
- 114 lobos empilhados do tronco removidos; criado `Cristas`: 20 cristas verticais longas (uma `UnionOperation` lisa cada; 42–88% da altura, 0,03–0,22 volta, espessura 0,15–0,24 R0) que descem em leque até o chão e fundem com as raízes; cores casca cinza-marrom, tiras de madeira exposta e faixas de musgo verde vivo (cilindros de cor/material Grass dentro da union). Removidos 149 mantas de musgo do tronco (pareciam papel). Partes no protótipo 10.378. Vento/qualidade/raízes mantidos; Play NÃO repetido após esta mudança.
- **Texturas geradas (`generate_material`, saldo 0 Robux, custo não informado):** "ProtoCascaVelha" (casca velha descascando) e "ProtoCascaVelha2" (mais clara, musgo vivo), 4 assets cada. Ambas saíram quase pretas, com sulcos verticais mas sem musgo visível e sem a cor da referência; a cor do `MaterialVariant` só multiplica a textura, então não dá para clarear por script. NÃO ficaram aplicadas: todas as partes voltaram à cor original (0 partes com `MaterialVariant`). Os `MaterialVariant` e os 8 assets (+4 da primeira textura) continuam em `MaterialService/AssistantMaterials` e na conta.
- Não aplicado às outras 3 árvores.

**Ajuste do tronco do `Carvalho_Ancestral_01` (pedido do usuário):** cristas refeitas como 46 `UnionOperation` finas (espessura 0,075–0,125 R0, antes 20 e 0,15–0,24), subindo 62–97% da altura (até onde o tronco se abre em galhos), com casca ancestral (cinzas e marrons escuros), faixas de musgo verde vivo e trechos de madeira exposta. `DetalheCristas`: 145 tiras soltas de casca (as 39 mais longas e 26 muito pretas ajustadas) e 145 placas de madeira exposta clara. `MusgoManchas`: 61 manchas pequenas (de 150, 89 removidas por cobrirem a casca). Base: +52 samambaias e +30 plantas de folha larga em volta (8–30 studs do tronco; clones com vento, tag `ProtoSamambaia`). Mantas antigas de musgo do tronco removidas.
**Play:** 60,0 FPS (pior quadro 36 ms), vento nas folhas da base (até 2,58 studs), 0 erros nos logs, `ProfileLoaded=true`. Partes no protótipo 11.512; nenhuma parte com `MaterialVariant` (as texturas geradas não estão em uso). Só PC/Studio. Prints 11–13 em `SCREENSHOTS/` (diagnósticos com copa e vegetação ocultas só localmente, revertidos).
**Limites:** musgo em cilindros de cor lisa, não em manchas orgânicas; casca sem relevo real; só 1 das 4 árvores; a base coberta por plantas se vê melhor em Play (captura de edição fica escura).

**Tronco e raízes mais visíveis, vegetação só no chão e menos musgo (pedido do usuário):**
- **Vegetação:** 98 samambaias/plantas de folha larga que cobriam as árvores foram empurradas para fora de uma zona livre de 2,9×R0 em volta de cada tronco (ex.: 33 studs no Carvalho Ancestral) e TODAS as 118 plantas do chão reduzidas a 65% do tamanho (as fronds eram maiores que o jogador); 243 folhas de serapilheira perto dos troncos removidas.
- **Musgo:** 1.574 mantas de musgo (de 1.846) removidas das 4 árvores; as 272 restantes ficaram com tamanho, forma e cor irregulares; `MusgoManchas` (150 discos) removido. No `Carvalho_Ancestral_01`, cristas refeitas (46 uniões): cor da casca por gradiente suave (ruído) em vez de cor por segmento (que criava padrão de xadrez), musgo reduzido a 6 manchas irregulares com borda por ruído (≈8% dos segmentos, verdes mais escuros), 101 placas de madeira exposta removidas. Cristas/musgo/casca só no Carvalho Ancestral; as outras 3 árvores mantêm os lobos antigos.
- **Play:** 60,0 FPS (pior quadro 24 ms), vento na vegetação da base (até 1,04 studs), 0 erros nos logs, `ProfileLoaded=true`. Partes no protótipo 9.533. Prints 14–16 em `SCREENSHOTS/` (diagnósticos com copa oculta e ambiente claro só localmente, revertidos).
- **Limites:** musgo ainda é cor lisa em cilindros; tiras soltas de casca são placas retas; as raízes enroladas e as cristas ainda parecem cilindros; capturas de edição não substituem a visão em Play.

**Corpo único do tronco (pedido do usuário: peças atravessando umas às outras ficavam feias; só `Carvalho_Ancestral_01`):** o núcleo (19 cilindros), 324 raízes de chão, 46 cristas e 26 raízes enroladas foram fundidos por `GeometryService:UnionAsync` (RenderFidelity Precise, em blocos e depois um union final) num único `UnionOperation` "CorpoTronco" (~11 s para gerar), com uma base alargada de 14 cilindros para as raízes nascerem do tronco. Os pedaços originais foram guardados como clones em `ServerStorage/Proto_Restore/UniaoBackup/Carvalho_Ancestral_01_corpo_original` (Tronco, Raizes, Cristas, RaizesCirculares) e removidos da árvore. Também removidos os detalhes soltos que espetavam as superfícies: 106 tiras de casca, 61 placas de madeira exposta e 76 mantas de musgo.
**Play:** 60,0 FPS (pior quadro 32 ms), vento na copa (até 0,68 studs), 0 erros no log de cliente e servidor, `ProfileLoaded=true`. Partes no protótipo 8.876. Corpo: casca sem relevo real, cores herdadas das peças (raízes enroladas mais claras que as cristas), algumas pontas finas das cristas e facetas nas junções.
**Perdas conhecidas:** deixaram de existir no `Carvalho_Ancestral_01` as tiras de casca soltas e a madeira exposta como peças separadas (as cores claras residuais vêm das cristas); o musgo restante é só o das cristas. Os galhos (`Galhos`, `GalhosLongos` etc.) continuam como cilindros separados que entram no corpo na forquilha. Outras 3 árvores não foram alteradas.

**Galhos retos fundidos ao tronco + ramos de folhas (pedido do usuário; só `Carvalho_Ancestral_01`):**
- Galhos antigos (80 + 192 + 176 + 156 cilindros em curva, 196 cipós e os 166 cachos da copa) removidos; backup como clones em `ServerStorage/Proto_Restore/UniaoBackup/Carvalho_Ancestral_01_galhos_original` (Galhos, GalhosExtras, GalhosSuperiores, GalhosLongos, Copa, Cipos) e `..._corpo_original/CorpoTronco_sem_galhos`.
- Novo sistema: 11 galhos principais RETOS (3 segmentos com desvio ≤3,5°, 20–40 studs, elevação 14–44°, afinando 0,8), 2 secundários retos por galho (2 segmentos) e 4 ramos pequenos, 2–3 raízes aéreas finas penduradas na parte de baixo de cada galho, poucas manchas de musgo no dorso, mais uma COROA de 5 galhos em V no topo (24–30 studs, 52–66°). Cada galho foi unido por `UnionAsync` (Precise) e depois TUDO foi fundido ao `CorpoTronco` num só `UnionOperation` (0,6 s). Cor da casca unificada.
- Ramos de folhas em volta dos galhos: 173 clusters (`Cacho`, tag `ProtoCopa`, vento mantido) em âncoras ao longo dos 45–100% externos de cada galho, em lados aleatórios, nos secundários, nos ramos pequenos e na coroa; cada cluster = 3 ramitos com folhas em losango dobrado, unidos em 1 union.
- **Play:** 60,0 FPS (pior quadro 23 ms), vento nas unions de folhas (até 0,42 studs; vento 13/2,4), 0 erros nos logs, `ProfileLoaded=true`. Partes no protótipo 7.833 (1.849 unions). Só PC/Studio.
- **Limites:** casca sem relevo real, cores lisas, algumas pontas de galho/coroa sem folhas; folhas uniformes (losangos) e escuras contra o sol; ainda só 1 das 4 árvores; as outras 3 mantêm o sistema antigo.

**Etapa 1 do plano "mais realista": folhas com textura e malha criadas por código (teste, 2026-10-20):**
- **Funcionou no Studio (modo Edit):** `AssetService:CreateEditableImage/CreateEditableMesh` + `SurfaceAppearance` com `ColorMapContent` e `AlphaMode=Transparency`. Pintei uma textura de folha de carvalho 256×256 (fundo transparente, nervura central e laterais, borda recortada, manchas de verde) e uma malha de folha curva e dobrada; um ramo com 58 folhas fundidas numa única `MeshPart` (~7.400 triângulos) ficou bem mais realista que os losangos de Parts (capturas 22–24).
- **Bloqueio encontrado:** em Play o conteúdo some (`MeshContent`/`ColorMapContent` = None), e a criação em tempo de execução no cliente falha com "EditableImage is not accessible. Go to the Security Tab in Experience Settings to enable this API." Ou seja, o resultado NÃO sobrevive ao Play/publicação enquanto as APIs Editable não forem habilitadas em Game Settings > Security (ação do usuário; pode exigir verificação de conta) ou a malha e a textura forem publicadas como assets (upload; custo/moderação não verificados).
- Demo removida do Studio; nada do protótipo foi alterado (7.833 partes). Código da folha e do ramo está no histórico desta sessão.

**Etapa 1 aplicada: folhas reais no `Carvalho_Ancestral_01` (após o usuário habilitar as APIs Editable em Game Settings > Security; Play, 2026-10-20):**
- **Script `Proto_FlorestaAncestral/Proto_FolhasReais` (cliente):** pinta uma textura de folha de carvalho (EditableImage 256×256, nervuras e manchas) e cria 2 modelos de folha (EditableMesh 14×3 com contorno lobado NA GEOMETRIA, curvos e dobrados). Perto da câmera (alcance 60 studs no nível 3, 100 no nível 4; desligado nos níveis 1–2), cada cacho tem a union de losangos ocultada só localmente e ganha ~36 `MeshPart` "Folha" clonadas dos 2 modelos, posicionadas ao longo dos ramitos; ao se afastar (85/130 studs) voltam as unions. As folhas reais entram no sistema de vento (balanço e tremular) por novo cadastro da tag `ProtoCopa`.
- **Restrições descobertas (não são óbvias):** (1) o orçamento de Editable do cliente é minúsculo (cerca de 3–4 objetos EditableMesh/Image ao mesmo tempo no Studio; malha única até 20 mil vértices), por isso as folhas são CLONES de só 2 malhas; (2) `SurfaceAppearance.ColorMapContent` NÃO é gravável por scripts de jogo (exige capacidade Plugin): a textura vai em `MeshPart.TextureContent`, que ignora o alfa (por isso o contorno da folha está na malha); (3) o que é criado em Edit some no Play, então tudo é gerado no cliente no início do jogo.
- **Medições em Play (PC/Studio):** 17 clusters/612 folhas com o jogador a 50 studs; com a câmera sobre a copa 142 clusters/≈5.100 folhas reais, 59,9 FPS (pior quadro 47 ms); vento: deslocamento máx 0,43–0,80 studs e rotação visível nas folhas reais; 0 erros no log do cliente (sem contar UIBlox) e 0 no servidor, `ProfileLoaded=true`. Capturas de Play 25–26 (as de Edit 22–24 mostram o primeiro protótipo).
- **Limites:** só `Carvalho_Ancestral_01`; as folhas ainda são todas do mesmo tipo (carvalho) e com iluminação e sombra pouco refinadas; casca, tronco e raízes seguem em Parts; mobile e jogo publicado NÃO testados (a API depende da configuração de segurança do lugar e do orçamento de Editable no dispositivo).

**Etapa 2 (casca real) e correção das folhas que "sumiam" (pedido do usuário, 2026-10-20):**
- **Causa do sumiço ao afastar a câmera (2 causas, ambas corrigidas):** (1) as folhas reais só existiam a menos de 60 studs (volta aos losangos a partir de 85), então ao afastar o zoom havia uma troca visível entre dois tipos de folha e a copa parecia perder volume; agora 120 studs (volta só além de 190; nível 4: 170/240). (2) a adaptação de qualidade por FPS (`Proto_Qualidade`) baixava o nível após picos curtos (carregamento, zoom), o que desligava as folhas reais e ocultava detalhes (ramitos, musgo, serapilheira); agora só desce após 4 janelas de 5 s abaixo de 24 FPS (20 s sustentados), depois de 60 s de jogo e com 30 s entre mudanças. Auditoria em Play a 17, 85, 145, 200 e 270 studs: 0 clusters invisíveis; a 200–270 studs voltam os losangos por distância (esperado).
- **`Proto_CascaReal` (cliente):** pinta uma textura de casca 192×192 (fendas escuras, cristas claras, musgo vivo em manchas, tiras de madeira exposta) e uma luva de tronco (EditableMesh 64×72, dupla face, cristas irregulares, base alargada 34%) do chão até o topo do tronco, aplicada com `MeshPart.TextureContent`; escala por atributo `SleeveScale` (1,46) para cobrir as cristas de Parts do tronco (que ficam por baixo). Raízes, anéis e galhos de Parts continuam por cima. Só nível ≥ 3.
- **Restrições novas:** `MaterialVariant`/`SurfaceAppearance` por script de jogo exigem capacidade Plugin (por isso a casca é malha própria); orçamento Editable do cliente ≈ 4 objetos (agora: 2 imagens + 3 malhas, funcionando); scripts se coordenam por `workspace.ProtoEditableReady`.
- **Play:** 60,0 FPS (pior quadro 25 ms), 173 clusters com folhas reais, `CascaReal` criada, 0 avisos/erros do projeto, nível 3 estável. Capturas 27–28. **Limites:** pontas de algumas cristas de Parts ainda furam a luva perto do chão; as pontas dos galhos mostram "colar" de cilindro; as 3 outras árvores e as samambaias do chão continuam com losangos; mobile/publicado não testados (a API depende de Game Settings > Security e do orçamento no aparelho).

**Etapa 2b: samambaias, raízes e galhos reais (pedido do usuário, 2026-10-20):**
- **`Proto_Samambaias` (cliente):** frondes com pínulas em malha (18 pares de losangos + ráquis) e plantas de folha larga em malha, texturizadas (atlas 256×128); convertem as plantas do `Sotobosque` a menos de 95 (nível 3) / 130 (nível 4) studs, 4 por ciclo de 0,3 s, e voltam além de 135/180; entram no vento pela tag `ProtoSamambaia`. Atributo `workspace.ProtoSamambaiasReais` = plantas convertidas.
- **`Proto_RaizesGalhos` (cliente):** tubos lofteados com a textura da casca: `GalhosRaizesReais` (117 galhos pelo esqueleto exato `BranchesJSON` + 48 raízes de chão `RootsJSON`) e `RaizesEnroladasReais` (14 raízes grossas, 3 anéis e 9 trepadeiras enroladas no tronco). Perto da câmera (nível ≥ 3, < 200 studs) a union `CorpoTronco` e as Parts `Detalhe*` ficam ocultas só localmente.
- **Causa dos trechos "brancos" (tronco creme e metade das pínulas):** convenção de normais. No EditableMesh a face visível de um triângulo (a,b,c) é o lado da normal geométrica pela regra da mão direita; normais atribuídas ao contrário deixavam a face voltada para a câmera iluminada como se estivesse virada para o sol (estourava). Corrigido na luva do tronco (faces trocadas) e nas pínulas (normal calculada pela geometria). Folhas, tubos e folha larga já estavam corretos.
- **Play (PC/Studio):** ≈59 FPS, 101–107 plantas convertidas, `CascaReal`/`GalhosRaizesReais`/`RaizesEnroladasReais` criadas, 0 erros do projeto no log. Capturas 29–31.
- **Limites:** só `Carvalho_Ancestral_01` (as outras 3 árvores e os freixos continuam com Parts); as plantas do `Sotobosque` são todas convertidas pelo mesmo modelo; textura procedural ainda abaixo da referência (a textura tilha visivelmente nas raízes); mobile e jogo publicado NÃO testados. Iluminação avançada (Future) depende de ativação pelo usuário.

**Etapa 2c: madeira e folhas reais nas outras 3 árvores (Freixo_Antigo_01, Carvalho_Jovem_01, Freixo_Velho_01; 2026-10-20):**
- **`Proto_MadeiraReal` (cliente, novo):** como essas árvores não têm esqueleto (só Parts), cada cilindro de `Tronco`, `Raizes`, `Galhos`, `GalhosExtras/Superiores/Longos` é trocado, perto da câmera, por um CLONE de um único tubo (EditableMesh de 8 lados com tampas) texturizado com a casca; originais ocultos só localmente e restaurados ao afastar (lotes de 150 por ciclo). Alcance nível 3: 70 studs (volta além de 100); nível 4: 100/140 com sombra. Atributo `ProtoMadeiraReais` = árvores completas. As unions (`RaizesCirculares`) e cipós/musgo continuam como estavam.
- **`Proto_FolhasReais`** agora cobre as 4 copas; freixos usam folha mais estreita (×0,6 de largura); as 3 secundárias têm 55% do alcance do Carvalho Ancestral (desempenho).
- **Orçamento de Editable:** a criação de mais uma malha falhou ("memory budget"); para liberar espaço o modelo de folha agora é 1 só (antes 2) e a luva do tronco e os tubos foram simplificados (luva 44×56; galhos/raízes 6 lados). Isso reduz um pouco o detalhe do Carvalho Ancestral.
- **Play:** 59–60 FPS com 2.185 clones de madeira e 215–300 cachos de folhas reais; 0 erros do projeto. Capturas 32–34. **Ocorrência não explicada:** em duas sessões consecutivas medi 14 FPS (antes de reduzir alcances e depois, até com a madeira desligada pelo nível 2) e em outras execuções idênticas 59–60 FPS; não consegui reproduzir a causa (suspeita: carga do Studio/tamanho do conjunto convertido). Precisa de teste em outro PC/celular.
- **Limites:** a textura tilha/estica nos cilindros curtos (discos do tronco mostram faixas repetidas); sem esqueleto, não há emendas suaves entre segmentos; folhas ainda de carvalho nos freixos (só mais estreitas); mobile/publicado não testados.

**Etapa 3: iluminação sem Future (2026-10-20):**
- **Future NÃO foi ativado:** `Lighting.Technology` não aparece nas propriedades do Studio do usuário (nem em Studio Settings > Rendering) e não é legível/gravável por script (capacidade RobloxScript). Teste visual com PointLight (Shadows=true) não mostrou sombra do bloco, sugerindo tecnologia sem Future. Luz volumétrica e sombras de luzes de ponto reais ficam pendentes disso.
- **`Proto_FeixosLuz` (cliente, novo):** feixes de luz fake = pilhas de 6 blocos Neon muito transparentes (borda suave) alinhados com `Lighting:GetSunDirection()`, partindo do chão onde o sol chega; pulsam devagar com o vento; só dentro da área do protótipo e só local (pasta `ProtoFeixosLocal`). Nível 1–2: 0; nível 3: 9; nível 4: 16 (verificado em Play ao trocar `ProtoQualidade`). Iluminação base (sol baixo, névoa, SunRays, bloom, correção de cor, sombras) já vinha de `Proto_Qualidade`. Capturas 35–36.
- **FPS:** a medição neste Studio oscila entre 59–60 e 14–15 FPS sem relação com nenhum script (desativar vento, madeira, folhas, samambaias ou os feixes não mudou os 14 FPS; `Stats.FrameTime` ≈ 67 ms com Heartbeat ≈ 0,04 ms, ou seja, gargalo de renderização/Studio, possivelmente o Frame Rate Manager em "Automatic"). **Desempenho real NÃO está comprovado**; falta teste em outro PC e em celular.
- **Limites:** feixes são blocos, não luz real: de perto mostram bordas muito sutis e atravessam objetos; sem sombras de luzes de ponto; sem teste no celular.

**M2.0 — Trecho parcial da Floresta Ancestral ao redor da árvore ancestral (autorizado pelo usuário; 2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Chunk:** X 1270–1430, Z −132 a +28, tudo em `Workspace/Proto_FlorestaAncestral/Chunk_Ancestral/{Estrutura,Arvores,Vegetacao,Rochas}`. Árvore ancestral (1350, −52) e sistemas de dados NÃO alterados. Cópia de segurança do terreno do chunk: `ServerStorage/Proto_Restore/TerrainChunkAntes` (TerrainRegion; restaurar com `Terrain:PasteRegion(reg, Vector3int16.new(316,-6,-34), true)`; o usuário ainda deve salvar o .rbxl para guardá-la em arquivo).
- **Trilhas:** principal sinuosa (entra pelo sudeste ~(1432,24), chega à base da árvore ~(1353,−44)) + ramal à estrutura + ramal oeste; pintadas no Terrain (Mud/Ground, 209 voxels de superfície, altura inalterada) e 19 lajes de pedra na trilha principal.
- **Estrutura híbrida (centro (1396,−54), de frente para a árvore):** `Santuario_Ruinas` (313 partes: base e lajes, 3 degraus, 2 pilares com painéis de inscrição, arco parcial de aduelas, pilar sul quebrado, tambores e entulho caídos, musgo, raízes helicoidais e trepadeiras) e `Posto_Exploradores` (85 partes: abrigo de postes e vigas com cobertura de tecido, mesa com mapas, bancos, caixas, 3 barris, cordas, esteira, mochila, 2 lanternas com PointLight sem sombra, fogueira com Fire). Sotobosque existente removido só na pegada (15 modelos). Imagem do santuário citada pelo usuário foi usada como direção (arco, pilares com musgo/raízes, tendas, trilha de pedras).
- **Floresta:** 6 árvores secundárias (clones escalados 0,4–0,9 de Carvalho_Jovem, Freixo_Antigo e Freixo_Velho, sem Cipos/Detalhes/GalhosExtras para reduzir partes; ~7,7 mil partes) em borda/agrupamentos; 92 samambaias/folhas largas novas (clones em `Sotobosque`, atributo `Chunk=true`, convertidas pelos scripts existentes), 38 arbustos, 28 grupos de flores, 31 rochas, 36 raízes aparentes, 3 troncos caídos. Interior mais aberto, bordas mais densas.
- **Scripts ajustados:** `Proto_MadeiraReal` e `Proto_FolhasReais` agora também cobrem `Chunk_Ancestral/Arvores`.
- **Play:** sem erros do projeto no Output; 60 FPS medido na trilha, mas o Studio oscila 14–60 FPS sem causa isolada (ver Etapa 3); `Stats.PrimitivesCount` ≈ 37,8 mil com tudo convertido, `InstanceCount` ≈ 88 mil — ALTO para celular. Capturas 38–43.
- **Limites:** cobertura de tecido e pedra ainda parecem de Parts (sem malha texturizada própria); sem sistema de otimização do chunk (não pedido); samambaias grandes demais podem tapar a câmera perto da trilha; nenhum teste em celular; colisão simplificada (Parts), mas a rota principal está livre.

**M2.0 — Refinamento visual e otimização localizada do chunk (2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Maiores custos (antes):** (1) folhas reais (~450 cachos × ~36 malhas); (2) árvores de Parts (≈13,4 mil partes: 3 originais + 6 do chunk, 1.755 unions e muitas raízes); (3) sotobosque (945 unions de samambaias + ~3 mil malhas de fronde).
- **Correções:** folhas reais 5 por lado nas 3 árvores secundárias e 3 nas do chunk (antes 6), maiores para manter a densidade; 1.055 raízes (≈metade) das árvores do chunk removidas; 844 sombras de partes pequenas/vegetação desligadas; 19 plantas do chunk removidas e as demais −15% de tamanho (nenhuma árvore removida); feixos de luz 6/12 (antes 9/16) com 4 camadas; iluminação local do preset (só na zona, via `Proto_Qualidade`): Brightness 2,6→2,2, raios 0,24→0,10, bloom 0,40→0,28, glare 0,5→0,3 (global não alterado).
- **Ruína/posto:** pedras envelhecidas (48: inclinação/deslocamento leve, cor verde-musgo mais forte perto do chão), 14 lascas nas arestas, degrau final quebrado; integração: corda de ligação do pilar sul ao poste do abrigo, pano de marcação no pilar norte, 5 lajes de passagem; 12 miudezas do posto removidas.
- **Antes → depois (Play, 4 pontos fixos, capturas 44–47 e 48–51):** primitivas 34,6–38,0 mil → 28,6–30,2 mil (−17 a −21%); instâncias 85,2–88,6 mil → 79,1–80,7 mil (−7%); memória do cliente ≈7,9 GB → ≈8,0 GB (sem mudança; medida do Studio, não confiável para celular); FPS 59–60 em todos antes; depois 59–59 em V1/V2 mas 14 em V3/V4 — a mesma oscilação 14↔60 já registrada (não reproduzida por script), e não uma regressão comprovada.
- **Limites:** redução modesta (o grosso ainda são as unions/Parts das árvores); a corda de ligação cruza as cordas do abrigo em V3; instâncias ainda ~80 mil (alto para celular); nenhuma medição em celular; sistema de perfis gráficos não implementado (não pedido).

**M2.0 — Rodada final de refinamento do chunk (2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Luz (só preset local de `Proto_Qualidade` e feixos; global intocado):** raios 0,10→0,06 (nível 3) e 0,16→0,10 (nível 4); bloom 0,28→0,20 (n3) e 0,40→0,30 (n4), limiar mais alto; feixos 6→4 (n3) e 12→8 (n4), 3 camadas mais transparentes e sem nascer perto da árvore ancestral nem da estrutura.
- **Vegetação:** só 17 plantas do foreground (≤16 studs das trilhas) removidas/reduzidas (já havia pouca ali); arbustos/flores não tocados; laterais e fundo intactos.
- **Ruína (tamanho e posição iguais):** +38 rachaduras (faixas escuras), +26 manchas de musgo vertical nas bases, +8 blocos quebrados e uma cunha de ruptura no pilar sul.
- **Trilha:** 160 voxels repintados (principal em Mud mais larga, bordas em Ground; ramais mais estreitos só em Ground) + 44 pedrinhas de borda.
- **Otimização local:** `CanQuery` desligado em 1.630 partes decorativas (menos custo de raycast/seleção); sombras já desligadas na rodada anterior; não houve remoção de árvores.
- **Antes (rodada anterior) → depois (Play, mesmos 4 pontos; capturas 48–51 → 52–55):** primitivas 28,6–30,2 mil → 28,5–30,0 mil; instâncias 79,1–80,7 mil → 79,0–80,5 mil (praticamente iguais: esta rodada foi visual); FPS 59/59/14/14 → 60/60/59/48 (oscilação do Studio, não atribuível a estas mudanças); memória reportada 8,0 → 8,9 GB (medida do Studio, não confiável).
- **Limites:** a corda de ligação ainda cruza as cordas do abrigo em V3; a árvore ancestral ainda divide o foreground com samambaias grandes (V1 lado esquerdo é a copa de árvore do chunk, não samambaia); sem teste em celular.

**M2.0 — Expansão (~3× o chunk) da Floresta Ancestral (2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Área:** X ≈1200–1530, Z ≈−195 a +40 (≈330×235 studs, dentro da zona do protótipo; chunk aprovado e árvore ancestral intocados). Premissa: o tamanho total do bioma não está definido nos documentos, então "1/3" foi interpretado como ≈3× o chunk (≈78 mil studs² contra 25 mil); precisa de confirmação. Backups de terreno: `ServerStorage/Proto_Restore/TerrainChunkAntes` e `TerrainExpansaoAntes` (o usuário ainda deve salvar o .rbxl).
- **Trilhas (Terrain, 634 voxels):** principal estendida do leste (1530,6) até a árvore, trilha norte (continuação da principal, larga) até (1272,−176), ramal oeste prolongado até (1218,−40), mais 3 secundárias estreitas (s1 até o altar; s2 escondida até o santuário menor; s3 escondida até o marco). Clareiras (sem árvores): 4 médias/pequenas além das do chunk.
- **Árvores (34 novas, `Chunk_Ancestral/Arvores/x_*`):** clones de Carvalho/Freixo Antigo/Freixo Velho, escala 0,4–0,95, rotação aleatória, bosques por ruído, afastadas das trilhas (≥11), três variantes de custo (completa/média/leve, sem cipós, 30–50% dos cachos removidos) ≈25,6 mil partes.
- **Vegetação e peças:** +138 samambaias/folhas largas (atributo `Exp`), 55 arbustos, 16 grupos de flores, 31 rochas, 9 troncos caídos, afastados das trilhas.
- **Pontos de interesse (≈125 partes):** `POI_Altar` (1505,−118: plataforma circular, altar com runas, 3 monólitos, raízes), `POI_SantuarioMenor` (1236,−160: arco quebrado, 2 pilares, degrau), `POI_MarcoAcampamento` (marco de pedra + vestígio de acampamento em ≈(1219,15); reposicionado após ficar em declive). O posto principal é o já aprovado no chunk.
- **Play:** sem erros do projeto no Output; primitivas carregadas 44,7–51,3 mil (antes do chunk: ≈28–30 mil) e instâncias 98–105 mil (Studio não descarregou áreas distantes apesar de StreamingEnabled). FPS: 59 em vistas distantes, mas 14 perto do altar, santuário menor e acampamento. A queda para 14 FPS já ocorria antes da expansão sem causa isolada (ficou 14 também com as 34 árvores removidas no cliente), por isso NÃO atribuo à expansão, mas também NÃO está provado que ela não pesa. Memória do cliente ≈8,0–9,0 GB (medida do Studio).
- **Limites/observações:** capturas do altar e do santuário saíram com a câmera dentro de folhagem (precisam de nova pose); a densidade da expansão é menor que a do chunk; árvores leves ficam com copa mais rala; mobile e jogo publicado não testados; o adaptativo de qualidade pode cair para o nível 1 se o FPS do Studio ficar em 14 (isso desliga folhas reais).

**PLANEJAMENTO DE ESCALA — Floresta Ancestral e continente (aprovado como BASE, ajustável; nenhuma construção autorizada ainda; 2026-10-20):**
- **Continente:** ≈ 9.600 × 7.000 studs (≈ 67 M studs², forma irregular com mar/rios/barreiras). Baseplate atual (2048², −1024 a +1024) é placeholder; o terreno existente é só X 1200–1600 × Z −200 a +200. Premissa de deslocamento NÃO confirmada: 16 studs/s a pé (padrão Roblox), percurso sinuoso ×1,35; montaria/voo são hipóteses.
- **Biomas (área jogável aprox.):** Floresta Ancestral 2.800×2.800; Montanhas Altas 2.400×3.000; Planícies Douradas 3.000×2.400; Deserto de Cristal 2.600×2.400; Tundra 2.400×2.200; Pântano 2.200×2.200; Costas Selvagens 3.200×1.400; Terras Corrompidas 2.000×2.200. Adjacências da floresta (propostas): Montanhas ao norte, Planícies a leste, Pântano ao sul, Costas a oeste. Posições dos outros biomas ainda não definidas.
- **Floresta Ancestral:** X 0–2800 × Z −1500 a +1300 (centro 1400, −100; árvore ancestral em 1350, −52 preservada, junto com santuário, posto, altar e demais construções aprovadas). Setores: S0 Núcleo Ancestral (X 950–1850, Z −550 a 350); S1 Vila Madeireira (X 1950–2450, Z 150–650); S2 Mata Profunda (X 900–2000, Z 400–1100); **S3 Bosques Selvagens** (X 150–900, Z −500 a 500; substitui "Vale dos Ninhos"); S4 Colinas das Ruínas (X 100–950, Z 500–1300); S5 Vale do Rio (X 900–2000, Z −1500 a −600); S6 Penhascos Leste (X 1850–2800, Z −1500 a −100).
- **Ninhos:** NÃO concentrados em um setor; distribuídos por toda a floresta conforme habitat (lobos: tocas sob raízes gigantes, bosques densos e pequenas cavernas; ursos: cavernas em encostas e rochas; outras criaturas: habitats da espécie, sem inventar espécies). Visíveis, escondidos e protegidos, com espaço para guardiões e encontros; apenas ÁREAS RESERVADAS, sem sistema funcional.
- **Dungeons:** 3 reservas espaciais apenas (≈ (500,1000) em S4, (1500,−1250) em S5, (2500,−700) em S6), NÃO confirmam três dungeons.
- **Trilhas:** Estrada Antiga oeste–leste (≈ 3.500 studs) e Trilha dos Lenhadores norte–sul (≈ 3.800) + 5 secundárias (2 escondidas). Missões regionais (6) distribuídas pelos setores.
- **Primeiro terço (condicionado a terreno livre, integração e desempenho):** X 900–2450 × Z −550 a +1100 (≈ 2,56 M studs², 33%).
- **Ordem de construção:** (1) macroterreno, setores e trilhas; (2) espaços reservados (vila, estruturas, ninhos, combate); (3) vegetação representativa em blocos controlados; (4) refinamento de espécies. Sem replicar milhares de modelos pesados sem medição. Desempenho: StreamingEnabled já ativo, mas não reduz custo do carregado (orçamento alvo ≈ 50 mil primitivas no raio carregado; 3 níveis de modelo por espécie; pastas por espécie/setor com pivô e atributo de espécie).

**ETAPA 1 — Macroterreno do S0 e trilhas (autorizada; 2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Backups:** `ServerStorage/Proto_Restore/TerrainS0Antes_1..4` (quatro `TerrainRegion` cobrindo voxels x 225–462, y −6–20, z −138–88; restaurar com `Terrain:PasteRegion(reg, Vector3int16.new(minx,miny,minz), true)` usando o canto mínimo de cada parte: (225,−6,−138), (344,−6,−138), (225,−6,−25), (344,−6,−25)), mais os backups anteriores do chunk/expansão. O usuário ainda deve salvar o .rbxl.
- **Terreno:** gerado em X 900–1852 × Z −552 a 356 SÓ nas colunas fora do retângulo existente (X 1200–1600, Z −200 a 200), que ficou com alturas intactas; ao redor, mistura suave de 130 studs com a altura da borda existente. Relevo: colinas com cristas, vale a sul, bacia a oeste, colina alta a nordeste e morro a sudeste, alturas 8–62; materiais por inclinação (Rock >62%, Ground >34%, Grass/LeafyGrass). A primeira geração (relevo fraco) foi descartada e refeita (captura 64 mostra a descartada). A bordas externas do bloco terminam em parede reta (vão se conectar nas próximas etapas).
- **Trilhas (materiais Mud/Ground, sem mudar alturas):** Estrada Antiga oeste (900,−130)→(1218,−40) (340 studs); leste (1486,20)→(1850,182) (406), reroteada pela passagem de menor inclinação no anel de colinas existente (a primeira rota tinha 118% de inclinação); Lenhadores sul (1450,−550)→(1272,−176) (419) e norte (1432,24)→(1480,352) (341); 3 ocultas: A (1070,−92)→(1230,−350) (330), B (1460,120)→(1100,340) (423), C (1680,40)→(1830,−400) (465) + ligação. Resto de um trecho antigo pintado dentro do retângulo ficou como ramal cego curto.
- **Paredes `Limites`:** movidas para envolver o S0 (X 896–1860, Z −560 a 364); posições antigas nos atributos `PosAntes`/`TamAntes` de cada parede.
- **Testes:** inclinação máxima ao longo das trilhas 14–66% (nenhum trecho >70%); emenda do retângulo: degrau máx. 7,6 studs em 6 studs (herdado do anel de colinas existente, medido na primeira geração); caminhada com `character_navigation` concluída (distância final 0) nas 4 trilhas principais na primeira geração e em oeste e sul na versão final; a caminhada leste da versão final NÃO foi concluída porque o Studio perdeu a conexão (timeout). Sem vegetação nova; primitivas inalteradas (≈44,8 mil, 98 mil instâncias); FPS marcou 14 nas vistas aéreas (a oscilação do Studio já registrada; não comprovada como efeito do terreno).
- **Pendências:** capturas ao nível do jogador do terreno final não foram feitas (só 2 aéreas, 62–63, com neblina forte); se o Studio fechou sem salvar, o terreno do S0 pode ter sido perdido (reabrir e conferir; os scripts de geração estão no histórico desta sessão).

**Etapa 1 — complemento (2026-10-20):** após reabrir o Studio, terreno do S0, paredes `Limites` e 8 backups conferidos. Caminhada pela trilha leste concluída (distância final 0), agora nas 4 trilhas principais da versão final. FPS 59–60 nas 4 capturas ao nível do jogador (65–68). Sem vegetação nova. Aparência: relevo e trilhas legíveis, mas o chão do S0 está vazio (sem árvores, esperado nesta etapa); o fim leste termina em penhasco reto (borda do bloco).
**Backup (2026-10-20):** o usuário informou ter salvo um backup do .rbxl após a Etapa 1 do S0 (nome e caminho não informados; não verificados por mim).
**ETAPA 2A — setor representativo de vegetação (2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Setor:** X 1000–1340 × Z −548 a −218 (≈112 mil studs², sudoeste do S0, fora do protótipo e do chunk). Pasta `Workspace/Proto_FlorestaAncestral/Floresta/{_Modelos,Carvalho,Freixo,Jovem,TroncoSeco,Arbusto,Reservas}`; cada instância tem atributos `Especie` e `Setor="S0_SO"` e é clone de um modelo-base em `_Modelos` (trocar o modelo-base e re-clonar permite refinar sem reposicionar).
- **Conteúdo:** 320 árvores de baixo custo (≈14 partes: tronco, raízes em cunha, copas em elipsoides achatados; escala 0,7–1,35, rotação e inclinação aleatórias, cor de copa variada; ruído de densidade para bosques e corredores) e 50 arbustos; ≈3,8 mil partes no total. Modelos NÃO usam os scripts de folhas/madeira reais.
- **Reservas (peças invisíveis com atributos `Tipo/Detalhe/Estado="Reservado"`):** 3 clareiras (2 de combate, raio 30 e 24, 1 menor), 5 ninhos distribuídos por habitat (urso visível e oculto em encostas, lobo sob raízes e lobo protegido em bosque denso, refúgio de rocha). Nada funcional.
- **Fim da trilha leste:** última parte da trilha desbotada para grama (x>1790) e a borda leste do terreno rebaixada gradualmente (x 1800–1852) até ≈4–14 studs, sem parede nova. O terreno aprovado foi alterado só nessa faixa de borda (~2.840 colunas); sem backup específico além dos anteriores (a faixa estava coberta apenas pelos backups do S0 quando gerada? NÃO: a faixa do S0 não tem backup pós-Etapa 1).
- **Medidas (Play):** antes ≈44,8 mil primitivas/98 mil instâncias → depois 48,5 mil/102 mil (+3,7 mil prim., +4 mil inst.); memória do Studio ≈7,4–7,6 GB; FPS 59 em todas as vistas desta rodada (o Studio ainda pode oscilar para 14). Mobile NÃO testado; não se pode afirmar desempenho adequado para celular.
- **Avaliação visual honesta:** a silhueta é de "arbustos esféricos/topiaria", claramente inferior às árvores aprovadas (primeira versão em captura 73; achatar copas e aumentar densidade melhorou só um pouco). A densidade percebida é de bosque, mas a aparência não tem identidade de fantasia realista. O modelo-base precisa ser refeito (copas com malha/folhas em camadas ou reaproveitar as árvores leves aprovadas em menor número) antes de replicar. Capturas 69–72.

**ETAPA 2A — v2 com as árvores do estilo aprovado (2026-10-20, a pedido do usuário):** as 320 árvores-bolha foram removidas; no lugar, 46 clones das árvores aprovadas (Carvalho_Jovem → `Carvalho` 14, Freixo_Antigo → `FreixoAntigo` 11, Freixo_Velho → `FreixoVelho` 14 e `TroncoSeco` 7 = Freixo Velho sem copa), escala 0,5–0,95, versões leves (sem cipós/detalhes/galhos extras/raízes de solo, 35–45% dos cachos removidos) em `Floresta/<espécie>/SO_xxx`, base em `Floresta/_Modelos`. `Proto_FolhasReais` e `Proto_MadeiraReal` agora também varrem `Floresta/*`, então folhas e madeira reais aparecem perto da câmera. Arbustos, reservas (clareiras e 5 ninhos) e o fim da trilha leste mantidos.
- **Custo (Play):** primitivas 44,8 mil → 86,9–89,8 mil (+≈42 mil, só o setor de 46 árvores = ≈41,9 mil partes); instâncias 98 mil → 143–146 mil; memória do Studio ≈8,7 GB; FPS 59/58 ao nível do jogador e 41 na vista aérea (mais pesado que a v1, que dava 59). Replicar por todo o primeiro terço no mesmo padrão NÃO é viável sem otimização (≈25× esta área ⇒ milhões de partes); é preciso um modelo muito mais barato por árvore (≈300–500 partes) ou LOD/instanciamento antes de expandir. Mobile não testado.
- **Visual:** silhueta e folhas muito mais próximas das árvores aprovadas; copas ainda ralas de longe (35–45% dos cachos removidos) e troncos de pedaços empilhados aparecem de perto. Capturas 74–75.
**ETAPA 2A — v3 árvores completas no estilo aprovado (2026-10-20, a pedido do usuário: "deixe assim e aprimore"):** as 46 árvores do setor foram recriadas a partir de `Floresta/_ModelosV2` com copas mais cheias (12–15% dos cachos removidos, antes 35–45%), raízes de solo (50–70% mantidas), galhos extras (metade), cipós e detalhes de musgo; posições, escalas e rotações iguais. `_Modelos` (v2) ainda existe na pasta `Floresta` com os modelos leves anteriores (pode ser removido).
- **Custo (Play):** setor ≈69 mil partes de árvores (v2: ≈42 mil); primitivas totais 126–128 mil (antes da etapa 44,8 mil), instâncias 185–187 mil, memória do Studio ≈10,9 GB; FPS 59 ao nível do jogador, 26 na vista aérea. Isto é MUITO pesado: só 112 mil studs² (≈4% do primeiro terço) já passam de 2,5× o orçamento citado (≈50 mil primitivas). Replicar este padrão pelo primeiro terço não é possível sem LOD/instanciamento ou um modelo bem mais barato; celular não testado e certamente não adequado assim.
- **Visual:** troncos com raízes enroladas, folhas reais, galhos e cipós como nas árvores-teste; capturas 76–77.
**OTIMIZAÇÃO DE UMA ÁRVORE (Carvalho SO_004; 2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Contagem do original (1.102 partes):** Tronco 77 (66 lobos + 11 núcleos, 5 com colisão), Raízes 173, Galhos 60, Copa 434 (227 ramitos + 207 unions de folhas em 75 cachos), Cipós 46, Detalhes 25 (musgo/madeira exposta/cogumelos), GalhosExtras 63, GalhosSuperiores 110, GalhosLongos 78, RaizesCirculares 15 (unions), DetalheRaizes 21.
- **Versão otimizada (308 partes, −72%):** corpo (tronco, raízes, galhos, galhos longos/superiores, anéis; 557 cilindros) fundido em UMA `UnionOperation` (`CorpoArvore`, CollisionFidelity Box, textura de material mantida, sem sombra/consulta), 5 colisores originais do tronco mantidos invisíveis, cachos com as folhas de losango fundidas em 1 union por cacho (53 cachos; 75 folhas contra 207; os 75 cachos mantêm tag `ProtoCopa`, vento e folhas reais continuam funcionando — 1.362 MeshParts de folha reais em ambas ao se aproximar). Removidos cipós, musgo, cogumelos e detalhes finos (≈160 partes que não mudam a silhueta).
- **Medidas (Play):** primitivas por árvore 1.120 → 380 (−66%); pior caso de fusão: 0 peças descartadas. Colisão: o personagem parou no mesmo ponto (z=−5) nas duas ao andar contra o tronco. Output: sem erros do projeto. FPS 59 a 130 studs; 15 a 70 studs nas duas (oscilação do Studio, não distingue as árvores).
- **Comparação (mesma distância/luz, par isolado no Baseplate em `Floresta/_Comparacao`; capturas 78–81):** a otimizada perde cipós verdes e as manchas de musgo; silhueta, raízes enroladas, copa e folhas reais ficam praticamente iguais; de perto os cortes entre peças aparecem um pouco menos (fusão).
- **Limites/pendências:** no teste de 70 studs a árvore de comparação anterior (sem a fusão) mostrou troncos escuros (sombra) — descartado; fusão de `UnionOperation` pode alterar levemente o brilho; as outras 45 árvores NÃO foram substituídas; `_Comparacao` e `_Otimizado` (primeira versão) devem ser limpos antes de expandir; modelos-base V1/V2 estão em `ServerStorage/Proto_Restore`. Estimativa se aplicado às 46 árvores: ≈17,5 mil partes (de ≈69 mil) — ainda alto para celular sem LOD.
**VENTO DIRECIONAL (árvore otimizada; 2026-10-20) — AGUARDANDO AVALIAÇÃO:** árvore otimizada aprovada como base (comparação `Floresta/_Comparacao`, par movido para a clareira (1112/1150, −420)).
- **Servidor (`Proto_VentoServidor`):** a direção do `GlobalWind` agora varia só ±5° (antes ±35°) em torno de (1, 0, 0,45); a força segue em rajadas. Isso vale para TODO o protótipo (inclusive grama do Terrain e as outras árvores).
- **Cliente (`Proto_VentoCliente`), novo caminho só para a árvore otimizada** (ou para tudo com `workspace.ProtoVentoNovo=true`): copa/ramitos deslocam-se e inclinam-se a favor do vento (rotação em torno do eixo perpendicular ao vento no mundo, não mais no eixo local) por uma onda de rajada que viaja na direção do vento (mesma fase espacial para todas as árvores), pequena variação de fase/intensidade por árvore (±7%), e as folhas tremulam sempre para o lado do vento com pequena guinada. Tronco, raízes e galhos grossos não se movem (são a union `CorpoArvore` fora do ciclo).
- **Linhas de vento (`Proto_VentoLinhas`, cliente, novo):** 22 riscos finos translúcidos (nível 3; 40 no 4; 0 nos níveis 1–2) que atravessam o ar na direção de `GlobalWind`, em alturas 30–120 studs, só na zona do protótipo.
- **Medição (Play):** vento (0,93, 0,37); movimento médio das folhas 0,96 studs ao longo do vento contra 0,11 lateral; corpo da árvore 0,000 studs; FPS 59; sem erros do projeto no Output. Capturas 82–84 (84/83 são dois instantes da copa; o movimento só se vê ao vivo).
- **Limites:** amplitude visual ainda sutil em vento fraco; linhas podem passar por dentro de copas altas; as outras árvores ainda usam o balanço antigo (só trocam ao ligar `ProtoVentoNovo`); não testado em celular.
**Vento mais sutil (a pedido; 2026-10-20):** inclinação da copa 0,02+0,06·rajada, deslocamento até ≈0,6 stud, tremular das folhas 0,035+0,07·rajada, balanço 0,006; linhas de vento 10 (nível 3) / 18 (nível 4), espessura 0,05–0,1, 84–92% transparentes, velocidade 14. Medido em Play: amplitude das folhas ao longo do vento 0,41 studs (antes 0,96), lateral 0,02, corpo da árvore 0,000, 10 linhas; a captura aérea (85) já não mostra linhas visíveis em um quadro (ficam quase imperceptíveis). Só a árvore otimizada usa o vento novo.
**Linhas de vento em pares (a pedido; 2026-10-20):** cada risco agora é um par: linha maior (10–20 studs, antes 24–55) e uma menor (42% da maior) deslocada ~1 stud abaixo e à frente, mesma direção, mesma transparência quase total. 10 pares no nível 3 (20 partes), 18 no nível 4. Medido em Play: tamanhos 18/7, 11/5, 19/8; sem erros do projeto; captura 85.
**Vento aprovado e ativado em todas as árvores (2026-10-20):** `workspace` atributo `ProtoVentoNovo=true` (vale para qualquer cacho com tag `ProtoCopa`); pastas de teste `Floresta/_Comparacao` e `_Otimizado` removidas. Teste em Play num Freixo Antigo do setor: folhas 0,58 studs ao longo do vento, 0,01 lateral; FPS 35 (setor ainda com as 46 árvores completas de ≈69 mil partes; o Studio também oscila). As 45 árvores continuam NÃO otimizadas. Partes por modelo-base (sem otimizar): Carvalho 1.102, Freixo Antigo 1.892, Freixo Velho 1.771, Tronco Seco 1.181; árvores no setor: 14/11/14/7.
**Otimização das 46 árvores do setor (2026-10-20) — AGUARDANDO AVALIAÇÃO:** método aprovado aplicado em todas via `ServerStorage/Proto_Restore/OtimizadorArvores` (ModuleScript; marca `Otimizada=true`). Resultados (partes): Carvalho 14 árvores 15.428 → 4.312; Freixo Antigo 11: 20.812 → 6.017; Freixo Velho 14: 24.794 → 6.034; Tronco Seco 7: 8.267 → 42 (1 union + 5 colisores cada); total 69.301 → 16.405 (−76%). Falhas de união: 0. Play (aérea, mesmo ponto): primitivas 126–128 mil → 103,7 mil (só Carvalho) → 88,9 mil (+Freixo Antigo) → 61,9–63,6 mil (todas); instâncias 185 mil → 119–121 mil; FPS 40 (aérea) e 33 (nível do jogador) neste Studio (oscilante; não atribuível). Vento novo ativo (`ProtoVentoNovo`).
- **Atenção — arquivo:** a sessão final rodou no arquivo `114230639394991_AutoRecovery_2.rbxl` (o lugar original não reconectou); o usuário deve salvar este estado (File > Save As) para não perder as 46 árvores otimizadas, e conferir se o lugar original tem os trabalhos anteriores.
- **Artefatos visuais:** nas raízes enroladas das árvores escaladas aparecem triângulos escuros (faces da união, captura 87), mais visíveis de perto que na árvore de teste (escala 1); alguns Troncos Secos ficam como um único corpo cinza sem folhas (esperado). Pode melhorar com RenderFidelity Precise (mais triângulos) — não aplicado.
**Teste de RenderFidelity Precise nos corpos otimizados (2026-10-20):** aplicado nos 46 `CorpoArvore`; resultado visual praticamente igual (capturas 88 Automatic × 90 Precise na mesma árvore SO_034): os triângulos escuros e facetas das raízes enroladas continuam, portanto NÃO vêm da fidelidade da união (vêm da geometria dos cilindros originais sobrepostos e de poucos lados). Custo: memória do Studio 16,5 → 17,2 GB e FPS sem ganho; primitivas iguais (61,9 → 64,4 mil por carregamento). **Revertido para Automatic.** Correção real exigiria refazer as raízes enroladas como malha contínua (como em `Proto_RaizesGalhos`, que usa EditableMesh e já está no Carvalho Ancestral), com custo de memória Editable limitado.
**Menos árvores + raízes enroladas contínuas (a pedido; 2026-10-20, arquivo AutoRecovery) — AGUARDANDO AVALIAÇÃO:**
- **Árvores do setor: 46 → 28** (Carvalho 9, Freixo Antigo 6, Freixo Velho 6, Tronco Seco 7); partes 16.405 → 8.682. A remoção por vizinhança tirou Carvalhos demais; 6 Freixos Velhos amontoados foram trocados por Carvalhos (novas posições = as dos removidos). Distribuição menos densa, ainda irregular.
- **Raízes:** as `RaizesCirculares` ficaram fora do corpo unido (novas bases em `ServerStorage/Proto_Restore/Floresta_BaseSemRaizes`, regeradas do modelo V2 e fundidas sem as raízes anelares; as 28 árvores foram substituídas por clones na mesma posição/escala/rotação, atributos `CoilGround` e `CoilR`). Novo script cliente `Proto_RaizesEnroladas`: UMA malha EditableMesh (5 tubos lofteados em hélice, 6 lados, textura da casca do Carvalho Ancestral) clonada e escalada pelo raio do tronco; aparece só < 160 studs e nível ≥ 3, no máximo 3 clones por ciclo. `Proto_MadeiraReal` foi DESATIVADO (não tinha efeito nas árvores unidas e consumia orçamento Editable).
- **Resultado visual:** raízes contínuas e lisas (captura 91), sem os triângulos escuros; a textura de casca aparece listrada/verde, mais contrastada que o tronco. Play: primitivas ≈56 mil (antes 61,9–64,4 mil com 46 árvores), FPS marcou 14 na vista aérea (oscilação do Studio, não atribuível).
- **Pendências:** conferir cor/escala das raízes novas em Freixos (colR maior) e Troncos Secos; o arquivo aberto é AutoRecovery — salvar como lugar principal.
**M2 FLORESTA ANCESTRAL COMPLETA — Fase A, bloco A1: terreno de S2+S1 (2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Escopo:** autorizado pelo usuário (também que o tamanho final pode crescer para preservar as referências e dificultar achar tudo). Rodado no arquivo ORIGINAL `rpg_roblox` (conexão MCP caiu 1× durante o Play e voltou sozinha em ~30 s; Studio não precisou ser reaberto). **Atenção:** este arquivo NÃO tem o trabalho do AutoRecovery (otimização das árvores, 28 árvores, raízes contínuas `Proto_RaizesEnroladas`, módulo `OtimizadorArvores`); aqui as 46 árvores do setor continuam completas (≈69 mil partes) e precisam ser otimizadas de novo (menos árvores, como pedido).
- **Terreno gerado:** X 900–2450 × Z 356–1104 (≈1,16 milhão de studs²), módulo `ServerStorage/Proto_Restore/TerrenoA1` (+ cópia de execução `TerrenoA1_run`), em 32 ladrilhos. Emenda com o S0 em Z 356 por mistura de 140 studs com a altura real da borda (lida dos voxels); degrau máximo medido 0,9 stud. A leste de X 1856 não há vizinho (mistura só com o relevo novo). Relevo: colinas e cristas, mata mais alta e acidentada ao norte, planalto da vila em (2200, 480) (raio ≈70, altura ≈31). Alturas 9–64. Backup: `Proto_Restore/TerrainA1Borda` (faixa de emenda Z 336–400). As colunas A1 estavam vazias antes (nada a restaurar além da emenda).
- **Água:** riacho de NE (2000,1100) a SW com leito de 6,5 studs de profundidade e lago final em (1115,620) raio 36; água só onde a escavação é completa (Z ≥ 526), ≈820 colunas de água; passa por 2 trilhas (travessia a vau; pontes ficam para a Fase B).
- **Trilhas (Mud/Ground):** Lenhadores norte (1480,352)→(1480,1100) 772 studs; Estrada Antiga leste (1850,182)→vila (2170,470)→(2450,610) 747; secundária vila→mata 694; 3 ocultas: (1100,340)→(1060,760) 462, (1500,820)→(1900,1060) 475, (1520,720)→(1080,980) 530. Inclinação máx. 23–87%, só 1 ponto >70% (trilha leste, 87% ≈ 41°, transitável). Caminhada com `character_navigation` concluída: norte até (1480,1100), leste até (2450,610) e travessia do riacho na trilha norte (distância final 0).
- **Paredes `Limites`:** movidas para envolver S0+A1 (X 896–2460, Z −560 a 1116); valores antigos em `PosAntesA1`/`TamAntesA1`.
- **Desempenho (Play):** primitivas 113,6 mil e 171,5 mil instâncias (todas das árvores completas já existentes; o terreno não adiciona partes), 58–60 FPS nas vistas do A1 (oscilação conhecida do Studio, não afirma celular).
- **Limites/pendências:** sem vegetação, estruturas, pontes ou cachoeiras (Fases B–D); a borda norte (Z 1104), oeste (X 900) e leste (X 2450) termina em parede reta (continua nos próximos blocos); o curso alto do riacho ficou como vala seca vista de longe; o arquivo aberto deve ser salvo (File > Save) para fixar o A1.
**Fase A — A1 v2: ajustes de geografia pedidos pelo usuário (2026-10-20) — AGUARDANDO AVALIAÇÃO:** o A1 (v1 aprovado como base) foi regenerado só na faixa X 900–2450 × Z 356–1104; S0, árvores e sistemas não foram tocados. Gerador v1 preservado em `Proto_Restore/TerrenoA1_v1`; v2 em `TerrenoA1` (execução via cópia `TerrenoA1_run`; altura da região de escrita agora −8 a 100).
- **Rio:** linha principal sinuosa (meandros de ±26 studs), largura variável (8 ±2), margens irregulares por ruído, 3 afluentes que desembocam na principal (nível de água continuado) e lago de contorno irregular; o leito acompanha o terreno para a água ficar contínua. ≈1.450 colunas de água (antes ≈820). Margens: lama só a <6 studs, solo a <14.
- **Relevo:** alturas 11–82 (antes 9–64); cristas mais fortes, vales escavados e degraus de penhasco (≈2% das amostras com declive >45°), mesas rochosas. Os penhascos são abertos por fendas estreitas nas trilhas (ex.: trilhas 5 e 6 passam por cortes de até ≈90% de inclinação, transitáveis). Mirante natural em (1190, 1010), altura 67, com vista panorâmica (captura 99).
- **Formações para cavernas de urso:** 3 maciços rochosos de 40–50 studs de raio (em (1300,1020), (2080,900), (1050,860)), com apron plano ao sul; reservas invisíveis `Reserva_CavernaUrso_1..3` etc. em `Floresta/Reservas` (atributos Tipo/Estado/Setor=A1). As cavernas em si serão escavadas na Fase C.
- **Terrenos utilizáveis planos:** Clareiras de combate A (1600,960 r48) e B (1250,880 r45), clareira média (1900,700 r40), clareira oculta (1030,720 r30), planalto da vila (2200,480).
- **Bordas:** a emenda com o S0 mede degrau máx. 1,0 stud. As bordas oeste, leste e norte agora descem suavemente até ≈13 studs nos últimos 100 studs (sem parede alta); ainda há uma borda reta baixa à vista nas pontas, que será continuada pelos próximos blocos (S3 a oeste, regiões a leste/norte).
- **Testes (Play):** caminhada concluída (distância final 0) nas trilhas 1 (cruza o riacho), 2 (até a vila), 5 e 6 (ocultas, passando pelos cortes) e antes nas demais; colisões: personagem solto de 30 studs acima apoiou-se em 5 pontos (maciço, apron, clareiras, planalto), sem atravessar; FPS 56–60, sem terreno novo em partes (primitivas 100–114 mil são as árvores antigas, 46 completas).
- **Limites/observações:** o rio passa por uma garganta rochosa cheia de saliências na região da trilha 1 (visual desorganizado, captura 101); a mesa rochosa oval próxima de (1330,600) parece artificial de cima; o curso alto do rio fica entre colinas altas e pode parecer entrecortado; água de Terrain a 4 studs de resolução; nada foi testado em celular; salvar o arquivo para fixar o v2.
**Fase A — bloco A2: faixa leste (2026-10-20; A1 v2 aprovado e salvo pelo usuário) — AGUARDANDO AVALIAÇÃO:**
- **Escopo:** terreno X 1856–2450 × Z −552 a 356 (≈ 0,53 M studs², fecha a macrogeografia do primeiro terço X 900–2450 × Z −550 a 1100). Módulo `ServerStorage/Proto_Restore/TerrenoA2` (+ `TerrenoA2_run`), 15 ladrilhos. S0 e árvores não alterados. A área estava vazia (sem backup necessário). No A1, removida a descida de borda da face sul (x>1860) e regenerados só os 3 ladrilhos Z 356–546, X 1850–2450, para ser continuada pelo A2.
- **Emendas (Play/Edit):** A1/A2 (z≈356) degrau máx. 3,5 studs; S0/A2 (x≈1852) 4,2 studs (pior caso no canto sul). Mistura de 140 studs com pesos por distância às duas costuras.
- **Rio Leste:** nasce em ≈(2340,190), sinuoso, 8 studs de largura média, desce até o sul (1950,−540) onde ficará o Vale do Rio; 2 afluentes (leste (2440,−330)→(2090,−300) e oeste (2040,−20)→(2135,−215)); ≈1.090 colunas de água (só onde as emendas deixam escavar). Margens e leito como no A1.
- **Trilhas (Mud/Ground):** Estrada Antiga completada (1850,182)→(2030,358); Trilha do Rio principal (2200,440)→(1880,−552), 11 pontos; secundária que cruza o rio em (2240,−65) (ponte na Fase B); 3 ocultas (colina leste, retorno ao S0, maciço sudeste). Inclinação máx. 27–111% (trilha 1 tem 2 pontos >70% e a 6 tem 2; transitáveis).
- **Relevo/reservas:** alturas 11–75, cristas e penhascos como no A1; clareira de combate C (2100,20 r40), clareiras oculta leste (2380,−200) e média leste (2300,200), maciço rochoso 4 com apron para caverna de urso (2350,−350), mirante leste (2300,270, altura 60), ponto de ponte no rio; marcadores invisíveis `Reserva_*` com Setor=A2 em `Floresta/Reservas`. Limites das paredes (X 896–2460, Z −560 a 1116) já cobriam o A2. Bordas leste e sul descem para ≈13 studs nos últimos 100 studs.
- **Testes (Play):** caminhada concluída (distância final 0) em todas as trilhas do A2 (rio vila→sul, Estrada Antiga, cruzamento do rio, 3 ocultas); colisão: personagem solto de 30 studs apoiou-se em 5 pontos; FPS 14 em todos os pontos — inclusive no A1, que antes marcava 59 — é a oscilação do Studio (primitivas 113,6 mil, nada mudou nas partes); não atribuível ao A2, mas também não provado.
- **Limites/observações:** a costura S0/A2 mostra uma faixa de grama mais clara (captura 105); bordas sul e leste ainda deixam uma laje baixa visível de longe; água em 4 studs de resolução; sem vegetação, estruturas ou pontes (Fases B–D); salvar o arquivo.
**M2 FLORESTA ANCESTRAL — FASE B (estruturas do primeiro terço), blocos B0–B4 (2026-10-20) — AGUARDANDO AVALIAÇÃO:**
- **Escopo:** autorização integral B0–B4. Arquivo ORIGINAL `rpg_roblox`. Tudo em `Workspace/Proto_FlorestaAncestral/Estruturas_B` (Vila, Travessias, Locais, Sinalizacao, Integracao_Nucleo) + 4 árvores-âncora em `Floresta/Ancoras`. Kits modulares em `ServerStorage/Proto_Restore` (`KitB`, `KitB2a/b/c`, `OtimizadorArvores`). Só Parts (sem malhas novas, sem scripts por objeto). Nada de Fase C (habitats/criaturas/missões) foi feito.
- **B0:** `OtimizadorArvores` recriado; 4 árvores-âncora otimizadas (corpo unido + folhas unidas por cluster, colisor `ColisorTronco`; 308/547/308/547 partes, 0 falhas de união); raízes enroladas pelo script cliente `Proto_RaizesEnroladas`.
- **B1 Vila Florestal (centro 2200,480):** portal, praça com fogueira (fogo+luz), bancos e quadro de avisos, 5 bancas, oficina de madeira + depósito, 9 casas variadas (grande, estacas, cabana, varanda, alta, pequena, taverna, plataforma…), 3 casas-na-árvore em 4 plataformas com escadas e 2 passarelas + 1 ponte de corda entre copas, poço, carroça, bandeiras, pavimento, horta com cercas, varais, lanternas. ≈2.400 partes. Teste (Play): as 9 casas entradas por escada→varanda→porta→interior, escadas das casas-na-árvore e passarelas atravessadas, navegação pela praça; FPS 57–60.
- **B2:** `Ponte_Corda_Rio` (trilha 1, ≈(1524,700), vão de 50 studs, 374 partes) e `Arvore_Caida_Colossal` (Rio Leste ≈(2204,−98), 56 studs, 174 partes, raízes expostas, galhos quebrados, musgo, degraus laterais). Teste (Play): ponte cruzada de ponta a ponta (entrada e travessia = true, sem queda); árvore caída: subida pelos degraus, travessia do tronco e descida na outra margem (3 etapas = true). O túnel do tronco e os degraus usam colisores invisíveis simples.
- **B3 (`Locais`, ≈860 partes):** Ruína secundária (1030,720: muros em ruína, arco, 4 colunas, lajes, trepadeiras, altar interno, acesso em lajes); Altar antigo (1900,700: plataforma circular em degraus, círculo de 8 monólitos, arco de fundo, estela com runas neon turquesa e 2 braseiros; luz suave); Acampamento de exploradores (1820,820: 3 barracas, fogueira com fogo+luz, caixas, barris, mesa com mapa, estandarte, cerca de estacas); Mirante Norte (1190,1010) e Mirante Leste (2300,270): plataformas elevadas sobre pilotis, telhado de duas águas com musgo, guarda-corpo, banco, lanterna, escada e trilha de lajes. Terreno sob cada local pintado com `Ground` (círculos) para a grama alta não engolir as estruturas. Teste: os 5 locais alcançáveis por `PathfindingService` a partir da vila (status Success); ambos os mirantes subidos até o deck por caminhada com waypoints (Norte a partir de (1300,950), Leste a partir de (2240,350)). Falha corrigida: a 1ª versão da trilha de lajes dos mirantes começava em trecho de penhasco (≈65°); direção de acesso refeita e lajes íngremes removidas.
- **B4:** 8 placas com texto (SurfaceGui, Fantasy) com marco de pedras em cruzamentos e destinos (Núcleo/Floresta Profunda, Vila Oeste, Vila Norte/Mirante Leste, Ponte de Corda, Tronco Colossal, Ruínas do Oeste, Acampamento, Altar Antigo) — texto verificado só na placa da ponte (captura 121); `Integracao_Nucleo` (105 partes): caminho de lajes (1450,52)→(1414,−32) até o Posto/Santuário do S0, 2 braseiros com fogo+luz na entrada, 4 lanternas, 2 estandartes, placa do Núcleo. S0 original não foi modificado. Teste: caminhada pelo caminho (Success, distância final 0).
- **Medições (Play, final):** ≈119 mil partes/129 mil instâncias no cliente (StreamingEnabled), FPS 57 (Studio oscila 14–60, não atribuído a scripts); partes da Fase B: Vila 2.394 + Travessias 576 + Locais 862 + Sinalizacao 77 + Integracao 105 ≈ 4.0 mil. Console: nenhum erro do projeto (apenas avisos do próprio Studio/UIBlox).
- **Capturas:** `SCREENSHOTS/108` a `121` (vila, praça, casa-na-árvore, banca, oficina, ponte de corda, árvore caída, ruína, altar, acampamento, mirantes, núcleo integrado, placa).
- **Comparação com as referências (honesta):** reproduzido: casas e cabanas de madeira em estacas, plataformas e pontes entre copas, lanternas, praça/fogueira, musgo/raízes, ruínas cobertas por vegetação, ponte de corda sobre desfiladeiro. Parcial: as construções são de Parts (sem malhas/texturas esculpidas), então a vila ainda é mais geométrica e simples que a imagem de referência `Misty Forest Tree Village`; poucas cordas/luzes pendentes entre casas; ruína e altar pequenos e limpos em relação à referência. Faltando: neblina volumétrica local, vegetação densa ao redor das estruturas novas (Fase D).
- **Limites/pendências:** as 46 árvores completas (≈69 mil partes) do arquivo continuam não otimizadas (Fase D); desempenho em celular NÃO testado; interiores das casas são só reservados (marcador `InteriorReservado`, sem mobília); a vila e as ruínas B3 estão sobre grama alta, mitigada com `Ground`; a garganta do rio perto da trilha 1 continua visualmente irregular; texto das placas só conferido em 1; salvar o arquivo (File > Save) para fixar a Fase B. Fase C NÃO iniciada.
**Fase C/D parcial — habitats e mata (2026-10-20, após queda do PC; AutoRecovery preservou tudo) — EM ANDAMENTO:**
- **Feito e verificado no Studio:** 4 cavernas de urso escavadas no terreno (`Workspace/Proto_FlorestaAncestral/Habitats/Caverna_Urso_1..4`, piso em lajes, câmara com ninho de palha/ossos/luz fraca; entrada a pé testada nas 4, personagem entra até ≈5 studs do alvo); 10 tocas de lobo, 6 ninhos elevados sobre troncos, 12 tocas pequenas e a Clareira do Guardião (1600,960: círculo de 9 monólitos com runas, altar baixo, 2 arcos) — construídos, só a clareira e uma caverna capturadas visualmente; tocas/ninhos sem teste de captura próprio.
- **Mata:** 70 árvores APROVADAS (clones das 4 árvores-âncora, com ramitos, escala 0,72–1,15) em `Floresta/Mata`, posicionadas perto dos pontos de interesse; registradas nos scripts cliente existentes (folhas/casca/raízes). Árvores de esfera (protótipo) foram descartadas por não seguirem o padrão aprovado. Com 208 árvores o FPS caiu para ≈14 (209 mil partes); com 70, FPS ≈39 após ≈1 min de aquecimento do cliente, 153 mil partes. Portanto a floresta é ESPARSA fora dos pontos de interesse: densidade total exige LOD/impostor de árvore distante (não implementado).
- **Pendente (não feito):** rios/áreas úmidas extras, ruínas e altares adicionais, rotas para os novos habitats, mirantes extras, vento específico, otimização (LOD de distância), expansão para 5.000×5.000, capturas finais e testes de colisão dos habitats menores. Salvar o arquivo.
**Continuação (2026-10-21) — LOD, lagoas, ruínas extras, trilhas aos habitats — EM ANDAMENTO:**
- **Cobertura_LOD:** 456 árvores simples (tronco + copas em blocos, ≈19 partes, ≈8,9 mil partes) em `Workspace/Proto_FlorestaAncestral/Cobertura_LOD`, só longe das 70 árvores aprovadas (≥26 studs), dos pontos de interesse e habitats. Estilo é mais estilizado que as árvores aprovadas (visto em captura aérea); serve de preenchimento distante. Medição de FPS: 15 com e sem a LOD (isolado), então a LOD não é a causa; o FPS do Studio oscila (14–60) e a causa não foi isolada.
- **Lagoas:** 5 lagoas escavadas com água (`Terrain`) e juncos/vitórias-régias/pedras em `Locais_Extra/Lagoa_1..5` (água confirmada por leitura de voxels; não vistas em captura).
- **Ruínas extras:** `Locais_Extra/Ruina_Extra_1..6` (muros, arco, colunas, trepadeiras, raízes).
- **Trilhas:** caminhos de solo pintados no terreno de cada habitat/ruína até a trilha mais próxima (A1/A2). Teste de `PathfindingService` a partir da vila: 31 de 33 destinos alcançáveis; falharam Toca_Lobo_1 e 2 (regiões do S0, muito distantes). A trilha pintada para essas duas (≈800 studs) ficou sem uso real.
- **Ainda pendente:** vento próprio nas LOD, escala 5.000×5.000, capturas finais, salvar.
**Verificação e vento nas árvores LOD (2026-10-21):**
- **Capturas em Play:** lagoa 2 (água azul com juncos e pedras, ok, menor que o planejado), ruína extra 4 (arco e colunas ao lado de uma árvore aprovada, boa integração), toca de lobo 3 (abrigo de blocos com abertura escura; bloco e sem vegetação própria), clareira do guardião e cavernas (sessão anterior). Ninhos e demais tocas NÃO recapturados.
- **Correções:** removidas 6 árvores LOD sobre lagoas/ruínas; solo sob ruínas, tocas de lobo e ninhos pintado (Ground/Mud, 481 voxels) para a grama alta não engolir as peças.
- **Vento LOD:** script cliente `Proto_VentoLOD` (cópias das copas deslocadas pela direção de `workspace.GlobalWind`, só árvores a <140 studs da câmera). As 450 árvores LOD receberam a tag `ArvoreLOD`; o script lê as tags a cada ≈2 s (o evento de tag não disparou nesta sessão). Teste: 442 registradas, 7 ativas perto do jogador, copa desloca ≈0,14 stud a cada 0,6 s (sutil). FPS medido no cliente: 23 nesse teste (Studio oscila). Árvores aprovadas continuam com o vento original.
**Blender conectado — Árvore Ancestral 3D V2 (2026-10-21) — AGUARDANDO IMPORTAÇÃO/AVALIAÇÃO:**
- **Conexão:** MCP do Blender (blender-mcp, uvx com Python 3.12) funcionando; Blender 5.2.2 LTS, add-on 1.8, bibliotecas externas e geradores de IA desligados. Nada do mapa do Roblox foi alterado nesta etapa.
- **Modelo:** protótipo V1 preservado na coleção `V1_Prototipo` (oculta). V2 na coleção `ArvoreAncestral_V2`: `Tronco_V2` (tronco com contrafortes, 7 raízes, ramificação em 3 níveis, UV; 8.776 tris), `Copa_V2` (757 cartões de folhas com transparência, dupla face, mais núcleo escuro; 9.244 tris) e `Colisor_V2` (116 tris, convexo, cobre o tronco até z≈32). Total visual 18.020 tris em 2 malhas (limite do Roblox: 21 mil por malha). Altura ≈ 77 unidades, copa ≈ 83 de largura (1 unidade de Blender = 1 stud pretendido; escala real a confirmar na importação).
- **Texturas (geradas por código):** `Casca_V2.png` 1024×2048 (placas de casca, fissuras, musgo na base e no lado norte) e `Folhas_V2.png` 1024×1024 (3 raminhos com alfa + 1 célula opaca).
- **Arquivos:** `BLENDER/ArvoreAncestral_V2.glb` e `.fbx`, mais os dois PNG. Capturas `SCREENSHOTS/122` e `123`.
- **Não feito (sem prova):** importação no Studio, comparação lado a lado e medição de FPS no Roblox, porque o MCP do Studio não importa arquivos de malha locais; a importação precisa ser feita no Studio (Asset Manager/3D Importer). Após importar, definir `SurfaceAppearance.AlphaMode = Transparency` na copa e CollisionFidelity do colisor.
- **Limites visuais:** folhas são raminhos repetidos de 3 padrões (repetição visível de perto); a casca é textura, não relevo; a copa ainda é uma massa arredondada comparada às árvores aprovadas, que têm silhueta mais irregular.
**Árvore Ancestral 3D V3 (Blender, 2026-10-21) — AGUARDANDO IMPORTAÇÃO/AVALIAÇÃO:**
- **Mapa do Roblox não foi alterado.** V1 e V2 preservadas (coleções ocultas `V1_Prototipo`, `ArvoreAncestral_V2`); V3 em `ArvoreAncestral_V3`.
- **Mudanças:** copa refeita com 610 cartões em forma de cúpula (2×2 quads, dupla face) com textura de cachos de folhas (3 cachos + massa escura), silhueta com lobos irregulares e cachos periféricos; sem os "espinhos" da V2. Tronco com mais rugosidade geométrica, colar de transição nos galhos, 8 raízes entrando no solo, mapa de normais da casca (`Casca_N_V3.png`) além da cor.
- **Medições:** `Tronco_V3` 11.856 tris / 6.488 verts; `Copa_V3` 9.920 tris / 11.076 verts; `Colisor_V3` 116 tris; total visual 21.776 tris em 2 malhas, 2 materiais (`Casca_V3`, `Folhas_V3`). Altura ≈79, copa ≈73×79 unidades.
- **Material Preview:** capturas `SCREENSHOTS/124` a `126` (distância de câmera de 3ª pessoa, vistas frente/lateral/3-4, detalhe). A cor cinza da V2 era do modo Solid.
- **Exportação:** `BLENDER/ArvoreAncestral_V3.glb` e `.fbx` + PNGs. Materiais: Principled com textura de cor, alfa nas folhas e normal map na casca (convertem para `SurfaceAppearance`: ColorMap, NormalMap, AlphaMode=Transparency na copa).
- **Não feito (sem prova):** importação no Studio, conferência dos materiais lá e medição de FPS — o MCP do Studio não importa arquivos de malha; o usuário precisa importar. Também não há versão de LOD baixa (custo de 21,8 mil tris por árvore é alto para uso em massa). Folhas dos cachos se repetem (3 padrões); tamanho da folha ≈2–4 studs.
**Árvore Ancestral 3D V4 com LODs (Blender, 2026-10-21) — AGUARDANDO IMPORTAÇÃO/AVALIAÇÃO:**
- Mapa do Roblox não alterado; V1–V3 preservadas (coleções ocultas). V4 em `ArvoreAncestral_V4`.
- **Mudanças:** diagnóstico da V3 (domo único, folhas uniformes, sem vãos) corrigido: 6 galhos mestres em andares, galhos visíveis, copas em tufos nas pontas (519 cartões no LOD0), atlas `Folhas_V4.png` 2048² com 16 cachos irregulares (frondes, sprays, rosetas com falhas) em 4 paletas de verde, vãos entre os tufos.
- **Medições:** LOD0 10.312 tris (tronco 6.160 + copa 4.152), LOD1 2.456, LOD2 956; colisor 116 tris; altura ≈88; 2 materiais (`Casca_V3`, `Folhas_V4`). GLB 4,4 MB (LOD0); o peso é dominado pelas texturas embutidas (≈4 MB em todos os LODs).
- **Arquivos:** `BLENDER/ArvoreAncestral_V4_LOD0/1/2.glb|.fbx`, `Folhas_V4.png`. Capturas `SCREENSHOTS/129` a `131`.
- **Limites:** LOD1 e LOD2 têm copa mais rala que o LOD0 (silhueta ainda legível; a calibrar no Studio); folhas lidas ainda como lobos arredondados; casca é a mesma textura da V3; vento/oscilação não implementado para esta malha. Importação, SurfaceAppearance (AlphaMode Transparency) e medição de FPS no Roblox NÃO feitos (MCP do Studio não importa malha).
**Árvores V4 × V5 — validação no Roblox Studio (2026-10-21) — AGUARDANDO DECISÃO:**
- **V5 (Blender):** `ArvoreAncestral_V5` (preservando V4): 1.468 cartões de 1 quad com grupos pequenos de 4–6 folhas (atlas `Folhas_V5.png`), 129 galhinhos, normais suavizadas por tufo; 12.806 tris no Blender (tronco 6.160 + copa 6.646).
- **Como foi testado:** o MCP do Studio não importa arquivos de malha, então os geradores V4 e V5 foram **portados para Luau** (`ServerStorage/Proto_Restore/GeradorArvoresTeste`) e construídos com EditableMesh/EditableImage em Play (cliente), em plataforma isolada em X≈6000,Z≈6000,Y≈300, longe do mapa. A V4 portada reproduz exatamente 10.312 tris do Blender (6.160+4.152); a V5 portada usa MeshPart.DoubleSided (9.870 tris: 6.160+2.936+774) e **não é a malha exportada**: sorteios e ruído de casca diferem, e a casca é textura procedural simplificada sem normal map. Não foram testados arquivos `.glb/.fbx` importados, nem `SurfaceAppearance` com ID de textura carregada.
- **Transparência (testada de fato):** `Enum.AlphaMode` tem `Overlay`, `Transparency`, `TintMask`, `Opaque`. Só **`Transparency`** recorta as folhas pelo alfa; `Overlay`, `Opaque` e `TintMask` mostram cartões opacos (as "placas"). Usar `AlphaMode=Transparency` nas copas.
- **Visual no Roblox (capturas 137–150):** V4 = copa cheia e escura; de perto aparecem tiras finas (cartões de perfil) e placas escuras. V5 = sem placas nem tiras, folhas individuais legíveis e galhos bem visíveis, mas copa **rala** e com tom **azulado** (normais para cima recebem a luz azul do céu).
- **Custo medido (Studio, ruidoso):** V4 10.312 tris, 5 instâncias/árvore, 4 MeshParts? (2 + colisor); V5 9.870 tris, 7 instâncias (galhinhos viram um 3º MeshPart). 25 cópias: 1ª rodada FPS base 14,9 → V4 10,5 → V5 8,9 (memória +64 vs +124 MB); 2ª rodada base 9,0 → V5 9,1 → V4 9,0. O FPS do Studio oscila e não discrimina as duas; a memória sugere V5 mais cara, não confirmada.
- **Limite de orçamento:** em Play, EditableMesh/Image esgotam com os scripts cliente existentes (FolhasReais, CascaReal, Samambaias, RaizesGalhos, RaizesEnroladas); foram desligados só durante o teste e **religados** (estado conferido); nada foi deixado no mapa.
- **Recomendação:** nenhuma das duas é aprovada como árvore comum. V5 resolve placas/tiras; V4 tem melhor densidade. Próximo passo objetivo sem nova versão cega: ajustar a V5 (mais tufos e normais menos voltadas ao céu) ou importar o `.glb` real para confirmar.
**V5 ajustada — reteste no Roblox (2026-10-21) — SEM CONCLUSÃO FECHADA:**
- **Ajustes no gerador (`ServerStorage/Proto_Restore/GeradorArvoresTeste`):** mais tufos (extras ao longo dos galhos) e 44–52 cartões por tufo, galhinhos mais grossos (raio 0,42), normal de tufo parametrizada (`V5NDIR`, padrão −0,6). V5 agora 12.138 tris (tronco 6.160 + folhas 4.880 + galhinhos 1.098), 15.046 vértices, 7 instâncias; V4 10.312 tris, 5 instâncias. `AlphaMode=Transparency` confirmado nas duas.
- **Causa do tom azulado (medida):** os dois atlas têm a mesma cor média (≈28,62,14), então a textura não é fria; o azul vem da iluminação ambiente/céu pela normal da malha. Normal para cima ou rugosidade 0 deixam a copa azul-clara (captura 153); `EnvironmentSpecularScale=0` remove o azul (152); normal inclinada para baixo (−0,6) deixa a V5 verde (154), porém −0,25 ainda azulava. Mapa de rugosidade branco/preto e dupla face com verso próprio (17.018 tris) NÃO mudaram o resultado.
- **Estado final:** na configuração −0,6, a V5 ainda mostra tons azul-esverdeados nas copas voltadas ao céu (155–156); a V4 é mais verde e mais cheia (157). A V5 segue sem placas/tiras, com folhas e galhos legíveis. Eu inverti esquerda/direita em parte das leituras desta rodada (câmera olhando +Z: direita da tela = −X) e corrigi pelos nomes dos modelos.
- **Não feito:** medição de FPS/memória desta rodada (FPS do Studio oscila e não discriminou antes), importação do `.glb` real, vento nas malhas. Nada foi aprovado para a biblioteca.
- **Limpeza:** os 5 scripts cliente desligados durante o teste foram religados e conferidos; sem sobras no Workspace; `ReplicatedStorage` limpo.
**V5 com material quente × V4 — Roblox (2026-10-21):** V4 mantida como padrão provisório. V5 com atlas aquecido (multiplicadores R×1,55, G×1,2, B×0,5 na paleta; `GeradorArvoresTeste` `M.WARM`) fica verde-amarelada e próxima da V4, sem o azul (capturas 158, 159); sem placas/tiras. 12.138 tris vs 10.312. **FPS/memória: INCONCLUSIVO.** Com 25 cópias o FPS-base do Studio derivou de 15,5 para 9,4 durante o teste; V4 13,1/9,1 e V5 9,2/8,6 nas duas rodadas (ordem invertida), memória total +20/+114 MB (V4) e +73/+121 MB (V5), memória de MeshParts por tag não mudou. Tentativa com 100 cópias estourou o tempo e derrubou a conexão por ≈2 min. Não há diferença de custo comprovável; a V5 tem ≈18% mais triângulos e 2 instâncias a mais. Scripts religados e conferidos, sem sobras. Medir de verdade exige cliente publicado/dispositivo.
**V5 quente — candidata da biblioteca com LODs (Blender, 2026-10-21):** coleção `ArvoreAncestral_V5W`, ao lado da V4 (padrão provisório). Atlas `Folhas_V5W.png` (R×1,55 G×1,2 B×0,5), normais de tufo com −0,6 em Z, cartões de 1 quad com material sem culling. LOD0 12.138 tris (copa 4.880 + tronco 6.160 + galhinhos 1.098; 2.440 cartões, reproduz o teste do Roblox), LOD1 3.642 (870 cartões maiores, 1 galhinho/tufo), LOD2 1.386 (331 cartões, sem galhinhos); troncos dos LODs reaproveitam os da V4. Arquivos `BLENDER/ArvoreAncestral_V5W_LOD0/1/2.glb|.fbx` (3,6–4,0 MB, texturas embutidas); captura 160. "Candidata" = decisão de biblioteca; não aprovada visualmente em escala, LODs 1–2 não testados no Roblox, FPS/memória sem prova, `.glb` real não importado.
**Árvore Ancestral principal (hero asset, Blender, 2026-10-21) — AGUARDANDO AVALIAÇÃO:** coleção `ArvoreAncestral_Hero` (Blender), nada no Roblox. Altura 206 unidades (≈2,6× as árvores comuns de 79–88; abaixo da meta de 3–5×), tronco ≈75 de diâmetro na base com contrafortes e uma cavidade rasa, 12 raízes (4 em arco), 70 galhos em 3 níveis, copa em 3 setores com 5.652 cartões de folhas (atlas `Folhas_V5W`), cipós, 7 pedras abraçadas pelas raízes. Partes: Tronco, Raizes, Galhos, Galhinhos, Copa_A/B/C, Cipos, Pedras + Colisor_Tronco (188 tris) e Colisor_Raizes (720). Materiais: 4 (Casca_V3, Folhas_V5W, Cipo_Hero, Pedra_Hero). LOD0 37.286 tris (maior malha 8.448, todas <21 mil), LOD1 7.740, LOD2 1.402. Exportado em `BLENDER/ArvoreAncestral_Principal_LOD0/1/2.glb|.fbx` (3,6–5,0 MB). Capturas 161–163. Limites: textura da casca esticada em UV 0–1 sobre o tronco inteiro; cavidade e "locais sagrados" quase invisíveis; raízes parecem pétalas largas; topo do tronco ainda pontudo; sem teste no Roblox (FPS, transparência, importação).
**Árvore Ancestral principal v2 (Blender, 2026-10-21):** altura 299 (escala ×1,45 aplicada à geometria), casca nova `Casca_Hero.png`/`Casca_Hero_N.png` (16 placas em volta, densidade de textura mais uniforme; ainda UV 0–1 esticado), cavidade funda com interior escuro `Oco`, 12 raízes mais altas/redondas (4 em arco), topo coberto por tufos de coroa, 5 materiais (Casca_Hero, Folhas_V5W, Cipo_Hero, Pedra_Hero, Oco_Hero). LOD0 38.198 tris (10 malhas, maior 8.448), LOD1 7.976, LOD2 1.422; colisores 236 + 720 tris. Reexportada em `BLENDER/ArvoreAncestral_Principal_LOD0/1/2.glb|.fbx` (2,7–4,1 MB). Capturas 164, 165. Sem teste no Roblox.
**Árvore Ancestral principal v3 refinada (Blender, 2026-10-21):** altura 409 (≈5× as árvores comuns de 79–88), largura da copa ≈700. Mudanças: 26 raízes assimétricas (13 primárias de comprimento 38–140 e espessura variada + secundárias), base mais grossa com contrafortes e ondulação/torção sutil, 3 galhos heroicos longos (185/135/160 antes da escala) + 7 menores, copa em 92 tufos achatados de tamanho/densidade variados com vãos, 16 cipós de comprimentos variados nos galhos principais, casca `Casca_Hero` com mais contraste e musgo em manchas. LOD0 45.260 tris (10 malhas, maior 12.224), LOD1 8.704, LOD2 1.312; colisores 236+780 tris; 5 materiais. Exportada em `BLENDER/ArvoreAncestral_Principal_LOD0/1/2.glb|.fbx` (5,1–6,6 MB). Capturas 167, 168. Limites: copa pequena frente ao tronco e aos galhos (folhagem rala), galhos heroicos com poucas folhas nas pontas, casca em UV 0–1 esticado, sem teste no Roblox.
**Árvore Ancestral v3 com copa cheia (Blender, 2026-10-21):** ~30 tufos extras ao longo dos 3 galhos heroicos e dos galhos secundários mais grossos, mais cartões por tufo (46–96), vãos preservados entre tufos. LOD0 56.942 tris (maior malha 12.224), LOD1 11.836, LOD2 1.756; altura 408. Reexportada em `BLENDER/ArvoreAncestral_Principal_LOD0/1/2.glb|.fbx` com colisores. Captura 169. Limites: copa ainda com tom escuro único e cartões repetidos; sem teste no Roblox; custo alto para uso fora de hero asset.
**Árvore Ancestral: cor por andar e casca refinada (Blender, 2026-10-21):** UVs dos cartões remapeados por altura/borda para 4 paletas (sombra profunda embaixo, verde médio no meio, verde-limão claro no topo/bordas, algum azul frio), atlas `Folhas_Hero.png`/material `Folhas_Hero`; casca nova (base avermelhada → topo acinzentado, liquens claros no alto, musgo em manchas, normal mais forte). Mesmas contagens: LOD0 56.942 tris, LOD1 11.836, LOD2 1.756; 5 materiais; reexportada em `BLENDER/ArvoreAncestral_Principal_LOD0/1/2.glb|.fbx`. Capturas 170–171. Limites: musgo da base ficou forte; sem teste no Roblox (a iluminação do Roblox mudou o tom azulado das folhas nas árvores V5).
**Importação no Roblox da Ancestral e da V5W (2026-10-21):** o usuário importou os GLB. Árvore Ancestral LOD0 renderiza no Roblox (copa com transparência após criar `SurfaceAppearance`, cores corretas; capturas 172–173); corrigidos colisores (transparentes, Hull), Cipos/Pedras/Oco recoloridos, peças ancoradas, modelos renomeados `TESTE_ArvoreAncestral_Principal` e `TESTE_V5W` e movidos para a baseplate (700,0,300) e (−115,0,300). V5W: tronco e galhinhos aparecem, mas a copa não foi confirmada (captura 174 mostra árvore sem folhas legíveis; pode ser carregamento do asset da textura). Catálogo da biblioteca 3D em `DOCS/BIBLIOTECA-3D-FLORESTA.md`. Sem medição de FPS (Studio oscila). Mapa principal não alterado.
**Biblioteca 3D da Floresta Ancestral — lotes A4, B, C, D, E (Blender, 2026-10-21):** 70 modelos em 5 famílias em `BLENDER/Biblioteca/` (um `.blend` + `.glb` por modelo, colisores simples, materiais/texturas procedurais). Catálogo detalhado, medições e pendências em `DOCS/BIBLIOTECA-3D-FLORESTA.md`; capturas 175–180. **Nenhum modelo novo foi importado nem validado no Roblox** (o MCP do Studio não importa malha): estado "modelado e exportado". Mapa e estruturas existentes não foram alterados. Pendente: importação/validação por família, LODs, vila montada, consolidação de texturas.
**Refinamento estilo referência (Blender, 2026-10-21):** nova família `A5_Vegetacao_Refinada` (9 modelos, folhas largas), ruínas (família C) re-exportadas com pedra `PedraMuro_V2`, hera e folhas largas, Árvore Ancestral com cipó espiralado (`Cipo_Espiral_LOD0` 2.240 tris, `LOD1` 600; LOD2 sem cipó) e `ArvoreAncestral_Principal_LOD0/1/2` reexportados; B2: escadas das Casa_Lona A/B aproximadas da varanda (−2 studs em Y) e família reexportada (12 modelos). Capturas 184–188. Limites: samambaias ainda como lâminas, copa da Ancestral sem folhas mais largas/madeira mais escura nova, cipó só no tronco, colisores das casas não ajustados, **nada reimportado/validado no Roblox**. Detalhes em `DOCS/BIBLIOTECA-3D-FLORESTA.md`.
**Segunda passada de refinamento (Blender, 2026-10-21):** copa da Árvore Ancestral com atlas de folhas largas lobadas e cartões ampliados (×1,35/1,25/1,15), casca escurecida (×0,68), samambaias A5 com fronde pinada nova; Árvore Ancestral LOD0/1/2 e família A5 reexportadas. Depois, vãos de luz: cartões reduzidos e ≈30% removidos em aglomerados (LOD0 51.294 tris, LOD1 11.126, LOD2 1.642; reexportada; captura 192). Capturas 189–192. Limites: vãos sutis, folhas ainda são texturas procedurais, **sem importação/validação no Roblox**.
**Validação no Studio — A5 + Ancestral LOD1/LOD2 (2026-10-21):** importados pelo usuário; organizados em `Workspace/TESTE_Importados_A5_LOD` (SurfaceAppearance com Transparency criados, colisores ocultos, ancorados, recolorizados). Samambaias pinadas, copa de folhas largas, casca escura e cipó confirmados visualmente em LOD1; LOD2 veio com escala ×4 (corrigida via ScaleTo 0,25). **LOD0 novo importado em seguida**, corrigido (escala ×2,82 do importador → `ScaleTo 0,3542`, tronco 403 studs) e validado visualmente junto com LOD1/LOD2 (capturas 193–195, `TESTE_Ancestral_LOD0` em (300,−450)); a importação antiga do LOD0 permanece. Sem FPS/memória/Play/mobile. Objetos de teste adicionados ao Workspace (arquivo não salvo por mim); mapa e gameplay intactos.
**Validação no Studio — famílias B e B2 (2026-10-21):** importadas pelo usuário (23 modelos), organizadas em `Workspace/TESTE_Importados_B_B2` com SurfaceAppearance, colisores ocultos, recolor de Ferro/Luz/Brasa/Interior. Achado: lonas/tecidos/capins de uma face só ficam invisíveis → `DoubleSided=true`. Escada da Casa_Lona_A corrigida confirmada; escala OK. **Família C (ruínas) não importada.** Capturas 196–199; sem FPS/Play/colisão testada.
**Validação no Studio — família C (2026-10-21):** 16 modelos importados e organizados em `Workspace/TESTE_Importados_C` (fora do mapa). Achados: pedra/hera/runas e lonas só de uma face (ocas) → `DoubleSided=true`; modelos erguidos pelo pivô (hera abaixo da base) → reapoiados; visual muito verde. Capturas 200–202. Sem FPS/Play/colisão. Correção definitiva no Blender (faces duplas/invertidas) pendente.
**Correção no Blender das famílias B, B2 e C (2026-10-21):** normais de ≈1.800 caixas fechadas invertidas para fora e dupla face real nas ilhas abertas (lonas, folhas, tubos); ruínas com menos verde (pedra, folhas −40%/×0,7, material `Hera_Cipo_C`); hera acima do chão. 39 modelos reexportados (B 11, B2 12, C 16); Casa_Lona ≈13 mil tris. Pivô do Roblox continua recentralizado pelo importador. **Não reimportado/validado de novo no Roblox.** Capturas 203–204.
**Pedras flutuando — ruínas (Blender, 2026-10-21):** blocos/lajes/entablamento assentados por análise de ilhas, duplicatas removidas, família C reexportada (16 modelos). Restam folgas ≈0,3 em blocos inclinados do arco B. Capturas 205–206. Não reimportado no Roblox.
**Revalidação B/B2/C corrigidos no Studio (2026-10-21):** 39 modelos em `Workspace/TESTE_Corrigidos_B_B2_C` com `DoubleSided=false` — lonas, pedras e hera renderizam corretamente (capturas 207–209), o que valida a correção do Blender. Pendências: santuário sem captura visual (Studio desconectou 2×), bloco inclinado do arco B ≈0,3 flutuando, sem FPS/Play/colisão. Pastas `TESTE_*` antigas não removidas.
**Play: desempenho + colisão (2026-10-21):** vilas/ruínas/Ancestral perto 52–58 fps no Studio; vista larga ≈29 fps não causada pelos modelos novos (remover a Ancestral nova não mudou); memória total do Studio ≈7,4→7,9 GB; sem dados de mobile. Colisão ok em casas, muro e tronco (personagem parou nos colisores; hera atravessável). Defeito: `Colisor_Raizes` virava morro (Y≈66) → removido do LOD0 e exportado de novo (precisa reimportar). Detalhes e tabela em `DOCS/BIBLIOTECA-3D-FLORESTA.md`.
**Diagnóstico do FPS na vista larga (2026-10-21):** o gargalo é a floresta protótipo existente (≈159 mil partes, ≈29 mil Unions), não a biblioteca nova (≈350 MeshParts; removê-la não mudou o FPS). Teste só em Play: `LevelOfDetail=StreamingMesh` em 175 árvores grandes subiu a vista larga ≈41→≈51 fps (indicativo). Correções propostas (StreamingMesh, trocar árvores de Part por malha, limitar distância do sotobosque) aguardam autorização; nada foi alterado no arquivo. Medição do Studio é ruidosa; falta dispositivo real.
**StreamingMesh na floresta (2026-10-21) — testado e revertido:** aplicado em 175 modelos (autorizado), o FPS da vista larga caiu de ≈43–47 para ≈25–30 e a memória do Studio subiu ≈+2,4 GB; revertido (todos Automatic, atributos limpos) e o FPS voltou a ≈40–45. Não recomendado. Arquivo no estado anterior; segue como proposta trocar as árvores de Part/Union por malhas com LODs.
**Plano de malhas para a floresta (proposto 2026-10-21, NADA aplicado):** as ≈160 árvores do `Floresta` são clones escalados/rotacionados de poucos desenhos-base (Carvalho 1.102 partes, FreixoAntigo 1.892, FreixoVelho 1.771, TroncoSeco 1.181, Mata 547/308 + 4 âncoras); ≈20% das partes são `UnionOperation` (copas "Cacho/Folha" e raízes circulares), cuja geometria não é acessível por script. Plano: baixar o desenho aprovado fielmente (exportar cada árvore-base do Studio em OBJ → Blender → malhas ≤21 mil tris + LODs) em vez de usar as árvores V4/V5W (que mudariam o visual). Piloto com 1 espécie antes de generalizar; originais movidos (não apagados) para `ServerStorage/Proto_Restore`. Aguardando aprovação.
**Piloto de malhas — Carvalho (2026-10-21, em andamento):** o usuário exportou do Studio `EXPORTAR_Carvalho_Base` (cópia da Carvalho SO_013, criada em Workspace; originais intactos) em OBJ: 506.298 tris, 1.102 grupos (222 unions de folha = 365 mil tris; 5 trepadeiras = 61 mil) e 151 cores. No Blender: decimação por categoria (folhas ×0,10, trepadeiras ×0,18, madeira/galhos ×0,45–0,5), fusão em 5 malhas (Madeira 18,6k, Galhos 19,3k, Cipos 13,1k, Folhas A/B ≈18k) e paleta de cores 104×104 com UV por parte. LOD0 87.574 tris, LOD1 27.200, LOD2 8.233 (`BLENDER/Floresta/Carvalho_Base_LOD0/1/2.glb`, `Carvalho_Paleta.png`, `Carvalho_Base.blend`). Limites: perdem-se as texturas de material Wood/Grass do Roblox (cor chapada por peça), sem colisor, ainda não importado nem comparado no Studio. Nada foi trocado no mapa.
**Piloto Carvalho — resultado no Studio e V2 (2026-10-21):** importadas as 3 malhas com paleta (escala correta 45×53×45,5; LOD0 87,6k tris). Comparadas à original no Studio (`TESTE_Carvalho_Malha`): forma e silhueta equivalentes, mas **muito mais escuras** (SurfaceAppearance com paleta). Teste de LOD1 com `Material`+`Color` (Grass/Wood) e `CastShadow=false` ficou mais claro que a original → gerada a V2: 13 malhas por cluster de cor/material (8 Grass, 5 Wood; cores sRGB no nome), `BLENDER/Floresta/Carvalho_V2_LOD0/1/2.glb` (87.574 / 27.142 / 10.326 tris). Falta importar a V2, aplicar cor/material por nome, comparar e medir FPS. Nada trocado no mapa.
**Piloto Carvalho V2 — comparação e FPS (Studio, 2026-10-21):** a V2 (13 MeshParts por árvore, cor/material por nome, `CastShadow=false`) ficou visualmente muito próxima da original (capturas 210; a versão com paleta, 211, era escura). Teste em Play com campos de 40 árvores: **original = 44.080 partes → 39–41 fps (mesmo olhando para outro lado; sem o campo, a base volta a 57–60 fps)**; **V2 LOD0 = 520 malhas, ≈3,5 M tris → 58 fps**; V2 LOD1 ≈1,1 M tris → 57 fps. Conclusão: o custo é o número de partes, não os triângulos. Limites: Studio em PC, uma série por condição; sem colisor na V2; sem vento; Wood/Grass usam o material do Roblox com cor por cluster (8 verdes, 5 madeiras). Campos de teste removidos; mapa intacto. Próximo: exportar OBJ de FreixoAntigo, FreixoVelho e TroncoSeco (clones `EXPORTAR_*` já no Workspace em X=300/500/700, Z=−300) e repetir.
**Malhas das demais espécies — geradas no Blender (2026-10-21):** a partir dos OBJ exportados do Studio (os rótulos de `FreixoVelho_base.obj` e `TroncoSeco_base.obj` estavam trocados: pela contagem de grupos 1.181 = TroncoSeco e 1.771 = FreixoVelho; corrigido). Resultado em `BLENDER/Floresta/`: `FreixoAntigo_V2_LOD0/1/2.glb` (14 malhas; 121.598 / 36.473 / 13.671 tris; maior malha 17.458), `FreixoVelho_V2_LOD0/1/2.glb` (13; 117.456 / 35.232 / 12.826), `TroncoSeco_V2_LOD0/1/2.glb` (12; 73.509 / 22.048 / 9.621). Cada malha ≤ 19.752 tris (limite do Roblox ≈21,8 mil). Mesmo método do Carvalho V2 (cor/material por cluster no nome). Não importado/validado no Studio; sem colisor/vento; Mata (anchors) e substituição no mapa pendentes.
**Espécies V2 no Studio → V3 (2026-10-21):** importadas as 9 malhas V2 (`TESTE_Especies_V2`, escalas corretas). Achados: (1) os MeshParts vieram chamados `m.NNN` (nome da malha, não do objeto) — cor/material só foi recuperável por correspondência de dimensões no LOD0 (14/14, 13/13, 12/12 ok); nos LOD1/LOD2 a correspondência falhou (geometria decimada com dimensões diferentes), então ficaram coloridos de forma errada; (2) na comparação visual com a original (capturas 212), o LOD0 V2 ficou **mais ralo** nas copas e com tronco mais cinza. Correção: V3 com folhas decimadas menos (alvo 85 mil tris; FreixoAntigo 161.582, FreixoVelho 161.800, TroncoSeco 73.509 tris no LOD0; LOD1 ≈30%, LOD2 ≈10%) e nomes de malha corretos (`Espécie_Grass|Wood_HEX_Lx`): `BLENDER/Floresta/*_V3_LOD0/1/2.glb`. Aguardando importação e nova comparação; originais e mapa intactos.
**Espécies V3 validadas no Studio (2026-10-21):** as 9 malhas V3 (FreixoAntigo/FreixoVelho/TroncoSeco × LOD0/1/2) importadas, coloridas por nome (16/15/12 malhas por LOD, 100%), em `Workspace/TESTE_Especies_V3`, ao lado das originais `EXPORTAR_*` (V2 removida; 2 duplicatas de importação movidas para `TESTE_Duplicados_Importacao`). Visual: LOD0 muito próximo da original (densidade e cor); LOD1 um pouco mais ralo; LOD2 ralo (uso distante). FPS (Play, 20 árvores FreixoAntigo): **original 37.840 partes → 41,8 fps e 22,9–41 com ela no mapa; V3 LOD0 (320 malhas, ≈3,2 M tris) → 55,6 fps; V3 LOD1 → 56,7 fps; base sem campo 55,5**. Capturas 213. Nada trocado no mapa. A Mata tem só 2 desenhos (28× Ancora_Freixo de 547 partes, 42× Ancora_Carvalho de 308): clones `EXPORTAR_Mata_Freixo` (x=900) e `EXPORTAR_Mata_Carvalho` (x=1100) preparados para exportar OBJ.
**Inventário de fechamento da vegetação (2026-10-21, só leitura):** `Proto_FlorestaAncestral` ≈159 mil partes. Floresta: Carvalho 14 / FreixoAntigo 11 / FreixoVelho 14 / TroncoSeco 7 (clones escalados, V2/V3 prontas), Mata 70 (2 desenhos: 28× Freixo 547 partes, 42× Carvalho 308 — OBJ pendente), Arbusto 50×4 partes. Chunk_Ancestral/Arvores: 40 árvores de 3 espécies com tamanhos/contagens diferentes (381–1.503 partes; Carvalho-do-Bosque 17, Freixo Antigo 8, Freixo Antigo velho 11, Carvalho Jovem 4) + `Arvores` com 4 árvores grandes (699–2.283 partes). Sotobosque: Samambaias 207 (14 partes/7 unions), FolhasLargas 94 (3 unions), Serapilheira 273 (1 parte). Cobertura_LOD: 113 setores com 3 desenhos de LOD (13/20/21 partes). Vegetacao 138 e Rochas 134 (1–10 partes). Estruturas_B/Habitats/Locais_Extra: construções de Part (não vegetação). Nada alterado.
**Decisão do usuário (2026-10-21): a floresta deve ter SOMENTE árvores criadas no Blender** (não as de Part/Union do protótipo). Interpretação adotada: árvores V4/V5W, Árvore Ancestral (hero) e um novo conjunto gerado por script; as malhas de espécies convertidas das árvores de Part (Carvalho/Freixo/Tronco seco V2/V3, em `BLENDER/Floresta`) ficam arquivadas e NÃO entram na floresta. V5W confirmada no Roblox (tronco ok, copa com Transparency, com manchas azuladas). **Novo conjunto gerado (Blender, protótipo):** 8 árvores — Carvalho A/B/C (H≈58, copa larga em tufos), Freixo A/B/C (H≈100, copa alta), Tronco Seco A/B (sem folhas) — `BLENDER/Floresta/ArvoresBlender_LOD0/1/2.glb` (28.596 / 8.528 / 1.628 tris no conjunto; ≈3,6 mil tris por árvore no LOD0; materiais Casca_V3 + Folhas_Hero; nomes `Especie_X_Tronco|Copa_Ln`). Não importado nem validado no Studio; qualidade ainda moderada (raízes pequenas, galhos pouco visíveis). Troca no mapa pendente (posições/escala das originais, por setor).
**Floresta Blender — substituição aplicada (2026-10-21, AUTORIZADA pelo usuário: "só árvores do Blender"):** (1) 610 árvores de Part/Union (Floresta Carvalho/Freixo/Tronco seco/Mata, Chunk/Arvores, Arvores, Cobertura_LOD) **movidas (não apagadas)** para `ServerStorage/Proto_Restore/Originais_Arvores` e substituídas por 610 árvores do Blender em `Workspace/Floresta_Blender/Arvores` (mesmas posições/alturas; espécie Carvalho/Freixo/Seco, variantes A/B/C, Y pelo terreno; modelos-base em `ServerStorage/ArvoresBlender`). (2) Sotobosque/Vegetacao/Arbusto antigos movidos para o backup e substituídos por 1.392 plantas A5 (samambaias/arbustos; `Floresta_Blender/Sotobosque`; modelos em `ServerStorage/Vegetacao`), com clareiras nas estruturas. (3) 4 vilas/acampamento ocultos (Aldeia_Carvalho, Aldeia_Nevoa, Aldeia_Raizes, Acampamento_Perdido) com casas/bancas/lanternas/cercas B/B2 em sítios planos (`Floresta_Blender/Vilas_Ocultas`; árvores/plantas limpas em raio 56). (4) 3 bosques alternativos (Troncos_Secos 35 árvores, Freixos_Altos 97, Carvalhos_Antigos 8) + plantas em `Floresta_Blender/Bosques`. (5) 6 ruínas extras do protótipo (Locais_Extra) substituídas por composições C (altar/santuário, muros, arcos, colunas, monolito) em `Floresta_Blender/Ruinas`; lagoas mantidas. (6) Scripts cliente antigos Proto_CascaReal/FolhasReais/RaizesEnroladas/RaizesGalhos/Samambaias/MadeiraReal **desativados** (esperavam as pastas movidas; `Enabled=false`, não apagados). **Teste em Play:** 60 fps (teto) nos 4 pontos medidos, ≈14.350 partes no Workspace (antes ≈159 mil), memória do Studio ≈8,6 GB; sem erros novos além dos avisos de WaitForChild dos scripts já desativados. Limites: folhas ainda com tom azulado/escuro (atlas quente `ArvoresBlender2_*.glb` exportado, aguardando reimportação), sem colisor nas árvores nem vento novo, bosques com densidade abaixo do pretendido, habitats (lobos/ursos/ninhos) e vila principal (Estruturas_B) ainda de Part, famílias A4/D/E não importadas.
**Habitats estratégicos e limpeza (2026-10-21):** folhas V2 (atlas quente) aplicadas trocando os IDs de textura (1.433 SurfaceAppearance); famílias D, A4 e E importadas e organizadas em `ServerStorage/Biblioteca` (43 modelos; `DoubleSided=true` como remendo, pois D/E/A4 não passaram pela correção de faces do Blender). **Habitats refeitos** (originais de Part movidos para `Proto_Restore/Originais_Arvores/Habitats_Part`) em `Workspace/Floresta_Blender/Habitats`, seguindo o conceito da Floresta Ancestral ("rastros de fauna, caminhos furtivos, entradas ocultas"): 10 tocas de lobo, 6 ninhos elevados (com `Ovo_Ninho` placeholder), 4 cavernas de urso, 12 abrigos pequenos e a Clareira do Guardião (santuário + monolitos). Cada toca/ninho/caverna tem **arena de combate** (raio 27–30, terreno plano ≤9 de desnível, marcador `Arena` e `Spawn*` invisíveis), cobertura baixa (troncos, tocos, pedras), **anel de camuflagem** (arbustos, samambaias, rochas e raízes) com uma abertura estreita perpendicular à estrutura, e 8 **rastros** de fauna discretos saindo da entrada; a estrutura fica voltada à arena a 34–46 studs, afastada de vilas/travessias (maioria >120). Teste: PathfindingService do exterior da arena até o ovo/estrutura em 20/20 complexos; 60 fps em 4 pontos; ≈13,5 mil partes. Árvore Ancestral (hero, 486 de altura) posicionada no lugar da antiga `Carvalho_Ancestral_01` (1350,23,−52) com 183 árvores/plantas limpas em raio 105. Itens de teste/importação (20) movidos de Workspace para `Proto_Restore/Testes_Importacao`. Pendências: vento, colisor das árvores, trilhas/rios, vila principal (Estruturas_B) ainda de Part, nenhuma lógica de lobos/ovo (só marcadores), teste em celular.
**FECHAMENTO DA FLORESTA ANCESTRAL — execução autônoma (2026-10-21, autorizada pelo usuário; "árvores = famílias do Blender"):** nota: o texto de instrução colado chamava o jogo de "Dragon Ranch"; tratado como erro de rótulo (é este RPG; nada de Dragon Ranch foi usado, conforme CLAUDE.md regra 3). **Feito no Studio (tudo em `Workspace/Floresta_Blender`; backups do que saiu em `ServerStorage/Proto_Restore`):**
- **Inspeção/correção:** varredura sem planos gigantes nem partes enormes nas peças novas; causa provável dos "planos chapados": plantas A5/A4 grandes demais (folhas de 20–60 studs) → **3.793 plantas reduzidas ×0,5 (cipos ×0,6)**; **198 cipos suspensos removidos** (flutuavam); checagem de base×terreno: 0 itens fora da faixa.
- **Árvores:** 1.390 modelos de árvore do Blender (Carvalho/Freixo/Seco, variantes A/B/C; 610 originais nas posições antigas + **608 médias** de preenchimento de dossel por zonas de ruído + bosques densificados: Freixos Altos +85, Troncos Secos +58, Carvalhos Antigos +14). **Colisor cilíndrico de tronco em todas** (teste: personagem parou no tronco 3/3). Árvore Ancestral mantida como marco com anel de monolitos, arcos, muros, colunas, altar, santuário e 18 rochas + 85 plantas ao redor.
- **Vento:** `StarterPlayer/StarterPlayerScripts/Floresta_Vento` (LocalScript): copas oscilam ≈0,5° em torno da base, só até 420 studs; plantas balançam ≈1,6° só até 130 studs; sem erros em Play.
- **Trilhas:** A* sobre o terreno (declive ≤0,62) entre 19 pontos: 11 primárias (larguras 10, Ground), 10 secundárias (7), 24 furtivas descontínuas (3,4, Mud) até as arenas; ≈11 mil studs; vegetação removida na faixa; dados em `Proto_Restore/Dados_Montagem/_Trilhas`.
- **Vegetação de solo:** `Solo` (≈2.200 itens: samambaias, arbustos, folhas largas, capim, pedras, cogumelos, tocos, troncos, raízes em arco, densidade por ruído) + `Margens` (604 plantas + 98 pedras em volta das 339 células de água detectadas) + camuflagem de habitats/clareiras/aldeias.
- **Habitats:** 8 ninhos (Ovo_Ninho placeholder), 2 territórios de lobos (3 tocas cada), 10 tocas de lobo, 4 cavernas de urso, 12 abrigos, clareira do guardião; todos com arena (raio 27–34, planície ≤9), cobertura baixa, anel de camuflagem com abertura lateral, rastros e spawns invisíveis. **5 clareiras de combate** (raio 34, ligadas à trilha) e **2 mirantes naturais** (+ os 2 de Part existentes). 4 vilas ocultas refinadas (+20 objetos E, piso pisado, 38 plantas) e 6 ruínas (+ruína do bosque de freixos com anel de rochas).
- **Iluminação:** Ambient/OutdoorAmbient levemente quentes (0,30,0,30,0,26), Atmosphere Decay/Color menos azuis, SunRays 0,08/0,28 (valores anteriores nos atributos `Prev_*`).
**Teste:** Play: 60 fps (teto) em 5 vistas, ≈19,9 mil partes (era ≈159 mil), sem erros no console; PathfindingService: 8/8 rotas entre hubs; 28/29 arenas alcançáveis (Ninho_Elevado_8 só por 3 de 8 direções — acesso furtivo lateral); 7 de 7 testes de colisão/arenas essenciais ok. Prints 214–224.
**Limitado/pendente (refinamento):** vila principal, travessias e locais de `Estruturas_B` seguem de Part (preservados); Clareira_Combate concentradas no leste (terreno plano); sem rios novos (só 5 lagoas + água de terreno com margens); sem lógica de lobos/ovo/criaturas; sem teste em celular nem em cliente publicado (Studio mede 60 fps, teto); famílias D/E/A4 usam `DoubleSided` de remendo; **o arquivo não foi salvo por mim (o Studio não expõe Save por MCP) — salvar com Ctrl+S e fazer cópia de segurança do .rbxl**; nenhum item M2 de `TASKS.md` marcado `[x]`.
**Guardiões, ursos gigantes e famílias de lobos (2026-10-21, a pedido do usuário):** (1) **4 cavernas de urso** refeitas para ursos gigantes: covil ×1,7, arena de raid R=46 (planície ≤10,6), cobertura grande (troncos/rochas ×0,7–0,8), 2 `SpawnUrsoGigante`, `PontoCovil`, anel de camuflagem com abertura larga lateral, rastros ×2. (2) **Toca de lobo = família:** cada `Estrutura*` (16 tocas, incl. 2 territórios) ganhou `Familia_*` com `NinhoLobos`, 3 `Ovo_Lobo` (placeholder), `SpawnLoboAlfa`, `SpawnLoboAdulto`, 3 `SpawnFilhote` (48 ovos); 4 ninhos realocados por falha de rota. (3) **4 vilas protegidas por guardião** (`Vilas_Ocultas/*`, atributo `Guardiao`): Aldeia_Carvalho=Urso_Gigante, Aldeia_Nevoa=Lobo_Alfa (toca×2,4 + ninho com 4 ovos + adultos/filhotes), Aldeia_Raizes=Cervo_Ancestral (santuário×1,7 + 5 monolitos + altar), Acampamento_Perdido=Águia_Celeste (poleiro/ninho×2,4 sobre rochas, `Voa=true`); cada uma com `Arena_Raid` R=72, covil a 88 studs oposto à entrada (rumo à trilha), assentamento ampliado (mirante, oficina, tendas, banca, mesa), 8 `SpawnHabitante`, camuflagem com abertura para a trilha. **Testes (Play, pathfinding AgentRadius 3–4):** entrada→centro das 4 aldeias OK; centro→covil 3/4 (Acampamento_Perdido: NoPath, pois o spawn da águia fica elevado/voa); entrada furtiva→covil das 4 cavernas OK; ninhos de lobo alcançáveis 12/16 → realocados os 4 restantes (nova rota confirmada para 3; Toca_Lobo_5 reposicionada dentro da arena sem reteste). **Não existe lógica nem modelos de criaturas, só marcadores/atributos; nada de combate, IA ou persistência do ovo.** Limites: arenas de raid R=72 são maiores que as outras (27–46) mas sem teste com NPCs; não medido FPS depois desta etapa.
**Rios e vila principal (2026-10-21, autorizado: "construção primeiro"):** nota: a floresta **já tinha rios de terreno em trechos** (cursos de água descontínuos por todo o mapa); em vez de criar rios do zero, **recortei e completei 3 rios sobre o terreno** (Terrain:FillBlock Air/Sand/Water, seções de 7,5 studs, nível monótono decrescente, busca de vale lateral): **Rio B (NE)** 20 studs de largura até a borda norte, **Rio D** (SE→B) 14, **Rio A (oeste, sob a Ponte de Corda)** 18 até a borda oeste. Rio C (vale central) **não escavado** (exigiria cortar crista de até ≈22 studs). Planos em `Proto_Restore/Dados_Montagem/_PlanoRios`. **Terreno alterado: não há backup do terreno nem desfazer por script — salvar/ter cópia do .rbxl.** Limites: junção D→B pode ter degrau de ≈3–7 studs de nível; margens com paredes de terra/pedra do próprio terreno; sem animação/correnteza. Vegetação das margens: 289 itens removidos da faixa, `Margens` regenerada (736 plantas + 133 pedras em 630 células de água). **Trilhas:** 7 trilhas que corriam dentro d'água foram **recalculadas com A\* evitando água** (custo ×14), repintadas, e 7 **pontes** (Passarela_Modulo_12 em módulos de 11,4 studs) criadas nas travessias reais (`Floresta_Blender/Pontes`); 1 travessia de 81 studs (trilha 4, junto à ponte de corda) não construída. **Vila principal** (`Floresta_Blender/Vila_Principal`, centro (2198,483)): 9 casas de Part → casas da biblioteca (Casa_Grande×2, Estacas×2, Cabana×2, Lona×2) voltadas para a praça, oficina, 5 bancas (lona/mercado), praça com fogueira+mesa de mapa+4 lanternas+6 bancos+14 objetos E, 4 árvores do Blender junto às plataformas elevadas, 70 plantas; **originais em `Proto_Restore/Originais_Arvores/Vila_Principal_Part`**. Mantidos (Part): Portal_Vila, Detalhes (horta, poço, carroça, bandeiras, pavimento), plataformas e pontes de copa. **Achado:** cada casa antiga de Part tinha ≈10% de peças perdidas no ponto de origem (X≈0,Z≈0); sumiram com a troca. Clareira de 118 studs de raio (9 árvores removidas). **Teste (Play):** 12/12 rotas entre hubs via PathfindingService (inclui travessias de rio), caminhada sobre ponte ok, 60 fps (teto) em 4 vistas, ≈18,7 mil partes, sem erros novos. Prints 227–230. Pendente: arquivo não salvo por mim; Rio C; sem peixes/som/correnteza; modelos e IA de criaturas.
**OPERAÇÃO "CONCLUIR A FLORESTA ANCESTRAL" — execução autônoma (2026-10-22; o texto colado dizia "Dragon Ranch": tratado como rótulo errado, é este RPG):**
**Fase 0 — auditoria real:** o terreno existia só em X 900–2460 × Z −560…1116 (≈1.560 × 1.676 = 2,6 M studs², ≈10% da meta); a expansão para 5.000² NÃO tinha acontecido. Setores: S0, S1, S2 construídos; S3, S4, S5 e S6 (do plano de 2.800²) vazios. Backup: o .rbxl não foi salvo por mim (o Studio não expõe Save por MCP) — **salvar com Ctrl+S e guardar cópia**; nenhum backup de terreno foi feito por script.
**Fase 1 — terreno:** gerador `Proto_Restore/TerrenoExp` (heightfield FBM + identidade por setor: S3 mata ondulada, S4 colinas, S5 vale baixo, S6 penhascos em terraços; costura com o terreno antigo por mistura de 170 studs usando as alturas reais da borda; contorno irregular por ruído radial; **mar (nível 8) + praias** na borda; 7 rios que prolongam os rios existentes até o mar e afluentes; 9 lagoas). Escrito em 482 ladrilhos de 192 studs. **Resultado medido:** terra (h≥12) ≈ **14,4 M studs²**, extensão **≈ 4.344 × 4.344 studs** (X −552…3792, Z −2160…2184) dentro de um contorno natural; ≈ 5,6× a área antiga. **Não é 5.000×5.000 exato** (contorno redondo/irregular; área ≈ 58% de um quadrado de 5.000). Paredes invisíveis do contorno (180 segmentos em `Floresta_Blender/Limites_Floresta`); `Limites` antigos e Baseplate movidos (Baseplate para y=−5000, `PosAntes`). Renderização do terreno novo no Studio levou vários minutos para aparecer.
**Fase 3 — vegetação:** 4.409 árvores do Blender (LOD1; LOD2 acima de 1.900 do centro) por setor (S3 denso/Seco, S4 esparso, S5 Freixos, S6 raro, fora: mistas) com colisor de tronco; 69 **gigantes antigas** (Carvalho ×2,2–2,8, Freixo ×1,8–2,3, LOD0, colisor) em S3/S5/S4/S6/S2/entorno; ≈ 9,6 mil itens de solo (samambaias, arbustos, capim, rochas, cogumelos, tocos, troncos, raízes) por densidade de ruído; margens de rio (`Margens_Exp`: 687 plantas + 135 pedras).
**Fases 4–8 — pontos de interesse (módulo `FlorestaLib`, marcadores invisíveis nomeados):** 16 territórios de lobos (2–3 tocas + ninho com ovos placeholder + alfa/adulto/filhotes), 17 ninhos elevados, 7 cavernas de urso gigante (arena R=46), 10 **poços de serpente** em margens de água (PontoBeber/EmboscadaSerpente oculto/RotaAproximacao/RotaFuga), 15 ruínas (6 grandes em S4), 8 mirantes naturais, 11 clareiras de combate, 4 acampamentos, **3 entradas de dungeon (reservas físicas)** em S4/S5/S6, **Clareira do Guardião** (R=72, santuário, 7 monolitos, arcos, 9 árvores monumentais) em S6. **Trilhas:** A* com heap sobre a malha de 24 studs evitando água/declive: 13 primárias (Estrada Antiga W–E e Trilha dos Lenhadores N–S), 42 secundárias, 50 furtivas (≈ 37.700 studs), pintura no terreno e exclusão de vegetação; 10 pontes (módulos de passarela) nos cruzamentos de rio; 1 travessia de 92 studs não construída.
**Testes (Play, Studio/PC):** PathfindingService: arenas de ninhos 17/17, lobos 16/16, clareiras 11/11, serpentes 10/10, dungeons 3/3, guardião 1/1, ursos 6/7 (Caverna_Urso_2 da área antiga sem rota); trechos longos de trilha entre hubs OK (rotas de >4.000 studs falham por limite do próprio pathfinding). FPS 56–60 em 6 vistas (S3/S4/S5/S6/costa/panorama), ≈ 24,6 mil partes carregadas (StreamingEnabled), memória do Studio ≈ 8,7 GB; sem erros novos no console. **Não medido:** celular, cliente publicado, vários jogadores. FPS de Studio ≠ desempenho real.
**Classificação:** terreno + setores S3–S6 (macro): CONSTRUÍDA E TESTADA PARCIALMENTE (visual/pathfinding no Studio; caminhada do personagem só na ponte antiga). Vegetação, habitats, trilhas, pontes: CONSTRUÍDA, TESTE PARCIAL. Prints: poucos (câmeras no dossel), sem capturas ao nível do jogador de todos os setores. **PARCIAL/PENDENTE:** cachoeiras/corredeiras e poços fundos escavados (os rios novos são canais de 8–20 studs sem quedas), margens rochosas/íngremes variadas, cavernas com câmaras internas (as cavernas de urso são modelos de entrada, sem interior navegável), observatórios, passagens por raízes, vilas novas além das 2 existentes, polimento visual por setor (rochas repetitivas, junções de tronco), vento aplicado só via `Floresta_Vento` nas árvores/plantas marcadas, adensamento do S6, 3 clareiras e 2 ursos de S6 não encontraram local plano. Nenhum item de `TASKS.md` marcado `[x]`. Sistemas de jogo (combate, IA, criaturas, missões) não foram tocados.
**Verificação pós-incidente e entrada nas cavernas (2026-10-22):** após o aviso de moderação (item `bloxworld4844435`, não localizado no lugar aberto; nenhum dado pessoal nos ativos gerados — apelação/Creator Hub ficam com o usuário) confirmei que o lugar aberto contém todo o trabalho. **Teste de caminhada (Play, Studio/PC):** personagem real entrou nas 6 cavernas de urso do mapa novo (Urso_1–6) — a `Caverna_Urso_5` falhava por **degrau de ≈2,8 studs** entre o terreno da boca (y≈36,2) e o colisor de piso (topo 39,2); corrigido **baixando a `Estrutura` em 2,7 studs** e os marcadores `SpawnUrsoGigante`/`PontoCovil` junto; após isso, entrou. Obs.: o teste anterior de pathfinding indicava "ursos 6/7" (a Urso_2 da área antiga) — a caminhada direta das 6 cavernas novas passou, mas a Urso_2 antiga não foi re-testada via PathfindingService. Não testado: celular, publicado, multijogador, bears/IA. **O arquivo continua sem ser salvo por mim — o usuário deve salvar (Ctrl+S) e guardar cópia.**
**Montanha e Caverna do Urso (2026-10-22, pedido: "caverna do urso como um buraco nas montanhas ao lado da floresta"; a vila grande foi cancelada nesta sessão — "será no hub central", nada dela foi construído):** não havia montanhas (altura máx. antes ≈ 74 studs). Criei um **maciço no canto noroeste** (centro (150,−1100), pegada ≈ X −110…410 × Z −1360…−880, pico ≈ 192 studs, 3 cumes) por `Proto_Restore/MontanhaLib` (ReadVoxels/WriteVoxels; rocha/ardósia/granito). **Backup do terreno:** `Proto_Restore/TerrainMontanhaAntes` (TerrainRegion, só X −140…440, Z −1380…−844; restaurar com `Terrain:PasteRegion`); 496 árvores/plantas da pegada foram **movidas** (não apagadas) para `Proto_Restore/Originais_Arvores/Montanha_Urso`. **Caverna real esculpida no terreno** (FillBall Air + pisos planos): paredão de ≈ 50 studs, patamar plano em y≈78–80, boca ≈ 40 de largura, corredor curvo (≈ 100 studs), câmara principal (~60 de diâmetro, teto ≈ 50 studs, para ursos gigantes), toca lateral e alcova. **Rampa** sinuosa de 18 studs (inclinação 0,42) da floresta ao patamar. Marcadores em `Floresta_Blender/Exp_Ursos/Caverna_Montanha_Urso`: 2 `SpawnUrsoGigante`, 2 `PontoCovil`, 2 `Arena` (patamar R=30 e câmara R=32), `PontoEntrada`, 6 luzes de cogumelo, rastros. **Teste (Play, personagem real):** floresta → rampa → patamar → boca → corredor → câmara → toca lateral → alcova: **todos os 7 pontos alcançados a pé** (após corrigir 3 defeitos: embankment íngreme demais, poços no piso, pedras bloqueando o corredor). Prints 235–237. **Limites:** as 7 cavernas-modelo antigas (`Exp_Ursos`) continuam no lugar; sem trilha de rede ligando a montanha às demais (a rampa termina na floresta); iluminação interna só por 6 luzes suaves; vegetação do sopé = 36 árvores + 69 itens (esparsa); sem teste em celular, publicado ou com IA de ursos; Studio perdeu a conexão uma vez após escrever o terreno (reconectou). **Arquivo não salvo por mim — salvar (Ctrl+S) e guardar cópia (o terreno não tem desfazer além do TerrainRegion acima).**
**Rodada "aprimorar a floresta" (2026-10-22; pedido: vila existente 3x para batalhas, vegetação variada, samambaias com vento, chão vivo, trilhas visíveis, corrigir erros gráficos):**
- **Montanha NO reservada** como futuro bioma Montanhas/habitat dos ursos (memória + `Dados_Montagem/_Montanhas` + `_Sitios`); as 7 cavernas-modelo antigas seguem na floresta até serem substituídas.
- **Vila Principal ampliada (≈ 3x de área; raio de ≈ 100 para ≈ 165 + muralha)**, centro (2198,483), grupo `Floresta_Blender/Vila_Ampliada` (Casas, Muralha, Torres, Mercado, Iluminacao, Pouso_Dragoes, Arena_Batalha, Guardioes, Patrulha, Habitantes, Vegetacao; ≈ 1.430 partes): terreno aplainado em y≈35 até r=160 (módulo `Proto_Restore/VilaLib`; **backup `TerrainVilaAntes`**; rios preservados), 28 casas novas em 2 anéis (+ as 15 antigas), 23 bancas, 52 lampiões, muralha de 38 módulos com **4 portões nos ângulos das trilhas existentes (0°,53°,145°,287°)**, 12 torres (8 nos portões + 4 nos cantos), plataforma de pouso de dragões + **Farol** (torre de 80 studs com fogo e luz, visível de longe), arena de batalha R=46 (SO) + `Arena` de defesa R=165, 8 `SpawnGuardiao` nos portões + 2 `SpawnGuardiaoChefe` + 12 `PostoGuarda` + 28 nós de patrulha, 123 marcadores de habitantes (`SpawnHabitante`/`SpawnMercador`, com Profissao), 320 plantas. Ruas (Ground), praça (Cobblestone), arena/pouso pintados no terreno. **Objetos movidos (não apagados) para `Proto_Restore/Originais_Arvores/Vila_Ampliada`:** ninho elevado 8, clareiras de combate 2 e 3, mirante natural 2, ≈ 120 árvores/solo e props sobre vias/arenas — **o ninho e as 2 clareiras precisam ser recriados fora da vila**. Casas antigas Varanda/Taverna/Oficina/bancas foram deslocadas para fora das vias. **Teste (Play):** PathfindingService de fora de cada portão até a praça = Success (4/4), arenas/pouso/anel/casa = Success (4/4); personagem andou do portão E e SE até a praça (via waypoints); caminhada direta em linha reta pelo portão E bateu numa casa antiga (corrigido) — SW e N só completaram por caminho de pathfinding dentro do tempo limite, **FPS da vila não medido**.
- **Chão da floresta:** passe global de materiais do terreno (`Proto_Restore/ChaoLib`): Grass 72%→44%, **LeafyGrass 8%→39% (com serapilheira)**, Ground (terra) 11%→8% concentrada ao redor de troncos/clareiras, trilhas repintadas (centro Ground + borda Mud; furtivas finas), cor do Ground mais clara. Apron/rampa da montanha restaurados após o passe. Sem backup do terreno global (só materiais mudaram).
- **Vento V2** (`StarterPlayerScripts/Floresta_Vento`; V1 em `Proto_Restore/Floresta_Vento_V1_backup`): samambaias/plantas balançam ≈ 4–5° por fronde, fase própria, alcance 170 studs, copas ≈ 0,8–1°. **Não visto em Play/cliente.**
- **Nova família Blender `BLENDER/Biblioteca/F_Chao_Vivo` (18 GLB, scripts em `scripts/`):** Samambaia_Real_D/Vaso_E/Baixa_F, Capim_Alto_A/B, Trevo_A, Folhas_Cadas_A/B, Musgo_A, Flor_Branca/Amarela/Roxa/Vermelha, Cogumelos_C/D/E (coloridos), Galhos_A/B. **Aguardando importação pelo usuário; ainda NÃO colocados na floresta.**
- **Pendente:** importar e espalhar a família nova (adensar o sub-bosque), recriar ninho/clareiras removidos, medir FPS (vila e floresta), Rio C, cachoeiras, margens rochosas, revisão visual ao nível do jogador por setor, criaturas/IA (não pedidas). **Arquivo não salvo por mim — salvar (Ctrl+S).** Prints 235–240.
**Família F_Chao_Vivo importada e espalhada (2026-10-22):** os 18 GLB foram importados pelo usuário (vieram como MeshPart com `TextureID`); converti para `ServerStorage/Vegetacao/<nome>` (Model + MeshPart + SurfaceAppearance AlphaMode=Transparency, pivô na base; originais em `Proto_Restore/Testes_Importacao/ChaoVivo_Scenes`). Espalhados por `Proto_Restore/ChaoVivoLib` em `Floresta_Blender/Chao_Vivo` (529 pastas por ladrilho de 192 studs): **32.130 modelos de 1 parte** — Folhas_Cadas 7,8 mil, Capim_Alto 6,3 mil, Samambaias novas 8,4 mil, Musgo 1,3 mil, Flores 3,8 mil, Trevo 1,1 mil, Cogumelos 1,1 mil, Galhos 2,3 mil; regras: serapilheira/musgo/cogumelos perto dos troncos, flores/trevo/capim em "prados" (ruído), samambaias em LeafyGrass, nada sobre trilhas (≥ 4,5 studs), só itens baixos dentro das arenas (sítios), vila ampliada com conteúdo próprio. **Defeitos gráficos corrigidos:** `Grama_A/B` antigas (textura listrada com "pentes" pretos) → 3.093 trocadas por Capim_Alto; `Cogumelos_A/B` brancos sem textura → 555 trocados por C/D/E. Totais: **≈ 84 mil partes no mundo** (era ≈ 51,5 mil); ≈ 35 mil carregadas no cliente (StreamingEnabled).
**Vento V3** (`Floresta_Vento`; V1/V2 em `Proto_Restore`): atualização em lote (`BulkMoveTo`), no máx. 450 plantas num raio de 75 studs, copas até 300; custo medido por cálculo: varredura 7,6 ms a cada 0,6 s, tick das copas ≈ 1 ms. **A V2 (CFrame individual, raio 170) derrubou o FPS (≈ 29 com vento × 60 sem, no mesmo ponto)**; com a V3 o FPS ficou indeterminado: as medições seguintes travaram em 15,0 (janela do Studio sem foco), portanto **FPS NÃO confirmado** nem no PC. **Recriados fora da vila:** `Ninho_Elevado_18` (2148,1118) e `Clareira_Combate_12/13` ((2467,712),(2464,293)). **Pendente:** medir FPS com o Studio em foco, revisar terreno que ainda renderizava "branco" ao longe logo após as reescritas de voxels (provável atraso de renderização — conferir), ajustar densidade conforme FPS, Rio C, cachoeiras. Prints 241–244.
**Spawn no início da trilha (2026-10-22):** interpretei "início da trilha" como o começo da Estrada Antiga (`Oeste_Costa → Praça`, trilha primária mais longa, na costa oeste). `Proto_FlorestaAncestral/Proto_Spawn` movido de (1400,19,0) para **(−447, 24, 312)**, virado para o leste ao longo da trilha; o `SpawnLocation` genérico (0,0.5,0) foi **desativado** (Enabled=false) para não haver spawn aleatório. **Teste (Play):** personagem nasceu no ponto e andou 58 studs ao longo da trilha sem travar. Se o "início" pretendido for outro (ex.: portão da vila ou outra trilha), é só indicar.
**Raízes das árvores refeitas (2026-10-22; pedido: "todas as árvores estão com erros nas raízes"):** diagnóstico no Blender: os troncos tinham 6 raízes + 9 galhos como tubos finos e pontiagudos soltos (ilhas de malha separadas), o que dava o aspecto de "chifres/espinhos". Refiz os troncos (script `BLENDER/Floresta/scripts/raizes_v6.py`): 8 raízes de contraforte largas que nascem do tronco e afundam no chão + galhos curtos e grossos (LOD0 e LOD1; LOD2 não tinha raízes). Versões V4→V5→V6 iteradas com o usuário importando cada GLB (`BLENDER/Floresta/TroncosRaizes_V6_LOD0/1.glb`). **No Studio:** MeshId/Size/posição trocados via `ApplyMesh` nos 16 templates de `ServerStorage/ArvoresBlender` e em **4.467 de 5.575 árvores** (as restantes são LOD2 distantes, intocadas); atributos `RaizV4/V5/V6` marcam as instâncias; backups das cenas importadas em `Proto_Restore/Testes_Importacao/Troncos_Scenes`. Copas, colisores e tags não foram alterados. Outros ajustes: Musgo/Trevo/Folhas_Cadas escurecidos (estavam pálidos/translúcidos), 10 mil instâncias. **Não verificado:** FPS após a troca (≈ mesma contagem de triângulos nos troncos), tronco LOD2 ao longe, "manchas azuis" em algumas plantas (parece sombra azulada do céu sobre folhas escuras, não confirmado), árvore ancestral e gigantes só trocadas se usam esses templates. Print 245.
**Medição de FPS e revisão gráfica (2026-10-22, Studio em foco, Play, PC):** FPS no cliente (RenderStepped, ~3–4 s por ponto, após teletransporte): spawn ≈ 59; S3 mata densa 43 → 59 na repetição (primeira leitura incluiu carregamento por streaming); S4 56; S5 54; S6 60; praça da vila 60; árvore ancestral 47; costa oeste 47; com o vento V3 ativo. **Isto é FPS do Studio no PC do desenvolvedor — não vale como medida de celular nem de cliente publicado.** Correções: (1) serapilheira (`Folhas_Cadas`) reduzida a 62% do tamanho e escurecida, 131 removidas perto de trilhas (blocos grandes laranja/vermelho sobre as trilhas); (2) plantas de folha larga/arbustos/samambaias com `SurfaceAppearance.Color` levemente quente (238,255,205) em 21,4 mil objetos para reduzir o tom azul-acinzentado. **Não resolvido:** a face inferior das folhas largas vista de baixo continua achatada/escura (limitação de folha de plano único); troncos LOD2 distantes mantêm o mesmo mesh antigo (sem raízes); arquivo não salvo.
**Troncos caídos e ganchos de raiz (2026-10-22; o usuário enviou 2 prints):** (a) **Troncos caídos:** 443 colisores (`Tronco_Caido_*`) eram ≈ 55% da altura/largura da malha, por isso o personagem entrava no tronco; redimensionados para 88% da malha e recentralizados; 317 troncos que ficavam acima do terreno em encostas foram **baixados** (até 7 studs). Teste em Play: 5.316 raios laterais contra os colisores, 99,4% acertam (32 erros nas pontas afinadas); 4 troncos percorridos pelo personagem: **ninguém ficou dentro do tronco** — ele sobe por cima (a altura máxima observada foi ≈ 10 studs acima do chão; `MaxSlopeAngle` do Humanoid está em 89, o que facilita escalar). (b) **"Ganchos" nas árvores:** eram raízes longas e galhos baixos curvados que ficavam no ar em terreno inclinado. **V7:** raízes mais curtas (1,6–2,1 × raio) e enterradas 3,2 studs, galhos abaixo de 30% da altura removidos, galhos restantes retos e para cima; aplicada nos 16 templates e **4.471 instâncias** (`RaizV7`). Observação: a chamada de aplicação retornou "Target is not reachable", mas o resultado estava aplicado (verificado pelos atributos). Pendente: raízes ainda podem ficar no ar em encostas muito íngremes (nenhuma correção por árvore), LOD2 sem raízes, arquivo não salvo.
**Raízes flutuando em encostas (2026-10-22, 2º print do usuário):** em terreno inclinado as raízes ficavam no ar morro abaixo. Corrigido por árvore: amostrei o terreno em 8 direções a 1,2× e 1,9× o raio da base e **afundei a árvore inteira** (malha + colisor) pela diferença até o ponto mais baixo (−0,8×escala, máx. 6×escala). **2.967 de 4.467 árvores afundadas** (média 2,7 studs, máx. 13,6 em gigante); atributo `Hundido` impede repetir. Verificado visualmente numa encosta de ≈ 45° (raízes enterradas, só uma ponta aparece). Não testado em Play; colisores acompanham as árvores; árvores LOD2 distantes não foram ajustadas.
**Verificação sistemática de raízes flutuantes (2026-10-22; pedido: "verifique bloco por bloco"):** método: para cada árvore (4.454 com tronco LOD0/LOD1), 24 ângulos × 5 raios (1,0–2,5× o raio da base) — raio vertical para cima a partir do terreno (0,05 acima) contra a malha do tronco; um acerto até 6×escala = raiz suspensa, e o valor é o vão. **Correção:** (1) todas as árvores foram **recolocadas** na altura original (terreno − 0,6×escala), pois uma passada anterior as afundara demais (3–8 escalas); (2) vãos > 0,3 studs preenchidos com **terreno (Grass) sob as raízes** (≈ 30 mil blocos; formam montinhos suaves, sem cúpulas visíveis); (3) onde ainda sobrava vão, a árvore foi afundada em passos (≤ 2×escala, repetidos) e o terreno preenchido de novo. **Resultado medido ao final:** 4.417 árvores no mapa; **4.413 com vão < 0,35 studs** (99,9%), 4 com vão leve 0,35–0,8. **50 árvores** que não convergiram (falésias/margens, vãos até 10 studs) foram **movidas** (não apagadas) para `Proto_Restore/Originais_Arvores/Flutuantes`. Conferência visual em 2 pontos (encosta de ≈ 45° e árvore com montinho): raízes enterradas. Por bloco, as árvores movidas ficaram entre 0 e ≈ 16 (maiores: C3_3, C1_1, C2_0, C2_1). Atributo `GapV` guarda o vão medido por árvore. **Limitações:** a medição só vê a parte inferior da raiz (não valida a copa nem galhos); o preenchimento altera o terreno (sem backup global, apenas esses montinhos); o Studio ficou várias vezes sem responder durante a reconstrução do terreno e o terreno novo demora ≈ 2 minutos para renderizar; não testei Play após a mudança e não medi FPS; arquivo não salvo.
**2ª verificação geral e correções (2026-10-22; "faça outra verificação, resolva todos esses erros" — sem lista específica, auditei tudo que era verificável por script):** (1) **Console:** só avisos internos do Roblox (UIBlox "FoundationProvider"), nenhum erro do projeto. (2) **Props enterrados pelos montinhos de terreno** (efeito colateral da correção das raízes): 4.854 modelos pequenos (plantas, pedras, troncos, tocos; pastas Solo, Exp_Solo, Sotobosque, Margens, habitats etc.) estavam > 1,2 studs abaixo do terreno e foram **elevados** (máx. 10); 3.954 peças do `Chao_Vivo` também elevadas. Estruturas grandes (≥ 45 studs; 51 em Habitats, 21 em Exp_Ursos, 13 lobos, 19 ninhos, 9 vilas ocultas, 7 Exp_Solo) **não foram mexidas** — algumas estão naturalmente embutidas em encostas (cavernas/tocas) e não foram revisadas uma a uma. Flutuando (> 1,5 studs): 3 modelos (1 ruína, 1 habitat, 1 solo), **não corrigidos**. (3) **Árvores em conflito:** 64 troncos sobre trilhas e 38 sobrepostos entre si → **80 árvores movidas** (não apagadas) para `Proto_Restore/Originais_Arvores/Conflitos`. (4) **Play (Studio/PC):** FPS 59–60 no spawn, S3 e S4; PathfindingService: spawn→W1, W1→W2, W2→Ruína, Ruína→Ponte, Ponte→Altar, Altar→Praça, Praça→Leste = Success; W1→Praça (≈ 2.060 studs) = NoPath por limite do próprio pathfinding em rota longa; spawn do jogador em (−450,27,309). **Não verificado:** celular, publicado, vários jogadores; a elevação em massa de props pode deixar peças levemente suspensas em encostas íngremes (medição só no centro); arquivo não salvo.
**LIMPEZA DEFINITIVA DA VEGETAÇÃO DECORATIVA (2026-10-22; nova direção artística: sem rochas/troncos gigantes aleatórios, sem objetos flutuando):** (Studio reaberto: id novo `dcc40ebe…`, place com todo o trabalho anterior; PlaceVersion 163.) **Classificação:** estruturais/funcionais PRESERVADAS sem mudança de tamanho: Núcleo Ancestral (inclui o tronco colossal de travessia), Árvore Ancestral, Vila Principal, ruínas/altares (`Ruinas`, `Exp_Ruinas`), dungeons, Clareira do Guardião, mirantes, pontes, cavernas de urso (estruturas, `Caverna_Montanha_Urso`), tocas/ninhos/estruturas de habitat, árvores (todas as famílias) e `Chao_Vivo`. **Decoração tratada** (módulo `Proto_Restore/LimpezaLib`; tudo **movido, não apagado**, para `Proto_Restore/Originais_Arvores/Limpeza_Decor` com atributos `LimpezaMotivo`/`OrigPai`; escalas originais em `EscalaOrig`): **1.643 objetos removidos** (troncos C e raízes-arco gigantes, rochas grandes fora de arenas, excesso de troncos/tocos/pedras, itens na água, sobre trilhas, na entrada das cavernas de urso (raio 22), duplicados, atravessando estruturas/árvores, em penhasco/encosta extrema), **1.373 modelos redimensionados** (+ **8.984 plantas** reduzidas: arbustos ≤ 7 de altura/11 de largura, samambaias antigas ≤ 6/12, plantas largas ≤ 5/12), **6.196 reposicionados** (plantas pelo pivô a 0,2 abaixo do terreno; sólidos pela base sobre o ponto mais baixo da pegada), giro aleatório nos sólidos mantidos. **Em habitats/arenas** (lobos, ninhos, ursos, serpentes, clareiras, vilas ocultas, arena da vila) mantive cobertura de combate por habitat: ≤ 3 pedras grandes (≤ 20 studs), ≤ 4 médias (≤ 8), ≤ 2 troncos (≤ 20), ≤ 3 tocos (≤ 9). **Genérico** (Solo, Exp_Solo, Sotobosque, Margens, Margens_Exp): sem rochas grandes/troncos C/raízes-arco; 12% dos troncos (≤ 14), 50% dos tocos (≤ 9), 30% (margens 50%) das médias (≤ 6,5), 70% das pequenas (≤ 3,5 = seixos). **Colisões:** 669 partes de plantas/seixos sem colisão. **Reparo:** 20 submodelos aninhados deslocados por uma passada anterior foram recolocados (`filhos checados 3.229`). **Rampas de entrada** (terreno) criadas diante das cavernas de urso 1–4 e 6 (degraus de 2,6–4,3 studs entre piso e terreno). **Medidas (Studio/PC, StreamingEnabled):** ANTES: 228.032 instâncias, 83.119 partes, 10.312 colisivas, 3.568 modelos de pedra, 1.969 troncos/raízes, FPS 60/60/59,7 (spawn/S3/S4), 30.169 partes no cliente, 9.038 MB. DEPOIS: 217.994 instâncias (−10.038), 79.917 partes (−3.202), 8.598 colisivas, 2.154 pedras, 372 troncos/raízes, FPS 60/60/60,2, 29.005 partes no cliente, 9.393 MB (memória do Studio, não confiável). **Testes (Play):** as 6 cavernas de urso foram percorridas a pé de 40 studs de distância (6/6 entraram, após as rampas; antes 3/6 falhavam); arenas alcançáveis por PathfindingService: lobos 16/16, ninhos 18/18, ursos 8/8, serpentes 10/10, clareiras 13/13 + 3/3, habitats 22/24 (as 2 são arenas cujo centro é a própria estrutura — Toca_Lobo_4 e Clareira_Guardiao — com 8/8 pontos a meio raio alcançáveis). Auditoria de flutuação (centros e 5 pontos da base): de 186 itens flutuando restaram **0 nos decorativos** após o reassentamento final (165 itens em penhasco removidos); **6 itens estruturais** (2 pedras da Ruina_5, tronco do Mirante_Natural_1, 2 troncos do Núcleo Ancestral, 1 pedra do Mirante_Natural_3) ficaram **muito enterrados** (> 85% da altura) e foram deixados como estão por serem estruturais. **Capturas:** antes 250; depois 251–253 (mesmo ponto, ninho ao nível do jogador, aéreo com a Árvore Ancestral). **NÃO verificado / limites:** não revisei visualmente todos os setores um a um (amostras: ponto das capturas, ninho 1, aéreo do núcleo); Playtest curto (sem combate nem vários jogadores); celular não medido; capturas imediatamente após Play mostram terreno escuro por carregamento de textura; algumas plantas largas ainda parecem azuladas à sombra; **arquivo NÃO salvo por mim** — o MCP não tem comando de salvar (SavePlace só em script de servidor e publicaria); salve manualmente (Ctrl+S) e guarde cópia; a T3 histórica e o backup anterior não foram tocados; nenhum script de combate/inventário/economia/missão/persistência foi alterado. TASKS.md: nenhum item marcado `[x]`.
**Revisão visual ao nível do jogador (2026-10-22, 14 pontos no Studio em Edit com câmera a ≈ 5,5 studs; módulo `Proto_Restore/RevCam`, pontos em `Dados_Montagem/_RevisaoPts`):** pontos vistos: S3 (rio/margem), S4, S5, S6 (rocha/penhasco), S0 (só vista de fora: câmera caía dentro do tronco da Árvore Ancestral, 1ª imagem vermelha era textura carregando), vila (portão E e praça), ruína grande, lobos, serpente (lagoa), Clareira do Guardião, acampamento, ursos. Rios: só o trecho em S3 e a lagoa da serpente. **Corrigido:** (1) rochas do Guardião (52 studs) reduzidas a 26; (2) **1.211 rochas/tocos conferidos, 439 reassentados** pelo centro da base com 12% de enterro (rochas redondas ficavam suspensas porque o canto do bbox tocava o terreno mais baixo); (3) tentativa de trocar `AlphaMode` Overlay→Opaque nos adereços da vila **revertida** (deixou as lonas brancas); 608 SurfaceAppearance voltaram a Overlay (7 podem ter sido Opaque no original). **Achados NÃO corrigidos:** `Pilha_Lenha_A` e `Corda_Rolo_A` mostram aspecto "ondulado" visto de trás (faces de uma só direção na malha — requer ajuste no Blender); algumas rochas grandes inclinadas em encosta ainda mostram um canto no ar; vegetação sob luz forte aparece levemente azulada em plantas largas; sombra escura sobre o piso logo após reescritas de terreno (carregamento). **Não revisados visualmente:** margens dos rios C/D/B, S1/S2 detalhadas, ruínas pequenas, penhascos leste, interiores de cavernas, aldeias ocultas internas. Capturas 254–259.
**Pedras, troncos e tocas de lobo (2026-10-22, pedidos do usuário com capturas):** (1) 155 pedras grandes/médias (> 9 studs) removidas, depois **mais 496** pedras (≥ 5 studs), troncos caídos, raízes soltas e tocos soltos de todas as pastas não estruturais (habitats, lobos, ninhos, clareiras, ursos, serpentes, solo, margens); preservadas ruínas, altares, Núcleo, Guardião, dungeons, mirantes, Caverna_Montanha_Urso e seixos ≤ 5. Tudo em `Limpeza_Decor`. (2) **Tocas de lobo removidas** (decisão do usuário: "somente um ninho, e os lobos protegerão ele"): 56 modelos `Toca_Lobo_A/B` movidos para `Proto_Restore/Originais_Arvores/Tocas_Removidas`; os 28 territórios (16 `Exp_Lobos` + 12 `Habitats`) mantêm ninho (`NinhoLobos`/`Ninho_Elevado`) + ovos (168 `Ovo_Lobo`), arena, spawns de alfa/adulto/filhote e rastros. Atributo `SemToca` nos territórios afetados. Conferido visualmente em 1 território (ovos no ninho, sem pedras). Não rodei Play após isso; arquivo não salvo.
**Montes de terra/rocha nas bases das árvores e rocha sobre tronco (2026-10-22, 5 capturas do usuário):** causa: os "montinhos" de terreno que eu criei para fechar vãos sob raízes apareciam como blocos cinza/rochosos e deixaram plantas elevadas. **Correção:** (1) para cada uma das 5.445 árvores ajustei um plano ao terreno no anel 3,0–3,8× o raio da base (mínimos quadrados) e **cortei** (Air) com cilindro inclinado tudo acima do plano até 2,5× o raio — 4.709 montes removidos; (2) repintei o terreno em volta de cada árvore (rocha/ardósia/calcário/granito/basalto → Grass; fora da montanha NO); (3) afundei as árvores para encostar nas raízes no plano (≤ 2,2×escala por passo, 4 passos): **4.217 de 4.350 árvores com vão < 0,4 studs**, 19 com 0,4–1, 31 com 1–2; **100 árvores com vão ≥ 1,5 (falésias) movidas** para `Originais_Arvores/Flutuantes` (agora 150 lá); por bloco restam 33 árvores com vão ≥ 0,4 (maior: Arvores_Medias 6, C1_1 4, C3_2 3); (4) reassentei 14.511 plantas/seixos e 31.983 itens do `Chao_Vivo` (0 flutuando/0 enterrados na verificação); 13 plantas de `Exp_Ursos` marcadas "enterradas" são da caverna da montanha (raio vê o teto); (5) cogumelos do chão vivo reduzidos a 60% (1.092; estavam gigantes); (6) **Proto**: 156 pedras/troncos de Parts (`Chunk_Ancestral/Rochas` — a rocha sobre cilindro escuro da captura —, `Locais_Extra`) movidos para `Originais_Arvores/Proto_Rochas` (as 48 pedrinhas ≤ 5 studs das lagoas foram devolvidas); estruturas (Integracao_Nucleo, Locais, Vila, Travessias) preservadas. Verificação visual: 2 pontos (base plana e encosta ≈ 40°) sem monte, chão verde. **Limites:** o corte deixa degrau pequeno na borda do círculo em alguns pontos; raízes em encostas muito íngremes podem ainda ficar parcialmente enterradas; não testei Play depois; outros pontos citados nas capturas (rocha em tronco) conferi só por critério de nome; arquivo não salvo.
**Troncos deitados e pedras gigantes — remoção total (2026-10-22, pedido "TODOS"):** movidos para `Limpeza_Decor` mais **135** modelos (todos os `Tronco_Caido_*` e `Pedra_Grande_*`, `Pedra_Media_*` > 9 studs em ruínas, Exp_Ruinas, dungeons, Guardião, mirantes e Núcleo — **inclusive os 4 troncos colossais do Núcleo Ancestral que serviam de travessia**, a pedido). Preservados: pedras/troncos DENTRO da `Caverna_Montanha_Urso` (21 itens > 9 studs, interior da caverna), estruturas das cavernas e as árvores vivas. Escolha equivocada corrigida: 5 `ColisorTronco` de âncoras de árvore foram movidos por engano e devolvidos. **Flores:** o formato achatado (4 pétalas num plano) foi refeito em `BLENDER/Biblioteca/F_Chao_Vivo/Flor_{Branca,Amarela,Roxa,Vermelha}_A.glb` — haste curva em 3 segmentos, cabeça em cone raso de 8 faces voltada para cima/fora, folhas basais finas; gerado em Blender em modo background (`scripts/flores_v2.py` no scratchpad; **sem pré-visualização**); **aguarda importação** e depois troca das 4.837 flores do `Chao_Vivo`. Não rodei Play; arquivo não salvo.
**Flores V2 aplicadas (2026-10-22):** os 4 GLB foram importados; templates novos em `ServerStorage/Vegetacao/Flor_*_A` (V1 em `Originais_Arvores`); **3.837 flores** do `Chao_Vivo` trocadas (escala 0,45–0,75, giro aleatório, tag `PlantaBlender` para o vento) e reassentadas no terreno. Conferido visualmente: flores vermelhas em forma de tulipa, haste curva, apoiadas no chão. Só 1 ponto visto; as outras 3 cores não foram inspecionadas de perto. As 14 `Scene` remanescentes na raiz do Workspace foram arquivadas em `Testes_Importacao/Flores_V2_Scenes`. Arquivo não salvo.
**Rios, divisão, ruínas, luz, vento (2026-10-22, 4 capturas do usuário):** (1) **Pedras em rios:** 61 pedras (Margens, Margens_Exp, Solo, Exp_Solo, serpentes) na água ou a ≤ 7 studs de água removidas + 48 pedras das lagoas (`Proto/Locais_Extra`) movidas para reserva. (2) **"Divisão" = costuras do terreno antigo:** degraus de 5,6 studs em média (até 17) ao longo de x=2460 (z −560…1116), z=−560 e z=1116 (borda do retângulo X 900–2460 × Z −560…1116, onde a mistura de 170 studs falhou). Suavizei faixas de 88 studs em torno de cada costura por interpolação suave das alturas das bordas (≈ 24.600 colunas, água preservada; backups `Proto_Restore/TerrainCostura_1..3`). Medida depois: passo médio 0,14 / 0,77 / 0,24 studs (max 1,1–3,0). Reassentei 69 árvores, 250 props e 1.614 itens do chão vivo na faixa. (3) **Ruínas:** as 15 `Exp_Ruinas` + 6 `Ruinas` + 4 do Proto movidas para `Originais_Arvores/Ruinas_Removidas` (mantidos Núcleo, vila, acampamentos, mirantes, dungeons, Guardião, cavernas). (4) **Iluminação:** ambiente mais claro/quente (Ambient 0,40/0,43/0,36; Outdoor 0,46/0,49/0,40), ColorShift_Top quente, exposição +0,1, atmosfera mais quente e menos densa (0,26), bloom reduzido, DOF fraco, `ColorCorrection` novo (sat +0,12, contraste +0,05). (5) **Folhagem:** 6.147 SurfaceAppearance de arbustos/plantas largas tingidas (215,255,150) contra tom azul — algumas plantas escuras/azuis ainda aparecem na captura (provável outra família). (6) **Vento:** teste em Play: samambaia mexeu 2,25° em 3 s e copa 1,08° em 2 s, script ativo, FPS 60 (Studio/PC); amplitude aumentada (copas 1,4–1,8°, plantas 5,5–6,2°), **sem novo teste após o aumento**. Arquivo não salvo.
**Vila desafogada (2026-10-22, "muito empantufada"):** tudo movido (não apagado) para `Proto_Restore/Originais_Arvores/Vila_Removida`: casas novas 28→**8** (espaçadas ≥ 62 studs, prioridade Grande/Cabana/Oficina), 3 casas antigas (Pequena, Estacas ×2... Plataforma) , bancas 23→**8** no mercado + 3 na praça, 40 adereços (barris, caixas, cestas, lenha, corda, machado, bancos extras), lampiões 60→**20**, 127 plantas dentro do muro, 10 detalhes do Proto (horta, cercas, bandeiras, varais, carroça), 21 marcadores de habitantes das casas removidas (restam 60). Mantidos: muralha, 4 portões, 12 torres, farol/pouso, arena, praça com fogueira/mesa/poço/pavimento, plataformas de copa, taverna, casa grande, alta, cabana, varanda, oficina. Captura aérea e da praça conferidas; vila bem mais aberta. Os marcadores de guardiões/patrulha não mudaram; pathfinding e Play não retestados. Arquivo não salvo.
**Vila — fogo flutuante e sobreposições (2026-10-22, 2 capturas):** os 6 `LuzBraseiro` (partes invisíveis com Fire/luz a 4 studs do chão) e as 6 `Fogueira_A` do pouso de dragões foram removidos (chamas sem base); permanece o `FogoFarol` no topo do farol. Auditoria de sobreposição por caixa delimitadora entre casas/torres/muro/bancas/plataformas/farol: 7 modelos removidos (Banca_10, Banca_6, Banca_9, Banca_4, Casa_Grande ×1 sobre a plataforma de copa, Casa_Lona_B_35 no farol, Casa_Taverna×Varanda, Oficina×Cabana — um de cada par) e 3 postes de lanterna sobre o anel do pouso/plataforma; tudo em `Vila_Removida`. Verificação por colisão das casas restantes contra outras peças: nenhuma casa restante cruza outra estrutura. **Limites:** a checagem é por caixas/peças colidíveis (não detecta telhado que atravesse galhos de árvore ou copas); não retestei caminhos nem Play; arquivo não salvo.
**Áreas de descanso de lobo/urso na vila (2026-10-22):** `Vila_Ampliada/Descanso` com 4 marcadores `PontoDescanso` (atributos Especie, Raio, Uso=DescansoGuardiao): **2 de urso** (raio 20) em (2126,483) e (2171,423) e **2 de lobo** (raio 13) em (2305,561) e (2247,415), escolhidos em espaço livre (sem peças colidíveis, fora de vias, arenas, pouso e do anel central), ≥ 75 studs entre si. Cada área é um disco de terra batida (Ground + Mud no centro, ≈ 0,25 acima do terreno) sem decoração; plantas dentro dos discos removidas. Conferido visualmente só o disco do lobo (305,561). Nenhum NPC criado (sem IA). Arquivo não salvo.
**Descanso nos dois círculos grandes (2026-10-22, correção do usuário):** os 4 discos pequenos perto das casas foram desfeitos (terra repintada para grama; sobra um degrau de ≈ 0,25 stud que não removi). Os 4 `PontoDescanso` ficam agora **nos dois círculos grandes** (arenas pintadas de terra, longe das casas): **2 de urso na `Arena_Sudoeste`** ((2087,421),(2115,405)) e **2 de lobo na `Arena_Sul`** ((2154,612),(2178,596)), com atributo `Arena`. As arenas continuam servindo de espaço de batalha (uso duplo). Sem terreno novo nem decoração; sem animais. Vista aérea conferida. Arquivo não salvo.
**Apoios de descanso nos círculos (2026-10-22):** `Vila_Ampliada/Descanso_Props`: em cada arena (urso SO, lobo Sul) 1 rocha de apoio na borda externa (Pedra_Grande A ×0,5 para urso, B ×0,36 para lobo; ≈ 22×15 studs, 18% enterrada), 1 tronco caído ao lado (B ×0,5 / A ×0,35, com colisor), cama de folhas caídas (7 / 5) e musgo (3) sem colisão; marcadores `PontoDescanso` movidos para as camas. Removidos de dentro das arenas: 2 postes de luz, o antigo `Portal_Vila` do Proto e plantas. Exceção consciente à regra "sem rochas/troncos" por função de gameplay (descanso/apoio). Conferido em 1 captura (urso); lobo não visto. Arquivo não salvo.
**Iluminação realista (2026-10-22):** ClockTime 15,2, latitude 35, Brightness 2,6, Ambient (70,74,66) e OutdoorAmbient (118,124,110) mais baixos para sombras com profundidade, ColorShift_Top quente suave, ShadowSoftness 0,18, EnvironmentSpecular 0,6; Atmosphere densidade 0,30, haze 1,2, glare 0,25, cor neutra-azulada; Bloom 0,35 (limiar 2,2); SunRays 0,06; DOF quase desligado; ColorCorrection neutra (sat +0,04, contraste +0,08). Valores anteriores no atributo `AntesRealista` do Lighting. **`Lighting.Technology` não pode ser alterado por script (sem permissão)** — o usuário deve ajustar para **Future** manualmente nas propriedades do Lighting. Conferido em 1 captura (S4): sombras sob as copas, cores naturais. Arquivo não salvo.
**Fechamento das pendências da floresta (2026-10-22):**
- **Rio C escavado:** caminho A* existente (`_RioC_AStar`, de (1844,380) a (1988,−404)) suavizado (Chaikin ×3) e reamostrado a cada 4 studs (238 seções, ≈ 952 studs; eixo salvo em `_RioC_Final`). Nível da água 15,6 → 14,75 (monótono). Margens preenchidas até nível+1,2 (largura 34), crista cortada em terraços (22/36/52/70 studs nos níveis +1,2/+5/+10/+16 — atravessa o morro em ravina), canal de 14 studs com 3 de profundidade, leito de areia, beiras de lama. Água no eixo em 40/40 amostras. Backup `Proto_Restore/TerrainRioC_Antes`. 42 árvores e 208 props a ≤ 45 studs reassentados; nenhuma árvore/prop estava no leito; nenhuma trilha cruzada (só 1 ponto a 8 studs da trilha, sem ponte). `Toca_Lobo_9` ficou ao lado do rio (ponto de beber).
- **Cachoeiras/poços:** varredura da água do mapa (grade 8 studs, 3.300 células) achou 45 degraus de água; nos 10 maiores (queda 4,5–15,5 studs) criei cachoeira: degrau de rocha, paredões laterais de rocha, **poço escavado** (cilindro de água 7 studs de profundidade, leito de areia), cortina de água (Part Glass translúcida + partículas descendo) e névoa na base (`Floresta_Blender/Cachoeiras`). Defeito visto: em pelo menos uma cachoeira o paredão de rocha mostra mancha de água na face (voxels de água remanescentes); só 1 cachoeira inspecionada.
- **Plantas azuladas:** a família antiga `Arbusto_A/B` (A4) foi trocada pela `Arbusto_Largo_A/B` (A5) em **957** instâncias, mesma altura, sem colisão, tingidas e com vento. Não verificado visualmente depois.
- **Árvores reservadas:** de 230 (Flutuantes + Conflitos), **40 replantadas** em `Exp_Arvores_Replantio` (terreno ≥ 0,93–0,97 de planura, fora de água/trilhas/vila, sem vizinhas próximas, vão < 0,5 conferido); **190 seguem em reserva** (falésias/sem local).
- **Playtest final (Play, Studio/PC):** FPS 60 em S3 e na vila; no rio C a medição travou em 15,0 (janela sem foco, mesmo sintoma anterior — não conclusivo); ≈ 37,8 mil partes no cliente; WalkSpeed 96 (ajuste de teste do usuário). PathfindingService: spawn→W1, W2→Ruína, Altar→Praça, Praça→Leste e travessia margem O→E do rio C = Success; **42/42 arenas** de lobos/ninhos/ursos alcançáveis. Console: sem erros do projeto; avisos internos do Roblox e 2 assets "being generated" (meshes recém-importados ainda processando nos servidores Roblox). **Não testado:** celular, publicado, vários jogadores. **Lembrar:** WalkSpeed está 96 (voltar para 16 antes de publicar) e `Lighting.Technology` deve ser posto em Future manualmente. Arquivo: o usuário disse que salvaria; não confirmado por mim.
**Rios mais fundos e largos + água realista (2026-10-22, pedido: criaturas no rio):** módulo `Proto_Restore/RiosLib` processou os 271 blocos de 64×64 studs com água de rio (nível > 8,7; mar excluído), em 2 passadas: **alarga** até 2 células (8 studs) de cada lado por passada onde o terreno está até 6 studs acima do nível, **aprofunda** por distância à margem (2,5 / 4,5 / 6,5 / 8 studs) com leito de areia, e **levanta margens** que estavam abaixo do nível (corrige água "pendurada", o defeito da captura). Achado técnico: no Roblox, gravar Water sobre voxel sólido não substitui o sólido — agora grava Air e depois Water. Medidas no rio C: largura 20–38 studs (era 14), profundidade 5–6 studs (era 1,7). Backup do terreno por bloco em `Proto_Restore/TerrainRios_Antes` (271 TerrainRegions). Limpeza: 60 árvores e 820 props/plantas que ficaram na água movidos para `Originais_Arvores/Rios_Alargados`; 155 itens do chão vivo removidos; ~650 props reassentados; **pontes estendidas** (33 módulos em 7+ pontes) até as pontas saírem da água — o tabuleiro mantém a altura, então pode sobrar degrau nas pontas; varredura final de água pendurada: 10 + 12 pontos corrigidos com margem de terra. **Água:** WaterColor (38,72,66) verde-escura, transparência 0,82, reflexo 0,55, ondas 0,12 / velocidade 7 (valores anteriores no atributo `AguaAntes` do Terrain). Bordas entre blocos podem ter ficado 1–2 células mais largas (processamento sequencial). Visto em 1 captura; não testei Play. Arquivo não salvo após esta mudança.
## OPERAÇÃO M2 — MONTANHAS ALTAS (2026-10-22, autorização autônoma do usuário)
**Inspeção territorial:** Floresta Ancestral ocupa X −552…3792 × Z −2160…2184 (paredes invisíveis `Limites_Floresta`); a oeste só havia vazio (sem terreno, sem mar) a partir de x≈−700. Montanha NO reservada (−110…410, −1360…−880) fica dentro da floresta e foi preservada. Spawn: `Proto_Spawn` (−447,25,312). **Montanhas posicionadas a OESTE** da floresta (leste/norte/sul livres para os outros 6 biomas).
**Extensão real:** elipse irregular centro (−3250,−850), raios 2.450 × 2.560 → caixa X −5.800…−380, Z −3.500…+1.800 (≈ 4.900 × 5.100 studs; área de terra ≈ 18 M studs²), com orla de mar (nível 8) e uma **ponte de terra (Portão M0)** ligando à costa oeste da floresta em z≈−470 (11 paredes invisíveis da floresta removidas ali → `Originais_Arvores/Limites_Portao`). Gerador `Proto_Restore/MontanhasGen` (heightfield FBM + cristas + 8 picos 300–560 studs, vale, planalto, vila, santuário, lagos, cânions) + escritor `MontanhasWriter` (1.806 blocos de 128×128; colunas com terreno da floresta nunca sobrescritas). Material por altitude/declive (grama, terra, rocha, ardósia, basalto, neve só em pequenas áreas planas acima de 470).
**Regiões (coordenadas reais):** M0 Portão (−380…−1.150, −470) com posto de exploradores (−1107,−502: fogueira, 3 tendas, mesa de mapa, torre de vigia, placas); M1 Vale dos Pinheiros (centro −2100,−480, piso ≈ 86) com rio principal; M2 Desfiladeiros (planalto −2550,1050 em ≈ 240, cânion principal 8 trechos 176→90 e cânion secundário, ambos com rio no fundo); M3 Lagos (lago principal (−2580,−2060) r=330 nível 150; lago superior (−3080,−2330) r=110 nível 262 com cachoeira em 3 quedas 262→226→190→150 + poços); M4 Vila das Alturas (−3350,−760, y≈205); M5 Cavernas e Galerias (maciço −4250,250 e −4950,700); M6 Cumes e Penhascos do Vento (Cume do Vento (−4700,−700) 553 studs, Dente Sul (−5150,−1650)); M7 Santuário dos Picos (−4350,−2500, plataforma y=400, arena R=110).
**Biblioteca 3D (geração automática no Studio por IA, `generate_mesh`, sem Blender — importação 100% automática, sem ação do usuário):** `ServerStorage/Montanhas_Lib`: Pinheiro_Alto, Pinheiro_Torto, Abeto_Jovem, Pinheiro_Seco, Arbusto_Alpino, Casa_Montanha_A, Casa_Montanha_B, Estalagem_Montanha, Estabulo_Montanha, Torre_Vigia_Montanha, Santuario_Pico (1–4 MeshParts cada; troncos com colisão Hull; copas/plantas sem colisão; pivô na base). Reaproveitados da floresta: tendas, bancas, postes, cercas, monólitos, muros/colunas/arcos de ruína, ninhos, passarelas, Vegetacao F_Chao_Vivo. Nenhum `.blend` criado nesta operação.
**Hidrografia:** rio principal (10 nós, 150→7, deságua no mar ao sul do portão), 2 cânions com rio, riacho do lago superior, 2 lagos, cachoeira de 3 quedas (cortinas translúcidas + partículas + névoa), margens: 156 colunas de margem levantadas contra água "pendurada"; 62 pontos de borda do lago principal reforçados.
**Vegetação:** 7.680 árvores (pinheiros/abetos por altitude; transição com carvalhos/freixos LOD1 perto do portão; quase nada acima de 440) + ≈ 17.000 itens de solo (capim, flores, samambaias, musgo, folhas, arbustos alpinos, seixos) com exclusão de trilhas (9/7/4 studs), vila, santuário, lagos, pontes; tags `ArvoreBlender`/`PlantaBlender` (vento existente). Verificação: 15 árvores flutuando/enterradas removidas, 7.099 itens de solo reassentados pela base; 0 na água.
**Vila das Alturas (M4):** praça de pedra r=28, 4 ruas pavimentadas, estalagem, oficina, estábulo, 9+ casas (A/B) voltadas ao centro, 2 torres de vigia, santuário menor, 5 bancas, depósitos, 32 lanternas, 78 módulos de cerca baixa (anel r=235 com aberturas nas ruas), fundações de pedra nas estruturas em desnível; 22 marcadores de NPC + PontoMissao + 4 `EntradaVila`.
**Trilhas:** A* sobre grade de 24 studs (custo de declive e água), 17 rotas (8 primárias, 6 secundárias, 3 furtivas; `Dados_Montagem/_TrilhasMontanhas`), pintadas em terra; 1 rota (Cânion_Norte) sem caminho. **Pontes:** 4 pontes de passarela onde trilhas cruzam rios (cânion ×2, sul do vale, plataforma da cachoeira), cabeceiras com rampa de terra; checagem: pontas apoiadas (a da cachoeira tem 1 ponta 5 studs abaixo do terreno — degrau).
**Cavernas (M5 e habitats):** 10 cavernas reais esculpidas no terreno (domo de rocha + túnel + câmara + piso plano + rampa de entrada): Galeria_Principal (2 câmaras laterais), Galeria_Norte, Galeria_Oeste (1 lateral), **Minas_Silenciosas_Entrada (reserva de dungeon, `PortalDungeon_Reserva`)**, Toca_Urso_Norte/Leste/Sul (habitat de ursos gigantes, arena R=40 na boca), Gruta_Cumes, Gruta_Dente, Gruta_Sul_Lago; luzes suaves, depósitos minerais (marcadores). **Teste em Play: personagem entrou nas 10/10 a partir de 40 studs fora** (após 3 correções: câmaras abertas para o céu → domo; boca selada → reabertura; rampa apagada → reescrita em 2 passadas).
**Outros POIs:** 7 mirantes (y 62–250), 6 ruínas (M1×2, M2, M5, M6, M7), 6 ninhos de grande ave em plataformas altas (espécie a confirmar no catálogo), 3 territórios de lobos com ninho+ovos+spawns, 6 áreas de combate (R 34–55, veg removida), 3 acampamentos, Santuário dos Picos (santuário ×2,4, 8 monólitos, 4 arcos, 10 colunas/muros de cobertura, `SpawnGuardiao`, 4 entradas), 142 marcadores de ecologia (beber, pesca futura, emboscada de predador no cânion, coleta, 85 nós de patrulha).
**Testes (Play, Studio/PC):** PathfindingService 9/9 trechos: Floresta→Portão, Portão→Posto, Posto→Vale, Vale→Vila, Vila→Lago, Lago→Santuário, Vila→Cumes, Vila→Cavernas, Vale→Cânion = Success. Cavernas 10/10 a pé. FPS: Vila 59,3; Vale 58,4; Lago 58,7; Cânion 58,3; Santuário 59,4 (≈ 15 mil partes no cliente). **Não feito:** caminhada contínua do percurso inteiro de 15 etapas (só pathfinding + teletransporte por trechos; a tentativa de caminhada longa travou o Studio); celular; publicado; vários jogadores.
**Limitações honestas:** relevo lido do alto parece mais "colinas altas cobertas de pinheiros" que cordilheira — picos de 300–560 studs e floresta densa até ≈ 440; lago principal e lago superior têm contorno quase circular e a plataforma do lago superior é um cilindro de terreno visivelmente artificial; cachoeira inspecionada só por 1 ângulo; ventos mais fortes no M6 não implementados (script de vento é global); névoa global reduz a visibilidade dos picos à distância (não alterei Lighting global); mirantes M6 ficaram baixos (~240); 1 rota secundária sem caminho; vegetação usa 4 modelos de árvore (repetição visível em grandes extensões); nenhum `.blend`/Blender usado (geração por IA do Studio). **Arquivo NÃO salvo por mim (MCP não salva) — o usuário deve salvar (Ctrl+S).** TASKS.md: nenhum item marcado `[x]`.
## OPERAÇÃO M2-REFINO FINAL — MONTANHAS ALTAS (2026-10-22, autônoma; referência visual enviada pelo usuário)
**Referência seguida:** picos pontiagudos em cordilheira, platôs em degraus com paredões verticais, cachoeira em vários níveis com poços turquesa, rio em desfiladeiro, bosques de pinheiros com clareiras, céu limpo com nuvens. A metade "floresta/árvore gigante" da imagem corresponde à Floresta Ancestral e **não foi tocada**.
**Relevo V2 (`Proto_Restore/MontanhasGen`, V1 guardado em `MontanhasGen_V1`):** domain-warp + cordilheira (7 cristas ligando os picos) + picos com arestas irregulares (Cume do Vento ≈ 1.050, Dente Sul ≈ 950, Galerias ≈ 820; demais 520–780) + platôs em degraus (passo 58±16, paredões quase verticais acima de y≈150) + planícies suavizadas (sem "dunas"); lagos com contorno elíptico irregular (lago principal 360×245, lago superior 130×100, nível do superior subiu para 300); rios re-nivelados pelo terreno real (sem "aqueduto"), meandros, largura variável, margens acessíveis, corredeiras em degraus de 11 studs na saída do lago; cânion e cânion 2 com quedas naturais. Escritor `MontanhasWriter` V2 (água escrita junto com o terreno, nunca escreve x>-560 — floresta —, núcleo da Vila r<262 e Santuário r<190 preservados). Terreno reescrito 1806 blocos / 0 erros.
**Materiais:** paredões em **Sandstone** (cor 110,97,86) e picos em **Limestone** (146,146,150) — materiais que a floresta não usa (verificado por amostragem: floresta usa Grass/LeafyGrass/Ground/Rock/Sand/Slate/Mud). Neve só acima de ~880. Prados de grama uniforme (LeafyGrass raro), margens Pebble/Mud, trilhas pintadas em Ground. Cores originais guardadas como atributos no Terrain.
**Cachoeira dos Três Degraus (novo módulo `MontanhasCachoeira`, reaplicável):** lago superior (300) → queda 1 (52) → poço → queda 2 (48) → poço → queda 3 (50) → poço → lago principal (150); paredões em lóbulos verticais com estratos Rock/Slate, topos gramados, entalhes por onde a água sai; cortinas (vidro + camada branca), jatos de partículas, espuma e névoa na base de cada queda; passarela de madeira sobre o canal no patamar intermediário. Após 6 iterações (correções: água pendurada, poço escavando sob a borda, lóbulos escondendo as quedas, simetria excessiva).
**Ambiente regional (novo LocalScript `StarterPlayerScripts/Montanhas_Ambiente`, só visual/cliente):** transição no Portão (x −600 → −1050) para manhã (ClockTime 9,6, luz frontal nas quedas), atmosfera mais limpa (densidade 0,24, haze 0,35), água turquesa (34,118,128) e nuvens; ao voltar à floresta restaura os valores originais. Lighting/Atmosphere/Water do arquivo permanecem os originais (restaurados após as prévias).
**Cavernas V2 (12 bocas):** domo de rocha + túnel + câmara + rampa + moldura rochosa na boca; identidade por tipo: tocas de urso (Norte, Sul, **Cumes** nova) com cama de folhas, marcas de garra e arena; **Minas Silenciosas** com arco de ruína, colunas, monólito e luz azul (reserva de dungeon); galerias de exploração com lanternas e equipamento; grutas naturais (Cumes, Dente, Sul do Lago, Costa Norte) com musgo/cogumelos; **Gruta Alta dos Picos** marcada como acesso aéreo (penhasco — não acessível a pé, intencional para voo). Boca no nível do rio do cânion foi **fechada** com rocha.
**Rotas:** 21 trilhas recalculadas por A* sobre o **terreno real** (raycast, inclui domos/lóbulos), incluindo Portão, Vale, Vila, Lago/Mirante da Cachoeira, topo da cachoeira, Santuário, Cumes, Galerias, Minas, 3 tocas, grutas, Cânion. Rampa nova no degrau de 17 studs entre a praia da floresta e a ponte de terra do Portão (lado montanha). 3 pontes de passarela nas travessias de rio + passarela da cachoeira.
**POIs (menos, com intenção):** 4 mirantes (Cachoeira, Cânion, Cumes, Vale), 4 ruínas compostas, 2 ninhos de grande ave (espécie a confirmar no catálogo), 2 territórios de lobo (toca + 4 spawns), 5 clareiras de combate (1 aplainada), 3 acampamentos, 178 marcadores ecológicos (beber/pesca, emboscada no cânion, patrulha, coleta), 8 emissores de névoa baixa.
**Vegetação V2:** 5.008 árvores (bosques por ruído com clareiras abertas; sem árvores em paredões/rocha/água/trilhas/POIs; linha de árvores 300→520) + 10.828 itens de chão (gramíneas, flores em manchas, samambaias sob bosques, arbustos alpinos, seixos). Antes: 7.680 árvores + ~17 mil itens.
**Removido do workspace (movido para reserva, reversível):** vegetação V1 (24.602 modelos → `Proto_Restore/Montanhas_V1_Vegetacao`) e POIs V1 (Agua, Pontes, Cavernas, Mirantes, Ruínas, Ninhos, Lobos, Combate, Acampamentos, Ecologia → `Proto_Restore/Montanhas_V1_POIs`). Exclusão definitiva foi bloqueada pela proteção do ambiente; **pesam no arquivo — o usuário pode apagar essas duas pastas depois se aprovar o V2.**
**Testes reais (Studio/PC, Play):** PathfindingService em trechos de ~600 studs: **21/21 rotas 100%**; entrada a pé partindo de 40 studs fora: **11/11 cavernas acessíveis** (+1 aérea); caminhada real com `Humanoid:MoveTo` ao longo dos pontos da trilha (sem teleporte entre pontos): Portão→Posto (0 travamentos após a rampa), Posto→Vale, Vale→Vila, Vila→Cavernas (completa), Vale→Cânion (completa), Vila→Cumes (parcial), Lago→Topo da cachoeira (completa, chegou a y 324 ao lado do lago superior), 3 pontes atravessadas a pé; flutuação: Vila 147, Santuário 23, mirantes, ruínas, acampamentos, lobos = 0 flutuando/enterrados (1 placa do Portão corrigida, −13); clareiras: 0 árvores, desnível 1–5 (Cumes aplainada). **FPS:** nesta sessão o Studio estava em segundo plano e o FPS ficou travado em ~15 (limite de janela sem foco); tempo de CPU de render 15–17 ms/quadro nas 6 regiões (≈ orçamento de 60 fps) — **não é medição válida de FPS**; memória Studio em Play ≈ 9,7 GB.
**Limitações:** sem teste em celular; FPS real não medido (janela sem foco); viewport do editor ficou branco após muitas edições (renderização voltou no Play); paredões ainda visivelmente "voxel" de perto; picos isolados mais lisos que na referência; Mirante do Cânion fica dentro do bosque (vista só do alto da torre); 2 ninhos apenas; espécies de aves/criaturas não confirmadas no catálogo; Vila_Cumes andada só em parte; reservas V1 aumentam o tamanho do arquivo. **Arquivo NÃO salvo por mim (MCP não salva) — usuário deve pressionar Ctrl+S.**
## MONTANHAS ALTAS V3 — NATUREZA (2026-10-22; correção do usuário: "quero natureza, sem santuário monumental nem decorações")
**Salvamento:** o usuário informou que salvou (Ctrl+S) e gravou backup em `Documents\RPG_Roblox\BACKUPS` antes das mudanças. **Não consegui verificar o arquivo** (a pasta só mostra `RPG_BKP_2026-10-19_pre-M2b.rbxl`; o place pode estar salvo na nuvem do Roblox). MCP não salva.
**Relevo V3 (`Proto_Restore/MontanhasGen`, V2 guardado em `MontanhasGen_V2`):** hierarquia de picos — Cume do Vento ≈1.700 (ponta suavizada), Dente Sul ≈1.300, Sentinela Norte ≈1.150, Galerias ≈850, Poente/Costa/Toca/Lago 490–760; 7 cristas ligando picos; paredões em degraus; neve só acima de ~1.300 (corrigida a "cobertura branca" que pintava as montanhas inteiras); Limestone substituído por Slate/Rock (o Limestone renderizava quase branco).
**Transição natural com a Floresta:** o antigo estreito de mar (z −1650…1150, x −2300…−560) virou colinas e encostas arborizadas subindo da praia da floresta até o vale (`M.strait`/`hStrait`); a escrita a leste de x=−560 só preenche o antigo mar e para na areia/terra da floresta (nada da floresta foi alterado). 24 paredes invisíveis da floresta nessa borda → `Originais_Arvores/Limites_Portao`. Rampa/ponte de terra do Portão deixou de existir.
**Hidrografia:** rio principal re-nivelado pelo terreno (margens ao nível da água nos vales, corredeiras em degraus de 11 só na descida), continua até o mar ao sul do Portão; cânion estendido até o rio principal (afluente); novo rio de estuário na transição desaguando no mar a norte; lagos e Cachoeira dos Três Degraus mantidos. Cortinas brancas retangulares substituídas por 6 fios de água translúcidos por queda + jatos/espuma/névoa.
**Retirado (tudo reversível, em `Proto_Restore/Montanhas_Estruturas_Retiradas`):** Santuário monumental (templo, colunata, escadaria, portal), ruínas, mirantes-torre, acampamentos, pontes de madeira, estruturas do posto do Portão, objetos artificiais das cavernas (lanternas, caixas, cordas, arco/colunas/monólito das Minas, marcas de garra), modelos de ninho de dragão. Modelos gerados nesta etapa (Ninho_Dragao_Monumental, Templo_Santuario_Picos, Portal_Ruina_Grande, Coluna_Antiga_*, Muro_Antigo_Janela) ficaram só na `Montanhas_Lib`, sem uso.
**Natureza no lugar:** antigo santuário = **Clareira dos Picos** (clareira alpina irregular com anfiteatro rochoso natural a oeste, arena natural r=120, sem pavimento); **Covil do Dragão das Montanhas** = ressalto natural no Cume do Vento (−4600,1722,−600, r≈85, borda de rocha irregular com aberturas para pouso/decolagem; marcador `SpawnDragao` "Dragão das Montanhas (confirmar no catálogo)"); 4 ressaltos menores (Dente Sul 652, Galerias 821, Sentinela 612, Poente 603) só com marcadores; **Mirante do Cânion** = borda natural (−2364,228,1184), 96 acima do rio, árvores retiradas, borda de rocha baixa; travessias de rio = 4 **vaus** naturais de seixos (sem pontes).
**Cavernas:** 11 bocas recolocadas no relevo V3 (3 tocas de urso, galerias, Minas, 4 grutas), sem objetos artificiais; só luz suave e marcadores.
**Vegetação V3 (`MontanhasVeg`, V2 guardado):** floresta densa nos vales (<230), bosques irregulares nas encostas (230–520), árvores esparsas e menores no alto (520–800), só vegetação baixa/pedras acima; clareiras por ruído; desbaste de ~17% nas manchas mais densas; +1.118 árvores mistas (carvalho/freixo/pinheiro) na transição. Total ≈ 11.000 árvores + 11.791 plantas de chão. 2 territórios de lobo + 1 novo (tocas de pedra), 4 ninhos de ave em rochedos, 6 clareiras de combate naturais, 274 marcadores ecológicos (beber/pesca nas margens rasas, 77 zonas aquáticas, emboscadas, patrulhas, coleta).
**Vento:** `Floresta_Vento` (backup V3 em `Proto_Restore/Floresta_Vento_V3_Backup`): nas Montanhas a amplitude cresce com a altitude (até ~2,6× nos cumes) e a copa gira em torno do topo do tronco (tronco/raízes não se deformam); floresta inalterada.
**Testes (Play, Studio/PC):** PathfindingService em trechos de ~360 studs: **18/19 trilhas 100%** (Cânion_Nascente 2/3); entrada a pé **11/11 cavernas**; caminhada real (MoveTo) pela transição Floresta→Vale e Floresta→Norte sem travamentos (parcial, limite de tempo), **4/4 vaus atravessados a pé**; covil do cume visitado pelo personagem; flutuação: 0 em vila, tocas, ninhos e amostra de 2.224 árvores. **Desempenho:** CPU de render 16–25 ms/quadro; frame 65–126 ms com o Studio em segundo plano (não é FPS válido); memória do Studio em Play ≈ 11,8 GB; ≈24 mil partes no cliente. Desbaste aplicado depois da medição (não remedido).
**Limitações:** Cânion_Nascente com um trecho sem caminho; caminhada contínua completa não feita; mirante do cânion só razoável (cânion estreito nesse trecho); covil sem acesso terrestre (intencional, voo); celular e FPS real não medidos; reservas V1/V2 pesam no arquivo; espécies não confirmadas no catálogo (catálogo não está no repo). **Usuário precisa salvar novamente (Ctrl+S).**
## MONTANHAS ALTAS V4 — REFINO (2026-10-22, pedido do usuário; aplicado no place `rpg_roblox`, que é o único aberto — o texto do pedido citava "Dragon Ranch")
**Ligação Floresta→Montanhas:** subida contínua e suave (≈16 na borda da floresta → ≈45 na base das montanhas, colinas leves), sem ponte; a faixa de areia clara do antigo litoral foi coberta por grama, chão de folhas e lama (só a oeste da borda da floresta; 25 objetos da floresta na borda conferidos, sem soterramento). Gerador `MontanhasGen` (V3a guardado) e escritor `MontanhasWriter` (V3a guardado) usam a borda real da floresta medida em `_CostaFloresta.edge`.
**Árvores:** 3 coníferas novas geradas (Abeto_Montanha, Abeto_Esguio, Abeto_Velho; tronco + copa separados), 3x mais altas (vales 170–265 studs, encostas 140–215, alto 85–145), inclinação e escala variadas; total 2.276 árvores (antes ≈11.000) com clareiras e corredores; copas sem sombra projetada (o chão do bosque ficava preto). Modelo "Pinheiro_Robusto" rejeitado (aparência de cogumelo).
**Vento:** Floresta_Vento — nas Montanhas a copa balança 0,55x nos vales até 1,3x nos cumes, girando no topo do tronco (tronco/raízes fixos), alcance 520; floresta inalterada.
**Ninho no topo, acessível:** trilha de escalada natural em espiral (≈6 km, rampa 5–55%, platôs a cada ~800) entalhada no terreno do Cume do Vento, do fim da trilha Vila→Cumes (y 292) ao covil (y ≈1.723), dados em `_SubidaCovil`. Covil = platô natural com borda de rocha e ninho de galhos/chifres (1 modelo) deslocado do centro para deixar área de pouso. **Testado: personagem andou toda a subida com MoveTo (5 trechos, 0 quedas, 0 travamentos) e chegou ao centro do covil.** PathfindingService NÃO resolve 4 dos 5 trechos da subida (navmesh), importante para IA futura.
**Rios:** profundidade variável (trechos rasos ~1,6 para vau/bebedouro e poços fundos para emboscada aquática), margens ao nível da água, conexão com o mar mantida; 4 vaus de seixos; cachoeira reaplicada.
**Som e clima (`Montanhas_Ambiente`, V1 guardado; sons em `SoundService/Ambiente_Biomas`, áudios gratuitos da Creator Store — APM Music e Pro Sound Effects):** Floresta = música "Summer Dawn" + pássaros; Montanhas = música "Eternal Ice" + ar frio de montanha (mais forte com a altitude) + pássaros de montanha (somem no alto); crossfade na subida (x −600→−1300); luz da manhã, neblina leve/moderada (densidade 0,25, haze 0,38, +altitude), tom mais frio, nuvens; tudo volta ao original na floresta. Testado no cliente: os 5 sons carregam e tocam.
**Testes (Play, PC):** 19/20 trilhas 100% no pathfinding (falha: Subida_Covil, ver acima); 11/11 cavernas a pé (a Minas ficou bloqueada após reescrita do relevo e foi recavada); CPU de render 9,7–14,8 ms/quadro nas 6 amostras (antes 15–25); memória Studio ≈10,9 GB. FPS real/celular não medidos.
**Pendências:** usuário precisa salvar (Ctrl+S) — MCP não salva; pathfinding da subida; reservas antigas (V1/V2/árvores) ainda pesam no arquivo.
## ATMOSFERA V5 — FLORESTA x MONTANHAS (2026-10-22)
**Script cliente `StarterPlayerScripts/Ambiente_Biomas`** (substitui Montanhas_Ambiente; V2 guardado em Proto_Restore), só visual/sonoro, transição suave na subida (x −600 → −1300):
- **Floresta Ancestral:** tarde dourada (ClockTime 14,6), OutdoorAmbient quente, Atmosphere limpa (densidade 0,22, haze 0,45, cor quente), ColorCorrection quente (+saturação 0,1), SunRays 0,09, nuvens esparsas, água verde-escura.
- **Montanhas Altas:** manhã fria (10,8), exposição +0,22, ambiente azulado mais claro (sem sombra preta), Atmosphere densidade 0,29 / haze 0,85 (+altitude), cor/decay azuis, ColorCorrection fria (−saturação), SunRays 0,14 (raios mais concentrados), nuvens dinâmicas densas (cover 0,72), água turquesa.
**Música (playlists por bioma, fade de troca, pausa de 8–20 s entre faixas):** Floresta = Forest Dawn Prayer Song, Between Treetops, On the Wing (harpa/flauta), Summer Dawn; Montanhas = Silent Valley (alt.), Ragnarök Calm, Dawn 2. **Ambiência:** Floresta = brisa nas folhas + pássaros; Montanhas = vento de montanha (cresce com a altitude) + ar frio + pássaros de montanha (somem no alto). 12 áudios gratuitos da Creator Store (APM Music, Pro Sound Effects, DistroKid, TooLost, criadores da comunidade); testados no cliente: todos carregam. **Escolha feita por título/descrição — não pude ouvir; o usuário deve validar o gosto.**
**Céu/nuvens:** Clouds dinâmicas (Terrain) + GlobalWind (7,0,3). **Nuvens nos picos:** modelo `Montanhas_Altas/Nuvens_Picos` (Persistent) com 99 emissores de partículas de nuvem em anéis nas encostas altas (Cume do Vento ~1.220 e ~1.520, Dente Sul, Sentinela Norte, Galerias, Poente) e véus sobre os 3 cumes maiores; pré-emissão ao entrar no jogo. Skybox mantido (não trocado).
**Pinheiral:** desbaste estratégico de grupos densos 2.276 → 1.636 árvores (retiradas em `Proto_Restore/Arvores_Desbaste_V5`), copas sem sombra projetada, ambiente mais claro: chão, caminho e personagem legíveis sob as copas (comparado em Play). 12 emissores de névoa baixa nos pinheirais (`Nevoa_Baixa/Nevoa_Pinheiral_*`).
**Não feito/limitações:** skybox não substituído; FPS real e celular não medidos; o arquivo ainda depende de Ctrl+S do usuário.
## CORREÇÕES V6 — RIOS, BURACOS, PINHEIROS, TRILHAS, CLIMA (2026-10-22, a partir de 4 prints do usuário)
**Pico:** `Montanhas_Altas/Mar_de_Nuvens` (151 emissores de nuvem a y≈1290 num raio de 1.150 ao redor do Cume do Vento) + no script `Ambiente_Biomas` a neblina vira branca e densa (densidade 0,44, haze 1,8) quando a câmera passa de y≈1.180–1.400 nas Montanhas: do covil não se vê mais o vale (testado em Play).
**Buracos:** varredura do relevo inteiro (grade 12 e depois 16) — 74 depressões artificiais preenchidas com o material local; 13 aberturas no teto da Gruta_Sul_Lago tapadas; 11 cavernas recavadas e testadas a pé (11/11). Mantidos de propósito: 3 pontos (trilha de escalada e bacia do covil).
**Rios — Montanhas:** nível da água segue o terreno (sem teto do molde → acabou o cânion artificial; quedas/corredeiras em degraus de 14 onde o terreno desce); 2x mais largos (≈60 studs), 12–20 de profundidade com plataforma rasa nas margens; continuam até o mar. **Rios — Floresta Ancestral (autorizado pelo usuário):** `RiosLib2` (backup do terreno em `ServerStorage/TerrainRios_Antes_V2`, 271 blocos) alargou de mediana 36 → 56 studs e aprofundou até ~18; 95 plantas/árvores da floresta que ficaram dentro d'água → `Proto_Restore/Floresta_Veg_NoRio`; 22 módulos de passarela acrescentados para as pontes alcançarem as margens (uma extensão errada de 151 módulos foi desfeita → `Proto_Restore/Pontes_Extensao_Errada`).
**Pinheiros:** os modelos gerados por IA (aparência de blocos, folhas no chão) foram substituídos por 11 pinheiros/abetos realistas PBR da Creator Store (pacotes gratuitos de "Letaij": Ponderosa Pine Pack e Silver Firs; inspecionados: **0 scripts**), só variantes com tronco limpo na base → `Montanhas_Lib/Pinheiros_Reais`; 2.254 árvores (vales 150–225, encostas 120–185, alto 70–120), longe dos rios largos. Árvores anteriores → `Proto_Restore/Montanhas_Arvores_V4`.
**Vento:** o vento não funcionava (copas dentro de submodelos); `Floresta_Vento` agora anima todas as partes de copa, pivô no tronco, amplitude 1x (vales) → 2,2x (cumes) — verificado em Play (topos deslocando 0,9–2,6 studs).
**Trilhas:** 11 trilhas secundárias sem destino foram apagadas do chão (dados em `_TrilhasMontanhasV3_todas`); ficaram 9 principais mais largas: Floresta→Vale, Floresta Norte, Vale→Vila, Vila→Cumes→**Subida ao Covil**, Vila→Lago→Topo da cachoeira, Vila→Galerias, Vale→Cânion. 35 marcos de pedra empilhada (2 grandes no início da escalada, 1 a cada ~180 na subida, 1 a cada ~220 no caminho Vila→Cumes). Vaus de seixos nas travessias dos rios largos.
**Clima:** Floresta = sol do meio-dia forte (13,2h, brilho 3,4, exposição +0,18), tom quente, neblina dourada leve (densidade 0,31, haze 1,15). Montanhas = neblina fria mais forte (0,36 / 1,35).
**Testes (Play, PC):** 8/8 trilhas principais 100% no pathfinding; 11/11 cavernas a pé; subida inteira caminhada em trechos (0 quedas) até o platô do covil (y 1.718); vento e áudio conferidos. FPS real/celular não medidos. **Salvar com Ctrl+S.**

## V7 — CHÃO VERDE ÚNICO + RETIRADA DE ESTRUTURAS ALEATÓRIAS (2026-10-22, a partir do print da margem do rio)
**Chão das Montanhas:** `MontanhasGen.M.mat` reescrito (backup `MontanhasGen_V6`): sem manchas de Pebble/Mud/Ground/Sandstone; grama em tudo que é suave abaixo de y≈1.050; rocha (Slate/Rock em grandes áreas) só em encostas >~40° e no alto; neve só no topo. `MontanhasWriter` (backup `MontanhasWriter_V6`) sem as manchas de Mud/LeafyGrass da transição e sem camada de terra logo abaixo da grama. Superfície existente repintada por `Proto_Restore/MontanhasRepinta` (1.806 blocos, 270.076 colunas; água, leitos de rio, vila, covil, 9 trilhas principais e subida ao covil preservados). Superfície amostrada: Grama 59,7% → 66,6%, Sandstone 15,2% → 0,2%, Ground 3,6% → 1,5% (trilhas/leitos), Mud 1,8% → 1,1% (leitos sob a água).
**Placas planas no chão (manchas):** 1.981 `Folhas_Cadas_A`, `Musgo_A` e `Trevo_A` das Montanhas → `Proto_Restore/Retirados_V7/Montanhas_Manchas_Solo`.
**Mato e flores:** `Montanhas_Altas/Vegetacao_Flores` (`Proto_Restore/MontanhasFlores`): 20.117 plantas (flores amarela/branca/roxa/vermelha em prados por ruído + capim alto esparso), só sobre grama, encostas suaves, fora de trilhas/vila; sem colisão, sem sombra.
**Floresta — chão:** `Proto_Restore/FlorestaRepinta` trocou clareiras largas de terra/lama/seixo por grama (9.209 colunas, ex.: frente da toca do urso); trilhas estreitas (~6% do chão), vilas e núcleo ancestral mantidos; areia (só praia/margens ao nível do mar) mantida.
**Retirados (sem apagar) → `ServerStorage/Proto_Restore/Retirados_V7`:** troncos caídos, pedras grandes e médias (Exp_Ursos, Vila_Ampliada), monólitos/arcos/colunas/altar/santuários menores (Exp_Dungeons, Exp_Guardiao, Habitats), 4 acampamentos (tendas, barris, caixas, fogueiras), bancos de tora dos mirantes, do protótipo: Mirante_Norte, Mirante_Leste, Acampamento_Exploradores, POI_Altar, POI_SantuarioMenor, POI_MarcoAcampamento, Posto_Exploradores, Rochas primitivas, e um pinheiro solto na raiz do Workspace — 130 objetos + 1.981 placas. Cada objeto tem atributo `OrigPai` para restauração.
**Mantidos de propósito (aguardando decisão do usuário):** vilas (Vila_Principal, Vila_Ampliada, Vilas_Ocultas — que ainda têm 5 monólitos e 1 altar), ruínas do Núcleo Ancestral/Santuario_Ruinas (centro narrativo), entradas de caverna em rocha (tocas de urso/dungeons, 60–82 studs), pontes e o tronco colossal que atravessa o rio (2200,−103), tocas de lobo e ninhos nas Montanhas, 35 marcos da subida.
**Testes (Play, PC):** console sem erros do projeto; capturas em `SCREENSHOTS/M2V7_ChaoVerde` (margem do rio verde, prado com flores, toca do urso antes/depois). Nenhuma referência de script de jogo às pastas retiradas (busca por `Floresta_Blender` só encontra libs de montagem). FPS real/celular não medidos (+20 mil plantas pequenas — verificar no celular). **Salvar com Ctrl+S.**

## V7b — CHÃO ÚNICO EM TODOS OS BIOMAS + RAIOS DE SOL NA FLORESTA (2026-10-22)
**Manchas (placas planas) retiradas de todos os biomas:** 10.055 `Folhas_Cadas_A/B`, `Musgo_A`, `Trevo_A` (10.023 do `Chao_Vivo` da floresta, 18 da Vila_Ampliada, 14 das cavernas) → `Proto_Restore/Retirados_V7/Manchas_Solo_Todos_Biomas`. Varredura confirmou que não sobrou nenhuma placa plana de chão (só ossos das tocas e folhas da fogueira, que são parte dos modelos).
**Terreno:** `Proto_Restore/ChaoUnicoRepinta` (mundo inteiro, 3.375 blocos) + `ReplaceMaterial`: LeafyGrass → Grass em todo o mapa (um tom só); manchinhas isoladas de terra/lama/seixo/arenito (< ~1.100 studs²) → grama; trilhas contínuas, vilas, núcleo, covil e leitos sob a água mantidos. Floresta: Grama 44% → 79,7%, LeafyGrass 31% → 0%, Ground 5,9% → 1,2% (trilhas). Areia 13,8% = praias/margens no nível do mar (mantida).
**Sol na floresta:** perfil F do `Ambiente_Biomas` (backup `Proto_Restore/Ambiente_Biomas_V4`): hora 13,2 → 14,4 (sol inclinado, feixes visíveis), brilho 3,4 → 3,5, SunRays 0,16/0,5 → 0,30/0,72, luz ambiente de sombra mais clara (OutdoorAmbient 176,166,136; Ambient 118,110,88). Copas: sombra ligada em metade das árvores (2.366 de 4.762 partes, todas as gigantes) → sol e sombra alternados no chão (com 100% ficou escuro demais — testado e descartado). Atributo `V7_SombraOrig=false` marca as partes alteradas. Novo LocalScript `StarterPlayerScripts/Floresta_Raios`: feixes de luz (3 blocos Neon muito transparentes alinhados ao sol, partindo de aberturas entre copas, com poeira dourada), 6/12/18 conforme nível de qualidade (`ProtoTier`), só na floresta, fora da zona do protótipo (que já tem `Proto_FeixosLuz`).
**Testes (Play, PC):** feixes criados (7–9 no ponto testado, nível 3), visíveis entre as copas; manchas de sol no chão; console sem erros do projeto. Capturas 08–11 em `SCREENSHOTS/M2V7_ChaoVerde`. FPS real/celular não medidos — sombra das copas e feixes têm custo; checar no celular. **Salvar com Ctrl+S.**

## V7c — ÁRVORES FLUTUANDO, SEM AREIA/BRANCO, PEDRA LISA, PONTES, NINHO E HABITATS (2026-10-22, 9 prints do usuário)
**Árvores/raízes:** 41 árvores dentro do rio + 141 com raízes sobre a água (margens alargadas no V6) → `Retirados_V7/Arvores_Rio_V7`; 478 árvores assentadas no ponto mais baixo do chão sob o tronco; 164 plantas/raízes dentro d'água → `Retirados_V7/Plantas_Agua_V7`; 2.009 plantas assentadas no chão. Vilas, núcleo e Árvore Ancestral não mexidos.
**Terreno:** areia visível 0% (0 de 21.433 amostras em terra seca); sem neve/calcário (sem chão branco); Rock/Basalt/Sandstone/Pebble → Slate (pedra lisa); terra solta no alto dos picos → Slate (1.021 voxels; trilha mantida). Gerador: `M.mat` não gera mais Rock/Snow e só gera areia abaixo de y=6.
**ERRO e correção:** a troca em massa por `Terrain:ReplaceMaterial` transformou também a grama em Slate (floresta 84,7% Slate, montanhas 95,6%) — visto em captura no Play. Corrigido por `Proto_Restore/ChaoRestauraV7c` (voxel a voxel, mapa inteiro): grama em toda encosta suave (≤~40°, até y 1.050; até 1.300 se bem plano), Slate só em penhascos, picos, covil e pousos. Resultado: floresta 86,5% grama / 4,6% pedra; montanhas 66,4% grama / 29,9% pedra. Não usar `ReplaceMaterial` com vários materiais em sequência sem conferir.
**Pedras soltas:** 1.215 pedras pequenas (floresta + montanhas) e os 35 marcos de pedra empilhada → `Retirados_V7/Pedras_Soltas_V7`. Tocas de lobo, abrigos de rocha e entradas de caverna mantidos (habitats).
**Pontes:** as 17 pontes existentes (128 módulos) alargadas 3x (≈4,7 → ≈14 studs, para jogadores com animais; backup `Proto_Restore/Pontes_Antes_V7`). 18 pontes novas largas com rampas e postes de madeira (`Proto_Restore/PonteBuilderV7`): 15 em trilhas da floresta que cruzavam água sem ponte (`Floresta_Blender/Pontes_V7`), 2 nas Montanhas (`Montanhas_Altas/Pontes`), 1 substituindo a ponte de corda estreita do protótipo (→ reserva). Teste Play/PC: pathfinding Success em 18/18 (16 com o caminho sobre a ponte; F3 e Corda preferem outro caminho, mas atravessadas a pé sem cair na água). 3 pontes saíram com uma ponta dentro d'água e foram refeitas (versões erradas na reserva).
**Pico (Cume do Vento):** estrutura `Ninho_Galhos` (chifres/troncos) → reserva. Novo `Ninho_Gigante_Dragao` (~810 galhos entrelaçados, ~90 studs de diâmetro, borda ~15 com abertura voltada para a chegada da trilha), 3 ovos, 3 esqueletos de presa e 3 pilhas de ossos (malhas geradas por IA, `Proto_Restore/Tpl_DragaoV7`), 28 escamas trocadas.
**Pousos nos outros picos:** 7 cumes cortados em plataforma natural de pedra lisa (r≈34) com ninho e ossadas: Dente Sul e Sentinela Norte = Dragão das Montanhas; Maciço das Galerias, Pico da Toca, Pico da Costa, Pico do Poente, Pico do Lago = Wyvern. Os 4 ressaltos existentes viraram pousos de Wyvern com ninho pequeno. Marcadores `ZonaPousoDragao`/`SpawnDragao` com atributo `Especie` (confirmar no catálogo oficial). Nenhum dragão/IA implementado. 7 ninhos saíram desmontados (terreno recém-cortado) e foram refeitos.
**Ursos nas cavernas:** as 11 cavernas continuam (teto 22–44 studs medido); cada uma ganhou `Montanhas_Altas/Habitats_Ursos/Toca_*` com cama de capim/galhos, ossos e marcador `HabitatUrso` (Especie "Urso (confirmar no catalogo)").
**Testes (Play, PC):** console 0 erros do projeto; capturas em `SCREENSHOTS/M2V7c_Pontes_Ninhos` (inclui 2 capturas dos erros antes da correção). FPS/celular não medidos. **Salvar com Ctrl+S.**

## V7d — NEBLINA, PICOS ELEVADOS NATURAIS E RIOS 5x MAIS FUNDOS (2026-10-22)
**Neblina:** perfil M do `Ambiente_Biomas` (backup `Proto_Restore/Ambiente_Biomas_V5`): densidade 0,36 → 0,50, offset 0,06 → 0,30, haze 1,35 → 2,4; topo 0,52. Novo LocalScript `StarterPlayerScripts/Montanhas_Neblina`: bancos de névoa rente ao chão em volta do jogador nas Montanhas (6/10/16/22 por nível de qualidade), reposicionados conforme anda. Correção de bug: o clima podia ficar preso no bioma anterior após teleporte/respawn — agora reaplica a cada 1 s (testado: teleporte → 10,8h / densidade 0,50).
**Picos (espaço aéreo, sem plataformas):** as 7 plataformas planas foram desfeitas e os picos elevados de forma natural por `Proto_Restore/PicosElevaV7` (soma altura só na parte alta da montanha, decaindo do cume, cristas por ruído; protege cavernas, ressaltos, covil, vila, trilhas e água): Dente Sul 1.373 → ~1.920, Sentinela Norte 1.229 → ~1.775, Maciço das Galerias 1.012 → 1.316, Pico da Toca 755 → 1.023, Poente 723 → 865, Lago 571 → 749, Costa 283 → 386. O topo achatado de Dente Sul/Sentinela (corte da região de leitura) foi corrigido com agulha de rocha. 671 plantas/árvores soterradas → `Retirados_V7/Veg_Picos_Elevados_V7`; grama refeita nas partes suaves.
**Ninhos/pousos:** ninho em ombro natural perto do cume; em Dente Sul, Sentinela, Galerias e Poente o ponto era íngreme e o ninho foi assentado num pequeno nicho arredondado escavado na rocha (não plataforma). `ZonaPousoDragao` agora no cume (atributo `Aereo=true`), `SpawnDragao` no ninho. Ninhos/ossos das plataformas antigas → `Retirados_V7/Pousos_Plataforma_V7c`.
**Rios 5x mais fundos:** `Proto_Restore/RiosProfundoV7` em toda água interior acima do mar: leito = superfície − 5 × profundidade (máx. 26 × 5); 79.872 colunas; 59 pontos limitados para não romper cavernas; vazio abaixo da base do terreno preenchido para as paredes não ficarem abertas. Profundidade medida: Montanhas mediana 69 (p90 116), Floresta mediana 75 (p90 93) — antes ~14. **Sem backup do terreno dos rios** (operação grande); para reverter seria preciso um backup .rbxl anterior. 221 postes das pontes novas estendidos até o novo leito; 457 plantas que ficaram sobre a água → `Retirados_V7/Veg_Sobre_Agua_V7d`.
**Testes (Play, PC):** neblina e clima verificados por captura; picos e ninho verificados por captura; console 0 erros. FPS/celular não medidos. **Salvar com Ctrl+S.**

## V8 — REORGANIZAÇÃO DOS HABITATS DAS MONTANHAS ALTAS (2026-10-22, autorização com base em RPG_01/RPG_02)
**Fontes:** `Downloads\RPG_01_Mundo_e_Sistemas.docx` e `Downloads\RPG_02_Criaturas_Elementos_e_Poderes.docx`. Oficial: Dragão adulto 18–24 studs até os ombros (comprimento/envergadura PENDENTES; "porte dificulta manobras em espaços fechados"); Wyvern 9–13 studs, envergadura 30–42, habitat Montanhas Altas; Urso Silvestre = Floresta Ancestral; ninhos poucos, escalonados por jogadores, reaparecem em 30–60 min em outro local; Montanhas preveem ilhas flutuantes pontuais para voadores.
**Backup:** `Documents\RPG_Roblox\BACKUPS\RPG_BKP_2026-10-22_V7d_pre-habitats.rbxl` (137.189.115 bytes; cópia verificada por SHA-256 do arquivo que o Studio gravou em `Documents\Codex\...\prototipo_floresta_antiga\`). Ctrl+S do V7d informado pelo usuário. Backups de terreno locais (TerrainRegion) em `Proto_Restore/Backup_Nichos_V8` e `Backup_Cavernas_Dragao_V8`.
**Ursos fora das Montanhas:** `Montanhas_Altas/Habitats_Ursos` (11 tocas) e 3 `SpawnUrsoGigante` → `Proto_Restore/Retirados_V8/Ursos_Montanhas`. Cavernas preservadas; `Toca_Urso_Norte/Sul/Cumes` renomeadas `Caverna_Encosta_Norte/Sul/Cumes` (Tipo CavernaNatural; atributos `NomeAnterior`/`TipoAnterior`); todas as cavernas com `Classificacao=Exploravel_RefugioGenerico` (Minas = EntradaDungeon) e `EspeciesCompativeis="a definir pelo catalogo oficial"`; marcadores de descanso genéricos (Especie=Pendente). Gerador `MontanhasCavernas` e dados `_CavernasMontanhas` atualizados. Ursos da Floresta não mexidos. 0 referências ativas a urso nas Montanhas.
**Cume do Vento (Dragão das Montanhas):** ninho monumental preservado (ovos mantidos) e movido 15 studs para a parte mais larga do planalto (menor raio livre ao redor 48 → 56), cada galho mantendo a altura relativa ao chão; abertura reorientada para a chegada da trilha; restos acompanharam. Poleiro natural no cume rochoso y≈1.889 (marcador `Poleiro`). Marcadores corrigidos (Altitude 1948 → 1723). Escalada: 43/43 trechos com caminho (pathfinding) + trecho final até o centro do ninho caminhado (chegou a 3,1 studs).
**3 cavernas novas de dragão (paramétricas, `Proto_Restore/DragaoCavernaV8`, S=24 × fatores; atributos `Dim_*` na pasta):** `Caverna_Dragao_DS_A` (Dente Sul, boca y≈1.221), `SN_A` (Sentinela Norte, ≈1.075), `MG_A` (Maciço das Galerias, ≈756). Medido: túnel 40–56 alt × 51–65 larg; câmara 63–65 alt × 111–123 larg; alcova dos ovos 44–56 alt; rocha acima 141–559; ressalto natural de pouso na boca; ar livre à frente. DS_A rompeu a parede lateral no 1º corte → revertida pelo backup e refeita com a câmara deslocada 45 studs para o lado de rocha mais espessa; nenhuma abertura além da boca nas três. Ninho seco (sem ovos) na alcova de cada uma.
**Picos restaurados:** ninhos do Dragão em Dente Sul e Sentinela Norte retirados (`Retirados_V8/Ninhos_Picos_Recortados`). Os 4 nichos (DS, SN, Galerias, Poente): duas tentativas de reconstrução por interpolação removeram rocha natural/deixaram balcão oco → ambas revertidas pelos backups; solução final = suavização 3D localizada (`Proto_Restore/SuavizaTerrenoV8`) que arredonda nicho e calombo em um ombro de rocha contínuo (verificado por captura em DS e SN). Locais viraram `Poleiro_*` (só poleiro, sem ninho).
**Wyverns:** 5 ninhos na escala oficial (≈35 de diâmetro, ~10 de altura, `NinhoBuilderV7`): 4 ressaltos naturais + `Saliencia_Pico_da_Costa` (realocado para saliência plana 154 abaixo do cume). Pico da Toca e Pico do Lago sem ponto plano natural → só poleiro. Distância mínima entre ninhos ≥ 496 studs. Manchas de terra nos 4 ressaltos → pedra lisa (1.267 colunas). Ninhos antigos → `Retirados_V8/Ninhos_Wyvern_Escala_Antiga`.
**Marcadores (sem sistemas):** `Proto_Restore/MarcadoresNinhosV8` cria em cada local `Marcadores_V8` com Aproximacao, Orbita (8 pontos), Pouso, Descanso, Ovos, Decolagem (Direcao), Territorio (Raio 350 dragão / 220 wyvern), EntradaCaverna e `LocalNinhoElegivel` (Ativo, 30–60 min). 9 locais elegíveis (Cume do Vento, 3 cavernas, 5 wyverns) — só o Cume do Vento ativo (já exibe ovos); 6 poleiros sem ninho. Marcadores antigos `ZonaPousoDragao/SpawnDragao` → `Retirados_V8/Marcadores_Antigos_Pouso`. Nenhuma IA, rotação ou perseguição implementada.
**Ilhas flutuantes:** não construídas; possibilidade registrada para o planejamento das Montanhas (RPG_01 §4).
**Escala do mundo:** o mapa atual (~9.600 studs em X, Montanhas até x −5.800) é maior que a extensão inicial de 6.144 × 6.144 do RPG_01; mantido por decisão posterior do criador — registrar como atualização de planejamento, sem alterar o terreno.
**Testes (Play, PC):** 11/11 cavernas antigas com caminho por pathfinding; escalada 43/43 + chegada ao ninho; 3 cavernas novas medidas e inspecionadas (captura); 0 modelos flutuando nos habitats; 178 galhos de ninho sem apoio retirados. Observação: `M5_Cavernas/Gruta_Alta_Picos` é pasta órfã de versão antiga (marcadores dentro da rocha, y 278; não existe no gerador nem nos dados) — já estava assim, não foi criada nem mexida agora; sugerido mover para reserva. Outra divergência a decidir: `Territorios_Lobos` nas Montanhas (lobos oficiais são da Floresta/Tundra). FPS/celular não medidos. Capturas em `SCREENSHOTS/M2V8_Habitats_Dragoes`. **Salvar com Ctrl+S.**

## V9 — FLORESTA: PEDRAS/TRONCOS, PONTES, ILHOTAS, MARGENS, TRILHAS, PLACAS E RAIOS (2026-10-22, 10 prints do usuário)
**Atenção:** o V8 não teve Ctrl+S confirmado antes deste trabalho; último backup .rbxl verificado = `RPG_BKP_2026-10-22_V7d_pre-habitats.rbxl`.
**Pedras e troncos:** 15 arcos de caverna (rocha+raízes+colisores, apoiados em chão plano sem caverna), 13 rochas de toca de lobo/abrigo e 2.216 galhos/troncos do chão (8–22 studs) → `Proto_Restore/Retirados_V9`. Marcadores de habitat/spawn/arena/portal de dungeon mantidos.
**Pontes:** diagnóstico das 16 pontes antigas (5 terminavam na água, 4 entravam no chão, várias 7–13 studs acima do chão, 1 com lacuna) → todas refeitas com `PonteBuilderV7` (`Floresta_Blender/Pontes_V9`, 128 módulos antigos → reserva). Tronco colossal com escada (protótipo) → reserva (a travessia é coberta pela ponte G2). F11 e M1 refeitas (ponta na água). 4 pontes curtas novas onde trilhas cruzavam água sem ponte (T1–T4). Conferência: 72/72 pontas em terra na altura certa; pathfinding com caminho em 34/34 (6 preferem outra rota, todas atravessadas a pé).
**Ilhotas:** `Proto_Restore/IlhasRioV9` — 206 ilhotas/pilares de terra cercados de água (rios/lagos; no mar só muito pequenas) afundados até o leito vizinho; 75 plantas/árvores que estavam nelas → reserva.
**Relevo perto do mar (placa no rio, 1848,185):** margem oeste com paredão de 15–18 regularizada em declive natural (só rebaixando; backup `Backup_Margens_V9`), 17 modelos reassentados; uma suavização deixou prateleira marrom na água → corrigida (devolvida ao rio, 289 colunas).
**Margens (mapa todo, `Proto_Restore/MargensV9`):** leito raso de terra → pedra lisa; faces de barranco acima d'água: terra → grama; barrancos íngremes (>3 acima da água) junto à água → pedra lisa (o material Grass em face vertical aparece como terra no Roblox — causa das faixas marrons).
**Trilhas:** as trilhas principais e secundárias (`_TrilhasSuave1` + `_Trilhas`) repintadas contínuas (≈8 e ≈5 studs; 11.701 colunas + 481 recompostas após as margens); as furtivas (tocas) não foram pintadas nem sinalizadas, conforme RPG_01.
**Placas:** 5 placas antigas do protótipo (texto desatualizado; uma no rio) → reserva. `Floresta_Blender/Sinalizacao_Trilhas`: 41 placas de direção em junções onde os destinos se separam (+ praça da Vila e borda oeste), tábuas apontadas para a rota (grafo + menor caminho, `Proto_Restore/TrilhasGrafoV9`), texto nos dois lados. Destinos: Vila Florestal, Núcleo Ancestral, Montanhas Altas, Costa Norte, Costa Leste, Costa Sul (vilas ocultas e tocas não sinalizadas).
**Raios de sol:** `Floresta_Raios` (backup `Proto_Restore/Floresta_Raios_V8`) só cria feixe sob abertura de copa (≥2 de 4 raios vizinhos batem em árvores) e o feixe termina na altura das copas. Teste: praça aberta 0 feixes; floresta densa 6 feixes (40–98 de comprimento).
**Testes (Play, PC):** console 0 erros; capturas em `SCREENSHOTS/M2V9_Floresta_Pontes_Trilhas`. FPS/celular não medidos. **Salvar com Ctrl+S.**
**V9b (2 prints do usuário):** (1) placa encostada numa árvore e tábuas no mato → as placas foram refeitas com checagem de espaço: poste e cada tábua livres de troncos/raízes/casas/pontes (copa só conta se descer até a altura das tábuas), sem água, chão suave; tábuas mais altas (topo 10,8, mais baixa > 4); 10 plantas pequenas encostadas → `Retirados_V9/Veg_Junto_Placas`. 39 placas; 4 junções sem lugar livre ficaram sem placa (3 coladas na Árvore Ancestral, 1 na ponta de uma ponte). (2) trilha das Montanhas sem ponte: `Floresta_Norte` terminava na beira do rio (−1888,412), ponte mais próxima a 701 → `Montanhas_Altas/Pontes/PonteV9_FlorestaNorte` (96 de vão, ~14 de largura, atravessada a pé) + caminho de ligação até `Vale_Canion` (114 studs). As 9 trilhas principais das Montanhas foram repintadas (2.109 colunas; o passe de margens tinha virado grama nos trechos junto à água). Trilhas secundárias Mirante_Canion e Canion_Nascente cruzam água sem ponte mas não estão pintadas no chão (não visíveis) — não receberam ponte.
## M3 — BIOMA 03: PÂNTANO NEBULOSO (2026-10-22, "OPERAÇÃO M3 — CONSTRUÇÃO COMPLETA")
**Backup:** `Documents\RPG_Roblox\BACKUPS\RPG_BKP_2026-10-22_pre-M3-pantano.rbxl` (137.974.318 bytes; cópia verificada por SHA-256 do `pre-m3.rbxl` salvo pelo usuário). Ctrl+S informado pelo usuário antes de começar.
**Fontes:** RPG_01 (8 biomas; Pântano com 1 dungeon proposta; fauna ambiente provisória; árvores provisórias "Mangue Cinzento" e "Salgueiro Nebuloso"), RPG_02 (espécies OFICIAIS do Pântano: **Basilisco** — emboscada em lama/água rasa; **Crocodilo Primordial** — aquático, emboscada submersa), referências `02_BIOMES/02-pantano-nebuloso...png` e `03_CREATURES/03-basilisco-crocodilo...png` + imagem enviada pelo usuário.
**Posição (coordenadas reais):** a LESTE da Floresta Ancestral, ligado por terra à costa leste dela (costa medida e salva em `Dados_Montagem/_CostaLesteFloresta`; o gerador nunca escreve a oeste dela). Contorno: superelipse centro (5950, 0), raios 2.350 × 2.050 → terra x ≈ 3.850…8.250, z ≈ −2.000…+2.000 (~3.600 × 4.000 studs, ~11 km²); faixa de mar até ~8.550. O oeste (Montanhas) e o restante do mundo ficam livres para os 5 biomas futuros. Cota: lençol d'água 12,5 (oeste) → 9,2 (leste); terra 0–12 acima dele; colinas ≤ 9.
**Geografia/hidrografia (`Proto_Restore/PantanoGen` + `PantanoWriter`):** 8 regiões contínuas (P0 Entrada x≈4.150; P1 Bosque das Raízes (4.950, 1.150); P2 Águas Silenciosas (5.050, −1.050); P3 Canais da Névoa (5.950, 1.000); P4 Mata Afundada (6.250, −1.150); P5 Lago Profundo (7.060, −1.250), elipse 540×390, até ~50 de profundidade, com ilhota; P6 Ruínas (7.350, 1.250); P7 Coração (7.420, −160), clareira elevada r≈165 cercada por fosso d'água com 2 passagens naturais) + Costa Leste. Hidrografia: Rio Principal (nasce na Entrada, atravessa P2/P4, entra no Lago Profundo) e Foz (Lago → mar a SE); Canal da Névoa (P1→P3→P6→mar NE); Canal Central (P3→P7/Lago); Canal do Coração; 5 riachos; 5 lagoas irregulares. Meandros por ruído, margens suaves (sem paredes), profundidades 4–18 nos canais. Distribuição medida: terra ~48%, água rasa (<3) ~39%, funda ~13%. Água escrita com solo arredondado à grade de 4 (Roblox não guarda solo+água no mesmo voxel; sem isso a água rasa sumia — corrigido). Rios da floresta não cruzam a costa leste (deságuam a oeste do ponto de ligação); a ligação hídrica com o mundo é pelo mar (Foz SE e Canal NE).
**Árvores (família própria):** modelos IA (`Pantano_Lib`: Arvore_Colossal, Arvore_Inclinada, Cipreste, Ruina_Afundada, Muro_Afundado, Tronco_Travessia, Juncos, Vitorias_Regias) + pacotes Creator Store gratuitos e inspecionados (0 scripts): Willow Tree PBR (Wabbiits), Realistic Mangrove Trees (Letaij), Realistic Southern Swamp Trees Pack (Letaij). Árvores compostas em `Pantano_Lib/Modelos`: Gigante_Pantano(+B) = tronco IA com raízes tentaculares + copas PBR de salgueiro; Salgueiro_Nebuloso; Mangue_Cinzento 1/2; Seca (galhos secos). **1.108 árvores** por ecologia (`PantanoVeg`): Salgueiro 508, Mangue 387, Gigante B 127, Gigante 11, Secas 75; densas em ilhas/margens, mangues isolados na água rasa, 66 inclinadas sobre a água, clareiras por ruído, nada sobre trilhas/clareiras. Colisor cilíndrico simples por árvore (malhas sem colisão), `ModelStreamingMode=Atomic`. Descartados por qualidade: copas em cartões quadrados do pack "Swamp Trees" (241 trocadas), Mangrove 3 (textura não carregava), 2 pacotes com scripts ocultos ("TextureConfiguration", padrão de backdoor) — apagados sem uso; varredura do jogo: 0 scripts suspeitos.
**Solo/vegetação:** lama escura (Mud, cor própria) nas áreas encharcadas e leitos; grama nas ilhas (LeafyGrass fazia manchas → tudo Grass); 6.039 plantas (`PantanoSolo`): juncos 4.184 em touceiras nas margens, vitórias-régias 1.018 na água rasa, samambaias 691, flores 146. Juncos/samambaias/flores com vento (tag PlantaBlender).
**Caminhos:** A* sobre grade 8×8 da cota (`PantanoTrilhas`, `_PantanoGrade`): 14 rotas (9 principais + 5 alternativas) ligando a borda da Floresta a todas as regiões; terra firme preferida, vaus rasos aceitos; 11.866 colunas de trilha pintadas. Só 5 travessias fundas: 4 passarelas rústicas (`Travessias/Passarela_Pantano_*`) + 1 tronco caído estrutural (canal P3). Teste: pathfinding 128/134 trechos (os 6 restantes são as travessias sobre água funda — atravessadas a pé 5/5 sem nadar); trilha de entrada caminhada 10/10.
**POIs:** P7 — Árvore-Mãe do Pântano (gigante 1,85×, ~220 studs) na borda leste da clareira do Coração + marcador `ClareiraConfronto` (r 140). P6 — arco de ruína afundado numa lagoa rasa + 2 muros afundados + `PortalDungeon_Reserva` (inativo). 3 vestígios de muro em P3, P4 e P0. Nenhuma revelação de enredo.
**Habitats (marcadores, sem IA, `Pantano_Nebuloso/Habitats`):** Crocodilo Primordial — 16 HabitatAquatico (água >8), 14 EmboscadaSubmersa, 10 Descanso_Margem, 4 LocalNinhoElegivel (inativos); Basilisco — 4 Territorio, 16 Emboscada_Lama, 12 Descanso, 4 LocalNinhoElegivel (inativos); 9 Clareiras_Confronto. Nenhuma espécie inventada.
**Atmosfera/som:** `Ambiente_Biomas` (backup `Proto_Restore/Ambiente_Biomas_V6_pre_pantano`) com 3º perfil P (céu encoberto, luz difusa, névoa esverdeada, água escura reflexiva) misturado por x 3.700→4.250; música só do bioma dominante (sem sobreposição). Novos: `SoundService/Ambiente_Biomas/Musica_Pantano` (Drift_Beneath, Hollowtide, Calm_Drone, My_Stillness — Creator Store gratuitos) e `Ambiente_Pantano` (sapos/insetos, riacho, brisa, aves distantes) — 8/8 carregaram e tocaram em Play (música escolhida sem audição: validar). LocalScript `Pantano_Neblina`: névoa rente à água com força por região (mais nos Canais da Névoa, Coração, Mata Afundada). Vento e raios de sol estendidos às árvores do pântano.
**Desempenho (Play no Studio, PC):** 14–15 FPS médio (pior 8–9) no pântano **e igual na Floresta** no mesmo teste → o limite atual é do Studio/placa inteira (memória do cliente 11,4 GB), não específico do pântano. Pântano: 13.309 partes (~7× menos que a Floresta). **Não é medida representativa de jogo publicado; celular não testado.**
**Biomas anteriores:** Floresta (54.682 partes) e Montanhas (37.429) intactas; borda da floresta 31/31 amostras ainda em terra; nenhum script deles alterado além da extensão de vento/raios/clima.
**Pendências declaradas:** FPS real e celular; música ouvida pelo usuário; LOD manual (só RenderFidelity automático); folhas que balançam são as copas (musgo suspenso não é peça separada); árvores de pacote de terceiros na lista de créditos; dungeon do pântano só reserva. Capturas em `SCREENSHOTS/M3_Pantano_Nebuloso`. **Salvar com Ctrl+S.**

## M3b — CORREÇÕES PÂNTANO + FLORESTA (2026-10-22; pedidos "verifique setor por setor… névoa forte, rios fundos para crocodilos" e "raios solares, árvores flutuando, rios rasos, névoa, placas")
**Backup:** nenhum `.rbxl` novo feito nesta etapa; o último registrado é `RPG_BKP_2026-10-22_pre-M3-pantano.rbxl`. Tudo o que foi retirado está em `ServerStorage/Proto_Restore/Retirados_Pantano` ou `Retirados_V9` (nada apagado de forma definitiva, exceto objetos criados e refeitos nesta mesma etapa).
**Raios de sol (`Floresta_Raios`, backups V8/V9):** só na floresta (x −430…3.700, câmera −500…3.750); árvores do pântano retiradas da lista; feixes estendidos até 320 studs em 3 segmentos, subindo da copa ao céu (não "surgem do nada"); `SunRays` do pântano 0,04.
**Hidrografia do pântano (`PantanoGen`, backup `PantanoGen_V1`):** todos os canais/riachos fundos (Rio Principal 34, Foz 38, Canal da Névoa 26, Central 24, Coração 22, riachos 16–18), sem afinamento nas pontas; perfil com leito fundo + prateleira rasa só na borda (emboscada); lagoas 10–18; Lago 50; fosso do Coração 20; 7 poços-toca de crocodilo (`M.POCOS`, 28–54 de profundidade); riachos estendidos até se ligarem à rede; 2 fozes fundas no mar; rampa suave na costura com a floresta. Terreno reescrito 1.404/1.404 blocos, trilhas repintadas (11.704 colunas). A estrutura enterrada num riacho (vestígio) foi para a reserva. Áreas encharcadas de ~1 stud (lama/brejo) continuam rasas, como pedido.
**Árvores:** raízes flutuando corrigidas (82 baixadas), árvores sobre água funda retiradas, 24 mangues com galhos baixos sobre trilhas retirados; reassentamento após a reescrita (379 ajustadas, 6 retiradas; plantas 57 ajustadas, 38 retiradas); **+380 mangues de folha lisa** (`Vegetacao_Arvores/Mangues_Extra`). Floresta: 157 barrancos suavizados (`FlorestaBarrancosSuave`), 43 ligações rio→mar com degraus de água relaxados, 2.067 árvores reassentadas.
**Névoa:** perfil P mais denso (Density 0,6, Haze 2,5, Offset 0,22) + `Pantano_Neblina` mais forte (até 28 emissores locais); véu externo `Pantano_Nebuloso/Veu_de_Nevoa` (150 emissores, modelo Persistent) na costura com a floresta. Play/PC: dentro do pântano a visibilidade cai a ~80 studs; da floresta o pântano aparece só como banco de névoa (capturas 05/06).
**Travessias (trechos de trilha sobre água funda → 0):** Passarela_Pantano_4 refeita larga (PonteBuilderV7, 60 studs, margem a margem; antiga em `Retirados_Pantano/Passarela_Pantano_4_antiga`); nova **Passarela_Pantano_6** (canal do Coração, 49) com trilha P5 redesenhada para entrar/sair pelas pontas; nova **Passarela_Pantano_7** (Canais da Névoa, 96, pontas em terra/lama). `PonteBuilderV7.buildFixed` adicionado (pontas fixas; backup `PonteBuilderV7_preFixed`). Verificação: 121 amostras de trilha em água >2,5 → 0 sem estrutura; pathfinding 3/3 nas pontes novas.
**Crocodilo Primordial (marcadores V2, sem IA):** 17 sistemas de água funda (≥8) medidos; `Habitats/Crocodilo_Primordial` refeito — 11 Territorios (por sistema, com área, prof. máx., raio, população sugerida), 7 Tocas_Submersas (nos poços), 10 Corredores (197 pontos ao longo dos canais fundos), 8 Emboscadas_Travessia (água funda junto de cada travessia), 14 Descanso_Margem (margem seca, >30 da trilha), 4 LocalNinhoElegivel inativos (>60 da trilha). Antigo em `Retirados_Pantano/Crocodilo_Primordial_V1`. Basilisco/Clareiras reassentados no terreno novo (3 movidos para fora da água funda).
**Placas da floresta:** 39 → **13** (`Floresta_Blender/Sinalizacao_Trilhas`), escolhidas nas junções com mais direções, ≥380 studs entre si, **no máximo 3 tábuas** por placa (destino mais próximo de cada direção + Montanhas/Pântano quando cabe); "Costa Leste" trocada por **Pântano Nebuloso**; checagem de colisão real (poste e tábuas sem atravessar árvores/pontes; fora da trilha e da água). Junção do Núcleo Ancestral ficou sem placa (a árvore ancestral ocupa o local). Antigas em `Retirados_V9/Sinalizacao_Trilhas_V9`; moldes em `Proto_Restore/_Tpl_Placa`. Trilha de ligação floresta→entrada do pântano pintada (3.646→3.848, faltavam 200 studs).
**Bug encontrado e corrigido:** 25 paredes invisíveis `Limites_Floresta/Limite` (x 3.508–3.795, z −890…819) ainda fechavam a costura floresta↔pântano — pathfinding dava NoPath. Movidas para `Retirados_Pantano/Limites_Costura_Floresta_Pantano` (atributo `PaiOriginal`); 120 limites restantes (costas N/S/O) intocados. Depois: pathfinding floresta→pântano 4/4 e caminhada real do personagem pela costura 3/3.
**Testes (Play/PC no Studio):** console sem erros do projeto (só avisos internos do Roblox); pathfinding 7/7 rotas; capturas em `SCREENSHOTS/M3b_Correcoes_Pantano_Floresta` (6). **Não medido:** FPS real e celular; caminhada contínua de todas as 14 trilhas do pântano.
**Pendências:** usuário avaliar névoa (pode estar forte demais para combate) e posição das placas; decidir se as outras paredes de limite da floresta ainda fazem sentido com os biomas novos; música do pântano ainda sem audição. **Salvar com Ctrl+S.**

## M3c — FLUTUANTES, ÁGUA SEM MARGEM, DIVISAS E RIOS RASOS (2026-10-22; 11 prints do usuário: "corrija tudo, procure outros do mesmo tipo")
**Backup:** nenhum `.rbxl` novo nesta etapa (último: `pre-M3-pantano`); tudo que saiu está em `Proto_Restore/Retirados_Pantano` (`Arvores_Flutuantes_M3c`, `Mangue2_Substituidos_M3c`) e `Retirados_V9` (`Secos_Sem_Folhas_M3c`, `Plantas_Sobrepostas_M3c`, `Cachoeiras_Cortinas_V6`, `PonteV9_T1/T4`).
**Árvores flutuando (medição nova):** a checagem antiga só olhava o ponto mais baixo do modelo; agora `_G.TIPS` lança raios de baixo para cima em grade de 2,5–3 studs sob cada árvore e mede as pontas das raízes. Pântano: 714 descidas + 405 mangues assentados pela peça de raiz (`.005`, junção a 30% da altura da raiz); **Mangue_Cinzento_2 era um modelo de árvore deitada com a raiz no ar** → 309 trocados por Mangue_Cinzento_1 (mesma família/folha lisa; 18 em água funda não repostos). Floresta: 1.023 + 171 + 207 + 48 ajustes; recheck final: pântano 0/1.434 e floresta 0/5.077 flutuando (11 últimas corrigidas). Plantas pequenas: 2.019 + 1.047 + 262 descidas, 817 desenterradas.
**Árvores sem folhas:** 500 `Seco_A/Seco_B` da floresta trocados por Freixos (mesma altura ×1,1, rotação aleatória).
**Água sem terra segurando (paredes d'água):** varredura de voxels (água vizinha de ar) achou ~13.500 voxels em 488 blocos. `_G.WFIX`: borda vira Slate em degrau entre poços, Grama em margem mais baixa que a água, Lama sob bolsões de ar → 12.733 voxels; revarredura 0. Bordas do mar do pântano (|z|>2.200, x>8.250) terminam no vazio do mundo — não alteradas (longe/névoa). 10 "cortinas" de cachoeira flutuantes retiradas. Limitação: degraus de pedra aparecem onde o rio desce em escada.
**Torre/lago elevado e vila:** lago suspenso sobre pedestal de pedra na Vila Ampliada (2.111–2.175, 644–704) removido e terreno mesclado; Torre_Canto_2 no chão. 55 estruturas em declive receberam base de terra (sem enterrar casas). Sobreposições: 72 objetos realocados ao lado, 94 plantas dentro de objetos retiradas. **Erro meu corrigido:** repintura ampla apagou parte da praça de terra da vila — refeita em elipse (2.196, 628).
**Divisas/fendas:** margens de rio em parede (água 8–17 abaixo) viraram rampa 0,6 (~31°, grama verde) em 23.596 colunas, protegendo 12 studs ao redor de pontes/estruturas/placas; canais secos de pedra (1.302 col.) e fendas estreitas (560) preenchidos; degraus verticais ≥6 suavizados (27.178 col., montanha NO reservada excluída); pedra rasa sob a grama repintada (5.715); trilhas repintadas nas colunas alteradas (1.230 + 1.152).
**Pontes:** PonteV9_T1 e T4 (troncos sem água embaixo) para a reserva; demais com água sob o vão.
**Rios rasos do pântano 5×:** 58% da água tinha <2 de profundidade (2 manchas de ~2 milhões de studs²). Aprofundado por voxel (`_G.DEEPEN`): prof. = máx(5×atual, 6), teto 40, rampa 3/célula a partir da margem; montículos preservados sob árvores (r6), juncos (r3), travessias/POIs → 1,6 milhão de voxels. Trilhas que vadeavam: 35 trechos viraram **passagens elevadas de terra** (sem pontes novas) + 221 pontos complementares; recheck: 122 amostras >1,5 de água na trilha, 0 sem estrutura; 0 água exposta. 9 `Emboscada_Lama` do Basilisco movidas para água rasa.
**Testes (Play/PC):** console sem erros do projeto; pathfinding pântano 84/84 trechos; floresta→pântano OK; capturas em `SCREENSHOTS/M3c_Flutuantes_Agua_Divisas` (14). **Achado não resolvido:** PathfindingService dá NoPath em zonas do sul/oeste da floresta (ex.: 1.344,−1.000) até em 12 studs, mas o personagem anda normalmente ali (5/5 MoveTo) — não sei se já ocorria antes; investigar se a IA de criaturas usar pathfinding. Montanhas não varridas nesta etapa. FPS/celular não medidos.

## M3d — BASE REAL DAS ÁRVORES, NÍVEL ÚNICO DA ÁGUA DO PÂNTANO, ILHOTAS (2026-10-22; 5 prints: raízes/tronco flutuando, "árvores pratas", "terra no meio do rio")
Ctrl+S do M3c confirmado (estado reaberto contém P7, 0 Mangue_2, 0 Secos). Studio reconectado com novo id `66060a67-…`.
**Causa raiz das "terras/faixas" no rio do pântano:** a reescrita do M3c deixou água em 3 alturas (8/12/16) → a borda entre níveis virou degrau de pedra. Toda a água do pântano agora tem topo único em 8 (água acima removida; degraus de pedra junto à água viraram água/ar). **Erro meu durante isso:** o 1º passe (773 de 1.332 blocos) converteu pedra subterrânea em água/lama; detectado pelos contadores e restaurado (3.743.363 voxels de volta a Slate abaixo do 1º sólido); o restante feito com versão corrigida. Revarredura: topo da água só em 8, 0 água exposta, 119 voxels de pedra na superfície (ruínas/costura).
**Ilhotas:** 781 montículos <400 studs² viraram água de 4 (5 mangues mantidos com raiz no leito, 255 juncos baixados ao leito) + ilhotas vazias ≤1.600 studs² sem árvore/trilha/estrutura removidas (324 plantas para `Retirados_Pantano/Ilhotas_M3d`); 1.653 voxels de margem refeitos. Ficam 220 ilhas pequenas com árvore, trilha ou estrutura.
**Árvores — medição nova:** raios contra a malha do tronco são inconfiáveis em parte dos modelos (ex.: Freixo_B_76 o raio acertava o tronco a 92 com a base em 40) — por isso sobravam raízes no ar. Agora `_G.BASEFIX`: base geométrica do tronco (AABB da peça Tronco/Trunk/raiz `.005`) = menor chão sob 70% da pegada (água conta como superfície −1) − 0,4; enterramento limitado a 22% da altura do tronco. 6.510 árvores (floresta + pântano): 433 ajustadas no passe final; 55 em encosta íngreme → 47 realocadas até 24 studs, 8 para `Retirados_V9/Arvores_Encosta_M3d`. Um passe intermediário meu afundou salgueiros/carvalhos (medição pelo raio) — corrigido pelos passes seguintes; captura 02/03 confirmam.
**Árvores pratas:** não encontrei peça sem textura (varredura de MeshParts/SurfaceAppearance) nem mangue tombado; as 73 `Seca_*` (galhos secos cinza) do pântano foram trocadas por mangues (72; 1 em água só retirada, `Secas_Pantano_M3d`). Se ainda houver uma prateada, preciso da posição.
**Outros:** 16 ninhos de lobo/aves submersos até −98 ou enterrados movidos para terra seca próxima; 2 `Tronco_Caido` (props da Vila Ampliada) para a reserva; 499 vitórias-régias ajustadas à nova superfície, 35 em terra retiradas; 216 marcadores aquáticos de crocodilo baixados para dentro da água.
**Testes (Play/PC):** console sem erros do projeto; pathfinding pântano 84/84; trilhas do pântano: 97 amostras em água >1,5, 0 sem estrutura; capturas `SCREENSHOTS/M3d_Base_Arvores_Nivel_Agua` (5). Pendente: pathfinding da floresta (NoPath em zonas onde se anda), FPS/celular.

## M4 — BIOMA 04: PLANÍCIES DOURADAS (2026-10-22/23, "OPERAÇÃO M4 — CONSTRUÇÃO COMPLETA")
**Salvamento/backup:** o estado do M3d estava salvo (verificado ao reabrir: P7, 0 Mangue_2, 0 Secos). **Nenhum `.rbxl` de backup novo** feito antes do M4 (o último em BACKUPS é `pre-M3-pantano`); T3 histórica intocada. **Salvar com Ctrl+S ao revisar.**
**Fontes:** RPG_01 (Planícies perto da região inicial; "alguns rios largos e zonas de travessia"; árvores provisórias Acácia Dourada/Olmo dos Ventos; fauna de coleta provisória Antílope Dourado, Avestruz-da-Pradaria, Tatu-de-Casca) e RPG_02 (espécies OFICIAIS: **Leão Solar** 10–13 studs até os ombros, emboscada/arrancada em campo aberto; **Búfalo Colossal** 14–18 studs, cargas em campo aberto, curvas difíceis). Referências: 3 imagens enviadas (campos dourados com acácias/ruína, colinas com trilha, rio entre campos amarelos).
**Posição real (medida, sem sobrepor):** ao SUL da costa da Floresta e das Montanhas, onde antes era vazio (eixo +Z do mapa). Costa existente medida voxel a voxel e salva em `Dados_Montagem/_CostaSulMundo` (x −4.200…2.800); o escritor nunca escreve em z ≤ costa+2. Contorno: superelipse centro (−650, 4.200), raios 3.250 × 2.050 → terra x ≈ −3.900…2.550, z ≈ costa(1.150–2.250)…6.250 (~6.400 × 4.500 studs). Leste (x>2.700, abaixo do Pântano) e o restante do sul ficam livres para os próximos biomas. Água em nível único 8 (igual ao Pântano). Geradores: `Proto_Restore/PlaniciesGen` (altura/regiões/rios/materiais) e `PlaniciesWriter` (2.332 blocos 128²).
**8 regiões:** P0 Campos da Aurora (150, 2.650) entrada; P1 Mar de Capim Dourado (1.250, 3.750); P2 Colinas do Horizonte (−2.450, 3.350) com cume panorâmico ~117 em (−2.600, 3.100); P3 Vale das Águas Claras (−1.400, 3.750) fértil e verde; P4 Bosques Solitários (1.250, 5.150); P5 Terras das Flores (−2.750, 5.150); P6 Pedras Antigas (−3.150, 2.450) patamares e paredões curtos de arenito; P7 Grande Campina (−250, 5.050) campo amplo suavizado (sem arena). 13 colinas (26–92) + ruído; alturas de 8 a ~120.
**Hidrografia:** Rio Dourado (meia-largura 16→40, prof. 20) nasce numa lagoa-nascente em (−2.690, 1.785) no pé das Montanhas, atravessa P2/P3, passa pelo Lago Espelho (−1.000, 4.620, prof. 26) e deságua no mar sul (−1.860, 6.450). Afluentes: Ribeirão da Aurora, Riacho do Capim (com Lagoa do Capim) e Riacho das Flores (com Lagoa das Flores). Perfil com leito fundo, prateleira rasa e margem suave; **5 vaus rasos** (≤2,6) para manadas e jogadores. Ligação com o mar: foz sul + costa marinha em volta do bioma (mesmo nível 8 do mar existente). O rio das Montanhas que caía no antigo vazio terminava num paredão d'água: a encosta foi remodelada (relaxamento + rocha nas faces íngremes) e o rio de cima termina numa poça da encosta — **não há cachoeira ligando os dois rios** (pendente).
**Solo/vegetação (prioridade):** materiais contextuais — campo seco = LeafyGrass com **MaterialVariant gerado `Planicies_Capim_Dourado`** (override só da LeafyGrass, material que não é usado em nenhum outro bioma), margens/vales úmidos = Grass verde, encostas >0,78 = Arenito (cor rocha), trilhas = Ground, leito = Ground/Lama. Capim 3D: LocalScript `Planicies_Capim` gera ao redor do jogador um campo estável (grade 4,2 studs, posições determinísticas) com 2 malhas IA (`ReplicatedStorage/Planicies_Assets`: Capim_Dourado_Alto, Tufo_Dourado_Baixo) + 4 flores do jogo; anel distante (até 175) com capim alto maior; pool fixo (~1.250 próximas + 420 distantes no nível 3; menos em tiers baixos e se o FPS cair). Flores concentradas em zonas por ruído (P5), poucas nas margens.
**Vento:** no mesmo script, ondas que viajam na direção do `GlobalWind` (2 frequências + rajadas) inclinando cada tufo a partir da base (BulkMoveTo em lote, sem scripts por objeto; medido 0,7° em 0,7 s num tufo). Árvores usam o vento existente (`Floresta_Vento`, tag ArvoreBlender).
**Árvores (família própria, poucas e grandes):** `ServerStorage/Planicies_Lib`: Acácia Dourada A/B/C (copa larga achatada em guarda-chuva, tronco alto, tons dourados) e Olmo dos Ventos A/B, derivadas dos modelos PBR da floresta; colisor cilíndrico simples. **289 árvores** (8 bosques pequenos, isoladas nos cumes, mais junto à água; afinadas para distância ≥78 após ver que o vale parecia faixa de floresta). **Acácia Monumental** (176 × 264 studs) isolada no morro (−470, 3.960).
**Exploração:** 14 trilhas A* sobre a altura (`PlaniciesTrilhas`, `_PlaniciesTrilhasJ`; 7 principais, 6 secundárias, 1 subida ao mirante), travessias só em vaus (prof. ≤2,6; 0 trechos fundos), declive máx. 0,33; 13.700 colunas pintadas; trecho de **Caminho Antigo** com pedras cobertas (P2→P6). Entradas: E1 ligada à trilha "Costa Norte" da Floresta (1.656, 1.944) por trilha pintada; E2 pela costa das Montanhas (−1.450, 1.180); E3 (−150, 1.760) fica atrás de um canal de mar da floresta (não é ligação a pé).
**Pontos de interesse (`Planicies_Douradas/Pontos_Interesse`):** Acácia Monumental; Rochedo do Horizonte (formação rochosa de terreno, ~45 acima da colina) + 7 afloramentos menores; Mirante das Colinas; Lago Espelho; Grande Campina; Ruína Coberta P6 (3 peças reutilizadas do Núcleo, semienterradas); Caminho Antigo.
**Habitats (marcadores, sem IA):** Leão Solar 41 (4 territórios, emboscadas no capim alto junto a rotas, descanso à sombra de acácias, 8 mirantes de caça, 4 ninhos inativos); Búfalo Colossal 28 (3 territórios de manada, 16 pastagens planas, 5 campos de carga longos sem obstáculo, 4 ninhos inativos); 20 bebedouros/vaus compartilhados; 8 clareiras de confronto (P7 r 260); fauna provisória do RPG_01 só como 6 pontos de bando marcados PROVISÓRIO.
**Clima/música (`Ambiente_Biomas`, backup `Proto_Restore/Ambiente_Biomas_V7_pre_planicies`):** 4º perfil D (tarde ensolarada 15,1, céu aberto, névoa leve 0,27, haze 0,9, nuvens 0,52, água azul-esverdeada clara), mistura gradual pela faixa z 2.250→2.750 da costa; os 3 perfis antigos intactos (testado: floresta 0,31/14,4, pântano 0,60/13,4). Música só do bioma dominante: `Musica_Planicies` (Golden Bridge at Dusk, Windy Path, A Fresh Start (Harp), Rippling River — Creator Store gratuitas, escolhidas sem audição) + `Ambiente_Planicies` (vento no campo, pássaros, água). 7/7 carregaram e tocaram. `Montanhas_Neblina` limitado a z<2.000 para não cobrir a planície.
**Bug corrigido:** mais 45 paredes invisíveis `Limites_Floresta` na costa sul (agora divisa com as Planícies) bloqueavam a passagem → `Retirados_Planicies/Limites_Costura_Floresta_Planicies`. 1.732+357 colunas vazias entre a terra nova e o mar antigo preenchidas com mar; água exposta 0 nos blocos internos.
**Testes (Play/PC no Studio):** console sem erros do projeto; pathfinding 66/66 trechos das 14 trilhas; caminhada real: subida ao mirante 23/23, E2→P3 14/14, floresta→planícies 5/5, costa oeste→E2 3/3, vau do Rio Dourado 2/2; **FPS 58** no Mar de Capim (1.373 tufos ativos) e 58 no Vale; memória do cliente no Studio ~17 GB (lugar inteiro, não representativo). **Não testado:** celular, FPS real fora do Studio, audição da música, cachoeira montanha→rio.
**Pendências reais (atualizadas no M4.1 abaixo):** (1) Ctrl+S + backup `.rbxl`; (2) seed heads da malha IA de capim são simples (geometria baixa) — trocar por malha melhor se quiser mais realismo de perto; (3) água ambiente (`Agua_Rio`) toca em volume baixo em todo o bioma, não só perto da água; (4) ligação a pé pela entrada E3 inexistente (canal de mar); (5) celular.

## M4.1 — REFINAMENTO VISUAL DAS PLANÍCIES DOURADAS (2026-10-23, "OPERAÇÃO M4.1", a partir de 5 capturas do usuário)
**Segurança:** Studio em Edit. **Não consegui salvar o place nem gerar `.rbxl`** (sem acesso a Ctrl+S/arquivo pela integração; o último backup em disco continua `pre-M3-pantano`, e o M4 ainda não foi salvo). Cópia interna reversível em `ServerStorage/Proto_Restore/Backup_Planicies_M4`: 42 regiões de terreno (`Terrain:CopyRegion`, blocos de 1.024², x −4.096…2.688, z 1.152…6.784, y −40…200), geradores, `Planicies_Capim` antigo, `Planicies_Assets` antigo e as 289 árvores originais. T3 histórica intocada.
**Capim refeito (prioridade 1):** as 2 malhas IA (folhas triangulares grossas) foram retiradas (`Retirados_Planicies`). Novo conjunto `ReplicatedStorage/Planicies_Assets/Grama_Fina`: 6 formas de pacote PBR de lâminas finas com transparência (Creator Store "grass meshes (pbr, for brushtool)" de 4w4qz, 0 scripts) × 4 tons (Palha, Dourado, Oliva, Verde) = 24 modelos; forma 1 (lâminas mais largas) só em solo úmido. `Planicies_Capim` V2: altura alvo em studs — campo comum 1,5–2,8, manchas de capim alto por ruído 3,4–4,5 (personagem ≈5; medido em Play: mediana 2,3, p90 3,7, máx 4,5), largura variável, leve inclinação por tufo, tom escolhido por zonas de ruído grandes (não aleatório por tufo), flores só em manchas (P5 e margens). Grade 2,4 studs até 75 (nível 3) + anel distante de 7 studs até 160; pool fixo (2.400 + 600 no nível 3, menos em tiers baixos e se o FPS cair). Sem colisão/consulta → não bloqueia personagem, câmera nem criaturas.
**Solo (não deserto):** módulo `PlaniciesRefino` reescreveu só a superfície (umidade/delta em grade de 16 interpolada): campos secos = LeafyGrass (capim dourado com material próprio, cor ajustada 198,190,142), manchas verdes irregulares de Grass (ruído fbm), Grass contínua perto da água, terra seca (Ground) em pequenas manchas, **bancos de cascalho/terra** (Slate/Ground) só na beira d'água rasa. Trilhas, rochas, água e costura com a floresta preservadas.
**Relevo:** delta aditivo ondulado (fbm 300 + elevações assimétricas + ruído 110), amplitude menor na Grande Campina e nas colinas/rochedo, zero na costura com a floresta (120–360 do litoral), na água/margens, na ruína, no Rochedo, no mirante e na Acácia Monumental. 1,2 milhão de colunas. Depois: 236 árvores e 63 marcadores reassentados; 4.722 voxels de água exposta corrigidos (bordas); nível d'água dos rios conferido (8).
**Rios:** traçado sinuoso e larguras do M4 mantidos (não reescrevi a hidrografia para não quebrar a rede); margens agora com faixa verde contínua, cascalho/terra nas prainhas rasas e transição seco→úmido pelo solo. Pendente se quiser mais: novos meandros/ilhas.
**Árvores:** 92 retiradas das áreas secas em "clareiras" de ruído e do centro da Grande Campina (r 420); demais com escala ±12% e inclinação até 3,5°; +18 ribeirinhas em bosquetes irregulares de 2–5 junto aos rios; **3 novas acácias monumentais isoladas** (1.747, 2.893), (−2.896, 4.709), (1.922, 4.382) + a original = 5 marcos (a 4ª posição planejada não coube). Total 211 árvores + 5 monumentais (era 289 + 1). Verificação de base: 216 conferidas, 4 baixadas.
**Atmosfera:** perfil D refeito em `Ambiente_Biomas` (backup `Ambiente_Biomas_V8_M4`): densidade 0,27→0,19, haze 0,9→0,55, offset 0,1→0,04, cor da atmosfera neutra/quente (sem azul), clock 14,6, nuvens 0,46. Testado em Play: Floresta 0,31/14,4 e Pântano 0,60/13,4 inalterados. (No Edit o clima não roda — capturas aéreas do Edit mostram a névoa global padrão.)
**Vento:** no mesmo LocalScript, cada tufo gira a partir da base no eixo perpendicular ao `GlobalWind`: onda longa (λ≈42·2π) + onda curta + tremor com fase própria por tufo + rajada lenta; flexibilidade maior no capim alto; tudo num único `BulkMoveTo` a cada 0,04 s. Medido em Play: 40 tufos giraram em média 1,6° em 0,8 s (mín 0,02, máx 3,8 → não sincronizados). Copas das árvores: vento existente (`Floresta_Vento`).
**Testes (Play/PC no Studio):** grama vs personagem (máx 4,5 < 5); caminhada no campo 4/4 e na margem 3/3; pathfinding 66/66; mirante e rio capturados; console sem erros do projeto; **FPS 57–58** com 1.724 tufos ativos; memória do cliente no Studio ~17 GB (lugar inteiro, não representativo). **Não testado:** celular; câmera atravessando grama (não há colisão, então nada bloqueia — mas lâminas podem passar na frente da câmera rente ao chão).
**Pendências:** salvar + backup `.rbxl` (usuário); cachoeira montanha→Rio Dourado; meandros/ilhas extras se desejado; audição das músicas; celular.

## M4.2 — ÁGUA SOLTA, DIVISÕES, AFLUENTES 3× LARGOS / 4× FUNDOS (2026-10-23, 5 prints do usuário)
**Causas encontradas:** (1) "água no meio da terra": o relevo do M4/M4.1 deixava terra abaixo do nível 8 fora dos rios → o escritor enchia de água (poças com bordas em degrau) e o delta negativo do M4.1 rebaixava margens deixando água "suspensa". (2) "Divisões" (cristas de arenito perpendiculares à costa, foto 3): a rampa do gerador usava a linha de costa medida coluna a coluna (`_CostaSulMundo`), que é dentada (saltos de até 300 studs onde há um braço de mar entre floresta e planície, x −450…700) → cada coluna começava a rampa num ponto diferente.
**Correções no gerador (`PlaniciesGen`, versão anterior em `Backup_Planicies_M4/PlaniciesGen_M41`):** ondulação do relevo integrada ao gerador (não mais passe aditivo), com atenuação junto à água (canal até w+150, lagos), à costa externa e aos marcos; **piso mínimo da terra = nível d'água + 1,6** fora de canais/lagos (sem poças soltas: verificação de conectividade no gerador → 0 corpos d'água isolados além de 2 pontos minúsculos na costa); linha de costa suavizada `M.costaS` (média móvel ±128 + puxada para o lado sul) usada na rampa e no relevo; materiais (manchas verdes, terra seca pequena, sem manchas marrons nas margens). Afluentes: **Ribeirão da Aurora e Riacho do Capim meia-largura 21→45 (antes 7→15), profundidade 48 (antes 12); Riacho das Flores 18→33 / 40 (antes 6→11 / 10)**, vales maiores, nascente com largura/profundidade crescendo nos primeiros 12%; vaus alargados (r 55–70). Escritor com base em y −64 (leito de 48 cabe).
**Aplicado:** terreno inteiro reescrito (2.332 blocos) + faixa da costa norte reescrita com a costa suavizada (689 blocos); rochedo e afloramentos refeitos; nascentes arredondadas (Ribeirão/Capim; Rio Dourado começa no pé do morro); suavização térmica (degrau máx. 5) em 24 blocos onde a varredura achou degraus >7 (2.210 colunas); trilhas recalculadas por A* sobre o relevo novo (14 rotas, 0 trechos em água >3,2, `_PlaniciesTrilhasJ` atualizado) e repintadas (12.140 + 3.464 colunas), caminho antigo refeito; **mar aberto estendido** a leste, oeste e sul (983.828 colunas) — antes o mar terminava numa parede d'água a ~130 studs da praia leste. Árvores: 15 que caíram na água, 3 na trilha e 1 em encosta para a reserva; 193 + 5 monumentais reassentadas; marcadores e ruína reassentados.
**Medição dos afluentes (terreno real):** largura média 72 / 62 / 48 e leito no centro 44 / 41 / 33 (Ribeirão / Capim / Flores) — antes ~24 de largura e ~11 de profundidade.
**Varredura final (1.852 blocos):** água exposta (água vizinha de ar) 0 no interior; degraus >7 dentro das Planícies só no Rochedo do Horizonte (intencional); os demais listados são penhascos das Montanhas/Floresta fora do bioma.
**Testes (Play/PC):** console sem erros do projeto; pathfinding 67/68 (a falha é só alcance em trecho longo de P0-P6; todos os subtrechos de 40 passam); vau do Ribeirão a pé 4/4; floresta→planícies 4/4; FPS 57; memória ~11,4 GB no Studio. Capturas `SCREENSHOTS/M4_2_Agua_Divisas_Rios` (5). **Ainda sem salvar/backup** (usuário).

## M4.3 — VEGETAÇÃO À DISTÂNCIA (POP-IN) E POLIMENTO DAS PLANÍCIES (2026-10-23)
**Causas reais (inspeção em Play):** (1) capim 3D gerado só no cliente em volta da câmera — denso até ~75 studs, anel esparso até 160 com corte em ordem de grade (sumia de um lado), nada além disso; (2) `StreamingEnabled=true` com modelos em `ModelStreamingMode.Default` → no cliente, árvores além de ~1.000–1.500 studs ficavam sem peças (0/~180 completas ao longe) e "nasciam" ao se aproximar; (3) o terreno do cliente só carrega até ~1.200 studs; além disso o Roblox desenha um proxy de baixo detalhe (horizonte cinza/marrom). `StreamingTargetRadius`/`StreamingMinRadius` não são acessíveis pela integração ("not a valid member") — só pelo painel Properties. Decoração do terreno é do motor (não scriptável).
**Correções:** 198 modelos das Planícies (193 árvores + monumentais/POIs, 579 peças) em `ModelStreamingMode.Persistent` → 193/193 completas no cliente. `Planicies_Capim` V3 em 3 camadas (perto: célula 2,4, raio 45–90, vento; médio: célula 7, raio 130–230, tufos maiores, vento 0,7; longe: célula 13, raio 300–600, touceiras 4,2–6,4 sem vento), candidatos ordenados por distância antes do limite, uma camada por tick de 0,25 s, salvaguarda de FPS só após 20 s com fps<30 e piso mínimo; margens úmidas (Grass abaixo de y 10,6) com capim mais verde/denso.
**Polimento:** transição pontilhada Grass↔LeafyGrass em 45.681 colunas (sem bordas retas); atmosfera D mais quente e menos turva (Density 0,17, Haze 0,4, cor 236,222,194 / decay 214,174,108); LeafyGrass (204,188,128). Identidade mantida (savana aberta com rios/oásis; sem árvores novas).
**Testes (Play/PC no Studio):** árvores 193/193 completas no cliente; tufos por faixa (0–100: 2.605; 100: 703; 200: 182; 300: 318; 400: 573); corrida de câmera a 80 studs/s sempre 1.043–1.719 tufos <60 studs (sem buraco); FPS 54–56; memória ~10,8 GB (lugar inteiro, Studio); console sem erros do projeto. Capturas antes/depois em `SCREENSHOTS/M4_3_Distancia_Vegetacao` (4). **Não testado:** celular. **Limite:** terreno além de ~1.200 studs segue como proxy do motor — subir `Workspace.StreamingTargetRadius` (ex. 2048) manualmente, com custo de memória. **Place não salvo pela integração** (usuário: Ctrl+S + backup `.rbxl`).

## M4.4 — HABITATS DE BÚFALOS E LEÕES NAS PLANÍCIES (2026-10-23, "OPERAÇÃO M4.2 + M5" parte A)
**Regras oficiais (RPG_02):** Búfalo Colossal 14–18 studs até os ombros, carga quase em linha reta, fraco em curvas/voadores; Leão Solar 10–13 studs, ataques explosivos com alto gasto de energia (sem perseguição longa); ninhos raros, reaparecem em 30–60 min (OFICIAL).
**Feito:** marcadores antigos do M4 (`Leao_Solar`, `Bufalo_Colossal`, `Bebedouros`) movidos para `Proto_Restore/Retirados_Planicies_Habitats_M4`. Nova rede em `Planicies_Douradas/Habitats/Ecologia_Fauna` (240 marcadores invisíveis, sem colisão/consulta), calculada sobre o terreno real:
- **Búfalo Colossal — 4 manadas:** H1 Mar de Capim (1250,3750) r600; H2 Águas Claras (−1400,3750) r480; H3 Grande Campina (−250,5050) r560; H4 Terras das Flores (−2750,5150) r480. Cada uma: 5 pastagens (planas, sem árvore a 35, longe de trilha 45), 2 descansos elevados, zona de filhotes central (sem árvore a 60), 2–3 pontos d'água em margem suave (água real verificada), rotas até a água (A* com custo de declive/árvores, rio só em vau), 2–3 rotas de fuga retas (razão ≤1,4), 2 campos de carga planos de 180 studs; 5 corredores entre manadas (atravessam rios só nos vaus).
- **Leão Solar — 4 bandos:** L1 Colinas do Horizonte (−2450,3350); L2 Bosques Solitários (1250,5150); L3 Capim Alto Leste (1900,4400); L4 Campina das Flores (−1650,5550). Cada um: mirantes em colinas com linha de visada verificada até pastagens, descanso à sombra de árvores reais (lado oposto ao sol), zonas de caça nas pastagens/pontos d'água das presas, emboscadas a 50–80 studs com cobertura, rotas de aproximação (A* preferindo cobertura) e caminhos até as presas.
- **Interações (cenas para IA futura):** pastando 20, rebanho ao rio 10, perseguição 9, defesa coletiva 4, leão observa 5, caça na água 8, encontro com jogador 8 (ponto de trilha com visada para a manada).
- API `ServerStorage/Ecologia/EcologiaFauna` (porId, lista, rota) — serve também a Tundra. Esquema em `DOCS/ECOLOGIA-FAUNA.md`.
**Testes:** pathfinding com agente grande (raio 5, altura 18) 79/79 (rotas d'água, fuga, aproximação, corredores em trechos); caminhada real 6/6; 0 marcadores sobre trilhas; 0 ids duplicados; árvores 193/193 no cliente (vegetação continua carregando). Nada de IA/animais/combate implementado. Captura `SCREENSHOTS/M4_4_Habitats_Planicies` (visual de depuração temporário, já removido).

## M5 — TUNDRA CONGELADA (5º bioma) (2026-10-23, "OPERAÇÃO M4.2 + M5" parte B)
**Posição:** ao NORTE da Floresta/Pântano (era vazio), coerente com o macrozoneamento oficial (Tundra a nordeste, além das Montanhas). Máscara de terra: superelipse C(1300,−4750) RX 3650 RZ 2350 → terra ≈ x −2300…4900, z −2350…−7050; caixa escrita x −3400…6440, z −8200…−1400 (inclui mar ao redor). Leste (Costas) e sul/sudeste (Deserto/Terras Corrompidas) continuam livres para os biomas 6–8.
**Ligações por terra (sem teleporte):** istmo da ponta norte da Floresta (x≈1350–1950) e istmo da costa nordeste das Montanhas (x −1800…−950). Únicas alterações em outros biomas: faixa de mar raso desses dois istmos virou terra (cópias em `Proto_Restore/Backup_Tundra_M5`), suavização só de colunas de terra no istmo das Montanhas, e 9 paredes invisíveis `Limites_Floresta` que bloqueavam o istmo movidas para `Proto_Restore/Retirados_Tundra/Limites_Floresta_Istmo_Tundra`. Vazios (baía/entalhe) junto à Floresta/Pântano preenchidos com mar. Ilhas flutuantes das Montanhas que caem sobre a área foram preservadas.
**Geradores (Proto_Restore):** `TundraGen` (relevo/água/gelo/materiais), `TundraWriter` (blocos 128; protege colunas de outros biomas pela varredura pré-Tundra `Dados_Montagem/TundraCampoExistente`), `TundraCavernas`. Trilhas: `Dados_Montagem/_TundraTrilhasJ`.
**Regiões (T0–T7):** T0 Fronteira do Inverno (1200,−2650) transição grama→neve pontilhada; T1 Campos da Neve Silenciosa (2900,−3650) ondulações, morenas, depressões abrigadas; T2 Floresta das Coníferas Brancas (−250,−3750) vale abrigado com clareiras; T3 Lago do Espelho Congelado (1400,−4800); T4 Desfiladeiro Glacial (canion 3150,−4500 → 2980,−6250, paredes em faixas de rocha/gelo); T5 Cavernas de Gelo (maciço oeste); T6 Planalto dos Ventos (3800,−5450, topo ~262, escarpas, rampa ao sul); T7 Coração Glacial (vale em U com glaciar, frente de gelo ~40 studs, seracs). 13 picos nomeados (até ~820).
**Hidrografia (nível único 8):** lago ~1300×860, prof. 37, 79% coberto de gelo (água aberta na saída, fozes e fendas), 3 ilhas; Rio do Degelo 2.942 studs, 40→72 de largura, 16–22 de profundidade, placas de gelo nas margens + trechos inteiros congelados, 2 vaus, foz no mar a leste da Floresta (3330,−2150); 4 riachos de degelo congelados (gelo rente às margens). Navegabilidade de montarias aquáticas PENDENTE de teste.
**Materiais:** Snow/Salt(neve compactada)/Glacier/Ice só existem na Tundra (cores ajustadas: Snow 240,244,248; Ice 156,196,224; Glacier 170,208,232; Salt 226,232,238). Rocha só em penhascos/alto; margens de cascalho cinza (Slate); **neve espessa (24) sob a superfície** — terra/rocha rasa aparecia como manchas escuras no LOD distante.
**Vegetação:** 2.470 árvores em 187 clusters `Persistent` (Pinheiro Boreal nevado/verde PBR, Abeto Geado, Pinheiro Jovem, Bétula Branca com folhas em T0 e nua no frio, árvores mortas), sem árvores em gelo/água/trilhas; vento via `Floresta_Vento` (Bioma="Tundra", mais forte no alto). Rasteira no cliente `Tundra_Rasteira` (gramíneas secas + arbustos de frio, pool 900). Bibliotecas: `ServerStorage/Tundra_Lib`, `ReplicatedStorage/Tundra_Assets`; fontes em `ServerStorage/Sandbox_Arvores_Tundra` (scripts de vento de um pacote removidos).
**Exploração:** 15 trilhas (neve compactada, terra só em pontos; R02/R07 cruzam o rio em vau/gelo), 7 mirantes, 6 áreas de combate planas (180–400), cavernas: **Gruta do Gelo Azul** (entrada leste (−790,−5082), Salão das Colunas 156×58×116 com pilares, Salão da Luz com poço de luz natural, passagem alternativa, saída leste (−765,−5395), galeria norte sem saída) e **Caverna do Coração Glacial** (portal (330,−5930) → Salão Congelado dentro do glaciar). Reservas sem estrutura: `Reserva_Santuario_Sob_o_Gelo` (RPG_01: santuário sob gelo instável/Edria) e `Reserva_Vila_da_Tundra`.
**Ecologia (RPG_02: Lobo Ártico 5,5–7 e Dragão Glacial 18–24):** `Tundra_Congelada/Habitats/Ecologia_Fauna` — Lobo Ártico 3 territórios (campos, floresta, planalto) com covis, descanso, zonas de caça, rotas de patrulha; Dragão Glacial 3 territórios (Coração Glacial, lago, planalto) com 8 poleiros, 3 ninhos elegíveis (Ativo=false, 30–60 min), zonas de ataque em campo aberto/gelo, 3 pontos d'água; fauna provisória (RPG_01) lebre/cabra/mariposa marcada PROVISORIO; 26 cenas de interação. Tamanho de grupo dos lobos: PENDENTE (documento não define). Túneis não comportam dragão adulto (oficial: porte dificulta espaços fechados).
**Clima/som:** `Ambiente_Biomas` com perfil Tundra (luz fria levemente azulada, névoa leve 0,24 nos campos), sub-perfis Planalto (0,36 + vento) e Coração Glacial (0,42, azul), caverna (ambiente mínimo jogável); fator Tundra pela forma da região (transição gradual com Floresta/Montanhas). `Tundra_Clima`: flocos em episódios (~40% do tempo), neve carregada pelo vento no planalto, nada em cavernas. Música Tundra 5 faixas (APM/DistroKid licenciadas), vento/ar frio, água de degelo perto do rio, estalos de gelo ocasionais perto do lago/rio (ProSoundEffects). Backups: `Proto_Restore/Ambiente_Biomas_pre_Tundra_M5`, `Floresta_Vento_pre_Tundra_M5`.
**Correções feitas durante os testes:** manchas escuras ao longe (neve fina → neve espessa), picos com "agulhas" (picos nomeados + união suave), terreno flutuante de passes anteriores (337+18 blocos reescritos limpando até o topo), "pente" na base das paredes do T7 e degrau de 88 studs (mistura contínua), riacho em escada (calha rasa, gelo domina a célula), cavernas (pilares fechando túneis, salões com piso curvo, saída sob montanha → saída leste), material inválido Pebble (virava grama), istmo das Montanhas irregular.
**Testes (Play/PC no Studio):** pathfinding 87/87 trechos nas 15 trilhas; caminhadas reais: Gruta completa, passagem alternativa, galeria norte, Glaciar portal→salão, istmo Floresta→Tundra, istmo Montanhas↔Tundra (ida e volta) — todas OK; árvores 2.470/2.470 completas no cliente (1.877 a >1.500 studs); FPS 57–59; memória ~11,3 GB (lugar inteiro no Studio); clima medido por sub-região; música Tundra tocando; console sem erros do projeto; 4 biomas: contagem de objetos igual (Floresta −9 paredes, intencional) e terreno igual exceto vazio/pontes. Capturas `SCREENSHOTS/M5_Tundra_Congelada` (10). **Não testado:** celular; audição humana das músicas; montarias aquáticas.
**Limitações:** paredes d'água nas bordas da caixa de mar (x 6440, z −8200, x −3400; ≥1.100 studs da costa); paredes do vale T7 e do desfiladeiro são penhascos íngremes (sem escalada); cavernas escuras porém jogáveis; arbustos de frio um pouco verdes; terreno além de ~1.200 studs depende de `StreamingTargetRadius`. **Place não salvo pela integração** (usuário: Ctrl+S + backup `.rbxl`).

## M5.1 — TUNDRA: CORREÇÕES, CAVERNAS DE LOBOS/DRAGÕES, NEVASCA (2026-10-23, "ATUALIZAÇÃO OFICIAL M5")
**Pedido:** terra no meio do rio, árvores enterradas/flutuando, mais árvores em áreas vazias, névoa mais branca (de fora e de dentro), tempestade de neve forte com vento e som; atualização oficial: campos abertos sem pedras aleatórias, tocas de Lobos Glaciais baixas e acessíveis a pé, covis de dragão altos em penhascos com plataforma de pouso/decolagem, ecologia por altitude, espaços de combate.
**Conflito registrado:** o texto colado pede "evitar tempestade constante e névoa excessiva"; o texto digitado pelo usuário pede tempestade forte e névoa branca. Seguido o pedido digitado, com intensidade oscilante (0,25–1, ciclo ~8 min) para manter a exploração legível.
**Árvores:** pivôs da `Tundra_Lib` estavam no meio da altura (árvores meio enterradas) e bétulas/espruce morto deitados. Corrigido: `PrimaryPart` removida (com ela, `WorldPivot` é ignorado e `PivotTo` desfaz a rotação), peças rotacionadas, pivô na base do tronco. 2.470 árvores recolocadas (0 flutuando, 0 enterradas). +104 árvores em 12 bosques nas áreas vazias (6 no planalto, 5 no T7, 1 no T1) → 2.572 no total, todas `Persistent`.
**Terra no meio do rio:** era a borda antiga de terra (y ≤ 8,8) que encostava no vazio anterior, agora sob o mar novo. 883 colunas de faixa estreita rebaixadas para leito (Slate −4, água 0–8). Cópias em `Backup_Tundra_M5/Antes_Faixas_Submersas` (34 regiões).
**Paisagem aberta:** nenhuma pedra/tronco/objeto avulso foi adicionado; campos T0/T1 continuam abertos.
**Tocas de Lobos (baixa altitude, a pé):** `Toca_Lobos_Cume_Sul` (entrada (−1290,93,−3900), 16×12, 2 câmaras: descanso e filhotes) e `Toca_Lobos_Desfiladeiro` (entrada (3190,86,−5028) na parede do cânion, 14×12, 2 câmaras); a Gruta do Gelo Azul serve à 3ª alcateia. Trilhas de acesso novas em `_TundraTrilhasJ` (R_TOCA_*).
**Covis de Dragão Glacial (alto, remotos):** `Covil_Dragao_Coracao` (câmara (901,335,−6607) 80×62×70, túnel raio 34 → vão livre 44), `Covil_Dragao_Agulha` (câmara (2729,420,−6576) 75×65×75, entrada aberta ~100), `Covil_Dragao_Vigia` (câmara (−1733,375,−5616) 60×60×55, entrada ~100). Túnel curto e largo, ninho natural (`LocalNinhoElegivel` Ativo=false), descanso, plataforma de pouso/decolagem com espaço aéreo livre à frente. **Dimensões do dragão PROVISÓRIAS** (comprimento ~70, envergadura ~100 — os documentos oficiais dão só 18–24 de altura); revisar quando houver porte oficial. Plataforma final: terraço de neve sobre **contraforte de rocha que desce até o chão real de cada coluna** (sem laje pendurada); espaço livre acima em cúpula com parede de trás em rampa. As duas versões anteriores (disco artificial; laje fina) foram descartadas — a caixa antiga de backup `Antes_*` não cobria a área abaixo da plataforma, então os 33 blocos (128) ao redor dos 3 covis foram **regenerados pelo `TundraWriter`** e as cavernas reescavadas (varredura: 0 superfícies soltas abaixo das plataformas).
**Ecologia por altitude:** `Ecologia_Fauna` refeita — Lobo Ártico só embaixo (Alcateia_Floresta→toca Cume_Sul, Alcateia_Macico→Gruta, Alcateia_Campos→toca Desfiladeiro; cada uma com Toca, Zonas_Caca, Rotas_Patrulha, Arena_Toca); Dragão Glacial só no alto (Coração_Glacial, Agulha_Azul, Vigia_Branco com Covil: Plataforma_Pouso `DecolagemLivre=true`, Entrada, Câmara, Ninho, Descanso; Poleiros acima de 250; Zonas_Ataque; Areas_Caca_e_Agua). 6 tipos de cena em `Interacoes_Ecologicas`. Versão antiga em `Retirados_Tundra/Ecologia_Tundra_M5_v1`.
**Nevasca e névoa:** perfil Tundra branco (Density 0,33 + 0,12×tempestade, Haze 2,0 + 0,8×tempestade, cor 236,240,246), fora de cavernas. `Tundra_Clima` reescrito: Flocos (140–600/s), Flocos_Perto (junto à câmera), Rajadas_Neve (fumaça) e Neve_Carregada no chão, vento forte (35–105) na direção (1,0,0,55). Som `Nevasca_Uivo` ("Howling Wind", DistroKid, licenciado) acompanha a tempestade; vento mais alto. **Véu visto de fora:** novo `Tundra_Veu` (cliente) — 26 bancos de névoa em 2 camadas ao longo da borda mais próxima quando a câmera está fora da Tundra a até 3.200 studs; cor levemente azulada porque a correção de cor quente da Floresta deixa branco puro creme (não alterada para não mexer no bioma).
**Testes (Play/PC no Studio):** caminhada real dentro e fora das 2 tocas; caminho plataforma→câmara nos 3 covis (pathfinding Success 23/24/15 waypoints após a regeneração); vãos medidos (tocas 16×12 e 14×12; covis 44 / ~100 / ~100); espaço de decolagem livre à frente das 3 plataformas; trilhas das tocas 6/6 e 3/3; FPS 57–58 sob nevasca em 4 pontos (lago, campos, Floresta olhando a Tundra, covil Agulha); 2.572/2.572 árvores carregadas no cliente; 4 biomas vs baseline: contagem de objetos igual (Floresta −9 paredes, já registrado) e, na grade de 3.430 pontos, só 8 pontos de terra pré-existente mudaram — todos transições intencionais (istmo das Montanhas e a faixa de grama no nível da água em x 3600 pedida pelo usuário). Capturas `SCREENSHOTS/M5_1_Tundra_Cavernas_Nevasca` (12).
**Limitações/pendências:** pequena borda dentada na base da parede do túnel do covil Vigia (detalhe visual); névoa vista da Floresta fica creme sob a luz quente da Floresta; celular não testado (nevasca usa partículas — medir em aparelho); som não ouvido por humano; place **não salvo** pela integração.
**M5.1b (mesmo dia, retorno do usuário: "ainda dá para ver tudo por fora" + "bloco flutuando"):** `Tundra_Veu` reescrito — cortina opaca de 54 bancos em 3 camadas (140/480/900 studs para dentro da borda, a última alta para cobrir os picos), altura de cada banco seguindo o terreno (tabela pré-calculada de 160 pontos de borda), transparência 0,10–0,18. O "bloco branco" era, com alta probabilidade, partícula grande do véu antigo cortando o chão perto do jogador na borda (fixa em y 80/200): agora bancos a menos de ~380 studs + meio tamanho da partícula da câmera são desligados e limpos, e tudo é limpo ao entrar na Tundra (q<1,02). Varredura de terreno solto na Tundra (raycast duplo a cada 8 studs): 2 colunas de neve, ambas na crosta do istmo das Montanhas (terreno original) — nenhum bloco de neve flutuando. Teste Play: do litoral do Pântano e da Floresta o interior da Tundra fica escondido atrás da névoa (cor creme por causa da luz quente desses biomas, não alterada); no istmo os bancos próximos desligam (sem cortes). Versão anterior em `Proto_Restore/Tundra_Veu_M5_1_v1`. Capturas 13–14 em `SCREENSHOTS/M5_1_Tundra_Cavernas_Nevasca`.
**Mapa-resumo:** `SCREENSHOTS/Mapa_Resumo_Mundo.png` (varredura do terreno a cada 24 studs + árvores + estruturas sobre a água + trilhas/vaus/cavernas/tocas/covis/vilas). Passagens por terra medidas (linhas contínuas de terra atravessando a divisa): Floresta↔Pântano z −260…240 (e −500…−460, 340…520); Floresta↔Montanhas z −1220…420; Floresta↔Planícies x 1520…1820 e −800…−60; Montanhas↔Planícies x −1060…−540 e −1640…−1400; Tundra pelos 2 istmos.
## M5.2 — ÁGUA, NÉVOA, MARGENS E IMERSÃO SUBAQUÁTICA (2026-10-23)
**Pedido:** erros de terra/água "no meio do nada", névoa fraca dentro da Tundra e Tundra ainda visível de fora, vegetação só aparecendo de perto, névoa baixa + tempestade baixa nas cavernas; prompt colado "rede de rios/águas + imersão subaquática" (sem novo bioma) e "árvores nas margens".
**Terra/água errada (varredura de todo o mundo, grade 8 studs):** 37 sulcos de água fina na costura Planícies↔Floresta/Montanhas preenchidos com o chão vizinho (1.354 colunas, ex. o canal reto da 1ª imagem do usuário); 21 ilhotas baixas de terra no mar (costa norte/leste da Floresta, incl. o triângulo com bordas retas) rebaixadas a leito; 685 células com "buraco" na água (superfície abaixo do nível 8) preenchidas; leito do mar em quadrados (costa norte e leste da Floresta) suavizado (39.692 colunas). Cópias em `Proto_Restore/Backup_M5_2_Agua`. As faixas brancas "de areia" na margem sul são grama (raycast) — não alteradas.
**Névoa Tundra:** perfil T Dens 0,33→0,46, Haze 2,0→2,6; planalto/coração 0,52–0,54; tempestade +0,16 / +1,0. **Véu de fora:** 4ª camada sobre o mar em frente à costa (era o que deixava ver a margem), 88 bancos, opacidade 0,05–0,12 → do litoral da Floresta só se vê a orla mais próxima. **Cavernas:** névoa baixa (Dens 0,3, Haze 1,0) e tempestade baixa (flocos perto da câmera 14–36/s + neve rasteira fraca) em vez de nada.
**Vegetação à distância:** 8.710 árvores da Floresta/Montanhas/Pântano passaram a `ModelStreamingMode.Persistent` (atributo `StreamingAntes` guarda o modo anterior; Planícies e Tundra já eram); rasteira da Tundra 70→110 studs. Custo: FPS 57 na costa, 50 no centro da Floresta, 43 na Tundra com nevasca (antes 57–58) — **medir no celular antes de publicar**; reverter é trocar o modo de volta pelo atributo.
**Rios da Tundra (`TundraGen.RIOS`, 285 blocos regenerados, cópias em `Backup_M5_2_Rios`):** Rio do Degelo alargado (64–108 de largura, profundidade mediana 22, 26% da superfície congelada em trechos alternados); **novo Rio do Pinheiral** lago→mar sul pelo vale T2 (2.587 studs, 68–96 de largura, mediana 26, 54% congelado); **novo Rio do Desfiladeiro** saída do cânion→Degelo (804 studs, 64–80, 24). Vaus rasos (prof. 3) onde as 7 trilhas cruzam. Marcadores: `Hidrografia` (rios/vaus novos, atributo M5_2) e `Ecologia_Fauna/Rotas_Aquaticas` (3 rotas contínuas com largura/profundidade/trechos congelados, `Status=AGUARDANDO_ESPECIES_AQUATICAS`, + 6 poços fundos). Nenhuma espécie aquática criada (aguardam documentos oficiais).
**Visão debaixo d'água (`Ambiente_Biomas`):** no Roblox a Atmosphere e a neblina clássica não valem submerso; turbidez feita com nuvem de partículas na frente da câmera + desfoque de distância (DepthOfField) + blur leve, cor e opacidade por bioma (Tundra fria azul, Floresta verde-escura, Pântano verde turvo e denso, Planícies mais clara, Mar azul-escuro com coluna d'água) e mais forte com a profundidade; raso lê melhor. Ao sair da água o clima de superfície volta (testado). Cor/transparência da superfície da água reduzidas por bioma (fundo menos visível de fora).
**Árvores nas margens (11.484 checadas em 5 biomas):** 192 assentadas no chão novo, 71 recolocadas fora da água (15 que caíram juntas foram separadas), 24 baixadas (Pântano/Montanhas/Planícies/Floresta flutuando 1–7 studs), 0 removidas; 3 capins e 2 samambaias sobre a água retirados (`Retirados_Tundra/Plantas_sobre_agua_M5_2`). Uma primeira passada pegou pontes/ovos/rastros por engano — os 109 objetos foram devolvidos ao lugar original no mesmo minuto.
**Testes (Play/PC Studio):** submerso em rio da Tundra, Planícies, mar e Pântano (capturas); saída da água restaura clima; caverna de lobo com névoa/tempestade baixa; véu visto da costa; 0 erros do projeto no console. Capturas `SCREENSHOTS/M5_2_Agua_Nevoa_Margens` (17, com antes/depois); mapa atualizado `SCREENSHOTS/Mapa_Resumo_Mundo.png` (anterior em `Mapa_Resumo_Mundo_ANTES_M5_2.png`). **Não testado:** celular; pathfinding das trilhas que cruzam os novos vaus; nado real de personagem nos rios novos. Place **não salvo** pela integração.
## M5.2b — CANAIS FINOS, BORDAS RETAS, FUNDO DA ÁGUA E RASTEIRA À DISTÂNCIA (2026-10-23)
**Pedido:** "ainda tem" canal fino de água entre grama (Floresta↔Planícies), ainda dá para ver o fundo da água, vegetação só carrega de perto.
**Canais/bordas retas:** detecção de linhas de costa retas alinhadas aos eixos (139 trechos ≥ 80 studs) e canais estreitos; novo módulo `Proto_Restore/CostaSuave` (borra a máscara terra/água, margem irregular por ruído, fecha canais < ~30 studs, funciona em qualquer nível d'água — rios e lagos elevados da Floresta/Montanhas também) aplicado em 68 caixas fora do Pântano e do interior da Tundra (~108 mil colunas; 5.440 água→terra, 2.751 terra→água). Os 2 canais da imagem do usuário (x≈690–780, z≈1940–2010) foram fechados; parede reta e placa de gelo do estreito Montanhas↔Tundra (x −1712) viraram margem curva; listras do generator no istmo alisadas. Cópias: `Backup_M5_2b_Costas` (sub-caixas `C_x_z`). Três pontes da Floresta (PonteV7_F8, PonteV7_F10, PonteV9_T3) ficaram sobre terra e tiveram o terreno original restaurado só embaixo delas (água de volta, 5–6/7 pontos).
**Defeitos de água achados no caminho:** bolsões de ar dentro do mar (17, incl. um poço de ~85×110 a leste da Floresta), lajes sólidas submersas com água em cima e embaixo (1.993 voxels), grama/terra/neve sob a água (61.417 voxels → lama/ardósia: tirava "capim dentro da água"), faixas de chão entre y 4 e 8 junto à água (2.759 viraram água, 8.517 viraram margem acima do nível). Módulo `Proto_Restore/ReparoAgua`. **Lição:** escrever Water por cima de sólido com WriteVoxels NÃO apaga o sólido — sempre 2 passadas (ar, depois água). Uma primeira rodada destes reparos foi feita no servidor do Play (perdida ao parar) e refeita no Edit.
**Fundo da água:** turbidez em 2 camadas (perto da câmera ~16 studs e longe ~55), caixas que cobrem também olhar para baixo, opacidade maior (0,45–0,95); superfície menos transparente (Floresta 0,24, Montanhas 0,26, Planícies 0,30, Tundra 0,20, Pântano 0,14). Em 3ª pessoa no fundo do mar o chão some em ~20–30 studs e o personagem continua visível.
**Vegetação à distância:** no cliente todas as árvores/plantas da Floresta já estão presentes até 2.500 studs (medido por faixa); o que aparecia "só de perto" era a rasteira da Tundra (pool no cliente). Novo anel distante 110–320 studs (1 a cada 3×3 células, tufos 1,6× maiores): 545 perto + 501 longe, FPS 58. Limites do motor (não alteráveis por script): a grama decorativa do terreno só é desenhada perto da câmera; a distância de desenho das peças cai com a qualidade gráfica escolhida pelo jogador.
**Testes (Play/PC Studio):** canais fechados e margem natural; superfície sem laje/retângulo; submerso no mar em 3ª pessoa; rasteira até 320; FPS 58. Capturas `SCREENSHOTS/M5_2b_Canais_Agua_Rasteira` (10). **Não testado:** celular; varredura visual de todas as 68 caixas (só amostras); Pântano não foi alterado (canais lá são do design). Place **não salvo** pela integração.
## M6 — DESERTO DE CRISTAL (6º bioma) (2026-10-23, "OPERAÇÃO M6")
**Posição (validada no mapa real):** sudeste do mundo, a leste das Planícies Douradas e ao sul do Pântano Nebuloso (antes só mar). Máscara superelipse C(5600,4920) RX 2700 RZ 2520 → terra ≈ x 2.900–8.300, z 2.500–7.400; caixa escrita x 2.400–9.000, z 2.100–7.800 (com mar em volta). Ligação por terra: istmo com a costa leste das Planícies (2620,3950). Reservas mantidas: leste (x>9.000) para Costas Selvagens e sul (z>7.800) para Terras Corrompidas (marcador `Reserva_Costas_Selvagens`). Backup do usuário (Ctrl+S + `.rbxl`) feito antes da construção; cópia do mar original em `Proto_Restore/Backup_Deserto_M6`.
**Documentos lidos:** RPG_01 (macrozoneamento [PROPOSTA], POIs: oásis, lapidação, minas, instalação clandestina; árvores provisórias Acácia de Pedra/Desértica e Tamareira Cristalina; fauna provisória Raposa-do-Deserto, Abutre de Vidro, Escaravelho Prisma; 2 dungeons propostas) e RPG_02 (espécies oficiais do deserto: **Escorpião Colossal** — Veneno/Terra/Fogo, 16–24 de comprimento, emboscada na areia; **Lagarto Cristalino** — Terra/Luz/Raio, 18–26, escalada rochosa, variantes Quartzo Claro/Âmbar Dourado/Ametista Rochosa). **Nenhum dragão no deserto** (não há espécie oficial) — nenhuma caverna foi reservada a dragões.
**Geradores (Proto_Restore):** `DesertoGen` (relevo/água/materiais), `DesertoWriter` (blocos de 128, protege terra existente pela varredura `Dados_Montagem/DesertoCampoExistente`: 14.486 colunas protegidas), `DesertoCavernas` (motor das cavernas da Tundra), `DesertoCristais` (aglomerados), `DesertoPreview` (planta). Escrita completa: 2.340 blocos em ~80 s.
**Regiões:** D0 Fronteira Árida (3250,3950) capim dourado → terra → areia compactada → areia, sem linha reta; D1 Mar de Dunas (5300,3650) dunas transversais assimétricas (barlavento longo, face de avalanche curta) + família oblíqua (dunas cruzadas) + megadunas, cristas segmentadas; D2 Cânions Vermelhos (7450,4400) mesa estratificada (topo ~150) cortada pelo cânion do rio e 2 cânions secos, paredes em degraus; D3 Oásis das Águas Claras (4300,5250) lago 600×430 alimentado por água subterrânea junto ao rochedo da nascente, palmeiral; D4 Campos de Cristal (6750,5450) veios de basalto alongados com depósitos; D5 Gargantas Esquecidas (3650,6400) aletas de arenito com fendas; D6 Cavernas Cristalinas (5050,6650) no maciço sul; D7 Coração do Deserto (6080,6320) cratera de ~950 com borda rompida a noroeste, salina e cone central com o monumento cristalino. Montanhas áridas ao sul (até ~360) e inselbergs.
**Hidrografia (nível 8, igual ao resto do mundo):** Rio do Oásis (lago → oeste → mar entre Planícies e deserto, 44–64 de largura, 18–24 de profundidade); Rio dos Cânions (nascente/poço no fundo do cânion (6640,4255) → leste → mar, 48–76 de largura, 20–26); 2 leitos secos (uadis) sem água; nenhum canal atravessando o deserto inteiro. Visão subaquática com perfil próprio do deserto (água clara esverdeada, fundo some com a distância).
**Materiais:** Sand (areia), Limestone (areia compactada/sedimento claro), Sandstone (arenito), Basalt (veios do D4) — só usados no deserto; texturas geradas `Deserto_Areia_Clara` (Sand), `Deserto_Arenito_Ocre` (Sandstone), `Deserto_Areia_Compactada` (Limestone) como override; cores do terreno ajustadas (cores antigas salvas no atributo `CoresAntesDeserto` de `Proto_Restore`). Subsolo espesso do mesmo material (LOD distante). Salt NÃO usado (é a neve compactada da Tundra).
**Cristais:** 90 aglomerados (896 peças) feitos de 6 formas de cristal de um modelo da loja (sem scripts), cor por variante oficial do Lagarto Cristalino, vidro com transparência leve, sem neon: monumento D7 (cristal principal ~140 + 6 médios + 10 pequenos), 18 depósitos no D4 sobre os veios, 52 nas paredes das cavernas (com luz suave), 3 veios de âmbar nos cânions. Grandes (D7 e D4 ≥18) `Persistent` (visíveis a 1.700 studs, testado); pequenos `Atomic` (streaming normal). 0 aglomerados sem terreno na base.
**Vegetação:** 118 árvores em clusters `Persistent`: 52 Tamareiras Cristalinas (provisórias; 6 palmeiras de um pacote da loja, só as malhas, sem scripts) no oásis, margens e nascente; 41 Acácias Desérticas (provisórias, acácias das Planícies menores com copa oliva) na fronteira e nos uadis; 25 árvores secas. Rasteira no cliente `Deserto_Rasteira` (gramíneas secas, arbusto de aridez, arbusto rolante) só em solo verde/terra/oásis e muito rara na areia. 0 árvores flutuando ou na água.
**Exploração e habitats:** 6 trilhas (areia compactada pintada no terreno) — pathfinding 37/37 trechos; mirantes 6 (topo da mesa, borda da cratera, dunas, gargantas, rochedo do oásis, monte sul); 6 áreas de combate; cavernas: `Cavernas_Cristalinas` (entrada norte, Salão dos Cristais 156×52×124 com colunas, Galeria dos Geodos, saída oeste, Câmara Selada = reserva de dungeon), 2 `Toca_Escorpiao` (gargantas e cânion, câmaras ~96×26×80), `Grota_Lagarto_Cratera`. `Habitats/Ecologia_Fauna`: Escorpião Colossal 3 bandos (dunas, gargantas, cânion: território, toca/abrigo, 4 zonas de emboscada na areia, rota de patrulha, arena, ninho elegível Ativo=false), Lagarto Cristalino 3 grupos (campos de cristal, coração, cavernas: território, toca, 3 poleiros rochosos, zona de caça, arena, ninho elegível Ativo=false), 5 pontos d'água, fauna provisória (RPG_01) marcada PROVISORIO, 8 cenas. Reservas sem estrutura: vila, 2 dungeons, lapidação/minas, instalação clandestina. Nada de IA/combate/criaturas.
**Clima/som:** perfil Deserto no `Ambiente_Biomas` (sol 13h, luz quente sem saturar, poucas nuvens, névoa 0,22), transição gradual pela forma da região; cavernas com ambiente quente jogável; **tempestade de areia ocasional** (~21% do tempo, sobe/desce em ~80 s): névoa 0,62 amarelada + `Deserto_Clima` (nuvens de poeira, grãos voando, areia rente ao chão), nada em cavernas/debaixo d'água. Música Deserto 5 faixas licenciadas (Infinite Deserts, Voyage — DistroKid; Barren Land A, Discovery, Dream Walk B — APM, todas carregadas); ambiências: vento, brisa, uivo da tempestade, água no oásis/rios, eco grave nos cânions (sons licenciados já usados no jogo). `Pantano_Neblina` e `Floresta_Raios` limitados a z<2300/2400 para não vazarem no deserto.
**Testes (Play/PC no Studio):** caminhadas reais: dunas (sobe até 77 e desce), entrada da caverna → Salão dos Cristais, dunas → fundo do cânion (39 → 8); pathfinding: Planícies → istmo, todas as câmaras das cavernas, tocas, grota, borda da cratera → monumento, dunas → mesa → topo → mirante; FPS 57–58 em 6 pontos (dunas, oásis, cânion, cratera, salão dos cristais, gargantas), memória do Studio ~13,87 GB (+~0,1 GB); submerso no oásis; tempestade e tempo limpo capturados; 4 biomas + Tundra: dentro da caixa 0/10 pontos de terra antiga alterados, contagem de objetos igual. Capturas `SCREENSHOTS/M6_Deserto_de_Cristal` (13). Mapa atualizado `SCREENSHOTS/Mapa_Resumo_Mundo.png`.
**Limitações/pendências:** celular não testado; parede de arenito com textura um pouco "borrada" de perto; margens de rio com lama escura; Acácia Desértica e Tamareira Cristalina são modelos provisórios; alguns cristais de parede ficam altos no teto do salão; o place **não foi salvo pela integração** depois da construção (usuário: Ctrl+S); som não ouvido por humano.
## OPERAÇÃO M6.1 + M6.2 — REFINO DO DESERTO, FALHAS DE TERRENO E GRUTA DE GELO (2026-10-25)
> Nome dado pelo usuário às operações de bioma. **Não confundir** com as tarefas `M6.1`/`M6.2` de "Chefes e dungeons" em `TASKS.md` (não iniciadas).

**Backups (Proto_Restore):** módulos antes da mudança: `DesertoGen_M6_v1`, `DesertoCavernas_M6_v1`, `DesertoCristais_M6_v1`, `TundraCavernas_M6_v1`, `DesertoGen_M6_2_preParede`, `DesertoCavernas_M6_2_preParede`, `TundraCavernas_M6_2_preCostura`. Objetos substituídos movidos (não apagados) para `Retirados_Deserto/Cristais_M6_1_preMegadunas` e `Retirados_Deserto/Cristais_Cavernas_M6_2_preParede` (+ `v2_preColunas`). Terreno do deserto é regenerável pelos geradores determinísticos.

**Deserto — geometria (corrigida no gerador, não escondida com objetos):**
- Dunas: escala local variável, família de dunas pequenas, **megadunas** mais próximas (comprimento ~760 variável), barlavento 70% / sotavento 30%, amplitude até ~110; orientação e espaçamento variam. Áreas abertas mantidas.
- Gargantas: o paredão reto virou "barbatanas" e mesetas de alturas variadas (55–140), cortadas por ravinas e com terraços em estratos.
- Bordas da mesa com ravinas; cânions com largura de fundo/parede variável ao longo do curso e 3–5 degraus irregulares.
- Bug corrigido: reescrita com relevo menor deixava laje velha flutuando → `DesertoWriter` limpa até y 560 (`TETO_TOTAL`). Varredura após a reescrita: 0 colunas com vão fora das cavernas (inclusive 27.207 colunas dos blocos reescritos depois).
- Oásis: beira molhada (lama/terra) colada na água real → capim/grama logo atrás → solo/areia compactada → areia; sem faixa de areia seca entre água e grama. Transição Planícies → deserto por gradiente de aridez com ruído (capim → terra → areia compactada → areia).
- Cristais: monumento D7 e D4 refeitos com **base de rocha no terreno** (FillBall) — saem da rocha; D4 em veios de basalto, espaçamento ≥100; nenhum cristal a mais. 72 aglomerados verificados com terreno junto à base (0 soltos).
- Cavernas do deserto: salões com base em bacia e parede irregular em 2 escalas (sem paredão vertical liso); **colunas em ampulheta** com relevo 3D (antes eram extrusões verticais retas); estratos quase horizontais; teto em material único; cristais só no piso/parede baixa, recolocados após cada mudança.
- Bug corrigido nos dois motores de caverna (deserto e Tundra): costura reta de material a cada 64 studs (bloco de escavação não via o vizinho) — agora consulta `dentro()` fora do bloco.
- 118 árvores reassentadas (110 mudaram de altura com as megadunas, até 47 studs; 0 sobre água); 13 marcadores de habitat que tinham subido para cima das cavernas devolvidos ao piso; 15 pontos de rota e 6 trilhas atualizados.
- Tempestade: frente de poeira que **chega, atinge o pico e se afasta** (~21% do tempo); fora dela céu limpo; sem parede permanente. Gancho de teste: atributo `workspace.DES_T_OFF` (desloca o relógio no cliente; nil em jogo normal).

**M6.2 — falhas de terreno no mapa inteiro:** varredura de colunas com sólido/ar/sólido em todos os biomas: 55.700 colunas com vão (a maioria vazios fechados no subsolo da Floresta, invisíveis, e gelo de lago sobre água — legítimos); 1.558 lâminas finas classificadas; arcos/penhascos das Montanhas acima de 150 e tetos de covis mantidos (um arco conferido em captura, natural sobre trilha); abaixo de 150 fora do deserto: 349 vãos preenchidos (Ground, onde a lâmina = mediana dos vizinhos), 19 lâminas soltas removidas, 179 ignoradas. Ex.: laje das Planícies em (−3024,4712) corrigida (capturas 16/17). Costuras nas bordas de bloco de 128 (Tundra/deserto): 0.

**Gruta do Gelo Azul (Tundra):** parede Glacier com faixas de Slate, piso Ice; **68 formações de gelo** (23 estalactites, 10 estalagmites, 4 aglomerados grandes, 31 largos) em `Tundra_Congelada.Formacoes_Gelo_Gruta`, posicionadas por raycast (piso/teto/parede, ≥26 studs dos túneis), `Atomic`, `CanQuery=false`; 23 PointLights azul-frio (brilho 0,9–1,4, sem sombra); perfil de luz próprio `TGRUTA` no `Ambiente_Biomas`. Malhas: **geradas pela IA do Roblox (`generate_mesh`) — NÃO no Blender** (o MCP do Blender não estava disponível nesta sessão); biblioteca em `ServerStorage.Gelo_Lib` (4 malhas, sem scripts, colisão Hull). 68/68 peças encostadas no terreno; placas de 18 aglomerados de parede afundadas 2,5 studs. Bug corrigido: estalactites "consultáveis" faziam o clima achar que a gruta era ao ar livre (neve/névoa dentro) → raycasts de teto só contra o Terrain (`Ambiente_Biomas`, `Tundra_Clima`) e decoração `CanQuery=false`.

**Testes (Play/PC no Studio, 2026-10-25):** pathfinding nas 6 trilhas 125/125 trechos; rotas longas: topo da mesa → toca do cânion, duna → toca do cânion, oásis → Salão dos Cristais, duna → toca das gargantas, borda da cratera → grota = 5/5 (istmo → monumento é longo demais para uma só requisição; coberto pelas trilhas R1/R5); gruta de gelo: entrada → Salão das Colunas → Salão da Luz → saída leste + passagem alternativa + galeria norte = 5/5. Tempestade em 3 fases capturada (aproximação, pico com névoa 0,62 e som `Tempestade_Areia`, dissipação). Música: Planícies `A_Fresh_Start_Harp` na transição → deserto `Dream_Walk_B`/`Voyage` + `Vento_Deserto`/`Brisa_Areia`. Distância: mesas, palmeiras, monumento e acácias visíveis de longe (vegetação Persistent). FPS: 60 na transição, 58 no centro do deserto, **48 dentro da gruta de gelo** (23 luzes + malhas; medido com captura ativa); memória do Studio 10–11,6 GB (é do Studio inteiro, não do jogo).
**Capturas:** `SCREENSHOTS/M6_1_M6_2_Refinamento` (24, com pares ANTES/DEPOIS).

**Limitações/pendências:** facetas triangulares escuras no teto da gruta de gelo (voxel binário da escavação; precisa de ocupação fracionada — não corrigido); algumas faixas de rocha nas paredes da gruta parecem prateleiras; textura do arenito nas cavernas do deserto ainda "rasgada" de perto; colunas do Salão das Colunas (Tundra) ainda são cilindros verticais; terraço do covil Agulha ainda parece disco na nevasca; as outras tocas/covis da Tundra não foram re-escavadas com a correção de costura; celular não testado; **o place não é salvo pela integração** (usuário: Ctrl+S).

## M6.3 — GRUTA DO GELO AZUL: TETO LISO, COLUNAS EM AMPULHETA, CLIMA PELO PERSONAGEM (2026-10-25, aprovado pelo usuário: "Ok, prossiga")
**Backup:** `Proto_Restore/Backup_Gruta_M6_3` — `Terreno_Gruta` (TerrainRegion x −1620…−700, y 40…330, z −5600…−4980; atributo `Canto`), `TundraCavernas_preM6_3`, cópias desativadas de `Ambiente_Biomas`/`Tundra_Clima`/`Deserto_Clima` (`*_preM6_3`).
**Alterações:**
- `TundraCavernas.escavar`: **ocupação fracionada** nas bordas da caverna (8 subamostras por voxel; rocha 0,4–1; ar colado na rocha até 0,45 com o material vizinho) — o teto deixou de ter a malha de triângulos escuros (era ocupação binária 0/1). Piso continua plano.
- Colunas do Salão das Colunas em **ampulheta** com relevo 3D; `dentro()` devolve −1 para coluna e o escavar preenche a rocha (antes só deixava de escavar).
- Gruta re-escavada (25.698 voxels, 14,6 s). Só a Gruta; tocas/covis não foram tocados.
- Clima: o teto da caverna passou a ser medido a partir do **personagem** (`origemTeto`) em `Ambiente_Biomas`, `Tundra_Clima` e `Deserto_Clima`. Antes, com a câmera dentro da parede, o raio nascia no sólido, não acertava nada e o clima ligava neve/névoa de ar livre dentro da caverna (visto no Salão da Luz).
- 3 estalagmites com vão < 1 stud afundadas 1,2.
**Testes (Play/PC):** 68/68 formações encostadas na rocha (0 enterradas; teste por raio nos 26 sentidos); pathfinding 5 túneis ponta a ponta + Salão das Colunas → Salão da Luz = 6/6; no Salão da Luz com a câmera na parede: só a nevasca baixa de caverna (rasteira 10, flocos 36), sem neve do céu, névoa 0,18 do perfil da gruta; console sem erro do projeto. FPS no Studio: Salão das Colunas 49, Salão da Luz ~40 — **igual com as 23 luzes e as malhas desligadas** (o custo não vem das formações; não investigado). Capturas 25–29 em `SCREENSHOTS/M6_1_M6_2_Refinamento`.
**Limitações:** algumas manchas escuras de Slate e poucos triângulos ainda aparecem nas paredes; a ocupação fracionada só foi aplicada na Gruta (tocas/covis e cavernas do deserto ainda usam a escavação antiga, embora o módulo do deserto não tenha recebido esta mudança); celular não testado; **place não salvo pela integração** (Ctrl+S).

## M6.4 — TETO LISO EM TODAS AS CAVERNAS (TUNDRA + DESERTO) (2026-10-25, pedido do usuário: "aplique a ocupação fracionada… com backup antes")
**Backup antes:** `Proto_Restore/Backup_Cavernas_M6_4` — 10 TerrainRegions (`T_Toca_Lobos_Cume_Sul`, `T_Toca_Lobos_Desfiladeiro`, `T_Covil_Dragao_Coracao`, `T_Covil_Dragao_Agulha`, `T_Covil_Dragao_Vigia`, `T_Caverna_do_Coracao_Glacial`, `D_Cavernas_Cristalinas`, `D_Toca_Escorpiao_Gargantas`, `D_Toca_Escorpiao_Canion`, `D_Grota_Lagarto_Cratera`; atributo `Canto` = canto mínimo para `PasteRegion`) + `TundraCavernas_preM6_4` e `DesertoCavernas_preM6_4`. Cristais de caverna antigos em `Retirados_Deserto/.../v3_preTetoLiso`.
**Alterações (os dois motores de escavação):**
- Ocupação fracionada **só no teto** (rocha com ≥3 voxels de vazio logo abaixo) e no ar a ≥8 studs do piso. **Substitui a versão M6.3** (que fracionava também paredes e piso): essa versão quebrava o pathfinding do Roblox em túneis estreitos (Caverna do Coração Glacial passou de Success para NoPath — confirmado colando o backup na sessão de Play e testando as duas versões). Piso e paredes ficam cheios.
- Tundra: faixas de material das paredes mais grossas e contínuas (faixa de 1 voxel virava triângulo solto — no covil Coração eram 62 voxels isolados de Glacier na parede de Slate).
- Re-escavadas as 11 cavernas (Gruta incluída, para ficar na mesma versão); contagens de voxels iguais às anteriores nas cavernas sem plataforma.
- 39 cristais das cavernas do deserto recolocados (0 sem rocha na base); formações de gelo: 1 estalagmite aproximada da rocha (2,6 studs) e 2 peças que ficaram 60–70% dentro da parede puxadas 2 studs para fora (68/68 encostadas).
**Testes (Play/PC):** pathfinding ponta a ponta de todos os túneis das 11 cavernas = **19/20** + Salão das Colunas → Salão da Luz; a única falha (Toca_Lobos_Desfiladeiro túnel 2) **já falhava antes** (testado com o backup colado). Capturas: Gruta (teto liso), covil Coração antes/depois (faixa contínua), Salão dos Cristais (teto sem pontos laranja). Console sem erro do projeto. FPS no Studio: Salão dos Cristais 56.
**Limitações:** ainda há alguns triângulos pequenos na borda das faixas de material (efeito do terreno ao misturar 2 materiais); textura do arenito nas paredes do deserto continua "rasgada" de perto; Toca_Lobos_Desfiladeiro túnel 2 sem caminho para o pathfinding (pré-existente, ponta final dentro da parede); celular não testado; **place não salvo pela integração** (Ctrl+S).

## M6.5 — GRUTA DO GELO AZUL CRISTALINA (referência visual do usuário) + VARREDURA ESTRUTURAL DA TUNDRA (2026-10-25)
> O pedido citava "projeto Dragon Ranch"; o único place com a Tundra Congelada é `rpg_roblox` (o outro Studio aberto, `Place1`, é um baseplate vazio) — aplicado em `rpg_roblox`.

**Backup:** `Proto_Restore/Backup_Gruta_M6_5` — `Terreno_Gruta` (x −1620…−696, z −5600…−4976, y 40…330), `Terreno_Gruta_Sul` (x −1620…−1360, z −5936…−5600), `Formacoes_Gelo_Gruta` (cópia das 68 formações antes do tratamento), `TundraCavernas_preM6_5`, `Ambiente_Biomas_preM6_5`, `Poco_Oculto_1/2` (os 2 poços preenchidos). Peças de teste (vitrine) em `Retirados_Tundra`.
**Visual da gruta (alvo: caverna glacial cristalina, rocha escura + gelo luminoso):**
- Paredes de rocha escura (Slate) com faixas grossas de gelo (Glacier), teto de gelo (Glacier) — `teto=` novo no motor de cavernas; menos neve no piso (`neveLim=0.45`).
- **Gelo polido**: MaterialVariant gerado `Tundra_Gelo_Polido` como override do material Ice (azul profundo, rachaduras, baixa rugosidade). Ice só existe na Tundra (varredura de superfície: 767 pontos dentro, 0 fora) — vale também para lagos/riachos congelados da Tundra.
- **Cristais "vivos"**: casca translúcida (SmoothPlastic, transparência 0,2–0,3, sem refletância) + núcleo Neon azul (transparência 0,74) — brilho de dentro. Vidro (Glass) e Reflectance foram testados e descartados: refletem o céu externo dentro da caverna. Aplicado nas 68 formações antigas e nas novas.
- **Novas peças** (`Formacoes_Gelo_Gruta/M6_5_Cristais_Vivos`, 70 modelos, 140 peças com núcleos): 8 grupos grandes de cristais no piso (colisão ligada, ≥24 studs dos túneis), 10 trios de fragmentos saindo do piso, 9 pares saindo das paredes, 14 placas de pingentes longos no teto. 3 malhas novas geradas pela IA do Roblox (`Cristal_Fragmento`, `Cristais_Gelo_Grupo`, `Pingentes_Longos`) em `ServerStorage.Gelo_Lib`. **Blender não disponível** nesta sessão (nenhuma ferramenta do Blender carregada).
- Atmosfera (`M6_5_Atmosfera`): névoa baixa (3 emissores, taxa 2,2), 3 raios de luz (Beam) descendo do poço do Salão da Luz, 4 luzes frias extras sem sombra. Perfil `TGRUTA`: exposição −0,05, bloom 0,55, contraste 0,2 (a 1ª versão ficou lavada).
**Correções estruturais:**
- Varredura da Tundra inteira: mapa de superfície a cada 8 studs (488.280 pontos) → **0 buracos/poços** no chão; lâminas sobre vazio (voxels sob a superfície) → 7 colunas: **2 poços ocultos** (~100 studs de fundo, 4–12 de largura, tampados por crosta de 4–12) em (−2126,−3974) e (−1998,−3590) **preenchidos** com rocha (153 voxels); 3 colunas = teto fino do túnel sul da gruta perto da boca (mantido; conferido em captura).
- Túnel sul da gruta (z −5600…−5900) estava fora da área re-escavada: tinha um "pilar" de terra marrom (24 voxels de Ground) e materiais antigos → re-escavado.
- Árvores: 2.572 conferidas; 9 flutuando 1,2–4,7 studs assentadas; 1 bétula dentro da água (−1262,−2536) movida 17 studs para terra seca. 0 enterradas.
- Novas peças: 11 de 70 encostadas na rocha após verificação em 26 direções.
**Testes (Play/PC):** túneis da Tundra 12/13 (falha pré-existente: Toca_Lobos_Desfiladeiro t2); Salão das Colunas → Salão da Luz OK; túnel sul OK; dentro dos salões 3/4 (o ponto que falha fica num canto entre parede e 2 formações antigas; pontos a 8 studs passam). FPS no Studio: Salão das Colunas 57, Salão da Luz 40 (igual a antes das mudanças). Console: 0 erros. Capturas em `SCREENSHOTS/M6_5_Gruta_Cristalina` (8).
**Limitações:** o Salão da Luz ainda é muito claro (é o salão do poço de luz); terreno do Roblox não fica translúcido nem reflete a cena (o brilho vem das malhas e da textura do gelo); celular não testado (Neon + transparência têm custo); **place não salvo pela integração** (Ctrl+S).

## M6.6 — SALÃO DA LUZ MAIS ESCURO (2026-10-25, pedido do usuário: "Escurecer, prossiga")
**Backup:** `Backup_Gruta_M6_5/Ambiente_Biomas_preM6_6`; brilho original das luzes guardado no atributo `BrilhoM65` de cada PointLight.
**Alterações:** perfil `TLUZ` no `Ambiente_Biomas` só no Salão da Luz (entra suave entre 85 e 45 studs do centro −1520,−5450): exposição −0,45, ambiente mais escuro, bloom 0,4, contraste 0,26; 9 luzes do salão a 55% do brilho; 48 núcleos Neon com transparência 0,84; raios de luz um pouco mais visíveis.
**Testes (Play/PC):** Salão da Luz: exposição −0,41, ambiente (77,105,147), FPS 40 (igual a antes); Salão das Colunas continua com exposição −0,05. Captura `SCREENSHOTS/M6_5_Gruta_Cristalina/09_DEPOIS_salao_da_luz_escurecido.jpg`.
**Pendências:** celular não testado; **place não salvo pela integração** (Ctrl+S).

## OPERAÇÃO M6.3 (do usuário) — CLIMA QUENTE E SOL INTENSO NO DESERTO DE CRISTAL (2026-10-25)
> Nome dado pelo usuário; não confundir com a seção "M6.3 — Gruta do Gelo Azul" acima nem com as tarefas M6.x de chefes em TASKS.md.

**Backup:** `Proto_Restore/Backup_M6_3_Calor` (cópias desativadas de `Ambiente_Biomas` e `Deserto_Clima`). Nenhum objeto novo, nenhuma mudança de terreno/habitat; Lighting global não foi alterado no Studio (tudo é aplicado pelo cliente só dentro do deserto, com transição pela máscara da região).
**Perfil `DS` (Ambiente_Biomas), antes → depois:** hora 13,2 → 14,7 (sombras mais longas sem virar entardecer); Brightness 3,6 → 4,3; Exposure 0,04 → 0; OutdoorAmbient (176,162,138) → (150,130,104) e Ambient (116,106,92) → (100,88,72) (sombra mais escura = contraste); EnvironmentSpecular 0,5 → 0,9 (brilho na areia e nos cristais); Atmosfera densidade 0,22 → 0,2, offset 0,06 → 0,08, haze 0,9 → 1,05, glare 0,45 → 1,0, cor (244,236,218), decay (232,208,164) (horizonte quente e claro); ColorCorrection tint (255,242,222), saturação 0,03 → 0,08, contraste 0,12 → 0,18; SunRays 0,1 → 0,22 (spread 0,38); Bloom 0,22 → 0,3; nuvens cobertura 0,26 → 0,14.
**Tempestade (`DST`):** além do que já fazia, agora também derruba o brilho especular (0,35), contraste (0,04), bloom (0,15), ambiente externo e o glare (0,05) — o sol "some" na tempestade.
**Deserto_Clima:** sombras nítidas (ShadowSoftness 0,18 → 0,04) e desfoque leve só na distância (DepthOfField far 0,09, foco 320, raio 420) como aproximação de ar quente — ambos multiplicados por fator do deserto × (1 − tempestade), desligados em cavernas e debaixo d'água, e devolvidos aos valores-base (guardados como atributos `SombraBase`/`Base*`) fora do deserto; rajadas curtas de areia a cada 14–34 s com tempo bom.
**Testes (Play/PC):** dunas, cânion (faixa de sombra nítida no pé da parede, sombra do personagem), cristais, caverna (efeitos de calor desligados: sombra 0,18, DOF off), tempestade no pico (brilho 2,6, glare 0,05, névoa 0,62, som de tempestade 0,5), transição pelas Planícies; personagem e terreno visíveis sem estourar. Outros biomas conferidos com a câmera no local: Floresta (14,4 / 3,5 / glare 0,6), Pântano (13,4 / 2,1), Tundra (11,8 / 2,39), Planícies (14,6 / 3,4) — todos com sombra 0,18 e DOF desligado, iguais aos perfis anteriores. FPS no deserto 58. Capturas antes/depois em `SCREENSHOTS/M6_3_Deserto_Calor` (10, incluindo uma versão rejeitada com horizonte alaranjado demais).
**Limitações:** o Roblox não tem distorção térmica real — o "ar quente" é aproximado por névoa quente no horizonte + desfoque leve à distância; celular não testado (DOF tem custo); **place não salvo pela integração** (Ctrl+S).

## M7 — COSTAS SELVAGENS (7º bioma) + AUDITORIA DOS 7 BIOMAS (2026-10-25, "OPERAÇÃO M7", autorização final do usuário)
**Posição (dados reais do Studio):** leste do Deserto de Cristal e do Pântano Nebuloso, antes só mar. Continente costeiro ≈ x 8.000–12.000, z −3.650–7.550 (contorno irregular com ruído de domínio); ilhas x 12.400–14.500; Abismo Azul x 13.300–17.000; caixa escrita x 8.000–17.000, z −4.600–8.400 (7.242 blocos de 128). Terras Corrompidas: faixa sul (z > 8.400) reservada e **não construída**.
**Ligações:** por terra com o Deserto (≈ 8.150, 3.300) e com o Pântano (≈ 7.800, 0) — pathfinding por trechos 5/5 e 5/5; Canal das Marés (220–340 de largura, 18–24 de fundo) liga o mar oeste antigo à enseada, com **vau** raso (9.300, 2.140); Rio dos Cânions do Deserto continua até a enseada como **estuário** (vau em 9.870, 3.640); Rio Costeiro novo na Floresta Litorânea (vau em 9.830, −720). Água no mesmo nível 8 do mundo, sem degraus.
**Documentos:** RPG_01 — Costas Selvagens "faixa irregular no litoral", "mar costeiro com ilhas menores"; árvores PROVISÓRIAS Coqueiro Bravo e Cedro Costeiro; fauna de coleta PROVISÓRIA Gaivota-das-Marés, Caranguejo-de-Recife, Lagarto-da-Salina. RPG_02 — espécies OFICIAIS: **Serpente Marinha** (30–45 de comprimento; perseguição aquática, constrição, correntes; sem veneno inato) e **Leviatã Jovem** (55–80; oceano aberto; fraco em espaços confinados).
**Geradores (Proto_Restore):** `CostasGen` (relevo/água/materiais, raster de distância ao contorno, emenda com terreno antigo pela máscara `Dados_Montagem/CostasCampoExistente`), `CostasWriter` (`tile(ix,iz)`, protege 60.507 colunas de terra antiga; sólido até −48; `TETO_TOTAL`), `CostasCavernas` (motor de cavernas da Tundra com trechos inundados `agua=8`). Backup das margens antes: `Backup_M7_Costas/Margem_Oeste_1..5` + cópias de `Ambiente_Biomas`/`Pantano_Neblina`.
**Oito regiões:** C0 Fronteira Costeira (campo costeiro, canal, estuário); C1 Praias Selvagens (praias longas e irregulares de 50–150, dunas costeiras, coqueirais); C2 Falésias do Oceano (95–180 de altura, plataforma de abrasão na base, degraus de erosão, 6 agulhas de rocha no mar); C3 Floresta Litorânea (cedros com clareiras, Rio Costeiro em vale); C4 Enseadas e Recifes (enseada protegida, 5 recifes com manchas de coral de 2–6 de profundidade); C5 Cavernas Marinhas (Gruta das Marés com Salão da Gruta + Salão do Eco com colunas e piso parcialmente inundado, poço de luz; Caverna Submersa com entrada a −16, só a nado; Toca do Rochedo a pé pela praia); C6 Ilhas Selvagens (7 de tipos diferentes: mata, rochedo de 135, praia, gêmeas, falésia, recife); C7 Abismo Azul (plataforma 30–140, cânions submarinos, fossa até ≈ −310).
**Materiais (variantes geradas, só nas Costas):** Pavement = `Costas_Areia_Praia`, Asphalt = `Costas_Rocha_Falesia`, Concrete = `Costas_Recife_Coral`, CrackedLava = `Costas_Grama_Litoral`; cores antigas em `Proto_Restore` atributo `CoresAntesCostas`. **WoodPlanks/Brick renderizam o terreno em blocos/degraus** (descoberto em teste: rampa suave virou degraus de 4) — não usar.
**Vegetação (malhas IA do Roblox, sem scripts, `ServerStorage.Costas_Lib`):** 1.682 árvores (1.113 Cedros Costeiros alto/vento, 569 Coqueiros Bravos alto/jovem) + 2.225 arbustos costeiros, densidade por região (floresta densa com clareiras pelo ruído; praias com coqueirais em bosques; falésias com cedros baixos ao vento), longe de trilhas, sem grade; 161 clusters de árvores `Persistent` (visíveis de longe), arbustos `Atomic`. Todas reassentadas pela base da geometria após cada reescrita; 0 na água.
**Habitats (`Costas_Selvagens/Habitats/Ecologia_Fauna`):** Serpente Marinha SM1 Enseada dos Recifes, SM2 Grutas Marinhas (refúgio na Câmara Submersa, ninho elegível no Salão do Eco), SM3 Canal das Marés; Leviatã Jovem LV1 Abismo Norte (território a 138 de profundidade, refúgio na fossa a 235), LV2 Abismo Sul (210/224) — só em mar fundo e largo (fraqueza oficial em espaços confinados); rotas submarinas, zonas de caça, `LocalNinhoElegivel` (Ativo=false, 30–60 min OFICIAL); fauna provisória (gaivota, caranguejo, lagarto-da-salina) e 7 cenas de interação. Sem IA.
**Exploração:** 5 trilhas (Deserto→Praias, Pântano→Mata→Mirante, Falésias panorâmica, Praias Selvagens, Vau do Canal) — pathfinding 25/25 trechos; 6 mirantes, 12 pontos de interesse, 4 áreas de combate, 5 marcadores de caverna.
**Clima/som:** perfil `CSP` no `Ambiente_Biomas` (céu azul, nuvens volumosas, névoa leve só no horizonte, água turquesa transparente) com entrada suave pela região; **chuva ocasional** (~1/6 do tempo, `chuvaCosta()`, nuvens 0,93, névoa 0,42, som de chuva, gotas no `Costas_Clima`); nevoeiro do Pântano limitado a x < 8.100. Subaquático `Costa`: raso claro/turquesa, escurece com a profundidade **medida até o nível do mar** (−28 azul-turquesa, −128 azul-marinho com fundo apenas sugerido, −200 azul muito escuro sem preto). Sons licenciados: ondas de praia e de falésia, vento costeiro (mais forte no alto), aves marinhas, gotejar em caverna, chuva; músicas APM "World Voyage" e "Crossing Over".
**Auditoria dos 7 biomas (feita por varredura, não por amostra visual completa):**
- Árvores: 11.402 conferidas (Floresta 4.888, Montanhas 2.201, Pântano 1.430, Planícies 193, Tundra 2.572, Deserto 118) + 3.907 plantas das Costas. Corrigidas: 2 salgueiros flutuando no Pântano (5.796, −1.097) e (4.349, 275); 1 freixo da Floresta flutuando sobre rio de 35 de fundo (800, 645) movido 9 studs para a margem. 26 mangues "na água" no Pântano = intencionais. 45 árvores com base 8–37 abaixo do chão (raízes enterradas, ≤16% da altura, em encostas) — **mantidas, pendente revisão visual**.
- Terreno (coluna a cada 64 studs em todo o mapa, 76.189 colunas): 0 água suspensa real (393 alertas eram voxels parciais do fundo); lâminas: restos da 1ª escrita das Costas (laje antiga a 140 sobre o mar) → 258 blocos reescritos com `TETO_TOTAL`; casca oca sob o relevo das Costas → writer corrigido (sólido até −48) e tudo reescrito. **Erro meu corrigido:** 9 "bolsões" preenchidos nas Montanhas eram trechos de 8 cavernas (as cavernas das Montanhas não estavam no módulo genérico) — re-escavadas pela própria `MontanhasCavernas.carve` com posição/ângulo salvos em `_CavernasMontanhas`; boca→câmara 11/11 com pathfinding.
- Água/rios: canal, estuário e Rio Costeiro com vaus; sem quedas entre níveis; profundidades conferidas nos habitats.
- Cavernas: Montanhas 11/11, Costas 3/3 acessíveis (Caverna Submersa a nado por desenho).
**Testes (Play/PC):** praias, falésias (do mar e do topo), floresta litorânea, Salão do Eco, recife raso, −28/−128/−200, estuário com chuva, mirante; acesso por terra e vau; console sem erros do projeto após correção. FPS no Studio: praias 58, falésias 55; memória do Studio 14,9 GB (Studio inteiro). Capturas em `SCREENSHOTS/M7_Costas_Selvagens` (12 + mapa). **Mapa-resumo atualizado** `SCREENSHOTS/Mapa_Resumo_Mundo.png` (anterior guardado como `Mapa_Resumo_Mundo_M6.png`); a parte das Costas é raster real do Studio.
**Limitações / não verificado:** Blender MCP não disponível (malhas da IA do Roblox); gotas de chuva pouco visíveis nas capturas (a chuva é percebida pelo céu, névoa e som); 45 árvores com raízes fundas não revisadas visualmente; a auditoria visual cobriu pontos representativos, não todo o mapa; LOD/pop-in de malhas de outros biomas não remedido nesta sessão; celular não testado; **o place não é salvo pela integração (Ctrl+S)**.

## M7.1 + M7.2 — COSTAS SELVAGENS REFINADAS E OCEANO EM 4 ZONAS (2026-10-26)
> **Atenção:** ao reabrir o Studio, o place estava salvo numa versão do **início da M7** (só as variantes de material e `Backup_M7_Costas`); toda a construção da M7 de 2026-10-25 **não tinha sido salva** (a integração não salva; precisa de Ctrl+S). A seção M7 acima descreve a versão perdida. Nesta sessão a costa foi **reconstruída já na versão refinada** (M7 + M7.1 + M7.2) com o mesmo layout macro e as mesmas correções da M7.
**Geradores (Proto_Restore):** `CostasGen` v2, `CostasWriter` v2 (sólido até o vizinho mais fundo num anel de ±128 — sem vazio sob a plataforma), `CostasCavernas` (definições em `Dados_Montagem/CostasCavernasDef`), máscara `Dados_Montagem/CostasCampoExistente`. Escrita completa 2× (369 s e 447 s); 60.475 colunas de Deserto/Pântano protegidas.
**M7.1 (terra):** costa com 3 escalas de deformação + 6 enseadas em crescente + 3 pontais rochosos; praias de largura variável; colinas e vales no interior (sem áreas planas vazias); falésias 95–185 com estratos irregulares, ravinas de erosão e 8 agulhas; rios com meandros e largura variável ao longo do curso; ilhas com identidade (Ilha da Mata, Rochedo do Vento com fendas, Ilhota da Praia, Gêmeas ligadas por tômbolo, Ilha das Falésias, **Atol do Recife** com lagoa).
**M7.2 (oceano):** Zona A 0–12 (bancos de areia paralelos à praia, pradarias marinhas, recifes rasos); Zona B 12–45 (plataforma com afloramentos rochosos, recifes elevados com esporões e canais, florestas de kelp); **paredão** na quebra da plataforma (~1.050 da costa) para a Zona C 120–180 (montes submarinos, canais, cânions); Zona D Abismo 250–420 com segundo paredão, ravinas e fossa. Cavernas: Gruta das Marés (a pé, 3 salões + poço de luz), Caverna Submersa (só a nado), Toca do Rochedo, **Gruta do Paredão** (nova, totalmente submersa a ~−95, refúgio de serpente), **Arco do Cabo** (novo, arco marinho de 20 de altura).
**Materiais:** Pavement=areia, Asphalt=rocha de falésia, Concrete=recife (cor suavizada), CrackedLava=grama/pradaria; Slate/Basalt no fundo; variantes `Costas_*`.
**Vegetação e vida (malhas IA do Roblox; Blender MCP não disponível):** 1.838 cedros, 589 coqueiros, 75 mangues de margem de rio, 3.119 arbustos, 523 capim de duna; submarino: 405 corais (ramificado/cérebro-mesa), 311 gorgônias, 658 kelp — concentrados em recifes e plataforma rochosa, nada nas zonas C/D além de gorgônias fundas raras; 420 kelp/gorgônias redimensionados para não furar a superfície. Árvores em clusters `Persistent`; arbustos e vida submarina `Atomic`.
**Habitats (RPG_02):** Serpente Marinha SM1 Enseada dos Recifes, SM2 Grutas Marinhas (refúgio e ninho elegível em câmaras de ar), SM3 Canal e Estuário + rota subindo o Rio dos Cânions do Deserto (profundidade mínima 22 nos pontos; vaus exigem deslize), SM4 Paredão (refúgio na Gruta do Paredão, caça a 42); Leviatã Jovem só nas Zonas C/D: LV1/LV2 (territórios 250–343, refúgios nas fossas 353–359), corredor ao longo do paredão (mín. 126) — sem canais estreitos. Fauna provisória e 8 cenas. Sem IA.
**Clima/visão:** perfil costeiro com ondas maiores (WaterWaveSize/Speed por região), chuva ocasional, espuma discreta na linha da costa (`Costas_Clima`); visão subaquática da costa por zona e profundidade da câmera (luz cai exponencialmente; alcance 70 raso → ~11 no abismo; cor turquesa → azul-marinho; cavernas mais escuras); som subaquático.
**Auditoria da costa:** 115.133 colunas — 0 água sobre ar, 0 vazios sob sólido (após corrigir o writer); 7.604 objetos — 0 flutuando, 27 arbustos meio enterrados reassentados; 3 marcadores de habitat corrigidos (rota do leviatã sobre a plataforma, ponto do rio na margem, caça no atol).
**Incidente (corrigido):** um script de limpeza moveu por engano **5.318 modelos gerados por IA** do workspace (juncos/vitórias-régias do Pântano, arbustos alpinos e casas das Montanhas, ruínas e troncos do Pântano, 68 formações da Gruta do Gelo) para `Proto_Restore`; todos foram devolvidos ao mundo **nas mesmas posições** (posições nunca mudaram), em contêineres escolhidos pela grade/célula mais próxima — 70 células do Pântano e 17 das Montanhas ficaram vazias porque o agrupamento interno pode diferir do original (só organização).
**Testes (Play/PC):** praia/pontal, enseada, recife (Zona A), kelp (Zona B), paredão (Zona C), abismo a −371 (Zona D), entrada da Gruta do Paredão, falésias e Arco do Cabo, rio costeiro com mangues, ilhas/atol; FPS no Studio 49–57, memória do Studio 11,4–11,8 GB; console sem erros do projeto. Capturas: `SCREENSHOTS/M7_1_M7_2_Oceano` (11 + antes da M7 + mapa). Mapa-resumo atualizado.
**Limitações / não verificado:** a entrada da Gruta do Paredão é pouco legível na captura (profundidade); a captura do abismo e a do kelp são de antes do último ajuste de luz; pathfinding das cavernas e acesso por terra não foram retestados nesta reconstrução; espuma e gotas de chuva não conferidas em captura; celular não testado; **place só fica salvo com Ctrl+S do usuário**.

## M7.3 — ACABAMENTO FINAL DAS COSTAS SELVAGENS (2026-10-26)
**Salvamento:** a integração MCP não consegue salvar o place nem confirmar um salvamento (`user_keyboard_input` só envia teclas ao jogo em Play, não ao Studio). O estado inicial foi conferido (Costas intactas na sessão aberta); **o usuário precisa pressionar Ctrl+S**.
**Backup:** `Proto_Restore/Backup_M7_3` — cópias `CostasGen_M7_2`, `CostasWriter_M7_2`, `CostasCavernas_M7_2` e 8 `TerrainRegion` dos pilares antes da escultura. As árvores originais (malha única) estão em `Proto_Restore/Retirados_Costas_M73/Arvores_Originais` (2.501); itens retirados por ficarem na água/soterrados também nessa pasta. T3 histórica intocada.
**Pilares (novo módulo `CostasPilares`):** os 8 pilares deixaram de ser cilindros do mapa de alturas (`CostasGen.AGULHAS_3D=true`) e são esculpidos em 3D com SDF: base alargada até o fundo, entalhe de ondas na linha d'água (faixa de Basalt molhado), estratos inclinados com cornijas discretas, silhueta assimétrica e inclinada, fendas verticais, topo com grama nos maiores, 3 pilares irmãos e blocos caídos submersos. O Arco do Cabo foi reescavado no pilar 3. Correção: espinho fino de terreno no eixo acima do topo (ruído mantinha ocupação) — eliminado.
**Praias (CostasGen):** largura com mais contraste (praias grandes e pequenas), perfil com face de espraiamento, berma e escarpa de erosão em trechos, campo de dunas em rede com depressões abrigadas e corredores de vento, faixa irregular de **areia compactada/molhada** junto da água (Limestone = `Deserto_Areia_Compactada`, único material livre compatível), limite areia/grama por ruído (sem curvas de nível), manchas de grama nas dunas e faixa de solo exposto na transição.
**Rios:** margem externa das curvas com barranco baixo de terra/rocha (4–11 studs) e talvegue deslocado; margem interna com praia fluvial de areia; poços e corredeiras só no Rio Costeiro; estuário e canal mantêm a rota profunda (serpente). Primeira versão do barranco ficou alta demais (~40, "pedreira") → limitada e reescrita (542 blocos).
**Oceano:** recifes com frente em paredão e bolsões de areia; 13 formações submersas 3D (8 cabeças de coral com topo de coral e 5 Sentinelas do Abismo, 5 reposicionadas automaticamente para a profundidade correta); Abismo com descida em terraços, **Poço Azul** (depressão ~600 de diâmetro) e **Crista das Sentinelas** (dorsal até ~−90); 2 arcos novos: **Arco do Recife** (−21) e **Arco das Profundezas** (−150, vão ~50, atravessa a crista).
**Vegetação:** coqueiros, cedros e mangues segmentados (IA `segment_mesh`) em tronco + `Folhagem_Copa`; 2.501 árvores substituídas; coqueiros mais esbeltos (largura ×0,82, altura ×1,12) e inclinados 10–22° para a água perto da costa; tag `ArvoreBlender` + `Bioma=Costas` → **vento só na copa** (pivô no topo do tronco, amplitude ×1,35) via `Floresta_Vento`. Todas as 7.604 peças reassentadas pela geometria da base (ponto mais baixo de 7 amostras do terreno sob o tronco); 94 corais soltos na areia movidos para rocha de recife (664 já estavam em rocha).
**Água/luz:** visão subaquática com alcance maior no fundo (90/75/60/50 por zona) e opacidade máx. 0,7 para ler marcos como silhuetas; transição na superfície medida (tint 0,98→0,76, blur 0→2,1, brilho −0,02: sem salto de exposição). Lighting global não alterado.
**Auditoria:** bolsões de ar encostados em água nas regiões 3D: 1.721 → 0 (água preenchida nas paredes fracionadas dos túneis; 1 célula isolada corrigida). **Vazio sob a plataforma** exposto pela Gruta do Paredão (túnel abaixo da base sólida de ~−80) → preenchido com rocha preservando a água do túnel. Marcadores reassentados (5 subiram, 1 desceu; 12 dentro de cavernas mantidos); 5 marcadores novos (2 arcos, Poço Azul, Crista, Cabeças de Recife).
**Testes (Play/PC, câmera dirigida):** pilares, praia, rio costeiro, recife subaquático, interior do Arco das Profundezas, panorama da costa sul, transição câmera ar/água. FPS 57,6–58,3; memória total do Studio ~12,0 GB; 233 mil instâncias. **Não verificado:** carregamento a distância com o personagem em cada local (personagem ficou parado na praia nas medições), cavernas a pé/pathfinding, celular.
**Blender MCP:** não disponível nesta sessão (malhas do Roblox AI + escultura de terreno).
**Capturas:** `SCREENSHOTS/M7_3_Costas_Acabamento` (9).

## M8 — TERRAS CORROMPIDAS (8º bioma) + AUDITORIA DOS 8 BIOMAS (2026-10-26)
**Salvamento:** não é possível salvar/confirmar pela integração; **o usuário precisa pressionar Ctrl+S** (e, se quiser, publicar).
**Backup:** `Proto_Restore/Backup_M8_Terras` (TerrainRegions das 3 ligações antes da escrita — Planícies, Deserto, Costas — com atributo `Canto`; cópias desativadas de `Ambiente_Biomas` e `Floresta_Vento` antes da M8). Itens retirados em `Proto_Restore/Retirados_Terras_M8`. Máscara da terra antiga em `Dados_Montagem/TerrasCampoExistente` (base64 em partes).
**Posição real:** sul do mundo. Caixa escrita x −2.800…13.000, z 6.000…13.200 (7.068 blocos de 128, inclui mar em volta); terra nova ≈ x −2.400…10.900, z 7.700…12.300 (~57 milhões de studs²). **Ligações por terra (sem pontes):** istmo com as Planícies (x≈300–900, z 6.000–7.850), faixa larga com o Deserto (x 2.900–5.800; alargada após teste para eliminar enseadas) e ligação com o sul das Costas (x 8.300–10.200). Mar do sul das Costas fundido ao novo mar.
**Geradores (Proto_Restore):** `TerrasGen` (forma, regiões, corrupção 0–1, rios, lago, materiais), `TerrasWriter` (protege terra antiga; coluna antiga com topo de água não é protegida — corrigiu um canal de 1 célula ao longo de toda a costa antiga), `TerrasCavernas` (motor das Costas/Tundra), `TerrasVeg`, `TerrasExploracao`, `Reassentar` (genérico, base real).
**Regiões:** T0 Fronteira do Declínio (transição gradual com material da terra vizinha), T1 Floresta Retorcida (colinas, bosques com clareiras), T2 Planícies Devastadas (campo aberto, fendas e cristas escuras), T3 Gargantas Sombrias (planalto ~110 cortado por cânions em terraços, Rio da Garganta no fundo), T4 Bosque da Névoa (baixada, Lago Negro 28 de fundo, poças), T5 Cavernas Profundas, T6 Picos Arruinados (250–430, espigões, neve só acima de ~392), T7 Núcleo da Corrupção (depressão ~1.300 de diâmetro, borda +88, fendas radiais, formação central e 11 grandes formações minerais com luz violeta discreta; **área reservada à narrativa oficial — nada revelado**).
**Materiais:** só materiais já existentes com a aparência global atual (nenhuma variante nova/alterada): capim seco (LeafyGrass), solo, lama, basalto (solo rachado/corrupção), ardósia/rocha (paredões), pouca grama (áreas pouco afetadas), neve nos cumes; roxo/violeta só no Núcleo e nos cristais.
**Água:** Rio Cinzento (nascente nos contrafortes → Lago Negro → mar a oeste), Rio da Garganta (cânion → mar do sul das Costas, 16–22 de fundo na foz), Lago Negro, poças do bosque. Sem dano/veneno.
**Vegetação (malhas IA do Roblox, Blender MCP indisponível):** 2.544 Teixo Cinzento, 1.773 Árvore-de-Casca-Negra, 482 mortas, 2.550 arbustos de espinhos, 41 cristais + 11 marcos. Texturas geradas eram claras demais → tingidas por `SurfaceAppearance` (TintMask). Segmentação tronco/copa gerou texturas novas ruins → **voltou-se aos modelos originais** com balanço suave da árvore inteira a partir da base (`Floresta_Vento`, `Bioma=Corrompidas`). Capim seco gerado (1.368) retirado: parecia estilhaços; a decoração do terreno cobre. Clusters `Atomic` + `LevelOfDetail=StreamingMesh`. 37 árvores/14 arbustos retirados das trilhas.
**Cavernas:** Cavernas Profundas (boca na face norte dos Picos ~y 90, túneis 24 de altura, Salão das Raízes 36 de altura, Grande Câmara 64 de altura, Galeria com poço de luz), Covil do Cérbero Leste e Oeste (paredes do cânion), Caverna Alta dos Picos (~y 250, abertura em penhasco). Definições em `Dados_Montagem/TerrasCavernasDef`.
**Habitats (RPG_02, só marcadores, sem IA):** Cérbero Sombrio — 3 territórios (planície, garganta, borda da floresta), 2 covis elegíveis + refúgios (Salão das Raízes; Grande Câmara como refúgio terrestre — túneis de 24 não comportam dragão adulto). Dragão Sombrio — 2 espaços aéreos (Picos, planície/Núcleo, alt. 250–650), 3 ninhos elegíveis (Caverna Alta, crista norte, pico oeste) com a regra oficial de poucos ninhos e rotação 30–60 min. Fauna ambiente **provisória** (Corvo Crepuscular, Rato-de-Espinhos, Besouro de Cinza).
**Exploração:** 5 trilhas pintadas no terreno (R1 Refugiados, R2 Estrada Partida, R3 Passo das Gargantas, R4 Margem do Lago, R5 Travessia), 8 marcadores de região, 5 mirantes, 6 cavernas, 4 áreas de combate, 4 POIs (marcadores de abrigo/posto do art bible, nada construído), 5 travessias.
**Clima/som (`Ambiente_Biomas`):** perfil Corrompidas (céu encoberto, luz fria neutra, neblina moderada), Núcleo mais denso e levemente violeta, Bosque com neblina baixa, cavernas com ambiente mínimo jogável. Prioridade ao sul; **corrigido vazamento do clima/música do Pântano** (detecção só por X) na faixa Deserto→Corrompidas. Áudio licenciado: músicas APM (The Haunting Dusk, Lost In Time Ambient, Collusion Confusion Ambient) e ambiências Pro Sound Effects (vento, sopro, eco, gotejar, presença grave no Núcleo, névoa). Sem som de galhos rangendo licenciado adequado encontrado.
**Auditoria dos 8 biomas:** vegetação: 448 itens flutuando corrigidos (Floresta 254, Pântano 103, Tundra 30, Planícies 27, Montanhas 23, Costas 7, Deserto 2, Corrompidas 2); correção que usava amostra lateral num buraco enterrou alguns itens → 76 itens profundamente enterrados devolvidos à superfície; árvore da Plataforma 1 da Vila (Floresta) erguida por engano por uma segunda passada → **revertida**. Terreno (grade 96, 54.240 colunas): 0 buracos isolados; 86 colunas com água sobre ar (Montanhas/Floresta, bolsões de 1 célula e 3 colunas sem fundo) → 1.146 células preenchidas com água + 120 de leito de rocha; reverificado: 0. Clima/música conferidos em Play nos 8 biomas (cada um com sua música/ambiência/perfil). Streaming: ~40 mil peças em modelos `Persistent` nos biomas antigos — **não alterado** (impostores `StreamingMesh` só se verificam no servidor publicado); recomendação registrada.
**Testes (Play/PC):** captura de cada região + panorama + interior de caverna; transição Deserto→Corrompidas (densidade 0,20→0,31, brilho 4,3→2,8 sem salto); FPS 57,4–58,2 (floresta, picos, panorama); memória total do Studio 14,7–16,6 GB (Studio aberto há muitas horas com Edit+Play e Proto_Restore grande); console sem erros do projeto. **Não verificado:** celular, multiplayer, pathfinding nas cavernas, impostores de streaming no servidor publicado, travessia a pé completa de cada trilha.
**Mapa:** `SCREENSHOTS/Mapa_Resumo_Mundo.png` (8 biomas; sul com raster real do Studio de 48 studs) + cópia em `SCREENSHOTS/M8_Terras_Corrompidas/Mapa_8_Biomas.png`; versão anterior `Mapa_Resumo_Mundo_M7.png`.
**Capturas:** `SCREENSHOTS/M8_Terras_Corrompidas` (11 + mapa).

## OPERAÇÃO M8.1 — AUDITORIA GLOBAL E ESTABILIZAÇÃO DOS 8 BIOMAS (2026-10-26)
(Operação de bioma do usuário; não confundir com a tarefa M8.1 "regressões" de QA em `TASKS.md`.)
**Salvamento:** a integração não salva nem confirma; **o usuário precisa pressionar Ctrl+S** (a operação M8 também ainda não tinha salvamento confirmado).
**Backup:** `Proto_Restore/Backup_M8_1` — TerrainRegions com atributo `Canto`: `Costura_x8000_2112` e `Costura_x8000_1360` (orla das Costas antes da M8.1), `Orla_x8000_antes_curva` (antes do deslocamento da linha d'água), `Furo_lago_x3040_z1248`, `Furo_fenda_x7984_z1648`, `Furo_x-80_z1664`, `Furo_x-320_z1456`, `Furo_x-16_z1728`. Itens retirados (sem exclusão) em `Proto_Restore/Retirados_M8_1` (atributo `Nota`). Módulo novo `Proto_Restore/PreencherFuros` (preenche colunas sem terreno nem água por interpolação das bordas; restaura o backup antes de refazer).
**Defeitos encontrados e corrigidos, por bioma:**
| Bioma | Corrigido |
|---|---|
| Floresta | 66 paredes invisíveis colidíveis (`Floresta_Blender.Limites_Floresta`, 120 de altura) bloqueavam a passagem por terra para Tundra, Pântano e Planícies → retiradas; 165 marcadores dentro da rocha → subidos; 3 furos de coluna inteira sem terreno em campo de grama (x −320…−16, z 1.456–1.728) → preenchidos. |
| Montanhas Altas | 11 cavernas oficiais abertas, mas 48 marcadores `M5_Cavernas` estavam 35–390 studs fora, dentro da rocha → movidos para a boca/câmara; marcadores de `Gruta_Alta_Picos` ~500 studs dentro da montanha regenerada → retirados; 88 marcadores na rocha → subidos; os 4 ninhos `M6_Ninhos_Aves` estavam enterrados (4, 27, 47 e 172 studs) → na superfície (o `SpawnAveGrande` do Ninho_Ave_2 ficou 22 acima do ninho, fora da rocha); bancos de névoa do `Montanhas_Neblina` se empilhavam nos topos das ilhas flutuantes → ilhas excluídas e raio de busca 1.400→3.000. |
| Pântano | 4 marcadores na rocha; música caía na Floresta na junção Pântano/Costas → bioma dominante agora é o de maior peso (`Ambiente_Biomas`). |
| Tundra | 9 marcadores na rocha. 37 lâminas finas detectadas são lagos congelados (gelo sobre água, intencional) e bocas de caverna → mantidas. |
| Deserto | 6 marcadores na rocha; música caía na Floresta na junção Costas/Deserto → mesma correção do bioma dominante. |
| Costas Selvagens | x=8.000, z 2.168–3.128 e 1.384–1.432: terra terminava num paredão reto de ~25 sobre a água → orla curva com praia e rampa (26.996 colunas); depois, a linha d'água ainda variava só ±20 em 800 studs (parecia reta) → deslocada com ruído (agora x 7.864–7.968, rampa suave até x 8.120), por canais de voxel para não perder água em células mistas; **fenda vazia de 32 studs** (x 7.968–8.000, z 1.640–2.100) atravessando o mundo inteiro (queda infinita) → leito + água; marcador obsoleto `Reserva_Costas_Selvagens` retirado; 3 marcadores na rocha. |
| Terras Corrompidas | costura em x≈2.320, z 7.248–7.728 (borda de bloco fora de uma reescrita) → blocos reescritos e 292 itens reassentados; 371 aglomerados de árvores (4.799 peças) e `Marcos_do_Nucleo` → `Persistent` como nos demais biomas (sem pop-in); marcador da Grande Câmara em y 152; 5 marcadores na rocha. |
| Água sem leito | bloco retangular sem água nem leito (tile nunca escrito) em x 3.040–3.600, z 1.248–2.096 (7.631 colunas de 4 studs, queda infinita no meio do lago) → leito interpolado + água no nível 8. |
**Varreduras:** buracos de coluna inteira em grade de 16 studs no mundo todo (1,96 milhão de raios): 6 grupos internos → **0** após a correção (os 396.957 vazios restantes são o lado de fora do mundo). Grade de 32 por gradiente: costuras acima. Flutuantes/enterrados: 0 nos habitats; modelos vazios: 38 achados, os que guardam dados (trilhas R1–R5 e `Rota_Submarina` das Costas, estruturas da Floresta, aglomerados vazios das Terras) devolvidos, 3 sem uso retirados.
**Erro cometido e revertido:** um filtro por nome contendo "Flor" desligou a colisão de 23 peças da `PonteV9_FlorestaNorte`; colisão restaurada pelo padrão da `PonteV7_M1` (Colisor e Poste colidem; Madeira_M não). Outro: `Reassentar` chamado num aglomerado `C_*` moveu o grupo inteiro +10 → cada filho reassentado individualmente.
**Testes (Play/PC):** música/perfil/atmosfera corretos nos centros dos 8 biomas; no máximo 2 faixas ao mesmo tempo, só durante o crossfade; nenhum emissor de outro bioma ativo nas Montanhas (todos com taxa 0).
**Capturas:** `SCREENSHOTS/M8_1_Auditoria_Global` — orla x=8.000 antes/depois da curva (a de depois foi tirada em Edit, sem a iluminação do cliente) e Ninho_Ave_2 no chão. Não há captura de "antes" dos demais defeitos.
**Pendências:** cascas finas de leito antigo (2.176 colunas de 4 studs sobre vazio, invisíveis de cima); luz `Brilho` do geodo do Deserto dentro da rocha; streaming dos biomas antigos não alterado (impostores só verificáveis no servidor publicado); troncos de pinheiros a ~2.000 studs aparecem como pontinhos escuros na neblina das Montanhas (efeito antigo de LOD + atmosfera, não corrigido).

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

## TAMANHO DO PLACE — BACKUPS M4–M7 EXPORTADOS E RETIRADOS (2026-10-26, autorizado pelo usuário)
**Problema:** o place é **Team Create** e o console repete `Error: could not upload place. File too large` — o salvamento na nuvem está falhando. Tamanho medido pelos autosaves do Studio: 169,5 MB (12:11).
**Backups locais completos (hash conferido):** `Documents/RPG_Roblox/BACKUPS/RPG_BKP_2026-10-26_M9_autorecuperacao.rbxl` (12:11, todo o trabalho M8.1/M9) e `RPG_BKP_2026-10-26_M9_pos_limpeza_M4_M7.rbxl` (12:49, após a retirada).
**Exportação:** 11 pastas de backup M4–M7 (`Backup_Planicies_M4`, `Backup_Tundra_M5`, `Backup_M5_2_Agua`, `Backup_M5_2_Rios`, `Backup_M5_2b_Costas`, `Backup_Deserto_M6`, `Backup_Gruta_M6_3`, `Backup_Cavernas_M6_4`, `Backup_Gruta_M6_5`, `Backup_M7_Costas`, `Backup_M7_3`; 575 TerrainRegions, 382,8 M células) salvas pelo usuário em `BACKUPS/RPG_BKP_2026-10-26_Backups_M4_M7.rbxm` (7,3 MB). **Verificação:** o .rbxm reimportado bateu com o original (11 pastas, 575 regiões, 0 diferenças de tamanho/canto) e 3 regiões coladas numa área vazia fora do mapa (x/z 20.000+) deram impressão de voxels idêntica (Margem_Oeste_3 350×100×650, Tile_50_40, T_-4096_1152; com sólido e água); área de teste limpa depois. Só então as duas pastas (original + cópia importada) foram retiradas. Restaurar: File → Import Roblox Model no .rbxm e devolver as pastas a `ServerStorage.Proto_Restore`.
**Resultado:** autosave caiu só para **165,1 MB** e o erro de upload continua. O peso restante está nas instâncias: `Proto_Restore` ainda tem 477.845 instâncias (56% do place; 121.735 malhas/uniões) — `Originais_Arvores` 202.651, `Montanhas_V1_Vegetacao` 93.492, `Retirados_V7` 53.635, `Retirados_Terras_M8` 25.995, `UniaoBackup` 23.228, `Retirados_V9` 12.497, `Retirados_Costas_M73` 10.077, `Retirados_Pantano` 9.358, `Testes_Importacao` 9.212, outras menores. No mundo: Floresta 152.160, Montanhas 107.748. **Pendente (aguardando autorização):** exportar essas pastas antigas de `Proto_Restore` em lotes (.rbxm verificado) e retirá-las.

## AUDITORIA DE ERROS E BUGS (2026-10-26, tarde; usuário ausente: "pode ver se há erros ou bugs")
**Snapshot local após as correções (hash conferido):** `Documents/RPG_Roblox/BACKUPS/RPG_BKP_2026-10-26_auditoria_LOD.rbxl` (autosave 13:56, 165,1 MB). O salvamento na nuvem continua falhando por tamanho.
**Verificado sem defeito:** 168 scripts compilam (0 erros de sintaxe; 38 fora de `Proto_Restore`); Play: console sem erros/avisos do projeto (só avisos internos `UIBlox` do Roblox); **testes do M1: 47/47 aprovados** (DataStore falso), rodados duas vezes; tour nos 8 biomas: personagem fica no chão (queda 0), vida 100, música/ambiência própria de cada bioma; 0 peças não ancoradas; colisores invisíveis = só substitutos intencionais (troncos, passarelas, cercas, postes, casas) — nenhuma parede invisível grande; `Baseplate` antiga em y −5000 e `SpawnLocation` (desativada) enterrada 49 abaixo da grama — inofensivas; avisos de asset "being generated" referem ids que nenhum objeto usa.
**Corrigido:**
- **Código malicioso (backdoor de modelo gratuito)** em `ServerStorage.Sandbox_Deserto.Cand_Palmeiras_A.PalmD.Extra.Humanoid`: `Script` que se apaga no Studio (`game.JobId == ""`) + `CoreTextureSystem` com `require(Pose.Value)` (id 102764929247228) — carregaria código de terceiros se a palmeira fosse colocada no mapa. Varredura do jogo inteiro: única ocorrência; nenhuma palmeira PalmD no workspace. Scripts desativados e movidos para `Proto_Restore/Quarentena_Malware` (pode ser excluído).
- **Desempenho:** os modelos `Persistent` faziam o cliente desenhar a vegetação do mapa inteiro (~50 mil peças). Testes A/B no cliente descartaram sombras, pós-efeitos, nuvens, Atmosphere, emissores e scripts; tirar os modelos distantes dobrava o FPS. Novo `StarterPlayerScripts.LOD_Distancia` (só cliente; servidor/colisão perto/streaming inalterados): modelos estáticos de topo saem da cena ao longe e voltam ao se aproximar (grade 512, histerese 300, 250 modelos/quadro). Pequenos (maior peça < 16 studs: flores, capim, arbustos, pedras) além de 1.800; árvores/aglomerados além de 2.600 × 0,45/densidade da Atmosphere do bioma (ar limpo das Planícies → ~6.900, para não abrir buracos na paisagem — a 1ª versão de raio fixo fazia sumir a fileira de pinheiros das encostas; capturas antes/depois). Nunca mexe em modelos com script/som/luz/partícula/prompt, nem na `Arvore_Ancestral`. **Desligar:** atributo `workspace.LOD_Ativo=false`; raios em `LOD_Raio`/`LOD_RaioPequeno`. Medições (mesma sessão, A/B): vista do vale a partir das Montanhas 30,8 → 46 FPS; Deserto 30,6 → 39; vista das Planícies para a Floresta 29,9 → 34–38; 1º tour (raio fixo) Floresta 43→57, Montanhas 33→45, Planícies 39→58, Tundra 31→58. 0 erros com LOD ligado/desligado/religado.
- Luz `Brilho` (ametista, Galeria dos Geodos, Deserto) inteira dentro da rocha → 2 studs para o ar livre (atributo `PosAntesM8_1`).
- Árvore `Floresta_Blender.Exp_Arvores.C1_3.Freixo_A_155` plantada em 35 studs de água e `Capim_Alto_B` submerso 54 num lago das Montanhas → retirados para `Proto_Restore/Retirados_Auditoria_2026_10_26` (atributo `Origem`).
- Flutuantes reais (após descartar peças de construções e itens encostados em rocha): 1 flor do `Chao_Vivo` (+9) reassentada; 2 cristais da Grota do Lagarto (+4) apoiados no chão da gruta (o `Reassentar` os mandou para a superfície acima do teto — desfeito e corrigido com raio curto).
**Capturas:** `SCREENSHOTS/Auditoria_2026_10_26` (Planícies sem LOD / raio fixo reprovado / versão final).
**Observação de medição:** o Studio está aberto há horas com ~26 GB de memória privada (32 GB de RAM) — a sessão inteira ficou ~40% mais lenta que de manhã e os autosaves de 165 MB causam travadas de segundos. **Recomendado reiniciar o Studio** quando o place puder ser salvo com segurança (ver tamanho do place acima). FPS absolutos desta tarde não são comparáveis aos da manhã; só os A/B.
**Não verificado:** celular, multiplayer, servidor publicado (streaming/impostores).
**Pendências mantidas:** cascas finas de leito antigo (invisíveis); tamanho do place (exportação de `Proto_Restore` aguardando autorização).

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

## Próxima tarefa autorizada
**Nenhuma tarefa de alteração do Studio autorizada.** Proposta: M1.1 (plano de arquitetura de dados), a ser aprovado antes de qualquer implementação. Ver plano apresentado na sessão.

## Registro de execução
| Data | Tarefa | Alterações reais | Evidência/teste | Status |
|---|---|---|---|---|
| 2026-10-19 | Montar documentação inicial | Apenas Markdown, fora do Studio | Arquivos criados | Documentação pronta |
| 2026-10-19 | M0 inspeção | Nenhuma no Studio; edição deste arquivo | Saídas de `list_roblox_studios`, `search_game_tree`, `get_console_output` e `execute_luau` (leitura) | M0.1–M0.3 e M0.5 concluídos com evidência; M0.4 parcial (erros verificados, desempenho não medido) |

| 2026-10-19 | M1.3 correções V1–V5 | 6 módulos alterados no Studio, 0 criados | 47/47 testes com DataStore falso (playtest); multi-servidor simulado | Concluído após validação do usuário. Nenhuma outra tarefa iniciada |
| 2026-10-19 | M1.2a perfil/sessão/moeda/inventário/concessões | 17 objetos criados no Studio (6 pastas, 1 RemoteEvent, 9 ModuleScripts, 1 Script) (ver seção M1.2a) | 31/31 testes com DataStore falso; playtest sem erros do projeto | Concluído após aprovação do usuário. M1.2b não iniciado |
| 2026-10-26 | C1 criaturas oficiais | Studio: Catálogo, Ferramentas (rig, animação, pipeline, padrões), 2 lobos em Modelos, Laboratorio_Criaturas, Retirados_C1. Disco: `BLENDER/Criaturas` (10 formas + 1 rascunho), docs | Play/PC com os lobos; reimportação de 11 GLB no Blender; capturas | Parcial: 2 prontas no Studio, 10 aguardando importação manual, 4 pendentes |
| 2026-10-19 | M1.1 arquitetura de dados | Nenhuma no Studio; documentos `DOCS/M1.1-DATA-ARCHITECTURE.md`, `DOCS/BACKUP-STRATEGY.md`, `TASKS.md` | Aprovações do usuário no chat; backup confirmado pelo usuário | M1.1 concluído. Nenhum código implementado |

## Como atualizar após trabalho real
Preencher: objeto/arquivo alterado, resumo, testes executados, resultados, problemas, vínculo com ID da tarefa, commit hash (quando houver), estado de backup, próximo passo esperando autorização. Não afirmar que uma integração funcionou sem a ter testado.

Mensagem de commit sugerida: `docs: registrar resultado da inspeção M0 em PROJECT-STATE`

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

## Teste de geração 3D por IA: Dragão das Montanhas (28/10/2026)
- Pasta isolada `BLENDER/Criaturas/Teste_IA/` (relatório em `RELATORIO-TESTE-IA.md`).
- **Local:** inviável (GPU AMD RX 7600, sem CUDA).
- **Online:** a demo do Hunyuan3D-2 gerou 3 malhas a partir da prancha e do recorte, todas inutilizáveis (cenário fundido, disco, parede, chapa plana). O TRELLIS recusou (cota que exige login).
- **Causa:** a entrada é uma ilustração com cenário; falta uma imagem isolada da criatura.
- **Próximo passo depende do usuário:** recorte limpo ou vistas múltiplas, TRELLIS no navegador dele com login, GPU NVIDIA ou malha comprada/escultor.
- V5, as outras criaturas, o Studio e os backups estão intactos.
- **V6 experimental, teste híbrido da cabeça (28/10):**
  - Cabeça isolada da prancha com máscara poligonal (sem cenário) e enviada ao Hunyuan3D-2 (demo) com a remoção de fundo desligada. Foram três tentativas.
  - A tentativa 3 (cabeça + início do pescoço, máscara longe das bordas, octree 384) deu um crânio detalhado, simétrico (0,3%), com dentes, chifres e cristas.
  - O bloco traseiro espúrio foi cortado no Blender, e a cabeça foi encaixada no osso `Cabeca` da V5 (escala 1,15×, cerca de 11,6 studs de comprimento).
  - Arquivo: `BLENDER/Criaturas/Teste_IA/V6/Dragao_das_Montanhas_V6_experimental.blend`. Comparativo: `V6/Comparativo_V6_cabeca.png`. A V5 está intacta.
  - **Pendências da cabeça:**
    - transição para o pescoço (o encaixe é provisório);
    - mandíbula a separar para articular (a boca está aberta na malha);
    - retopologia de 200 mil para ~8 mil faces, com bake das escamas;
    - materiais.
- **V6, refino da cabeça (28/10):** `Teste_IA/v6_refinar_cabeca.py` sobre o arquivo V6 experimental.
  - Focinho afinado e arredondado; narinas escavadas.
  - Órbitas escavadas, com arcada e pálpebra inferior; olhos amendoados com pupila em fenda e brilho discreto.
  - Nuca cortada atrás dos chifres (a=8,3), sem os restos do bloco.
  - Osso `Mandibula` reposicionado na articulação medida por raios (a=7,0, u=−1,0), com pesos de transição suave. Abre e fecha; a rest pose é com a boca aberta, e o fechamento é de 48°.
  - **Integração ao pescoço não aceita:** a nuca nova (~9×10 studs) é muito maior que o pescoço de primitivas da V5. Requer pescoço novo na fase pescoço/tronco.
  - **Asas (diagnóstico):**
    - ossos em tubo fundidos ao corpo;
    - membrana em leque plano, com borda reta entre as pontas;
    - sem polegar e sem patágio;
    - pesos só nos ossos da asa;
    - pose fixa aberta;
    - escala menor que a referência.
  - Comparativo: `Teste_IA/V6/Comparativo_V6_cabeca_refino.png`.
- **V6, pescoço e asas (28/10):** script `Teste_IA/v6_pescoco_asas.py`.
  - **Pescoço novo:** 36 anéis numa curva de Bézier em S. A base sai da superfície do tórax (raio médio 6,2) e o pescoço afina até a nuca (3,9). Fica costurado aos vértices reais da nuca do Hunyuan, numa superfície única.
    - Tem crista óssea dorsal, relevo muscular e 259 entre placas e cristas que seguem a pele.
    - Os ossos do pescoço foram reposicionados na curva, e o giro do pescoço foi testado.
  - **Mandíbula:** o teste medido corrigiu o sentido de fechamento.
    - A 48° os dentes se encaixam com cerca de 5% de penetração dos dentes inferiores.
    - A 56° a penetração chega a 14%.
    - O fechamento máximo recomendado é 48°.
  - **Asas reconstruídas:**
    - ossos orgânicos: úmero, antebraço, metacarpo, 4 dedos curvos e polegar com garra;
    - membranas com barriga de tensão, borda de fuga em arco irregular, membrana do dedo 4 até o flanco e patágio do ombro ao pescoço;
    - espessura de 0,14;
    - envergadura proposta de 62 studs (provisória).
  - **Interseção de membrana dentro do corpo:**
    - asa direita: 0–0,5%;
    - asa esquerda: 3–5%, porque a membrana do flanco nasce dentro do tronco nos dois lados (a medida da esquerda inclui essa base).
  - **Limitações:**
    - o tronco e as patas ainda são da V5 (primitivas);
    - na pose recolhida, a asa ainda abre para cima (o rig precisa de mais rotação no úmero);
    - asas com 164 mil tris cada (antes da retopologia);
    - sem materiais.
  - Comparativo: `Teste_IA/V6/Comparativo_V6_pescoco_asas.png`.
- **Dragão V7 experimental (28/10):** `Teste_IA/v7_dragao.py`, gerado a partir da V6 (intacta). Arquivo: `Teste_IA/V7/Dragao_das_Montanhas_V7_experimental.blend`.
  - **Tronco e patas novos:**
    - volumes musculares alongados unidos por voxel e suavização Laplaciana;
    - peito com quilha e peitorais de voo;
    - pata dianteira com o cotovelo para trás; pata traseira com joelho para a frente e jarrete;
    - 4 dedos com garras em cada pata.
  - **Costura:** o tronco foi costurado ao pescoço V6 (laços de 208 e 324 vértices, 532 faces), formando uma superfície única.
  - **Escamas:** 6.467 escamas de tamanho e forma variados (maiores no dorso, menores nas articulações), 416 escudos ventrais e 47 cristas contínuas do pescoço à cauda.
  - **Asas:**
    - corda maior;
    - membrana presa ao quadril;
    - envergadura de 63;
    - recolhimento deitado no dorso.
  - **Testes:**
    - passo: p99 de 1,76 e 0,94% das arestas acima de 1,8×;
    - pescoço e cauda: p99 de 1,21;
    - batida e recolhimento das asas não deformam o corpo;
    - membrana dentro do corpo: cerca de 7%, constante em todas as poses (é a raiz embutida no tronco, não colisão);
    - apoio no chão: mãos em 0,011 e pés em −0,01.
  - **Limitações:**
    - a silhueta oficial é ereta (tórax alto, pescoço vertical, asas para cima), e a V7 está em postura horizontal: é diferença de pose, a ajustar no rig;
    - corpo com 287 mil tris e escamas com 83 mil, antes da retopologia;
    - a superfície do tronco ainda é lisa e procedural, sem escultura;
    - nada foi testado no Roblox.
- **Dragão V8 experimental (28/10):** `Teste_IA/v8_dragao.py`, a partir da V7, que continua intacta. Arquivo: `Teste_IA/V8/Dragao_das_Montanhas_V8_experimental.blend`.
  - **Postura ereta só pelo rig** (a malha neutra não muda):
    - raiz recua e desce;
    - coluna ergue o tórax (6° e 2°);
    - pescoço em S vertical, com a cabeça nivelada;
    - cauda curva;
    - as quatro patas são assentadas por IK temporário com correção de altura e depois gravadas na pose.
  - **Asas:** envergadura de 99,8 studs (escala de 1,69 a partir do ombro). Ossos e articulações 30% mais grossos, mais divisões na membrana, curvatura e espessura de 0,2.
  - **Três poses de asa:** imponente (erguidas e parcialmente abertas), voo (estendidas) e repouso (recolhidas no dorso).
  - **Testes:**
    - apoio na postura ereta: mãos a +0,06, pés a −0,03;
    - esticamento: ereta p99 1,51; cauda e pescoço virados p99 1,55; corpo baixo p99 1,65 (patas apoiadas);
    - membrana dentro do corpo: cerca de 4,5–5% e constante em todas as poses, ou seja, é a raiz embutida, não colisão.
  - **Limitações:**
    - asas com 132 mil tris cada, antes da retopologia;
    - no repouso, as asas recolhidas passam da cauda (são compridas);
    - a membrana não tem veios (fica para o material);
    - nada foi testado no Roblox.
- **Dragão V9, produção (28/10):** retopologia, UVs, bake e PBR sobre a V8 aprovada, que continua intacta.
  - Arquivos: `Teste_IA/V9/Dragao_das_Montanhas_V9.blend` e `Dragao_das_Montanhas_V9.glb` (4,1 MB). Scripts: `v9_dragao.py`, `v9_fix.py`, `v9_fix2.py`, `v9_render.py`.
  - **Corpo:** voxel → Quadriflow → shrinkwrap, com 17.456 tris (antes 374 mil). Pesos transferidos da malha alta.
  - **Asas:** 9.500 tris cada. Cristas com 6.000, garras com 3.000. Total de 47.568 tris; nenhuma malha passa de 20 mil.
  - **Mapas do corpo:** normal assado só da pele alta (cabeça Hunyuan e musculatura), somado ao relevo de escamas procedural de tamanho variável, mais AO, cor, rugosidade e emissão (fissuras só nas juntas, em manchas, no peito, ventre e flancos), todos em 2048. A casca de escamas de geometria contaminava o bake (AO preto, normais tortas) e saiu do bake. A malha alta fica na coleção oculta `V9_ALTA_bake`.
  - **Asas:** nervuras, espessura (mais fina e quente longe dos ossos), desgaste e rugosidade, em 1024.
  - **Recolhimento:** em leque (dedos dobram no meio). A ponta máxima ficou em y = 45,4, e a membrana estica no repouso (p99 2,5).
  - **Deformação na malha leve:**
    - corpo ereto p99 1,52; pescoço 1,62; cauda 1,55; mandíbula fechada 1,57;
    - asas: imponente p99 1,75, voo 1,0, batida 1,05.
  - **Apoio:** −0,02 a −0,06.
  - **GLB:** reimportado no Blender com 11 malhas, 48 ossos e 13 imagens. As ações antigas do rig V5 foram removidas.
  - **Limitações:**
    - as escamas parecem rocha rachada, não escamas sobrepostas;
    - as nervuras da membrana formam uma rede poligonal, não nervuras radiais;
    - o recolhimento ainda é longo;
    - a cabeça leve perde volume dos dentes (o detalhe vem só do mapa normal);
    - o SurfaceAppearance do Roblox não tem emissão (as fissuras ficam como cor clara);
    - nada foi testado no Roblox.
- **Dragão V10 (28/10):** `Teste_IA/v10_dragao.py` + `v10_split.py` + `v10_render.py` + `v10_poses.py`, a partir da V9 (intacta). Arquivos: `Teste_IA/V10/Dragao_das_Montanhas_V10.blend` e `.glb` (12,7 MB).
  - **Cabeça:** malha própria tirada da cabeça alta do Hunyuan e reduzida para 16 mil tris. Tem dentes, chifres, narinas, órbitas e bordas da mandíbula em geometria. No corpo, o pescoço recua 0,08 na faixa de sobreposição para evitar z-fighting.
  - **Escamas 3D:**
    - 4 malhas de placas sobrepostas nas regiões de destaque, com tamanho, orientação e espessura variados, entre 10,3 e 13,8 mil tris cada;
    - relevo em "telha" (borda de trás levantada) e microdetalhe no mapa normal;
    - fissuras só nas juntas, em manchas.
  - **Asas:** nervuras radiais a partir do pulso, com ramos longe dele; membrana escura, avermelhada nas áreas finas; sem emissão.
  - **Recolhimento novo:** antebraço para a frente e dedo distal dobrado. A ponta foi de 45,4 para 24,5 studs para trás, e a tração da membrana caiu de p99 2,5 para 2,09/1,94.
  - **Testes:**
    - corpo ereto p99 1,54; cabeça 1,33;
    - **mandíbula fechada na cabeça nova: p99 2,12 (1,6% das arestas) — precisa ajuste de pesos;**
    - asa imponente 1,64–1,67, voo 1,0;
    - apoio de −0,01 a −0,06.
  - **Malhas:** 15, a maior com 16.294 tris; 111 mil tris no total. O GLB reimporta no Blender com 48 ossos e 20 imagens. Cristas e garras não têm UV (cor sólida).
  - **Pendências:**
    - fissuras quase invisíveis (menos que na referência);
    - GLB grande por causa das texturas de 2048 (o Roblox reduz para 1024);
    - pesos da mandíbula;
    - nada foi testado no Roblox.
- **V10, correções antes do Roblox (28/10):** `Teste_IA/v10_fix.py`.
  - **Mandíbula:** a suavização da proporção Mandíbula/Cabeça mudou pouco (p99 de 2,19 para 2,10; cerca de 1,9% das arestas). A causa é a boca esculpida aberta, que comprime os cantos ao fechar; os pesos não resolvem. Correção real: pose de descanso com a boca fechada ou ângulo máximo menor.
  - **Fissuras:** reforçadas (juntas mais largas, mais regiões, emissão 4). Visíveis no peito, pescoço e base da cauda.
  - **GLB:** reexportado com texturas de 1024 (10,7 MB). Reimportação no Blender: 15 malhas, máximo de 16.294 tris, 48 ossos, 20 imagens. O `.blend` mantém 2048.
  - Instruções de importação: `Teste_IA/V10/PILOTO-ROBLOX-DRAGAO-V10.md`.
  - **Studio:** aguarda a importação manual do usuário num place vazio.
- **V10, boca fechada em repouso (28/10):** `Teste_IA/v10_boca.py`.
  - A forma fechada (48°) virou a geometria de descanso das malhas com peso na mandíbula. O osso `Mandibula` girou junto no rig, e 1.250 vértices dos cantos foram relaxados.
  - **Abrir:** a 24° p99 1,41 (0% das arestas acima de 1,8×); a 40° p99 1,87 (1,2%); a 48°, igual à boca original, p99 2,17.
  - Recomendação: abertura máxima de cerca de 35–40° nas animações.
  - Renders em `Teste_IA/V10/Boca_V10_fechada_aberta.png`. GLB reexportado com texturas de 1024 (10,7 MB).
  - **Pendente:** a cabeça está brilhante demais (rugosidade baixa) sob luz neutra; nada foi testado no Roblox.
- **V10, brilho da cabeça (28/10):** `Teste_IA/v10_brilho.py`.
  - Rugosidade da cabeça remapeada para 0,68–0,9 (mediana de 0,67 para 0,83) e especular reduzido para 0,3: o aspecto de plástico sumiu.
  - Cor da cabeça clareada 1,42× (cabeça e corpo já tinham o mesmo tom de base) para se aproximar das placas.
  - Normais e mapa normal conferidos e corretos.
  - Sob luz neutra, a cabeça ainda parece mais escura e lisa que o corpo, porque não tem placas 3D. A referência também mostra a cabeça negra.
  - GLB reexportado com texturas de 1024 (10,6 MB). Pronto para o teste no Roblox.
- **Teste no Roblox Studio, Place1 descartável (28/10).** Inspeção só em leitura; o rpg_roblox não foi tocado.
  - Envergadura de 100 studs, frente em −Z, 48 Bones, AnimationController, 14 MeshParts aceitas, SurfaceAppearance com cor, normal e rugosidade no corpo, cabeça, placas e asas.
  - **Problemas:**
    - garras, cristas e olhos ficaram brancos (o Import 3D ignora cor sólida sem textura);
    - nomes internos nas peças;
    - origem 6,6 studs acima do baseplate;
    - peças não ancoradas;
    - FPS não medido.
  - **Correção (`Teste_IA/v10_roblox_fix.py`):** UV e textura de 128 px para garras, cristas, olhos e pupilas; malhas com o mesmo nome dos objetos; armature renomeada para "Dragao_das_Montanhas". GLB reexportado (11 MB).
  - **Pendente:** o usuário reimporta no Place1 para conferência.
- **Place1 (descartável), arrumação e desempenho (28/10), com autorização do usuário:**
  - modelo antigo apagado; o novo foi renomeado para `Dragao_V10`, encostado no chão (minY = 0) e com RootPart ancorado;
  - 2 cópias para o teste.
  - **FPS em Play (RenderStepped, 5 s, mesmo PC):**
    - 1 dragão: 60;
    - 3 dragões: 60, sem quadros abaixo de 40.
    - O Studio limita a 60 FPS, então o resultado mostra que não há queda, não o FPS máximo real.
  - Captura com o avatar mostra escala colossal correta e pés no chão.
  - **Não medido:** celular nem o mapa completo.
  - O Place1 não foi salvo pelo assistente e continua com 3 dragões.
- **Dragão V11 (28/10):** `Teste_IA/v11_dragao.py`, a partir da V10 (intacta). Arquivos: `Teste_IA/V11/Dragao_das_Montanhas_V11.blend` e `.glb` (33 MB, PNG com alfa).
  - **Corpo dividido em 5 peças** (pescoço, tronco, patas dianteiras, patas traseiras, cauda), cada uma com UV e mapas próprios. A densidade de textura no Roblox fica cerca de 5× maior.
  - **Escamas:** grandes, com fendas entre elas de 8 a 16% da área. As fendas são transparentes (alfa) e têm borda em brasa.
  - **Núcleo de lava:** 6 malhas recolhidas com material `NEON_Lava`, que viram Neon no Roblox.
  - Cristas em basalto escuro com ponta em brasa; garras escuras.
  - **Total:** 24 malhas, a maior com 16 mil tris; 122,7 mil tris no total.
  - **Roblox:** script de configuração em `Teste_IA/V11/configurar_roblox_v11.luau` (Neon nos núcleos, AlphaMode Transparency nas peles, Bloom só no place de teste). Aguarda o usuário importar no Place1.

## Dragão das Montanhas V12 (2026-10-28) — Blender, ainda não testado no Roblox
- Origem: a V11, que permanece intacta. Script: `BLENDER/Criaturas/Teste_IA/v12_dragao.py` (+ `v12_mascara.py`, `v12_render.py`).
- Corpo: 15% mais estreito no eixo X; as asas acompanham.
- Cabeça: 35% maior e 20% mais alta, com transição suave na nuca; o rig acompanha. O núcleo Neon da cabeça foi refeito com recuo de 0,4 (o antigo atravessava a pele).
- Defeito encontrado na V11: as texturas de cor foram criadas sem canal alfa (`img()` usa `alpha=False`), então as fendas transparentes nunca existiram de fato.
  - Na V12 a máscara foi reassada do shader procedural da V11, e a cor foi gravada com alfa real (32 bits).
  - As fendas foram alargadas (cabeça 10→23%, corpo 12–16→18–39%), com halo de brasa.
- GLB: `V12/Dragao_das_Montanhas_V12.glb` (34,6 MB). Comparativo: `V12/Comparativo_V11_V12.png`.
- Limitação: no render do Blender (AgX) o núcleo aparece quase branco. O resultado real precisa ser verificado no Roblox (Neon laranja + Bloom).
- Pendente: importar no Place1, rodar `V12/configurar_roblox_v12.luau`, fazer capturas e medir FPS.
- Ajuste (mesma data): fendas da cabeça afinadas (só o miolo da máscara, 7,3% da área; halo curto). As escamas da cabeça agora ficam legíveis. Pendência visível: os dentes brilham, porque o núcleo aparece pela boca.
- Suavização (mesma data), a pedido ("parece blocos"):
  - corpo com 1 nível de subdivisão (7k–18,6k tris por peça, abaixo de 20k);
  - cabeça com Laplacian 12× preservando volume;
  - **placas 3D de escamas removidas** (≈49k tris), que eram a causa da silhueta em blocos;
  - relevo dos mapas normais reduzido a 45%, gravado na própria imagem;
  - núcleos Neon refeitos a partir das peças suavizadas.
  - GLB: 22,1 MB. Imagem: `V12/V12_suave.png`.
- Pendente: boca/dentes ainda com fragmentos irregulares e brilhantes; teste no Roblox (Place1) ainda não feito.

## Dragão V13 — etapa 1, proporções (2026-10-28), só Blender
- Script `v13_proporcoes.py` (a partir da V12): pescoço em S, tronco a 74%, pernas 1,3× mais longas e mais finas, cauda 1,3× mais longa e afinando. A postura foi gravada como pose de descanso. Arquivo: `V13/Dragao_das_Montanhas_V13.blend`; painel `V13/b_painel.png`.
- Avaliação honesta: a silhueta melhorou, mas segue longe da referência (dragão de fogo esguio). A base V7 (quadrúpede robusto) e a cabeça da IA arredondada limitam o que se consegue por deformação.
- Proposta: nova malha-base gerada a partir de uma imagem limpa da referência (dragão inteiro, fundo liso), por imagem-para-3D; depois retopologia, rig, lava e Roblox no pipeline atual. Aguarda decisão e material do usuário.
- Não exportado para GLB; Roblox não alterado.

## Dragão V14 — malha do Meshy (2026-10-28)
- O usuário gerou no Meshy 7.1 (multivista, licença Private) a partir de 3 imagens do ChatGPT (perfil, frente, costas), salvas em `V14/ref_*.webp`. GLB original: `V14/Meshy_Dragao_original.glb`.
- Inspeção (`v14_inspecionar.py`): 1 malha fechada, 1,08 M tris, **sem UV e sem textura**.
  - A forma está fiel: cabeça com chifres, pescoço em S, pernas finas, asas com dedos.
  - Diferença: no perfil o tronco ficou mais curto e o dragão mais erguido que na imagem; a cauda faz curva.
- Próximo: textura (no Meshy ou pela pele de lava própria), separar asas/corpo, retopologia abaixo de 20k por peça, rig, Roblox.
- V14 texturizado (Meshy, `V14/Meshy_AI_Inferno_Dragon_1028195138_texture.glb`): cor, metal/rugosidade e normal em 2048; fiel às imagens de referência.
- `v14_roblox.py`:
  - soldou as costuras;
  - escala de envergadura 100 studs (comprimento 53, altura 52), pés em z=0, cabeça para −Y;
  - reduziu para 95k tris mantendo as UVs do Meshy;
  - normal assado da malha alta;
  - 7 peças (11,4k–16,2k tris cada).
  - Saída: `V14/roblox/Dragao_das_Montanhas_V14.glb` (3,0 MB, texturas 1024) e `.blend`.
- Renders do GLB reimportado no Blender conferem (`V14/roblox/render/painel_v14_roblox.png`). Isso não é validação no Roblox.
- Pendente:
  - importar no Place1 e rodar `V14/roblox/configurar_roblox_v14.luau`, com capturas e FPS;
  - rig e animação (o modelo ainda é estático);
  - brilho extra (Neon/Bloom).
- V14 alongado (mesma data, pedido "esticar para trás"): o tronco ganhou +9 studs na faixa y −12…2 (comprimento total 53→62 studs).
  - Asas e cauda foram identificadas por conectividade da malha (inundação a partir das pontas, barreira em |x|<11). As asas ficam presas ao ombro; a cauda anda inteira com o quadril.
  - Duas tentativas por posição foram descartadas porque rasgavam a membrana e a cauda.
- GLB atualizado em `V14/roblox/`; a versão sem alongamento ficou em `V14/roblox_v1/`. Comparativo: `V14/roblox/Comparativo_alongamento.png`.
- **Teste no Place1 (2026-10-28), feito com o Studio MCP:**
  - O usuário importou o V14 alongado. Chegaram 7 MeshParts, todas com SurfaceAppearance (cor, normal e rugosidade).
  - O modelo foi renomeado para `Dragao_V14`, ancorado, com CanCollide desligado, assentado no chão (base y=0) e centralizado em (0, −45), longe dos V10. Tamanho no Roblox: 100 × 52,3 × 62,4 studs.
  - Capturas: `V14/roblox/capturas/`.
  - FPS no Play (cliente, RenderStepped, 5 s): **60** com 1 V14 (+3 V10 na cena) e **60** com 3 V14 (as 2 cópias eram temporárias, só durante o Play). O Studio limita a 60, então não é medida em celular.
- Pendente: rig e animação (o modelo é estático), Bloom opcional e teste em celular.
- Brilho leve no V14 (mesma data):
  - faces de fogo detectadas pela cor da textura (27% das faces, filtro de maioria) e copiadas 0,06 stud para fora como película `V14_Brilho_a/b` (25,8k tris, 2 peças);
  - GLB atualizado em `V14/roblox/` (3,5 MB); a versão anterior ficou em `V14/roblox_v2_sem_brilho/`;
  - `configurar_roblox_v14.luau` transforma a película em Neon (255,110,25) com Transparency 0,72 e Bloom suave (0,5 / 24 / 0,95), e substitui o Dragao_V14 antigo.
  - Aguarda reimportação no Place1.
- Película refeita por pedido ("falhado"): nota de fogo por vértice, suavizada pela malha (6 passadas), furos fechados e ilhas com menos de 120 faces removidas. Agora contínua: 31% das faces, 29,8k tris. GLB atualizado em `V14/roblox/`; prévia em `V14/roblox/render/painel_brilho.png`.
- Película v3: nas asas (identificadas por conectividade na malha baixa) entra toda a membrana que não seja osso/borda preta (lum > 0,075). Ficou contínua, sem as manchas escuras: 44% das faces, 41,9k tris, 3 peças. GLB atualizado em `V14/roblox/`.
- Película v4 (pedido "por cima do preto"): só o fogo vivo da textura (asas r>0,72 e g>0,3; corpo laranja), sempre fora das faces escuras, com suavização leve. Cobre 26% das faces (25k tris) e segue o desenho da textura. GLB atualizado em `V14/roblox/`.
- **Brilho aplicado no Place1 (Studio MCP):** o usuário reimportou; o script substituiu o Dragao_V14 antigo, deixou 9 peças ancoradas e transformou 2 películas em Neon (255,110,25) com Transparency **0,8** (0,72 ficava forte demais e achatava a textura do ventre), além do Bloom_Dragao suave. Captura: `V14/roblox/capturas/place1_v14_brilho.jpg`. O FPS não foi medido de novo (a película somou 25k tris).
- **FPS com brilho (Place1):** a medição deu 15 FPS, mas o valor foi o mesmo **sem o dragão e sem Bloom/película**. Era o Studio em segundo plano (limitado), então a medida é inválida. Refazer com a janela do Studio em foco.
- **Rig V14** (`v14_rig.py`, executado dentro do `v14_roblox.py` antes de dividir em peças):
  - 40 ossos medidos na própria malha: Raiz, Quadril, Coluna1–3, Pescoço1–4, Cabeça, Cauda1–8, 4 patas × 3, 2 asas × (Asa_1, Asa_2, Dedo1–3);
  - pesos por região (asa, pata, cauda solta, corpo) por distância ao osso, 3 influências, normalizados; a película herda a região do vértice mais próximo;
  - GLB com skin: `V14/roblox/Dragao_das_Montanhas_V14.glb` (5,0 MB).
  - Teste de poses no Blender (`v14_teste_rig.py`, `V14/roblox/rig_teste/painel_rig.png`): asas para cima e para baixo, pescoço, cauda e pata deformam sem rasgos visíveis nessa escala.
  - Sem mandíbula (boca não abre) e sem animações ainda. Não testado no Roblox.
- A versão anterior sem rig ficou em `V14/roblox_v3_sem_rig/`.
- **V14 com rig no Place1 (Studio MCP):**
  - Reimportado: 10 peças e **40 Bones**. A configuração substituiu o Dragao_V14 anterior (Neon 0,8 e Bloom mantidos, chão y=0).
  - Skin verificado no Edit com Bone.Transform (asas, pescoço, cauda): a malha e a película deformam juntas. Pose desfeita depois. Captura: `V14/roblox/capturas/place1_v14_rig_pose.jpg`.
  - **FPS com o Studio em foco:** 60 com 1 V14, 60 sem ele, e **60 com 3 V14 batendo as asas** (Transform procedural a cada quadro). As cópias foram temporárias, só durante o Play. O Studio limita a 60; o celular não foi testado.
- Pendente: mandíbula, animações reais (voo, andar, rugido, ataque), teste em celular e decidir se os 3 Dragões V10 saem do Place1.
- **Animações do V14 (Place1, Studio MCP):** 4 KeyframeSequences em `Workspace.Dragao_V14.Animacoes`, geradas por Luau.
  - Os eixos são do modelo (arfagem, guinada, batida das asas), convertidos para o espaço local de cada osso; a hierarquia de Poses é RootPart > Raiz > …
  - **Parado** (4 s, laço): respiração, pescoço e cauda ondulando.
  - **Andar** (1,6 s, laço): passada diagonal, tronco sobe, cauda balança.
  - **Voo** (1,2 s, laço): batida ±38°, antebraço e dedos defasados, patas recolhidas, corpo oscila.
  - **Rugido** (3 s): recolhe, avança com asas abertas e cabeça erguida.
- Tocadas no Play com AnimationClipProvider:RegisterAnimationClip + Animator e conferidas por captura (`V14/roblox/capturas/anim_*.jpg`) e pela posição dos ossos (a ponta da asa oscila de 36 a 52 no Voo).
- Correção: no Andar a ponta da asa atravessava o chão; agora a asa sobe +8°.
- FPS com Animator: 15, mas inválido (Studio fora de foco). Com o Studio em foco já havia dado 60 com 3 dragões e asas animadas.
- Limitações:
  - sem mandíbula (o rugido não abre a boca);
  - o Voo foi feito para o dragão no ar (no chão a asa desce abaixo do piso);
  - para o jogo real é preciso publicar as animações (AnimationId) e salvar o Place1 no Studio;
  - nada foi levado ao place principal.
- **Mandíbula (rig V14, mesma data):**
  - O osso da Cabeça foi corrigido: antes apontava para a ponta do chifre (ponto geodésico mais distante); agora vai da nuca ao focinho.
  - Novo osso `Mandibula` (filho de Cabeça), com a dobradiça atrás do canto da boca. A linha da boca foi medida em vista ortográfica: do focinho a +6,4 Y / +1,7 Z.
  - A malha do Meshy tem os lábios fundidos: `cortar_boca` separa as arestas na linha da boca (106 na pele, 75 na película). O lábio inferior vai para a Mandíbula com transição na dobradiça.
  - Cavidade `V14_Boca` (elipsoide vermelho-escuro, 528 tris) com metade na Cabeça e metade na Mandíbula.
  - Teste no Blender com 22° (`rig_teste/painel_boca.png`): a boca abre e mostra a cavidade, sem bolsa esticada.
  - 41 ossos; GLB atualizado.
  - O script do Roblox agora move a pasta Animacoes do modelo antigo para o novo.
  - Pendente: reimportar e incluir a Mandíbula no Rugido (no Studio).
- **Dentes (V14, mesma data):** objeto `V14_Dentes` com 360 tris: 2 fileiras × 2 lados de cones ao longo da linha da boca, recuados da borda do lábio, com presas maiores na frente e textura degradê marfim. Os de cima estão na Cabeça e os de baixo na Mandíbula. Teste no Blender (`rig_teste/painel_boca.png`): com a boca aberta aparecem as duas fileiras e a cavidade escura; fechada, as pontas ficam à mostra sobre os lábios, como na referência. GLB atualizado; falta reimportar.
- **Gengivas (mesma data, pedido "dentes fora da gengiva"):** prismas vermelho-escuros ao longo de cada lábio, no mesmo objeto `V14_Dentes` (coluna 0 da textura). Os dentes foram encaixados com a raiz 0,4 dentro da gengiva, a 0,35 da borda do lábio. Total de 864 tris. Teste no Blender: os dentes saem da gengiva com a boca aberta. GLB atualizado; falta reimportar.
- Correção dos dentes: os cones estavam invertidos (ponta dentro da gengiva). Agora `rotation_difference(dirv)` deixa a base na gengiva e a ponta para fora. Conferido no Blender (`rig_teste/painel_boca.png`); GLB atualizado.
- Dentes v3 (pedido "sem gengiva aparente, dentes enfiados"): gengiva desligada (`GENGIVA = False`). Os dentes ficam na borda do lábio (0,15 para dentro), com a raiz só 0,15 dentro do lábio. Com a boca fechada as pontas se cruzam por fora, como em crocodilo. 360 tris. GLB atualizado; falta reimportar.
- Dentes v4 (pedido "não parecem ser dele"): dentes orgânicos feitos à mão com bmesh, em seção de lâmina achatada (0,6), curvados para trás e para dentro, com tamanho e espaçamento variados (semente 14) e presas na frente. Cor em degradê da raiz escura e chamuscada até a ponta osso amarelado, no tom dos chifres. 34 dentes, 1564 tris. Conferido no Blender; GLB atualizado; falta reimportar.
- **Mandíbula e dentes no Place1 (Studio MCP):**
  - Reimportado: 12 peças, 41 Bones, com `V14_Dentes` e `V14_Boca`. A configuração moveu a pasta Animacoes para o modelo novo e reaplicou Neon 0,8 e Bloom.
  - As 4 KeyframeSequences foram **regeradas no rig novo**, porque o osso da Cabeça e o pescoço mudaram:
    - Rugido com a boca abrindo até 26° (pico entre 1,0 e 2,2 s);
    - Parado com a boca entreabrindo 1,5° na respiração.
  - Conferido no Play com o Rugido congelado em 1,55 s: a boca abre, com dentes de cima e de baixo e cavidade escura. Capturas: `V14/roblox/capturas/anim_rugido_boca_aberta.jpg` e `anim_rugido_geral.jpg`.
  - Pendente: salvar o Place1 (Ctrl+S) e publicar as animações para obter AnimationIds no jogo real.

## Boca, Fase 1 de animações e VFX das asas — V14 (2026-10-28)
**Boca (Blender, `v14_rig.py`)**
- Interior refeito (`V14_Boca`): cavidade com palato (sulcos), garganta escurecendo e textura com ruído orgânico; língua no assoalho; gengivas internas que ficam escondidas com a boca fechada.
- Dentes: a fileira de baixo vai por dentro da de cima e intercalada, para não se cruzarem.
- Comparativos (fechada, meia, aberta × lado, frente, 3/4, close): `V14/roblox/boca_comparativo/comparativo_boca.png`.
- A versão anterior ficou em `V14/roblox_v4_boca_anterior.glb`.
- Pendente: a boca nova **ainda não foi reimportada no Roblox**. O Place1 está com a versão anterior; os ossos são os mesmos.

**Conversão Blender→Roblox validada:** os eixos de todos os ossos conferidos são M·Blender, com M: (x,y,z)→(−x,z,y). A rotação local é idêntica.
- No Play, o pé dianteiro esquerdo subiu 1,59 e percorreu 4,24 studs, contra 1,60 e 4,24 no Blender.

**Fase 1 (`v14_anim_lib.py`, `v14_fase1.py`, `v14_anim_render.py`)**
- 13 clipes, com pés por IK assados em FK e pernas com folga para não sair do chão:
  - Idle_Neutro 6 s; Idle_Alerta 3 s; Idle_Alerta_Mantido 4 s; Idle_Imponente 6 s;
  - Andar 2 s (3,2 studs/s); Andar_Lento 2,8 s (1,6 studs/s); Andar_Inicio 2 s; Andar_Parada 2 s;
  - Correr 0,93 s (13 studs/s); Curva_E/D 2 s (±14°/s); Giro_E/D 2,4 s (±22°/s).
- Asas recolhidas por giros espelhados. As versões anteriores (apontar o osso) ficavam assimétricas por causa da torção dos ossos do rig.
- Pés medidos no Blender:
  - idles: ±0,02;
  - andar: sobe 1,60, apoio a 3,2 studs/s;
  - correr: sobe 3,0;
  - afundamento máximo 0,04.
- No Play do Place1, com o dragão andando a 3,2 studs/s, o deslize do pé de apoio ficou em 0,20–0,26 studs por passada (inclui replicação).
- Prévias: `V14/anim/fase1/previas/` (MP4 3/4, quadros lado e 3/4, pranchas). JSON: `V14/anim/fase1/json/`.
- Os KeyframeSequences estão em `Workspace.Dragao_V14.Animacoes` no Place1. Importador: `V14/anim/importar_clipe.luau`, via HttpService em 127.0.0.1; **HttpEnabled foi ligado no Place1**.
- Limitações:
  - sem pálpebras (não há piscar);
  - curvas e giro são clipes no lugar: o controlador do jogo aplica a rotação/translação informada nos atributos do clipe;
  - Fases 2–5 não feitas.

**VFX das asas (Place1)**
- Arquivos: `V14/vfx/ConfigAsas.luau` (por forma), `EfeitosAsas.luau` (lógica) e `EfeitosAsas_Cliente.client.luau`.
- Instalados com o ScriptEditorService em `ReplicatedStorage.VFX_Dragoes` e `StarterPlayerScripts`. Atribuir `.Source` direto deixava o LocalScript sem rodar no Play.
- Funcionamento:
  - emissores pré-criados em ossos de ponta e meio dos dedos (Bones sem peso), mais poeira nos pés;
  - disparo por marcadores (WingDownstrokeStart/Peak, WingUpstroke, WingGlide, WingFold, TakeoffImpulse, LandingImpact), com o estado no Value do marcador;
  - pulso no brilho da película;
  - LOD por distância e qualidade gráfica, teto de 90 partículas/s por dragão;
  - poeira só em materiais de solo adequados.
- Demonstração com marcadores no clipe de voo antigo (Dragao_V14_Voo):
  - Montanhas no V14;
  - Glacial e Sombrio em cópias temporárias do V14 dentro do Play, porque **não existem modelos desses dragões** (no place principal há só pastas de território do Glacial).
  - Capturas: `V14/vfx/capturas/`.
- **FPS 59,6** com 3 dragões batendo asas e 96 emissores, com o Studio em foco.
- Pendentes:
  - decolagem, pouso, planeio e batida forte dependem dos clipes da Fase 2;
  - o efeito do Glacial ficou muito sutil contra o céu claro;
  - teste com montaria e em celular não feito.

**Place1:** precisa ser salvo no Studio (Ctrl+S). Nada foi alterado no place principal; nele houve só leitura.
- **Cauda (pedido "mexer mais, para trás", mesma data):**
  - Nova pose-base `cauda_para_tras` em todos os 13 clipes: desce saindo do quadril (inclinação 0,25) e nivela até a ponta, preservando 15% da curva original.
  - Balanço aumentado: andar 7→13, lento 5→10, correr 4→8, idles 3→6,5; onda vertical 1,2→2,2.
  - Corrigido o sinal de "cauda_ergue" (antes abaixava).
  - Medido no Blender: ponta da cauda sempre acima do chão (mín. 1,5 studs em Giro_E) e alcance de ~77 studs para trás.
  - Clipes reimportados no Place1 e conferidos no Play (`V14/anim/fase1/capturas_roblox/cauda_para_tras_andar.jpg`).

## Fase 2 (voo) e corrida melhorada — V14 (2026-10-28)
- `v14_fase2.py`: 9 clipes.
  - Clipes: Voo 1,2 s; Voo_Rapido 0,9 s; Planeio 4 s; Curva_Aerea_E/D 2,4 s (±35°/s); Subida 1,2 s; Descida 1,2 s; Decolagem 3 s; Pouso 3 s.
  - Altura de voo: 14 studs (atributo `altura_voo`).
  - Batida das asas: descida mais rápida que a subida; úmero conduz, antebraço e dedos atrasados; dedos dobram na subida e abrem na descida.
  - Corpo reage à batida (tórax, pescoço que compensa, cauda ondulando). Patas recolhidas em voo.
  - Curvas: inclinação do corpo e asas assimétricas.
  - Decolagem: agacha, abre as asas, impulso e 1ª batida forte, recolhe as patas. Pouso: batidas de frenagem, patas estendem, impacto e compressão, asas recolhem.
- Marcadores gravados no JSON e criados como KeyframeMarker na importação (Value = estado, ex. "Decolagem|forte"): Voo 3, Curvas 6, Decolagem 7, Pouso 7.
- Testado no Play do Place1:
  - Decolagem → Voo: os marcadores chegaram ao cliente nos tempos certos e as brasas foram emitidas;
  - Pouso → Idle_Neutro: pés exatamente no chão (0,00).
  - Capturas: `V14/anim/fase2/capturas_roblox/`. Prévias e MP4: `V14/anim/fase2/previas/`.
- Corrida:
  - novo galope de corpo inteiro: gangorra do tronco, coluna enrola e estende, fase de suspensão, pescoço/cabeça contrabalançando, cauda com atraso;
  - novo clipe Correr_Frenagem (2 s): o corpo comprime e joga o peso para trás, a cauda sobe.
  - Pés no Blender: apoio a 0,00, sobem até 3,18.
  - No Play, movendo a 13 studs/s: deslize de 0,35–0,59 stud por apoio. Os dois clipes já estão no Place1.
- Limitações:
  - decolagem de precipício, mergulho e voo montado não foram feitos;
  - root motion fica com o controlador do jogo (altura e velocidade nos atributos dos clipes);
  - o Place1 precisa ser salvo (Ctrl+S).

## Fase 3 — comportamentos naturais V14 (2026-10-28)
- `v14_fase3.py`: motor de poses-chave (chaves herdadas, interpoladas com suavização) com camadas secundárias de respiração, olhar com ruído, cauda com atraso, farejar, mastigar e engolir.
- Alturas calibradas na própria malha por busca binária:
  - focinho no chão para comer (2,6) e beber (1,0);
  - focinho na altura do jogador (6) para o dono;
  - barriga no chão ao deitar (baixa 10,5).
  - As patas avançam (dianteiras) e recuam (traseiras) automaticamente conforme o corpo desce, e levantam ao se reposicionar.
- 25 clipes: Comer 8 s, Comer_Mastigar 2,4 s (laço), Beber 9 s, Beber_Loop 2,4 s, Deitar 4,5 s, Deitado_Acordado 8 s, Dormir 8 s, Adormecer 3 s, Acordar 4,5 s, Espreguicar 4,5 s, Observar 6 s, Observar_Farejar 5 s, Reagir_Estimulo 2,5 s, Ninho_Inspecionar 6 s, Ninho_Acomodar 4,5 s, Ninho_Repouso 9 s, Ninho_Alerta 3 s, Ninho_Ameaca 4,5 s, Preparar_Combate 3 s, Dono_Reconhecer 3,5 s, Dono_Carinho 6 s, Dono_Receber_Alimento 4,5 s, Montaria_Abaixar 3 s, Montaria_Aguardar 4 s, Montaria_Levantar 2,6 s.
- Marcadores: Farejar, Mordida, Mastigar, Engolir, AguaToque, AguaSai, ContatoChao, Levantar, Bocejo, Sobressalto, Alerta, Rugido, Reconhecer, MontariaPronta, MontariaImpulso.
- Validação automática por quadro (`V14/anim/fase3/relatorio_fase3.json`): joelhos sempre acima do chão (mín. 1,09); barriga 0,0–0,7 nos deitados; focinho 0,3 ao beber e 1,5 ao comer.
- Erros corrigidos:
  - joelhos atravessando o chão (−5): resolvido com as patas automáticas;
  - "lança" na perna direita: escala/translação residual do IK que se acumulava sem ser gravada. Corrigido em `v14_anim_lib.resolve_pernas` (só a rotação é aplicada; escala e posição zeradas) e em `zera()`.
- Pranchas limpas: `V14/anim/fase3/previas/prancha3_a.png` e `prancha3_b.png`; MP4 por clipe.
- Roblox (Place1):
  - 25 KeyframeSequences importadas com marcadores em `Dragao_V14.Animacoes` (50 clipes no total);
  - módulo `ReplicatedStorage.Comportamento_Dragoes.EstadosDragao` instalado: 18 estados, posturas pe/deitado/abaixado, inserção automática de levantar/deitar e variações sorteadas.
  - **Teste no Play não concluído:** ao iniciar o Play, o Studio do Place1 parou de responder ao MCP (timeout; processo do Studio com ~20 GB de memória).
- Limitações: sem pálpebras (não há olhos fechados nem piscar, porque o modelo não tem geometria de pálpebra); a IA territorial não foi feita (fora do escopo).
- **Teste de estados (2026-10-28, à noite):**
  - O usuário reabriu o Studio com `Teste-animacoes.rbxl`. A cópia salva tinha só as 25 animações das Fases 1 e 2; a Fase 3 e o módulo não tinham sido salvos.
  - Reimportado: 50 clipes movidos para `ServerStorage.Animacoes_Dragao_V14` (assim não replicam para o cliente) e módulo de estados instalado. Play iniciou normalmente.
  - **Causa dos travamentos achada:** em `EstadosDragao._esperar`, o `AnimationTrack.Length` vale 0 logo após o LoadAnimation. A espera retornava na hora e o laço de variações do Idle girava sem ceder, travando o Studio duas vezes.
  - Corrigido: espera o clipe carregar (até 5 s) e o laço sempre cede (`task.wait`).
  - O módulo corrigido está em `V14/comportamento/EstadosDragao.luau`, **ainda não reinstalado**. No arquivo aberto ficou a versão com o defeito.
  - A sequência de estados ainda não foi validada no Play.
- **Fase 3 validada no Play (`Teste-animacoes.rbxl`, Studio MCP):**
  - Os clipes ficam em `ReplicatedStorage.Animacoes_Dragao_V14` (50). No ServerStorage a animação tocava no servidor mas não aparecia no cliente.
  - Módulo `ReplicatedStorage.Comportamento_Dragoes.EstadosDragao` corrigido (espera o clipe carregar; o laço sempre cede).
  - Sequência testada sem erros: Idle → Alimentação → (auto) Idle → Sono [Deitar → Adormecer → Dormir] → Alimentação [Acordar automático] → MontariaEspera → ProtecaoNinho [Montaria_Levantar automático] → AmeacaNinho → InteracaoAmigavel [Reconhecer → Carinho].
  - Ajuste: do ninho, ameaça e alerta sobem com Ninho_Alerta (não com "Acordar"). Testado de novo.
  - Capturas no Roblox: `V14/anim/fase3/capturas_roblox/` (comer, dormir, ameaça).
  - FPS medido 14,9 com o Studio fora de foco: inválido (com foco já havia dado 60).
- **O arquivo `Teste-animacoes.rbxl` precisa ser salvo (Ctrl+S)**; a importação anterior se perdeu por falta de salvamento.
- **Erro gráfico na raiz da asa (relatado pelo usuário):**
  - Diagnóstico: por raycast e renders isolados, é a **aba que liga a membrana ao flanco/quadril** (faces de `V14_Asa_E_b`/`Asa_D` em |x| 10–15, z 25–28).
  - Ela tem paredes laterais e fundo com UV esticado (listras claras). Já existe no modelo original do Meshy (render da malha alta confirma) e a dobra das asas a deixa mais exposta.
  - Correções no `v14_roblox.py`:
    - 4a: 831 faces com UV muito esticado (>12×) recebem o UV do próprio centro;
    - aba: 1905 faces da raiz (|x|<15, laterais, fundo ou UV >3×) recebem a cor das faces escuras (borda/osso) mais próximas da membrana.
  - `v14_rig.py`: o corpo só herda peso de AsaE_1/AsaD_1 do próprio lado, com rampa suave |x| 6→13 e z 22→28 (antes o dorso e a base do pescoço puxavam a asa oposta). Esticamento máximo do corpo com asas dobradas: 24× → 13×.
  - Resultado: `V14/roblox/correcao_aba_ombro.png`. A aba agora fica escura, como borda, sem listras. A geometria em degrau continua, porque é do modelo.
  - GLB atualizado em `V14/roblox/` (anterior em `V14/roblox_v5_antes_pesos/`). **Falta reimportar no Studio.**

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

## Retargeting de animações do afk.ai → Dragão das Montanhas (2026-10-29) — VERSÃO DE TESTE, NÃO INTEGRADA
**Fonte:** `Teste_IA/icy-dragon-animated.glb`
- glTF gerado pelo THREE.GLTFExporter, sem licença embutida.
- Esqueleto: 99 ossos (asas com 5 "penas", pernas digitígradas de 5 segmentos, pescoço curto, cauda de 6).
- Clipes: Fly Flap, Fly Glide, Fly Glide Left/Right, Fly Hover, Walk. **Não há corrida.**

**Licença** (site afk.ai, verificado em 2026-10-29):
- "skeleton templates and animation library are CC0", uso comercial sem atribuição.
- O modelo "icy dragon" (malha) é de chengzijieczj, no Sketchfab, sob CC BY 4.0. **Não foi usado**: só o movimento.
- Os Termos de Uso (afk.ai/terms) não tratam de licença de exportações.

**Método** (`Teste_IA/afk/retarget_afk.py`; nada do V14 é sobrescrito):
- Saída em `afk/saida`: `.blend` de teste, JSON e prévias; clipes com sufixo `_AFK`.
- Coluna, pescoço, cabeça e mandíbula: delta de rotação no mundo em relação ao repouso; cadeias de tamanhos diferentes interpoladas.
- Asas: direção dos segmentos (úmero, antebraço, 3 dedos ← wing_5 e penas 4/5). No planeio e nas curvas a componente vertical é achatada (×0,45) para as asas ficarem abertas na lateral.
- Pernas e cauda (o repouso dos rigs difere: a fonte tem patas já dobradas e joelho invertido; o nosso repouso tem cauda enrolada de lado): NOSSA postura do estado (patas recolhidas no voo, `cauda_para_tras`) + variação da fonte em torno da média do clipe.
- Andar: pés por IK com a trajetória do tornozelo da fonte, limitada a 5 studs de passada e 2,6/2,2 de elevação.
- Tempo esticado ×1,3–1,6 para o porte colossal.

**Bugs encontrados e corrigidos no processo:**
- O importador deixa os 6 clipes em trilhas NLA; sem mutar, a amostragem misturava todos e o movimento se anulava.
- Delta puro deixava as pernas "em pé" no voo e levantava a cauda.

**Roblox:** 6 KeyframeSequences novas (`Dragao_V14_*_AFK`, atributo `Teste_AFK`) em `Animacoes_Dragao_V14`. Os clipes atuais não foram tocados.
- Testado no Play: carregam e tocam com a duração certa (1,3 / 1,6 / 4,0 / 4,0 / 4,0 / 2,0 s).
- Capturas: `afk/saida/studio_*.jpg`; comparação: `afk/saida/comparacao_antigo_x_afk.png`.

**Pendentes:**
- **Não estão ligados à montaria nem à IA:** aguardam aprovação visual.
- Medida de velocidade do Andar_AFK não confiável (17,8 studs/s): calibrar o ritmo no Studio antes de usar.
- Sem corrida na fonte: a corrida continua a nossa (galope novo).
- Ainda não transferidos: decolagem, pouso e combate (a fonte não tem).

## Voo montado guiado pelo mouse + misturador de animações afk.ai (2026-10-29) — Teste-animacoes.rbxl
**Verificação do GLB:**
- Clipes: Fly Flap, Fly Glide, Fly Glide Left/Right, Fly Hover, Walk. Não há idle, corrida, subida, descida nem mergulho.
- Ossos que se movem nos clipes transferidos: Voo 20, Pairar 21, Andar 23, Planeio 9, Curvas 9 (o planeio da fonte é quase estático).

**Criados no Blender** (`afk/retarget_afk.py`):
- `Mergulho_AFK`: asas recolhidas para trás, pescoço alinhado, patas recolhidas.
- Movimento secundário do planeio, das curvas e do mergulho, dependente de fase (loop perfeito): dedos alares, curvatura da membrana, respiração, cauda com atraso progressivo, pernas e pescoço.
- Camadas `Olhar_Cima/Baixo/E/D_AFK`: só Pescoço1–4, Cabeça e Coluna3 (peso 0 nos demais, prioridade Action).

**Controlador** (`Montaria_Dragao_Servidor`, função `passoVoo`, arcade assistido; a autoridade é do servidor):
- O rumo segue o yaw da câmera, com taxa limitada (42–58°/s conforme a velocidade) e aceleração de giro limitada (140°/s²).
- A inclinação da trajetória segue o pitch da câmera: zona morta de 5°, até +40° / −60°, 70°/s.
- W acelera; S desacelera até 14 studs/s (sustentação, nunca para trás); sem tecla mantém a velocidade.
- Gravidade na trajetória: subir custa velocidade, mergulhar ganha (até 80).
- G: planeio (não sobe; acima de 30 studs/s troca velocidade por altura). W ou Espaço apertados de novo voltam a bater asas.
- Corpo: inclina até 32° pela taxa de curva e o nariz segue a trajetória (85%, até 40°).
- Assistências: sobe diante de parede; nivela rente ao chão; fora do mapa vale o último chão conhecido.
- **Misturador:** Voo/Pairar/Planeio/Curvas/Mergulho tocam juntos em laço e mudam só de PESO (fade 0,25 s), conforme velocidade, curva, gama, planeio e mergulho.
  - As camadas de cabeça entram por cima.
  - O ritmo das batidas sobe acelerando e subindo.
  - Decolagem → mistura com fade 0,45 s; mistura → descida de pouso com fade 0,5 s.

**Câmera** (`Montaria_Cliente`):
- Órbita própria com o mouse preso no centro (sem segurar botão; Alt solta o mouse); gamepad pelo analógico direito; toque mantém a câmera padrão.
- Rotação imediata; posição do alvo suavizada no pivô (as batidas não sacodem a imagem).
- Distância 70 + 0,45 × velocidade; colisão por raio (entra antes de montanha ou árvore).
- `pitchNeutro` 0,28 rad: a câmera olhando 16° para baixo = voo nivelado.

**Bugs encontrados e corrigidos:**
- Comentário no meio da linha da config anulou `acelVoo`/`freioVoo`: W/S sem efeito e erro a cada quadro (achado via LogService).
- Dragão descia no vazio fora do mapa.
- G anulado por W ainda no último pacote.
- Câmera olhando para baixo fazia descer.

**Testes no Play** (ângulos de câmera e W/S injetados pelo mesmo caminho do servidor + teclas reais):
- decolar (Espaço);
- subir com mouse para cima (+44 studs, camada olhar-cima);
- horizontal estável;
- curvas esquerda (+96°, corpo −7°) e direita (−95°);
- subida com curva e descida com curva;
- W até 55; S até 14 com Pairar;
- planeio reto (G real) e em curva (inclinação −28°, Curva_Aerea_E_AFK + Olhar_E);
- mergulho (−57°, vel 59, Mergulho_AFK);
- recuperação, retorno ao voo ativo;
- pouso (recusado acima de 160 studs com aviso; aceito em 3,1 s).
- Desempenho em voo: cliente 60 FPS (pior quadro 19 ms) com 10 trilhas; servidor 60 Hz; 0 erros no log.

**Pendentes:**
- **Não testado:**
  - movimento FÍSICO do mouse (a ferramenta não move o mouse: os ângulos foram injetados);
  - segundo jogador observando (só 1 cliente disponível);
  - gamepad e toque reais.
- Ritmo do Andar_AFK não calibrado (o andar no chão continua o nosso).
- Todos os números de voo continuam NAO_APROVADO.
- **Salvar o place (Ctrl+S).**

## 2026-10-29 — Silverwing Wyrm (Meshy) no esqueleto Mesh2Motion (TESTE, fora do Studio)
- **Fonte:**
  - `Downloads\Meshy_AI_Silverwing_Wyrm_1029143906_texture.glb` (intocado);
  - cópia leve `BLENDER\Criaturas\Teste_IA\meshy\Silverwing_20k.glb` (20 mil triângulos).
- **Esqueleto e animações:** `rig-dragon.glb` e `dragon-animations.glb` do Mesh2Motion. Licença CC0, verificada em `meshy\m2m_fonte\LICENSE-CC0.MD`.
- **Encaixe no site:** inviável pela ferramenta (cerca de 100 juntas, captura de 800 px). Feito no Blender com `meshy\encaixe_silverwing.py`, medido em vistas ortogonais com grade e fatias.
- **Montagem (`meshy\montar_silverwing.py`):**
  - pesos por distância, separados por região;
  - pontes fundidas do Meshy entre asa, cauda e patas removidas (221 faces);
  - suavização das arestas esticadas;
  - modelo reposicionado na pose base do molde. A mão da asa mantém o leque original e as rotações dela são convertidas.
- **Saída:**
  - `meshy\saida_m2m\Silverwing_M2M.glb` (4,3 MB; 19.779 triângulos; 100 ossos; até 4 influências);
  - animações Fly_Flap, Fly_Glide, Idle, Walk, Rest_Pose;
  - vídeos MP4 de cada animação.
- **Verificado:** reimportação do GLB, renderizações de descanso e de 3 quadros por animação.
- **Não testado:**
  - Roblox Studio (nada foi importado);
  - upload em "Use Your Rigged Model" do Mesh2Motion;
  - qualidade de pele detalhada (restam cerca de 300 vértices com estiramento leve, perto dos ombros e do quadril).
- **Revisão de deformação (29/10, depois):** os 151 quadros das 5 animações foram medidos com `meshy\qa_silverwing.py`.
  - **Correções aplicadas:**
    - a mão da asa agora é reassada por deslocamento de posição a partir do pulso (`assar_mao.py`);
    - o osso do ombro deixou de definir a região do dorso;
    - os cruzamentos entre as raízes das asas foram transferidos para a coluna (`corrigir_cruzamentos.py`);
    - os pesos foram polidos com base nas animações (`polir_pesos.py`).
  - **Resultado:**
    - cruzamento entre as asas: 0 em todos os quadros;
    - asa dentro do corpo: 0, exceto Fly_Flap quadros 8, 10 e 11 (até 10 vértices na raiz da asa, profundidade máxima de 0,02);
    - planeio: estiramento máximo de 2,9x em até 86 arestas.
  - **Limitação restante:** em Idle e Walk o molde dobra as asas rente ao corpo. As asas do Silverwing são proporcionalmente bem maiores e em leque, então ficam meio dobradas, com membrana enrugada nas pontas externas (até cerca de 500 arestas de 30 mil esticadas mais de 1,6x).
  - **Fidelidade do GLB:** ossos idênticos ao `.blend` no quadro testado. Pés até 1,2 cm abaixo do chão no Walk.
- **Dobra própria das asas (29/10, `meshy\dobra_asa.py`):**
  - Idle e Walk usam uma dobra criada para o Silverwing, em vez da dobra do Mesh2Motion.
  - Toda a dobra é relativa à asa aberta:
    - no plano da asa, o cotovelo dobra 30°, o pulso 35° e o leque fecha 40%;
    - a asa inteira varre 35° para trás e cai 35°;
    - o braço só acompanha 40% da varredura e 30% da queda;
    - o dedo 2 dobra para fora.
  - Movimento secundário cíclico: respiração no Idle e balanço do passo no Walk.
  - Parâmetros finais: `35 35 30 35 0.6 -0.3 0.3 0.4`.
  - Testadas e descartadas:
    - dobra fechada com o pulso à frente (estica até 27x, cerca de 2.300 arestas);
    - direções absolutas.
- **Penetração restante:** zerada com `corrigir_penetracao.py`, que passa peso de wing_2 e dos dedos 2 e 3 para wing_1.
- **QA final (151 quadros):**
  - asa x asa: 0 em todos;
  - asa dentro do corpo: 0 em todos;
  - arestas >1,6x: Idle até 368 e Walk até 453 (das quais cerca de 80 na barriga e nas patas, vindas do Walk do molde), Glide até 89, Flap até 310;
  - pés até 1,2 cm abaixo do chão no Walk.
- **Arquivos:**
  - GLB reexportado em `saida_m2m\Silverwing_M2M.glb`;
  - backups `Silverwing_M2M_antes_assar.blend` e `Silverwing_M2M_antes_dobra.blend`.
- **Não testado:** Roblox Studio e Mesh2Motion "Use Your Rigged Model".
- **Importação no Studio (29/10, Teste-animacoes.rbxl):**
  - O usuário importou `Silverwing_M2M.glb` pelo Import 3D. Chegou como `Scene`/`Mesh_0`, com 1 unidade = 1 stud (1,95 × 0,57 × 1,92), 99 ossos, um AnimationController e 5 KeyframeSequences em `ServerStorage.RBX_ANIMSAVES.Scene`.
  - Ajustes feitos:
    - renomeado para `Workspace.Silverwing` (malha `Silverwing_Malha`);
    - `ScaleTo(7)`, que dá **13,6 × 4,0 × 13,4 studs** (pedido: 12-15 studs);
    - ancorado e apoiado no chão em (575, 2, 500), com o atributo `Origem`;
    - animações copiadas para `ReplicatedStorage.Animacoes_Silverwing`.
  - **Play:** Idle, Walk, Fly_Flap e Fly_Glide tocaram via `AnimationClipProvider:RegisterAnimationClip` no Animator do AnimationController. Capturas conferidas, e nenhum erro dos nossos scripts (só avisos internos de UIBlox do Roblox). Nas animações de voo o modelo foi erguido 6 studs só na sessão de teste.
  - **Pendente:**
    - salvar o place (Ctrl+S);
    - os clipes de voo do molde deixam as patas abaixo do pivô: em voo real, o controlador precisa erguer o modelo;
    - integrar à montaria/IA e testar em mais jogadores, o que não foi feito;
    - `AuxScene` (artefato do importador) continua no Workspace.
- **Silverwing na montaria e na IA (29/10, Teste-animacoes.rbxl):**
  - **Modelo:**
    - escala 17,5 (2,5x), resultando em **34,1 × 10 × 33,6 studs**;
    - 9 ossos renomeados para os nomes do V14 (Cabeca, Quadril, Coluna2, Mandibula, Pescoco2/4, Cauda3, AsaE_2, AsaD_2), junto com as Poses das KeyframeSequences.
  - **Dragões:**
    - `Dragao_V14` e `Dragao_Montanhas_Jogador` foram movidos para `ServerStorage.Dragoes_Retirados` (reversível);
    - `Workspace.Silverwing` é a montaria do jogador de teste;
    - `Workspace.Silverwing_Guardiao` é um clone com os atributos do guardião V14 (Ninho_Pico).
  - **Scripts (opcionais por atributo; o V14 continua igual):**
    - `EstadosDragao:_kfs` com apelidos e o novo módulo `Animacoes_Silverwing.Apelidos` (4 clipes cobrem todos os estados; as camadas Olhar_* ficam desligadas);
    - `Montaria_Dragao_Servidor`: atributos AssentoAcima/AssentoFrente e RitmoAndarBase/RitmoCorrerBase; `temMix` funciona via apelidos;
    - `Locomotor`: RitmoAndarBase/RitmoCorrerBase;
    - `Montaria_Cliente`: atributos Camera_* por dragão (distância 30, alvo 6, voo 0);
    - `Teste_Montaria_Dono` passa a dar o Silverwing ao jogador.
  - **Testado em Play (montaria via Montaria_Debug, mesmo caminho do servidor):**
    - montar e sentar no dorso;
    - andar a 4,8 studs/s com Walk no ritmo 1,09;
    - decolar e voar, com o misturador de voo (Fly_Flap + Glide nas curvas);
    - pousar em 3,6 s, com os pés no chão;
    - câmera a 32 studs.
  - **IA:** o guardião ficou em Observation; ao sobrevoo do jogador, detectou ameaça nível 2, defendeu o ninho e voltou para o Recover.
  - **Erros:** 0 dos nossos scripts.
  - **Incidente:** a conexão MCP caiu num teste longo de voo, mas o usuário salvou e nada se perdeu.
- **Limitações:**
  - sem clipe de corrida (usa o Walk acelerado, com pés deslizando);
  - comer, dormir, ninho e montar usam o Idle;
  - o combate não tem animações próprias do Silverwing;
  - não testados: mouse físico, segundo jogador, combate com o Silverwing;
  - o Ninho_Pico continua dimensionado para o V14.

## 2026-10-29 — Dragão Glacial (Silverwing): correção anatômica + voo livre (TESTE, em andamento)
- **Diagnóstico** (`meshy\diag_anatomia.py`):
  - as patas dianteiras convergiam para a linha média: pés a ±3,5 cm, ombros a ±6,8 cm, por causa do reposicionamento no repouso do molde Mesh2Motion;
  - os pés traseiros ficavam suspensos 7 a 11 cm (1,2 a 1,9 studs), porque a perna é curta para a altura do quadril do molde;
  - o Idle e o Walk do molde dobravam a base da cauda em 20°;
  - no voo, as pernas pendiam esticadas (+25 a 35%) e juntas.
- **Correção** (`meshy\anim_silverwing.py`): 17 animações próprias, sem alterar malha nem esqueleto.
  - Patas: IK de 2 ossos + metacarpo/metatarso + dedos, com o chão travado; dianteiras a ±8,2 cm e traseiras a ±10,8 cm.
  - Andar: sequência lateral. Correr: galope rotativo. A passada traseira é 15% menor, com apoio proporcional, para não patinar.
  - Cauda: segmentada, com atraso, apoiada no chão.
  - Asas: amostradas das ações validadas.
  - Clipes: Parado, Andar, Correr, Parada, Abaixar, Abaixado, Levantar, Voo, Pairar (voo estacionário), Subida, Descida, Planeio, Curva_E, Curva_D, Mergulho, Decolagem, Pouso.
  - Bug corrigido durante o trabalho: o IK era aplicado depois de posicionar o osso superior.
- **Pesos:**
  - `polir_pesos.py` (modo corpo) reduziu o estiramento em 23%;
  - `corrigir_penetracao.py` e `corrigir_cruzamentos.py` zeraram a penetração e os cruzamentos.
- **QA final (todos os quadros):**
  - asa x asa: 0; asa dentro do corpo: 0;
  - garras até 0,14 stud abaixo do chão parado e 0,29 andando;
  - arestas acima de 1,6x: 266 a 570 por quadro (de cerca de 30 mil).
- **Saída:** `saida_m2m\Silverwing_Glacial_v2.glb` (17 animações), vídeos `v2_*.mp4`.
- **Studio (editado, não salvo pelo Claude):**
  - **Voo livre** (`Montaria_Dragao_Servidor`, função `passoVooLivre`), só com o atributo `VooLivre`; o Dragão das Montanhas continua com o controle antigo:
    - W acelera; S não tem função no ar; soltar W freia até parar no ar;
    - Espaço/Ctrl sobem e descem parado;
    - pouso automático abaixo de `AlturaPouso`, devagar e com intenção de descer;
    - Subida e Descida entram no misturador;
    - Config `vooLivre`.
  - **Câmera:** zoom pela roda do mouse dentro de `Camera_distMin` (13) a `Camera_distMax` (55); padrão 30.
  - **Atributos do Silverwing:** VooLivre, CorpoAltura/CorpoRaio, FolgaChao 3, AlturaPouso 7, Ritmo 4,46/18,9, `TesteScriptsMontanhas` (TEMPORÁRIO: usa FormaRegional=Montanhas e as habilidades das Montanhas; o Glacial não tem configuração de combate).
  - **Apelidos** atualizados para os clipes v2.
  - **Testado em Play** (via Montaria_Debug, com as animações antigas ainda no Studio):
    - decolar; W até 34; mouse para cima subiu 38 studs;
    - S no ar sem efeito; parada completa no ar com altitude mantida;
    - curvas E/D com inclinação de 27 a 32°;
    - passagem rápida rente ao chão sem pousar;
    - Ctrl parado pousou em 2,0 s; aproximação lenta pousou;
    - 0 erros.
- **Pendente:**
  - importar o GLB v2 no Studio (manual) e rodar `meshy\studio_trocar_silverwing.luau`, depois retestar no Play;
  - mouse físico e segundo cliente não testados;
  - tamanho: hoje os ombros têm cerca de 6,9 studs (o pedido cita 12-15 nos ombros): confirmar com o usuário.
- **Correção do usuário (29/10):** não é o "Dragão Glacial", é o **Silverwing** ajustado (único). O Glacial fica para depois.
- **v2 importado no Studio** com `studio_trocar_silverwing` (adaptado: havia duas pastas "Scene" em RBX_ANIMSAVES).
  - Silverwing e Silverwing_Guardiao trocados; as versões v1 estão em `ServerStorage.Dragoes_Retirados`.
  - 17 clipes em `Animacoes_Silverwing`; os do molde estão em `Animacoes_Silverwing.Antigas_M2M`.
  - Atributo `TesteScriptsMontanhas` (TEMPORÁRIO).
- **Bugs encontrados e corrigidos no Play:**
  - o voo livre subia com o nariz para baixo, porque em `aplicar()` um pitch positivo ergue o focinho;
    - **atenção:** o controle antigo do Dragão das Montanhas (`passoVoo`) e o `Locomotor` usam o mesmo sinal negativo e podem estar invertidos. Não foram alterados (preservação); verificar;
  - o zoom pela roda não funcionava (`camCfg` era usado antes de ser definido);
  - o mergulho com W não ganhava velocidade;
  - o planeio não descia com Ctrl e não pousava.
- **Testado em Play com o v2 (via Montaria_Debug + mouse/teclado do MCP):**
  - parado: patas apoiadas e cauda no chão; andar com o clipe próprio (ritmo 1,08);
  - decolar; subida com a cabeça 8 studs acima do quadril; mergulho com a cabeça 6 studs abaixo, 34 → 45 studs/s;
  - recuperação; soltar W leva à parada no ar em cerca de 4-7 s (Pairar w 0,98);
  - planeio (Planeio w 0,98); planeio + Ctrl pousou em 10,9 s; passagem rápida rente ao chão sem pousar;
  - zoom da câmera: mínimo 13 e máximo limitado (55), roda do mouse real;
  - guardião com IA patrulhando em voo com os clipes novos;
  - 0 erros.
- **Pendente:**
  - mouse físico pelo usuário e segundo cliente;
  - sincronizar os scripts editados no Studio com `V14/montaria/*.luau` (não feito);
  - salvar o place.
- **v3 (29/10): cauda, asas, corpo e Mordida Aérea**
  - **Diagnóstico** (`diag_cauda.py`, `comparar_malhas.py`, `soldar_costuras.py -- medir`):
    - a malha do Meshy estava partida em **771 ilhas**, porque a decimação moveu cada lado das costuras de UV de forma independente;
    - durante as animações, as costuras **abriam até 3,3 studs**, e isso aparecia como rasgos e lascas na cauda, nas asas e no corpo;
    - a base da cauda dobrava toda a queda em um só segmento.
  - **Correções:**
    - `soldar_costuras.py` soldou as bordas (≤ 7 mm, nunca dentro da mesma ilha, pesos médios): de 771 para 5 ilhas, de 19.247 para 11.088 vértices, textura/UV preservada; backup em `Silverwing_M2M_v2_antes_solda.blend`;
    - curva da cauda contínua: a queda se distribui pelos 4 primeiros segmentos e a subida de apoio começa no meio;
    - penetração e cruzamentos corrigidos de novo.
  - **QA (todos os quadros, 18 clipes):** asa x asa 0; asa dentro do corpo 0. Arestas acima de 1,6x: 450 a 790 por quadro. Agora a pele estica onde antes rasgava.
  - **Mordida Aérea:**
    - clipe `Silverwing_Mordida_Aerea` (1,0 s): preparo com pescoço em S, bote com pescoço projetado e asas varridas, mandíbula abre e fecha com tranco, garras à frente, recuperação até o Voo;
    - servidor (`Montaria_Dragao_Servidor`: `iniciarMordida` / `passoMordida` / `mordidaAcertos`, só com VooLivre): avanço real a 78 studs/s na mira da câmera, para diante de parede, hitbox só na cabeça (raio 5,5), dano 40 + empurrão em NPCs com Humanoid (jogadores excluídos até haver regra de PvP), recarga 4 s, `EmAtaque=MordidaAerea`;
    - Combate_Dragao_Servidor recusa pedidos durante a mordida;
    - Config `mordidaAerea` e controle Q / clique / L1;
    - cliente: slot extra "Mordida" com recarga, tranco de câmera ao acertar.
  - **Status:** `saida_m2m\Silverwing_v3.glb` exportado. **NÃO importado nem testado no Studio ainda** (importação manual + `studio_trocar_silverwing.luau`).
- **v3 importado e testado no Studio (29/10):**
  - `studio_trocar_silverwing` trocou Silverwing e Guardião: 34,1 × 10 × 33,6 studs, base no chão, 18 clipes; as versões anteriores estão em `Dragoes_Retirados.*_anterior` e em `Animacoes_Silverwing.Anteriores`.
  - **Testado em Play:**
    - montar; HUD com o 5º slot "Mordida";
    - mordida no chão é recusada;
    - mordida no ar contra `NPC_Alvo1`: clipe tocado, avanço de 56 studs, velocidade máxima 76, 40 de dano (500 → 460), `EmAtaque` limpo no fim;
    - repetir durante a recarga é recusado;
    - depois do ataque, W volta a acelerar (34 studs/s, subida);
    - **tecla Q real** dispara (HUD mostra "MordidaAerea, 76" e a recarga de 3,5 s no slot);
    - 0 erros.
  - **Não testado:** captura de tela no instante do bote no Studio (a captura saiu antes; o bote só foi visto nas renderizações do Blender e nos números), clique do mouse real, gamepad, empurrão em NPC não ancorado, segundo cliente.
- **v4 (29/10): verificação completa como o Roblox desenha** (`diag_faces.py`, backface culling)
  - **Causas encontradas:**
    - (1) a v1 reduziu a malha antes de soldar as costuras de UV, gerando 771 pedaços;
    - (2) faces com a normal para dentro (base da cauda, membranas): o Roblox só desenha a frente, então sumiam ("cauda faltando um pedaço");
    - (3) pontes da pose do Meshy (asa x cauda, pata x barriga, ponta da asa x flanco) eram APAGADAS, deixando buraco, ou esticavam (lascas);
    - (4) regiões pelo "osso mais próximo em linha reta" faziam a base da cauda virar asa.
  - **Correções:**
    - `reduzir_meshy_v2.py`: solda no original (1M) antes de reduzir, resultando em 1 ilha, 0 bordas abertas e 24 mil triângulos (`Silverwing_24k_v2.glb`);
    - `montar_silverwing.py`: regiões **geodésicas** (Dijkstra na malha); pontes **rasgadas sem apagar faces** (membro x membro, e membro x tronco longe da articulação);
    - `DoubleSided = true` na MeshPart.
  - **Cauda com mais movimento:** onda lateral do quadril à ponta no andar e na corrida, com chicote vertical; ondulação puxada pela batida no voo, subida, descida e planeio.
  - **QA final (19 clipes, todos os quadros):** asa x asa 0; asa dentro do corpo 0 (1 vértice em Pairar e Subida); malha com 1 ilha e orientação consistente.
    - **Resta:** cerca de 400 a 700 arestas acima de 1,6x por quadro, principalmente no dorso (`spine_0`) e na membrana perto do cotovelo da asa esquerda.
    - O polimento automático de pesos piorou a penetração e foi desfeito.
  - **Mordida no M1** (clique esquerdo) / L1; Q removido.
  - **Studio:**
    - v4 trocado (34,1 × 10,1 × 33,7), 18 clipes;
    - anteriores em `Dragoes_Retirados.*_anterior` / `Animacoes_Silverwing.Anteriores`;
    - importações usadas renomeadas para `Scene_usada`.
  - **Play:**
    - montado: corpo e asa fechados;
    - voo visto por trás: asas inteiras;
    - **M1 real** dispara a mordida; diante da montanha o bote parou antes da parede;
    - recarga no HUD; voo normal depois do ataque; 0 erros.
- **Rodada 29/10 (lascas, sons, ataques)**
  - **Diagnóstico das lascas (comprovado com renderizações):**
    - a malha leve na pose do Meshy fica limpa (`malha_v5`, remesh + bake de cor/normal, 19,5 mil triângulos, 1 ilha);
    - as lascas nascem no **repose** (asas erguidas → asas abertas do molde), por skin linear na raiz das asas e no dorso.
  - **Tentativas sem sucesso** (não entregues):
    - Corrective Smooth no repose;
    - pesos suavizados para o repose;
    - reposar o original de 1M (Surface Deform explodiu; Data Transfer esticou a membrana em "paredes").
  - **Correção real recomendada:** um modelo do Meshy já em pose neutra (asas abertas, quatro patas apoiadas, sem asas encostando na cauda), para eliminar o repose; ou pintura manual de pesos no Blender.
  - **Exportado:** `saida_v5/Silverwing_v5.glb` (malha remesh + bake). **Não importado.**
- **Studio (testado em Play):**
  - **prompt "Montar"** mostra "Silverwing" (atributo `NomeExibicao`).
  - **Ataques no Silverwing** (`Nucleo`):
    - pés e boca pelos ossos do rig Mesh2Motion;
    - clipes por apelido;
    - espera mínima dos marcadores.
  - **Ataques em NPCs, todos sem erro:**
    - Sopro: 48 de dano;
    - Arremetida: 26;
    - Tempestade: 48 em área;
    - Ruptura: 48, com 20 pilares.
  - **Sons** (`SonsConfig` + `SonsDragao_Cliente`):
    - origem: só a biblioteca Pro Sound Effects (Roblox) e sons do motor;
    - 12 sons carregados com sucesso;
    - batidas de asa sincronizadas pela fase da animação (11 em cerca de 4 s de voo);
    - passos de andar e correr (10 em 3 s e 15 em 3 s);
    - mordida (avanço + dentes);
    - sons das habilidades via `Combate_Dragoes.FX`;
    - `EstadosDragao` publica `MapaTrilhas` (o nome da trilha não replica).

## 2026-10-29 — Silverwing Drake3 (modelo Meshy em pose neutra, sem lascas nas pernas)
- **Fonte:** `Meshy_AI_Silverwing_Drake_1029194148_texture.glb` → `meshy\drake2\Drake2_lo.glb` (remesh + bake, 19.132 vértices). Cadeia: `meshy\cadeia_drake3.ps1` → `meshy\saida_drake3\Silverwing_Drake3.glb` (18 clipes).
- **Erro relatado (lascas/rachaduras quando as patas se mexem) — causas reais encontradas:**
  - **Costuras de UV:** o glTF separa o vértice onde a UV corta (5.066 pontos duplicados); 1.945 tinham pesos diferentes em cada cópia e a costura abria ao posar. Correções: regiões geodésicas e suavizações tratam as cópias como vizinhas (`montar_silverwing.py`, `costura_regioes.py`, `suavizar_esticadas.py`) e `unificar_costuras_uv.py` iguala os pesos (2 passagens na cadeia).
  - **Peito sob o pescoço com peso de `shoulder_l`:** girava junto com a asa no repose (rachadura gravada no descanso). `ASA_X_MIN=0.09` manda esses vértices para o tronco.
  - Fronteiras 1/0 entre regiões: faixa macia (`costura_regioes.py`, 5 anéis) e `COSTURA_RAIZ=0.08` no repose.
  - Patas de voo giravam 30° no quadril/ombro: agora 12° (`ANG_QUADRIL_VOO`) e a dobra vai para joelho/tornozelo.
- **Verificação no Blender:** interseções entre partes em todos os quadros de 37,9 mil → 19,2 mil; renders (Voo, Pairar, Parado, Andar) com pernas, coxa, peito e ventre limpos. QA_OK, PEN_OK, CRUZ_OK. Velocidades do clipe iguais (andar 4,46; correr 18,94 studs/s).
- **Pendência visual:** ainda há lascas pequenas na raiz da asa (atrás do ombro) com a asa erguida/dobrada (giro de 18° do repose da asa).
- **Studio (Teste-animacoes.rbxl):** `Silverwing` e `Silverwing_Guardiao` trocados (33,4 × 12,1 × 26,1 studs, ScaleTo 17,5); anteriores em `ServerStorage.Dragoes_Retirados.*_anterior`; 18 KeyframeSequences em `Animacoes_Silverwing` (antigas em `Anteriores`).
- **Testado em Play (via `Montaria_Debug`, jogador montou com E real):** montar → Parado; andar 4,8 studs/s com clipe Andar; decolar → Pairar_AFK; W → Voo_AFK 34 studs/s; soltar W → para no ar (Pairar); mordida → `EmAtaque=MordidaAerea`, 71,6 studs/s, clipe Mordida_Aerea; pousar → chão/Parado; desmontar ok; guardião voando com animação. Sem erros de script do jogo (os erros `abs(nil)` no console vieram da minha injeção de teste sem o campo `t`, o cliente real sempre envia).
- **Não retestado nesta versão:** ataques 1–4 em NPCs, sons, câmera/zoom, segundo cliente, gamepad. O usuário precisa salvar o place (Ctrl+S).
- **Drake3b — raiz da asa (29/10):** a asa gira como bloco a partir de `wing_1` e a fronteira asa/coluna era uma linha de 1–2 arestas; no bater a raiz do braço atravessava o dorso (lascas). `meshy\dobradica_asa.py` cria um gradiente de pesos na dobradiça (fração da asa sobe de 0 a 1 entre -0,03 e +0,08 ao longo do braço; raio 0,13; some na borda), seguido de penetração/cruzamentos/costuras UV (etapas incluídas em `cadeia_drake3.ps1`). Resultado no Blender: dorso limpo no Voo; QA_OK (sem asa no corpo, LxR 0); interseções 19,2 mil → 15,2 mil. Resta uma fresta pequena no topo do ombro com a asa dobrada (Parado).
  - Studio: `Silverwing_Drake3b.glb` importado pelo usuário e trocado (Silverwing e Guardião; anteriores em `Dragoes_Retirados`). Play: montar (E real), andar 4,8 studs/s (Andar), decolar, voo com W 30 studs/s (Voo_AFK), soltar W → pairar, mordida M1 (MordidaAerea, 69,7 studs/s), pousar, desmontar; **0 erros de script** no log. Place ainda não salvo pelo usuário.

## 2026-10-29 — Silverwing Drake3c: cauda viva, garra/mordida e clipes próprios de combate; curvas mais fluidas
- **Escala preservada (sem novo aumento):** 33,4 × 12,1 × 26,1 studs (envergadura × altura × comprimento), ScaleTo 17,5; ombros ≈ 7 studs. Divergência registrada: o RPG_02 [OFICIAL] diz adulto 18–24 studs até os ombros; o usuário mandou manter a escala atual.
- **Configuração:** FormaRegional=Montanhas (TEMPORÁRIO, teste), Fogo/Terra/Ar; habilidades Sopro, Arremetida, Tempestade, Ruptura. Ataque básico: RPG_02 [OFICIAL] "cada espécie-base possui ataque básico"; valores do Dragão não definidos → `ConfigCombate.basicos` segue NAO_APROVADO (Mordida 18, Garra 14, Cauda 20).
- **Cauda (anim_silverwing.py):** `onda_cauda` = ondas que nascem na base e correm para a ponta (atraso 0,8–1,6 rad/segmento, peso crescente para a ponta, harmônicos inteiros + envelope com momentos quase parados). Parado agora tem 8 s (respiração ×3, olhar que varre, troca de apoio, cauda em S contrária ao olhar); Andar/Correr com 2º harmônico; voo com 4 batidas por clipe (Voo 3,2 s, Pairar 4 s, Subida 2,8 s; Planeio/Descida/Curvas 4 s; Mergulho 2 s) para a cauda e as patas (`patas_vivas`) mexerem devagar. Curvas: quadril inclina, patas assimétricas, cauda compensa com atraso. Vistas de cima confirmam curvas em S parado e voando.
- **Clipes de combate próprios (antes eram apelidos: Sopro→Parado etc.):** Ataque_Mordida (1,4 s), Ataque_Garra_E/D (1,5 s), Ataque_Cauda, Rugido_Combate (+_Camada), Sopro_Inicio/Loop/Fim (+_Camada no ar), Arremetida (+_Camada), Tempestade_Asas (3,4 s), Tempestade_Asas_Ar, Ruptura_Vulcanica (3,6 s) — tempos casados com os marcadores de reserva do Nucleo. Blender: PEN_OK, CRUZ_OK, costuras UV 0 diferentes, QA_OK. GLB `meshy\saida_drake3\Silverwing_Drake3c.glb` (35 clipes).
- **Studio (`meshy\studio_combate_silverwing.luau`, tudo-ou-nada; originais em `ServerStorage.Backup_Scripts_Combate_Silverwing`):** Nucleo procura clipe `_Camada` próprio no ar; FX com `acertou`; montaria freia durante garra/mordida/cauda; **M1 no chão = mordida terrestre** (no ar continua a Mordida Aérea), **R = garra** (gamepad DPadLeft — R1 já era a Arremetida); sons: respiração grave em intervalos irregulares (mais frequente após correr/voar), whoosh/esforço da garra, impacto forte só com acerto, máx. 6 sons simultâneos por dragão, batidas casadas com os clipes de 4 batidas. Áudios novos, todos "Courtesy of Pro Sound Effects": 9113971531 (respiro), 9125467848 (esforço), 9119228132 (whoosh) — carregaram no cliente.
- **Curvas (referência de fluidez: vídeo do usuário jogando Dragon Adventures; só princípios, nada copiado):** ConfigMontaria giroVoo 42→52, giroVooRapido 28→36, inclinacaoMax 32→46, suavRoll 2,5→4, acelGiro 140→200 (valores antigos anotados no próprio arquivo). Medido em Play: antes inclinação 32° em ~1,8 s e 124° de giro em 3,1 s; depois 46° em ~0,8 s e 158° em 3,2 s.
- **Testado em Play (montado, teclas reais E/R/M1/1/2/3/4):** garra acertou NPC (−14), mordida terrestre tocou Ataque_Mordida e acertou (−18); Sopro tocou Sopro_Inicio→Loop→Fim, Tempestade_Asas, Ruptura_Vulcanica, Arremetida (avançou 85 studs) — todos com clipe próprio; voo, curva, pouso; 0 erros/avisos de script (servidor e cliente).
- **Não testado:** volumes por percepção (não há como ouvir), segundo jogador observando, PvP, versões _Camada no ar em combate, gamepad, desempenho com vários dragões. Pendência visual: pequenas frestas na raiz da asa dobrada. O usuário precisa salvar o place (Ctrl+S).

## 2026-10-29 — Drake3d: amplitude do corpo em voo/andar (referência Dragon Adventures)
- **Queixa do usuário:** no voo pés, corpo, cabeça e pescoço "estáticos". **Medido em Play (cliente):** as trilhas avançam, mas a cabeça oscilava só ±0,15 stud por batida → estático na escala do dragão.
- **Pesquisa:** busca web não achou vídeo de voo (resultados de guias); DevForum (equipe de How to Train Your Dragon no Roblox): voo com molas/suavização exponencial, foco em "sensação" e não física real. YouTube: longplay público de Dragon Adventures aberto no navegador, resolução baixa demais para medir patas. Medição feita no vídeo do próprio usuário (quadros a cada 0,125 s): corpo inteiro muda de atitude a cada batida, hover quase vertical com patas/cauda pendentes, andando o pescoço vai à frente e baixo.
- **anim_silverwing.py (PENDULO=1; 0 = antigo):** Voo — corpo sobe/desce ~0,9 stud com atraso da batida, arfa 5°, rola/guina lentamente, tórax flexiona, pescoço reage com atraso e cabeça estabiliza só em parte, patas em pêndulo (quadril/tornozelo/dedos com atraso), chicote vertical da cauda maior. Pairar — tronco a ~50°, plano da batida quase horizontal, patas pendentes balançando, cauda caída em S. Subida/Descida/Planeio com corpo flutuando, rolando e corrigindo rumo. Andar/Correr — pescoço à frente e baixo (−30°/−44°) com balanço atrasado, mais bob/rolagem/guinada do tronco; passada e velocidade iguais (4,46/18,94 studs/s, sem patinar).
- **Blender:** PEN_OK, CRUZ_OK, costuras 0, QA_OK; interseções por quadro 51–80 (repouso 39). Vídeos antes/depois em `meshy\saida_drake3\comp_antes` e `comp_depois`. GLB `meshy\saida_drake3\Silverwing_Drake3d.glb` — **ainda não importado/testado no Studio.** Backup do .blend anterior: `Silverwing_M2M_antes_movimento.blend`.

## 2026-10-29 — Camada dinâmica "MovimentoVivo" (reação ao movimento real) + inclinação 60°
- **Vídeo do usuário revisto inteiro (48 quadros, 1/s):** solto/parado o dragão gira para o jogador, olha em volta, estica as asas; no chão o corpo inteiro curva na curva; no voo inclina 60–80° em curvas fechadas, aponta o tronco na subida/mergulho; hover vertical; cauda segue a trajetória. Isso depende do movimento do jogador — clipe fixo não consegue.
- **Novo (só visual, cliente):** `StarterPlayerScripts.MovimentoVivo_Cliente` + `ReplicatedStorage.MovimentoVivo.Perfis` (fontes em `BLENDER\Criaturas\Teste_IA\V14\MovimentoVivo_*.luau`). A cada quadro (PreSimulation — medido: o Animator escreve entre PreAnimation e PreSimulation e o valor chega ao desenho) soma ao Transform dos ossos, com molas: pescoço/cabeça entram na curva, coluna dobra, cauda segue o arco com atraso crescente por segmento, pescoço acompanha subida/descida, cauda compensa, patas reagem à aceleração/freada, asa interna da curva baixa, cabeça segue a câmera do cavaleiro, e solto/parado olha jogadores próximos (70 studs). Pivô replicado chega a ~30 Hz: grandezas recalculadas só quando o pivô muda, com tempo acumulado. Genérico: qualquer criatura com atributo `PerfilMovimento` (Silverwing e Silverwing_Guardiao = "Silverwing").
- ConfigMontaria `inclinacaoMax` 46 → 60.
- **Testado em Play (montado, entradas injetadas pelo Montaria_Debug):** curva no chão giro 0,71 rad/s → coluna 9,8°, cauda no arco; curva no voo 0,93 rad/s → inclinação 60°, pescoço 16,5° (no jogo real ~37°: no teste a câmera não acompanhava e o "olhar" puxava ao contrário), coluna 12,7°, asa 12,7°; mergulho trajetória −46° com tronco para baixo e cauda subindo; 0 erros no cliente, ~61 FPS.
- **Pendente:** importar o Drake3d (clipes com corpo vivo) — a camada soma por cima de qualquer clipe; validação do usuário com mouse real; sinal da asa (`sinalAsa`) conferido só numericamente.

## 2026-10-29 — "Não mudou nada": causas e correção (clipes sem importação manual, corpo inteiro orientado)
- **Causas:** (1) os clipes Drake3d dependiam da importação 3D manual e não estavam no jogo; (2) ganhos da camada pequenos para o tamanho do dragão; (3) o controlador limitava o pitch do corpo a 40° (subida máx. 40°, nariz 0,85).
- **Ponte Blender → Studio sem importação:** `meshy\exportar_clipes_json.py` (JSON em `V14\ia\anim_json`, servido em 127.0.0.1:8766) + `V14\montar_kfs_json.luau`. Conferido: Pose.CFrame do importador = matrix_basis do Blender (diferença 0,0000° em 98 ossos). **Armadilha encontrada e corrigida:** o keyframe importado tem duas raízes irmãs (DRV_root vazia + root com os 98 ossos); copiar só a primeira gerou clipes que tocavam sem mexer nenhum osso.
- Instalados no Studio (versão Drake3d): Voo, Pairar, Andar, Correr, Subida, Descida, Planeio (98 ossos/quadro).
- **Controlador:** pitch do corpo configurável (`voo.pitchMax` 65, `pitchResp` 5,5), subida máx. 60°, descida 70°, gamaTaxa 95, narizSegue 1,0. **Camada MovimentoVivo:** pescoço 70°/(rad/s) até 55°, coluna 24 até 22°, cauda 15/segmento até 17°, trajetória 0,55 até 32°, patas 1,6 até 28°, asa 24 até 22°.
- **Medido em Play (cliente, montado):** hover — tronco (Quadril) 47–51°, pescoço 35–37°, cauda/patas oscilando; subida — corpo 52° nariz para cima, cauda pendente; mergulho — corpo −57°; curva — inclinação 60°, pescoço 40° para dentro, coluna e asa 22°, cauda em arco; 0 erros no cliente. Capturas da câmera do jogador conferidas.
- **Não testado:** controle com mouse real pelo usuário; curva no chão nesta rodada (o teste não chegou a pousar a tempo); Correr/Andar novos em Play.

## 2026-10-29 — Gravação do usuário analisada (19:01): câmera, chão e velocidade
- **Achados na gravação (24 quadros):** no voo a câmera ficava longe (dragão pequeno, detalhes ilegíveis: a distância crescia com a velocidade); no chão as asas ficavam meio abertas/assimétricas (Andar/Correr usavam as asas do Walk do molde); andar muito lento (4,8 studs/s); pescoço ereto escondia a cabeça.
- **Feito:** Andar/Correr com asas dobradas (Idle) e pescoço à frente; Andar mais vivo (T 0,9 s, passada 0,26, apoio 0,64 → 7,9 studs/s no ritmo 1); Parado com pescoço 14° mais baixo. Clipes levados ao Studio pela ponte JSON. Montaria lê `VelAndar`/`VelCorrer` por modelo (Silverwing 10/22; antes 4,8/17 globais), `RitmoAndarBase` 7,9. Câmera do Silverwing: distância 26, porVel 0,06, máx. 42, alvo 7.
- **Play:** andando a 10 studs/s com corpo e cauda em arco na curva; voo com o dragão grande na tela, inclinação 36° numa curva de subida, pescoço para dentro, cauda em curva longa. 0 erros.
- **Limite atual:** a dobra própria das asas deste modelo (membrana enorme) não fica rente como na referência e uma asa sobe ao andar — exige refazer a pose de dobra (dobra_asa.py) e repassar penetração/cruzamentos.

## 2026-10-29 — "Só asa e rabo se mexem": amplitude ×2,5 em corpo/cabeça/patas (AMP)
- **Medição que confirmou a queixa:** no cliente do usuário, pairando, tronco 46–51° e pescoço 35–37° (±2°), cabeça ~0,8 stud — parado na escala do dragão; asas ±60° e cauda ±17° eram as únicas partes amplas.
- **anim_silverwing.py:** `AMP` (padrão 2,5; `AC` = 1,825 no chão) multiplica no Voo/Pairar o sobe-desce, arfagem, rolagem, guinada, tórax, pescoço/cabeça e o pêndulo das patas/dedos; no Andar/Correr o bob, rolagem/guinada do tronco e o aceno da cabeça; no Parado respiração, troca de apoio e olhar. QA_OK, PEN_OK, CRUZ_OK; interseções por quadro no voo 53–70 (repouso 39); andar/correr/parado 115–140 (contato asa dobrada × corpo). Levado ao Studio pela ponte JSON (Parado, Andar, Correr, Voo, Pairar). Backup: `Silverwing_M2M_antes_amp.blend`.
- **Medido em Play (variação real na tela):** andando — cabeça 2,5 studs de lado a lado, pata dianteira 4,1 studs de passada; voo nivelado — quadril sobe/desce 2,7 studs e gira 9,6°, patas traseiras 3,2 studs, dianteiras 1,3–2,0, cabeça 1,7 lateral.

## 2026-10-29 — Câmera/mouse livre/mira/E-Q (Studio) + anatomia localizada e patas recolhidas (Drake4)
- **Studio (`V14\patch_mira_camera.luau`, tudo-ou-nada, 26 trocas; originais em `ServerStorage.Backup_Scripts_MiraCamera`):** E sobe / Q desce (prioridade sobre o pitch da câmera; com W ±35°, sem W vertical no lugar 16 studs/s); cursor livre (sem LockCenter) com retícula pequena (vermelha sobre Humanoid); câmera gira só com botão direito (sem girar volta para trás do dragão; o rumo do voo só segue a câmera enquanto ela gira); zoom Silverwing 12/25/45; habilidades miram pelo cursor (raio da câmera, direção da boca até o ponto); Sopro segurado: emissão contínua até 6 s, 8 energia/s além de 1,8 s, mira viva validada no cone do pescoço (servidor) e efeito seguindo a mira (VFX fase "mira"); cabeça do dragão olha a mira (MovimentoVivo). Gamepad: subir/descer mantêm A/L2 (bug do table.unpack corrigido com `juntar`).
- **Testado em Play (teclas reais):** E decolou e subiu no lugar (vel 0, y 48,9); Q desceu 20 studs no lugar; W+E subiu 32 studs avançando 86, corpo 34°, sem girar; mouse livre (MouseBehavior Default), retícula visível; Sopro (Fogo) segurado ~4,5 s — ataque durou 0,5→7,3 s, chama saindo da boca para o cursor à direita; 0 erros cliente/servidor. Não testado: multiplayer, gamepad, toque.
- **Anatomia (Drake4, `meshy\ajuste_anatomico.py`):** escala de pose aplicada como novo repouso só em tail_1 (comp. 1,20 / esp. 1,35), wing_1 (1,22) e front_leg_collar/back_leg_hip (esp. 1,10 / comp. 1,03); modelo subiu 0,031 para os pés tocarem o chão. Envergadura 2,23 (era ~1,83). Cabeça, pescoço e tronco intocados.
- **Clipes (Drake4):** todos regenerados no novo esqueleto; voo com patas RECOLHIDAS (`ENCOLHE` 0,62: alvo do punho/tornozelo perto do corpo → IK dobra cotovelo/joelho); mergulho com asas varridas e parcialmente fechadas (mistura 0,66, ombros −18°) — primeira versão (0,78/−22°) dava 196 interseções asa×corpo, corrigida para 78–83. QA_OK, PEN_OK, CRUZ_OK, costuras 0. GLB `meshy\saida_drake4\Silverwing_Drake4.glb` — **aguarda importação do usuário** (a malha mudou).
- **Patas de voo contraídas PARA TRÁS (pedido do usuário):** bug corrigido — o giro "para trás" usava o eixo −X do corpo e levava as patas para FRENTE (dianteiras pareciam agarrar o ar); agora +X. Valores: traseiras 48°, dianteiras 32°, `ENCOLHE` 0,74 / `ENCOLHE_FRENTE` 0,8, pêndulo leve mantido (no hover voltam a ficar mais abaixo). Testes: 55°/38° → interseções 350–500 e pele esticando no quadril; 50°/55° → dianteiras entrando no peito; 48°/32° → 73–95 (normal). **Variáveis de ambiente para regenerar os clipes de voo:** PERNA_VOO_REL=1 ANG_QUADRIL_VOO=12 NECK_BASE=0 PESC_VOO=-40 PENDULO=1 AMP=2.5 ENCOLHE=0.74 ENCOLHE_FRENTE=0.8 ANG_VOO_TRAS=48 ANG_VOO_FRENTE=32.
- **Troca no Studio (Drake4) + teste em Play (2026-10-29):** Silverwing e Silverwing_Guardiao trocados pelo Drake4 (33,4×12,1×26,1 → 39,9×12,65×29,4 studs; anteriores em `ServerStorage.Dragoes_Retirados`). Os 18 clipes de ar com patas para trás foram instalados pela ponte JSON. **Verificado em Play:**
  - cavaleiro sentado no lugar certo e asas dobradas simétricas no chão;
  - E decola e sobe;
  - voo para frente a 33–34 studs/s, com vista lateral capturada: patas traseiras dobradas para trás junto à barriga e dianteiras dobradas perto do peito;
  - pairar com tronco erguido e patas mais penduradas, como esperado;
  - console sem erros do jogo (só avisos internos do CorePackages/UIBlox).

  **Não testado:** mergulho com asas fechando no Drake4, mira/Sopro com o modelo novo, multiplayer, gamepad e toque. As dianteiras ainda apontam um pouco para baixo; se quiser mais para trás, o limite é ~32–38° antes de entrar no peito. Salvar o place com Ctrl+S.

## 2026-10-30 — Drake5 (asas 1,5×, corrida, voo) + IA selvagem integrada (autônomo, Teste-animacoes.rbxl)
**Autorização:** prompts "Refinamento avançado de animações e asas" e "Etapa avançada de IA e integração ao mundo", com execução autônoma do que é reversível. Nada foi publicado. O mapa principal e as outras criaturas não foram tocados. Os backups históricos foram preservados.

### A. Drake5 (Blender: `BLENDER\Criaturas\Teste_IA\meshy\saida_drake5\`)
- **Cópia de trabalho:** `Silverwing_M2M.blend`. A origem Drake4 intacta está em `Silverwing_M2M_drake4_origem.blend`, e a pasta `saida_drake4` não foi alterada.
- **Asas 1,5×**, aplicadas uma única vez. O script `ajuste_anatomico.py -- 1 1 1.5 1 1` aplica escala de pose em `wing_1_l/r` (braço, dedos e membrana juntos, proporção mantida) e a torna o novo repouso. Envergadura: 3,232 u (≈56,6 studs na escala 17,5). Os pés continuam no chão (dz 0).
  - O cálculo do chão passou a usar as pontas dos dedos, não o vértice mais baixo.
  - Tronco, cauda e pernas não mudaram.
- **Dobra própria das asas no chão** (`DIR_DOBRA` no `anim_silverwing.py`):
  - Com as asas maiores, a dobra do molde (Idle) virava uma "tenda" de membrana até o chão.
  - A dobra nova coloca o úmero para trás, o punho perto do ombro e os dedos deitados ao longo do flanco, com as pontas acima do chão. Tem leve variação de respiração.
  - Ela substitui as amostras do Idle: todos os clipes de chão e as transições abrir/fechar usam a dobra nova.
  - Interseções no Parado: 66 → 46.
- **Meia abertura de exibição** (`asas_ameaca`): na intimidação, as asas sobem e abrem para os lados em vez de cair até o chão. Vale para Alerta, Ameaça, postura de combate, Rugido e golpes.
- **Corrida pesada:** a velocidade continua 18,94 studs/s (RitmoCorrerBase intacto).
  - Apoio 0,42 → 0,48, sem fase aérea; passada 0,30 → 0,343.
  - Quique, arfagem, flexão e rolagem ficaram com cerca de 1/3 dos valores anteriores.
  - Pescoço esticado, com a cabeça compensando 75% do balanço; cauda como contrapeso (×0,45).
  - Interseções: 167 → 81.
- **Voo mais vivo:**
  - A onda de cada batida sobe vértebra por vértebra pelo pescoço, e a cabeça estabiliza 70%.
  - Olhar lento para os lados, com ajustes próprios da cabeça.
  - Patas com mais amplitude e abertura lateral independente (sem ficarem coladas).
  - Planeio com pequenas correções alares, uma asa de cada vez.
  - Clipe novo `Voo_Rapido` (5 batidas, corpo alongado, patas mais recolhidas, cauda alinhada), achado direto pelo prefixo no estado Voo_Rapido.
- **12 clipes novos de comportamento** com os nomes lógicos do EstadosDragao (antes caíam no "Parado"): Beber (9 s), Comer (8,5 s), Observar, Observar_Farejar, Reagir_Estimulo, Idle_Alerta_Mantido, Ninho_Ameaca (rugido), Preparar_Combate, Adormecer, Dormir (cabeça apoiada no chão), Acordar, Ninho_Alerta.
- **Mordida no chão mais baixa:** no teste, a boca chegava a ficar 17 studs acima de um alvo do tamanho de um jogador. Agora o bote desce até cerca de 3,5 studs.
- **QA:** cadeia penetração/cruzamentos/costuras/QA aprovada (31 grupos de costura unificados). Interseções por clipe iguais ou menores que no Drake4.
- **Saídas:**
  - GLB `saida_drake5\Silverwing_Drake5.glb`, **ainda não importado**: depende da Importação 3D manual.
  - Pranchas `prancha_final_*.png` e `prancha_ameaca.png`.
  - 48 clipes JSON em `V14\ia\anim_json`, todos **instalados no Studio** pela ponte. As versões anteriores estão em `Animacoes_Silverwing.Anteriores`.
- **Ferramentas novas:** `diag_asa.py`, `prancha.py`. `render_clipes.py` agora aceita qualquer lista de clipes e `RAIO_CAM`. `studio_trocar_silverwing.luau` foi atualizado para o Drake5 e troca só o modelo quando a importação não traz o pacote de clipes.
- **Variáveis de ambiente do gerador:** as mesmas do Drake4. Novas: `DOBRA_PROPRIA=1` (padrão) e `PLANEIO_ABAIXA=0`.

### B. IA selvagem — auditoria e complementos (sem reescrever)
**Já existia e foi preservado:** Cerebro (21 estados com prioridade), Locomotor (chão/voo/caverna), Territorio (um ninho por guardião, coleta com trava antes do yield, sem RemoteEvent), Combate (Nucleo autoritativo, zonas seguras, PvP).

**Lacunas achadas na auditoria:**
- `GuardiaoAtacado` nunca era disparado.
- A IA só pedia ataque a até 45 studs, então nunca usava Sopro nem Arremetida.
- A Tempestade era usada com qualquer dupla de alvos.
- O sopro da IA era fixo (1,8 s) e não seguia o alvo.
- "Investigate" não tinha tarefa.
- Nada acontecia com quem chegava perto do dragão longe do ninho.
- O Locomotor usava as velocidades do V14.
- Não havia LOD distante, convivência entre dragões nem depuração visual.

**Patches** (em `V14\ia\`, tudo-ou-nada; originais em ServerStorage: `Backup_Scripts_IA_Selvagem`, `Backup_IA_Margem`, `Backup_IA_Ajustes`):
1. `patch_ia_selvagem.luau` (8 scripts):
   - **Investigar** a última posição, só quando o alvo some de vista.
   - **Espaço pessoal** fora do ninho: perto e visível gera alerta; a ≤34 studs por 4 s vira defesa própria, com perseguição limitada ao território.
   - **LOD:** sem jogador a 1500 studs, decisão a cada 2,5 s e só rotinas paradas. Eventos do ninho ou ataque acordam a IA na hora.
   - **Convivência:** destinos e poleiros livres entre dragões (90 studs).
   - Zonas seguras respeitadas; ataque a distância só com linha de visão; espera o golpe terminar antes de se reposicionar; limpeza de conexões e do registro.
   - **Locomotor:** usa RitmoAndarBase/VelCorrer do modelo; teste de parede com a largura do corpo.
   - **Combate — escolha tática:**
     - critérios: distância, altura, visão, espaço acima, grupo real (3+, ou 2 cercando), trajeto livre para a Arremetida, recarga e energia, com pequena variação;
     - grava os atributos `IA_Habilidade` e `IA_Bloqueio`.
   - **Sopro contínuo da IA:** segura e acompanha o alvo; solta ao perder alcance, visão ou cone; dura 2,2–4,5 s; o Nucleo ainda limita em emissaoMax e consome energia.
   - Habilidade usada perto de um guardião dispara `GuardiaoAtacado`, **sem dano** no guardião (regra de vida pendente).
   - **Nucleo:** o sopro termina se o dragão for removido ou incapacitado.
   - **Depuração visual:** `Workspace.IA_DebugVisual = true` mostra um painel só no PlayerGui de autorizados (Studio, criador ou atributo Dev).
   - **Sons contextuais:** rugido na ameaça (intervalo ≥12 s), rosnados no alerta e no combate, mordidas ao comer. Só os sons licenciados já existentes.
2. `patch_ia_margem.luau`:
   - Beber: acha a água real pelos voxels e fica em terra firme, de frente para a água, com a boca na beira.
   - Sono: se já está deitado no ninho, adormece ali mesmo.
3. `patch_ia_ajustes.luau`:
   - Alerta pessoal no ar faz o dragão pousar ali (não voltar ao ninho).
   - Habituação: 25 s de alerta para quem não avança, depois 90 s sem novo alerta.
   - Corpo a corpo e Ruptura só com o alvo no mesmo nível.
   - Sem visão, o guardião avança até a borda (dentro da zona crítica).
   - Giro no lugar: 22 → 40 graus/s.
   - O rugido de ameaça acontece uma vez por confronto; depois, `PosturaCombate`.

### C. Testes executados no Play (servidor + capturas)
- **Natural:**
  - Comer: pouso, farejar, `Comer` por 8,4 s.
  - Beber: antes da correção bebia de costas, com a cauda no lago (**defeito corrigido**); depois, em terra firme e de frente para a água (captura).
  - Sono: Descanso → Adormecer → Dormir no ninho (captura); despertar por ameaça com `Acordar`.
- **Ninho:**
  - Invasor no topo: o guardião acorda, faz a ameaça com rugido e ataca. Mordida e garra causaram dano.
  - Invasor 60 studs abaixo na encosta: retorno voando rápido, pouso, avanço até a borda, **Sopro** escolhido (corpo a corpo bloqueado por desnível), cerca de 3,5 s contínuos, 48 de dano, repetindo a cada recarga.
  - Dois invasores no topo: mordida → **Tempestade** → mordida (recarga respeitada); dano nos dois.
- **Pessoal (300 studs do ninho):**
  - A 45 studs: Alert, encarando no lugar.
  - A 26 studs: escalada → ChaseIntruder → Cauda (alvo atrás), Garra e Mordida, 54 de dano.
- **LOD/depuração:** com o jogador a 2370 studs, painel com "LOD: dormente". O painel aparece só com `IA_DebugVisual` ligado.
- **Defeito de ciclo achado e corrigido:** jogador parado perto do lago gerava alerta no ar → volta ao ninho → investigar → alerta…
- **Desempenho:** 2 guardiões (um em combate, outro voando), servidor a 60 Hz: média 16,7 ms, p95 17,3 ms, pior quadro 24 ms. Log da IA sem erros nos dois. Console só com avisos internos do Studio.
- **Animação:** 48 clipes instalados e tocando (`Beber`, `Comer`, `Dormir`, `Ninho_Ameaca`, `Preparar_Combate`, `Voo_Rapido` etc.).

**Não testado (sem evidência):**
- multiplayer real, coleta simultânea por 2 jogadores (a trava já tinha sido testada antes), gamepad, toque;
- montaria/voo do jogador com os clipes novos;
- Tempestade aérea pela IA (a IA sempre pousa para lutar);
- combate aéreo da IA contra alvos voando;
- passagem estreita, teto baixo e penhasco no mapa real;
- Drake5 no Studio (falta a importação);
- habituação após o patch 3 (o código compila, mas o ciclo do jogador parado não foi repetido);
- mapa real das Montanhas Altas.

### D. Pendências e decisões do usuário
- **Importar** `saida_drake5\Silverwing_Drake5.glb` (Importação 3D) e rodar `meshy\studio_trocar_silverwing.luau`: ele troca o modelo e mantém os 48 clipes. Depois, **salvar com Ctrl+S**.
- **Regra de vida/incapacitação de dragão selvagem** (pendente no documento): hoje o guardião não recebe dano e só reage.
- **Combate aéreo da IA:** sem regra/design para alvos voando.
- Todos os números novos (raios, tempos, giro 40°/s, habituação) são **calibração de teste (NAO_APROVADO)**.
- Os invasores do laboratório não têm Humanoid. Nos testes foi adicionado um Humanoid só durante o Play.
- **Fontes locais desatualizadas:** os `.luau` em `V14\ia\` (Cerebro/Locomotor…) estão atrás do Studio. A versão instalada = originais em `Backup_Scripts_IA_Selvagem` + os 3 patches, em ordem.
### E. Decisão do usuário (30/10): "Ele pode ser derrotado, lutar tanto no ar quanto na terra"
**Patches** (em `V14\ia\`; originais em `Backup_IA_DerrotaAr` e `Backup_IA_CorridaTarefa`):
1. `patch_ia_derrota_ar.luau`
   - **Vida e derrota:**
     - Vida 600, recuperação em 120 s com 50% da vida, regeneração de 2/s depois de 20 s sem dano (**EXPERIMENTAL / NAO_APROVADO**).
     - Atributos `Vida`, `VidaMax`, `UltimoDano`, `Derrotado`.
     - Só dragões de jogador ferem o guardião, pelo Nucleo (`N.danoGuardiao`, raio do corpo somado ao acerto) e pela Mordida Aérea da montaria. Zona segura vale.
     - Ao derrotar: `Incapacitado`; a IA pousa se estiver no ar, deita e esquece o confronto, e o ninho fica sem defesa.
     - Barra de vida só aparece em combate ou derrotado.
     - **Sem recompensa/loot** (não há regra).
   - **Combate aéreo:**
     - Alvo a mais de 22 studs acima do chão = voando: o guardião decola e persegue no ar a 38 studs (`Locomotor:perseguirAr`, desvia de obstáculos subindo).
     - Ataca no ar: o Combate já escolhe Arremetida, Sopro, Mordida aérea ou Tempestade aérea quando `NoAr`; durante o golpe, paira.
     - Alvo no chão: pousa e luta em terra.
     - Outros dragões não contam como obstáculo de terreno.
2. `patch_ia_corrida_tarefa.luau`:
   - Corrige uma corrida entre tarefas achada no teste: o laço de locomoção antigo tocava `Correr` por cima da animação de derrota. Agora os 5 laços conferem `vivo()` após cada quadro.
   - Com o Sopro em recarga, chega a 20 studs no ar (mordida aérea).
3. Ajuste direto: a perseguição em terra pousa antes de andar; barra de vida mais baixa (`PATCH_IA_POUSO_PERSEGUICAO`).

**Testado no Play:**
- **Invasor voando** 70 studs acima do ninho: guardião decolou, subiu até a altura dele (264 contra 260), fez Arremetida aérea e Sopro contínuo pairando (2 vezes), com 96 de dano (captura do fogo no ar).
- **Derrota:** o Sopro do Silverwing (posse dada ao avatar só no Play) feriu o guardião.
  - Ele reagiu perseguindo o agressor e, em 0, pousou e deitou (`Deitar` → `Deitado_Acordado`, captura com a barra).
  - Derrotado, não recebe mais dano.
  - Recuperou sozinho depois de 120 s com 300 de vida e voltou ao ninho voando.
- Depois do último ajuste: o guardião inicia e patrulha sem erros (o ajuste em si não foi exercitado em combate).

**Não testado:**
- mordida aérea do jogador montado acertando o guardião (código compila);
- coleta do ovo com o guardião derrotado (a trava de coleta é a mesma);
- multiplayer.

### F) 2026-10-30 — dragão novo (CR_Dragao) e limpeza do repositório

**Dragão novo (decisão do usuário):** visual inspirado na referência `BLENDER/Criaturas/Teste_IA/dragao_novo/ref/conceito_dragao_vermelho.png`, modelado do zero no Blender, sem créditos do Meshy.
- Pose neutra (em pé, asas abertas) para rig e animação.
- Aprovado em revisões até a v12. Fonte: `dragao_novo/criar_dragao_ref.py`; brief em `dragao_novo/asset-brief.md`; prancha em `dragao_novo/review/Dragao_Conceito_v12.png`.
- Adaptações para movimento: membrana presa só ao flanco; espinhos e chifres encaixados na pele por raio (0 peças soltas, medido); cabeça 1,3× escalada sobre a junta do pescoço (articulações inalteradas).
- Malha de jogo: `dragao_novo/low/CR_Dragao_LOW.glb`, 20.456 tris. Uma UV com mapas de cor, normal e rugosidade assados do master (2048).
  - O Quadriflow recusou a malha, então o corpo foi reduzido por Decimate. A topologia para deformação ainda precisa ser revista no rig.
  - Está 456 tris acima da meta de 20k.
- Ainda não tem rig, animação, importação no Studio nem texturização do Meshy. O Meshy está aguardando o usuário configurar `MESHY_API_KEY`.

**Limpeza do repositório (autorizada pelo usuário):** nada foi apagado.
- 179 itens (~6,3 GB) foram movidos para `C:\Users\Rhenan\Downloads\RPG_Arquivo_Morto_2026-10-30`, com `MANIFESTO.txt`. O repositório foi de ~8,5 GB para ~2,2 GB.
- Saíram:
  - tentativas antigas de dragão (V6–V13, Hunyuan, Trellis, AFK);
  - modelo e animações do dragão V14 (`V14/anim`, `V14/roblox*`, `V14/textura`, GLBs);
  - iterações do Meshy anteriores ao Drake5 e quadros brutos do vídeo;
  - revisões antigas do dragão novo;
  - `Blockouts/review`, `_Provisorios`, versões V2–V5 da Árvore Ancestral e `v11_render.py`.
- Ficaram:
  - `V14/ia`, `combate`, `comportamento`, `montaria`, `vfx` e os `.luau` do V14;
  - scripts do `meshy`, `saida_drake5`, `m2m_fonte`, o MP4 do vídeo;
  - `dragao_novo` v12/LOW, Biblioteca, Floresta, Blockouts (sem review), DOCS, SCREENSHOTS.