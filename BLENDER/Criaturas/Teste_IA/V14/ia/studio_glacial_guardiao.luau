-- studio_glacial_guardiao.luau (Studio, modo Edit): DRAGAO GLACIAL SELVAGEM para testar a IA (sistema universal 01/11).
-- Ninho proprio "Ninho_Glacial" (copia da estrutura do Ninho_Pico: Base + Ovo) em terreno aberto, longe dos ninhos do
-- Montanhas, usando os POIs do Laboratorio_IA; guardiao "Glacial_Guardiao" = copia do workspace.Glacial (mesma malha,
-- clipes Glacial_) com GuardiaoNinho/GuardiaoId. FormaRegional Glacial: o combate so usa os basicos (mordida, garra,
-- cauda); kit de gelo PENDENTE. Reversivel: apagar Ninho_Glacial e Glacial_Guardiao.
local lab = workspace.Laboratorio_IA
assert(workspace:FindFirstChild("Glacial"), "workspace.Glacial nao existe (rode studio_montar_glacial.luau)")
local function chao(x, z)
	local r = workspace:Raycast(Vector3.new(x, 600, z), Vector3.new(0, -1200, 0))
	return r and r.Position.Y, r and r.Instance
end
local X, Z = 150, 300                 -- terreno plano e visivel (em -200,400 o ninho ficava na borda, sobre a placa-base)
local y, inst = chao(X, Z); assert(y, "sem chao em " .. X .. "," .. Z)
local velhoN = lab:FindFirstChild("Ninho_Glacial"); if velhoN then velhoN:Destroy() end
local ninho = lab.Ninho_Pico:Clone(); ninho.Name = "Ninho_Glacial"
ninho:SetAttribute("NinhoId", "Ninho_Glacial"); ninho:SetAttribute("FormaRegional", "Glacial"); ninho:SetAttribute("Guardiao", "Guardiao_Glacial_01")
ninho:SetAttribute("Entrada", nil)
ninho:PivotTo(CFrame.new(X, y, Z) * (ninho:GetPivot() - ninho:GetPivot().Position))
local cfN, szN = ninho:GetBoundingBox()                                  -- assenta o FUNDO do ninho no chao
ninho:PivotTo(ninho:GetPivot() - Vector3.new(0, (cfN.Position.Y - szN.Y / 2) - y + 0.2, 0))
ninho.Parent = lab
local velhoG = workspace:FindFirstChild("Glacial_Guardiao"); if velhoG then velhoG:Destroy() end
local g = workspace.Glacial:Clone(); g.Name = "Glacial_Guardiao"
for _, k in ipairs({"DonoUserId", "Cavaleiro", "Controlador", "MontariaModo"}) do g:SetAttribute(k, nil) end
g:SetAttribute("GuardiaoNinho", "Ninho_Glacial"); g:SetAttribute("GuardiaoId", "Guardiao_Glacial_01")
g:SetAttribute("PastaAnimacoes", "Glacial"); g:SetAttribute("TomVoz", 0.8)
for _, d in ipairs(g:GetDescendants()) do if d:IsA("ProximityPrompt") then d:Destroy() end end      -- selvagem: nao monta
-- altura pivo -> chao igual a do Glacial montavel (raio IGNORANDO os dragoes: senao batia no proprio dorso)
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {workspace.Glacial, g}
local ref = workspace.Glacial:GetPivot().Position
local alt = ref.Y - workspace:Raycast(Vector3.new(ref.X, 600, ref.Z), Vector3.new(0, -1200, 0), rp).Position.Y
g:PivotTo(CFrame.new(X + 40, y + alt, Z + 40))
g.Parent = workspace
return ("Ninho_Glacial em (%d, %.1f, %d) chao=%s | Glacial_Guardiao em %s"):format(X, y, Z, inst and inst.Name or "?", tostring(g:GetPivot().Position))
