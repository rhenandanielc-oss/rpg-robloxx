-- Cabeca_Cliente (Script RunContext=Client, dentro da pasta de UM lobo artico) - r1 26/11/2026 [PROPOSTA][A TESTAR]
-- Pendencia "cabeca acompanhando o alvo": por cima da animacao, gira Pescoco1/Pescoco2/Cabeca em volta do eixo VERTICAL do mundo na
-- direcao de OlharAlvo (atributo publicado pelo Controle quando a IA orienta o lobo para o intruso). Total ate 45 graus, dividido
-- 30/30/40 entre os tres ossos; suavizado (0,18 s); sem alvo ou alvo atras (> 110 graus) volta ao normal. So roda com o lobo a
-- menos de 80 studs da camera (celular). Visual apenas: nada no servidor muda (dano, mira e cone da mordida continuam no Kit).
local RunService = game:GetService("RunService")
local pasta = script.Parent
local lobo = pasta:WaitForChild("LoboArtico_LOW", 30)
if not lobo then return end
local CFG = {max = math.rad(45), partes = {Pescoco1 = 0.3, Pescoco2 = 0.3, Cabeca = 0.4}, suave = 0.18, atras = math.rad(110), distCamera = 80}
local ossos = {}
local function achar()
	for nome in pairs(CFG.partes) do ossos[nome] = ossos[nome] or lobo:FindFirstChild(nome, true) end
end
achar()
local atual = 0
local function plano(v) return Vector3.new(v.X, 0, v.Z) end
RunService.PreRender:Connect(function(dt)
	if not lobo.Parent then return end
	local cam = workspace.CurrentCamera
	local pv = lobo:GetPivot()
	if cam and (cam.CFrame.Position - pv.Position).Magnitude > CFG.distCamera * (lobo:GetAttribute("Escala") or 1) then atual = 0; return end
	if not (ossos.Pescoco1 and ossos.Cabeca) then achar(); return end
	local alvoDir = lobo:GetAttribute("OlharAlvo")
	local alvoAng = 0
	if typeof(alvoDir) == "Vector3" and plano(alvoDir).Magnitude > 0.1 and not lobo:GetAttribute("PoderAtivo") then
		local f = plano(pv.LookVector).Unit; local d = plano(alvoDir).Unit
		local a = math.atan2(f.Z * d.X - f.X * d.Z, f.X * d.X + f.Z * d.Z)        -- + = esquerda (mesma convencao do Controle)
		if math.abs(a) < CFG.atras then alvoAng = math.clamp(a, -CFG.max, CFG.max) end
	end
	atual += (alvoAng - atual) * (1 - math.exp(-dt / CFG.suave))
	if math.abs(atual) < 1e-3 then return end
	for _, nome in ipairs({"Pescoco1", "Pescoco2", "Cabeca"}) do
		local b = ossos[nome]
		if b then
			local W = b.TransformedWorldCFrame.Rotation
			local extra = W:Inverse() * CFrame.Angles(0, atual * CFG.partes[nome], 0) * W     -- giro em volta do eixo vertical do mundo
			b.Transform = b.Transform * extra
		end
	end
end)
