# Matriz de criaturas — Operação C1

Fonte oficial: `RPG_02_Criaturas_Elementos_e_Poderes.docx` (edição 18/10/2026). Totais oficiais: **13 espécies-base, 16 formas regionais, 48 padrões visuais** (3 por forma) e 4 habilidades por espécie. No Studio, os mesmos dados estão em `ServerStorage.Biblioteca_Criaturas.Catalogo`.

As classes de porte e complexidade são classificações **de produção** (não oficiais). A medida oficial é a da coluna "Medida oficial (adulto)". Comprimento e envergadura que o documento não define ficam **provisórios**.

## Estado de produção

Legenda de estado: Não iniciada · Modelagem em andamento · Modelagem concluída · Rig concluído · Animações concluídas · Importação validada · Testes aprovados · Pronta para futura IA.

| Forma | Bioma | Locomoção | Medida oficial (adulto) | Porte (prod.) | Complexidade | Estado | Observações |
|---|---|---|---|---|---|---|---|
| Lobo Ancestral | Floresta Ancestral | Terrestre | 5,5–7 ombro | Médio | Intermediária | **Testes aprovados** | Modelo 6,57 ombro; 13 animações; 3 padrões |
| Lobo Ártico | Tundra Congelada | Terrestre | 5,5–7 ombro | Médio | Intermediária | **Testes aprovados** | Escala ajustada para 6,6 ombro; 13 animações |
| Urso Silvestre | Floresta Ancestral | Terrestre | 8–10 ombro | Grande | Intermediária | **Provisório** (rig + animações prontos) | 3ª geração aceitável mas estilizada (9,14 ombro); aparência pendente de aprovação; 2 gerações reprovadas |
| Dragão das Montanhas | Montanhas Altas | Terrestre + voo | 18–24 ombro | Colossal | Muito avançada | **Animações concluídas (Blender)**; importação manual pendente | 21 ombro; 45 ossos com pele deformável; 15 animações; 3 padrões; GLB validado. 4 gerações no Studio reprovadas |
| Dragão Glacial | Tundra Congelada | Terrestre + voo | 18–24 ombro | Colossal | Muito avançada | **Animações concluídas (Blender)**; importação manual pendente | Mesma base; mais esguio, pescoço longo, chifres retos, cristas cristalinas; 3 padrões |
| Dragão Sombrio | Terras Corrompidas | Terrestre + voo | 18–24 ombro | Colossal | Muito avançada | **Animações concluídas (Blender)**; importação manual pendente | Mesma base; vários chifres, espinhos maiores, asas mais recortadas; 3 padrões |
| Wyvern | Montanhas Altas | Voo + terrestre | 9–13 ombro; envergadura 30–42 | Grande | Muito avançada | **Animações concluídas (Blender)**; importação manual pendente | 11 ombro; 38 envergadura; 38 ossos; 18 animações (incl. Rasante, FerraoAtaque, GuinadaEvasiva); 3 padrões; apoio bípede |
| Basilisco | Pântano Nebuloso | Terrestre (lama/água rasa) | 7–10 ombro | Grande | Intermediária | **Animações concluídas (Blender)**; importação manual pendente | ~8,3 ombro (crista até 10,6); comprimento ~25 (provisório); 23 ossos; 10 animações (4 habilidades); 3 padrões |
| Crocodilo Primordial | Pântano Nebuloso | Semiaquática | 5–7 ombro; 24–32 comprimento | Grande | Intermediária | **Animações concluídas (Blender)**; importação manual pendente | 6,2 ombro; 25,7 comprimento; 23 ossos; 11 animações (incl. Natacao e 4 habilidades); 3 padrões |
| Leão Solar | Planícies Douradas | Terrestre | 10–13 ombro | Grande | Intermediária | Não iniciada | |
| Búfalo Colossal | Planícies Douradas | Terrestre | 14–18 ombro | Gigante | Intermediária | Não iniciada | |
| Escorpião Colossal | Deserto de Cristal | Terrestre (areia) | 16–24 comprimento | Grande | Muito avançada | **Animações concluídas (Blender)**; importação manual pendente | 22,9 comprimento; 8 pernas, pinças e cauda segmentada; 42 ossos; 9 animações (3 habilidades); 3 padrões |
| Lagarto Cristalino | Deserto de Cristal | Terrestre (escalada) | 18–26 comprimento | Grande | Avançada | **Animações concluídas (Blender)**; importação manual pendente | 19,9 comprimento; 23 ossos; 10 animações (4 habilidades); 3 padrões. Crescimento dos cristais com a idade ainda não modelado |
| Serpente Marinha | Costas Selvagens | Aquática | 30–45 comprimento | Gigante | Avançada | **Animações concluídas (Blender)**; importação manual pendente | 39 comprimento; 15 ossos em cadeia; 10 animações (2 de 4 habilidades); 3 padrões |
| Leviatã Jovem | Costas Selvagens | Aquática | 55–80 comprimento | Colossal | Avançada | **Animações concluídas (Blender)**; importação manual pendente | 69,7 comprimento; 4 nadadeiras; 22 ossos; 11 animações (3 de 4 habilidades); 3 padrões |
| Cérbero Sombrio | Terras Corrompidas | Terrestre | 12–16 ombro | Gigante | Avançada | **Provisório no Studio** (rig + 13 animações testadas em Play; aparência aguardando aprovação) | `Laboratorio_Criaturas.Cerbero_Sombrio_PROVISORIO`, 14,0 ombro. Base do Lobo Ancestral aprovado: tronco mais largo, patas mais grossas, 3 pescoços/cabeças em juntas próprias. MordidasTriplices (cabeças em sequência), RugidoInfernal, Observar (laterais olham para fora); 3 padrões. Investida Sombria e Fúria das Três Cabeças ainda sem animação. Rascunho Blender reprovado em `_Provisorios` |

## Pipeline técnico (C1.1)

- **Malha:** gerador de malhas da IA do Roblox (`generate_mesh`) com segmentação anatômica explícita (até 8 partes) e textura. Prompt com **menos de ~500 caracteres** (acima disso a geração falha com "Character limit exceeded").
- **Rig (`Ferramentas.RigQuadrupede`):** alinha frente = −Z e cria `RaizCriatura` (invisível, ancorada) → `Tronco` → `Pescoco` → `Cabeca`; `Tronco` → `Cauda` e 4 patas. As juntas são `Motor6D` com pivôs anatômicos (topo das patas, base do pescoço, nuca, base da cauda), calculados a partir das CFrames **originais** gravadas (`CFrameOriginal`). Cada rig confere o erro de montagem (atributo `ErroRig`, ~0,003 stud).
- **Animações (`Ferramentas.AnimQuadrupede`):** `KeyframeSequence` paramétricas por espécie (atributos na pasta `Animacoes`). Conjunto: Repouso (respiração), Andar (sequência lateral), Trote (pares diagonais), Corrida (galope rotatório, com suspensão), VirarEsquerda/VirarDireita, Observar, Farejar (alimentação), Deitar → Deitado → Levantar, vocalização (Uivo/Rugido) e Mordida (ataque básico).
- **Verificação (`Ferramentas.VerificaPose`):** avalia poses por cálculo da cadeia de juntas (sem o Animator do modo Edit) e mede o contato das patas com o chão. A pose deitada é calibrada pelas pontas das patas (`PipelineQuadrupede.calibrarDeitar`).
- **Escala oficial:** `PipelineQuadrupede` com `alvoOmbro` usa `Model:ScaleTo` para levar a altura até os ombros ao alvo dentro da faixa do catálogo.
- **Padrões (`Ferramentas.Padroes`):** um único modelo-base por forma. Os 3 padrões são tingimentos (`SurfaceAppearance` TintMask sobre a textura), compartilhando rig e animações. **Os tons são interpretação provisória** dos nomes oficiais.
- **Laboratório:** `Workspace.Laboratorio_Criaturas` (x/z 30.000, fora do mapa), com piso e um boneco humano R15 de 5,2 studs para escala. Não é conteúdo do jogo.

## Pipeline Blender (Dragões, Wyvern, aquáticos, répteis e Escorpião)

O gerador do Studio não produziu dragões aceitáveis: saíram sentados, caricatos e com a segmentação das asas falha. Por isso, Dragões e Wyvern foram feitos no **Blender 5.2 local, em linha de comando**:

- geometria por modificador Skin + detalhes (chifres, placas, garras);
- asas com úmero, antebraço, punho com garra, 4 dedos e membrana;
- esqueleto com pele deformável e pesos por proximidade dentro de cada região (corpo/asa), com até 4 influências por vértice;
- animações em ações separadas;
- textura procedural (escamas e couro) assada em atlas de 2048 (cor + normal).

Arquivos em `BLENDER/Criaturas/` (GLB, FBX, PNG por padrão, `.blend`); scripts em `BLENDER/Criaturas/scripts/`; instruções em `BLENDER/Criaturas/LEIA-ME-IMPORTACAO.md`. O GLB foi validado por reimportação: 1 armature, contagem de ossos e animações conferida, 2 texturas. **A importação no Studio é manual** (a integração não lê arquivos locais), e a validação no Roblox fica para depois dela.

## Limitações conhecidas

- **Lobos e Urso (feitos no Studio):** sem pele deformável. Os membros são segmentos rígidos (Motor6D), e as articulações podem mostrar pequenas emendas em ângulos grandes. As formas feitas no Blender têm pele deformável, mas dependem da **importação manual**.
- As animações rodam no Studio por `AnimationClipProvider:RegisterAnimationClip` (IDs temporários). **Para o jogo publicado, cada `KeyframeSequence` precisa ser publicada como Animation** (Animation Editor → Publish), uma ação manual.
- O gerador tende a estilizar ursos e dragões, então cada geração passa por inspeção visual. As reprovadas ficam em `ServerStorage.Proto_Restore.Retirados_C1`, com o atributo `Motivo`.
- Não gerar malhas com o Studio em Play: a geração falha ("Model generation should only be called from the server").
- **Escala das animações (corrigido em 26/10):** o Animator multiplica as translações das poses por `Model:GetScale()`. O `PipelineQuadrupede` aplicava a escala de novo, então modelos escalados deitavam fundo demais (Cérbero ×2,09) ou flutuavam (Lobo Ártico ×0,87: barriga a 0,45). Agora as translações ficam na escala-base. As animações do Lobo Ártico foram regeneradas e a barriga deitada ficou em 0,10. `VerificaPose` ainda mede as translações sem a escala, então para modelos escalados a conferência real é feita em Play.

## Compatibilidade com habitats existentes (inspeção somente leitura, 26/10)

Medidas reais dos modelos em pose de solo:
- **Dragões:** ~20 de largura × ~102–106 de comprimento (com cauda) × ~37–38 de altura; envergadura ~85–90.
- **Wyvern:** ~12 × 56 × 19; envergadura 38.

| Local | Dimensão existente | Cabe? |
|---|---|---|
| Montanhas — 3 cavernas paramétricas de dragão | entrada 52,8 × 42; câmara Ø 124,8 × 57,6 de altura | **Sim.** 5 de folga na altura da entrada; câmara permite girar |
| Tundra — Covil Coração / Agulha | câmara 160 × 140 / Ø 150, altura 62–65; entrada Ø 54–56 | **Sim** |
| Tundra — Covil Vigia | câmara 120 × 110, altura 60 | **Apertado:** ~4 de folga para girar |
| Plataformas de pouso da Tundra | raio 44–46 (Ø 88–92) | **Cauda sobra** ~10–15 |
| Ilha dos Ventos Altos — pouso do Dragão | Ø ~80 | **Cauda sobra** ~20 |
| 5 ninhos de Wyvern (Montanhas) | ~35 × 35 | Corpo cabe; **cauda (56) sobra**, a menos que se enrole |
| Pouso da Wyvern na ilha | raio 20 (Ø 40) | Corpo cabe; cauda sobra |

**Divergência entre valores provisórios:** a pasta `Tundra_Congelada.Habitats.Ecologia_Fauna.Dragao_Glacial` registra "comprimento ~70, envergadura ~100". O modelo tem ~106 de comprimento e ~88 de envergadura. O RPG_02 não define nenhum dos dois.

**Decisão do usuário:** encurtar a cauda dos modelos ou ampliar plataformas e ninhos. Nada foi alterado no mapa.
