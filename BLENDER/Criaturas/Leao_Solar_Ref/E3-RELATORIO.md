# Leão Solar — E3, relatório técnico (03/11/2026, em avaliação)

- **Base:** cópia da E2 v11 aprovada. `Leao_Solar_Ref_E2_v11.blend` não foi alterado (data do arquivo: 16:09).
- **Entrega:** `Leao_Solar_Ref_E3.blend`.
- **Intermediários preservados:** `_E3_t1` (topologia), `_E3_t2` (antebraços), `_E3_t3` (boca).
- Tudo foi gerado e testado **só no Blender** (EEVEE, luz neutra igual à das pranchas da E2). Nada foi testado no Roblox.

## 1. Manchas dos antebraços (`build/e3_03_antebracos.py`)
- **Causa:** a mancha estava no próprio albedo. Na frente dos antebraços, entre Z 3 e 4, a luma era ~100, contra ~160–180 no pelo vizinho.
- **Correção, texel a texel:**
  1. mapa de posição 3D de cada texel dos membros, rasterizado na UV;
  2. baixa frequência em 3D (~0,45 stud);
  3. alvo = percentil 80 da luminância do mesmo membro numa janela de ±1,5 stud de altura;
  4. só clareia (até 3× em luz linear) o que está abaixo de 92% do alvo, e a razão é suavizada em 3D.
  - A variação fina do pelo fica.
- **Resultado:** cor média na frente do antebraço em Z 3 foi de (159,90,43) para ~(200,113,54).
- **Evidência:** `review/E3_membros.png` (frente, perfil, trás e 3/4; antes | depois).
- **Resto:** ainda há um leve tom alaranjado no alto do antebraço, junto à juba. Os flancos acima das coxas ficaram um pouco mais claros.

## 2. Mandíbula articulável (`build/e3_05_boca.py`)
- **Decisão técnica:**
  - Recorte rígido abriria uma fenda na garganta ao abrir a boca. No Roblox, sem renderizar o verso das faces, daria para ver através da cabeça.
  - Por isso o lábio foi aberto ao longo da linha da boca. A linha foi medida na v11: comissura (Y −13,96; Z 12,23), frente (Y −15,33; Z 12,43). O corte vai só entre as comissuras: 202 arestas, 102 vértices por lábio.
  - A mandíbula é um grupo de vértices `Mandibula`:
    - peso 1 abaixo da fenda, com a largura anatômica (0,70–1,05 stud de meia-largura);
    - transição suave atrás das comissuras (as bochechas esticam), na barba (acompanha 35–100%) e nas laterais.
- **Rig de teste:** `Leao_Rig_Teste_Boca`, ossos `Cabeca` e `Mandibula`, com pivô na articulação têmporo-mandibular em (0, −12,75, 12,35). Não é o rig final.
- **Poses testadas:** 0°, 10°, 20° e 32° (`build/e3_06_render_boca.py`).
- **Penetração da mandíbula na pele da cabeça ou da juba** (vértices com peso > 0,5 que entram na superfície):

  | Pose | Vértices |
  |---|---|
  | 10° | 3 |
  | 20° | 0 |
  | 32° | 0 |
  | 0° (fechada) | 61 |

  Com a boca fechada, os 61 são o lábio inferior encostado no superior, dentro de 0,25 stud. Não aparece por fora.

## 3. Interior da boca
- Na mesma malha, material `M_Leao_Boca` (cor por atributo `CorBoca`), **fechado e ligado aos lábios:**
  - palato a partir do lábio superior;
  - assoalho a partir do inferior;
  - paredes internas das bochechas, que esticam;
  - garganta compartilhada (peso 0,5);
  - grade de 23 × 10, sombreamento suave e arestas duras na divisa entre pele e interior.
- **Gengivas:** fileira rosada logo atrás da margem escura do lábio.
- **Objetos próprios:**

  | Objeto | Conteúdo | Tris | Preso a |
  |---|---|---|---|
  | `Leao_Lingua` | língua | 400 | Mandibula |
  | `Leao_Dentes_Sup` | 2 caninos, 6 incisivos, 4 pré-molares | 480 | Cabeca |
  | `Leao_Dentes_Inf` | idem | 480 | Mandibula |

- **Boca aberta:** profundidade real; não se vê através da cabeça (o interior é fechado até a garganta).
- **Boca fechada:**
  - 48 de 1.185 vértices do interior, língua e dentes ficam fora da pele: dois filetes escuros milimétricos nas comissuras;
  - diferença de pixels contra a v11 nos closes do rosto: média 0,9 (perfil) e 1,2 (frente), em 255; 0,4–0,5% dos pixels acima de 12 níveis.
- **Testado e descartado:** escurecer a margem dos lábios na textura borrava o bigode e o queixo; ficou só a linha escura que a v11 já tinha.
- **Evidência:** `review/E3_boca.png`, com a boca fechada (v11 × E3, perfil e frente), aberta a 10°, 20° e 32° em 3/4, perfil a 32° e vista interna a 20° e 32°.

## 4. Bordas abertas e não-manifold (`build/e3_00_auditar.py`, `e3_01_topologia.py`, `e3_09_nao_manifold.py`)

| | v11 (costuras de UV soldadas em cópia) | E3 (malha real, sem solda) |
|---|---|---|
| Bordas abertas | **573**, em 274 laços | **4**, em 2 laços |
| Laços por região | juba 249, rosto 17, corpo/cauda 5, tufo 2, patas 1 | 2 na juba (perímetros 0,28 e 0,16 stud) |
| Tamanho dos laços | 272 com 1–4 arestas, 2 com 5–12, nenhum maior | 2 com 2 arestas |
| Arestas com > 2 faces | 287 | 33 (todas na juba) |
| Vértices não-manifold | 35 | 54 (todos na juba) |

- **Causa:** fendas e agulhas do remesh do Meshy, onde as mechas se cruzam. Nenhuma é abertura anatômica nem borda intencional de mecha (a casca do Meshy é fechada).
- **Correção:** fusão no centro de 301 laços com perímetro < 0,8 stud e no máximo 12 vértices; faces degeneradas dissolvidas. A UV ficou nos loops.
- **Os 2 laços restantes** são fendas de 2 arestas presas em vértices não-manifold da juba. Os 54 vértices não-manifold são pontos de contato entre mechas, criados pela fusão.
  - Não são visíveis e ficam para a retopologia da malha de jogo, que reconstrói a superfície.
- A boca não acrescenta borda aberta nem aresta não-manifold.
- **Nota:** a auditoria com solda conta 134 arestas não-manifold na E3, porque junta vértices coincidentes de propósito no interior fechado (paredes que se afastam quando a boca abre). O número real, sem solda, é 33.

## 5. Conjunto
- `review/E3_geral.png`: referência | v11 | E3 em perfil, frente e trás, mais 3/4 de frente e de trás.
- Diferença de pixels contra a v11 nas vistas inteiras: frente 1,4 e perfil 1,1 de média, vinda das pernas.
- **Contagem:**
  - `Leao_Solar_E3`: 206.216 tris, materiais Material_0 (pelo) e M_Leao_Boca;
  - língua e dentes: 1.360 tris;
  - texturas de 2048: albedo da E3, normal e rugosidade do Meshy.
- **Malha de trabalho, não de jogo.**

## Pendências para a próxima etapa (malha de jogo, aguardando aprovação da E3)
- Retopologia deformável para ~15–18 mil tris, com laços de articulação, mais lábios, interior e dentes com orçamento próprio.
- UV nova e bake de albedo e normal a partir da E3.
- Comparação visual LOW × E3 nas mesmas vistas e na de tamanho de jogo, com a perda registrada.
- Se a meta de tris causar perda visível, mostrar alternativas com custo medido antes de decidir.
- Os nomes de osso do rig final devem seguir a regra do Roblox: ligação por nome, sem renomear no Studio.
