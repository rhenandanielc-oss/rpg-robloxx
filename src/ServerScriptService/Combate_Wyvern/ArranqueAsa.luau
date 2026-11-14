-- ArranqueAsa (ModuleScript, ServerScriptService.Combate_Wyvern) — passiva ARRANQUE DE ASA da Wyvern (kit aprovado pelo
-- usuario 13/11/2026). AUTORIDADE DO SERVIDOR.
-- Regra aprovada: ao passar de aceleracao DESLIGADA para LIGADA, aplica um impulso frontal curto se a recarga estiver pronta.
-- Recarga de 10 s contada desde o impulso. Aceleracao continua nao reativa (so a borda de subida conta). Durante a recarga
-- acelerar funciona normalmente e NAO agenda impulso. Para disparar de novo e preciso desacelerar e voltar a acelerar com a
-- recarga pronta.
-- r2 (usuario 13/11, ao aprovar a r1): impulso mais forte ("um impulso para frente mesmo") e TAMBEM no chao (a r1 so
-- disparava em voo). A recarga de 10 s e uma so para chao e ar.
-- Gancho: Montaria_Dragao_Servidor (PATCH_ARRANQUE_ASA) chama A.tentar(m, M, "voo"|"chao") na borda de subida do W/joystick
-- (voo livre e passo de chao); devolve o ganho de velocidade (studs/s) ou nil. O impulso decai pela desaceleracao normal do
-- controlador e respeita o teto de velocidade e as colisoes/bloqueios que ele ja faz.
-- Atributos para o cliente/HUD/teste: ArranqueAsaT (hora do servidor do ultimo impulso; dispara a aura), ArranqueAsaModo
-- ("voo"/"chao"), ArranqueAsaPronto (hora do servidor em que a recarga termina), ArranqueAsaN (contador, so teste).
local A = {}
A.CONFIG = {
	formas = {Wyvern = true},          -- formas com a passiva
	recarga = 10,                      -- s desde o impulso (APROVADO)
	-- r3 (13/11): o impulso parte da velocidade NORMAL de deslocamento (voo 34 / corrida da forma), nao da atual: de
	-- parado ou devagar ele ainda passa do normal ("um impulso para frente mesmo"); a r2 somava +25 no chao e caia de
	-- volta a corrida (17) em ~0,6 s. Pico = max(vel, normal) + impulso; o controlador traz de volta pela desaceleracao.
	impulso = {voo = 35, chao = 25},   -- studs/s acima da velocidade normal (PROVISORIO, balanceamento)
}
local function agora() return workspace:GetServerTimeNow() end
local CfgM = require(game:GetService("ReplicatedStorage"):WaitForChild("Montaria_Dragoes"):WaitForChild("ConfigMontaria"))
local function normal(m, modo)
	if modo == "chao" then return m:GetAttribute("VelCorrer") or CfgM.correrVel end
	return CfgM.vooVel
end

function A.tem(m) return m and A.CONFIG.formas[m:GetAttribute("FormaRegional") or ""] == true end

-- m = modelo montado; M = estado do controlador da montaria (so leitura aqui); modo = "voo" | "chao".
function A.tentar(m, M, modo)
	modo = modo or "voo"
	local ganho = A.CONFIG.impulso[modo]
	if not ganho or not A.tem(m) then return nil end
	if not m:GetAttribute("Cavaleiro") then return nil end                       -- so com controle de um jogador
	if m:GetAttribute("Incapacitado") or m:GetAttribute("EmAtaque") then return nil end
	if M and (M.picado or M.modo ~= modo) then return nil end                    -- voo normal ou chao (nao em transicao)
	local t = agora()
	if t < (m:GetAttribute("ArranqueAsaPronto") or 0) then return nil end       -- em recarga: nao agenda nada
	m:SetAttribute("ArranqueAsaPronto", t + A.CONFIG.recarga)
	m:SetAttribute("ArranqueAsaModo", modo)
	m:SetAttribute("ArranqueAsaT", t)
	m:SetAttribute("ArranqueAsaN", (m:GetAttribute("ArranqueAsaN") or 0) + 1)
	local v = (M and M.vel) or 0
	return math.max(v, normal(m, modo)) + ganho - v                            -- ganho real sobre a velocidade atual
end

return A
