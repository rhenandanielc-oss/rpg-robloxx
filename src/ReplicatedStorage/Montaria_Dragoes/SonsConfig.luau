-- SonsConfig (ModuleScript) — audio dos dragoes. SO audio licenciado: biblioteca Pro Sound Effects publicada na Roblox
-- ("Courtesy of Pro Sound Effects", conta ProSoundEffects) e sons do proprio motor (rbxasset://). Nada copiado de jogos.
-- Volumes/tons provisorios (NAO_APROVADO). corte = segundos ate parar (trecho util de um arquivo longo).
local function id(n) return "rbxassetid://" .. n end
return {
	NAO_APROVADO = true,
	distMax = 260,
	asa = {id(9120771864), id(9120776877)},        -- Wing Flaps 27 / 1 (SFX): "Large Flying Creature"
	asaVolume = 0.9, asaTom = {0.75, 0.9},
	passo = {"rbxasset://sounds/action_footsteps_plastic.mp3"}, passoTom = {0.42, 0.55}, passoVolume = 0.9,
	passoPeso = id(9118633669), passoPesoCorte = 0.35, passoPesoVolume = 0.35,   -- Rock Impacts Deep Crunchy Hits 11
	mordida = {id(9125467298), id(9125466463)},   -- Creature Bite Pterodactyl Crunch (SFX)
	mordidaTom = {0.7, 0.85},
	avanco = id(9126229255),                         -- Whoosh By Fast Airy Swooshing (SFX)
	fogo = id(9114463219),                           -- Flame Licks 8 (SFX)
	ar = id(9125805579),                             -- Rising Whoosh Hissing Build Up (SFX)
	rocha = id(9118633669), rochaArrasto = id(9125881604),   -- Rock Impacts / Rock Scrape (SFX)
	rugido = id(9113985445),                         -- Creature Roar Deep Throaty Growls 2 (SFX)
	respiro = id(9113971531), respiroVolume = 0.35, respiroTom = {0.55, 0.7},   -- Creature Growls Lion 4: Deep Quiet Breathy (SFX)
	respiroIntervalo = {7, 15},                      -- segundos entre respiracoes audiveis (parado/andando), nunca regular
	esforco = id(9125467848), esforcoVolume = 0.55,  -- Creature Growls Lion Deep Guttural Rumbling (SFX): esforco curto
	garra = id(9119228132), garraVolume = 0.9,       -- Slow Whoosh Beefy Airy Pass By 5 (SFX): deslocamento do golpe
	impacto = id(9118633669), impactoCorte = 0.3,    -- Rock Impacts Deep Crunchy: so quando ACERTA
	maxSimultaneos = 6,                              -- por dragao (evita sobreposicao)
}
