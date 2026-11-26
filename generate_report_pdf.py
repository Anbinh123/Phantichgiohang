"""Generate clean academic PDF report for Nhóm 23 matching Nhóm 20 style and Bài 1–3 rubrics."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "outputs" / "figures"
HTML_PATH = ROOT / "outputs" / "nhom23_report.html"
PDF_PATH = ROOT / "Nhóm 23 - Báo cáo hoàn chỉnh.pdf"


def img_uri(filename: str) -> str:
    return (FIG_DIR / filename).resolve().as_uri()


def build_html() -> str:
    html = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<title>Báo cáo Tiểu luận Học máy - Nhóm 23 - ICTU</title>
<style>
  @page {
    size: A4;
    margin: 2.2cm 2.0cm 2.2cm 2.8cm;
    @bottom-center {
      content: counter(page);
      font-family: "Times New Roman", Times, serif;
      font-size: 11pt;
      color: #334155;
    }
  }
  @page :first {
    margin: 1.5cm 1.5cm 1.5cm 1.5cm;
    @bottom-center { content: ""; }
  }
  body {
    font-family: "Times New Roman", Times, serif;
    font-size: 12.5pt;
    line-height: 1.48;
    color: #0F172A;
    margin: 0;
    padding: 0;
    text-align: justify;
  }
  /* Cover Page */
  .cover-outer {
    border: 3px double #0F172A;
    padding: 1.4cm 1.3cm;
    height: 24.8cm;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
  }
  .cover-uni {
    font-size: 13.5pt;
    font-weight: bold;
    text-transform: uppercase;
    line-height: 1.35;
  }
  .cover-dept {
    font-size: 13pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-top: 4pt;
  }
  .cover-rule {
    width: 140pt;
    border-top: 1.5pt solid #0F172A;
    margin: 8pt auto 0 auto;
  }
  .cover-logo {
    width: 105pt;
    height: auto;
    margin: 12pt auto;
  }
  .cover-report {
    font-size: 18pt;
    font-weight: bold;
    text-transform: uppercase;
    margin-top: 6pt;
  }
  .cover-course {
    font-size: 13.5pt;
    font-weight: bold;
    margin-top: 6pt;
  }
  .cover-topic-label {
    font-size: 13.5pt;
    font-weight: bold;
    margin-top: 18pt;
  }
  .cover-topic {
    font-size: 15.5pt;
    font-weight: bold;
    text-transform: uppercase;
    line-height: 1.4;
    margin: 8pt auto 0 auto;
    max-width: 92%;
  }
  .cover-meta {
    text-align: left;
    margin: 20pt auto 0 auto;
    width: 85%;
    font-size: 12.5pt;
    line-height: 1.65;
  }
  .cover-meta table {
    width: 100%;
    border: none;
    margin: 0;
  }
  .cover-meta td {
    border: none;
    padding: 3pt 6pt;
    vertical-align: top;
  }
  .cover-footer {
    font-size: 12.5pt;
    font-weight: bold;
    margin-top: 16pt;
  }

  /* Page breaks & section headings */
  .page-break { page-break-before: always; }
  h1.front-title {
    font-size: 15pt;
    font-weight: bold;
    text-transform: uppercase;
    text-align: center;
    margin: 0 0 14pt 0;
  }
  h1.chapter-title {
    font-size: 15pt;
    font-weight: bold;
    text-transform: uppercase;
    text-align: left;
    margin: 0 0 12pt 0;
    line-height: 1.35;
    border-bottom: 1.5pt solid #1E3A8A;
    padding-bottom: 4pt;
    color: #0F172A;
  }
  h2 {
    font-size: 13pt;
    font-weight: bold;
    margin: 14pt 0 6pt 0;
    color: #0F172A;
    page-break-after: avoid;
  }
  h3 {
    font-size: 12.5pt;
    font-weight: bold;
    margin: 10pt 0 4pt 0;
    color: #1E293B;
    page-break-after: avoid;
  }
  p {
    margin: 0 0 7pt 0;
    text-indent: 20pt;
  }
  p.no-indent { text-indent: 0; }
  ul, ol {
    margin: 4pt 0 8pt 18pt;
    padding-left: 12pt;
  }
  li { margin-bottom: 4pt; }

  /* Tables */
  table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 8pt 0 12pt 0;
    font-size: 10.5pt;
    line-height: 1.35;
    page-break-inside: avoid;
  }
  table.data-table th, table.data-table td {
    border: 0.75pt solid #475569;
    padding: 5pt 6pt;
    vertical-align: middle;
    text-align: left;
  }
  table.data-table th {
    background-color: #E2E8F0;
    font-weight: bold;
    text-align: center;
  }
  table.data-table td.num, table.data-table th.num {
    text-align: center;
  }
  .table-caption {
    font-size: 11pt;
    font-weight: bold;
    text-align: center;
    margin: 10pt 0 4pt 0;
    page-break-after: avoid;
  }

  /* Figures */
  .figure-block {
    text-align: center;
    margin: 10pt 0 10pt 0;
    page-break-inside: avoid;
  }
  .figure-block img {
    max-width: 96%;
    max-height: 9.2cm;
    height: auto;
    border: 0.5pt solid #CBD5E1;
  }
  .figure-caption {
    font-size: 11pt;
    font-style: italic;
    margin-top: 4pt;
    text-align: center;
  }

  /* Math & Code blocks */
  .formula-box {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 6pt 18pt;
    font-style: italic;
    font-size: 12pt;
  }
  .formula-expr {
    flex: 1;
    text-align: center;
  }
  .formula-num {
    width: 40pt;
    text-align: right;
    font-style: normal;
  }
  pre.code-block {
    background: #F8FAFC;
    border: 0.75pt solid #CBD5E1;
    border-left: 3pt solid #1E3A8A;
    padding: 7pt 9pt;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 9.5pt;
    line-height: 1.38;
    white-space: pre-wrap;
    margin: 6pt 0 10pt 0;
    page-break-inside: avoid;
  }
  code {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 10.5pt;
    background: #F1F5F9;
    padding: 0 3pt;
    border-radius: 2pt;
  }
  .dots-line {
    border-bottom: 1pt dotted #64748B;
    height: 18pt;
    margin-bottom: 4pt;
  }
  .toc-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 4pt;
    font-size: 11.2pt;
  }
  .toc-row span:first-child {
    padding-right: 14pt;
  }
  .toc-l1 { font-weight: bold; margin-top: 5pt; }
  .toc-l2 { padding-left: 18pt; }
  .toc-l3 { padding-left: 34pt; font-size: 11pt; }
  .sig-row {
    display: flex;
    justify-content: space-between;
    margin-top: 24pt;
    text-align: center;
  }
  .sig-col { width: 45%; }
</style>
</head>
<body>

<!-- ==================== TRANG BÌA ==================== -->
<div class="cover-outer">
  <div>
    <div class="cover-uni">TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG</div>
    <div class="cover-dept">KHOA CÔNG NGHỆ THÔNG TIN</div>
    <div class="cover-rule"></div>
    <img class="cover-logo" src="{img_uri('ictu_logo.png')}" alt="ICTU Logo" />
  </div>

  <div>
    <div class="cover-report">BÁO CÁO TIỂU LUẬN</div>
    <div class="cover-course">HỌC PHẦN: HỌC MÁY (MACHINE LEARNING)</div>
    <div class="cover-topic-label">ĐỀ TÀI:</div>
    <div class="cover-topic">
      PHÂN TÍCH GIỎ HÀNG VÀ PHÁT HIỆN<br/>
      CÁC SẢN PHẨM THƯỜNG ĐƯỢC MUA KÈM
    </div>
  </div>

  <div class="cover-meta">
    <table>
      <tr><td style="width: 34%;"><strong>Giảng viên hướng dẫn:</strong></td><td>ThS. Nguyễn Tuấn Anh</td></tr>
      <tr><td><strong>Lớp học phần:</strong></td><td>CNTT K22H</td></tr>
      <tr><td><strong>Nhóm thực hiện:</strong></td><td>Nhóm 23</td></tr>
      <tr><td><strong>Sinh viên thực hiện:</strong></td><td>1. Trần Văn Thực – MSV: DTC235200734<br/>2. Nguyễn Đức An Bình – MSV: DTC235200066</td></tr>
    </table>
  </div>

  <div class="cover-footer">Thái Nguyên, Tháng 11 Năm 2026</div>
</div>

<!-- ==================== NHẬN XÉT GIẢNG VIÊN ==================== -->
<div class="page-break"></div>
<h1 class="front-title">NHẬN XÉT CỦA GIẢNG VIÊN</h1>
<p class="no-indent"><strong>1. Về hình thức và bố cục báo cáo:</strong></p>
<div class="dots-line"></div><div class="dots-line"></div><div class="dots-line"></div>
<p class="no-indent" style="margin-top:10pt;"><strong>2. Về nội dung và kết quả thực hiện:</strong></p>
<div class="dots-line"></div><div class="dots-line"></div><div class="dots-line"></div><div class="dots-line"></div>
<p class="no-indent" style="margin-top:10pt;"><strong>3. Về tinh thần, thái độ làm việc của nhóm:</strong></p>
<div class="dots-line"></div><div class="dots-line"></div><div class="dots-line"></div>
<p class="no-indent" style="margin-top:12pt;"><strong>4. Điểm đánh giá:</strong></p>
<table class="data-table">
  <thead>
    <tr><th class="num" style="width:8%;">STT</th><th style="width:46%;">Họ và tên sinh viên</th><th class="num" style="width:22%;">Điểm số</th><th class="num" style="width:24%;">Điểm chữ</th></tr>
  </thead>
  <tbody>
    <tr><td class="num">1</td><td>Trần Văn Thực – DTC235200734</td><td></td><td></td></tr>
    <tr><td class="num">2</td><td>Nguyễn Đức An Bình – DTC235200066</td><td></td><td></td></tr>
  </tbody>
</table>
<div style="text-align:right; margin-top:26pt; padding-right:24pt;">
  <em>Thái Nguyên, ngày ... tháng ... năm 2026</em><br/>
  <strong>Giảng viên hướng dẫn</strong><br/>
  <em>(Ký và ghi rõ họ tên)</em><br/><br/><br/><br/>
  <strong>ThS. Nguyễn Tuấn Anh</strong>
</div>

<!-- ==================== BẢNG PHÂN CÔNG NHIỆM VỤ ==================== -->
<div class="page-break"></div>
<h1 class="front-title">BẢNG PHÂN CÔNG NHIỆM VỤ</h1>
<p class="no-indent">Toàn bộ mã nguồn thực nghiệm, dữ liệu chuẩn và ứng dụng demo sản phẩm được tổ chức tại thư mục dự án (gồm <code>app.py</code>, <code>run_part3_experiments.py</code>, <code>src/</code>, <code>tests/verify_pipeline.py</code>).</p>
<table class="data-table">
  <thead>
    <tr><th class="num" style="width:7%;">STT</th><th style="width:23%;">Họ và tên</th><th style="width:55%;">Nhiệm vụ phụ trách (Bài 1, Bài 2 &amp; Bài 3)</th><th class="num" style="width:15%;">Mức độ hoàn thành</th></tr>
  </thead>
  <tbody>
    <tr>
      <td class="num">1</td>
      <td><strong>Trần Văn Thực</strong><br/>MSV: DTC235200734</td>
      <td>
        • Nghiên cứu lý thuyết khai phá tập phổ biến (FIM), luật kết hợp (ARM) và các độ đo Support, Confidence, Lift, Conviction.<br/>
        • Xây dựng pipeline nạp, làm sạch dữ liệu Groceries/Online Retail, lọc giỏ hàng &lt; 2 món và chia Hold-out 80/20 chống rò rỉ (<code>src/data_pipeline.py</code>).<br/>
        • Tự cài đặt thuật toán Apriori bằng Python kèm cơ chế theo dõi cắt tỉa ứng viên <i>C<sub>k</sub> → L<sub>k</sub></i> và triển khai FP-Growth (<code>mlxtend</code>).<br/>
        • Soạn thảo phần Mở đầu, Chương 1, Chương 2 và kiểm thử tính nhất quán (<code>tests/verify_pipeline.py</code>).
      </td>
      <td class="num">100%</td>
    </tr>
    <tr>
      <td class="num">2</td>
      <td><strong>Nguyễn Đức An Bình</strong><br/>MSV: DTC235200066</td>
      <td>
        • Cài đặt thuật toán bổ trợ ECLAT (biểu diễn dọc TID-set) và đo lường đối sánh thời gian chạy, bộ nhớ đỉnh giữa Apriori, ECLAT và FP-Growth theo ngưỡng support.<br/>
        • Thiết kế quy trình kiểm định chéo 5-Fold CV, Grid Search, Ablation Study và thuật toán hậu xử lý cắt tỉa luật dư thừa (<code>src/part3_experiments.py</code>, <code>run_part3_experiments.py</code>).<br/>
        • Trực quan hóa mạng lưới luật kết hợp, phân cụm quầy kệ siêu thị và xây dựng ứng dụng demo tương tác Streamlit 7 phân hệ (<code>app.py</code>, <code>src/visualizations.py</code>).<br/>
        • Soạn thảo Chương 3, Kết luận và Phụ lục hướng dẫn tái lập.
      </td>
      <td class="num">100%</td>
    </tr>
  </tbody>
</table>

<!-- ==================== LỜI CAM ĐOAN ==================== -->
<div class="page-break"></div>
<h1 class="front-title">LỜI CAM ĐOAN</h1>
<p>Chúng em xin cam đoan báo cáo tiểu luận <strong>“PHÂN TÍCH GIỎ HÀNG VÀ PHÁT HIỆN CÁC SẢN PHẨM THƯỜNG ĐƯỢC MUA KÈM”</strong> là kết quả làm việc của nhóm dưới sự hướng dẫn của giảng viên ThS. Nguyễn Tuấn Anh. Các số liệu, bảng biểu và kết quả thực nghiệm trình bày trong báo cáo là hoàn toàn trung thực, được sinh trực tiếp từ mã nguồn của nhóm (<code>run_part3_experiments.py</code>, <code>tests/verify_pipeline.py</code>) và có thể tái lập chính xác.</p>
<p><strong>Khai báo sử dụng công cụ AI tạo sinh:</strong> Nhóm có sử dụng công cụ AI tạo sinh để hỗ trợ tra cứu kiến thức học thuật, tham khảo giải pháp tối ưu cấu trúc mã nguồn Python/Streamlit, phát hiện lỗi và rà soát cách diễn đạt trong báo cáo. Mọi kết quả thực nghiệm đều được nhóm kiểm chứng bằng cách chạy lại trực tiếp trên dữ liệu thật và chịu trách nhiệm hoàn toàn về nội dung trình bày.</p>
<p>Nếu phát hiện có bất kỳ sự gian lận nào, chúng em xin hoàn toàn chịu trách nhiệm trước giảng viên và nhà trường.</p>
<div style="text-align:right; margin-top:20pt; padding-right:16pt;">
  <em>Thái Nguyên, ngày ... tháng ... năm 2026</em><br/>
  <strong>NHÓM SINH VIÊN THỰC HIỆN</strong><br/>
  <em>(Ký và ghi rõ họ tên)</em>
</div>
<div class="sig-row">
  <div class="sig-col"><strong>Trần Văn Thực</strong></div>
  <div class="sig-col"><strong>Nguyễn Đức An Bình</strong></div>
</div>

<!-- ==================== LỜI CẢM ƠN ==================== -->
<div class="page-break"></div>
<h1 class="front-title">LỜI CẢM ƠN</h1>
<p>Trước hết, chúng em xin gửi lời cảm ơn chân thành đến thầy <strong>Nguyễn Tuấn Anh</strong>, giảng viên hướng dẫn học phần Học máy, đã tận tình giảng dạy, cung cấp nền tảng kiến thức và đưa ra những góp ý quý báu giúp nhóm hoàn thiện báo cáo tiểu luận với đề tài “Phân tích giỏ hàng và phát hiện các sản phẩm thường được mua kèm”.</p>
<p>Trong quá trình thực hiện qua ba giai đoạn kiểm tra, nhóm đã có cơ hội vận dụng bài bản quy trình một dự án học máy thực tế: từ phát biểu bài toán, khảo sát EDA, xử lý chất lượng dữ liệu chống rò rỉ, cài đặt và so sánh các thuật toán khai phá luật kết hợp, cho đến kiểm định chéo 5-Fold CV, tối ưu siêu tham số, thực hiện Ablation Study và đóng gói thành ứng dụng web demo phục vụ gợi ý mua kèm.</p>
<p>Mặc dù đã nỗ lực hoàn thành báo cáo với tinh thần nghiêm túc và trung thực cao nhất, do kinh nghiệm thực tế còn hạn chế, báo cáo khó tránh khỏi những thiếu sót. Chúng em rất mong nhận được những ý kiến nhận xét, đóng góp từ thầy để tiếp tục hoàn thiện kiến thức chuyên môn.</p>
<p>Cuối cùng, chúng em xin kính chúc thầy sức khỏe, hạnh phúc và gặt hái nhiều thành công trong công tác giảng dạy.</p>
<p style="text-align:right; margin-top:18pt;"><em>Chúng em xin chân thành cảm ơn!</em></p>
<div style="text-align:right; margin-top:12pt;">
  <strong>Nhóm sinh viên thực hiện</strong><br/>
  <em>Trần Văn Thực – Nguyễn Đức An Bình</em>
</div>

<!-- ==================== MỤC LỤC & TỪ VIẾT TẮT ==================== -->
<div class="page-break"></div>
<h1 class="front-title">MỤC LỤC</h1>
<div class="toc-row toc-l1"><span>NHẬN XÉT CỦA GIẢNG VIÊN</span><span>__P_NHAN_XET__</span></div>
<div class="toc-row toc-l1"><span>BẢNG PHÂN CÔNG NHIỆM VỤ</span><span>__P_PHAN_CONG__</span></div>
<div class="toc-row toc-l1"><span>LỜI CAM ĐOAN</span><span>__P_CAM_DOAN__</span></div>
<div class="toc-row toc-l1"><span>LỜI CẢM ƠN</span><span>__P_CAM_ON__</span></div>
<div class="toc-row toc-l1"><span>DANH MỤC KÝ HIỆU VÀ TỪ VIẾT TẮT</span><span>__P_VIET_TAT__</span></div>
<div class="toc-row toc-l1"><span>DANH MỤC HÌNH VẼ VÀ BẢNG BIỂU</span><span>__P_HINH_BANG__</span></div>
<div class="toc-row toc-l1"><span>MỞ ĐẦU</span><span>__P_MO_DAU__</span></div>
<div class="toc-row toc-l1"><span>CHƯƠNG 1. CƠ SỞ LÝ THUYẾT VÀ MÔ HÌNH HÓA BÀI TOÁN</span><span>__P_CH1__</span></div>
<div class="toc-row toc-l2"><span>1.1. Phát biểu bài toán học máy và hàm mục tiêu</span><span>__P_1_1__</span></div>
<div class="toc-row toc-l2"><span>1.2. Mục tiêu thực tế và tiêu chí thành công định lượng</span><span>__P_1_2__</span></div>
<div class="toc-row toc-l2"><span>1.3. Cơ sở lý thuyết mô hình cơ sở và các thuật toán sử dụng</span><span>__P_1_3__</span></div>
<div class="toc-row toc-l2"><span>1.4. Hệ thống các chỉ số đánh giá và lý giải lựa chọn</span><span>__P_1_4__</span></div>
<div class="toc-row toc-l1"><span>CHƯƠNG 2. DỮ LIỆU THỰC NGHIỆM, TIỀN XỬ LÝ VÀ QUY TRÌNH HUẤN LUYỆN</span><span>__P_CH2__</span></div>
<div class="toc-row toc-l2"><span>2.1. Nguồn dữ liệu và từ điển đặc trưng</span><span>__P_2_1__</span></div>
<div class="toc-row toc-l2"><span>2.2. Khảo sát thống kê và phân bố dữ liệu (EDA)</span><span>__P_2_2__</span></div>
<div class="toc-row toc-l2"><span>2.3. Phân tích quan hệ đồng xuất hiện giữa các đặc trưng</span><span>__P_2_3__</span></div>
<div class="toc-row toc-l2"><span>2.4. Phát hiện, xử lý chất lượng dữ liệu và so sánh trước – sau</span><span>__P_2_4__</span></div>
<div class="toc-row toc-l2"><span>2.5. Chuẩn bị dữ liệu chống rò rỉ và quy trình kiểm định chéo 5-Fold CV</span><span>__P_2_5__</span></div>
<div class="toc-row toc-l1"><span>CHƯƠNG 3. THỰC NGHIỆM, TỐI ƯU HÓA VÀ ĐÁNH GIÁ MÔ HÌNH</span><span>__P_CH3__</span></div>
<div class="toc-row toc-l2"><span>3.1. Môi trường thực nghiệm và thiết lập tái lập</span><span>__P_3_1__</span></div>
<div class="toc-row toc-l2"><span>3.2. Kết quả thực nghiệm ban đầu và so sánh hiệu năng tính toán</span><span>__P_3_2__</span></div>
<div class="toc-row toc-l2"><span>3.3. Phân tích hạn chế của mô hình ban đầu và đề xuất giải pháp cải tiến</span><span>__P_3_3__</span></div>
<div class="toc-row toc-l2"><span>3.4. Cải tiến dữ liệu, thử nghiệm hậu xử lý và tối ưu siêu tham số (Grid Search 5-Fold)</span><span>__P_3_4__</span></div>
<div class="toc-row toc-l2"><span>3.5. So sánh trước – sau cải tiến (Ablation Study) và khả năng tổng quát hóa</span><span>__P_3_5__</span></div>
<div class="toc-row toc-l2"><span>3.6. Trực quan hóa mạng luật kết hợp và đề xuất ứng dụng thực tiễn</span><span>__P_3_6__</span></div>
<div class="toc-row toc-l1"><span>KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN</span><span>__P_KET_LUAN__</span></div>
<div class="toc-row toc-l1"><span>TÀI LIỆU THAM KHẢO</span><span>__P_TLTK__</span></div>
<div class="toc-row toc-l1"><span>PHỤ LỤC A. HƯỚNG DẪN CÀI ĐẶT, TÁI LẬP VÀ CHẠY DEMO</span><span>__P_PHU_LUC__</span></div>

<div class="page-break"></div>
<h1 class="front-title">DANH MỤC KÝ HIỆU VÀ TỪ VIẾT TẮT</h1>
<table class="data-table">
  <thead>
    <tr><th class="num" style="width:10%;">STT</th><th style="width:22%;">Viết tắt</th><th style="width:68%;">Ý nghĩa đầy đủ</th></tr>
  </thead>
  <tbody>
    <tr><td class="num">1</td><td><strong>ARM</strong></td><td>Association Rule Mining – Khai phá luật kết hợp</td></tr>
    <tr><td class="num">2</td><td><strong>FIM</strong></td><td>Frequent Itemset Mining – Khai phá tập phổ biến</td></tr>
    <tr><td class="num">3</td><td><strong>MBA</strong></td><td>Market Basket Analysis – Phân tích giỏ hàng</td></tr>
    <tr><td class="num">4</td><td><strong>AOV</strong></td><td>Average Order Value – Giá trị trung bình mỗi đơn hàng</td></tr>
    <tr><td class="num">5</td><td><strong>BFS / DFS</strong></td><td>Breadth-First Search / Depth-First Search – Tìm kiếm chiều rộng / chiều sâu</td></tr>
    <tr><td class="num">6</td><td><strong>FP-Growth</strong></td><td>Frequent Pattern Growth – Thuật toán phát triển mẫu phổ biến trên cây tiền tố FP-Tree</td></tr>
    <tr><td class="num">7</td><td><strong>ECLAT</strong></td><td>Equivalence Class Transformation – Thuật toán biến đổi lớp tương đương theo TID-set</td></tr>
    <tr><td class="num">8</td><td><strong>CV</strong></td><td>Cross-Validation – Kiểm định chéo</td></tr>
    <tr><td class="num">9</td><td><strong>EDA</strong></td><td>Exploratory Data Analysis – Phân tích khám phá dữ liệu</td></tr>
    <tr><td class="num">10</td><td><strong>TID</strong></td><td>Transaction Identifier – Mã định danh hóa đơn giao dịch</td></tr>
  </tbody>
</table>

<!-- ==================== DANH MỤC HÌNH & BẢNG ==================== -->
<div class="page-break"></div>
<h1 class="front-title">DANH MỤC HÌNH VẼ VÀ ĐỒ THỊ</h1>
<table class="data-table">
  <thead><tr><th class="num" style="width:14%;">Hình</th><th style="width:74%;">Tên hình vẽ / đồ thị</th><th class="num" style="width:12%;">Trang</th></tr></thead>
  <tbody>
    <tr><td class="num">Hình 1.1</td><td>Quy trình thực hiện dự án phân tích giỏ hàng qua 5 giai đoạn</td><td class="num">__F_1_1__</td></tr>
    <tr><td class="num">Hình 2.1</td><td>Phân bố tần suất Top 15 sản phẩm phổ biến nhất và kích thước giỏ hàng (Groceries)</td><td class="num">__F_2_1__</td></tr>
    <tr><td class="num">Hình 2.2</td><td>Ma trận tỷ lệ đồng xuất hiện giữa Top 8 nhóm sản phẩm chính</td><td class="num">__F_2_2__</td></tr>
    <tr><td class="num">Hình 2.3</td><td>Sơ đồ quy trình Hold-out 80/20 kết hợp kiểm định chéo 5-Fold CV chống rò rỉ dữ liệu</td><td class="num">__F_2_3__</td></tr>
    <tr><td class="num">Hình 3.1</td><td>Đường cong so sánh thời gian thực thi và bộ nhớ đỉnh (Apriori, ECLAT, FP-Growth)</td><td class="num">__F_3_1__</td></tr>
    <tr><td class="num">Hình 3.2</td><td>Đường cong kiểm định chéo 5-Fold (Lift TB ± Std) theo min_support và min_lift</td><td class="num">__F_3_2__</td></tr>
    <tr><td class="num">Hình 3.3</td><td>So sánh Lift và Confidence (5-Fold CV vs Hold-out Test 20%) qua từng bước cải tiến</td><td class="num">__F_3_3__</td></tr>
    <tr><td class="num">Hình 3.4</td><td>Phân bố Support, Confidence và Lift của 266 luật kết hợp cuối cùng</td><td class="num">__F_3_4__</td></tr>
    <tr><td class="num">Hình 3.5</td><td>Mạng lưới 15 luật kết hợp mạnh nhất theo Lift (FP-Growth sau tối ưu &amp; Pruning)</td><td class="num">__F_3_5__</td></tr>
    <tr><td class="num">Hình A.1</td><td>Giao diện ứng dụng web demo sản phẩm chạy trên Streamlit</td><td class="num">__F_A_1__</td></tr>
  </tbody>
</table>

<div class="page-break"></div>
<h1 class="front-title">DANH MỤC BẢNG BIỂU</h1>
<table class="data-table">
  <thead><tr><th class="num" style="width:14%;">Bảng</th><th style="width:74%;">Tên bảng biểu</th><th class="num" style="width:12%;">Trang</th></tr></thead>
  <tbody>
    <tr><td class="num">Bảng 1.1</td><td>Mục tiêu thực tế, mục tiêu học máy và tiêu chí thành công định lượng</td><td class="num">__T_1_1__</td></tr>
    <tr><td class="num">Bảng 1.2</td><td>Tổng hợp mô hình cơ sở, thuật toán sử dụng và tham số chính</td><td class="num">__T_1_2__</td></tr>
    <tr><td class="num">Bảng 2.1</td><td>Từ điển dữ liệu bộ giao dịch bán lẻ Groceries</td><td class="num">__T_2_1__</td></tr>
    <tr><td class="num">Bảng 2.2</td><td>Thống kê định lượng các vấn đề chất lượng dữ liệu và giải pháp xử lý</td><td class="num">__T_2_2__</td></tr>
    <tr><td class="num">Bảng 2.3</td><td>So sánh bộ dữ liệu trước và sau bước tiền xử lý làm sạch</td><td class="num">__T_2_3__</td></tr>
    <tr><td class="num">Bảng 2.4</td><td>Phân bố kích thước các tập dữ liệu và 5 Fold kiểm định chéo trên tập Train</td><td class="num">__T_2_4__</td></tr>
    <tr><td class="num">Bảng 3.1</td><td>So sánh kết quả ban đầu giữa mô hình cơ sở và 3 thuật toán (min_support = 0,008; Lift ≥ 1,30)</td><td class="num">__T_3_1__</td></tr>
    <tr><td class="num">Bảng 3.2</td><td>So sánh thời gian thực thi và bộ nhớ đỉnh của Apriori, ECLAT và FP-Growth theo min_support</td><td class="num">__T_3_2__</td></tr>
    <tr><td class="num">Bảng 3.3</td><td>Bảng phân tích hạn chế mô hình ban đầu và đề xuất giải pháp cải tiến</td><td class="num">__T_3_3__</td></tr>
    <tr><td class="num">Bảng 3.4</td><td>Không gian tìm kiếm và Top cấu hình từ Grid Search trên kiểm định chéo 5-Fold CV</td><td class="num">__T_3_4__</td></tr>
    <tr><td class="num">Bảng 3.5</td><td>Nghiên cứu đóng góp từng cải tiến (Ablation Study) trên 5-Fold CV và Hold-out Test 20%</td><td class="num">__T_3_5__</td></tr>
    <tr><td class="num">Bảng 3.6</td><td>Top 8 luật kết hợp tiêu biểu của mô hình cuối cùng (sau tối ưu và Pruning)</td><td class="num">__T_3_6__</td></tr>
    <tr><td class="num">Bảng 3.7</td><td>Đối chiếu chỉ tiêu kỹ thuật cam kết ban đầu với kết quả mô hình cuối cùng</td><td class="num">__T_3_7__</td></tr>
    <tr><td class="num">Bảng 3.8</td><td>Đề xuất phân khu sắp xếp quầy kệ siêu thị từ phân cụm mạng luật kết hợp</td><td class="num">__T_3_8__</td></tr>
  </tbody>
</table>

<!-- ==================== MỞ ĐẦU ==================== -->
<div class="page-break"></div>
<h1 class="chapter-title">MỞ ĐẦU</h1>
<h2>1. Lý do chọn đề tài</h2>
<p>Trong hoạt động bán lẻ hiện đại và thương mại điện tử, mỗi hóa đơn thanh toán thường chứa nhiều mặt hàng được khách hàng lựa chọn trong cùng một chuyến mua sắm. Việc khai phá tự động những nhóm sản phẩm thường xuyên xuất hiện cùng nhau giúp nhà quản lý tối ưu hóa sơ đồ trưng bày quầy kệ, thiết kế các gói khuyến mãi bán chéo (cross-selling) và xây dựng tính năng gợi ý sản phẩm theo thời gian thực (“Thường được mua kèm”) nhằm gia tăng giá trị trung bình trên mỗi đơn hàng (AOV).</p>
<p>Đề tài <strong>“Phân tích giỏ hàng và phát hiện các sản phẩm thường được mua kèm”</strong> giải quyết trọn vẹn bài toán thực tế trên bằng kỹ thuật khai phá tập phổ biến (FIM) và luật kết hợp (ARM) trên bộ dữ liệu giao dịch chuẩn Groceries (9.835 hóa đơn), xuyên suốt từ giai đoạn khảo sát – tiền xử lý (Bài 1), cài đặt – đánh giá mô hình cơ sở (Bài 2), đến tối ưu hóa siêu tham số, kiểm định chéo 5-Fold và Ablation Study (Bài 3).</p>

<h2>2. Mục tiêu và nhiệm vụ nghiên cứu</h2>
<ul>
  <li><strong>Nghiên cứu lý thuyết:</strong> Hệ thống hóa bài toán khai phá tập phổ biến, luật kết hợp và các độ đo cốt lõi (<code>Support</code>, <code>Confidence</code>, <code>Lift</code>, <code>Conviction</code>).</li>
  <li><strong>Tiền xử lý &amp; chống rò rỉ:</strong> Làm sạch dữ liệu giao dịch, định lượng và xử lý ngoại lai (giỏ hàng 1 món), chia tập Hold-out 80/20 (<code>random_state=42</code>) và chỉ khớp bộ mã hóa trên tập huấn luyện.</li>
  <li><strong>Cài đặt &amp; đối sánh thuật toán:</strong> Tự cài đặt thuật toán <code>Apriori</code> và <code>ECLAT</code> bằng Python, kết hợp sử dụng <code>FP-Growth</code> (thư viện <code>mlxtend</code>), so sánh thời gian chạy và bộ nhớ theo ngưỡng <code>min_support</code>, đồng thời đối chiếu với mô hình cơ sở (<em>Most Popular</em>).</li>
  <li><strong>Tối ưu hóa &amp; kiểm chứng (Bài 3):</strong> Phân tích hạn chế mô hình ban đầu, áp dụng cải tiến dữ liệu, thực hiện Grid Search trên kiểm định chéo 5-Fold CV (tuyệt đối không dùng tập Test để chọn tham số), cắt tỉa luật dư thừa, thực hiện Ablation Study và kiểm chứng độc lập trên tập Test giữ lại 20%.</li>
  <li><strong>Ứng dụng thực tiễn:</strong> Trực quan hóa mạng lưới luật kết hợp, phân cụm đề xuất bố trí quầy kệ và đóng gói thành ứng dụng demo web tương tác bằng Streamlit.</li>
</ul>

<h2>3. Kết cấu báo cáo</h2>
<p>Ngoài phần Mở đầu, Kết luận, Tài liệu tham khảo và Phụ lục, báo cáo được tổ chức thành 3 chương:</p>
<ul>
  <li><strong>Chương 1. Cơ sở lý thuyết và mô hình hóa bài toán:</strong> Phát biểu bài toán học máy, bảng mục tiêu – tiêu chí thành công, cơ sở lý thuyết của mô hình cơ sở cùng 3 thuật toán Apriori, FP-Growth, ECLAT và hệ chỉ số đánh giá.</li>
  <li><strong>Chương 2. Dữ liệu thực nghiệm, tiền xử lý và quy trình huấn luyện:</strong> Mô tả bộ dữ liệu Groceries, từ điển đặc trưng, khảo sát thống kê EDA, xử lý chất lượng dữ liệu trước–sau và quy trình 5-Fold CV chống rò rỉ.</li>
  <li><strong>Chương 3. Thực nghiệm, tối ưu hóa và đánh giá mô hình:</strong> Trình bày kết quả ban đầu, so sánh thời gian và bộ nhớ, phân tích hạn chế, Grid Search trên 5-Fold CV, Ablation Study, đánh giá tổng quát hóa trên tập Test, trực quan hóa mạng luật và đề xuất ứng dụng thực tế.</li>
</ul>

<!-- ==================== CHƯƠNG 1 ==================== -->
<div class="page-break"></div>
<h1 class="chapter-title">CHƯƠNG 1. CƠ SỞ LÝ THUYẾT VÀ MÔ HÌNH HÓA BÀI TOÁN</h1>

<h2>1.1. Phát biểu bài toán học máy và hàm mục tiêu</h2>
<p>Bài toán phân tích giỏ hàng được mô hình hóa dưới dạng bài toán <strong>Học không giám sát (Unsupervised Learning)</strong> — cụ thể là Khai phá tập phổ biến (Frequent Itemset Mining) và Sinh luật kết hợp (Association Rule Mining) trên dữ liệu giao dịch thưa:</p>
<ul>
  <li><strong>Đơn vị mẫu:</strong> Một giỏ hàng (mỗi hóa đơn thanh toán độc lập <i>T<sub>i</sub></i>).</li>
  <li><strong>Đầu vào (Đặc trưng):</strong> Tập các sản phẩm xuất hiện trong từng hóa đơn, được mã hóa thành ma trận nhị phân <code>0/1</code> (One-Hot Encoding) kích thước <i>N × d</i>, trong đó <i>d = 169</i> mặt hàng (trên tập Train 6.140 giỏ có 168 mặt hàng xuất hiện ít nhất 1 lần).</li>
  <li><strong>Đầu ra:</strong> Tập các luật kết hợp có ý nghĩa dạng <i>X ⇒ Y</i> (<i>X ∩ Y = ∅</i>), diễn giải rằng khi khách hàng mua tập sản phẩm <i>X</i> thì có xu hướng mua kèm tập sản phẩm <i>Y</i>, thỏa mãn đồng thời các ngưỡng <code>min_support</code>, <code>min_confidence</code> và <code>min_lift</code>.</li>
</ul>

<div class="figure-block">
  <img src="{img_uri('fig_1_1_pipeline.png')}" alt="Quy trình thực hiện dự án" />
  <div class="figure-caption">Hình 1.1: Quy trình thực hiện dự án phân tích giỏ hàng qua 5 giai đoạn.</div>
</div>

<h2>1.2. Mục tiêu thực tế và tiêu chí thành công định lượng</h2>
<p>Để chuyển hóa mục tiêu kinh doanh siêu thị thành tiêu chí kỹ thuật kiểm chứng được, nhóm xác lập Bảng 1.1:</p>
<div class="table-caption">Bảng 1.1: Mục tiêu thực tế, mục tiêu học máy và tiêu chí thành công định lượng</div>
<table class="data-table">
  <thead>
    <tr><th style="width:30%;">Mục tiêu thực tế</th><th style="width:32%;">Mục tiêu học máy</th><th class="num" style="width:16%;">Chỉ số chính</th><th class="num" style="width:22%;">Mức mong muốn</th></tr>
  </thead>
  <tbody>
    <tr><td>Phát hiện các sản phẩm thực sự thường được mua kèm (không phải ngẫu nhiên)</td><td>Khai phá luật kết hợp có tương quan dương vượt mốc gợi ý đại trà</td><td class="num"><strong>Lift</strong></td><td class="num"><strong>≥ 1,30</strong> (vượt Baseline 1,00)</td></tr>
    <tr><td>Đảm bảo độ tin cậy khi hiển thị gợi ý cho khách hàng tại POS / web</td><td>Tối ưu xác suất có điều kiện khách mua thêm món gợi ý</td><td class="num"><strong>Confidence</strong></td><td class="num"><strong>≥ 25,0%</strong></td></tr>
    <tr><td>Đảm bảo khả năng mở rộng khi hạ thấp ngưỡng hỗ trợ xuống 0,008 – 0,005</td><td>Giảm chi phí quét CSDL và tránh bùng nổ tập ứng viên trung gian</td><td class="num"><strong>Thời gian chạy (s)</strong></td><td class="num">FP-Growth nhanh hơn Apriori <strong>≥ 3 lần</strong></td></tr>
  </tbody>
</table>

<h2>1.3. Cơ sở lý thuyết mô hình cơ sở và các thuật toán sử dụng</h2>
<ul>
  <li><strong>Mô hình cơ sở (Baseline – Most Popular):</strong> Luôn gợi ý mặt hàng xuất hiện nhiều nhất trong toàn bộ tập huấn luyện (trên Groceries là <code>whole milk</code>) cho mọi khách hàng mà không xét đến các món đang nằm trong giỏ. Với cách gợi ý này, xác suất mua thêm đúng bằng tỷ lệ xuất hiện mặc định (<code>Confidence = Support</code>), tương ứng <code>Lift = 1,00</code> (không tạo ra hiệu ứng thúc đẩy mua kèm).</li>
  <li><strong>Thuật toán 1 – Apriori (tự cài đặt Python):</strong> Khai thác nguyên lý phản đơn điệu (mọi tập con của tập phổ biến đều phải phổ biến) để duyệt theo chiều rộng (BFS). Ở mỗi mức độ dài <i>k</i>, thuật toán sinh tập ứng viên <i>C<sub>k</sub></i> từ <i>L<sub>k−1</sub></i>, cắt tỉa các ứng viên có tập con không phổ biến, rồi quét toàn bộ danh sách giao dịch để đếm tần suất lọc ra <i>L<sub>k</sub></i>. Đây là chuẩn đối chiếu trực quan nhưng chậm khi <code>min_support</code> nhỏ do phải quét CSDL nhiều lượt.</li>
  <li><strong>Thuật toán 2 – FP-Growth (thư viện <code>mlxtend</code>):</strong> Nén toàn bộ CSDL giao dịch vào cấu trúc cây tiền tố nén <strong>FP-Tree</strong> kết hợp bảng liên kết <em>Header Table</em> chỉ sau 2 lần quét CSDL, sau đó khai phá trực tiếp các mẫu phổ biến theo cơ sở mẫu điều kiện mà không cần sinh tập ứng viên <i>C<sub>k</sub></i>.</li>
  <li><strong>Thuật toán 3 – ECLAT (tự cài đặt Python, bổ trợ):</strong> Chuyển biểu diễn dữ liệu sang dạng dọc theo danh sách mã giao dịch (<em>TID-set</em>) cho từng mặt hàng và duyệt theo chiều sâu (DFS), tính nhanh Support của tổ hợp bằng phép giao tập hợp <code>|TID(X) ∩ TID(Y)|</code>, rất hiệu quả trên ma trận giỏ hàng thưa.</li>
</ul>

<div class="table-caption">Bảng 1.2: Tổng hợp mô hình cơ sở, thuật toán sử dụng và tham số chính</div>
<table class="data-table">
  <thead>
    <tr><th style="width:24%;">Mô hình / Thuật toán</th><th style="width:28%;">Tham số chính</th><th class="num" style="width:20%;">Cấu hình ban đầu</th><th style="width:28%;">Mục đích kỹ thuật</th></tr>
  </thead>
  <tbody>
    <tr><td>Baseline (Most Popular)</td><td><code>top_popular</code></td><td class="num">Top-1 (<code>whole milk</code>)</td><td>Xác lập mốc sàn <code>Lift = 1,00</code> để đối chứng</td></tr>
    <tr><td>Apriori (Python tự cài)</td><td><code>min_support</code>, <code>max_len</code></td><td class="num"><code>0,008</code>, <code>None</code></td><td>Chuẩn đối chiếu tốc độ, bộ nhớ và vết cắt tỉa <i>C<sub>k</sub> → L<sub>k</sub></i></td></tr>
    <tr><td>ECLAT (Python tự cài)</td><td><code>min_support</code>, <code>max_len</code></td><td class="num"><code>0,008</code>, <code>None</code></td><td>Kiểm chứng biểu diễn dọc TID-set trên dữ liệu thưa</td></tr>
    <tr><td>FP-Growth (<code>mlxtend</code>)</td><td><code>min_support</code>, <code>min_conf</code>, <code>min_lift</code>, <code>max_len</code></td><td class="num"><code>0,008</code>, <code>0,25</code>, <code>1,30</code>, <code>None</code></td><td>Lõi khai phá tốc độ cao; tinh chỉnh tối ưu ở Bài 3</td></tr>
  </tbody>
</table>

<h2>1.4. Hệ thống các chỉ số đánh giá và lý giải lựa chọn</h2>
<p>Với luật kết hợp <i>X ⇒ Y</i> trên tập <i>N</i> hóa đơn, chất lượng luật và hiệu năng thuật toán được đo bằng 4 độ đo chuẩn:</p>
<div class="formula-box"><div class="formula-expr">Support(X ⇒ Y) = P(X ∪ Y) = |{T ∈ D : X ∪ Y ⊆ T}| / N</div><div class="formula-num">(1.1)</div></div>
<div class="formula-box"><div class="formula-expr">Confidence(X ⇒ Y) = P(X ∪ Y) / P(X)</div><div class="formula-num">(1.2)</div></div>
<div class="formula-box"><div class="formula-expr">Lift(X ⇒ Y) = Confidence(X ⇒ Y) / P(Y) = P(X ∪ Y) / [P(X) · P(Y)]</div><div class="formula-num">(1.3)</div></div>
<div class="formula-box"><div class="formula-expr">Conviction(X ⇒ Y) = [1 − P(Y)] / [1 − Confidence(X ⇒ Y)]</div><div class="formula-num">(1.4)</div></div>
<p><strong>Lý giải lựa chọn:</strong> Trong siêu thị, các mặt hàng thiết yếu như <code>whole milk</code> (25,55%) xuất hiện rất phổ biến; nếu chỉ dùng <code>Confidence</code>, nhiều sản phẩm không liên quan đi kèm với sữa vẫn có điểm cao. Chỉ số <strong>Lift ≥ 1,30</strong> giúp loại bỏ trùng hợp ngẫu nhiên (chỉ giữ cặp có tần suất đi cùng cao hơn kỳ vọng độc lập ít nhất 30%), còn <strong>Conviction</strong> đo độ sai lệch có hướng, giúp phân biệt chiều gợi ý đáng tin cậy hơn giữa <i>X ⇒ Y</i> và <i>Y ⇒ X</i>.</p>

<!-- ==================== CHƯƠNG 2 ==================== -->
<div class="page-break"></div>
<h1 class="chapter-title">CHƯƠNG 2. DỮ LIỆU THỰC NGHIỆM, TIỀN XỬ LÝ VÀ QUY TRÌNH HUẤN LUYỆN</h1>

<h2>2.1. Nguồn dữ liệu và từ điển đặc trưng</h2>
<ul>
  <li><strong>Nguồn dữ liệu:</strong> Bộ dữ liệu giao dịch bán lẻ chuẩn <strong>Groceries</strong> do Hahsler, Grün &amp; Hornik (2005) công bố trong gói <code>arules</code> và kho dữ liệu mở Kaggle (<code>https://www.kaggle.com/datasets/irfanasrullah/groceries</code>), cung cấp công khai miễn phí cho nghiên cứu học thuật.</li>
  <li><strong>Quy mô:</strong> Gồm <strong>9.835</strong> hóa đơn giao dịch thu thập trong 30 ngày tại điểm bán hàng thực tế, bao phủ <strong>169</strong> danh mục sản phẩm khác nhau.</li>
</ul>
<div class="table-caption">Bảng 2.1: Từ điển dữ liệu bộ giao dịch bán lẻ Groceries</div>
<table class="data-table">
  <thead><tr><th class="num" style="width:8%;">STT</th><th style="width:24%;">Tên đặc trưng</th><th style="width:18%;">Kiểu dữ liệu</th><th style="width:50%;">Ý nghĩa mô tả</th></tr></thead>
  <tbody>
    <tr><td class="num">1</td><td><code>TransactionID</code></td><td>Số nguyên</td><td>Mã định danh duy nhất của mỗi hóa đơn thanh toán (1 – 9.835)</td></tr>
    <tr><td class="num">2</td><td><code>Item_1 ... Item_32</code></td><td>Chuỗi văn bản</td><td>Tên các mặt hàng xuất hiện trong từng hóa đơn (tối đa 32 món/hóa đơn)</td></tr>
    <tr><td class="num">3</td><td><code>Basket_Size</code></td><td>Số nguyên</td><td>Tổng số mặt hàng duy nhất trong giỏ (đặc trưng phái sinh phục vụ lọc nhiễu)</td></tr>
    <tr><td class="num">4</td><td><code>OneHot_Items</code></td><td>Nhị phân (0/1)</td><td>Ma trận sau mã hóa One-Hot: <code>1</code> nếu sản phẩm xuất hiện trong giỏ, <code>0</code> nếu không (169 cột gốc; 168 cột có mặt trong tập Train sau chia)</td></tr>
  </tbody>
</table>

<h2>2.2. Khảo sát thống kê và phân bố dữ liệu (EDA)</h2>
<p>Thống kê mô tả trên toàn bộ 9.835 hóa đơn gốc (169 mặt hàng) cho thấy độ dài trung bình mỗi giỏ hàng là <strong>4,41 sản phẩm/hóa đơn</strong> (độ lệch chuẩn <code>3,59</code>; trung vị <code>3</code>; tối đa <code>32</code> sản phẩm) và độ thưa ma trận đạt <strong>97,39%</strong> (chỉ 2,61% ô mang giá trị 1).</p>
<div class="figure-block">
  <img src="{img_uri('fig_3_1_eda.png')}" alt="EDA Top 15 sản phẩm và phân bố kích thước giỏ hàng" />
  <div class="figure-caption">Hình 2.1: Phân bố tần suất Top 15 sản phẩm phổ biến nhất và kích thước giỏ hàng (9.835 hóa đơn).</div>
</div>
<p><strong>Nhận xét Hình 2.1:</strong> Phân bố tần suất sản phẩm lệch phải mạnh theo quy luật Pareto 80/20: 5 mặt hàng thiết yếu dẫn đầu chiếm tỷ trọng áp đảo gồm <code>whole milk</code> (25,55%), <code>other vegetables</code> (19,35%), <code>rolls/buns</code> (18,39%), <code>soda</code> (17,44%) và <code>yogurt</code> (13,95%), trong khi hơn 70% mặt hàng còn lại có Support dưới 2%. Đồng thời, biểu đồ kích thước giỏ hàng cho thấy có tới <strong>2.159 hóa đơn chỉ mua đúng 1 món (21,95%)</strong> — đây là nhóm dữ liệu không tạo ra thông tin đồng xuất hiện.</p>

<h2>2.3. Phân tích quan hệ đồng xuất hiện giữa các đặc trưng</h2>
<div class="figure-block">
  <img src="{img_uri('fig_3_2_cooccurrence.png')}" alt="Ma trận đồng xuất hiện Top 8" />
  <div class="figure-caption">Hình 2.2: Ma trận tỷ lệ đồng xuất hiện giữa Top 8 nhóm sản phẩm chính (%).</div>
</div>
<p><strong>Ba nhận xét cốt lõi rút ra từ Hình 2.2 cho việc xây dựng mô hình:</strong></p>
<ol>
  <li><strong>Nhóm thực phẩm thiết yếu gắn kết mạnh nhất:</strong> Cặp <code>whole milk</code> và <code>other vegetables</code> có tỷ lệ mua kèm cao nhất toàn tập dữ liệu (<code>7,48%</code>), kế tiếp là <code>whole milk + rolls/buns</code> (<code>5,66%</code>) và <code>whole milk + yogurt</code> (<code>5,60%</code>).</li>
  <li><strong>Tần suất đơn lẻ cao không đồng nghĩa liên kết mạnh:</strong> <code>soda</code> xuất hiện tới <code>17,44%</code> nhưng tỷ lệ đi kèm <code>root vegetables</code> chỉ đạt <code>1,86%</code> (thấp hơn mức ngẫu nhiên kỳ vọng 17,44% × 10,90% = 1,90%), khẳng định bắt buộc phải lọc theo chỉ số <code>Lift ≥ 1,30</code> thay vì chỉ dùng Support/Confidence.</li>
  <li><strong>Định hướng khoảng tìm kiếm tham số:</strong> Tỷ lệ đồng xuất hiện phổ biến của các cặp chính nằm trong dải <code>1,5% – 7,5%</code>; do đó cần thiết lập <code>min_support</code> ở mức thấp (<code>0,005 – 0,015</code>) để bắt được các nhóm sản phẩm ngách mà vẫn đảm bảo tốc độ bằng thuật toán FP-Growth.</li>
</ol>

<h2>2.4. Phát hiện, xử lý chất lượng dữ liệu và so sánh trước – sau</h2>
<div class="table-caption">Bảng 2.2: Thống kê định lượng các vấn đề chất lượng dữ liệu và giải pháp xử lý</div>
<table class="data-table">
  <thead><tr><th style="width:20%;">Vấn đề</th><th style="width:26%;">Định lượng phát hiện</th><th style="width:54%;">Cách xử lý và lý do kỹ thuật</th></tr></thead>
  <tbody>
    <tr><td>Giá trị thiếu</td><td>Ô trống cuối dòng do độ dài hóa đơn khác nhau (1–32 món)</td><td>Bỏ qua ô trống khi phân tách từng dòng giao dịch thành danh sách sản phẩm hợp lệ.</td></tr>
    <tr><td>Bản ghi trùng</td><td>0 hóa đơn trùng hoàn toàn; kiểm tra trùng lặp nội bộ trong giỏ</td><td>Chuyển mỗi giỏ hàng thành tập hợp (<code>set</code>) để đảm bảo khai phá luật kết hợp nhị phân không bị sai lệch tần suất.</td></tr>
    <tr><td>Giá trị ngoại lai</td><td><strong>2.159</strong> hóa đơn chỉ có 1 món (<strong>21,95%</strong>)</td><td>Lọc bỏ các giỏ có <code>Basket_Size &lt; 2</code> vì giỏ 1 món không tạo ra quan hệ mua kèm và làm loãng giá trị Support.</td></tr>
    <tr><td>Mất cân bằng tần suất</td><td>&gt; 70% mặt hàng có <code>Support &lt; 2%</code></td><td>Không áp dụng tái lấy mẫu SMOTE (không phù hợp dữ liệu giỏ hàng nhị phân); hạ <code>min_support = 0,008</code> kết hợp lọc <code>Lift ≥ 1,30–1,50</code>.</td></tr>
    <tr><td>Nguy cơ rò rỉ dữ liệu</td><td>Toàn bộ 9.835 hóa đơn nếu mã hóa trước khi chia</td><td>Chia Hold-out 80/20 ngay từ đầu (<code>random_state=42</code>); <code>TransactionEncoder</code> chỉ <code>.fit()</code> trên tập Train.</td></tr>
  </tbody>
</table>

<div class="table-caption">Bảng 2.3: So sánh bộ dữ liệu trước và sau bước tiền xử lý làm sạch</div>
<table class="data-table">
  <thead><tr><th style="width:42%;">Chỉ số thống kê</th><th class="num" style="width:29%;">Trước xử lý (Dữ liệu gốc)</th><th class="num" style="width:29%;">Sau xử lý (Lọc giỏ ≥ 2 món)</th></tr></thead>
  <tbody>
    <tr><td>Tổng số hóa đơn (mẫu)</td><td class="num">9.835</td><td class="num"><strong>7.676</strong> (giảm 21,95% nhiễu)</td></tr>
    <tr><td>Độ dài giỏ hàng trung bình ± Std</td><td class="num">4,41 ± 3,59 món</td><td class="num"><strong>5,37 ± 3,52 món</strong></td></tr>
    <tr><td>Độ dày ma trận One-Hot (tỷ lệ giá trị 1)</td><td class="num">2,61% (độ thưa 97,39%)</td><td class="num"><strong>3,14%</strong> (trên Train) / <strong>3,11%</strong> (trên Test)</td></tr>
  </tbody>
</table>

<h2>2.5. Chuẩn bị dữ liệu chống rò rỉ và quy trình kiểm định chéo 5-Fold CV</h2>
<p>Tập dữ liệu sạch (7.676 giỏ ≥ 2 món) được chia theo chiến lược <strong>Hold-out 80/20</strong> với <code>random_state = 42</code> thành Tập huấn luyện phát triển (<strong>6.140 giỏ</strong>) và Tập kiểm tra giữ lại (<strong>1.536 giỏ</strong>). Tập kiểm tra được niêm phong hoàn toàn, tuyệt đối không dùng để chọn siêu tham số. Trên 6.140 giỏ Train, nhóm tổ chức thêm <strong>kiểm định chéo 5-Fold (5-Fold CV)</strong> để đánh giá độ ổn định (Mean ± Std) và tối ưu hóa siêu tham số ở Chương 3; trong mỗi fold, <code>TransactionEncoder</code> chỉ khớp (<code>fit</code>) trên 4 fold huấn luyện.</p>

<div class="figure-block">
  <img src="{img_uri('fig_2_1_cv_workflow.png')}" alt="Quy trình Hold-out 80/20 và 5-Fold CV" />
  <div class="figure-caption">Hình 2.3: Sơ đồ quy trình Hold-out 80/20 kết hợp kiểm định chéo 5-Fold CV chống rò rỉ dữ liệu.</div>
</div>

<div class="table-caption">Bảng 2.4: Phân bố kích thước các tập dữ liệu và 5 Fold kiểm định chéo trên tập Train</div>
<table class="data-table">
  <thead><tr><th class="num">Tập / Fold</th><th class="num">Số mẫu Train</th><th class="num">Số mẫu Val / Test</th><th class="num">Số đặc trưng</th><th class="num">Mục đích sử dụng</th></tr></thead>
  <tbody>
    <tr><td class="num">Fold 1 – Fold 5 (CV)</td><td class="num">4.912 giỏ / fold</td><td class="num">1.228 giỏ / fold</td><td class="num">168</td><td>Đánh giá ổn định (Mean ± Std) &amp; Grid Search</td></tr>
    <tr><td class="num">Toàn bộ Train (80%)</td><td class="num">6.140 giỏ</td><td class="num">—</td><td class="num">168</td><td>Huấn luyện mô hình cuối cùng sau khi chốt tham số</td></tr>
    <tr><td class="num">Hold-out Test (20%)</td><td class="num">—</td><td class="num">1.536 giỏ</td><td class="num">168</td><td>Kiểm chứng tổng quát hóa độc lập một lần duy nhất</td></tr>
  </tbody>
</table>

<!-- ==================== CHƯƠNG 3 ==================== -->
<div class="page-break"></div>
<h1 class="chapter-title">CHƯƠNG 3. THỰC NGHIỆM, TỐI ƯU HÓA VÀ ĐÁNH GIÁ MÔ HÌNH</h1>

<h2>3.1. Môi trường thực nghiệm và thiết lập tái lập</h2>
<p>Toàn bộ thực nghiệm được lập trình bằng <strong>Python 3.12</strong> trên Windows 64-bit với các thư viện chính: <code>pandas 3.1.1</code>, <code>numpy 2.5.5</code>, <code>scikit-learn 1.9.1</code>, <code>mlxtend 0.25.0</code>, <code>networkx 3.7</code>, <code>matplotlib 3.11.2</code>, <code>plotly 7.2.0</code> và <code>streamlit 1.67.0</code>. Mọi bước chia tách dữ liệu và kiểm định chéo đều cố định <code>random_state = 42</code> để bảo đảm kết quả tái lập chính xác.</p>

<h2>3.2. Kết quả thực nghiệm ban đầu và so sánh hiệu năng tính toán</h2>
<p>Ở giai đoạn đánh giá ban đầu trên tập Train (6.140 giỏ ≥ 2 món) với cấu hình khởi điểm (<code>min_support = 0,008</code>, <code>min_confidence = 0,25</code>, <code>min_lift = 1,30</code>, không giới hạn <code>max_len</code>), cả 3 thuật toán đều tìm ra chính xác cùng một tập luật (nhất quán 100% về mặt toán học), vượt xa mô hình cơ sở <em>Most Popular</em>.</p>

<div class="table-caption">Bảng 3.1: So sánh kết quả ban đầu giữa mô hình cơ sở và 3 thuật toán (min_support = 0,008; Lift ≥ 1,30)</div>
<table class="data-table">
  <thead><tr><th style="width:28%;">Mô hình / Thuật toán</th><th class="num">Số tập phổ biến</th><th class="num">Số luật tìm được</th><th class="num">Confidence TB (%)</th><th class="num">Lift TB</th><th class="num">Thời gian chạy (s)</th></tr></thead>
  <tbody>
    <tr><td>Cơ sở (<em>Most Popular: whole milk</em>)</td><td class="num">—</td><td class="num">1</td><td class="num">31,51%</td><td class="num">1,00</td><td class="num">0,001</td></tr>
    <tr><td>Apriori (Python tự cài đặt)</td><td class="num">715</td><td class="num"><strong>406</strong></td><td class="num">40,34%</td><td class="num">1,82</td><td class="num">3,083</td></tr>
    <tr><td>ECLAT (Python tự cài đặt)</td><td class="num">715</td><td class="num"><strong>406</strong></td><td class="num">40,34%</td><td class="num">1,82</td><td class="num">0,050</td></tr>
    <tr><td>FP-Growth (<code>mlxtend</code>)</td><td class="num">715</td><td class="num"><strong>406</strong></td><td class="num">40,34%</td><td class="num">1,82</td><td class="num"><strong>0,072</strong></td></tr>
  </tbody>
</table>

<p>Để đánh giá khả năng mở rộng khi hạ dần ngưỡng hỗ trợ từ <code>0,050</code> xuống <code>0,005</code>, nhóm tách riêng lượt đo thời gian thực thi (<code>perf_counter</code> không bị ảnh hưởng bởi hook cấp phát) và lượt đo bộ nhớ heap đỉnh (<code>tracemalloc</code>) trong Bảng 3.2 và Hình 3.1:</p>

<div class="table-caption">Bảng 3.2: Thời gian thực thi (s) và bộ nhớ đỉnh (MB) theo ngưỡng min_support</div>
<table class="data-table">
  <thead><tr><th class="num">min_support</th><th class="num">Số tập phổ biến</th><th class="num">Apriori (s / MB)</th><th class="num">ECLAT (s / MB)</th><th class="num">FP-Growth (s / MB)</th><th class="num">Tốc độ FP / Apriori</th></tr></thead>
  <tbody>
    <tr><td class="num">0,050</td><td class="num">41</td><td class="num">0,221 / 3,04</td><td class="num">0,016 / 2,18</td><td class="num">0,030 / 2,20</td><td class="num">7,5×</td></tr>
    <tr><td class="num">0,030</td><td class="num">98</td><td class="num">0,694 / 3,43</td><td class="num">0,022 / 2,58</td><td class="num">0,067 / 3,79</td><td class="num">10,4×</td></tr>
    <tr><td class="num">0,020</td><td class="num">178</td><td class="num">1,185 / 3,62</td><td class="num">0,032 / 2,81</td><td class="num">0,076 / 4,56</td><td class="num">15,6×</td></tr>
    <tr><td class="num">0,010</td><td class="num">514</td><td class="num">2,351 / 4,40</td><td class="num">0,034 / 3,16</td><td class="num">0,100 / 5,97</td><td class="num">23,5×</td></tr>
    <tr><td class="num">0,008</td><td class="num">715</td><td class="num">3,379 / 5,09</td><td class="num">0,051 / 3,27</td><td class="num">0,116 / 6,50</td><td class="num"><strong>29,1×</strong></td></tr>
    <tr><td class="num">0,005</td><td class="num">1.520</td><td class="num">5,668 / 7,20</td><td class="num">0,051 / 3,64</td><td class="num">0,125 / 7,95</td><td class="num"><strong>45,2×</strong></td></tr>
  </tbody>
</table>

<div class="figure-block">
  <img src="{img_uri('fig_benchmark_runtime_memory.png')}" alt="So sánh thời gian chạy và bộ nhớ" />
  <div class="figure-caption">Hình 3.1: Đường cong thời gian thực thi (a) và bộ nhớ đỉnh tracemalloc (b) khi giảm dần min_support.</div>
</div>
<p><strong>Nhận xét Hình 3.1:</strong> Khi giảm <code>min_support</code> xuống <code>0,005</code>, số ứng viên cần duyệt của Apriori tăng mạnh khiến thời gian chạy vọt lên <code>5,668 giây</code> theo xu hướng hàm mũ, trong khi FP-Growth chỉ mất <code>0,125 giây</code> (<strong>nhanh gấp 45,2 lần Apriori</strong>, vượt xa tiêu chí ≥ 3 lần ở Bảng 1.1). Về bộ nhớ Python heap (<code>tracemalloc</code>), cả ba đều giữ ở mức rất nhẹ (&lt; 8 MB); ECLAT tốn ít bộ nhớ Python nhất (<code>3,64 MB</code>) do chỉ lưu danh sách chỉ số hóa đơn dạng tập hợp dọc, còn FP-Growth lưu cây FP-Tree khoảng <code>7,95 MB</code> để đổi lấy tốc độ khai phá gần như hằng số.</p>

<h2>3.3. Phân tích hạn chế của mô hình ban đầu và đề xuất giải pháp cải tiến</h2>
<p>Quan sát kết quả thực nghiệm ban đầu cho thấy 3 hạn chế cụ thể cần khắc phục ở giai đoạn tối ưu hóa (Bài 3):</p>
<ol>
  <li><strong>Hạn chế về hiệu năng Apriori:</strong> Apriori quét danh sách giao dịch theo từng mức ứng viên (ví dụ tại <code>min_support = 0,008</code> phải sinh và kiểm tra <code>5.565</code> cặp <i>C<sub>2</sub></i> và <code>2.119</code> bộ ba <i>C<sub>3</sub></i>), dẫn tới thời gian chạy chậm gấp 29–45 lần so với FP-Growth.</li>
  <li><strong>Nhiễu từ hóa đơn 1 sản phẩm và dao động cao giữa các fold:</strong> Khi chạy trực tiếp trên dữ liệu thô chưa lọc 2.159 giỏ 1 món (21,95%), độ tin cậy trên kiểm định chéo 5-Fold chỉ đạt <code>36,28% ± 1,75%</code>, độ lệch chuẩn lớn và các cặp sản phẩm ngách bị loãng Support.</li>
  <li><strong>Tập luật quá lớn và còn luật yếu/dư thừa:</strong> Ở ngưỡng <code>Lift ≥ 1,30</code> và không giới hạn độ dài, mô hình sinh ra tới <strong>406 luật</strong>, bao gồm các luật dài 4 món khó áp dụng trưng bày và những luật có tập con đã đạt Confidence cao hơn (dư thừa).</li>
</ol>

<div class="table-caption">Bảng 3.3: Bảng phân tích hạn chế mô hình ban đầu và đề xuất giải pháp cải tiến</div>
<table class="data-table">
  <thead><tr><th class="num" style="width:7%;">STT</th><th style="width:28%;">Hạn chế dựa trên bằng chứng</th><th style="width:30%;">Giải pháp cải tiến đề xuất</th><th style="width:35%;">Cơ sở lý thuyết &amp; Kỳ vọng tác động</th></tr></thead>
  <tbody>
    <tr><td class="num">1</td><td>Apriori mất <code>3,38 – 5,67s</code> khi giảm ngưỡng hỗ trợ</td><td>Chuẩn hóa <strong>FP-Growth</strong> làm lõi khai phá chính (đối chiếu cùng ECLAT)</td><td>Cấu trúc cây tiền tố nén FP-Tree giảm số lần quét CSDL xuống 2 lần, loại bỏ bước sinh <i>C<sub>k</sub></i>.</td></tr>
    <tr><td class="num">2</td><td>2.159 giỏ 1 món gây loãng Support &amp; tăng Std CV (<code>±1,75%</code>)</td><td><strong>Cải tiến dữ liệu:</strong> Lọc bỏ giỏ <code>&lt; 2</code> món (<code>Basket_Size ≥ 2</code>)</td><td>Loại bỏ giao dịch không có thông tin đồng xuất hiện, ổn định phân phối và giảm phương sai giữa các fold.</td></tr>
    <tr><td class="num">3</td><td>406 luật ở <code>Lift ≥ 1,30</code> còn dài và chứa luật dư thừa</td><td><strong>Grid Search 5-Fold CV</strong> + <strong>Hậu xử lý cắt tỉa luật dư thừa (Pruning)</strong></td><td>Loại luật dài &gt; 3 món và loại luật <i>X ⇒ Y</i> nếu đã có <i>X' ⊂ X</i> đạt <code>Conf(X'⇒Y) ≥ Conf(X⇒Y)</code>.</td></tr>
  </tbody>
</table>

<h2>3.4. Cải tiến dữ liệu, thử nghiệm hậu xử lý và tối ưu siêu tham số (Grid Search 5-Fold)</h2>
<p>Nhóm thực hiện Grid Search trên <strong>kiểm định chéo 5-Fold chỉ trên 6.140 giỏ Train</strong> (tuyệt đối không chạm vào 1.536 giỏ Test) với lưới tham số: <code>min_support ∈ {0,005; 0,008; 0,010; 0,015}</code>, <code>min_confidence ∈ {0,20; 0,25; 0,30}</code>, <code>min_lift ∈ {1,30; 1,50; 1,80}</code> và <code>max_len ∈ {2; 3; None}</code> (tổng cộng 108 cấu hình).</p>

<div class="table-caption">Bảng 3.4: Kết quả tiêu biểu từ Grid Search trên kiểm định chéo 5-Fold CV (chỉ trên tập Train)</div>
<table class="data-table">
  <thead><tr><th class="num">min_support</th><th class="num">min_conf</th><th class="num">min_lift</th><th class="num">max_len</th><th class="num">Số luật TB ± Std</th><th class="num">CV Lift TB ± Std</th><th class="num">CV Conf TB ± Std (%)</th><th class="num">Ghi chú chọn</th></tr></thead>
  <tbody>
    <tr><td class="num">0,005</td><td class="num">0,20</td><td class="num">1,80</td><td class="num">None</td><td class="num">806,6 ± 58,2</td><td class="num">2,208 ± 0,125</td><td class="num">35,22 ± 1,50</td><td>Quá nhiều luật, Std cao</td></tr>
    <tr><td class="num">0,005</td><td class="num">0,25</td><td class="num">1,80</td><td class="num">2</td><td class="num">37,6 ± 3,4</td><td class="num">2,114 ± 0,092</td><td class="num">32,10 ± 1,18</td><td>Ít luật, bỏ sót tổ hợp 3 món</td></tr>
    <tr><td class="num">0,008</td><td class="num">0,25</td><td class="num">1,30</td><td class="num">3</td><td class="num">330,4 ± 17,2</td><td class="num">1,697 ± 0,061</td><td class="num">38,40 ± 1,07</td><td>Ngưỡng Lift còn rộng</td></tr>
    <tr style="background:#EFF6FF;"><td class="num"><strong>0,008</strong></td><td class="num"><strong>0,25</strong></td><td class="num"><strong>1,50</strong></td><td class="num"><strong>3</strong></td><td class="num"><strong>223,2 ± 13,5</strong></td><td class="num"><strong>1,817 ± 0,069</strong></td><td class="num"><strong>38,94 ± 1,05</strong></td><td><strong>Tối ưu cân bằng &amp; ổn định</strong></td></tr>
    <tr><td class="num">0,010</td><td class="num">0,25</td><td class="num">1,50</td><td class="num">3</td><td class="num">131,8 ± 7,1</td><td class="num">1,831 ± 0,066</td><td class="num">38,24 ± 0,95</td><td>Ít luật gợi ý hơn ~41%</td></tr>
  </tbody>
</table>

<div class="figure-block">
  <img src="{img_uri('fig_cv_validation_curve.png')}" alt="Đường cong kiểm định chéo 5-Fold" />
  <div class="figure-caption">Hình 3.2: Đường cong kiểm định chéo 5-Fold (Lift TB ± Std) theo min_support và min_lift tại min_conf = 0,25, max_len = 3.</div>
</div>
<p><strong>Nhận xét Hình 3.2:</strong> Khi nâng ngưỡng <code>min_lift</code> lên <code>1,80</code>, Lift TB tăng lên ~<code>2,0</code> nhưng độ lệch chuẩn giữa các fold (thanh sai số Std) mở rộng đáng kể (<code>±0,11</code>) và làm rơi mất nhiều luật hữu ích. Cấu hình <code>min_support = 0,008</code>, <code>min_confidence = 0,25</code>, <code>min_lift = 1,50</code>, <code>max_len = 3</code> nằm ở vùng cân bằng tối ưu: sai số giữa các fold nhỏ (<code>Std = 0,069</code>), tỷ lệ giữ luật trên tập kiểm định đạt cao ổn định và số lượng luật vừa đủ để triển khai gợi ý.</p>

<h2>3.5. So sánh trước – sau cải tiến (Ablation Study) và khả năng tổng quát hóa</h2>
<div class="table-caption">Bảng 3.5: Nghiên cứu đóng góp từng cải tiến (Ablation Study) trên 5-Fold CV và Hold-out Test 20%</div>
<table class="data-table">
  <thead><tr><th style="width:34%;">Cấu hình mô hình</th><th class="num">Số luật (Train)</th><th class="num">CV Lift TB ± Std</th><th class="num">CV Conf TB ± Std (%)</th><th class="num">Test Lift TB</th><th class="num">Test Conf TB (%)</th></tr></thead>
  <tbody>
    <tr><td>0. Mô hình cơ sở (<em>Most Popular: whole milk</em>)</td><td class="num">1</td><td class="num">1,000 ± 0,000</td><td class="num">31,51 ± 0,00</td><td class="num">1,000</td><td class="num">29,75</td></tr>
    <tr><td>1. FP-Growth ban đầu (dữ liệu thô, Lift ≥ 1,30)</td><td class="num">286</td><td class="num">1,897 ± 0,106</td><td class="num">36,28 ± 1,75</td><td class="num">2,033</td><td class="num">36,79</td></tr>
    <tr><td>2. + Cải tiến dữ liệu: Lọc bỏ giỏ &lt; 2 món</td><td class="num">406</td><td class="num">1,751 ± 0,058</td><td class="num">38,46 ± 1,09</td><td class="num">1,697</td><td class="num">34,71</td></tr>
    <tr><td>3. + Tối ưu siêu tham số (Lift ≥ 1,50, max_len=3)</td><td class="num">270</td><td class="num">1,817 ± 0,069</td><td class="num">38,94 ± 1,05</td><td class="num">1,788</td><td class="num">34,98</td></tr>
    <tr style="background:#F0FDF4;"><td><strong>4. + Hậu xử lý cắt tỉa luật dư thừa (Cuối cùng)</strong></td><td class="num"><strong>266</strong></td><td class="num"><strong>1,816 ± 0,067</strong></td><td class="num"><strong>38,91 ± 0,96</strong></td><td class="num"><strong>1,784</strong></td><td class="num"><strong>35,07</strong></td></tr>
  </tbody>
</table>

<div class="figure-block">
  <img src="{img_uri('fig_ablation_cv_vs_test.png')}" alt="Ablation Study CV vs Test" />
  <div class="figure-caption">Hình 3.3: So sánh chỉ số Lift (a) và Confidence (b) giữa 5-Fold CV và tập Kiểm tra 20% qua từng bước cải tiến.</div>
</div>

<p><strong>Phân tích đóng góp &amp; giải thích kết quả:</strong></p>
<ul>
  <li><strong>Tác động của cải tiến dữ liệu (Bước 1 → Bước 2):</strong> Việc loại bỏ 2.159 giỏ hàng 1 món làm mẫu số giảm từ <code>9.835</code> xuống <code>7.676</code> giỏ, giúp 120 cặp hàng ngách vượt ngưỡng <code>min_support = 0,008</code> (số luật tăng từ <code>286 → 406</code>). Kết quả này giúp <strong>CV Confidence tăng mạnh từ 36,28% lên 38,46% (+2,18%)</strong> và <strong>giảm gần một nửa độ lệch chuẩn giữa các fold</strong> (<code>CV Lift Std: 0,106 → 0,058</code>; <code>CV Conf Std: 1,75% → 1,09%</code>). Giá trị Lift TB giảm nhẹ (<code>1,897 → 1,751</code>) do 120 luật mới được mở khóa có Lift nằm trong vùng <code>1,30 – 1,50</code>.</li>
  <li><strong>Tác động của tối ưu tham số &amp; Pruning (Bước 2 → Bước 4):</strong> Khi siết ngưỡng <code>min_lift = 1,50, max_len = 3</code> và cắt tỉa 4 luật dư thừa (<code>270 → 266</code> luật), chỉ số <code>CV Lift</code> tăng trở lại <strong><code>1,816 ± 0,067</code></strong>, đồng thời <code>CV Conf Std</code> giảm xuống mức thấp nhất (<code>0,96%</code>) và <code>Test Confidence TB</code> đạt mức cao nhất sau lọc (<strong><code>35,07%</code></strong>).</li>
  <li><strong>Đánh giá khả năng tổng quát hóa:</strong> Trên <strong>266 luật cuối cùng</strong> (huấn luyện trên 100% tập Train cho <code>Train Lift TB = 1,920</code>, <code>Train Conf TB = 41,37%</code>), khi kiểm chứng độc lập một lần duy nhất trên <strong>1.536 giỏ Test</strong>, mô hình đạt <strong><code>Test Lift TB = 1,784</code></strong> và <strong><code>Test Conf TB = 35,07%</code></strong>. Chênh lệch giữa <code>CV Lift (1,816)</code> và <code>Test Lift (1,784)</code> chỉ là <strong><code>-1,76%</code></strong> (nằm hoàn toàn trong 1 độ lệch chuẩn <code>±0,067</code>), chứng tỏ mô hình tổng quát hóa tốt và không bị quá khớp.</li>
</ul>

<div class="figure-block">
  <img src="{img_uri('fig_3_3_rules_scatter.png')}" alt="Scatter 266 luật cuối cùng" />
  <div class="figure-caption">Hình 3.4: Phân bố Support, Confidence và Lift của 266 luật kết hợp cuối cùng (toàn bộ nằm trên ngưỡng Confidence = 25%).</div>
</div>

<div class="table-caption">Bảng 3.6: Top 8 luật kết hợp tiêu biểu của mô hình cuối cùng (sau tối ưu và Pruning)</div>
<table class="data-table">
  <thead><tr><th class="num">Hạng</th><th>Sản phẩm đã mua (Vế trái X)</th><th>Gợi ý mua kèm (Vế phải Y)</th><th class="num">Support (%)</th><th class="num">Confidence (%)</th><th class="num">Lift</th><th class="num">Conviction</th></tr></thead>
  <tbody>
    <tr><td class="num">1</td><td><code>butter, other vegetables</code></td><td><code>whipped/sour cream</code></td><td class="num">0,81%</td><td class="num">30,7%</td><td class="num"><strong>3,41</strong></td><td class="num">1,31</td></tr>
    <tr><td class="num">2</td><td><code>herbs</code></td><td><code>root vegetables</code></td><td class="num">0,91%</td><td class="num">46,7%</td><td class="num"><strong>3,33</strong></td><td class="num">1,61</td></tr>
    <tr><td class="num">3</td><td><code>berries</code></td><td><code>whipped/sour cream</code></td><td class="num">1,19%</td><td class="num">27,4%</td><td class="num"><strong>3,05</strong></td><td class="num">1,25</td></tr>
    <tr><td class="num">4</td><td><code>other vegetables, tropical fruit</code></td><td><code>pip fruit</code></td><td class="num">1,30%</td><td class="num">28,2%</td><td class="num"><strong>2,94</strong></td><td class="num">1,26</td></tr>
    <tr><td class="num">5</td><td><code>other vegetables, pip fruit</code></td><td><code>tropical fruit</code></td><td class="num">1,30%</td><td class="num">38,3%</td><td class="num"><strong>2,88</strong></td><td class="num">1,41</td></tr>
    <tr><td class="num">6</td><td><code>beef, other vegetables</code></td><td><code>root vegetables</code></td><td class="num">1,07%</td><td class="num">39,5%</td><td class="num"><strong>2,82</strong></td><td class="num">1,42</td></tr>
    <tr><td class="num">7</td><td><code>root vegetables, yogurt</code></td><td><code>whipped/sour cream</code></td><td class="num">0,88%</td><td class="num">25,2%</td><td class="num"><strong>2,81</strong></td><td class="num">1,22</td></tr>
    <tr><td class="num">8</td><td><code>pip fruit, yogurt</code></td><td><code>tropical fruit</code></td><td class="num">0,90%</td><td class="num">36,9%</td><td class="num"><strong>2,78</strong></td><td class="num">1,37</td></tr>
  </tbody>
</table>

<div class="table-caption">Bảng 3.7: Đối chiếu chỉ tiêu kỹ thuật cam kết ban đầu (Bảng 1.1) với kết quả mô hình cuối cùng</div>
<table class="data-table">
  <thead><tr><th>Chỉ tiêu đánh giá</th><th class="num">Mục tiêu cam kết</th><th class="num">Kết quả 5-Fold CV</th><th class="num">Kết quả Test (20%)</th><th class="num">Đánh giá</th></tr></thead>
  <tbody>
    <tr><td>Lift trung bình</td><td class="num">≥ 1,30</td><td class="num"><strong>1,816 ± 0,067</strong></td><td class="num"><strong>1,784</strong></td><td class="num">Đạt vượt mức</td></tr>
    <tr><td>Confidence trung bình</td><td class="num">≥ 25,0%</td><td class="num"><strong>38,91% ± 0,96%</strong></td><td class="num"><strong>35,07%</strong></td><td class="num">Đạt vượt mức</td></tr>
    <tr><td>Tốc độ FP-Growth vs Apriori</td><td class="num">Nhanh hơn ≥ 3 lần</td><td class="num" colspan="2">Nhanh hơn <strong>29,1×</strong> (tại 0,008) &amp; <strong>45,2×</strong> (tại 0,005)</td><td class="num">Đạt vượt mức</td></tr>
  </tbody>
</table>

<h2>3.6. Trực quan hóa mạng luật kết hợp và đề xuất ứng dụng thực tiễn</h2>
<div class="figure-block">
  <img src="{img_uri('fig_3_7_network.png')}" alt="Mạng lưới 15 luật mạnh nhất" />
  <div class="figure-caption">Hình 3.5: Mạng lưới 15 luật kết hợp mạnh nhất theo Lift từ mô hình FP-Growth cuối cùng.</div>
</div>
<p><strong>Nhận xét Hình 3.5 &amp; Đề xuất ứng dụng:</strong> Đồ thị mạng cho thấy các nút trung tâm (hub) có nhiều mũi tên hội tụ và phân nhánh là <code>other vegetables</code>, <code>tropical fruit</code>, <code>whipped/sour cream</code> và <code>root vegetables</code>. Từ phân cụm tính mô-đun (Modularity Clustering) trên đồ thị 266 luật trong ứng dụng demo (Tab 4), nhóm đề xuất 4 phân khu sắp xếp quầy kệ và gợi ý mua kèm trong Bảng 3.8:</p>

<div class="table-caption">Bảng 3.8: Đề xuất phân khu sắp xếp quầy kệ siêu thị và gợi ý bán chéo</div>
<table class="data-table">
  <thead><tr><th class="num" style="width:12%;">Khu vực</th><th style="width:22%;">Sản phẩm tâm điểm</th><th style="width:36%;">Nhóm hàng hóa nên bố trí liền kề</th><th style="width:30%;">Ứng dụng gợi ý mua kèm / Combo</th></tr></thead>
  <tbody>
    <tr><td class="num">Khu 1</td><td><code>other vegetables</code></td><td>Rau củ (<code>root vegetables</code>), thảo mộc (<code>herbs</code>), thịt bò (<code>beef</code>)</td><td>Combo nấu ăn gia đình; gợi ý thêm rau/củ khi khách chọn thịt bò hoặc gia vị.</td></tr>
    <tr><td class="num">Khu 2</td><td><code>whole milk</code></td><td>Bơ (<code>butter</code>), kem tươi (<code>whipped/sour cream</code>), bánh ngọt</td><td>Đặt tủ kem tươi/bơ cạnh quầy sữa; gợi ý kem/sữa chua khi mua quả mọng (<code>berries</code>).</td></tr>
    <tr><td class="num">Khu 3</td><td><code>tropical fruit</code></td><td>Trái cây (<code>pip fruit</code>, <code>citrus fruit</code>), sữa chua (<code>yogurt</code>)</td><td>Tạo đảo trưng bày “Trái cây &amp; Sữa chua”; giảm giá 10% khi mua kèm <code>pip fruit</code>.</td></tr>
    <tr><td class="num">Khu 4</td><td><code>rolls/buns</code></td><td>Xúc xích (<code>sausage</code>), nước đóng chai, đồ ăn sáng</td><td>Đặt quầy bánh mì gần quầy thịt nguội/đồ nguội phục vụ giỏ hàng bữa sáng nhanh.</td></tr>
  </tbody>
</table>

<!-- ==================== KẾT LUẬN ==================== -->
<div class="page-break"></div>
<h1 class="chapter-title">KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN</h1>
<h2>1. Kết quả đạt được</h2>
<ul>
  <li>Hoàn thiện đầy đủ quy trình 3 giai đoạn của dự án Học máy trên bộ dữ liệu bán lẻ thực tế Groceries (9.835 hóa đơn, 169 mặt hàng).</li>
  <li>Cài đặt và kiểm chứng tính nhất quán tuyệt đối (100% tập phổ biến và tập luật trùng khớp) giữa <strong>Apriori</strong> (Python tự cài đặt), <strong>ECLAT</strong> (TID-set dọc) và <strong>FP-Growth</strong> (<code>mlxtend</code>); chứng minh FP-Growth nhanh hơn Apriori từ <strong>29,1 lần</strong> (tại <code>0,008</code>) đến <strong>45,2 lần</strong> (tại <code>0,005</code>).</li>
  <li>Thực hiện kiểm định chéo 5-Fold CV, Grid Search không rò rỉ dữ liệu, Ablation Study và hậu xử lý cắt tỉa luật dư thừa, thu được <strong>266 luật kết hợp chất lượng cao</strong> đạt <code>CV Lift TB = 1,816 ± 0,067</code>, <code>Test Lift TB = 1,784</code> và <code>Test Confidence TB = 35,07%</code> (vượt xa Baseline <code>Lift = 1,00</code> và các chỉ tiêu đã cam kết).</li>
  <li>Đóng gói hoàn chỉnh thành ứng dụng demo web 7 phân hệ bằng Streamlit (<code>app.py</code>) hỗ trợ gợi ý mua kèm theo thời gian thực, lọc dữ liệu Groceries/Online Retail và chạy trực tiếp các thử nghiệm kiểm định chéo.</li>
</ul>

<h2>2. Những hạn chế còn tồn tại</h2>
<ul>
  <li>Bộ dữ liệu Groceries chỉ ghi nhận danh mục sản phẩm có mặt trong hóa đơn, chưa có số lượng mua từng món, đơn giá, biên lợi nhuận hay khung giờ giao dịch.</li>
  <li>Các độ đo truyền thống đánh đồng trọng số mọi mặt hàng như nhau, chưa ưu tiên gợi ý những sản phẩm mang lại lợi nhuận cao cho cửa hàng và chưa cá nhân hóa theo từng phân khúc khách hàng.</li>
</ul>

<h2>3. Hướng nghiên cứu và phát triển tiếp theo</h2>
<ul>
  <li>Mở rộng sang <strong>Khai phá tập phổ biến có trọng số lợi nhuận</strong> (Weighted Frequent Itemset Mining / High-Utility Itemset Mining) để tối đa hóa doanh thu thực tế thay vì chỉ tối ưu tần suất.</li>
  <li>Kết hợp phân cụm khách hàng (RFM / K-Means) trước khi khai phá luật kết hợp cho từng nhóm khách hàng mục tiêu, và đóng gói thành REST API tích hợp vào hệ thống thương mại điện tử.</li>
</ul>

<!-- ==================== TÀI LIỆU THAM KHẢO ==================== -->
<h1 class="chapter-title" style="margin-top:20pt;">TÀI LIỆU THAM KHẢO</h1>
<ol style="font-size:11.5pt; line-height:1.45;">
  <li>R. Agrawal, R. Srikant (1994), “Fast algorithms for mining association rules in large databases”, in <em>Proceedings of the 20th International Conference on Very Large Data Bases (VLDB)</em>, pp. 487–499.</li>
  <li>J. Han, J. Pei, Y. Yin (2000), “Mining frequent patterns without candidate generation”, in <em>Proceedings of the 2000 ACM SIGMOD International Conference on Management of Data</em>, pp. 1–12.</li>
  <li>M. J. Zaki (2000), “Scalable algorithms for association mining”, <em>IEEE Transactions on Knowledge and Data Engineering</em>, vol. 12, no. 3, pp. 372–390.</li>
  <li>M. Hahsler, B. Grün, K. Hornik (2005), “arules – A computational environment for mining association rules and frequent item sets”, <em>Journal of Statistical Software</em>, vol. 14, no. 15, pp. 1–25.</li>
  <li>S. Raschka (2018), “MLxtend: Providing machine learning and data science utilities and extensions to Python’s scientific computing stack”, <em>Journal of Open Source Software</em>, vol. 3, no. 24, p. 638.</li>
  <li>P.-N. Tan, M. Steinbach, A. Karpatne, V. Kumar (2019), <em>Introduction to Data Mining</em> (2nd Edition), Chapter 5: Association Analysis, Pearson.</li>
  <li>F. Pedregosa et al. (2011), “Scikit-learn: Machine learning in Python”, <em>Journal of Machine Learning Research</em>, vol. 12, pp. 2825–2830.</li>
</ol>

<!-- ==================== PHỤ LỤC A ==================== -->
<div class="page-break"></div>
<h1 class="chapter-title">PHỤ LỤC A. HƯỚNG DẪN CÀI ĐẶT, TÁI LẬP VÀ CHẠY DEMO</h1>

<h2>A.1. Cấu trúc mã nguồn dự án</h2>
<ul>
  <li><code>data/groceries.csv</code>: Bộ dữ liệu giao dịch chuẩn Groceries (9.835 hóa đơn, 169 mặt hàng).</li>
  <li><code>src/data_pipeline.py</code>: Nạp dữ liệu (hỗ trợ cả Groceries và Online Retail CSV), làm sạch, lọc giỏ &lt; 2 món, chia Hold-out 80/20 (<code>random_state=42</code>) và mã hóa One-Hot.</li>
  <li><code>src/algorithms.py</code>: Cài đặt Apriori (kèm trace <i>C<sub>k</sub> → L<sub>k</sub></i>), ECLAT, FP-Growth (<code>mlxtend</code>), đánh giá trên Test, phân cụm quầy kệ và gợi ý mua kèm.</li>
  <li><code>src/part3_experiments.py</code> &amp; <code>run_part3_experiments.py</code>: Chạy kiểm định chéo 5-Fold CV, Grid Search, Ablation Study, cắt tỉa luật dư thừa và xuất bảng/biểu đồ.</li>
  <li><code>app.py</code> &amp; <code>src/visualizations.py</code>: Ứng dụng web demo tương tác 7 phân hệ trên Streamlit.</li>
  <li><code>tests/verify_pipeline.py</code>: Kiểm thử đối chiếu tính nhất quán giữa 3 thuật toán và pipeline dữ liệu.</li>
</ul>

<h2>A.2. Yêu cầu môi trường và các bước thực hiện</h2>
<p class="no-indent">Yêu cầu <strong>Python ≥ 3.10</strong>. Mở cửa sổ dòng lệnh tại thư mục dự án và chạy lần lượt các lệnh sau:</p>
<pre class="code-block"># Bước 1: Cài đặt toàn bộ thư viện phụ thuộc
pip install -r requirements.txt

# Bước 2: Chạy kiểm thử và tái lập toàn bộ bảng biểu / hình vẽ thực nghiệm
python tests/verify_pipeline.py
python run_part3_experiments.py

# Bước 3: Khởi chạy ứng dụng demo sản phẩm trên trình duyệt (http://localhost:8501)
streamlit run app.py</pre>

<div class="figure-block">
  <img src="{img_uri('fig_appendix_demo.png')}" alt="Giao diện demo Streamlit" />
  <div class="figure-caption">Hình A.1: Giao diện ứng dụng web demo sản phẩm chạy trên trình duyệt (Streamlit).</div>
</div>

</body>
</html>
"""
    replacements = {
        "{img_uri('ictu_logo.png')}": img_uri("ictu_logo.png"),
        "{img_uri('fig_1_1_pipeline.png')}": img_uri("fig_1_1_pipeline.png"),
        "{img_uri('fig_3_1_eda.png')}": img_uri("fig_3_1_eda.png"),
        "{img_uri('fig_3_2_cooccurrence.png')}": img_uri("fig_3_2_cooccurrence.png"),
        "{img_uri('fig_2_1_cv_workflow.png')}": img_uri("fig_2_1_cv_workflow.png"),
        "{img_uri('fig_benchmark_runtime_memory.png')}": img_uri("fig_benchmark_runtime_memory.png"),
        "{img_uri('fig_cv_validation_curve.png')}": img_uri("fig_cv_validation_curve.png"),
        "{img_uri('fig_ablation_cv_vs_test.png')}": img_uri("fig_ablation_cv_vs_test.png"),
        "{img_uri('fig_3_3_rules_scatter.png')}": img_uri("fig_3_3_rules_scatter.png"),
        "{img_uri('fig_3_7_network.png')}": img_uri("fig_3_7_network.png"),
        "{img_uri('fig_appendix_demo.png')}": img_uri("fig_appendix_demo.png"),
    }
    for k, v in replacements.items():
        html = html.replace(k, v)
    return html


def _render_pdf(html_text: str, browser_exe: Path) -> None:
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(html_text, encoding="utf-8")
    cmd = [
        str(browser_exe),
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={PDF_PATH}",
        HTML_PATH.resolve().as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if res.returncode != 0 or not PDF_PATH.exists():
        raise RuntimeError(f"PDF generation failed (exit={res.returncode}): {res.stderr}")


def _resolve_page_numbers(pdf_path: Path) -> dict[str, str]:
    import pymupdf

    markers = {
        "__P_NHAN_XET__": "NHẬN XÉT CỦA GIẢNG VIÊN",
        "__P_PHAN_CONG__": "BẢNG PHÂN CÔNG NHIỆM VỤ",
        "__P_CAM_DOAN__": "LỜI CAM ĐOAN",
        "__P_CAM_ON__": "LỜI CẢM ƠN",
        "__P_VIET_TAT__": "DANH MỤC KÝ HIỆU VÀ TỪ VIẾT TẮT",
        "__P_HINH_BANG__": "DANH MỤC HÌNH VẼ VÀ ĐỒ THỊ",
        "__P_MO_DAU__": "1. Lý do chọn đề tài",
        "__P_CH1__": "CHƯƠNG 1. CƠ SỞ LÝ THUYẾT",
        "__P_1_1__": "1.1. Phát biểu bài toán",
        "__P_1_2__": "1.2. Mục tiêu thực tế",
        "__P_1_3__": "1.3. Cơ sở lý thuyết",
        "__P_1_4__": "1.4. Hệ thống các chỉ số",
        "__P_CH2__": "CHƯƠNG 2. DỮ LIỆU THỰC NGHIỆM",
        "__P_2_1__": "2.1. Nguồn dữ liệu",
        "__P_2_2__": "2.2. Khảo sát thống kê",
        "__P_2_3__": "2.3. Phân tích quan hệ",
        "__P_2_4__": "2.4. Phát hiện, xử lý",
        "__P_2_5__": "2.5. Chuẩn bị dữ liệu",
        "__P_CH3__": "CHƯƠNG 3. THỰC NGHIỆM",
        "__P_3_1__": "3.1. Môi trường thực nghiệm",
        "__P_3_2__": "3.2. Kết quả thực nghiệm ban đầu",
        "__P_3_3__": "3.3. Phân tích hạn chế",
        "__P_3_4__": "3.4. Cải tiến dữ liệu",
        "__P_3_5__": "3.5. So sánh trước",
        "__P_3_6__": "3.6. Trực quan hóa mạng",
        "__P_KET_LUAN__": "KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN",
        "__P_TLTK__": "TÀI LIỆU THAM KHẢO",
        "__P_PHU_LUC__": "PHỤ LỤC A.",
        "__F_1_1__": "Hình 1.1:",
        "__F_2_1__": "Hình 2.1:",
        "__F_2_2__": "Hình 2.2:",
        "__F_2_3__": "Hình 2.3:",
        "__F_3_1__": "Hình 3.1:",
        "__F_3_2__": "Hình 3.2:",
        "__F_3_3__": "Hình 3.3:",
        "__F_3_4__": "Hình 3.4:",
        "__F_3_5__": "Hình 3.5:",
        "__F_A_1__": "Hình A.1:",
        "__T_1_1__": "Bảng 1.1:",
        "__T_1_2__": "Bảng 1.2:",
        "__T_2_1__": "Bảng 2.1:",
        "__T_2_2__": "Bảng 2.2:",
        "__T_2_3__": "Bảng 2.3:",
        "__T_2_4__": "Bảng 2.4:",
        "__T_3_1__": "Bảng 3.1:",
        "__T_3_2__": "Bảng 3.2:",
        "__T_3_3__": "Bảng 3.3:",
        "__T_3_4__": "Bảng 3.4:",
        "__T_3_5__": "Bảng 3.5:",
        "__T_3_6__": "Bảng 3.6:",
        "__T_3_7__": "Bảng 3.7:",
        "__T_3_8__": "Bảng 3.8:",
    }

    doc = pymupdf.open(pdf_path)
    # Search after front-matter TOC/lists pages for body & captions
    page_texts = [p.get_text("text") for p in doc]
    doc.close()

    resolved: dict[str, str] = {}
    for key, needle in markers.items():
        # Front-matter sections appear before page 10; body/captions appear from page 9 onward (or exact section)
        start_p = 1 if key.startswith("__P_") and key not in {"__P_NHAN_XET__", "__P_PHAN_CONG__", "__P_CAM_DOAN__", "__P_CAM_ON__", "__P_VIET_TAT__", "__P_HINH_BANG__"} else 0
        # For TOC lines themselves (around page 6-8), skip page 6..9 when resolving body headings & captions
        for idx, txt in enumerate(page_texts):
            pno = idx + 1
            if key in {"__P_NHAN_XET__", "__P_PHAN_CONG__", "__P_CAM_DOAN__", "__P_CAM_ON__"}:
                if pno <= 5 and needle in txt:
                    resolved[key] = str(pno)
                    break
            elif key in {"__P_VIET_TAT__", "__P_HINH_BANG__"}:
                if 7 <= pno <= 9 and needle in txt:
                    resolved[key] = str(pno)
                    break
            else:
                if pno >= 10 and needle in txt:
                    resolved[key] = str(pno)
                    break
        resolved.setdefault(key, "—")
    return resolved


def main() -> None:
    chrome_candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    browser_exe = next((p for p in chrome_candidates if p.exists()), None)
    if browser_exe is None:
        raise FileNotFoundError("Chrome or Edge executable not found for headless PDF printing.")

    # Pass 1: initial PDF to measure exact page numbers
    base_html = build_html()
    _render_pdf(base_html, browser_exe)
    page_map = _resolve_page_numbers(PDF_PATH)

    # Pass 2: inject exact page numbers into TOC and lists
    final_html = base_html
    for k, v in page_map.items():
        final_html = final_html.replace(k, v)
    _render_pdf(final_html, browser_exe)
    print(f"Generated PDF with exact page numbers: {PDF_PATH} ({PDF_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
