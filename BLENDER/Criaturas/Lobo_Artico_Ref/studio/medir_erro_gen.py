# Gera Luau (Edit) que toca cada clipe por Animator:StepAnimations e devolve o pior desvio contra o Blender.
# Uso: python medir_erro_gen.py <clipes,...> <fonte: importado|corrigido> [flip]
import json, sys
r = json.load(open('json_v41/rest_v41.json'))
clipes = sys.argv[1].split(','); fonte = sys.argv[2]; flip = len(sys.argv) > 3
L = "Cabeca=1.56518, Mandibula=1.08703, Dedos_E=0.46152, Dedos_D=0.48715, DedosPe_E=0.48285, DedosPe_D=0.40998, Quadril=1.16977, Cauda4=1.17277"
ref = []
for c in clipes:
    am = []
    n = len(r['pontos'][c]['Cabeca'])
    for i in range(n):
        f = r['pontos'][c]['Cabeca'][i][0]
        pts = ", ".join("%s=Vector3.new(%.4f,%.4f,%.4f)" % (p, -v[i][1], v[i][3], v[i][2] + 0.708) for p, v in r['pontos'][c].items())
        am.append("{t=%.5f, %s}" % (f / 30, pts))
    ref.append('%s={%s}' % (c, ", ".join(am)))
pasta = 'low.AnimSaves.Value[c]' if fonte == 'importado' else 'game.ReplicatedStorage.Animacoes_LoboArtico["LoboArtico_" .. c]'
print("""local L = {%s}
local REF = {%s}
local low = workspace.Teste_LoboArtico.LoboArtico_LOW
local an = low.AnimationController:FindFirstChildOfClass("Animator")
local base = low:FindFirstChild("Raiz", true).WorldPosition
local out = {}
for c, ams in pairs(REF) do
  local ac = an.Parent; an:Destroy(); an = Instance.new("Animator"); an.Parent = ac   -- uma faixa so por medicao
  for _, b in ipairs(low:GetDescendants()) do if b:IsA("Bone") then b.Transform = CFrame.identity end end
  local a = Instance.new("Animation"); a.AnimationId = game:GetService("KeyframeSequenceProvider"):RegisterKeyframeSequence(%s)
  local tr = an:LoadAnimation(a); local t0 = os.clock()
  while tr.Length == 0 and os.clock() - t0 < 2 do task.wait() end
  tr:Play(0); an:StepAnimations(0); local pior, onde = 0, ""
  for _, am in ipairs(ams) do
    tr.TimePosition = math.min(am.t, tr.Length - 1e-4); an:StepAnimations(0)
    for n, l in pairs(L) do
      local p = (low:FindFirstChild(n, true).TransformedWorldCFrame * CFrame.new(0, l, 0)).Position - base
      %s
      local d = (p - am[n]).Magnitude
      if d > pior then pior = d; onde = string.format("%%s t=%%.2f", n, am.t) end
    end
  end
  tr:Stop(0); an:StepAnimations(0); tr:Destroy()
  table.insert(out, string.format("%%s %%.4f %%s len=%%.3f", c, pior, onde, tr.Length))
end
table.sort(out); return table.concat(out, string.char(10))""" % (L, ", ".join(ref), pasta, "p = Vector3.new(-p.X, -p.Y, p.Z)" if flip else ""))
