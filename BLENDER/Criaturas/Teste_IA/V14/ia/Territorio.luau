-- IA_Dragao/Territorio — ninho, ovo e registro de guardioes (servidor).
-- Um ninho tem UM guardiao (registro global impede dupla atribuicao). Coleta do ovo por ProximityPrompt:
-- o INICIO da coleta sempre alerta o guardiao (regra oficial); a conclusao e validada no servidor e trava antes de
-- qualquer espera, entao o ovo nunca e concedido duas vezes. Nenhum RemoteEvent: o cliente nao escolhe alvo/estado.
local ServerStorage = game:GetService("ServerStorage")
local T = {}
T.__index = T

local donos = {}                                 -- ninhoId -> guardiaoId

local function eventos()
	local p = ServerStorage:FindFirstChild("IA_Eventos")
	if not p then p = Instance.new("Folder"); p.Name = "IA_Eventos"; p.Parent = ServerStorage end
	for _, n in ipairs({"OvoColetado", "AtaqueSolicitado", "GuardiaoAtacado"}) do
		if not p:FindFirstChild(n) then local e = Instance.new("BindableEvent"); e.Name = n; e.Parent = p end
	end
	return p
end
T.Eventos = eventos()

function T.novo(ninho, cfg)
	local self = setmetatable({}, T)
	self.ninho, self.cfg = ninho, cfg
	self.id = ninho:GetAttribute("NinhoId") or ninho:GetFullName()
	self.ovo = ninho:FindFirstChild("Ovo")
	self.centro = (self.ovo or ninho.PrimaryPart or ninho:FindFirstChildWhichIsA("BasePart")).Position
	self.forma = ninho:GetAttribute("FormaRegional")
	self.Alerta = Instance.new("BindableEvent")       -- (alvo: Model, motivo: "coleta"|"coletou"|"ataque")
	self.travado = false
	if self.ovo then
		if self.ovo:GetAttribute("Estado") == nil then self.ovo:SetAttribute("Estado", "Presente") end
		local pp = self.ovo:FindFirstChildOfClass("ProximityPrompt") or Instance.new("ProximityPrompt")
		pp.ActionText = "Coletar ovo"; pp.ObjectText = "Ovo"; pp.HoldDuration = cfg.coletaSegundos
		pp.MaxActivationDistance = cfg.coletaDist; pp.RequiresLineOfSight = false; pp.Parent = self.ovo
		pp.Enabled = self:ovoPresente()
		self.prompt = pp
		pp.PromptButtonHoldBegan:Connect(function(plr)
			if self:ovoPresente() and plr.Character then self.Alerta:Fire(plr.Character, "coleta") end
		end)
		pp.Triggered:Connect(function(plr) self:tentarColetar(plr) end)
	end
	return self
end

function T:atribuir(guardiaoId)
	local atual = donos[self.id]
	if atual and atual ~= guardiaoId then
		error(("ninho %s ja pertence ao guardiao %s (tentativa: %s)"):format(self.id, atual, guardiaoId))
	end
	donos[self.id] = guardiaoId
	self.ninho:SetAttribute("Guardiao", guardiaoId)
end
function T:liberar(guardiaoId) if donos[self.id] == guardiaoId then donos[self.id] = nil; self.ninho:SetAttribute("Guardiao", nil) end end
function T.dono(ninhoId) return donos[ninhoId] end

function T:ovoPresente() return self.ovo ~= nil and self.ovo:GetAttribute("Estado") == "Presente" end

-- Validacao no servidor; trava ANTES de qualquer yield.
function T:tentarColetar(plr)
	if self.travado or not self:ovoPresente() then return false, "indisponivel" end
	local ch = plr.Character
	local hum = ch and ch:FindFirstChildOfClass("Humanoid"); local hrp = ch and ch:FindFirstChild("HumanoidRootPart")
	if not (hum and hum.Health > 0 and hrp) then return false, "personagem invalido" end
	if (hrp.Position - self.ovo.Position).Magnitude > self.cfg.coletaDist + 4 then return false, "longe" end
	self.travado = true
	self.ovo:SetAttribute("Estado", "Coletado"); self.ovo:SetAttribute("ColetadoPor", plr.UserId)
	self.ovo.Transparency = 1; self.ovo.CanCollide = false
	if self.prompt then self.prompt.Enabled = false end
	self.ninho:SetAttribute("Ativo", false)          -- reaparecimento (30-60 min, oficial) fica com o sistema de ninhos
	T.Eventos.OvoColetado:Fire(plr, self.forma, self.id)
	self.Alerta:Fire(ch, "coletou")
	return true
end
return T
