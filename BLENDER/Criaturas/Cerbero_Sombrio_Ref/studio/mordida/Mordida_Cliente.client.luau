-- Mordida_Cliente (LocalScript em StarterPlayerScripts) - PROTOTIPO da mordida basica do Cerbero: clique + visual (27/11).
-- Clique esquerdo perto do Cerbero: pede a mordida (alvo sob o mouse); o servidor escolhe a cabeca e decide o acerto.
-- Visual: faiscas e um pouco de fogo no ponto da mordida que acertou (roxo na Furia). Sem luz extra.
-- Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/mordida/Mordida_Cliente.client.luau
local RS = game:GetService("ReplicatedStorage")
local UIS = game:GetService("UserInputService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")

local pasta = RS:WaitForChild("MordidaCerbero")
local Pedido = pasta:WaitForChild("PedidoMordida")
local mouse = Players.LocalPlayer:GetMouse()
local FOGO_TEX = "rbxasset://textures/particles/fire_main.dds"
local BRILHO_TEX = "rbxasset://textures/particles/sparkles_main.dds"

local pastaLocal = Instance.new("Folder"); pastaLocal.Name = "Mordida_Local"; pastaLocal.Parent = workspace

pasta:WaitForChild("Efeito").OnClientEvent:Connect(function(tipo, a, roxo)
	if tipo ~= "acerto" then return end
	local p = Instance.new("Part")
	p.Size = Vector3.one; p.CFrame = CFrame.new(a); p.Transparency = 1
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.Parent = pastaLocal
	local c1 = roxo and Color3.fromRGB(232, 205, 255) or Color3.fromRGB(255, 232, 150)
	local c2 = roxo and Color3.fromRGB(150, 60, 240) or Color3.fromRGB(255, 120, 25)
	local s = Instance.new("ParticleEmitter")
	s.Texture = BRILHO_TEX; s.Color = ColorSequence.new(c1, c2); s.LightEmission = 1; s.LightInfluence = 0; s.Brightness = 3
	s.Enabled = false; s.Lifetime = NumberRange.new(0.3, 0.6); s.Speed = NumberRange.new(10, 22); s.SpreadAngle = Vector2.new(180, 180)
	s.Drag = 2; s.Acceleration = Vector3.new(0, -15, 0); s.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.5), NumberSequenceKeypoint.new(1, 0)})
	s.Parent = p
	local f = Instance.new("ParticleEmitter")
	f.Texture = FOGO_TEX; f.Color = ColorSequence.new(c2, Color3.fromRGB(60, 10, 5)); f.LightEmission = 0.8; f.LightInfluence = 0; f.Brightness = 1.6
	f.Enabled = false; f.Lifetime = NumberRange.new(0.2, 0.4); f.Speed = NumberRange.new(4, 9); f.SpreadAngle = Vector2.new(180, 180); f.Drag = 3
	f.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.4), NumberSequenceKeypoint.new(1, 0.3)})
	f.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.3), NumberSequenceKeypoint.new(1, 1)})
	f.Parent = p
	s:Emit(18); f:Emit(8)
	Debris:AddItem(p, 1)
end)

UIS.InputBegan:Connect(function(inp, gpe)
	if gpe or inp.UserInputType ~= Enum.UserInputType.MouseButton1 then return end
	Pedido:FireServer(mouse.Target, mouse.Hit and mouse.Hit.Position or nil)
end)
