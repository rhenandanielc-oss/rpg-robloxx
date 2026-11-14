-- ToxinaFerrao_Cliente (LocalScript, StarterPlayerScripts) — efeito VISUAL discreto da intoxicacao da Wyvern (so cosmetico).
-- O servidor (Combate_Wyvern.ToxinaFerrao) marca o alvo intoxicado com a tag ToxinaFerrao_Alvo e o atributo Intoxicado
-- (hora do servidor do fim). Enquanto valer, um leve vapor esverdeado sobe do corpo; renovar so muda o fim; ao acabar ou
-- ser removido (antidoto/purificacao futuros) a tag sai e o vapor apaga. Sem varrer o Workspace: so os alvos com a tag.
local CS = game:GetService("CollectionService")
local TAG = "ToxinaFerrao_Alvo"
local TEXTURA = "rbxasset://textures/particles/smoke_main.dds"
local ativos = {}

local function raiz(m) return m:FindFirstChild("HumanoidRootPart") or m:FindFirstChild("UpperTorso") or m.PrimaryPart end
local function ligar(m)
	if ativos[m] or not m:IsA("Model") then return end
	local r = raiz(m); if not r then return end
	-- r2 (13/11): nascia no centro do corpo (dentro do alvo) e nao aparecia; agora nasce no alto do corpo
	local topo = Instance.new("Attachment"); topo.Name = "ToxinaFerrao_Topo"
	topo.WorldPosition = r.Position + Vector3.new(0, m:GetExtentsSize().Y * 0.45, 0); topo.Parent = r
	local p = Instance.new("ParticleEmitter"); p.Name = "ToxinaFerrao_Vapor"
	p.Texture = TEXTURA
	p.Color = ColorSequence.new(Color3.fromRGB(150, 210, 70), Color3.fromRGB(90, 140, 40))
	p.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.25, 0.55), NumberSequenceKeypoint.new(1, 1)})
	local grande = m:GetAttribute("GuardiaoNinho") or m:GetAttribute("FormaRegional")
	p.Size = grande and NumberSequence.new({NumberSequenceKeypoint.new(0, 2.5), NumberSequenceKeypoint.new(1, 6)})
		or NumberSequence.new({NumberSequenceKeypoint.new(0, 1.2), NumberSequenceKeypoint.new(1, 3)})
	p.Lifetime = NumberRange.new(0.8, 1.4); p.Rate = grande and 10 or 8
	p.Speed = NumberRange.new(1.5, 3); p.SpreadAngle = Vector2.new(35, 35)
	p.EmissionDirection = Enum.NormalId.Top; p.Acceleration = Vector3.new(0, 1.5, 0)
	p.LightEmission = 0.15; p.LightInfluence = 0.8
	p.Parent = topo
	ativos[m] = p
end
local function desligar(m)
	local p = ativos[m]; if not p then return end
	ativos[m] = nil; p.Enabled = false
	task.delay(1.5, function() p.Parent:Destroy() end)
end
for _, m in ipairs(CS:GetTagged(TAG)) do ligar(m) end
CS:GetInstanceAddedSignal(TAG):Connect(ligar)
CS:GetInstanceRemovedSignal(TAG):Connect(desligar)
