-- RastroBreu_Cliente (LocalScript) — EFEITO VISUAL da passiva Rastro do Breu (Dragao Sombrio). So cosmetico: quem
-- decide o impulso e o servidor (RastroBreu_Servidor publica RastroModo / RastroCarga no modelo).
-- LINHAS negras com borda violeta saem das pontas das asas, da ponta da cauda e do quadril: fracas enquanto o impulso
-- carrega, fortes com o impulso ativo, e se desfazem atras do dragao. Cada linha = 2 Trails finos (nucleo preto
-- estreito + halo violeta mais largo e transparente), para nao cobrir a silhueta. Sem particulas, sem luz dinamica,
-- sem mexer em anatomia/rig. LOD por distancia da camera.
-- v2 (03/11): a v1 ligava ossos distantes e virava placas largas sobre a asa (reprovado na revisao do proprio teste).
-- v3 (04/11, pedido do usuario: "linha mais reta e maior"): os Trails nao ficam mais presos no osso (a batida da asa
-- desenhava zigue-zague): cada ponto e um Attachment no mundo que segue a posicao do osso RELATIVA a um referencial so de
-- direcao (altura filtrada) com filtro lento (SUAVE): o corpo anda sem atraso e a batida da asa / o passo somem -> reta. Vida 0,45 -> 1,0 s
-- (linha mais longa) e larguras 0,35/1,1 -> 0,5/1,5.
-- Valores artisticos NAO_APROVADO (prototipo para revisao do usuario).
local RunService = game:GetService("RunService")
local cam = workspace.CurrentCamera
local FORMAS = {Sombrio = true}
local LOD = 350                                         -- studs: alem disto as linhas ficam desligadas
local VIDA = 1.0                                        -- s de vida de cada linha (comprimento do rastro)
local SUAVE = 1.0                                       -- 1/s: quanto menor, mais reta (amortece a batida da asa e o passo)
local SUAVE_Y = 3.0                                     -- 1/s: altura do referencial (tira o sobe-e-desce do corpo)
local PRETO, VIOLETA = Color3.fromRGB(6, 0, 12), Color3.fromRGB(165, 60, 255)
local LARG_NUCLEO, LARG_HALO = 0.5, 1.5                 -- studs (modelo em escala 17,5)
local PONTOS = {"wing_tip_l", "wing_tip_r", "wing_feather_4_tip_l", "wing_feather_4_tip_r", "tail_tip", "Quadril"}
local registrados = {}                                  -- [modelo] = {lista, pontos}
local function registrar(m)
	if registrados[m] or not FORMAS[m:GetAttribute("FormaRegional") or ""] or not m.PrimaryPart then return end
	local B = {}; for _, b in ipairs(m:GetDescendants()) do if b:IsA("Bone") then B[b.Name] = b end end
	local lista, pontos = {}, {}
	local pasta = Instance.new("Folder"); pasta.Name = "RastroBreu_VFX"
	for _, nome in ipairs(PONTOS) do
		local o = B[nome]
		if o then
			local pt = {osso = o, local0 = nil, pares = {}}
			for _, c in ipairs({{"nucleo", LARG_NUCLEO, PRETO, 0, 1}, {"halo", LARG_HALO, VIOLETA, 0.8, 0.2}}) do
				local a0 = Instance.new("Attachment"); a0.Name = "Rastro_" .. nome .. "_" .. c[1] .. "_A"; a0.Parent = workspace.Terrain
				local a1 = Instance.new("Attachment"); a1.Name = "Rastro_" .. nome .. "_" .. c[1] .. "_B"; a1.Parent = workspace.Terrain
				table.insert(pt.pares, {a0, a1, c[2]})
				local tr = Instance.new("Trail"); tr.Name = nome .. "_" .. c[1]; tr.Attachment0 = a0; tr.Attachment1 = a1
				tr.Color = ColorSequence.new(c[3]); tr.Lifetime = VIDA; tr.MinLength = 0.15; tr.FaceCamera = true
				tr.LightEmission = c[4]; tr.LightInfluence = c[5]; tr.Enabled = false; tr:SetAttribute("Halo", c[1] == "halo")
				tr.Parent = pasta; table.insert(lista, tr)
			end
			table.insert(pontos, pt)
		end
	end
	pasta.Parent = m.PrimaryPart
	local R = {lista = lista, pontos = pontos}
	registrados[m] = R
	m.AncestryChanged:Connect(function()
		if not m:IsDescendantOf(workspace) then
			registrados[m] = nil
			for _, pt in ipairs(pontos) do for _, p in ipairs(pt.pares) do p[1]:Destroy(); p[2]:Destroy() end end
		end
	end)
end
local function transp(base) return NumberSequence.new({NumberSequenceKeypoint.new(0, base), NumberSequenceKeypoint.new(1, 1)}) end
local ultNivel = {}
RunService.RenderStepped:Connect(function(dt)
	for _, m in ipairs(workspace:GetChildren()) do if m:IsA("Model") and not registrados[m] and FORMAS[m:GetAttribute("FormaRegional") or ""] then registrar(m) end end
	local k = 1 - math.exp(-SUAVE * math.min(dt, 0.1)); local ky = 1 - math.exp(-SUAVE_Y * math.min(dt, 0.1))
	for m, R in pairs(registrados) do
		local nivel = 0
		local root = m.PrimaryPart
		if root and (root.Position - cam.CFrame.Position).Magnitude < LOD then
			if m:GetAttribute("RastroModo") then nivel = 2 elseif (m:GetAttribute("RastroCarga") or 0) > 0 then nivel = 1 end
		end
		if nivel > 0 and root then                                   -- pontos suavizados no referencial do corpo (antes de ligar)
			-- referencial so de direcao (sem inclinar/rolar) com altura filtrada: o corpo anda sem atraso e o balanco some
			local lv = root.CFrame.LookVector; lv = Vector3.new(lv.X, 0, lv.Z); lv = lv.Magnitude > 0.05 and lv.Unit or Vector3.zAxis
			R.y = R.y and (R.y + (root.Position.Y - R.y) * ky) or root.Position.Y
			local o = Vector3.new(root.Position.X, R.y, root.Position.Z)
			local rcf = CFrame.lookAt(o, o + lv); local up = Vector3.yAxis
			for _, pt in ipairs(R.pontos) do
				local alvo = rcf:PointToObjectSpace(pt.osso.TransformedWorldCFrame.Position)
				pt.local0 = pt.local0 and pt.local0:Lerp(alvo, k) or alvo
				local p = rcf:PointToWorldSpace(pt.local0)
				for _, par in ipairs(pt.pares) do par[1].WorldPosition = p - up * (par[3] / 2); par[2].WorldPosition = p + up * (par[3] / 2) end
			end
		elseif R.pontos[1] then R.y = nil; for _, pt in ipairs(R.pontos) do pt.local0 = nil end end
		if nivel ~= ultNivel[m] then
			ultNivel[m] = nivel
			for _, tr in ipairs(R.lista) do
				local halo = tr:GetAttribute("Halo")
				tr.Enabled = nivel > 0
				if nivel == 2 then tr.Transparency = transp(halo and 0.55 or 0.1)
				elseif nivel == 1 then tr.Transparency = transp(halo and 0.9 or 0.75) end
			end
		end
	end
end)
