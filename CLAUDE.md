# Instruções permanentes para Claude Code — RPG Roblox

1. **NÃO modifique o Roblox Studio sem autorização expressa do usuário para a tarefa atual.** Inicie sempre com inspeção SOMENTE LEITURA (M0) e relatório do que realmente existe.
2. Leia `MASTER-PROMPT.md`, `PROJECT-STATE.md`, a tarefa correspondente em `TASKS.md` e apenas as especificações necessárias. Não absorva todo o histórico a cada sessão.
3. **Não confunda este RPG com o projeto separado Dragon Ranch.** Regras, mapas, fazendas e dragões de Dragon Ranch não pertencem automaticamente a este jogo.
4. Identifique o escopo exato, dependências, arquivos/objetos afetados, riscos e critérios de aceite. Na dúvida relevante, não invente regra.
5. Execute uma mudança pequena por vez. Evite reescrever sistemas funcionais, alterar serviços sem necessidade ou criar múltiplos `.rbxl` de backup.
6. Mantenha uma cópia de trabalho identificada e um backup de segurança. Não sobrescreva backups históricos. Confirmar a estratégia de backup antes de mudanças destrutivas.
7. **Só marque `[x]` em `TASKS.md` após implementação real + teste + evidência.** Não marque como concluído algo apenas descrito, escrito parcialmente ou presumido.
8. Ao final de cada tarefa autorizada: registre mudanças, resultados de testes, limitações, próximos passos e status factual em `PROJECT-STATE.md`; sugira mensagem de commit. Commit/push só quando autorizado e disponível.
9. Respeite separação servidor/cliente no Roblox; valide moedas, inventário, loot, progressão, comércio e compras no servidor. Sem promessas de segurança não verificadas.
10. Dados persistentes, reconexões, cooperação e compras exigem testes de falha, não apenas testes de sucesso.
11. Mantenha mundo em fantasia realista, natural e imersivo, com animação de vento localizada nas folhas/plantas, água integrada e identidade por bioma; desempenho em PC e celular é requisito.
12. Não revele antecipadamente na narrativa que a entidade ancestral era protetora. A verdade só aparece após vencer a organização E derrotar a entidade.
13. Monetização: nunca ignorar requisitos narrativos/lendários, não aumentar atributos/loot via compra ou transformar PvP em pay-to-win.
14. Não executar instalação de dependências, acesso externo, compras, exclusões em massa ou mudanças de arquitetura sem consentimento.
15. Se a ferramenta de integração com Roblox Studio não estiver disponível ou falhar, reporte claramente. Nunca declare implementação/teste sem prova.

## Modelo obrigatório de resposta do Claude
- Tarefa autorizada e objetivo
- Leitura/inspeção efetuada
- Alterações reais efetuadas (ou "nenhuma")
- Testes e evidências
- Riscos/pendências
- Arquivos atualizados e estado para próxima sessão
- Próximo passo proposto **aguardando aprovação**
