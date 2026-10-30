-- EfeitosAsas_Cliente (LocalScript em StarterPlayerScripts): registra todo modelo com o atributo FormaRegional
-- (Montanhas / Glacial / Sombrio) no sistema de efeitos das asas. Efeitos so no cliente (cosmeticos).
-- Varredura leve a cada 2 s: com streaming, modelos e atributos chegam ao cliente depois do inicio.
local RS = game:GetService("ReplicatedStorage")
local jogador = game:GetService("Players").LocalPlayer
jogador:SetAttribute("VFX_Etapa", "inicio")
local Efeitos = require(RS:WaitForChild("VFX_Dragoes"):WaitForChild("EfeitosAsas"))
jogador:SetAttribute("VFX_Etapa", "modulo_ok")
local ciclos = 0
while true do
	for _, m in ipairs(workspace:GetChildren()) do
		if m:IsA("Model") and m:GetAttribute("FormaRegional") then
			local ok, err = pcall(Efeitos.registrar, m)
			if not ok then jogador:SetAttribute("VFX_Erro", tostring(err)) end
		end
	end
	ciclos += 1; jogador:SetAttribute("VFX_Ciclos", ciclos)
	task.wait(2)
end
