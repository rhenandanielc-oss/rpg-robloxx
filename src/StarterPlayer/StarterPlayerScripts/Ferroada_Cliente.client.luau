-- Ferroada_Cliente (LocalScript, StarterPlayerScripts) — VISUAL da Ferroada da Wyvern: a cauda segue a MIRA (so cosmetico).
-- O servidor (Combate_Wyvern.Ferroada) marca FerroadaYaw (graus, + = esquerda, visto de cima) e FerroadaT0 (hora do
-- servidor) no inicio do golpe. Aqui a cauda gira em torno do eixo vertical, distribuido pela base (tail_01, tail_02,
-- Cauda3), por cima do clipe FerraoAtaque: entra suave enquanto a cauda sobe, segura no golpe e volta suave no fim.
-- Mesmo giro que o servidor usa no acerto. Usuario 13/11: "se o alvo estiver de lado ou atras, a cauda deve seguir".
local RunService = game:GetService("RunService")
local OSSOS = {{"tail_01", 0.5}, {"tail_02", 0.3}, {"Cauda3", 0.2}}
local DUR, ENTRA, SAI = 1.5, 0.35, 0.4                -- s (clipe FerraoAtaque = 1,5 s)
local modelos = {}

local function suave(k) k = math.clamp(k, 0, 1); return k * k * (3 - 2 * k) end
local function ligar(m)
	if modelos[m] or not m:IsA("Model") or m:GetAttribute("FormaRegional") ~= "Wyvern" then return end
	modelos[m] = {}                                   -- ossos procurados na hora do golpe (com streaming chegam depois)
	m.AncestryChanged:Connect(function(_, p) if not p then modelos[m] = nil end end)
end
for _, m in ipairs(workspace:GetChildren()) do ligar(m) end
workspace.ChildAdded:Connect(function(m) task.defer(ligar, m) end)
task.spawn(function() while true do task.wait(3); for _, m in ipairs(workspace:GetChildren()) do if not modelos[m] then ligar(m) end end end end)

RunService.PreSimulation:Connect(function()
	for m, o in pairs(modelos) do
		local yaw, t0 = m:GetAttribute("FerroadaYaw"), m:GetAttribute("FerroadaT0")
		if yaw and t0 and math.abs(yaw) > 0.5 then
			local t = workspace:GetServerTimeNow() - t0
			local w = (t < ENTRA and suave(t / ENTRA)) or (t > DUR - SAI and suave((DUR - t) / SAI)) or 1
			if w > 0 and not (o[1] and o[1].Parent) then
				for _, d in ipairs(m:GetDescendants()) do
					if d:IsA("Bone") then for i, x in ipairs(OSSOS) do if d.Name == x[1] then o[i] = d end end end
				end
			end
			if w > 0 then
				for i, x in ipairs(OSSOS) do
					local b = o[i]
					if b then
						local eixo = b.TransformedWorldCFrame:VectorToObjectSpace(Vector3.yAxis)
						b.Transform = b.Transform * CFrame.fromAxisAngle(eixo, math.rad(yaw) * x[2] * w)
					end
				end
			end
		end
	end
end)
