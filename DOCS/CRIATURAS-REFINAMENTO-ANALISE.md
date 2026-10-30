# Fase de refinamento das criaturas: análise antes de modificar (26/10/2026)

**Base:** os 16 blockouts de `BLENDER/Criaturas/Blockouts` (a silhueta principal é preservada; nada recomeça do zero).

**Fontes consultadas:**
- `RPG_Referencias_Visuais_GitHub/REFERENCES`:
  - `00_ART-DIRECTION`;
  - os 4 painéis de `03_CREATURES` (imagem principal, recortes de detalhe, silhueta e palavras-chave);
  - o `README` com as regras de uso.
- `MASTER-PROMPT.md` e `SPECIFICATIONS/BIOMES-ART-BIBLE.md`: "fantasia realista, visual cinematográfico e natural".
- `RPG_02` (medidas e anatomia oficiais) e `DOCS/ECOLOGIA-FAUNA.md`.

## O que as referências pedem (comum a todas)
- **Realismo:** concept art de jogo cinematográfico, com anatomia de animal real exagerada só em escala e ornamento. Nada de proporção infantil (cabeça grande, olho grande, membros curtos e gordos).
- **Massa e peso:** apoio firme no chão, peso visível no peito e nos ombros, membros com articulações legíveis.
- **Identidade pela cabeça e pela superfície:** cada painel destaca em close a cabeça, a pata/garra e o material (pelo, escama, placa, cristal).
- **Diferença regional:** Lobo Ancestral "esguio · ágil" × Lobo Ártico "robusto · poderoso"; os Dragões pelos materiais (rocha vulcânica / cristais de gelo / escamas de sombra), pelos chifres e pelas asas.

## Problemas comuns nos blockouts atuais
1. **Membros "tubo":** cilindros com afinamento uniforme, sem marcos de articulação (cotovelo, carpo, jarrete, joelho), sem grupos musculares e com patas em forma de "panqueca". Por isso as criaturas não parecem capazes de correr nem de apoiar o peso.
2. **Superfície de "balão":** a suavização forte apagou os planos ósseos (espinha da escápula, crista ilíaca, costelas, arcada zigomática). Tudo parece inflado.
3. **Cabeças genéricas:** vários focinhos são o mesmo cone. De frente, os canídeos parecem cavalo/lhama e os Dragões, cachorros.
4. **Inserção dos membros:** a pata "brota" do tronco sem ombro e sem quadril que a recebam.
5. **Asas:** a membrana é um leque plano preso ao flanco, sem propatágio (a membrana dianteira, do ombro ao punho), sem ligação natural ao corpo/perna e sem espessura variável.

## Análise por criatura

| Criatura | Referência (GitHub) | Problemas atuais | Correções propostas |
|---|---|---|---|
| **Leão Solar** | Majestoso, juba enorme laranja/dourada em mechas, cauda com tufo, pose altiva | Juba "capacete" lisa; patas tubo; focinho de bola; corpo sem planos de leão (ombro alto, cintura fina) | Juba em **mechas grandes** com caimento (sem pelo fino); crânio felino (testa larga, focinho curto e quadrado, maçãs); escápula e cotovelo marcados; antebraço grosso; pata felina com 4 dedos; ventre recolhido; coxa e jarrete |
| **Lobo Ancestral** | Esguio, ágil, pelo com musgo/folhas ("natural armor") | Cabeça de cavalo de frente; pescoço tubo; patas sem pastern; ombro como bola | Crânio canino em cunha (stop, focinho afinando); orelhas eretas; peito fundo e estreito; **pastern** (metacarpo inclinado) e pata digitígrada com dedos; jarrete angulado; cauda em pincel. O musgo fica para a fase de material |
| **Lobo Ártico** | Robusto, pelo muito espesso, olhos azuis | Igual ao Ancestral + volume uniforme | Mesma base, com **colar e calças de pelo** em mechas grossas; patas largas para neve; focinho um pouco mais curto e largo (adaptação ao frio). Silhueta mais "fofa", sem perder anatomia |
| **Urso Silvestre** | Massivo, corcova, boca aberta, garras longas, musgo/folhas | Cabeça "ursinho" de frente (orelhas no topo, face achatada); patas colunas; sem garras | Crânio ursídeo (focinho médio e alongado, testa inclinada); **corcova muscular**; patas plantígradas largas com **garras longas** (o painel destaca); dobra no cotovelo; garupa baixa |
| **Búfalo Colossal** | Bisão gigante: corcova, pelo espesso, **chifres grandes curvos** | Chifres pequenos; cabeça bola; capa de pelo uniforme; patas tubo | Chifres **grandes**, curvados para fora e para cima (como no painel); cabeça larga e baixa com testa de pelo; barba; capa até o joelho; patas fortes com **casco fendido**; traseiro menor e firme |
| **Cérbero Sombrio** | 3 cabeças escalonadas, muscular, rosnando, pelo e placas corrompidas | 3 cabeças iguais na mesma altura (de "cavalo"); pescoços separados demais | **Pescoços fundidos num peito único**; cabeças em alturas diferentes (central mais alta), focinhos de predador com rugas e mandíbula forte; ombros enormes; garras. As rachaduras/brilho vermelho são efeito/material, para depois |
| **Crocodilo Primordial** | Mandíbula massiva (aberta), couraça, cauda devastadora | Pescoço/cabeça "de jacaré de borracha"; patas tubo; osteodermos como bolinhas | Crânio largo e plano com **mandíbula pesada** e linha de dentes; olhos e narinas no topo; placas dorsais em **escudos** (osteodermos quadrados) em fileiras; patas com cotovelo para fora e dedos com garras; cauda com crista dupla |
| **Basilisco** | Escamas blindadas, cristas espinhosas grandes, olhar venenoso, cauda enrolada | Cabeça de cachorro; espinhos de cone; patas de cavalo | Cabeça reptiliana angulosa com **arcadas pesadas sobre os olhos** (olhar ameaçador); cristas em **lâminas** (placas espinhosas, não cones); patas semi-eretas com cotovelo e dedos com garras; pescoço mais grosso |
| **Lagarto Cristalino** | Robusto, aglomerados de cristais naturais grandes e variados | Cristais como cones iguais e simétricos ("orelhas de coelho" de frente) | **Aglomerados** de prismas hexagonais de tamanhos e inclinações variadas (natural, assimétrico); cabeça de lagarto com placas; patas fortes com garras |
| **Escorpião Colossal** | Pinças **massivas**, carapaça espinhosa, ferrão | Pinças pequenas; pernas "palito"; segmentos lisos | Pinças grandes e espessas (mão + dedo fixo + dedo móvel com dentes); pernas segmentadas com articulações; carapaça com bordas, sulcos e espinhos; ferrão em gancho |
| **Serpente Marinha** | Cabeça dracônica com cristas e babados, nadadeiras longas, corpo escamado em S | Corpo muito baixo/achatado; cabeça pequena; nadadeiras pequenas | Corpo hidrodinâmico mais alto (seção oval vertical); **cabeça dracônica maior** com cristas em leque e mandíbula; nadadeira dorsal contínua e nadadeiras laterais longas; ventre com escamas largas |
| **Leviatã Jovem** | Colossal, couraça, cristas dorsais espinhosas, nadadeiras grandes | Cabeça de foca; corpo de "salsicha"; placas de cone | Cabeça massiva de réptil marinho (crânio longo, mandíbula com dentes); **4 nadadeiras** grandes em remo; couraça em placas; cristas em leque; cauda musculosa com nadadeira vertical |
| **Wyvern** | Leve, asas enormes, ferrão venenoso, ágil | Asas como leque plano; corpo fino demais; pernas sem garras fortes | **Asa-braço**: úmero, antebraço, punho com garra, 3 dedos longos; membrana do flanco até a coxa; propatágio; **pernas traseiras fortes** com garras de rapina; ferrão em gancho; cabeça com chifres para trás |
| **Dragão das Montanhas** | Massivo, escamas vulcânicas, formações rochosas, asas enormes | Cabeça de cachorro; pescoço tubo; asas leque; patas de elefante | Crânio dracônico (focinho longo, mandíbula, chifres múltiplos para trás); placas rochosas no dorso; patas com garras grandes; asas com 4 dedos + propatágio + membrana até a coxa; peito em quilha |
| **Dragão Glacial** | Esguio, cristais de gelo, asas enormes | Igual à base + cristais pequenos | Mais esguio; **espinhos cristalinos** altos e finos (em leque) no dorso e no pescoço; chifres retos; asas mais longas e finas |
| **Dragão Sombrio** | Agressivo, chifres espinhosos, asas recortadas, escamas de sombra | Igual à base + espinhos | **Coroa de chifres**; espinhos duplos maiores; asas com bordas rasgadas e esporas; postura mais baixa e ameaçadora. O brilho magenta é efeito, para depois |

## Famílias anatômicas (estrutura-base reaproveitada, proporções próprias)
- **Canídeos:** Lobo Ancestral, Lobo Ártico, Cérbero (base `lobo_base`).
- **Felino:** Leão Solar (base própria).
- **Quadrúpedes pesados:** Urso (plantígrado), Búfalo (ungulado). Bases diferentes.
- **Reptilianos terrestres:** Crocodilo (espalhado), Basilisco e Lagarto (semi-eretos). Mesma lógica de membro, crânios distintos.
- **Artrópode:** Escorpião.
- **Aquáticos:** Serpente Marinha (sem patas), Leviatã (4 nadadeiras).
- **Voadores:** Dragões (quadrúpede + 2 asas, base `dragao_base`), Wyvern (bípede, asa-braço).

## Técnica do refinamento (skill blender-image-to-3d, Fase 3 "Forms")
1. **Membros por grupos musculares**, com marcos ósseos nas posições anatômicas. Patas e pés **específicos por família**: dedos e almofadas, casco fendido, pé plantígrado, pata de réptil com garras.
2. **Duas camadas de suavização:** tecido mole suavizado; marcos ósseos e planos (escápula, quadril, arcadas, focinho) com suavização leve, para manter a leitura de planos.
3. **Construtor de cabeça por família:** crânio, arcadas, focinho em caixa ou cunha, mandíbula separável para o rig, orelhas e cornos.
4. **Asas reconstruídas:** propatágio + plagiopatágio ligado ao flanco/coxa; dedos finos com membrana recortada; espessura maior na raiz.
5. **Controle:** cada criatura é comparada de novo à silhueta oficial (`world_gate`, para não perder a silhueta aprovada). As folhas de frente, lateral, 3/4 e 128 px são refeitas, e o limite de 20.000 tris por objeto se mantém.

## Conflitos entre referências e documentos (prioridade aplicada)
1. **Escala do humano nos painéis:** os painéis mostram o humano com escala diferente da oficial (ex.: Leão ~1,1× o humano no painel, contra 2,2× pelo RPG_02).
   - Decisão: **medidas oficiais do RPG_02**, como diz o README das referências.
   - Proporções e forma seguem os painéis.
2. **Brilhos e energia** (rachaduras vermelhas do Cérbero, magma do Dragão das Montanhas, magenta do Sombrio, ferrão verde da Wyvern, cristais luminosos): material e efeito, **não geometria**. Ficam para a fase de materiais/VFX, sem inventar detalhe agora.
3. **Wyvern bípede** e detalhe de asa: o RPG_02 marca como [PROPOSTA VISUAL]. O painel confirma essa leitura (duas patas, asas como braços), então sigo o painel.
4. **Musgo e folhas** sobre Lobo Ancestral e Urso: superfície (material/acessório), não anatomia. Ficam para depois.

## Ordem proposta
1. Canídeos.
2. Felino.
3. Pesados.
4. Reptilianos.
5. Artrópode.
6. Aquáticos.
7. Voadores.

As folhas antes/depois de cada família serão mostradas ao final; nada será importado no Roblox.
