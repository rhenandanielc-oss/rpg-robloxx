-- ================================================================== Etapa 4: FORTALEZA VIVA (05/11)
-- Decisoes do usuario (05/11): escudo em area para o urso e o treinador, com resistencia PROPRIA (nao e bonus de defesa
-- e nao transfere dano ao HP do urso). Numeros = LAB. O SERVIDOR decide tudo:
--   * v2 (05/11, "escudo em volta de todo o corpo, ate no ar ... 50% a mais ... 3-5 s para se formar"): area = DOMO
--     (meia esfera) de raio L.raio centrado no pivo do urso; forma-se aos poucos em L.formacao s: a reserva cresce de 0 ao
--     maximo nesse tempo (absorve so o que ja formou e nao quebra enquanto forma); a duracao conta depois de formado.
--   * area: domo de raio L.raio centrado no urso, que ACOMPANHA o urso (o urso fica -50%: atributo
--     VelocidadeBonus_FortalezaViva; o urso ainda nao tem sistema de movimento no place). Sem Carga nem Golpe durante;
--   * protege quem da dupla (urso e treinador) estiver DENTRO no instante do golpe;
--   * golpe vindo de FORA (origem fora do cilindro ou desconhecida): a reserva compartilhada absorve; o golpe que quebra
--     gasta o resto e o EXCEDENTE passa ao alvo (nunca ao HP do urso por transferencia);
--   * golpe de atacante DENTRO da area: passa com defesa de 75% (sem gastar a reserva);
--   * dura L.duracao ou ate quebrar; recarga conta a partir do fim; reaplicar ativo = recusado (nao renova nem acumula);
--   * regeneracao de vida (Rugido) NAO recarrega a reserva; controle (queda/lancamento) vindo de fora: PENDENTE (nao bloqueia).
-- Interface de laboratorio: M.danoRecebido(alvo, dano, origemPos) -> dano aplicado. O combate oficial do place ainda nao
-- chama esta funcao (integracao com arquivo compartilhado: PENDENTE, pedir autorizacao).
M.LAB.FortalezaViva = {
	recarga = 25.0, energia = 35, duracao = 8.0,
	raio = 18.0,                        -- studs: domo (meia esfera) em volta do pivo do urso (v1: cilindro 12 x 10)
	formacao = 4.0,                     -- s: o domo se forma aos poucos (pedido: 3-5 s)
	reserva = 600,                      -- pontos de dano absorvidos (compartilhados pelos dois); 05/11 dobrado a pedido (era 300). LAB
	defesaDentro = 0.75,                -- golpe de atacante dentro da area: -75%
	lentidao = 0.50,                    -- urso -50% de velocidade
}
local fortes = {}                       -- [urso] = {reserva, max, expira, id, loop}
M.fortes = fortes
local function donoChar(urso)
	local d = urso:GetAttribute("DonoUserId"); local p = d and Players:GetPlayerByUserId(d); return p and p.Character
end
local function dentroArea(urso, pos)
	local L = M.LAB.FortalezaViva; local c = urso:GetPivot().Position; local d = pos - c
	return d.Magnitude <= L.raio and d.Y >= -3
end
M.dentroFortaleza = dentroArea
local function fimFortaleza(urso, motivo)
	local f = fortes[urso]; if not f then return end
	fortes[urso] = nil
	local L = M.LAB.FortalezaViva; local e = estado[urso] or {}; estado[urso] = e
	e.recFV = workspace:GetServerTimeNow() + L.recarga
	if e.acao == "FortalezaViva" then e.acao = nil; e.faixa = nil end
	if urso.Parent then
		urso:SetAttribute("Fortaleza_Reserva", nil); urso:SetAttribute("Fortaleza_Ate", nil); urso:SetAttribute("VelocidadeBonus_FortalezaViva", nil)
		if f.loop then f.loop:Stop(0.2) end
		if motivo ~= "removido" then pcall(function() faixa(urso, "Urso_FortalezaFim"):Play(0.15) end) end
	end
	registrar({ev = "fv_fim", id = f.id, motivo = motivo, reserva = f.reserva})
	Efeitos:FireAllClients({tipo = "FortalezaViva", fase = motivo == "quebrou" and "quebra" or "fim", urso = urso, motivo = motivo})
end
M.fimFortaleza = fimFortaleza
function M.fortalezaViva(urso, quem)
	local L = M.LAB.FortalezaViva; local agora = workspace:GetServerTimeNow()
	local e = estado[urso] or {}; estado[urso] = e
	e.recFV = e.recFV or 0
	if urso:GetAttribute("Incapacitado") then registrar({ev = "recusado", motivo = "incapacitado"}); return false, "incapacitado" end
	if fortes[urso] then registrar({ev = "recusado", motivo = "fortaleza_ativa"}); return false, "fortaleza_ativa" end
	if e.acao then registrar({ev = "recusado", motivo = "ocupado"}); return false, "ocupado" end
	if e.recFV > agora then registrar({ev = "recusado", motivo = "recarga"}); return false, "recarga" end
	local en = urso:GetAttribute("EnergiaLab") or 100
	if en < L.energia then registrar({ev = "recusado", motivo = "energia"}); return false, "energia" end
	urso:SetAttribute("EnergiaLab", en - L.energia)
	local f, kfs = faixa(urso, "Urso_FortalezaInicio")
	local tAt = kfs:GetAttribute("AtivarS") or 0.8
	local id = game:GetService("HttpService"):GenerateGUID(false)
	e.acao = "FortalezaViva"; e.faixa = f; e.ataque = id
	f:Play(0.15); registrar({ev = "fv_inicio", id = id, quem = quem})
	Efeitos:FireAllClients({tipo = "FortalezaViva", fase = "inicio", urso = urso})
	local t0 = os.clock(); local ativou = false
	local con; con = RS.Heartbeat:Connect(function()
		if ativou then
			local fv = fortes[urso]
			if not fv or fv.id ~= id then con:Disconnect(); return end
			if not urso:IsDescendantOf(workspace) then con:Disconnect(); fimFortaleza(urso, "removido"); return end
			if urso:GetAttribute("Incapacitado") then con:Disconnect(); fimFortaleza(urso, "incapacitado"); return end
			local agoraF = workspace:GetServerTimeNow()
			if not fv.formado then
				local k = math.min(1, (agoraF - fv.forma0) / L.formacao)
				fv.reserva = math.max(0, fv.max * k - fv.gasto)
				if k >= 1 then
					fv.formado = true; fv.expira = agoraF + L.duracao; urso:SetAttribute("Fortaleza_Ate", fv.expira)
					registrar({ev = "fv_formado", id = id, reserva = fv.reserva})
					Efeitos:FireAllClients({tipo = "FortalezaViva", fase = "formado", urso = urso, reserva = fv.reserva, max = fv.max, duracao = L.duracao})
					if fv.reserva <= 0 then con:Disconnect(); fimFortaleza(urso, "quebrou"); return end
				end
				if not fv.ultAttr or agoraF - fv.ultAttr > 0.25 then fv.ultAttr = agoraF; urso:SetAttribute("Fortaleza_Reserva", math.floor(fv.reserva)) end
			elseif agoraF >= fv.expira then con:Disconnect(); fimFortaleza(urso, "expirou"); return end
			-- terminou a animacao de inicio: fica na postura firmada (loop)
			if e.faixa == f and f.Length > 0 and not f.IsPlaying and not fv.loop then
				fv.loop = faixa(urso, "Urso_FortalezaParado"); fv.loop.Looped = true; fv.loop:Play(0.2)
				if e.ataque == id then e.acao = nil; e.faixa = nil end
			end
			return
		end
		if e.ataque ~= id or not urso:IsDescendantOf(workspace) or urso:GetAttribute("Incapacitado") then
			con:Disconnect(); f:Stop(0.15); if e.ataque == id then e.acao = nil; e.faixa = nil end
			registrar({ev = "fv_interrompido", id = id}); return
		end
		if (f.Length > 0 and f.TimePosition >= tAt) or os.clock() - t0 >= tAt + 1.2 then     -- 1o uso: espera o clipe carregar (Length 0)
			ativou = true
			local agora2 = workspace:GetServerTimeNow()
			fortes[urso] = {reserva = 0, max = L.reserva, gasto = 0, forma0 = agora2, formado = false, expira = agora2 + L.formacao + L.duracao, id = id}
			urso:SetAttribute("Fortaleza_Reserva", 0); urso:SetAttribute("Fortaleza_Ate", agora2 + L.formacao + L.duracao)
			urso:SetAttribute("VelocidadeBonus_FortalezaViva", -L.lentidao)
			registrar({ev = "fv_ativou", id = id, tp = math.floor(f.TimePosition * 100 + 0.5) / 100})
			Efeitos:FireAllClients({tipo = "FortalezaViva", fase = "ativar", urso = urso, raio = L.raio, max = L.reserva, formacao = L.formacao, duracao = L.duracao})
		end
	end)
	return true, id
end
-- dano de laboratorio: escudo (se o alvo for do par protegido e estiver dentro) -> defesa (DefesaBonus_*) -> vida
function M.danoRecebido(alvo, dano, origemPos)
	local L = M.LAB.FortalezaViva; local det = "normal"
	local pAlvo = alvo:IsA("Model") and alvo:GetPivot().Position
	for urso, fv in pairs(fortes) do
		if (alvo == urso or alvo == donoChar(urso)) and pAlvo and dentroArea(urso, pAlvo) then
			if typeof(origemPos) == "Vector3" and dentroArea(urso, origemPos) then
				dano = dano * (1 - L.defesaDentro); det = "dentro"
			else
				local abs_ = math.min(dano, fv.reserva); fv.reserva -= abs_; fv.gasto += abs_; dano -= abs_; det = fv.formado and "absorvido" or "absorvido_formando"
				urso:SetAttribute("Fortaleza_Reserva", math.floor(fv.reserva))
				if abs_ > 0 then
					Efeitos:FireAllClients({tipo = "FortalezaViva", fase = "golpe", urso = urso, reserva = fv.reserva, max = fv.max,
						pos = typeof(origemPos) == "Vector3" and origemPos or nil, alvoPos = pAlvo})
				end
				if fv.formado and fv.reserva <= 0 then det = "quebrou"; fimFortaleza(urso, "quebrou") end      -- formando: nao quebra
			end
			break
		end
	end
	dano = M.danoComDefesa(alvo, dano)
	if dano > 0 then
		local h = alvo:FindFirstChildOfClass("Humanoid")
		if h then h:TakeDamage(dano)
		elseif alvo:GetAttribute("Vida") then alvo:SetAttribute("Vida", math.max(0, alvo:GetAttribute("Vida") - dano)) end
	end
	registrar({ev = "fv_dano", alvo = alvo.Name, det = det, aplicado = math.floor(dano * 10 + 0.5) / 10})
	return dano, det
end
