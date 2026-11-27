$b = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$env:CERB_MONTARIA = '1'
$p = Start-Process -FilePath $b -ArgumentList '-b','-t','1','rig/CR_Cerbero_Rig.blend','-P','rig/anim_cerbero.py','--','montaria/clipes_m2_r2','MontarE,MontarD,DesmontarE,DesmontarD' -NoNewWindow -PassThru -RedirectStandardOutput montaria/log_clipes_m2_r2.txt -RedirectStandardError montaria/log_clipes_m2_r2_err.txt
$p.PriorityClass = 'Idle'; $p.WaitForExit()
$p = Start-Process -FilePath $b -ArgumentList '-b','-t','1','montaria/CB_M1_sela.blend','-P','montaria/m2_demo_montaria.py','--','montaria/clipes_m2_r2/CR_Cerbero_Anim.blend','montaria/CB_M2_montaria_r2.blend','montaria/m2_qa_r2.json' -NoNewWindow -PassThru -RedirectStandardOutput montaria/log_m2_demo_r2.txt -RedirectStandardError montaria/log_m2_demo_r2_err.txt
$p.PriorityClass = 'Idle'; $p.WaitForExit()
