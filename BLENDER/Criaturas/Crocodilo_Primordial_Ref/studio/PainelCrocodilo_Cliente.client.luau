-- 20/11 PAINEL DE TESTE do Crocodilo Primordial (cliente): botoes + teclas. So pede ao servidor (PainelCrocodilo_Servidor).
local RepS, UIS, Players = game:GetService("ReplicatedStorage"), game:GetService("UserInputService"), game:GetService("Players")
local ev = RepS:WaitForChild("PainelCrocodilo")
local gui = Instance.new("ScreenGui"); gui.Name = "PainelCrocodilo"; gui.ResetOnSpawn = false
gui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui")
local caixa = Instance.new("Frame"); caixa.Size = UDim2.fromOffset(200, 0); caixa.AutomaticSize = Enum.AutomaticSize.Y
caixa.Position = UDim2.new(0, 12, 0.5, -170); caixa.BackgroundColor3 = Color3.fromRGB(20, 28, 30); caixa.BackgroundTransparency = 0.25
caixa.Parent = gui
Instance.new("UICorner", caixa).CornerRadius = UDim.new(0, 8)
local pad = Instance.new("UIPadding", caixa); for _, k in ipairs({"PaddingTop", "PaddingBottom", "PaddingLeft", "PaddingRight"}) do pad[k] = UDim.new(0, 8) end
local lista = Instance.new("UIListLayout", caixa); lista.Padding = UDim.new(0, 5); lista.SortOrder = Enum.SortOrder.LayoutOrder
local titulo = Instance.new("TextLabel"); titulo.Size = UDim2.new(1, 0, 0, 22); titulo.BackgroundTransparency = 1
titulo.Text = "Crocodilo - teste"; titulo.TextColor3 = Color3.fromRGB(190, 230, 220); titulo.Font = Enum.Font.GothamBold; titulo.TextSize = 15
titulo.LayoutOrder = 0; titulo.Parent = caixa
local BOTOES = {
	{"agarrao", "1  Mordida de Agarrao", Enum.KeyCode.One},
	{"emboscada", "2  Emboscada", Enum.KeyCode.Two},
	{"submersao", "3  Submersao", Enum.KeyCode.Three},
	{"cauda", "4  Cauda de Mare", Enum.KeyCode.Four},
	{"virar", "R  Virar para a presa", Enum.KeyCode.R},
	{"cancelar", "X  Cancelar poder", Enum.KeyCode.X},
	{"bonecos", "Bonecos de pe", nil},
	{"ir", "Ir ao crocodilo", nil},
}
local TECLA = {}
for i, b in ipairs(BOTOES) do
	local bt = Instance.new("TextButton"); bt.Size = UDim2.new(1, 0, 0, 30); bt.LayoutOrder = i
	bt.BackgroundColor3 = i <= 4 and Color3.fromRGB(34, 78, 92) or Color3.fromRGB(52, 58, 62)
	bt.TextColor3 = Color3.new(1, 1, 1); bt.Font = Enum.Font.Gotham; bt.TextSize = 14; bt.Text = b[2]
	bt.TextXAlignment = Enum.TextXAlignment.Left; bt.AutoButtonColor = true; bt.Parent = caixa
	Instance.new("UICorner", bt).CornerRadius = UDim.new(0, 6)
	Instance.new("UIPadding", bt).PaddingLeft = UDim.new(0, 8)
	bt.Activated:Connect(function() ev:FireServer(b[1]) end)
	if b[3] then TECLA[b[3]] = b[1] end
end
local dica = Instance.new("TextLabel"); dica.Size = UDim2.new(1, 0, 0, 0); dica.AutomaticSize = Enum.AutomaticSize.Y
dica.BackgroundTransparency = 1; dica.TextWrapped = true; dica.TextXAlignment = Enum.TextXAlignment.Left
dica.TextColor3 = Color3.fromRGB(170, 180, 180); dica.Font = Enum.Font.Gotham; dica.TextSize = 12; dica.LayoutOrder = 99
dica.Text = "Montar: segure o botao perto da sela. Descer: E. Agua de verdade: Canal ao sul. Emboscada: logo depois de emergir da Submersao."
dica.Parent = caixa
local aviso = Instance.new("TextLabel"); aviso.Size = UDim2.new(0.6, 0, 0, 0); aviso.AutomaticSize = Enum.AutomaticSize.Y
aviso.Position = UDim2.new(0.2, 0, 1, -110); aviso.BackgroundColor3 = Color3.fromRGB(0, 0, 0); aviso.BackgroundTransparency = 0.45
aviso.TextColor3 = Color3.new(1, 1, 1); aviso.TextWrapped = true; aviso.Font = Enum.Font.Gotham; aviso.TextSize = 15
aviso.Text = ""; aviso.Visible = false; aviso.Parent = gui
Instance.new("UIPadding", aviso).PaddingTop = UDim.new(0, 6)
local n = 0
ev.OnClientEvent:Connect(function(tipo, txt)
	if tipo ~= "msg" then return end
	n += 1; local meu = n; aviso.Text = tostring(txt); aviso.Visible = true
	task.delay(4, function() if n == meu then aviso.Visible = false end end)
end)
UIS.InputBegan:Connect(function(inp, proc)
	if proc then return end
	local a = TECLA[inp.KeyCode]; if a then ev:FireServer(a) end
end)
