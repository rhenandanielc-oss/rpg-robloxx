---
name: ideia-de-jogo
description: Transformar uma ideia solta do usuário (criatura, poder, missão, bioma, sistema, item, evento, loja, visual de qualquer coisa) em uma proposta de design clara para este RPG Roblox — conferida contra as regras oficiais, com 2–3 opções, referência visual e, depois da aprovação, um pedido pronto em DOCS/pedidos/ para o chat certo executar. Use quando o usuário disser "tive uma ideia", "como ficaria", "o que acha de", "quero algo assim", pedir sugestões de design ou quiser pensar uma parte do jogo antes de construir.
---

# Da ideia ao pedido aprovado

Este é o RPG de fantasia realista do Roblox (`MASTER-PROMPT.md`). NÃO é o Dragon Ranch. Nesta skill nada é construído: o resultado é uma decisão do usuário e um pedido escrito. Studio, Blender e código ficam para depois, com a autorização da tarefa.

## 1. Entender sem inventar
1. Repita a ideia em uma frase e pergunte só o que mudaria o design, no método da skill `questionar-antes`: rodadas curtas com opções e sem repetir o que já está decidido.
2. Leia apenas o necessário:
   - `MASTER-PROMPT.md`;
   - `DOCS/DECISIONS-AND-OPEN-ISSUES.md`;
   - a ficha do assunto em `DOCS/biomas/`, `DOCS/criaturas/`, `DOCS/fauna/` ou `DOCS/equipamentos/`;
   - poderes: `REFERENCIAS_PODERES_E_EFEITOS.md`;
   - loja: `SPECIFICATIONS/MONETIZATION.md`;
   - visual de bioma: `SPECIFICATIONS/BIOMES-ART-BIBLE.md`;
   - os documentos oficiais `RPG_01_Mundo_e_Sistemas_ATUALIZADO.docx` e `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO.docx` (raiz do repositório; a seção de 30/10 prevalece).
3. Marque cada ponto como **OFICIAL**, **PROPOSTA**, **PENDENTE** ou **CONFLITO**. Em caso de conflito, mostre as duas fontes e deixe o usuário decidir.

## 2. Filtros obrigatórios (a ideia passa por todos)
- **Narrativa:** nada pode revelar antes do fim que a entidade ancestral era protetora; a Guilda do Horizonte é a culpada.
- **Monetização:**
  - a compra nunca dá vantagem automática no PvP, mais atributo nem mais loot;
  - não pula requisitos narrativos/lendários;
  - preços de referência só valem confirmados.
- **Dungeons:** ninguém revive aliados; no máximo 3 ressurreições totais por pessoa por tentativa.
- **Mundo:**
  - fantasia realista e natural;
  - identidade por bioma;
  - formações naturais em vez de estruturas monumentais;
  - nada de pedras/troncos gigantes aleatórios;
  - vento localizado nas plantas e água integrada.
- **PvP:** ataques e poderes funcionam em movimento (skill `design-poderes`).
- **Técnico:**
  - o servidor valida moedas, inventário, loot, progressão, comércio e compras;
  - tem que rodar no celular (orçamento de malha ≤ 20k tris por MeshPart, texturas ≤ 1024, efeitos com LOD);
  - dados persistentes exigem plano de teste de falha.
- **Escopo:** isso está no lançamento oficial ou é para atualização? Diga qual.

## 3. Propor como designer
1. Ofereça **2 ou 3 opções** diferentes de verdade, não variações do mesmo. Para cada uma:
   - como o jogador vive aquilo (antes, durante, depois);
   - por que é divertido;
   - o que custa construir (quais chats, modelos, clipes, scripts);
   - riscos.
   Termine com a sua recomendação.
2. **Referências de design:** pode citar princípios de jogos conhecidos (ex.: a fluidez de movimento estilo Dragon Adventures), mas nunca copiar nome, personagem, arte, música ou mapa de outro jogo.
3. **Referência visual** quando a ideia for visual. Prefira, nesta ordem:
   - imagens do usuário em `REFERENCIAS/<bioma>/<criatura>/` e em `C:/Users/Rhenan/Downloads/RPG_Referencias_Visuais_GitHub/REFERENCES/`;
   - um esboço rápido no Blender, em segundo plano (skills `blender-*`), com prancha de vistas;
   - o Meshy só com o OK do usuário para cada geração (gasta créditos; skill `pipeline-criatura`).
   Mostre as etapas com capturas (`SendUserFile`). O usuário quer o resultado o mais próximo possível da referência, qualidade antes de quantidade.
4. **Ideias com números** (economia, tempo de farm, dano): monte uma tabela simples com as hipóteses marcadas **[A TESTAR]**. Nunca apresente número inventado como oficial.

## 4. Fechar com um pedido
1. Pergunte UMA coisa por vez (`AskUserQuestion` ou o botão do `wrap_up`) até ter a decisão.
2. Registre a decisão na ficha certa em `DOCS/`, marcada como decisão do usuário com a data, e na memória quando for uma regra que vale para outras conversas.
3. Escreva o pedido em `DOCS/pedidos/AAAA-MM-DD-<chat>-<assunto>.md` no formato dos existentes (ex.: `2026-11-13-wyvern-criacao-poderes.md`):
   - chat de destino e bioma;
   - o que ler primeiro (CLAUDE.md, ficha, documentos oficiais);
   - tabela do que foi aprovado;
   - a primeira entrega pequena e os critérios de aceite testáveis;
   - o que preservar e quais arquivos compartilhados exigem aprovação;
   - Studio somente com reserva em `DOCS/estado/studio-em-uso.md`;
   - relatório no formato do CLAUDE.md.
   Escreva em português simples, sem jargão.
4. Para outro chat executar o pedido, ofereça abrir uma sessão nova com ele; não execute aqui sem o usuário pedir.
