-- Combate_Dragao_Servidor (Script, ServerScriptService): registra dragoes no Nucleo de combate, atende a IA
-- (IA_Eventos.AtaqueSolicitado) e pedidos de DONOS pelo RemoteEvent Pedido (sempre validados no servidor).
local Players = game:GetService("Players")
local SSS = game:GetService("ServerScriptService"); local SS = game:GetService("ServerStorage"); local RS = game:GetService("ReplicatedStorage")
local pasta = SSS:WaitForChild("Combate_Dragao")
local N = require(pasta.Nucleo); local Cfg = require(pasta.ConfigCombate)
local rede = RS:WaitForChild("Combate_Dragoes")
local Pedido = rede:FindFirstChild("Pedido") or Instance.new("RemoteEvent"); Pedido.Name = "Pedido"; Pedido.Parent = rede

local function dragao(m) return m:IsA("Model") and m:FindFirstChildOfClass("AnimationController") and m:GetAttribute("FormaRegional") end
for _, m in ipairs(workspace:GetChildren()) do if dragao(m) then N.registrar(m) end end
workspace.ChildAdded:Connect(function(m) task.defer(function() if dragao(m) then N.registrar(m) end end) end)

-- escolha da IA (ofensiva): Ruptura Vulcanica quando ha alvo no leque de erupcao e o dragao esta no solo (com espaco
-- minimo entre usos alem da recarga, para nao ficar repetitiva), Tempestade contra grupos, cauda atras, mordida/garra perto,
-- sopro a media distancia, arremetida a longa distancia. So entram habilidades da forma (temHabilidade).
local ultimaRuptura = {}
local function raiz(m) return m and (m:FindFirstChild("HumanoidRootPart") or m.PrimaryPart) end
local function escolher_antigo(c, alvo)          -- substituida pela escolha tatica abaixo
	local r = raiz(alvo); if not r then return nil end
	local p = c.m:GetPivot().Position; local v = Vector3.new(r.Position.X - p.X, 0, r.Position.Z - p.Z); local d = v.Magnitude
	local f = c:frente(); local atras = d > 1 and f:Dot(v.Unit) < -0.2
	local perto = 0; for _, a in ipairs(c:alvosValidos()) do if (raiz(a).Position - p).Magnitude < Cfg.habilidades.Tempestade.raio then perto += 1 end end
	local ordem = {}
	local R = Cfg.habilidades.Ruptura
	if c:temHabilidade("Ruptura") and d > 10 and d < R.aneis[#R.aneis] + 4 and not atras and os.clock() - (ultimaRuptura[c.m] or -99) > R.recarga * 1.6 then
		table.insert(ordem, "Ruptura")
	end
	if c:temHabilidade("Dominio") and not c.m:GetAttribute("DominioAtivo") then table.insert(ordem, "Dominio") end
	if perto >= 2 then table.insert(ordem, "Tempestade") end
	local dBoca = (c:boca() - r.Position).Magnitude                   -- alcance real da mordida e a partir da boca
	if dBoca < 26 then table.insert(ordem, math.random() < 0.6 and "Mordida" or "Garra")
	elseif d < 45 then                                                -- embaixo/ao lado do corpo (fora do alcance da boca)
		table.insert(ordem, atras and "Cauda" or "Garra"); table.insert(ordem, "Tempestade"); table.insert(ordem, "Cauda")
	elseif d < 95 then table.insert(ordem, "Sopro")
	elseif d < 170 then table.insert(ordem, "Arremetida"); table.insert(ordem, "Sopro") end
	for _, h in ipairs(ordem) do
		if c:temHabilidade(h) and c:podeUsar(h) then
			if h == "Ruptura" then ultimaRuptura[c.m] = os.clock() end
			return h
		end
	end
	return nil
end
-- PATCH_IA_SELVAGEM: escolha TATICA (distancia, altura, linha de visao, espaco acima, grupo de verdade, trajeto livre,
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
	local pePos = c.peE and c.peE.TransformedWorldCFrame.Position.Y or (p.Y - 10)
	local dyPe = r.Position.Y - pePos; local mesmoNivel = dyPe > -12 and dyPe < 20       -- garras/cauda/ruptura: alvo no chao do dragao
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
	elseif d < 45 and not noAr and mesmoNivel then add(atras and "Cauda" or "Garra", 0.95)
	elseif d < 45 then table.insert(bloqueio, "corpo a corpo: desnivel") end
	if atras and d < 62 and mesmoNivel then add("Cauda", 1.0) end
	-- Ruptura: so no solo (o Nucleo confirma), alvo no leque a frente, intervalo extra entre usos
	local R = Cfg.habilidades.Ruptura
	if not noAr and mesmoNivel and d > 10 and d < R.aneis[#R.aneis] + 4 and not atras and os.clock() - (ultimaRuptura[c.m] or -99) > R.recarga * 1.6 then
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

-- IA_Eventos: o mesmo par de pastas/eventos que o Territorio cria (busca ou cria; sem esperar)
local IA_Ev = SS:FindFirstChild("IA_Eventos") or Instance.new("Folder"); IA_Ev.Name = "IA_Eventos"; IA_Ev.Parent = SS
for _, n in ipairs({"OvoColetado", "AtaqueSolicitado", "GuardiaoAtacado"}) do if not IA_Ev:FindFirstChild(n) then local e = Instance.new("BindableEvent"); e.Name = n; e.Parent = IA_Ev end end
do
	IA_Ev.AtaqueSolicitado.Event:Connect(function(m, alvo)
		local c = N.registro[m] or (dragao(m) and N.registrar(m)); if not c then return end
		local h = escolher(c, alvo); if not h then return end
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
		end)
	end)
end

-- pedidos de jogadores: so o dono, com intervalo minimo; o cliente manda SO a habilidade/elemento/direcao
local ultimo = {}
Pedido.OnServerEvent:Connect(function(plr, m, acao, arg, dir)
	if typeof(m) ~= "Instance" or not N.registro[m] then return end
	if m:GetAttribute("DonoUserId") ~= plr.UserId then return end
	local c0 = N.registro[m]
	if acao == "mira" then                                                -- direcao da mira (so usada pelo sopro segurado)
		if typeof(dir) == "Vector3" and dir.Magnitude > 0.5 and dir.Magnitude < 2 and os.clock() - (c0.miraT or 0) > 0.05 then c0.miraDir = dir.Unit; c0.miraT = os.clock() end
		return
	end
	if acao == "soltar" then c0.segurando = false; return end
	if m:GetAttribute("EmAtaque") == "MordidaAerea" then return end        -- ataque da montaria em curso (sem sobrepor)
	if os.clock() - (ultimo[plr] or 0) < Cfg.pedidoIntervaloMin then return end
	ultimo[plr] = os.clock()
	local c = N.registro[m]
	if acao == "elemento" and typeof(arg) == "string" then c:trocarElemento(arg); return end
	if acao == "usar" and typeof(arg) == "string" and (Cfg.habilidades[arg] or Cfg.basicos[arg]) then
		if arg == "Sopro" and not c.ocupado then c.segurando = true; c.miraDir = typeof(dir) == "Vector3" and dir.Unit or nil end
		local usou = c:usar(arg, {direcao = typeof(dir) == "Vector3" and dir or nil, segurar = arg == "Sopro"})
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
		end
	end
end)
Players.PlayerRemoving:Connect(function(p) ultimo[p] = nil end)

-- depuracao (somente servidor)
local dbg = SS:FindFirstChild("Combate_Debug") or Instance.new("BindableFunction"); dbg.Name = "Combate_Debug"; dbg.Parent = SS
dbg.OnInvoke = function(cmd, nome, a, b)
	local m = workspace:FindFirstChild(nome or "Dragao_V14"); local c = m and (N.registro[m] or N.registrar(m)); if not c then return "sem dragao" end
	if cmd == "usar" then return c:usar(a, b) end
	if cmd == "trocar" then return c:trocarElemento(a) end
	if cmd == "pode" then return c:podeUsar(a) end
	if cmd == "auditar" then return table.concat(c:auditarDados(), "; ") end
	if cmd == "lista" then return table.concat(Cfg.habilidadesForma[c.forma] or {}, ",") .. " | elementos=" .. table.concat(c:elementos(), ",") end
	if cmd == "escolher" then return escolher(c, b) end
	if cmd == "info" then
		local rec = {}; for h, t in pairs(c.recargas) do if t > os.clock() then table.insert(rec, ("%s %.1fs"):format(h, t - os.clock())) end end
		return ("elemento=%s equipados=[%s] energia=%d ocupado=%s dominio=%s recargas=[%s]"):format(tostring(m:GetAttribute("ElementoAtivo")), table.concat(c:elementos(), ","), c.energia, tostring(c.ocupado), tostring(m:GetAttribute("DominioAtivo")), table.concat(rec, ", "))
	end
end
