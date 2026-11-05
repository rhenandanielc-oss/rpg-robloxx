# Leão Solar — E3b, correção da boca e da junção da mandíbula (03/11/2026, em avaliação)

- **Base:** `Leao_Solar_Ref_E3_t2.blend` (cópia da v11 com a topologia e os antebraços da E3, antes da boca).
- **Preservados sem alteração** (datas dos arquivos conferidas):
  - `Leao_Solar_Ref_E2_v11.blend` (aprovada, 16:09);
  - `Leao_Solar_Ref_E3.blend` (E3 anterior, 16:55).
- **Entrega:** `Leao_Solar_Ref_E3b.blend`. O intermediário `Leao_Solar_Ref_E3b_t8.blend` é a mesma geometria com o albedo antigo.
  - Apaguei as iterações de teste t1–t7, criadas nesta tarefa.
- **Scripts:** `build/e3c/`
  - `c02_boca.py`: boca;
  - `c03_render.py`: poses, vistas e medições;
  - `c05_antebracos.py`: membros;
  - `c06_video.py`: vídeo;
  - `c07_nm_posicoes.py`: restos não-manifold;
  - `c08_prancha.py`: prancha.
- Tudo é render e auditoria **no Blender** (EEVEE, luz neutra das pranchas). **Nada foi testado no Roblox.**

## Entregas
| Arquivo | Conteúdo |
|---|---|
| `review/E3b_prancha.png` | 1. Boca fechada: referência \| E2 v11 \| E3 anterior \| E3b (perfil e frente)<br>2. Aberta 10°/20°/32°: E3 × E3b (3/4, frente, interna)<br>3. Closes a 32°: perfil, 3/4 do outro lado, de baixo<br>4. Quadros intermediários 0–32° (3/4 e frente)<br>5. Tamanho de jogo<br>6. Membros e flancos |
| `review/E3b_boca_34.mp4`, `review/E3b_boca_frente.mp4` | Abre e fecha 0→32→0°, 76 quadros, 24 qps, 640 px |
| `review/e3c/final/` | Todas as poses (0, 5, 10, 15, 20, 26, 32) × vistas (3/4 dos dois lados, perfil, frente, baixo, interna, jogo) + `medidas.json` |
| `review/e3c/e3_antiga/` | As mesmas câmeras e medições aplicadas à E3 anterior |
| `review/e3c/auditoria_e3b_sem_solda.json`, `review/e3c/nm/` | Auditoria da malha, posições dos restos não-manifold e closes |

## 1. Boca: o que mudou em relação à E3
1. **Linha da boca:**
   - o focinho da malha é assimétrico (linha média em x = −0,23, não 0); a boca agora é centrada nele;
   - os degraus do corte do lábio foram alisados no plano da boca, igual nos dois lábios, que continuam coincidentes com a boca fechada.
2. **Junção focinho / lábios / comissura / mandíbula / bochecha:**
   - os pesos da pele são um campo contínuo;
   - no último 1,0 stud antes de cada comissura os lábios convergem para 0,6, e a abertura afina até a comissura sem rasgo;
   - o lábio superior perto da comissura desce um pouco junto, como as bochechas de felino;
   - atrás da comissura a faixa de transição alarga até a articulação, para a bochecha esticar;
   - a largura da mandíbula é medida no próprio lábio inferior, de cada lado;
   - a pele e a barba sob o assoalho acompanham a mandíbula inteira. Na E3 elas ficavam a 35–75%, e o assoalho atravessava a barba (a mancha de pelo laranja vista dentro da boca).
3. **Cavidade contínua:**
   - margem do lábio fina e escura;
   - gengiva com crista;
   - palato em abóbada com rugas;
   - assoalho mais fundo atrás;
   - garganta escura;
   - bochechas internas como membrana com pesos graduados e curvatura (na E3 eram um quad plano cinza).
   - Toda a cavidade é mantida **dentro** da pele, com folga mínima de 0,07 stud medida por paridade de raios e de 0,10 na vertical (dobra da barba sob o queixo).
   - Junto às comissuras, a mucosa acompanha o lábio e vai ficando rígida para dentro. A margem ali é mucosa escura, e não a borda preta (sem "abas").
   - Não há face com material padrão: interior `M_Leao_Boca` (cor por vértice), dentes `M_Leao_Dentes`.
4. **Dentição de leão:**
   - por lado e por arcada: I1–I3, canino curvo para trás e inclinado para fora (superior com 0,42 exposto, inferior com 0,34), P2 pequeno e P3/P4 em lâmina (inferior: P3, P4, M1);
   - as raízes ficam enterradas na gengiva;
   - a arcada inferior fica por dentro da superior (mordida em tesoura), com o canino inferior entre o I3 e o canino superiores;
   - há bolsos no palato e no assoalho para os caninos;
   - os dentes que afloravam com a boca fechada foram recuados ou encurtados automaticamente.
5. **Língua:**
   - nasce do assoalho, com o ventre afundado nele e a base que some na garganta;
   - dorso abaulado com sulco, até 0,26 de espessura;
   - fica limitada pelo palato com a boca fechada e se estreita automaticamente onde tocaria os dentes;
   - osso `Lingua` (filho de `Mandibula`) para movimento discreto: a ponta enrola de leve no vídeo.

## 2. Medições por pose (mesmas funções nas duas versões; `review/e3c/*/medidas.json`)
| Medida | Pose | E3 anterior | E3b |
|---|---|---|---|
| Pontos do interior/dentes/língua **fora da pele** com a boca fechada (paridade) | 0° | 38 | **0** |
| Vértices de pele **dentro da cavidade** (entre palato e assoalho) | 10° / 20° / 32° | 55 / 73 / 87 | **0 / 0 / 0** |
| Língua × pele (pares de triângulos) | 10° / 20° / 32° | 56 / 90 / 121 | **0 / 0 / 0** |
| Dentes × pele | todas | 6 | **0** |
| Interior profundo × pele | todas | 0 | 0 |
| Faces do interior (fora a 1ª fileira) × pele | todas | 210–268 | **11** |
| Mandíbula entrando na cabeça/juba (vértices) | 0° / 5° / 10° / ≥15° | 61 / 32 / 3 / 0 | 86 / 19 / 0 / 0 |
| Dentes sup. × inf. | 0° / 5° / ≥10° | 0 / 0 / 0 | 86 / 66 / **0** |
| Dentes × tecido oposto | 0° / 5° / ≥10° | 34 / 0 / 0 | 129 / 54 / **0** |
| Língua × dentes / palato | todas | 0–20 | **0** |

- **Faces do interior × pele (11):** são faces da margem do lábio inferior que tocam a própria pele do lábio, na mesma região de peso, então são constantes em todas as poses. Não aparecem nos closes.
- **Mandíbula entrando na cabeça com a boca fechada (86):** é o lábio inferior encostado no superior.
- **Dentes com a boca fechada e a 5°:**
  - os caninos ficam cruzados dentro dos lábios, invisíveis por fora (0 pontos fora da pele);
  - a 5° ainda se tocam dentro da boca quase fechada;
  - de 10° em diante, zero.
- **Rosto fechado contra a v11 aprovada** (média em 255; % de pixels acima de 12 níveis):

  | Vista | E3b | E3 anterior |
  |---|---|---|
  | Close de perfil | 0,85 (0,32%) | 0,90 (0,42%) |
  | Close de frente | 1,15 (0,47%) | 1,17 (0,53%) |

  - Os filetes escuros das comissuras da E3 sumiram (0 pontos fora da pele).
  - O resto da diferença é ruído do EEVEE na juba.

## 3. Antebraços e flancos (reavaliação)
- **Na E3, três problemas locais:**
  - linha clara horizontal nas coxas traseiras (limite da máscara em Z 7,5);
  - flancos e coxas clareados;
  - alto do antebraço saturado para laranja (ganho de até 3× na transição com a juba).
- **E3b** (`c05_antebracos.py`, a partir do albedo da v11):
  - corrige só os membros dianteiros, com transição vertical longa;
  - a luminância sobe pela razão local e a matiz é puxada para a do pelo claro vizinho na proporção da correção;
  - membros traseiros, flancos e coxas voltam a ser exatamente os da v11;
  - a paleta global não muda.
- **Cor média na frente do antebraço** (render de frente):

  | Versão | Esquerdo | Direito |
  |---|---|---|
  | Referência | (166,107,59) | (165,109,65) |
  | v11 | (147,94,59) | (158,92,49) |
  | E3 | (191,118,68) | (191,109,55) |
  | **E3b** | **(180,121,74)** | **(182,111,60)** |

  - Resta uma sombra leve no meio do antebraço.

## 4. Auditoria da malha (`Leao_Solar_E3`, sem solda)
| Item | Valor |
|---|---|
| Vértices / faces | 103.655 / 206.350 |
| Triângulos | 207.476 |
| Bordas abertas | 4, em 2 laços de 2 arestas na juba: (2,25; −8,13; 15,75) e (2,87; −8,21; 14,58) |
| Arestas com mais de 2 faces | 33 |
| Vértices não-manifold | 54 |

- A boca nova não acrescenta borda aberta nem não-manifold.
- **Correção do relatório da E3:** os restos não estão todos na juba. São 24 grupos:
  - 22 na juba da cabeça, do pescoço e do dorso;
  - 1 no tufo da cauda (1,43; 14,31; 3,20);
  - 1 na barba/peito (−0,18; −12,96; 6,81).
  - Lista com posições: `review/e3c/nm/nao_manifold_posicoes.json`.
- Os closes dos 6 maiores grupos (`review/e3c/nm_closes.png`) mostram pontos de contato entre mechas sobrepostas, sem artefato visível.
- A E3b **não** está topologicamente fechada. A malha de jogo, que reconstrói a superfície, é que deve sair limpa.

## 5. Objetos e materiais (`Leao_Solar_Ref_E3b.blend`)
| Objeto | Tris | Material | Grupos / ossos |
|---|---|---|---|
| `Leao_Solar_E3` | 207.476 | `Material_0` (pelo: `albedo_e3b.png`, normal e rugosidade do Meshy), `M_Leao_Boca` | `Mandibula`, `Cabeca`, `Boca_Profundo` (só verificação) |
| `Leao_Dentes_Sup` (14 dentes) | 2.688 | `M_Leao_Dentes` | `Cabeca` |
| `Leao_Dentes_Inf` (14 dentes) | 2.688 | `M_Leao_Dentes` | `Mandibula` |
| `Leao_Lingua` | 1.248 | `M_Leao_Boca` | `Lingua`, `Mandibula` |
| `Leao_Rig_Teste_Boca` | — | — | ossos `Cabeca`, `Mandibula` (pivô (0; −12,75; 12,35)), `Lingua`. Rig de teste, não o final. |

- Malha de trabalho, não de jogo.

## 6. Limitações e pendências
- **Perfil exato com a boca bem aberta:** dá para ver o fundo através da frente da boca, entre os lábios dos dois lados, como num animal real. Em 3/4 e de frente, a cavidade fecha a vista.
- **Lábio inferior aberto:** é a borda do corte da malha fechada, fina, e em perfil parece uma prateleira escura.
- **Comissura:** é dobra de mucosa, sem dobra de pele esculpida. A pele da bochecha só estica.
- **Tamanho de jogo:** a boca aberta mal aparece no render de 360 px do corpo inteiro.
- **Custo da boca:** dentes e língua somam 6,6 mil tris e o interior ~1,3 mil faces (na maioria quads). A malha de jogo precisa de versão reduzida (alvo de ~1,5 mil para a boca toda).
- **Vermelho dos antebraços:** um pouco mais claro e menos saturado que a referência.
- A aprovação visual é do usuário.
