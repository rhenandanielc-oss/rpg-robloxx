# Leão Solar — ficha do subchat

Criatura **domesticável** das **Planícies Douradas**. Espécie-base **Leão**, que tem uma única forma regional: o Leão Solar.

Fontes: `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO` (topo 30/10, §1, §2, ficha "Leão — Leão Solar [FICHA-BASE FINALIZADA]", tabela de padrões §10, Etapa 24.1/24.2, §19.2). O `RPG_01` só cita o Leão no catálogo. A **ATUALIZAÇÃO OFICIAL de 30/10/2026** prevalece sobre o que vem depois no documento.

Regras de convivência: `DOCS/ORGANIZACAO-CHATS.md`. Studio um chat por vez (`DOCS/estado/studio-em-uso.md`).

Ficha criada em 03/11/2026, só com leitura. Nada foi alterado no Studio, em `src/` nem em arquivos compartilhados.

## 1. Identidade

| Item | Valor | Status |
|---|---|---|
| Bioma | Planícies Douradas | [OFICIAL] |
| Corpo | Felino colossal, **anatomicamente natural** | [OFICIAL] |
| Porte adulto | **10–13 studs até os ombros** (altura, não comprimento) | [OFICIAL] |
| Papel | Ataques explosivos, intimidação e dano concentrado; ataques de abertura poderosos | [OFICIAL] |
| Rugido | "Bônus moderados ao Rugido": o Rugido de Comando fortalece o Leão e dá **pequenos** bônus temporários a aliados próximos, **sem** substituir o Urso como defensor e **sem** tornar o Leão curandeiro | [OFICIAL] |
| Fraqueza | **Alto gasto de energia** nos ataques explosivos; impede sequências explosivas contínuas | [OFICIAL] |
| Vantagem ambiental | Nas Planícies, maior eficiência de **arrancada** e ataque em **campo aberto** | [OFICIAL] |
| Estágios | Ovo + 5 modelos (Bebê, Jovem, Pré-adulto, Adulto, Ancião) — regra geral | [OFICIAL] |
| Montaria | A partir do **Adulto**, com **sela adaptada a corpo felino** | [OFICIAL] |
| Ataque básico | Fora dos slots de habilidade (regra geral de 30/10). Golpes específicos do Leão não descritos | [OFICIAL] / [PENDENTE] |
| Padrões visuais | **Dourado Solar**, **Bronze Selvagem**, **Areia Clara**. Só cosméticos, separados da raridade e do elemento | [OFICIAL] |
| Cores exatas de cada padrão | Não confirmadas (o brief do Blender usa tons próprios para o Dourado Solar) | [PENDENTE] |
| Evolução estética por estágio e adornos por raridade | — | [PENDENTE] |
| Painel de referência | `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/01-lobos-urso-leao.png`, painel 04. Direção de arte; em conflito, valem os documentos. O humano do painel está fora de escala (≈1,1× contra 2,2× oficial) | referência visual |

## 2. Elemento e habilidades

### Elemento
- **[OFICIAL — 30/10/2026]** Cada criatura tem **um único elemento natural**. Não há 2º/3º elemento, alternância nem fusão elemental.
- **[PENDENTE]** O elemento único do Leão Solar **ainda não foi escolhido**.
  - A lista "Fogo, Luz, Ar" da ficha-base (com "no máximo três por indivíduo") é anterior a 30/10 e virou histórico. Não presumir nenhum dos três.
  - O nome "Solar" não exige Luz: a própria ficha diz que "Salto Solar" não exige afinidade Luz.

### Habilidades
- **[OFICIAL — 30/10/2026]** Cada criatura tem no mínimo **1 passiva + 3 ativas**. Nomes, efeitos e quantidades são aprovados criatura por criatura. As listas de quatro habilidades viram referência anterior.
- **Lista da ficha-base** (nomes e papéis gerais marcados [OFICIAL] antes de 30/10; a lista final da forma está **[PENDENTE]**):
  1. **Salto Solar** — ataque explosivo de aproximação que permite continuar a sequência ofensiva.
  2. **Rugido de Comando** — fortalece o próprio Leão e dá pequenos bônus temporários a aliados próximos.
  3. **Garra Circular** — golpe com as patas dianteiras que ameaça um arco próximo e abre espaço.
  4. **Foco do Predador** — concentra a ofensiva num alvo e melhora a percepção de oportunidades de ataque.
- **Passiva:** nenhuma definida. **[PENDENTE]**
- **[PENDENTE]** Energia, dano, recarga, alcance e duração de cada habilidade.
- **[PROPOSTA — histórico, superada]** Versões por afinidade (Fogo/Luz/Ar) e as 6 fusões direcionais do Leão contrariam a regra de elemento único. Não implementar.

## 3. Atributos (Etapa 24)
- **[OFICIAL — 24.1]** São 6 atributos: Vida, Defesa, Força, Velocidade, Energia e Poder Elemental. Comparação entre Adultos de nível 100. Vantagem ambiental de 10–15%; raridade influencia 1–5%.
- **[PROPOSTA — 24.2, NÃO APROVADA; mantida só como referência inicial]** Números do Leão Solar:
  - escala 1–5: Vida 3, Defesa 2, Força 5, Velocidade 5, Energia 2, Poder Elemental 4;
  - valores absolutos: 3.850 HP, Defesa 100, Força 205, Energia 100, Poder Elemental 155;
  - velocidade: terra 42 studs/s (manobra 5), água 12 studs/s (manobra 1), sem voo.
  - Coerente com o papel: muita força e arrancada, pouca energia.
- **Comparação [OFICIAL] dentro das Planícies:** o Leão prioriza ataques explosivos e mobilidade inicial; o Búfalo usa força massiva e aceleração crescente.
- **[SIMULAÇÃO ILUSTRATIVA, NÃO OFICIAL]** Duelos de teste em §19.2: Urso Silvestre × Leão Solar; Búfalo Colossal × Leão Solar.

## 4. Mundo e habitat (segundo os registros do mapa; não conferido nesta sessão)
- `DOCS/estado/mundo-planicies.md` e `DOCS/ECOLOGIA-FAUNA.md`: rede `workspace.Planicies_Douradas.Habitats.Ecologia_Fauna` com **4 bandos** de leões, tudo **marcadores invisíveis, sem IA**:
  - L1 Colinas do Horizonte (−2450, 3350); L2 Bosques Solitários (1250, 5150); L3 Capim Alto Leste (1900, 4400); L4 Campina das Flores (−1650, 5550).
  - Por bando: `Territorio_Bando`, `Mirante_Observacao` (`VeAlvos`), `Descanso_Sombra` (`Arvore`), `Zona_Caca` (`Alvo`), `Ponto_Emboscada` (`Cobertura`, a 50–80 studs), `Rota_Aproximacao`, `Caminho_Presas`.
  - Cenas para IA futura: `Cena_Leao_Observa`, `Cena_Perseguicao`, `Cena_Caca_na_Agua`, `Cena_Encontro_Jogador` etc.
  - 4 ninhos inativos. Os marcadores antigos do M4 (`Leao_Solar`) foram para `Proto_Restore/Retirados_Planicies_Habitats_M4`.
- **[OFICIAL]** Ninhos raros, reaparecem em 30–60 min. Quantidade por jogador ainda é [PROPOSTA].
- **[PENDENTE]** Tamanho do bando (o RPG_02 não define). Lore do nascimento de mamíferos por ovos. Dieta.
- O mapa/terreno é **compartilhado**: qualquer mudança nele precisa ser combinada com o usuário e com o chat do bioma.

## 5. O que já existe

### Roblox Studio (segundo os registros; não conferido nesta sessão)
- `ServerStorage.Biblioteca_Criaturas.Catalogo.Leao_Solar` registra a forma (citado no `asset-brief.md`).
- **Nenhum modelo aprovado no Studio.** O leão do gerador do Studio foi **reprovado por ser caricato** e está em `Proto_Restore.Retirados_C1` (atributo `Motivo`).
- `DOCS/CRIATURAS-C1-MATRIZ.md`: Leão Solar = "Não iniciada".

### Blender (nada testado no Roblox; nada aprovado pelo usuário)
- `BLENDER/Criaturas/CR_Leao_Solar/` (26/10) — Fase 0/blockout da skill `blender-image-to-3d`:
  - `asset-brief.md`: escala 11,5 de ombro, 12 proporções medidas na silhueta, partes (mandíbula separada para o rugido, juba deformável, 18 garras), materiais, sockets (boca, olhos, patas, sela), orçamento ≤ 16.000 tris;
  - `ref/` (conceito, rosto, juba, silhueta lateral), `build/` (scripts 00–02), `review/02_blockout*` (gate de silhueta IoU 0,851);
  - `CR_Leao_Solar_master.blend` (fora do git pelo `.gitignore`).
- `BLENDER/Criaturas/Blockouts/Leao_Solar/` — linha da biblioteca das 16 formas (arquivos `.blend` fora do git):
  - **v2** (`Leao_Solar_blockout`/`_refinado`/`_final.blend`): corrige a v1 reprovada (cabeça grande, juba oval, peito estreito, patas finas, cauda artificial). Ombro 11,5; topo da juba 19,05; comprimento 27,1; IoU 0,821.
  - **v5** (`Leao_Solar_refinado_v5`/`_final_v5.blend`, 27/10): pelo com subpelo + cartões, juba e tufo da cauda; textura assada; rig **felino de 36 ossos**; 28 animações procedurais (auditoria 4 aprovadas / 17 com ajustes / 7 para refazer); 32.188 tris (maior malha 18.000).
  - Exportações: `_Export/Leao_Solar.glb` (v2, 2,0 MB) e `_Export/Leao_Solar_v5.glb` (4,2 MB), validadas só por reimportação no Blender.
  - Problemas registrados: juba ainda lisa / precisa de cards ou escultura; peito pouco volumoso sob a juba; **sem cavidade da boca, dentes e língua** (necessária para o Rugido); animações procedurais.
- Planos gerais: `DOCS/CRIATURAS-REFINAMENTO-ANALISE.md` (anatomia felina: juba em mechas grandes, crânio felino, escápula e cotovelo marcados), `DOCS/CRIATURAS-RIG-ANIMACOES-PLANO.md` (família felino ~48 ossos com ossos de juba; passo amplo, cabeça alta, ombros "rolando").

### Sons
- **Nenhum som próprio do Leão.** Atenção: a família "Lion" da biblioteca Pro Sound Effects **já é usada pelos dragões** em arquivos compartilhados (`SonsConfig` — Glacial usa Lion Roar Tired/Short Blast/Snarl; Montanhas e `SonsFogo` usam Lion Guttural e "Thunder With Lion Roar"). Para o Leão, escolher tomadas diferentes para não soar igual a um dragão, e combinar com o usuário antes de mexer em `SonsConfig`.

### Código (`src/`)
- Nada específico do Leão (IA, combate, montaria, progressão).

### Modelo novo pela referência principal (03/11/2026) — EM AVALIAÇÃO
- Referência atual: `REFERENCIAS/planicies-douradas/leao-solar/leao-solar-referencia-principal.png` (perfil, frente e traseira; enviada pelo usuário).
- Pasta própria: `BLENDER/Criaturas/Leao_Solar_Ref/`. Leia o `LEIA-ME.md`.
- **Etapa 1 (silhueta e massas)** entregue: `Leao_Solar_Ref_E1_massas.blend` e a prancha `review/E1_prancha_massas_r8.png`.
  - IoU da silhueta: perfil 0,839; frente 0,926; traseira 0,889.
  - O IoU é só um auxílio: a aprovação é visual e cabe ao usuário.
- Malha nova (corpo por campo de distância, juba em mechas de fluxo). Os antecedentes v2/v5/CR ficaram intactos.
- Não aprovado, não testado no Roblox, sem rig, sem animação e sem textura.
- **E1 r8 REPROVADA pelo usuário** em 03/11 (juba em placas, cor apagada, rosto de mascote, corpo liso).
- **E2 v8 (03/11) — EM AVALIAÇÃO:** gerada no Meshy (Multi-Image to 3D das 3 vistas, 30 créditos, autorizado pelo usuário).
  - Depois: normalizada, com material de pelo fosco e albedo corrigido por zona.
  - Arquivos: `Leao_Solar_Ref_E2_v8.blend`, pranchas `review/E2_v8_*.png`.
  - IoU 0,911 / 0,897 / 0,877; erro de cor 19,1. Detalhes no `LEIA-ME.md` da pasta.
  - Pendências: mandíbula e interior da boca, 573 bordas abertas, malha de jogo (retopologia/UV/bake), rig. Nada foi testado no Roblox.
- **E3 (03/11) — EM AVALIAÇÃO:** `Leao_Solar_Ref_E3.blend`, uma cópia da v11, que segue intocada.
  - Feito: antebraços uniformizados; lábios abertos e mandíbula por pesos, com pivô na articulação; interior fechado (palato, gengivas, língua, dentes, garganta); bordas abertas de 573 para 4.
  - Relatório: `BLENDER/Criaturas/Leao_Solar_Ref/E3-RELATORIO.md`. Pranchas: `review/E3_{geral,membros,boca}.png`.
  - Só no Blender.
  - O supervisor apontou: boca aberta com painéis cinza, comissura angulosa, língua em placa e dentes uniformes. A E3 foi substituída pela E3b.
- **E3b (03/11) — EM AVALIAÇÃO:** `Leao_Solar_Ref_E3b.blend`. A v11 e a E3 seguem intocadas.
  - Boca refeita:
    - pesos contínuos até a comissura;
    - cavidade contínua mantida dentro da pele;
    - dentição de leão com caninos;
    - língua apoiada no assoalho, com osso próprio.
  - Medições: 0 pontos do interior fora da pele com a boca fechada (a E3 tinha 38); 0 de pele dentro da boca aberta (a E3 tinha até 87); 0 colisões de dentes a partir de 10°.
  - Antebraços corrigidos só nos dianteiros; o resto volta a ser o da v11.
  - Relatório: `BLENDER/Criaturas/Leao_Solar_Ref/E3b-RELATORIO.md`. Prancha: `review/E3b_prancha.png`. Vídeos: `review/E3b_boca_{34,frente}.mp4`.
  - Só no Blender.
  - **APROVADA pelo usuário em 03/11/2026**, no Blender.
- **E4 (03/11) — MALHA DE JOGO, EM AVALIAÇÃO:** `Leao_Solar_Ref_E4.blend`.
  - 17.798 tris numa malha, com 1 material (cor/normal/rugosidade 2048 e 1024). Pele: 15.200 (rosto 2.088). Interior: 946. Dentes: 1.344. Língua: 308.
  - Superfície nova por voxel e redução em duas passadas, com o rosto protegido.
  - 0 bordas abertas, 0 arestas não-manifold, 0 normais inconsistentes. A boca da E3b foi refeita leve e está limpa a partir de 10°.
  - Perda principal: pintura do rosto mais macia em close e mechas finas da juba fundidas.
  - Deformação testada só com rig provisório.
  - Relatório: `BLENDER/Criaturas/Leao_Solar_Ref/E4-RELATORIO.md`. Prancha: `review/E4_prancha.png`.
  - Nada testado no Roblox.
  - Supervisor: aparência aceita como direção, mas não como malha pronta para rig.
- **S1 sela r4 (06/11) — APROVADA pelo usuário (Blender):** foco nos materiais regionais oficiais, a pedido do usuário.
  - Couro das Planícies no assento, aba, manta (tom claro), alça, cilha e apoios.
  - Âmbar Solar no adorno solar (maior), na patilha, nos apoios de pé e nas argolas.
  - Ferro nas ferragens e Tendão de Antílope só na costura.
  - Arquivo `Leao_Solar_Ref_S1r4_sela.blend`.
- **S2 subida na sela (06/11) — APROVADA pelo usuário (Blender):** `Montar_E` / `Montar_D` (4,6 s), com o cavaleiro de teste em salto apoiado atrás da juba.
  - Sela r4 sem entrar no corpo nos 28 clipes (pior 0,003).
  - Arquivos `Leao_Solar_Ref_S2_montaria.blend` e `Leao_Solar_Ref_E5_clipes_r7.blend`; relatórios `S1-RELATORIO.md` (r3) e `S2-RELATORIO.md`. Nada testado no Roblox.
- **S1 sela felina (06/11) — EM REVISÃO [PROPOSTA]:** sela de Couro das Planícies sobre manta de Pele de Antílope.
  - Debrum de Tendão de Antílope, alça de Chifre Leve, adorno solar de Âmbar Solar em ferro.
  - Cilha atrás dos cotovelos e apoios de pé fixos; sem peitoral (a juba cobre o peito).
  - Centrada no corpo (malha 0,45 para +X da coluna); assento em y 0,2, quadril do cavaleiro a 12,23.
  - Arquivo `Leao_Solar_Ref_S1_sela.blend`; relatório `BLENDER/Criaturas/Leao_Solar_Ref/S1-RELATORIO.md`. Nada testado no Roblox.
- **E5 Bote r4 (05/11) — APROVADO pelo usuário (Blender).** Arquivo oficial dos clipes: `Leao_Solar_Ref_E5_clipes_r6.blend` (28 ações da Fase A + B). Ainda pendentes: a mira no jogo e o teste no Roblox.
  - Detalhes: agachamento mais fundo (2,9 studs), com o mesmo impulso e o alcance máximo de 45 studs.
  - Arquivo `Leao_Solar_Ref_E5_clipes_r6.blend`. Nada testado no Roblox.
- **E5 Bote r3 (05/11) — substituído pelo r4:** impulso das traseiras e **alcance máximo de 45 studs** (decisão do usuário em 05/11/2026; a mira escolhe o pouso até esse limite).
  - Arquivo `Leao_Solar_Ref_E5_clipes_r5.blend`.
  - A mira no jogo ainda não foi feita. Nada testado no Roblox.
- **E5 Bote r2 (05/11) — substituído pelo r3:** estalo das patas da frente na decolagem corrigido.
  - Saltos: punho de 90 para 23°/quadro, cotovelo de 66 para 31°, dedos de 102 para 17°.
  - Arquivo `Leao_Solar_Ref_E5_clipes_r4.blend` (`Leao_Bote_v1` mantido). Nada testado no Roblox.
- **E5 Patadas r3 (05/11) — APROVADAS pelo usuário; FASE B ACEITA em 05/11/2026 (Blender).** Arquivo oficial: `Leao_Solar_Ref_E5_clipes_r3.blend`, com as 28 ações da Fase A + B. Nada testado no Roblox.
  - Correção: pesos do antebraço e do punho limpos (sem Peito nem Juba abaixo do cotovelo) e punho ≤ 40° na subida.
  - Arquivos `Leao_Solar_Ref_E5_rig.blend` (anterior em `e5/…_v2_antes_pesos_punho.blend`) e `Leao_Solar_Ref_E5_clipes_r3.blend`.
- **E5 Patadas r2 (05/11) — substituída pela r3:** o punho torcia porque era orientado por ângulo no mundo.
  - Agora o punho só flexiona em relação ao antebraço e o cotovelo funciona como dobradiça.
  - Arquivo `Leao_Solar_Ref_E5_clipes_r2.blend` (v1 mantida). A Fase B só será certificada após a revisão.
- **E5 Fase B (05/11) — ACEITA em 05/11 (com as patadas r3):** 12 clipes só de movimento, sem efeitos: Alerta_Ameaca, Intimidacao, Rosnado, Rugido, Aproximacao_Furtiva, Bote, Patada_E/D, Mordida, Esquiva_E/D e Fadiga_Recuperacao.
  - Lábios no rig (63 ossos). Todas as 28 ações estão em `Leao_Solar_Ref_E5_clipes.blend`.
  - Relatório: `E5-RELATORIO.md`, seção 8. Nada testado no Roblox.
- **E5 (04/11) — FASE A ACEITA pelo usuário em 05/11/2026 (Blender); Fase B em produção:** `Leao_Solar_Ref_E5_faseA.blend`, com 16 clipes: repousos, observar, andar, trote, corrida, arrancada, frenagem, viradas e transições.
  - Patas paradas no apoio e IK sem erro (QA no Blender).
  - r3 (04/11): pata dianteira não contorce mais na corrida; traseiras não entram no corpo (joelho esquerdo recolocado, dobra limitada).
  - Corrida e Arrancada refeitas (r2): galope baixo, coluna fechando/abrindo, voo recolhido; arrancada com agachamento e patas escalonadas.
  - Rig de produção com 61 ossos.
  - A "mecha fundida" da E4b r2 era diagnóstico errado.
  - Relatório: `BLENDER/Criaturas/Leao_Solar_Ref/E5-RELATORIO.md`. Nada testado no Roblox; Fase B não iniciada.
- **E4b r2 (04/11) — EM AVALIAÇÃO:** `Leao_Solar_Ref_E4b_r2.blend`. O usuário pediu para corrigir o cotovelo, o punho e a juba do peito antes do rig final.
  - Mesma malha; ossos auxiliares de volume no cotovelo e no punho (giram metade do filho); peso do tronco retirado da pata dianteira.
  - Punho afina menos que na E4. Cotovelo sem perda de volume. A pele do peito e do ombro estica bem menos.
  - Ainda falta: uma mecha longa, fundida no antebraço pelo voxel, estica mais. Resolver exige soltar a ponta dela, mexendo na geometria e no bake.
  - Relatório: `BLENDER/Criaturas/Leao_Solar_Ref/E4b_r2-RELATORIO.md`. Nada testado no Roblox.
- **E4b (03/11) — EM AVALIAÇÃO:** `Leao_Solar_Ref_E4b.blend`, 17.602 tris.
  - Juntas medidas no perfil; zonas de articulação mais densas; 3 anéis em cotovelos, punhos, joelhos, jarretes e base da cauda.
  - Rig de teste de 53 ossos, com mandíbula, 2 ossos de língua, 8 cadeias de juba e 2 ossos de tufo.
  - Pesos: 0 sem peso, máximo de 4 influências, todos normalizados.
  - Melhor volume no jarrete, joelho e cauda; prega interna pior no cotovelo e no punho; a juba do peito ainda estica com a pata avançando.
  - Relatório: `BLENDER/Criaturas/Leao_Solar_Ref/E4b-RELATORIO.md`. Prancha: `review/E4b_prancha.png`. Vídeos: `review/e4b/videos/`.
  - Nada testado no Roblox.
- **E2 v11 (03/11) — APARÊNCIA APROVADA pelo usuário em 03/11/2026 como base do adulto.** Aprovação só no Blender: rig, boca, malha de jogo e Roblox continuam pendentes. Meshy Retexture com a referência como estilo (10 créditos; 40 no total).
  - Mais a correção de albedo por zona e o ajuste do nariz e do rosto.
  - Arquivos: `Leao_Solar_Ref_E2_v11.blend`, `review/E2_v11_*.png`; comparação `review/E2_v9_x_v11.png`.
  - A v9 fica como alternativa.

## 6. Pendências
1. **[PENDENTE — usuário]** Elemento único, passiva(s) e lista final de ativas (as 4 históricas servem de base).
2. **[PENDENTE — usuário]** Escolher a linha de modelo: continuar a v5 do Blender, retomar o `CR_Leao_Solar` (pipeline novo da skill `pipeline-criatura`, como os dragões) ou outra abordagem; e aprovar a aparência.
3. Modelo: juba volumosa em mechas, peito largo, boca com dentes e língua, mandíbula articulada para o rugido, pose neutra para rig.
4. Cores exatas dos 3 padrões; evolução por estágio e adornos por raridade.
5. Sela felina (posição e montagem) e testes de montaria.
6. Números de energia/dano/recarga; tamanho do bando; dieta.
7. Nada testado no Roblox (importação manual de GLB, escala, ossos, FPS em PC e celular).

## 7. Próximos passos sugeridos (aguardando aprovação)
1. Usuário revisar as capturas existentes (`SCREENSHOTS/Blockouts_2026_10_26/Folha_Leao_Solar.png`, `SCREENSHOTS/Criaturas_Final_2026_10_26/Folha_Leao_Solar.png`, `CR_Leao_Solar/review/02_blockout_folha.png`; reprovado: `SCREENSHOTS/C1_Criaturas/C1_93_reprovado_leao_caricato.jpg`) e decidir a linha de modelo. Não há folha própria da v5 encontrada.
2. Com a linha aprovada: refino anatômico no Blender (juba, peito, boca), etapa por etapa com capturas.
3. Rig felino + clipes básicos (Repouso, Andar, Trote, Corrida, Virar, Observar, Rugido) e, depois, as habilidades como animação sem efeito.
4. Só com o kit oficial definido: VFX, sons próprios, IA selvagem nos bandos das Planícies e montaria.
