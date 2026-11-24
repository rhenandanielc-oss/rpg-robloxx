-- criar_aura_A4.luau (20/11): troca as chamas da aura r6 (AuraA3_*/AuraExtra_*) pelas ~90 chamas da A4 (Blender aprovada).
-- Rodar em Edit no Cerbero-testes. Backup: ServerStorage.Cerbero_ANTES_A4_2026-11-20. Brasas mantidas.
-- Dados: aura_A4_sitios.lua {osso, x, y, z (Blender, mundo, Raiz na origem), altura, largura, zona, filha}
local CH = {{"PescocoD2",2.270,-8.022,15.729,8.35,1.90,"juba",1},{"PescocoE2",-5.676,-8.013,16.565,5.91,2.13,"juba",1},{"PescocoC1",-0.800,-3.586,15.179,5.71,2.29,"juba",1},{"PescocoC2",-1.314,-9.119,18.876,7.91,2.66,"juba",1},{"PescocoC1",-1.259,-7.987,12.879,6.99,2.37,"juba",1},{"PescocoD1",3.240,-5.871,12.893,4.26,2.37,"juba",1},{"PescocoE1",-4.022,-5.295,15.416,5.54,2.59,"juba",1},{"PescocoC2",-0.535,-6.076,17.709,6.36,2.78,"juba",1},{"PescocoE2",-3.026,-9.278,15.092,5.58,2.31,"juba",1},{"PescocoD2",4.914,-6.746,15.220,7.20,2.25,"juba",1},{"PescocoD1",2.540,-5.047,15.598,7.18,2.65,"juba",1},{"PescocoD1",1.230,-7.642,11.507,6.37,2.77,"juba",1},{"PescocoE2",-4.193,-8.049,13.444,8.08,2.52,"juba",1},{"PescocoC2",-0.390,-8.827,14.667,5.21,2.70,"juba",1},{"PescocoE2",-3.131,-8.936,17.147,6.80,2.10,"juba",1},{"PescocoC2",0.872,-8.292,17.154,5.33,2.43,"juba",1},{"PescocoD1",1.747,-7.955,13.403,7.20,1.91,"juba",1},{"PescocoC1",0.580,-5.706,16.196,7.96,2.39,"juba",1},{"PescocoC1",-1.624,-5.044,15.653,5.82,2.49,"juba",1},{"PescocoD2",4.256,-6.550,16.761,6.82,2.55,"juba",1},{"PescocoC2",0.339,-9.012,18.648,6.55,2.16,"juba",1},{"PescocoD2",2.223,-6.379,16.519,5.84,2.79,"juba",1},{"PescocoC2",-1.972,-7.822,17.429,7.29,2.64,"juba",1},{"PescocoE2",-5.538,-7.839,14.335,6.89,2.16,"juba",1},{"PescocoE2",-4.074,-7.659,16.821,7.20,2.29,"juba",1},{"PescocoC2",-0.721,-7.709,18.607,6.95,2.29,"juba",1},{"PescocoE1",-1.730,-7.465,14.246,5.22,2.03,"juba",1},{"PescocoE2",-3.411,-6.342,16.387,4.67,2.26,"juba",1},{"PescocoD2",2.984,-9.112,14.967,7.95,2.25,"juba",1},{"PescocoD2",3.451,-8.747,16.321,7.24,2.14,"juba",1},{"PescocoD2",2.995,-7.944,13.973,5.36,2.39,"juba",1},{"PescocoD2",3.675,-5.768,15.472,4.89,1.91,"juba",1},{"PescocoE1",-2.793,-8.193,14.108,6.21,2.30,"juba",1},{"PescocoE1",-4.562,-5.984,14.537,6.81,2.48,"juba",1},{"EscapulaE",-3.961,-4.578,14.379,4.08,1.59,"ombro",1},{"EscapulaD",1.059,-1.832,13.842,2.90,1.58,"ombro",1},{"EscapulaE",-4.332,-7.039,10.903,3.18,1.66,"ombro",1},{"EscapulaE",-5.543,-4.062,10.616,3.45,1.52,"ombro",1},{"EscapulaE",-2.470,-3.124,14.930,3.80,1.77,"ombro",1},{"EscapulaE",-4.592,-3.775,11.991,3.04,1.89,"ombro",1},{"Coluna3",0.558,-7.463,9.590,3.93,1.66,"peito",1},{"Coluna3",0.237,-4.770,7.783,3.09,1.73,"peito",1},{"Coluna3",-2.310,-7.445,9.970,2.38,1.69,"peito",1},{"Coluna3",-0.285,-8.113,12.075,3.36,1.64,"peito",1},{"Coluna3",-1.354,-7.588,11.121,3.66,1.77,"peito",1},{"Coluna3",-0.721,-7.165,8.923,3.30,1.56,"peito",1},{"Coluna3",-0.615,-7.687,10.120,3.35,1.78,"peito",1},{"Coluna3",-0.681,-5.526,7.819,2.58,1.46,"peito",1},{"Coluna1",-2.904,3.468,11.708,6.72,2.00,"dorso",1},{"Coluna2",-0.220,-4.684,7.240,2.86,1.68,"dorso",1},{"Coluna2",0.862,-1.074,13.602,3.84,2.23,"dorso",1},{"Coluna1",-1.222,0.904,7.758,1.48,2.58,"dorso",1},{"Coluna2",-3.121,-1.389,12.006,2.30,1.55,"dorso",1},{"Coluna1",2.200,1.602,10.265,2.00,1.79,"dorso",1},{"Coluna1",0.365,4.319,12.445,4.95,1.61,"dorso",1},{"Coluna2",2.400,-1.619,10.098,3.48,2.06,"dorso",1},{"Coluna2",-2.515,-1.481,7.667,3.12,1.54,"dorso",1},{"Coluna1",-0.363,1.983,12.927,2.87,2.01,"dorso",1},{"Coluna2",-0.659,-2.628,6.453,3.42,2.26,"dorso",1},{"Coluna2",-2.315,-3.651,7.477,3.00,1.89,"dorso",1},{"Coluna1",-3.052,0.209,10.535,2.22,1.86,"dorso",1},{"Coluna1",-3.812,2.439,10.472,3.82,1.80,"dorso",1},{"Coluna2",-0.790,-0.902,6.502,5.69,1.98,"dorso",1},{"Pelve",-0.834,5.670,12.000,3.56,1.82,"quadril",1},{"Pelve",0.136,7.025,9.874,2.94,1.92,"quadril",1},{"Pelve",1.166,5.150,11.311,3.42,1.90,"quadril",1},{"Pelve",-1.521,5.952,9.919,3.38,1.49,"quadril",1},{"Pelve",-1.350,4.515,12.040,2.67,1.76,"quadril",1},{"Pelve",-0.457,6.636,11.475,3.04,1.65,"quadril",1},{"Pelve",-0.074,4.953,12.164,3.46,1.51,"quadril",1},{"Pelve",0.953,5.791,10.563,2.57,1.67,"quadril",1},{"Cauda1",-0.371,9.186,9.147,4.95,1.53,"cauda",1},{"Cauda3",-0.495,11.606,9.532,4.48,1.41,"cauda",1},{"Cauda1",0.126,7.335,9.731,4.75,1.70,"cauda",1},{"Cauda3",-1.300,10.667,8.214,4.35,1.57,"cauda",1},{"Cauda2",-0.242,9.634,7.411,3.64,1.31,"cauda",1},{"Cauda1",-1.382,8.074,8.842,3.50,1.71,"cauda",1},{"Cauda3",-0.032,10.709,8.621,3.67,1.80,"cauda",1},{"BracoD",3.351,-5.527,7.937,2.55,0.91,"perna",1},{"CanelaE",-3.966,5.595,5.683,2.06,1.09,"perna",1},{"BracoE",-5.138,-3.782,7.346,2.26,0.93,"perna",1},{"CoxaD",1.937,4.517,11.218,1.39,1.03,"perna",1},{"CanelaD",2.866,7.025,4.455,2.40,0.91,"perna",1},{"CoxaE",-2.778,5.417,10.419,1.64,0.92,"perna",1},{"CoxaE",-3.835,2.529,9.286,2.22,0.80,"perna",1},{"BracoE",-5.088,-5.739,9.621,2.11,0.82,"perna",1},{"CoxaD",2.767,3.757,9.195,1.67,1.00,"perna",1},{"BracoE",-4.387,-5.683,6.842,2.32,0.80,"perna",1},{"BracoD",3.395,-3.738,8.885,2.41,1.06,"perna",1},{"CoxaD",1.680,5.554,9.966,2.12,1.17,"perna",1}}
local m = workspace.Teste_Cerbero.Cerbero_Sombrio
local rp = m.RootPart; local raiz = m:FindFirstChild("Raiz", true)
for _, b in ipairs(m:GetDescendants()) do if b:IsA("Bone") then b.Transform = CFrame.identity end end
for _, o in ipairs(m:GetDescendants()) do if o:IsA("Bone") and (o.Name:match("^AuraA3_") or o.Name:match("^AuraExtra_") or o.Name:match("^AuraA4_")) then o:Destroy() end end
local r0 = rp.CFrame:PointToObjectSpace(raiz.WorldPosition)
local rnd = Random.new(2011)
local COR = ColorSequence.new({ColorSequenceKeypoint.new(0, Color3.fromRGB(255, 236, 160)), ColorSequenceKeypoint.new(0.18, Color3.fromRGB(255, 160, 40)),
  ColorSequenceKeypoint.new(0.55, Color3.fromRGB(235, 75, 10)), ColorSequenceKeypoint.new(1, Color3.fromRGB(110, 15, 5))})
local n = 0
for i, c in ipairs(CH) do
  local osso = m:FindFirstChild(c[1], true)
  local wp = rp.CFrame:PointToWorldSpace(r0 + Vector3.new(-c[2], c[4], c[3]))
  local zona, h, w = c[7], c[5], c[6]
  local inc = (zona == "dorso" or zona == "quadril") and 22 or 12
  local anc = Instance.new("Bone"); anc.Name = string.format("AuraA4_%02d_%s", i - 1, zona); anc.Parent = osso
  anc.WorldCFrame = CFrame.new(wp) * CFrame.Angles(math.rad(rnd:NextNumber(-inc, inc)), 0, math.rad(rnd:NextNumber(-inc, inc)))
  local pe = Instance.new("ParticleEmitter"); pe.Name = "Chama"
  pe.Texture = "rbxasset://textures/particles/fire_main.dds"
  pe.Color = COR; pe.LightEmission = 0.8; pe.LightInfluence = 0; pe.Brightness = 2.4
  pe.Orientation = Enum.ParticleOrientation.VelocityParallel
  pe.Squash = NumberSequence.new({NumberSequenceKeypoint.new(0, -0.6), NumberSequenceKeypoint.new(0.5, -1.4), NumberSequenceKeypoint.new(1, -0.8)})
  pe.Size = NumberSequence.new({NumberSequenceKeypoint.new(0, w * 0.55, w * 0.1), NumberSequenceKeypoint.new(0.35, w * 0.85, w * 0.15), NumberSequenceKeypoint.new(1, w * 0.18)})
  pe.Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.55), NumberSequenceKeypoint.new(0.12, 0.1), NumberSequenceKeypoint.new(0.6, 0.3), NumberSequenceKeypoint.new(1, 1)})
  pe.Lifetime = NumberRange.new(0.55, 0.85)
  pe.Rate = 4
  pe.Speed = NumberRange.new(h * 0.45, h * 0.7)
  pe.Acceleration = Vector3.new(0, h * 1.4, 0)
  pe.EmissionDirection = Enum.NormalId.Top; pe.SpreadAngle = Vector2.new(10, 10)
  pe.Rotation = NumberRange.new(-10, 10); pe.RotSpeed = NumberRange.new(-25, 25)
  pe.Drag = 1.2; pe.LockedToPart = false; pe.ZOffset = 0.4
  pe:SetAttribute("TaxaPC", 4); pe:SetAttribute("Zona", zona); pe:SetAttribute("SubidaBase", h * 1.4)
  pe.Parent = anc
  n += 1
end
m:SetAttribute("AuraA3", nil)
m:SetAttribute("AuraA4", "A4 20/11: " .. n .. " chamas (taxa 4/s) + brasas; inclina na corrida; Furia violeta por atributo")
m:SetAttribute("NumChamas", n)
m:SetAttribute("Furia", false)
local brasas = 0
for _, d in ipairs(m:GetDescendants()) do if d:IsA("ParticleEmitter") and d.Name == "Brasa" then brasas += 1 end end
return n .. " chamas, " .. brasas .. " brasas"

-- A4 r2 (20/11, visto no Play): chamas do corpo (menos juba e cauda) afastadas 1 stud do osso para nao sumirem dentro da
-- malha; peito, ombro e perna x1,4 no tamanho. Atributo AjusteA4r2 evita aplicar duas vezes.
for _, d in ipairs(m:GetDescendants()) do
  if d:IsA("ParticleEmitter") and d.Name == "Chama" and not d:GetAttribute("AjusteA4r2") then
    local z = d:GetAttribute("Zona")
    if z ~= "juba" and z ~= "cauda" then
      local anc, osso = d.Parent, d.Parent.Parent
      local dir = anc.WorldPosition - osso.WorldPosition
      dir = Vector3.new(dir.X, math.max(dir.Y, 0) * 0.5, dir.Z)
      if dir.Magnitude > 0.1 then anc.WorldCFrame = anc.WorldCFrame + dir.Unit * 1.0 end
    end
    if z == "perna" or z == "peito" or z == "ombro" then
      local ks = {} for _, k in ipairs(d.Size.Keypoints) do table.insert(ks, NumberSequenceKeypoint.new(k.Time, k.Value * 1.4, k.Envelope * 1.4)) end
      d.Size = NumberSequence.new(ks)
    end
    d:SetAttribute("AjusteA4r2", true)
  end
end

-- A4 r3 (23/11, pedido do usuario: "o fogo nao acompanha o corpo, fica para tras conforme o animal corre"):
-- chamas e brasas PRESAS ao corpo (LockedToPart); o script do cliente so inclina de leve (INCLINA_MAX 0,35).
for _, d in ipairs(m:GetDescendants()) do
  if d:IsA("ParticleEmitter") and (d.Name == "Chama" or d.Name == "Brasa") then d.LockedToPart = true end
end
