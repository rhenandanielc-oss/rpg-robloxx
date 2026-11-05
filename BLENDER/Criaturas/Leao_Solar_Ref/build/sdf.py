"""Campo de distancia (SDF) em grade numpy + extracao de superficie por surface nets. So numpy (roda no Blender).
Primitivas: elipsoide e cone arredondado (capsula com raios diferentes), uniao suave polinomial.
Cada primitiva so e avaliada dentro da sua caixa (mais a folga da uniao suave)."""
import numpy as np

class Campo:
    def __init__(self, lim, g):
        self.g = g; self.o = np.array([l[0] for l in lim], float)
        self.n = [int(np.ceil((l[1] - l[0]) / g)) + 1 for l in lim]
        self.F = np.full(self.n, 50.0, np.float32)
    def _bloco(self, lo, hi):
        i0 = np.clip(np.floor((np.array(lo) - self.o) / self.g).astype(int), 0, np.array(self.n) - 1)
        i1 = np.clip(np.ceil((np.array(hi) - self.o) / self.g).astype(int) + 1, 0, np.array(self.n))
        sl = tuple(slice(a, b) for a, b in zip(i0, i1))
        ax = [self.o[d] + self.g * np.arange(i0[d], i1[d]) for d in range(3)]
        X, Y, Z = np.meshgrid(*ax, indexing="ij")
        return sl, X, Y, Z
    def _unir(self, sl, d, k):
        a = self.F[sl]
        if k <= 0: self.F[sl] = np.minimum(a, d); return
        h = np.clip(k - np.abs(a - d), 0, None) / k
        self.F[sl] = np.minimum(a, d) - h * h * k * 0.25
    def subtrair(self, sl, d, k):
        a = self.F[sl]; h = np.clip(k - np.abs(-d - a), 0, None) / k if k > 0 else 0
        self.F[sl] = np.maximum(a, -d) + h * h * k * 0.25
    def elipsoide(self, c, r, k=0.0, menos=False):
        c = np.asarray(c, float); r = np.asarray(r, float); f = max(r) + k + self.g
        sl, X, Y, Z = self._bloco(c - f, c + f)
        px, py, pz = (X - c[0]) / r[0], (Y - c[1]) / r[1], (Z - c[2]) / r[2]
        k0 = np.sqrt(px * px + py * py + pz * pz)
        k1 = np.sqrt((px / r[0]) ** 2 + (py / r[1]) ** 2 + (pz / r[2]) ** 2) + 1e-9
        d = (k0 * (k0 - 1.0) / k1).astype(np.float32)
        (self.subtrair if menos else self._unir)(sl, d, k)
    def cone(self, a, b, r1, r2, k=0.0):
        a = np.asarray(a, float); b = np.asarray(b, float); f = max(r1, r2) + k + self.g
        sl, X, Y, Z = self._bloco(np.minimum(a, b) - f, np.maximum(a, b) + f)
        ba = b - a; l2 = ba @ ba; rr = r1 - r2; a2 = l2 - rr * rr; il2 = 1.0 / l2
        pax, pay, paz = X - a[0], Y - a[1], Z - a[2]
        y = pax * ba[0] + pay * ba[1] + paz * ba[2]; z = y - l2
        qx, qy, qz = pax * l2 - ba[0] * y, pay * l2 - ba[1] * y, paz * l2 - ba[2] * y
        x2 = qx * qx + qy * qy + qz * qz; y2 = y * y * l2; z2 = z * z * l2
        kk = np.sign(rr) * rr * rr * x2
        d = np.where(np.sign(z) * a2 * z2 > kk, np.sqrt(x2 + z2) * il2 - r2,
                     np.where(np.sign(y) * a2 * y2 < kk, np.sqrt(x2 + y2) * il2 - r1,
                              (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1))
        self._unir(sl, d.astype(np.float32), k)
    def cadeia(self, pts, k=0.0, k_ini=None):
        """pts: [(ponto, raio)]; uniao suave k entre segmentos (k_ini no primeiro, para soldar ao tronco)"""
        for i, ((a, ra), (b, rb)) in enumerate(zip(pts, pts[1:])):
            self.cone(a, b, ra, rb, k_ini if (i == 0 and k_ini is not None) else k)

def surface_nets(F, origem, g, nivel=0.0):
    """malha de quads da isosuperficie F=nivel (dentro < nivel). Retorna (verts Nx3, quads Mx4)."""
    F = F - nivel; nx, ny, nz = F.shape
    neg = F < 0
    c = [F[i:nx - 1 + i, j:ny - 1 + j, k:nz - 1 + k] for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    cn = [neg[i:nx - 1 + i, j:ny - 1 + j, k:nz - 1 + k] for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    algum = np.zeros(cn[0].shape, bool); todos = np.ones(cn[0].shape, bool)
    for a in cn: algum |= a; todos &= a
    ativo = algum & ~todos
    idx = np.argwhere(ativo)
    soma = np.zeros((len(idx), 3)); cont = np.zeros(len(idx))
    cs = [a[ativo] for a in c]
    off = [(i, j, k) for i in (0, 1) for j in (0, 1) for k in (0, 1)]
    for e0 in range(8):
        for e1 in range(e0 + 1, 8):
            d = np.subtract(off[e1], off[e0])
            if abs(d).sum() != 1: continue
            fa, fb = cs[e0], cs[e1]; m = (fa < 0) != (fb < 0)
            t = np.where(m, fa / np.where(m, fa - fb, 1), 0)
            soma[m] += np.asarray(off[e0])[None] + t[m, None] * d[None]; cont[m] += 1
    verts = origem + g * (idx + soma / np.maximum(cont, 1)[:, None])
    mapa = -np.ones(ativo.shape, np.int32); mapa[ativo] = np.arange(len(idx))
    quads = []
    for ax in range(3):
        sl0 = [slice(0, n) for n in F.shape]; sl1 = list(sl0)
        sl0[ax] = slice(0, F.shape[ax] - 1); sl1[ax] = slice(1, F.shape[ax])
        e = neg[tuple(sl0)] != neg[tuple(sl1)]
        dentro = neg[tuple(sl0)]
        o1, o2 = [a for a in range(3) if a != ax]
        sel = [slice(None)] * 3; sel[o1] = slice(1, -1); sel[o2] = slice(1, -1)
        e = e[tuple(sel)]; dentro = dentro[tuple(sel)]
        p = np.argwhere(e); p[:, o1] += 1; p[:, o2] += 1
        def cel(d1, d2):
            q = p.copy(); q[:, o1] -= d1; q[:, o2] -= d2
            q[:, ax] = np.minimum(q[:, ax], mapa.shape[ax] - 1)
            return mapa[q[:, 0], q[:, 1], q[:, 2]]
        a, b, cc, d = cel(1, 1), cel(0, 1), cel(0, 0), cel(1, 0)
        f = np.stack([a, b, cc, d], 1)
        inv = dentro[e]
        if (ax == 1): inv = ~inv
        f[inv] = f[inv][:, ::-1]
        quads.append(f[(f >= 0).all(1)])
    return verts, np.concatenate(quads)
