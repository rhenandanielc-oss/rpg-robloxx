# Prova de nao-interferencia: compara keyframes de TODAS as actions entre dois .blend (A = origem, B = nova versao).
# Uso: blender -b --factory-startup -P 09d_comparar_actions.py -- <A.blend> <B.blend> <saida.json>
import bpy, sys, json, hashlib
argv = sys.argv[sys.argv.index("--") + 1:]
def assinatura(path):
    with bpy.data.libraries.load(path) as (src, dst): dst.actions = list(src.actions)
    out = {}
    for a in dst.actions:
        h = hashlib.sha256()
        for L in a.layers:
            for s in L.strips:
                for cb in s.channelbags:
                    for f in sorted(cb.fcurves, key=lambda f: (f.data_path, f.array_index)):
                        co = [0.0] * (len(f.keyframe_points) * 2); f.keyframe_points.foreach_get("co", co)
                        h.update((f.data_path + str(f.array_index)).encode()); h.update(repr([round(x, 7) for x in co]).encode())
        out[a.name] = h.hexdigest()[:16]
        bpy.data.actions.remove(a)
    return out
A, B = assinatura(argv[0]), assinatura(argv[1])
R = {"iguais": sorted(n for n in A if B.get(n) == A[n]), "diferentes": sorted(n for n in A if n in B and B[n] != A[n]),
     "so_A": sorted(set(A) - set(B)), "so_B": sorted(set(B) - set(A))}
json.dump(R, open(argv[2], "w"), indent=1); print("CMP", json.dumps(R))
