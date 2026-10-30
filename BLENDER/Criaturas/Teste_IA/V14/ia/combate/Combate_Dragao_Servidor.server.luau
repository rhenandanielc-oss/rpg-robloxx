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
local function escolher(c, alvo)
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
-- IA_Eventos: o mesmo par de pastas/eventos que o Territorio cria (busca ou cria; sem esperar)
local IA_Ev = SS:FindFirstChild("IA_Eventos") or Instance.new("Folder"); IA_Ev.Name = "IA_Eventos"; IA_Ev.Parent = SS
for _, n in ipairs({"OvoColetado", "AtaqueSolicitado", "GuardiaoAtacado"}) do if not IA_Ev:FindFirstChild(n) then local e = Instance.new("BindableEvent"); e.Name = n; e.Parent = IA_Ev end end
do
	IA_Ev.AtaqueSolicitado.Event:Connect(function(m, alvo)
		local c = N.registro[m] or (dragao(m) and N.registrar(m)); if not c then return end
		local h = escolher(c, alvo); if h then c:usar(h, {alvo = alvo}) end
	end)
end

-- pedidos de jogadores: so o dono, com intervalo minimo; o cliente manda SO a habilidade/elemento/direcao
local ultimo = {}
Pedido.OnServerEvent:Connect(function(plr, m, acao, arg, dir)
	if typeof(m) ~= "Instance" or not N.registro[m] then return end
	if m:GetAttribute("DonoUserId") ~= plr.UserId then return end
	if os.clock() - (ultimo[plr] or 0) < Cfg.pedidoIntervaloMin then return end
	ultimo[plr] = os.clock()
	local c = N.registro[m]
	if acao == "elemento" and typeof(arg) == "string" then c:trocarElemento(arg); return end
	if acao == "usar" and typeof(arg) == "string" and (Cfg.habilidades[arg] or Cfg.basicos[arg]) then
		c:usar(arg, {direcao = typeof(dir) == "Vector3" and dir or nil})
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
