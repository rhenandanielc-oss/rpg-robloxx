# Lobo Ancestral (referência de 03/11/2026): asset brief

- **Referência:** `ref/lobo-ancestral-referencia.png`, cópia de `REFERENCIAS/floresta-ancestral/lobo-ancestral/lobo-ancestral-referencia.png`. É uma pintura em 3/4 frontal, com câmera baixa e perspectiva.
- **Regras oficiais (RPG_02):**
  - adulto com 5,5–7 studs até os ombros; esguio e atlético;
  - quadrúpede digitígrado, montável no Adulto (sela leve). A sela não entra nesta tarefa.
  - Os padrões oficiais são Cinza da Floresta, Marrom Selvagem e Areia do Bosque. A referência se aproxima de "Cinza da Floresta" (dorso cinza-escuro, flancos castanhos, máscara e peito creme).
- **Marcas verdes:** são só aparência. Não definem elemento nem poderes; o elemento do lobo continua [PENDENTE].
- **Escala de trabalho:** 1 unidade = 1 stud. Frente em −Y, pés em Z = 0, simétrico em X (esquerda do lobo = +X). Cernelha-alvo: 6,5.
- **O que priorizar:** proporções, rosto, distribuição das cores e direção do pelo.
- **O que não copiar:** distorção de perspectiva da pintura (patas dianteiras enormes e cabeça girada para a câmera). O modelo fica em pose neutra.

## Técnica
1. **Corpo HIGH:** grafo Skin → remesh voxel 0,034 → escultura do rosto. A cabeça é escalada ×1,22 em torno do alto do pescoço.
2. **Pelo:**
   - subpelo: a pele é inflada pela espessura do pelo em cada região;
   - cerca de 5 mil tufos esculpidos na própria pele: crista no meio, sulco entre os tufos e ponta afinando no sentido do crescimento. Vira normal map na LOW.
   - cerca de 800 mechas de malha opaca só onde fazem silhueta: juba, cauda, bochechas, franja da barriga, culote e trás do cotovelo.
   - Sem cartões alpha nesta rodada, para evitar transparência excessiva.
3. **Cor:** atributo de vértice por região → bake 1024 na LOW. As marcas verdes ficam num atributo separado (emissão baixa).
4. **LOW (próxima etapa):** corpo decimado (~10k tris) + mechas reduzidas. Cada MeshPart com ≤ 20k tris; textura de 1024.

## Medidas registradas por rodada
Ver `review/rNN/` (renders, prancha) e o log impresso pelo script (`LOBO_MEDIDAS`, `LOBO_TRIS`).
