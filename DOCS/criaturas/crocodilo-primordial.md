# Crocodilo Primordial — ficha do subchat

Criatura **domesticável** do **Pântano Nebuloso**. Espécie-base **Crocodilo** (forma regional única: Crocodilo Primordial). A outra domesticável do bioma é o **Basilisco** (subchat próprio).

Fontes: `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO` (§0, §1, §2, Etapa 15.1, §10, §12, §13, §15, §18.2, §19.2) e `RPG_01` (só cita o Crocodilo no catálogo). A **ATUALIZAÇÃO OFICIAL de 30/10/2026** prevalece sobre o que vem depois no documento.

Regras de convivência: `DOCS/ORGANIZACAO-CHATS.md`. Studio um chat por vez (`DOCS/estado/studio-em-uso.md`).

Ficha criada em 03/11/2026, só com leitura. Nada foi alterado no Studio nem em `src/`.

## 1. Identidade

| Item | Valor | Status |
|---|---|---|
| Bioma / habitat | Pântano Nebuloso; margens, lagos e canais | [OFICIAL] |
| Anatomia | Crocodiliano **quadrúpede gigantesco**, corpo baixo, escamas grossas, cauda musculosa | [OFICIAL] |
| Locomoção | **Anfíbio**: caminha em terra normalmente e se desloca na água | [OFICIAL] |
| Especialidade | **Agarrões, emboscadas aquáticas (submersas) e combate próximo** | [OFICIAL] |
| Porte adulto | **5–7 studs até os ombros**; **~24–32 studs de comprimento total** (inclui cauda). Não confundir as duas medidas | [OFICIAL] |
| Estágios | Ovo, Bebê, Jovem, Pré-adulto, Adulto, Ancião (regra geral) | [OFICIAL] |
| Tamanho por estágio | — | [PENDENTE] |
| Montaria | A partir do **Adulto**, sela para locomoção em **terra E água** (ambas aprovadas na Etapa 15.1) | [OFICIAL] |
| Mergulho com cavaleiro | **Não definido** — nem aprovado nem proibido. Faltam respiração, câmera, profundidade, oxigênio/segurança e interações; diferenciar de Serpente/Leviatã (que têm mergulho montado aprovado) | [PENDENTE] |
| Velocidade relativa terra × água | — | [PENDENTE] |
| Padrões visuais | **Verde Pantanal**, **Marrom Aluvial**, **Negro de Rio**. Só cosméticos: não definem elemento nem raridade | [OFICIAL] |
| Cores exatas, evolução estética por estágio, adornos por raridade | — | [PENDENTE] |
| Pistas de aproximação | Lentidão em terra seca; trilhas de bolhas e ondulações que revelam a aproximação | [PROPOSTA] |
| Painel de referência | `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/03-basilisco-crocodilo-escorpiao-lagarto.png` | referência visual |

Papel ecológico em relação aos vizinhos:
- **[OFICIAL]** Leviatã = ofensiva oceânica; Serpente Marinha = perseguição/constrição aquática; **Crocodilo = emboscada de margens e rios** (agarrões, emboscada anfíbia, com patas).
- **[PROPOSTA]** Basilisco domina terra/água rasa; Crocodilo tende a dominar canais e água mais profunda. Precisa de margem e cobertura; fraco contra alvos aéreos; pouca perseguição prolongada em terra seca e aberta.

## 2. Elemento e habilidades

### Elemento
- **[OFICIAL — 30/10/2026]** Cada criatura tem **um único elemento natural**. Não há 2º/3º elemento, alternância nem fusão elemental no sistema atual.
- **[PENDENTE]** O elemento único do Crocodilo Primordial **ainda não foi escolhido**.
  - A lista da Etapa 15.1 "Água, Terra, Natureza" (nasce com uma e desbloqueia até mais duas) é histórico superado. Não presumir nenhuma das três.

### Habilidades
- **[OFICIAL — 30/10/2026]** Cada criatura tem no mínimo **1 passiva + 3 ativas**; nomes, efeitos e quantidades são aprovados criatura por criatura. Ataques básicos físicos não ocupam slots.
- **Lista da Etapa 15.1** (era OFICIAL; após 30/10 vale como referência anterior; a lista final está **[PENDENTE]**):
  1. **Mordida de Agarrão** — mordida que agarra. PvE: agarrões prolongados. PvP: ver conflito abaixo. [PROPOSTA] dano inicial, sinais de antecipação, esquiva por ângulo/distância.
  2. **Giro Predatório** — rotação de corpo e cauda, especialmente eficaz na água. [PROPOSTA] redemoinho local que desloca inimigos.
  3. **Submersão** — [OFICIAL] mergulho e aproximação furtiva na água; **fora da água vira postura de camuflagem em lama e vegetação, não desaparecimento mágico total**. [PROPOSTA] bolhas/ondulações/folhas mexidas denunciam.
  4. **Cauda de Maré** — golpe poderoso de cauda que desloca inimigos; aproveita a água para gerar ondas locais. [PROPOSTA] em solo seco, varredura lateral.
- **Passiva:** nenhuma definida. **[PENDENTE]**
- **[PROPOSTA — histórico, superada]** Transformações por afinidade (Água/Terra/Natureza) e as seis fusões direcionais (Corrente de Cipós, Manguezal Vivo, Couraça Enraizada, Armadilha das Margens etc.) contrariam a regra de elemento único. Não implementar.

### ⚠️ Conflito no documento: agarrão contra jogadores (PvP)
O próprio RPG_02 se contradiz. **Perguntar ao usuário antes de qualquer combate PvP.**
- **Versão A — "PvP só empurra":** ficha da Etapa 15.1, catálogo §2, tabela de habilidades, comparação ecológica, tabela de balanceamento, tabela §10 e o texto "a decisão 7 foi opção C, não A". Diz: agarrões prolongados só no PvE; no PvP, efeitos de agarrão viram **empurrões, sem prender nem arrastar, mesmo com interrupção por aliados**.
- **Versão B — "agarrão PvP mais longo, interrompível por aliados":** §12 (correção de consistência), §13 item 2 e §18.2. Diz que "só empurra" **foi um erro de auditoria** e que a escolha do usuário na Etapa 15.1 foi agarrão PvP mais longo, porém interrompível por aliados.
- Em ambas: **PvE pode ter agarrão prolongado**; durações, resistência a controle repetido e contrajogo estão **[PENDENTE]**. A regra global (§18.2) exige resistência a controle repetido e interrupção por aliados.

## 3. Atributos (Etapa 24)
- **[OFICIAL — 24.1]** 6 atributos: Vida, Defesa, Força, Velocidade, Energia, Poder Elemental. Comparação entre Adultos nível 100. Velocidade e manobra analisadas separadamente em terra, água e ar. Vantagem ambiental ~10–15%; raridade 1–5%.
- **[PROPOSTA — 24.2, NÃO APROVADA]** Números do Crocodilo Primordial:
  - escala 1–5: Vida 4, Defesa 4, Força 4, Velocidade 5 (no meio favorável), Energia 3, Poder Elemental 3;
  - valores absolutos: 5.350 HP, Defesa 160, Força 190, Energia 120, Poder Elemental 120;
  - velocidade: terra 16 studs/s (manobra 1), água 43 studs/s (manobra 5), sem voo.
- **[SIMULAÇÃO ILUSTRATIVA, NÃO OFICIAL]** §19.2: duelo Crocodilo Primordial × Basilisco ≈ 111,5 s.

## 4. Mundo e habitat (segundo os registros do mapa)
- `DOCS/estado/mundo-pantano.md` (M3/M3b, 22/10): marcadores em `Pantano_Nebuloso/Habitats/Crocodilo_Primordial` (V2, **sem IA**):
  - 11 Territórios (um por sistema de água funda ≥8, com área, profundidade máx., raio e população sugerida);
  - 7 Tocas_Submersas (poços-toca de 28–54 de profundidade, `M.POCOS` do `PantanoGen`);
  - 10 Corredores (197 pontos ao longo dos canais fundos);
  - 8 Emboscadas_Travessia (água funda junto de cada travessia);
  - 14 Descanso_Margem (margem seca, >30 da trilha);
  - 4 LocalNinhoElegivel **inativos** (>60 da trilha).
  - Versão antiga em `Retirados_Pantano`. M3d baixou 216 marcadores aquáticos para dentro da água.
- Hidrografia: canais 16–38 de profundidade, prateleira rasa nas bordas (emboscada), Lago Profundo até ~50.
- **[OFICIAL]** Ninhos reaparecem em 30–60 min; quantidade por jogador é [PROPOSTA].
- **Conferir no Studio** se os marcadores continuam lá antes de usar (não conferido nesta sessão).

## 5. O que já existe

### Roblox Studio (segundo os registros; não conferido nesta sessão)
- `ServerStorage.Biblioteca_Criaturas.Catalogo` registra a forma (medidas, elementos históricos, locomoção, montaria, 4 habilidades) — `DOCS/estado/criaturas-gerais.md`, 26/10.
- **Nenhum modelo do Crocodilo foi importado nem testado no Studio.**
- Atenção: o PILOTO de 27/10 registrou um place antigo aberto (PlaceVersion 394) sem `Biblioteca_Criaturas`. Conferir qual place está aberto antes de qualquer trabalho.

### Blender
Três gerações, nenhuma aprovada artisticamente pelo criador:
1. **C1 (26/10)** — `BLENDER/Criaturas/Crocodilo_Primordial.blend/.glb/.fbx` + `_Cor_Verde_Pantanal`, `_Cor_Marrom_Aluvial`, `_Cor_Negro_de_Rio`, `_Normal` (.png). 23 ossos, 8.520 tris, 6,2 de ombro e 25,7 de comprimento (dentro do oficial). 11 animações: Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar, Natacao + MordidaDeAgarrao, GiroPredatorio, Submersao, CaudaDeMare. Script: `BLENDER/Criaturas/scripts/repteis_crocodilo_basilisco_lagarto.py`.
2. **V2 refinada (27/10)** — `BLENDER/Criaturas/Blockouts/Crocodilo_Primordial/` (`_blockout`, `_refinado`, `_final` .blend) e `_Export/Crocodilo_Primordial.glb`. Script `build/build_Crocodilo_Primordial.py` (+ `esqueletos.py`, `pipeline_final.py`). 24 ossos, 31 animações, 28.718 tris. Crânio largo e plano, mandíbula pesada com dentes, olhos/narinas no topo, osteodermos em escudos, crista dupla na cauda, patas com cotovelo para fora. Medida do blockout: ombro ~5,8, comprimento 30,6.
   - Auditoria numérica `AUDITORIA-ANIMACOES-V2.csv`: 30 aprovadas, 1 "pequenos ajustes" (**GuardarNinho**). Inclui locomoção, Arrancada/Frenagem, ReacaoGolpe, AtaqueBasico, Morte, Comer, Descanso (3), Montar/Desmontar, Montado* (5), Alerta, Ameaca, **NadoCruzeiro, Mergulho, Emersao** e as 4 habilidades.
3. **V5 (27/10)** — `_refinado_v5.blend`, `_final_v5.blend`, `_Export/Crocodilo_Primordial_v5.glb` (5,0 MB). Revestimento de placas (`build/revest.py`), osteodermos maiores. 56.198 tris (maior malha 15.998), 24 ossos, animações 30/1/0. **Falta cavidade da boca, dentes e língua** para rugido/ameaça. Anatomia ainda é a silhueta V2.
- Renders `review/Crocodilo_Primordial/` são citados no relatório V5, mas **não foram encontrados** no repositório.

### Código (`src/`)
- Nada específico do Crocodilo: sem IA, combate, montaria, nado nem sons. A IA, os sons e a montaria existentes são dos dragões e são arquivos compartilhados (`Cerebro`, `EstadosDragao`, `ConfigCombate`, `SonsConfig`…).

### Modelo adulto fiel à referência (03/11/2026, aguardando aprovação visual)
- Referência escolhida pelo usuário: `REFERENCIAS/pantano-nebuloso/crocodilo-primordial/crocodilo-primordial-referencia-principal.png` (cópia sem alteração, SHA-256 `dc5df015…888f`).
- Pasta própria: `BLENDER/Criaturas/Crocodilo_Primordial_Ref/` (`asset-brief.md`, `scripts/`, `review/`, `meshy/`). Nada anterior foi alterado.
- **Base A — procedural** (`scripts/criar_crocodilo.py` → `CR_Crocodilo_Ref.blend`): seções elípticas + voxel, boca cortada (fenda, cavidade, garganta), dentes/gengivas/língua/olhos/cristas/garras. 8 rodadas (R1–R8). 30,2 de comprimento, ombro 6,63. Corpo ~500 mil tris (alta). Fica longe da referência no rosto e na pele.
- **Base B — Meshy 7.1 image-to-3D** (`scripts/meshy_img3d.py`, 1 tarefa, **30 créditos**; `normalizar_meshy.py` → `CR_Crocodilo_Meshy.blend`): muito mais fiel no rosto, olho, dentes, cristas e escamas. Boca aberta como a referência, com palato, língua e gengivas.
  - Escala: com 29,5 de comprimento, ombro da pele ≈ 4,7–4,9, **abaixo do mínimo oficial de 5**. Com 32 (máximo oficial), ombro ≈ 5,1. Corpo mais esguio que a referência.
  - Defeitos: textura rosada na parte de baixo da mandíbula; ventre e mandíbula mais claros (creme) que o ocre da referência; garras fundidas aos dedos; 692 mil tris; malha dividida por costuras de UV (432 ilhas).
- Prancha: `review/PRANCHA_comparativa_A_procedural_x_B_meshy.png`.
- Não testado no Roblox nem no celular.

**03/11/2026 (tarde) — usuário escolheu a base B (Meshy).** Feito (só Blender, sem Studio):
- Escala oficial: comprimento **32,0** (máximo da faixa), ombro da pele ≈ **5,3–5,5** (5,73 com cristas), largura 10,1. `CR_Crocodilo_Meshy_v2.blend` (o v1 com 29,5 foi preservado).
- Cor: máscara por geometria na HIGH — ventre/flanco baixo creme → ocre terroso; faixa rosada sob a mandíbula removida; saturação +15%, valor −7%. Dentes, garras e boca fora da máscara.
- LOW: `CR_Crocodilo_LOW.blend` — **19.000 tris / 9.487 verts, 1 malha, 1 material** (cabe num MeshPart ≤ 20k). Costuras soldadas antes do Decimate, UV nova. Bake HIGH→LOW: cor, normal (tangente), rugosidade em `tex/` 2048 (mestre) e 1024 (Roblox). Memória estimada a 1024: ~4 MB por mapa sem compressão (~12 MB os 3, +⅓ com mipmaps); comprimido na GPU ~0,7–1,3 MB por mapa.
- Rig de TESTE (`CR_Crocodilo_LOW_rigteste.blend`, 27 ossos: Raiz, Pelve, Coluna, Pescoco, Pescoco2, Cabeca, Mandibula, Cauda1–8, 4 patas × 3): pesos heat + mandíbula por disputa geodésica crânio×queixo. Dobradiça medida y −10,26 / z 3,92; boca do Meshy aberta ~14°.
  - Cauda: flexão lateral e vertical limpas.
  - Mandíbula: fecha bem até **80%**; a 100% os dentes de baixo atravessam o focinho (o Meshy não tem encaixes). Aberta +14°: faixa esticada e um dente de cima puxado no canto da boca → corrigir com pesos manuais no rig final.
- Prancha: `review/m3/prancha_m3.png` (cor/escala) e `review/rig4/PRANCHA_rig_teste.png` (rig).
- Diferenças que continuam frente à referência: corpo mais esguio e baixo (patas mais curtas); ventre ainda um pouco mais claro; garras fundidas aos dedos; cristas na região do ombro vão atrapalhar a sela.
- [PROPOSTA] LOD: deixar `RenderFidelity` automático do Roblox ou exportar LOD1 ~8k e LOD2 ~3k para distância.

**03/11/2026 (noite) — visual aprovado pelo usuário ("Aprovo, seguir"): rig final, 6 clipes e GLB (só Blender).**
- `scripts/rig_final.py` → `CR_Crocodilo_Rig.blend`: 28 ossos com nomes do jogo (Raiz, Pelve, Coluna1–2, Pescoco, Pescoco2, Cabeca, Mandibula, Cauda1–8, BracoE/D, AntebracoE/D, MaoE/D, CoxaE/D, CanelaE/D, PeE/D). Articulações de cada pata medidas na própria malha. As traseiras do Meshy estão desencontradas (pose de passo da referência); **a malha não foi reposicionada** (lição do Silverwing).
  - Pesos: heat + mandíbula por disputa geodésica crânio×queixo com linha lateral do lábio + voto de maioria; suavização só atrás do canto; ≤ 4 influências.
  - IK de 2 ossos por pata só para animar (polo por busca numérica, desvio no repouso 0,0003); os clipes são gravados em FK.
- `scripts/anim_crocodilo.py` → `CR_Crocodilo_Anim.blend` + `clipes/Crocodilo_<Clipe>.json` (mesmo formato dos dragões para `montar_kfs_json.luau`) + `clipes/manifesto_clipes.json`:
  - Repouso (4 s, laço; boca 80% fechada, respiração, cauda lenta); Andar (1,5 s, laço, pares diagonais, **1,85 studs/s**); Corrida (16 quadros, laço, **8,75 studs/s**); Nado (2 s, laço, patas recolhidas, cauda em onda); Mordida (1 s, antecipação → bote → recuperação); Ameaça (2 s, corpo e cabeça erguidos, boca aberta com tremor).
  - QA numérico: erro de IK ≤ 0,005; escorregão do pé apoiado ≤ 0,06 studs/s (corrida) e 0 (andar); ponta do pé no chão.
  - A traseira direita tem a base 0,6 stud para dentro em todos os clipes (no Meshy está aberta e quase esticada).
  - Limites da boca: fecha no máximo **80%** (a 100% os dentes de baixo atravessam o focinho); abre no máximo **+4°** além da boca do Meshy (~14°, a abertura da referência). Mais que isso estica dentes.
- `scripts/exportar_croc.py` → `export/CR_Crocodilo_Primordial.glb` (7,0 MB): 1 malha 19.000 tris, 28 ossos (todos com peso), texturas 1024, sem animação. Reimportado no Blender: 1 malha, 28 juntas, 4 influências, 32,0 × 10,1 × 5,7.
- Pranchas: `review/clipes4/PRANCHA_boca_v3.png` (estado atual da boca), `review/clipes2/PRANCHA_patas.png`, `review/clipes2/PRANCHA_topo.png`, GIFs em `review/clipes2/`.
- **Defeitos conhecidos:** 1 dente grande de cima ainda estica como fio quando a boca abre além do repouso; uma pontinha de dente fica sob o queixo no estalo da Mordida. A tentativa automática de corrigir contatos dente-arcada piorou (jogava a ponta do focinho na mandíbula) e ficou desligada (`CONTATOS = False`). Correção dirigida por vértice pendente.
- **Não testado no Roblox/celular.** Importação do GLB (Import 3D) é passo manual; KeyframeSequence só toca no Studio; publicar animações exige a conta do usuário. Unidade: 1 unidade Blender = 1 stud (conferir escala na importação).

**03/11/2026 — correção do dente (pedido do usuário "Sim, corrigir dente").** Diagnóstico com `scripts/diag_esticadas.py` (arestas que esticam com a mandíbula girada):
- Causa: entre palato e assoalho, por dentro dos dentes, o Meshy fez uma parede contínua (bochecha interna) que liga as arcadas; e os caninos esquerdos de cima e de baixo se tocam ponta com ponta.
- Correções em `rig_final.py`: (1) membrana interna com peso em degradê do assoalho ao palato; (2) suavização local (bola de 0,3) onde ainda esticava; (3) canino de baixo esquerdo todo com a mandíbula e **encurtado para 55%** a partir da base (a ponta para dentro do canino de cima ao fechar); a ponta do canino de cima volta para o crânio.
- Em `anim_crocodilo.py`: fecha no máximo **65%** (a boca descansa entreaberta, como crocodilos reais) e **não abre além da boca do Meshy** (`ABRE_MAX = 0`, que é a abertura da referência).
- Testado e descartado: trocar dono por contato (cascata, focinho ia para a mandíbula); bolas inteiras para um lado (até 7,7×); inclinar o canino para fora (fica enterrado na lateral do focinho).
- Resultado: na abertura máxima dos clipes nenhuma aresta estica (1,00×); fechada 65%, máximo 1,8× em arestas minúsculas. Prancha: `review/clipes9/PRANCHA_boca_corrigida.png`. GLB reexportado (19.000 tris, 28 ossos).
- Diferença visível frente ao Meshy: canino de baixo esquerdo mais curto, ligado ao de cima por uma ponte fina na boca aberta.
- **Superado pelo Lote 1** (abaixo): os limites 65%/0° escondiam o defeito.

**03/11/2026 — Lote 1 do complemento (boca funcional + revisão dos 6 clipes). Aguardando aprovação.**
- Baseline preservado: `baseline_L0/` (rig, anim, JSON, GLB e scripts anteriores).
- Diagnóstico: `scripts/cortes_boca.py` → `review/cortes_L0.png`. Na frente as arcadas já eram cascas separadas, ligadas só por pontas de dente; de y −12,75 até o canto (−10,8), colunas de tecido do Meshy ligam as arcadas por dentro.
- Correção na origem (`scripts/rig_final_v2.py` → `CR_Crocodilo_Rig.blend`): rasgo da malha entre faces de donos diferentes na frente (contatos de dente) e no meio das colunas internas do canto; furinhos tampados com UV do vizinho e normais refeitas; degradê só no canto anatômico. Removidos os remendos da v1 (membrana, bolas, canino encurtado). Malha: 19.012 tris (12 de tampas), 1 malha, 1 material, texturas 1024.
- Resultado: **fecha 100%** com os dentes de cima por fora, sem furar o focinho; **abre +12°** além da boca do Meshy sem fios. Prancha antes/depois: `review/L1_boca/ANTES_DEPOIS_boca.png` (fechada/meia/repouso/aberta × esquerda/direita/frente).
- Clipes (`scripts/anim_crocodilo.py`): boca 100%/+12°; pé dobra na saída/pouso sem entrar no chão; Repouso com cauda mais calma; Nado com patas encostadas apontando para trás e cabeça estabilizada.
- Exportador: o osso Raiz recebe só 2% num vértice (antes 100% → puxão).
- Evidências: `review/L1_clipes/` (FOLHA_* e GIFs de 3 ciclos; Mordida e Ameaça também em câmera lenta). Chão quadriculado de 1 stud com deslocamento na velocidade do clipe; água de teste no Nado (não é física).
- QA (`scripts/qa_clipes_json.py`): 28 ossos iguais no JSON e no GLB reimportado, erro de norma ≤ 0,000007, laços sem salto exceto a Corrida (último→primeiro quadro da mão 26° contra passo máximo de 17°, ciclo de 16 quadros).
- Pendências: 2–3 lasquinhas minúsculas e franjas finas no fundo da boca só visíveis bem aberta; dedos não são ossos (pé é bloco único); Roblox/celular/física não testados.
- Inventário completo e especificação dos poderes: `DOCS/criaturas/crocodilo-primordial-animacoes.md`.

**03/11/2026 — correções finais do Lote 1 (versão L1b). Aguardando aprovação; Lote 2 não iniciado.**
- Versão do Lote 1 preservada em `versao_L1/` (além de `baseline_L0/`).
- **Corrida:** diagnóstico com `scripts/diag_ciclo.py` (posição e rotação no mundo, quadro a quadro, incluindo o retorno último→primeiro). O salto vinha do IK: o pouso da dianteira caía no ponto mais à frente com a pata quase esticada, e o antebraço girava 26,7° num quadro. Correção: passo das dianteiras centrado 0,3 stud mais para trás (sob o ombro), mesma passada (2,1), mesma duração (16 quadros) e mesma velocidade de sincronização (8,75 studs/s). Retorno agora abaixo do maior passo interno em todos os ossos (antebraço esquerdo 12,9° contra 15,6°; braço 9,9° contra 15,0°); no JSON a mão passou de +8,98° para −4,06°; escorregão do pé 0. Tabelas por osso dos seis clipes: `review/diag_ciclo_<Clipe>.txt`.
- **Boca:** causas achadas com `scripts/diag_bordas.py` e `scripts/pixel_face.py` (raio da câmera até a face):
  - lasca escura = uma tampa de 8 lados (face 19000) atravessando a ponta do canino de cima esquerdo;
  - franjas = 4 laços abertos deixados pelo rasgo das colunas do canto.
  - Correção em `rig_final_v2.py`: rasgo da frente separa também os vértices das pontas; os furos da frente são fechados juntando a borda num ponto; as faces mistas das colunas do canto saem e todo laço aberto do canto recebe um leque com UV de tecido do palato. O dono (crânio/mandíbula) passou a viajar numa camada da malha, porque juntar vértices renumera índices.
  - Testados e descartados: encolher os toquinhos (textura em listras), tampa com UV do vizinho (atravessa ilhas da UV).
- Mantido: fecha 100% e abre +12°. Malha final 18.993 tris, 28 ossos, 1 material, texturas 1024; bordas abertas na cabeça: 2 arestas na ponta de um canino.
- Evidências: `review/L1b/` — `boca/GRADE_L1_antes.png` × `boca/GRADE_L1b_depois.png`; `clipes/` (folhas e GIFs de 3 ciclos; Corrida, Mordida e Ameaça também em câmera lenta); `glb/GRADE_glb_json.png` (GLB reimportado + quadros dos JSON); `PRANCHA_ref_x_L1b.png`.
- GLB reimportado: 28 ossos, raiz "Raiz", 1 material, 28 grupos, modificador Armature; poses dos JSON reproduzidas. **Roblox, celular e física continuam sem teste.**

**03/11/2026 — Lote 2 (locomoção, transições e água). Aguardando aprovação; Lote 3 não iniciado.**
- Versão L1b preservada em `versao_L1b/`. Rig e GLB **não mudaram** (só animação): `export/CR_Crocodilo_Primordial.glb` continua válido; 21 JSON em `clipes/`, todos com os 28 ossos do GLB.
- 15 clipes novos em `scripts/anim_crocodilo.py`: VirarEsquerda/Direita (laço), Arrancada, Frenagem, RepousoParaAndar, AndarParaRepouso, AndarParaCorrida, CorridaParaAndar, NadoParado (laço), CurvaAquaticaEsquerda/Direita (laço), Mergulho, Emersao, EntradaAgua, SaidaAgua. Nado = NadoCruzeiro (sem duplicata). NadoRapido não feito (proposta).
- Técnica: planejador de passos (pé fixo no mundo, pouso meio passo à frente do neutro, levanta ao chegar ao limite de alcance de cada pata, passos de acomodação ao parar, estado inicial igual ao do laço de origem); viradas com o pé apoiado girando em torno do pivô; na água os alvos dos pés acompanham o corpo.
- QA: IK ≤ 0,04 e escorregão no mundo ≤ 0,06 studs/s em todos; laços fecham sem salto; tabelas em `review/qa_json_L2.txt` e `review/diag_ciclo_<Clipe>.txt`; emendas em `clipes/emendas_transicoes.json`.
- Evidências: `review/L2/clipes/` (22 folhas, 36 GIFs) e resumos `review/L2/RESUMO_terra.png`, `RESUMO_agua.png`.
- Limitações: na entrada/saída da água não há margem nem água no render de teste (o corpo aparece afundando no chão); a profundidade do mergulho é do jogo; velocidades/giros são sincronização técnica; curvas aquáticas com giro só proposto (25°/s).

**03/11/2026 — pendências do Lote 2 (versão L2b). Lote 2 aguardando avaliação; Lote 3 não iniciado.**
- Versão L2 preservada em `versao_L2/`. Rig e GLB **não mudaram**. Só 4 JSON mudaram (EntradaAgua, SaidaAgua, VirarDireita, VirarEsquerda); os outros 17 estão idênticos à L2.
- **VirarDireita, divergência:** o "0,002/0,06" do relatório L2 vinha de uma rodada parcial anterior; o manifesto (0,0058/0,175) era o real. Medido de novo (`scripts/qa_pe_mundo.py`): osso MaoE 0,175 studs/s no fim do apoio e sola 0,473; a VirarEsquerda também escorregava na sola (0,263) porque o pé não contra-girava. Correção na origem: o pé apoiado gira junto com o corpo (guinada = ângulo de apoio) e as dianteiras ficam 0,25 para dentro. Agora IK 0, osso 0, sola 0,135 (D) e 0,119 (E), resíduo da deformação da pele do tornozelo; laço fecha com excedente ≤ 0,01°.
- **EntradaAgua/SaidaAgua:** cena de teste `scripts/cena_agua.py` (margem 10°, fundo submerso, plano de água; **água só visual, não é física do Roblox**). Problemas achados e corrigidos: a entrada desacelerava até 0 e nivelava o corpo em cima da rampa (rabo/quadril penetrando até 4,7); havia um salto oculto da Raiz (−0,35) e arfagens internas que brigavam com a inclinação do terreno. Agora a entrada mantém a passada, a inclinação vem do terreno (jogo) e a profundidade também. Penetração máxima nas sequências Andar→EntradaAgua→Nado, Nado→SaidaAgua→Andar e terra: 0,18 (garras).
- Emendas: EntradaAgua começo×Andar 1,4°, fim×Nado 10,1°; SaidaAgua começo×Nado 6,5°, fim×Andar 13,3° (crossfade no jogo).
- Evidências: `review/L2b/` — `seq/` (folhas e GIFs lado/3-4, normal e lento, `medidas_*.json`), `virar/` (topo e patas, 3 ciclos), `virar_antes/`, `COMPARA_VirarDireita_antes_depois.png`, `RESUMO_L2b.png`; QA em `review/qa_json_L2b.txt`.
- Pendências achadas (fora do escopo): Mergulho termina e Emersao começa com a Raiz em −0,35 (salto de 0,35 se emendar com o Nado; proposta: profundidade pelo jogo); sola do Andar 0,19 e da Corrida 1,0 studs/s no fim do apoio (osso em 0). Roblox, celular e física sem teste.
- **Lote 2 (com L2b) aprovado pelo usuário em 03/11/2026** ("Aprovo, Lote 3").

**03/11/2026 — Lote 3 (reações e vida). Aguardando aprovação; Lote 4 não iniciado.**
- Versão L2b preservada em `versao_L2b/`. Rig e GLB **não mudaram**; 29 JSON em `clipes/` (28 ossos, iguais ao GLB); os 21 anteriores estão idênticos à L2b.
- 8 clipes novos: ReacaoGolpe (0,8 s), Morte/incapacitação visual (2,4 s, fica no último quadro), Comer (3,0 s), Deitar (2,0 s), DescansoDeitado (6,0 s, laço), Levantar (1,8 s), Observar (4,0 s), Alerta (2,5 s). GuardarNinho continua proposta.
- Técnica: patas plantadas (IK 0, pé não escorrega); Deitar desce a frente primeiro e depois o quadril, abre as dianteiras 0,35 com um passo curto (o cotovelo D entrava 0,05 no chão) e pousa o queixo; Levantar faz o inverso e devolve as patas sob o ombro. Transições saem/chegam no quadro 0 do Repouso (emenda 0,4°) e do DescansoDeitado (0,5°). Eventos visuais no bloco `sincronizacao` (ex.: Comer abocanha 0,62 s, engole 1,25 s).
- Correção achada no render: a Mandibula é filha do Pescoco2 (não da Cabeca); girar só a Cabeca cruzava os dentes. Nos clipes do Lote 3 a mandíbula gira junto (`soma_cab`); clipes anteriores não foram mexidos.
- QA de contato com o chão (malha deformada, `scripts/qa_malha_chao.py`, z = 0): corpo ≥ 0,04, cauda ≥ 0,13, cabeça/focinho ≥ −0,003 (queixo apoiado), pernas ≥ 0,009. Pés: −0,21 a −0,23 na ponta da traseira D, **igual ao Repouso aprovado (−0,21) e ao Andar (−0,27)** — pendência antiga da malha, não do Lote 3.
- Evidências: `review/L3/` — `clipes/` (folhas e GIFs lado/3-4 normal e lento; cabeça para ReacaoGolpe, Comer, Observar, Alerta, Morte; patas para Deitar/Levantar/Descanso, 3 ciclos), `PRANCHA_ref_x_L3.png`, `qa_chao_L3.txt/.json`, `qa_transicoes_L3.txt`, `qa_json_L3.txt`, `geracao_L3.txt`.
- Limites: Morte é só visual (sem regra de morte, ragdoll ou física); ReacaoGolpe só de frente; Alerta não tem laço (proposta); Roblox, celular e FPS sem teste.

**04/11/2026 — Lote 4 (montaria, só apresentação no Blender). Aprovado pelo usuário em 04/11/2026 ("Aprovar Lote 4").**
- A aprovação vale para a apresentação no Blender. Sela, lado de montar, mergulho montado e a integração no Roblox continuam pendentes.
- Versão L3 preservada em `versao_L3/` (Anim.blend, clipes, scripts, md5 do GLB/rig). Rig e GLB **não mudaram**; agora 31 JSON (28 ossos, iguais ao GLB); os 29 anteriores estão idênticos.
- Encaixe (`scripts/encaixe_l4.py`, `scripts/manequim_r15.py`): manequim de teste com proporções aproximadas do R15 em bloco (altura 5,2, quadril 2,0) — **não é rig R15 validado**. O dorso fica a ~5,5 studs (acima da cabeça do manequim em pé). As cristas grandes do ombro ficam em y −7 a −9; o assento foi posto em y −4,6 (perto do pivô de giro, y −4,2), atrás delas, e o volume `TESTE_Sela_PROPOSTA` (2,4 × 2,3, 0,22 de espessura, preso ao osso Coluna1) cobre as cristas menores do dorso. Sem a sela o manequim apoia direto nas pontas das cristas. Nada da criatura foi reduzido ou deformado.
- Montar (4,0 s) e Desmontar (3,6 s): clipes do crocodilo (baixa 0,20 com patas plantadas, IK 0; rola 1,5° para o lado do apoio; cabeça acompanha; amortece ao sentar). Cavaleiro de demonstração: chega pela esquerda, mãos espalmadas no flanco, pé E no cotovelo, pé D atrás do cotovelo, mãos na borda do dorso, perna D passa por cima da garupa e senta; Desmontar faz outro caminho (perna D volta pela garupa, desce de frente para o flanco segurando a borda e solta perto do chão). Emenda com o Repouso 0,4°; maior passo do quadril na sequência inteira 0,23 stud por quadro (sem teleporte).
- Folgas medidas (caixa do manequim × pele, negativa = entra): corpo e membros ≥ −0,18 em 5 de 121 quadros (Montar) e ≥ −0,15 em 4 de 109 quadros (Desmontar); mãos/pés de apoio até −0,26 em quadros de troca de apoio. Sentado: −0,06 (canela no dorso) e −0,13 no volume da sela. Reutilização: Repouso, Andar, Corrida, VirarE/D, NadoParado, Nado, CurvaAquáticaE/D em 3 ciclos com o cavaleiro preso ao osso — deriva 0, nenhuma parte abaixo de −0,07 da pele; nenhuma variante Montado* foi necessária.
- Água de teste (só superfície): no nado o quadril fica 2,1 acima da linha d'água e a base do tronco 2,5; na entrada pela margem o tronco fica ≥ 1,57 e o pé toca a água (−0,02); na saída o tronco fica ≥ 1,97. **Não é teste de respiração, flutuação nem física do Roblox.** Mergulho/Emersão montados não foram feitos.
- Evidências: `review/L4/` — `PRANCHA_ref_x_L3_x_L4.png`, `PRANCHA_encaixe_L4.png`, `encaixe/`, `demo/` (Montar/Desmontar em lado, 3/4, frente, topo, subida e flanco; GIF normal e lento), `seq/` (Repouso → Montar → montado → Desmontar → Repouso), `reuso/` (GIFs de 3 ciclos), `agua/` (entrada/saída), `RESUMO_L4.txt`, `qa_demo_L4.json`, `qa_transicoes_L4.txt`, `qa_json_L4.txt`, `qa_chao_L4.txt`. Cena: `CR_Crocodilo_Montaria_Teste.blend`.
- Limites: manequim em caixas de 1 stud (membros R15 reais são mais finos, e a animação final do personagem será outra); sela e lado de montar não são definição; sem controles, câmera, física, autoridade do servidor, regra de queda em combate; Roblox, celular e FPS sem teste. Herdados e não corrigidos: ponta do pé traseiro D −0,21 (Repouso), cotovelo D a −0,005 do chão na pose baixa, resíduos de sola e da Raiz na emenda Mergulho/Emersao↔Nado (L2b), reação a golpe só frontal.

**04/11/2026 — correção: dentes rangendo/colidindo com o crocodilo em movimento (pedido do usuário).**
- **Correção aprovada pelo usuário em 04/11/2026** ("Aprovar correção"). Lote 4 (montaria) aprovado em seguida, no mesmo dia.
- Causa: a Mandibula é filha do Pescoco2, não da Cabeca. Em todos os clipes a cabeça girava (até 2° no Repouso, 7,3° nas viradas) e a mandíbula ficava para trás: os dentes raspavam de lado (até 7,3°, VirarE/D), o queixo deslizava até 0,65 stud em relação à cabeça e Arrancada, Mergulho e Mordida fechavam até 5° além do fechado (arcadas cruzando). O ajuste do Lote 3 (`soma_cab`) só cobria parte dos clipes novos.
- Correção em `scripts/anim_crocodilo.py` (`mandibula_segue_cabeca`): na amostragem de cada quadro a mandíbula recebe o mesmo giro da cabeça em torno do pivô da cabeça (mordida rígida); abrir/fechar vale em relação à cabeça e nunca passa do fechado aprovado (100%). Rig, malha e GLB **não mudaram**.
- Medição (`scripts/qa_boca_relativa.py`, `review/boca_mov/qa_boca_antes.txt` × `qa_boca_depois.txt`): nos 31 clipes o desvio lateral caiu para ≤ 0,07° (resíduo da pose de descanso), o deslizamento do queixo para 0,000 e nenhum clipe fecha além do fechado.
- Regressão: nos 31 JSON só o canal da Mandibula mudou (quadros e sincronização iguais); 28 ossos iguais ao GLB; emendas com os mesmos ângulos; contato do focinho com o chão igual ou melhor (Deitar/Descanso/Levantar −0,003 → +0,019). Mergulho continua com o focinho abaixo de z 0, como antes (é clipe de água). A cena `CR_Crocodilo_Montaria_Teste.blend` foi regenerada sem mudança nas medidas do cavaleiro.
- Efeito visível: com a boca fechada os dentes de cima ficam por fora, como no estado "fechada 100%" aprovado no Lote 1. Na Mordida/Ameaça a abertura agora é exatamente a da mandíbula (máx. +12°), sem o giro extra da cabeça. Versão anterior em `versao_L4/`. Prancha: `review/boca_mov/PRANCHA_boca_antes_depois.png`; GIFs de cabeça em `review/boca_mov/antes|depois/`. Roblox não testado.

**05/11/2026 — Lote 5 (montaria): sela definitiva e subida/descida pelos dois lados. Aprovado pelo usuário em 06/11/2026 ("Aprovar Lote 5").**
- A aprovação vale para a forma da sela e os clipes no Blender. Textura em atlas, GLB da sela, integração no Roblox e mergulho montado continuam pendentes.
- Decisões do usuário (05/11): sela definitiva no Blender; o jogador sobe e desce **pelos dois lados**; mergulho montado **continua pendente**.
- Sela (`scripts/sela_crocodilo.py`, malha `CR_Croc_Sela`, 5.824 tris, 2.934 vértices): manta de tecido verde-musgo com debrum ocre (passa lisa por cima das cristas no meio e cai como pano na borda), aba de couro escuro, assento de couro com cabeça (frente) e patilha (atrás), alça de bronze na cabeça para a mão, cilha de couro em volta da barriga em y −3,95 com argolas de bronze nos dois lados, e **apoios de pé** de couro com alça de bronze nos dois lados. Não há estribo pendurado: o dorso é largo e as pernas do R15 são curtas, então o estribo ficaria solto no ar sem cavaleiro. O corpo do Meshy não é simétrico: o apoio direito é mais alto (0,48 contra 0,21). Pesos copiados da pele (média suave, até 4 ossos, incluindo as patas, porque a pele do ombro se mexe com elas). Rig, malha do crocodilo, escala e GLB **não mudaram**. Cena: `CR_Crocodilo_Sela.blend`.
- Folga sela × pele, quadro a quadro, nos 33 clipes (`scripts/qa_sela_clipes.py`): em terra ≥ −0,04 em todos. Nos clipes de água a cilha chega a −0,11/−0,13 (Nado, CurvaAquáticaE/D, Emersão) sob a pata dianteira recolhida; EntradaAgua −0,07, SaidaAgua −0,08. Cilha mais atrás (y −3,8) batia na coxa traseira direita.
- Clipes novos: `MontarDireita` (4,0 s) e `DesmontarDireita` (3,6 s), espelhos de Montar/Desmontar (rolagem, olhar e cauda para −X). Montar/Desmontar continuam sendo o lado esquerdo, sem mudança. Agora 33 JSON; os 31 anteriores estão **idênticos** (md5 em `versao_L4b/md5_clipes.txt`); no manifesto só entraram as 2 linhas novas.
- Cavaleiro de demonstração (`scripts/demo_montaria_l5.py`; base: demo do Lote 4 sem reescrever trajetórias): o lado direito é calculado num mundo espelhado em X e devolvido ao mundo real com esquerda↔direita trocados; os apoios são medidos na pele e na sela reais. Ajustes do lado direito: pontos do braço 0,3 para dentro (a pata dianteira D é mais fechada), descida em y −4,1 e 0,6 mais longe do corpo (o joelho traseiro D abre até x 4,1). Mãos apoiadas na manta usam a normal da pele.
- Folgas (manequim × pele; apoio = mãos/pés): Montar E corpo −0,18 / apoio −0,26 (iguais ao Lote 4); Desmontar E −0,15 / −0,25; MontarDireita −0,15 / −0,30 (1 quadro de pé de apoio no cotovelo); DesmontarDireita −0,11 / −0,03. Cavaleiro × sela: sentado −0,13 (coxa na lateral do assento), até −0,20 quando a perna passa sobre a sela. Reutilização (Repouso, Andar, Corrida, VirarE/D, NadoParado, Nado, CurvaAquáticaE/D, 3 ciclos): deriva 0, corpo ≥ −0,12 da pele, ≥ −0,15 da sela. Sequências Repouso → Montar → montado → Desmontar → Repouso dos dois lados: maior passo do quadril 0,23 stud por quadro.
- Evidências: `review/L5/` — `PRANCHA_sela_forma.png`, `PRANCHA_dois_lados.png`, `forma/`, `demo/` (folhas e GIFs dos 4 clipes), `seq/`, `reuso/`, `qa3/`, `qa_sela_clipes.txt`, `qa_demo_L5.json`, `RESUMO_L5.txt`. Cena: `CR_Crocodilo_Montaria_L5.blend`. Versão aprovada do Lote 4 em `versao_L4b/`.
- Limites: sela com materiais procedurais do Blender (5 materiais) — falta assar textura em um atlas e exportar o GLB da sela para o Roblox (só após aprovação da forma); manequim em caixas (R15 real é mais fino); sem controles, câmera, física, regra de lado no jogo; Roblox, celular e FPS sem teste; mergulho montado pendente.

**06/11/2026 — Lote 5b: textura em atlas e GLB da sela (só Blender). Aprovado pelo usuário em 06/11/2026 ("Aprovar e commitar").**
- `scripts/exportar_sela.py` (sobre `CR_Crocodilo_Sela.blend`): UV novo em atlas único (margem ~4 px) e os 5 materiais procedurais assados em 4 mapas 1024 num material só (`M_Sela_Atlas`): `tex/CR_Sela_cor_1024.png`, `_normal_1024`, `_rugosidade_1024`, `_metal_1024`. A cor é assada pela emissão (o passe difuso do Cycles deixava o bronze preto).
- `export/CR_Crocodilo_Sela.glb` (2,0 MB): só o esqueleto do crocodilo (mesmos 28 ossos, rig sem mudança) + a malha da sela (5.824 tris), sem animação. O GLB do crocodilo **não mudou** (md5 conferido).
- Conferência por reimportação: 1 malha no arquivo (a "Icosphere" que aparece é o desenho de osso criado pelo importador do Blender), 28 juntas, até 4 influências, ossos com peso: Pelve, Coluna1/2, Pescoço, BraçoE/D, CoxaE/D, Cauda1; medidas 5,74 × 3,39 × 5,84. Numa pose de teste (Pelve, Coluna1, Coluna2 e BraçoE girados) a sela reimportada fica a no máximo 0,000002 da original.
- No jogo: a sela entra como MeshPart DENTRO do modelo do crocodilo e usa os ossos dele (o Roblox liga a pele pelo nome do osso); os ossos que a sela não usa somem ao importar o GLB da sela, sem efeito. Importação (Import 3D) é manual; **Roblox não testado**.
- Evidências: `review/L5/PRANCHA_atlas.png` (procedural × atlas), `review/L5/atlas/`, `export/CR_Crocodilo_Sela_conferencia.json`. Cena de revisão: `CR_Crocodilo_Sela_Atlas.blend`.

**06/11/2026 — Lote 5c: materiais da sela pelos do Pântano Nebuloso (pedido do usuário). Aprovado pelo usuário em 06/11/2026 ("Aprovar e commitar").**
- Motivo: a sela aprovada usava materiais genéricos (bronze, que não é material básico, e manta de feltro tingido), fora da regra de materiais por bioma/fauna (RPG_01 25.3.1, 25.10, 25.22.7; base de peças em `DOCS/equipamentos/sela-dragoes.md`, que é [PROPOSTA] e feita para os dragões).
- Agora: assento, aba, cilha e apoios em couro de **Javali-do-Brejo** (escuro, lamacento); manta trançada de **Fibra de Mangue** (material estrutural oficial do bioma); argolas e alças dos pés em **ferro** escurecido com ferrugem (sem bronze); borda do arção em madeira de **Mangue Cinzento** na cabeça e na patilha; alça da mão em couro trançado com **tendão de Javali-do-Brejo**. Os nomes da fauna (Couro/Tendão de Javali-do-Brejo) são [PROPOSTA] da ficha de fauna.
- Adorno regional: Pena de Garça foi testada e **retirada** (as penas pareciam presas/espinhos saindo da sela). Fica [PENDENTE]; o material especial (Essência do Brejo) não tem visual definido.
- Forma, encaixe e pesos iguais aos do Lote 5. Peças novas só na borda de madeira (6.156 tris no GLB, antes 5.824). Medições refeitas iguais: sela × pele nos 33 clipes (terra ≥ −0,04; cilha −0,11/−0,13 nos clipes de água, como antes) e cavaleiro dos dois lados com os mesmos números do Lote 5.
- Atlas e GLB refeitos: `export/CR_Crocodilo_Sela.glb` (2,3 MB, 28 ossos, 1 malha, até 4 influências, pose de teste com diferença ≤ 0,000002); GLB do crocodilo sem mudança (md5). Versão anterior (aprovada) em `versao_L5b/`.
- Evidências: `review/L5c/PRANCHA_atual_x_pantano.png`, `review/L5c/forma/`, `review/L5c/atlas/`, `qa_sela_clipes.txt`, `qa_demo_L5c.json`. Roblox não testado.

**11/11/2026 — Lote R1 (comportamento real): postura de crocodilo de verdade. Aprovado pelo usuário em 11/11/2026 ("Aprovar e commitar").**
- Base: `DOCS/criaturas/crocodilo-primordial-referencias-reais.md` (pesquisa com fontes). Versão anterior preservada em `versao_L5c/` (clipes, Anim.blend, cena de montaria, script, md5).
- **Cauda arrastando** (`cauda_no_chao` em `scripts/anim_crocodilo.py`): na caminhada alta real a base da cauda sai do chão e a metade de trás vai encostada. Antes a cauda inteira ficava suspensa a 0,8–1,2 do chão. Agora, em todos os clipes de terra, Cauda4 a Cauda8 levam a pele ao chão e a Cauda3 desce até a metade; a onda lateral continua (a cauda varre o chão). Na água fica desligado; em EntradaAgua/SaidaAgua acompanha a troca das patas. Medido: cauda a 0,001–0,017 do chão em todos os 30 clipes de terra (encosta, não atravessa).
- Só os canais Cauda3–8 mudaram nos clipes de terra (quadros, sincronização e demais ossos iguais); Nado, CurvaAquáticaE/D, Mergulho e Emersão estão **idênticos** (md5). Emendas com os mesmos ângulos (diferença ≤ 0,1°), dentes iguais (lateral ≤ 0,07°, deslize ≤ 0,07), sela × pele igual ao Lote 5c, cavaleiro dos dois lados igual.
- **DeitadoBocaAberta** (novo, laço 6 s): *gaping* ao sol/calor — a mandíbula fica no chão e o **crânio sobe** a abertura máxima aprovada (+26°); queixo a 0,021 do chão. Emenda com DescansoDeitado por cruzamento curto.
- **NadoParado** refeito e **CurvaLentaEsquerda/Direita** (novos, 3 s, giro proposto 12°/s): devagar, patas abertas guiando; as traseiras remam alternadas (puxada para trás aberta, volta recolhida), na curva a traseira de fora rema mais forte e a dianteira de dentro segura. As CurvaAquática rápidas continuam com as patas recolhidas (correto para nado rápido). IK 0.
- Repouso padrão: o real fica deitado de barriga em terra. Os clipes já existem (Deitar → DescansoDeitado/DeitadoBocaAberta → Levantar); o "Repouso em pé" fica como pose de alerta/transição. **Quem escolhe deitar é a IA** (não existe ainda) — anotado para quando for feita.
- Agora 36 JSON. Evidências: `review/R1/` (antes × depois, `qa_chao_R1.txt`, `qa_transicoes_R1.txt`, `qa_sela_clipes.txt`, `qa_demo_R1.json`, `geracao_R1.txt`). Roblox não testado.

**11/11/2026 — Lote R2 (comportamento real): caça. Aprovado pelo usuário em 11/11/2026 ("Aprovar e commitar"). Só animação.**
- 8 clipes novos em `scripts/anim_crocodilo.py` (44 JSON; os 36 anteriores **idênticos**, md5 em `versao_R1/`):
  - **Espreita** (laço 6 s, água): imóvel, patas abertas e soltas, cabeça nivelada; o jogo deixa só olhos, narinas e cristas fora d'água.
  - **AproximacaoSubmersa** (laço 3 s, água): patas coladas, cauda em onda longa e baixa, corpo e cabeça estáveis (silencioso).
  - **BoteAquatico** (1,6 s, água): afunda e encolhe a cauda → chicotada lança o corpo para cima/frente (até 1,5 de altura e 1,2 à frente no clipe) com a **cabeça virada de lado** e a boca toda aberta → fecha de estalo no alto (0,62 s) → volta para a água segurando.
  - **MordidaLateralEsquerda/Direita** (1,0 s, terra): vira para o lado oposto e abre, varre a cabeça de lado e fecha no meio da varrida.
  - **ArrastarPresa** (laço 1,8 s): anda de ré (ciclo do Andar invertido, 0,79 studs/s para trás), cabeça baixa, boca travada, dois puxões de cabeça por ciclo; cauda arrasta.
  - **Engolir** (2,2 s): ergue a cabeça e dá dois trancos para trás com a boca entreaberta (o pedaço escorrega).
  - **RolarDaMorte** (laço 1,2 s = 1 volta): gira o corpo inteiro no eixo longo (eixo no meio do tronco, não na sola), patas coladas, cauda dobrada de lado, boca travada. **Só animação**: agarrão, dano, regra PvP e se vira habilidade continuam decisão do criador.
- QA: IK 0 nos 8; terra com cauda a 0,016–0,017 do chão e focinho ≥ 1,3 (mordidas), pés iguais ao Andar (−0,25, pendência antiga); dentes sem cruzar (lateral ≤ 0,07°, deslize 0). Alturas de água nos renders são **de teste**.
- Evidências: `review/R2/` (folhas e GIFs por clipe, `qa_chao_R2.txt`, `geracao_R2.txt`). Roblox não testado.

**11/11/2026 — Lote R3 (comportamento real): sinais. Aprovado pelo usuário em 11/11/2026 ("Aprovar e commitar"). Só animação.**
- 3 clipes novos (47 JSON; os 44 anteriores **idênticos**, md5 em `versao_R2/`):
  - **AmeacaInflada** (2,6 s, terra): ergue-se alto nas patas, arqueia o tronco, cabeça alta de boca toda aberta (sibilo, tremor), cauda chicoteando; termina com **bote curto** de estalo (0,45 à frente) e volta ao Repouso. O rig não tem canal de escala (JSON = rotação + posição): o "inflar" aparece pela postura.
  - **BatidaDeCabeca** (2,6 s, água): postura cabeça-e-cauda-para-fora (HOTA), ergue a cabeça de boca entreaberta e bate a parte de baixo na superfície fechando de estalo (evento em 1,2 s para som/respingo), quica e relaxa.
  - **Bramido** (4,0 s, água): HOTA com o dorso arqueado; **vibração** do tronco de 0,8 a 2,1 s (no jogo: gotas "dançando" sobre o dorso como VFX, desempenho a medir) e depois brame de boca meio aberta com a cabeça subindo.
- QA: IK ≤ 0,013 (o bote curto foi limitado a 0,45 porque 0,8 esticava a traseira E plantada, IK 0,14); AmeacaInflada com cauda a 0,015 do chão e pés iguais ao Repouso; dentes sem cruzar (lateral ≤ 0,07°, deslize 0).
- Evidências: `review/R3/` (folhas, GIFs normal e lento, `qa_chao_R3.txt`, `geracao_R3.txt`). Roblox não testado.

## 6. Pendências
1. **Decisões do criador:**
   - **conflito do agarrão PvP** (só empurra × agarrão mais longo interrompível por aliados);
   - elemento único;
   - lista final de passivas e ativas e seus efeitos;
   - **mergulho com cavaleiro** (sim/não; respiração, câmera, profundidade, segurança);
   - velocidades em terra e água; números (24.2 é só proposta);
   - duração do agarrão PvE e tamanho máximo de presa;
   - cores dos 3 padrões; tamanhos por estágio.
2. **Modelo:** escolher a base (V2 ou V5) e revisar contra o painel 03; boca/dentes/língua; custo da V5 (56 mil tris) precisa de LOD.
3. **Estágios:** só existe o Adulto. Faltam Bebê, Jovem, Pré-adulto, Ancião e ovo.
4. **Roblox:** importar (Import 3D manual), conferir escala, pés no chão, superfície da água (corpo meio submerso), SurfaceAppearance e FPS. Publicar animações exige a conta do usuário.
5. **Animações:** auditadas só numericamente. GuardarNinho com ajustes. Seguir `padrao-movimento-criaturas` (cauda em onda base→ponta, ondulação lateral no nado, antecipação→contato→recuperação nos ataques).
6. **Sistemas (não iniciados):** IA selvagem (território, emboscada submersa, toca, descanso na margem), companheiro domesticado, montaria anfíbia (troca terra↔água), sons (rugido grave, sibilo, batida de mandíbula, respingos), VFX (bolhas, ondulações, ondas da cauda). Tudo com validação no servidor; agarrão com autoridade do servidor e regra PvP/PvE separada.

## 7. Próximos passos sugeridos (aguardam aprovação)
1. **Pedir ao criador** a decisão do conflito do agarrão PvP e, se possível, elemento único + kit (passiva + ativas) antes de qualquer VFX ou combate.
2. **Revisar V2 × V5** com prancha lado a lado com o painel 03 (só leitura e renders no Blender) e listar correções (boca, mandíbula, patas espalhadas, osteodermos).
3. **Teste de importação num place vazio local** (sem tocar no mapa): escala 5–7 de ombro, nado na linha d'água, Mergulho/Emersão.
4. **Só depois:** clipes refinados, sons, IA selvagem e montaria terra/água. Um sistema por vez; mergulho montado só depois de definido pelo criador.
