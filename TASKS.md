# TASKS — checklist de execução (não de intenções)

## Convenções
- `[ ]` não iniciado / não validado.
- `[~]` em andamento (convenção textual, não marcador GitHub padrão; prefira `[ ]` com nota).
- `[x]` somente com implementação, evidência, teste e aprovação do escopo.
- O planejamento está aprovado em diversos aspectos, mas **NENHUMA tarefa abaixo foi comprovadamente implementada neste Studio**.

## M0 — Inspeção sem alterações (PRIMEIRA TAREFA A AUTORIZAR)
- [ ] M0.1 Confirmar projeto correto, caminho, ID e ambiente Roblox Studio.
- [ ] M0.2 Inventariar Workspace/Terrain, biomas, água, iluminação, vegetação e pontos de interesse.
- [ ] M0.3 Inventariar scripts, serviços, pastas, remotes, models e dados persistentes.
- [ ] M0.4 Verificar erros e desempenho sem criar ou modificar objetos.
- [ ] M0.5 Relatar diferenças entre Studio e documentos e recomendar primeiro bloco seguro.

## M1 — Dados e estrutura
- [ ] M1.1 Aprovar arquitetura de dados e salvamento.
- [ ] M1.2 Implementar e validar persistência de moedas/inventário/criaturas.
- [ ] M1.3 Implementar proteção básica contra duplicações e operações inconsistentes.

## M2 — Mundo e ambiente
- [ ] M2.1 Validar topologia/escala e oito regiões no projeto existente.
- [ ] M2.2 Construir macroterreno regional aprovado, por lotes reversíveis.
- [ ] M2.3 Água, transições ambientais e caminhos de exploração.
- [ ] M2.4 Vegetação regional, árvores com vento otimizado, clima e iluminação.
- [ ] M2.5 Vilas, ruínas, instalações e entradas físicas de dungeons.
- [ ] M2.6 Testes de desempenho desktop e mobile.

## M3 — Criaturas e combate
- [ ] M3.1 Reconciliar fichas oficiais do documento RPG_02.
- [ ] M3.2 Combate misto, elementos, habilidades e testes PvE/PvP.
- [ ] M3.3 Evolução, crescimento, companhia e persistência.
- [ ] M3.4 Criaturas premium, probabilidades do ovo e Serpente Abissal.

## M4 — Inventário e economia
- [ ] M4.1 Inventário, materiais, coleta e crafting.
- [ ] M4.2 Auditar e configurar as 75 receitas e variantes regionais iniciais.
- [ ] M4.3 Aprimoramentos, comércio, taxas e proteção de recursos.

## M5 — Missões e história
- [ ] M5.1 Diário, pistas e progresso individual/cooperativo.
- [ ] M5.2 Implementar 48 missões principais e campanha central.
- [ ] M5.3 Auditoria de spoilers sobre origem da entidade.

## M6 — Chefes e dungeons
- [ ] M6.1 Grupos 1–4, instâncias, retorno, checkpoints e ressuscitação individual.
- [ ] M6.2 Chefes obrigatórios, contadores Lendários e recompensas.
- [ ] M6.3 Oficiais, dungeon final e sequência narrativa protegida.

## M7 — Loja e monetização
- [ ] M7.1 Aprovar cadastros, tipos de compra e políticas antes de ativar loja.
- [ ] M7.2 Concessão persistente e idempotente dos 10 produtos.
- [ ] M7.3 Divulgação e elegibilidade das chances reais do ovo, sem duplicação nos 3 primeiros.
- [ ] M7.4 Testes de restauração, falha de compra e anti-pay-to-win.

## M8 — QA e publicação
- [ ] M8.1 Testar regressões de todos os sistemas.
- [ ] M8.2 Validar acessibilidade, desempenho e persistência.
- [ ] M8.3 Alfa fechado, beta e correções.
- [ ] M8.4 Autorizar lançamento público após critérios aprovados.
