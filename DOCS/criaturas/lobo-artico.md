# Lobo Ártico — ficha do subchat

Criatura **domesticável** da **Tundra Congelada**. Espécie-base **Lobo**, que tem duas formas regionais: Lobo Ártico (este subchat) e Lobo Ancestral (Floresta Ancestral, subchat próprio, ficha em `DOCS/criaturas/lobo-ancestral.md`).

Fontes: `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO` (§0 tabela de formas, §1, §5–7, §10, §11, §14–15) e `RPG_01` (só cita o Lobo no catálogo). A **ATUALIZAÇÃO OFICIAL de 30/10/2026** prevalece sobre o que vem depois no documento.

Regras de convivência: `DOCS/ORGANIZACAO-CHATS.md`. Studio um chat por vez (`DOCS/estado/studio-em-uso.md`).

Ficha criada em 03/11/2026, só com leitura. Nada foi alterado no Studio nem em `src/`.

## 1. Identidade

| Item | Valor | Status |
|---|---|---|
| Bioma | Tundra Congelada | [OFICIAL] |
| Locomoção | Terrestre; **perseguição em neve e gelo** (melhor locomoção em neve/gelo) | [OFICIAL] |
| Papel | Velocidade, esquiva e perseguição (comum à espécie Lobo) | [OFICIAL] |
| Fraqueza | Menos vida e defesa que as criaturas grandes | [OFICIAL] |
| Corpo | **Mais robusto** que o Ancestral | [OFICIAL] |
| Porte adulto | 5,5–7 studs até os ombros | [OFICIAL] |
| Estágios | Ovo + 5 modelos (Bebê, Jovem, Pré-adulto, Adulto, Ancião) | [OFICIAL] |
| Animações | Naturais; filhotes com animações próprias e brincalhonas | [OFICIAL] |
| Ambiente | Pegadas em neve, respingos e reação da vegetação | [OFICIAL] |
| Montaria | A partir do **Adulto**, com **sela leve** | [OFICIAL] |
| Ataque básico | Sequência de mordidas e garras, com animações variadas (fora dos slots de habilidade) | [OFICIAL] |
| Padrões visuais | **Branco Polar**, **Cinza da Geada**, **Prateado Boreal** (Etapa 23). Só cosméticos: não definem elemento nem raridade | [OFICIAL] |
| Cores exatas de cada padrão | Não confirmadas | [PENDENTE] |
| Evolução estética por estágio e adornos por raridade | — | [PENDENTE] |
| Painel de referência | `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/01-lobos-urso-leao.png`, **painel 02** ("robusto · poderoso · resiliente · terras nevadas"): pelagem branca/cinza longa e espessa, juba volumosa no pescoço, olhos azul-gelo, patas largas de neve, corpo horizontal e maciço, paleta cinza-azulada a branco | referência visual |

## 2. Elemento e habilidades

> **Consolidação de 18/11/2026 (§8.72; aprovada pelo usuário em 19/11).** Vale sobre o texto histórico abaixo:
> - **Elemento:** **Gelo e Ar**, decisão do usuário de 16/11 (`REFERENCIAS_PODERES_E_EFEITOS.md` §0). Ela supera, para os lobos, a regra de "elemento único" de 30/10. Se essa regra também cai para as outras criaturas: [A CONFIRMAR].
> - **Kit final [PROPOSTA][A TESTAR]:** 3 ativas e 2 passivas (§3 do documento). Todas estão implementadas e testadas no Teste-animacoes:
>   - **Ativas:** Cometa Glacial (slot 1), Uivo Boreal (slot 2) e Avalanche (slot 3).
>   - **Passivas:** Instinto Boreal e Pelagem Polar.
>   - **Ataque básico:** só mordidas, inclusive andando ou correndo.
> - **Números:** são os do documento, com uma exceção pedida pelo usuário: o Cometa tem alcance de 60 e segue o alvo (r7, 17/11). Os demais valores (velocidade, altura, cone) estão marcados [ENSAIO] no `Kit_Servidor`.
> - **Idades [PROPOSTA][A TESTAR]:** multiplicadores de `ESTATISTICAS_POR_IDADE.md` no `Idade_Servidor`.
>   - Por enquanto o modelo Adulto é usado em escala para todas as idades.
>   - Modelos próprios por idade e o ovo: [PENDENTE].

### Elemento
- **[OFICIAL — 30/10/2026]** Cada criatura tem **um único elemento natural**. Não há 2º/3º elemento, alternância nem fusão elemental no sistema atual.
- **[PENDENTE]** O elemento único do Lobo Ártico **ainda não foi escolhido**.
  - A lista antiga "Gelo, Ar, Água" (§0 e §5) é histórico. Não indica a escolha final.
  - Não presumir Gelo só porque o Dragão Glacial é Gelo.

### Habilidades
- **[OFICIAL — 30/10/2026]** No mínimo **1 passiva + 3 ativas**. Nomes, efeitos e quantidades são aprovados criatura por criatura.
- **Lista histórica da espécie-base Lobo** (§5, compartilhada com o Ancestral). Referência anterior; a lista final do Ártico está **[PENDENTE]**:
  1. **Salto Predatório**: seleciona um alvo.
  2. **Uivo**: fortalece temporariamente o próprio Lobo.
  3. **Investida**: segue a direção escolhida.
  4. **Instinto de Caça**: rastreia inimigos; na exploração, encontra pistas de ninhos por odor, pegadas e sinais, **sem revelar coordenadas**.
- **[OFICIAL]** Habilidades ofensivas rápidas, recargas relativamente baixas. Números pendentes.
- **Passiva:** nenhuma definida. **[PENDENTE]**
- **[PROPOSTA — histórico, superada]** Versões por elemento (§6: Gelo = cristais/zona escorregadia, trilha congelada etc.) e fusões direcionais do Ártico (§7: Gelo+Água, Gelo+Ar, Água+Ar…) contrariam a regra de elemento único. Não implementar; podem servir só de inspiração se o criador pedir.

## 3. Atributos (Etapa 24)
- **[OFICIAL — 24.1]** 6 atributos: Vida, Defesa, Força, Velocidade, Energia e Poder Elemental. Comparação entre Adultos nível 100. Vantagem ambiental de 10–15%; raridade influencia 1–5%.
- **[PROPOSTA — 24.2, NÃO APROVADA]** Números do Lobo Ártico:
  - escala 1–5: Vida 2, Defesa 2, Força 3, Velocidade 4, Energia 4, Poder Elemental 2;
  - valores absolutos: 3.250 HP, Defesa 95, Força 145, Energia 135, Poder Elemental 110;
  - velocidade: terra 35 studs/s (manobra 4), água 14 studs/s (manobra 3), sem voo.
  - (Comparado ao Ancestral: um pouco mais de vida/defesa, um pouco menos veloz em terra, melhor na água — coerente com "mais robusto".)

## 4. Mundo e habitat (segundo os registros do mapa; não conferido nesta sessão)
- `DOCS/estado/mundo-tundra.md` (M5/M5.1, 23/10) e `DOCS/ECOLOGIA-FAUNA.md`:
  - `workspace.Tundra_Congelada.Habitats.Ecologia_Fauna.Lobo_Artico`: **3 alcateias só em baixa altitude** — `Alcateia_Floresta` → `Toca_Lobos_Cume_Sul` (entrada (−1290,93,−3900), 16×12, 2 câmaras: descanso e filhotes); `Alcateia_Macico` → Gruta do Gelo Azul; `Alcateia_Campos` → `Toca_Lobos_Desfiladeiro` (entrada (3190,86,−5028), 14×12, 2 câmaras).
  - Cada alcateia tem `Toca`, `Zonas_Caca`, `Rotas_Patrulha`, `Arena_Toca`. Trilhas `R_TOCA_*` em `_TundraTrilhasJ`; caminhadas reais e pathfinding OK nos testes de 23/10.
  - `Interacoes_Ecologicas` inclui cenas de patrulha de lobos, perseguição na neve e alcateia na toca.
  - Tudo são **marcadores**: não há lógica de lobos, ovos nem criação.
  - O registro M5.1 chama as tocas de "Lobos Glaciais" — é o mesmo Lobo Ártico (nome oficial: **Lobo Ártico**).
- **[OFICIAL]** Ninhos reaparecem em 30–60 min. Quantidade de ninhos por jogador ainda é [PROPOSTA].
- **[PENDENTE]** Tamanho da alcateia (o RPG_02 não define). Lore do nascimento de mamíferos por ovos.
- Convivência com o **Dragão Glacial** (só no alto, covis em penhascos) e com a fauna de recurso da Tundra (Lebre Ártica, Cabra-das-Neves, Mariposa Glacial) — esta última é do subchat de fauna, não deste.

## 5. O que já existe

### Roblox Studio (segundo os registros de 26/10; não conferido nesta sessão)
- `ServerStorage.Biblioteca_Criaturas.Modelos` → **Lobo Ártico** feito no próprio Studio:
  - 6,6 de ombro;
  - rig Motor6D com segmentos rígidos, **sem pele deformável**;
  - 13 animações (KeyframeSequence);
  - 3 padrões por tingimento;
  - `Estado` = Testes aprovados (Play/PC). 12 lobos animados sem queda de FPS mensurável.
- `Biblioteca_Criaturas.Catalogo` registra a forma com as 4 habilidades históricas (e provavelmente a lista antiga de elementos — conferir antes de usar).
- **Atenção:** o PILOTO de 27/10 registrou que o Studio abriu uma versão antiga do place (PlaceVersion 394), sem `Biblioteca_Criaturas`. Backup: `Documents/RPG_Roblox/BACKUPS/RPG_BKP_2026-10-26_C1_criaturas.rbxl`. Conferir qual place está aberto antes de qualquer trabalho.

### Blender (`BLENDER/Criaturas/Blockouts/`)
- **Scripts** em `build/`:
  - `lobo_artico.py` (27/10): script próprio; **importa a técnica do `lobo_v5`** do Ancestral sem alterá-lo (fator de pelo 1,4, pelo nas orelhas, sem calombo na mandíbula);
  - `build_Lobo_Artico.py` (blockout V2), `lobo_base.py` (base canina compartilhada com Ancestral e Cérbero), `pipeline_final.py` (flag `LOBO`), `esqueletos.py`.
  - **Dependência:** qualquer mudança em `lobo_v5.py`/`lobo_base.py` afeta também o Ancestral (e o Cérbero) → combinar com o subchat do Lobo Ancestral e o usuário.
- **Arquivos** em `Lobo_Artico/`: `_blockout`, `_refinado`, `_final` e `_refinado_v5`, `_final_v5` `.blend`.
- **Exports** em `_Export/`: `Lobo_Artico.glb` (V2, 1,7 MB) e `Lobo_Artico_v5.glb` (5,2 MB, 27/10).
- **Estado da V5 (cartões de pelo com alpha, técnica aprovada pelo usuário):**
  - massas 8–12% maiores que no Ancestral; patas de neve largas; pelagem branca e cinza ~30% mais longa e ~8% mais densa, sem vegetação; olhos azul-gelo;
  - 42 ossos (inclui 10 `Pelo_*` de balanço), 28 animações;
  - ~32,5 mil tris na versão com cartões (registro anterior com geometria opaca chegou a 55–73 mil);
  - auditoria 7 / 12 / 9;
  - **anatomia não aprovada como final.**
- **Diferenças abertas frente ao painel 02** (registros de 27/10): referência mais horizontal, maciça e comprida, cabeça mais baixa e juba mais volumosa; pelos do rosto espetados; mecha longa saindo da nuca (corrigida? não confirmado); custo alto (precisa de LOD).
- **Auditoria de animações V2** (`AUDITORIA-ANIMACOES-V2.csv`, 28 clipes): Aprovadas 4 (Repouso, ReacaoGolpe, AtaqueBasico, MontadoRepouso); **Refazer 9** (Corrida, Arrancada, DeitarDescanso, Descanso, LevantarDescanso, MontadoCorrida, GuardarNinho, SaltoPredatorio, Investida); demais com pequenos ajustes. Auditoria só numérica.
- **Roblox:** **nenhuma versão GLB foi importada nem testada.** Importação manual (Import 3D), ver `PILOTO-ROBLOX-LOBO.md`.
- `review/Lobo_Artico/Prancha_Lobo_Artico_v5.png` é citado nos registros, mas a pasta **não existe** no repositório nesta inspeção (`review/` só tem pastas de rugidos/boca de fogo).

### Código (`src/`)
- Nada específico do lobo: sem IA, combate, montaria nem sons. A IA, sons e montaria existentes são dos dragões e são arquivos compartilhados (`Cerebro`, `EstadosDragao`, `ConfigCombate`, `SonsConfig`…).

## 6. Pendências
1. **Decisões do criador:**
   - elemento único;
   - lista final de passivas e ativas e seus efeitos;
   - números (24.2 é só proposta);
   - cores dos 3 padrões (Branco Polar, Cinza da Geada, Prateado Boreal);
   - tamanho da alcateia.
2. **Modelo:**
   - aprovar ou ajustar a V5 frente ao painel 02 (mais horizontal/maciço, juba volumosa, cabeça baixa, rosto menos espetado);
   - LOD antes de uso em alcateia.
3. **Estágios:** só existe o Adulto. Faltam Bebê, Jovem, Pré-adulto, Ancião e ovo.
4. **Roblox:**
   - importar a V5 (Import 3D manual) num place de teste;
   - conferir SurfaceAppearance com AlphaMode Transparency, DoubleSided, ordenação e FPS (PC e celular);
   - testar escala, pés no chão, animações;
   - publicar animações exige a conta do usuário.
5. **Animações:** refazer os 9 clipes marcados; seguir `padrao-movimento-criaturas` (fluidez); locomoção própria em neve/gelo (passada larga, patas afundando, pegadas).
6. **Sistemas (não iniciados):** IA selvagem e alcateia; companheiro domesticado; montaria com sela leve; sons (uivo, rosnado, passos em neve); VFX; tudo com validação no servidor.

## 7. Próximos passos sugeridos (aguardam aprovação)
1. **Revisar a V5** com uma prancha lado a lado com o painel 02 (só leitura e renders no Blender) e listar as correções de anatomia.
2. **Pedir ao criador** o elemento único e o kit (passiva + ativas) antes de qualquer VFX ou combate.
3. **Combinar com o subchat do Lobo Ancestral** como dividir `lobo_v5.py`/`lobo_base.py` (base compartilhada) antes de mexer neles.
4. **Teste de importação** da V5 num place vazio local, sem tocar no mapa, com o Studio reservado em `studio-em-uso.md`.
5. **Só depois:** clipes refinados, sons, IA e montaria. Um sistema por vez.

> Os itens 1, 3 e 4 acima ficaram superados em 03/11: o usuário pediu um Lobo Ártico **novo, do zero**, a partir de uma referência nova (seção 8). Os protótipos antigos (V2/V5) foram preservados e não são a base.

## 8. Lobo Ártico Ref — modelo novo (03/11/2026, aguardando aprovação do modelo)

**Pedido:** criar do zero, com a imagem nova como referência principal (prevalece sobre o painel 02). Primeira entrega: só o modelo no Blender. Rig, animações e importação no Roblox ficam para depois da aprovação.

**Referência:** `REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png` (1672×941), com cópia em `BLENDER/Criaturas/Lobo_Artico_Ref/ref/`.

**Pasta:** `BLENDER/Criaturas/Lobo_Artico_Ref/`. Não importa nem usa nenhum script, malha, rig, material ou animação dos protótipos antigos (`Blockouts/lobo_*.py`).

| Arquivo | Função |
|---|---|
| `asset-brief.md` | proporções, peças, materiais, áreas inferidas, adaptações |
| `texturas_lobo.py` | atlas de mechas 1024 RGBA (4 tufos) e máscara da marca (system python + PIL) |
| `criar_lobo_artico.py` | HIGH em pose neutra: grafo de nós → metaballs elipsoidais → voxel → massas musculares → relevo de mechas por campo de fluxo → rosto; orelhas, olhos, garras, cristais e cartões de mechas |
| `low_lobo_artico.py` | LOW: 3 MeshParts, UV, bake 2048 → finais 1024, LOD1/LOD2, GLB, `custo_lobo_artico.json` |
| `verificar_glb.py` | reimporta o GLB e confere malhas, tris, materiais, imagens, cernelha e pés no chão |
| `render_lobo.py` / `prancha.py` | vistas sob luz neutra e pranchas lado a lado com a referência |

**Resultado no Blender (rodada r11):**
- Porte: cernelha a **6,74 studs** com o pelo, dentro do oficial de 5,5–7. Comprimento do focinho à ponta da cauda: 13,3.
- HIGH: corpo com 269 mil tris; pelagem com 3.109 cartões (17,4 mil tris).
- Identidade preservada: corpo robusto e alongado, peito fundo, juba com babador, focinho com nariz escuro, olhos azul-gelo, orelhas com pelo, patas largas digitígradas, cauda longa e cheia, 6 cristais translúcidos no alto do dorso e marca ciano em espiral no ombro **esquerdo**.

**Export validado por reimportação** (`low/*_verificacao.json`):

| LOD | Corpo | Pelagem | Cristais | Total |
|---|---|---|---|---|
| LOD0 `CR_LoboArtico_LOW.glb` | 10.802 | 17.408 | 204 | 28.414 |
| LOD1 `CR_LoboArtico_LOD1.glb` | 4.500 | 8.946 (só mechas longas) | 204 | 13.650 |
| LOD2 `CR_LoboArtico_LOD2.glb` | 1.784 | — | 204 | 1.988 |

- **Texturas:** `cor`, `normal`, `rugosidade` e `emissao` do corpo em 1024 (bake intermediário 2048 em `low/bake2048/`), mais o atlas de mechas 1024 RGBA. São 3 materiais, um por MeshPart.
- **Pés no chão:** z mínimo −0,04 (pata levemente abaixo de 0). Será ajustado no rig.
- **Avisos:**
  - o exportador marcou a malha do LOD2 como "não válida" (decimação); precisa revisar antes de usar;
  - os cristais exportam sem UV (cor e transparência só pelo material).

**Estratégia de LOD [PROPOSTA, não medida no Roblox]:**
- LOD0 até cerca de 40 studs, no máximo 1–2 lobos por vez no celular.
- LOD1 de 40 a 120 studs.
- LOD2 de 120 a 300 studs; acima disso, oculto ou com o `LOD_Distancia` do projeto.
- Exemplo: uma alcateia de 4 com 1 em LOD0 e 3 em LOD1 soma cerca de 69 mil tris.
- O custo principal no celular deve ser o **overdraw** dos cartões com alpha, e não os tris. Isso precisa ser medido no Studio, no emulador **e** num celular real.

**Decisões sobre áreas ocultas [PROPOSTA]:**
- Lado direito sem marca (não se inventa simetria).
- Cristais na linha do dorso, com 1 cristal pequeno à direita.
- 4 dedos por pata.
- Peito, traseira e parte de baixo da cauda pela anatomia de lobo.

**Adaptações:**
- Cristais espaçados e só no trecho torácico, para pescoço e lombo dobrarem.
- Nenhuma mecha nasce sobre a marca nem perto dos cristais.
- A marca está na textura (emissão), não em geometria.
- O vapor da respiração e o cenário ficaram fora.

**Diferenças restantes frente à referência:**
- **Cabeça:** menor e mais "raposa"; o crânio ainda arredondado; os olhos sem o formato amendoado e com contorno largo.
- **Juba e pelagem:** juba menos volumosa e menos clara; pernas pouco peludas.
- **Cristais:** mais simples, sem a lapidação interna.
- **Marca:** sem as folhas de gelo e sem o pelo cristalizado em volta.

**Não testado no Roblox** (este pedido não autorizou o Studio).

### 8.1 Alternativa Meshy (03/11/2026, autorizada pelo usuário: "pode criar no meshy, se for melhor")
- **Geração:** 1 tarefa image-to-3D (`meshy_lobo_img3d.py`, meshy-7.1, PBR 4K) a partir de um recorte da referência (`ref/lobo-artico-recorte.png`).
  - Tarefa `01a1a2b9-bb11-712f-966e-9bb045df0a14`, SUCCEEDED, **30 créditos**.
  - O saldo foi de 590 para 524. A diferença de 36 é atribuída a outros chats que usavam o Meshy ao mesmo tempo (não verificado).
- **Arquivos:** `meshy/CR_LoboArtico_meshy.glb` e `.fbx`, com texturas 4K em `meshy/tex_*.png`. A versão normalizada (`normalizar_meshy.py`: 1 u = 1 stud, frente −Y, cernelha 6,6) está em `meshy/CR_LoboArtico_meshy_norm.blend`.
- **Malha bruta:** 6,17 milhões de tris, 1 material.
- **Renders e pranchas:** `review/m01_meshy/`, `review/comparar_proprio_x_meshy.png` e `review/comparar_rosto_proprio_x_meshy.png`.
- **Pontos melhores que o modelo próprio:** cabeça e rosto (focinho, olhos amendoados azul-gelo, orelhas com pelo), volume da juba, mechas da cauda, patas e silhueta geral.
- **Problemas do Meshy:**
  - **cabeça virada** para a câmera, como na referência: não está em pose neutra; precisa ser endireitada antes do rig;
  - cristais viraram **placas de "folha"** opacas ao longo do dorso, em vez de cristais translúcidos;
  - a **marca foi repetida no lado direito** e é só relevo, sem brilho;
  - de perto, o pelo lembra penas ou espinhos;
  - a pata dianteira esquerda está um pouco à frente.
- **Caminho proposto (híbrido, aguarda aprovação):**
  1. Endireitar a cabeça e o pescoço com rotação suavizada por peso (pose neutra).
  2. Reduzir para LOW de no máximo 20 mil tris e assar a cor e a normal do Meshy em 1024.
  3. Trocar as placas do dorso pelos cristais translúcidos próprios (MeshPart separada).
  4. Projetar a marca emissiva própria só no ombro esquerdo, ou manter as duas marcas se o usuário preferir.
  5. Opcional: cartões de mechas só nas bordas da silhueta para suavizar o aspecto de penas.

### 8.2 Base escolhida: Meshy híbrido (03/11/2026, decisão do usuário: "o mais fiel possível... sem afetar as animações")
- **Pose neutra** (`meshy_neutro.py`; arquivo `meshy/CR_LoboArtico_meshy_neutro.blend`):
  - tronco alinhado a Y pelo eixo entre as patas dianteiras e as traseiras (corrigidos 12,9°);
  - cabeça e pescoço girados com peso suave a partir da base do pescoço (corrigidos 39,1°, focinho para −Y);
  - cauda centralizada (deslocamento de 1,22 stud a partir da raiz);
  - o resto do corpo não se move; não apareceram rasgos nos renders.
- **Malha de jogo** (`low_meshy.py`, saída em `low_meshy/`):
  - remesh voxel de 0,035, que dá malha fechada e densidade uniforme (boa para deformar);
  - decimação e limpeza: as arestas não-manifold caíram de 667 para 3;
  - UV única; bake 2048 → finais 1024 (cor, normal, rugosidade, emissão).
- **Marca:** brilho **só no ombro esquerdo**. A máscara vem do ciano da própria textura do Meshy, restrita a uma caixa achada pelas amostras do lado +X (x 0,44–1,97; y −3,70 a −0,83; z 4,28–5,99). A marca em relevo do lado direito ficou **sem brilho** [PROPOSTA; decisão do usuário].
- **Cristais:** 6 translucidos próprios (MeshPart separada, 276 tris), presos ao dorso por raio. As placas do Meshy ficaram como "pelo gelado".
- **Export validado por reimportação** (`low_meshy/*_verificacao.json`):

| LOD | Corpo | Cristais | Total |
|---|---|---|---|
| LOD0 `CR_LoboArtico_LOW.glb` | 18.716 | 276 | 18.992 |
| LOD1 `CR_LoboArtico_LOD1.glb` | 6.818 | 276 | 7.094 |
| LOD2 `CR_LoboArtico_LOD2.glb` | 2.318 | 276 | 2.594 |

- **Medidas:** 4 texturas de 1024; pés com z mínimo −0,002. A escala foi normalizada pela cernelha em 6,6, mas a crista da juba logo acima do ombro chega a **7,05**. É um único fator de escala, ajustável antes do rig se o limite de 7 valer para o topo do pelo.
- **Pendências do modelo antes do rig:**
  - **Boca fechada e sem interior:** para morder, uivar e rosnar é preciso separar o lábio inferior e criar gengiva, dentes e língua.
  - **Olhos só na textura:** sem pálpebras, não há piscar.
  - **Detalhe de perto:** o LOW fica facetado e a textura perde nitidez no rosto (UV fragmentada numa só textura 1024).
    - Proposta: separar cabeça e corpo em 2 MeshParts com texturas próprias, o que dobra a densidade de texels.
  - **Aviso "malha não válida" do exportador:** ainda aparece; a reimportação está correta, mas falta investigar.
  - **Pata dianteira esquerda:** um pouco à frente; pode ser corrigida no rig.
- **Não testado no Roblox.**

### 8.3 Refino para o rig (03/11/2026, autorizado: "Sim, refinar")
Scripts:
- `rosto_meshy.py`: mede nariz, olhos (íris ciano) e linha da boca (traço escuro) e grava `meshy/rosto.json`.
- `refinar_meshy.py`: saída em `low_ref/`.
- `teste_boca_olhos.py`: teste visual **sem rig**.

**Cabeça e corpo em 2 MeshParts:**
- A malha única é cortada num plano escondido na juba. As duas peças dividem os mesmos vértices da costura.
- A cabeça recebe mais densidade e **texturas 1024 próprias**: o rosto ficou visivelmente mais nítido (`review/m11_ref/comparar_rosto.png`).
- A faixa u, v > 0,9 da textura da cabeça é reservada para as cores da boca e das pálpebras.

**Boca:**
- Corte dos lábios no traço escuro do Meshy (z = 7,158 + 0,318·y), à frente do canto (y = −5,79): 22 arestas separadas, unidas no canto.
- Interior: cavidade (gengiva), língua e dentes (caninos, laterais e incisivos), criados só onde o ponto está comprovadamente dentro da cabeça.
- Os dentes são proporcionais à mandíbula do Meshy, que é fina: 0,10–0,25 stud.
- **Teste sem rig:** fechada, nada vaza (só a ponta de um canino aparece no lábio). Aberta 25°, mostra gengiva, dentes e língua sem rasgar.

**Pálpebras** (superior e inferior, nos dois olhos):
- Cascas modeladas fechadas sobre o olho e giradas até o repouso aberto: superior +80°, inferior −55°.
- Em repouso, ficam também **recuadas** 0,07 stud para dentro da cabeça.
- **Teste sem rig:** abertas, só um fio aparece sobre a íris; fechadas, cobrem o olho inteiro.

**Grupos de vértices** (base dos pesos do rig):
- `Palpebra_Sup_E/D`, `Palpebra_Inf_E/D`, `Boca_Superior`, `Boca_Inferior`.

**Pivôs para o rig:** `low_ref/rig_pivos.json`.
- Mandíbula: pivô sugerido 0,55 stud atrás do canto, na altura dos lábios.
- Olhos: centro do globo, eixo de giro, ângulos e vetores de recuo.
- Costura entre cabeça e corpo.

**Export validado por reimportação** (`low_ref/*_verificacao.json`):

| LOD | Cabeça | Corpo | Cristais | Total |
|---|---|---|---|---|
| LOD0 `CR_LoboArtico_LOW.glb` | 11.760 | 19.820 | 276 | 31.856 |
| LOD1 `CR_LoboArtico_LOD1.glb` | 3.444 | 6.329 | 276 | 10.049 |
| LOD2 `CR_LoboArtico_LOD2.glb` | 944 | 1.829 | 276 | 3.049 |

- 8 texturas 1024 (cabeça e corpo: cor, normal, rugosidade, emissão), assadas em 2048.

**Pendências:**
- **Pálpebras fechadas:** parecem cascas lisas com uma faixa cinza; aceitável num piscar rápido, mas pode melhorar.
- **Bake:** ficaram alguns pontos pretos nas pontas do pelo da juba (raios que não acharam o HIGH); corrigir antes de exportar a versão final.
- **Altura:** a juba ainda chega a 7,05 acima do ombro (ajuste de escala, se necessário).
- **Simetria do rosto:** a cabeça do Meshy não é perfeitamente simétrica (olhos um pouco diferentes).
- **Não testado no Roblox.**

### 8.4 Complemento v2: rodada 1, olhos, pálpebras e boca (03/11/2026)
Pedido: correção do modelo m11 antes do rig (rosto, pelagem, adornos, malha). As rodadas são pequenas, cada uma apresentada antes da seguinte.

**M0:** não havia versões posteriores à m11. O Studio estava reservado pelo Dragão Sombrio e não foi usado.

**Scripts:**
- `rosto_v2.py`: parte de `low_ref/` (m11, preservada) e salva em `low_v2/`, com texturas copiadas.
- `teste_rosto_v2.py`: teste geométrico **sem rig**. Aplica os pesos dos grupos numa cópia em memória; **não é animação validada**.

**Mudanças:**
- **Olhos:**
  - fenda amendoada (0,211 × 0,099, canto externo 12° mais alto) recortada na pele, que foi refinada em volta;
  - globo em calota no formato da amêndoa, com raio ajustado à pele da margem (0,186 e 0,185);
  - íris azul-gelo pintada numa amostra própria (pupila, raios, anel escuro), com UV plana, igual nos dois olhos;
  - posições dos olhos simetrizadas pela média dos dois lados.
- **Pálpebras:**
  - são a própria pele da margem (as cascas da m11 foram removidas), com 140 e 84 vértices de margem;
  - os pesos vêm do ângulo real de cada vértice até a linha de encontro;
  - a de cima passa 1,5° da linha e fica 0,004 por fora da de baixo;
  - a tinta azul que o Meshy pôs fora da fenda foi repintada de pelo, e a borda da pálpebra é escura.
- **Boca:**
  - saco bucal soldado às bordas do corte: lábio enrolado escuro, gengiva, palato, assoalho e garganta recuada;
  - 18 dentes: incisivos, caninos curvos e pré-molares em lâmina;
  - língua com ponta e sulco;
  - vértices do interior que ficavam fora da pele foram trazidos para dentro.
- **Grupos:** `Palpebra_Sup/Inf_E/D` (pesos graduais), `Boca_Superior` e `Boca_Inferior`.
- **Pivôs:** `low_v2/rig_pivos.json`.

**Custo (export reimportado):**

| Peça | Tris |
|---|---|
| LOW_Cabeca | 14.498 |
| LOW_Corpo | 19.820 |
| LOW_Cristais | 276 |
| LOD1 (total) | 10.200 |
| LOD2 (total) | 3.203 |

**Evidências:**
- `review/v2_r8/grade_olhos.png` e `grade_boca.png`: repouso, meio e máximo × frente, perfil, 3/4 e por baixo.
- `review/v2_r8/prancha_rodada1_ref_m11_v2.png`: comparação com a referência e a m11.

**Pendências da rodada 1:**
- Borda da pálpebra serrilhada de perto (triângulos longos na margem).
- Pontinhos azuis nos cantos com o olho fechado.
- Olho mais redondo e aberto que o da referência.
- Bochecha atrás do canto da boca com triângulos grandes escuros na abertura máxima.
- Sulcos fortes em volta dos olhos vindos da normal do Meshy: ficam para a rodada de bake.

### 8.5 Complemento v3: rodada 2, pelagem, marca e cristais (03/11/2026)
**Scripts:**
- `pelagem_r2.py`: parte de `low_ref/` (m11, preservada) e salva em `low_ref2/`.
- Em seguida, `rosto_v2.py` (rodada 1) é reaplicado sobre `low_ref2/` e gera **`low_v3/`, a versão atual**.
- `marca_v3.py`: desenho da marca. Gera `tex/marca_mascara_v3.png`.

**HIGH (só para o bake):**
- pontas de mecha suavizadas (mais forte sobre a marca, para eliminar o "tubo");
- relevo de fios finos no mapa de normal;
- placas azuis do dorso viraram pelo gelado claro, para não competirem com os cristais;
- tinta ciano grossa da marca e manchas escuras do Meshy (fora do rosto e das garras) viraram pelo.

**LOW:**
- 9.277 vértices suavizados de leve (lascas), 2.434 vértices das pernas com mais volume (pés no chão intactos) e o relevo da marca achatado;
- novo bake 2048 → 1024 com as mesmas UVs, preenchendo pixels de falha.

**Peças novas:**

| Peça | Tris | Conteúdo |
|---|---|---|
| `LOW_Pelagem` | 3.548 | 887 cartões de mecha com alpha: pernas, franja da barriga, peito, juba lateral, flancos, cauda e bochechas |
| `LOW_Marca` | 1.352 | decalque no ombro esquerdo com textura própria 512: espiral, haste com folhas de gelo e gavinha, emissão 1,4 |
| `LOW_Cristais` | 340 | 4+1 cristais lapidados (7 faces) com UV e textura de veios 512 com alpha |

- **Opção B da marca direita:** existe só no `.blend` (`OPCAO_Marca_Direita`, oculta e **fora do export**). O padrão exportado é a **opção A**, sem marca à direita, e a escolha está [PENDENTE] com o usuário.

**Custo LOD0 (export reimportado):**

| Peça | Tris |
|---|---|
| Cabeça | 14.498 |
| Corpo | 19.820 |
| Pelagem | 3.548 |
| Marca | 1.352 |
| Cristais | 340 |
| **Total** | **39.558** |

- LOD1: 13.586 tris (cartões pela metade). LOD2: 3.436 tris (sem cartões e sem decalque).
- **Texturas:** 8 de 1024 (cabeça e corpo) + atlas de pelo 1024 + marca 512 + cristal 512 → cerca de 46 MB sem compressão na memória. A estimativa no Roblox depende da compressão do motor.

**Evidências:**
- `review/v3_r7/prancha_rodada2_ref_m11_v3.png`: ombro, cristais, câmera da referência e lado, comparando referência, m11 e v3.
- `review/v3_r7/marca_direita_opcoes_A_B.png`: as duas opções da marca direita.

**Pendências da rodada 2:**
- De perto, a pelagem ainda lê como lascas, porque é a geometria do Meshy no limite de 20 mil tris. Na distância de jogo melhorou.
- A marca ainda é menor e menos luminosa que a da referência.
- Resta um leve relevo circular no ombro direito.
- Os cartões com alpha precisam de teste real de ordenação e de overdraw no Roblox.

### 8.6 Complemento v4: rodada 3, malha, pose neutra e exports (03/11/2026). Versão atual: `low_v4/`
**Decisão do usuário:** a marca do lado direito fica **sem marca** (opção A). O objeto da opção B foi removido.

**Scripts:**
- `auditar_lobo.py`: auditoria só de leitura. Gera `review/v3_audit/` e `review/v4_audit/auditoria.json`.
- `ajuste_r3.py`: parte de `low_v3/` (preservada) e salva em `low_v4/`.

**Achados e correções:**

| Achado | Antes (v3) | Correção | Agora (v4) |
|---|---|---|---|
| Aviso de "malha inválida" | 565 arestas e 153 vértices soltos na cabeça (sobra do recorte dos olhos) | removidos | 0 soltos, 0 não-manifold na cabeça |
| Face degenerada na cabeça | 1 | removida | 0 |
| "Furos" no corpo e na cabeça | 168 + 30 triângulos minúsculos (≈0,00007 stud²) presos só pelos vértices, sobre superfície já fechada | removidos | corpo com 7 arestas não-manifold e 7 bordas pequenas restantes |
| Interior da boca | 22 arestas com enrolamento invertido | cada componente orientado para o eixo da boca | 8 (encontro de dentes e língua fechados com o saco bucal) |

- **Vértices duplicados:** os 21 da cabeça são o corte dos **lábios** (intencional), e não foram fundidos.
- **Costura cabeça-corpo:** 777 × 777 vértices, distância 0, antes e depois.
- **Pose neutra das patas:**
  - a traseira direita estava 1,17 stud à frente (y 0,88): girada 16,9° em torno do quadril, ficou em y 2,01 (a esquerda está em 2,11);
  - a dianteira esquerda estava aberta para fora (x 1,80): girada 7,9° em torno do ombro, ficou em x 1,24, simétrica à direita (−0,97) em torno do eixo do tronco (0,12);
  - os cartões de pelo acompanham; as UVs e texturas não mudam; as quatro patas apoiam em z ≈ 0 (de −0,01 a 0,0).
- **Medidas (`auditoria.json`):**
  - topo do **pelo na cernelha 6,68** (o oficial é 5,5–7);
  - ombro lateral 6,61; topo dos cristais 7,12; topo das orelhas 7,42;
  - a cernelha **anatômica** sob o pelo não é mensurável diretamente na malha do Meshy (ela é a própria superfície do pelo). Fica abaixo de 6,68, portanto dentro do porte; **não foi aplicada redução de escala**.

**Export reimportado:**

| Peça | LOD0 (`CR_LoboArtico_LOW.glb`) |
|---|---|
| Cabeça | 14.467 |
| Corpo | 19.652 |
| Pelagem | 3.548 |
| Marca | 1.352 |
| Cristais | 340 |
| **Total** | **39.359** |

- LOD1: 13.564 tris. LOD2: 3.435 tris (sem cartões nem decalque).
- Materiais e escala foram preservados; nenhuma peça passa de 20 mil; texturas de 1024 ou menos.

**Evidências** (`review/v4_final/`):
- `prancha_final_ref_m11_v4.png`;
- `vistas.png` e `comparar_*.png`;
- `grade_olhos.png` e `grade_boca.png`: teste geométrico **sem rig**.

**Ainda não feito ou limitado:**
- sulcos fortes em volta dos olhos (vêm do relevo do Meshy);
- pelagem com leitura de lascas de perto;
- marca menor e menos luminosa que a da referência;
- leve relevo no ombro direito;
- borda da pálpebra serrilhada de perto;
- bochecha angulosa na boca aberta ao máximo.

**Não testado no Roblox:** transparência dos cartões e dos cristais, decalque e desempenho com alcateia (PC, emulador e celular real).

### 8.7 Correção v5: olhos e laterais da boca (03/11/2026). Versão atual: `low_v5/` (v4 preservada em `low_v4/`)

Pedido: `DOCS/pedidos/2026-11-03-lobo-artico-v4-correcao-olhos-boca.md`. Sem Meshy novo, sem Studio, sem rig final.

**Cadeia reproduzível:** `low_ref2/` → `rosto_v5.py` → `low_v5a/` → `ajuste_r3.py` → `low_v5/`.
- Teste: `teste_rosto_v5.py` (`[arame]` sobrepõe o wireframe).
- Pranchas: `prancha_v5.py` (referência | v4 | v5).

**Olhos:**
- **Anel novo:** a pele em volta é refinada (77 a 91 vértices na borda do buraco). O anel tem 40 colunas × 5 aros, com fenda em amêndoa inclinada 12°.
- **Globo:** menor e recuado 0,016 atrás da margem, sem cara de disco colado.
- **Íris:** cobre 76% da fenda, com anel limbar em degradê. O entorno é cinza-castanho pouco brilhante (sem crescente branco).
- **Pálpebras:** fecham por coluna; a de cima faz 65% do curso. Fecham por completo, sem íris exposta.
- **Pintura:** o delineado escuro do Meshy foi clareado só em volta do olho, e o relevo dos sulcos suavizado localmente. A tinta azul fora da fenda virou pelo.
- **Topologia:**
  - 6 furos minúsculos do refino foram fundidos (antes, o `ajuste_r3` os tapava dobrando a pele);
  - o anel segue o enrolamento da pele vizinha (46 faces viradas).

**Boca:**
- **Causa dos triângulos esticados da v4:** o grupo `Mandibula` da pele era decidido pelo plano da boca. A aba do lábio superior pende abaixo do plano e ganhava peso 1 ao lado de pele com peso 0.
- **Primeira correção, por conectividade:** o grupo partia do lábio de baixo, mas contornava a ponta do corte no canto e subia pelo focinho (v5_r4 e v5_r5).
- **Correção final:** busca em duas frentes (lábio de cima × de baixo); cada face fica com o lado mais próximo. Resultado: 1.457 faces do queixo, 1.119 do lábio superior e 14 vértices na fronteira com peso 0,5.
- **Atrás do canto:** gradiente contínuo, vertical e para trás.
- **Refino da malha:** cantos com 2 subdivisões locais e frente da mandíbula refinada (536 faces).
- **Saco bucal:**
  - 3 fileiras intermediárias de garganta (pesos 0,25/0,5/0,75);
  - a bochecha interna usa essas fileiras (a faixa própria sobreposta gerava aresta com 3 faces);
  - dentes e língua não são empurrados.

**Números finais:**

| Item | Valor |
|---|---|
| Cabeça | 19.344 tris |
| Corpo | 19.652 tris |
| LOD1 cabeça | 3.597 tris |
| LOD2 cabeça | 1.098 tris |
| Texturas | ≤1024 |

- Costura cabeça–corpo: 777/777 vértices, distância 0.
- Cernelha: 6,678. Patas apoiadas (z mínimo de 0 a −0,01).
- Auditoria da cabeça LOW (v4 → v5):
  - duplicados 21 → 35, dos quais 33 são o corte dos lábios (intencional, não fundidos) e 2 ficam no canto;
  - não-manifold 0 → 1 (zíper do olho esquerdo);
  - enrolamento invertido 8 → 20 (10 no anel do olho, 10 no saco bucal).

**Reimportação dos GLBs:** LOW, LOD1 e LOD2 foram reimportados em cena limpa. Materiais, UV e imagens estão corretos.
- Os **grupos de vértices NÃO ficam no GLB** (sem armature). Ficam no `.blend` e em `low_v5/rig_pivos.json`.
- Os LODs mantêm os grupos no `.blend`, mas com poucos vértices nas pálpebras: 4 a 6 no LOD1 e 1 a 2 no LOD2.
- No LOD2 a decimação fechou o corte da boca, então a boca **não abre no LOD2**.

**Evidências** (`review/v5_final/`):
- `comparar_olhos_ref_v4_v5.png` e `comparar_boca_ref_v4_v5.png`;
- `comparar_vistas_v4_v5.png` e `vistas.png`;
- `rosto/grade_*.png` e `arame/grade_*.png`;
- `auditoria.json`.

Rodadas intermediárias: `review/v5_r1` a `v5_r6`.

**Tipo de teste:** só teste geométrico sem rig (os pesos girados em memória) e export reimportado. **Nenhum teste no Roblox.**

**Limitações:**
- mandíbula fina herdada do Meshy (de perfil, na abertura máxima);
- dobra estreita da bochecha no canto;
- leve sombreado escuro no canto interno do olho;
- textura listrada na pálpebra de cima fechada do olho esquerdo;
- olhos e boca pobres nos LODs.

### 8.8 Cabeça endireitada: v6 (04/11/2026). Preservada em `low_v6/`

**Problema:** nas vistas ortográficas da v5 (`review/v5_final/simetria/`), a cabeça estava torta, um defeito herdado da base Meshy.
- O crânio estava girado no pescoço, com o focinho apontando para o lado esquerdo do lobo.
- O olho direito ficava 0,078 mais à frente que o esquerdo, e o nariz estava em x=0,138.

**Correção:** `endireitar_v6.py` aplicado sobre `low_v5a` (preservada) gera `low_v6a`; depois `ajuste_r3.py` gera `low_v6`.
- **Medição:** o plano de simetria do crânio foi medido por espelho + KDTree. O giro encontrado foi de 7,05°, e o custo do espelho caiu de 0,0996 para 0,0471.
- **Giro:** a cabeça gira em torno do eixo vertical, num ponto do plano na altura da costura. O peso é suave pela distância à frente da costura (0 → 0,7), então corpo e costura não se movem.
- **Focinho:** só a parte à frente dos olhos (y −5,85 → −6,35) foi deslocada 0,057 para o nariz ficar em x=0.
- **Malhas e pivôs:** o campo depende só da posição e foi aplicado igual a todas as malhas. Os pivôs do `rig_pivos.json` foram transformados pelo mesmo campo (centro e eixo dos olhos, pivô da mandíbula com x=0) e os parâmetros estão na chave `endireitar_v6`.

**Resultado:**
- olhos E (0,266; −5,529; 6,194) e D (−0,269; −5,541; 6,177);
- meio dos olhos em x=−0,002;
- diferença entre os olhos de 0,012 na frente/trás e 0,017 na altura;
- nariz em x=0.

**Auditoria (`review/v6_final/auditoria.json`):** igual à v5.
- cabeça: 19.344 tris, 35 duplicados, 1 aresta não-manifold, 20 arestas com orientação invertida;
- corpo: 19.652 tris, 7 arestas não-manifold;
- costura: 777/777 vértices, distância 0;
- cernelha 6,678 e patas no chão.

**GLBs reimportados:** LOW 44.236, LOD1 13.564 e LOD2 3.435 tris, com as texturas de antes (1024; cristal e marca 512).

**Evidências (`review/v6_final/`):** `simetria/`, `comparar_vistas_v5_v6.png`, `comparar_olhos_ref_v5_v6.png`, `comparar_boca_ref_v5_v6.png`, `rosto/` e `arame/`.

**Tipo de teste:** só teste geométrico sem rig e export reimportado. Nenhum teste no Roblox.

**Limitações:**
- os olhos continuam com tamanhos diferentes (raio do globo 0,189 no E e 0,215 no D), herança da v5;
- as câmeras do teste do rosto continuam centradas no nariz antigo (`meshy/rosto.json`, x=0,138), o que só afeta o enquadramento;
- `simetria.json` mostra `nariz_x` antigo (vem do `rosto.json`); o valor real está em `rig_pivos.json` → `endireitar_v6.nariz_depois`.

### 8.9 LODs do rosto: v7 (04/11/2026). Preservada em `low_v7/`

**Pedido:** corrigir LOD1/LOD2 do rosto antes do rig. O modelo final não foi aprovado e o refinamento artístico geral continua pendente.

**Diagnóstico da v6** (`review/v7_final/diag_antes.txt` e `aud_v6/`):
- **Costura:** cabeça e corpo eram decimados separadamente, então as bordas não coincidiam. Fresta de 0,032 no LOD1 e 0,162 no LOD2.
- **Pálpebras:** 9 a 11 vértices com peso no LOD1 e 5 a 8 no LOD2. No LOD2 a íris aparecia com o olho fechado.
- **Boca:** no LOD2 restavam só 3 arestas do corte; a boca não abria.

**Correção (`lod_rosto_v7.py`, sobre `low_v6/`):**
- **LOD0, só os defeitos que atrapalham redução ou deformação:**
  - colapsada a aresta não-manifold do canto do olho E (aresta de 0,014 com 4 faces);
  - 10 faces viradas (anel/saco) acertadas por maioria dos vizinhos;
  - restam 10 arestas com enrolamento invertido, nenhuma dobra; os lábios cortados não foram fundidos;
  - cabeça LOD0 com 19.340 tris.
- **Pele + corpo:** reduzidos juntos, soldando só os 777 vértices da costura, e separados de novo pelo material. A costura vira a mesma polilinha nos dois lados.
- **Peças soltas** (globos, dentes, língua): redução própria (35% no LOD1, 14% no LOD2). Na redução conjunta elas seguravam ~1,7k tris no LOD2.
- **Grupo `Protecao_LOD`** (0 = protegido), usado no Decimate e documentado no LOD0 (não vai ao GLB):
  - margem das pálpebras e globo;
  - corte dos lábios e cantos;
  - articulação da mandíbula;
  - saco bucal e nariz;
  - perfil mais leve no LOD2.
- **Desdobrar:** faces de pele viradas pela redução voltam à superfície do LOD0. Costura e bordas ficam travadas.
- **Grupos de vértices:** interpolados pelo Decimate. Os pivôs são os mesmos do LOD0.

**Resultados:** `auditar_lod_v7.py`, no `.blend` com grupos. Formato das células: v6 → v7.

| | LOD1 | LOD2 |
|---|---|---|
| tris da cabeça | 3.598 → 3.863 | 1.097 → 1.398 |
| tris do corpo | 6.498 → 6.495 | 1.998 → 1.996 |
| fresta da costura | 0,032 → 0 | 0,162 → 0 |
| vértices de pálpebra (>0,01) | 9–11 → 62–76 | 5–8 → 45–69 |
| arestas do corte da boca (LOD0 = 138) | 74 → 138 | 3 → 92 |
| íris descoberta com o olho fechado | 0 → 0 | 1 de 6 → 0 de 34 |
| arestas de pele visíveis esticadas >2× (boca no máximo) | 8 → 9 | 3 → 0 |
| faces de pele viradas (cabeça) | 4 → 0 | 8 → 8 (área 0,036 → 0,016) |
| não-manifold na cabeça | 1 → 0 | 1 → 0 |

- **Aumento de tris:** cabeça +7% no LOD1 e +27% no LOD2. Vai para a margem das pálpebras, o corte dos lábios, a articulação e o nariz; o resto da cabeça fica mais leve que antes. Todas as malhas seguem ≤20k tris.
- **Mandíbula no focinho de cima:** 1 vértice com 0,31 no LOD1 e nenhum no LOD2. O LOD0 de referência tem 3, até 0,38.
- **Peso do rosto na costura:** 0 em todos os LODs, então os pesos futuros do pescoço podem ser iguais dos dois lados.

**GLBs reimportados** (`verificar_glb.py`):

| GLB | tris | cernelha | z mínimo |
|---|---|---|---|
| LOW | 44.232 | 6,666 | −0,049 |
| LOD1 | 13.826 | 6,709 | −0,039 |
| LOD2 | 3.734 | 6,709 | +0,014 |

- Materiais iguais aos da v6, com 1 UV por malha. Texturas em 1024, exceto cristal e marca (512).
- Os grupos de vértices **não** vão no GLB sem armature: todos os testes de pálpebra e boca foram feitos no `.blend`.
- No `.blend`, auditoria geral igual (`auditoria.json`): costura 777/777 vértices a distância 0, cernelha 6,678, patas apoiadas.

**Evidências (`review/v7_final/`):**
- `comparar_boca_{frente,perfil,34,baixo}.png` e `comparar_olhos_{frente,perfil,34}.png` (referência | LOD0 | LOD1 v6 | LOD1 v7 | LOD2 v6 | LOD2 v7, fases repouso/meio/máximo);
- `LOW|LOD1|LOD2/grade_*.png` e `arame_*/grade_*.png`;
- `comparar_arame_{boca,olhos}.png` e `protecao.png` (mapa do grupo);
- `distancia.png`: **proposta** sem medição no Roblox (LOD0 até 35 studs, LOD1 de 35 a 80, LOD2 acima de 80; campo de visão vertical de 70°);
- `auditoria_lod.json`, `aud_v6/` e `aud_v7/`.

**Reproduzir:**
```
blender -b low_v6/CR_LoboArtico_LOW.blend -P lod_rosto_v7.py -- low_v7
blender -b low_v7/CR_LoboArtico_LOW.blend -P teste_lod_v7.py -- review/v7_final/<LOD> <LOW|LOD1|LOD2> [arame] [protecao]
blender -b low_v7/CR_LoboArtico_LOW.blend -P vistas_distancia_v7.py -- review/v7_final/distancia
blender -b low_v7/CR_LoboArtico_LOW.blend -P auditar_lod_v7.py -- review/v7_final
python prancha_lod_v7.py review/v7_final
```

**Tipo de teste:** geométrico sem rig no `.blend` (pesos girados em memória) e export reimportado. **Nenhum teste no Roblox; nenhuma animação validada.**

**Limitações aceitas por distância:**
- LOD2 com pele facetada em volta dos olhos;
- dentes simplificados no LOD1 e quase sumidos no LOD2;
- língua em poucas faces no LOD2;
- LOD2 com as patas 0,014 acima do chão.

**Pendências:**
- **Dobra fina dos cantos da boca no LOD0** (herdada da v5): vértices com peso de mandíbula 1,0 e 0,5 a ~0,005 um do outro. Com a boca no máximo, 114 arestas pequenas esticam mais de 2× (até 0,2 stud). Os LODs herdam isso sem piorar.
- **Corpo:** faces viradas por camada de pelo na redução, iguais às da v6 (77 / 129 contra 70 / 121). Fora do escopo.
- **Distâncias de troca de LOD:** ainda precisam de medição no Roblox, em PC e celular, e com alcateias.

### 8.10 Cantos da boca na origem: v8 (04/11/2026). Base do rig piloto: `low_v8/` (v7 preservada)

**Pedido:** corrigir na origem (LOD0) a dobra dos cantos da boca e regerar LOD1/LOD2. O modelo final não está aprovado; pelagem, marca, cristais e as faces invertidas do corpo ficam para outra etapa.

**Causa** (`diag_canto_v8.py`, `review/v8_final/antes_v7/` e `canto_*_{pesos,classe,textura}.png`):
- Na comissura, o grupo Mandibula da v5 (BFS em duas frentes) põe vértices de pele com peso 1,0 / 0,5 / 0,0 a 0,005–0,017 stud uns dos outros.
- A abertura do canto cai inteira nessa faixa sem largura: um "acordeão" de lascas e uma lâmina na junção pele/mucosa.

**Correção** (`canto_v8.py` gera `low_v8a/` a partir de `low_v7/`; `lod_rosto_v7.py` gera `low_v8/` a partir de `low_v8a/`):
- **Topologia local:** 86 lascas de pele (< 0,006) na zona de 0,25 do canto fundidas, longe da faixa do lábio e das bordas. Cabeça LOD0 19.340 → 19.168 tris.
- **Pesos:** Mandibula harmônico (média dos vizinhos ponderada por 1/comprimento) na zona de 0,32 de cada canto.
  - Fixos: as bordas funcionais do corte dos lábios a mais de 0,08 do canto (lábio de cima 0, de baixo 1).
  - Mistura suave com o peso original: à frente do canto, só numa faixa da linha da boca (0,16 abaixo, 0,09 acima); atrás do canto, toda a bochecha; a mistura some antes da borda da zona.
- **Gerador de LODs:**
  - remove ilhas soltas de até 3 faces com área < 0,001 no corpo (4 por LOD);
  - fecha furos junto à costura na malha unida (nenhum nesta rodada).
- **Auditoria:** a costura agora só conta bordas junto ao anel real do pescoço.

**Cantos do LOD0** (boca a 32°; zona de 0,35; arestas de pele/lábio/mucosa). Formato das células: v7 → v8.

| | E | D |
|---|---|---|
| arestas curtas (<0,02) com salto de peso >0,3 | 24 → 1 | 22 → 1 |
| visíveis (>0,06 abertas) >2× / >3× | 60/50 → 31/17 | 66/53 → 29/11 |
| p95 da razão das visíveis | 11,7 → 3,5 | 11,3 → 3,8 |
| pior aresta (l0 → l1; razão) | 0,0052 → 0,199; 37,9× | 0,0058 → 0,175; 30,0× |
| pior aresta, v8 | 0,0052 → 0,089; 17× | 0,0158 → 0,175; 11× (junção lábio/pele no fim do corte) |
| área aberta das faces problema | 0,112 → 0,075 | 0,079 → 0,033 |
| faces viradas visíveis (área > 2e-4) | 34 (0,047) → 16 (0,021) | 17 (0,017) → 12 (0,006) |

- **Pesos da pele na zona (histograma):** o pico em 0,5 caiu de 103 para 17 vértices (E) e as faixas 0,6–0,9 se encheram.
- **Lábio de cima** (pele acima da linha + 0,06, à frente do canto): 5 vértices com peso, máximo 0,34. A v7 tinha 3, até 0,38.

**Cantos nos LODs** (`canto_v{7,8}_LOD{1,2}/`):
- LOD1: visíveis >2× caíram de 10/8 para 6/6, e as faces viradas visíveis de 6/1 para 2/0.
- LOD2: 0/0 → 0/1 (uma aresta de 2,9× no canto D, p95 1,8–2,9).

**Sem regressão** (`auditoria_lod.json`):

| | LOD0 | LOD1 | LOD2 |
|---|---|---|---|
| tris cabeça / corpo | 19.168 / 19.652 | 3.887 / 6.493 | 1.400 / 1.994 |
| fresta da costura | 0 | 0 | 0 |
| corte da boca (arestas abertas) | 138 | 138 | 92 |

- Íris descoberta com o olho fechado: 0 em todos os LODs. Vértices de pálpebra iguais aos da v7.
- Não-manifold na cabeça: 0. Enrolamento invertido: 10 / 7 / 4.
- Costura do LOD0: 777/777 vértices, distância 0. Patas no chão; cernelha 6,678.

**GLBs reimportados** (`verificar_glb.py`):

| GLB | tris | cernelha | z mínimo |
|---|---|---|---|
| LOW | 44.060 | 6,666 | −0,049 |
| LOD1 | 13.848 | 6,709 | −0,039 |
| LOD2 | 3.734 | 6,709 | +0,014 |

- Materiais e 1 UV por malha iguais aos da v7; texturas de 1024 e 512.
- Os grupos não vão no GLB sem armature: todos os testes de boca e olhos foram feitos no `.blend`.

**Evidências (`review/v8_final/`):**
- `canto_{E,D}_{pesos,classe,textura}.png`: v7 e v8, lateral/3/4/baixo, repouso/meio/máximo, com arame e mapas de pesos e de tecido;
- `comparar_boca_{frente,perfil,34,baixo,perfil_D,34_D}.png` e `comparar_olhos_*.png` (referência | LOD0/1/2 v7 e v8);
- `LOW|LOD1|LOD2/grade_*.png` e `arame_*/grade_*.png`;
- `sequencia.png` e `sequencia_*.gif`: 13 quadros, de 0° a 32° e de volta;
- `distancia.png`: proposta sem medição no Roblox, recorte ampliado sem filtro;
- `simetria/`, `auditoria.json` e `auditoria_lod.json`.

**Reproduzir:**
```
blender -b low_v7/CR_LoboArtico_LOW.blend -P canto_v8.py -- low_v8a
blender -b low_v8a/CR_LoboArtico_LOW.blend -P lod_rosto_v7.py -- low_v8
blender -b low_v8/CR_LoboArtico_LOW.blend -P diag_canto_v8.py -- review/v8_final/canto_v8 render
blender -b low_v8/CR_LoboArtico_LOW.blend -P teste_lod_v7.py -- review/v8_final/<LOD> <LOW|LOD1|LOD2> lados [arame]
blender -b low_v8/CR_LoboArtico_LOW.blend -P sequencia_v8.py -- review/v8_final/sequencia
blender -b low_v8/CR_LoboArtico_LOW.blend -P auditar_lod_v7.py -- review/v8_final
python prancha_v8.py review/v8_final review/v7_final
```

**Tipo de teste:** geométrico sem rig no `.blend` (mandíbula girada pelos pesos) e export reimportado. **Nenhum teste no Roblox; nenhuma animação validada.**

**Limitações:**
- **Canto E:** restam 16 faces pequenas que viram na abertura máxima (área 0,021, cada uma ≤0,001), no lábio de cima junto do canto; não aparecem nas pranchas.
- **Fim do corte:** a junção lábio/pele estica até 0,2 stud (fica sob a mucosa da bochecha, que aparece rosada dentro do canto).
- **Repouso, vista por baixo:** fio rosado fino de mucosa no canto, herdado da v7; mais visível no LOD2.
- **LOD2:** canto facetado.
- **Mandíbula fina do Meshy:** inalterada.

### 8.11 Rig piloto v9 e validação de deformação no Blender (04/11/2026). Preservado em `rig_v9/` (base da v10)

**Pedido:** rig piloto próprio sobre a v8 (aprovada como base do teste, não como arte final), skinning dos 3 LODs, uma ação técnica curta, export com armature e validação pelo esqueleto reimportado. Ficaram fora:
- biblioteca de clipes;
- Studio (registro ocupado pelo Urso Silvestre);
- IA e habilidades.

Nenhum rig ou clipe dos protótipos V2/V5 de `Blockouts/` foi usado. Elemento e kit continuam indefinidos.

**Scripts (`BLENDER/Criaturas/Lobo_Artico_Ref/`):**

| Script | Função |
|---|---|
| `rig_v9.py` | esqueleto, pesos dos 3 LODs, pelagem/marca/cristais → `rig_v9/CR_LoboArtico_Rig.blend`, `rig_v9.json`, `rig_pivos.json` |
| `acao_v9.py` | ação técnica `Teste_Piloto` (807 quadros, 30 qps) → `rig_v9/acao_v9.json` (trechos e limites) |
| `auditar_rig_v9.py` / `resumo_rig_v9.py` | auditoria com o rig real por LOD e por pico → `review/v9_rig/auditoria_rig.json`, `resumo_rig.json` |
| `exportar_rig_v9.py` | 3 GLBs com armature + ação → `rig_v9/export/`; grava a referência de deformação do rig original |
| `reimportar_rig_v9.py` | reimporta em cena limpa, toca a ação pelo esqueleto importado e compara → `reimport_rig_v9.json`, `reimport_<LOD>.blend` |
| `vistas_rig_v9.py`, `ossos_desenho_v9.py`, `prancha_rig_v9.py`, `video_rig_v9.py`, `renders_rig_v9.sh` | renders com o rig real, ossos desenhados, pranchas e vídeo |

**Esqueleto: 37 ossos com os nomes finais do jogo** (E = +x = lado esquerdo do lobo):
```
Raiz (no chão, sem peso; triângulo-guarda no export)
└ Quadril ─ Coluna1 ─ Coluna2 ─ Coluna3 ─ Pescoco1 ─ Pescoco2 ─ Cabeca ─ Mandibula
  │                              │                                  ├ Palpebra_Sup_E/Inf_E/Sup_D/Inf_D
  │                              │                                  └ Orelha_E / Orelha_D
  │                              └ Escapula_X ─ Umero_X ─ Antebraco_X ─ Metacarpo_X ─ Dedos_X   (X = E, D)
  ├ Coxa_X ─ Tibia_X ─ Metatarso_X ─ DedosPe_X
  └ Cauda1 ─ Cauda2 ─ Cauda3 ─ Cauda4
```

**Por que 37 ossos:**
- **Coluna:** quadril + 3 segmentos, para curvar e inclinar sem dobrar num ponto só.
- **Pescoço:** 2 segmentos.
- **Patas digitígradas:** 5 ossos na dianteira (escápula, úmero, antebraço, metacarpo, dedos) e 4 na traseira (coxa, tíbia, metatarso, dedos).
- **Cauda:** 4 segmentos, para uma cauda longa e cheia.
- **Rosto:** mandíbula, 4 pálpebras (os grupos já aprovados) e 1 osso por orelha.
- **Sem ossos de língua nem de dedos separados:** a língua e os dentes de baixo seguem a Mandibula; a pata tem um bloco único de dedos na malha.

**Orientação e medidas:**
- **Eixos:** o X local de todo osso é o X global, então a flexão é um giro em X local. Exceção: nas pálpebras, o X local é o eixo de fechamento da v5/v8 (`rig_pivos.json`).
- **Escala:** 1, sem transformações, em studs.
- **Raiz:** no chão (z 0), entre as patas.
- **Repouso:** é a malha v8 sem nenhuma mudança; o desvio no quadro 0 é 1e-6.
- **Marcos:** medidos na malha (fatias de altura por pata, linha do dorso, ponto mais alto das orelhas). A mandíbula e as pálpebras usam os pivôs da v8.
- **Pés:** patas em (1,24; −3,52), (−0,97; −3,79), (1,49; 2,11) e (−1,05; 2,01). O z mínimo do LOD0 é −0,049 (pata levemente abaixo do chão, herdado).
- **Altura:** a cernelha foi medida no corpo junto ao ombro, sem orelhas nem cristais. Dá 6,666 no GLB reimportado do LOD0 e 6,709 no LOD1/LOD2, dentro do porte de 5,5–7.
- **Orelhas:** a base da orelha D ficou 0,23 mais para fora que a da E (assimetria da malha).

**Pesos:**
- **Base:** heat do Blender num proxy fechado (voxel 0,07) da pele unida cabeça + corpo. Os pesos passam a cada pele dos 3 LODs por interpolação da face mais próxima. No proxy:
  - os ossos da pata dianteira não pesam na garganta nem no peito à frente do ombro (somem de y −3,9 a −4,6);
  - os da traseira não pesam na barriga (somem de y 1,0 a 0,2);
  - antes desse limite, o heat dava peso de escápula à garganta, e uma aresta chegava a 10,6×;
  - a troca de lado E/D é suave na linha do meio;
  - 4 passadas de alisamento.
- **Rosto:**
  - fórmula: peso final = (1 − m − p) × base + m × Mandibula + p × Palpebra, onde m e p são os pesos aprovados da v8;
  - os grupos originais ficam guardados como `v8_<grupo>`;
  - longe do plano da costura, o rosto fica 100% na Cabeca.
- **Orelhas:** peso ao longo do eixo base → ponta.
- **Peças soltas** (globos, dentes, língua): Cabeca 100%, mais a Mandibula da v8.
- **Costura:** os pares coincidentes cabeça/corpo (777 / 85 / 81 por LOD) recebem a média. A diferença antes da média era 0.
- **Limite:** no máximo 4 influências por vértice, normalizadas; nenhum vértice sem influência.
- **Pelagem:** cada cartão inteiro recebe o peso da pele na raiz (distância raiz–pele: média 0,008, máxima 0,067).
- **Marca:** cada vértice recebe o peso da pele mais próxima.
- **Cristais:** cada cristal inteiro recebe o peso da base.
- **LODs:** os 3 usam o mesmo esqueleto, os mesmos nomes e o mesmo repouso. Os pesos vêm do mesmo proxy, mais os grupos faciais de cada LOD.

**Tentativa desfeita: separar cauda e pata traseira**
- **O que foi testado:** eixo da cauda pelo miolo do volume e separação dos pesos cauda/pata por distância, com faixas de 0,4 e de 1,0.
- **Por que piorou:** a cauda do Meshy está fundida à coxa e ao jarrete esquerdos, e separar os pesos rasgou a junção:
  - faces viradas no quadril para trás: de 0 para 96–109;
  - cauda para cima: 94–97 arestas >2× no corpo (antes eram 3).
- **Resultado:** voltou-se à versão anterior.

**Ação técnica `Teste_Piloto`** (parâmetros do piloto, não regras oficiais; trechos marcados na linha do tempo):

| Quadros | Trecho | Amplitudes |
|---|---|---|
| 0–58 | mandíbula | 15° e 32° (máxima prevista, a mesma dos testes v7/v8) |
| 58–82 | piscar | 50% e 100%, dois olhos |
| 82–184 | cabeça | lados 35° (pescoço 30+30%, cabeça 40%); cima 25°; baixo 18° (pescoço 45+35%, cabeça 20%) |
| 184–366 | tronco | coluna ±12°; inclinação ±8°; peso 0,18 lateral e 0,20 frente/trás |
| 366–606 | cada membro | ombro/quadril +15° e −18°; passo dianteiro −18°/45°/95° (ombro/cotovelo/carpo); passo traseiro −10°/50°/−65° (quadril/joelho/jarrete); dedos −20°/+25° com a pata no ar |
| 606–688 | cauda | lados 35°; cima 30°; baixo 10° |
| 688–758 | orelhas | trás 35°; frente 15°; giro 25° |
| 758–806 | combinação | cabeça virada 30° + pescoço baixo 15° + boca 32° |

- **Patas plantadas nos trechos do tronco:** IK analítico de 2 ossos, gravado como FK. Deslize máximo de 0,0008 (LOD0) e 0,0013 (LOD2); afundamento 0.
- **Primeira versão reprovada no próprio teste, depois corrigida:**
  - coluna a 24°: com as patas presas, as pernas cruzavam;
  - passo dianteiro a 50/65: a pata esticava para trás em vez de subir.

**Teste com o rig no Blender** (`resumo_rig.json`; pior pico de cada métrica):

| | LOD0 | LOD1 | LOD2 |
|---|---|---|---|
| repouso (desvio) | 1e-6 | 1e-6 | 1e-6 |
| fresta da costura (todos os picos) | 0 | 0 | 0 |
| íris descoberta no piscar total | 0/416 | 0/77 | 0/34 |
| boca máxima: desvio do rig × teste v8 | 0,027 | 0,024 | 0,022 |
| cantos visíveis >2× E/D: rig (v8) | 33/32 (31/29) | 6/7 (6/6) | 0/2 (0/2) |
| corpo: arestas >2× (pior) | 111 (cabeça cima) | 35 | 17 |
| corpo: maior razão | 3,84 | 3,61 | 3,30 |
| cabeça fora da boca: arestas >2× | 1 | 0 | 0 |
| corpo: faces viradas (pior) | 112 (cabeça baixo) | 38 | 15 |
| corpo: área virada (pior) | 0,707 (combinação) | 0,681 | 0,666 |
| colapso de volume (vértices) | 58 (passo traseiro E) | 19 | 6 |
| cristais: variação de aresta | 0,9% | 0,9% | 0,9% |
| marca: distância à pele (repouso → pior) | 0,014 → 0,018 | 0,053 → 0,053 | — |
| pelagem: raiz–pele (p99 / máx.) | 0,017 / 0,089 | 0,019 / 0,056 | — |
| cruzamentos novos da pele (só LOD0) | 321 (cabeça baixo) | — | — |

- **Rosto, sem regressão:**
  - abrir a boca só com o rig mexe os mesmos vértices, com os mesmos pesos da v8;
  - a mistura linear do skinning difere do giro por peso da v8 em até 0,027 stud;
  - os cantos ficam praticamente iguais aos da v8 (+2/+3 arestas visíveis no LOD0).
- **O que mais estica é o corpo, não o rosto:**
  - cabeça para cima: nuca e juba na base do pescoço;
  - cabeça para baixo e combinação: a garganta e a juba dobram contra o peito. São 112 faces viradas e 321 pares de triângulos que passam a se cruzar, quase todos de `Pescoco2`/`Umero`;
  - ombro e quadril à frente: axila e flanco, com 23–32 faces viradas.
- **Cauda × pata traseira esquerda (defeito herdado da malha):**
  - no passo e no quadril para trás, 38–58 vértices do lado de dentro do jarrete/cauda se aproximam do osso (colapso);
  - há cruzamentos `Tibia_E` × `Cauda`;
  - a malha do Meshy funde as duas superfícies; só uma correção de malha resolve.
- **Pata testada no ar:** girada isolada para trás, desce até 0,10 abaixo do repouso (o arco do membro sem IK). Em clipes reais com a pata no chão, usar IK.
- **Marca no LOD1:** fica 0,053 acima da pele já no repouso, porque é a mesma marca do LOD0 sobre um corpo reduzido (herdado da v7). Acompanha a pele sem descolar mais.
- **Cristais:** mantêm a forma (variação ≤0,9%). A base se afasta da pele no máximo 0,018 (LOD1).

**Export e ação validada após reimportação** (`rig_v9/export/`, `reimport_rig_v9.json`):

| GLB | MB | tris por MeshPart (todas ≤20k) |
|---|---|---|
| `CR_LoboArtico_LOW_Rig.glb` | 14,6 | cabeça 19.168, corpo 19.653, pelagem 3.548, marca 1.352, cristais 340 |
| `CR_LoboArtico_LOD1_Rig.glb` | 12,6 | 3.887 / 6.494 / 1.776 / 1.352 / 340 |
| `CR_LoboArtico_LOD2_Rig.glb` | 10,9 | 1.400 / 1.995 / 340 |

- **Esqueleto e malhas reimportados:**
  - 1 armature com os 37 ossos, nomes e hierarquia iguais aos do `rig_v9.json`;
  - nenhum grupo que não seja osso;
  - até 4 influências, soma dos pesos 1,0000, 0 vértices sem influência;
  - materiais e texturas de 1024/512 presentes;
  - escala igual à da v8 (cernelha 6,666; z mínimo −0,049).
- **Ação:** `Teste_Piloto`, quadros 0–806, 37 ossos animados.
- **Deformação pelo esqueleto reimportado:** em 123 quadros de amostra, o desvio máximo contra o rig original é 0,00001 stud, nos 3 LODs.
- **Triângulo-guarda:** são 3 vértices extras no corpo de cada LOD, para a Raiz (sem peso) não sumir no Roblox.
- **Ossos-folha no reimportado:** o glTF guarda só as juntas, e o importador recalcula o comprimento dos ossos-folha (pálpebras, Raiz, dedos aparecem mais longos em `reimport_<LOD>.png`). Não muda a deformação (desvio de 1e-5).
- **Diferença de pixels:** repouso v8 × rig chega a 54/255 e original × reimportado a 55/255, sempre em pixels isolados de cartões com alfa (ruído do EEVEE e materiais do GLB). A prova de forma é o desvio geométrico.
- **Manchas pretas pequenas** na juba e na costura já aparecem no repouso da v8: são cartões de pelo de costas, herdados.
- **Primeiro export falhou:** os GLBs de LOD1/LOD2 saíram sem as malhas do LOD, que ficam ocultas no `.blend`. O script agora as mostra e confere a seleção.

**Teste real no Roblox: não feito.** Fica para verificar no Studio:
- limite de ossos por malha e de influências por vértice;
- se o Importador 3D traz a ação do GLB;
- nomes dos ossos após a importação;
- se a Raiz é mantida pelo triângulo-guarda;
- escala em studs.

Se a ação não vier no GLB, a ponte JSON → KeyframeSequence do pipeline continua disponível. Ela ainda não foi feita para este piloto.

**Evidências (`review/v9_rig/`):**
- `repouso_<LOD>.png`: referência | v8 sem rig | rig no quadro 0 | diferença ×8, em 17 vistas;
- `poses_<LOD>_<vista>.png`: todos os picos, com os ossos desenhados;
- `boca_<LOD>.png`, `olhos_<LOD>.png`, `costura_<LOD>.png` e `arame_cantos.png`: closes;
- `reimport_<LOD>.png`: rig original × esqueleto reimportado;
- `hierarquia.png`: ossos com nomes e árvore;
- `video/LoboArtico_rig_v9_normal_30qps.mp4` e `video/LoboArtico_rig_v9_lento_0.5x.mp4`: a ação inteira no LOD0, com os ossos;
- `auditoria_rig.json`, `resumo_rig.json` e `repouso_diferenca_pixels.json`.

**Reproduzir:**
```
blender -b low_v8/CR_LoboArtico_LOW.blend -P rig_v9.py -- rig_v9
blender -b rig_v9/CR_LoboArtico_Rig.blend -P acao_v9.py
blender -b rig_v9/CR_LoboArtico_Rig.blend -P auditar_rig_v9.py -- review/v9_rig
python resumo_rig_v9.py review/v9_rig
blender -b rig_v9/CR_LoboArtico_Rig.blend -P exportar_rig_v9.py -- rig_v9/export <dir_ref>
blender -b --factory-startup -P reimportar_rig_v9.py -- rig_v9/export <dir_ref> rig_v9/rig_v9.json
sh renders_rig_v9.sh && python prancha_rig_v9.py review/v9_rig
blender -b --factory-startup -P video_rig_v9.py -- review/v9_rig/video/ossos review/v9_rig/video/LoboArtico_rig_v9
```

**Tipos de teste:**
- teste com o rig no Blender (armature real deformando as malhas);
- ação validada após a reimportação dos GLBs (esqueleto importado);
- **teste no Roblox: não realizado.**

**Pendências para a próxima etapa (aguardam aprovação):**
- dobra da garganta/juba ao baixar a cabeça;
- junção cauda/jarrete esquerdo (precisa de correção de malha);
- axila e flanco nos extremos;
- desempenho com alcateias em PC/celular;
- biblioteca de clipes;
- Studio, com reserva em `DOCS/estado/studio-em-uso.md`.

### 8.12 v10: cauda separada da coxa/jarrete esquerdos (05/11/2026). Preservada em `rig_v10/` (base da v11)

**Pedido:** correção localizada de malha e pesos para separar a cauda da pata traseira esquerda, sobre o rig v9. Mesmos 37 ossos, nomes, hierarquia, repouso e ação (mais um trecho de teste). Sem clipes completos, sem Studio (registro ocupado pelo chat do Dragão Sombrio) e sem mexer em boca, olhos, costura, garganta/juba ou axila/flanco.

**Scripts (pasta `BLENDER/Criaturas/Lobo_Artico_Ref/`):**

| Script | Função |
|---|---|
| `diag_cauda_v10.py` | diagnóstico por fatias: fusão topológica × contato, com classificação geodésica |
| `separar_cauda_v10.py` | corte, tampas, alisamento local, pesos e cartões → `rig_v10/` |
| `textura_cauda_v10.py` | UV das tampas e repintura da área de contato |
| `acao_v10.py` | a ação da v9 (quadros 0–806 idênticos) + trecho H (806–890) |
| `auditar_cauda_v10.py` | auditoria local E/D |
| `vistas_cauda_v10.py`, `prancha_cauda_v10.py`, `renders_cauda_v10.sh` | closes e pranchas |
| `refazer_v10.sh` | refaz tudo a partir de `rig_v9/` |

**Diagnóstico (`review/v10_cauda/diag_antes.json`, `diagnostico.png`):**
- **Fusão topológica, não só contato.** No lado esquerdo, a pele da cauda e a da coxa/jarrete formam um único contorno fechado em todas as fatias de z 1,1–1,5 até 3,7 nos três LODs. O lado direito nunca funde: cauda e pata estão em contornos separados.
- **Por que a separação só por pesos da v9 piorava:** a pele passava de uma superfície para a outra por uma faixa larga (área de contato de cerca de 2,9 stud²). A distância aos eixos dos ossos ainda errava o lugar da ponte, porque os ossos da cauda ficam no fundo do volume.

**Correção (por LOD, só no corpo, abaixo da raiz da cauda):**
1. **Linha da ponte.** É onde se igualam as distâncias geodésicas (pela pele) a sementes certas da cauda (dorso e ponta) e da pata E (lado de fora e pé). Sai uma linha em U: face interna, fundo em z ≈ 1,2 e face externa, com as pontas junto à raiz (z ≈ 3,8–3,9).
2. **Corte.** Cada face da região recebe a classe cauda ou pata; a pele é **descolada** nas arestas entre as classes (59 / 38 / 18). Nenhuma face é retirada.
3. **Tampas.** Cada lado ganha uma tampa própria (141 / 60 / 24 tris por lado):
   - preenchimento, subdivisão até a aresta-alvo e orientação coerente com a pele;
   - reprojeção num cilindro em torno do eixo real do lado: ossos da pata; na cauda, o miolo medido por fatias. Primeiro saíam planas e viravam "pranchas" no movimento;
   - as duas tampas só se tocam na linha de contato e no fecho junto à raiz.
4. **Faixa de contato.** A pele a menos de 0,15 do outro lado no repouso (escondida na v9, com lascas do Meshy) é alisada por lado, no máximo 0,08 por vértice.
5. **Pesos por conectividade.** Abaixo da raiz, os dois lados já não se tocam (0 vértices em comum nos 3 LODs).
   - 3 passadas de alisamento só em x > −0,3. Os componentes alcançam a pata D pelo períneo, e ela fica como na v9 (controle).
   - Depois, a cauda perde só os ossos da pata E e a pata E perde os da cauda.
   - A remoção é gradual de z 3,70 até 3,25 (LOD2: 3,62 → 3,17). Acima disso, os pesos da v9 garantem a transição para o quadril.
6. **Cartões de pelo.** 167 (LOD0) e 127 (LOD1) cartões da região recebem de novo o peso da pele na raiz.
7. **Textura** (`textura_cauda_v10.py`, sem novo bake):
   - **Tampas:** cada triângulo usa uma face limpa de referência (transformação afim). A primeira versão, com UV vértice a vértice, atravessava ilhas do atlas e aparecia como listras.
   - **Área de contato:** os texels das faces que ficavam escondidas (83 da cauda e 115 da pata, 2.124 texels) são repintados por transferência da pele limpa mais próxima, em cor, normal e rugosidade. O bake antigo tinha manchas escuras ali.
   - As cópias das texturas ficam em `rig_v10/`.

**Tentativas descartadas (informação técnica):**
- tirar a faixa e tapar: o buraco de uma faixa tem uma só borda pelos dois lados, e o preenchimento refazia a ponte;
- inserir vértices sobre a linha exata: +230 tris, o que estourava os 20k do LOD0;
- o `holes_fill` recusava o segundo lado no LOD1/LOD2, por isso o polígono é montado à mão;
- alisar os pesos pelo componente inteiro: alterava a pata D (1 aresta 2,30× no passo D);
- alisar só a menos de 0,6 do corte: criava degrau na pata E (12 arestas >2×).

**Ação:** `acao_v10.py` reproduz a da v9 e acrescenta o trecho H, combinações moderadas (70%) da cauda com a pata E:
- cauda E 25° + passo E;
- cauda para cima 20° + quadril E para trás 12°;
- cauda D 25° + quadril E à frente 13°.

A mesma ação foi aplicada a uma cópia da v9 (`review/v10_cauda/v9_base/`; `rig_v9/` intacto), para comparar com amplitudes iguais.

**Antes → depois** (`aud_cauda_v9.json` → `aud_cauda_v10.json`; pior pico da região; lado E corrigido, lado D de controle):

| LOD0 | E: v9 → v10 | D: v9 → v10 |
|---|---|---|
| colapso de volume (vértices) | 58 → 3 (passo E) | 1 → 1 |
| faces viradas (área) | 4 (0,094) → 3 (0,059) | 5 (0,146) → 5 (0,146) |
| arestas >2× | 3 → 0 | 3 → 0 |
| maior razão | 2,41 → 1,91 | 2,41 → 1,47 |
| maior aumento absoluto (stud) | 0,167 → 0,135 | 0,245 → 0,152 |
| cruzamentos novos pele × pele | 50 → 229 (cauda para baixo; 166 com tampa) | 15 → 31 |

- **LOD1:** colapso 19 → 2; área virada 0,088 → 0,056; maior razão 2,03 → 1,63; aumento absoluto 0,247 → 0,130; cruzamentos 8 → 108.
- **LOD2:** colapso 6 → 2; área virada 0,180 → 0,0005; maior razão 1,82 → 2,15 (1 aresta no passo E); aumento absoluto 0,384 → 0,319; cruzamentos 19 → 53.
- **Lado D (controle):** não piora em nenhum pico de nenhum LOD (diferença na maior razão ≤ 0,15).
- **Fusão depois:** nenhuma fatia no LOD0 e no LOD1. No LOD2 só z 3,7, já na raiz, acima das pontas do corte.
- **Cruzamentos que aumentaram:** são colisão, e não rasgo. Na v9, as superfícies fundidas esticavam juntas; na v10 são independentes e entram uma na outra quando se aproximam:
  - peso E 0 → 129, quadril E para trás 3 → 158, cauda para baixo 0 → 229;
  - 72–100% dos pares envolvem uma tampa (zona de contato interna);
  - profundidade máxima de 0,23 stud no LOD0, 0,29 no LOD1 e 0,44 no LOD2 (malha mais grossa);
  - nas vistas de trás e de 3/4 com pelo, não aparecem por fora (`poses_LOW_textura_*`).
- **Pelo × pele, medido à parte:** de −28 a +16 (LOD0) e de −22 a +8 (LOD1) triângulos de cartão por pico, sem tendência (o pelo já atravessava a pele na v9).

**Sem regressão** (`review/v10_cauda/global/resumo_rig.json` × v9):
- repouso 1e-6;
- costura 0;
- íris 0/416, 0/77, 0/34;
- cantos da boca iguais (33/32, 6/7, 0/2);
- cristais 0,9%;
- marca 0,014 → 0,018;
- pelagem raiz–pele: p99 0,018, máx. 0,089;
- colapso global do corpo: 58 → 4.

Garganta/juba (112 faces viradas ao baixar a cabeça) e axila/flanco continuam iguais aos da v9 e **não** foram tratados nesta tarefa.

**Tris (todas as MeshParts ≤ 20k):**

| LOD | corpo antes | corpo depois |
|---|---|---|
| LOD0 | 19.652 | 19.934 (19.935 com o triângulo-guarda) |
| LOD1 | 6.493 | 6.613 |
| LOD2 | 1.994 | 2.042 |

A cabeça, a pelagem, a marca e os cristais não mudaram. Texturas: 1024 (corpo e cabeça) e 512 (marca e cristais).

**Export e reimportação** (`rig_v10/export/`, 14,8 / 12,8 / 11,0 MB):
- 37 ossos com nomes e hierarquia iguais;
- ação `Teste_Piloto` 0–890, com 37 ossos animados;
- no máximo 4 influências, pesos com soma 1, 0 vértices sem influência;
- materiais e 11/11/9 imagens presentes;
- cernelha 6,666 / 6,709 / 6,709;
- a ação tocada pelo esqueleto reimportado difere do rig original em no máximo 0,00018 stud (pelagem do LOD1; corpo 0,00001), em 134 quadros.

**Evidências (`review/v10_cauda/`):**
- `diagnostico.png`: classe, pesos e pele sem pelo, v9 × v10, mais as tampas;
- `repouso_<LOD>.png`: v9 | v10 | diferença;
- `poses_<LOD>_<modo>_<vista>.png`: perfil E/D, traseira, 3/4, face interna (corte) e baixo, com e sem pelo e mapas de pesos;
- `tampas.png` (com arame);
- `LoboArtico_cauda_v9_v10_normal_30qps.mp4` e `_lento_0.5x.mp4`: v9 e v10 lado a lado, quadros 486–890;
- `aud_cauda_v9.json`, `aud_cauda_v10.json`, `diag_antes.json`, `diag_depois.json`, `global/`.

**Tipos de teste:**
- teste com o rig no Blender (v9 e v10 com a mesma ação);
- ação validada após a reimportação dos GLBs;
- **teste no Roblox: não realizado.**

**Pendências:**
- **Cauda × pata (colisão):** ao se aproximarem, as superfícies se interpenetram pela zona de contato (até 0,23 no LOD0 e 0,44 no LOD2); escondido pelo pelo nas vistas testadas. Se incomodar em clipes, as opções são limitar a amplitude da cauda para o lado E/baixo nos clipes ou usar um corretivo; não foi feito.
- **Lascas pontudas herdadas na face interna da cauda:** ficam visíveis com a cauda virada 35° para E (quadro 621, 3/4 de trás), mesmo depois do alisamento limitado a 0,08.
- **Tampas:** reusam a textura de pelo limpo vizinho; de perto, com a pata afastada, a face interna é mais lisa e uniforme que o resto da cauda.
- **Junção na raiz:** a cauda e a pata continuam ligadas acima de z ≈ 3,7–3,9, o que é anatômico (raiz da cauda e nádega).
- **Ficam para outra etapa:** garganta/juba, axila/flanco, biblioteca de clipes, Studio e desempenho com alcateias.

### 8.13 v11: garganta e juba ao baixar a cabeça (05/11/2026). Rig atual: `rig_v11/` (v10 preservada em `rig_v10/`); clipes em `anim_v12/` (8.14)

**Pedido:** correção localizada da garganta, do babador da juba e do peito sobre a v10.
- Mantidos: mesmos 37 ossos, nomes, hierarquia, repouso e ação.
- Sem Studio (registro ocupado pelo chat do Urso).
- Não tratados: colisões cauda/pata e lascas internas da cauda.

**Scripts (`BLENDER/Criaturas/Lobo_Artico_Ref/`):**

| Script | Função |
|---|---|
| `diag_garganta_v11.py` | diagnóstico por pico: pele × lâmina, ossos envolvidos, cruzamentos e membro na garganta |
| `garganta_v11.py` | correção dos pesos → `rig_v11/` |
| `renders_garganta_v11.sh` | renders de evidência |
| `prancha_garganta_v11.py` | pranchas |
| `refazer_v11.sh` | refaz a v11 a partir de `rig_v10/` |
| `vistas_cauda_v10.py` | ganhou as vistas `garganta_*` e `geral_jogo` e o modo `pescoco` |

**Diagnóstico (v10, LOD0, região de y < −2,6 e z < 5,6; `review/v11_garganta/diag_v10.json`):**
- **As dobras são da pele principal, não do pelo esculpido.** Com a cabeça baixa, 108 das 112 faces viradas são pele. As 793 "lâminas" do Meshy, faces de casca fina, respondem por 4 faces e 31 dos 298 cruzamentos novos.
- **Ossos nas faces viradas:** misturas de `Escapula`+`Pescoco2`+`Umero` (27 + 26) e de `Cabeca`+`Pescoco2` (19 + 18).
- **Peito puxado pelo membro:** 1.233 vértices da garganta/peito à frente do ombro tinham mais de 10% de peso de `Umero`/`Escapula`.
- **Sem fusão acidental de superfícies.** Os cruzamentos são da pele dobrando sobre si mesma, e a costura cabeça/corpo continua fechada (fresta 0).
- **Causa:** o heat deixava o peito e o babador nos ossos do membro, com um degrau abrupto para `Pescoco2` (`poses_LOW_pescoco_*`). Quando a cabeça baixa, essa faixa dobra contra o próprio peito.

**Correção (só pesos; nenhuma topologia, UV ou bake mudou; por LOD, na pele da cabeça e do corpo):**
1. **Pesos axiais** (`Coluna3`, `Pescoco1`, `Pescoco2`, `Cabeca`) refeitos como transição suave ao longo da cadeia.
   - O parâmetro é a posição ao longo do corpo entre as juntas reais do rig, com faixa de 45% do osso em cada junta.
   - A pele ventral abaixo do eixo do pescoço recua o parâmetro para trás: 0,9 por stud a partir de 0,4 de profundidade. Assim o peito fica ancorado na coluna e na base do pescoço, e a garganta comprime e desliza sobre ele.
2. **Ossos do membro só na ponta do ombro:** somem de y −3,3 a −3,9, antes disso perto da linha do meio, e o lado de fora do ombro continua até y −4,2. Os vértices com mais de 10% de membro caem de 1.233 para 452 (LOD0), 244 para 129 (LOD1) e 95 para 50 (LOD2).
3. **Mistura suave com os pesos da v10** fora da região. Nada muda no rosto (`Cabeca` ≥ 0,97), na mandíbula, nas pálpebras e nas orelhas.
4. **Alisamento e costura:** 2 passadas de alisamento só onde a máscara age; os pares coincidentes da costura (777 / 86 / 82) recebem a média; no máximo 4 influências.
5. **Cartões de pelo, marca e cristais:**
   - os cartões da região (342 no LOD0 e 258 no LOD1) recebem de novo o peso da pele na raiz;
   - a marca, vértice a vértice, e os cristais, pela base, seguem a pele nova. Sem isso, a marca descolava até 0,039 com a cabeça virada; esse passo foi acrescentado depois da 1ª auditoria.

**Varredura** (recuo ventral / profundidade inicial; LOD0; faces viradas com a cabeça baixa / na combinação; `scratchpad sw_*`):

| Parâmetros | Cabeça baixa | Combinação | Observação |
|---|---|---|---|
| 0,6 / 0,7 | 4 | 63 | |
| 0,9 / 0,7 | 0 | 50 | |
| 1,3 / 0,7 | 27 | 48 | |
| **0,9 / 0,4** | **13** | **39** | escolhida: menor área total e cruzamentos 89 na combinação |
| 1,3 / 0,4 | 95 | 136 | reprovada: 746 cruzamentos e o pescoço desmonta |

**Antes → depois** (v10 → v11, mesma ação `acao_v10` e mesmas câmeras; região garganta/peito; pele; `diag_v10.json` → `diag_v11.json`). Formato das células de faces viradas: número (área).

| LOD0 | faces viradas | cruzamentos novos | arestas >2× | maior razão | maior aumento absoluto | comprimidas <0,5× |
|---|---|---|---|---|---|---|
| cabeça E 35 | 26 (0,193) → 12 (0,041) | 86 → 30 | 74 → 2 | 2,75 → 2,13 | 0,263 → 0,126 | 64 → 88 |
| cabeça D 35 | 16 (0,157) → 1 (0,001) | 58 → 15 | 54 → 24 | 2,92 → 2,35 | 0,281 → 0,177 | 24 → 28 |
| cabeça cima 25 | 0 → 0 | 13 → 15 | 222 → 2 | 3,84 → 2,02 | 0,601 → 0,163 | 0 → 0 |
| cabeça baixo 18 | 108 (0,646) → 13 (0,053) | 298 → 55 | 0 → 0 | 1,62 → 1,45 | 0,093 → 0,056 | 60 → 150 |
| combinação | 106 (0,708) → 39 (0,199) | 294 → 89 | 14 → 0 | 2,24 → 1,96 | 0,202 → 0,108 | 50 → 146 |
| ombro E à frente | 20 (0,099) → 0 | 65 → 21 | 25 → 0 | 2,56 → 1,99 | 0,151 → 0,136 | 46 → 24 |
| ombro D à frente | 28 (0,154) → 0 | 23 → 18 | 20 → 2 | 3,31 → 2,30 | 0,157 → 0,115 | 62 → 6 |
| inclinação E / peso E | 0 → 0 | 21 → 15 / 6 → 11 | 4 → 0 / 0 → 0 | 2,63 → 1,57 / 1,35 → 1,17 | — | — |

- **LOD1:** cabeça baixa 36 (0,666) → 1 (0,000); combinação 38 (0,682) → 6 (0,048); cabeça para cima >2× 70 → 0; axila 2–4 → 0.
- **LOD2:** cabeça baixa 13 (0,606) → 0; combinação 11 (0,666) → 3 (0,093); cabeça para cima >2× 34 → 0.
- **Arestas comprimidas na cabeça baixa e na combinação** (60 → 150 e 50 → 146 no LOD0): a garganta agora comprime em vez de dobrar contra o peito. Nas pranchas (perfil, frente, baixo, sem pelo) não aparece colapso de volume; o colapso global do corpo continua 4 (igual à v10).

**Global e regressão** (`review/v11_garganta/global/resumo_rig.json` × `review/v10_cauda/global/`):
- **Corpo, pior pico (LOD0):**
  - arestas >2×: 111 → 23;
  - maior razão: 3,84 → 3,24 (agora o ombro à frente);
  - faces viradas: 112 → 34;
  - área virada: 0,707 → 0,306 (agora o quadril D à frente, igual à v10).
- **Corpo, LOD1/LOD2:** área virada 0,681 → 0,315 e 0,666 → 0,132.
- **Sem mudança:**
  - repouso 1e-6;
  - costura 0;
  - íris 0/416, 0/77, 0/34;
  - cantos da boca idênticos;
  - cristais 0,9% e base ≤ 0,018;
  - marca 0,014 → 0,017 (v10: 0,018);
  - pelagem raiz–pele p99 0,018 / máx. 0,089 (igual à v10);
  - colapso global 4 / 3 / 2.
- **Cauda/pata E** (`aud_cauda_v11.json` × v10): nenhuma métrica piora mais de 2 em nenhum pico.
- **Repouso:** diferença de pixels ≤ 11/255 em 5 vistas e 3 LODs, só ruído, porque a geometria é idêntica.

**Tris e export** (mesma geometria da v10):
- MeshParts: cabeça 19.168, corpo 19.935 com o triângulo-guarda, pelagem 3.548, marca 1.352, cristais 340; LOD1 3.887 / 6.614 / 1.776; LOD2 1.400 / 2.043.
- Texturas 1024 / 512 (as mesmas da v10, copiadas para `rig_v11/`).
- **Reimportação dos 3 GLBs** (`rig_v11/export/`):
  - 37 ossos, nomes e hierarquia iguais;
  - ação 0–890 com 37 ossos animados;
  - no máximo 4 influências;
  - 11 / 11 / 9 imagens;
  - cernelha 6,666 / 6,709 / 6,709;
  - a deformação pelo esqueleto reimportado difere do rig original em no máximo 0,00018 stud, em 134 quadros.

**Corretivos:** nenhum shape key nem driver exclusivo do Blender; só pesos de ossos, exportáveis no GLB.

**Evidências (`review/v11_garganta/`):**
- `repouso_<LOD>.png`;
- `poses_<LOD>_<modo>_<vista>.png`, com os modos textura, textura sem pelo e `pescoco` (pesos + arame) e as vistas `garganta_frente`, `_E`, `_D`, `_baixo`, `_34`, `_34_D` e `geral_jogo` (cerca de 25 studs, proposta);
- `LoboArtico_garganta_v10_v11_normal_30qps.mp4` e `_lento_0.5x.mp4`: cabeça (ida e volta contínua), ombro E e combinação, v10 e v11 lado a lado;
- `diag_v10.json`, `diag_v11.json`, `global/` e `aud_cauda_v11.json`.

**Tipos de teste:**
- teste com o rig no Blender (v10 e v11, mesma ação);
- ação validada após a reimportação;
- **teste no Roblox: não realizado.**

**Pendências:**
- **Restos nas poses extremas:**
  - combinação: 39 faces viradas (área 0,199) na frente do ombro esquerdo, do lado de dentro da curva do pescoço; é compressão anatômica, mas fica uma prega pequena;
  - cabeça para E: 12 faces (0,041);
  - cruzamentos residuais de 55–89.
- **Cabeça para D:** 24 arestas >2× (antes 54).
- **Fora desta tarefa:** axila e flanco dos membros traseiros (área 0,306 com o quadril D à frente, igual à v10); colisões cauda/pata e lascas da cauda.
- **Limites técnicos do piloto** (não oficiais): amplitudes mantidas iguais à v9.
- **Não medido:** Roblox, PC/celular e alcateias.

### 8.14 Lote 1 de clipes: Repouso e Andar (05/11/2026). Pasta: `anim_v12/` (rig v11 preservado em `rig_v11/`); manchas corrigidas em `anim_v13/` (8.15)

**Pedido:** fazer só os clipes Repouso e Andar no Blender, sobre o rig v11 (aprovado como base deste lote, não como arte final).
- Não entram nesta etapa: Studio (registro ocupado pelo chat do Urso), corrida, ataques, controlador e regras de jogo.

**Scripts (`BLENDER/Criaturas/Lobo_Artico_Ref/`):**

| Script | Função |
|---|---|
| `clipes_v12.py` | gera os clipes em `anim_v12/CR_LoboArtico_Anim.blend` e `clipes_v12.json` |
| `auditar_clipes_v12.py` | auditoria de apoios, laço e deformação |
| `exportar_clipes_v12.py` / `reimportar_clipes_v12.py` | exporta os GLBs e valida pela reimportação |
| `vistas_clipes_v12.py` | renders com chão em grade e opção de apresentação com deslocamento |
| `prancha_clipes_v12.py` | pranchas e mosaicos dos vídeos |
| `renders_clipes_v12.sh` | lote de renders |

**Contrato: no lugar** (como no Urso v2).
- O jogo move o modelo.
- A Raiz fica fixa no chão, entre as patas, sem translação; a relação pivô→pés é a da v9.
- A frente é −Y no Blender.
- O deslocamento do corpo existe só na apresentação: o objeto anda no render, e nada disso vai para o export.

**Como os clipes são feitos:**
- IK analítico de 2 ossos, gravado em FK (quaternions em todos os quadros).
- O resto do corpo gira em eixos globais do repouso.
- Sem constraints nem drivers no export.

**Parâmetros técnicos** (ajustáveis; não são regras oficiais nem balanceamento):
- **Andar:**
  - ciclo de 1,2 s (36 quadros a 30 qps) e 3,6 studs por ciclo, ou seja, **3,0 studs/s**;
  - sequência lateral de apoios: traseira E 0 → dianteira E 0,25 → traseira D 0,5 → dianteira D 0,75;
  - fator de apoio 0,62;
  - altura do balanço 0,42 (dianteira) e 0,36 (traseira);
  - rolamento de 28°;
  - dobra no balanço de 95° (carpo) e 70° (jarrete).
- **Repouso:**
  - 8 s (240 quadros), com 2 respirações de 4 s;
  - compensação de peso lenta, com as patas presas pelo IK;
  - 1 piscada em 5,3 s;
  - contração das orelhas E (2,1 s) e D (6,4 s);
  - cauda lenta;
  - boca fechada.
- Todas as curvas são periódicas.

**Correções feitas no próprio lote:**
- **Clipes calculados sem ação atribuída.** O Repouso saía contaminado pelo Andar: o Blender reaplicava a ação a cada atualização do IK.
- **Rolamento em torno do contato dos dedos com o chão.** Na articulação, 0,3 acima do chão, ele arrastava as almofadas. O deslize caiu de 0,05–0,06 para 0,012–0,034.
- **Altura do balanço só chega a zero no toque.** Antes zerava em 87% do balanço, e a pata encostava ainda avançando (cerca de 0,13 de escorregão no pouso).
- **Rolamento desfeito entre 20% e 60% do balanço.** Antes o calcanhar voltava a tocar o chão na saída.
- **Transição técnica:** apoios passo a passo, alvo pela amplitude do meio do apoio e altura cheia já no início da rampa.

**Teste com o rig no Blender** (`review/v12_clipes/aud_clipes.json`):
- **Deslize:** medido pelos vértices que tocam o chão no meio do apoio, seguidos enquanto continuam no chão.
- **Tolerâncias técnicas:** deslize ≤ 0,03 stud, afundamento ≤ 0,03 e flutuação ≤ 0,035.

| | Andar LOD0 | Andar LOD1 | Andar LOD2 | Repouso (3 LODs) |
|---|---|---|---|---|
| deslize máximo por apoio (DE/DD/TE/TD) | 0,012 / 0,034 / 0,028 / 0,016 | 0,022 / 0,030 / 0,029 / 0,016 | 0,013 / 0,052 / 0,025 / 0,014 | ≤ 0,009 |
| afundamento máximo | 0,007 | 0,019 | 0,035 | ≤ 0,001 |
| altura máxima do balanço | 0,21–0,24 | 0,21–0,30 | 0,19–0,28 | — |
| laço: pose do q0 × último quadro | 0 | 0 | 0 | 0 |
| aceleração na emenda × máxima no clipe | 0,18 × 0,27 | 0,18 × 0,28 | 0,19 × 0,26 | 0,0003 × 0,0004 |
| boca / pálpebras fora da piscada / costura | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |

- **Velocidade de 3,0 studs/s, igual à passada:** com o corpo deslocado a 3,0, a pata apoiada fica parada no chão dentro do deslize medido (erro ≤ 0,05 studs/s num apoio de 0,74 s).
- **"Velocidade medida" pelo centro do contato:** 2,5–3,0. Subestima, porque o centro anda para a frente no rolamento almofada → dedos.
- **Marca:** a distância à pele varia no máximo 0,006.
- **Deformação no Andar** (pior quadro do ciclo):
  - garganta: 3–4 faces viradas (área 0,06–0,07; 0,22 no LOD2);
  - axila: 1–5 faces (área ≤ 0,03);
  - cauda/pata E: 1 face;
  - flanco direito: 40–77 faces (área 0,92–1,12) na prega coxa D/barriga (`Coluna2`/`Coxa_D`/`Tibia_D`), quando a traseira D avança no fim do balanço. Não aparece nos perfis, com ou sem pelo; é a pendência de flanco desde a v9.

**Transição técnica** (`Teste_Transicao`, não exportada): Repouso 2 s → rampa 0,6 s → 3 ciclos → rampa 0,6 s → Repouso 2 s.
- No andar pleno, a pata apoiada fica parada no chão.
- Nas rampas, a amplitude muda no meio do apoio: deslize de 0,05–0,10 em três patas e 0,38 na dianteira E.
- No fim, as patas param onde estavam, não na pose de repouso.
- É só um teste: a transição real é mistura no sistema de animação do jogo.

**Export e ação validada após reimportação** (`anim_v12/export/`, `reimport_clipes_v12.json`):

| GLB | MB | tris |
|---|---|---|
| `CR_LoboArtico_LOW_Clipes.glb` | 13,9 | cabeça 19.168, corpo 19.935 com o triângulo-guarda, pelagem 3.548, marca 1.352, cristais 340 |
| `CR_LoboArtico_LOD1_Clipes.glb` | 11,9 | 3.887 / 6.614 / 1.776 / 1.352 / 340 |
| `CR_LoboArtico_LOD2_Clipes.glb` | 10,1 | 1.400 / 2.043 / 340 |

- **Só as ações Andar (0–36) e Repouso (0–240)** estão no GLB; `Teste_Piloto` e `Teste_Transicao` foram removidas na sessão de export.
- **Esqueleto e canais:** 37 ossos animados, com canais de rotação, posição e escala por osso; 37 ossos, nomes e hierarquia iguais.
- **Laço:** o último quadro é igual ao primeiro (diferença 0).
- **Malhas:** até 4 influências e pesos somando 1; imagens 11 / 11 / 9; z de 0 a 7,421.
- **Deformação:** cada ação, pelo esqueleto reimportado, difere do rig original em no máximo 0,00022 stud.
- **Teste no Roblox: não realizado.** A ponte JSON → KeyframeSequence do pipeline ainda não foi gerada para estes clipes.

**Evidências (`review/v12_clipes/`):**
- **Vídeos** `LoboArtico_<nome>_normal_30qps.mp4` e `_lento_0.5x.mp4`:
  - `andar`: referência, perfil E/D, frente, traseira e 3/4; 3 ciclos com deslocamento sobre a grade;
  - `andar_closes`: patas E/D e cauda/pata E, com e sem pelo;
  - `andar_nolugar`: contrato do jogo, mais a garganta;
  - `repouso`: 8 s;
  - `lods`;
  - `transicao`.
- **Pranchas:**
  - `repouso_v11_x_v12.png`;
  - `apoios_andar.png`, com a fase de cada pata;
  - `emenda_andar.png` e `emenda_repouso.png`;
  - `repouso_sequencia.png`;
  - `transicao.png`.

**Tipos de teste:**
- ação no Blender (rig real, 3 LODs);
- ação validada após reimportação;
- **teste no Roblox: não realizado.**

**Pendências** (a 1ª bloqueia o aceite visual do Andar):
1. **Manchas escuras na face interna esquerda da cauda.**
   - O que é: a borda serrilhada do corte da v10, que ficou fora da faixa repintada e mantém o bake escuro antigo.
   - Onde aparece: num Andar normal, pelos perfis E e D (quadros 0–6 e 27–33).
   - Diagnóstico: é textura; a geometria da tampa está lisa (`tampa`, quadro 6).
   - Correção localizada proposta (aguarda aprovação): estender a repintura dos texels da cauda até a borda do corte (até 0,35 do outro lado, ou pelas faces visíveis com a pata afastada) e, se preciso, alisar mais as lascas da borda.
2. **Prega do flanco direito no Andar:** é interna e não aparece nas vistas testadas.
3. **Velocidade, cadência e passada:** são parâmetros técnicos e precisam de validação em jogo, com o controlador.
4. **Transição real:** fica para o sistema de animação.
5. **Não medidos:** Roblox, PC/celular e alcateias.

### 8.15 v13: correção das manchas escuras da cauda E (06/11/2026). Pasta: `anim_v13/` (`anim_v12/` preservado)

**Pedido:** corrigir as manchas escuras da face interna da cauda/pata traseira E que bloqueavam o aceite visual do Andar (pendência 1 da 8.14). Clipes, rig e pesos de osso não mudam.

**Diagnóstico** (o da 8.14 estava incompleto):
- Não é pelo: sem pelagem e com descarte de faces de costas a mancha continua.
- Não é normal map: com o mapa de normais desligado a mancha continua.
- **É a cor base das tampas da v10.** Com a cor base trocada por uma cor uniforme, a mancha some. As tampas (faces `lado_tampa` ≠ 0) usavam UV emprestada, um triângulo por face de referência vizinha, e essas referências eram as faces da faixa escondida com o bake escuro da fresta cauda/pata. Como os texels são compartilhados, repintar a faixa (passo 1) quase não muda a imagem.

**Passos (`BLENDER/Criaturas/Lobo_Artico_Ref/`, todos sobre `anim_v13/CR_LoboArtico_Anim.blend`; `refazer_v13.sh` refaz tudo a partir de `anim_v12/`):**

| Passo | Script | O que faz | Resultado |
|---|---|---|---|
| 1 | `textura_borda_v13.py` | repinta as faces escuras da região (luminância < 0,72 × mediana) e 1 anel, por transferência | 17 escuras, 48 repintadas; luminância 0,49 → 0,64; efeito visual pequeno |
| 2 | `lascas_v13.py` | alisa as lascas do lado da cauda escondidas no repouso, borda fixa, ≤ 0,2 | 108 / 25 / 5 vértices (LOW/LOD1/LOD2); efeito pequeno |
| 3 | `normais_tampa_v13.py` | enrolamento das tampas igual ao das vizinhas; alisa vértices internos em dobras (≤ 0,08) | arestas com enrolamento oposto 2/19/5 → 0; cantos invertidos 27/64/20 → 23/25/18 |
| 4 | `uv_tampa_v13.py` | **correção**: UV própria das tampas num quadrado vazio do atlas do corpo; texels pintados por transferência das faces limpas do mesmo lado; normal plana | quadrado livre de 46 px em (491, 0), útil 40 px; 2 retângulos (cauda/pata) de 40 × 19 px, cerca de 14 px/stud; 282 / 120 / 48 faces de tampa com UV nova |

- Os cantos ainda "invertidos" do passo 3 ficam na borda do corte, onde a tampa encontra a superfície em ângulo fechado. Depois do passo 4 não aparecem nas vistas testadas.
- A textura da tampa é mais lisa e menos detalhada que o pelo vizinho (14 px/stud). Ela só aparece na fresta entre cauda e coxa, com a pata afastada.

**Testes no Blender** (evidências em `review/v13_manchas/`):
- `manchas_andar.png`: referência | antes (v12) | depois (v13), close da cauda/pata E no Andar, quadros 0, 3 e 30, com e sem pelo. As manchas somem.
- `manchas_lods.png`: LOD1 e LOD2, antes e depois. As manchas somem nos dois.
- `repouso_v12_x_v13.png`: Repouso q0 em 5 vistas, com a diferença × 8. A diferença fica só na junção cauda/coxa E e a silhueta é igual.
- `LoboArtico_manchas_antes_depois_normal_30qps.mp4` e `_lento_0.5x.mp4`: ciclo do Andar, antes | depois, com e sem pelo.
- Auditoria dos clipes (`aud_clipes_v13.json`): dos 400 números, 394 são iguais aos do v12. A única mudança é na cauda/pata E do LOW: de 1 para 2 faces viradas, com área de 0,0002 para 0,0004. Deslize, laço, boca e costura ficam iguais

**Export e ação validada após reimportação** (`anim_v13/export/`):
- 3 GLBs com o mesmo tamanho do v12: 13,9 / 11,9 / 10,1 MB.
- Contagens iguais às do v12: corpo LOW com 19.930 tris no GLB (19.935 no Blender com o triângulo-guarda).
- Só as ações Andar e Repouso; 37 ossos; laço com diferença 0; até 4 influências; pesos somando 1; imagens de 1024.
- Desvio da reimportação × rig: ≤ 0,00022 stud.
- **Teste no Roblox: não realizado.**

**Pendências:**
- Revisão visual do usuário.
- Prega do flanco D (8.14, pendência 2) sem mudança.
- Velocidade e cadência continuam parâmetros técnicos.
- `refazer_v13.sh` foi escrito, mas não rodado de ponta a ponta: os passos foram rodados um a um.

### 8.16 v14: pelo da cauda preso na perna traseira E (06/11/2026). Pasta: `anim_v14/` (`anim_v13/` preservado)

**Relato do usuário:** no Andar, parte do pelo da cauda acompanha a perna.

**Diagnóstico em `anim_v13/`:**
- **Pelagem:** 12 cartões no LOW e 11 no LOD1 tinham peso misto, da cauda (`Cauda1`–`Cauda4`) e da perna E (`Coxa_E`/`Tibia_E`/`Metatarso_E`). A parte com peso de perna puxava o cartão com a coxa.
- **Corpo:** 106 vértices no LOW (38 no LOD1, 8 no LOD2) tinham peso misto, a maioria do lado da cauda e na base da cauda na linha média, com `Coxa_E` até 0,26.

**Correção:** `pesos_cauda_v14.py` mexe só nos pesos de osso. Geometria, UV, textura, rig e clipes ficam iguais.
- **Corpo:**
  - vértice com face do lado da cauda e nenhuma da pata: sem perna E;
  - com face da pata e nenhuma da cauda: sem cauda;
  - na base da cauda, na linha média (|x| < 0,35): sem coxas;
  - o peso retirado é dividido entre os ossos que sobram, com 2 passadas de alisamento que não trazem de volta os ossos retirados.
- **Pelagem:** todo cartão com cauda > 0,05 e qualquer peso de perna E recebe um dono, pela face do corpo mais próxima do centro do cartão; ficam só os ossos do lado do dono.
- **Corrigidos:**
  - LOW: corpo 64/37/21 vértices (cauda/pata/meio); 19 cartões;
  - LOD1: corpo 20/23/10; 14 cartões;
  - LOD2: corpo 5/8/3.
- **Resíduo:** 14 vértices no LOW, no alto do quadril, com cauda ≤ 0,05.

**Teste no Blender** (`review/v14_pelo_cauda/`):
- **Medida** `medir_pelo_cauda_v14.py` (`pelo_cauda_v13/v14.json`): afastamento máximo, no Andar, dos cartões da cauda em relação ao seu osso de cauda dominante.

  | | v13 (antes) | v14 (depois) |
  |---|---|---|
  | LOW, cartões com perna E (de 143) | 18 | **0** |
  | LOW, afastamento máximo | 0,318 | 0,090 |
  | LOD1, cartões com perna E (de 115) | 12 | **0** |
  | LOD1, afastamento máximo | 0,409 | 0,106 |

  O que sobra, ≤ 0,1, é a flexão normal entre os ossos da cauda.
- **Pranchas e vídeos:**
  - `pelo_cauda_andar.png`: referência | antes | depois; cauda_E, trás e 3/4 trás; quadros 12/24/30;
  - `pelo_cauda_lod1.png`;
  - `repouso_v13_x_v14.png`: diferença máxima de 18–37/255, só na junção; silhueta igual;
  - `LoboArtico_pelo_cauda_antes_depois_*.mp4`.
  - Visualmente, a fresta cauda/coxa fica limpa: no v13 o pelo atravessava entre a coxa e a cauda (q24–30).
- **Auditoria dos clipes** (`aud_clipes_v14.json`): deslize, laço, boca e costura iguais. Só a região cauda/pata E mudou:

  | Cauda/pata E | v13 | v14 |
  |---|---|---|
  | LOW, faces viradas | 2 | 4 |
  | LOW, área | 0,0004 | 0,0127 |
  | LOW, faces esticadas > 2× | 1 | 5 |
  | LOD1, faces viradas | 1 | 2 |
  | LOD1, área | 0,003 | 0,012 |

  É a fronteira mais dura de pesos na base da cauda; a área é pequena e não apareceu nas vistas.

**Export e ação validada após reimportação** (`anim_v14/export/`):
- 3 GLBs: 13,9 / 11,9 / 10,1 MB.
- Contagens iguais às do v12/v13.
- Só Andar e Repouso; 37 ossos; laço com diferença 0; até 4 influências; desvio ≤ 0,00022.
- **Teste no Roblox: não realizado.**

### 8.17 v15: cartões de pelo da perna E sobre a cauda + vídeos de revisão legíveis (06/11/2026). Pasta: `anim_v15/` (`anim_v14/` preservado)

**Relato do usuário:** no vídeo da v14 não dava para ver direito o "depois".

**Vídeos novos** (`vistas_pelo_cauda_v14.py` e `video_pelo_cauda_v14.py`):
- Câmera parada e fechada na fresta cauda/coxa E (vistas `fresta_E`, `fresta_tras`, `fresta_baixo`), clipe no lugar, fundo escuro.
- Cada lado tem 960 × 720, com rótulos grandes ANTES | DEPOIS.
- Modo **cores** (Workbench), pelo osso dominante de cada vértice:
  - laranja = cauda;
  - azul = perna traseira E;
  - cinza = resto.

**O que o modo cores mostrou:** um resto do defeito que a v14 não pegava.
- Cartões de pelo da **perna** E, com raiz na coxa e peso 100% perna, se estendiam por cima da cauda: 16 no LOW, 8 deles com metade ou mais sobre a cauda.
- No Andar eles deslizam sobre a cauda junto com a perna.

**Correção:** `pelo_fresta_v15.py`, só na geometria e nos pesos dos cartões de pelo; corpo, UV, rig e clipes iguais.
- Cartão de um lado com vértice sobre o outro lado (pela face do corpo mais próxima, atributo `classe_cauda`): encolhe em direção à raiz até não cruzar, no mínimo até 0,35.
- Se ainda cruza e está majoritariamente do outro lado (nasce na fresta): volta ao tamanho original e passa de lado, com o peso do corpo do outro lado mais perto da raiz.
- O peso é aplicado depois do `to_mesh`, porque o bmesh sobrescrevia os grupos.

| | LOW | LOD1 |
|---|---|---|
| Perna sobre cauda, cartões encolhidos | 10 (média 0,61) | 9 (média 0,58) |
| Perna sobre cauda, cartões que passaram para a cauda | 6 | 1 |
| Cauda sobre perna, cartões encolhidos | 2 | 3 |
| Cauda sobre perna, cartões que passaram para a perna | 0 | 1 |
| Cartões de perna E sobre a cauda, antes → depois | 16 → 2 | 10 → 1 |

Os cartões que restam estão encolhidos a 0,35, com 1/3 dos vértices sobre a cauda.

**Teste no Blender** (`review/v14_pelo_cauda/revisao/`):
- `Pelo_cauda_v15_cores_fresta_*` e `Pelo_cauda_v15_real_fresta_*`, `_lento_0.5x.mp4` e `_normal_30qps.mp4`: v13 (antes) | v15 (depois), 3 ciclos.
- `prancha_v15_cores_fresta_E.png` e `prancha_v15_real_fresta_E.png`: quadros 6/18/24/30.
- Cartões da cauda com peso de perna E: 0 no LOW e no LOD1.
- Afastamento máximo dos cartões da cauda em relação à cauda: 0,090 no LOW e 0,106 no LOD1 (flexão normal da cauda).
- Auditoria dos clipes: igual à da v14 (0 números diferentes).
- **Visual:**
  - quadros 6, 24 e 30: fresta limpa;
  - quadro 18: ainda há uma faixa fina de pelo da perna na borda da cauda, onde a coxa encosta na cauda no balanço.

**Ação validada após reimportação** (`anim_v15/export/`):
- 3 GLBs: 13,9 / 11,9 / 10,1 MB; pelagem com 3.548 / 1.776 tris, iguais às da v14.
- Só Andar e Repouso; 37 ossos; laço com diferença 0; desvio ≤ 0,00022.
- **Teste no Roblox: não realizado.**

### 8.18 Diagnóstico: lobo da cauda do lado da perna (corte da v10 no lugar errado) (06/11/2026). Pastas: `anim_v16a/`, `anim_v16/` (tentativa só de pesos, NÃO aceita)

**Relato do usuário (print da v15):** "ainda gruda na perna".

**Diagnóstico** (`review/v16_lobo/diagnostico_lobo_v16.png`):
- O lado "pata" do corte da v10 (`classe_cauda` = +1) contém **um lobo inteiro da cauda**: uma faixa comprida com pelo de cauda, entre a tampa da pata e um vinco fundo junto à coxa.
- Esse lobo é pesado em `Coxa_E`/`Tibia_E` e, no Andar, vai com a perna. É ele o "pelo da cauda grudado na perna" do print.
- Causa: as sementes geodésicas da v10 deixaram a linha de igual distância (cauda × pata) entre o lobo e o resto da cauda. Ela deveria passar no vinco da coxa.
- As correções v14 (pesos) e v15 (cartões que cruzam a fresta) estavam certas no que mediam, mas não tocavam no lobo, que é malha do corpo.

**Tentativa só de pesos** (`lobo_cauda_v16.py`, depois `pelo_fresta_v15.py`; `anim_v14` → `anim_v16a` → `anim_v16`):
- Lobo isolado por distância geodésica: mais perto da tampa da pata do que da fronteira com o corpo. São 318 / 124 / 30 vértices (LOW / LOD1 / LOD2).
- O lobo recebe o peso da face interna da cauda, com transição suave no vinco (T0 0,3); os cartões de pelo do lobo vão com ele (39 / 28).
- **Resultado no Blender:**
  - o lobo segue a cauda;
  - mas o lobo continua ligado à coxa ao longo de todo o vinco, e com a perna à frente (q33) essa pele estica numa **membrana** coxa → cauda;
  - pesos sozinhos não resolvem.
- **Não aceita.** Não foi exportada.

**Correção proposta (aguarda aprovação):** refazer o corte da v10 no vinco da coxa, com o lobo do lado da cauda.
- Mudar a classificação de `separar_cauda_v10.py` numa versão nova: semente de cauda no lobo, ou desvio da linha G.
- Descolar a pele no vinco, com tampas, UV e pesos pelo mesmo método.
- Refazer em cascata, preservando as versões atuais:
  - garganta v11;
  - clipes do lote 1;
  - v13 (UV das tampas);
  - v14 (pesos);
  - v15 (cartões).
- Depois: export, reimportação e vídeos de revisão (close + cores).
- Risco: mexe na base aprovada (v10/v11); o orçamento de tris (LOD0 19.935) tem pouca folga para tampas maiores.

### 8.19 v17: corte cauda × coxa E refeito no vinco da coxa + cascata completa (06/11/2026). Pasta: `anim_v17/` (atual: `anim_v20/`, 8.20)

**Pedido do usuário:** "Sim, refazer o corte" (proposta da 8.18).

**Preservado:** `rig_v9` a `rig_v11` e `anim_v12` a `anim_v16`, todos intactos.

**Pastas novas:** `rig_v17/` → `rig_v17_garganta/` → `anim_v17_clipes/` → `anim_v17_tampas/` → `anim_v17_pesos/` → `anim_v17/`.

**Scripts:**
- `exportar_lobo_v17.py`: pontos do lobo diagnosticado na 8.18, salvos em `corte_v17/lobo_pontos.json`.
- `separar_cauda_v17.py`: cópia do `separar_cauda_v10.py` com o mesmo método de descolar, tampa, UV, pesos e pelagem. Mudanças:
  1. As faces do lado "pata" que coincidem com o lobo passam para o lado da cauda: 372 / 142 / 19 faces (LOW / LOD1 / LOD2). No LOD2, usa o lobo do LOW pelo centro da face, com raio 0,05.
  2. Cada classe fica com um componente só: as ilhas soltas são trocadas.
  3. Os furos pequenos fechados que o corte deixa (uma pinça no tubo da pele) são fechados com face própria: 1 por lado no LOW, 1 na pata no LOD1.
  4. A tampa principal é feita pela cadeia que tem as duas pontas.
- `refazer_v17.sh`: refaz tudo a partir da v9, rodado de ponta a ponta.

**Cascata** (mesmos scripts das versões anteriores):
- textura e ação da v10;
- garganta da v11;
- clipes Repouso/Andar da v12;
- borda, lascas, enrolamento e UV própria das tampas da v13;
- pesos da v14;
- cartões na fresta da v15.

**Resultado do corte** (`rig_v17/rig_v10.json`):

| | LOW | LOD1 | LOD2 |
|---|---|---|---|
| Arestas cortadas | 75 | 52 | 19 |
| Tris do corpo no Blender | 19.934 | 6.613 | 2.042 |

- Vértices sem peso: 0.
- Pesos do outro lado abaixo da raiz: 0.

**Teste no Blender** (`review/v17_corte/`):
- **Vídeos** `revisao/Pelo_cauda_v17_{cores,real}_fresta_{E,tras,baixo}_{lento_0.5x,normal_30qps}.mp4`: antes (v13) | depois (v17), câmera fechada, 3 ciclos. No modo cores, laranja = cauda e azul = perna E.
  - O lobo agora é cauda: não anda mais com a perna.
  - A fronteira perna | cauda fica no vinco da coxa, nos quadros 6, 18, 27 e 33.
  - Não há a membrana da v16.
- **Auditoria dos clipes** (`aud_clipes_v17.json`) × v15:
  - cauda/pata E: faces viradas 4 → 1, área 0,0127 → 0,0002;
  - aceleração na emenda do laço: 0,18 → 0,14;
  - deslize, afundamento, boca e costura iguais.
- **Cartões de pelo** (`pelo_cauda_v17.json`): 177 cartões de cauda no LOW e 138 no LOD1, agora incluindo os do lobo.
  - Com peso de perna E: 0.
  - Afastamento máximo: 0,13 / 0,12. É a flexão da cauda, que agora tem o lobo junto.
- **Resto visível:** com a perna bem à frente (q33), a tampa da fresta aparece como uma superfície mais escura na sombra entre a coxa e a cauda.

**Ação validada após reimportação** (`anim_v17/export/`):
- 3 GLBs: 13,9 / 11,9 / 10,1 MB.
- Corpo no GLB: 19.920 / 6.606 / 2.041 tris; pelagem: 3.548 / 1.776.
- Só Andar e Repouso; 37 ossos; laço com diferença 0; até 4 influências; 0 vértices sem influência; desvio ≤ 0,00022.
- **Teste no Roblox: não realizado.**

### 8.20 v18 a v20: a "mecha fina" que sobrou junto da perna E (06/11/2026). Versão atual: `anim_v20/`

**Relato do usuário (print da v17):** "ainda tem uma leve mecha grudada na perna".

**Diagnóstico** (renders em cores, `classe_cauda` e osso dominante):
- A tira fina é **azul**: é a **borda de trás da própria coxa E**.
- Um sulco fundo do modelo do Meshy separa essa borda do resto da coxa.
- Ela anda com a perna porque é perna, mas parece uma mecha solta.

**v18** (`separar_cauda_v18.py`, `refazer_v18.sh`; `rig_v18*/`, `anim_v18*/`): o corte da v17 entra 1 anel a mais no vinco, a "crista", com 130 faces no LOW e 77 no LOD1.
- Com 3 ou mais anéis a borda vira várias cadeias e a tampa não fecha; no LOD2 já 1 anel quebra a tampa.
- Auditoria igual à da v17.
- A tira diminui, mas continua.

**v19** (`parede_vinco_v19.py`, `anim_v19/`): **descartada**.
- Tentou tratar a parede do vinco por peso, com a borda do corte seguindo a cauda.
- Arrastava a tampa da perna: faces esticadas no q33.

**v20** (`sulco_coxa_v20.py`, `refazer_v20.sh`; `anim_v18` → `anim_v20`): **rasa o sulco**.
- Alisa a pele do lado da perna a menos de 0,6 (geodésica) da borda do corte.
- 24 passadas, deslocamento ≤ 0,3; a tampa da perna é relaxada junto.
- Vértices alisados: 232 / 96 / 41 (LOW / LOD1 / LOD2).
- 51 / 36 cartões de pelo com raiz na faixa foram transladados junto com a pele.
- Pesos, UV, rig e clipes iguais.

**Teste no Blender** (`review/v20_sulco/`):
- `fresta_v18_x_v20_close.png` e `revisao/Pelo_cauda_v20_{real,cores}_fresta_{E,tras,baixo}_*.mp4`, antes (v18) | depois (v20):
  - a borda de trás da coxa se junta à coxa;
  - fica uma fresta só entre a coxa e a cauda;
  - a tira solta some na maior parte.
- `repouso_v18_x_v20.png`: silhueta igual; a diferença aparece só dentro da fresta, de 25 a 53/255 nas 5 vistas.
- Auditoria × v18, cauda/pata E do LOW:

  | | v18 | v20 |
  |---|---|---|
  | Faces viradas | 1 | 0 |
  | Faces esticadas > 2× | 1 | 13 |

  As faces esticadas ficam na faixa alisada, dentro da fresta. O resto da auditoria é igual.
- Cartões da cauda com peso de perna E: 0.

**Ação validada após reimportação** (`anim_v20/export/`):
- 3 GLBs: 13,9 / 11,9 / 10,1 MB.
- Corpo: 19.932 / 6.611 / 2.041 tris.
- Só Andar e Repouso; 37 ossos; laço com diferença 0; desvio ≤ 0,00022.
- **Teste no Roblox: não realizado.**

### 8.21 Lote 1 (Repouso + Andar) APROVADO pelo usuário (09/11/2026)

- **Aprovação:** o usuário respondeu "Aprovar lote 1" depois da revisão da v20 (8.20).
- **Base oficial do lote 1:** `anim_v20/` e `anim_v20/export/CR_LoboArtico_{LOW,LOD1,LOD2}_Clipes.glb` (só Andar e Repouso, 37 ossos).
- **Reprodução:** `refazer_v17.sh` → `refazer_v18.sh` → `refazer_v20.sh`, a partir do `rig_v9`.
- **Aprovado:** aceite visual no Blender (clipes, cauda e fresta).
- **Ainda NÃO testado:**
  - Roblox: não há ponte JSON → KeyframeSequence nem Studio, e o Studio exige reserva em `DOCS/estado/studio-em-uso.md`;
  - PC/celular;
  - controlador e velocidade em jogo, que continuam como parâmetros técnicos.
- **Pendências que seguem:** a prega interna do flanco D e as 13 faces esticadas dentro da fresta (8.20).
- **Próximo passo, aguardando aprovação:** planejar o lote 2 de clipes.

### 8.22 PLANO do lote 2 de clipes: locomoção e transições (09/11/2026, AGUARDANDO APROVAÇÃO; nada implementado)

**Base:** `anim_v20/` (lote 1 aprovado). Os clipes novos são acrescentados como ações nessa malha já corrigida, numa pasta nova `anim_v21/`. A `anim_v20/` só é lida. Não se regera a partir do rig: isso perderia as correções v13–v20.

**Contrato do lote 1, mantido:**
- clipes no lugar: Raiz fixa, frente −Y;
- IK analítico gravado em FK;
- sem constraints;
- velocidades são parâmetros técnicos, não regras;
- o jogo move o modelo e pode escalar a velocidade de reprodução.

**Clipes propostos** (todos no chão; referência de estilo: só os princípios de fluidez de `padrao-movimento-criaturas`):

| Etapa | Clipe | Tipo | Proposta técnica (ajustável) |
|---|---|---|---|
| L2a | **Trote** | laço | pares diagonais (DE+TD / DD+TE), apoio ~0,40, ciclo ~0,6 s, passada ~3,6 → ~6 studs/s |
| L2a | **Corrida** (galope de perseguição) | laço | galope rotatório de lobo: coluna flexiona e estende, fase de suspensão, cabeça baixa e estável, cauda em contrapeso; ciclo ~0,5 s, passada ~6–7 → ~12–14 studs/s naturais |
| L2b | **Arrancada** (Repouso → Corrida) | transição | agachamento e impulso das traseiras, patas escalonadas |
| L2b | **Frenagem** (Corrida → Repouso) | transição | traseiras sob o corpo, apoio das dianteiras, passos de acomodação |
| L2b | **VirarEsquerda / VirarDireita** | laço | giro no lugar com passos, pivô entre as patas, ~±45°/s técnicos |
| L2b | **Andar↔Trote**, **Trote↔Corrida** | transições | 4 clipes curtos, para não depender só de crossfade |

**Saídas:**
- `clipes_v21.py` (gerador sobre `anim_v20`);
- `clipes_v21.json`, com sincronização: velocidade natural, deslocamento por quadro nas transições e quadro de entrada sugerido;
- `emendas_v21.json`;
- auditoria, export e reimportação com os scripts do lote 1;
- GLBs só com as ações finais.

**Critérios de aceite:**
- **Deslize** do pé apoiado ≤ 0,03, como no lote 1. No galope vale o apoio real; a suspensão não conta.
- **Laços** com diferença 0 e emenda suave.
- **Deformação** sem piora frente ao Andar. Nas extensões grandes da coxa, conferir em especial:
  - a **fresta cauda × coxa E** (risco principal; vídeo em cores com close);
  - a garganta, com a cabeça baixa na corrida;
  - a prega do flanco D.
- **Patas:** sem atravessar o chão, sem dedos invertidos e sem cruzar as patas no trote.
- **Reimportação:** 37 ossos e desvio ≤ 0,001.

**Evidências** (`review/v21_lote2/`):
- referência | clipe;
- MP4 normal e 0,5x de cada clipe, com deslocamento sobre a grade e no lugar;
- perfil E/D, frente, trás, 3/4 e patas;
- vídeo da fresta em modo real e em cores;
- prancha de apoios por fase;
- LOD1/LOD2.

**Ordem:**
1. L2a (Trote + Corrida), depois **parada para revisão**.
2. L2b (arrancada, frenagem, viradas e transições), depois **parada para revisão**.

**Fora deste lote:** ataques (mordidas e garras), Uivo, Salto Predatório, Investida, Instinto de Caça, Deitar/Descanso, Comer, Morte, montaria, nado, filhotes, IA, sons, VFX, Studio/Roblox e regras de jogo.

**Decisões do usuário:**
1. Corrida: galope rotatório real de lobo (proposto) ou outro estilo.
2. Velocidade: a proposta NÃO aprovada da 24.2 diz 35 studs/s em terra. Seria uma passada de ~17 studs por ciclo para um animal de ~7 de cernelha, irreal visualmente. Proposta: o clipe tem a velocidade natural (~12–14) e o jogo escala a reprodução e o deslocamento, se a regra final for maior.
3. Incluir o Trote (proposto) ou ir direto Andar → Corrida.
4. Nado: fica fora (a locomoção oficial é terrestre; a velocidade na água é só proposta).

**Riscos:**
- extensão da coxa na corrida pode reabrir a fresta ou a cauda pode entrar na coxa;
- cabeça baixa forçando a garganta;
- muitos clipes de uma vez: por isso a divisão L2a/L2b.

### 8.23 Lote 2, etapa L2a: Trote e Corrida (09/11/2026). Pasta: `anim_v21/` (`anim_v20/` preservado, só lido)

**Pedido do usuário:**
- Incluir o Trote e a Corrida em galope natural de lobo; nado fora; só a L2a.
- As velocidades são parâmetros iniciais, a ajustar pela passada e pela cadência demonstradas.
- Não descartar 35 studs/s sem medir.
- Deslize ≤ 0,03.
- Corpo inteiro em velocidade normal e lenta, e closes em cores da fresta, da garganta e do flanco D.
- Diagnóstico antes de ampliar qualquer correção. Sem Studio e sem commit.

**Scripts (`BLENDER/Criaturas/Lobo_Artico_Ref/`):**

| Script | Função |
|---|---|
| `marcha_v21.py` | funções do lote 1 generalizadas para qualquer cronograma de marcha |
| `alcance_v21.py` | alcance de cada pata no chão |
| `clipes_v21.py` | gera Trote e Corrida sobre a `anim_v20` e grava `clipes_v21.json` |
| `auditar_clipes_v21.py` | auditoria por marcha (inclui a região `flanco_D`) |
| `vistas_clipes_v21.py` | renders de corpo inteiro |
| `vistas_closes_v21.py` | closes reais e em cores pela mistura de pesos por grupo de ossos |
| `prancha_lote2_v21.py`, `renders_v21.sh` | pranchas, vídeos e lote de renders |
| `exportar_clipes_v21.py` / `reimportar_clipes_v21.py` | export e validação com 4 ações |

**Alcance medido** (`review/v21_lote2/alcance_v21.json`; perna ≤ 97% esticada; frente / trás em studs):

| Quadril | DE | DD | TE | TD |
|---|---|---|---|---|
| na altura do repouso | 1,2 / 0,5 | 1,2 / 0,6 | 1,0 / 1,2 | 1,9 / 1,2 |
| 0,6 abaixo | 2,3 / 1,5 | 2,2 / 1,6 | 2,0 / 2,2 | 2,7 / 2,1 |

- A traseira E fica ~0,5 mais atrás que a D: assimetria herdada da pose.

**Parâmetros técnicos** (não são regras):

| | Trote | Corrida (galope rotatório) |
|---|---|---|
| Cronograma | pares diagonais DE+TD / DD+TE | TE 0 → TD 0,08 → DD 0,30 → DE 0,40 |
| Apoio por pata | 0,40 | 0,28; suspensão recolhida ~32% |
| Ciclo | 0,600 s (18 quadros), 1,67 Hz | 0,467 s (14 quadros), 2,14 Hz |
| Passada | 4,0 por ciclo; varredura no apoio 1,6 | 9,5 por ciclo; varredura no apoio 2,66 |
| **Velocidade demonstrada** | **6,67 studs/s** | **20,36 studs/s** |
| Quadril | −0,12 | −0,32 ± 0,16 (mais alto na suspensão) |
| Rolamento no fim do apoio | 15° | 20° |

- **Corrida:**
  - a coluna flexiona na suspensão e estende no impulso;
  - a extensão é compensada pela inclinação do quadril, para o dorso estender sem erguer os ombros: sem isso, as dianteiras não alcançavam o chão (erro de IK de 0,40);
  - a arfagem só baixa a frente;
  - a cabeça fica baixa e estabilizada pelo pescoço;
  - a cauda fica estendida em contrapeso e as orelhas para trás.
- **Erro de IK:** 0 nas duas marchas. A maior extensão de perna é de 0,989, na DD ao pousar no galope.
- **Rolamento:** com 30–35° o contato das almofadas deslizava 0,032–0,036. Com 0° o deslize zera; 15° e 20° mantêm o calcanhar subindo dentro do limite.

**Sobre 35 studs/s (medido, não presumido):**
- Com este rig, a varredura no apoio chega a ~4,0 com o quadril 0,6 abaixo.
- Com o apoio e a cadência atuais, isso dá ~30 studs/s.
- 35 studs/s exigiria ~2,5 Hz com corpo bem baixo, ou apoio por pata ~0,22. Parece possível, mas **não foi testado**.
- Acelerar a reprodução não foi assumido como solução.

**Teste com o rig no Blender** (`review/v21_lote2/aud_clipes_v21.json`, 3 LODs). Deslize máximo por pata (DE / DD / TE / TD):

| | LOW | LOD1 | LOD2 |
|---|---|---|---|
| Trote | 0,012 / 0,022 / 0,020 / 0,019 | 0,013 / 0,020 / 0,021 / 0,019 | 0,014 / **0,037** / 0,024 / 0,017 |
| Corrida | 0,000 / 0,021 / 0,012 / 0,018 | 0,014 / 0,020 / 0,012 / 0,018 | 0,001 / 0,018 / **0,037** / 0,016 |
| Andar (lote 1, remedido) | 0,012 / 0,034 / 0,028 / **0,034** | 0,022 / 0,030 / 0,029 / 0,035 | 0,013 / 0,045 / 0,025 / 0,031 |

- **LOD2:** a DD do Trote e a TE da Corrida não mudam nem com rolamento 0. A causa é a pata do LOD2 (malha grosseira e pesos da sola), e não o clipe. O Andar aprovado já tinha 0,044 ali.
- **Correção da auditoria do lote 1:** o apoio que cruza a emenda do laço era contado em dois pedaços. Com o apoio inteiro, o Andar mede TD 0,034 (antes relatado 0,016). Os outros números do lote 1 não mudam.
- **Afundamento:** ≤ 0,025.
- **Laço:** diferença 0. A aceleração na emenda é menor que a máxima dentro do clipe: 0,81× no Trote e 0,66× na Corrida.
- **Velocidade medida pelo centro do contato:** Trote 5,7 e Corrida 18,3. Subestima, como no lote 1, porque o centro anda no rolamento. A prova do deslocamento equivalente é o deslize ≤ 0,022 com o corpo andando à velocidade do clipe.
- **Deformação** (pior quadro do ciclo, LOW; faces viradas / área):

| | Andar | Trote | Corrida |
|---|---|---|---|
| Garganta | 3 / 0,06 | 19 / 0,17 | 73 / 1,08 (q12) |
| Flanco D | 45 / 0,75 | 50 / 0,80 | 83 / 1,20 (q12) |
| Fresta cauda/coxa E | 0 | 7 / 0,011 | 22 / 0,050 |
| Axila | 5 / 0,03 | 0 | 19 / 0,15 |
| Resto | 37 / 0,37 | 85 / 0,79 | 267 / 2,20 (q12, barriga) |

**Diagnóstico da deformação na Corrida** (sem correção, aguardando decisão):
- O pior quadro é o q12, a suspensão recolhida: a coluna flexiona e as traseiras vêm para baixo do ventre.
- As faces viradas ficam na **pele de baixo da barriga** (x ≈ 0, z 2–3), na pele da coxa encostada no ventre e na garganta comprimida.
- **Nas vistas:**
  - closes da fresta, da garganta e do flanco D, em cores e real: sem rasgo nem colisão visível;
  - vista de baixo da barriga (`barriga`): pele amassada, sem buraco;
  - a **prega do flanco D**, pendência desde a v9, abre mais e aparece como uma superfície esticada entre a coxa D e a barriga, vista de baixo, no Trote (q6) e na Corrida (q6/q10). Não aparece nos perfis.

**Ação validada após reimportação** (`anim_v21/export/`, `reimport_clipes_v21.json`):
- 3 GLBs: 14,0 / 12,0 / 10,2 MB, com Repouso, Andar, Trote (0–18) e Corrida (0–14).
- 37 ossos, nomes e hierarquia iguais; laço com diferença 0; até 4 influências; pesos somando 1.
- Desvio ≤ 0,00034 stud.
- Corpo: 19.932 / 6.611 / 2.041 tris.
- **Teste no Roblox: não realizado.**

**Evidências (`review/v21_lote2/`):**
- vídeos `LoboArtico_<nome>_normal_30qps.mp4` e `_lento_0.5x.mp4`, 3 ciclos:
  - `corpo_Trote` e `corpo_Corrida`: referência, perfil E/D, frente, trás e 3/4, com deslocamento sobre a grade;
  - `nolugar_*`: contrato do jogo, mais as patas;
  - `closes_cores_*` e `closes_real_*`: fresta, garganta e flanco D;
  - `lods`;
- pranchas `apoios_Trote.png` e `apoios_Corrida.png`, com a fase de cada pata;
- `closes_comparacao_{real,cores}.png`: Andar × Trote × Corrida nos piores quadros;
- closes `barriga`.

**Pendências e decisões:**
1. Prega do flanco D e barriga na suspensão da Corrida: aceitar ou propor uma correção localizada de pesos? Diagnóstico acima.
2. Deslize de 0,037 no LOD2 (pata do LOD2): aceitar no LOD de longe ou corrigir os pesos da sola no LOD2?
3. Velocidade final de jogo: Corrida demonstrada a 20,4 studs/s; teste de uma passada maior se a regra pedir ~35.
4. L2b (arrancada, frenagem, viradas, transições) só depois da aprovação da L2a.

### 8.24 v22: flanco direito / ventre na locomoção — diagnóstico e correção de pesos parcial (09/11/2026). Pastas: `anim_v22/` (intermediária, NÃO exportada); `anim_v21/` preservada

**Pedido do usuário:**
- Correção localizada dos pesos do flanco D e do ventre, mais o acompanhamento dos cartões de pelo.
- Se o problema exigir corte ou reconstrução de malha, parar depois do diagnóstico e propor.
- Não iniciar a L2b.

**M0:** a versão mais recente é a `anim_v21/` (09/11). Ela foi só lida.

**Scripts:**

| Script | Função |
|---|---|
| `diag_flanco_v22.py` | faces viradas, arestas esticadas > 1,8× e > 2,5× por composição de pesos, interpenetração na coxa D e degraus de peso |
| `diag_vistas_v22.py` | vistas real, sem pelo, arame e mapa de pesos: barriga, flanco D, virilha D e traseira de baixo |
| `pesos_flanco_v22.py` | correção de pesos em faixa, só no lado D |
| `prancha_flanco_v22.py` | prancha do diagnóstico |

**Diagnóstico** (`review/v22_flanco/diagnostico_flanco_v22.png`; `diag/` com os modos real, sem pelo, arame e pesos):

| Problema | Causa | Correção nesta rodada | Evidência | Pendência |
|---|---|---|---|---|
| Membrana lisa entre a coxa D e a barriga (Trote q6, vista de baixo) | **Geometria:** um leque de triângulos-agulha do Meshy na junção coxa D × barriga (LOW 21, até 0,66 de comprimento e proporção 15:1; LOD1 11; LOD2 1), já fino e sem pelo no repouso, que estica quando a perna vai para trás | pesos gradeados (`anim_v22`): a membrana **continua** | `agulhas_*`, `real_LOW_Trote_barriga_q0006` v21 × v22 | precisa de retopologia local: **aguarda autorização** |
| Fronteira abrupta de peso (1–2 anéis) Coluna1/2 × Coxa_D+Tibia_D, com Tíbia na pele da prega junto à barriga | pesos herdados do rig | faixa ±0,45 em torno da linha onde a perna D cruza 0,5 de peso: Tibia→Coxa_D a menos de 0,3 da barriga, 25 passadas de difusão, âncoras fixas fora da faixa (LOW 192 vértices, 24 cartões; LOD1 99 e 16; LOD2 29) | mapa de pesos v21 × v22 | — |
| Coxa D entrando na barriga com a perna à frente (Corrida q8–q12, Andar q14) | fronteira abrupta mais o leque de agulhas | parcial (mesma correção de pesos) | ver números abaixo | depende da retopologia |
| Faixa escura entre a coxa e a barriga na Corrida | textura da parte de baixo da barriga, que fica à mostra (igual no repouso) | — | `real_*_virilha_D` | não é defeito de malha |
| Arestas esticadas no peito, entre as dianteiras (Coluna2+Úmero) | outra região (axila e esterno); igual no Andar aprovado | fora do escopo | `diag_flanco` | registrar |

**Malha:** a pele da coxa e a da barriga são contínuas, sem furo nem fusão anômala. O problema é o leque de agulhas, uma topologia ruim numa prega legítima do flanco.

**Números (LOW, região do flanco e ventre, v21 → v22 só pesos):**

| Quadro | Faces viradas (área) | Arestas > 1,8× | Vértices dentro da coxa D |
|---|---|---|---|
| Trote q6 | 24 (0,12) → 21 (0,10) | 116 → 110 | 25 → 33 |
| Corrida q8 | 130 (1,60) → 81 (0,85) | 82 → 75 | 43 → 23 |
| Corrida q10 | 127 (1,65) → 102 (1,64) | 108 → 87 | 56 → 32 |
| Corrida q12 | 257 (2,35) → 241 (2,44) | 148 → 123 | 80 → 47 |
| Andar q14 | 81 (1,15) → 42 (0,75) | 90 → 82 | 35 → 21 |

- A redução das contagens não remove a membrana visível.
- **A v22 não é dada como resolvida e não foi exportada.**

**Proposta (aguarda autorização: é mudança de malha):** retopologia local do leque de agulhas nos 3 LODs.
1. Girar as arestas longas (beautify), dividir as agulhas mais longas e relaxar as posições dentro da prega, com a silhueta de repouso preservada (diferença medida).
2. Orçamento: o LOW tem 19.932 tris no GLB, ou seja, até +68 tris; LOD1 e LOD2 têm folga.
3. UV pelo ponto mais próximo, o mesmo método das tampas.
4. Pesos da `v22` reaplicados, mais os cartões da região.
5. Depois: auditoria completa (fresta, garganta, apoios, laços, boca, marca, costura) e export/reimportação com as 4 ações.

**Pendências registradas sem mexer:**
- deslize de 0,037 no LOD2 (Trote DD, Corrida TE);
- Andar remedido acima de 0,03 (LOW DD e TD 0,034; LOD1 TD 0,035; LOD2 DD 0,045).
- O critério de 0,03 continua valendo; nada foi aceito por distância.
- Roblox e desempenho em PC/celular/alcateias: não testados.

### 8.25 v23: retopologia localizada da prega coxa D × ventre (10/11/2026). Pasta exportada: `anim_v23/`; intermediária `anim_v23_topo/`; `anim_v21/` e `anim_v22/` preservadas

**Pedido:** `DOCS/pedidos/2026-11-10-lobo-artico-v22-retopologia-flanco.md`. Ele autoriza corrigir a topologia local nos 3 LODs. Não autoriza iniciar a L2b nem acessar o Studio.

**M0:** a versão mais recente era a `anim_v22/`. Não havia v23.

**Scripts novos (reproduzíveis):**

| Script | Função |
|---|---|
| `agulhas_v23.py` | mapa, só leitura, das agulhas por LOD (aresta > 0,35 e proporção > 6) |
| `retopo_flanco_v23.py` | `anim_v21` → `anim_v23_topo`: remendo, remalha, UV própria, texels, pesos v21 interpolados e cartões |
| `metricas_flanco_v23.py` | métricas independentes da topologia, com varredura de todos os quadros |
| `diag_vistas_v23.py` | cópia da `diag_vistas_v22` com o modo `dobras` e vistas de corpo inteiro |
| `renders_v23.sh` | renders com as mesmas câmeras na v21, na v22 e na v23 |
| `prancha_flanco_v23.py` | pranchas e mosaicos de vídeo |

**Cadeia:**
1. `retopo_flanco_v23.py` (`anim_v21` → `anim_v23_topo`).
2. `pesos_flanco_v22.py` sem mudança, aplicado sobre `anim_v23_topo` (saída `anim_v23`).
3. `exportar_clipes_v21.py` e `reimportar_clipes_v21.py` em `anim_v23/export/`.

**Método:**
- **Remendo:** agulhas do núcleo dentro da caixa da prega, mais as faces a menos de R (geodésico) delas. Só entra pele, fora do corte cauda/pata e longe da pata E. A borda fica fixa, então o resto da malha não muda.
- **Remalha isotrópica dentro do remendo:**
  - dividir, colapsar e girar arestas pelo critério de Delaunay, desde que fiquem coladas na superfície;
  - relaxar tangencialmente e projetar na superfície **original** do próprio LOD, com teste de normal para não atravessar a prega;
  - limpeza dirigida dos triângulos com proporção > 4;
  - o script é determinístico: a ordem é feita por índices.
- **UV:** o atlas do Meshy tem cerca de 4 faces por ilha (o LOW tem 5.080 ilhas), então não dá para remalhar dentro das ilhas.
  - Cada LOD ganha uma ilha **própria**: LSCM, sem dobra, num retângulo livre do atlas (livre em todos os LODs, margem de 3 px), na densidade do corpo daquele LOD.
  - Texels transferidos da superfície **original do próprio remendo**: cor, rugosidade e emissão; o normal map é convertido entre os espaços tangentes usando a normal **suave** interpolada.
  - A 1ª versão, com normal plana por face, gerava listras escuras e foi corrigida.
- **Pesos:**
  - os vértices novos recebem os pesos v21 interpolados no ponto de origem;
  - depois vem a faixa gradeada da v22, reavaliada nesta topologia;
  - variantes comparadas: só topologia; faixa da v22; faixa estreita (W 0,3 e 15 passadas); Tíbia→Coxa só junto à barriga. Esta última piorou as dobras da Corrida q12 (0,26 → 0,32) e foi descartada.
- **Cartões:** os da raiz no remendo foram levados à pele nova (translação máxima de 0,015) e repesados (LOW 5, LOD1 1). Depois a faixa repesou LOW 23 e LOD1 16.

**Topologia e custo (repouso):**

| LOD | Faces do remendo | Agulhas | Proporção > 4 | Proporção máx. | Ângulo mín. | Tris do corpo (fonte → v23) | Tris no GLB | Desvio da superfície original (médio / máx.) |
|---|---|---|---|---|---|---|---|---|
| LOW | 130 → 154 | 14 → 0 | 29 → 1 | 29,3 → 5,5 | 2,5° → 15,3° | 19.932 → 19.956 | 19.957 (teto 20.000; folga de 43) | 0,009 / 0,076 |
| LOD1 | 47 → 41 | 1 → 0 | 4 → 0 | 6,5 → 2,7 | 10,4° → 31,9° | 6.613 → 6.607 | 6.608 | 0,014 / 0,080 |
| LOD2 | 23 → 27 | 1 → 0 | 1 → 0 | 8,9 → 3,5 | 11,3° → 24,8° | 2.042 → 2.046 | 2.047 | 0,011 / 0,061 |

- Área do remendo LOW: 1,53 → 1,32 (−13%). É a cunha dobrada do leque, aquele "prisma" de agulhas, que deixou de existir.
- Silhueta de repouso igual nas 5 vistas de corpo inteiro (`01_repouso_corpo.png`).
- Ilhas UV:
  - LOW: 43×30 px em (802, 992), 20,3 px/stud, igual ao corpo; estiramento do UV mediano 1,08 e máximo 1,63;
  - LOD1: 31×23 em (400, 41), 17,1 px/stud;
  - LOD2: 35×26 em (582, 167), 14,0 px/stud;
  - nenhuma face invertida no UV e nenhum texel sem origem compatível.
- Texturas continuam em 1024.

**Deformação (LOW). Pele:**
- Quadros pedidos: Trote q6, Corrida q6/q8/q10/q12 e Andar q14.
- Pior caso de todos os quadros de Andar, Trote e Corrida, mais o Repouso a cada 8.
- `s1` = estiramento principal (relativo); "aresta" = estiramento absoluto em stud; "dobras" = critério geométrico (normal oposta à das vizinhas).

| Métrica | v21 | v22 | v23 |
|---|---|---|---|
| Prega: área com s1 > 1,8 (pior) | 0,540 (Corrida q12) | 0,445 | **0,172** (Andar q15) |
| Prega: s1 máximo (pior) | 6,09 (Trote q15) | 4,68 | **3,91** (Trote q6) |
| Trote q6: área com s1 > 1,8 / s1 máx. | 0,156 / 5,51 | 0,113 / 3,75 | 0,118 / 3,91 |
| Corrida q12: área com s1 > 1,8 / aresta máx. | 0,541 / 0,91 | 0,422 / 0,70 | **0,088 / 0,54** |
| Andar q14: área com s1 > 1,8 / s1 máx. | 0,279 / 5,63 | 0,164 / 3,74 | 0,162 / 3,42 |
| Compressão: prega com s2 < 0,5 (pior) | 1,01 | 0,82 | 1,10 (Corrida q0) |
| Dobras na região (pior, Corrida q13) | 0,203 | 0,283 | **0,295** (pior) |
| Dobras na prega (pior) | 0,094 | 0,082 | 0,093 |
| Viradas pelo osso dominante (pior) | 2,38 | 2,46 | 2,70 |
| Penetração na coxa D (fração dos vértices; pior) | 0,076 | 0,047 | 0,050 |
| Penetração na coxa D (profundidade máx.) | 0,25 | 0,24 | 0,24 |

- O critério de "viradas pelo osso dominante" exagera em peso misturado.

**Deformação (LOW). Pelo:**

| Métrica | v21 | v22 | v23 |
|---|---|---|---|
| Cartões atravessando a pele (repouso / pior) | 39 / 69 | — / 77 | 40 / 74 |

- Os cartões já atravessam a pele no repouso por construção (39–40).

**LOD1** (pior caso, v21 → v23):
- prega com s1 > 1,8: 0,61 → 0,24;
- dobras: 0,26 → 0,38;
- penetração: 0,074 → 0,042.

**LOD2** (pior caso, v21 → v23):
- prega com s1 > 1,8: 0,44 → 0,11;
- s1 máximo: 5,5 → 2,6;
- dobras: 0,99 → 0,63.

**Leitura dos números:**
- O estiramento da prega caiu forte.
- A compressão e as dobras geométricas subiram um pouco na Corrida q10–q13, com a perna à frente: a pele da prega agora acompanha a coxa e dobra ao comprimir.
  - São manchas pequenas (`03_poses_dobras.png`), espalhadas pelo joelho D e pela lateral do flanco.
  - Não são concentradas no remendo. Fica registrado.

**Evidências** (`review/v23_flanco/`):

| Arquivo | Conteúdo |
|---|---|
| `revisao/01_repouso_corpo.png` | referência e corpo inteiro (perfil D/E, três-quartos, traseira, baixo) |
| `revisao/02_repouso_<vista>.png` | real, sem cartões, arame e pesos |
| `revisao/03_poses_<modo>.png` | real, sem pelo, arame, pesos e dobras |
| `revisao/04_lods.png` | LOD1 e LOD2 |
| `revisao/05_uv_ilhas.png` | ilhas UV novas |
| `revisao/Flanco_<Trote\|Corrida\|Andar>_normal_30qps.mp4` e `_lento_0.5x.mp4` | v21 \| v22 \| v23 × barriga, virilha D e três-quartos, real com cartões |
| `metricas/*.json` | métricas |
| `aud_clipes_v23*.json` | auditoria |

**Causa, correção, evidência e pendência:**

| Problema | Causa | Correção | Evidência | Pendência |
|---|---|---|---|---|
| Membrana lisa esticada coxa D × ventre (Trote q6) | Leque de agulhas do Meshy (geometria) mais fronteira abrupta de peso | Retopologia local nos 3 LODs e faixa gradeada de pesos | `03_poses_sempelo` / `real` Trote q6; s1 máx. 5,5 → 3,9 | Revisão visual do usuário |
| Prisma facetado da cunha no repouso | Agulhas dobradas | Remalha projetada na superfície original | `02_repouso_*` arame | — |
| Coxa entrando na barriga (Corrida q8–q12, Andar q14) | Fronteira abrupta | Faixa de pesos | Penetração 0,076 → 0,050 | Dobras de compressão um pouco maiores na Corrida q10–q13 |
| UV / textura no remendo | Ilhas de ~4 faces | Ilha própria e transferência de texels (normal map convertido com normal suave) | `05_uv_ilhas`, `02_repouso_*_real` | O remendo fica um pouco mais liso que o normal map "espinhoso" vizinho (aparece só sem cartões) |
| Estiramento na virilha da linha média (Trote q15, s1 ~6 na v21) | Faces minúsculas entre as duas coxas | Reduzida pela faixa (pior da prega na v23 = 3,9) | Métricas | Fora do remendo; registrar |

**Regressões** (auditoria da v23 contra a v21, mesmo script):
- iguais: fresta cauda/coxa E (costura 0), garganta, axila, boca/mandíbula (0°), pálpebra fora da piscada (0°), marca e cristais, costura cabeça-corpo (cabeça intocada), apoios e deslizes de todas as patas, laços;
- mudança mínima na região "resto", que vizinha o flanco.

**Export e reimportação** (`anim_v23/export/`, cena limpa):
- 3 GLBs, cada um com armature de 37 ossos e as 4 ações.
- Nomes, hierarquia, ≤ 4 influências, soma dos pesos 1, nenhum vértice sem influência, materiais e 11 imagens.
- Escala igual à v21; laços 0.
- Desvio contra o rig de origem ≤ 0,00034, igual à v21.
- **Versão efetivamente exportada: v23** (`anim_v23/export/CR_LoboArtico_{LOW,LOD1,LOD2}_Clipes.glb`).
- Isto é validação no Blender, não teste no Roblox.

**Pendências registradas sem mexer** (critério de 0,03 mantido, nada aceito por distância):

| Peça | Patas acima do critério |
|---|---|
| Andar LOW | DD 0,034 e TD 0,034 |
| Andar LOD1 | TD 0,035 |
| Andar LOD2 | DD 0,045 e TD 0,031 |
| Trote LOD2 | DD 0,037 |
| Corrida LOD2 | TE 0,037 |

- Roblox e desempenho em PC/celular/alcateias: não testados.
- L2a continua não aprovada; L2b não iniciada.

### 8.26 v24: correção do deslize dos apoios em Andar, Trote e Corrida (10/11/2026). Pasta exportada: `anim_v24/`; intermediária `anim_v24_clipes/` (só clipes); `anim_v23/` e anteriores preservadas

**Pedido:** corrigir os apoios acima de 0,03 stud por fase. A v23 foi aprovada como correção localizada do flanco (com as dobras residuais registradas); isso não é aprovação final da L2a. Não iniciar a L2b nem acessar o Studio.

**M0:** a versão mais recente era a `anim_v23/`. Não havia v24.

**Método (contrato de aceite, sem alteração; mesmo do `auditar_clipes_v21.py`):**
- apoio = cronograma da marcha (`clipes_v21.json`);
- o apoio que cruza a emenda é **uma** fase: quadros < 0 = ciclo anterior;
- deslocamento de apresentação contínuo, −v·q/30 (v = D/T: Andar 3,0, Trote 6,667 e Corrida 20,357 stud/s);
- pontos medidos = vértices da pata que tocam o chão (até 0,03 acima do mais baixo) no **meio** do apoio, **fixos** na fase inteira, contados enquanto estão a menos de 0,06 do chão;
- deslize = maior deslocamento horizontal de um ponto em relação a ele mesmo no meio do apoio, em stud;
- afundamento e flutuação também pela auditoria;
- valores com 5 casas no diagnóstico; as pranchas arredondam **para cima** na 4ª casa.

**Diagnóstico** (`diag_apoios_v24.py`, novo, só leitura):
- Ele reproduz exatamente a auditoria (Andar LOW TD 0,03419, DD 0,03411) e separa três componentes:
  - **osso:** o ponto rígido no osso dominante, isto é, o clipe;
  - **pele:** a diferença vinda dos pesos;
  - **pivô:** o ponto de giro do rolamento.

| Achado | Leitura |
|---|---|
| Pivô C (70% do osso dos dedos, rígido no metacarpo) | parado no apoio (~1e-5) → trajetória do apoio e IK **corretos** |
| LOW/LOD1 (Andar TD 0,034, componente osso 0,034, pele 0, altura ~0) | o **rolamento** gira a pata em torno de pontos acima da sola (C na linha do osso e a ponta dos dedos) → a almofada plantada dos dedos é arrastada para trás no fim do apoio |
| LOD2 (Andar DD 0,044, Trote DD 0,037, Corrida TE 0,037: componente osso ~0, pele = tudo) | pesos da sola da malha reduzida misturam o osso de cima (por exemplo Metacarpo 0,45, Dedos 0,40 e **Antebraço 0,15**) |
| Centro da área de contato | anda naturalmente no rolamento; é só informativo, não é o critério |

- `VERIFICAR=1` reconstrói a v23 com o pivô antigo com diferença ≤ 2e-6, o que prova que a reconstrução é fiel.

**Correção:**
1. **`clipes_v24.py`** (`anim_v23` → `anim_v24_clipes`):
   - pose da v23 por quadro; refaz **só as 4 patas** pelo mesmo IK analítico gravado em FK (`marcha_v21.py`), com os mesmos parâmetros de cada marcha;
   - cronograma, cadência, passada, velocidade, alturas, dobras, ângulos de rolamento, corpo, cabeça e cauda **iguais**.
   - **Só o rolamento muda:**
     - pivô do metacarpo/metatarso a 0,8 do osso dos dedos (era 0,7);
     - pivô **descido** da linha do osso em direção à sola: 0,25 nas traseiras e 0,20 nas dianteiras (era 0);
     - dedos apontados para a **almofada plantada** em vez da ponta do osso;
     - a mesma regra vale nos 3 LODs;
     - sem rolamento, a pose é idêntica à v23.
   - Diferença máxima das pernas contra a v23: Andar 0,064, Trote 0,047, Corrida 0,055 (fim do apoio e saída do balanço).
   - Erro de IK: Andar 0,02087 (o mesmo da v23, herdado do lote 1), Trote 0 e Corrida 0.
2. **`pesos_sola_v24.py`** (`anim_v24_clipes` → `anim_v24`):
   - no LOD1 e no LOD2, os **vértices de contato** (até 0,03 acima da sola, com transição até 0,06) recebem os pesos do LOW interpolados no ponto mais próximo da pele da mesma pata;
   - o LOW não foi mexido.

**Testes descartados (medidos pela auditoria oficial):**

| Variante | Problema |
|---|---|
| Pivô na articulação MCP (dedos parados) | almofada do metacarpo desliza 0,06 |
| Pivô no chão sob a MCP ou sob C | dedos afundam 0,07–0,19 |
| Grade F (0,4–1,0) × L (0–0,8), dedos para a ponta ou para a almofada | (comparação) |
| Dianteiras com L = 0,25 | afundamento do LOD2 DD 0,033 |
| Faixa larga de pesos (0,18/0,40) | o calcanhar do LOD2 (aresta direta até o jarrete) dobrava no balanço (0,14 stud² na TE) |

**Resultado** (stud; deslize = pior fase; "→" = v23 → v24; afundamento pela auditoria; flutuação 0 em todas as fases; tolerância numérica 1e-5):

| LOD | Ação | DE | DD | TE | TD | Afundamento máx. v23 → v24 |
|---|---|---|---|---|---|---|
| LOW | Andar | 0,0118 → 0,0066 | 0,0341 → **0,0298** (emenda, −9..13) | 0,0276 → 0,0214 | 0,0342 → 0,0060 (emenda, −18..4) | 0,0069 → 0,0001 |
| LOW | Trote | 0,0116 → 0,0060 | 0,0217 → 0,0194 | 0,0200 → 0,0170 | 0,0194 → 0,0020 | 0,0025 → 0 |
| LOW | Corrida | 0,0002 → 0,0001 | 0,0205 → 0,0183 | 0,0121 → 0,0111 | 0,0182 → 0,0032 | 0,0036 → 0 |
| LOD1 | Andar | 0,0220 → 0,0167 | 0,0300 → 0,0229 | 0,0288 → 0,0214 | 0,0348 → 0,0021 | 0,0191 → 0,0050 |
| LOD1 | Trote | 0,0135 → 0,0044 | 0,0202 → 0,0182 | 0,0207 → 0,0170 | 0,0194 → 0,0020 | 0,0025 → 0 |
| LOD1 | Corrida | 0,0136 → 0,0034 | 0,0197 → 0,0150 | 0,0123 → 0,0111 | 0,0182 → 0,0015 | 0,0080 → 0 |
| LOD2 | Andar | 0,0134 → 0,0066 | 0,0445 → 0,0201 | 0,0251 → 0,0186 | 0,0311 → 0,0085 | 0,0354 → 0,0288 |
| LOD2 | Trote | 0,0140 → 0,0023 | 0,0374 → 0,0132 | 0,0237 → 0,0139 | 0,0165 → 0,0027 | 0,0181 → 0,0125 |
| LOD2 | Corrida | 0,0012 → 0,0001 | 0,0178 → 0,0125 | 0,0366 → 0,0086 | 0,0163 → 0,0044 | 0,0249 → 0,0192 |

- Intervalos (quadros de apoio, iguais nos 3 LODs):
  - Andar: DE 9..31, DD −9..13, TE 0..22, TD −18..4;
  - Trote: DE e TD 0..7, DD e TE 9..16;
  - Corrida: TE 0..3, TD 2..5, DD 5..8, DE 6..9.
- **Todas as patas ≤ 0,03 em todas as fases nos 3 LODs.** O pior caso é 0,02977 (LOW Andar DD), com pouca margem.
- **Afundamento por pata no LOD2:** subiu um pouco em algumas, todas abaixo de 0,03:

| Ação LOD2 | DD | TE |
|---|---|---|
| Andar | 0,027 → 0,029 | 0,004 → 0,008 |
| Trote | 0,007 → 0,013 | — |
| Corrida | 0,014 → 0,019 | — |

  O máximo do LOD2 caiu de 0,035 para 0,029.
- Velocidade medida no lugar: LOW Trote 5,95 → 5,87, por exemplo. É o recuo do centro de contato, só informativo; a velocidade do clipe não mudou.

**Reimportação** (`apoios_reimport_v24.py`, novo; GLBs em cena limpa, ações executadas pelo esqueleto importado, mesmos pontos e mesmo contrato de deslocamento):
- deslize igual ao da fonte em todas as 36 patas × ação × LOD (diferença ≤ 0,00002);
- `reimportar_clipes_v21.py`:
  - 37 ossos, nomes e hierarquia certos;
  - malhas presentes, ≤ 4 influências, soma 1, nenhum vértice sem influência;
  - materiais; 11 imagens (LOD2: 9); escala igual;
  - durações Repouso 240, Andar 36, Trote 18 e Corrida 14 quadros;
  - laço 0; desvio contra a fonte ≤ 0,00034.

**Regressões** (auditoria completa v23 × v24):
- Iguais:
  - costura cabeça-corpo e fresta (0), marca e cristais, boca (0°), pálpebras fora da piscada (0°);
  - laços (q0 = qN; aceleração na emenda igual ou menor);
  - repouso idêntico;
  - fresta cauda/coxa E e flanco/ventre D: prega com s1 > 1,8 0,172 = 0,172; penetração 0,050 → 0,049; dobras da prega iguais;
  - dobras geométricas das patas iguais à v23 nos 3 LODs.
- Pequenas, por causa da nova pose das patas dianteiras na Corrida:
  - "garganta", área virada pelo osso dominante: LOW 1,08 → 1,12, LOD1 1,11 → 1,13, LOD2 1,41 → 1,53;
  - "resto": +1–2%;
  - dobras da região do flanco LOD1: 0,38 → 0,40.
- **Dobras e colisões residuais do flanco (v23) continuam; não foram corrigidas aqui.**

**Custo:**
- tris iguais à v23 (corpo LOW 19.957 no GLB);
- sem geometria nova; texturas iguais (1024).

**Evidências** (`review/v24_apoios/`):

| Arquivo | Conteúdo |
|---|---|
| `revisao/01_deslize_barras.png` | barras v23 × v24 por ação, LOD e pata, com a linha de 0,03 |
| `revisao/02_trajetorias.png` | deslocamento do pior ponto ao longo da fase, incluindo a emenda |
| `revisao/Apoios_<Andar\|Trote\|Corrida>_LOW_{normal_30qps,lento_0.5x}.mp4` | 2–3 ciclos com deslocamento equivalente e grade de 0,5/1 stud; v23 \| v24 em perfil D/E, frente, traseira, três-quartos e closes das patas E e D, com o rastro dos pontos medidos (DE azul, DD vermelho, TE verde, TD amarelo) e a referência |
| `revisao/Apoios_*_LODs_*.mp4` | LOD1 e LOD2: perfil D e closes das patas |
| `diag_apoios_v23.json`, `diag_apoios_v24.json` | intervalos, pontos, trajetória do pior ponto, componentes osso/pele/pivô |
| `aud_clipes_v24.json`, `apoios_reimport_v24.json`, `metricas_flanco_v24.json` | auditoria, medição no reimportado e flanco |

**Scripts novos:** `diag_apoios_v24.py`, `clipes_v24.py`, `pesos_sola_v24.py`, `apoios_reimport_v24.py`, `vistas_apoios_v24.py`, `renders_v24.sh` e `prancha_apoios_v24.py`.

**Versão efetivamente exportada: v24** (`anim_v24/export/CR_LoboArtico_{LOW,LOD1,LOD2}_Clipes.glb`, com armature e só as 4 ações). Isto é validação no Blender, não teste no Roblox.

**Pendências:**
- pior deslize perto do limite (0,0298 no LOW Andar DD);
- dobras residuais do flanco (v23);
- L2a não aprovada; L2b não iniciada;
- Roblox e desempenho em PC/celular/alcateias não testados.

### 8.27 v25: L2b, 1º bloco — Arrancada e Frenagem (10/11/2026). Pasta: `anim_v25/` (exportada); `anim_v24/` e anteriores preservadas

**Pedido:** `DOCS/pedidos/2026-11-10-lobo-artico-v24-arrancada-frenagem.md`. Só Arrancada e Frenagem; viradas e transições Andar/Trote/Corrida ficam para outro bloco. Sem Studio. A v24 dos apoios foi aprovada tecnicamente.

**M0:** a versão mais recente era a `anim_v24/`. Não havia v25.

**Contrato do bloco:**
- **Arrancada = Repouso q0 → Corrida q0.**
  - Começa idêntica ao Repouso q0 (diferença 1e-6).
  - Termina idêntica à Corrida q0 (1e-5); a Corrida continua a partir do q1.
- **Frenagem = Corrida q0 → Repouso q0.**
  - Sai da Corrida no fim de um ciclo (q14 = q0).
  - Começa idêntica à Corrida q0 (1e-6) e termina idêntica ao Repouso q0 (1e-6).
- As duas são ações de uma vez, não laços.
- Clipe **no lugar** (Raiz fixa, frente −Y).
- O deslocamento de apresentação é uma **curva não uniforme**, gravada em `transicoes_v25.json`: `X_por_quadro`, `v_por_quadro`, direção (0, −1, 0), relógio de fase e apoio por quadro. Não há deslocamento na Raiz, então nada é duplicado.

**Gerador** (`transicoes_v25.py`, sobre a `anim_v24`; as 4 ações antigas ficam intocadas):
- **Curva v(t):**
  - Arrancada: 0,30 s de antecipação (v = 0), depois sobe rápido no início e suaviza até 20,357 stud/s em 1,25 s; mais ≥ 1 ciclo inteiro de Corrida; 75 quadros = 2,50 s, 36,7 stud.
  - Frenagem: desacelera de forma progressiva em 1,15 s, mais 0,45 s de acomodação; 48 quadros = 1,60 s, 11,1 stud.
- **Relógio de fase do galope:** ordem TE → TD → DD → DE (as fases da Corrida). O ciclo T(r) vai de 0,62 a 0,467 s e a fração de apoio de 0,60 a 0,28, com r = v / v_corrida: mais tempo no chão quando está devagar. Os limites de cada apoio são calculados no instante exato (interpolação do relógio).
- **Patas:**
  - no apoio, a pata recua no referencial do corpo **exatamente ∫v** (não desliza por construção);
  - o toque é planejado para centrar o apoio;
  - balanço min-jerk;
  - alturas, dobras e rolamento escalados por r (mínimo de 35%);
  - Arrancada: as 4 patas começam plantadas, as traseiras empurram e saem primeiro;
  - Frenagem: cada pata dá um último passo de acomodação que pousa onde, quando o corpo parar, ela estará na posição de repouso.
- **Corpo:**
  - slerp da pose do Repouso q0 com o corpo da Corrida (mesma fase do relógio);
  - atraso leve de 0,07 s em pescoço e cabeça e de 0,12 s na cauda (inércia);
  - antecipação: agacha 0,10, peso atrás −3° no Quadril;
  - impulso: inclina 2,5° para a frente, proporcional à aceleração;
  - freio: senta as traseiras (−3,5°, −0,06) e cabeça para cima −4°, proporcional à desaceleração, entrando do zero.
- No último ciclo da Arrancada e no 1º da Frenagem os parâmetros são **exatamente** os da Corrida.
- IK analítico gravado em FK, com o rolamento da v24. 37 ossos, nomes, hierarquia, repouso, escala e pivô iguais. Sem constraints.
- Erro de IK: 0 nas duas ações.
- Extensão máxima da perna: Arrancada DE **0,997** (Corrida 0,926); Frenagem DD 0,99.

**Auditoria da sequência contínua** (`auditar_sequencia_v25.py`, novo):
- Linha do tempo sem duplicados: Repouso q230..239 | Arrancada | Corrida ×3 | Frenagem | Repouso q0..10.
- X é a curva gravada (a Corrida a v constante).
- O apoio é o do cronograma; uma fase atravessa as emendas.
- Pontos fixos do meio do apoio, como na v24.
- Tolerância numérica 1e-5. Unidade: stud.

| LOD | DE | DD | TE | TD | Afundamento máx. | Flutuação máx. |
|---|---|---|---|---|---|---|
| LOW | 0,0059 | 0,0183 | 0,0199 | 0,0032 | 0,0001 | 0,0003 |
| LOD1 | 0,0044 | 0,0157 | 0,0199 | 0,0021 | 0,0001 | 0,0003 |
| LOD2 | 0,0023 | 0,0125 | 0,0167 | 0,0044 | 0,0192 | 0 |

- Os valores são o deslize máximo das 8 fases de cada pata que tocam a Arrancada ou a Frenagem.
- **Todas ≤ 0,03.** Pior: 0,0199, na TE da Frenagem q0..4.
- **Emendas:** a aceleração na emenda é menor que a máxima dentro dos clipes vizinhos em todas:

| Emenda | Aceleração na emenda | Máx. vizinha |
|---|---|---|
| Repouso → Arrancada | 0,027 | 0,56 |
| Arrancada → Corrida | 0,73 | 1,13 |
| Corrida → Frenagem | 0,73 | 1,13 |
| Frenagem → Repouso | 0,007 | 0,25 |

  A velocidade de deslocamento é contínua (0 → 20,357 → 0).

**Ações antigas:**
- Auditoria completa igual à v24: 672 métricas idênticas.
- Pior apoio continua 0,02977 (LOW Andar DD), e a margem não mudou.

**Deformação das ações novas**, comparada com a Corrida (LOW), sem região nova:
- fresta 0, boca 0°, pálpebras 0°, marca igual;
- prega do flanco com s1 > 1,8 0,104 = 0,104;
- dobras do flanco 0,298 → 0,347 e axila (área virada) 0,15 → 0,28, na fase de galope lento da Arrancada (alcance maior das dianteiras);
- pelo atravessando 74 = 74;
- closes reais e em cores (fresta, garganta e flanco) sem defeito novo visível.
- Dobras e colisões residuais da v23 continuam.

**Export e reimportação:**
- `exportar_clipes_v25.py` e `reimportar_clipes_v25.py`, cópias das v21 com 6 ações.
- 3 GLBs com armature e só Repouso, Andar, Trote, Corrida, Arrancada e Frenagem.
- 37 ossos, nomes e hierarquia; canais location+rotation+scale; durações Arrancada 75 e Frenagem 48 quadros.
- ≤ 4 influências, soma 1; materiais; 11 imagens (LOD2: 9); escala igual; tris iguais à v24 (corpo LOW 19.957).
- Desvio contra a fonte ≤ 0,00034.
- O "laço" da Arrancada e da Frenagem (1,14) é só informativo: elas não são laços.
- **Sequência rodada pelo esqueleto importado:** deslize igual ao da fonte (diferença ≤ 0,00002; pior 0,0199); duplicados das emendas ≤ 1e-5.
- **Apoios das 4 ações antigas** no reimportado: pior 0,02977 (diferença ≤ 0,00002).
- Bug corrigido no meu script: em cena nova o modo GLB abria a 24 qps e o importador convertia o tempo errado (dava "deslize" de ~2 stud); agora fixa 30 qps antes de importar.

**Evidências** (`review/v25_transicoes/`):

| Arquivo | Conteúdo |
|---|---|
| `revisao/01_curvas.png` | v(t), X(t) e faixas de apoio por pata; sequência com as emendas |
| `revisao/02_apoios.png` | deslize e afundamento por pata e LOD |
| `revisao/03_repouso.png` | referência, Repouso v24, Repouso v25 e último quadro da Frenagem |
| `revisao/Sequencia_LOW_{normal_30qps,lento_0.5x}.mp4` | sequência contínua sem cortes: perfil D/E, frente, traseira, três-quartos, patas E/D e câmera fixa; grade e rastro dos apoios; faixa com ação, quadro, v, \|X\|, patas no chão e cursor na linha do tempo |
| `revisao/Sequencia_LODs_*.mp4` | LOD1 e LOD2 |
| `revisao/Closes_{Arrancada,Frenagem}_*.mp4` | fresta, garganta e flanco D, real e cores |
| `aud_seq_v25*.json`, `aud_clipes_v25_antigas.json`, `aud_deform_transicoes_v25.json`, `metricas_flanco_*_v25.json`, `apoios_reimport_v25_antigas.json` | auditorias e métricas |

**Scripts novos:** `transicoes_v25.py`, `auditar_sequencia_v25.py`, `vistas_sequencia_v25.py`, `prancha_transicoes_v25.py`, `renders_v25.sh`, `exportar_clipes_v25.py` e `reimportar_clipes_v25.py`.

**Ajustes compatíveis em scripts deste lobo** (o padrão continua igual):
- `metricas_flanco_v23.py` (env `ACOES_MET`);
- `apoios_reimport_v24.py` (env `EXP_JSON`).

**Versão exportada: v25** (`anim_v25/export/CR_LoboArtico_{LOW,LOD1,LOD2}_Clipes.glb`). Isto é validação no Blender; não foi testado no Roblox.

**Pendências e riscos:**
- naturalidade a confirmar pelo usuário nos vídeos;
- DE da Arrancada quase estendida (0,997);
- axila e dobras um pouco maiores no galope lento;
- velocidade final de jogo não definida;
- viradas e transições entre marchas não feitas;
- L2b continua.

### 8.28 v26: L2b, 2º bloco — VirarEsquerda e VirarDireita (10/11/2026). Pasta: `anim_v26/` (exportada); `anim_v25/` e anteriores preservadas

**Pedido:** só as duas viradas com passos; sem as transições entre marchas; sem Studio.

**M0:** a versão mais recente era a `anim_v25/` (6 ações). Não havia v26.

**Contrato e eixos:**
- **Eixos:** frente −Y, cima +Z, lado **esquerdo** do lobo +X.
- **Rumo externo ψ** em torno de +Z, anti-horário visto de cima.
  - **VirarEsquerda:** ψ 0 → **+90°** (a frente vai de −Y para +X).
  - **VirarDireita:** ψ 0 → **−90°**.
  - 90° é parâmetro técnico, não regra.
- **Raiz fixa nos ossos** (clipe no lugar).
- **Transformação externa** por quadro em `viradas_v26.json`: `psi_graus_por_quadro`, `omega_graus_s_por_quadro` e `T_por_quadro`.
  - T = P − Rz(ψ)·P mantém parado o **pivô P = (0; −0,7; 0)**, o centro das 4 patas.
  - T final: (−0,70; −0,70) na VirarEsquerda e (+0,70; −0,70) na VirarDireita.
  - **Posição no mundo = T + Rz(ψ)·posição deformada local.** Não há rotação nos ossos da Raiz, então nada é duplicado.
- Começam e terminam com os ossos no **Repouso q0** (diferença 1e-6): o Repouso continua no rumo novo.
- Cada virada: 92 quadros = 3,07 s.
  - 0,25 s de antecipação: a cabeça lidera.
  - 2,4 s de giro: velocidade angular em trapézio suave, média 37,5°/s e pico ~50°/s.
  - 0,40 s de acomodação.

**Gerador** (`viradas_v26.py`):
- **Passos:** 4 ciclos, fração de apoio 0,65.
  - Ordem própria por lado: Esquerda DE → TD → DD → TE; Direita DD → TE → DE → TD.
  - A VirarDireita é gerada pelo mesmo código, **não espelhada**: cada lado da malha deforma com seus próprios pesos.
- **Cada pata plantada guarda posição e orientação no mundo.** O metacarpo e os dedos ganham uma guinada própria em relação ao corpo, então a sola não pivota contra o chão.
- O pouso fica na posição do repouso no rumo do **meio** do próximo apoio (apoio centrado); o último pouso fica no rumo final.
- Balanço min-jerk no mundo, com altura de 0,30 e dobra de passo; rolamento da v24 (12°) só antes de levantar.
- **Corpo:**
  - cabeça e pescoço antecipam o giro em 0,15 s;
  - coluna curva para o lado do giro;
  - cauda faz contrapeso com atraso de 0,12 s;
  - transferência de peso: o quadril se afasta da pata no ar (0,05) e abaixa 0,02 por pata no ar.
- IK analítico gravado em FK (o de `marcha_v21`, com guinada da pata). 37 ossos, nomes, hierarquia, repouso, escala e pivô iguais. Sem constraints.
- Erro de IK: 0. Extensão máxima da perna: 0,955.
- Plantas no mundo de cada apoio (posição e orientação) registradas em `plantas_mundo`.

**Auditoria mundial** (`auditar_viradas_v26.py`, novo):
- Composição: base acumulada @ T(t) @ Rz(ψ(t)) aplicados à malha deformada.
- **Sequências de ida e volta:**
  - Repouso q230..239 | VirarEsquerda | VirarDireita | Repouso q0..10;
  - Repouso q230..239 | VirarDireita | VirarEsquerda | Repouso q0..10.
- Uma fase de apoio atravessa as emendas; pontos fixos do meio do apoio (método v24).
- O deslize é **horizontal no mundo**: pega também a pata que pivota (pontos longe do centro da pata andam).
- Tolerância numérica 1e-5. Unidade: stud.

| LOD | DE | DD | TE | TD | Afundamento máx. | Flutuação |
|---|---|---|---|---|---|---|
| LOW | 0,0074 | 0,0166 | 0,0154 | 0,0021 | 0,0001 | 0 |
| LOD1 | 0,0042 | 0,0156 | 0,0154 | 0,0021 | 0,0001 | 0 |
| LOD2 | 0,0023 | 0,0112 | 0,0120 | 0,0018 | 0,0079 | 0 |

- Os valores são o deslize máximo das 18 fases de cada pata que tocam as viradas.
- **Todas ≤ 0,03.** Pior: 0,0166.
- **Emendas:** pose idêntica (≤ 1e-6).

| Emenda | Aceleração na emenda | Máx. vizinha |
|---|---|---|
| Repouso → virada | 0,007 | 0,31–0,34 |
| virada → virada | 0 | 0,40–0,43 |
| virada → Repouso | 0,007 | 0,36–0,43 |

- Rumo e translação contínuos (velocidade angular 0 nas pontas).
- Rumo final da ida e volta: 0,0°, posição (0, 0).

**Ações antigas:**
- Auditoria de Repouso, Andar, Trote e Corrida idêntica à v24 (0 diferenças); pior apoio 0,02977.
- Sequência Arrancada/Frenagem: pior 0,0199, igual à v25.

**Deformação** (LOW; comparada com o Andar):
- fresta 0, boca 0°, pálpebras 0°, marca ≤ 0,006;
- área virada: garganta 0,04 (Andar 0,06), flanco D ≤ 0,20 (Andar 0,51), cauda/pata E ≤ 0,05;
- prega com s1 > 1,8: 0,149 (Andar 0,172);
- **dobras do flanco 0,123 (Andar 0,066)**;
- pelo atravessando 64 (Andar 73).
- Closes reais e em cores (fresta, garganta e flanco), no lugar, para revisão.
- Dobras e colisões residuais da v23 continuam.

**Export e reimportação:**
- `exportar_clipes_v26.py` e `reimportar_clipes_v26.py` (8 ações).
- 3 GLBs com armature e só Repouso, Andar, Trote, Corrida, Arrancada, Frenagem, VirarEsquerda e VirarDireita.
- 37 ossos, nomes e hierarquia; viradas com 92 quadros.
- ≤ 4 influências, nenhum vértice sem influência; materiais; 11 imagens (LOD2: 9); escala igual; tris iguais (corpo LOW 19.957).
- Desvio contra a fonte ≤ 0,00034.
- **Reexecutado pelo esqueleto importado com as curvas externas:** viradas iguais à fonte (diferença ≤ 0,00001); duplicados ≤ 2e-6; transições pior 0,0199; ações antigas pior 0,02977.

**Evidências** (`review/v26_viradas/`):

| Arquivo | Conteúdo |
|---|---|
| `revisao/01_rumo.png` | ψ(t), velocidade angular, T(t), faixas de apoio e mapa de pegadas visto de cima com a orientação das patas |
| `revisao/02_apoios.png` | deslize e afundamento por pata e LOD |
| `revisao/03_repouso.png` | referência, Repouso v25, Repouso v26 e últimos quadros das viradas |
| `revisao/IdaVolta_{E,D}_LOW_{normal_30qps,lento_0.5x}.mp4` | câmeras fixas no mundo: topo (giro real e passos), três-quartos, perfil E/D, frente, traseira, patas E/D; grade, seta de rumo e rastro dos apoios; faixa com rumo e patas no chão |
| `revisao/IdaVolta_E_LODs_*.mp4` | LOD1 e LOD2 |
| `revisao/Closes_Virar{Esquerda,Direita}_*.mp4` | fresta, garganta e flanco, real e cores |

**Scripts novos:** `viradas_v26.py`, `auditar_viradas_v26.py`, `vistas_viradas_v26.py`, `prancha_viradas_v26.py`, `renders_v26.sh`, `exportar_clipes_v26.py` e `reimportar_clipes_v26.py`. Ajuste compatível: `auditar_sequencia_v25.py` (env `EXP_JSON`).

**Versão exportada: v26.** Isto é validação no Blender; não foi testado no Roblox.

**Pendências:**
- naturalidade a confirmar nos vídeos;
- a cada ciclo há um instante curto com só um par diagonal no chão (2 patas, como no trote);
- dobras do flanco um pouco maiores que no Andar;
- a guinada da pata é feita no carpo/jarrete (metacarpo/dedos), não por rotação do membro inteiro; observar nos closes de patas;
- velocidade de giro de jogo não definida;
- transições entre marchas não feitas;
- L2b continua.

### 8.29 v27: viradas com as pernas sem entrar para dentro (10/11/2026). Pasta: `anim_v27/` (exportada); `anim_v26/` preservada

**Pedido do usuário:** "Ao virar sua perna vai dentro, arrume isso."

**Causa (diagnóstico `diag_pernas_v27.py`, LOW):**
- Na v26 cada pata era plantada no repouso no rumo do **meio** do apoio.
- O corpo gira sobre a pata plantada. Uma pata a ~3 stud do pivô varre ~1 stud de lado por apoio (no referencial do corpo), e metade disso ia **para dentro**.
- As quatro patas entravam até 0,53–0,56, as pernas passavam do meio do corpo e as dianteiras chegavam a 0,21 uma da outra (repouso 0,81).

**Correção (`viradas_v27.py`, cópia da v26):**
- A **posição** de cada planta intermediária é escolhida por bissecção no rumo da planta, de modo que o alvo do MCP não entre mais que `dentro_max` = 0,10 durante o apoio. A varredura fica para **fora** (abdução).
- A **orientação** da pata plantada continua no rumo do meio do apoio.
- No balanço, a corda do giro não puxa a pata para dentro (limite suave).
- Passos mais curtos: 5 ciclos (eram 4) e fração de apoio 0,55 (era 0,65).
- O resto é igual à v26: 92 quadros, ±90°, mesmo pivô e mesmo contrato.

| Medida (LOW) | v26 | v27 | Andar |
|---|---|---|---|
| Entrada máxima do MCP | 0,53–0,56 | 0,11–0,12 | 0 |
| Abertura máxima para fora | – | 0,55–0,60 | 0 |
| Distância mínima entre as dianteiras (DE × DD) | 0,21 | 0,65 | 0,81 |
| Distância mínima entre as traseiras (TE × TD) | 0,37 | 0,69 | 0,75 |
| Vértices de perna que passam do meio | até 28 | até 4 (parte de cima da DE na VirarDireita) | 2 |

O LOD1 e o LOD2 têm o mesmo quadro (o JSON tem os valores por quadro).

**Apoios** (auditoria mundial com rotação, ida e volta E e D):
- deslize máximo: LOW 0,0169, LOD1 0,0159, LOD2 0,0120, **todos ≤ 0,03**;
- afundamento ≤ 0,0084; flutuação 0;
- emendas exatas (1e-6); rumo final 0°, posição 0.

**Ações antigas:**
- os apoios das antigas ficaram idênticos à v26;
- transições: pior 0,0199.

**Deformação:**
- dobras do flanco 0,115 (v26 0,123);
- penetração da coxa no LOD2 0,231 (v26 0,115; Andar LOD2 0,207);
- o resto ficou igual.

**Export e reimportação:**
- 3 GLBs com 8 ações (`anim_v27/export/`).
- O reimportado mede igual à fonte (≤ 1e-5); transições 0,0199.

**Evidências** em `review/v27_pernas/revisao/`:

| Arquivo | Conteúdo |
|---|---|
| `01_lateral.png` | entrada lateral e distância entre as pernas, v26 × v27 |
| `02_antes_depois.png` | frente e trás nos piores quadros da v26 |
| `03_apoios.png` | deslize e afundamento por pata e LOD |
| `Comparativo_v26_v27_*.mp4` | v26 × v27 lado a lado |
| `IdaVolta_{E,D}_LOW_*.mp4` | 8 vistas fixas |
| `IdaVolta_E_LODs_*.mp4` | LOD1 e LOD2 |

Closes da boca e do flanco não foram renderizados de novo (a mudança é só nas pernas; as métricas foram refeitas).

**Scripts:** `viradas_v27.py`, `diag_pernas_v27.py`, `prancha_pernas_v27.py`, `renders_v27.sh` e cópias v27 de `auditar_viradas`, `vistas_viradas`, `exportar_clipes` e `reimportar_clipes`.

**Pendências:**
- naturalidade a confirmar nos vídeos (abertura para fora de até 0,6 e passos mais rápidos);
- apoio diagonal mais longo que na v26 (fração de apoio 0,55);
- Roblox não testado.

**Aprovação:** v27 (VirarEsquerda/VirarDireita sem a perna entrar para dentro) **APROVADA pelo usuário em 10/11/2026**, na revisão dos vídeos no Blender. Roblox ainda não testado. Próximo bloco da L2b (transições entre marchas) só com autorização.

### 8.30 v28: L2b, 3º bloco — trocas de marcha (10/11/2026). Pasta: `anim_v28/` (exportada, 12 ações); `anim_v27/` preservada

**Pedido:** o usuário aprovou o próximo passo proposto, as transições Andar ↔ Trote ↔ Corrida. Sem Studio.

**Ações novas (de uma vez, não laço):**

| Ação | Entra em | Sai para | Quadros | v (stud/s) | Distância |
|---|---|---|---|---|---|
| AndarParaTrote | Andar q0 | Trote q0 | 70 (2,33 s) | 3,0 → 6,67 | 13,2 |
| TroteParaAndar | Trote q0 | Andar q0 | 111 (3,70 s) | 6,67 → 3,0 | 13,6 |
| TroteParaCorrida | Trote q0 | Corrida q0 | 63 (2,10 s) | 6,67 → 20,36 | 35,6 |
| CorridaParaTrote | Corrida q0 | Trote q0 | 62 (2,07 s) | 20,36 → 6,67 | 22,6 |

- Velocidades e durações são parâmetros técnicos.
- "Entra em" é o quadro da marcha de origem igual ao q0 da transição; o jogo sai no fim de um ciclo da origem.
- "Sai para" é o quadro da marcha de destino igual ao último quadro da transição; o jogo continua no q1 do destino.
- O deslocamento é uma curva gravada em `marchas_v28.json` (X por quadro, X = −∫v), como na v25.

**Gerador** (`transicoes_marcha_v28.py`):
- **Uma marcha que se transforma.** Peso s(t) de 0 (origem) a 1 (destino), em rampa suave de 1,0–1,3 s.
- **Parâmetros interpolados por s:** v, cadência, fração de apoio, fase de cada pata, centro do apoio, altura do balanço, dobra e rolamento.
- **Fases:** um deslocamento global escolhido minimiza a maior mudança de fase por pata.
  - Andar ↔ Trote: ±0,10 nas dianteiras e ∓0,15 nas traseiras.
  - Trote ↔ Corrida: até 0,35.
- **Apoio:** recua exatamente ∫v (sem deslize por construção), com o toque centrado.
- **Balanço:** min-jerk.
- **Pontas exatas:**
  - o plano começa 2 ciclos antes, só com a origem, e segue 2 ciclos depois, só com o destino;
  - o apoio e o balanço que estão em curso no q0 continuam os da origem (correção do toque entra com velocidade 0);
  - a fração do apoio e o rolamento são calculados pela fase, como na `pata_marcha`.
- **Corpo:** ossos fora das pernas lidos dos próprios clipes de origem e destino na fase e misturados por s. Cabeça com atraso de 0,08 s e cauda com 0,14 s.
- O IK analítico é gravado em FK; 37 ossos sem mudança e sem constraints.
- Erro de IK: 0 em AndarParaTrote e TroteParaCorrida; 0,021 em TroteParaAndar (no trecho já em Andar, igual ao próprio Andar); 0,057 em CorridaParaTrote (pata TE **no ar**, perna estendida).

**Auditoria** (`auditar_marchas_v28.py`, método v24: pontos fixos, fase que atravessa emendas):
- **Sequência:** Andar ×2 | AndarParaTrote | Trote ×3 | TroteParaCorrida | Corrida ×3 | CorridaParaTrote | Trote ×2 | TroteParaAndar | Andar ×2, num total de 583 quadros.
- **Pior deslize** nas fases que tocam as transições: LOW 0,0298, LOD1 0,0230, LOD2 0,0201. **Todos ≤ 0,03** e iguais aos piores do próprio Andar aprovado (LOW DD 0,02977).
- Afundamento ≤ 0,0288 (LOD2 DD, também igual ao do Andar); flutuação ≤ 0,0003.
- **Emendas:** aceleração na emenda abaixo da maior dos clipes vizinhos em todas.
- **Quadros duplicados:** ≤ 0,00009.

**Ações antigas:**
- apoios idênticos à v27;
- Arrancada/Frenagem: pior 0,0199;
- viradas: pior 0,0169.

**Deformação** (LOW, comparada com a origem e o destino):

| Transição | Dobras do flanco | Marchas de referência |
|---|---|---|
| AndarParaTrote | 0,136 | Trote 0,106 |
| TroteParaAndar | 0,085 | – |
| TroteParaCorrida | 0,298 | Corrida 0,298 |
| CorridaParaTrote | 0,262 | – |

- Prega 0,17–0,19, contra 0,10–0,17 nas marchas.
- Penetração e pelo atravessando no nível das marchas.
- Closes reais e em cores para revisão.

**Export e reimportação:**
- 3 GLBs com 12 ações (`exportar_clipes_v28.py` e `reimportar_clipes_v28.py`); 37 ossos, ≤ 4 influências; corpo LOW 19.956 tris.
- Reimportado e reexecutado pelo esqueleto importado: igual à fonte (≤ 2e-5).

**Evidências** em `review/v28_marchas/revisao/`:

| Arquivo | Conteúdo |
|---|---|
| `01_curvas.png` | v, s, cadência e apoios por transição |
| `02_apoios.png` | deslize e afundamento por pata e LOD |
| `Sequencia_LOW_*.mp4` | 7 vistas que acompanham o corpo, com grade e rastro dos apoios; normal e 0,5x |
| `Sequencia_LODs_*.mp4` | LOD1 e LOD2 |
| `Closes_<ação>_*.mp4` | closes de cada transição |

**Scripts:** `marchas_v28.py` (módulo comum), `transicoes_marcha_v28.py`, `auditar_marchas_v28.py`, `vistas_marchas_v28.py`, `prancha_marchas_v28.py`, `renders_v28.sh`, `exportar_clipes_v28.py` e `reimportar_clipes_v28.py`.

**Versão exportada: v28.** Validado no Blender e após reimportação; o Roblox não foi testado.

**Pendências:**
- naturalidade a confirmar nos vídeos;
- TroteParaAndar é longo (3,7 s, porque termina com 1,5 ciclo de Andar);
- pata TE estendida no ar no CorridaParaTrote;
- velocidades de jogo não definidas;
- Arrancada/Frenagem (v25) ainda aguardam revisão.

### 8.31 v29: revisão das desacelerações TroteParaAndar e CorridaParaTrote (10/11/2026). Pasta: `anim_v29/` (exportada, 12 ações); `anim_v28/` preservada

**Pedido:** revisar as duas desacelerações da v28 e ajustar só se o defeito fosse confirmado; sem novo lote, sem Studio. Status anterior: v28 aprovada tecnicamente (apoios/export), naturalidade não aprovada.

**Revisão (antes de mudar)** — `diag_desacel_v29.py`, quadro a quadro, com as marchas aprovadas como controle (`review/v29_desacel/diag_v28.json`):
- **CorridaParaTrote — defeito confirmado.**
  - A TE (traseira esquerda) **trava reta no ar** nos q11–12 (joelho/jarrete 4,6°/3,6°, extensão 0,9995 = limite do IK). Depois volta a dobrar (28° no q13–14) e trava de novo no q15 (5°), antes do toque.
  - Controles: Corrida 22,4° no mínimo, Trote 42,7°; a TD (controle) não muda (62,8°).
  - Causa: a mudança de fase da TE (+0,25 de ciclo) era absorvida **esticando o apoio**, com 3,32 stud contra 2,58 na Corrida. Com isso o toque ia muito à frente (y 0,40) e o balanço tinha de alcançar além da perna. A DE (+0,35) tinha o mesmo efeito, mais leve (0,961 de extensão).
- **TroteParaAndar — sem defeito de movimento, mas resposta demorada.**
  - A velocidade já é a do Andar a partir do q40 (1,33 s).
  - A pose fica a <0,001 stud do Andar a partir do q64 e exata (≤2e-6) a partir do q73. Do q73 ao q111 a v28 só anexava **Andar puro** (1 ciclo a mais), para cair num q0.
  - O pico de aceleração angular da DE no fim do balanço (21,3 °/q², q17) fica um pouco acima do Trote (17,4); nos vídeos não aparece tranco. Foi registrado e não alterado.

**Alterações** (`transicoes_marcha_v29.py`; regera só as 2 ações e copia as outras 10 da v28):
- **CorridaParaTrote:** o apoio não estica além do comprimento natural da marcha intermediária (v·β/cadência no meio do apoio, folga 5%). A mudança de fase das patas que atrasam passa a ser absorvida no **balanço**, que fica mais longo.
  - Apoios cortados: TE 1 (3,32 → 2,56 stud) e DE 2.
  - Mantido: toque centrado, recuo = ∫v, rolamento pela distância no apoio cortado.
  - Duração, velocidades, curva de deslocamento, pontas q0/q0 e fases de entrada e saída iguais às da v28.
- **TroteParaAndar:** plano idêntico ao da v28 (quadros 0–75 iguais nos quadros inteiros). A ação termina no **primeiro Andar q0 depois da convergência exata** (q75), não no q111.
  - **Contrato de saída mantido:** Andar q0, o jogo continua no q1.

| Ação | v28 | v29 | v (stud/s) | Distância |
|---|---|---|---|---|
| TroteParaAndar | 111 q (3,70 s) | **75 q (2,50 s)** | 6,67 → 3,0 (rampa 1,3 s, termina em 1,33 s) | 13,6 → **10,0** |
| CorridaParaTrote | 62 q (2,07 s) | 62 q (2,07 s) | 20,36 → 6,67 | 22,6 (igual) |

- Deslocamento por quadro: `anim_v29/marchas_v29.json`, que também registra a convergência, os apoios cortados e o erro de IK por pata no apoio e no balanço.
- Sequência de referência: 547 quadros (era 583).

**Resultados (Blender, fonte e reimportação):**

| Medida | v28 | v29 |
|---|---|---|
| TE CorridaParaTrote: joelho mínimo | 3,6° | **28,4°** (Corrida 28,4° no toque) |
| TE CorridaParaTrote: extensão máxima | 0,9995 | **0,9695** |
| IK CorridaParaTrote | 0,057 (no balanço) | **0** (≤1e-6), apoio e balanço |
| IK TroteParaAndar | 0,021 | 0,021, no **apoio** da DE já em Andar (igual ao Andar aprovado); balanço 0 |
| Pior deslize LOW / LOD1 / LOD2 | 0,02977 / 0,0230 / 0,0201 | **iguais** (LOW = Andar DD, margem pequena) |
| Afundamento / flutuação | ≤0,0288 / ≤0,0003 | iguais |

- Pontas: `TroteParaAndar fim × Andar q0` = 1e-6; as demais ≤ 8,7e-5.
- Emendas: aceleração abaixo das vizinhas em todas (TroteParaAndar→Andar 0,136 contra 0,277).
- 10 ações preservadas idênticas à v28 (curvas, diferença 0), conferido com `comparar_acoes_v29.py`.
- Auditorias antigas: Arrancada/Frenagem 0,0199 e viradas 0,0169, sem mudança.
- Deformação LOW (fonte da v29 contra v28):
  - dobras do flanco na CorridaParaTrote: 0,262 → 0,238;
  - TroteParaAndar: igual;
  - penetração ≤0,242, pelo atravessando ≤75; LOD1 e LOD2 iguais.
  - Dobras e colisões residuais continuam, **não resolvidas**.
- Export: 3 GLBs com armature e as mesmas 12 ações, 37 ossos, hierarquia e materiais iguais, tris iguais (≤19.956).
- Reimport: desvio contra a fonte ≤0,00034; apoios refeitos pelo esqueleto importado iguais aos da fonte.

**Evidências** (`review/v29_desacel/revisao/`):
- `00_referencia_resultado`, `01_curvas` (v28×v29), `02_apoios`, `03_pernas` (joelho/extensão da TE e da TD).
- `Comparativo_CorridaParaTrote` e `Comparativo_TroteParaAndar`: v28 em cima, v29 embaixo, mesmas câmeras (perfil D, traseiras E/D), faixa com v, patas no chão e marcador. Em velocidade normal e 0,5x.
- `Comparativo_CorridaParaTrote_LODs`.
- `Sequencia_LOW`: 8 vistas sobre grade, perfil E/D, ¾, frente, trás, patas e traseiras.
- `Sequencia_LODs`; `Closes_*` reais e em cores.

**Status:**
- Aprovação técnica: os apoios e o export passam.
- **APROVADA pelo usuário em 10/11/2026 ("Aprovar v29")**, incluindo a naturalidade das duas desacelerações. O bloco 3 da L2b (trocas de marcha) fica com a v29 como base.
- Roblox e desempenho em PC/celular **não testados**. Sem commit.

### 8.32 Revisão técnica da Arrancada e da Frenagem (v25, iguais na `anim_v29/`) — 10/11/2026, sem alteração

**Pedido:** "Prossiga", referindo-se ao próximo passo proposto, a revisão da v25. Somente leitura, sem Studio.

**Método:** `diag_arranca_freio_v29.py` mede, quadro a quadro e por pata, o ângulo do joelho/cotovelo, a extensão e a velocidade e aceleração angular. Controles: Corrida e Repouso. Saída em `review/v29_arranca_freio/diag.json`. Os quadros-chave foram conferidos nos renders da v25.

**Achados:**

| Ação | Pata | Joelho/cotovelo mínimo | Extensão máxima | Controle | Leitura |
|---|---|---|---|---|---|
| Arrancada | DE | 9,5° (q7) | 0,997 | Corrida 44,4°; Andar aprovado 3,6° | Na antecipação (v = 0, q0–9) |
| Arrancada | DD | 16,2° (q7) | 0,990 | – | Na antecipação |
| Frenagem | DE | 22,4° | – | Corrida 44,4° | – |
| Frenagem | DD | 16,1° | – | Corrida 16,8° | – |
| Frenagem | TE | 28,4° | – | Corrida 22,4° | – |
| Frenagem | TD | 61,0° | – | Corrida 61,8° | – |

- **Dianteiras na antecipação da Arrancada:** ficam quase retas com as 4 patas no chão, enquanto o peso vai para trás. A curva é suave (aceleração ≤ 2,8 °/q²). Na imagem do q7 parece uma postura canina normal, de pernas em coluna. **Não é travamento no ar.**
- **Picos de aceleração angular** no fim do balanço (TD 23,8 no q34 da Arrancada; TE/TD ~20 na Frenagem): seguem o mesmo padrão de "chegada ao toque" da Corrida aprovada (velocidade 29–31 → 6, com Corrida TD 31,7 → 5,3). Não são defeito novo.
- **Erro de IK:** 0 nas duas ações.
- **Apoios:** ≤ 0,0199, reconfirmado na auditoria da v29.
- **Deformação:** sem mudança desde §8.27. Dobras do flanco 0,347 e axila 0,28 no galope lento continuam como residuais **não resolvidos**.

**Conclusão:** nenhum defeito objetivo encontrado, e nenhuma mudança foi feita. A aprovação visual da v25 é do usuário.

### 8.33 v30: patas dianteiras sem virar no ar (10/11/2026). Pasta: `anim_v30/` (exportada, 12 ações); `anim_v29/` preservada

**Pedido:** "Percebi que as patas da frente se viram muito, parecendo que está bugado/errado, arrume isto." Sem Studio.

**Diagnóstico** (`diag_patas_giro_v30.py`; renders v29):
- No passo no ar, o carpo das dianteiras dobrava até **105° no Andar, 120° no Trote e 141–152° na Corrida e nas transições**, e os dedos até 85–92°.
- A pata virava com a sola para cima e para trás, e o punho da malha estrangulava (Andar q1, vista patas_E).
- Na vista de frente da Corrida (q11–13), as duas patas viravam de lado e mostravam a sola.
- A DE, inclinada 18,7° no repouso do rig, parecia girar para fora.
- As traseiras não têm esse problema e não foram tocadas.

**Correção** (`patas_dianteiras_v30.py`, pós-processo sobre a `anim_v29`):
- Só os ossos das **dianteiras** (Úmero, Antebraço, Metacarpo, Dedos) e **só nos quadros de passo no ar**, conforme o cronograma de apoio de cada ação. A pata no chão e todos os outros ossos ficaram idênticos.
- **Carpo:** comprimido a partir de 30° (fator 0,35, joelho suave).
- **Dedos:** comprimidos a partir de 28° (fator 0,35).
- **Eixo de giro:** o X do corpo, o mesmo que o IK original usa para dobrar o pé. A inclinação lateral do pé fica **igual à da v29** (DE 18,7°, DD 6,6°), sem cruzar nem abrir.
  - Duas tentativas descartadas: o eixo pelo produto vetorial jogava a pata 64° para o lado; o eixo X do antebraço fazia as patas se cruzarem na Corrida.
- **Folga:** com menos dobra, a pata ficaria mais baixa. Por isso o **punho sobe** no ar o necessário para manter a folga da v29 na malha LOW (limite de 0,06), até 0,13 stud. O IK de 2 ossos do braço é refeito no mesmo plano da `marcha_v21`, com erro 0. A subida é suavizada no tempo.
- **Pontas das transições:** nos primeiros e últimos 6 quadros, o peso e a subida acompanham os da marcha vizinha já corrigida. A emenda fica exata.
- Os laços continuam laços.

| Medida (máximo no ar) | v29 | v30 |
|---|---|---|
| Carpo DE/DD — Andar | 105/108° | **66/67°** |
| Carpo DE/DD — Trote | 120/124° | **68/71°** |
| Carpo DE/DD — Corrida | 141/142° | **77/77°** |
| Carpo DE/DD — CorridaParaTrote | 141/152° | **77/80°** |
| Dedos — Corrida | 85–92° | **51–54°** |
| Inclinação lateral do pé | 18,7/6,6° | **igual** |
| Torção pé × antebraço — Corrida | 12° | 22–34° (a imagem de frente não mostra giro) |

**Testes (Blender, fonte e reimportação):**
- **Apoios:** deslize, afundamento e flutuação idênticos à v29 em todas as fases e nos 3 LODs. Pior deslize: LOW 0,02977 (Andar DD), LOD1 0,0230, LOD2 0,0201.
- **Emendas:** duplicados ≤ 0,0001 (antes da correção das pontas chegavam a 0,07); aceleração na emenda abaixo das vizinhas em todas.
- **Auditorias antigas:** Arrancada/Frenagem 0,0199 e viradas 0,0169, sem mudança.
- **Repouso:** idêntico.
- **Folga das dianteiras no ar:** LOW e LOD1 ≥ a da v29 (ou ≥ 0,06). No LOD2, Andar DD e Trote DD caem para 0,031/0,029 (eram 0,046/0,092). Continuam acima do chão.
- **Flanco:** dobras no nível anterior (Andar 0,066, Trote 0,106, Corrida 0,297).
- **Export e reimport:** 3 GLBs com as 12 ações e 37 ossos. Desvio ≤ 0,00034; apoios refeitos pelo esqueleto importado iguais aos da fonte.

**Evidências** (`review/v30_patas/revisao/`):
- `00_referencia_resultado`, `01_angulos`, `02_apoios` e `03_frente_corrida`.
- `Comparativo_Patas`: v29 em cima, v30 embaixo; perfil E, frente e patas E/D, nos trechos de Andar, Trote e Corrida. Em velocidade normal e 0,5x.
- `Comparativo_Patas_LODs`; `Sequencia_LOW` e `Sequencia_LODs` (sequência completa).

**Status:**
- Aguarda a revisão visual do usuário.
- A v29 (aprovada) e a revisão da v25 continuam válidas para tudo o que não é a pata dianteira no ar.
- Roblox não testado. Sem commit.

### 8.34 v31: pernas dianteiras retas vistas de frente (11/11/2026). Pasta: `anim_v31/` (exportada, 12 ações); `anim_v30/` preservada

**Pedido:** com uma captura da vista de frente — "a perna se curva toda e vira, muito estranho, deixe isto mais reto ao se movimentar." Sem Studio.

**Diagnóstico** (`diag_perna_frontal_v31.py`, sobre a `anim_v30`):
- O IK do braço escolhia o lado da dobra pelo vetor de dobra da pose de repouso, que já é inclinado (plano a 4–7° no Repouso) e gira junto com o ombro.
- Na vista de frente, o cotovelo entrava para baixo do peito e a perna fazia arco:

| Ação | Cotovelo para dentro (stud) | Plano da dobra fora do sagital |
|---|---|---|
| Andar | até 0,18 | – |
| Trote | até 0,24 | – |
| Corrida (DD) | até 1,06 | até 80° |

- O pé torcia até 34° em relação ao antebraço.

**Correção** (`pernas_retas_v31.py`, pós-processo em todos os quadros das 12 ações, inclusive o Repouso, para as emendas continuarem exatas):
- Só Úmero e Antebraço das **dianteiras**.
- É o mesmo IK de 2 ossos, agora com a direção da dobra sempre perpendicular ao eixo lateral e à reta ombro-punho, no sentido do cotovelo original. O cotovelo fica no plano vertical frente-trás.
- O punho fica no mesmo lugar e o Metacarpo/Dedos mantêm a orientação no mundo. Pé e apoio idênticos: ponta dos dedos ≤ 0,0000025; erro de IK ≤ 0,000001.
- Funciona só com a pose de cada quadro, então pontas iguais continuam iguais.
- Tentativa descartada: projetar o vetor de dobra no plano sagital ficava indefinido na DD da Corrida (o arco continuava em 1,02).

**Resultado (v30 → v31):**

| Medida | v30 | v31 |
|---|---|---|
| Cotovelo para dentro, todas as ações | até 1,06 | **0** |
| Plano da dobra — marchas | até 80° | **≤ 12°** |
| Plano da dobra — viradas (pé colocado de lado) | – | ≤ 25° |
| Torção do pé — Corrida | até 34° | **≤ 5°** |

**Testes (Blender, fonte e reimportação):**
- **Apoios:** iguais à v30 nos 3 LODs. Pior deslize LOW 0,02977, LOD1 0,0230, LOD2 0,0201; diferença ≤ 0,00002.
- **Emendas:** duplicados ≤ 0,0001; todas as emendas abaixo das vizinhas.
- **Auditorias antigas:** Arrancada/Frenagem 0,0199 e viradas 0,0169.
- **Folga das dianteiras no ar:** igual à v30 (diferença ≤ 0,003).
- **Flanco:** dobras da Corrida 0,297 → 0,273 e do Trote 0,106 → 0,084; o resto igual. Residuais continuam.
- **Export e reimport:** 12 ações e 37 ossos, nomes e hierarquia iguais; desvio ≤ 0,00034.

**Evidências** (`review/v31_frontal/revisao/`):
- `00_referencia_resultado`, `01_frontal`, `02_apoios` e `03_frente_corrida`.
- `Comparativo_Patas`: v30 em cima, v31 embaixo; frente, trás e patas E/D em Andar, Trote e Corrida. Em velocidade normal e 0,5x.
- `Comparativo_Patas_LODs`; `Sequencia_LOW` e `Sequencia_LODs`.

**Status:** aguarda a revisão visual do usuário (v30 e v31). Roblox não testado. Sem commit.

### 8.35 Auditoria contra lobos reais (11/11/2026, sobre a `anim_v31`) — sem alteração de ações

- Pesquisa de filmagens e dados de lobos reais: `DOCS/criaturas/lobo-artico-referencias-reais.md`.
- Auditoria ação por ação: `DOCS/criaturas/lobo-artico-auditoria-real.md`.
- Medidas em `review/v32_lobo_real/auditoria_v31.json`; quadros marcados em `review/v32_lobo_real/revisao/`.
- **Principais desvios:**
  - cabeça alta no trote (0,95 acima da cernelha);
  - passada do Trote com cerca de metade do comprimento estimado do lobo (0,81 × ≈1,6 AO);
  - patas afastadas, sem convergir para a linha do meio;
  - cauda vertical demais;
  - viradas sem a cabeça conduzir;
  - no rig, base larga e assimétrica.
- **Corretos:** registro direto no trote, galope rotatório, sequência lateral do passo e pernas retas de frente (v31).
- **Lado a lado com o lobo real:** não foi montado, porque exige baixar vídeos de terceiros (aguarda decisão).
- **Primeira correção proposta:** postura de viagem (cabeça/pescoço/cauda), aguardando escolha.

### 8.36 v32: postura de viagem — cabeça no nível do dorso e cauda mais alta (11/11/2026). Pasta: `anim_v32/` (exportada, 12 ações); `anim_v31/` preservada

**Pedido:** "Sim, postura v32". É a 1ª correção proposta pela auditoria contra lobos reais (§8.35; `DOCS/criaturas/lobo-artico-auditoria-real.md`).

**Base real:**
- O lobo se desloca com a cabeça no nível do dorso (Heptner & Naumov).
- A cauda neutra fica a cerca de 45° abaixo do dorso (etograma do IWC).

**Correção** (`postura_viagem_v32.py`, pós-processo sobre a v31):
- Só os ossos Pescoço1/2, Cabeça e Cauda1/2, girados no eixo X do corpo: pescoço −14°/−9°, cabeça +12° (compensação, para o focinho não apontar para o chão), cauda +15°/+5°.
- **Pesos por ação:**
  - Trote 1;
  - Andar 0,5;
  - Corrida 0,7 na cabeça e 1 na cauda;
  - Repouso e viradas 0.
- **Transições:** seguem a mistura gravada (`s_por_quadro`), com o mesmo atraso da v28 (cabeça 0,08 s, cauda 0,14 s).
- **Arrancada e Frenagem:** seguem a razão v/v_corrida.
- **Pontas:** iguais às das marchas vizinhas.
- Rig sem mudança; nenhum osso de perna muda.

**Resultado (v31 → v32, média por ação):**

| Ação | Cabeça acima da cernelha (stud) | Cauda abaixo da horizontal |
|---|---|---|
| Trote | 0,95 → **0,14** | 70,5° → **51,8°** |
| Andar | 1,11 → 0,72 | 66,7° → 57,3° |
| Corrida | 0,56 → −0,01 | 77,9° → 62,2° |
| Arrancada | 0,67 → 0,28 | – |
| TroteParaAndar | 1,06 → 0,54 | – |
| Repouso e viradas | iguais | iguais |

**Testes:**
- **Apoios:** iguais à v31 nos 3 LODs. Pior deslize 0,02977 / 0,0230 / 0,0201; Arrancada/Frenagem 0,0199; viradas 0,0169.
- **Emendas:** duplicados ≤ 0,0001; todas abaixo das vizinhas.
- **Malha:** flanco igual (dobras, penetração e pelo atravessando). No close real da garganta no Trote, nada novo visível.
- **Export e reimport:** 12 ações, 37 ossos, desvio ≤ 0,00034; apoios no reimportado iguais.

**Evidências** (`review/v32_postura/revisao/`):
- `01_postura`, `02_apoios`.
- `Comparativo_Patas`: v31 em cima, v32 embaixo; perfil, ¾, frente e trás, em velocidade normal e 0,5x.
- `Comparativo_Patas_LODs`, `Sequencia_LOW` e `Sequencia_LODs`.

**Status:** **APROVADA pelo usuário em 11/11/2026** ("Sim"). Roblox não testado. Sem commit.

### 8.37 v33: patas sem virar ao andar e correr (quatro patas) (11/11/2026). Pasta: `anim_v33/` (exportada, 12 ações); `anim_v32/` preservada

**Pedido:** "Sim [v32 aprovada], só novamente, arrume as patas, estão virando muito ao andar e correr." Sem Studio.

**Diagnóstico** (`diag_patas_giro_v30.py`; orientação dos ossos do pé; vista de trás):
- As **traseiras** nunca tinham sido tratadas. No passo no ar os dedos dobravam até 76–84° (repouso 37°).
- O **metatarso** do rig tem inclinação lateral fixa de cerca de 15°. Quando o jarrete dobra, ele fica quase horizontal, apontando para trás, e essa inclinação joga a pata para o lado: de trás ela parecia virada mostrando a sola.
- Nas **dianteiras**, os dedos ainda dobravam 46–54° e o carpo 87–102° (medido em 3D) na Corrida. A DE tem a mesma inclinação do rig (18,7°).

**Correção** (`patas_v33.py`, cópia adaptada da v30 sobre a v32, nas **4 patas**, só no passo no ar):
- **Carpo/jarrete e dedos** comprimidos acima de um limiar:
  - dianteiras: 30° com fator 0,5 no carpo; 24° com fator 0,35 nos dedos;
  - traseiras: 55° com fator 0,45 no jarrete; 40° com fator 0,35 nos dedos.
- **Pé** (metacarpo/metatarso) levado ao plano frente-trás no ar, sem a inclinação lateral do rig. No chão a inclinação continua a mesma, então o apoio não muda.
- **Folga:** o punho/jarrete sobe o necessário para manter a folga da malha LOW. O IK de 2 ossos usa a dobra no plano frente-trás, como a v31.
- **Pontas:** iguais às das marchas vizinhas.

**Resultado (máximo no ar, v32 → v33):**

| Pata | Medida | Andar | Trote | Corrida |
|---|---|---|---|---|
| Traseiras | Dedos | 76° → 56° | 78° → 56° | 84° → 58° |
| Dianteiras | Dedos | 46–49° → 35–36° | – | 51–54° → 37–39° |
| Dianteiras | Carpo | – | – | 87/102° → 64/69° |

- De trás, as traseiras passam a ficar sob o corpo.
- Cotovelo/joelho sem arco e torção do pé ≤ 10°.

**Testes:**
- **Apoios:** iguais à v32 nos 3 LODs. Pior deslize 0,02977 / 0,0230 / 0,0201; Arrancada/Frenagem 0,0199; viradas 0,0169.
- **Emendas:** duplicados ≤ 0,00011; todas abaixo das vizinhas.
- **Folga:** no LOW, ≥ a da v32 (ou ≥ 0,06). Nos LODs a folga cai em alguns trechos, porque a proteção mede a malha LOW:
  - LOD1: DE na Corrida/Frenagem 0,05;
  - LOD2: mínimo 0,024 (DE na Arrancada) e 0,027 (TD no Trote/Andar);
  - tudo continua acima do chão.
- **Flanco:** dobras no Andar 0,066 → 0,083 e no Trote 0,084 → 0,072; Corrida igual.
- **Export e reimport:** 12 ações, 37 ossos, desvio ≤ 0,00034; apoios no reimportado iguais.

**Evidências** (`review/v33_patas/revisao/`):
- `03_tras_corrida` (vista de trás, v32 × v33).
- `Comparativo_Patas`: de trás, de frente e das patas E/D, em velocidade normal e 0,5x.
- `Comparativo_Patas_LODs`, `Sequencia_LOW` e `Sequencia_LODs`.

**Status:** **APROVADA pelo usuário em 11/11/2026** ("Aprovar v33"). A `anim_v33/` é a base atual das 12 ações. Roblox não testado. Sem commit.


### 8.38 Viradas: a cabeça já conduz (11/11/2026) — sem alteração

Foi medida a guinada na `anim_v33`:
- **cabeça:** começa no q8, antes do corpo (q10–12), e chega a 29°;
- **pescoço:** 19°;
- **peito:** 9°;
- **cauda:** −8°.

O item "viradas sem a cabeça conduzir" da auditoria (§8.35) estava errado, porque a auditoria mediu só a altura da cabeça; foi corrigido em `lobo-artico-auditoria-real.md`. Nenhuma versão nova. A próxima correção da fila (patas convergindo para a linha do meio) muda onde a pata pisa e aguarda aprovação após a análise de impacto.

### 8.39 v34: patas convergindo para a linha do meio (11/11/2026). Pasta: `anim_v34/` (exportada, 12 ações); `anim_v33/` preservada

**Pedido:** "Patas convergindo" (fila da auditoria contra lobos reais, §8.35/§8.38).

**Base real:** o lobo trota com "uma pata diretamente à frente da outra" (Mech & Boitani), quase em linha única. O nosso pisava com a largura do repouso: 2,12 stud nas dianteiras e 2,48 nas traseiras, em todas as marchas.

**Limite da malha:** as pernas são grossas. Pelo `diag_pernas_v27`, cada pata entra no máximo cerca de 0,25 antes de as pernas se tocarem. A linha única real é impossível com esta malha.

**Correção** (`convergir_v34.py`, pós-processo sobre a v33, nas 4 patas):
- O pé inteiro desloca para dentro um valor **constante em cada apoio** e muda só no ar (min-jerk). Assim o deslize não muda por construção.
- O braço/coxa é refeito com IK de 2 ossos, com a dobra no plano frente-trás (v31/v33).
- **Quanto entra, por membro:** dianteiras 0,22, traseiras 0,20. Esse valor é multiplicado pelo peso da marcha no toque:
  - Trote 1;
  - Corrida 0,8;
  - Andar 0,5;
  - transições: pela mistura gravada;
  - Arrancada/Frenagem: pela razão v/v_corrida (abaixo de 0,25 fica 0, para começar/terminar no Repouso);
  - Repouso e viradas: 0.

**Largura entre as patas no apoio (dianteira/traseira, stud), v33 → v34:**

| Ação | v33 | v34 |
|---|---|---|
| Trote | 2,12/2,48 | **1,68/2,08** |
| Corrida | 2,12/2,48 | 1,77/2,16 |
| Andar | 2,12/2,48 | 1,90/2,28 |
| Arrancada | 2,12/2,48 | 1,95/2,32 |
| Repouso e viradas | 2,12/2,48 | iguais |

**Testes:**
- **Apoios:** iguais à v33 nos 3 LODs. Pior deslize 0,02977 / 0,0230 / 0,0201 (LOD2 DE 0,0066 → 0,0069); Arrancada/Frenagem 0,0199; viradas 0,0169.
- **Emendas:** duplicados ≤ 0,00011; todas abaixo das vizinhas.
- **Pernas não se tocam:** menor distância entre as partes baixas de 0,31 (Corrida/Arrancada) a 0,51 (Andar). Antes era 0,65–0,81.
- **Folga das patas no ar:** igual à v33 nos 3 LODs.
- **Erro de IK:** ≤ 0,0015 (no Andar, com a DE quase toda estendida).
- **Flanco:** dobras no Andar 0,083 → 0,071, no Trote 0,072 → 0,074 e na Corrida 0,273 → 0,284.
- **Export e reimport:** 12 ações, 37 ossos, desvio ≤ 0,00034; apoios no reimportado iguais.

**Evidências** (`review/v34_convergir/revisao/`):
- `01_postura`, com a largura entre as patas por ação.
- `Comparativo_Patas`: frente, trás, ¾ e patas D; v33 × v34, em velocidade normal e 0,5x.
- `Comparativo_Patas_LODs`, `Sequencia_LOW` e `Sequencia_LODs`.

**Status:** **APROVADA pelo usuário em 11/11/2026** ("Aprovar v34"). A `anim_v34/` é a base atual das 12 ações. Roblox não testado. Sem commit.

### 8.40 Lote de vida, bloco 1, etapa 1: pose Deitado (esfinge) (11/11/2026) — proposta para revisão, sem clipe ainda

**Pedido:** "Lote de vida".

**Plano em blocos, com revisão entre eles:**
1. Deitar / Deitado / Levantar;
2. Sentar / Sentado / Levantar;
3. Farejar / Comer / Beber;
4. Sacudir / Uivar.

**Primeiro passo:** só a pose deitada estática, `pose_deitado_v35.py` sobre a `anim_v34`. Nada foi exportado e nenhuma ação foi alterada.

**Lições aplicadas do Lobo Ancestral** (§6o–6s da ficha dele): o usuário quer o lobo **totalmente deitado**, com barriga no chão, sem corcunda e com a cara no chão; patas e jarretes não podem atravessar o chão.

**Pose t8:**
- tronco desce 2,7 atrás e 2,15 na frente;
- antebraços e pés dianteiros deitados para a frente;
- metatarsos traseiros deitados para a frente, com os joelhos um pouco para fora;
- pescoço baixo, com a cabeça quase nivelada (12° para baixo) e o focinho entre as patas;
- cauda deitada para o lado.

**Contato** (ponto mais baixo por região na malha LOW; 0 = chão):

| Região | z (stud) | Situação |
|---|---|---|
| Barriga | −0,01 | encostando |
| Antebraços | −0,01 | encostando |
| Patas dianteiras | −0,03 | compressão leve |
| Jarretes | −0,04 | compressão leve |
| Patas traseiras | 0,17 | – |
| Queixo | 0,15 | – |
| Esterno | 0,22 | – |
| Pelve | 0,44 | apoiada nas coxas dobradas |
| Cauda | 0,30 | – |

- IK 0 nas 4 patas.
- **Evidência:** `review/v35_vida/pose/deitado_t8_prancha.png` (perfil E/D, frente, trás, ¾, baixo). As tentativas t1–t7 ficam na mesma pasta.

**Status:** pose **APROVADA pelo usuário em 11/11/2026** ("Aprovar pose"); animada na v35 (§8.41).


### 8.41 v35: lote de vida, bloco 1 — Deitar, Deitado e LevantarDeitado (11/11/2026). Pasta: `anim_v35/` (exportada, 15 ações); `anim_v34/` preservada

**Pedido:** "Aprovar pose" (§8.40). Gerador `gen_deitar_v35.py`, sobre a `anim_v34`.

**Como funciona:**
- Construtor de pose por quadro a partir do Repouso q0 exato.
- **Tronco:** frente e trás descem com pivô no quadril.
- **Patas:** por IK. Alvo fixo no mundo enquanto plantadas; arco quando dão o passo; o pé aplaina no ar.
- **Pescoço/cabeça e cauda:** a cauda fica erguida enquanto o quadril está baixo.
- **Ações antigas:** as 12 ficaram idênticas à v34 (diferença 0).

**As três ações:**

| Ação | Duração | Fases |
|---|---|---|
| **Deitar** | 93 q, 3,1 s | as dianteiras avançam em passos alternados enquanto a frente desce (Cotovelos, 1,6 s); tronco e quadril baixam e as traseiras se recolhem (Deitado, 2,47 s); a cabeça desce entre as patas (CaraNoChao, 3,1 s) |
| **Deitado** | 120 q, 4 s, laço | respiração no peito (0,6°), orelha que mexe de vez em quando, ponta da cauda balançando |
| **LevantarDeitado** | 72 q, 2,4 s | ergue a cabeça; recolhe as dianteiras sob os ombros e levanta a frente; o quadril sobe logo em seguida, com as traseiras dando o passo; acomoda no Repouso q0 |

**Testes (`auditar_vida_v35.py`, nos 3 LODs):**
- **Deslize nas janelas plantadas:** pior 0,0215 (LOD1 Deitar); Deitado ≤ 0,0002; LevantarDeitado ≤ 0,0102.
- **Emendas:**
  - Repouso→Deitar 1e-6;
  - Deitar→Deitado 4e-6;
  - laço do Deitado ≤ 8e-5;
  - Deitado→LevantarDeitado 0;
  - LevantarDeitado→Repouso 1e-6;
  - aceleração na emenda abaixo da dos clipes em todas.
- **Erro de IK:** 0 no Deitar e no Deitado; 0,024 no LevantarDeitado.
- **Contato:**
  - Deitado sem nada abaixo de −0,05;
  - **compressões passageiras:** pata dianteira −0,17 (Deitar q16), antebraço −0,24 (Deitar q59), barriga −0,08 (q60), pata traseira −0,13 e jarrete −0,08 (Levantar q47).
- **Flanco no deitado:** dobras 0,31–0,39 (de pé 0,07–0,27), penetração ≤ 0,25, pelo atravessando 60–76.
- **Export e reimport:** 15 ações, 37 ossos, desvio ≤ 0,00047.
- O deslize das ações novas foi medido na fonte, nos 3 LODs. A reimportação confere ossos, quadros e deformação contra a fonte.

**Evidências** (`review/v35_vida/revisao/`):
- `01_fases_<ação>`, `02_contato`.
- Vídeos `<ação>_LOW` (perfil E, frente, trás, ¾) e `<ação>_LODs`, em velocidade normal e 0,5x.

**Status:** **revista pelo usuário em 11/11** ("antes de dormir, ele deve descansar, deitar porém de cabeça erguida"); substituída pela v36 (§8.42).


### 8.42 v36: deitado de cabeça erguida antes de dormir (11/11/2026). Pasta: `anim_v36/` (exportada, 18 ações); `anim_v35/` preservada

**Pedido:** "Antes de dormir, ele deve descansar, deitar porém de cabeça erguida."

**Gerador:** `gen_deitar_v36.py`, cópia adaptada da v35 sobre a `anim_v34`. O Deitado de cabeça baixa da v35 virou o Dormindo.

**Ações** (o rótulo é o estado em que o lobo termina):

| Ação | Duração | O que faz |
|---|---|---|
| **Deitar** | 80 q, 2,67 s | mesmas fases da v35, mas termina de **cabeça erguida** (= Descanso q0) |
| **Descanso** | 150 q, 5 s, laço | deitado de cabeça erguida, olhando em volta (até 9°); respiração; orelhas que mexem; uma piscada no q100 |
| **Adormecer** | 66 q, 2,2 s | a cabeça desce entre as patas (CaraNoChao 1,73 s) e os olhos fecham (2,13 s) |
| **Dormindo** | 180 q, 6 s, laço | olhos fechados, respiração lenta e mais funda (0,9°), orelha rara, ponta da cauda |
| **Despertar** | 45 q, 1,5 s | abre os olhos (0,4 s) e ergue a cabeça até o Descanso q0 (1,4 s) |
| **LevantarDeitado** | 66 q, 2,2 s | parte do Descanso: recolhe as dianteiras e levanta a frente, o quadril sobe e acomoda no Repouso q0 |

**Fluxo:** Repouso → Deitar → Descanso ⇄ (Adormecer → Dormindo → Despertar) → Descanso → LevantarDeitado → Repouso.

**Pálpebras:** primeira vez que são usadas no Lobo Ártico. Ângulo no X local calibrado na malha (fenda ≤ 0,006): superior −16,7°/−15,8° e inferior +14,2°/+13,4° (E/D).

**Testes (`auditar_vida_v36.py`, nos 3 LODs):**
- **Deslize:** pior 0,0179 (Deitar); Descanso, Adormecer, Dormindo e Despertar ≤ 0,0003; LevantarDeitado 0,0114.
- **Emendas** (10 pares, incluindo os dois laços): ≤ 0,00008. Aceleração na emenda abaixo da dos clipes em todas.
- **Erro de IK:** 0, exceto 0,024 na LevantarDeitado.
- **Contato:** compressões passageiras iguais às da v35 (pata dianteira −0,17 e antebraço −0,24 no Deitar; pata traseira −0,13 na LevantarDeitado). Os laços e as transições de cabeça não têm nada abaixo de −0,05.
- **Ações antigas:** as 12 iguais à v34.
- **Export e reimport:** 18 ações, 37 ossos, desvio ≤ 0,00047.

**Evidências** (`review/v36_descanso/revisao/`): `01_fases_<ação>`, `02_contato` e vídeos `<ação>_LOW`/`_LODs`, em velocidade normal e 0,5x.

**Status:** **APROVADA pelo usuário em 11/11/2026** ("Aprovar v36"). A `anim_v36/` (18 ações) é a base atual. Roblox não testado. Sem commit.

### 8.43 Lote de vida, bloco 2, etapa 1: pose Sentado (11/11/2026) — proposta para revisão, sem clipe ainda

**Pedido:** "Aprovo" (bloco 2). Pose estática `pose_sentado_v37.py` sobre a `anim_v36`. Nada foi exportado e nenhuma ação foi alterada.

**Base:**
- etograma do IWC (*Sit*: peso nos quartos baixados, tronco ereto);
- lições do Lobo Ancestral (metatarsos traseiros deitados para a frente, dianteiras retas sob o peito, cabeça nivelada, cauda no chão).

**Pose s6:**
- tronco erguido a 34° (o real é cerca de 44°, mas o corpo deste rig é mais comprido; a 38° as dianteiras não alcançam o chão, IK 0,56–0,62);
- quadril desce 3,4;
- dianteiras quase retas sob o peito (extensão 0,90–0,92), pés normais no chão;
- traseiras dobradas com os metatarsos deitados para a frente e os joelhos um pouco para fora;
- pescoço compensa 22° e a cabeça fica quase nivelada (8°);
- cauda no chão, para trás e para o lado.

**Contato** (malha LOW; 0 = chão):

| Região | z (stud) |
|---|---|
| Garupa/pelve | 0,10 |
| Patas dianteiras | −0,01 |
| Jarretes | −0,04 |
| Patas traseiras | 0,17 |
| Cauda | 0,12 |

- IK 0 nas 4 patas.
- **Evidência:** `review/v37_sentado/pose/sentado_s6_prancha.png`. As tentativas s1–s5 ficam na mesma pasta.

**Status:** aguarda aprovação da pose antes de animar Sentar (peso para trás em fases, traseiras dobram), Sentado (laço) e LevantarSentado.

**Ajuste da cauda (11/11, usuário: "só deite a sua cauda atrás dele, ela está levantada") → pose s8:**
- **Antes:** na s6 a cauda saía para o lado com o tufo erguido.
- **Como foi deitada:** cada osso da cauda agora é apontado.
  - Cauda1 desce da base até a linha da cauda (0,8 de altura).
  - Cauda2–4 seguem rentes ao chão, para trás, com uma curva leve para o lado.
  - A cauda é larga de perfil e estreita de trás; por isso é girada −90° no próprio eixo, para a parte larga ficar deitada.
- **Testes descartados:**
  - linha mais baixa: o volume da malha afundava −0,9 a −1,6;
  - giro +90° no próprio eixo: afundava −0,77.
- **Contato:**

| Região | z (stud) | Situação |
|---|---|---|
| Cauda | −0,07 | compressão leve do pelo, deitada atrás |
| Pelve (ponto mais baixo) | 0,40 | garupa sentada de perfil; o 0,10 da s6 vinha da base da cauda pendurada |
| Dianteiras | −0,01 | – |
| Jarretes | −0,04 | – |

- **Evidência:** `review/v37_sentado/pose/sentado_s8_prancha.png`.
- **Parâmetros:** pitch 34, desce_quadril 3,4, cauda_z 0,8, cauda_rolo −90.

**Cauda revista (11/11, usuário: "na verdade deixe a cauda em pé, porém na direção do seu corpo; levemente curvada") → pose cB:**
- Foram renderizadas variantes em `review/v37_sentado/pose/sentado_cauda_variantes.png` e `sentado_cauda_AB.png`.
- **B (proposta):** a cauda fica erguida ao longo das costas, na direção do tronco, com curva leve (−10/−12/−14° por osso). Não toca o chão (cauda 0,94; pelve 0,40).
- **A** (continuar a linha do corpo para trás e subir em J) e **C** (curvada para a frente ao lado do corpo): inviáveis neste rig. Sentado, a base da cauda fica a 0,86 do chão, e a cauda entrava no chão (−1,7 a −3,3).
- **Parâmetros:** `cauda_modo` "corpo_alto", `cauda_curva` [−10, −12, −14].

**Status da pose:** variante B **APROVADA pelo usuário em 11/11** ("Sim, variante B"); animada na v37 (§8.44).

### 8.44 v37: lote de vida, bloco 2 — Sentar, Sentado e LevantarSentado (11/11/2026). Pasta: `anim_v37/` (exportada, 21 ações); `anim_v36/` preservada

**Gerador:** `gen_sentar_v37.py`, mesmo construtor do bloco 1, sobre a `anim_v36`. Pose final = Sentado cB aprovado, com a cauda em pé ao longo do corpo, levemente curvada.

**As três ações:**

| Ação | Duração | Fases |
|---|---|---|
| **Sentar** | 57 q, 1,9 s | o peso vai para trás e o quadril desce; as traseiras dão um passo curto para a frente e assentam com o quadril quase no fim; as dianteiras se ajustam sob o peito; a cabeça nivela; a cauda sobe **antes** de o quadril baixar, para não enterrar |
| **Sentado** | 150 q, 5 s, laço | respiração, olhar em volta (até 10°), orelhas, piscada no q75, ponta da cauda balançando |
| **LevantarSentado** | 48 q, 1,6 s | as dianteiras se ajustam, as traseiras recuam e empurram, o quadril sobe; a cauda só desce depois; acomoda no Repouso q0 |

**Testes (`auditar_vida_v37.py`, nos 3 LODs):**
- **Deslize:** Sentar 0,0102 / 0,0102 / 0,0212; Sentado ≤ 0,0002; LevantarSentado ≤ 0,0120.
  - Na 1ª versão o LOD2 da Sentar dava 0,034: um único ponto no jarrete deitado arrastava enquanto o quadril terminava de descer. Atrasar o passo das traseiras corrigiu.
- **Emendas:** Repouso↔Sentar↔Sentado (laço)↔LevantarSentado↔Repouso ≤ 0,000008. Aceleração na emenda abaixo da dos clipes em todas.
- **Erro de IK:** 0.
- **Compressões passageiras:** pata traseira −0,17 e jarrete −0,12 durante os passos (q13 da Sentar e q33 da LevantarSentado); cauda −0,15 no q12. O Sentado não tem nada abaixo de −0,05.
- **Ações antigas:** as 18 iguais à v36.
- **Flanco sentado:** dobras 0,38–0,49 (o tronco dobra), penetração ≤ 0,25, pelo atravessando 76–81.
- **Export e reimport:** 21 ações, 37 ossos, desvio ≤ 0,00047.

**Evidências** (`review/v37_sentado/revisao/`): `01_fases_<ação>`, `02_contato` e vídeos `<ação>_LOW`/`_LODs`, em velocidade normal e 0,5x.

**Status:** aguarda a revisão visual. Roblox não testado. Sem commit.

### 8.45 v38: LevantarSentado com a cauda voltando por fora (12/11/2026). Pasta: `anim_v38/` (exportada, 21 ações); `anim_v37/` preservada

**Pedido:** ao levantar, a cauda deve voltar para trás por fora, não por dentro do corpo.

**Diagnóstico (`diag_cauda_v38.py`):** mede o ângulo da cauda no plano do tronco (0° = ao longo das costas, +90° = em pé, 180° = para trás, −90° = para baixo, por dentro).
- Na v37, a LevantarSentado ia de 0° a −139° (Repouso) passando por −90°. Era o caminho curto da interpolação, e a cauda atravessava o quadril, entre as traseiras.
- A Sentar da v37 faz o mesmo caminho ao contrário. Não foi alterada, porque não fazia parte do pedido.

**Correção (`gen_levantar_v38.py`, sobre a `anim_v37`):**
- Só a LevantarSentado foi refeita.
- A Cauda1 gira pelo caminho longo do mesmo eixo (X, 220,7° em vez de 139,3°): 0° → +90° (q23) → 180° (q32) → Repouso. Cauda2 a 4 seguem a curva normal.
- A janela da cauda passou de 24–46 para 6–44: ela sobe e volta enquanto o quadril sobe.

**Testes (`renders_v38.sh`):**
- **Deslize:** LOW 0,0106, LOD1 0,0106, LOD2 0,0120.
- **Emendas:** Sentado→Levantar 2e-6 e Levantar→Repouso 1e-6, com aceleração da emenda menor que a dos clipes.
- **Cauda:** ponto mais baixo a +0,36 do chão (q44).
- **Erro de IK:** 0.
- **Demais ações:** as outras 20 estão idênticas à v37 (diferença 0).
- **Export e reimport:** 21 ações, 37 ossos.

**Evidências** (`review/v38_cauda/revisao/`): `01_fases_LevantarSentado`, `02_contato`, vídeos LOW e LODs em velocidade normal e 0,5x.

**Status:** APROVADA pelo usuário em 12/11/2026. Roblox não testado. Sem commit.

### 8.46 v39: Sentar com a cauda subindo por fora (12/11/2026). Pasta: `anim_v39/` (exportada, 21 ações); `anim_v38/` preservada

**Pedido:** depois da v38, aplicar a mesma correção na Sentar.

**Correção (`gen_sentar_v39.py`, sobre a `anim_v38`):**
- Só a Sentar foi refeita.
- A Cauda1 percorre pelo caminho longo o mesmo eixo usado na v38. O caminho fica −139° (Repouso) → 180° (para trás, q12) → +90° (em pé, q21) → 0° (ao longo das costas, q34).
- A cauda sobe por trás e passa por cima, sem atravessar o quadril.
- A janela continua 2–34: a cauda termina antes de o quadril baixar.

**Testes (`renders_v39.sh`):**
- **Deslize:** 0,0102 / 0,0102 / 0,0212, igual à v37.
- **Emendas:** Repouso→Sentar 1e-6 e Sentar→Sentado 3e-6, com aceleração da emenda menor que a dos clipes.
- **Cauda:** na v37 ia a −0,15 no q12; agora o ponto mais baixo fica a +0,36 do chão.
- **Erro de IK:** 0.
- **Demais ações:** as outras 20 estão idênticas à v38 (diferença 0).
- **Export e reimport:** 21 ações, 37 ossos nos 3 LODs.

**Evidências** (`review/v39_cauda/revisao/`): `01_fases_Sentar`, `02_contato`, vídeos LOW e LODs em velocidade normal e 0,5x.

**Status:** APROVADA pelo usuário em 12/11/2026. Roblox não testado. Sem commit.

### 8.47 Lote de vida, bloco 3, etapa 1: poses Farejar, Comer e Beber (12/11/2026) — proposta para revisão, sem clipe ainda

**Script:** `pose_bloco3_v40.py`, sobre a `anim_v39`, sem alterá-la. Parte do Repouso q0. A frente do tronco desce com pivô no quadril, e as patas ficam no chão por IK. O pescoço desce por bissecção até a ponta do focinho chegar à altura pedida, e a cabeça tem inclinação absoluta. Saída: `review/v40_bloco3/pose/`, com a prancha `poses_bloco3_v40.png` e um JSON por pose.

**Poses:**

| Pose | Tronco | Focinho | Cabeça | Outros |
|---|---|---|---|---|
| **Farejar** (t2) | frente 13° abaixo | 0,35 acima do chão, à frente das patas (y −5,2) | 55° | patas no lugar; orelhas para a frente |
| **Comer** (t2) | 16° | 0,15 | 66° | boca aberta 16°; dianteiras 0,25 mais abertas e 0,35 à frente |
| **Beber** (t3) | 17° | 0,08 (lambendo a superfície) | 40° | boca entreaberta 8°; dianteiras agachadas, cotovelos dobrados, antebraços a 0,29 do chão |

**Medições:** erro de IK 0 em todas.
- **Peito:** 0,88 (Farejar), 0,55 (Comer), 0,36 (Beber).
- **Patas:** o ponto mais baixo fica até 0,01 abaixo do chão.

**Tentativas descartadas:**
- **t1:** com o pescoço dobrado demais, a cabeça ficava encolhida entre as dianteiras. No Farejar, o focinho nem alcançava o chão.
- **t2 do Beber:** as dianteiras abriam para os lados como as de um sapo, e o peito ficava a 0,13 do chão.

**Status:** poses APROVADAS pelo usuário em 12/11/2026; clipes na §8.48.

### 8.48 v40: lote de vida, bloco 3 — Farejar, Comer e Beber (12/11/2026). Pasta: `anim_v40/` (exportada, 30 ações); `anim_v39/` preservada

**Gerador:** `gen_bloco3_v40.py`, mesmo construtor dos blocos 1 e 2, sobre a `anim_v39`. Usa as poses aprovadas de `review/v40_bloco3/pose/`. Cada comportamento tem entrada, laço e saída:

| Ação | Duração | O que acontece |
|---|---|---|
| **Farejar** | 30 q, 1 s | a frente desce e o focinho vai ao chão; patas no lugar |
| **Farejando** | 120 q, 4 s, laço | varre o chão de um lado a outro (±14°), fungadas rápidas (focinho sobe até 1,6°), orelhas |
| **PararFarejar** | 30 q, 1 s | a cabeça sobe primeiro, depois o tronco; volta ao Repouso |
| **Comer** | 45 q, 1,5 s | as dianteiras dão um passo curto para fora e à frente; a frente desce; a boca abre sobre o alimento |
| **Comendo** | 150 q, 5 s, laço | mastiga 3×/s (a boca fecha até 11°); 3 puxões do pescoço para cima e para trás (7°) |
| **PararComer** | 45 q, 1,5 s | a cabeça sobe, o tronco volta e as dianteiras recolhem |
| **Beber** | 54 q, 1,8 s | as dianteiras abrem e se agacham; o pescoço se estende e o focinho chega à água |
| **Bebendo** | 90 q, 3 s, laço | lambidas 3×/s: a boca abre e fecha (7°) e o focinho sobe de leve (2,2°) |
| **PararBeber** | 54 q, 1,8 s | a cabeça sobe, o tronco volta e as dianteiras recolhem |

Os desvios dos laços valem zero no q0, o que dá emenda exata, e só levantam o focinho.

**Testes (`auditar_vida_v40.py` e `renders_v40.sh`, nos 3 LODs):**
- **Deslize:** ≤ 0,0167 (pior caso: Beber e PararBeber; Farejar no LOD2 0,0097).
- **Emendas:** todas ≤ 8e-6 (Repouso → entrada → laço ↺ → saída → Repouso). A aceleração na emenda fica abaixo da dos clipes em todas.
- **Erro de IK:** 0.
- **Focinho nos laços:** 0,35–0,37 no Farejando, 0,15–0,48 no Comendo (puxões) e 0,08–0,14 no Bebendo. No Bebendo, o queixo vai a −0,11, dentro da água.
- **Compressão passageira:** a pata dianteira chega a −0,10 durante o passo de entrada e de saída (q11–15 e q33–39). No LOD2 fica em ≤ −0,06.
- **Demais ações:** as 21 antigas são iguais às da v39.
- **Export e reimport:** 30 ações, 37 ossos, desvio ≤ 0,00047.

**Evidências** (`review/v40_bloco3/revisao/`): `01_fases_<ação>` (9), `02_contato` e 36 vídeos (`<ação>_LOW`/`_LODs`, em velocidade normal e 0,5x).

**Riscos:**
- No Studio, o focinho só alcança água ou alimento que estejam na altura do chão do clipe. O Urso reprovou nisso em 12/11, então é preciso posicionar o alvo (água rasa ou carcaça) na altura certa.
- Roblox não testado.

**Status:** APROVADO pelo usuário em 12/11/2026 (anim_v40 = base atual). Sem commit.

### 8.49 Lote de vida, bloco 4, etapa 1: poses Uivar e Sacudir (12/11/2026) — proposta para revisão, sem clipe ainda

**Script e saída:**
- `pose_bloco4_v41.py`: mesmo construtor do bloco 3, sobre a `anim_v40`, sem alterá-la.
- Os parâmetros finais estão em `AJUSTE_V41` (t3) e em `review/v41_bloco4/pose/<pose>.json`.
- Prancha: `poses_bloco4_v41.png`.

**Poses:**
- **Uivar (de pé):**
  - peito um pouco erguido: frente 4° acima, quadril 0,45 mais baixo;
  - pescoço esticado para cima (44°), focinho 55° acima do horizonte, a 8,7 de altura;
  - boca entreaberta em "O" (18°), orelhas um pouco para trás, cauda baixa e neutra.
- **Sacudir:** é o pico da torção. O clipe alterna os lados de 4 a 5 vezes por segundo.
  - base aberta (0,2 por pata) e um pouco agachada (quadril 0,5 mais baixo);
  - peito rola 16° para um lado e o quadril 5° para o outro;
  - cabeça rola 42° na direção oposta, cauda balança para o lado (35°), orelhas para trás.

**Medições:** erro de IK 0; patas no chão (≤ 0,01 abaixo); cauda ≥ 0,25 do chão.

**Tentativas descartadas (t1):**
- No Uivar, o peito erguido tirava as dianteiras do chão (0,37) e a cauda raspava o chão.
- No Sacudir, o rolo do quadril deixava as pernas 0,24 curtas.
- Na t2, a cauda do Uivar ficou a −0,23, porque o quadril mais baixo a deixou abaixo do chão.

**Status:** poses APROVADAS pelo usuário em 12/11/2026; clipes na §8.50.

### 8.50 v41: lote de vida, bloco 4 — Uivar e Sacudir (12/11/2026). Pasta: `anim_v41/` (exportada, 34 ações); `anim_v40/` preservada

**Gerador:** `gen_bloco4_v41.py`, mesmo construtor dos blocos anteriores, sobre a `anim_v40`. Usa as poses aprovadas de `review/v41_bloco4/pose/`. As patas não saem do lugar. O Sacudir usa a base do Repouso, sem o passo de abrir as patas que aparece na pose estática.

| Ação | Duração | O que acontece |
|---|---|---|
| **Uivar** | 36 q, 1,2 s | o quadril baixa, o peito sobe, o pescoço estica e o focinho aponta para o alto; a boca abre no fim |
| **Uivando** | 150 q, 5 s, laço | uma nota longa (q0–110), em que a boca abre mais em "O" e o focinho sobe 5°; depois a inspiração (q110–150), em que a boca quase fecha, a cabeça desce 4° e o peito enche |
| **PararUivar** | 36 q, 1,2 s | a cabeça desce primeiro e volta ao Repouso |
| **Sacudir** | 60 q, 2 s | agacha (q0–12); depois a torção corre em onda da cabeça à cauda, alternando os lados cerca de 4,5 vezes por segundo (cabeça na frente, peito +1 q, barriga +1,6 q, quadril +2,4 q, cauda +3,2 q), com o envelope subindo e descendo entre q10 e q50; assenta no Repouso |

**Testes (`auditar_vida_v41.py` e `renders_v41.sh`, nos 3 LODs):**
- **Deslize:** ≤ 0,0054 (Sacudir no LOD2); nos demais casos ≤ 0,0015.
- **Emendas:** todas ≤ 4e-6 (Repouso → Uivar → Uivando ↺ → PararUivar → Repouso, e Repouso → Sacudir → Repouso).
  - A aceleração na emenda fica abaixo da dos clipes em todas.
  - Na 1ª geração, as emendas com o Repouso davam 0,066: as pernas usavam IK desde o q0. Corrigi com a mesma mistura FK→IK dos blocos anteriores.
- **Erro de IK:** 0.
- **Patas:** ponto mais baixo −0,043 (Sacudir q57).
- **Demais ações:** as 30 antigas são iguais às da v40.
- **Export e reimport:** 34 ações, 37 ossos, desvio ≤ 0,00047.

**Evidências** (`review/v41_bloco4/revisao/`): `01_fases_<ação>` (4), `02_contato` e 16 vídeos (LOW e LODs, em velocidade normal e 0,5x).

**Status:** APROVADO pelo usuário em 12/11/2026. A anim_v41 é a base atual e o lote de vida está completo: blocos 1–4, 34 ações. Roblox não testado. Sem commit.

### 8.51 Piloto no Roblox Studio — anim_v41 no place Teste-animacoes (15/11/2026)

**Pedido:** importar o lobo e as 34 animações aprovadas (anim_v41) num lugar isolado do Teste-animacoes (placeId 101211272245630) e testar em Play, como base dos poderes. Rodou em segundo plano. O rpg_roblox não foi tocado.

**Import (Import 3D feito pelo usuário):**
- O usuário importou os três GLB de `anim_v41/export/`: LOW, LOD1 e LOD2.
- Os modelos ficaram em `Workspace.Teste_LoboArtico`:
  - `LoboArtico_LOW` no chão em (−600, 1500, −600), ancorado;
  - LOD1 e LOD2 em `LODs_Reserva`, ancorados (só para a validação de LOD, depois).
- Conferências:
  - 37 ossos com os mesmos nomes; LOW com 5 MeshParts (Cabeca 19.168 tris, Corpo 19.956, Pelagem, Marca, Cristais);
  - escala 1:1, com a cabeça 6,05 acima da Raiz, igual ao Blender; frente em −Z e lado E em −X;
  - pivô (RootPart 2×2×1) no chão, 0,708 atrás da Raiz.
- Colisão: as MeshParts ficaram sem colisão e sem toque (`Box`, `Massless`); a RootPart ficou invisível. Ainda não há caixa de combate.
- Material: o Import 3D lê o canal azul da textura de rugosidade como **metal**, porque o GLB usa a rugosidade como `metallicRoughnessTexture` e o Roblox ignora o `metallicFactor = 0`. Resultado: pelo cromado.
  - Corrigido no Studio com `MetalnessMap = ""` nos SurfaceAppearance de Cabeca e Corpo dos 3 LODs. O id antigo ficou guardado no atributo `MetalnessMap_Importado`.
  - Correção definitiva proposta: exportar sem `metallicRoughnessTexture` ou com o canal B preto.
- Pelagem e Cristais vêm sem SurfaceAppearance (só TextureID). Em close aparecem cartões retangulares claros nas pernas e no flanco. A emissão dos cristais e da marca do Blender não existe no Roblox. **Pendente.**

**Animações:**
- **O importador também trouxe 34 KeyframeSequences por LOD** (`ServerStorage.RBX_ANIMSAVES`, 3×34, 243.606 instâncias). Não servem:
  - estão reamostradas a 24 fps (erro até 0,23 stud nas marchas rápidas);
  - estão todas com `Loop = true`;
  - têm o Raiz no topo da árvore, e o Animator ignora a pose do topo.
  - Ficaram intactas. **Apagar exige aprovação.**
- **Biblioteca nova:** `ReplicatedStorage.Animacoes_LoboArtico`.
  - 34 KFS `LoboArtico_<ação>` a 30 fps, com os quadros exatos do Blender (103.814 instâncias).
  - Loop só nos 11 laços; prioridade Idle no Repouso, Movement na locomoção e nas transições, Action no resto.
  - Fonte: `studio/json_v41/` → `studio/montar_kfs_lobo_v41.luau` (r2).
- **Convenção medida osso a osso, com a orientação completa** (`studio/conferir_giro_v41.luau` + `exportar_matrizes_v41.py`):
  - osso do jogo = osso do Blender girado 180°, então `Pose = M⁻¹·basis·M` (equivalente a CONVENCAO giro180y);
  - árvore `RootPart > Raiz > …`.
- **r1 descartada:** as pontas dos ossos batiam, mas os ossos giravam 180° em torno do próprio eixo e a malha saía torcida no Play (`review/studio_v41/folha_play_r1_DEFEITO_torcao.jpg`).
  - Lições: conferir a orientação, não só as pontas.
  - No Edit, `Stop` não tira a faixa do Animator; é preciso recriar o Animator antes de cada medição.
- **`Movimento_LoboArtico`** (ModuleScript na mesma pasta, gerado por `studio/gerar_movimento_v41.py`): deslocamento aprovado por quadro.
  - Fontes: X das transições e trocas de marcha; ψ e T das viradas.
  - Velocidades dos laços: Andar 3,0, Trote 6,67 e Corrida 20,36 studs/s.

**Testes e evidências:**
- **Conferência no Edit contra o Blender (34/34):**
  - pontas de cabeça, mandíbula, 4 patas, quadril e cauda em 102 quadros: ≤ 0,0023 stud;
  - orientação completa dos 37 ossos em 6 poses (Corrida, Deitar, Sacudir, Sentado, Farejar, Uivando): ≤ 0,2°;
  - durações iguais às do Blender.
- **Play (cliente, 51 segmentos, 55–61 fps; o cliente do Studio é limitado a 60):** as 34 ações rodaram em sequência, com emendas no quadro exato e o deslocamento em fase.
  - Encadeamentos: Repouso → Andar → AndarParaTrote → Trote → TroteParaCorrida → Corrida → CorridaParaTrote → Trote → TroteParaAndar → Andar; Arrancada → Corrida → Frenagem; VirarE e VirarD.
  - Vida: Deitar → Descanso → Adormecer → Dormindo → Despertar → Descanso → LevantarDeitado; Sentar → Sentado → LevantarSentado; Farejar → Farejando → PararFarejar; Comer → Comendo → PararComer; Beber → Bebendo → PararBeber; Uivar → Uivando → PararUivar; Sacudir.
  - Vídeos: `review/studio_v41/play_r2/`, `play_r2b/` e as folhas `folha_play_r2*.jpg`.
- **Beber:**
  - poça de água do Terrain com a superfície no nível do chão (y = 1500, conferido nos voxels);
  - lobo na margem: queixo 0,117 dentro da água (z −592,12, borda em −592) e nariz 0,60 acima;
  - pontas das dianteiras em terra, a −591,65 e −591,87.
- **Comer:** alimento de ensaio (`Comida_Ensaio`, 1,4×0,2×1,0; não é fauna oficial). O queixo fica 0,004 acima do topo.
- **Deslize das patas apoiadas** (Edit, 60 Hz, com o deslocamento; apoio = até 0,01 do ponto mais baixo de cada pata):
  - Andar ≤ 0,041, Trote ≤ 0,014 e viradas ≤ 0,015;
  - AndarParaTrote ≤ 0,035 e TroteParaAndar ≤ 0,038;
  - nas marchas rápidas o apoio dura menos de uma amostra (não mensurável assim).
- **Contato:** compressões passageiras já conhecidas do Blender — Deitar com a pata DD a −0,04 e Sentar e LevantarSentado com as traseiras a −0,05.
- **Achado:** **Andar → Repouso** não tem transição própria. Com mistura de 0,3 s, as patas deslizam até 1,06. É preciso um clipe `AndarParaRepouso`, ou parar no q0 do Andar.
- **Comparação visual:** `review/studio_v41/comparacao_ref_blender_studio.jpg` (referência × Blender v41 × Studio; mesma câmera e luz em cada etapa do Studio). Forma, cores, cristais e marca coerentes com a referência.
- **Desempenho (PC, cliente do Play):**
  - passo de animação: 0,344 ms sem faixa, 0,345 ms com 1 lobo e 0,375 ms com 10 lobos andando (cópias só no cliente);
  - FPS 60 nos três casos.
  - A deformação da malha, na GPU, não entra nessa medida.
  - **Celular não testado**; LOD1 e LOD2 não validados.

**Pontos de integração para os poderes** (só leitura; nada implementado):
- **Ossos de ancoragem:**
  - ponta de `Cabeca` (nariz) e `Mandibula`: origem do uivo e do som, mordida do ataque básico;
  - `Dedos_E`/`Dedos_D`/`DedosPe_E`/`DedosPe_D`: pegadas na neve, rastros do Instinto de Caça e impacto do Salto;
  - malhas `LOW_Marca` (ombro E, SurfaceAppearance Transparency) e `LOW_Cristais` (dorso): realce visual neutro, sem elemento.
- **Clipes que já servem:**
  - Uivar (1,2 s), Uivando (5 s: nota longa 0–3,67 s e inspiração 3,67–5 s) e PararUivar (1,2 s) → **Uivo**;
  - Farejar, Farejando e PararFarejar → **Instinto de Caça**;
  - Arrancada (2,5 s, 36,7 studs), Corrida e Frenagem → base de locomoção da **Investida**.
  - **Faltam** clipes próprios de Salto Predatório e Investida (como os `Hab_*` do Lobo Ancestral) e o ataque básico (mordidas e garras).
- **Movimento:** `Movimento_LoboArtico` dá o deslocamento por quadro, para o servidor mover o modelo em fase com o clipe.
- **Separação servidor/cliente:**
  - o servidor valida estado, recarga, energia, alcance e linha de visão e aplica os efeitos;
  - o Animator do AnimationController toca as faixas e replica;
  - VFX e som ficam no cliente.
- **Regras oficiais que limitam:**
  - habilidades da espécie Lobo: Salto Predatório (alvo selecionado), Uivo (fortalece **só o próprio** lobo), Investida (direção escolhida) e Instinto de Caça (pistas sem revelar coordenadas);
  - mínimo de 1 passiva + 3 ativas;
  - **elemento único do Lobo Ártico PENDENTE** (não presumir Gelo);
  - lista final do Ártico e todos os números PENDENTES.

**Primeiro poder proposto — Uivo (PROPOSTA, aguarda aprovação):**
- **Por quê:** só usa clipes aprovados, não depende do elemento pendente, não causa dano e é autobuff (sem risco de pay-to-win nem de PvP desequilibrado).
- **Roteiro:** Uivar (1,2 s, parado) → **efeito começa no fim do Uivar** → Uivando até 3,67 s (fim da nota longa) → PararUivar. Total ≈ 6 s, parado durante a animação; se tomar dano forte, cancela para o Repouso (regra a decidir).
- **Efeito (PROPOSTA, com os números do Ancestral como ponto de partida, não aprovados para o Ártico):** só o próprio lobo, 6 s, +15% de velocidade e +20% de janela de esquiva; recarga 18 s; custo 15 de energia. Sem bônus de grupo. Validado no servidor.
- **Visual e som:** neutros até o elemento ser escolhido — leve pulso da Marca e da respiração visível, som de uivo a partir da ponta da Cabeca.
- **Etapas:** E1 servidor + faixas no place isolado → E2 teste em Play com falha (recarga, energia insuficiente, interrupção, reconexão) → E3 visual e som.

**Arquivos novos (disco):**
- `BLENDER/Criaturas/Lobo_Artico_Ref/studio/`:
  - `exportar_clipes_json_v41.py`, `json_v41/` (34 JSON + `rest_v41.json` + `matrizes_v41.json`) e `exportar_matrizes_v41.py`;
  - `montar_kfs_lobo_v41.luau` (r2), `conferir_giro_v41.luau` e `medir_erro_gen.py`;
  - `gerar_movimento_v41.py` + `Movimento_LoboArtico.lua`;
  - `TestePlay_LoboArtico.client.luau`.
- `review/studio_v41/`: vídeos em JPG com `ts.txt`, folhas e a comparação.

**Objetos no place (Teste-animacoes):**
- `Workspace.Teste_LoboArtico`: chão de neve, poça (água do Terrain 16×16 em (−584…−568, −608…−592)), `Comida_Ensaio`, `Marco_Lobo`, `Pista_Ensaio` (temporária, 20×320) e os 3 modelos;
- `ReplicatedStorage.Animacoes_LoboArtico` (34 KFS + Movimento_LoboArtico);
- `ServerStorage.RBX_ANIMSAVES` (3 pastas "Scene" criadas pelo importador).
- Instâncias do place: 2,42 M → 2,76 M.
- Nada mais foi tocado; nenhum script foi instalado (o teste rodou pelo cliente do Play).

**Status:**
- Modelo e 34 animações **funcionando no Studio** (KeyframeSequence só toca no Studio; para o jogo publicado é preciso publicar como Animation, com a conta do usuário).
- **Não salvei nem publiquei o place**: as mudanças estão na sessão colaborativa aberta. Sem commit.
- Aguarda: revisão visual do usuário, decisão sobre `RBX_ANIMSAVES` e a aprovação do primeiro poder.

### 8.52 Uivo — E1 servidor + faixas no Teste-animacoes (15/11/2026)

**Autorização:** o usuário aprovou o Uivo como primeiro poder (15/11). Feito: E1 e a parte de falhas da E2 que dá para testar no Studio.

**Instalado (só na área isolada):**
- `Workspace.Teste_LoboArtico.Uivo_Servidor` (Script). A fonte está em `BLENDER/Criaturas/Lobo_Artico_Ref/studio/Uivo_Servidor.server.luau`.
- Em Play, ele cria `Rede_Uivo` (RemoteEvent), `Interromper_Uivo` (BindableEvent do servidor, para dano forte) e `Ensaio_DefinirEnergia` (só para teste).
- **Autoridade do servidor:**
  - o cliente manda só o nome `"Uivo"`;
  - o servidor confere personagem, distância (80 studs no ensaio), dono (`DonoUserId`, se existir), fase, recarga e energia;
  - toca as faixas no Animator do servidor (elas replicam: o cliente viu Repouso + Uivar tocando);
  - aplica os atributos `MultVelocidade`/`MultEsquiva` e `Parado`, que são os ganchos para o controlador do lobo, que ainda não existe.
- **Números PROVISÓRIOS:**
  - custo 15, recarga 18 s (desde o pedido aceito);
  - efeito 6 s, +15% de velocidade e +20% de esquiva;
  - energia máx 100 e regen 6/s, a mesma convenção do ConfigCombate dos dragões.
- **Regra PROVISÓRIA de interrupção (a decidir):**
  - cancelado durante o Uivar: fica sem efeito, mas energia e recarga continuam gastas;
  - cancelado depois do fim do Uivar: o efeito já dado segue até o fim e só a animação é cortada.

**Testes em Play (servidor + cliente, 15/11):**
| Caso | Resultado |
|---|---|
| Uivo completo | aceito; Uivar 0,14 → efeito 1,35 → PararUivar 5,03 → Repouso 6,25; efeito 1,35–7,35 = 6,00 s; energia 100→85 |
| Pedido durante o Uivar | recusado "ja uivando" |
| Pedido com recarga correndo | recusado "recarga 16,0 s" |
| Energia 2 < 15 | recusado |
| Interrompido 0,32 s após aceitar (Uivar) | fase cancelada, `MultVelocidade` 1, efeito agendado não aparece (conferido 1,5 s depois) |
| Interrompido no Uivando | animação cortada, efeito mantido, terminou a 0,12 s do fim previsto |
| Jogador a 200 studs | recusado "longe do lobo" |
| Cliente manda "Investida", tabela `{custo=0}`, nil | ignorados (contador não muda) |
| Cliente grava `MultVelocidade=5` no próprio modelo | servidor segue com 1 (não replica) |

- Duas tentativas da primeira rodada não valeram, por tempo do próprio teste: o pedido "em recarga" caiu depois da recarga acabar e a interrupção "no Uivar" chegou depois de 1,2 s. As duas foram refeitas com tempo controlado e aparecem na tabela acima.

**Não testado:**
- reconexão real: o Studio tem um jogador só. O estado fica no modelo e na hora do servidor, então não reinicia com o jogador, mas isso não foi provado;
- vários jogadores e o dono real (`DonoUserId` não existe no ensaio);
- celular;
- velocidade e esquiva aplicadas de fato, porque ainda não há controlador de movimento nem sistema de esquiva do lobo;
- tecla ou botão para o jogador (o teste disparou pelo cliente via integração);
- visual e som (E3).

**Status:** E1 funcionando no Studio (Teste-animacoes). Place não salvo, sem commit. Pendentes: aprovar os números e a regra de interrupção, E3 visual/som neutros e o controlador do lobo que lê os multiplicadores.

### 8.53 Uivo — números aprovados + E3 visual e som neutros (16/11/2026)

**Aprovação (usuário, 16/11, "Aprovar e ir à E3"):** os números da §8.52 deixam de ser provisórios para o ensaio:
- custo 15, recarga 18 s;
- efeito 6 s, +15% de velocidade e +20% de esquiva;
- energia máx 100 e regen 6/s;
- a regra de interrupção também foi aprovada.

**Instalado (só em `Workspace.Teste_LoboArtico`):**
- `Uivo_Cliente`: Script com RunContext = Client. A fonte está em `studio/Uivo_Cliente.client.luau`. Só lê os atributos do servidor e não decide nada.
- `Uivo_Servidor` r2: deixa o lobo com `ModelStreamingMode = Persistent`, porque o cliente precisa dos ossos. Fora isso, igual à E1.
- **Pontos de efeito:** ossos sem peso criados só no cliente.
  - `FX_Boca` = Cabeca + (0; 1,66; −0,31);
  - `FX_Nariz` = Cabeca + (0; 1,565; 0);
  - `FX_Marca` = Escapula_E + (−0,57; 0,72; 0,13).
  - No Repouso em Play, o nariz ficou a 0,06 stud do ponto do Blender.
- **Som:** `rbxassetid://9120790529`, "Wolf Howl Two Versions 1 (SFX)", da biblioteca Pro Sound Effects do Roblox (3,51 s), saindo do nariz.
  - Começa no início do Uivando, compensando o atraso de rede, e acaba sozinho antes do PararUivar.
  - Se a fase for cortada, some em 0,25 s; no PararUivar, em 0,5 s.
- **Respiração visível:** névoa branca fina saindo da boca durante a nota longa: 22 partículas/s, que caem para 6/s nos últimos 0,5 s.
- **Pulso da Marca:** PointLight branca fria no ombro E (alcance 3,5, brilho até 0,7, 1 Hz) enquanto o efeito está ativo, apagando nos últimos 0,8 s.
- **Sem cor de elemento:** o elemento do Ártico continua PENDENTE.

**r1 → r2 (pela captura):**
- na r1 a névoa virava uma bola grande acima da cabeça e a luz (alcance 7, brilho 1,4) estourava o pelo do corpo inteiro;
- na r2 a névoa ficou fina e a luz ficou só no ombro.
- Evidências em `review/studio_v41/`: `folha_uivo_e3.jpg` (r1), `folha_uivo_e3_r2.jpg` e `zoom_uivo_e3_r2.jpg` (r2), mais os quadros em `uivo_e3/` e `uivo_e3_r2/` (10 fps, com `ts.txt`).

**Testes em Play (cliente, 16/11):**
- **Uivo completo:**
  - som tocando de 1,3 a 4,7 s após o pedido;
  - névoa de 1,3 a 4,7 s;
  - luz pulsando até cerca de 7,4 s (fim do efeito) e depois zerada.
- **Interrompido 1,5 s após o início do Uivando:**
  - o som cai para 0,13 de volume e para em menos de 0,25 s;
  - a névoa para;
  - a luz continua até o fim do efeito mantido, como manda a regra aprovada.
- **Primeira tentativa falhou:** o script de cliente começou antes de o lobo chegar ao cliente (streaming) e desistiu. Corrigido com espera pelos ossos + Persistent no servidor.

**Não testado:**
- celular (custo baixo: no máximo cerca de 20 partículas e 1 luz sem sombra);
- volume e alcance do som com vários jogadores ao redor;
- reconexão;
- controlador de movimento e esquiva do lobo, que ainda não existe;
- tecla ou botão do jogador.

**Status:** Uivo E1 + E3 funcionando no Studio (Teste-animacoes). Place não salvo, sem commit.

### 8.54 Controlador de ensaio do lobo (16/11/2026)

**Pedido:** o usuário escolheu "Controlador do lobo". Feito: a camada de locomoção controlada pelo servidor, que a montaria (sela leve a partir do Adulto, ainda sem modelo) e a IA vão usar depois. No ensaio, quem dirige é um jogador que "assume" o lobo.

**Instalado (só em `Workspace.Teste_LoboArtico`):**
- **`Controle_Servidor` r2** (fonte `studio/Controle_Servidor.server.luau`). Autoridade do servidor: o cliente manda só a direção no plano e a marcha pedida (`andar`/`trote`/`correr`).
  - O servidor escolhe marcha, transições e giro e move por PivotTo, seguindo o chão por raycast.
  - **Velocidades** são as do próprio clipe, vezes `MultVelocidade`, com o clipe acelerado junto:
    - Andar 3,0 / Trote 6,667 / Corrida 20,357 studs/s;
    - a proposta 24.2 de 35 studs/s **não** foi usada porque não está aprovada.
  - **Trocas de marcha** sempre pelos clipes aprovados, com o deslocamento do Blender quadro a quadro (`Movimento_LoboArtico`):
    - parado → Andar (por mistura) ou → Arrancada → Corrida;
    - Andar ↔ Trote ↔ Corrida;
    - Corrida sem direção → Frenagem;
    - parado com mais de 60° → VirarEsquerda/VirarDireita.
  - **Giro andando (PROVISÓRIO):** Andar 60, Trote 70, Corrida 45 graus/s.
  - **Proteções:**
    - para antes de as patas dianteiras saírem do chão;
    - ignora pacote inválido ou acima de 30/s;
    - solta o comando sem pacote por 0,6 s ou quando o jogador sai;
    - só aceita assumir a até 25 studs.
  - **Uivo pelo controle:** o lobo freia primeiro (ex.: Corrida → Frenagem) e só então pede o Uivo pelo `Pedir_Uivo`.
- **`Controle_Cliente` r2** (Script RunContext Client; fonte `studio/Controle_Cliente.client.luau`):
  - F assume/solta, WASD, Shift corre, Ctrl anda, H uiva;
  - botões de toque Lobo/Correr/Uivo;
  - a câmera segue o lobo;
  - HUD de ensaio (marcha, velocidade, energia, recarga, multiplicador).
  - Este place não tem PlayerModule, então lê WASD direto e usa `Humanoid.MoveDirection` como reserva para toque.
- **`Uivo_Servidor` r3:**
  - o Repouso passou a ser do controlador;
  - recusa "em movimento" (VelAtual > 0,3);
  - ganhou o `Pedir_Uivo` (BindableEvent do servidor, só para o controlador).

**Testes em Play (16/11; intenções enviadas pelo cliente via integração, teclas não apertadas de verdade):**
| Caso | Resultado |
|---|---|
| Trote reto | Andar → AndarParaTrote → Trote 6,67 |
| Desvio de 45° e volta à linha | x −640 → −648 → −640 |
| Correr | TroteParaCorrida → Corrida 20,36 |
| Uivo pedido correndo | Frenagem → parou → Uivar; durante o uivo, mesmo pedindo correr, o lobo ficou parado (posição constante) |
| Arrancada com o efeito ativo | velocidade de pico 22,3 (×1,15) até o efeito acabar |
| Andar com o efeito ativo | 3,45 (= 3,0 × 1,15), voltando a 3,00 quando o efeito acaba |
| Sem pacotes | soltou em cerca de 0,6 s → TroteParaAndar → parado |
| Virar 180° | duas viradas de 90° no lugar |
| Borda da pista | parou com o pivô em x −634,5 (patas dianteiras na borda), "sem chao a frente"; 0 trocas de estado segurando contra a borda por 2 s |
| Pacote NaN/marcha "voar" | ignorado |
| Depois de soltar | ignorado |
| Assumir a 60 studs | recusado |
| HUD do cliente | rodando |

- Na r1, a borda não foi testada de fato e a checagem só olhava o pivô. Na r2 o teste olha também a frente das patas e foi refeito.
- Evidências: `review/studio_v41/folha_controle_r2.jpg` e os quadros em `controle_r2/` (Arrancada → Corrida → Frenagem → parado).

**Achado de projeto (decisão do usuário):**
- Com os números aprovados, o efeito do Uivo (6 s a partir do fim do Uivar, 1,2 s) acaba cerca de **1,1 s depois** que o lobo volta a se mover, porque a animação toda dura 6,07 s parado.
- Na prática, o +15% de velocidade quase não é usado.
- Opções: contar os 6 s a partir do fim do PararUivar, aumentar a duração ou permitir mover durante o PararUivar.
- Nada foi alterado.

**Não testado:**
- teclas reais e celular (botões de toque);
- vários jogadores;
- terreno irregular ou encosta (só chão plano);
- água e nado;
- esquiva, porque não há sistema de esquiva;
- montaria com sela.
- Conhecido: Andar → Repouso por mistura desliza (falta `AndarParaRepouso`), e começar a trotar direto do repouso entra no AndarParaTrote a 3 studs/s.

**Status:** controlador de ensaio funcionando no Studio (Teste-animacoes). Place não salvo, sem commit.

### 8.55 Referências novas de 16/11 (só leitura; nada alterado)

Dois arquivos novos na raiz do repositório, ainda fora do git: `REFERENCIAS_PODERES_E_EFEITOS.md` (v5.2) e `ESTATISTICAS_POR_IDADE.md`. Para o Lobo Ártico, chamado de "Lobo Glacial" no documento, eles registram:

**Decisões do usuário (16/11):**
- elementos **Gelo e Ar**;
- teto de esquiva 35%;
- esquiva = **chance** sorteada no servidor a cada golpe, separada da Esquiva Perfeita;
- "Uivos aumentados";
- "todo efeito no corpo; fora só neve levada pelo vento";
- espinhos de gelo nas costas e no pescoço.

**Kit [PROPOSTA], 3 ativas + 2 passivas:**
- Cometa Glacial, **Uivo Boreal** e Avalanche (ativas);
- Instinto Boreal e Pelagem Polar (passivas).

**Uivo Boreal:**
- +20% de velocidade, +25% de chance de esquiva, 8 s;
- inimigos a até 20 studs: −30% de velocidade por 4 s;
- recarga 22 s, energia 25;
- base: vida 400, energia 100, recuperação +5/s.

**Conflitos com o que existe aqui:**
1. **Elemento:** a §2 dizia "elemento único, PENDENTE" (regra de 30/10). A decisão de 16/11 dá **dois** elementos (Gelo e Ar). Vale a mais nova, mas a regra de 30/10 fica superada só para os lobos? A confirmar.
2. **Uivo do ensaio (§8.52–8.54):** usa 15%/20%/6 s/18 s/15 e regen 6/s. Os novos valores são 20%/25%/8 s/22 s/25 e regen 5/s.
   - A esquiva está como multiplicador (`MultEsquiva` 1,20); passaria a ser **chance somada** (base 5% + 25%, teto 35%).
   - Falta a lentidão em área.
3. **Visual E3 (§8.53):**
   - a névoa que **sai da boca** fere a regra "nada sai do corpo";
   - a luz no ombro e o som simples não seguem o Uivo Boreal: linhas azul-gelo contínuas, espinhos de gelo crescendo em 0,6 s e recolhendo em 0,8 s, geada no dorso, olhos azul-gelo, neve em órbita, e "uivo agudo com vento cortante e tilintar de gelo".
4. **Modelo:** o documento cita o modelo **antigo** (`Biblioteca_Criaturas.Modelos.Lobo_Artico`, 13 animações). A base atual é o Lobo Ártico Ref (anim_v41, 34 clipes).
5. **Kit:** Salto Predatório e Investida saem do kit do Ártico; entram Cometa Glacial e Avalanche, que precisam de clipes novos [PENDENTE].
6. **Por idade:**
   - Adulto: 12 studs de comprimento, vida 400, dano 10, esquiva 35%;
   - velocidade de 115% no Filhote a 90% no Ancião;
   - o controlador ainda não lê a idade.
7. **Achado da §8.54:** com 8 s, sobram cerca de 3,1 s de efeito depois que o lobo volta a andar. Ainda é curto; segue para a decisão do usuário.

### 8.56 Uivo Boreal no ensaio (16/11/2026)

**Pedido:** "Adaptar ao Boreal". Base: `REFERENCIAS_PODERES_E_EFEITOS.md` v5.2, §3 e §5.1/§5.3. Os números são [PROPOSTA][A TESTAR] do documento.

**Servidor — `Uivo_Servidor` r4** (fonte `studio/Uivo_Servidor.server.luau`; a r3 ficou em `Uivo_Servidor_r3_antes_boreal.server.luau`):
- +20% de velocidade;
- **chance** de esquiva 5% → 30% (base 5% + 25%, teto 35%), com `SortearEsquiva` (BindableFunction do servidor, para o sistema de dano chamar a cada golpe);
- efeito de 8 s, recarga 22 s, custo 25, energia com regen 5/s;
- **lentidão em área:** −30% de velocidade por 4 s em inimigos a até 20 studs.
  - Respeita o teto de 60% somado por alvo.
  - Funciona em Humanoid (WalkSpeed) e em criaturas (atributo `Lentidao`).
  - O dono/controlador nunca é afetado. Os outros jogadores só são afetados se `CFG.lentidao.jogadores` estiver ligado (PvP [A CONFIRMAR]).
- O roteiro e a regra de interrupção aprovados continuam iguais.

**Cliente — `Uivo_Cliente` r3** (fonte `studio/Uivo_Cliente.client.luau`; a r2 neutra ficou em `Uivo_Cliente_r2_neutro.client.luau`):
- **Removidos:** a névoa que saía da boca e a luz do ombro, porque ferem "nada sai do corpo".
- **No corpo:**
  - os cristais do dorso acendem em azul-gelo (Highlight só no `LOW_Cristais`, sem contorno);
  - pulso de 1,5 s, pico no uivo, fade-in de 0,6 s e fade-out no último 1,5 s;
  - olhos azul-gelo (pontos Neon presos aos ossos das pálpebras).
- **Fora do corpo, só** neve levada pelo vento: 8 faixas finas em espiral elíptica ao redor do corpo, na frente e atrás, com flocos brancos.
- **Som** (Pro Sound Effects, os mesmos do kit Gelo do place):
  - uivo mais agudo (×1,12);
  - vento contínuo (9125742111, ×1,25) durante o efeito;
  - tilintar de vidro (9114590297) no pico;
  - estalos de gelo (9114858178) no Uivar.
- **Geada nos alvos com lentidão:** Highlight azul-gelo translúcido enquanto durar.

**Testes em Play (16/11):**
- **Efeito:** durou 1,35 → 9,4 s (8 s), com velocidade ×1,20 e chance de esquiva 0,30.
- **Sorteio da esquiva (4000 golpes):** 4,8% antes do Uivo e 28,5% durante (esperado 5% e 30%).
- **Energia:** 100 → 75, depois volta a 100 em cerca de 5 s.
- **Inimigo de ensaio a 12 studs:** WalkSpeed 16 → 11,2 (×0,70) por 4 s e depois volta a 16; a geada apareceu e sumiu.
- **Inimigo a 25 studs e o jogador:** sem efeito.
- **Evidências:** `review/studio_v41/folha_boreal_r1.jpg` (longe), `folha_boreal_r1_perto.jpg` e `zoom_boreal_r1_perto.jpg`, mais os quadros em `boreal_r1/` e `boreal_r1_perto/`. Os inimigos de ensaio só existiram durante o Play.

**Problemas vistos na captura:**
1. O brilho dos cristais aparece **através dos cartões de pelo** e forma uma mancha azul difusa no peito e no ombro.
2. Neve em órbita, olhos e cristais são discretos e quase somem contra a neve branca, de longe.

**PENDENTE (precisa de textura/malha nova, não feito):**
- linhas azul-gelo contínuas pelo corpo ("capa de efeito" com UV do pelo);
- espinhos de gelo que **crescem** do pelo em 0,6 s e recolhem em 0,8 s (hoje só acendem os cristais que já existem);
- película de geada no dorso.

**Não testado:**
- teto de 60% com duas fontes de lentidão;
- lentidão em jogadores (PvP);
- celular;
- volume do som com vários jogadores.

**Status:** Uivo Boreal (servidor + efeitos r1) funcionando no Studio (Teste-animacoes). Place não salvo, sem commit.

### 8.57 Linhas e espinhos do Uivo Boreal (16/11/2026)

**Pedido:** "verifique as novas atualizações e prossiga com as linhas e espinhos".
- **Verificação:** nada novo para o Ártico. As referências seguem v5.2 (16:46) e o arquivo por idade é das 19:05; os commits novos são do Crocodilo.
- **Decisão adotada:** a dúvida "espinhos só no Uivo ou permanentes" continua aberta no documento. Adotei o texto da §5.3: crescem no início e recolhem no fim. A mudança é de 1 linha no cliente.

**Blender** (`boreal/boreal_fx.py` sobre `anim_v41/CR_LoboArtico_Anim.blend` em repouso; renders r1–r6 em `boreal/review_r*/` e `boreal/prancha_boreal_r*.jpg`):
- **Linhas:**
  - fitas de 0,075 de largura, continuas, nas costas (5 linhas), na cauda e nas 4 pernas (lado de fora), subindo pelo pescoço até a nuca; rosto limpo;
  - pele copiada da `LOW_Corpo` por proximidade;
  - 5 malhas por região: Linhas_1 pescoço → Linhas_6 cauda.
- **Espinhos:** 8 cristais facetados com ponta secundária, rígidos, com a origem na base.
  - Começam logo atrás dos cristais permanentes da nuca, que já são o ponto mais alto, e diminuem de 0,95 a 0,36 até a garupa.
- **Correções r1→r6:**
  - as linhas flutuavam (cartões de pelo): passaram para pele + folga, e só pelo na juba e na cauda;
  - os espinhos 1 e 2 caíam no mesmo ponto;
  - depois viravam "chifre" entre as orelhas: a fileira passou a começar atrás dos cristais.
- **Tamanho:** linhas 900 tris, espinhos 320 tris.
- **Exportação:** `boreal/exportar_boreal.py` → `boreal/export/CR_LoboArtico_BorealFX_r6.glb` (0,13 MB) e `boreal_fx_r6.json`.

**Studio:**
- O usuário importou o GLB r6 como `Workspace.Import_BorealFX_r6`. Um import do r3 também ficou no Workspace como `Scene`, com 10 espinhos, sem uso.
- `studio/montar_boreal.luau` leva tudo para `LoboArtico_LOW.FX_Boreal`:
  - **Linhas:** Neon azul-gelo, `DoubleSided`; a pele liga nos ossos pelo nome.
  - **Espinhos:** Glass azul-gelo, ancorados, com os atributos `OssoEspinho`, `OffsetOsso`, `BaseLocal` e `TamanhoCheio`.
  - Tudo invisível até o Uivo.
- **Medido:** o import e o lobo em repouso diferem só por translação (30 ossos, desvio 0,0001, sem giro).
- **Dois defeitos achados e corrigidos:**
  1. o Import 3D solda as peças, e mover uma arrastava as outras; corrigido tirando as soldas antes de mover;
  2. as fitas saíram do Blender com a face para dentro e não apareciam; corrigido com `DoubleSided = true`. No próximo export, inverter as normais.
- **`Uivo_Cliente` r4:**
  - linhas com opacidade 35–55%, brilho correndo da cabeça para a cauda (1,5 s) e pico no uivo;
  - espinhos crescem a partir da base em 0,6 s no início do efeito e recolhem em 0,8 s no fim, presos ao osso a cada quadro;
  - saiu o Highlight dos cristais, que vazava pelo pelo.

**Teste em Play (16/11):**
- espinho 1: aparece com o efeito (1,3 s), tamanho cheio em ~1,9 s, recolhe até sumir em ~9,3 s;
- linha 3: transparência 0,47–0,65, pulsando;
- sem erro no console.
- Evidências: `review/studio_v41/folha_boreal_r4.jpg`, `zoom_boreal_r4.jpg` e os quadros em `boreal_r4/`.

**Observado na captura:**
- o conjunto fica um pouco "enevoado": brilho do Neon mais as faixas de neve passando na frente do corpo;
- os espinhos aparecem pouco nesta câmera;
- o avatar do jogador entrou na frente.

**Não feito / não testado:**
- sulco escuro ao lado das linhas;
- película de geada no dorso;
- linhas do pescoço meio escondidas pela juba;
- linhas e espinhos com o lobo andando ou correndo (o teste foi parado);
- celular.

**Status:** linhas e espinhos funcionando no Studio. Place não salvo, sem commit.

### 8.58 Linhas pintadas no corpo (r7b) + sem nada flutuando (16/11/2026)

**Pedido do usuário:** "quero que as linhas façam parte do corpo do lobo. Não quero que flutuem ao redor do lobo, mas sim, o poder do uivo implemente ao seu corpo, estes efeitos."

**Mudança de método:**
- As linhas deixaram de ser fitas soltas e passaram a ser **pintadas na textura de emissão do próprio corpo**.
  - `boreal/assar_linhas_corpo.py`: as fitas do r6 são assadas (Cycles EMIT, selected-to-active) na UV da `LOW_Corpo`.
  - `boreal/preparar_emissao_r7.py`: afina a máscara (r7b) e soma os brilhos antigos.
  - Resultado: `boreal/tex/LoboArtico_Corpo_emissao_boreal.png` (1024).
- Revisão no Blender: `boreal/prancha_boreal_r7.jpg` (faixas largas demais) → `prancha_boreal_r7b.jpg` (finas, aprovadas para o teste).
- **Imagem enviada à conta do usuário** com autorização ("Envie você") → `rbxassetid://111250623946372`.
- **No Studio, a SurfaceAppearance da `LOW_Corpo` recebeu:**
  - `EmissiveMaskContent` = a nova máscara (a original, `rbxassetid://114785580686867`, está guardada no atributo `EmissiveMask_Original`);
  - `EmissiveTint` (60, 160, 255);
  - `EmissiveStrength` 0 em repouso. Os brilhos antigos, mínimos, também ficam apagados em repouso.
- **`Uivo_Cliente` r5:**
  - no Uivo, a emissão do corpo acende (5 + 2,5 de respiração em 1,5 s + 7 no pico, com fade-in de 0,6 s e fade-out de 1,5 s) e volta a 0;
  - **removidas** a neve em órbita e as fitas soltas (guardadas em `ServerStorage.LoboArtico_Boreal_Retirados`, não apagadas);
  - continuam os espinhos que crescem do dorso, os olhos azul-gelo, a geada nos alvos e os sons.
  - Cópias: `Uivo_Cliente_r4_fitas.client.luau` e `Uivo_Cliente_r3.client.luau`.

**Testes em Play (16/11):**
- **Parado:** emissão 0 → 5–9 durante o efeito → 0. As linhas aparecem só no corpo (pata dianteira, pata traseira, flanco), sem nada em volta.
- **Correndo com o efeito:** 24,43 studs/s (20,36 × 1,2); emissão e espinhos ativos; espinhos presos ao dorso sem folga visível nos quadros.
  - O desvio medido de até ~1 stud foi tempo de leitura do teste; em repouso é 0,000–0,007.
- Evidências em `review/studio_v41/`:
  - `folha_boreal_r5.jpg`, `zoom_boreal_r5.jpg` (parado);
  - `folha_boreal_r5_corrida3.jpg`, `zoom_boreal_r5_corrida3.jpg` (correndo com o efeito).

**Observações:**
- As linhas ficam brancas-azuladas (emissão sobre pelo branco) e o conjunto fica um pouco mais claro com o bloom.
- Sem o "brilho correndo da cabeça para a cauda": a máscara é uma só, então o corpo inteiro respira junto.
- Sulco escuro e geada no dorso continuam pendentes.
- Os 3 LODs, LOD1 e LOD2, não receberam a máscara.
- Não testado no celular.

**Status:** efeitos do Uivo Boreal só no corpo, funcionando no Studio. **Visual APROVADO pelo usuário em 16/11/2026** ("Aprovado"): linhas pintadas no corpo (máscara r7b) + espinhos que crescem do dorso + olhos azul-gelo, sem nada flutuando. Place não salvo, sem commit.

### 8.59 Kit completo do Lobo Ártico no ensaio (16/11/2026)

**Commit anterior:** `f233ede`, com só o Lobo Ártico, autorizado pelo usuário ("Sim, commit"). `PROJECT-STATE.md` e `studio-em-uso.md` ficaram fora porque têm linhas de outros chats.

**Pedido:** "Prossiga com os poderes, seguindo o documento de poderes, já faça todos os poderes de uma vez."
- Base: `REFERENCIAS_PODERES_E_EFEITOS.md` v5.2, §1, §3, §0b e §5.4–5.7.
- O Uivo Boreal já estava pronto. Foram feitos os outros 4.

**Instalado (só em `Workspace.Teste_LoboArtico`; fontes em `studio/`):**
- **`Kit_Servidor` r3** (autoridade do servidor):
  - **Cometa Glacial:**
    - energia 22, recarga 9 s;
    - preparo de 0,25 s, depois voo em arco até 35 studs;
    - curva máxima de 120°/s;
    - obstáculo no caminho explode no ponto;
    - explosão: raio 8, dano 0,8 × mordida (8), lentidão 30% por 2 s.
  - **Avalanche:**
    - energia 15, recarga 6 s;
    - corrida teleguiada até 30 studs, curva máxima de 90°/s, inclina nas curvas;
    - para ao chegar no alvo, em obstáculo ou sem chão;
    - termina numa onda cônica: dano 1,2 × mordida (12), lentidão 30%;
    - deixa uma trilha de gelo por 3 s, e o inimigo que pisa nela ganha `Escorregando`.
  - **Mira:**
    - ordem: alvo travado, depois o mais próximo num cone de 60° até 40 studs, depois a direção do cliente (mouse/câmera);
    - exige linha de visão; um alvo travado escondido continua valendo por até 0,5 s.
  - **Instinto Boreal:**
    - marca de 8 s ao travar ou acertar;
    - detecta inimigos `SobNeve` a até 90 studs;
    - em nevasca (`workspace.Nevasca`): +12% de velocidade e +10% de esquiva.
  - **Pelagem Polar:**
    - `ImuneFrio` e `ImuneNeveProfunda`;
    - −20% de dano de gelo (`ReceberDano`);
    - parado ≥ 2 s na neve: `Camuflado`, alcance em que inimigos o notam ×0,6; some ao atacar ou ao se mover.
  - **Bônus somados:** `BonusVel_*` → `MultVelocidade` e `BonusEsquiva_*` → `ChanceEsquiva`, com teto de 35%.
  - **`ReceberDano`:** sorteia a esquiva antes de aplicar a resistência.
- **`Kit_Cliente`:**
  - **Comandos:**
    - PC: Q = Cometa, E = Avalanche, clique num inimigo trava o alvo, T solta;
    - toque: botões;
    - a direção da Avalanche é enviada a 10 Hz.
  - **Efeitos no corpo:**
    - casca de gelo (Highlight azul-gelo no próprio lobo) no voo do Cometa;
    - linhas do corpo e espinhos no preparo;
    - FOV +8 no voo;
    - no impacto: flash, estouro curto de 0,3 s, tremor e som de vidro;
    - neve compactada (Highlight branco) na Avalanche, com som de neve;
    - camuflagem (contraste cai em 1 s).
  - **Só para o dono:** marca (contorno + seta), pegadas dos inimigos (8 s) e luz azul nos inimigos detectados sob a neve.
- **Ajustes em scripts existentes:**
  - `Uivo_Servidor` r5: bônus somados, `AplicarLentidao` e `GastarEnergia` compartilhados, recusa com outro poder ativo;
  - `Uivo_Cliente` r6: o visual depende de `BonusVel_Uivo` (a nevasca não liga o Uivo);
  - `Controle_Servidor` r3: pausa durante `PoderAtivo`.
- **[ENSAIO], fora do documento:**
  - Cometa: velocidade 34, altura 5,5, alcance mínimo 8;
  - Avalanche: velocidade 24, cone de 10 studs com meio-ângulo de 35°, lentidão de 2 s;
  - trilha: o efeito é só o atributo `Escorregando`;
  - jogadores fora como alvo (PvP [A CONFIRMAR]).
- **Animações [PENDENTE no documento]:** usam os clipes aprovados como substitutos. Preparo = Arrancada; voo = quadro da Corrida congelado; fim = Frenagem.

**Testes em Play (16/11, alvos de ensaio criados só no Play):**
| Caso | Resultado |
|---|---|
| Nevasca liga/desliga | velocidade 1,12/0,15 de esquiva → 1,00/0,05 |
| 2000 golpes de gelo 10 | 4,9% de esquiva; dano por acerto 8,00 (físico 10,00) |
| Cometa no alvo travado | arco 5,5; dano 8 (100→92); WalkSpeed 16→11,2; marca; recarga recusada (6,7 s) |
| Cometa com parede | parou antes da parede ("obstaculo: Ensaio_Parede"); alvo atrás sem dano |
| Avalanche sem alvo | percorreu 30, seguindo a direção; trilha marcou `Escorregando` no inimigo do caminho |
| Avalanche com alvo atrás a 28,8 | não chega (curva de 90°/s gasta os 30 studs), sem acerto |
| Avalanche com alvo à frente | chegou em 11,6; dano 12; lentidão por 2 s |
| Camuflagem | ligou após 1,9 s parado na neve (×0,6); desligou ao atacar |
| Inimigo sob a neve a 81 studs | detectado |
| Pegadas | 3 em 10 studs do inimigo andando |

- **Defeitos achados e corrigidos:**
  - r1: o chão do voo era consultado com Y=0, achava o mapa embaixo e fazia o Cometa explodir parado;
  - r2: o Cometa pousava em cima do alvo; a r3 pousa 2,5 studs antes. **A r3 está instalada mas não foi testada em Play.**
- **Evidências:** `review/studio_v41/folha_kit_r1.jpg` e os quadros em `kit_r1/`. A câmera ficou longe; precisa de capturas de perto para a revisão visual.

**Não testado:**
- teclas reais, clique e toque;
- celular;
- vários jogadores;
- encosta, água e trilha de fato escorregadia;
- o giro medido no cliente deu até 118°/s por ruído de replicação (o servidor limita a 90°/s por código).

**Status:** kit completo funcionando no Studio (ensaio). Place não salvo; sem commit desta etapa. Pendentes:
- clipes próprios do Cometa e da Avalanche;
- revisão visual de perto;
- números [ENSAIO].

### 8.60 Clipes próprios do Cometa Glacial e da Avalanche — v42 no Blender (17/11/2026, aguardando revisão)

Gerador `BLENDER/Criaturas/Lobo_Artico_Ref/gen_kit_v42.py` sobre `anim_v41` (34 ações intactas) → `anim_v42/CR_LoboArtico_Anim.blend` (39 ações) + `anim_v42/kit_v42.json`. Mesmo construtor do bloco 4 (Repouso q0, tronco com pivô no quadril, patas plantadas por IK).

| Ação | Quadros | Tipo | Conteúdo |
|---|---|---|---|
| CometaPreparar | 8 (0,27 s) | uma vez | agacha (quadril −0,95, peso para trás), cabeça baixa mirando, orelhas para trás; marcador Salto 0,27 s |
| CometaVoo | 24 | laço | corpo esticado: dianteiras à frente, traseiras para trás, pescoço na linha das costas, cauda reta; leve ondulação. Sem altura (a trajetória é do servidor) |
| CometaPouso | 24 (0,8 s) | uma vez | toque (q0, marcador Impacto) → amortece fundo (q5) → Repouso (q24) |
| AvalancheCorrida | 14 (= Corrida) | laço | Corrida aprovada com camadas só em pescoço/cabeça baixos, orelhas coladas, boca entreaberta, cauda reta (patas idênticas à Corrida) |
| AvalancheOnda | 30 (1 s) | uma vez | finca as dianteiras e empurra peito e cabeça para baixo e à frente com a boca aberta (marcador Onda 0,2 s), volta ao Repouso |

QA: erro de IK 0 em todas; ponto mais baixo: sola dianteira −0,09 stud em CometaPouso q20 e −0,08 em AvalancheOnda q26 (mistura FK→IK perto do Repouso, mesmo método do v41); cauda do Preparar corrigida (descia abaixo do chão, agora sobe +8°). Pranchas: `review/v42_kit/revisao/kit_v42_{perfil_E,34_E,frente}.png` (`prancha_kit_v42.py`).
Pendente: aprovação visual → export/reimport (GLB por LOD) → JSON → KFS no Teste-animacoes → trocar os placeholders no `Kit_Servidor`. Inclinação nas curvas da Avalanche fica no código (rolagem do modelo), não no clipe.

**Vídeo-teste no Studio (17/11, pedido do usuário antes de aprovar):**
- Ponte: `studio/exportar_clipes_json_v42.py` → `studio/json_v42/` (5 JSON + `matrizes_v41.json`, mesmo rig) → `studio/montar_kfs_lobo_v42.luau`. Os 5 KFS foram para `ReplicatedStorage.Animacoes_LoboArtico` (laço só em CometaVoo e AvalancheCorrida; prioridade Action).
- Conferência: AvalancheCorrida × Corrida no Studio, mesma pose das pernas (diferença ≤ 0,006) e só pescoço/cabeça mudam.
- `Kit_Servidor` r4: troca os substitutos pelos clipes (Preparar acelerado para 0,25 s; Pouso 0,75 s; Onda 0,9 s). Backup local `Kit_Servidor_r3_placeholders.server.luau`; no place, `ServerStorage.LoboArtico_Backups.Kit_Servidor_r3`/`_r4`.
- **Achado no 1º vídeo:** nos dois poderes o peito do lobo terminava DENTRO do alvo. O pivô fica nas ancas e o código não contava os ~6 studs do corpo à frente.
- **r5:** `CFG.focinho = 6.2`, `folgaAlvo = 1.2`. O Cometa pousa a d − 7,4; os raios de obstáculo vão até o focinho; a explosão sai do peito (pivô + 3 à frente). A Avalanche para a 7,9 do alvo.
- Teste em Play r5:
  - Cometa: pivô a 7,85 do alvo, 8 de dano;
  - Avalanche: "chegou no alvo" após 16,6 studs, a 7,67, 12 de dano.
- Vídeo: `review/studio_v42/video_kit_v42_r1.mp4` (velocidade real + metade). Capturas em `cometa_r3/` e `avalanche_r2/`; o 1º vídeo, com o defeito, está em `cometa_r2/` e `avalanche_r1/`.
- Status: aguardando a revisão do usuário. Place não salvo; sem commit.

**Mais testes (17/11, pedido: alvo mais longe e Cometa mais alto) — Kit_Servidor r6:**
- Arco do Cometa: altura = min(10, distância × 0,32) [ENSAIO] (antes fixo 5,5). Saltos longos sobem até 10; saltos curtos não sobem reto.
- Play:
  - Cometa a 30 studs: atingiu, parou a 7,99 do alvo;
  - Cometa a 38 studs: atingiu, parou a 7,89;
  - Avalanche a 36 studs: "chegou no alvo" após 28,2 studs, a 8,00, 12 de dano.
- Vídeo: `review/studio_v42/video_kit_v42_r2.mp4`. Backups: `studio/Kit_Servidor_r5.server.luau` e `ServerStorage.LoboArtico_Backups.Kit_Servidor_r5`.
- Achado: os modelos `LODs_Reserva` estão no chão por volta de z −645, no caminho de testes mais longos para o norte.
- **Pedido novo (17/11):** efeitos 100% fiéis à imagem de referência PREPARO/VOO/POUSO enviada no chat, iguais em todos os poderes. Plano em etapas, aguardando aprovação.

### 8.61 Efeitos de gelo fiéis à referência — E1 no Blender (17/11/2026, aguardando revisão)

**Pedido:** efeitos 100% fiéis à imagem PREPARO/VOO/POUSO enviada no chat, iguais em todos os poderes (Uivo, Cometa, Avalanche). A imagem não está salva em disco (só no chat). Etapas: E1 espinhos + linhas; E2 casca de gelo do voo; E3 estilhaços do pouso e rastro; E4 Studio.

**E1 (r8):**
- Fontes:
  - `boreal/boreal_fx_r8.py` (sobre `anim_v42`) → `boreal/CR_LoboArtico_Boreal_r8.blend` + `export/boreal_fx_r8.json`;
  - `boreal/assar_linhas_r8.py` → `tex/LoboArtico_Corpo_linhas_raw_r8.png`;
  - `boreal/mascara_r8.py` → `tex/LoboArtico_Corpo_emissao_gelo_r8.png`;
  - render de revisão: `boreal/render_r8.py`.
- **Espinhos:** crista alta de cristais translúcidos em 11 posições, da nuca até o meio das costas.
  - Pico na cernelha: 2,35 × 0,86–1,08 de variação; menores para trás (0,46 no fim).
  - Cristais laterais em leque, ponta secundária e lascas na base.
  - Material de vidro com brilho nas bordas.
  - 1.088 tris. Cada posição é um objeto preso ao osso mais próximo (mesmo contrato do r6).
- **Linhas** (máscara de emissão na UV da LOW_Corpo, como no r7b):
  - espiral no ombro, atrás da juba; na juba o pelo cobria e borrava;
  - onda pelo flanco até a anca com volta, linha alta nas costas, barriga, pernas e cauda;
  - dos dois lados.
- **Iterações:**
  - r8a: fita torcida no peito virou "escada";
  - r8b: espiral borrada sob a juba;
  - r8d: fita mais fina não afina (o bake abre em leque);
  - r8e: erosão de 5 px, como no r7b → linhas finas.
- A "espinha de peixe" no ombro é a marca original do modelo aprovado, não uma linha nova.
- Prancha: `boreal/prancha_gelo_r8.jpg` (Repouso e CometaPreparar q8, perfil e 3/4).
- Pendente: aprovação do E1; no Roblox, trocar os espinhos (FX_Boreal) e a máscara (upload) e testar.
- **r8f (17/11, pedido "cristais mais baixos e decrescentes"):**
  - alturas 1,35 → 0,32, sempre caindo da nuca até o meio das costas (antes: pico 2,35 na cernelha);
  - variação leve de ±3% que nunca inverte a ordem;
  - linhas iguais ao r8e;
  - prancha `boreal/prancha_gelo_r8f.jpg`.
- **r8g (17/11, pedido "linhas alinhadas como a referência"):** a espiral do ombro passa a ser o centro (y −1,95, z 3,62, raio 0,62, 2 voltas) e as linhas saem dela.
  - **Do topo:** sobe ao dorso, corre sob a crista e desce na anca.
  - **Da ponta de trás:** corre pelo flanco, sobe ao quadril, contorna a coxa e continua pela perna traseira (Tíbia/Metatarso).
  - **De baixo:** desce pela pata dianteira (Antebraço/Metacarpo).
  - **Retiradas:** linha da barriga e linha solta das costas.
  - Prancha: `boreal/prancha_gelo_r8g.jpg`.
  - **Limite:** a juba (pelagem com atlas compartilhado) cobre a frente do ombro e a ligação espiral→pata dianteira perto do cotovelo, então essas partes ficam menos nítidas que na imagem.
- **r8h–r8j (17/11, "ainda não está igual" + "mais espaço entre os cristais, penteados para trás"):**
  - **Cristais:** 8 posições a cada ~0,72 (antes 11), eixo ~60° para trás; laterais e lascas também para trás; alturas 1,35 → 0,32 decrescentes.
  - **Espiral:** desceu para cima da pata dianteira (y −2,45, z 3,30, raio 0,62, 1,9 volta). Dela saem 4 linhas:
    - pescoço;
    - dorso → anca;
    - flanco → coxa → traseira;
    - frente da pata dianteira.
  - **Lição:** a máscara do jogo é 1024 (~25 px/stud no corpo). Voltas da espiral com menos de ~7 px de espaço viram borrão (r8h: raio 0,5 com 2,6 voltas = 4 px). A projeção curta do bake (r8i) não resolvia e engrossava as linhas; o bake voltou ao do r7b com erosão de 5 px.
  - **Arquivos:** `boreal/prancha_gelo_r8j.jpg` e `boreal/zoom_ombro_r8j.jpg`.
  - **Observação:** a pequena espiral com "seta" no alto do ombro é a marca original do modelo aprovado (máscara antiga), não faz parte da referência.
- **r8k–r8l (17/11, pedido "o símbolo redondo em sua perna"):**
  - **Posição:** espiral na parte de cima da pata dianteira, nos dois lados (y −3,06, z 2,62, raio 0,42, 1,5 volta).
  - **r8k falhou:** o bake deformava a espiral na perna estreita e curva, e o anel cruzava costuras de UV (erro ~700 px).
  - **Correção r8l:**
    - `boreal/uv_simbolo_r8.py` varreu a perna atrás de um ponto sem costura (anel de raio 0,42 sem salto > 4 px; erro E 2,9 px, D 7,7 px);
    - o mesmo script converte cada ponto da espiral redonda em 3D para UV;
    - `mascara_r8.py` desenha a espiral direto na máscara (4096 → 1024).
  - **Conectores:** as 4 linhas (pescoço, dorso → anca, flanco → coxa → traseira, frente da pata) partem do anel.
  - **Arquivos:** `boreal/prancha_gelo_r8l.jpg` e `boreal/zoom_perna_r8l.jpg`.
  - **E1 r8l APROVADA pelo usuário (17/11).**

### 8.62 Efeitos de gelo E2 — casca vítrea do voo + rastro (17/11/2026)
- **Pedido:** VOO da referência PREPARO/VOO/POUSO; casca de gelo vítreo sobre corpo e patas + rastro de cristais.
- **Script:** `boreal/casca_e2.py` (roda sobre `CR_LoboArtico_Boreal_r8.blend` → `CR_LoboArtico_Boreal_E2.blend`, relatório `export/casca_e2.json`).
  - **Casca** `Casca_Gelo_E2`: cópia da LOW_Corpo com Decimate 0,10 em repouso (pesos mantidos), empurrada 0,08–0,15 pela normal com variação (placas irregulares), sombreamento plano, Armature no mesmo rig → acompanha qualquer clipe. 1.994 tris. Material vidro (Transmission 0,9, IOR 1,31), borda ciano por Layer Weight (emissão ×3, alfa 0,10–0,75).
  - **Rastro** `Rastro_Gelo_E2`: 70 cristais alongados + 160 grãos de pó num cone que sai da anca para trás, diminuindo com a distância; preso ao osso Quadril só para revisão. 1.900 tris. No Roblox vira ParticleEmitter.
- **Render:** `boreal/render_e2.py` (cópia do render_r8 com vista traseira 3/4), CometaVoo q0 e q12 → `boreal/review_e2/`, prancha `boreal/prancha_gelo_e2.jpg`.
- **Status:** só Blender; aguarda revisão do usuário. Studio não tocado.
- **E2 APROVADA pelo usuário (17/11).**

### 8.63 Efeitos de gelo E3 — estilhaços do pouso (17/11/2026)
- **Pedido:** POUSO da referência: lascas de gelo explodindo no impacto. A casca do voo some e "vira" as lascas.
- **Script:** `boreal/estilhacos_e3.py` (sobre `CR_LoboArtico_Boreal_E2.blend` → `CR_LoboArtico_Boreal_E3.blend`, relatório `export/estilhacos_e3.json`).
  - `Estilhacos_Chao_E3`: coroa de 78 cristais cravados em 2 anéis elípticos, inclinados para fora, maiores perto do lobo (1.504 tris).
  - `Lascas_Ar_E3`: 55 lascas voando para fora/cima + 170 grãos de pó (1.800 tris).
  - `Placa_Gelo_E3`: crosta rachada em placas irregulares (r2; a r1 em fatias regulares parecia pizza) (109 tris).
  - Casca e rastro da E2 escondidos no render do pouso.
- **Roblox (E4):** coroa = Parts que crescem e somem; lascas/pó = ParticleEmitter; crosta = decal/placas que derretem.
- **Render:** CometaPouso q1 e q6 → `boreal/review_e3/`, prancha `boreal/prancha_gelo_e3.jpg`. Só Blender; Studio não tocado.
- **E3 APROVADA pelo usuário (17/11).**

### 8.64 Efeitos de gelo E4 — no Studio (Teste-animacoes, 17/11/2026)
- **Export:** `boreal/exportar_e4.py` → `boreal/export/CR_LoboArtico_GeloFX_E4.glb` (0,4 MB): rig, Espinho_01..08 (r8l), Casca_Gelo (pele), Molde_Coroa_1..3, Molde_Lasca_1..2, crosta.
- **Import 3D (usuário):** entrou como `Scene`. Lição: o Import 3D nomeia as peças pela **malha**, não pelo objeto (`Casca_Gelo_E2`, `Placa_Gelo_E3`) → `studio/montar_gelo_e4.luau` renomeia antes de montar; o que sobra fica em `Workspace.Import_GeloFX_E4`.
- **Montagem:** `montar_gelo_e4.luau` (T por 30 ossos, giro 0). FX_Boreal anterior guardado em `ServerStorage.LoboArtico_Backups.FX_Boreal_r6`. Base dos espinhos: Blender (x,y,z) → Roblox (−x, z, y) a partir do pivô (conferido com o r6). Moldes guardados em y −300 (acima do FallenPartsDestroyHeight).
- **Imagens enviadas à conta do usuário:** máscara das linhas r8l `rbxassetid://103482067734616` (LOW_Corpo SurfaceAppearance; a anterior 111250623946372 ficou no atributo `MascaraAnterior`) e lasca do rastro `rbxassetid://89705690599635` (`boreal/tex/LoboArtico_LascaGelo_sprite.png`; levou alguns minutos para ficar disponível).
- **`studio/Kit_Cliente.client.luau` r2** (backup local `Kit_Cliente_r1_highlight`, no place `LoboArtico_Backups.Kit_Cliente_r1`):
  - Cometa: casca real (`Casca_Gelo`, Glass) só no VOO (forma em 0,15 s); rastro = 2 ParticleEmitter no osso Quadril (lascas 160/s + pó 300/s); pouso = coroa de cristais (2 anéis elípticos, crescem 0,12 s, afundam e somem até 1,7 s) + 28 lascas balísticas + crosta que derrete em 2,4 s + pó.
  - Avalanche: mantém a neve no corpo; ganhou espinhos, linhas e olhos; estouro de gelo menor (escala 0,6) na onda.
  - Olhos azul-gelo nos dois poderes (pontos Neon nas pálpebras, como no Uivo).
- **Teste em Play (17/11):** Cometa a 30 studs (2 vezes; r2 com rastro reforçado) e Avalanche a 30 studs; sem erros de script no console. Capturas `review/studio_v42/e4_cometa_r1`, `e4_cometa_r2`, `e4_avalanche_r1`, folhas `folha_e4_*.jpg`, zoom `zoom_e4_r2.jpg`, vídeo **`review/studio_v42/video_kit_e4_r1.mp4`** (36 s, real + metade).
- **Uivo Boreal:** usa os mesmos espinhos/máscara (contrato igual); não foi gravado nesta rodada.
- **Place não salvo.** Aguarda revisão do usuário.
- **E4 APROVADA pelo usuário (17/11).**

### 8.65 Cometa r7 — segue o alvo, longo alcance (17/11/2026)
- **Pedido:** "esse ataque segue o alvo, pois ele deve ter um longo alcance".
- **Antes (r6):** a distância do salto era fixada na partida (teto 35) e a mira só travava até 40 → alvo em movimento ou longe ficava fora.
- **`studio/Kit_Servidor.server.luau` r7** (backup local `Kit_Servidor_r6.server.luau`; no place `LoboArtico_Backups.Kit_Servidor_r6`):
  - cometa.alcance 35 → **60**, giro 120 → **240 °/s**, vel 34 → **40**; mira.dist 40 → **65** (todos [ENSAIO]);
  - no voo, o ponto de pouso **acompanha o alvo** a cada quadro (distância restante − focinho − folga, suavizada, teto = alcance); a altura do arco é fixada na partida (teto 10) para não pular.
- **Teste em Play na `Pista_Ensaio`** (o piso do teste acaba antes de 55 studs; o personagem precisou ir para perto da pista por causa do streaming — sem isso a câmera mostrava só o vazio):
  - alvo parado a 55 studs: percorreu 46,6, atingiu (8 de dano);
  - alvo fugindo a 6 studs/s em zigue-zague (começo a 40): percorreu 42,1, virou junto e atingiu (8 de dano).
- **Evidência:** `review/studio_v42/r7_cometa_55`, `r7_cometa_fuga`, folhas `folha_r7_*.jpg`, vídeo **`review/studio_v42/video_cometa_r7.mp4`** (30 s). O avatar do jogador aparece no quadro.
- **Place:** Team Create já gravou (save_place: sem mudanças pendentes); conferido no Edit: servidor r7, cliente r2, casca, 6 moldes, máscara nova.

### 8.66 Ataque básico andando — v43 (17/11/2026)
- **Pedido:** "mordida e garra: em vez de atacar parado, atacar andando; senão não existe PvP de verdade".
- **Antes:** o Lobo Ártico ainda não tinha ataque básico (nem clipe, nem código; só `CFG.mordida = 10`).
- **Solução:** clipes **parciais** — só os ossos do golpe têm chave; no Roblox tocam em prioridade **Action2** por cima de Repouso/Andar/Trote/Corrida e o resto do corpo segue a locomoção.
- **`gen_ataque_v43.py`** (sobre anim_v42 → `anim_v43/CR_LoboArtico_Anim.blend` + `ataque_v43.json`): 15 q (0,5 s) cada.
  - Mordida1 (bote frontal, contato q6 = 0,2 s) e Mordida2 (bote lateral que rasga girando a cabeça) — Pescoco1/2, Cabeca, Mandibula, Orelhas (6 ossos);
  - GarraE / GarraD (ergue a pata e golpeia para baixo, contato q7 = 0,233 s) — mesmos 6 + Umero/Antebraco/Metacarpo/Dedos do lado (10 ossos).
- **Revisão:** `render_ataque_v43.py` sobrepõe cada golpe a Repouso, Andar e Corrida (como o Roblox faz) → `review/v43_ataque/revisao/ataque_v43_*_perfil_E.jpg` (`prancha_ataque_v43.py`).
- **Servidor preparado (só arquivo local, não instalado):** `studio/Kit_Servidor.server.luau` r8 (backup `Kit_Servidor_r7.server.luau`): ação de rede `basico`; sequência Mordida1 → GarraE → Mordida2 → GarraD (reinicia após 1 s sem atacar), intervalo 0,5 s, dano 10 (mordida) / 8 (garra), alvo no cone de 75° a até 3,5 do focinho medido **no instante do contato**; **não** marca PoderAtivo (o Controle continua movendo o lobo). Valores [ENSAIO].
- **Status:** aguarda revisão dos clipes; Studio não tocado.
- **Studio (17/11, aprovado "ir ao Studio"):**
  - `studio/exportar_ataque_json_v43.py` → `studio/json_v43/` (só os ossos com chave) e `studio/montar_kfs_lobo_v43.luau`: ossos animados com Weight 1; ossos que só ligam a raiz aos animados com **Weight 0** (caminho); o resto fica fora. Prioridade **Action2**, marcador `Contato`. **Confirmado em Play: as Poses de peso 0 não congelam a locomoção.**
  - Instalados: `Kit_Servidor` r8 e `Kit_Cliente` r3 (backups no place `LoboArtico_Backups.Kit_Servidor_r7` e `Kit_Cliente_r2`). Cliente: clique esquerdo ataca (segurar repete a cada 0,5 s) e, se cair num inimigo, trava o alvo; botão de toque "Atacar" (e R2 no controle).
  - **Teste em Play na `Pista_Ensaio`** (controle assumido por script, alvo acompanhando 8 studs à frente):
    - andando: 17,8 studs em 6 s sem parar (3 studs/s), 10 golpes, alvo perdeu 82;
    - correndo: 106,9 studs, velocidade 20,36 mantida até o fim, 8 golpes, alvo perdeu 64.
  - Evidência: `review/studio_v43/basico_andar`, `basico_correr`, folhas `folha_basico_*.jpg`, vídeo **`review/studio_v43/video_ataque_basico_v43.mp4`** (42 s). Console sem erros de script.
  - Aguarda revisão do usuário.
- **Mordida r2 (17/11, usuário: "por que ele não abre a boca ao morder"):**
  - Causa: **sinal da mandíbula invertido** — no rig, `girar("Mandibula","X", +g)` ABRE (convenção do gen_bloco4_v41: "boca > 0 fecha" com −). A r1 usava −, então a mandíbula subia para dentro do crânio (só aparecia uma linha fina); além disso abria só por 3 quadros com a cabeça já baixa.
  - Correção em `gen_ataque_v43.py`: boca abre já no recuo (+40°, rosto à mostra, q0→q2,5), segura e fecha de estalo no contato (q5→q6), solta +11° depois; garra com rosnado entreaberto (+14°, sinal corrigido).
  - Revisão Blender `review/v43_ataque/revisao/mordida_boca_r2.jpg` (close da cabeça); clipes reexportados e remontados no place; close em Play andando `review/studio_v43/mordida_boca_r2`, `zoom_mordida_boca_r2.jpg`, vídeo `review/studio_v43/video_mordida_boca_r2.mp4`. (Neste teste o alvo não acompanhou por erro do script de teste — o laço do alvo começou antes de ele entrar no Workspace; o dano já tinha sido provado no teste anterior.)
  - **Atenção:** o mesmo sinal invertido existe em `gen_kit_v42.py` (CometaPouso `boca 4`, AvalancheOnda `boca 24`, AvalancheCorrida `boca 7`): nesses clipes a boca **fecha** em vez de abrir. Não corrigido ainda.
- **r3 (17/11, usuário: "quero animação nos olhos; as patadas estão estranhas, não precisa colocar tão para cima"):**
  - **Olhos:** os 4 golpes passam a animar as 4 pálpebras (mesmo método da piscada do Repouso: rotação local em X com os ângulos de `rig_pivos.json`): estreitam mirando no preparo (~40%) e fecham por reflexo no contato (mordida 92%/85%, garra 75%/65%), depois reabrem.
  - **Piscar** (novo clipe parcial, 8 q = 0,27 s, só as 4 pálpebras): `Kit_Servidor` r9 toca a cada 2,5–6,5 s em **Action3** (acima dos golpes), andando, correndo ou parado. Backup `Kit_Servidor_r8` (local e no place).
  - **Garra mais baixa:** úmero −62° → −32°, antebraço −30° → −16°, metacarpo 38° → 26°, giro para dentro −10° → −6°.
  - Revisão Blender `review/v43_ataque/revisao/ataque_r3_olhos_garra.jpg` + `zoom_olhos_r3.jpg`; Studio: clipes remontados (Mordida1/2 10 ossos, Garras 14, Piscar 4), Play andando: close `review/studio_v43/olhos_r3` (piscada em 1,16 s; olhos estreitando em 3,3 s), lateral `garra_r3`, `zoom_olhos_r3.jpg`, vídeo `review/studio_v43/video_ataque_r3_olhos_garra.mp4`. Dano conferido: 6 golpes, alvo −46.

### 8.67 Ataque básico v43 r4 — patadas e mordidas reconstruídas (17/11/2026, só Blender)
- **Pedido:** "agora nem se parecem com patadas" + roteiro do usuário (bote que avança até o contato, boca legível, patada em arco baixo e curto distinguível de um passo, locomoção preservada; integração no Studio só com nova autorização).
- **M0:** sem revisão posterior à r3 (anim_v43 e gen_ataque_v43 de 16:49). Lidos CLAUDE.md, ORGANIZACAO-CHATS, §8.66, regras oficiais (§1: ataque básico = sequência de mordidas e garras com animações variadas, fora dos slots). Referência `REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png` (lobo parado de perfil 3/4: postura horizontal, pescoço com juba, patas largas — serve de cabeçalho nas pranchas).
- **Pesquisa (17/11):** lobos quase não agarram com as patas — sem garras retráteis nem antebraço que gira; dependem da boca e da perseguição ([NPS Yellowstone](https://www.nps.gov/yell/learn/ys-24-1-understanding-the-limits-to-wolf-hunting-ability.htm); [Paleobiology 2005](https://bioone.org/journals/paleobiology/volume-31/issue-1/0094-8373(2005)031<0056:WTPCIT>2.0.CO;2/Were-there-pack-hunting-canids-in-the-Tertiary-and-how/10.1666/0094-8373(2005)031<0056:WTPCIT>2.0.CO;2.full); [MacNulty et al. 2009](https://wyofile.com/wp-content/uploads/MacNulty-et-al-2009_body-size.pdf)). Lobos-árticos atacam bois-almiscarados isolando filhotes ([Ynet/Amos Nachoum](https://www.ynetnews.com/environment/article/r1rlbk5jfx); [National Geographic](https://www.nationalgeographic.com/animals/article/arctic-wolves-harsh-lives-living-on-top-of-the-world-feature)). Força de mordida cai com a abertura ([dingo FE, PMC2376057](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2376057/)). **Não encontrei filmagem com minutagem verificável** (não consigo assistir vídeo quadro a quadro); nenhuma minutagem foi inventada. Consequência: a garra é **adaptação de jogo** do gesto de pisar/prender com a dianteira.
- **QA da r3 (`medir_ataque_r4.py`, golpe sobre a locomoção como no Roblox):** Mordida no contato = focinho **0,42–1,12 para TRÁS** e **0,65–1,94 para BAIXO** (despenca); Garra = pata vai 2,0 à frente e 0,93 para cima e no contato fica **0,82 atrás** da posição da locomoção (desenho de passada); na Corrida a pata atravessava o chão até 0,95.
- **r4 (`gen_ataque_v43r4.py` sobre CÓPIA da r3 → `anim_v43r4/`; r3 copiada como `R3_*` para comparar; r3 intacta em anim_v43):**
  - Mordida1/2: trajetória-alvo do focinho resolvida quadro a quadro (busca nos ângulos de Pescoco1/2; Cabeca dá a mira) + **avanço do pescoço** (translação da base do Pescoco1 até 0,60, = empurrão dos ombros; o Pescoco1 é "conectado" no Blender e foi desconectado só no .blend de trabalho, repouso idêntico). Recua e ergue a cabeça (q0–3) → bote à frente/abaixo → **contato q6** (boca 44° em q4–q5, fecha para 4° em q6) → puxa (Mordida2 rasga girando) → volta. Mordida2: focinho 0,8–0,9 para o lado do bote.
  - GarraE/D: pata por IK (`marcha_v21.ik`/`alvo_pata`), spline Catmull-Rom (acelera continuamente até o contato): preparo discreto (sobe 0,30, carpo dobrado 55°) → alcance (0,80 à frente, 0,42 acima, dedos abertos) → **contato q7** (1,15 à frente, junto ao chão, um pouco para dentro, dedos cravando) → puxa para trás pelo chão → recolhe dobrando o carpo (35°). Cabeça acompanha o lado, boca em rosnado.
  - Olhos: estreitam mirando (0,40) e piscam forte só no contato (0,75 mordida / 0,60 garra).
  - **Variantes `_Corrida`** (4 clipes): no galope o ombro desce 0,39–1,07 → pata 0,90 mais alta e focinho 0,70 mais baixo o clipe todo.
- **QA r4 (contato):**
  - Mordidas: focinho **0,25–0,65 À FRENTE** em todas as marchas (r3: 0,42–1,12 para trás); boca 44° → 4° no contato; Corrida com variante: altura −0,06 (r3/base +0,58).
  - Garras: altura máx da pata 0,72 (Repouso); no chão no contato e no puxão (Andar −0,01/−0,03; Trote até −0,15 nos quadros de entrada/saída; Corrida com variante até −0,17, r3 −0,95/−1,07); outra pata sempre ≥ 1,35 de distância (sem cruzar); ombro não sobe pelo golpe (as subidas medidas 0,18–0,29 são iguais na r3: vêm da locomoção); torção do carpo (medida swing-twist) 15–34 na base e até 50 na variante Corrida E — acompanha a dobra do carpo; o Andar aprovado tem 15–21 na mesma medida → **conferir no close das patas**.
- **Export parcial validado** (`studio/json_v43r4/`, mesmo exportador): mesmos ossos da r3 (10 mordida, 14 garra, 4 Piscar); marcadores **Contato 0,2 / 0,233 = iguais à r3 → servidor não muda**; única translação = Pescoco1 0,466 (espaço do osso) nas mordidas, mesmo canal da translação do Quadril já usada na locomoção. 6,4–9,2 KB por clipe.
- **Piscar × golpes:** o Piscar (Action3) substitui as pálpebras do golpe — na mira a pálpebra está a 7–8° e o Piscar força 0° no início/fim (olho "abre" no meio do golpe). **Proposta (servidor, aguarda aprovação):** não disparar o Piscar enquanto um golpe toca (+0,2 s).
- **Sincronização necessária para as variantes (servidor, aguarda aprovação):** em `basico()`, usar `<nome>_Corrida` quando a marcha for Corrida/Arrancada (atributo `VelAtual` > ~12 ou marcha do Controle); mesmos marcadores, então o tempo do dano não muda.
- **Custo:** cada golpe = 1 faixa extra de 0,5 s com 10–14 ossos (273–353 instâncias de KFS); 9 clipes parciais + 4 variantes ≈ 3,7 mil instâncias no total, avaliadas só durante o golpe; nenhuma partícula, malha ou script novo → custo desprezível em PC e celular. No jogo publicado são 13 Animations a publicar.
- **Limitações:** clipe parcial não controla o tronco nem a outra dianteira: em fases da passada em que a outra dianteira está no ar, as duas ficam fora do chão por instantes (Andar/Trote); o golpe começa e termina na pose de repouso dos ossos com chave (fade 0,06 s no jogo); avanço do pescoço estica levemente a pele entre ombro e pescoço (conferir no close).
- **Evidências r4 (Blender, 17/11):** `BLENDER/Criaturas/Lobo_Artico_Ref/review/v43r4/revisao/`:
  - `comp_<golpe>.jpg` — referência + r3 × r4 sobre Andar (corpo inteiro, close da cabeça e de frente nas mordidas, close das patas nas garras), contato em vermelho;
  - `bases_<golpe>.jpg` — r4 sobre Repouso, Andar (2 fases), Trote e Corrida (variante);
  - `video_ataque_r3_x_r4.mp4` — sequência Mordida1 > GarraE > Mordida2 > GarraD, r3 | r4 lado a lado (perfil + close), depois r4 em Trote e Corrida, velocidade real e metade;
  - `qa_r4.json` — números por quadro.
  - Scripts: `gen_ataque_v43r4.py`, `render_ataque_r4.py`, `prancha_ataque_r4.py`, `medir_ataque_r4.py`, `review_r4_lotes.sh`. Render Eevee 8 amostras, 480×330, um processo do Blender por vez.
- **Studio NÃO tocado nesta rodada.** Integração (remontar 9 clipes + 4 variantes, servidor escolhendo a variante pela marcha e sem Piscar durante golpe) aguarda revisão e autorização, com reserva em `DOCS/estado/studio-em-uso.md`.

### 8.68 Garras v43 r5 — sincronizadas por fase (17/11/2026, só Blender)
- **Pedido:** roteiro "Corrigir as patadas do Lobo Ártico" (GarraE/D + variantes de Corrida sobre cópia da r4; mordidas e locomoção preservadas; sem afundar, sem arrasto, sem torção visível, apoio coerente; Contato q7 = 0,233 s e 0,5 s mantidos; integração só com nova autorização).
- **M0:** base `anim_v43r4/` (17:54), sem revisão posterior. Referência de postura `lobo-artico-referencia.png` no cabeçalho das pranchas. Pesquisa: mesmas fontes da §8.67; nenhuma filmagem com minutagem verificável → patada = adaptação de jogo.
- **QA de fases (`medir_garra_r5.py`):** golpe sobreposto à locomoção como no Roblox (Action2; fade de entrada 0,06 s; fim seco), varrendo **todas** as fases de início de Andar (36), Trote (18) e Corrida (14); mede afundamento da sola (3 pontos, contra a altura de apoio), arrasto no mundo com o deslocamento da marcha (3,0 / 6,667 / 20,357 studs/s), perda de apoio **causada** pelo golpe (dianteira do golpe apoiada na passada e nenhuma dianteira apoiada no composto), virada/rolagem visível do pé, giro que não é flexão (rotação no mundo sem a componente no eixo lateral = dobra natural), salto no fim (descontando o que a passada anda no quadro) e folga até o alvo de ensaio (HRP 2×5×2, face a 7 studs do pivô).
- **Diagnóstico r4 (pior fase):** Andar: afunda 0,19–0,22, arrasto 0,81–0,83, perda de apoio em 24–25 de 36 fases, **salto no fim 1,55–1,65**; Trote: afunda 0,39, arrasto 0,78–0,80, perda em 18/18, salto 2,0–2,1; Corrida (variante r4): afunda 0,50–0,71, arrasto 1,09–1,18, salto 2,9–3,3. Causa: com pose de início/fim FIXA, a camada parcial não sabe onde a passada está — a perna "pula" para a passada no fim e afunda/arrasta na entrada/saída. Uma r5a com o mesmo princípio (contato no alvo, sem cravar) melhorou pouco → **a camada parcial sozinha não resolve com início em fase qualquer**.
- **r5 (`gen_garra_v43r5.py`, cópia da r4 → `anim_v43r5/`; r4 das garras guardada como `R4_*`; mordidas, Piscar, `Mordida*_Corrida` e locomoção intactos):**
  - **Repouso (`GarraE`/`GarraD`, parado):** preparo discreto (descola até q1,5; pata recolhida sob o peito com o carpo dobrado 55° em q3,5) → acelera (dedos abrindo) → **contato no alvo em q7** (1,30 à frente, 0,42 acima do apoio, perna estendida, dedos abertos) → garras fecham no impacto → recolhe dobrando o carpo → volta ao apoio. Não crava no chão (sem puxão = sem arrasto) e sem translação para dentro.
  - **Andando, trotando, correndo (`GarraE/D_Andar`, `_Trote`, `_Corrida`, sincronizadas):** cada clipe começa no quadro em que aquela pata **descola** na passada (E: Andar 32, Trote 8, Corrida 10; D: Andar 14, Trote 17, Corrida 9) e mistura **posições** (alvo do IK vai da pata da passada ao alvo do golpe), devolvendo a pata ao chão **no quadro em que a passada a apoiaria** (Andar q13, Trote q10, Corrida q9–10) — as rotações só voltam às da passada nesses 2 últimos quadros, onde as posições já coincidem.
- **QA r5 (na fase sincronizada; dois lados):** afundamento 0,000–0,012 (Repouso 0,016–0,018); arrasto causado 0,00 (Repouso 0,04); perda de apoio causada: nenhuma; salto extra no fim 0,00; giro que não é flexão em relação ao repouso ≤ 3,2° (os 18,7° de "rolagem" do lado E são da própria passada aprovada no balanço, não do golpe); altura no contato 0,53–0,66; folga até a face do alvo de ensaio 1,57–1,79 (o alcance de acerto do servidor cobre; visualmente a pata não encosta no alvo do teste). **Fora de fase** as mesmas garras voltam a falhar (afunda até 0,61, salto até 2,7) → a sincronização é obrigatória.
- **Export parcial (`studio/json_v43r5/`):** Mordida1/2 e Piscar **idênticos à r4**; garras com os mesmos 14 ossos e **Contato 0,233**; 6 garras sincronizadas novas + `Mordida*_Corrida`; 13 clipes, 102 KB.
- **Sincronização necessária (servidor/controle — PROPOSTA, não alterada):** quando for a vez de uma garra na sequência, escolher o lado cuja pata dianteira **descola primeiro** na passada atual e tocar `Garra<lado>_<marcha>` exatamente nesse instante (usa o tempo da faixa de locomoção: E descola em 1,067 s/0,267 s/0,333 s e D em 0,467 s/0,567 s/0,300 s do ciclo de Andar/Trote/Corrida). Espera máxima = meio ciclo (Andar 0,6 s, Trote 0,3 s, Corrida 0,23 s); o dano continua 0,233 s após o início do clipe. Parado: `Garra<lado>` sem espera. Transições de marcha (AndarParaTrote etc.) ainda não têm garra própria → usar a versão parada ou esperar a marcha estabilizar.
- **Custo:** 1 faixa extra de 0,5 s com 14 ossos por garra; 13 clipes (≈ 4,2 mil instâncias de KFS), 102 KB de JSON; avaliados só durante o golpe → desprezível em PC e celular. No jogo publicado: 13 Animations.
- **Evidências r5 (Blender):** `BLENDER/Criaturas/Lobo_Artico_Ref/review/v43r5/revisao/`: `comp_GarraE.jpg` e `comp_GarraD.jpg` (referência | r4 na pior fase | r5 sincronizada sobre Andar; corpo inteiro, close lateral das patas com o alvo de ensaio, close de frente sem o alvo), `bases_GarraE.jpg` e `bases_GarraD.jpg` (r5 em Repouso, Andar, Trote e Corrida, corpo e patas), `video_garras_r4_x_r5.mp4` (dois lados × quatro bases, r4 | r5 + close das patas, velocidade real e metade; legenda com afundamento/salto/arrasto do QA), `qa_garra_r5.json` (todas as fases). Scripts: `gen_garra_v43r5.py`, `medir_garra_r5.py`, `render_garra_r5.py`, `prancha_garra_r5.py`, `review_r5_lotes.sh`.
- **Limitações:** a patada continua baixa (contato 0,53–0,66 acima do apoio) e a diferença para um passo vem do carpo dobrado no preparo, da pata parando no ar na altura do alvo e do recolhimento — legível em close, discreta no corpo inteiro a distância; a pata não encosta no alvo de ensaio (falta 1,6–1,8 stud; o servidor acerta por alcance); garras de transição de marcha (AndarParaTrote etc.) não existem; sem a sincronização no servidor, as versões por marcha falham como a r4.
- **Studio NÃO tocado.** Integração (remontar 13 clipes, servidor escolhendo lado/marcha e disparando no descolamento, sem Piscar durante golpe) aguarda aprovação expressa, M0 e reserva em `DOCS/estado/studio-em-uso.md`.
- **Integração no Studio (17/11, aprovado "Aprovar e integrar"; Teste-animacoes reservado):**
  - 13 clipes r5 montados (`studio/json_v43r5/` + `montar_kfs_lobo_v43r5.luau`; Action2; marcadores Contato).
  - **`Kit_Servidor` r10/r10b** (backup `Kit_Servidor_r9` local e no place): na vez da garra, se o Controle está em marcha (`CtrlModo = Laco`), acha a faixa da marcha (comprimento do ciclo) e escolhe o lado cuja pata descola primeiro (`DESCOLA` do gen_garra_v43r5), espera esse instante e toca `Garra<lado>_<marcha>` no ritmo da faixa; parado/transição = `GarraE`/`GarraD`; na Corrida as mordidas usam `Mordida*_Corrida`; o dano sai 0,233 s (garra) / 0,2 s (mordida) após o início do clipe; **Piscar não dispara durante o golpe (+0,2 s)**; r10b: o reinício da sequência conta do golpe tocado (a espera da garra fazia voltar sempre à Mordida1 — achado no teste).
  - **Teste em Play (Pista_Ensaio, alvo acompanhando 8 studs à frente):** parado 7 golpes/7 acertos (sequência completa); andando 8/8 (GarraD_Andar e GarraE_Andar alternando, espera 0,15–0,53 s); trotando 8/8 (GarraE/D_Trote, espera 0–0,03 s após a troca de marcha); correndo 8/8 (Mordida1_Corrida, GarraD_Corrida, espera 0,09–0,28 s). Sem erros de script.
  - Evidência: `review/studio_v43r5/{repouso,andar,trote,corrida}`, folhas `folha_*.jpg`, vídeo **`review/studio_v43r5/video_garras_r5_studio.mp4`** (75 s, real + metade).
  - **Limitações observadas:** durante a Arrancada e as trocas de marcha (Controle fora de `Laco`) tocam as garras paradas; no galope as duas dianteiras descolam quase juntas (q9/q10), então a espera pode chegar perto de um ciclo (0,47 s) e o lado escolhido tende a ser o mesmo; a câmera do vídeo é lateral e de longe (closes de pata e sola estão nas pranchas do Blender).

### 8.69 Garras só na caça de presa pequena (17/11/2026) — decisão do usuário
- **Decisão:** "sem garras, somente para animais pequenos de caça, como javali, coruja, etc... No combate não." → **combate = só mordidas** (Mordida1 ↔ Mordida2, com `_Corrida` correndo); **garras só contra presa pequena de caça**.
- **`studio/Kit_Servidor.server.luau` r11/r11b** (backup `Kit_Servidor_r10b` local e no place): o alvo do pedido (`escolherAlvo`) decide a sequência — presa pequena → `Mordida1 > Garra > Mordida2 > Garra` (garras sincronizadas da §8.68); qualquer outro alvo → `Mordida1 > Mordida2`. Atributo `BasicoModo` = `caca`/`combate`.
  - **Presa pequena [PROVISÓRIO]:** atributo `PresaPequena = true` no modelo (contrato proposto para os chats de fauna) **ou** nome/`Especie` contendo "Javali" ou "Coruja" (exemplos do usuário). Outras espécies (Lebre Ártica, Rato Espinhoso, etc.) só entram com decisão do usuário.
  - r11b: tolerância de 0,05 s no intervalo e reinício da sequência 1,0 → 1,2 s (segurando o botão a sequência voltava à Mordida1 quando um pedido chegava um pouco cedo).
- **Teste em Play (17/11):** combate andando 7/7 só mordidas; caça andando contra `Javali_Teste` 7/7 com GarraD_Andar/GarraE_Andar entre as mordidas (−64); combate parado após r11b: Mordida1 > Mordida2 alternando 9/9 (−90). Sem erros de script.
- Clipes de garra (parados e sincronizados) continuam no place para a caça.

### 8.70 Sem garras + boca do kit corrigida (17/11/2026)
- **Decisão do usuário:** "esqueça da garra, não é necessário" → **ataque básico = só mordidas** (Mordida1 ↔ Mordida2, `_Corrida` correndo), em combate e na caça. `studio/Kit_Servidor.server.luau` **r12** (backup `Kit_Servidor_r11b` local e no place); `BasicoModo = mordidas`. Os clipes de garra continuam no place **sem uso** (histórico na §8.66–8.69).
- **Boca do kit:** o mesmo sinal invertido da mandíbula da mordida r1 estava em `gen_kit_v42.py` (a boca FECHAVA para dentro do crânio). `gen_kit_v42b.py` (cópia, só o sinal muda; `anim_v42b/`, a v42 fica intacta): AvalancheOnda abre até 28° (antes ia para dentro), CometaPouso 8° → 4° (ofegante, antes 0°), AvalancheCorrida 11° (rosnado, antes 3°). Prancha `review/v42b_boca/boca_kit_v42_x_v42b.jpg`. Export `studio/json_v42b/` + `studio/montar_kfs_lobo_v42b.luau`; 5 clipes do kit remontados no place.
- **Teste em Play:** contra `Javali_Teste` só mordidas alternando 7/7 (−70); Avalanche contra o javali acertou (−12) com a boca aberta na corrida e na onda (`review/studio_v42b/avalanche`, `folha_avalanche.jpg`). Sem erros de script.

### 8.71 Uivo Boreal gravado com os efeitos de gelo E4 (17/11/2026)
- O Studio do Teste-animacoes caiu por GPU ("Device removed 0x887a0006") ao iniciar o primeiro Play (outros dois Studios em Play no PC). Após o usuário reabrir: place conferido — Kit_Servidor r12, kit v42b, clipes v43r5 e FX_Boreal intactos (Team Create guardou tudo).
- Lição: depois que o Studio reabre a JANELA muda (hwnd novo); a primeira gravação saiu preta por usar a janela antiga — achar o hwnd de novo antes de capturar.
- Play: Uivo Boreal 2× (recarga 22 s), corpo inteiro em 3/4 e close da cabeça (`review/studio_uivo_e4/corpo`, `cabeca`, folhas, `zoom_uivo_e4.jpg`, vídeo **`review/studio_uivo_e4/video_uivo_boreal_e4.mp4`**). Visto: linhas de gelo acendem no corpo e na pata dianteira com a espiral, olhos azul-gelo, cristais r8l na crista, uivo de boca aberta. Sem erros.
- **Uivo Boreal com os efeitos E4 APROVADO pelo usuário (17/11).**

### 8.72 Kit consolidado + idades + mordida com som/impacto + vídeo dos poderes (18–19/11/2026)
**Pedido:** "Prossiga com todos os passos de uma vez e depois eu avalio. Mande um vídeo dos poderes ao finalizar tudo." (e: "sem lagar o Opera e o Roblox").

**Consolidação (§2, nota no topo):**
- elemento Gelo e Ar (decisão do usuário de 16/11);
- kit: Cometa Glacial, Uivo Boreal, Avalanche + Instinto Boreal e Pelagem Polar;
- números do documento [PROPOSTA][A TESTAR].

**Idades — `studio/Idade_Servidor.server.luau` r1 (novo):**
- O atributo `Idade` do lobo (Filhote/Jovem/PreAdulto/Adulto/Anciao) aplica os multiplicadores de `ESTATISTICAS_POR_IDADE.md`.
- O modelo Adulto é usado em escala (`Model:ScaleTo`); modelos próprios por idade e o ovo: [PENDENTE].
- **Grava:** Escala, VidaMax/Vida (proporcional), MultDano, MultDefesa, MultForca, BonusVel_Idade, TetoEsquiva, EnergiaMax, RegenEnergia e Ativas.
- **Liberação [A CONFIRMAR]:** Filhote nenhuma ativa; Jovem Uivo; Pré-adulto + Avalanche; Adulto/Ancião + Cometa. A ordem é proposta minha.

**Ajustes nos scripts (cópias das versões anteriores com sufixo `_r12`/`_r3`/`_r5`/`_r3`, e no Studio em `ServerStorage.LoboArtico_Backups.Antes_r13_idades_19_11`):**
- `Controle_Servidor` r4: deslocamento dos clipes de transição e apoio à frente ×Escala; o clipe toca a MultVelocidade/Escala (patas casadas).
- `Kit_Servidor` r13:
  - dano ×MultDano, teto de esquiva por idade, focinho/alcance da mordida ×Escala;
  - recusa "bloqueada na idade";
  - evento `basico_acerto`.
- `Kit_Servidor` r13b — **bug antigo corrigido:** o raio de obstáculo do Cometa (e da Avalanche) batia no próprio alvo. O Cometa pousava ~7 studs antes e a explosão (raio 8) não o alcançava. Agora inimigo não conta como obstáculo.
- `Uivo_Servidor` r6: EnergiaMax/RegenEnergia/TetoEsquiva por idade e bloqueio do Uivo.
- `Kit_Cliente` r4:
  - estalo da mordida (sons "Creature Bite" já usados nos dragões, 9125467298/9125466463, mais agudos);
  - no acerto, pancada surda (9113445183) + nuvem curta de neve e lascas de gelo no ponto da mordida.

**Clipes de garra:** os 8 `LoboArtico_Garra*` saíram de `ReplicatedStorage.Animacoes_LoboArtico` para `ServerStorage.LoboArtico_Backups.Garras_retiradas_19_11` (sem apagar).

**Testes em Play (Teste-animacoes, alvo de ensaio criado só no Play):**

| Caso | Resultado |
|---|---|
| 5 idades | escala 0,40/0,65/0,85/1,00/1,10; vida 120/200/300/400/460; vel 1,15/1,10/1,05/1,00/0,90 |
| Filhote andando/trotando/correndo | 3,5 / 7,7 / 23,4 studs/s, sem bloqueio |
| Mordida andando | 8 a 11 acertos em 8 s, 10 de dano cada; eventos `basico_acerto` recebidos no cliente |
| Cometa a 50 studs (r13b) | pousou a 7,4 do alvo, dano 8, alvo atingido (antes da correção: 0) |
| Avalanche | dano 12 |
| Uivo | vel 1,20, esquiva 0,30 durante o efeito |
| Pelagem | Camuflado = true, AlcanceNotarMult 0,6 parado |
| Instinto | marca no alvo (MarcaBoreal_Fim) |
| Filhote | Cometa, Avalanche e Uivo recusados |
| Jovem | Uivo aceito, Avalanche recusada |
| Energia | máxima 60 (Filhote) e 75 (Jovem) |

- **Vídeo:** `review/studio_poderes/video_poderes_lobo_artico.mp4` (~87 s; capturas de 6–10 q/s para não pesar o PC).
- **Sem som na captura:** o PrintWindow não grava áudio. O som da mordida está só no código, sem ser ouvido por mim.

**Pendências/riscos:**
- Filhote a 115% do adulto, com 40% do tamanho: o clipe toca ~2,9× mais rápido (visual apressado). Decidir se a velocidade da idade deve ser relativa ao tamanho.
- Os efeitos de gelo (espinhos, casca, lascas) têm tamanho fixo e podem ficar grandes no filhote.
- A nuvem de neve do acerto é branca sobre neve (pouco visível).
- Place não salvo por mim (Team Create grava as mudanças do Edit).
- **Vídeo e mudanças APROVADOS pelo usuário (19/11: "Aprovar e commitar").** Os números continuam [PROPOSTA][A TESTAR] do documento.

### 8.73 Velocidade relativa ao tamanho + efeitos na escala da idade (19/11/2026, aprovado)
**Pedido:** "Ok prossiga, já tem todos os tamanhos" (próximo passo do §8.72: filhote apressado e efeitos de tamanho fixo).

**Alterações (cópias das versões anteriores com sufixo; no Studio em `ServerStorage.LoboArtico_Backups.Antes_r13c_escala_19_11`):**
- `Controle_Servidor` r5: a velocidade da idade passa a ser **relativa ao tamanho**.
  - O clipe toca a MultVelocidade (Filhote 1,15 = passada 15% mais rápida).
  - O deslocamento é o do clipe ×Escala×mult.
  - Filhote: corrida 9,3 studs/s (= 20,4 × 1,15 × 0,40), patas casadas. Antes: 23,4 studs/s com o clipe a 2,9×.
  - Sobre a regra do documento, isso é uma interpretação: os 115% valem em relação ao corpo, não em studs/s absolutos.
- `Kit_Servidor` r13c: a passada da Avalanche acompanha a escala (o alcance do poder não muda).
- `Kit_Cliente` r5 e `Uivo_Cliente` r7 — os números fixos do Adulto passam a ×Escala:
  - espinhos (OffsetOsso/BaseLocal/TamanhoCheio);
  - olhos (tamanho e posição);
  - rastro do Cometa (tamanho/velocidade das partículas);
  - estilhaços do pouso (distâncias da coroa, lascas, pó);
  - nuvem da mordida;
  - ponto do som do uivo.
  - As malhas do FX_Boreal (casca, moldes) já encolhem com `Model:ScaleTo`.
  - Bug achado no 1º Play e corrigido: `BaseLocal` é Vector3, não CFrame.

**Testes em Play (Teste-animacoes):**
- Filhote andando/trotando/correndo: corrida 9,34 studs/s, sem bloqueio.
- Uivo no Jovem (0,65): espinhos na crista com 1,19 de tamanho, olhos e linhas no corpo. Console sem erros depois da correção.
- Avalanche no Pré-adulto (0,85): dano 9,6 (12 × 0,80). Passada e estouro na escala.
- **Vídeo:** `review/studio_escala/video_escala_idades.mp4` (~48 s, sem som).

**Não testado:** Cometa no Ancião (1,10); efeitos do Cometa em escala diferente de 1. O Cometa só libera a partir do Adulto.

### 8.74 Proposta visual por idade — protótipo no Blender (19/11/2026, aprovado: "Aprovar e seguir")
**Pedido:** "Também quero diferenças no visual, do bebê-jovem-préadulto-adulto-ancião".

**Protótipo:** `idades_v1.py` sobre `anim_v42b` (não salva o .blend) + `prancha_idades_v1.py` → `review/idades_v1d/prancha_idades.jpg`.
- Só pose dos ossos (escala por osso, com `inherit_scale = NONE` para não acumular), tinta multiplicada na cor da pelagem e cristais escalados em torno da própria base.
- **Base real:** filhotes de lobo-ártico nascem escuros (cinza-acastanhado) e clareiam; cabeça grande, focinho curto, orelhas e patas grandes, cauda curta; o jovem é pernalta; o ancião engrossa pescoço/juba e baixa a cabeça.
- **Fantasia [PROPOSTA]:** os cristais do dorso nascem no Jovem e crescem com a idade.

| Idade | Escala | Proporções (cabeça / pernas / patas / cauda / corpo) | Pelagem (multiplica) | Cristais |
|---|---|---|---|---|
| Filhote | 0,40 | 1,30 (focinho 0,90) / 0,80 / 1,32 / 0,60 / 0,85; pescoço 0,75 | 0,30 0,27 0,25 (cinza-acastanhado) | não |
| Jovem | 0,65 | 1,14 / 1,08 / 1,14 / 0,84 / 0,93 | 0,58 (cinza claro) | 0,45 |
| Pré-adulto | 0,85 | 1,05 / 1,03 / 1,04 / 0,95 / 0,98 | 0,84 | 0,75 |
| Adulto | 1,00 | base | base | 1,00 |
| Ancião | 1,10 | pescoço/juba ×1,16, cabeça 10° mais baixa | 1,00 0,91 0,76 (marfim) | 1,35 |

**Limites do protótipo:**
- A marca do ombro está pintada na textura: no Filhote ela continua visível, mesmo com a malha de brilho escondida.
- A escala da cabeça também aumenta a juba.

**Caminho para o Roblox (depois da aprovação):**
- Para cada idade, aplicar a pose como repouso numa cópia, mantendo os mesmos 37 ossos e nomes.
- Exportar um GLB por idade, com a textura tingida assada (ou cor no SurfaceAppearance).
- Os clipes atuais tocam nas 5 malhas: são rotações relativas ao repouso, mas é preciso conferir as alturas das patas por idade.
- O `Idade_Servidor` troca a malha em vez de só usar `ScaleTo`.

### 8.75 Malhas por idade — export, QA dos clipes e montagem no Studio (19/11/2026)
**Pedido:** "Aprovar e seguir" (proposta §8.74). Depois: "Sem lagar a tarefa do Opera/Roblox, talvez as renderizações estejam travando".

**Blender:**
- `tingir_idades_v1.py`: cor da pelagem por idade, mais clara que o protótipo porque no GLB pesava mais.
  - Filhote 0,46/0,42/0,39; Jovem 0,70; Pré-adulto 0,88; Ancião 1,00/0,95/0,86.
- `exportar_idades_v1.py` → `idades_v1/export/CR_LoboArtico_<Idade>.glb` (+ .blend e JSON):
  - proporções aplicadas como repouso, com os mesmos 37 ossos e as mesmas orientações;
  - patas no chão, cristais na escala da idade;
  - Filhote sem `LOW_Marca`;
  - GLB sem animações (não cria RBX_ANIMSAVES).
- `qa_idades_v1.py`: 19 clipes do jogo em cada idade.
  - **r1:** perna curta = pata afundando ao andar (−0,32).
  - **r2:** a perna inteira proporcional. Deitar e sentar ainda afundavam o filhote (−0,78) e faziam o jovem flutuar (+0,25).
  - **r3 (final):** pernas com o comprimento do Adulto em todas as idades. A idade aparece na cabeça, corpo (curto/gordinho no Filhote, magro no Jovem), patas largas, cauda, pescoço, pelagem e cristais.
  - Ancião: pescoço 1,10 e cabeça no repouso normal. Girar o repouso mudaria a convenção dos clipes.
  - **Resultado:** o pior quadro de cada idade fica dentro do próprio Adulto (−0,233 no Deitar). O Filhote sentado afunda −0,185, o que dá 0,07 stud na escala 0,40.
  - Prancha: `review/idades_qa/prancha_malhas_idades.jpg`.

**Para não pesar o PC:**
- `blender_leve.ps1`: Blender em prioridade Idle, `-t 2`, janela oculta.
- Renders de revisão em Cycles CPU (sem GPU, que o Studio e o Opera usam). O `nice` do Git Bash não baixava a prioridade no Windows.

**Studio:**
- O usuário importou os 5 GLB; todos entraram como `Scene`. Identificados pelas medidas:
  - Filhote: sem Marca;
  - Jovem, Pré-adulto e Ancião: altura dos cristais 0,81 / 1,13 / 1,90;
  - Adulto: igual ao atual.
- `studio/montar_idades_v1.luau`:
  - `ServerStorage.LoboArtico_Idades.{Adulto, Filhote, Jovem, PreAdulto, Anciao}` com as MeshParts LOW_*, posição relativa à RootPart e a tabela de repouso dos ossos;
  - SurfaceAppearance sem metal e com a máscara de emissão do Uivo (103482067734616) copiada;
  - os imports originais foram guardados em `ServerStorage.Import_CR_LoboArtico_*`; nada apagado.
- `Idade_Servidor` r2: troca a malha e o repouso dos ossos na escala do Adulto, depois aplica `ScaleTo`.
- `Kit_Cliente` r6 e `Uivo_Cliente` r8: pegam a SurfaceAppearance da LOW_Corpo nova.
- Cópias: `_r1`, `_r5`, `_r7` e `ServerStorage.LoboArtico_Backups.Antes_idades_malha_19_11`.

**Pendente:** testar a troca em Play. Não foi feito porque o Studio do Lobo Ancestral estava em Play (dois Plays juntos já derrubaram a placa de vídeo).

**Play (usuário: "Pode fazer já", com dois outros Studios em Play; teste curto, captura a 10 q/s):**
- 1º Play: os imports recém-enviados ainda estavam sendo processados pelo Roblox ("Asset content representation is being generated").
- **Bug achado no 1º Play:** as MeshParts trocadas sumiam.
  - Cada peça pende da RootPart por um Motor6D, e o do clone apontava para a RootPart do import guardado: a peça caía no vazio.
  - **`Idade_Servidor` r2b** religa o Motor6D na RootPart do lobo (C0 = posição relativa guardada).
- 2º Play: as 5 trocas OK (Filhote 4 peças, demais 5), malhas visíveis e animando. Filhote andou, trotou e correu; console sem erros.
- **Vídeo:** `review/studio_idades_malha/video_idades_malha.mp4` (~40 s).
- **Observado:** no Roblox, Filhote e Jovem saem mais escuros que no Blender (sem a curva AgX). Ajustar a tinta se o usuário quiser.
- **APROVADO pelo usuário (19/11: "Aprovar e commitar")**, junto com §8.73 (velocidade relativa ao tamanho e efeitos na escala).

### 8.76 Pelagem do Filhote/Jovem no Roblox, cabeça do Ancião e números finais do kit (19/11/2026)
**Pedido:** "Siga com os dois" (clarear Filhote/Jovem no Roblox + pendências do kit).

**Pelagem (sem reimportar):**
- `tingir_idades_r2.py` → `idades_v1/roblox_r2/`.
- As texturas foram enviadas ao Roblox e trocadas só nas malhas guardadas em `ServerStorage.LoboArtico_Idades`:
  - `SurfaceAppearance.ColorMap` de Corpo e Cabeça;
  - `TextureID` da Pelagem.
- As ids antigas ficaram nos atributos `ColorMap_r1` e `TextureID_r1`.

| Tentativa | Filhote | Jovem | Resultado |
|---|---|---|---|
| r1 | 0,46 | 0,70 | escuro demais no Roblox |
| r2a | 0,64 | 0,85 | não avaliável |
| r2b | 0,55 0,50 0,46 | 0,78 | em uso |

- Na r2a, a imagem branca não era a cor: era a textura ainda não processada pelo Roblox ("Asset content representation is being generated").

**Cabeça mais baixa do Ancião — `Idade_Servidor` r3:**
- O repouso do `Pescoco1` gira 8° para baixo só nessa idade. Os clipes (Bone.Transform) continuam por cima.
- Sinal medido em Play: a cabeça fica 6,29 acima do pivô, contra 6,72 sem o giro (−0,43 stud). Com o sinal +1 subia para 6,94.

**Números finais do kit — APROVADOS pelo usuário em 19/11 ("Aprovar e commitar"; continuam [A TESTAR] em jogo).** Os do documento (§3 de `REFERENCIAS_PODERES_E_EFEITOS.md`) continuam valendo. Abaixo, só os que nasceram no ensaio e ainda não estão no documento:

| Poder | Campo | Valor no ensaio | Por que / origem |
|---|---|---|---|
| Cometa | alcance | 60 | pedido do usuário 17/11 ("longo alcance, segue o alvo"); o documento diz 35 |
| Cometa | giro (curva no voo) | 240°/s | para seguir alvo em movimento (documento: 120) |
| Cometa | velocidade de voo | 40 studs/s | 60 studs em ~1,5 s |
| Cometa | altura do arco | até 10 (32% da distância) | pedido 17/11 "pular mais alto" |
| Cometa | alcance mínimo | 8 | evita arco degenerado colado no alvo |
| Mira | distância de travar alvo | 65 | um pouco além do alcance do Cometa |
| Avalanche | velocidade | 24 studs/s | um pouco acima da Corrida (20,4): 30 studs em 1,25 s |
| Avalanche | onda | cone de 10 studs, meio-ângulo 35° | — |
| Avalanche | lentidão | 30% por **2 s** | o documento não dá a duração |
| Avalanche | trilha | raio 2,5, 3 s | — |
| Básico | mordidas | intervalo 0,5 s, alcance 3,5 (+focinho), cone 75°, recomeça a sequência após 1,2 s | — |
| PvP | jogadores como alvo | desligado | [A CONFIRMAR] em todos os poderes |

**Play final (r2b + r3):**
- Filhote em cinza médio, mais claro que a r1; gradiente cinza → branco até o Adulto.
- O Jovem saiu quase branco. A textura dele ainda constava como "sendo gerada" pelo Roblox nesse Play, então a cor final do Jovem não foi confirmada.
- Ancião com a cabeça mais baixa.
- Evidência: `review/studio_idades_r2/fila_r2b.jpg`. Sem vídeo, para não pesar o PC.
- **Pelagem r2b, cabeça do Ancião e números do kit APROVADOS pelo usuário (19/11).** A cor do Jovem ainda deve ser conferida no próximo Play.

### 8.77 Levar o Lobo Ártico ao rpg_roblox — montagem isolada (19/11/2026)
**Pedido:** "Abri o rpg, me diga o que devo importar lá" → "Importados".

**M0 (somente leitura):**
- Só existia o modelo antigo `ServerStorage.Biblioteca_Criaturas.Modelos.Lobo_Artico` (9 partes), que ficou intocado.
- Existe o habitat `Tundra_Congelada.Habitats.Ecologia_Fauna.Lobo_Artico` (3 itens).
- Não havia biblioteca de animações nem scripts do lobo novo.
- O Workspace tem 372 mil descendentes.

**Imports do usuário:** 5 GLB de idade + `CR_LoboArtico_GeloFX_E4.glb`. Identificados pelas medidas (Filhote sem Marca; altura dos cristais 0,81 / 1,13 / 1,37 / 1,90) e sem RBX_ANIMSAVES.

**Montado (Edit; código enviado inline):**
- `Workspace.Teste_LoboArtico` (área isolada a y=1500, vazia antes; atributo `Origem`), com 5 chãos de neve e um marco.
- `LoboArtico_LOW` = import do Adulto no pivô (−600, 1500, −600):
  - RootPart ancorada e invisível; MeshParts sem colisão e sem toque, Massless;
  - SurfaceAppearance sem metal, com as máscaras de emissão iguais às do Teste-animacoes:
    - Corpo: 103482067734616, tinta (60, 160, 255), força 0;
    - Cabeça: 91057023039203, força 1;
    - Marca: 123224124316631, força 1,4.
- `FX_Boreal` (lógica do `montar_gelo_e4`): 8 espinhos nos ossos, Casca_Gelo e 6 moldes; o import foi guardado em ServerStorage.
- `ServerStorage.LoboArtico_Idades` (lógica do `montar_idades_v1`): Adulto + 4 idades, SurfaceAppearance copiadas do Adulto e pelagem r2b no Filhote e no Jovem. Imports guardados como `ServerStorage.Import_CR_LoboArtico_*`.

**Bloqueio:** o Assistant do Studio do rpg_roblox recusa `http://127.0.0.1:8766` ("not in the Assistant HTTP allowlist"). As animações (3,9 MB de JSON) e os scripts vêm desse servidor local. No Teste-animacoes o domínio já estava liberado. Liberar é configuração de segurança do Studio, ou seja, passo do usuário.

**Depois de liberado (usuário: "Liberado"):**
- **Animações:** 44 KeyframeSequences em `ReplicatedStorage.Animacoes_LoboArtico`, montadas pelos mesmos construtores (`montar_kfs_lobo_v41`, `v42b`, `v43r5`) medindo a convenção no lobo do próprio place.
  - 34 de locomoção e vida, 5 do kit, 4 mordidas e o Piscar; as garras ficaram fora.
  - Junto, o ModuleScript `Movimento_LoboArtico`.
  - O place passou de 536 mil para 645 mil instâncias.
- **Scripts:** os 7 scripts conferidos iguais aos do Teste-animacoes (Kit r13c, Kit_Cliente r6, Uivo r6/r8, Controle r5, Idade r3) foram instalados na pasta, com os clientes em RunContext Client.

**Play no rpg_roblox (curto, captura a 10 q/s):**
- Os 4 servidores rodaram.
- Troca Filhote ↔ Adulto com malha própria.
- 6 mordidas = 6 acertos (alvo 1000 → 940).
- Uivo: velocidade 1,20, esquiva 0,30, linhas e espinhos acesos.
- Evidência: `review/rpg_lobo/folha_play_rpg.jpg`.

**Avisos e pendências:**
- No início do Play os clientes avisam "Infinite yield possible" no `WaitForChild("LoboArtico_LOW")`, porque o place usa streaming e a área está longe do spawn. A espera termina quando o jogador chega perto, e tudo funcionou.
- Os imports novos ainda estavam sendo processados ("being generated"); no Play o Filhote saiu claro.
- Os scripts da pasta rodam em todo Play do rpg_roblox. São leves e só agem quando um jogador assume o lobo.
- Não salvei nem publiquei o place (Team Create).
- Não foi feito:
  - substituir o modelo antigo da Biblioteca;
  - pôr o lobo no habitat da Tundra, IA selvagem ou spawn;
  - publicar as animações como Animation (a KeyframeSequence só toca no Studio).

### 8.78 Alcateias selvagens na Tundra: IA, ovo na toca e spawn no habitat (19/11/2026)
**Pedido:** "Faça o push e prossiga com a ida, ninhos, spawn no habitat, IA selvagem" + "o lobo já tem cavernas para esconder seus ovos e dormir lá".
- **Ovo e sono:** o ovo fica escondido na toca (Abrigo_Filhotes) e a alcateia dorme no Descanso_Toca.
- **Tamanho da alcateia:** o usuário não respondeu. Usei 3 por alcateia [PROPOSTA], fácil de mudar em `CFG.membros`.

**Base do levantamento (só leitura):**
- Regras OFICIAIS de ovo (urso-silvestre.md:64-67):
  - o ovo reaparece em 30–60 min;
  - acha-se por pistas, nunca por coordenada;
  - o primeiro a terminar a coleta leva;
  - guardião adulto selvagem não é capturável.
- O tamanho da alcateia e a lore de mamífero nascer de ovo continuam [PENDENTE].
- O habitat do M5.1 já tinha, por alcateia: toca (entrada, descanso, abrigo dos filhotes), 2 zonas de caça, rota de patrulha, arena e território.

**Implementação (fontes em `BLENDER/Criaturas/Lobo_Artico_Ref/studio/`):**
- `Controle_Servidor` r6b (cópia r5):
  - `IA_Mover` (a IA manda a mesma intenção do jogador: direção + marcha) e `IA_PedirUivo`;
  - lobo `Selvagem` não pode ser assumido;
  - sem chão à frente, gira no lugar em direção à intenção (antes travava de frente para a parede da toca).
- `Kit_Servidor` r14 (cópia r13c):
  - `IA_Acao` (básico/Cometa/Avalanche com as mesmas regras);
  - o lobo **selvagem** trata jogador vivo como alvo; o lobo de ensaio continua sem PvP;
  - lobos da mesma `Alcateia` não se atacam.
- `Uivo_Servidor` r7 (cópia r6): `IA_Uivo`.
- `selvagem/IA_LoboArtico.server.luau` r1e (um por lobo):
  - **rotinas** Dormir (Deitar → Dormindo no Descanso, peso 3× à noite), Patrulhar (1 de cada 4 pontos da rota), Caçar (Farejar nas zonas) e Guardar (perto do ovo; Sacudir/Farejar);
  - **defesa:** jogador a até 40 do ovo, ou que bate no lobo, vira alvo de toda a alcateia (atributo na pasta da alcateia). O Líder uiva como aviso (Uivo Boreal com os bônus) e os outros perseguem mordendo andando. Desistem fora da coleira de 75 do ovo;
  - **nocaute** com vida 0: deita 60 s e se recupera (não morre, não é capturável) [PROPOSTA];
  - **dormente** sem jogador a até 600 (tick de 2 s);
  - **toca:** a toca é estreita demais para o Pathfinding no tamanho do lobo (NoPath com raio 2–3 em todas). Na 1ª vez o lobo calcula a "cadeia da toca" com um agente pequeno (raio 1, altura 3): Entrada → Descanso, mais o trecho até o Abrigo em pontos de 6 studs. Dentro da toca segue a cadeia; fora, o Pathfinding normal;
  - **destrava:** parado 3 s → próximo ponto e recalcula; 3 falhas → troca de rotina.
- `selvagem/IA_LoboArtico_Servidor.server.luau` r2 (ServerScriptService):
  - cria `Workspace.Criaturas_IA.Lobos_Articos.<Alcateia>` com 3 lobos (Líder Adulto, Guardião Pré-adulto, Membro Adulto) clonados de `ServerStorage.LoboArtico_Selvagem_Modelo` (lobo + 5 scripts de servidor + `Uivo_Cliente`), na câmara de Descanso;
  - **ovo** em cada toca: forma provisória, segurar 4 s a 10 studs. Ao começar a pegar, a alcateia ataca o jogador. A coleta é validada no servidor (trava antes de esperar), grava `ColetadoPor`/`ColetadoEm` e dispara `ServerStorage.IA_LoboArtico_Eventos.OvoColetado(jogador, alcateia)`. Nenhum item é entregue. Reaparece em 30–60 min (`ReaparecerTesteSeg` só para teste);
  - desliga com `workspace:SetAttribute("IA_LoboArtico_Ativa", false)`.

**Testes em Play no rpg_roblox (curtos):**

| Caso | Resultado |
|---|---|
| Spawn | 3 lobos + ovo na Floresta; dormentes com o jogador longe |
| Pathfinding r1 | NoPath dentro da toca → lobos presos (r1b/r1c/r1d/r1e corrigiram) |
| Rotina r1e | Líder e Membro saem pela cadeia e patrulham (~3 studs/s); Guardião chega ao abrigo do ovo; Membro dorme no Descanso |
| Defesa (jogador a 30 do ovo) | os 3 em Defender; Líder uivou de longe e voltou correndo; Guardião e Membro morderam (vida 100 → 11 em ~15 s) |
| Ovo | segurar 4 s pelo cliente → `ColetadoPor` gravado, ovo escondido, alcateia marcou o jogador; reapareceu no tempo de teste (20 s) com o prompt ligado |
| 3 alcateias | Maciço (cadeia 171 pontos) e Campos (40) com ovo e lobos se movendo (guardar/patrulhar/caçar) |

**Pendências:**
- **Modelo:** modelo do ovo do lobo; tamanho da alcateia e quantos ninhos por jogador [PENDENTE/PROPOSTA].
- **Números:**
  - dano dos lobos em jogador: o Pré-adulto morde 8 e o Adulto 10. Pode ser letal em grupo; ajustar com o usuário.
- **Integração:**
  - o item do ovo depende do inventário (só evento);
  - publicar as animações como Animation para o jogo publicado.
- **Revisão visual:** não fiz captura das alcateias (só números); falta um vídeo de revisão.

**Vídeo da IA (pedido "Quero o vídeo da IA funcionando"):** `review/rpg_ia/video_ia_alcateias.mp4` (~71 s; Play curto no rpg_roblox, captura a 10 q/s). Cenas:
- Líder saindo da toca e patrulhando;
- Guardião dormindo no Descanso;
- defesa com o jogador a 27 do ovo.

**Achados na gravação:**
- **Lobo dentro do jogador:** o lobo entra no corpo do jogador ao morder, em vez de parar na frente. A IA manda andar até o alvo e o lobo não tem colisão. Corrigir: parar a ~3–4 studs do focinho e girar para o alvo.
- **Regeneração cobrindo as mordidas:** com vida 600, a regeneração padrão do Roblox (1%/s) quase cobre as mordidas de um só lobo.
- **Distância de alerta:** a 41 studs do ovo a alcateia não reage (raio de alerta 40), como configurado.

### 8.79 IA selvagem: diagnóstico, correção local r2c e plano de comportamento (19/11/2026)
**Pedido:** "Lobo Ártico — corrigir a IA e aproximar o comportamento de lobos reais". Revisão e correção LOCAL; sem Studio e sem commit.
- **Documento completo:** `DOCS/criaturas/lobo-artico-ia-plano.md` (diagnóstico, regras, matriz, testes, decisões).
- **Os 10 achados:** confirmados na r1e, com linhas citadas. A sobreposição foi confirmada direto nos quadros `review/rpg_ia/defesa/`.
- **Regras (RPG_01 §8, versão 22/10):** os `_ATUALIZADO.docx` não estão em Downloads.
  - **Conflitos:** ovo nas 3 tocas sempre ("nem todo grupo possui ninho"; quantidade conforme jogadores) e ovo voltando na mesma toca ("distantes da localização anterior").
  - **A confirmar:** Pré-adulto como Guardião.
- **[CÓDIGO LOCAL] `IA_LoboArtico` r2c** (cópia r1e):
  - contato medido do focinho, com histerese; para e se orienta no contato; aproxima/acompanha;
  - reposiciona quando o alvo fica sob o tronco;
  - repulsão entre membros;
  - status `chegou`/`andando`/`falhou` (NoPath só com Spherecast livre; 3 travamentos = falha, não chegada);
  - Blockcast do corpo da idade limitando a cadeia da toca;
  - token de geração nas poses; Uivo sem travar a IA.
- **[CÓDIGO LOCAL] `Controle_Servidor` r7** (cópia r6b): `IA_Olhar` (orienta sem andar).
- **Testes locais:**
  - `selvagem/conferir_blocos_luau.py`: blocos OK em 7 scripts;
  - `selvagem/simular_contato_r2.py` (modelo 2D, não é o Roblox): sem corpo atravessado em 6 de 7 cenários (o glued começa dentro e sai em 0,97 s). Acertos com alvo parado: 3 → 20; com o Pré-adulto: 6 → 19.
- **Não feito:**
  - instalação e Play no rpg_roblox (precisa de autorização);
  - filmagens reais com minutagem verificada;
  - comparação visual (esta entrega não muda visual).

### 8.80 Teste da IA r2 no rpg_roblox (20/11/2026)
- Autorizado ("Autorizo o teste").
- **Instalado:** IA r2j + Controle r7 no modelo selvagem e no lobo de ensaio, com backup `ServerStorage.LoboArtico_Backups.Antes_IA_r2c_20_11`.
- **Contato frontal em Play:** 0 s de sobreposição e 38 acertos em 25 s (r2d).
- **Revisões feitas no teste:** r2d–r2i. Os detalhes, a geometria real da toca e o aceite estão em `DOCS/criaturas/lobo-artico-ia-plano.md` §8.
- **Pendências:**
  - alvo circulando (giro de confronto ausente);
  - toca baixa para o Adulto (teto 5,7–6,1; decisão do usuário);
  - achado 4.
- **Vídeo:** `review/rpg_ia_r2/video_diagnostico_r2.mp4`. Sem commit.

### 8.81 IA r3 local: ameaça antes do ataque (20/11/2026)
- **Pedido:** o lobo chegava perto demais e atacava direto.
- **Feito, só local** (nada no Studio, sem commit):
  - IA r3 com os níveis Calmo, Atenção, Ameaça, Defesa e Desengajar;
  - coordenador por alcateia;
  - visão com memória;
  - autoria do dano;
  - postos entre o intruso e a toca, a 11×Escala do focinho;
  - Kit r15: `ReceberDano` com origem validada e `IA_DanoRecebido`; o selvagem só morde o alvo travado;
  - spawner r3: a coleta grava UserId.
- **Simulação local:** com 13 cenários, aviso de ≥ 2 s antes de atacar por aproximação, e recuar encerra o confronto.
- **Falta:** os clipes Alerta/Ameaça/Giro/Recuar (contrato) e o Play.
- **Detalhes:** `DOCS/criaturas/lobo-artico-ia-plano.md` §9.

### 8.82 Teste da IA r3 no rpg_roblox (20/11/2026)
- Autorizado ("Autorizo o teste").
- **Instalado:** IA r3i, Kit r15 (só no modelo selvagem) e spawner r3, com backup `ServerStorage.LoboArtico_Backups.Antes_IA_r3_20_11`.
- **Revisões feitas no Play:** r3b–r3i.
- **Resultado:**
  - quem vê o aviso, para e recua não é atacado;
  - quem insiste recebe 6,4 s de aviso antes da mordida (contato 1,1–2,9);
  - coleta e dano validado: defesa imediata;
  - dano sem autoria: só investigar;
  - morte, saída e todos longe: volta a Calmo sozinha.
- **Vídeos:** `review/rpg_ia_r3/video_r3_limpo.mp4` e `video_r3_diagnostico.mp4`.
- **Falta:** clipes de ameaça e recuo, teto da toca, decisão sobre a boca da toca como zona crítica. Sem commit.

### 8.83 Lobo solitário + viradas naturais (20/11/2026, local)
- **Decisão do usuário:** lobo sozinho. Interpretação: 1 lobo por território/toca (3 no total).
- **Feito, só local** (sem Studio, sem commit):
  - IA r4: papel Solitário, coordena e adverte sozinho;
  - spawner r4: idempotente; excedentes vão para backup;
  - Controle r8: zona morta, giro preciso no contato, viradas com passos;
  - clipes VirarCurtoEsquerda/Direita (45°, 1,53 s) em cópia `anim_v44b`: deslize 0,017 stud, emenda com o Repouso exata.
- **Vídeos:** `review/v44_viradas_curtas/`.
- **Falta:**
  - cabeça acompanhando no cliente;
  - giro rápido para alvo circulando;
  - teste em Play (spawn, defesa e giro).
- **Detalhes:** plano §10.

### 8.84 Lobo solitário + viradas no rpg_roblox (20/11/2026)
- Autorizado ("Pode montar e testar").
- **Instalado:**
  - IA r4 e Controle r8b, só no modelo selvagem;
  - spawner r4;
  - clipes VirarCurto e `Movimento_LoboArtico` v44;
  - backup em `Antes_r4_20_11`.
- **Play:**
  - 1 lobo Solitário por território, idempotente; a migração de um grupo de 3 guarda 2 no backup;
  - defesa sozinho preservada: aviso, recuo e mordida (80 de dano em 10 s);
  - viradas sempre com passos (0° sem clipe), sem tremor.
- **Vídeos:** `review/rpg_r4/`.
- **Falta:** giro rápido para alvo circulando e cabeça no cliente. Sem commit. Detalhes no plano §10.3.

### 8.85 Ameaça visível e sonora (20/11/2026)
- **Decisões do usuário:**
  - rosnar com os ossos atuais;
  - rosnado + latido;
  - investida de aviso a ~10 studs e ataque se o jogador ficar ~2 s.
- **Clipes** (anim_v45 r2, sem tremor da boca, aprovados): `AmeacaEntrar`, `Ameaca`, `AmeacaSair`, `InvestidaAviso`.
- **No rpg_roblox:** IA r5 + clipes + sons Pro Sound Effects; backup `Antes_r5_20_11`.
- **Play:** rosna, late quando o jogador avança, investida a 9,1 e defesa 3,2 s depois se ele ficar.
- **Vídeo:** `review/rpg_r5/` (sem som). Sem commit. Detalhes no plano §11.

### 8.86 Ameaça mais agressiva (20/11/2026)
- **Decisões do usuário:**
  - postura mais feroz;
  - carga mais forte;
  - ataque mais cedo;
  - som mais raivoso;
  - dano igual.
- **No rpg_roblox:** IA r6d + clipes r3; backup `Antes_r6_20_11`.
- **Play:**
  - carga correndo de até 12 studs e bote a 4–8 do jogador;
  - quem recua não é atacado;
  - quem fica é atacado ~2,4 s depois do bote.
- **Vídeo:** `review/rpg_r6/`. Sem commit.

### 8.87 Giro sem shift lock + patas no chão (20/11/2026)
- **Causa:** poses da IA (Action, corpo inteiro) tocando durante viradas e passos congelavam as pernas; o pivô girava sem chão à frente; o corpo não inclinava com o terreno.
- **Correção instalada:**
  - IA r7 (poses param quando o lobo anda ou vira);
  - Controle r9 (sem giro de pivô; inclinação com o terreno; IK das patas parado), também no lobo de ensaio;
  - backup `Antes_r7_20_11`.
- **Play:** 0 quadros com pose congelando as pernas em 24 s de ameaça girando.
- **Vídeo:** `review/rpg_r9/`. Sistema geral para jogadores e outras criaturas: sessão `pes-no-chao`. Sem commit.

### 8.88 Árvores sólidas na Tundra + lobo contornando troncos (20/11/2026)
- **Causa:** as malhas das árvores da Tundra não tinham colisão nem eram detectáveis.
- **Correção:**
  - 2.572 colisores invisíveis nos troncos (copa atravessável; reversível);
  - Controle r10e: o lobo enxerga e contorna troncos por um ponto de passagem ao lado, com passos normais;
  - backup `Antes_r10_20_11`.
- **Play:** encosto 0, sem piscar, atravessa o bosque; o jogador também para no tronco.
- **Vídeo:** `review/rpg_r10/`. Sem commit.

### 8.89 Andar em curva com passos (20/11/2026, local em cópia)
- **Causa do "giro no eixo":** andando, o Controle r10e gira o pivô sobre o Andar reto. As patas apoiadas escorregam 0,6–1,0 stud por apoio a 30°/s e até 2,0 a 60°/s. Parado, as viradas giram com o pivô quase fixo.
- **Feito (anim_v46c, 16 clipes na fase do Andar):**
  - laços AndarCurva (30°/s) e AndarCurvaFechada (45°/s);
  - transições de 2 ciclos entre reto, curva e fechada;
  - correções CurvaBreve (18°) e CurvaCurta (36°).
  - O Andar aprovado é "dobrado": patas apoiadas fixas no mundo; corpo abaixa, inclina, a coluna e a cabeça entram na curva e a cauda compensa; giro em volta do meio do corpo.
- **Auditoria mundial nos 3 LODs:**
  - deslize 0,007–0,049 (antes: 0,47–1,52);
  - aceleração igual à do Andar;
  - sem cruzamento;
  - reimportação do JSON idêntica.
- **Controlador:** proposta r11 em cópia, não instalada. O pivô segue a curva do clipe e a escolha é feita por ciclo.
- **Vídeos:** `review/v46_curvas/`.
- **Falta:**
  - partida parada com passos;
  - teste em Play (exige autorização);
  - filmagem real de referência.
- Sem commit. Detalhes no plano §14.

### 8.90 Curvas andando no rpg_roblox (23/11/2026)
- **Instalado:**
  - 16 clipes de curva;
  - `Movimento` v46b;
  - Controle **r11c** (selvagem + ensaio);
  - backup em `Antes_r11_20_11`.
- **Play:**
  - curva de 90° em arco, sem giro no lugar;
  - zigue-zague com curvas curtas;
  - desvio de tronco por curva;
  - IA ameaça e defende normalmente;
  - deslize na curva igual ao do Andar reto.
- **Corrigido no teste:**
  - r11b: tronco na linha piscava Parado/Andar;
  - r11c: em Defender, a curva afastava o lobo.
- **Falta:**
  - virada rápida de combate com passos (em Defender a 1ª mordida demorou 8,6 s);
  - partida parada sem virar no lugar.
- **Vídeo:** `review/rpg_r11/`. Sem commit. Plano §14.9.

### 8.91 Virada de combate (24/11/2026, local em cópia)
- **Decisões do usuário:**
  - pivô nas traseiras;
  - 90° em cerca de 1,0 s;
  - só em ameaça e defesa;
  - mordida emenda.
- **Clipes:** VirarCombate90 (1,0 s) e VirarCombate180 (1,6 s), esquerda e direita, em `anim_v47b`.
- **Auditoria:**
  - deslize ≤0,017 nos 3 LODs;
  - emendas lisas;
  - reimportação do JSON idêntica.
- **Controlador:** proposta r11d em cópia (usa essas viradas só em Ameaçar/Defender acima de 45°).
- **Vídeo:** `review/v47_combate/`.
- **Falta:** Studio e Play (autorização). Sem commit. Plano §15.

### 8.92 Virada de combate no rpg_roblox (24/11/2026)
- **Instalado:**
  - 6 viradas de combate (45° 0,63 s; 90° 1,0 s; 180° 1,6 s);
  - `Movimento` v47;
  - Controle **r11e**;
  - backup em `Antes_r11d_24_11`.
- **Defesa no túnel:** 1ª mordida 0,2–0,5 s depois de entrar em Defender (antes 8,6 s), sem viradas calmas e sem giro do pivô parado.
- **Falta:**
  - mira da IA a partir da cabeça (vai e volta com o jogador colado);
  - suavização menor em combate.
- **Vídeo:** `review/rpg_r11/`. Sem commit. Plano §15.1.
