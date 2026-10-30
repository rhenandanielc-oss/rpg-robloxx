# Visão modular — dependências

## Sequência de dependências
1. M0 Inspeção: confirmar jogo correto e estado existente.
2. M1 Dados: identidades, persistência e proteção contra duplicações.
3. M2 Mundo: terreno, biomas, caminhos, entradas de dungeon e otimização.
4. M3 Criaturas e combate: entidades, atributos, IA, progressão, elementos, PvP/PvE.
5. M4 Equipamentos/economia: coleta, receitas, mercado, inventário e melhorias.
6. M5 Missões: NPCs, 48 missões regionais, oito pistas, história central.
7. M6 Dungeons/chefes: grupo 1–4, ressurreições, loot, bosses e história final.
8. M7 Loja: produtos, validação de compra, concessão, direitos e ovos.
9. M8 QA: testes integrados, dispositivos, falhas, beta e lançamento.

## Componentes transversais
- Inventário/loja/loot usam o MESMO modelo de direitos e salvamento; evitar três sistemas incompatíveis.
- Missões, conquistas e chefes escrevem progresso sem duplicação por reconexão.
- Criaturas e habilidades precisam funcionar com humano e cliente móvel.
- Dungeons possuem retorno seguro ao mundo e contador imutável por tentativa.
- Desempenho e interfaces devem ser observados em TODOS os módulos, não apenas ao final.

## Parâmetros ajustáveis
Dano, tempos, custos, chances (exceto os pesos oficiais do ovo), limites de recursos, distância de renderização, densidade de árvores e número de instâncias precisam ficar configuráveis. Não usar valores ilustrativos antigos como oficiais.
