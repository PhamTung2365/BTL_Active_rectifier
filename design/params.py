# -*- coding: utf-8 -*-
"""Tham so mach luc va bo dieu khien lien tuc (ket qua Phan 3) - dung chung cho cac script."""
import numpy as np

deg = np.pi / 180

# Mach luc
U_n, U_min, U_max = 220.0, 198.0, 242.0
f_n = 50.0
w0 = 2 * np.pi * f_n
Vm = np.sqrt(2) * U_n
P = 2000.0
L, rL = 5e-3, 0.1
C = 2200e-6
Vdc = 400.0
R_load = Vdc**2 / P
fs = 20e3
Ts = 1 / fs
Td = 1.5 * Ts

# Vong dong - PR (fc = 1 kHz, PM = 60 deg tinh ca tre Td)
fc_i = 1000.0
wc_i = 2 * np.pi * fc_i
PM_i = 60.0
_Gc = np.exp(-1j * wc_i * Td) / (1j * wc_i * L + rL)
Ac = PM_i - (np.angle(_Gc) / deg + 180)
Kp_i = np.cos(Ac * deg) / abs(_Gc)
Kr_i = np.tan(-Ac * deg) * Kp_i * (wc_i**2 - w0**2) / wc_i
wrc = np.pi

# Vong ap - PI + notch
Kv = Vm / (2 * C * Vdc)
zeta_v, wn_v = 0.707, 2 * np.pi * 10.0
Kp_v = 2 * zeta_v * wn_v / Kv
Ki_v = wn_v**2 / Kv
Im_max = 20.0
wN, Q_N = 2 * w0, 1.0

# SOGI-PLL
k_sogi = np.sqrt(2)
zeta_p, wn_p = 0.707, 2 * np.pi * 20.0
Kp_pll = 2 * zeta_p * wn_p / Vm
Ki_pll = wn_p**2 / Vm

# Ham truyen lien tuc dang da thuc (he so theo luy thua giam dan cua s)
PLANT_I = ([1.0], [L, rL])                                  # G_iv = 1/(Ls + rL)
PLANT_V = ([Kv], [1.0, 0.0])                                # G_vi = Kv/s
PLANT_VR = ([Vm * R_load / (2 * Vdc)], [R_load * C, 2.0])   # G_vi voi tai R
PR_IDEAL = ([Kp_i, Kr_i, Kp_i * w0**2], [1.0, 0.0, w0**2])
PR_NONID = ([Kp_i, 2 * wrc * Kp_i + Kr_i, Kp_i * w0**2], [1.0, 2 * wrc, w0**2])
PI_V = ([Kp_v, Ki_v], [1.0, 0.0])
NOTCH = ([1.0, 0.0, wN**2], [1.0, wN / Q_N, wN**2])
SOGI_D = ([k_sogi * w0, 0.0], [1.0, k_sogi * w0, w0**2])
SOGI_Q = ([k_sogi * w0**2], [1.0, k_sogi * w0, w0**2])
PI_PLL = ([Kp_pll, Ki_pll], [1.0, 0.0])
