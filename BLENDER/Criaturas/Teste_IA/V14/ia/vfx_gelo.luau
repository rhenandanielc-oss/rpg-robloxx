-- VFXGelo (ModuleScript, ReplicatedStorage.Combate_Dragoes) — efeitos e sons COSMETICOS do Gelo (kit do Dragao
-- Glacial, oficial 02/11), so no cliente. Chamado pelo VFXCombate para todo evento com el = "Gelo" e para o Frostbite.
-- Paleta: branco-gelo, azul glacial claro, azul profundo so nos nucleos; brilho limpo, sem poluicao. Nada aqui altera
-- dano/alvos nem o mapa (pecas temporarias em workspace.VFX_Temporarios). LOD pelo fator recebido (distancia/qualidade).
-- Audio: SO Pro Sound Effects (biblioteca licenciada publicada na Roblox) e o rugido ja usado pelo projeto.
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local G = {}

local C3 = Color3.fromRGB
local BRANCO_GELO, AZUL_CLARO, AZUL, AZUL_FUNDO = C3(240, 250, 255), C3(170, 225, 255), C3(110, 185, 245), C3(55, 120, 200)
local TEX = {fumaca = "rbxasset://textures/particles/smoke_main.dds", faisca = "rbxasset://textures/particles/sparkles_main.dds"}
local function id(n) return "rbxassetid://" .. n end
local SOM = {
	jato = id(9114437277), jatoCurto = id(9114437231),             -- Fire Extinguisher 2 / 1 (SFX): pressao fria
	vento = id(9125742111),                                          -- Plasma Trails Constant Airy Whooshing Windy 1 (SFX)
	tempestade = id(9125443744),                                     -- Clouds Swirl Swirling Steamy Rumble Churning 1 (SFX)
	disparo = {id(9125648149), id(9125648137), id(9125648134)},      -- Magic Zoom Up Sharp Tubular Whoosh Fast Hiss (SFX)
	estilhaco = {id(9114591164), id(9114590269)},                    -- Glass Break 9 / Glass Break 1 crash-shatter (SFX)
	estilhacoForte = id(9114590476),                                 -- Glass Break 1: thin plate shatters twice (SFX)
	rachar = id(9118762653),                                         -- Safety Glass 4: slow cracking (SFX)
	rugido = id(9113985445),                                         -- Creature Roar Deep Throaty Growls 2 (SFX)
}
local function seq(cs) local k = {}; for i, c in ipairs(cs) do table.insert(k, ColorSequenceKeypoint.new((i - 1) / (#cs - 1), c)) end; return ColorSequence.new(k) end
local function ns(...) local a = {...}; local k = {}; for i = 1, #a, 2 do table.insert(k, NumberSequenceKeypoint.new(a[i], a[i + 1])) end; return NumberSequence.new(k) end

-- ===== utilitarios ================================================================================================
local function pastaFX()
	local f = workspace:FindFirstChild("VFX_Temporarios")
	if not f then f = Instance.new("Folder"); f.Name = "VFX_Temporarios"; f.Parent = workspace end
	return f
end
local function peca(props, classe)
	local p = Instance.new(classe or "Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	for k, v in pairs(props) do p[k] = v end
	p.Parent = props.Parent or pastaFX(); return p
end
local function ancora(pos) local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain; return a end
local function emissor(pai, t) local e = Instance.new("ParticleEmitter"); for k, v in pairs(t) do e[k] = v end; e.Parent = pai; return e end
local luzes = 0
local function luz(pai, cor, brilho, alcance, dur)
	if luzes >= 6 then return end
	local l = Instance.new("PointLight"); l.Color = cor; l.Brightness = brilho; l.Range = alcance; l.Shadows = false; l.Parent = pai; luzes += 1
	if dur then
		TweenService:Create(l, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Brightness = 0}):Play()
		task.delay(dur, function() l:Destroy(); luzes -= 1 end)
	end
	return l
end
local function liberarLuz(l) if l and l.Parent then l:Destroy(); luzes -= 1 end end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local cacheOsso = setmetatable({}, {__mode = "k"})
local function ossoC(m, nome)
	cacheOsso[m] = cacheOsso[m] or {}
	local b = cacheOsso[m][nome]; if b and b.Parent then return b end
	b = osso(m, nome); cacheOsso[m][nome] = b; return b
end
local function raizDe(m) return m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart end
-- boca real (ponta do focinho) e direcao cabeca -> focinho
local function boca(m)
	local tip = ossoC(m, "mouth_upper_tip"); local cab = ossoC(m, "Cabeca")
	if tip and cab then
		local p = tip.TransformedWorldCFrame.Position; local d = p - cab.TransformedWorldCFrame.Position
		return p, d.Magnitude > 0.1 and d.Unit or m:GetPivot().LookVector
	end
	return m:GetPivot().Position + Vector3.new(0, 20, 0), m:GetPivot().LookVector
end
local function centro(m)
	local q = ossoC(m, "Quadril"); local c = ossoC(m, "Coluna3") or ossoC(m, "Coluna2")
	if q and c then return (q.TransformedWorldCFrame.Position + c.TransformedWorldCFrame.Position) / 2 end
	return m:GetPivot().Position + Vector3.new(0, 15, 0)
end
local ativosSom = {}
local function som(pai, sid, vol, tom, corte, dist)
	if not (pai and pai.Parent) then return end
	if (ativosSom[pai] or 0) >= 8 then return end
	ativosSom[pai] = (ativosSom[pai] or 0) + 1
	local s = Instance.new("Sound"); s.SoundId = sid; s.Volume = vol or 1; s.PlaybackSpeed = tom or 1
	s.RollOffMode = Enum.RollOffMode.InverseTapered; s.RollOffMinDistance = 14; s.RollOffMaxDistance = dist or 300
	s.Parent = pai; s:Play()
	local fim = corte or 6
	task.delay(fim, function()
		ativosSom[pai] = math.max(0, (ativosSom[pai] or 1) - 1)
		if s.Parent then TweenService:Create(s, TweenInfo.new(0.25), {Volume = 0}):Play(); Debris:AddItem(s, 0.3) end
	end)
	return s
end
local function somEm(pos, sid, vol, tom, corte) local a = ancora(pos); Debris:AddItem(a, (corte or 4) + 0.5); return som(a, sid, vol, tom, corte) end
local function sorteia(t) return type(t) == "table" and t[math.random(#t)] or t end
local function tomVoz(m) return (m and m:GetAttribute("TomVoz")) or 1 end
local function anel(c, raioFinal, cor, dur, espessura, transp, normal)
	local cf = normal and (CFrame.lookAt(c, c + normal) * CFrame.Angles(0, math.rad(90), 0)) or (CFrame.new(c) * CFrame.Angles(0, 0, math.rad(90)))
	local a = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(espessura or 0.6, 4, 4), Material = Enum.Material.Neon, Color = cor, Transparency = transp or 0.4, CFrame = cf})
	TweenService:Create(a, TweenInfo.new(dur, Enum.EasingStyle.Quint, Enum.EasingDirection.Out), {Size = Vector3.new(0.2, raioFinal * 2, raioFinal * 2), Transparency = 1}):Play()
	Debris:AddItem(a, dur + 0.05)
end
-- cristal de gelo: dois prismas (cunhas costas com costas) com nucleo leve; nasce de baixo e afunda ao sumir
local function cristal(base, up, altura, largura, vida)
	local m = Instance.new("Model"); m.Name = "Cristal"
	up = (up or Vector3.yAxis).Unit
	local x = up:Cross(Vector3.zAxis); if x.Magnitude < 0.1 then x = up:Cross(Vector3.xAxis) end
	local cf0 = CFrame.fromMatrix(base, x.Unit, up) * CFrame.Angles(math.rad(math.random(-18, 18)), math.random() * 6.28, math.rad(math.random(-18, 18)))
	local cor = AZUL_CLARO:Lerp(BRANCO_GELO, math.random() * 0.5)
	local fim = {}
	for i = 0, 1 do
		local cf = cf0 * CFrame.new(0, altura / 2, (i == 0 and 1 or -1) * largura * 0.25) * CFrame.Angles(0, i * math.pi, 0)
		local p = peca({Size = Vector3.new(largura, altura, largura * 0.5), Material = Enum.Material.Ice, Color = cor, Transparency = 0.15,
			Reflectance = 0.05, CFrame = cf - up * altura, Parent = m}, "WedgePart")
		table.insert(fim, {p, cf})
	end
	local nucleo = peca({Size = Vector3.new(largura * 0.3, altura * 0.7, largura * 0.3), Material = Enum.Material.Neon, Color = AZUL_CLARO, Transparency = 0.55,
		CFrame = cf0 * CFrame.new(0, altura * 0.35, 0) - up * altura, Parent = m})
	table.insert(fim, {nucleo, cf0 * CFrame.new(0, altura * 0.35, 0)})
	m.Parent = pastaFX()
	for _, x2 in ipairs(fim) do TweenService:Create(x2[1], TweenInfo.new(0.22, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {CFrame = x2[2]}):Play() end
	task.delay(vida, function()
		for _, x2 in ipairs(fim) do
			if x2[1].Parent then TweenService:Create(x2[1], TweenInfo.new(0.7, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = x2[2] - up * altura * 0.8, Transparency = 1}):Play() end
		end
		Debris:AddItem(m, 0.75)
	end)
	return m
end
-- estilhaco contido: lascas de vidro-gelo, vapor frio e brilho curto
local function estilhaco(pos, escala, fator, normal)
	if fator <= 0 then return end
	local a = ancora(pos); Debris:AddItem(a, 2.5)
	emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightInfluence = 0.6, LightEmission = 0.2, Size = ns(0, 2 * escala, 1, 9 * escala),
		Transparency = ns(0, 0.35, 1, 1), Lifetime = NumberRange.new(0.6, 1.1), Speed = NumberRange.new(6, 18), SpreadAngle = Vector2.new(180, 180), Drag = 3,
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-40, 40), Rate = 0}):Emit(math.floor(14 * escala * fator))
	emissor(a, {Texture = TEX.faisca, Color = seq({C3(255, 255, 255), AZUL_CLARO}), LightEmission = 1, Size = ns(0, 0.5 * escala, 1, 0), Lifetime = NumberRange.new(0.4, 0.9),
		Speed = NumberRange.new(25, 60), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, -40, 0), Drag = 1.2, Rate = 0}):Emit(math.floor(24 * escala * fator))
	for i = 1, math.floor(7 * escala * fator) do
		local s = 0.4 + math.random() * 0.9 * escala
		local l = peca({Size = Vector3.new(s, s * 1.6, s * 0.4), Material = Enum.Material.Glass, Color = AZUL_CLARO:Lerp(BRANCO_GELO, math.random()), Transparency = 0.25,
			CFrame = CFrame.new(pos) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)}, "WedgePart")
		local dir = (Vector3.new(math.random() - 0.5, math.random() * 0.8, math.random() - 0.5) + (normal or Vector3.zero) * 0.6).Unit
		local alvo = pos + dir * (5 + math.random() * 9) * escala
		TweenService:Create(l, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Position = alvo, Orientation = l.Orientation + Vector3.new(math.random(-200, 200), math.random(-200, 200), 0)}):Play()
		task.delay(0.35, function() if l.Parent then TweenService:Create(l, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Position = alvo - Vector3.new(0, 6 * escala, 0), Transparency = 1}):Play() end end)
		Debris:AddItem(l, 0.9)
	end
	luz(a, AZUL_CLARO, 3, 26 * escala, 0.35)
	anel(pos, 9 * escala, AZUL_CLARO, 0.35, 0.3, 0.45, normal)
end
-- brilho frio no corpo inteiro (Highlight) — fill 0..1 (1 = apagado)
local brilhos = {}
local function brilhoCorpo(m, fill, contorno, dur)
	local h = brilhos[m]
	if not (h and h.Parent) then
		h = Instance.new("Highlight"); h.Name = "BrilhoGelo"; h.FillColor = C3(140, 215, 255); h.OutlineColor = C3(225, 245, 255)
		h.FillTransparency = 1; h.OutlineTransparency = 1; h.DepthMode = Enum.HighlightDepthMode.Occluded; h.Adornee = m; h.Parent = m; brilhos[m] = h
	end
	TweenService:Create(h, TweenInfo.new(dur or 0.3, Enum.EasingStyle.Sine, Enum.EasingDirection.Out), {FillTransparency = fill, OutlineTransparency = contorno or 1}):Play()
end

-- ===== Sangue Glacial: olhos e boca com brilho frio em combate; "respiracao" de nevoa na boca =====================
local sangue = {}
local function ligarSangue(m)
	local cab = ossoC(m, "Cabeca"); local tip = ossoC(m, "mouth_upper_tip"); if not cab then return end
	local s = {}
	s.l = Instance.new("PointLight"); s.l.Color = C3(150, 215, 255); s.l.Brightness = 0; s.l.Range = 14; s.l.Shadows = false; s.l.Parent = cab
	TweenService:Create(s.l, TweenInfo.new(0.6), {Brightness = 1.6}):Play()
	if tip then
		s.e = emissor(tip, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightEmission = 0.25, LightInfluence = 0.7, Size = ns(0, 0.8, 1, 4),
			Transparency = ns(0, 0.55, 1, 1), Lifetime = NumberRange.new(1.0, 1.6), Speed = NumberRange.new(1, 3), Acceleration = Vector3.new(0, -2.5, 0),
			SpreadAngle = Vector2.new(30, 30), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-20, 20), Rate = 5})
		s.c = emissor(tip, {Texture = TEX.faisca, Color = ColorSequence.new(AZUL_CLARO), LightEmission = 1, Size = ns(0, 0.25, 1, 0), Lifetime = NumberRange.new(0.5, 1.0),
			Speed = NumberRange.new(0.5, 2), SpreadAngle = Vector2.new(180, 180), Rate = 4})
	end
	sangue[m] = s
end
local function desligarSangue(m)
	local s = sangue[m]; sangue[m] = nil; if not s then return end
	if s.l then TweenService:Create(s.l, TweenInfo.new(0.8), {Brightness = 0}):Play(); Debris:AddItem(s.l, 0.9) end
	for _, e in ipairs({s.e, s.c}) do if e then e.Enabled = false; Debris:AddItem(e, 1.8) end end
end

-- ===== Frostbite nos alvos: nevoa fria, cristais, tom azulado crescente; congelado = crosta de gelo ===============
local frio, crostas = {}, {}
local vigiar = setmetatable({}, {__mode = "k"})                  -- alvos atingidos fora da raiz do Workspace
local function ligarFrio(m)
	local r = raizDe(m); if not r then return end
	local grande = m:GetAttribute("FormaRegional") ~= nil; local k = grande and 3 or 1
	local a = Instance.new("Attachment"); a.Name = "VFX_Frostbite"; a.Parent = (grande and ossoC(m, "Quadril")) or r
	local f = {a = a, k = k}
	f.nevoa = emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightInfluence = 0.8, Size = ns(0, 1.2 * k, 1, 4 * k), Transparency = ns(0, 0.6, 1, 1),
		Lifetime = NumberRange.new(1, 1.6), Speed = NumberRange.new(0.5, 2), Acceleration = Vector3.new(0, -1.5, 0), Shape = Enum.ParticleEmitterShape.Box,
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-15, 15), Rate = 0})
	f.cristais = emissor(a, {Texture = TEX.faisca, Color = ColorSequence.new(C3(220, 245, 255)), LightEmission = 1, Size = ns(0, 0.3 * k, 1, 0),
		Lifetime = NumberRange.new(0.6, 1.2), Speed = NumberRange.new(1, 4), SpreadAngle = Vector2.new(180, 180), Shape = Enum.ParticleEmitterShape.Box, Rate = 0})
	f.h = Instance.new("Highlight"); f.h.FillColor = C3(150, 210, 255); f.h.OutlineColor = C3(220, 245, 255); f.h.FillTransparency = 1; f.h.OutlineTransparency = 1
	f.h.DepthMode = Enum.HighlightDepthMode.Occluded; f.h.Adornee = m; f.h.Parent = m
	frio[m] = f
end
local function atualizarFrio(m, v)
	local f = frio[m]; if not f then return end
	local x = math.clamp(v / 100, 0, 1)
	f.nevoa.Rate = (2 + 10 * x) * f.k; f.cristais.Rate = (2 + 14 * x) * f.k
	if not (brilhos[m] and brilhos[m].FillTransparency < 0.8) then
		TweenService:Create(f.h, TweenInfo.new(0.25), {FillTransparency = 1 - 0.5 * x, OutlineTransparency = 1 - 0.6 * x}):Play()
	end
end
local function desligarFrio(m)
	local f = frio[m]; frio[m] = nil; if not f then return end
	f.nevoa.Enabled = false; f.cristais.Enabled = false; Debris:AddItem(f.a, 1.8)
	TweenService:Create(f.h, TweenInfo.new(0.5), {FillTransparency = 1, OutlineTransparency = 1}):Play(); Debris:AddItem(f.h, 0.6)
end
local function congelar(alvo, dur, fator)
	local r = alvo and raizDe(alvo); if not r or crostas[alvo] then return end
	local grande = alvo:GetAttribute("FormaRegional") ~= nil
	local ext = grande and Vector3.new(14, 10, 22) or alvo:GetExtentsSize()
	local pecas = {}
	local n = grande and 10 or 7
	for i = 1, n do
		local ang = i / n * math.pi * 2 + math.random() * 0.4
		local off = Vector3.new(math.cos(ang) * ext.X * 0.42, (math.random() - 0.35) * ext.Y * 0.7, math.sin(ang) * ext.Z * 0.42)
		local s = (grande and 4 or 1.3) * (0.7 + math.random() * 0.6)
		local p = peca({Size = Vector3.new(s, s * 1.8, s * 0.8), Material = Enum.Material.Ice, Color = AZUL_CLARO:Lerp(BRANCO_GELO, math.random() * 0.6), Transparency = 0.2,
			CFrame = r.CFrame * CFrame.new(off) * CFrame.Angles(math.random() * 0.8, math.random() * 6, math.random() * 0.8)}, "WedgePart")
		p.Size = p.Size * 0.2
		TweenService:Create(p, TweenInfo.new(0.18, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {Size = Vector3.new(s, s * 1.8, s * 0.8)}):Play()
		table.insert(pecas, {p, r.CFrame:ToObjectSpace(p.CFrame)})
	end
	crostas[alvo] = pecas
	somEm(r.Position, SOM.rachar, 0.9, 1.15, 1.4)
	local con; con = RunService.Heartbeat:Connect(function()
		if not r.Parent then con:Disconnect(); return end
		for _, x in ipairs(pecas) do if x[1].Parent then x[1].CFrame = r.CFrame * x[2] end end
	end)
	task.delay(dur, function()
		con:Disconnect(); crostas[alvo] = nil
		if r.Parent then estilhaco(r.Position, grande and 1.4 or 0.7, math.max(fator, 0.3)); somEm(r.Position, sorteia(SOM.estilhaco), 0.9, 1.1, 2) end
		for _, x in ipairs(pecas) do x[1]:Destroy() end
	end)
end
task.spawn(function()
	while true do
		task.wait(0.25)
		local agora = workspace:GetServerTimeNow()
		local vistos = {}
		local lista = workspace:GetChildren(); for a in pairs(vigiar) do if a.Parent and a.Parent ~= workspace then table.insert(lista, a) end end
		for _, m in ipairs(lista) do
			if m:IsA("Model") then
				vistos[m] = true
				local v = m:GetAttribute("Frostbite")
				if v and v > 0 then if not frio[m] then ligarFrio(m) end; atualizarFrio(m, v) elseif frio[m] then desligarFrio(m) end
				local sg = m:GetAttribute("SangueGlacialFim")
				if sg and sg > agora then if not sangue[m] then ligarSangue(m) end elseif sangue[m] then desligarSangue(m) end
			end
		end
		for m in pairs(frio) do if not vistos[m] then desligarFrio(m) end end
		for m in pairs(sangue) do if not vistos[m] then desligarSangue(m) end end
	end
end)

-- ===== SOPRO GLACIAL: jato continuo (emissores reaproveitados por dragao, seguem a boca e a mira) =================
local sopro = {}
local function velPara(alc, frac, drag, vida) local d = alc * frac; if drag <= 0.01 then return d / vida end; return d * drag / (1 - math.exp(-drag * vida)) end
local function emissoresSopro(m)
	local s = sopro[m]; if s and s.anc and s.anc.Parent then return s end
	s = {anc = ancora(m:GetPivot().Position), e = {}}; sopro[m] = s
	-- nucleo: jato concentrado branco-azulado (alcance casado com a hitbox)
	s.e.nucleo = emissor(s.anc, {Texture = TEX.fumaca, Color = seq({C3(245, 252, 255), AZUL_CLARO, C3(140, 200, 245)}), LightEmission = 0.25, LightInfluence = 0.35,
		Size = ns(0, 1.0, 0.25, 4.5, 1, 11), Transparency = ns(0, 0.3, 0.7, 0.55, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-60, 60),
		SpreadAngle = Vector2.new(4, 4), EmissionDirection = Enum.NormalId.Front, Rate = 0, ZOffset = 1})
	-- nevoa fria envolvendo o jato (recebe luz da cena: branca, pesada, cai um pouco)
	s.e.nevoa = emissor(s.anc, {Texture = TEX.fumaca, Color = seq({C3(225, 238, 248), C3(185, 212, 235)}), LightEmission = 0, LightInfluence = 1,
		Size = ns(0, 3, 1, 18), Transparency = ns(0, 0.62, 0.6, 0.78, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-25, 25),
		SpreadAngle = Vector2.new(9, 9), Acceleration = Vector3.new(0, -4, 0), EmissionDirection = Enum.NormalId.Front, Rate = 0, ZOffset = -1})
	-- cristais finos cintilando no fluxo
	s.e.cristais = emissor(s.anc, {Texture = TEX.faisca, Color = seq({C3(255, 255, 255), AZUL_CLARO}), LightEmission = 1, Size = ns(0, 0.45, 0.7, 0.3, 1, 0),
		SpreadAngle = Vector2.new(7, 7), EmissionDirection = Enum.NormalId.Front, Rate = 0})
	-- lancas de pressao junto a boca (curtas, muito claras)
	s.e.jato = emissor(s.anc, {Texture = TEX.fumaca, Color = ColorSequence.new(C3(225, 245, 255)), LightEmission = 0.6, LightInfluence = 0, Size = ns(0, 0.8, 1, 3.5),
		Transparency = ns(0, 0.2, 1, 1), Lifetime = NumberRange.new(0.12, 0.18), Speed = NumberRange.new(120, 140), SpreadAngle = Vector2.new(2, 2),
		EmissionDirection = Enum.NormalId.Front, Rate = 0, ZOffset = 2})
	return s
end
local PERF = {nucleo = {1.0, 0.7, 0.95, 140}, nevoa = {0.9, 1.5, 1.7, 30}, cristais = {1.05, 0.9, 1.0, 120}, jato = {nil, nil, nil, 70}}
local function ligarSopro(m, ligado, f, alvo, alcance)
	local s = emissoresSopro(m); s.alvo = alvo
	if ligado then
		if s.con then s.con:Disconnect() end
		s.con = RunService.RenderStepped:Connect(function()
			local b, d = boca(m)
			if s.alvo then local v = s.alvo - b; if v.Magnitude > 5 then d = (d * 0.3 + v.Unit * 0.7).Unit end end
			s.anc.WorldCFrame = CFrame.lookAt(b, b + d)
		end)
		for k, e in pairs(s.e) do
			local p = PERF[k]; e.Rate = p[4] * f
			if p[1] and alcance then
				local v = velPara(alcance, p[1], p[2], p[3]); e.Drag = p[2]; e.Lifetime = NumberRange.new(p[3] * 0.9, p[3]); e.Speed = NumberRange.new(v * 0.92, v * 1.04)
			end
		end
		if not s.luz then s.luz = luz(s.anc, C3(160, 215, 255), 1.8, 34) end
	else
		for _, e in pairs(s.e) do e.Rate = 0 end
		liberarLuz(s.luz); s.luz = nil
		task.delay(1.8, function() if s.con and s.e.nucleo.Rate == 0 then s.con:Disconnect(); s.con = nil end end)
	end
end
local soproTok, soproMira, soproSom = {}, {}, {}
local function soproEvento(m, d, f)
	local pp = m.PrimaryPart
	if d.fase == "preparo" then                                       -- frio se acumulando na boca, peito brilha de leve
		local b = boca(m); local a = ancora(b); Debris:AddItem(a, 1.3)
		emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightEmission = 0.4, Size = ns(0, 3, 1, 0.5), Transparency = ns(0, 0.5, 1, 1),
			Lifetime = NumberRange.new(0.35, 0.6), Speed = NumberRange.new(-14, -8), SpreadAngle = Vector2.new(180, 180), Rate = 60 * f})
		emissor(a, {Texture = TEX.faisca, Color = ColorSequence.new(AZUL_CLARO), LightEmission = 1, Size = ns(0, 0.5, 1, 0), Lifetime = NumberRange.new(0.3, 0.5),
			Speed = NumberRange.new(-16, -10), SpreadAngle = Vector2.new(180, 180), Rate = 50 * f})
		luz(a, C3(160, 215, 255), 2, 22, 1.2)
		brilhoCorpo(m, 0.95, 0.93, 0.5)
		som(pp, SOM.jatoCurto, 0.45, 0.55, 1.0)
	elseif d.fase == "emissao" then
		soproTok[m] = (soproTok[m] or 0) + 1; local tok = soproTok[m]; soproMira[m] = d.alvoPos
		ligarSopro(m, true, f, d.alvoPos, d.alcance)
		-- som: pressao fria comprimida (extintor grave) em camadas + vento fino, sem estourar
		task.spawn(function()
			local lim = os.clock() + 7
			while soproTok[m] == tok and os.clock() < lim and m.Parent do
				som(pp, SOM.jato, 0.8, 0.62 + math.random() * 0.06, 2.0)
				task.wait(1.15)
			end
		end)
		soproSom[m] = som(pp, SOM.vento, 0.55, 1.25, 7)
		-- impacto continuo onde o jato toca o mundo: vapor frio, lascas e cristais pequenos que crescem e somem
		task.spawn(function()
			local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {m, pastaFX()}
			local lim, ultCristal = os.clock() + 7, 0
			while soproTok[m] == tok and os.clock() < lim and m.Parent do
				local b, dr = boca(m); local ap = soproMira[m]; if ap then dr = (ap - b).Unit end
				local h = workspace:Raycast(b, dr * (d.alcance or 100), rp)
				if h then
					estilhaco(h.Position, 0.45, f, h.Normal)
					if os.clock() - ultCristal > 0.5 and h.Normal.Y > 0.5 then ultCristal = os.clock(); cristal(h.Position, h.Normal, 2.5 + math.random() * 2, 1.2, 2.2) end
				end
				task.wait(0.25)
			end
		end)
	elseif d.fase == "mira" then soproMira[m] = d.alvoPos; local s = emissoresSopro(m); s.alvo = d.alvoPos
	elseif d.fase == "fim" then
		soproTok[m] = (soproTok[m] or 0) + 1; soproMira[m] = nil
		ligarSopro(m, false, f)
		brilhoCorpo(m, 1, 1, 0.8)
		local s = soproSom[m]; if s and s.Parent then TweenService:Create(s, TweenInfo.new(0.5), {Volume = 0}):Play(); Debris:AddItem(s, 0.6) end
		local b = boca(m); local a = ancora(b); Debris:AddItem(a, 2)               -- ultimo sopro de nevoa saindo da boca
		emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightInfluence = 0.8, Size = ns(0, 2, 1, 8), Transparency = ns(0, 0.5, 1, 1),
			Lifetime = NumberRange.new(0.9, 1.4), Speed = NumberRange.new(3, 8), Acceleration = Vector3.new(0, -3, 0), SpreadAngle = Vector2.new(40, 40), Rate = 0}):Emit(math.floor(14 * f))
	end
end

-- ===== RAJADAS DE GELO: lancas de gelo com nucleo luminoso, rastro frio e cristais na trajetoria ==================
local lancas = {}
local function rajadas(m, d, f)
	local pp = m.PrimaryPart
	if d.fase == "preparo" then
		brilhoCorpo(m, 0.95, 0.93, 0.3)
		local b = boca(m); local a = ancora(b); Debris:AddItem(a, 0.8)
		emissor(a, {Texture = TEX.faisca, Color = ColorSequence.new(AZUL_CLARO), LightEmission = 1, Size = ns(0, 0.6, 1, 0), Lifetime = NumberRange.new(0.25, 0.45),
			Speed = NumberRange.new(-14, -8), SpreadAngle = Vector2.new(180, 180), Rate = 70 * f})
		task.delay(2.3, function() brilhoCorpo(m, 1, 1, 0.6) end)
	elseif d.fase == "disparo" then
		local de, dir = d.de, d.dir
		som(pp, sorteia(SOM.disparo), 0.85, 1.25 + math.random() * 0.15, 1.2)
		som(pp, SOM.jatoCurto, 0.35, 1.4, 0.5)
		-- clarao/anel de pressao na boca e um pouco de nevoa
		anel(de + dir * 3, 6, BRANCO_GELO, 0.22, 0.25, 0.35, dir)
		local am = ancora(de); Debris:AddItem(am, 1.2)
		emissor(am, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightInfluence = 0.7, Size = ns(0, 1.5, 1, 6), Transparency = ns(0, 0.5, 1, 1),
			Lifetime = NumberRange.new(0.4, 0.7), Speed = NumberRange.new(4, 10), SpreadAngle = Vector2.new(35, 35), Rate = 0}):Emit(math.floor(8 * f))
		-- lanca: haste de gelo translucido facetada + nucleo luminoso + ponta afiada
		local cf0 = CFrame.lookAt(de, de + dir)
		local corpo = peca({Size = Vector3.new(1.1, 1.1, 7), Material = Enum.Material.Glass, Color = C3(205, 238, 255), Transparency = 0.2, Reflectance = 0.1, CFrame = cf0})
		local nucleo = peca({Size = Vector3.new(0.45, 0.45, 6), Material = Enum.Material.Neon, Color = AZUL_CLARO, Transparency = 0.15, CFrame = cf0})
		local ponta = peca({Size = Vector3.new(1.1, 1.1, 2.6), Material = Enum.Material.Ice, Color = BRANCO_GELO, Transparency = 0.1, CFrame = cf0}, "WedgePart")
		local a0 = Instance.new("Attachment", corpo); a0.Position = Vector3.new(0, 0.5, 2.5); local a1 = Instance.new("Attachment", corpo); a1.Position = Vector3.new(0, -0.5, 2.5)
		local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = 0.35; tr.LightEmission = 0.7; tr.FaceCamera = true
		tr.Color = seq({C3(255, 255, 255), AZUL_CLARO, AZUL}); tr.Transparency = ns(0, 0.15, 1, 1); tr.WidthScale = ns(0, 1, 1, 0.1); tr.Parent = corpo
		local ac = Instance.new("Attachment", corpo); ac.Position = Vector3.new(0, 0, 2)
		emissor(ac, {Texture = TEX.faisca, Color = ColorSequence.new(C3(225, 245, 255)), LightEmission = 1, Size = ns(0, 0.35, 1, 0), Lifetime = NumberRange.new(0.3, 0.6),
			Speed = NumberRange.new(2, 6), SpreadAngle = Vector2.new(180, 180), Rate = 45 * f})
		emissor(ac, {Texture = TEX.fumaca, Color = ColorSequence.new(BRANCO_GELO), LightInfluence = 0.8, Size = ns(0, 0.8, 1, 3), Transparency = ns(0, 0.65, 1, 1),
			Lifetime = NumberRange.new(0.4, 0.7), Speed = NumberRange.new(0.5, 2), Rate = 25 * f})
		local l = luz(nucleo, C3(160, 215, 255), 2, 16)
		local t0 = os.clock(); local giro = 0
		local reg = {pecas = {corpo, nucleo, ponta}, luz = l}
		lancas[m] = lancas[m] or {}; lancas[m][d.indice] = reg
		local tmax = (d.alcance or 230) / (d.vel or 240) + 0.4
		reg.con = RunService.RenderStepped:Connect(function(dt)
			local t = os.clock() - t0
			if t > tmax or reg.fim then
				reg.con:Disconnect(); liberarLuz(l)
				for _, p in ipairs(reg.pecas) do p:Destroy() end
				return
			end
			giro += dt * 9
			local p = de + dir * (d.vel or 240) * math.min(t, tmax)
			local cf = CFrame.lookAt(p, p + dir) * CFrame.Angles(0, 0, giro)
			corpo.CFrame = cf; nucleo.CFrame = cf; ponta.CFrame = cf * CFrame.new(0, 0, -4.7) * CFrame.Angles(math.rad(90), 0, 0)
		end)
	elseif d.fase == "impacto" or d.fase == "dissipa" then
		local reg = lancas[m] and lancas[m][d.indice]; if reg then reg.fim = true; lancas[m][d.indice] = nil end
		if d.fase == "impacto" then
			estilhaco(d.pos, d.acertou and 1.1 or 0.8, f, d.normal)
			somEm(d.pos, sorteia(SOM.estilhaco), d.acertou and 1.1 or 0.8, 1.0 + math.random() * 0.15, 2)
			if not d.acertou and d.normal and d.normal.Y > 0.4 then      -- errou no chao: pequeno impacto glacial (3 cristais)
				for i = 1, 3 do
					local off = Vector3.new(math.random(-20, 20) / 10, 0, math.random(-20, 20) / 10)
					cristal(d.pos + off, (d.normal + Vector3.new(math.random() - 0.5, 0, math.random() - 0.5) * 0.5).Unit, 2.5 + math.random() * 2.5, 1.1, 2.5)
				end
			end
		else
			local a = ancora(d.pos); Debris:AddItem(a, 1.2)
			emissor(a, {Texture = TEX.faisca, Color = ColorSequence.new(AZUL_CLARO), LightEmission = 1, Size = ns(0, 0.5, 1, 0), Lifetime = NumberRange.new(0.3, 0.6),
				Speed = NumberRange.new(5, 14), SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(math.floor(14 * f))
		end
	end
end

-- ===== ZERO ABSOLUTO: tensao -> onda circular, chao tomado pelo gelo, cristais emergindo, neblina rasteira =========
local function zero(m, d, f)
	local pp = m.PrimaryPart
	if d.fase == "preparo" then
		brilhoCorpo(m, 0.86, 0.85, d.emissao or 1)
		som(pp, SOM.jato, 0.5, 0.45, 1.2)
		local c = centro(m); local a = ancora(c); Debris:AddItem(a, (d.emissao or 1) + 0.3)
		-- o frio e PUXADO para o corpo (particulas convergem) e uma neblina comeca a escorrer para o chao
		emissor(a, {Texture = TEX.faisca, Color = ColorSequence.new(AZUL_CLARO), LightEmission = 1, Size = ns(0, 0.7, 1, 0), Lifetime = NumberRange.new(0.5, 0.8),
			Speed = NumberRange.new(-45, -30), SpreadAngle = Vector2.new(180, 180), Shape = Enum.ParticleEmitterShape.Sphere, Rate = 90 * f})
		emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightInfluence = 0.8, Size = ns(0, 4, 1, 12), Transparency = ns(0, 0.6, 1, 1),
			Lifetime = NumberRange.new(1.0, 1.4), Speed = NumberRange.new(4, 9), Acceleration = Vector3.new(0, -14, 0), SpreadAngle = Vector2.new(180, 180), Rate = 18 * f})
		local l = luz(a, C3(160, 215, 255), 0, 40); if l then TweenService:Create(l, TweenInfo.new(d.emissao or 1), {Brightness = 2}):Play(); task.delay((d.emissao or 1) + 0.4, function() liberarLuz(l) end) end
	elseif d.fase == "onda" then
		local c = d.centro; local R, vel = d.raio or 64, d.vel or 95; local tOnda = R / vel
		local normal = d.normal or Vector3.yAxis
		brilhoCorpo(m, 0.62, 0.55, 0.12); task.delay(0.6, function() brilhoCorpo(m, 1, 1, 1.0) end)
		som(pp, SOM.jato, 1.0, 0.42, 1.8); som(pp, sorteia(SOM.estilhaco), 0.9, 0.7, 2)
		somEm(c, SOM.rachar, 1.2, 0.8, 4.5)
		local ac = ancora(c + Vector3.new(0, 1, 0)); Debris:AddItem(ac, (d.zona or 4) + 2)
		luz(ac, C3(170, 225, 255), 2.2, R * 0.8, 0.9)
		-- frente da onda (anel luminoso fino + anel de pressao mais largo e transparente)
		anel(c + normal * 0.6, R, BRANCO_GELO, tOnda, 1.2, 0.25, normal)
		anel(c + normal * 2.5, R * 1.08, AZUL_CLARO, tOnda * 1.15, 4, 0.65, normal)
		-- lencol de nevoa rasteira que acompanha a onda: 12 bocas em circulo, cada uma soprando para fora
		for k = 1, 12 do
			local ang = k / 12 * math.pi * 2; local dh = Vector3.new(math.cos(ang), 0, math.sin(ang))
			local a = Instance.new("Attachment"); a.Parent = workspace.Terrain; a.WorldCFrame = CFrame.lookAt(c + Vector3.new(0, 1.5, 0) + dh * 4, c + Vector3.new(0, 1.5, 0) + dh * 5)
			Debris:AddItem(a, 2.5)
			emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, C3(205, 228, 242)}), LightInfluence = 1, Size = ns(0, 5, 1, 16), Transparency = ns(0, 0.45, 1, 1),
				Lifetime = NumberRange.new(1.4, 2.0), Speed = NumberRange.new(vel * 0.45, vel * 0.6), SpreadAngle = Vector2.new(14, 3), Drag = 0.9,
				Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-20, 20), Rate = 0, EmissionDirection = Enum.NormalId.Front}):Emit(math.max(2, math.floor(6 * f)))
		end
		if d.noChao then
			-- chao dominado pelo frio: disco de gelo que se espalha com a onda e fica durante a zona
			local disco = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.25, 4, 4), Material = Enum.Material.Ice, Color = C3(185, 220, 245), Transparency = 0.45,
				CFrame = CFrame.lookAt(c + normal * 0.12, c + normal * 1.12) * CFrame.Angles(0, math.rad(90), 0)})
			local zr = d.zonaRaio or 52
			TweenService:Create(disco, TweenInfo.new(zr / vel, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = Vector3.new(0.25, zr * 2, zr * 2)}):Play()
			task.delay(d.zona or 4, function() if disco.Parent then TweenService:Create(disco, TweenInfo.new(1.2), {Transparency = 1}):Play(); Debris:AddItem(disco, 1.3) end end)
			-- neblina fria rasteira persistente sobre a zona (pontos espalhados, fumaca lenta que escorre pelo chao)
			for k = 1, math.max(3, math.floor(7 * f)) do
				local ang = math.random() * math.pi * 2; local rr = math.sqrt(math.random()) * zr * 0.85
				local a = ancora(c + Vector3.new(math.cos(ang) * rr, 1.5, math.sin(ang) * rr)); Debris:AddItem(a, (d.zona or 4) + 3.5)
				local nz = emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, C3(210, 232, 245)}), LightInfluence = 1, Size = ns(0, 7, 1, 16),
					Transparency = ns(0, 0.75, 0.5, 0.62, 1, 1), Lifetime = NumberRange.new(2.5, 3.5), Speed = NumberRange.new(2, 6), SpreadAngle = Vector2.new(180, 180),
					Acceleration = Vector3.new(0, -2, 0), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-10, 10), Rate = 3})
				task.delay(d.zona or 4, function() nz.Enabled = false end)
			end
			-- cristais emergindo da superficie em aneis, no tempo da onda (raycast no relevo real)
			local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {m, pastaFX()}
			local aneis = {0.35, 0.6, 0.85}
			for ia, fr in ipairs(aneis) do
				local r = R * fr; local n = math.max(6, math.floor((8 + ia * 4) * f))
				task.delay(r / vel, function()
					local g0 = math.random() * math.pi * 2
					for k = 1, n do
						local ang = g0 + k / n * math.pi * 2 + math.random() * 0.3
						local xz = c + Vector3.new(math.cos(ang), 0, math.sin(ang)) * (r + math.random(-3, 3))
						local h = workspace:Raycast(xz + Vector3.new(0, 18, 0), Vector3.new(0, -40, 0), rp)
						if h then
							local alt = (11 - ia * 2) * (0.7 + math.random() * 0.6)
							cristal(h.Position, (h.Normal + (h.Position - c).Unit * 0.35).Unit, alt, alt * 0.3, (d.zona or 4) - r / vel + 0.4)
						end
					end
				end)
			end
		end
	end
end

-- ===== NEVASCA ANCESTRAL: corpo inteiro azul brilhante, tempestade de fragmentos em ondas =========================
local nevascas = {}
local function fragmentos(m, c, raio, f, n)
	for i = 1, math.floor(n * f) do
		local dir = Vector3.new(math.random() - 0.5, (math.random() - 0.35) * 0.9, math.random() - 0.5).Unit
		local s = 0.5 + math.random() * 1.4
		local p = peca({Size = Vector3.new(s * 0.45, s * 0.45, s * 3.2), Material = math.random() < 0.5 and Enum.Material.Glass or Enum.Material.Ice,
			Color = AZUL_CLARO:Lerp(BRANCO_GELO, math.random()), Transparency = 0.15, CFrame = CFrame.lookAt(c + dir * 6, c + dir * 7)}, "WedgePart")
		local alvo = c + dir * raio * (0.75 + math.random() * 0.35)
		local dur = 0.32 + math.random() * 0.22
		TweenService:Create(p, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = CFrame.lookAt(alvo, alvo + dir), Transparency = 0.6}):Play()
		Debris:AddItem(p, dur + 0.05)
	end
end
local function nevasca(m, d, f)
	local pp = m.PrimaryPart
	if d.fase == "inicio" then
		local reg = {itens = {}}; nevascas[m] = reg
		local f2 = math.max(f, 0.35)
		brilhoCorpo(m, 0.8, 0.85, 0.6)
		-- subida: asas puxam ar frio, cristais saem das pontas
		local c0 = centro(m)
		som(pp, SOM.vento, 0.9, 0.7, 2.5)
		-- rugido muito alto + corpo INTEIRO azul brilhante (Highlight cobre cabeca, olhos, tronco, patas, garras, cauda e asas)
		task.delay(d.rugido or 1.75, function()
			if not m.Parent or nevascas[m] ~= reg then return end
			som(pp, SOM.rugido, 2.2, 0.7 * tomVoz(m), 3.0, 420)
			brilhoCorpo(m, 0.28, 0, 0.35)
			local cb = ossoC(m, "Coluna2") or pp
			local l = Instance.new("PointLight"); l.Color = C3(150, 215, 255); l.Brightness = 0; l.Range = 60; l.Shadows = false; l.Parent = cb
			TweenService:Create(l, TweenInfo.new(0.35), {Brightness = 5}):Play(); table.insert(reg.itens, l)
			-- aura de energia glacial no corpo todo (pontos nos ossos principais e nas asas)
			for _, n in ipairs({"Coluna2", "Pescoco2", "Cabeca", "Cauda3", "Cauda5", "Quadril", "AsaE_2", "AsaD_2", "wing_tip_l", "wing_tip_r", "wing_3_l", "wing_3_r"}) do
				local b = ossoC(m, n)
				if b then
					table.insert(reg.itens, emissor(b, {Texture = TEX.faisca, Color = seq({C3(255, 255, 255), AZUL_CLARO}), LightEmission = 1, Size = ns(0, 0.9, 1, 0),
						Lifetime = NumberRange.new(0.5, 0.9), Speed = NumberRange.new(6, 14), SpreadAngle = Vector2.new(180, 180), Rate = 16 * f2}))
				end
			end
			-- tempestade glacial ao redor: anel de neve girando + nevoa + fragmentos rapidos continuos
			local ac = ancora(centro(m)); table.insert(reg.itens, ac)
			table.insert(reg.itens, emissor(ac, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightInfluence = 0.8, LightEmission = 0.05, Size = ns(0, 4, 1, 14),
				Transparency = ns(0, 0.72, 1, 1), Lifetime = NumberRange.new(1.0, 1.5), Speed = NumberRange.new(70, 100), SpreadAngle = Vector2.new(180, 30),
				Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-80, 80), Drag = 1.2, Rate = 18 * f2}))
			table.insert(reg.itens, emissor(ac, {Texture = TEX.faisca, Color = seq({C3(255, 255, 255), AZUL_CLARO}), LightEmission = 1, Size = ns(0, 0.8, 1, 0.2),
				Lifetime = NumberRange.new(0.5, 0.9), Speed = NumberRange.new(140, 200), SpreadAngle = Vector2.new(180, 60), Rate = 120 * f2}))
			local giro = Instance.new("Attachment"); giro.Parent = workspace.Terrain; table.insert(reg.itens, giro)
			local braco = {}
			for k = 1, 3 do
				local a = Instance.new("Attachment"); a.Parent = workspace.Terrain; table.insert(reg.itens, a); table.insert(braco, a)
				table.insert(reg.itens, emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightInfluence = 0.7, Size = ns(0, 3, 1, 8),
					Transparency = ns(0, 0.65, 1, 1), Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(2, 6), Rate = 22 * f2}))
			end
			local t0 = os.clock()
			reg.con = RunService.RenderStepped:Connect(function()
				if not m.Parent then return end
				local c = centro(m); ac.WorldPosition = c
				local t = os.clock() - t0
				for k, a in ipairs(braco) do
					local ang = t * 3.2 + k * 2.094; local r = 38 + 10 * math.sin(t * 2 + k)
					a.WorldPosition = c + Vector3.new(math.cos(ang) * r, -8 + 10 * math.sin(t * 1.4 + k), math.sin(ang) * r)
				end
			end)
			reg.somT = som(pp, SOM.tempestade, 1.4, 1.0, (d.duracao or 5.6) - (d.rugido or 1.75), 400)
			som(pp, SOM.vento, 1.1, 0.85, 3.5, 400)
		end)
		-- fim do brilho: diminui suave e volta ao normal
		task.delay((d.duracao or 5.6) - 0.9, function()
			if nevascas[m] ~= reg then return end
			brilhoCorpo(m, 1, 1, 1.1)
			for _, x in ipairs(reg.itens) do
				if x:IsA("ParticleEmitter") then x.Enabled = false; Debris:AddItem(x, 1.5)
				elseif x:IsA("PointLight") then TweenService:Create(x, TweenInfo.new(1.0), {Brightness = 0}):Play(); Debris:AddItem(x, 1.1)
				else Debris:AddItem(x, 1.6) end
			end
			task.delay(1.5, function() if reg.con then reg.con:Disconnect() end end)
		end)
		task.delay(0.4, function() if m.Parent then som(pp, sorteia(SOM.disparo), 0.6, 0.7, 1) end end)
		local a = ancora(c0); Debris:AddItem(a, 1.8)
		emissor(a, {Texture = TEX.faisca, Color = ColorSequence.new(AZUL_CLARO), LightEmission = 1, Size = ns(0, 0.8, 1, 0), Lifetime = NumberRange.new(0.6, 1.0),
			Speed = NumberRange.new(-30, -18), SpreadAngle = Vector2.new(180, 180), Shape = Enum.ParticleEmitterShape.Sphere, Rate = 60 * f2})
	elseif d.fase == "onda" then
		local c = d.pos or centro(m); local i = d.indice or 1
		fragmentos(m, c, d.raio or 95, math.max(f, 0.35), i == 1 and 46 or 26)
		anel(c, (d.raio or 95) * (i == 1 and 1 or 0.8), BRANCO_GELO, 0.55, 1.5, i == 1 and 0.3 or 0.5)
		anel(c, (d.raio or 95) * 0.7, AZUL_CLARO, 0.45, 0.6, 0.55, Vector3.new(0, 0, 1))
		brilhoCorpo(m, 0.1, 0, 0.08); task.delay(0.22, function() if nevascas[m] then brilhoCorpo(m, 0.28, 0, 0.3) end end)
		som(pp, sorteia(SOM.disparo), 1.2, 0.8 + 0.1 * i, 1.2, 400); som(pp, sorteia(SOM.estilhaco), 1.0, 0.75, 2, 400)
		if i == 1 then som(pp, SOM.estilhacoForte, 1.0, 0.8, 3, 400) end
	elseif d.fase == "fim" then
		nevascas[m] = nil
	end
end

-- ===== despacho ==================================================================================================
function G.evento(d, f)
	local m = d.d; if not m or not m.Parent then return end
	if d.fase == "reacao" then                                           -- alvo atingido por Gelo: estalo frio curto
		local a = d.alvo; if not (a and a.Parent) then return end
		vigiar[a] = true
		local h = Instance.new("Highlight"); h.FillColor = C3(170, 225, 255); h.OutlineTransparency = 1
		h.FillTransparency = d.intensidade == "pesado" and 0.2 or d.intensidade == "moderado" and 0.4 or 0.6; h.Parent = a
		TweenService:Create(h, TweenInfo.new(0.4), {FillTransparency = 1}):Play(); Debris:AddItem(h, 0.45)
		local r = raizDe(a); if r and f > 0 then
			local a2 = ancora(r.Position); Debris:AddItem(a2, 1.2)
			emissor(a2, {Texture = TEX.faisca, Color = ColorSequence.new(AZUL_CLARO), LightEmission = 1, Size = ns(0, 0.45, 1, 0), Lifetime = NumberRange.new(0.3, 0.6),
				Speed = NumberRange.new(8, 18), SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(10)
		end
		local lp = Players.LocalPlayer
		if lp and lp.Character == a then                               -- tremor curto so para quem foi atingido
			local amp = d.intensidade == "pesado" and 0.3 or 0.15; local cam = workspace.CurrentCamera; local t0 = os.clock()
			local c; c = RunService.RenderStepped:Connect(function()
				local k = 1 - (os.clock() - t0) / 0.22; if k <= 0 then c:Disconnect(); return end
				cam.CFrame *= CFrame.new((math.random() - 0.5) * amp * k, (math.random() - 0.5) * amp * k, 0)
			end)
		end
		return
	end
	if d.hab == "Frostbite" and d.fase == "congelar" then congelar(d.alvo, d.duracao or 1.4, f); return end
	if f <= 0 then return end
	if d.hab == "Sopro" then soproEvento(m, d, f)
	elseif d.hab == "Rajadas" then rajadas(m, d, f)
	elseif d.hab == "ZeroAbsoluto" then zero(m, d, f)
	elseif d.hab == "Nevasca" then nevasca(m, d, f)
	elseif (d.hab == "Mordida" or d.hab == "Garra" or d.hab == "Cauda") and d.fase == "impacto" then
		estilhaco(d.pos, 0.55, f)
	elseif d.hab == "Rugido" and d.fase == "emissao" then              -- rugido basico do Glacial: halito gelado e aneis frios
		local b, dr = boca(m)
		for i = 0, 2 do task.delay(i * 0.25, function() anel(b + dr * (8 + i * 10), 12 + i * 8, BRANCO_GELO, 0.5, 0.3, 0.75, dr) end) end
		local a = ancora(b); Debris:AddItem(a, 2)
		emissor(a, {Texture = TEX.fumaca, Color = seq({BRANCO_GELO, AZUL_CLARO}), LightInfluence = 0.8, Size = ns(0, 2, 1, 10), Transparency = ns(0, 0.5, 1, 1),
			Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(20, 35), SpreadAngle = Vector2.new(25, 25), Rate = 0}):Emit(math.floor(18 * f))
	end
end
return G
