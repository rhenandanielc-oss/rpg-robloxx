# Contrato: golpes por porte, queda e finalização (19/11) [PROPOSTA]

O protótipo existe só no kit do Lobo Ancestral, no place isolado Testes-loboancestral. Nenhuma outra espécie usa este contrato ainda; cada uma adota no próprio chat.

**Regras oficiais usadas** (`REFERENCIAS_PODERES_E_EFEITOS.md` v6.2, §0b–0d):
- porte = ombro (ou comprimento ÷ 2,5) × tamanho da idade;
- classes: pequeno < 3, médio 3–8, grande 8–16, colossal ≥ 16;
- lentidão de no máximo 60%;
- pelo menos 4 s entre atordoamentos;
- colossal sofre metade da duração;
- Força resiste a derrubada.

Os demais números estão em `ConfigKitLobo.Controle` e são todos [A TESTAR].

## 1. Atributos que o ALVO expõe
| Atributo | Tipo | Uso |
|---|---|---|
| `Domesticavel` | bool | habilita a regra. Lobo do kit e `GuardiaoNinho` contam automaticamente. Fauna de recurso e humano nunca entram |
| `PorteOmbro` ou `PorteComprimento` | studs (adulto) | define a classe. Sem os dois, o porte é estimado pela caixa e o log registra isso |
| `Idade` | Filhote/Jovem/Pre-adulto/Adulto/Anciao | multiplica tamanho (40/65/85/100/110%) e Força (30/55/80/100/110%) |
| `Forca` | índice §0c | proporção atacante/alvo, limitada a 0,35–1,5 |
| `DonoUserId` | número (0 = selvagem) | define o desfecho e o PvP |
| `ImuneDerrubada` / `ImuneLentidao` | bool (opcional) | por exemplo, o Búfalo (imune a derrubada §0c) |
| `Vida` / `VidaMax` / `ReceberDano` | contrato r8 | já existente |

## 2. Estados temporários (o servidor grava; o cliente só mostra)
| Estado | Atributos | Efeito |
|---|---|---|
| Lentidão | `LentidaoControle` (0–0,6), `LentidaoAte` | passo mais curto |
| Claudicação | `Mancando = true`, `LentidaoControle`, `LentidaoAte` | lentidão maior; pata falha |
| Queda (Vida > 0) | `Caido = true`, `CaidoAte` (horário do servidor), `CaidoLado` = "E"/"D" (Lobo, 20/11 r3) | não anda, não ataca, não esquiva; levanta com transição visível. No Lobo: tomba de lado (barriga para o atacante; troca de lado com parede/sem chão) |
| Finalização em curso | `FinalizacaoDe` = nome do atacante | aviso visível; some ao concluir ou cancelar |
| Retirada (criatura de jogador) | `RetiradaDeCombate = true` + `Incapacitado = true` | sai da luta e vai ao refúgio, sem morte permanente |
| Morte (selvagem) | `Vida = 0`, `Estado = "Morto"`, `Incapacitado` | só depois de finalização válida |

**`Incapacitado` nunca marca uma queda recuperável.** Os sistemas atuais deixam de mirar quem está `Incapacitado`.

## 3. Quando o controle acontece
1. Só depois de um acerto válido com dano > 0 (sem esquiva e sem proteção). É uma rolagem por golpe, no servidor.
2. A chance multiplica estes fatores:

   | Fator | Valores |
   |---|---|
   | base do efeito | queda 16%, manca 14%, lento 30% |
   | impacto do golpe | Mordida 1,0, Garra 0,8, Salto 1,6, Investida 2,0 |
   | porte relativo | por classe de diferença: −3 → 0,05, −2 → 0,2, −1 → 0,55, 0 → 1, +1 → 1,3, +2 → 1,6, +3 → 1,8 |
   | Força relativa | atacante / alvo |

3. Restrições de golpe:
   - **Queda:** só com impacto ≥ 1,6 (Salto e Investida).
   - **Claudicação:** só com impacto ≥ 1,0.
4. Restrições de repetição e duração:
   - **Intervalo entre quedas:** ≥ 4 s **de pé**, contados a partir do fim do levantar (não do início da queda). Se a queda for negada, o efeito vira claudicação.
   - **Duração base da queda:** 3,0 s (era 2,4 s; 2,4 s não dava tempo para abordar, anunciar e morder).
   - **Duração por porte do alvo:** pequeno ×1,15, médio ×1, grande ×0,8, colossal ×0,5.
5. **PvP** (criatura de jogador atacada por criatura de **outro jogador**; o ataque de um selvagem é PvE e usa as durações normais):
   - duração × 0,5, caindo pela metade a cada repetição numa janela de 12 s;
   - depois de 2 controles seguidos, imunidade por duração + 8 s;
   - com PvP desligado ou alvo protegido (inclusive aliado), não há dano e portanto não há controle. O kit do Lobo passou a proteger a criatura de outro jogador quando `PvPAtivo` não está ligado.
   - **Achado:** a queda em PvP (1,5 s) é mais curta que anúncio + bote (cerca de 1,4–1,5 s). Na prática, a finalização em PvP só conclui se o lobo já estiver em posição. O número fica [A TESTAR].
6. **Log:** todo golpe registra a classe e a medida do atacante e do alvo, a idade, a Força, a diferença de classes, as três chances e o resultado ou o motivo da recusa.

## 4. Finalizar ou poupar (IA)
- **Só com o alvo enfraquecido:** Vida do alvo ≤ 35% (`vidaAlvoMax`). Acima disso a IA **aproveita** a queda com golpes normais, sem golpe final, e registra `APROVEITA`.
- **Uma decisão por queda.** O resultado é registrado (plano `Finalizar` ou `Vigiar`).
- **Poupar** acontece quando qualquer item abaixo vale:
  - lobo do dono (sem finalização automática);
  - alvo que não lutou com ele;
  - outro inimigo a menos de 25 studs;
  - própria Vida < 30% ou energia < 10;
  - alvo que já estava fugindo (plano `Recuar` ou `Desistir` antes de cair);
  - alvo a mais de 14 studs;
  - o lobo não chega antes de o alvo levantar;
  - sem linha de visão, alvo protegido ou fora da coleira.
- **Ao poupar:** rosna, mantém 8 studs de distância, não morde quem está no chão e retoma a luta quando o alvo levanta.
- **Ao finalizar:** aproxima-se (até 7,5 studs e 58° da frente) e anuncia (rosnado de 0,9 s, `EmAtaque = "Finalizacao"`, evento `Finalizacao`). As condições são conferidas a cada quadro e de novo no contato da mordida.
  - O cone vale 120°. Durante o anúncio e o bote há folga de +30° e +1 stud, para o corpo que está caindo não cancelar no mesmo quadro.
- **Cancela sem dano** se o alvo levantar, sair do alcance ou do cone, ficar protegido, perder a linha de visão ou for removido, ou se o lobo for derrubado, morrer ou for removido. O motivo é registrado.
- **Desfecho:**

  | Alvo | Resultado |
  |---|---|
  | selvagem | morte no protótipo, sem loot nem respawn |
  | criatura de jogador | retirada; o refúgio é simulado e a integração fica pendente |
  | humano | nunca |

## 5. Plano de adoção (cada chat implementa na própria espécie; nada foi feito fora do Lobo)
Classe por idade: Filhote / Jovem / Pré-adulto / Adulto / Ancião (medida efetiva em studs).

| Espécie | Chat | Medida adulto | Classes por idade | Força adulto | Observações para adoção |
|---|---|---|---|---|---|
| Lobo Ancestral | Floresta | ombro 6,2 | P 2,5 / M 4,0 / M 5,3 / M 6,2 / M 6,8 | 20 | **protótipo** (este kit) |
| Urso Silvestre | Floresta | ombro 9 | M / M / M / G 9,0 / G 9,9 | 65 | precisa de queda/levantar próprios (há Deitar/Dormir) |
| Lobo Ártico | Tundra | ombro 6,2 (confirmar) | igual ao Lobo | 20 (confirmar) | kit separado; usa Frostbite (lentidão já existe, somar no teto de 60%) |
| Leão Solar | Planícies | ombro 11,5 | M / M / G / G 11,5 / G 12,7 | 38 | clipes de dormir/impacto no Blender; Roblox pendente |
| Búfalo Colossal | Planícies | ombro 16 | M / G / G / C 16 / C 17,6 | 62 | `ImuneDerrubada` (§0c); lentidão com duração ×0,5 |
| Basilisco | Pântano | ombro 8,5 | M / M / M / G / G | 30 | modelo a confirmar |
| Crocodilo Primordial | Pântano | comp. 28 → 11,2 | M / M / G / G / G | 60 | agarrão PvP (Versão B) já prende; não somar agarrão e queda |
| Lagarto | Deserto | comp. 22 → 8,8 | M / M / M / G / G | 28 | — |
| Escorpião | Deserto | comp. 20 → 8,0 | M / M / M / G / G | 45 | — |
| Serpente Marinha | Costas | comp. 37,5 → 15 | M / G / G / G 15 / C 16,5 | 40 | na água, "queda" = atordoamento sem deitar (definir) |
| Leviatã | Costas | comp. 67,5 → 27 | G / C / C / C / C | 90 | quase sempre colossal: duração ×0,5 |
| Cérbero Sombrio | Corrompidas | ombro 14 | M / G / G / G / G 15,4 | 52 | 26 clipes; precisa de queda/levantar |
| Wyvern | Montanhas | ombro 11 | M / M / G / G / G | 55 | em voo: queda = perde altitude/pousa (definir) |
| Dragões (Montanhas, Glacial, Sombrio) | Montanhas / Tundra / Corrompidas | ombro 21 | G / G / C / C / C | 100 | já usam `Incapacitado` como estado final; manter, adicionar só `Caido` temporário |

**Passos de adoção por espécie:**
1. Expor os atributos da seção 1.
2. Tratar `Caido` e `LentidaoControle` na própria locomoção e IA.
3. Ter clipes de queda, deitado e levantar (ou equivalente em voo ou na água).
4. Testar com o Lobo como atacante (portes P/M/G/C).
5. Ligar a retirada ao refúgio real só quando o sistema de refúgio existir.

## 6. Hitbox de contato e finalização por espécie (20/11)
- **Corpo para golpes:** o alvo é medido pelas cápsulas nos ossos (sem cauda/pelos), não pela caixa da malha. Cada espécie pode publicar a sua lista de cápsulas; sem lista, usa osso → pai com raio genérico.
- **Ponto de ataque:** o golpe conta do ponto que bate (boca, pata, cauda, chifre...). Acerta só com contato real, com o limite em config.
- **Finalização:** cada espécie define o seu `estilo` com anúncio, contato, ação de controle e desfecho, sempre interrompível e sem dano atrasado.

| Espécie | Finalização proposta |
|---|---|
| Lobo | **implementada no protótipo (r2, 20/11):** ir ao meio do corpo, morder o flanco/barriga e sacudir a própria cabeça; o alvo não é movido (a v81, com pescoço/puxar/estrangular, foi recusada) |
| Urso | prender com as patas e morder |
| Leão | mordida na garganta segurando |
| Crocodilo | agarrão com giro mortal (já tem agarrão PvP Versão B) |
| Serpente / Leviatã | constrição |
| Dragões | pisar e prender + sopro |
| Demais | definir no chat de cada uma |

Só a do Lobo existe; as demais são propostas para os chats de cada espécie.
- 20/11: alvo já enfraquecido (Vida ≤ 35%) leva +2,5 s para levantar [A TESTAR], para a finalização pelo flanco caber na janela.
- 20/11 r3: no Lobo a queda é lateral (clipes próprios QuedaLado/CaidoLado/LevantarLado E/D) e a mordida usa a barriga do lado das patas (`CaidoLado`). Cada espécie que adotar a finalização pela barriga precisa de pose caída que exponha a barriga.
