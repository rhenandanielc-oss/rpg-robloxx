-- IA_FaunaFloresta/CenaFloresta (17/11/2026) - PILOTO PEQUENO no MAPA REAL (pedido do usuario 17/11: "piloto pequeno,
-- perto da Vila Principal"). Clareira a leste da Vila: Exp_Clareiras.Clareira_Combate_13 (2464, ~20, 292), 100% aberta e
-- plana (amostrada por raycast 17/11), cercada por carvalhos de Arvores_Medias. Quantidades e locais sao [PROPOSTA]
-- (a regra oficial de reaparecimento/quantidade segue [PENDENTE]).
--   3 cervos na clareira, 2 javalis na borda do bosque (sub-bosque, oeste), 1 coruja em galhos REAIS de 3 carvalhos
--   (pontos medidos no tronco por raycast; A e B normais, C = seguro, o mais alto).
-- So dados: as alturas do chao sao lidas no terreno na hora (raycast), nada e construido no mapa.
local S = {}

local CENTRO = Vector3.new(2464, 20, 292)
S.area = { centro = CENTRO, tamanho = Vector3.new(200, 60, 220) }   -- caixa XZ onde a fauna pode andar/fugir

-- animais: nome, especie, casa (XZ) e direcao inicial
S.animais = {
	{ nome = "Cervo_1", especie = "Cervo", pos = Vector3.new(2470, 0, 284), dir = Vector3.new(1, 0, 0.3) },
	{ nome = "Cervo_2", especie = "Cervo", pos = Vector3.new(2482, 0, 300), dir = Vector3.new(-0.4, 0, 1) },
	{ nome = "Cervo_3", especie = "Cervo", pos = Vector3.new(2463, 0, 308), dir = Vector3.new(0.6, 0, -1) },
	{ nome = "Javali_1", especie = "Javali", pos = Vector3.new(2441, 0, 330), dir = Vector3.new(1, 0, -0.2) },
	{ nome = "Javali_2", especie = "Javali", pos = Vector3.new(2446, 0, 236), dir = Vector3.new(1, 0, 0.4) },
	{ nome = "Coruja_1", especie = "Coruja", poleiro = "A" },
}

-- poleiros: ponto do galho (superficie medida) + arvore (Model usado para ignorar colisao no pouso) + direcao ao pousar
local AM = "Arvores_Medias"
S.poleiros = {
	A = { topo = Vector3.new(2429.2, 37.75, 298.8), arvore = { AM, "Carvalho_A_m588" }, dir = Vector3.new(1, 0, 0) },
	B = { topo = Vector3.new(2436.4, 35.65, 258.3), arvore = { AM, "Carvalho_B_m598" }, dir = Vector3.new(1, 0, 0.3) },
	C = { topo = Vector3.new(2397.7, 44.55, 306.5), arvore = { AM, "Carvalho_C_m569" }, dir = Vector3.new(1, 0, 0), seguro = true },
}
S.corujaInicio = "A"
function S.topo(n) return S.poleiros[n].topo end

-- rotas aereas: sai do galho subindo, passa alto no meio e chega ~22 studs antes do destino, 3,6 acima (como na cena de teste)
local function rota(a, b)
	local A, B = S.poleiros[a].topo, S.poleiros[b].topo
	local d = Vector3.new(B.X - A.X, 0, B.Z - A.Z); local u = d.Unit; local L = d.Magnitude
	local alto = math.max(A.Y, B.Y)
	local p1 = A + u * math.min(8, L * 0.25) + Vector3.new(0, 4, 0)
	local p2 = A + u * (L * 0.5) + Vector3.new(0, alto - A.Y + 6, 0)
	local p3 = B - u * math.min(22, L * 0.45) + Vector3.new(0, 3.6, 0)
	return { p1, p2, p3 }
end
S.rotas = {}
for a in pairs(S.poleiros) do for b in pairs(S.poleiros) do if a ~= b then S.rotas[a .. "_" .. b] = rota(a, b) end end end

local rpT = RaycastParams.new(); rpT.FilterType = Enum.RaycastFilterType.Include; rpT.FilterDescendantsInstances = { workspace.Terrain }
function S.chao(p)
	local r = workspace:Raycast(Vector3.new(p.X, 400, p.Z), Vector3.new(0, -600, 0), rpT)
	return r and r.Position.Y or CENTRO.Y
end

function S.arvore(P)
	local f = workspace:FindFirstChild("Floresta_Blender"); f = f and f:FindFirstChild(P.arvore[1])
	return f and f:FindFirstChild(P.arvore[2])
end

-- CFrame da casa no chao real
function S.casa(a)
	local p = Vector3.new(a.pos.X, S.chao(a.pos), a.pos.Z)
	return CFrame.lookAt(p, p + Vector3.new(a.dir.X, 0, a.dir.Z))
end

return S
