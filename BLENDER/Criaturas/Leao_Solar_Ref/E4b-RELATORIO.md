# Leão Solar — E4b, malha preparada para deformar (03/11/2026, em avaliação)

- **Preservados sem alteração nesta tarefa:**
  - `Leao_Solar_Ref_E2_v11.blend`;
  - `Leao_Solar_Ref_E3b.blend`;
  - `Leao_Solar_Ref_E4.blend` (última gravação 19:06, na entrega da E4).
- **Entrega:** `Leao_Solar_Ref_E4b.blend`, com a malha `Leao_Solar_E4b` e o rig de teste `Leao_Solar_Rig_Teste`, de 53 ossos.
- **Texturas:** `e4b/tex/Leao_Solar_E4b_{cor,normal,rugosidade}_{2048,1024}.png`.
- **Intermediários:**
  - `e4b/E4b_corpo.blend`: superfície com laços;
  - `e4b/E4b_boca.blend`: boca com peças separadas, usada para as medições da boca;
  - `Leao_Solar_Ref_E4b_semrig.blend`: UV e bake, sem rig;
  - `e4b/E4_rig_novo.blend`: a E4 com o mesmo rig e os mesmos pesos, usada como base de comparação.
- **Scripts** (`build/e4b/`), em ordem:
  1. `e4b_01_juntas.py`;
  2. `e4b_02_retopo.py`;
  3. boca: `build/e4/e4_03_boca_leve.py`;
  4. UV e bake: `build/e4/e4_04_uv_bake.py`;
  5. `e4b_03_rig_pesos.py`;
  6. `e4b_04_poses.py`;
  7. `e4b_05_videos.py`;
  8. `e4b_06_prancha.py`.
- **Evidências:**
  - `review/E4b_prancha.png`;
  - vídeos em `review/e4b/videos/` (12 MP4);
  - medições `review/e4b/poses_e4/poses.json`, `review/e4b/poses_e4b/poses.json`, `pesos_e4b.json`, `auditoria_e4b.json`, `medidas_boca_e4b.json`, `videos/contatos.json` e `diferencas_neutra.json`.
- Tudo foi feito no Blender, com um **rig de teste**. **Nada foi importado nem testado no Roblox.**

## 1. O que mudou em relação à E4
1. **Juntas medidas no perfil da malha densa** (`e4b/juntas.json`, gráfico `review/e4b/juntas.png`):
   - punho no entalhe do coxim;
   - jarrete na saliência do calcanhar;
   - joelho na frente da coxa;
   - cotovelo sob o peito;
   - ombro e quadril dentro do corpo.
   - No teste da E4, as juntas eram adivinhadas por alturas fixas, com o jarrete fora do lugar: essa era a causa principal da razão de 0,22.
2. **Topologia:**
   - mesma casca por voxel;
   - redução em 3 passadas: uniforme, depois rosto protegido, depois rosto e **zonas de articulação** protegidos (ombros, cotovelos, punhos, quadris, joelhos, jarretes, base da cauda e base do pescoço).
3. **Laços de articulação:** 3 anéis de arestas, perpendiculares à bissetriz dos ossos, em cada cotovelo, punho, joelho e jarrete e na base da cauda (9 articulações, +704 tris).
   - A pele continua triangulada, sem quads desenhados à mão.
   - Os anéis dão linhas de dobra no sentido certo. Ombro, quadril e pescoço ficam dentro da juba e do corpo, e por isso só ganharam densidade, sem anéis.
4. **Boca:** o mesmo gerador leve da E4, sobre a pele nova. As medições ficaram idênticas às da E4 (seção 5).
5. **UV e bake:** refeitos, porque a geometria mudou: 410 cartas e 13.916 vértices com UV. O bake é igual ao da E4: cor, normal e rugosidade vindas da E3b; boca com cor por vértice.

## 2. Orçamento (triângulos)
| Região | E4 | E4b |
|---|---|---|
| Rosto / focinho | 2.088 | 2.050 |
| Juba + corpo | 11.464 | 10.385 |
| Zonas de articulação (com os laços) | — (dentro de corpo e patas) | 1.056 |
| Patas (abaixo de 1,5) | 741 | 711 |
| Cauda + tufo | 907 | 802 |
| **Pele** | **15.200** | **15.004** |
| Interior da boca + dentes + língua | 2.598 | 2.598 |
| **Total** | **17.798** | **17.602** |

- O total ficou dentro da faixa de 15–18 mil; não houve aumento de custo.
- Os laços foram pagos com uma redução proporcional da juba e do corpo.

## 3. Rig de teste e pesos
**Hierarquia** (a lista completa está em `pesos_e4b.json`):
- `Raiz` (no chão, não deforma) → `Quadril` → `Coluna1` → `Coluna2` → `Peito` → `Pescoco1` → `Pescoco2` → `Cabeca` → `Mandibula` → `Lingua1` → `Lingua2`;
- dianteiras (filhas do Peito): `Escapula_*` → `Umero_*` → `Antebraco_*` → `Mao_*` → `Dedos_*`;
- traseiras (filhas do Quadril): `Coxa_*` → `Canela_*` → `Metatarso_*` → `Dedos_*`;
- cauda: `Cauda1`…`Cauda6`, filhas do Quadril;
- secundários do tufo: `Tufo1` e `Tufo2` (filhos da Cauda4), que seguem a Cauda5/6 e recebem o atraso da mola;
- secundários da juba: 8 cadeias de 2 ossos, `Juba_<Topo|TopoD|Dir|BaixoD|Peito|BaixoE|Esq|TopoE>_1/_2`, filhas do Pescoco1.

**Pesos:**
- **Corpo:** pesos automáticos com os ossos do esqueleto.
- **Boca:**
  - a fração da mandíbula vem do gerador da boca e é aplicada sobre a influência da cabeça e do pescoço;
  - dentes superiores = `Cabeca` 1; dentes inferiores = `Mandibula` 1;
  - língua = `Mandibula`, `Lingua1` e `Lingua2` ao longo do comprimento.
- **Juba:**
  - identificada pela cor do albedo (laranja saturado) e pela posição;
  - o peso secundário cresce para fora do pescoço, repartido entre os 2 setores mais próximos e os 2 ossos da cadeia (2.699 vértices);
  - as mechas que caem sobre ombro e antebraço deixam de seguir os ossos da pata (4.971 vértices, com transição);
  - suavização de 12 passos fora do rosto.
- **Tufo:** os pelos fora do miolo da cauda vão para `Tufo1/2` (321 vértices).

**Relatório automático:**

| Item | Valor |
|---|---|
| Vértices | 8.821 |
| Sem peso | **0** |
| Influências por vértice (máx.) | **4** |
| Vértices com 1 / 2 / 3 / 4 influências | 1.102 / 861 / 1.111 / 5.747 |
| Mal normalizados (\|soma − 1\| > 0,001) | **0** |
| Ossos (que deformam) | 53 (52) |

- Na E4 eram 286 vértices sem peso e até 8 influências.

## 4. Deformação — mesmo rig nas duas malhas (`poses_e4` × `poses_e4b`)
- **Como foi medido:** razão de comprimento das arestas (posada / repouso) e **espessura** (distância até os ossos, posada / repouso), na zona de cada articulação.
- **Poses:** flexões extremas, com o sinal escolhido para fechar o ângulo da junta. Os ângulos estão acima do uso normal: cotovelo 95°, punho 85°, joelho 70°, jarrete 75°.

| Pose | E4: aresta mín / máx | E4: espessura p5 | E4b: aresta mín / máx | E4b: espessura p5 |
|---|---|---|---|---|
| Ombro avanço | 0,49 / 1,33 | 0,20 | 0,52 / 3,88 | 0,23 |
| Cotovelo 95° | 0,78 / 1,48 | **0,86** | 0,46 / 3,30 | **0,58** |
| Punho 85° | 0,62 / 1,01 | 0,46 | 0,18 / 1,54 | 0,36 |
| Passo dianteiro | 0,62 / 2,86 | 0,43 | 0,42 / 6,86 | 0,42 |
| Quadril recuo | 0,80 / 1,44 | 0,93 | 0,79 / 1,41 | 0,95 |
| Joelho 70° | 0,78 / 1,19 | 0,80 | 0,53 / 1,47 | **0,87** |
| Jarrete 75° | 0,65 / 1,03 | 0,51 | 0,22 / 1,62 | **0,71** |
| Passo traseiro | 0,31 / 1,30 | 0,57 | 0,32 / 1,65 | **0,61** |
| Pescoço baixo e virado | 0,26 / 4,48 | 0,89 | 0,44 / 5,12 | 0,89 |
| Coluna curva | 0,84 / 2,07 | 0,93 | 0,83 / 1,28 | 0,93 |
| Cauda curva | 0,95 / 1,20 | 0,46 | 0,52 / 4,91 | **0,67** |
| Boca 32° | 0,60 / 12,9 | 0,84 | 0,60 / 13,0 | 0,84 |

**Leitura franca:**
1. **O ganho maior veio das juntas certas e dos pesos.** Com o rig provisório, a E4 tinha jarrete de 0,22 e passo dianteiro de 2,07. Com o rig de teste novo, a própria E4 já melhora muito.
2. **A E4b preserva mais volume** (espessura) no jarrete (0,71 contra 0,51), no joelho, no passo traseiro e na cauda (0,67 contra 0,46).
3. **Onde ficou pior:**
   - no cotovelo (0,58 contra 0,86) e no punho (0,36 contra 0,46), a E4b afina mais na dobra interna;
   - a densidade maior pega a prega interna que a E4, mais esparsa, simplesmente não tinha;
   - no render, o cotovelo da E4b dobra sem quebra visível, mas a prega interna aparece. Não está resolvido.
4. **Arestas com razão mínima baixa** (0,18 no punho, 0,22 no jarrete): são arestas muito curtas da prega interna, que encostam. Em valor absoluto o encurtamento é pequeno, e a espessura mostra que o volume se mantém melhor que na E4. Ainda assim, é compressão real na dobra.
5. **Picos de alongamento** (ombro 3,9, passo dianteiro 6,9, pescoço 5,1, cauda 4,9, boca 13):
   - são arestas muito curtas;
   - no corpo inteiro, o maior alongamento absoluto é de 0,2–1,35 stud;
   - ficam em três lugares:
     - na junção juba/peito/pata, onde o voxel fundiu as mechas à pele;
     - na comissura da boca, igual à E3b;
     - na ponta do tufo.
   - Arestas esticadas acima de 1,5× **e** mais de 0,05 stud: ombro 206, passo dianteiro 125, pescoço 291.
   - **Esse é o principal problema que sobra:** a juba do peito e do ombro estica quando a pata dianteira avança ou o pescoço vira forte.

## 5. Boca, juba e tufo
- **Boca:** medições idênticas às da E4.
  - fechada: 0 pontos do interior aparecendo por fora;
  - 0 vértices de pele dentro da boca, de 0° a 32°;
  - dentes encostando a 0° e a 5° (dentro dos lábios), 0 a partir de 10°.
  - Na abertura em vídeo, comissuras, língua e dentes acompanham. A borda fina do lábio inferior continua como na E3b.
- **Juba:**
  - no vídeo `juba` (cabeça virando, balanço de corrida no pescoço e parada), as cadeias atrasam e voltam por uma mola amortecida (1,6 Hz, amortecimento 0,35, limite de 20°);
  - as mechas grandes se mantêm e não atravessam o rosto nem a boca;
  - **o movimento secundário é discreto**: as cadeias são 8 setores largos, então cada setor move um bloco de mechas, não cada mecha.
- **Tufo:** segue a cauda e atrasa um pouco no vídeo da cauda.

## 6. Contato das patas nos vídeos (`videos/contatos.json`)
- Em todos os clipes, as patas que o clipe não mexe ficam paradas: escorregamento de 0,000 e altura mínima de −0,006 a 0,010 stud (o chão está em 0).
- O tronco não se move nos vídeos. Os passos só levantam e devolvem a pata; não há locomoção.

## 7. Aparência neutra (mesmas câmeras; `diferencas_neutra.json`, média 0–255)
| Vista | E4b × E4 | E4b × E3b | E4 × E3b |
|---|---|---|---|
| Lado / frente / trás | 0,81 / 1,01 / 0,91 | 1,07 / 1,41 / 1,32 | 1,03 / 1,39 / 1,25 |
| Close do rosto (frente / perfil) | 2,42 / 2,25 | 3,64 / 3,04 | 3,68 / 3,12 |
| Juba 3/4 / tufo / tamanho de jogo | 0,90 / 1,10 / 0,20 | 1,32 / 1,40 / 0,36 | 1,25 / 1,24 / 0,34 |

- A E4b fica tão perto da E3b quanto a E4.
- O tufo perdeu um pouco mais de detalhe (802 tris contra 907).

## 8. Auditoria (`auditoria_e4b.json`)
| Item | Valor |
|---|---|
| Bordas abertas | 0 |
| Arestas com mais de 2 faces | 0 |
| Vértices não-manifold | 0 |
| Faces degeneradas | 0 |
| Normais inconsistentes | 0 |
| Cascas | 30 |

- **Autointerseções:** 1.227 pares, todos na boca fechada (raízes dos dentes, caninos cruzados, lábios encostados), como na E4.

## 9. Pendências e riscos
- **Prega interna do cotovelo e do punho:** a E4b afina mais que a E4. Opções: anéis mais espaçados ou só densidade (sem anéis) no cotovelo e no punho.
- **Juba do peito e do ombro:** estica quando a pata avança ou o pescoço vira forte. Opções: limitar o arco do ombro no rig final, mais cadeias de juba no peito ou separar parte das mechas do peito da pele.
- **Juba e tufo:** o secundário é por setores. Para mechas individuais seriam necessários mais ossos (custo de ossos no Roblox, a medir).
- **Rig:**
  - é de teste: sem orelhas, sem dedos separados e sem IK;
  - as restrições do tufo e da juba (seguir e atrasar) foram calculadas no script, não montadas como constraints.
- **Roblox:** nada foi testado (importação, skinning com 4 influências, `SurfaceAppearance`, FPS).
