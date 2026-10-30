"""Le um GLB e calcula, por animacao/osso/quadro, a transformacao RELATIVA ao repouso (rest^-1 * anim), que e o
que o Roblox guarda em Pose.CFrame. Saida JSON: {anim: {"tempo": [...], "loop": true, "ossos": {nome: [[px,py,pz,qx,qy,qz,qw], ...]}}}.
Uso: python glb_poses.py arquivo.glb saida.json [anim1,anim2] [renomear.json]"""
import json, struct, sys, math

def ler_glb(caminho):
    b = open(caminho, "rb").read()
    n = struct.unpack_from("<I", b, 12)[0]
    j = json.loads(b[20:20 + n])
    off = 20 + n; bin_ = None
    while off < len(b):
        ln, tp = struct.unpack_from("<II", b, off)
        if tp == 0x004E4942: bin_ = b[off + 8: off + 8 + ln]
        off += 8 + ln
    return j, bin_

def acessar(j, bin_, i):
    a = j["accessors"][i]; bv = j["bufferViews"][a["bufferView"]]
    nc = {"SCALAR": 1, "VEC3": 3, "VEC4": 4}[a["type"]]
    assert a["componentType"] == 5126
    base = bv.get("byteOffset", 0) + a.get("byteOffset", 0); passo = bv.get("byteStride", 4 * nc)
    return [struct.unpack_from("<%df" % nc, bin_, base + k * passo) for k in range(a["count"])]

# quaternions (x,y,z,w)
def qmul(a, b):
    ax, ay, az, aw = a; bx, by, bz, bw = b
    return (aw * bx + ax * bw + ay * bz - az * by, aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw, aw * bw - ax * bx - ay * by - az * bz)
def qinv(q): x, y, z, w = q; n = x * x + y * y + z * z + w * w; return (-x / n, -y / n, -z / n, w / n)
def qrot(q, v):
    p = qmul(qmul(q, (v[0], v[1], v[2], 0.0)), qinv(q)); return p[:3]

def amostra(tempos, vals, t, quat):
    if t <= tempos[0]: return vals[0]
    if t >= tempos[-1]: return vals[-1]
    for k in range(len(tempos) - 1):
        if tempos[k] <= t <= tempos[k + 1]:
            u = (t - tempos[k]) / max(tempos[k + 1] - tempos[k], 1e-9); a, b = vals[k], vals[k + 1]
            if quat:
                d = sum(x * y for x, y in zip(a, b))
                if d < 0: b = tuple(-x for x in b)
                r = tuple(x + (y - x) * u for x, y in zip(a, b)); n = math.sqrt(sum(x * x for x in r)); return tuple(x / n for x in r)
            return tuple(x + (y - x) * u for x, y in zip(a, b))

def extrair(caminho, filtro=None, renomear=None):
    j, bin_ = ler_glb(caminho)
    nos = j["nodes"]; out = {}
    for an in j.get("animations", []):
        if filtro and an["name"] not in filtro: continue
        canais = {}; tmax = 0; tempos_todos = set()
        for c in an["channels"]:
            s = an["samplers"][c["sampler"]]; no = c["target"]["node"]; cam = c["target"]["path"]
            if cam not in ("translation", "rotation"): continue
            ts = [x[0] for x in acessar(j, bin_, s["input"])]; vs = acessar(j, bin_, s["output"])
            canais.setdefault(no, {})[cam] = (ts, vs); tmax = max(tmax, ts[-1]); tempos_todos.update(round(t, 5) for t in ts)
        tempos = sorted(tempos_todos)
        ossos = {}
        for no, cs in canais.items():
            nd = nos[no]; nome = nd.get("name", str(no)); nome = (renomear or {}).get(nome, nome)
            rT = nd.get("translation", [0, 0, 0]); rR = tuple(nd.get("rotation", [0, 0, 0, 1]))
            lst = []
            for t in tempos:
                T = amostra(*cs["translation"], t, False) if "translation" in cs else rT
                R = amostra(*cs["rotation"], t, True) if "rotation" in cs else rR
                # rel = rest^-1 * anim  (T_rest,R_rest)^-1 * (T,R) = (R_rest^-1 (T - T_rest), R_rest^-1 R)
                iR = qinv(rR); dp = qrot(iR, [T[0] - rT[0], T[1] - rT[1], T[2] - rT[2]]); dq = qmul(iR, R)
                lst.append([round(x, 6) for x in (*dp, *dq)])
            ossos[nome] = lst
        out[an["name"]] = {"tempo": tempos, "ossos": ossos}
    return out

if __name__ == "__main__":
    filtro = sys.argv[3].split(",") if len(sys.argv) > 3 and sys.argv[3] != "-" else None
    ren = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else None
    r = extrair(sys.argv[1], filtro, ren)
    json.dump(r, open(sys.argv[2], "w"))
    for k, v in r.items(): print("ANIM", k, len(v["tempo"]), "quadros", len(v["ossos"]), "ossos")
