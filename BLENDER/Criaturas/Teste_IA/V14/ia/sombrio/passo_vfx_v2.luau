-- ===== PASSO SOMBRIO v2 (04/11): dragao (e cavaleiro) se desfazem em breu por alguns segundos ======================
-- So no cliente (LocalTransparencyModifier). Para os OUTROS somem por completo (sem nome/vida do cavaleiro); para o
-- dono/cavaleiro ficam um vulto (VULTO) para ele continuar se guiando. Estouro de breu ao sumir e ao voltar; o corpo
-- some/volta aos poucos (ENTRA/SAI s). O fim vem do atributo PassoInvisivel (tempo do servidor). Sem luz.
local lpPasso = Players.LocalPlayer
local VULTO, ENTRA, SAI = 0.65, 0.35, 0.45
local passoAtivo = {}
local function invisivelAte(x) local v = x and x.Parent and x:GetAttribute("PassoInvisivel"); return typeof(v) == "number" and v > workspace:GetServerTimeNow() end
local function partesDe(md, l) for _, d in ipairs(md:GetDescendants()) do if d:IsA("BasePart") or d:IsA("Decal") then table.insert(l, d) end end end
local function estouroBreu(pos, f, escala)
	if f <= 0 then return end
	local a = ancora(pos); Debris:AddItem(a, 2.2)
	emissor(a, flipFumaca({Color = seq({PRETO, BREU, C3(55, 20, 95)}), LightEmission = 0.05, LightInfluence = 0.5, Size = ns(0, 4 * escala, 1, 14 * escala),
		Transparency = ns(0, 0.35, 0.5, 0.55, 1, 1), Lifetime = NumberRange.new(0.7, 1.1), Speed = NumberRange.new(14, 26), Drag = 3,
		Rotation = NumberRange.new(0, 360), RotSpeed = NumberRange.new(-60, 60), SpreadAngle = Vector2.new(180, 180), Rate = 0})):Emit(math.max(6, math.floor(26 * f)))
	emissor(a, {Texture = TEX.fumaca, Orientation = Enum.ParticleOrientation.VelocityParallel, Color = seq({PRETO, C3(90, 35, 160)}), LightEmission = 0.1,
		LightInfluence = 0.4, Size = ns(0, 0.8 * escala, 1, 0.2), Squash = ns(0, 1.2, 1, 0.6), Transparency = ns(0, 0.4, 1, 1),
		Lifetime = NumberRange.new(0.35, 0.55), Speed = NumberRange.new(40, 70), Drag = 4, SpreadAngle = Vector2.new(180, 180), Rate = 0}):Emit(math.max(4, math.floor(18 * f)))
end
local function passoEvento(m, d, f)
	local escala = math.clamp((m:GetAttribute("CorpoRaio") or 8) / 8, 0.5, 2)
	local centro = (m.PrimaryPart and m.PrimaryPart.Position) or m:GetPivot().Position
	if d.fase == "fim" then estouroBreu(centro, f, escala); return end
	if d.fase ~= "inicio" then return end
	estouroBreu(centro, f, escala)
	if passoAtivo[m] then return end
	passoAtivo[m] = true
	local cav = typeof(d.cav) == "Instance" and d.cav or nil
	local meu = m:GetAttribute("DonoUserId") == lpPasso.UserId or (cav ~= nil and cav == lpPasso.Character)
	local alvoT = meu and VULTO or 1
	local hum = (not meu) and cav and cav:FindFirstChildOfClass("Humanoid")
	local tipoNome = hum and hum.DisplayDistanceType
	if hum then hum.DisplayDistanceType = Enum.HumanoidDisplayDistanceType.None end   -- nome/vida do cavaleiro somem
	local placas = {}                                                  -- placas (nome/barra de vida) do dragao e do cavaleiro
	if not meu then
		for _, md in ipairs(cav and {m, cav} or {m}) do
			for _, g in ipairs(md:GetDescendants()) do if g:IsA("BillboardGui") and g.Enabled then g.Enabled = false; table.insert(placas, g) end end
		end
	end
	local lista, tLista, k, saindo = {}, -1, 0, false
	local c
	c = RunService.RenderStepped:Connect(function(dt)
		if os.clock() - tLista > 0.5 then                                  -- refaz a lista (acessorios, partes novas)
			lista = {}; partesDe(m, lista); if cav and cav.Parent then partesDe(cav, lista) end; tLista = os.clock()
		end
		if not saindo and not invisivelAte(m) then saindo = true end
		k = saindo and math.max(0, k - dt / SAI) or math.min(1, k + dt / ENTRA)
		local v = alvoT * (k * k * (3 - 2 * k))
		for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = v end end
		if saindo and k <= 0 then
			c:Disconnect(); passoAtivo[m] = nil
			for _, p in ipairs(lista) do if p.Parent then p.LocalTransparencyModifier = 0 end end
			if hum and hum.Parent then hum.DisplayDistanceType = tipoNome end
			for _, g in ipairs(placas) do if g.Parent then g.Enabled = true end end
		end
	end)
end

