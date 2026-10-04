%% PHAN 5 - HE SO BO DIEU KHIEN SO (TUSTIN) CHO SIMULINK
% Chay sau params_active_rectifier.m. Tao cac bien *_b, *_a dung cho khoi
% "Discrete Transfer Fcn" (Numerator = *_b, Denominator = *_a, Sample time = Ts).
% Neu dung MATLAB Function block thi chi can ctrl_digital_step.m.
run('params_active_rectifier.m');

K0 = w0/tan(w0*Ts/2);          % prewarp 50 Hz
KN = wN/tan(wN*Ts/2);          % prewarp 100 Hz
tustin2 = @(n, d, K) deal( ...
    [n(1)*K^2 + n(2)*K + n(3), 2*(n(3) - n(1)*K^2), n(1)*K^2 - n(2)*K + n(3)] / (K^2 + d(1)*K + d(2)), ...
    [1, 2*(d(2) - K^2), K^2 - d(1)*K + d(2)] / (K^2 + d(1)*K + d(2)));

%% Bo dieu khien (Tustin)
[PR_b, PR_a]   = tustin2([Kp_i, 2*wrc*Kp_i + Kr_i, Kp_i*w0^2], [2*wrc, w0^2], K0);  % PR khong ly tuong
[PRi_b, PRi_a] = tustin2([Kp_i, Kr_i, Kp_i*w0^2], [0, w0^2], K0);                   % PR ly tuong
[NO_b, NO_a]   = tustin2([1, 0, wN^2], [wN/Q_N, wN^2], KN);                          % Notch 100 Hz
[SD_b, SD_a]   = tustin2([0, k_sogi*w0, 0], [k_sogi*w0, w0^2], K0);                  % SOGI v'
[SQ_b, SQ_a]   = tustin2([0, 0, k_sogi*w0^2], [k_sogi*w0, w0^2], K0);                % SOGI qv'
PIv_b  = [Kp_v + Ki_v*Ts/2, -Kp_v + Ki_v*Ts/2];   PIv_a  = [1 -1];                   % PI ap
PIp_b  = [Kp_pll + Ki_pll*Ts/2, -Kp_pll + Ki_pll*Ts/2];  PIp_a = [1 -1];             % PI PLL

%% Doi tuong roi rac (de kiem tra on dinh)
Giv_T_b = Ts/(2*L + rL*Ts)*[1 1];   Giv_T_a = [1, -(2*L - rL*Ts)/(2*L + rL*Ts)];     % Tustin
Giv_Z_b = (1 - exp(-rL*Ts/L))/rL;    Giv_Z_a = [1, -exp(-rL*Ts/L)];                  % ZOH
Gvi_T_b = Kv*Ts/2*[1 1];             Gvi_T_a = [1 -1];
Gvi_Z_b = Kv*Ts;                     Gvi_Z_a = [1 -1];

fprintf('PR    b = [%.10g %.10g %.10g], a = [1 %.10g %.10g]\n', PR_b, PR_a(2:3));
fprintf('Notch b = [%.10g %.10g %.10g], a = [1 %.10g %.10g]\n', NO_b, NO_a(2:3));
fprintf('SOGI-D b = [%.10g %.10g %.10g], a = [1 %.10g %.10g]\n', SD_b, SD_a(2:3));
fprintf('SOGI-Q b = [%.10g %.10g %.10g], a = [1 %.10g %.10g]\n', SQ_b, SQ_a(2:3));
fprintf('PI ap b = [%.10g %.10g];  PI PLL b = [%.10g %.10g]\n', PIv_b, PIp_b);

%% Doi chieu bang c2d va kiem tra du tru on dinh (Control System Toolbox)
if exist('c2d', 'file')
    s = tf('s');  z = tf('z', Ts);
    opt = c2dOptions('Method', 'tustin', 'PrewarpFrequency', w0);
    PRz_chk = c2d(Kp_i + Kr_i*s/(s^2 + 2*wrc*s + w0^2), Ts, opt);
    disp('c2d PR (phai trung voi PR_b, PR_a):'); PRz_chk
    PRz  = tf(PR_b, PR_a, Ts);
    Givz = c2d(1/(L*s + rL), Ts, 'zoh');            % doi tuong ZOH (chinh xac tai thoi diem lay mau)
    Li   = PRz*Givz*z^-1;                            % + tre tinh toan 1 chu ky
    figure; margin(Li); title('Vong dong so: PR_z * G_{ZOH} * z^{-1}');
    fprintf('Cuc kin vong dong: max|z| = %.6f\n', max(abs(pole(feedback(Li, 1)))));
    Ti   = feedback(Li, 1);
    Lv   = tf(PIv_b, PIv_a, Ts)*tf(NO_b, NO_a, Ts)*Ti*c2d(Kv/s, Ts, 'zoh');
    figure; margin(Lv); title('Vong ap so');
end
