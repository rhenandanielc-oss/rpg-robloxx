# MASTER-PROMPT — RPG Roblox fantasia realista

## Objetivo
Desenvolver um RPG de mundo aberto no Roblox, com combate em tempo real de personagem humano e criatura, exploração livre, história central, criação de equipamentos, PvE, PvP, cooperação e monetização controlada. O projeto do jogo Roblox é separado de Dragon Ranch.

## Escopo de lançamento OFICIAL
- Continente de 8 biomas conectados, acessíveis em ordens diferentes; hub inicial seguro.
- Todos os animais/espécies e formas previamente aprovados no documento de criaturas (reconciliar lista antes de criar modelos).
- 8 campanhas regionais completas, 6 missões por bioma = 48 missões principais, e campanha central completa.
- 15 conjuntos de armaduras (5 em cada estilo) e variantes regionais básicas; receitas individuais precisam de auditoria.
- Dungeons 1–4 jogadores, chefes necessários à campanha e aos equipamentos Lendários; chefes opcionais podem chegar em atualizações.
- Dez produtos de loja previstos na abertura, sujeitos à validação das políticas de Roblox, experiências de compra e balanceamento.

## Estética e mundo
**Fantasia realista:** natureza predominante; civilização pontual; geografia coerente; árvores de espécies regionais, copas e folhas com vento suave, grama/arbustos dinâmicos; rios coerentes, mar, montanhas, áreas úmidas, gelo, areia e corrupção localizada. Biomas detalhados em `SPECIFICATIONS/BIOMES-ART-BIBLE.md`.
A extensão citada no planejamento é aproximadamente 6144×6144 studs; **confirmar no documento e no Studio antes de impor dimensões**. Escala e geometria não são autorização para gerar o mapa.

## Combate e criaturas
Combate misto em tempo real (humano + criatura), habilidades, elementos, movimentação e progressão. Referência de criaturas: documento `RPG_02_Criaturas_Elementos_e_Poderes.docx`; resumos não substituem os dados detalhados oficiais. Dano, duração e outros números não aprovados = parâmetros ajustáveis.

## Missões e segredo narrativo
O jogador chega como aventureiro; a Guilda do Horizonte é respeitada publicamente mas conduz experimentos ilegais. Uma entidade ancestral é corrompida pelos experimentos; **o jogador não pode descobrir previamente que ela era originalmente benevolente**. Oito pistas são necessárias para desbloquear conclusão; a dungeon final tem batalha contra a organização, pausa de recuperação, depois batalha contra entidade. Só após derrotá-la, ela conta a verdade. Progressão individual, possibilidade de cooperação e missões repetíveis limitadas.

## Equipamentos e economia
Três estilos livres, cinco raridades e 15 conjuntos base; cinco peças por conjunto. Conjuntos Raros estimados 4–7h, Lendários 15–25h (metas de design a validar). Melhoria até +10; conjunto Lendário com bônus principal de até 15%, limites por atributo; recursos especiais e oito biomas + chefe para projeto Lendário. Mercado entre jogadores com preços livres, histórico e taxa de 3%. Revisar receitas e economia antes de publicar.

## Dungeons
Grupo 1 a 4. Até 3 ressurreições TOTAIS por jogador por dungeon, sendo padrão 1, possibilidade de +1 por missão e terceira por passe Robux; **não ressuscitar aliados**. Derrota de todo grupo encerra a tentativa e retorna à entrada no mundo. Reconexão à tentativa ainda ativa não restaura ressurreições. Item especial de chefe Lendário: garantia até quinta vitória válida por jogador/chefe, com participação real e persistência.

## Loja
Preços de referência: títulos 99, skin individual 159, inventário 159, pacote skins 399, cosmético evento 179, aparência criatura 459, evolução Serpente Abissal 999, terceira ressurreição PvE 299, ovo premium 499, VIP 399 Robux. Confirmar todos antes de configurar produtos Roblox. Loja vende acessos e cosméticos sem vantagem automática PvP.
Ovo premium: Serpente das Profundezas 10%, Águia Celeste 30%, Cervo Prismático 60% no primeiro ovo; três primeiros ovos sem duplicação, chances condicionais recalculadas e reveladas, após terceiro não se compra mais. Evolução premium para Serpente Abissal tem QUATRO poderes finais: Travessia Abissal, Erupção Sombria, Espiral de Pressão, Eclipse Telúrico (substitui Ruptura do Subsolo pela última decisão oficial).

## Regras de execução
- M0 inspeção leitura apenas primeiro.
- Seguir módulos e testes em `TASKS.md` / `ACCEPTANCE-TESTS.md`.
- Dados e integrações antes de conteúdo, aprovação por partes.
- Separar: OFICIAL, PROPOSTA, PENDENTE, VERIFICADO NO STUDIO.
- Sem programação nem mudanças no Studio até pedido e autorização específicos.
