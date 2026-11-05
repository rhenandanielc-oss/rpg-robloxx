import sys, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d = np.load(sys.argv[1]); out = sys.argv[2]
fig, ax = plt.subplots(1, 2, figsize=(16, 8))
for k, c in zip(["sx_0.0", "sx_0.4", "sx_0.8", "sx_1.2"], "kbgr"):
    s = d[k]
    for a in s: ax[0].plot([a[1], a[4]], [a[2], a[5]], c, lw=0.8)
    ax[0].plot([], [], c, label=k)
ax[0].plot([-13.96, -15.33], [12.23, 12.43], "m--", label="linha boca E3"); ax[0].plot([-12.75], [12.65], "mo")
ax[0].set_xlim(-16, -11); ax[0].set_ylim(9.8, 14.5); ax[0].set_aspect("equal"); ax[0].legend(); ax[0].grid(alpha=.3); ax[0].set_title("sagital (y,z)")
cm = plt.cm.viridis
ks = [k for k in d.files if k.startswith("sy_")]
for i, k in enumerate(ks):
    for a in d[k]: ax[1].plot([a[0], a[3]], [a[2], a[5]], color=cm(i / len(ks)), lw=0.8)
    ax[1].plot([], [], color=cm(i / len(ks)), label=k)
ax[1].set_xlim(-3, 3); ax[1].set_ylim(9.8, 14.5); ax[1].set_aspect("equal"); ax[1].legend(); ax[1].grid(alpha=.3); ax[1].set_title("transversal (x,z)")
plt.tight_layout(); plt.savefig(out, dpi=90)
