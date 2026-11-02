-- VFXFogo (ModuleScript, ReplicatedStorage.Combate_Dragoes) — efeitos COSMETICOS do Fogo do Dragao das Montanhas
-- (refinamento 02/11), so no cliente. Chamado pelo VFXCombate antes do efeito generico; devolve true quando trata o
-- evento sozinho. Nada aqui altera dano/alvos nem o mapa (pecas temporarias em workspace.VFX_Temporarios).
-- Texturas proprias (V14/vfx/gerar_texturas_fogo.py): brasa (risco), poeira, onda (arco de ar quente), lingua (chama);
-- flipbooks de fogo/fumaca/lava ja existentes (gerar_flipbooks.py).
local RunService = game:GetService("RunService")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local Players = game:GetService("Players")
local F = {}

local C3 = Color3.fromRGB
local BRANCO = ColorSequence.new(Color3.new(1, 1, 1))
local TEX = {faisca = "rbxasset://textures/particles/sparkles_main.dds", fogo = "rbxasset://textures/particles/fire_main.dds",
	brasa = "rbxassetid://73966766890807", poeira = "rbxassetid://123198895964803", onda = "rbxassetid://137152423294429",
	lingua = "rbxassetid://74172540285919"}
local FB = {fogo = "rbxassetid://81072138040568", fumaca = "rbxassetid://114973539727313"}
local function seq(cs) local k = {}; for i, c in ipairs(cs) do table.insert(k, ColorSequenceKeypoint.new((i - 1) / (#cs - 1), c)) end; return ColorSequence.new(k) end
local function ns(...) local a = {...}; local k = {}; for i = 1, #a, 2 do table.insert(k, NumberSequenceKeypoint.new(a[i], a[i + 1])) end; return NumberSequence.new(k) end
local function flip(t, tex) t.Texture = tex; t.FlipbookLayout = Enum.ParticleFlipbookLayout.Grid8x8; t.FlipbookMode = Enum.ParticleFlipbookMode.OneShot; return t end
local QUENTE = seq({C3(255, 245, 190), C3(255, 170, 50), C3(235, 75, 15), C3(110, 25, 8)})
local BRASA = seq({C3(255, 240, 170), C3(255, 140, 35), C3(200, 45, 10)})

local function pastaFX()
	local f = workspace:FindFirstChild("VFX_Temporarios")
	if not f then f = Instance.new("Folder"); f.Name = "VFX_Temporarios"; f.Parent = workspace end
	return f
end
local function peca(props, classe)
	local p = Instance.new(classe or "Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
	for k, v in pairs(props) do p[k] = v end
	p.Parent = pastaFX(); return p
end
local function ancora(pos, vida) local a = Instance.new("Attachment"); a.WorldPosition = pos; a.Parent = workspace.Terrain; if vida then Debris:AddItem(a, vida) end; return a end
local function emissor(pai, t) local e = Instance.new("ParticleEmitter"); for k, v in pairs(t) do e[k] = v end; e.Parent = pai; return e end
local luzes = 0
local function luz(pai, cor, brilho, alcance, dur)
	if luzes >= 5 or not pai then return end
	local l = Instance.new("PointLight"); l.Color = cor; l.Brightness = brilho; l.Range = alcance; l.Shadows = false; l.Parent = pai; luzes += 1
	if dur then TweenService:Create(l, TweenInfo.new(dur, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Brightness = 0}):Play(); task.delay(dur, function() l:Destroy(); luzes -= 1 end) end
	return l
end
local function liberarLuz(l) if l and l.Parent then l:Destroy(); luzes -= 1 end end
local cacheOsso = setmetatable({}, {__mode = "k"})
local function osso(m, ...)
	cacheOsso[m] = cacheOsso[m] or {}
	for _, n in ipairs({...}) do
		local b = cacheOsso[m][n]
		if not (b and b.Parent) then b = nil; for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") and d.Name == n then b = d; break end end; cacheOsso[m][n] = b end
		if b then return b end
	end
end
local function boca(m)
	local tip = osso(m, "mouth_upper_tip"); local cab = osso(m, "Cabeca")
	if tip and cab then local p = tip.TransformedWorldCFrame.Position; local d = p - cab.TransformedWorldCFrame.Position; return p, d.Magnitude > 0.1 and d.Unit or m:GetPivot().LookVector end
	return m:GetPivot().Position + Vector3.new(0, 20, 0), m:GetPivot().LookVector
end
local gp = RaycastParams.new(); gp.FilterType = Enum.RaycastFilterType.Include
local function chao(p, alcance)
	gp.FilterDescendantsInstances = {workspace.Terrain, workspace:FindFirstChild("Baseplate")}
	return workspace:Raycast(p + Vector3.new(0, 20, 0), Vector3.new(0, -(alcance or 60), 0), gp)
end

-- explosao ignea localizada (bola de chama + brasas com rastro + fumaca + clarao), escala ~ 1 = mordida
local function explosao(pos, escala, f)
	local a = ancora(pos, 3)
	emissor(a, flip({Color = BRANCO, LightEmission = 0.6, LightInfluence = 0, Size = ns(0, 3 * escala, 0.3, 11 * escala, 1, 14 * escala), Transparency = ns(0, 0, 0.7, 0.3, 1, 1),
		Lifetime = NumberRange.new(0.45, 0.7), Speed = NumberRange.new(8, 22 * escala), SpreadAngle = Vector2.new(180, 180), Drag = 3, Rotation = NumberRange.new(0, 360),
		RotSpeed = NumberRange.new(-80, 80), Acceleration = Vector3.new(0, 14, 0), Rate = 0}, FB.fogo)):Emit(math.floor(14 * escala * f) + 2)
	emissor(a, {Texture = TEX.brasa, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = BRASA, LightEmission = 1, Size = ns(0, 1.2 * escala, 1, 0.4),
		Lifetime = NumberRange.new(0.5, 1.1), Speed = NumberRange.new(30 * escala, 70 * escala), SpreadAngle = Vector2.new(180, 180), Drag = 1.8,
		Acceleration = Vector3.new(0, -40, 0), Rate = 0}):Emit(math.floor(36 * escala * f) + 4)
	emissor(a, flip({Color = seq({C3(75, 60, 52), C3(38, 33, 31)}), LightInfluence = 1, Size = ns(0, 5 * escala, 1, 18 * escala), Transparency = ns(0, 0.4, 1, 1),
		Lifetime = NumberRange.new(1.2, 1.8), Speed = NumberRange.new(4, 12), SpreadAngle = Vector2.new(180, 180), Acceleration = Vector3.new(0, 7, 0),
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-20, 20), Rate = 0}, FB.fumaca)):Emit(math.floor(7 * escala * f) + 1)
	luz(a, C3(255, 140, 50), 5, 30 * escala, 0.45)
end

-- ===== ARREMETIDA (5 s): chamas surgem pelo corpo e crescem com a VELOCIDADE real; rastro de fogo entre as asas e
-- atras do corpo; mordida = mandibula em brasa; contato = explosao ignea + tranco de camera do cavaleiro ===============
local arr = {}
local function arremetida(m, d, f)
	if d.fase == "preparo" then
		local s = arr[m]; if s and s.con then s.con:Disconnect() end
		s = {emis = {}, t0 = os.clock(), dur = d.duracao or 5}; arr[m] = s
		for _, spec in ipairs({{{"Coluna2", "spine_0"}, 26, 7}, {{"Pescoco4", "Pescoco2"}, 18, 5}, {{"Quadril"}, 22, 7}, {{"Cauda2", "Cauda3"}, 14, 5},
			{{"wing_1_l", "AsaE_1"}, 12, 5}, {{"wing_1_r", "AsaD_1"}, 12, 5}}) do
			local b = osso(m, table.unpack(spec[1]))
			if b then
				local e = emissor(b, flip({Color = BRANCO, LightEmission = 0.5, LightInfluence = 0, Size = ns(0, spec[3] * 0.5, 0.5, spec[3], 1, spec[3] * 0.3), Transparency = ns(0, 0.2, 1, 1),
					Lifetime = NumberRange.new(0.25, 0.45), Speed = NumberRange.new(2, 6), SpreadAngle = Vector2.new(180, 180), Rotation = NumberRange.new(0, 360),
					RotSpeed = NumberRange.new(-60, 60), Rate = 0, Shape = Enum.ParticleEmitterShape.Sphere}, FB.fogo))
				local e2 = emissor(b, {Texture = TEX.brasa, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = BRASA, LightEmission = 1, Size = ns(0, 0.9, 1, 0.3),
					Lifetime = NumberRange.new(0.4, 0.8), Speed = NumberRange.new(4, 12), SpreadAngle = Vector2.new(180, 180), Drag = 1.2, Rate = 0})
				table.insert(s.emis, {e = e, base = spec[2]}); table.insert(s.emis, {e = e2, base = spec[2] * 0.6})
			end
		end
		local a0, a1 = osso(m, "wing_3_l", "AsaE_2"), osso(m, "wing_3_r", "AsaD_2")
		if a0 and a1 then
			local tr = Instance.new("Trail"); tr.Attachment0 = a0; tr.Attachment1 = a1; tr.Lifetime = 0.2; tr.LightEmission = 0.9; tr.LightInfluence = 0
			tr.Color = seq({C3(255, 220, 120), C3(255, 110, 25), C3(120, 25, 8)}); tr.Transparency = ns(0, 0.55, 1, 1); tr.Texture = TEX.fogo
			tr.TextureMode = Enum.TextureMode.Stretch; tr.FaceCamera = false; tr.Parent = m.PrimaryPart; s.tr = tr
		end
		local q = osso(m, "Quadril")
		if q then                                                          -- esteira de chamas que fica para tras
			s.esteira = emissor(q, flip({Color = BRANCO, LightEmission = 0.45, LightInfluence = 0, Size = ns(0, 6, 0.5, 12, 1, 4), Transparency = ns(0, 0.3, 1, 1),
				Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(0, 2), SpreadAngle = Vector2.new(180, 180), Rotation = NumberRange.new(0, 360),
				Acceleration = Vector3.new(0, 10, 0), Rate = 0, LockedToPart = false}, FB.fogo))
		end
		s.luz = luz(m.PrimaryPart, C3(255, 130, 45), 0, 36)
		s.con = RunService.Heartbeat:Connect(function()
			if not m.Parent then s.con:Disconnect(); return end
			local t = os.clock() - s.t0
			local v = m:GetAttribute("Velocidade") or 0
			local k = math.clamp(v / 70, 0, 1)
			local entra = math.clamp(t / 0.45, 0, 1)                         -- chamas SURGEM (nao aparecem prontas)
			local sai = s.fim and math.clamp(1 - (os.clock() - s.fim) / 0.9, 0, 1) or 1
			local g = entra * sai * (0.25 + 0.75 * k) * f
			for _, x in ipairs(s.emis) do x.e.Rate = x.base * g end
			if s.esteira then s.esteira.Rate = 40 * k * entra * sai * f end
			if s.tr then s.tr.Lifetime = 0.12 + 0.45 * k; s.tr.Transparency = ns(0, 1 - 0.6 * k * sai, 1, 1) end
			if s.luz then s.luz.Brightness = 3 * g end
			if s.fim and sai <= 0 then
				s.con:Disconnect()
				for _, x in ipairs(s.emis) do Debris:AddItem(x.e, 1.2) end
				if s.esteira then Debris:AddItem(s.esteira, 1.2) end
				if s.tr then Debris:AddItem(s.tr, 0.6) end
				liberarLuz(s.luz); if arr[m] == s then arr[m] = nil end
			end
		end)
	elseif d.fase == "mordida" then                                       -- mandibula abre em brasa
		local tip = osso(m, "mouth_upper_tip", "Cabeca")
		if tip then
			local e = emissor(tip, flip({Color = BRANCO, LightEmission = 0.7, LightInfluence = 0, Size = ns(0, 2, 0.5, 5, 1, 1), Transparency = ns(0, 0.1, 1, 1),
				Lifetime = NumberRange.new(0.2, 0.35), Speed = NumberRange.new(4, 10), SpreadAngle = Vector2.new(50, 50), Rate = 55 * f}, FB.fogo)); Debris:AddItem(e, 0.5)
		end
	elseif d.fase == "impacto" then
		explosao(d.pos, d.mordida and 1.5 or 1.0, f)
		local lp = Players.LocalPlayer                                     -- tranco curto so para o cavaleiro deste dragao
		if lp and m:GetAttribute("Cavaleiro") == lp.UserId then
			local cam = workspace.CurrentCamera; local t0 = os.clock()
			local c; c = RunService.RenderStepped:Connect(function()
				local k = 1 - (os.clock() - t0) / 0.3; if k <= 0 then c:Disconnect(); return end
				cam.CFrame *= CFrame.new((math.random() - 0.5) * 0.8 * k, (math.random() - 0.5) * 0.8 * k, 0)
			end)
		end
	elseif d.fase == "fim" then
		local s = arr[m]; if s then s.fim = os.clock() end
	end
	return true
end

-- ===== TEMPESTADE: cada batida REAL = coluna de ar quente descendo + frentes de pressao irregulares + poeira subindo
-- do chao + rochas arrancadas com trajetoria fisica (gravidade, giro, quique no chao) + brasas varridas com rastro ======
local rochas = {}                                                     -- simulacao balistica leve, um so laço para todas
local conRochas
local function simularRochas()
	if conRochas then return end
	conRochas = RunService.Heartbeat:Connect(function(dt)
		dt = math.min(dt, 1 / 20)
		for i = #rochas, 1, -1 do
			local r = rochas[i]
			r.t += dt; r.v += Vector3.new(0, -70, 0) * dt
			local nova = r.p + r.v * dt
			local h = workspace:Raycast(r.p, nova - r.p, gp)
			if h and r.v.Y < 0 then                                         -- quique: perde energia, poeirinha no impacto
				r.v = Vector3.new(r.v.X * 0.55, -r.v.Y * 0.32, r.v.Z * 0.55); nova = h.Position + h.Normal * r.raio; r.quiques += 1
				if r.quiques <= 1 then
					local a = ancora(h.Position, 1.2)
					emissor(a, {Texture = TEX.poeira, Color = seq({C3(150, 128, 105), C3(110, 95, 82)}), LightInfluence = 1, Size = ns(0, 1.5, 1, 4.5),
						Transparency = ns(0, 0.45, 1, 1), Lifetime = NumberRange.new(0.5, 0.8), Speed = NumberRange.new(3, 8), SpreadAngle = Vector2.new(70, 70),
						EmissionDirection = Enum.NormalId.Top, Rotation = NumberRange.new(0, 360), Rate = 0}):Emit(4)
				end
			end
			r.p = nova; r.rot = r.rot * CFrame.Angles(r.w.X * dt, r.w.Y * dt, r.w.Z * dt)
			if r.parte.Parent then r.parte.CFrame = CFrame.new(r.p) * r.rot end
			if r.t > r.vida or r.quiques > 2 then
				TweenService:Create(r.parte, TweenInfo.new(0.4), {Transparency = 1}):Play(); Debris:AddItem(r.parte, 0.45); table.remove(rochas, i)
			end
		end
		if #rochas == 0 then conRochas:Disconnect(); conRochas = nil end
	end)
end
local function rocha(origem, dir, forca, tam)
	if #rochas > 40 then return end
	local s = tam * (0.6 + math.random() * 0.8)
	local p = peca({Size = Vector3.new(s, s * (0.6 + math.random() * 0.4), s * (0.7 + math.random() * 0.5)), Material = Enum.Material.Basalt,
		Color = C3(58 + math.random(0, 18), 49 + math.random(0, 12), 44 + math.random(0, 8)), CFrame = CFrame.new(origem)}, math.random() < 0.45 and "WedgePart" or "Part")
	if math.random() < 0.35 then                                          -- algumas incandescentes (rocha vulcanica)
		p.Material = Enum.Material.CrackedLava; p.Color = C3(90, 55, 40)
	end
	table.insert(rochas, {parte = p, p = origem, v = dir * forca + Vector3.new(0, forca * (0.5 + math.random() * 0.5), 0), raio = s * 0.5,
		w = Vector3.new(math.random(-8, 8), math.random(-8, 8), math.random(-8, 8)), rot = CFrame.Angles(math.random() * 6, math.random() * 6, 0),
		t = 0, vida = 2.4, quiques = 0})
	simularRochas()
end
local function tempestadeBatida(m, d, f)
	local c = d.pos; local raio = d.raio or 78; local i = d.indice or 1
	local k = (i == 1 and 1 or 0.72) * f                                    -- 1a batida mais forte; as seguintes continuam fortes
	local alto = (d.altura or 0) + 18
	-- 1) coluna de ar quente descendo das asas ate o chao (antes da onda radial)
	local col = ancora(c + Vector3.new(0, alto, 0), 2)
	emissor(col, {Texture = TEX.onda, Color = seq({C3(255, 225, 180), C3(255, 170, 110)}), LightEmission = 0.25, LightInfluence = 0.6, Size = ns(0, 10, 1, 26),
		Transparency = ns(0, 0.72, 1, 1), Lifetime = NumberRange.new(0.28, 0.38), Speed = NumberRange.new(alto * 2.6, alto * 3.2), EmissionDirection = Enum.NormalId.Bottom,
		SpreadAngle = Vector2.new(18, 18), Rotation = NumberRange.new(-20, 20), Rate = 0}):Emit(math.floor(8 * k) + 2)
	if not d.superficie then                                              -- no alto: so ar quente e brasas em volta do corpo
		local a = ancora(m:GetPivot().Position + Vector3.new(0, 12, 0), 2)
		emissor(a, {Texture = TEX.onda, Color = seq({C3(255, 220, 170), C3(255, 150, 80)}), LightEmission = 0.3, LightInfluence = 0.5, Size = ns(0, 12, 1, 40),
			Transparency = ns(0, 0.75, 1, 1), Lifetime = NumberRange.new(0.45, 0.6), Speed = NumberRange.new(70, 100), SpreadAngle = Vector2.new(180, 25),
			Rotation = NumberRange.new(0, 360), Rate = 0, Orientation = Enum.ParticleOrientation.VelocityPerpendicular}):Emit(math.floor(10 * k) + 3)
		emissor(a, {Texture = TEX.brasa, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = BRASA, LightEmission = 1, Size = ns(0, 1.3, 1, 0.4),
			Lifetime = NumberRange.new(0.6, 1.0), Speed = NumberRange.new(60, 110), SpreadAngle = Vector2.new(180, 30), Drag = 1.4, Rate = 0}):Emit(math.floor(50 * k) + 5)
		return
	end
	task.delay(0.08, function()
		-- 2) frentes de pressao: arcos translucidos IRREGULARES saindo em leque (nao um anel perfeito) + calor tremulo
		local n = math.max(6, math.floor(14 * k))
		for j = 1, n do
			local ang = (j / n) * math.pi * 2 + (math.random() - 0.5) * 0.5
			local dir = Vector3.new(math.cos(ang), 0, math.sin(ang))
			local a = ancora(c + dir * 6 + Vector3.new(0, 2 + math.random() * 3, 0), 2)
			emissor(a, {Texture = TEX.onda, Color = seq({C3(255, 230, 190), C3(240, 175, 120)}), LightEmission = 0.2, LightInfluence = 0.7,
				Size = ns(0, 6, 1, 20 + math.random() * 10), Transparency = ns(0, 0.7, 0.6, 0.82, 1, 1), Lifetime = NumberRange.new(0.55, 0.8),
				Speed = NumberRange.new(raio * 1.4, raio * 1.7), Drag = 1.6, EmissionDirection = Enum.NormalId.Front, SpreadAngle = Vector2.new(6, 4),
				Orientation = Enum.ParticleOrientation.VelocityPerpendicular, Rotation = NumberRange.new(-15, 15), Rate = 0}).Parent = a
			a.WorldCFrame = CFrame.lookAt(a.WorldPosition, a.WorldPosition + dir)
			a:FindFirstChildOfClass("ParticleEmitter"):Emit(math.random(2, 3))
		end
		-- 3) poeira: anel baixo varrido para fora, depois nuvens que SOBEM devagar seguindo o vento
		local base = peca({Shape = Enum.PartType.Cylinder, Size = Vector3.new(1, raio * 0.5, raio * 0.5), Transparency = 1,
			CFrame = CFrame.new(c + Vector3.new(0, 2, 0)) * CFrame.Angles(0, 0, math.rad(90))}); Debris:AddItem(base, 3.5)
		emissor(base, {Shape = Enum.ParticleEmitterShape.Cylinder, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface, ShapeInOut = Enum.ParticleEmitterShapeInOut.Outward,
			Texture = TEX.poeira, Color = seq({C3(165, 142, 118), C3(120, 104, 90)}), LightInfluence = 1, Size = ns(0, 5, 1, 18), Transparency = ns(0, 0.35, 0.7, 0.6, 1, 1),
			Lifetime = NumberRange.new(1.1, 1.8), Speed = NumberRange.new(raio * 0.9, raio * 1.3), Drag = 2.2, Acceleration = Vector3.new(0, 6, 0),
			Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-40, 40), Rate = 0}):Emit(math.floor(40 * k) + 6)
		-- 4) brasas incandescentes varridas para fora com rastro curto
		emissor(base, {Shape = Enum.ParticleEmitterShape.Cylinder, ShapeStyle = Enum.ParticleEmitterShapeStyle.Surface, ShapeInOut = Enum.ParticleEmitterShapeInOut.Outward,
			Texture = TEX.brasa, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = BRASA, LightEmission = 1, Size = ns(0, 1.4, 1, 0.4),
			Lifetime = NumberRange.new(0.6, 1.2), Speed = NumberRange.new(raio * 1.0, raio * 1.6), Drag = 1.5, Acceleration = Vector3.new(0, 14, 0), Rate = 0}):Emit(math.floor(70 * k) + 8)
		-- labaredas rasteiras curtas (vento QUENTE), poucas
		for j = 1, math.floor(5 * k) do
			local ang = math.random() * math.pi * 2; local r = raio * (0.25 + math.random() * 0.4)
			local h = chao(c + Vector3.new(math.cos(ang) * r, 4, math.sin(ang) * r))
			if h then
				local a = ancora(h.Position, 1.8)
				emissor(a, flip({Color = BRANCO, LightEmission = 0.5, LightInfluence = 0, Size = ns(0, 2, 0.4, 5, 1, 2), Transparency = ns(0, 0.2, 1, 1),
					Lifetime = NumberRange.new(0.35, 0.6), Speed = NumberRange.new(8, 16), EmissionDirection = Enum.NormalId.Top, SpreadAngle = Vector2.new(40, 40),
					Acceleration = Vector3.new(math.cos(ang) * 30, 6, math.sin(ang) * 30), Rotation = NumberRange.new(0, 360), Rate = 0}, FB.fogo)):Emit(math.random(3, 5))
			end
		end
		luz(base, C3(255, 140, 55), 2.5 * k, raio * 0.8, 0.5)
	end)
	-- 5) rochas arrancadas da superficie real perto do centro (quantidade por batida; LOD)
	local nR = math.floor((i == 1 and 12 or 7) * f)
	for j = 1, nR do
		local ang = math.random() * math.pi * 2; local r = raio * (0.12 + math.random() * 0.35)
		local h = chao(c + Vector3.new(math.cos(ang) * r, 6, math.sin(ang) * r))
		if h then
			local dir = Vector3.new(math.cos(ang), 0, math.sin(ang))
			task.delay(0.06 + r / 300, function() rocha(h.Position + Vector3.new(0, 1.5, 0), dir, 26 + math.random() * 22, i == 1 and 2.2 or 1.6) end)
		end
	end
end

-- ===== SOPRO (camadas extras sobre o jato do VFXCombate): garganta acende no preparo; linguas de chama irregulares
-- no meio do jato (forma organica, sem cone rigido) e calor tremulo junto a boca ===================================
local sopro = {}
local function soproExtra(m, d, f)
	if d.fase == "preparo" then
		local g = osso(m, "Pescoco4", "Pescoco2")
		if g then local l = luz(g, C3(255, 120, 40), 0, 14); if l then TweenService:Create(l, TweenInfo.new(1.0, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Brightness = 2.2}):Play(); task.delay(1.4, function() liberarLuz(l) end) end end
	elseif d.fase == "emissao" then
		local s = sopro[m]; if s and s.con then s.con:Disconnect() end
		s = {}; sopro[m] = s
		local b, dir = boca(m)
		s.a = ancora(b)
		local alc = d.alcance or 110
		s.linguas = emissor(s.a, {Texture = TEX.lingua, Color = QUENTE, LightEmission = 0.75, LightInfluence = 0, Size = ns(0, 2.5, 0.35, 9, 0.8, 15, 1, 8),
			Transparency = ns(0, 0.35, 0.6, 0.45, 1, 1), Lifetime = NumberRange.new(0.5, 0.75), Speed = NumberRange.new(alc * 1.25, alc * 1.45), Drag = 1.3,
			SpreadAngle = Vector2.new(7, 7), Orientation = Enum.ParticleOrientation.VelocityParallel, Acceleration = Vector3.new(0, 12, 0), Rate = 45 * f,
			EmissionDirection = Enum.NormalId.Front})
		s.tremulo = emissor(s.a, {Texture = TEX.onda, Color = seq({C3(255, 235, 200), C3(255, 200, 150)}), LightEmission = 0.15, LightInfluence = 0.6,
			Size = ns(0, 3, 1, 9), Transparency = ns(0, 0.82, 1, 1), Lifetime = NumberRange.new(0.25, 0.4), Speed = NumberRange.new(20, 35),
			SpreadAngle = Vector2.new(25, 25), Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-90, 90), Rate = 18 * f, EmissionDirection = Enum.NormalId.Front})
		s.alvo = d.alvoPos
		s.con = RunService.RenderStepped:Connect(function()
			if not m.Parent then s.con:Disconnect(); return end
			local p, dr = boca(m)
			if s.alvo then local v = s.alvo - p; if v.Magnitude > 5 then dr = (dr * 0.3 + v.Unit * 0.7).Unit end end
			-- turbulencia: a direcao oscila de leve (o fluxo nao e um cilindro parado)
			local t = os.clock()
			dr = (dr + Vector3.new(math.sin(t * 7.3), math.sin(t * 5.1) * 0.6, math.cos(t * 6.2)) * 0.035).Unit
			s.a.WorldCFrame = CFrame.lookAt(p, p + dr)
			s.linguas.Rate = (38 + 14 * math.sin(t * 9)) * f                -- variacoes naturais de densidade
		end)
	elseif d.fase == "mira" then local s = sopro[m]; if s then s.alvo = d.alvoPos end
	elseif d.fase == "fim" then
		local s = sopro[m]; sopro[m] = nil
		if s then
			for _, e in ipairs({s.linguas, s.tremulo}) do if e then TweenService:Create(e, TweenInfo.new(0.35), {Rate = 0}):Play() end end
			task.delay(1.0, function() if s.con then s.con:Disconnect() end; if s.a then s.a:Destroy() end end)
		end
	end
	return false                                                          -- o jato principal continua no VFXCombate
end

function F.evento(d, f)
	local m = d.d; if not (m and m.Parent) or f <= 0 then return false end
	if d.hab == "Arremetida" then return arremetida(m, d, f)
	elseif d.hab == "Tempestade" and d.fase == "batida" then tempestadeBatida(m, d, f); return false   -- o resto (asas em brasa) segue no VFXCombate
	elseif d.hab == "Sopro" then return soproExtra(m, d, f) end
	return false
end
return F
