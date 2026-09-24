# Thiết Kế Hệ Thống Điều Khiển Chỉnh Lưu Tích Cực 1 Pha (Active PFC Boost Converter)

Dự án thiết kế, mô hình hóa và mô phỏng hệ thống điều khiển bộ biến đổi PFC kiểu Boost 1 pha hòa lưới, dựa trên bài giảng và tài liệu môn Điều khiển Điện tử công suất.

---

##  1. Thông Số Thiết Kế Hệ Thống

| Thông số | Ký hiệu | Giá trị định mức |
| :--- | :--- | :--- |
| Điện áp lưới đầu vào | $U_s$ | $220\text{ VAC} \pm 10\% / 50\text{ Hz} \pm 1\%$ |
| Công suất định mức | $P$ | $2\text{ kVA}$ |
| Điện áp DC đầu ra | $V_{dc}$ | $400\text{ VDC}$ |
| Điện cảm cuộn lọc | $L$ | $5\text{ mH}$ (Nội trở $r_L = 0.1\,\Omega$) |
| Tụ điện Bus DC | $C_{dc}$ | $2200\,\mu\text{F}$ |
| Tần số đóng cắt | $f_s$ | $20\text{ kHz} \div 50\text{ kHz}$ |

---

##  2. Yêu Cầu Kỹ Thuật & Chỉ Tiêu Đánh Giá

- **Hệ số công suất (Power Factor - PF)**: $\approx 1$ ($PF > 0.99$).
- **Độ méo dạng sóng hài tổng (THD)**: $THD < 5\%$ (IEEE 519) hoặc $THD < 2.5\%$ (IEEE 1547/IEC 61727).
- **Điện áp DC ra**: Ổn định ở $400\text{ VDC}$, độ nhấp nhô điện áp (voltage ripple) nhỏ trong giới hạn cho phép.
- **Tính vững chãi**: Hệ thống hoạt động ổn định khi điện áp lưới biến động $\pm 10\%$ và tải thay đổi đột ngột ($100\% \leftrightarrow 50\%$).

---

##  3. Bố Cục Nội Dung Chi Tiết

### Phần 1: Tổng quan & Thông số Mạch lực
- Tổng quan về bài toán hiệu chỉnh hệ số công suất (PFC) và bộ biến đổi Boost.
- Phân tích và chốt bộ thông số mạch lực theo yêu cầu thiết kế.
- Lựa chọn tần số đóng cắt $f_s$ cho van bán dẫn.

### Phần 2: Cấu trúc Điều khiển Hệ thống
- Xây dựng sơ đồ khối cấu trúc điều khiển 2 mạch vòng lồng nhau (Cascade Control):
  - **Mạch vòng trong (Inner Current Loop)**: Điều khiển dòng điện qua cuộn cảm $i_L$ bám theo tín hiệu hình sin $i_L^*$.
  - **Mạch vòng ngoài (Outer Voltage Loop)**: Điều khiển và ổn định điện áp DC ra $V_{dc} = 400\text{V}$.
- Tích hợp khâu **Feedforward điện áp lưới** ($1/\bar{u}_{in}^2$) để bù biến động điện áp đầu vào.
- Khâu tạo dạng sóng $v_{ac}(t) = |\sin(\omega t)|$ đồng pha với điện áp lưới.

### Phần 3: Mô hình hóa & Tính toán Bộ điều chỉnh
- **Mô hình hóa tín hiệu nhỏ (Small-Signal Modeling)**:
  - Phương trình vi phân trung bình trong 1 chu kỳ $T_s$.
  - Tuyến tính hóa tín hiệu nhỏ xung quanh điểm cân bằng $x = X + \hat{x}$.
- **Tính toán Mạch vòng Dòng điện ($R_i$)**:
  - Hàm truyền đối tượng dòng điện $G_{id}(s) \approx \frac{V_{dc}}{sL + r_L}$.
  - Thiết kế bộ điều chỉnh PI dòng điện $R_i(s)$ bằng phương pháp đồ thị Bode (Tần số cắt $f_{ci} \approx f_s / 10$, độ trữ pha $PM \ge 45^\circ$).
- **Tính toán Mạch vòng Điện áp ($R_v$)**:
  - Hàm truyền đối tượng điện áp $G_{vI}(s)$ dựa trên cân bằng công suất.
  - Thiết kế bộ điều chỉnh PI điện áp $R_v(s)$ (Tần số cắt $f_{cv} \approx 10\text{ Hz} \div 20\text{ Hz} \ll 100\text{ Hz}$ để lọc thành phần nhấp nhô 100Hz trên bus DC).

### Phần 4: Mô phỏng & Đánh giá Kết quả
- Xây dựng sơ đồ mô phỏng chi tiết trên MATLAB/Simulink (hoặc PSIM).
- **Đánh giá chế độ xác lập**: Điện áp $V_{dc}$, dòng điện lưới $i_s$ hình sin đồng pha với $u_s$.
- **Phân tích phổ FFT**: Xác định độ méo sóng hài $THD$ của dòng điện lưới.
- **Đánh giá chế độ quá độ**:
  - Biến động điện áp lưới $U_s \in [198\text{V}, 242\text{V}]$.
  - Biến động tải đột ngột từ $2\text{ kVA} \rightarrow 1\text{ kVA} \rightarrow 2\text{ kVA}$.

### Phần 5: Rời rạc hóa & Điều khiển Số (Mở rộng)
- Rời rạc hóa bộ điều khiển PI từ miền $s$ sang miền $z$ (phương pháp Tustin/Euler).

---

##  4. Phân Công Công Việc (Nhóm 2 Thành viên)

| Thành viên | Nhiệm vụ chính | Chi tiết công việc & Sản phẩm bàn giao |
| :--- | :--- | :--- |
| **Thành viên 1** | **Mô hình hóa toán học & Tính toán bộ điều khiển** | - Tổng quan bài toán & Thông số mạch lực (Phần 1).<br>- Xây dựng mô hình tín hiệu nhỏ cho bộ Boost PFC (Phần 3.1).<br>- Tính toán tham số bộ điều chỉnh PI Dòng điện $R_i(s)$ & Điện áp $R_v(s)$ bằng phương pháp Bode (Phần 3.2, 3.3).<br>- Soạn thảo báo cáo phần Lý thuyết & Tính toán toán học. |
| **Thành viên 2** | **Cấu trúc điều khiển & Mô phỏng kiểm chứng** | - Thiết lập sơ đồ khối cấu trúc điều khiển, khâu Feedforward & Đồng pha (Phần 2).<br>- Xây dựng mô hình mô phỏng trên MATLAB/Simulink / PSIM (Phần 4.1).<br>- Chạy mô phỏng quá độ (thay đổi áp lưới, đột biến tải), phân tích phổ FFT/THD & đo hệ số PF (Phần 4.2, 4.3).<br>- (Mở rộng) Rời rạc hóa bộ điều khiển sang miền $z$ (Phần 5).<br>- Tổng hợp file mô phỏng & Đồ thị kết quả. |

---

##  5. Công Cụ Sử Dụng
- **Mô phỏng**: MATLAB/Simulink.
- **Tính toán & Đồ thị**: MATLAB Control System Toolbox / Python.
- **Soạn thảo**: LaTeX / MS Word / Markdown.
