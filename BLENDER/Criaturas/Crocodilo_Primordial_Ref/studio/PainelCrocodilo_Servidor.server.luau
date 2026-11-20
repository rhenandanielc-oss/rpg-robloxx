-- 20/11 PAINEL DE TESTE do Crocodilo Primordial (usuario: "libere tudo, quero testar os poderes e a montaria, e deixe
-- uma criatura viva"). SO PARA O PLACE DE TESTE. O cliente so PEDE; o servidor valida (acao conhecida, recarga curta,
-- crocodilo sem cavaleiro) e chama o piloto PoderesTeste (mesma instancia do modulo que a montaria usa).
-- Cria tambem a Presa_Viva: criatura de teste que anda sozinha pela arena e renasce 6 s depois de morrer.
local SS, RepS, Players, RS = game:GetService("ServerStorage"), game:GetService("ReplicatedStorage"), game:GetService("Players"), game:GetService("RunService")
local M = require(SS:WaitForChild("Crocodilo_Piloto"):WaitForChild("PoderesTeste"))
local pasta = workspace:WaitForChild("Teste_Crocodilo")
local arena = pasta:WaitForChild("Arena")
local modelo = pasta:WaitForChild("Crocodilo_Primordial")

local ev = RepS:FindFirstChild("PainelCrocodilo") or Instance.new("RemoteEvent")
ev.Name = "PainelCrocodilo"; ev.Parent = RepS
local function avisar(plr, t) ev:FireClient(plr, "msg", t); print("[PainelCrocodilo] " .. plr.Name .. ": " .. t) end

-- ===================================================================== Presa viva
local AREA, RAIO = Vector3.new(-300, 0, -335), 22          -- terra firme na frente do crocodilo (a agua real e o Canal ao sul)
local BLOQ = {"Agarrado", "Caido", "Derrubado", "Incapacitado"}
local presa
local function pontoAleatorio()
	local a, r = math.random() * math.pi * 2, math.sqrt(math.random()) * RAIO
	return AREA + Vector3.new(math.cos(a) * r, 0, math.sin(a) * r)
end
local function parte(m, nome, tam, cor, cf, hrp)
	local p = Instance.new("Part"); p.Name = nome; p.Size = tam; p.Color = cor; p.Material = Enum.Material.SmoothPlastic
	p.CanCollide = false; p.Massless = true; p.CFrame = hrp.CFrame * cf; p.Parent = m
	local w = Instance.new("WeldConstraint"); w.Part0 = hrp; w.Part1 = p; w.Parent = p
	return p
end
local function criarPresa()
	local m = Instance.new("Model"); m.Name = "Presa_Viva"
	local pos = pontoAleatorio()
	local hrp = Instance.new("Part"); hrp.Name = "HumanoidRootPart"; hrp.Size = Vector3.new(2, 2, 3); hrp.Transparency = 1
	hrp.CFrame = CFrame.new(pos + Vector3.new(0, 2.5, 0)); hrp.Parent = m; m.PrimaryPart = hrp
	local marrom = Color3.fromRGB(122, 92, 62)
	parte(m, "Corpo", Vector3.new(2.2, 1.9, 3.6), marrom, CFrame.new(0, 0.2, 0), hrp)
	parte(m, "Head", Vector3.new(1.4, 1.3, 1.5), marrom, CFrame.new(0, 0.7, -2.2), hrp)
	for i, xz in ipairs({{-0.7, -1.2}, {0.7, -1.2}, {-0.7, 1.2}, {0.7, 1.2}}) do
		parte(m, "Pata" .. i, Vector3.new(0.5, 1.2, 0.5), Color3.fromRGB(90, 68, 46), CFrame.new(xz[1], -1.1, xz[2]), hrp)
	end
	local h = Instance.new("Humanoid"); h.RigType = Enum.HumanoidRigType.R15; h.HipHeight = 1.7; h.WalkSpeed = 8
	h.BreakJointsOnDeath = false; h.MaxHealth = 100; h.Health = 100
	h.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.Viewer; h.Parent = m
	m:SetAttribute("BonecoTeste", true); m:SetAttribute("PosicaoInicial", pos)
	m.Parent = arena; hrp:SetNetworkOwner(nil)
	h.Died:Connect(function()
		print("[PainelCrocodilo] Presa_Viva morreu; renasce em 6 s")
		task.delay(6, function() if presa == m then m:Destroy(); presa = criarPresa() end end)
	end)
	print("[PainelCrocodilo] Presa_Viva criada em " .. tostring(pos))
	return m
end
presa = criarPresa()
-- 20/11: presa FIRME (sem fisica) enquanto o crocodilo ataca perto, presa na boca ou caida. Antes ela tinha fisica e o
-- corpo do crocodilo, ao se ajustar na mordida, a arremessava longe ("a presa sumiu, evaporou"). Solta 0,4 s depois.
task.spawn(function()
	local livreDesde = 0
	while true do
		task.wait(0.1)
		local m = presa; local hrp = m and m.Parent and m.PrimaryPart
		if hrp then
			local perto = (hrp.Position - modelo:GetPivot().Position).Magnitude < 30
			local preso = ((M.estado().poder ~= nil or modelo:GetAttribute("Virando")) and perto) or m:GetAttribute("Agarrado") or m:GetAttribute("Caido")
			if preso then
				livreDesde = os.clock()
				if not hrp.Anchored then hrp.AssemblyLinearVelocity = Vector3.zero; hrp.Anchored = true end
			elseif hrp.Anchored and os.clock() - livreDesde > 0.4 then
				local cf = m:GetPivot(); local _, ry = cf:ToOrientation()          -- volta de pe
				m:PivotTo(CFrame.new(cf.Position.X, math.max(cf.Position.Y, 2.7), cf.Position.Z) * CFrame.Angles(0, ry, 0))
				hrp.Anchored = false
			end
		end
	end
end)
task.spawn(function()                                      -- passeia: novo destino a cada 3-6 s (pausa quando presa/caida)
	while true do
		task.wait(3 + math.random() * 3)
		local m = presa; local h = m and m.Parent and m:FindFirstChildOfClass("Humanoid"); local hrp = m and m.PrimaryPart
		if h and hrp and h.Health > 0 and not hrp.Anchored then
			local livre = true
			for _, a in ipairs(BLOQ) do if m:GetAttribute(a) then livre = false end end
			if livre then h:MoveTo(pontoAleatorio()) end
		end
	end
end)

-- ===================================================================== Acoes do painel
local function cabeca()
	local cf = modelo:GetPivot(); return cf.Position + cf.LookVector * 7, cf
end
local function presaMaisPerto(raio)
	local cab = cabeca(); local melhor, dm = nil, raio
	for _, a in ipairs(arena:GetChildren()) do
		local h = a:FindFirstChildOfClass("Humanoid"); local p = a.PrimaryPart or a:FindFirstChild("HumanoidRootPart")
		if a:GetAttribute("BonecoTeste") and h and h.Health > 0 and p then
			local d = (Vector3.new(p.Position.X, 0, p.Position.Z) - Vector3.new(cab.X, 0, cab.Z)).Magnitude
			if d < dm then melhor, dm = a, d end
		end
	end
	return melhor, dm
end
local CFG = require(SS.Crocodilo_Piloto:WaitForChild("ConfigPoderes_Teste"))
local function angulo(a)                                    -- graus da presa em relacao a frente do crocodilo
	local p = (a.PrimaryPart or a:FindFirstChild("HumanoidRootPart")).Position
	local l = modelo:GetPivot():PointToObjectSpace(p); return math.deg(math.atan2(-l.X, -l.Z))
end
local function bonecosDePe()
	for _, a in ipairs(arena:GetChildren()) do
		local h = a:FindFirstChildOfClass("Humanoid"); local orig = a:GetAttribute("PosicaoInicial")
		if a:GetAttribute("BonecoTeste") and h and a ~= presa and not a:GetAttribute("Agarrado") then
			for _, n in ipairs({"Caido", "CaidoAte", "Derrubado", "Incapacitado", "LentidaoAte", "Mancando", "ImuneAgarraoAte"}) do a:SetAttribute(n, nil) end
			h.Health = h.MaxHealth
			if typeof(orig) == "Vector3" then a:PivotTo(CFrame.new(orig)) end
		end
	end
	if presa and presa.Parent then local h = presa:FindFirstChildOfClass("Humanoid"); if h and h.Health > 0 then h.Health = h.MaxHealth end end
end

local ACOES = {}
ACOES.agarrao = function(plr)
	local a, d = presaMaisPerto(18)
	if not a then return "Nenhuma presa a ate 18 studs da cabeca. Leve o crocodilo para perto (montado) e desca." end
	local virou = ""                                          -- 20/11: fora da frente, vira com as patas antes (sem estalo)
	if math.abs(angulo(a)) > CFG.Agarrao.cone_virar then virou = " | " .. tostring(M.virarPara(a, 8)) end
	local cena = M.estado().naAgua and "agua" or "terra"
	return string.format("Mordida de Agarrao em %s (%.0f studs, %.0f graus, %s): %s%s", a.Name, d, angulo(a), cena, tostring(M.agarrao(a, cena)), virou)
end
ACOES.emboscada = function() return "Emboscada: " .. tostring(M.emboscada()) end
ACOES.submersao = function() return "Submersao: " .. tostring(M.submersao((not M.estado().naAgua) and "terra" or nil)) end
ACOES.cauda = function() return "Cauda de Mare: " .. tostring(M.caudaDeMare()) end
ACOES.virar = function()
	local a = presaMaisPerto(60); if not a then return "Nenhuma presa a ate 60 studs" end
	return a.Name .. ": " .. tostring(M.virarPara(a, 3))
end
ACOES.cancelar = function() return "Cancelar: " .. tostring(M.cancelar("painel")) end
ACOES.bonecos = function() bonecosDePe(); return "Bonecos de pe e curados" end
ACOES.ir = function(plr)
	local hrp = plr.Character and plr.Character:FindFirstChild("HumanoidRootPart"); if not hrp then return "sem personagem" end
	local cf = modelo:GetPivot(); hrp.CFrame = CFrame.lookAt(cf.Position - cf.RightVector * 9 + Vector3.new(0, 3, 0), cf.Position)
	return "Levado para o lado do crocodilo"
end
local SEM_MONTARIA = {agarrao = true, emboscada = true, submersao = true, cauda = true, virar = true}
local recarga = {}
ev.OnServerEvent:Connect(function(plr, acao)
	if type(acao) ~= "string" or not ACOES[acao] then return end
	local t = os.clock(); if recarga[plr] and t - recarga[plr] < 0.4 then return end; recarga[plr] = t
	local fase = modelo:GetAttribute("FaseMontaria")
	if SEM_MONTARIA[acao] and fase and fase ~= "livre" then
		avisar(plr, "Desca do crocodilo (tecla E) para usar os poderes: poderes montado ainda nao foram decididos."); return
	end
	local ok, r = pcall(ACOES[acao], plr)
	avisar(plr, ok and tostring(r) or ("erro: " .. tostring(r)))
end)

local function entrou(plr)
	if not modelo:GetAttribute("DonoUserId") then modelo:SetAttribute("DonoUserId", plr.UserId) end   -- Sentido de Vibracao mostra ao dono
	local function nasceu(ch)                                  -- nasce ao lado do crocodilo (o SpawnLocation fica longe, nos dragoes)
		local hrp = ch:WaitForChild("HumanoidRootPart", 10); task.wait(0.3)
		if hrp then ACOES.ir(plr) end
	end
	plr.CharacterAdded:Connect(nasceu)
	if plr.Character then task.spawn(nasceu, plr.Character) end
end
Players.PlayerAdded:Connect(entrou)
for _, p in ipairs(Players:GetPlayers()) do task.spawn(entrou, p) end
print("[PainelCrocodilo] pronto: teclas 1-4 poderes, R virar, X cancelar; Presa_Viva na arena")
