-- SonsDragao_Cliente (LocalScript) — sons 3D dos dragoes (so visual/audio no cliente; nao afeta jogo).
-- Asas e passos: SINCRONIZADOS com as animacoes que estao tocando (fase da trilha -> evento), volume pelo peso.
-- Ataques: eventos cosmeticos do combate (Combate_Dragoes.FX) e atributos da Mordida Aerea.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Cfg = require(RS:WaitForChild("Montaria_Dragoes"):WaitForChild("SonsConfig"))
local cam = workspace.CurrentCamera

-- eventos por ciclo de cada clipe: fases (0..1) em que toca o som. Batida = golpe descendente; passos = apoio de cada pe
local Q4 = {0.1375, 0.3875, 0.6375, 0.8875}; local Q4s = {0.125, 0.375, 0.625, 0.875}
local ASAS = {Voo = Q4, Voo_AFK = Q4, Pairar = Q4, Pairar_AFK = Q4, Subida = Q4s, Subida_AFK = Q4s,
	Decolagem = {0.45, 0.85}, Voo_Rapido = {0.55}}
local PASSOS = {Andar = {0.02, 0.27, 0.52, 0.77}, Correr = {0.02, 0.14, 0.52, 0.64}, Correr_Frenagem = {0.1, 0.3},
	Pouso = {0.35}, Montaria_Levantar = {0.6}}

-- VOZ (comportamento da IA): som num ponto do clipe, com chance e intervalo minimo por dragao (nada de rugir sempre)
-- {fase, som em SonsConfig, chance, volume, tom}
local VOZ = {
	Ninho_Ameaca = {{0.36, "rugido", 1, 1.0, 0.9}}, Reagir_Estimulo = {{0.12, "esforco", 0.8, 0.7, 0.9}},
	Idle_Alerta_Mantido = {{0.5, "esforco", 0.35, 0.55, 0.85}}, Preparar_Combate = {{0.3, "esforco", 0.4, 0.65, 0.8}},
	Comer = {{0.1, "mordida", 1, 0.7, 0.8}, {0.433, "mordida", 1, 0.7, 0.8}, {0.766, "mordida", 1, 0.7, 0.8}},
}
local VOZF = {}; for n, l in pairs(VOZ) do VOZF[n] = {}; for _, e in ipairs(l) do table.insert(VOZF[n], e[1]) end end
local INTERVALO_VOZ = {rugido = 12, esforco = 7, mordida = 0.5}
local ultimaVoz = {}

local ativos = {}
local function tocar(pai, sid, vol, tom, corte)
	if not (pai and pai.Parent) then return end
	if (ativos[pai] or 0) >= (Cfg.maxSimultaneos or 6) then return end
	ativos[pai] = (ativos[pai] or 0) + 1
	task.delay(corte or 2.5, function() ativos[pai] = math.max(0, (ativos[pai] or 1) - 1) end)
	local s = Instance.new("Sound"); s.SoundId = sid; s.Volume = vol or 1; s.PlaybackSpeed = tom or 1
	s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = 12; s.RollOffMaxDistance = Cfg.distMax
	s.Parent = pai; s:Play()
	if corte then task.delay(corte, function() if s.Parent then s:Stop(); s:Destroy() end end)
	else s.Ended:Once(function() s:Destroy() end); task.delay(12, function() if s.Parent then s:Destroy() end end) end
end
local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end
local function faixa(f) return f and (f[1] + (f[2] - f[1]) * math.random()) or 1 end
local function tocarVoz(m, pp, nome, fase)
	for _, ev in ipairs(VOZ[nome]) do
		if ev[1] == fase and math.random() <= ev[3] then
			local k = ev[2]; ultimaVoz[m] = ultimaVoz[m] or {}
			if os.clock() - (ultimaVoz[m][k] or -99) >= (INTERVALO_VOZ[k] or 5) then
				ultimaVoz[m][k] = os.clock()
				tocar(pp, sorteia(Cfg[k]), ev[4], ev[5] * (0.95 + math.random() * 0.1), k == "esforco" and 1.2 or nil)
			end
		end
	end
end

local estado = {}                      -- [modelo] = {[track] = ultimaFase}
-- nome logico da trilha: o servidor publica MapaTrilhas (nome -> AnimationId); o nome nao replica
local function nomeTrilha(m, t)
	local id = t.Animation and t.Animation.AnimationId or ""
	local mapa = m:FindFirstChild("MapaTrilhas")
	-- um mesmo clipe pode servir a varios nomes (apelidos: Andar/Giro_E/Correr...): prefere um nome que tenha som
	local achado
	if mapa then for _, sv in ipairs(mapa:GetChildren()) do
		if sv.Value == id or sv.Value:find(id, 1, true) or id:find(sv.Value, 1, true) then
			if ASAS[sv.Name] or PASSOS[sv.Name] or VOZ[sv.Name] then return sv.Name end
			achado = achado or sv.Name
		end
	end end
	return achado or (t.Animation and t.Animation.Name or "")
end
local function dragoes()
	local l = {}
	for _, m in ipairs(workspace:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("FormaRegional") and m.PrimaryPart and m:FindFirstChildOfClass("AnimationController") then table.insert(l, m) end
	end
	return l
end
local acc = 0
RunService.Heartbeat:Connect(function(dt)
	acc += dt; if acc < 1 / 30 then return end; acc = 0
	for _, m in ipairs(dragoes()) do
		local pp = m.PrimaryPart
		if (pp.Position - cam.CFrame.Position).Magnitude > Cfg.distMax then continue end
		local an = m:FindFirstChildOfClass("AnimationController"):FindFirstChildOfClass("Animator"); if not an then continue end
		local st = estado[m] or {}; estado[m] = st
		local asaJa = false
		for _, t in ipairs(an:GetPlayingAnimationTracks()) do
			local nome = nomeTrilha(m, t)
			local fases = ASAS[nome] or PASSOS[nome] or VOZF[nome]
			if fases and t.Length > 0 and t.WeightCurrent > 0.3 then
				local f = (t.TimePosition / t.Length) % 1
				local ant = st[t]
				if ant then
					for _, alvo in ipairs(fases) do
						local passou = (ant < alvo and f >= alvo) or (f < ant and (alvo > ant or alvo <= f))   -- cruzou (inclusive na volta do laco)
						if passou then
							if ASAS[nome] and not asaJa then
								asaJa = true                                   -- mistura de varias trilhas de voo: 1 batida
								tocar(pp, sorteia(Cfg.asa), Cfg.asaVolume * math.clamp(t.WeightCurrent, 0.4, 1), faixa(Cfg.asaTom))
							elseif PASSOS[nome] and not m:GetAttribute("NoAr") then
								tocar(pp, sorteia(Cfg.passo), Cfg.passoVolume, faixa(Cfg.passoTom))
								tocar(pp, Cfg.passoPeso, Cfg.passoPesoVolume * (nome == "Correr" and 1.4 or 1), 0.9 + math.random() * 0.2, Cfg.passoPesoCorte)
							elseif VOZ[nome] then
								tocarVoz(m, pp, nome, alvo)
							end
						end
					end
				end
				st[t] = f
			else st[t] = nil end
		end
	end
end)

-- respiracao grave e discreta (intervalos irregulares); depois de correr/voar fica mais frequente por ~20 s
local esforcoAte, proxRespiro = {}, {}
task.spawn(function()
	while true do
		task.wait(1)
		for _, m in ipairs(dragoes()) do
			local pp = m.PrimaryPart
			if (pp.Position - cam.CFrame.Position).Magnitude > 120 then continue end
			local modo = m:GetAttribute("MontariaModo")
			if modo == "voo" or m:GetAttribute("NoAr") or m:GetAttribute("EmAtaque") then esforcoAte[m] = os.clock() + 20; continue end
			local cansado = (esforcoAte[m] or 0) > os.clock()
			local prox = proxRespiro[m]
			if not prox then
				local a, b = Cfg.respiroIntervalo[1], Cfg.respiroIntervalo[2]
				proxRespiro[m] = os.clock() + (cansado and a * 0.5 or a) + math.random() * (b - a)
			elseif os.clock() >= prox then
				proxRespiro[m] = nil
				tocar(pp, Cfg.respiro, Cfg.respiroVolume * (cansado and 1.4 or 1), faixa(Cfg.respiroTom), 1.8)
			end
		end
	end
end)

-- Mordida Aerea: avanco (whoosh) no inicio, mordida no fechar da boca, estalo forte se acertar
local ligados = {}
local function ligar(m)
	if ligados[m] or not (m:IsA("Model") and m:GetAttribute("FormaRegional")) then return end
	ligados[m] = true
	m:GetAttributeChangedSignal("EmAtaque"):Connect(function()
		if m:GetAttribute("EmAtaque") == "MordidaAerea" and m.PrimaryPart then
			task.delay(0.25, function() tocar(m.PrimaryPart, Cfg.avanco, 1.2, 0.85) end)
			task.delay(0.58, function() tocar(m.PrimaryPart, sorteia(Cfg.mordida), 1.3, faixa(Cfg.mordidaTom)) end)
		end
	end)
	m:GetAttributeChangedSignal("MordidaAcertou"):Connect(function()
		if m.PrimaryPart then tocar(m.PrimaryPart, sorteia(Cfg.mordida), 1.8, 0.6) end
	end)
end
for _, m in ipairs(workspace:GetChildren()) do ligar(m) end
workspace.ChildAdded:Connect(function(m) task.defer(ligar, m) end)

-- habilidades (eventos cosmeticos do servidor)
local FX = RS:WaitForChild("Combate_Dragoes"):WaitForChild("FX", 30)
if FX then
	FX.OnClientEvent:Connect(function(e)
		if type(e) ~= "table" or typeof(e.d) ~= "Instance" or not e.d.PrimaryPart then return end
		local pp = e.d.PrimaryPart; local h, f, el = e.hab, e.fase, e.el
		if h == "Sopro" and f == "emissao" then
			if el == "Fogo" then tocar(pp, Cfg.fogo, 1.4, 0.8); task.delay(0.9, function() tocar(pp, Cfg.fogo, 1.2, 0.75) end)
			elseif el == "Terra" then tocar(pp, Cfg.rochaArrasto, 1.2, 0.9)
			else tocar(pp, Cfg.ar, 1.3, 0.8) end
		elseif h == "Sopro" and f == "preparo" then tocar(pp, Cfg.rugido, 0.6, 1.15, 0.9)
		elseif h == "Sopro" and f == "projetil" then tocar(pp, Cfg.avanco, 0.7, 1.1)
		elseif h == "Arremetida" and f == "emissao" then tocar(pp, Cfg.avanco, 1.4, 0.75)
		elseif h == "Arremetida" and f == "impacto" then tocar(pp, Cfg.rocha, 1, 1, 0.6)
		elseif h == "Tempestade" and f == "impulso" then tocar(pp, sorteia(Cfg.asa), 1.6, 0.6); tocar(pp, Cfg.ar, 1.2, 0.7)
		elseif h == "Tempestade" and f == "batida" then                    -- cada batida real: asa + rajada (seguintes mais leves)
			local k = (e.indice or 1) == 1 and 1 or 0.65
			tocar(pp, sorteia(Cfg.asa), 1.6 * k, 0.6); tocar(pp, Cfg.ar, 1.2 * k, 0.7); if e.superficie then tocar(pp, Cfg.rochaArrasto, 0.6 * k, 0.9) end
		elseif h == "Tempestade" and f == "pouso" then tocar(pp, Cfg.rocha, 0.8, 1, 0.5)
		-- Coracao Infernal: carga (rosnado grave contido) -> lamina sai da boca (chama forte + rugido curto) -> silvos a cada
		-- meia volta da lamina (casados com a funcao de giro do servidor) -> impactos
		elseif h == "Coracao" and f == "carga" then tocar(pp, Cfg.esforco, 0.7, 0.7, 1.1); tocar(pp, Cfg.fogo, 0.5, 0.6)
		elseif h == "Coracao" and f == "lamina" then
			tocar(pp, Cfg.rugido, 1.0, 0.8, 1.2); tocar(pp, Cfg.fogo, 1.5, 0.75)
			local n = math.max(1, math.floor((e.voltas or 1) * 2))
			for i = 1, n do
				local k = (i - 0.5) / n                                       -- fracao do giro (velocidade maior no meio)
				task.delay((e.expele or 0.4) + (e.giro or 1.7) * k, function() if pp.Parent then tocar(pp, Cfg.avanco, 1.1, 0.7 + 0.1 * math.random()); tocar(pp, Cfg.fogo, 0.6, 0.9) end end)
			end
		elseif h == "Coracao" and f == "impacto" then tocar(pp, Cfg.impacto, 0.8, 0.85, Cfg.impactoCorte)
		elseif h == "SangueDeMagma" and f == "ativar" then tocar(pp, Cfg.esforco, 0.6, 0.65, 1.0)
		elseif h == "Ruptura" and f == "preparo" then tocar(pp, Cfg.rugido, 0.9, 0.9)
		elseif h == "Ruptura" and f == "impacto" then tocar(pp, Cfg.rocha, 1.6, 0.8); tocar(pp, Cfg.rochaArrasto, 1.2, 0.8)
		elseif h == "Mordida" and f == "preparo" then
			task.delay(0.5, function() tocar(pp, Cfg.garra, 0.5, 1.2) end)
		elseif h == "Mordida" and f == "impacto" then
			tocar(pp, sorteia(Cfg.mordida), e.acertou and 1.2 or 0.7, faixa(Cfg.mordidaTom))
			if e.acertou then tocar(pp, Cfg.impacto, 0.7, 0.8, Cfg.impactoCorte) end
		elseif h == "Garra" and f == "preparo" then
			if math.random() < 0.35 then tocar(pp, Cfg.esforco, Cfg.esforcoVolume, 0.8 + math.random() * 0.15, 1.0) end
			task.delay(0.45, function() tocar(pp, Cfg.garra, Cfg.garraVolume, 0.85 + math.random() * 0.1) end)
		elseif h == "Garra" and f == "impacto" and e.acertou then tocar(pp, Cfg.impacto, 0.8, 0.9, Cfg.impactoCorte)
		elseif h == "Cauda" and f == "impacto" then tocar(pp, Cfg.garra, 1.0, 0.7)
		elseif h == "Rugido" and f == "emissao" then tocar(pp, Cfg.rugido, 1.5, 0.95) end
	end)
end
