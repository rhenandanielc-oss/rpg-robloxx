-- Investida_Cliente (LocalScript em StarterPlayerScripts) - PROTOTIPO da Investida Sombria: tecla de teste + visual (26/11).
-- Tecla E perto do Cerbero: investe na direcao do mouse; durante o boost a direcao segue o mouse (o servidor limita a curva).
-- Visual (sem luz extra): rastro escuro rente ao chao com brasas (some em 3 s), lufada de fogo na largada, faiscas e chamas
-- no impacto e nas 3 mordidas, faiscas na passagem por cima e na parede. Furia: brasas e fogo roxos.
-- Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/investida/Investida_Cliente.client.luau
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local TS = game:GetService("TweenService")

local pasta = RS:WaitForChild("InvestidaSombria")
local Pedido = pasta:WaitForChild("Pedido")
local Direcao = pasta:WaitForChild("Direcao")
local mouse = Players.LocalPlayer:GetMouse()

local FOGO_TEX = "rbxasset://textures/particles/fire_main.dds"
local BRILHO_TEX = "rbxasset://textures/particles/sparkles_main.dds"
local PALETA = {
	[false] = {c = {Color3.fromRGB(255, 232, 150), Color3.fromRGB(255, 140, 30), Color3.fromRGB(205, 50, 8), Color3.fromRGB(70, 10, 4)}},
	[true] = {c = {Color3.fromRGB(232, 205, 255), Color3.fromRGB(180, 90, 255), Color3.fromRGB(112, 30, 222), Color3.fromRGB(40, 5, 80)}},
}
local function seqCor(p)
	return ColorSequence.new({ColorSequenceKeypoint.new(0, p.c[1]), ColorSequenceKeypoint.new(0.25, p.c[2]),
		ColorSequenceKeypoint.new(0.65, p.c[3]), ColorSequenceKeypoint.new(1, p.c[4])})
end

local pastaLocal = Instance.new("Folder"); pastaLocal.Name = "Investida_Local"; pastaLocal.Parent = workspace

local function peca(nome, tam, cf)
	local p = Instance.new("Part")
	p.Name = nome; p.Size = tam; p.CFrame = cf
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Transparency = 1; p.Parent = pastaLocal
	return p
end
local function emissor(pai, t)
	local e = Instance.new("ParticleEmitter")
	for k, v in pairs(t) do e[k] = v end
	e.LightInfluence = 0
	e.Parent = pai
	return e
end
local function explosaoPequena(pos, roxo, nFogo, nFaisca, tam)
	local pal = PALETA[roxo == true]
	local b = peca("Estouro", Vector3.one * 2, CFrame.new(pos))
	local f = emissor(b, {Texture = FOGO_TEX, Color = seqCor(pal), LightEmission = 0.8, Brightness = 1.8, Enabled = false,
		Lifetime = NumberRange.new(0.35, 0.7), Speed = NumberRange.new(8, 18), SpreadAngle = Vector2.new(180, 180), Drag = 3,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, tam), NumberSequenceKeypoint.new(0.4, tam * 1.3), NumberSequenceKeypoint.new(1, tam * 0.3)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(1, 1)}),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-120, 120)})
	local s = emissor(b, {Texture = BRILHO_TEX, Color = ColorSequence.new(pal.c[1], pal.c[2]), LightEmission = 1, Brightness = 3, Enabled = false,
		Lifetime = NumberRange.new(0.5, 1.0), Speed = NumberRange.new(14, 30), SpreadAngle = Vector2.new(180, 180), Drag = 1.5,
		Acceleration = Vector3.new(0, -20, 0), Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.7), NumberSequenceKeypoint.new(1, 0)})})
	f:Emit(nFogo); s:Emit(nFaisca)
	Debris:AddItem(b, 1.6)
end
local function centro(m)
	local r = m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart)
	return r and r.Position
end

pasta:WaitForChild("Efeito").OnClientEvent:Connect(function(tipo, a, b, c, d)
	if tipo == "rastro" then
		local pos, yaw, roxo, dur = a, b, c, d
		local pal = PALETA[roxo == true]
		local seg = peca("Rastro", Vector3.new(6, 0.1, 3.2), CFrame.new(pos + Vector3.new(0, 0.06, 0)) * CFrame.Angles(0, yaw, 0))
		seg.Material = Enum.Material.Slate; seg.Color = roxo and Color3.fromRGB(28, 12, 40) or Color3.fromRGB(26, 14, 12); seg.Transparency = 0.25
		local br = emissor(seg, {Texture = BRILHO_TEX, Color = ColorSequence.new(pal.c[2], pal.c[3]), LightEmission = 1, Brightness = 2,
			Rate = 4, Lifetime = NumberRange.new(0.6, 1.1), Speed = NumberRange.new(0.5, 1.8), EmissionDirection = Enum.NormalId.Top,
			Acceleration = Vector3.new(0, 2.5, 0), Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.45), NumberSequenceKeypoint.new(1, 0)})})
		task.delay(dur - 0.8, function()
			br.Enabled = false
			TS:Create(seg, TweenInfo.new(0.8), {Transparency = 1}):Play()
		end)
		Debris:AddItem(seg, dur + 0.5)
	elseif tipo == "inicio" then
		local cf = a:GetPivot()
		explosaoPequena(cf.Position - cf.LookVector * 6 + Vector3.new(0, 1.5, 0), b, 20, 10, 3)
	elseif tipo == "impacto" then
		local p = centro(a); if p then explosaoPequena(p + Vector3.new(0, 3, 0), b, 40, 35, 4.5) end
	elseif tipo == "mordida" then
		local p = centro(a); if p then explosaoPequena(p + Vector3.new(({-2, 2, 0})[c] or 0, 5 + (c or 0), 0), b, 8, 16, 2.2) end
	elseif tipo == "passagem" then
		local p = centro(a); if p then explosaoPequena(p + Vector3.new(0, 4, 0), b, 18, 28, 3) end
	elseif tipo == "parede" then
		explosaoPequena(a, b, 14, 30, 2.5)
	end
end)

-- tecla de teste: E investe para o mouse; a direcao segue o mouse por ~5 s
local enviando = false
UIS.InputBegan:Connect(function(inp, gpe)
	if gpe or inp.KeyCode ~= Enum.KeyCode.E then return end
	Pedido:FireServer(mouse.Hit and mouse.Hit.Position or nil)
	if enviando then return end
	enviando = true
	task.spawn(function()
		local t0 = os.clock()
		while os.clock() - t0 < 5.2 do
			task.wait(0.1)
			if mouse.Hit then Direcao:FireServer(mouse.Hit.Position) end
		end
		enviando = false
	end)
end)
