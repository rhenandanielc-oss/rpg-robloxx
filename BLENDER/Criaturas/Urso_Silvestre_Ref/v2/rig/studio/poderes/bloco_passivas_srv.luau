-- ================================================================== PASSIVAS (05/11) - escolhidas pelo usuario
-- "Furia do Protetor, porem 30% de velocidade" e "Faro do Protetor". Numeros = LAB. O SERVIDOR decide tudo:
-- FURIA DO PROTETOR: quando o TREINADOR fica com vida <= limiar (30%) estando perto do urso (<= alcance), o urso entra em
--   furia por L.duracao: +30% de velocidade (atributo VelocidadeBonus_FuriaProtetor) e +15% de forca
--   (ForcaBonus_FuriaProtetor, usado no dano do Golpe Colossal por M.forcaMult). Recarga L.recarga a partir do inicio;
--   nao renova durante; a soma de bonus de velocidade do urso tem teto (M.velocidadeBonus, teto 0,5); termina cedo se o
--   urso for incapacitado/removido. O urso ainda nao tem sistema de movimento no place: o bonus fica no atributo.
-- Ursos considerados: os marcados com a tag "UrsoLab" (o piloto do laboratorio).
-- FARO DO PROTETOR: a cada L.intervalo, o servidor procura inimigos ESCONDIDOS a ate L.raio do urso: invisiveis
--   (PassoInvisivel ativo, do Passo Sombrio), furtivos (atributo Furtivo) ou sem linha de visada do treinador (atras de
--   parede/terreno). Achou: marca para o TREINADOR (so o cliente dele) por L.marca s e entra em recarga. Os atributos de
--   invisibilidade so sao LIDOS (nada aqui muda outros sistemas). Inimigos: outros jogadores (se PvP), alvos de teste e
--   modelos com PassoInvisivel (dragoes).
M.LAB.FuriaProtetor = {limiar = 0.30, alcance = 20.0, duracao = 6.0, recarga = 30.0, velocidade = 0.30, forca = 0.15}
M.LAB.FaroProtetor = {raio = 25.0, intervalo = 0.5, marca = 3.0, recarga = 15.0}
local function somaAttr(m, prefixo)
	local s = 0
	for k, v in pairs(m:GetAttributes()) do if string.sub(k, 1, #prefixo) == prefixo and type(v) == "number" then s += v end end
	return s
end
function M.forcaMult(urso) return 1 + math.max(0, somaAttr(urso, "ForcaBonus_")) end
function M.velocidadeBonus(urso) return math.clamp(somaAttr(urso, "VelocidadeBonus_"), -0.9, 0.5) end
local function dono(urso) local d = urso:GetAttribute("DonoUserId"); return d and Players:GetPlayerByUserId(d) end
local furias = {}                       -- [urso] = {fim, id}
M.furias = furias
local function fimFuria(urso, motivo)
	local f = furias[urso]; if not f then return end; furias[urso] = nil
	if urso.Parent then urso:SetAttribute("VelocidadeBonus_FuriaProtetor", nil); urso:SetAttribute("ForcaBonus_FuriaProtetor", nil); urso:SetAttribute("Furia_Ate", nil) end
	registrar({ev = "furia_fim", motivo = motivo})
	Efeitos:FireAllClients({tipo = "FuriaProtetor", fase = "fim", urso = urso})
end
local function iniciarFuria(urso, plr)
	local L = M.LAB.FuriaProtetor; local e = estado[urso] or {}; estado[urso] = e
	local agora = workspace:GetServerTimeNow()
	if furias[urso] or (e.recFuria or 0) > agora or urso:GetAttribute("Incapacitado") then return false end
	e.recFuria = agora + L.recarga
	furias[urso] = {fim = agora + L.duracao}
	urso:SetAttribute("VelocidadeBonus_FuriaProtetor", L.velocidade); urso:SetAttribute("ForcaBonus_FuriaProtetor", L.forca)
	urso:SetAttribute("Furia_Ate", agora + L.duracao)
	registrar({ev = "furia_inicio", treinador = plr.Name, velocidade = M.velocidadeBonus(urso), forca = M.forcaMult(urso)})
	Efeitos:FireAllClients({tipo = "FuriaProtetor", fase = "inicio", urso = urso, dur = L.duracao})
	return true
end
M.iniciarFuria = iniciarFuria
-- gatilho: vida do treinador (HealthChanged no servidor) + distancia; ligado quando o personagem aparece
local ligados = {}
local function ligarTreinador(urso, plr, ch)
	local h = ch:FindFirstChildOfClass("Humanoid"); if not h then return end
	local chave = ch; if ligados[chave] then return end
	ligados[chave] = h.HealthChanged:Connect(function(v)
		if v <= 0 or v > h.MaxHealth * M.LAB.FuriaProtetor.limiar then return end
		if not urso:IsDescendantOf(workspace) or urso:GetAttribute("DonoUserId") ~= plr.UserId then return end
		local r = ch:FindFirstChild("HumanoidRootPart"); if not r then return end
		if (r.Position - urso:GetPivot().Position).Magnitude <= M.LAB.FuriaProtetor.alcance then iniciarFuria(urso, plr) end
	end)
	ch.AncestryChanged:Connect(function() if not ch:IsDescendantOf(game) and ligados[chave] then ligados[chave]:Disconnect(); ligados[chave] = nil end end)
end
-- faro
local function escondido(m, olho, rp)
	local agora = workspace:GetServerTimeNow()
	local inv = m:GetAttribute("PassoInvisivel")
	if typeof(inv) == "number" and inv > agora then return "invisivel" end
	if m:GetAttribute("Furtivo") then return "furtivo" end
	local r = raiz(m); if not r or not olho then return nil end
	local hit = workspace:Raycast(olho, r.Position - olho, rp)
	if hit and not hit.Instance:IsDescendantOf(m) then return "sem_visada" end
	return nil
end
local function inimigosPerto(urso, plr, c, raio)
	local t = {}
	local pvp = workspace:GetAttribute("PvPAtivo")
	for _, p in ipairs(Players:GetPlayers()) do
		if p ~= plr and pvp and p.Character then table.insert(t, p.Character) end
	end
	for _, m in ipairs(CS:GetTagged("AlvoTesteUrso")) do table.insert(t, m) end
	for _, m in ipairs(workspace:GetChildren()) do
		if m:IsA("Model") and m ~= urso and m:GetAttribute("PassoInvisivel") ~= nil then table.insert(t, m) end      -- so filhos diretos (sem varredura funda)
	end
	local perto, visto = {}, {}
	for _, m in ipairs(t) do
		if m.Parent and m ~= urso and not visto[m] and (not plr.Character or m ~= plr.Character) then
			visto[m] = true
			local ok, pos = pcall(function() return m:GetPivot().Position end)
			if ok and (pos - c).Magnitude <= raio then table.insert(perto, m) end
		end
	end
	return perto
end
local acumFaro = 0
RS.Heartbeat:Connect(function(dt)
	acumFaro += dt; local LF = M.LAB.FaroProtetor; if acumFaro < LF.intervalo then return end; acumFaro = 0
	local agora = workspace:GetServerTimeNow()
	-- furia: fim por tempo / incapacitado
	for urso, f in pairs(furias) do
		if not urso:IsDescendantOf(workspace) then fimFuria(urso, "removido")
		elseif urso:GetAttribute("Incapacitado") then fimFuria(urso, "incapacitado")
		elseif agora >= f.fim then fimFuria(urso, "expirou") end
	end
	-- faro + ligacao do gatilho da furia, por urso de laboratorio
	for _, urso in ipairs(CS:GetTagged("UrsoLab")) do
		local plr = dono(urso); local ch = plr and plr.Character
		if ch then ligarTreinador(urso, plr, ch) end
		local e = estado[urso] or {}; estado[urso] = e
		if plr and ch and not urso:GetAttribute("Incapacitado") and (e.recFaro or 0) <= agora then
			local c = urso:GetPivot().Position
			local cab = ch:FindFirstChild("Head"); local olho = cab and cab.Position
			local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.RespectCanCollide = true
			rp.FilterDescendantsInstances = {urso, ch}
			local achados, motivos = {}, {}
			for _, m in ipairs(inimigosPerto(urso, plr, c, LF.raio)) do
				local porque = escondido(m, olho, rp)
				if porque then table.insert(achados, m); table.insert(motivos, m.Name .. ":" .. porque) end
			end
			if #achados > 0 then
				e.recFaro = agora + LF.recarga
				registrar({ev = "faro", alvos = table.concat(motivos, ",")})
				pcall(function() Efeitos:FireClient(plr, {tipo = "FaroProtetor", fase = "marca", urso = urso, alvos = achados, dur = LF.marca}) end)
				Efeitos:FireAllClients({tipo = "FaroProtetor", fase = "farejou", urso = urso})
			end
		end
	end
end)
