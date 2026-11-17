# Lobo Ancestral — corrigir caroços no início das patas dianteiras

**Chat executor:** Lobo Ancestral (Floresta Ancestral). Pedido visual direto do usuário. Imagem do defeito anexada a esta mensagem; arquivo temporário: `C:/Users/Rhenan/AppData/Local/Temp/codex-clipboard-3cd63b89-5eb0-4bd4-9368-a76678cac42b.png`. Referência original: `REFERENCIAS/floresta-ancestral/lobo-ancestral/lobo-ancestral-referencia.png`.

Na vista frontal do modelo atual há **dois caroços/quinas escuras na parte superior das patas dianteiras**, logo abaixo das laterais do peito e da juba, na transição ombro–braço. Eles parecem saliências soltas e quebram a anatomia do lobo. Corrija esse defeito localizado; não trate apenas com câmera, iluminação ou mudança global de pose.

Leia `CLAUDE.md`, `DOCS/criaturas/lobo-ancestral.md` (estado mais recente, §6f), `DOCS/ORGANIZACAO-CHATS.md` e inspecione `BLENDER/Criaturas/Lobo_Ancestral_Ref/rig5/`, `clipes5/`, `export5/` e scripts próprios. Antes de editar, identifique em close frontal e três-quartos se os caroços vêm da geometria da malha, de pelos do peito, de pesos do ombro/braço ou de sombreamento/normal. Marque os vértices e ossos envolvidos e mostre o diagnóstico. Preserve `rig5/export5` como comparação.

Suavize e integre a transição do peito para cada pata, mantendo o volume natural das escápulas e a separação legível entre as duas patas. Faça ajuste mínimo na origem do problema, preservando textura, UV, marcas, silhueta lateral, articulações, rig e custo Roblox. Não simplesmente corte o ombro nem esconda o defeito com pelo extra. Se alterar pesos ou malha, confira deformação ao levantar e apoiar a pata.

**Aceite visual:** entregue closes **antes × depois × referência** de frente, lado e três-quartos, na mesma câmera e luz; mostre Repouso e pelo menos três quadros de Andar e Corrida, incluindo a pata em apoio e elevada. Não pode restar caroço, buraco, dobra brusca, interseção com a juba ou nova assimetria. Reimporte o GLB, confira os 23 clipes e registre qualquer regressão. Diga explicitamente se o apoio estranho da pata em Repouso também foi corrigido ou se continua pendente; não o declare resolvido apenas por medida de IK.

Trabalhe somente no Lobo Ancestral. Não use o Studio nesta correção; qualquer teste futuro respeita `DOCS/estado/studio-em-uso.md`. Não altere outras criaturas, bases compartilhadas, scripts globais ou terreno. Sem instalação, compra, commit ou push sem autorização. Siga a atualização oficial de 30/10/2026 e responda no formato de `CLAUDE.md`, com evidências e próximo passo aguardando aprovação.
