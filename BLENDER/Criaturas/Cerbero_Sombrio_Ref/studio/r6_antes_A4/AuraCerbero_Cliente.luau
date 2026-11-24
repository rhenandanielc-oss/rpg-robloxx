-- AuraCerbero_Cliente (LocalScript em StarterPlayerScripts) - aura de FOGO A3 do Cerbero Sombrio, so visual, no cliente.
-- 1) PELE: pulso lento (1,8 s, como a A3) + cintilacao no EmissiveStrength da SurfaceAppearance (Corpo e Cabecas).
--    Precisa da mascara EmissiveMaskContent aplicada (aura/roblox_A3/T_Cerbero_*_EmissivaMascara.png); sem ela nao ha brilho.
--    Pulso UNICO nas tres cabecas (decisao do usuario 20/11: separar as cabecas fica para depois).
-- 2) CHAMAS (49 ParticleEmitters "Chama" sob os ossos AuraA3_*): no celular (toque sem teclado) liga so metade (25) com taxa 4
--    (~70 particulas vivas); no PC todas com a taxa do atributo TaxaPC (4/s, ~157 vivas).
-- 3) LOD por distancia da camera: acima de 160 studs desliga as chamas; acima de 90 corta a taxa pela metade.
-- Valores [A TESTAR] no Roblox. Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/AuraCerbero_Cliente.luau
local RS = game:GetService("RunService")
local UIS = game:GetService("UserInputService")
local CELULAR = UIS.TouchEnabled and not UIS.KeyboardEnabled
local PULSO = 1.8
local BASE, AMPL, CINT = 0, 0, 0   -- r5 (pedido 20/11): corpo SEM brilho, so o fogo das chamas

local registros = {}
local function registrar(modelo, forcar)
	if registros[modelo] and not forcar then return end
	local r = {modelo = modelo, sa = {}, chamas = {}, nivel = -1, visto = os.clock()}
	for _, d in ipairs(modelo:GetDescendants()) do
		if d:IsA("SurfaceAppearance") and (d.Parent.Name == "Cerbero_Corpo" or d.Parent.Name == "Cerbero_Cabecas") then
			table.insert(r.sa, d)
			if d.Parent.Name == "Cerbero_Corpo" then d.EmissiveTint = Color3.fromRGB(255, 120, 40) else d.EmissiveTint = Color3.fromRGB(255, 110, 35) end
		elseif d:IsA("ParticleEmitter") and (d.Name == "Chama" or d.Name == "Brasa") then
			table.insert(r.chamas, d)
		end
	end
	table.sort(r.chamas, function(a, b) return a.Parent.Name < b.Parent.Name end)
	registros[modelo] = r
end

local function aplicarNivel(r, nivel)          -- 0 desligado, 1 metade da taxa, 2 cheio
	if r.nivel == nivel then return end
	r.nivel = nivel
	for i, pe in ipairs(r.chamas) do
		local taxa = pe:GetAttribute("TaxaPC") or 4
		local ligado = nivel > 0 and (not CELULAR or i % 2 == 1)
		pe.Enabled = ligado
		pe.Rate = (nivel == 1) and taxa * 0.5 or taxa
	end
end

local function procurar()
	for _, d in ipairs(workspace:GetDescendants()) do
		if d:IsA("Model") and d:GetAttribute("AuraA3") then registrar(d) end
	end
end
procurar()
workspace.DescendantAdded:Connect(function(d)
	if d:IsA("Model") and d:GetAttribute("AuraA3") then task.defer(registrar, d) end
end)

local t = 0
RS.RenderStepped:Connect(function(dt)
	t += dt
	local cam = workspace.CurrentCamera
	for modelo, r in pairs(registros) do
		if not modelo.Parent then registros[modelo] = nil; continue end
		-- StreamingEnabled: o Model chega antes das pecas; enquanto faltar parte, registra de novo (1x por segundo)
		if (#r.sa < 2 or #r.chamas < 49) and os.clock() - r.visto > 1 then registrar(modelo, true); r = registros[modelo] end
		local pp = modelo.PrimaryPart or modelo:FindFirstChildWhichIsA("BasePart")
		local dist = pp and (pp.Position - cam.CFrame.Position).Magnitude or 0
		aplicarNivel(r, dist > 160 and 0 or (dist > 90 and 1 or 2))
		local pulso = 0.5 + 0.5 * math.sin(2 * math.pi * t / PULSO)
		local cint = math.noise(t * 3.1, 0.37) * CINT
		local forca = (dist > 160) and BASE * 0.6 or (BASE + AMPL * pulso + cint)
		for _, sa in ipairs(r.sa) do sa.EmissiveStrength = math.max(0, forca) end
	end
end)
