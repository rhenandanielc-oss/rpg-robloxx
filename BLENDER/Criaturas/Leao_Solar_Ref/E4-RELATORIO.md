# Leão Solar — E4, malha de jogo a partir da E3b (03/11/2026, em avaliação)

- **Fontes, preservadas sem alteração:**
  - `Leao_Solar_Ref_E2_v11.blend` (aparência oficial);
  - `Leao_Solar_Ref_E3b.blend` (boca e antebraços aprovados): é a fonte do bake;
  - `Leao_Solar_Ref_E3_t2.blend`: a mesma malha da E3b antes da boca; é a fonte da superfície fechada.
- **Entrega:** `Leao_Solar_Ref_E4.blend`. Contém o objeto `Leao_Solar_E4` e o rig de teste da boca.
- **Texturas:** `e4/tex/Leao_Solar_E4_{cor,normal,rugosidade}_{2048,1024}.png`.
- **Intermediários:**
  - `e4/E4_corpo.blend`: superfície nova, boca fechada;
  - `e4/E4_boca.blend`: boca leve, com dentes e língua ainda separados; é onde as medições da boca são feitas;
  - `e4/E4_teste_deformacao.blend`: rig provisório.
- **Scripts** (`build/e4/`), em ordem:
  1. `e4_01_retopo.py`;
  2. `e4_03_boca_leve.py`;
  3. `e4_04_uv_bake.py` (usa `e4_uv_regioes.py`);
  4. `e4_05_auditoria.py`;
  5. `e4_06_deformacao.py`;
  6. `e4_07_prancha.py`.
- **Evidências:**
  - prancha `review/E4_prancha.png` e diferenças em `review/E4_prancha_diferencas.json`;
  - auditoria em `review/e4/auditoria_e4.json`;
  - boca em `review/e4/medidas_boca_e4.json`;
  - deformação em `review/e4/deform/deformacao.json`.
- Tudo foi feito e renderizado **no Blender**. **Nada foi importado nem testado no Roblox**: não há FPS, importação ou escala aprovados.

## 1. Como foi feita
1. **Superfície nova:**
   - remesh por voxel de 0,04 stud a partir da casca de boca fechada: 1,16 milhão de faces e uma casca só; 38 ilhas soltas de 8 vértices foram descartadas;
   - isso reconstrói a superfície e elimina as fendas e os 24 grupos não-manifold da E3b, sem decimar esses pontos.
2. **Redução em duas passadas:**
   - uniforme até 60 mil triângulos;
   - depois o rosto e a boca ficam protegidos e o resto é reduzido até 15,2 mil.
   - Distância da E3b até a E4: média 0,030, p95 0,095, máximo 0,74 stud (pontas de mecha).
   - O Quadriflow foi tentado e recusou a malha, como já registrado na skill do pipeline.
3. **Boca:**
   - o mesmo gerador da E3b (`c02_boca.py`), em resolução reduzida: interior 17×9 com paredes 3, dentes de 6 lados × 4 anéis, língua 11×7;
   - foi aplicado sobre a pele nova, no mesmo plano da boca e com a mesma lógica de pesos, folgas e encaixe dos dentes.
4. **Montagem:**
   - dentes e língua foram unidos à malha, mantendo os grupos `Cabeca`, `Mandibula` e `Lingua`;
   - normais recalculadas por casca: corpo e interior formam uma casca fechada, e o lado visível do interior é o de dentro da boca.
5. **UV:**
   - cartas grandes por crescimento de região (normal a menos de 55°, cartas minúsculas unidas), desdobradas por ângulo e com a mesma densidade em todas;
   - a pele do rosto tem o dobro da densidade e a boca, de cor lisa, 0,7×;
   - 455 cartas, 14.360 vértices com UV para 8.919 vértices reais. O Smart UV dava milhares de ilhas e 20,7 mil vértices de UV.
6. **Bake (Cycles):**
   - **corpo:** a partir da E3b, por projeção com afastamento de 0,10: cor sem luz, normal em espaço tangente e rugosidade;
   - **boca:** a cor vem da própria malha de jogo (as mesmas cores por vértice da E3b), com normal plana e rugosidade de 0,55 na mucosa e 0,35 nos dentes;
   - o "brilho" do pelo continua sendo só cor iluminada no albedo; o material é fosco (especular 0,25, metálico 0) e sem emissão.

## 2. Orçamento e contagens por peça
| Peça | Triângulos |
|---|---|
| Pele: rosto/focinho | 2.088 |
| Pele: juba + corpo | 11.464 |
| Pele: patas (abaixo de 1,5 stud) | 741 |
| Pele: cauda + tufo | 907 |
| **Subtotal da pele** | **15.200** |
| Interior da boca + corte dos lábios | 946 |
| Dentes (28: 14 por arcada, 48 tris cada) | 1.344 |
| Língua | 308 |
| **Total (uma malha, um material)** | **17.798** |

- **Mechas:** as da juba e do tufo estão incluídas na pele; não são peças separadas.
- **Vértices:** 8.919 reais e 14.360 com as costuras de UV.
- **Limite do Roblox:** a peça fica abaixo de 20 mil triângulos.
- **Material:** `M_Leao_Solar_E4` (Principled; cor, normal e rugosidade), com o verso das faces oculto, como no Roblox.
- **Texturas:** 3, com mestre em 2048 e versão de jogo em 1024.
- **Memória estimada das texturas de jogo** (1024): sem compressão, 4 MB cada (12 MB); comprimidas na GPU, cerca de 0,5–1 MB cada. Estimativa, não medida no Roblox.
- **Ossos planejados para o rig final** (pedido de rig): cerca de 45–60.
  - raiz/quadril, 3–4 de coluna e peito, 2 de pescoço, cabeça, mandíbula, 2 de língua, 2 de orelha;
  - escápulas e 4 membros com 4 segmentos cada;
  - 6–8 de cauda e 2 de tufo;
  - 8–12 secundários da juba.
- **Influências:** no máximo 4 por vértice (limite do Roblox). O teste automático gerou até 8, então o rig final precisa limitar e normalizar.
- **Orientação e pivô:** frente em −Y, Z para cima, 1 unidade = 1 stud. Patas em Z = 0 e origem do objeto em (0, 0, 0), sem rotação e com escala 1. Caixa: X −5,29…5,35; Y −15,74…18,15; Z 0,01…18,65.

## 3. Auditoria topológica (`Leao_Solar_E4`)
| Item | Valor |
|---|---|
| Bordas abertas | **0** (a boca não é furo: o interior fecha a fenda) |
| Arestas com mais de 2 faces | **0** |
| Vértices não-manifold | **0** |
| Faces degeneradas, arestas de comprimento zero | **0 / 0** |
| Arestas com normais inconsistentes | **0** (eram 60 na junção lábio/interior antes do recálculo) |
| Cascas | 30: corpo + interior (1), língua (1), dentes (28) |

**Autointerseções (pares de triângulos que se cruzam), todas na boca e esperadas em repouso:**

| Tipo | Pares | Causa |
|---|---|---|
| Corpo × peças | 1.014 | Raízes dos dentes enterradas na gengiva e caninos cruzados dentro dos lábios fechados |
| Peça × peça | 129 | Caninos superiores e inferiores encaixados com a boca fechada |
| Corpo × corpo | 93 | Lábio superior encostado no inferior e margem do lábio, com a boca fechada |

- Com a boca aberta não sobra nenhuma: a partir de 10°, dentes × dentes, dentes × tecido, língua × pele e cavidade × pele são todos 0.
- **Boca** (mesmas medições da E3b, `review/e4/medidas_boca_e4.json`):
  - fechada: 0 pontos do interior aparecendo por fora;
  - aberta de 0° a 32°: 0 vértices de pele dentro da boca;
  - mandíbula entrando na cabeça: 26 vértices a 0° (lábios encostados), 2 a 5°, 0 a partir de 10°;
  - faces da margem do lábio tocando a pele: 8, constantes (na E3b eram 11).

## 4. Perda visual (luz neutra, as mesmas câmeras da v11 e da E3b)
| Vista | E4 × E3b, média (% de pixels > 12) | E3b × v11, para comparação |
|---|---|---|
| Lado / frente / trás | 1,03 (1,4%) / 1,39 (2,2%) / 1,25 (1,7%) | 0,49 / 1,27 / 0,28 |
| 3/4 frente e trás | 0,42 (0,6%) / 0,31 (0,4%) | 0,29 / 0,10 |
| Close do rosto (frente / perfil) | **3,68 (6,3%) / 3,12 (5,7%)** | 1,15 / 0,85 |
| Close da juba 3/4 / do tufo | 1,25 (1,9%) / 1,24 (2,0%) | 0,69 / 0,23 |
| Tamanho de jogo (3/4 pequeno) | 0,34 (0,13%) | 0,22 |

**O que se percebe, em ordem de importância:**
1. **Rosto em close:**
   - a pintura fica mais macia (texel limitado);
   - pintas dos bigodes e contorno dos olhos menos nítidos;
   - linha da boca de perfil mais fina.
   - Formas, proporção e expressão da boca fechada se mantêm. Na versão de 1024 fica mais macio ainda.
2. **Juba:**
   - a silhueta e as mechas grandes ficam;
   - as mechas finas que se separavam na E3b ficam fundidas no volume (o voxel de 0,04 une vãos menores que isso);
   - a separação volta só como sombra no mapa de normal.
3. **Tufo:** a forma e as pontas grandes se mantêm, com algumas pontas mais curtas.
4. **Patas e corpo:** praticamente iguais; os antebraços corrigidos da E3b foram preservados.
5. **Boca aberta:**
   - legível a 10°, 20° e 32°, com caninos, pré-molares, gengiva, língua e cavidade;
   - interior com menos subdivisão (palato menos curvo), dentes com 6 lados;
   - a borda do lábio inferior em perfil continua fina, como na E3b, sem piorar; a dobra da comissura também ficou igual, sem regressão.
6. **Tamanho de jogo:** praticamente indistinguível da E3b.

## 5. Deformação (rig PROVISÓRIO, pesos automáticos; não é o rig final)
- **Rig:** 31 ossos.
  - Raiz, Coluna 1–3, Pescoço 1–2, Cabeça;
  - escápula, úmero, antebraço e pata em cada dianteira;
  - coxa, canela e pata em cada traseira;
  - Cauda 1–5.
  - As juntas foram achadas na própria malha.
- **Pesos automáticos:** 286 vértices ficaram sem peso (dentes e língua, cascas soltas); no teste foram para `Cabeca`.
- **Arestas esticadas por pose** (`review/e4/deform/deformacao.json`):

  | Pose | Esticadas > 1,5× | Encolhidas < 0,6× | Razão máx | Razão mín |
  |---|---|---|---|---|
  | Pescoço baixo e virado | 29 | 27 | 1,66 | 0,45 |
  | Passo dianteiro | 6 | 25 | 2,07 | 0,41 |
  | Passo traseiro | 6 | 30 | 1,59 | 0,22 |
  | Coluna curvada | 0 | 0 | 1,26 | 0,81 |
  | Cauda erguida | 0 | 0 | 1,40 | 0,71 |

- **No render:** não há rasgo nem afundamento grande. A juba acompanha a cabeça em bloco, com dobra suave no pescoço.
- **Limite honesto: não há laços de articulação desenhados à mão.**
  - A redução produz triângulos irregulares, com mais densidade no rosto.
  - Cotovelos, joelhos e jarretes dobram pelos pesos, sem anéis dedicados; em dobras fortes, a compressão (razão até 0,22 no jarrete) pode afinar ou marcar o volume.
  - As mechas da juba não têm cadeias próprias; os controles secundários vão depender de pesos pintados no rig.
  - Se o rig mostrar cisalhamento nas mechas ou nas articulações, a saída é reforçar a densidade nessas regiões, protegendo-as na 2ª passada como foi feito com o rosto. Isso custa triângulos e eu traria o custo medido antes.

## 6. Alternativas (para decisão do usuário; nenhuma foi aplicada)
Na minha avaliação, a meta de 15–18 mil não destruiu a identidade: a perda está concentrada na nitidez da pintura do rosto em close. Se o usuário quiser mais fidelidade, há duas trocas possíveis.

| Opção | Custo | O que resolve |
|---|---|---|
| A. Atlas do rosto à parte | +1 material e +1 jogo de texturas de 1024 | Rosto com cerca de 2–3× mais texel |
| B. Juba e corpo com mais triângulos (~28–32 mil no total) | Malha em 2 MeshParts, cada uma abaixo de 20 mil | Mechas finas separadas |

- A opção B não foi medida; eu mediria antes de decidir.

## 7. Pendências e riscos
- Aprovação visual da E4 pelo usuário; o rig e as animações só começam depois.
- Não testado no Roblox: importação do GLB, escala, skinning, `SurfaceAppearance` com 1024 e FPS em PC e celular.
- A exportação de teste (GLB) não foi feita: sem o rig final, ela não testaria o que importa (pesos e ossos). Fica para depois do rig.
- Rig final:
  - limitar a 4 influências por vértice;
  - dar pesos aos dentes e à língua (`Cabeca`, `Mandibula`, `Lingua`);
  - laços e controles da juba.
- A boca de jogo herda a mesma comissura simplificada e o lábio inferior fino da E3b.
