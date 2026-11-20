---
name: questionar-antes
description: Entrevistar o usuário sobre a mecânica e sobre como tudo deve ser ANTES de construir qualquer coisa neste RPG Roblox — poder, ataque, IA, criatura, animação, sistema, missão, bioma, item, loja, interface ou efeito visual. Levanta o que não está decidido nos documentos oficiais, pergunta em rodadas curtas com opções claras, confirma o entendimento e só então libera a execução. Use no início de toda tarefa nova de criação ou mudança de comportamento, e sempre que o pedido deixar margem para interpretação.
---

# Questionar antes de agir

O usuário quer ser consultado sobre as mecânicas e sobre como cada coisa deve ser **antes** de qualquer construção. Construir a partir de uma suposição e depois refazer custa mais do que perguntar. Esta skill roda depois da inspeção M0 (somente leitura) do CLAUDE.md e antes de qualquer edição, Blender, Studio ou geração paga.

## 1. Descobrir o que já está decidido (não perguntar isso de novo)
Leia, só o necessário:
- `MASTER-PROMPT.md` e `DOCS/DECISIONS-AND-OPEN-ISSUES.md`;
- a ficha do assunto em `DOCS/criaturas/`, `DOCS/biomas/`, `DOCS/fauna/` ou `DOCS/equipamentos/`;
- `REFERENCIAS_PODERES_E_EFEITOS.md` (poderes);
- os pedidos em `DOCS/pedidos/` e a memória;
- os documentos oficiais `RPG_01_Mundo_e_Sistemas_ATUALIZADO.docx` e `RPG_02_Criaturas_Elementos_e_Poderes_ATUALIZADO.docx` (raiz do repositório; vale a seção de 30/10 e a decisão mais recente e explícita).

Monte uma lista curta, separando:
- **Já decidido**, citando a fonte;
- **Em aberto**, o que vai para as perguntas.

## 2. O que perguntar (escolha só o que muda o resultado)
**Mecânica**
- o que dispara;
- quem usa: jogador montado, IA selvagem ou os dois;
- em terra e/ou no ar;
- alvo: travado, mouse, câmera, área, primeiro na linha;
- quantas vezes acerta cada alvo;
- o que acontece se errar ou bater num obstáculo;
- interação com outros poderes, estados e elementos;
- como cancela;
- se funciona em movimento (regra do usuário: ataques em movimento).

**Sensação e visual**
- como o jogador percebe a preparação, a ação e o impacto;
- velocidade e peso;
- cores do elemento/bioma;
- som;
- referência que o usuário tem em mente, ou se ele quer opções;
- o que NÃO pode parecer (ex.: "laser", "jaula").

**Números e equilíbrio**
- só pergunte se o usuário quer definir agora;
- o padrão é deixar **PROVISÓRIO** e balancear depois (decisão já repetida pelo usuário).

**Escopo e entrega**
- qual a primeira entrega pequena;
- onde testar (place, área isolada);
- o que preservar;
- o que conta como pronto (critério de aceite testável).

**Regras do jogo** (confirmar só se o pedido parecer esbarrar nelas)
- vantagem paga no PvP;
- segredo da entidade ancestral;
- reviver aliados em dungeon;
- desempenho no celular.

## 3. Como perguntar
- Rodadas de **no máximo 4 perguntas**, com `AskUserQuestion`, cada uma com 2–4 opções concretas.
  - A sua recomendação vem primeiro, com "(Recomendado)".
  - Quando ajudar, use `preview` para mostrar um esboço, código curto ou tabela.
- Cada pergunta se sustenta sozinha: diga do que se trata e por que importa em uma frase.
- Linguagem simples, sem jargão técnico. Se um termo for inevitável, explique entre parênteses.
- Uma decisão por pergunta; não junte duas com "e".
- Quando a dúvida é visual, mostre: imagem de referência, esboço rápido ou captura do estado atual (`SendUserFile`) antes ou junto da pergunta.
- Nada de perguntar o que está em "Já decidido". Se a fonte parecer desatualizada ou em conflito, mostre as duas versões e pergunte qual vale.
- Pare de perguntar quando o que falta não muda a primeira entrega. Detalhes de rodadas futuras podem esperar.

## 4. Confirmar antes de executar
1. Escreva um resumo curto, "Entendi assim":
   - o que será feito na primeira entrega;
   - o comportamento esperado;
   - o que fica PROVISÓRIO;
   - o que será preservado;
   - como vai ser testado e mostrado.
2. Peça um "pode seguir" explícito. Sem ele, não construa.
3. Registre as respostas na ficha certa em `DOCS/`, como "decisão do usuário (data)". Regras que valem para outras conversas vão também para a memória.

## 5. Durante a execução
- Se surgir uma dúvida nova que mude o resultado, pare e pergunte (uma pergunta só) em vez de supor.
- Escolhas pequenas e reversíveis (nome de variável, ordem de arquivos) não viram pergunta: decida, diga qual foi e siga.
- Ao entregar, mostre o resultado (vídeo/captura) e faça UMA pergunta de aprovação ou ajuste.

Skills relacionadas: `ideia-de-jogo` (quando o usuário ainda está pensando a ideia) e `design-poderes` (regras e padrões de poderes e efeitos).
