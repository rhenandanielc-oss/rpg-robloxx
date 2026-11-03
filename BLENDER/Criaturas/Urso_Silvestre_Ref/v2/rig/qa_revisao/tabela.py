import json, sys
A=json.load(open('qa_antes.json',encoding='utf-8')); D=json.load(open('qa_depois.json',encoding='utf-8'))
def der(c): 
    s=c.get('sola_mundo',{}); return max([v['deriva_max_studs'] for v in s.values()] or [0])
def chao(c,r): return c.get('chao_por_regiao',{}).get(r,{}).get('prof_max',0)
def pk(c): p=c.get('picos_aceleracao',[]); return len(p)
regs=['garra/dedo','sola','cotovelo/antebraco','cotovelo/braco','joelho/canela','calcanhar','punho','tronco','cabeca/pescoco']
L=["| Clipe | Deriva máx (antes→depois) | Garra | Sola | Cotovelo | Joelho | Tronco | Picos | Boca ext>3x |","|---|---|---|---|---|---|---|---|---|"]
for n in D['clipes']:
    a=A['clipes'].get(n,{}); d=D['clipes'][n]
    f=lambda r:"%.3f→%.3f"%(chao(a,r),chao(d,r))
    cot=lambda c:max(chao(c,'cotovelo/antebraco'),chao(c,'cotovelo/braco'))
    L.append("| %s | %.3f→%.3f | %s | %s | %.3f→%.3f | %.3f→%.3f | %s | %d→%d | %s→%s |"%(n,der(a),der(d),f('garra/dedo'),f('sola'),cot(a),cot(d),chao(a,'joelho/canela'),chao(d,'joelho/canela'),f('tronco'),pk(a),pk(d),a.get('boca_arestas_3x',{}).get('exterior','-'),d.get('boca_arestas_3x',{}).get('exterior','-')))
L+=["","| Transição | Salto pose ° | Afunda máx (antes→depois) |","|---|---|---|"]
for n,t in D['transicoes'].items():
    ta=A.get('transicoes',{}).get(n,{}); m=lambda x:max(x.get('chao_por_regiao',{}).values() or [0])
    L.append("| %s | %s→%s | %.3f→%.3f |"%(n,ta.get('salto_pose_graus','-'),t.get('salto_pose_graus'),m(ta),m(t)))
open('tabela_antes_depois.md','w',encoding='utf-8').write("\n".join(L)); print("\n".join(L))
