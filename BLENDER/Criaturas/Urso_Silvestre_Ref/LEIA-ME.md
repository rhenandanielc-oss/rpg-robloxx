# Urso Silvestre: modelo novo fiel à referência (03/11/2026)

**Situação:** modelo 3D e malha de jogo prontos no Blender, **aguardando aprovação visual do usuário**. Ainda não há rig final, animações nem importação no Roblox.

- Referência: `ref/urso-silvestre-referencia.png`. É cópia de `REFERENCIAS/floresta-ancestral/urso-silvestre/`.
- Brief: `asset-brief.md`.

## Como gerar (tudo por script, Blender 5.2 headless)
1. `python texturas_urso.py tex`: cria os atlas 1024 do pelo (4 formas × 3 tons) e da vegetação (samambaia, folha, raminho, musgo, casca), cada um com mapa normal.
2. `blender -b --factory-startup -P criar_urso_corpo.py -- review/rNN`: cria o corpo (metaballs → voxel), o rosto, a boca recortada, os dentes, a língua, os olhos e as garras.
3. `blender -b review/rNN/CR_Urso_corpo.blend -P pelo_urso.py -- review/rNN`: adiciona os cartões de pelo, as placas de casca, os cipós, o musgo, as samambaias e as folhas. Saída: `CR_Urso_master.blend`.
4. `blender -b review/rNN/CR_Urso_master.blend -P low_urso.py -- low`: gera a malha de jogo, assa a cor e a normal do corpo e exporta o GLB e o LOD1 do pelo.
5. `blender -b --factory-startup -P validar_glb.py -- low/CR_Urso_Silvestre_LOW.glb`: reimporta e confere o GLB.
6. `blender -b <arquivo.blend> -P render_urso.py -- <dir>` + `python prancha.py <dir>`: gera as vistas e as comparações com a referência.

A pose de teste do render (cabeça erguida, boca aberta) é deformação direta, sem rig. Serve só para comparar com a referência.

## Rodada vigente: r07 (master) / r08_low (malha de jogo)

| Malha (GLB `low/CR_Urso_Silvestre_LOW.glb`) | Tris | Material / texturas |
|---|---|---|
| Urso_Corpo (pele + garras + dentes + língua + olhos) | 15.056 | cor + normal assadas, 1024 |
| Urso_Pelo_A (metade dianteira) | 14.424 | atlas de pelo com alfa, 1024, + normal |
| Urso_Pelo_B (metade traseira) | 14.436 | atlas de pelo com alfa, 1024, + normal |
| Urso_Vegetacao (samambaias, musgo, folhas) | 2.240 | atlas de vegetação com alfa, 1024, + normal |
| Urso_Casca (placas de casca + cipós) | 3.360 | mesmo atlas, região opaca |
| **Total LOD0** | **49.516** | 6 texturas de 1024 |
| Urso_Pelo_LOD1 (55% das mechas, mais largas), em `low/CR_Urso_Silvestre_Pelo_LOD1.glb` | 16.140 | total com LOD1 = 36.796 |

- **Medidas:** ombro com pelo 8,91 studs (oficial 8–10); comprimento 16,55; pés em Z = 0.
- **Validação por reimportação no Blender:** 5 malhas, todas ≤ 20k tris, com UV, 1 material e imagens 1024. Resultado: `GLB_VALIDO`.

## Estratégia de LOD e desempenho
Isto é proposta, não orçamento oficial.
- O pelo em cartões com alfa é o custo principal (~29k tris e sobreposição transparente).
- **Para várias criaturas:**
  - perto, usar o LOD0;
  - a média distância, trocar Pelo_A+B pelo LOD1 (−12,7k tris);
  - longe, deixar só Corpo + Casca (~18k), com a cor assada já carregando o tom do pelo.
- A troca seria por script de distância, como o `LOD_Distancia` do mapa. A RenderFidelity automática do Roblox também reduz as MeshParts.
- **Medição pendente:** só pode ser feita no Studio, com várias instâncias, em PC e em celular.

## Diferenças restantes em relação à referência
- Pelo em mechas mais "recortadas" e com mais contraste que a pintura da referência. Falta o brilho dourado das pontas, que na imagem vem da luz do sol.
- Placas de casca menores e menos salientes que na imagem. A vegetação lateral do ombro é mais discreta.
- Rosto liso (pelo curto só na textura). A juba do pescoço é menor que na referência.
- Olhos da malha de jogo saem borrados no bake (esfera pequena). Corrigir com material próprio ou mais resolução de UV.
- As patas dianteiras parecem menos colossais que na imagem, que usa grande-angular e câmera baixa. As proporções seguem o porte oficial.

## Adaptações técnicas
- Pose neutra (em pé, boca fechada); a referência ruge com a cabeça erguida.
- A boca é recortada até o canto, com interior, língua e dentes. Ela fecha corretamente.
- Casca em placas separadas, como telhas, sobre o dorso e o alto dos ombros. Nenhuma vegetação na cabeça ou no pescoço.
- O cipó vai do ombro até pouco abaixo do cotovelo.
- A vegetação é só aparência: não define elemento, habilidade nem efeito.

## Arquivos antigos preservados
Nada foi alterado em `Blockouts/Urso_Silvestre/`, `_Export/Urso_Silvestre*.glb` e `build/build_Urso_Silvestre.py`.

O V5 foi avaliado em `review/r00_v5_antigo/` e **não foi reaproveitado** como malha: a cabeça não tinha rosto nem boca e não havia casca. Ficou só como referência de proporção. O registro anterior das 28 ações serve de lista-base para os clipes depois da aprovação.

Binários (`.blend`, `.glb`, `.png` de revisão) não vão para o git. Os `.blend` das rodadas r01–r06 são intermediários reproduzíveis pelos scripts.
