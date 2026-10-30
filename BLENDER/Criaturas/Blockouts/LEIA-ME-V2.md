# Operação Criaturas V2 (27/10/2026): resultados verificados

**Resumo honesto:** a V2 melhorou textura, pesos, contato com o chão e as cabeças das espécies mais fracas, e agora há uma auditoria medida de todas as animações. **Ainda não atinge o critério "não parecer manequim"**: as formas continuam lisas e arredondadas, porque foram modeladas por primitivas e não esculpidas. **Nada foi testado no Roblox**; ver o impedimento abaixo.

## Fase 0: compatibilidade com o Roblox
- **Impedimento 1:** as ferramentas da integração com o Studio só inserem assets por ID e enviam imagens; **não importam GLB/FBX locais**. A importação é manual: Import 3D, passos em `PILOTO-ROBLOX-LOBO.md`.
- **Impedimento 2, risco de dados:** o Studio desta sessão abriu uma **versão antiga do place** (PlaceVersion 394). Faltam Costas Selvagens, Terras Corrompidas, as ilhas flutuantes, `Biblioteca_Criaturas`, `Laboratorio_Criaturas` e `LOD_Distancia`. A causa provável é a falha de salvamento na nuvem por tamanho.
  - Não alterei nada nessa sessão.
  - A versão completa está em `Documents/RPG_Roblox/BACKUPS/RPG_BKP_2026-10-26_C1_criaturas.rbxl`.
- **Não executados:** Fase 6 (testes no Studio) e publicação de animações. Não há IDs de animação.

## Fase 1: anatomia (alterações reais)
- **Basilisco e Lagarto:** a cabeça canina virou crânio reptiliano baixo e largo, com focinho longo e chato, mandíbula plana e musculatura da mandíbula. Os membros ficaram mais finos e semi-eretos (úmero lateral). Nos cristais do Lagarto, a base mineralizada nasce da pele, os prismas saem de dentro dela e os aglomerados são maiores.
- **Cérbero:**
  - raiz única e maciça dos três pescoços;
  - cabeças escalonadas: a central mais alta e dominante, a esquerda mais baixa, a direita baixa e em ataque;
  - crânios largos de predador, maxilar e rugas do focinho.
- **Wyvern:** peito em quilha com músculos de voo, ombros das asas, coxas mais fortes, pescoço mais grosso, arcadas na cabeça.
- **Leão:** testei mechas geométricas na juba e **reprovei** (ficou "espinhosa"). A juba voltou à massa lisa, e o detalhe de pelo ficou só na textura. **A juba continua lisa demais** (pendência).
- **Demais espécies:** sem mudança de forma nesta etapa (mantêm o refinamento de 26/10).

## Fase 2: texturas e materiais
- Corpo de cada criatura com UV, **cor 1024 + normal map 1024 assados**:
  - pelo com fibra fina;
  - escamas em células de Voronoi com sulcos;
  - quitina mais lisa e brilhante.
- Membranas com textura de couro (512).
- Os materiais finais são simples (imagem de cor + normal + rugosidade constante): é o que o Import 3D converte em SurfaceAppearance. Não dependem de nós do Blender.
- Garras, chifres e dentes mantêm materiais próprios por cor e rugosidade.
- Olhos com cor por espécie (âmbar; azul no Lobo Ártico e no Glacial) e brilho, **sem emissão**.
- Textura embutida no GLB como JPEG, 1,5–3,2 MB por criatura.
- **Sem língua nem cavidade bucal.**

## Fase 3: rig e pesos
- **Pesos por regiões:** cada membro, cauda e cabeça só recebe os próprios ossos e o tronco. As fronteiras são suavizadas pela malha, a linha média da barriga pertence ao tronco, e a cauda não puxa as coxas.
- **Corrigido:** nos voadores, os dedos das asas fundidos ao corpo estavam presos à coxa. Foi a causa de quase todo o "Refazer" da primeira rodada (140 → 4).
- Nomes de ossos mantidos (compatíveis com as animações).

## Fase 4: animações (auditoria medida)
- **507 ações.**
  - Entraram AbrirAsas e RecolherAsas nos voadores, e AtaqueSubaquatico e Desacelerar nos aquáticos.
  - Os passos foram reduzidos, as poses deitadas ficaram mais leves, e a altura agora é corrigida pelos pés: em locomoção os pés ficam no chão, e nas demais ações os pés não afundam.
- **Classificação automática** (`AUDITORIA-ANIMACOES-V2.csv`): esticamento das arestas do corpo em 3 quadros (p99 e % de arestas >1,8×) mais erro de contato com o chão.
  - **Aprovada: 224 · Pequenos ajustes: 246 · Refazer: 37 · Incompatível: 0.**
  - Os "Refazer" concentram-se em Deitar/Descanso/Levantar, GuardarNinho, Empoleirar e saltos. São as poses de dobra extrema dos membros sobre um tronco fundido.
- **A métrica mede deformação, não beleza.** As animações continuam procedurais e não substituem animação à mão.

## Fase 5: custo e otimização (por criatura, medido)
- Tris totais: 16,8 mil (Lobo) a 38 mil (Dragão Sombrio, por causa da fileira dupla de espinhos).
- Ossos: 22–48. Materiais: 3–6. Texturas: 2 × 1024 no corpo (+512 por membrana).
- GLB: 1,5–3,2 MB. Tudo em `review/<Especie>/final.json` e `review/v2_resumo.txt`.
- **Hitboxes** simplificadas (cápsula por osso principal) em `final.json` → `hitboxes`, para colisão e dano futuros.
- **LOD:** o Roblox gera LODs automaticamente para MeshPart (RenderFidelity = Automatic). Não exportei cadeias de LOD manuais.
- **Custo de várias criaturas simultâneas: não medido.** Exige o Studio.

## Pendências
1. Importação e testes no Roblox, depois de decidir qual versão do place usar.
2. Forma ainda "lisa":
   - o próximo salto de qualidade exige escultura (multires e detalhe esculpido);
   - ou fur cards para juba e pelagem.
3. Animações: ~37 para refazer e 246 com ajustes. Melhor caminho: IK de pés e retoque manual das poses de deitar.
4. Leão: a juba precisa de cards de pelo ou escultura.
5. O close da cabeça nas folhas enquadra mal algumas espécies (mostra o pescoço).

## Arquivos
- `<Especie>/<Especie>_final.blend` (V2) e `_Export/<Especie>.glb` (V2, validados por reimportação: 1 esqueleto, ações conferidas, 2+ imagens).
- `AUDITORIA-ANIMACOES-V2.csv`.
- `review/V2_A.png`, `V2_B.png` (frente, lateral, 3/4, cabeça, pose) e `V2_antes_depois.png`.
- Cópias em `SCREENSHOTS/Criaturas_V2_2026_10_27/`.
- Os blockouts e a biblioteca V1 estão preservados.
