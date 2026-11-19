-- SoltarAliado_Cliente (LocalScript em StarterPlayerScripts) - 19/11 [PROPOSTA], so o place de teste do Crocodilo.
-- Quando o crocodilo agarra a criatura de um aliado (PvP), o SERVIDOR manda "mostrar" e aparece a opcao "Soltar aliado"
-- (botao clicavel/tocavel no celular + tecla E / botao X do controle). Escolher manda "ir" ao servidor, que valida e leva o
-- personagem ate a cabeca do crocodilo para golpear. "esconder" some com a opcao (aliado solto ou pegada acabou).
-- O cliente so mostra e pede: quem decide, move, confere alcance e aplica dano e o servidor.
local Players = game:GetService("Players")
local CAS = game:GetService("ContextActionService")
local Rem = game:GetService("ReplicatedStorage"):WaitForChild("Crocodilo_SoltarAliado")
local pl = Players.LocalPlayer

local gui = Instance.new("ScreenGui"); gui.Name = "SoltarAliado"; gui.ResetOnSpawn = false; gui.DisplayOrder = 50
local bt = Instance.new("TextButton"); bt.Name = "Botao"; bt.AnchorPoint = Vector2.new(0.5, 1)
bt.Position = UDim2.new(0.5, 0, 1, -120); bt.Size = UDim2.fromOffset(340, 64)
bt.BackgroundColor3 = Color3.fromRGB(150, 40, 30); bt.BackgroundTransparency = 0.1; bt.AutoButtonColor = true
bt.TextColor3 = Color3.new(1, 1, 1); bt.Font = Enum.Font.GothamBold; bt.TextScaled = true; bt.Visible = false
local c = Instance.new("UICorner"); c.CornerRadius = UDim.new(0, 12); c.Parent = bt
local s = Instance.new("UIStroke"); s.Color = Color3.fromRGB(255, 210, 120); s.Thickness = 2; s.Parent = bt
local pad = Instance.new("UIPadding"); pad.PaddingLeft = UDim.new(0, 10); pad.PaddingRight = UDim.new(0, 10); pad.Parent = bt
bt.Parent = gui; gui.Parent = pl:WaitForChild("PlayerGui")

local ativo, nomeAliado = false, ""
local function esconder() ativo = false; bt.Visible = false; CAS:UnbindAction("SoltarAliado") end
local function ir()
	if not ativo then return end
	ativo = false; bt.Text = "Indo soltar " .. nomeAliado .. "..."
	Rem:FireServer("ir")
end
bt.Activated:Connect(ir)
Rem.OnClientEvent:Connect(function(acao, nome)
	if acao == "mostrar" then
		ativo, nomeAliado = true, tostring(nome or "aliado")
		bt.Text = "Soltar aliado  [E]"; bt.Visible = true
		CAS:BindAction("SoltarAliado", function(_, estado)
			if estado == Enum.UserInputState.Begin then ir() end
			return Enum.ContextActionResult.Sink
		end, false, Enum.KeyCode.E, Enum.KeyCode.ButtonX)
	elseif acao == "esconder" then
		esconder()
	end
end)
_G.SoltarAliado_Teste = ir   -- so para o teste automatizado (equivale a clicar)
