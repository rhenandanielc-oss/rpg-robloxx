# Leão Solar — S2: subir na sela pelos dois lados (06/11/2026), APROVADA pelo usuário em 06/11/2026 (Blender; nada testado no Roblox)

**Pedido do usuário:** depois de ajustar a sela, fazer a animação de subida.

**Decisões do usuário (06/11):**
- o leão agacha e o cavaleiro sobe;
- subir pelos dois lados.

**Método:** o mesmo dos Lotes 4/5 do Crocodilo, já aprovados.
- **Manequim de teste:** caixas com proporções aproximadas do R15 (`manequim_r15.py` do Crocodilo, só importado). Não é rig R15 validado nem animação publicada.
- **Animação:** alvos de quadril, mãos e pés com IK, assados em FK.
- **Apoios:** medidos na pele e na sela do leão agachado; acompanham o osso.

## Clipes do leão (`build/e5/e5_22_montaria.py`, só movimento)

| Clipe | Quadros | s | Erro IK | Escorregamento p90 | Altura mín. | O que faz |
|---|---|---|---|---|---|---|
| Montar_E | 139 | 4,6 | 0 | ≤ 0,0002 | −0,01 | olha e vira as orelhas para o cavaleiro; agacha nivelado (2,6 studs), baixando o lado E; absorve o salto (1,45 s), o puxão (1,9 s) e a sentada (2,55 s); levanta com o cavaleiro (3,0–3,9 s) e termina no repouso |
| Montar_D | 139 | 4,6 | 0 | ≤ 0,0002 | −0,01 | o mesmo, espelhado para o lado D |

- **Lados:** lado E = x− (patas DE/TE), lado D = x+.
- **Assimetria da malha:** a malha do leão está ~0,45 para +X em relação à coluna. O caminho do cavaleiro é medido a partir do centro do corpo (XC), e os apoios são medidos em cada lado. O lado D é mais largo.

## Subida do cavaleiro (`build/s2/s2_02_demo_montaria.py`)

**Por que não pelo cotovelo:** subir pelo cotovelo da pata da frente, como no Crocodilo, atravessava o ombro e a **juba**. Ela cobre os lados até y −3 e é muito larga.

**Por que não pelo joelho:** o joelho de trás não serve de degrau. Agachado, o joelho E fica escondido sob o corpo (rig assimétrico).

**Solução: salto apoiado atrás da juba, na altura da sela:**
1. **0–0,9 s:** chega com dois passos.
2. **0,9–1,42 s:** espera o leão agachar e agacha (quadril a 1,72).
3. **1,45 s:** salta.
   - O pé da frente empurra na parte mais larga do flanco, com o joelho dobrando para fora.
   - As mãos sobem rente ao corpo, por fora.
4. **1,74–1,92 s:** agarra a borda da aba. Depois, a mão da frente passa para a **alça de Chifre Leve**.
5. **1,5–2,75 s:** a perna de trás passa por cima da garupa e desce do outro lado.
6. **2,75 s:** sentado, com os pés nos apoios.
7. **3,0–3,9 s:** o leão levanta com ele.

**Assento:** quadril a 0,1 acima do projeto da sela, com os pés no mesmo lugar dos apoios, para as coxas do R15 não entrarem na aba. O cavaleiro fica preso ao osso `Coluna1` em (0,45; 0,2; 12,51).

**Correção no manequim:** a perna dele partia reta e o IK não dobrava o joelho ao agachar, então o pé afundava 0,4 no chão. A demonstração agora dá uma dobra inicial de 15° nas canelas antes do IK (o módulo do Crocodilo não foi alterado).

## QA (manequim de teste)

Folga com sinal: negativa = a caixa do manequim entra.

| Clipe | Pior contra o leão | Pior contra a sela | Pés no chão | Velocidade máx. do quadril |
|---|---|---|---|---|
| Sentado | RightFoot 0.19 (q1), RightLowerLeg 0.19 (q1) | LeftUpperLeg -0.07 (q1), RightLowerLeg -0.06 (q1) | 11.05 | 0.0 |
| Montar_E | RightLowerLeg -0.11 (q53), RightUpperLeg 0.05 (q53) | LeftLowerArm -0.08 (q62), RightUpperLeg -0.08 (q81) | 0.03 | 15.9 |
| Montar_D | LeftLowerLeg -0.15 (q56), LeftUpperLeg 0.00 (q56) | LeftUpperLeg -0.09 (q85), RightLowerArm -0.09 (q61) | 0.03 | 15.9 |

- **Contra o leão:** a única entrada é a canela do pé que empurra o flanco, num só quadro do salto: −0,11 no lado E e −0,15 no lado D. Vem das caixas de 1 stud de espessura do manequim.
- **Mãos e tronco:** não tocam o leão em nenhum quadro.
- **Pés:** nunca afundam no chão.
- **Contra a sela:** os toques de −0,06 a −0,09 são das coxas sentadas apertando o couro do assento. A alça e a aba ficam sob as mãos.

**Sentado nos clipes reaproveitados** (`build/s2/s2_04_montado.py`, preso a `Coluna1`):

| Clipe | Menor folga contra o leão | Contra a sela (coxas) |
|---|---|---|
| Repouso Vigilante | 0.19 (RightFoot) | -0.07 |
| Andar | 0.11 (RightLowerLeg) | -0.08 |
| Trote | 0.12 (RightLowerLeg) | -0.08 |
| Corrida | 0.06 (RightLowerLeg) | -0.08 |
| Virar E | 0.07 (RightLowerLeg) | -0.08 |
| Frenagem | 0.06 (RightLowerLeg) | -0.08 |

## Evidência (`review/s2/`)

- `videos/Montar_{E,D}_{lado,34,frente,tras_34,close}.mp4` e `_lento.mp4`;
- `qa_montaria.json` e `qa_montado.json`.

## Arquivos

- `Leao_Solar_Ref_S2_montaria.blend`: cena de teste com o leão, a sela r4 (foco em Âmbar Solar e Couro das Planícies), o manequim e as ações `Leao_Montar_E/D` e `DEMO_Cav_Montar_E/D`/`DEMO_Cav_Sentado`.
- `Leao_Solar_Ref_E5_clipes_r7.blend`: as 28 ações oficiais mais `Leao_Montar_E/D` (30). O r6 ficou como estava.
- **Scripts:**
  - `build/e5/e5_22_montaria.py`: clipes do leão;
  - `build/s2/s2_02_demo_montaria.py`: demonstração da subida;
  - `build/s2/s2_03_render_montaria.py`: renders;
  - `build/s2/s2_04_montado.py`: teste sentado.

## Pendências

- Revisão visual do usuário.
- A desmontagem não foi pedida e não foi feita.
- No jogo, o cavaleiro real é um R15 (as caixas são só teste). A animação do jogador e a câmera ficam para o Studio, com autorização.
- Faltam textura de jogo e GLB da sela.
- Nada testado no Roblox.
