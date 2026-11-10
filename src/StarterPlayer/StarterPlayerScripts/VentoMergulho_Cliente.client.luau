-- VentoMergulho_Cliente (LocalScript, StarterPlayerScripts) — PATCH_MERGULHO_PICADO (10/11, TESTE, NAO_APROVADO).
-- Vento das batidas de asa no chao durante o FREIO do mergulho de bico (e na recuperacao logo depois), "como o
-- deslocamento de ar de um helicoptero" (direcao textual do usuario; nada de helice). So visual e so no cliente; vale
-- para qualquer dragao com o atributo MergulhoFase (o do jogador e o de outros jogadores).
-- Cada batida (periodo do Pairar no ritmo do freio) solta, com o atraso do ar descendo ate o piso, um anel de ar rente
-- a superficie que se espalha para fora (particulas transparentes, sem disco solido). Poeira leve SO em material solto
-- (terra, areia, lama, neve, grama = fiapos finos) com a cor do proprio material; agua = spray baixo; piso limpo/rocha/
-- madeira/pedra = so o ar. Sem superficie a ate ALCANCE studs abaixo do corpo: nada. Nao move nem danifica nada.
-- LOD: longe da camera nada; distancia media = metade das particulas. Uma peca invisivel por dragao, reaproveitada.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

local Cfg = require(RS:WaitForChild("Montaria_Dragoes"):WaitForChild("ConfigMontaria"))
local MP = Cfg.mergulhoPicado
if not MP then return end

local V = {
	alcance = 38,                                  -- studs do ponto mais baixo do corpo ate o piso
	periodo = 1.0 / (MP.ritmoFreio or 1.8),        -- Pairar: 4 batidas em 4 s no ritmo 1 -> 1 s por batida
	atrasoBase = 0.08, vAr = 70,                   -- atraso = base + distancia / velocidade do ar descendo
	raioAnel = 10, emissores = 10,               -- (10/11) anel maior: com 4 o ar ficava escondido sob as asas (~50 studs)
	lodLonge = 450, lodMedio = 220,
	textura = "rbxasset://textures/particles/smoke_main.dds",
}
local SOLTO = {                                    -- material -> {qtd por batida, transparencia inicial}
	[Enum.Material.Sand] = {6, 0.55}, [Enum.Material.Ground] = {5, 0.6}, [Enum.Material.Mud] = {3, 0.7},
	[Enum.Material.Snow] = {8, 0.45}, [Enum.Material.Grass] = {2, 0.8}, [Enum.Material.LeafyGrass] = {2, 0.8},
	[Enum.Material.Sandstone] = {2, 0.75}, [Enum.Material.Salt] = {4, 0.6},
}

local pasta = workspace:FindFirstChild("VFX_Temporarios")
if not pasta then pasta = Instance.new("Folder"); pasta.Name = "VFX_Temporarios"; pasta.Parent = workspace end

local function emissor(pai, nome, props)
	local e = Instance.new("ParticleEmitter"); e.Name = nome; e.Enabled = false; e.Texture = V.textura
	e.LightInfluence = 1; e.LightEmission = 0; e.Rate = 0
	for k, v in pairs(props) do e[k] = v end
	e.Parent = pai; return e
end

local function criarPeca(m)
	local p = Instance.new("Part"); p.Name = "VentoChao_" .. m.Name; p.Anchored = true; p.CanCollide = false; p.CanQuery = false
	p.CanTouch = false; p.Transparency = 1; p.Size = Vector3.one; p.CastShadow = false
	local anel = {}
	for i = 1, V.emissores do
		local a = Instance.new("Attachment"); a.Name = "Ar" .. i
		local ang = (i - 1) / V.emissores * math.pi * 2
		local dir = Vector3.new(math.cos(ang), 0, math.sin(ang))
		a.CFrame = CFrame.lookAt(dir * V.raioAnel + Vector3.yAxis * 1, dir * (V.raioAnel + 1) + Vector3.yAxis * 1)   -- Front = para fora
		a.Parent = p
		local ar = emissor(a, "Ar", {EmissionDirection = Enum.NormalId.Front, SpreadAngle = Vector2.new(14, 5),
			Speed = NumberRange.new(55, 75), Drag = 1.6, Lifetime = NumberRange.new(0.9, 1.4), Acceleration = Vector3.new(0, 3, 0),
			Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 4), NumberSequenceKeypoint.new(1, 14)}),
			Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.7), NumberSequenceKeypoint.new(0.5, 0.8), NumberSequenceKeypoint.new(1, 1)}),
			Color = ColorSequence.new(Color3.fromRGB(232, 236, 240)), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-40, 40)})
		local po = emissor(a, "Poeira", {EmissionDirection = Enum.NormalId.Front, SpreadAngle = Vector2.new(18, 10),
			Speed = NumberRange.new(30, 50), Drag = 1.8, Lifetime = NumberRange.new(1.0, 1.6), Acceleration = Vector3.new(0, 1.5, 0),
			Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 2), NumberSequenceKeypoint.new(1, 9)}),
			Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-25, 25)})
		local sp = emissor(a, "Spray", {EmissionDirection = Enum.NormalId.Front, SpreadAngle = Vector2.new(10, 18),
			Speed = NumberRange.new(25, 40), Drag = 1.2, Lifetime = NumberRange.new(0.5, 0.8), Acceleration = Vector3.new(0, -40, 0),
			Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.8), NumberSequenceKeypoint.new(1, 2.4)}),
			Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.45), NumberSequenceKeypoint.new(1, 1)}),
			Color = ColorSequence.new(Color3.fromRGB(235, 245, 250))})
		anel[i] = {ar = ar, po = po, sp = sp}
	end
	p.Parent = pasta
	return {peca = p, anel = anel}
end

local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.IgnoreWater = false
local dados = {}                                     -- [modelo] = {fx, proxBatida, ossos}
local function pontoBaixo(m, d)
	if not d.ossos then
		d.ossos = {}
		for _, b in ipairs(m:GetDescendants()) do
			if b:IsA("Bone") and (b.Name == "mouth_upper_tip" or b.Name == "wing_tip_l" or b.Name == "wing_tip_r" or b.Name == "Quadril") then table.insert(d.ossos, b) end
		end
	end
	local menor = m:GetPivot().Position
	for _, b in ipairs(d.ossos) do local q = b.TransformedWorldCFrame.Position; if q.Y < menor.Y then menor = q end end
	return menor
end

local function batida(m, d)
	local pv = m:GetPivot().Position
	local baixo = Vector3.new(pv.X, pontoBaixo(m, d).Y, pv.Z)                -- sob o CENTRO do corpo, na altura do ponto mais baixo
	local ex = {m, pasta}; for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(ex, pl.Character) end end
	rp.FilterDescendantsInstances = ex
	local h = workspace:Raycast(baixo, Vector3.new(0, -V.alcance, 0), rp)
	if not h then return end                                                  -- sem superficie perto: sem vento
	local cam = workspace.CurrentCamera
	local dc = cam and (cam.CFrame.Position - h.Position).Magnitude or 0
	if dc > V.lodLonge then return end
	local lod = dc > V.lodMedio and 0.5 or 1
	local dist = (baixo - h.Position).Magnitude
	local k = math.clamp(1 - dist / V.alcance, 0.15, 1)                         -- mais perto = mais forte
	d.fx = d.fx or criarPeca(m)
	local n = h.Normal
	local giro = math.random() * math.pi * 2
	-- anel deitado no piso (Y local = normal da superficie; vale em rampa), girado ao acaso a cada batida
	local lado = n:Cross(Vector3.zAxis); if lado.Magnitude < 0.1 then lado = n:Cross(Vector3.xAxis) end
	local cf = CFrame.fromMatrix(h.Position, lado.Unit, n) * CFrame.Angles(0, giro, 0)
	local mat = h.Material
	local agua = mat == Enum.Material.Water
	local solto = SOLTO[mat]
	local corPo
	if solto then
		corPo = h.Instance:IsA("Terrain") and workspace.Terrain:GetMaterialColor(mat) or h.Instance.Color
		corPo = corPo:Lerp(Color3.fromRGB(205, 200, 190), 0.35)                  -- poeira e mais clara que o piso
	end
	task.delay(V.atrasoBase + dist / V.vAr, function()
		if not (d.fx and d.fx.peca.Parent) then return end
		d.fx.peca.CFrame = cf + n * 0.2
		for _, e in ipairs(d.fx.anel) do
			e.ar:Emit(math.max(1, math.floor((1 + 2 * k) * lod + 0.5)))
			if solto then
				e.po.Color = ColorSequence.new(corPo)
				e.po.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, solto[2] + (1 - solto[2]) * (1 - k) * 0.6), NumberSequenceKeypoint.new(1, 1)})
				local q = solto[1] * k * lod / 4
				if q >= 1 or math.random() < q then e.po:Emit(math.max(1, math.floor(q))) end
			elseif agua then
				if math.random() < 0.7 * k * lod then e.sp:Emit(math.max(1, math.floor(2 * k * lod))) end
			end
		end
	end)
end

local function limpar(m)
	local d = dados[m]; if not d then return end
	if d.fx then local p = d.fx.peca; task.delay(2, function() p:Destroy() end) end      -- deixa as ultimas particulas morrerem
	dados[m] = nil
end

local candidatos, ultVarredura = {}, 0                -- dragoes (FormaRegional) relidos a cada 1 s, nao o workspace todo por quadro
RunService.Heartbeat:Connect(function()
	if os.clock() - ultVarredura > 1 then
		ultVarredura = os.clock(); candidatos = {}
		for _, m in ipairs(workspace:GetChildren()) do if m:IsA("Model") and m:GetAttribute("FormaRegional") then table.insert(candidatos, m) end end
	end
	for _, m in ipairs(candidatos) do
		local fase = m.Parent and m:GetAttribute("MergulhoFase")
		if fase == "freio" or fase == "recuperacao" then
			local d = dados[m]
			if not d then d = {proxBatida = os.clock() + 0.05}; dados[m] = d end
			if os.clock() >= d.proxBatida then d.proxBatida = os.clock() + V.periodo; batida(m, d) end
		elseif dados[m] and not fase then limpar(m)
		elseif dados[m] then dados[m].proxBatida = os.clock() + 0.05 end   -- virada/queda: proxima batida no inicio do freio
	end
	for m in pairs(dados) do if not m.Parent then limpar(m) end end
end)
