-- IA_FaunaFloresta/CenaLagoa (17/11/2026) - HABITATS APROVADOS (usuario 17/11) em volta da Lagoa_5 da Floresta Ancestral
-- (Proto_FlorestaAncestral.Locais_Extra.Lagoa_5, centro 1701,-259; 925 studs da Vila, ~280 da placa de trilha mais perto).
-- Pontos escolhidos por inspecao (raycast/medidas 17/11). Quantidades/tempos [A TESTAR].
--   Cervo : abrigo entre carvalhos e freixos a OESTE; 2 arbustos baixos (Sotobosque Arbusto_Largo_A_934 e _887) com folhagem
--           na altura da boca do Pastar (1,58 x escala); agua: margem rasa SUDOESTE (a185).
--   Javali: sub-bosque umido sob o Carvalho_C_382 ao SUL; farejar/fucar no solo entre raizes; agua: margem SUL (a92), longe
--           da rota do cervo (~50 studs).
--   Coruja: galho de vigia no Freixo_C_m283 (37 studs, corredor livre sobre a lagoa); poleiro abrigado no alto do
--           Carvalho_B_m264 (dentro da copa); seguro no Freixo_B_376; agua: margem NORDESTE (a345, lamina 0,5);
--           zona do roedor de TESTE no campo ao norte.
-- As 3 margens rasas foram criadas no terreno com aprovacao do usuario (17/11); backup dos voxels em
-- Fauna_Floresta_Piloto.Marcadores_Vivencia.Backup_Terreno (restauracao: ver LEIA-ME da IA).
local Config = require(script.Parent:WaitForChild("Config"))
local S = {}

S.lagoa = Vector3.new(1701, 37.5, -259)
S.area = { centro = Vector3.new(1690, 40, -255), tamanho = Vector3.new(220, 80, 230) }

local rpS = RaycastParams.new(); rpS.FilterType = Enum.RaycastFilterType.Include; rpS.FilterDescendantsInstances = { workspace.Terrain }
rpS.IgnoreWater = true
local rpW = RaycastParams.new(); rpW.FilterType = Enum.RaycastFilterType.Include; rpW.FilterDescendantsInstances = { workspace.Terrain }
function S.chao(p) local r = workspace:Raycast(Vector3.new(p.X, 250, p.Z), Vector3.new(0, -400, 0), rpS); return r and r.Position.Y or p.Y end
function S.agua(p) local r = workspace:Raycast(Vector3.new(p.X, 250, p.Z), Vector3.new(0, -400, 0), rpW); return r and r.Material == Enum.Material.Water and r.Position.Y or nil end
local function no(p) return Vector3.new(p.X, S.chao(p), p.Z) end
local function u(x, z) return Vector3.new(x, 0, z).Unit end

S.animais = {
	{ nome = "Cervo_1", especie = "Cervo", casa = Vector3.new(1628, 0, -275), dir = u(1, 0.2) },
	{ nome = "Cervo_2", especie = "Cervo", casa = Vector3.new(1637, 0, -271), dir = u(1, 0.3) },   -- (17/11: 1624,-262 ficava a 6 do tronco e travava a saida)
	{ nome = "Javali_1", especie = "Javali", casa = Vector3.new(1673, 0, -186), dir = u(1, -0.3) },
	{ nome = "Coruja_1", especie = "Coruja", poleiro = "Vigia" },
}

-- poleiros da coruja (galhos medidos no tronco por raycast 17/11)
S.poleiros = {
	-- 19/11: a vigia antiga (Freixo_C_m283, 85,44) ficava dentro da copa e a coruja nao aparecia do chao; agora e o galho
	-- quebrado da arvore seca propria do piloto (BLENDER/Floresta/Arvore_Seca_Vigia), no campo aberto a leste da lagoa
	Vigia = { topo = Vector3.new(1720.65, 60.98, -282.41), arvore = { "@piloto", "Arvore_Seca_Vigia" }, dir = u(-1, 0.17) },
	Abrigo = { topo = Vector3.new(1719.0, 77.13, -319.4), arvore = { "Arvores_Medias", "Carvalho_B_m264" }, dir = u(0, 1) },
	Seguro = { topo = Vector3.new(1736.2, 84.83, -309.9), arvore = { "Arvores", "Freixo_B_376" }, dir = u(-0.5, 1), seguro = true },
}
S.coruja = { vigia = "Vigia", abrigo = "Abrigo" }
function S.arvore(P)
	if P.arvore[1] == "@piloto" then   -- 18/11: arvore propria do piloto (Fauna_Floresta_Piloto.Cenario_Vivencia)
		local f = workspace:FindFirstChild("Fauna_Floresta_Piloto"); f = f and f:FindFirstChild("Cenario_Vivencia")
		return f and f:FindFirstChild(P.arvore[2])
	end
	local f = workspace:FindFirstChild("Floresta_Blender"); f = f and f:FindFirstChild(P.arvore[1])
	return f and f:FindFirstChild(P.arvore[2])
end
function S.topo(n) return S.poleiros[n].topo end

-- rota aerea entre dois pontos: sai subindo, passa no meio e chega ~22 studs antes, 3,6 acima. Se a diferenca de altura
-- pede mais caminho que a reta (subida/descida limitadas do voo), desvia por cima da lagoa (lado aberto).
function S.rota(A, B)
	local d = Vector3.new(B.X - A.X, 0, B.Z - A.Z); local L = d.Magnitude; local un = L > 0.1 and d.Unit or Vector3.new(1, 0, 0)
	local V = Config.especies.Coruja.voo
	local dY = B.Y - A.Y
	local taxa = dY >= 0 and V.subida or V.descida
	local vel = Config.especies.Coruja.vClipe.Planar * 3
	local precisa = math.abs(dY) / taxa * vel * 1.15
	local pts = { A + un * math.min(8, L * 0.25) + Vector3.new(0, math.max(3, (V.folgaChao or 4) + 0.6), 0) }   -- partindo do chao: acima da folga
	if precisa > L * 1.05 then
		local meio = (A + B) / 2
		local perp = Vector3.new(-un.Z, 0, un.X)
		if perp:Dot(S.lagoa - meio) < 0 then perp = -perp end
		local h = math.sqrt(math.max(0, (precisa / 2) ^ 2 - (L / 2) ^ 2))
		local w = Vector3.new(meio.X, (A.Y + B.Y) / 2 + 4, meio.Z) + perp * math.min(h, 45)
		table.insert(pts, w)
	else
		table.insert(pts, Vector3.new((A.X + B.X) / 2, math.max(A.Y, B.Y) + 4, (A.Z + B.Z) / 2))
	end
	-- ultimo ponto longe o bastante do alvo para alinhar antes do pouso/mergulho (o perfil do mergulho anda ~11 studs)
	table.insert(pts, B - un * math.clamp(L * 0.6, 14, 24) + Vector3.new(0, math.max(3.6, (V.folgaChao or 4) + 0.6), 0))   -- alvo no chao: acima da folga
	-- nenhum ponto da rota abaixo da folga de voo sobre o chao embaixo dele (barrancos altos perto da margem)
	local folga = (V.folgaChao or 4) + 0.6
	for i, p in ipairs(pts) do local yc = S.chao(p); if p.Y < yc + folga then pts[i] = Vector3.new(p.X, yc + folga, p.Z) end end
	return pts
end

-- ponto de acao: pivo onde o animal fica PARADO na acao (pos), direcao (dir), tipo de contato e dados do alvo
-- (agua: o pivo e procurado ao longo do eixo ate a boca/bico ficar na lamina; folhas: ate a boca entrar na folhagem)
local function pontoFolhas(id, arbusto, dirChegada, especie, esc)
	local cf, sz = arbusto:GetBoundingBox()
	local b = Config.especies[especie].boca.Pastar * (esc / Config.escRef)
	local dir = Vector3.new(dirChegada.X, 0, dirChegada.Z).Unit
	-- boca na borda da folhagem (25% para dentro), na altura da boca do clipe
	local raioDir = math.abs(dir.X) * sz.X / 2 + math.abs(dir.Z) * sz.Z / 2
	local alvoBoca = Vector3.new(cf.X, 0, cf.Z) - dir * raioDir * 0.6
	local piv = alvoBoca + dir * b.Z     -- b.Z e negativo (frente): pivo atras da boca
	piv = no(piv)
	return { id = id, tipo = "folhas", pos = piv, dir = dir, alvoInst = arbusto,
		folhas = { centro = cf.Position, meio = sz / 2 + Vector3.new(0.3, 0.2, 0.3) }, arbusto = arbusto:GetFullName() }
end
local function pontoAgua(id, base, dir, especie, esc, clipe)
	local cfg = Config.especies[especie]
	local fe = esc / Config.escRef
	local b = cfg.boca[clipe] * fe
	local h = (cfg.cascos or 0) * fe
	local melhor, nota = nil, math.huge
	for s = -3, 6, 0.1 do
		local p = base + dir * s
		local yF = S.chao(p + dir * h); local yT = S.chao(p - dir * h)
		local piv = Vector3.new(p.X, (yF + yT) / 2, p.Z)
		local pitch = h > 0 and math.atan2(yF - yT, 2 * h) or 0
		local cf = CFrame.lookAt(piv, piv + dir) * CFrame.Angles(pitch, 0, 0)
		local boca = (cf * CFrame.new(b)).Position
		local w = S.agua(boca)
		local wPe = S.agua(p + dir * h)
		if w and wPe and (wPe - yF) <= cfg.profMax * fe then
			local e = math.abs(boca.Y - (w - 0.06))
			if e < nota then melhor, nota = { pos = piv, erro = boca.Y - w, pitch = math.deg(pitch), prof = wPe - yF }, e end
		end
	end
	if not melhor then return nil end
	return { id = id, tipo = "agua", pos = melhor.pos, dir = dir, calc = melhor }
end

-- monta os pontos (chamado pelo servidor depois de posicionar/escalar os modelos)
function S.preparar(pastaMarcadores, escalas)
	S.pastaMarcadores = pastaMarcadores
	local F = workspace.Floresta_Blender
	local arbA = F.Sotobosque:FindFirstChild("Arbusto_Largo_A_934")
	local arbB = F.Sotobosque:FindFirstChild("Arbusto_Largo_A_885")   -- (17/11: _887 espremido na margem; s163 com degrau no leste)
	local eC, eJ, eO = escalas.Cervo or 3, escalas.Javali or 3, escalas.Coruja or 3
	local P = { Cervo = {}, Javali = {}, Coruja = {} }
	P.Cervo.arbusto = {}
	if arbA then table.insert(P.Cervo.arbusto, pontoFolhas("Cervo_ArbustoA", arbA, u(0.92, -0.38), "Cervo", eC)); P.Cervo.arbusto[#P.Cervo.arbusto].preDist = 10 end
	if arbB then table.insert(P.Cervo.arbusto, pontoFolhas("Cervo_ArbustoB", arbB, u(-1, 0), "Cervo", eC)) end   -- pelo LESTE: chao ~42,6, folhas 42,8-45,9
	-- margem rasa SUDOESTE (borda 1663.6,-262.3; eixo para dentro n; faixa t=-1,5)
	local nC = u(0.996, 0.087); local tC = Vector3.new(-nC.Z, 0, nC.X)
	P.Cervo.agua = { pontoAgua("Cervo_Agua", Vector3.new(1663.6, 0, -262.3) + tC * -1.5, nC, "Cervo", eC, "Beber") }
	-- o arbusto _887 fica colado a margem: o cervo passa roçando nele (as folhas nao barram o corpo na chegada)
	if P.Cervo.agua[1] then P.Cervo.agua[1].alvoInst = F.Sotobosque:FindFirstChild("Arbusto_Largo_A_887"); P.Cervo.agua[1].preDist = 9 end   -- (mais longe caia no tronco do Carvalho_A_339)
	P.Javali.farejar = { { id = "Javali_Farejar", tipo = "solo", pos = no(Vector3.new(1683, 0, -197)), dir = u(0.6, -0.8) } }
	P.Javali.fucar = { { id = "Javali_Fucar", tipo = "solo", pos = no(Vector3.new(1675, 0, -179)), dir = u(0, 1) } }   -- solo plano (42,0) sob a copa, a oeste do tronco
	local nJ = u(0.035, -0.999); local tJ = Vector3.new(-nJ.Z, 0, nJ.X)
	P.Javali.agua = { pontoAgua("Javali_Agua", Vector3.new(1699.7, 0, -222.5) + tJ * -3.5, nJ, "Javali", eJ, "Beber") }
	local nO = u(-0.966, 0.259); local tO = Vector3.new(-nO.Z, 0, nO.X)
	local pO = Vector3.new(1715.0, 0, -262.8) + nO * 4.5 + tO * 1
	P.Coruja.agua = { { id = "Coruja_Agua", tipo = "agua", pos = no(pO), dir = nO } }
	P.Coruja.presa = { { id = "Presa_Norte", pos = no(Vector3.new(1712, 0, -300)) }, { id = "Presa_Noroeste", pos = no(Vector3.new(1700, 0, -308)) } }
	S.pontos = P
	-- marcadores visiveis so para inspecao (invisiveis em jogo: Transparency 1, sem colisao/consulta)
	local mk = pastaMarcadores:FindFirstChild("Pontos") or Instance.new("Folder"); mk.Name = "Pontos"; mk.Parent = pastaMarcadores
	mk:ClearAllChildren()
	for esp, grupos in pairs(P) do for g, lista in pairs(grupos) do for _, p in ipairs(lista) do
		if p then
			local m = Instance.new("Part"); m.Name = p.id; m.Size = Vector3.new(1, 0.2, 1); m.Anchored = true; m.CanCollide = false
			m.CanQuery = false; m.CanTouch = false; m.Transparency = 1; m.CFrame = CFrame.lookAt(p.pos, p.pos + (p.dir or Vector3.new(0, 0, -1)))
			m:SetAttribute("Especie", esp); m:SetAttribute("Grupo", g)
			if p.calc then m:SetAttribute("ErroBocaAgua", p.calc.erro); m:SetAttribute("Profundidade", p.calc.prof); m:SetAttribute("Inclinacao", p.calc.pitch) end
			m.Parent = mk
		end
	end end end
	return P
end

function S.casa(a)
	local p = no(a.casa)
	return CFrame.lookAt(p, p + a.dir)
end

return S
