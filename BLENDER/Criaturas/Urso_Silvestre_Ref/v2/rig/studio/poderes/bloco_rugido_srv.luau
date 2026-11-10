-- ================================================================== Etapa 2: RUGIDO PROTETOR (04/11)
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

