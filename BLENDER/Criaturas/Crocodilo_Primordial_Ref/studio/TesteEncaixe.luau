-- TesteEncaixe (ModuleScript em ServerStorage.Crocodilo_Piloto) - SO TESTE (20/11): presas de teste para o encaixe real da
-- presa na boca (agarrao e Mordida esmagadora). Cria bonecos simples (partes ancoradas + Humanoid, atributo BonecoTeste)
-- no referencial do crocodilo e roda um caso por chamada, devolvendo o log do PoderesTeste e as medidas da pegada.
local P = game.ServerStorage.Crocodilo_Piloto
local M = require(P.PoderesTeste)
local ARENA = workspace.Teste_Crocodilo.Arena
local croc = workspace.Teste_Crocodilo.Crocodilo_Primordial
local X = {}
X.BASE0 = croc:GetPivot()

function X.limpar() for _, c in ipairs(ARENA:GetChildren()) do if c:GetAttribute("PresaEncaixe") then c:Destroy() end end end

-- partes: {nome, Vector3 tamanho, x lateral, h altura do centro acima do chao, z a frente do pivo}; a primeira = HumanoidRootPart
function X.presa(nome, partes, cor, base)
	base = base or croc:GetPivot()
	local m = Instance.new("Model"); m.Name = nome
	for i, pt in ipairs(partes) do
		local p = Instance.new("Part"); p.Name = (i == 1) and "HumanoidRootPart" or pt[1]
		p.Size = pt[2]; p.CFrame = base * CFrame.new(pt[3], pt[4] - 2.87, -pt[5]) * (pt[6] or CFrame.identity)
		p.Anchored = true; p.CanCollide = false; p.Material = Enum.Material.SmoothPlastic
		p.Color = cor or Color3.fromRGB(150, 120, 90); p:SetAttribute("Regiao", pt[1]); p.Parent = m
	end
	m.PrimaryPart = m.HumanoidRootPart
	local h = Instance.new("Humanoid"); h.MaxHealth = 100; h.Health = 100; h.Parent = m
	m:SetAttribute("BonecoTeste", true); m:SetAttribute("Inimigo", true); m:SetAttribute("PresaEncaixe", true)
	m.Parent = ARENA
	return m
end

-- formas (x lateral, h altura, z frente); a boca normal aberta fica em x 0,3 h 2,3 z 14,8; de lado E em x 2,2 h 1,8 z 14,4
function X.filhote(dx, dz, alt, nome)           -- filhote de cervo em pe: tronco atravessado na frente da boca
	alt = alt or 1.0; dx = dx or 0.3; dz = dz or 14.8
	local hc = 2.3
	local t = {{"Tronco", Vector3.new(2.2, alt, 0.9), dx, hc, dz}}
	for _, o in ipairs({{-0.8, -0.3}, {-0.8, 0.3}, {0.8, -0.3}, {0.8, 0.3}}) do
		local topo = hc - alt / 2; table.insert(t, {"Perna", Vector3.new(0.22, topo, 0.22), dx + o[1], topo / 2, dz + o[2]})
	end
	table.insert(t, {"Pescoco", Vector3.new(0.4, 0.9, 0.4), dx + 1.25, hc + 0.5, dz})
	table.insert(t, {"Cabeca", Vector3.new(0.7, 0.45, 0.45), dx + 1.5, hc + 1.0, dz})
	return X.presa(nome or "Presa_Filhote", t, Color3.fromRGB(160, 120, 80))
end
function X.grandeFocinho()                       -- presa grande (corpo largo) com focinho estreito voltado para a boca
	return X.presa("Presa_GrandeFocinho", {
		{"Tronco", Vector3.new(3.0, 2.6, 4.2), 0.3, 2.6, 19.2},
		{"Pescoco", Vector3.new(1.4, 1.4, 1.2), 0.3, 2.6, 16.8},
		{"Cabeca", Vector3.new(0.9, 0.95, 1.6), 0.3, 2.3, 15.2},
		{"Perna", Vector3.new(0.5, 1.4, 0.5), -0.9, 0.7, 18.0}, {"Perna", Vector3.new(0.5, 1.4, 0.5), 1.5, 0.7, 18.0},
		{"Perna", Vector3.new(0.5, 1.4, 0.5), -0.9, 0.7, 20.6}, {"Perna", Vector3.new(0.5, 1.4, 0.5), 1.5, 0.7, 20.6},
	}, Color3.fromRGB(90, 70, 60))
end
function X.bufalo()                              -- grande demais: tronco largo de frente, sem parte estreita perto
	return X.presa("Presa_Bufalo", {{"Tronco", Vector3.new(4.0, 3.0, 3.0), 0.3, 2.4, 16.0}}, Color3.fromRGB(70, 60, 55))
end
function X.deitado(pesc, nome, base)              -- deitado de lado (caido), cabeca erguida: pescoco em pe ao lado da boca
	pesc = pesc or 0.9
	return X.presa(nome or "Presa_Deitada", {
		{"Tronco", Vector3.new(3.2, 1.5, 1.4), 2.4, 0.75, 17.2},
		{"Pescoco", Vector3.new(pesc, 1.8, pesc), 2.2, 1.6, 15.1},
		{"Cabeca", Vector3.new(0.8, 0.6, 1.3), 2.2, 2.75, 15.4},
	}, Color3.fromRGB(150, 110, 75), base)
end

local function copiaLog() local t = {} for i, s in ipairs(M.log) do t[i] = s end return t end
local function esperar(maxT)
	local t = 0
	repeat task.wait(0.2); t += 0.2 until (M.estado().poder == nil and t > 0.5) or t > maxT
	return t
end
local function resumo(r)
	if not r then return "sem pegada" end
	return string.format("modo=%s regiao=%s pose=%s tU=%s tF=%s alfa=%s d=%s lateral=%s altura=%s andou=%s | %s", tostring(r.modo), tostring(r.nome), tostring(r.pose),
		r.tU and string.format("%.2f", r.tU) or "-", r.tF and string.format("%.2f", r.tF) or "-", r.alfa and string.format("%.1f", r.alfa) or "-",
		r.dPega and string.format("%.2f", r.dPega) or "-", r.lateral and string.format("%.2f", r.lateral) or "-", r.altura and string.format("%.2f", r.altura) or "-",
		r.andou and string.format("%.2f", r.andou) or "-", tostring(r.motivo))
end
X.resumo = resumo

-- agarrao num alvo ja criado; devolve resumo + log
function X.agarrar(alvo, cena, maxT)
	M.ultimaPegada = nil
	local ok = M.agarrao(alvo, cena or "terra")
	local t = esperar(maxT or 9)
	return string.format("[%s] %s (%.1f s)\n%s\n%s", alvo.Name, tostring(ok), t, resumo(M.ultimaPegada), table.concat(copiaLog(), "\n"))
end
function X.finalizar(alvo, maxT)
	M.ultimaPegada = nil
	alvo:SetAttribute("Caido", true); alvo:SetAttribute("CaidoAte", workspace:GetServerTimeNow() + 30)
	local h = alvo:FindFirstChildOfClass("Humanoid"); h.Health = 30
	local ok = M.finalizar(alvo, true)
	local t = esperar(maxT or 9)
	return string.format("[%s] finalizar %s (%.1f s)\n%s\n%s", alvo.Name, tostring(ok), t, resumo(M.ultimaPegada), table.concat(copiaLog(), "\n"))
end
return X
