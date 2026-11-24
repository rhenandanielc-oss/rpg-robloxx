-- aplicar_texturas_aura.luau - roda no EDIT pelo execute_luau (PluginSecurity) depois que o usuario importa as 4 imagens.
-- Guarda as texturas originais em atributos (ColorMapOriginal) para voltar atras e aplica a cor com fogo + mascara de emissao.
-- Preencher os 4 IDs abaixo (Asset Manager > Images > botao direito > Copy Asset ID).
local IDS = {
	Corpo = {cor = 0, mascara = 0},
	Cabecas = {cor = 0, mascara = 0},
}
local m = workspace.Teste_Cerbero.Cerbero_Sombrio
local out = {}
for nome, ids in pairs(IDS) do
	local sa = m["Cerbero_" .. nome].SurfaceAppearance
	if sa:GetAttribute("ColorMapOriginal") == nil then sa:SetAttribute("ColorMapOriginal", sa.ColorMapContent.Uri) end
	sa.ColorMapContent = Content.fromUri("rbxassetid://" .. ids.cor)
	sa.EmissiveMaskContent = Content.fromUri("rbxassetid://" .. ids.mascara)
	sa.EmissiveStrength = 2.2
	sa.EmissiveTint = Color3.fromRGB(255, 120, 40)
	table.insert(out, nome .. " ok")
end
return table.concat(out, ", ")
