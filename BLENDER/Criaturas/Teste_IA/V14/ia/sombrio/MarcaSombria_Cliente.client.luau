-- MarcaSombria_Cliente (LocalScript) — VISUAL da Marca Sombria (passiva do Dragao Sombrio). So cosmetico: o servidor
-- (Combate_Dragao.Passivas) decide as marcas e publica o atributo MarcaSombria (total) no alvo.
-- Fios de nevoa violeta em volta do alvo, mais densos por marca: 1 ParticleEmitter por alvo marcado, taxa limitada,
-- sem luz dinamica; some quando as marcas acabam ou o alvo sai. LOD por distancia. Valores NAO_APROVADO.
local RunService = game:GetService("RunService")
local cam = workspace.CurrentCamera
local LOD = 250
local TEX = "rbxasset://textures/particles/smoke_main.dds"
local ativos = {}                                     -- [alvo] = emissor
local function raiz(a) return a:FindFirstChild("HumanoidRootPart") or a.PrimaryPart end
local function criar(alvo)
	local r = raiz(alvo); if not r then return end
	local e = Instance.new("ParticleEmitter"); e.Name = "MarcaSombria_VFX"; e.Texture = TEX
	e.Color = ColorSequence.new(Color3.fromRGB(150, 50, 230), Color3.fromRGB(20, 0, 35))
	e.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.6), NumberSequenceKeypoint.new(0.5, 0.75), NumberSequenceKeypoint.new(1, 1)})
	e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.6), NumberSequenceKeypoint.new(1, 1.6)})
	e.Lifetime = NumberRange.new(0.8, 1.3); e.Speed = NumberRange.new(0.5, 1.5); e.SpreadAngle = Vector2.new(180, 180)
	e.LightEmission = 0.4; e.LightInfluence = 0.5; e.Rotation = NumberRange.new(0, 360); e.RotSpeed = NumberRange.new(-40, 40)
	e.Acceleration = Vector3.new(0, 1.5, 0); e.Rate = 0; e.Parent = r
	ativos[alvo] = e
end
local acum = 0
RunService.Heartbeat:Connect(function(dt)
	acum += dt; if acum < 0.2 then return end; acum = 0
	local vistos = {}
	for _, d in ipairs(game:GetService("CollectionService"):GetTagged("MarcaSombria")) do    -- tag posta pelo servidor
		if d:IsA("Model") and d:GetAttribute("MarcaSombria") then vistos[d] = d:GetAttribute("MarcaSombria") end
	end
	for alvo, n in pairs(vistos) do
		if not ativos[alvo] then criar(alvo) end
		local e = ativos[alvo]
		if e then
			local r = raiz(alvo); local longe = not r or (r.Position - cam.CFrame.Position).Magnitude > LOD
			e.Rate = longe and 0 or math.min(5, n) * 3                     -- ate 15 particulas/s por alvo
		end
	end
	for alvo, e in pairs(ativos) do
		if not vistos[alvo] or not alvo:IsDescendantOf(workspace) then e:Destroy(); ativos[alvo] = nil end
	end
end)
