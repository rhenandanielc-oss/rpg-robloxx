# BIOMES ART BIBLE — Mundo de fantasia realista

> **Status:** direção de arte e requisitos de construção propostos para uso na implementação; descrição técnica detalhada e escala definitiva dependem de inspeção M0 e da documentação oficial. **Não autoriza modificar o Studio.**

## 1. Identidade global
- Fantasia realista, visual cinematográfico e natural; ecossistemas coerentes e transições graduais entre regiões.
- Natureza dominante; vilas, comércio, guardas, ruínas, pontes e acampamentos pontuais.
- Diferenciar regiões por geologia, espécies vegetais, clima, iluminação, erosão, água, fauna e materiais.
- Evitar árvores clonadas em grade, montanhas triangulares artificiais, cores neon generalizadas, vazios imensos sem propósito e árvores sobre estradas.
- Prever vias de transporte, áreas seguras, rotas alternativas, clareiras adequadas a combate e locais exploráveis.

## 2. Vegetação e vento — requisito visual explícito
- Folhas, copas, ramos finos, gramíneas e arbustos devem reagir ao vento de forma **sutil e variada**, não em sincronia robótica.
- Preferir animação por shader/material/estratégia técnica suportada e aprovada ou animação seletiva de malhas/ossos somente onde justificado; **não presumir recursos não existentes em Roblox**.
- Troncos principais quase rígidos; extremidades das copas oscilam; rajadas ocasionais podem intensificar movimento.
- Direção e força do vento coerentes dentro da zona e com vegetação: planícies ondulantes, litoral exposto, tundra e montanhas com vento mais forte, pântanos mais discretos.
- Não animar milhares de folhas como objetos físicos independentes. Usar variantes visuais, instanciamento racional, distância/culling, animação de proximidade, LOD onde viável, StreamingEnabled e perfil de desempenho mensurado.
- Se uma solução realista não for viável no motor ou dispositivos-alvo, apresentar opção técnica de menor custo **antes** de executar.

## 3. Terreno, hidrologia e iluminação
- Macrorelevo primeiro: cordilheiras, vales, planícies, encostas, fozes, litoral; microdetalhes depois.
- Rios descem com declividade plausível em direção a lagos/oceano; evitar lagos flutuantes e cursos interrompidos sem explicação.
- Usar água coerente com o motor Roblox e com custo de renderização; alternativas para espuma, reflexos e ondas devem ser testadas em dispositivos móveis.
- Iluminação unificada, com atmosferas por bioma: névoa leve em mata, névoa pesada no pântano, ar seco no deserto, frio na tundra, energia localizada nas terras corrompidas.
- Evitar animações ambientais pesadas, excesso de luzes dinâmicas, partículas permanentes e colisão detalhada desnecessária.

## 4. Oito biomas

### Floresta Ancestral
**Visual:** floresta úmida, antiga, vegetação alta, copas densas, sombra com feixes solares e trilhas orgânicas. **Relevo:** colinas suaves, rios e clareiras. **Vegetação:** Freixo Antigo, Carvalho-do-Bosque, musgos, raízes, samambaias, arbustos e vento visível nas folhas. **POIs:** vila, lenhadores, guardiões, clareira, ruínas e entradas ocultas. **Gameplay:** rastros de fauna, madeira marcada, caminhos furtivos; NPC Maera e campanha Rastros na Mata.

### Montanhas Altas
**Visual:** rocha maciça, cristas, pinheiros, penhascos, vales e nuvens baixas. **Relevo:** verticalidade, passagens montanhosas e mineração subterrânea. **Vegetação:** Pinheiro Serrano e Teixo-da-Montanha nas cotas apropriadas. **Água:** nascentes, riachos e cachoeiras. **POIs:** vila mineradora, mina interditada, postos e cavernas. **Gameplay:** desmoronamentos, rotas alternativas, Torven e As Minas Silenciosas.

### Pântano Nebuloso
**Visual:** águas escuras e lentas, árvores tortas, raízes aéreas, névoa. **Relevo:** ilhas baixas, solo lamacento, canais, passarelas quebradas. **Vegetação:** Mangue Cinzento, Salgueiro-do-Brejo, juncos. **POIs:** palafitas, cabanas de curandeiros, ruínas alagadas. **Gameplay:** água profunda, baixa visibilidade, amostras contaminadas, Neris e Águas Alteradas.

### Planícies Douradas
**Visual:** campos extensos dourado-esverdeados sob céu amplo, bosques esparsos e rotas comerciais. **Relevo:** colinas baixas, horizontes largos, rios moderados. **Vegetação:** Acácia Dourada, Olmo-das-Planícies e capim balançando ao vento. **POIs:** caravanas, mercados, fazendas, postos de estrada e depósitos. **Gameplay:** navegação, planejamento de rotas e logística, Alina e A Rota Interrompida.

### Tundra Congelada
**Visual:** gelo, neve, ventos frios, ruínas cobertas, luz azul-acinzentada. **Relevo:** fendas, lagos congelados, encostas e passagens sob gelo. **Vegetação:** Pinheiro Boreal e Bétula Branca nas áreas plausíveis. **POIs:** santuário, abrigo, ruínas recém-expostas. **Gameplay:** nevasca, visibilidade limitada, gelo frágil, Edria e Sob o Gelo.

### Deserto de Cristal
**Visual:** dunas, cânions erodidos, afloramentos cristalinos discretos e oásis. **Relevo:** depressões, fendas, cavernas sob dunas. **Vegetação:** Acácia Desértica, Tamareira Cristalina e arbustos resistentes. **POIs:** oásis, lapidação, minas e instalação clandestina. **Gameplay:** calor, areia, cristais instáveis, Sahir e A Ressonância.

### Costas Selvagens
**Visual:** falésias, praias rochosas, mar, enseadas, farol e neblina oceânica. **Relevo:** litoral recortado, cavernas sujeitas a marés e rios desembocando no oceano. **Vegetação:** Coqueiro Selvagem, Cedro Costeiro e vegetação deformada pelo vento. **POIs:** vila de pescadores, porto, farol, recife e enseadas. **Gameplay:** correntes, marés, resgates, Cora e Sinais na Maré.

### Terras Corrompidas
**Visual:** solo rachado, vegetação enferma, ruínas desertas, névoa densa e magia corrompida localizada. **Relevo:** fendas, campos instáveis, ravinas e trilhas de refugiados. **Vegetação:** Teixo Cinzento, Árvore-de-Casca-Negra, espinhos e árvores parcialmente mortas. **POIs:** abrigos, postos abandonados, instalações clandestinas. **Gameplay:** resgates, ambientes contaminados, Rovan e A Origem da Ruptura. **Narrativa:** não revelar benevolência original da entidade.

## 5. Ordem segura de construção
0. INSPEÇÃO do mapa existente, referências, terrain, água, iluminação, plugins, restrições e FPS (somente leitura).
1. Croqui topográfico e limites de biomas; checar escala de navegação e conectividade. Aprovação.
2. Macroterreno e transições; aprovação e teste.
3. Hidrologia e costa; aprovação e teste.
4. Vegetação estrutural regional; aprovação e teste de FPS.
5. Vento/iluminação/clima, sem efeitos custosos disseminados; aprovação e teste.
6. Vilas, trilhas, POIs, entradas físicas das dungeons; aprovação e teste.
7. Fauna/spawns/coleta/rotas PvE e PvP; aprovação e teste.
8. Otimização/colisões/dispositivos móveis; revisão integrada.

## 6. Definição de pronto
Cada lote deve conter: antes/depois, objetos criados/removidos, localização, screenshots ou inspeção visual, erros no Output, estimativa de custo e teste de navegação. **Não considerar um bioma pronto só porque existe terreno básico com grama.**
