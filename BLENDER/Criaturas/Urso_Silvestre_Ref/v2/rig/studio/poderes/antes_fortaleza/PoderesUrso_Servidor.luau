-- PoderesUrso_Servidor (ModuleScript em ServerStorage.Urso_v2_Piloto.Poderes) - LABORATORIO ISOLADO do Urso Silvestre v2.
-- Etapa 1: GOLPE COLOSSAL. O SERVIDOR decide tudo: dono, estado, recarga, energia, ponto de impacto, alvos e dano.
-- O cliente so pede (RemoteEvent Pedido) e mostra efeitos (RemoteEvent Efeitos). Nada aqui e regra oficial:
-- TODOS os numeros sao PARAMETROS DE LABORATORIO PROVISORIOS (tabela LAB). Nao usa nem altera os sistemas dos dragoes.
-- Elegibilidade de alvo (LAB, ate existir o sistema oficial de PvP/aliancas no place):
--   * boneco de teste com atributo AlvoTesteUrso = true;
--   * jogador so com workspace.PvPAtivo == true (mesmo atributo de laboratorio dos dragoes), nunca o dono do urso,
--     nunca quem tem AliadoDe == dono, ninguem dentro de parte com tag ZonaSegura.
local RS = game:GetService("RunService")
local Players = game:GetService("Players")
local CS = game:GetService("CollectionService")
local M = {}

M.LAB = {               -- PROVISORIO (nao aprovado): ajustar so com decisao do usuario
	GolpeColossal = {
		recarga = 8.0,          -- s
		energia = 20,           -- custo (energia do urso em atributo EnergiaLab; sem sistema oficial de energia no place)
		raio = 76.0,            -- (2x em 04/11: "aumente 2x mais o alcance"; era 38) studs, horizontal, a partir do CENTRO DO CORPO (v5, 04/11, pedido do usuario: "amplie o raio" -
		                        -- acompanha as rachaduras em volta do corpo inteiro; antes 14 a partir do ponto das patas)
		alturaMax = 4.0,        -- studs: diferenca vertical maxima entre o chao do impacto e o pe do alvo
		dano = 40,              -- dano fixo de laboratorio (sem queda com a distancia nesta versao)
		janelaAcerto = 0.10,    -- s: o dano e aplicado uma unica vez dentro desta janela apos o contato
		alcanceRaioChao = 6.0,  -- studs: raycast do ponto entre as patas para baixo
	},
}

local pasta = game.ServerStorage:WaitForChild("Urso_v2_Piloto")
local remotos = game.ReplicatedStorage:FindFirstChild("Urso_v2_Lab") or Instance.new("Folder")
remotos.Name = "Urso_v2_Lab"; remotos.Parent = game.ReplicatedStorage
local function remoto(n) local r = remotos:FindFirstChild(n) or Instance.new("RemoteEvent"); r.Name = n; r.Parent = remotos; return r end
local Pedido, Efeitos = remoto("Pedido"), remoto("Efeitos")

local ACP = game:GetService("AnimationClipProvider")
local estado = {}           -- [urso] = {acao, faixa, recargaAte, ataque}
local log = {}              -- registro do laboratorio (testes leem daqui)
M.log = log
local function registrar(t) t.t = workspace:GetServerTimeNow(); table.insert(log, t); if #log > 400 then table.remove(log, 1) end end

local function raiz(mod) return mod and (mod:FindFirstChild("HumanoidRootPart") or mod.PrimaryPart) end
local function emZonaSegura(pos)
	for _, z in ipairs(CS:GetTagged("ZonaSegura")) do
		if z:IsA("BasePart") then
			local p = z.CFrame:PointToObjectSpace(pos); local s = z.Size / 2
			if math.abs(p.X) <= s.X and math.abs(p.Y) <= s.Y and math.abs(p.Z) <= s.Z then return true end
		end
	end
	return false
end
local function elegivel(urso, mod)
	if mod == urso then return false, "proprio" end
	local h = mod:FindFirstChildOfClass("Humanoid"); if not (h and h.Health > 0) then return false, "sem_vida" end
	local r = raiz(mod); if not r then return false, "sem_raiz" end
	local dono = urso:GetAttribute("DonoUserId")
	local plr = Players:GetPlayerFromCharacter(mod)
	if plr then
		if dono and plr.UserId == dono then return false, "dono" end
		if workspace:GetAttribute("PvPAtivo") ~= true then return false, "pvp_desligado" end
	elseif not mod:GetAttribute("AlvoTesteUrso") then return false, "nao_alvo" end
	if dono and mod:GetAttribute("AliadoDe") == dono then return false, "aliado" end
	if emZonaSegura(r.Position) then return false, "zona_segura" end
	return true
end

local function animator(urso)
	local ac = urso:FindFirstChildOfClass("AnimationController") or Instance.new("AnimationController", urso)
	return ac:FindFirstChildOfClass("Animator") or Instance.new("Animator", ac)
end
local idCache = {}
local function faixa(urso, nome)
	local kfs = pasta.Animacoes:FindFirstChild(nome); assert(kfs, "KFS ausente: " .. nome)
	idCache[nome] = idCache[nome] or ACP:RegisterAnimationClip(kfs)
	local a = Instance.new("Animation"); a.AnimationId = idCache[nome]
	local f = animator(urso):LoadAnimation(a); f.Priority = Enum.AnimationPriority.Action2
	return f, kfs
end

-- ponto de impacto: meio das duas patas dianteiras (ossos MaoE/MaoD), raycast PARA BAIXO a partir de pouco acima
-- (2,5 studs): acha o chao sob as patas, nunca um teto ou outro andar acima.
local function pontoImpacto(urso)
	local function osso(n) local b = urso:FindFirstChild(n, true); return b and b.TransformedWorldCFrame.Position end
	local a, b = osso("MaoE"), osso("MaoD"); if not (a and b) then return nil end
	local c = (a + b) / 2
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	local excl = {urso}; for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(excl, p.Character) end end
	for _, m in ipairs(CS:GetTagged("AlvoTesteUrso")) do table.insert(excl, m) end
	rp.FilterDescendantsInstances = excl
	local r = workspace:Raycast(c + Vector3.new(0, 2.5, 0), Vector3.new(0, -M.LAB.GolpeColossal.alcanceRaioChao, 0), rp)
	return r and r.Position or nil, r and r.Normal or nil, rp
end

-- alvos (v5: medidos do CENTRO do corpo, nao das patas): horizontal <= raio, |altura| <= alturaMax, linha de visada livre (do chao +1,5 ate o centro do alvo, ignorando
-- personagens): parede/obstaculo bloqueia. Cada MODELO conta uma vez (nao por parte).
local function alvos(urso, P, rp)
	local piv = urso:GetPivot().Position; local C = Vector3.new(piv.X, P.Y, piv.Z)     -- centro do corpo, na altura do chao
	local L = M.LAB.GolpeColossal; local lista, motivos = {}, {}
	local vistos = {}
	for _, h in ipairs(workspace:GetDescendants()) do
		if h:IsA("Humanoid") then
			local mod = h.Parent
			if mod and not vistos[mod] then
				vistos[mod] = true
				local ok, por = elegivel(urso, mod)
				local r = raiz(mod)
				if ok then
					local pe = r.Position - Vector3.new(0, (h.HipHeight or 0) + r.Size.Y / 2, 0)
					local dh = Vector3.new(r.Position.X - C.X, 0, r.Position.Z - C.Z).Magnitude
					local dy = math.abs(pe.Y - P.Y)
					if dh > L.raio then ok, por = false, string.format("fora_raio(%.1f)", dh)
					elseif dy > L.alturaMax then ok, por = false, string.format("altura(%.1f)", dy)
					else
						local o = C + Vector3.new(0, 1.5, 0)
						local hit = workspace:Raycast(o, r.Position - o, rp)
						if hit and not hit.Instance:IsDescendantOf(mod) then ok, por = false, "obstaculo(" .. hit.Instance.Name .. ")" end
					end
				end
				if ok then table.insert(lista, mod) end
				motivos[mod.Name] = ok and "ACERTO" or por
			end
		end
	end
	return lista, motivos
end

function M.golpeColossal(urso, quem)
	local L = M.LAB.GolpeColossal; local agora = workspace:GetServerTimeNow()
	local e = estado[urso] or {}; estado[urso] = e
	if urso:GetAttribute("Incapacitado") then registrar({ev = "recusado", motivo = "incapacitado"}); return false, "incapacitado" end
	if e.acao then registrar({ev = "recusado", motivo = "ocupado"}); return false, "ocupado" end
	if (e.recargaAte or 0) > agora then registrar({ev = "recusado", motivo = "recarga"}); return false, "recarga" end
	local en = urso:GetAttribute("EnergiaLab") or 100
	if en < L.energia then registrar({ev = "recusado", motivo = "energia"}); return false, "energia" end
	urso:SetAttribute("EnergiaLab", en - L.energia)
	local f, kfs = faixa(urso, "Urso_GolpeColossal")
	local tImp = kfs:GetAttribute("ImpactoS") or 1.10
	local tRug = kfs:GetAttribute("RugidoS")                 -- v2: rugido antes de bater (so apresentacao: som/efeito)
	local id = game:GetService("HttpService"):GenerateGUID(false)
	e.acao = "GolpeColossal"; e.faixa = f; e.recargaAte = agora + L.recarga; e.ataque = id; e.rugiu = false
	f:Play(0.12); registrar({ev = "inicio", id = id, quem = quem})
	Efeitos:FireAllClients({tipo = "GolpeColossal", fase = "inicio", urso = urso, id = id})
	local feito = false
	local con; con = RS.Stepped:Connect(function()
		if feito then return end
		if not f.IsPlaying or e.ataque ~= id then           -- interrompido antes do contato: sem dano e sem efeito
			feito = true; con:Disconnect(); registrar({ev = "interrompido", id = id, tp = f.TimePosition}); return
		end
		if tRug and not e.rugiu and f.TimePosition >= tRug then
			e.rugiu = true; Efeitos:FireAllClients({tipo = "GolpeColossal", fase = "rugido", urso = urso, id = id})
		end
		if f.TimePosition >= tImp then
			feito = true; con:Disconnect()
			if f.TimePosition > tImp + L.janelaAcerto / math.max(f.Speed, 0.05) + 0.05 then
				registrar({ev = "janela_perdida", id = id, tp = f.TimePosition}); return
			end
			local P, N, rp = pontoImpacto(urso)
			if not P then registrar({ev = "sem_chao", id = id}); return end
			local lista, motivos = alvos(urso, P, rp)
			local feridos = {}
			for _, mod in ipairs(lista) do
				local h = mod:FindFirstChildOfClass("Humanoid")
				if h and mod:GetAttribute("UltimoAtaqueUrso") ~= id then       -- trava por ataque: nunca 2x no mesmo modelo
					mod:SetAttribute("UltimoAtaqueUrso", id); h:TakeDamage(L.dano); table.insert(feridos, mod.Name)
				end
			end
			registrar({ev = "impacto", id = id, tp = f.TimePosition, velocidade = f.Speed, pos = P, feridos = feridos, motivos = motivos})
			Efeitos:FireAllClients({tipo = "GolpeColossal", fase = "impacto", urso = urso, id = id, pos = P, normal = N, raio = L.raio})
		end
	end)
	f.Stopped:Once(function() if e.ataque == id then e.acao = nil; e.faixa = nil end end)
	return true, id
end

function M.interromper(urso)                                -- ex.: atordoado/derrotado; o servidor chama
	local e = estado[urso]; if e and e.faixa then e.ataque = nil; e.faixa:Stop(0.15); e.acao = nil end
end

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

-- ================================================================== Etapa 3: CARGA SELVAGEM (04/11)
-- Proposta aprovada pelo usuario (04/11): o urso corre rapido ate o alvo; ao atingir um jogador elegivel, DERRUBA-O no
-- chao e aplica atordoamento temporario. Numeros = LAB (provisorios). O SERVIDOR decide tudo:
--   * alvo: o treinador indica um alvo; o servidor confere (elegivel, distancia, cone a frente, linha de visada). Sem
--     alvo valido = carga reta para a frente. Alvo perto demais (< distMin) = recusado (sem custo);
--   * trajeto: o servidor move o urso PASSO A PASSO (Heartbeat), com a velocidade do proprio clipe (perfil por quadro);
--     a cada passo: Blockcast do peito na direcao do movimento (parede/obstaculo = para) e raycast do chao (o urso
--     acompanha o terreno; degrau alto demais conta como parede). Nunca teleporta ate o alvo e nao usa Touched;
--   * curva limitada (graus/s); PERDE o alvo se ele sair do cone, passar de perdaDist, ficar atras de parede ou deixar
--     de ser elegivel -> segue reto ate o fim;
--   * impacto UNICO: o primeiro alvo elegivel no caminho (o travado ou outro que entre na frente) dispara o clipe
--     CargaImpacto; no instante ImpactoS o servidor confere de novo a distancia e so entao derruba;
--   * queda: PlatformStand (o corpo cai de verdade, juntas intactas, sem ragdoll) + giro de tombo, movimento e pulo
--     bloqueados por DELTA guardado (devolvido exatamente). O SERVIDOR libera sozinho no prazo, mesmo se o cliente falhar;
--   * repeticao: nao acumula (ja derrubado = ignora) e, depois de levantar, imunidade a nova queda por L.imunidade;
--   * dano: PENDENTE (0). LANCAMENTO (05/11, aprovado: "Aprovar lancamento"): alvo PEQUENO (altura <= alturaPequeno) voa
--     em arco para a frente (lancDist, conferido no servidor contra parede e barranco); alvo grande so cai no lugar.
M.LAB.CargaSelvagem = {
	recarga = 12.0, energia = 25,
	distMin = 8.0, distMax = 45.0,      -- studs: alvo valido entre estes limites; a carga anda no maximo distMax
	tempoMax = 3.0,                     -- s: seguranca (fim da carga mesmo sem acerto)
	velocidade = 29.41,                 -- studs/s na corrida (a do clipe: patas sem escorregar). Parametro tecnico
	escalaVel = 1.0,                    -- LAB: multiplica a velocidade e a do clipe juntos (1,7 ~ 50 studs/s)
	curva = 90.0,                       -- graus/s
	cone = 35.0,                        -- graus para cada lado (70 no total)
	perdaDist = 55.0,
	raioImpacto = 3.5,                  -- studs: meia largura da faixa de impacto a frente do urso
	alturaImpacto = 5.0,
	frente = 5.5,                       -- studs: do pivo ate o peito/ombro (frente do urso, -Z)
	degrauMax = 2.5,                    -- studs: subida maxima por passo antes de contar como parede
	atordoamento = 1.5, levantar = 0.6, imunidade = 6.0,
	giroTombo = 7.0,                    -- rad/s: so o tombo (nao e empurrao)
	alturaPequeno = 6.5,                -- studs: altura do modelo ate a qual o alvo e lancado (personagem R15 ~5)
	lancDist = 12.0, lancAlt = 3.5,     -- studs: distancia horizontal e altura do arco (proposta aprovada 10-14). LAB
	dano = 0,                           -- PENDENTE
}
local quedas = {}                       -- [modelo] = {hum, ate, fimAte, dws, djp, campo, cons, plr}
M.quedas = quedas
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
local function excluirChars(urso)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	local ex = {urso}; for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(ex, p.Character) end end
	for _, m in ipairs(CS:GetTagged("AlvoTesteUrso")) do table.insert(ex, m) end
	local fx = workspace:FindFirstChild("Urso_v2_EfeitosLab"); if fx then table.insert(ex, fx) end
	rp.FilterDescendantsInstances = ex; rp.RespectCanCollide = true      -- vegetacao sem colisao (arbustos, capim) nao e parede nem tampa a visada
	return rp
end
local function perfil(nome)
	local v = pasta.Dados_Clipes:FindFirstChild("Perfis_" .. nome); local t = {}
	if v then local s = string.match(v.Value, "perfil=(.*)$") or ""; for x in string.gmatch(s, "[^,]+") do table.insert(t, tonumber(x)) end end
	return t
end
local function velPerfil(t, tp) if #t == 0 then return 0 end; local i = math.clamp(math.floor(tp * 30 + 0.5) + 1, 1, #t); return t[i] end
local function visivel(de, mod, rp)
	local r = raiz(mod); local hit = workspace:Raycast(de, r.Position - de, rp)
	return not hit or hit.Instance:IsDescendantOf(mod)
end
local function candidatos(urso)
	local t = {}
	for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(t, p.Character) end end
	for _, m in ipairs(CS:GetTagged("AlvoTesteUrso")) do table.insert(t, m) end
	return t
end

local function soltar(mod, motivo)
	local q = quedas[mod]; if not q then return end
	quedas[mod] = nil
	for _, c in ipairs(q.cons) do c:Disconnect() end
	for _, nc in ipairs(q.nc or {}) do nc:Destroy() end
	local h = q.hum
	if h and h.Parent then
		h.PlatformStand = false
		h.WalkSpeed += q.dws; h[q.campo] += q.djp
		if not q.plr and h.Health > 0 then h:ChangeState(Enum.HumanoidStateType.GettingUp) end
	end
	if mod.Parent then
		mod:SetAttribute("Derrubado_CargaSelvagem", nil); mod:SetAttribute("AtordoadoAte", nil)
		if motivo == "recuperou" then mod:SetAttribute("QuedaImuneAte", workspace:GetServerTimeNow() + M.LAB.CargaSelvagem.imunidade) end
	end
	registrar({ev = "cs_levantou", alvo = mod.Name, motivo = motivo})
	Efeitos:FireAllClients({tipo = "Atordoado", fase = "fim", alvo = mod})
end
M.soltarQueda = soltar
-- trajeto do lancamento conferido no SERVIDOR: passos de 2 studs a partir do alvo; para antes de parede (raycast na
-- altura da raiz) ou de barranco (sem chao ou queda > 6 studs). Retorna a distancia segura (< 2 = nao lanca).
local function distSegura(r, dir, D, rp)
	local p = r.Position; local ok = 0
	for s = 2, D, 2 do
		local a = p + dir * (s - 2); local b = p + dir * s
		if workspace:Raycast(a, b - a, rp) then break end
		local g = workspace:Raycast(b + Vector3.new(0, 2, 0), Vector3.new(0, -9, 0), rp)
		if not g or (p.Y - g.Position.Y) > 9 then break end
		ok = s
	end
	return math.max(0, ok - 1)
end
function M.derrubar(mod, dir, id, urso)
	local L = M.LAB.CargaSelvagem; local agora = workspace:GetServerTimeNow()
	if quedas[mod] then registrar({ev = "cs_ja_derrubado", alvo = mod.Name}); return "ja_derrubado" end
	if (mod:GetAttribute("QuedaImuneAte") or 0) > agora then registrar({ev = "cs_imune", alvo = mod.Name}); return "imune" end
	local h = mod:FindFirstChildOfClass("Humanoid"); local r = raiz(mod)
	if not (h and r and h.Health > 0) then return "sem_vida" end
	local campo = h.UseJumpPower and "JumpPower" or "JumpHeight"
	local q = {hum = h, ate = agora + L.atordoamento, fimAte = agora + L.atordoamento + L.levantar, dws = h.WalkSpeed, djp = h[campo],
		campo = campo, cons = {}, plr = Players:GetPlayerFromCharacter(mod)}
	h.WalkSpeed -= q.dws; h[campo] -= q.djp
	h.PlatformStand = true
	local w = Vector3.yAxis:Cross(plano(dir).Unit) * L.giroTombo          -- tomba PARA LONGE do urso (topo vai na direcao da carga)
	-- lancamento: so alvo pequeno; velocidade de arco balistico pela gravidade real (sobe lancAlt, anda D). Fisica real:
	-- nada teleporta, e a distancia ja vem cortada antes de parede/barranco
	local lanc, alt = nil, mod:GetExtentsSize().Y
	-- o corpo do urso (solido, ancorado e movido pelo servidor) ficava por cima do alvo na ombrada e segurava o voo:
	-- enquanto o alvo estiver derrubado, ele NAO colide com o urso (NoCollisionConstraint por par; sem grupo de colisao)
	local nc = {}
	if urso then
		local pu, pa = {}, {}
		for _, p in ipairs(urso:GetDescendants()) do if p:IsA("BasePart") and p.CanCollide then table.insert(pu, p) end end
		for _, p in ipairs(mod:GetDescendants()) do if p:IsA("BasePart") and p.CanCollide then table.insert(pa, p) end end
		for _, a in ipairs(pu) do for _, b in ipairs(pa) do
			local c = Instance.new("NoCollisionConstraint"); c.Name = "Urso_SemColisaoQueda"; c.Part0 = a; c.Part1 = b; c.Parent = b; table.insert(nc, c)
		end end
	end
	if alt <= L.alturaPequeno and L.lancDist > 0 then
		local D = distSegura(r, plano(dir).Unit, L.lancDist, excluirChars(mod))
		if D >= 2 then
			local g = workspace.Gravity; local vy = math.sqrt(2 * g * L.lancAlt); local T = 2 * vy / g
			lanc = plano(dir).Unit * (D / T) + Vector3.new(0, vy, 0)
		end
		registrar({ev = "cs_lancamento", alvo = mod.Name, altura = math.floor(alt * 10 + 0.5) / 10, dist = lanc and D or 0})
	end
	if q.plr then
		local ok = pcall(function() Efeitos:FireClient(q.plr, {tipo = "Queda", fase = "cair", giro = w, lanc = lanc, dur = L.atordoamento}) end)
		if not ok then registrar({ev = "cs_cliente_falhou", alvo = mod.Name}) end
	else
		pcall(function() r:SetNetworkOwner(nil) end)                   -- NPC: o servidor e dono da fisica do voo
		r.AssemblyAngularVelocity = w; if lanc then r.AssemblyLinearVelocity = lanc end
	end
	table.insert(q.cons, h.Died:Connect(function() soltar(mod, "morte") end))
	table.insert(q.cons, mod.AncestryChanged:Connect(function() if not mod:IsDescendantOf(workspace) then soltar(mod, "removido") end end))
	q.nc = nc; quedas[mod] = q
	mod:SetAttribute("Derrubado_CargaSelvagem", true); mod:SetAttribute("AtordoadoAte", q.ate)
	if L.dano > 0 then h:TakeDamage(L.dano) end                         -- PENDENTE (0 no laboratorio)
	registrar({ev = "cs_derrubou", alvo = mod.Name, id = id})
	Efeitos:FireAllClients({tipo = "Atordoado", fase = "inicio", alvo = mod, dur = L.atordoamento})
	return "derrubado"
end
RS.Heartbeat:Connect(function()
	local agora = workspace:GetServerTimeNow()
	for mod, q in pairs(quedas) do
		if not q.levantando and agora >= q.ate then
			q.levantando = true
			if q.hum.Parent then q.hum.PlatformStand = false end
			if q.plr then pcall(function() Efeitos:FireClient(q.plr, {tipo = "Queda", fase = "levantar"}) end)
			elseif q.hum.Parent and q.hum.Health > 0 then q.hum:ChangeState(Enum.HumanoidStateType.GettingUp) end
		end
		if agora >= q.fimAte then soltar(mod, "recuperou") end
	end
end)
Players.PlayerRemoving:Connect(function(plr) if plr.Character and quedas[plr.Character] then soltar(plr.Character, "desconexao") end end)

function M.cargaSelvagem(urso, quem, alvo)
	local L = M.LAB.CargaSelvagem; local agora = workspace:GetServerTimeNow()
	local e = estado[urso] or {}; estado[urso] = e
	e.recCS = e.recCS or 0
	if urso:GetAttribute("Incapacitado") then registrar({ev = "recusado", motivo = "incapacitado"}); return false, "incapacitado" end
	if e.acao then registrar({ev = "recusado", motivo = "ocupado"}); return false, "ocupado" end
	if e.recCS > agora then registrar({ev = "recusado", motivo = "recarga"}); return false, "recarga" end
	local en = urso:GetAttribute("EnergiaLab") or 100
	if en < L.energia then registrar({ev = "recusado", motivo = "energia"}); return false, "energia" end
	local rp = excluirChars(urso)
	local pv = urso:GetPivot(); local dir = plano(pv.LookVector).Unit
	local peito = pv.Position + Vector3.new(0, 4, 0)
	-- alvo indicado: o servidor confere tudo; invalido = carga reta (perto demais = recusa sem custo)
	local travado, porque = nil, "sem_alvo"
	if typeof(alvo) == "Instance" and alvo:IsA("Model") and alvo:IsDescendantOf(workspace) then
		local ok, por = elegivel(urso, alvo)
		if ok then
			local d = plano(raiz(alvo).Position - pv.Position); if d.Magnitude < 0.01 then d = dir * 0.01 end
			local ang = math.deg(math.acos(math.clamp(dir:Dot(d.Unit), -1, 1)))
			if d.Magnitude < L.distMin then registrar({ev = "recusado", motivo = "alvo_perto_demais"}); return false, "alvo_perto_demais"
			elseif d.Magnitude > L.distMax then porque = string.format("longe(%.1f)", d.Magnitude)
			elseif ang > L.cone then porque = string.format("fora_cone(%.0f)", ang)
			elseif not visivel(peito, alvo, rp) then porque = "sem_visada"
			else travado, porque = alvo, "travado" end
		else porque = por end
	end
	urso:SetAttribute("EnergiaLab", en - L.energia)
	local id = game:GetService("HttpService"):GenerateGUID(false)
	e.acao = "CargaSelvagem"; e.recCS = agora + L.recarga; e.ataque = id
	local esc = L.escalaVel
	local fIni, kIni = faixa(urso, "Urso_CargaInicio"); local fCor = faixa(urso, "Urso_CargaCorrida")
	local tEmp = (kIni and kIni:GetAttribute("EmpurraoS")) or 0.34; local empurrou = false     -- 05/11: patas empurram o chao (racha no cliente)
	local fImp, kImp = faixa(urso, "Urso_CargaImpacto"); local fFre = faixa(urso, "Urso_Frenagem")
	local pIni, pImp, pFre = perfil("Urso_CargaInicio"), perfil("Urso_CargaImpacto"), perfil("Urso_Frenagem")
	local tImp = kImp:GetAttribute("ImpactoS") or 0.2
	local escFre = L.velocidade / math.max(pFre[1] or L.velocidade, 1)          -- a Frenagem parte da velocidade da carga
	e.faixa = fIni; fIni:Play(0.12, 1, esc)
	registrar({ev = "cs_inicio", id = id, quem = quem, alvo = travado and travado.Name or nil, porque = porque})
	Efeitos:FireAllClients({tipo = "CargaSelvagem", fase = "inicio", urso = urso, id = id})
	local fase = "inicio"; local t0 = os.clock(); local andou = 0; local alvoImp = nil; local acertou, conferiu = false, false
	local altChao = nil
	do local g = workspace:Raycast(pv.Position + Vector3.new(0, 3, 0), Vector3.new(0, -10, 0), rp); altChao = g and (pv.Position.Y - g.Position.Y) or 0 end
	local function trocar(f, nova) e.faixa:Stop(0.12); e.faixa = f; f:Play(0.10, 1, esc); fase = nova end
	local function terminar(motivo)
		if fase == "fim" then return end
		fase = "fim"; if e.ataque == id then e.acao = nil; e.faixa = nil end
		registrar({ev = "cs_fim", id = id, motivo = motivo, andou = math.floor(andou * 10 + 0.5) / 10, acertou = acertou})
		Efeitos:FireAllClients({tipo = "CargaSelvagem", fase = "fim", urso = urso, id = id, motivo = motivo})
	end
	local con; con = RS.Heartbeat:Connect(function(dt)
		if fase == "fim" then con:Disconnect(); return end
		if e.ataque ~= id or not urso:IsDescendantOf(workspace) or urso:GetAttribute("Incapacitado") then
			if e.faixa then e.faixa:Stop(0.15) end; con:Disconnect(); terminar("interrompido"); return
		end
		local f = e.faixa
		-- velocidade = a do clipe que esta tocando (perfil por quadro)
		local v
		if fase == "inicio" then v = velPerfil(pIni, f.TimePosition)
			if not empurrou and (f.TimePosition >= tEmp or os.clock() - t0 >= tEmp / esc) then empurrou = true; Efeitos:FireAllClients({tipo = "CargaSelvagem", fase = "arrancada", urso = urso, id = id, dir = dir}) end
			if f.Length > 0 and (not f.IsPlaying or f.TimePosition >= f.Length - 0.02) then trocar(fCor, "corrida") end   -- Length 0 = ainda carregando (1o uso)
		elseif fase == "corrida" then v = L.velocidade
		elseif fase == "impacto" then v = velPerfil(pImp, f.TimePosition)
		elseif fase == "freada" then v = velPerfil(pFre, f.TimePosition) * escFre end
		v = (v or 0) * esc
		pv = urso:GetPivot()
		-- curva limitada e perda do alvo (so antes do impacto)
		if travado and (fase == "inicio" or fase == "corrida") then
			local ok = elegivel(urso, travado)
			local r = ok and raiz(travado)
			local d = r and plano(r.Position - pv.Position); if d and d.Magnitude < 0.01 then d = dir * 0.01 end
			local motivo = nil
			if not ok then motivo = "inelegivel"
			elseif d.Magnitude > L.perdaDist then motivo = "longe"
			elseif math.deg(math.acos(math.clamp(dir:Dot(d.Unit), -1, 1))) > L.cone then motivo = "fora_cone"
			elseif not visivel(pv.Position + Vector3.new(0, 4, 0), travado, rp) then motivo = "sem_visada" end
			if motivo then registrar({ev = "cs_perdeu_alvo", id = id, motivo = motivo}); travado = nil
			else
				local cruz = dir:Cross(d.Unit).Y; local ang = math.acos(math.clamp(dir:Dot(d.Unit), -1, 1))
				local passo = math.min(ang, math.rad(L.curva) * dt) * (cruz >= 0 and 1 or -1)
				dir = (CFrame.Angles(0, passo, 0) * dir).Unit           -- em Y, angulo positivo gira de -Z para -X (cruz.Y > 0)
				if (dir:Cross(d.Unit).Y >= 0) ~= (cruz >= 0) then dir = d.Unit end
			end
		end
		local passo = v * dt
		if passo > 0 then
			-- parede: Blockcast do peito na direcao do movimento
			local cfB = CFrame.lookAt(pv.Position + Vector3.new(0, 4, 0) + dir * (L.frente - 1), pv.Position + Vector3.new(0, 4, 0) + dir * L.frente)
			local hit = workspace:Blockcast(cfB, Vector3.new(5, 5, 1), dir * (passo + 0.5), rp)
			local novo = pv.Position + dir * passo
			local g = workspace:Raycast(novo + Vector3.new(0, 3 + L.degrauMax, 0), Vector3.new(0, -(8 + L.degrauMax), 0), rp)
			local yNovo = g and (g.Position.Y + altChao) or novo.Y
			if (hit or (yNovo - pv.Position.Y) > L.degrauMax) and fase == "impacto" then
				passo = 0                                                   -- ja no impacto: so para (o clipe do impacto continua)
			elseif hit or (yNovo - pv.Position.Y) > L.degrauMax then
				local dist = hit and math.max(0, hit.Distance - 0.5) or 0
				urso:PivotTo(CFrame.lookAt(pv.Position + dir * dist, pv.Position + dir * (dist + 1)))
				andou += dist
				registrar({ev = "cs_parede", id = id, obj = hit and hit.Instance.Name or "degrau"})
				Efeitos:FireAllClients({tipo = "CargaSelvagem", fase = "parede", urso = urso, id = id, pos = hit and hit.Position or pv.Position})
				e.faixa:Stop(0.1); local fR = faixa(urso, "Urso_ReacaoImpacto"); e.faixa = fR; fR:Play(0.08)
				terminar("parede"); return
			end
			novo = Vector3.new(novo.X, yNovo, novo.Z); if passo == 0 then novo = pv.Position end
			-- alvo no caminho (faixa de impacto a frente; segmento do passo; nao usa Touched)
			if fase == "inicio" or fase == "corrida" then
				local fr0 = pv.Position + dir * L.frente; local antecip = L.velocidade * tImp          -- distancia andada ate o contato do clipe (v*esc durante tImp/esc s)
				for _, m in ipairs(candidatos(urso)) do
					if m ~= urso and elegivel(urso, m) and not quedas[m] then
						local r = raiz(m); local rel = plano(r.Position - fr0); local ao = rel:Dot(dir)
						local lat = (rel - dir * ao).Magnitude; local dy = math.abs(r.Position.Y - (pv.Position.Y + 3))
						if ao >= -1.5 and ao <= passo + antecip and lat <= L.raioImpacto and dy <= L.alturaImpacto then alvoImp = m; break end
					end
				end
				if alvoImp then trocar(fImp, "impacto"); registrar({ev = "cs_contato_previsto", id = id, alvo = alvoImp.Name}) end
			end
			if passo > 0 then urso:PivotTo(CFrame.lookAt(novo, novo + dir)); andou += passo end
		end
		if fase == "impacto" then
			if not conferiu and e.faixa.TimePosition >= tImp then
				conferiu = true
				local r = alvoImp and alvoImp.Parent and raiz(alvoImp)
				local fr = urso:GetPivot().Position + dir * L.frente
				local d = r and plano(r.Position - fr).Magnitude
				if r and d <= L.raioImpacto + 2.5 and elegivel(urso, alvoImp) then
					acertou = true; local res = M.derrubar(alvoImp, dir, id, urso)
					registrar({ev = "cs_impacto", id = id, alvo = alvoImp.Name, res = res, d = math.floor(d * 10 + 0.5) / 10})
					Efeitos:FireAllClients({tipo = "CargaSelvagem", fase = "impacto", urso = urso, id = id, pos = r.Position, alvo = alvoImp, res = res})
				else
					registrar({ev = "cs_desviou", id = id, d = d})
					Efeitos:FireAllClients({tipo = "CargaSelvagem", fase = "impacto", urso = urso, id = id, pos = fr})
				end
				alvoImp = nil
			end
			if e.faixa.Length > 0 and (not e.faixa.IsPlaying or e.faixa.TimePosition >= e.faixa.Length - 0.02) then e.faixa:Stop(0.2); terminar(acertou and "acertou" or "desviou"); return end
		elseif fase ~= "freada" and (andou >= L.distMax or os.clock() - t0 > L.tempoMax) then
			trocar(fFre, "freada"); registrar({ev = "cs_errou", id = id, andou = andou})
		elseif fase == "freada" and e.faixa.Length > 0 and (not e.faixa.IsPlaying or e.faixa.TimePosition >= e.faixa.Length - 0.02) then
			e.faixa:Stop(0.2); terminar("errou"); return
		end
	end)
	return true, id
end

-- pedido do cliente: so o DONO do urso; o servidor ignora qualquer dado alem do nome do poder e do urso
Pedido.OnServerEvent:Connect(function(plr, poder, urso, alvo)
	if typeof(urso) ~= "Instance" or not urso:IsDescendantOf(workspace) then return end
	if urso:GetAttribute("DonoUserId") ~= plr.UserId then registrar({ev = "recusado", motivo = "nao_dono", quem = plr.Name}); return end
	if poder == "GolpeColossal" then M.golpeColossal(urso, plr.Name) end
	if poder == "RugidoProtetor" then M.rugidoProtetor(urso, plr.Name) end
	if poder == "CargaSelvagem" then M.cargaSelvagem(urso, plr.Name, alvo) end
end)
return M
