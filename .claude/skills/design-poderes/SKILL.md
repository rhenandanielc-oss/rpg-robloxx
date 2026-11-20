---
name: design-poderes
description: Projetar, melhorar e testar poderes, ataques básicos e efeitos visuais (VFX) das criaturas deste RPG Roblox — da leitura das regras oficiais ao vídeo antes/depois no Studio. Reúne as regras de jogabilidade e os padrões visuais já aprovados pelo usuário (atacar em movimento, brilho em camadas, jato contínuo, validação no servidor, números provisórios). Use ao propor um poder novo, revisar o kit de uma criatura, deixar um efeito "mais bonito/brilhante", corrigir um poder que parece errado ou preparar o teste e a aprovação de um poder.
---

# Design de poderes e efeitos

Siga CLAUDE.md antes de tudo: M0 somente leitura, uma mudança pequena por vez, Studio só com autorização da tarefa e reserva em `DOCS/estado/studio-em-uso.md`. Este RPG NÃO é o Dragon Ranch.

Antes de construir um poder novo ou mudar um comportamento, use a skill `questionar-antes`: pergunte ao usuário o que está em aberto e espere o "pode seguir".

## 1. Regra do poder (antes de qualquer código ou visual)
1. Fontes, em ordem de precedência (vale a decisão oficial mais recente e explícita):
   - o documento oficial `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO.docx` (na raiz do repositório), com a seção "ATUALIZAÇÃO OFICIAL — 30/10/2026" prevalecendo;
   - `REFERENCIAS_PODERES_E_EFEITOS.md`: kits definidos de quase todas as criaturas, com as decisões do usuário de 16/11 em diante. Fora dele ficam Wyvern, Urso e Dragões;
   - as decisões posteriores em `DOCS/criaturas/<criatura>.md`, `DOCS/pedidos/` e na memória (ex.: kits oficiais do Glacial e do Sombrio).
   Regras gerais desse documento, que valem para todas as criaturas:
   - kit = 3 ativas + 2 passivas;
   - mira das habilidades dirigidas: alvo travado → mouse → câmera;
   - alvos de tamanhos muito diferentes usam classes de tamanho;
   - veneno/toxina nunca mata sozinho;
   - todo buff, debuff ou estado tem efeito visual no corpo;
   - nas criaturas desse lote, os efeitos ficam no corpo; fora do corpo só vento (Ancestral) e neve com vento (Glacial).
2. Classifique cada item como **OFICIAL / PROPOSTA / PENDENTE / VERIFICADO NO STUDIO**. Não invente nome, efeito ou elemento oficial. Se faltar regra, proponha 2–3 opções com prós e contras e pergunte.
3. Ficha mínima de cada poder (escreva-a no doc da criatura antes de implementar):
   - tipo (ativa, passiva, básico) e elemento;
   - leitura visual: o que o jogador vê na preparação, na emissão e no impacto;
   - em terra e/ou no ar; com montaria ou selvagem (a IA usando o kit é decisão do usuário);
   - alvo e acerto (cone, projétil, área, contato), quantas vezes acerta cada alvo, interação com obstáculos;
   - recarga, custo, duração e dano marcados **PROVISÓRIO/NAO_APROVADO** até o usuário aprovar números;
   - entrada no PC e no celular.
4. Limites fixos do jogo:
   - **Monetização:** nada comprado aumenta dano, atributo ou loot, e o PvP não vira pay-to-win (`SPECIFICATIONS/MONETIZATION.md`).
   - **Narrativa:** nenhum poder ou texto revela antes da hora que a entidade ancestral era protetora.

## 2. Jogabilidade aprovada pelo usuário
- **Atacar em movimento (PvP de verdade).** Ataques básicos e poderes de cabeça/pescoço não travam a locomoção:
  - entram como clipes PARCIAIS de camada (só os ossos do golpe; os pais até a raiz com peso 0), em prioridade Action/Action2 por cima de Andar/Trote/Corrida;
  - o servidor não pausa o controlador;
  - golpes que movem uma perna precisam de um clipe por marcha que comece no descolamento daquela pata.
- **Lobo Ártico:** o ataque básico é só mordidas. Não propor garras/patadas sem pedido.
- **Câmera:** não atravessa obstáculos, a pé e montado (`CameraSemAtravessar_Cliente`).
- **Servidor valida tudo** (estado, recarga, alcance, acerto, permissão de controle). O cliente só envia a intenção e desenha o efeito. Rejeite a mira impossível no servidor.
- **Obstáculos:**
  - poderes de movimento não atravessam paredes;
  - verifique se o dano respeita Parts. Hoje `N:visivel` só testa Terrain, então registre isso como pendência sem corrigir por conta própria.
- **Custo multiplayer:** consultas e raycasts a ~10 Hz, sem `PointLight` novo por efeito (limite de luzes), peças temporárias em `workspace.VFX_Temporarios` com `Debris`.

## 3. Padrões visuais que já funcionaram
Referências: `VFXSombra.luau` (PATCH_UMBRAL_BRILHO r3), `VFXFogo.luau` (PATCH_FOGO_BRILHO) e `VFXGelo.luau` (PATCH_GELO_BRILHO r2), em `src/ReplicatedStorage/Combate_Dragoes/`.
- **Mais bonito = camadas brilhantes POR CIMA, nunca trocar o que já foi aprovado:**
  - veios alongados (`TEX.faisca`, `LightEmission 1`, `LightInfluence 0`, `Orientation VelocityParallel`, ZOffset alto);
  - faíscas ou brasas;
  - clarão na boca;
  - disco Neon de pressão a cada ~0,3 s até o contato, só se o fator de LOD for ≥ 0,5;
  - bola de clarão no ponto de contato a cada ~0,35 s.
- **`Squash` NEGATIVO** (ex.: −2) alonga a partícula no sentido da velocidade; positivo achata e vira "corte de lado".
- **Jato contínuo:**
  - com fps baixo (o Studio roda a ~15 fps), cada quadro solta um lote que viaja junto e o jato fica "cortado" em bolhas;
  - espalhe `Speed` (≈ 0,6–1,04 da velocidade alvo);
  - dê uma base contínua com `Beam` fino;
  - recorte a vida das partículas na distância do contato (raycast que ignora modelos com Humanoid).
- **Translúcido não é fraco:** um feixe opaco e brilhante pareceu "laser" (Glacial, 02/11). Mantenha o corpo translúcido e coloque o brilho nos detalhes.
- **Jato já saturado** (Fogo) muda pouco com camadas novas: avise o usuário e ofereça contraste (núcleo branco, fumaça escura), não só "mais brilho".
- **O usuário gosta de efeitos mais brilhantes.** Na Wyvern ele preferiu manter o VFX genérico de Ar por ser mais brilhante.
- **Identidade por bioma e elemento:**
  - Gelo: branco e azul glacial;
  - Fogo: branco-amarelo e laranja;
  - Sombra: violeta;
  - Ar: branco translúcido;
  - Natureza: verde.
  Sem poluição visual.

## 4. Teste e aprovação (sempre com evidência)
1. **Antes:**
   - confira se a fonte no Studio é igual ao `src/` (compare normalizando CRLF);
   - faça backup do módulo em `ServerStorage` com data;
   - compile com `loadstring` antes de gravar `.Source`.
   Detalhes do patch: skill `roblox-patch`.
2. **Cena padrão de ensaio:**
   - criatura montada (`ServerStorage.Montaria_Debug:Invoke("montar", plr, m)` + `Montaria_Dragoes.Comando:FireServer("montar", m)`);
   - alvo `Laboratorio_IA.Alvos_Teste.NPC_Alvo1` ancorado a ~45 studs à frente;
   - parede (Part) a ~62 para ver a interação com obstáculos;
   - câmera fixa de perfil.
   **Mire a partir da boca** (`mouth_upper_tip`), não da cabeça.
3. **Antes/depois com a MESMA câmera, luz e escala:**
   - capture a janela do Studio com `review/teaser_anuncio/scripts/cap.py <HWND> <pasta> <segundos> 12 4 144 1740 945`;
   - monte o vídeo pelo Blender (memória video-captura-studio);
   - faça uma prancha de quadros com zoom no efeito.
4. **Meça:** dano antes/depois (precisa ficar igual, a menos que o pedido seja de números), pico de peças em `VFX_Temporarios`, fps do cliente e erros no console.
5. **Diagnóstico de efeito estranho:** em Play, ligue e desligue as camadas (feixes, partículas) em fases durante o mesmo sopro e capture; não chute a causa.
6. **Celular:** sem dispositivo real, escreva "mobile não testado". Separe o medido do emulado.
7. **Iteração:** envie o vídeo e o zoom (`SendUserFile`) e faça UMA pergunta (aprovar, reforçar ou ajustar). Cada revisão vira r2, r3… no diário, com o arquivo anterior guardado.
8. **Depois de aprovar:** registre no diário da criatura, em `PROJECT-STATE.md` e na memória. Commit só quando o usuário pedir, adicionando só as partes deste chat (outros chats deixam linhas nos mesmos arquivos de notas).

## 5. Ferramentas úteis
- **Skills do Roblox Studio** (via `list_roblox_skills` / `get_roblox_skill`):
  - `rbx-perf-profiling` e `rbx-scene-analysis` para o custo dos efeitos;
  - `rbx-network-simulator` para PvP com lag;
  - `rbx-unit-test` para regras de recarga e dano em ModuleScripts.
- **Clipes de poder:** skill `pipeline-criatura` (Blender → JSON → KeyframeSequence; convenção `giro180y`).
- **Fechamento:** skill `relatorio-rpg`.
