-- IA_FaunaFloresta_Servidor (Script em Workspace.Teste_FaunaFloresta.IA_FaunaFloresta) - PILOTO, so na cena isolada.
-- Liga a IA nos 3 modelos de teste. Desligar: atributo Ativo=false na pasta IA_FaunaFloresta (ou apagar a pasta inteira).
local pastaIA = script.Parent
local area = pastaIA.Parent
if pastaIA:GetAttribute("Ativo") == false then return end
local Cena = require(pastaIA:WaitForChild("Cena"))
local K = require(pastaIA:WaitForChild("Controlador"))

local cena = area:FindFirstChild("Cena_IA") or Cena.construir(area)
local poleiros = {}
for nome, p in pairs(Cena.poleiros) do
	poleiros[nome] = { topo = Cena.topo(nome), inst = cena:WaitForChild("Poleiro_" .. nome), seguro = p.seguro }
end

local F = {}
F.controladores = {}

function F.iniciar()
	for _, c in pairs(F.controladores) do c:parar() end
	F.controladores = {}
	Cena.posicionar(area)
	for _, esp in ipairs({ "Cervo", "Javali", "Coruja" }) do
		local m = area:FindFirstChild(esp .. "_Teste")
		if m and pastaIA:GetAttribute("So") ~= nil and pastaIA:GetAttribute("So") ~= esp then m = nil end
		if m then
			local casa = Cena.casas[esp] and CFrame.lookAt(Cena.casas[esp].pos, Cena.casas[esp].pos + Cena.casas[esp].dir) or m:GetPivot()
			local c = K.novo(m, esp, { area = Cena.area, casa = casa, poleiros = esp == "Coruja" and poleiros or nil,
				rotas = esp == "Coruja" and Cena.rotas or nil, poleiro = Cena.corujaInicio })
			c:iniciar()
			F.controladores[esp] = c
		end
	end
end

_G.FaunaIA = F      -- so para o roteiro de teste/depuracao
F.iniciar()
-- roteiros de teste (DEBUG): o depurador escreve o nome no atributo Comando; o resultado vira JSON em Resultado_<nome>
local HS = game:GetService("HttpService")
pastaIA:GetAttributeChangedSignal("Comando"):Connect(function()
	local nome = pastaIA:GetAttribute("Comando"); if not nome or nome == "" then return end
	pastaIA:SetAttribute("Comando", "")
	task.spawn(function()
		local res = require(pastaIA:WaitForChild("Roteiro")).rodar(nome)
		local sv = pastaIA:FindFirstChild("Resultado_" .. nome) or Instance.new("StringValue")
		sv.Name = "Resultado_" .. nome; sv.Value = HS:JSONEncode(res); sv.Parent = pastaIA
	end)
end)
pastaIA:SetAttribute("Pronto", true)
