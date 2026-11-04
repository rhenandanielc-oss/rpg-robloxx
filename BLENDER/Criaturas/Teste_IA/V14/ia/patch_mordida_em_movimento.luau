-- patch_mordida_em_movimento.luau (Studio, modo Edit) — usuario 03/11 (Dragao Sombrio): "quando a mordida e usada em
-- movimento, o andar fica parado, as pernas nao se movem". Causa (mesma do sopro em 02/11):
--  * a montaria trata "Mordida" como ataque FIXO (velocidade-alvo 0 e nao toca Andar/Correr durante o ataque);
--  * o Nucleo toca o Ataque_Mordida do CORPO INTEIRO (patas incluidas, prioridade Action) por cima da locomocao.
-- Correcao, OPCIONAL POR MODELO (atributo MordidaEmMovimento = true; so o workspace.Sombrio recebe agora -- os outros
-- dragoes ficam exatamente como estao ate o chat de cada um decidir):
--  1) clipe Sombrio_Ataque_Mordida_Sup: copia com Pose.Weight = 0 fora de pescoco/cabeca/mandibula/focinho (igual aos
--     _Sup do sopro);
--  2) Nucleo._Mordida: com o atributo e Velocidade > 3 no chao, toca o _Sup (as patas seguem o Andar/Correr);
--  3) montaria: com o atributo, a Mordida deixa de ser ataque fixo no chao (segue andando e trocando Andar/Correr).
-- Backup unico: ServerStorage.Backup_Mordida_Movimento_2026-11-03. Reversivel: tirar o atributo (volta ao comportamento
-- antigo) ou restaurar o backup.
local RS, SS, SSS = game:GetService("ReplicatedStorage"), game:GetService("ServerStorage"), game:GetService("ServerScriptService")
local SUP = {Pescoco2 = true, spine_3 = true, Pescoco4 = true, Cabeca = true, Mandibula = true, mouth_upper = true, mouth_upper_tip = true, mouth_lower_tip = true}
local pasta = RS.Animacoes_Sombrio
local k = pasta:FindFirstChild("Sombrio_Ataque_Mordida"); assert(k, "Sombrio_Ataque_Mordida nao encontrado")
local velho = pasta:FindFirstChild("Sombrio_Ataque_Mordida_Sup"); if velho then velho:Destroy() end
local c = k:Clone(); c.Name = "Sombrio_Ataque_Mordida_Sup"
for _, p in ipairs(c:GetDescendants()) do if p:IsA("Pose") and not SUP[p.Name] then p.Weight = 0 end end
c:SetAttribute("Parcial", "pescoco/cabeca/mandibula (Pose.Weight 0 no resto)"); c.Parent = pasta
if workspace:FindFirstChild("Sombrio") then workspace.Sombrio:SetAttribute("MordidaEmMovimento", true) end

local alvos = {NU = SSS.Combate_Dragao.Nucleo, MS = SSS.Montaria_Dragao_Servidor}
if alvos.NU.Source:find("PATCH_MORDIDA_MOVIMENTO", 1, true) then return "clipe _Sup recriado | scripts ja aplicados" end
local novo = {}; for kk, s in pairs(alvos) do novo[kk] = s.Source:gsub("\r\n", "\n") end
local function troca(kk, a, b)
	local i, j = string.find(novo[kk], a, 1, true); assert(i, kk .. ": trecho nao encontrado: " .. a:sub(1, 70))
	assert(not string.find(novo[kk], a, j + 1, true), kk .. ": trecho repetido: " .. a:sub(1, 70))
	novo[kk] = novo[kk]:sub(1, i - 1) .. b .. novo[kk]:sub(j + 1)
end
troca("NU", [=[	local t = self:tocar("Ataque_Mordida", noAr, {Impacto = 0.74}, function(n)]=],
	[=[	-- PATCH_MORDIDA_MOVIMENTO (03/11): andando no chao (modelos com MordidaEmMovimento), so pescoco/cabeca/mandibula (_Sup)
	local mov = not noAr and self.m:GetAttribute("MordidaEmMovimento") and (self.m:GetAttribute("Velocidade") or 0) > 3
	local nomeM = (mov and self:clipe("Ataque_Mordida_Sup", false)) and "Ataque_Mordida_Sup" or "Ataque_Mordida"
	local t = self:tocar(nomeM, noAr, {Impacto = 0.74}, function(n)]=])
troca("MS", [=[	local fixo = ataque == "Ruptura" or ataque == "Coracao" or ataque == "Tempestade" or ataque == "Garra" or ataque == "Mordida" or ataque == "Cauda"]=],
	[=[	local fixo = ataque == "Ruptura" or ataque == "Coracao" or ataque == "Tempestade" or ataque == "Garra" or ataque == "Cauda"
		or (ataque == "Mordida" and not m:GetAttribute("MordidaEmMovimento"))   -- PATCH_MORDIDA_MOVIMENTO (03/11)]=])
for kk, s in pairs(novo) do assert(loadstring(s), kk .. " nao compila depois do patch") end
if not SS:FindFirstChild("Backup_Mordida_Movimento_2026-11-03") then
	local f = Instance.new("Folder"); f.Name = "Backup_Mordida_Movimento_2026-11-03"
	alvos.NU:Clone().Parent = f; alvos.MS:Clone().Parent = f; f.Parent = SS
end
alvos.NU.Source = novo.NU; alvos.MS.Source = novo.MS
return "aplicado: clipe Sombrio_Ataque_Mordida_Sup + Nucleo + montaria; backup ServerStorage.Backup_Mordida_Movimento_2026-11-03"
