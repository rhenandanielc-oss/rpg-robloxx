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
local aplicarDano                                  -- r8: definida mais abaixo (contrato de dano)
local function alvosPasta() return AREA:FindFirstChild("Alvos") end
-- r8 (18/11, "contrato de criatura", so arquivos do Lobo): alvo nao precisa mais estar na pasta de teste. Vale:
--   (a) Model com Humanoid vivo; (b) Model com atributo Criatura = true (convencao ja usada pelo Lobo Artico) ou
--   GuardiaoNinho (guardioes do jogo), com Vida > 0 e sem Incapacitado. As protecoes (dono, aliado, zona segura, PvP,
--   mesmo dono) continuam em protegido(). O Lobo tambem EXPOE o contrato (Criatura, Vida/VidaMax, ReceberDano).
local function ehCriatura(m) return m:GetAttribute("Criatura") == true or m:GetAttribute("GuardiaoNinho") == true end
local function alvoValido(m)
	if typeof(m) ~= "Instance" or not m:IsA("Model") or not m:IsDescendantOf(workspace) then return false end
	local h = m:FindFirstChildOfClass("Humanoid")
	if h then return h.Health > 0 and (m.PrimaryPart or m:FindFirstChild("HumanoidRootPart")) ~= nil end
	if ehCriatura(m) then
		if m:GetAttribute("Incapacitado") or m:GetAttribute("Estado") == "Morto" then return false end
		return (m:GetAttribute("Vida") or 1) > 0 and m:FindFirstChildWhichIsA("BasePart", true) ~= nil
	end
	return false
end
local function centro(m) local r = m.PrimaryPart or m:FindFirstChild("HumanoidRootPart"); return r and r.Position or (m:IsA("Model") and m:GetPivot().Position) end
-- sobe de uma parte ate o Model do alvo (personagem, criatura ou guardiao)
local function modeloAlvo(inst)
	local m = inst and inst:FindFirstAncestorOfClass("Model")
	while m do
		if m:FindFirstChildOfClass("Humanoid") or ehCriatura(m) then return m end
		m = m:FindFirstAncestorOfClass("Model")
	end
end
-- candidatos perto do lobo (partes num raio -> modelos alvo unicos); a pasta Alvos do ensaio continua valendo
local function candidatos(L, raio)
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude; op.FilterDescendantsInstances = {L.modelo}
	local vistos, lista = {}, {}
	for _, pt in ipairs(workspace:GetPartBoundsInRadius(L.modelo:GetPivot().Position, raio, op)) do
		local m = modeloAlvo(pt)
		if m and not vistos[m] then vistos[m] = true; table.insert(lista, m) end
	end
	local pa = alvosPasta()
	for _, a in ipairs(pa and pa:GetChildren() or {}) do if not vistos[a] then vistos[a] = true; table.insert(lista, a) end end
	return lista
end
-- r5 (18/11, auditoria de compatibilidade): alcance e contato medidos ate a SUPERFICIE do corpo do alvo (ponto mais proximo
-- das partes visiveis), nao ao centro. Antes: Mordida/Garra 0 em corpos grandes, Salto pousava dentro e o Instinto perdia
-- colossais. Devolve o ponto e a distancia HORIZONTAL ate ele.
-- 20/11 HITBOX DE CONTATO: corpo = capsulas nos ossos (acompanham a animacao, sem cauda/pelos); golpes medidos da BOCA/PATA.
local HB = CFG.Hitbox
local cacheCorpo = setmetatable({}, {__mode = "k"})
local function ignorarOsso(n) for _, k in ipairs(HB.ignorarOssos) do if n:find(k) then return true end end return false end
local function corpoDe(m)
	local c = cacheCorpo[m]
	if c ~= nil then return c or nil end
	local ossos, segs = {}, {}
	for _, d in ipairs(m:GetDescendants()) do if d:IsA("Bone") then ossos[d.Name] = d end end
	local esc = (m.GetScale and m:GetScale()) or 1
	if ossos.Peito and ossos.Pelve and ossos.Cabeca and ossos.Mandibula then          -- quadrupede no padrao do Lobo
		for _, sg in ipairs(HB.capsulasLobo) do
			local a, b = ossos[sg[1]], ossos[sg[2]]
			if a and b then table.insert(segs, {a, b, sg[3] * esc}) end
		end
	elseif next(ossos) then                                                             -- outra criatura com ossos: osso -> pai
		local _, sz = m:GetBoundingBox(); local r = math.min(sz.X, sz.Y, sz.Z) * HB.raioGenerico
		for _, b in pairs(ossos) do
			local pai = b.Parent
			if pai and pai:IsA("Bone") and not ignorarOsso(b.Name) and not ignorarOsso(pai.Name) then table.insert(segs, {pai, b, r}) end
		end
	end
	if #segs == 0 then cacheCorpo[m] = false; return nil end
	cacheCorpo[m] = segs; return segs
end
local function pontoSeg(p, a, b) local ab = b - a; local t = math.clamp((p - a):Dot(ab) / math.max(ab:Dot(ab), 1e-6), 0, 1); return a + ab * t end
-- distancia 3D de um ponto a SUPERFICIE do corpo (capsulas); nil se o alvo nao tem ossos
local function distCorpo(alvo, p)
	local segs = corpoDe(alvo); if not segs then return nil end
	local md, mq = math.huge, nil
	for _, sg in ipairs(segs) do
		local q = pontoSeg(p, sg[1].TransformedWorldCFrame.Position, sg[2].TransformedWorldCFrame.Position)
		local d = (p - q).Magnitude - sg[3]
		if d < md then md, mq = d, q end
	end
	return md, mq
end
K.distCorpo = distCorpo
local function ossoDe(m, nome) local x = m:FindFirstChild(nome, true); return x and x:IsA("Bone") and x or nil end
-- ponta do focinho do lobo (Mandibula + HB.boca na direcao pescoco -> mandibula) e patas dianteiras
local function boca(L)
	local mj, pc = ossoDe(L.modelo, "Mandibula"), ossoDe(L.modelo, "Pescoco1")
	if not (mj and pc) then local piv = L.modelo:GetPivot(); return piv.Position + piv.LookVector * 6.3 + Vector3.new(0, 6.3, 0) end
	local a, b = pc.TransformedWorldCFrame.Position, mj.TransformedWorldCFrame.Position
	return b + (b - a).Unit * HB.boca * ((L.modelo.GetScale and L.modelo:GetScale()) or 1)
end
local function patas(L)
	local r = {}
	for _, n in ipairs({"MaoD", "MaoE"}) do local o = ossoDe(L.modelo, n); if o then table.insert(r, o.TransformedWorldCFrame.Position) end end
	return r
end
K.boca = boca
K.patas = patas
-- contato de um golpe: menor distancia entre os pontos de ataque e o corpo; sem ossos no alvo = caixa das partes (como antes)
local function contato(alvo, pontos)
	local md = math.huge
	for _, p in ipairs(pontos) do
		local d = distCorpo(alvo, p)
		if d == nil then                                                                   -- fallback: superficie das partes visiveis
			for _, pt in ipairs(alvo:GetDescendants()) do
				if pt:IsA("BasePart") and pt.Transparency < 1 then
					local l = pt.CFrame:PointToObjectSpace(p); local h = pt.Size / 2
					local q = pt.CFrame:PointToWorldSpace(Vector3.new(math.clamp(l.X, -h.X, h.X), math.clamp(l.Y, -h.Y, h.Y), math.clamp(l.Z, -h.Z, h.Z)))
					d = math.min(d or math.huge, (p - q).Magnitude)
				end
			end
		end
		if d and d < md then md = d end
	end
	return md
end
K.contato = contato
-- r3 20/11: lado da BARRIGA do caido (onde estao as patas), perpendicular ao eixo Peito-Pelve: +1/-1 em nrm, mais a medida
function K.ladoBarriga(alvo)
	local pe, pv = alvo:FindFirstChild("Peito", true), alvo:FindFirstChild("Pelve", true)
	if not (pe and pv and pe:IsA("Bone") and pv:IsA("Bone")) then return nil end
	local P1, P2 = pe.TransformedWorldCFrame.Position, pv.TransformedWorldCFrame.Position
	local e = Vector3.new(P1.X - P2.X, 0, P1.Z - P2.Z); if e.Magnitude < 1e-3 then return nil end
	e = e.Unit; local nrm = Vector3.new(-e.Z, 0, e.X); local meio = (P1 + P2) / 2
	local soma, n = Vector3.zero, 0
	for _, nm in ipairs({"MaoE", "MaoD", "PeE", "PeD"}) do local o = alvo:FindFirstChild(nm, true); if o and o:IsA("Bone") then soma += o.TransformedWorldCFrame.Position; n += 1 end end
	local lp = 0
	if n > 0 then local d = soma / n - meio; lp = Vector3.new(d.X, 0, d.Z):Dot(nrm) end
	return (lp < 0) and -1 or 1, lp, nrm, P1, P2
end
-- r3 20/11: capsula do TRONCO para a mordida. Em pe/deitado sobre o peito: Pelve-Peito com raio 1,3 x escala. Deitado DE LADO
-- (atributo CaidoLado): a coluna fica na borda de cima e a barriga para o lado das patas, entao a capsula vai para o centro
-- real do tronco (ladoDesloc) com a meia largura medida (ladoRaio), as duas como fracao do comprimento Peito-Pelve.
function K.troncoAlvo(alvo)
	local E = CFG.Controle.estilo
	local pe, pv = alvo:FindFirstChild("Peito", true), alvo:FindFirstChild("Pelve", true)
	if not (pe and pv and pe:IsA("Bone") and pv:IsA("Bone")) then return nil end
	local P1, P2 = pe.TransformedWorldCFrame.Position, pv.TransformedWorldCFrame.Position
	if alvo:GetAttribute("CaidoLado") then
		local s, _, nrm = K.ladoBarriga(alvo)
		if s then
			local len = (P1 - P2).Magnitude; local off = nrm * (s * E.ladoDesloc * len)
			return P1 + off, P2 + off, E.ladoRaio * len, nrm * s
		end
	end
	return P1, P2, E.raioTronco * ((alvo.GetScale and alvo:GetScale()) or 1), nil
end
-- 20/11 r2: distancia a superficie do TRONCO (barriga/flanco = capsula Pelve-Peito); outras criaturas: o corpo todo
function K.distTronco(alvo, p)
	local P1, P2, raio = K.troncoAlvo(alvo)
	if P1 then return (p - pontoSeg(p, P2, P1)).Magnitude - raio end
	return contato(alvo, {p})
end
local function pontoProximo(alvo, de)
	-- 20/11: com ossos, superficie das capsulas (horizontal, como antes); sem ossos, caixa das partes
	local segs = corpoDe(alvo)
	if segs then
		local mq, md = nil, math.huge
		for _, sg in ipairs(segs) do
			local a, b = sg[1].TransformedWorldCFrame.Position, sg[2].TransformedWorldCFrame.Position
			local a2, b2 = Vector3.new(a.X, de.Y, a.Z), Vector3.new(b.X, de.Y, b.Z)
			local q = pontoSeg(de, a2, b2)
			local d = math.max(0, (Vector3.new(de.X, 0, de.Z) - Vector3.new(q.X, 0, q.Z)).Magnitude - sg[3])
			if d < md then
				local dir = Vector3.new(de.X - q.X, 0, de.Z - q.Z); dir = dir.Magnitude > 1e-3 and dir.Unit or Vector3.zero
				local qy = pontoSeg(de, a, b).Y
				md, mq = d, Vector3.new(q.X, qy, q.Z) + dir * sg[3]
			end
		end
		return mq, md
	end
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
	if L and m == L.modelo then return "proprio lobo" end
	if dono and m:GetAttribute("DonoUserId") == dono then return "mesmo dono" end   -- r8: criaturas do mesmo jogador
	local plr = Players:GetPlayerFromCharacter(m)
	if plr then
		if dono and plr.UserId == dono then return "dono" end
		if workspace:GetAttribute("PvPAtivo") ~= true then return "PvP desligado" end
	end
	if dono and m:GetAttribute("AliadoDe") == dono then return "aliado" end
	-- 19/11: criatura de OUTRO jogador so e alvo do lobo de um dono com PvP ligado (lobo selvagem segue podendo atacar: PvE)
	local donoAlvo = m:GetAttribute("DonoUserId")
	if dono and donoAlvo and donoAlvo ~= 0 and donoAlvo ~= dono and workspace:GetAttribute("PvPAtivo") ~= true then return "PvP desligado (criatura de outro jogador)" end
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
	if dt <= 0 then return end
	local pa = alvosPasta(); local lista = pa and pa:GetChildren() or {}
	for _, L in pairs(K.lobos) do for a in pairs(L.percebidos or {}) do table.insert(lista, a) end end   -- r8
	local feitos = {}                                   -- 19/11: alvo na pasta E percebido entrava 2x por quadro (2a passada = vel 0)
	for _, a in ipairs(lista) do
		if feitos[a] then continue end; feitos[a] = true
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
	-- r8: contrato de criatura (mesmo do Lobo Artico): Criatura, Vida/VidaMax e ReceberDano(valor, elemento, fonte)
	modelo:SetAttribute("Criatura", true); modelo:SetAttribute("VidaMax", CFG.Vida); modelo:SetAttribute("Vida", CFG.Vida)
	local fn = modelo:FindFirstChild("ReceberDano") or Instance.new("BindableFunction"); fn.Name = "ReceberDano"; fn.Parent = modelo
	fn.OnInvoke = function(valor, elemento, fonte)
		if type(valor) ~= "number" or valor <= 0 then return 0, "invalido" end
		local res = K.receberDano(L, valor, fonte)
		return res == "acertou" and valor or 0, res
	end
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
	if K.limparFinalizacao then pcall(K.limparFinalizacao, L, "lobo removido") end
	if K.limparControle then K.limparControle(L.modelo) end
	L.ativo = false; L.estado = "Removido"
	for _, t in ipairs(L.tarefas) do pcall(task.cancel, t) end
	L.mods = {}; pcall(recalcular, L)
	K.lobos[L.modelo] = nil
	log("lobo encerrado: " .. motivo)
end
function K.morrer(L)
	if K.limparFinalizacao then K.limparFinalizacao(L, "lobo morreu") end
	L.vida = 0; L.estado = "Morto"; L.mods = {}; recalcular(L)
	L.modelo:SetAttribute("Caido", nil); L.modelo:SetAttribute("CaidoAte", nil)
	for _, t in ipairs(L.tarefas) do pcall(task.cancel, t) end; L.tarefas = {}
	L.C.pararTudo(0.1); L.C.acao("Impacto", 0.05)
	L.modelo:SetAttribute("Estado", "Morto"); log("lobo morto")
end
-- dano recebido (para testar esquiva): rola a chance calculada no servidor
function K.receberDano(L, dano, origem)
	if not vivo(L) then return "morto" end
	if origem then L.atacadoPor = {alvo = origem, ate = os.clock() + 6} end     -- a IA trata como ameaca (se perceber o atacante)
	if L.estado ~= "Caido" and L.estado ~= "Levantando" and math.random() < L.esquiva then   -- 19/11: caido nao esquiva
		log("esquivou"); logc("ESQUIVA", L, "passiva (sorteio) contra " .. (origem and origem.Name or "?"))
		if K.esquivaDesloc then task.spawn(K.esquivaDesloc, L, origem, "passiva") end   -- 19/11: reacao visivel (sem mudar o resultado)
		return "esquivou"
	end
	L.vida -= dano; L.modelo:SetAttribute("Vida", math.max(0, L.vida)); if L.vida <= 0 then K.morrer(L) end
	logc("HABILIDADE", L, string.format("recebeu %.1f de %s (vida %.0f)", dano, origem and origem.Name or "?", math.max(0, L.vida)))
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
	local vistos = {}
	local piv = L.modelo:GetPivot().Position
	for _, a in ipairs(candidatos(L, IC.raio + 40)) do                 -- r8: qualquer criatura/personagem perto (nao so a pasta)
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
	if L.dashando then return false, "esquivando" end                                                 -- 19/11
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
-- 19/11 (IA estrategica): o golpe em curso fica publico no atributo EmAtaque (mesma convencao do combate dos dragoes),
-- para outras IAs (inclusive outro lobo) poderem esquivar/recuar. Limpo no fim do golpe.
local function anunciar(L, nome) L.modelo:SetAttribute("EmAtaque", nome) end
local function encerrar(L, nome) if L.modelo:GetAttribute("EmAtaque") == nome then L.modelo:SetAttribute("EmAtaque", nil) end end
local function presaMarcada(L, alvo) return L.presa ~= nil and L.presa.alvo == alvo and os.clock() < L.presa.ate end
-- r8: aplicacao do dano pelo CONTRATO. Ordem: (1) Nucleo do jogo (N.ferir), se existir no place - resistencias, guardioes,
-- reacao e UltimoCombate ficam com ele; (2) Humanoid; (3) ReceberDano do proprio alvo (esquiva/resistencias dele);
-- (4) guardiao/criatura so com Vida: desconta Vida (guardiao: so lobo COM dono, como no Nucleo; avisa IA_Eventos).
local Nucleo = nil
pcall(function()
	local cd = game:GetService("ServerScriptService"):FindFirstChild("Combate_Dragao")
	local mod = cd and cd:FindFirstChild("Nucleo")
	if mod and mod:IsA("ModuleScript") then Nucleo = require(mod) end
end)
aplicarDano = function(L, alvo, d, tipo)
	local agora = workspace:GetServerTimeNow()
	if Nucleo and Nucleo.ferir then
		local ok = Nucleo.ferir(L.modelo, alvo, d, nil, tipo, "moderado")
		return ok and d or 0, "Nucleo.ferir"
	end
	local h = alvo:FindFirstChildOfClass("Humanoid")
	local aplicado, via = 0, "?"
	if h then h:TakeDamage(d); aplicado, via = d, "Humanoid"
	else
		local fn = alvo:FindFirstChild("ReceberDano")
		if fn and fn:IsA("BindableFunction") then
			local ok, v = pcall(function() return fn:Invoke(d, nil, L.modelo) end)
			aplicado, via = (ok and type(v) == "number") and v or 0, "ReceberDano do alvo"
		elseif alvo:GetAttribute("GuardiaoNinho") then
			via = "Vida do guardiao (sem Nucleo no place)"
			if L.dono then
				local v = math.max(0, (alvo:GetAttribute("Vida") or alvo:GetAttribute("VidaMax") or 600) - d)
				alvo:SetAttribute("Vida", v); alvo:SetAttribute("UltimoDano", agora); aplicado = d
				local ev = game:GetService("ServerStorage"):FindFirstChild("IA_Eventos")
				if ev and ev:FindFirstChild("GuardiaoAtacado") then ev.GuardiaoAtacado:Fire(alvo, (L.dono and L.dono.Character) or L.modelo) end
				if v <= 0 then alvo:SetAttribute("Incapacitado", true); alvo:SetAttribute("Derrotado", agora) end
			else via ..= ": lobo sem dono nao fere guardiao (regra do Nucleo)" end
		elseif alvo:GetAttribute("Criatura") then
			local v = math.max(0, (alvo:GetAttribute("Vida") or 0) - d); alvo:SetAttribute("Vida", v); aplicado, via = d, "Vida da criatura"
		end
	end
	if aplicado > 0 then L.modelo:SetAttribute("UltimoCombate", agora); alvo:SetAttribute("UltimoCombate", agora) end
	return aplicado, via
end
local function causarDano(L, alvo, base, tipo)
	local pr = protegido(L, alvo)                                          -- r6: ultima barreira (ex.: alvo entrou na zona no voo)
	if pr then logc("PROTECAO", L, tipo .. " sem dano em " .. alvo.Name .. " (" .. pr .. ")"); return 0 end
	local mult = L.danoMult
	local marcada = presaMarcada(L, alvo)
	if marcada then mult += IC.marcaDano end                                   -- aditivo com noite/kit (teto do dano do kit nao muda)
	local d = base * mult
	local aplicado, via = aplicarDano(L, alvo, d, tipo)
	logc("HABILIDADE", L, string.format("%s acertou %s: %.1f (x%.2f%s) via %s -> aplicado %.1f", tipo, alvo.Name, d, mult, marcada and ", presa marcada" or "", via, aplicado))
	K.ultimoDano = {tipo = tipo, alvo = alvo.Name, dano = d, aplicado = aplicado, via = via, mult = mult, marcada = marcada}
	marcar(L, alvo)
	-- 19/11: controle por porte SO depois de acerto valido com dano (uma rolagem por golpe, no servidor)
	if aplicado > 0 and K.rolarControle and alvo.Parent and (alvo:GetAttribute("Vida") or 1) > 0 and alvo:GetAttribute("Estado") ~= "Morto" then
		local ok, R = pcall(K.rolarControle, L, alvo, tipo, aplicado, false, K.forcarControle)
		if not ok then logc("CONTROLE", L, "erro: " .. tostring(R))
		elseif R and R.porteA then
			logc("CONTROLE", L, string.format("%s -> %s: porte %s(%.1f %s, F%.0f) x %s(%.1f %s, F%.0f) rel %+d | chances queda %.0f%% manca %.0f%% lento %.0f%% | %s%s",
				tipo, alvo.Name, R.porteA.nome, R.porteA.medida, R.porteA.idade, R.porteA.forca, R.porteB.nome, R.porteB.medida, R.porteB.idade, R.porteB.forca, R.rel,
				R.cQ * 100, R.cM * 100, R.cL * 100, R.efeito, R.motivo and (" (" .. R.motivo .. ")") or ""))
		end
		K.ultimoControle = R
	end
	return aplicado
end
-- espera ate o tempo t do clipe (pelo relogio do servidor); cancela se o lobo deixar de existir
local function ate(L, t0, t) while vivo(L) and os.clock() - t0 < t do RS.Heartbeat:Wait() end return vivo(L) end

-- ------------------------------------------------------------------ CONTROLE POR PORTE, QUEDA E FINALIZACAO (19/11) [PROPOSTA]
-- Contrato geral das domesticaveis (prototipo no Lobo; as outras especies adotam nos chats delas):
--   ALVO expoe: PorteOmbro ou PorteComprimento (studs, adulto), Idade, Forca (indice §0c), Domesticavel = true, DonoUserId
--   (0 = selvagem), ImuneDerrubada / ImuneLentidao (opcionais).
--   ESTADOS TEMPORARIOS (atributos no alvo, decididos so no servidor, so depois de acerto com dano > 0):
--     LentidaoControle (0..0,6) + LentidaoAte; Mancando = true + LentidaoAte; Caido = true + CaidoAte (Vida > 0).
--     Caido NUNCA usa Incapacitado (os sistemas atuais deixam de mirar quem esta Incapacitado).
--   DESFECHO (so por finalizacao anunciada com contato real): selvagem -> Vida 0 + Estado "Morto" (sem loot/respawn aqui);
--     criatura de jogador -> RetiradaDeCombate + Incapacitado (vai ao refugio; integracao pendente); humano -> nunca.
local CT = CFG.Controle
K.ultimoStun, K.drCtrl = {}, {}
local function classePorte(m)
	local L2 = K.lobos[m]
	local ombro, comp, idade, forca
	if L2 then   -- lobo do kit: porte oficial; atributos so para os testes de porte simulado (registrado no log)
		ombro, idade, forca = m:GetAttribute("PorteOmbro") or CT.porte.ombro, m:GetAttribute("Idade") or CT.porte.idade, m:GetAttribute("Forca") or CT.porte.forca
	else ombro, comp, idade, forca = m:GetAttribute("PorteOmbro"), m:GetAttribute("PorteComprimento"), m:GetAttribute("Idade") or "Adulto", m:GetAttribute("Forca") end
	local medida, fonte = ombro, "ombro"
	if not medida and comp then medida, fonte = comp / 2.5, "comprimento/2,5" end
	if not medida then local _, sz = m:GetBoundingBox(); medida, fonte = sz.Y * 0.65, "estimado pela caixa" end
	medida *= (CT.tamanhoIdade[idade] or 1)
	local nome, idx = "colossal", 4
	for i, c in ipairs(CT.classes) do if medida < c[2] then nome, idx = c[1], i; break end end
	forca = (forca or 20) * (CT.forcaIdade[idade] or 1)
	return {nome = nome, idx = idx, medida = medida, fonte = fonte, forca = forca, idade = idade}
end
K.classePorte = classePorte
local function deJogador(m) return (m:GetAttribute("DonoUserId") or 0) ~= 0 end
local function ehDomesticavel(m) return K.lobos[m] ~= nil or m:GetAttribute("Domesticavel") == true or m:GetAttribute("GuardiaoNinho") ~= nil end
local function agoraS() return workspace:GetServerTimeNow() end
-- aplica (ou so simula) o controle depois de um acerto valido; devolve o resultado para log/medicao
function K.rolarControle(L, alvo, tipo, aplicado, simular, forcar)
	local g = CT.golpes[tipo]
	if not g or not alvo or not alvo.Parent then return {efeito = "nenhum", motivo = "golpe sem controle"} end
	if Players:GetPlayerFromCharacter(alvo) then return {efeito = "nenhum", motivo = "humano: regra so de criatura"} end
	if not ehDomesticavel(alvo) then return {efeito = "nenhum", motivo = "nao e domesticavel (fauna de recurso/outro)"} end
	if not simular and (aplicado or 0) <= 0 then return {efeito = "nenhum", motivo = "sem dano valido (esquiva/protecao)"} end
	local pa, pb = classePorte(L.modelo), classePorte(alvo)
	local rel = math.clamp(pa.idx - pb.idx, -3, 3)
	local fP = CT.porteRelativo[rel] or 1
	local fF = math.clamp(pa.forca / math.max(pb.forca, 1), CT.forcaMinMax[1], CT.forcaMinMax[2])
	local k = g.impacto * fP * fF
	local cQ = (g.impacto >= CT.queda.impactoMin and not alvo:GetAttribute("ImuneDerrubada")) and CT.queda.chance * k or 0
	local cM = (g.impacto >= CT.manca.impactoMin and not alvo:GetAttribute("ImuneLentidao")) and CT.manca.chance * k or 0
	local cL = (not alvo:GetAttribute("ImuneLentidao")) and CT.lento.chance * k or 0
	local R = {porteA = pa, porteB = pb, rel = rel, fP = fP, fF = fF, cQ = cQ, cM = cM, cL = cL, efeito = "nenhum"}
	local t = agoraS()
	local pvp = deJogador(alvo) and L.dono ~= nil         -- PvP = criatura de jogador atacada por criatura de outro jogador (selvagem = PvE)
	local dr = K.drCtrl[alvo]
	if pvp and dr and t > dr.ate + CT.pvp.janela then dr = nil; K.drCtrl[alvo] = nil end
	local u = math.random()
	local efeito
	if forcar then efeito = forcar
	elseif u < cQ then efeito = "queda" elseif u < cQ + cM then efeito = "manca" elseif u < cQ + cM + cL then efeito = "lento" end
	if not efeito then R.motivo = string.format("sorteio %.2f acima das chances", u); return R end
	-- regras oficiais: >= 4 s entre atordoamentos (queda); PvP: duracao curta, resistencia a repeticao, imunidade temporaria
	-- r2: os 4 s contam a partir de quando o alvo TERMINA de levantar (de pe), nao do inicio da queda: sem derrubada em cadeia
	if efeito == "queda" and K.ultimoStun[alvo] and t < K.ultimoStun[alvo] + CT.queda.intervaloMin then
		R.motivo = string.format("queda negada: de pe ha %.1f s (< %d s)", math.max(0, t - K.ultimoStun[alvo]), CT.queda.intervaloMin); efeito = "manca"
	end
	if pvp and dr and dr.imuneAte and t < dr.imuneAte then R.efeito = "nenhum"; R.motivo = "imune a controle (PvP, repeticao)"; return R end
	local base = (efeito == "queda" and CT.queda.dur) or (efeito == "manca" and CT.manca.dur) or CT.lento.dur
	local dur = base * (CT.duracaoPorte[pb.nome] or 1)
	if efeito == "queda" and CT.queda.extraEnfraquecido then                      -- r2: enfraquecido (Vida <= limite de finalizar) levanta mais devagar
		local vF = (alvo:GetAttribute("Vida") or 1) / math.max(alvo:GetAttribute("VidaMax") or 1, 1)
		if vF <= CT.finalizar.vidaAlvoMax then dur += CT.queda.extraEnfraquecido * (CT.duracaoPorte[pb.nome] or 1); R.enfraquecido = true end
	end
	if pvp then dur *= CT.pvp.fatorDur * (0.5 ^ (dr and dr.n or 0)) end
	R.efeito, R.dur = efeito, dur
	R.fracao = (efeito == "manca" and CT.manca.fracao) or (efeito == "lento" and CT.lento.fracao) or nil
	if simular then return R end
	if pvp then
		dr = dr or {n = 0, ate = 0}; dr.n += 1; dr.ate = t
		if dr.n >= CT.pvp.maxSeguidos then dr.imuneAte = t + dur + CT.pvp.imuneSeg end
		K.drCtrl[alvo] = dr
	end
	K.aplicarEstado(L, alvo, efeito, dur, R.fracao)
	return R
end
-- estados temporarios: no lobo do kit mexem no estado/velocidade; em outro modelo so os atributos do contrato
-- r3 20/11: escolhe o lado em que o caido tomba. Preferido: cair para LONGE do atacante (barriga voltada para ele). Confere,
-- na escala do alvo, se ha espaco para as pernas (lado da barriga) e para as costas (lado oposto) - paredes e outros corpos
-- por raio horizontal, chao/desnivel por raio para baixo. Nenhum lado livre: o de mais espaco, e o log registra a limitacao.
local function espacoLado(alvo, piv, dir, s)
	local QL = CT.queda.lateral
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude
	local ign = {alvo}; for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(ign, pl.Character) end end
	rp.FilterDescendantsInstances = ign
	local o = piv.Position + Vector3.new(0, QL.alturaSonda * s, 0)
	local perna, costas = QL.pernas * s, QL.costas * s
	local h1 = workspace:Raycast(o, dir * perna, rp); local h2 = workspace:Raycast(o, -dir * costas, rp)
	local livreP = h1 and (h1.Position - o).Magnitude or perna
	local livreC = h2 and (h2.Position - o).Magnitude or costas
	local motivo = nil
	if h1 then motivo = "pernas batem em " .. h1.Instance.Name elseif h2 then motivo = "costas batem em " .. h2.Instance.Name end
	if not motivo then
		for _, ponta in ipairs({o + dir * perna * 0.8, o - dir * costas * 0.8}) do
			local hc = workspace:Raycast(ponta, Vector3.new(0, -(QL.alturaSonda * s + QL.desnivelMax * s + 1), 0), rp)
			if not hc then motivo = "sem chao"; break end
			if math.abs(hc.Position.Y - piv.Position.Y) > QL.desnivelMax * s then motivo = string.format("desnivel %.1f", hc.Position.Y - piv.Position.Y); break end
		end
	end
	return motivo, livreP / perna + livreC / costas
end
function K.escolherLadoQueda(L, alvo)
	local QL = CT.queda.lateral
	local piv = alvo:GetPivot(); local s = (alvo.GetScale and alvo:GetScale()) or 1
	local pA = L.modelo:GetPivot().Position
	local dir = Vector3.new(piv.Position.X - pA.X, 0, piv.Position.Z - pA.Z)
	local rv = Vector3.new(piv.RightVector.X, 0, piv.RightVector.Z).Unit
	local function barriga(lado) return rv * QL.barrigaE * (lado == "E" and 1 or -1) end
	-- barriga voltada para o atacante: o lado cuja barriga aponta contra o golpe (dir vai do atacante para o alvo)
	local pref = (dir.Magnitude < 0.1 or barriga("E"):Dot(-dir.Unit) >= 0) and "E" or "D"
	local outro = (pref == "E") and "D" or "E"
	local res = {}
	for _, lado in ipairs({pref, outro}) do
		local m, folga = espacoLado(alvo, piv, barriga(lado), s)
		res[lado] = {m = m, folga = folga}
		if not m then return lado, (lado == pref) and "barriga para o atacante" or ("outro lado: " .. tostring(res[pref].m)) end
	end
	local lado = (res.E.folga >= res.D.folga) and "E" or "D"
	return lado, string.format("LIMITACAO: nenhum lado livre (E: %s; D: %s) - usa o de mais espaco", tostring(res.E.m), tostring(res.D.m))
end
function K.aplicarEstado(L, alvo, efeito, dur, fracao)
	local t = agoraS()
	local L2 = K.lobos[alvo]
	if efeito == "queda" then
		local QL = CT.queda.lateral
		local ladoQ, porqueQ = "E", "-"
		-- r3: ja caido de lado (nova queda antes de levantar): mantem o lado e so prolonga, sem repetir o tombo
		local jaCaido = L2 and L2.estado == "Caido" and alvo:GetAttribute("CaidoLado")
		if jaCaido then ladoQ, porqueQ = jaCaido, "ja estava caido"
		elseif L2 then ladoQ, porqueQ = K.escolherLadoQueda(L, alvo) end
		local okC, cl = pcall(LA.clipe, QL.clipeLevantar .. ladoQ)
		local tLev = (L2 and okC and cl and cl.quadros) and (cl.quadros / cl.fps / CT.queda.levantarVel) or (L2 and 1.6 or 0)
		K.ultimoStun[alvo] = t + dur + tLev                                       -- fim do levantar (de pe)
		alvo:SetAttribute("Caido", true); alvo:SetAttribute("CaidoAte", t + dur)
		if L2 and vivo(L2) then
			K.limparFinalizacao(L2, "derrubado durante a finalizacao")
			-- interrompe tudo o que estava em curso (habilidade, golpe andando, esquiva): sem dano atrasado de quem caiu
			for _, tk in ipairs(L2.tarefas) do pcall(task.cancel, tk) end; L2.tarefas = {}
			L2.modelo:SetAttribute("EmAtaque", nil); L2.dashando = false
			if L2.ia then L2.ia.mov = nil; L2.ia.andando = false end
			pcall(function() if K.IA2 and K.IA2.pararMov and L2.ia then K.IA2.pararMov(L2, L2.ia, QL.clipeCaido .. ladoQ) end end)
			L2.estado = "Caido"; L2.basicoAte = nil
			-- r3 20/11: tombo LATERAL proprio (QuedaLado) -> laco de lado respirando (CaidoLado); nada de Deitado (descanso)
			local fq = nil
			if jaCaido then logc("CONTROLE", L2, string.format("continua caido de lado %s (nova queda so prolonga)", ladoQ))
			else
				alvo:SetAttribute("CaidoLado", ladoQ)
				L2.C.pararTudo(0.1); fq = L2.C.acao(QL.clipeQueda .. ladoQ, 0.08)
				logc("CONTROLE", L2, string.format("tomba de lado %s (%s)", ladoQ, porqueQ))
			end
			L2.quedaId = (L2.quedaId or 0) + 1; local id = L2.quedaId
			task.delay(math.max(0.2, ((fq and fq.Length > 0) and fq.Length or 1.1) - 0.12), function()
				if L2.estado == "Caido" and L2.quedaId == id then L2.C.base(QL.clipeCaido .. ladoQ, 0.12) end
			end)
			task.delay(dur, function() K.levantar(L2, id) end)
		else
			task.delay(dur, function() if alvo.Parent and (alvo:GetAttribute("CaidoAte") or 0) <= agoraS() + 0.05 then alvo:SetAttribute("Caido", nil) end end)
		end
	else
		local fr = math.min(fracao or 0, CT.tetoLentidao)
		alvo:SetAttribute("LentidaoControle", fr); alvo:SetAttribute("LentidaoAte", t + dur)
		if efeito == "manca" then alvo:SetAttribute("Mancando", true) end
		if L2 then setMod(L2, "Controle", {vel = -fr}) end
		task.delay(dur, function()
			if not alvo.Parent or (alvo:GetAttribute("LentidaoAte") or 0) > agoraS() + 0.05 then return end
			alvo:SetAttribute("LentidaoControle", nil); alvo:SetAttribute("LentidaoAte", nil); alvo:SetAttribute("Mancando", nil)
			if L2 and L2.mods.Controle then setMod(L2, "Controle", nil) end
		end)
	end
	logc("CONTROLE", L, string.format("%s em %s por %.1f s%s", efeito, alvo.Name, dur, fracao and string.format(" (lentidao %.0f%%)", math.min(fracao, CT.tetoLentidao) * 100) or ""))
	EVENTO:FireAllClients("Controle", alvo, efeito, dur)
end
function K.prolongarQueda(alvo, ate)
	if not (alvo and alvo.Parent) or ate <= (alvo:GetAttribute("CaidoAte") or 0) then return end
	alvo:SetAttribute("Caido", true); alvo:SetAttribute("CaidoAte", ate)
	if K.ultimoStun[alvo] then K.ultimoStun[alvo] = math.max(K.ultimoStun[alvo], ate + 1.6) end
	local L2 = K.lobos[alvo]
	if L2 and L2.estado == "Caido" then
		L2.quedaId = (L2.quedaId or 0) + 1; local id = L2.quedaId
		task.delay(ate - agoraS(), function() K.levantar(L2, id) end)
	elseif not L2 then
		task.delay(ate - agoraS(), function() if alvo.Parent and (alvo:GetAttribute("CaidoAte") or 0) <= agoraS() + 0.05 then alvo:SetAttribute("Caido", nil) end end)
	end
end
function K.levantar(L2, id)
	if not vivo(L2) or L2.estado ~= "Caido" or (id and L2.quedaId ~= id) then return end
	L2.estado = "Levantando"
	local lado = L2.modelo:GetAttribute("CaidoLado") or "E"
	local f = L2.C.acao(CT.queda.lateral.clipeLevantar .. lado, 0.15, CT.queda.levantarVel)   -- r3: levanta pelo lado em que caiu
	logc("CONTROLE", L2, "levanta (queda terminou)")
	-- r3: duracao pelo clipe (quadros/fps); a faixa recem-carregada tem Length 0 e o levantar "terminava" na hora
	local okL, clL = pcall(LA.clipe, CT.queda.lateral.clipeLevantar .. lado)
	local durL = (okL and clL and clL.quadros) and (clL.quadros / clL.fps) or ((f and f.Length > 0) and f.Length or 1.9)
	task.delay(durL / CT.queda.levantarVel, function()
		if L2.estado == "Levantando" and vivo(L2) then
			L2.estado = "Livre"; L2.C.base("Repouso", 0.2)
			L2.modelo:SetAttribute("Caido", nil); L2.modelo:SetAttribute("CaidoAte", nil); L2.modelo:SetAttribute("CaidoLado", nil)
		end
	end)
end
-- desfecho de criatura caida (so via finalizacao valida)
local function desfecho(L, alvo)
	local L2 = K.lobos[alvo]
	if deJogador(alvo) then
		alvo:SetAttribute("RetiradaDeCombate", true); alvo:SetAttribute("Incapacitado", true); alvo:SetAttribute("Caido", nil)
		if L2 then L2.estado = "Retirado"; for _, tk in ipairs(L2.tarefas) do pcall(task.cancel, tk) end; L2.tarefas = {} end
		logc("CONTROLE", L, alvo.Name .. ": criatura de jogador RETIRADA da luta (refugio: integracao pendente; sem morte permanente)")
		return "retirada"
	end
	if L2 then
		L2.vida = 0; L2.estado = "Morto"; L2.mods = {}; recalcular(L2)
		for _, tk in ipairs(L2.tarefas) do pcall(task.cancel, tk) end; L2.tarefas = {}
		L2.C.base(CT.queda.lateral.clipeCaido .. (alvo:GetAttribute("CaidoLado") or "E"), 0.2, 0)   -- r3: fica de lado, parado (sem respirar)
	end
	alvo:SetAttribute("Vida", 0); alvo:SetAttribute("Estado", "Morto"); alvo:SetAttribute("Incapacitado", true); alvo:SetAttribute("Caido", nil)
	logc("CONTROLE", L, alvo.Name .. ": selvagem finalizado (prototipo: sem loot/respawn)")
	return "morte"
end
-- FINALIZACAO anunciada: valida, anuncia (rosnado), confere de novo no contato; qualquer condicao falhando = cancela sem dano
function K.finalizar(L, alvo, motivo, encaixe)
	local F = CT.finalizar
	local function pode(fase)
		if not vivo(L) then return false, "lobo fora de acao" end
		if not (alvo and alvo.Parent) then return false, "alvo removido" end
		if Players:GetPlayerFromCharacter(alvo) then return false, "humano nao e finalizavel" end
		if not alvo:GetAttribute("Caido") or (alvo:GetAttribute("CaidoAte") or 0) <= agoraS() then return false, "alvo levantou" end
		local pr = protegido(L, alvo); if pr then return false, "alvo protegido (" .. pr .. ")" end
		-- r2: histerese. O inicio exige alcance/cone normais; durante anuncio e bote ha folga (+1 stud, +30 graus), senao o ponto
		-- mais proximo do corpo que esta caindo troca de lado e cancelava no mesmo quadro do anuncio (ensaio 19/11)
		local folgaA, folgaC = 0, 0
		if fase ~= "inicio" then folgaA, folgaC = 1.0, 30 end
		local piv = L.modelo:GetPivot(); local sp, ds = pontoProximo(alvo, piv.Position)
		if ds > F.alcance + folgaA then return false, string.format("fora do alcance (%.1f)", ds) end
		local d = Vector3.new(sp.X - piv.Position.X, 0, sp.Z - piv.Position.Z)
		local semCone = encaixe ~= nil and (fase == "inicio" or fase == "anuncio")   -- r2: com encaixe, o cone vale depois do giro
		if not semCone and d.Magnitude > 0.1 and math.deg(math.acos(math.clamp(d.Unit:Dot(piv.LookVector), -1, 1))) > F.cone / 2 + folgaC then return false, "alvo fora do cone" end
		if not linhaDeVisao(L, alvo) then return false, "sem linha de visao" end
		return true
	end
	if L.estado ~= "Livre" then return false, "ocupado (" .. tostring(L.estado) .. ")" end
	if L.virando then return false, "girando no lugar" end                    -- r3: o giro aplica 90 graus no fim e virava o lobo de costas
	local ok, por = pode("inicio"); if not ok then logc("CONTROLE", L, "finalizacao recusada: " .. por); return false, por end
	L.estado = "Finalizando"; L.finalizando = alvo; anunciar(L, "Finalizacao"); alvo:SetAttribute("FinalizacaoDe", L.modelo.Name)
	L.C.acao(F.clipeAnuncio, 0.1)
	logc("CONTROLE", L, string.format("FINALIZACAO anunciada em %s (%s)", alvo.Name, motivo or "-"))
	EVENTO:FireAllClients("Finalizacao", L.modelo, alvo, F.anuncio)
	tarefa(L, function()
		local function cancelar(p)
			logc("CONTROLE", L, "finalizacao CANCELADA: " .. p .. " (sem dano)")
			if alvo.Parent then alvo:SetAttribute("FinalizacaoDe", nil); alvo:SetAttribute("MordidoPor", nil) end
			L.finalizando = nil
			encerrar(L, "Finalizacao"); if vivo(L) and L.estado == "Finalizando" then L.estado = "Livre"; L.C.base("Repouso", 0.2) end
			K.ultimaFinalizacao = {resultado = "cancelada", motivo = p, lobo = L.modelo.Name, alvo = alvo.Name}
		end
		local t0 = os.clock()
		local pivE0 = L.modelo:GetPivot()
		if encaixe then                                                           -- encaixe so pequeno (nada de deslizar longe)
			local dE = Vector3.new(encaixe.X - pivE0.X, 0, encaixe.Z - pivE0.Z).Magnitude
			local _, yA = pivE0:ToOrientation(); local _, yB = encaixe:ToOrientation()
			local dG = math.abs(math.deg((yB - yA + math.pi) % (2 * math.pi) - math.pi))
			if dE > CT.estilo.ajusteMax or dG > CT.estilo.giroMax then encaixe = nil; logc("CONTROLE", L, string.format("encaixe grande demais (%.1f studs, %.0f graus): sem encaixe", dE, dG))
			else encaixe = CFrame.new(Vector3.new(encaixe.X, pivE0.Y, encaixe.Z)) * CFrame.fromOrientation(0, yB, 0) end
		end
		while os.clock() - t0 < F.anuncio do
			RS.Heartbeat:Wait()
			if L.estado ~= "Finalizando" then return cancelar("lobo interrompido") end
			local ok2, p2 = pode("anuncio"); if not ok2 then return cancelar(p2) end
			if encaixe then                                                       -- r2: assenta ao lado do flanco durante o rosnado
				local u = math.clamp((os.clock() - t0) / F.anuncio, 0, 1)
				L.modelo:PivotTo(pivE0:Lerp(encaixe, 1 - (1 - u) ^ 2))
			end
		end
		-- 20/11 r2 FINALIZACAO DO LOBO: mordida no FLANCO/barriga do caido + sacudidas da PROPRIA cabeca (Hab_MordidaFlanco).
		-- O alvo NAO e puxado nem girado; a boca precisa encostar no tronco no Contato e continuar encostada ate soltar.
		local E = CT.estilo
		local clipeF = alvo:GetAttribute("CaidoLado") and E.clipeLado or E.clipe   -- r3: alvo de lado = boca na barriga lateral
		local cl = LA.clipe(clipeF); local tC, tS = 0.5, 1.85
		for _, mk in ipairs(cl.marcadores) do if mk.nome == "Contato" then tC = mk.t elseif mk.nome == "Solta" then tS = mk.t end end
		local fl = L.C.acao(clipeF, 0.12)
		local function soltar() if alvo.Parent then alvo:SetAttribute("MordidoPor", nil) end; if fl then pcall(function() fl:Stop(0.25) end) end end
		local t1 = os.clock()
		while os.clock() - t1 < tC do
			RS.Heartbeat:Wait()
			if L.estado ~= "Finalizando" then soltar(); return cancelar("lobo interrompido no bote") end
			local okB, pB = pode("bote"); if not okB then soltar(); return cancelar(pB .. " (no bote)") end
		end
		local d0 = K.distTronco(alvo, boca(L))
		if d0 > E.contato then soltar(); return cancelar(string.format("boca a %.2f da barriga no contato (sem encaixe)", d0)) end
		K.prolongarQueda(alvo, agoraS() + (tS - tC) + 0.8)                      -- segura a queda enquanto morde
		alvo:SetAttribute("MordidoPor", L.modelo.Name)
		EVENTO:FireAllClients("MordidaFlanco", L.modelo, alvo, tS - tC)
		local pivA0 = alvo:GetPivot()
		logc("CONTROLE", L, string.format("FINALIZACAO: mordeu o flanco de %s (boca a %.2f da barriga); sacode a cabeca", alvo.Name, d0))
		local vida0, dmin, dmax = L.vida, d0, d0
		while os.clock() - t1 < tS do
			RS.Heartbeat:Wait()
			if L.estado ~= "Finalizando" then soltar(); return cancelar("lobo interrompido durante a mordida") end
			if L.vida < vida0 - E.cancelaDano then soltar(); return cancelar("lobo ferido: soltou a mordida") end
			local okS, pS = pode("segurar"); if not okS then soltar(); return cancelar(pS .. " (durante a mordida)") end
			local d = K.distTronco(alvo, boca(L)); dmin = math.min(dmin, d); dmax = math.max(dmax, d)
			if d > E.contatoSegurar then soltar(); return cancelar(string.format("perdeu o contato com a barriga (%.2f)", d)) end
		end
		local moveu = (alvo:GetPivot().Position - pivA0.Position).Magnitude
		K.ultimaMordidaFlanco = {dmin = dmin, dmax = dmax, alvoMoveu = moveu}
		logc("CONTROLE", L, string.format("segurou %.1f s: boca->barriga %.2f a %.2f; corpo do alvo moveu %.2f", tS - tC, dmin, dmax, moveu))
		if alvo.Parent then alvo:SetAttribute("MordidoPor", nil) end
		local r = desfecho(L, alvo)
		if alvo.Parent then alvo:SetAttribute("FinalizacaoDe", nil) end
		L.finalizando = nil
		K.ultimaFinalizacao = {resultado = r, lobo = L.modelo.Name, alvo = alvo.Name, estilo = E.nome}
		ate(L, t1, cl.quadros / cl.fps)
		encerrar(L, "Finalizacao")
		if vivo(L) and L.estado == "Finalizando" then L.estado = "Livre"; L.C.base("Repouso", 0.2) end
	end)
	return true
end
-- limpeza: lobo removido/morto nao deixa estado preso em ninguem
-- limpeza: finalizacao interrompida por fora (lobo derrubado, morto ou removido) nao deixa atributo preso no alvo
function K.limparFinalizacao(L, motivo)
	local a = L.finalizando; if not a then return end
	L.finalizando = nil
	if a.Parent then a:SetAttribute("FinalizacaoDe", nil); a:SetAttribute("MordidoPor", nil) end
	if L.modelo.Parent then encerrar(L, "Finalizacao") end
	logc("CONTROLE", L, "finalizacao CANCELADA: " .. motivo .. " (sem dano)")
	K.ultimaFinalizacao = {resultado = "cancelada", motivo = motivo, lobo = L.modelo.Name, alvo = a.Name}
end
function K.limparControle(m)
	K.ultimoStun[m] = nil; K.drCtrl[m] = nil
end


-- ------------------------------------------------------------------ basicos (fora dos slots)
local function basico(L, nome)
	local c = CFG.Basico[nome]
	local ok, por = podeUsar(L, nome, c); if not ok then return false, por end
	-- r7 (18/11, pedido do usuario: atacar ANDANDO para haver PvP de verdade): em movimento o basico NAO para o lobo.
	-- Usa o clipe PARCIAL (cabeca/pescoco; Garra + pata dianteira D) por cima da marcha e o estado continua "Livre"
	-- (o seguir/IA seguem andando); L.basicoAte impede outra habilidade ate o fim do golpe. Parado = clipe inteiro, como antes.
	local andando = ((L.seguindo and not L.parado and not L.virando) or (L.ia and L.ia.andando)) and true or false   -- r7b: so em movimento real
	gastar(L, nome, c); anunciar(L, nome)
	local clip = andando and (c.clipe .. "_Andando") or c.clipe
	local cl = LA.clipe(clip); local tC
	for _, mk in ipairs(cl.marcadores) do if mk.nome == c.marcador then tC = mk.t end end
	if andando then L.basicoAte = os.clock() + cl.quadros / cl.fps else L.estado = nome end
	L.C.acao(clip, 0.08)
	logc("HABILIDADE", L, nome .. (andando and " ANDANDO (clipe parcial, marcha continua)" or " parado"))
	tarefa(L, function()
		local t0 = os.clock()
		if not ate(L, t0, tC or 0.5) then return end
		-- 20/11: acerta so com CONTATO real: boca (Mordida) ou patas dianteiras (Garra) ate HB.contato da superficie do corpo
		local pontos = (nome == "Garra") and patas(L) or {boca(L)}
		local lim = (nome == "Garra") and HB.contatoGarra or HB.contatoMordida
		local melhor, md = nil, math.huge
		for _, a in ipairs(candidatos(L, c.alcance + 25)) do            -- r8
			if alvoPermitido(L, a) then
				local dc = contato(a, pontos)
				if dc <= lim and dc < md and linhaDeVisao(L, a) then melhor, md = a, dc end
			end
		end
		if melhor then causarDano(L, melhor, c.dano, nome); logc("HITBOX", L, string.format("%s contato %.2f (limite %.1f)", nome, md, lim))
		else
			local mais, dm = nil, math.huge
			for _, a in ipairs(candidatos(L, 12)) do if alvoPermitido(L, a) then local dc = contato(a, pontos); if dc < dm then mais, dm = a, dc end end end
			logc("HABILIDADE", L, nome .. " sem alvo" .. (mais and string.format(" (%s a %.2f do %s; limite %.1f)", mais.Name, dm, nome == "Garra" and "golpe da pata" or "focinho", lim) or ""))
		end
		ate(L, t0, cl.quadros / cl.fps); encerrar(L, nome); if vivo(L) and not andando then L.estado = "Livre" end
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
	if L.dashando then return false, "esquivando" end                                                 -- 19/11
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
	L.estado = "SaltoPredatorio"; if alvo then anunciar(L, "SaltoPredatorio") end
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
		-- 20/11: acerto so com CONTATO da boca/patas no corpo do alvo ao pousar (antes: 8,5 studs da anca ate a caixa)
		local pts = patas(L); table.insert(pts, boca(L))
		local dAlvo = alvo and alvoValido(alvo) and contato(alvo, pts) or nil
		if alvo and not parou and dAlvo and dAlvo <= HB.contatoSalto then
			dano = causarDano(L, alvo, CFG.Basico.Mordida.dano * SP.multDano, "SaltoPredatorio"); acertou = true
		elseif alvo then logc("HABILIDADE", L, "salto sem acerto" .. (parou and " (obstaculo)" or string.format(" (boca/patas a %.2f do corpo; limite %.1f)", dAlvo or -1, HB.contatoSalto)))
		else logc("HABILIDADE", L, "salto de mobilidade pousou" .. (parou and " (obstaculo)" or "")) end
		EVENTO:FireAllClients("SaltoPouso", L.modelo, {acertou = acertou, parou = parou ~= nil, cadeia = cadeia or false, pos = fim})
		K.ultimoSalto = {dist = (Vector3.new(fim.X, 0, fim.Z) - Vector3.new(p0.Position.X, 0, p0.Position.Z)).Magnitude, alvo = alvo ~= nil,
			cadeia = cadeia, custo = custo, tempoVoo = os.clock() - t0 - SP.decolagem, apice = hMax, desnivel = fim.Y - p0.Position.Y,
			parou = parou ~= nil, acertou = acertou, dano = dano, dAlvo = dAlvo, recuo = recuo, energia = L.energia, pouso = fim,
			planejado = destino, antecipou = anteci.Magnitude, inclinacao = math.deg(inclin or 0), recarga = L.recargas.SaltoPredatorio and (L.recargas.SaltoPredatorio - os.clock()) or 0}
		ate(L, t0, SP.golpe + SP.planeio + 0.49); encerrar(L, "SaltoPredatorio"); if vivo(L) then L.estado = "Livre" end
		if not cadeia and vivo(L) then L.saltoCadeiaAte = os.clock() + SP.cadeiaJanela end   -- abre a janela do 2o salto
	end)
	return true
end

-- ------------------------------------------------------------------ ESQUIVA VISIVEL (19/11) [PROPOSTA]
-- Pedido do usuario: quando uma esquiva REALMENTE ocorre (ativa da IA ou passiva sorteada no dano), o lobo da um pequeno
-- "teleporte" lateral muito rapido; o cliente mostra silhueta residual na saida e faixas verdes de ar no trajeto.
-- O SERVIDOR decide e valida: trajeto (paredes), chao nas patas de tras e da frente (borda/desnivel), corpo de outra
-- criatura no destino, zona segura e territorio (lobo com IA). Prefere o lado para onde o atacante NAO olha (sai do cone).
-- Nenhum lado seguro = reacao curta no lugar (registrada). Sem invulnerabilidade, sem bonus: a passiva mantem o sorteio e o
-- dano atuais (so ganha a reacao); a ativa (IA) sai de fato da linha do golpe. Intervalo minimo evita deslocamento duplo.
local EV = CFG.EsquivaVisual
function K.esquivaDesloc(L, origem, tipo)
	if not vivo(L) then return false, "inativo" end
	if L.estado == "Caido" or L.estado == "Levantando" or L.estado == "Finalizando" then return false, "caido/levantando" end
	local agora = os.clock()
	local piv = L.modelo:GetPivot(); local pos = piv.Position
	local fr = Vector3.new(piv.LookVector.X, 0, piv.LookVector.Z).Unit
	local function reagir(motivo)
		logc("ESQUIVA", L, string.format("%s: deslocamento bloqueado (%s) -> reacao no lugar", tipo, motivo))
		EVENTO:FireAllClients("Esquiva", L.modelo, pos, pos, 0, motivo)
		return false, motivo
	end
	if L.dashAte and agora < L.dashAte then return reagir("deslocamento recente") end
	if L.estado ~= "Livre" then return reagir("em habilidade " .. tostring(L.estado)) end
	local ref = (typeof(origem) == "Instance" and origem.Parent and centro(origem)) or (pos - fr * 5)
	local linha = Vector3.new(pos.X - ref.X, 0, pos.Z - ref.Z); if linha.Magnitude < 0.1 then linha = -fr end; linha = linha.Unit
	local lados = {Vector3.new(-linha.Z, 0, linha.X), Vector3.new(linha.Z, 0, -linha.X)}
	if typeof(origem) == "Instance" and origem.Parent then
		local lk = origem:GetPivot().LookVector
		if lados[1]:Dot(lk) > lados[2]:Dot(lk) then lados[1], lados[2] = lados[2], lados[1] end
	end
	local y0 = chaoY(L, pos); local off = y0 and (pos.Y - y0) or 0
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.RespectCanCollide = true
	local ign = {L.modelo}; for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(ign, pl.Character) end end
	rp.FilterDescendantsInstances = ign
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude; op.FilterDescendantsInstances = {L.modelo}
	-- 19/11: candidatos em ordem: laterais (preferido, oposto), diagonais AFASTANDO do atacante e laterais curtas.
	-- Em arena aberta quase sempre ha saida; parede/borda/corpo/zona/territorio continuam recusando cada candidato.
	local cands = {}
	for _, d in ipairs(lados) do table.insert(cands, {d = d, dist = EV.dist, nome = "lateral"}) end
	for _, d in ipairs(lados) do table.insert(cands, {d = (d + linha * EV.diagonal).Unit, dist = EV.dist, nome = "diagonal"}) end
	for _, d in ipairs(lados) do table.insert(cands, {d = d, dist = EV.distCurta, nome = "lateral curta"}) end
	local motivos = {}
	for i, cnd in ipairs(cands) do
		local d = cnd.d
		local dest = pos + d * cnd.dist
		local por = nil
		for _, f in ipairs({0.5, 2.2, 5.0}) do                                    -- traseira, meio e frente do corpo
			for _, h in ipairs({1.2, 3.5}) do
				local hit = workspace:Raycast(pos + fr * f + Vector3.new(0, h, 0), d * (cnd.dist + EV.largura / 2), rp)
				if hit and not por then por = "parede " .. hit.Instance.Name end
			end
		end
		local yT, yF = chaoY(L, dest + fr * 0.5), chaoY(L, dest + fr * 5.3)
		if not por and (not yT or not yF) then por = "sem chao (borda)" end
		if not por and y0 and (math.abs(yT - y0) > EV.desnivel or math.abs(yF - y0) > EV.desnivel) then por = string.format("desnivel %.1f", math.max(math.abs(yT - y0), math.abs(yF - y0))) end
		if not por then
			local cx = dest + fr * 2.2 + Vector3.new(0, 3, 0)
			for _, pt in ipairs(workspace:GetPartBoundsInBox(CFrame.lookAt(cx, cx + fr), Vector3.new(EV.largura, 4, EV.comprimento), op)) do
				local mm = modeloAlvo(pt)
				if mm and mm ~= L.modelo then por = "corpo de " .. mm.Name; break end
			end
		end
		if not por and emZonaSegura(dest) then por = "zona segura" end
		if not por and L.ia and L.ia.posto then
			local g = CFG.IA_Guardiao
			if Vector3.new(dest.X - L.ia.posto.X, 0, dest.Z - L.ia.posto.Z).Magnitude > g.coleira + g.raioAmeaca then por = "fora do territorio" end
		end
		if not por then
			L.dashAte = agora + EV.intervalo; L.dashando = true
			local yd = (yT or y0 or pos.Y) + off
			local para = CFrame.lookAt(Vector3.new(dest.X, yd, dest.Z), Vector3.new(dest.X, yd, dest.Z) + fr)
			EVENTO:FireAllClients("Esquiva", L.modelo, pos, para.Position, EV.dur, nil)
			logc("ESQUIVA", L, string.format("%s: deslocou %.1f (%s %s) em %.2f s%s", tipo, cnd.dist, cnd.nome, (i % 2 == 1) and "preferido" or "oposto",
				EV.dur, #motivos > 0 and (" (recusados antes: " .. table.concat(motivos, " / ") .. ")") or ""))
			K.ultimaEsquiva = {tipo = tipo, de = pos, para = para.Position, lado = i, t = agora}
			tarefa(L, function()
				local t0 = os.clock(); local de = L.modelo:GetPivot()
				while vivo(L) do
					local u = math.clamp((os.clock() - t0) / EV.dur, 0, 1); local s = 1 - (1 - u) ^ 3   -- quase instantaneo
					L.modelo:PivotTo(de:Lerp(para, s))
					if u >= 1 then break end
					RS.Heartbeat:Wait()
				end
				L.dashando = false
			end)
			return true
		end
		table.insert(motivos, por)
	end
	return reagir(table.concat(motivos, " / "))
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
	gastar(L, "Investida", IV); L.estado = "Investida"; anunciar(L, "Investida")
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
				local alvo = hit and modeloAlvo(hit.Instance)                   -- r8
				-- 20/11: criaturas/personagens saem do blockcast (a caixa da malha parava a investida de longe); o acerto e
				-- pela BOCA no corpo real; corpo encostado (peito) ou alvo protegido param sem dano
				local bc = boca(L)
				for _, a in ipairs(candidatos(L, 16)) do
					if not acertou[a] and alvoValido(a) then
						local dcB = contato(a, {bc})
						if not protegido(L, a) and dcB <= HB.contatoMordida then
							acertou[a] = true; causarDano(L, a, CFG.Basico.Mordida.dano * IV.multDano, "Investida")
							parado = true; fimTipo, fimPos = "alvo", bc; logc("HITBOX", L, string.format("investida mordeu %s (contato %.2f)", a.Name, dcB))
							EVENTO:FireAllClients("InvestidaFim", L.modelo, "alvo", bc); break
						elseif dcB <= HB.contatoMordida or contato(a, {pos + Vector3.new(0, 4.5, 0) + dir * 2}) <= HB.corpoInvestida then
							parado = true; fimTipo, fimPos = "corpo", bc; logc("HABILIDADE", L, "investida parou encostada em " .. a.Name .. (protegido(L, a) and " (protegido, sem dano)" or " (sem mordida)"))
							EVENTO:FireAllClients("InvestidaFim", L.modelo, "obstaculo", bc); break
						end
					end
				end
				if parado then
				elseif hit and alvo then                                        -- criatura: tratada acima, nao e parede
				elseif hit and hit.Distance < passo.Magnitude + 6.0 then   -- focinho fica ~6 studs a frente do pivo
					parado = true; fimTipo, fimPos = "obstaculo", hit.Position; logc("HABILIDADE", L, "investida parou em obstaculo: " .. hit.Instance.Name)
					EVENTO:FireAllClients("InvestidaFim", L.modelo, "obstaculo", hit.Position)
				end
				if not parado then L.modelo:PivotTo(CFrame.lookAt(pos + passo, pos + passo + dir)) end
			end
			RS.Heartbeat:Wait()
		end
		encerrar(L, "Investida"); if vivo(L) then L.estado = "Livre" end
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
			if vivo(L) and L.ia and not L.ia.v2 then          -- 19/11: lobos com a IA estrategica (LoboIA) ficam com ela
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
		if vivo(L) and L.estado == "Livre" and L.dono and L.dono.Character and L.dono.Character.PrimaryPart and not L.parado and not L.virando and not L.dashando then
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

-- ------------------------------------------------------------------ IA ESTRATEGICA (modulo LoboIA, 19/11) [PROPOSTA]
-- Percepcao/plano/locomocao no modulo; EXECUCAO pelas mesmas ACOES do jogador (acaoIA): validacoes iguais.
local function filtroMov(L, extra)
	local p = RaycastParams.new(); p.FilterType = Enum.RaycastFilterType.Exclude; p.RespectCanCollide = true
	local lista = {}
	for _, x in pairs(K.lobos) do table.insert(lista, x.modelo) end
	for _, pl in ipairs(Players:GetPlayers()) do if pl.Character then table.insert(lista, pl.Character) end end
	for _, x in ipairs(extra or {}) do table.insert(lista, x) end
	p.FilterDescendantsInstances = lista; return p
end
local IA2 = nil
do
	local mod = script:FindFirstChild("LoboIA")
	if mod then
		local ok, r = pcall(require, mod)
		if ok then
			IA2 = r.iniciar({CFG = CFG, lobos = K.lobos, logc = logc, vivo = vivo, alvoValido = alvoValido, alvoPermitido = alvoPermitido,
				protegido = protegido, pontoProximo = pontoProximo, centro = centro, linhaDeVisao = linhaDeVisao,
				visao = function(L, a) return visaoInstinto(L, a, partesVegetacao()) end, velAlvo = velAlvo, chaoY = chaoY,
				filtroMov = filtroMov, misturarCurva = misturarCurva, pararCurvas = pararCurvas, virarNoLugar = virarNoLugar,
				esquivaDesloc = function(L, origem, tipo) return K.esquivaDesloc(L, origem, tipo) end,
				classePorte = function(m) return K.classePorte(m) end, finalizar = function(L, alvo, motivo, enc) return K.finalizar(L, alvo, motivo, enc) end,
				distTronco = function(alvo, p) return K.distTronco(alvo, p) end, troncoAlvo = function(alvo) return K.troncoAlvo(alvo) end,
				boca = function(L) return K.boca(L) end, contato = function(alvo, pts) return K.contato(alvo, pts) end, patas = function(L) return K.patas(L) end,
				acao = function(L, n, d, motivo) return acaoIA(L, n, d, motivo) end})
			K.IA2 = IA2; log("LoboIA (IA estrategica) carregada")
		else log("LoboIA falhou: " .. tostring(r)) end
	end
end

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
		elseif cmd == "clonarIA2" then                                                      -- 19/11: lobo sem dono com a IA ESTRATEGICA
			if not IA2 then return nil end
			local L0 = umLobo(); local m2 = L0.modelo:Clone(); m2.Name = b or "Lobo_IA"; m2.Parent = AREA; m2:PivotTo(a)
			for _, k in ipairs({"EmAtaque", "PlanoIA", "UltimoCombate", "Caido", "CaidoAte", "LentidaoControle", "LentidaoAte", "Mancando",
				"RetiradaDeCombate", "Incapacitado", "Estado", "FinalizacaoDe", "PorteOmbro", "Idade", "Forca", "DecisaoQueda", "Estrangulado", "MordidoPor"}) do m2:SetAttribute(k, nil) end
			local L2 = registrar(m2, nil); IA2.ligar(L2, a.Position); return m2
		elseif cmd == "esquiva" then local L = umLobo(a); return K.esquivaDesloc(L, b, c or "teste")       -- 19/11: dispara a esquiva visivel (teste)
		elseif cmd == "vel" then local e = K.velAlvos[a]; return e and e.v or "sem registro"
		elseif cmd == "iaInfo" then local L = umLobo(a); return (L and IA2) and IA2.info(L) or {}
		elseif cmd == "setVida" then local L = umLobo(b); L.vida = a; L.modelo:SetAttribute("Vida", a); return true
		elseif cmd == "setEnergia" then local L = umLobo(b); L.energia = a; return true
		-- 19/11 controle por porte / queda / finalizacao (testes)
		elseif cmd == "porte" then local r = K.classePorte(a); return r
		elseif cmd == "forcarControle" then K.forcarControle = a; return true                 -- "queda"/"manca"/"lento"/nil
		elseif cmd == "simControle" then                                                       -- frequencia por porte sem aplicar (N sorteios)
			local L = umLobo(c); local n = {queda = 0, manca = 0, lento = 0, nenhum = 0}; local R
			for _ = 1, (b and b.n or 1000) do R = K.rolarControle(L, a, b and b.tipo or "Mordida", 1, true); n[R.efeito] = (n[R.efeito] or 0) + 1 end
			return {n = n, dur = R and R.dur, porteA = R and R.porteA and R.porteA.nome, porteB = R and R.porteB and R.porteB.nome, rel = R and R.rel, motivo = R and R.motivo}
		elseif cmd == "derrubar" then local L = umLobo(c); K.ultimoStun[a] = nil; K.aplicarEstado(L, a, b or "queda", K.rolarControle(L, a, "Investida", 1, true, b or "queda").dur); return true
		elseif cmd == "finalizar" then local L = umLobo(b); return K.finalizar(L, a, c or "teste")
		elseif cmd == "ultimaMordidaFlanco" then return K.ultimaMordidaFlanco
		elseif cmd == "ultimaFinalizacao" then return K.ultimaFinalizacao
		elseif cmd == "hitbox" then local L = umLobo(b); local pt = patas(L)
			return {boca = K.contato(a, {boca(L)}), patas = K.contato(a, pt), pivoSuperficie = select(2, pontoProximo(a, L.modelo:GetPivot().Position))}
		elseif cmd == "ultimoControle" then local R = K.ultimoControle; return R and {efeito = R.efeito, dur = R.dur, rel = R.rel, motivo = R.motivo} or nil
		elseif cmd == "estadoLobo" then local L = umLobo(a); return L and {estado = L.estado, vida = L.vida, vel = L.velMult, caido = L.modelo:GetAttribute("Caido"), lent = L.modelo:GetAttribute("LentidaoControle")} or nil
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
