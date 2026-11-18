"""Streamlines of flow past a cylinder with a Karman-like vortex row -> 64x64 SVG icon."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = sys.argv[1]
x0, x1, y0, y1 = -1.25, 3.25, -2.25, 2.25          # square domain
a, U = 0.55, 1.0                                     # cylinder radius, free stream
vort = [(1.35, 0.5, -3.0), (2.3, -0.5, 3.0), (3.25, 0.5, -3.0)]  # (x, y, Gamma)

n = 500
X, Y = np.meshgrid(np.linspace(x0, x1, n), np.linspace(y0, y1, n))
R2 = X**2 + Y**2
psi = U * Y * (1 - a**2 / np.maximum(R2, 1e-9))
for xv, yv, g in vort:
    psi += g / (2 * np.pi) * np.log(np.sqrt((X - xv) ** 2 + (Y - yv) ** 2) + 1e-6)
psi[R2 < a**2] = np.nan

fig = plt.figure()
base = list(np.linspace(-2.1, 2.1, 9))
extra = []
def psi_at(px, py):
    i = np.argmin(abs(Y[:, 0] - py)); j = np.argmin(abs(X[0] - px)); return psi[i, j]
for xv, yv, g in vort[:2]:
    for rr in (0.16, 0.32):
        extra.append(psi_at(xv + rr, yv))
levels = sorted(set(round(v, 4) for v in base + extra if np.isfinite(v)))
cs = plt.contour(X, Y, psi, levels=levels)
plt.close(fig)

def to_px(x, y):
    return (x - x0) / (x1 - x0) * 64, (y1 - y) / (y1 - y0) * 64

paths = []
for lev, segs in zip(cs.levels, cs.allsegs):
    for seg in segs:
        if len(seg) < 8:
            continue
        pts = [to_px(px, py) for px, py in seg[:: max(1, len(seg) // 120)]]
        length = sum(np.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1))
        if length < 6:
            continue
        d = "M" + " L".join("%.1f %.1f" % p for p in pts)
        color = "#ffffff" if abs(lev) < 0.9 or round(lev,4) in [round(e,4) for e in extra] else "#7fbde6"
        paths.append('<path d="%s" stroke="%s"/>' % (d, color))

cx, cy = to_px(0, 0)
r = a / (x1 - x0) * 64
svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <defs><clipPath id="c"><rect width="64" height="64" rx="12"/></clipPath></defs>
  <rect width="64" height="64" rx="12" fill="#0b3954"/>
  <g clip-path="url(#c)" fill="none" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round">
    %s
  </g>
  <circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ffb347"/>
</svg>
""" % ("\n    ".join(paths), cx, cy, r)
open(out, "w").write(svg)
print(len(paths), "paths")
