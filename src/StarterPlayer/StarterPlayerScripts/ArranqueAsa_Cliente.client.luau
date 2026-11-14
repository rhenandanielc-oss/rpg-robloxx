-- ArranqueAsa_Cliente (LocalScript, StarterPlayerScripts) — efeito VISUAL da passiva Arranque de Asa da Wyvern (so cosmetico).
-- Quando o servidor marca ArranqueAsaT no modelo (impulso aplicado), envolve o corpo numa AURA DE ACELERACAO discreta:
-- vento branco translucido (elemento Ar) que nasce no dorso, quadril, pescoco e nas maos das asas e escorre para tras por
-- ~1 s. Todos os jogadores veem (o atributo replica).
-- r2 (usuario 13/11): "em vez de uma linha, deve ter uma aura de aceleracao, nao tao escandalosa" -> a r1 desenhava dois
-- rastros (Trail) nas pontas das asas. Custo: 5 ParticleEmitters por impulso (taxa baixa, vida curta), criados e destruidos
-- na hora; a recarga de 10 s limita a frequencia por Wyvern.
local RunService = game:GetService("RunService")
local OSSOS = {"Coluna2", "Quadril", "Pescoco2", "hand_L", "hand_R"}
local DURACAO, VIDA = 1.0, 0.6                        -- s emitindo / vida maxima de cada particula
local TEXTURA = "rbxasset://textures/particles/smoke_main.dds"
local ligados = {}

local function emissor(osso, forte)
	local p = Instance.new("ParticleEmitter"); p.Name = "ArranqueAsa_Aura"
	p.Texture = TEXTURA
	p.Color = ColorSequence.new(Color3.fromRGB(235, 245, 255))
	p.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.2, 0.78),
		NumberSequenceKeypoint.new(1, 1)})
	p.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, forte and 2.2 or 1.4), NumberSequenceKeypoint.new(1, forte and 4.5 or 3)})
	p.Lifetime = NumberRange.new(0.35, VIDA)
	p.Rate = forte and 22 or 12
	p.Speed = NumberRange.new(0); p.Drag = 3
	p.SpreadAngle = Vector2.new(180, 180)
	p.Rotation = NumberRange.new(0, 360); p.RotSpeed = NumberRange.new(-40, 40)
	p.LightEmission = 0.25; p.LightInfluence = 0.6
	p.LockedToPart = false
	p.Parent = osso
	return p
end

local function disparar(m)
	local lista = {}
	for i, n in ipairs(OSSOS) do
		local b = m:FindFirstChild(n, true)
		if b and b:IsA("Bone") then table.insert(lista, emissor(b, i <= 2)) end
	end
	if #lista == 0 then return end
	-- o vento escorre para TRAS do corpo (aceleracao no mundo, renovada enquanto emite)
	local fim = os.clock() + DURACAO
	local con; con = RunService.RenderStepped:Connect(function()
		if os.clock() > fim or not m.Parent then
			con:Disconnect()
			for _, p in ipairs(lista) do p.Enabled = false end
			return
		end
		local tras = -m:GetPivot().LookVector * 55
		for _, p in ipairs(lista) do p.Acceleration = tras end
	end)
	task.delay(DURACAO + VIDA + 0.2, function() for _, p in ipairs(lista) do p:Destroy() end end)
end

local function ligar(m)
	if ligados[m] or not m:IsA("Model") or m:GetAttribute("FormaRegional") ~= "Wyvern" then return end
	ligados[m] = m:GetAttributeChangedSignal("ArranqueAsaT"):Connect(function() disparar(m) end)
	m.AncestryChanged:Connect(function(_, pai) if not pai and ligados[m] then ligados[m]:Disconnect(); ligados[m] = nil end end)
end

for _, m in ipairs(workspace:GetChildren()) do ligar(m) end
workspace.ChildAdded:Connect(function(m) task.defer(ligar, m) end)
-- com streaming o modelo pode chegar antes do atributo FormaRegional: varredura leve
task.spawn(function()
	while true do
		task.wait(3)
		for _, m in ipairs(workspace:GetChildren()) do if not ligados[m] then ligar(m) end end
	end
end)
_G.ArranqueAsa_Disparar = disparar     -- depuracao (cliente)
