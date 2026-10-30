# Piloto Roblox: Lobo Ancestral (passo manual)

A integração com o Studio **não importa arquivos 3D locais**: as ferramentas disponíveis só inserem assets por ID ou enviam imagens. Por isso a importação do piloto é manual e **ainda não foi feita**.

## ATENÇÃO antes de importar (verificado em 27/10)
O Studio aberto nesta sessão carregou uma **versão antiga do place** (PlaceVersion 394). Ela **não tem** Costas Selvagens, Terras Corrompidas, as ilhas flutuantes, `Biblioteca_Criaturas`, `Laboratorio_Criaturas` nem `LOD_Distancia`. A causa provável é que o salvamento na nuvem falhou por tamanho (166 MB).

- **Não publique nem salve por cima** a partir desta sessão antes de decidir.
- A versão completa está em `Documents/RPG_Roblox/BACKUPS/RPG_BKP_2026-10-26_C1_criaturas.rbxl` (cópia conferida por hash).
- Para o teste do piloto basta um **place vazio local** (File → New → Baseplate), o que evita qualquer risco ao mapa.

## Passos
1. Abra um place de teste (Baseplate vazio ou a cópia local).
2. **File/Avatar → Import 3D** → `BLENDER/Criaturas/Blockouts/_Export/Lobo_Ancestral.glb`.
3. No importador:
   - Scale Unit = **Stud**;
   - Rig General: **não converter para R15** (Custom/Keep);
   - marque **Import Animations / Import only as Model**, se aparecer.
4. Clique em Import e me avise. Eu verifico pelo Studio:
   - altura até o ombro ~6,5 e altura total ~8,1;
   - frente em −Z;
   - SurfaceAppearance (cor + normal);
   - hierarquia dos Bones;
   - pesos (deformação com as poses);
   - reprodução das animações pelo AnimationController;
   - posição no chão;
   - FPS com 8 cópias.
5. **Publicar animações** (Animation Editor → Publish, ou Avatar → Animations) é manual e precisa da sua conta. Eu registro os IDs que você me passar.

## O que o GLB contém
- 1 esqueleto (32 ossos).
- 3 malhas:
  - corpo 14.000 tris;
  - garras;
  - olhos.
- Textura de cor 1024 + normal 1024 (JPEG embutido).
- 28 ações.
- Unidade: 1 = 1 stud.
