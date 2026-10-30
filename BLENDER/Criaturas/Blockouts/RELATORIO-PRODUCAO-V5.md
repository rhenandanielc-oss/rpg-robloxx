# Produção autônoma V5: 15 criaturas (27/10/2026)

**Situação:** os 15 modelos estão tecnicamente concluídos no Blender e aguardam a sua avaliação artística.
- Cada criatura tem: revestimento novo, textura, rig, animações, exportação e validação por reimportação no Blender.
- Nenhum modelo foi testado no Roblox Studio e nenhum foi aprovado pelo criador.
- O Lobo Ancestral não foi alterado.

## Como foi feito
- **Lobo Ártico:** script próprio (`build/lobo_artico.py`), com a técnica da V5 do Ancestral. Nesta rodada, as orelhas ganharam pelo e o calombo sob a mandíbula foi removido.
- **Demais 14 criaturas:** novo módulo `build/revest.py`. Ele classifica cada vértice pelo osso mais próximo do esqueleto da espécie (cabeça, pescoço, tronco, perna, cauda, asa) e aplica o revestimento:
  - **Pelo** (Urso, Leão, Búfalo, Cérbero): o subpelo infla a superfície, com mechas no sentido do crescimento, e por cima vão cartões de pelo com transparência (técnica aprovada nos lobos).
    - Urso: folhas e samambaias.
    - Leão: juba em volta da cabeça e do pescoço, e tufo na ponta da cauda.
    - Búfalo: capa densa na cabeça, no pescoço e na corcova; chifres escuros.
    - Cérbero: pelo curto nas três cabeças, para que fiquem legíveis.
  - **Placas** (dragões, Wyvern, répteis, escorpião, aquáticos): escamas e placas de geometria sobrepostas, maiores no dorso e menores nos flancos. O ventre fica só na textura. Cada espécie tem um atlas com relevo, borda escura e estrias:
    - Dragão das Montanhas: fissuras de lava;
    - Dragão Sombrio: fissuras magenta;
    - Escorpião: fissuras quentes, na cor castanho-cobre;
    - Crocodilo: osteodermos maiores.
  - Os chifres e espinhos seguem a cor de cada prancha.
- **Silhueta:** é a da V2 aprovada (`<Esp>_refinado.blend`). A V2 foi preservada; a V5 tem arquivos próprios.
- **Pipeline:** `pipeline_final.py` com `CR_SUFIXO=_v5` gera textura assada, rig, pesos (as placas e cartões copiam os pesos da pele), animações, exportação GLB e auditoria. O caminho específico dos lobos agora fica restrito aos dois lobos.

## Tabela

Estados: **Anatomia** = silhueta V2 mais revestimento (sem nova escultura de forma). **Textura** = assada mais atlas de revestimento. **Rig** = esqueleto V2 da família (no Ártico, com 10 ossos de pelo). **Exportação** = GLB validado por reimportação no Blender (esqueleto, ações, imagens, nenhuma malha acima de 20 mil). **Roblox** = não testado em nenhuma.

| Criatura | Tris | Maior malha | Ossos | Animações A/PA/R* | GLB | Validação |
|---|---|---|---|---|---|---|
| Lobo Ártico | 32.646 | 11.998 | 42 | 7/12/9 | 5,1 MB | OK |
| Urso Silvestre | 41.619 | 16.000 | 25 | 8/15/5 | 4,8 MB | OK |
| Leão Solar | 32.188 | 18.000 | 36 | 4/17/7 | 4,2 MB | OK |
| Búfalo Colossal | 30.624 | 16.000 | 27 | 6/15/7 | 3,8 MB | OK |
| Cérbero Sombrio | 29.876 | 14.000 | 40 | 6/18/4 | 4,1 MB | OK |
| Dragão das Montanhas | 41.922 | 15.998 | 48 | 3/33/2 | 4,3 MB | OK |
| Dragão Glacial | 41.944 | 16.000 | 48 | 5/33/0 | 4,3 MB | OK |
| Dragão Sombrio | 48.844 | 16.000 | 48 | 4/33/1 | 4,5 MB | OK |
| Wyvern | 47.416 | 14.000 | 39 | 0/37/1 | 5,0 MB | OK |
| Basilisco | 71.716 | 16.000 | 28 | 25/3/0 | 7,5 MB | OK |
| Crocodilo Primordial | 56.198 | 15.998 | 24 | 30/1/0 | 5,0 MB | OK |
| Escorpião Colossal | 58.056 | 16.000 | 43 | 27/1/0 | 6,5 MB | OK |
| Lagarto Cristalino | 77.640 | 16.460 | 23 | 25/3/0 | 8,3 MB | OK |
| Serpente Marinha | 47.424 | 15.000 | 27 | 33/3/0 | 4,5 MB | OK |
| Leviatã Jovem | 29.784 | 16.000 | 22 | 27/9/0 | 2,6 MB | OK |

\*A/PA/R é a auditoria automática de deformação (Aprovada / Pequenos ajustes / Refazer). Ela não substitui a avaliação visual. As animações foram **regeneradas** com o mesmo código das V2 sobre o novo revestimento, sem animação nova feita à mão.

## Arquivos
- **Blender:**
  - `<Esp>/<Esp>_refinado_v5.blend` (modelo com revestimento);
  - `<Esp>/<Esp>_final_v5.blend` (modelo com rig e animações).
- **GLB:** `_Export/<Esp>_v5.glb`.
- **Dados:** `review/<Esp>/final_v5.json`; validação em `review/validacao_glb_v5.json`.
- **Renders:** `review/<Esp>/v5_fixo/` (frente, lateral, 3/4, cabeça, revestimento, silhueta com humano) e `review/<Esp>/v2_fixo/` (anterior).
- **Pranchas comparativas** com as referências oficiais: `review/<Esp>/Prancha_<Esp>_v5.png`.

## Problemas que continuam
1. **Anatomia:** os corpos ainda são as silhuetas V2, modeladas com primitivas fundidas. Não houve escultura nova de forma nesta rodada. As maiores diferenças para as pranchas são:
   - dragões: pescoço e peito pouco maciços;
   - Leão: peito volumoso sob a juba;
   - Urso: cabeça grande;
   - Serpente: postura.
2. **Asas** dos dragões e da Wyvern: as membranas são lisas, sem veios nem desgaste.
3. **Itens específicos ainda não modelados:**
   - musgo pendente do Basilisco;
   - cavidade da boca, dentes e língua para rugidos (Urso, Leão, Cérbero, Crocodilo);
   - fissuras vermelhas do Cérbero.
4. **Custo:** 30 a 78 mil tris por criatura. Basilisco e Lagarto são os mais pesados e precisam de LOD antes de usar em grupo.
5. **No Roblox, nada foi testado.** A importação é manual e é preciso confirmar:
   - a transparência dos cartões de pelo (SurfaceAppearance com AlphaMode = Transparency, MeshPart com DoubleSided);
   - a escala, os ossos e as animações;
   - o FPS.

## Decisões que precisam de você
- Avaliação artística de cada prancha.
- Se a próxima rodada deve ser de **escultura de forma** (anatomia) espécie por espécie, ou de **asas, boca e dentes**.
- A importação de teste no Roblox Studio, num place vazio.
