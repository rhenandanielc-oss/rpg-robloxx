-- IA_Dragao_Servidor (Script em ServerScriptService): liga a IA em todo modelo do Workspace com o atributo
-- "GuardiaoNinho" (nome do Model do ninho). POIs: pasta indicada pelo atributo "POIs" do ninho (ou irma "POIs").
-- Desligar: atributo "IA_Ativa" = false no modelo.
local SSS = game:GetService("ServerScriptService")
local Cerebro = require(SSS:WaitForChild("IA_Dragao"):WaitForChild("Cerebro"))
_G.IA_DRAGOES = _G.IA_DRAGOES or {}
local function ligar(m)
	if not (m:IsA("Model") and m:GetAttribute("GuardiaoNinho")) or _G.IA_DRAGOES[m] or m:GetAttribute("IA_Ativa") == false then return end
	local ninho = workspace:FindFirstChild(m:GetAttribute("GuardiaoNinho"), true)
	if not ninho then warn("IA_Dragao: ninho nao encontrado para " .. m.Name); return end
	local pois = ninho:FindFirstChild("POIs") or (ninho.Parent and ninho.Parent:FindFirstChild("POIs"))
	local ok, c = pcall(Cerebro.novo, m, ninho, pois)
	if ok then _G.IA_DRAGOES[m] = c else warn("IA_Dragao: " .. tostring(c)) end
end
-- depuracao (somente servidor; nao e acessivel ao cliente): log, necessidades e ameacas de cada guardiao
local dbg = game:GetService("ServerStorage"):FindFirstChild("IA_Debug") or Instance.new("BindableFunction")
dbg.Name = "IA_Debug"; dbg.Parent = game:GetService("ServerStorage")
dbg.OnInvoke = function(cmd, nome, valor)
	local c; for m, x in pairs(_G.IA_DRAGOES) do if m.Name == nome or not nome then c = x end end
	if not c then return "sem guardiao" end
	if cmd == "log" then return table.concat(c.log, "\n", math.max(1, #c.log - (valor or 40) + 1)) end
	if cmd == "set" then for k, v in pairs(valor) do c[k] = v end; return "ok" end
	if cmd == "iniciarColeta" then c.T.Alerta:Fire(valor.Character, "coleta"); return "ok" end   -- = segurar o prompt
	if cmd == "coletar" then return c.T:tentarColetar(valor) end                                   -- = concluir o prompt
	if cmd == "atribuirOutro" then local ok, e = pcall(function() c.T:atribuir("Guardiao_Intruso") end); return ok, tostring(e) end
	if cmd == "info" then
		local am = {}; for alvo, a in pairs(c.ameacas) do table.insert(am, ("%s n%d %s"):format(alvo.Name, a.nivel, tostring(a.motivo))) end
		return ("estado=%s tarefa=%s fome=%.2f sede=%.2f sono=%.2f noAr=%s ameacas=[%s]"):format(tostring(c.estado), c.tarefa and c.tarefa.nome or "-", c.fome, c.sede, c.sono, tostring(c.L.noAr), table.concat(am, "; "))
	end
end
task.wait(1)
for _, m in ipairs(workspace:GetChildren()) do ligar(m) end
workspace.ChildAdded:Connect(function(m) task.defer(ligar, m) end)
