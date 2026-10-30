# Criaturas feitas no Blender: como importar no Roblox Studio

Estes arquivos foram gerados por script no Blender 5.2, em linha de comando (o Blender MCP não estava disponível). A integração com o Studio **não consegue importar arquivos locais**, então a importação é manual (cerca de 1 minuto por criatura).

## Arquivos

| Criatura | Modelo | Texturas (cor = padrão oficial) | Ossos | Triângulos | Animações |
|---|---|---|---|---|---|
| Dragão das Montanhas | `Dragao_das_Montanhas.glb` / `.fbx` | `_Cor_Basalto_Cinzento`, `_Cor_Cobre_das_Alturas`, `_Cor_Verde_da_Montanha`, `_Normal` | 45 | 16.478 | 15 |
| Dragão Glacial | `Dragao_Glacial.glb` / `.fbx` | `_Cor_Branco_Glacial`, `_Cor_Azul_da_Geada`, `_Cor_Cinza_da_Nevasca`, `_Normal` | 45 | 16.582 | 15 |
| Dragão Sombrio | `Dragao_Sombrio.glb` / `.fbx` | `_Cor_Negro_Obsidiana`, `_Cor_Roxo_Crepuscular`, `_Cor_Carmesim_Corrompido`, `_Normal` | 45 | 18.354 | 15 |
| Wyvern | `Wyvern.glb` / `.fbx` | `_Cor_Verde_Musgo`, `_Cor_Marrom_Rochoso`, `_Cor_Cinza_Acinzentado`, `_Normal` | 38 | 14.144 | 18 |
| Serpente Marinha | `Serpente_Marinha.glb` / `.fbx` | `_Cor_Azul_Oceanico`, `_Cor_Verde_Profundo`, `_Cor_Prateado_Marinho`, `_Normal` | 15 | 7.680 | 10 |
| Leviatã Jovem | `Leviata_Jovem.glb` / `.fbx` | `_Cor_Azul_Abissal`, `_Cor_Negro_Oceanico`, `_Cor_Prateado_Profundo`, `_Normal` | 22 | 7.216 | 11 |
| Crocodilo Primordial | `Crocodilo_Primordial.glb` / `.fbx` | `_Cor_Verde_Pantanal`, `_Cor_Marrom_Aluvial`, `_Cor_Negro_de_Rio`, `_Normal` | 23 | 8.520 | 11 |
| Basilisco | `Basilisco.glb` / `.fbx` | `_Cor_Verde_Pantanoso`, `_Cor_Marrom_Lamacento`, `_Cor_Negro_Musgo`, `_Normal` | 23 | 7.760 | 10 |
| Lagarto Cristalino | `Lagarto_Cristalino.glb` / `.fbx` | `_Cor_Quartzo_Claro`, `_Cor_Ambar_Dourado`, `_Cor_Ametista_Rochosa`, `_Normal` | 23 | 7.776 | 10 |
| Escorpião Colossal | `Escorpiao_Colossal.glb` / `.fbx` | `_Cor_Negro_Obsidiana`, `_Cor_Bronze_Desertico`, `_Cor_Areia_Rochosa`, `_Normal` | 42 | 6.552 | 9 |

Os `.blend` guardam a cena-fonte (rig e ações), para ajustes. Os scripts geradores estão em `BLENDER/Criaturas/scripts/`. Todos os GLB foram **validados por reimportação** no Blender (1 esqueleto, no máximo 4 influências por vértice, contagem de ossos e ações conferida, textura de cor + normal embutidas). Em 26/10, Dragão Glacial e Dragão Sombrio foram reexportados porque a malha interna ainda se chamava "Dragao_das_Montanhas".

**`_Provisorios/Cerbero_Sombrio.*`: rascunho reprovado, NÃO importar.** O Cérbero provisório atual está no Studio (`Laboratorio_Criaturas`), montado a partir do Lobo Ancestral. As três cabeças, o rig (31 ossos) e as 11 animações funcionam, mas a aparência foi reprovada na inspeção: cabeças com focinho de foca, membros tubulares e uma dobra no peito.

- **Escala:** 1 unidade = 1 stud. Dragões com 21 de altura até os ombros (oficial 18–24); Wyvern com 11 (oficial 9–13) e 38 de envergadura (oficial 30–42).
- **Escala das demais formas:**
  - Serpente: 39 de comprimento (oficial 30–45).
  - Leviatã: 69,7 de comprimento (oficial 55–80).
  - Crocodilo: 6,2 até os ombros e 25,7 de comprimento (oficial 5–7 e 24–32).
  - Basilisco: ~8,3 até os ombros (oficial 7–10), crista até 10,6.
  - Lagarto: 19,9 de comprimento (oficial 18–26).
  - Escorpião: 22,9 de comprimento (oficial 16–24).
- **Provisórios** (os documentos não definem):
  - comprimento dos Dragões ≈ 100 (com a cauda) e envergadura ≈ 85–90;
  - comprimento da Wyvern ≈ 57;
  - comprimento do Basilisco ≈ 25.
- **Frente:** o focinho aponta para −Z depois da importação (o exportador converte Blender −Y/Z-cima para Roblox).

## Passo a passo (Studio)

1. **Avatar/Home → Import 3D** (ou File → Import 3D) e escolha o `.glb` (de preferência) ou o `.fbx`.
2. Na janela do importador:
   - em **Rig General**, deixe o rig como **R15/Custom** (não converter para R15);
   - em **File Dimensions / Scale Unit**, escolha **Stud** (1 unidade = 1 stud);
   - marque **Import animations**, se a opção aparecer.
3. Importe para o Workspace e mova o modelo para `ServerStorage.Biblioteca_Criaturas.Modelos`.
4. Os padrões 2 e 3 são só troca de textura de cor: no `SurfaceAppearance` da malha, troque `ColorMap` pela imagem do padrão (envie as PNGs como Decal/Image pela Asset Manager).
5. Me avise: na próxima sessão eu confiro a escala, a orientação, as animações (`AnimationController`/`Animator`), as colisões (`CollisionFidelity = Box` na malha e uma caixa de colisão simplificada) e o desempenho, como fiz com os lobos.

## Animações incluídas

- **Dragões:** Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar, Rugido (com mandíbula), AbrirAsas, RecolherAsas, Decolagem, Voo, Planeio, CurvaAereaEsquerda, CurvaAereaDireita, Pouso.
- **Wyvern:** Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar (ferrão erguido), Vocalizar (mandíbula), AbrirAsas, RecolherAsas, Decolagem, Voo (batida mais rápida), Planeio, CurvaAereaEsquerda, CurvaAereaDireita, Pouso, Rasante, FerraoAtaque, GuinadaEvasiva. As três últimas são habilidades oficiais, só como animação, sem efeitos.
- **Serpente Marinha:** Repouso, Natacao, NatacaoRapida, Subir, Descer, VirarEsquerda, VirarDireita, DeslizeTerrestre; habilidades EspiralAquatica e MordidaProfunda.
- **Leviatã Jovem:** Repouso, Natacao, NatacaoRapida, Subir, Descer, VirarEsquerda, VirarDireita, DeslizeTerrestre; habilidades MergulhoAbissal, RugidoOceanico e RupturaDasMares.
- **Crocodilo Primordial:** Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar, Natacao; habilidades MordidaDeAgarrao, GiroPredatorio, Submersao e CaudaDeMare.
- **Basilisco:** Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar; habilidades OlharAmeacador, MordidaToxica, EspiralDefensiva e Emboscada.
- **Lagarto Cristalino:** Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar; habilidades EscamasCristalinas, GolpeDeCauda, DisparoPrismatico e Escalada.
- **Escorpião Colossal:** Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar; habilidades FerraoPerfurante, PincasEsmagadoras e EscavacaoDeAreia. "Nuvem de Areia" é efeito de partículas e fica para a fase de combate.
- Habilidades ainda sem animação (exigem efeitos ou combate):
  - Serpente: Investida Submersa e Correnteza.
  - Leviatã: Onda Titânica.
  - Dragões: Sopro, Arremetida, Tempestade de Asas e Domínio.

Todos os nomes de habilidade vêm de `Biblioteca_Criaturas.Catalogo` (RPG_02). Nenhum foi inventado.

## Limitações honestas

- Os modelos foram feitos por script (modificador Skin + detalhes), não esculpidos à mão. O resultado é "realista-estilizado", sem a riqueza de um modelo esculpido.
- A membrana em repouso pode mostrar pequenas dobras pontiagudas. Em solo, a Wyvern se apoia nas patas traseiras; o apoio nos punhos das asas, que o documento cita como [PROPOSTA], ficou para ajuste futuro.
- Répteis, aquáticos e Escorpião têm menos detalhe que os dragões (de 6,5 mil a 8,5 mil triângulos). O Escorpião tem segmentos rígidos de quitina, com no máximo 3 influências.
- Ainda não foi verificado dentro do Roblox. Depois da importação, publicar as animações (Animation Editor → Publish) é necessário para o jogo publicado.
