# Estratégia de backup (PROPOSTA)

**Status:** APROVADA em 2026-10-19 (pasta `Documents\RPG_Roblox\BACKUPS` e nomes da seção 3). Backup `RPG_BKP_2026-10-19_pre-M1.rbxl` confirmado pelo usuário em 2026-10-19. Nada foi criado, salvo ou alterado no Studio.
**Base:** `CLAUDE.md` itens 5, 6 e 14. Local do backup estava "A DEFINIR" em `PROJECT-STATE.md`.

## 1. O que a inspeção mostrou
- O lugar é `rpg_roblox` (placeId 114230639394991), aberto em sessão de edição ao vivo ("joined live editing session"), o que indica um lugar salvo na nuvem da Roblox.
- Nenhum `.rbxl` do RPG foi encontrado em Documentos, Área de Trabalho, Downloads ou OneDrive (profundidade 4; arquivos de Dragon Ranch e ilha_coracao excluídos). Também não foi lida a pasta de autosave do Studio, que não existe ou está vazia.
- Portanto: **não existe hoje backup nem cópia local verificável**. Isso não foi confirmado fora dessas pastas.

## 2. Camadas propostas
| Camada | O que é | Quando | Como |
|---|---|---|---|
| A. Histórico de versões da Roblox | Versões publicadas do lugar, restauráveis | Já existe, a cada publicação | Roblox Creator Hub > Versions |
| B. Backup de segurança do `.rbxl` | Um arquivo exportado e imutável | Antes da primeira mudança destrutiva e antes de cada marco (M1, M2, ...) | Você faz `File > Save to File As...` no Studio |
| C. Cópia de trabalho identificada | Arquivo local de uso diário | Contínuo | Mesmo fluxo, nome com marcador de trabalho |
| D. Código-fonte em Git | Scripts e documentos | A cada tarefa aprovada | Commit e push somente com sua autorização |

Observação: arquivos `.rbxl` não funcionam bem no Git (binários grandes). Use Git para Markdown e scripts, e para `.rbxl` use apenas a camada B.

## 3. Nomes e pasta sugeridos
Pasta: `C:\Users\Rhenan\Documents\RPG_Roblox\BACKUPS\` (fora do repositório, não sincronizada com Git; confirmar se prefere outro local).

- Backup de segurança, nunca sobrescrito: `RPG_BKP_<AAAAMMDD>_<marco>.rbxl`, por exemplo `RPG_BKP_20261019_pre-M1.rbxl`.
- Cópia de trabalho: `RPG_WORK.rbxl`.
- Regra: um arquivo novo por marco, e a data no nome impede sobrescrita. Sem backups por tarefa pequena, para evitar a proliferação de `.rbxl` que `CLAUDE.md` item 5 proíbe.
- Retenção: manter todos os backups de marco; podar apenas com sua autorização.

## 4. Quando o backup é obrigatório
1. Antes de qualquer tarefa que escreva no Studio pela primeira vez (início do M1.2).
2. Antes de mudanças destrutivas: apagar ou substituir terreno, migração em massa, reorganização de pastas.
3. Ao fechar cada marco (M1, M2, ...) depois de testes aprovados.

Não é necessário backup para: inspeção, edição de Markdown ou propostas.

## 5. Papel de cada parte
- **Você:** salvar o `.rbxl` (o Claude não consegue fazer `Save As` por MCP de forma verificável) e confirmar que o arquivo existe.
- **Claude:** pedir o backup antes da tarefa, conferir o nome/caminho informado por você e registrar a data e o nome em `PROJECT-STATE.md`. Não declarar backup feito sem sua confirmação.

## 6. Restauração
1. Camada A: restaurar versão pelo Creator Hub e republicar.
2. Camada B: abrir o `.rbxl` de backup, `Save As` para o lugar e publicar sobre o lugar do RPG somente com sua decisão.
3. Testar abertura e contagem básica (Workspace, scripts) após restaurar e registrar o resultado.

## 7. Riscos
- Edição colaborativa ativa: outro colaborador pode alterar o lugar durante a tarefa. Combinar janela de edição antes de mudanças grandes.
- Backup feito com o lugar vazio tem pouco valor agora, mas fixa o ponto de partida do M1.
- Perfis de jogadores (DataStores) não fazem parte do `.rbxl`. Serão cobertos pela cópia da versão anterior do perfil prevista em `DOCS/M1.1-DATA-ARCHITECTURE.md`.

## 8. Decisões necessárias
1. Aprovar a pasta e o padrão de nomes acima, ou indicar outro.
2. Confirmar se existe algum `.rbxl` do RPG que eu não encontrei (inclusive em outro disco).
3. Confirmar que fará o backup `RPG_BKP_<data>_pre-M1.rbxl` antes do M1.2.
