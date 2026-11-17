-- CrocodiloFX_Cliente (LocalScript em StarterPlayer.StarterPlayerScripts do place de TESTE RBX Crocodilo) - P4 16/11
-- PREVIA DE TESTE dos efeitos do Crocodilo Primordial. So visual: o servidor (PoderesTeste) decide agua, alcance, alvo,
-- energia, dano, estados e soltura; aqui so se desenha o que ele anuncia (RemoteEvent Crocodilo_FX e atributos no modelo).
-- Reacao FISICA da agua (ondulacao, rastro, bolhas) separada dos efeitos MAGICOS (linhas nas escamas, pulso). Tudo
-- temporario, limpo ao fim/cancelamento. Orcamento (ref. 5.10): so ate 150 studs; poucas pecas; metade no celular.
local RS = game:GetService("RunService"); local TS = game:GetService("TweenService")
local UIS = game:GetService("UserInputService"); local Debris = game:GetService("Debris")
local T = workspace:WaitForChild("Teste_Crocodilo"); local croc = T:WaitForChild("Crocodilo_Primordial")
local ev = game:GetService("ReplicatedStorage"):WaitForChild("Crocodilo_FX")
local CELULAR = UIS.TouchEnabled and not UIS.KeyboardEnabled
local ESCALA = CELULAR and 0.5 or 1
local pasta = Instance.new("Folder"); pasta.Name = "FX_Cliente_Crocodilo"; pasta.Parent = workspace
local cam = workspace.CurrentCamera
local function perto(pos) return (cam.CFrame.Position - pos).Magnitude <= 150 end
local function osso(n) return croc:FindFirstChild(n, true) end

-- anel fino na superficie (SurfaceGui com UIStroke = traco constante enquanto cresce)
local function anel(pos, r0, r1, dur, alfa, espessura)
	if not perto(pos) then return end
	local p = Instance.new("Part"); p.Name = "FX_Anel"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Transparency = 1; p.Size = Vector3.new(r0 * 2, 0.05, r0 * 2); p.CFrame = CFrame.new(pos + Vector3.new(0, 0.06, 0))
	local sg = Instance.new("SurfaceGui"); sg.Face = Enum.NormalId.Top; sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud
	sg.PixelsPerStud = 24; sg.LightInfluence = 1; sg.Parent = p
	local f = Instance.new("Frame"); f.Size = UDim2.fromScale(1, 1); f.BackgroundTransparency = 1; f.Parent = sg
	Instance.new("UICorner", f).CornerRadius = UDim.new(0.5, 0)
	local st = Instance.new("UIStroke"); st.Color = Color3.fromRGB(214, 226, 214); st.Thickness = espessura or 5; st.Transparency = alfa; st.Parent = f
	p.Parent = pasta
	local ti = TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
	TS:Create(p, ti, {Size = Vector3.new(r1 * 2, 0.05, r1 * 2)}):Play(); TS:Create(st, ti, {Transparency = 1}):Play()
	Debris:AddItem(p, dur + 0.1)
end
local function ondulacao(pos, forca)
	forca = forca or 1
	for k = 0, 2 do
		task.delay(k * 0.18, function() anel(pos, 1.5 + k, (7 + 4 * k) * forca, 1.3 + 0.2 * k, 0.25 + 0.15 * k, 6 - k) end)
	end
end
-- poucas bolhas: esferas pequenas que sobem e somem na superficie
local function bolha(pos, sup)
	if not perto(pos) then return end
	local b = Instance.new("Part"); b.Name = "FX_Bolha"; b.Shape = Enum.PartType.Ball; b.Anchored = true; b.CanCollide = false
	b.CanQuery = false; b.CanTouch = false; b.CastShadow = false; b.Material = Enum.Material.Glass; b.Color = Color3.fromRGB(230, 240, 235)
	b.Transparency = 0.45; local r = 0.18 + math.random() * 0.22; b.Size = Vector3.new(r, r, r); b.Position = pos; b.Parent = pasta
	local subida = math.max(0.2, sup - pos.Y); local dur = subida / 3.2
	TS:Create(b, TweenInfo.new(dur, Enum.EasingStyle.Linear), {Position = Vector3.new(pos.X + (math.random() - 0.5), sup, pos.Z + (math.random() - 0.5))}):Play()
	task.delay(dur, function() if b.Parent then anel(Vector3.new(b.Position.X, sup, b.Position.Z), 0.2, 1.2, 0.6, 0.5, 3); b:Destroy() end end)
end
-- aviso de recusa (raso / sem agua): texto curto sobre a cabeca por 1,8 s
local function recusa(pos, texto)
	local cab = osso("Cabeca"); if not cab then return end
	local bb = Instance.new("BillboardGui"); bb.Name = "FX_Recusa"; bb.Size = UDim2.fromOffset(260, 40); bb.StudsOffsetWorldSpace = Vector3.new(0, 5, 0)
	bb.Adornee = croc.PrimaryPart or croc:FindFirstChildWhichIsA("BasePart", true); bb.AlwaysOnTop = true
	local t = Instance.new("TextLabel"); t.Size = UDim2.fromScale(1, 1); t.BackgroundColor3 = Color3.fromRGB(120, 30, 20); t.BackgroundTransparency = 0.2
	t.TextColor3 = Color3.new(1, 1, 1); t.Font = Enum.Font.GothamBold; t.TextScaled = true; t.Text = "✕ " .. texto; t.Parent = bb
	Instance.new("UICorner", t).CornerRadius = UDim.new(0, 8); bb.Parent = pasta
	Debris:AddItem(bb, 1.8)
end

-- laco: bolhas e rastro enquanto o servidor marca Submerso/Movendo
local acc, accR = 0, 0
RS.Heartbeat:Connect(function(dt)
	if not croc:GetAttribute("Submerso") then return end
	local sup = croc:GetAttribute("Superficie"); if not sup then return end
	local cab = osso("Cabeca"); local cauda = osso("Cauda5"); if not cab then return end
	local movendo = croc:GetAttribute("Movendo")
	acc += dt * (movendo and 5 or 1.5) * ESCALA
	while acc >= 1 do
		acc -= 1
		local fonte = (math.random() < 0.6 or not cauda) and cab or cauda
		bolha(fonte.TransformedWorldCFrame.Position + Vector3.new(0, 1, 0), sup)
	end
	if movendo then                                            -- rastro: aneis rasos acima da cabeca, ficando para tras
		accR += dt
		if accR >= 0.3 / ESCALA then
			accR = 0; local p = cab.TransformedWorldCFrame.Position
			anel(Vector3.new(p.X, sup, p.Z), 1.0, 5.5, 1.6, 0.55, 4)
		end
	end
end)

-- ---------------------------------------------------------------- Giro de Emboscada (P4): previa de teste
-- antes: agua escurece em volta e poucas bolhas sobem (silencioso); no ar: agua escorrendo do corpo + linhas verde-escuras
-- discretas presas ao corpo (contorno continuo, previa da "capa" de linhas); pouso: anel de impacto no chao + po/lama.
local function discoEscuro(pos, raio, dur)
	if not perto(pos) then return end
	local p = Instance.new("Part"); p.Name = "FX_AguaEscura"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Shape = Enum.PartType.Cylinder; p.Material = Enum.Material.SmoothPlastic; p.Color = Color3.fromRGB(18, 26, 18)
	p.Transparency = 1; p.Size = Vector3.new(0.05, raio * 2, raio * 2); p.CFrame = CFrame.new(pos + Vector3.new(0, 0.04, 0)) * CFrame.Angles(0, 0, math.rad(90)); p.Parent = pasta
	TS:Create(p, TweenInfo.new(dur * 0.4), {Transparency = 0.55}):Play()
	task.delay(dur * 0.5, function() if p.Parent then TS:Create(p, TweenInfo.new(dur * 0.5), {Transparency = 1}):Play() end end)
	Debris:AddItem(p, dur + 0.1)
end
local giroFX = {}
local function giroLigar(on)
	for _, o in ipairs(giroFX) do if o.Parent then if o:IsA("ParticleEmitter") then o.Enabled = false; Debris:AddItem(o, 1.2) else TS:Create(o, TweenInfo.new(0.5), {OutlineTransparency = 1}):Play(); Debris:AddItem(o, 0.6) end end end
	giroFX = {}
	if not on then return end
	for _, n in ipairs({"Coluna1", "Coluna2", "Pelve", "Cauda3", "Pescoco"}) do               -- agua escorrendo (gotas que caem)
		local b = osso(n); if b then
			local e = Instance.new("ParticleEmitter"); e.Name = "FX_Escorre"; e.Texture = "rbxasset://textures/particles/smoke_main.dds"
			e.Color = ColorSequence.new(Color3.fromRGB(200, 214, 205)); e.LightEmission = 0.1; e.Transparency = NumberSequence.new(0.35, 1)
			e.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.35), NumberSequenceKeypoint.new(1, 0.12)})
			e.Lifetime = NumberRange.new(0.4, 0.7); e.Rate = 26 * ESCALA; e.Speed = NumberRange.new(1, 3); e.SpreadAngle = Vector2.new(180, 180)
			e.Acceleration = Vector3.new(0, -60, 0); e.Drag = 1; e.Parent = b; table.insert(giroFX, e)
		end
	end
	local h = Instance.new("Highlight"); h.Name = "FX_LinhasEscamas"; h.Adornee = croc; h.FillTransparency = 1
	h.OutlineColor = Color3.fromRGB(46, 104, 58); h.OutlineTransparency = 1; h.DepthMode = Enum.HighlightDepthMode.Occluded; h.Parent = pasta
	TS:Create(h, TweenInfo.new(0.25), {OutlineTransparency = 0.45}):Play(); table.insert(giroFX, h)
end
croc:GetAttributeChangedSignal("Giro"):Connect(function() giroLigar(croc:GetAttribute("Giro") == true) end)
local function giroAntes(pos, look)
	discoEscuro(pos, 10, 1.0); ondulacao(pos, 0.7)
	for k = 1, math.floor(6 * ESCALA) do task.delay(k * 0.06, function() bolha(pos + Vector3.new(math.random() * 6 - 3, -3 - math.random() * 2, math.random() * 6 - 3), pos.Y) end) end
end
local function giroPouso(pos, raio, naAgua)
	if not perto(pos) then return end
	if naAgua then ondulacao(pos, 1.6) end
	for k = 0, 1 do                                                                   -- anel de impacto (lama) ate o raio
		task.delay(k * 0.1, function()
			local p = Instance.new("Part"); p.Name = "FX_Impacto"; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
			p.CastShadow = false; p.Transparency = 1; p.Size = Vector3.new(2, 0.05, 2); p.CFrame = CFrame.new(pos + Vector3.new(0, 0.08, 0))
			local sg = Instance.new("SurfaceGui"); sg.Face = Enum.NormalId.Top; sg.SizingMode = Enum.SurfaceGuiSizingMode.PixelsPerStud; sg.PixelsPerStud = 24; sg.Parent = p
			local f = Instance.new("Frame"); f.Size = UDim2.fromScale(1, 1); f.BackgroundTransparency = 1; f.Parent = sg
			Instance.new("UICorner", f).CornerRadius = UDim.new(0.5, 0)
			local st = Instance.new("UIStroke"); st.Color = Color3.fromRGB(110, 92, 62); st.Thickness = 10 - 4 * k; st.Transparency = 0.15; st.Parent = f
			p.Parent = pasta
			local ti = TweenInfo.new(0.55, Enum.EasingStyle.Quad, Enum.EasingDirection.Out)
			TS:Create(p, ti, {Size = Vector3.new(raio * 2, 0.05, raio * 2)}):Play(); TS:Create(st, TweenInfo.new(0.7), {Transparency = 1}):Play()
			Debris:AddItem(p, 0.8)
		end)
	end
	local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain                -- po/lama baixa
	local e = Instance.new("ParticleEmitter"); e.Texture = "rbxasset://textures/particles/smoke_main.dds"; e.Color = ColorSequence.new(Color3.fromRGB(120, 104, 78))
	e.Transparency = NumberSequence.new(0.4, 1); e.Size = NumberSequence.new(2, 5); e.Lifetime = NumberRange.new(0.6, 1.0); e.Speed = NumberRange.new(6, 12)
	e.SpreadAngle = Vector2.new(80, 10); e.Rotation = NumberRange.new(0, 360); e.Acceleration = Vector3.new(0, -4, 0); e.Drag = 3; e.Enabled = false; e.Parent = a
	e:Emit(math.floor(24 * ESCALA)); Debris:AddItem(a, 1.3)
end

-- ---------------------------------------------------------------- Cauda de Mare e Escamas Grossas (P4): previa de teste
-- cauda: na AGUA a ponta da cauda deixa aneis na superficie enquanto varre e o impacto solta uma onda grande no nivel da
-- agua; em TERRA a ponta levanta lama baixa e o impacto e um anel de lama menor. Escamas: pulso curto verde-escuro nas
-- escamas no ponto do golpe (sem escudo permanente).
local caudaCon
croc:GetAttributeChangedSignal("CaudaVarre"):Connect(function()
	local modo = croc:GetAttribute("CaudaVarre")
	if caudaCon then caudaCon:Disconnect(); caudaCon = nil end
	if not modo then return end
	local nivel = croc:GetAttribute("Nivel") or 0; local acc = 0
	caudaCon = RS.Heartbeat:Connect(function(dt)
		acc += dt; if acc < 0.05 / ESCALA then return end; acc = 0
		local b = osso("Cauda8"); if not b then return end
		local p = b.TransformedWorldCFrame.Position
		if modo == "agua" then anel(Vector3.new(p.X, nivel, p.Z), 0.6, 3.2, 0.9, 0.35, 4)
		else anel(Vector3.new(p.X, nivel, p.Z), 0.4, 1.8, 0.6, 0.45, 3) end
	end)
end)
local function caudaImpacto(pos, raio, naAgua)
	if naAgua then
		ondulacao(pos, 1.2); task.delay(0.12, function() anel(pos, 2, raio, 1.1, 0.1, 9) end)
	else
		anel(pos, 1, raio, 0.6, 0.2, 7)
		local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain
		local e = Instance.new("ParticleEmitter"); e.Texture = "rbxasset://textures/particles/smoke_main.dds"; e.Color = ColorSequence.new(Color3.fromRGB(120, 104, 78))
		e.Transparency = NumberSequence.new(0.45, 1); e.Size = NumberSequence.new(1.5, 3.5); e.Lifetime = NumberRange.new(0.5, 0.8); e.Speed = NumberRange.new(4, 8)
		e.SpreadAngle = Vector2.new(70, 10); e.Drag = 3; e.Enabled = false; e.Parent = a; e:Emit(math.floor(12 * ESCALA)); Debris:AddItem(a, 1.0)
	end
end
local function escamasPulso(pos)
	if not perto(pos) then return end
	local p = Instance.new("Part"); p.Name = "FX_PulsoEscamas"; p.Shape = Enum.PartType.Ball; p.Anchored = true; p.CanCollide = false; p.CanQuery = false
	p.CanTouch = false; p.CastShadow = false; p.Material = Enum.Material.ForceField; p.Color = Color3.fromRGB(46, 104, 58)
	p.Size = Vector3.new(0.8, 0.8, 0.8); p.Position = pos; p.Transparency = 0.1; p.Parent = pasta
	TS:Create(p, TweenInfo.new(0.28, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = Vector3.new(3.2, 3.2, 3.2), Transparency = 1}):Play()
	Debris:AddItem(p, 0.35)
end

ev.OnClientEvent:Connect(function(tipo, a, b, c)
	if tipo == "ondulacao" then ondulacao(a, b)
	elseif tipo == "recusa" then recusa(a, b)
	elseif tipo == "giro_antes" then giroAntes(a, b)
	elseif tipo == "giro_pouso" then giroPouso(a, b, c)
	elseif tipo == "cauda_impacto" then caudaImpacto(a, b, c)
	elseif tipo == "escamas_pulso" then escamasPulso(a)
	elseif tipo == "limpar" then pasta:ClearAllChildren()
	end
end)
