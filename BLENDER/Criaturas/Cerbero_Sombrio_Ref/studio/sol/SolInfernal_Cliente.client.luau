-- SolInfernal_Cliente (LocalScript em StarterPlayerScripts) - PROTOTIPO do Sol Infernal: tecla de teste + visual (26/11).
-- Tecla R perto do Cerbero: pede o lancamento (alvo sob o mouse ou ponto do mouse); o servidor decide tudo.
-- Visual (so no cliente, sem luz extra): nucleo Neon claro + chamas saindo da superficie + brilho + faiscas;
-- cresce com o atributo Escala durante a carga; explosao com clarao, chamas e faiscas; queimadura no alvo por 3 s.
-- Furia: atributo Roxo na bola -> fogo roxo de nucleo claro (mesmos numeros).
-- r3 (26/11): explosao com linguas no chao, fumaca e marca queimada (pedido: mais efeitos na colisao).
-- r2 (26/11): r1 saiu branca/estourada pelo Bloom -> nucleo laranja translucido, chamas maiores e menos brilhantes, clarao menor e laranja.
-- Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/sol/SolInfernal_Cliente.client.luau
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local UIS = game:GetService("UserInputService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local TS = game:GetService("TweenService")

local pasta = RS:WaitForChild("SolInfernal")
local C = require(pasta:WaitForChild("SolInfernal_Config"))
local Pedido = pasta:WaitForChild("Pedido")
local plr = Players.LocalPlayer
local mouse = plr:GetMouse()

local FOGO_TEX = "rbxasset://textures/particles/fire_main.dds"
local BRILHO_TEX = "rbxasset://textures/particles/sparkles_main.dds"

local PALETA = {
	[false] = {nucleo = Color3.fromRGB(255, 150, 45), c = {Color3.fromRGB(255, 232, 150), Color3.fromRGB(255, 140, 30), Color3.fromRGB(205, 50, 8), Color3.fromRGB(70, 10, 4)}},
	[true] = {nucleo = Color3.fromRGB(170, 80, 255), c = {Color3.fromRGB(232, 205, 255), Color3.fromRGB(180, 90, 255), Color3.fromRGB(112, 30, 222), Color3.fromRGB(40, 5, 80)}},
}
local function seqCor(p)
	return ColorSequence.new({ColorSequenceKeypoint.new(0, p.c[1]), ColorSequenceKeypoint.new(0.25, p.c[2]),
		ColorSequenceKeypoint.new(0.65, p.c[3]), ColorSequenceKeypoint.new(1, p.c[4])})
end

local pastaLocal = Instance.new("Folder"); pastaLocal.Name = "SolInfernal_Local"; pastaLocal.Parent = workspace

local function peca(nome, forma, tam)
	local p = Instance.new("Part")
	p.Name = nome; p.Shape = forma; p.Size = tam
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Material = Enum.Material.Neon
	return p
end

local function emissor(pai, t)
	local e = Instance.new("ParticleEmitter")
	for k, v in pairs(t) do e[k] = v end
	e.LightInfluence = 0
	e.Parent = pai
	return e
end

local function escalarSeq(base, f)
	local ks = {}
	for _, k in ipairs(base.Keypoints) do table.insert(ks, NumberSequenceKeypoint.new(k.Time, k.Value * f, k.Envelope * f)) end
	return NumberSequence.new(ks)
end

-- ===== bola =====
local function montarBola(bolaServ)
	local roxo = bolaServ:GetAttribute("Roxo") == true
	local R = bolaServ:GetAttribute("Raio") or C.RaioVisual
	local pal = PALETA[roxo]
	local cor = seqCor(pal)

	local nucleo = peca("Nucleo", Enum.PartType.Ball, Vector3.one)
	nucleo.Color = pal.nucleo; nucleo.Transparency = 0.35; nucleo.Parent = pastaLocal
	local casca = peca("Casca", Enum.PartType.Ball, Vector3.one)
	casca.Transparency = 1; casca.Parent = pastaLocal

	local tamChama = NumberSequence.new({NumberSequenceKeypoint.new(0, R * 0.55), NumberSequenceKeypoint.new(0.45, R * 0.7), NumberSequenceKeypoint.new(1, R * 0.15)})
	local tamBrilho = NumberSequence.new({NumberSequenceKeypoint.new(0, R * 2.1), NumberSequenceKeypoint.new(1, R * 2.4)})
	local chamas = emissor(casca, {Name = "Chamas", Texture = FOGO_TEX, Color = cor, LightEmission = 0.8, Brightness = 1.8,
		Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface, ShapeInOut = Enum.ParticleEmitterShapeInOut.Outward,
		Rate = 90, Lifetime = NumberRange.new(0.35, 0.6), Speed = NumberRange.new(2, 5), Size = tamChama,
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.35), NumberSequenceKeypoint.new(0.6, 0.4), NumberSequenceKeypoint.new(1, 1)}),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-90, 90), ZOffset = 1})
	local brilho = emissor(nucleo, {Name = "Brilho", Texture = BRILHO_TEX, Color = ColorSequence.new(pal.c[2]), LightEmission = 0.6, Brightness = 0.8,
		Rate = 8, Lifetime = NumberRange.new(0.3, 0.4), Speed = NumberRange.new(0), Size = tamBrilho,
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.85), NumberSequenceKeypoint.new(1, 1)}), LockedToPart = true, ZOffset = -1})
	local faiscas = emissor(casca, {Name = "Faiscas", Texture = BRILHO_TEX, Color = ColorSequence.new(pal.c[1], pal.c[2]), LightEmission = 1, Brightness = 3,
		Shape = Enum.ParticleEmitterShape.Sphere, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface, ShapeInOut = Enum.ParticleEmitterShapeInOut.Outward,
		Rate = 25, Lifetime = NumberRange.new(0.6, 1), Speed = NumberRange.new(6, 12), Drag = 1, Acceleration = Vector3.new(0, -6, 0),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.7), NumberSequenceKeypoint.new(1, 0)})})

	local v = {serv = bolaServ, nucleo = nucleo, casca = casca, emissores = {
		{chamas, tamChama, 90}, {brilho, tamBrilho, 8}, {faiscas, faiscas.Size, 25}}, esc = -1, pos = bolaServ.Position}

	local function aplicarEscala(e)
		e = math.max(e, 0.06)
		v.esc = e
		nucleo.Size = Vector3.one * (R * 0.9 * e)
		casca.Size = Vector3.one * (R * 1.7 * e)
		for _, it in ipairs(v.emissores) do
			local em, base, taxa = it[1], it[2], it[3]
			em.Size = escalarSeq(base, e)
			em.Rate = taxa * math.max(e, 0.3)
		end
	end
	aplicarEscala(bolaServ:GetAttribute("Escala") or 0)

	local con
	con = Run.RenderStepped:Connect(function(dt)
		if not bolaServ.Parent then
			con:Disconnect()
			for _, it in ipairs(v.emissores) do it[1].Enabled = false end
			nucleo.Transparency = 1
			Debris:AddItem(nucleo, 1.2); Debris:AddItem(casca, 1.2)
			return
		end
		local e = bolaServ:GetAttribute("Escala") or 1
		if math.abs(e - v.esc) >= 0.04 then aplicarEscala(e) end
		v.pos = v.pos:Lerp(bolaServ.Position, math.clamp(dt * 18, 0, 1))
		local cf = CFrame.new(v.pos) * CFrame.Angles(0, os.clock() * 1.5, 0)
		nucleo.CFrame = cf; casca.CFrame = cf
		nucleo.Transparency = 0.35 + 0.08 * math.sin(os.clock() * 14)
	end)
end

local vfx = workspace:WaitForChild("VFX_SolInfernal", 30)
if vfx then
	vfx.ChildAdded:Connect(function(c) if c.Name == "SolInfernal_Bola" then task.defer(montarBola, c) end end)
	for _, c in ipairs(vfx:GetChildren()) do if c.Name == "SolInfernal_Bola" then montarBola(c) end end
end

-- ===== explosao (r3, 26/11: mais efeitos na colisao, como a explosao aprovada no Blender r3/r3b) =====
-- massa de fogo que abre + clarao + faiscas + linguas de fogo no chao + fumaca subindo + marca queimada com brasas (some em ~5 s).
-- Sem luz extra. Particulas de pico ~200 por explosao (curtas).
local SMOKE_TEX = "rbxasset://textures/particles/smoke_main.dds"
local paramsChao = RaycastParams.new()
paramsChao.FilterType = Enum.RaycastFilterType.Exclude
pasta:WaitForChild("Explodiu").OnClientEvent:Connect(function(pos, roxo, raio)
	local pal = PALETA[roxo == true]
	-- 1) clarao
	local clarao = peca("Clarao", Enum.PartType.Ball, Vector3.one * 2)
	clarao.Color = pal.c[2]; clarao.Transparency = 0.45; clarao.CFrame = CFrame.new(pos); clarao.Parent = pastaLocal
	TS:Create(clarao, TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = Vector3.one * raio * 1.4}):Play()
	TS:Create(clarao, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Transparency = 1}):Play()
	-- 2) massa de fogo que abre + faiscas
	local base = peca("Explosao", Enum.PartType.Block, Vector3.one * 4)
	base.Transparency = 1; base.CFrame = CFrame.new(pos); base.Parent = pastaLocal
	local fogo = emissor(base, {Texture = FOGO_TEX, Color = seqCor(pal), LightEmission = 0.8, Brightness = 1.8, Enabled = false,
		Lifetime = NumberRange.new(0.5, 1.0), Speed = NumberRange.new(14, 32), SpreadAngle = Vector2.new(180, 180), Drag = 3,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 6), NumberSequenceKeypoint.new(0.4, 8), NumberSequenceKeypoint.new(1, 1.5)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1)}),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-120, 120)})
	local faisca = emissor(base, {Texture = BRILHO_TEX, Color = ColorSequence.new(pal.c[1], pal.c[2]), LightEmission = 1, Brightness = 3, Enabled = false,
		Lifetime = NumberRange.new(0.8, 1.6), Speed = NumberRange.new(25, 50), SpreadAngle = Vector2.new(180, 180), Drag = 1.5,
		Acceleration = Vector3.new(0, -24, 0), Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.9), NumberSequenceKeypoint.new(1, 0)})})
	fogo:Emit(90); faisca:Emit(70)
	Debris:AddItem(clarao, 0.6); Debris:AddItem(base, 2)
	-- 3) chao embaixo da explosao (ate 30 studs): linguas de fogo, fumaca e marca queimada
	paramsChao.FilterDescendantsInstances = {pastaLocal, workspace:FindFirstChild("VFX_SolInfernal"), plr.Character}
	local hit = workspace:Raycast(pos + Vector3.new(0, 2, 0), Vector3.new(0, -32, 0), paramsChao)
	local chao = hit and hit.Position or (pos - Vector3.new(0, math.min(pos.Y, 20), 0))
	local largura = raio * 1.5
	local disco = peca("Linguas", Enum.PartType.Block, Vector3.new(largura, 0.4, largura))
	disco.Transparency = 1; disco.CFrame = CFrame.new(chao + Vector3.new(0, 0.3, 0)); disco.Parent = pastaLocal
	local linguas = emissor(disco, {Texture = FOGO_TEX, Color = seqCor(pal), LightEmission = 0.8, Brightness = 1.8,
		EmissionDirection = Enum.NormalId.Top, Orientation = Enum.ParticleOrientation.VelocityParallel,
		Squash = NumberSequence.new({NumberSequenceKeypoint.new(0, -0.5), NumberSequenceKeypoint.new(0.5, -1.3), NumberSequenceKeypoint.new(1, -0.6)}),
		Rate = 45, Lifetime = NumberRange.new(0.5, 0.9), Speed = NumberRange.new(6, 13), SpreadAngle = Vector2.new(12, 12),
		Acceleration = Vector3.new(0, 8, 0), Drag = 1,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 2.2), NumberSequenceKeypoint.new(0.4, 3.2), NumberSequenceKeypoint.new(1, 0.6)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.3), NumberSequenceKeypoint.new(0.7, 0.4), NumberSequenceKeypoint.new(1, 1)})})
	linguas:Emit(30)
	local fumaca = emissor(disco, {Texture = SMOKE_TEX, Color = ColorSequence.new(Color3.fromRGB(70, 52, 44), Color3.fromRGB(32, 28, 28)),
		LightEmission = 0, Rate = 10, Lifetime = NumberRange.new(2, 3), Speed = NumberRange.new(4, 8), EmissionDirection = Enum.NormalId.Top,
		SpreadAngle = Vector2.new(25, 25), Acceleration = Vector3.new(0, 2, 0), Drag = 0.6,
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 5), NumberSequenceKeypoint.new(1, 14)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(0.6, 0.75), NumberSequenceKeypoint.new(1, 1)})})
	fumaca.LightInfluence = 1
	fumaca:Emit(8)
	task.delay(1.1, function() linguas.Enabled = false end)
	task.delay(1.6, function() fumaca.Enabled = false end)
	Debris:AddItem(disco, 5)
	-- marca queimada com brasas
	local marca = Instance.new("Part")
	marca.Name = "Marca"; marca.Shape = Enum.PartType.Cylinder; marca.Size = Vector3.new(0.12, raio * 1.6, raio * 1.6)
	marca.Anchored = true; marca.CanCollide = false; marca.CanQuery = false; marca.CanTouch = false; marca.CastShadow = false
	marca.Material = Enum.Material.Slate; marca.Color = Color3.fromRGB(22, 14, 12); marca.Transparency = 0.15
	marca.CFrame = CFrame.new(chao + Vector3.new(0, 0.07, 0)) * CFrame.Angles(0, 0, math.rad(90)); marca.Parent = pastaLocal
	local brasas = emissor(marca, {Texture = BRILHO_TEX, Color = ColorSequence.new(pal.c[2], pal.c[3]), LightEmission = 1, Brightness = 2,
		Rate = 14, Lifetime = NumberRange.new(0.6, 1.2), Speed = NumberRange.new(0.5, 2), EmissionDirection = Enum.NormalId.Right,
		Acceleration = Vector3.new(0, 3, 0), Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.5), NumberSequenceKeypoint.new(1, 0)})})
	task.delay(3, function() brasas.Enabled = false end)
	task.delay(3.5, function() TS:Create(marca, TweenInfo.new(1.5), {Transparency = 1}):Play() end)
	Debris:AddItem(marca, 5.2)
end)

-- ===== queimadura no alvo =====
pasta:WaitForChild("Queima").OnClientEvent:Connect(function(modelo, dur, roxo)
	local raiz = modelo and (modelo:FindFirstChild("HumanoidRootPart") or modelo.PrimaryPart)
	if not raiz then return end
	local pal = PALETA[roxo == true]
	local e = emissor(raiz, {Name = "SolQueima", Texture = FOGO_TEX, Color = seqCor(pal), LightEmission = 1, Brightness = 2,
		Rate = 22, Lifetime = NumberRange.new(0.4, 0.6), Speed = NumberRange.new(2, 4), Acceleration = Vector3.new(0, 6, 0),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 2), NumberSequenceKeypoint.new(1, 0.4)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.3), NumberSequenceKeypoint.new(1, 1)})})
	task.delay(dur, function() e.Enabled = false; Debris:AddItem(e, 1) end)
end)

-- ===== tecla de teste =====
UIS.InputBegan:Connect(function(inp, gpe)
	if gpe or inp.KeyCode ~= Enum.KeyCode.R then return end
	Pedido:FireServer(mouse.Target, mouse.Hit and mouse.Hit.Position or nil)
end)
