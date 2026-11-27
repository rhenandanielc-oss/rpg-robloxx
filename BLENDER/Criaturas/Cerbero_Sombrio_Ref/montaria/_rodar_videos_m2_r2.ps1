param([string]$vista = 'lado', [string]$janelas = '')
$b = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
foreach ($c in @(@('Montar', 271), @('Desmontar', 274))) {
  if ($janelas -ne '') { $q = $janelas.Split(';')[[int]($c[0] -eq 'Desmontar')] }
  else { $q = (0..($c[1] - 1) | Where-Object { $_ % 2 -eq 0 } | ForEach-Object { $_ + 1 }) -join ',' }
  $env:S2_QUADROS = $q; $env:S2_VISTAS = $vista; $env:S2_CLIPES = $c[0]; $env:S2_PAUSA = '0.5'
  $p = Start-Process -FilePath $b -ArgumentList '-b','-t','1','montaria/CB_M2_montaria_r2.blend','-P','montaria/m2_render_montaria.py','--','montaria/review_m2_r2','E,D','540' -NoNewWindow -PassThru -RedirectStandardOutput ("montaria/log_m2r2_video_" + $vista + "_" + $c[0] + ".txt") -RedirectStandardError ("montaria/log_m2r2_video_" + $vista + "_" + $c[0] + "_err.txt")
  $p.PriorityClass = 'Idle'; $p.WaitForExit()
}
