-- patch_vfx_sombra_revisao.luau (Studio, Edit) — revisao VISUAL do Sopro Umbral (v2) e das Correntes da Noite (v4).
-- Gerado por sombrio/gerar_patch_vfx_revisao.py a partir do src/. Troca so o VFXSombra (cliente) e cria o Elo_Sombra.
-- Backup unico: ServerStorage.Backup_VFXSombra_Revisao_2026-11-04.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage")
local M = game:GetService("ReplicatedStorage").Combate_Dragoes.VFXSombra
local vfx = [=====[
-- VFXSombra (ModuleScript, ReplicatedStorage.Combate_Dragoes) — efeitos COSMETICOS da Sombra (kit do Dragao Sombrio,
-- definido pelo usuario em 03/11), so no cliente. Chamado pelo VFXCombate para todo evento com el = "Sombra";
-- evento() devolve true quando tratou o evento (o resto segue no perfil Neutro do VFXCombate).
-- Sopro Umbral (04/11; v2 visual 04/11): jato continuo de nevoa negra-violeta + vinheta LEVE na tela do jogador atingido (so visual,
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
local function peca(props, pai)
	local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	for k, v in pairs(props) do p[k] = v end; p.Parent = pai or pastaFX(); return p
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

-- ===== SOPRO UMBRAL v2 (revisao visual 04/11): fluxo volumetrico de breu ==========================================
-- Sem feixes (liam como tubo/laser). Camadas: garganta densa e pequena na boca -> nucleo de breu (flipbook proprio de
-- fumaca turbulenta, recolorido) que cresce e desacelera -> turbilhoes lentos e largos que sobem e se desfazem;
-- violeta so na borda (nevoa atras do nucleo) e fiapos finos dando a direcao; sem centelhas. Origem entre as pontas
-- da boca; direcao da cabeca puxada para a mira no maximo BOCA_MAX. Paredes/chao: a vida das particulas encurta ate o
-- contato (nao atravessa) e ali sai uma nuvem baixa; personagens nao param o jato (o cone do servidor os atravessa).
-- Abre crescendo (0,3 s); ao fim a emissao para e o que esta no ar se dissipa. 175 particulas/s no fator 1, ~140 vivas
-- (a garganta, 80/s, vive 0,3 s; v1: 150/s, ~155 vivas).
local FB_FUMACA = "rbxassetid://114973539727313"                   -- V14/vfx/gerar_flipbooks.py (cinza neutro, 8x8)
local BOCA_MAX, ABRE = math.rad(35), 0.3
local sopro = {}
local function velPara(alc, frac, drag, vida) local d = alc * frac; if drag <= 0.01 then return d / vida end; return d * drag / (1 - math.exp(-drag * vida)) end
local function vidaAte(D, v0, k, vida)                                -- tempo para a particula percorrer D (arrasto k)
	if k <= 0.01 then return math.min(vida, D / v0) end
	local x = D * k / v0; if x >= 1 then return vida end
	return math.min(vida, -math.log(1 - x) / k)
end
local function bocaJato(m)
	local cab, up, lo = ossoC(m, "Cabeca"), ossoC(m, "mouth_upper_tip"), ossoC(m, "mouth_lower_tip")
	if cab and up then
		local pu = up.TransformedWorldCFrame.Position
		local d = pu - cab.TransformedWorldCFrame.Position; d = d.Magnitude > 0.1 and d.Unit or m:GetPivot().LookVector
		local p = lo and (pu + lo.TransformedWorldCFrame.Position) / 2 or pu
		return p + d * 0.3, d
	end
	return boca(m)
end
local function limitar(d, alvo, max)                                  -- gira d para alvo, no maximo `max` rad
	local ang = math.acos(math.clamp(d:Dot(alvo), -1, 1)); if ang <= max then return alvo end
	local ax = d:Cross(alvo); if ax.Magnitude < 1e-4 then return d end
	return CFrame.fromAxisAngle(ax.Unit, max) * d
end
local function raioSolido(o, v, m)                                    -- terreno/paredes; personagens nao bloqueiam
	local ign = {m, pastaFX()}; local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	for _ = 1, 3 do
		rp.FilterDescendantsInstances = ign
		local h = workspace:Raycast(o, v, rp); if not h then return nil end
		local mdl = h.Instance:FindFirstAncestorOfClass("Model")
		if mdl and mdl:FindFirstChildOfClass("Humanoid") then table.insert(ign, mdl) else return h end
	end
end
local function flipFumaca(t) t.Texture = FB_FUMACA; t.FlipbookLayout = Enum.ParticleFlipbookLayout.Grid8x8; t.FlipbookMode = Enum.ParticleFlipbookMode.OneShot; return t end
-- {fracao do alcance, arrasto, vida, taxa, variacao de velocidade}
local PERF = {garganta = {0.25, 2.5, 0.3, 80, 0.85}, nucleo = {0.95, 1.6, 1.25, 55, 0.78}, turbilhao = {0.8, 2.4, 1.6, 12, 0.6},
	borda = {0.9, 1.4, 1.2, 12, 0.8}, fiapos = {1.0, 1.2, 0.8, 16, 0.85}}
local function limparSopro(m)
	local s = sopro[m]; if not s then return end
	sopro[m] = nil; if s.con then s.con:Disconnect() end
	s.anc:Destroy(); s.imp:Destroy()
end
local function emissoresSopro(m)
	local s = sopro[m]; if s and s.anc.Parent then return s end
	s = {anc = ancora(m:GetPivot().Position), imp = ancora(m:GetPivot().Position), e = {}, vel = {}, f = 1}; sopro[m] = s
	local F = Enum.NormalId.Front
	-- garganta: curta e densa, levemente alongada no sentido do jato (Squash) para nao abrir buracos entre particulas
	-- rapidas; textura macia (o flipbook esticado virava lascas afiadas na boca)
	s.e.garganta = emissor(s.anc, {Texture = TEX.fumaca, Color = seq({PRETO, BREU}), LightEmission = 0, LightInfluence = 0.3,
		Orientation = Enum.ParticleOrientation.VelocityParallel, Squash = ns(0, 0.8, 1, 0),
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.9, 0.2), NumberSequenceKeypoint.new(1, 3, 0.6)}),
		Transparency = ns(0, 0.55, 0.2, 0.3, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-50, 50),
		SpreadAngle = Vector2.new(4, 4), EmissionDirection = F, Rate = 0, ZOffset = 1.5})
	s.e.nucleo = emissor(s.anc, flipFumaca({Color = seq({PRETO, BREU, C3(38, 12, 58)}), LightEmission = 0, LightInfluence = 0.35,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.4, 0.3), NumberSequenceKeypoint.new(0.06, 3, 0.6), NumberSequenceKeypoint.new(0.3, 5.5, 1.2), NumberSequenceKeypoint.new(0.65, 8.5, 2), NumberSequenceKeypoint.new(1, 10.5, 2.5)}),
		Transparency = ns(0, 0.6, 0.08, 0.3, 0.5, 0.45, 0.85, 0.75, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-45, 45),
		Acceleration = Vector3.new(0, 1.2, 0), SpreadAngle = Vector2.new(6, 6), EmissionDirection = F, Rate = 0, ZOffset = 1}))
	s.e.turbilhao = emissor(s.anc, flipFumaca({Color = seq({BREU, C3(18, 6, 28)}), LightEmission = 0, LightInfluence = 0.4,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.4, 0.4), NumberSequenceKeypoint.new(1, 13, 3)}),
		Transparency = ns(0, 0.85, 0.3, 0.55, 0.75, 0.75, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-90, 90),
		Acceleration = Vector3.new(0, 2.2, 0), SpreadAngle = Vector2.new(16, 16), EmissionDirection = F, Rate = 0}))
	s.e.borda = emissor(s.anc, {Texture = TEX.nevoa, Color = seq({C3(95, 35, 160), C3(45, 15, 80)}), LightEmission = 0.25, LightInfluence = 0.5,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2, 0.3), NumberSequenceKeypoint.new(1, 12, 2.5)}),
		Transparency = ns(0, 0.92, 0.35, 0.74, 1, 1), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30),
		SpreadAngle = Vector2.new(11, 11), EmissionDirection = F, Rate = 0, ZOffset = -1})
	s.e.fiapos = emissor(s.anc, {Texture = TEX.fumaca, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = ColorSequence.new(PRETO),
		LightEmission = 0, LightInfluence = 0.3, Size = ns(0, 0.25, 1, 0.75), Transparency = ns(0, 0.6, 0.4, 0.45, 1, 1),
		SpreadAngle = Vector2.new(9, 9), EmissionDirection = F, Rate = 0, ZOffset = 2})
	s.eImp = emissor(s.imp, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.5,
		Size = NumberSequence.new({NumberSequenceKeypoint.new(0, 3, 0.8), NumberSequenceKeypoint.new(1, 12, 3)}), Transparency = ns(0, 0.75, 0.3, 0.6, 1, 1),
		Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(5, 11), Drag = 2.5, Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-40, 40),
		SpreadAngle = Vector2.new(80, 80), EmissionDirection = F, Rate = 0}))
	return s
end
local function ligarSopro(m, ligado, f, alvo, alcance)
	local s = emissoresSopro(m); s.alvo = alvo
	if ligado then
		s.ligado, s.t0, s.f, s.prox = true, os.clock(), f, 0
		s.alc = alcance or 95; local alc = s.alc
		for k, e in pairs(s.e) do
			local p = PERF[k]; local v = velPara(alc, p[1], p[2], p[3]); s.vel[k] = v
			e.Drag = p[2]; e.Lifetime = NumberRange.new(p[3] * 0.85, p[3]); e.Speed = NumberRange.new(v * p[5], v * 1.04)
		end
		if s.con then return end
		s.con = RunService.RenderStepped:Connect(function()
			if not m.Parent then limparSopro(m); return end
			local b, d = bocaJato(m)
			if s.alvo then local v = s.alvo - b; if v.Magnitude > 5 then d = limitar(d, v.Unit, BOCA_MAX) end end
			s.anc.WorldCFrame = CFrame.lookAt(b, b + d)
			local agora = os.clock()
			if s.ligado then local k = math.min(1, (agora - s.t0) / ABRE); for n, e in pairs(s.e) do e.Rate = PERF[n][4] * s.f * (0.3 + 0.7 * k) end end
			if agora < s.prox then return end
			s.prox = agora + 0.1                                       -- contato: 10x/s basta
			local h = raioSolido(b, d * s.alc, m)
			local D = h and (h.Position - b).Magnitude or s.alc
			for n, e in pairs(s.e) do local p = PERF[n]; local t = vidaAte(D * 1.12, s.vel[n] * 1.04, p[2], p[3]); e.Lifetime = NumberRange.new(t * 0.85, t) end
			if h and s.ligado then
				local r = d - 2 * d:Dot(h.Normal) * h.Normal                   -- espalha rente a superficie, no sentido do jato
				local p = h.Position - d * 2 + h.Normal * 0.6                 -- um pouco antes do contato: emenda com o jato
				s.imp.WorldCFrame = CFrame.lookAt(p, p + (h.Normal + r * 0.6).Unit); s.eImp.Rate = 10 * s.f
			else s.eImp.Rate = 0 end
		end)
	else
		s.ligado = false; for _, e in pairs(s.e) do e.Rate = 0 end; s.eImp.Rate = 0
		task.delay(1.8, function() if s.con and not s.ligado then s.con:Disconnect(); s.con = nil end end)
	end
end
local function soproEvento(m, d, f)
	if d.fase == "preparo" then                                       -- breu puxado para a boca: nasce numa casca e converge
		local b = bocaJato(m)
		local casca = peca({Shape = Enum.PartType.Ball, Size = Vector3.new(9, 9, 9), Transparency = 1, CFrame = CFrame.new(b)}); Debris:AddItem(casca, 1.6)
		local e = emissor(casca, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.5, Size = ns(0, 1.6, 1, 0.3),
			Transparency = ns(0, 1, 0.25, 0.55, 0.8, 0.5, 1, 1), Lifetime = NumberRange.new(0.4, 0.5), Speed = NumberRange.new(8, 11), Rate = 36 * f,
			Shape = Enum.ParticleEmitterShape.Sphere, ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface}))
		local c; c = RunService.Heartbeat:Connect(function() if not casca.Parent or not m.Parent then c:Disconnect(); return end; casca.CFrame = CFrame.new((bocaJato(m))) end)
		task.delay(1.0, function() if e.Parent then e.Rate = 0 end end)
	elseif d.fase == "emissao" then
		ligarSopro(m, true, f, d.alvoPos, d.alcance)
	elseif d.fase == "mira" then local s = emissoresSopro(m); s.alvo = d.alvoPos
	elseif d.fase == "fim" then
		ligarSopro(m, false, f)
		local b, dr = bocaJato(m); local a = ancora(b); a.WorldCFrame = CFrame.lookAt(b, b + dr); Debris:AddItem(a, 2.2)
		local e = emissor(a, flipFumaca({Color = seq({PRETO, BREU}), LightEmission = 0, LightInfluence = 0.5, Size = ns(0, 0.8, 1, 4.5),
			Transparency = ns(0, 0.6, 0.3, 0.45, 1, 1), Lifetime = NumberRange.new(1.0, 1.6), Speed = NumberRange.new(1.5, 4), Drag = 1,
			Acceleration = Vector3.new(0, 1.4, 0), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30),
			SpreadAngle = Vector2.new(30, 30), EmissionDirection = Enum.NormalId.Front, Rate = 10 * f}))   -- resto saindo da boca
		task.delay(0.4, function() if e.Parent then e.Rate = 0 end end)
	end
end

-- ===== CORRENTES DA NOITE v4 (revisao visual 04/11): elos encaixados que saem do chao e contem o alvo ===============
-- Elo = anel alongado COM FURO (UnionOperation Combate_Dragoes.Elo_Sombra, feita por sombrio/criar_elo_sombra.luau;
-- sem ela, 4 barras), alternando 90 graus e encaixado no vizinho (passo = comprimento - 2 fios: a ponta de um elo
-- passa pelo furo do outro). Por alvo: NCORR correntes saem de pontos REAIS do chao em volta (raycast; sem chao, a
-- corrente nao aparece), empurradas para fora da terra ate um anel que FECHA em volta do corpo (bracos e tronco) a
-- partir dos pontos de chegada e da um tranco amortecido; presas, ficam esticadas com vibracao amortecida e tremor
-- minimo e seguem o alvo (se ele se afasta, mais elos saem do chao; nenhum elo estica). Soltar: o anel afrouxa e cai e
-- as correntes recolhem para o chao em T_SOLTA s; tudo e destruido no fim. Acabamento: Metal quase preto (reflexo
-- discreto) + Highlight violeta so no contorno (le em grafico baixo). Orcamento por alvo (servidor prende ate 3):
-- ate NCORR x MAX_BASE + MAX_ANEL = 45 elos, 1 Highlight, 1 Heartbeat (BulkMoveTo); sem colisao/consulta/sombra/luz.
local ELO = {comp = 1.1, larg = 0.6, fio = 0.17}                      -- studs (escala 1 = R15 de ~5,5 de altura)
local NCORR, MAX_BASE, MAX_ANEL, R_BASE = 3, 9, 18, 4.0
local T_SOBE, T_FECHA, T_SOLTA = 0.28, 0.22, 0.35
local COR_ELO = C3(20, 13, 28)
local correntes = {}                                                 -- [alvo] = {modelo, cad, anel, con, ...}
local function novoElo(esc, pai)                                     -- {{parte, deslocamento}}; eixo longo = Y, plano XY
	local t = script.Parent:FindFirstChild("Elo_Sombra")
	if t then
		local p = t:Clone(); p.Size = t.Size * esc; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
		p.CastShadow = false; p.Transparency = 1; p.CFrame = CFrame.new(0, -500, 0); p.Parent = pai; return {{p, CFrame.identity}}
	end
	local L, W, F = ELO.comp * esc, ELO.larg * esc, ELO.fio * esc; local r = {}
	for _, sx in ipairs({-1, 1}) do table.insert(r, {peca({Size = Vector3.new(F, L, F), Color = COR_ELO, Material = Enum.Material.Metal, Transparency = 1, CFrame = CFrame.new(0, -500, 0)}, pai), CFrame.new(sx * (W - F) / 2, 0, 0)}) end
	for _, sy in ipairs({-1, 1}) do table.insert(r, {peca({Size = Vector3.new(W - 2 * F, F, F), Color = COR_ELO, Material = Enum.Material.Metal, Transparency = 1, CFrame = CFrame.new(0, -500, 0)}, pai), CFrame.new(0, sy * (L - F) / 2, 0)}) end
	return r
end
local function cfElo(pos, dir, giro)                                 -- eixo longo do elo ao longo de dir, girado `giro` nele
	local up = math.abs(dir.Y) > 0.97 and Vector3.xAxis or Vector3.yAxis
	return CFrame.lookAt(pos, pos + dir, up) * CFrame.Angles(math.rad(90), 0, 0) * CFrame.Angles(0, giro, 0)
end
local function cfChao(pos, n)                                        -- cilindro deitado no chao (eixo X = normal)
	local r = n:Cross(Vector3.zAxis); if r.Magnitude < 0.1 then r = n:Cross(Vector3.xAxis) end
	return CFrame.fromMatrix(pos, n, r.Unit)
end
local function normalChao(pos, ign)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ign
	local h = workspace:Raycast(pos + Vector3.new(0, 3, 0), Vector3.new(0, -8, 0), rp); return h and h.Normal or Vector3.yAxis
end
local function aviso(d, f)
	local r = d.raio or 16; local dur = d.duracao or 0.5
	local n = normalChao(d.pos, {pastaFX(), d.d})
	local disco = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.15, r * 0.6, r * 0.6), Color = VIOLETA, Material = Enum.Material.SmoothPlastic, Transparency = 0.8,
		CFrame = cfChao(d.pos + n * 0.12, n)})
	local miolo = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.18, r * 0.4, r * 0.4), Color = PRETO, Material = Enum.Material.SmoothPlastic, Transparency = 0.5,
		CFrame = cfChao(d.pos + n * 0.14, n)})
	TweenService:Create(disco, TweenInfo.new(dur), {Size = Vector3.new(0.15, r * 2, r * 2), Transparency = 0.55}):Play()
	TweenService:Create(miolo, TweenInfo.new(dur), {Size = Vector3.new(0.18, r * 1.5, r * 1.5)}):Play()
	task.delay(dur, function()
		TweenService:Create(disco, TweenInfo.new(0.4), {Transparency = 1}):Play(); TweenService:Create(miolo, TweenInfo.new(0.4), {Transparency = 1}):Play()
	end)
	Debris:AddItem(disco, dur + 0.5); Debris:AddItem(miolo, dur + 0.5)
	if f > 0 then
		local a = ancora(d.pos + n * 0.5); Debris:AddItem(a, dur + 1)
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
local function poeiraBase(pos, n, f, qtd)
	local a = ancora(pos + n * 0.3); Debris:AddItem(a, 1.6)
	emissor(a, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.6, Size = ns(0, 0.8, 1, 2.6), Transparency = ns(0, 0.5, 1, 1),
		Lifetime = NumberRange.new(0.6, 1.0), Speed = NumberRange.new(1.5, 4), Drag = 2, SpreadAngle = Vector2.new(70, 70), Rotation = NumberRange.new(0, 360),
		EmissionDirection = Enum.NormalId.Top, Rate = 0})):Emit(math.max(1, math.floor(qtd * f)))
end
local function destruirCorrentes(c, devagar)
	if c.con then c.con:Disconnect(); c.con = nil end
	c.modelo:Destroy()
	for _, x in ipairs(c.extras) do if devagar then Debris:AddItem(x, 1.2) else x:Destroy() end end
end
local function soltarCorrentes(alvo, rapido)
	local c = correntes[alvo]; if not c then return end
	if rapido then correntes[alvo] = nil; destruirCorrentes(c, false); return end
	if c.soltando then return end
	c.soltando = os.clock(); local lento = c.lento or 1
	for _, x in ipairs(c.extras) do local e = x:FindFirstChildOfClass("ParticleEmitter"); if e then e.Rate = 0 end end
	for _, cad in ipairs(c.cad) do poeiraBase(cad.base, cad.normal, c.f, 4) end
	TweenService:Create(c.hl, TweenInfo.new(T_SOLTA * lento), {OutlineTransparency = 1, FillTransparency = 1}):Play()
	task.delay(T_SOLTA * lento + 0.05, function() if correntes[alvo] == c then correntes[alvo] = nil; destruirCorrentes(c, true) end end)
end
local function easeOutBack(x) local k = 1.3; return 1 + (k + 1) * (x - 1) ^ 3 + k * (x - 1) ^ 2 end
local ESCONDE = CFrame.new(0, -500, 0)
local function prender(d, f)
	local alvo = d.alvo; local r = alvo and raizDe(alvo); if not r or f <= 0 then return end
	soltarCorrentes(alvo, true)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {alvo, pastaFX()}; rp.IgnoreWater = true
	local _, ext = alvo:GetBoundingBox()
	local esc = math.clamp(ext.Y / 5.5, 0.8, 2)
	local passo = (ELO.comp - 2 * ELO.fio) * esc
	local hc = workspace:Raycast(r.Position, Vector3.new(0, -30, 0), rp)
	local chaoY = hc and hc.Position.Y or (r.Position.Y - 3)
	local modelo = Instance.new("Model"); modelo.Name = "Correntes_" .. alvo.Name; modelo.Parent = pastaFX()
	local hl = Instance.new("Highlight"); hl.Adornee = modelo; hl.DepthMode = Enum.HighlightDepthMode.Occluded
	hl.FillColor = VIOLETA; hl.FillTransparency = 0.9; hl.OutlineColor = C3(115, 45, 190); hl.OutlineTransparency = 0.5; hl.Parent = modelo
	local lento = math.max(1, tonumber(workspace:GetAttribute("VFXSombra_Lento")) or 1)   -- so revisao (capturas): desacelera a animacao
	local c = {modelo = modelo, hl = hl, cad = {}, extras = {}, t0 = os.clock(), f = f, esc = esc, passo = passo, lento = lento,
		anel = {a = math.max(ext.X / 2 + 0.2 * esc, esc), b = math.max(ext.Z / 2 + 0.3 * esc, esc), y = 0.35 * esc, elos = {}}}
	correntes[alvo] = c
	local giro = math.random() * math.pi * 2
	for i = 1, NCORR do
		local fi = giro + (i - 1) * 2 * math.pi / NCORR + (math.random() - 0.5) * 0.35
		local rb = R_BASE * esc * (0.9 + math.random() * 0.2)
		local pw = r.CFrame * Vector3.new(math.cos(fi) * rb, 0, math.sin(fi) * rb)
		local h = workspace:Raycast(Vector3.new(pw.X, r.Position.Y + 2, pw.Z), Vector3.new(0, -(r.Position.Y - chaoY) - 8, 0), rp)
		if h then                                                         -- sem chao real ali: essa corrente nao existe
			local cad = {fi = fi, base = h.Position, normal = h.Normal, giro = math.random() * math.pi, fase = math.random() * 6, elos = {}}
			for _ = 1, MAX_BASE do table.insert(cad.elos, {pc = novoElo(esc, modelo), vis = false}) end
			table.insert(c.cad, cad)
			local a = ancora(h.Position + h.Normal * 0.3); table.insert(c.extras, a)  -- breu residual na boca do buraco
			emissor(a, flipFumaca({Color = seq({BREU, PRETO}), LightEmission = 0, LightInfluence = 0.6, Size = ns(0, 0.7, 1, 2.2), Transparency = ns(0, 0.6, 1, 1),
				Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(0.5, 1.5), SpreadAngle = Vector2.new(60, 60), Rotation = NumberRange.new(0, 360),
				EmissionDirection = Enum.NormalId.Top, Rate = 3 * f}))
			poeiraBase(h.Position, h.Normal, f, 5)
		end
	end
	local A = c.anel                                                     -- perimetro da elipse (Ramanujan) -> n par de elos
	local per = math.pi * (3 * (A.a + A.b) - math.sqrt((3 * A.a + A.b) * (A.a + 3 * A.b)))
	local n = math.clamp(math.floor(per / passo + 0.5), 8, MAX_ANEL); if n % 2 == 1 then n -= 1 end
	A.n, A.th0 = n, (c.cad[1] and c.cad[1].fi or giro)
	for _ = 1, n do table.insert(A.elos, {pc = novoElo(esc, modelo), vis = false}) end
	local partes, cfs = {}, {}
	local function por(el, cf, tr)
		for _, x in ipairs(el.pc) do table.insert(partes, x[1]); table.insert(cfs, cf * x[2]); if x[1].Transparency ~= tr then x[1].Transparency = tr end end
	end
	local tc = T_SOBE * 0.7 + T_FECHA                                     -- anel fechado
	c.con = RunService.Heartbeat:Connect(function()
		if not (alvo.Parent and r.Parent) then soltarCorrentes(alvo, true); return end
		local agora = os.clock(); local t = (agora - c.t0) / lento
		if not c.soltando and agora - c.t0 > (d.duracao or 2.5) + 1.5 then soltarCorrentes(alvo, false) end   -- seguranca se o "soltar" nao chegar
		local s = c.soltando and math.min(1, (agora - c.soltando) / (T_SOLTA * lento)) or 0
		local tr = s > 0 and s ^ 1.5 or 0
		local rcf = r.CFrame
		local escA = t < tc and 1.15 or 1 + 0.15 * math.exp(-(t - tc) / 0.12) * math.cos(22 * (t - tc))
		escA += 0.35 * s; local dy = -0.9 * esc * s
		local function pontoAnel(th) return rcf * Vector3.new(math.cos(th) * A.a * escA, A.y + dy, math.sin(th) * A.b * escA) end
		table.clear(partes); table.clear(cfs)
		-- correntes do chao: a ponta sobe com inercia (passa um pouco e volta); elos saem empurrados da terra
		local sobe = math.min(1, t / T_SOBE)
		local frac = s > 0 and (1 - s * s) or (sobe < 1 and easeOutBack(sobe) or 1)
		for _, cad in ipairs(c.cad) do
			local alvoP = pontoAnel(cad.fi)
			local V = alvoP - cad.base; local L = V.Magnitude
			if L > (MAX_BASE - 0.5) * passo then                            -- alvo se afastou: a corrente sai de um ponto mais perto
				local p = alvoP - V.Unit * (MAX_BASE - 1) * passo
				local h = workspace:Raycast(p + Vector3.new(0, 3, 0), Vector3.new(0, -12, 0), rp)
				if h then cad.base, cad.normal = h.Position, h.Normal; V = alvoP - cad.base; L = V.Magnitude end
			end
			local u = L > 0.01 and V / L or Vector3.yAxis
			local perp = u:Cross(Vector3.yAxis); perp = perp.Magnitude > 0.1 and perp.Unit or Vector3.xAxis
			local tl = t - T_SOBE
			local amp = (tl > 0 and 0.22 * esc * math.exp(-tl / 0.2) * math.sin(38 * tl) or 0) + 0.02 * esc * math.sin(6 * t + cad.fase)
			local comp = L * frac; local ponta = cad.base + u * comp
			for k, el in ipairs(cad.elos) do
				local sk = (k - 0.5) * passo
				if sk <= comp + 0.1 * passo then
					local x = math.clamp((comp - sk) / L, 0, 1)
					por(el, cfElo(ponta - u * sk + perp * (math.sin(math.pi * x) * amp), u, cad.giro + (k % 2) * math.pi / 2), tr); el.vis = true
				elseif el.vis then por(el, ESCONDE, 1); el.vis = false end
			end
		end
		-- anel: fecha a partir dos pontos de chegada das correntes
		local fecha = math.clamp((t - T_SOBE * 0.7) / T_FECHA, 0, 1)
		local meio = math.pi / math.max(1, #c.cad) + 0.3
		for j, el in ipairs(A.elos) do
			local th = A.th0 + (j - 1) * 2 * math.pi / A.n
			local dmin = math.pi
			if #c.cad == 0 then dmin = 0 else for _, cad in ipairs(c.cad) do local dd = math.abs((th - cad.fi + math.pi) % (2 * math.pi) - math.pi); if dd < dmin then dmin = dd end end end
			if dmin <= fecha * meio then
				local tg = rcf:VectorToWorldSpace(Vector3.new(-math.sin(th) * A.a, 0, math.cos(th) * A.b)).Unit
				por(el, cfElo(pontoAnel(th), tg, (j % 2) * math.pi / 2), tr); el.vis = true
			elseif el.vis then por(el, ESCONDE, 1); el.vis = false end
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
]=====]
local fn, err = loadstring(vfx); assert(fn, "VFXSombra nao compila: " .. tostring(err))
local criarElo = loadstring([=====[
-- criar_elo_sombra.luau (Studio, Edit) — cria/recria ReplicatedStorage.Combate_Dragoes.Elo_Sombra: o elo das Correntes
-- da Noite (VFXSombra v4, 04/11). Anel alongado COM FURO feito por CSG (estadio externo - estadio interno), eixo longo Y,
-- plano XY, espessura Z. Medidas = ELO do VFXSombra (comp 1,1 / larg 0,6 / fio 0,17). Sem colisao/consulta/sombra.
-- Reexecutavel: substitui o elo anterior (nao mexe em mais nada).
local comp, larg, fio = 1.1, 0.6, 0.17
local pasta = game:GetService("ReplicatedStorage"):WaitForChild("Combate_Dragoes")
local tmp = Instance.new("Folder"); tmp.Name = "_tmp_elo"; tmp.Parent = workspace
local function bloco(sz, cf, forma)
	local p = Instance.new("Part"); p.Anchored = true; p.Size = sz; p.CFrame = cf; p.Shape = forma or Enum.PartType.Block; p.Parent = tmp; return p
end
local DISCO = CFrame.Angles(0, math.rad(90), 0)                       -- cilindro do Roblox tem eixo X: gira para Z
local function estadio(w, t, folga)
	local reto = comp - larg                                          -- trecho reto entre as duas pontas redondas
	local partes = {bloco(Vector3.new(w, reto, t + folga), CFrame.new())}
	for _, sy in ipairs({-1, 1}) do table.insert(partes, bloco(Vector3.new(t + folga, w, w), CFrame.new(0, sy * reto / 2, 0) * DISCO, Enum.PartType.Cylinder)) end
	return partes
end
local ok, res = pcall(function()
	local fora = estadio(larg, fio, 0)
	local dentro = estadio(larg - 2 * fio, fio, 0.4)
	local cheio = fora[1]:UnionAsync({fora[2], fora[3]})
	cheio.Parent = tmp
	local buraco = dentro[1]:UnionAsync({dentro[2], dentro[3]})
	buraco.Parent = tmp
	local elo = cheio:SubtractAsync({buraco})
	return elo
end)
if not ok then tmp:Destroy(); error("CSG falhou: " .. tostring(res)) end
local elo = res
elo.Name = "Elo_Sombra"; elo.UsePartColor = true; elo.Color = Color3.fromRGB(20, 13, 28); elo.Material = Enum.Material.Metal
elo.Anchored = true; elo.CanCollide = false; elo.CanQuery = false; elo.CanTouch = false; elo.CastShadow = false
elo.CollisionFidelity = Enum.CollisionFidelity.Box; elo.RenderFidelity = Enum.RenderFidelity.Automatic; elo.SmoothingAngle = 30
elo:SetAttribute("Origem", "sombrio/criar_elo_sombra.luau (04/11)")
local velho = pasta:FindFirstChild("Elo_Sombra"); if velho then velho:Destroy() end
elo.CFrame = CFrame.new(); elo.Parent = pasta
tmp:Destroy()
return ("Elo_Sombra criado: tamanho %s"):format(tostring(elo.Size))
]=====]); assert(criarElo, "criar_elo nao compila")
local nome = "Backup_VFXSombra_Revisao_2026-11-04"
if not SS:FindFirstChild(nome) then local f = Instance.new("Folder"); f.Name = nome; M:Clone().Parent = f; f.Parent = SS end
local r = criarElo()
M.Source = vfx
return "aplicado: VFXSombra (" .. #vfx .. " bytes) | " .. r .. " | backup ServerStorage." .. nome
