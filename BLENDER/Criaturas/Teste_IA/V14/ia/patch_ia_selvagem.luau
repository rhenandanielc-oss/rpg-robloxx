-- patch_ia_selvagem.luau (rodar no Studio, modo Edit; servido em http://127.0.0.1:8766/patch_ia_selvagem.luau)
-- IA selvagem do Dragao das Montanhas — etapa "inteligencia e integracao ao mundo" (30/10). Audita e completa o que ja
-- existia (IA_Dragao: Cerebro/Locomotor/Territorio; Combate_Dragao) SEM reescrever: trocas pontuais, tudo-ou-nada
-- (todas as trocas sao conferidas antes de gravar), originais em ServerStorage.Backup_Scripts_IA_Selvagem (1a versao).
--   Cerebro : Investigar (ultima posicao), espaco pessoal fora do ninho (alerta -> defesa propria), LOD por distancia
--             (decisao 2,5 s e so rotinas paradas sem jogador a 1500 studs; eventos do ninho acordam na hora),
--             convivencia (destinos/poleiros livres entre dragoes), zonas seguras, ataque a distancia com linha de
--             visao, espera o golpe terminar antes de reposicionar, encarar sem "girar a toa", limpeza de conexoes.
--   Locomotor: velocidades do proprio rig (RitmoAndarBase / VelCorrer) e teste de parede com a largura do corpo.
--   Combate : escolha tatica (distancia, altura, visao, espaco, grupo, trajeto livre, variacao) com IA_Habilidade /
--             IA_Bloqueio; sopro continuo da IA (segura e acompanha o alvo, solta ao perder alcance/visao/cone);
--             guardiao reage a habilidades usadas perto dele (GuardiaoAtacado — sem dano: regra de vida pendente).
--   Nucleo  : sopro encerra se o dragao sumir ou for incapacitado.
--   IA_Servidor: depuracao visual so para autorizados (Workspace.IA_DebugVisual = true) + limpeza do registro.
--   Sons    : vozes contextuais dos clipes novos (ameaca, alerta, reagir, combate, comer) com intervalo minimo.
--   Apelidos: Ninho_Inspecionar -> Observar_Farejar (clipe novo).
local SSS, RS, SS = game:GetService("ServerScriptService"), game:GetService("ReplicatedStorage"), game:GetService("ServerStorage")
local SPS = game:GetService("StarterPlayer").StarterPlayerScripts
local alvos = {
	Cerebro = SSS.IA_Dragao.Cerebro, Config = SSS.IA_Dragao.Config, Locomotor = SSS.IA_Dragao.Locomotor,
	IAServ = SSS.IA_Dragao_Servidor, CombServ = SSS.Combate_Dragao_Servidor, Nucleo = SSS.Combate_Dragao.Nucleo,
	Sons = SPS.SonsDragao_Cliente, Apelidos = RS.Animacoes_Silverwing.Apelidos,
}
if alvos.Cerebro.Source:find("PATCH_IA_SELVAGEM", 1, true) then return "ja aplicado" end
local novo = {}
for k, s in pairs(alvos) do novo[k] = s.Source end
local function troca(k, a, b)
	local i, j = string.find(novo[k], a, 1, true)
	assert(i, k .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[k], a, j + 1, true), k .. ": trecho repetido: " .. a:sub(1, 70))
	novo[k] = novo[k]:sub(1, i - 1) .. b .. novo[k]:sub(j + 1)
end

-- ============================================================== Config
troca("Config", [=[tickCalmo = 1.0, tickAtivo = 0.25, distJogadorAtivo = 600,]=], [=[tickCalmo = 1.0, tickAtivo = 0.25, distJogadorAtivo = 600,
	-- LOD comportamental: sem jogador a menos de distJogadorLonge, decide a cada tickDormente e so rotinas paradas
	-- (eventos do ninho/ataque acordam a IA na hora: 'urgente')
	tickDormente = 2.5, distJogadorLonge = 1500,
	-- espaco pessoal (vale fora do ninho): perto e visivel -> alerta; muito perto por toleranciaProximo s -> defesa propria
	espacoPessoal = 75, espacoCritico = 34, toleranciaProximo = 4,
	-- investigacao da ultima posicao de uma presenca que sumiu (janela para comecar, tempo farejando/olhando)
	investigarJanela = 40, investigarTempo = 7,
	-- a IA pede ataque ate distAtaqueMax (alem de distAtaque exige linha de visao); o Combate escolhe golpe/habilidade
	distAtaqueMax = 150,
	-- convivencia: distancia minima entre destinos/posicoes de dragoes diferentes (patrulha, poleiros)
	distEntreDragoes = 90,]=])

-- ============================================================== Cerebro
troca("Cerebro", [=[local EstadosDragao = require(game:GetService("ReplicatedStorage").Comportamento_Dragoes.EstadosDragao)]=],
[=[local EstadosDragao = require(game:GetService("ReplicatedStorage").Comportamento_Dragoes.EstadosDragao)
-- PATCH_IA_SELVAGEM (30/10): investigar, espaco pessoal, LOD, convivencia entre dragoes, zonas seguras, ataque a distancia
local okN, Nucleo = pcall(function() return require(game:GetService("ServerScriptService"):WaitForChild("Combate_Dragao", 5):WaitForChild("Nucleo", 5)) end)
local function zonaSegura(pos) return okN and type(Nucleo) == "table" and Nucleo.emZonaSegura and Nucleo.emZonaSegura(pos) or false end]=])
troca("Cerebro", [=[self.T.Alerta.Event:Connect(function(alvo, motivo) self:ameaca(alvo, 2, motivo) end)]=],
	[=[self.proximoDesde = {}
	self.cxAlerta = self.T.Alerta.Event:Connect(function(alvo, motivo) self:ameaca(alvo, 2, motivo); self.urgente = true end)]=])
troca("Cerebro", [=[Territorio.Eventos.GuardiaoAtacado.Event:Connect(function(guardiao, atacante)]=],
	[=[self.cxAtacado = Territorio.Eventos.GuardiaoAtacado.Event:Connect(function(guardiao, atacante)]=])
troca("Cerebro", [=[if guardiao == modelo and atacante then self:ameaca(atacante, 2, "ataque") end]=],
	[=[if guardiao == modelo and atacante then self:ameaca(atacante, 2, "ataque"); self.urgente = true end]=])
troca("Cerebro", [=[if motivo == "coletou" or motivo == "ataque" then a.persegue = true end]=],
	[=[if motivo == "coletou" or motivo == "ataque" or motivo == "invasao" then a.persegue = true end
	-- ameaca PESSOAL (ao dragao, nao ao ninho): o limite da perseguicao passa a ser o territorio inteiro
	if motivo == "ataque" or motivo == "invasao" or motivo == "proximo" then a.pessoal = true end]=])
troca("Cerebro", [=[local perto = false]=], [=[local perto = false; local minDist = math.huge]=])
troca("Cerebro", [=[local dD = plano(r.Position - self.L:pos()).Magnitude]=],
	[=[local dD = plano(r.Position - self.L:pos()).Magnitude; minDist = math.min(minDist, dD, dN)]=])
troca("Cerebro", [=[if a and (dN <= raioV or (a.persegue and dN <= cfg.perseguicaoMax)) then a.t = agora; a.ultimaPos = r.Position end]=],
[=[-- ESPACO PESSOAL (tambem longe do ninho): perto do dragao e visivel -> alerta (encara, asas meio abertas);
		-- muito perto por toleranciaProximo s -> defesa propria. Dentro de zona segura: so observa.
		if dD <= cfg.espacoPessoal and not zonaSegura(r.Position) then
			local vis = dD < cfg.espacoCritico or not workspace:Raycast(cab, r.Position - cab, self.L.params)
			if vis then
				if dD <= cfg.espacoCritico then
					self.proximoDesde[alvo] = self.proximoDesde[alvo] or agora
					if agora - self.proximoDesde[alvo] >= cfg.toleranciaProximo then self:ameaca(alvo, 2, "invasao")
					else self:ameaca(alvo, 1, (self.ameacas[alvo] and self.ameacas[alvo].motivo) or "proximo") end
				else
					self.proximoDesde[alvo] = nil
					self:ameaca(alvo, 1, (self.ameacas[alvo] and self.ameacas[alvo].motivo) or "proximo")
				end
			end
		else
			self.proximoDesde[alvo] = nil
		end
		a = self.ameacas[alvo]
		local lim = a and a.pessoal and cfg.territorio or cfg.perseguicaoMax
		if a and (dN <= raioV or (a.persegue and dN <= lim) or (a.pessoal and dD <= cfg.espacoPessoal * 1.3)) then a.t = agora; a.ultimaPos = r.Position end]=])
troca("Cerebro", [=[local longe = r and plano(r.Position - self.casa).Magnitude > cfg.perseguicaoMax]=],
	[=[local longe = r and plano(r.Position - self.casa).Magnitude > (a.pessoal and cfg.territorio or cfg.perseguicaoMax)]=])
troca("Cerebro", [=[if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) then]=],
	[=[if not r or not alvo.Parent or agora - a.t > cfg.lembrarAmeaca or (longe and agora - a.t > 1) or (r and zonaSegura(r.Position)) then]=])
troca("Cerebro", [=[self.ameacas[alvo] = nil; self:registrar("ameaca encerrada: " .. alvo.Name)]=],
	[=[self.ameacas[alvo] = nil; self:registrar("ameaca encerrada: " .. alvo.Name); self.proximoDesde[alvo] = nil
			-- presenca que sumiu sem confronto: vai conferir a ultima posicao conhecida (por tempo limitado)
			if a.nivel < 2 and a.ultimaPos and r and alvo.Parent then self.investigar = {pos = a.ultimaPos, t = agora} end]=])
troca("Cerebro", [=[return perto]=], [=[self.longe = minDist > cfg.distJogadorLonge; self.dormente = self.longe
	return perto]=])
troca("Cerebro", [=[if alvo and a.nivel == 1 then return "Alert" end]=], [=[if alvo and a.nivel == 1 then return "Alert" end
	if self.investigar and os.clock() - self.investigar.t < self.cfg.investigarJanela then return "Investigate" end]=])
troca("Cerebro", [=[local opcoes = {{"Wander", 4}, {"Patrol", 3}, {"Rest", 2}, {"Idle", 1}}]=],
	[=[-- LOD: longe de todos os jogadores so rotinas paradas (sem locomocao por quadro); perto, rotina completa
	local opcoes = self.dormente and {{"Rest", 2}, {"Idle", 1}} or {{"Wander", 4}, {"Patrol", 3}, {"Rest", 2}, {"Idle", 1}}]=])
troca("Cerebro", [=[local perto = self:perceber()]=], [=[if self.m:GetAttribute("Controlador") then self.L:soltar(); task.wait(0.5); continue end   -- montado: nunca disputa o controle
		local perto = self:perceber()]=])
troca("Cerebro", [=[task.wait(perto and self.cfg.tickAtivo or self.cfg.tickCalmo)]=],
	[=[-- LOD comportamental + reacao imediata a eventos (Alerta do ninho / ataque marcam 'urgente')
		local espera = perto and self.cfg.tickAtivo or (self.longe and self.cfg.tickDormente or self.cfg.tickCalmo)
		local fimE = os.clock() + espera
		while os.clock() < fimE and not self.urgente and self.m.Parent do task.wait(0.1) end
		self.urgente = false]=])
troca("Cerebro", [=[self.T:liberar(self.id)]=], [=[self.T:liberar(self.id)
	if self.cxAlerta then self.cxAlerta:Disconnect() end; if self.cxAtacado then self.cxAtacado:Disconnect() end
	self.ameacas, self.proximoDesde = {}, {}]=])
troca("Cerebro", [=[local function aleatorioNoTerritorio(self)]=], [=[local function _pontoSorteado(self)]=])
troca("Cerebro", [=[-- ===== tarefas]=], [=[-- convivencia entre dragoes: ponto livre = longe da posicao e do destino atual dos outros guardioes
function C:pontoLivre(p)
	for m, outro in pairs(_G.IA_DRAGOES or {}) do
		if outro ~= self and m.Parent and outro.L then
			if plano(outro.L:pos() - p).Magnitude < self.cfg.distEntreDragoes then return false end
			if outro.destino and plano(outro.destino - p).Magnitude < self.cfg.distEntreDragoes then return false end
		end
	end
	return true
end
function C:poleiroLivre()
	local _, ps = self:poi("Poleiro"); if not ps then return nil end
	local livres = {}
	for _, p in ipairs(ps) do if self:pontoLivre(p.Position) then table.insert(livres, p.Position) end end
	return #livres > 0 and livres[math.random(#livres)] or nil
end
local function aleatorioNoTerritorio(self)
	local p
	for _ = 1, 6 do p = _pontoSorteado(self); if self:pontoLivre(p) then return p end end
	return p
end
-- ataque: perto sempre; a distancia (sopro/arremetida) so com linha de visao; nunca em zona segura
function C:podeAtacar(alvo)
	local r = raizDe(alvo); if not r or zonaSegura(r.Position) then return false end
	local d = plano(self.L:pos() - r.Position).Magnitude
	if d <= self.cfg.distAtaque then return true end
	if d > self.cfg.distAtaqueMax then return false end
	local cab = self.m.PrimaryPart:FindFirstChild("Cabeca", true).WorldPosition
	return workspace:Raycast(cab, r.Position - cab, self.L.params) == nil
end
-- encara so se estiver bem fora (evita girar no lugar a toa e reiniciar o clipe de alerta)
function C:encarar(pos, vivo)
	local d = plano(pos - self.L:pos())
	if d.Magnitude > 1 and self.L:frente():Dot(d.Unit) < 0.9 and not self.L.noAr then self.L:virarPara(pos, vivo) end
end
function C:_Investigate(vivo)
	local inv = self.investigar; self.investigar = nil
	if not inv or not self:emPe(vivo) then return end
	local d = plano(inv.pos - self.L:pos())
	if d.Magnitude > 30 and plano(inv.pos - self.casa).Magnitude <= self.cfg.territorio then
		self.destino = inv.pos
		local ok = self:ir(inv.pos - d.Unit * 28, false, vivo, 14)
		if not ok or not vivo() then return end
	end
	self:encarar(inv.pos, vivo)
	self:definir("Investigate"); self:comportamento("Observacao", self.cfg.investigarTempo, vivo)   -- fareja e olha em volta
end

-- ===== tarefas]=])
troca("Cerebro", [=[local poi = self:poi("Observacao"); local alvo = poi and poi.Position or aleatorioNoTerritorio(self)]=],
	[=[local poi = self:poi("Observacao"); local alvo = (poi and self:pontoLivre(poi.Position)) and poi.Position or aleatorioNoTerritorio(self)
	self.destino = alvo]=])
troca("Cerebro", [=[for i = 1, 3 do local _, ps = self:poi("Poleiro"); table.insert(rota, (ps and math.random() < 0.4) and ps[math.random(#ps)].Position or aleatorioNoTerritorio(self)) end]=],
	[=[for i = 1, 3 do local pl = math.random() < 0.4 and self:poleiroLivre(); table.insert(rota, pl or aleatorioNoTerritorio(self)) end]=])
troca("Cerebro", [=[self:definir(i == 2 and "Glide" or "Fly"); self.L.planar = (i == 2)]=],
	[=[self:definir(i == 2 and "Glide" or "Fly"); self.L.planar = (i == 2); self.destino = ponto]=])
troca("Cerebro", [=[local pouso = (ps and math.random() < 0.5) and ps[math.random(#ps)].Position or (self.T:ovoPresente() and self.casa or aleatorioNoTerritorio(self))]=],
	[=[local pl = math.random() < 0.5 and self:poleiroLivre()
	local pouso = pl or (self.T:ovoPresente() and self.casa or aleatorioNoTerritorio(self)); self.destino = pouso]=])
troca("Cerebro", [=[if plano(self.L:pos() - self.casa).Magnitude > self.cfg.vigilancia then]=],
	[=[-- alerta PESSOAL (alguem perto do dragao, fora do ninho): fica onde esta, encarando
	if not a.pessoal and plano(self.L:pos() - self.casa).Magnitude > self.cfg.vigilancia then]=])
troca("Cerebro", [=[while vivo() and self:maiorAmeaca() do self:comportamento("Alerta", 2, vivo) end]=],
	[=[while vivo() and self:maiorAmeaca() do
		local _, a2 = self:maiorAmeaca(); if a2 and a2.ultimaPos then self:encarar(a2.ultimaPos, vivo) end
		self:comportamento("Alerta", 2, vivo)
	end]=])
troca("Cerebro", [=[if not alvo or a.nivel < 2 then break end]=], [=[if not alvo or a.nivel < 2 then break end
		if self.m:GetAttribute("EmAtaque") then task.wait(0.1); continue end      -- golpe em curso: nao interrompe nem desliza]=])
troca("Cerebro", [=[if dIN > self.cfg.perseguicaoMax then]=], [=[if dIN > (a.pessoal and self.cfg.territorio or self.cfg.perseguicaoMax) or zonaSegura(pI) then]=])
troca("Cerebro", [=[if plano(self.L:pos() - raizDe(alvo).Position).Magnitude <= self.cfg.distAtaque and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then]=],
	[=[if self:podeAtacar(alvo) and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then]=])
troca("Cerebro", [=[if plano(self.L:pos() - pI).Magnitude <= self.cfg.distAtaque and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then]=],
	[=[if self:podeAtacar(alvo) and os.clock() - ultimoAtaque > self.cfg.intervaloAtaque then]=])

-- ============================================================== Locomotor
troca("Locomotor", [=[local vel = correr and cfg.correrVel * cfg.correrRitmo or cfg.andarVel * cfg.andarRitmo]=],
	[=[-- outro rig informa as proprias velocidades: anda no ritmo natural do clipe (RitmoAndarBase), corre em VelCorrer
	local vel = correr and (self.m:GetAttribute("VelCorrer") or cfg.correrVel * cfg.correrRitmo)
		or (self.m:GetAttribute("RitmoAndarBase") or cfg.andarVel * cfg.andarRitmo)]=])
troca("Locomotor", [=[local base = Vector3.new(p.X, g0 + 22, p.Z)
	local r = workspace:Raycast(base, dir * 40, self.params)
	if r and r.Normal.Y < 0.5 then return false, "parede" end]=],
	[=[-- corpo largo: raio central + dois nas laterais (largura do corpo com asas recolhidas) + um baixo (rochas no peito)
	local lado = dir:Cross(Vector3.yAxis).Unit * ((self.m:GetAttribute("CorpoRaio") or 8) + 4)
	for _, o in ipairs({Vector3.zero, lado, -lado, Vector3.new(0, -12, 0)}) do
		local r = workspace:Raycast(Vector3.new(p.X, g0 + 22, p.Z) + o, dir * 40, self.params)
		if r and r.Normal.Y < 0.5 then return false, "parede" end
	end]=])

-- ============================================================== Nucleo
troca("Nucleo", [=[if agora >= fim and not segue then break end]=], [=[if not self.m.Parent or self.m:GetAttribute("Incapacitado") then break end   -- removido/incapacitado: encerra ja
			if agora >= fim and not segue then break end]=])

-- ============================================================== Combate (servidor)
troca("CombServ", [=[local function escolher(c, alvo)]=], [=[local function escolher_antigo(c, alvo)          -- substituida pela escolha tatica abaixo]=])
troca("CombServ", [=[-- IA_Eventos: o mesmo par de pastas/eventos que o Territorio cria (busca ou cria; sem esperar)]=],
[=[-- PATCH_IA_SELVAGEM: escolha TATICA (distancia, altura, linha de visao, espaco acima, grupo de verdade, trajeto livre,
-- recarga/energia) com pequena variacao; grava IA_Habilidade (escolha) e IA_Bloqueio (por que as outras nao) no modelo.
local gpMundo = RaycastParams.new(); gpMundo.FilterType = Enum.RaycastFilterType.Exclude
local function mundo(c)
	local ex = {c.m}; for _, p in ipairs(Players:GetPlayers()) do if p.Character then table.insert(ex, p.Character) end end
	gpMundo.FilterDescendantsInstances = ex; return gpMundo
end
local function alcSopro(c)
	local e = Cfg.habilidades.Sopro.porElemento[c.m:GetAttribute("ElementoAtivo") or ""]; return e and e.alcance or 100
end
local function escolher(c, alvo)
	local r = raiz(alvo); if not r then return nil end
	if N.emZonaSegura(r.Position) then c.m:SetAttribute("IA_Bloqueio", "alvo em zona segura"); return nil end
	local p = c.m:GetPivot().Position; local v = Vector3.new(r.Position.X - p.X, 0, r.Position.Z - p.Z); local d = v.Magnitude
	local f = c:frente(); local atras = d > 1 and f:Dot(v.Unit) < -0.2; local frente = d < 1 or f:Dot(v.Unit) > 0.5
	local b = c:boca(); local dBoca = (b - r.Position).Magnitude
	local acima = r.Position.Y - p.Y
	local noAr = c.m:GetAttribute("NoAr") == true
	local perto, atrasN = 0, 0
	for _, a in ipairs(c:alvosValidos()) do
		local ra = raiz(a).Position
		if (ra - p).Magnitude < Cfg.habilidades.Tempestade.raio * 0.85 then
			perto += 1
			local va = Vector3.new(ra.X - p.X, 0, ra.Z - p.Z); if va.Magnitude > 1 and f:Dot(va.Unit) < -0.2 then atrasN += 1 end
		end
	end
	local bloqueio, ordem = {}, {}
	local function add(h, peso) table.insert(ordem, {h, peso + math.random() * 0.25}) end
	-- colado: mordida/garras (nunca sopro); atras: cauda
	if dBoca < 26 then add("Mordida", 1.0); add("Garra", 0.9)
	elseif d < 45 and not noAr then add(atras and "Cauda" or "Garra", 0.95) end
	if atras and d < 62 then add("Cauda", 1.0) end
	-- Ruptura: so no solo (o Nucleo confirma), alvo no leque a frente, intervalo extra entre usos
	local R = Cfg.habilidades.Ruptura
	if not noAr and d > 10 and d < R.aneis[#R.aneis] + 4 and not atras and os.clock() - (ultimaRuptura[c.m] or -99) > R.recarga * 1.6 then
		add("Ruptura", perto >= 2 and 1.05 or 0.85)
	end
	-- Tempestade: grupo de verdade (3+, ou 2 cercando/aleatorio), espaco livre acima para o impulso
	if perto >= 3 or (perto >= 2 and (atrasN >= 1 or math.random() < 0.35)) then
		if not noAr and workspace:Raycast(p + Vector3.new(0, 10, 0), Vector3.new(0, 45, 0), mundo(c)) then table.insert(bloqueio, "Tempestade: teto baixo")
		else add("Tempestade", 1.1) end
	end
	-- Sopro: media distancia, alvo a frente e visivel
	if d >= 30 and d < alcSopro(c) then
		if not c:visivel(b, alvo) then table.insert(bloqueio, "Sopro: sem linha de visao")
		elseif not frente then table.insert(bloqueio, "Sopro: fora do cone")
		else add("Sopro", 0.9) end
	end
	-- Arremetida: trajeto livre ate o alvo e sem desnivel grande (no solo)
	local Ar = Cfg.habilidades.Arremetida
	if d >= 50 and d < 170 then
		if workspace:Spherecast(p + Vector3.new(0, 20, 0), 14, v.Unit * math.min(d, Ar.distancia), mundo(c)) then table.insert(bloqueio, "Arremetida: obstaculo")
		elseif math.abs(acima) > 30 and not noAr then table.insert(bloqueio, "Arremetida: desnivel")
		else add("Arremetida", d > alcSopro(c) and 1.0 or 0.75) end
	end
	table.sort(ordem, function(x, y) return x[2] > y[2] end)
	for _, o in ipairs(ordem) do
		local h = o[1]
		if c:temHabilidade(h) then
			local ok, motivo = c:podeUsar(h)
			if ok then
				if h == "Ruptura" then ultimaRuptura[c.m] = os.clock() end
				c.m:SetAttribute("IA_Habilidade", h); c.m:SetAttribute("IA_Bloqueio", #bloqueio > 0 and table.concat(bloqueio, "; ") or nil)
				return h
			end
			table.insert(bloqueio, h .. ": " .. tostring(motivo))
		end
	end
	c.m:SetAttribute("IA_Bloqueio", #bloqueio > 0 and table.concat(bloqueio, "; ") or "nada ao alcance")
	return nil
end

-- IA_Eventos: o mesmo par de pastas/eventos que o Territorio cria (busca ou cria; sem esperar)]=])
troca("CombServ", [=[local h = escolher(c, alvo); if h then c:usar(h, {alvo = alvo}) end]=],
[=[local h = escolher(c, alvo); if not h then return end
		if h ~= "Sopro" then c:usar(h, {alvo = alvo}); return end
		-- SOPRO CONTINUO DA IA: segura enquanto o alvo estiver vivo, ao alcance, visivel e no cone do pescoco (o Nucleo
		-- valida o cone, consome energia e limita em emissaoMax); solta num tempo variado (nao mecanico)
		c.segurando = true; c.miraDir = (raiz(alvo).Position - c:boca()).Unit
		if not c:usar("Sopro", {alvo = alvo, segurar = true}) then c.segurando = nil; c.miraDir = nil; return end
		local limite = os.clock() + 2.2 + math.random() * 2.3
		task.spawn(function()
			task.wait(0.05)
			while m.Parent and m:GetAttribute("EmAtaque") == "Sopro" do
				local r = raiz(alvo); local hum = alvo and alvo:FindFirstChildOfClass("Humanoid"); local b = c:boca()
				if not (r and alvo.Parent and hum and hum.Health > 0) or os.clock() > limite or m:GetAttribute("Incapacitado")
					or (r.Position - b).Magnitude > alcSopro(c) or not c:visivel(b, alvo) or N.emZonaSegura(r.Position) then
					c.segurando = false; break
				end
				c.miraDir = (r.Position - b).Unit
				task.wait(0.1)
			end
		end)]=])
troca("CombServ", [=[c:usar(arg, {direcao = typeof(dir) == "Vector3" and dir or nil, segurar = arg == "Sopro"})]=],
[=[local usou = c:usar(arg, {direcao = typeof(dir) == "Vector3" and dir or nil, segurar = arg == "Sopro"})
		-- habilidade usada perto de um guardiao selvagem (ou mirando nele): ele reage ao agressor (direcao aproximada).
		-- Sem dano no guardiao: vida/incapacitacao de dragao selvagem ainda sem regra aprovada.
		if usou and plr.Character then
			local pd = m:GetPivot().Position; local fr = c:frente()
			for _, g in ipairs(workspace:GetChildren()) do
				if g ~= m and g:IsA("Model") and g:GetAttribute("GuardiaoNinho") and g.PrimaryPart then
					local v = g:GetPivot().Position - pd; local vp = Vector3.new(v.X, 0, v.Z)
					if v.Magnitude < 60 or (v.Magnitude < 170 and vp.Magnitude > 1 and fr:Dot(vp.Unit) > 0.5) then IA_Ev.GuardiaoAtacado:Fire(g, plr.Character) end
				end
			end
		end]=])

-- ============================================================== IA_Dragao_Servidor
troca("IAServ", [=[if ok then _G.IA_DRAGOES[m] = c else warn("IA_Dragao: " .. tostring(c)) end]=],
	[=[if ok then _G.IA_DRAGOES[m] = c else warn("IA_Dragao: " .. tostring(c)) end
	m.AncestryChanged:Connect(function(_, p) if not p then _G.IA_DRAGOES[m] = nil end end)     -- limpeza ao remover]=])
troca("IAServ", [=[task.wait(1)]=], [=[-- DEPURACAO VISUAL (so desenvolvimento): Workspace atributo IA_DebugVisual = true mostra, SO a jogadores autorizados
-- (Studio, criador do jogo ou atributo Dev = true no Player), um painel sobre cada guardiao: estado/tarefa, alvo,
-- destino, distancia do ninho, ultima posicao do alvo, energia, habilidade escolhida, motivo de bloqueio, necessidades.
-- O painel vai no PlayerGui do autorizado (os outros jogadores nao recebem nada).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local function autorizado(p) return RunService:IsStudio() or p.UserId == game.CreatorId or p:GetAttribute("Dev") == true end
local function v3(v) return v and ("%.0f, %.0f, %.0f"):format(v.X, v.Y, v.Z) or "-" end
task.spawn(function()
	while true do
		task.wait(0.5)
		local ligado = workspace:GetAttribute("IA_DebugVisual") == true
		for _, p in ipairs(Players:GetPlayers()) do
			local pg = p:FindFirstChildOfClass("PlayerGui")
			if not pg then continue end
			for _, bb in ipairs(pg:GetChildren()) do
				if bb.Name:sub(1, 9) == "IA_Debug_" and not (ligado and autorizado(p)) then bb:Destroy() end
			end
			if not (ligado and autorizado(p)) then continue end
			for m, c in pairs(_G.IA_DRAGOES) do
				if not (m.Parent and m.PrimaryPart) then continue end
				local nome = "IA_Debug_" .. m.Name
				local bb = pg:FindFirstChild(nome)
				if not bb then
					bb = Instance.new("BillboardGui"); bb.Name = nome; bb.Size = UDim2.fromOffset(360, 160); bb.StudsOffset = Vector3.new(0, 32, 0)
					bb.AlwaysOnTop = true; bb.ResetOnSpawn = false; bb.MaxDistance = 2000
					local t = Instance.new("TextLabel"); t.Name = "T"; t.Size = UDim2.fromScale(1, 1); t.BackgroundTransparency = 0.35
					t.BackgroundColor3 = Color3.new(0, 0, 0); t.TextColor3 = Color3.new(1, 1, 0.75); t.TextSize = 13; t.Font = Enum.Font.Code
					t.TextXAlignment = Enum.TextXAlignment.Left; t.TextYAlignment = Enum.TextYAlignment.Top; t.Parent = bb
					bb.Parent = pg
				end
				bb.Adornee = m.PrimaryPart
				local alvo, a = c:maiorAmeaca()
				local pos = c.L:pos()
				bb.T.Text = ("estado   %s  (tarefa %s)\nalvo     %s  nivel %s  %s\ndestino  %s\nninho    %.0f studs | no ar %s\nult.pos  %s\nenergia  %s | habilidade %s\nbloqueio %s\nfome %.2f sede %.2f sono %.2f%s"):format(
					tostring(c.estado), c.tarefa and c.tarefa.nome or "-", alvo and alvo.Name or "-", a and tostring(a.nivel) or "-",
					a and tostring(a.motivo or "") or "", v3(c.destino),
					(Vector3.new(pos.X, 0, pos.Z) - Vector3.new(c.casa.X, 0, c.casa.Z)).Magnitude, tostring(c.L.noAr),
					v3(a and a.ultimaPos), tostring(m:GetAttribute("Energia") or "-"), tostring(m:GetAttribute("IA_Habilidade") or "-"),
					tostring(m:GetAttribute("IA_Bloqueio") or "-"), c.fome, c.sede, c.sono, c.dormente and "\nLOD: dormente (sem jogador perto)" or "")
			end
		end
	end
end)
task.wait(1)]=])

-- ============================================================== Sons (cliente)
troca("Sons", [=[local ativos = {}]=], [=[-- VOZ (comportamento da IA): som num ponto do clipe, com chance e intervalo minimo por dragao (nada de rugir sempre)
-- {fase, som em SonsConfig, chance, volume, tom}
local VOZ = {
	Ninho_Ameaca = {{0.36, "rugido", 1, 1.0, 0.9}}, Reagir_Estimulo = {{0.12, "esforco", 0.8, 0.7, 0.9}},
	Idle_Alerta_Mantido = {{0.5, "esforco", 0.35, 0.55, 0.85}}, Preparar_Combate = {{0.3, "esforco", 0.4, 0.65, 0.8}},
	Comer = {{0.1, "mordida", 1, 0.7, 0.8}, {0.433, "mordida", 1, 0.7, 0.8}, {0.766, "mordida", 1, 0.7, 0.8}},
}
local VOZF = {}; for n, l in pairs(VOZ) do VOZF[n] = {}; for _, e in ipairs(l) do table.insert(VOZF[n], e[1]) end end
local INTERVALO_VOZ = {rugido = 12, esforco = 7, mordida = 0.5}
local ultimaVoz = {}

local ativos = {}]=])
troca("Sons", [=[local function faixa(f) return f and (f[1] + (f[2] - f[1]) * math.random()) or 1 end]=],
	[=[local function faixa(f) return f and (f[1] + (f[2] - f[1]) * math.random()) or 1 end
local function tocarVoz(m, pp, nome, fase)
	for _, ev in ipairs(VOZ[nome]) do
		if ev[1] == fase and math.random() <= ev[3] then
			local k = ev[2]; ultimaVoz[m] = ultimaVoz[m] or {}
			if os.clock() - (ultimaVoz[m][k] or -99) >= (INTERVALO_VOZ[k] or 5) then
				ultimaVoz[m][k] = os.clock()
				tocar(pp, sorteia(Cfg[k]), ev[4], ev[5] * (0.95 + math.random() * 0.1), k == "esforco" and 1.2 or nil)
			end
		end
	end
end]=])
troca("Sons", [=[if ASAS[sv.Name] or PASSOS[sv.Name] then return sv.Name end]=], [=[if ASAS[sv.Name] or PASSOS[sv.Name] or VOZ[sv.Name] then return sv.Name end]=])
troca("Sons", [=[local fases = ASAS[nome] or PASSOS[nome]]=], [=[local fases = ASAS[nome] or PASSOS[nome] or VOZF[nome]]=])
troca("Sons", [=[0.9 + math.random() * 0.2, Cfg.passoPesoCorte)]=], [=[0.9 + math.random() * 0.2, Cfg.passoPesoCorte)
							elseif VOZ[nome] then
								tocarVoz(m, pp, nome, alvo)]=])

-- ============================================================== Apelidos
troca("Apelidos", [=[Correr_Frenagem = c("Parada"), Giro_E = c("Andar"), Giro_D = c("Andar"),]=],
	[=[Correr_Frenagem = c("Parada"), Giro_E = c("Andar"), Giro_D = c("Andar"),
	Ninho_Inspecionar = c("Observar_Farejar"),       -- clipes proprios de comportamento (30/10) sao achados pelo prefixo]=])

-- ============================================================== backup + gravacao (so chega aqui se TODAS as trocas casaram)
local bk = SS:FindFirstChild("Backup_Scripts_IA_Selvagem")
if not bk then
	bk = Instance.new("Folder"); bk.Name = "Backup_Scripts_IA_Selvagem"
	for k, s in pairs(alvos) do
		local c = s:Clone(); c.Name = k .. "__" .. s.Name
		if c:IsA("BaseScript") then c.Enabled = false end
		c.Parent = bk
	end
	bk.Parent = SS
end
local n = 0
for k, s in pairs(alvos) do if novo[k] ~= s.Source then s.Source = novo[k]; n += 1 end end
return "aplicado: " .. n .. " scripts"
