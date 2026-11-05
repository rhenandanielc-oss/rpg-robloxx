# Leão Solar adulto — modelo pela referência principal

**APROVADO (aparência, no Blender) em 03/11/2026: `Leao_Solar_Ref_E2_v11.blend`.** Ainda falta: mandíbula e interior da boca, as 573 bordas abertas, as manchas dos antebraços, a malha de jogo, o rig e o teste no Roblox.

## E5 Fase B (05/11/2026): atitude agressiva e ataques — FASE B ACEITA em 05/11 (patadas r3; oficial `Leao_Solar_Ref_E5_clipes_r3.blend`)
- **Bote r4 (05/11), APROVADO; arquivo oficial dos clipes: `Leao_Solar_Ref_E5_clipes_r6.blend`:** agacha mais fundo antes do bote (2,9 studs; 3,2 encostava o peito no chão).
  - Arquivo `Leao_Solar_Ref_E5_clipes_r6.blend` (r3, r2 e v1 guardados); `E5-RELATORIO.md`, seção 8.5.
- **Bote r3 (05/11), substituído pelo r4:** impulso das traseiras (agacha, empurra na ponta dos dedos, sai esticada, recolhe no voo).
  - Alcance máximo de 45 studs (aprovado), gerador paramétrico para a mira.
  - Arquivo `Leao_Solar_Ref_E5_clipes_r5.blend` (r2 e v1 mantidos); `E5-RELATORIO.md`, seção 8.4.
- **Bote r2 (05/11), substituído pelo r3:** as patas da frente ficaram sem o estalo da decolagem.
  - Modo relativo, meio do balanço em relação ao ombro e agachamento/pouso mais suaves.
  - Arquivo `Leao_Solar_Ref_E5_clipes_r4.blend` (`Leao_Bote_v1` mantido); `E5-RELATORIO.md`, seção 8.3.
- **Patadas r3 (05/11), APROVADAS:** a pele do punho vincava por causa de pesos do Peito e da juba no antebraço.
  - Pesos limpos no rig (`build/e5/e5_15_pesos_antebraco.py`) e punho limitado a ~40° na subida.
  - Arquivo `Leao_Solar_Ref_E5_clipes_r3.blend` (r2 e v1 guardadas); `E5-RELATORIO.md`, seção 8.2.
- **Patadas r2 (05/11), em revisão:** a torção do punho foi corrigida em `Leao_Solar_Ref_E5_clipes_r2.blend` (as Patadas v1 continuam no arquivo como `_v1`).
  - Evidência em `review/e5/patada_r2/`; relatório em `E5-RELATORIO.md`, seção 8.1.
- Rig com lábios (`Labio_D/E`, 63 ossos); `Leao_Solar_Ref_E5_clipes.blend` com 28 ações (Fase A + B).
- Clipes em `build/e5/e5_21_faseB.py`, prancha `review/E5_faseB_prancha.png`, vídeos em `review/e5/faseB/`, relatório `E5-RELATORIO.md` (seção 8).

## E5 (04/11/2026): rig de produção + clipes da Fase A — FASE A ACEITA em 05/11
- `Leao_Solar_Ref_E5_rig.blend`: 61 ossos, com orelhas e pálpebras.
- `Leao_Solar_Ref_E5_faseA.blend`: 16 ações `Leao_<clipe>`.
- Relatório `E5-RELATORIO.md`, scripts `build/e5/`, prancha `review/E5_prancha.png` e vídeos em `review/e5/faseA/`.
- A "mecha fundida" da E4b r2 não existia (cortes em `review/e5/`).

## E4b r2 (04/11/2026): correção de cotovelo, punho e juba do peito, em avaliação
- `Leao_Solar_Ref_E4b_r2.blend`: mesma malha e texturas da E4b; mudam o rig de teste (57 ossos, com auxiliares de volume `Cotovelo_Aux`/`Punho_Aux` a meia rotação) e os pesos da pata dianteira.
- Relatório `E4b_r2-RELATORIO.md`, scripts `build/e4b_r2/`, prancha `review/E4b_r2_prancha.png` e vídeos em `review/e4b_r2/videos/`.

## E4b (03/11/2026): malha preparada para deformar + rig de teste, em avaliação
- `Leao_Solar_Ref_E4b.blend`, com texturas em `e4b/tex/`, relatório `E4b-RELATORIO.md`, scripts `build/e4b/`, prancha `review/E4b_prancha.png` e vídeos em `review/e4b/videos/`.

## E4 (03/11/2026): malha de jogo, em avaliação
- `Leao_Solar_Ref_E4.blend`, com texturas em `e4/tex/`, relatório `E4-RELATORIO.md`, scripts `build/e4/e4_0*.py` e prancha `review/E4_prancha.png`.
- Pipeline: voxel 0,04 → redução em duas passadas (rosto protegido) → boca leve (`e4_03`, cópia do `c02`) → UV por regiões → bake da E3b.

## E3 e E3b (03/11/2026): boca, mandíbula, antebraços, em avaliação
- E3: `Leao_Solar_Ref_E3.blend`, relatório `E3-RELATORIO.md`, scripts `build/e3_*.py`.
- E3b (correção da boca e da junção da mandíbula): `Leao_Solar_Ref_E3b.blend`, relatório `E3b-RELATORIO.md`, scripts `build/e3c/c0*.py`, prancha `review/E3b_prancha.png`, vídeos `review/E3b_boca_*.mp4`.
- **Regra:** não rodar dois Blender renderizando ao mesmo tempo. Um render de jogo saiu com ruído cinza por concorrência de GPU; refeito sozinho, saiu limpo.

## E2 (03/11/2026): correção visual da E1 r8 com o Meshy, em avaliação
O usuário reprovou a E1 r8 e autorizou o Meshy no chat ("pode criar no meshy, se for melhorar para chegar a referencia").
- **Geração:** 1 Multi-Image to 3D (`build/meshy_leao.py`) com as 3 vistas recortadas da referência principal (`meshy/entrada/`), com textura PBR.
  - Custo: **30 créditos**; o saldo passou de 685 para 655.
  - Saída crua: `meshy/v1/` (GLB/FBX, texturas de 2048, miniatura, `tarefa.json`).
- **Normalização** (`build/06_importar_meshy.py`, depois `10_e2_v2.py`):
  - frente em −Y, pés em Z = 0, escala pelo topo da juba (18,66);
  - deslocamento de +10 px no perfil para o melhor encaixe.
  - Dorso medido: 11,2–11,5 studs.
  - Os 4 pés tocam o chão: Z mínimo de 0 a 0,005.
- **Material de pelo** (`build/15_material_pelo.py`):
  - metal 0, especular 0,25, rugosidade ~0,8;
  - o especular 0,5 do Meshy deixava o pelo cinza/plástico.
- **Albedo** (correção na textura, não na exposição; `09_corrigir_albedo.py`, `12_zonas_uv.py`, `13_ganhos_albedo.py`):
  - zona juba/tufo × corpo marcada por face pelo volume das 3 vistas e rasterizada na UV;
  - ganho por canal em luz linear contra as médias de 9 regiões do perfil;
  - no corpo, ganho só nos tons médios e escuros; os claros vão para um creme quente.
  - Erro médio de cor: 28,5 (Meshy cru) → **19,1** (v8).
- **Renders:** `build/07_render_eevee.py` (EEVEE, mundo cinza uniforme + sol suave, a mesma luz em todas as vistas). Pranchas: `build/08_prancha_e2.py`.
- **Entrega:**
  - `Leao_Solar_Ref_E2_v8.blend`;
  - `review/E2_v8_conjunto.png` (referência | E1 r8 | E2 | silhuetas; 3/4 frente e trás; tamanho de jogo);
  - `review/E2_v8_closes.png` (rosto de perfil e de frente, tufo, juba);
  - `review/E2_v8_cores.png` e `review/E2_v1_cores_antes.png`; métricas em `review/E2_v8_metricas.json`.
  - IoU: perfil 0,911, frente 0,897, traseira 0,877.
- **Malha E2:**
  - 205.876 tris, 1 material e texturas de 2048 (albedo, normal, rugosidade);
  - com as costuras de UV soldadas vira 1 peça só (103.000 vértices), mas tem **573 bordas abertas** (furos pequenos a localizar);
  - casca fechada: **sem mandíbula separada e sem interior da boca**.
  - QA: `build/11_qa_malha.py` e `16_qa_soldado.py`.
- **Versões intermediárias preservadas:** `_E2_meshy_v1`, `_v2`…`_v7` e `review/e2_*`. A E1 r8 (`Leao_Solar_Ref_E1_massas.blend`) não foi alterada.

### E2 v9–v11 (03/11/2026, com o usuário ausente; Meshy autorizado por ele)
- **v9:** a v8 com ajuste local do rosto (`build/17_regioes_rosto_uv.py`, `18_rosto_albedo.py`):
  - trufa do nariz marrom-escura (escolhida pela cor rosada perto da ponta do focinho);
  - rosto com saturação −15%.
  - Erro de cor: 19,0.
- **v10:** Meshy **Retexture** da mesma malha, com a referência como estilo e a UV original (`build/meshy_retexture_leao.py`).
  - Custo: **10 créditos**. Saída em `meshy/retex1/`.
  - Erro de cor cru: 24,3.
- **v11 (recomendada):** o albedo do Retexture com a correção por zona e a do nariz/rosto. Erro de cor 19,3.
  - Visualmente mais fiel que a v9 no rosto, queixo, ventre e patas (sem branco-amarelado).
  - Defeito: manchas mais escuras nos antebraços.
- Arquivos: `Leao_Solar_Ref_E2_v11.blend`, `review/E2_v11_{conjunto,closes,cores}.png` e a comparação direta `review/E2_v9_x_v11.png`.
- Créditos do Meshy gastos por este chat: 40 (30 + 10). Saldo da conta lido às 16h de 03/11: 514. A conta é compartilhada; os outros 131 créditos foram consumidos por outros chats ao mesmo tempo.

**Estado:** etapa 1 (silhueta e massas) entregue em 03/11/2026 para aprovação. O modelo **não** está aprovado, **não** foi testado no Roblox e **não** é a criatura pronta no jogo.

**Referência principal:** `REFERENCIAS/planicies-douradas/leao-solar/leao-solar-referencia-principal.png`, cópia sem alteração do anexo do usuário. Tem perfil, frente e traseira do mesmo leão.

## Arquivos
- **Trabalho:** `Leao_Solar_Ref_E1_massas.blend`, coleção `CR_Leao_Solar_E1`. Fica fora do git pelo `.gitignore`.
- **Prancha da entrega:** `review/E1_prancha_massas_r8.png`, com os IoU em `review/E1_prancha_massas_r8_iou.json`.
  - Rodadas anteriores: `review/e1_r1` … `e1_r8`.
- **Máscaras da referência:** `ref/`. São geradas pelos scripts 00 e 01 e podem ser refeitas.

### Scripts (`build/`, reproduzíveis)

| Script | Função |
|---|---|
| `00_mascaras.py` | Máscara do fundo e caixas das 3 vistas (python do sistema). |
| `01_mascaras_npy.py` | Máscaras `.npy`: perfil, região da juba, tufo, frente e traseira simetrizadas. |
| `sdf.py` | Campo de distância em numpy (elipsoides, cones arredondados, união suave) e extração por surface nets. |
| `02_massas.py` | Constrói tudo (Blender headless, ~16 s). |
| `03_render_vistas.py` | Renders ortográficos alinhados pixel a pixel com os recortes da referência, mais o 3/4. Workbench, luz de estúdio neutra, sem sombras. |
| `04_prancha.py` | Prancha: referência, modelo e sobreposição de silhuetas, com IoU. |

### Como regenerar

Os comandos rodam dentro da pasta `Leao_Solar_Ref/`.

1. Máscaras:
   ```bash
   python build/00_mascaras.py <ref.png> ref
   ```
   ```bash
   python build/01_mascaras_npy.py ref
   ```
2. Modelo:
   ```bash
   blender -b --factory-startup -P build/02_massas.py -- ref Leao_Solar_Ref_E1_massas.blend
   ```
3. Renders:
   ```bash
   blender -b Leao_Solar_Ref_E1_massas.blend -P build/03_render_vistas.py -- review/<rodada> [Juba,Tufo]
   ```
   O segundo argumento (opcional) lista objetos a ocultar.
4. Prancha:
   ```bash
   python build/04_prancha.py <ref.png> ref review/<rodada> review/<rodada>/prancha.png "<título>"
   ```

## Escala e unidades
- 1 unidade do Blender = 1 stud. Ao importar no Roblox, usar escala em studs.
- Frente = −Y; pés em Z ≈ 0; simétrico em X.
- **Ombro (cernelha): 11,5 studs.** É a medida técnica de trabalho, dentro da faixa oficial de 10–13. Não é regra nova.
- Conversão da referência:
  - perfil: K = 11,5/360 stud/px (dorso a 360 px do chão);
  - frente e traseira: escala pelo topo da juba (18,66 studs) → 0,03024 e 0,03038 stud/px.
- Medido no modelo:
  - topo do dorso sob a juba: 11,15;
  - topo da juba: 18,41;
  - largura total: 9,8 (juba);
  - comprimento do focinho à ponta do tufo: 33,3;
  - fundo das patas: −0,12 (falta assentar em Z = 0).

## Técnica (e por que não reaproveitei v2/v5/CR antigos)
**Antecedentes inspecionados:**
- `CR_Leao_Solar` (blockout de 26/10);
- `Blockouts/Leao_Solar` v2/v5 (rig felino de 36 ossos e 28 animações).

São massas lisas feitas sobre outra referência, com a cauda erguida em gancho, e foram reprovadas ou estão pendentes (juba lisa, peito fraco, boca sem interior). Adaptá-las custaria mais do que construir de novo. A malha é nova; os originais não foram tocados.

**Aproveitado dos antecedentes:**
- a convenção de escala (11,5 de ombro, 1 unidade = 1 stud, frente −Y);
- a ideia de grafo de massas da skill `pipeline-criatura`;
- as notas de anatomia felina de `DOCS/CRIATURAS-REFINAMENTO-ANALISE.md`.

**Corpo:**
- 1ª tentativa com o modificador Skin: deu seções quadradas, foi descartada.
- Versão atual: campo de distância com elipsoides musculares, a saber:
  - tronco, escápula, tríceps, pernil e gastrocnêmio;
  - crânio, maçãs, almofadas dos bigodes e orelhas.
- Membros, pescoço e cauda são cones arredondados, com cotovelo para trás, joelho para frente e jarrete para trás.
- Tudo é unido com fusão suave e extraído por surface nets.

**Mandíbula:**
- Objeto separado `Leao_Mandibula`, com pivô na articulação têmporo-mandibular.
- Boca fechada nesta etapa.

**Juba:**
- Núcleo: volume das 3 vistas (casco visual com seção em superelipse, estreitando para trás sobre os ombros). Rosto e orelhas ficam fora desse volume.
- Mechas: ~420 tubos achatados e afilados. Cada um segue a superfície como **linha de fluxo**: para cima e para trás no topo, para trás na parte de trás, para baixo no peito. Só a ponta aflora no contorno.
- Núcleo e mechas são unidos por remesh voxel de 0,08.
- Cor por atributo: dourado no alto e na frente, cobre e vermelho embaixo e atrás; pontas mais claras, fundo entre mechas mais escuro.

**Tufo:** mesma técnica, com o fluxo ao longo do eixo do tufo.

**Pose:** neutra, com as 4 patas simétricas e as traseiras alinhadas, para o rig.

## Custo atual (malha de TRABALHO, não de jogo)

| Objeto | Tris |
|---|---|
| Corpo | 399.496 |
| Juba | 281.072 |
| Tufo | 54.820 |
| Mandíbula | 20.984 |
| Olhos | 2 × 528 |
| **Total** | **757.428** |

- 3 materiais (M_Leao_Pelo, M_Leao_Juba, M_Leao_Olho), só com cor por vértice; ainda não há texturas.
- A malha de jogo será feita depois: retopologia/decimação, UV e mapas assados.
- O alvo de jogo (16k do brief antigo e 32k da v5) ainda **não foi definido**. Os dois valores são antecedentes; nenhum está aprovado.
- FPS e desempenho no celular **não** foram medidos.
