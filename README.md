# DỰ ÁN HỌC MÁY: PHÂN TÍCH GIỎ HÀNG VÀ PHÁT HIỆN CÁC SẢN PHẨM THƯỜNG ĐƯỢC MUA KÈM (MARKET BASKET ANALYSIS)

> **Báo cáo Tiểu luận môn học: Học máy (Machine Learning)**  
> **Trường Đại học Công nghệ Thông tin & Truyền thông - Đại học Thái Nguyên (ICTU)**  
> **Khoa Công nghệ Thông tin**

---

## 👥 THÀNH VIÊN NHÓM THỰC HIỆN (NHÓM 23)

| STT | Họ và tên | Mã sinh viên | Lớp học phần | Vai trò & Nhiệm vụ chính |
|:---:|:---|:---:|:---:|:---|
| 1 | **Trần Văn Thực** | DTC235200734 | CNTT K22H | Nghiên cứu bài toán khai phá tập phổ biến (FIM) và luật kết hợp (ARM) cùng 4 độ đo (`Support`, `Confidence`, `Lift`, `Conviction`); xây dựng pipeline làm sạch dữ liệu, lọc giỏ hàng `< 2` món và chia Hold-out `80/20` chống rò rỉ (`src/data_pipeline.py`); tự cài đặt thuật toán `Apriori` bằng Python kèm theo dõi cắt tỉa ứng viên $C_k \rightarrow L_k$; hoàn thiện sổ tay `bai1/kt1_eda.ipynb` và kiểm thử (`tests/verify_pipeline.py`). |
| 2 | **Nguyễn Đức An Bình** | DTC235200066 | CNTT K22H | Tự cài đặt thuật toán `ECLAT` (biểu diễn dọc TID-set) và đối sánh thời gian chạy, bộ nhớ với `Apriori` & `FP-Growth` (`mlxtend`); thiết kế quy trình **5-Fold CV Grid Search**, **Ablation Study** và hậu xử lý cắt tỉa luật dư thừa (`src/part3_experiments.py`); xây dựng bộ dữ liệu Siêu thị Việt Nam (`data/sieu_thi_viet_nam.csv`), hệ thống trực quan hóa & phân cụm quầy kệ, và ứng dụng web **SmartBasket** (`web_app.py`, `app.py`). |

* **Giảng viên hướng dẫn:** ThS. Nguyễn Tuấn Anh

---

## 📌 TỔNG QUAN NỘI DUNG NGHIÊN CỨU

Đề tài được tổ chức thực hiện xuyên suốt qua **3 giai đoạn kiểm tra** cùng **ứng dụng sản phẩm demo thực tế**:

### 1. Giai đoạn 1 (Bài kiểm tra 1): Khám phá, làm sạch dữ liệu và chống rò rỉ
- **Bộ dữ liệu chuẩn:** *Groceries* (Hahsler et al., 2005) gồm **9.835 hóa đơn** với **169 danh mục sản phẩm** (độ dài trung bình `4,41 ± 3,59` món, độ thưa `97,39%`).
- **Bộ dữ liệu mở rộng (Việt Nam):** `data/sieu_thi_viet_nam.csv` gồm **3.000 hóa đơn** với **44 mặt hàng siêu thị Việt Nam** phục vụ trình diễn ứng dụng POS thực tế.
- **Xử lý chất lượng dữ liệu:** Loại bỏ trùng lặp nội bộ trong giỏ (`set`), lọc bỏ **2.159 hóa đơn chỉ có 1 sản phẩm (`21,95%`)** → còn **7.676 giỏ hợp lệ**.
- **Phân chia chống rò rỉ:** Hold-out `80/20` (`random_state = 42`) với $N_{\text{Train}} = 6.140$ giỏ và $N_{\text{Test}} = 1.536$ giỏ; `TransactionEncoder` chỉ `.fit()` trên tập Train.
- **Sổ tay thực nghiệm:** `bai1/kt1_eda.ipynb`.

### 2. Giai đoạn 2 (Bài kiểm tra 2): Cài đặt, huấn luyện và đối sánh thuật toán
- **Mô hình cơ sở (Baseline):** Chiến lược *Most Popular* (`whole milk`, `Lift = 1,00`, `Train Conf = 31,51%`, `Test Conf = 29,75%`).
- **3 thuật toán khai phá:** `Apriori` (Python tự cài đặt theo BFS), `ECLAT` (Python tự cài đặt theo TID-set DFS) và `FP-Growth` (`mlxtend`).
- **Tính nhất quán toán học:** Cả 3 thuật toán tìm ra chính xác cùng tập **715 tập phổ biến** và **406 luật kết hợp** ở ngưỡng khởi điểm (`min_support = 0,008`, `min_confidence = 0,25`, `min_lift = 1,30`) với `Conf TB = 40,34%` và `Lift TB = 1,82`.
- **Hiệu năng tốc độ:** Khi hạ `min_support` xuống `0,005`, thời gian của Apriori tăng theo hàm mũ lên `5,668s` trong khi FP-Growth chỉ mất `0,125s` (**nhanh gấp 45,2 lần Apriori**).
- **Sổ tay thực nghiệm:** `kt2.ipynb`.

### 3. Giai đoạn 3 (Bài kiểm tra 3): Tối ưu hóa, cải tiến và tổng quát hóa
- **Tối ưu siêu tham số (chỉ trên Train qua 5-Fold CV):** Grid Search qua 108 tổ hợp chọn cấu hình tối ưu cân bằng **`min_support = 0,008`**, **`min_confidence = 0,25`**, **`min_lift = 1,50`**, **`max_len = 3`**.
- **Hậu xử lý & Ablation Study (5-Fold CV vs Hold-out Test 20%):**
  - Lọc giỏ `< 2` món giúp tăng `CV Confidence` (`36,28% → 38,46%`) và giảm gần một nửa độ lệch chuẩn (`Lift Std: 0,106 → 0,058`).
  - Tối ưu tham số + cắt tỉa luật dư thừa (*Redundant Rule Pruning*) rút gọn còn **266 luật** tinh gọn, đạt **`CV Lift TB = 1,816 ± 0,067`**, **`Test Lift TB = 1,784`** (chỉ lệch `-1,76%`, nằm gọn trong `±1 Std`) và **`Test Conf TB = 35,07%`**.
- **Sổ tay & Script tái lập:** `kt3.ipynb`, `run_part3_experiments.py` | **Báo cáo đầy đủ:** `Nhóm 23 - Báo cáo hoàn chỉnh.pdf`, `Nhóm 23 - Bài kiểm tra 3.docx`.

---

## 📁 CẤU TRÚC KHO MÃ NGUỒN CHÍNH

```text
├── data/
│   ├── groceries.csv                    # Bộ dữ liệu chuẩn Groceries (9.835 hóa đơn, 169 mặt hàng)
│   └── sieu_thi_viet_nam.csv            # Bộ dữ liệu giao dịch siêu thị Việt Nam (3.000 hóa đơn, 44 mặt hàng)
├── src/
│   ├── data_pipeline.py                 # Nạp dữ liệu (Groceries & Online Retail CSV), làm sạch, Hold-out 80/20
│   ├── algorithms.py                    # Cài đặt Apriori (trace C_k -> L_k), ECLAT, FP-Growth, phân cụm quầy kệ
│   ├── part3_experiments.py             # Kiểm định chéo 5-Fold CV, Grid Search, Ablation Study, Pruning
│   └── visualizations.py                # Biểu đồ tương tác Plotly & mạng lưới NetworkX
├── web/                                 # Giao diện Web Sản phẩm hiện đại (SmartBasket HTML/CSS/JS)
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── bai1/
│   └── kt1_eda.ipynb                    # Sổ tay Jupyter Giai đoạn 1 (EDA & Tiền xử lý)
├── kt2.ipynb                            # Sổ tay Jupyter Giai đoạn 2 (Apriori, ECLAT, FP-Growth & Benchmark)
├── kt3.ipynb                            # Sổ tay Jupyter Giai đoạn 3 (5-Fold CV Grid Search, Ablation & Test)
├── web_app.py                           # Máy chủ Web Sản phẩm SmartBasket (Starlette + Uvicorn)
├── app.py                               # Ứng dụng Web Demo Streamlit (theo Phụ lục A báo cáo)
├── run_part3_experiments.py             # Script tái lập toàn bộ bảng số liệu & biểu đồ Phần 3
├── generate_all_figures.py              # Script sinh toàn bộ biểu đồ báo cáo (outputs/figures/)
├── generate_report_pdf.py               # Script biên dịch báo cáo PDF hoàn chỉnh (31 trang)
├── generate_part3_docx.py               # Script xuất file Word riêng cho Bài kiểm tra 3 (.docx)
├── generate_vn_dataset.py               # Script sinh dữ liệu siêu thị Việt Nam
├── tests/verify_pipeline.py             # Kiểm thử tính nhất quán 3 thuật toán & pipeline dữ liệu
├── outputs/
│   ├── figures/                         # Toàn bộ biểu đồ PNG độ phân giải cao dùng trong báo cáo
│   └── tables/                          # Bảng kết quả CSV (benchmark, cv_grid_search, ablation, test_eval)
├── docs/BAO_CAO_PHAN_3_VA_RA_SOAT.md    # Tài liệu rà soát tiêu chí Bài 1–2–3
├── Nhóm 23.pdf                          # Báo cáo gốc ban đầu
├── Nhóm 23 - Báo cáo hoàn chỉnh.pdf     # Báo cáo PDF hoàn chỉnh chuẩn ICTU (31 trang)
├── Nhóm 23 - Bài kiểm tra 3.docx        # Báo cáo Word riêng cho Bài kiểm tra 3
├── requirements.txt                     # Danh sách thư viện môi trường thực thi chuẩn
└── README.md                            # Tài liệu tổng quan dự án
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT VÀ TÁI LẬP THỰC NGHIỆM

### 1. Khởi tạo môi trường ảo Python (>= 3.10)
```bash
python -m venv .venv
```
- **Kích hoạt trên Windows (PowerShell):**
  ```powershell
  .venv\Scripts\activate
  ```
- **Kích hoạt trên Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```

### 2. Cài đặt thư viện phụ thuộc
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng Demo Sản phẩm (Web UI)
- **Giao diện Web Sản phẩm Hiện đại (SmartBasket — `http://localhost:8501`):**
  ```bash
  python web_app.py
  ```
- **Hoặc giao diện Streamlit (theo Phụ lục A báo cáo):**
  ```bash
  streamlit run app.py
  ```

### 4. Chạy lại các Sổ tay Jupyter & Thực nghiệm tái lập
```bash
# Kiểm thử pipeline & tính nhất quán thuật toán
python tests/verify_pipeline.py

# Tái lập toàn bộ bảng & biểu đồ Phần 3
python run_part3_experiments.py

# Mở sổ tay Jupyter từng giai đoạn
jupyter notebook bai1/kt1_eda.ipynb
jupyter notebook kt2.ipynb
jupyter notebook kt3.ipynb
```
