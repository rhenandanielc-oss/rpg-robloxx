-- VFXSombra (ModuleScript, ReplicatedStorage.Combate_Dragoes) — efeitos COSMETICOS da Sombra (kit do Dragao Sombrio,
-- definido pelo usuario em 03/11), so no cliente. Chamado pelo VFXCombate para todo evento com el = "Sombra";
-- evento() devolve true quando tratou o evento (o resto segue no perfil Neutro do VFXCombate).
-- Sopro Umbral (04/11): jato continuo de nevoa negra-violeta + vinheta LEVE na tela do jogador atingido (so visual,
-- curta, sem cegar). Desempenho: sem luz dinamica, taxas limitadas e escaladas pelo fator de LOD recebido.
-- Valores artisticos NAO_APROVADO (prototipo para revisao do usuario).
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local S = {}

local C3 = Color3.fromRGB
local PRETO, BREU, VIOLETA, VIOLETA_CLARO = C3(6, 0, 12), C3(28, 6, 45), C3(120, 40, 200), C3(175, 95, 255)
local TEX = {fumaca = "rbxasset://textures/particles/smoke_main.dds", faisca = "rbxasset://textures/particles/sparkles_main.dds",
	-- texturas neutras (brancas) ja enviadas para o Gelo; aqui so recebem cor
	nevoa = "rbxassetid://105424368956403", jato_h = "rbxassetid://114995351681928"}
local VINHETA = {pico = 0.55, segura = 0.25, some = 0.6, largura = 0.2}   -- transparencia minima, s, s, fracao da tela

local function seq(cs) local k = {}; for i, c in ipairs(cs) do table.insert(k, ColorSequenceKeypoint.new((i - 1) / (#cs - 1), c)) end; return ColorSequence.new(k) end
local function ns(...) local a = {...}; local k = {}; for i = 1, #a, 2 do table.insert(k, NumberSequenceKeypoint.new(a[i], a[i + 1])) end; return NumberSequence.new(k) end
local function ancora(pos) local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain; return a end
local function emissor(pai, t) local e = Instance.new("ParticleEmitter"); for k, v in pairs(t) do e[k] = v end; e.Parent = pai; return e end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local cacheOsso = {}
local function ossoC(m, nome)
	cacheOsso[m] = cacheOsso[m] or {}
	local b = cacheOsso[m][nome]; if b and b.Parent then return b end
	b = osso(m, nome); cacheOsso[m][nome] = b; return b
end
local function raizDe(m) return m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart end
local function boca(m)
	local cab, tip = ossoC(m, "Cabeca"), ossoC(m, "mouth_upper_tip")
	if cab and tip then
		local p = tip.TransformedWorldCFrame.Position; local d = p - cab.TransformedWorldCFrame.Position
		return p, d.Magnitude > 0.1 and d.Unit or m:GetPivot().LookVector
	end
	return m:GetPivot().Position + Vector3.new(0, 20, 0), m:GetPivot().LookVector
end
local function pastaFX()
	local f = workspace:FindFirstChild("VFX_Temporarios")
	if not f then f = Instance.new("Folder"); f.Name = "VFX_Temporarios"; f.Parent = workspace end
	return f
end

-- ===== vinheta leve (so o jogador atingido pelo Sopro Umbral) ======================================================
-- 4 faixas nas bordas com gradiente para dentro; nada no centro da tela. Cada acerto renova; sem acertos, some.
local vin
local function vinheta()
	local lp = Players.LocalPlayer; if not lp then return end
	if not (vin and vin.gui.Parent) then
		local g = Instance.new("ScreenGui"); g.Name = "VinhetaSombra"; g.IgnoreGuiInset = true; g.ResetOnSpawn = false; g.DisplayOrder = 5
		local faixas = {}
		for _, lado in ipairs({{0, 0, 1, VINHETA.largura, 90}, {0, 1 - VINHETA.largura, 1, VINHETA.largura, -90}, {0, 0, VINHETA.largura, 1, 0}, {1 - VINHETA.largura, 0, VINHETA.largura, 1, 180}}) do
			local fr = Instance.new("Frame"); fr.BorderSizePixel = 0; fr.BackgroundColor3 = BREU; fr.BackgroundTransparency = 1
			fr.Position = UDim2.fromScale(lado[1], lado[2]); fr.Size = UDim2.fromScale(lado[3], lado[4])
			local gr = Instance.new("UIGradient"); gr.Rotation = lado[5]; gr.Transparency = ns(0, 0, 1, 1)
			gr.Color = seq({PRETO, VIOLETA}); gr.Parent = fr
			fr.Parent = g; table.insert(faixas, fr)
		end
		g.Parent = lp:WaitForChild("PlayerGui")
		vin = {gui = g, faixas = faixas, ate = 0}
	end
	vin.ate = os.clock() + VINHETA.segura
	if vin.con then return end
	vin.con = RunService.RenderStepped:Connect(function()
		local resto = os.clock() - vin.ate                                 -- < 0: segurando; 0..some: sumindo
		local k = resto <= 0 and 0 or math.min(1, resto / VINHETA.some)
		local tr = VINHETA.pico + (1 - VINHETA.pico) * k
		for _, fr in ipairs(vin.faixas) do fr.BackgroundTransparency = tr end
		if k >= 1 then vin.con:Disconnect(); vin.con = nil end
	end)
end

-- ===== reacao ao acerto de Sombra =================================================================================
local function reacao(d, f)
	local a = d.alvo; if not (a and a.Parent) then return end
	local h = Instance.new("Highlight"); h.FillColor = VIOLETA; h.OutlineColor = PRETO; h.OutlineTransparency = 0.6
	h.FillTransparency = d.intensidade == "pesado" and 0.35 or d.intensidade == "moderado" and 0.5 or 0.7; h.Parent = a
	TweenService:Create(h, TweenInfo.new(0.35), {FillTransparency = 1, OutlineTransparency = 1}):Play(); Debris:AddItem(h, 0.4)
	local r = raizDe(a)
	if r and f > 0 then
		local a2 = ancora(r.Position); Debris:AddItem(a2, 1.2)
		emissor(a2, {Texture = TEX.fumaca, Color = seq({VIOLETA, BREU}), LightEmission = 0.2, LightInfluence = 0.6, Size = ns(0, 1, 1, 3),
			Transparency = ns(0, 0.5, 1, 1), Lifetime = NumberRange.new(0.4, 0.7), Speed = NumberRange.new(3, 8), SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(math.max(1, math.floor(5 * f)))
	end
	local lp = Players.LocalPlayer
	if lp and lp.Character == a then                                   -- so quem foi atingido: tremor curto (igual ao generico)
		if d.tipo == "Sopro" then vinheta() end
		local amp = d.intensidade == "pesado" and 0.35 or d.intensidade == "moderado" and 0.2 or 0.1
		local cam = workspace.CurrentCamera; local t0 = os.clock()
		local c; c = RunService.RenderStepped:Connect(function()
			local k = 1 - (os.clock() - t0) / 0.25; if k <= 0 then c:Disconnect(); return end
			cam.CFrame *= CFrame.new((math.random() - 0.5) * amp * k, (math.random() - 0.5) * amp * k, 0)
		end)
	end
end

-- ===== SOPRO UMBRAL: jato continuo de nevoa negra-violeta ==========================================================
-- Feixe translucido escuro (direcao e continuidade) + nucleo de fumaca preta, nevoa violeta envolvendo e fiapos de
-- breu; centelhas violeta raras. Nada brilha muito: a Sombra se le pelo contraste preto/violeta, nao por luz.
local sopro = {}
local function velPara(alc, frac, drag, vida) local d = alc * frac; if drag <= 0.01 then return d / vida end; return d * drag / (1 - math.exp(-drag * vida)) end
local function emissoresSopro(m)
	local s = sopro[m]; if s and s.anc and s.anc.Parent then return s end
	s = {anc = ancora(m:GetPivot().Position), fim = ancora(m:GetPivot().Position), e = {}}; sopro[m] = s
	local VP = Enum.ParticleOrientation.VelocityParallel
	s.e.nucleo = emissor(s.anc, {Texture = TEX.fumaca, Color = seq({PRETO, BREU}), LightEmission = 0, LightInfluence = 0.4,
		Size = ns(0, 1.5, 0.4, 5, 1, 10), Transparency = ns(0, 0.25, 0.7, 0.5, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-60, 60),
		SpreadAngle = Vector2.new(5, 5), EmissionDirection = Enum.NormalId.Front, Rate = 0, ZOffset = 1})
	s.e.nevoa = emissor(s.anc, {Texture = TEX.nevoa, Color = seq({VIOLETA, BREU}), LightEmission = 0.25, LightInfluence = 0.5,
		Size = ns(0, 2.5, 1, 15), Transparency = ns(0, 0.55, 0.6, 0.7, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30),
		SpreadAngle = Vector2.new(9, 9), EmissionDirection = Enum.NormalId.Front, Rate = 0})
	s.e.fiapos = emissor(s.anc, {Texture = TEX.fumaca, Orientation = VP, Color = ColorSequence.new(PRETO), LightEmission = 0, LightInfluence = 0.3,
		Size = ns(0, 0.6, 1, 1.4), Transparency = ns(0, 0.4, 1, 1), SpreadAngle = Vector2.new(11, 11), EmissionDirection = Enum.NormalId.Front, Rate = 0, ZOffset = 2})
	s.e.centelhas = emissor(s.anc, {Texture = TEX.faisca, Color = ColorSequence.new(VIOLETA_CLARO), LightEmission = 0.8, Size = ns(0, 0.5, 1, 0),
		SpreadAngle = Vector2.new(8, 8), EmissionDirection = Enum.NormalId.Front, Rate = 0})
	local function feixe(w0, w1, tl, vel, tr, cor)
		local b = Instance.new("Beam"); b.Attachment0 = s.anc; b.Attachment1 = s.fim; b.Texture = TEX.jato_h; b.TextureMode = Enum.TextureMode.Wrap
		b.TextureLength = tl; b.TextureSpeed = vel; b.Width0 = w0; b.Width1 = w1; b.FaceCamera = true; b.Segments = 10; b.LightEmission = 0; b.LightInfluence = 0.4
		b.Color = cor; b.Transparency = tr; b.Enabled = false; b.Parent = s.anc; return b
	end
	s.feixe = feixe(2.4, 12, 24, 1.6, ns(0, 0.55, 0.5, 0.78, 1, 1), seq({BREU, VIOLETA}))
	s.miolo = feixe(0.9, 3, 12, 2.6, ns(0, 0.35, 0.5, 0.7, 1, 1), ColorSequence.new(PRETO))
	return s
end
-- {fracao do alcance, arrasto, vida, taxa} — total ~150 particulas/s no fator 1
local PERF = {nucleo = {0.95, 0.9, 1.0, 55}, nevoa = {0.9, 1.3, 1.4, 30}, fiapos = {1.0, 0.8, 0.9, 50}, centelhas = {1.0, 0.8, 0.9, 15}}
local function ligarSopro(m, ligado, f, alvo, alcance)
	local s = emissoresSopro(m); s.alvo = alvo
	if ligado then
		if s.con then s.con:Disconnect() end
		local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {m, pastaFX()}
		local alc = alcance or 95
		s.con = RunService.RenderStepped:Connect(function()
			local b, d = boca(m)
			if s.alvo then local v = s.alvo - b; if v.Magnitude > 5 then d = (d * 0.3 + v.Unit * 0.7).Unit end end
			s.anc.WorldCFrame = CFrame.lookAt(b, b + d)
			local h = workspace:Raycast(b, d * alc * 0.85, rp)
			s.fim.WorldPosition = h and h.Position or (b + d * alc * 0.85)
		end)
		for k, e in pairs(s.e) do
			local p = PERF[k]; e.Rate = p[4] * f
			local v = velPara(alc, p[1], p[2], p[3]); e.Drag = p[2]; e.Lifetime = NumberRange.new(p[3] * 0.9, p[3]); e.Speed = NumberRange.new(v * 0.92, v * 1.04)
		end
		s.feixe.Enabled = true; s.miolo.Enabled = true
	else
		for _, e in pairs(s.e) do e.Rate = 0 end
		s.feixe.Enabled = false; s.miolo.Enabled = false
		task.delay(1.6, function() if s.con and s.e.nucleo.Rate == 0 then s.con:Disconnect(); s.con = nil end end)
	end
end
local soproTok, soproMira = {}, {}
local function soproEvento(m, d, f)
	if d.fase == "preparo" then                                       -- breu sendo sugado para a boca
		local b = boca(m); local a = ancora(b); Debris:AddItem(a, 1.3)
		local e = emissor(a, {Texture = TEX.fumaca, Color = seq({VIOLETA, PRETO}), LightEmission = 0.1, LightInfluence = 0.6, Size = ns(0, 3, 1, 0.4),
			Transparency = ns(0, 0.5, 1, 1), Lifetime = NumberRange.new(0.35, 0.6), Speed = NumberRange.new(-14, -8), SpreadAngle = Vector2.new(180, 180), Rate = 40 * f})
		task.delay(1.0, function() if e.Parent then e.Rate = 0 end end)
	elseif d.fase == "emissao" then
		soproTok[m] = (soproTok[m] or 0) + 1; local tok = soproTok[m]; soproMira[m] = d.alvoPos
		ligarSopro(m, true, f, d.alvoPos, d.alcance)
		task.spawn(function()                                          -- onde o jato bate: nuvem de breu rente a superficie
			local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {m, pastaFX()}
			local lim = os.clock() + 7
			while soproTok[m] == tok and os.clock() < lim and m.Parent do
				local b, dr = boca(m); local ap = soproMira[m]; if ap then dr = (ap - b).Unit end
				local h = workspace:Raycast(b, dr * (d.alcance or 95), rp)
				if h then
					local a = ancora(h.Position + h.Normal); Debris:AddItem(a, 1.6)
					emissor(a, {Texture = TEX.nevoa, Color = seq({BREU, VIOLETA}), LightEmission = 0.15, LightInfluence = 0.6, Size = ns(0, 4, 1, 11),
						Transparency = ns(0, 0.55, 1, 1), Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(4, 9), SpreadAngle = Vector2.new(70, 70),
						Rotation = NumberRange.new(0, 360), Rate = 0}):Emit(math.max(1, math.floor(3 * f)))
				end
				task.wait(0.3)
			end
		end)
	elseif d.fase == "mira" then soproMira[m] = d.alvoPos; local s = emissoresSopro(m); s.alvo = d.alvoPos
	elseif d.fase == "fim" then
		soproTok[m] = (soproTok[m] or 0) + 1; soproMira[m] = nil
		ligarSopro(m, false, f)
		local b = boca(m); local a = ancora(b); Debris:AddItem(a, 2)
		emissor(a, {Texture = TEX.fumaca, Color = seq({BREU, PRETO}), LightInfluence = 0.6, Size = ns(0, 2, 1, 7), Transparency = ns(0, 0.5, 1, 1),
			Lifetime = NumberRange.new(0.9, 1.4), Speed = NumberRange.new(2, 6), Acceleration = Vector3.new(0, 1.5, 0), SpreadAngle = Vector2.new(40, 40), Rate = 0}):Emit(math.floor(10 * f))
	end
end

-- ===== CORRENTES DA NOITE (04/11): aviso no chao, erupcao de breu e correntes que sobem e prendem ===================
-- Cada corrente = elos (pecas pequenas, sem colisao/sombra) ao longo de uma curva do chao ate a cintura do alvo,
-- alternando 90 graus, em espiral que aperta ate a cintura; so alguns elos em Neon violeta (sem luz dinamica).
-- Sobem em 0,3 s, seguem o alvo e se desfazem ao soltar. Limite: 3 correntes x 16 elos por alvo (o servidor prende
-- no maximo 3 alvos por ativacao). v2 (04/11): a v1 arqueava para fora e parecia patas de aranha.
local NCORR, NELOS, SOBE = 3, 16, 0.3
local correntes = {}                                                 -- [alvo] = {elos, base, con, ...}
local function peca(props)
	local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	for k, v in pairs(props) do p[k] = v end; p.Parent = pastaFX(); return p
end
local function aviso(d, f)
	local r = d.raio or 16; local dur = d.duracao or 0.5
	local disco = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.15, r * 0.6, r * 0.6), Color = VIOLETA, Material = Enum.Material.SmoothPlastic, Transparency = 0.8,
		CFrame = CFrame.new(d.pos + Vector3.new(0, 0.12, 0)) * CFrame.Angles(0, 0, math.rad(90))})
	local miolo = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.18, r * 0.4, r * 0.4), Color = PRETO, Material = Enum.Material.SmoothPlastic, Transparency = 0.5,
		CFrame = CFrame.new(d.pos + Vector3.new(0, 0.14, 0)) * CFrame.Angles(0, 0, math.rad(90))})
	TweenService:Create(disco, TweenInfo.new(dur), {Size = Vector3.new(0.15, r * 2, r * 2), Transparency = 0.55}):Play()
	TweenService:Create(miolo, TweenInfo.new(dur), {Size = Vector3.new(0.18, r * 1.5, r * 1.5)}):Play()
	task.delay(dur, function()
		TweenService:Create(disco, TweenInfo.new(0.4), {Transparency = 1}):Play(); TweenService:Create(miolo, TweenInfo.new(0.4), {Transparency = 1}):Play()
	end)
	Debris:AddItem(disco, dur + 0.5); Debris:AddItem(miolo, dur + 0.5)
	if f > 0 then
		local a = ancora(d.pos + Vector3.new(0, 0.5, 0)); Debris:AddItem(a, dur + 1)
		local e = emissor(a, {Texture = TEX.fumaca, Color = seq({VIOLETA, PRETO}), LightEmission = 0.1, LightInfluence = 0.6, Size = ns(0, 1.5, 1, 3),
			Transparency = ns(0, 0.55, 1, 1), Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(r * 0.6, r * 1.2), Drag = 3,
			SpreadAngle = Vector2.new(180, 10), EmissionDirection = Enum.NormalId.Top, Rate = 20 * f})
		task.delay(dur, function() if e.Parent then e.Rate = 0 end end)
	end
end
local function erupcao(d, f)
	if f <= 0 then return end
	local a = ancora(d.pos + Vector3.new(0, 1, 0)); Debris:AddItem(a, 2)
	emissor(a, {Texture = TEX.nevoa, Color = seq({PRETO, BREU, VIOLETA}), LightEmission = 0.1, LightInfluence = 0.6, Size = ns(0, 2, 1, 6),
		Transparency = ns(0, 0.55, 1, 1), Lifetime = NumberRange.new(0.6, 0.9), Speed = NumberRange.new(5, 11), SpreadAngle = Vector2.new(60, 60),
		Rotation = NumberRange.new(0, 360), Acceleration = Vector3.new(0, 3, 0), EmissionDirection = Enum.NormalId.Top, Rate = 0}):Emit(math.max(2, math.floor(12 * f)))
end
local function soltarCorrentes(alvo, rapido)
	local c = correntes[alvo]; if not c then return end
	correntes[alvo] = nil
	if c.con then c.con:Disconnect() end
	for _, el in ipairs(c.elos) do
		if rapido then el:Destroy() else TweenService:Create(el, TweenInfo.new(0.3), {Transparency = 1}):Play(); Debris:AddItem(el, 0.35) end
	end
	for _, x in ipairs(c.extras) do Debris:AddItem(x, rapido and 0 or 0.35) end
	for _, b in ipairs(c.fios) do b.Enabled = false end
	if not rapido and c.base then
		local a = ancora(c.base); Debris:AddItem(a, 1.5)
		emissor(a, {Texture = TEX.fumaca, Color = seq({BREU, PRETO}), LightInfluence = 0.6, Size = ns(0, 1.2, 1, 3), Transparency = ns(0, 0.5, 1, 1),
			Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(2, 5), SpreadAngle = Vector2.new(70, 70), Rate = 0}):Emit(6)
	end
end
local function prender(d, f)
	local alvo = d.alvo; local r = alvo and raizDe(alvo); if not r or f <= 0 then return end
	soltarCorrentes(alvo, true)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {alvo, pastaFX()}
	local hc = workspace:Raycast(r.Position, Vector3.new(0, -30, 0), rp)
	local chaoY = hc and hc.Position.Y or (r.Position.Y - 3)
	local c = {elos = {}, fios = {}, extras = {}, cadeias = {}, t0 = os.clock(), base = Vector3.new(r.Position.X, chaoY, r.Position.Z)}
	correntes[alvo] = c
	local giro = math.random() * math.pi * 2
	for i = 1, NCORR do
		local ang = giro + (i - 1) * (math.pi * 2 / NCORR)
		local cad = {ang = ang, elos = {}}
		for k = 1, NELOS do
			local el = peca({Size = Vector3.new(0.15, 0.72, 0.4), Color = (k % 4 == 0) and C3(55, 18, 95) or C3(14, 8, 22),
				Material = (k % 4 == 0) and Enum.Material.Neon or Enum.Material.Metal, Transparency = 1})
			table.insert(cad.elos, el); table.insert(c.elos, el)
		end
		table.insert(c.cadeias, cad)
	end
	local fum = ancora(c.base + Vector3.new(0, 0.4, 0)); table.insert(c.extras, fum)
	emissor(fum, {Texture = TEX.fumaca, Color = seq({VIOLETA, PRETO}), LightEmission = 0.1, LightInfluence = 0.6, Size = ns(0, 1, 1, 2.5), Transparency = ns(0, 0.6, 1, 1),
		Lifetime = NumberRange.new(0.6, 1), Speed = NumberRange.new(0.5, 2), SpreadAngle = Vector2.new(70, 70), Rate = 8 * f})
	local partes, cfs = {}, {}
	c.con = RunService.Heartbeat:Connect(function()
		if not (alvo.Parent and r.Parent) or os.clock() - c.t0 > (d.duracao or 2.5) + 1.5 then soltarCorrentes(alvo, true); return end
		local s = math.min(1, (os.clock() - c.t0) / SOBE)
		local topo = r.Position + Vector3.new(0, 0.3, 0)
		table.clear(partes); table.clear(cfs)
		for _, cad in ipairs(c.cadeias) do
			-- espiral: sai do chao a 2,6 studs e da 3/4 de volta em torno do corpo, apertando ate a cintura
			local function ponto(t)
				local a = cad.ang + t * math.pi * 1.5
				local rr = 2.6 + (1.15 - 2.6) * math.min(1, t * 1.4)
				return Vector3.new(r.Position.X + math.cos(a) * rr, chaoY + (topo.Y - chaoY) * t, r.Position.Z + math.sin(a) * rr)
			end
			for k, el in ipairs(cad.elos) do
				local t = (k - 0.5) / NELOS
				if t <= s then
					local p0, p1 = ponto(math.max(0, t - 0.05)), ponto(math.min(1, t + 0.05))
					local cf = CFrame.lookAt(ponto(t), ponto(t) + (p1 - p0)) * CFrame.Angles(math.rad(90), (k % 2 == 0) and math.rad(90) or 0, 0)
					table.insert(partes, el); table.insert(cfs, cf)
					if el.Transparency > 0 then el.Transparency = 0 end
				end
			end
		end
		if #partes > 0 then workspace:BulkMoveTo(partes, cfs, Enum.BulkMoveMode.FireCFrameChanged) end
	end)
end
local function correntesEvento(m, d, f)
	if d.fase == "aviso" then aviso(d, f)
	elseif d.fase == "erupcao" then erupcao(d, f)
	elseif d.fase == "prender" then prender(d, f)
	elseif d.fase == "soltar" then if d.alvo then soltarCorrentes(d.alvo, false) end end
end

function S.evento(d, f)
	local m = d.d
	if d.hab == "Correntes" and d.fase == "soltar" then correntesEvento(m, d, f); return true end   -- soltar mesmo sem o dragao
	if not m or not m.Parent then return false end
	if d.fase == "reacao" then reacao(d, f); return true end           -- vinheta mesmo sem LOD visual
	if d.hab == "Sopro" then if f > 0 or d.fase == "fim" then soproEvento(m, d, f) end; return true end
	if d.hab == "Correntes" then correntesEvento(m, d, f); return true end
	return false
end
return S
