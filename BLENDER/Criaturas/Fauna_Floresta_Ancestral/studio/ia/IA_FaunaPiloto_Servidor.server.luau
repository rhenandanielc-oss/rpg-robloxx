-- IA_FaunaPiloto_Servidor (17/11/2026) - liga a IA da fauna no PILOTO do mapa real (Workspace.Fauna_Floresta_Piloto).
-- Usa os mesmos modulos da cena de teste (Controlador/Movimento/Anim/Percepcao/Sons/Config) com os dados da cena escolhida
-- no atributo Cena da pasta IA ("CenaLagoa" = habitats aprovados da Lagoa_5 com a rotina de Vivencia; "CenaFloresta" =
-- clareira perto da Vila, sem vivencia). Um controlador por animal. Desligar: atributo Ativo=false na pasta IA (ou apagar a
-- pasta Fauna_Floresta_Piloto: o resto do mapa so muda nas 3 margens rasas da Lagoa_5, que tem backup de voxels).
local pastaIA = script.Parent
local raiz = pastaIA.Parent
if pastaIA:GetAttribute("Ativo") == false then return end
local nomeCena = pastaIA:GetAttribute("Cena") or "CenaFloresta"
local Cena = require(pastaIA:WaitForChild(nomeCena))
local K = require(pastaIA:WaitForChild("Controlador"))
local okV, Vivencia = pcall(require, pastaIA:WaitForChild("Vivencia", 5))
if not okV then Vivencia = nil end
local animais = raiz:WaitForChild("Animais")
local marcadores = raiz:FindFirstChild("Marcadores_Vivencia") or raiz

local poleiros = {}
for nome, p in pairs(Cena.poleiros) do
	local arv = Cena.arvore(p)
	if arv then poleiros[nome] = { topo = p.topo, inst = arv, seguro = p.seguro }
	else warn("[FaunaPiloto] arvore do poleiro " .. nome .. " nao encontrada") end
end

-- so os animais desta cena ficam ativos (os outros saem do mapa ao iniciar o Play)
local usados = {}
for _, a in ipairs(Cena.animais) do usados[a.nome] = true end
for _, m in ipairs(animais:GetChildren()) do if not usados[m.Name] then m.Parent = nil end end

local escalas = {}
local controladores = {}
for _, a in ipairs(Cena.animais) do
	local m = animais:FindFirstChild(a.nome)
	if m then
		escalas[a.especie] = m:GetScale()
		local opts = { area = Cena.area }
		if a.especie == "Coruja" then
			local P = Cena.poleiros[a.poleiro]
			m:PivotTo(CFrame.lookAt(P.topo, P.topo + P.dir))
			opts.casa = m:GetPivot(); opts.poleiros = poleiros; opts.rotas = Cena.rotas or {}; opts.poleiro = a.poleiro
		else
			opts.casa = Cena.casa(a)
			m:PivotTo(opts.casa)
		end
		local ok, c = pcall(K.novo, m, a.especie, opts)
		if ok then controladores[a.nome] = c
			if Cena.rota then c.rotaFn = Cena.rota end
		else warn("[FaunaPiloto] falha ao iniciar " .. a.nome .. ": " .. tostring(c)) end
	else warn("[FaunaPiloto] modelo ausente: " .. a.nome) end
end
-- vizinhos: os outros animais nao bloqueiam o corpo, o passo se afasta deles (Movimento.vizinhos)
for nome, c in pairs(controladores) do
	for outro, c2 in pairs(controladores) do if outro ~= nome then table.insert(c.mov.vizinhos, c2.m) end end
end
-- vivencia (so na cena que a define)
if Vivencia and Cena.preparar then
	Cena.preparar(marcadores, escalas)
	for _, c in pairs(controladores) do c.viv = Vivencia.novo(c, Cena) end
end
for _, c in pairs(controladores) do c:iniciar() end
pastaIA:SetAttribute("Pronto", true)
pastaIA:SetAttribute("Controladores", #Cena.animais)
