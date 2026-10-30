-- EfeitosAsas_Cliente (LocalScript em StarterPlayerScripts): registra todo modelo com o atributo FormaRegional
-- (Montanhas / Glacial / Sombrio) no sistema de efeitos das asas. Efeitos so no cliente (cosmeticos).
-- Varredura leve a cada 2 s: com streaming, modelos e atributos chegam ao cliente depois do inicio.
local RS = game:GetService("ReplicatedStorage")
local Efeitos = require(RS:WaitForChild("VFX_Dragoes"):WaitForChild("EfeitosAsas"))
while true do
	for _, m in ipairs(workspace:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("FormaRegional") then pcall(Efeitos.registrar, m) end
	end
	task.wait(2)
end
