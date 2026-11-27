-- Ferramenta de Edit (26/11): alarga o tunel da toca AO LONGO de uma cadeia fixa (lista de pontos no chao), para o Ancião
-- (escala 1,1, degrau 1,98) caber. Por trecho bloqueado:
--   objeto (cristal etc.) -> afasta os 2 pontos 1,5 stud na normal (nao mexe no objeto);
--   terreno -> zera o voxel solido mais proximo do contato, so se: nao for piso (normal Y <= 0,6), o teto acima tiver >= 3 studs,
--   e o voxel de tras na direcao da parede continuar solido (nao abre buraco para fora); se nao for seguro, afasta os pontos.
-- O Filhote (0,4) so e medido no relatorio (degrau minimo 1,0 nao se resolve escavando). Faca backup TerrainRegion antes. Uso: loadstring(...)()(cadeia, limiteVoxels) -> relatorio; a cadeia e alterada no lugar.
return function(c, limiteVoxels)
	local T = workspace.Terrain
	local rpL = RaycastParams.new(); rpL.FilterType = Enum.RaycastFilterType.Exclude
	local ex = {}; for _, n in ipairs({"Criaturas_IA", "Teste_LoboArtico"}) do local o = workspace:FindFirstChild(n); if o then table.insert(ex, o) end end
	rpL.FilterDescendantsInstances = ex
	local rpT = RaycastParams.new(); rpT.FilterType = Enum.RaycastFilterType.Include; rpT.FilterDescendantsInstances = {T}
	local function chao(q) local r = workspace:Raycast(q + Vector3.new(0, 6, 0), Vector3.new(0, -20, 0), rpL); return r and r.Position end
	local function bate(i, e)
		local dg = math.max(1, 1.8 * e); local al = 6 * e - dg
		local a = c[i] + Vector3.new(0, dg + al / 2, 0); local b = c[i + 1] + Vector3.new(0, dg + al / 2, 0); local d = b - a
		if d.Magnitude < 0.2 then return nil end
		return workspace:Blockcast(CFrame.lookAt(a, b), Vector3.new(2 * e, al, 0.5), d, rpL)
	end
	local function occ(v) local reg = Region3.new(v * 4, v * 4 + Vector3.new(4, 4, 4)); local m, o = T:ReadVoxels(reg, 4); return o[1][1][1], reg, m, o end
	local empurros, abertos, parou = {}, 0, nil
	for passo = 1, 600 do
		local i, r
		for k = 1, #c - 1 do local h = bate(k, 1.1) or bate(k, 1.0); if h then i, r = k, h; break end end
		if not r then break end
		local function afastar(motivo)
			local n = Vector3.new(r.Normal.X, 0, r.Normal.Z); if n.Magnitude < 0.1 then parou = "t" .. i .. " " .. motivo .. " sem normal lateral"; return false end
			n = n.Unit; empurros[i] = (empurros[i] or 0) + 1
			if empurros[i] > 6 then parou = "t" .. i .. " nao afasta (" .. motivo .. ")"; return false end
			for _, k in ipairs({i, i + 1}) do local q = chao(c[k] + n * 1.5); if q and math.abs(q.Y - c[k].Y) < 2 then c[k] = q end end
			return true
		end
		if r.Instance ~= T then
			if not afastar(r.Instance:GetFullName()) then break end
		else
			if r.Normal.Y > 0.6 then parou = string.format("t%d degrau do piso em (%d,%.1f,%d)", i, r.Position.X, r.Position.Y, r.Position.Z); break end
			local piso = math.min(c[i].Y, c[i + 1].Y)
			local v0 = Vector3.new(math.floor(r.Position.X / 4), math.floor(r.Position.Y / 4), math.floor(r.Position.Z / 4))
			local melhor, mo = nil, 0.05
			for dx = -1, 1 do for dy = -1, 1 do for dz = -1, 1 do
				local v = v0 + Vector3.new(dx, dy, dz); local cy = v.Y * 4 + 2
				if cy > piso + 0.5 then local o = occ(v); if o > mo then melhor, mo = v, o end end
			end end end
			if not melhor then if afastar(string.format("sem voxel perto de (%d,%.1f,%d)", r.Position.X, r.Position.Y, r.Position.Z)) then continue else break end end
			local centro = melhor * 4 + Vector3.new(2, 2, 2)
			local top = workspace:Raycast(Vector3.new(centro.X, centro.Y + 200, centro.Z), Vector3.new(0, -199, 0), rpT)
			local seguro = not (top and top.Position.Y - (centro.Y + 2) < 3)
			local nh = Vector3.new(r.Normal.X, 0, r.Normal.Z)
			if nh.Magnitude > 0.5 then
				local atras = melhor - Vector3.new(math.round(nh.Unit.X), 0, math.round(nh.Unit.Z))
				if (atras - melhor).Magnitude > 0 and occ(atras) < 0.5 then seguro = false end
			end
			if not seguro then if afastar(string.format("rocha fina em (%d,%d,%d)", centro.X, centro.Y, centro.Z)) then continue else break end end
			local _, reg, m, o = occ(melhor); o[1][1][1] = 0; m[1][1][1] = Enum.Material.Air; T:WriteVoxels(reg, 4, m, o); abertos += 1
			if abertos >= (limiteVoxels or 60) then parou = "limite de voxels"; break end
		end
		if passo % 8 == 0 then task.wait() end
	end
	local nE = 0; for _ in pairs(empurros) do nE += 1 end
	local res = {}
	for _, e in ipairs({0.4, 1.0, 1.1}) do
		local lim, nota = #c, ""
		for k = 1, #c - 1 do local h = bate(k, e); if h then lim = k; nota = string.format(" %s (%d,%.0f,%d)", h.Instance.Name, h.Position.X, h.Position.Y, h.Position.Z); break end end
		table.insert(res, string.format("e%.1f %d/%d%s", e, lim, #c, nota))
	end
	return string.format("trechos afastados %d, voxels abertos %d, parou: %s | %s", nE, abertos, tostring(parou or "-"), table.concat(res, " | "))
end
