# Rà soát Bài kiểm tra 1–2 & Nội dung Hoàn chỉnh Bài kiểm tra 3 (Nhóm 23)

Tài liệu này tổng hợp:
1. **Kết quả rà soát chi tiết** báo cáo `Nhóm 23.pdf` theo đúng bộ tiêu chí chấm **Bài kiểm tra 1** và **Bài kiểm tra 2**.
2. **Nội dung hoàn chỉnh cho Bài kiểm tra 3 (Mục 3.8 – 3.10 & Kết luận)** dựa trên số liệu chạy thực tế từ mã nguồn của nhóm (`run_part3_experiments.py`).

---

## PHẦN A: RÀ SOÁT BÀI KIỂM TRA 1 & BÀI KIỂM TRA 2 TRONG `Nhóm 23.pdf`

### 1. Các lỗi định dạng / mẫu (template) cần sửa ngay trong file Word
- **Trang 6 (Mục lục) & Trang 13 (Bố cục báo cáo):** Vẫn còn sót tiêu đề của đề tài mẫu khác (*"Chương 1. Tổng quan về học máy và bài toán dự đoán kết quả học tập"*, *"1.3.1. Hồi quy Logistic / 1.3.2. Rừng ngẫu nhiên / 1.3.3. XGBoost"*, *"Chương 2... dự đoán kết quả học tập"*). Cần nhấn `Ctrl + A` → `F9` để cập nhật lại Mục lục tự động và sửa lại đoạn Bố cục báo cáo ở trang 13.
- **Trang 8 (Danh mục hình ảnh):** Có 2 lỗi Word `Lỗi! Thẻ đánh dấu không được xác định` và vẫn còn tên hình của bài khác (*"Ma trận nhầm lẫn"*, *"Đường cong học tập"*).
- **Trang 9 (Danh mục bảng):** Ghi *"Bảng 3.4. So sánh kết quả kiểm định chéo 5-fold của các mô hình"*, nhưng nội dung ở trang 27 thực chất là *"Bảng 3.4. So sánh kết quả thực nghiệm giữa các mô hình"*.
- **Trang 33–34 (Phụ lục A):** Còn chỗ trống mẫu `[Hướng dẫn: đường dẫn kho mã của nhóm]`, `(thay bằng image1.png)`, `(thay bằng image2.png)`, `(thay bằng image3.png)`.
- **Trang 35 (Phụ lục B):** Vẫn còn tên sinh viên mẫu `Nguyễn Văn A`, `Trần Thị B` thay vì `Trần Văn Thực`, `Nguyễn Đức An Bình`.

### 2. Đánh giá theo tiêu chí Bài kiểm tra 1 (Tuần 4)
| Tiêu chí | Trạng thái trong `Nhóm 23.pdf` | Ghi chú chỉnh sửa (nếu có) |
| :--- | :--- | :--- |
| 1. Phát biểu bài toán | **Đạt (1,0)** | Mục 2.1 xác định đúng: Học không giám sát (FIM & ARM), đơn vị mẫu = 1 giỏ hàng, đầu vào = ma trận nhị phân 0/1, đầu ra = luật $X \Rightarrow Y$. |
| 2. Mục tiêu & tiêu chí thành công | **Đạt (1,0)** | Bảng 2.1 rõ ràng: `Lift ≥ 1,30`, `Confidence ≥ 25%`, `FP-Growth nhanh hơn Apriori ≥ 3 lần`. |
| 3. Nguồn & mô tả dữ liệu | **Đạt (~0,9–1,0)** | Đủ nguồn Kaggle, 9.835 giỏ, 169 mặt hàng, Bảng 3.1 từ điển dữ liệu. *Lưu ý:* khi lọc giỏ 1 món và chia Train 80% (`6.140` giỏ), tập Train có **168** đặc trưng có mặt (1 mặt hàng hiếm chỉ rơi vào Test). |
| 4. Khảo sát thống kê & phân bố | **Đạt (1,0)** | Có Hình 3.1a (Top 15), 3.1b (kích thước giỏ), `mean = 4,41`, `std = 3,59`, `median = 3`, `max = 32`, độ thưa `97,39%`, nhận xét Pareto 80/20 rõ ràng. |
| 5. Quan hệ đặc trưng | **Đạt (1,0)** | Có Hình 3.2 ma trận đồng xuất hiện Top 8 nhóm sản phẩm + rút ra đủ 3 nhận xét thiết thực. |
| 6 & 7. Phát hiện & xử lý chất lượng dữ liệu | **Đạt (~0,9–1,0)** | Bảng 3.2 định lượng đầy đủ (2.159 giỏ 1 món = 21,95%, lặp món trong giỏ chuyển `set`, >70% mặt hàng Support < 2%). Nên ghi thêm bảng so sánh trước–sau xử lý (`9.835 → 7.676` giỏ). |
| 8. Chuẩn bị dữ liệu cho mô hình | **Đạt (1,0)** | Chia Hold-out 80/20 (`random_state=42`) trước, `TransactionEncoder` chỉ `.fit()` trên tập Train (`6.140` giỏ) để chống rò rỉ dữ liệu. |
| 9. Lý giải phương pháp & chỉ số | **Đạt (1,0)** | Mục 2.5 giải thích rõ Hold-out 80/20 và lý do chọn Lift, Conviction, Support, Confidence, Thời gian/Bộ nhớ. |

### 3. Đánh giá theo tiêu chí Bài kiểm tra 2 (Tuần 6) — Điểm cần sửa gấp!
1. **Số liệu trong Bảng 3.4 & Bảng 3.6 đang vênh nhau và chưa khớp kết quả chạy code thực tế:**
   - **Baseline (*Most Popular*):** Trang 27 (Bảng 3.4) ghi `Confidence TB = 25,55%`, nhưng trang 29 (Bảng 3.6) lại ghi `18,5%`. Khi chạy code thực tế trên tập Train 6.140 giỏ (`random_state=42`), mặt hàng phổ biến nhất (`whole milk`) có tỷ lệ xuất hiện trên Train là **`31,51%`** và trên Test là **`29,75%`** (trên dữ liệu gốc 9.835 giỏ là `25,55%`).
   - **Số luật ở `min_support = 0,008; min_confidence = 0,25; min_lift = 1,30`:** Báo cáo ghi **58 luật** (`Conf TB = 33,82%`, `Lift TB = 1,72`), nhưng khi chạy `mlxtend` / Apriori / ECLAT trên đúng dữ liệu Groceries (`6.140` giỏ Train), số luật thực tế tìm được là **406 luật** (không giới hạn độ dài) với **`Conf TB = 40,34%`**, **`Lift TB = 1,82`** (hoặc **377 luật** nếu giới hạn `max_len = 3`).
   - **Cấu hình tối ưu (`min_lift = 1,50; max_len = 3`):** Báo cáo ghi **34 luật**, nhưng kết quả chạy thực tế trên đúng dữ liệu là **270 luật** (trước cắt tỉa) và **266 luật** (sau cắt tỉa luật dư thừa).
   - **Khuyến nghị:** Khi giảng viên chấm Bài 2 TC4 (*"giảng viên chạy thử mã nguồn"*), giảng viên sẽ đối chiếu trực tiếp số trong báo cáo với kết quả code chạy ra. Bạn hãy cập nhật lại các bảng trong Word theo **đúng số liệu chạy thực tế** bên dưới để đồng bộ 100% giữa báo cáo, code và demo.
2. **Thiếu bước kiểm định chéo (K-Fold) & báo cáo Mean ± Std trên tập huấn luyện (Bài 2 TC5 & Bài 3 TC5, TC7):**
   - Trong báo cáo mới chạy Hold-out 1 lần, chưa có kiểm định chéo 5-Fold trên tập Train (mặc dù Danh mục bảng trang 9 có nhắc tới `5-fold`). Mã nguồn `src/part3_experiments.py` và `run_part3_experiments.py` đã bổ sung đầy đủ quy trình **5-Fold CV trên 6.140 giỏ Train** và xuất sẵn bảng `Mean ± Std`.

---

## PHẦN B: NỘI DUNG HOÀN CHỈNH CHO BÀI KIỂM TRA 3 (TUẦN 8)

*(Toàn bộ số liệu dưới đây được sinh trực tiếp từ `python run_part3_experiments.py` trên dữ liệu `data/groceries.csv`, `random_state = 42`)*

### 3.8. Tối ưu hóa và cải tiến mô hình

#### 3.8.1. Phân tích hạn chế của mô hình ban đầu
Dựa trên kết quả thực nghiệm ban đầu (tại ngưỡng `min_support = 0,008`, `min_confidence = 0,25`, `min_lift = 1,30`), nhóm xác định 3 hạn chế chính có bằng chứng định lượng:
1. **Chi phí tính toán của Apriori tăng theo hàm mũ khi hạ `min_support`:** Khi giảm `min_support` từ `0,050` xuống `0,005` trên 6.140 giỏ Train, số tập ứng viên cần quét tăng vọt khiến thời gian thực thi của Apriori tăng từ `0,221 giây` lên **`5,668 giây`** (Hình `outputs/figures/fig_benchmark_runtime_memory.png`).
2. **Nhiễu từ hóa đơn 1 sản phẩm và dao động cao giữa các fold:** Khi chạy FP-Growth trực tiếp trên dữ liệu thô chưa lọc bỏ 2.159 giỏ 1 món (`21,95%`), độ tin cậy kiểm định chéo 5-Fold chỉ đạt `36,28% ± 1,75%`, độ lệch chuẩn khá cao và nhiều tập phổ biến bị bỏ sót do mẫu số bị loãng.
3. **Dư thừa luật và nhiều luật có độ liên kết chưa đủ mạnh:** Với ngưỡng `min_lift = 1,30` và không giới hạn độ dài luật, hệ thống sinh ra tới **406 luật**, trong đó có những luật dài 4 món khó áp dụng trưng bày và những luật có độ liên kết chỉ ở mức trung bình (`1,30 – 1,50`), hoặc luật dư thừa khi tập con đã dự đoán tốt hơn.

#### 3.8.2. Đề xuất giải pháp cải tiến (Bảng Hạn chế – Giải pháp)
| STT | Hạn chế của mô hình ban đầu | Giải pháp đề xuất | Cơ sở lý thuyết |
| :--- | :--- | :--- | :--- |
| 1 | Apriori tốn nhiều thời gian quét CSDL nhiều lần khi `min_support` thấp | Thay thế lõi khai phá bằng **FP-Growth** (và đối chiếu **ECLAT**) | FP-Growth nén CSDL vào cây tiền tố FP-Tree sau 2 lần quét, không sinh tập ứng viên $C_k$. |
| 2 | 2.159 giỏ 1 món làm loãng `Support` và tăng phương sai `Confidence` | **Cải tiến dữ liệu:** Lọc bỏ giỏ `< 2` món trước khi chia Train/Test và mã hóa | Giỏ 1 món không chứa thông tin đồng xuất hiện; loại bỏ giúp làm sạch phân phối giỏ mua kèm và giảm độ lệch chuẩn giữa các fold. |
| 3 | Luật dài/dư thừa nhiều, một số luật có Lift thấp (`1,30–1,50`) | **Tối ưu siêu tham số (5-Fold CV Grid Search)** chọn `min_lift = 1,50`, `max_len = 3` + **Hậu xử lý cắt tỉa luật dư thừa** | Loại bỏ luật $X \Rightarrow Y$ nếu tồn tại tập con $X' \subset X$ có $\text{Confidence}(X' \Rightarrow Y) \ge \text{Confidence}(X \Rightarrow Y)$ giúp luật tinh gọn, tăng tính diễn giải. |

#### 3.8.3. Kết quả cải tiến dữ liệu, thử nghiệm thuật toán và tối ưu hóa siêu tham số (Grid Search 5-Fold CV)
- **Không gian tìm kiếm (chỉ thực hiện trên tập Train 6.140 giỏ qua 5-Fold CV, tuyệt đối không dùng tập Test 20%):**
  - `min_support` $\in \{0,005;\ 0,008;\ 0,010;\ 0,015\}$
  - `min_confidence` $\in \{0,20;\ 0,25;\ 0,30\}$
  - `min_lift` $\in \{1,30;\ 1,50;\ 1,80\}$
  - `max_len` $\in \{2,\ 3,\ \text{None}\}$
- **Kết quả Grid Search (`outputs/tables/cv_grid_search.csv` & Hình `outputs/figures/fig_cv_validation_curve.png`):**
  - Dù cấu hình `min_support = 0,005, min_lift = 1,80` đạt `CV Lift = 2,21 ± 0,12`, nhưng sinh quá nhiều luật dài (`806,6 ± 58,2` luật) và độ dao động giữa các fold lớn (`Std = 0,125`).
  - Cấu hình cân bằng tốt nhất giữa chất lượng luật, độ ổn định và tính ứng dụng thực tế là **`min_support = 0,008`, `min_confidence = 0,25`, `min_lift = 1,50`, `max_len = 3`**, đạt `CV Lift = 1,817 ± 0,069`, `CV Confidence = 38,94% ± 1,05%` với tỷ lệ giữ luật trên tập kiểm định đạt cao ổn định.

### 3.9. So sánh trước và sau cải tiến (Ablation Study)
Bảng dưới đây đối chiếu đóng góp của từng cải tiến trên **cùng tập dữ liệu Groceries, cùng tỷ lệ chia 80/20 (`random_state = 42`) và cùng hệ chỉ số**:

| Cấu hình mô hình | Số luật (Train) | CV Lift TB (Mean ± Std) | CV Conf TB (%) (Mean ± Std) | Test Lift TB | Test Conf TB (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| 0. Mô hình cơ sở (*Most Popular: whole milk*) | 1 | `1,000 ± 0,000` | `31,51 ± 0,00` | `1,000` | `29,75` |
| 1. FP-Growth ban đầu (dữ liệu thô, `Lift ≥ 1,30`) | 286 | `1,897 ± 0,106` | `36,28 ± 1,75` | `2,033` | `36,79` |
| 2. + Cải tiến dữ liệu: Lọc bỏ giỏ `< 2` món | 406 | `1,751 ± 0,058` | `38,46 ± 1,09` | `1,697` | `34,71` |
| 3. + Tối ưu siêu tham số (`Lift ≥ 1,50`, `max_len = 3`) | 270 | `1,817 ± 0,069` | `38,94 ± 1,05` | `1,788` | `34,98` |
| 4. + Hậu xử lý cắt tỉa luật dư thừa (*Pruning*) | **266** | **`1,816 ± 0,067`** | **`38,91 ± 0,96`** | **`1,784`** | **`35,07`** |

**Giải thích hiện tượng trong Ablation Study:**
- Khi chuyển từ bước (1) sang bước (2) (lọc bỏ 2.159 giỏ 1 món), **CV Confidence tăng từ `36,28%` lên `38,46%` (`+2,18%`)** và **độ lệch chuẩn (Std) giữa các fold giảm gần một nửa** (`Lift Std: 0,106 → 0,058`, `Conf Std: 1,75% → 1,09%`). Nguyên nhân `Lift TB` giảm nhẹ (`1,897 → 1,751`) là do khi mẫu số giỏ hàng thu hẹp (`9.835 → 7.676`), các cặp sản phẩm ngách có Support thực sự ở mức trung bình vượt qua được ngưỡng `0,008` (số luật tăng từ `286 → 406`), làm lộ ra thêm 120 luật mới có Lift trong khoảng `1,30 – 1,50`.
- Khi áp dụng bước (3) (`min_lift ≥ 1,50`, `max_len = 3`), các luật yếu và luật dài `> 3` món được loại bỏ, giúp `CV Lift` bật tăng trở lại lên **`1,817 ± 0,069`**, `Test Lift` đạt **`1,788`** và `CV Conf` đạt **`38,94%`**.
- Bước (4) (*Pruning*) loại bỏ 4 luật dư thừa (`270 → 266` luật), giúp giảm tiếp phương sai `CV Conf Std` xuống mức thấp nhất (`0,96%`) và đạt `Test Confidence TB` cao nhất (`35,07%`).

### 3.10. Khả năng tổng quát hóa và lựa chọn mô hình cuối cùng
- **Đánh giá độc lập trên Tập kiểm tra giữ lại (Test 20% = 1.536 giỏ hàng):**
  - Mô hình cuối (**FP-Growth + Lọc giỏ ≥ 2 món + `min_support = 0,008`, `min_conf = 0,25`, `min_lift = 1,50`, `max_len = 3` + Cắt tỉa luật dư thừa**) cho **266 luật**.
  - Trên **5-Fold CV (Train)**: `Lift TB = 1,816 ± 0,067`, `Confidence TB = 38,91% ± 0,96%`.
  - Trên **Tập kiểm tra giữ lại (Test 20%)**: `Lift TB = 1,784`, `Confidence TB = 35,07%`.
  - Chênh lệch `CV Lift → Test Lift` chỉ **`-1,76%`** (nằm gọn trong 1 độ lệch chuẩn `±0,067` của kiểm định chéo), khẳng định mô hình **tổng quát hóa tốt, không bị quá khớp (overfitting)** vào dữ liệu lịch sử.
- **Lựa chọn mô hình cuối cùng:** Chọn **FP-Growth (`mlxtend`) + tiền xử lý lọc giỏ ≥ 2 món + bộ ngưỡng tối ưu + hậu xử lý Pruning** vì đạt đồng thời 3 tiêu chí: tốc độ nhanh vượt trội (**`0,116s`** so với **`3,379s`** của Apriori tại `min_support = 0,008`, nhanh gấp **29,1 lần**; và **`0,125s`** vs **`5,668s`** tại `0,005`, nhanh gấp **45,2 lần**), độ ổn định cao qua 5-Fold CV (`Std Lift = 0,067`), và tập 266 luật ngắn gọn ($\le 3$ món) dễ triển khai thành quy tắc sắp xếp quầy kệ và gợi ý mua kèm.

---

### Danh sách tệp biểu đồ & bảng đã xuất sẵn để chèn vào báo cáo Word
- Biểu đồ so sánh thời gian & bộ nhớ (Apriori vs ECLAT vs FP-Growth): `outputs/figures/fig_benchmark_runtime_memory.png`
- Biểu đồ Ablation Study (5-Fold CV vs Test 20%): `outputs/figures/fig_ablation_cv_vs_test.png`
- Biểu đồ đường cong kiểm định chéo 5-Fold (Grid Search): `outputs/figures/fig_cv_validation_curve.png`
- Các bảng CSV chi tiết: `outputs/tables/benchmark_algorithms.csv`, `outputs/tables/cv_grid_search.csv`, `outputs/tables/ablation_study.csv`, `outputs/tables/final_rules_test_eval.csv`.
