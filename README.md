# Thiết Kế Hệ Thống Điều Khiển Chỉnh Lưu Tích Cực 1 Pha
---

##  1. Tham Số Thiết Kế Tham Khảo

| Thông số | Ký hiệu | Giá trị tham khảo |
| :--- | :--- | :--- |
| Điện áp lưới đầu vào | $U$ | $220\text{ VAC} \pm 10\%$ |
| Tần số lưới | $f$ | 50 Hz ± 1% |
| Công suất thiết kế | $P$ | $2\text{ kVA}$ |
| Điện cảm cuộn lọc | $L$ | $5\text{ mH}$ (nội trở $r_L = 0.1\,\Omega$) |
| Tụ điện Bus DC | $C_{dc}$ | $2200\,\mu\text{F}$ |
| Điện áp DC đầu ra | $V_{dc}$ | $400\text{ VDC}$ |

> Tần số đóng cắt $f_s$ không được cho sẵn trong đề — cần tự lựa chọn và biện luận (thường $10-50$ kHz) dựa trên loại van bán dẫn, tổn hao đóng cắt và đáp ứng băng thông vòng dòng điện mong muốn.

---

##  2. Nội Dung Thiết Kế (theo đề bài)

1. **Mô hình hóa** hệ thống chỉnh lưu tích cực 1 pha.
2. **Cấu trúc điều khiển** (sơ đồ khối tổng thể).
3. **Cách thức tính toán bộ điều chỉnh** dòng điện và điện áp một chiều.
4. **Mô phỏng cấu trúc điều khiển** để kiểm chứng.

---

## 3. Bố Cục Nội Dung Chi Tiết

### Phần 1: Mô hình hóa
- Sơ đồ mạch lực bộ chỉnh lưu tích cực 1 pha (cuộn cảm $L$, van bán dẫn, tụ $C_{dc}$, tải).
- Phương trình vi phân phía AC: $L\dfrac{di_s}{dt} = v_s - v_{conv} - r_L i_s$.
- Phương trình cân bằng công suất phía DC: $C_{dc}\dfrac{dv_{dc}}{dt} = \dfrac{v_s i_s}{v_{dc}} - i_{load}$.
- Mô hình hóa tín hiệu nhỏ (small-signal): tuyến tính hóa quanh điểm làm việc $x = X + \hat{x}$.

### Phần 2: Cấu trúc điều khiển
Mạch lực: cầu H 1 pha (4 van bán dẫn + diode ngược) → cuộn cảm $L$ nối lưới, $C_{dc}$ ở đầu ra. Cấu trúc điều khiển 2 mạch vòng lồng nhau (cascade control):
- **Mạch vòng ngoài (vòng điện áp)**: so sánh $u_{dc}^*$ với $u_{dc}$ đo về **qua Notch Filter** (lọc gợn $2\omega_{lưới}$ = 100 Hz trước khi vào bộ điều chỉnh, tránh vòng áp bám theo ripple và bơm hài bậc 3 vào dòng tham chiếu) → **ĐC điện áp (PI có giới hạn/anti-windup)** → biên độ dòng tham chiếu $I_m^*$.
- **Tạo dòng tham chiếu**: $i_s^* = I_m^*\cdot\sin(\theta)$, với $\sin(\theta)$ lấy từ khối **PLL** đồng bộ theo điện áp lưới đo được $e_n$.
- **Mạch vòng trong (vòng dòng điện)**: so sánh $i_s^*$ với $i_s$ đo về → **ĐC dòng điện dùng bộ điều khiển PR** (Proportional-Resonant — bắt buộc về nguyên lý cho hệ 1 pha vì không có sẵn khung dq; PI thường không triệt tiêu hoàn toàn sai lệch bám sin, xem giải thích ở mục thảo luận) → $u_s^*$.
- **Feedforward điện áp lưới**: cộng $e_n$ vào $u_s^*$ (decoupling) để bộ PR chỉ cần xử lý phần động học sai lệch, cải thiện đáp ứng quá độ.
- **Chuẩn hóa chỉ số điều chế**: chia $(u_s^*+e_n)$ cho $v_{dc}$ đo về → chỉ số điều chế $m$, đưa vào khối **PWM** để tạo tín hiệu đóng cắt cho cầu H.
- **Đồng bộ pha lưới — SOGI-PLL**: hệ 1 pha không có sẵn 2 thành phần lệch pha 90° như hệ 3 pha, nên cần khối **SOGI (Second-Order Generalized Integrator)** tạo tín hiệu trực giao từ $e_n$ trước khi đưa vào PLL dạng SRF-PLL (Synchronous Reference Frame):
$$v'(s) = \frac{k\omega_n s}{s^2+k\omega_n s+\omega_n^2}\,e_n(s), \qquad qv'(s) = \frac{k\omega_n^2}{s^2+k\omega_n s+\omega_n^2}\,e_n(s)$$
  trong đó $v'$ đồng pha $e_n$ (đã lọc hài), $qv'$ lệch pha $90^\circ$; $\omega_n=2\pi\cdot50$ rad/s. Cặp $(v', qv')$ qua phép biến đổi Park (dùng $\theta$ ước lượng) tạo thành phần $q$, đưa vào bộ PI của PLL để ép $q\to0$, tích phân ra $\theta$.

### Phần 3: Tính toán bộ điều chỉnh
- **Vòng dòng điện (PR)**: hàm truyền đối tượng $G_{id}(s) \approx \dfrac{V_{dc}}{sL + r_L}$; bộ điều chỉnh $G_{PR}(s) = K_p + \dfrac{K_r s}{s^2+\omega_0^2}$ với $\omega_0 = 2\pi\cdot50$ rad/s. Thiết kế $K_p$ theo phương pháp module tối ưu / đồ thị Bode ($f_{ci}\approx f_s/10$, $PM\ge45^\circ$); chọn $K_r$ để triệt tiêu sai lệch xác lập đúng tần số lưới mà vẫn đảm bảo độ nhạy nhiễu chấp nhận được.
- **Vòng điện áp DC (PI)**: hàm truyền đối tượng $G_{vI}(s)$ từ cân bằng công suất (gần đúng khâu tích phân); thiết kế PI, chọn tần số cắt $f_{cv} \approx 10$–$20\text{ Hz} \ll 100\text{ Hz}$; kết hợp Notch Filter tại $2\omega_{lưới}$ để loại gợn 100 Hz trên bus DC trước khi vào PI.
- Nguyên tắc tách vòng: băng thông vòng áp thấp hơn băng thông vòng dòng ít nhất 5–10 lần.
- *(Phương án thay thế, cần biện luận nếu chọn)*: có thể dùng PI thay PR cho vòng dòng nếu đặt băng thông vòng dòng đủ cao ($f_{ci}\gg 50$ Hz) để sai lệch xác lập đủ nhỏ, hoặc chuyển sang khung dq (cần tạo trục ảo bằng SOGI/trễ $T/4$) — khi đó PI trong dq tương đương về bản chất với PR trong hệ tọa độ tĩnh.
- **Tham số SOGI-PLL** *(khối hỗ trợ để mô phỏng chạy được, không thuộc 2 bộ điều chỉnh chính đề bài yêu cầu, nhưng bắt buộc phải có giá trị cụ thể)*:
  - Hệ số $k$ của SOGI: chọn $k=\sqrt2$ (thỏa hiệp tốt giữa tốc độ đáp ứng và lọc hài bậc cao).
  - Bộ PI của PLL: tuyến tính hóa quanh điểm khóa pha, chọn theo hệ số tắt dần $\zeta\approx0.707$ và tần số tự nhiên vòng PLL $\omega_{n,PLL}$ (băng thông thường 10–20 Hz, thấp hơn hẳn $2\omega_{lưới}=100$ Hz để không bị nhiễu bởi gợn/hài):
$$K_{p,PLL} = \frac{2\zeta\,\omega_{n,PLL}}{V_m}, \qquad K_{i,PLL} = \frac{\omega_{n,PLL}^2}{V_m}$$
  với $V_m=\sqrt2\,U_s$ là biên độ điện áp lưới tại điểm tuyến tính hóa.

### Phần 4: Mô phỏng cấu trúc điều khiển
- Xây dựng sơ đồ mô phỏng trên MATLAB/Simulink (hoặc PSIM) theo đúng cấu trúc điều khiển ở Phần 2, với các tham số đã tính ở Phần 3.
- Đánh giá chế độ xác lập: dạng sóng $V_{dc}$, dòng điện lưới $i_s$ hình sin đồng pha với $u_s$.
- Đánh giá chế độ quá độ: biến động điện áp lưới trong dải $\pm 10\%$, thay đổi tải đột ngột.

---

## 4. Công Cụ Sử Dụng
- **Mô phỏng**: MATLAB/Simulink hoặc PSIM.
- **Tính toán & vẽ Bode**: MATLAB Control System Toolbox / Python.
- **Soạn thảo báo cáo**: LaTeX / MS Word / Markdown.
