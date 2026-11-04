-- PATCH_CORRENTES_NOITE (04/11): Correntes da Noite (Sombrio, slot Arremetida). Longo alcance: o ponto vem da mira
-- (montado: direcao da boca ao cursor, com mira viva ate a batida; IA: o alvo). As garras batem no chao -> aviso curto
-- no ponto (tempo para sair) -> correntes de sombra saem do chao e PRENDEM ate maxAlvos alvos no raio (nao andam nem
-- pulam; podem atacar), com acerto inicial (Marca) e dano Sombra continuo enquanto presos (ticks: multiplicador da
-- Marca, sem marcar). Alvo no ar (acima de alturaChao) nao e preso. Recem-solto fica resistente por `resistencia` s:
-- novas correntes so causam o acerto. Dragoes/guardioes (sem Humanoid) so recebem dano. Numeros NAO_APROVADO.
local presos, resistente = {}, {}                                     -- [alvo] = {ate, ws, pulo, usaJP, fonte} / [alvo] = os.clock()
N.presosCorrentes = presos
local function soltarCorrente(a)
	local p = presos[a]; if not p then return end
	presos[a] = nil
	local h = a.Parent and a:FindFirstChildOfClass("Humanoid")
	if h then h.WalkSpeed = p.ws; if p.usaJP then h.JumpPower = p.pulo else h.JumpHeight = p.pulo end end
	if a.Parent then a:SetAttribute("PresoCorrentes", nil) end
	FX:FireAllClients({d = p.fonte, hab = "Correntes", fase = "soltar", alvo = a, el = "Sombra"})
end
local rpC = RaycastParams.new(); rpC.FilterType = Enum.RaycastFilterType.Exclude
local function chaoAbaixo(pos, ignorar)
	rpC.FilterDescendantsInstances = ignorar
	local h = workspace:Raycast(pos + Vector3.new(0, 6, 0), Vector3.new(0, -400, 0), rpC); return h and h.Position
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
	local centro
	if op.alvo and raiz(op.alvo) then
		centro = chaoAbaixo(raiz(op.alvo).Position, ignorar) or raiz(op.alvo).Position
	else
		local d = self.miraDir or (typeof(op.direcao) == "Vector3" and op.direcao.Magnitude > 0.1 and op.direcao.Unit) or self:frente()
		local b = self:boca()
		rpC.FilterDescendantsInstances = ignorar
		local h = workspace:Raycast(b, d * def.alcance, rpC)
		local p = h and h.Position or (b + d * def.alcance)
		centro = chaoAbaixo(p, ignorar) or p
	end
	local pv = m:GetPivot().Position; local hz = plano(centro - pv)          -- alcance horizontal a partir do dragao
	if hz.Magnitude > def.alcance then centro = chaoAbaixo(Vector3.new(pv.X, centro.Y, pv.Z) + hz.Unit * def.alcance, ignorar) or centro end
	FX:FireAllClients({d = m, hab = "Correntes", fase = "aviso", el = el, pos = centro, raio = def.raio, duracao = def.aviso})
	task.wait(def.aviso)
	if not m.Parent then return end
	local lista = {}                                                       -- no raio e perto do chao (nao voando), mais proximos primeiro
	for _, a in ipairs(self:alvosValidos()) do
		local r = raiz(a)
		if r and plano(r.Position - centro).Magnitude <= def.raio and math.abs(r.Position.Y - centro.Y) <= def.alturaChao + 6 then
			local g = chaoAbaixo(r.Position, ignorar)
			if not g or r.Position.Y - g.Y <= def.alturaChao then table.insert(lista, {a, plano(r.Position - centro).Magnitude}) end
		end
	end
	table.sort(lista, function(x, y) return x[2] < y[2] end)
	FX:FireAllClients({d = m, hab = "Correntes", fase = "erupcao", el = el, pos = centro, raio = def.raio})
	for i = 1, math.min(#lista, def.maxAlvos) do
		local a = lista[i][1]
		self:aplicar({a}, def.dano, "Correntes", def.intensidade, el)         -- acerto inicial: dano + Marca
		local h = a:FindFirstChildOfClass("Humanoid")
		if h and h.Health > 0 and (resistente[a] or 0) < os.clock() and not presos[a] then
			local usaJP = h.UseJumpPower
			local p = {ate = os.clock() + def.preso, ws = h.WalkSpeed, pulo = usaJP and h.JumpPower or h.JumpHeight, usaJP = usaJP, fonte = m}
			presos[a] = p
			h.WalkSpeed = 0; if usaJP then h.JumpPower = 0 else h.JumpHeight = 0 end
			a:SetAttribute("PresoCorrentes", workspace:GetServerTimeNow() + def.preso)
			FX:FireAllClients({d = m, hab = "Correntes", fase = "prender", el = el, alvo = a, duracao = def.preso})
			task.spawn(function()
				while presos[a] == p and os.clock() < p.ate do
					task.wait(def.tick)
					if presos[a] ~= p or not (a.Parent and h.Health > 0) then break end
					if h.WalkSpeed ~= 0 then h.WalkSpeed = 0 end                -- outro script tentou soltar: continua preso
					N.ferir(m, a, def.danoTick, el, "Correntes", "leve", true)  -- tick: usa a Marca, nao marca
				end
				if presos[a] == p then soltarCorrente(a); resistente[a] = os.clock() + def.resistencia end
			end)
		end
	end
	local resto = (noAr and def.duracaoAr or def.duracao) - batida - def.aviso
	if resto > 0 then task.wait(resto) end
end
