-- VigiliaFuria_Cliente (LocalScript em StarterPlayerScripts) - PROTOTIPO da Vigilia e da Furia: tecla F + visual (26/11).
-- Furia: estouro de fogo na boca de cada cabeca no rugido (C, E, D); 3 faixas finas de vento quente girando no tronco enquanto
-- o atributo Furia estiver ligado (somem aos poucos no ultimo 1,5 s, atributo FuriaFade); fumaca cinza nos afetados pelo Rugido.
-- A cor roxa da aura e dos poderes vem do atributo Furia (AuraCerbero_Cliente, Sol, Investida).
-- Vigilia: pupilas (emissores "Pupila" nos ossos Pupila_*) acendem 1 s; contorno laranja-fogo (Highlight) so neste cliente (dono).
-- Sem luz extra. Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/vigilia/VigiliaFuria_Cliente.client.luau
local RS = game:GetService("ReplicatedStorage")
local Run = game:GetService("RunService")
local UIS = game:GetService("UserInputService")
local Debris = game:GetService("Debris")

local pasta = RS:WaitForChild("VigiliaFuria")
local Pedido = pasta:WaitForChild("PedidoFuria")
local cerbero = workspace:WaitForChild("Teste_Cerbero"):WaitForChild("Cerbero_Sombrio")

local FOGO_TEX = "rbxasset://textures/particles/fire_main.dds"
local BRILHO_TEX = "rbxasset://textures/particles/sparkles_main.dds"
local SMOKE_TEX = "rbxasset://textures/particles/smoke_main.dds"
local ROXO = {Color3.fromRGB(232, 205, 255), Color3.fromRGB(180, 90, 255), Color3.fromRGB(112, 30, 222), Color3.fromRGB(40, 5, 80)}
local LARANJA = Color3.fromRGB(255, 130, 35)

local pastaLocal = Instance.new("Folder"); pastaLocal.Name = "VigiliaFuria_Local"; pastaLocal.Parent = workspace
local function peca(tam, cf)
	local p = Instance.new("Part")
	p.Size = tam; p.CFrame = cf; p.Transparency = 1
	p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	p.Parent = pastaLocal
	return p
end
local function emissor(pai, t)
	local e = Instance.new("ParticleEmitter")
	for k, v in pairs(t) do e[k] = v end
	e.LightInfluence = 0
	e.Parent = pai
	return e
end
local function seq(c) return ColorSequence.new({ColorSequenceKeypoint.new(0, c[1]), ColorSequenceKeypoint.new(0.25, c[2]), ColorSequenceKeypoint.new(0.65, c[3]), ColorSequenceKeypoint.new(1, c[4])}) end

-- ===== rugido: estouro de fogo na boca =====
local function rugido(k)
	local mand = cerbero:FindFirstChild("Mandibula" .. k, true)
	local cab = cerbero:FindFirstChild("Cabeca" .. k, true)
	if not (mand and cab) then return end
	local frente = cerbero:GetPivot().LookVector
	local pos = mand.WorldPosition + frente * 2.5
	local b = peca(Vector3.one, CFrame.new(pos, pos + frente))
	local f = emissor(b, {Texture = FOGO_TEX, Color = seq(ROXO), LightEmission = 0.8, Brightness = 1.8, Enabled = false,
		EmissionDirection = Enum.NormalId.Front, SpreadAngle = Vector2.new(35, 35), Speed = NumberRange.new(10, 20), Drag = 3,
		Lifetime = NumberRange.new(0.35, 0.6), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-120, 120),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.8), NumberSequenceKeypoint.new(0.4, 3.2), NumberSequenceKeypoint.new(1, 0.6)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.2), NumberSequenceKeypoint.new(1, 1)})})
	local s = emissor(b, {Texture = BRILHO_TEX, Color = ColorSequence.new(ROXO[1], ROXO[2]), LightEmission = 1, Brightness = 3, Enabled = false,
		EmissionDirection = Enum.NormalId.Front, SpreadAngle = Vector2.new(50, 50), Speed = NumberRange.new(14, 26), Drag = 1.5,
		Lifetime = NumberRange.new(0.4, 0.8), Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.6), NumberSequenceKeypoint.new(1, 0)})})
	f:Emit(30); s:Emit(20)
	Debris:AddItem(b, 1.2)
end

-- ===== vento quente no tronco (3 faixas com Trail girando) =====
local vento = nil
local function ligarVento()
	if vento then return end
	local col = cerbero:FindFirstChild("Coluna2", true)
	if not col then return end
	vento = {pecas = {}, trilhas = {}, t = 0}
	for i = 1, 3 do
		local p = peca(Vector3.one * 0.2, CFrame.new(col.WorldPosition))
		local a0 = Instance.new("Attachment"); a0.Position = Vector3.new(0, 0.35, 0); a0.Parent = p
		local a1 = Instance.new("Attachment"); a1.Position = Vector3.new(0, -0.35, 0); a1.Parent = p
		local tr = Instance.new("Trail")
		tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = 0.45; tr.LightEmission = 1; tr.LightInfluence = 0
		tr.Color = ColorSequence.new(ROXO[1], ROXO[2]); tr.FaceCamera = true
		tr.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.25), NumberSequenceKeypoint.new(1, 1)})
		tr.WidthScale = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(1, 0.2)})
		tr.Parent = p
		table.insert(vento.pecas, p); table.insert(vento.trilhas, tr)
	end
end
local function desligarVento()
	if not vento then return end
	for _, p in ipairs(vento.pecas) do Debris:AddItem(p, 0.6) end
	for _, tr in ipairs(vento.trilhas) do tr.Enabled = false end
	vento = nil
end
Run.RenderStepped:Connect(function(dt)
	local furia = cerbero:GetAttribute("Furia") == true
	if furia then ligarVento() elseif vento then desligarVento() end
	if not vento then return end
	vento.t += dt
	local col = cerbero:FindFirstChild("Coluna2", true)
	local cf = cerbero:GetPivot()
	local c = col and col.WorldPosition or cf.Position + Vector3.new(0, 10, 0)
	local fade = cerbero:GetAttribute("FuriaFade") == true
	for i, p in ipairs(vento.pecas) do
		local ang = vento.t * 4.2 + i * (2 * math.pi / 3)
		local raio = 8.5 + math.sin(vento.t * 2 + i) * 0.8
		local local_ = Vector3.new(math.cos(ang) * raio * 0.62, (i - 2) * 2.4 + math.sin(ang * 2) * 0.6, math.sin(ang) * raio)
		p.CFrame = CFrame.new(c + cf:VectorToWorldSpace(local_))
		vento.trilhas[i].Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, fade and 0.7 or 0.25), NumberSequenceKeypoint.new(1, 1)})
	end
end)

-- ===== afetado pelo Rugido: fumaca cinza por 4 s =====
local function debuff(m, dur)
	local raiz = m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart)
	if not raiz then return end
	local e = emissor(raiz, {Texture = SMOKE_TEX, Color = ColorSequence.new(Color3.fromRGB(110, 105, 110)), LightEmission = 0, Rate = 10,
		Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(1, 3), Acceleration = Vector3.new(0, 2, 0),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.5), NumberSequenceKeypoint.new(1, 3)}),
		Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.5), NumberSequenceKeypoint.new(1, 1)})})
	e.LightInfluence = 1
	task.delay(dur, function() e.Enabled = false; Debris:AddItem(e, 1.5) end)
end

-- ===== Vigilia: pupilas e contorno =====
local function pupilas(dur)
	for _, d in ipairs(cerbero:GetDescendants()) do
		if d:IsA("ParticleEmitter") and d.Name == "Pupila" then d.Enabled = true end
	end
	task.delay(dur, function()
		for _, d in ipairs(cerbero:GetDescendants()) do
			if d:IsA("ParticleEmitter") and d.Name == "Pupila" then d.Enabled = false end
		end
	end)
end
local contornos = {}
local function contorno(m, ligar)
	if ligar then
		if contornos[m] then return end
		local h = Instance.new("Highlight")
		h.FillTransparency = 0.85; h.FillColor = LARANJA; h.OutlineColor = LARANJA; h.OutlineTransparency = 0
		h.DepthMode = Enum.HighlightDepthMode.AlwaysOnTop; h.Adornee = m; h.Parent = pastaLocal
		local antes = {}
		for _, p in ipairs(m:GetDescendants()) do
			if p:IsA("BasePart") then antes[p] = p.Transparency; p.Transparency = math.min(p.Transparency, 0.92) end  -- so neste cliente
		end
		contornos[m] = {h, antes}
	elseif contornos[m] then
		local h, antes = contornos[m][1], contornos[m][2]
		h:Destroy()
		for p, t in pairs(antes) do if p.Parent then p.Transparency = t end end
		contornos[m] = nil
	end
end

pasta:WaitForChild("Efeito").OnClientEvent:Connect(function(tipo, a, b)
	if tipo == "rugido" then rugido(a)
	elseif tipo == "debuff" then debuff(a, b)
	elseif tipo == "pupilas" then pupilas(a)
	elseif tipo == "contorno" then contorno(a, b)
	end
end)

UIS.InputBegan:Connect(function(inp, gpe)
	if gpe or inp.KeyCode ~= Enum.KeyCode.F then return end
	Pedido:FireServer()
end)
