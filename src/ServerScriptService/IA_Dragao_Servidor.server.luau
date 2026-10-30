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
	m.AncestryChanged:Connect(function(_, p) if not p then _G.IA_DRAGOES[m] = nil end end)     -- limpeza ao remover
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
-- DEPURACAO VISUAL (so desenvolvimento): Workspace atributo IA_DebugVisual = true mostra, SO a jogadores autorizados
-- (Studio, criador do jogo ou atributo Dev = true no Player), um painel sobre cada guardiao: estado/tarefa, alvo,
-- destino, distancia do ninho, ultima posicao do alvo, energia, habilidade escolhida, motivo de bloqueio, necessidades.
-- O painel vai no PlayerGui do autorizado (os outros jogadores nao recebem nada).
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local function autorizado(p) return RunService:IsStudio() or p.UserId == game.CreatorId or p:GetAttribute("Dev") == true end
local function v3(v) return v and ("%.0f, %.0f, %.0f"):format(v.X, v.Y, v.Z) or "-" end
task.spawn(function()
	while true do
		task.wait(0.5)
		local ligado = workspace:GetAttribute("IA_DebugVisual") == true
		for _, p in ipairs(Players:GetPlayers()) do
			local pg = p:FindFirstChildOfClass("PlayerGui")
			if not pg then continue end
			for _, bb in ipairs(pg:GetChildren()) do
				if bb.Name:sub(1, 9) == "IA_Debug_" and not (ligado and autorizado(p)) then bb:Destroy() end
			end
			if not (ligado and autorizado(p)) then continue end
			for m, c in pairs(_G.IA_DRAGOES) do
				if not (m.Parent and m.PrimaryPart) then continue end
				local nome = "IA_Debug_" .. m.Name
				local bb = pg:FindFirstChild(nome)
				if not bb then
					bb = Instance.new("BillboardGui"); bb.Name = nome; bb.Size = UDim2.fromOffset(360, 160); bb.StudsOffset = Vector3.new(0, 32, 0)
					bb.AlwaysOnTop = true; bb.ResetOnSpawn = false; bb.MaxDistance = 2000
					local t = Instance.new("TextLabel"); t.Name = "T"; t.Size = UDim2.fromScale(1, 1); t.BackgroundTransparency = 0.35
					t.BackgroundColor3 = Color3.new(0, 0, 0); t.TextColor3 = Color3.new(1, 1, 0.75); t.TextSize = 13; t.Font = Enum.Font.Code
					t.TextXAlignment = Enum.TextXAlignment.Left; t.TextYAlignment = Enum.TextYAlignment.Top; t.Parent = bb
					bb.Parent = pg
				end
				bb.Adornee = m.PrimaryPart
				local alvo, a = c:maiorAmeaca()
				local pos = c.L:pos()
				bb.T.Text = ("estado   %s  (tarefa %s)\nalvo     %s  nivel %s  %s\ndestino  %s\nninho    %.0f studs | no ar %s\nult.pos  %s\nenergia  %s | habilidade %s\nbloqueio %s\nfome %.2f sede %.2f sono %.2f%s"):format(
					tostring(c.estado), c.tarefa and c.tarefa.nome or "-", alvo and alvo.Name or "-", a and tostring(a.nivel) or "-",
					a and tostring(a.motivo or "") or "", v3(c.destino),
					(Vector3.new(pos.X, 0, pos.Z) - Vector3.new(c.casa.X, 0, c.casa.Z)).Magnitude, tostring(c.L.noAr),
					v3(a and a.ultimaPos), tostring(m:GetAttribute("Energia") or "-"), tostring(m:GetAttribute("IA_Habilidade") or "-"),
					tostring(m:GetAttribute("IA_Bloqueio") or "-"), c.fome, c.sede, c.sono, c.dormente and "\nLOD: dormente (sem jogador perto)" or "")
			end
		end
	end
end)
task.wait(1)
for _, m in ipairs(workspace:GetChildren()) do ligar(m) end
workspace.ChildAdded:Connect(function(m) task.defer(ligar, m) end)
