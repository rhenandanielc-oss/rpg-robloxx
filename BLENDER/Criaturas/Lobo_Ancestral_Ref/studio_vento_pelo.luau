-- RASCUNHO (NAO instalado; precisa de aprovacao do usuario antes de ir para src/ ou para o Studio).
-- VentoPelo_Cliente (LocalScript, StarterPlayerScripts): o pelo das criaturas balanca com a FORCA DO VENTO DO CLIMA
-- (workspace.GlobalWind, que os scripts de clima/ambiente ja variam) somada ao ar do proprio movimento, por cima dos
-- clipes (que saem SEM vento). So visual, so no cliente; nada vai ao servidor.
-- Criatura: modelo com a TAG "PeloVento" e o atributo "PerfilPelo" (ex.: "Lobo") -> ReplicatedStorage.PeloVento.<Perfil>
-- (modulo GERADO pelo Blender: vento_pelo_comum.py -> PeloVento_Lobo.luau). Abrigo: atributo numerico "Abrigo" (0..1)
-- no modelo (caverna/toca) reduz o vento ambiente.
-- Formula = a da previa do Blender (previa_vento.py): forca(w) = min(maximo, minimo + (w/ref)^expoente); rajada lenta +
-- tremulacao com frequencias que sobem com o vento; angulo = amp * forca * (parte do vento perpendicular a mecha) * ganho.
-- Custo: so criaturas a ate DIST studs da camera; ~27 ossos por lobo.
local RS = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local CollectionService = game:GetService("CollectionService")
local cam = workspace.CurrentCamera
local DIST = 90
local Perfis = RS:WaitForChild("PeloVento")

local function forca(c, w) return math.min(c.maximo, c.minimo + (math.max(w, 0) / c.ref) ^ c.expoente) end
local function ganho(t, fase, w)
	local f1, f2, f3 = 0.22 + 0.02 * w, 1.3 + 0.10 * w, 2.6 + 0.20 * w
	local tau = 2 * math.pi
	return 0.55 + 0.30 * math.sin(tau * f1 * t + fase) + 0.12 * math.sin(tau * f2 * t + 1.7 * fase) + 0.05 * math.sin(tau * f3 * t + 2.3 * fase)
end

local estados = {}
local function preparar(m)
	local nome = m:GetAttribute("PerfilPelo"); local mod = nome and Perfis:FindFirstChild(nome)
	if not mod then return nil end
	local P = require(mod); local piv = m:GetPivot(); local lista = {}
	for _, b in ipairs(m:GetDescendants()) do
		local cfg = b:IsA("Bone") and P.ossos[b.Name]
		if cfg then
			-- direcao da mecha no espaco do proprio osso, tirada do REPOUSO (WorldCFrame nao inclui o Transform do clipe)
			local dirLocal = b.WorldCFrame:VectorToObjectSpace(piv:VectorToWorldSpace(cfg.dir)).Unit
			table.insert(lista, {osso = b, amp = cfg.amp, fase = cfg.fase, dir = dirLocal})
		end
	end
	return {P = P, ossos = lista, ult = {}, pos = piv.Position}
end
local function ligar(m) estados[m] = preparar(m) end
for _, m in ipairs(CollectionService:GetTagged("PeloVento")) do ligar(m) end
CollectionService:GetInstanceAddedSignal("PeloVento"):Connect(ligar)
CollectionService:GetInstanceRemovedSignal("PeloVento"):Connect(function(m) estados[m] = nil end)

local t = 0
RunService.PreSimulation:Connect(function(dt)
	t += dt
	local vento = workspace.GlobalWind
	for m, e in pairs(estados) do
		if not m.Parent then estados[m] = nil; continue end
		local c = e.P.curva
		local p = m:GetPivot().Position
		local vel = (p - e.pos) / math.max(dt, 1e-3); e.pos = p
		local longe = (p - cam.CFrame.Position).Magnitude > DIST
		local ar = vento * (1 - (m:GetAttribute("Abrigo") or 0)) - vel * c.arMovimento     -- ar relativo (mundo)
		local w = ar.Magnitude; local s = forca(c, w)
		for _, o in ipairs(e.ossos) do
			local b = o.osso
			-- desfaz o que esta camada somou no quadro anterior se nenhum clipe reescreveu o osso
			local u = e.ult[b]; if u and b.Transform == u.T then b.Transform = u.T * u.R:Inverse() end
			e.ult[b] = nil
			if longe or w < 1e-3 then continue end
			local cf = b.TransformedWorldCFrame
			local d = cf:VectorToWorldSpace(o.dir)
			local emp = ar - d * ar:Dot(d)
			if emp.Magnitude < 1e-3 then continue end
			local sens = math.min(1, emp.Magnitude / w)
			local eixoLocal = cf:VectorToObjectSpace(d:Cross(emp.Unit))
			local R = CFrame.fromAxisAngle(eixoLocal, math.rad(o.amp * s * sens * ganho(t, o.fase, w)))
			b.Transform = b.Transform * R
			e.ult[b] = {T = b.Transform, R = R}
		end
	end
end)
