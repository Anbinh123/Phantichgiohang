# Demo Sản phẩm: Phân tích Giỏ hàng & Phát hiện Sản phẩm Thường được Mua kèm

Dự án demo được xây dựng dựa trên báo cáo tiểu luận **Nhóm 23 — Học phần Học máy (CNTT K22H, ICTU)**:
- **Đề tài:** Phân tích giỏ hàng và phát hiện các sản phẩm thường được mua kèm (*Market Basket Analysis*)
- **Sinh viên thực hiện:** Trần Văn Thực (`DTC235200734`), Nguyễn Đức An Bình (`DTC235200066`)
- **Giảng viên hướng dẫn:** Nguyễn Tuấn Anh

## Cấu trúc thư mục
- `app.py` — Ứng dụng web demo tương tác (Streamlit) gồm 6 phân hệ:
  1. **Demo Gợi ý Mua kèm (POS & TMĐT)**: Chọn giỏ hàng thực tế hoặc kịch bản mẫu, nhận gợi ý mua kèm kèm Confidence, Lift, Conviction và đối chiếu với mô hình cơ sở (*Most Popular*).
  2. **Khám phá Dữ liệu (EDA)**: Thống kê mô tả, Top 15 sản phẩm, phân bố kích thước giỏ hàng, ma trận đồng xuất hiện Top 8 nhóm sản phẩm, kiểm toán chất lượng dữ liệu; hỗ trợ tải lên file CSV chuẩn Groceries hoặc Online Retail (`InvoiceNo`, `Description`).
  3. **Luật kết hợp & Lọc Lift**: Khai phá luật theo ngưỡng `min_support`, `min_confidence`, `min_lift`, `max_len`, so sánh tác động lọc Lift (`1.00` vs `1.30` vs `1.50`), xuất CSV và kiểm chứng tổng quát hóa trên 20% tập kiểm tra độc lập.
  4. **Mạng lưới & Quầy kệ**: Trực quan hóa đồ thị mạng luật kết hợp có mũi tên định hướng & lọc theo sản phẩm trung tâm (`NetworkX` + `Plotly`), phân cụm thành 4 khu vực quầy kệ và sinh đề xuất bán chéo.
  5. **So sánh Hiệu năng Thuật toán**: Đo thời gian chạy (tách biệt khỏi chi phí theo dõi bộ nhớ) và bộ nhớ đỉnh trực tiếp giữa **Apriori (Python tự cài đặt)**, **ECLAT (Python)** và **FP-Growth (mlxtend)**.
  6. **Lý thuyết & Độ đo**: Trình bày công thức LaTeX `Support`, `Confidence`, `Lift`, `Conviction`, máy tính minh họa 2 chiều trên luật thực tế và bảng theo dõi cắt tỉa ứng viên Apriori (`C_k → L_k`).
- `src/data_pipeline.py` — Nạp dữ liệu (hỗ trợ cả Groceries & Online Retail CSV), làm sạch, lọc giỏ hàng `< 2` món, chia Hold-out `80/20` (`random_state=42`) và mã hóa One-Hot (`TransactionEncoder` chỉ khớp trên tập Train).
- `src/algorithms.py` — Cài đặt Apriori (quét ngang + theo dõi cắt tỉa `C_k → L_k`), ECLAT (dọc TID-set + DFS), FP-Growth (`mlxtend`), đánh giá tập kiểm tra, phân cụm khu vực quầy kệ và engine gợi ý sản phẩm.
- `src/visualizations.py` — Các biểu đồ tương tác bằng Plotly & NetworkX.
- `data/groceries.csv` — Bộ dữ liệu chuẩn Groceries (9.835 giao dịch, 169 mặt hàng).
- `tests/verify_pipeline.py` — Kiểm thử đối chiếu số liệu và tính nhất quán của cả 3 thuật toán.

## Hướng dẫn cài đặt và chạy chương trình
Yêu cầu Python >= 3.10:

```bash
pip install -r requirements.txt

# Cách 1: Chạy giao diện Web Sản phẩm Hiện đại (SmartBasket — http://localhost:8501)
python web_app.py

# Cách 2: Chạy giao diện Streamlit (theo Phụ lục A báo cáo)
streamlit run app.py
```
