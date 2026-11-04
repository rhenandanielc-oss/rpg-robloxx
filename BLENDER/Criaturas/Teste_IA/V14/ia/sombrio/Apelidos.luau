-- Apelidos do DRAGAO SOMBRIO (ReplicatedStorage.Animacoes_Sombrio, clipes "Sombrio_*"; copia dos apelidos do Glacial).
-- Mesmo esqueleto e mesmos nomes logicos (EstadosDragao e IA compartilhados); o modelo usa PastaAnimacoes = "Sombrio".
-- Kit de SOMBRA PENDENTE (decisao do usuario): nenhum poder de Fogo/Gelo e montado nesta pasta; Sopro/Arremetida/
-- Tempestade/Ruptura/Coracao caem nos apelidos abaixo. Clipes Hab_* (movimento generico, sem efeito) ficam prontos.
-- Base copiada dos apelidos do Silverwing:
-- Apelidos (ModuleScript) — o Silverwing (Meshy + Mesh2Motion, TESTE) so tem 4 clipes: Idle, Walk, Fly_Flap, Fly_Glide.
-- O EstadosDragao procura primeiro "<prefixo><nome>"; se nao houver, usa este mapa (nome logico -> KeyframeSequence).
-- false = clipe inexistente de proposito (ex.: camadas Olhar_* do misturador de voo nao podem cair no Idle).
-- ["*"] = qualquer comportamento sem clipe proprio (comer, deitar, ninho...) toca o Idle.
-- v2 (29/10): clipes PROPRIOS (anim_silverwing.py: IK nas patas, cauda segmentada, voo estacionario). Os do molde
-- Mesh2Motion ficaram em Antigas_M2M (so referencia). Nomes com o prefixo ("Silverwing_Parado") sao achados direto.
local function c(n) return "Sombrio_" .. n end
return {
	prefixo = "Sombrio_",
	["*"] = c("Parado"),
	Descanso = c("Abaixado"), Sono = c("Abaixado"), Deitar = c("Abaixar"), Adormecer = c("Abaixado"), Dormir = c("Abaixado"),
	Deitado_Acordado = c("Abaixado"), Acordar = c("Levantar"), Ninho_Acomodar = c("Abaixar"), Ninho_Repouso = c("Abaixado"),
	Montaria_Abaixar = c("Abaixar"), Montaria_Aguardar = c("Abaixado"), Montaria_Levantar = c("Levantar"),
	Correr_Frenagem = c("Parada"), Giro_E = c("Andar"), Giro_D = c("Andar"),
	Ninho_Inspecionar = c("Observar_Farejar"),       -- clipes proprios de comportamento (30/10) sao achados pelo prefixo
	Voo_Rapido = c("Voo"), Curva_Aerea_E = c("Curva_E"), Curva_Aerea_D = c("Curva_D"),
	-- misturador de voo da montaria (pesos por manobra)
	Voo_AFK = c("Voo"), Pairar_AFK = c("Pairar"), Planeio_AFK = c("Planeio"), Curva_Aerea_E_AFK = c("Curva_E"),
	Curva_Aerea_D_AFK = c("Curva_D"), Mergulho_AFK = c("Mergulho"), Subida_AFK = c("Subida"), Descida_AFK = c("Descida"),
	-- combate: clipes PROPRIOS (Silverwing_Ataque_*, Sopro_*, Arremetida, Tempestade_*, Ruptura_Vulcanica, Rugido_Combate
	-- e versoes _Camada no ar) sao achados pelo prefixo; os apelidos abaixo so valem se faltar um clipe
	Ataque_Mordida_Camada = c("Mordida_Aerea"),
	Ataque_Mordida = c("Mordida_Aerea"), Arremetida = c("Mordida_Aerea"), Rugido_Combate = c("Parado"),
	Sopro_Inicio = c("Parado"), Sopro_Loop = c("Parado"), Sopro_Fim = c("Parado"),
	Tempestade_Asas = c("Decolagem"), Tempestade_Asas_Ar = c("Pairar"), Ruptura_Vulcanica = c("Abaixar"),
	Coracao_Infernal = c("Parado"), Coracao_Infernal_Camada = c("Pairar"), Arremetida_Camada = c("Mordida_Aerea"),
	Olhar_Cima_AFK = false, Olhar_Baixo_AFK = false, Olhar_E_AFK = false, Olhar_D_AFK = false,
}
