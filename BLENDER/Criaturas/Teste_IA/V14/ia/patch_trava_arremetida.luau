-- patch_trava_arremetida.luau (Studio, Edit) — a Arremetida montada persegue o alvo travado (04/11).
-- Gerado por sombrio/gerar_patch_trava_arremetida.py; backup unico ServerStorage.Backup_Trava_Arremetida_2026-11-04.
assert(not game:GetService("RunService"):IsRunning(), "aplicar no Edit, fora do Play")
local SS = game:GetService("ServerStorage"); local S = game:GetService("StarterPlayer").StarterPlayerScripts.Montaria_Cliente
local src = S.Source:gsub("\r\n", "\n")
if src:find("PATCH_TRAVA_ARREMETIDA", 1, true) then return "ja aplicado" end
local a, b = [==[		if not (orbAtivo or stick or not UIS.MouseEnabled) then cy, cp = nil, 0 end
		Entrada:FireServer({f = -mv.Z, t = mv.X, ]==], [==[		if not (orbAtivo or stick or not UIS.MouseEnabled) then cy, cp = nil, 0 end
		local fAv = -mv.Z
		local tA = travaAtual()                                         -- PATCH_TRAVA_ARREMETIDA: a investida persegue o alvo travado
		if tA and m:GetAttribute("EmAtaque") == "Arremetida" then
			local v = tA.raiz.Position - m:GetPivot().Position
			if v.Magnitude > 2 then v = v.Unit; cy = math.atan2(v.X, v.Z); cp = math.asin(math.clamp(v.Y, -1, 1)); fAv = math.max(fAv, 0.3) end
		end
		Entrada:FireServer({f = fAv, t = mv.X, ]==]
local i, j = string.find(src, a, 1, true); assert(i and not string.find(src, a, j + 1, true), "ancora")
src = src:sub(1, i - 1) .. b .. src:sub(j + 1); assert(loadstring(src), "nao compila")
if not SS:FindFirstChild("Backup_Trava_Arremetida_2026-11-04") then local f = Instance.new("Folder"); f.Name = "Backup_Trava_Arremetida_2026-11-04"; S:Clone().Parent = f; f.Parent = SS end
S.Source = src
return "aplicado: Montaria_Cliente (" .. #src .. " bytes)"
