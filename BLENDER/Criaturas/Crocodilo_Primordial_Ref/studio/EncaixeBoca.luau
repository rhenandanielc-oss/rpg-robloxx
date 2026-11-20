-- EncaixeBoca (ModuleScript em ServerStorage.Crocodilo_Piloto) - 20/11 [PROPOSTA], encaixe REAL da presa na boca.
-- Pedido do usuario: "agarre o alvo na boca, simetricamente na boca, o corpo encaixe certinho; se nao couber, so morde".
-- * Referencial da boca (servidor, a cada uso): O = dobradica (osso Mandibula), F = frente do cranio (osso Cabeca +Y),
--   U = cima do cranio (osso Cabeca +Z = -LookVector), R = F x U. Plano mediano = plano F/U pelo centro (x lateral 0).
-- * Capacidade medida na malha (scripts/medir_boca.py -> boca_medidas.json; malha 1:1 com o Studio): folga interna entre
--   as arcadas (terco central, gengiva/palato) por profundidade d (ao longo de F, a partir da dobradica) e abertura alfa
--   (0 = fechada ... ALFA_MAX = 25,57 graus, a abertura maxima do rig). MEIO = altura do meio do vao (ao longo de U).
-- * Secao da presa medida com RAIOS na colisao da propria presa (partes/MeshPart), no ponto candidato: espessura ao longo
--   de U (o que fica entre as arcadas) e extensao ao longo de F (quanto o corpo entra para o fundo da boca). Candidatos =
--   pontos nos segmentos osso->pai da presa (sem olhos/raiz); sem ossos, pontos na caixa das partes.
-- * Cabe: espessura <= folga na abertura maxima em toda a faixa que o corpo ocupa (do fundo ate a ponta; a frente da boca
--   e aberta). Abertura de contato: menor alfa com folga >= espessura nessa faixa (as arcadas encostam no corpo).
-- * Nao cabe: so mordida (sem captura). Sem contato/alcance: erra.
-- Custo: ~4 raios por candidato, so no instante da decisao (nao por quadro); diagnostico visual so com Diagnostico=true.
local M = {}
M.ALFA_MAX = 25.57
M.CENTRO_LOCAL = Vector3.new(0.32, -0.57, -14.76)
M.CENTRO_LADO_E = Vector3.new(2.17, -1.04, -14.38); M.CENTRO_LADO_D = Vector3.new(-1.64, -1.46, -14.45)   -- poses SegurarLadoE/D (Play 20/11)   -- centro do vao aberto na pose SegurarPresa, no referencial do pivo (medido em Play 20/11)
M.PONTA_D = 5.739                       -- ponta do focinho a partir da dobradica
M.DS = {2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5}
M.ALFAS = {0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24}
M.FOLGA = {
	[0] = {-0.663, -0.548, -0.842, -0.457, -0.415, -0.882, -0.823},
	[2] = {-0.574, -0.448, -0.715, -0.325, -0.251, -0.701, -0.697},
	[4] = {-0.486, -0.347, -0.589, -0.193, -0.090, -0.520, -0.514},
	[6] = {-0.453, -0.247, -0.462, -0.060, 0.070, -0.338, -0.329},
	[8] = {-0.375, -0.146, -0.335, 0.072, 0.231, -0.155, -0.145},
	[10] = {-0.295, -0.045, -0.209, 0.204, 0.391, 0.027, 0.039},
	[12] = {-0.216, 0.056, -0.082, 0.336, 0.544, 0.209, 0.223},
	[14] = {-0.137, 0.156, 0.044, 0.468, 0.695, 0.390, 0.558},
	[16] = {-0.058, 0.256, 0.170, 0.713, 0.846, 0.571, 0.746},
	[18] = {0.021, 0.355, 0.296, 0.848, 0.996, 0.751, 0.930},
	[20] = {0.211, 0.454, 0.420, 0.981, 1.175, 0.929, 1.139},
	[22] = {0.293, 0.552, 0.544, 1.113, 1.334, 1.107, 1.329},
	[24] = {0.374, 0.649, 0.667, 1.317, 1.487, 1.282, 1.518},
}
M.MEIO = {
	[0] = {0.121, 0.091, 0.104, 0.122, 0.185, 0.258, 0.226},
	[4] = {0.032, -0.009, -0.023, -0.010, 0.023, 0.076, 0.072},
	[8] = {-0.024, -0.110, -0.150, -0.143, -0.138, -0.106, -0.113},
	[12] = {-0.103, -0.210, -0.276, -0.275, -0.294, -0.288, -0.297},
	[16] = {-0.182, -0.311, -0.403, -0.463, -0.445, -0.469, -0.558},
	[20] = {-0.316, -0.410, -0.528, -0.597, -0.610, -0.648, -0.755},
	[24] = {-0.398, -0.507, -0.651, -0.765, -0.766, -0.825, -0.944},
}
M.LARG = {2.052, 1.858, 1.921, 1.687, 1.632, 1.464, 0.922}
M.TOL = {contato = 1.0, altura = 1.2, lateral = 0.6}   -- studs: alcance do ponto ate a boca; desnivel vertical; desvio do plano mediano

local function interp(tab, alfa, d)                     -- bilinear na tabela (alfa em graus, d em studs)
	local as = {}; for a in pairs(tab) do table.insert(as, a) end; table.sort(as)
	alfa = math.clamp(alfa, as[1], as[#as]); d = math.clamp(d, M.DS[1], M.DS[#M.DS])
	local a0, a1 = as[1], as[#as]
	for i = 1, #as - 1 do if alfa >= as[i] and alfa <= as[i + 1] then a0, a1 = as[i], as[i + 1]; break end end
	local i0 = 1; for i = 1, #M.DS - 1 do if d >= M.DS[i] then i0 = i end end
	local i1 = math.min(i0 + 1, #M.DS); local u = (i1 == i0) and 0 or (d - M.DS[i0]) / (M.DS[i1] - M.DS[i0])
	local function linha(a) return tab[a][i0] + (tab[a][i1] - tab[a][i0]) * u end
	local v = (a1 == a0) and 0 or (alfa - a0) / (a1 - a0)
	return linha(a0) + (linha(a1) - linha(a0)) * v
end
function M.folga(alfa, d) return interp(M.FOLGA, alfa, d) end
function M.meio(alfa, d) return interp(M.MEIO, alfa, d) end

-- referencial da boca do crocodilo (mundo)
function M.boca(croc)
	local cab = croc:FindFirstChild("Cabeca", true); local mand = croc:FindFirstChild("Mandibula", true)
	local cf = cab.TransformedWorldCFrame
	local F = cf.UpVector; local U = -cf.LookVector; local R = F:Cross(U).Unit
	return {O = mand.TransformedWorldCFrame.Position, F = F, U = U, R = R}
end
function M.pontoBoca(b, d, alfa) return b.O + b.F * d + b.U * M.meio(alfa, d) end

-- secao da presa num ponto: espessura ao longo de U e extensao ao longo de F (raios so na presa)
local function raio(origem, dir, filtro)
	local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Include; rp.FilterDescendantsInstances = {filtro}
	return workspace:Raycast(origem, dir, rp)
end
function M.secao(presa, p, F, U)
	local cima = raio(p + U * 8, -U * 16, presa); local baixo = raio(p - U * 8, U * 16, presa)
	local frente = raio(p + F * 10, -F * 20, presa); local tras = raio(p - F * 10, F * 20, presa)
	if not (cima and baixo) then return nil end
	local tU = (cima.Position - baixo.Position):Dot(U)
	local tF = (frente and tras) and (frente.Position - tras.Position):Dot(F) or 0
	local centroU = (cima.Position + baixo.Position) / 2
	-- tras = superficie do lado da dobradica (o que entra primeiro); frente = a mais distante (pode ficar fora, pela ponta)
	local aTras = tras and math.max(0, (p - tras.Position):Dot(F)) or tF / 2
	local cFrente = frente and math.max(0, (frente.Position - p):Dot(F)) or tF / 2
	return {tU = math.max(0, tU), tF = math.max(0, tF), aTras = aTras, cFrente = cFrente, cima = cima.Position, baixo = baixo.Position, centro = centroU}
end

-- pontos candidatos de pegada na presa
local IGN = {"Olho", "Palpebra", "Raiz", "Root"}
local function ignora(n) for _, k in ipairs(IGN) do if n:find(k) then return true end end return false end
function M.candidatos(presa)
	local out = {}
	for _, b in ipairs(presa:GetDescendants()) do
		if b:IsA("Bone") and b.Parent:IsA("Bone") and not ignora(b.Name) and not ignora(b.Parent.Name) then
			local a, c = b.Parent.TransformedWorldCFrame.Position, b.TransformedWorldCFrame.Position
			for _, u in ipairs({0.25, 0.5, 0.75}) do table.insert(out, {p = a:Lerp(c, u), nome = b.Parent.Name .. ">" .. b.Name}) end
		end
	end
	if #out == 0 then
		for _, pt in ipairs(presa:GetDescendants()) do
			if pt:IsA("BasePart") and pt.Transparency < 1 then
				local cf, s = pt.CFrame, pt.Size; local ax = (s.X >= s.Y and s.X >= s.Z) and cf.RightVector * s.X or ((s.Y >= s.Z) and cf.UpVector * s.Y or cf.LookVector * s.Z)
				for _, u in ipairs({-0.35, 0, 0.35}) do table.insert(out, {p = cf.Position + ax * u, nome = pt.Name}) end
			end
		end
	end
	return out
end

-- avalia uma pegada no ponto p com o referencial b (F, U do cranio): cabe? em que profundidade e abertura?
-- crava (20/11 r2, usuario "enfincar mais os dentes"): as arcadas fecham `crava` studs ALEM da espessura (dentes dentro do
-- corpo, simetrico: o corpo fica no centro do vao). res.alfaContato = abertura em que as arcadas so encostam.
function M.avaliar(presa, p, b, crava)
	local s = M.secao(presa, p, b.F, b.U)
	if not s then return {cabe = false, motivo = "sem secao (raio nao achou o corpo)"} end
	-- faixa util: do fundo minimo dMin (folga >= espessura daqui ate a ponta, na abertura maxima) ate a ponta
	local dMin = nil
	for d = 5.5, 2.5, -0.1 do if M.folga(M.ALFA_MAX - 1.5, d) >= s.tU then dMin = d else break end end
	local res = {tU = s.tU, tF = s.tF, secao = s}
	if not dMin then res.cabe = false; res.motivo = string.format("espessura %.2f > folga maxima %.2f", s.tU, M.folga(M.ALFA_MAX - 1.5, 5.5)); return res end
	-- o corpo ocupa [dPega - aTras, dPega + cFrente]: o lado da dobradica precisa ficar na faixa util; a frente pode sair pela ponta
	local dPega = math.min(5.3, dMin + s.aTras + 0.05)
	if dPega - s.aTras < dMin - 0.05 then res.cabe = false; res.motivo = string.format("parte de tras %.2f nao entra: faixa util %.2f-%.2f", s.aTras, dMin, M.PONTA_D); return res end
	res.d0, res.d1 = math.max(2.5, dPega - s.aTras), math.min(5.5, dPega + s.cFrente)
	-- abertura de contato: menor alfa com folga >= espessura em toda a faixa ocupada (arcadas encostam)
	local function alfaPara(t)
		for a = 0, M.ALFA_MAX, 0.25 do
			local ok = true
			for d = res.d0, res.d1, 0.1 do if M.folga(a, d) < t then ok = false; break end end
			if ok then return a end
		end
		return M.ALFA_MAX
	end
	local alfaC = alfaPara(s.tU)
	local alfa = (crava and crava > 0) and alfaPara(math.max(0, s.tU - crava)) or alfaC
	res.cabe = true; res.dPega = dPega; res.alfa = alfa; res.w = alfa / M.ALFA_MAX; res.dMin = dMin; res.alfaContato = alfaC; res.crava = crava or 0
	res.motivo = string.format("cabe: espessura %.2f, extensao %.2f, faixa %.2f-%.2f, pega em d=%.2f, abertura %.1f graus (contato %.1f, crava %.2f)", s.tU, s.tF, dMin, M.PONTA_D, dPega, alfa, alfaC, crava or 0)
	return res
end

-- escolhe a regiao de pegada: mais perto da boca entre as que cabem; se nenhuma cabe, a mais perto (so mordida)
function M.escolher(croc, presa, alcanceMax, preferir, bRef, yLado)
	local b = bRef or M.boca(croc)
	local pv = croc:GetPivot()
	local ref = pv * M.CENTRO_LOCAL                        -- fixo no corpo: a cabeca virada do bote nao muda a escolha
	local refL = {pv * M.CENTRO_LADO_E, pv * M.CENTRO_LADO_D}
	local melhor, melhorNao
	local function pref(nome) if not preferir then return false end for _, k in ipairs(preferir) do if nome:find(k) then return true end end return false end
	for _, c in ipairs(M.candidatos(presa)) do
		local baixo = yLado and c.p.Y <= yLado                -- regiao baixa = MORDIDA DE LADO (cabeca girada: o vao fica na horizontal)
		local dist = baixo and math.min((c.p - refL[1]).Magnitude, (c.p - refL[2]).Magnitude) or (c.p - ref).Magnitude   -- 3D ate o centro do vao na pose
		if dist <= (alcanceMax or 40) then
			local yaw = (c.p - b.O) * Vector3.new(1, 0, 1); yaw = yaw.Magnitude > 0.1 and yaw.Unit or b.F
			local bb = {O = b.O, F = (yaw + Vector3.new(0, b.F.Y, 0)).Unit, U = b.U, R = b.R}   -- boca virada para o ponto
			if baixo then bb.F = yaw; bb.U = Vector3.new(-yaw.Z, 0, yaw.X); bb.R = bb.F:Cross(bb.U) end
			local r = M.avaliar(presa, c.p, bb); r.p = c.p; r.nome = c.nome; r.dist = dist
			r.score = dist - (pref(c.nome) and 6 or 0)       -- regiao preferida (ex.: pescoco na finalizacao) ganha 6 studs
			if r.cabe then if not melhor or r.score < melhor.score then melhor = r end
			elseif not melhorNao or dist < melhorNao.dist then melhorNao = r end
		end
	end
	return melhor, melhorNao
end

-- diagnostico visual temporario (eixos da boca, limites e pegada); some sozinho
function M.desenhar(croc, alfa, pega, dur)
	local pasta = workspace:FindFirstChild("Diag_Boca") or Instance.new("Folder"); pasta.Name = "Diag_Boca"; pasta.Parent = workspace
	local b = M.boca(croc)
	local function linha(a, c, cor, esp)
		local p = Instance.new("Part"); p.Anchored = true; p.CanCollide = false; p.CanQuery = false; p.CanTouch = false; p.CastShadow = false
		p.Material = Enum.Material.Neon; p.Color = cor; p.Size = Vector3.new(esp or 0.06, esp or 0.06, (c - a).Magnitude)
		p.CFrame = CFrame.lookAt((a + c) / 2, c); p.Parent = pasta; game:GetService("Debris"):AddItem(p, dur or 3)
	end
	local base = M.pontoBoca(b, 2.5, alfa)
	linha(b.O, b.O + b.F * M.PONTA_D, Color3.new(1, 0.2, 0.2))                  -- F (vermelho): eixo da boca
	linha(b.O, b.O + b.U * 1.5, Color3.new(0.2, 1, 0.2))                         -- U (verde)
	linha(b.O, b.O + b.R * 1.5, Color3.new(0.3, 0.5, 1))                         -- R (azul): lateral
	for _, d in ipairs({2.5, 3.5, 4.5, 5.5}) do                                   -- limites do vao (folga) na abertura atual
		local c = M.pontoBoca(b, d, alfa); local h = math.max(0, M.folga(alfa, d)) / 2
		linha(c - b.U * h, c + b.U * h, Color3.new(1, 1, 0.3), 0.04)
	end
	if pega then local s = Instance.new("Part"); s.Shape = Enum.PartType.Ball; s.Anchored = true; s.CanCollide = false; s.CanQuery = false
		s.Material = Enum.Material.Neon; s.Color = Color3.new(1, 0.4, 1); s.Size = Vector3.new(0.35, 0.35, 0.35); s.Position = pega; s.Parent = pasta
		game:GetService("Debris"):AddItem(s, dur or 3) end
	return base
end
return M
