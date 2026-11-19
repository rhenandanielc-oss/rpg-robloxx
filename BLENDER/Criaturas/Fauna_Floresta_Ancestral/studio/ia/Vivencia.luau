-- IA_FaunaFloresta/Vivencia (17/11/2026) - rotina AUTONOMA de vida dos animais da Floresta (habitats aprovados pelo usuario
-- 17/11). Roda no repouso do controlador (K:esperarComVivencia) e devolve o controle assim que surge uma ameaca (prioridade).
--   Cervo : repousar no abrigo -> andar ate um arbusto -> ramonear (PastarEntrar/Pastar/PastarSair) -> agua -> beber
--           (BeberEntrar/Beber/BeberSair) -> voltar ao abrigo
--   Javali: repousar -> farejar -> fucar (come bolotas/raizes/larvas) -> agua -> beber -> voltar
--   Coruja: observar do galho de vigia -> mergulhar no roedor de TESTE -> voltar ao poleiro com a presa -> comer ->
--           (de tempos em tempos) descer a margem, beber -> poleiro abrigado e cochilar
-- Cada acao: selecao do ponto (reserva) -> aproximacao (rota) -> alinhamento (entra pelo eixo do ponto, sem girar parado) ->
-- conferencia do contato (boca/bico x agua/folhas) -> acao (pivo parado, corpo pela linha dos cascos) -> saida -> retorno.
-- Interrupcao: libera a reserva, solta a presa, cancela a acao (token) e volta ao fluxo de ameaca; a rotina recomeca do
-- inicio (volta ao abrigo antes), nunca repete fora do ponto a acao interrompida. Consumo e so visual: nada de inventario,
-- loot, dano, economia, spawn global ou persistencia. Numeros [A TESTAR].
local Config = require(script.Parent:WaitForChild("Config"))
local Movimento = require(script.Parent:WaitForChild("Movimento"))
local plano, angulo = Movimento.plano, Movimento.angulo

local V = {}
V.__index = V
V.reservas = {}          -- id do ponto -> controlador que o ocupa (compartilhado entre animais)

local rng = Random.new()
local function sorteio(par) return par[1] + rng:NextNumber() * (par[2] - par[1]) end

function V.novo(k, cena)
	local self = setmetatable({}, V)
	self.k, self.cena, self.esp = k, cena, k.especie
	self.cfg = Config.especies[k.especie].vivencia
	self.ciclos, self.reserva, self.presa = 0, nil, nil
	self.eventos = {}
	return self
end

-------------------------------------------------------------------------------- utilidades
function V:pastaIA() return self.k.m.Parent and self.k.m.Parent.Parent and self.k.m.Parent.Parent:FindFirstChild("IA") end
function V:fatorTempo()
	local p = self:pastaIA(); local f = p and p:GetAttribute("TempoTeste")
	return (type(f) == "number" and f > 0) and f or (Config.vivencia.tempoTeste or 1)
end
function V:evento(txt)
	local e = string.format("%.1f %s", os.clock() - self.k.t0, txt)
	table.insert(self.eventos, e); if #self.eventos > 40 then table.remove(self.eventos, 1) end
	self.k:registrar("viv: " .. txt)
	self.k.m:SetAttribute("Vivencia", txt)
	self.k.m:SetAttribute("VivenciaLog", table.concat(self.eventos, "\n"))
end
-- espera 's' (dividido pelo TempoTeste) olhando a ameaca; devolve true se surgiu ameaca
function V:esperar(s)
	local t, alvo = 0, s / self:fatorTempo()
	while t < alvo do
		if not self.k:vivo() then return true end
		t += self.k:quadro()
		if self.k.alvo then return true end
	end
	return false
end
function V:reservar(id)
	local dono = V.reservas[id]
	if dono and dono ~= self.k and dono:vivo() then return false end
	V.reservas[id] = self.k; self.reserva = id; return true
end
function V:liberar()
	if self.reserva and V.reservas[self.reserva] == self.k then V.reservas[self.reserva] = nil end
	self.reserva = nil
end
function V:limpar()
	self:liberar()
	if self.presa then self.presa:Destroy(); self.presa = nil end
	if self.conPresa then self.conPresa:Disconnect(); self.conPresa = nil end
	pcall(function() self.k.anim:pararAcao(0.2) end)
end

-- ponto bloqueado? (reserva de outro animal, jogador em cima, ou algo solido no lugar de pe)
function V:bloqueado(P)
	local dono = V.reservas[P.id]
	if dono and dono ~= self.k and dono:vivo() then return "reservado" end
	for _, pl in ipairs(game:GetService("Players"):GetPlayers()) do
		local c = pl.Character; local r = c and c:FindFirstChild("HumanoidRootPart")
		if r and plano(r.Position - P.pos).Magnitude < 5 then return "jogador no ponto" end
	end
	local op = OverlapParams.new(); op.FilterType = Enum.RaycastFilterType.Exclude
	local ign = { self.k.m, workspace.Terrain }
	for _, x in ipairs(self.k.mov.vizinhos or {}) do table.insert(ign, x) end
	op.FilterDescendantsInstances = ign
	for _, x in ipairs(workspace:GetPartBoundsInBox(CFrame.new(P.pos + Vector3.new(0, 2, 0)), Vector3.new(2.4, 3, 2.4), op)) do
		if x.CanCollide and not x:IsDescendantOf(workspace.Floresta_Blender) then return "obstaculo: " .. x.Name end
	end
	return nil
end

-- escolhe o ponto livre de um grupo (ordem sorteada); espera um pouco se todos estiverem reservados; limita tentativas
function V:escolher(grupo)
	local lista = table.clone(self.cena.pontos[self.esp][grupo] or {})
	for i = #lista, 2, -1 do local j = rng:NextInteger(1, i); lista[i], lista[j] = lista[j], lista[i] end
	local tent = 0
	for rodada = 1, 2 do
		for _, P in ipairs(lista) do
			tent += 1; if tent > (Config.vivencia.tentativasPonto or 2) + #lista then break end
			local b = self:bloqueado(P)
			if not b and self:reservar(P.id) then return P end
			self:evento(string.format("ponto %s indisponivel (%s)", P.id, tostring(b or "reservado")))
		end
		if rodada == 1 then
			if self:esperar(sorteio(Config.vivencia.esperaReserva)) then return nil, "ameaca" end
		end
	end
	return nil, "sem ponto livre"
end

-------------------------------------------------------------------------------- deslocamento ate um ponto de acao
-- aproximacao: rota (Pathfinding se preciso) ate um ponto ANTES do ponto, no eixo dele; depois anda reto ate o pivo.
-- Assim o animal chega alinhado sem girar parado (o giro sai da passada).
function V:irAte(P)
	local k = self.k
	local C = k.cfg.clipes
	local rg = (k.mov.raioGiro or 3)
	local dir = P.dir
	local pre = P.pos - dir * (P.preDist or math.max(4, 3.2 * rg))   -- longe o bastante para endireitar na linha antes do ponto
	local t0 = os.clock()
	local function perigo() return k.alvo ~= nil or (os.clock() - t0 > Config.vivencia.tempoMaxIda) end
	-- ja esta perto e quase alinhado? pula o ponto de antes
	local dAte = plano(P.pos - k:pos())
	local lateral = (dAte - dir * dAte:Dot(dir)).Magnitude
	local alinhado = dAte:Dot(dir) > 1.5 and dAte:Dot(dir) < 3.2 * rg + 2 and lateral < 0.6 * k.fe and math.abs(angulo(k.mov:frente(), dir)) < math.rad(12)
	if not alinhado then
		local r = k:retorno(C.andar, C.repouso, perigo, pre, "Vivencia_Andando", 2.0)
		if r == "ameaca" then return k.alvo and "ameaca" or "tempo" end
	end
	-- trecho final reto ate o pivo do ponto (o alvo da acao, ex. o arbusto, nao conta como obstaculo: a boca entra nele)
	if k.anim.baseNome ~= C.andar then k.anim:base(C.andar, 0.25, 1) end
	k.mov.ignorarTemp = P.alvoInst and { P.alvoInst } or nil
	local erro = math.huge
	local tf = 0
	-- segue a LINHA do eixo do ponto (perseguicao pura: mira um ponto a frente na linha), entao chega com a direcao do ponto
	local look = math.max(1.2, 0.6 * rg)
	-- andando devagar no ajuste final o animal fecha mais a curva (metade do raio da passada normal); nunca gira parado
	local rgOrig = k.mov.raioGiro
	if rgOrig then k.mov.raioGiro = rgOrig * 0.5 end
	while k:vivo() do
		local dt = k:quadro(); tf += dt
		if k.alvo then k.mov.raioGiro = rgOrig; return "ameaca" end
		local p = k:pos()
		local d = plano(P.pos - p)
		local falta = d:Dot(dir)                                   -- distancia ao ponto ao longo do eixo
		erro = d.Magnitude
		if falta <= (Config.vivencia.precisao or 0.45) * k.fe then break end
		if tf > 12 then k.mov.raioGiro = rgOrig; return "nao alinhou" end
		local naLinha = P.pos - dir * falta                        -- projecao do animal na linha do eixo
		local mira = naLinha + dir * math.min(look, falta)
		local v = k:v("Andar")
		local passo = math.min(v, math.max(0.3 * v, falta / math.max(dt, 1e-3)))
		if not k.mov:passo(dt, passo, plano(mira - p), math.rad(60)) then   -- ajuste final andando devagar: curva mais fechada que o clipe de curva
			k.mov.ignorarTemp = nil; k.mov.raioGiro = rgOrig
			return "bloqueado na chegada (" .. tostring(k.mov.ultimoBloqueio) .. ")"
		end
	end
	k.mov.raioGiro = rgOrig
	erro = plano(P.pos - k:pos()).Magnitude
	k.mov.ignorarTemp = nil
	k.anim:base(C.repouso, 0.35)
	local ang = math.deg(math.abs(angulo(k.mov:frente(), dir)))
	return "ok", erro, ang
end

-- assenta o corpo no terreno do ponto (cascos no fundo, corpo pela inclinacao) e mede o contato da boca/bico
function V:assentar(P, clipeContato)
	local k = self.k
	local cf, pitch = k:poseNoTerreno(k:pos(), k.mov:frente())
	-- transicao curta (0,3 s) da pose nivelada para a pose no terreno (nao desliza: so assenta)
	local c0 = k.m:GetPivot()
	for i = 1, 9 do k.m:PivotTo(c0:Lerp(cf, i / 9)); k:quadro() end
	local medida = nil
	local b = clipeContato and k.cfg.boca and k.cfg.boca[clipeContato]
	if b then
		local boca = (cf * CFrame.new(b * k.fe)).Position
		if P.tipo == "agua" then
			local w = k.mov:agua(boca)
			medida = { tipo = "agua", boca = boca, agua = w, erro = w and (boca.Y - w) or nil }
		elseif P.tipo == "folhas" and P.folhas then
			local f = P.folhas   -- {centro, meio (tamanho/2)}
			local rel = boca - f.centro
			local dentro = math.abs(rel.X) <= f.meio.X and math.abs(rel.Z) <= f.meio.Z and math.abs(rel.Y) <= f.meio.Y
			medida = { tipo = "folhas", boca = boca, dentro = dentro, alturaRel = rel.Y }
		else
			local yc = k.mov:chao(boca)
			medida = { tipo = "solo", boca = boca, erro = yc and (boca.Y - yc) or nil }
		end
	end
	k.m:SetAttribute("UltimoContato", medida and game:GetService("HttpService"):JSONEncode({
		tipo = medida.tipo, erro = medida.erro, dentro = medida.dentro, alturaRel = medida.alturaRel,
		pitch = math.deg(pitch) }) or "")
	return medida, pitch
end

-- toca uma acao parado (entrada, laco por 'dur' s, saida) ou um clipe 'vezes'; devolve true se interrompida por ameaca
function V:acao(entrar, laco, sair, dur, unico, vezes)
	local k = self.k
	local tok = k.tok
	if unico then
		for i = 1, vezes or 1 do
			local r = k:transicao(unico, { fade = 0.25, parar = function() return k.alvo and "ameaca" or nil end, proxima = { k.cfg.clipes.repouso, 1 } })
			if r == "ameaca" or k.alvo then return true end
		end
		return false
	end
	if entrar then
		local r = k:transicao(entrar, { fade = 0.25, parar = function() return k.alvo and "ameaca" or nil end })
		if r == "ameaca" or k.alvo then return true end
	end
	k.anim:base(laco, 0.15, 1)
	if self:esperar(dur * self:fatorTempo()) then   -- a acao dura o tempo real (o TempoTeste so encurta o repouso)
		-- ameaca no meio: sai da acao rapido (clipe de saida acelerado) antes de reagir, sem repetir a acao
		if sair then k.anim:acao(sair, 0.1); k.anim:base(k.cfg.clipes.repouso, 0.3) end
		return true
	end
	if sair then k:transicao(sair, { fade = 0.1, proxima = { k.cfg.clipes.repouso, 1 } }) end
	return k.alvo ~= nil
end

-- sai do ponto da acao dando a volta ANDANDO em curva fechada (devagar) para o lado por onde entrou: na margem rasa a
-- frente e agua funda e o raio de curva normal nao cabe (o animal ficava preso girando). Nunca gira parado.
function V:sairDoPonto(P)
	local k = self.k; local C = k.cfg.clipes
	local rg = k.mov.raioGiro or 3
	local volta = P.pos - P.dir * (P.preDist or math.max(4, 3.2 * rg))
	local rgOrig, pmOrig = k.mov.raioGiro, k.mov.profMax
	if rgOrig then k.mov.raioGiro = rgOrig * 0.4 end
	if pmOrig then k.mov.profMax = pmOrig + 0.4 * k.fe end
	k.mov.ignorarTemp = P.alvoInst and { P.alvoInst } or nil
	k.anim:base(C.andar, 0.25, 1)
	local t = 0
	while k:vivo() and t < 8 do
		local dt = k:quadro(); t += dt
		if k.alvo then break end
		local d = plano(volta - k:pos())
		if d.Magnitude < 1 or math.abs(angulo(k.mov:frente(), d.Unit)) < math.rad(30) then break end
		k.mov:passo(dt, k:v("Andar") * 0.45, d, math.rad(75))
	end
	k.mov.raioGiro, k.mov.profMax = rgOrig, pmOrig
end

-- volta ao abrigo/casa (andando, curva com a passada)
function V:voltar()
	local k = self.k; local C = k.cfg.clipes
	if plano(k.casa.Position - k:pos()).Magnitude < 5 * k.fe then return false end
	-- sai do ultimo ponto ainda ignorando o alvo dele (ex.: o arbusto colado a margem) e aceita chegar a 5 studs x escala da casa
	k.mov.ignorarTemp = self.ultimoAlvoInst and { self.ultimoAlvoInst } or nil
	local r = k:retorno(C.andar, C.repouso, function() return k.alvo ~= nil end, k.casa.Position, "Vivencia_Voltando", 5 * k.fe)
	k.mov.ignorarTemp = nil; self.ultimoAlvoInst = nil
	k.anim:base(C.repouso, 0.35)
	return r == "ameaca"
end

-- uma etapa "ir + acao" para terrestres; devolve "ameaca" | "ok" | motivo de pular
function V:visitar(grupo, contato, fazer)
	local P, porque = self:escolher(grupo)
	if not P then self:evento(grupo .. ": " .. tostring(porque)); return porque == "ameaca" and "ameaca" or "pulou" end
	self:evento("indo a " .. P.id)
	local r, erro, ang = self:irAte(P)
	if r == "ok" and (erro > 1.0 * self.k.fe or ang > 25) then
		self:evento(string.format("%s: chegou torto (%.2f, %.0f graus) - refaz a aproximacao", P.id, erro, ang))
		r, erro, ang = self:irAte(P)
	end
	if r ~= "ok" then self:liberar(); self:evento(P.id .. ": " .. tostring(r)); return r == "ameaca" and "ameaca" or "pulou" end
	if self:bloqueado(P) == "jogador no ponto" then self:liberar(); return "pulou" end
	local medida, pitch = self:assentar(P, contato)
	self:evento(string.format("%s: chegou (erro %.2f, %.0f graus, corpo %.0f graus)%s", P.id, erro, ang, math.deg(pitch),
		medida and (medida.erro and string.format(", contato %.2f", medida.erro) or (medida.dentro ~= nil and (", boca nas folhas: " .. tostring(medida.dentro)) or "")) or ""))
	self.k:mudar(fazer.estado, P.id)
	local interrompeu = fazer.rodar()
	self.ultimoAlvoInst = P.alvoInst
	self:liberar()
	if not interrompeu and P.tipo == "agua" then self:sairDoPonto(P) end
	if interrompeu then self:evento(P.id .. ": interrompido (ameaca)"); return "ameaca" end
	self:evento(P.id .. ": concluido")
	return "ok"
end

-------------------------------------------------------------------------------- CERVO
function V:cicloCervo()
	local k, Cv = self.k, self.cfg.clipes
	if self:voltar() then return "ameaca" end
	k:mudar("Vivencia_Repouso"); k.anim:base(k.cfg.clipes.repouso, 0.3)
	local dur = sorteio(self.cfg.repouso)
	local extra = self.cfg.extrasRepouso[rng:NextInteger(1, #self.cfg.extrasRepouso)]
	if self:esperar(dur * 0.6) then return "ameaca" end
	if self:acao(nil, nil, nil, nil, extra) then return "ameaca" end
	if self:esperar(dur * 0.4) then return "ameaca" end
	local r = self:visitar("arbusto", "Pastar", { estado = "Vivencia_Comendo", rodar = function()
		return self:acao(Cv.pastarEntrar, Cv.pastar, Cv.pastarSair, sorteio(self.cfg.pastar)) end })
	if r == "ameaca" then return r end
	r = self:visitar("agua", "Beber", { estado = "Vivencia_Bebendo", rodar = function()
		return self:acao(Cv.beberEntrar, Cv.beber, Cv.beberSair, sorteio(self.cfg.beber)) end })
	if r == "ameaca" then return r end
	if self:voltar() then return "ameaca" end
	return "ok"
end

-------------------------------------------------------------------------------- JAVALI
function V:cicloJavali()
	local k, Cj = self.k, self.cfg.clipes
	if self:voltar() then return "ameaca" end
	k:mudar("Vivencia_Repouso"); k.anim:base(k.cfg.clipes.repouso, 0.3)
	if self:esperar(sorteio(self.cfg.repouso)) then return "ameaca" end
	local r = self:visitar("farejar", "Farejar", { estado = "Vivencia_Farejando", rodar = function()
		return self:acao(nil, nil, nil, nil, Cj.farejar) end })
	if r == "ameaca" then return r end
	r = self:visitar("fucar", "Fucar", { estado = "Vivencia_Comendo", rodar = function()
		return self:acao(nil, nil, nil, nil, Cj.fucar, self.cfg.fucar) end })
	if r == "ameaca" then return r end
	r = self:visitar("agua", "Beber", { estado = "Vivencia_Bebendo", rodar = function()
		return self:acao(nil, nil, nil, nil, Cj.beber, self.cfg.beber) end })
	if r == "ameaca" then return r end
	if self:voltar() then return "ameaca" end
	return "ok"
end

-------------------------------------------------------------------------------- CORUJA
-- roedor de TESTE: so um marcador visual local (nao e especie de producao nem sistema de caca)
function V:criarPresa(pos)
	local m = Instance.new("Model"); m.Name = "Roedor_Teste"
	local corpo = Instance.new("Part"); corpo.Name = "Corpo"; corpo.Size = Vector3.new(0.32, 0.22, 0.55)
	corpo.Color = Color3.fromRGB(110, 86, 62); corpo.Material = Enum.Material.Fabric; corpo.Anchored = true
	corpo.CanCollide = false; corpo.CanQuery = false; corpo.CanTouch = false; corpo.CastShadow = false
	local cab = corpo:Clone(); cab.Name = "Cabeca"; cab.Size = Vector3.new(0.2, 0.18, 0.2)
	corpo.CFrame = CFrame.new(pos + Vector3.new(0, 0.11, 0)); cab.CFrame = corpo.CFrame * CFrame.new(0, 0.02, -0.33)
	corpo.Parent = m; cab.Parent = m; m.PrimaryPart = corpo
	m:SetAttribute("AlvoTeste", true)
	m.Parent = self.cena.pastaMarcadores or workspace
	return m
end
function V:segurarPresa()
	local k = self.k
	local dE, dD
	for _, b in ipairs(k.m:GetDescendants()) do if b:IsA("Bone") then if b.Name == "DedosE" then dE = b elseif b.Name == "DedosD" then dD = b end end end
	if not (dE and dD) or not self.presa then return end
	self.conPresa = game:GetService("RunService").Heartbeat:Connect(function()
		if not self.presa or not self.presa.Parent then return end
		local p = (dE.TransformedWorldCFrame.Position + dD.TransformedWorldCFrame.Position) / 2
		self.presa:PivotTo(CFrame.lookAt(p - Vector3.new(0, 0.12, 0), p - Vector3.new(0, 0.12, 0) + k.mov:frente()))
	end)
end
function V:soltarPresa()
	if self.conPresa then self.conPresa:Disconnect(); self.conPresa = nil end
end

-- voa ao destino (poleiro real ou ponto virtual da vivencia) usando o voo validado do controlador
function V:voarPara(destino, opts)
	local k = self.k
	local pts, porque, dirP = k:planoVoo(destino, opts and opts.pousar)
	if not pts then self:evento("voo para " .. destino .. " recusado: " .. tostring(porque)); return false end
	k:voar(destino, pts, dirP, opts)
	return true
end

function V:cicloCoruja()
	local k, Cc, cena = self.k, self.cfg.clipes, self.cena
	local PL = cena.coruja
	-- 1) vai ao galho de vigia (se nao estiver nele) e observa
	if k.poleiro ~= PL.vigia then
		if not self:voarPara(PL.vigia, { decolar = Cc.decolarCalmo, estadoDecolagem = "Vivencia_Decolando", estadoPouso = "Vivencia_Pousando" }) then return "pulou" end
	end
	k:mudar("Vivencia_Observando", k.poleiro); k.anim:base(k.cfg.clipes.repouso, 0.3)
	local olhares = { Cc.olharE, Cc.inclinar, Cc.olharD, Cc.espreitar }
	local tObs = sorteio(self.cfg.observar)
	for i = 1, 3 do
		if self:esperar(tObs / 4) then return "ameaca" end
		if self:acao(nil, nil, nil, nil, olhares[rng:NextInteger(1, #olhares)]) then return "ameaca" end
	end
	-- 2) caca o roedor de teste
	local zona = cena.pontos.Coruja.presa[rng:NextInteger(1, #cena.pontos.Coruja.presa)]
	if not self.presa then self.presa = self:criarPresa(zona.pos) end
	k.poleiros.Presa = { topo = zona.pos, inst = self.presa, virtual = true }
	self:evento("viu o roedor de teste em " .. zona.id)
	if k:poleiroLivre("Presa") == false then self:evento("presa com jogador perto: nao desce") else
		if self:voarPara("Presa", { decolar = Cc.decolarCalmo, pousar = Cc.mergulho, semRepouso = true,
			estadoDecolagem = "Vivencia_Decolando", estadoPouso = "Vivencia_Mergulho" }) then
			local erro = plano(self.presa:GetPivot().Position - k:pos()).Magnitude
			self:evento(string.format("captura: garras a %.2f do roedor", erro))
			self:segurarPresa()
			if self:esperar(0.6) then self:limpar(); return "ameaca" end
			-- 3) volta ao galho de vigia com a presa e come
			local foi = self:voarPara(PL.vigia, { decolar = Cc.decolarCalmo, estadoDecolagem = "Vivencia_Levando", estadoPouso = "Vivencia_Pousando" })
			if not foi then k.poleiros.Presa = nil; self:limpar(); return "pulou" end
			k:mudar("Vivencia_Comendo", k.poleiro)
			local r = k:transicao(Cc.comer, { fade = 0.3, parar = function() return k.alvo and "ameaca" or nil end, proxima = { k.cfg.clipes.repouso, 1 } })
			self:soltarPresa(); if self.presa then self.presa:Destroy(); self.presa = nil end
			self:evento("comeu (roedor de teste removido)")
			if r == "ameaca" or k.alvo then k.poleiros.Presa = nil; return "ameaca" end
		end
	end
	k.poleiros.Presa = nil
	-- 4) agua ocasional
	local pasta = self:pastaIA()
	local forcar = pasta and pasta:GetAttribute("ForcarAgua")
	self.ciclos += 1
	if forcar or self.ciclos % (self.cfg.aguaCadaCiclos or 3) == 0 then
		if pasta then pasta:SetAttribute("ForcarAgua", nil) end
		local M = cena.pontos.Coruja.agua[1]
		if self:reservar(M.id) and not self:bloqueado(M) then
			k.poleiros.Margem = { topo = M.pos, inst = cena.pastaMarcadores or workspace.Terrain, virtual = true }
			self:evento("descendo a margem para beber")
			if self:voarPara("Margem", { decolar = Cc.decolarCalmo, estadoDecolagem = "Vivencia_Decolando", estadoPouso = "Vivencia_PousandoMargem" }) then
				local medida = self:assentar(M, "Beber")
				self:evento(string.format("na margem: bico x agua %.2f", medida and medida.erro or -99))
				k:mudar("Vivencia_Bebendo", "Margem")
				local inter = self:acao(nil, nil, nil, nil, Cc.beber)
				self:liberar()
				if inter then return "ameaca" end
				self:voarPara(PL.vigia, { decolar = Cc.decolarCalmo, estadoDecolagem = "Vivencia_Decolando", estadoPouso = "Vivencia_Pousando" })
			end
			k.poleiros.Margem = nil
		else self:evento("margem ocupada/bloqueada: fica para o proximo ciclo") end
		self:liberar()
	end
	-- 5) poleiro abrigado e cochilo
	if self:voarPara(PL.abrigo, { decolar = Cc.decolarCalmo, estadoDecolagem = "Vivencia_Decolando", estadoPouso = "Vivencia_Pousando" }) then
		k:mudar("Vivencia_Repouso", k.poleiro)
		if self:acao(nil, nil, nil, nil, Cc.ajeitar) then return "ameaca" end
		local r = k:transicao(Cc.adormecer, { fade = 0.3, parar = function() return k.alvo and "ameaca" or nil end })
		if r == "ameaca" or k.alvo then return "ameaca" end
		k.anim:base(Cc.dormindo, 0.2, 1)
		local acordou = self:esperar(sorteio(self.cfg.repouso))
		k:transicao(Cc.despertar, { fade = 0.15, proxima = { k.cfg.clipes.repouso, 1 } })
		if acordou then return "ameaca" end
	end
	return "ok"
end

-------------------------------------------------------------------------------- laco
function V:rodar()
	local k = self.k
	local ciclo = (self.esp == "Cervo" and self.cicloCervo) or (self.esp == "Javali" and self.cicloJavali) or self.cicloCoruja
	while k:vivo() and not k.alvo do
		local ok, r = pcall(ciclo, self)
		if not ok then self:evento("ERRO " .. tostring(r)); self:limpar(); warn("[FaunaIA] vivencia", self.esp, r); task.wait(2); continue end
		if r == "ameaca" then self:limpar(); self:evento("ameaca: rotina pausada"); return "ameaca" end
		if r == "pulou" then if self:esperar(3) then self:limpar(); return "ameaca" end end
		self.ciclos = (self.esp == "Coruja") and self.ciclos or self.ciclos + 1
		k.m:SetAttribute("VivenciaCiclos", self.ciclos)
	end
	self:limpar()
	return k.alvo and "ameaca" or "fim"
end

return V
