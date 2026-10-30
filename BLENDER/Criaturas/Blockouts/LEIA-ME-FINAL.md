# Criaturas: refinamento, finalização, rig e animações (26/10/2026)

**Estado:** as 16 formas oficiais estão refinadas, finalizadas (materiais e cores-base), com rig e animadas no Blender, e exportadas em GLB validado por reimportação.

**Ainda não feito:** importação e teste no Roblox Studio. É **manual**: Import 3D e depois publicar as animações.

**Avaliação:** a qualidade é de **protótipo jogável**, não de arte final cinematográfica. As limitações estão listadas abaixo.

## Arquivos
- `<Especie>/<Especie>_refinado.blend`: modelo refinado (Fase 3, formas).
- `<Especie>/<Especie>_final.blend`: materiais, rig e animações (ações em faixas NLA, silenciadas para a pose de descanso).
- `_Export/<Especie>.glb`: entrega para o Roblox (malhas com pele, esqueleto e todas as ações).
- `CR_Criaturas_Final_Biblioteca.blend`: as 16 formas finais lado a lado (`CREATURES/BLOCKOUTS/<Especie>`).
- `CR_Blockouts_Biblioteca_v1_silhuetas.blend`: cópia da fase de silhuetas aprovada (preservada).
- `build/`:
  - `blockout_lib.py` (modelagem), `lobo_base.py` e `dragao_base.py` (bases de família), `build_*.py`;
  - `esqueletos.py` (rigs por família);
  - `pipeline_final.py` (finalização, rig, animações e exportação);
  - `render_poses.py`.
- Evidências:
  - `review/Final_16_criaturas_material.png`;
  - `review/_poses_*.png`;
  - `review/<Especie>/final.json` (ossos, animações, triângulos);
  - `review/validacao_glb_final.txt`.
  - Cópias em `SCREENSHOTS/Criaturas_Final_2026_10_26/`.

## 1. Refinamento (o que mudou em relação aos blockouts)
- **Duas camadas:** tecido mole fundido com suavização Laplaciana (que preserva volume e tira os "calombos de balão"). Por cima, marcos ósseos com suavização leve: espinha da escápula, cotovelo, crista ilíaca, calcâneo, carpo, arcadas e maçãs.
- **Patas por família:**
  - canídeos e felino: digitígrados, com almofada, 4 dedos e garras;
  - urso: plantígrado com 5 garras longas;
  - búfalo: casco fendido;
  - répteis: pé espalhado com 5 dedos e garras;
  - escorpião: pernas segmentadas com juntas.
- **Cabeças com identidade:**
  - Lobo: crânio em cunha, focinho longo, orelhas eretas.
  - Leão: focinho largo, almofadas dos bigodes, juba suavizada e integrada.
  - Urso: focinho alongado, testa inclinada.
  - Búfalo: chifres grandes curvos para fora e para cima, como no painel.
  - Crocodilo: crânio plano, mandíbula pesada, dentes, olhos e narinas no topo.
  - Basilisco: arcadas pesadas ("olhar ameaçador" oficial).
  - Dragões: focinho em cunha, mandíbula, dentes, narinas.
- **Estruturas por espécie:**
  - Crocodilo: osteodermos em escudos, crista dupla na cauda.
  - Basilisco: cristas em lâmina.
  - Lagarto: **aglomerados naturais de prismas hexagonais**, variados e assimétricos.
  - Escorpião: pinças massivas, dentes, espinhos, ferrão em gancho.
  - Serpente: seção oval vertical, cabeça dracônica maior, dentes, nadadeiras maiores.
  - Leviatã: dentes, raios ósseos nas nadadeiras.
  - Asas: a membrana agora desce até a coxa, ligada ao corpo.
- **Silhueta preservada:** IoU contra a silhueta oficial Leão 0,820, Lobo Ancestral 0,827, Lobo Ártico 0,833, Urso 0,795, Búfalo 0,795. As medidas continuam dentro das faixas do RPG_02.

## 2. Finalização visual
- **Materiais separados por papel** (um objeto por material, pronto para MeshPart/SurfaceAppearance): corpo (pelo/escama/quitina), garra, osso/corno/dentes, olho, membrana, cristal (com transmissão).
- **Cores-base neutras = padrão oficial 1 de cada forma**:
  - Cinza da Floresta, Branco Polar, Negro Carbonizado, Dourado Solar, Castanho do Bosque;
  - Verde Pantanal, Verde Pantanoso, Quartzo Claro, Negro Obsidiana, Azul Oceânico, Azul Abissal, Verde Musgo;
  - Basalto Cinzento, Branco Glacial, Negro Obsidiana.
  - O Búfalo usa castanho profundo **provisório**.
  - Os padrões 2 e 3 ficam para a fase de texturas, trocando só a cor.
- **Cor de vértice "Sombreamento":** contra-sombreamento (dorso mais escuro, ventre mais claro), juba castanho-avermelhada no Leão, sela dorsal nos Lobos, capa no Búfalo. Nada de neon nem brilho mágico: efeitos elementais ficam para VFX.
- **Orçamento:** maior objeto com 18.000 tris (limite do MeshPart: 20.000). GLBs de 1,2 a 2,4 MB.

## 3. Rigs por família (pele deformável, até 4 influências por vértice)

| Forma | Família | Ossos | Animações |
|---|---|---|---|
| Lobo Ancestral / Lobo Ártico | canídeo | 32 / 32 | 28 / 28 |
| Cérbero Sombrio | canídeo + 3 cadeias de pescoço/cabeça/mandíbula | 40 | 28 |
| Leão Solar | felino | 36 | 28 |
| Urso Silvestre | plantígrado | 25 | 28 |
| Búfalo Colossal | ungulado | 27 | 28 |
| Crocodilo Primordial | réptil (+ nado) | 24 | 31 |
| Basilisco / Lagarto Cristalino | réptil | 28 / 23 | 28 / 28 |
| Escorpião Colossal | artrópode (8 pernas × 3, pinças + dedo móvel, cauda 7 + ferrão) | 43 | 28 |
| Serpente Marinha | serpentino | 27 | 34 |
| Leviatã Jovem | marinho de 4 nadadeiras | 22 | 34 |
| Wyvern | bípede + asa-braço (3 dedos) | 39 | 36 |
| Dragões (×3) | quadrúpede + 2 asas (4 dedos) | 48 cada | 36 cada |

**Total: 495 animações.**

**Regras de pesos:**
- partes rígidas presas 100% ao osso mais próximo, ilha por ilha (cada garra, dente e cristal);
- membranas só nos ossos da asa/nadadeira/coluna/cauda;
- a mandíbula só move o que fica abaixo da linha da boca.

## 4. Animações
- **Pacote base (todas):** Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Arrancada, Frenagem, ReacaoGolpe, AtaqueBasico, Morte, Comer, DeitarDescanso, Descanso, LevantarDescanso.
- **Montaria (todas, montáveis no Adulto pelo RPG_02):** Montar, Desmontar, MontadoRepouso, MontadoAndar, MontadoCorrida, MontadoVirarE, MontadoVirarD.
- **Territorial (todas):** GuardarNinho, Alerta, Ameaca. O Urso ergue-se nas patas traseiras.
- **Voo (Dragões, Wyvern):** Decolagem, Pouso, Planeio, VooBatido, Pairar, AtaqueAereo, Empoleirar, CurvaAerea.
- **Nado:**
  - Serpente e Leviatã: NadoParado, NadoCruzeiro, NadoRapido, NadoSuperficie, Mergulho, Emersao.
  - Crocodilo: NadoCruzeiro, Mergulho, Emersao.
  - Para Serpente e Leviatã, Andar/Corrida = deslize em terra (oficial).
- **As 4 habilidades oficiais de cada forma**, como movimento sem efeito. Exemplos:
  - MordidasTriplices (as cabeças mordem em sequência);
  - FuriaDasTresCabecas;
  - GiroPredatorio;
  - FerraoPerfurante;
  - RasantePredatorio;
  - SoproDraconico.

**Caráter por espécie:** amplitude, peso (ciclos mais lentos e menos bob nos pesados) e cabeça. Exemplos:
- Lobo Ancestral leve;
- Lobo Ártico mais firme;
- Búfalo e Leviatã lentos e pesados;
- Wyvern rápida.

**Reaproveitamento:** um gerador por família, com parâmetros por espécie. Os mesmos ciclos derivam montaria de andar/corrida. Não há reaproveitamento entre famílias.

## Limitações honestas e pontos que precisam de aprovação
1. **Nada foi testado no Roblox.**
   - A importação é manual (Import 3D, Scale Unit = Stud), assim como a publicação das animações.
   - A cor de vértice pode não ser importada; nesse caso é preciso assar em textura.
   - O desempenho dos rigs de 48 ossos (Dragões) no celular não foi medido.
2. **Animações procedurais:** são legíveis e coerentes por família, mas não substituem animação à mão.
   - Corrida e pouso estão funcionais, mas simples.
   - Asas dobradas em repouso ainda têm dobras duras na membrana.
   - Ao abrir a mandíbula surge um vão sem cavidade bucal. Por isso a abertura é contida nos répteis, aquáticos e Dragões.
3. **Anatomia que ainda merece correção antes de um rig definitivo:**
   - Basilisco e Lagarto: membros grossos e cabeça um pouco canina.
   - Lagarto: corpo claro demais (o padrão "Quartzo Claro" pede ajuste de tom).
   - Cérbero: as cabeças ainda se parecem com as do lobo.
   - Wyvern: corpo fino e asas largas.
   - Leão: juba ainda em massas lisas.
4. **Faltam:** textura/normal assadas (só cores-base e cor de vértice), LODs e colisores simplificados.
5. **Provisórios:** cor do Búfalo; comprimentos e alturas que o RPG_02 não define (ver `LEIA-ME-BLOCKOUTS.md`).
