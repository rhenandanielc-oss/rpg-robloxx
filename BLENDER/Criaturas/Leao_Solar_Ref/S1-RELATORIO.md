# Leão Solar — S1: sela felina (06/11/2026), r4 APROVADA pelo usuário em 06/11/2026 (Blender; arquivo oficial `Leao_Solar_Ref_S1r4_sela.blend`)

**Pedido do usuário:** fazer a sela e a animação de subir na sela, no Blender, antes do Studio.

**Decisões do usuário (06/11):**
- **Subida:** o leão agacha e o cavaleiro sobe.
- **Estilo:** couro com detalhes dourados, "dentro das características visuais dos materiais para a sela do leão, como está nos documentos".
- **Lados:** subir pelos dois lados.

**Etapas:**
- **S1 = sela:** este relatório.
- **S2 = Montar pelos dois lados:** só depois da aprovação da sela, porque a posição do assento define a animação.

**Regras oficiais seguidas:**
- **Montaria** a partir do Adulto, com **sela adaptada a corpo felino** (`DOCS/criaturas/leao-solar.md`, `DOCS/biomas/planicies-douradas.md`).
- **Equipamento de criatura** só sela e arreio, apropriados à anatomia (RPG_01 25.1.8).
- **Materiais:** os básicos são couro, ferro, aço, madeira e tecido reforçado (25.3.1). O material animal só entra se tiver função plausível na peça e aparecer no visual (25.6.4, 25.16, 25.22.7).
- **Materiais regionais das Planícies:** estrutural **Couro das Planícies**, especial **Âmbar Solar**. Do antílope vêm Pele de Antílope, Tendão de Antílope e Chifre Leve.

## Peças e materiais (proposta)

| Peça | Material (fonte) | Função |
|---|---|---|
| Assento com cabeça e patilha; aba; cilha; apoios de pé | **Couro das Planícies** (regional estrutural) | onde o cavaleiro senta; prende a sela; apoio dos pés |
| Manta sob a sela | **Pele de Antílope** (Antílope-das-Planícies), pelo curto dourado | protege o dorso e dá o tom dourado |
| Debrum da manta e costura da aba | **Tendão de Antílope** | costura e acabamento visíveis |
| Alça da mão, na cabeça do assento | **Chifre Leve** (antílope) | pegador ao subir e ao sentar |
| Adorno solar: pedra na cabeça do assento e nas argolas da cilha | **Âmbar Solar** (regional especial), sem emissão nem efeito | identidade das Planícies |
| Guarnição do adorno (8 raios), argolas da cilha, alças dos apoios | **Ferro** (básico) | ferragens |

**Sem peitoral:** a juba cobre todo o peito e os ombros, até y −2 no dorso e −3 nos lados. Um peitoral ficaria escondido e brigaria com os fios.

**Sem estribo pendurado:** o dorso do leão é largo (~4 studs) e as pernas do R15 são curtas. Um estribo ficaria solto no ar, sem cavaleiro. Por isso usei apoios de pé fixos na manta, como na sela aprovada do Crocodilo.

## Encaixe

- **Malha do leão descentrada:** ela está ~0,45 stud deslocada para +X em relação à coluna do rig, em todo o dorso.
  - A sela é centrada no corpo (x 0,45), não no osso.
  - O cavaleiro também ficará em x 0,45, preso ao osso `Coluna1`.
- **Posição:** trecho plano do dorso (11,3 studs), atrás da juba.
  - manta de y −2,05 a +2,15;
  - assento centrado em y 0,20;
  - cilha em y −2,35, atrás dos cotovelos e da borda da juba.
- **Altura:** o topo do assento fica a 11,6 studs e o quadril do cavaleiro a 12,23.
  - alça da mão: (0,45, −0,95, 12,45);
  - apoios de pé: tornozelos em (2,35 / −1,45, −0,35, 11,38).
- **Tamanho:** 5.970 triângulos e 3.057 vértices numa só malha, `Leao_Solar_Sela`, com 6 materiais. A sela do Crocodilo tem 5.824.
- **Pesos:** copiados da pele do leão, com no máximo 4 ossos por vértice.
  - Os ossos da juba, cauda, pescoço e cabeça ficam fora, para a sela não balançar com a juba.
  - O raio da média é de 0,7 no centro e na cilha e de 0,45 na borda da manta, que acompanha melhor o lombo e os ombros.
  - Argolas, alça e adorno são rígidos (pesos do ponto de ancoragem).
- **O que não mudou:** malha, rig, pesos e clipes do leão.

## QA da sela nos 28 clipes oficiais

Medido com `build/s1/s1_03_qa_sela.py`, a cada 2 quadros:
- **Sela ↔ pele:** menor distância com sinal (negativa = a pele passa a sela), medida por paridade de raios.
- **Juba:** fios da juba dentro do volume da sela.

| Clipe | Pele passa a sela (pior, studs) | Cilha (aperto, de propósito) | Fios da juba dentro da sela |
|---|---|---|---|
| Alerta Ameaca | 0.00 | -0.05 | nenhum |
| Andar | -0.03 | -0.07 | nenhum |
| Andar para Repouso | -0.01 | -0.06 | nenhum |
| Andar para Trote | -0.04 | -0.06 | nenhum |
| Aproximacao Furtiva | -0.00 | -0.04 | nenhum |
| Arrancada | -0.13 | -0.08 | nenhum |
| Bote | -0.10 | -0.06 | nenhum |
| Corrida | -0.14 | -0.09 | nenhum |
| Corrida para Trote | -0.13 | -0.07 | nenhum |
| Esquiva D | -0.06 | -0.06 | nenhum |
| Esquiva E | -0.01 | -0.06 | nenhum |
| Fadiga Recuperacao | 0.00 | -0.05 | nenhum |
| Frenagem | -0.13 | -0.07 | nenhum |
| Intimidacao | 0.00 | -0.05 | nenhum |
| Mordida | -0.06 | -0.06 | nenhum |
| Observar Farejar | -0.02 | -0.05 | nenhum |
| Patada D | -0.00 | -0.06 | nenhum |
| Patada E | 0.00 | -0.05 | nenhum |
| Repouso Relaxado | 0.00 | -0.05 | nenhum |
| Repouso Vigilante | 0.00 | -0.05 | nenhum |
| Repouso para Andar | -0.07 | -0.06 | nenhum |
| Rosnado | 0.00 | -0.04 | nenhum |
| Rugido | -0.00 | -0.05 | nenhum |
| Trote | -0.03 | -0.06 | nenhum |
| Trote para Andar | -0.06 | -0.08 | nenhum |
| Trote para Corrida | -0.14 | -0.08 | nenhum |
| Virar D | -0.06 | -0.06 | nenhum |
| Virar E | -0.12 | -0.08 | nenhum |

- **Juba:** em nenhum clipe um fio chega a menos de 1 stud da sela.
- **Galope e Virar_E:** a pior entrada é de 0,10 a 0,14 stud, nas bordas da manta e no debrum, quando a coluna dobra. Nos renders desses quadros, com a câmera seguindo a raiz (`review/s1/pior/`), não aparece pele por cima da sela.
- **Cilha:** fica 0,04 a 0,09 apertada na barriga, de propósito.

## Evidência (`review/s1/`)

- `repouso/`: perfil D/E, 3/4 frente e trás, topo, frente, close do assento e da cilha, com e sem o manequim de **teste** sentado.
  - O manequim tem proporções aproximadas do R15 e vem do módulo do Crocodilo (só importado). Não é um rig R15 validado.
- `pior/`: os quadros com maior entrada (Arrancada q53, Trote_para_Corrida q33, Virar_E q47).
- `movimento/`: sela em Andar, Corrida e Bote, perfil e 3/4, em tempo real e lento.
- `qa_sela.json` e `sela_info.json`.

## Arquivos

- `Leao_Solar_Ref_S1_sela.blend`: leão com a sela e as 28 ações oficiais.
- Scripts:
  - `build/s1/s1_00_medir_dorso.py`: mede o dorso;
  - `build/s1/s1_01_sela_leao.py`: constrói a sela;
  - `build/s1/s1_02_render_sela.py`: renders;
  - `build/s1/s1_03_qa_sela.py`: QA nos clipes.

## Pendências

- **Revisão visual do usuário.**
- **Textura:** os materiais são procedurais. Faltam atlas e textura ≤ 1024.
- **Exportação:** falta o GLB da sela (MeshPart próprio).
- **S2:** Montar_E e Montar_D, com o leão agachando e o manequim subindo, e o teste sentado nos clipes reaproveitados (Repouso, Andar, Corrida).
- **Roblox:** nada foi testado.

## r3 (06/11): sela sem entrar no corpo nas animações

**Pedido do usuário:** "ajuste mais um pouco, para ficar certinho no corpo do leão, sem a sela entrar dentro do seu corpo nas animações".

**Método (`build/s1/s1_04_folga.py`):**
1. Em todos os quadros (passo 2) dos 28 clipes oficiais, mede quanto cada vértice da sela fica dentro da pele do leão (sem os fios da juba).
2. Afasta a sela só onde entra, com margem de 0,04 e suavizado:
   - **Peças do dorso:** sobem em Z por um campo de alturas, então a espessura não muda.
   - **Cilha:** se afasta na direção radial, por faixa de ângulo, e deixa de apertar a barriga.
3. Repete medir e afastar.

As argolas da cilha também se afastam 0,05 na direção radial (`s1_05_argolas.py`).

**Ciclos:**

| Ciclo | Vértices dentro | Pior entrada |
|---|---|---|
| 0 | 217 | 0,145 (manta, Trote_para_Corrida) |
| 1 | 15 | 0,077 |
| 2 | 6 | 0,054 |
| 3 | 3 | 0,027 |
| 4 | 2 | 0,018 |
| 5–6 | 1 | 0,010 (argola) |

Depois do ajuste das argolas, o QA completo (`s1_03_qa_sela.py`, 28 clipes, passo 2) deu:
- **pior entrada na pele: 0,003 stud**, no nível de arredondamento;
- **0** vértice-quadro acima de 0,05;
- nenhum fio da juba dentro da sela.

Pesos, materiais e peças não mudaram; a sela só se afastou do corpo, no máximo ~0,2 stud nas bordas da manta e ~0,3 radial na cilha.

**Arquivo:** `Leao_Solar_Ref_S1r3_sela.blend`. A versão anterior, `Leao_Solar_Ref_S1_sela.blend`, foi mantida.

## Conferência dos materiais com os documentos (06/11)

Os documentos só definem os **nomes e o status** dos materiais. Não descrevem cor nem textura, então o visual de cada material é interpretação minha, coerente com o que ele é.

| Material na sela | Status nos documentos | Visual usado |
|---|---|---|
| Couro das Planícies | [OFICIAL], material regional estrutural. A fonte (antílope, búfalo ou curtume) está [PENDENTE] | couro marrom quente |
| Âmbar Solar | [OFICIAL], material regional especial. O local de coleta está [PENDENTE] | resina laranja-dourada lisa, levemente translúcida, sem emissão |
| Pele de Antílope | proposta nas receitas; o animal tem a variante "Antílope Dourado" | pelo curto castanho-dourado |
| Tendão de Antílope | nome usado nas receitas aprovadas como base (ex.: Adagas de Caçador). "Tendão Elástico" era nome histórico; o texto foi corrigido | cordão bege |
| Chifre Leve | **[PROPOSTA]**: só aparece numa lista antiga, nenhuma receita usa | marfim claro |
| Ferro | [OFICIAL], material básico | ferro escuro |

## r4 (06/11): foco em Âmbar Solar e Couro das Planícies

**Pedido do usuário:** "Foque mais no âmbar solar e couro das planícies", os dois materiais regionais **oficiais** das Planícies.

Feito sobre a sela r3 sem reconstruir (`build/s1/s1_06_materiais_regionais.py`), então a folga medida foi mantida:

| Peça | r3 | r4 |
|---|---|---|
| Manta | Pele de Antílope | **Couro das Planícies**, tom claro com acabamento de camurça |
| Alça da mão | Chifre Leve ([PROPOSTA]) | **Couro das Planícies**: pegador de couro |
| Adorno solar da cabeça | Âmbar Solar | **Âmbar Solar 35% maior**, com guarnição de 8 raios de ferro |
| Patilha (traseira do assento) | — | **pedra nova de Âmbar Solar** em aro de ferro |
| Apoios de pé (dois lados) | — | **pedra nova de Âmbar Solar** no alto da alça de ferro |
| Argolas da cilha | ferro + Âmbar Solar | sem mudança |
| Costura e debrum | Tendão de Antílope | sem mudança (só costura) |

- **Materiais da r4:** Couro das Planícies (duas tonalidades), Âmbar Solar, Ferro e Tendão de Antílope na costura. A Pele de Antílope e o Chifre Leve saíram da sela.
- **Tamanho:** 6.780 triângulos e 3.468 vértices.
- **Pesos das pedras novas:** os do vértice mais próximo da sela (peças rígidas).

**Arquivo:** `Leao_Solar_Ref_S1r4_sela.blend`. A r3 foi mantida. Renders em `review/s1/r4/`.

**QA da r4** (`review/s1/r4/qa_sela_r4.json`, 28 clipes, passo 2):
- **Pior entrada na pele: 0,003 stud.** Nenhum vértice-quadro acima de 0,05, e nenhum fio da juba dentro da sela.
- **Primeira tentativa:** a pedra da patilha ficou na borda de baixo, colada na manta, e entrava 0,15 no galope. Subi a pedra para o alto da traseira da patilha.
- **Subida:** a cena da subida foi refeita com a r4 e deu os mesmos números da r3 (`S2-RELATORIO.md`).
