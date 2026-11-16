-- conferir_giro_v41.luau (Edit, so leitura do modelo; nada e gravado no place)
-- Compara a ORIENTACAO COMPLETA de cada osso (nao so a ponta) contra o Blender (json_v41/matrizes_v41.json).
-- G: Blender armature -> Roblox mundo; M_b = (G*B_rest)^-1 * W_rest (constante por osso, mede a convencao do import).
-- Esperado numa pose: W = G * B_pose * M_b. Candidatos: biblioteca montada, basis bruto e basis com giro180y.
local H = game:GetService("HttpService")
local KSP = game:GetService("KeyframeSequenceProvider")
local low = workspace.Teste_LoboArtico.LoboArtico_LOW
local an = low.AnimationController:FindFirstChildOfClass("Animator") or Instance.new("Animator", low.AnimationController)
local MZ = H:JSONDecode(H:GetAsync("http://127.0.0.1:8766/json_v41/matrizes_v41.json"))
local function cfm(m) return CFrame.new(m[1][4], m[2][4], m[3][4], m[1][1], m[1][2], m[1][3], m[2][1], m[2][2], m[2][3], m[3][1], m[3][2], m[3][3]) end
local ossos = {}
for _, b in ipairs(low:GetDescendants()) do if b:IsA("Bone") then ossos[b.Name] = b; b.Transform = CFrame.identity end end
local G = CFrame.fromMatrix(low:GetPivot().Position, Vector3.new(-1, 0, 0), Vector3.new(0, 0, 1), Vector3.new(0, 1, 0))
local M, out = {}, {}
local mInfo = {}
for n, b in pairs(ossos) do
	M[n] = (G * cfm(MZ.rest[n])):Inverse() * b.TransformedWorldCFrame
	local ax, ang = M[n]:ToAxisAngle()
	table.insert(mInfo, string.format("%s:%.0f@(%.1f,%.1f,%.1f) t=%.3f", n, math.deg(ang), ax.X, ax.Y, ax.Z, M[n].Position.Magnitude))
end
table.sort(mInfo)
local function ang(a, b) local _, x = a:ToObjectSpace(b):ToAxisAngle(); return math.deg(math.abs(x)) end
local function medir(kfs, t, chave)
	-- Stop no Edit nao tira a faixa da mistura (o tempo nao anda): recria o Animator para medir uma faixa so
	local ac = an.Parent; an:Destroy(); an = Instance.new("Animator"); an.Parent = ac
	for _, b in pairs(ossos) do b.Transform = CFrame.identity end
	local a = Instance.new("Animation"); a.AnimationId = KSP:RegisterKeyframeSequence(kfs)
	local tr = an:LoadAnimation(a); local t0 = os.clock()
	while tr.Length == 0 and os.clock() - t0 < 2 do task.wait() end
	tr:Play(0); tr.TimePosition = t; an:StepAnimations(0)
	local ativas = #an:GetPlayingAnimationTracks()
	local pa, pp, onde = 0, 0, ""
	for n, b in pairs(ossos) do
		local esp = G * cfm(MZ.poses[chave][n]) * M[n]
		local w = b.TransformedWorldCFrame
		local e = ang(esp, w); local d = (esp.Position - w.Position).Magnitude
		if e > pa then pa = e; onde = n end
		pp = math.max(pp, d)
	end
	tr:Stop(0); an:StepAnimations(0); tr:Destroy()
	return string.format("ang=%.1f (%s) pos=%.3f faixas=%d", pa, onde, pp, ativas)
end
local function kfsJson(nome, f, modo)
	local js = H:JSONDecode(H:GetAsync("http://127.0.0.1:8766/json_v41/LoboArtico_" .. nome .. ".json"))
	local kfs = Instance.new("KeyframeSequence")
	local kf = Instance.new("Keyframe"); kf.Time = 0; kf.Parent = kfs
	local function rec(bone, parent)
		local d = js.ossos[bone.Name]; local o = f * 7
		local p = Instance.new("Pose"); p.Name = bone.Name
		if modo == "giro" then p.CFrame = CFrame.new(-d[o+5], d[o+6], -d[o+7], -d[o+1], d[o+2], -d[o+3], d[o+4])
		else p.CFrame = CFrame.new(d[o+5], d[o+6], d[o+7], d[o+1], d[o+2], d[o+3], d[o+4]) end
		p.Parent = parent
		for _, c in ipairs(bone:GetChildren()) do if c:IsA("Bone") then rec(c, p) end end
	end
	local topo = Instance.new("Pose"); topo.Name = "RootPart"; topo.Parent = kf
	rec(ossos.Raiz, topo)
	return kfs
end
local lib = game.ReplicatedStorage.Animacoes_LoboArtico
for chave in pairs(MZ.poses) do
	local nome, f = chave:match("(%w+)|(%d+)"); f = tonumber(f)
	table.insert(out, string.format("%s q%d | biblioteca %s | bruto %s | giro %s", nome, f,
		medir(lib["LoboArtico_" .. nome], f / 30, chave), medir(kfsJson(nome, f, "bruto"), 0, chave), medir(kfsJson(nome, f, "giro"), 0, chave)))
	task.wait()
end
return "M por osso (graus@eixo, translacao):\n" .. table.concat(mInfo, " ") .. "\n\n" .. table.concat(out, "\n")
