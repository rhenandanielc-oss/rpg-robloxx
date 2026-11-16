# Fauna da Floresta Ancestral no Studio (16/11/2026)

Piloto de importação de Cervo (rig r2), Javali (rig r4) e Coruja (rig r4) no **rpg_roblox**, autorizado pelo usuário ("Sim, reimportar rigs"; "Use no rpg_roblox, depois excluimos as partes indesejadas").

## Arquivos
- `exportar_studio_fauna.py`: gera o GLB de importação de cada animal.
  - Comando: `blender -b <rig.blend> -P studio/exportar_studio_fauna.py -- <Animal>`.
  - Saída: `export/<Animal>_Studio.glb` + `_info.json`.
  - O osso `Raiz` não tinha peso, e o Import 3D descarta ossos sem peso. Por isso o GLB leva 1 triângulo degenerado no Corpo com peso 1 em `Raiz`, mesmo método do Lobo Ancestral.
  - Malha, pesos, UV e texturas não mudaram; o .blend de origem não é salvo.
- `empacotar_fauna.py`: gera `dados/<Animal>/<Clipe>.txt`, `inventario.json` e `fauna_dados.project.json`.
  - Formato do lobo.
  - Depois do script, rodar `rojo build studio/fauna_dados.project.json -o studio/FaunaFloresta.rbxm`.
- `AdaptadorFauna.luau`: cópia do AdaptadorLobo, com uma fábrica por animal.
  - Uso: `require(FaunaFloresta.AdaptadorFauna).para("Cervo")`.
  - `aplicarQuadro` (prévia em Edit) multiplica a translação pela escala do modelo; em Play o Animator já faz isso.

## Clipes empacotados (bases aprovadas)
| Animal | Clipes | Fontes |
|---|---|---|
| Cervo | 31 | `rig/clipes_r2` |
| Javali | 24 | `rig/clipes_LA`, `LB`, `LC`, `LD_r2` |
| Coruja | 32 | `rig/clipes_LA_r2`, `LB`, `LC_r2`, `LD`. Lotes A e B foram feitos no rig r3, sem pálpebras: nesses clipes elas ficam abertas. |

## No rpg_roblox
- `ReplicatedStorage.FaunaFloresta`: AdaptadorFauna + `<Animal>.Dados`.
- `Workspace.Teste_FaunaFloresta`, em (0, 2600, 300):
  - `Chao`;
  - `Cervo_Teste`, `Javali_Teste` e `Coruja_Teste`, ancorados, com escala **×3 [PROPOSTA]** (1 m do Blender = 3 studs; porte oficial PENDENTE), gravada no atributo `EscalaProposta`;
  - `TesteFauna_Servidor`, **desativado**, que monta e mede os clipes em Play.
- Apagados a pedido do usuário: os lows sem esqueleto (3 modelos `Scene`) e `CR_Cervo_meshy`. O `Scene` do Javali-do-Brejo ficou intacto.

## Testes (16/11)
- Convenção do Import 3D novo confirmada (osso = Blender girado 180° em Y).
- Em Edit, quadro 6 da Corrida (cervo, javali) e do BaterAsas (coruja), comparando com as posições dos ossos no Blender:
  - convenção nova com a translação ×3: erro máximo de 0,004 a 0,005 stud;
  - convenção antiga: erro de 1,2 a 4,3 studs.
- Em Play, no servidor, com `RegisterAnimationClip`:
  - todos os clipes carregaram (31/31, 24/24 e 32/32);
  - pose congelada no q6 com erro de 0,0035 a 0,0049 stud, com o Animator escalando a translação sozinho.
- Captura em Edit: as poses aparecem certas.
- **Cervo cinza (resolvido 16/11):** os assets de imagem do primeiro upload não carregavam, e reimportar o mesmo GLB reaproveitou os mesmos ids (o Roblox deduplica pelo conteúdo). O GLB foi regerado com `FAUNA_NOVO_HASH=1` (1 pixel do canto ±1/255 em cor e normal, só em memória; PNGs aprovados com md5 igual). Reimportado: ids novos, textura visível. Clipes conferidos de novo no modelo novo (Corrida q6: 0,0045 stud; 31 clipes sem osso faltando).
- Não houve vídeo em Play: com o streaming, o cliente não carrega a área a y=2600.

## Limites
- KeyframeSequence só toca no Studio. No jogo publicado, os clipes precisam ser publicados como Animation.
- Sem IA nem comportamento: as regras da fauna (porte, alerta, fuga, coleta) seguem PENDENTES em `DOCS/fauna/floresta-ancestral.md`.
- O place não foi salvo pela integração.
