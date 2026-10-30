-- patch_ia_corrida_tarefa.luau (Studio, modo Edit) — achado no teste de derrota (30/10): ao trocar de tarefa, o laco de
-- locomocao da tarefa ANTIGA ainda rodava 1 quadro depois do Heartbeat e tocava "Correr" por cima da animacao nova
-- (o guardiao derrotado ficava correndo parado). Agora todo laco de locomocao confere vivo() logo apos cada quadro.
-- + combate aereo: com o Sopro em recarga, chega mais perto (alcance de mordida aerea) em vez de so pairar longe.
local SSS, SS = game:GetService("ServerScriptService"), game:GetService("ServerStorage")
local L, C = SSS.IA_Dragao.Locomotor, SSS.IA_Dragao.Cerebro
if L.Source:find("PATCH_IA_CORRIDA_TAREFA", 1, true) then return "ja aplicado" end
local a = "local dt = RunService.Heartbeat:Wait()"
local srcL, n = L.Source:gsub(a:gsub("%p", "%%%0"), "local dt = RunService.Heartbeat:Wait(); if not vivo() then break end")
assert(n >= 5, "esperava >= 5 lacos, achou " .. n)
srcL = "-- PATCH_IA_CORRIDA_TAREFA: lacos conferem vivo() apos cada quadro\n" .. srcL
local srcC = C.Source
local ant = ", self.cfg.distCombateAr)"
local i, j = srcC:find(ant, 1, true); assert(i, "trecho do combate aereo nao encontrado")
assert(not srcC:find(ant, j + 1, true), "trecho repetido")
-- Sopro em recarga: aproxima ate o alcance da mordida aerea
srcC = srcC:sub(1, i - 1) .. ", ((self.m:GetAttribute(\"RecargaFim_Sopro\") or 0) > workspace:GetServerTimeNow()) and 20 or self.cfg.distCombateAr)" .. srcC:sub(j + 1)
assert(loadstring(srcL), "Locomotor nao compila"); assert(loadstring(srcC), "Cerebro nao compila")
if not SS:FindFirstChild("Backup_IA_CorridaTarefa") then
	local f = Instance.new("Folder"); f.Name = "Backup_IA_CorridaTarefa"; L:Clone().Parent = f; C:Clone().Parent = f; f.Parent = SS
end
L.Source = srcL; C.Source = srcC
return "aplicado (" .. n .. " lacos)"
