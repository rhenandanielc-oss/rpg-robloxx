# Marcadores ecológicos de fauna (M4.4 Planícies / M5 Tundra)

Somente ambiente e dados para a futura IA. **Nenhum animal, IA, ataque ou combate está implementado.**
Espécies apenas oficiais (RPG_02); fauna de coleta do RPG_01 aparece só como `PROVISORIO`.

## Onde ficam
- `workspace.Planicies_Douradas.Habitats.Ecologia_Fauna` — Búfalo Colossal, Leão Solar, Interacoes_Ecologicas
- `workspace.Tundra_Congelada.Habitats.Ecologia_Fauna` — Lobo_Artico, Dragao_Glacial, Fauna_Ambiente_Provisoria, Interacoes_Ecologicas
- `workspace.Tundra_Congelada.Exploracao` — Regioes, Mirantes, Areas_Combate, Cavernas, Pontos_Interesse, Trilhas
- `workspace.Tundra_Congelada.Hidrografia` — lago, rio, vaus, riachos congelados

Marcadores: `Part` 4×4×4 invisível, ancorada, `CanCollide/CanQuery/CanTouch=false` (não bloqueiam trilhas nem tiros).
Cada marcador tem o atributo `Id` (único). Rotas guardam os pontos no atributo `Pontos` (JSON `[[x,y,z],...]`), mais `Comprimento`, `De`, `Para`.

## API (servidor)
```lua
local Eco = require(game.ServerStorage.Ecologia.EcologiaFauna)
Eco.porId("H1_PAST_2")                      -- Part do marcador
Eco.lista("Bufalo_Colossal", "Pastagem")    -- todos os marcadores desse tipo
Eco.rota("H1_RAGUA_1")                      -- {Vector3,...}
Eco.recarregar()                            -- reindexa (após mudar marcadores)
```

## Planícies Douradas
| Espécie (oficial) | Porte | Grupos (centro, raio) |
|---|---|---|
| Búfalo Colossal | 14–18 studs até os ombros | H1 Mar de Capim (1250,3750) 600 · H2 Águas Claras (−1400,3750) 480 · H3 Grande Campina (−250,5050) 560 · H4 Terras das Flores (−2750,5150) 480 |
| Leão Solar | 10–13 studs até os ombros | L1 Colinas do Horizonte (−2450,3350) · L2 Bosques Solitários (1250,5150) · L3 Capim Alto Leste (1900,4400) · L4 Campina das Flores (−1650,5550) |

Tipos — Búfalo: `Territorio_Manada`, `Pastagem`, `Descanso_Manada`, `Zona_Filhotes`, `Ponto_Agua`, `Rota_Agua`, `Rota_Fuga`/`Destino_Fuga`, `Campo_Carga` (atributo `Direcao`), `Corredor`.
Leão: `Territorio_Bando`, `Mirante_Observacao` (`VeAlvos`), `Descanso_Sombra` (`Arvore`), `Zona_Caca` (`Alvo`), `Ponto_Emboscada` (`Cobertura`), `Rota_Aproximacao`, `Caminho_Presas`.
Cenas: `Cena_Pastando`, `Cena_Rebanho_ao_Rio`, `Cena_Perseguicao`, `Cena_Defesa_Coletiva`, `Cena_Leao_Observa`, `Cena_Caca_na_Agua`, `Cena_Encontro_Jogador`.

## Tundra Congelada (M5.1 — separada por altitude)
| Espécie (oficial) | Porte | Grupos / territórios | Abrigo |
|---|---|---|---|
| Lobo Ártico (baixo) | 5,5–7 studs | Alcateia_Floresta · Alcateia_Macico · Alcateia_Campos | Toca_Lobos_Cume_Sul (−1290,93,−3900) · Gruta do Gelo Azul · Toca_Lobos_Desfiladeiro (3190,86,−5028) |
| Dragão Glacial (alto) | 18–24 studs (altura) | Coracao_Glacial · Agulha_Azul · Vigia_Branco | Covil_Dragao_Coracao (câmara 901,335,−6607) · Covil_Dragao_Agulha (2729,420,−6576) · Covil_Dragao_Vigia (−1733,375,−5616) |

Tipos — Lobo: `Toca` (câmaras de descanso e filhotes), `Zona_Caca`, `Rota_Patrulha` (circuito), `Arena_Toca` (combate perto da toca). Tamanho de grupo **PENDENTE** (RPG_02 não define). Tocas acessíveis a pé (entradas 16×12 e 14×12), trilhas R_TOCA_* em `_TundraTrilhasJ`.
Dragão: pasta `Covil` com `Plataforma_Pouso` (`DecolagemLivre=true`), `Entrada_Covil`, `Camara_Covil`, `LocalNinhoElegivel` (`Ativo=false`, reaparecimento 30–60 min — OFICIAL), `Descanso_Covil`; `Poleiro` (acima de y 250, `EspacoLivre`), `Zona_Ataque` (`Superficie`), `Areas_Caca_e_Agua`. Atributo `DimensoesProvisorias` = comprimento ~70, envergadura ~100 (**PROVISÓRIO** — usado só para dimensionar entradas/plataformas).
Provisório (RPG_01): Lebre Ártica, Cabra-das-Neves, Mariposa Glacial (`Ponto_Bando`, `Status=PROVISORIO`).
Cenas (`Interacoes_Ecologicas`): 6 tipos — patrulha de lobos, perseguição na neve, alcateia na toca, dragão pousado na plataforma, dragão sobre o gelo, encontro com jogador.
Versão anterior (M5, sem separação por altitude) em `Proto_Restore/Retirados_Tundra/Ecologia_Tundra_M5_v1`.

## Deserto de Cristal (M6) — `workspace.Deserto_de_Cristal.Habitats.Ecologia_Fauna`
| Espécie (oficial RPG_02) | Porte | Grupos | Abrigo |
|---|---|---|---|
| Escorpião Colossal (Veneno/Terra/Fogo) | 16–24 studs de comprimento | ES1 Bando_Mar_de_Dunas · ES2 Bando_Gargantas · ES3 Bando_Canion | Abrigo_Rocha (4850,4400) · Toca_Escorpiao_Gargantas (3555,35,6410) · Toca_Escorpiao_Canion (7610,17,4040) |
| Lagarto Cristalino (Terra/Luz/Raio) | 18–26 studs de comprimento | LC1 Campos_de_Cristal · LC2 Coracao_do_Deserto · LC3 Cavernas_Cristalinas | Grota_Lagarto_Cratera (5535,18,6332) · Galeria dos Geodos · Toca (6500,5250) |

Tipos — Escorpião: `Territorio`, `Toca`/`Abrigo_Rocha`, `Zona_Emboscada_Areia` (`Superficie`, `Cobertura=Poeira`), `Rota_Patrulha`, `Arena_Combate`, `LocalNinhoElegivel` (Ativo=false, 30–60 min OFICIAL).
Lagarto: `Territorio`, `Toca`, `Poleiro_Rochoso` (pontos altos reais para escalada), `Zona_Caca`, `Arena_Combate`, `LocalNinhoElegivel` (Ativo=false); atributo `VarianteProvavel` por grupo (Quartzo Claro / Âmbar Dourado / Ametista Rochosa — os cristais da região usam as mesmas paletas).
Também: `Pontos_Agua` (5), `Fauna_Ambiente_Provisoria` (Raposa-do-Deserto, Abutre de Vidro, Escaravelho Prisma — PROVISORIO, RPG_01), `Interacoes_Ecologicas` (8 cenas). Nenhum dragão no deserto (não há espécie oficial associada).

## Restrições respeitadas
- Túneis das tocas/Gruta servem ao Lobo e ao jogador; o Dragão adulto usa só os covis altos (túnel curto e largo, câmaras 60–80).
- Nada de recinto/curral; nada de estrutura artificial nova. Santuário e vila da Tundra são só `Reserva_*`.
- Ninhos inativos até a fase de criaturas.
