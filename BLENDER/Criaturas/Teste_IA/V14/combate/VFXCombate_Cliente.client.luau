-- VFXCombate_Cliente (LocalScript, StarterPlayerScripts): repassa os eventos cosmeticos do servidor ao VFXCombate.
local RS = game:GetService("ReplicatedStorage")
local rede = RS:WaitForChild("Combate_Dragoes")
local VFX = require(rede:WaitForChild("VFXCombate"))
rede:WaitForChild("FX").OnClientEvent:Connect(function(d)
	local ok, err = pcall(VFX.evento, d)
	if not ok then warn("VFXCombate: " .. tostring(err)) end
end)
