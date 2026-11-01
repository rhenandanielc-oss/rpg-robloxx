# Sistema universal de animações — espécie Dragão

Atualizado em 2026-11-01, no lugar `Teste-animacoes_CR.rbxl` (Studio) e em `BLENDER/Criaturas/Teste_IA`.

Formas regionais:
- **Dragão das Montanhas** (Fogo): desenvolvido.
- **Dragão Glacial** (Gelo): em desenvolvimento.
- **Dragão Sombrio** (Sombra): ainda sem modelo.

## 1. Arquitetura compartilhada (o que é reutilizado)

| Camada | Onde | Papel | Por forma |
|---|---|---|---|
| Gerador de clipes | `meshy/anim_silverwing.py` (Blender) | Gera cada clipe com antecipação, ação, reação do corpo, movimento secundário e recuperação. Inclui IK nas patas, cauda em ondas da base à ponta, asas por subárvores e mistura de poses. | Personalidade por variáveis de ambiente (ver seção 2) |
| Esqueleto | Silverwing: 100 ossos, mesmos nomes | O mesmo gerador, o mesmo apelido de ossos e o mesmo Studio servem para todos. | Cada forma encaixa o esqueleto na própria anatomia (`rig_dragao.py`, `rig_glacial.py`); poses não são transferidas entre malhas |
| Ponte para o Studio | `meshy/exportar_clipes_json.py` + `V14/ia/montar_kfs_json_*.luau` | JSON → KeyframeSequence, com cópia anterior recuperável | Prefixo por forma: `Silverwing_` (Fogo), `Glacial_`; pasta `Animacoes_<Forma>` |
| Nomes lógicos | `Animacoes_<Forma>/Apelidos` | Nome lógico → clipe, com reserva quando a forma não tem o clipe | O Glacial não herda os poderes de Fogo (caem em Parado/Pairar) |
| Máquina de estados | `ReplicatedStorage.Comportamento_Dragoes.EstadosDragao` | Estados → entrada, laço e saída, com fades. Insere a transição de postura (em pé, deitado, abaixado, sentado). `M:Pontual()` toca uma reação por cima do estado, com prioridade Action e peso proporcional. | Comum |
| Movimento secundário | `MovimentoVivo_Cliente` + `MovimentoVivo.Perfis` | Só no cliente. Pescoço e cabeça entram nas curvas, a cauda segue com atraso, as patas reagem à aceleração e a asa interna abaixa na curva. O olhar segue a câmera do cavaleiro ou o alvo da IA (`AlvoOlhar`). | Perfil por rig (`PerfilMovimento`) |
| IA selvagem | `ServerScriptService.IA_Dragao.Cerebro` | Contexto → estado (ver seção 4) | Comum |
| Combate | `Combate_Dragao.Nucleo` | Clipes de ataque com marcadores (contato, emissão) casados com a configuração | Habilidades por forma (`ConfigCombate.habilidadesForma`) |
| Montaria | `Montaria_Dragao_Servidor` / `Montaria_Cliente` | Mistura de voo por manobra; velocidades medidas nos pés | `ConfigMontaria` por modelo |

## 2. Personalidade por forma (variáveis do gerador)

| Forma | Arquivo | Valores | Efeito |
|---|---|---|---|
| Montanhas (Fogo) | `dragao_novo/env_clipes_cr.sh` | AMP 2,5; 4 batidas por clipe de voo; PASSO_PESADO | Enérgico, passada pesada, batidas fortes |
| Glacial (Gelo) | `dragao_gelo/env_clipes_glacial.sh` | AMP 2,0; NB_VOO 3; NB_PAIRAR 3; NECK_BASE 0; sentado com recua 30 | Calculado, batidas amplas e cadenciadas, pescoço erguido nobre |
| Sombrio (Sombra) | (a criar) | Proposta, ainda não aprovada: AMP ~1,6; giros curtos e precisos; postura baixa (`base_pe`); cauda rente | Furtivo e predatório; definir com o modelo |

As velocidades de andar e correr (medidas nos pés) não mudam com a personalidade: VEL_ANDAR 7,9 e VEL_CORRER 18,94 studs/s nas duas formas.

## 3. Repertório (✔ existe, ★ novo em 01/11, ✗ falta)

**Comportamento**
- ★ Rugido territorial (`Rugido_Territorial`)
- ★ Intimidação (`Intimidar`, em laço)
- ★ Curiosidade (`Curiosidade`, com a cabeça inclinada de lado)
- ✔ Alerta e observação (`Reagir_Estimulo`, `Idle_Alerta_Mantido`, `Observar`, `Observar_Farejar`)
- ✔ Descanso, sono e despertar (`Abaixar`, `Abaixado`, `Adormecer`, `Dormir`, `Acordar`, `Sentar`, `Sentado`, `Levantar_Sentado`)
- ✔ Alimentação e água (`Comer`, `Beber`)
- ★ Reação a dano (`Dano_Leve`, `Dano_Forte`, `_Ar`)
- ★ Rugido direcionado: o rugido de combate continua; a novidade é que a IA grava `AlvoOlhar` e o cliente vira pescoço e cabeça para o alvo.

**Locomoção**
- ✔ Parado, Andar, Correr, Parada (frenagem)
- ✔ Decolagem, Voo, Voo_Rapido, Planeio, Pairar, Subida, Descida, Mergulho, Curva_E/D, Pouso
- ★ Recuperação do mergulho (`Mergulho_Saida`)

**Combate**
- ✔ Ataque_Mordida, Mordida_Aerea, Ataque_Garra_E/D, Ataque_Cauda, Rugido_Combate (+ `_Camada`), Preparar_Combate (postura e intimidação em combate)
- ✔ Fogo: Sopro (início, laço e fim), Arremetida, Tempestade de Asas, Coração Infernal
- ✗ Gelo e Sombra: kits pendentes nos documentos oficiais. **Não criar** poderes nem copiar os do Fogo.

**Faltam ou são limitações conhecidas**
- Língua e garganta não têm ossos próprios. A língua é rígida no maxilar, e a garganta reage pelo pescoço e peito.
- Áudio por forma: o rugido grave do Glacial ainda não foi feito (SonsDragao_Cliente + SonsConfig).
- `Mergulho_Saida` ainda não está ligado ao misturador de voo da montaria.
- Dano no voo montado ainda não está ligado.

## 4. IA → animação (Cerebro, PATCH_ANIM_UNIVERSAL)

| Contexto | Estado / clipe | Regra contra repetição |
|---|---|---|
| Jogador distante observado | Observação ou Curiosidade, alternando | Observação no máximo a cada 25 s (regra já existente) |
| Jogador perto do dragão (alerta pessoal) | Intimidação, encarando o alvo | Sai por habituação (25 s parado sem avançar) |
| Ameaça ao ninho, nível 1 | Alerta | — |
| Invasor ou ataque (nível 2) | Ameaça do ninho (rugido direcionado, 1× por confronto), depois postura de combate e ataques | O rugido de ameaça acontece só na primeira vez |
| Depois de um confronto | Inspeção do ninho, Alerta, Rugido territorial, Espreguiçar | 1 vez por confronto |
| Território calmo, com alguém observando de longe | Rugido territorial | No máximo 1 a cada 240 s, só perto de casa |
| Golpe recebido | `Dano_Leve`/`Dano_Forte` (`_Ar` no ar), por cima do estado, peso 0,45 a 1 | Intervalo de 0,7 s; nunca durante ataque próprio |
| Ambiente seguro | Descanso, sentado, sono, comer, beber, patrulha (rotinas existentes) | Rotinas sorteadas por peso |

## 5. Dragão Sombrio: requisitos para quando o modelo existir

1. **Esqueleto:** encaixar o mesmo esqueleto (100 ossos) na anatomia aprovada com `rig_<forma>.py`. O modelo fica em pose neutra.
2. **Personalidade:** `env_clipes_sombrio.sh` (proposta a validar):
   - postura baixa;
   - menos amplitude;
   - giros rápidos e curtos;
   - asas mais rentes no chão;
   - pouso silencioso (sem tranco).
3. **Clipes próprios a desenhar quando houver modelo** (comportamento de emboscada):
   - `Espreitar` (andar agachado);
   - `Bote_Emboscada`;
   - `Recuo_Sombra`.
   - Os poderes de Sombra dependem do kit oficial.
4. **Integração:**
   - prefixo `Sombrio_`;
   - pasta `Animacoes_Sombrio` + `Apelidos`;
   - perfil `MovimentoVivo.Perfis.Sombrio`;
   - `PastaAnimacoes = "Sombrio"` no modelo.

## 6. Validação feita (01/11)

- **Blender:** os 8 clipes novos foram gerados no Glacial e no CR sem estiramento anormal de patas (≤0,96). O Glacial foi regerado com a personalidade; as velocidades não mudaram.
- **Studio (Play):**
  - o Silverwing tocou Intimidação, Rugido territorial e Dano_Forte (Pontual com prioridade Action e peso 0,8);
  - no guardião selvagem, o jogador a 45 studs gerou `Alert` → `Intimidar` com `AlvoOlhar` replicado ao cliente e o olhar ativo no MovimentoVivo.
- **Glacial no Studio:** a pasta `Animacoes_Glacial` tem 48 clipes + Apelidos (todos os apelidos apontam para clipes que existem). O **modelo** ainda não está no Studio: falta a importação 3D manual de `dragao_gelo/final/GL_Dragao_Roblox.glb`.
