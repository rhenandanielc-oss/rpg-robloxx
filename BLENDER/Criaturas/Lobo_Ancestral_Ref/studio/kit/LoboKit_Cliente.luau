-- LoboKit_Cliente (LocalScript em StarterPlayer.StarterPlayerScripts) - entrada, HUD minima e efeitos discretos do kit
-- Natureza do Lobo Ancestral (prototipo, place isolado, 15/11/2026). Fonte: studio/kit/LoboKit_Cliente.luau.
-- O cliente so PEDE (PedidoKit) e mostra; dano, alvo, alcance, recarga e bonus sao decididos no servidor.
-- Teclas (prototipo): Z = Salto Predatorio (alvo sob o mouse), X = Uivo Ancestral, C = Investida (direcao do mouse no chao),
-- V = Mordida, B = Garra (basicos, fora dos slots). Sons: nao ha sons do lobo no projeto ainda (pendente).
local Players = game:GetService("Players")
local UIS = game:GetService("UserInputService")
local Debris = game:GetService("Debris")
local TweenService = game:GetService("TweenService")
local Rep = game:GetService("ReplicatedStorage")
local PASTA = Rep:WaitForChild("LoboAncestral")
local REM = PASTA:WaitForChild("Remotes")
local PEDIDO, EVENTO = REM:WaitForChild("PedidoKit"), REM:WaitForChild("EventoKit")
local eu = Players.LocalPlayer
local mouse = eu:GetMouse()
local AREA = workspace:WaitForChild("Teste_LoboAncestral")

local function meuLobo()
	for _, m in ipairs(AREA:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("DonoUserId") == eu.UserId then return m end
	end
end
-- HUD minima: estado, energia, bonus e ultima resposta
local gui = Instance.new("ScreenGui"); gui.Name = "LoboKitHUD"; gui.ResetOnSpawn = false; gui.Parent = eu:WaitForChild("PlayerGui")
local txt = Instance.new("TextLabel"); txt.Size = UDim2.new(0, 360, 0, 92); txt.Position = UDim2.new(0, 12, 1, -104)
txt.BackgroundTransparency = 0.45; txt.BackgroundColor3 = Color3.fromRGB(20, 26, 20); txt.TextColor3 = Color3.fromRGB(225, 235, 215)
txt.TextXAlignment = Enum.TextXAlignment.Left; txt.TextYAlignment = Enum.TextYAlignment.Top; txt.Font = Enum.Font.Gotham; txt.TextSize = 13
txt.Text = "Lobo Ancestral"; txt.Parent = gui
local ultima = ""
task.spawn(function()
	while true do
		local m = meuLobo()
		if m then
			txt.Text = string.format("Lobo Ancestral  Vida %s  Energia %s  %s
Z Salto | X Uivo | C Investida | V/B basicos
Bonus: %s  (vel x%.2f, esquiva %.0f%%, dano x%.2f)
%s",
				tostring(m:GetAttribute("Vida")), tostring(m:GetAttribute("Energia")), m:GetAttribute("Noite") and "NOITE" or "dia",
				(m:GetAttribute("Bonus") or "") ~= "" and m:GetAttribute("Bonus") or "-",
				m:GetAttribute("VelMult") or 1, (m:GetAttribute("Esquiva") or 0) * 100, m:GetAttribute("DanoMult") or 1, ultima)
		end
		task.wait(0.2)
	end
end)

local function alvoSobMouse()
	local t = mouse.Target
	local m = t and t:FindFirstAncestorOfClass("Model")
	return m
end
UIS.InputBegan:Connect(function(inp, gp)
	if gp then return end
	local m = meuLobo(); if not m then return end
	local k = inp.KeyCode
	if k == Enum.KeyCode.Z then PEDIDO:FireServer(m, "SaltoPredatorio", alvoSobMouse())
	elseif k == Enum.KeyCode.X then PEDIDO:FireServer(m, "UivoAncestral")
	elseif k == Enum.KeyCode.C then
		local d = mouse.Hit.Position - m:GetPivot().Position
		PEDIDO:FireServer(m, "Investida", Vector3.new(d.X, 0, d.Z))
	elseif k == Enum.KeyCode.V then PEDIDO:FireServer(m, "Mordida")
	elseif k == Enum.KeyCode.B then PEDIDO:FireServer(m, "Garra") end
end)

-- ------------------------------------------------------------------ efeitos discretos (folhas/vento, sem brilho constante)
local VERDE = Color3.fromRGB(96, 128, 64)
local function folhas(cf, qtd, vel, vida)
	local a = Instance.new("Attachment"); a.WorldCFrame = cf; a.Parent = workspace.Terrain
	local pe = Instance.new("ParticleEmitter")
	pe.Texture = "rbxasset://textures/particles/sparkles_main.dds"
	pe.Color = ColorSequence.new(VERDE, Color3.fromRGB(150, 140, 80)); pe.LightEmission = 0; pe.LightInfluence = 1
	pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(1, 0.05)})
	pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1)})
	pe.Lifetime = NumberRange.new(vida * 0.6, vida); pe.Speed = NumberRange.new(vel * 0.5, vel); pe.SpreadAngle = Vector2.new(40, 40)
	pe.Rotation = NumberRange.new(0, 360); pe.RotSpeed = NumberRange.new(-180, 180); pe.Drag = 2; pe.Acceleration = Vector3.new(0, -3, 0)
	pe.Enabled = false; pe.Parent = a; pe:Emit(qtd)
	Debris:AddItem(a, vida + 0.5)
end
local function rastroVento(m, dur)
	local root = m:FindFirstChild("RootPart"); if not root then return end
	local a0 = Instance.new("Attachment", root); a0.Position = Vector3.new(0.9, 4.2, 2)
	local a1 = Instance.new("Attachment", root); a1.Position = Vector3.new(-0.9, 4.2, 2)
	local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = 0.25
	tr.Color = ColorSequence.new(Color3.fromRGB(205, 215, 190)); tr.LightEmission = 0
	tr.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.75), NumberSequenceKeypoint.new(1, 1)})
	tr.WidthScale = NumberSequence.new(1, 0.2); tr.Parent = root
	task.delay(dur, function() tr.Enabled = false; Debris:AddItem(tr, 0.4); Debris:AddItem(a0, 0.4); Debris:AddItem(a1, 0.4) end)
end
local pegadas = {}
local function pegada(p)
	local k = string.format("%d_%d", math.floor(p.X / 2), math.floor(p.Z / 2))
	if pegadas[k] then return end
	local d = Instance.new("Part"); d.Anchored = true; d.CanCollide = false; d.CanQuery = false; d.CanTouch = false; d.CastShadow = false
	d.Size = Vector3.new(0.7, 0.05, 0.9); d.Color = Color3.fromRGB(70, 60, 45); d.Material = Enum.Material.SmoothPlastic; d.Transparency = 0.45
	d.CFrame = CFrame.new(p + Vector3.new(math.random() - 0.5, 0.03, math.random() - 0.5)) * CFrame.Angles(0, math.random() * 6.28, 0)
	d.Name = "PegadaInstinto"; d.Parent = workspace.Terrain; pegadas[k] = d
	TweenService:Create(d, TweenInfo.new(6), {Transparency = 1}):Play()
	task.delay(6, function() pegadas[k] = nil; d:Destroy() end)
end
EVENTO.OnClientEvent:Connect(function(tipo, m, a, b, c, d)
	if tipo == "Resposta" then ultima = string.format("%s: %s %s", tostring(a), b and "ok" or "recusado", c or "")
	elseif tipo == "Pegadas" then for _, p in ipairs(a) do pegada(p) end
	elseif tipo == "PistaNinho" then
		local base = m:GetPivot().Position + Vector3.new(0, 3, 0)
		folhas(CFrame.lookAt(base, base + a) * CFrame.Angles(0, 0, 0), 12, 14, 1.4)  -- rajada curta de folhas na direcao aproximada
	elseif tipo == "Salto" then folhas(CFrame.new(a + Vector3.new(0, 1, 0)), 10, 6, 1.0); task.delay(0.86, function() folhas(CFrame.new(b + Vector3.new(0, 0.5, 0)), 14, 8, 1.0) end)
	elseif tipo == "Uivo" then
		local root = m:FindFirstChild("RootPart")
		for i = 0, 2 do task.delay(i * 0.5, function() if m.Parent then folhas(m:GetPivot() * CFrame.new(0, 6, -3), 8, 5, 1.6) end end) end
	elseif tipo == "Investida" then task.delay(0.22, function() rastroVento(m, 0.74) end)
	elseif tipo == "Noite" then ultima = a and "Cacador Noturno ativo (noite)" or "Cacador Noturno inativo (dia)" end
end)
