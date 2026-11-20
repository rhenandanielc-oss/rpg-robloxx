# Lobo Ancestral: auditoria de compatibilidade e ensaios controlados (18/11/2026)

> Os números de combate continuam [A TESTAR]/[PROPOSTA]. Esta auditoria **não aprova números** e **não autoriza integrar o kit** ao place principal.
> Os ensaios foram feitos só no place isolado Testes-loboancestral (73543092389791), em Play no PC, com **alvos temporários**. Nenhuma outra criatura real estava disponível, então isto **não é combate entre criaturas reais**.

## 1. Fontes lidas (somente leitura)
- **Regras do projeto e da criatura:**
  - CLAUDE.md;
  - DOCS/ORGANIZACAO-CHATS.md;
  - `DOCS/criaturas/lobo-ancestral.md` (§6am, §6ap–6av);
  - PROJECT-STATE.md;
  - TASKS.md (M3.1–M3.4 todos `[ ]`, M3.2 = "criaturas reais com rig/animações": não iniciado para o Lobo).
- **Documentos de poderes:**
  - `C:/Users/Rhenan/Documents/RPG_Roblox/REFERENCIAS_PODERES_E_EFEITOS.md` v6.2 (§0b, §0c, §0d, §1, §2, §3–§4i);
  - a cópia da raiz do repositório é v5.2: sem §0d, classes de porte por comprimento, kit do Lobo igual.
- **Documentos oficiais:** `RPG_01_Mundo_e_Sistemas_ATUALIZADO.docx` e `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO.docx`, na raiz do repositório, incluindo a "ATUALIZAÇÃO OFICIAL — 30/10/2026".
- **Código:**
  - `BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/kit/`;
  - sistemas de combate em `src/` (Combate_Dragao/Nucleo, ConfigCombate, Passivas, Combate_Dragao_Servidor, IA_Dragao, IA_Urso, Montaria_Dragao_Servidor, Combate_Wyvern).

## 2. Conflito registrado (nada foi alterado)
- **Oficial 30/10 (RPG_01 e RPG_02):** "Cada animal/criatura terá APENAS UM elemento natural". O elemento único de cada criatura, exceto os dragões, está [PENDENTE]. **O Lobo não tem elemento oficial definido.**
- **v6.2 §2:** o Lobo é "Natureza e Ar" (Salto e Investida = Ar, Uivo = Natureza). O `ConfigKitLobo.Elementos` segue {"Natureza", "Ar"}, o que viola a regra oficial.
- **Código principal:** usa um elemento por forma (ConfigCombate) e não tem "Natureza" em `elementosGlobais`.
- **Decisão:** do usuário. Os elementos não foram alterados.
- **Conflitos correlatos na v6.2:**
  - todas as outras criaturas têm de 2 a 4 elementos;
  - a petrificação total do Basilisco contraria "imobilização total NÃO foi aprovada" (PvP oficial);
  - a vantagem ambiental de 10–15% é oficial, mas sem método.

## 3. O que existe de fato para cada outra criatura
Legenda: a = só conceito; b = Blender; c = protótipo isolado; d = poderes testados em Play; e = no place principal.

| Criatura | Porte (doc) | Estado real | Saúde no código | IA que ataca |
|---|---|---|---|---|
| Urso Silvestre | tank (8–10 de ombro) | b, c, d, e (IA_Urso no rpg_roblox 13/11) | IA fere o Humanoid (pata 22, mordida 30); o urso não é derrotável | sim (protege o ovo) |
| Dragão das Montanhas / Glacial / Sombrio | colossal | b, c, d (Teste-animacoes; não no mapa principal) | guardião: atributos Vida/VidaMax 600, **sem Humanoid**; dragão do jogador não recebe dano | sim (guardiões) |
| Wyvern | grande, voa | b, c, d | mesmo Nucleo, sem Humanoid | sim (guardião) |
| Lobo Ártico | ágil (médio) | b, c, d (Teste-animacoes) | Vida@ 400 + `ReceberDano` próprio (esquiva) | não |
| Crocodilo Primordial | tank (grande) | b, c, d (só contra bonecos) | vida própria não encontrada | não |
| Cérbero, Leão, Búfalo | grande / colossal | só b | — | não |
| Basilisco, Escorpião, Lagarto, Serpente, Leviatã | grande / colossal | a/b (blockouts) | — | não |
| Cervo, Javali, Coruja; Javali-do-Brejo | fauna | b, c (IA piloto com Ativo=false) | — | não |

Os valores de vida da v6.2 (por exemplo Búfalo 1100, Leviatã 2600, dragões 2800) **não estão em nenhum código**.

## 4. Matriz de compatibilidade (protótipo do Lobo × mundo)
| Tema | Protótipo do Lobo | Jogo principal (`src/`) | Situação |
|---|---|---|---|
| Alvos válidos | só `Workspace.Teste_LoboAncestral.Alvos`, com Humanoid + HumanoidRootPart | `N:alvosValidos()` no Workspace inteiro, excluindo dono, aliados (`AliadoDe`), jogadores sem `PvPAtivo` e zonas seguras | **incompatível** |
| Dano | `Humanoid:TakeDamage` direto | `N.ferir` (resistências, vulnerabilidade, marcas, FX de reação, `UltimoCombate`, `GuardiaoAtacado`) | **incompatível**: não fere dragões/guardiões (sem Humanoid); guardião atingido não reage |
| Elemento / resistências / imunidades | 2 elementos declarados; nenhum é passado no dano | 1 elemento por forma; ResistenciaFogo/Gelo, Imune* | **incompatível** + conflito oficial |
| Defesa (fórmula oficial 200/(200+Def)) | inexistente: defesa do alvo ignorada (medido) | inexistente também no `src/` | **lacuna de design comum** |
| Esquiva | rolagem de 5–35% no próprio `receberDano` | não existe rolagem; esquiva = janela de tempo e invisibilidade | **diferente** |
| Vida e morte do Lobo | `L.vida` em variável Lua; morte = Estado "Morto"; dano externo só pelo gancho de teste | Vida@/Incapacitado, recuperação, respawn pendente | **incompatível**: nenhuma IA do jogo consegue ferir o Lobo |
| Energia / recarga | 100 + 5/s, `Recarga_<n>`, `os.clock` | 100 + 6/s, `RecargaFim_`/`EmAtaque` | **duplicado** |
| Alcance | ao **centro** (HRP): básicos, raio de acerto do Salto e Instinto | `CorpoRaio×1,6` e `pontoAlvo`/`centroCorpo` para corpos grandes | **falha medida** em grande/colossal |
| Linha de visão | raycast contra tudo, menos o lobo e os jogadores | raycast só contra Terrain | **diferente** |
| PvE/PvP / zonas seguras | nenhuma checagem | `PvPAtivo`, `ZonaSegura`, proteção ao iniciante (oficial) | **incompatível** (risco: ferir jogador em zona segura) |
| Marca / Instinto / revelar | só alvos da pasta; indicador ao dono | — | revela jogadores sem checar PvP/invisibilidade (`PassoInvisivel`) |
| IA | guardião de teste vê só a pasta Alvos | ameaças, `IA_Eventos`, `Invasor_Teste` | **isolada**; dragões e urso nunca miram o Lobo |
| Montaria | não existe | exige `FormaRegional` + `DonoUserId` | **pendente** |
| Noite | ClockTime 18,5–5,5 | Cerebro do dragão: < 6 ou > 19 | **limiar diferente** |
| Catálogo | não registrado; remotes próprios | `habilidadesForma`/`kitForma`; `Catalogo` do Studio com 4 slots (precisa de 5) | **pendente**; arquivos compartilhados exigem acordo |

## 5. Ensaios em Play (alvos temporários, só no Play, removidos)
- **Alvos de ensaio** (Model + HumanoidRootPart + Humanoid, dentro de `Alvos`, com atributos de porte e defesa):
  - **ágil:** 2×2,5×4, vida 150, ataque de ensaio 6;
  - **tank:** 6×7×11, vida 900, "defesa" 0,2, ataque 18;
  - **colossal:** 20×18×40, vida 6000, "defesa" 0,3, ataque 45.
- **Como foi acionado:** tudo pelo gancho `LoboKitTeste`, que passa pelo mesmo `K.pedido` do remoto. **Nenhuma tecla física.**

| Interação | Ágil | Tank | Colossal |
|---|---|---|---|
| Mordida, focinho encostado | **funciona**: 10 | **funciona no limite** (centro a 9 = alcance 7+2): 10 | **falha**: 0 ("sem alvo"; centro a 16) |
| Garra, focinho encostado | **funciona**: 8,8 (com marca) | **falha**: 0 (centro 9 > 6+2) | **falha**: 0 |
| Salto com alvo, a 25 da superfície | dano 13,2, mas patas da frente 3,3 dentro do alvo | dano 13,2, patas 5,3 dentro | dano 13,2, mas **pivô 7 studs dentro do corpo** (falha visual/colisão) |
| Salto sem alvo por cima | — | passou por cima (ápice 8,1 > altura 7) e pousou atrás: **funciona** | não testado |
| Investida a 12 da superfície | **funciona**: 13,2, para na superfície | **funciona**: 13,2 | **funciona**: 13,2 |
| Investida com parede no caminho | — | **funciona**: para na parede, 0 de dano | não testado |
| Salto com alvo atrás da parede | — | **funciona**: recusado (sem linha de visão) | não testado |
| Uivo | **funciona** (bônus no lobo; independe do alvo) | idem | idem |
| Instinto (superfície a 70) | **funciona**: percebido a 71 | **funciona**: 73 | **falha**: não percebido (centro a 80 = limite do raio) |
| Caçador Noturno (21h) | **funciona**: mordida 11,2; com marca 12,2; esquiva 15% | não testado | não testado |
| Marca da presa | **funciona**: +10% na mesma presa | funciona (13,2 = 1,2 × 10 × 1,1) | funciona |
| Ataques do alvo contra o Lobo (gancho `atacar`) | Lobo cai em 69 golpes (esquiva 2/69) | em 23 golpes (0 esquivas) | em 10 golpes (1 esquiva); a "defesa" dos alvos **não é usada** pelo kit |
| Tempo para derrotar (rotação real do kit, 25 s) | não medido | 8,3 de dano/s → ~108 s | 5,2 de dano/s → **~19 min** (Mordida e Garra não alcançam) |
| IA guardiã (sozinha com o alvo) | **funciona**: Uivo + Investida, 12 | **funciona**: Salto (13,2) + Uivo + Salto; nunca Mordida | Salto (13,2) + Uivo; nunca Mordida |
| IA com parede entre o guardião e o tank | — | **funciona**: calmo, sem reação | não testado |
| Cancelamento | alvo morre no voo: sem dano e sem erro | — | — |
| Cancelamento: Lobo morre na Investida | tarefas canceladas; pedido seguinte recusado ("lobo inativo") | — | — |

- **Não testado (sem evidência):** criaturas reais (nenhuma no place); voo, água e subterrâneo; PvP real; multiplayer; celular; idades; montaria.
- **Defesa, resistências e imunidades:** não existem no kit.
- **Artefato do ensaio:** zerar a vida do Humanoid de um alvo o deixa morto de vez (estado Dead). O alvo ágil foi recriado.

## 6. Bugs de integração × balanceamento
**Bugs de integração (corrigir antes de qualquer entrada no mundo):**
1. Alvo restrito à pasta de teste e só a Humanoid: não fere dragão nem guardião (Vida@).
2. Dano fora do `N.ferir`: pula resistências, marcas, reação dos guardiões e `UltimoCombate`.
3. Sem checagem de PvP, zona segura, dono e aliado.
4. Alcance, raio de acerto do Salto e Instinto medidos ao centro. Em corpos grandes:
   - Mordida e Garra falham;
   - o Salto pousa dentro do alvo;
   - o Instinto perde colossais.
5. Vida e morte do Lobo isoladas: nada no jogo consegue feri-lo.
6. Energia, recarga e noite duplicadas, com outros limiares.
7. Revelar e pegadas ignoram PvP e invisibilidade.

**Balanceamento (decisão do usuário, não é bug):**
- Lobo com 400 de vida sem defesa contra golpes de 18/45: cai em 23/10 golpes.
- ~19 min contra um colossal de 6000.
- Esquiva base de 5%.
- Faltam a fórmula de defesa oficial e a vantagem elemental de 1,15/0,85.
- O elemento do Lobo está pendente.

## 7. Menor próximo passo proposto (aguardando aprovação)
Só nos arquivos do Lobo, no place isolado: **medir alcance e contato até a superfície do alvo**.
- Ponto mais próximo do corpo do alvo, e não o centro, nos básicos, no raio de acerto e no pouso do Salto e no raio do Instinto.
- Pouso do Salto diante da **superfície**.
- Repetir esta mesma bateria (ágil, tank e colossal).

Sem tocar em `src/` nem em scripts compartilhados. A ligação com `N.ferir`, alvos válidos, PvP e zonas seguras fica para uma etapa combinada com o dono do sistema de combate.

## 8. r5: alcance e contato até a SUPERFÍCIE (18/11/2026, aprovado como próximo passo pelo usuário; só arquivos do Lobo)
- **Mudança:** função `pontoProximo` no servidor (ponto mais próximo das partes visíveis do alvo e distância horizontal). Usada em:
  - básicos (alcance + 0,5);
  - mira e pouso do Salto com alvo (pousa a `folgaPouso` 5,8 da superfície, acerto se ≤ `raioAcertoSuperficie` 8,5);
  - raio do Instinto;
  - distância de ameaça e de ação da IA.
- **Config:** `folgaPouso` e `raioAcertoSuperficie` [A TESTAR].
- **Studio:** instalado e conferido por checksum (servidor 49485 bytes / config 4507). Backups `LoboKit_Servidor_antes_superficie` e `ConfigKitLobo_antes_superficie` em `ServerStorage.Backup_KitLobo_efeitos_r3_2026-11-17`. Place salvo.
- **Bateria repetida em Play** (alvos temporários, removidos):

| Interação | Ágil | Tank | Colossal |
|---|---|---|---|
| Mordida encostada | **funciona** 10 | **funciona** 10 (antes: limite) | **funciona** 10 (antes: 0) |
| Garra encostada | **funciona** 8,8 | **funciona** 8,8 (antes: 0) | **funciona** 8,8 (antes: 0) |
| Salto com alvo a 25 e a 45 | acerta 13,2; pivô a 5,8 da superfície, patas fora (antes: 3,3 dentro) | idem (antes: 5,3 dentro) | idem (antes: pivô 7 dentro do corpo) |
| Investida a 12 | funciona 13,2 | funciona | funciona |
| Instinto, superfície a 70 / a 85 | 70 / fora | 70 / fora | **70** (antes: fora) / fora |
| Rotação real por 20 s | — | 9,6 de dano/s → ~94 s (antes ~108) | 9,6 de dano/s → **~10,4 min** (antes ~19) |
| IA guardiã | — | Salto, Uivo, **Mordida 11**, Investida | Salto, Uivo, **Mordida 11 ×10** (antes: nunca mordia) |

- **Limites conferidos (tank):** Mordida acerta a 7,4 e não a 8,0; Garra acerta a 6,4 e não a 7,0.
- **Regressão nos alvos pequenos originais:**
  - salto curto acerta;
  - alvo a 55 da superfície: recusado;
  - atrás da parede: recusado;
  - móvel lateral a 8 studs/s: acerta, com 10 de antecipação e a 5,5 da superfície no pouso.
- **Efeito colateral:** com o alvo a 12 studs do centro, o salto agora percorre só 5,2 (pousa com o focinho encostado). O alcance mínimo de 8 é medido até a superfície.
- **Evidências:** `Lobo_Compatibilidade_r5_superficie.mp4`, `compat_r5_superficie_prancha.jpg`.
- **Continua pendente (integração combinada):** `N.ferir`, alvos fora da pasta e sem Humanoid (Vida@), PvP e zonas seguras, vida e morte do Lobo, energia, recarga e noite.

## 9. Diagnóstico de dano e proteções (18/11/2026; aprovado pelo usuário após o r5; nada alterado no place nem no código)
- **M0:**
  - Testes-loboancestral (73543092389791), último save v35. Scripts r5 instalados = locais (checksum: servidor 1752851, config 310595659, cliente 650755383).
  - **Nenhuma criatura real no place.** Sem `Combate_Dragao`/`Nucleo`, sem zona segura, `PvPAtivo` nil. O Lobo não tem Humanoid nem `GuardiaoNinho`.
- **Criaturas reais:**
  - rpg_roblox (Urso) e Teste-animacoes (guardiões dragão/Wyvern, Lobo Ártico) estavam **em Play com outros chats**.
  - Mesmo livres, as ferramentas não copiam modelos entre places, e o comportamento real (IA_Dragao, `N.ferir`) depende de `src/`, ausente no place isolado.
  - **Nenhum teste contra criatura real foi feito.** Os ensaios abaixo usam **réplicas sem IA**, rotuladas `ReplicaEnsaio`, criadas e removidas só no Play.
- **Réplicas:**
  - guardião com vida por atributo (`GuardiaoNinho`, `Vida`/`VidaMax` 600, sem Humanoid, 14×12×28);
  - Humanoid dentro de uma parte com a tag `ZonaSegura` (mesma regra de `Nucleo.emZonaSegura`);
  - Humanoid com `AliadoDe` = dono;
  - Humanoid grande (14×12×28, vida 3000).
- **"Regra do Nucleo":** reproduzida numa sonda só de leitura, a partir de `alvosValidos`/`emZonaSegura`/`N.ferir`, sem rodar o Nucleo.

| Interação | Resultado | Valores / evidência | Tipo |
|---|---|---|---|
| Mordida/Garra/Salto/Investida na réplica de guardião (Vida@) | **falha** | Vida 600 → 600: Mordida "sem alvo", Salto "alvo inválido", Investida "parou em obstáculo". O Nucleo o trata como alvo válido (`danoGuardiao`) | falha do kit |
| Mesmas ações na réplica em zona segura | **falha** (fere) | 200 → 190 / 191,2 / 186,8 / 186,8. O Nucleo bloquearia | falha do kit |
| Mesmas ações na réplica aliada | **falha** (fere) | 200 → 190 / 191,2 / 186,8 / 186,8. O Nucleo bloquearia | falha do kit |
| Mesmas ações na réplica grande com Humanoid | **funciona** (r5 preservado) | 3000 → 2990 (Mordida), 2991,2 (Garra), 2986,8 (Salto e Investida); pivô a 5,8–7,3 da superfície | — |
| Caminho do dano | **falha de contrato** | `Humanoid:TakeDamage` direto. Sem resistência, vulnerabilidade, FX "reacao" nem `GuardiaoAtacado`. `UltimoCombate` = nil em todos os acertos (o `N.ferir` grava na fonte e no alvo) | falha do kit |
| Instinto revela aliado escondido na vegetação | **falha** | aliado percebido a 18,5 e "1 revelado" enviado ao dono; réplica em zona segura também percebida | falha do kit / regra indefinida (PvP e invisibilidade) |
| IA guardiã de teste perto de aliado / zona segura | **falha** | Uivo + Investida + Mordida ×2 nos dois; vida 200 → 177 | falha do kit |
| Parede / linha de visão (regressão r5) | **funciona** | Salto recusado "sem linha de visão"; Investida para em obstáculo | — |
| Criatura fere o Lobo pela via normal (`N.ferir`) | **não testado em Play** (sem Nucleo no place) | por código: o Lobo não tem Humanoid nem `GuardiaoNinho`, nenhum ramo de `N.ferir` se aplica, então o dano não entra; o atributo `Vida` 400 é só informativo | falha do kit (integração) |
| Reação do alvo atingido | **não testado** | réplicas sem IA; reação real depende de IA_Dragao/IA_Urso | limite do modelo de teste |
| Dono e jogador com PvP desligado | **não testado em Play** (um só jogador) | por código: o kit só aceita a pasta `Alvos`, então jogadores nunca são alvos (sem PvP algum); o dono nunca é alvo | regra indefinida (PvP do Lobo) |
| Lobo pela IA contra guardião real | **não testado** | sem criatura real | limite |
| Celular / multiplayer / PvP real | **não testado** | — | — |

- **Regras ainda indefinidas:** elemento do Lobo (oficial pede um só; v6.2 diz Natureza+Ar); se o Instinto pode revelar jogadores e invisíveis no PvP; fórmula de defesa oficial `200/(200+Def)` (não existe no kit nem em `src/`).
- **Evidências:**
  - `studio/review/Lobo_Diagnostico_protecoes.mp4`: zona segura ferida, aliado ferido, guardião por atributo imune;
  - `diag_protecoes_prancha.jpg`;
  - `diag_lobo_referencia_x_studio.jpg`: Lobo × referência. Visual sem adaptação nova: mesma malha, rig e textura já aprovadas; efeitos r4 e espontâneo r2.

## 10. r6: proteções no kit (18/11/2026; aprovado pelo usuário: "Proteções no kit"; só arquivos do Lobo)
- **Mudança em `LoboKit_Servidor.luau`:** cópia local da regra de proteção do jogo (`Nucleo.alvosValidos`/`emZonaSegura`, só leitura; `src/` não foi alterado). A função `protegido(L, alvo)` bloqueia:
  - o dono;
  - aliado do dono (`AliadoDe`);
  - alvo dentro de parte com a tag `ZonaSegura`;
  - jogador sem `workspace.PvPAtivo`.
- **Onde vale:** básicos, Salto (recusa com o motivo), Investida (alvo protegido conta como obstáculo, sem dano), dano (última barreira), marca da presa, Instinto (pegadas e revelar) e IA.
- **Logs:** novo `[PROTECAO]`.
- **Studio:** instalado e conferido por checksum (51503 bytes). Backup `LoboKit_Servidor_r5_antes_protecao` em `ServerStorage.Backup_KitLobo_efeitos_r3_2026-11-17`. Place salvo.
- **Ensaios em Play** com as mesmas réplicas sem IA rotuladas (`ReplicaEnsaio`), removidas. **Não são criaturas reais.**

| Interação | Antes (§9) | Depois (r6) |
|---|---|---|
| Mordida/Garra/Salto/Investida em alvo dentro da zona segura | fere (200 → 186,8–191,2) | **funciona**: 200 → 200. Salto "alvo protegido (zona segura)"; Mordida/Garra "sem alvo"; Investida para sem dano |
| As mesmas ações em aliado (`AliadoDe` = dono) | fere | **funciona**: 200 → 200. Salto "alvo protegido (aliado)" |
| Alvo grande comum (regressão do r5) | 3000 → 2986,8 | **funciona**: igual (10 / 8,8 / 13,2 / 13,2) |
| Zona segura criada com o Lobo já no ar | — | **funciona**: "SaltoPredatorio sem dano em … (zona segura)", vida 3000/3000 |
| Instinto perto de aliado escondido / zona segura | revelava | **funciona**: não percebido, 0 revelados. Controle sem `AliadoDe` no mesmo arbusto: revelado |
| IA de teste (sem dono) perto de alvo em zona segura | atacava (200 → 177) | **funciona**: nenhuma decisão, 200/200 |
| IA de teste (sem dono) perto de aliado de um jogador | atacava | ainda ataca (200 → 177). **Coerente com o Nucleo**: aliado é sempre aliado do dono, e guardião sem dono não tem aliados. Regra para lobo selvagem × aliados: indefinida |
| Parede (regressão) | recusa | **funciona**: "sem linha de visão" |
| Guardião com vida por atributo (sem Humanoid) | imune | **ainda falha**: 600 → 600 (depende da ligação com `N.ferir`, etapa combinada) |
| Jogador com PvP desligado e dono | por código | **não testado em Play** (um só jogador; o kit só aceita a pasta Alvos); regra implementada por código |
| Criatura ferindo o Lobo pela via do jogo | por código | **não testado** (sem Nucleo no place); continua impossível pelo código |

- **Evidências:** `studio/review/Lobo_r6_protecoes.mp4`, `r6_protecoes_prancha.jpg`, `r6_lobo_referencia_x_studio.jpg` (Lobo × referência; sem adaptação nova de malha, rig ou textura).
- **Pendente:**
  - ligação com `N.ferir`/`alvosValidos` (guardiões Vida@, resistências, `UltimoCombate`, reação dos guardiões);
  - vida e morte do Lobo pela via do jogo;
  - teste contra criatura real (exige copiar um modelo real ao place isolado);
  - PvP real, multiplayer e celular.

## 11. r7: Mordida e Garra andando e correndo (18/11/2026; pedido do usuário: "o lobo em vez de atacar parado, possa atacar andando, pois se não, não existirá PvP de verdade")
- **`AdaptadorLobo.luau`:** clipes **parciais** derivados dos aprovados, sem dado novo nem Blender.
  - `Mordida_Andando`: pescoço, cabeça, mandíbula, orelhas, pálpebras, juba e pelos do pescoço.
  - `Garra_Andando`: os mesmos ossos mais a pata dianteira **direita** (a Garra golpeia com a direita: maior amplitude em MaoD 0,78 e AntebracoD 0,60).
  - Os outros ossos ficam com peso 0 e seguem a marcha por baixo.
- **`LoboKit_Servidor.luau`:**
  - **Em movimento** (seguindo o dono, ou IA voltando ao posto): o básico usa o clipe parcial e **não** prende o estado (continua "Livre"). `L.basicoAte` impede outra habilidade até o fim do golpe.
  - **Parado:** clipe inteiro, como antes.
  - Na r7b a detecção de movimento passou a ignorar o lobo parado pelo gancho de teste.
- **Studio:** instalado e conferido por checksum (servidor 52452 bytes, adaptador 7156). Backups `LoboKit_Servidor_r6_antes_andando` e `AdaptadorLobo_antes_andando`. Place salvo (v37).
- **Testes em Play** (o Lobo seguindo o dono; alvo de ensaio Humanoid 3×5×2 posto à frente; acionado pelo gancho, sem tecla física):

| Caso | Resultado | Valores |
|---|---|---|
| Mordida andando (3,2 studs/s) | **funciona** | estado "Livre" durante o golpe; Lobo andou 5,4 studs em 1,8 s; dano 10 |
| Garra andando | **funciona** | andou 5,4; dano 8,8 |
| Mordida correndo (22 studs/s) | **funciona** | correu 38,2–38,6 studs em 1,8 s; dano 10–11 |
| Garra correndo | **funciona** | 38,6 studs; dano 8,8 |
| Patas durante o golpe (cliente, altura relativa ao pivô) | **funciona** | andando: PeE 0,47 contra 0,50 na marcha; MaoE 0,71 contra 0,71. Correndo: PeE 0,85 contra 0,88; MaoE 1,13 contra 1,16. Só MaoD muda (patada) |
| Mordida parado (controle) | **funciona** | estado "Mordida" (clipe inteiro), dano 11 |

- **Limites e pendências:**
  - a cabeça morde na direção em que o Lobo corre (cone de 70°), sem virar o corpo para o alvo;
  - não há clipe próprio de "mordida em corrida" (a parcial reaproveita a Mordida parada);
  - PvP real e multiplayer não testados (um só jogador; o kit continua aceitando só a pasta Alvos).
- **Evidências:** `studio/review/Lobo_r7_ataque_andando.mp4`, `r7_ataque_andando_prancha.jpg`, `r7_lobo_referencia_x_studio.jpg`.

## 12. r8: contrato de criatura no kit (18/11/2026; place v38)
- **Pedido:** "Prossiga" no passo de ligar o kit ao sistema de dano. Feito só no kit do Lobo; `src/` e o Nucleo **não** foram tocados.
- **Contrato adotado:** é a mesma convenção do Lobo Ártico.
  - No modelo: atributo `Criatura = true`, `Vida`/`VidaMax` e uma BindableFunction `ReceberDano(valor, elemento, fonte)`.
- **O que mudou em `LoboKit_Servidor.luau` (57708 bytes, checksum 240065038; backup `LoboKit_Servidor_r7_antes_contrato`):**
  - **O Lobo registra o contrato** (Vida 400 [PROPOSTA]). `ReceberDano` passa por esquiva/resistências e grava `Vida`.
  - **Alvos:** além da pasta Alvos, aceita no workspace modelos com Humanoid vivo, `Criatura` ou `GuardiaoNinho` com Vida > 0. Ignora `Incapacitado`/`Morto`.
  - **Proteções:** passam a incluir o próprio Lobo e qualquer criatura do mesmo dono (`DonoUserId`).
  - **`aplicarDano` segue esta ordem**, e o log informa por qual via o dano entrou:
    1. `Nucleo.ferir`, se `ServerScriptService.Combate_Dragao.Nucleo` existir;
    2. Humanoid;
    3. `ReceberDano` do alvo;
    4. guardião por `Vida` (só com dono; grava UltimoDano, IA_Eventos e Incapacitado em 0);
    5. `Vida` de criatura.
  - Grava `UltimoCombate` no alvo.
- **Testes em Play** (réplicas temporárias, removidas no fim; nenhuma criatura real neste place):

| Caso | Resultado | Valores |
|---|---|---|
| Contrato no Lobo do dono | **funciona** | Criatura=true, Vida 400/400, ReceberDano presente |
| Réplica de guardião fora da pasta Alvos | **funciona** | Mordida 600→590; Salto 590→576,8 (via Vida do guardião; não há Nucleo no place) |
| Réplica de criatura com ReceberDano próprio (resistência 50%) | **funciona** | Mordida 10→5 (300→295); Investida 13,2→6,6 (295→288,4) |
| Salto em clone do Lobo do mesmo dono | **bloqueado (correto)** | "alvo protegido (mesmo dono)" |
| **Duelo Lobo × Lobo**, 24,1 s (Lobo do dono guiado pelo gancho × Lobo guardião, IA de teste, sem dono) | **funciona** | dano nos dois sentidos via ReceberDano, com esquivas ("aplicado 0.0"); o do dono terminou com 247/400 (3 acertos, 2 recebidos), o guardião com 347,2/400 (12 acertos, 11 recebidos). A diferença vem do guia simples do teste e não mede equilíbrio |

- **O que não foi testado:**
  - o caminho `Nucleo.ferir`, porque não há Nucleo neste place;
  - criaturas reais de outros places;
  - PvP entre jogadores, multiplayer e celular.
- **Proposta para o Nucleo compartilhado [PROPOSTA; precisa de aprovação do usuário e do dono do combate; não aplicada]:**
  1. Em `N.ferir`: quando o alvo tiver `Criatura` + `ReceberDano`, chamar `ReceberDano(valor, elemento, atacante)` em vez de só procurar Humanoid. Assim o Lobo, o Lobo Ártico e outras criaturas com contrato recebem dano dos dragões.
  2. Em `alvosValidos` e nas listas de ameaça da IA: incluir modelos com `Criatura` (sem dono ou com `PvPAtivo`), mantendo as regras de dono, `AliadoDe` e ZonaSegura.
  3. Teste de falha depois da mudança: criatura sem `ReceberDano`, `Invoke` com erro, alvo morto e dono saindo do jogo.
- **Evidências:** `studio/review/Lobo_r8_duelo_lobos.mp4`, `r8_duelo_lobos_prancha.jpg`, `r8_lobo_referencia_x_studio.jpg`.

## Evidências (`BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/review/`)
- `Lobo_Compatibilidade_ensaios.mp4` (21 s, Play, tempo real):
  - colossal: Mordida, Salto e Investida;
  - tank: Mordida e Garra;
  - IA contra o ágil.
- `compat_ensaios_prancha.jpg`.
- `compat_lobo_referencia_x_studio.jpg`: referência × Lobo no Studio.
