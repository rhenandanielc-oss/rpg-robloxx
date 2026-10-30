# RPG Roblox — repositório de planejamento e execução controlada

Este repositório será usado pelo Claude Code e pelo responsável pelo jogo para controlar a implementação do RPG Roblox. **Este pacote é documentação: não implementa nem altera o Roblox Studio.**

## Comece aqui
1. Leia `CLAUDE.md` (regras operacionais obrigatórias).
2. Consulte `MASTER-PROMPT.md` (escopo, decisões e prioridades).
3. Consulte `PROJECT-STATE.md` (status verificado; inicialmente DESCONHECIDO).
4. Escolha somente uma tarefa AUTORIZADA em `TASKS.md`.
5. Consulte a especificação do módulo em `SPECIFICATIONS/` e seus critérios de teste.
6. Após implementar e verificar, registre evidências no `PROJECT-STATE.md`, marque a tarefa correspondente e faça commit.

## Verdade das fontes
Os documentos originais `RPG_01_Mundo_e_Sistemas.docx` e `RPG_02_Criaturas_Elementos_e_Poderes.docx` são referência histórica. Os resumos deste GitHub são operacionais e podem omitir detalhes. Em caso de conflito, prevalecem as **decisões oficiais mais recentes** dos documentos, NÃO propostas anteriores. Antes de agir sobre ambiguidade relevante, interromper e solicitar decisão.

## Fluxo inicial
Primeira interação com Claude: executar **somente M0 — inspeção sem modificações**. Não criar biomas, scripts, serviços, pastas no Studio, nem apagar a baseplate antes da autorização expressa do usuário.

## Documentos principais
- `CLAUDE.md`: instruções curtas lidas pelo Claude Code.
- `MASTER-PROMPT.md`: constituição do projeto.
- `PROJECT-STATE.md`: estado factual e registro do último trabalho.
- `TASKS.md`: lista de tarefas autorizáveis e concluídas.
- `ACCEPTANCE-TESTS.md`: testes de aceitação.
- `SPECIFICATIONS/BIOMES-ART-BIBLE.md`: direção visual e construção dos oito biomas.
- `SPECIFICATIONS/SYSTEMS-OVERVIEW.md`: dependências de sistemas.
- `SPECIFICATIONS/MONETIZATION.md`: loja e criaturas premium.
- `DOCS/DECISIONS-AND-OPEN-ISSUES.md`: decisões aprovadas e bloqueios reais.
- `.gitignore`: arquivos que não devem ser versionados.

## GitHub e Roblox Studio
O GitHub versiona os arquivos presentes no repositório, **não acompanha automaticamente** alterações feitas apenas dentro de um arquivo `.rbxl`. Claude deve descrever quais alterações foram feitas no Studio e salvar o projeto com segurança. Avaliar futuramente Rojo somente se fizer sentido; não instalar ferramentas ou migrar a estrutura sem aprovação.
