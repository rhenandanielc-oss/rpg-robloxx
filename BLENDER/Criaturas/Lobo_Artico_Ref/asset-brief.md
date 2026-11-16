ASSET      CR_LoboArtico (Adulto) — criacao do zero a partir de ref/lobo-artico-referencia.png
           (copia de REFERENCIAS/tundra-congelada/lobo-artico/lobo-artico-referencia.png; prevalece sobre os paineis antigos)
CATEGORY   criatura quadrupede digitigrada (canideo), domesticavel, Tundra Congelada
VIEWS      unica imagem: perspectiva, lado ESQUERDO do lobo com leve 3/4 de frente, camera perto da altura do ombro,
           lente ~45-50 mm. Serve para identidade, silhueta e materiais; NAO para medir proporcoes exatas
           (a perspectiva aumenta a cabeca e o peito, mais perto da camera).
SCALE      1 unidade Blender = 1 stud. Porte OFICIAL: 5,5-7 studs ate os ombros (RPG_02).
           Alvo: cernelha ~6,3-6,8 com o pelo; frente = -Y, pes em Z = 0, lado esquerdo = +X.
PROPORTIONS (estimadas na referencia, tolerancia larga)
           - corpo robusto e alongado: peito ao quadril ~1,2x a altura do ombro
           - peito fundo (fundo do peito ~ metade da altura)
           - juba muito volumosa no pescoco e ombros, babador descendo no peito
           - cabeca larga com colar nas bochechas, focinho definido, nariz escuro, olhos azul-gelo
           - patas largas, cauda longa e cheia pendendo ate perto do chao
PARTS      Corpo (pele unica, deforma) | Orelhas E/D (pecas, presas ao cranio) | Olhos E/D | Garras x16 |
           Pelagem (cartoes de mechas com alpha, deformam com a pele) | Cristais x6 (rigidos, presos ao trecho toracico)
MATERIALS  pelagem branca com sombras cinza frias; nariz/labios/contorno dos olhos escuros; orelha interna cinza;
           olhos azul-gelo com brilho leve; cristais azul translucido; marca ciano emissiva no ombro esquerdo
APARENCIA  cristais e marca sao SO aparencia: nao definem elemento, poderes nem atributos (elemento e kit PENDENTES)
INFERRED   [PROPOSTA] lado direito (oculto): SEM marca (nao se inventa simetria); cristais centrados na linha do dorso
           com 1 cristal pequeno do lado direito; peito/ventre, traseira, patas traseiras e parte de baixo da cauda
           seguem a anatomia de lobo; numero de dedos 4 por pata (sem ergot visivel).
ADAPTACOES (diferencas deliberadas para animar / custo)
           - pose neutra em pe (a referencia ja esta em pe), cabeca para frente, cauda pendendo
           - cristais espacados, inclinados para tras, so sobre o trecho toracico (pescoco e lombo dobram livres)
           - nenhum cartao de pelo nasce na area da marca nem a menos de 0,45 stud dos cristais
           - marca na TEXTURA (emissao), nao em geometria: acompanha a pele sem pecas soltas
           - pelos finos da referencia viram mechas: geometria nos volumes + ~3.100 cartoes curtos/longos
           - sopro de vapor da referencia e cenario: fora da entrega
TARGET     Roblox, GLB; MeshPart <= 20k tris; texturas finais <= 1024; bake intermediario 2048
