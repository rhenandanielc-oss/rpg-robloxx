# Fundação: estado inicial do Studio, M1

Voltar ao índice: [[PROJECT-STATE]]

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

