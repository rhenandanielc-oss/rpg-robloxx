-- VFXCombate (ModuleScript, ReplicatedStorage.Combate_Dragoes) — efeitos COSMETICOS do combate, so no cliente.
-- Recebe eventos do servidor (RemoteEvent FX) e desenha por elemento: Fogo (chamas/brasas/fumaca/calor), Terra (rochas,
-- poeira, ondas de choque, rachaduras temporarias), Raio (descargas ramificadas, clarao curto sem estroboscopia),
-- Ar (vortices, aneis de pressao, poeira levada). Nada aqui altera dano/alvos; nada altera Terrain/Parts do mapa.
-- LOD: distancia da camera + nivel grafico; teto de luzes; emissores do sopro reaproveitados por dragao.
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local M = {}

local TEX = {fogo = "rbxasset://textures/particles/fire_main.dds", fumaca = "rbxasset://textures/particles/smoke_main.dds", faisca = "rbxasset://textures/particles/sparkles_main.dds"}
-- flipbooks proprios 8x8 (V14/vfx/gerar_flipbooks.py): o quadro avanca com a vida da particula (nasce quente, esfria, some)
local FB = {fogo = "rbxassetid://81072138040568", fumaca = "rbxassetid://114973539727313", lava = "rbxassetid://76516973198217"}
local function flip(t, tex)
	t.Texture = tex; t.FlipbookLayout = Enum.ParticleFlipbookLayout.Grid8x8; t.FlipbookMode = Enum.ParticleFlipbookMode.OneShot
	return t
end
local C3 = Color3.fromRGB
local BRANCO = ColorSequence.new(Color3.new(1, 1, 1))
local PERFIL = {
	Fogo = {cor = C3(255, 120, 30), luz = C3(255, 140, 50), nucleo = {C3(255, 245, 170), C3(255, 170, 40), C3(230, 70, 15), C3(90, 20, 10)}},
	Terra = {cor = C3(150, 110, 75), luz = C3(255, 190, 120), nucleo = {C3(200, 170, 130), C3(140, 105, 75), C3(90, 70, 55), C3(60, 50, 45)}},
	Raio = {cor = C3(150, 200, 255), luz = C3(170, 210, 255), nucleo = {C3(255, 255, 255), C3(170, 215, 255), C3(90, 140, 255), C3(40, 60, 160)}},
	Ar = {cor = C3(215, 235, 245), luz = C3(220, 240, 255), nucleo = {C3(255, 255, 255), C3(220, 240, 250), C3(190, 215, 230), C3(160, 185, 200)}},
}
local function seq(cs) local k = {}; for i, c in ipairs(cs) do table.insert(k, ColorSequenceKeypoint.new((i - 1) / (#cs - 1), c)) end; return ColorSequence.new(k) end
local function ns(...) local a = {...}; local k = {}; for i = 1, #a, 2 do table.insert(k, NumberSequenceKeypoint.new(a[i], a[i + 1])) end; return NumberSequence.new(k) end

-- ===== LOD ======================================================================================================
local function fatorLOD(pos)
	local cam = workspace.CurrentCamera; if not cam or not pos then return 1 end
	local d = (pos - cam.CFrame.Position).Magnitude
	if d > 700 then return 0 end
	local f = d < 250 and 1 or 0.5
	local q = UserSettings():GetService("UserGameSettings").SavedQualityLevel.Value
	if q ~= 0 and q <= 3 then f *= 0.45 elseif q ~= 0 and q <= 6 then f *= 0.75 end
	return f
end
local luzesAtivas = 0
local function luz(pai, cor, brilho, alcance, dur)
	if luzesAtivas >= 6 then return end
	local l = Instance.new("PointLight"); l.Color = cor; l.Brightness = brilho; l.Range = alcance; l.Shadows = false; l.Parent = pai
	luzesAtivas += 1
	if dur then
		TweenService:Create(l, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Brightness = 0}):Play()
		task.delay(dur, function() l:Destroy(); luzesAtivas -= 1 end)
	end
	return l
end
local function liberarLuz(l) if l and l.Parent then l:Destroy(); luzesAtivas -= 1 end end

-- ===== ancoras no mundo ==========================================================================================
local function ancora(pos)
	local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain; return a
end
local function emissor(pai, t)
	local e = Instance.new("ParticleEmitter")
	for k, v in pairs(t) do e[k] = v end
	e.Parent = pai; return e
end
local function osso(m, nome) for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == nome then return d end end end
local function bocaDe(m)
	local cab = osso(m, "Cabeca"); local pes = osso(m, "Pescoco4")
	if not cab then return m:GetPivot().Position, m:GetPivot().LookVector end
	local cf = cab.TransformedWorldCFrame; local dir = cf.UpVector               -- eixo do osso Cabeca = nuca -> focinho
	return cf.Position + dir * 10 + Vector3.new(0, -1.5, 0), dir
end

-- ===== sopro (emissores reaproveitados por dragao) ===============================================================
local estado = {}                                                   -- [modelo] = {anc, emissores, luz, conexao}
local function emissoresSopro(m, el)
	local s = estado[m] or {}; estado[m] = s
	if s.el == el and s.anc and s.anc.Parent then return s end
	if s.anc then s.anc:Destroy() end
	s.el = el; s.anc = ancora(m:GetPivot().Position); s.e = {}
	local P = PERFIL[el]
	if el == "Fogo" then
		-- labareda: flipbook com cor embutida (branco-amarelo -> laranja -> vermelho escuro), cresce e desacelera no ar
		-- Speed e calculado em ligarSopro a partir do ALCANCE validado pelo servidor (o jato visual termina onde a hitbox termina)
		s.e.nucleo = emissor(s.anc, flip({Color = BRANCO, LightEmission = 0.55, LightInfluence = 0, Size = ns(0, 2.2, 0.2, 9, 0.6, 18, 1, 26),
			Transparency = ns(0, 0, 0.85, 0.15, 1, 1), Lifetime = NumberRange.new(1.0, 1.1), Speed = NumberRange.new(130, 150), SpreadAngle = Vector2.new(5, 5),
			Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-45, 45), Drag = 0.6, Acceleration = Vector3.new(0, 7, 0), Rate = 0,
			EmissionDirection = Enum.NormalId.Front, ZOffset = 1}, FB.fogo))
		-- chamas secundarias volumosas que enchem o meio do jato (mais lentas, maiores)
		s.e.chamas = emissor(s.anc, flip({Color = BRANCO, LightEmission = 0.4, LightInfluence = 0.1, Size = ns(0, 4, 0.5, 16, 1, 22),
			Transparency = ns(0, 0.15, 0.8, 0.35, 1, 1), Lifetime = NumberRange.new(0.8, 1.0), Speed = NumberRange.new(70, 90), SpreadAngle = Vector2.new(8, 8),
			Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30), Drag = 0.9, Acceleration = Vector3.new(0, 10, 0), Rate = 0,
			EmissionDirection = Enum.NormalId.Front}, FB.fogo))
		-- jato quente junto a boca (curto e muito claro)
		s.e.jato = emissor(s.anc, flip({Color = ColorSequence.new(C3(255, 250, 225), C3(255, 200, 120)), LightEmission = 1, LightInfluence = 0, Size = ns(0, 1.2, 1, 6),
			Transparency = ns(0, 0.15, 1, 1), Lifetime = NumberRange.new(0.12, 0.2), Speed = NumberRange.new(110, 130), SpreadAngle = Vector2.new(3, 3),
			Rotation = NumberRange.new(0, 360), Rate = 0, EmissionDirection = Enum.NormalId.Front, ZOffset = 2}, FB.fogo))
		-- fumaca escura que sobe da ponta das chamas (recebe luz da cena: nao brilha)
		s.e.fumaca = emissor(s.anc, flip({Color = seq({C3(70, 55, 48), C3(38, 34, 33)}), LightInfluence = 1, Size = ns(0, 5, 1, 30), Transparency = ns(0, 0.3, 0.6, 0.55, 1, 1),
			Lifetime = NumberRange.new(1.5, 2.3), Speed = NumberRange.new(55, 75), SpreadAngle = Vector2.new(11, 11), Rate = 0, EmissionDirection = Enum.NormalId.Front,
			Drag = 1.6, Acceleration = Vector3.new(0, 7, 0), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-25, 25), ZOffset = -1}, FB.fumaca))
		s.e.brasas = emissor(s.anc, {Texture = TEX.faisca, Color = seq({C3(255, 235, 160), C3(255, 120, 30), C3(200, 50, 10)}), LightEmission = 1, Size = ns(0, 0.55, 0.7, 0.4, 1, 0),
			Lifetime = NumberRange.new(0.9, 1.7), Speed = NumberRange.new(80, 130), SpreadAngle = Vector2.new(14, 14), Acceleration = Vector3.new(0, -18, 0), Drag = 1.1,
			Rate = 0, EmissionDirection = Enum.NormalId.Front})
	elseif el == "Terra" then
		s.e.poeira = emissor(s.anc, {Texture = TEX.fumaca, Color = seq(P.nucleo), Size = ns(0, 3, 1, 12), Transparency = ns(0, 0.5, 1, 1),
			Lifetime = NumberRange.new(0.5, 0.9), Speed = NumberRange.new(30, 55), SpreadAngle = Vector2.new(18, 18), Rate = 0, EmissionDirection = Enum.NormalId.Front})
		s.e.lascas = emissor(s.anc, {Texture = TEX.faisca, Color = seq({C3(170, 140, 110), C3(90, 75, 60)}), Size = ns(0, 1.2, 1, 0.6), LightEmission = 0.2,
			Lifetime = NumberRange.new(0.6, 1.0), Speed = NumberRange.new(60, 90), SpreadAngle = Vector2.new(12, 12), Acceleration = Vector3.new(0, -60, 0), Rate = 0, EmissionDirection = Enum.NormalId.Front})
	elseif el == "Raio" then
		s.e.faiscas = emissor(s.anc, {Texture = TEX.faisca, Color = seq(P.nucleo), LightEmission = 1, Size = ns(0, 1.4, 1, 0), Lifetime = NumberRange.new(0.15, 0.35),
			Speed = NumberRange.new(15, 40), SpreadAngle = Vector2.new(70, 70), Rate = 0, EmissionDirection = Enum.NormalId.Front})
	else -- Ar
		s.e.vortice = emissor(s.anc, {Texture = TEX.fumaca, Color = seq(P.nucleo), Size = ns(0, 5, 1, 26), Transparency = ns(0, 0.45, 0.6, 0.7, 1, 1),
			Lifetime = NumberRange.new(0.6, 0.9), Speed = NumberRange.new(80, 110), SpreadAngle = Vector2.new(20, 20), Rotation = NumberRange.new(0, 360),
			RotSpeed = NumberRange.new(260, 420), Rate = 0, EmissionDirection = Enum.NormalId.Front, Drag = 0.8})
		s.e.linhas = emissor(s.anc, {Texture = TEX.faisca, Color = seq({C3(255, 255, 255), C3(200, 230, 245)}), Size = ns(0, 1.1, 1, 0.2), LightEmission = 0.7,
			Lifetime = NumberRange.new(0.4, 0.7), Speed = NumberRange.new(120, 160), SpreadAngle = Vector2.new(25, 25), Rate = 0, EmissionDirection = Enum.NormalId.Front})
	end
	return s
end
-- perfil de alcance de cada emissor do sopro: velocidade inicial para a particula percorrer 'frac' do alcance com
-- arrasto 'drag' durante 'vida' segundos: d = v/drag * (1 - e^(-drag*vida))
local ALCANCE = {nucleo = {1.0, 0.6, 1.05}, chamas = {0.7, 0.9, 0.9}, fumaca = {0.9, 1.6, 1.9}, brasas = {1.05, 1.1, 1.3},
	vortice = {1.0, 0.8, 0.9}, linhas = {1.0, 0.0, 0.6}, poeira = {0.35, 1.0, 0.7}, lascas = {0.45, 0.0, 0.8}}
local function velPara(alc, frac, drag, vida)
	local d = alc * frac
	if drag <= 0.01 then return d / vida end
	return d * drag / (1 - math.exp(-drag * vida))
end
local TAXAS = {nucleo = 210, chamas = 70, jato = 120, fumaca = 38, brasas = 70, poeira = 90, lascas = 60, faiscas = 120, vortice = 170, linhas = 140}
local function seguirBoca(m, s)
	if s.con then s.con:Disconnect() end
	s.con = RunService.RenderStepped:Connect(function()
		local b, d = bocaDe(m)
		if s.alvo then local v = s.alvo - b; if v.Magnitude > 5 then d = (d * 0.3 + v.Unit * 0.7).Unit end end   -- mira no alvo validado pelo servidor
		s.anc.WorldCFrame = CFrame.lookAt(b, b + d)
	end)
end
local miraSopro, soproAtivo = {}, {}                                  -- mira viva e ficha do sopro em curso, por dragao
local function ligarSopro(m, el, ligado, fator, alvo, alcance)
	local s = emissoresSopro(m, el); s.alvo = alvo
	if ligado then
		seguirBoca(m, s)
		for k, e in pairs(s.e) do
			e.Rate = (TAXAS[k] or 60) * fator
			local a = ALCANCE[k]
			if a and alcance then                                          -- casa o alcance visual com a hitbox
				local v = velPara(alcance, a[1], a[2], a[3]); e.Drag = a[2]; e.Lifetime = NumberRange.new(a[3] * 0.92, a[3])
				e.Speed = NumberRange.new(v * 0.92, v * 1.04)
			end
		end
		if not s.luz then s.luz = luz(s.anc, PERFIL[el].luz, el == "Raio" and 2 or 3.5, 45) end
	else
		for _, e in pairs(s.e) do e.Rate = 0 end
		liberarLuz(s.luz); s.luz = nil
		task.delay(1.6, function() if s.con and not s.e.nucleo or (s.e.nucleo and s.e.nucleo.Rate == 0) then if s.con then s.con:Disconnect(); s.con = nil end end end)
	end
end

-- ===== pecas temporarias =========================================================================================
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
-- rocha vulcanica irregular: lascas de basalto inclinadas em volta de um nucleo incandescente (nada de cilindro/bloco unico)
local function rochaVulcanica(base, normal, altura, largura, quente)
	local m = Instance.new("Model"); m.Name = "Pilar"
	local up = (Vector3.yAxis * 0.8 + (normal or Vector3.yAxis) * 0.2).Unit       -- segue o relevo so em parte (pilar continua "de pe")
	local x = up:Cross(Vector3.zAxis); if x.Magnitude < 0.1 then x = up:Cross(Vector3.xAxis) end
	local cf0 = CFrame.fromMatrix(base, x.Unit, up) * CFrame.Angles(0, math.random() * 6.28, 0)
	local n = 4 + math.random(0, 2)
	for i = 1, n do
		local h = altura * (0.55 + math.random() * 0.5); local w = largura * (0.35 + math.random() * 0.35); local dd = largura * (0.3 + math.random() * 0.3)
		local ang = i / n * 6.28 + math.random() * 0.6; local off = Vector3.new(math.cos(ang), 0, math.sin(ang)) * largura * 0.28
		local inc = CFrame.Angles(math.rad(math.random(-16, 16)), math.random() * 6.28, math.rad(math.random(-16, 16)))
		local wedge = math.random() < 0.55
		local cf = cf0 * CFrame.new(off) * inc * CFrame.new(0, h / 2, 0) * (wedge and CFrame.Angles(0, math.random(0, 3) * math.pi / 2, 0) or CFrame.new())
		peca({Size = Vector3.new(w, h, dd), CFrame = cf, Material = Enum.Material.Basalt, Color = C3(48 + math.random(-6, 6), 40, 37), Parent = m}, wedge and "WedgePart" or "Part")
	end
	-- nucleo de magma visivel entre as lascas
	peca({Size = Vector3.new(largura * 0.45, altura * 0.85, largura * 0.45), CFrame = cf0 * CFrame.new(0, altura * 0.42, 0) * CFrame.Angles(0, 0.7, math.rad(math.random(-8, 8))),
		Material = quente and Enum.Material.CrackedLava or Enum.Material.Basalt, Color = quente and C3(255, 110, 30) or C3(60, 45, 40), Parent = m})
	-- ponta irregular: duas cunhas costas com costas formam um pico quebrado e torto (silhueta pontiaguda, nao bloco)
	local hp = altura * (0.35 + math.random() * 0.25); local wp = largura * 0.5
	local topo = cf0 * CFrame.new(math.random(-1, 1) * largura * 0.08, altura * 0.98 + hp / 2, 0) * CFrame.Angles(math.rad(math.random(-14, 14)), math.random() * 6.28, math.rad(math.random(-14, 14)))
	peca({Size = Vector3.new(wp, hp, wp * 0.5), CFrame = topo * CFrame.new(0, 0, wp * 0.25), Material = Enum.Material.Basalt, Color = C3(42, 35, 33), Parent = m}, "WedgePart")
	peca({Size = Vector3.new(wp, hp, wp * 0.5), CFrame = topo * CFrame.new(0, 0, -wp * 0.25) * CFrame.Angles(0, math.pi, 0), Material = Enum.Material.Basalt, Color = C3(46, 38, 35), Parent = m}, "WedgePart")
	for i = 1, 2 do                                                  -- estilhacos laterais
		local ang = math.random() * 6.28
		peca({Size = Vector3.new(largura * 0.3, altura * (0.3 + math.random() * 0.2), largura * 0.25), Material = Enum.Material.Basalt, Color = C3(50, 41, 37), Parent = m,
			CFrame = cf0 * CFrame.new(math.cos(ang) * largura * 0.5, altura * 0.2, math.sin(ang) * largura * 0.5) * CFrame.Angles(math.rad(math.random(-35, 35)), ang, math.rad(math.random(-35, 35)))}, "WedgePart")
	end
	m.Parent = pastaFX()
	return m, cf0
end
local function anel(centro, raioFinal, cor, dur, altura, transp, normal)
	local cf = normal and (CFrame.lookAt(centro, centro + normal) * CFrame.Angles(0, math.rad(90), 0)) or (CFrame.new(centro) * CFrame.Angles(0, 0, math.rad(90)))
	local a = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(altura or 1, 4, 4), Material = Enum.Material.Neon, Color = cor,
		Transparency = transp or 0.45, CFrame = cf})
	TweenService:Create(a, TweenInfo.new(dur, Enum.EasingStyle.Quint, Enum.EasingDirection.Out), {Size = Vector3.new(0.3, raioFinal * 2, raioFinal * 2), Transparency = 1}):Play()
	Debris:AddItem(a, dur + 0.05)
end
local function rajada(pos, el, escala, fator)
	if fator <= 0 then return end
	local P = PERFIL[el]; local a = ancora(pos); Debris:AddItem(a, 3)
	local n = math.floor(30 * escala * fator)
	if el == "Fogo" then
		emissor(a, flip({Color = BRANCO, LightEmission = 0.5, LightInfluence = 0, Size = ns(0, 4 * escala, 0.4, 13 * escala, 1, 17 * escala), Transparency = ns(0, 0, 1, 1),
			Lifetime = NumberRange.new(0.6, 1.0), Speed = NumberRange.new(14, 40), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, 14, 0), Rate = 0, Drag = 3,
			Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-30, 30)}, FB.fogo)):Emit(n)
		emissor(a, {Texture = TEX.faisca, Color = seq({C3(255, 230, 150), C3(255, 90, 20)}), LightEmission = 1, Size = ns(0, 0.8, 1, 0), Lifetime = NumberRange.new(0.8, 1.5),
			Speed = NumberRange.new(40, 90), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, -50, 0), Rate = 0}):Emit(n)
		emissor(a, flip({Color = seq({C3(70, 55, 48), C3(35, 31, 30)}), LightInfluence = 1, Size = ns(0, 6 * escala, 1, 24 * escala), Transparency = ns(0, 0.35, 1, 1),
			Lifetime = NumberRange.new(1.6, 2.4), Speed = NumberRange.new(6, 18), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, 9, 0), Rate = 0,
			Rotation = NumberRange.new(0, 360)}, FB.fumaca)):Emit(math.floor(n / 3))
		luz(a, P.luz, 6, 50 * escala, 0.45)
		anel(pos, 26 * escala, C3(255, 120, 40), 0.5, 1)
	elseif el == "Terra" then
		-- impacto de rocha vulcanica: poeira, respingos de magma, chamas curtas, lascas de basalto e fissuras que esfriam
		emissor(a, flip({Color = seq({C3(130, 108, 88), C3(85, 72, 62)}), LightInfluence = 1, Size = ns(0, 6 * escala, 1, 24 * escala), Transparency = ns(0, 0.3, 1, 1),
			Lifetime = NumberRange.new(1.2, 2.0), Speed = NumberRange.new(14, 34), SpreadAngle = Vector2.new(180, 60), Acceleration = Vector3.new(0, 4, 0), Rate = 0, Drag = 2,
			Rotation = NumberRange.new(0, 360)}, FB.fumaca)):Emit(math.floor(n / 2))
		emissor(a, flip({Color = BRANCO, LightEmission = 0.35, LightInfluence = 0.2, Size = ns(0, 1.4, 1, 0.8), Lifetime = NumberRange.new(0.9, 1.4), Speed = NumberRange.new(25, 50),
			SpreadAngle = Vector2.new(55, 55), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, -70, 0), Rotation = NumberRange.new(0, 360), Rate = 0}, FB.lava)):Emit(math.floor(n * 0.6))
		emissor(a, flip({Color = BRANCO, LightEmission = 0.5, LightInfluence = 0, Size = ns(0, 3 * escala, 0.4, 9 * escala, 1, 12 * escala), Transparency = ns(0, 0, 1, 1),
			Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(10, 25), SpreadAngle = Vector2.new(60, 60), EmissionDirection = Enum.NormalId.Top, Rate = 0,
			Rotation = NumberRange.new(0, 360)}, FB.fogo)):Emit(math.floor(n / 3))
		luz(a, C3(255, 140, 60), 3, 35 * escala, 0.5)
		for i = 1, math.floor(10 * escala * fator) do                  -- detritos (temporarios)
			local r = peca({Size = Vector3.new(1, 0.8, 1.2) * (1 + math.random() * 2.2 * escala), Material = Enum.Material.Basalt, Color = C3(55, 45, 40),
				CFrame = CFrame.new(pos) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)}, math.random() < 0.6 and "WedgePart" or "Part")
			local alvo = pos + Vector3.new(math.random(-1, 1) * math.random() * 22 * escala, 4 + math.random() * 12 * escala, math.random(-1, 1) * math.random() * 22 * escala)
			TweenService:Create(r, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Position = alvo}):Play()
			task.delay(0.35, function() if r.Parent then TweenService:Create(r, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Position = Vector3.new(alvo.X, pos.Y, alvo.Z), Transparency = 0.3}):Play() end end)
			Debris:AddItem(r, 2.2)
		end
		for i = 1, 5 do                                               -- rachaduras temporarias quebradas em 2 trechos (pecas, nao o terreno)
			local ang = math.rad(i * 72 + math.random(-15, 15)); local L = (8 + math.random() * 10) * escala
			local meio = pos + Vector3.new(math.cos(ang), 0, math.sin(ang)) * L * 0.55 + Vector3.new(math.random(-2, 2), 0, math.random(-2, 2))
			M.fissura(pos, meio, 1.4, 0.45); M.fissura(meio, pos + Vector3.new(math.cos(ang + 0.3), 0, math.sin(ang + 0.3)) * L, 1.4, 0.3)
		end
		anel(pos, 30 * escala, C3(150, 120, 95), 0.6, 0.6, 0.6)
	elseif el == "Raio" then
		luz(a, P.luz, 7, 55 * escala, 0.18)                            -- clarao unico e curto
		emissor(a, {Texture = TEX.faisca, Color = seq(P.nucleo), LightEmission = 1, Size = ns(0, 1.6, 1, 0), Lifetime = NumberRange.new(0.2, 0.5),
			Speed = NumberRange.new(30, 80), SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(n)
		for i = 1, 4 do                                               -- ramificacoes na superficie
			local ang = math.random() * math.pi * 2
			M.descarga(pos + Vector3.new(0, 1, 0), pos + Vector3.new(math.cos(ang), 0, math.sin(ang)) * (12 + math.random() * 14) * escala, el, 0.25, 0.8)
		end
		anel(pos, 20 * escala, C3(160, 210, 255), 0.3, 0.6, 0.3)
	else -- Ar
		emissor(a, {Texture = TEX.fumaca, Color = seq(P.nucleo), Size = ns(0, 6 * escala, 1, 30 * escala), Transparency = ns(0, 0.7, 1, 1), Lifetime = NumberRange.new(0.8, 1.3),
			Speed = NumberRange.new(40, 70), SpreadAngle = Vector2.new(180, 25), RotSpeed = NumberRange.new(200, 400), Rotation = NumberRange.new(0, 360), Rate = 0, Drag = 2.5}):Emit(n)
		emissor(a, {Texture = TEX.fumaca, Color = seq({C3(170, 150, 120), C3(130, 115, 95)}), Size = ns(0, 4, 1, 14), Transparency = ns(0, 0.55, 1, 1),
			Lifetime = NumberRange.new(0.9, 1.4), Speed = NumberRange.new(25, 50), SpreadAngle = Vector2.new(180, 10), Rate = 0}):Emit(math.floor(n / 2))
		anel(pos, 40 * escala, C3(225, 240, 250), 0.55, 0.5, 0.6); task.delay(0.12, function() anel(pos, 30 * escala, C3(225, 240, 250), 0.5, 0.5, 0.7) end)
	end
end

-- descarga ramificada (Beams entre attachments com desvios); dur curta e unica
function M.descarga(de, ate, el, dur, largura)
	local P = PERFIL[el or "Raio"]
	local n = 9; local pts = {}; local d = ate - de
	local lado = d:Cross(Vector3.yAxis); lado = lado.Magnitude > 0.01 and lado.Unit or Vector3.xAxis
	local cima = lado:Cross(d.Unit)
	for i = 0, n do
		local t = i / n; local amp = (i == 0 or i == n) and 0 or d.Magnitude * 0.06
		table.insert(pts, ancora(de + d * t + lado * (math.random() - 0.5) * 2 * amp + cima * (math.random() - 0.5) * 2 * amp))
	end
	for i = 1, n do
		local b = Instance.new("Beam"); b.Attachment0 = pts[i]; b.Attachment1 = pts[i + 1]; b.Color = ColorSequence.new(P.nucleo[1], P.nucleo[2])
		b.LightEmission = 1; b.LightInfluence = 0; b.Width0 = largura or 2.2; b.Width1 = (largura or 2.2) * 0.8; b.FaceCamera = true; b.Segments = 1
		b.Transparency = NumberSequence.new(0); b.Parent = pts[i]
		TweenService:Create(b, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Width0 = 0, Width1 = 0}):Play()
	end
	for _, p in ipairs(pts) do Debris:AddItem(p, dur + 0.05) end
end

-- projetil (Terra): bolo de rocha vulcanica com rachaduras de magma, girando em arco leve, com rastro de calor,
-- fumaca e respingos de lava (o acerto e calculado no servidor no destino; isto so desenha o voo)
local function projetil(de, ate, tempo, fator)
	local corpo = peca({Size = Vector3.new(4.6, 4.0, 4.3), Material = Enum.Material.CrackedLava, Color = C3(255, 120, 40), CFrame = CFrame.new(de)})
	local cascas = {}
	for i = 1, 3 do
		table.insert(cascas, {peca({Size = Vector3.new(3.2 + math.random(), 2.4 + math.random(), 2.2), Material = Enum.Material.Basalt, Color = C3(52, 42, 38)}, i == 2 and "WedgePart" or "Part"),
			CFrame.Angles(math.random() * 6, math.random() * 6, math.random() * 6) * CFrame.new(0, 1.3, 0)})
	end
	local a0 = Instance.new("Attachment", corpo); a0.Position = Vector3.new(0, 1.4, 0); local a1 = Instance.new("Attachment", corpo); a1.Position = Vector3.new(0, -1.4, 0)
	local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = 0.25; tr.LightEmission = 0.8; tr.FaceCamera = true
	tr.Color = seq({C3(255, 220, 140), C3(255, 110, 30), C3(120, 30, 10)}); tr.Transparency = ns(0, 0.2, 1, 1); tr.WidthScale = ns(0, 1, 1, 0.2); tr.Parent = corpo
	local ac = Instance.new("Attachment", corpo)
	emissor(ac, flip({Color = BRANCO, LightEmission = 0.5, LightInfluence = 0, Size = ns(0, 3.5, 1, 9), Transparency = ns(0, 0.1, 1, 1), Lifetime = NumberRange.new(0.3, 0.5),
		Speed = NumberRange.new(1, 4), Rotation = NumberRange.new(0, 360), Rate = 70 * fator}, FB.fogo))
	emissor(ac, flip({Color = seq({C3(80, 65, 55), C3(40, 36, 34)}), LightInfluence = 1, Size = ns(0, 3, 1, 12), Transparency = ns(0, 0.45, 1, 1), Lifetime = NumberRange.new(0.8, 1.3),
		Speed = NumberRange.new(1, 3), Acceleration = Vector3.new(0, 5, 0), Rotation = NumberRange.new(0, 360), Rate = 28 * fator}, FB.fumaca))
	emissor(ac, {Texture = TEX.faisca, Color = seq({C3(255, 230, 150), C3(255, 100, 20)}), LightEmission = 1, Size = ns(0, 0.5, 1, 0), Lifetime = NumberRange.new(0.5, 0.9),
		Speed = NumberRange.new(4, 12), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, -40, 0), Rate = 40 * fator})
	local l = luz(corpo, C3(255, 140, 60), 2.5, 22)
	local t0 = os.clock(); local giro = CFrame.Angles(math.random() * 2, math.random() * 2, 0)
	local arco = math.min((ate - de).Magnitude * 0.08, 10)
	local con; con = RunService.RenderStepped:Connect(function()
		local k = math.min((os.clock() - t0) / tempo, 1)
		local p = de:Lerp(ate, k) + Vector3.new(0, math.sin(k * math.pi) * arco, 0)
		local cf = CFrame.new(p) * CFrame.Angles(k * 9, k * 6, 0) * giro
		corpo.CFrame = cf
		for _, c in ipairs(cascas) do c[1].CFrame = cf * c[2] end
		if k >= 1 then con:Disconnect(); corpo:Destroy(); for _, c in ipairs(cascas) do c[1]:Destroy() end; liberarLuz(l) end
	end)
end

-- ===== aura do Dominio ===========================================================================================
local auras = {}
local function aura(m, el, ligar, dur)
	if auras[m] then for _, x in ipairs(auras[m]) do x:Destroy() end; auras[m] = nil end
	if not ligar then
		for _, p in ipairs(m:GetDescendants()) do if p:IsA("BasePart") and p.Name:find("Brilho") then TweenService:Create(p, TweenInfo.new(0.8), {Transparency = 0.8}):Play() end end
		return
	end
	local P = PERFIL[el]; local lista = {}; auras[m] = lista
	for _, nome in ipairs({"Coluna2", "Pescoco2", "Cauda3", "AsaE_2", "AsaD_2", "Quadril"}) do
		local b = osso(m, nome)
		if b then
			local props = el == "Fogo" and {Texture = TEX.faisca, Color = seq({C3(255, 220, 140), C3(255, 90, 20)}), LightEmission = 1, Size = ns(0, 1.0, 1, 0), Lifetime = NumberRange.new(1, 1.8), Speed = NumberRange.new(4, 10), Acceleration = Vector3.new(0, 12, 0), Rate = 14, SpreadAngle = Vector2.new(180, 180)}
				or el == "Terra" and {Texture = TEX.faisca, Color = seq({C3(185, 150, 115), C3(110, 90, 70)}), Size = ns(0, 1.3, 1, 0.8), Lifetime = NumberRange.new(1.2, 2), Speed = NumberRange.new(2, 5), Acceleration = Vector3.new(0, 6, 0), Rate = 10, SpreadAngle = Vector2.new(180, 180)}
				or el == "Raio" and {Texture = TEX.faisca, Color = seq(P.nucleo), LightEmission = 1, Size = ns(0, 1.2, 1, 0), Lifetime = NumberRange.new(0.15, 0.3), Speed = NumberRange.new(10, 25), Rate = 8, SpreadAngle = Vector2.new(180, 180)}
				or {Texture = TEX.fumaca, Color = seq(P.nucleo), Size = ns(0, 3, 1, 9), Transparency = ns(0, 0.8, 1, 1), Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(14, 22), RotSpeed = NumberRange.new(200, 360), Rate = 10, SpreadAngle = Vector2.new(180, 30)}
			table.insert(lista, emissor(b, props))
		end
	end
	if el == "Fogo" then for _, p in ipairs(m:GetDescendants()) do if p:IsA("BasePart") and p.Name:find("Brilho") then TweenService:Create(p, TweenInfo.new(0.6), {Transparency = 0.55}):Play() end end end
	if el == "Raio" then                                              -- arcos discretos e espacados entre ossos
		task.spawn(function()
			local t0 = os.clock()
			while auras[m] == lista and os.clock() - t0 < (dur or 12) do
				local a, b = osso(m, ({"AsaE_2", "Coluna3", "Cauda2"})[math.random(3)]), osso(m, ({"Dedo1E", "Pescoco3", "Cauda5", "Dedo1D"})[math.random(4)])
				if a and b then M.descarga(a.TransformedWorldCFrame.Position, b.TransformedWorldCFrame.Position, "Raio", 0.15, 0.8) end
				task.wait(0.9 + math.random() * 0.6)
			end
		end)
	end
end

-- ===== reacao do alvo ============================================================================================
local function reacao(alvo, el, intensidade)
	if not alvo or not alvo.Parent then return end
	local h = Instance.new("Highlight"); h.FillColor = PERFIL[el or "Fogo"].cor; h.OutlineTransparency = 1
	h.FillTransparency = intensidade == "pesado" and 0.25 or intensidade == "moderado" and 0.45 or 0.65; h.Parent = alvo
	TweenService:Create(h, TweenInfo.new(0.35), {FillTransparency = 1}):Play(); Debris:AddItem(h, 0.4)
	local lp = Players.LocalPlayer
	if lp and lp.Character == alvo then                                -- tremor curto e contido so para quem foi atingido
		local amp = intensidade == "pesado" and 0.35 or intensidade == "moderado" and 0.2 or 0.1
		local cam = workspace.CurrentCamera; local t0 = os.clock()
		local c; c = RunService.RenderStepped:Connect(function()
			local k = 1 - (os.clock() - t0) / 0.25; if k <= 0 then c:Disconnect(); return end
			cam.CFrame *= CFrame.new((math.random() - 0.5) * amp * k, (math.random() - 0.5) * amp * k, 0)
		end)
	end
end

-- ===== Ruptura Vulcanica =========================================================================================
local function tremor(pos, forca, dur)                              -- moderado e localizado (cai com a distancia)
	local cam = workspace.CurrentCamera; if not cam then return end
	local d = (cam.CFrame.Position - pos).Magnitude; local amp = forca * math.clamp(1 - d / 160, 0, 1)
	if amp <= 0.02 then return end
	local t0 = os.clock()
	local c; c = RunService.RenderStepped:Connect(function()
		local k = 1 - (os.clock() - t0) / dur; if k <= 0 then c:Disconnect(); return end
		cam.CFrame *= CFrame.Angles((math.random() - 0.5) * amp * 0.02 * k, (math.random() - 0.5) * amp * 0.02 * k, 0) * CFrame.new((math.random() - 0.5) * amp * k, (math.random() - 0.5) * amp * k, 0)
	end)
end
local function fissura(de, ate, dur, largura)                        -- rachadura luminosa temporaria que corre pelo chao
	local v = Vector3.new(ate.X - de.X, 0, ate.Z - de.Z); local L = v.Magnitude; if L < 1 then return end
	local cf = CFrame.lookAt(de + Vector3.new(0, 0.12, 0), de + v + Vector3.new(0, 0.12, 0))
	local f = peca({Size = Vector3.new(largura or 0.9, 0.15, 0.1), Material = Enum.Material.Neon, Color = C3(255, 140, 50), Transparency = 0.05, CFrame = cf})
	TweenService:Create(f, TweenInfo.new(0.22, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = Vector3.new(largura or 0.9, 0.15, L), CFrame = cf * CFrame.new(0, 0, -L / 2)}):Play()
	task.delay(0.25, function() TweenService:Create(f, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Color = C3(70, 40, 30), Transparency = 1}):Play() end)
	Debris:AddItem(f, dur + 0.35)
end
M.fissura = fissura
local rupturas = {}
local function brilhoCorpo(m, alvoT, dur)
	for _, p in ipairs(m:GetDescendants()) do if p:IsA("BasePart") and p.Name:find("Brilho") then TweenService:Create(p, TweenInfo.new(dur), {Transparency = alvoT}):Play() end end
end
local function pilarErupcao(p, f, centro)
	local alt = (16 + math.random() * 12) * (0.85 + 0.15 * p.anel); local larg = 5.5 + math.random() * 3
	local pilar, cf0 = rochaVulcanica(p.pos - (p.normal or Vector3.yAxis) * (alt + 1), p.normal, alt, larg, true)
	-- inclina levemente para fora do centro (empurrado pela erupcao)
	local fora = Vector3.new(p.pos.X - centro.X, 0, p.pos.Z - centro.Z); fora = fora.Magnitude > 0.1 and fora.Unit or Vector3.xAxis
	local giro = CFrame.fromAxisAngle(fora:Cross(Vector3.yAxis).Unit, -math.rad(5 + math.random() * 8))
	local pecas = {}; for _, x in ipairs(pilar:GetChildren()) do pecas[x] = (CFrame.new(p.pos - (p.normal or Vector3.yAxis) * (alt + 1))):ToObjectSpace(x.CFrame) end
	local baixo = CFrame.new(p.pos - (p.normal or Vector3.yAxis) * (alt + 1)); local cima = CFrame.new(p.pos - Vector3.new(0, 1.2, 0)) * giro
	local t0 = os.clock(); local subir = 0.2
	local con; con = RunService.Heartbeat:Connect(function()
		local k = math.min((os.clock() - t0) / subir, 1); local e = 1 - (1 - k) ^ 3 * (1 - 1.6 * k * (1 - k))     -- sai rapido com leve sobressalto
		local base = baixo:Lerp(cima, math.clamp(e, 0, 1.08))
		for x, rel in pairs(pecas) do if x.Parent then x.CFrame = base * rel end end
		if k >= 1 then con:Disconnect() end
	end)
	-- explosao no pe do pilar: chamas, lava, brasas, fumaca e pedras
	local a = ancora(p.pos + Vector3.new(0, 1, 0)); Debris:AddItem(a, 4)
	emissor(a, flip({Color = BRANCO, LightEmission = 0.5, LightInfluence = 0, Size = ns(0, 4, 0.4, 11, 1, 14), Transparency = ns(0, 0, 1, 1), Lifetime = NumberRange.new(0.6, 1.0),
		Speed = NumberRange.new(18, 45), SpreadAngle = Vector2.new(30, 30), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, 10, 0), Drag = 2.5,
		Rotation = NumberRange.new(0, 360), Rate = 0}, FB.fogo)):Emit(math.floor(9 * f))
	emissor(a, flip({Color = BRANCO, LightEmission = 0.35, LightInfluence = 0.2, Size = ns(0, 1.6, 1, 0.9), Lifetime = NumberRange.new(1.0, 1.6), Speed = NumberRange.new(35, 60),
		SpreadAngle = Vector2.new(40, 40), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, -70, 0), Rotation = NumberRange.new(0, 360),
		RotSpeed = NumberRange.new(-200, 200), Rate = 0}, FB.lava)):Emit(math.floor(22 * f))
	emissor(a, {Texture = TEX.faisca, Color = seq({C3(255, 235, 160), C3(255, 110, 25)}), LightEmission = 1, Size = ns(0, 0.6, 1, 0), Lifetime = NumberRange.new(0.8, 1.6),
		Speed = NumberRange.new(30, 70), SpreadAngle = Vector2.new(50, 50), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, -45, 0), Rate = 0}):Emit(math.floor(30 * f))
	emissor(a, flip({Color = seq({C3(85, 70, 60), C3(45, 40, 38)}), LightInfluence = 1, Size = ns(0, 7, 1, 26), Transparency = ns(0, 0.35, 1, 1), Lifetime = NumberRange.new(1.8, 2.8),
		Speed = NumberRange.new(8, 20), SpreadAngle = Vector2.new(60, 60), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, 6, 0), Drag = 1.2,
		Rotation = NumberRange.new(0, 360), Rate = 0}, FB.fumaca)):Emit(math.floor(7 * f))
	for i = 1, math.floor(4 * f) do                                  -- pedras lancadas
		local r = peca({Size = Vector3.new(1, 0.8, 1.1) * (0.9 + math.random() * 1.6), Material = Enum.Material.Basalt, Color = C3(55, 45, 40),
			CFrame = CFrame.new(p.pos + Vector3.new(0, 2, 0)) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)}, math.random() < 0.5 and "WedgePart" or "Part")
		local alvo = p.pos + Vector3.new((math.random() - 0.5) * 22, 9 + math.random() * 12, (math.random() - 0.5) * 22)
		TweenService:Create(r, TweenInfo.new(0.35, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Position = alvo}):Play()
		task.delay(0.35, function() if r.Parent then TweenService:Create(r, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Position = Vector3.new(alvo.X, p.pos.Y, alvo.Z)}):Play() end end)
		Debris:AddItem(r, 2.0)
	end
	return pilar
end
local function ruptura(m, d, f)
	if d.fase == "preparo" then
		-- fissuras do corpo acendem; pedrinhas tremem junto as patas
		brilhoCorpo(m, 0.68, 1.2)                                     -- fissuras mais vivas, sem "pintar" o corpo todo
		local lista = {}; rupturas[m] = lista
		for _, nome in ipairs({"PernaDE_3", "PernaDD_3", "PernaTE_3", "PernaTD_3"}) do
			local b = osso(m, nome)
			if b then
				local pos = b.TransformedWorldCFrame.Position
				for i = 1, math.floor(3 * f + 0.5) do
					local r = peca({Size = Vector3.new(0.9, 0.7, 1) * (0.6 + math.random()), Material = Enum.Material.Basalt, Color = C3(60, 48, 42),
						CFrame = CFrame.new(pos + Vector3.new((math.random() - 0.5) * 9, -1, (math.random() - 0.5) * 9)) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)})
					table.insert(lista, r)
					task.spawn(function()
						local base = r.CFrame; local t0 = os.clock()
						while r.Parent and os.clock() - t0 < 1.4 do
							r.CFrame = base * CFrame.new((math.random() - 0.5) * 0.3, math.abs(math.sin((os.clock() - t0) * 30)) * 0.5 * (os.clock() - t0), (math.random() - 0.5) * 0.3)
							task.wait()
						end
					end)
					Debris:AddItem(r, 1.5)
				end
				local e = emissor(b, {Texture = TEX.faisca, Color = seq({C3(255, 220, 140), C3(255, 100, 20)}), LightEmission = 1, Size = ns(0, 0.5, 1, 0),
					Lifetime = NumberRange.new(0.5, 1.0), Speed = NumberRange.new(3, 9), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, 10, 0), Rate = 18 * f})
				Debris:AddItem(e, 1.4)
			end
		end
		local c = m:GetPivot().Position; local a = ancora(c); Debris:AddItem(a, 1.6); luz(a, C3(255, 120, 40), 1.2, 30, 1.5)
	elseif d.fase == "impacto" then
		local c = d.pos
		tremor(c, 0.55, 0.45)
		anel(c + Vector3.new(0, 0.6, 0), (d.raio or 22) * 1.6, C3(255, 150, 70), 0.45, 0.8, 0.35)
		task.delay(0.06, function() anel(c + Vector3.new(0, 0.4, 0), (d.raio or 22) * 2.2, C3(150, 120, 95), 0.7, 1.4, 0.55) end)
		local a = ancora(c + Vector3.new(0, 1, 0)); Debris:AddItem(a, 4)
		local base = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(1, 10, 10), Transparency = 1, CFrame = CFrame.new(c + Vector3.new(0, 1.5, 0)) * CFrame.Angles(0, 0, math.rad(90))})
		Debris:AddItem(base, 3.5)
		emissor(base, flip({Shape = Enum.ParticleEmitterShape.Cylinder, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface, ShapeInOut = Enum.ParticleEmitterShapeInOut.Outward,
			Color = seq({C3(140, 115, 90), C3(90, 75, 62)}), LightInfluence = 1, Size = ns(0, 5, 1, 20), Transparency = ns(0, 0.3, 1, 1), Lifetime = NumberRange.new(1.0, 1.8),
			Speed = NumberRange.new(40, 65), Drag = 2.2, Rotation = NumberRange.new(0, 360), Rate = 0}, FB.fumaca)):Emit(math.floor(40 * f))
		emissor(a, {Texture = TEX.faisca, Color = seq({C3(255, 235, 160), C3(255, 110, 25)}), LightEmission = 1, Size = ns(0, 0.7, 1, 0), Lifetime = NumberRange.new(0.8, 1.4),
			Speed = NumberRange.new(40, 80), SpreadAngle = Vector2.new(70, 70), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, -55, 0), Rate = 0}):Emit(math.floor(50 * f))
		luz(a, C3(255, 130, 50), 4, 55, 0.5)
		for i = 1, math.floor(8 * f) do                                   -- fragmentos lancados para fora
			local ang = math.random() * 6.28; local r = peca({Size = Vector3.new(1.2, 1, 1.4) * (0.8 + math.random() * 1.5), Material = Enum.Material.Basalt, Color = C3(58, 47, 42),
				CFrame = CFrame.new(c + Vector3.new(0, 1.5, 0)) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)}, "WedgePart")
			local alvo = c + Vector3.new(math.cos(ang), 0, math.sin(ang)) * (12 + math.random() * 16) + Vector3.new(0, 8 + math.random() * 8, 0)
			TweenService:Create(r, TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Position = alvo}):Play()
			task.delay(0.3, function() if r.Parent then TweenService:Create(r, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Position = Vector3.new(alvo.X, c.Y, alvo.Z), Transparency = 0.4}):Play() end end)
			Debris:AddItem(r, 2.2)
		end
	elseif d.fase == "erupcao" then
		local lista = rupturas[m] or {}; rupturas[m] = lista
		local c = d.centro
		for _, p in ipairs(d.pilares or {}) do
			-- fissura corre do impacto ate o pilar ANTES dele sair (sinal para esquiva), depois o pilar irrompe
			fissura(c, p.pos, 1.8, 0.6 + 0.3 * f)
			task.delay(0.25 + (p.anel - 1) * (d.intervalo or 0.16) - 0.02, function()
				local pilar = pilarErupcao(p, f, c); table.insert(lista, pilar)
			end)
		end
		-- explosao vulcanica central (sobe atras do impacto)
		task.delay(0.3, function()
			local a = ancora(c + Vector3.new(0, 3, 0)); Debris:AddItem(a, 5)
			emissor(a, flip({Color = BRANCO, LightEmission = 0.45, LightInfluence = 0, Size = ns(0, 6, 0.4, 15, 1, 19), Transparency = ns(0, 0, 1, 1), Lifetime = NumberRange.new(0.8, 1.2),
				Speed = NumberRange.new(20, 40), SpreadAngle = Vector2.new(25, 25), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, 18, 0), Drag = 2,
				Rotation = NumberRange.new(0, 360), Rate = 0}, FB.fogo)):Emit(math.floor(12 * f))
			emissor(a, flip({Color = seq({C3(75, 62, 55), C3(40, 36, 35)}), LightInfluence = 1, Size = ns(0, 10, 1, 40), Transparency = ns(0, 0.3, 1, 1), Lifetime = NumberRange.new(2.5, 3.5),
				Speed = NumberRange.new(14, 26), SpreadAngle = Vector2.new(25, 25), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, 5, 0), Drag = 0.8,
				Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-20, 20), Rate = 0}, FB.fumaca)):Emit(math.floor(12 * f))
			luz(a, C3(255, 120, 40), 3, 70, 1.2)
		end)
	elseif d.fase == "fim" then
		-- recuperacao: pilares afundam e se desfazem em poeira; brilho do corpo volta ao normal
		brilhoCorpo(m, 0.8, 1.0)
		local lista = rupturas[m]; rupturas[m] = nil
		for _, pilar in ipairs(lista or {}) do
			if pilar:IsA("Model") and pilar.Parent then
				local pv = pilar:GetPivot()
				local a = ancora(pv.Position); Debris:AddItem(a, 3)
				emissor(a, flip({Color = seq({C3(130, 110, 90), C3(85, 72, 62)}), LightInfluence = 1, Size = ns(0, 5, 1, 16), Transparency = ns(0, 0.45, 1, 1),
					Lifetime = NumberRange.new(1.0, 1.6), Speed = NumberRange.new(4, 12), SpreadAngle = Vector2.new(180, 40), Rate = 0, Rotation = NumberRange.new(0, 360)}, FB.fumaca)):Emit(math.floor(6 * f))
				for _, x in ipairs(pilar:GetChildren()) do
					if x:IsA("BasePart") then
						TweenService:Create(x, TweenInfo.new(0.9, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = x.CFrame - Vector3.new(0, 14, 0), Transparency = 0.6, Color = C3(45, 38, 35)}):Play()
					end
				end
				Debris:AddItem(pilar, 1.0)
			end
		end
	elseif d.fase == "lancamento" then                                  -- so o cliente dono do personagem atingido recebe
		local ch = Players.LocalPlayer and Players.LocalPlayer.Character
		local r = ch and ch:FindFirstChild("HumanoidRootPart"); local h = ch and ch:FindFirstChildOfClass("Humanoid")
		if r and h and typeof(d.vel) == "Vector3" and d.vel.Magnitude < 120 then
			h:ChangeState(Enum.HumanoidStateType.Jumping); r.AssemblyLinearVelocity = d.vel
		end
	end
end

-- ===== ossos com nomes do rig novo (CR_Dragao: nomes do Blender) ===============================================
local function ossoA(m, ...) for _, n in ipairs({...}) do local b = osso(m, n); if b then return b end end end
local function centroDe(m)                                           -- meio do tronco (mesma regra do servidor)
	local q = osso(m, "Quadril"); local c = ossoA(m, "Coluna3", "Coluna2")
	if not q then return m:GetPivot().Position end
	local a = q.TransformedWorldCFrame.Position
	return c and (a + c.TransformedWorldCFrame.Position) / 2 or a
end
local function bocaReal(m)                                           -- ponta do focinho (rig Mesh2Motion/CR) ou estimativa
	local f = osso(m, "mouth_upper_tip")
	if f then local _, dir = bocaDe(m); return f.TransformedWorldCFrame.Position, dir end
	return bocaDe(m)
end

-- ===== Coracao Infernal ==========================================================================================
-- Lamina de fogo VOLUMETRICA (nao e peca rigida): cadeia de ancoras ao longo da lamina, ligadas por Beams em camadas
-- (nucleo incandescente branco-amarelo, chama laranja com textura correndo, halo vermelho escuro), particulas de chama
-- e brasas em cada ancora (ficam para tras = rastro), Trails na ponta e no meio (risco do giro), luz no meio. A pose da
-- lamina vem da MESMA funcao de angulo do servidor (t0 do servidor), centrada no tronco que se move (no ar o voo segue).
local coracoes = {}                                                  -- [modelo] = {hl, luz, pecas...}
local function coracaoEstado(d, t)
	if t < 0 then return 0, 0, false end
	if t <= d.expele then local k = t / d.expele; return 0, 1 - (1 - k) ^ 3, true end
	local k = math.clamp((t - d.expele) / d.giro, 0, 1)
	return d.sentido * 2 * math.pi * d.voltas * (k * k * (3 - 2 * k)), 1, t <= d.expele + d.giro
end
local function brilhoCarga(m, dur, f)
	local s = coracoes[m] or {}; coracoes[m] = s
	if s.hl then s.hl:Destroy() end
	local hl = Instance.new("Highlight"); hl.FillColor = C3(255, 105, 25); hl.OutlineColor = C3(255, 170, 60); hl.FillTransparency = 1; hl.OutlineTransparency = 1
	hl.DepthMode = Enum.HighlightDepthMode.Occluded; hl.Adornee = m; hl.Parent = m; s.hl = hl
	TweenService:Create(hl, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {FillTransparency = 0.62, OutlineTransparency = 0.55}):Play()
	-- energia convergindo para o peito e a garganta (brasas puxadas para dentro), calor crescendo
	for _, b in ipairs({ossoA(m, "Coluna2", "spine_0"), ossoA(m, "Pescoco4", "Pescoco2")}) do
		local e = emissor(b, {Shape = Enum.ParticleEmitterShape.Sphere, ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward, Texture = TEX.faisca,
			Color = seq({C3(255, 240, 170), C3(255, 120, 30)}), LightEmission = 1, Size = ns(0, 0.9, 1, 0), Lifetime = NumberRange.new(0.35, 0.6),
			Speed = NumberRange.new(14, 24), Rate = 60 * f}); Debris:AddItem(e, dur)
		local e2 = emissor(b, flip({Color = BRANCO, LightEmission = 0.6, LightInfluence = 0, Size = ns(0, 3, 1, 0.5), Transparency = ns(0, 0.6, 1, 1),
			Lifetime = NumberRange.new(0.3, 0.5), Speed = NumberRange.new(0, 3), SpreadAngle = Vector2.new(180, 180), Rate = 18 * f}, FB.fogo)); Debris:AddItem(e2, dur)
	end
	local peito = ossoA(m, "Coluna2", "spine_0")
	if peito then
		local l = luz(peito, C3(255, 120, 40), 0.4, 18); s.luz = l
		if l then TweenService:Create(l, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Brightness = 2.2, Range = 26}):Play() end
	end
end
local function fimCarga(m, dur)
	local s = coracoes[m]; if not s then return end
	if s.hl then local hl = s.hl; TweenService:Create(hl, TweenInfo.new(dur), {FillTransparency = 1, OutlineTransparency = 1}):Play(); Debris:AddItem(hl, dur + 0.05); s.hl = nil end
	if s.luz then local l = s.luz; s.luz = nil; TweenService:Create(l, TweenInfo.new(dur), {Brightness = 0}):Play(); task.delay(dur, function() liberarLuz(l) end) end
end
local NA = 9                                                          -- ancoras ao longo da lamina
local function larguraEm(u)                                           -- perfil de espada: base estreita, largura maxima ~25%, ponta fina
	if u < 0.22 then return 0.45 + 0.55 * (u / 0.22) end
	return ((1 - u) / 0.78) ^ 0.85
end
local function lamina(m, d, f)
	local s = coracoes[m] or {}; coracoes[m] = s
	local pasta = pastaFX()
	local anc = {}
	for i = 1, NA do local a = Instance.new("Attachment"); a.Parent = workspace.Terrain; anc[i] = a end
	local wMax = (d.largura or 6) * 2.6                                -- espada larga e legivel de longe
	local camadas = {
		{cor = seq({C3(255, 255, 235), C3(255, 236, 150)}), transp = 0.02, larg = 0.42, luz = 1, tex = nil},                 -- nucleo incandescente
		{cor = seq({C3(255, 200, 80), C3(255, 120, 25)}), transp = 0.12, larg = 0.85, luz = 0.9, tex = TEX.fogo, vel = 3.2},   -- chama
		{cor = seq({C3(240, 80, 20), C3(120, 25, 10)}), transp = 0.62, larg = 1.35, luz = 0.55, tex = TEX.fogo, vel = -2.2},   -- halo/turbulencia
	}
	local beams = {}
	for _, c in ipairs(camadas) do
		for i = 1, NA - 1 do
			local b = Instance.new("Beam"); b.Attachment0 = anc[i]; b.Attachment1 = anc[i + 1]; b.FaceCamera = true; b.Segments = 4
			b.Color = c.cor; b.LightEmission = c.luz; b.LightInfluence = 0; b.Transparency = NumberSequence.new(c.transp)
			if c.tex then b.Texture = c.tex; b.TextureMode = Enum.TextureMode.Stretch; b.TextureLength = 1; b.TextureSpeed = c.vel end
			b.Width0, b.Width1 = 0, 0; b.Parent = anc[i]
			table.insert(beams, {b = b, c = c, i = i})
		end
	end
	-- particulas: chamas e brasas soltas pela lamina em movimento ficam para tras (rastro); fumaca leve no halo
	local emis = {}
	for i = 2, NA do
		local u = (i - 1) / (NA - 1)
		table.insert(emis, emissor(anc[i], flip({Color = BRANCO, LightEmission = 0.55, LightInfluence = 0, Size = ns(0, 3.5 * larguraEm(u) + 1, 0.5, 6 * larguraEm(u) + 2, 1, 1),
			Transparency = ns(0, 0.1, 0.8, 0.5, 1, 1), Lifetime = NumberRange.new(0.3, 0.5), Speed = NumberRange.new(1, 5), SpreadAngle = Vector2.new(180, 180),
			Acceleration = Vector3.new(0, 10, 0), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-60, 60), Rate = 32 * f}, FB.fogo)))
		if i % 2 == 0 then
			table.insert(emis, emissor(anc[i], {Texture = TEX.faisca, Color = seq({C3(255, 235, 160), C3(255, 110, 25)}), LightEmission = 1, Size = ns(0, 0.6, 1, 0),
				Lifetime = NumberRange.new(0.6, 1.2), Speed = NumberRange.new(4, 14), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, -22, 0), Drag = 1.2, Rate = 22 * f}))
			table.insert(emis, emissor(anc[i], flip({Color = seq({C3(80, 62, 52), C3(40, 34, 32)}), LightInfluence = 1, Size = ns(0, 3, 1, 10), Transparency = ns(0, 0.6, 1, 1),
				Lifetime = NumberRange.new(0.8, 1.3), Speed = NumberRange.new(2, 6), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, 8, 0), Rate = 5 * f}, FB.fumaca)))
		end
	end
	-- riscos do giro: trails horizontais na ponta e no meio (pares de ancoras acima/abaixo do plano)
	local rastros = {}
	for _, iu in ipairs({NA, math.floor(NA * 0.55)}) do
		local a0 = Instance.new("Attachment"); a0.Parent = workspace.Terrain
		local a1 = Instance.new("Attachment"); a1.Parent = workspace.Terrain
		local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = 0.32; tr.LightEmission = 1; tr.LightInfluence = 0
		tr.Color = seq({C3(255, 220, 120), C3(255, 90, 20), C3(110, 20, 8)}); tr.Transparency = ns(0, 0.15, 0.6, 0.55, 1, 1); tr.FaceCamera = true
		tr.WidthScale = ns(0, 1, 1, 0.2); tr.Texture = TEX.fogo; tr.TextureMode = Enum.TextureMode.Stretch; tr.Parent = a0
		table.insert(rastros, {a0 = a0, a1 = a1, i = iu, tr = tr})
	end
	local luzMeio = luz(anc[math.floor(NA * 0.5)], C3(255, 130, 40), 2.2, 28)       -- luz contida (sem "disco" no chao)
	-- clarao na boca no instante em que a lamina sai
	local b0 = bocaReal(m); rajada(b0, "Fogo", 0.32, f)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {m, pasta}
	local ultChao, fimTotal = 0, d.expele + d.giro + d.dissipa
	local con
	con = RunService.RenderStepped:Connect(function()
		local t = workspace:GetServerTimeNow() - d.t0
		if not m.Parent or t > fimTotal + 0.05 then
			con:Disconnect()
			for _, e in ipairs(emis) do e.Enabled = false end
			for _, r in ipairs(rastros) do r.tr.Enabled = false end
			task.delay(1.4, function()
				for _, a in ipairs(anc) do a:Destroy() end
				for _, r in ipairs(rastros) do r.a0:Destroy(); r.a1:Destroy() end
			end)
			liberarLuz(luzMeio)
			return
		end
		local ang, ext = coracaoEstado(d, math.min(t, d.expele + d.giro))
		local fade = t > d.expele + d.giro and 1 - (t - d.expele - d.giro) / d.dissipa or 1   -- dissipacao
		local c = centroDe(m); local yL = c.Y + d.dy
		local dir = CFrame.Angles(0, ang, 0):VectorToWorldSpace(d.dir0)
		local base = Vector3.new(c.X, yL, c.Z) + dir * d.rIn
		if t < d.expele then base = bocaReal(m) end                       -- nasce na boca
		local ponta = Vector3.new(c.X, yL, c.Z) + dir * (d.rIn + (d.rOut - d.rIn) * ext)
		-- leve ondulacao vertical (turbulencia) e curvatura para tras do giro (a lamina "arrasta" a ponta)
		local lado = Vector3.new(0, 1, 0):Cross(dir) * -d.sentido
		for i = 1, NA do
			local u = (i - 1) / (NA - 1)
			local p = base:Lerp(ponta, u) + lado * (u * u * 4 * (t > d.expele and 1 or 0)) + Vector3.new(0, math.sin(t * 13 + i * 0.9) * 0.6 * u, 0)
			anc[i].WorldPosition = p
		end
		for _, x in ipairs(beams) do
			local u0, u1 = (x.i - 1) / (NA - 1), x.i / (NA - 1)
			local w = wMax * x.c.larg * fade * (0.92 + 0.08 * math.sin(t * 20 + x.i))
			x.b.Width0 = w * larguraEm(u0); x.b.Width1 = w * larguraEm(u1)
			if fade < 1 then x.b.Transparency = NumberSequence.new(1 - (1 - x.c.transp) * fade) end
		end
		for _, r in ipairs(rastros) do
			local p = anc[r.i].WorldPosition
			r.a0.WorldPosition = p + Vector3.new(0, 1.6 * fade, 0); r.a1.WorldPosition = p - Vector3.new(0, 1.6 * fade, 0)
		end
		if fade < 1 then for _, e in ipairs(emis) do e.Enabled = fade > 0.5 end end
		-- rastro de chamas no chao sob a ponta (so com superficie perto; no ar alto nao aparece nada no chao)
		if f > 0 and t > d.expele and t < d.expele + d.giro and os.clock() - ultChao > 0.07 then
			ultChao = os.clock()
			local h = workspace:Raycast(ponta * Vector3.new(1, 0, 1) + Vector3.new(0, yL + 2, 0), Vector3.new(0, -32, 0), rp)
			if h then
				local a = ancora(h.Position); Debris:AddItem(a, 2.2)
				emissor(a, flip({Color = BRANCO, LightEmission = 0.5, LightInfluence = 0, Size = ns(0, 2.5, 0.4, 6, 1, 3), Transparency = ns(0, 0.15, 1, 1),
					Lifetime = NumberRange.new(0.7, 1.3), Speed = NumberRange.new(2, 6), SpreadAngle = Vector2.new(25, 25), EmissionDirection = Enum.NormalId.Top,
					Acceleration = Vector3.new(0, 6, 0), Rotation = NumberRange.new(0, 360), Rate = 0}, FB.fogo)):Emit(math.floor(5 * f) + 1)
				emissor(a, {Texture = TEX.faisca, Color = seq({C3(255, 220, 140), C3(255, 90, 20)}), LightEmission = 1, Size = ns(0, 0.5, 1, 0),
					Lifetime = NumberRange.new(0.6, 1.2), Speed = NumberRange.new(6, 16), SpreadAngle = Vector2.new(60, 60), EmissionDirection = Enum.NormalId.Top,
					Acceleration = Vector3.new(0, -30, 0), Rate = 0}):Emit(math.floor(6 * f) + 1)
			end
		end
	end)
end
local function coracao(m, d, f)
	if d.fase == "carga" then brilhoCarga(m, d.carga or 1.1, math.max(f, 0.3))
	elseif d.fase == "lamina" then lamina(m, d, math.max(f, 0.3)); task.delay(d.expele + d.giro, function() fimCarga(m, d.dissipa + 0.4) end)
	elseif d.fase == "impacto" and f > 0 then rajada(d.pos, "Fogo", 0.7, f) end
end

-- ===== passivas: Burning (alvos) e Sangue de Magma (dragao) ======================================================
-- Indicadores DISCRETOS guiados por atributos do servidor: Queimando (fim, tempo do servidor) e SangueMagmaFim.
local queimando, sangue = {}, {}
local function raizDe(m) return m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart end
local function ligarQueima(m)
	local r = raizDe(m); if not r then return end
	local grande = m:GetAttribute("FormaRegional") ~= nil
	local k = grande and 3 or 1
	local a = Instance.new("Attachment"); a.Name = "VFX_Queimando"; a.Parent = r
	if grande then local q = osso(m, "Quadril"); if q then a.Parent = q end end
	local e = {
		emissor(a, flip({Color = BRANCO, LightEmission = 0.45, LightInfluence = 0, Size = ns(0, 1.2 * k, 0.5, 2.6 * k, 1, 0.6 * k), Transparency = ns(0, 0.25, 1, 1),
			Lifetime = NumberRange.new(0.45, 0.8), Speed = NumberRange.new(2, 5), SpreadAngle = Vector2.new(40, 40), EmissionDirection = Enum.NormalId.Top,
			Shape = Enum.ParticleEmitterShape.Box, Acceleration = Vector3.new(0, 6, 0), Rotation = NumberRange.new(0, 360), Rate = 9 * k}, FB.fogo)),
		emissor(a, {Texture = TEX.faisca, Color = seq({C3(255, 220, 140), C3(255, 90, 20)}), LightEmission = 1, Size = ns(0, 0.35 * k, 1, 0),
			Lifetime = NumberRange.new(0.7, 1.3), Speed = NumberRange.new(3, 8), SpreadAngle = Vector2.new(50, 50), EmissionDirection = Enum.NormalId.Top, Rate = 6 * k}),
		emissor(a, flip({Color = seq({C3(70, 60, 55), C3(40, 36, 34)}), LightInfluence = 1, Size = ns(0, 1.5 * k, 1, 5 * k), Transparency = ns(0, 0.6, 1, 1),
			Lifetime = NumberRange.new(1, 1.6), Speed = NumberRange.new(2, 5), EmissionDirection = Enum.NormalId.Top, Acceleration = Vector3.new(0, 4, 0), Rate = 3 * k}, FB.fumaca)),
	}
	local l = Instance.new("PointLight"); l.Color = C3(255, 120, 40); l.Brightness = 0.8; l.Range = 8 * k; l.Shadows = false; l.Parent = a
	queimando[m] = a
end
local function desligarQueima(m)
	local a = queimando[m]; queimando[m] = nil
	if a then for _, e in ipairs(a:GetChildren()) do if e:IsA("ParticleEmitter") then e.Enabled = false end end; Debris:AddItem(a, 1.4) end
end
local function ligarSangue(m)
	local hl = Instance.new("Highlight"); hl.FillColor = C3(255, 90, 20); hl.OutlineColor = C3(255, 150, 50); hl.FillTransparency = 0.86; hl.OutlineTransparency = 0.7
	hl.DepthMode = Enum.HighlightDepthMode.Occluded; hl.Adornee = m; hl.Parent = m
	local b = ossoA(m, "Coluna2", "spine_0") or raizDe(m)
	local e = b and emissor(b, {Texture = TEX.faisca, Color = seq({C3(255, 220, 140), C3(255, 80, 20)}), LightEmission = 1, Size = ns(0, 0.6, 1, 0),
		Lifetime = NumberRange.new(0.8, 1.4), Speed = NumberRange.new(4, 9), SpreadAngle = Vector2.new(70, 70), EmissionDirection = Enum.NormalId.Top,
		Shape = Enum.ParticleEmitterShape.Sphere, Rate = 10})
	local l = b and Instance.new("PointLight"); if l then l.Color = C3(255, 110, 40); l.Brightness = 1.2; l.Range = 22; l.Shadows = false; l.Parent = b end
	sangue[m] = {hl = hl, e = e, l = l}
end
local function desligarSangue(m)
	local s = sangue[m]; sangue[m] = nil; if not s then return end
	TweenService:Create(s.hl, TweenInfo.new(0.6), {FillTransparency = 1, OutlineTransparency = 1}):Play(); Debris:AddItem(s.hl, 0.7)
	if s.e then s.e.Enabled = false; Debris:AddItem(s.e, 1.5) end
	if s.l then Debris:AddItem(s.l, 0.1) end
end
task.spawn(function()
	while true do
		task.wait(0.25)
		local agora = workspace:GetServerTimeNow()
		local vistos = {}
		for _, m in ipairs(workspace:GetChildren()) do
			if m:IsA("Model") then
				vistos[m] = true
				local q = m:GetAttribute("Queimando")
				if q and q > agora and fatorLOD(m:GetPivot().Position) > 0 then if not queimando[m] then ligarQueima(m) end
				elseif queimando[m] then desligarQueima(m) end
				local sm = m:GetAttribute("SangueMagmaFim")
				if sm and sm > agora then if not sangue[m] then ligarSangue(m) end
				elseif sangue[m] then desligarSangue(m) end
			end
		end
		for m in pairs(queimando) do if not vistos[m] then desligarQueima(m) end end
		for m in pairs(sangue) do if not vistos[m] then desligarSangue(m) end end
	end
end)
local function lancamento(d)                                          -- reacao curta do proprio personagem (empurrao)
	local ch = Players.LocalPlayer and Players.LocalPlayer.Character
	local r = ch and ch:FindFirstChild("HumanoidRootPart"); local h = ch and ch:FindFirstChildOfClass("Humanoid")
	if r and h and typeof(d.vel) == "Vector3" and d.vel.Magnitude < 120 then
		h:ChangeState(Enum.HumanoidStateType.Jumping); r.AssemblyLinearVelocity = d.vel
	end
end
-- fragmentos de rocha arrancados da SUPERFICIE real sob a onda (nunca no ar sem chao)
local function fragmentosSolo(centro, raio, f, escala)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {workspace.Terrain, workspace:FindFirstChild("Baseplate")}
	for i = 1, math.floor(9 * f * escala) do
		local ang = math.random() * math.pi * 2; local r = raio * (0.2 + math.random() * 0.45)
		local x = centro + Vector3.new(math.cos(ang) * r, 0, math.sin(ang) * r)
		local h = workspace:Raycast(x + Vector3.new(0, 20, 0), Vector3.new(0, -50, 0), rp)
		if h then
			local p = peca({Size = Vector3.new(1.2, 0.9, 1.4) * (1 + math.random() * 1.6), Material = Enum.Material.Basalt, Color = C3(62, 52, 46),
				CFrame = CFrame.new(h.Position) * CFrame.Angles(math.random() * 6, math.random() * 6, 0)}, math.random() < 0.5 and "WedgePart" or "Part")
			local fora = Vector3.new(math.cos(ang), 0, math.sin(ang))
			local topo = h.Position + fora * (8 + math.random() * 10) * escala + Vector3.new(0, 6 + math.random() * 8 * escala, 0)
			local cai = Vector3.new(topo.X, h.Position.Y, topo.Z) + fora * 6
			TweenService:Create(p, TweenInfo.new(0.32, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Position = topo}):Play()
			task.delay(0.32, function() if p.Parent then TweenService:Create(p, TweenInfo.new(0.45, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Position = cai, Transparency = 0.35}):Play() end end)
			Debris:AddItem(p, 1.9)
		end
	end
end

-- ===== despacho ==================================================================================================
local trilhasArr = {}
function M.evento(d)
	local m = d.d; if not m or not m.Parent then return end
	local f = fatorLOD(m:GetPivot().Position); local el = d.el or "Fogo"; local P = PERFIL[el]
	if d.fase == "reacao" then reacao(d.alvo, el, d.intensidade); return end
	if d.fase == "lancamento" then lancamento(d); return end              -- empurrao (Tempestade/Ruptura): so o personagem atingido
	if f <= 0 then return end
	if d.hab == "Ruptura" then ruptura(m, d, f); return end
	if d.hab == "Coracao" then coracao(m, d, f); return end
	if d.hab == "SangueDeMagma" and d.fase == "ativar" then                -- reforco ativado: pulso de calor no peito (discreto)
		local b = ossoA(m, "Coluna2", "spine_0"); local pos = b and b.TransformedWorldCFrame.Position or m:GetPivot().Position
		rajada(pos, "Fogo", 0.35, f); return
	end
	if d.hab == "Sopro" then
		if d.fase == "preparo" then                                    -- acumulo perto da boca (sem dano)
			local b = bocaDe(m); local a = ancora(b); Debris:AddItem(a, 1.2)
			emissor(a, {Texture = el == "Ar" and TEX.fumaca or TEX.faisca, Color = seq(P.nucleo), LightEmission = el == "Terra" and 0.2 or 1,
				Size = ns(0, el == "Ar" and 3 or 0.8, 1, 0), Transparency = ns(0, el == "Ar" and 0.75 or 0, 1, 1), Lifetime = NumberRange.new(0.3, 0.6),
				Speed = NumberRange.new(-12, -6), SpreadAngle = Vector2.new(180, 180), Rate = 70 * f})
			luz(a, P.luz, 1.5, 20, 1.1)
			if el == "Raio" then for i = 1, 2 do task.delay(i * 0.35, function() local b2 = bocaDe(m); M.descarga(b2, b2 + Vector3.new(math.random(-6, 6), math.random(-3, 3), math.random(-6, 6)), "Raio", 0.12, 0.5) end) end end
		elseif d.fase == "mira" then                                         -- sopro segurado: nova direcao validada pelo servidor
			miraSopro[m] = d.alvoPos; local s = emissoresSopro(m, el); s.alvo = d.alvoPos
		elseif d.fase == "emissao" then
			miraSopro[m] = d.alvoPos; soproAtivo[m] = (soproAtivo[m] or 0) + 1
			if d.forma ~= "projetil" then ligarSopro(m, el, true, f, d.alvoPos, d.alcance) end
			if el == "Fogo" then brilhoCorpo(m, 0.6, 0.4) end                -- fissuras vulcanicas acendem durante o sopro
			if el == "Fogo" or el == "Ar" then                              -- impacto continuo onde o jato toca o mundo
				task.spawn(function()
					local tok = soproAtivo[m]; local lim = os.clock() + 8
					local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {m, pastaFX()}
					while soproAtivo[m] == tok and os.clock() < lim and m.Parent do
						local b, dr = bocaDe(m); local ap = miraSopro[m] or d.alvoPos; if ap then dr = (ap - b).Unit end
						local h = workspace:Raycast(b, dr * (d.alcance or 90), rp)
						if h then
							if el == "Fogo" then rajada(h.Position, "Fogo", 0.45, f) else rajada(h.Position, "Ar", 0.55, f) end
						end
						task.wait(el == "Fogo" and 0.28 or 0.35)
					end
				end)
			end
			if el == "Raio" then                                       -- arco continuo (forma muda, brilho constante: sem estroboscopia)
				task.spawn(function()
					local fim = os.clock() + (d.duracao or 1.8)
					while os.clock() < fim and m.Parent do
						local b, dr = bocaDe(m)
						local alvo = d.alvoPos or (b + dr * (d.alcance or 90))
						M.descarga(b, alvo, "Raio", 0.14, 1.6)
						task.wait(0.09)
					end
				end)
			end
			if el == "Ar" then                                       -- aneis de pressao viajando na direcao da rajada + poeira no destino
				local alc = d.alcance or 60
				for i = 0, 8 do task.delay(i * 0.2, function()                   -- aneis de pressao viajam ate o fim do alcance
					local b, dr = bocaDe(m); if d.alvoPos then dr = (d.alvoPos - b).Unit end
					local r = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.6, 9, 9), Material = Enum.Material.Neon, Color = C3(235, 245, 255), Transparency = 0.5, CFrame = CFrame.lookAt(b, b + dr) * CFrame.Angles(0, math.rad(90), 0)})
					TweenService:Create(r, TweenInfo.new(0.75, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = r.CFrame + dr * alc, Size = Vector3.new(0.3, 44, 44), Transparency = 1}):Play(); Debris:AddItem(r, 0.8)
				end) end
				if d.alvoPos then task.delay(0.6, function() rajada(d.alvoPos, "Ar", 0.9, f) end) end
			end
		elseif d.fase == "pulso" then M.descarga(d.de, d.ate, "Raio", 0.22, 2.6); luz(ancora(d.ate), P.luz, 4, 45, 0.15); rajada(d.ate, "Raio", 0.6, f)
		elseif d.fase == "projetil" then projetil(d.de, d.ate, d.tempo, f)
		elseif d.fase == "impacto" then rajada(d.pos, el, 0.8, f)
		elseif d.fase == "fim" then soproAtivo[m] = (soproAtivo[m] or 0) + 1; miraSopro[m] = nil; ligarSopro(m, el, false, f); if el == "Fogo" then brilhoCorpo(m, 0.8, 0.9) end end
	elseif d.hab == "Arremetida" then
		if d.fase == "emissao" then
			local a0, a1 = ossoA(m, "AsaE_1", "wing_1_l"), ossoA(m, "AsaD_1", "wing_1_r")
			if a0 and a1 then
				local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = 0.45; tr.LightEmission = el == "Terra" and 0.1 or 0.8
				tr.Color = seq({P.nucleo[1], P.nucleo[3]}); tr.Transparency = ns(0, 0.25, 1, 1); tr.FaceCamera = false; tr.Parent = m.PrimaryPart
				trilhasArr[m] = tr; Debris:AddItem(tr, (d.duracao or 0.7) + 0.6)
			end
			-- chamas envolvendo PARTE do corpo (peito, pescoco, quadril) durante a investida; somem na recuperacao
			for _, b in ipairs({osso(m, "Coluna2"), ossoA(m, "Pescoco4", "Pescoco2"), osso(m, "Quadril")}) do
				local e = emissor(b, el == "Fogo" and flip({Color = BRANCO, LightEmission = 0.5, LightInfluence = 0, Size = ns(0, 3, 0.5, 8, 1, 2), Transparency = ns(0, 0.2, 1, 1),
					Lifetime = NumberRange.new(0.25, 0.45), Speed = NumberRange.new(4, 12), SpreadAngle = Vector2.new(180, 180), Rotation = NumberRange.new(0, 360), Rate = 45 * f}, FB.fogo)
					or {Texture = el == "Raio" and TEX.faisca or TEX.fumaca, Color = seq(P.nucleo), LightEmission = el == "Raio" and 1 or 0, Size = ns(0, 4, 1, 12),
					Transparency = ns(0, el == "Ar" and 0.75 or 0.3, 1, 1), Lifetime = NumberRange.new(0.4, 0.8), Speed = NumberRange.new(5, 15), SpreadAngle = Vector2.new(180, 180), Rate = 90 * f})
				Debris:AddItem(e, d.duracao or 0.7)
			end
			if el == "Fogo" then local pp = m.PrimaryPart; if pp then luz(pp, P.luz, 3, 40, (d.duracao or 0.7) + 0.3) end end
		elseif d.fase == "impacto" then rajada(d.pos, el, 1.0, f)
		elseif d.fase == "fim" then local tr = trilhasArr[m]; if tr and tr.Parent then tr.Enabled = false end end
	elseif d.hab == "Tempestade" then
		if d.fase == "preparo" then                                        -- ar comeca a ser puxado para as asas
			local c = m:GetPivot().Position; local a = ancora(c + Vector3.new(0, 2, 0)); Debris:AddItem(a, 2)
			local e = emissor(a, flip({Shape = Enum.ParticleEmitterShape.Sphere, ShapeInOut = Enum.ParticleEmitterShapeInOut.Inward, Color = seq({C3(150, 130, 110), C3(110, 98, 86)}),
				LightInfluence = 1, Size = ns(0, 4, 1, 9), Transparency = ns(0, 0.6, 1, 1), Lifetime = NumberRange.new(0.6, 0.9), Speed = NumberRange.new(20, 30),
				Rotation = NumberRange.new(0, 360), Rate = 30 * f}, FB.fumaca)); Debris:AddItem(e, 1.1)
		elseif d.fase == "impulso" then                                    -- patas deixam o chao: poeira e detritos, rastros nas pontas das asas
			rajada(d.pos, "Terra", 0.7, f); anel(d.pos + Vector3.new(0, 1, 0), 40, C3(160, 140, 120), 0.6, 1.2, 0.5)
			for _, lado in ipairs({{"Dedo2E", "Dedo1E", "wing_tip_l", "wing_3_l"}, {"Dedo2D", "Dedo1D", "wing_tip_r", "wing_3_r"}}) do
				local b = ossoA(m, lado[1], lado[3]); local b2 = ossoA(m, lado[2], lado[4])
				if b and b2 then
					local tr = Instance.new("Trail"); tr.Attachment0 = b; tr.Attachment1 = b2; tr.Lifetime = 0.35; tr.LightEmission = el == "Fogo" and 0.7 or 0.1
					tr.Color = seq({PERFIL[el].nucleo[2], PERFIL[el].nucleo[4]}); tr.Transparency = ns(0, 0.45, 1, 1); tr.Parent = m.PrimaryPart; Debris:AddItem(tr, 1.9)
				end
			end
		elseif d.fase == "pouso" then
			rajada(d.pos, "Terra", 0.6, f); tremor(d.pos, 0.3, 0.3)
		elseif d.fase == "batida" and d.superficie == false then
			-- no alto, sem superficie perto: so a onda de vento quente em volta do corpo (nada de rocha/poeira no ar)
			local c = m:GetPivot().Position + Vector3.new(0, 14, 0)
			anel(c, (d.raio or 70) * 0.8, P.cor, 0.6, 0.8, 0.6)
			local a = ancora(c); Debris:AddItem(a, 2)
			emissor(a, flip({Shape = Enum.ParticleEmitterShape.Disc, Color = BRANCO, LightEmission = 0.4, LightInfluence = 0, Size = ns(0, 4, 1, 12), Transparency = ns(0, 0.45, 1, 1),
				Lifetime = NumberRange.new(0.4, 0.6), Speed = NumberRange.new(50, 80), Rotation = NumberRange.new(0, 360), Rate = 0}, FB.fogo)):Emit(math.floor(24 * f))
			return
		elseif d.fase == "batida" then
			if (d.indice or 1) > 1 then f *= 0.6 end                       -- batidas seguintes: ondas menores
			tremor(d.pos, 0.5, 0.4)
			if d.superficie then fragmentosSolo(d.pos, d.raio or 70, f, (d.indice or 1) == 1 and 1 or 0.6) end
			-- massa de ar descendo das asas ate o chao (coluna) antes da onda radial
			local topo = d.pos + Vector3.new(0, (d.altura or 0) + 20, 0)
			local col = ancora(topo); Debris:AddItem(col, 2.5)
			emissor(col, flip({Shape = Enum.ParticleEmitterShape.Disc, Color = seq(P.nucleo), LightEmission = el == "Fogo" and 0.45 or 0, LightInfluence = el == "Fogo" and 0 or 1,
				Size = ns(0, 6, 1, 18), Transparency = ns(0, el == "Ar" and 0.55 or 0.25, 1, 1), Lifetime = NumberRange.new(0.35, 0.5), Speed = NumberRange.new(70, 95),
				EmissionDirection = Enum.NormalId.Bottom, Rotation = NumberRange.new(0, 360), Rate = 0}, el == "Fogo" and FB.fogo or FB.fumaca)):Emit(math.floor(30 * f))
			anel(d.pos + Vector3.new(0, 1.5, 0), d.raio or 70, P.cor, 0.7, 0.8, 0.62)          -- um anel so e translucido (nao um disco chapado)
			if el == "Fogo" then                                         -- rajadas de calor: explosoes em volta, brasas varridas para fora
				for i = 1, math.floor(8 * f) do
					local ang = i / 8 * math.pi * 2 + math.random() * 0.4; local r = (d.raio or 70) * (0.35 + math.random() * 0.45)
					task.delay(0.1 + r / 260, function() rajada(d.pos + Vector3.new(math.cos(ang) * r, 1, math.sin(ang) * r), "Fogo", 0.55, f) end)
				end
			elseif el == "Terra" then
				for i = 1, math.floor(6 * f) do
					local ang = math.random() * math.pi * 2; local r = (d.raio or 70) * (0.3 + math.random() * 0.5)
					task.delay(0.1 + r / 260, function() rajada(d.pos + Vector3.new(math.cos(ang) * r, 1, math.sin(ang) * r), "Terra", 0.6, f) end)
				end
			else                                                          -- Ar: vortices em volta e correntes de pressao horizontais
				for i = 1, math.floor(6 * f) do
					local ang = i / 6 * math.pi * 2; local r = (d.raio or 70) * 0.55
					local v = ancora(d.pos + Vector3.new(math.cos(ang) * r, 4, math.sin(ang) * r)); Debris:AddItem(v, 2.5)
					emissor(v, flip({Color = seq(P.nucleo), Size = ns(0, 4, 1, 14), Transparency = ns(0, 0.55, 1, 1), Lifetime = NumberRange.new(0.8, 1.2), Speed = NumberRange.new(10, 18),
						SpreadAngle = Vector2.new(15, 15), EmissionDirection = Enum.NormalId.Top, Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(300, 480), Rate = 0}, FB.fumaca)):Emit(12)
				end
				for i = 0, 4 do task.delay(i * 0.06, function()
					local ang = math.random() * math.pi * 2; local dir = Vector3.new(math.cos(ang), 0, math.sin(ang))
					local r = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(0.5, 14, 14), Material = Enum.Material.Neon, Color = C3(235, 245, 255), Transparency = 0.5,
						CFrame = CFrame.lookAt(d.pos + Vector3.new(0, 6, 0), d.pos + Vector3.new(0, 6, 0) + dir) * CFrame.Angles(0, math.rad(90), 0)})
					TweenService:Create(r, TweenInfo.new(0.8, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = r.CFrame + dir * (d.raio or 70), Size = Vector3.new(0.3, 34, 34), Transparency = 1}):Play(); Debris:AddItem(r, 0.85)
				end) end
			end
		end
		if d.fase == "batida" then                                          -- lencol de particulas varrendo para fora + rajadas das pontas das asas
			local c = d.pos; local raio = d.raio or 70
			anel(c + Vector3.new(0, 2, 0), raio, P.cor, 0.7, 1.5, el == "Ar" and 0.6 or 0.35)
			-- emissor em anel (peca invisivel com forma de cilindro) jogando particulas para fora
			local base = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(2, raio * 0.6, raio * 0.6), Transparency = 1, CFrame = CFrame.new(c + Vector3.new(0, 3, 0)) * CFrame.Angles(0, 0, math.rad(90))})
			Debris:AddItem(base, 2.5)
			emissor(base, {Shape = Enum.ParticleEmitterShape.Cylinder, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface, ShapeInOut = Enum.ParticleEmitterShapeInOut.Outward,
				Texture = el == "Fogo" and TEX.fogo or el == "Raio" and TEX.faisca or TEX.fumaca, Color = seq(P.nucleo), LightEmission = (el == "Fogo" or el == "Raio") and 1 or 0,
				Size = ns(0, el == "Raio" and 1.5 or 5, 1, el == "Raio" and 0 or 16), Transparency = ns(0, el == "Ar" and 0.7 or 0.25, 1, 1),
				Lifetime = NumberRange.new(0.6, 1.1), Speed = NumberRange.new(45, 80), Rate = 0, Drag = 1.5, RotSpeed = NumberRange.new(-200, 200)}):Emit(math.floor(90 * f))
			if el == "Raio" then for i = 1, 3 do local ang = math.random() * 6.28; M.descarga(c + Vector3.new(0, 30, 0), c + Vector3.new(math.cos(ang) * raio * 0.7, 1, math.sin(ang) * raio * 0.7), "Raio", 0.25, 2) end end
			if el == "Terra" then rajada(c, "Terra", 1.3, f) elseif el == "Fogo" then luz(base, P.luz, 5, raio, 0.5) end
			for _, nome in ipairs({{"Dedo2E", "wing_tip_l"}, {"Dedo2D", "wing_tip_r"}}) do   -- rajada saindo das pontas das asas
				local b = ossoA(m, nome[1], nome[2]); if b then local e = emissor(b, {Texture = TEX.fumaca, Color = seq(P.nucleo), Size = ns(0, 4, 1, 16), Transparency = ns(0, 0.7, 1, 1),
					Lifetime = NumberRange.new(0.5, 0.9), Speed = NumberRange.new(30, 60), SpreadAngle = Vector2.new(40, 40), Rate = 0}); e:Emit(math.floor(25 * f)); Debris:AddItem(e, 1.2) end
			end
		end
	elseif d.hab == "Dominio" then
		if d.fase == "ativar" then aura(m, el, true, d.duracao); rajada(m:GetPivot().Position + Vector3.new(0, 25, 0), el, 1.0, f)
		elseif d.fase == "encerrar" then aura(m, el, false); anel(m:GetPivot().Position + Vector3.new(0, 2, 0), 40, P.cor, 0.6, 1, 0.6) end
	elseif d.hab == "Rugido" and d.fase == "emissao" then
		local b, dr = bocaDe(m); for i = 0, 2 do task.delay(i * 0.25, function() anel(b + dr * (8 + i * 10), 12 + i * 8, C3(240, 235, 225), 0.5, 0.3, 0.8) end) end
	elseif (d.hab == "Mordida" or d.hab == "Garra" or d.hab == "Cauda") and d.fase == "impacto" then
		rajada(d.pos, el, 0.45, f)
	end
end
return M
