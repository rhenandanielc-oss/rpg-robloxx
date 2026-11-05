import json,sys
Ms=[(n,json.load(open(f))) for n,f in zip(sys.argv[1::2],sys.argv[2::2])]
print('%-22s'%'pose'+''.join('%30s'%n for n,_ in Ms))
for p in Ms[0][1]:
  f=lambda M:'%.2f %.2f %4d %.2f %6.2f'%(M[p]['zona']['espessura_p5'],M[p]['zona']['espessura_min'],M[p]['corpo']['arestas_esticadas_>1.5x_e_>0.05'],M[p]['corpo']['alongamento_abs_max'],M[p].get('volume_perdido_studs3',0))
  print('%-22s'%p+''.join('%30s'%f(M) for _,M in Ms))
