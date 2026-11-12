# Wyvern — ficha-resumo do subchat (Montanhas Altas)

Mantida pelo subchat da Wyvern (ver `DOCS/ORGANIZACAO-CHATS.md`). Criada em 03/11/2026, só com leitura: nada foi alterado no Studio, em `src/` ou nos arquivos compartilhados.

Fontes: `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO` (seção da Wyvern, tabelas 10, 15.1–15.4 e 16; ATUALIZAÇÃO OFICIAL de 30/10/2026) e `RPG_01_Mundo_e_Sistemas_ATUALIZADO` (§8, ninhos e ovos). **A atualização de 30/10/2026 prevalece** sobre a ficha antiga quando as duas se contradizem.

Legenda: **[OFICIAL]** aprovado pelo criador · **[PROPOSTA]** sugestão, não autoriza implementação · **[PENDENTE]** falta decisão · **[SUPERADO]** era oficial, mas foi substituído pela atualização de 30/10.

---

## 1. Identidade

- [OFICIAL] **Espécie-base própria**, distinta do Dragão (o catálogo tem 13 espécies-base; Wyvern e Cérbero são independentes). Ela tem uma única forma regional, a própria **Wyvern**.
- [OFICIAL] **Habitat:** Montanhas Altas. O bioma é o mesmo do Dragão das Montanhas, mas a espécie é outra.
- [OFICIAL] **Especialidade:** PREDADORA VENENOSA, com rasantes, ferrão e desgaste das presas. É voadora, rápida e agressiva no ar, especializada em manobras de caça e ataques precisos.
- [OFICIAL] **Identidade de voo:** voa **mais rápido que os Dragões**, mas tem **menor resistência de voo** e não aguenta perseguições longas.
- [OFICIAL] **Três padrões (pelagens):** Verde Musgo, Marrom Rochoso e Cinza Acinzentado. São cosméticos: não são espécies nem definem raridade ou elemento.
- [PROPOSTA de balanceamento] Não sustenta troca de golpes frontal com um Dragão (que tem mais alcance, área e sopro). Bate e sai.

## 2. Porte, anatomia e montaria

- [OFICIAL] **Adulto:** 9–13 studs de altura até os ombros e **30–42 studs de envergadura**.
- [OFICIAL] **Montável só no estágio Adulto**, com **sela adaptada ao voo**.
- [OFICIAL] **O voo montado exige uma missão de desbloqueio** (vale para Dragões e Wyverns).
- [PROPOSTA VISUAL] Corpo mais aerodinâmico e leve que o do Dragão, **duas patas traseiras**, membros dianteiros ligados às asas (asa-braço), cauda terminada em ferrão e sela presa sem atrapalhar as asas. Locomoção terrestre "com apoio anatômico compatível". Anatomia, encaixe da sela e rig dependem de validação visual.
- [PENDENTE] Comprimento total (o modelo atual tem ~56–57 com a cauda; não é valor oficial), diferenças entre estágios e se as pelagens mudam pouco a anatomia.
- [PENDENTE] Se ela se apoia nos **punhos das asas** em terra. O plano de rig deixou isso para o usuário aprovar.

## 3. Elemento e habilidades

### 3.1 Elemento
- [SUPERADO] A ficha antiga dizia: "Elementos permitidos Ar, Fogo e Veneno; nasce com uma afinidade e desbloqueia até mais duas por missões", com fusões direcionais.
- [OFICIAL — 30/10] **Cada criatura tem APENAS UM elemento natural**, definido na ficha dela. Não há segundo ou terceiro elemento, alternância em combate nem fusões.
- [PENDENTE] **Qual é o único elemento da Wyvern.** A lista antiga (Ar/Fogo/Veneno) não indica a escolha final, e o documento pede para não presumir. Dragão das Montanhas = Fogo já está fixado; vale evitar uma sobreposição sem querer, mas a decisão é do usuário.

### 3.2 Toxina biológica (anatomia, não elemento)
- [OFICIAL] O **ferrão causa intoxicação biológica LEVE desde o nascimento**, qualquer que seja o elemento.
- [OFICIAL] A intoxicação é renovada por novas ferroadas e ataques básicos, mas **não acumula excessivamente**.
- [OFICIAL] Antídotos e habilidades de purificação removem ou reduzem o efeito.
- [OFICIAL] Veneno anatômico ≠ afinidade Veneno. Tratar a toxina como vantagem elemental automática é erro.
- [PENDENTE] Limite numérico, duração e dano da intoxicação (dependem de testes).

### 3.3 Kit de habilidades
- [OFICIAL — 30/10] Regra geral: **no mínimo 1 passiva e 3 ativas**, aprovadas criatura por criatura. As listas históricas de 4 habilidades valem como **referência**, não como obrigação. Ataques básicos físicos (mordida, garra) não ocupam slots.
- Referência histórica [OFICIAL na ficha antiga — nomes e papéis gerais]:
  1. **Rasante Predatório:** mergulho aéreo rápido com ataque preciso e saída lateral/ascendente. É caça, não impacto amplo como o do Dragão.
  2. **Ferrão Venenoso:** ferroada da cauda que aplica ou renova a intoxicação leve, mesmo sem afinidade Veneno.
  3. **Guinada Evasiva:** manobra brusca de evasão no ar, adaptada ao solo. Não presumir invulnerabilidade.
  4. **Caçada dos Céus:** estado temporário de perseguição de presas e de aproveitamento de oportunidades.
- [PROPOSTA, agora sem efeito] As tabelas "habilidades × Ar/Fogo/Veneno" e as seis fusões direcionais **não valem mais**, porque fusões foram abolidas em 30/10.
- [PENDENTE] **Kit final:** quais ativas (≥3) e passivas (≥1), nomes, efeitos, ângulos, distâncias, custos, recargas e janelas de reação. Uma candidata natural a passiva é a toxina do ferrão, mas isso é só observação, não decisão.

## 4. Números propostos (Etapa 24.2 — NÃO APROVADOS)

Os números servem só como referência de teste. Nenhum é oficial.

| Item | Wyvern | Comparação |
|---|---|---|
| Matriz 1–5 (Vida/Def/Força/Vel/Energia/P.Elem) | 3 / 2 / 4 / 5 / 3 / 4 | — |
| Vida / Def / Força / Energia / P.Elem (Adulto n100) | 3.800 / 95 / 175 / 115 / 160 | Dragão Sombrio 6.150 de vida |
| Velocidade: terra / água / ar (studs/s) | 27 / — / **58** | Dragões 43–47 no ar |
| Manobra: terra / ar (1–5) | 3 / **5** | Dragões 4 no ar |
| Fôlego de voo | **95** | Dragões 145–160 |

- [PENDENTE] Consumo do fôlego (subir, planar, acelerar, esquivar), regeneração, o que acontece quando ele zera, altitude e contrajogo terrestre.
- [PROPOSTA] Rasante Predatório tem aceleração própria, fora da velocidade normal de deslocamento.

## 5. Mundo: ninhos e pousos (já existem no mapa)

- [OFICIAL — RPG_01 §8] Os ninhos são poucos e escalonados pelo número de jogadores. Reaparecem em **30–60 min**, longe do local anterior, e são achados por pistas naturais, sem coordenada automática.
- **Já no mapa (V7c/V8, M9):**
  - **5 ninhos de Wyvern** na escala oficial (≈35 de diâmetro, ~10 de altura): 4 ressaltos naturais e `Saliencia_Pico_da_Costa`. Pico da Toca e Pico do Lago têm só poleiro. Ficam a ≥ 496 studs uns dos outros.
  - **Marcadores sem sistema** (`Marcadores_V8`): Aproximacao, Orbita (8 pontos), Pouso, Descanso, Ovos, Decolagem, **Territorio Raio 220 (wyvern)** e `LocalNinhoElegivel` (30–60 min).
  - **Ilhas flutuantes:** o Terraço de Pedra (−4.300, −2.300; topo ~1.080) é reservado a voadores e é o único ninho elegível de Wyvern nas ilhas. A Ilha dos Ventos Altos tem pouso/acesso da Wyvern.
  - Detalhes em `DOCS/estado/mundo-floresta-montanhas-v5-v9.md` e `DOCS/estado/mundo-ilhas.md`.
- Problema conhecido: nos ninhos (~35×35) e no pouso da ilha (Ø 40), **a cauda (~56) sobra**, a menos que a Wyvern se enrole (`DOCS/CRIATURAS-C1-MATRIZ.md`).

## 6. O que já existe no projeto

### 6.1 Modelo Blender (C1, 26/10) — feito por script, importação no Studio PENDENTE
- Arquivos em `BLENDER/Criaturas/`: `Wyvern.blend`, `Wyvern.fbx` (10,3 MB), `Wyvern.glb` (7,3 MB), `Wyvern_Cor_Verde_Musgo.png`, `Wyvern_Cor_Marrom_Rochoso.png`, `Wyvern_Cor_Cinza_Acinzentado.png` e `Wyvern_Normal.png` (2048).
- Gerador: `BLENDER/Criaturas/scripts/wyvern_completo.py` (Skin + Subsurf, rig `Wyvern_Rig`, atlas assado).
- Medidas: **11 de ombro**, **38 de envergadura**, ~12 × 56 × 19, **14,1 mil tris** e **38 ossos** (bípede, asa-braço com 3 dedos, ferrão).
- **18 clipes:** Repouso, Andar, Corrida, VirarEsquerda, VirarDireita, Observar (ferrão erguido), Vocalizar (mandíbula), AbrirAsas, RecolherAsas, Decolagem, Voo (batida mais rápida), Planeio, CurvaAereaEsquerda, CurvaAereaDireita, Pouso, Rasante, FerraoAtaque e GuinadaEvasiva. As três últimas são só animação, sem efeito.
- Validado só por reimportação no Blender. **Nunca foi importado nem testado no Studio.**
- Avaliação registrada:
  - qualidade de "protótipo jogável", com animações procedurais;
  - pede ajuste anatômico (peito e coxas; "corpo fino e asas largas");
  - membrana lisa, sem veios, e com pequenas dobras pontiagudas em repouso.
- Inconsistência a conferir: o cabeçalho do script fala em "punhos das asas no chão", mas o `LEIA-ME-IMPORTACAO.md` diz que a Wyvern se apoia só nas patas traseiras e que o apoio no punho ficou para depois.
- Versão mais pesada nos blockouts: `BLENDER/Criaturas/Blockouts/build/build_Wyvern.py` (47 mil → 14 mil tris, 39 ossos, 36 animações no plano final).
- Análise de refinamento (`DOCS/CRIATURAS-REFINAMENTO-ANALISE.md`) do alvo anatômico:
  - asa-braço com úmero, antebraço, punho com garra e 3 dedos longos;
  - membrana do flanco até a coxa, com propatágio;
  - pernas traseiras fortes com garras de rapina;
  - ferrão em gancho e cabeça com chifres para trás.
- Plano de animação (`DOCS/CRIATURAS-RIG-ANIMACOES-PLANO.md`): **34 clipes** (12 base, 7 de interação, 3 territoriais e 8 de voo). Personalidade: "rápida, guinadas e rasante". **Nunca reaproveitar clipes do Dragão** (famílias diferentes).

### 6.2 No jogo (`src/`) e no Studio
- `src/` não tem **nenhum script nem config específico da Wyvern**.
- O catálogo `ServerStorage.Biblioteca_Criaturas.Catalogo` (no Studio, segundo `DOCS/estado/criaturas-gerais.md`) registra a forma com medidas, elementos, locomoção, montaria e as 4 habilidades. **Os elementos ali seguem a regra antiga (3 afinidades) e precisarão de revisão.** Não conferi no Studio.

### 6.3 Base técnica reaproveitável (referência; arquivos dos Dragões, NÃO mexer)
São protótipos do Dragão das Montanhas em `Teste-animacoes.rbxl` (ver `DOCS/estado/dragao-ia-combate-montaria.md` e `DOCS/SISTEMA-ANIMACAO-DRAGOES.md`):
- **Montaria:**
  - scripts: `src/ServerScriptService/Montaria_Dragao_Servidor.server.luau`, `src/ReplicatedStorage/Montaria_Dragoes/ConfigMontaria.luau` e `src/StarterPlayer/StarterPlayerScripts/Montaria_Cliente.client.luau`;
  - validações no servidor: dono, estágio (ovo/bebê/jovem não montam; pré-adulto só no chão), missão `VooDesbloqueado`, guardião nunca e um controlador por criatura;
  - ciclo: abaixar → Weld na sela → levantar; voo com subir/descer/planar/pousar; desmontar só no chão, parado e em local livre;
  - teclas: WASD, Shift, Espaço, Ctrl, G, F, X, 1–4;
  - HUD de energia e recargas.
- **IA selvagem/territorial:** `src/ServerScriptService/IA_Dragao/` (Cerebro, Locomotor, Territorio, Config), com voo por relevo, desvio por spherecast, órbita do ninho e pouso de emergência. É **compartilhado** (Cerebro).
- **Combate:** `src/ServerScriptService/Combate_Dragao/` (Nucleo, Passivas, **ConfigCombate — compartilhado**), com autoridade do servidor para dano e recargas.
- **Animação:** sistema universal dos dragões (gerador único + ambiente por forma, prefixo/pasta por forma) e `MovimentoVivo/Perfis.luau` (movimento procedural no cliente).
- **Sons:** `SonsConfig` e `SonsDragao_Cliente` (**compartilhados**).
- Para a Wyvern, o caminho provável é criar arquivos próprios (perfil de montaria, config de IA e de combate da Wyvern) ou, com o acordo do usuário, generalizar os compartilhados. **Isso ainda não foi decidido.**

### 6.4 Base adotada: Ashwing Drake Lite (Literock Studios)

**Adotada pelo usuário em 03/11/2026**, com o pedido de adaptar e "transformar levemente" para o visual do jogo. A adaptação está em `BLENDER/Criaturas/Wyvern_Ashwing/` (ver `LEIA-ME.md`):
- **E1 proporção:** cernelha 10 e envergadura 36–40 (ambas dentro da faixa oficial), asas a 64% e cauda a 80%.
- **E2 ferrão:** bulbo e gancho curvo.
- **E3 padrões:** os 3 padrões oficiais na paleta do painel 04 Wyvern.
- **E4 transição do ferrão (04/11/2026):**
  - Corrige só a junção cauda–bulbo–gancho, com os mesmos vértices, UV, material, ossos e texturas.
  - Causas medidas:
    - remapeamento por fatias esparsas no E2;
    - raio só C0 no pico do bulbo;
    - normais personalizadas desatualizadas e `sharp_edge` original;
    - salto de peso 0→1 entre tail_09 e tail_10 sobre o bulbo;
    - espícula fina herdada do Ashwing.
  - Resultado:
    - 0 autointerseções em repouso (o E3 tinha 75);
    - estiramento nos ciclos igual ao do E1.
  - Detalhes e métricas: `BLENDER/Criaturas/Wyvern_Ashwing/LEIA-ME.md`.
  - **Aguarda avaliação.**
- **Verificação local do E4, caso a caso (04/11/2026):**
  - Em idle e walk não há penetração real; o E4 removeu as 2 do Ashwing no walk.
  - Restam 3 defeitos herdados do Ashwing:
    - uma aba dobrada na junção (y≈22,7), com o verso visível por baixo;
    - 2 penetrações mínimas no fly, frames 4–10, profundidade ≤ 0,01;
    - uma fenda de borda aberta de ~0,4 stud no lado interno do gancho.
  - A tentativa de corrigir só movendo vértices (E5) foi reprovada.
  - O conserto exige ajuste local de topologia (cerca de ±20 triângulos), **proposto e não autorizado**.
  - O E4 segue como base. Detalhes no `LEIA-ME.md` da pasta.
- **E6, ajuste local de topologia autorizado (04/11/2026):**
  - Removidas a aba da junção (8 faces, buraco fechado com 8 triângulos sobre os vértices existentes) e as 12 abas soltas da ponta, que eram a "fenda".
  - Pesos tail_08/tail_09 em rampa na junção.
  - Resultado:
    - 11.980 triângulos;
    - 0 bordas abertas;
    - 0 faces com verso visível;
    - 0 penetrações em todos os frames de idle, walk e fly.
  - Fora de y ≥ 22,3 nada mudou.
  - **Ferrão aprovado pelo usuário em 05/11/2026.**
- **Lote 1 de clipes (05/11/2026, aprovado pelo usuário):** `Wyvern_E7_clipes_L1.blend`.
  - Clipes: Corrida, VirarEsquerda, VirarDireita, Planeio, CurvaAereaEsquerda, CurvaAereaDireita e Pouso.
  - São derivados dos clipes do próprio Ashwing.
  - O QA não mostra piora em relação aos originais.
  - Nada foi para o Studio. Faltam os outros lotes, a exportação e as habilidades (estas dependem do elemento).
- **Lote 2 de clipes (05/11/2026, em avaliação):** `Wyvern_E7_clipes_L2.blend` (lote 1 + 9).
  - Clipes: FerraoAtaque, Alerta (= Observar, ferrão erguido), Ameaca, ReacaoGolpe, Morte, Comer, Deitar, Deitado, Levantar.
  - O ferrão é só animação: nenhum efeito, dano ou toxina foi definido.
  - QA sem afundar no chão e com loops fechados; deitado tem ~370 autointerseções a mais (perna dobrada, escondida sob o corpo).
  - Aceite parcial do usuário. **Descanso v2 (05/11/2026; aceito pelo usuário em 06/11/2026 com a prega residual):** `Wyvern_E7_clipes_L2b.blend` refaz só Deitar/Deitado/Levantar: pés plantados (o corpo recua sobre os pés), perna aberta, emendas exatas; demais actions idênticas. Resta a dobra canela×coxa visível de perto (≤0,46). **Pesos locais (W1, 05/11) testados e NÃO aplicados**: não reduzem o contato (é volume ao longo da canela) e a variante com flanco deforma o corpo em pé; pose sentada (S1, 05/11) também testada e NÃO adotada: com o peito no chão a barriga desce sobre os joelhos; com o peito alto o corpo fica agachado (barriga 1–1,5 acima do chão) e a prega continua. Afinar a malha da perna (M1, 05/11) também testado: melhora o idle e parte das transições, mas a prega do quadril (coxa/canela × flanco) continua; candidato `Wyvern_E8_perna_afinada_CANDIDATO.blend` NÃO adotado. Restam: ossos auxiliares, afinar também o flanco, ou aceitar o L2b (LEIA-ME). **Comer corrigido (06/11/2026, aprovado pelo usuário; `Wyvern_E7_clipes_L2c.blend` é a base atual dos clipes):** `Wyvern_E7_clipes_L2c.blend` (só o Comer regravado): o afundamento era do pé esquerdo (−0,136) e da ponta da cauda, não da mandíbula; agora −0,022 (= idle) em todos os quadros; a dobra passa a ficar no joelho (prega canela × coxa visível de perto, mesma profundidade de antes).
- **Lote 3 de clipes (06/11/2026, aprovado):** `Wyvern_E7_clipes_L3.blend` (L2c + 6): Arrancada, Frenagem, VooBatido, PairarCurto, Empoleirado e GuardaNinho; emendas exatas com Corrida/idle; anteriores idênticos; nada no Studio.
- **Subida, Descida e Mergulho (06/11/2026, aprovados):** `Wyvern_E7_clipes_L3b.blend` (L3 + 3 loops de voo) — base até a montaria (31 actions); nada no Studio.
- **Montaria (06/11/2026, aprovada):** `Wyvern_E7_clipes_L4.blend` — **base atual dos clipes (38 actions)** (L3b + Mount, Dismount, RideIdle, RideWalk, RideRun, RideVirarEsquerda, RideVirarDireita): dorso da sela ~65% mais estável; emendas exatas; anteriores idênticos. Sela, encaixe do cavaleiro e regras não definidos; nada no Studio.
- **Demonstração do cavaleiro (09/11/2026, APROVADA pelo usuário):** manequim R15 de caixas (`build/17_demo_cavaleiro.py`, sem alterar o L4): subida/descida pelos dois lados em salto por cima do flanco; assento atrás das asas preso ao osso da sela, 1.2 stud acima da pele (espaço de sela), pernas estilo jóquei; montado sem o corpo entrar na Wyvern. O cavaleiro fica **meio deitado para a frente** (tronco 60°) e **segura no dorso da Wyvern** com as duas mãos (pegada acompanha a pele; erro ≤ 0.179); a alça provisória foi removida. Cabeça erguida olhando à frente e **física**: o tronco reage à aceleração do dorso por mola amortecida (caminhada ~[4.65, 2.42]°, corrida ~[8.0, 6.18]° à frente/trás e de lado) e a cabeça estabiliza o olhar. Não é a animação final do jogador; nada no Studio.
- **Sela (09/11/2026, APROVADA pelo usuário; materiais [PROPOSTA]):** `Wyvern_S1_sela.blend` (L4 + `Wyvern_Sela`, `build/18_sela_wyvern.py`): manta de Pele de Íbex, aba e assento de couro, cinta na base da cauda com argolas de Ferro Montanhês, sem alça; 4224 tris; pesos só do corpo; em todos os clipes a sela entra na pele no máx. 0.07 (0.14 no auge da ferroada) e a pele na sela no máx. 0.04. **Textura de jogo 1024 e GLB APROVADOS (10/11)**: `export/sela/Wyvern_Sela.glb` (4224 tris, 61 ossos, ≤ 3 influências, texturas embutidas; reimportado com desvio 0.0). Roblox pendente.
- **Lote 5 — realismo (12/11/2026, APROVADO 12/11; Farejar v3 com boca fechada +18° e balanço da cabeça) [PROPOSTA]:** `Wyvern_E7_clipes_L5.blend` (L4 + 7 actions = 45; `build/19_clipes_lote5.py`): SacudirCorpo, AlisarAsaEsquerda/Direita, Espreguicar, Farejar, OlharVolta, DecolagemPenhasco. Emendas com o idle/Planeio 0°, pés parados, nada abaixo do chão do idle, 38 anteriores idênticas. Nada no Studio.
- **Lote 6 — realismo 2 (12/11/2026, APROVADO 12/11) [PROPOSTA]:** `Wyvern_E7_clipes_L6.blend` (L5 + 4 actions = 49; `build/20_clipes_lote6.py`): AsasEscudo, SecarAsas, AgarrarPresa (pisa e morde na postura do Comer; presa não modelada), AndarQuatroApoios (loop, pulsos das asas no chão). Emendas 0°, 45 anteriores idênticas. Nada no Studio.
- A aparência ainda espera a aprovação do usuário. Nada foi para o Studio.
- Não há referência da Wyvern em `REFERENCIAS/`; a pasta só tem floresta, pântano, planícies e tundra, conferido em 04/11. O painel usado como referência visual está em `Downloads\RPG_Referencias_Visuais_GitHub\REFERENCES\03_CREATURES\02-dragoes-wyvern.png`, fora do repositório.

Análise inicial (antes da adaptação):
Recebido do usuário em 03/11/2026: `Downloads\Ashwing_Drake_Lite_v1.0.0.zip` (23 MB). Inspecionei só no Blender, em modo headless, numa cópia extraída fora do repositório. Nada foi copiado para o repositório nem para o Studio.

- **Licença (LICENSE.txt):**
  - permite uso gratuito em jogos, inclusive comerciais, sem royalties, e permite modificar;
  - **proíbe redistribuir ou reenviar o asset, mesmo modificado, "on its own"**: só pode ir embutido no produto final;
  - proíbe usar como dado de treino de IA e proíbe reivindicar autoria;
  - crédito apreciado, não obrigatório ("Ashwing Drake by Literock Studios");
  - parte do modelo foi feita com Meshy.
  - Consequências práticas:
    - não publicar o modelo na Creator Store nem como modelo público;
    - não deixar o place descopiável;
    - não versionar os arquivos originais num repositório público (no git local, só com o acordo do usuário).
- **Conteúdo:**
  - GLB/FBX com malha de **11.992 tris** e 4 influências por vértice;
  - **61 ossos**: root, pelvis, spine ×3, neck ×5, head, jaw, `breath_socket`, asa-braço com úmero/antebraço/mão, 2 dedos, polegar e 8 "struts" por lado, cauda ×10, perna com coxa/canela/pé/dedo;
  - 1 material com 3 texturas 2K (cor, normal, metal/rugosidade);
  - **6 clipes** a 30 fps: idle_loop, walk_loop, roar, bite, takeoff e fly_loop.
- **Medidas (metros; README diz 12 m de envergadura):**
  - ombro (osso `shoulder_L`) ≈ **1,78 m** no idle;
  - comprimento ≈ 9,3 m, a maior parte cauda;
  - largura com as asas fechadas ≈ 3,5 m.
- **Visual:** é de fato uma wyvern (bípede, asa-braço) que **caminha apoiada nos punhos das asas**. Asas rasgadas, chifres para trás, cauda muito longa e fina com **ponta em losango (não é ferrão)**. Pele cinza-escura e membrana bege. Folha de poses renderizada na pasta de rascunho da sessão (`ashwing_folha.png`).
- **Confronto com as regras:**
  - **Escala × oficial (conflito):** a razão envergadura/ombro é ≈ 6,7, e a oficial fica entre 2,3 e 4,7.
    - Ombro 9 studs (×5,06) → envergadura ≈ 61 e comprimento ≈ 47.
    - Envergadura 42 studs (×3,5) → ombro ≈ 6,2 (abaixo de 9).
    - Para cumprir as duas faixas, é preciso **encurtar as asas ~30%** (e provavelmente a cauda, por causa dos ninhos de ~35), escalando os ossos no Blender.
  - **Ferrão (oficial: ferroada com a cauda e toxina inata):** não existe. É preciso modelar a ponta da cauda e criar um clipe de ferroada.
  - **Padrões oficiais (Verde Musgo, Marrom Rochoso, Cinza Acinzentado):** só há 1 textura. O cinza atual se aproxima do Cinza Acinzentado; os outros dois exigem recolorir a textura.
  - **Clipes:** faltam corrida, giros, planeio, curvas aéreas, pouso, Rasante, Ferrão, Guinada, Observar e deitar. Os nomes de osso iguais aos do pacote completo não dão acesso aos 33 clipes dele (é pago).
  - **Apoio nos punhos:** combina com a [PROPOSTA] do RPG_02, mas o usuário ainda precisa confirmar.
  - **Roblox:** 12 mil tris cabem no limite de malha. A importação e os 61 ossos ainda não foram testados no Studio.

## 7. Pendências (decisão do usuário)

1. **Elemento único** da Wyvern (regra de 30/10).
2. **Kit final:** ≥1 passiva e ≥3 ativas. Decidir se os 4 nomes antigos ficam e se a toxina do ferrão vira a passiva.
3. **Aparência:** aprovar a anatomia do modelo C1 ou refazê-lo (o pipeline atual dos dragões usa Meshy + rig próprio, com qualidade bem maior que o modelo por script). Confirmar o apoio nos punhos.
4. **Missão de desbloqueio do voo montado** (conteúdo, onde e como) e **sela adaptada** (visual e encaixe).
5. Valores de intoxicação, fôlego de voo, velocidades e custos (os números da Etapa 24.2 não foram aprovados).
6. Comportamento selvagem: território (o marcador usa 220), caça, ninho e reação a jogadores.
7. Cauda × tamanho dos ninhos e pousos (ela se enrola, o ninho cresce ou fica como está).
8. Estágios de crescimento: escala por estágio e quais padrões aparecem em cada um.

## 8. Próximos passos sugeridos (aguardando aprovação)

1. **Decidir o elemento e o kit** com o usuário. Sem isso, IA e combate não começam.
2. **Revisão visual do modelo C1:** renderizar folhas de vistas no Blender, comparar com a referência visual e decidir entre refinar ou refazer pelo pipeline Meshy.
3. Com o modelo aprovado: **rig + clipes próprios** (34 do plano, personalidade rápida, sem copiar o Dragão) e importação no Studio em lugar de teste, seguindo a regra do Studio "um chat por vez".
4. Depois: IA selvagem e de ninho, montaria/voo (com a missão) e habilidades, cada etapa pequena e autorizada.

## Histórico desta ficha

- 03/11/2026: ficha criada (somente leitura). Nenhuma alteração no Studio, em `src/` ou em arquivos compartilhados, e nenhum commit.
