# Biblioteca 3D da Floresta Ancestral — catálogo (2026-10-21)

Pasta: `BLENDER/Biblioteca/<Família>/` (um `.blend` por família + um `.glb` por modelo; texturas em `Biblioteca/Texturas/`). Árvores ficam em `BLENDER/` (`ArvoreAncestral_*`). Escala 1 unidade = 1 stud, pivô na base, colisores simples como peças `Colisor_*` (importar com Transparency 1, CanCollide true, CanQuery false; peças visuais CanCollide false). **Nenhum modelo da biblioteca nova foi importado ou validado no Roblox: estado = "modelado e exportado".**

## Situação por família
| Família | Modelos / variantes | Tris visuais (LOD único salvo árvores) | Roblox |
|---|---|---|---|
| Árvores comuns V4 / V5W | LOD0/1/2 | V4 10.312/2.456/956; V5W 12.138/3.642/1.386 | V5W LOD0 importada pelo usuário; copa não confirmada |
| Árvore Ancestral (hero) | LOD0/1/2 + colisores | 56.942 / 11.836 / 1.756 | LOD0 importada e renderiza (corrigida: AlphaMode, colisores, cores) |
| A4 Vegetação pequena (`A4_Vegetacao_Pequena`) | Samambaia A/B/C, Arbusto A/B, Grama A/B, Pedras (2 pequenas, média, 2 grandes), Tronco_Caido A/B/C, Toco A/B, Raiz_Arco A/B, Cipo A/B, Cogumelos A/B (23) | 28–648 | não importado |
| B Vila e estruturas (`B_Vila_Estruturas`) | Casa_Cabana A/B, Casa_Grande_A, Casa_Estacas_A, Oficina_A, Banca_Mercado_A, Passarela_Modulo_12, Escada_Madeira_8, Mirante_A, Placa_Direcional_A, Poste_Lanterna_A (11) | 48–3.372 | não importado |
| C Ruínas/santuários/acampamento (`C_Ruinas_Santuarios_Acampamento`) | Muro_Ruina A/B/C, Coluna (inteira, 2 quebradas), Arco_Ruina A/B, Altar_Antigo_A, Monolito A/B, Santuario_Menor_A, Tenda A/B, Fogueira_A, Mesa_Mapa_A (16) | 108–1.032 | não importado |
| D Cavernas/habitats (`D_Cavernas_Habitats`) | Caverna_Entrada A/B, Toca_Lobo A/B, Ninho_Elevado A/B, Abrigo_Rocha_A (7) | 880–3.996 | não importado |
| E Objetos (`E_Objetos_Decoracao`) | Barril A/B, Caixa A/B/Grande, Cesta, Banco_Tora A/B, Pilha_Lenha, Lanterna_Mao, Tocha_Parede, Machado_Tora, Corda_Rolo (13) | 24–1.200 | não importado |

| **B2 Vila refinada** (`B2_Vila_Refinada`, estilo `Misty Forest Tree Village`: madeira escura envelhecida, amarrações de corda, lona caída, lanternas) | Casa_Lona A/B (≈7,4 mil tris), Banca_Lona A/B, Fogueira_Panela_A (tripé, panela, toras), Cerca_Modulo A/B, Poste_Lanterna_B, Pilha_Caixas_A, Passarela_Corda_12, Grama_Larga A/B (12) | 54–7.448 | não importado |

Total: 70 modelos novos (+12 refinados em B2) em 5 famílias, 75 `.glb` e 5 `.blend`. Capturas: `SCREENSHOTS/175`–`180`.

## Limites e pendências (honestos)
- **Qualidade:** arquitetura e ruínas são construídas de caixas/vigas com variação, texturas procedurais e musgo; melhor que blocos simples, mas ainda geométricas de perto. Ruínas, caverna e rochas usam o mesmo material de pedra.
- **Defeitos conhecidos:** samambaias parecem folhas largas (as folíolos pouco visíveis); pilha de lenha e troncos com extremidades abertas; janelas das casas mostram interior escuro simples; textura de casca/madeira usa UV 0–1 esticado; Lanterna_Mao e Tocha com luz como material emissivo (sem PointLight no glTF).
- **Tamanho dos arquivos:** cada `.glb` embute texturas (≈0,6–5 MB); a pasta soma ≈135 MB. Convém consolidar em atlas antes de uso em massa.
- **Não feitos:** variantes de LOD dos modelos acima, vila completa montada (praça, casas múltiplas, pontes de corda), pontes de corda como modelo, árvores gigantes antigas intermediárias, importação e validação no Roblox, FPS/memória, integração no mapa.
- **Regras mantidas:** mapa principal e estruturas existentes (≈2.400 Parts da vila etc.) não foram alterados ou substituídos; sem mudança em gameplay/DataStore.

## Refinamento B2 (referência da vila)
Atlas novo `Madeira_V2` (tábuas escuras e envelhecidas, topo de tora, corda), `Lona_V2`, `Grama_V2` (lâminas largas). Defeitos conhecidos: escada da casa fica afastada da varanda; pontas de tora e cordas em tom claro demais; grama lê pálida no preview; sem tronco com cipó espiralado nem árvores com galhos grossos como na referência (a Árvore Ancestral não foi refeita). Capturas 181–183. Ainda não importado no Roblox.

## Refinamento no estilo da referência — A5, ruínas, Árvore Ancestral, correções B2 (2026-10-21)
- **A5 Vegetação refinada** (`A5_Vegetacao_Refinada`, 9 `.glb`): Samambaia_R A/B/C, Arbusto_Largo A/B, Planta_Larga A/B, Cipo_Largo A/B; 112–196 tris cada; folhagem larga estilo bordo e lâminas largas. Samambaias ainda parecem lâminas e as folhas largas são pequenas — sem validação no Roblox.
- **Ruínas (família C re-exportada, 16 modelos):** pedra nova `PedraMuro_V2` + hera (tubos `*_Hera`) e folhas largas (`*_HeraFolhas`) em altar, arcos, colunas, fogueira, monolitos, muros e santuário (ex.: Muro_Ruina_C 1.476 tris, Santuario_Menor_A 1.472).
- **Árvore Ancestral:** adicionado cipó espiralado (`Cipo_Espiral_LOD0` 2.240 tris, `LOD1` 600; ≈3,4 voltas no tronco, material `CipoEspiral_Hero`) e reexportados `ArvoreAncestral_Principal_LOD0/1/2` (`.glb` + `.fbx`, ≈8,1 / 6,2 / 5,5 MB). LOD2 sem cipó (propositalmente). Não foram feitas folhas mais largas nem madeira mais escura na copa; o cipó só envolve o tronco (não os galhos heróicos). Os anéis de cipó estão visíveis, mas não colados perfeitamente à casca em todos os pontos. Não reimportado no Roblox.
- **B2 corrigida e reexportada (12 modelos):** escadas das Casa_Lona A e B deslocadas 2 studs para a varanda (topo do degrau encosta no deck); atlas de madeira com cordas/topos de tora já escurecido. A escada da B tem 2 degraus (não 3) e o colisor das casas não foi ajustado. Capturas 184–188.

### Segunda passada (mesmo dia): copa, madeira e samambaias
- **Árvore Ancestral:** atlas `Folhas_Hero.png` refeito com aglomerados de folhas largas lobadas (estilo bordo, 3–4 folhas por célula, cor por linha mantida: sombra → verde médio → verde-limão → escuro); cartões da copa ampliados (LOD0 ×1,35, LOD1 ×1,25, LOD2 ×1,15, mesmas contagens de tris: 56.942 + cipó / 11.836 / 1.756); casca `Casca_Hero` escurecida (×0,68). Reexportada em `BLENDER/` (.glb ≈9,0 / 7,1 / 6,4 MB). Cartões maiores podem se sobrepor mais e a copa ficou mais densa (menos vãos de luz). Captura 189, atlas 191.
- **Vãos de luz (terceira passada):** cartões voltaram a ×1,10/×1,10/×1,08 do original (reduzidos ×0,815/0,88/0,93) e foram removidos por aglomerados (≈30% LOD0, 24% LOD1, 14% LOD2) mais ≈12%/8% aleatórios; copa LOD0 10.250→6.306 cartões. Contagens finais: LOD0 51.294 tris (tudo, sem colisores), LOD1 11.126, LOD2 1.642; .glb 8,3 / 6,8 / 6,3 MB. Captura 192. Os vãos são sutis a distância; falta conferir olhando por baixo/em Roblox.
- **Samambaias A5:** atlas `Samambaia_V2` refeito com fronde pinada (raque + 22 pares de folíolos finos); os 3 modelos mantêm 112–196 tris. Captura 190. Reexportada a família A5 inteira (9 modelos). Arbustos/plantas largas e cipós continuam com o atlas anterior.
- Não validado no Roblox (transparência, brilho/azulado das copas, custo da copa maior com cartões ampliados).

### Validação no Roblox Studio (2026-10-21) — A5 e Árvore Ancestral LOD1/LOD2
- Importados pelo usuário e organizados em `Workspace/TESTE_Importados_A5_LOD` (fora do mapa): 9 modelos A5 em fila (Z=−120), `TESTE_Ancestral_LOD1` (−300,−450) e `TESTE_Ancestral_LOD2` (700,−450).
- Correções aplicadas (padrão): `TextureID` → `SurfaceAppearance` (ColorMap, `AlphaMode=Transparency`; 16 criados), peças ancoradas, visuais `CanCollide=false`, colisores transparentes (Hull, CanQuery false), Cipos/Pedras/Oco/Hastes recoloridos.
- Resultado visual: samambaias A5 aparecem como frondes pinadas com recorte de alfa (sem placas); LOD1 da Ancestral mostra folhas largas lobadas, casca escura e cipó espiralado, com vãos visíveis; LOD2 funciona.
- **Achado:** o LOD2 foi importado com escala ×4 (Roblox mostrou ~1.600–2.048 studs em vez de ~400); corrigido com `ScaleTo(×0,25)` — conferir a escala de importação ao importar LODs.
- **LOD0 novo importado depois** (13 partes, com `Cipo_Espiral_LOD0`): chegou com escala ≈×2,82 (importador reduz para caber em 2048); corrigido com `ScaleTo(0,3542)` (tronco 403,3 studs de altura) e colocado em `TESTE_Importados_A5_LOD/TESTE_Ancestral_LOD0` (300,−450) com os mesmos ajustes (SurfaceAppearance Transparency nas copas e no cipó, colisores ocultos Hull, ancorado, recolor). Renderiza com folhas largas, vãos, casca escura e cipó espiralado visível (capturas 194–195). A escala de importação varia por arquivo (×4 no LOD2, ×2,82 no LOD0): sempre conferir pela altura do tronco.
- **Importação antiga:** `Workspace/ArvoreAncestral_Principal_LOD0` (sem cipó) e `Scene` do V5W seguem como estavam (não apaguei).
- **Não validado:** FPS/memória, Play, mobile e colisão com personagem. Capturas Roblox 193–195.

### Validação no Roblox — famílias B e B2 (2026-10-21)
- O usuário importou **B (11 modelos) e B2 (12)**; a **família C (ruínas) NÃO foi importada** (não há nenhum modelo `Muro_Ruina`, `Altar` etc. no Studio). Organizados em `Workspace/TESTE_Importados_B_B2` (grade em X −300…25, Z 600–780), 23 modelos, fora do mapa.
- Escala de importação correta nestes modelos (ex.: Casa_Lona_A 19,8×15,8×21 studs = Blender).
- Ajustes aplicados: `TextureID` → `SurfaceAppearance` (Overlay; capins `Transparency`), colisores transparentes/Hull, ancorado, `Ferro` metal escuro, `Luz` Neon quente, `Brasa` Neon laranja, `Interior` madeira escura.
- **Defeito encontrado e corrigido no Roblox:** as lonas/tecidos (`*_Lona_M`, `*_Tecido_M`) e capins são malhas de uma face só e ficavam invisíveis (casa só com caibros, captura 199); corrigido com `MeshPart.DoubleSided=true` (captura 196). Para reexportar, ideal duplicar/inverter as faces no Blender.
- Escada da Casa_Lona_A agora encosta na varanda (captura 197). Casa_Lona_B/Banca/Fogueira e família B renderizam (captura 198).
- Não validado: ruínas (C), FPS/memória, Play, colisão de personagem nos colisores, luz real das lanternas (só material Neon).

### Validação no Roblox — família C (2026-10-21)
- Importados 16 modelos (Tendas A/B, Fogueira_A, Muros A/B/C, Arcos A/B, Monolitos A/B, Mesa_Mapa, Altar, Colunas, Santuário) em `Workspace/TESTE_Importados_C` (X −300…25, Z 880–930). Escala correta (ex.: Muro_Ruina_C 27,5 studs de largura).
- Ajustes: SurfaceAppearance (Pedra/Raízes Overlay, HeraFolhas Transparency), colisores Hull/transparentes, ancorado, Brasa/Runas Neon, Hera verde.
- **Defeitos achados no Roblox:** (1) pedras de caixas, hera e runas ficam com faces ocas (uma face só) → `DoubleSided=true` resolve (captura 201); lonas das tendas também. (2) A hera/folhas pendem abaixo do chão (modelos erguidos 3–7 studs pelo pivô) → reapoiados pelo ponto mais baixo das peças sem hera. (3) Tudo ficou muito verde (musgo + hera), tom saturado; folhas da hera grandes.
- Raiz do problema: faces de uma só direção e normais invertidas nos meshes de caixas/lona; correção definitiva exige reexportar do Blender com faces duplicadas/invertidas. Pivôs não estão na base do modelo (importador centraliza).
- Não validado: FPS/memória, Play, colisão de personagem. Capturas 200–202.

### Correção no Blender e reexportação de B, B2 e C (2026-10-21)
- **Faces:** diagnóstico por ilha de malha: 1.008 (B), 380 (C) e 444 (B2) caixas/ilhas fechadas estavam com a normal para dentro (volume negativo) → invertidas para fora; ilhas abertas (lonas, capins, folhas e tubos de hera/raízes: 4.019 em C, 8.897 em B2) receberam cópia com faces invertidas (dupla face real, sem depender de `DoubleSided`). Custo: Casa_Lona A/B passaram de ≈7,4 mil para ≈13 mil tris (muitas tábuas abertas foram duplicadas); demais valores no relatório de exportação (B 48–3.372; B2 108–13.048; C 108–2.624).
- **Verde das ruínas:** `PedraMuro_V2` com o excesso de verde reduzido (−65%) e leve aquecimento; folhas da hera 40% removidas e as restantes ×0,7; material próprio `Hera_Cipo_C` (verde-escuro, sem afetar a Ancestral); hera/folhas presas acima do chão (z ≥ 0,05).
- **Pivôs:** o glTF mantém um só pivô (origem do arquivo, base em z=0); o importador do Roblox recentraliza o pivô na caixa envolvente, então isso não é corrigível no Blender — a base visual agora coincide com o chão (hera não passa de z=0), logo basta apoiar pela caixa envolvente.
- Reexportados: 11 modelos B, 12 B2, 16 C. **Ainda não reimportados no Roblox** (os `TESTE_Importados_*` no Studio usam a versão anterior com `DoubleSided`). Capturas 203–204.

### Pedras flutuando — correção nas ruínas (2026-10-21)
- Causa: entulho (lajes finas e blocos soltos) gerado em altura aleatória e grupos de blocos sem contato com a base (entablamento do santuário ≈0,7 acima das colunas, pontas do arco, lajes a vários metros do chão).
- Correção por análise de ilhas da malha: duplicatas coincidentes removidas (colunas tinham tambores repetidos) e dupla face reposta nas ilhas abertas; grupos de blocos sem conexão (distância de vértices <0,35) assentados até o suporte abaixo ou o chão; lajes finas pousadas sobre o suporte sob o centro; blocos isolados baixados. Ex.: santuário com entablamento apoiado nas colunas (captura 206); Arco B com entulho no chão (205).
- Limite: ainda restam pequenas folgas (≈0,3 stud) em blocos inclinados do arco B e o bloco superior do arco continua em balanço. Reexportada a família C (16 modelos, mesmas contagens de tris). Precisa reimportar no Roblox para confirmar.

### Revalidação no Roblox das famílias corrigidas (2026-10-21)
- Reimportados 39 modelos (B 11, B2 12, C 16) → `Workspace/TESTE_Corrigidos_B_B2_C` (prefixo `NOVO_`, grade X 100–375, Z 600–990). As pastas antigas `TESTE_Importados_*` ficaram como estavam.
- **Teste principal: `DoubleSided=false` em todas as peças** (0 com DoubleSided). Resultado: Casa_Lona com lona no telhado, paredes e pedras sólidas, ruínas sem faces ocas, hera e folhas aparecem (capturas 207–209). Confirma a correção das normais/dupla face no Blender.
- Ajustes automáticos de importação mantidos: 79 SurfaceAppearance (HeraFolhas/Grama Transparency; demais Overlay), 35 colisores transparentes Hull, TextureID zerado, recolor de Ferro/Luz/Brasa/Runas/Raízes/Hera/Interior, base apoiada em Y=0 pelas peças sem hera.
- Pedras: muros e arco B assentados, tom menos verde (captura 208). Resta um bloco superior inclinado do arco B pairando por ≈0,3 e o entulho inclinado.
- **Santuário:** medidas ok (16,1×14,0×17,3; base Y=0), mas a captura visual falhou duas vezes (timeout/Studio desconectou) — ele NÃO foi conferido visualmente no Roblox. Studio usa ≈3,3 GB de RAM; sem FPS/memória medidos, sem Play, sem colisão de personagem.

### Teste em Play: desempenho e colisão (2026-10-21)
**Método:** Play no Studio (cliente com câmera scriptable, 3–5 s por ponto, FPS = frames/Heartbeat; memória `Stats.GetTotalMemoryUsageMb`). Studio com ≈7,4–7,9 GB de memória total (inclui edição, servidor e cliente) e ≈3,3 GB do processo em Edit. **Medição ruidosa; é do Studio em PC, não de celular.**
| Vista | FPS | Pior frame |
|---|---|---|
| Céu (base) | 54,5 | 212 ms |
| Chão vazio | 58,4 | 44 ms |
| Ancestral LOD0 perto (tronco) | 52,9 | 44 ms |
| Ancestral longe (copa inteira; vista larga para o mapa) | 28,6 | 198 ms |
| 3 Ancestrais (LOD0/1/2) | 29,4 | 80 ms |
| Vila B2 / Vila B / Ruínas C | 58,0 / 57,8 / 57,4 | 106 / 196 / 188 ms |
| Visão alta do conjunto | 60,0 | 32 ms |
- Memória total subiu ≈+370 MB ao abrir as vistas (7.415→7.780 MB) e ≈+100 MB ao olhar toda a área; `GraphicsMeshParts` e `GraphicsTexture` ficaram ≈11 / 140–145 MB (o custo gráfico específico dos novos modelos não apareceu nessas tags).
- **FPS baixo na vista longa (≈29):** retirar o conjunto Ancestral novo (LOD0+1+2) só variou 28,3–29,9 fps → o gargalo não é a árvore nova, e sim o restante do que está visível (outras árvores/Proto). Não consegui isolar o culpado: remover/reinserir os grupos grandes derrubou a chamada ao cliente. Console mostra muitos "Asset content representation is being generated" (texturas recém-enviadas ainda sendo processadas).
- Casos fora do escopo/não medidos: mobile, servidor publicado, vários jogadores, árvore Ancestral como instância repetida.
**Colisão (servidor, Humanoid andando 4–9 s):** Casa_Lona_A parou a ≈9,6 do centro (colisor 17×11×18) ✔; Casa_Grande_A parou a ≈9,9 (26×11×18) ✔; Muro_Ruina_C parou a ≈1,6 (colisor 22×11×2) ✔; HeraFolhas `CanCollide=false` (atravessável) ✔; controle em campo vazio andou ≈48 em 4 s ✔; tronco da Ancestral bloqueou o personagem a ≈48,5 do centro ✔.
- **Defeito de colisão encontrado:** `Colisor_Raizes` (hull de 458×438×82) funcionava como um **morro**: o personagem subiu até Y≈66 ao andar na direção do tronco; o resultado não mudou com `PreciseConvexDecomposition`. Correção: colisor de raízes removido do LOD0 (no Studio `CanCollide=false` em `TESTE_Ancestral_LOD0/Colisor_Raizes`; no Blender renomeado `X_Raizes_Colisor_desativado` e **LOD0 reexportado sem ele**, 8,4 MB). Só o `Colisor_Tronco` permanece. Precisa reimportar para valer no arquivo do Roblox.

### Diagnóstico do FPS baixo na vista larga (2026-10-21)
- **Culpado identificado: a floresta protótipo existente, não os modelos novos.** `Workspace/Proto_FlorestaAncestral` tem **≈159 mil partes** (Floresta 98.765, Chunk_Ancestral 34.864, Cobertura_LOD 8.433, Arvores 6.406, Sotobosque 3.453), todas ancoradas: `Part` ≈115 mil, `UnionOperation` ≈29 mil, `WedgePart` ≈2,5 mil; só ≈3 mil com CastShadow e ≈1,6 mil com CanCollide. Os modelos novos somam ≈350 MeshParts (Corrigidos 152 + Importados B/B2 75 + C 69 + A5/Ancestral 45).
- **Evidência:** (1) com FOV 30 e câmera olhando para o lado das árvores novas (yaw 0) → 60 fps; subindo o yaw rumo à floresta (X≥900) → 54 e 49 fps; (2) com FOV 70 a vista larga mede ≈41 fps estável (4 rodadas 40,4–41,9); (3) remover `TESTE_Corrigidos_B_B2_C` → 39 fps (sem efeito); remover a Ancestral nova (LOD0+1+2) → 28,3–29,9 vs 29,9 (sem efeito) nas medições anteriores. As quedas iniciais (15 e 29 fps) eram aquecimento (assets "being generated" e carga de texturas) e oscilam muito: o FPS do Studio é ruidoso.
- `StreamingEnabled=true` já ativo; todos os ≈16,7 mil `Model` com `LevelOfDetail=Automatic`. Maiores árvores: 141 (Floresta) + 23 (Chunk) + 11 (Arvores) modelos com ≥150 partes diretas (≈32 mil partes); um modelo típico (`SO_010`) tem 1.102 partes.
- **Teste de correção (só na sessão Play, não salvo):** `LevelOfDetail=StreamingMesh` em 175 modelos grandes → vista larga ≈41 → ≈50–52 fps (3 rodadas); floresta de longe 47,9 → 46,7 (sem ganho). Indicativo, não conclusivo (uma série por condição).
- **Correções propostas (aguardam autorização, nada aplicado no arquivo):**
  1. Aplicar `LevelOfDetail=StreamingMesh` nas árvores grandes da floresta (baixo risco, reversível; confirmar visual dos impostores).
  2. Trocar as árvores feitas de ≈1.000 `Part`/`UnionOperation` pelas árvores em malha (V5W/V4 LOD0–2: 3 MeshParts por árvore, 1–12 mil tris) — corta ≈99% das partes; é a mudança de maior efeito, mas altera o visual aprovado e exige importar/validar LODs.
  3. Reduzir a distância visível de vegetação pequena (Sotobosque/Cobertura) via streaming radius/Atmosphere e ocultar o sotobosque além de ~300 studs com script cliente.
  4. Verificar/atualizar `CastShadow`: já baixo (≈3 mil), manter.
  5. Medir em dispositivo real/cliente publicado (o Studio mede ≈29–60 fps de forma instável e usa ≈3,3 GB).

### StreamingMesh aplicado no arquivo, medido e REVERTIDO (2026-10-21)
- Autorizado: `LevelOfDetail=StreamingMesh` em 175 modelos com ≥150 partes (Floresta 141, Chunk_Ancestral 23, Arvores 11), com atributo `LOD_Anterior` para reverter.
- Medição com o mesmo protocolo (aquecimento 12 s, 3 rodadas de 4 s, vista larga FOV 70): **antes** 46,7 / 43,0 / 43,2 fps (floresta de longe 36,1); **depois** 29,0 / 25,3 / 28,1 (floresta de longe 24,7) e, 60 s depois, 26–30 fps; memória total do Studio subiu para ≈10,3 GB (vs ≈7,9 GB antes). **A mudança PIOROU o desempenho no Studio** (≈−35% de FPS e mais memória), ao contrário do teste efêmero da sessão anterior (que sugeria +25%); o resultado anterior não se confirmou.
- **Revertido** (175 modelos de volta a `Automatic`, atributos removidos; nenhum modelo com LOD ≠ Automatic restante). Após reverter: 45,2 / 40,3 / 40,5 fps (floresta de longe 33,9) — volta à faixa anterior. Estado final do arquivo = o de antes.
- Conclusão: `StreamingMesh` **não** é recomendado aqui (ao menos para modelos de ~1.000 `Part`; a geração de impostores custa memória/CPU). Seguem válidas as propostas 2 e 3 (trocar as árvores por malhas V5W/V4 com LODs; limitar a distância do sotobosque). Memória absoluta do processo do Studio oscila e cresce ao longo da sessão (≈9,7–10,6 GB) — comparar só dentro da mesma sessão.

## Como importar (usuário)
Studio > View > Asset Manager > Bulk Import > selecione os `.glb` de uma família. Depois: criar `SurfaceAppearance` com ColorMap vindo de `TextureID` e `AlphaMode = Transparency` nas folhas/capins; recolorir peças sem textura; ancorar; ocultar colisores.
