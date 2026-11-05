# Leão Solar — E4b r2: correção de cotovelo, punho e juba do peito (04/11/2026)

Pedido do usuário depois da E4b: "Corrigir antes" (cotovelo, punho e juba do peito antes do rig final).
Tudo no Blender. Nada importado nem testado no Roblox. Sem Meshy, sem Studio, sem commit.

## O que mudou (só rig de teste e pesos; a malha é a mesma)

Mesma malha da E4b (17.602 tris, mesma UV, mesmas texturas `e4b/tex/`), então a aparência neutra não muda.
Arquivo: `Leao_Solar_Ref_E4b_r2.blend` (a `Leao_Solar_Ref_E4b.blend` ficou intacta). Scripts em `build/e4b_r2/`.

1. **Ossos auxiliares de volume** (`Cotovelo_Aux_DD/DE`, `Punho_Aux_DD/DE`).
   - Ficam na junta, com a mesma orientação de repouso do osso filho. São filhos do Úmero e do Antebraço.
   - Giram **metade** da rotação do filho. No rig final, isso vira uma restrição Copy Rotation com influência 0,5, gravada nos clipes para o Roblox.
   - A faixa de mistura dos pesos passou de "pai ↔ filho" para "pai → aux → filho", em tenda: no meio da faixa o vértice segue só o auxiliar.
   - Com isso, a dobra não perde mais volume por mistura de ossos: o afinamento máximo cai de cos(a/2) para cos(a/4).
   - O rig agora tem 57 ossos (56 deformam).
2. **Peso do tronco fora da pata dianteira.**
   - Abaixo do meio do antebraço/pata (u ≥ 1,2 na cadeia ombro→dedos), dentro do raio real da pata, o peso de Peito, Coluna e Juba volta para os ossos da pata.
   - Na E4b, o Peito chegava com 0,05–0,27 até o punho. Por isso o punho e o antebraço eram puxados pelo tronco.
   - As mechas da juba (máscara de cor) não entram nessa limpeza.
3. **Variantes testadas para a juba do peito**, todas com o mesmo conjunto de poses:
   - **gradiente por distância:** espalha o esticamento, mas a mecha sobre a pata passa a ser arrastada com a pata;
   - **retirada total do peso da pata na máscara (como na E4b):** foi a escolhida;
   - **mechas longas tratadas como juba:** reprovada. A ponta da mecha está fundida no antebraço pelo voxel, então o esticamento só passava para a pele.
   - **Escolha:** retirada total, mais a limpeza do item 2. As mechas longas que pendem do peito até o antebraço ficam com a pata. O esticamento que sobra fica na própria mecha (pelo), não na pele.

## Medições (mesmas 12 poses da E4b; E4 e E4b com o rig de teste da E4b)

- **pata:** espessura (distância até os ossos, posado/repouso) só dos vértices que pertencem à pata, ou seja, com peso ≥ 0,5 na cadeia, numa esfera de 2,2.
  - A medida "da zona" da E4b, numa esfera de 1,3, pegava no cotovelo 58 de 59 vértices de juba.
  - Por isso o "cotovelo pior que a E4" da E4b era a juba cruzando a pata, não a pele afinando.
- **pele:** arestas fora da máscara de cor da juba.
- **vol perd.:** perda de volume do corpo inteiro na pose. Um valor positivo quer dizer que a dobra afinou.

| Pose | Versão | Pata p5 / mín | Pele: arestas > 1,5× / abs máx | Corpo: arestas > 1,5× / abs máx | Vol perd. |
|---|---|---|---|---|---|
| cotovelo 95° | E4 | – (2 v) | sem máscara | 42 / 0,74 | 2,28 |
| | E4b | 0,56 / 0,54 | 42 / 0,51 | 105 / 0,82 | 1,51 |
| | **r2** | **0,58 / 0,58** | **2 / 0,36** | **58** / 0,92 | **0,03** |
| punho 85° | E4 | 0,51 / 0,33 | sem máscara | 2 / 0,33 | 1,67 |
| | E4b | 0,43 / 0,29 | 1 / 0,20 | 1 / 0,23 | 0,49 |
| | **r2** | **0,54 / 0,43** | 2 / 0,19 | 11 / 0,35 | **−0,81** |
| ombro 38° à frente | E4b | – | 62 / 0,53 | 206 / 1,35 | −11,2 |
| | **r2** | – | **8** / 0,64 | **143** / 1,78 | −10,7 |
| passo dianteiro | E4b | 0,45 / 0,42 | 40 / 0,62 | 125 / 1,19 | −3,2 |
| | **r2** | 0,46 / 0,45 | **9 / 0,50** | **96** / 1,48 | −6,7 |
| pescoço baixo e virado | E4b | – | 27 / 0,30 | 291 / 0,84 | 13,3 |
| | r2 | – | 27 / 0,30 | 305 / 0,84 | 13,8 |

- **Patas traseiras, cauda, coluna e boca:** idênticas à E4b (pesos não mudaram ali).

Tabela completa: `review/e4b_r2/med3_*/poses.json` e a prancha.

## Leitura honesta

- **Punho:** melhorou e agora afina menos que na E4 (mín 0,43 contra 0,33). O volume da dobra não cai mais.
- **Cotovelo:**
  - A perda de volume sumiu (1,51 → 0,03).
  - A pele fora da juba quase não estica mais: 42 → 2 arestas acima de 1,5×, com no máximo 2,33× (antes 5,43×).
  - A espessura da pata ficou igual (0,56 → 0,58). Ela é a compressão do lado de dentro da dobra, que existe mesmo com rotação rígida.
- **Juba do peito/ombro:**
  - A pele (fora da juba) estica muito menos: ombro 62 → 8 arestas, passo 40 → 9.
  - O total de arestas esticadas caiu de 206 para 143 no ombro e de 125 para 96 no passo.
  - **Mas** o maior alongamento absoluto subiu (1,35 → 1,78 no ombro; 1,19 → 1,48 no passo). Ele fica numa mecha comprida que pende do peito e tem a ponta fundida no antebraço pelo voxel: a mecha estica em vez da pele da pata.
  - Resolver isso de vez exige mexer na geometria: soltar a ponta dessas mechas da pata, o que refaz UV e bake nessa região.
- **Pescoço baixo e virado:** sem mudança relevante (291 → 305 arestas na juba, mesma pele).

## Vídeos

`review/e4b_r2/videos/`: passo dianteiro, pescoço e juba (lado e 3/4, com chão). Os demais clipes não mudam (pesos iguais aos da E4b).
Contatos das patas apoiadas (`review/e4b_r2/videos/contatos.json`): escorregamento 0,000 em todos; altura mínima de −0,006 a 0,010.

## Arquivos

- `Leao_Solar_Ref_E4b_r2.blend`: E4b + rig de teste revisado (57 ossos) e pesos novos.
  - Tem o atributo de QA `qa_juba`, só para as medições: remover antes de exportar.
- `build/e4b_r2/`:
  - `r2_03_rig_pesos.py` (rig e pesos);
  - `r2_04_poses.py` (poses e medições);
  - `r2_05_videos.py`;
  - `r2_06_prancha.py`;
  - `r2_00_diag.py` e `r2_poses_lib.py` (diagnóstico);
  - `r2_qa_attr.py`;
  - `r2_quadros.py` (quadros dos MP4 pelo editor de vídeo);
  - `r2_tab.py`.
- `review/E4b_r2_prancha.png`.
- `review/e4b_r2/pesos_r2.json`:
  - 0 sem peso;
  - no máximo 4 influências;
  - 0 mal normalizados;
  - hierarquia completa.
- Variantes descartadas: `review/e4b_r2/var_*.blend` e `med_*`, mantidas como evidência.
