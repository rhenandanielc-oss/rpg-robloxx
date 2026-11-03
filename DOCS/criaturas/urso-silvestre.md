# Urso Silvestre — ficha-resumo do subchat (03/11/2026)

Subchat responsável: **Urso Silvestre** (grupo Floresta Ancestral). Mapa dos chats: `DOCS/ORGANIZACAO-CHATS.md`.
Fontes: RPG_01 e RPG_02 ATUALIZADOS (texto extraído nas notas da sessão principal). A **ATUALIZAÇÃO OFICIAL de 30/10/2026** prevalece sobre o histórico.
Esta ficha só resume. Em caso de dúvida, vale o documento oficial.

## 1. Identidade

| Item | Valor | Status |
|---|---|---|
| Espécie-base | Urso (1 das 13 espécies-base) | [OFICIAL] |
| Forma regional | Urso Silvestre (única forma do Urso) | [OFICIAL] |
| Bioma / habitat | Floresta Ancestral | [OFICIAL] |
| Categoria | Criatura **domesticável** (não é fauna de recursos) | [OFICIAL] |
| Papel | **Tanque protetor do treinador**: interceptação física de ameaças, baixa velocidade | [OFICIAL] |
| Porte adulto | **8–10 studs até os ombros** | [OFICIAL] |
| Montaria | Montável desde **Adulto**, com **sela reforçada** | [OFICIAL] |
| Ataques básicos | Golpes de patas, mordidas e combos pesados (não ocupam slots de habilidade) | [OFICIAL] |
| Estágios | Ovo, Bebê, Jovem, Pré-adulto, Adulto, Ancião (regra geral) | [OFICIAL] |
| Raridades | Comum, Incomum, Raro, Épico, Lendário; influência pequena (1–5%) e visual | [OFICIAL] |
| Padrões visuais (3) | **Castanho do Bosque**, **Negro da Floresta**, **Mel Dourado** (Etapa 23) | [OFICIAL] |

Os padrões são só cosméticos: não determinam elemento nem raridade.

## 2. Elemento

- **Regra vigente (30/10/2026):** cada criatura tem **um único elemento natural**. Não há segundo/terceiro elemento, alternância nem fusões elementais no sistema atual. [OFICIAL]
- O catálogo histórico lista para o Urso Silvestre os elementos permitidos **Terra, Luz, Natureza**. Pela atualização, essa lista não indica a escolha final.
- **[PENDENTE] Qual é o único elemento do Urso Silvestre.** A atualização só definiu os dos dragões (Fogo, Gelo, Sombra). Não presumir.

## 3. Habilidades

**Regra vigente (30/10/2026):** no mínimo **1 passiva + 3 ativas**, com nomes e efeitos aprovados criatura por criatura. A lista antiga de 4 habilidades vira referência, não obrigação. [OFICIAL]

Ficha histórica de combate (aprovada antes de 30/10, ainda não revista para o kit de elemento único):

| Habilidade | Função-base aprovada |
|---|---|
| Golpe Colossal | Ataque pesado das patas; dano em área e interrupção de aproximações |
| Rugido Protetor | Aumenta temporariamente a capacidade de proteger o treinador |
| Carga Selvagem | Avanço pesado de curto/médio alcance, com empurrão e quebra de formação |
| Fortaleza Viva | Proteção de área com movimento lento; o treinador pode ser interceptado pelo corpo do Urso |

- **[PENDENTE]** Kit final: quais ativas ficam (3 ou mais), **qual é a passiva** (nenhuma foi definida) e como cada uma fica com o elemento escolhido.
- **[PROPOSTA, histórico]** Transformações por elemento (ex.: Terra = tremor e pedras; Luz = impacto radiante; Natureza = raízes). Também as 6 fusões direcionais (Bastião Radiante, Muralha Enraizada, Santuário Vital etc.). As fusões estão **superadas** pela regra de elemento único.

### Comportamento e combate [OFICIAL]
- Protege o treinador **posicionando-se entre ele e o atacante**. A IA prioriza inimigos próximos que ameaçam o treinador, respeitando ordens manuais.
- Proteção **ativa** (interposição, bloqueio, controle, posição). **Não há transferência automática de dano** (Etapa 24.4).
- Interceptação automática de ameaças ao treinador é **exclusiva do Urso** (o Búfalo não a herda).
- Recuperação por habilidades é gradual e limitada.
- Fraquezas no PvP: lentidão e dificuldade contra alvos distantes ou rápidos.
- Criatura derrotada fica incapacitada; o PvP segue até a Vida do humano chegar a zero.
- **[PENDENTE]** Validar a interposição do Urso sem criar invulnerabilidade, com resistência a controle repetido.

### Atributos
- Seis atributos oficiais: Vida, Defesa, Força, Velocidade, Energia, Poder Elemental. [OFICIAL]
- **Números da Etapa 24.2 = [PROPOSTA, NÃO APROVADA]**, só para referência:
  - escala 1–5: Vida 5, Def 5, Força 4, Vel 1, Energia 3, P.Elem 3;
  - Adulto n100: 6.200 HP, Def 185, Força 165, Energia 120, P.Elem 135;
  - velocidade: terra 18 studs/s, água 14, sem voo; manobra terra 2, água 2.
- **[PENDENTE]** Cooldowns, energia, alcance, dano, animações finais e balanceamento.

## 4. Ninhos e ovos (regras gerais) [OFICIAL]
- Poucos ninhos; a quantidade varia com o número de jogadores. Reaparecem em 30–60 min, longe do anterior, em habitat coerente.
- Ninhos são achados por pistas naturais (rastros, sons, odores), sem marcador de coordenada.
- O primeiro jogador a concluir a coleta ganha o ovo. Guardiões adultos selvagens não podem ser capturados.
- **[PENDENTE de lore]** Justificativa narrativa/visual de mamíferos (Ursos inclusive) nascerem de ovos.
- **[PROPOSTA]** Faixas de quantidade de ninhos por número de jogadores.

## 4b. Modelo novo fiel à referência — 03/11/2026 (AGUARDANDO APROVAÇÃO VISUAL)
- Pedido: `DOCS/pedidos/2026-11-03-urso-silvestre-modelo-e-animacoes.md`.
- Referência do usuário: `REFERENCIAS/floresta-ancestral/urso-silvestre/urso-silvestre-referencia.png`.
- Pasta própria: `BLENDER/Criaturas/Urso_Silvestre_Ref/`. Lá estão os scripts reproduzíveis, o LEIA-ME com a tabela de triângulos e o LOD, e as revisões `review/r01..r08_low`.
- **Feito no Blender:**
  - corpo novo (metaballs → voxel), rosto, boca recortada que abre e fecha, dentes, língua, olhos âmbar e 5 garras por pata;
  - ~2.400 cartões de pelo com atlas próprio;
  - placas de casca, cipós, musgo, samambaias e folhas.
- **Malha de jogo:** `low/CR_Urso_Silvestre_LOW.glb`, 49,5k tris em 5 malhas ≤ 20k, 6 texturas 1024. LOD1 do pelo: total de 36,8k.
- **Export validado** por reimportação no Blender (`GLB_VALIDO`). Ombro com pelo: 8,91 studs.
- **Não feito:** rig final, animações, importação e teste no Roblox. Nenhum acesso ao Studio.
- Prancha para aprovação: `BLENDER/Criaturas/Urso_Silvestre_Ref/review/PRANCHA_APROVACAO_r08.png`.

## 4c. v2 — correção visual completa (03/11/2026, AGUARDANDO APROVAÇÃO VISUAL)
- A v1 (4b) foi **reprovada** pelo usuário (painel `BLENDER/Criaturas/Urso_Silvestre_Ref/review/v2_painel_reprovado/`). A v1 foi preservada.
- **Nova versão:** `BLENDER/Criaturas/Urso_Silvestre_Ref/v2/` (ver `LEIA-ME-v2.md`).
  - Gerada no **Meshy**, com autorização do usuário: Image to Image (pose neutra) + Multi-Image to 3D. **36 créditos.**
  - Finalizada no Blender: voxel, redução, boca recortada com gengivas/dentes/língua, bake de cor e normal.
- **Malha de jogo:** `v2/low/CR_Urso_Silvestre_v2_LOW.glb`, 36.524 tris em 4 malhas ≤ 20k, 3 materiais, sem transparência. Ombro 8,97 studs.
- **Boca e dentes ajustados** a pedido do usuário: recorte na malha densa, dentição maior, dentes escondidos com a boca fechada. Ver `v2/review/PRANCHAS_v2/07_boca_ajustada.png`.
- **Export validado** por reimportação no Blender.
- **Visual APROVADO** pelo usuário em 03/11/2026 ("Aprovado, seguir ao rig").
- **Rig feito** (`v2/rig/`): 31 ossos com nomes do jogo, pele deformável, testado em poses extremas no Blender (erguer-se, passada, cabeça baixa, torção, mandíbula).
  - GLB com rig `v2/rig/export/CR_Urso_Silvestre_v2_Rig.glb` validado por reimportação.
- **Clipes feitos** (`v2/rig/clipes/`, 18 JSON + ações no `CR_Urso_v2_Anim.blend`):
  - Repouso, Observar, Andar, Corrida, Arrancada, Frenagem, VirarE/D;
  - Sentar/LevantarSentado, Deitar/LevantarDeitado, Comer;
  - Rugir, Ameaca, GolpePata, Mordida, ReacaoImpacto.
  - QA no Blender: IK, escorregão, chão, loops. GIFs normal/lento em `v2/rig/clipes_render/gif/`.
  - Velocidades são PROPOSTA.
- **Revisão de apoio e deformação dos clipes** (03/11/2026, autorizada; clipes APROVADOS visualmente pelo usuário em 03/11/2026; Roblox ainda não testado). Ver `v2/LEIA-ME-v2.md`, seção "Revisão".
  - Deriva da pata apoiada no mundo ≤ 0,045 em todos os clipes (antes até 4,5 no Virar).
  - Garras ≤ 0,002 e solas ≤ 0,016 abaixo do chão.
  - Pesos ajustados (sola, boca, orelhas); GLB reexportado e validado.
  - Pendentes:
    - transições por mistura afundam até 0,19;
    - franja da barriga no Deitar 0,10;
    - arestas da boca.
  - Velocidades da simulação são parâmetros técnicos, não regras.
  - Cópia anterior em `v2/rig/antes_revisao/`.
- **Não feito:** Studio (importação e montagem das KeyframeSequences), teste em PC ou celular.
- Elemento continua [PENDENTE]. A vegetação é só aparência.

## 5. O que já existe no projeto (segundo os registros; o Studio NÃO foi aberto nesta sessão)

### Blender (`BLENDER/Criaturas/Blockouts/`)
- `Urso_Silvestre/`: `_blockout.blend` (26/10), `_refinado.blend` (V2), `_final.blend`, `_refinado_v5.blend`, `_final_v5.blend` (27/10).
- `_Export/Urso_Silvestre.glb` (V2, 1,6 MB) e `_Export/Urso_Silvestre_v5.glb` (4,9 MB).
- Script `build/build_Urso_Silvestre.py`; referências `ref/Urso_Silvestre_matte.png` e `ref/Urso_Silvestre_silhueta_x4.png`. No git estão **só o script e as 2 referências**; `.blend` e `.glb` não estão versionados.
- Blockout: corcova 9,0 (dentro de 8–10), comprimento 14,9, IoU 0,802 contra a silhueta oficial (`LEIA-ME-BLOCKOUTS.md`).
- Refino V2 (`LEIA-ME-FINAL.md`):
  - plantígrado com 5 garras longas, focinho alongado, testa inclinada;
  - **25 ossos, 28 animações**: pacote base, montaria, territorial (GuardarNinho, Alerta, Ameaça, erguendo-se nas patas traseiras) e as 4 habilidades históricas como clipes.
- Auditoria V2 (`AUDITORIA-ANIMACOES-V2.csv`):
  - **Ameaca = Refazer**;
  - em "pequenos ajustes": Corrida, Arrancada, Frenagem, Comer, Deitar/Descanso/Levantar, Montar/Desmontar, MontadoCorrida, GuardarNinho, GolpeColossal, CargaSelvagem.
- V5 (`RELATORIO-PRODUCAO-V5.md`):
  - revestimento de pelo (subpelo + cartões) com **folhas e samambaias**;
  - 41.619 tris (maior malha 16.000), 25 ossos, animações 8 A / 15 PA / 5 R, validado por reimportação no Blender.
  - **Não testado no Roblox e não aprovado pelo criador.**
- Análise de refino (`DOCS/CRIATURAS-REFINAMENTO-ANALISE.md`): alvo de crânio ursídeo, corcova muscular, patas plantígradas largas com garras longas. Musgo e folhas como superfície.

### Roblox Studio (segundo `DOCS/estado/criaturas-gerais.md` e `DOCS/CRIATURAS-C1-MATRIZ.md`)
- **Urso provisório** da 3ª geração do gerador do Studio, **estilizado**, 9,14 de ombro, em `Laboratorio_Criaturas`.
  - Rig Motor6D (segmentos rígidos, sem pele deformável) com animações.
  - Aparência **pendente de aprovação**.
  - 2 gerações anteriores reprovadas, em `ServerStorage.Proto_Restore.Retirados_C1` (atributo `Motivo`).
- `ServerStorage.Biblioteca_Criaturas.Catalogo` registra a forma (medidas, elementos, montaria, 4 habilidades). **Escrito antes de 30/10**: ainda tem a lista de 3 elementos e 4 habilidades.
- Captura: `SCREENSHOTS/C1_Criaturas/C1_08_urso_PROVISORIO_estilizado.jpg`.
- **Nenhum script de IA, combate, montaria ou som do Urso** em `src/`. Os sistemas existentes (`Combate_Dragao`, `Montaria_Cliente` etc.) são dos dragões.

### Mapa: habitats de urso (só marcadores e estruturas, sem criatura nem IA)
- **Floresta Ancestral** (`DOCS/estado/mundo-floresta.md`):
  - cavernas de urso `Caverna_Urso_1..6/7` (Habitats / `Exp_Ursos`);
  - arenas R≈46 e marcadores `SpawnUrsoGigante` / `PontoCovil`;
  - `Caverna_Montanha_Urso`, esculpida na montanha NO **dentro da floresta** (reservada);
  - reservas `Reserva_CavernaUrso_*`;
  - vila oculta `Aldeia_Carvalho` com atributo `Guardiao = Urso_Gigante`.
  - Caminhada a pé testada nas 6 cavernas novas. Nenhum teste com IA, celular ou multijogador.
- **Montanhas Altas** (`DOCS/estado/mundo-montanhas.md`, memória `bioma-montanhas-urso`): foram criadas as tocas `Toca_Urso_Norte/Sul/Cumes` (antes também Leste).
  - Na **V8 (22/10)**, por decisão do criador, **os ursos foram retirados das Montanhas** ("urso é da Floresta"). A fauna oficial de lá é só Dragão das Montanhas e Wyvern.
  - As cavernas ficaram como exploráveis/refúgio genérico. **Registrado apenas, nada mudado.**
- Observação: "Urso Gigante" (guardião/raid) aparece nos marcadores do mapa, mas **não está** no RPG_02 como forma. Tratar como [PENDENTE]: guardião adulto selvagem do Urso Silvestre ou coisa à parte? Não inventar.

## 6. Pendências
1. **[PENDENTE — criador]** Único elemento do Urso Silvestre, entre os históricos Terra/Luz/Natureza.
2. **[PENDENTE — criador]** Kit final: passiva(s) e ativas (manter as 4 históricas? quais nomes e efeitos com o elemento único?).
3. **[PENDENTE]** Aprovação artística do modelo: V5 do Blender vs. provisório estilizado do Studio. Nenhum foi aprovado.
4. Animações: refazer Ameaca e ajustar os clipes marcados. Validar no Roblox (nenhum teste até agora).
5. Importar a malha com pele deformável no Studio (pipeline C1: Bone/skin, KeyframeSequence).
   - Atenção à memória `roblox-skin-nomes-ossos`: não renomear ossos e alinhar o pivô aos pés.
6. Catálogo do Studio (`Biblioteca_Criaturas.Catalogo`) desatualizado em relação à regra de 30/10. Atualizar só com autorização.
7. Estágios de crescimento (proporções Bebê → Ancião), sela reforçada (modelo/ajuste), sons, IA de proteção e montaria: nada feito.
8. Papel do "Urso Gigante" nos marcadores do mapa (ver §5).

## 7. Próximos passos sugeridos (aguardando aprovação; nada iniciado)
- **A.** O criador define elemento + kit (passiva/ativas). Esta ficha é atualizada com [OFICIAL].
- **B.** Inspeção M0 **somente leitura** no Studio (reservando `DOCS/estado/studio-em-uso.md`): o que existe do urso em `Laboratorio_Criaturas`, `Biblioteca_Criaturas` e `Retirados_C1`, com capturas.
- **C.** Escolher a base do modelo final (V5 Blender ou nova geração), seguindo o painel `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/01-lobos-urso-leao.png` e a skill `pipeline-criatura`. Mostrar etapa por etapa com capturas.
- **D.** Depois do modelo aprovado: rig, clipes (locomoção plantígrada pesada, balanço lateral, ergue-se para ameaçar), montaria com sela reforçada e IA de interposição. Tudo com o servidor autoritativo para dano e recargas.
