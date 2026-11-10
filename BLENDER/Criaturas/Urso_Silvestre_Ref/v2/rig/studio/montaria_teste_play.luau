-- Montaria do urso: codigo do TESTE no Play (09/11/2026), rodado pelo MCP (execute_luau); NAO e sistema do jogo.
-- Registro do que foi executado, para repetir o ensaio. Lab: Workspace.Teste_Urso_v2 (urso + Urso_Sela_Teste + TESTE_Cavaleiro_R15).

-- [CLIENTE] sela segue o urso + cavaleiro preso ao dorso quando montado + camera lateral (lado E = -X do Studio)
-- A sela importada tem os PROPRIOS 18 ossos (mesmos nomes do urso, mas o Raiz veio girado 180 graus no import): ligar a pele
-- aos ossos do urso pelo nome deformava errado, e ossos de mesmo nome no MESMO Model fazem a pele do urso usar os da sela.
-- Por isso a sela fica num Model separado (Urso_Sela_Teste, Motor6D na RootPart do urso) e cada osso dela copia o osso do urso.
local RS = game:GetService("RunService")
local lab = workspace:WaitForChild("Teste_Urso_v2")
local urso = lab:WaitForChild("Urso_Silvestre_v2_Piloto"); local selaM = lab:WaitForChild("Urso_Sela_Teste", 10); local rig = lab:WaitForChild("TESTE_Cavaleiro_R15", 10)
local sela = selaM:WaitForChild("Urso_Silvestre_Sela", 10)
local rp = urso:WaitForChild("RootPart", 10)
local function rest(b) local p = b.Parent; if p:IsA("Bone") then return rest(p) * b.CFrame end; return p.CFrame * b.CFrame end
local ossos = {}
local function coletar(inst) for _, c in inst:GetChildren() do if c:IsA("Bone") then table.insert(ossos, c); coletar(c) end end end
coletar(sela)
local par = {}
for _, b in ossos do local bu = rp:FindFirstChild(b.Name, true); if bu then par[b] = {u = bu, rel = rest(bu):Inverse() * rest(b)} end end
local c2 = rp:FindFirstChild("Coluna2", true); local relC2 = rest(c2):Inverse() * rp.CFrame
local hrp = rig:WaitForChild("HumanoidRootPart")
RS:BindToRenderStep("SelaSegue", Enum.RenderPriority.Last.Value + 2, function()
	for _, b in ossos do                                    -- pai antes do filho
		local p = par[b]
		if p then
			local desejado = p.u.TransformedWorldCFrame * p.rel
			local pai = b.Parent:IsA("Bone") and b.Parent.TransformedWorldCFrame or b.Parent.CFrame
			b.Transform = (pai * b.CFrame):Inverse() * desejado
		end
	end
	-- montado: a HRP do cavaleiro segue a Coluna2 (como no Blender); subindo/descendo: fica na RootPart do urso (dados do clipe)
	if rig:GetAttribute("ModoMontado") then hrp.CFrame = c2.TransformedWorldCFrame * relC2 else hrp.CFrame = rp.CFrame end
end)

-- [SERVIDOR] sequencia: Montar_E (urso + cavaleiro juntos) -> Sentado em loop + Andar 3,6 s + Corrida 2,8 s -> parar -> Desmontar_E
-- local T = require(PASTA.TestePlayUrso); faixas do cavaleiro: AnimationClipProvider:RegisterAnimationClip(PASTA.Montaria.Cav_*)
-- carregadas no Animator do Humanoid do TESTE_Cavaleiro_R15 (HRP ancorada); atributo ModoMontado liga o modo montado no cliente.
