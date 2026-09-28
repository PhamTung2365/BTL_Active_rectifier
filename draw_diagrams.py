# -*- coding: utf-8 -*-
"""Ve so do mach luc va so do cau truc dieu khien (luu vao figures/)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle
import schemdraw
import schemdraw.elements as elm

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "figures")
os.makedirs(FIG, exist_ok=True)

# =====================================================================
# 1) SO DO MACH LUC
# =====================================================================
schemdraw.config(fontsize=13)


def switch(d, name, at):
    """IGBT + diode nguoc, dat thang dung, collector o tren. Tra ve (top, bottom)."""
    q = d.add(elm.IgbtN(anchor="collector").at(at).theta(0).label(name, loc="left", ofst=0.1))
    top, bot = q.collector, q.emitter
    # diode nguoc song song (catot o collector)
    d.add(elm.Line().at(top).right(0.9))
    dd = d.add(elm.Diode().down().toy(bot).reverse())
    d.add(elm.Line().left(0.9).to(bot))
    return top, bot


with schemdraw.Drawing(show=False) as d:
    d.config(unit=2.2)
    H = 6.0
    xa, xb = 3.0, 17.0
    # leg A
    a1t, a1b = switch(d, "$S_1$", (xa, H))
    a4t, a4b = switch(d, "$S_4$", (xa, a1b[1] - 1.6))
    d.add(elm.Line().at(a1b).to(a4t))
    mid_a = (xa, (a1b[1] + a4t[1]) / 2)
    # leg B
    b3t, b3b = switch(d, "$S_3$", (xb, H))
    b2t, b2b = switch(d, "$S_2$", (xb, b3b[1] - 1.6))
    d.add(elm.Line().at(b3b).to(b2t))
    mid_b = (xb, (b3b[1] + b2t[1]) / 2)
    ybot = a4b[1]
    # thanh cai DC
    xc, xr = 21.0, 24.5
    d.add(elm.Line().at((xa, H)).to((xr, H)))
    d.add(elm.Line().at((xa, ybot)).to((xr, ybot)))
    for x_ in (xb, xc):
        d.add(elm.Dot().at((x_, H))); d.add(elm.Dot().at((x_, ybot)))
    d.add(elm.Capacitor(polar=True).at((xc, H)).toy(ybot).down()
          .label("$C_{dc}$\n2200 µF", loc="bottom", ofst=0.25))
    d.add(elm.Resistor().at((xr, H)).toy(ybot).down().label("Tải", loc="bottom", ofst=0.25))
    d.add(elm.Gap().at((xr + 3.6, H)).toy(ybot).down().label(["+", "$v_{dc}$ = 400 V", "−"]))
    # nhanh AC giua 2 diem giua cau (a, b)
    d.add(elm.Dot().at(mid_a)); d.add(elm.Dot().at(mid_b))
    d.add(elm.Line().at(mid_a).right(0.6))
    d.add(elm.Inductor2(loops=3).right(2.4).label("$L$ = 5 mH", loc="top"))
    d.add(elm.Resistor().right(2.4).label("$r_L$ = 0.1 Ω", loc="top"))
    d.add(elm.Line().right(1.2).label("← $i_s$", loc="top"))
    src_start = d.here
    d.add(elm.SourceSin().right(2.4).label("$e_n$ = 220 V, 50 Hz", loc="top", ofst=0.35)
          .label(["+", "−"], loc="bottom", ofst=0.1))
    d.add(elm.Line().to(mid_b))
    d.add(elm.Label().at((xa - 0.4, mid_a[1] + 0.4)).label("a"))
    d.add(elm.Label().at((xb + 0.4, mid_b[1] + 0.4)).label("b"))
    d.add(elm.Label().at(((xa + xb) / 2, mid_a[1] - 1.7))
          .label("$u_s = v_a - v_b = m\,v_{dc}$   (điện áp xoay chiều phía bộ biến đổi)", fontsize=12))
    d.save(os.path.join(FIG, "fig_power_circuit.png"), dpi=170)
    d.save(os.path.join(FIG, "fig_power_circuit.svg"))

# =====================================================================
# 2) SO DO CAU TRUC DIEU KHIEN (matplotlib)
# =====================================================================
fig, ax = plt.subplots(figsize=(15, 6.6))
ax.set_xlim(0, 150); ax.set_ylim(0, 66); ax.axis("off")
C_BOX = "#fdf3e7"; C_EDGE = "#b5452f"; C_SIG = "#222222"; C_PLL = "#e8f1fb"; C_PLLE = "#2f6db5"


def box(x, y, w, h, text, fc=C_BOX, ec=C_EDGE, fs=11):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.25",
                                fc=fc, ec=ec, lw=1.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs)
    return (x - w / 2, x + w / 2, y - h / 2, y + h / 2)


def summ(x, y, signs="+-", r=1.6):
    ax.add_patch(Circle((x, y), r, fc="white", ec=C_SIG, lw=1.3))
    ax.plot([x - r * 0.7, x + r * 0.7], [y - r * 0.7, y + r * 0.7], color=C_SIG, lw=0.8)
    ax.plot([x - r * 0.7, x + r * 0.7], [y + r * 0.7, y - r * 0.7], color=C_SIG, lw=0.8)
    return r


def mult(x, y, r=1.6):
    ax.add_patch(Circle((x, y), r, fc="white", ec=C_SIG, lw=1.3))
    ax.text(x, y, "×", ha="center", va="center", fontsize=13)


def arrow(p, q, text=None, tpos=0.5, dy=1.4, dx=0, fs=12, color=C_SIG):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3,
                                                    shrinkA=0, shrinkB=0, mutation_scale=13))
    if text:
        ax.text(p[0] + (q[0] - p[0]) * tpos + dx, p[1] + (q[1] - p[1]) * tpos + dy, text,
                ha="center", va="bottom", fontsize=fs)


def line(pts, color=C_SIG):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=1.3)


Y = 44          # truc tin hieu chinh
r = 1.6
# vong ap
ax.text(1.5, Y + 1.2, "$v_{dc}^*$", fontsize=14, ha="left", va="bottom")
summ(10, Y); ax.text(10 - 3.2, Y + 1.2, "+", fontsize=11); ax.text(10 + 0.4, Y - 4.0, "−", fontsize=12)
arrow((3, Y), (10 - r, Y))
b_pi = box(21.5, Y, 12, 7.5, "ĐC điện áp PI\n(anti-windup)\n$K_p+K_i/s$", fs=10)
arrow((10 + r, Y), (b_pi[0], Y), "$e_v$", dy=0.6)
b_lim = box(33.5, Y, 6, 5.5, "", fs=9)
line([(31.3, Y - 1.8), (32.5, Y - 1.8), (34.5, Y + 1.8), (35.7, Y + 1.8)])
ax.text(33.5, Y + 3.5, "giới hạn", fontsize=8.5, ha="center")
arrow((b_pi[1], Y), (b_lim[0], Y))
mult(44, Y)
arrow((b_lim[1], Y), (44 - r, Y), "$I_m^*$", dy=0.6)
# vong dong
summ(54, Y); ax.text(54 - 3.2, Y + 1.2, "+", fontsize=11); ax.text(54 + 0.4, Y - 4.0, "−", fontsize=12)
arrow((44 + r, Y), (54 - r, Y), "$i_s^*$", dy=0.6)
b_pr = box(66, Y, 12, 7, "ĐC dòng điện PR\n$K_p+\\dfrac{K_r s}{s^2+\\omega_0^2}$", fs=10)
arrow((54 + r, Y), (b_pr[0], Y), "$e_i$", dy=0.6)
summ(80, Y); ax.text(80 + 1.2, Y + 2.0, "+", fontsize=11); ax.text(80 - 3.3, Y + 1.0, "−", fontsize=12)
arrow((b_pr[1], Y), (80 - r, Y), "$u_L^*$", dy=0.6)
b_div = box(90, Y, 5, 5, "÷", fs=16)
arrow((80 + r, Y), (b_div[0], Y), "$u_s^*$", dy=0.6)
b_pwm = box(101, Y, 10, 6, "PWM\nđơn cực\n$f_s$ = 20 kHz", fs=10)
arrow((b_div[1], Y), (b_pwm[0], Y), "$m$", dy=0.6)
b_pc = box(125, Y, 22, 16, "MẠCH LỰC\nCầu H 1 pha (4 IGBT)\n$L$ = 5 mH, $r_L$ = 0.1 Ω\n$C_{dc}$ = 2200 µF\nLưới 220 V/50 Hz",
           fc="#eeeeee", ec="#555555", fs=10.5)
arrow((b_pwm[1], Y), (b_pc[0], Y), "$S_1..S_4$", dy=0.6)
# feedforward e_n vao bo cong u_s*
line([(80, 60), (80, Y + r + 0.05)]); arrow((80, 60.5), (80, Y + r))
ax.text(80.8, 57, "$e_n$ (feedforward)", fontsize=11, ha="left")
line([(80, 60.5), (140, 60.5), (140, Y + 8)])
ax.text(141, 57, "đo $e_n$", fontsize=10, ha="left", color="#555")
# v_dc do ve -> chia
line([(90, 26), (90, Y - 2.5)]); arrow((90, 26), (90, Y - 2.5))
ax.text(90.8, 30, "$v_{dc}$", fontsize=12)
# phan hoi dong i_s
yi = 33
line([(128, Y - 8), (128, yi), (54, yi)]); arrow((54, yi), (54, Y - r))
ax.text(100, yi + 0.6, "$i_s$ (đo dòng lưới)", fontsize=11, ha="center")
# phan hoi v_dc qua notch
yv = 22
line([(122, Y - 8), (122, yv), (26, yv)])
line([(90, yv), (90, 26)])
ax.plot(90, yv, "o", color=C_SIG, ms=4)
b_nf = box(20, yv, 12, 6, "Notch 100 Hz\n$\\dfrac{s^2+\\omega_N^2}{s^2+\\frac{\\omega_N}{Q}s+\\omega_N^2}$", fs=9.5)
arrow((26, yv), (b_nf[1], yv))
line([(b_nf[0], yv), (10, yv)]); arrow((10, yv), (10, Y - r))
ax.text(108, yv + 0.6, "$v_{dc}$ (đo điện áp bus DC)", fontsize=11, ha="center")
# SOGI-PLL
yp = 8
b_pll = box(87, yp, 50, 9, "SOGI-PLL\n$e_n\\ \\rightarrow$ SOGI $(v', qv')$ → Park → $e_q$ → PI → $\\omega$ → $\\int$ → $\\hat\\theta$",
            fc=C_PLL, ec=C_PLLE, fs=10)
line([(134, Y - 8), (134, yp), (b_pll[1], yp)]); arrow((134, yp), (b_pll[1], yp))
ax.text(135, yp + 1, "$e_n$", fontsize=12)
b_sin = box(50, yp, 7, 5, "sin(·)", fc=C_PLL, ec=C_PLLE, fs=11)
arrow((b_pll[0], yp), (b_sin[1], yp), "$\\hat\\theta$", dy=0.6)
line([(b_sin[0], yp), (44, yp)]); arrow((44, yp), (44, Y - r))
ax.text(44.8, 14, "$\\sin\\hat\\theta$", fontsize=12)
# chu thich vong
ax.add_patch(FancyBboxPatch((4.5, 36.5), 33, 14.5, boxstyle="round,pad=0.3", fc="none", ec="#999", ls="--", lw=1))
ax.text(5.5, 52.3, "Mạch vòng điện áp (ngoài) ~ 15 Hz", fontsize=10, color="#666")
ax.add_patch(FancyBboxPatch((49, 36.5), 46, 14.5, boxstyle="round,pad=0.3", fc="none", ec="#999", ls="--", lw=1))
ax.text(50, 52.3, "Mạch vòng dòng điện (trong) ~ 1 kHz", fontsize=10, color="#666")
fig.tight_layout()
fig.savefig(os.path.join(FIG, "fig_control_structure.png"), dpi=170)
fig.savefig(os.path.join(FIG, "fig_control_structure.svg"))
print("OK")
