---
name: pipeline-criatura
description: Pipeline de criaturas deste RPG Roblox - modelo de conceito no Blender (pose neutra), malha de jogo LOW com UV e mapas assados, texturização opcional no Meshy (API do usuário), rig, clipes por script e ponte JSON para KeyframeSequences no Studio. Use ao criar, refinar, texturizar, animar ou importar dragões e outras criaturas.
---

# Pipeline de criaturas (Blender 5.2 → Roblox)

Blender: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`, sempre headless (`-b ... -P script.py -- args`). Tudo é script reproduzível; nada de edição manual sem script.

## 1. Conceito (HIGH)
- Siga a skill `blender-image-to-3d`: referência em `<criatura>/ref/`, `asset-brief.md`, renders comparativos a cada rodada.
- Exemplo vivo: `BLENDER/Criaturas/Teste_IA/dragao_novo/criar_dragao_ref.py` (grafo Skin → remesh voxel → escultura do rosto; peças rígidas encaixadas na pele por `ray_cast`).
- POSE NEUTRA (em pé, asas abertas, patas retas). Mudar visual sem mover articulações (escala da cabeça sobre a junta do pescoço, só raios/cores) para não afetar animações.
- Revisão: `render_cabeca.py` (close-ups) + prancha com a referência lado a lado. Mostrar ao usuário etapa por etapa.

## 2. Malha de jogo (LOW)
- `dragao_novo/low_dragao.py`: corpo reduzido (≤ ~12k tris), membranas sem espessura (DoubleSided no Roblox), peças rígidas reduzidas, tudo unido, UV única, bake Cycles HIGH→LOW de cor/normal/rugosidade (2048), GLB.
- Limite: ≤ 20k tris por MeshPart. Quadriflow recusa a malha do voxel; o fallback é Decimate (rever topologia de articulação no rig).

## 3. Texturização Meshy (opcional, gasta créditos do usuário)
- Chave SOMENTE na variável de ambiente de usuário `MESHY_API_KEY` (configurada pelo usuário). Ler com `[Environment]::GetEnvironmentVariable("MESHY_API_KEY","User")`. Nunca imprimir, gravar em arquivo ou usar chave colada no chat.
- Pedir OK com custo estimado antes de CADA geração. Usar a LOW com UV original para que as texturas sirvam no jogo.
- Auto-rig/animações do Meshy não servem para criaturas aladas (só humanoide/quadrúpede cão).

## 4. Rig e clipes
- Rig próprio no Blender (coluna, pescoço, cauda, mandíbula, 4 patas, asas com úmero/antebraço/4 dedos + polegar).
- Clipes gerados por script (referência: `meshy/anim_silverwing.py`), cadeia de QA (`corrigir_penetracao` → `corrigir_cruzamentos` → `qa_silverwing` → `mapa_intersecoes`).
- Velocidade de locomoção medida nos pés (pé apoiado não escorrega) — ver `meshy/video_demo.py` (`vel_passada`).

## 5. Studio
- Importar GLB (Import 3D) → script de troca que preserva posição/atributos e guarda a versão anterior em `ServerStorage.Dragoes_Retirados`.
- Clipes: `exportar_clipes_json.py` → JSON servido em `http://127.0.0.1:8766` → `montar_kfs_json.luau` (`montar("Silverwing_" .. nome)`).
- KeyframeSequence só toca no Studio; para o jogo publicado o usuário precisa publicar os clipes como Animation.

Não mexer em outras criaturas, mapa ou biomas sem pedido. Binários (.blend/.glb/.png de revisão) ficam fora do git.
