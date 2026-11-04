-- RastroBreu_Cliente (LocalScript) — EFEITO VISUAL da passiva Rastro do Breu (Dragao Sombrio). So cosmetico: quem
-- decide o impulso e o servidor (RastroBreu_Servidor publica RastroModo / RastroCarga no modelo).
-- LINHAS negras com borda violeta saem das pontas das asas, da ponta da cauda e do quadril: fracas enquanto o impulso
-- carrega, fortes com o impulso ativo, e se desfazem atras do dragao. Cada linha = 2 Trails finos entre dois
-- Attachments proximos criados nos ossos (nucleo preto estreito + halo violeta mais largo e transparente), para nao
-- cobrir a silhueta. Sem particulas, sem luz dinamica, sem mexer em anatomia/rig. LOD por distancia da camera.
-- v2 (03/11): a v1 ligava ossos distantes e virava placas largas sobre a asa (reprovado na revisao do proprio teste).
-- Valores artisticos NAO_APROVADO (prototipo para revisao do usuario).
local RunService = game:GetService("RunService")
local cam = workspace.CurrentCamera
local FORMAS = {Sombrio = true}
local LOD = 350                                         -- studs: alem disto as linhas ficam desligadas
local VIDA = 0.45                                       -- s de vida de cada linha
local PRETO, VIOLETA = Color3.fromRGB(6, 0, 12), Color3.fromRGB(165, 60, 255)
local LARG_NUCLEO, LARG_HALO = 0.35, 1.1                -- studs (modelo em escala 17,5)
local PONTOS = {"wing_tip_l", "wing_tip_r", "wing_feather_4_tip_l", "wing_feather_4_tip_r", "tail_tip", "Quadril"}
local registrados = {}                                  -- [modelo] = {trilhas}
local function par(osso, larg, nome, pasta)
	local a0 = Instance.new("Attachment"); a0.Name = nome .. "_A"; a0.Position = Vector3.new(0, -larg / 2, 0); a0.Parent = osso
	local a1 = Instance.new("Attachment"); a1.Name = nome .. "_B"; a1.Position = Vector3.new(0, larg / 2, 0); a1.Parent = osso
	table.insert(pasta, a0); table.insert(pasta, a1)
	return a0, a1
end
local function registrar(m)
	if registrados[m] or not FORMAS[m:GetAttribute("FormaRegional") or ""] or not m.PrimaryPart then return end
	local B = {}; for _, b in ipairs(m:GetDescendants()) do if b:IsA("Bone") then B[b.Name] = b end end
	local lista, extras = {}, {}
	local pasta = Instance.new("Folder"); pasta.Name = "RastroBreu_VFX"
	for _, nome in ipairs(PONTOS) do
		local o = B[nome]
		if o then
			for _, c in ipairs({{"nucleo", LARG_NUCLEO, PRETO, 0, 1}, {"halo", LARG_HALO, VIOLETA, 0.8, 0.2}}) do
				local a0, a1 = par(o, c[2], "Rastro_" .. c[1], extras)
				local tr = Instance.new("Trail"); tr.Name = nome .. "_" .. c[1]; tr.Attachment0 = a0; tr.Attachment1 = a1
				tr.Color = ColorSequence.new(c[3]); tr.Lifetime = VIDA; tr.MinLength = 0.15; tr.FaceCamera = true
				tr.LightEmission = c[4]; tr.LightInfluence = c[5]; tr.Enabled = false; tr:SetAttribute("Halo", c[1] == "halo")
				tr.Parent = pasta; table.insert(lista, tr)
			end
		end
	end
	pasta.Parent = m.PrimaryPart
	registrados[m] = {lista = lista, extras = extras}
	m.AncestryChanged:Connect(function() if not m:IsDescendantOf(workspace) then registrados[m] = nil end end)
end
local function transp(base) return NumberSequence.new({NumberSequenceKeypoint.new(0, base), NumberSequenceKeypoint.new(1, 1)}) end
local ultNivel = {}
RunService.RenderStepped:Connect(function()
	for _, m in ipairs(workspace:GetChildren()) do if m:IsA("Model") and not registrados[m] and FORMAS[m:GetAttribute("FormaRegional") or ""] then registrar(m) end end
	for m, R in pairs(registrados) do
		local nivel = 0
		if m.PrimaryPart and (m.PrimaryPart.Position - cam.CFrame.Position).Magnitude < LOD then
			if m:GetAttribute("RastroModo") then nivel = 2 elseif (m:GetAttribute("RastroCarga") or 0) > 0 then nivel = 1 end
		end
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
