-- PATCH_CORRENTES_AR (04/11, pedido do usuario: "as correntes tambem devem prender o aereo"): o alvo pode estar no AR.
-- Centro: alvo da IA / ponto mirado; se ali nao ha chao perto (mais de `alturaChao` acima), o centro fica no ar (no
-- alvo/ponto) e as correntes saem de fendas de sombra no ar (visual). Selecao: distancia 3D ao centro <= raio (+ corpo
-- dos guardioes). Prender: personagem (Humanoid) perde andar/pulo aos poucos e, se estiver no ar, e SEGURADO onde esta
-- (AlignPosition com forca crescente); dragao/guardiao (sem Humanoid) recebe PresoFator 1 -> 0 em `aperta` s, que a IA
-- (Locomotor) e a montaria usam para frear ate parar. Tempo preso, ticks, dano, Marca e resistencia iguais.
local presos, resistente = {}, {}                                     -- [alvo] = {ate, ws, pulo, usaJP, fonte, ...} / [alvo] = os.clock()
N.presosCorrentes = presos
local function soltarCorrente(a)
	local p = presos[a]; if not p then return end
	presos[a] = nil
	local h = a.Parent and a:FindFirstChildOfClass("Humanoid")
	if h then h.WalkSpeed = p.ws; if p.usaJP then h.JumpPower = p.pulo else h.JumpHeight = p.pulo end end
	if p.segura then p.segura:Destroy() end; if p.ancA then p.ancA:Destroy() end
	if a.Parent then a:SetAttribute("PresoCorrentes", nil); a:SetAttribute("PresoFator", nil) end
	FX:FireAllClients({d = p.fonte, hab = "Correntes", fase = "soltar", alvo = a, el = "Sombra"})
end
local rpC = RaycastParams.new(); rpC.FilterType = Enum.RaycastFilterType.Exclude
local function chaoAbaixo(pos, ignorar, ate)
	rpC.FilterDescendantsInstances = ignorar
	local h = workspace:Raycast(pos + Vector3.new(0, 6, 0), Vector3.new(0, -(ate or 400) - 6, 0), rpC); return h and h.Position
end
function N:_Correntes(def, el, noAr, op)
	el = "Sombra"
	local m = self.m
	local ignorar = {m}; for _, a in ipairs(self:alvosValidos()) do table.insert(ignorar, a) end
	local vfx = workspace:FindFirstChild("VFX_Temporarios"); if vfx then table.insert(ignorar, vfx) end
	self.miraDir = nil                                                     -- so a mira desta ativacao (mira viva do cliente)
	FX:FireAllClients({d = m, hab = "Correntes", fase = "preparo", el = el, noAr = noAr})
	self:tocar(def.clipe, noAr, {}, function() end)
	local batida = noAr and def.batidaAr or def.batida
	task.wait(batida)
	if not m.Parent or m:GetAttribute("Incapacitado") then return end
	-- ponto: alvo da IA ou mira; perto do chao -> centro no chao; longe -> centro no ar (no proprio ponto)
	local p
	if op.alvo and raiz(op.alvo) then p = raiz(op.alvo).Position
	else
		local d = self.miraDir or (typeof(op.direcao) == "Vector3" and op.direcao.Magnitude > 0.1 and op.direcao.Unit) or self:frente()
		local b = self:boca()
		rpC.FilterDescendantsInstances = {m, vfx}                            -- a mira PODE acertar um alvo no ar
		local h = workspace:Raycast(b, d * def.alcance, rpC)
		p = h and h.Position or (b + d * def.alcance)
	end
	local pv = m:GetPivot().Position
	if (p - pv).Magnitude > def.alcance then p = pv + (p - pv).Unit * def.alcance end
	local g = chaoAbaixo(p, ignorar, def.alturaChao + 4)
	local noChao = g ~= nil
	local centro = g or p
	FX:FireAllClients({d = m, hab = "Correntes", fase = "aviso", el = el, pos = centro, raio = def.raio, duracao = def.aviso, ar = not noChao})
	task.wait(def.aviso)
	if not m.Parent then return end
	local lista = {}                                                       -- no raio (3D), mais proximos primeiro
	for _, a in ipairs(self:alvosValidos()) do
		local r = raiz(a)
		if r then
			local extra = a:GetAttribute("GuardiaoNinho") and (a:GetAttribute("CorpoRaio") or 8) or 0
			local dist = (r.Position - centro).Magnitude
			if noChao then dist = math.min(dist, (plano(r.Position - centro).Magnitude ^ 2 + math.max(0, math.abs(r.Position.Y - centro.Y) - def.alturaChao) ^ 2) ^ 0.5) end
			if dist <= def.raio + extra then table.insert(lista, {a, dist}) end
		end
	end
	table.sort(lista, function(x, y) return x[2] < y[2] end)
	FX:FireAllClients({d = m, hab = "Correntes", fase = "erupcao", el = el, pos = centro, raio = def.raio, ar = not noChao})
	for i = 1, math.min(#lista, def.maxAlvos) do
		local a = lista[i][1]
		self:aplicar({a}, def.dano, "Correntes", def.intensidade, el)         -- acerto inicial: dano + Marca
		local h = a:FindFirstChildOfClass("Humanoid")
		local vivo = (h and h.Health > 0) or (not h and not a:GetAttribute("Incapacitado"))
		if vivo and (resistente[a] or 0) < os.clock() and not presos[a] then
			local r = raiz(a)
			local usaJP = h and h.UseJumpPower
			local p = {ate = os.clock() + def.preso, ws = h and h.WalkSpeed or 0, pulo = h and (usaJP and h.JumpPower or h.JumpHeight) or 0, usaJP = usaJP, fonte = m, t0 = os.clock()}
			presos[a] = p
			-- PATCH_CORRENTES_APERTA (04/11): as correntes apertam aos poucos; o movimento cai ate 0 em def.aperta s
			local ap = def.aperta or 0
			local noAlto = not chaoAbaixo(r.Position, ignorar, def.alturaChao)  -- alvo no ar: segura onde esta
			if h and noAlto then
				p.ancA = Instance.new("Attachment"); p.ancA.Name = "Correntes_Ancora"; p.ancA.Parent = r
				p.segura = Instance.new("AlignPosition"); p.segura.Name = "Correntes_Segura"; p.segura.Mode = Enum.PositionAlignmentMode.OneAttachment
				p.segura.Attachment0 = p.ancA; p.segura.Position = r.Position; p.segura.Responsiveness = 12; p.segura.MaxForce = 0; p.segura.Parent = r
			end
			local function fator() if ap <= 0 then return 0 end; local x = math.clamp((os.clock() - p.t0) / ap, 0, 1); return (1 - x) ^ 2 end
			local function apertar()
				local k = fator()
				if h then
					local ws, pl = p.ws * k, p.pulo * k
					if h.WalkSpeed > ws + 0.01 then h.WalkSpeed = ws end                -- outro script tentou soltar: continua apertando
					if usaJP then if h.JumpPower > pl + 0.01 then h.JumpPower = pl end elseif h.JumpHeight > pl + 0.01 then h.JumpHeight = pl end
					if p.segura then p.segura.MaxForce = (1 - k) * r.AssemblyMass * workspace.Gravity * 6 end
				else
					a:SetAttribute("PresoFator", k)                                   -- IA/montaria freiam por este fator
				end
			end
			apertar()
			if ap > 0 then task.spawn(function() while presos[a] == p and os.clock() - p.t0 < ap + 0.05 do RunService.Heartbeat:Wait(); if presos[a] == p then apertar() end end end) end
			a:SetAttribute("PresoCorrentes", workspace:GetServerTimeNow() + def.preso)
			FX:FireAllClients({d = m, hab = "Correntes", fase = "prender", el = el, alvo = a, duracao = def.preso, aperta = ap, ar = noAlto})
			task.spawn(function()
				while presos[a] == p and os.clock() < p.ate do
					task.wait(def.tick)
					local ok = a.Parent and ((h and h.Health > 0) or (not h and not a:GetAttribute("Incapacitado")))
					if presos[a] ~= p or not ok then break end
					apertar()                                                   -- PATCH_CORRENTES_APERTA (antes: WalkSpeed = 0 direto)
					N.ferir(m, a, def.danoTick, el, "Correntes", "leve", true)  -- tick: usa a Marca, nao marca
				end
				if presos[a] == p then soltarCorrente(a); resistente[a] = os.clock() + def.resistencia end
			end)
		end
	end
	local resto = (noAr and def.duracaoAr or def.duracao) - batida - def.aviso
	if resto > 0 then task.wait(resto) end
end
