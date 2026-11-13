-- Apelidos da WYVERN (ReplicatedStorage.Animacoes_Wyvern, clipes "Wyvern_*"; 12/11/2026, TESTE no Teste-animacoes).
-- Esqueleto proprio (base Ashwing adaptada, 61 ossos; Quadril/Coluna2/Cabeca/Mandibula/mouth_upper_tip/tail_tip/
-- toes_tip_* com os nomes do jogo, o resto com os nomes do rig). Os clipes sao os APROVADOS no Blender
-- (Wyvern_E7_clipes_L6.blend, 49 actions; build/22_exportar_clipes_wyvern.py com CONVENCAO_ROBLOX=giro180y, conferido
-- no Studio contra o Blender). Nunca reaproveitar clipes do Dragao (familias diferentes): aqui so se mapeia o nome
-- logico que a IA/montaria pedem para o clipe da Wyvern mais proximo.
-- Sem clipe proprio (usa o mais proximo, ate existir um): Beber/Beber_Loop -> Comer (cabeca ao chao a frente);
-- Dormir/Adormecer -> Deitado; Sentar/Sentado -> Deitar/Deitado. Elemento e kit da Wyvern estao PENDENTES: nenhum
-- clipe de habilidade (Sopro_*, Hab_*, Tempestade...) existe; caem no "*" (repouso).
local function c(n) return "Wyvern_" .. n end
return {
	prefixo = "Wyvern_",
	["*"] = c("idle_loop"),
	-- em pe
	Parado = c("idle_loop"), Idle_Neutro = c("idle_loop"), Observar = c("OlharVolta"), Observar_Farejar = c("Farejar"),
	Curiosidade = c("Farejar"), Reagir_Estimulo = c("Alerta"), Idle_Alerta_Mantido = c("Alerta"), Intimidar = c("Ameaca"),
	Preparar_Combate = c("Alerta"), Rugido_Territorial = c("roar"), Rugido_Combate = c("roar"), Espreguicar = c("Espreguicar"),
	-- chao
	Andar = c("walk_loop"), Correr = c("Corrida"), Giro_E = c("VirarEsquerda"), Giro_D = c("VirarDireita"),
	Parada = c("Frenagem"), Correr_Frenagem = c("Frenagem"),
	-- ar
	Decolagem = c("takeoff"), Voo = c("fly_loop"), Voo_Rapido = c("VooBatido"), Pairar = c("PairarCurto"), Planeio = c("Planeio"),
	Pouso = c("Pouso"), Subida = c("Subida"), Descida = c("Descida"), Mergulho = c("Mergulho"),
	Curva_E = c("CurvaAereaEsquerda"), Curva_D = c("CurvaAereaDireita"),
	Curva_Aerea_E = c("CurvaAereaEsquerda"), Curva_Aerea_D = c("CurvaAereaDireita"),
	Mergulho_Entrada = c("Mergulho"), Mergulho_Picado = c("Mergulho"), Mergulho_Freio = c("Planeio"), Mergulho_Saida = c("Planeio"),
	-- misturador de voo da montaria (pesos por manobra)
	Voo_AFK = c("fly_loop"), Pairar_AFK = c("PairarCurto"), Planeio_AFK = c("Planeio"), Curva_Aerea_E_AFK = c("CurvaAereaEsquerda"),
	Curva_Aerea_D_AFK = c("CurvaAereaDireita"), Mergulho_AFK = c("Mergulho"), Subida_AFK = c("Subida"), Descida_AFK = c("Descida"),
	Olhar_Cima_AFK = false, Olhar_Baixo_AFK = false, Olhar_E_AFK = false, Olhar_D_AFK = false,
	-- vida
	Comer = c("Comer"), Comer_Mastigar = c("Comer"), Beber = c("Comer"), Beber_Loop = c("Comer"),
	Deitar = c("Deitar"), Deitado_Acordado = c("Deitado"), Adormecer = c("Deitado"), Dormir = c("Deitado"), Acordar = c("Levantar"),
	Descanso = c("Deitado"), Sono = c("Deitado"), Sentar = c("Deitar"), Sentado = c("Deitado"), Levantar_Sentado = c("Levantar"),
	Ninho_Acomodar = c("Deitar"), Ninho_Repouso = c("Deitado"), Ninho_Inspecionar = c("Farejar"), Ninho_Alerta = c("Alerta"),
	Ninho_Ameaca = c("Ameaca"),
	-- montaria (o cavaleiro sobe pela frente da asa com a Wyvern em pe; parada montada = RideIdle aprovado)
	-- montado (Montaria_Dragao_Servidor PATCH_RIDE_CLIPES): dorso estabilizado sob a sela (Ride* aprovados 06/11)
	Montado_Parado = c("RideIdle"), Montado_Andar = c("RideWalk"), Montado_Correr = c("RideRun"),
	Montado_Giro_E = c("RideVirarEsquerda"), Montado_Giro_D = c("RideVirarDireita"),
	Montaria_Abaixar = c("idle_loop"), Montaria_Aguardar = c("RideIdle"), Montaria_Levantar = c("idle_loop"),
	-- ataques basicos fisicos (nao ocupam slot; numeros de combate NAO aprovados)
	Ataque_Mordida = c("bite"), Mordida_Aerea = c("bite"), Ataque_Cauda = c("FerraoAtaque"),
	Dano_Leve = c("ReacaoGolpe"), Dano_Forte = c("ReacaoGolpe"), Dano_Leve_Ar = c("fly_loop"), Dano_Forte_Ar = c("fly_loop"),
}
