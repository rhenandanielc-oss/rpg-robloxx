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
- **[OFICIAL — 30/10/2026]** Cada criatura tem **um único elemento natural**. Não há 2º/3º elemento, alternância nem fusão elemental no sistema atual.
- **[PENDENTE]** O elemento único do Lobo Ancestral **ainda não foi escolhido**.
  - A lista antiga "Natureza, Terra, Ar" (§2 e §5) é histórico. Ela não indica a escolha final.
  - Não presumir nenhum dos três.

### Habilidades
- **[OFICIAL — 30/10/2026]** Cada criatura tem no mínimo **1 passiva + 3 ativas**. Nomes, efeitos e quantidades são aprovados criatura por criatura.
- **Lista histórica da espécie-base Lobo** (§5, compartilhada com o Ártico). Vale como referência anterior; a lista final do Ancestral está **[PENDENTE]**:
  1. **Salto Predatório**: seleciona um alvo.
  2. **Uivo**: fortalece temporariamente o próprio Lobo.
  3. **Investida**: segue a direção escolhida.
  4. **Instinto de Caça**: rastreia inimigos. Na exploração, encontra pistas de ninhos por odor, pegadas e sinais, **sem revelar coordenadas**.
- **[OFICIAL]** Habilidades ofensivas rápidas, com recargas relativamente baixas. Os números estão pendentes.
- **Passiva:** nenhuma definida. **[PENDENTE]**
- **[PROPOSTA — histórico, superada]** As versões por elemento (§6) e as fusões direcionais (§7) contrariam a regra de elemento único. Não implementar.

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

## 7. Próximos passos sugeridos (aguardam aprovação)
1. **Revisar a V5** com uma prancha lado a lado com o painel 01 (só leitura e renders) e listar as correções.
2. **Decidir a base para o Roblox:** importar a V5 com pele deformável no lugar do modelo Motor6D rígido de 26/10. Fazer o teste num place vazio local, sem tocar no mapa.
3. **Pedir ao criador** o elemento único e o kit (passiva + ativas) antes de qualquer VFX ou combate.
4. **Só depois:** clipes refinados, sons, IA e montaria. Um sistema por vez.
