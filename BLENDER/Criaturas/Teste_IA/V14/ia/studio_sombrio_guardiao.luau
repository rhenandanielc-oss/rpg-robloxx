-- studio_sombrio_guardiao.luau (Studio, modo Edit): DRAGAO SOMBRIO SELVAGEM para testar a IA com o kit da Sombra (04/11).
-- Ninho proprio "Ninho_Sombrio" (copia da estrutura do Ninho_Pico: Base + Ovo) em terreno aberto (-150, 300), a 300
-- studs do Ninho_Sombrio; guardiao "Sombrio_Guardiao" = copia do workspace.Sombrio (mesma malha, clipes Sombrio_) com
-- GuardiaoNinho/GuardiaoId; kit Sombra completo (Sopro Umbral, Correntes, Passo, Eclipse; tatica em patch_ia_sombra).
-- Reversivel: apagar Ninho_Sombrio e Sombrio_Guardiao.
local lab = workspace.Laboratorio_IA
assert(workspace:FindFirstChild("Glacial"), "workspace.Sombrio nao existe (rode studio_montar_sombrio.luau)")
local function chao(x, z)
	local r = workspace:Raycast(Vector3.new(x, 600, z), Vector3.new(0, -1200, 0))
	return r and r.Position.Y, r and r.Instance
end
local X, Z = -150, 300                -- terreno (Terrain, y 2); 300 studs a oeste do Ninho_Glacial
local y, inst = chao(X, Z); assert(y, "sem chao em " .. X .. "," .. Z)
local velhoN = lab:FindFirstChild("Ninho_Sombrio"); if velhoN then velhoN:Destroy() end
local ninho = lab.Ninho_Pico:Clone(); ninho.Name = "Ninho_Sombrio"
ninho:SetAttribute("NinhoId", "Ninho_Sombrio"); ninho:SetAttribute("FormaRegional", "Sombrio"); ninho:SetAttribute("Guardiao", "Guardiao_Sombrio_01")
ninho:SetAttribute("Entrada", nil)
ninho:PivotTo(CFrame.new(X, y, Z) * (ninho:GetPivot() - ninho:GetPivot().Position))
local cfN, szN = ninho:GetBoundingBox()                                  -- assenta o FUNDO do ninho no chao
ninho:PivotTo(ninho:GetPivot() - Vector3.new(0, (cfN.Position.Y - szN.Y / 2) - y + 0.2, 0))
ninho.Parent = lab
local velhoG = workspace:FindFirstChild("Sombrio_Guardiao"); if velhoG then velhoG:Destroy() end
local g = workspace.Sombrio:Clone(); g.Name = "Sombrio_Guardiao"
for _, k in ipairs({"DonoUserId", "Cavaleiro", "Controlador", "MontariaModo", "PassoInvisivel", "PassoBonus", "RastroBonus", "RastroModo", "RastroCarga"}) do g:SetAttribute(k, nil) end
g:SetAttribute("GuardiaoNinho", "Ninho_Sombrio"); g:SetAttribute("GuardiaoId", "Guardiao_Sombrio_01")
g:SetAttribute("PastaAnimacoes", "Sombrio")
for _, d in ipairs(g:GetDescendants()) do if d:IsA("ProximityPrompt") then d:Destroy() end end      -- selvagem: nao monta
-- altura pivo -> chao igual a do Glacial montavel (raio IGNORANDO os dragoes: senao batia no proprio dorso)
local rp = RaycastParams.new(); rp.FilterType = Enum.RaycastFilterType.Exclude; rp.FilterDescendantsInstances = {workspace.Sombrio, g}
local ref = workspace.Sombrio:GetPivot().Position
local alt = ref.Y - workspace:Raycast(Vector3.new(ref.X, 600, ref.Z), Vector3.new(0, -1200, 0), rp).Position.Y
g:PivotTo(CFrame.new(X + 40, y + alt, Z + 40))
g:SetAttribute("HabilidadesForma", "Sopro,Arremetida,Tempestade,Coracao")
g.Parent = workspace
return ("Ninho_Sombrio em (%d, %.1f, %d) chao=%s | Sombrio_Guardiao em %s"):format(X, y, Z, inst and inst.Name or "?", tostring(g:GetPivot().Position))
