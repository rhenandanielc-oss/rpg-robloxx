# Organização dos chats por bioma e criatura (03/11/2026)

O usuário pediu um **chat principal por bioma** e, dentro de cada bioma:
- um **subchat por criatura domesticável**;
- um **subchat de fauna selvagem**, que cobre os 3 animais de recurso do bioma.

Cada bioma é um **grupo** na barra lateral do app. Os chats de um mesmo bioma ficam juntos no grupo.

Fontes (versões vigentes):
- `C:\Users\Rhenan\Downloads\RPG_01_Mundo_e_Sistemas_ATUALIZADO.docx`;
- `C:\Users\Rhenan\Downloads\RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO.docx`.

A seção "ATUALIZAÇÃO OFICIAL — 30/10/2026" de cada documento prevalece.

## Mapa

| Bioma | Criaturas domesticáveis (1 subchat cada) | Fauna selvagem (1 subchat por bioma) |
|---|---|---|
| Floresta Ancestral | Lobo Ancestral; Urso Silvestre | Cervo-do-Bosque, Javali Silvestre, Coruja-da-Floresta |
| Montanhas Altas | Dragão das Montanhas (Fogo); Wyvern | Íbex Montanhês, Águia-real, Besouro Rochoso |
| Pântano Nebuloso | Basilisco; Crocodilo Primordial | Garça-do-Pântano, Javali-do-Brejo, Besouro Luminoso |
| Planícies Douradas | Leão Solar; Búfalo Colossal | Antílope-das-Planícies, Avestruz Selvagem, Tatu Rochoso |
| Tundra Congelada | Lobo Ártico; Dragão Glacial (Gelo) | Lebre Ártica, Cabra-das-Neves, Mariposa Glacial |
| Deserto de Cristal | Escorpião Colossal; Lagarto Cristalino | Raposa-do-Deserto, Abutre Desértico, Escaravelho Cristalino |
| Costas Selvagens | Serpente Marinha; Leviatã Jovem | Gaivota Costeira, Caranguejo-de-Recife, Lagarto Costeiro |
| Terras Corrompidas | Cérbero Sombrio; Dragão Sombrio (Sombra) | Corvo Sombrio, Rato Espinhoso, Besouro-de-Cinzas |

Situação das criaturas já trabalhadas:
- **Dragão das Montanhas e Dragão Glacial:** já produzidos. Todo o trabalho está no repositório (git), em `DOCS/estado/dragao-*.md` e nas memórias do projeto.
- **Dragão Sombrio:** em produção. O chat original foi movido para o grupo Terras Corrompidas.

Cada subchat mantém a ficha-resumo da sua criatura em `DOCS/criaturas/<criatura>.md`.

## Regras de convivência (todos os chats)

1. **Escopo.** Cada chat mexe só na sua criatura ou bioma: pastas, clipes e arquivos próprios. Mudança em arquivo compartilhado precisa ser combinada com o usuário antes. São compartilhados:
   - `meshy/anim_silverwing.py`;
   - `SonsConfig`, `SonsDragao_Cliente`, `SonsGelo`;
   - `ConfigCombate`, `EstadosDragao`, `Cerebro`;
   - o mapa/terreno.
2. **Roblox Studio: um chat por vez.**
   - Antes de usar o Studio (Edit ou Play), leia `DOCS/estado/studio-em-uso.md`.
   - Se outro chat estiver usando, não mexa: avise o usuário.
   - Se estiver livre, escreva seu nome e a hora no arquivo; ao terminar, volte para "livre".
3. **Git.** Faça commit só dos arquivos que você mudou, sem `git add -A`, e só quando o usuário autorizar.
   - Nunca faça stash, reset nem troca de branch.
   - O commit termina com `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
4. **`CLAUDE.md` vale para todos.** Inclui o formato de relatório, nada de inventar regra, `[PROPOSTA]` não é oficial e Dragon Ranch é outro projeto.
5. **Não confundir as categorias.** A fauna de recursos não é criatura domesticável, e vice-versa.
