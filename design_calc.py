# -*- coding: utf-8 -*-
"""
Tinh toan thiet ke he thong dieu khien chinh luu tich cuc 1 pha (EE4331 - Bai 26)
Phan 1: Bai toan thiet ke (kiem tra mach luc)
Phan 3: Mo hinh hoa, tong hop bo dieu chinh (PR dong dien, PI dien ap, Notch, SOGI-PLL)

Chay:  python design_calc.py
Ket qua: in bang so lieu ra man hinh + luu hinh vao thu muc figures/
"""
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")
import math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.35,
                     "figure.dpi": 110, "savefig.dpi": 160})

deg = np.pi / 180

# =====================================================================
# 1. THONG SO THIET KE
# =====================================================================
U_n, U_min, U_max = 220.0, 198.0, 242.0          # V rms
f_n, f_min, f_max = 50.0, 49.5, 50.5             # Hz
S = 2000.0                                       # VA (PF = 1 -> P = 2 kW)
L, rL = 5e-3, 0.1                                # H, Ohm
C = 2200e-6                                      # F
Vdc = 400.0                                      # V
fs = 20e3                                        # Hz  (tan so dong cat - tu chon)
Ts = 1 / fs
w0 = 2 * np.pi * f_n
Vm = np.sqrt(2) * U_n

P = S
I_n = P / U_n;       Ipk_n = np.sqrt(2) * I_n
I_max = P / U_min;   Ipk_max = np.sqrt(2) * I_max
R_load = Vdc**2 / P
I_load = P / Vdc

# Dap mach dong dien (dieu che don cuc - unipolar, tan so gon song 2fs)
dI_uni = Vdc / (8 * L * fs)          # dinh-dinh, lon nhat khi v = Vdc/2
dI_bi = Vdc / (2 * L * fs)           # dieu che luong cuc (so sanh)
# Gon song 100 Hz tren bus DC
dV_pp = P / (w0 * C * Vdc)
# Kiem tra he so dieu che: U_s = E - (rL + jwL) I  (PF = 1 phia luoi)
def conv_voltage(U, Pw, f=f_n):
    I = Pw / U
    Us = U - (rL + 1j * 2 * np.pi * f * L) * I
    return abs(Us) * np.sqrt(2), np.angle(Us) / deg
Us_pk_max, dlt_max = conv_voltage(U_max, P, f_max)
Us_pk_min, dlt_min = conv_voltage(U_min, P, f_min)
m_max = Us_pk_max / Vdc
# Dien ap / dong dien dat len van
V_sw = Vdc + dV_pp / 2
I_sw = Ipk_max + dI_uni / 2

print("=" * 70)
print("PHAN 1 - BAI TOAN THIET KE")
print("=" * 70)
print(f"Vm (dinh) danh dinh / min / max   = {Vm:.1f} / {np.sqrt(2)*U_min:.1f} / {np.sqrt(2)*U_max:.1f} V")
print(f"Dong luoi danh dinh I = {I_n:.2f} A rms, dinh {Ipk_n:.2f} A")
print(f"Dong luoi lon nhat (U=198V) = {I_max:.2f} A rms, dinh {Ipk_max:.2f} A")
print(f"Tai tuong duong R = {R_load:.1f} Ohm, I_load = {I_load:.2f} A")
print(f"fs = {fs/1e3:.0f} kHz: dap mach dong unipolar = {dI_uni:.3f} A pp ({dI_uni/Ipk_n*100:.1f}% dinh), "
      f"bipolar = {dI_bi:.2f} A pp")
print(f"Gon song 100Hz tren Vdc = {dV_pp:.2f} V pp ({dV_pp/Vdc*100:.2f}%)")
print(f"Us dinh can thiet (242V, 50.5Hz, 2kW) = {Us_pk_max:.1f} V -> m_max = {m_max:.3f}, "
      f"goc lech {dlt_max:.2f} deg")
print(f"Us dinh can thiet (198V, 49.5Hz, 2kW) = {Us_pk_min:.1f} V -> m = {Us_pk_min/Vdc:.3f}")
print(f"Ung suat van: V = {V_sw:.1f} V, I_dinh = {I_sw:.2f} A")
print(f"Ton hao dong tren rL = {rL*I_max**2:.1f} W (U=198V)")

# =====================================================================
# 3.1 VONG DONG DIEN - PR
# =====================================================================
fc_i = 1000.0
wc_i = 2 * np.pi * fc_i
Td = 1.5 * Ts                                   # tre PWM + lay mau/tinh toan (so)
PM_i = 60.0                                     # du tru pha mong muon (da tinh tre)

def G_iv(s):                                    # doi tuong vong dong
    return 1 / (L * s + rL)

def G_dt(s, delay=True):
    return G_iv(s) * (np.exp(-s * Td) if delay else 1)

Gc = G_dt(1j * wc_i)
Ac = PM_i - (np.angle(Gc) / deg + 180)          # pha can bu cua PR tai wc (am)
Kp_i = np.cos(Ac * deg) / abs(Gc)               # |G_PR(jwc)| = 1/|G_dt(jwc)|
Kr_i = np.tan(-Ac * deg) * Kp_i * (wc_i**2 - w0**2) / wc_i

def G_PR(s, Kp=Kp_i, Kr=Kr_i, w=w0, wrc=0.0):
    return Kp + Kr * s / (s**2 + 2 * wrc * s + w**2)

wrc = np.pi                                     # PR khong ly tuong: bang thong +/-0.5 Hz

print("\n" + "=" * 70)
print("PHAN 3.1 - VONG DONG DIEN (PR)")
print("=" * 70)
print(f"Td = 1.5 Ts = {Td*1e6:.0f} us, fc = {fc_i:.0f} Hz, PM mong muon = {PM_i:.0f} deg")
print(f"|G_dt(jwc)| = {abs(Gc):.5f}, goc G_iv = {np.angle(G_iv(1j*wc_i))/deg:.2f} deg, "
      f"goc tre = {-wc_i*Td/deg:.2f} deg")
print(f"A_c (pha cua PR tai wc) = {Ac:.2f} deg")
print(f"Kp = {Kp_i:.3f}  Ohm,  Kr = {Kr_i:.1f}  Ohm/s")
print(f"Hang so thoi gian hoi tu sai lech bien do tai 50 Hz tau = 2Kp/Kr = {2*Kp_i/Kr_i*1e3:.1f} ms")

def margins(Lfun, w):
    Lw = Lfun(1j * w)
    mag = np.abs(Lw)
    ph = np.unwrap(np.angle(Lw)) / deg
    # tan so cat: lan cat 1 cuoi cung
    idx = np.where(np.diff(np.sign(mag - 1)) != 0)[0]
    k = idx[-1]
    wc = np.interp(1, [mag[k + 1], mag[k]], [w[k + 1], w[k]])
    phc = np.interp(wc, w, ph)
    pm = 180 + phc
    # du tru bien do: pha = -180 (sau tan so cat)
    j = np.where((np.diff(np.sign(ph + 180)) != 0) & (w[:-1] > wc))[0]
    gm = -20 * np.log10(np.abs(Lfun(1j * w[j[0]]))) if len(j) else np.inf
    return wc, pm, gm

w = np.logspace(0, 5.5, 200000)
for lab, fun in [("khong tre (mo hinh nguyen ly)", lambda s: G_PR(s) * G_dt(s, False)),
                 ("co tre 1.5Ts (thuc thi so)", lambda s: G_PR(s) * G_dt(s, True)),
                 ("PR khong ly tuong wrc=pi, co tre", lambda s: G_PR(s, wrc=wrc) * G_dt(s, True))]:
    wc, pm, gm = margins(fun, w)
    print(f"  {lab:38s}: fc = {wc/2/np.pi:7.1f} Hz, PM = {pm:5.1f} deg, GM = {gm:5.1f} dB")
# Do loi vong ho tai 50.5 Hz
for f_ in (49.5, 50.5):
    s_ = 1j * 2 * np.pi * f_
    T_ideal = abs(G_PR(s_) * G_iv(s_))
    T_nonid = abs(G_PR(s_, wrc=wrc) * G_iv(s_))
    print(f"  |L(j2pi{f_})| PR ly tuong = {T_ideal:.0f}, PR khong ly tuong = {T_nonid:.0f} "
          f"-> sai lech bien do ~ {100/T_nonid:.2f}%")
s50 = 1j * w0
print(f"  |L(j2pi50)| PR khong ly tuong = {abs(G_PR(s50, wrc=wrc)*G_iv(s50)):.0f}; "
      f"Kr_nonideal (dang slide 18) = Kr/(2wrc) = {Kr_i/(2*wrc):.1f}")

# So sanh cac lua chon PM (bang tham khao)
print("  Bang so sanh lua chon PM (co tre):")
for pm_ in (45, 50, 60, 70):
    A = pm_ - (np.angle(Gc) / deg + 180)
    kp = np.cos(A * deg) / abs(Gc); kr = np.tan(-A * deg) * kp * (wc_i**2 - w0**2) / wc_i
    print(f"    PM={pm_:2d}: Ac={A:6.2f}, Kp={kp:6.2f}, Kr={kr:9.1f}, tau={2*kp/kr*1e3:6.2f} ms")

# =====================================================================
# 3.2 VONG DIEN AP - PI + NOTCH
# =====================================================================
Kv = Vm / (2 * C * Vdc)                          # G_vi(s) = Kv / s
zeta_v = 0.707
fn_v = 10.0
wn_v = 2 * np.pi * fn_v
Kp_v = 2 * zeta_v * wn_v / Kv
Ki_v = wn_v**2 / Kv
wN = 2 * w0; Q_N = 1.0

def G_notch(s, wn=wN, Q=Q_N):
    return (s**2 + wn**2) / (s**2 + wn / Q * s + wn**2)

def T_i(s):                                      # ham truyen kin vong dong (bien do)
    Lz = G_PR(s) * G_dt(s, True)
    return Lz / (1 + Lz)

def G_vi(s):
    return Kv / s

def G_vi_R(s):                                   # co tai tro R (cuc thuc)
    return Vm * R_load / (2 * Vdc * (R_load * C * s + 2))

def G_PI_v(s):
    return Kp_v + Ki_v / s

print("\n" + "=" * 70)
print("PHAN 3.2 - VONG DIEN AP (PI + NOTCH 100 Hz)")
print("=" * 70)
print(f"Kv = Vm/(2 C Vdc) = {Kv:.2f}  (V/s)/A")
print(f"zeta = {zeta_v}, fn = {fn_v} Hz -> Kp_v = {Kp_v:.4f} A/V, Ki_v = {Ki_v:.3f} A/(V.s)")
print(f"Notch: wN = {wN:.1f} rad/s (100 Hz), Q = {Q_N}")
print(f"Tai tro: cuc = 2/(R C) = {2/(R_load*C):.2f} rad/s ({2/(R_load*C)/2/np.pi:.2f} Hz)")
w2 = np.logspace(-1, 4.5, 200000)
for lab, fun in [("ly tuong (PI * Kv/s)", lambda s: G_PI_v(s) * G_vi(s)),
                 ("+ notch", lambda s: G_PI_v(s) * G_notch(s) * G_vi(s)),
                 ("+ notch + vong dong + tai R", lambda s: G_PI_v(s) * G_notch(s) * T_i(s) * G_vi_R(s))]:
    wc, pm, gm = margins(fun, w2)
    print(f"  {lab:30s}: fc = {wc/2/np.pi:6.2f} Hz, PM = {pm:5.1f} deg, GM = {gm:5.1f} dB")
print(f"  Ti so bang thong vong dong / vong ap = {fc_i/ (margins(lambda s: G_PI_v(s)*G_vi(s), w2)[0]/2/np.pi):.0f}")
# Suy giam cua notch tai 99, 100, 101 Hz va pha tai fc
for f_ in (99, 101):
    print(f"  |Notch(j2pi{f_})| = {20*np.log10(abs(G_notch(1j*2*np.pi*f_))):.1f} dB")
wcv = margins(lambda s: G_PI_v(s) * G_vi(s), w2)[0]
print(f"  pha notch tai fc_v = {np.angle(G_notch(1j*wcv))/deg:.2f} deg")
Im_lim = 20.0
print(f"  Gioi han Im* = {Im_lim} A  (dinh dong can thiet lon nhat {Ipk_max:.2f} A)")

# =====================================================================
# 3.3 SOGI-PLL
# =====================================================================
k_sogi = np.sqrt(2)
zeta_p = 0.707
fn_p = 20.0
wn_p = 2 * np.pi * fn_p
Kp_pll = 2 * zeta_p * wn_p / Vm
Ki_pll = wn_p**2 / Vm
print("\n" + "=" * 70)
print("PHAN 3.3 - SOGI-PLL")
print("=" * 70)
print(f"k_SOGI = {k_sogi:.4f}; bang thong BPF = k w0 = {k_sogi*w0:.1f} rad/s; "
      f"tau bien do = 2/(k w0) = {2/(k_sogi*w0)*1e3:.2f} ms")
for h in (3, 5, 7):
    Hd = k_sogi * w0 * 1j * h * w0 / ((1j * h * w0)**2 + k_sogi * w0 * 1j * h * w0 + w0**2)
    Hq = k_sogi * w0**2 / ((1j * h * w0)**2 + k_sogi * w0 * 1j * h * w0 + w0**2)
    print(f"  hai bac {h}: |D| = {abs(Hd):.3f}, |Q| = {abs(Hq):.3f}")
print(f"PLL: zeta = {zeta_p}, fn = {fn_p} Hz -> Kp = {Kp_pll:.4f} rad/(s.V), Ki = {Ki_pll:.3f} rad/(s^2.V)")
print(f"  (neu chuan hoa e_q/Vm: Kp = {2*zeta_p*wn_p:.2f}, Ki = {wn_p**2:.1f})")
print(f"  thoi gian xac lap (2%) ~ 4/(zeta wn) = {4/(zeta_p*wn_p)*1e3:.1f} ms")

# =====================================================================
# HINH VE
# =====================================================================
def bode_plot(ax_m, ax_p, fun, w, label, **kw):
    H = fun(1j * w)
    ax_m.semilogx(w / 2 / np.pi, 20 * np.log10(np.abs(H)), label=label, **kw)
    ax_p.semilogx(w / 2 / np.pi, np.unwrap(np.angle(H)) / deg, label=label, **kw)

# --- Hinh 1: Bode vong dong ---
wb = np.logspace(1, 5, 20000)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.5, 6), sharex=True)
bode_plot(a1, a2, G_iv, wb, r"$G_{iv}(s)=1/(Ls+r_L)$", color="0.55", ls="--")
bode_plot(a1, a2, lambda s: G_PR(s) * G_dt(s, False), wb, r"$G_{PR}G_{iv}$ (không trễ)", color="C0")
bode_plot(a1, a2, lambda s: G_PR(s) * G_dt(s, True), wb, r"$G_{PR}G_{iv}e^{-sT_d}$ (trễ $1.5T_s$)", color="C3")
a1.axhline(0, color="k", lw=0.8); a2.axhline(-180, color="k", lw=0.8)
a1.axvline(fc_i, color="C2", lw=0.8, ls=":"); a2.axvline(fc_i, color="C2", lw=0.8, ls=":")
a1.set_ylabel("Biên độ (dB)"); a2.set_ylabel("Pha (độ)"); a2.set_xlabel("Tần số (Hz)")
a1.set_ylim(-60, 80); a2.set_ylim(-270, 0)
a1.set_title(f"Vòng dòng điện: Kp = {Kp_i:.2f}, Kr = {Kr_i:.0f}, fc = {fc_i:.0f} Hz")
a1.legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig_current_loop_bode.png"))

# --- Hinh 2: Bode bo PR (ly tuong va khong ly tuong) ---
wb2 = np.logspace(1.5, 4, 40000)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.5, 5.5), sharex=True)
bode_plot(a1, a2, G_PR, wb2, "PR lý tưởng", color="C0")
bode_plot(a1, a2, lambda s: G_PR(s, wrc=wrc), wb2, r"PR không lý tưởng ($\omega_{rc}=\pi$)", color="C1")
a1.set_ylabel("Biên độ (dB)"); a2.set_ylabel("Pha (độ)"); a2.set_xlabel("Tần số (Hz)")
a1.set_ylim(20, 110)
a1.set_title("Bộ điều chỉnh PR dòng điện")
a1.legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig_PR_bode.png"))

# --- Hinh 3: Bode vong dien ap ---
wv = np.logspace(0, 3.5, 20000)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.5, 6), sharex=True)
bode_plot(a1, a2, lambda s: G_PI_v(s) * G_vi(s), wv, "PI·Kv/s", color="C0")
bode_plot(a1, a2, lambda s: G_PI_v(s) * G_notch(s) * G_vi(s), wv, "PI·Notch·Kv/s", color="C1")
bode_plot(a1, a2, lambda s: G_PI_v(s) * G_notch(s) * T_i(s) * G_vi_R(s), wv,
          r"PI·Notch·$T_i$·$G_{vi}$ (tải R)", color="C3", ls="--")
a1.axhline(0, color="k", lw=0.8); a2.axhline(-180, color="k", lw=0.8)
a1.set_ylabel("Biên độ (dB)"); a2.set_ylabel("Pha (độ)"); a2.set_xlabel("Tần số (Hz)")
a1.set_ylim(-80, 60); a2.set_ylim(-270, 0)
a1.set_title(f"Vòng điện áp: Kp = {Kp_v:.3f}, Ki = {Ki_v:.2f}, notch 100 Hz (Q = {Q_N})")
a1.legend(fontsize=8); fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig_voltage_loop_bode.png"))

# =====================================================================
# KIEM TRA SO BO: mo phong mo hinh TRUNG BINH phi tuyen (khong phai Phan 4)
# =====================================================================
def simulate(t_end=1.0, dt=2e-6, events=None):
    n = int(t_end / dt)
    # trang thai
    i = 0.0; v = Vm * 0.95          # sau nap truoc qua diode
    x1 = x2 = 0.0                   # PR: x1' = x2, x2' = -w^2 x1 - 2wrc x2 + e  -> out = Kr*x2
    xi_v = 0.0                      # tich phan PI ap
    n1 = n2 = 0.0                   # notch (dang khong gian trang thai)
    sa = sb = 0.0                   # SOGI: v', qv'
    th = 0.0; xi_p = 0.0            # PLL
    th_g = 0.0
    U = U_n; R = R_load * 2         # bat dau 50% tai
    Vref0, Vref1, t_ramp = Vm * 0.95, Vdc, 0.15
    rec = {k: np.zeros(n // 10) for k in ("t", "i", "iref", "v", "e", "Im")}
    delay_buf = [0.0] * int(round(Td / dt))
    for k in range(n):
        t = k * dt
        if events:
            for (te, key, val) in events:
                if abs(t - te) < dt / 2:
                    if key == "U": U = val
                    if key == "R": R = val
        th_g += w0 * dt
        e = math.sqrt(2) * U * math.sin(th_g)
        # SOGI
        err = (e - sa) * k_sogi
        dsa = (err - sb) * w0 ; dsb = sa * w0
        # PLL: qv' = w0*int(v') = -Vm cos(theta)  ->  e_q = v' cos(th) + qv' sin(th) = Vm sin(theta - th)
        eq = sa * math.cos(th) + sb * math.sin(th)
        xi_p += Ki_pll * eq * dt
        wpll = w0 + Kp_pll * eq + xi_p
        th += wpll * dt
        sa += dsa * dt; sb += dsb * dt
        # vong ap
        vref = Vref0 + (Vref1 - Vref0) * min(t / t_ramp, 1.0)
        # Notch = 1 - BPF,  BPF = (wN/Q) s / (s^2 + (wN/Q) s + wN^2)
        dn1 = n2
        dn2 = -wN**2 * n1 - (wN / Q_N) * n2 + v
        vf = v - (wN / Q_N) * n2
        n1 += dn1 * dt; n2 += dn2 * dt
        ev = vref - vf
        Im_un = Kp_v * ev + xi_v
        Im = min(max(Im_un, 0.0), Im_lim)
        # anti-windup (kep tich phan)
        if Im == Im_un or (Im_un > Im_lim and ev < 0) or (Im_un < 0 and ev > 0):
            xi_v += Ki_v * ev * dt
        iref = Im * math.sin(th)
        # PR
        ei = iref - i
        dx1 = x2; dx2 = -w0**2 * x1 - 2 * wrc * x2 + ei
        uPR = Kp_i * ei + Kr_i * x2
        x1 += dx1 * dt; x2 += dx2 * dt
        us_ref = e - uPR                             # feedforward luoi
        m = min(max(us_ref / v, -1.0), 1.0)
        delay_buf.append(m); m_d = delay_buf.pop(0)
        us = m_d * v
        di = (e - rL * i - us) / L
        dv = (m_d * i - v / R) / C
        i += di * dt; v += dv * dt
        if k % 10 == 0:
            j = k // 10
            if j < len(rec["t"]):
                rec["t"][j] = t; rec["i"][j] = i; rec["iref"][j] = iref
                rec["v"][j] = v; rec["e"][j] = e; rec["Im"][j] = Im
    return rec

print("\n" + "=" * 70)
print("KIEM TRA SO BO BANG MO HINH TRUNG BINH (averaged, co tre 1.5Ts)")
print("=" * 70)
ev = [(0.40, "R", R_load), (0.60, "U", U_min), (0.80, "U", U_max)]
r = simulate(1.0, 2e-6, ev)
t = r["t"]
def stat(t0, t1):
    m_ = (t > t0) & (t < t1)
    return r["v"][m_].mean(), r["v"][m_].max() - r["v"][m_].min(), np.max(np.abs(r["i"][m_] - r["iref"][m_]))
for lab, (t0, t1) in [("50% tai, 220V", (0.30, 0.40)), ("100% tai, 220V", (0.50, 0.60)),
                      ("100% tai, 198V", (0.70, 0.80)), ("100% tai, 242V", (0.90, 1.0))]:
    vm_, vpp, ei_ = stat(t0, t1)
    print(f"  {lab:16s}: Vdc TB = {vm_:6.1f} V, gon pp = {vpp:5.2f} V, |i - i*|max = {ei_:.3f} A")
m_ = (t > 0.40) & (t < 0.55)
print(f"  Nhay tai 50->100% tai t=0.4s: Vdc min = {r['v'][m_].min():.1f} V "
      f"(sut {Vdc - r['v'][m_].min():.1f} V)")
# THD dong o 100% tai 220V
m_ = (t >= 0.50) & (t < 0.60)
ii = r["i"][m_]; tt = t[m_]
N = len(ii); F = np.fft.rfft(ii * 1.0) / N * 2; fr = np.fft.rfftfreq(N, tt[1] - tt[0])
h1 = np.abs(F[np.argmin(abs(fr - 50))])
hs = [np.abs(F[np.argmin(abs(fr - 50 * h))]) for h in range(2, 40)]
print(f"  THD dong luoi (mo hinh TB, 100% tai) = {np.sqrt(np.sum(np.square(hs)))/h1*100:.2f}%, "
      f"I1 = {h1/np.sqrt(2):.2f} A rms")

fig, ax = plt.subplots(3, 1, figsize=(8, 7.5), sharex=True)
ax[0].plot(t, r["v"], lw=0.8); ax[0].set_ylabel("$v_{dc}$ (V)"); ax[0].set_ylim(280, 430)
ax[1].plot(t, r["i"], lw=0.6, label="$i_s$"); ax[1].plot(t, r["iref"], lw=0.6, ls="--", label="$i_s^*$")
ax[1].set_ylabel("Dòng (A)"); ax[1].legend(fontsize=8, loc="upper left")
ax[2].plot(t, r["e"] / 20, lw=0.6, label="$e_n/20$"); ax[2].plot(t, r["i"], lw=0.6, label="$i_s$")
ax[2].set_xlim(0, 1); ax[2].set_ylabel("V/20, A"); ax[2].set_xlabel("t (s)"); ax[2].legend(fontsize=8, loc="upper left")
for a in ax:
    for te, _, _ in ev: a.axvline(te, color="k", lw=0.6, ls=":")
ax[0].set_title("Kiểm tra sơ bộ trên mô hình trung bình (tải 50%→100% @0.4s, U 220→198 @0.6s, →242 V @0.8s)", fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(FIG, "fig_avg_model_check.png"))
print("\nDa luu hinh vao:", FIG)
