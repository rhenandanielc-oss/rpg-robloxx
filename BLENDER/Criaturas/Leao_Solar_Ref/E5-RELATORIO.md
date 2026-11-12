# Leão Solar — E5: junção juba/peito/pata, rig de produção e clipes da Fase A (04/11/2026)

**Fase A ACEITA pelo usuário em 05/11/2026** (no Blender, após a correção r3). Nada testado no Roblox.

Pedido: `DOCS/pedidos/2026-11-04-leao-solar-rig-animacoes-naturais-agressivas.md` (corrigir a dependência da mecha, rig de produção, Fase A).
Tudo no Blender. **Nada importado nem testado no Roblox.** Sem Studio, sem Meshy, sem commit.

## 1. A "mecha fundida no antebraço" não existe (correção do relatório E4b r2)

O relatório E4b r2 dizia que uma mecha longa do peito tinha a ponta fundida no antebraço. **Esse diagnóstico estava errado.**

- **Cortes horizontais e verticais** da malha densa (E3b) e da malha de jogo (`review/e5/cortes.png`, `review/e5/cortes_x.png`):
  - abaixo de z ≈ 5,4 o antebraço é uma coluna separada;
  - a juba que pende entre as patas é feita de mechas soltas;
  - a pata se junta ao peito em z ≈ 5–6, como numa junção anatômica de cotovelo/axila.
  - Não há mecha sobre o antebraço, nem na E3b nem na E4b.
- **Mapa da cor** (`review/e5/_zona_grade.png`): a pele do antebraço é pelo dourado, sem juba pintada.
- **Origem do engano:** a aresta "comprida" atribuída a uma mecha era um triângulo comprido da pele do antebraço (2,6 studs, da decimação). O vértice de cima, atrás do cotovelo, seguia o Peito porque a máscara da juba era feita por **saturação**, e a saturação também pega o pelo dourado do alto do cotovelo.
- **Consequência:**
  - não há geometria a separar, então **0 triângulos acrescentados ou removidos**;
  - UV, bake e aparência ficam iguais aos da E4b (17.602 tris);
  - o que resta é o esticamento da pele na junção cotovelo/peito quando o úmero avança.
- **Variantes de peso testadas para essa junção:** máscara por cor avermelhada (t1) e pertencimento geométrico à pata (t2). Ambas **pioraram** as poses dianteiras e o pescoço (`review/e5/med_t1`, `med_t2`):
  - ombro: 483 arestas esticadas, 3,0 studs;
  - contra o r2: 143 arestas, 1,8 stud.
- **Ficam os pesos do r2**, que foram os melhores entre 7 variantes.

## 2. Rig de produção (`Leao_Solar_Ref_E5_rig.blend`, armadura `Leao_Solar_Rig`)

- **Base:** o rig da E4b r2, com os mesmos pesos do corpo, e mais:
  - `Orelha_D/E` (filhas da Cabeça; 53 e 52 vértices);
  - `Palpebra_D/E` (pálpebra superior; −25° semicerra, −40° fecha quase todo o olho).
  - Teste visual: `review/e5/_rosto_t1.png`.
- **Contagem:** 61 ossos, 60 deformam. `Raiz` fica no chão e não deforma.
- **Pesos:**
  - 0 vértices sem peso;
  - no máximo 4 influências por vértice, todas normalizadas;
  - nenhum osso que deforma ficou sem peso (no Roblox, ossos sem peso somem).
- **Atributo de QA** `qa_juba`: removido. A evidência ficou nos arquivos de revisão.
- **Hierarquia e pivôs:** `review/e5/rig_producao.json`. Resumo:
  - `Raiz` > `Quadril` > `Coluna1` > `Coluna2` > `Peito` > `Pescoco1` > `Pescoco2` > `Cabeca` > `Mandibula` > `Lingua1` > `Lingua2`;
  - na `Cabeca`: `Orelha_D/E`, `Palpebra_D/E`;
  - no `Pescoco1`: 8 cadeias `Juba_<setor>_1/2`;
  - no `Peito`: `Escapula` > `Umero` > `Antebraco` > `Mao` > `Dedos`, com `Cotovelo_Aux` (filho do Úmero) e `Punho_Aux` (filho do Antebraço);
  - no `Quadril`: `Coxa` > `Canela` > `Metatarso` > `Dedos`, e `Cauda1`…`Cauda6`, com `Tufo1/2` filhos da `Cauda4`.
- **Nada depende de solver no Roblox.** Tudo é gravado em chaves:
  - os auxiliares de volume ficam com metade da rotação do filho;
  - o tufo segue a cauda e a juba usa mola amortecida sobre a velocidade angular do pai;
  - o IK das patas é resolvido no gerador e gravado.
- **Boca no rig final** (`review/e5/_poses_rig.png`): abre de 0° a 32° com a mesma medição da E4b. Boca fechada inalterada.
- **Dobras do cotovelo e do punho, pescoço virado:** mesmas medidas do r2.
  - Espessura da pata: cotovelo 0,58, punho 0,54.
  - Passo dianteiro: 96 arestas esticadas, 1,48 stud.
  - Pescoço: 312 arestas na juba, 0,84 stud. A juba do ombro acompanha sem rasgo.

## 3. Clipes da Fase A (`Leao_Solar_Ref_E5_faseA.blend`, 16 ações `Leao_<clipe>`)

- **Gerador:** `build/e5/e5_20_clipes.py`, determinístico.
  - **Raiz:** trajetória com deslocamento real.
  - **Patas:** planejador por pata. No apoio a pata fica parada no mundo; o pouso mira o meio do próximo apoio; a pata decola cedo se passar do alcance; o corpo desce quando a pata apoiada não alcança o chão.
  - **Pernas:** IK analítico de 2 ossos. O metacarpo e o metatarso seguem regras de extensão no fim do apoio e de dobra no balanço.
  - **Escápula:** rola com o úmero (32%).
  - **Cabeça:** estabilizada no mundo.
  - **Sola no balanço:** checada pelos vértices reais.
  - **Secundários:** gravados depois.
- **Dados:** 30 FPS. As velocidades são **proposta** (o RPG_02 24.2 propõe até 42 studs/s, sem aprovação).
- **Versão para o jogo:** a mesma ação com a translação da `Raiz` zerada, já que o jogo move o modelo.
- **Vídeos:** `review/e5/faseA/<clipe>_{perfil,34}.mp4` (tempo real) e `_lento.mp4` (1/3 da velocidade), com chão quadriculado e sombra.

| Clipe | Quadros | s | Tipo | v (studs/s) | Desloc. | Erro IK | Escorreg. p90/quadro | Altura mín. | Pousos (quadro) |
|---|---|---|---|---|---|---|---|---|---|
| Repouso_Vigilante | 204 | 6.80 | loop | 0.0 | 0.0 | 0.000 | 0.000 | -0.01 | patas paradas |
| Repouso_Relaxado | 264 | 8.80 | loop | 0.0 | 0.0 | 0.000 | 0.000 | -0.01 | patas paradas |
| Observar_Farejar | 157 | 5.23 | ação | 0.0 | 0.0 | 0.000 | 0.000 | -0.01 | patas paradas |
| Andar | 73 | 2.43 | loop | 7.8 | 18.7 | 0.000 | 0.009 | -0.07 | DD 30,67; DE 12,49; TD 3,39; TE 21,57 |
| Trote | 46 | 1.53 | loop | 17.0 | 25.4 | 0.000 | 0.021 | -0.07 | DD 2,25; DE 14,37; TD 15,38; TE 3,26 |
| Repouso_para_Andar | 73 | 2.43 | ação | 0.0 | 12.4 | 0.000 | 0.009 | -0.07 | DD 34,68; DE 25,50; TD 41; TE 25,58 |
| Andar_para_Repouso | 79 | 2.63 | ação | 7.8 | 5.0 | 0.000 | 0.061 | -0.07 | DD 30; DE 12,49; TD 3,39; TE 21,57 |
| Andar_para_Trote | 73 | 2.43 | ação | 7.8 | 31.7 | 0.000 | 0.022 | -0.07 | DD 29,48,69; DE 12,39,57; TD 3,36,58; TE 21,47,70 |
| Trote_para_Andar | 73 | 2.43 | ação | 17.0 | 26.8 | 0.000 | 0.060 | -0.07 | DD 2,25,55,71; DE 14,39; TD 15,41; TE 3,26,60 |
| Trote_para_Corrida | 61 | 2.03 | ação | 17.0 | 56.4 | 0.000 | 0.041 | -0.06 | DD 2,24,43; DE 14,34,53; TD 15,38,59; TE 3,26,44 |
| Corrida_para_Trote | 61 | 2.03 | ação | 34.7 | 45.2 | 0.000 | 0.034 | -0.06 | DD 3,22,43; DE 3,22,43; TD 4,23,38,61; TE 6,25,49 |
| Arrancada | 70 | 2.33 | ação | 0.0 | 49.3 | 0.000 | 0.047 | -0.07 | DD 35,53; DE 37,54; TD 39,57; TE 41,59 |
| Frenagem | 73 | 2.43 | ação | 34.7 | 23.7 | 0.000 | 0.034 | -0.07 | DD 3,22,68; DE 3,22,69; TD 4,23,41; TE 6,25,63 |
| Virar_E | 88 | 2.93 | ação | 0.0 | 1.6 | 0.000 | 0.060 | -0.07 | DD 14,38,62; DE 12,26,50,74; TD 20,44,68; TE 12,32,56,80 |
| Virar_D | 88 | 2.93 | ação | 0.0 | 1.6 | 0.000 | 0.048 | -0.07 | DD 12,26,50,74; DE 14,38,62; TD 12,32,56,80; TE 20,44,68 |
| Corrida | 38 | 1.27 | loop | 34.7 | 42.8 | 0.000 | 0.031 | -0.23 | DD 19,38; DE 18,37; TD 4,23; TE 6,25 |

- **Altura mínima:** −0,07 é a ponta de um dedo dianteiro que no repouso já está em −0,01 (afunda 0,06 com a pata apoiada). Na Corrida, num quadro, essa ponta chega a −0,23 quando o calcanhar sobe no fim do apoio.
- **Loops** (Andar, Trote, Corrida, repousos): fecham sozinhos. A diferença bruta entre o último e o primeiro quadro é de no máximo 1° (cauda), e ela é distribuída ao longo do ciclo.

## 4. Revisão visual (folhas de quadros na prancha `review/E5_prancha.png`): o que está bom e o que falta

| Clipe | Achado |
|---|---|
| Repouso_Vigilante / Relaxado | Respiração, pequena troca de peso, olhar, orelhas, piscadas e cauda. O relaxado tem cabeça mais baixa e olhos meio fechados. Sutil: avaliar no vídeo. |
| Observar_Farejar | Ergue a cabeça, fixa à esquerda, fareja em 3 pulsos e volta. As orelhas mexem pouco (ficam dentro da juba). |
| Andar | Sequência lateral (TE, DE, TD, DD), patas paradas no apoio, pata dianteira dobrando no balanço, cabeça estável, juba e cauda com atraso. É o melhor clipe. |
| Trote | Pares diagonais com quique. Bom. |
| **Corrida (refeita r2, corrigida r3)** | Galope rotatório: traseira direita, traseira esquerda, dianteira esquerda, dianteira direita, com 2 a 3 quadros de defasagem dentro de cada par. A coluna **fecha** (corcova) no voo recolhido e **abre** quando as traseiras empurram e as dianteiras alcançam. Tronco mais baixo que no trote, passada de 22 studs, 1,58 passadas/s, cauda alta de equilíbrio e orelhas para trás. Na r3, a pata dianteira não vira mais e as traseiras ficam esticadas no voo (seção 7). |
| **Arrancada (refeita, r2)** | Agachamento fundo (−1,8 stud), coluna fechada, pescoço baixo, olhar fixo à frente, orelhas para a frente e cauda alta (sem tocar o chão). Na explosão, as dianteiras saem escalonadas (quadros 17/19), as traseiras empurram em seguida (22/24), a coluna abre, o peito sobe e a dianteira alcança longe. Depois o galope acelera até ~35 studs/s em ~1,1 s. |
| Frenagem | Sai do galope e desacelera passando por trote e andar até parar de pé. O peito baixa, mas a frenagem com as dianteiras ainda é discreta. |
| Transições (andar↔trote, trote↔corrida, partir/parar) | Sem tranco nem escorregamento nos números. As de galope foram regeneradas com o galope novo. |
| Virar_E / Virar_D | 90° no lugar com passos de reposição, cabeça antecipando e cauda para fora. Bom. |

## 5. Riscos e pendências

- **Corrida e Arrancada:** refeitas (r2) e corrigidas (r3). O script da primeira versão está em `review/e5/e5_20_clipes_faseA_v1.py`. A frenagem com as dianteiras ainda é discreta.
- **Perna traseira esquerda do rig:** corrigida na r3 (seção 7). A malha dessa perna continua na pose recuada do Meshy, então a deformação da coxa esquerda deve ser conferida no vídeo do lado esquerdo.
- **Junção cotovelo/peito:** ainda estica nos avanços grandes do úmero, até 1,8 stud numa aresta de pele.
- **Orelhas:** quase não aparecem, porque ficam dentro da juba.
- **Pálpebras:** funcionam por deslizamento da pele (não há pálpebra modelada).
- **Rugido e língua:** não fazem parte da Fase A; a boca foi testada só como pose.
- **Roblox:** importação, skin com 4 influências, desempenho e reprodução dos clipes não foram testados.

## 6. Arquivos

- `Leao_Solar_Ref_E5_rig.blend` (rig de produção, sem animação)
- `Leao_Solar_Ref_E5_faseA.blend` (rig + 16 ações)
- `build/e5/`:
  - `e5_11_rig_producao.py`
  - `e5_12_teste_rosto.py`
  - `e5_20_clipes.py`
  - `e5_30_prancha.py`
  - inspeções `e5_00`…`e5_06`
  - pesos testados `e5_10`
- `review/E5_prancha.png`
- `review/e5/faseA/` (vídeos, quadros, `clipes_*.json`)
- `review/e5/rig_producao.json`
- `review/e5/cortes*.png` e `_zona_grade.png` (evidência da mecha)

## 7. Correção r3 (04/11): pata dianteira contorcida e traseiras entrando no corpo (pedido do usuário)

- **Pata dianteira na corrida (ia para trás e se contorcia):**
  - **Causa:** no balanço o metacarpo dobrava 105° e ficava dobrado até ~55% do balanço, com a sola virada para cima mesmo com a perna já à frente.
  - **Correção:** dobra máxima de 58°, só no começo do balanço; a pata chega esticada quando a perna avança. Os dedos dianteiros dobram 55% do que dobravam.
- **Traseiras entrando no corpo:**
  1. **Joelho esquerdo do rig fora do lugar.** A coxa tinha 2,73 e a canela 3,42; a direita tem 3,71 e 2,85. O joelho foi recolocado com os comprimentos da direita, de (−1,65; 7,0; 6,2) para (−1,06; 6,76; 5,16), dentro da malha (`review/e5/traseiras_juntas.png`). Os pesos foram refeitos (`e5/juntas_e5.json`, `e5/E5_pesos_r3.blend`).
  2. **A perna fechava demais no balanço** e a canela atravessava a coxa/flanco. Agora há uma distância mínima ombro|quadril → punho|jarrete: 70% do comprimento nas dianteiras, 76% nas traseiras.
  3. **Galope:** as traseiras sobem menos (1,3 em vez de 2,2), pousam no máximo 2,6 à frente do quadril (antes 4,2) e o tronco fica 0,3 mais alto.
- **Evidência:** `review/e5/_corrida_antes_depois.png` (mesma câmera, 12 quadros). Os 16 clipes foram regenerados e renderizados de novo, com a tabela de QA acima.
- **Medida automática de "perna dentro do corpo"** (distância assinada à pele mais próxima): foi testada, mas oscila na junção joelho/flanco (dá 1,1 stud até no Observar, em que a pose quase não muda). Por isso **não** serve de prova; a evidência é visual.
- **Backups:** rig anterior em `e5/Leao_Solar_Ref_E5_rig_v1.blend`, vídeos anteriores em `review/e5/faseA_r2_antiga/`.

## 8. Fase B (05/11/2026): atitude agressiva e ataques, em revisão

Só **movimento**: sem poderes, dano, alcance, cadência, VFX nem Fogo/Luz. Os nomes são neutros até o kit ser aprovado.

### Rig

- **Lábios superiores:** `Labio_D` e `Labio_E`, filhos da Cabeça, 40 vértices cada (sem dentes nem interior).
  - Sobem por translação (até 0,32 stud) e mostram caninos e gengiva aos poucos.
  - Acima de 0,4 o canto da boca forma pontas, então esse valor não é usado.
  - Teste: `review/e5/_rosnado_t1.png`.
- **Contagem:** 63 ossos. 0 vértices sem peso, no máximo 4 influências por vértice.
- **Versões:** o rig da Fase A ficou em `e5/Leao_Solar_Ref_E5_rig_faseA.blend`. As ações da Fase A continuam válidas (os lábios ficam em repouso).
- **Hierarquia:** `review/e5/rig_producao.json`.

### Gerador

- **Agenda de patas** (`agenda_pata`): instantes de decolagem e pouso, alvo do pouso e pontos de passagem (Catmull-Rom) com o ângulo do metacarpo. Usada no bote, na patada, na mordida e na esquiva.
- **Novos controles:**
  - deslocamento lateral da raiz;
  - língua (`Lingua1/2`) e lábios;
  - avanço do tronco;
  - limite de dobra da perna ajustável por clipe (0,40 nas patadas, para o cotovelo poder erguer a pata).
- **Regressão:** os clipes da Fase A deram o mesmo QA de antes.
- **Arquivos:** os clipes estão em `build/e5/e5_21_faseB.py`.

### Clipes (`Leao_Solar_Ref_E5_clipes.blend` = Fase A + B, 28 ações `Leao_<clipe>`)

| Clipe | Quadros | s | Tipo | Desloc. (studs) | Erro IK | Escorreg. p90/quadro | Altura mín. | Pousos (quadro) |
|---|---|---|---|---|---|---|---|---|
| Alerta_Ameaca | 79 | 2.63 | ação | 0.0 | 0.000 | 0.000 | -0.01 | patas paradas |
| Intimidacao | 127 | 4.23 | ação | 0.0 | 0.000 | 0.000 | -0.01 | patas paradas |
| Rosnado | 90 | 3.00 | loop | 0.0 | 0.000 | 0.000 | -0.00 | patas paradas |
| Rugido | 139 | 4.63 | ação | 0.0 | 0.000 | 0.000 | -0.01 | patas paradas |
| Aproximacao_Furtiva | 96 | 3.20 | loop | 11.9 | 0.000 | 0.006 | -0.07 | DD 19,67; DE 43,91; TD 31,79; TE 7,55 |
| Bote | 76 | 2.53 | ação | 15.0 | 0.000 | 0.023 | -0.20 | DD 35; DE 37; TD 40; TE 42 |
| Patada_D | 58 | 1.93 | ação | 0.0 | 0.000 | 0.024 | -0.06 | DD 37 |
| Patada_E | 58 | 1.93 | ação | 0.0 | 0.000 | 0.020 | -0.03 | DE 37 |
| Mordida | 61 | 2.03 | ação | 1.5 | 0.000 | 0.024 | -0.07 | DD 21,46; DE 23,48; TD 25,50; TE 27,51 |
| Esquiva_E | 49 | 1.63 | ação | 4.5 | 0.000 | 0.025 | -0.06 | DD 22; DE 22; TD 24; TE 24 |
| Esquiva_D | 49 | 1.63 | ação | 4.5 | 0.000 | 0.025 | -0.06 | DD 22; DE 22; TD 24; TE 24 |
| Fadiga_Recuperacao | 145 | 4.83 | ação | 0.0 | 0.000 | 0.000 | -0.01 | patas paradas |

| Clipe | O que faz |
|---|---|
| Alerta_Ameaca | O corpo firma e sobe um pouco, o peso vai para trás, a cabeça ergue e fixa, as orelhas vão para a frente, os olhos se abrem, a respiração se segura e a cauda dá um piparote. |
| Intimidacao | Parte do alerta. O corpo baixa e avança o peso, a cabeça baixa com o olhar para cima, as orelhas vão para trás, os lábios sobem aos poucos, a boca se entreabre com vibração, a cauda chicoteia e o peito ronca. |
| Rosnado (loop) | Boca semiaberta, lábios erguidos, peito vibrando (9 Hz) na expiração, cabeça baixa e cauda balançando. |
| Rugido | Inspiração (tórax enche, cabeça sobe), antecipação (cabeça desce), rugido com a boca a 32°, língua, lábios, olhos fechando, orelhas para trás e o tronco empurrando à frente. Depois, três roncos decrescentes, fechamento e retorno. |
| Aproximacao_Furtiva (loop) | Tronco ~1,35 mais baixo, coluna levemente arqueada, passos lentos (0,63 passada/s, 3,8 studs/s), cabeça baixa e nivelada com o olhar fixo, orelhas para a frente e ponta da cauda tremendo. |
| Bote | Agacha fundo com o quadril rebolando. As dianteiras saem primeiro e alcançam esticadas; as traseiras empurram. Voa ~2,8 stud de altura e 15 à frente. Pousa com as dianteiras, absorve, as traseiras chegam depois, e a respiração fica pesada. |
| Patada_D / Patada_E | O peso vai para as outras três patas (para o lado oposto e para trás) e a frente do corpo ergue. A pata sobe até a juba com o cotovelo alto e as garras recolhidas, desce em diagonal com as garras estendidas, varre para dentro e volta ao chão. Lábios erguidos e orelhas para trás. |
| Mordida | Avança 5 studs (patas dão um passo) com o pescoço estendido e a boca abrindo até 30°. Fecha rápido, sacode a cabeça, recua 3,5 studs com novos passos, e a boca relaxa. |
| Esquiva_E / Esquiva_D | Agacha, salta 4,5 studs para o lado (dianteiras juntas, traseiras logo depois), o corpo inclina para o lado, a cabeça fica no alvo e a cauda equilibra. Aterrissa absorvendo. |
| Fadiga_Recuperacao | Ofego com a boca entreaberta e a língua: a respiração passa de 1,35 para 0,4 Hz em ~4,5 s, a cabeça sobe aos poucos e os olhos se abrem. Serve para o fim de sequências intensas (a fraqueza oficial é o alto gasto de energia). |

### Evidência

- `review/E5_faseB_prancha.png`.
- Vídeos em `review/e5/faseB/<clipe>_{perfil,34}.mp4` e `_lento.mp4`.
- Close frontal e 3/4 do rosto (`<clipe>_rosto_frente*.mp4`, `_rosto_34*.mp4`) no Rugido, Rosnado, Intimidacao, Mordida e Fadiga.

### Achados e limitações

- **Patada:** a pata sobe até a altura da juba do peito, e parte do preparo fica escondida atrás da juba.
- **Orelhas:** quase não aparecem, porque ficam dentro da juba.
- **Bote:** uma almofada chega a −0,20 pouco antes do salto, quando o calcanhar sobe.
- **Esquiva:** as patas pousam em pares (dianteiras juntas, traseiras juntas). Avaliar no vídeo.
- **Variações de intensidade:** não fiz. O Rosnado cobre a ameaça leve e o Rugido, a completa.
- **Roblox:** importação, reprodução, skin com 4 influências e desempenho não foram testados.

### 8.1 Correção das patadas (r2, 05/11/2026): EM REVISÃO

O usuário aprovou a direção geral da E5, mas pediu correção obrigatória: em `Patada_D/E` a pata girava e torcia demais no golpe. A Fase B **não** está certificada até a revisão visual desta correção.

**Causa da torção (medida quadro a quadro com `build/e5/e5_40_diag_patada.py`):**
- **Punho por ângulo no mundo:** o metacarpo (`Mao`) era orientado por um ângulo fixo no mundo (`orientar` com os ângulos +70/+40/−40/−12 dos pontos de passagem), sem levar em conta para onde o antebraço apontava.
  - Com a pata erguida, o punho chegava a 155–160° de flexão, quase dobrado sobre si mesmo.
  - Nessa situação, a torção residual trocava de lado entre quadros: de +20° para −118° (Patada_E, q21–22) e de −54° para +106° (Patada_D), com saltos de ~50°/quadro.
- **Estalos nas pontas:** na decolagem, o ângulo pulava direto da regra do apoio para +70° (61–63°/quadro em q10).
  - Na troca de +40° para −40°, o ponto do punho (pata − metacarpo) também pulava, e o úmero girava 43–46°/quadro (q22).
- **Auxiliar herdava o defeito:** o `Punho_Aux` (metade da rotação da Mao) torcia até 42°.
- **Descartado como causa:**
  - Catmull-Rom: o caminho da pata era contínuo.
  - Troca de sinal de quaternion: 0 ocorrências.
  - `Cotovelo_Aux`: só flexão.
  - Gimbal: tudo é quaternion.

**Correção, só no gerador do Leão Solar (rig e pesos sem mudança):**
- **Modo de golpe (`posar_golpe` em `e5_20_clipes.py`), usado apenas por balanços com `rel`:**
  - punho e dedos giram só em X local (flexão/extensão), com torção e desvio zero;
  - o sinal da flexão é medido no repouso para cada lado, sem supor espelhamento de eixos;
  - nas pontas do balanço, a pose se mistura suavemente com a regra do apoio, sem estalo na decolagem nem no pouso;
  - o polo do cotovelo é o "para trás" girado pela flexão do ombro, então o cotovelo funciona como dobradiça estável;
  - o metacarpo real realimenta o alvo do punho (até 4 passadas).
- **Caminho da pata:** spline de Hermite com nós no tempo real de cada trecho (`hermite_nu`), com pausa curta na armada e no fim do seguimento.
- **Gesto (`e5_21_faseB.py`):**
  - **0–0,32 s:** o peso vai para as outras três patas e o peito/escápula começam o alcance (escápula 0,45).
  - **Decolagem e subida (0,32–0,76 s):** a pata sobe junto ao corpo e depois sobe à frente e para fora da juba, até a altura do queixo, com o punho dobrado (até 84°).
  - **Golpe (até 0,90 s):** diagonal rápida para baixo e para dentro. No contato, o punho estende (−4°), as garras abrem e as almofadas ficam voltadas para a frente e para baixo.
  - **Seguimento e retorno:** seguimento curto até 0,98 s com retração dos dedos; pouso macio à frente em 1,36 s.
  - **Tronco:** reage ao impacto (descida de 0,10, pitch e pescoço).
  - **Elevação do peito reduzida:** a v1 subia o ombro ~1,7 stud e forçava o corpo a baixar 2,5 studs. A r2 baixa só 0,67, por causa da transferência de peso.
  - A pata de apoio continua plantada.

**Ângulos da pata de golpe** (relativos ao osso pai; números mostram continuidade, não provam naturalidade):

```
Patada_D antes  | punho flexao max 159.6 | punho torcao max 105.9 | punho salto max  61.3/q | cotovelo flexao max 104.3 | cotovelo salto max  23.1/q | umero salto max  46.2/q | Punho_Aux torcao max  33.7
Patada_D depois | punho flexao max  83.7 | punho torcao max   3.5 | punho salto max  21.2/q | cotovelo flexao max  97.7 | cotovelo salto max  28.2/q | umero salto max  24.2/q | Punho_Aux torcao max   1.7
Patada_E antes  | punho flexao max 155.3 | punho torcao max 118.4 | punho salto max  62.8/q | cotovelo flexao max 106.8 | cotovelo salto max  24.1/q | umero salto max  43.5/q | Punho_Aux torcao max  42.1
Patada_E depois | punho flexao max  83.7 | punho torcao max   2.7 | punho salto max  21.2/q | cotovelo flexao max 100.7 | cotovelo salto max  28.6/q | umero salto max  22.0/q | Punho_Aux torcao max   1.4
```

Os maiores saltos que sobraram (punho ~21°/quadro, cotovelo ~28°/quadro, úmero ~24°/quadro) ficam nos quadros 26–27, que são o próprio golpe rápido. Gráfico: `review/e5/patada_r2/_angulos_antes_depois.png`.

**QA do gerador (r2):**
- **Erro do IK nas patas apoiadas:** 0.
- **Escorregamento p90 por quadro:**
  - pata de golpe antes de decolar e depois de pousar: 0,023 (D) e 0,019 (E);
  - outra dianteira: ≤ 0,001;
  - traseiras: 0.
- **Altura mínima da malha:** −0,07 (D) e −0,04 (E), na almofada quando o calcanhar sobe antes de decolar.
- **Pata de golpe:** chega a até 0,27 stud do caminho planejado no alto da armada (perna estendida ao máximo).
- **Inclinação da sola na armada:** a sola nunca vira para cima; a inclinação para fora é 0,33 (D) e 0,23 (E). Essa pequena diferença entre os lados vem do rig, que não é perfeitamente espelhado.

**Regressão:** Andar, Trote, Corrida, Bote, Mordida, Esquiva_E e Esquiva_D foram gerados de novo com o gerador r2. As chaves são idênticas às aceitas (diferença máxima 0,000000 em 261 canais; `build/e5/e5_42_comparar_acoes.py`). O modo novo só atua nas patadas.
- **Achado fora do escopo:** o **Bote** tem um estalo parecido na decolagem das dianteiras (Mao ~90°/quadro, Dedos ~100°/quadro em q19–20), porque ainda usa o ângulo no mundo da agenda. Não foi alterado, e corrigir depende de aprovação.

**Arquivos:**
- `Leao_Solar_Ref_E5_clipes_r2.blend`: 30 ações. `Leao_Patada_D/E` = r2; `Leao_Patada_D/E_v1` = versão anterior, para comparação.
- O `Leao_Solar_Ref_E5_clipes.blend` original ficou intacto.
- Scripts anteriores: `review/e5/patada_r2/scripts_antes/`.

**Evidência visual em `review/e5/patada_r2/`:**
- **Vídeos** `{antes,depois}_Patada_{D,E}_<vista>.mp4` e `_lento.mp4`, nas vistas:
  - `perfil`, `frente` e `34` (do lado do golpe);
  - `qa_livre` (baixa, de fora e à frente, sem a juba cobrindo);
  - `close` e `close_wire` (pata e punho com wireframe).
- **Folhas:** `_folha_Patada_{D,E}_antes_depois.png`, com preparo, maior elevação, pré-contato, contato, seguimento e recuperação.

**Pendências:**
- Revisão visual do usuário.
- A reação do tronco ao impacto é discreta.
- Nada testado no Roblox.

### 8.2 Patadas r3 (05/11/2026): pele do punho, APROVADAS em 05/11/2026

**Status:** o usuário aprovou as patadas r3 em 05/11/2026, o que fecha a **Fase B como aceita no Blender**.
- **Arquivo oficial:** `Leao_Solar_Ref_E5_clipes_r3.blend`, com as 28 ações da Fase A + B. As patadas `_r2` e `_v1` ficam só para comparação.
- **Rig oficial:** `Leao_Solar_Ref_E5_rig.blend`, com os pesos r3.
- **Roblox:** nada foi testado.

Na revisão da r2, o usuário mostrou um print em que a pata ainda "se contorce levemente" quando sobe para bater. Os ossos já não torciam; quem se deformava era a **pele**.

**Medição (`build/e5/e5_46_pele_punho.py`, zona com peso em `Mao`/`Punho_Aux`, comparada ao repouso):**
- **Compressão:** p2 do comprimento das arestas.
- **Dobra:** p99.5 da mudança do ângulo entre faces vizinhas.

| Versão | Patada_D | Patada_E |
|---|---|---|
| v1 (pesos antigos) | compressão 0,47 / dobra 158° | 0,46 / 153° |
| r2 (pesos antigos; é a do print) | 0,56 / 154° (q14–24) | 0,55 / 143° |
| r3 | 0,80 / 47° | 0,79 / 45° |

**Causas:**
1. **Pesos (principal):**
   - Vértices do antebraço e do punho, abaixo do cotovelo, tinham peso do **Peito** (até 0,6) e de ossos `Juba_*`. Isso veio do vazamento de pesos da juba do peito, que cai sobre o antebraço.
   - Com a pata erguida, a parte de trás do punho (almofada do carpo) ficava presa ao peito e vincava.
   - Os vértices piores estavam em (±2,5…2,75, −7,3…−7,8, 0,2…3,1), com Peito 0,14–0,25 e `Punho_Aux` 0,4–0,7.
2. **Pose:** a r2 mantinha o punho em 75–84° de flexão por ~10 quadros na subida. Mesmo sem torção, isso fecha demais a pele.

**Correção:**
- **Pesos** (`build/e5/e5_15_pesos_antebraco.py`):
  - em vértices com ≥ 0,3 de peso na parte baixa da perna, o peso de outros ossos sai abaixo de z 4,4, com transição até z 5,4 (o cotovelo está em z 5,2);
  - o peso tirado vai para os ossos da própria perna, na mesma proporção;
  - 66 vértices mudaram na DD e 74 na DE;
  - continua no máximo 4 influências por vértice e 0 vértices sem peso.
- **Rig:**
  - aplicado em `Leao_Solar_Ref_E5_rig.blend`;
  - versão anterior guardada em `e5/Leao_Solar_Ref_E5_rig_v2_antes_pesos_punho.blend`;
  - ossos, nomes e juntas não mudaram.
- **Pose:**
  - flexão do punho limitada a ~40° na subida e na armada;
  - dedos menos fechados (6°);
  - o resto do gesto r2 foi mantido (caminho, tempos, contato, impacto).

**Ângulos da pata de golpe, v1 x r3:**

```
Patada_D v1     | punho flexao max 159.6 | punho torcao max 105.9 | punho salto max  61.3/q | cotovelo flexao max 104.3 | cotovelo salto max  23.1/q | umero salto max  46.2/q | Punho_Aux torcao max  33.7
Patada_D r3     | punho flexao max  40.7 | punho torcao max   3.5 | punho salto max  12.4/q | cotovelo flexao max  98.0 | cotovelo salto max  26.0/q | umero salto max  21.0/q | Punho_Aux torcao max   1.7
Patada_E v1     | punho flexao max 155.3 | punho torcao max 118.4 | punho salto max  62.8/q | cotovelo flexao max 106.8 | cotovelo salto max  24.1/q | umero salto max  43.5/q | Punho_Aux torcao max  42.1
Patada_E r3     | punho flexao max  40.7 | punho torcao max   2.7 | punho salto max  12.8/q | cotovelo flexao max  99.5 | cotovelo salto max  26.2/q | umero salto max  18.9/q | Punho_Aux torcao max   1.4
```

**Regressão:**
- **Chaves:** Andar, Trote, Corrida, Bote, Mordida e Esquiva_E/D, gerados de novo com o rig r3, têm chaves idênticas às aceitas (diferença 0 em 261 canais).
- **QA do gerador, igual ao aceito:**

  | Clipe | Escorregamento p90 | zmin |
  |---|---|---|
  | Andar | ≤ 0,009 | −0,07 |
  | Trote | ≤ 0,021 | −0,07 |
  | Corrida | ≤ 0,031 | −0,23 |
  | Bote | ≤ 0,023 | −0,20 |
  | Mordida | ≤ 0,024 | −0,07 |
  | Esquivas | ≤ 0,025 | −0,06 |

- **Pele do punho também melhorou nesses clipes** (dobra p99.5 da DD, pesos antigos → r3):

  | Clipe | Pesos antigos | r3 |
  |---|---|---|
  | Andar | 147° | 51° |
  | Trote | 155° | 57° |
  | Corrida | 149° | 62° |
  | Bote | 135° | 72° |
  | Mordida | 141° | 66° |
  | Esquivas | 70° | 48–62° |

  Como os pesos mudaram, a deformação de todos os clipes (Fase A incluída) fica um pouco diferente, só no antebraço e no punho das dianteiras. Vale uma olhada nos vídeos.

**Arquivos:**
- `Leao_Solar_Ref_E5_clipes_r3.blend`: pesos r3 e 32 ações. `Leao_Patada_D/E` = r3; `_r2` e `_v1` guardadas para comparação.
- Os arquivos `Leao_Solar_Ref_E5_clipes.blend` e `_r2.blend` ficaram como estavam.

**Evidência em `review/e5/patada_r3/`:**
- vídeos `r3_Patada_{D,E}_{perfil,frente,34,qa_livre,close,close_wire}.mp4` e `_lento`;
- folhas `_folha_Patada_{D,E}_r2_r3.png`;
- close da subida com wireframe `_close_subida_Patada_{D,E}_r2_r3.png`;
- gráfico `_angulos_v1_r3.png`.

**Pendências:**
- Revisão visual do usuário.
- O estalo do Bote na decolagem continua fora do escopo.
- Nada testado no Roblox.

### 8.3 Bote r2 (05/11/2026): dianteiras sem estalo, EM REVISÃO

O usuário pediu: "Corrija o bote". O Bote v1 (aprovado na Fase B) tinha um estalo nas patas da frente, achado na revisão das patadas.

**Medição v1 (`e5_40_diag_patada.py`):**
- **Decolagem (q19–20):** num único quadro, o punho girava ~90°, o cotovelo 63–66°, o úmero ~27° e os dedos 52–102°.
- **Voo:** os dedos ficavam dobrados por baixo (74–87°).
- **Antes do pouso (q31–32):** novos saltos de 18–38°/quadro.

**Causas:**
1. **Punho por ângulo no mundo:** era o mesmo modo da Patada v1 (−30° no mundo), e a pata trocava da regra de apoio para a do balanço sem transição.
2. **Agachamento solto de uma vez:** o tronco saía do agachamento em 0,08 s, subindo 1,5 stud em ~3 quadros. O amortecimento do pouso também era de 0,08 s.
3. **Alvo fora do alcance:** no voo, o ombro sobe ~4,8 studs (pitch e curva da coluna) e anda 15. Um alvo relativo ao chão ou à translação do tronco ficava longe demais, e a perna "travava" esticada de um quadro para o outro.

**Correção (só o Bote; as outras 27 ações têm chaves idênticas, diferença 0 em 261 canais):**
- **Modo relativo das patas da frente** (o mesmo da Patada r3): punho e dedos só flexionam, o cotovelo funciona como dobradiça e a pose se mistura com o apoio nas pontas do balanço.
- **Meio do balanço em relação ao ombro real** (`via_ombro`): a pata recolhe sob o peito ao decolar, estica à frente no voo e desce para o pouso.
  - Decolagem e pouso continuam presos no chão (caminho no mundo).
  - O alcance satura de forma suave, sem a perna travar esticada.
  - A sola, incluindo a almofada do carpo, não entra no chão.
- **Tronco:**
  - o agachamento solta em 0,22 s (era 0,08);
  - o amortecimento do pouso leva 0,18 s (era 0,08);
  - a DE decola 0,02 s antes, em 0,60 s.
- **Dedos:** fecham um pouco ao recolher e abrem antes do pouso.

**Ângulos das patas da frente** (graus; "salto" = maior variação entre quadros):

```
Bote DD v1     | punho flexao max  61.1 | punho torcao max  11.4 | punho salto max  89.7/q | cotovelo flexao max  79.8 | cotovelo salto max  63.3/q | umero salto max  26.3/q | Punho_Aux torcao max   5.3
Bote DD r2     | punho flexao max  56.1 | punho torcao max  10.4 | punho salto max  14.7/q | cotovelo flexao max  68.4 | cotovelo salto max  21.2/q | umero salto max  14.5/q | Punho_Aux torcao max   4.9
Bote DE v1     | punho flexao max  57.7 | punho torcao max  16.0 | punho salto max  90.3/q | cotovelo flexao max  82.6 | cotovelo salto max  65.9/q | umero salto max  27.0/q | Punho_Aux torcao max   7.5
Bote DE r2     | punho flexao max  53.8 | punho torcao max  13.8 | punho salto max  22.9/q | cotovelo flexao max  71.5 | cotovelo salto max  31.0/q | umero salto max  15.9/q | Punho_Aux torcao max   6.5
```

- **Dedos:** salto máximo de 52–102 caiu para 16–17°/quadro.
- **Pele do punho** (dobra p99.5): de 72° (DD) e 91° (DE) para 39°.

**QA do gerador:**
- erro do IK no apoio: 0;
- pata da frente até 0,27 stud do caminho planejado;
- escorregamento p90: ≤ 0,023;
- altura mínima da malha: −0,06 (antes −0,20);
- pousos: DD q35, DE q37, TD q40, TE q42.

**Arquivos:**
- `Leao_Solar_Ref_E5_clipes_r4.blend`: 33 ações. `Leao_Bote` = r2; `Leao_Bote_v1` = o aprovado antes; Patadas r3 com `_r2`/`_v1`.
- `Leao_Solar_Ref_E5_clipes_r3.blend` ficou como estava.
- `e5_15_pesos_antebraco.py` agora não aplica duas vezes: marca a malha com `pesos_punho_r3`, já marcada no rig e no r3.

**Evidência em `review/e5/bote_r2/`:**
- vídeos `r2_Bote_v1_*` e `r2_Bote_*`, nas vistas perfil, frente, 3/4, qa_livre, close e close_wire, normal e `_lento` (câmera acompanha a raiz);
- folha `_folha_Bote_v1_r2.png`;
- gráfico `_angulos_bote_v1_r2.png`.

**Pendências:**
- Revisão visual do usuário.
- Saltos de até 31°/quadro no cotovelo da DE na decolagem: é o empurrão, mais rápido que o resto.
- As traseiras do Bote não foram alteradas.
- Nada testado no Roblox.

### 8.4 Bote r3 (05/11/2026): impulso das traseiras e alcance de 45 studs, EM REVISÃO

**Pedido do usuário:** mais movimento das traseiras ("parecer que ele está se impulsionando"); a perna de trás dobra um pouco e "pula com tudo, como um leão mesmo"; o bote terá uma mira, com alcance limitado mas grande, e seguirá a mira.
- **Alcance máximo escolhido pelo usuário:** ~45 studs, cerca de 2 corpos; o leão tem ~24 studs.

**Referências pesquisadas** (só princípios, nada copiado):
- **Gatos:** no salto, a fase de lançamento das traseiras dura ~150 ms. Os extensores disparam do quadril para o tornozelo (proximal → distal), depois de uma preparação que carrega o salto.
  - Fonte: *Hindlimb muscular activity, kinetics and kinematics of cats jumping to their maximum achievable heights*, J. Exp. Biol. 91:73 (resumo).
- **Lagartos e rãs:** a extensão de quadril/joelho/tornozelo e a retração da coxa produzem a maior parte do trabalho do salto.
- **Distância do leão:** fontes de divulgação citam ~10–12 m na horizontal (~4 corpos). Aqui o salto fica limitado a 45 studs, por escolha do usuário.

**Gesto (91 quadros, 3,0 s, deslocamento de 45 studs):**
1. **Agachamento (0,05–0,52 s):** o quadril baixa e recua sobre as traseiras dobradas (z −1,9, quadril 1,3 para trás, pitch −2,5°), a coluna carrega, o quadril "rebola" e a cabeça fica baixa com o olhar fixo na mira.
2. **Impulso (0,52–0,77 s):** o tronco avança, a coluna estende e as dianteiras saem primeiro (0,62/0,65 s).
   - O calcanhar das traseiras sobe até 62° nos últimos 0,28 s do apoio: o leão empurra na ponta dos dedos.
   - A coxa e a canela estendem e a perna sai **esticada atrás** (TE 0,73 s, TD 0,75 s).
3. **Voo (0,76–1,65 s):** voo balístico de ~7 studs de altura.
   - As dianteiras estendem à frente, relativas ao ombro.
   - As traseiras saem esticadas e **recolhem sob a barriga**, relativas ao quadril, com o jarrete fechando.
   - A cauda equilibra.
4. **Pouso:** as dianteiras pousam em q51/52, as traseiras em q57/58, e o amortecimento leva 0,16 s; depois vem a respiração pesada.

**Mira (lado da animação):**
- **Gerador paramétrico:** `vel_bote(t, dist)` e `altura_bote(dist)`. Com a mira mais perto, o tempo de voo é o mesmo e o arco fica mais baixo (variante de teste `Bote_Mira25`, só para revisão, gerada com `E5_BOTE_MIRA=25`).
- **Lado do jogo (ainda não feito):** precisa de autorização e do Studio livre.
  - virar o leão para o ponto mirado;
  - limitar a distância a 45 studs;
  - escalar o deslocamento do voo do clipe "no lugar".

**Mudanças no gerador (`e5_20_clipes.py`, só ativas no Bote; as outras 27 ações têm chaves idênticas):**
- **`empurra` / `t_emp`:** o calcanhar da pata apoiada sobe até o ângulo dado antes de decolar, e o balanço parte desse ângulo, sem salto.
- **`via_quadril`:** o meio do balanço da traseira segue o quadril real. A traseira também ganhou limite suave de alcance (sem travar esticada).
- **`jarrete`:** no voo, metatarso e dedos da traseira só flexionam em relação à canela. O ângulo no mundo torcia ~40° ao recolher.
- **Passadas extras:** para o metatarso relativo e para a checagem da sola.
- **`dmin_tras=0.55` no Bote:** sem isso, a regra de extensão mínima não deixava a TE recolher.

**Ângulos (r2 15 studs x r3 45 studs; "salto" = maior variação entre quadros):**

```
== Leao_Bote_r2 DD
  Umero_DD         torcao_max    0.0 (q1)  flexao_max   34.8  salto_max  14.5 (q25)  trocas_sinal 0
  Antebraco_DD     torcao_max    0.0 (q1)  flexao_max   68.4  salto_max  21.2 (q25)  trocas_sinal 0
  Mao_DD           torcao_max   10.4 (q17)  flexao_max   56.1  salto_max  14.7 (q23)  trocas_sinal 0
  Dedos_DD         torcao_max    2.9 (q18)  flexao_max   21.8  salto_max  16.1 (q20)  trocas_sinal 0
== Leao_Bote_r2 DE
  Umero_DE         torcao_max    0.0 (q1)  flexao_max   34.2  salto_max  15.9 (q22)  trocas_sinal 0
  Antebraco_DE     torcao_max    0.0 (q1)  flexao_max   71.5  salto_max  31.0 (q20)  trocas_sinal 0
  Mao_DE           torcao_max   13.8 (q17)  flexao_max   53.8  salto_max  22.9 (q20)  trocas_sinal 0
  Dedos_DE         torcao_max    2.1 (q18)  flexao_max   21.9  salto_max  16.1 (q21)  trocas_sinal 0
== Leao_Bote_r2 TD
  Coxa_TD          torcao_max    0.0 (q1)  flexao_max   32.8  salto_max  12.2 (q22)  trocas_sinal 0
  Canela_TD        torcao_max    0.0 (q1)  flexao_max   65.4  salto_max  28.2 (q24)  trocas_sinal 0
  Metatarso_TD     torcao_max   17.6 (q29)  flexao_max   81.6  salto_max  25.8 (q31)  trocas_sinal 0
  Dedos_TD         torcao_max    1.4 (q21)  flexao_max   16.5  salto_max  10.8 (q25)  trocas_sinal 0
== Leao_Bote_r2 TE
  Coxa_TE          torcao_max    0.0 (q1)  flexao_max   29.0  salto_max  18.2 (q22)  trocas_sinal 0
  Canela_TE        torcao_max    0.0 (q1)  flexao_max   45.2  salto_max  39.6 (q22)  trocas_sinal 0
  Metatarso_TE     torcao_max   17.8 (q30)  flexao_max   73.5  salto_max  25.9 (q22)  trocas_sinal 0
  Dedos_TE         torcao_max    1.3 (q22)  flexao_max   31.2  salto_max  21.8 (q23)  trocas_sinal 0
== Leao_Bote DD
  Umero_DD         torcao_max    0.0 (q1)  flexao_max   41.4  salto_max  16.8 (q24)  trocas_sinal 0
  Antebraco_DD     torcao_max    0.0 (q1)  flexao_max   84.2  salto_max  28.5 (q24)  trocas_sinal 0
  Mao_DD           torcao_max    9.8 (q17)  flexao_max   58.5  salto_max  17.7 (q50)  trocas_sinal 0
  Dedos_DD         torcao_max    2.9 (q19)  flexao_max   21.7  salto_max  10.7 (q22)  trocas_sinal 0
== Leao_Bote DE
  Umero_DE         torcao_max    0.0 (q1)  flexao_max   41.5  salto_max  17.5 (q25)  trocas_sinal 0
  Antebraco_DE     torcao_max    0.0 (q1)  flexao_max   86.6  salto_max  38.0 (q20)  trocas_sinal 0
  Mao_DE           torcao_max   13.5 (q52)  flexao_max   50.1  salto_max  21.3 (q20)  trocas_sinal 0
  Dedos_DE         torcao_max    2.1 (q20)  flexao_max   21.9  salto_max  12.5 (q23)  trocas_sinal 0
== Leao_Bote TD
  Coxa_TD          torcao_max    0.0 (q1)  flexao_max   39.5  salto_max  20.2 (q26)  trocas_sinal 0
  Canela_TD        torcao_max    0.0 (q1)  flexao_max   67.5  salto_max  22.6 (q26)  trocas_sinal 0
  Metatarso_TD     torcao_max   15.8 (q20)  flexao_max   75.7  salto_max  24.7 (q19)  trocas_sinal 0
  Dedos_TD         torcao_max    6.0 (q23)  flexao_max   61.7  salto_max  24.0 (q25)  trocas_sinal 0
== Leao_Bote TE
  Coxa_TE          torcao_max    0.0 (q1)  flexao_max   51.0  salto_max  25.7 (q23)  trocas_sinal 0
  Canela_TE        torcao_max    0.0 (q1)  flexao_max   75.8  salto_max  30.9 (q23)  trocas_sinal 0
  Metatarso_TE     torcao_max   11.5 (q23)  flexao_max   68.2  salto_max  31.1 (q19)  trocas_sinal 0
  Dedos_TE         torcao_max    5.5 (q22)  flexao_max   61.6  salto_max  24.8 (q25)  trocas_sinal 0
```

| Traseira | Amplitude da coxa | Amplitude da canela | Maior altura da pata |
|---|---|---|---|
| r2 | 29–31° | 45–60° | 2,4 studs |
| r3 | 38–51° | 62–76° | 10–11 studs |

Os maiores saltos (~31°/quadro) ficam no próprio empurrão e na decolagem.

**QA do gerador:**
- erro do IK no apoio: 0;
- pata da frente até 0,77 stud do caminho planejado no alcance do voo, porque a perna satura de forma suave;
- escorregamento p90: dianteiras ≤ 0,024 e traseiras 0,05. Nas traseiras são os dedos rolando quando o calcanhar sobe, não a pata deslizando;
- altura mínima da malha: −0,13, nos dedos da TE apertando o chão no empurrão.

**Arquivos:**
- `Leao_Solar_Ref_E5_clipes_r5.blend`: `Leao_Bote` = r3; `Leao_Bote_r2` e `Leao_Bote_v1` guardados.
- Scripts anteriores em `review/e5/bote_r3/scripts_antes/`.

**Evidência em `review/e5/bote_r3/`:**
- vídeos `r3_Bote_r2_*` e `r3_Bote_*`, nas vistas perfil, frente, 3/4, qa_livre, close, close_wire, `close_tras` e `close_tras_wire`, normal e `_lento`;
- `r3_Bote_Mira25_{perfil,34}`;
- folha `_folha_Bote_r2_r3.png`.

**Pendências:**
- Revisão visual do usuário.
- A mira e o limite de 45 studs no jogo ainda não foram feitos.
- Nada testado no Roblox.

### 8.5 Bote r4 (05/11/2026): agachamento mais fundo, APROVADO em 05/11/2026

**Status:** aprovado pelo usuário no Blender.
- **Arquivo oficial dos clipes:** `Leao_Solar_Ref_E5_clipes_r6.blend`, com as 28 ações da Fase A + B. Bote r4, Patadas r3; as versões anteriores (`_r3`, `_r2`, `_v1`) ficam só para comparação.
- **Rig oficial:** `Leao_Solar_Ref_E5_rig.blend`.
- **Roblox:** nada foi testado. A mira de 45 studs no jogo ainda não foi feita.

O usuário pediu: "Quero que ele abaixe mais antes de dar o bote".

**Mudança (só em `c_bote`, `e5_21_faseB.py`):**
- o agachamento foi de **1,9 para 2,9 studs**;
- o quadril recua 1,5 stud (era 1,3);
- tempos, impulso, voo, pouso e alcance de 45 studs continuam iguais ao r3.

**Limite medido:** com 3,2 studs o peito atravessava o chão (−0,13 no q15). Com 2,9 studs o peito fica acima dele, e o ponto mais baixo da malha volta a ser os dedos da traseira apertando o chão no empurrão (−0,13 no q20, igual ao r3).

**QA:**
- erro do IK no apoio: 0;
- escorregamento p90: dianteiras ≤ 0,023, traseiras 0,05 (dedos rolando no empurrão);
- pele do punho: dobra p99.5 ≤ 41°.
- **Saltos máximos por quadro:** agora no empurrão, porque a perna estende mais no mesmo tempo:
  - cotovelo DD: 38° (era 28°);
  - canela TE: 36° (era 31°);
  - metatarso TE: 37° (era 31°).
- **Regressão:** gerei de novo os 28 clipes e só o Bote mudou.

**Arquivos:**
- `Leao_Solar_Ref_E5_clipes_r6.blend`: `Leao_Bote` = r4; `Leao_Bote_r3`, `_r2` e `_v1` guardados.
- A variante de teste `Bote_Mira25` em `review/e5/bote_r3/mira25/` foi feita com o agachamento do r3.

**Evidência em `review/e5/bote_r4/`:**
- vídeos `r4_Bote_r3_*` e `r4_Bote_*`, nas vistas perfil, frente, 3/4, qa_livre, close, `close_tras` e `close_tras_wire`, normal e `_lento`;
- folha `_folha_Bote_r3_r4.png`.

**Pendências:**
- Revisão visual do usuário.
- A mira e o limite de 45 studs no jogo ainda não foram feitos.
- Nada testado no Roblox.

## 9. Fase C (11/11/2026): clipes de vida (comer, beber, deitar, dormir...), EM REVISÃO
Pedido do usuário: "faca isto" (os clipes de vida que faltavam). Só movimento, nomes neutros, sem VFX/dano/alcance. Blender apenas; **Roblox não testado**.

### Gerador
- Novo módulo `build/e5/e5_23_vida.py` (executado pelo `e5_20_clipes.py` depois do módulo da montaria).
- `e5_20`: novas chaves de corpo `meta_dian` / `meta_tras` (dobra do metacarpo/metatarso nas patas apoiadas, padrão 0) e `pes_ini` no clipe (pés já fora do repouso no quadro 1, para os loops deitado/sentado).
- Convenção medida (varredura): `pesc` **negativo abaixa o pescoço**.
- **Regressão:** os 32 clipes existentes, gerados de novo com o gerador alterado, têm diferença **0,000000** em 261/261 canais contra `Leao_Solar_Ref_E5_clipes_r8.blend` (`e5_42_comparar_acoes.py`).

### Clipes novos (15) em `Leao_Solar_Ref_E5_clipes_r9.blend` (= r8 + 15, 54 ações; r8 preservado)
| Clipe | s | loop | IK | escorr. p90 | malha zmin | obs. |
|---|---|---|---|---|---|---|
| Beber | 6,2 | não | 0 | 0,0002 | −0,005 | pescoço −85°, língua 2,6 Hz; cabeça a 0,58 do chão |
| Comer | 7,2 | não | 0 | 0,0002 | −0,005 | 3 ciclos morde/puxa + mastigar |
| Bocejar | 3,6 | não | 0 | 0,0001 | −0,006 | |
| Lamber_Pata | 5,4 | não | 0 | 0,022 | −0,065 | boca–pata 1,95; erro do caminho da pata 1,85 (parte fora do alcance) |
| Espreguicar | 5,4 | não | 0 | 0,025 | −0,10 | juba do peito roça o chão |
| Reacao_Golpe_E / _D | 1,6 | não | 0 | 0,002 | −0,01 | |
| Deitar | 4,0 | não | 0 | 0,022 | −0,44 | |
| Descanso_Deitado | 6,0 | sim (emenda 0°) | 0 | 0 | −0,51 | |
| Dormir | 8,0 | sim (emenda 0°) | 0 | 0 | −0,62 | olhos fechados |
| Levantar | 3,0 | não | 0 | 0,015 | −0,42 | |
| Sentar | 2,6 | não | 0 | 0,015 | −0,57 | |
| Sentado | 5,0 | sim (emenda 0,07°) | 0 | 0 | −0,70 | |
| Levantar_Sentado | 2,0 | não | 0 | 0,018 | −0,67 | |
| Morte | 3,4 | não | 0 | 0,019 | −0,43 | cai de lado |

### Achados e correções (C2)
- 1ª geração: tufo da cauda até **−7,5** abaixo do chão (cauda reta pendurada). Corrigido: cauda deitada e curvada para o lado (`cauda_base` +12°/+26°, `cauda_yaw` +35°/+45°), subindo já no agachar.
- Metacarpo −80° enterrava punho/mão 1,7; corpo baixo enterrava o peito 1,7. Ajustado: deitado z −3,2, metacarpo −25°, metatarso −50°; sentado z −5,0, metatarso −45°.
- Morte: o peito batia no chão (−1,97) com o nariz para baixo na queda; pitch agora −4°.
- Restante no chão: −0,4 a −0,7 = peito/coxa/mão **apoiados** (contato, não atravessamento visível); perna traseira dobrada encosta na barriga até 0,85 (esperado com a perna sob o corpo). Conferir nos vídeos.

### Evidência
Vídeos em `review/c/c1/` e `review/c/c2/` (perfil, 3/4, frente; tempo real e lento). Binários fora do git.

### 9.1 Revisão r2 (11/11/2026), pedido do usuário com 3 referências (sentado, dormindo com a cabeça nas patas, deitado lambendo a pata)
Pedido: sentar com a garupa no chão; dormir e morrer de olhos fechados; dormir igual à referência (antebraços deitados, cabeça entre as patas); espreguiçar com a pata da frente esticada; lamber a pata deitado; parar de arregalar o olho; movimento nos olhos.

**Olhos (todos os clipes):**
- Achado: no osso `Palpebra_*`, a rotação **negativa** arregalava o olho e rasgava a pele acima dele, e a positiva fecha (+30° fecha limpo; medido em close).
- A convenção dos clipes continua `palp −42 = fechado`. O `posar` agora aplica `palp × PALP_K` (`PALP_K = −30/42`).
- Piscadas automáticas em todos os clipes: a cada 3,1 s a partir de 0,7 s, com 0,18 s, sem cruzar o fim do clipe. A chave `piscar_auto=False` desliga.
- Dormir: a dobra de ~95° entre o pescoço e a cabeça (pesc −90 / cabeça nivelada) esticava a pálpebra (há pesos do `Pescoco2` nela). Mesmo o osso a +57° não fechava. Passar o peso para a Cabeca só no teste não resolveu.
  - Correção na pose: pesc −55 e focinho −30. Close conferido: olho fechado, queixo nas patas.

**Pose deitada:**
- Nova chave de corpo `esc_sobe`: a escápula desce em relação ao tronco, gravada só nos clipes com `escapula_loc=True` (deitado/sentado/espreguiçar/lamber).
- Deitado: corpo z −5,7, pitch −7,5, escápula −1,0, mãos à frente (y −6,5), metacarpo −50. Antebraço quase rente ao chão, como na referência.
- Traseiras: pés (±1,4, −4, 0), metatarso −64 (com −85 o jarrete entrava no chão).

**Outros clipes:**
- Sentar/Sentado/Levantar_Sentado: garupa no chão (z −7,4, pitch −28, escápula −1,4, pés traseiros (±1,4, −3,5), metatarso −64); cauda 40/28.
- Espreguicar: as duas mãos dão um passo à frente (y −7,0) com a perna esticada; o corpo desce junto do passo e a garupa fica alta (pitch 15).
- Lamber_Pata: refeito **deitado**. A pata direita sobe até a boca (punho 75°, escápula sobe 0,38), com a cabeça virada e lambidas em 1,3 Hz.
- Morte: pose final mantida (constantes próprias `MORTE`); olhos fecham pela correção do sinal.

**QA (gerador):**
- Mínimo da malha: −1,3 a −1,5 nos deitados (peito/juba apoiados e comprimidos no chão; é o custo do antebraço rente) e ≈ −1,0 nos sentados (coxa).
- Perna dentro do corpo até 1,08 no sentado (coxa dobrada contra a barriga).
- Deitar: IK 0,075, escorregamento 0,054. Descanso_Deitado: emenda 0,5°.

**Regressão por osso:**
- Nos 32 clipes anteriores, só `Palpebra_D/E` mudaram (correção intencional).
- No r10 contra o r9: Bote_r3 e os históricos ficaram idênticos; Dormir do r10 = gen4.

**Arquivos:**
- `Leao_Solar_Ref_E5_clipes_r10.blend` (54 ações = r9 com os 47 atuais trocados; históricos `_v1/_r2/_r3` mantidos; r9 preservado).
- Script de montagem `build/e5/e5_44_versao_r10.py`.

**Evidência:**
- Vídeos em `review/c/c3/` (perfil, 3/4, rosto) e `review/c/c4/` (Dormir final).
- Folhas `review/c/folha_C3a/b/c.png`, `folha_C3_rosto.png`, `folha_C4_dormir*.png`.

**Status:** APROVADA pelo usuário em 11/11/2026 (Blender), junto com o Dormir r3 (9.2). Roblox não testado.

### 9.2 Dormir r3 (11/11/2026): corpo todo no chão, pernas relaxadas, APROVADO pelo usuário em 11/11 (Blender)
Pedido do usuário: "quero que suas pernas relaxem, não fiquem em posição de esforço... quero seu corpo todo no chão".

**Pose:**
- Quadril tombado para o lado E (`roll` −55°). O peito volta 30° (`peito_roll`) e fica de esfinge, com a cabeça nas patas.
- Corpo 0,75 mais baixo.
- Traseiras soltas e deitadas para o lado D (`PES_DORM`: TD (4,5, −4, 0,3), TE (6, −1, 0,3), pata girada 70°).
- Cauda curvada junto das patas (base −20°, giro 50°).

**Gerador:**
- `e5_20` aceita `pes_yaw` por pata no início do clipe (padrão 0, sem efeito nos outros clipes).
- A pose foi escolhida em testes estáticos (`teste_dorm`, variantes r1–r6). O sentido do tombo foi conferido: a barriga fica virada para o lado das patas.

**QA:**
- Quadril a 1,4 do chão. A coxa de baixo encosta no chão; o flanco E deita no chão.
- O peito fica −2,0 dentro do chão (compressão do apoio).
- Olhos continuam fechados (close).
- Perna dentro do corpo: 2,1 / 1,5, das traseiras deitadas encostadas na barriga. A medida já se mostrou instável; conferir no vídeo.

**Limitações:**
- O tufo da cauda fica de pé entre as patas. Parte da cauda fica até −1,3 abaixo do chão; o controle da cauda é uniforme e não deita a cadeia no chão.
- A pose do Dormir agora é diferente da do Descanso_Deitado (esfinge). A troca entre os dois depende da mistura do jogo; um clipe de transição pode ser feito depois.

**Arquivos e evidência:**
- `Leao_Solar_Ref_E5_clipes_r10.blend` (Dormir trocado; conferido igual ao gerado).
- Vídeos em `review/c/c5/` (lado D: perfil, 3/4, rosto; lado E: perfil, 3/4).

### 9.3 Realismo extra (11/11/2026): cauda deitada, transições do sono, pulo, nado e encosta. APROVADO pelo usuário em 11/11 (Blender)
Pedido do usuário: "siga com o 2" (opcionais de realismo). Só movimento; Blender apenas; **Roblox não testado**.

**Gerador (`e5_20`), todas as opções desligadas por padrão:**
- `cauda_seg`: (pitch, yaw) por segmento da cauda, misturado com a postura uniforme por `cauda_mix`.
- `cauda_chao`: ajuste por quadro que ergue cada segmento o mínimo necessário para a cauda e o tufo não entrarem no chão.
- Balanço da agenda com `yaw` (a pata gira).
- `inclinacao` (graus): o chão e a raiz sobem ao longo da rampa (`chao_z`). As duas travas de "pata acima do chão" no balanço passaram a usar o chão inclinado; sem isso, as patas da frente ficavam presas no plano na descida.
- Render: `E5_INCLINACAO` (rampa) e `E5_AGUA` (superfície da água).
- Módulo novo `build/e5/e5_24_extra.py`.

**Clipes:**
- **Dormir (cauda):** a cauda sai do quadril, desce ao chão e contorna o lado das patas. Ângulos por busca gulosa por segmento (`CAUDA_DORM`). O tufo não fica mais de pé.
- **Deitado_para_Dormir / Dormir_para_Deitado (4 s):**
  - mistura do Descanso_Deitado (esfinge) com o Dormir r3;
  - as traseiras escorregam para o lado da barriga (e voltam);
  - ao acordar, os olhos abrem depois de a cabeça se mexer;
  - sem o ajuste, a cauda chegava a −6,8 dentro do chão no meio do tombo; com ele, o tufo fica até −1,6, compressão do penacho.
- **Pular_Obstaculo (2,8 s):** o mesmo impulso, voo e pouso do Bote r4 aprovado, com 16 studs de distância, arco de 6,5, agachamento menor, boca fechada e orelhas à frente.
- **Nadar (loop, 4,5 studs/s) / Nadar_Parado (loop):** "nado de cachorro" do leão real:
  - cabeça alta e dorso rente à superfície;
  - dianteiras em remada alternada: sobe dobrada até sob o queixo, estica à frente e puxa com a pata aberta;
  - traseiras chutam em diagonal com a dianteira oposta;
  - cauda boiando e boca bufando no ritmo.
  - Na r2 a remada foi ampliada (a 1ª parecia andar debaixo d'água) e o chute para trás foi reduzido: a canela TE virava 50° na emenda.
- **Subir_Encosta / Descer_Encosta (loop, rampa de 20°):** o tronco inclina junto (pitch ±20°), a cabeça olha ao longo da rampa e a passada fica mais curta (82%). Na descida o corpo desce até 1,13 quando as dianteiras não alcançam.

**QA:**

| Clipe | IK | escorr. p90 | emenda | obs. |
|---|---|---|---|---|
| Deitado_para_Dormir | 0 | 0,011 | — | emenda com o Dormir: cauda 5° (fase da onda), resto < 0,5° |
| Dormir_para_Deitado | 0 | 0,011 | — | emenda com o Dormir: 0,2° |
| Pular_Obstaculo | 0 | 0,05 | — | erro do caminho das dianteiras 0,97 (como no Bote, partes fora do alcance) |
| Nadar | 0 | — | 0° | |
| Nadar_Parado | 0 | — | 0° | |
| Subir_Encosta | 0 | 0,009 | 0° | |
| Descer_Encosta | 0 | 0,009 | 8,7° (úmero DE; salto interno 8,3°) | |

- A altura mínima da malha não vale para a encosta (medida contra z=0).

**Para o jogo:**
- A raiz sobe/desce na encosta e anda no nado. Na conversão "no lugar" para o Roblox, a translação da raiz sai inteira, como nos clipes de marcha.
- A posição na água (altura da superfície) é do jogo.

**Arquivos e evidência:**
- `Leao_Solar_Ref_E5_clipes_r11.blend`.
- Vídeos em `review/c/c8/` (sono), `review/c/c7/` (pulo e encostas), `review/c/c9/` (nado r2).
- Folhas `review/c/folha_C8_sono.png`, `folha_C7a/b.png`, `folha_C9_nado.png`.
