local function ins(mod, ancora, novo, antes)
	local src = mod.Source; local i, j = string.find(src, ancora, 1, true); assert(i, mod.Name .. " ancora"); assert(not string.find(src, ancora, j + 1, true), "repetida")
	if antes then src = string.sub(src, 1, i - 1) .. novo .. string.sub(src, i) else src = string.sub(src, 1, j) .. novo .. string.sub(src, j + 1) end
	mod.Source = src
end
local function soma(mod) local s = mod.Source; local x = 0; for k = 1, #s do x = (x + string.byte(s, k)) % 1000003 end; return mod.Name .. " bytes=" .. #s .. " soma=" .. x end
local s = game.ServerStorage.Urso_v2_Piloto.Poderes.PoderesUrso_Servidor
local c = game.ReplicatedStorage.Urso_v2_Lab.EfeitosUrso_Cliente
ins(s, "-- pedido do cliente: so o DONO do urso;", [=====[-- ================================================================== Etapa 2: RUGIDO PROTETOR (04/11)
-- Aprovado pelo usuario: o rugido concede VELOCIDADE, DEFESA e REGENERACAO ao URSO e ao TREINADOR (dono). Nao vale para
-- outros aliados. Numeros = LAB (provisorios). O servidor decide tudo; o cliente so mostra a onda e a aura.
--   * velocidade: treinador = Humanoid.WalkSpeed + delta (delta guardado e devolvido exatamente: outros bonus/penalidades
--     aplicados por outros sistemas durante o efeito ficam intactos); urso = atributo VelocidadeBonus_RugidoProtetor
--     (o urso ainda nao tem sistema de movimento no place);
--   * defesa: atributo DefesaBonus_RugidoProtetor; M.danoComDefesa(alvo, dano) aplica a soma dos DefesaBonus_* (teto 60%).
--     PENDENTE: nenhum sistema de dano do place le esse atributo ainda (integracao futura com o combate oficial);
--   * regeneracao GRADUAL (nunca cura instantanea): % da vida maxima por segundo, em ticks; nunca passa da vida maxima;
--     nao age em quem esta com vida 0 / incapacitado. Urso: atributos Vida/VidaMax (LAB; o urso nao tem Humanoid);
--   * renovar: novo rugido com o efeito ativo RENOVA a duracao (nao acumula delta nem soma bonus);
--   * remocao: fim da duracao, morte/incapacitacao do alvo, saida do jogador, personagem removido. Remove SO o deste poder.
M.LAB.RugidoProtetor = {
	recarga = 20.0, energia = 30, duracao = 10.0,
	alcanceTreinador = 40.0,      -- studs entre o urso e o treinador no instante do efeito
	velocidade = 0.20,            -- +20% de velocidade
	defesa = 0.25,                -- 25% menos dano (via M.danoComDefesa)
	regenPorSeg = 0.02,           -- 2% da vida maxima por segundo (10 s -> ate 20%)
	tick = 0.5,
	vidaUrsoLab = 600,            -- VidaMax de laboratorio do urso, se ainda nao houver
}
local ativos = {}                 -- [alvo] = {expira, delta, hum, cons}
M.ativos = ativos
local NOME = "RugidoProtetor"
local function removerBuff(alvo, motivo)
	local b = ativos[alvo]; if not b then return end
	ativos[alvo] = nil
	for _, c in ipairs(b.cons) do c:Disconnect() end
	if b.hum and b.hum.Parent then b.hum.WalkSpeed = math.max(0, b.hum.WalkSpeed - b.delta) end
	if alvo.Parent then alvo:SetAttribute("DefesaBonus_" .. NOME, nil); alvo:SetAttribute("VelocidadeBonus_" .. NOME, nil); alvo:SetAttribute("Buff_" .. NOME, nil) end
	registrar({ev = "rp_fim", alvo = alvo.Name, motivo = motivo})
	Efeitos:FireAllClients({tipo = NOME, fase = "fim", alvo = alvo})
end
M.removerBuff = removerBuff
local function aplicarBuff(alvo)
	local L = M.LAB.RugidoProtetor; local agora = workspace:GetServerTimeNow()
	local b = ativos[alvo]
	if b then b.expira = agora + L.duracao; registrar({ev = "rp_renovado", alvo = alvo.Name}); return "renovado" end
	b = {expira = agora + L.duracao, delta = 0, cons = {}}
	local hum = alvo:FindFirstChildOfClass("Humanoid")
	if hum then
		if hum.Health <= 0 then return "sem_vida" end
		b.hum = hum; b.delta = hum.WalkSpeed * L.velocidade; hum.WalkSpeed += b.delta
		table.insert(b.cons, hum.Died:Connect(function() removerBuff(alvo, "morte") end))
	else
		alvo:SetAttribute("VelocidadeBonus_" .. NOME, L.velocidade)
		if not alvo:GetAttribute("VidaMax") then alvo:SetAttribute("VidaMax", L.vidaUrsoLab); alvo:SetAttribute("Vida", L.vidaUrsoLab) end
	end
	table.insert(b.cons, alvo.AncestryChanged:Connect(function() if not alvo:IsDescendantOf(workspace) then removerBuff(alvo, "removido") end end))
	alvo:SetAttribute("DefesaBonus_" .. NOME, L.defesa); alvo:SetAttribute("Buff_" .. NOME, true)
	ativos[alvo] = b
	registrar({ev = "rp_aplicado", alvo = alvo.Name, delta = b.delta})
	return "aplicado"
end
-- dano com defesa (para os sistemas que vierem a usar; hoje so os testes)
function M.danoComDefesa(alvo, dano)
	local d = 0
	for k, v in pairs(alvo:GetAttributes()) do if string.sub(k, 1, 12) == "DefesaBonus_" and type(v) == "number" then d += v end end
	return dano * (1 - math.min(d, 0.6))
end
-- ticks de regeneracao e expiracao
local acum = 0
RS.Heartbeat:Connect(function(dt)
	acum += dt; local L = M.LAB.RugidoProtetor; if acum < L.tick then return end
	local passo = acum; acum = 0; local agora = workspace:GetServerTimeNow()
	for alvo, b in pairs(ativos) do
		if agora >= b.expira then removerBuff(alvo, "expirou")
		elseif b.hum then
			if b.hum.Health > 0 and b.hum.Health < b.hum.MaxHealth then b.hum.Health = math.min(b.hum.MaxHealth, b.hum.Health + b.hum.MaxHealth * L.regenPorSeg * passo) end
		else
			if alvo:GetAttribute("Incapacitado") then removerBuff(alvo, "incapacitado")
			else
				local v, mx = alvo:GetAttribute("Vida") or 0, alvo:GetAttribute("VidaMax") or L.vidaUrsoLab
				if v > 0 and v < mx then alvo:SetAttribute("Vida", math.min(mx, v + mx * L.regenPorSeg * passo)) end
			end
		end
	end
end)
Players.PlayerRemoving:Connect(function(plr)
	if plr.Character and ativos[plr.Character] then removerBuff(plr.Character, "desconexao") end
end)
function M.rugidoProtetor(urso, quem)
	local L = M.LAB.RugidoProtetor; local agora = workspace:GetServerTimeNow()
	local e = estado[urso] or {}; estado[urso] = e
	e.recRP = e.recRP or 0
	if urso:GetAttribute("Incapacitado") then registrar({ev = "recusado", motivo = "incapacitado"}); return false, "incapacitado" end
	if e.acao then registrar({ev = "recusado", motivo = "ocupado"}); return false, "ocupado" end
	if e.recRP > agora then registrar({ev = "recusado", motivo = "recarga"}); return false, "recarga" end
	local en = urso:GetAttribute("EnergiaLab") or 100
	if en < L.energia then registrar({ev = "recusado", motivo = "energia"}); return false, "energia" end
	urso:SetAttribute("EnergiaLab", en - L.energia)
	local f, kfs = faixa(urso, "Urso_RugidoProtetor")
	local tRug, tEf = kfs:GetAttribute("RugidoS") or 0.7, kfs:GetAttribute("EfeitoS") or 1.0
	local id = game:GetService("HttpService"):GenerateGUID(false)
	e.acao = NOME; e.faixa = f; e.recRP = agora + L.recarga; e.ataque = id
	f:Play(0.15); registrar({ev = "rp_inicio", id = id, quem = quem})
	local rugiu, feito = false, false
	local con; con = RS.Stepped:Connect(function()
		if feito then return end
		if not f.IsPlaying or e.ataque ~= id then feito = true; con:Disconnect(); registrar({ev = "rp_interrompido", id = id, tp = f.TimePosition}); return end
		if not rugiu and f.TimePosition >= tRug then rugiu = true; Efeitos:FireAllClients({tipo = NOME, fase = "rugido", urso = urso}) end
		if f.TimePosition >= tEf then
			feito = true; con:Disconnect()
			local alvos = {urso}; local res = {[urso.Name] = aplicarBuff(urso)}
			local dono = urso:GetAttribute("DonoUserId"); local plr = dono and Players:GetPlayerByUserId(dono)
			local ch = plr and plr.Character; local hr = ch and ch:FindFirstChild("HumanoidRootPart")
			if hr then
				local d = (hr.Position - urso:GetPivot().Position).Magnitude
				if d <= L.alcanceTreinador then res[ch.Name] = aplicarBuff(ch); table.insert(alvos, ch)
				else res[ch.Name] = string.format("fora_alcance(%.1f)", d) end
			end
			registrar({ev = "rp_efeito", id = id, tp = f.TimePosition, res = res})
			Efeitos:FireAllClients({tipo = NOME, fase = "efeito", urso = urso, alvos = alvos, duracao = L.duracao})
		end
	end)
	f.Stopped:Once(function() if e.ataque == id then e.acao = nil; e.faixa = nil end end)
	return true, id
end

]=====], true)
ins(s, '	if poder == "GolpeColossal" then M.golpeColossal(urso, plr.Name) end
', '	if poder == "RugidoProtetor" then M.rugidoProtetor(urso, plr.Name) end
', false)
ins(c, "function M.iniciar(remotos)
", [=====[-- ================================================================== Rugido Protetor (Etapa 2, 04/11) - so visual
-- Onda de choque dourado-esverdeada saindo do urso no pico do rugido + AURA discreta em cada alvo que recebeu os bonus
-- (urso e treinador): poucas particulas pequenas e um anel fino nos pes que acompanha o alvo. Nada esconde os
-- personagens (transparencia alta, sem Highlight, sem neblina). A aura sai quando o servidor avisa "fim" do bonus.
M.SOM_RUGIDO_PROTETOR = nil      -- rbxassetid do rugido protetor quando existir (PENDENTE)
M.VIS_RP = {cor = Color3.fromRGB(196, 214, 120), raioOnda = 40, durOnda = 0.9, particulas = 6}
local auras = {}                 -- [alvo] = {pecas, con}
local function pecaRP(nome)
	local p = Instance.new("Part"); p.Name = nome; p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false
	p.CastShadow = false; p.Material = Enum.Material.Neon; p.Color = M.VIS_RP.cor; p.Shape = Enum.PartType.Cylinder; return p
end
local function chaoSob(pos, ex)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = ex
	local h = workspace:Raycast(pos + Vector3.new(0, 1, 0), Vector3.new(0, -12, 0), rp); return h and h.Position or pos
end
local function tirarAura(alvo)
	local a = auras[alvo]; if not a then return end; auras[alvo] = nil
	if a.con then a.con:Disconnect() end
	for _, p in ipairs(a.pecas) do if p.Parent then TS:Create(p, TweenInfo.new(0.4), {Transparency = 1}):Play(); task.delay(0.45, function() p:Destroy() end) end end
	if a.emissor then a.emissor.Enabled = false; task.delay(1.5, function() if a.at then a.at:Destroy() end end) end
end
local function porAura(alvo, dur)
	tirarAura(alvo)
	local base = alvo:FindFirstChild("HumanoidRootPart") or alvo.PrimaryPart or alvo:FindFirstChildWhichIsA("BasePart", true)
	if not base then return end
	local anel = pecaRP("AnelRP"); anel.Transparency = 0.55
	local ext = alvo:GetExtentsSize(); local r = math.clamp(math.max(ext.X, ext.Z) * 0.6, 2.5, 7)
	anel.Size = Vector3.new(0.06, r * 2, r * 2); anel.Parent = pasta
	local at = Instance.new("Attachment"); at.Parent = base
	local pe = Instance.new("ParticleEmitter"); pe.Texture = "rbxasset://textures/particles/sparkles_main.dds"
	pe.Color = ColorSequence.new(M.VIS_RP.cor); pe.LightEmission = 0.5; pe.Size = NumberSequence.new(0.25, 0.05)
	pe.Transparency = NumberSequence.new(0.3, 1); pe.Lifetime = NumberRange.new(0.8, 1.4); pe.Rate = M.VIS_RP.particulas
	pe.Speed = NumberRange.new(1, 2); pe.SpreadAngle = Vector2.new(180, 180); pe.Parent = at
	local a = {pecas = {anel}, at = at, emissor = pe}
	a.con = RS.RenderStepped:Connect(function()
		if not alvo.Parent then tirarAura(alvo); return end
		local pos = chaoSob(alvo:GetPivot().Position, {alvo, pasta})
		anel.CFrame = CFrame.new(pos + Vector3.new(0, 0.05, 0)) * CFrame.Angles(0, 0, math.rad(90))
	end)
	auras[alvo] = a
	task.delay(dur + 2, function() if auras[alvo] == a then tirarAura(alvo) end end)        -- seguranca: nunca fica para sempre
end
function M.rugidoProtetorEfx(d)
	if d.fase == "rugido" and d.urso then
		local cab = d.urso:FindFirstChild("Cabeca", true); som(M.SOM_RUGIDO_PROTETOR, cab and cab.TransformedWorldCFrame.Position or d.urso:GetPivot().Position)
	elseif d.fase == "efeito" and d.urso then
		local c = chaoSob(d.urso:GetPivot().Position, {d.urso, pasta})
		local onda = pecaRP("OndaRP"); onda.Transparency = 0.35; onda.Size = Vector3.new(0.08, 4, 4)
		onda.CFrame = CFrame.new(c + Vector3.new(0, 0.3, 0)) * CFrame.Angles(0, 0, math.rad(90)); onda.Parent = pasta
		local D = M.VIS_RP.raioOnda * 2
		TS:Create(onda, TweenInfo.new(M.VIS_RP.durOnda, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = Vector3.new(0.08, D, D), Transparency = 1}):Play()
		task.delay(M.VIS_RP.durOnda + 0.1, function() onda:Destroy() end)
		for _, alvo in ipairs(d.alvos or {}) do porAura(alvo, d.duracao or 10) end
		M.ultimoRP = {alvos = #(d.alvos or {}), t = os.clock()}
	elseif d.fase == "fim" and d.alvo then
		tirarAura(d.alvo)
	end
end
M.auras = auras
]=====], true)
ins(c, '		if d.tipo ~= "GolpeColossal" then return end
', '		if d.tipo == "RugidoProtetor" then M.rugidoProtetorEfx(d); return end
', true)
return soma(s) .. "
" .. soma(c)
