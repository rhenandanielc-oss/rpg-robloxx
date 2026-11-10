# Lote 3 no Studio (04/11/2026) — resultados medidos

Place `rpg_roblox` (PlaceId 114230639394991). Ambiente: Play/PC no Studio. Medido no servidor; o cliente foi conferido depois da replicação.

## Métricas
- **Pose:** posição dos ossos no espaço do modelo, comparada com o Blender quadro a quadro.
- **Deriva:** osso de punho/tornozelo (Mao/Pe) e de dedos (Dedos/DedosPe, aproximação da garra), em coordenadas do mundo.
  - Apoio = altura menor que o mínimo + limiar. Limiar 0,01 = apoio firme; limiar 0,04 inclui o rolamento da pata.
  - Amostragem no Heartbeat (cerca de 30–60 Hz), durante todo o clipe, descartando só o transitório até a faixa avançar 0,02 s.
  - **Não** é a sola nem a pele deformada: o Studio não lê vértices.
- **osso_max:** maior velocidade de osso no espaço do modelo, para separar ação rápida de estalo.

## Poses conhecidas (Animator, faixa congelada)
- 33 quadros: início, extremos e final.
  - As 6 poses de quadro 0 iguais ao repouso entraram uma vez só.
  - O último quadro foi lido 0,5 ms antes do fim.
- **ERRO_MAX = 0,0025 stud.**
- Cliente = servidor na Ameaça q31 (mandíbula y 12,375; Blender 12,3751), com as 4 malhas com skin.

## Ensaios isolados

| Clipe | Duração (s) | Loop | Prioridade | Repetições 1× / 1/3 | Razão tempo 1× / 1/3 | Deriva lim 0,01 (punho/dedos) | Deriva lim 0,04 | osso_max Studio 1× (Blender) |
|---|---|---|---|---|---|---|---|---|
| Observar | 4,4 | não | Action | 3 / 3 | 0,986–0,995 / 0,333 | ≤ 0,002 | ≤ 0,002 | 4,7 (4,5) |
| Sentar | 1,4 | não | Action | 3 / 3 | 0,978–0,982 / 0,331 | ≤ 0,003 | ≤ 0,012 | 5,6 (4,9) |
| LevantarSentado | 1,4 | não | Action | 3 / 3 | 0,980–0,983 / 0,331–0,332 | ≤ 0,003 | ≤ 0,012 | 5,4 (4,9) |
| Deitar | 2,0 | não | Action | 3 / 3 | 0,986–0,988 / 0,332 | ≤ 0,003 | ≤ 0,013 | 8,0 (7,3) |
| LevantarDeitado | 2,0 | não | Action | 3 / 3 | 0,970–0,988 / 0,331–0,332 | ≤ 0,003 | ≤ 0,012 | 8,2 (7,3) |
| Comer | 2,4 | sim (3 ciclos) | Action | 2 / 1 | 0,996 / 0,333 | 0,000 | 0,000 | 0,7 (0,6) |
| Ameaça | 3,2 | não | Action2 | 3 / 3 | 0,985–0,993 / 0,332–0,333 | ≤ 0,048 | ≤ 0,071 | 26,2 (23,6) |
| GolpePata | 1,3 | não | Action2 | 3 / 3 | 0,977–0,980 / 0,331 | ≤ 0,018 | ≤ 0,094 | 40,2 (41,2) |
| Mordida | 1,0 | não | Action2 | 3 / 3 | 0,971–0,974 / 0,330–0,331 | ≤ 0,002 | ≤ 0,002 | 26,8 (24,8) |
| ReaçãoImpacto | 1,0 | não | Action3 | 3 / 3 | 0,974–0,978 / 0,330–0,331 | ≤ 0,006 | ≤ 0,006 | 22,3 (31,1) |

- **Condições dos ensaios:**
  - Todos começaram limpos e em tempo 0, sem mistura com outra faixa.
  - Todos terminaram por `Stopped` (as ações únicas) ou ao atingir o alvo de 3 ciclos (Comer).
  - Pivô restaurado e nenhuma conexão sobrando.
- **Referência do Blender** com a mesma métrica de ossos, limiar 0,04, 30 Hz:
  - Ameaça Mao 0,072/0,074, dedos 0,008;
  - GolpePata MaoE 0,034, DedosE 0,041;
  - Sentar e Deitar: dedos traseiros 0,008–0,009;
  - demais ≤ 0,0002.
- **Interpretação:** o Studio amostra entre os keyframes de 30 qps, com interpolação linear, então a métrica de 0,04 sobe. No lote 2, o teste determinístico a 90 Hz provou essa origem.

## Sequências de postura e ação (mistura 0,1 s, sem reiniciar a pose; pivô fixo)

| Sequência | Resultado | osso_max | Deriva lim 0,01 / 0,04 |
|---|---|---|---|
| Repouso→Sentar→(pose sustentada 1,5 s)→LevantarSentado→Repouso | OK | 5,4 (sozinho 5,6) | 0,002 / 0,011 |
| Repouso→Deitar→(sustentada 1,5 s)→LevantarDeitado→Repouso | OK | 7,9 | 0,003 / 0,010 |
| Repouso→Ameaça→Repouso | OK | 26,5 | 0,031 / 0,035 |
| Repouso→Observar→Repouso | OK | 4,4 | 0,002 / 0,002 |
| Repouso→GolpePata→Repouso | OK, leve acima do clipe sozinho | 45,1 (sozinho 40,2; Blender 41,2) | 0,018 / 0,070 |
| Repouso→Mordida→Repouso | OK | 26,0 | 0,002 / 0,002 |
| Repouso→ReaçãoImpacto→Repouso | OK | 28,9 | 0,004 / 0,019 |
| **Repouso→Comer→Repouso** | **PENDENTE** | 28,6 (0,1 s); 9,3 (0,3 s); 6,0 (0,5 s) | **0,154–0,297 / 0,600** |

- **Por que o Comer falha:** o clipe começa com a MaoE 0,6 mais à frente (z −2,03 contra −1,43 no Repouso) e com a cabeça 1,8 mais baixa. A mistura desliza a pata 0,6 no chão, sem passo, e a mistura mais longa não resolve. Corrigir exige passo de entrada e de saída no clipe, que é mudança no Blender.
- **Como a pose terminal é sustentada:** a faixa de Sentar/Deitar é congelada com `AdjustSpeed(0)` no passo de animação, antes de terminar, em `Length − 0,0005`. Não há loop nem retorno automático. O clipe seguinte entra por mistura.

## Defeitos encontrados e corrigidos no teste do urso (não nos clipes)
1. Transitório da 1ª amostra (pose do clipe anterior).
2. Faixa parada ainda listada por um ou dois passos.
3. **O Animator mantém a última pose quando a faixa para** (Comer parado no meio do loop: 20 ossos fora do repouso). `parar()` agora zera os `Transform`.
4. O encadeador congelava a pose terminal tarde demais (pelo `task.wait`), com a faixa já encerrada. O fade misturava com o repouso (osso a 24–32 studs/s). Agora congela no `Stepped`.

## Regressão
- **Repouso:** 3 ciclos, razão 0,999.
- **Rugir:** 2,4 s.
- **Andar a 3,23:** deriva de 0,015 / 0,055. O piloto ficou em 0,003–0,049; os 0,055 caem na faixa de 0,04, que inclui o rolamento.
- **Lote 2:** KeyframeSequences e dados preservados, conferidos por contagem e somas.

## Capturas
`studio/` (14 capturas, cliente) e `blender/` (renders com as mesmas câmeras). Pranchas:
- `review/PRANCHAS_v2/15_lote3_posturas_blender_x_roblox.png`
- `review/PRANCHAS_v2/16_lote3_acoes_boca_blender_x_roblox.png`

GIFs do Blender, normal e lento: `gif_blender/`. **No Studio não houve gravação de vídeo** (a ferramenta só captura imagens). A evidência de velocidade normal e lenta no Studio é a razão de tempo medida, mais as capturas em quadros conhecidos.
