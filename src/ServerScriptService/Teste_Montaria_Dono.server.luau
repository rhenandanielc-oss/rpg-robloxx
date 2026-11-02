-- Teste_Montaria_Dono (Script, ServerScriptService) — SOMENTE NO LUGAR DE TESTE. Simula o sistema de posse:
-- o primeiro jogador que entra vira dono do "Dragao_Montanhas_Jogador". No jogo real, DonoUserId/Estagio/
-- VooDesbloqueado vem do salvamento da criatura e da missao de voo (nao deste script).
local Players = game:GetService("Players")
local function dar(plr)
	for _, nome in ipairs({"Silverwing", "Dragao_Montanhas_Jogador", "Glacial"}) do
		local m = workspace:FindFirstChild(nome)
		if m and not m:GetAttribute("DonoUserId") then m:SetAttribute("DonoUserId", plr.UserId) end
	end
end
for _, p in ipairs(Players:GetPlayers()) do dar(p) end
Players.PlayerAdded:Connect(dar)
