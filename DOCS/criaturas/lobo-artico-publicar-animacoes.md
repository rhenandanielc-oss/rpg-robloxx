# Lobo Ártico: como publicar as animações e salvar o place (passo a passo para o usuário)

Escrito em 26/11/2026. Até aqui os clipes do Lobo Ártico existem no `rpg_roblox` como **KeyframeSequence**, em `ReplicatedStorage.Animacoes_LoboArtico` (76 clipes). Os scripts tocam esses clipes com `KeyframeSequenceProvider:RegisterKeyframeSequence`.

**Isso só funciona no Studio.** No jogo publicado, cada clipe precisa ser uma **Animation publicada na sua conta** (ou no grupo dono do jogo).

O Claude não publica nada em seu nome (é uma ação externa e pública): estes passos são para você.

## 1. Salvar o place

No Studio do rpg_roblox: **Arquivo → Salvar no Roblox** (ou Ctrl+S).

Mudanças instaladas pela integração e ainda não salvas por mim (cada uma tem backup em `ServerStorage.LoboArtico_Backups`):
- **Scripts e módulos:**
  - Controle **r12** no modelo selvagem e no `Teste_LoboArtico`;
  - IA **r7b**;
  - `Movimento_LoboArtico` **v48**;
  - `Cabeca_Cliente` **r1**.
- **Clipes:** curvas (16), viradas de combate (6) e partida/parada (4).
- **Mapa:** 2.572 `Colisor_Tronco` nas árvores da Tundra.

## 2. Publicar cada clipe como Animation

Para cada `KeyframeSequence` de `ReplicatedStorage.Animacoes_LoboArtico`:

1. Clique com o botão direito no clipe → **Salvar no Roblox** (ou abra no Editor de Animação e use **Publicar no Roblox**).
2. Dê o nome igual ao do clipe (ex.: `LoboArtico_AndarCurvaEsquerda`) e publique na mesma conta ou grupo do jogo.
3. Anote o ID gerado (`rbxassetid://...`).

Dica: dá para publicar em lotes, mas são 76 clipes. Os essenciais para o lobo selvagem andar e lutar são:
- **Locomoção:**
  - Repouso, Andar, Trote, Corrida;
  - Arrancada, Frenagem, trocas de marcha;
  - Virar/VirarCurto.
- **Curvas e partidas:**
  - as 16 curvas;
  - as 6 VirarCombate;
  - PartidaAndar, PartidaCurvaEsquerda/Direita e ParadaAndar.
- **Ameaça e combate:**
  - AmeacaEntrar, Ameaca, AmeacaSair, InvestidaAviso;
  - as mordidas e os clipes do kit.

## 3. Ligar os IDs nos scripts (o Claude faz, com o seu OK)

Me passe a lista `nome → ID` (ou deixe os IDs como atributos nos próprios KeyframeSequence, por exemplo `AnimId`). Eu troco o `RegisterKeyframeSequence` por `Animation.AnimationId = <ID>` nos scripts que tocam os clipes:
- `Controle_Servidor`, linha ~103;
- `Kit_Servidor`, linhas ~100, ~110 e ~135;
- `Uivo_Servidor`, linha ~60;
- `IA_LoboArtico`, linha ~139.

A troca mantém o `RegisterKeyframeSequence` como reserva quando o clipe não tiver ID, para o Studio continuar funcionando.

## 4. Conferir

Depois de publicar, rode um Play no Studio e um teste no cliente do Roblox. Os lobos devem andar, curvar, partir, parar e ameaçar como nos vídeos de `review/rpg_r11` e `review/rpg_r12`.
