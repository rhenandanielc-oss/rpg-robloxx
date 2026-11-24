-- AuraCerbero_Cliente (LocalScript em StarterPlayerScripts) - aura de FOGO do Cerbero Sombrio, so visual, no cliente.
-- A4 (20/11, aprovada no Blender e levada ao Studio): ~90 ParticleEmitters "Chama" sob ossos AuraA4_* + 8 "Brasa".
-- 1) CORRIDA: le a velocidade horizontal do modelo (pela posicao, suavizada ~0,25 s de atraso) e inclina as chamas
--    para tras pela Acceleration (mundo). So visual.
-- 2) FURIA: atributo booleano "Furia" no modelo troca as cores de chamas e brasas para violeta de nucleo claro.
-- 3) CELULAR (toque sem teclado): liga so metade das chamas. LOD pela distancia da camera: >90 studs metade da taxa,
--    >160 desliga. Pele SEM brilho (pedido 20/11: corpo nao alaranjado, so o fogo). Sem luzes.
-- Valores [A TESTAR] no Roblox. Versao anterior (r6/A3): r6_antes_A4/AuraCerbero_Cliente.luau
-- Fonte: BLENDER/Criaturas/Cerbero_Sombrio_Ref/studio/AuraCerbero_Cliente.luau
local RS = game:GetService("RunService")
local UIS = game:GetService("UserInputService")
local CELULAR = UIS.TouchEnabled and not UIS.KeyboardEnabled
local VREF, INCLINA_MAX, ATRASO = 30, 0.35, 0.25  -- r3 23/11: chamas PRESAS ao corpo (LockedToPart); so inclinacao leve na corrida

local VIOLETA = ColorSequence.new({ColorSequenceKeypoint.new(0, Color3.fromRGB(240, 220, 255)), ColorSequenceKeypoint.new(0.18, Color3.fromRGB(190, 110, 255)),
	ColorSequenceKeypoint.new(0.55, Color3.fromRGB(125, 40, 230)), ColorSequenceKeypoint.new(1, Color3.fromRGB(45, 5, 90))})

local registros = {}
local function registrar(modelo, forcar)
	if registros[modelo] and not forcar then return end
	local antigo = registros[modelo]
	local r = {modelo = modelo, chamas = {}, nivel = -1, visto = os.clock(), furia = nil,
		vel = antigo and antigo.vel or Vector3.zero, pos = nil}
	for _, d in ipairs(modelo:GetDescendants()) do
		if d:IsA("SurfaceAppearance") then d.EmissiveStrength = 0
		elseif d:IsA("ParticleEmitter") and (d.Name == "Chama" or d.Name == "Brasa") then
			if d:GetAttribute("CorBase") == nil then d:SetAttribute("CorBase", d.Color) end   -- cor original (nao a violeta)
			table.insert(r.chamas, {pe = d, cor = d:GetAttribute("CorBase"), subida = d:GetAttribute("SubidaBase") or d.Acceleration.Y, chama = d.Name == "Chama"})
		end
	end
	table.sort(r.chamas, function(a, b) return a.pe.Parent.Name < b.pe.Parent.Name end)
	registros[modelo] = r
end

local function aplicarNivel(r, nivel)          -- 0 desligado, 1 metade da taxa, 2 cheio
	if r.nivel == nivel then return end
	r.nivel = nivel
	for i, c in ipairs(r.chamas) do
		local taxa = c.pe:GetAttribute("TaxaPC") or c.pe.Rate
		c.pe:SetAttribute("TaxaPC", taxa)
		c.pe.Enabled = nivel > 0 and (not CELULAR or not c.chama or i % 2 == 1)
		c.pe.Rate = (nivel == 1) and taxa * 0.5 or taxa
	end
end

local function aplicarFuria(r, furia)
	if r.furia == furia then return end
	r.furia = furia
	for _, c in ipairs(r.chamas) do c.pe.Color = furia and VIOLETA or c.cor end
end

local function ehAura(d) return d:IsA("Model") and (d:GetAttribute("AuraA4") or d:GetAttribute("AuraA3")) end
for _, d in ipairs(workspace:GetDescendants()) do if ehAura(d) then registrar(d) end end
workspace.DescendantAdded:Connect(function(d) if ehAura(d) then task.defer(registrar, d) end end)

RS.RenderStepped:Connect(function(dt)
	local cam = workspace.CurrentCamera
	for modelo, r in pairs(registros) do
		if not modelo.Parent then registros[modelo] = nil; continue end
		-- StreamingEnabled: o Model chega antes das pecas; enquanto faltar parte, registra de novo (1x por segundo)
		local esperado = (modelo:GetAttribute("NumChamas") or 49) + 8
		if #r.chamas < esperado and os.clock() - r.visto > 1 then registrar(modelo, true); r = registros[modelo] end
		local pp = modelo.PrimaryPart or modelo:FindFirstChildWhichIsA("BasePart")
		if not pp then continue end
		local p = pp.Position
		local dist = (p - cam.CFrame.Position).Magnitude
		aplicarNivel(r, dist > 160 and 0 or (dist > 90 and 1 or 2))
		aplicarFuria(r, modelo:GetAttribute("Furia") == true)
		-- velocidade horizontal suavizada (atraso ~ATRASO s), pela posicao: funciona com CFrame/anim e com fisica
		local v = Vector3.zero
		if r.pos and dt > 0 then v = (p - r.pos) / dt; v = Vector3.new(v.X, 0, v.Z) end
		r.pos = p
		if v.Magnitude > 200 then v = r.vel end                 -- teleporte: ignora
		r.vel = r.vel:Lerp(v, math.clamp(dt / ATRASO, 0, 1))
		r.tAcc = (r.tAcc or 0) + dt
		if r.nivel > 0 and r.tAcc >= 1 / 15 then          -- 15x por segundo basta (custo menor)
			r.tAcc = 0
			local k = math.min(r.vel.Magnitude / VREF, 1) * INCLINA_MAX
			local tras = r.vel.Magnitude > 0.5 and -r.vel.Unit or Vector3.zero
			for _, c in ipairs(r.chamas) do
				if c.chama then c.pe.Acceleration = Vector3.new(0, c.subida, 0) + tras * (c.subida * k) end
			end
		end
	end
end)
