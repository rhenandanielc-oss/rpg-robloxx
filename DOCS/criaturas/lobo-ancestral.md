# Lobo Ancestral — ficha do subchat

Criatura **domesticável** da **Floresta Ancestral**. Espécie-base **Lobo**, que tem duas formas regionais: Lobo Ancestral (este subchat) e Lobo Ártico (Tundra Congelada, subchat próprio).

Fontes: `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO` (§0, §1, §2, §5–7, §10, §14–15, §19) e `RPG_01` (só cita o Lobo no catálogo). A **ATUALIZAÇÃO OFICIAL de 30/10/2026** prevalece sobre o que vem depois no documento.

Regras de convivência: `DOCS/ORGANIZACAO-CHATS.md`. Studio um chat por vez (`DOCS/estado/studio-em-uso.md`).

Ficha criada em 03/11/2026, só com leitura. Nada foi alterado no Studio nem em `src/`.

## 1. Identidade

| Item | Valor | Status |
|---|---|---|
| Bioma | Floresta Ancestral | [OFICIAL] |
| Locomoção | Terrestre; melhor locomoção em florestas | [OFICIAL] |
| Papel | Velocidade, esquiva e perseguição | [OFICIAL] |
| Fraqueza | Menos vida e defesa que as criaturas grandes | [OFICIAL] |
| Corpo | Esguio e atlético (o Ártico é mais robusto) | [OFICIAL] |
| Porte adulto | 5,5–7 studs até os ombros | [OFICIAL] |
| Estágios | Ovo + 5 modelos (Bebê, Jovem, Pré-adulto, Adulto, Ancião) | [OFICIAL] |
| Animações | Naturais; filhotes com animações próprias e brincalhonas | [OFICIAL] |
| Ambiente | Pegadas, respingos e reação da vegetação | [OFICIAL] |
| Montaria | A partir do **Adulto**, com **sela leve** | [OFICIAL] |
| Ataque básico | Sequência de mordidas e garras, com animações variadas (fora dos slots de habilidade) | [OFICIAL] |
| Padrões visuais | **Cinza da Floresta**, **Marrom Selvagem**, **Areia do Bosque** (Etapa 23). São só cosméticos: não definem elemento nem raridade | [OFICIAL] |
| Cores exatas de cada padrão | Não confirmadas | [PENDENTE] |
| Evolução estética por estágio e adornos por raridade | — | [PENDENTE] |
| Painel de referência | `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/01-lobos-urso-leao.png`, painel 01: esguio, ágil, pelagem com musgo e folhas | referência visual |

## 2. Elemento e habilidades

### Elemento
- **[OFICIAL — 30/10/2026]** Cada criatura tem **um único elemento natural**. Não há 2º/3º elemento, alternância nem fusão elemental.
- **[DECISÃO DO USUÁRIO — 10/11/2026, aprovada em conceito]** Elemento do Lobo Ancestral: **Natureza** (pedido `DOCS/pedidos/2026-11-10-lobo-ancestral-habilidades-passivas.md`).

### Habilidades — kit aprovado em conceito (10/11/2026)
- **[OFICIAL — 30/10/2026]** No mínimo 1 passiva + 3 ativas; o ataque básico de mordidas e garras fica **fora** dos slots.
- **[DECISÃO DO USUÁRIO — 10/11/2026]** 2 passivas + 3 ativas:
  1. **Passiva — Instinto de Caça:** pistas perceptíveis (odor, pegadas, vestígios) de inimigos na perseguição e de ninhos na exploração. Indica direção/pista; **não** revela coordenadas, posição através de obstáculos nem entrega recompensa.
  2. **Passiva — Caçador Noturno:** só à noite (estado único calculado no servidor), melhora agilidade de perseguição/esquiva e o dano físico de mordida/garra. Termina ao amanhecer.
  3. **Ativa — Salto Predatório:** alvo selecionado; salta até ele e golpeia ao aterrissar. Alcance, linha de visão e acerto validados no servidor; sem teleporte nem atravessar paredes.
  4. **Ativa — Uivo Ancestral:** uivo audível que fortalece temporariamente **só o próprio lobo** (mobilidade/esquiva); sem buff de grupo.
  5. **Ativa — Investida:** avanço rápido na direção escolhida; golpe físico no primeiro alvo válido; obstáculo interrompe; no máximo 1 acerto por alvo por uso.
- **Números:** nenhum aprovado. Os valores de protótipo estão em §6ae como **[PROPOSTA]**.
- **[PROPOSTA — histórico, superada]** As versões por elemento (§6) e as fusões direcionais (§7 do RPG_02) contrariam a regra de elemento único. Não implementar.

## 3. Atributos (Etapa 24)
- **[OFICIAL — 24.1]** São 6 atributos: Vida, Defesa, Força, Velocidade, Energia e Poder Elemental. A comparação é entre Adultos de nível 100. Vantagem ambiental de 10–15%; raridade influencia 1–5%.
- **[PROPOSTA — 24.2, NÃO APROVADA]** Números do Lobo Ancestral:
  - escala 1–5: Vida 2, Defesa 2, Força 3, Velocidade 5, Energia 4, Poder Elemental 2;
  - valores absolutos: 2.950 HP, Defesa 85, Força 140, Energia 135, Poder Elemental 105;
  - velocidade: terra 38 studs/s (manobra 5), água 12 studs/s (manobra 2), sem voo.
- **[SIMULAÇÃO ILUSTRATIVA, NÃO OFICIAL]** Duelos de teste em §19.2: Lobo × Escorpião, Lobo × Urso, Cérbero × Lobo.

## 4. Mundo e habitat (segundo os registros do mapa)
- `DOCS/estado/mundo-floresta.md`, 21–22/10:
  - 16 territórios de lobos (2–3 tocas cada). Cada toca tem uma `Familia_*` com `NinhoLobos`, `Ovo_Lobo` placeholder, `SpawnLoboAlfa`, `SpawnLoboAdulto` e 3 `SpawnFilhote`.
  - A Aldeia_Nevoa tem o guardião `Lobo_Alfa`.
  - Pathfinding chega às 16 tocas.
  - Tudo são **marcadores**: não há lógica de lobos, ovos nem criação.
- Ninhos de lobo ficam em tocas sob raízes gigantes, bosques densos e pequenas cavernas.
- **[OFICIAL]** Ninhos reaparecem em 30–60 min. A quantidade de ninhos por jogador ainda é [PROPOSTA].
- Assets: `BLENDER/Biblioteca/D_Cavernas_Habitats/Toca_Lobo_A.glb` e `Toca_Lobo_B.glb`.
- A V9 retirou 13 rochas de toca/abrigo para `Proto_Restore/Retirados_V9`. **Conferir no Studio** se as tocas continuam íntegras.
- **[PENDENTE]** Tamanho da alcateia (o RPG_02 não define). Lore do nascimento de mamíferos por ovos.

## 5. O que já existe

### Roblox Studio (segundo os registros de 26/10; não conferido nesta sessão)
- `ServerStorage.Biblioteca_Criaturas.Modelos` → **Lobo Ancestral** feito no próprio Studio:
  - 6,57 de ombro;
  - rig Motor6D com segmentos rígidos, **sem pele deformável**;
  - 13 animações (KeyframeSequence);
  - 3 padrões por tingimento;
  - `Estado` = Testes aprovados (Play/PC). 12 lobos animados sem queda de FPS mensurável.
- `Biblioteca_Criaturas.Catalogo` registra a forma, com as 4 habilidades históricas.
- O `Cerbero_Sombrio_PROVISORIO` foi feito a partir de um clone deste lobo.
- **Atenção:** o PILOTO de 27/10 registrou que o Studio abriu uma versão antiga do place (PlaceVersion 394), sem `Biblioteca_Criaturas`. Backup completo: `Documents/RPG_Roblox/BACKUPS/RPG_BKP_2026-10-26_C1_criaturas.rbxl`. Conferir qual place está aberto antes de qualquer trabalho.

### Blender (`BLENDER/Criaturas/Blockouts/`)
- **Scripts** em `build/`:
  - `lobo_base.py`: base canina compartilhada com o Ártico e o Cérbero;
  - `build_Lobo_Ancestral.py`, `lobo_v3.py`, `lobo_v4.py`, `lobo_v5.py`: o `lobo_v5` também é importado pelo `lobo_artico.py`;
  - `pipeline_final.py` (flag `LOBO`) e `esqueletos.py` (`canideo_v3`).
- **Arquivos** em `Lobo_Ancestral/`: `_blockout`, `_refinado` e `_final` nas versões V2, v3, v4 e v5 `.blend`.
- **Exports** em `_Export/`: `Lobo_Ancestral.glb` (V2, 32 ossos, 28 ações), `_v3.glb`, `_v4.glb` e `_v5.glb`.
- **Estado da V5** (27/10), o modelo mais recente:
  - pelagem em cartões com alpha, **técnica aprovada pelo usuário**;
  - 42 ossos, incluindo 10 `Pelo_*` de balanço;
  - cerca de 35,9 mil tris;
  - cabeça 12% maior;
  - auditoria 8/14/6 e 7/12/9;
  - **a anatomia da V5 não foi aprovada como final.**
- **Roblox:** **nenhuma versão GLB (V2–V5) foi importada nem testada.** A importação é manual (Import 3D), segundo `PILOTO-ROBLOX-LOBO.md`.
- `review/Lobo_Ancestral/` é citado nos registros, mas **não foi encontrado** no repositório nesta inspeção.

### Código (`src/`)
- Nada específico do lobo: sem IA, combate, montaria nem sons. A IA, os sons e a montaria existentes são dos dragões e são arquivos compartilhados.

## 6. Pendências
1. **Decisões do criador:**
   - elemento único;
   - lista final de passivas e ativas e seus efeitos;
   - números (24.2 é só proposta);
   - cores dos 3 padrões;
   - tamanho da alcateia.
2. **Modelo:**
   - aprovar ou ajustar a V5 frente ao painel 01;
   - pendências abertas: patas finas de frente, máscara creme pouco visível, brilho da pupila, pelos espetados na testa;
   - custo alto: precisa de LOD antes de uso em matilha.
3. **Estágios:** só existe o Adulto. Faltam Bebê, Jovem, Pré-adulto, Ancião e ovo.
4. **Roblox:**
   - importar a V5 (Import 3D manual);
   - conferir SurfaceAppearance com AlphaMode Transparency, DoubleSided, ordenação e FPS;
   - testar escala, pés no chão e animações;
   - publicar as animações exige a conta do usuário.
5. **Animações:** foram auditadas só numericamente (a auditoria V2 marcou Corrida com membros embolados). Seguir `padrao-movimento-criaturas` (fluidez).
6. **Sistemas (não iniciados):**
   - IA selvagem e alcateia;
   - companheiro domesticado;
   - montaria com sela leve;
   - sons (uivo, rosnado, passos);
   - VFX;
   - tudo com validação no servidor.

## 6b. Novo modelo pela referência de 03/11/2026 (em andamento, NÃO aprovado)
- **Referência preservada:** `REFERENCIAS/floresta-ancestral/lobo-ancestral/lobo-ancestral-referencia.png` (cópia em `BLENDER/Criaturas/Lobo_Ancestral_Ref/ref/`).
- **Pasta nova:** `BLENDER/Criaturas/Lobo_Ancestral_Ref/`, com:
  - `criar_lobo_ref.py`: modelo por código; skin → voxel; cor por região; marcas verdes só visuais;
  - `prancha.py`: referência × render;
  - `render_existente.py`: render de .blend antigo, sem salvar;
  - `asset-brief.md`.
  - A V2–V5 em `Blockouts/` **não foi alterada**.
- **Rodadas HIGH** (`review/r01`–`r04`, pranchas `Prancha_rNN.png`):
  - **r01–r02:** pernas finas e longas, cabeça pequena, mechas retas virando espinhos.
  - **r03:** tufos esculpidos parecendo calçamento; cernelha 7,46, acima do limite oficial de 7.
  - **r04:** mechas acompanhando a pele, sem espinhos, mas com aspecto "amassado". Cores sem a sela escura clara. Focinho em tubo e orelhas em cone. Escala corrigida (fator 0,902).
  - **Custo r04:** 422 mil tris (HIGH, não é a malha de jogo).
- **Decisão do usuário (03/11):** usar base no Meshy. As rodadas por código ficam só como histórico.
- **Meshy Image to 3D (03/11):**
  - autorizado pelo usuário; 35 créditos consumidos (saldo antes: 685);
  - parâmetros: meshy-7.1, geometria 2k, textura 4k PBR; entrada `ref/entrada_meshy.png`, recorte da referência;
  - script: `meshy_img3d.py`; resultado em `meshy/g01/`: GLB de 1,44 M tris e texturas 4k.
- **Normalização** (`normalizar_meshy.py` → `review/m02`): orientação pelo eixo do tronco (PCA), rotação Z de 56°, frente em −Y, pés em Z = 0, cernelha 6,6.
- **Pose neutra** (`endireitar.py` → `review/m03`):
  - a cabeça vinha girada 36° (herança da pintura) e foi rodada de volta, com transição suave no pescoço;
  - a cauda foi desenrolada pela linha central, mantendo o comprimento do arco (4,54) e a altura.
  - As patas mantêm a passada desencontrada da pintura.
- **LOW de jogo** (`low_lobo.py` → `low/l02`, revisão em `review/l02`):
  - malha soldada e decimada para **17.998 tris** (1 MeshPart; limite de 20k);
  - 1 material; UV nova com a cabeça ×2,2 em texels;
  - bake Cycles HIGH→LOW de cor e normal em 2048, reduzido para **1024**; GLB de 3,7 MB.
  - Reimportação do GLB conferida (`validar_glb.py`): 1 malha, 1 UV, 2 imagens 1024, cernelha 6,70 (medida com o pelo), altura 8,50 (orelhas), comprimento 14,04 (com a cauda), zmin −0,006.
  - 11 bordas abertas e 25 arestas não-manifold em 27 mil.
- **Diferenças restantes frente à referência:**
  - patas em passada;
  - leve arrasto diagonal no pelo do peito, deixado pela correção da cabeça;
  - peito creme menor e mais acinzentado;
  - leque da cauda assimétrico;
  - marcas verdes só na cor (sem emissão), mais suaves na LOW;
  - mechas mais grossas na LOW.
- **Situação:** **aguardando a aprovação visual do 3D.** Ainda não há rig, Studio nem commit.

## 6c. Rig e animações do Meshy g01 (03/11/2026, para avaliação, NÃO aprovado)
Pasta `BLENDER/Criaturas/Lobo_Ancestral_Ref/`. As velocidades e durações abaixo são **parâmetros dos clipes, não regras oficiais**.

### Arquivos usados e gerados
| Etapa | Script | Entrada → saída |
|---|---|---|
| Base | (aprovada) | `review/m03/Lobo_Meshy_endireitado.blend` (HIGH, 1,44 M tris) |
| Malha do rig | `preparar_rig.py` | → `low/l03/Lobo_Ancestral_LOW_rig.blend` (+ `marcos_rig.json`, texturas 1024) |
| Lábios | `medir_labio.py` | → `low/labio.json` (traço escuro da textura) |
| Rig (2 passadas) | `rig_lobo.py` | 1ª: repouso com 4 patas apoiadas → `low/l03/Lobo_Ancestral_LOW_repouso.blend`; 2ª (`sem_repose espelhar`): esqueleto simétrico + pesos → `rig/Lobo_Ancestral_Rig.blend` |
| Clipes | `anim_lobo.py` | → `rig/Lobo_Ancestral_Anim.blend` (23 ações `Lobo_*`), `clipes/LoboAncestral_*.json`, `clipes/manifesto_clipes.json` |
| Vídeos | `video_clipes.py`, `folha.py` | → `videos/Lobo_<clipe>_normal.mp4` (30 fps) e `_lento.mp4` (10 fps = 1/3), 3 vistas, chão quadriculado correndo na velocidade do clipe |
| Exportação | `exportar_lobo.py`, `validar_glb_rig.py` | → `export/Lobo_Ancestral.glb` (5,3 MB), `export/validacao_glb.json` |
| Studio | `studio_montar_lobo.luau` | JSON → KeyframeSequences com KeyframeMarker (ainda não executado) |

### Malha de jogo para o rig
- **Total:** 18.687 tris numa MeshPart (corpo 18.160 + língua e dentes 527), 1 material.
- **Texturas:** cor e normal 1024.
- **Recentro em X:** −0,65, pela linha média do tronco.
- **Cabeça:** decimada com densidade ×4.
- **Boca:** corte pela curva escura dos lábios; parede interna de cada lábio → palato e assoalho → garganta; língua e 24 dentes. A boca fechada não mostra o interior.
- **Bordas abertas:** 17, todas fora da boca, herdadas do Meshy (11 originais). Não foram fechadas.

### Rig
- **Ossos (39):**
  - Raiz, Pelve, Coluna1–2, Peito, Pescoco1–2, Cabeca, Mandibula;
  - Orelha E/D, Juba E/D, JubaPeito, Cauda1–7;
  - patas dianteiras: Escapula/Braco/Antebraco/Mao/Dedos E/D;
  - patas traseiras: Coxa/Canela/Metatarso/Pe E/D.
- **Pesos:**
  - calor numa cópia voxel fechada, depois Data Transfer para a LOW;
  - boca pelos atributos;
  - suavização ×3 fora do focinho;
  - no máximo 4 influências; 0 vértices sem peso.
- **Repouso:**
  - as 4 patas apoiadas (z mínimo 0,00) e simétricas por par;
  - ombros e quadril simétricos;
  - IK de 2 ossos por pata, com desvio de repouso de 0,0001.
- **Olhos:** são só textura (não há globo ocular). O "observar" usa cabeça e orelhas, não os olhos.

### Clipes (QA automático de `manifesto_clipes.json` + revisão visual por folhas de quadros)
"Malha mín." = vértice mais baixo fora da pata. O valor negativo nas poses apoiadas é o pelo das pernas sobre o chão (compressão). Barriga, peito e cauda ficam acima do chão em todos os clipes.

| Clipe | Finalidade | Duração | Loop | Teste (IK / escorregão / malha mín.) | Pendências |
|---|---|---|---|---|---|
| Repouso | parado, respiração discreta | 4,0 s | sim | 0 / — / +0,27 | — |
| Observar | olha E/D com cabeça e orelhas | 4,5 s | não | 0 / — / +0,27 | sem movimento de olhos |
| Andar | 4 tempos, sequência lateral | 1,2 s (36 q) | sim | 0 / 0 / +0,18 | — |
| Trote | diagonais | 0,67 s (20 q) | sim | 0 / 0 / +0,28 | — |
| Corrida | galope transverso, com suspensão | 0,47 s (14 q) | sim | 0 / 0 / +0,38 | coxa traseira torce no recolhimento; dianteira bem dobrada no balanço |
| Partida | parado → trote | 1,33 s | não | 0 / — / +0,20 | — |
| Freada | trote → parado | 1,33 s | não | 0 / — / +0,15 | — |
| VirarE / VirarD | giro de 90° no lugar, 16 passos (a raiz gira; o jogo aplica o giro ao modelo) | 2,4 s | não | 0,29 / — / +0,26 | uma pata atrasa em parte do giro |
| Sentar / Sentado / LevantarSentado | transição; parado sentado | 1,3 / 4,0 / 1,1 s | não / sim / não | 0 / — / −0,66 (metatarso no chão) | pose sentada ainda pouco natural (coxas abertas) |
| Deitar / Deitado / Descanso / Despertar / LevantarDeitado | esfinge; cabeça baixa; desperta | 1,8 / 4,0 / 5,0 / 2,6 / 1,6 s | Deitado e Descanso em loop | 0 / — / −0,79 (antebraço no chão) | antebraço e metacarpo com pelo sob o chão |
| Salto | agacha, impulsão, fase aérea, aterrissagem | 1,45 s | não | 0 / — / +0,04 | — |
| Uivo | cabeça erguida, boca aberta sustentada | 4,0 s | não | 0 / — / +0,04 | — |
| Rosnar | ameaça: cabeça baixa, orelhas para trás, boca entreaberta, tremor | 2,4 s | não | 0 / — / +0,08 | sem lábio repuxado (o rig não tem) |
| Mordida | antecipação → bote → fecha | 1,0 s | não | 0 / — / +0,14 | — |
| Garra | pata dianteira direita varre | 1,05 s | não | 0 / — / +0,04 | golpe discreto demais |
| Impacto | recuo com giro de cabeça | 0,65 s | não | 0 / — / +0,05 | — |

- **Marcadores** (no JSON e nas ações): Contato e Antecipação (Mordida e Garra), UivoInicio e UivoFim, RosnadoInicio e RosnadoFim, Impulso, Decolagem e Aterrissagem, GiroCompleto, Impacto, entre outros. Não há dano, habilidade nem IA.
- **Acabamento secundário:** cauda, juba e orelhas seguem com atraso o movimento do corpo (pela velocidade da raiz) e oscilam nos ciclos.
- **GLB reimportado:**
  - 1 malha, 39 ossos, 23 ações, 2 imagens 1024;
  - 0 vértices sem peso, 0 com mais de 4 influências;
  - pose de 6 ossos-chave em 5 clipes idêntica (erro 0,000).
  - A `Raiz` recebeu peso 0,02 num vértice interno para não sumir no Roblox.

### Roblox Studio (03/11)
- **Reserva:** feita e liberada.
- **Inspeção somente leitura:** a instância aberta é o arquivo local `Teste-animacoes_CR.rbxl` dos dragões (PlaceId 0), sem `Biblioteca_Criaturas`. Nada foi alterado nele.
- **Pendente (passo manual do usuário):** abrir um place novo isolado (Baseplate) e fazer Import 3D de `export/Lobo_Ancestral.glb`.
- **Não feito ainda:** testes em Play, desempenho com várias cópias e publicação das animações (depende da conta do usuário). Nada foi testado em emulação nem em celular real.

## 6d. Correção do alinhamento (03/11/2026, aprovada pelo usuário; para avaliação)
**Medição:**
- `medir_alinhamento.py`: centro em X por fatia, apoios e ossos.
- `orto_alinhamento.py`: vistas ortográficas frente/cima/lado com a linha central (vermelha) e os 4 apoios (amarelo).
- Resultados em `review/alinh/`, comparando cada etapa: m02 normalizado → m03 pose neutra → l03 LOW → repouso → clipe.

**Causas encontradas e etapa em que surgiram:**
1. **Cauda deslocada +0,65 a +1,1 em X (`endireitar.py` v1, pose neutra).**
   - A cauda reta era centrada em x = 0, com o tronco em x ≈ −0,6 naquela etapa (o recentro vem depois, no `preparar_rig`).
   - O eixo da cauda era calculado pela média, que o leque assimétrico puxava.
   - O pivô do giro da cabeça estava em x −0,45, e não na linha média.
2. **Cotovelos em x ±0,49, com ombros e punhos em ±1,28 (`rig_lobo.py` v1).**
   - A seção que media o cotovelo incluía o pelo do peito.
   - Resultado: patas dianteiras em "X" e ombro e juba arrastados quando o repouso moveu cada pata ~0,8 para os lados.
3. **Arrasto diagonal na frente da juba:** transição curta do giro da cabeça (`endireitar.py` v1).

**O que NÃO era defeito:**
- **Juba mais volumosa em +X:** a diferença entre o centro de massa e o centro do contorno no peito era de +0,44 já no m02, antes de qualquer correção. É pelagem natural do Meshy.
- **Tronco:** já estava centrado (±0,3).
- **Apoios:** já eram simétricos depois do repouso.

**Correções na origem** (originais preservados em `review/endireitar_v1.py`, `review/rig_lobo_v1.py`, `review/anim_lobo_v1.py`, `review/m03`, `low/l03`, `rig/`, `clipes/`, `videos/`, `export/`):
- **`endireitar.py` v2, variante "largo" → `review/m04c`:**
  - linha média do tronco medida (x −0,574 naquela etapa);
  - pivô da cabeça e eixo da cauda sobre essa linha;
  - eixo da cauda pelo meio do contorno da faixa central;
  - transição longa do giro da cabeça.
  - A variante "pescoco" (`m04b`) foi reprovada: a cabeça só girava 60%.
- **`preparar_rig.py` → `low/l04`:**
  - mesma aparência, UV, textura e boca;
  - curva dos lábios da l03 deslocada −0,074 em y (`low/labio.json`). A medição nova, em `low/labio_m04c_bruto.json`, foi descartada porque pegava a trufa.
  - 18.554 tris; 13 bordas abertas.
- **`rig_lobo.py` v2 → `rig2/`:**
  - cotovelo e joelho sobre a reta ombro→punho e quadril→jarrete na vista frontal (cotovelos em ±1,34);
  - cotovelo 0,30 atrás da linha (olécrano), para a perna dianteira ter folga de IK (0,35; com o cotovelo sobre a reta a folga era 0,13 e o IK falhava no trote);
  - joelho +0,06 para fora.
- **`anim_lobo.py`:**
  - os clipes não mudaram (nenhuma compensação por clipe);
  - entrou a medida `alinhamento` no manifesto: tronco visível, centro e diferença de avanço de cada par de apoios, desnível de ombros e quadris, centros dos pares.
  - Saída em `clipes2/` e `rig2/Lobo_Ancestral_Anim.blend`.

**Resultado (`clipes2/manifesto_clipes.json`):**
- **Tronco visível:** x médio +0,10 em todos os clipes. Era +0,10 a +0,33 por fatia e subia a +1,1 na cauda.
- **Apoios:** centro de cada par em 0,000 ±0,002.
- **Desnível de ombros e quadris:** ≤ 0,20 nos ciclos, ≤ 0,28 no Impacto.
- **IK:** 0 em Repouso, Andar, Trote, Corrida e na maioria dos clipes; Impacto 0,10; Viradas 0,26.
- **Escorregão:** 0 nos ciclos.
- Nas Viradas, o "deslocamento" medido do tronco e dos apoios é o próprio giro de 90° da raiz.

**Evidências** em `videos2/`:
- `Prancha_orto_antes_depois.png` e `Prancha_antes_depois_referencia.png`;
- MP4 normal e lento dos 23 clipes.

**GLB:** `export2/Lobo_Ancestral.glb`, reimportado (`export2/validacao_glb.json`):
- 1 malha, 18.690 tris, 39 ossos, 23 ações, 2 texturas 1024;
- 0 vértices sem peso; pose idêntica em 5 clipes;
- cernelha 6,73, altura 8,49, comprimento 14,06.

**Diferenças visuais restantes:**
- juba mais cheia em +X (natural do Meshy);
- tronco +0,10 em X (pelagem);
- pelo das pernas apoiadas abaixo do chão no sentado e no deitado (compressão);
- coxa traseira torce no recolhimento do galope;
- garra discreta;
- sentado com coxas abertas.

**Studio:** não foi usado nesta etapa.

## 6e. Correção da leitura frontal do peito/juba (03/11/2026, para avaliação)
**Medição antes de editar:**
- `analise_frontal.py` + `sobrepor_frontal.py` geram uma vista frontal ortográfica com:
  - classes de malha separadas: corpo (amarelo), juba/peito (ciano) e cabeça (magenta);
  - linha central;
  - eixos do crânio, do esterno, da coluna e dos ombros/pelve.
- Resultados em `review/frontal/antes|depois/` (imagem `Sobreposicao_frontal.png` + `analise.json`) e `review/frontal/Sobreposicao_antes_depois.png`.

**Achado (rig2):**
- **Ossos:** tronco, ombros, pelve e apoios estavam centrados.
- **Juba deslocada em sentidos opostos por altura**, o que se lê como mechas descendo em diagonal (um "cisalhamento"):
  - parte alta (z 5,2–7,2): centro em −0,24 a −0,43, com só 34–47% da massa em +X;
  - peito baixo (z 3,6–4,8): centro em +0,13 a +0,40, com 65–71% da massa em +X.
- **Esterno:** pontos mais à frente do peito entre +0,04 e +0,39.
- **Crânio:** inclinação residual de +2,4° (nariz em +0,09, orelhas niveladas); não foi corrigida.
- **Pescoço:** acompanha a juba; não havia arrasto próprio fora dela.

**Tentativas:**
1. **v1, espelhamento** (`simetrizar_juba.py`): a metade −X foi espelhada sobre a +X, na geometria, na textura (bake) e nos pesos. **Reprovada:** a projeção dobrou a malha e o bake deixou manchas escuras no pescoço, estragando a silhouette lateral. Arquivos guardados em `rig3_v1_espelho/` e `review/simetrizar_juba_v1_espelho.py`.
2. **v2** (`desentortar_juba.py`), só na região juba/peito (máscara macia, à frente dos ombros) e sem projeção nem bake:
   - primeiro, um **giro local de 18° no plano frontal** em torno do centro do peito, que endireita a direção das mechas. Desvanece acima de z 6,2, para não mexer na juba alta atrás da cabeça. O ângulo e o sinal saíram da comparação −20/−12/+12/+18/+24 (`review/giro/`).
   - depois, uma **recentragem lateral suave por altura**, para o centro da juba voltar a 0.
   - Variantes descartadas: só recentragem (`rig3_passada1`, as mechas continuavam diagonais) e giro sem desvanecimento (`rig3_giro_alto`, que deixava um tufo perto da orelha).

**Resultado (`rig3/`):**
- **Juba:** o centro ficou em −0,10 a +0,08 de z 3,6 a 5,6. Na faixa z 6,0–6,4 sobra −0,18 a −0,24 (juba alta mais larga em −X, pelagem natural).
- **Esterno:** −0,01 a +0,06 entre z 3,2 e 4,4; −0,20 e −0,33 em z 4,8–5,2.
- **No close frontal:** o peito forma um "V" vertical, como na referência.
- **Preservado:** 3/4, lateral, máscara facial e marcas verdes.
- **Mudou só posição de vértice:** 3.726 de 9.374 (máx. 0,73; perto da cabeça, máx. 0,48).
- **Idênticos ao rig2 (hash):** UV, topologia, textura de cor, normal e pesos.

**Verificação dos clipes:**
- Os 23 clipes regenerados em `clipes3/` ficaram idênticos ao `clipes2` (diferença 0), exceto o Descanso: 0,0002 na `Raiz`, pela elevação automática que lê a malha do peito.
- O alinhamento, o IK e o contato no manifesto são os mesmos da §6d.
- Nenhum vértice da juba entra nas cápsulas das patas dianteiras (raio 0,25) em 11 clipes (`juba_patas.py`).

**GLB:** `export3/Lobo_Ancestral.glb`, validado por reimportação:
- 18.690 tris, 39 ossos, 23 ações, 2 texturas 1024;
- 0 vértices sem peso; pose idêntica em 5 clipes;
- cernelha 6,73; largura 4,05 (antes 4,17, pela juba menos larga).

**Evidências** em `review/juba_cmp/`:
- `Prancha_Repouso_antes_depois_ref.png`;
- `Close_peito_antes_depois_ref.png`;
- `Prancha_Andar_Corrida.png`: 3 momentos de cada, frontal e 3/4;
- vídeos finais em `videos3/`.

**Restante:**
- juba alta um pouco mais larga em −X (orgânico);
- crânio +2,4°;
- os itens da §6d (pelo das pernas apoiadas, coxa no galope, garra, sentado).
- `rig2/` e `export2/` estão preservados para comparação.
- O Studio não foi usado.

## 6f. Patas, peitoral e cabeça retos na vista frontal (03/11/2026, pedido do usuário: "deixe 100% reto")
**Medição** (`medir_patas_frontal.py` + `linhas_patas.py`: linha central da malha de cada pata por altura, comparada à linha dos ossos, em ±1,3).

**No rig3:**
- **Patas dianteiras deslocadas para +X** (direita na imagem), em +0,1 a +0,27 por altura:
  - a E se abria para fora no antebraço (+1,41 a +1,55);
  - a D entrava para dentro no cotovelo (−0,65 a −0,87).
- **Volume dos ombros** acima das patas: +0,24 a +0,27.
- **Traseira E** aberta para fora (+1,71 contra −1,45 da D).
- **Cabeça:** girada 2,4° (trufa 0,09 para o lado).
- **Peitoral:** a geometria estava centrada. O que pesava para a direita era a COR:
  - medido numa vista frontal só com a cor da textura (`cor_peito.py`), porque a luz da cena enviesava a medida feita no render iluminado;
  - mancha marrom-escura grande no ombro e no alto da pata D, com o lado E claro.

**Correções na origem (só posição de vértice e tom da textura; ossos, pesos, UV, topologia e apoios intactos):**
1. **`endireitar_patas.py` → `rig4/`:**
   - linha central da malha de cada uma das 4 patas levada à linha dos ossos da própria pata, por um campo lateral suave por altura (máscara macia, com transição para o corpo);
   - peitoral entre e acima das patas recentrado.
   - 2.683 vértices, máximo 0,57.
2. **`simetrizar_frente.py` v3 → `rig5/`:**
   - **cabeça:** yaw de −2,42° em torno do atlas; trufa em x = 0,000.
   - **tom da cor** na frente dos ombros e do peito, lado −X: a diferença entre a cor média suavizada do lado espelhado e a do próprio lado, atenuada a 70% e limitada a ±0,10, é somada à textura original. Os traços do pelo e a normal ficam como estavam.
   - **Variantes descartadas:**
     - bake de cópia espelhada (`rig5_v1_bake`): 69% dos texels sem acerto e borda magenta;
     - cópia texel a texel (`rig5_v2_copia`): quebrava os traços e manchava o peito;
     - tom sem limite: estourava o creme.

**Resultado:**
- **Patas dianteiras:** ±1,33 do antebraço ao punho; apoios em +1,33 e −1,21 (centro +0,06). As 4 patas no chão (z 0,00).
- **Patas traseiras:** simétricas (±1,4 a ±1,5).
- **Cabeça:** centrada.
- **Peitoral:** mancha escura removida; o creme do peito fica centrado no render sem luz (`review/patas/albedo_rig4_rig5.png`).
- **3/4 e lateral:** preservadas.

**Clipes** (`clipes5/`):
- animação igual ao `clipes3` (≤ 0,0002), exceto Sentar, Sentado e LevantarSentado (0,02–0,03 na raiz, pelo apoio automático no chão).
- IK, escorregão e alinhamento iguais aos da §6d.
- A juba não entra nas patas (`juba_patas.py`, 0 vértices).

**GLB:** `export5/Lobo_Ancestral.glb`, reimportado:
- 18.690 tris, 39 ossos, 23 ações, 2 texturas 1024;
- 0 vértices sem peso; cernelha 6,73.

**Evidências** em `review/patas/`:
- `Frontal_linhas_antes_depois.png`, `Frontal_perspectiva_3etapas.png`;
- `Prancha_Repouso_antes_depois_ref.png`, `Close_peito_final.png`;
- vídeos em `videos5/`.

**Preservados para comparação:** `rig2`, `rig3`, `rig4`, `export2` e `export3`.

## 6g. Lobo 100% simétrico por espelho da metade D (04/11/2026, usuário: "NÃO MUDOU NADA... a perna tá pra direita")
**Medição no rig5** (`medir_assimetria_patas.py`: malha de cada pata E contra o espelho da pata D, por altura):
- os **ossos** das duas patas já estavam exatamente simétricos na pose (Repouso q0 = repouso do rig);
- a **malha** da pata dianteira E (+X, direita na imagem) diferia do espelho da D em 0,25–0,50 (mediana por altura; até 0,75 no ombro): pata torcida, punho e dedos virados para dentro, ombro e peitoral E pendendo para fora;
- a medida da §6f (só a linha central por percentis) não enxergava a torção, por isso a correção anterior quase não mudou a leitura.

**Variante descartada** (`rig6_v1_ajuste/`, scripts `espelhar_frente.py` + `espelhar_textura.py`): ajuste não rígido da metade +X sobre a superfície espelhada da −X, com cor e normal copiadas do espelho. As patas ficaram retas, mas o pelo do peito e do ombro E ficou amassado e facetado, porque a topologia dos dois lados é diferente.

**Correção adotada** (`espelhar_metade.py` → `rig6/`):
1. Corte da malha no plano x = 0; a metade +X é descartada e substituída pelo espelho exato da metade −X.
2. O espelho leva junto UV (mesma textura), atributos `interior`/`mandibula`, pesos com troca de nomes E↔D e normais personalizadas espelhadas.
3. Costura: 687 vértices fundidos, com pesos simetrizados.
4. A metade D é mais densa: o espelho dava 21.550 tris, acima do limite de 20 mil do Roblox. Aplicado Decimate simétrico (eixo X), com a cabeça preservada → **18.138 tris**; normais transferidas da malha antes da redução; máximo de 4 influências.
5. Esqueleto inalterado (já era simétrico).

**Conferência:**
- erro de espelho máximo 0,0 (todo vértice tem par exato);
- 0 vértices sem peso; z mínimo 0,00;
- juba dentro das patas (`juba_patas.py`): 0 vértices em Repouso, Andar, Trote, Corrida, Sentado e Deitado.

**Efeitos colaterais (lado E agora igual ao D):**
- as marcas verdes do peito E somem; ficam as do lado D, espelhadas;
- a cauda fica um pouco mais fina e perde parte da ponta clara, que estava mais no lado E;
- no meio do peito o pelo forma um "V" (risca) na linha de espelho.

**Evidências** em `review/espelho/`:
- `AD_Repouso_0_frontal.png`, `AD_Repouso_0_tres_quartos.png`, `close_r5_r6.png`;
- `Prancha_movimento_rig5_rig6.png` (lateral e Andar/Corrida, frontal e 3/4).

**Clipes** (`clipes6/`, `anim_lobo.py` no rig6): os 23 foram regenerados.
- erro de IK 0 e escorregão 0 nos andamentos;
- alinhamento do tronco, ombros e apoios 0,000 em todos os clipes simétricos (Garra e Impacto são assimétricos de propósito).

**GLB** (`export6/Lobo_Ancestral.glb`, 5,25 MB), reimportado com `validar_glb_rig.py`:
- 18.138 tris, 39 ossos, 23 ações, 2 texturas 1024;
- 0 vértices sem peso, máximo de 4 influências.
- A "Icosphere" listada é o formato de osso que o próprio importador cria; não faz parte do arquivo e já aparecia no export5.

**Vídeos:** `videos6/` (8 clipes, normal e lento).

**Preservados:** `rig5`, `export5`, `clipes5`, `videos5` e `rig6_v1_ajuste`.

## 6h. Patas retas e dentro do corpo (04/11/2026, usuário: "quero as pernas retas, as duas, dentro do corpo, não pra fora")
**Medição no rig6:**
- linha dos ossos das dianteiras em ±1,3;
- borda externa da pata no cotovelo chegava a 1,8, enquanto o peito mede ±1,6 → as patas abriam para fora;
- traseiras com o pé em ±1,55, aparecendo para fora atrás das dianteiras na vista frontal.

**Correção** (`patas_para_dentro.py` → `rig7/`): malha e ossos de repouso deslocados juntos, com o mesmo campo lateral por altura; o sinal do lado mantém a simetria exata.
- **Dianteiras:** antebraço, punho e dedos verticais em ±0,95; articulação do ombro em ±1,22; escápula fixa.
- **Traseiras:** metatarso e pé verticais em ±1,00; joelho em ±0,95; quadril fixo.
- 1.944 vértices movidos (máximo 0,55); pesos, UV e topologia intactos.
- IK refeito (alvos, polos e ângulo do polo); desvio da malha em repouso com IK ligado: 0,0004.

**Resultados:**
- **Clipes (`clipes7/`):** IK 0 e escorregão 0 em todos, exceto Impacto (0,018). Distância mínima entre patas 0,91. Juba dentro das patas: 0, com 0,3 vértice por quadro no Deitado.
- **GLB (`export7/Lobo_Ancestral.glb`):** 18.138 tris, 39 ossos, 23 ações, 0 vértices sem peso.
- **Vídeos:** `videos7/`.

**Evidências:** `review/dentro/Prancha_Repouso_rig6_rig7.png` e `review/dentro/videos7_quadros.png`.

**Correção v2 (04/11, usuário: "parece um osso fora do lugar nas pernas"):**
- **Erro da v1 (`rig7_v1_dobrado/`):** os ossos encadeados compartilham cabeça e cauda, então somar o deslocamento em cada um movia duas vezes. Cotovelo e punho foram para 0,56 enquanto a malha ficou em 0,95: o osso saía de dentro da perna e entortava a perna nos clipes.
- **Agora:** as posições são calculadas de forma absoluta a partir do repouso original. Ossos: ombro 1,22; cotovelo, punho e dedos 0,95; joelho 0,95; metatarso e pé 1,00.
- **Clipes regenerados (`clipes7`):** IK ≤ 0,036, exceto Impacto (0,073); escorregão 0; juba nas patas 0 em todos.
- **GLB `export7`:** 18.138 tris, 23 ações, 0 vértices sem peso.
- **Vídeos:** `videos7`.
- **Evidências:** `review/colunas/Frontal_v1_bug_x_corrigido.png` e `close_r6_r7.png`.
- **Medido:** a mancha escura vista entre as patas de frente é a CAUDA (vértices Cauda2–7, y +0,1 a +6), não pelo do peito. Ela não foi alterada.

## 6i. Caroços escuros no começo das patas dianteiras (04/11/2026) → `rig8/`
**Base:** o pedido citava `rig5`/`clipes5`/`export5`, mas a versão atual já era `rig7` (espelho §6g e patas retas §6h). As comparações cobrem as duas.

**Diagnóstico** (`diag_ombro.py`: closes de frente, 3/4 e lado em quatro modos; mesma câmera e luz):
- **Textura (causa principal):** mancha marrom-escura com o núcleo quase preto no topo interno de cada pata, logo abaixo do peito. Parece uma sombra da axila do modelo Meshy assada na cor. Na vista só com a cor, sem luz, ela aparece mesmo sem iluminação.
- **Geometria (causa secundária):** uma aba de pelo do peito fica sobre o topo da pata e forma um degrau que faz sombra. Na 3/4 há um degrau na frente do cotovelo. Não há saliência de volume (render em argila).
- **Pesos do rig:** normais (mapa de osso dominante); não são a causa.
- **Sombreamento:** só a sombra natural sob o peito.

**Correção na origem:**
1. **`suavizar_axila.py`:** suavização de Taubin (λ 0,5 / μ −0,53, preserva o volume), 12 iterações, só na junção peito–escápula–topo da pata. Usa máscara macia e não toca bordas abertas nem a linha central. 182 vértices; deslocamento mediano 0,086, máximo 0,31.
2. **`corrigir_axila.py`:** ajuste só do tom, por face, em duas passadas.
   - ganho de luminância até a média da vizinhança (raio 0,85, percentil 50), o que mantém o matiz: o marrom continua marrom;
   - só o que o ganho não alcança no núcleo recebe cor somada, com o matiz da pele vizinha;
   - a UV é espelhada, então os dois lados compartilham os mesmos texels.
   - **Descartados:** v1 (cor clara somada) acinzentava a marca marrom; a primeira passada isolada (`rig8_passada1/`) deixava resíduo.
3. **Não feito:** acrescentar pelo, cortar o volume do ombro ou mexer em UV, pesos ou rig.

**Verificação:**
- **Malha (`qa_malha.py`), rig7 → rig8:** mesmas 14 bordas abertas (nenhum buraco novo) e mesmos 16 não-manifold; dobras > 120° na região caíram de 60 para 42; simetria com erro 0,0; 18.138 tris; 0 vértices sem peso.
- **Juba nas patas:** 0 nos 23 clipes.
- **Clipes (`clipes8`, 23):** IK máximo 0,073 (Impacto); escorregão 0.
- **GLB `export8` reimportado:** 39 ossos, 23 ações, 2 texturas 1024.
- **Vídeos:** `videos8`.

**Pata que parecia dobrada ou levantada em Repouso** (`apoio_patas.py`: malha deformada mais closes rentes ao chão):
- **rig5:** a dianteira E estava na ponta dos dedos. Dedos a 0,16 do chão, sola inclinada 6°, 23% da sola encostada; a D tinha 42% e 1,1°.
- **rig8: corrigida.** As duas dianteiras estão iguais: dedos no chão, sola a 0,7°, 48% encostada.
- **Traseiras: pendência pequena.** Ficam 0,03 acima do chão, com a almofada de trás erguida, o que é natural no lobo.

**Resíduo:** ainda há uma sombra suave sob a borda do peito no topo das patas (oclusão real da aba do peito), sem o núcleo escuro.

**Evidências** em `review/ombros/`:
- `Prancha_ombros_antes_depois_ref.png` (frente, lado e 3/4, com a região marcada);
- `Zoom_axila_zoom_frente_r5_r7_r8.png`, `Zoom_axila_zoom_34_r5_r7_r8.png`;
- `diag_rig5_*.png`, `diag_rig7_*.png`;
- `Prancha_movimento_rig5_rig8.png` (Repouso; Andar 0/9/18; Corrida 0/4/9);
- `Repouso_patas_chao_r5_r8.png`, `qa_rig*.json`, `r5_apoio_patas.json`, `r8_apoio_patas.json`.

**Preservados para comparação:** `rig5`, `rig7`, `rig8_passada1`, `export5` e `export7`.

## 6j. Pelo balançando com o vento (04/11/2026, usuário: "quero que os pelos balancem com o vento, não pelos estáticos") → `rig9/`
**Ossos de pelo** (`ossos_pelo.py`): 17 ossos novos, totalizando 56, filhos dos ossos do corpo:
- `PeloNuca1/2`, `PeloJubaE1/E2/D1/D2`, `PeloBochechaE/D`, `PeloPeito1/2`;
- `PeloDorso1/2`, `PeloBarriga`, `PeloCotoveloE/D`, `PeloCoxaE/D`.

**Pesos:**
- Dentro da cápsula de cada osso, o peso cresce com a distância ao eixo do osso do corpo: a camada rente ao corpo (abaixo do percentil 35) fica presa e a camada externa (até o percentil 97) fica solta.
- 2.390 vértices recebem peso de pelo, até 0,86 nas pontas; máximo de 4 influências; simétrico.
- **Descartado:** "afastamento de uma malha suavizada" (v1/v2). Quase não pegava a juba, que é um volume grosso.
- **Conferência visual:** `review/vento/pesos_v3.png`.

**Vento nos clipes** (`anim_lobo.py`, função `vento`):
- Cada mecha gira empurrada pelo ar relativo: o vento ambiente `VENTO_AMB`, da frente-esquerda, mais o ar do próprio movimento (0,12 × velocidade).
- Ganho geral `FORCA_VENTO = 2`. O movimento combina uma rajada lenta, ~0,35 Hz, com tremulação, ~1,6 e ~3,1 Hz.
- As frequências dão um número inteiro de ciclos na duração do clipe, então o loop fecha sem salto.
- Cadeias "…2" e a ponta da cauda atrasam e balançam mais. Juba antiga e cauda também recebem o vento.
- Nos clipes em que a cauda fica apoiada (sentar e deitar), o vento na cauda é reduzido a 20%, para o ajuste ao chão não "pular".

**Medido** (`medir_vento.py`, relativo ao peito):
- **Repouso, Sentado e Deitado:** balanço pico a pico mediano 0,08, p90 0,22, até 0,40 nas pontas.
- **Fechamento do loop:** 0,03, igual a um quadro normal; maior passo por quadro 0,032 (sem saltos).
- **Juba nas patas:** 0 nos clipes medidos.
- **Clipes (`clipes9`):** IK máximo 0,073; escorregão 0.
- **GLB `export9`:** 56 ossos, 23 ações, 18.138 tris, 0 vértices sem peso, nenhum osso sem peso.

**Evidências:** `review/vento/Juba_vento_Repouso.gif`, `Juba_vento_4quadros.png` e vídeos em `videos9/`.

**Vento em tempo real (rascunho, não instalado):** `studio_vento_pelo.luau`.
- LocalScript que soma o balanço por cima dos clipes, usando `workspace.GlobalWind` e a velocidade do modelo, por tag `PeloVento`, só até 90 studs.
- Se for adotado, os clipes devem ser gerados sem o vento assado.
- Precisa de aprovação para ir a `src/` (é um sistema novo de cliente, ao lado do `MovimentoVivo_Cliente`).

**6j-2. Força do pelo pela força do vento do clima** (04/11, usuário: "haverá climas no jogo... dependendo da força do vento, se assemelhará a força"):
- **Vento do jogo:** é o `workspace.GlobalWind`, que os scripts de ambiente e clima variam (cerca de 3–15 no Play; Montanhas (7,0,3)). Os scripts de vegetação já o seguem.
- **Clipes:** agora saem **sem** vento gravado (`clipes10`, `export10`; `FORCA_VENTO = 0`, opcional `LOBO_VENTO_ASSADO`). O vento vem do jogo em tempo real.
- **Fórmula única:** `vento_pelo_comum.py`, a mesma no Blender e no Roblox.
  - `forca(w) = min(1,75; 0,10 + (w/12)^0,85)`, com w = |GlobalWind − 0,12 × velocidade do corpo|;
  - rajada mais tremulação, com frequências que sobem com o vento;
  - ângulo = amplitude-base × força × parte do vento perpendicular à mecha × ganho.
- **Módulo gerado:** `PeloVento_Lobo.luau` (amplitudes, fases e direção de repouso das 27 mechas, no espaço glTF).
- **Script de cliente (rascunho, não instalado):** `studio_vento_pelo.luau`. Usa a tag `PeloVento`, o atributo `PerfilPelo` e um atributo `Abrigo` 0..1 para cavernas e tocas. Atua só até 90 studs e desfaz a própria soma a cada quadro.
- **Prévia no Blender** (`previa_vento.py`, Repouso), balanço pico a pico das mechas, mediana / p90 / máximo:

  | Vento | Studs/s | Mediana | p90 | Máximo |
  |---|---|---|---|---|
  | Calmaria (só a respiração do clipe) | 0 | 0,03 | 0,05 | 0,11 |
  | Brisa | 4 | 0,05 | 0,10 | 0,16 |
  | Forte | 12 | 0,08 | 0,20 | 0,37 |
  | Tempestade | 25 | 0,12 | 0,31 | 0,54 |

  Evidência: `review/vento/Pelo_por_forca_do_vento.gif`.
- **`export10`:** 56 ossos, 23 ações, 18.138 tris, nenhum osso sem peso; clipes com IK máximo 0,073 e escorregão 0.
- **Não verificado:** a orientação do eixo depois da importação no Roblox (o importador pode girar o modelo) e o custo no celular. Fica para o teste no Studio.

## 6k. Pata dianteira reta de lado, como na referência (04/11/2026, usuário: "pernas totalmente retas... embaixo ela tá contorcida para trás") → `rig10/`
**Medido no rig9** (`lado_perna.py` + `desenhar_linhas.py`: lateral ortográfica com a linha dos ossos):
- a malha do antebraço já era vertical (centro y ≈ −4,1 de z 1,0 a 2,8);
- a pata ficava 0,25 à frente da coluna, o que fazia a perna parecer dobrada embaixo;
- os ossos não seguiam a perna: cotovelo na borda de trás (y −3,34) e punho na borda da frente (y −4,44). O antebraço cruzava a perna na diagonal e, ao animar, torcia a parte de baixo.

**Correção** (`perna_reta_lateral.py`):
- **Malha:** abaixo do punho a malha recua até 0,25 (z 1,15 → 0,45), e a pata fica sob a coluna.
- **Ossos de repouso:** punho no centro da coluna (−4,06); cotovelo na parte de trás da coluna (−3,60, como o olécrano do lobo); base dos dedos recuada junto com a pata.
- **Articulação do ombro:** vai para a frente, dentro do peito (y −4,50).
- **v1 descartada** (`rig10_v1/`, ombro fixo e cotovelo no centro): a cadeia ficou esticada, sem folga para o IK. Erro até 0,36 e escorregão 1,2.

**Resultados:**
- **Clipes (`clipes11`):** IK máximo 0,089 (Uivo), 0,02 nas viradas; escorregão 0.
- **Patas dianteiras em Repouso:** no chão, com a sola a 0,7°.
- **Malha:** simetria 0,0; nenhum buraco novo; dobras > 120° na região caíram de 42 para 22.
- **GLB `export11`:** 56 ossos, 23 ações, 18.138 tris, nenhum osso sem peso.
- **Juba nas patas** (`juba_patas.py`): subiu para 1–10 vértices por quadro de 2.215, máximo 17 na Corrida. A cápsula do osso do braço agora passa dentro do peito, porque o ombro foi para a frente; nos quadros renderizados não se vê interseção. **Conferir no Studio.**

**Evidências:** `review/retas/Lateral_antes_depois_ref.png` e `Prancha_movimento_r9_r10.png`; vídeos em `videos11/`.

## 6l. Perna dianteira como coluna lisa, sem "cotovelo" no meio (04/11/2026, usuário: "ainda tem dobramento, parece um cotovelo") → `rig11/`
**Medido no rig10** (`mascara_perna.py`: máscara ortográfica só da perna; centro e largura por altura, em px de 0,0071 stud):
- **De frente:** a perna afinava até o punho e alargava de novo logo abaixo, com a parte branca mais larga. O centro deslocava 13 px para fora embaixo, e isso desenhava um "cotovelo" a cerca de 40% da altura.
- **De lado:** a parte de baixo inclinava levemente para trás.
- **Descartado:** a medida pela silhueta do render normal, porque a cauda e a barriga escuras atrás das pernas contaminavam o contorno.

**Correção** (`coluna_perna.py`):
- **De frente (x):** os contornos de fora e de dentro viram retas entre logo acima da pata (z 0,65) e logo abaixo do cotovelo (z 2,95). Cada vértice mantém a posição relativa dentro do contorno.
- **De lado (y):** só o centro vira vertical; a largura não muda e a pata acompanha.
- **Ossos e IK:** o punho e a pata foram para o novo centro e o IK foi refeito.
- **Descartados:**
  - v1, retas por mínimos quadrados sobre percentis: afinava o alto da perna e abria um vinco;
  - v2, também em y pela largura: engrossava a perna de lado;
  - uma passada intermediária em que o lado D desfazia o E: simetria 0,143. Corrigido somando os dois lados.

**Resultados:**
- **De frente:** centro da perna entre 306 e 314 px do punho ao cotovelo; largura regular.
- **Malha:** simetria 0,0; nenhum buraco novo.
- **Clipes (`clipes12`):** IK máximo 0,072; escorregão 0.
- **Patas dianteiras em Repouso:** no chão, com a sola a 0,7°.
- **GLB `export12`:** 56 ossos, 23 ações, 18.138 tris, nenhum osso sem peso.
- **Juba nas patas:** 0 a 11 vértices por quadro, de 2.215; é a mesma medida da §6k, com o ombro dentro do peito. Conferir no Studio.

**Evidências:** `review/retas/Frente_antes_depois_ref.png` e `Prancha_movimento_r10_r11.png`; vídeos em `videos12/`.

## 6m. Perna dianteira 100% reta, trecho a trecho (04/11/2026, usuário: "ainda tem pequenas dobras, verifique cada partezinha") → `rig12/`
**Medido no rig11:**
- `medir_coluna.py`, fatias a cada 0,1 e raio em 16 direções em volta do eixo: calombos de raio até 0,19 (p90 0,09), com picos em z 1,6 (punho) e 2,6 (alto do antebraço).
- `contorno_mascara.py`, contorno real da superfície na máscara da perna, linha a linha: centro fugindo da reta até 0,025 de frente e 0,063 de lado.

**Correção** (`perna_cilindro.py`):
- O trecho entre a pata (z 0,62) e o cotovelo (z 2,85) vira uma coluna regular, com eixo vertical único: x = ±0,989, y = −4,113.
- Em cada uma de 16 direções, o raio segue uma reta em z (afinamento suave), com transição macia nas pontas.
- Mechas de pelo ficam fora; UV, textura e pesos não mudam; simétrico.
- O punho (osso) foi para o eixo e o IK foi refeito.

**Resultado:**

| Medida | Antes | Depois |
|---|---|---|
| Calombos de raio, máximo | 0,19 | 0,057 |
| Calombos de raio, p90 | 0,09 | 0,031 |
| Desvio do centro, de frente (máximo / p90) | 0,025 | 0,012 / 0,005 |
| Desvio do centro, de lado (máximo / p90) | 0,063 | 0,033 / 0,018 |

- Bordas dentro de ±0,03 do punho ao alto do antebraço; nas pontas resta só o alargamento natural no encontro com o cotovelo e com a pata.
- **Malha:** simetria 0,0; nenhum buraco novo; dobras > 120° na região caíram para 20.
- **Clipes (`clipes13`):** IK máximo 0,074; escorregão 0. Patas dianteiras em Repouso no chão (sola a 0,7°).
- **GLB `export13`:** 56 ossos, 23 ações, 18.138 tris, nenhum osso sem peso.
- **Juba nas patas:** igual à §6k (0–11 vértices por quadro, de 2.215; conferir no Studio).

**Evidências:** `review/retas/Perna_coluna_antes_depois_ref.png` (frente, lado e máscaras), `Prancha_movimento_r11_r12.png`; vídeos em `videos13/`.

## 6n. Peitoral acima das patas com mais pontas de pelo, separadas e volumosas (05/11/2026) → `rig13/`
**Histórico do pedido:**
- 1º: "está parecendo pelos agrupados". Alisei o peito (`alisar_peito.py`, guardado em `rig13_alisado/`).
- 2º, depois de ver o resultado: "na verdade, quero mais pontas de pelos aparecendo, mais separados e volumosos". O alisamento foi descartado e a base voltou ao `rig12`.

**1. `volume_peito.py` (`realca 0.9`, `infla 0.07`, `cai 0.25`) → `rig13_volume/`:**
- as mechas que saem da superfície suavizada de referência ficam 1,9× mais longas;
- a região cresce 0,07 para fora e as pontas caem um pouco;
- o efeito sozinho é pequeno, porque a malha é leve.

**2. `pontas_peito.py` (`95 0.17`) → `rig13/`:** 190 mechas novas (95 por lado, espelhadas).
- Curvas em dois segmentos (base → meio → ponta), com a ponta caindo.
- Lâmina com frente e verso (6 tris); comprimento 0,24–0,48, meia-largura 0,045–0,075, espaçamento mínimo 0,17.
- Espalhadas na frente do peito entre z 3,15 e 5,6, fora da cabeça e das patas.
- UV = cor do pelo do ponto onde nascem; pesos = os do vértice mais próximo, então acompanham os clipes e o vento do pelo.
- Normal personalizada = normal da pele, para se misturarem ao peito.
- **Versões descartadas:** cones finos (pareciam espinhos) e lâminas planas com a normal da face (pareciam triângulos colados).

**Verificação:**
- **Malha:** 19.278 tris, abaixo do limite de 20 mil; simetria 0,0; 0 vértices sem peso.
- As bordas abertas subiram para 1.914: são as bordas das lâminas das mechas, abertas por natureza.
- **Clipes (`clipes14`):** IK máximo 0,074; escorregão 0.
- **GLB `export14`:** 56 ossos, 23 ações, nenhum osso sem peso.
- **Juba nas patas** (`juba_patas.py`): subiu. Médias de 7 no Trote, 20 na Corrida e 36 no Deitado, máximo 53, de 2.215 vértices: as mechas caem sobre o alto das patas. Nos quadros renderizados não aparece nada atravessando. **Conferir no Studio.**

**Aprovado pelo usuário em 05/11/2026** ("Sim, ficou bom"). Base atual do Lobo: `rig13/` + `clipes14/` + `export14/Lobo_Ancestral.glb`.

**Evidências:** `review/peito/Peito_pontas_antes_depois_ref.png`, `close_pontas_r12_r13.png`, `Prancha_movimento_r12_r13.png`; vídeos em `videos14/`.

## 6o. Sentar e deitar como lobo de verdade (06/11/2026, usuário: "no deitado o lobo deve encostar a cara no chão e realmente deitar; adicione a animação de sentar igual a um lobo") → `rig14/` + `clipes15/` + `export15/`
**Referências usadas:**
- etograma de canídeos da LMU (*sit*: traseiro no chão, patas traseiras dobradas, dianteiras estendidas; *lie*: tronco apoiado no chão, cabeça erguida ou abaixada);
- definição de deitado esternal (peito no chão, traseiras dos lados);
- fotos de lobo deitado (zoológico de Zurique, Photo12).

A busca não trouxe referência anatômica do jarrete no chão ao sentar. A pose segue o lobo real: metatarsos deitados para a frente.

**Mudanças em `anim_lobo.py`** (o original ficou em `review/poses/anim_lobo_antes_poses.py`):
- **`sentado_pose`:**
  - coluna a 44°, traseiro no chão (`assentar_tronco`, com o tronco sem o pelo solto);
  - metatarsos traseiros deitados para a frente (inclinação −86°), joelhos um pouco para fora;
  - dianteiras retas sob o peito; cabeça nivelada; cauda no chão para o lado.
- **`deitado_pose`:**
  - peito no chão e quadril apoiado nas coxas dobradas: `nivelar_tronco` com folga de 0,5 e pitch final −4,3°;
  - antebraços deitados para a frente; traseiras dobradas com os joelhos para fora; cauda enrolada.
  - **Descartadas:** a v2 deixava o quadril alto, como lobo de tocaia; a v4, sem folga, empinava o tronco 18°.
- **`cara_no_chao`:** peito, pescoço e cabeça baixam com compensação na cabeça até o queixo tocar o chão (z 0,05). A v1, que só dobrava o pescoço, trazia o focinho contra o peito.
- **Clipes:**
  - `Deitado` e `Descanso` agora ficam com a cara no chão;
  - `Deitar` ganhou o final em que abaixa a cabeça: 2,5 s, marcadores `Deitado` 1,8 e `CaraNoChao` 2,5;
  - `LevantarDeitado` parte da cara no chão (1,9 s);
  - `Despertar` vai da cara no chão para a cabeça erguida;
  - `Sentar`, `Sentado` e `LevantarSentado` usam a nova pose sentada.

**Verificação:**
- **Clipes (`clipes15`, 23):** IK 0 nos 8 clipes de chão; IK máximo geral 0,074; escorregão 0.
- **GLB `export15`:** 56 ossos, 23 ações, nenhum osso sem peso.
- **Juba nas patas:** Sentado 0; Deitado e Descanso até 18 de 2.215. São as mechas do peito sobre os antebraços deitados, como no pelo real.

**Evidências:** `review/poses/Poses_antes_depois.png`, `Sequencia_sentar_deitar.png`; vídeos em `videos15/` (Sentar, Sentado, Deitar, Deitado, Descanso, LevantarDeitado, Repouso, Andar).

## 6p. Revisão de Sentar e Deitar (06/11/2026, pedido detalhado do usuário) → `rig15/` + `clipes16/` + `export16/` — NÃO aceita (pendências abaixo)
**Inspeção prévia:**
- os MP4 de `videos15` foram decodificados quadro a quadro pelo sequenciador do Blender (`quadros_mp4.py`; folhas em `review/poses/mp4_folha_*.png`);
- **confirmado:** no Sentado a cauda ficava erguida como pluma e a garupa apoiava num ponto; no Deitar o corpo inteiro descia junto (agachamento) e só no fim baixava a cara.

**Referências:**
- etograma de canídeos da LMU (*sit* e *lie*);
- definição de deitado esternal (PMC);
- estudo de *sit-to-stand* em galgos (Frontiers, material suplementar): ao levantar, as traseiras dão a força e as dianteiras estabilizam; o peso fica dividido entre frente e trás;
- clipe de arquivo "Arctic wolf lying down slow motion" (Storyblocks), só a descrição da listagem;
- as páginas do MUN Wolf Ethogram (*Laying down / Less than standing*) recusaram a conexão.
- **Não assisti a vídeos reais:** a ferramenta não reproduz vídeo.

**Mudanças em `anim_lobo.py`** (versão anterior em `review/poses/anim_lobo_v15.py`):
- **`cauda_no_chao`:** a cauda repousa no chão, desce até o pelo encostar, fica atrás ou ao lado e nunca entre as patas. O passo de malha de `cauda_acima`, que a erguia como pluma, fica desligado nos clipes de chão (`CAUDA_MALHA`).
- **`sentado_pose` v2:**
  - dianteiras plantadas, quase verticais sob os ombros (pitch buscado: −34°, ombro−pata 0,03);
  - quadril sob o corpo; patas traseiras recolhidas e apoiadas (`apoiar_membros`);
  - garupa mais baixa: pelve a 0,15 do chão (antes 0,25), esterno 0,36 (antes 0,96).
- **`Sentar`, 1,6 s:** o peso vai para trás em três fases (`meio_sentar` 0,3/0,6/0,85, com o corpo descendo até as dianteiras alcançarem); as traseiras dão o passo com arco.
- **`LevantarSentado`, 1,4 s:** o caminho inverso.
- **`Deitar`, 3,1 s, em fases:**
  1. 0,9 s, `Cotovelos`: as dianteiras dobram e os cotovelos e antebraços vão ao chão, com o quadril alto (pitch 30°);
  2. 1,9 s, `Deitado`: peito, tronco e quadril baixam e as traseiras se recolhem com arco;
  3. 3,1 s, `CaraNoChao`: só então o pescoço e a cabeça descem até o queixo.
- **`Deitado` e `Descanso`:** respiração discreta (o corpo só sobe 0–0,012; a cabeça apoiada não balança).
- **`LevantarDeitado`, 2,3 s:** ergue a cabeça, traz as patas para debaixo do corpo (`Apoios` 1,1 s) e só depois levanta.
- **Clipes que mudaram (8):** Sentar (40 → 49 quadros), Sentado, LevantarSentado (34 → 43), Deitar (76 → 94), Deitado, Descanso, Despertar e LevantarDeitado (58 → 70). Os outros 15 ficaram iguais.

**Medido** (`contatos_chao.py`: ponto mais baixo por região na malha deformada, discos verdes no chão):

| Pose | Pelve | Esterno | Cotovelos | Patas dianteiras | Jarretes | Queixo | Cauda |
|---|---|---|---|---|---|---|---|
| Sentado (v16) | 0,15 | 0,36 | — | 0,00 | −0,24 | — | −0,19 |
| Deitado (v16) | 0,47 | 0,40 | 0,07 | −0,89 | −0,80 | 0,61 | −0,43 |
| Deitado (v15) | 1,05 | 0,46 | 0,09 | −0,90 | −0,80 | 0,80 | 0,15 |

- **Clipes:** IK 0 em Deitar, Deitado, Descanso, Despertar e LevantarDeitado; escorregão 0.
- **GLB `export16`:** 56 ossos, 23 ações, nenhum osso sem peso.

**Pendências que impedem o aceite:**
1. **Patas e jarretes atravessam o chão** no Deitado (−0,89 e −0,80; já era assim no v15). A inclinação que deixa o antebraço deitado põe o punho e o jarrete abaixo do solo. Buscar inclinações (`apoiar_membros` com `pes_deitados`) ou erguer as bolas suspendia o lobo inteiro, com os cotovelos a 0,7–1,0 do chão. Precisa de outra solução: dobra própria do carpo/tarso ou correção de peso nas patas.
2. **IK das dianteiras em `Sentar` e `LevantarSentado`:** 0,41–0,44 no meio da transição (os ombros sobem mais que o alcance entre as chaves), e 0,20 nas traseiras ao levantar.
3. **Cauda no Deitado:** volta a enrolar para cima no fim; a cauda baixa sob o tronco penetra −0,43.
4. **Pelve no Deitado a 0,47:** o quadril fica sobre as coxas dobradas, de propósito (folga 0,3), mas não "encosta".
- **Variantes descartadas** neste dia: v2 a t11 em `review/poses/` e `review/poses/contatos/`.

**Evidências:**
- `review/poses/Transicao_{Sentar,LevantarSentado,Deitar,LevantarDeitado,Despertar}_antes_depois.png` (0/25/50/75/100%, lateral e 3/4);
- `review/poses/Contatos_antes_depois.png`;
- vídeos `videos16/` (8 clipes, normal e lento; câmera fixa lateral, frontal e 3/4).

## 6q. Apoios de Sentar e Deitar (07/11/2026) → `rig16/` + `clipes17/` + `export17/` — quase aceito; pendências abaixo
**Diagnóstico** (`diag_apoios.py` + `contatos_chao.py`, na malha deformada, nos ossos e nos alvos de IK, a 0/25/50/75/100% de cada transição):
1. **Metacarpo e metatarso passavam do plano.** A inclinação fixa (−86/−88) sobre os ~53/64° de repouso deixava o metacarpo a −32° e o metatarso a −24°, com o punho a −0,31 e o jarrete a −0,41 do chão. A malha afundava: metacarpo −0,89, antebraço −0,61, metatarso −0,80, canela −0,58.
2. **O assentar só olhava o tronco.** O corpo descia até os membros afundarem.
3. **Polos do IK parados na altura de pé** (empties não acompanhavam a raiz). Deitado, puxavam cotovelos e joelhos para cima (cotovelo z 1,8, joelho 2,0): os antebraços não deitavam e o tronco ficava suspenso.
4. **A "elevação automática" de `anim_lobo`** (malha fora das patas abaixo do chão sobe a raiz) contava o pelo da cauda e as mechas. Nos clipes de chão erguia o lobo inteiro 0,3–0,4.
5. **A malha da pata é quase toda pesada em Mao/Metatarso.** Erguer a bola até o tufo atrás do carpo/jarrete encostar deixava os dedos 0,5–0,7 no ar.
6. **Alcance ao sentar:** entre as chaves os ombros subiam além do alcance das dianteiras plantadas (IK 0,41–0,44).
7. **Cauda:** a de COTOVELOS herdava a do deitado e pendia; o passo de malha de `cauda_acima` a erguia.

**Correções** (`anim_lobo.py`; a versão anterior está em `review/poses/anim_lobo_v16.py`):
- **`PLANO`** (−53/−64) e **`pe_rente`:** os dedos e almofadas (a malha da pata à frente da bola) encostam a 0,02. Busca-se a inclinação perto do plano que menos enterra o resto. O tufo atrás do carpo/jarrete comprime no máximo 0,08; a bola sobe se for preciso.
- **`assentar_deitado`:** os antebraços (frente) e a pelve/canelas (trás) encostam a 0,03, com o pitch igualando os dois. O esterno, entre os antebraços, pode encostar até −0,05.
- **Polos do IK acompanham a raiz** quando o corpo desce mais de 0,3 (peso 0 de pé). Andar, correr e os outros não mudam.
- **Elevação automática desligada nos clipes de chão.**
- **Alcance quadro a quadro** em Sentar, LevantarSentado, Deitar e LevantarDeitado: o corpo desce até as patas plantadas alcançarem, sem o núcleo nem os antebraços entrarem no chão.
- **Cauda:**
  - `cauda_no_chao` também na fase COTOVELOS e depois de o corpo assentar;
  - o passo de malha volta nas transições com limite de −0,15;
  - nas poses paradas fica desligado.
- **LevantarDeitado:** as dianteiras ficam onde estavam (empurram o peito), as traseiras vêm para debaixo do quadril e depois as dianteiras dão o passo (arco 0,25).

**Resultados** (região: v16 → v17; negativo = abaixo do chão):

| Região | Deitado v16 | Deitado v17 | Sentado v16 | Sentado v17 |
|---|---|---|---|---|
| Patas dianteiras | −0,89 | −0,07 | 0,00 | 0,00 |
| Jarretes | −0,80 | −0,08 | −0,24 | −0,08 |
| Cotovelos (tufo) | 0,07 | −0,12 | — | — |
| Esterno | 0,40 | 0,04 | 0,36 | 0,15 |
| Pelve | 0,47 | 0,04 | 0,15 | −0,02 |
| Queixo | 0,61 | 0,06 | — | — |
| Cauda | −0,43 | −0,12 | −0,19 | −0,18 |

- **IK:** máximo geral 0,074 (Uivo, inalterado); Sentar e LevantarSentado ≤ 0,0001 (antes 0,41–0,44).
- **Escorregão:** 0 em todos os clipes.
- **Regressão nos outros 15:** diferença ≤ 0,003 (Corrida 0,002, Salto 0,003, Rosnar 0,0004; os demais 0).
- **GLB `export17`:** 56 ossos, 23 ações, 19.278 tris, nenhum osso sem peso.

**Pendências (por que "quase aceito"):**
1. **Cotovelos no meio do Deitar** (50%): o tufo do cotovelo chega a −0,33 e o esterno a −0,11.
2. **Cauda no meio do Deitar** (50–75%): sobe enrolada enquanto o corpo baixa e volta a repousar no fim. Pelo da cauda ≤ −0,15 nas transições.
3. **Contatos residuais nas poses finais:** −0,06 a −0,18 (tufos de pelo de cotovelo, jarrete e cauda comprimidos).
4. **Juba/mechas sobre os antebraços deitados:** até 42 de 2.215 vértices por quadro no Deitado e até 314 no meio do Deitar. Igual ao v16 (mechas do peito sobre os antebraços).
5. **Vídeos:** não assisti; revisei pelos quadros.

**Evidências** em `review/apoios/`:
- `Transicao_{Sentar,LevantarSentado,Deitar,LevantarDeitado,Despertar}_v16_v17.png`;
- `Poses_v16_v17_ref.png`;
- contatos em `contatos/` (JSON e renders lateral, 3/4 e de cima);
- vídeos `videos17/` com marcas de contato (`LOBO_MARCAS=1`), chão fixo, normal e lento, 3 vistas.

## 6r. Deitado sem corcunda (07/11/2026, usuário: "quero o lobo totalmente deitado, não com essa corcunda") → `rig17/` + `clipes18/` + `export18/`
**Medido** (`perfil_costas.py`: altura máxima da malha sem pelo solto por fatia de y, da nuca ao quadril):
- **v17:** cernelha a 3,9 e quadril a 1,6; tronco com pitch −18° (o assentar igualava antebraços e pelve). A cara no chão girava o peito em 15°, e a "corcunda" (cernelha acima da reta nuca–quadril) era de 2,74.

**Correções** (`anim_lobo.py`):
- **Cara no chão:** só o pescoço desce (Pescoço1 0,62 / Pescoço2 0,38); o peito não gira.
- **Tronco:** pitch fixo `PITCH_DEITADO` −4° (costas quase niveladas). O quadril repousa sobre as coxas dobradas.
- **Antebraços mais abertos** (`DEIT_ABRE` ±0,45): o peito desce entre eles.
- **Escápulas giradas −25°** (`DEIT_ESCAP`): a cernelha fica mais baixa.
- Os valores podem ser trocados por variáveis de ambiente (`LOBO_ABRE`, `LOBO_ESCAP`, `LOBO_PITCH`, `LOBO_QUEIXO`) para testes.

**Resultados** (Deitado):

| Medida | v17 | v18 |
|---|---|---|
| Corcunda | 2,74 | 1,92 |
| Peito (osso) | 2,60 | 2,20 |
| Escápula | 2,92 | 2,70 |
| Pelve (osso) | 0,81 | 1,32 |

- **Contatos:** esterno −0,04, pelve 0,15, cotovelos 0,14, queixo 0,06, cauda 0,23 (fora do chão), patas e jarretes −0,07/−0,08 (tufo comprimido).
- **Meio do Deitar:** o cotovelo, que chegava a −0,33, agora fica em 0,01–0,28.
- **Clipes:** só Deitar, Deitado, Descanso, Despertar e LevantarDeitado mudaram; os outros 18 ficaram idênticos (diferença 0,000). IK máximo 0,074 (Uivo); escorregão 0.
- **GLB `export18`:** 56 ossos, 23 ações, nenhum osso sem peso.

**Pendências:**
- a corcunda diminuiu, mas não sumiu: a juba volumosa e as escápulas ainda formam o ponto alto atrás da cabeça baixa;
- a cauda ainda se ergue no meio do Deitar (50%);
- juba e mechas sobre os antebraços deitados: ~270 de 2.215 vértices por quadro, contra 40 no v17, porque o peito desceu entre os antebraços abertos. Visualmente as mechas repousam sobre os antebraços; conferir.

**Evidências:** `review/deitado18/Deitado_v17_v18.png`, `Transicao_Deitar_v17_v18.png`, `Transicao_LevantarDeitado_v17_v18.png`; vídeos `videos18/` com marcas de contato.

## 6s. Deitado de verdade: barriga no chão e menos corcunda (07/11/2026, usuário: "quero menos corcunda ao deitar, barriga no chão também") → `clipes19/` + `export19/` (rig17)
**Varredura** (`metr_deitado.py`: barriga, pelve e esterno mais baixos e topo das costas por região):

| Teste | Efeito |
|---|---|
| Abrir mais as coxas | nenhum efeito (o IK domina a coxa) |
| Ceder a coluna (Coluna1/2) | erguia o quadril |
| Pelo da nuca, dorso e juba assentado (−35°) | cernelha 4,40 → 4,04 |
| Pitch −8° | garupa 3,98 → 3,30 e pelve 1,31 → 1,16 |
| Peito cedendo 15° | cernelha → 3,76 |
| Peito 20–30° | erguia o quadril e afundava os cotovelos |

**Adotado:** `DEIT_PELO = −35`, `PITCH_DEITADO = −8`, `DEIT_SAG_P = 15` (com `DEIT_ABRE = 0,45` e `DEIT_ESCAP = −25` da §6r).

**Resultado** (Deitado):
- **Barriga:** −0,04 (encostada); antes também encostava, mas com o quadril alto.
- **Pelve:** 0,02 (antes 0,15).
- **Topo das costas:** cernelha 3,76 / meio 2,78 / garupa 3,30. No v18 era 4,40 / 3,26 / 3,98 com a mesma medida (a §6r usava outra métrica).
- **Queixo:** −0,06 (encostado).
- **Clipes:** só os 5 clipes de deitar mudaram. IK máximo 0,074 (Uivo); escorregão 0.
- **GLB `export19`:** 56 ossos, 23 ações, nenhum osso sem peso.

**Pendências:**
- tufo dos cotovelos −0,24 e cauda −0,31 no Deitado: pelo comprimido no chão;
- ainda há algum volume na cernelha pela juba.

**Evidências:** `review/deitado19/Deitado_v18_v19.png`, `Deitar_v19.png`; vídeos `videos19/` com marcas de contato.

## 6t. Patas relaxadas e cauda deitada (07/11/2026, usuário: "relaxe também as patas dele, e deite a cauda também") → `clipes20/` + `export20/` (rig17)
**Mudanças** (`anim_lobo.py`):
- **`GIRO_PE`:** dianteiras viradas 14° para fora, só quando o corpo está deitado (peso pela altura da raiz; de pé e sentado, 0).
  - **Testado nas traseiras** (22°): as canelas erguiam o corpo (barriga 0,37, pelve 1,53); ficou 0.
- **`DEDOS_SOLTOS` +8°:** dedos das dianteiras levemente flexionados depois de encostarem.
- **Cauda deitada:** `cauda_no_chao(..., comprime=-0,30)` e curva lateral −13°. O pelo volumoso da cauda pode comprimir no chão, em vez de erguer a cauda em rolo. Agora ela repousa estendida atrás e ao lado.

**Resultado** (Deitado):
- barriga −0,04, pelve 0,02, esterno −0,04, queixo −0,06;
- topo da garupa 2,11 (antes 3,30), com a cauda baixa;
- cotovelos −0,11; patas e jarretes −0,07/−0,08 (tufos);
- pelo da cauda −0,40 (comprimido no chão, de propósito).

**Clipes:**
- mudaram Deitar, Deitado, Descanso, Despertar e LevantarDeitado;
- Sentar, Sentado e LevantarSentado variaram até 0,06 (efeito colateral pequeno, não investigado em detalhe);
- os outros 15 ficaram iguais;
- IK máximo 0,074 (Uivo); escorregão 0.

**GLB `export20`:** 56 ossos, 23 ações, nenhum osso sem peso.

**Evidências:** `review/deitado20/Deitado_v19_v20.png` (lateral, 3/4 e de cima); vídeos `videos20/` (Deitar, Deitado, LevantarDeitado) com marcas de contato.

## 6u. Perna da frente reta e descansada no deitado (09/11/2026, usuário: "a perna da frente, ao deitar, fique reta no chão... parece que está forçando as pernas") → `clipes21/` + `export21/` (rig17)
**Medido** (`diag_apoios.py`, v20): cotovelo z 0,20, punho z 0,85 e bola 0,43. O carpo ficava erguido (metacarpo a 24°) e o antebraço subia até o punho, o que lia como perna forçada.

**Correção** (`anim_lobo.py`, `pata_reta`):
- nas dianteiras deitadas, o metacarpo fica no plano do antebraço (`PLANO + INC_RETA`, 4°);
- a bola só sobe o necessário para os dedos encostarem;
- o tufo de pelo sob o carpo pode comprimir até `PELO_CARPO` 0,40;
- as traseiras continuam com `pe_rente`.

**Resultado** (Deitado):
- cotovelo 0,28, punho 0,43, bola 0,35 e metacarpo a 5°: perna reta e rente ao chão;
- corpo igual ao v20 (pelve 0,02, esterno −0,04, queixo −0,06);
- tufo sob o carpo comprimido −0,39, de propósito.

**Clipes:** só os 5 de deitar mudaram (até 0,33); IK máximo 0,074 (Uivo); escorregão 0.

**GLB `export21`:** 56 ossos, 23 ações, nenhum osso sem peso.

**Evidências:** `review/deitado21/Deitado_v20_v21.png`; vídeos `videos21/` (Deitar, Deitado, LevantarDeitado) com marcas de contato.

## 6v. Dormindo como na foto do usuário (09/11/2026) → `clipes22/` + `export22/` (rig17), 24 clipes
**Referência:** `BLENDER/Criaturas/Lobo_Ancestral_Ref/ref/dormir/lobo_dormindo_referencia.webp` (lobo dormindo de lado, cabeça à direita da imagem).

**Pose `dormindo_pose`** (`anim_lobo.py`; a versão anterior está em `review/poses/anim_lobo_v21.py`):
- deitado sobre o quadril esquerdo: raiz rolada 16°, pelve +18°;
- traseira direita (lado de cima) estendida para trás e para fora; traseira esquerda dobrada por baixo;
- dianteira direita esticada rente ao chão (`pata_reta`); dianteira esquerda recolhida;
- cabeça de lado com o queixo no chão: yaw 20° para o lado da câmera, rolagem 14°; orelhas para trás;
- cauda deitada ao longo do corpo.

**Clipes:**
- **`Descanso`** agora é o lobo dormindo nessa pose (5,5 s, respiração lenta);
- **novo `Adormecer`** (2,4 s): da cara no chão para o tombar de lado com as patas se acomodando (marcador `Dormindo`);
- **`Despertar`** (3,0 s): sai do sono de lado, volta à cara no chão, ergue a cabeça e olha em volta;
- `studio_montar_lobo.luau` inclui `Adormecer`;
- os outros 21 clipes ficaram iguais;
- IK máximo 0,074 (Uivo); Descanso, Adormecer e Despertar ≤ 0,0003; escorregão 0.

**GLB `export22`:** 56 ossos, **24** ações, nenhum osso sem peso.

**Contatos no Descanso:**
- queixo 0,05, esterno 0,15, pelve 0,35;
- pata direita esticada −0,40 (tufo do carpo comprimido);
- cauda −0,41 (pelo comprimido).

**Diferenças em relação à foto (limites):**
- **olhos:** o rig não tem pálpebras e os olhos ficam abertos. Fechar exige ossos ou shape keys de pálpebra, ou uma troca de textura;
- **cabeça:** na foto repousa mais de lado (bochecha no chão); aqui está mais voltada para baixo;
- **corpo:** o lobo da foto está mais enrolado e arredondado; o modelo fica mais alongado.

**Evidências:** `review/dormir/Dormindo_vs_foto.png` (foto × mesmo ângulo × de cima); vídeos `videos22/` (Adormecer, Descanso, Despertar) com marcas de contato.

## 6w. Dormindo refeito detalhe por detalhe da foto (09/11/2026) → `clipes23/` + `export23/` (rig17)
**Pedido do usuário:** "a cabeça passa por dentro da perna, a pata está totalmente errada, assim como a postura e a perna... verifique detalhe por detalhe da referência e copie."

**O que a foto mostra:**
- a câmera está na frente-direita do lobo, baixa;
- só o QUADRIL tomba sobre o lado esquerdo; o peito fica apoiado como no Deitado;
- a dianteira direita tem o cotovelo sob o peito e o antebraço deitado à frente; a pata fica ao lado da bochecha;
- a cabeça repousa com o queixo no chão POR DENTRO da pata direita, cara quase nivelada e voltada para a câmera, um pouco tombada, boca fechada;
- a dianteira esquerda não aparece; a traseira direita fica deitada para fora.

**Erros do v22, medidos:**
- tombar o tronco inteiro (16°) erguia o ombro direito a z 3,3 e o cotovelo a 2,2: perna esticada no ar e pata virada;
- a cabeça entrava no antebraço (até 456 vértices);
- o queixo do clipe ficava a −0,28: a busca de giro repetia o `cara_no_chao` sobre o pescoço já dobrado, e ele não conseguia erguer a cabeça.

**Correção** (`anim_lobo.py`, `dormindo_pose` v23; a versão anterior está em `review/poses/anim_lobo_v22b.py`):
- o peito não rola; só a pelve tomba 30° (`LOBO_D_PELVE`) e a Coluna1 0,15 disso;
- a dianteira direita fica na frente e por fora (offset −0,8, −2,7) com `pata_reta`;
- a cabeça é inclinada para cima (−25), girada para a câmera (−14) e tombada 14°, com a mandíbula fechada (−5);
- o giro do pescoço é escolhido pela menor interseção, e cada tentativa parte da mesma cabeça. `cara_no_chao` ganhou `amin` e pode erguer a cabeça;
- a base da cauda é erguida até o pelo comprimir no máximo 0,30 (antes −0,65, com o quadril tombado);
- Adormecer e Despertar: o peito sobe até 0,35 enquanto a pata esquerda recolhe ou sai (antes o braço esquerdo entrava −0,6 no chão); no Despertar a cabeça sobe um pouco nessa troca.

**Medido no clipe assado:**
- Descanso: queixo 0,056; interseção cabeça × perna 0 (E) e 0 (D); o ponto mais baixo é −0,36 a −0,39, que é o tufo do carpo comprimido de propósito, como no v21;
- Adormecer e Despertar: interseção 0 a 4 vértices nos quadros verificados; ponto mais baixo −0,40.

**Clipes:**
- só Descanso, Adormecer e Despertar mudaram; os outros 21 são idênticos ao `clipes22`;
- IK máximo 0,074 (Uivo, igual a antes); escorregão 0.

**GLB `export23`:** 19.278 tris, 56 ossos, 24 ações, nenhum vértice sem peso. "Icosphere" na validação é a forma de osso do importador.

**Limites que continuam:**
- **olhos abertos:** o rig não tem pálpebras. A foto tem olhos fechados;
- **cor e volume:** o lobo da foto é branco e bem mais fofo e arredondado. Aqui fica a pelagem do modelo aprovado.

**Evidências:**
- `review/dormir/Dormindo_v23_vs_foto.png` (foto, v22, v23 no mesmo ângulo, de cima e closes da cabeça);
- vídeos `videos23/` (Adormecer, Descanso, Despertar, normal e lento, com marcas de contato);
- ferramentas: `review/poses/teste_dorm.sh`, `fundo.py`, `ossos_dorm.py`, `close_cab.py`.

**Studio:** não testado.

## 6x. Dormindo: cara encostada no chão (09/11/2026) → `clipes24/` + `export24/` (rig17)
**Pedido do usuário:** "Encoste a cara dele no chão, mas não para entrar no chão, mas sim encostar".
- v23 pousava o queixo a 0,05 (pairava) e a respiração (giro do Peito) fazia a cara subir/descer ±0,04.
- `anim_lobo.py`: alvo do queixo no dormindo = `LOBO_D_QUEIXO` 0,0; `respira(..., "fixa")` no Descanso — o Pescoco1 desfaz o giro do peito (`LOBO_RESP_PESC` 1,8) para a cara ficar parada.
- Medido (`review/poses/queixo.py`, todos os quadros, `review/dormir/log_queixo24.txt`): Descanso queixo entre −0,003 e +0,004 (18–20 vértices a menos de 0,03 do chão); fim do Adormecer/início do Despertar −0,000. Interseção cabeça×perna E 0 / D 1.
- Só Descanso, Adormecer e Despertar mudaram; os outros 21 clipes iguais a `clipes23`. GLB `export24`: 19.278 tris, 56 ossos, 24 ações, 0 vértices sem peso.
- Pendente: no Deitado (DEIT_B, aprovado antes) o pelo sob a mandíbula comprime −0,067 — aparece no início do Adormecer e meio do Despertar; não mexido sem pedido. Studio não testado. Prancha: `review/dormir/Cara_no_chao_v23_v24.png`.

## 6y. Pálpebras: fechar/abrir os olhos (09/11/2026) → `rig18/` + `clipes25/` + `export25/`
**Pedido do usuário:** "e os olhos: façam animação de fechar também".
- **Antes:** os olhos eram só pintura na textura (íris em ±0,50, −6,06, 7,09), sem globo nem pálpebra.
- **Construção (`palpebras.py`, a partir de `rig17` → `rig18/Lobo_Ancestral_Rig.blend`):**
  - uma pálpebra superior por olho, malha de 15×7 vértices;
  - feita na forma fechada, a 0,01 da pele do olho;
  - aberta (repouso), fica escondida sob a sobrancelha, porque o olho é fundo e a sobrancelha fica 0,04–0,10 acima;
  - os cantos ficam sob a pele.
- **Ossos novos:** `PalpebraE`/`PalpebraD`, filhos de Cabeca:
  - pivô 0,25 para dentro do olho;
  - giro em X local de ∓41,3° fecha;
  - peso 1−(u/U)² (canto preso);
  - ângulo gravado em `arm["palpebra_fecha_graus"]`.
- **Pintura própria (cinza da máscara + linha escura dos cílios):** dois retângulos vazios da `T_Lobo_Cor` (96×40 px; normal neutra). Cópias em `rig18/T_Lobo_Cor.png` e `T_Lobo_Normal.png`.
- **Malha:** 19.278 → 19.614 tris; ossos 56 → 58.
- **Animação (`anim_lobo.py` v25):** `"F"` = fração fechada.
  - Adormecer: os olhos pesam (0,55), piscam e fecham até 2,1 s.
  - Descanso: fechados.
  - Despertar: entreabrem (0,55 s), piscam e abrem (1,2 s).
  - Outros 21 clipes: olhos abertos; os ossos do corpo são idênticos aos de `clipes24` (diferença 0,0000).
- **Testes:**
  - `review/poses/medir_palp.py`: aberta, 0/105 vértices fora da pele (máx. −0,004); fechada, folga máx. 0,013.
  - `review/olhos/p6.png`: original × aberto × meio × fechado.
  - `review/olhos/Olhos_v25_tira.png`: sequência nos clipes.
  - Queixo no Descanso: −0,003 a +0,004.
  - GLB `export25`: 58 ossos, 24 ações, 0 vértices sem peso.
- **Limites:**
  - fechada, a borda interna da pálpebra é reta e há leve riscado na pintura;
  - só pálpebra superior;
  - piscar no Repouso/Observar não foi feito;
  - Studio não testado.

## 6z. Dormindo: patas traseiras desviradas (09/11/2026) → `clipes26/` + `export26/` (rig18)
**Pedido do usuário:** "arrume sua pata traseira. Está estranha, totalmente virada".
- **Causa:** no v23–v25 as traseiras ficavam com a pata sob a canela dobrada (paw D (−2,20, 0,03), jarrete em y 1,56 e joelho à frente da pata), virando um bolo amassado sob a coxa, sem a pata aparecer.
- **Correção (`anim_lobo.py`):**
  - deslocamentos de B0 das traseiras no dormindo: `LOBO_D_TD` = (1,0; 1,3) e `LOBO_D_TE` = (0,2; 1,3);
  - as patas vão para a frente, ao lado da garupa (D (−2,00, −0,97), E (1,20, −0,97));
  - apoiadas pela sola, dedos para a frente e visíveis, como a traseira de cima da foto.
- **Testado em 3 posições por lado** (`review/dormir/td_teste.png`, `te_teste.png`).
- **Medido:**
  - IK 0,0002;
  - queixo no Descanso de 0,003 a 0,005;
  - ponto mais baixo: o tufo da pata dianteira D (−0,39, de propósito);
  - a base da cauda comprime −0,28.
- **Cabeça:** a busca de giro do pescoço foi para 30°. A cabeça encosta na lateral do antebraço D (14 vértices na cápsula de 0,40), sem atravessá-lo no close.
- **Mudaram só Adormecer, Descanso e Despertar.**
- **GLB `export26`:** 58 ossos, 24 ações.
- **Prancha:** `review/dormir/Traseiras_v25_v26.png`.
- Studio não testado.

**APROVADO pelo usuário em 09/11/2026 ("Aprovado"):** pose de dormir v26 (`rig18` + `clipes26/` + `export26/` + `videos26/`) — dormindo copiado da foto (v23), cara encostada no chão (v24), pálpebras fechando/abrindo (v25) e patas traseiras apoiadas (v26). Base para próximas mudanças: `rig18` + `anim_lobo.py` atual. Studio ainda não testado.

## 6aa. Montaria M1: sela leve (10/11/2026, APROVADA pelo usuário em 10/11: "Aprovado, siga") → `montaria/`
**Pedido do usuário:** "Pode fazer a montaria, a sela de acordo com o visual de seus ingredientes, a animação de subida e de descida."
- **Oficial (§1):** montável desde o Adulto com **sela leve**. A referência mostra a pelagem com musgo e folhas; o lobo tem marcas verdes.
- **M0 (`montaria/m0_medir_dorso.py` → `m0_dorso.json`):**
  - o dorso é estreito (meia largura ~0,8–1,1) e o meio dele fica em z 5,8 (y −1,5…0,5);
  - a juba sobe até 8,2 na frente;
  - a barriga fica em ~3,3–3,8.
- **M1 (`montaria/m1_sela_lobo.py` → `LA_M1_sela.blend`, `m1_sela.json`):**
  - mesmo método da sela do Urso (campo de alturas por raios + pesos copiados da pele, sem os ossos Pelo*/Juba*/Palpebra);
  - nada do lobo foi alterado.
  - **Peças e materiais:**
    - manta fina de Pele de Cervo;
    - aba, assento baixo e cilha fina (y −2,05, atrás das patas da frente) de Couro de Javali;
    - folhas de couro verde-musgo na borda da manta (as folhas da pelagem);
    - debrum e costuras de Tendão de Cervo;
    - pegada de galho fino de Madeira Ancestral, enrolada em tendão, com folhinhas e gota de Resina Viva verde (as marcas do lobo);
    - fivelas pequenas de Ferro com Resina Viva;
    - estribos leves: cordão de tendão e degrau de Madeira Ancestral.
  - **Números:**
    - assento z 6,07, quadril do cavaleiro z 6,57 (y −0,62);
    - tornozelo do R15 em (±1,10, −0,92, 5,09), perna 1,62;
    - 8.440 tris; estribos rígidos no osso do assento (Coluna2 0,55 / Coluna1 0,43).
  - **Renders:** `montaria/review_m1/Sela_Lobo_M1.png`, com e sem o manequim R15 aproximado.
- **Próximo (aguardando aprovação da sela):**
  - M2: subida e descida pelos dois lados (o lobo deita, como o Urso, pois o dorso de 5,8 é mais alto que o R15);
  - M3: textura e GLB da sela.
- Studio não testado.

## 6ab. Montaria M2 r3: subida e descida COM PULO, segurando na sela, pelos dois lados (10/11/2026, APROVADA pelo usuário em 10/11) → `montaria/`
- **Pedidos do usuário (10/11):**
  - "em vez do lobo subir assim e descer assim, faça com que o jogador pule" → o lobo não deita mais (r2);
  - "quero que ele encene que está segurando no lobo para pular, porque agora está irreal" → o cavaleiro se agarra na sela (r3).
  - A versão com o lobo deitando ficou em `montaria/v1_deitado/` (scripts e QA), com os vídeos em `montaria/review_m2/`.
- **Sela (r2, mantida):** estribos a 0,62 fora do flanco; tornozelo em (±1,36, −0,92, 5,23). Sentado, a canela e o pé ficam de −0,13 a −0,27 no pelo.
- **Clipes do lobo (`montaria/clipes_montaria.py`, carregado com `LOBO_MONTARIA=1`):**
  - `Montar_E/D` (3,0 s): em pé, olha para o cavaleiro; enquanto ele se agarra e se puxa, rola 2,5° para o lado dele e cede 0,05; cede 0,08 quando ele assenta. Marcadores Agarra 1,32 / Pulo 1,6 / Sentado 2,4.
  - `Desmontar_E/D` (3,2 s): rola 2,5° para o lado e cede 0,05 com ele pendurado; volta quando ele solta. Marcadores Pendurado 1,25 / Solta 1,55 / NoChao 1,85.
  - QA dos clipes: erro de IK 0 e deslize de pata 0.
  - Gravado em `rig18/Lobo_Ancestral_Anim_Montaria.blend` e `montaria/clipes_m2/`. Os clipes aprovados não mudam.
- **Cavaleiro de teste (`montaria/m2_demo_montaria.py`, manequim R15 aproximado):**
  - **Subida:** chega ao lado; agarra a face de fora da aba com as duas mãos (agarres medidos por raio, z 5,47); flexiona os joelhos segurando, com o tronco para trás; pula se puxando, o pé da frente entra no estribo; a perna de fora passa pela garupa e cai no outro estribo; senta.
  - **Descida:** mãos na aba; a perna de fora passa pela garupa e ele vira para o lobo; desce pendurado no flanco segurando a aba; solta, cai agachado e se afasta dois passos.
  - QA em `montaria/m2_qa.json`:
    - tronco e cabeça sempre fora do lobo e da sela;
    - mãos e antebraços afundam de 0,25 a 0,39 nos tufos de pelo em volta da aba nos quadros do puxão e da soltura;
    - pernas até −0,33 no pelo por poucos quadros (sentado −0,27);
    - sola ≥ 0,03; velocidade máxima do quadril 19 (subida) e 14 studs/s (descida).
- **Vídeos:** `montaria/review_m2_pulo/` (Montar/Desmontar × E/D, 3/4, normal e lento). Folhas: `folha_pulo_E.png`, `folha_pulo_D.png`.
- **Pendente:**
  - M3: textura e GLB da sela;
  - cavaleiro nos clipes de locomoção;
  - Studio (no jogo: animação do jogador + solda no servidor; não testado).

## 6ac. Montaria M3: textura de jogo e GLB da sela (10/11/2026, APROVADA pelo usuário em 10/11) → `montaria/export_sela/`
- **Script:** `montaria/m3_textura_glb.py`, adaptado do M3 aprovado do Urso (mesmo método). O `.blend` de entrada não é salvo; nada do lobo muda.
  - Correção: o `LA_M1_sela.blend` veio com o bake "selecionado para ativo" ligado ("No valid selected objects"); o script agora desliga.
- **Resultado:**
  - UV única de jogo (projeção inteligente, densidade igual, margem 0,003);
  - bake Cycles 1024×1024 dos 7 materiais: `T_LoboAncestral_Sela_Cor.png`, `_Normal.png` e `_MetalRug.png` (glTF: G = rugosidade, B = metal), além de `_Rug.png` e `_Metal.png` separados;
  - material único `M_LoboAncestral_Sela_Jogo`;
  - `Lobo_Ancestral_Sela.glb` (2,2 MB): só a sela + a armadura do lobo, sem animação, texturas embutidas;
  - `Lobo_Ancestral_Sela_Jogo.blend` para conferência.
- **Validação por reimportação (`montaria/m3_validar_glb.py` → `export_sela/validacao_glb.json`):**
  - 8.440 triângulos, 1 material, 3 imagens de 1024;
  - armadura com os 58 ossos do rig18, com os mesmos nomes do export26;
  - no máximo 4 influências por vértice, 0 vértices sem peso;
  - sela de z 3,08 a 6,56.
  - A `Icosphere` de 80 triângulos é a forma de exibição dos ossos; já aparece no export26.
- **Comparação procedural × jogo:** `montaria/review_m3/comparar_m1_m3.png` (e as vistas em `review_m3/`). A cor, o couro, as folhas, a resina e o ferro ficam iguais; as costuras ficam um pouco mais suaves no 1024.
- **Pendente:**
  - Studio: importar o GLB e prender a sela no lobo (não testado);
  - cavaleiro nos clipes de locomoção.

## 6ad. Montaria M4: cavaleiro de teste sentado nos clipes aprovados (10/11/2026, APROVADO pelo usuário em 10/11) → `montaria/m4_montado.py`
- **Método** (adaptado do teste aprovado do Urso):
  - o manequim R15 aproximado fica sentado, preso ao osso `Coluna2` no ponto do assento;
  - roda nos 15 clipes aprovados do v26 (`rig18/Lobo_Ancestral_Anim.blend`);
  - mede as folgas contra o lobo e a sela e o balanço do assento.
  - Só leitura. O cavaleiro não tem animação própria nem balanço secundário.
- **Resultados (`montaria/m4_montado.json`):**
  - tronco, braços e cabeça a ≥ 0,73 do lobo em todos os clipes;
  - pernas no máximo −0,28 no pelo do flanco (igual ao sentado parado, −0,27);
  - na sela, até −0,03, e −0,15 da canela D no `Impacto`.
  - Balanço do quadril em z: Andar 0,13, Trote 0,20, Corrida 0,14, Partida 0,31, Freada 0,36; ataques 0,21–0,27.
  - Inclinação para a frente: no máximo ±2° na Corrida, −4°/+5° na Partida e na Freada, ±6° nos ataques.
  - O `Salto` sobe 2,5 no próprio clipe; a inclinação vai de −7° a +10° e a aceleração vertical é alta no pouso.
- **Vídeo:** `montaria/review_m4/Montado_lobo.mp4` (Repouso, Andar, Trote, Corrida, VirarE, Salto, Mordida). Folha: `review_m4/folha_montado.png`.
- **Pendente:**
  - Studio: solda do cavaleiro na sela e animação sentada do R15 (não testado);
  - balanço secundário do cavaleiro (opcional).

## 6ae. Kit Natureza — etapa 1: clipes das ativas no Blender (10/11/2026, aguardando avaliação) → `habilidades/`
- **Pedido:** `DOCS/pedidos/2026-11-10-lobo-ancestral-habilidades-passivas.md` (autoriza criar/testar o kit só no place isolado do lobo).
- **Studio (10/11):** o Studio conectado estava **sem place aberto** ("Place is not open") e não encontrei o `.rbxl` do Baseplate isolado de 05/11. A reserva em `DOCS/estado/studio-em-uso.md` (chat Lobo, 05/11) **não pôde ser confirmada**; nada foi feito no Studio. Precisa que o usuário abra o place isolado do lobo (ou um Baseplate novo).
- **Clipes novos (`habilidades/clipes_kit.py`, carregado com `LOBO_KIT=1`; os 24 clipes aprovados não mudam):**
  - `Hab_SaltoPredatorio` (1,35 s): mira agachado (orelhas para trás) → impulso → bote no ar (dianteiras esticadas para a frente, traseiras para trás, boca aberta) → aterrissa fechando a mandíbula → amortece. Marcadores Mira 0,30 / Impulso 0,36 / Decolagem 0,42 / Golpe = Aterrissagem 0,86 / Recuperado 1,35. Diferente do `Salto` de vida (que é um pulo sem mira nem mordida).
  - `Hab_UivoAncestral` (2,6 s): firma as patas, estufa o peito, uiva (mais curto que o `Uivo` de 4 s) e sacode a juba; termina com a cauda alta. Marcadores UivoInicio 0,55 / BuffInicio 0,6 / UivoFim 1,85 / Fim 2,6.
  - `Hab_Investida` (1,2 s): carga baixa → arranque em galope baixo (passada do `Corrida` aprovado, cabeça estendida, boca abrindo) → mordida avançando o pescoço → freia. Marcadores Carga 0 / Arranque 0,22 / Contato 0,86 / Freia 0,96 / Fim 1,2.
  - Todos **no lugar**: o arco do salto e o avanço da investida vêm do jogo (servidor/física), não do clipe.
  - QA: erro de IK ≤ 0,022, malha fora das patas ≥ 0,009 do chão, dedos ≥ 0,10. Gravado em `rig18/Lobo_Ancestral_Anim_Kit.blend` e `habilidades/clipes_kit/` (JSON + manifesto).
- **Vídeos:** `habilidades/videos_kit/` (normal e lento de cada clipe) e `folha_kit_lado.png`.
- **Parâmetros de protótipo — [PROPOSTA], não aprovados, um único módulo de configuração no place isolado:**
  | Item | Proposta |
  |---|---|
  | Noite (Caçador Noturno) | `Lighting.ClockTime` ≥ 18,5 ou < 5,5, lido **só no servidor**, a cada 1 s, com histerese de 0,1 h |
  | Caçador Noturno | +12% velocidade de perseguição, janela de esquiva +10%, +12% dano de mordida/garra |
  | Uivo Ancestral | 6 s; +15% velocidade, janela de esquiva +20%; recarga 18 s; energia 15 |
  | Acúmulo | bônus somados numa tabela única de modificadores (aditivos) com teto de velocidade +25%; a vantagem ambiental da Floresta (10–15%) continua fora dessa tabela e **não** é reaplicada; montado, os bônus de mobilidade valem para o lobo (montaria), não para o cavaleiro |
  | Salto Predatório | alcance 8–40 studs, linha de visão, voo 0,44 s, acerto num raio de 6 na aterrissagem; dano 1,4× força-base; recarga 8 s; energia 20 |
  | Investida | 30 studs em 0,56 s, largura 5, para em obstáculo; dano 1,2×; 1 acerto por alvo; recarga 6 s; energia 15 |
  | Instinto de Caça | pegadas/odor visíveis só para o dono: rastro de até 8 s de inimigos a ≤ 60 studs e com linha de visão; pistas de ninho a ≤ 150 studs como direção aproximada (±30°), a cada 30 s; sem marcador de posição |
- **Pendente (etapa 2, depois da aprovação dos clipes e com o place isolado aberto):** servidor do kit (passivas + ativas), VFX discretos de folhas/vento, sons, testes em Play/PC e custo com várias instâncias. Celular real não testado.

## 6af. Pernas e patas na marcha — v27 (10/11/2026, aguardando avaliação) → `review/pernas/`, `clipes27/`, `export27/`
- **Pedido:** corrigir pernas e patas tortas em Andar, Trote e Corrida, sem Studio, preservando repouso, pelagem, dormir e sela.
- **Base conferida:** Andar/Trote/Corrida de `clipes14` (vídeos de `videos14/`) = `clipes26` (diferença ≤ 0,002; só entraram as pálpebras). A versão anterior fica preservada: `clipes26/`, `export26/`, `rig18/Lobo_Ancestral_Anim.blend` (regenerado idêntico, diferença 0) e o script `review/pernas/anim_lobo_v26.py`.
- **Inspeção:** ciclo inteiro, quadro a quadro, em frente/lado/trás/3/4 + 2 closes baixos com chão (`review/pernas/render_ciclo.py` → `antes/`, `depois/`, folhas `folha_<clipe>_<vista>.png`); medição por perna e quadro nos ossos e na malha (`analisar_pernas.py` → `analise_antes.json`, `analise_depois.json`): plano da perna, dobra, torção de cada osso, sola, z da pata, cruzamento E×D. Perfil de pesos do punho/jarrete: `medir_pesos_punho.py`.
- **Defeitos encontrados (v26), por clipe e perna** (balanço = quadros com a almofada acima do chão):
  | Clipe | Perna | Quadros | Defeito | Causa |
  |---|---|---|---|---|
  | Andar | DE / DD | balanço q1–9 e q33–36 / q15–27 | pata dobra fora do plano da perna (ponta desvia para o lado); punho dobra demais com os dedos enrolados → "toco" escuro e prega na malha | alvo do IK: a pata girava em volta do X do MUNDO, mas a perna é inclinada (plano 12,7–16,9°); dobra + dedos somados; malha LOW com poucos vértices no carpo |
  | Trote | DE / DD | balanço q11–20 / q1–10 | idem, mais forte (pata vira "toco" em q4 e q15) | idem |
  | Corrida | DE / DD | balanço q1–6, q12–14 / q1–8, q13–14 | idem; de frente as patas dobradas giram para dentro (q3) | idem |
  | todos | dianteiras | apoio inteiro | calcanhar sobe desde o pouso (sola +2° → −9°): a pata rola para a ponta sustentando o peso; pelo da pata −0,03 a −0,04 dentro do chão | perfil de inclinação do apoio (linear do pouso à saída) |
  | Andar / Trote / Corrida | TE / TD | balanço (Andar q24–36 / q6–18; Trote q1–10 / q11–20; Corrida q6–14 / q7–14) | pata chega de ponta, dedos para baixo, até o pouso | a dobra do balanço só zerava no último quadro |
  | Corrida | TE / TD | q10–12 (recolhimento) | coxa torce 4,5–5,1° (pendência antiga da ficha) | IK com polo fixo; não piorou nem foi resolvido (ver tentativas) |
  - **Descartado como causa:** torção dos ossos pelo IK (< 5°), pesos (transição Antebraço→Mão e Canela→Metatarso já larga, ~1,4 stud) e o pivô dos ossos (joelho/cotovelo dobram para o lado certo em todos os quadros).
- **Correção (só no código da marcha em `anim_lobo.py`; repouso, pelagem, rig, pesos e os outros 19 clipes idênticos):**
  - dianteiras dobram em volta da **normal do plano da própria perna** (`EIXO_PATA`) e com 80% da dobra anterior (`LOBO_FLEX_DIAN`);
  - dedos menos enrolados no balanço (`LOBO_DEDO_BAL` 0,55);
  - a dobra das dianteiras termina antes do pouso; as traseiras mantêm o perfil do v26 e aplainam no fim do balanço (`LOBO_TRAS_APLAINA` 0,6);
  - pouso plano (`LOBO_INCL_POUSO` 1°, antes 4–6°) e calcanhar só sobe nos últimos 45% do apoio;
  - polo do IK das dianteiras 4 studs mais longe na marcha (`LOBO_POLO_LONGE`).
  - **Tentativas descartadas (medidas):** eixo da perna também nas traseiras (coxa da Corrida 4,5° → 9,8°, plano 12 → 21°); dobra traseira 0,75 e perfil rápido (coxa 9–10°); polo traseiro mais longe ou mais perto do centro (coxa 9–13°).
- **Resultados v26 → v27 (`analise_*.json`, manifesto):**
  - plano das dianteiras: Andar 12,7–16,9° → 11,5–14,8°; Trote 14,3–15,5° → 12,1–13,4°; Corrida 14,2–16,3° → 12,0–13,3°;
  - pata no chão: −0,03/−0,04 → −0,01 (as 4 patas, os 3 clipes); malha fora das patas 0,17–0,19 → 0,24;
  - distância mínima entre as pernas E×D: dianteiras 0,07–0,10 → 0,08–0,11; traseiras na Corrida 0,016 → 0,023;
  - traseiras: plano e torção da coxa iguais ao v26 (Corrida 12,2° / 4,5–5,1°);
  - erro de IK ≤ 0,0002, deslize 0, dedos ≥ 0,10; loops fechados (a marcha é periódica); Partida/Freada usam a mesma passada (IK 0, malha 0,24).
- **Evidências:** `review/pernas/AntesDepois_{Andar,Trote,Corrida}_{normal,lento}.mp4` (lado, close lateral, frente baixa e trás, antes × depois); folhas `antes/` e `depois/folha_*`; `zoom_antes_depois.png`; `closes_patas_<clipe>.png` (cada pata no apoio e no balanço, fora e frente, v26 × v27).
- **Compatibilidade:** `export27/Lobo_Ancestral.glb` reimportado (`validacao_glb.json`): 19.614 tris, 58 ossos, 24 ações, pose de ossos-chave idêntica à referência (0,0), 0 vértices sem peso nem > 4 influências. Dormir/sela/ataques não mudam (JSON idênticos). Cavaleiro montado (`m4_montado.py` com o v27): igual ao v26, exceto a Freada (perna do cavaleiro −0,10 na sela num quadro; antes −0,02). `m4_montado.py` agora troca as ações do arquivo indicado (antes reaproveitava as antigas do `.blend` da sela).
- **Pendente:** a prega no carpo ainda aparece de leve na dobra máxima (malha LOW); coxa traseira da Corrida segue com 4,5–5,1° de torção; `Hab_Investida` usa o galope e precisa ser regenerada se o v27 for aprovado; Studio não testado. O v27 só substitui a base (`Lobo_Ancestral_Anim.blend`, `clipes26`/`export26`) depois da aprovação.

## 6ag. Pendências da v27: prega do carpo e torção da coxa — v28 (10/11/2026, APROVADA VISUALMENTE no Blender pelo usuário em 10/11; Roblox não testado) → `review/pernas2/`, `clipes28/`, `export28/`
- **Preservado para comparação:** v26 (`Lobo_Ancestral_Anim.blend`, `clipes26/`, `export26/`, `Lobo_Ancestral_Rig.blend`) e v27 (`Lobo_Ancestral_Anim_v27.blend`, `clipes27/`, `export27/`, script `review/pernas2/anim_lobo_v27.py`). A v28 tem rig próprio: `rig18/Lobo_Ancestral_Rig_v28.blend` → `Lobo_Ancestral_Anim_v28.blend`.
- **Diagnóstico (antes de editar; `diag_carpo_coxa.py` → `diag_v26/v27.json`; renders `diag_render.py` com malha, pesos, ossos, eixo de dobra e dedos → `diag_<clipe>_<perna>_<q>.png`):**
  - **Carpo:** flexão máxima na Corrida q1 (62° na v27; 97° na v26). Sem auto-interseção pata×antebraço (0) e sem pelo na região. O lado **palmar** comprime (arestas a 55% na Corrida, 67% no Trote) e forma um vinco em V; tufos de pelo do antebraço entram no vinco. A transição de pesos já era larga (~1,4 stud) — suavizá-la (`suavizar_carpo.py`, 3 intensidades) só levou 0,55 → 0,56–0,60 e piorou o Deitado. **Causa: geometria esparsa (3–7 vértices por faixa no carpo) + skin linear na rotação do carpo**, não os pesos nem o pelo.
  - **Coxa (Corrida q10–12, recolhimento):** o jarrete abre +0,12 em x (abertura lateral `abre` do balanço do galope) e o joelho entra até x 0,82 (repouso 0,95). Com o polo do joelho parado, o plano da perna gira e a coxa torce 4,5–5,1°. **Causa: alvo do IK com desvio lateral contra um polo fixo** (diferente das tentativas da v27, que moviam o polo de forma fixa).
- **Correção (menor mudança):**
  - **coxa:** o polo do joelho acompanha o desvio lateral do alvo (`LOBO_POLO_SEGUE` 1, só na marcha). Testado também sem a abertura lateral (`LOBO_ABRE_TRAS` 0): mesma torção, menos folga entre as traseiras.
  - **carpo:** osso auxiliar `CarpoE/CarpoD` (filho do antebraço, na junta) que recebe metade do giro da pata (`osso_carpo.py`, fração de peso 0,8, raio 0,9; `anim_lobo.carpo_meio`), mais 2 anéis de arestas só nos carpos (`aneis_carpo.py`, UV e pesos interpolados; +102 vértices, 19.614 → 19.818 tris; 4 influências no máximo). Só o osso ou só os pesos não mudavam o visual; os dois juntos arredondam a dobra (`zoom_carpo_4v.png`).
  - **clipes que não são da marcha:** os ossos antigos ficam **idênticos** aos da v27 (`mesclar_v28.py`; sem isso o assentamento por malha mudava até 0,16 no dormir); só ganham as chaves do osso do carpo. Andar/Trote/Partida/Freada também ficam iguais nos ossos antigos; só a Corrida muda (polo).
- **Resultados v26 → v27 → v28 (`diag_v28.json`, `analise_v28.json`, manifesto):**
  | Medida | v26 | v27 | v28 |
  |---|---|---|---|
  | Carpo, compressão palmar mín. (Corrida / Trote / Andar) | 0,19 / 0,44 / 0,68 | 0,55 / 0,67 / 0,79 | 0,67 / 0,79 / 0,85 |
  | Carpo, lado dorsal mín. (Corrida / Trote) | 0,38 / 0,62 | 0,66 / 0,75 | 0,65 / 0,70 |
  | Coxa, torção máx. na Corrida | 5,1° | 5,1° | 3,1° |
  | Joelho x mín. no recolhimento (repouso 0,95) | 0,82 | 0,82 | 0,87 |
  - pata no chão ≥ −0,012; sola plana no pouso e calcanhar só no fim do apoio (como a v27); deslize 0; IK ≤ 0,0002; dedos ≥ 0,10; malha ≥ 0,24; distância mín. entre pernas E×D: dianteiras 0,06–0,07, traseiras 0,030–0,034.
  - Dormir/Deitado/Sentado: ossos idênticos; visual igual nas 3 vistas (`diag_dormir_v27_v28.png`). No Adormecer, a pata dobrada sob o peito tem mais compressão dorsal (0,28 → 0,15), em região escondida.
- **Evidências:** `v26_v27_v28_{Andar,Trote,Corrida}_{normal,lento}.mp4` (lado, close lateral, frente baixa e trás; mesma câmera e luz); `closes_v26_v27_v28_<clipe>.png` (cada pata no apoio, no balanço e no pouso); `zoom_carpo_3v.png`, `zoom_carpo_4v.png`, `diag_*.png`.
- **GLB (`export28/validacao_glb.json`):** 19.818 tris, 60 ossos (58 + CarpoE/D), 24 ações, 2 texturas 1024, pose de referência idêntica (0,0), 0 vértices sem peso nem > 4 influências. Cavaleiro montado igual à v27.
- **Limitações e pendências:**
  - ainda há um vinco suave no carpo na flexão máxima da Corrida e tufos de pelo do antebraço entram nele; reduzir mais exigiria menos flexão (`LOBO_FLEX_DIAN`) ou mais geometria no carpo da LOW;
  - a coxa ainda torce 3,1° na Corrida (o jarrete continua abrindo 0,12 para não cruzar as pernas);
  - o esqueleto passa a ter 60 ossos: o GLB da sela (M3, 58 ossos) precisa ser reexportado com o rig v28 antes do Studio, se a v28 for aprovada;
  - `Hab_Investida` só deve ser regerada depois da aprovação; Studio não testado.

## 6ah. Sela e kit compatibilizados com a marcha v28 (10/11/2026, sela v28 e nova Investida APROVADAS pelo usuário em 10/11; Roblox não testado)
- **Status da base:** a marcha **v28** (§6ag) foi **aprovada visualmente no Blender** pelo usuário em 10/11. **Nada foi testado no Roblox.** v26 e v27 continuam preservadas.
- **Sela (`montaria/m3b_sela_v28.py` → `montaria/export_sela_v28/`):** a MESMA sela de jogo da M3 (malha, material único, UV, 3 texturas 1024, escala, posição e pesos) reexportada com a armadura de 60 ossos (58 + CarpoE/CarpoD, sem peso na sela). Bind pose: os 58 ossos antigos têm repouso idêntico ao do rig v28 (diferença 0,0); os 2 novos, 1,6e-7.
  - **Reimportação (`m3b_validar.py` → `export_sela_v28/validacao_sela_v28.json`):** sela v28 e lobo v28 com 60 ossos, mesmos nomes, mesmos pais, repouso mundial igual (0,0); sela v28 = sela M3 em vértices (8.113), triângulos (8.440), posição (0,0), UV (0,0), material, imagens e pesos (idênticos); máx. 4 influências, 0 sem peso, nenhum peso em CarpoE/D.
  - **Sela sobre o lobo (`m3b_sela_marcha.py` → `montaria/review_m3b/`, prancha `prancha_sela_v26_v28.png`):** v26 + sela M3 × v28 + sela v28 em Andar, Trote, Corrida, Partida, Freada, Salto e Impacto: profundidade máxima do pelo sob a sela −0,11 a −0,28 e fração da face de baixo dentro do pelo 0,6–3%, iguais nas duas versões (é o pelo comprimido sob a sela, já presente na M3 aprovada).
  - O GLB da sela M3 de 58 ossos (`export_sela/`) continua guardado para comparação.
- **Hab_Investida (`habilidades/clipes_kit.py`; anterior em `clipes_kit_v27.py`):** regerada sobre a Corrida v28 no rig v28 (`LOBO_KIT=1` → `rig18/Lobo_Ancestral_Anim_Kit_v28.blend`, `habilidades/clipes_kit28/`).
  - Mesmas fases e marcadores (Carga 0 / Arranque 0,22 / Contato 0,86 / Freia 0,96 / Fim 1,2), 37 quadros, no lugar.
  - **Patinagem corrigida** (já existia na versão anterior): curva de velocidade do avanço que o jogo aplica (`clipes_kit28/Investida_velocidade.json`: parado → rampa no Arranque → galope 21,4 studs/s → desacelera até o Freia → parado); as patas apoiadas ficam plantadas e recuam nessa curva; na carga só o corpo abaixa; recuo além de 0,75 vira um passo curto; na freada, passos alternados até o repouso (antes deslizavam 0,55). Também a regra da marcha (eixo da perna e polos) vale em todas as fases (antes trocava nas misturas).
  - **QA (`habilidades/qa_investida.py`, `diag_carpo_coxa.py`):** deslize das patas apoiadas 33,9 → 0,0 no avanço e 3,4 → 0,6 parado (o 0,6 é o quadro em que a curva zera); carpo: dobra máx. 99,5° → 66,9°, compressão palmar 0,18 → 0,64 (sem "toco"); coxa: torção 6,0° → 3,5°, joelho x mín. 0,79 → 0,85; IK 0,0003; malha ≥ 0,028 do chão; dedos ≥ 0,10.
  - Evidências: `habilidades/Investida_v27_v28_{normal,lento}.mp4` (lado, close lateral, frente baixa e trás), `closes_investida_v27_v28.png` (4 patas no apoio, no balanço e na freada, fora e frente), folhas `folha_investida_v28_{lado,close_lado,tras,frente}.png`, `comparar_referencia_v28.png`.
- **Hab_SaltoPredatorio e Hab_UivoAncestral:** só reexportados no esqueleto v28 — ossos antigos idênticos aos anteriores (diferença 0,0), mesma duração, mesmos marcadores, IK e malha; ganharam apenas as chaves do osso do carpo. Os 3 clipes do kit continuam **aguardando avaliação** (§6ae) e os números de combate seguem **[PROPOSTA]**.
- **Limitações:** a sela do jogo continua com o pelo comprimido sob ela (como na M3); a Investida ainda dobra a coxa 3,5° no galope; a curva de avanço é sincronismo de animação, não parâmetro de combate aprovado; Studio não usado.

## 6ai. Marcha v29: Andar e Corrida inspirados no Lobo Ártico (10/11/2026, aguardando avaliação; NÃO substitui a base v28) → `marcha/marcha_v29.py`, `review/marcha_v29/`, `clipes29/`, `export29/`
- **Pedido:** dar ao Andar e à Corrida a naturalidade do Lobo Ártico v29 (só esses dois clipes). Fontes só lidas: `Lobo_Artico_Ref/anim_v29/CR_LoboArtico_Anim.blend`, `clipes_v12.py`, `clipes_v21.py`, `marcha_v21.py` e a ficha do Ártico §8.26–8.31.
- **Lado a lado antes de alterar (`render_comparar.py`, mesmas câmeras relativas, luz e chão; 2 ciclos):** v28 × Ártico em lado, frente, trás, 3/4 e 2 closes; medição comparável normalizada pela perna e pela cernelha (`medir_marcha.py` → `marcha_v28.json`, `marcha_artico.json`).
- **Diferenças encontradas (v28 → Ártico):**
  | | Andar | Corrida |
  |---|---|---|
  | Sequência | igual (TE, DE, TD, DD lateral) | v28 **transverso** (TE, TD, DE, DD) → Ártico **rotatório** (TE, TD, DD, DE) |
  | Apoio (fração) | 0,72 → 0,61–0,69 | 0,36–0,43 → 0,29–0,36 |
  | Altura do balanço / perna | 0,07 → 0,10–0,135 | 0,16–0,17 → 0,18–0,22 |
  | Varredura do apoio / perna | 0,40–0,42 → 0,45–0,50 | 0,56–0,60 → 0,46–0,65 |
  | Dobra do carpo no balanço | 1–2° (pata rígida) → 67–77° | 37–38° → 103–111° |
  | Cotovelo | 34° → 45–48° | 75° → 97–100° |
  | Balanço da pata | perfil suave → **min-jerk**, altura que só zera no toque | idem |
  | Rolamento da sola | desde 55% do apoio → só nos últimos ~28% | idem (~40%) |
  | Corpo | quadril sobe-desce 2,7× e arfagem 1,6° → nivelado | traseira pula, frente parada → suspensão recolhida, coluna recolhe/estende |
  | Cauda lateral (/cernelha) | 0,31 → 0,12 | 0,09 → 0,05 |
  | Dedos no apoio | retos (0°) → 3–15° para fora (no Ancestral mantidos retos) | idem |
- **Nova versão (reversível, `LOBO_MARCHA29=1`; Trote, Partida, Freada, transições, habilidades e modelo/rig/pesos/texturas intocados):** `marcha29()` com balanço min-jerk, altura até o toque, rolamento no fim do apoio, dobra do carpo/jarrete no meio do balanço e desfeita antes do pouso, dedos retos, regra da v28 (eixo da perna, polos, carpo auxiliar). Andar: passada 2,25 (3,02 studs/s), apoio 0,62, alturas 0,58/0,48, dobra 48°/34°, corpo nivelado e cauda menor. Corrida: **galope rotatório** (fases do Ártico), apoio 0,28, 21,43 studs/s (igual à v28), alturas 0,95/0,85, dobra 45°/30°, coluna recolhe/estende, arfagem 6°, cabeça estabilizada, cauda de contrapeso, orelhas para trás. A dobra do carpo foi limitada (com a do Ártico, 88–120°, a compressão palmar caía para 0,30–0,51: volta do "toco").
- **Montagem:** `review/marcha_v29/montar_v29.py` → `rig18/Lobo_Ancestral_Anim_v29.blend` (cópia da v28 com só `Lobo_Andar` e `Lobo_Corrida` trocados) e `clipes29/` (= clipes28 + Andar/Corrida; os outros 22 JSON idênticos). v26, v27 e v28 preservadas.
- **Resultados (v28 → v29; Ártico entre parênteses):**
  | | Andar | Corrida |
  |---|---|---|
  | Carpo da frente (dobra máx.) | 2° → 40° (66°) | 38° → 48° (103°) |
  | Cotovelo | 35° → 49° (48°) | 75° → 79° (100°) |
  | Altura do balanço frente/trás (/perna) | 0,068/0,065 → 0,123/0,097 (0,131/0,104) | 0,169/0,161 → 0,201/0,171 (0,219/0,183) |
  | Apoio frente | 0,72 → 0,69 (0,61) | 0,36 → 0,36 (0,36) |
  | Quadril sobe-desce (/cernelha) | 0,030 → 0,009 (0,012) | 0,117 → 0,134 (0,065) |
  | Arfagem | 1,96° → 0,45° (0,06°) | 6,6° → 9,3° (7,6°) |
  | Cauda lateral | 0,31 → 0,13 (0,12) | 0,09 → 0,10 (0,05) |
  | Deslize / IK | 0 / 0 → 0 / 0 | 0 / 0,0002 → 0 / 0,0003 |
  | Sola: z mín. / inclinação no apoio | −0,011 / −7,8…−0,5° → −0,012 / −8,4…−0,4° | −0,012 / −9,3…−0,5° → −0,012 / −8,5…−0,4° |
  | Compressão palmar do carpo | 0,85 → 0,65 | 0,67 → 0,58 |
  | Torção da coxa | 2,4° → 2,1° | 3,1° → 4,6° |
  | Distância mín. pernas E×D (frente/trás) | 0,073/0,031 → 0,074/0,034 | 0,068/0,030 → 0,066/0,027 |
  | Emenda do loop (maior passo / emenda) | 0,175 / 0,087 (contínuo) | 0,318 / 0,130 (contínuo) |
  - (A cernelha do Ártico é medida em `Coluna3` e a do Ancestral no topo da escápula: comparação de corpo é aproximada.)
- **GLB `export29/` (reimportado, `validacao_glb.json`):** 19.818 tris, 60 ossos, 24 ações, 2 texturas 1024, 0 vértices sem peso, ≤ 4 influências, pose de referência idêntica.
- **Sela v28 sobre a v29 (`m3b_sela_marcha.py` → `review/marcha_v29/sela_v28|sela_v29`):** Corrida igual (−0,288 / 3,1% contra −0,28 / 3,1%); Andar: pelo sob a sela até −0,18 num quadro (v28 −0,11), 0,9% da face de baixo (v28 0,8%) — leve aumento pela nova rolagem lateral; sem interpenetração nova visível.
- **Evidências:** `v28_v29_Artico_{Andar,Corrida}_{A,B}_{normal,lento}.mp4` (A = lado, 3/4, close lateral; B = frente, trás, close frontal; 2 ciclos), folhas `folha_<clipe>_{lado,close_lado,frente,tras}.png`, `closes_patas_<clipe>_v28_v29.png` (4 patas em pouso, apoio, impulso e balanço, fora e frente), `comparar_referencias.png`, `marcha_v28/v29/artico.json`, `diag_v29.json`, `analise_v29.json`.
- **Limitações:** a carpa dobra menos que a do Ártico (limite da malha LOW do Ancestral); na Corrida o quadril ainda sobe-desce mais que a frente e a coxa torce 4,6° (v28 3,1°). Alternativa medida: arfagem em fase com a subida (`LOBO_V29_PIT=-4 LOBO_V29_PIT_F=0.78`) deixa o corpo mais parecido com o Ártico (quadril 0,044, cernelha 0,034) mas a coxa vai a 5,8°.
- **Dependência:** `Hab_Investida` usa o galope da v28 (transverso). Se a Corrida v29 for aprovada, a Investida precisa ser regerada sobre o galope rotatório em outra etapa.
- **Base:** a v28 continua a base aprovada; a v29 só a substitui após avaliação. Roblox/Studio não usados.

## 6aj. Marcha v30: correção das regressões da v29 em Andar e Corrida (10/11/2026, aguardando avaliação; NÃO substitui a base v28) → `marcha/marcha_v30.py`, `review/marcha_v30/`, `clipes30/`, `export30/`
- **Preservado:** v28 (base aprovada) e v29 (`marcha_v29.py`, `Anim_v29.blend`, `clipes29/`, `export29/`) intactas. A v30 é carregada com `LOBO_MARCHA30=1` e montada por `review/marcha_v30/montar_v30.py` (cópia da v28 com só Andar e Corrida trocados); os outros 22 clipes de `clipes30/` são idênticos à v28.
- **Diagnóstico quadro a quadro da v29 (`diag_carpo_coxa.py`, `analisar_pernas.py`):**
  - **carpo do Andar:** a compressão palmar só cai no meio do balanço (DE q1–5, DD q19–23), proporcional ao ângulo do punho (20° → 0,98; 46° → 0,74; 64° → 0,65). Limite da malha LOW: para 0,85 o carpo precisa ficar perto da v28.
  - **coxa da Corrida:** a torção cresce no apoio, à medida que a pata traseira recua (q3–q7: 1,7° → 5,3°). O plano de repouso da perna traseira é inclinado (9°) e não é paralelo ao movimento; a pata que recua em linha reta sai desse plano e o joelho gira (jarrete x 1,00 / joelho 1,05).
  - **quadril da Corrida:** o sobe-desce vinha da **arfagem em torno do centro do tronco** (a traseira, longe do pivô, subia e descia ~0,7 stud), não da subida do corpo.
- **Hipóteses testadas e descartadas (medidas):** polo do joelho preso à raiz (coxa 4,6 → 5,2°); polo calculado no plano de repouso (coxa 6,9°, traseiras a 0,01); abrir a traseira no balanço (6,2–8,2°); fração maior do carpo auxiliar (pior); correção lateral do jarrete também no apoio (coxa 2,5°, mas a pata deslizava de lado 0,7–3,3 studs/s); menos rolamento da traseira, mais arfagem ou menos coluna (4,1–4,4°).
- **Correção adotada (só no código da marcha v30):**
  - **coxa:** no balanço, a pata traseira é posta para o jarrete ficar no plano de repouso da perna; no apoio, x constante (o do meio do apoio) → sem deslize lateral; apoio traseiro um pouco à frente (centro 0,35);
  - **corpo da Corrida:** arfagem 4,5° em torno do **quadril** (a frente sobe e desce, o quadril fica estável, como no Ártico), subida do corpo 0,10, flexão da coluna/pelve à metade, menos rolamento da sola traseira (12°);
  - **carpo:** Andar com dobra de 10° e rolamento de 14° (limite da malha para 0,85+); Corrida com dobra de 38°.
  - Mantidos da v29: galope rotatório, balanço min-jerk, altura que só zera no toque, patas apontadas para a frente, velocidades (Andar 3,02, Corrida 21,43 studs/s).
- **Resultados (v28 → v29 → v30; Ártico entre parênteses):**
  | | Andar | Corrida |
  |---|---|---|
  | Compressão palmar do carpo | 0,85 → 0,65 → **0,865** | 0,674 → 0,58 → **0,672** |
  | Compressão dorsal do carpo | 0,79 → 0,63 → 0,825 | 0,645 → 0,64 → 0,675 |
  | Torção da coxa | 2,38° → 2,05° → **1,63°** | 3,13° → 4,62° → **3,12°** |
  | Quadril sobe-desce (/cernelha) | 0,030 → 0,009 → 0,009 (0,012) | 0,117 → 0,134 → **0,033** (0,065) |
  | Cernelha (ombros) sobe-desce | 0,026 → 0,013 → 0,013 (0,012) | 0,028 → 0,018 → **0,104** (0,138) |
  | Arfagem | 1,96° → 0,45° → 0,45° (0,06°) | 6,6° → 9,3° → **7,3°** (7,6°) |
  | Flexão da coluna | 2,2° → 1,9° → 1,9° (0,9°) | 14,2° → 15,5° → 7,9° (8,2°) |
  | Dobra do carpo da frente | 2° → 40° → 8° (66°) | 38° → 48° → 35° (103°) |
  | Cotovelo | 35° → 49° → 47° (48°) | 75° → 79° → 68° (100°) |
  | Altura do balanço frente (/perna) | 0,068 → 0,123 → 0,123 (0,131) | 0,169 → 0,201 → 0,201 (0,219) |
  | Distância mín. pernas E×D (frente/trás) | 0,073/0,031 → 0,074/0,034 → 0,069/0,028 | 0,068/0,030 → 0,066/0,027 → 0,069/0,032 |
  | Deslize (frente e lateral) / IK | 0 / 0 em todas | 0 / 0,0002 → 0 / 0,0003 → 0 / 0,0002 |
  | Pata abaixo do chão | −0,011 / −0,012 / −0,011 | −0,012 nas três |
  | Loop: maior passo / emenda | v30 0,101 / 0,038 | v30 0,226 / 0,126 (contínuo) |
  - (A cernelha do Ártico é medida em `Coluna3`, a do Ancestral no topo da escápula: comparação de corpo aproximada.)
- **Compromisso explícito:** no Andar, a meta de 0,85 só é atingida com o carpo quase sem dobra no balanço (8°, contra 66° do Ártico); a fluidez do Andar vem da passada min-jerk, da altura do balanço (0,123) e do cotovelo (47°). Com dobra de 25–35° a compressão fica em 0,81–0,76 (mais próximo do Ártico, mas pior que a v28). Na Corrida o carpo dobra 35° (v28 38°).
- **Pequenas pioras restantes:** no Andar a distância entre as pernas cai um pouco (0,073/0,031 → 0,069/0,028), sem cruzamento.
- **GLB `export30/` (reimportado):** 19.818 tris, 60 ossos, 24 ações, 2 texturas 1024, 0 vértices sem peso, ≤ 4 influências, pose de referência idêntica (0,0), 5,90 MB (igual à v28): sem custo adicional para PC/celular.
- **Sela v28:** Andar −0,182 / 1,0% e Corrida −0,286 / 3,5% de pelo sob a sela (v28: −0,11 / 0,8% e −0,28 / 3,1%); leve aumento no Andar, já presente na v29; sem interpenetração nova visível.
- **Evidências (`review/marcha_v30/`):** `v28_v29_v30_Artico_{Andar,Corrida}_{A,B}_{normal,lento_0.5x}.mp4` (A = lado, 3/4, close lateral; B = frente, trás, close frontal; 2 ciclos), folhas `folha_<clipe>_{lado,close_lado,frente,tras}.png`, `closes_patas_<clipe>_v28_v29_v30.png` (4 patas no apoio, balanço e pouso), `comparar_referencias_v30.png`, `tabela_v28_v29_v30_artico.json`, `diag_v30.json`, `analise_v30.json`, `marcha_v30.json`.
- **Dependência:** `Hab_Investida` continua sobre a Corrida v28 (galope transverso); atualizar em outra etapa se a v30 for aprovada.
- **Base:** v28 continua a base aprovada. Roblox/Studio não usados.

## 6ak. v31: patas apontadas 100% para a frente (11/11/2026, patas retas APROVADAS pelo usuário em 11/11; Roblox não testado) → `review/patas_dir/`, `rig18/Lobo_Ancestral_Anim_v31.blend`, `export31/`
- **Pedido:** "as patas estão viradas para o meio... a direita aponta à esquerda e a esquerda à direita"; depois "ainda possuem uma virada ao outro lado, quero 100% reta à frente".
- **Diagnóstico:** os ossos dos dedos já apontavam para a frente; o desvio é da **malha** (modelagem), igual na v28 e na v30.
- **Medida confiável (`direcao_fixa.py`):** vértices FIXOS da ponta e do calcanhar de cada sola, escolhidos uma vez no modelo original (`indices_sola.json`) e acompanhados em todas as versões (as medidas por forma da sola — quartis e eixo de simetria — eram instáveis com 18–36 vértices e chegaram a dar sinais contraditórios). v30: dianteiras **−9,35°** e traseiras **−27,23°** (para dentro).
- **Primeira tentativa (36°/9°, guardada em `Lobo_Ancestral_Anim_v31_36graus.blend`):** traseiras passaram para **+8,8° para fora** — a "virada ao outro lado" que o usuário viu.
- **Correção final (`endireitar_patas.py` com 27,23° traseiras e 9,35° dianteiras, sobre a v30):** gira só os vértices das patas em volta do eixo vertical do centro da sola (peso total até 0,45 de altura, transição até 1,1). Ossos, pesos, UV, texturas, tris (19.818) e ações iguais.
- **Resultado (graus; + fora / − dentro):** repouso **0,0** nas quatro; traseiras **0,0** em todos os quadros medidos do Andar, Trote e Corrida; dianteiras apoiadas −0,2 a +0,1; dianteiras no balanço (dobradas) −1 a −5,7 (a dobra segue o plano inclinado da perna); Sentado dianteiras +4,5.
- **Contato:** pata abaixo do chão Andar −0,011 → −0,020, Trote −0,012 → −0,024, Corrida −0,012 → −0,025; distância entre pernas, deslize e IK iguais.
- **GLB `export31/`:** 60 ossos, 24 ações, 2 texturas, 0 vértices sem peso, ≤ 4 influências.
- **Evidências:** `Patas_retas_v30_v31_{normal,lento_0.5x}.mp4` (frente, trás, close frontal; Andar e Corrida), `final_{baixo_tras,baixo,frente_baixa,tras_baixa}.png` (v30 × 36° × final), `fixa_v30.json`, `fixa_v31.json` (36°), `fixa_v31d.json` (final).
- **Limitações:** pequeno aumento do afundamento da pata (até −0,025); no balanço as dianteiras dobradas giram até 5,7° para dentro (no ar). Base aprovada continua v28; v29/v30/v31 aguardam avaliação; Roblox não testado.

## 6al. Repertório de vida realista (11/11/2026; lotes 1 a 5 APROVADOS em 12/11) → `comportamento/`
- **Pedido:** "todas as animações realistas; ele viverá naturalmente na floresta ancestral: beber, comer, descansar, uivar, entre todas as outras de um lobo da vida real; melhore movimentação, posições, adicione se necessário".
- **Inventário atual (24 + 3 kit + 4 montaria):** Repouso, Observar, Andar, Trote, Corrida, Partida, Freada, VirarE/D, Sentar/Sentado/LevantarSentado, Deitar/Deitado/Descanso/LevantarDeitado, Adormecer/Despertar (dormir aprovado), Salto, Uivo, Rosnar, Mordida, Garra, Impacto; kit Salto Predatório/Uivo Ancestral/Investida; Montar/Desmontar E/D.
- **Plano por lotes (cada um mostrado e aprovado antes do próximo):**
  1. **Lote 1 — necessidades básicas (APROVADO 11/11):** `Beber` (7 s: desce abrindo as dianteiras, lambe em rajadas de ~3/s, ergue e olha em volta, volta a beber), `Comer` (8 s: morde, puxa com o pescoço para trás e sacode, mastiga de lado), `Farejar` (laço 4 s: nariz baixo varrendo E/D com fungadas), `Sacudir` (1,8 s: onda da cabeça à cauda, 4,5 Hz), `Espreguicar` (4 s: reverência e esticada da traseira), `Bocejar` (2,4 s: boca bem aberta, olhos fecham).
  2. **Lote 2 — conforto e higiene (APROVADO 11/11 após r4; Cocar retirado):** `LamberPata` (5 s deitado: cabeça sobre a dianteira E, lambidas ~3/s com pausa), `Cavar` (4 s: frente baixa, dianteiras alternadas puxando a terra sob o peito), `DormirEnrolado` (laço 6 s: corpo em arco, focinho para a garupa, cauda contornando). **Adiados:** rolar no chão e mudar de lado deitado (exigem rotação do corpo inteiro no chão; arriscado no rig atual).
  3. **Lote 3 — alerta e caça (feito, em avaliação):**
     - `Alerta` (4 s): congela, cabeça alta, orelhas giram para o som, fareja o ar e relaxa.
     - `Espreita` (laço, 0,86 studs/s): corpo 1,7 mais baixo (barriga 1,5 do chão), cabeça na linha do dorso, cauda baixa, passada curta e lenta (apoio 76%).
     - `FarejarAndando` (laço, 1,61 studs/s): passo lento, focinho baixo varrendo, fungadas.
     - `OlharTras` (3,6 s): por cima do ombro esquerdo, patas plantadas.
     - `Bote` (2,8 s, salto de rato): fixa agachado, ajeita as traseiras, salta alto em arco, cai com as dianteiras prendendo e o focinho na presa. Termina 2,4 à frente, como o Salto.
  4. **Lote 4 — social e vocal:** uivo sentado e em pé (revisão do atual), latido curto/aviso, ganido, rosnado com lábio (limite do rig), cauda conforme o estado.
  5. **Lote 5 — revisão dos clipes existentes** para mais naturalidade (Repouso com troca de peso e orelhas, Observar, Sentar/Deitar, Uivo), sem quebrar o que já foi aprovado.
- **Lote 1 — técnica:** `comportamento/clipes_vida_l1.py` (carregado com `LOBO_VIDA=1`, clipes aprovados intactos), no rig v28; ações gravadas em `rig18/Lobo_Ancestral_Anim_Vida_L1.blend` com as patas retas da v31; JSON em `comportamento/clipes_l1/`. Para o focinho alcançar o chão em pé, a frente desce (raiz −1,5, arfagem 24°) com as dianteiras abertas e o pescoço estende (ajuste `cara_no_chao` do dormir): queixo z 0,10 (beber), 0,18 (comer), 0,48 (farejar). QA: erro de IK ≤ 0,0003 (Espreguiçar 0,015), malha ≥ 0,06 do chão (Espreguiçar −0,59 = antebraço apoiado no chão na reverência, como no deitado). A reverência saía fraca porque a elevação automática do gerador erguia o peito e porque girar a raiz esticava demais as traseiras (IK 0,57); agora a frente desce pela curva da coluna/peito (12°) com a raiz −0,3/12° e o clipe fica fora da elevação automática. Vídeos em `videos_v31/vida_lote1/`.
- **Correção 11/11 (usuário: "ao se espreguiçar as patas viram para o lado"):** a versão entregue e APROVADA ("Aprovado, siga") usa `eixo_perna` (a pata dobra no plano da perna) com inclinação −60° na reverência. Registro factual: uma variante com −6° foi escrita mas não chegou a ser gerada (erro de sintaxe no comentário); o arquivo foi restaurado e reproduz exatamente o clipe aprovado (diferença 0,0).
- **Lote 2 — técnica:** `comportamento/clipes_vida_l2.py` (`LOBO_VIDA=2` carrega lote 1 + 2; aprovados intactos), rig v28; ações em `rig18/Lobo_Ancestral_Anim_Vida_L2.blend` com patas retas v31; JSON em `comportamento/clipes_l2/`. QA: Cocar IK 0,013 / malha −0,179 (= base Sentado); LamberPata IK 0,0003 / −0,394 (= base Deitado); Cavar IK 0,0003 / malha +0,054; DormirEnrolado IK 0,0087 / −0,618 (antebraço no chão). Correções: no Cocar o alvo da pata era longo (IK 0,49) → encurtado; rolagem ±5° fazia o quadril entrar no chão → 0°; a perna ficava escondida atrás do corpo → alvo deslocado X −0,6 (X −0,9 deu IK 0,124). O enrolar do DormirEnrolado é moderado (`LOBO_ENROLA` 1,0), mais visível de frente. Vídeos em `videos_v31/vida_lote2/` + `folha_lote2.png`. Roblox não testado.
- **Correção r2 11/11 (usuário: "dormindo de lado as patas ficam tortas e parece quebrar o pescoço; ao se espreguiçar as patas dobram muito; parece que coça o vento e se contorce todo"):**
  - **DormirEnrolado:** a curva girava o PEITO e as dianteiras ficavam presas (torciam); pescoço 66° + cabeça 16° + rolagem 6°. Agora o peito fica parado (desvio 0,019), a curva (12° × 3 ossos) gira só a garupa (raiz −36°) e as traseiras acompanham posição e direção (`yaw_pe`, novo e opcional em `aplicar`, não afeta os clipes aprovados); pescoço+cabeça 26° sem rolar, queixo no chão (0,05), cauda contornando. IK 0,0001, malha −0,46 (pelo do peito).
  - **Espreguicar:** dianteiras iam só 1,3 à frente e o antebraço dobrava sob o peito (malha −0,63). Agora esticam 2,8 (pata −38, `eixo_perna` mantido): IK 0,015, malha −0,30.
  - **Cocar:** a pata ficava 0,7 fora do corpo (no ar). Medido: a orelha fica a 7,2 do quadril e a perna alcança 4,95 — sentado, este modelo não alcança a orelha; agora coça o OMBRO/flanco (como lobos reais também fazem), pata na superfície do pelo, metatarso −60, vaivém curto 6/s; cabeça vira pouco e olha para a pata, sem sacudir. Trocado para a traseira ESQUERDA (`LOBO_COCA_LADO`, visível nas vistas de revisão). IK 0,0, malha −0,179 (= Sentado).
- **Correção r3 11/11 (usuário: "retire a animação de coçar, arrume as patas dobradas ao espreguiçar e não deixe a cabeça entrar dentro da perna"):**
  - **Cocar RETIRADO** (código, JSON, entrada do manifesto, ação `Lobo_Cocar` do `Anim_Vida_L2.blend` e vídeos). O lote 2 fica com LamberPata, Cavar e DormirEnrolado.
  - **Espreguicar:** medido no modelo de patas retas, a −38° a sola rolava ~8° e os dedos curvavam (ponta para baixo). Agora a pata dobra a −53° no plano da perna: chapada, reta para a frente (desvio 0,5°), na linha do antebraço. Pescoço −28/−12 e cabeça +4, para o focinho não entrar no antebraço.
  - **Cabeça × pernas dianteiras** (vértices da cabeça a < 0,45 / < 0,30 do osso do antebraço/mão, varredura a cada 0,2 s):
    - Espreguicar: 196 → 0.
    - LamberPata: 1003 → 0 (pata 0,35 para fora, queixo a 0,9, lambe por cima).
    - DormirEnrolado: 958 → 0 (queixo apoiado SOBRE as patas a 0,7, pescoço 12°).
    - Beber, Comer, Farejar, Sacudir e Bocejar: 0.
    - **Clipes antigos aprovados não alterados:** Adormecer 536 (t 1,6), Descanso 79 e Cavar 26 (< 0,45; contato leve). Aguardam decisão.
  - **QA:** Espreguicar IK 0,015 / malha −0,30; LamberPata IK 0,0003 / −0,39 (base Deitado); DormirEnrolado IK 0,0001 / −0,46.
- **Correção r4 11/11 (usuário: "encoste a cabeça no chão ou na perna, e arrume a perna que agora vira e fica torta ao se espreguiçar"):**
  - **Perna torta no Espreguicar:** o polo do cotovelo (ajuste da marcha) deixava o plano de dobra do cotovelo 85° fora da perna: o cotovelo entrava sob o peito e o antebraço torcia. Nova opção `polo_frente_vert` em `aplicar` (polo no plano vertical ombro→pata, com peso pela reverência; não afeta os clipes aprovados): plano 10–12°. Patas 0,3 para fora (pernas paralelas, alinhadas aos ombros) e 3° para fora (`yaw_pe`).
  - **Cabeça encostando sem entrar:**
    - Espreguicar: queixo no chão entre as patas (0,05). Contato só de pelo da bochecha: 6 vértices a < 0,30 do osso, que não mudam com patas mais abertas.
    - LamberPata: queixo 0,55 encosta na pata (0 a < 0,30).
    - DormirEnrolado: queixo 0,4 encostado na perna (0 a < 0,30).
  - **QA:** Espreguicar IK 0,015 / malha −0,30; LamberPata 0,0003 / −0,39; DormirEnrolado 0,0001 / −0,46.
- **Lote 3 — técnica:**
  - `comportamento/clipes_vida_l3.py`, gerado com `LOBO_VIDA=3 LOBO_MARCHA30=1` e carregado depois da marcha v30. Espreita e FarejarAndando usam `marcha29`, a mesma do Andar aprovado, com outro corpo e outra passada.
  - Ações em `rig18/Lobo_Ancestral_Anim_Vida_L3.blend` (patas retas v31); JSON em `comportamento/clipes_l3/`; vídeos em `videos_v31/vida_lote3/` + `folha_lote3.png`.
  - **QA:** IK ≤ 0,0003 (Bote 0,023 no ar); malha ≥ 0,05; cabeça dentro das pernas 0 em todos; plano do cotovelo 13–21° (andar 13–15°); deslize dos pés 0.
- **Ajustes medidos no lote 3:**
  - Espreita a −0,85 quase não agachava (−2,1 estoura o IK) → −1,7.
  - FarejarAndando: o focinho a 4,2 do chão → pescoço 60/35, frente −0,6/12° → 2,0. O pescoço do modelo é curto.
  - OlharTras: o peito girando 9° torcia o cotovelo (28°) → 4° (21°).
  - Bote:
    - com as patas juntas a cabeça entrava nas pernas (174 vértices) → patas na largura dos ombros (0);
    - focinho até 0,7 do chão;
    - a cauda baixa no agachado fazia a elevação automática erguer o lobo → cauda mais alta (base 25°) e agachado −1,6/−1,9.
- **Correção r2 do lote 3 (usuário: "na espreita a perna traseira parece se mover mais do que pode; no farejar a cabeça mais perto do chão, indo da esquerda para a direita; no bote parece que come os próprios pelos — dê um impulso com a cabeça para a frente"):**
  - **Espreita:** a −1,7 o joelho traseiro dobrava 130–155° e o jarrete até 112° (Andar: 63–98° e 73°). Agora: corpo −1,3 com a frente 5° mais baixa e passo traseiro curto (altura 0,18, dobra 10, rolamento 4, apoio centrado 0,35). Resultado: joelho 110–126°, jarrete 55–92°, faixa do jarrete 88 → 37.
  - **FarejarAndando:**
    - pescoço esticado para a frente (60/10, cabeça −5), em vez de dobrado (60/35/−26);
    - frente −1,0/18°;
    - nariz de 2,06 para 1,50 do chão e mais à frente das patas;
    - varredura E↔D de 9 para 16 (cabeça a < 0,30 da perna: 0).
  - **Bote:**
    - o pescoço dobrado até o queixo no chão afundava o focinho na juba do peito. Agora o peito desce (−1,6/30°) com o pescoço reto e o focinho fica 0,85 à frente do peito;
    - nova ESTOCADA (1,95–2,35 s): impulso só do pescoço para a frente e para baixo, com a boca abrindo. Girar o corpo tirava as traseiras do chão (IK 0,63);
    - traseiras 0,4 mais atrás;
    - IK 0,023 (só no ar); focinho 1,35; cabeça × pernas 0.
- **Correção r3 do Farejar (12/11; usuário: "rosto mais à frente, virado ao chão; parece que está cheirando o pelo"):**
  - **Problema medido:** o pescoço 60/10 com a frente a 18° virava o osso da cabeça para trás: focinho a 117° da horizontal, nariz 0,81 atrás da frente do peito, ou seja, dentro da juba.
  - **Correção:** pescoço 55/−5, cabeça −30, frente −1,1/18°.
    - Focinho a 72° para baixo, nariz 1,10 à frente do peito e a 1,51 do chão.
    - IK 0,0002; cabeça × pernas 0; deslize 0,005.
  - **Limite:** com a frente a 21° o nariz descia a 1,41, mas as dianteiras esticavam demais (IK 0,13), então não usei.
- **Lote 3 APROVADO (12/11, "Aprovado, siga").**
- **Lote 4 — vocal e social (12/11, aguardando avaliação):**
  - **Onde está:** `comportamento/clipes_vida_l4.py`, carregado com `LOBO_VIDA=4` (não precisa da marcha). Blend `rig18/Lobo_Ancestral_Anim_Vida_L4.blend` (patas retas), JSON em `comportamento/clipes_l4/`, vídeos em `videos_v31/vida_lote4/`.
  - **Clipes da base intactos:** os aprovados "Uivo" e "Rosnar" não foram mexidos; os 6 clipes abaixo são novos.
  - **UivoSentado (7,0 s):** começa e termina no Sentado, com a cauda apoiada.
    - Orelhas atentas, depois inspira (o peito enche).
    - Focinho a 61° acima da horizontal, chegando a 65° quando a nota sobe.
    - Boca em "O" (mandíbula 11, não escancarada), vibrato e olhos semicerrados.
    - A nota cai no fim e a cabeça desce um pouco.
  - **UivoEmPe (6,4 s):** igual ao sentado, mas em pé, com o peso um pouco atrás e a cauda pendente. O corpo não sobe na inspiração, porque isso esticava as patas (IK 0,10).
  - **LatidoAviso (2,4 s):** postura alta de alarme: orelhas à frente, nuca levemente eriçada, cauda na horizontal. Dois latidos curtos ("uf"), cada um com tranco do peito, cabeça à frente e boca abrindo e fechando rápido.
  - **Ganido (3,6 s):**
    - Corpo encolhido, orelhas para trás e para os lados, cabeça baixa e inclinada (troca de lado).
    - Dois ganidos com a boca quase fechada, tremendo.
    - Cauda baixa abanando curto; ergue a pata dianteira esquerda.
  - **RosnadoAmeaca (3,4 s, ofensivo):**
    - Cabeça na linha do dorso, olhar fixo, orelhas eretas à frente.
    - Nuca, dorso e juba eriçados (medido: nuca/dorso eriçam com X+, a juba lateral com X−).
    - Cauda alta e rígida com a ponta tremendo, peso à frente, boca entreaberta com vibração no peito.
    - Ameaça mais forte em 1,7–2,3 s.
  - **Saudacao (3,6 s, social):** corpo baixo, orelhas coladas, cauda baixa abanando largo com o quadril rebolando, e o focinho sobe "lambendo" o ar duas vezes.
  - **Cauda conforme o estado:** relaxada (uivo), horizontal (alarme), baixa curta (ganido), alta e rígida (ameaça), baixa larga (saudação).
  - **Medido:**
    - IK 0 em todos, exceto UivoEmPe (0,009); cabeça × pernas 0; deslize 0.
    - Malha mínima fora das patas ≥ 0,11. No UivoSentado é −0,179, igual ao Sentado aprovado (pelo comprimido no assento).
  - **Limite do rig:** não há osso de lábio, então o rosnado não franze o lábio nem mostra só as presas. Isso exigiria um osso ou forma nova na boca, o que é uma mudança de rig e precisa de aprovação.
- **Lote 4 APROVADO (12/11, "Aprovado, siga").**
- **Lote 5 — revisão dos clipes existentes (12/11, APROVADO pelo usuário em 12/11):**
  - **Onde está:** `comportamento/clipes_vida_l5.py`, carregado com `LOBO_VIDA=5`. Substitui, só neste lote, os clipes de mesmo nome. A base aprovada v31 (`rig18/Lobo_Ancestral_Anim_v31.blend`, `clipes30/`) fica intacta. Blend `rig18/Lobo_Ancestral_Anim_Vida_L5.blend` (patas retas), JSON em `comportamento/clipes_l5/`, vídeos em `videos_v31/vida_lote5/` (e `antes/` com Uivo/Adormecer/Despertar da v31).
  - **Auditoria dos 24 clipes da base:** cabeça a < 0,30 do eixo do antebraço/pata e erro de IK.
    - Defeitos: Adormecer com 225 pontos da cabeça dentro do antebraço direito (1,3–2,0 s); Despertar com 264 (0,1–0,5 s); Uivo com IK 0,074 (o corpo subia 0,10 com as patas plantadas).
    - Descanso tem 12–17: a cabeça encosta na pata, como na foto aprovada; mantido.
    - Demais: 0.
  - **Adormecer/Despertar:** medido quadro a quadro, a cabeça passa pelo antebraço direito e a pata esquerda recolhe por baixo do queixo.
    - Correção: o pescoço gira para a esquerda durante a transição (Adormecer 18° com a cabeça um pouco mais alta e a pata esquerda 0,8 por fora; Despertar 16°) e volta a zero, então a pose de dormir aprovada não muda.
    - Erguer a cabeça sozinha piorava (testado).
    - Resultado: 225 → 11 e 264 → 12, igual ao contato da pose de dormir.
  - **Uivo (4 s, mesmos marcadores 0,78/3,2):** focinho a 61° (+4° na nota), boca em "O" (11) com vibrato, olhos semicerrados, inspiração no peito, corpo sem subir. IK 0,074 → 0,009.
  - **Repouso (laço 4 → 8 s, sobre o aprovado):** troca de peso E/D, cabeça olha devagar, orelhas giram sozinhas (E 1,3 s, D 4,6 s, as duas à frente 6,2 s), piscadas (2,2 e 5,8 s), fareja o ar (3,2–3,8 s).
  - **Observar (4,5 s, mesmos marcadores):** as orelhas giram 0,15 s antes da cabeça, pisca no início de cada giro, o peso vai para o lado do olhar, fareja em cada lado.
  - **Sentado (laço 4 → 8 s):** olha devagar para os lados, orelhas sozinhas, três piscadas, a ponta da cauda mexe uma vez.
  - **Medido:** IK ≤ 0,009, deslize 0, malha igual à base (Sentado −0,179, Adormecer −0,407 = corpo deitado); os laços fecham sem salto (diferença 0,00).
  - **Não mexidos (sem defeito medido):** marcha, Partida/Freada, viradas, Sentar/Levantar, Deitar/Deitado/Descanso/LevantarDeitado, Salto, Rosnar, Mordida, Garra, Impacto.
- **Observação do lote 1:** para beber/comer/farejar o lobo dobra bastante as dianteiras (a cabeça fica perto das patas); o pescoço do modelo é curto para alcançar o chão só estendendo.
- **Vídeos de todas as animações atuais (patas retas v31):** `videos_v31/base/` (24), `videos_v31/habilidades/` (3), `videos_v31/montaria/` (4), normal e lento, 3 vistas.

## 6am. Import no Studio + kit Natureza em protótipo (15/11/2026; place isolado "Testes-loboancestral", placeId 73543092389791; aguardando avaliação) → `studio/`, `export31_studio/`
- **Place:** confirmado pelo usuário em 15/11 (arquivo `Loboancestral-testes.rbxl`, publicado por ele durante a sessão). A cópia herdou o place dos dragões (4,58 M instâncias): o primeiro Play travou o Studio. Com o consentimento do usuário a cópia foi **limpa** (dragões, scripts e backups apagados em lotes; ~2,6 mil instâncias) e salva. Backup completo: `Documents\RPG_Roblox\BACKUPS\Loboancestral-testes_BACKUP_antes-lobo_2026-11-15.rbxl`. RPG principal, Dragon Ranch e outros places não foram tocados.
- **Preparação no Blender (testado no Blender):**
  - `Hab_Investida` regenerada sobre a Corrida v30 (`habilidades/clipes_kit_v30.py`, `LOBO_KIT=1 LOBO_MARCHA30=1` → `habilidades/clipes_kit30/`, `rig18/Lobo_Ancestral_Anim_Kit_v30.blend`): mesmas fases e marcadores; IK 0,0003, deslize 0,0, malha ≥ 0,024; Corrida idêntica à `clipes30` (0,0). Vídeos `videos_v31/habilidades_v30/`. A v28 (`clipes_kit28/`) foi preservada.
  - Montar/Desmontar E/D regenerados no rig de 60 ossos (`montaria/clipes_m2_v31/`): idênticos aos aprovados nos 58 ossos comuns (0,0).
  - **GLB de importação** `export31_studio/Lobo_Ancestral_Studio.glb` (`studio/exportar_studio.py`): lobo v31 + sela v28 no MESMO esqueleto, sem ações, + 1 triângulo degenerado com peso no `Raiz`. Motivo medido: no `export31` o Raiz não tinha peso e a sela GLB tinha 48 ossos sem peso — o Import 3D descarta ossos assim. Reimportado: 60 ossos, todos com peso.
  - **Pacote dos clipes** `studio/LoboAncestral.rbxm` (`studio/empacotar_lobo.py` + `rojo build`): 51 clipes (24 da base com os 6 do lote 5 substituídos por nome, L1–L4, 2 do kit v28, Investida v30, 4 de montaria) + `AdaptadorLobo` (`studio/AdaptadorLobo.luau`). Inventário com fonte, lote, quadros, duração, marcadores e md5 em `studio/inventario.json`.
- **Studio (importado e testado no Studio, Play/PC):**
  - O usuário fez o Import 3D e o Insert from File. Modelo em `Workspace.Teste_LoboAncestral.Lobo_Ancestral` (RootPart ancorado, malhas sem colisão, sela visível só montado). Dados em `ReplicatedStorage.LoboAncestral`.
  - **Convenção dos ossos medida:** quadros do Andar e da Mordida aplicados no Studio × posições do Blender = erro 0,002 stud na convenção nova (antiga 2,0). Fixada no adaptador. Escala 1:1, frente = −Z.
  - Animações só em Play, `AnimationClipProvider:RegisterAnimationClip` (nada publicado; `studio/LoboAnimacao.luau`). 51/51 tocam sem erro; **todos os marcadores disparam**.
  - Passada com o modelo movido na velocidade do clipe (deslize mediano das patas apoiadas / velocidade): Andar 0,12/3,02, Trote 0,50/7,67, Corrida 0,48/21,4, Espreita 0,05/0,86, FarejarAndando 0,06/1,61, Partida 0,58 e Freada 0,38 com curva suave, Investida 1,6 com a curva do clipe. Sem salto de cabeça nas emendas (só o bote intencional da Investida).
  - Capturas: escala, textura, marcas, olhos, patas retas de frente, Uivo e sela encaixada. Folha `studio/review/comparacao_studio_blender_ref.png`.
- **Kit Natureza (protótipo, testado no Studio pelo servidor e pelo remoto do cliente):** `studio/kit/ConfigKitLobo.luau` (números [PROPOSTA]), `LoboKit_Servidor.luau` (ServerScriptService.LoboAncestral_Kit), `LoboKit_Cliente.luau` (StarterPlayerScripts: teclas Z/X/C/V/B, HUD mínima, folhas/vento discretos, pegadas só para o dono).
  - Instinto de Caça: pegadas só de inimigos vistos (linha de visão) a ≤ 60, sempre ≥ 1 s atrasadas; alvo atrás da parede = 0 pegadas; pista de ninho = só direção, erro medido 23° (limite 30°).
  - Caçador Noturno: estado único no servidor (ClockTime ≥ 18,5 ou < 5,5, histerese 0,1 h — testado 18h27/18h21/18h33/18h42/5h33/6h); noite: vel ×1,12, esquiva 15%, mordida 11,2 e garra 9,0 (dia 10/8).
  - Salto Predatório: recusa outro jogador, alvo inválido, fora de alcance (60), sem linha de visão (parede), ocupado e recarga; válido aterrissa diante do alvo e golpeia no marcador (0,87 s, 14 = 1,4×); arco bloqueado → para antes e cai sem dano; alvo que sai do raio → erra. Sem teleporte nem atravessar.
  - Uivo Ancestral: bônus só no BuffInicio, 6 s, só o próprio lobo; noite + uivo respeita o teto (vel +25%, esquiva 35%).
  - Investida: avança 12,4 studs (curva do clipe, sem patinar), para na parede e no primeiro alvo, 1 acerto por uso (2 alvos em fila: só o 1º). Ajuste feito no teste: alcance da mordida 4 → 1,5.
  - Esquiva medida em 2.000 golpes: 5,8% (esperado 5%) e 36% à noite com uivo (35%). Morte e remoção zeram bônus, cancelam tarefas e recusam pedidos. Spam de 30 pedidos pelo remoto real: 1 aceito; habilidades simultâneas recusadas.
  - Custo: 9 lobos animando = servidor 60 Heartbeat/s (1 lobo: 60). FPS do cliente não medido de forma válida (o Studio fora de foco fica preso em 15).
- **Pendências e riscos:** montaria funcional do lobo não existe no place (teste montado PENDENTE); sons do lobo inexistentes (pendente); celular e multiplayer NÃO testados; vídeos normais/lentos do Studio não gravados (os do Blender existem); cor no Studio mais fria que no Blender (iluminação herdada) — CORRIGIDA em 15/11 (ver abaixo); o salto/investida usam chão plano (sem raycast de terreno); o lobo segue o dono a pé com Andar/Corrida (sem Trote nem Partida/Freada nas trocas); a Investida avança 12,4 studs (não os 30 da proposta antiga, que patinariam com este clipe); gancho de teste `ServerStorage.LoboKitTeste` só em Studio.

- **Cor (15/11, a pedido do usuário):** a textura importada estava certa; o tom frio vinha da iluminação herdada dos dragões (céu azul refletido com EnvironmentDiffuseScale 1,0, brilho 3, ambiente cinza). Só neste place: Brightness 3 → 2,2; EnvironmentDiffuseScale 1,0 → 0,35; EnvironmentSpecularScale 1,0 → 0,5; Ambient 0,32/0,30/0,25; OutdoorAmbient 0,52/0,49/0,41; ColorShift_Top 1,0/0,92/0,78; Atmosphere cor 0,78/0,76/0,66 e decay 0,45/0,47/0,38; Bloom 1,0 → 0,6; ColorCorrection `Floresta_CorLobo` (saturação +0,05, contraste +0,05, tom 1/0,98/0,94). Valores antigos em `ServerStorage.Backup_Iluminacao_Lobo_2026-11-15`. Resultado: marrom quente, peito creme e marca verde como no Blender (`studio/review/cor_antes_depois.png`). É iluminação de teste, não a iluminação oficial do bioma.
- **Vídeo dos 51 clipes no Studio (15/11, aguardando aprovação):** `studio/review/Lobo_Studio_51clipes.mp4` (1280×720, 30 qps, 3 min 16 s, sem som). Gravado em Edit, sem Play: uma cópia temporária do lobo (`_VideoLobo_TEMP`, removida depois, place NÃO salvo) é posada quadro a quadro pelo `AdaptadorLobo.aplicarQuadro`, a mesma conversão dos KFS. Captura por PrintWindow com código do passo na tela: 5.879 passos, 24 perdidos (0,4%, repetidos do vizinho). Ordem: Locomoção (11), Vida (26), Combate (7), Kit (3), Montaria (4), com o nome na legenda. Avanço do corpo pela velocidade do próprio clipe (Andar 3,02; Trote 7,67; Corrida 21,43; Espreita 0,86; FarejarAndando 1,61; Partida/Freada pela rampa; Investida pela curva do kit30). Salto Predatório com arco de demonstração de 16 studs [PROPOSTA]. Montar/Desmontar com a sela visível, mas sem cavaleiro. Iluminação de teste da floresta.

## 6an. Virar andando + patas no giro + pelo do rosnado (16/11/2026; APROVADO pelo usuário 16/11 pelo vídeo de revisão; ida ao Studio em §6ao) → `marcha/curvas_v32.py`, `marcha/review_curvas32/`

Pedido do usuário depois do vídeo do Studio: "ao virar deve ser mais natural, em vez de parar para virar, poder virar andando, e suas patas ficam estranhas ao virar [...] E ao rugir, seu pelo se divide".

- **AndarCurvaE / AndarCurvaD (novos):**
  - É o Andar v30 andando em curva. O jogo gira o modelo a 30°/s em volta do ponto sob o meio do corpo e avança 3,02 studs/s, o que dá um raio de cerca de 5,8 studs. O giro é `LOBO_CURVA_GIRO`, um parâmetro [PROPOSTA].
  - A pata apoiada fica parada no mundo, em posição e em direção. A pata no ar vai da saída ao pouso e já pousa virada para dentro da curva.
  - Na curva, a coluna dobra para dentro, a cabeça olha a curva, o corpo inclina 1,5° e a cauda faz contrapeso.
  - Gerado com `LOBO_MARCHA30=1 LOBO_CURVAS=1`, mais as patas retas (27,23/9,35).
  - Saídas: `rig18/Lobo_Ancestral_Anim_Curvas_v32.blend` e JSON em `marcha/clipes_curvas32/`. O Andar regenerado é idêntico ao do clipes30 (diferença 0).
- **VirarE / VirarD r2:** na r1, as patas mudavam de posição no círculo mas continuavam apontando para a frente antiga, e terminavam a 89° do corpo (medido). Na r2, cada pata gira junto com o próprio passo; no fim ficam a 0,6–1,8° do corpo.
- **Dedos:** `aplicar()` não passava o giro da pata (`yaw_pe`) para os ossos dos dedos. Agora passa, mas só quando o clipe marca `yaw_dedos`, então os clipes aprovados não mudam.
- **QA no mundo** (`marcha/render_curvas.py`): pata apoiada com deslize de 0,000 studs/s e giro de 0,0° nas 4 curvas e viradas, com IK 0.
  - A mesma conta acusa 3,02 studs/s no Andar sem o avanço do corpo, o que prova que ela detecta deslize.
  - Distância mínima entre patas na curva: 0,67, contra 1,71 na reta.
- **Pelo do rosnado (RosnadoAmeaca e LatidoAviso r2):**
  - **Causa medida (renders de perto):** os ossos PeloNuca e PeloDorso, girados para "eriçar", levantam a placa de pelo do dorso como uma aba escura descolada da juba. Isso acontece já com a nuca a 5–10°. Com 0°, a juba fica inteira.
  - **Correção:** `LOBO_ROS_PELO` passou de 22 para 0 e `LOBO_LAT_PELO` de 8 para 0. Só esses ossos de pelo mudaram; o resto do clipe é idêntico ao aprovado de 12/11.
  - Saídas: `rig18/Lobo_Ancestral_Anim_Vida_L4_r2.blend` e `comportamento/clipes_l4_r2/`. A comparação antes/depois está em `comportamento/review_pelo_r2/`.
- **Vídeo de revisão:** `marcha/review_curvas32/Lobo_Curvas_e_Pelo_r2.mp4` (32 s).
- **Pendente:**
  - aprovação do usuário;
  - empacotar os 6 clipes no Studio e girar o modelo no jogo durante a curva (combinação reta + curva, como no urso);
  - Trote e Corrida em curva.

## 6ao. Curvas v32 + VirarE/D r2 + pelo r2 no Studio (16/11/2026; Testes-loboancestral; vídeo APROVADO pelo usuário 16/11) → `studio/`, `studio/kit/LoboKit_Servidor.luau`
- **Aprovação:** o usuário aprovou a §6an em 16/11 ("Aprovado").
- **Pacote:** `studio/empacotar_lobo.py` agora tem 53 clipes:
  - novos: AndarCurvaE/D (`marcha/clipes_curvas32`);
  - substituídos pelo nome: VirarE/D (curvas v32, r2) e RosnadoAmeaca/LatidoAviso (`comportamento/clipes_l4_r2`).
  - O `rojo build` gerou um novo `studio/LoboAncestral.rbxm`. Só esses 6 `dados/*.txt` mudaram.
- **Studio (testado no Studio):**
  - Os 6 StringValues foram gravados em `ReplicatedStorage.LoboAncestral.Dados` e conferidos byte a byte (tamanho + checksum) contra os arquivos. Os 4 antigos ficaram em `ServerStorage.Backup_Dados_Lobo_2026-11-16`.
  - O adaptador lê os 6 com as fontes certas (rotação 36/−36/90/−90; marcadores GiroCompleto e Rosnado/Latido).
- **Jogo (`LoboKit_Servidor`, bloco "seguir o dono"; patch por âncora, compilação checada; original em `ServerStorage.Backup_LoboKit_Servidor_2026-11-16`):**
  - Andando, o lobo anda só para a frente e vira em volta de O = 2,196 studs à frente do pivô (o mesmo centro do Blender).
  - Andar e AndarCurvaE/D tocam juntos e em fase, com pesos 1−|pc| e |pc|; o giro aplicado é pc × 30°/s × ritmo.
  - Parâmetros [PROPOSTA]: ganho 1,6 e pc limitado a 3/s.
  - Dono a mais de 120° com o lobo parado: VirarE/D r2, e no marcador GiroCompleto o modelo gira 90° em volta de O.
  - A Corrida continua com o giro antigo (não há clipe de curva de corrida).
- **Teste em Play (cliente, 14 qps, Studio fora de foco):** deslize mediano da pata apoiada com o lobo em movimento:
  - reta: 0,04 studs/s;
  - curva E: 0,04 (giro total 125°);
  - curva D: 0,05 (giro total −125°);
  - dono atrás: VirarE seguido de curva, 0,08.
  - O peso do clipe de curva chegou a 1,0. Sem erros no console.
- **Vídeo:** `studio/review/Lobo_Studio_Curvas_e_Pelo_r2.mp4` (35 s, 1.054 passos, 76 perdidos e repetidos do vizinho).
  - Gravado em Edit pelo AdaptadorLobo, com uma cópia temporária removida depois.
  - Conteúdo: curvas E/D de cima e de perto, VirarE/D r2 e close do Rosnado/Latido.
  - A mistura reta+curva só foi medida em Play; não aparece no vídeo.
- **Place salvo na versão 17.**
- **Pendente:** aprovação do vídeo; curvas de Trote/Corrida; celular e multiplayer não testados.

## 6ap. Kit do Lobo Ancestral alinhado à v6.2 de REFERENCIAS_PODERES_E_EFEITOS (16/11/2026; Testes-loboancestral; place salvo v19; aguardando avaliação)
- **Fonte:** `Documents\RPG_Roblox\REFERENCIAS_PODERES_E_EFEITOS.md` v6.2 (19:43, com §0d escala do mundo), §2 Lobo Ancestral. As cópias da raiz do repositório ainda são a v5.2.
  - O §2 é igual nas duas versões.
  - A §0d dá ao lobo: ombro de 5,5–7, corrida de 21,4 [EXISTE] e alcance básico ≥ ombro (Mordida 7 / Garra 6 atendem).
- **Mudanças (todas [PROPOSTA]):** em `studio/kit/ConfigKitLobo.luau`, `LoboKit_Servidor.luau` e `LoboKit_Cliente.luau`; os originais estão em `ServerStorage.Backup_KitLobo_v6_2026-11-16`.
  - Elementos: Natureza e Ar.
  - Teto de bônus de velocidade 0,35 (noite + Uivo = 32%). Esquiva total limitada a 35% (base 5% + bônus até 30%).
  - **Uivo:** +20% de velocidade, +25% de esquiva, 8 s, recarga 20, energia 20.
  - **Salto Predatório:** alcance 8–50. Funciona sem alvo, indo ao ponto do mouse: o servidor limita a distância, não causa dano e custa 12 de energia.
    - Planeio de 0,6 s no ápice: o clipe congela no ápice.
    - Encadeável: em até 2 s após pousar, o 2º salto não tem recarga e custa metade da energia, uma vez por cadeia.
    - Dano de 1,2× com alvo.
  - **Instinto de Caça:**
    - raio 80;
    - marca da presa por 8 s (o alvo do Salto ou quem o lobo acerta), com +10% de dano só nela;
    - contorno verde e seta, visíveis só para o dono;
    - pegadas luminosas que somem em 8 s.
  - **Visual:** sem folhas ou partículas soltas. Fora do corpo, só faixas de vento em espiral: 8 no Uivo (fade no último 1,5 s), 4 no Salto e na Investida, e uma rajada na pista de ninho.
  - O arquivo local do cliente tinha a string do HUD quebrada em várias linhas e não compilaria; foi corrigido. O Studio usava a versão do instalador, que estava correta.
- **Testado em Play (servidor pelo gancho de teste + cliente; sem erros no console):**
  - **Uivo:**
    - durante o efeito: velocidade 1,20× e esquiva 0,30; repetir durante a animação é recusado;
    - depois de 8,8 s: 1,00× e 0,05;
    - noite + Uivo: 1,32×, esquiva 0,35 (teto) e dano 1,12×.
  - **Salto sem alvo:**
    - ponto a 80 studs: pousou a 50, custo 12, voo de 1,05 s;
    - encadeado: custo 6, sem recarga;
    - 3º salto e salto após a janela: recusados ("recarga");
    - recusados também: texto, nil, outro jogador, alvo a 70/80 (fora de alcance), alvo atrás da parede e alvo atrás de outro (sem linha de visão).
  - **Salto com alvo e marca da presa:**
    - presa marcada na decolagem; dano de 13,2 (10 × 1,2 × 1,10), custo 20;
    - mordida na presa marcada: 11,0;
    - após 8 s sem acerto, a marca some e a mordida volta a 10,0.
  - **Cliente:** 8 faixas de vento no Uivo e 4 no Salto, 0 emissores de partículas, contorno e seta na presa, HUD com o bônus. Captura em `studio/review/kit_v62_uivo_vento.jpg`.
- **Pendente:**
  - [PENDENTE] Linhas verde-musgo contínuas, runas e olhos do Uivo (§5.2): precisam da "capa de efeito".
  - [PENDENTE] Revelar inimigos escondidos na vegetação: não há sistema de esconderijo.
  - [PENDENTE] Mira pela câmera no celular e alvo travado: hoje é só o mouse.
  - Sons do lobo inexistentes.
  - Idades (§0c) não aplicadas: decisão conjunta de todas as criaturas.
  - Celular e multiplayer não testados.

## 6aq. Brilho do Uivo no corpo (linhas, runas e olhos), §5.1/§5.2 da v6.2 (16/11/2026; Testes-loboancestral; aguardando avaliação) → `habilidades/efeito_uivo/`
- **Documentos:** sem versão nova; a v6.2 (`Documents\RPG_Roblox`, 19:43) continua a última.
- **Como foi feito:** máscara emissiva na própria SurfaceAppearance do lobo; o efeito fica no pelo e acompanha a pele animada, sem malha nova.
  - `gerar_mascara_uivo.py` rasteriza o UV da malha LOW (1024², UV espelhado e reaproveitado).
  - Linhas: 5 em volta do tronco/pescoço/cauda e 2 descendo por cada pata (metade da força); espessura de 0,9% da altura; mais fortes nas costas e nos ombros.
  - Rosto: zerado em qualquer texel usado pela frente da cabeça.
  - Runas (haste + ramos + anel): ombro, flanco e coxa.
  - Olhos: marcados por triângulo.
  - Conferência no Blender: `review/r1–r5`.
- **Assets enviados à conta do usuário (com autorização):** listados em `habilidades/efeito_uivo/ASSETS.md`.
- **Limites medidos no Studio:**
  1. EditableImage no jogo exige "Allow Mesh / Image APIs" (segurança da experiência; não alterado).
  2. Uma EditableImage de 1024² fez a SurfaceAppearance parar de renderizar no Edit (restaurada na hora).
  3. Um LocalScript **não pode** trocar EmissiveMaskContent, só EmissiveStrength/Tint.
  - **Solução adotada:** máscara do pico fixa no lobo (salva no place), tinta verde-musgo e força 0 fora do Uivo. O cliente anima só a força: entrada de 0,3 s, respiração de 2,2 s, reforço no pico e saída no último 1,5 s.
- **Testado em Play:**
  - força medida a cada 0,9 s: 0 → 2,5 / 2,2 / 1,8 / 2,1 / 1,5 / 2,2 / 1,7 / 1,7 / 0,5 → 0 (volta a 0 no fim);
  - captura `studio/review/kit_v62_uivo_brilho.jpg`: linhas na juba e nas patas, runa da coxa acesa, vento circulando; fora do Uivo o lobo fica normal.
- **Place salvo.** Backups em `ServerStorage.Backup_KitLobo_v6_2026-11-16` (SA_Emissivo_antes, LoboKit_Cliente_antes_brilho).
- **Pendente:**
  - [PENDENTE] pulso de luz percorrendo o corpo (exigiria trocar a máscara em tempo real: só com EditableImage liberada ou outra técnica);
  - runas "apagadas" fora do pico: com a máscara fixa, acendem junto com as linhas;
  - contorno verde nos ombros e no pescoço;
  - sulco escuro ao lado das linhas;
  - tom por padrão de pelo;
  - celular não testado.

## 6ar. Brilho r2 + kit completo do Lobo Ancestral pelo documento de poderes (16/11/2026; Testes-loboancestral; aguardando avaliação)
- **Pedido do usuário:** "adicione linhas verdes, e quero que seus olhos brilhem verdes. As linhas devem estar no corpo"; depois, "faça todos os poderes do lobo ancestral, seguindo o documento de poderes". O §2 da v5.2 (raiz) é igual ao da v6.2.
- **Brilho r2:**
  - Linhas: 9 em volta do tronco, pescoço e cauda, e 4 em cada pata (força 0,7); espessura de 1,3% da altura (teto do §5.1).
  - Olhos com raio maior; tinta verde mais saturada (60, 210, 70), porque a íris original é amarela e o verde-musgo deixava os olhos amarelados.
  - Força 4 no cliente; máscara r2 `rbxassetid://134314902144047`.
  - **Play:** força 0 → 5,3 (pico) / 3,8 / 3,2 / 3,8 / 2,8 / 4,0 / 3,0 / 3,1 / 0,9 → 0. Captura `studio/review/kit_v62_uivo_brilho_r2.jpg`: linhas verdes no corpo, juba, patas e cauda, e olhos verdes durante o Uivo; lobo normal antes e depois.
- **Instinto de Caça, "revela inimigos escondidos em vegetação":**
  - Vegetação = parte com atributo `Vegetacao`. Ela não bloqueia a visão do Instinto; paredes e rochas continuam bloqueando.
  - Revelado = inimigo dentro da vegetação (raio de 1 stud) ou com atributo `Escondido`, a até 80 studs e visível por esse critério.
  - Só o dono vê: contorno verde AlwaysOnTop, renovado a cada 1 s.
  - **Testado em Play com arbustos temporários (removidos):**
    - sem arbusto: 0 revelados;
    - arbusto no Alvo_Perto: 1 (só ele tem contorno no cliente);
    - arbusto na frente do Alvo_Frente: ele continua não revelado, porque não está dentro do arbusto;
    - `Escondido` atrás da parede: não revelado, porque a parede bloqueia.
- **Mira (§1):** alvo travado → mouse → câmera no Salto e na Investida.
  - T trava o alvo válido mais próximo num cone de 60° da câmera, até 40 studs (contorno branco); T de novo destrava.
  - Sem mouse (celular/controle): ponto a 30 studs na direção da câmera.
  - O servidor revalida tudo.
  - **A tecla não foi testada** (sem entrada simulada); só a compilação e o caminho do servidor.
- **Kit completo do §2:** Salto, Uivo, Investida, Instinto e Caçador Noturno, todos implementados ([PROPOSTA], números do documento).
- **Pendente:**
  - [PENDENTE] pulso de luz percorrendo o corpo; o script do jogador não pode trocar a máscara;
  - contorno verde nos ombros e no pescoço; pegadas "com folhas";
  - sons;
  - idades (§0c);
  - celular e multiplayer;
  - testar a tecla T à mão.
- **Place salvo.** O original do servidor está em `ServerStorage.Backup_KitLobo_v6_2026-11-16.LoboKit_Servidor_antes_instinto`.

## 6as. Vídeo do kit v6.2 em Play + correção do Revelar (17/11/2026; Testes-loboancestral; place salvo v24; vídeo aguardando avaliação) → `studio/review/Lobo_Studio_Kit_v62.mp4`
- **Vídeo (33 s, tempo real, capturado por PrintWindow a ~18 qps e reamostrado a 30 qps no Blender):** poderes disparados pelo gancho `ServerStorage.LoboKitTeste` (mesmo caminho do remoto), câmera e rótulos só no Play.
  1. Uivo Ancestral (linhas e olhos verdes + vento); 2. Salto com alvo (Alvo_Frente, 22 studs, 13,2 de dano com marca); 3. Salto sem alvo 35 studs (custo 12) + encadeado 40 studs (custo 6); 4. Investida (parou no primeiro alvo, 12,0); 5. Instinto revelando inimigo dentro de arbusto temporário (removido).
- **Bug corrigido no cliente (r2 do Revelar):** o contorno durava 1,3 s e a renovação do servidor (a cada 1 s) era ignorada enquanto ele existia → piscava 1,3 s ligado / 0,7 s desligado. Agora renova o prazo (atributo `Ate`). Studio = local (14950 bytes, hash 671611028); backup do anterior em `ServerStorage.Backup_KitLobo_v6_2026-11-16.LoboKit_Cliente_antes_revelar_r2`.
- **Detalhe de tempo:** o 2º salto só é aceito ~1,95 s após o 1º (estado volta a Livre em golpe + planeio + 0,49 s); antes disso a resposta é "ocupado".
- **Pendente:** tecla T à mão, Caçador Noturno não aparece no vídeo, sons, celular e multiplayer.

## 6at. Efeitos r3 + percepção da IA + guardião de teste + bateria do Salto (17/11/2026; Testes-loboancestral 73543092389791; place salvo v29; aguardando avaliação) → `studio/kit/`, `studio/review/`
- **Fontes lidas:** CLAUDE.md, DOCS/ORGANIZACAO-CHATS.md, esta ficha (§6am, §6ap–6as), `studio/kit/`, `Documents/RPG_Roblox/REFERENCIAS_PODERES_E_EFEITOS.md` v6.2 (§2, §5.1, §5.2, §5.6, §5.10) e `REFERENCIAS/floresta-ancestral/lobo-ancestral/lobo-ancestral-referencia.png`.
- **Conflitos registrados, nada mudado:**
  - A v6.2 classifica o lobo como Natureza+Ar; a atualização oficial de 30/10 pede elemento único. `ConfigKitLobo.Elementos` continua {"Natureza", "Ar"} até decisão do usuário.
  - A §5.6 pede pegadas "com folhas"; o pedido de 17/11 proíbe folhas e partículas soltas. Valeu o pedido mais novo: pegadas sem folhas.
  - A referência mostra olhos âmbar; o usuário pediu olhos verdes em 16/11. Ficaram verdes.
- **M0 (só leitura):**
  - PlaceId e instância conferidos; placeVersion do Edit reporta 3, mas o save anterior foi v24.
  - Scripts instalados = locais, com duas linhas triviais diferentes no servidor.
  - Backups preservados.
  - Sons: 0 instâncias Sound no place → **sons pendentes**.
  - Em Play, um lobo sem dono e a regra antiga do laço (`if L.dono`) percebiam **0** alvos; com a regra nova, **3**. Teste A/B pela flag `percepcaoSemDono`.
- **Lacunas do v6.2 (ANTES):**
  - Uivo: sem preparação (o visual só começava no bônus, 0,6 s depois do clipe); pico por tempo fixo; faixas de vento de 0,12 stud, quase invisíveis.
  - Salto e Investida: só 4 faixas em órbita, sem brilho no corpo, sem sinal de pouso, contato ou obstáculo; o encadeado era igual ao normal.
  - Instinto: pegadas soltas sem direção; o contorno de revelado era AlwaysOnTop, sem checar parede entre a câmera e o alvo.
- **Servidor (`LoboKit_Servidor.luau`, todos [PROPOSTA]):**
  - **Percepção para todo lobo vivo:** raio 80, parede bloqueia e vegetação não. Os indicadores (pegadas, revelado, marca, pista de ninho) continuam só para o dono, por FireClient.
  - **Logs por categoria:** [PERCEPCAO], [IA], [HABILIDADE] e [INDICADOR].
  - **Velocidade de cada alvo:** medida no servidor, ignorando teletransporte de mais de 2 studs por quadro.
  - **Salto:**
    - pouso no chão real, sob as patas de trás (0,5) e da frente (5,3);
    - inclina com o declive até cerca de 26°;
    - recua da borda quando não há apoio firme; desnível máximo 8;
    - antecipa um alvo em movimento em até 10 studs, sem passar de 50;
    - obstáculo no voo faz o lobo cair até o chão (0,12–0,45 s), sem teleporte.
  - **Eventos de fase:** UivoInicio/UivoFim, SaltoPouso, InvestidaFim (alvo/obstáculo/nada).
  - **Guardião de TESTE (`IA_Guardiao` no Config):**
    - sem dono e sem patrulha; age só quando ameaçado: inimigo percebido a ≤ 22, chegando a ≥ 3 studs/s até 45, ou que o atacou;
    - escolhe Uivo → Mordida (≤ 8) → Investida (≤ 17) → Salto (18–50), com energia, recarga e alcance normais;
    - volta a calmo após 5 s sem ameaça e retorna andando ao posto;
    - não integrado ao jogo principal.
  - **Gancho de teste:** `recargas` agora zera a janela do encadeado (antes o salto seguinte saía como encadeado por engano). Comandos novos: flag, clonarIA, clonarSemDono, percebidos, ia, atacar, log, chao.
- **Cliente (`LoboKit_Cliente.luau`, efeitos r3; sem novos assets):**
  - **Mixer de brilho por camadas:** força e tinta da máscara r2, num laço único.
  - **Luz verde curta nos ossos** Pescoco1 e EscapulaE/D, acesa só nos picos (ombros e pescoço; sem halo).
  - **Fora do corpo só vento:** Trails de 0,2–0,3 stud.
  - **Uivo:** inspiração (linhas sobem com o ar, vento se fecha) → nota (pico 6, luz nos ombros, vento expande e acelera) → bônus respirando (cerca de 3,7) → término (último pulso e apaga em 1,5 s, vento sobe).
  - **Salto:** impulso (lampejo + ar puxado nas patas) → voo/planeio (brilho firme + vento rente que fica para trás) → pouso (lampejo + anel de ar no chão). Encadeado = tinta verde-água, duplo lampejo e hélice de vento; dano igual.
  - **Investida:** carga → brilho que acompanha a curva de velocidade + 4 faixas rentes. Contato = lampejo e ar empurrado à frente; obstáculo = linhas falham 2 vezes e ar desviado na parede.
  - **Instinto:**
    - marca com 3 pulsos e seta ▼ maior, balançando, com fade (Occluded, sem AlwaysOnTop);
    - pegadas em pares orientadas pelo movimento, a mais nova mais forte;
    - revelado e marca escondidos se houver parede entre a câmera e o alvo (vegetação não conta).
  - **Orçamento:** nada a mais de 150 studs; metade das faixas no celular (não testado).
- **Testes em Play (PC):**
  - **Salto:** 34 casos em `studio/review/testes_salto_r3.csv`, todos pelo gancho, que chama o mesmo `K.pedido` do remoto.
    - Com alvo parado a 10/25/35/45/50: acerto 13,2, custo 20, voo de 1,05 s, ápice 1,3–8,5.
    - Sem alvo 10–50: pousa no ponto; pedido de 80 limitado a 50; custo 12.
    - Com alvo a 55 ou 70: recusado.
    - Alvo em movimento: lateral 8/s, afastando 6/s e aproximando 6/s acertam (antecipação de 8,7–10); lateral 16/s erra por 14,4 (limite da antecipação).
    - Trajeto cruzando o muro: interrompido e cai. Alvo atrás do muro: recusado (sem linha de visão). Ponto dentro do muro: recua e pousa antes.
    - Plataforma +4: acerta. Rampa: inclina 14°, patas a 0,35 do chão. Borda de 12: recusada sem gastar energia. Queda de 4: ok.
    - Encadeado perto (+10) e longe (+50): custo 6; com alvo: custo 10, mesmo dano. 3º salto e salto fora da janela: recusados por recarga.
    - **Sincronismo:** clipe no pouso com mediana de 0,858 s (marcador 0,86).
  - **Remoto real do cliente** (FireServer, sem tecla física): Salto, Uivo e Investida aceitos; pedido em menos de 0,1 s ignorado; recarga e modelo inválido recusados.
  - **IA (gancho só para posicionar):**
    - percebeu o invasor a 44, saltou antecipando 8,8 e acertou 13,2; depois uivou, saltou de novo após a recarga e mordeu 11,0;
    - invasor parado atrás da parede a 12,7: não percebido, nenhuma reação; ao contornar, percebeu e uivou.
  - **Custo com 6 lobos no Uivo:** cerca de 0,2 ms/quadro de script do cliente; 48 Trails; 18 PointLights só no pico; 0 partículas.
    - FPS não medido de forma válida (Studio fora de foco fica em 15; 3 outros Studios em Play no PC).
- **Evidências (`studio/review/`):**
  - `Lobo_Studio_Kit_r3_antes_depois.mp4`: dia e noite lado a lado, lento 0,5x e as 2 cenas da IA. Captura em tempo real a 11–17,5 qps, então o lento repete quadros.
  - `kit_r3_antes_depois_dia.jpg`, `kit_r3_antes_depois_noite.jpg`, `kit_r3_6lobos_antes_depois.jpg`, `kit_r3_referencia_x_studio.jpg`, `testes_salto_r3.csv`.
- **Pendências e limites:**
  - **Sem teste:** sons (não há arquivos); celular e multiplayer; tecla física T/Z/X/C (não usei o teclado do usuário).
  - **Limites técnicos:**
    - o pulso de luz percorrendo o corpo e o destaque só das runas exigem trocar a máscara (precisaria de novo asset, só com autorização);
    - o giro da IA no lugar desliza as patas (sem clipe de virar parado ligado à IA);
    - a câmera do trecho do Instinto esconde o lobo atrás da parede (antes e depois).
  - **Backups:** `ServerStorage.Backup_KitLobo_efeitos_r3_2026-11-17` (versões instaladas antes do r3).

## 6au. Aura verde com ventania pela referência do usuário (18/11/2026; Testes-loboancestral; place salvo v32; aguardando avaliação) → `studio/review/Lobo_Studio_Kit_aura_r4.mp4`, `studio/review/kit_aura_r4_referencia_x_studio.jpg`
- **Pedido:** "siga a referência, seus pelos continuam da mesma forma, meio esverdeados, mas quero uma aura com ventania desta forma" (3 quadros: uivo, salto, corrida, com rajadas verdes em volta do corpo).
- **Mudança (só `LoboKit_Cliente.luau`; servidor intacto; nenhum asset novo):**
  - **Vento verde (150, 235, 125)**, cada rajada com 2 camadas:
    - halo largo e macio (textura `rbxasset://textures/particles/smoke_main.dds`, do próprio Roblox; 3x mais largo);
    - núcleo claro e fino (205, 255, 185).
  - **Uivo:** além da órbita, rajadas que correm da cabeça até a cauda a cada 0,35 s durante o bônus.
  - **Aura:** Highlight verde **só no contorno** (Occluded, tinta de 5% no máximo), acompanhando a força de cada fase.
    - Na 1ª tentativa a tinta de 20% pintou o lobo inteiro de verde: reprovada por mim antes de entregar.
- **Instalado e conferido por checksum:** cliente 29530 bytes. Backup em `ServerStorage.Backup_KitLobo_efeitos_r3_2026-11-17.LoboKit_Cliente_r3_antes_aura`.
- **Testado em Play (PC, dia):** Uivo, Salto curto/longo/encadeado e Investida, sem erro. Pelo continua como era; contorno verde e rajadas verdes visíveis.
- **Diferença que ainda resta para a referência:** lá as rajadas são mais numerosas, largas e macias e envolvem o corpo também no salto e na corrida; aqui, no salto e na investida, ainda ficam em poucas faixas.
- **Sem teste:** noite, várias cópias e celular. Os números continuam [PROPOSTA].

## 6av. TESTE: giros de vento espontâneos (18/11/2026; Testes-loboancestral; place salvo v33; aguardando avaliação) → `studio/review/Lobo_Studio_Vento_espontaneo_teste.mp4`, `studio/review/vento_r4_x_espontaneo.jpg`
- **Pedido:** "giros do vento mais espontâneos em vez de seguidos, vamos fazer como teste".
- **Mudança (só `LoboKit_Cliente.luau`):** chave `VENTO_ESPONTANEO = true`; `false` volta ao vento do r4.
  - Arcos curtos, cada um com centro ao longo do corpo, raio, inclinação, sentido, volta (140–320°), alongamento, subida, duração (0,55–1,15 s) e intervalo (0,1–0,45 s) sorteados.
  - Aparecem e somem suavemente.
  - **Uivo:** substituem a órbita e as rajadas em sequência; ficam mais densos na nota do uivo e somem no fim do bônus.
  - **Salto normal:** substituem os rastros retos. O encadeado mantém a hélice (sinal próprio).
  - **Investida:** substituem as faixas rentes; acompanham a velocidade.
  - No celular, metade da densidade (não testado).
- **Studio:** instalado e conferido por checksum (31725 bytes). Backup do r4 em `ServerStorage.Backup_KitLobo_efeitos_r3_2026-11-17.LoboKit_Cliente_aura_r4`.
- **Play (PC, dia):** Uivo, Salto curto/longo/encadeado e Investida, sem erro. Os giros saem soltos e irregulares, mas ficam mais esparsos que no r4. Um arco muito inclinado pode aparecer como um traço reto.
- **Sem teste:** noite, várias cópias e celular.
- **r2 (18/11, usuário escolheu "Espontâneo, mais denso"; place salvo v34):**
  - Cerca de 3x mais giros: intervalo de 0,06–0,26 s; densidade Uivo 1,6 (3,0 na nota), Salto 3,2, Investida 3,6.
  - Inclinação reduzida para ±18°/±12°, porque arcos de lado viravam traços retos.
  - **Instalado:** conferido por checksum (31826 bytes). Backup do r1 em `ServerStorage.Backup_KitLobo_efeitos_r3_2026-11-17.LoboKit_Cliente_espontaneo_r1`.
  - **Play (dia):** Uivo e Salto bem mais densos e sem traço reto; Investida (0,74 s) com pouca diferença. Custo: no máximo 23 faixas e luzes ativas, cerca de 0,02 ms por quadro.
  - **Evidências:** `studio/review/Lobo_Studio_Vento_espontaneo_r2.mp4`, `vento_espontaneo_r1_x_r2.jpg`.
  - **Sem teste:** noite, várias cópias e celular.

## 6aw. Auditoria de compatibilidade com o mundo + ensaios controlados (18/11/2026; Testes-loboancestral; nada foi alterado no place; aguardando avaliação) → `DOCS/criaturas/lobo-ancestral-compatibilidade.md`
- **Atualizações:** r5 alcance até a superfície (v35), r6 proteções (v36), r7 ataque andando (v37), **r8 contrato de criatura + duelo Lobo × Lobo (v38; §12 do relatório; Nucleo compartilhado não alterado, proposta pendente)**.
- **Leituras:** auditoria somente leitura das outras criaturas (o que existe de fato), dos sistemas de combate de `src/`, da v6.2 e dos .docx oficiais de 30/10.
- **Conflito registrado sem alterar:** elemento único oficial × Natureza+Ar na v6.2 (o elemento do Lobo está PENDENTE no oficial).
- **Nenhuma criatura real no place:** ensaios em Play com alvos temporários ágil, tank e colossal, criados e removidos só no Play. Scripts do Lobo inalterados (checksum).
- **Principais falhas medidas:**
  - alcance da Mordida/Garra, raio de acerto do Salto e Instinto medidos ao **centro** do alvo: Mordida e Garra 0 no colossal, Garra 0 no tank; Salto pousa dentro do corpo (7 studs no colossal); colossal com a superfície a 70 fica fora do Instinto;
  - kit isolado do `N.ferir`, de PvP e zonas seguras, da Vida@ dos dragões/guardiões e das IAs do jogo.
- **Funcionaram:** Investida nos três portes (para na superfície), parede (Salto recusado, Investida para), Uivo, Caçador Noturno, marca da presa, cancelamentos e a IA guardiã (reage aos três portes; atrás da parede, nenhuma reação).
- **Balanceamento (não é bug):** Lobo cai em 23 golpes do tank e 10 do colossal de ensaio; cerca de 19 min para derrotar um colossal de 6000.
- **Evidências:** `studio/review/Lobo_Compatibilidade_ensaios.mp4`, `compat_ensaios_prancha.jpg`, `compat_lobo_referencia_x_studio.jpg`.
- **Menor próximo passo:** alcance e contato até a superfície, só no kit do Lobo, e repetir a bateria.
- **r5 feito (18/11, place v35):** alcance, pouso do Salto, Instinto e IA medidos até a superfície; detalhes no §8 de `lobo-ancestral-compatibilidade.md`.

## 7. Próximos passos sugeridos (atualizado em 10/11/2026; aguardam aprovação)
- **Estado real:** a base é o rig18/clipes26/export26 (58 ossos, pálpebras), com dormir v26, montaria M1–M4 e GLB da sela aprovados no Blender. A antiga V5 e o modelo Motor6D de 26/10 estão superados.
1. **(15/11) Avaliar o import e o protótipo do kit no Testes-loboancestral (§6am)**: aparência no Studio, números [PROPOSTA], efeitos.
2. **Studio:** montaria funcional do lobo, sons, iluminação de bioma, teste em celular e multiplayer (cada um só com autorização).
3. **Depois:** sons próprios, IA do lobo selvagem e integração no place principal (só combinando com o usuário).

## 6ax. IA estratégica (protótipo, 19/11/2026; Testes-loboancestral v47; aguardando avaliação) → `DOCS/criaturas/lobo-ancestral-ia.md`
- Módulo `studio/kit/LoboIA.luau`: percepção/ameaça → plano (Calmo, Alerta, Investigar, Perseguir, Pressionar, Flanquear, Esquivar, Recuar, Recuperar, Desistir) → locomoção pelos clipes → execução pelas mesmas ações do jogador. Ensaios 1–9 com réplicas (sem criatura real); números [A TESTAR].
- 19/11: duelo mais móvel + esquiva visível (place v55) → seção "Duelo mais móvel + esquiva visível" em `DOCS/criaturas/lobo-ancestral-ia.md`.
- 19/11: refino de ritmo/posicionamento r6 (place v64) → seção "Refino de ritmo e posicionamento" em `DOCS/criaturas/lobo-ancestral-ia.md`.
- 19/11: correção de precisão/posição r7 (place v66) → seção "Correção de precisão e posição: r7" em `DOCS/criaturas/lobo-ancestral-ia.md`.
- 19/11: golpes por porte, queda e decisão de finalizar (place v75) → seção "Golpes por porte, queda e decisão de finalizar" em `DOCS/criaturas/lobo-ancestral-ia.md`; contrato e plano de adoção em `BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/kit/CONTRATO-CONTROLE-PORTE.md`.
- 20/11: hitbox de contato + finalização do Lobo (puxar, morder, estrangular), place v81 → seção "Hitbox de contato e finalização própria do Lobo" em `DOCS/criaturas/lobo-ancestral-ia.md`.
- 20/11: finalização corrigida — mordida no flanco/barriga com clipe próprio `Hab_MordidaFlanco` (place v91) → seção "Finalização corrigida: mordida no flanco" em `DOCS/criaturas/lobo-ancestral-ia.md`.
- 20/11: queda lateral — o derrubado tomba de lado (clipes próprios QuedaLado/CaidoLado/LevantarLado E/D e Hab_MordidaFlancoLado; place v99, aguardando avaliação) → seção "Queda lateral para a finalização" em `DOCS/criaturas/lobo-ancestral-ia.md`.
