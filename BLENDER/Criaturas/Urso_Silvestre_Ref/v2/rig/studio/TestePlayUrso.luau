-- TestePlayUrso (ModuleScript em ServerStorage.Urso_v2_Piloto) - toca os clipes do urso durante o PLAY, SEM publicar:
-- AnimationClipProvider:RegisterAnimationClip(kfs) gera um id temporario valido so no Studio.
-- Um ensaio por vez: tocar() sempre chama parar() antes (desliga a conexao do deslocamento, para as faixas,
-- volta o modelo a posicao inicial). Ao encerrar o Play o DataModel de teste e descartado.
-- Deslocamento do Andar: 3,23 studs/s = PARAMETRO TECNICO da simulacao do Blender, NAO velocidade oficial do jogo.
local RS = game:GetService("RunService")
local ACP = game:GetService("AnimationClipProvider")
local M = {}
local modelo = workspace:WaitForChild("Teste_Urso_v2"):WaitForChild("Urso_Silvestre_v2_Piloto")
local ANIM = game.ServerStorage.Urso_v2_Piloto.Animacoes
local PIVO0 = modelo:GetPivot()
local estado = {con = nil, faixa = nil, ids = {}}

local function animator()
	local ac = modelo:FindFirstChildOfClass("AnimationController")
	local an = ac:FindFirstChildOfClass("Animator") or Instance.new("Animator")
	an.Parent = ac
	return an
end

function M.parar()
	if estado.con then estado.con:Disconnect(); estado.con = nil end
	for _, f in ipairs(animator():GetPlayingAnimationTracks()) do f:Stop(0) end
	estado.faixa = nil
	modelo:PivotTo(PIVO0)
end

-- vel em studs/s ao longo da frente do modelo (LookVector do pivo); dur em s (o deslocamento para sozinho)
function M.tocar(nome, vel, dur, velocidadeClipe)
	M.parar()
	local kfs = ANIM[nome]
	estado.ids[nome] = estado.ids[nome] or ACP:RegisterAnimationClip(kfs)
	local a = Instance.new("Animation"); a.AnimationId = estado.ids[nome]
	local f = animator():LoadAnimation(a)
	f:Play(0, 1, velocidadeClipe or 1)
	estado.faixa = f
	-- num Play novo a 1a faixa demora a carregar (Length = 0 e TimePosition parado): espera ate 5 s
	local c0 = os.clock()
	while f.Length == 0 and os.clock() - c0 < 5 do task.wait() end
	if vel and vel > 0 then
		-- deslocamento amarrado ao TEMPO DA FAIXA (s = vel * tempo acumulado do clipe), como na simulacao do Blender.
		-- Medido no piloto (04/11): com os.clock a pata apoiada derivava 0,08-0,18 por apoio; amarrado a faixa, 0,012-0,049.
		local frente = PIVO0.LookVector; local acc, ult = 0, f.TimePosition
		estado.con = RS.Stepped:Connect(function()
			local tp = f.TimePosition; local d = tp - ult; if d < -0.5 * f.Length then d += f.Length end; ult = tp
			acc += d
			if dur and acc > dur then estado.con:Disconnect(); estado.con = nil; return end
			modelo:PivotTo(PIVO0 + frente * (vel * acc))
		end)
	end
	return {id = estado.ids[nome], duracao = f.Length, loop = f.Looped}
end

function M.info()
	local f = estado.faixa
	return {tocando = f and f.IsPlaying or false, tempo = f and f.TimePosition or 0, conexao = estado.con ~= nil,
		pivo = modelo:GetPivot().Position, faixas = #animator():GetPlayingAnimationTracks()}
end
return M
