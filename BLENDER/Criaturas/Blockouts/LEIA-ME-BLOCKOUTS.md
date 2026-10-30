# Biblioteca de blockouts de criaturas (Operação Creature Blockout, 26/10/2026)

**O que é:** silhuetas 3D (formas básicas) das **16 formas oficiais** do RPG_02, para avaliação **antes** do refinamento, da pelagem, do rigging e das animações.

**O que não é:** modelo final. Não há texturas, pelagem detalhada, materiais finais, rig, animação nem importação no Roblox.

## Fontes
- **Medidas e anatomia:** `RPG_02_Criaturas_Elementos_e_Poderes.docx`, conferido também contra o `Biblioteca_Criaturas.Catalogo` do Studio. Do `RPG_01_Mundo_e_Sistemas.docx` nada desta operação foi necessário além da lista de biomas.
- **Silhuetas:** as miniaturas de silhueta dos painéis em `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/`. O Leviatã não tem silhueta, então usei a imagem principal do painel.
- **Escala:** 1 unidade = 1 stud (importar no Roblox com *Scale Unit = Stud*). Frente −Y, Z para cima, apoio em z = 0. O boneco branco de 5,2 studs é o personagem do Roblox, só para escala.
- **Medidas fora do documento:** marcadas como **provisórias**. Alguns painéis colocam o humano com uma escala diferente da oficial; nesses casos vale o RPG_02.

## Arquivos
- `CR_Blockouts_Biblioteca.blend`: as 16 formas lado a lado (`CREATURES/BLOCKOUTS/<Especie>`) e os humanos em `REF_Escala`. Tem 41 objetos de malha, o maior com 18.000 triângulos.
- `<Especie>/<Especie>_blockout.blend`: versão de trabalho de cada forma, na origem.
- `build/`: scripts que regeneram tudo.
  - `blockout_lib.py`: massa fundida (voxel remesh + suavização), membranas, fileiras de espinhos.
  - `lobo_base.py`: base canina dos Lobos e do Cérbero.
  - `dragao_base.py`: base dracônica dos 3 Dragões.
  - `build_<Especie>.py`: um script por forma.
  - `gate.ps1`: build, `world_gate` (IoU) e renders.
  - `matte.py`, `analisar.py`, `folha.py`, `contato.py`, `montar_biblioteca.py`.
- `review/Folha_<Especie>.png`: silhueta oficial, gate (quando aplicável), frente, lateral, 3/4 e tamanho de jogo (128 px).
- `review/Biblioteca_16_formas_3-4.png`: visão geral.

## Técnica
Skill **blender-image-to-3d**, *fused organic base*:
1. Massas anatômicas: elipsoides de músculo, cadeias de membros com articulações, mechas.
2. União por **voxel remesh** numa **malha única**, com suavização proporcional ao tamanho da criatura.
3. Redução ao orçamento.

Separadas ficam só as partes rígidas (chifres, garras, cristais, espinhos, ferrão) e as membranas (asas, nadadeiras).

O gate de silhueta usa `world_gate.py`, que compara o modelo com a silhueta oficial **na escala e na posição reais**, pondo o modelo na passada da referência. A pose salva é a **neutra**, que é a usada para o rig.

## Resultado por forma

| Forma | Construção | Medidas (studs) | Gate de silhueta | Observações |
|---|---|---|---|---|
| Leão Solar | nova (v2 corrige a v1 reprovada) | ombro 11,5 (oficial 10–13); topo da juba 19,05; comprimento 27,1 | IoU **0,821** | A juba da referência passa da face; cobri-la enterraria o rosto (escolha anatômica) |
| Lobo Ancestral | nova (base canina) | ombro 6,5 (5,5–7); 13,0 × 8,3 | IoU **0,836** | Esguio/atlético (RPG_02) |
| Lobo Ártico | mesma base, parâmetros robustos | ombro 6,6 (5,5–7); 13,2 × 8,4 | IoU **0,841** | "Mais robusto": peito, pelo, patas, ventre |
| Urso Silvestre | nova | corcova 9,0 (8–10); 14,9 de comprimento | IoU **0,802** | A referência ruge de cabeça erguida; o blockout fica neutro |
| Búfalo Colossal | nova | corcova 16 (14–18); 21,2 de comprimento | IoU **0,799** (indicativo) | Silhueta oficial em perspectiva 3/4 |
| Cérbero Sombrio | base canina + 3 cabeças | ombro 14 (12–16); 27,5 × 17,9 | só visual | Silhueta oficial em 3/4, fundida às rochas |
| Crocodilo Primordial | nova | ombro ~5,8 (5–7); comprimento 30,6 (24–32) | só visual | Referência na água (patas submersas) |
| Basilisco | nova | ombro 8,3 (7–10); comprimento ~27,5 **provisório** (o RPG_02 não fixa) | só visual | Referência em água/lama |
| Lagarto Cristalino | nova | comprimento 24,2 (18–26); altura ~11 provisória | só visual | Referência sobre rochas |
| Escorpião Colossal | nova | comprimento ~20,4 com a cauda em arco; ~21,5 estendida (16–24) | só visual | Altura corporal PENDENTE no RPG_02 |
| Serpente Marinha | nova | ~40 ao longo do corpo (30–45); sem patas | só visual | Referência enrolada em S vertical |
| Leviatã Jovem | nova | comprimento 74,4 (55–80); 4 nadadeiras | só visual | Sem silhueta oficial |
| Wyvern | nova (anatomia bípede própria) | ombro 11 (9–13); envergadura 38 (30–42) | só visual | Bípede = PROPOSTA visual do RPG_02 |
| Dragão das Montanhas | base dracônica | ombro ~21 (18–24); 94 × 62 com as asas meio erguidas | só visual | Robusto, placas, chifres curvos |
| Dragão Glacial | base dracônica | ombro ~21; pescoço 15% mais longo | só visual | Esguio, chifres retos, cristais |
| Dragão Sombrio | base dracônica | ombro ~21 | só visual | Vários chifres, espinhos duplos, esporas nas asas |

**Gate "só visual":** a silhueta oficial está em pose dramática, em perspectiva ou fundida com água/rochas, e um IoU mediria o cenário, não a anatomia. A comparação é lado a lado nas folhas.

**Meta da skill (IoU 0,85 no blockout):** nenhuma forma a atingiu na versão final.
- O Leão chegou a 0,856, mas eu priorizei a anatomia (face projetada).
- Os demais ficaram entre 0,80 e 0,84, contra miniaturas de 120–180 px.

## Reaproveitamento
Os 10 modelos Blender da Operação C1 foram testados como blockout e **reprovados contra as referências**: magros, de patas altas e com aspecto de lagarto (`review/_contato_reaproveitados.png`). Por isso:
- **reaproveitados: 0**;
- **construídos: 16**.

Os `.blend` originais da C1 **não foram alterados**.

## Formas regionais
- **Com silhueta própria:**
  - Lobo Ancestral × Lobo Ártico, pela diferença documentada esguio × robusto;
  - os 3 Dragões, pelo documento: "chifres, asas, escamas e proporções regionais distintos".
- **Variantes só de cor/padrão:** os 3 padrões de cada forma (48 no total). Ficam para a fase de texturas, sem modelo próprio.

## Pendências conhecidas
- Leão abaixo da meta de IoU (escolha anatômica). Urso e Búfalo prejudicados pela pose e pela perspectiva das referências.
- Dragões e Wyvern: cabeças e asas genéricas para um blockout. Faltam a pose de asa fechada (repouso) e cabeças com mais caráter.
- Escorpião: altura corporal pendente no RPG_02. Basilisco: comprimento pendente. Lagarto: altura provisória.
- Cérbero: as três cabeças estão na mesma altura (a referência as escalona).
- Nada foi importado no Roblox, sem rig e sem testes de desempenho no jogo.
