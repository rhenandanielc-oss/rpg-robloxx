-- SUBSTITUIDO no piloto de 04/11/2026 (nao usado): o place principal tem HttpEnabled=false. Ver studio/AdaptadorUrso.luau e studio/TestePlayUrso.luau.
-- tocar_urso_play.luau (Studio, durante o PLAY, lado servidor) - toca um clipe do urso SEM publicar:
-- AnimationClipProvider:RegisterAnimationClip(kfs) gera um id temporario valido so no Studio.
-- Andar: move o modelo a 3,23 studs/s (PARAMETRO TECNICO da simulacao do Blender, NAO velocidade oficial do jogo).
local CLIPE, VEL, DUR = ...   -- ex.: "Urso_Andar", 3.23, 6
local modelo = workspace.Teste_Urso_v2:FindFirstChildWhichIsA("Model")
local kfs = game.ReplicatedStorage.Animacoes_Urso_v2[CLIPE]
local ac = modelo:FindFirstChildWhichIsA("AnimationController", true) or Instance.new("AnimationController", modelo)
local animator = ac:FindFirstChildWhichIsA("Animator") or Instance.new("Animator", ac)
for _, tr in ipairs(animator:GetPlayingAnimationTracks()) do tr:Stop(0) end
local a = Instance.new("Animation"); a.AnimationId = game:GetService("AnimationClipProvider"):RegisterAnimationClip(kfs)
local tr = animator:LoadAnimation(a); tr:Play(0)
if VEL and VEL > 0 then
	local ini = modelo:GetPivot(); local t0 = os.clock()
	local con; con = game:GetService("RunService").Heartbeat:Connect(function()
		local t = os.clock() - t0
		if t > (DUR or 6) then con:Disconnect(); return end
		modelo:PivotTo(ini * CFrame.new(0, 0, 0) + ini.LookVector * VEL * t)
	end)
end
return tr.Length
