# Cérbero Sombrio — modelo para Meshy

Destino: chat Claude **Cérbero Sombrio** (Terras Corrompidas). A imagem gerada neste chat é uma proposta visual para o modelo adulto. Use-a como entrada em Image to 3D. Quando ela estiver em `DOCS/pedidos/2026-11-17-cerbero-sombrio-referencia.png`, use esse arquivo. Compare com o painel 04 de `RPG_Referencias_Visuais_GitHub/REFERENCES/03_CREATURES/04-bufalo-serpente-marinha-leviata-cerbero.png` se estiver disponível. Não localizei uma imagem própria do Cérbero em `REFERENCIAS/`.

## Prompt para Meshy

```text
One full-body dark fantasy cerberus for a Roblox RPG. One heavy muscular canine body, exactly four digitigrade legs, large paws and one tapered tail. Exactly three broad canine heads on three short readable necks rooted in one massive shoulder girdle, with a higher center head and two lower heads angled slightly outward. Broad angular skulls, compact canine muzzles, dark red eyes and closed mouths with clear jaw seams. Short charcoal-black fur in broad sculpted clumps, a few fitted corrupted stone plates on the shoulders and spine, restrained crimson fissures in the texture. Preserve silhouette, proportions and neutral stance from the input image. Clear gaps between heads and limbs for deformation. Single game asset, clean silhouette, no props, saddle, ground, smoke, flames or floating geometry.
```

## Aura permanente de chamas

O Cérbero deve ter uma aura visível de chamas enquanto estiver em cena, inclusive parado e entre habilidades. No modelo, deixe a silhueta e as articulações livres para receber a aura como efeito separado no Roblox. Use chamas discretas junto ao corpo e às três cabeças, com intensidade de repouso que preserve a leitura das habilidades. A imagem base continua adequada para gerar a malha limpa. Para os efeitos de cada habilidade, siga o §4h e o §5.9h de `REFERENCIAS_PODERES_E_EFEITOS.md` v6.2, detalhados no pedido de animações.

## Conferência no Blender

Comece por inspeção M0. Leia a ficha `DOCS/criaturas/cerbero-sombrio.md` e localize a V5 registrada (`Cerbero_Sombrio_refinado_v5.blend` / `Cerbero_Sombrio_final_v5.blend`). Preserve as versões anteriores. Se houver malha gerada, salve uma versão própria do Cérbero e confira frente, perfil e 3/4 lado a lado com a referência a cada revisão. Valide três mandíbulas separáveis, interior da boca viável, quatro apoios e espaço para os pescoços se moverem. Planeje escala adulta de 12–16 studs no ombro e área livre atrás dos pescoços para futura sela. Use fissuras em textura/material e priorize silhueta, UVs, deformação e custo de malhas/materiais para Roblox em PC e celular. Registre tris, materiais e adaptações da referência. Aceite: anatomia correta, silhueta legível e malha apta a receber o rig, com renders para revisão. A anatomia e os materiais são o escopo. A cor das fissuras é cosmética.

Preserve outras criaturas, arquivos compartilhados, código do jogo e ativos existentes. Uso de conta, créditos, upload e geração no Meshy ficam com o usuário ou dependem de autorização específica. Trabalhe no Blender em segundo plano. Studio fica fora deste pedido. Para uma etapa posterior autorizada, confira `DOCS/estado/studio-em-uso.md` e respeite um chat por vez. Relate conforme `CLAUDE.md`: tarefa, inspeção, alterações, testes/evidências, riscos/pendências, arquivos/estado e próximo passo aguardando aprovação.
