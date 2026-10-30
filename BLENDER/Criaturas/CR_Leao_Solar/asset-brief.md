# Brief do asset: CR_Leao_Solar (Fase 0, skill blender-image-to-3d)

Fontes oficiais:
- **Catálogo:** `Biblioteca_Criaturas.Catalogo.Leao_Solar` (RPG_02): felino colossal anatomicamente natural, Planícies Douradas, terrestre, **10–13 studs até o ombro**.
  - Padrões: Dourado Solar, Bronze Selvagem, Areia Clara.
  - Habilidades: Salto Solar, Rugido de Comando, Garra Circular, Foco do Predador.
  - Montaria: adulto, sela felina.
- **Referência visual:** `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/01-lobos-urso-leao.png`, painel 04. É direção de arte; em conflito, valem os documentos oficiais.

```text
ASSET      CR_Leao_Solar
CATEGORY   creature, quadruped (felino, digitígrado), juba volumosa, cauda com tufo
VIEWS      ref/lateral_esquerda_matte.png: silhueta lateral ESQUERDA (cabeça à direita da imagem), quase ortográfica
             (miniatura de 178x114 ampliada 4x; precisão ~±5%), az 270, el 0, lens 0; o sujeito ocupa 97,8% da altura; chão na última linha
           ref/conceito_principal.png: conceito em perspectiva, 3/4 lateral-frontal pela direita, câmera baixa, lens ~35;
             só para silhueta, superfície e cor, NUNCA para proporções
           ref/rosto.png, ref/juba.png: detalhes (olhos âmbar, focinho, mechas da juba)
SCALE      ombro 11,5 studs (meio da faixa oficial 10–13). 1 unidade Blender = 1 stud (importar no Roblox com Scale Unit = Stud).
           Matte: dorso/cernelha a 218 px do chão → 0,0528 stud/px. Topo da juba 18,9; comprimento total 26,9 (focinho à curva da cauda).
           CONFLITO: no painel, o humano mede 0,84 do ombro (~184 px); no jogo, 5,2/11,5 = 0,45. Vale o oficial (10–13);
           a figura humana do painel não é usada para escala.
PROPORTIONS (razões medidas no matte, unidade = altura do ombro 218 px)
           1 topo da juba / ombro               = 1,64
           2 garupa (anca) / ombro              = 0,96
           3 linha da barriga (meio) / ombro    = 0,33
           4 fundo do peito (entre patas dianteiras) / ombro = 0,23
           5 comprimento do tronco (nádega → peito) / ombro = 1,56
           6 focinho: altura / ombro            = 0,92 (cabeça erguida, olhar à frente)
           7 frente da juba à nádega / ombro    = 1,73
           8 base da cauda: altura / ombro      = 0,80
           9 ponto mais baixo do arco da cauda / ombro = 0,40
           10 tufo da cauda: topo / ombro       = 1,24
           11 cauda (comprimento ao longo da curva) / ombro = ~1,30
           12 patas: distância entre apoio dianteiro e traseiro / ombro = 1,35
PARTS      (ordem de construção e sobreposição)
           tronco (caixa torácica e pelve como elipsoides separados, sob a pele) | malha deformável | raiz
           pescoço | deformável | tronco, pivô na base do pescoço
           cabeça (crânio, focinho, nariz) | deformável | pescoço, pivô na nuca
           mandíbula | objeto separado | cabeça, pivô na articulação têmporo-mandibular (abertura do rugido)
           olhos ×2 | separados (âmbar) | cabeça
           juba (massa de mechas em camadas, mais escura na base) | separada, deformável pelos ossos do pescoço/cabeça/peito | pescoço
           patas dianteiras ×2 (escápula, ombro, cotovelo, carpo, pata) | deformáveis | tronco
           patas traseiras ×2 (anca, joelho, jarrete, pata) | deformáveis | pelve
           garras ×18 (5 dianteiras e 4 traseiras por lado), retraídas | separadas | patas
           cauda (cadeia longa) + tufo | deformável | pelve
SILHOUETTE 1 juba enorme que envolve cabeça, pescoço e peito, mais alta que o dorso (1,64 do ombro)
           2 dorso reto e garupa quase no mesmo nível, barriga recolhida
           3 cauda longa em arco baixo terminando em tufo erguido
           4 patas fortes, dianteiras grossas, pose altiva com a cabeça erguida
           5 focinho largo e curto, de felino
MATERIALS  pelagem curta do corpo: dourado-castanho (#C8945A..#E0B070), rugosidade 0,75–0,9, sem brilho
           juba: laranja-ouro nas pontas, castanho-avermelhado na base (#E89A3A → #8A3A18), rugosidade 0,85
           focinho e queixo: creme (#EAD2A8); nariz: castanho-rosado escuro; olhos: âmbar (#E0A030)
           tufo da cauda: laranja-castanho escuro; garras: osso escuro; sem efeitos mágicos e sem brilho emissivo
ARTICULATION família quadrúpede (rigging-animation.md), pele deformável, até 4 influências.
           Sockets: boca (mordida/rugido), olhos, 4 patas, sela atrás da cernelha (montaria oficial: sela felina).
           Animações (Fase 8, só quando aprovado): Repouso, Andar, Trote, Corrida, VirarE/D, Observar, Rugido;
           habilidades oficiais como animação sem efeitos: SaltoSolar, RugidoDeComando, GarraCircular, FocoDoPredador.
INFERRED   frente, trás e topo (não há essas vistas): largura do corpo pela anatomia de leão (~0,42 do ombro no peito), # inferred
           lado direito espelhado do esquerdo; forma da cabeça sob a juba e da mandíbula pelo conceito e pelo rosto; # inferred
           posição das articulações pelas regras de quadrúpede (categories.md); garras retraídas # inferred
TARGET     Roblox; GLB (e FBX); orçamento ≤ 16.000 tris (limite de MeshPart: 20k); 1 textura de cor 2048 por padrão + normal;
           câmera de jogo: az 35, el 20, distância 55, lens 35; sujeito com ~128 px na distância típica
```

## Decisões de unidade
A skill sugere 1 unidade = 1 m. Este projeto já entrega todas as criaturas em **1 unidade = 1 stud**, então ruler, capsule (raio 1, altura 5,2 = personagem do Roblox), porta (4×8) e célula (4) foram convertidos para studs.
