---
name: relatorio-rpg
description: Fechamento de tarefa no RPG Roblox - relatório no formato obrigatório do CLAUDE.md (em português), registro factual nas notas de estado (DOCS/estado/ e PROJECT-STATE.md), TASKS.md só com evidência, mensagem de commit sugerida. Use ao terminar qualquer tarefa autorizada.
---

# Relatório e registro de estado

## Registro (antes do relatório)
1. Acrescente a entrada na nota do sistema em `DOCS/estado/` (dragão, IA, combate, biomas, ferramentas...) com data absoluta (AAAA-MM-DD): o que mudou, testes com evidência, o que NÃO foi testado, pendências.
2. Atualize o índice `PROJECT-STATE.md` (uma linha por entrada nova, com link `[[nota]]`).
3. `TASKS.md`: marque `[x]` SOMENTE com implementação real + teste + evidência. Nunca por presunção.
4. Commit local no git com mensagem em português, curta, no imperativo. Push só com autorização.

## Relatório ao usuário (formato obrigatório do CLAUDE.md)
- **Tarefa autorizada e objetivo**
- **Leitura/inspeção efetuada**
- **Alterações reais efetuadas** (ou "nenhuma") — arquivos e objetos do Studio
- **Testes e evidências** — o que foi medido/capturado; o que não foi testado, dito claramente
- **Riscos/pendências** — incluindo números `NAO_APROVADO` e decisões que são do usuário
- **Arquivos atualizados e estado para a próxima sessão**
- **Próximo passo proposto aguardando aprovação**

Fatos, não promessas: nunca declarar implementado/testado sem prova. Narrativa: não revelar que a entidade ancestral era protetora. Monetização sem pay-to-win.
