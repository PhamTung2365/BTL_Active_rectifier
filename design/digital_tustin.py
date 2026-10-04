# -*- coding: utf-8 -*-
"""
PHAN 5 - DIEU KHIEN SO: roi rac hoa doi tuong va bo dieu khien theo xap xi Tustin
  1. Roi rac hoa doi tuong G_iv, G_vi (Tustin; doi chieu ZOH)
  2. Roi rac hoa bo dieu khien (Tustin, prewarp cho PR/Notch/SOGI): he so + phuong trinh sai phan
  3. Kiem tra on dinh trong mien z (PM, GM, cuc kin)
  4. Mo phong so sanh: bo dieu khien lien tuc (nguyen ly) <-> bo dieu khien so (Ts, ZOH, tre 1 mau)

Chay:  python digital_tustin.py   (ket qua -> digital_output.txt khi chuyen huong, hinh -> figures/)
"""
import os
import sys
import math
import numpy as np
from scipy import signal
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding="utf-8")
from params import *  # noqa: F401,F403

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.35,
                     "figure.dpi": 110, "savefig.dpi": 160})


# =====================================================================
# Cong cu
# =====================================================================
def c2d_tustin(num, den, Ts, wp=None):
    """Tustin s = K (z-1)/(z+1), K = 2/Ts hoac wp/tan(wp Ts/2) (prewarp).
    Tra ve (b, a) theo luy thua giam cua z (cung la he so cua z^0, z^-1, ...), a[0] = 1."""
    K = 2 / Ts if wp is None else wp / math.tan(wp * Ts / 2)
    n = max(len(num), len(den)) - 1
    num = np.concatenate([np.zeros(n + 1 - len(num)), num])
    den = np.concatenate([np.zeros(n + 1 - len(den)), den])
    zm1, zp1 = np.array([1.0, -1.0]), np.array([1.0, 1.0])
    bz = np.zeros(n + 1); az = np.zeros(n + 1)
    for i in range(n + 1):                       # he so cua s^(n-i)
        p = n - i
        term = np.array([K**p])
        for _ in range(p): term = np.convolve(term, zm1)
        for _ in range(n - p): term = np.convolve(term, zp1)
        bz += num[i] * term; az += den[i] * term
    return bz / az[0], az / az[0]


def c2d_zoh(num, den, Ts):
    b, a, _ = signal.cont2discrete((num, den), Ts, method="zoh")
    b = np.trim_zeros(np.atleast_1d(np.squeeze(b)), "f")
    return b / a[0], a / a[0]


def fr_s(tf, w):
    s = 1j * w
    return np.polyval(tf[0], s) / np.polyval(tf[1], s)


def fr_z(tf, w, T=Ts):
    z = np.exp(1j * w * T)
    return np.polyval(tf[0], z) / np.polyval(tf[1], z)


def margins(Lw, w):
    mag = np.abs(Lw); ph = np.unwrap(np.angle(Lw)) / deg
    k = np.where(np.diff(np.sign(mag - 1)) != 0)[0][-1]
    wc = np.interp(1, [mag[k + 1], mag[k]], [w[k + 1], w[k]])
    pm = 180 + np.interp(wc, w, ph)
    j = np.where((np.diff(np.sign(ph + 180)) != 0) & (w[:-1] > wc))[0]
    gm = -20 * np.log10(mag[j[0]]) if len(j) else np.inf
    return wc / 2 / np.pi, pm, gm


def zmul(*tfs):
    b, a = np.array([1.0]), np.array([1.0])
    for t in tfs:
        b = np.convolve(b, t[0]); a = np.convolve(a, t[1])
    return b, a


def fmt(v):
    return "[" + ", ".join(f"{x:.10g}" for x in v) + "]"


DELAY = (np.array([1.0]), np.array([1.0, 0.0]))    # z^-1 (tre tinh toan 1 chu ky)
w_lo = 2 * np.pi * np.logspace(0, np.log10(0.999 * fs / 2), 300000)

# =====================================================================
# 1. ROI RAC HOA DOI TUONG
# =====================================================================
print("=" * 72)
print(f"1. ROI RAC HOA DOI TUONG  (Ts = {Ts*1e6:.0f} us)")
print("=" * 72)
Giv_T = c2d_tustin(*PLANT_I, Ts)
Giv_Z = c2d_zoh(*PLANT_I, Ts)
Gvi_T = c2d_tustin(*PLANT_V, Ts)
Gvi_Z = c2d_zoh(*PLANT_V, Ts)
GviR_T = c2d_tustin(*PLANT_VR, Ts)
print("G_iv(s) = 1/(Ls + rL)")
print(f"  Tustin : b = {fmt(Giv_T[0])}, a = {fmt(Giv_T[1])}")
print(f"           = {Ts/(2*L+rL*Ts):.6e} (z+1) / (z - {(2*L-rL*Ts)/(2*L+rL*Ts):.7f})")
print(f"  ZOH    : b = {fmt(Giv_Z[0])}, a = {fmt(Giv_Z[1])}")
print(f"           = {(1-math.exp(-rL*Ts/L))/rL:.6e} / (z - {math.exp(-rL*Ts/L):.7f})")
print("G_vi(s) = Kv/s")
print(f"  Tustin : b = {fmt(Gvi_T[0])}, a = {fmt(Gvi_T[1])}  (= Kv Ts/2 (z+1)/(z-1))")
print(f"  ZOH    : b = {fmt(Gvi_Z[0])}, a = {fmt(Gvi_Z[1])}  (= Kv Ts/(z-1))")
print(f"G_vi,R(s) (tai R) Tustin: b = {fmt(GviR_T[0])}, a = {fmt(GviR_T[1])}")
for f_ in (50, 1000, 5000):
    w_ = 2 * np.pi * f_
    c = fr_s(PLANT_I, np.array([w_]))[0] * np.exp(-1j * w_ * Td)
    t = fr_z(zmul(Giv_T, DELAY), np.array([w_]))[0]
    zz = fr_z(zmul(Giv_Z, DELAY), np.array([w_]))[0]
    print(f"  f = {f_:5d} Hz: pha lien tuc*e^(-1.5sTs) = {np.angle(c)/deg:7.2f}, "
          f"Tustin*z^-1 = {np.angle(t)/deg:7.2f}, ZOH*z^-1 = {np.angle(zz)/deg:7.2f} deg; "
          f"|.| = {abs(c):.5f} / {abs(t):.5f} / {abs(zz):.5f}")

# =====================================================================
# 2. ROI RAC HOA BO DIEU KHIEN
# =====================================================================
print("\n" + "=" * 72)
print("2. ROI RAC HOA BO DIEU KHIEN THEO TUSTIN")
print("=" * 72)
K0 = w0 / math.tan(w0 * Ts / 2)
KN = wN / math.tan(wN * Ts / 2)
print(f"K = 2/Ts = {2/Ts:.4f};  K(prewarp 50 Hz) = {K0:.4f};  K(prewarp 100 Hz) = {KN:.4f}")
CTRL = {
    "PR ly tuong (prewarp 50 Hz)": c2d_tustin(*PR_IDEAL, Ts, w0),
    "PR khong ly tuong (prewarp 50 Hz)": c2d_tustin(*PR_NONID, Ts, w0),
    "PR khong ly tuong (KHONG prewarp)": c2d_tustin(*PR_NONID, Ts),
    "PI dien ap": c2d_tustin(*PI_V, Ts),
    "Notch 100 Hz (prewarp 100 Hz)": c2d_tustin(*NOTCH, Ts, wN),
    "SOGI D(z) (prewarp 50 Hz)": c2d_tustin(*SOGI_D, Ts, w0),
    "SOGI Q(z) (prewarp 50 Hz)": c2d_tustin(*SOGI_Q, Ts, w0),
    "PI PLL": c2d_tustin(*PI_PLL, Ts),
}
for k_, (b, a) in CTRL.items():
    print(f"{k_:36s}: b = {fmt(b)}")
    print(f"{'':36s}  a = {fmt(a)}")
PRz = CTRL["PR khong ly tuong (prewarp 50 Hz)"]
PRz_np = CTRL["PR khong ly tuong (KHONG prewarp)"]
PIz = CTRL["PI dien ap"]
NOz = CTRL["Notch 100 Hz (prewarp 100 Hz)"]
SDz = CTRL["SOGI D(z) (prewarp 50 Hz)"]
SQz = CTRL["SOGI Q(z) (prewarp 50 Hz)"]
PLLz = CTRL["PI PLL"]
NCO = (np.array([Ts]), np.array([1.0, -1.0]))       # theta[k+1] = theta[k] + Ts*w[k]

# Kiem tra bao toan dap ung tai tan so prewarp
for lab, tfc, tfz, f_ in [("PR", PR_NONID, PRz, 50), ("PR (khong prewarp)", PR_NONID, PRz_np, 50),
                          ("Notch", NOTCH, NOz, 100), ("SOGI-D", SOGI_D, SDz, 50), ("SOGI-Q", SOGI_Q, SQz, 50)]:
    w_ = np.array([2 * np.pi * f_])
    hc, hz = fr_s(tfc, w_)[0], fr_z(tfz, w_)[0]
    if abs(hc) < 1e-6:
        print(f"  {lab:20s} tai {f_} Hz: lien tuc |.| = {abs(hc):.1e} | so |.| = {abs(hz):.1e} (diem khong)")
    else:
        print(f"  {lab:20s} tai {f_} Hz: lien tuc {abs(hc):10.4f} /{np.angle(hc)/deg:7.2f} deg | "
              f"so {abs(hz):10.4f} /{np.angle(hz)/deg:7.2f} deg")
# Sai lech pha cua SOGI tan so co dinh khi luoi lech tan so
for f_ in (49.5, 50.5):
    print(f"  SOGI co dinh w0: pha D(j2pi{f_}) = "
          f"{np.angle(fr_s(SOGI_D, np.array([2 * np.pi * f_]))[0])/deg:+.3f} deg")
# Dich tan so cong huong khi khong prewarp
for h in (1, 3, 5, 7):
    fd = 2 / Ts * math.atan(h * w0 * Ts / 2) / 2 / np.pi
    fd5 = 2 * 5e3 * math.atan(h * w0 / 5e3 / 2) / 2 / np.pi
    print(f"  Cong huong bac {h}: khong prewarp -> {fd:.4f} Hz (fs=20kHz), {fd5:.3f} Hz (neu fs=5kHz)")
# Cuc cua PR so
print(f"  |cuc PR(z)| = {np.abs(np.roots(PRz[1]))}, goc = {np.angle(np.roots(PRz[1]))/(w0*Ts)} x w0Ts")

# =====================================================================
# 3. KIEM TRA ON DINH TRONG MIEN z
# =====================================================================
print("\n" + "=" * 72)
print("3. KIEM TRA ON DINH TRONG MIEN z")
print("=" * 72)
w_c = 2 * np.pi * np.logspace(0, 5, 300000)
Li_c0 = fr_s(PR_NONID, w_c) * fr_s(PLANT_I, w_c)
Li_cd = Li_c0 * np.exp(-1j * w_c * Td)
Li_zZ = fr_z(zmul(PRz, Giv_Z, DELAY), w_lo)
Li_zT = fr_z(zmul(PRz, Giv_T, DELAY), w_lo)
print("Vong dong (PR khong ly tuong):")
for lab, Lw, ww in [("lien tuc, khong tre", Li_c0, w_c), ("lien tuc, tre 1.5Ts", Li_cd, w_c),
                    ("so: PR_Tustin * G_ZOH * z^-1", Li_zZ, w_lo),
                    ("so: PR_Tustin * G_Tustin * z^-1", Li_zT, w_lo)]:
    fc, pm, gm = margins(Lw, ww)
    print(f"  {lab:34s}: fc = {fc:7.1f} Hz, PM = {pm:5.1f} deg, GM = {gm:5.1f} dB")
Lol = zmul(PRz, Giv_Z, DELAY)
char_i = np.polyadd(Lol[1], Lol[0])
poles_i = np.roots(char_i)
print(f"  Cuc kin (ZOH): {np.array2string(poles_i, precision=6)}")
print(f"  max|z| = {np.max(np.abs(poles_i)):.6f}  -> {'ON DINH' if np.max(np.abs(poles_i)) < 1 else 'KHONG ON DINH'}")
Ti_z = (Lol[0], char_i)                                   # ham truyen kin vong dong (so)

# Vong ap
Lv_c = fr_s(PI_V, w_lo) * fr_s(NOTCH, w_lo) * fr_s(PLANT_V, w_lo)
Lv_z = fr_z(PIz, w_lo) * fr_z(NOz, w_lo) * fr_z(Ti_z, w_lo) * fr_z(Gvi_Z, w_lo)
Lv_zR = fr_z(PIz, w_lo) * fr_z(NOz, w_lo) * fr_z(Ti_z, w_lo) * fr_z(c2d_zoh(*PLANT_VR, Ts), w_lo)
print("Vong ap:")
for lab, Lw in [("lien tuc PI*Notch*Kv/s", Lv_c), ("so PI_z*Notch_z*Ti_z*Gvi_ZOH", Lv_z),
                ("so, tai R 80 Ohm", Lv_zR)]:
    fc, pm, gm = margins(Lw, w_lo)
    print(f"  {lab:34s}: fc = {fc:6.2f} Hz, PM = {pm:5.1f} deg, GM = {gm:5.1f} dB")
Lv_ol = zmul(PIz, NOz, Ti_z, Gvi_Z)
poles_v = np.roots(np.polyadd(Lv_ol[1], Lv_ol[0]))
print(f"  max|z| cuc kin vong ap = {np.max(np.abs(poles_v)):.7f}")
# PLL
Lp_c = Vm * fr_s(PI_PLL, w_lo) / (1j * w_lo)
Lp_z = Vm * fr_z(PLLz, w_lo) * fr_z(NCO, w_lo)
print("Vong PLL (tuyen tinh hoa):")
for lab, Lw in [("lien tuc", Lp_c), ("so (PI Tustin + NCO Euler)", Lp_z)]:
    fc, pm, gm = margins(Lw, w_lo)
    print(f"  {lab:34s}: fc = {fc:6.2f} Hz, PM = {pm:5.1f} deg, GM = {gm:5.1f} dB")

# =====================================================================
# HINH: doi tuong, bo dieu khien, vong ho
# =====================================================================
def bode2(ax, w, H, label, f_hz=True, **kw):
    f = w / 2 / np.pi
    ax[0].semilogx(f, 20 * np.log10(np.abs(H)), label=label, **kw)
    ax[1].semilogx(f, np.unwrap(np.angle(H)) / deg, label=label, **kw)


def finish(fig, ax, title, fname, ylim_m=None, ylim_p=None, nyq=True):
    ax[0].set_ylabel("Biên độ (dB)"); ax[1].set_ylabel("Pha (độ)"); ax[1].set_xlabel("Tần số (Hz)")
    ax[0].set_title(title)
    if ylim_m: ax[0].set_ylim(*ylim_m)
    if ylim_p: ax[1].set_ylim(*ylim_p)
    if nyq:
        for a in ax: a.axvline(fs / 2, color="k", lw=0.7, ls=":")
        ax[0].text(fs / 2, ax[0].get_ylim()[1], " fs/2", va="top", fontsize=8)
    ax[0].legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FIG, fname)); plt.close(fig)


wf = 2 * np.pi * np.logspace(1, np.log10(0.999 * fs / 2), 20000)
fig, ax = plt.subplots(2, 1, figsize=(7.5, 6), sharex=True)
bode2(ax, wf, fr_s(PLANT_I, wf) * np.exp(-1j * wf * Td), r"liên tục $\cdot e^{-1.5sT_s}$", color="k", lw=2)
bode2(ax, wf, fr_z(zmul(Giv_Z, DELAY), wf), r"ZOH $\cdot z^{-1}$", color="C0", ls="--")
bode2(ax, wf, fr_z(zmul(Giv_T, DELAY), wf), r"Tustin $\cdot z^{-1}$", color="C3", ls="-.")
finish(fig, ax, r"Đối tượng vòng dòng $G_{iv}$: liên tục và rời rạc ($T_s$ = 50 µs)",
       "fig5_plant_discrete.png", (-80, -10), (-300, 0))

wp = 2 * np.pi * np.logspace(np.log10(40), np.log10(62), 20000)
fig, ax = plt.subplots(2, 1, figsize=(7.5, 5.5), sharex=True)
bode2(ax, wp, fr_s(PR_NONID, wp), "PR liên tục", color="k", lw=2)
bode2(ax, wp, fr_z(PRz, wp), "Tustin + prewarp 50 Hz", color="C0", ls="--")
bode2(ax, wp, fr_z(PRz_np, wp), "Tustin không prewarp", color="C3", ls=":")
finish(fig, ax, "Bộ PR: liên tục và rời rạc Tustin (phóng to quanh 50 Hz)",
       "fig5_PR_discrete.png", nyq=False)

fig, ax = plt.subplots(2, 1, figsize=(7.5, 6), sharex=True)
bode2(ax, w_c[w_c < 2 * np.pi * 1e4], Li_c0[w_c < 2 * np.pi * 1e4], "liên tục, không trễ", color="0.5")
bode2(ax, w_c[w_c < 2 * np.pi * 1e4], Li_cd[w_c < 2 * np.pi * 1e4], "liên tục, trễ 1,5$T_s$", color="k", lw=2)
bode2(ax, w_lo, Li_zZ, r"số: PR$_z\cdot G_{ZOH}\cdot z^{-1}$", color="C0", ls="--")
for a in ax: a.axvline(fc_i, color="C2", lw=0.7, ls=":")
ax[0].axhline(0, color="k", lw=0.7); ax[1].axhline(-180, color="k", lw=0.7)
finish(fig, ax, "Vòng hở dòng điện: liên tục và số", "fig5_current_loop_z.png", (-40, 80), (-360, 0))

fig, ax = plt.subplots(2, 1, figsize=(7.5, 6), sharex=True)
m_ = w_lo < 2 * np.pi * 3000
bode2(ax, w_lo[m_], Lv_c[m_], "liên tục PI·Notch·Kv/s", color="k", lw=2)
bode2(ax, w_lo[m_], Lv_z[m_], r"số PI$_z$·Notch$_z$·$T_{i,z}$·$G_{vi,ZOH}$", color="C0", ls="--")
ax[0].axhline(0, color="k", lw=0.7); ax[1].axhline(-180, color="k", lw=0.7)
finish(fig, ax, "Vòng hở điện áp: liên tục và số", "fig5_voltage_loop_z.png", (-80, 80), (-300, 0), nyq=False)


# =====================================================================
# 4. MO PHONG SO SANH: LIEN TUC (nguyen ly) <-> SO (Tustin, ZOH, tre 1 mau)
# =====================================================================
class IIR:
    """Bo loc IIR dang Direct Form II Transposed: y = b/a."""
    def __init__(self, b, a):
        self.b = [float(x) for x in b]; self.a = [float(x) for x in a]
        self.n = len(self.a) - 1; self.s = [0.0] * self.n

    def step(self, x):
        b, a, s = self.b, self.a, self.s
        y = b[0] * x + (s[0] if self.n else 0.0)
        for i in range(self.n - 1):
            s[i] = b[i + 1] * x - a[i + 1] * y + s[i + 1]
        if self.n:
            s[self.n - 1] = b[self.n] * x - a[self.n] * y
        return y


class PIaw:
    """PI Tustin + chong bao hoa tich phan (clamping): u = Kp e + xi, xi[k] = xi[k-1] + Ki Ts/2 (e[k]+e[k-1])."""
    def __init__(self, Kp, Ki, T, umin, umax):
        self.Kp, self.Ki, self.T, self.lo, self.hi = Kp, Ki, T, umin, umax
        self.xi = 0.0; self.ep = 0.0

    def step(self, e):
        xi_new = self.xi + self.Ki * self.T / 2 * (e + self.ep)
        u = self.Kp * e + xi_new
        if not ((u > self.hi and e > 0) or (u < self.lo and e < 0)):
            self.xi = xi_new
        self.ep = e
        return min(max(self.Kp * e + self.xi, self.lo), self.hi)


EVENTS = [(0.40, "R", R_load), (0.60, "U", U_min), (0.80, "U", U_max), (0.95, "f", 50.5)]
T_END = 1.15
DT = Ts / 25
Vref0, t_ramp = 0.95 * Vm, 0.15


def simulate(digital):
    n = int(round(T_END / DT)); dec = 5
    rec = {k: np.zeros((n + dec - 1) // dec) for k in ("t", "i", "iref", "v", "e", "Im", "th")}
    i = 0.0; v = 0.95 * Vm; thg = 0.0
    U, R, fg = U_n, 2 * R_load, f_n
    m_apply = 0.0
    if digital:
        nsub = int(round(Ts / DT))
        pr = IIR(*PRz); notch = IIR(*NOz); sd = IIR(*SDz); sq = IIR(*SQz)
        piv = PIaw(Kp_v, Ki_v, Ts, 0.0, Im_max)
        pll = PIaw(Kp_pll, Ki_pll, Ts, -2 * np.pi * 5, 2 * np.pi * 5)
        th = 0.0; m_next = 0.0; iref = 0.0; Im = 0.0
    else:
        x1 = x2 = 0.0; xi_v = 0.0; n1 = n2 = 0.0; sa = sb = 0.0; th = 0.0; xi_p = 0.0
    for k in range(n):
        t = k * DT
        for (te, key, val) in EVENTS:
            if abs(t - te) < DT / 2:
                if key == "U": U = val
                if key == "R": R = val
                if key == "f": fg = val
        thg += 2 * np.pi * fg * DT
        e = math.sqrt(2) * U * math.sin(thg)
        vref = Vref0 + (Vdc - Vref0) * min(t / t_ramp, 1.0)
        if digital:
            if k % nsub == 0:                     # thoi diem lay mau (dinh song mang)
                m_apply = m_next                  # cap nhat PWM bang ket qua tinh o chu ky truoc
                # --- SOGI-PLL ---
                vp = sd.step(e); qv = sq.step(e)
                eq = vp * math.cos(th) + qv * math.sin(th)
                w_ = w0 + pll.step(eq)
                iref_th = th
                th = (th + Ts * w_) % (2 * np.pi)
                # --- vong ap ---
                vf = notch.step(v)
                Im = piv.step(vref - vf)
                iref = Im * math.sin(iref_th)
                # --- vong dong ---
                uL = pr.step(iref - i)
                m_next = min(max((e - uL) / v, -1.0), 1.0)
        else:
            err = (e - sa) * k_sogi
            dsa = (err - sb) * w0; dsb = sa * w0
            eq = sa * math.cos(th) + sb * math.sin(th)
            xi_p += Ki_pll * eq * DT
            th += (w0 + Kp_pll * eq + xi_p) * DT
            sa += dsa * DT; sb += dsb * DT
            dn1 = n2; dn2 = -wN**2 * n1 - (wN / Q_N) * n2 + v
            vf = v - (wN / Q_N) * n2
            n1 += dn1 * DT; n2 += dn2 * DT
            ev = vref - vf
            Im_un = Kp_v * ev + xi_v
            Im = min(max(Im_un, 0.0), Im_max)
            if Im == Im_un or (Im_un > Im_max and ev < 0) or (Im_un < 0 and ev > 0):
                xi_v += Ki_v * ev * DT
            iref = Im * math.sin(th)
            ei = iref - i
            dx1 = x2; dx2 = -w0**2 * x1 - 2 * wrc * x2 + ei
            uL = Kp_i * ei + Kr_i * x2
            x1 += dx1 * DT; x2 += dx2 * DT
            m_apply = min(max((e - uL) / v, -1.0), 1.0)
        # mach luc (mo hinh trung binh)
        di = (e - rL * i - m_apply * v) / L
        dv = (m_apply * i - v / R) / C
        i += di * DT; v += dv * DT
        if k % dec == 0:
            j = k // dec
            rec["t"][j] = t; rec["i"][j] = i; rec["iref"][j] = iref; rec["v"][j] = v
            rec["e"][j] = e; rec["Im"][j] = Im; rec["th"][j] = th
    return rec


def metrics(r, t0, t1, f0=50.0):
    """Phan tich Fourier tren dung 5 chu ky luoi (so nguyen chu ky -> khong ro pho)."""
    t = r["t"]; t1 = t0 + 5 / f0
    m = (t >= t0) & (t < t1)
    ii, ee, tt = r["i"][m], r["e"][m], t[m]

    def harm(x, h):
        return 2 * np.mean(x * np.exp(-1j * 2 * np.pi * h * f0 * tt))
    I1, E1 = harm(ii, 1), harm(ee, 1)
    hs = [abs(harm(ii, h)) for h in range(2, 40)]
    thd = math.sqrt(sum(x * x for x in hs)) / abs(I1) * 100
    phi = (np.angle(I1) - np.angle(E1)) / deg
    phi = (phi + 180) % 360 - 180
    return dict(V=r["v"][m].mean(), Vpp=r["v"][m].max() - r["v"][m].min(), THD=thd, phi=phi,
                PF=math.cos(phi * deg) / math.sqrt(1 + (thd / 100) ** 2), I1=abs(I1) / math.sqrt(2))


print("\n" + "=" * 72)
print("4. MO PHONG SO SANH (mo hinh trung binh; lien tuc = nguyen ly, so = Tustin + ZOH + z^-1)")
print("=" * 72)
R_c = simulate(False)
R_d = simulate(True)
wins = [("50% tai, 220 V, 50 Hz", 0.30, 0.40), ("100% tai, 220 V", 0.50, 0.60),
        ("100% tai, 198 V", 0.70, 0.80), ("100% tai, 242 V", 0.85, 0.95),
        ("100% tai, 242 V, 50.5 Hz", 1.04, 1.14)]
print(f"{'che do':26s} | {'lien tuc: Vdc  Vpp  THD%  phi  PF':38s} | {'so: Vdc  Vpp  THD%  phi  PF'}")
for lab, t0, t1 in wins:
    f0 = 50.5 if t0 > 0.95 else 50.0
    a = metrics(R_c, t0, t1, f0); b = metrics(R_d, t0, t1, f0)
    print(f"{lab:26s} | {a['V']:6.1f} {a['Vpp']:5.2f} {a['THD']:5.2f} {a['phi']:5.2f} {a['PF']:.4f}   "
          f"| {b['V']:6.1f} {b['Vpp']:5.2f} {b['THD']:5.2f} {b['phi']:5.2f} {b['PF']:.4f}")
for lab, r in [("lien tuc", R_c), ("so", R_d)]:
    t = r["t"]; m = (t > 0.40) & (t < 0.6)
    vmin = r["v"][m].min(); k = np.argmax(m) + np.argmin(r["v"][m])
    after = (t > t[k]) & (t < 0.6)
    rec_t = t[after][np.argmax(np.abs(r["v"][after] - Vdc) < 0.02 * Vdc + 3.7)] - 0.40
    m2 = (t > 0.0) & (t < 0.4)
    print(f"  {lab:8s}: nhay tai -> Vdc min = {vmin:6.1f} V (sut {Vdc - vmin:4.1f} V); "
          f"khoi dong: Vdc max = {r['v'][m2].max():6.1f} V, |i|max = {np.abs(r['i'][m2]).max():5.1f} A")
# sai lech giua 2 mo phong
tc = R_c["t"]; m = tc > 0.3
print(f"  max|Vdc_lien tuc - Vdc_so| (t>0.3s) = {np.max(np.abs(R_c['v'][m] - R_d['v'][m])):.2f} V; "
      f"max|i_lien tuc - i_so| = {np.max(np.abs(R_c['i'][m] - R_d['i'][m])):.3f} A")

fig, ax = plt.subplots(3, 1, figsize=(8.5, 8))
ax[0].plot(R_c["t"], R_c["v"], lw=1.0, color="k", label="liên tục (nguyên lý)")
ax[0].plot(R_d["t"], R_d["v"], lw=0.9, color="C0", ls="--", label="số (Tustin, $T_s$ = 50 µs)")
ax[0].set_ylabel("$v_{dc}$ (V)"); ax[0].set_ylim(290, 425); ax[0].legend(fontsize=8, loc="lower right")
for te, key, _ in EVENTS: ax[0].axvline(te, color="0.4", lw=0.6, ls=":")
ax[0].set_xlabel("t (s)")
ax[0].set_title("Tải 50→100% @0,4 s; lưới 198 V @0,6 s; 242 V @0,8 s; 50,5 Hz @0,95 s", fontsize=9)
for a, (t0, t1, ttl) in zip(ax[1:], [(0.38, 0.46, "Quanh thời điểm nhảy tải"), (0.94, 1.0, "Lưới nhảy tần số 50 → 50,5 Hz")]):
    for r, c, ls, lb in [(R_c, "k", "-", "$i_s$ liên tục"), (R_d, "C0", "--", "$i_s$ số")]:
        m = (r["t"] > t0) & (r["t"] < t1)
        a.plot(r["t"][m], r["i"][m], color=c, ls=ls, lw=1.0, label=lb)
    m = (R_d["t"] > t0) & (R_d["t"] < t1)
    a.plot(R_d["t"][m], R_d["e"][m] / 20, color="C1", lw=0.8, label="$e_n$/20")
    a.set_ylabel("A, V/20"); a.set_title(ttl, fontsize=9); a.legend(fontsize=8, loc="upper right", ncol=3)
ax[2].set_xlabel("t (s)")
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig5_sim_compare.png")); plt.close(fig)
print("\nDa luu hinh vao", FIG)

# =====================================================================
# HINH: gian do thoi gian lay mau - tinh toan - cap nhat PWM
# =====================================================================
fig, ax = plt.subplots(figsize=(9, 3.6))
tt = np.linspace(0, 3, 3001)
carrier = 2 * np.abs((tt % 1) - 0.5) * 2 - 1           # tam giac, dinh tai k*Ts
ax.plot(tt, carrier, color="0.3", lw=1.2, label="sóng mang PWM (20 kHz)")
ax.step([0, 1, 2, 3], [0.45, 0.05, 0.3, 0.3], where="post", color="C0", lw=2, label="$m$ áp dụng (ZOH)")
for x_, y_, lb in [(0.5, 0.45, "$m_{k-1}$"), (1.5, 0.05, "$m_k$"), (2.5, 0.3, "$m_{k+1}$")]:
    ax.text(x_, y_ + 0.06, lb, ha="center", va="bottom", fontsize=10, color="C0")
for k in range(4):
    ax.annotate("", xy=(k, -1.05), xytext=(k, -1.45), arrowprops=dict(arrowstyle="-|>", color="C3"))
    ax.text(k, -1.6, f"lấy mẫu\n$k{'+' + str(k) if k else ''}$".replace("k+", "k+"), ha="center", va="top", fontsize=8.5, color="C3")
ax.add_patch(plt.Rectangle((0.05, 1.15), 0.6, 0.25, color="C2", alpha=0.35))
ax.text(0.35, 1.275, "tính toán ($m_k$)", ha="center", va="center", fontsize=8.5)
ax.annotate("", xy=(1, 1.0), xytext=(0.65, 1.27), arrowprops=dict(arrowstyle="-|>", color="C2"))
ax.text(1.04, 1.3, "cập nhật PWM bằng $m_k$ tại $(k+1)T_s$", fontsize=8.5, va="center")
ax.annotate("", xy=(1.5, -0.62), xytext=(0, -0.62), arrowprops=dict(arrowstyle="<->", color="k"))
ax.text(0.75, -0.55, r"$T_d \approx T_s$ (tính toán) $+\,0{,}5T_s$ (ZOH/PWM) $=1{,}5T_s=75$ µs",
        ha="center", va="bottom", fontsize=9)
ax.set_xlim(-0.2, 3.2); ax.set_ylim(-2.1, 1.6); ax.set_yticks([])
ax.set_xticks([0, 1, 2, 3]); ax.set_xticklabels(["$kT_s$", "$(k+1)T_s$", "$(k+2)T_s$", "$(k+3)T_s$"])
ax.legend(fontsize=8, loc="upper right"); ax.grid(False)
ax.set_title("Giản đồ thời gian điều khiển số: lấy mẫu đồng bộ đỉnh sóng mang, cập nhật ở chu kỳ sau", fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig5_timing.png")); plt.close(fig)
