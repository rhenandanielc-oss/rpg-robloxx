# Dragão Sombrio (Sombra) — ficha do subchat

Criatura **domesticável** das **Terras Corrompidas**. Pertence à espécie-base **Dragão**, junto com o Dragão das Montanhas (Fogo) e o Dragão Glacial (Gelo).

Fontes oficiais lidas em 03/11/2026: `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO.docx` (topo "ATUALIZAÇÃO OFICIAL", revisões de 30/10, matriz de elementos, tabela de dragões) e `RPG_01`. O histórico técnico está em `DOCS/estado/dragao-2026-10-30.md`, seções **BF a BK**. Regras de convivência: `DOCS/ORGANIZACAO-CHATS.md`.

## 1. Regras oficiais (o que já está decidido)

| Item | Valor | Status |
|---|---|---|
| Elemento | **Sombra, exclusivo**. Não desbloqueia outro, não alterna e não funde | [OFICIAL 30/10] |
| Matriz da Sombra | vence **Ar e Raio**; é fraca contra **Água e Luz**; tema: "ofuscação, ocultação e efeitos sombrios" | [OFICIAL] |
| Papel | "Sombrio **maximiza pressão e emboscadas**"; dragões focam ataque, batalha aérea e campo aberto | [OFICIAL] |
| Kit | mínimo de **1 passiva e 3 ativas**, aprovadas criatura por criatura. As 4 habilidades históricas não são o kit | [OFICIAL] — kit do Sombrio **PENDENTE** |
| Montaria / voo | montável desde Adulto; voo montado só depois da missão de desbloqueio | [OFICIAL] |
| Números (dano, recarga, energia, alcance) | nenhum aprovado | [PENDENTE] |

## 2. Modelo no Studio (place `Teste-animacoes_CR.rbxl`)

- Importado pelo usuário: **GLB v4**. A conferência foi feita pela contagem de faces: Corpo 18.453, Asas 4.974 e Detalhes 14.752, iguais às do export v4. O v3 tem 14.368 em Detalhes.
- Montado em 03/11 com `V14/ia/studio_montar_sombrio.luau` como `workspace.Sombrio`, em (665; 8,33; 500), +90 studs do Silverwing:
  - 99 ossos com os nomes do jogo;
  - escala 17,5;
  - altura dos pés idêntica à do Silverwing (2,237);
  - `PastaAnimacoes = "Sombrio"`, `FormaRegional = "Sombrio"`, `ElementoNato = "Sombra"`.
- O importado original está guardado em `ServerStorage.Dragoes_Retirados.Sombrio_Importado_v4_<data>` (recuperável).
- Atributo `MigracaoPendente` = "ElementoNato Sombra fora da forma". Motivo: o `ConfigCombate` ainda não tem o Sombrio (o kit está pendente). Isso é esperado, não é erro.
- **05/11 — malha v10 / GLB v5 com boca interna** (DOCS/estado CR): nova peça `Silverwing_Boca` (3.794 tris, gengivas, 32 dentes, céu, língua, garganta); Detalhes agora 13.024. Trocada em `Sombrio` e `Sombrio_Guardiao` com `V14/ia/studio_trocar_sombrio_boca.luau` (atributos e altura dos pés mantidos; antigos em `ServerStorage.Dragoes_Retirados.*_antesBoca_*`).
- **O Studio não foi salvo pelas ferramentas.** Salvar (Ctrl+S) é passo do usuário.

## 3. Inventário real dos clipes (`ReplicatedStorage.Animacoes_Sombrio`, 68 + Apelidos)

Todos têm prioridade **Action**, como no Glacial e no Fogo. Consumidores: `EstadosDragao` (busca primeiro o prefixo `Sombrio_` e depois os Apelidos), `Combate_Dragao.Nucleo` (clipes de ataque), `Montaria_Dragao_Servidor` (locomoção, frenagem, voo) e `MovimentoVivo_Cliente` (perfil herdado `Silverwing`).

Legenda de status:
- **T** = testado em Play no modelo importado (03/11);
- **C** = corrigido nesta etapa;
- **E** = existe, gerado e montado, mas ainda não testado neste modelo;
- **P** = pendência conhecida.

| Grupo | Clipe (duração, L = loop) | Status |
|---|---|---|
| Chão | Parado 8,0 L · Andar 0,9 L · Correr 0,67 L | **T** (pés: ~11% da velocidade do corpo no apoio, igual ao Glacial certificado) |
| Chão | Parada 0,9 | **C + T** (frenagem refeita; ver seção 6) |
| Chão | Giro_E / Giro_D 0,9 L | E |
| Atenção | Reagir_Estimulo 1,2 · Idle_Alerta_Mantido 4,0 L · Observar 7,0 L · Observar_Farejar 2,5 · Curiosidade 5,0 · Ninho_Alerta 1,2 | **T**; **C** em Reagir/Observar/Farejar/Ninho_Alerta (cauda e focinho atravessavam o chão) |
| Postura de combate | Intimidar 3,6 L · Preparar_Combate 3,0 L | **T** (sem contato errado com o chão) |
| Rugidos | Rugido_Territorial 4,2 · Ninho_Ameaca 4,6 · Rugido_Combate 2,6 · Rugido_Combate_Camada 2,6 | **T**; **C** em Ninho_Ameaca/Rugido_Combate (cauda). Rugido com T montado: 1 som, sincronizado (15 ms), mas a **voz é a do Fogo** ("Creature Roar"). Rugido_Aereo e Rugido_Vitoria **não existem** no Sombrio (são clipes só do Fogo) |
| Descanso | Abaixar 0,7 · Abaixado 3,0 L · Levantar 0,7 · Deitar 2,2 · Deitado_Acordado 8,0 L · Adormecer 2,5 · Dormir 8,0 L · Acordar 2,0 · Espreguicar 4,0 | **C + T** (03/11): a cabeça inteira afundava no sono (−6 studs) → erguida pela base do pescoço (−1,3, pontas de espinhos); cauda no chão; Deitar −0,8 (patas, sem mudança) |
| Sentar | Sentar 1,6 · Sentado 8,0 L · Levantar_Sentado 1,2 | **C + T** (03/11): a cauda deita no chão (Sentado −3,5 → −0,45 stud) |
| Comer/beber | Comer 8,5 · Comer_Mastigar 3,0 L · Beber 9,0 · Beber_Loop 3,0 L | E (língua rígida: limitação do rig) |
| Voo | Decolagem 1,0 · Voo 3,2 L · Voo_Rapido 3,2 L · Planeio 4,0 L · Pairar 4,0 L · Subida 2,8 L · Descida 4,0 L · Curva_E/D 4,0 L · Mergulho 2,0 L · Mergulho_Saida 1,2 · Pouso 0,5 | **T** em voo montado (03/11); **C**: laço das curvas (cauda saltava 10,5°) e cauda no chão na Decolagem/Pouso. Voo_Rapido e (`Mergulho_Saida` ainda não está ligado ao misturador de voo; vale para todos os dragões) |
| Ataques básicos | Ataque_Mordida 1,4 (+ Ataque_Mordida_Sup) · Mordida_Aerea 1,0 · Ataque_Garra_E/D 1,5 · Ataque_Cauda 1,8 | **C + T** (03/11): mordida andando/correndo sem travar as patas; cauda/cabeça no chão; acertos em boneco. Mordida_Aerea **T** no ar (acerta −40) |
| Dano | Dano_Leve 0,6 · Dano_Forte 1,1 · Dano_Leve_Ar 0,6 · Dano_Forte_Ar 1,1 | **T** no chão e no ar (03/11; no ar o voo continua por baixo). Montado, o golpe recebido ainda não dispara a reação (só a IA) |
| Hab_* (movimento genérico, **nenhum poder**) | Hab_Concentracao 3,0 L · Hab_Preparo_Respiratorio(_Ar) 1,2 · Hab_Emissao_Loop(_Ar) 0,9 L · Hab_Emissao_Fim(_Ar) 0,8 · Hab_Investida(_Ar) 2,1 · Hab_Golpe_Garras 2,2 · Hab_Area 3,4 · Hab_Area_Ar 2,4 · Hab_Recuperacao 1,6 | E. Base corporal para os poderes futuros. O nome não significa poder implementado |
| Faltam | Espreitar, Bote_Emboscada, Recuo_Sombra; morte/incapacitação (não há clipe; nenhuma regra criada) | **P** (proposta, seção 4) |

## 4. Direção de atuação proposta, item a item [PROPOSTA — para revisão]

Personalidade: predador pesado e controlado (antecipação, ação, transferência de peso, movimento secundário e recuperação). O gerador usa `env_clipes_sombrio.sh`: AMP 1,6, passada leve, 4 batidas por clipe de voo. Essa personalidade é **NAO_APROVADA**.

| # | Animação | Clipe(s) | Direção proposta | Como validar |
|---|---|---|---|---|
| 1 | Parado | Parado | respiração no peito e nos flancos; pescoço atento; asas sem atravessar as costelas; cauda equilibrando | laço sem salto; deslocamento acumulado 0 (medido: pés 0,02–0,05 stud) |
| 2 | Andar | Andar | ombro e quadril alternados; cabeça estável; cauda atrasada | pé no apoio ≤ ~10% da velocidade (medido 11%) |
| 3 | Correr | Correr | impulsão traseira, compressão e extensão do tronco, alcance das dianteiras | idem (medido 11%) |
| 4 | Parada | Parada (nova) | passos curtos que desaceleram; peito segue por inércia; pescoço e cauda freiam | **feito**: deslize no apoio 0,9 stud no máximo (era 10–15) |
| 5 | Viradas no solo | Giro_E/D | a cabeça inicia, o tronco acompanha, as patas reposicionam, a cauda contrabalança | pés sem torcer; membros sem cruzar |
| 6 | Alerta | Reagir_Estimulo, Idle_Alerta_Mantido | pausa, cabeça para o estímulo, postura pronta; laço sutil | sem susto repetido no laço |
| 7 | Observar | Observar | varredura lenta com pausas; limite do pescoço; `AlvoOlhar` real | olhar para o alvo em Play |
| 8 | Farejar | Observar_Farejar | focinho busca a origem, pequenas inspirações | focinho sem entrar no chão |
| 9 | Curiosidade | Curiosidade | inclinação lateral moderada e aproximação curta | sem caricatura |
| 10 | Intimidar / preparar | Intimidar, Preparar_Combate | baixar o centro sem afundar o peito, abrir parcialmente as asas, firmar as patas | entrada, manutenção e saída distintas; sem dano |
| 11 | Rugido territorial | Rugido_Territorial | inspiração, expansão do peito, cabeça alta, projeção ao longe | um som por evento, sincronizado com a boca |
| 12 | Ameaça do ninho | Ninho_Ameaca | orientar-se ao invasor, advertência frontal, volta à guarda | sem sacudidas copiadas do Fogo |
| 13 | Rugido de combate | Rugido_Combate(_Camada) | projeção curta e agressiva; a camada não interrompe o estado base | Pontual/peso em Play |
| 14 | Rugido aéreo / vitória | — (não existem) | auditar se são necessários; se sim, desenhar próprios | depende de aprovação |
| 15 | Abaixar / levantar | Abaixar, Abaixado, Levantar | dianteiras flexionam, traseiras acomodam, levantar em ordem plausível | ventre e espinhos sem atravessar o chão |
| 16 | Sentar | Sentar, Sentado, Levantar_Sentado | o quadril recua entre os apoios; a cauda se acomoda fora do corpo | **corrigir a ponta da cauda (−3,5 studs)**; espaço do cavaleiro |
| 17 | Dormir | Adormecer, Dormir, Acordar, Deitar, Deitado_Acordado | pescoço acomoda, asas baixas, respiração lenta, despertar progressivo | não escorregar; afundamento ≤ Glacial |
| 18 | Espreguiçar | Espreguicar | estender dianteiras e dorso, abrir asas parcialmente | cristas e crina sem atravessar |
| 19 | Comer | Comer, Comer_Mastigar | alcançar o alimento real, ciclos de mandíbula | língua rígida (limitação) |
| 20 | Beber | Beber, Beber_Loop | focinho na superfície sem afundar a cabeça | altura ao ponto de água |
| 21 | Decolagem | Decolagem | flexão, impulso das patas e primeira batida coordenados | não subir antes do impulso |
| 22 | Voo | Voo | ombro/cotovelo/punho/dedos; corpo com atraso pequeno | laço sem estalo; raiz da asa presa (OMBRO_FIXO) |
| 23 | Voo rápido | Voo_Rapido | corpo inclinado, batida ajustada, patas recolhidas | não é só acelerar o Voo |
| 24 | Planeio | Planeio | ajustes sutis, cauda corrigindo a atitude | nem imóvel nem batendo |
| 25 | Pairar | Pairar | batidas que sustentam a massa; pés e cauda equilibram | passagem ao Voo sem queda |
| 26 | Subida / descida | Subida, Descida | atitude e esforço distintos; descer não é mergulhar | sem articulação invertida |
| 27 | Curvas | Curva_E/D | inclinação coordenada, asas diferentes, espelhamento correto | cavaleiro sem atravessar o pescoço |
| 28 | Mergulho | Mergulho, Mergulho_Saida | asas recolhidas no limite; recuperação progressiva | **verificar** a ligação ao misturador (hoje não está ligado) |
| 29 | Pouso | Pouso | asas freiam, patas projetam, impacto absorvido | pés sem afundar |
| 30 | Mordida | Ataque_Mordida | recuo, abertura, avanço, recuperação | marcador no contato real |
| 31 | Mordida aérea | Mordida_Aerea | ataque de cabeça mantendo o voo | asas sem pose impossível |
| 32 | Garras | Ataque_Garra_E/D | peso nos outros apoios, golpe, recolocar a pata | lados distintos |
| 33 | Cauda | Ataque_Cauda | quadril e tronco preparam; onda da base à ponta | contato acompanha a varredura |
| 34 | Dano | Dano_Leve, Dano_Forte | reação localizada ou ampla | sem stun novo; sem reiniciar o ciclo |
| 35 | Dano no ar | Dano_Leve_Ar, Dano_Forte_Ar | reação curta que mantém a sustentação | voo montado: integração pendente (todos os dragões) |
| 36 | Emboscada | Espreitar, Bote_Emboscada, Recuo_Sombra (**não existem**) | Espreitar: aproximação baixa com pés firmes. Bote: compressão, impulsão, contato, recuperação. Recuo: passos para trás com reposição de apoio | só estudo visual; nada de furtividade ou teleporte sem aprovação |
| 37 | Outros | Hab_* (12), Ninho_Alerta | Hab_* = movimento genérico, base dos poderes; Ninho_Alerta = alerta curto do ninho | não há clipe de morte nem regra de incapacitação |

## 5. Kit de Sombra — DEFINIDO PELO USUÁRIO em 03/11/2026 (números NAO_APROVADO, nada implementado ainda)

Escolha feita nesta conversa a partir das propostas. A segunda passiva, **Rastro do Breu**, foi aprovada depois, também em 03/11, e substitui integralmente a sugestão Instinto da Penumbra e as sugestões de mobilidade anteriores. A proposta completa continua abaixo, só como histórico. Regra oficial respeitada: só Sombra; 2 passivas e 3 ativas.

| Tipo | Nome | O que faz (decisão) | Slot de tecla | Base de animação |
|---|---|---|---|---|
| Passiva | **Marca Sombria** | Acertos de Sombra acumulam marcas no alvo. Cada marca aumenta o próximo dano Sombra do Sombrio contra ele. Sem lentidão e sem stun; decai fora de combate | — | nenhuma (efeito no alvo). **Implementada e testada em Play (03/11, NAO_APROVADO: até 5 marcas, +6%/marca, decai após 6 s)** |
| Passiva | **Rastro do Breu** | **Em combate:** ao perseguir um inimigo com Marca Sombria aplicada pelo próprio Sombrio, ganha impulso de velocidade no solo ou no voo. Termina ao deixar de persegui-lo ou quando as marcas acabam. Ter um inimigo marcado em outro lugar não dá bônus para fugir em outra direção. **Fora de combate:** depois de correr ou voar continuamente por um tempo, ganha impulso para explorar; ao parar, o impulso se desfaz. Os bônus dos dois modos **não se somam**. **Efeito:** linhas negras com bordas violetas saem atrás do corpo, das asas e da cauda, mais intensas durante o impulso, e se desfazem atrás do dragão; comunicam velocidade sem esconder a silhueta | — | nenhuma nova (locomoção existente). **Modos exploração (+15% após 4 s) e combate (+20% perseguindo alvo com marca própria) implementados e testados em Play (03/11, NAO_APROVADO)** |
| Ativa 1 | **Sopro Umbral** | Jato contínuo de névoa negra-violeta (segurar a tecla), com dano Sombra por tick e Marca. **Com vinheta leve** na tela do jogador atingido (só visual, curta, sem cegar) | 1 (sopro) | Hab_Preparo_Respiratorio / Hab_Emissao_Loop / Hab_Emissao_Fim (+ _Ar) |
| Ativa 2 | **Correntes da Noite** (IMPLEMENTADA 04/11, visual v4 APROVADO 04/11 — elos com furo encaixados, saem do chão, anel no tronco, DOCS/estado BY; números NAO_APROVADO; DOCS/estado BX: alcance 160, raio 16, até 3 alvos, aviso 0,5 s, preso 2,5 s, dano 10 + 4/0,5 s, alvo no ar não era preso até 04/11 — agora PRENDE no ar (fendas de sombra; DOCS/estado CF), resistência 6 s) | Correntes de sombra de **longo alcance** saem do chão sob os inimigos, **prendem** (não andam enquanto presos) e causam **dano Sombra contínuo** enquanto duram, aplicando Marca. Leitura "corrosiva", mas **não** é o elemento Veneno: interpretação registrada, a confirmar | 2 | Hab_Area (garras batem no chão) / Hab_Area_Ar |
| Ativa 4 (tecla 3) | **Passo Sombrio** (v2 IMPLEMENTADA 04/11, pedido do usuário; DOCS/estado CN: dragão e cavaleiro montado ficam invisíveis aos outros por 5 s com +60% de velocidade no chão e no voo; dono vê um vulto; não é invulnerável; sem trava/IA neles; sem dano; NAO_APROVADO. A v1 teleporte (CM) foi substituída) | Mobilidade | 3 | Hab_Investida |
| Ativa 3 | **Eclipse Dracônico** (IMPLEMENTADO 04/11, números NAO_APROVADO; DOCS/estado BZ: raio 60, detona em 2,15 s, 9 por marca, sem marca = 0, escuro 4 s; 04/11 a pedido do usuário: a área escura fere 3 a cada 0,5 s enquanto dura e o dragão segue rugindo — DOCS/estado CD) | Especial: rugido que escurece a área ao redor (correção de cor local) e **detona** as Marcas Sombrias dos inimigos ali (dano por marca). Sem invisibilidade, invulnerabilidade ou execução | 4 (especial) | Hab_Concentracao + Rugido_Combate |

Pendente de decisão (nenhum número foi inventado):
- dano, alcance, duração, recarga e energia de tudo;
- Rastro do Breu: velocidade adicional, duração e tempo de ativação (pendentes de balanceamento);
- máximo de marcas e decaimento;
- Correntes: tempo preso, resistência a prender de novo o mesmo alvo (a regra oficial do Basilisco já usa "resistência a controle repetido"), se prendem alvos voando (puxar para baixo?) e se o alvo preso pode atacar;
- se o slot 3 fica vazio ou recebe uma 4ª ativa no futuro.

Contrajogo pensado:
- Sopro: sair do cone.
- Correntes: aviso visual curto no chão antes de prender, para dar tempo de sair.
- Eclipse: sair da área na antecipação; não acumular marcas.
- Luz e Água resistem a Sombra pela matriz oficial.

Implementação exigirá autorização para arquivos compartilhados: `ConfigCombate` (forma Sombrio, kitForma), `Combate_Dragao.Nucleo` (funções novas), um módulo novo `VFXSombra` e `SonsConfig`/`SonsDragao_Cliente` (sons). Slots com os ids existentes: Sopro→SoproUmbral, Arremetida→Correntes, Coracao→Eclipse.

### Proposta anterior (histórico, 03/11)


Todos estão marcados **[PROPOSTA]**. Dano, alcance, duração, custo, recarga e limites estão **[PENDENTE]**: nenhum número foi inventado. O que guia a proposta é o texto oficial: Sombra como "ofuscação, ocultação e efeitos sombrios", o Sombrio como "pressão e emboscadas" e a Sombra como forma de "cortar rotas e atacar". Nada de invisibilidade, teleporte, roubo de vida, medo, execução ou invulnerabilidade.

### Passiva A — "Instinto da Penumbra" [PROPOSTA] (passiva mínima) — SUBSTITUÍDA por Rastro do Breu (03/11), não usar
- **Gatilho:** o primeiro golpe (básico ou habilidade) depois de um período sem receber nem causar dano [duração PENDENTE]. Recompensa a abertura de emboscada.
- **Benefício:** esse golpe causa dano Sombra extra [PENDENTE] e aplica 1 acúmulo de Marca Sombria (ver Passiva B, se aprovada).
- **Feedback discreto:** os olhos âmbar intensificam e um fio de névoa escura sai das narinas enquanto a passiva está pronta. Some ao disparar. Só no cliente, sem luz dinâmica.
- **Término e renovação:** dispara uma vez e rearma só depois de um novo período sem dano. Não acumula e não renova durante o combate contínuo.
- **Contra repetição:** recarga interna mínima [PENDENTE]; não vale contra o mesmo alvo duas vezes em X s [PENDENTE].
- **Decidir:** se vale também para ataques de voo; se o período conta "sem ser visto" (exige linha de visão no servidor, custo extra) ou só "sem dano" (mais simples).

### Passiva B — "Marca Sombria" [PROPOSTA] (opcional; papel parecido com o do Frostbite, mas sem controle)
- **Gatilho:** acertos de Sombra aplicam acúmulos [máximo PENDENTE] num alvo.
- **Benefício:** cada acúmulo aumenta o dano Sombra seguinte do Sombrio contra esse alvo [PENDENTE]. No acúmulo máximo, a próxima ativa consome a marca num estouro único de dano [PENDENTE]. **Sem lentidão nem stun**: pressão ofensiva, não controle.
- **Feedback:** fios de névoa violeta ao redor do alvo, mais densos por acúmulo, num anel simples (partículas com limite fixo). Jogadores veem a marca em si mesmos (contrajogo: recuar ou buscar luz/água se o mapa tiver).
- **Término:** decai acúmulo por acúmulo fora de combate [PENDENTE]. A morte do alvo e a troca de alvo zeram.
- **Decidir:** se é a passiva oficial, se acumula com aliados ou só com o próprio Sombrio, e o comportamento em PvP.

### Ativa 1 — "Sopro Umbral" (papel de sopro) — IMPLEMENTADO 04/11 (números NAO_APROVADO; ver DOCS/estado BW)
- Visual v2 (04/11, revisão, DOCS/estado BY): fluxo volumétrico de breu sem feixes/centelhas, para em paredes, nuvem de contato, preparo que converge para a boca; visual APROVADO pelo usuário em 04/11.
- Implementado: jato segurado (_Sopro) com Sombra, cone 95 studs/13°, dano 5 por pulso de 0,3 s (× Marca), 1 marca por alvo a cada 1 s de jato; clipes Sombrio_Sopro_Umbral_* (chão, _Camada, _Sup); visual VFXSombra (sem luz) e vinheta leve nas bordas da tela do jogador atingido.
- **Função:** jato contínuo de névoa negra-violeta. Dano Sombra por tick e aplicação de Marca.
- **Solo e ar; montado e selvagem:** solo parado ou andando devagar; no ar, pairando. Montado: segurar a tecla. Selvagem: IA a meia distância.
- **Antecipação:** pescoço recua, peito infla, asas abrem 30%, patas firmam. A mandíbula abre larga em 0,2–0,3 s.
- **Ação:** pescoço varre devagar (o jogador mira), cauda equilibra, asas sustentam no ar.
- **Origem e trajetória:** do osso `mouth_upper_tip` para frente, em cone estreito com névoa densa no núcleo e borda difusa.
- **Fases:** início, laço e fim. Clipes base: Hab_Preparo_Respiratorio, Hab_Emissao_Loop e Hab_Emissao_Fim (e as versões `_Ar`).
- **Marcador:** emissão quando a boca termina de abrir.
- **Área:** cone/cápsula à frente da boca [alcance PENDENTE], validado no servidor.
- **Leitura e som:** névoa escura com faíscas violeta; chiado grave contínuo, com início e fim distintos (som próprio, a definir).
- **Alvo:** dano por tick e Marca. "Ofuscação" opcional, só visual: vinheta leve na tela do jogador atingido [PENDENTE], **sem cegueira**.
- **Recuperação:** a boca fecha e a cabeça recua.
- **Cancelamento:** soltar a tecla, levar Dano_Forte, falta de energia.
- **Contrajogo:** sair do cone; Luz/Água (matriz) resistem.
- **Integração:** `ConfigCombate` (forma Sombrio), Nucleo (`_SoproUmbral`), VFX/SFX próprios (módulo novo VFXSombra).
- **Riscos e celular:** névoa é cara. Usar poucas partículas grandes com textura, sem luz por quadro, e limitar emissores por jogador.

### Ativa 2 — "Bote das Sombras" [PROPOSTA] (papel de investida/emboscada)
- **Função:** arremetida rasante curta em linha reta, com rastro de fumaça. O contato causa dano Sombra e aplica Marca; com a Passiva A pronta, dispara o bônus de emboscada.
- **Solo:** compressão (abaixa o peito), impulsão das traseiras, mordida no contato e recuperação com passos. Base: Hab_Investida e o futuro Bote_Emboscada.
- **Ar:** mergulho curto em direção ao alvo. Base: Hab_Investida_Ar.
- **Montado:** direção da câmera. **Selvagem:** a partir de Espreitar.
- **Antecipação:** 0,3–0,4 s bem legível (contrajogo): corpo baixo, asas coladas, cauda reta.
- **Trajetória:** linha reta com distância fixa [PENDENTE]. **Não é teleporte**: o corpo percorre o caminho e para em obstáculos.
- **Marcador:** contato no fechamento da mandíbula. Área = cápsula à frente da cabeça durante o avanço.
- **Leitura:** rastro escuro que se dissipa em 0,5 s; estalo seco no impacto.
- **Alvo:** dano e empurrão curto [PENDENTE]; sem stun.
- **Recuperação:** freio com passos (usa a técnica da Parada nova).
- **Cancelamento:** colisão, Dano_Forte.
- **Contrajogo:** desviar lateralmente durante a antecipação; Ar perde para Sombra pela matriz (pressão sobre voadores).
- **Integração:** reutilizar o movimento da Arremetida do Nucleo **só como mecânica de locomoção** (exige combinar), VFX próprio.
- **Riscos:** atravessar alvos ou paredes (usar `podePassar` da montaria).

### Ativa 3 — "Véu Crepuscular" [PROPOSTA] (papel de pressão de asas / cortar rotas)
- **Função:** batida forte das asas que projeta à frente uma cortina de névoa em arco, uma parede baixa e larga que dura alguns segundos [PENDENTE].
- **Efeito:** quem atravessa a cortina leva dano Sombra e Marca. A cortina bloqueia **só a visão** (efeito visual), não a passagem: é a "Cortina sombria" citada no RPG_02 para cortar rotas.
- **Solo:** Hab_Area (ergue o peito, abre e bate as asas para baixo e para frente, patas firmes). **Ar:** Hab_Area_Ar (batida para baixo, a cortina nasce no chão sob o dragão).
- **Antecipação:** asas erguem bem alto (leitura clara). Mandíbula entreaberta e rosnado.
- **Marcador:** emissão no ponto mais baixo da batida.
- **Área:** arco ou retângulo no chão [dimensões PENDENTES]; dano só ao atravessar ou ao surgir sobre o alvo.
- **Leitura e som:** onda de ar escura rente ao chão que vira névoa; rajada grave.
- **Recuperação:** asas voltam à pose.
- **Cancelamento:** Dano_Forte durante a antecipação.
- **Contrajogo:** contornar, ou esperar a cortina se dissipar; Luz resiste.
- **Integração:** zona temporária no servidor (o dano é decidido lá), visual no cliente.
- **Riscos e celular:** muita névoa → usar planos texturizados animados e no máximo N cortinas por servidor [PENDENTE].

### Ativa 4 (opcional) — "Eclipse Dracônico" [PROPOSTA] (papel de amplificação ofensiva / ultimate)
- **Função:** rugido longo que escurece uma área ao redor do Sombrio por alguns segundos [PENDENTE]. Lá dentro, as Marcas Sombrias dos inimigos são **detonadas** de uma vez (dano por acúmulo) e o Sombrio causa mais dano Sombra [PENDENTE].
- **Não** dá invisibilidade, invulnerabilidade nem execução.
- **Execução:** solo ou ar. Base: Hab_Concentracao + Rugido_Combate (antecipação longa, 0,8–1 s). Corpo ergue, asas abrem totalmente, crina eriçada (visual), olhos brilham.
- **Área:** esfera ou cilindro ao redor [raio PENDENTE].
- **Leitura:** a luz local escurece por correção de cor no cliente, só dentro da área (uma `ColorCorrection` local por jogador, sem luzes extras).
- **Contrajogo:** sair da área durante a antecipação; não acumular marcas.
- **Integração:** depende da Passiva B. Sem ela, vira só um rugido de bônus de dano.
- **Riscos:** ultimate forte em PvP; exige recarga longa e decisão de balanceamento.

### Matriz das propostas

| Proposta | Função | Animação exigida | Custo técnico | Resposta do adversário | O que precisa de aprovação |
|---|---|---|---|---|---|
| Instinto da Penumbra (passiva) | bônus de emboscada | nenhuma nova (feedback nos olhos/narinas) | baixo | evitar ser pego desprevenido; manter pressão | gatilho ("sem dano" ou "sem ser visto"), valores |
| Marca Sombria (passiva opcional) | acúmulo que amplia dano | nenhuma (VFX no alvo) | médio (estado por alvo no servidor) | recuar e deixar decair | se entra no kit; máximo; PvP |
| Sopro Umbral | dano contínuo a média distância | Hab_Preparo/Emissão (existem) | médio-alto (VFX de névoa) | sair do cone | ofuscação visual sim ou não; alcance |
| Bote das Sombras | emboscada / fechar distância | Hab_Investida (existe) + Bote_Emboscada (novo) | médio | desviar na antecipação | distância; empurrão; uso no ar |
| Véu Crepuscular | cortar rotas / pressão | Hab_Area(_Ar) (existem) | médio (zona temporária) | contornar ou esperar | bloqueia só visão?; duração; limite por servidor |
| Eclipse Dracônico (opcional) | ultimate de pressão | Hab_Concentracao + rugido (existem) | alto | sair da área | se é 4ª ativa; depende da Marca |

### 5.x IA selvagem com o kit (04/11, DOCS/estado CO; tática NAO_APROVADO)
- `Sombrio_Guardiao` (ninho `Ninho_Sombrio`, Laboratorio_IA) usa o kit inteiro: Correntes à distância ou contra alvo
  no ar; Eclipse com 2+ alvos na área ou 1 alvo com 3+ marcas; Passo Sombrio ferido (< 35%) ou para alcançar alvo a
  mais de 110 studs (o Locomotor recebe o +60%); Sopro Umbral até 95; garra/mordida/cauda de perto.
- Limite atual: ferido ele fica invisível mas não recua (o Cerebro não tem regra de fuga).

### 5.y Sons do kit (04/11, DOCS/estado CP; aprovados pelo usuário em 04/11)
- Módulo `SonsSombra` (só Pro Sound Effects): sucção reversa, vozes de espírito, zumbido maligno e respiração oca; correntes de metal nas Correntes; golpes graves na detonação do Eclipse; Passo com respiração baixa e de curto alcance enquanto invisível.
- Voz própria do Sombrio (05/11, DOCS/estado CQ, aprovada de ouvido): tigre grave (Tiger Roars/Hiss/Growls) com rosnado oco de espírito em camada, respiração de boi, dano de urso-polar; asas de membrana suave e passos acolchoados (padrão calmo de todos os dragões).

### 5.z Mergulho de bico jogável (10/11, DOCS/estado CY; TESTE, NAO_APROVADO)
- Montado em voo: **V** (ou botão de toque) = virada → asas fechadas, queda de bico → freio batendo as asas perto do chão/obstáculo → voo parado baixo. V de novo ou Espaço/E cancelam (freia). Locomoção, sem dano/custo/recarga; ativas bloqueadas durante a manobra. Só o Sombrio (`ConfigMontaria.mergulhoPicado.formas`).
- Vento no chão nas batidas do freio (`VentoMergulho_Cliente`): ar transparente radial; poeira só em material solto; spray em água.
- Evidência: `BLENDER/Criaturas/Teste_IA/dragao_sombra/review/mergulho_jogavel/`. Gamepad sem botão livre (não mapeado).

### 5.z2 Mergulho v2 (10/11, DOCS/estado CZ; TESTE, NAO_APROVADO)
- Clipes próprios: Mergulho_Entrada (recolhe em sequência), Mergulho_Picado v2 e Mergulho_Freio (abre, 2 batidas, chega no Pairar). O Pairar foi reexportado na convenção do jogo (antes tocava espelhado: peito para baixo, cauda para cima) e sem o tranco de cabeça a cada batida.
- Gerar: `source env_clipes_sombrio.sh` + `MERGULHO_V2=1 SINAL_FIXO=1 PIC2='{"cab":18,"cima":-26,"cauda":3}'`; exportar com `CONVENCAO_ROBLOX=giro180y`. Os demais clipes do Sombrio ainda tocam espelhados (pendente de aprovação).

### 5.z3 Clipes na convenção do jogo (10/11, DOCS/estado DA)
- Todos os KFS do Sombrio no Studio agora tocam como no Blender (antes espelhados em pitch/rolagem). Exportar sempre com `CONVENCAO_ROBLOX=giro180y`. Desfazer = aplicar a mesma conversão de novo.

## 6. Etapa 1 executada (03/11): ciclo de chão

- **Parado, Andar, Correr:** testados em Play no `workspace.Sombrio`, com o corpo movido nas velocidades de ritmo (7,9 e 18,94 studs/s). Pé no apoio a ~11% da velocidade do corpo, igual ao Glacial certificado medido no mesmo teste. No Parado, o pé desliza 0,02–0,05 stud.
- **Parada — defeito encontrado e corrigido:**
  - na montaria, a frenagem toca a Parada por 0,9 s enquanto o corpo freia de 22 para ~8,5 studs/s;
  - a Parada antiga mantinha os pés presos ao corpo, e um pé apoiado escorregava 10–15 studs (o Glacial tem o mesmo defeito: 11 studs);
  - a nova (`dragao_sombra/clipe_parada_sombrio.py`) usa a passada do próprio Correr desacelerada na mesma taxa do freio, mais a postura de frenagem no pescoço, cabeça e cauda;
  - resultado em Play (3 rodadas + 1 com o clipe gravado): maior deslize num apoio 0,9–2,7 studs (antes 10–12), total da frenagem 1,3–7,6 (antes 13–28).
- **Evidência:** `BLENDER/Criaturas/Teste_IA/dragao_sombra/review/anim_chao/`:
  - `ciclo_chao_antes_depois.mp4` (lado a lado, 9 s);
  - `.gif`;
  - `tira_frenagem_antes_depois.png`.
- **Limites:**
  - a frenagem foi calibrada para começar a 22 studs/s; começando de 11–20 studs/s o casamento fica aproximado;
  - a troca Correr → Parada não sincroniza a fase da passada;
  - montaria real com jogador **não testada**; celular e multiplayer **não testados**; FPS não medido nesta etapa.

## 7. Arquivos compartilhados que vão exigir autorização

- `ConfigCombate` (forma Sombrio: elemento, habilidades, passivas, kitForma), `Combate_Dragao.Nucleo` (funções dos poderes) e um VFXSombra novo (`ReplicatedStorage.Combate_Dragoes`): só depois de o kit ser aprovado.
- `SonsConfig` / `SonsDragao_Cliente`: voz, asas e passos próprios do Sombrio (hoje herdados).
- `MovimentoVivo.Perfis`: um perfil `Sombrio` (hoje usa `Silverwing`).
- ~~`Teste_Montaria_Dono`~~: **feito em 03/11** a pedido do usuário (o Sombrio entrou na lista; seção BL).
- `meshy/anim_silverwing.py`: para corrigir a cauda no Sentado, o afundamento no descanso e gerar Espreitar/Bote/Recuo pelo gerador. A alternativa é fazer scripts próprios do Sombrio, como a Parada.
- Opcional: aplicar a mesma correção da Parada ao Glacial e ao Fogo, que têm o mesmo defeito. Isso exige o chat de cada um.
