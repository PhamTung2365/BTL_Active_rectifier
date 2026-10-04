function [m, i_ref, theta, Im] = ctrl_digital_step(i_s, v_dc, e_n, vdc_ref)
%CTRL_DIGITAL_STEP  Bo dieu khien so cho chinh luu tich cuc 1 pha (Phan 5).
%   Goi MOT LAN moi chu ky lay mau Ts = 50 us (dung trong MATLAB Function
%   block, sample time = Ts; cac dau vao qua Zero-Order Hold Ts, lay mau
%   dong bo dinh song mang PWM).
%
%   Vao : i_s     dong luoi do duoc (A), chieu tu luoi vao bo bien doi
%         v_dc    dien ap bus DC (V)
%         e_n     dien ap luoi (V)
%         vdc_ref dien ap dat bus DC (V)
%   Ra  : m       he so dieu che dua vao PWM (da tre 1 chu ky: m tinh o
%                 buoc k duoc xuat ra o buoc k+1 -> mo hinh dung tre tinh toan)
%         i_ref, theta, Im : tin hieu de quan sat
%
%   Tat ca bo dieu khien lien tuc (Phan 3) duoc roi rac hoa theo Tustin:
%   PR va SOGI prewarp tai 50 Hz, Notch prewarp tai 100 Hz, PI khong prewarp.
%   He so khop voi digital_tustin.py / Phan5_Dieu_khien_so_Tustin.md.
%#codegen
persistent c st
if isempty(c)
    c  = init_coeffs();
    st = struct('pr', [0 0], 'no', [0 0], 'sd', [0 0], 'sq', [0 0], ...
                'xiV', 0, 'epV', 0, 'xiP', 0, 'epP', 0, 'th', 0, 'm_next', 0);
end

m = st.m_next;                                   % tre tinh toan z^-1

% ---- SOGI-PLL --------------------------------------------------------
[vp, st.sd] = df2t(c.sd_b, c.sd_a, e_n, st.sd);  % v'  (dong pha e_n)
[qv, st.sq] = df2t(c.sq_b, c.sq_a, e_n, st.sq);  % qv' (cham pha 90 do)
eq = vp*cos(st.th) + qv*sin(st.th);              % = Vm sin(theta - theta_hat)
[dw, st.xiP, st.epP] = pi_aw(c.Kp_pll, c.Ki_pll, c.Ts, -c.dw_max, c.dw_max, eq, st.xiP, st.epP);
theta = st.th;
st.th = mod(st.th + c.Ts*(c.w0 + dw), 2*pi);     % NCO: theta[k+1] = theta[k] + Ts*w[k]

% ---- Vong dien ap: Notch 100 Hz + PI (anti-windup) -------------------
[vf, st.no] = df2t(c.no_b, c.no_a, v_dc, st.no);
[Im, st.xiV, st.epV] = pi_aw(c.Kp_v, c.Ki_v, c.Ts, 0, c.Im_max, vdc_ref - vf, st.xiV, st.epV);
i_ref = Im*sin(theta);

% ---- Vong dong dien: PR + feedforward e_n + chuan hoa v_dc ------------
[uL, st.pr] = df2t(c.pr_b, c.pr_a, i_ref - i_s, st.pr);
st.m_next = min(max((e_n - uL)/max(v_dc, 1), -1), 1);
end

% =======================================================================
function c = init_coeffs()
Ts = 50e-6;  w0 = 2*pi*50;
L = 5e-3; rL = 0.1; C = 2200e-6; Vdc = 400; Vm = sqrt(2)*220;
% PR (Phan 3.4): fc = 1 kHz, PM = 60 deg tinh ca tre 1.5Ts
wc = 2*pi*1000; Td = 1.5*Ts;
Gc = exp(-1j*wc*Td)/(1j*wc*L + rL);
Ac = 60 - (angle(Gc)*180/pi + 180);
Kp_i = cosd(Ac)/abs(Gc);
Kr_i = tand(-Ac)*Kp_i*(wc^2 - w0^2)/wc;
wrc  = pi;
% PI ap (Phan 3.5)
Kv = Vm/(2*C*Vdc);  wn = 2*pi*10;  zeta = 0.707;
c.Kp_v = 2*zeta*wn/Kv;  c.Ki_v = wn^2/Kv;  c.Im_max = 20;
wN = 2*w0;  QN = 1;
% SOGI-PLL (Phan 3.6)
k = sqrt(2);  wp = 2*pi*20;
c.Kp_pll = 2*0.707*wp/Vm;  c.Ki_pll = wp^2/Vm;  c.dw_max = 2*pi*5;
c.Ts = Ts;  c.w0 = w0;
% Tustin + prewarp cho cac khau bac 2: G(s) = (n0 s^2 + n1 s + n2)/(s^2 + d1 s + d2)
K0 = w0/tan(w0*Ts/2);  KN = wN/tan(wN*Ts/2);
[c.pr_b, c.pr_a] = tustin2([Kp_i, 2*wrc*Kp_i + Kr_i, Kp_i*w0^2], [2*wrc, w0^2], K0);
[c.no_b, c.no_a] = tustin2([1, 0, wN^2], [wN/QN, wN^2], KN);
[c.sd_b, c.sd_a] = tustin2([0, k*w0, 0], [k*w0, w0^2], K0);
[c.sq_b, c.sq_a] = tustin2([0, 0, k*w0^2], [k*w0, w0^2], K0);
end

function [b, a] = tustin2(n, d, K)
% s = K (z-1)/(z+1);  tra ve b = [b0 b1 b2], a = [1 a1 a2] (he so cua z^0, z^-1, z^-2)
a0 = K^2 + d(1)*K + d(2);
b  = [n(1)*K^2 + n(2)*K + n(3), 2*(n(3) - n(1)*K^2), n(1)*K^2 - n(2)*K + n(3)]/a0;
a  = [1, 2*(d(2) - K^2)/a0, (K^2 - d(1)*K + d(2))/a0];
end

function [y, s] = df2t(b, a, x, s)
% Direct Form II Transposed bac 2: y = b0 x + s1; s1 = b1 x - a1 y + s2; s2 = b2 x - a2 y
y    = b(1)*x + s(1);
s(1) = b(2)*x - a(2)*y + s(2);
s(2) = b(3)*x - a(3)*y;
end

function [u, xi, ep] = pi_aw(Kp, Ki, Ts, umin, umax, e, xi, ep)
% PI Tustin: xi[k] = xi[k-1] + Ki*Ts/2*(e[k] + e[k-1]); u = Kp*e + xi
% Chong bao hoa tich phan: khong cap nhat xi khi dau ra bao hoa va e day tiep ra ngoai
xi_new = xi + Ki*Ts/2*(e + ep);
u_try  = Kp*e + xi_new;
if ~((u_try > umax && e > 0) || (u_try < umin && e < 0))
    xi = xi_new;
end
ep = e;
u  = min(max(Kp*e + xi, umin), umax);
end
