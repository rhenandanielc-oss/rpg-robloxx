-- LoboKit_Servidor (Script em ServerScriptService.LoboAncestral_Kit) - kit Natureza do Lobo Ancestral, PROTOTIPO no place
-- isolado Testes-loboancestral (15/11/2026). Fonte: BLENDER/Criaturas/Lobo_Ancestral_Ref/studio/kit/LoboKit_Servidor.luau.
-- Servidor decide tudo: dono, estado, alvo, alcance, linha de visao, obstaculos, dano, energia, recarga, duracao, noite e
-- acumulo de bonus. O cliente so pede (RemoteEvent PedidoKit) e mostra efeitos (EventoKit). Numeros: ConfigKitLobo [PROPOSTA].
-- Montaria do lobo nao existe neste place: teste montado fica PENDENTE.
local Players = game:GetService("Players")
local RS = game:GetService("RunService")
local Lighting = game:GetService("Lighting")
local Rep = game:GetService("ReplicatedStorage")
local PASTA = Rep:WaitForChild("LoboAncestral")
local CFG = require(PASTA:WaitForChild("ConfigKitLobo"))
local LA = require(PASTA:WaitForChild("LoboAnimacao"))
local AREA = workspace:WaitForChild("Teste_LoboAncestral")

local remotes = PASTA:FindFirstChild("Remotes") or Instance.new("Folder", PASTA); remotes.Name = "Remotes"
local function remote(n) local r = remotes:FindFirstChild(n) or Instance.new("RemoteEvent", remotes); r.Name = n; return r end
local PEDIDO, EVENTO = remote("PedidoKit"), remote("EventoKit")

local K = {lobos = {}, log = {}}
_G.LoboKit = K
local function log(s) table.insert(K.log, string.format("%.2f %s", os.clock(), s)); if #K.log > 400 then table.remove(K.log, 1) end end
-- 17/11: logs por categoria - [PERCEPCAO] (servidor viu/perdeu), [IA] (decisao do guardiao), [HABILIDADE] (execucao e
-- resultado), [INDICADOR] (o que foi mostrado ao dono). Formato: "<categoria> <lobo>: texto".
local function logc(cat, L, s) log(string.format("[%s] %s: %s", cat, L and L.modelo.Name or "-", s)) end

-- ------------------------------------------------------------------ alvos e geometria
local function alvosPasta() return AREA:FindFirstChild("Alvos") end
local function alvoValido(m)
	if typeof(m) ~= "Instance" or not m:IsA("Model") then return false end
	local pa = alvosPasta(); if not pa or not m:IsDescendantOf(pa) then return false end
	local h = m:FindFirstChildOfClass("Humanoid"); local r = m.PrimaryPart or m:FindFirstChild("HumanoidRootPart")
	return h ~= nil and h.Health > 0 and r ~= nil
end
local function centro(m) local r = m.PrimaryPart or m:FindFirstChild("HumanoidRootPart"); return r and r.Position end
-- r5 (18/11, auditoria de compatibilidade): alcance e contato medidos ate a SUPERFICIE do corpo do alvo (ponto mais proximo
-- das partes visiveis), nao ao centro. Antes: Mordida/Garra 0 em corpos grandes, Salto pousava dentro e o Instinto perdia
-- colossais. Devolve o ponto e a distancia HORIZONTAL ate ele.
local function pontoProximo(alvo, de)
	local melhor, md = nil, math.huge
	for _, p in ipairs(alvo:GetDescendants()) do
		if p:IsA("BasePart") and p.Transparency < 1 then
			local l = p.CFrame:PointToObjectSpace(de); local h = p.Size / 2
			local q = p.CFrame:PointToWorldSpace(Vector3.new(math.clamp(l.X, -h.X, h.X), math.clamp(l.Y, -h.Y, h.Y), math.clamp(l.Z, -h.Z, h.Z)))
			local dd = Vector3.new(q.X - de.X, 0, q.Z - de.Z).Magnitude
			if dd < md then melhor, md = q, dd end
		end
	end
	if not melhor then local c = centro(alvo); return c, c and Vector3.new(c.X - de.X, 0, c.Z - de.Z).Magnitude or math.huge end
	return melhor, md
end
-- r6 (18/11): mesmas PROTECOES do jogo (regra de Nucleo.alvosValidos/emZonaSegura, lida em src/, copiada aqui; o Nucleo
-- nao foi alterado): nunca o dono; nunca aliado do dono (AliadoDe); nunca alvo dentro de parte com a tag "ZonaSegura";
-- jogador so com workspace.PvPAtivo. Vale para basicos, Salto, Investida, dano, marca, Instinto (pegadas/revelar) e IA.
-- A integracao com N.ferir/alvosValidos do jogo continua pendente (etapa combinada).
local CS = game:GetService("CollectionService")
local function emZonaSegura(pos)
	for _, z in ipairs(CS:GetTagged("ZonaSegura")) do
		if z:IsA("BasePart") then
			local p = z.CFrame:PointToObjectSpace(pos); local s = z.Size / 2
			if math.abs(p.X) <= s.X and math.abs(p.Y) <= s.Y and math.abs(p.Z) <= s.Z then return true end
		end
	end
	return false
end
local function protegido(L, m)
	local dono = L and L.dono and L.dono.UserId
	local plr = Players:GetPlayerFromCharacter(m)
	if plr then
		if dono and plr.UserId == dono then return "dono" end
		if workspace:GetAttribute("PvPAtivo") ~= true then return "PvP desligado" end
	end
	if dono and m:GetAttribute("AliadoDe") == dono then return "aliado" end
	local c = centro(m); if c and emZonaSegura(c) then return "zona segura" end
	return nil
end
local function alvoPermitido(L, m) return alvoValido(m) and not protegido(L, m) end
K.protegido = protegido
local function filtro(L, extra)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude
	local lista = {L.modelo}
	for _, x in ipairs(extra or {}) do table.insert(lista, x) end
	for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(lista, pl.Character) end end
	p.FilterDescendantsInstances = lista; return p
end
local function peito(L) return L.modelo:GetPivot().Position + Vector3.new(0, 4.5, 0) end
-- linha de visao: raio do peito do lobo ao centro do alvo; so o proprio alvo pode ser atingido
local function linhaDeVisao(L, alvo)
	local a, b = peito(L), centro(alvo)
	local hit = workspace:Raycast(a, b - a, filtro(L))
	return hit == nil or hit.Instance:IsDescendantOf(alvo)
end
-- 17/11: velocidade estimada de cada alvo (posicao entre quadros; usa a fisica quando existe). Serve para o Salto antecipar
-- um alvo em movimento e para a IA medir quem se APROXIMA (sem confundir com o proprio movimento do lobo).
K.velAlvos = {}
RS.Heartbeat:Connect(function(dt)
	local pa = alvosPasta(); if not pa or dt <= 0 then return end
	for _, a in ipairs(pa:GetChildren()) do
		local r = a:IsA("Model") and (a.PrimaryPart or a:FindFirstChild("HumanoidRootPart"))
		if r then
			local e = K.velAlvos[a] or {p = r.Position, v = Vector3.zero}; K.velAlvos[a] = e
			local v = (r.Position - e.p) / dt
			if (r.Position - e.p).Magnitude > 2 then v = Vector3.zero; e.v = Vector3.zero end   -- teletransporte/respawn: nao e velocidade
			if not r.Anchored and r.AssemblyLinearVelocity.Magnitude > 0.5 then v = r.AssemblyLinearVelocity end
			e.v = e.v:Lerp(v, math.min(1, dt * 10)); e.p = r.Position
		end
	end
	for a in pairs(K.velAlvos) do if not a.Parent then K.velAlvos[a] = nil end end
end)
local function velAlvo(a) local e = K.velAlvos[a]; return e and Vector3.new(e.v.X, 0, e.v.Z) or Vector3.zero end

-- ------------------------------------------------------------------ modificadores (tabela unica, aditiva, com teto)
local function recalcular(L)
	local v, e, d = 0, 0, 0
	for _, mod in pairs(L.mods) do v += mod.vel or 0; e += mod.esq or 0; d += mod.dano or 0 end
	L.velMult = 1 + math.min(v, CFG.Acumulo.tetoVelocidade)
	L.esquiva = CFG.Esquiva.chanceBase + math.min(e, CFG.Acumulo.tetoEsquiva)
	L.danoMult = 1 + math.min(d, CFG.Acumulo.tetoDano)
	local m = L.modelo
	m:SetAttribute("VelMult", L.velMult); m:SetAttribute("Esquiva", L.esquiva); m:SetAttribute("DanoMult", L.danoMult)
	local fontes = {} for k in pairs(L.mods) do table.insert(fontes, k) end; table.sort(fontes)
	m:SetAttribute("Bonus", table.concat(fontes, ","))
end
local function setMod(L, nome, mod) L.mods[nome] = mod; recalcular(L) end

-- ------------------------------------------------------------------ lobo
local function vivo(L) return L.ativo and L.modelo.Parent ~= nil and L.vida > 0 end
local function registrar(modelo, dono)
	local L = {modelo = modelo, dono = dono, C = LA.preparar(modelo), mods = {}, recargas = {}, estado = "Livre",
		energia = CFG.Energia.max, vida = CFG.Vida, ativo = true, tarefas = {}, noite = false, rastros = {}, percebidos = {}}
	modelo:SetAttribute("DonoUserId", dono and dono.UserId or 0)
	K.lobos[modelo] = L
	recalcular(L)
	if noiteGlobalRef and noiteGlobalRef() then setMod(L, "CacadorNoturno", {vel = CFG.CacadorNoturno.velocidade, esq = CFG.CacadorNoturno.esquiva, dano = CFG.CacadorNoturno.danoFisico}); modelo:SetAttribute("Noite", true) end
	L.C.base("Repouso", 0)
	modelo.AncestryChanged:Connect(function(_, pai) if pai == nil then K.remover(L, "removido") end end)
	log("registrado " .. modelo:GetFullName() .. " dono=" .. tostring(dono))
	return L
end
function K.remover(L, motivo)
	if not L.ativo then return end
	L.ativo = false; L.estado = "Removido"
	for _, t in ipairs(L.tarefas) do pcall(task.cancel, t) end
	L.mods = {}; pcall(recalcular, L)
	K.lobos[L.modelo] = nil
	log("lobo encerrado: " .. motivo)
end
function K.morrer(L)
	L.vida = 0; L.estado = "Morto"; L.mods = {}; recalcular(L)
	for _, t in ipairs(L.tarefas) do pcall(task.cancel, t) end; L.tarefas = {}
	L.C.pararTudo(0.1); L.C.acao("Impacto", 0.05)
	L.modelo:SetAttribute("Estado", "Morto"); log("lobo morto")
end
-- dano recebido (para testar esquiva): rola a chance calculada no servidor
function K.receberDano(L, dano, origem)
	if not vivo(L) then return "morto" end
	if origem then L.atacadoPor = {alvo = origem, ate = os.clock() + 6} end     -- a IA trata como ameaca (se perceber o atacante)
	if math.random() < L.esquiva then log("esquivou"); return "esquivou" end
	L.vida -= dano; if L.vida <= 0 then K.morrer(L) end
	return "acertou"
end
local function tarefa(L, f) local t = task.spawn(f); table.insert(L.tarefas, t); return t end

-- ------------------------------------------------------------------ passiva: Cacador Noturno (estado unico no servidor)
local CN = CFG.CacadorNoturno
local noiteGlobal = nil
noiteGlobalRef = function() return noiteGlobal end
local function ehNoite(ct, anterior)
	local h = anterior and CN.histerese or -CN.histerese          -- histerese: para sair do estado precisa passar a borda
	return ct >= CN.noiteInicio - h or ct < CN.noiteFim + h
end
task.spawn(function()
	while true do
		local n = ehNoite(Lighting.ClockTime, noiteGlobal)
		if n ~= noiteGlobal then
			noiteGlobal = n; workspace:SetAttribute("LoboNoite", n)
			for _, L in pairs(K.lobos) do
				if vivo(L) then
					setMod(L, "CacadorNoturno", n and {vel = CN.velocidade, esq = CN.esquiva, dano = CN.danoFisico} or nil)
					L.modelo:SetAttribute("Noite", n)
					if L.dono then EVENTO:FireClient(L.dono, "Noite", L.modelo, n) end
				end
			end
			log("noite=" .. tostring(n) .. " ClockTime=" .. Lighting.ClockTime)
		end
		task.wait(CN.intervalo)
	end
end)
K.ehNoite = function() return noiteGlobal end

-- ------------------------------------------------------------------ passiva: Instinto de Caca
-- pegadas = posicoes ANTIGAS (>= atrasoMin s) de inimigos que o lobo viu (linha de visao) a <= raio; indicador so para o dono.
-- pista de ninho = direcao aproximada (erro aleatorio +-ninhoErroGraus), sem distancia nem posicao.
local IC = CFG.InstintoCaca
-- v6.2: "revela inimigos escondidos em vegetacao". Vegetacao = parte com atributo Vegetacao = true (arbusto, capim alto).
-- Para o Instinto a vegetacao NAO bloqueia a visao (paredes/rochas continuam bloqueando). Inimigo dentro de vegetacao ou
-- com atributo Escondido = true, a <= raio e visivel por esse criterio, e revelado SO para o dono (contorno no cliente).
local function partesVegetacao()
	local l = {}
	for _, d in ipairs(AREA:GetDescendants()) do if d:IsA("BasePart") and d:GetAttribute("Vegetacao") then table.insert(l, d) end end
	return l
end
local function escondido(a, veg)
	if a:GetAttribute("Escondido") then return true end
	local c = centro(a); if not c or #veg == 0 then return false end
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Include; op.FilterDescendantsInstances = veg
	return #workspace:GetPartBoundsInRadius(c, 1.0, op) > 0
end
local function visaoInstinto(L, alvo, veg)
	local a, b = peito(L), centro(alvo)
	local hit = workspace:Raycast(a, b - a, filtro(L, veg))
	return hit == nil or hit.Instance:IsDescendantOf(alvo)
end
-- 17/11: PERCEPCAO separada do INDICADOR. Antes o laco inteiro dependia de L.dono: um lobo sem dono (IA/guardiao) nao
-- percebia nada. Agora o servidor percebe para TODO lobo vivo (raio, linha de visao com paredes bloqueando e vegetacao
-- nao bloqueando, alvos validos); so os indicadores (pegadas, contorno de revelado, pista de ninho) vao ao dono, por
-- FireClient, nunca a todos. K.percepcaoSemDono = false reproduz o comportamento antigo (teste A/B pelo gancho).
K.percepcaoSemDono = true
local function perceber(L, veg)
	local pa = alvosPasta(); local vistos = {}
	local piv = L.modelo:GetPivot().Position
	for _, a in ipairs(pa and pa:GetChildren() or {}) do
		if alvoPermitido(L, a) then                                        -- r6: protegidos nao sao percebidos/revelados
			local c = centro(a); local _, dist = pontoProximo(a, piv)          -- r5: raio ate a superficie
			if dist <= IC.raio and visaoInstinto(L, a, veg) then
				vistos[a] = {dist = dist, pos = c, escondido = escondido(a, veg), t = os.clock()}
			end
		end
	end
	return vistos
end
K.perceber = perceber
task.spawn(function()
	local t = 0
	while true do
		task.wait(IC.intervalo); t += IC.intervalo
		local veg = partesVegetacao()
		for _, L in pairs(K.lobos) do
			if vivo(L) and (L.dono or K.percepcaoSemDono) then
				local agora = os.clock()
				local vistos = perceber(L, veg)
				-- [PERCEPCAO]: so mudancas (novo / perdido / escondido) para nao inundar o log
				for a, v in pairs(vistos) do
					local antes = L.percebidos[a]
					if not antes then logc("PERCEPCAO", L, string.format("viu %s a %.1f%s", a.Name, v.dist, v.escondido and " (escondido na vegetacao)" or ""))
					elseif antes.escondido ~= v.escondido then logc("PERCEPCAO", L, a.Name .. (v.escondido and " entrou na vegetacao" or " saiu da vegetacao")) end
				end
				for a in pairs(L.percebidos) do if not vistos[a] then logc("PERCEPCAO", L, "perdeu " .. (a.Parent and a.Name or "alvo removido")) end end
				L.percebidos = vistos
				-- rastros (servidor, para qualquer lobo): posicoes vistas com o tempo
				local pistas, revelados = {}, {}
				for a, v in pairs(vistos) do
					local hist = L.rastros[a] or {}; L.rastros[a] = hist
					table.insert(hist, {t = agora, p = Vector3.new(v.pos.X, 0, v.pos.Z)})
					if v.escondido then table.insert(revelados, a) end
				end
				for a, hist in pairs(L.rastros) do
					while hist[1] and agora - hist[1].t > IC.rastroSeg do table.remove(hist, 1) end
					if #hist == 0 or not a.Parent then L.rastros[a] = nil
					else
						-- pegadas com IDADE e ordem (o cliente orienta e esmaece pela idade); sempre >= atrasoMin atrasadas
						for _, h in ipairs(hist) do if agora - h.t >= IC.atrasoMin then table.insert(pistas, {p = h.p, idade = agora - h.t, id = a.Name}) end end
					end
				end
				if L.dono then
					K.ultimasPegadas = #pistas
					K.ultimosRevelados = #revelados
					if #pistas > 0 then EVENTO:FireClient(L.dono, "Pegadas", L.modelo, pistas) end
					if #revelados > 0 then EVENTO:FireClient(L.dono, "Revelar", L.modelo, revelados, IC.intervalo + 0.3) end
					local resumo = #pistas .. "/" .. #revelados
					if resumo ~= L.ultimoIndicador then L.ultimoIndicador = resumo; logc("INDICADOR", L, string.format("so ao dono %s: %d pegadas, %d revelados", L.dono.Name, #pistas, #revelados)) end
					if t % IC.ninhoIntervalo < IC.intervalo then
						for _, n in ipairs(AREA:GetDescendants()) do
							if n:IsA("BasePart") and n:GetAttribute("PistaNinho") then
								local d = n.Position - L.modelo:GetPivot().Position
								if Vector3.new(d.X, 0, d.Z).Magnitude <= IC.ninhoRaio then
									local ang = math.atan2(d.X, d.Z) + math.rad((math.random() * 2 - 1) * IC.ninhoErroGraus)
									local dirN = Vector3.new(math.sin(ang), 0, math.cos(ang))
									K.ultimaPistaNinho = {dir = dirN, erroGraus = math.deg(math.acos(math.clamp(dirN:Dot(Vector3.new(d.X, 0, d.Z).Unit), -1, 1)))}
									EVENTO:FireClient(L.dono, "PistaNinho", L.modelo, dirN)
									logc("INDICADOR", L, "pista de ninho ao dono (direcao com erro)")
								end
							end
						end
					end
				end
			end
		end
	end
end)

-- ------------------------------------------------------------------ energia e recargas
task.spawn(function()
	while true do
		local dt = task.wait(0.25)
		for _, L in pairs(K.lobos) do
			if vivo(L) then
				L.energia = math.min(CFG.Energia.max, L.energia + CFG.Energia.regenPorS * dt)
				L.modelo:SetAttribute("Energia", math.floor(L.energia)); L.modelo:SetAttribute("Vida", L.vida)
			end
		end
	end
end)
local function podeUsar(L, nome, c)
	if not vivo(L) then return false, "lobo inativo" end
	if L.estado ~= "Livre" then return false, "ocupado (" .. L.estado .. ")" end
	if L.basicoAte and os.clock() < L.basicoAte then return false, "ocupado (golpe andando)" end   -- r7
	local r = L.recargas[nome]; if r and os.clock() < r then return false, string.format("recarga %.1fs", r - os.clock()) end
	if c.energia and L.energia < c.energia then return false, "energia" end
	return true
end
local function gastar(L, nome, c)
	L.recargas[nome] = os.clock() + (c.recarga or 0)
	if c.energia then L.energia -= c.energia end
	L.modelo:SetAttribute("Recarga_" .. nome, L.recargas[nome])
end
-- Instinto de Caca v6.2: marca da presa (8 s, +10% de dano SO nela; so o dono ve). Marcada = alvo do Salto ou quem o lobo acerta.
local function marcar(L, alvo)
	if not alvoPermitido(L, alvo) then return end
	local novo = not (L.presa and L.presa.alvo == alvo and os.clock() < L.presa.ate)
	L.presa = {alvo = alvo, ate = os.clock() + IC.marcaSeg}
	if novo then logc("HABILIDADE", L, "presa marcada: " .. alvo.Name) end
	if novo and L.dono then EVENTO:FireClient(L.dono, "Marca", L.modelo, alvo, IC.marcaSeg); logc("INDICADOR", L, "marca da presa so ao dono " .. L.dono.Name) end
end
local function presaMarcada(L, alvo) return L.presa ~= nil and L.presa.alvo == alvo and os.clock() < L.presa.ate end
local function causarDano(L, alvo, base, tipo)
	local pr = protegido(L, alvo)                                          -- r6: ultima barreira (ex.: alvo entrou na zona no voo)
	if pr then logc("PROTECAO", L, tipo .. " sem dano em " .. alvo.Name .. " (" .. pr .. ")"); return 0 end
	local h = alvo:FindFirstChildOfClass("Humanoid"); if not h then return 0 end
	local mult = L.danoMult
	local marcada = presaMarcada(L, alvo)
	if marcada then mult += IC.marcaDano end                                   -- aditivo com noite/kit (teto do dano do kit nao muda)
	local d = base * mult
	h:TakeDamage(d); logc("HABILIDADE", L, string.format("%s acertou %s: %.1f (x%.2f%s)", tipo, alvo.Name, d, mult, marcada and ", presa marcada" or ""))
	K.ultimoDano = {tipo = tipo, alvo = alvo.Name, dano = d, mult = mult, marcada = marcada}
	marcar(L, alvo)
	return d
end
-- espera ate o tempo t do clipe (pelo relogio do servidor); cancela se o lobo deixar de existir
local function ate(L, t0, t) while vivo(L) and os.clock() - t0 < t do RS.Heartbeat:Wait() end return vivo(L) end

-- ------------------------------------------------------------------ basicos (fora dos slots)
local function basico(L, nome)
	local c = CFG.Basico[nome]
	local ok, por = podeUsar(L, nome, c); if not ok then return false, por end
	-- r7 (18/11, pedido do usuario: atacar ANDANDO para haver PvP de verdade): em movimento o basico NAO para o lobo.
	-- Usa o clipe PARCIAL (cabeca/pescoco; Garra + pata dianteira D) por cima da marcha e o estado continua "Livre"
	-- (o seguir/IA seguem andando); L.basicoAte impede outra habilidade ate o fim do golpe. Parado = clipe inteiro, como antes.
	local andando = ((L.seguindo and not L.parado and not L.virando) or (L.ia and L.ia.andando)) and true or false   -- r7b: so em movimento real
	gastar(L, nome, c)
	local clip = andando and (c.clipe .. "_Andando") or c.clipe
	local cl = LA.clipe(clip); local tC
	for _, mk in ipairs(cl.marcadores) do if mk.nome == c.marcador then tC = mk.t end end
	if andando then L.basicoAte = os.clock() + cl.quadros / cl.fps else L.estado = nome end
	L.C.acao(clip, 0.08)
	logc("HABILIDADE", L, nome .. (andando and " ANDANDO (clipe parcial, marcha continua)" or " parado"))
	tarefa(L, function()
		local t0 = os.clock()
		if not ate(L, t0, tC or 0.5) then return end
		local piv = L.modelo:GetPivot(); local melhor, md = nil, math.huge
		for _, a in ipairs(alvosPasta() and alvosPasta():GetChildren() or {}) do
			if alvoPermitido(L, a) then
				local sp, ds = pontoProximo(a, piv.Position)                       -- r5: ate a superficie do corpo
				local d = sp - piv.Position; local dh = Vector3.new(d.X, 0, d.Z)
				local ang = dh.Magnitude > 0.1 and math.deg(math.acos(math.clamp(dh.Unit:Dot(piv.LookVector), -1, 1))) or 0
				if ds <= c.alcance + 0.5 and ang <= c.cone / 2 and ds < md and linhaDeVisao(L, a) then melhor, md = a, ds end
			end
		end
		if melhor then causarDano(L, melhor, c.dano, nome) else logc("HABILIDADE", L, nome .. " sem alvo") end
		ate(L, t0, cl.quadros / cl.fps); if vivo(L) and not andando then L.estado = "Livre" end
	end)
	return true
end

-- ------------------------------------------------------------------ ATIVA 1: Salto Predatorio
local SP = CFG.SaltoPredatorio
-- v6.2: dados = Model (alvo travado / sob o mouse) OU Vector3 (ponto do mouse/camera no chao). Sem alvo: salto de mobilidade
-- (sem dano, energia 12). Planeio de 0,6 s no apice (o clipe congela no apice). Encadeavel: em ate 2 s apos pousar, o 2o
-- salto ignora a recarga e custa metade da energia (uma vez por cadeia).
-- 17/11: pouso no CHAO REAL (antes o lobo pousava na altura de partida: flutuava em declive e entrava em degrau).
-- Chao = raycast para baixo (respeita CanCollide; ignora lobos, alvos e jogadores). Desnivel ate SP.desnivelMax [PROPOSTA].
-- Sem alvo: se o ponto pedido nao tem chao valido (borda/buraco/parede alta), o pouso recua de 2 em 2 studs ate achar
-- (nunca alem do pedido nem do alcance). Com alvo: desnivel maior que o limite = recusado sem gastar energia.
local function filtroChao(L)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude; p.RespectCanCollide = true
	local lista = {}
	local pa = alvosPasta(); if pa then table.insert(lista, pa) end
	for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(lista, pl.Character) end end
	for _, x in pairs(K.lobos) do table.insert(lista, x.modelo) end
	if not K.lobos[L.modelo] then table.insert(lista, L.modelo) end
	p.FilterDescendantsInstances = lista; return p
end
local function chaoY(L, pos)
	local h = workspace:Raycast(Vector3.new(pos.X, pos.Y + 30, pos.Z), Vector3.new(0, -120, 0), filtroChao(L))
	return h and h.Position.Y or nil
end
K.chaoY = chaoY
-- pouso FIRME (medido no Studio 17/11: patas de tras ~0,5 e da frente ~5,3 studs a frente do pivo): chao sob as patas de
-- tras e da frente, sem degrau no meio; declive ate PATA_DESNIVEL entre elas (~26 graus) vira inclinacao do corpo no pouso.
local PATA_TRAS, PATA_FRENTE, PATA_DESNIVEL = 0.5, 5.3, 2.6
local function chaoFirme(L, p, dir, offPiv, yRef)
	local yT = chaoY(L, p + dir * PATA_TRAS); local yF = chaoY(L, p + dir * PATA_FRENTE)
	if not yT or not yF or math.abs(yF - yT) > PATA_DESNIVEL then return nil end
	local yM = chaoY(L, p + dir * ((PATA_TRAS + PATA_FRENTE) / 2))
	if not yM or math.abs(yM - (yT + yF) / 2) > 1.0 then return nil end          -- degrau/buraco entre as patas
	if math.abs(yT + offPiv - yRef) > SP.desnivelMax then return nil end
	return yT, math.atan2(yF - yT, PATA_FRENTE - PATA_TRAS)
end
local function salto(L, dados)
	if typeof(dados) == "Instance" and alvoValido(dados) then
		local pr = protegido(L, dados)
		if pr then logc("PROTECAO", L, "salto recusado: " .. dados.Name .. " (" .. pr .. ")"); return false, "alvo protegido (" .. pr .. ")" end
	end
	local alvo = (typeof(dados) == "Instance" and alvoValido(dados)) and dados or nil
	local ponto = (not alvo and typeof(dados) == "Vector3") and dados or nil
	if not alvo and not ponto then return false, "alvo invalido" end
	local cadeia = L.saltoCadeiaAte and os.clock() < L.saltoCadeiaAte
	local custo = (alvo and SP.energia or SP.energiaSemAlvo) * (cadeia and SP.cadeiaFatorEnergia or 1)
	if not vivo(L) then return false, "lobo inativo" end
	if L.estado ~= "Livre" then return false, "ocupado (" .. L.estado .. ")" end
	if L.basicoAte and os.clock() < L.basicoAte then return false, "ocupado (golpe andando)" end   -- r7
	if not cadeia then
		local r = L.recargas.SaltoPredatorio; if r and os.clock() < r then return false, string.format("recarga %.1fs", r - os.clock()) end
	end
	if L.energia < custo then return false, "energia" end
	local p0 = L.modelo:GetPivot()
	local c = alvo and (pontoProximo(alvo, p0.Position)) or ponto          -- r5: com alvo mira o ponto mais proximo do corpo
	local d = Vector3.new(c.X - p0.Position.X, 0, c.Z - p0.Position.Z)
	if d.Magnitude < 0.5 then return false, "direcao invalida" end
	local dist = d.Magnitude
	if alvo then
		if dist < SP.alcanceMin or dist > SP.alcanceMax then return false, string.format("fora de alcance (%.1f)", dist) end
		if not linhaDeVisao(L, alvo) then return false, "sem linha de visao" end
	else
		dist = math.clamp(dist, SP.alcanceMin, SP.alcanceMax)                    -- sem alvo: o servidor limita a distancia
	end
	local dir = d.Unit
	local y0 = chaoY(L, p0.Position)
	local offPiv = y0 and (p0.Position.Y - y0) or 0                              -- altura do pivo acima do chao (mantida no pouso)
	local destino, recuo, inclin
	local anteci = Vector3.zero
	if alvo then
		-- 17/11: alvo em movimento - mira onde ele estara no pouso (velocidade medida x tempo ate o pouso), limitado a
		-- SP.anteciparMax e SEM passar do alcance maximo (o alcance nao aumenta)
		anteci = velAlvo(alvo) * (SP.decolagem + SP.voo + SP.planeio)
		if anteci.Magnitude > SP.anteciparMax then anteci = anteci.Unit * SP.anteciparMax end
		local cp = Vector3.new(c.X, p0.Position.Y, c.Z) + anteci
		local dp = Vector3.new(cp.X - p0.Position.X, 0, cp.Z - p0.Position.Z)
		if dp.Magnitude > SP.alcanceMax then cp = p0.Position + dp.Unit * SP.alcanceMax; dp = Vector3.new(cp.X - p0.Position.X, 0, cp.Z - p0.Position.Z) end
		if dp.Magnitude >= SP.alcanceMin then dir = dp.Unit; c = cp else anteci = Vector3.zero end
		local dh = Vector3.new(c.X, p0.Position.Y, c.Z) - dir * SP.folgaPouso       -- r5: pousa diante da SUPERFICIE (focinho encostado)
		local yd = chaoY(L, dh)
		if not yd then return false, "sem chao diante do alvo" end
		if math.abs(yd + offPiv - p0.Position.Y) > SP.desnivelMax then return false, string.format("desnivel %.1f", yd + offPiv - p0.Position.Y) end
		local yF, ang = chaoFirme(L, dh, dir, offPiv, p0.Position.Y)
		if not yF then return false, "sem apoio firme diante do alvo" end
		destino = Vector3.new(dh.X, yF + offPiv, dh.Z); inclin = ang
	else
		local dd = dist
		while dd >= SP.alcanceMin do
			local pp = p0.Position + dir * dd
			local yd, ang = chaoFirme(L, pp, dir, offPiv, p0.Position.Y)
			if yd then destino = Vector3.new(pp.X, yd + offPiv, pp.Z); inclin = ang; break end
			dd -= 2
		end
		if not destino then return false, "sem chao valido no trajeto" end
		recuo = dist - dd
	end
	L.energia -= custo
	if cadeia then L.saltoCadeiaAte = nil else L.recargas.SaltoPredatorio = os.clock() + SP.recarga end
	L.modelo:SetAttribute("Recarga_SaltoPredatorio", L.recargas.SaltoPredatorio)
	L.estado = "SaltoPredatorio"
	if alvo then marcar(L, alvo) end
	L.modelo:PivotTo(CFrame.lookAt(p0.Position, p0.Position + dir))
	local faixa = L.C.acao(SP.clipe, 0.06)
	local vooTotal = SP.voo + SP.planeio
	EVENTO:FireAllClients("Salto", L.modelo, p0.Position, destino, vooTotal,
		{cadeia = cadeia or false, alvo = alvo ~= nil, decolagem = SP.decolagem, voo = SP.voo, planeio = SP.planeio, apice = SP.apiceClipe})
	local distH = (Vector3.new(destino.X, 0, destino.Z) - Vector3.new(p0.Position.X, 0, p0.Position.Z)).Magnitude
	logc("HABILIDADE", L, string.format("salto %s%s dist %.1f desnivel %.1f%s%s custo %.0f energia %.0f",
		alvo and ("com alvo " .. alvo.Name) or "sem alvo", cadeia and " (encadeado)" or "", distH, destino.Y - p0.Position.Y,
		(recuo and recuo > 0) and string.format(" (recuou %.0f da borda)", recuo) or "",
		anteci.Magnitude > 0.3 and string.format(" (antecipou %.1f)", anteci.Magnitude) or "", custo, L.energia))
	tarefa(L, function()
		local t0 = os.clock()
		if not ate(L, t0, SP.decolagem) then return end
		local ini = L.modelo:GetPivot().Position
		local alt = SP.alturaArco * distH; local prev = ini; local parou = nil; local hMax = 0
		local fp = filtro(L, alvo and {alvo} or nil)
		local congelado, soltou = false, false
		while vivo(L) do
			local tv = os.clock() - t0 - SP.decolagem
			local u = math.clamp(tv / vooTotal, 0, 1)
			-- planeio: o clipe para no apice enquanto o lobo plana; a altura segue um arco achatado no meio
			if not congelado and os.clock() - t0 >= SP.apiceClipe then faixa:AdjustSpeed(0); congelado = true end
			if congelado and not soltou and tv >= SP.voo / 2 + SP.planeio then faixa:AdjustSpeed(1); soltou = true end
			local h = math.min(1, 4 * u * (1 - u) * 1.35)                        -- topo plano (~40% do voo perto do apice)
			local pos = ini:Lerp(destino, u) + Vector3.new(0, alt * h, 0)
			hMax = math.max(hMax, pos.Y - ini.Y)
			local hit = workspace:Raycast(prev + Vector3.new(0, 3, 0), pos - prev, fp)   -- trajeto bloqueado: para ali e cai
			if hit then
				parou = hit.Position - (pos - prev).Unit * 2.5
				local yc = chaoY(L, parou) or (p0.Position.Y - offPiv)
				local de, para = Vector3.new(parou.X, prev.Y, parou.Z), Vector3.new(parou.X, yc + offPiv, parou.Z)
				logc("HABILIDADE", L, "salto interrompido por obstaculo: " .. hit.Instance.Name)
				local tq = os.clock(); local dq = math.clamp(math.sqrt(math.max(de.Y - para.Y, 0) / 40) * 1.2, 0.12, 0.45)   -- cai ate o chao (sem teleporte)
				while vivo(L) do
					local q = math.clamp((os.clock() - tq) / dq, 0, 1)
					local pq = de:Lerp(para, q * q)
					L.modelo:PivotTo(CFrame.lookAt(pq, pq + dir)); if q >= 1 then break end
					RS.Heartbeat:Wait()
				end
				break
			end
			L.modelo:PivotTo(CFrame.lookAt(pos, pos + dir)); prev = pos
			if u >= 1 then break end
			RS.Heartbeat:Wait()
		end
		if not vivo(L) then return end
		if congelado and not soltou then faixa:AdjustSpeed(1) end
		local fim = L.modelo:GetPivot().Position
		if not parou then L.modelo:PivotTo(CFrame.lookAt(destino, destino + dir) * CFrame.Angles(inclin or 0, 0, 0)); fim = destino end   -- acompanha o declive
		local acertou, dano = false, 0
		local dAlvo = alvo and alvoValido(alvo) and select(2, pontoProximo(alvo, fim)) or nil   -- r5: pouso -> superficie
		if alvo and not parou and dAlvo and dAlvo <= SP.raioAcertoSuperficie then
			dano = causarDano(L, alvo, CFG.Basico.Mordida.dano * SP.multDano, "SaltoPredatorio"); acertou = true
		elseif alvo then logc("HABILIDADE", L, "salto sem acerto" .. (parou and " (obstaculo)" or string.format(" (superficie a %.1f do pouso; raio %.1f)", dAlvo or -1, SP.raioAcertoSuperficie)))
		else logc("HABILIDADE", L, "salto de mobilidade pousou" .. (parou and " (obstaculo)" or "")) end
		EVENTO:FireAllClients("SaltoPouso", L.modelo, {acertou = acertou, parou = parou ~= nil, cadeia = cadeia or false, pos = fim})
		K.ultimoSalto = {dist = (Vector3.new(fim.X, 0, fim.Z) - Vector3.new(p0.Position.X, 0, p0.Position.Z)).Magnitude, alvo = alvo ~= nil,
			cadeia = cadeia, custo = custo, tempoVoo = os.clock() - t0 - SP.decolagem, apice = hMax, desnivel = fim.Y - p0.Position.Y,
			parou = parou ~= nil, acertou = acertou, dano = dano, dAlvo = dAlvo, recuo = recuo, energia = L.energia, pouso = fim,
			planejado = destino, antecipou = anteci.Magnitude, inclinacao = math.deg(inclin or 0), recarga = L.recargas.SaltoPredatorio and (L.recargas.SaltoPredatorio - os.clock()) or 0}
		ate(L, t0, SP.golpe + SP.planeio + 0.49); if vivo(L) then L.estado = "Livre" end
		if not cadeia and vivo(L) then L.saltoCadeiaAte = os.clock() + SP.cadeiaJanela end   -- abre a janela do 2o salto
	end)
	return true
end

-- ------------------------------------------------------------------ ATIVA 2: Uivo Ancestral (so o proprio lobo)
local UV = CFG.UivoAncestral
local function uivo(L)
	local ok, por = podeUsar(L, "UivoAncestral", UV); if not ok then return false, por end
	gastar(L, "UivoAncestral", UV); L.estado = "UivoAncestral"
	L.C.acao(UV.clipe, 0.1)
	-- 17/11: o visual acompanha o clipe desde o inicio (inspiracao 0-0,55 s, nota 0,55-1,85 s, bonus a partir de 0,6 s)
	EVENTO:FireAllClients("UivoInicio", L.modelo, UV.duracao, UV.buffInicio)
	logc("HABILIDADE", L, "uivo: inicio (clipe)")
	tarefa(L, function()
		local t0 = os.clock()
		if not ate(L, t0, UV.buffInicio) then return end
		setMod(L, "UivoAncestral", {vel = UV.velocidade, esq = UV.esquiva})
		L.modelo:SetAttribute("UivoAte", os.clock() + UV.duracao)
		EVENTO:FireAllClients("Uivo", L.modelo, UV.duracao); logc("HABILIDADE", L, "uivo: bonus ligado")
		ate(L, t0, 2.6); if vivo(L) and L.estado == "UivoAncestral" then L.estado = "Livre" end
		if not ate(L, t0, UV.buffInicio + UV.duracao) then return end
		setMod(L, "UivoAncestral", nil); L.modelo:SetAttribute("UivoAte", nil); logc("HABILIDADE", L, "uivo: bonus desligado")
		EVENTO:FireAllClients("UivoFim", L.modelo)
	end)
	return true
end

-- ------------------------------------------------------------------ ATIVA 3: Investida (direcao escolhida)
local IV = CFG.Investida
local VEL_GALOPE = 21.43
local function velInvestida(t)        -- = clipes_kit30/Investida_velocidade.json (sincronizado com as patas)
	local function s(x) x = math.clamp(x, 0, 1); return x * x * (3 - 2 * x) end
	if t < 0.22 then return 0 elseif t < 0.36 then return VEL_GALOPE * s((t - 0.22) / 0.14)
	elseif t < 0.78 then return VEL_GALOPE elseif t < 0.96 then return VEL_GALOPE * (1 - s((t - 0.78) / 0.18)) end
	return 0
end
local function investida(L, dir)
	local ok, por = podeUsar(L, "Investida", IV); if not ok then return false, por end
	if typeof(dir) ~= "Vector3" then return false, "direcao invalida" end
	dir = Vector3.new(dir.X, 0, dir.Z); if dir.Magnitude < 0.1 then return false, "direcao invalida" end
	dir = dir.Unit
	gastar(L, "Investida", IV); L.estado = "Investida"
	local p0 = L.modelo:GetPivot().Position
	L.modelo:PivotTo(CFrame.lookAt(p0, p0 + dir))
	L.C.acao(IV.clipe, 0.06)
	EVENTO:FireAllClients("Investida", L.modelo, dir)
	logc("HABILIDADE", L, "investida: inicio")
	tarefa(L, function()
		local t0 = os.clock(); local acertou = {}; local parado = false; local fimTipo, fimPos = "nada", nil
		local fp = filtro(L)
		local ultimo = 0
		while vivo(L) do
			local t = os.clock() - t0; if t >= 1.2 then break end
			local dt = t - ultimo; ultimo = t
			local v = parado and 0 or velInvestida(t)
			if v > 0 then
				local pos = L.modelo:GetPivot().Position; local passo = dir * v * dt
				-- obstaculo: caixa da largura do lobo a frente do peito (alvos validos contam como acerto, nao como parede)
				local cf = CFrame.lookAt(pos + Vector3.new(0, 3.5, 0), pos + Vector3.new(0, 3.5, 0) + dir)
				local hit = workspace:Blockcast(cf, Vector3.new(IV.largura, 4, 1), dir * (passo.Magnitude + 6.5), fp)
				local alvo = hit and hit.Instance:FindFirstAncestorOfClass("Model")
				if hit and alvo and alvoValido(alvo) and not protegido(L, alvo) then   -- r6: protegido conta como obstaculo (sem dano)
					if not acertou[alvo] and hit.Distance <= 6.5 + IV.alcanceMordida then
						acertou[alvo] = true; causarDano(L, alvo, CFG.Basico.Mordida.dano * IV.multDano, "Investida")
						parado = true; fimTipo, fimPos = "alvo", hit.Position; logc("HABILIDADE", L, "investida parou no primeiro alvo")
						EVENTO:FireAllClients("InvestidaFim", L.modelo, "alvo", hit.Position)
					end
				elseif hit and hit.Distance < passo.Magnitude + 6.0 then   -- focinho fica ~6 studs a frente do pivo
					parado = true; fimTipo, fimPos = "obstaculo", hit.Position; logc("HABILIDADE", L, "investida parou em obstaculo: " .. hit.Instance.Name)
					EVENTO:FireAllClients("InvestidaFim", L.modelo, "obstaculo", hit.Position)
				end
				if not parado then L.modelo:PivotTo(CFrame.lookAt(pos + passo, pos + passo + dir)) end
			end
			RS.Heartbeat:Wait()
		end
		if vivo(L) then L.estado = "Livre" end
		local n = 0 for _ in pairs(acertou) do n += 1 end
		K.ultimaInvestida = {dist = (L.modelo:GetPivot().Position - p0).Magnitude, acertos = n, fim = fimTipo}
		if fimTipo == "nada" then EVENTO:FireAllClients("InvestidaFim", L.modelo, "nada", L.modelo:GetPivot().Position) end
	end)
	return true
end

-- ------------------------------------------------------------------ pedidos (mesmo caminho para o remoto e os testes)
local ACOES = {SaltoPredatorio = function(L, d) return salto(L, d) end, UivoAncestral = function(L) return uivo(L) end,
	Investida = function(L, d) return investida(L, d) end, Mordida = function(L) return basico(L, "Mordida") end,
	Garra = function(L) return basico(L, "Garra") end}
function K.pedido(jogador, modelo, acao, dados)
	local L = K.lobos[modelo]
	if not L then return false, "lobo desconhecido" end
	if L.dono ~= jogador then return false, "nao e o dono" end
	local f = ACOES[acao]; if type(acao) ~= "string" or not f then return false, "acao invalida" end
	local ok, por = f(L, dados)
	logc("HABILIDADE", L, string.format("pedido do jogador %s -> %s %s", acao, ok and "executada" or "recusada", por or ""))
	return ok, por
end
local ultimoPedido = {}
PEDIDO.OnServerEvent:Connect(function(jogador, modelo, acao, dados)
	local t = os.clock(); if ultimoPedido[jogador] and t - ultimoPedido[jogador] < 0.1 then return end   -- limite de spam
	ultimoPedido[jogador] = t
	local ok, por = K.pedido(jogador, modelo, acao, dados)
	EVENTO:FireClient(jogador, "Resposta", modelo, acao, ok, por)
end)

-- ------------------------------------------------------------------ IA de DEFESA (guardiao de TESTE, 17/11) [PROPOSTA]
-- Nao existe IA de combate do lobo no projeto: este guardiao e so do place isolado (nao integrado ao jogo principal).
-- Liga com L.ia = {posto = Vector3}. Usa a MESMA percepcao do servidor (L.percebidos: raio, paredes bloqueiam, vegetacao nao)
-- e as MESMAS funcoes das habilidades (energia, recarga, alcance, linha de visao validados igual ao jogador).
-- Sem agressividade permanente: so age quando AMEACADO e volta a "Calmo" depois de IA.calmaSeg sem ameaca. Sem patrulha:
-- parado no posto; depois da ameaca volta andando ao posto. Nao persegue alem de IA.coleira do posto.
-- Ameaca = inimigo PERCEBIDO a <= IA.raioAmeaca, ou se aproximando (>= IA.aproximacao studs/s) a <= IA.raioAlerta,
-- ou que atacou o lobo (L.atacadoPor) e esta percebido. Inimigo atras de parede nao e percebido -> nao gera ameaca.
local IA = CFG.IA_Guardiao
local O_IA = CFrame.new(0, 0, -2.196)       -- gira em volta do meio do corpo (mesmo ponto das curvas)
local function linhaDeVisaoIA(L, a) return visaoInstinto(L, a, partesVegetacao()) end
local function acaoIA(L, acao, dados, motivo)
	local f = ACOES[acao]
	logc("IA", L, string.format("decidiu %s (%s)", acao, motivo))
	local ok, por = f(L, dados)
	logc("HABILIDADE", L, string.format("%s pela IA -> %s %s", acao, ok and "executada" or "recusada", por or ""))
	return ok, por
end
local function virarPara(L, p, dt)
	local piv = L.modelo:GetPivot()
	local d = Vector3.new(p.X - piv.Position.X, 0, p.Z - piv.Position.Z); if d.Magnitude < 0.1 then return 0 end
	local fr = Vector3.new(piv.LookVector.X, 0, piv.LookVector.Z).Unit
	local ang = math.atan2(fr:Cross(d.Unit).Y, fr:Dot(d.Unit))
	local passo = math.clamp(ang, -IA.giroGrausS * math.pi / 180 * dt, IA.giroGrausS * math.pi / 180 * dt)
	L.modelo:PivotTo(piv * O_IA * CFrame.Angles(0, passo, 0) * O_IA:Inverse())
	return math.deg(math.abs(ang - passo))
end
task.spawn(function()
	while true do
		local dt = task.wait(IA.intervalo)
		for _, L in pairs(K.lobos) do
			if vivo(L) and L.ia then
				local I = L.ia
				local agora = os.clock()
				local piv = L.modelo:GetPivot().Position
				-- escolhe a ameaca entre os PERCEBIDOS (re-checa distancia e parede a cada tick: a percepcao roda a cada 1 s)
				local melhor, mdist, motivo = nil, math.huge, nil
				for a, v in pairs(L.percebidos) do
					if alvoPermitido(L, a) and linhaDeVisaoIA(L, a) then
						local c, dist = pontoProximo(a, piv)                       -- r5: ameaca medida ate a superficie
						local distPosto = (c - I.posto).Magnitude
						local aprox = (dist > 0.1) and velAlvo(a):Dot(Vector3.new(piv.X - c.X, 0, piv.Z - c.Z).Unit) or 0   -- so o movimento DO ALVO
						local m = nil
						if dist <= IA.raioAmeaca then m = string.format("perto %.1f", dist)
						elseif dist <= IA.raioAlerta and aprox >= IA.aproximacao then m = string.format("aproximando %.1f studs/s a %.1f", aprox, dist)
						elseif L.atacadoPor and L.atacadoPor.alvo == a and agora < L.atacadoPor.ate then m = "atacou o lobo" end
						if m and distPosto <= IA.coleira + IA.raioAmeaca and dist < mdist then melhor, mdist, motivo = a, dist, m end
					end
				end
				if melhor then
					if I.estado ~= "Ameacado" or I.alvo ~= melhor then logc("IA", L, string.format("AMEACADO por %s (%s)", melhor.Name, motivo)) end
					I.estado = "Ameacado"; I.alvo = melhor; I.ultimaAmeaca = agora
				elseif I.estado == "Ameacado" and agora - (I.ultimaAmeaca or 0) > IA.calmaSeg then
					I.estado = "Calmo"; I.alvo = nil; logc("IA", L, "calmo (sem ameaca percebida por " .. IA.calmaSeg .. " s)")
				end
				if L.estado == "Livre" then
					if I.estado == "Ameacado" and I.alvo and alvoPermitido(L, I.alvo) then
						local a = I.alvo; local c, dist = pontoProximo(a, piv)
						local fora = virarPara(L, c, dt)
						local E = L.energia
						local livre = function(n) local r = L.recargas[n]; return not r or agora >= r end
						if livre("UivoAncestral") and E >= UV.energia and not L.mods.UivoAncestral and dist <= IA.uivoAte then
							acaoIA(L, "UivoAncestral", nil, string.format("defesa: buff com ameaca a %.1f", dist))
						elseif dist <= CFG.Basico.Mordida.alcance + 1 and fora <= 25 and livre("Mordida") then
							acaoIA(L, "Mordida", nil, string.format("corpo a corpo %.1f", dist))
						elseif dist > CFG.Basico.Mordida.alcance + 1 and dist <= IA.investidaAte and fora <= 12 and livre("Investida") and E >= IV.energia then
							local d = c - piv; acaoIA(L, "Investida", Vector3.new(d.X, 0, d.Z), string.format("investida %.1f", dist))
						elseif dist >= IA.saltoDesde and dist <= SP.alcanceMax and fora <= 20 and livre("SaltoPredatorio") and E >= SP.energia then
							acaoIA(L, "SaltoPredatorio", a, string.format("salto %.1f", dist))
						end
					elseif I.estado == "Calmo" then
						-- volta ao posto andando (Andar na velocidade do clipe, sem patinar); sem patrulha
						local d = Vector3.new(I.posto.X - piv.X, 0, I.posto.Z - piv.Z)
						if d.Magnitude > IA.voltaPostoDist then
							local fora = virarPara(L, I.posto, dt)
							if fora < 30 then
								L.C.base("Andar", 0.25, L.velMult)
								local p = L.modelo:GetPivot(); L.modelo:PivotTo(p + p.LookVector * math.min(CFG.Movimento.andar * L.velMult * dt, d.Magnitude))
								I.andando = true
							end
						elseif I.andando then I.andando = false; L.C.base("Repouso", 0.3); logc("IA", L, "de volta ao posto") end
					end
				end
			end
		end
	end
end)

-- ------------------------------------------------------------------ seguir o dono a pe (andar/corrida nas velocidades dos clipes)
-- 16/11 (curvas v32, aprovadas pelo usuario): ANDANDO o lobo nao gira mais "no lugar" - anda sempre para a frente e vira
-- descrevendo o arco dos clipes AndarCurvaE/D (giro de 30 graus/s na velocidade do Andar, em volta do ponto O sob o meio do
-- corpo, 2,196 studs a frente do pivo = o mesmo centro usado no Blender). Reto e curva tocam juntos, na mesma fase, com pesos
-- (1-|pc|) e |pc|; o giro aplicado = pc x 30 graus/s x ritmo, entao as patas apoiadas ficam paradas no chao.
-- Dono atras (> 120 graus) com o lobo parado: VirarE/D r2 (90 graus no lugar com as patas girando junto) e depois segue.
-- Corrida: sem clipe de curva ainda (mantem o giro antigo). Numeros [PROPOSTA].
local GIRO_CURVA = math.rad(30)              -- = LOBO_CURVA_GIRO do Blender (rotacao_raiz 36 graus por ciclo de 1,2 s)
local O_CURVA = CFrame.new(0, 0, -2.196)     -- Y_MEIO do rig (frente = -Z)
local GANHO_CURVA, SUAVE_CURVA = 1.6, 3.0     -- pc alvo = ganho x erro de direcao / giro; pc muda no maximo 3/s
local VIRAR_ANG = math.rad(120)
local function pararCurvas(L, fade)
	for _, n in ipairs({"AndarCurvaE", "AndarCurvaD"}) do local f = L.C.faixas[n]; if f and f.IsPlaying then f:Stop(fade or 0.2) end end
	L.pc = 0
end
local function misturarCurva(L, pc)
	local base = L.C.faixas["Andar"]
	if not base then return end
	local pesos = {AndarCurvaE = math.max(pc, 0), AndarCurvaD = math.max(-pc, 0)}
	for n, w in pairs(pesos) do
		local f = L.C.faixa(n); w = math.max(w, 0.001)
		if not f.IsPlaying then
			f:Play(0.15, w, L.velMult)
			if base.Length > 0 and f.Length > 0 then f.TimePosition = (base.TimePosition / base.Length % 1) * f.Length end
		else
			if math.abs(f.WeightTarget - w) > 0.01 then f:AdjustWeight(w, 0.1) end
			if math.abs(f.Speed - L.velMult) > 0.005 then f:AdjustSpeed(L.velMult) end
		end
	end
	local wb = math.max(1 - math.abs(pc), 0.001)
	if math.abs(base.WeightTarget - wb) > 0.01 then base:AdjustWeight(wb, 0.1) end
end
local function virarNoLugar(L, sinal)
	L.virando = true
	local nome = sinal > 0 and "VirarE" or "VirarD"
	local f = L.C.acao(nome, 0.15, 1)
	local feito = false
	local function concluir()
		if feito then return end; feito = true
		if L.modelo.Parent then L.modelo:PivotTo(L.modelo:GetPivot() * O_CURVA * CFrame.Angles(0, math.rad(90) * sinal, 0) * O_CURVA:Inverse()) end
		f:Stop(0); L.virando = false
	end
	f:GetMarkerReachedSignal("GiroCompleto"):Once(concluir)
	f.Stopped:Once(concluir)
	task.delay(f.Length + 0.5, concluir)            -- seguranca: nunca fica preso no giro
end
RS.Heartbeat:Connect(function(dt)
	for _, L in pairs(K.lobos) do
		if vivo(L) and L.estado == "Livre" and L.dono and L.dono.Character and L.dono.Character.PrimaryPart and not L.parado and not L.virando then
			local piv = L.modelo:GetPivot(); local alvo = L.dono.Character.PrimaryPart.Position
			local d = Vector3.new(alvo.X - piv.Position.X, 0, alvo.Z - piv.Position.Z)
			local dist = d.Magnitude
			local mv = CFG.Movimento
			if dist > mv.distSeguir or (L.seguindo and dist > mv.distParar) then
				local dir = d.Unit
				local fr = Vector3.new(piv.LookVector.X, 0, piv.LookVector.Z).Unit
				local ang = math.atan2(fr:Cross(dir).Y, fr:Dot(dir))       -- + = dono a esquerda
				if not L.seguindo and math.abs(ang) > VIRAR_ANG then
					virarNoLugar(L, ang > 0 and 1 or -1)
				else
					L.seguindo = true
					local corre = dist > 25
					local v = (corre and mv.corrida or mv.andar) * L.velMult
					L.C.base(corre and "Corrida" or "Andar", 0.25, L.velMult)      -- a passada acelera junto: sem patinar
					if corre then
						pararCurvas(L)
						local yaw = piv.LookVector:Lerp(dir, math.min(1, dt * 6))
						local novo = piv.Position + dir * math.min(v * dt, dist)
						L.modelo:PivotTo(CFrame.lookAt(novo, novo + Vector3.new(yaw.X, 0, yaw.Z)))
					else
						local alvoPc = math.clamp(GANHO_CURVA * ang / GIRO_CURVA, -1, 1)
						L.pc = (L.pc or 0) + math.clamp(alvoPc - (L.pc or 0), -SUAVE_CURVA * dt, SUAVE_CURVA * dt)
						misturarCurva(L, L.pc)
						local cf = piv + fr * (v * dt)                                   -- anda so para a frente (sem deslizar de lado)
						cf = cf * O_CURVA * CFrame.Angles(0, L.pc * GIRO_CURVA * L.velMult * dt, 0) * O_CURVA:Inverse()
						L.modelo:PivotTo(cf)
					end
				end
			elseif L.seguindo then
				L.seguindo = false; pararCurvas(L, 0.3); L.C.base("Repouso", 0.3)
			end
		end
	end
end)

-- lobo do teste: dono = primeiro jogador que entrar
local function iniciar(jogador)
	local m = AREA:FindFirstChild("Lobo_Ancestral")
	if m and not K.lobos[m] then registrar(m, jogador) end
end
Players.PlayerAdded:Connect(iniciar)
for _, p in ipairs(Players:GetPlayers()) do iniciar(p) end
K.registrar = registrar

-- ------------------------------------------------------------------ gancho de TESTE (so Studio; ServerStorage nao replica)
-- usa exatamente K.pedido / K.receberDano / K.morrer; nao ha atalho que pule a validacao
if RS:IsStudio() then
	local bf = game.ServerStorage:FindFirstChild("LoboKitTeste") or Instance.new("BindableFunction")
	bf.Name = "LoboKitTeste"; bf.Parent = game.ServerStorage
	local function umLobo(m) if m then return K.lobos[m] end for _, x in pairs(K.lobos) do if x.modelo.Name == "Lobo_Ancestral" then return x end end end
	bf.OnInvoke = function(cmd, a, b, c)
		local jogador = Players:GetPlayers()[1]
		if cmd == "pedido" then local L = umLobo(c); return K.pedido(jogador, L and L.modelo, a, b)
		elseif cmd == "pedidoOutro" then local L = umLobo(); return K.pedido("outro", L and L.modelo, a, b)
		elseif cmd == "estado" then
			local L = umLobo(a); if not L then return {existe = false} end
			local fontes = {} for k in pairs(L.mods) do table.insert(fontes, k) end
			local lg = {} for i = math.max(1, #K.log - (b or 8) + 1), #K.log do table.insert(lg, K.log[i]) end
			return {existe = true, ativo = L.ativo, estado = L.estado, energia = L.energia, vida = L.vida, velMult = L.velMult, esquiva = L.esquiva,
				danoMult = L.danoMult, bonus = table.concat(fontes, ","), noite = K.ehNoite(), pos = L.modelo:GetPivot().Position,
				ultimoDano = K.ultimoDano, ultimaInvestida = K.ultimaInvestida, ultimoSalto = K.ultimoSalto, revelados = K.ultimosRevelados,
				presa = (L.presa and os.clock() < L.presa.ate) and L.presa.alvo.Name or nil, recargaSalto = L.recargas.SaltoPredatorio and (L.recargas.SaltoPredatorio - os.clock()) or nil,
				cadeia = L.saltoCadeiaAte and (L.saltoCadeiaAte - os.clock()) or nil, pegadas = K.ultimasPegadas, ninho = K.ultimaPistaNinho, log = lg}
		elseif cmd == "dano" then
			local L = umLobo(); local r = {acertou = 0, esquivou = 0, morto = 0}
			for _ = 1, b or 1 do local x = K.receberDano(L, a); r[x] += 1 end
			return r
		elseif cmd == "morrer" then K.morrer(umLobo(a)); return true
		elseif cmd == "reviver" then local L = umLobo(); L.vida = CFG.Vida; L.estado = "Livre"; L.modelo:SetAttribute("Estado", nil); L.C.pararTudo(0); L.C.base("Repouso", 0); recalcular(L)
			if K.ehNoite() then setMod(L, "CacadorNoturno", {vel = CN.velocidade, esq = CN.esquiva, dano = CN.danoFisico}) end; return true
		elseif cmd == "recargas" then local L = umLobo(c); L.recargas = {}; L.energia = CFG.Energia.max; L.saltoCadeiaAte = nil; return true   -- 17/11: zera tambem a janela do encadeado
		elseif cmd == "flag" then K[a] = b; return true                                    -- ex.: ("flag", "percepcaoSemDono", false) = comportamento antigo
		elseif cmd == "clonarIA" then                                                       -- guardiao de TESTE sem dono, com IA de defesa
			local L0 = umLobo(); local m2 = L0.modelo:Clone(); m2.Name = b or "Lobo_Guardiao"; m2.Parent = AREA; m2:PivotTo(a)
			local L2 = registrar(m2, nil); L2.ia = {posto = a.Position, estado = "Calmo", dists = {}}; logc("IA", L2, "guardiao de teste criado (sem dono)"); return m2
		elseif cmd == "clonarSemDono" then                                                  -- lobo sem dono e SEM IA (so percepcao)
			local L0 = umLobo(); local m2 = L0.modelo:Clone(); m2.Name = b or "Lobo_SemDono"; m2.Parent = AREA; m2:PivotTo(a); registrar(m2, nil); return m2
		elseif cmd == "percebidos" then local L = umLobo(a); local r = {} if not L then return r end
			for al, v in pairs(L.percebidos) do r[al.Name] = string.format("%.1f%s", v.dist, v.escondido and " esc" or "") end; return r
		elseif cmd == "ia" then local L = umLobo(a); return L and L.ia and {estado = L.ia.estado, alvo = L.ia.alvo and L.ia.alvo.Name, energia = L.energia, estadoLobo = L.estado, pos = L.modelo:GetPivot().Position} or {}
		elseif cmd == "atacar" then local L = umLobo(a); return K.receberDano(L, c or 5, b)           -- b = alvo que ataca (Model)
		elseif cmd == "log" then local r = {} for i = math.max(1, #K.log - (a or 30) + 1), #K.log do if not b or K.log[i]:find(b, 1, true) then table.insert(r, K.log[i]) end end; return r
		elseif cmd == "chao" then local L = umLobo(); return K.chaoY(L, a)
		elseif cmd == "parado" then local L = umLobo(); L.parado = a; return true
		elseif cmd == "pivo" then local L = umLobo(b); L.modelo:PivotTo(a); return true
		elseif cmd == "clonar" then local L0 = umLobo(); local m2 = L0.modelo:Clone(); m2.Name = "Lobo_Clone"; m2.Parent = AREA; m2:PivotTo(a or CFrame.new(-680, 0, -680)); local L2 = registrar(m2, jogador); L2.parado = true; return m2
		end
	end
end
