-- IA_FaunaFloresta/Roteiro - roteiros de TESTE reproduziveis (so DEBUG). Alvos falsos (tag AlvoFaunaTeste) andam por
-- trajetos fixos; um amostrador grava estado/posicao dos animais a 10 Hz. Uso em Play (servidor):
--   task.spawn(require(pasta.Roteiro).rodar, "cervo_aprox")  ->  resultado em _G.FaunaIA.resultados[nome]
local RunService = game:GetService("RunService")
local CS = game:GetService("CollectionService")
local Config = require(script.Parent:WaitForChild("Config"))
local Cena = require(script.Parent:WaitForChild("Cena"))

local R = {}
local Y = Cena.Y
local function V(x, z) return Vector3.new(x, Y, z) end
local temp = {}

local function alvo(nome, p, cor)
	local m = Instance.new("Model"); m.Name = nome
	local h = Instance.new("Part"); h.Name = "HumanoidRootPart"; h.Anchored = true; h.CanCollide = true   -- 17/11: solido como o corpo de um jogador (o animal desvia, nao atravessa)
	h.Size = Vector3.new(2, 5, 1); h.Color = cor or Color3.fromRGB(220, 60, 60); h.Material = Enum.Material.Neon
	h.CFrame = CFrame.new(p + Vector3.new(0, 2.5, 0)); h.Parent = m; m.PrimaryPart = h
	CS:AddTag(m, Config.TAG_ALVO_TESTE); m.Parent = workspace.Teste_FaunaFloresta; table.insert(temp, m)
	return m
end
local function andar(m, destino, vel)
	local h = m.PrimaryPart
	while m.Parent do
		local dt = RunService.Heartbeat:Wait()
		local p = h.Position - Vector3.new(0, 2.5, 0); local d = Vector3.new(destino.X - p.X, 0, destino.Z - p.Z)
		if d.Magnitude < 0.2 then break end
		local np = p + d.Unit * math.min(d.Magnitude, vel * dt)
		h.CFrame = CFrame.lookAt(np + Vector3.new(0, 2.5, 0), np + Vector3.new(0, 2.5, 0) + d.Unit)
	end
end
local function bloco(nome, centro, tam)
	local b = Instance.new("Part"); b.Name = nome; b.Anchored = true; b.Size = tam; b.CFrame = CFrame.new(centro + Vector3.new(0, tam.Y / 2, 0))
	b.Material = Enum.Material.Slate; b.Color = Color3.fromRGB(120, 120, 125); b.Parent = workspace.Teste_FaunaFloresta; table.insert(temp, b)
	return b
end
local function limpar() for _, x in ipairs(temp) do if x.Parent then x:Destroy() end end; temp = {} end
local function esperarEstado(c, estados, tmax)
	local t0 = os.clock()
	while os.clock() - t0 < tmax do
		for _, e in ipairs(estados) do if c.estado == e then return true end end
		RunService.Heartbeat:Wait()
	end
	return false
end

R.cenarios = {}
local Sc = R.cenarios
-- CERVO (casa -50,330 olhando +X)
Sc.cervo_aprox = function(F) local c = F.controladores.Cervo; local a = alvo("Jogador1", V(15, 330))
	andar(a, V(-28, 330), 12); esperarEstado(c, { "Retorno" }, 20); a:Destroy(); esperarEstado(c, { "Repouso" }, 40) end
Sc.cervo_recua = function(F) local c = F.controladores.Cervo; local a = alvo("Jogador1", V(15, 330))
	andar(a, V(-16, 330), 12); task.wait(2.5); andar(a, V(40, 330), 12); esperarEstado(c, { "Repouso" }, 10); task.wait(1) end
Sc.cervo_obstaculo = function(F) local c = F.controladores.Cervo
	bloco("Muro_Teste", V(-68, 330), Vector3.new(3, 9, 70)); task.wait(0.5)
	local a = alvo("Jogador1", V(15, 330)); andar(a, V(-28, 330), 12)
	esperarEstado(c, { "Retorno" }, 20); a:Destroy(); esperarEstado(c, { "Repouso" }, 45) end
Sc.cervo_perda = function(F) local c = F.controladores.Cervo; local a = alvo("Jogador1", V(15, 330))
	andar(a, V(-28, 330), 12); esperarEstado(c, { "Fuga" }, 5); task.wait(1.0); a:Destroy(); esperarEstado(c, { "Repouso" }, 40) end
Sc.cervo_dois = function(F) local c = F.controladores.Cervo
	local a = alvo("Jogador1", V(15, 330)); local b = alvo("Jogador2", V(-50, 380), Color3.fromRGB(60, 120, 230))
	task.spawn(andar, b, V(-50, 362), 10); andar(a, V(-28, 330), 12)
	esperarEstado(c, { "Retorno" }, 20); a:Destroy(); b:Destroy(); esperarEstado(c, { "Repouso" }, 45) end
-- JAVALI (casa 30,345 olhando -X)
Sc.javali_aprox = function(F) local c = F.controladores.Javali; local a = alvo("Jogador1", V(-15, 345))
	andar(a, V(14, 345), 8); esperarEstado(c, { "Retorno" }, 15); andar(a, V(-40, 345), 14); a:Destroy(); esperarEstado(c, { "Repouso" }, 40) end
Sc.javali_recua = function(F) local c = F.controladores.Javali; local a = alvo("Jogador1", V(-15, 345))
	andar(a, V(10, 345), 8); esperarEstado(c, { "Ameaca" }, 8); andar(a, V(-25, 345), 14)
	esperarEstado(c, { "Repouso" }, 15); task.wait(1) end
Sc.javali_obstaculo = function(F) local c = F.controladores.Javali
	bloco("Tronco_Teste", V(22, 345), Vector3.new(2, 1.6, 7)); local a = alvo("Jogador1", V(-15, 345))
	andar(a, V(14, 345), 8); esperarEstado(c, { "Desiste", "Investida" }, 12); task.wait(1); a:Destroy(); esperarEstado(c, { "Repouso" }, 15) end
Sc.javali_dois = function(F) local c = F.controladores.Javali
	local a = alvo("Jogador1", V(-15, 345)); local b = alvo("Jogador2", V(30, 395), Color3.fromRGB(60, 120, 230))
	task.spawn(andar, b, V(30, 366), 8); andar(a, V(14, 345), 8)
	esperarEstado(c, { "Retorno" }, 15); a:Destroy(); b:Destroy(); esperarEstado(c, { "Repouso" }, 40) end
-- 17/11: alvo chega pelo lado (o javali olha -X): tem de virar ANDANDO em arco antes de ameacar/investir
Sc.javali_lado = function(F) local c = F.controladores.Javali; local a = alvo("Jogador1", V(30, 385))
	andar(a, V(30, 362), 8); esperarEstado(c, { "Retorno" }, 20); andar(a, V(30, 400), 14); a:Destroy(); esperarEstado(c, { "Repouso" }, 40) end
-- CORUJA (poleiro A 55,255 alto 10)
Sc.coruja_aprox = function(F) local c = F.controladores.Coruja; local a = alvo("Jogador1", V(100, 262))
	andar(a, V(64, 258), 10); esperarEstado(c, { "Pousada" }, 20); task.wait(0.3); a:Destroy(); task.wait(2) end
Sc.coruja_recua = function(F) local c = F.controladores.Coruja; local a = alvo("Jogador1", V(100, 262))
	andar(a, V(78, 262), 10); task.wait(2.5); andar(a, V(110, 262), 12); esperarEstado(c, { "Pousada" }, 8); a:Destroy(); task.wait(1) end
Sc.coruja_bloqueio = function(F) local c = F.controladores.Coruja
	local b = Cena.topo("B"); bloco("Galho_Teste", b + Vector3.new(0, 1.2, 0), Vector3.new(4, 1, 4))
	local a = alvo("Jogador1", V(100, 262)); andar(a, V(64, 258), 10)
	esperarEstado(c, { "Pousada" }, 25); a:Destroy(); task.wait(2) end
Sc.todos = function(F)
	local a = alvo("Jogador1", V(110, 300)); local b = alvo("Jogador2", V(-15, 395), Color3.fromRGB(60, 120, 230))
	task.spawn(function() andar(b, V(-40, 352), 10) end)
	andar(a, V(64, 262), 12); task.wait(1); andar(a, V(16, 330), 12); task.wait(5); a:Destroy(); b:Destroy()
	for _, c in pairs(F.controladores) do esperarEstado(c, { "Repouso", "Pousada" }, 40) end end

-- amostrador 10 Hz + execucao isolada (reinicia os animais nas posicoes iniciais antes de cada cenario)
function R.rodar(nome)
	local F = _G.FaunaIA; F.resultados = F.resultados or {}
	local so = ({ cervo = "Cervo", javali = "Javali", coruja = "Coruja" })[string.match(nome, "^(%a+)_") or ""]
	workspace.Teste_FaunaFloresta.IA_FaunaFloresta:SetAttribute("So", so)      -- cenario de uma especie: so ela ativa
	limpar(); F.iniciar(); task.wait(1.5)
	local amostras, t0, rodando = {}, os.clock(), true
	local quadros, inicioQ = 0, os.clock()
	local con = RunService.Heartbeat:Connect(function() quadros += 1 end)
	task.spawn(function()
		while rodando do
			for esp, c in pairs(F.controladores) do
				local p = c.m:GetPivot()
				local lv = p.LookVector     -- 17/11: + rumo (graus) para medir giro sem deslocamento
				table.insert(amostras, string.format("%.3f|%s|%s|%.2f|%.2f|%.2f|%.1f", os.clock() - t0, esp, c.estado, p.X, p.Y, p.Z,
					math.deg(math.atan2(-lv.X, -lv.Z))))
			end
			task.wait(0.1)
		end
	end)
	local ok, err = pcall(Sc[nome], F)
	rodando = false; con:Disconnect()
	local res = { ok = ok, erro = err and tostring(err), duracao = os.clock() - t0, fps = quadros / (os.clock() - inicioQ),
		amostras = amostras, logs = {}, leituras = {}, caminhos = {} }
	for esp, c in pairs(F.controladores) do
		res.logs[esp] = table.clone(c.log); res.leituras[esp] = c.perc.leituras; res.caminhos[esp] = c.mov.caminhos
		if c.ultimoPouso then res.pouso = c.ultimoPouso end
	end
	limpar()
	F.resultados[nome] = res
	workspace.Teste_FaunaFloresta.IA_FaunaFloresta:SetAttribute("UltimoRoteiro", nome .. (ok and " ok" or (" ERRO " .. tostring(err))))
	return res
end

return R
