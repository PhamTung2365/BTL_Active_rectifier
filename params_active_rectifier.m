%% THAM SO THIET KE - CHINH LUU TICH CUC 1 PHA (EE4331 - Bai 26)
% Chay file nay truoc khi chay mo hinh Simulink (Phan 4). Cac so lieu khop
% voi design_calc.py va file Ly_thuyet_Phan1-3.md.
clear; clc;

%% 1. Mach luc
U_n   = 220;            % V rms (dai 198..242 V)
f_n   = 50;             % Hz   (dai 49.5..50.5 Hz)
w0    = 2*pi*f_n;
Vm    = sqrt(2)*U_n;    % 311.1 V
P     = 2000;           % W (S = 2 kVA, PF = 1)
L     = 5e-3;           % H
rL    = 0.1;            % Ohm
C     = 2200e-6;        % F
Vdc   = 400;            % V
R_load = Vdc^2/P;       % 80 Ohm (day tai)
fs    = 20e3;           % Hz - tan so dong cat (PWM don cuc)
Ts    = 1/fs;
Td    = 1.5*Ts;         % tre tuong duong PWM + lay mau/tinh toan (dung cho thiet ke)

%% 2. Vong dong dien - PR (thiet ke theo fc va PM, slide 17 bai giang)
fc_i = 1000;  wc_i = 2*pi*fc_i;  PM_i = 60;          % PM da tinh ca tre Td
Gc   = 1/(1j*wc_i*L + rL) * exp(-1j*wc_i*Td);
Ac   = PM_i - (angle(Gc)*180/pi + 180);               % pha PR can tai wc (deg, am)
Kp_i = cosd(Ac)/abs(Gc);                              % ~31.37
Kr_i = tand(-Ac)*Kp_i*(wc_i^2 - w0^2)/wc_i;           % ~1.093e4
wrc  = pi;                                            % PR khong ly tuong (+/-0.5 Hz)

%% 3. Vong dien ap - PI + notch 100 Hz
Kv     = Vm/(2*C*Vdc);                                % G_vi(s) = Kv/s  (176.8)
zeta_v = 0.707;  wn_v = 2*pi*10;
Kp_v   = 2*zeta_v*wn_v/Kv;                            % ~0.503 A/V
Ki_v   = wn_v^2/Kv;                                   % ~22.33 A/(V.s)
Im_max = 20;                                          % A - gioi han bien do dong dat
wN     = 2*w0;  Q_N = 1;                              % notch 100 Hz

%% 4. SOGI-PLL
k_sogi = sqrt(2);
zeta_p = 0.707;  wn_p = 2*pi*20;
Kp_pll = 2*zeta_p*wn_p/Vm;                            % ~0.571 (dau vao e_q chua chuan hoa)
Ki_pll = wn_p^2/Vm;                                   % ~50.76

%% 5. Khoi dong (goi y cho mo phong)
Vdc_ref_start = Vm;     % sau nap truoc qua diode, v_dc ~ Vm
t_ramp        = 0.15;   % s - doc tang v_dc* tu Vm len 400 V

fprintf('PR : Kp = %.3f, Kr = %.1f\n', Kp_i, Kr_i);
fprintf('PI : Kp = %.4f, Ki = %.3f\n', Kp_v, Ki_v);
fprintf('PLL: Kp = %.4f, Ki = %.3f, k_SOGI = %.4f\n', Kp_pll, Ki_pll, k_sogi);

%% 6. Kiem tra bang Control System Toolbox (neu co)
if exist('tf', 'file')
    s     = tf('s');
    G_iv  = 1/(L*s + rL);
    G_PR  = Kp_i + Kr_i*s/(s^2 + w0^2);
    G_PRn = Kp_i + Kr_i*s/(s^2 + 2*wrc*s + w0^2);
    G_del = exp(-Td*s);
    figure; margin(G_PR*G_iv*G_del); title('Vong dong: PR * G_{iv} * e^{-sT_d}');
    G_PI  = Kp_v + Ki_v/s;
    G_N   = (s^2 + wN^2)/(s^2 + wN/Q_N*s + wN^2);
    figure; margin(G_PI*G_N*Kv/s); title('Vong ap: PI * Notch * K_v/s');
    % Tinh roi rac hoa Tustin (goi y Phan 5):
    % opt = c2dOptions('Method','tustin','PrewarpFrequency',w0);
    % G_PRz = c2d(G_PRn, Ts, opt);
end
