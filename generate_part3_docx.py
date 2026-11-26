"""Generate standalone Word (.docx) report for Bài kiểm tra 3 – Tuần 8 (Nhóm 23)."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
FIG_DIR = ROOT / "outputs" / "figures"
DOCX_PATH = ROOT / "Nhóm 23 - Bài kiểm tra 3.docx"


def set_run_font(run, size_pt: float = 13, bold: bool = False, italic: bool = False, color: RGBColor | None = None, font_name: str = "Times New Roman") -> None:
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color


def add_body_p(doc: Document, text: str, bold_prefix: str = "", space_after: float = 6, indent_cm: float = 0.7) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(indent_cm)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.35
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_run_font(r_pre, 13, bold=True)
    r = p.add_run(text)
    set_run_font(r, 13)


def add_bullet(doc: Document, bold_prefix: str, text: str) -> None:
    p = doc.add_paragraph(style="List Bullet")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.3
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        set_run_font(r_pre, 13, bold=True)
    r = p.add_run(text)
    set_run_font(r, 13)


def add_heading_1(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run_font(r, 14, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))
    # Bottom border under H1
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="3" w:color="1E3A8A"/></w:pBdr>')
    p._p.get_or_add_pPr().append(pBdr)


def add_heading_2(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run_font(r, 13, bold=True, color=RGBColor(0x1E, 0x3A, 0x8A))


def add_code_block(doc: Document, code_text: str) -> None:
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    cell.width = Cm(16.0)
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F8FAFC"/>')
    cell._tc.get_or_add_tcPr().append(shading)
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        '<w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>'
        '<w:left w:val="single" w:sz="18" w:space="0" w:color="1E3A8A"/>'
        '</w:tcBorders>'
    )
    cell._tc.get_or_add_tcPr().append(borders)
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(code_text)
    set_run_font(r, 9.5, font_name="Consolas")
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)


def add_styled_table(
    doc: Document,
    caption: str,
    headers: list[str],
    rows: list[list[str]],
    col_widths_cm: list[float],
    center_cols: set[int] | None = None,
    highlight_last_row: bool = False,
) -> None:
    center_cols = center_cols or set()
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(8)
    p_cap.paragraph_format.space_after = Pt(3)
    p_cap.paragraph_format.keep_with_next = True
    r_cap = p_cap.add_run(caption)
    set_run_font(r_cap, 11.5, bold=True)

    table = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Set thin borders on entire table
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="6" w:space="0" w:color="475569"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="475569"/>'
        '<w:left w:val="single" w:sz="6" w:space="0" w:color="475569"/>'
        '<w:right w:val="single" w:sz="6" w:space="0" w:color="475569"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="64748B"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="64748B"/>'
        '</w:tblBorders>'
    )
    tblPr.append(borders)

    # Header row
    hdr_row = table.rows[0]
    trPr = hdr_row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:tblHeader"))
    trPr.append(OxmlElement("w:cantSplit"))

    for c_idx, h_text in enumerate(headers):
        cell = hdr_row.cells[c_idx]
        cell.width = Cm(col_widths_cm[c_idx])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="E2E8F0"/>')
        cell._tc.get_or_add_tcPr().append(shd)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(h_text)
        set_run_font(r, 10.5, bold=True)

    # Data rows
    for r_idx, row_vals in enumerate(rows):
        row = table.rows[r_idx + 1]
        r_trPr = row._tr.get_or_add_trPr()
        r_trPr.append(OxmlElement("w:cantSplit"))
        is_hl = highlight_last_row and (r_idx == len(rows) - 1)
        for c_idx, val in enumerate(row_vals):
            cell = row.cells[c_idx]
            cell.width = Cm(col_widths_cm[c_idx])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if is_hl:
                shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="ECFDF5"/>')
                cell._tc.get_or_add_tcPr().append(shd)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in center_cols else WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(2.5)
            p.paragraph_format.space_after = Pt(2.5)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(val)
            set_run_font(r, 10.5, bold=is_hl)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(4)


def add_figure(doc: Document, img_name: str, caption: str, width_cm: float = 15.6) -> None:
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    run_img = p_img.add_run()
    run_img.add_picture(str(FIG_DIR / img_name), width=Cm(width_cm))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(6)
    r_cap = p_cap.add_run(caption)
    set_run_font(r_cap, 11, italic=True)


def add_page_number_footer(section) -> None:
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p.add_run("Trang ")
    set_run_font(r1, 10.5, color=RGBColor(0x47, 0x55, 0x69))
    fld = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls("w"))
    p._p.append(fld)


def main() -> None:
    doc = Document()

    # A4 page setup
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.0)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.5)
    sec.right_margin = Cm(2.0)
    add_page_number_footer(sec)

    # ===== HEADER / THÔNG TIN CHUNG =====
    p_uni = doc.add_paragraph()
    p_uni.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_uni.paragraph_format.space_after = Pt(2)
    set_run_font(p_uni.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG\nKHOA CÔNG NGHỆ THÔNG TIN"), 12, bold=True)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(4)
    set_run_font(p_title.add_run("BÁO CÁO BÀI KIỂM TRA 3 – TUẦN 8\nTỐI ƯU HÓA, CẢI TIẾN VÀ SO SÁNH MÔ HÌNH"), 15, bold=True, color=RGBColor(0x0F, 0x17, 0x2A))

    p_topic = doc.add_paragraph()
    p_topic.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_topic.paragraph_format.space_after = Pt(10)
    set_run_font(p_topic.add_run("Đề tài: Phân tích giỏ hàng và phát hiện các sản phẩm thường được mua kèm"), 13, bold=True, italic=True)

    add_styled_table(
        doc,
        caption="Thông tin nhóm thực hiện và môi trường tái lập",
        headers=["Thành phần", "Chi tiết thực hiện"],
        rows=[
            ["Giảng viên hướng dẫn", "ThS. Nguyễn Tuấn Anh"],
            ["Lớp học phần / Nhóm", "CNTT K22H – Nhóm 23"],
            ["Sinh viên thực hiện", "1. Trần Văn Thực (MSV: DTC235200734)\n2. Nguyễn Đức An Bình (MSV: DTC235200066)"],
            ["Dữ liệu & Tỷ lệ chia", "Groceries (9.835 hóa đơn gốc → 7.676 giỏ ≥ 2 món; Hold-out 80/20 với random_state=42: 6.140 Train / 1.536 Test)"],
            ["Mã nguồn tái lập", "run_part3_experiments.py, src/part3_experiments.py, src/algorithms.py, app.py (Tab 7)"],
        ],
        col_widths_cm=[4.8, 11.7],
        center_cols=set(),
    )

    # ===== 1. PHÂN TÍCH HẠN CHẾ CỦA MÔ HÌNH BAN ĐẦU =====
    add_heading_1(doc, "1. Phân tích hạn chế của mô hình ban đầu (Tiêu chí 1)")
    add_body_p(
        doc,
        "Ở Bài kiểm tra 2, nhóm đã xây dựng mô hình cơ sở (Most Popular: gợi ý whole milk với Lift = 1,00) và triển khai thực nghiệm 3 thuật toán khai phá luật kết hợp (Apriori tự cài đặt Python, ECLAT, FP-Growth mlxtend) tại ngưỡng khởi điểm min_support = 0,008, min_confidence = 0,25, min_lift = 1,30. Dù cả 3 thuật toán tìm ra chính xác 406 luật giống nhau (Train Lift TB = 1,82; Conf TB = 40,34%), phân tích định lượng sâu hơn cho thấy 3 hạn chế rõ rệt:"
    )
    add_bullet(
        doc,
        "Hạn chế 1 – Thời gian thực thi Apriori tăng theo hàm mũ khi hạ ngưỡng support: ",
        "Khi giảm dần min_support từ 0,050 xuống 0,005 trên tập Train (6.140 giỏ), số lượng tập ứng viên trung gian phải sinh và quét qua toàn bộ danh sách giao dịch tăng vọt (tại 0,008 cần duyệt 5.565 cặp C2 và 2.119 bộ ba C3), đẩy thời gian chạy Apriori từ 0,221s lên 5,668s (Hình 1), gây nghẽn cổ chai nếu mở rộng dữ liệu."
    )
    add_bullet(
        doc,
        "Hạn chế 2 – Nhiễu từ 2.159 giỏ hàng 1 sản phẩm và dao động cao giữa các fold: ",
        "Khi chạy FP-Growth trực tiếp trên dữ liệu thô chưa lọc 2.159 giỏ chỉ có 1 món (chiếm 21,95% trong 9.835 hóa đơn gốc), kiểm định chéo 5-Fold cho CV Confidence TB chỉ đạt 36,28% ± 1,75% (CV Lift TB = 1,897 ± 0,106). Độ lệch chuẩn lớn phản ánh sự thiếu ổn định khi giữ lại các hóa đơn đơn lẻ không mang thông tin mua kèm."
    )
    add_bullet(
        doc,
        "Hạn chế 3 – Tập luật quá rộng, chứa luật dài và luật dư thừa: ",
        "Với min_lift = 1,30 và không giới hạn độ dài max_len, hệ thống sinh tới 406 luật (từ 715 tập phổ biến), bao gồm cả các luật dài 4 sản phẩm khó triển khai trưng bày quầy kệ và các luật có độ liên kết trung bình (Lift 1,30–1,50) hoặc dư thừa so với tập con gọn hơn."
    )

    add_styled_table(
        doc,
        caption="Bảng 1: Kết quả thực nghiệm ban đầu (min_support = 0,008; min_confidence = 0,25; min_lift = 1,30)",
        headers=["Mô hình / Thuật toán", "Số tập phổ biến", "Số luật", "Conf TB (%)", "Lift TB", "Thời gian (s)", "Nhận xét hạn chế"],
        rows=[
            ["Cơ sở (Most Popular)", "—", "1", "31,51%", "1,00", "0,001", "Không xét ngữ cảnh giỏ hàng"],
            ["Apriori (Python tự cài)", "715", "406", "40,34%", "1,82", "3,083", "Chậm (5,67s ở 0,005) do sinh Ck"],
            ["ECLAT (Python tự cài)", "715", "406", "40,34%", "1,82", "0,050", "Nhanh trên dữ liệu thưa"],
            ["FP-Growth (mlxtend)", "715", "406", "40,34%", "1,82", "0,072", "Cần tinh chỉnh ngưỡng & lọc nhiễu"],
        ],
        col_widths_cm=[3.8, 1.8, 1.4, 2.0, 1.5, 2.0, 4.0],
        center_cols={1, 2, 3, 4, 5},
    )

    add_figure(
        doc,
        "fig_benchmark_runtime_memory.png",
        "Hình 1: Đường cong thời gian thực thi (a) và bộ nhớ đỉnh tracemalloc (b) của Apriori, ECLAT và FP-Growth khi giảm dần min_support (0,050 → 0,005).",
        width_cm=15.8,
    )
    add_body_p(
        doc,
        "Nhận xét Hình 1: Đồ thị (a) cho thấy thời gian thực thi của Apriori tăng vọt theo đường cong dốc lên 5,668 giây tại min_support = 0,005, trong khi FP-Growth gần như đi ngang ở mức 0,125 giây (nhanh hơn 45,2 lần) và ECLAT đạt 0,051 giây. Đồ thị (b) đo mức bộ nhớ Python heap (tracemalloc): cả 3 thuật toán tiêu thụ rất nhẹ dưới 8 MB; FP-Growth dùng khoảng 7,95 MB cho cấu trúc cây FP-Tree để đổi lấy tốc độ khai phá vượt trội."
    )

    # ===== 2. ĐỀ XUẤT GIẢI PHÁP CẢI TIẾN =====
    add_heading_1(doc, "2. Đề xuất giải pháp cải tiến (Tiêu chí 2)")
    add_body_p(
        doc,
        "Gắn trực tiếp với 3 hạn chế đã định lượng ở Mục 1, nhóm đề xuất 3 giải pháp cải tiến có cơ sở lý thuyết trong Bảng 2:"
    )
    add_styled_table(
        doc,
        caption="Bảng 2: Bảng đối ứng Hạn chế mô hình ban đầu – Giải pháp cải tiến – Cơ sở lý thuyết",
        headers=["STT", "Hạn chế của mô hình ban đầu", "Giải pháp cải tiến đề xuất", "Cơ sở lý thuyết & Kỳ vọng tác động"],
        rows=[
            [
                "1",
                "Apriori tốn 3,38–5,67s do sinh nhiều tập ứng viên Ck và quét CSDL nhiều lần.",
                "Chuyển lõi khai phá sang FP-Growth (đối sánh cùng ECLAT).",
                "FP-Growth nén toàn bộ giao dịch vào cây tiền tố FP-Tree + Header Table chỉ sau 2 lần quét CSDL, loại bỏ hoàn toàn bước sinh ứng viên Ck."
            ],
            [
                "2",
                "2.159 giỏ 1 món (21,95%) làm loãng Support và gây dao động lớn giữa các fold (Conf Std = ±1,75%).",
                "Cải tiến dữ liệu: Tạo đặc trưng Basket_Size và lọc bỏ giỏ < 2 món trước khi chia Train/Test.",
                "Giỏ 1 sản phẩm không chứa quan hệ đồng xuất hiện. Loại bỏ giúp làm sạch phân phối giỏ mua kèm và giảm phương sai thống kê giữa các fold."
            ],
            [
                "3",
                "406 luật ở Lift ≥ 1,30 còn luật dài 4 món, luật liên kết yếu và luật dư thừa.",
                "Tối ưu siêu tham số (Grid Search 5-Fold CV) chọn Lift ≥ 1,50, max_len = 3 + Hậu xử lý cắt tỉa luật dư thừa (Pruning).",
                "Loại bỏ luật X ⇒ Y nếu đã tồn tại tập con X' ⊂ X có Confidence(X'⇒Y) ≥ Confidence(X⇒Y), giúp tập luật tinh gọn, dễ diễn giải và ổn định hơn."
            ],
        ],
        col_widths_cm=[1.0, 4.7, 4.9, 5.9],
        center_cols={0},
    )

    # ===== 3. CẢI TIẾN DỮ LIỆU VÀ ĐẶC TRƯNG =====
    add_heading_1(doc, "3. Cải tiến dữ liệu và đặc trưng (Tiêu chí 3)")
    add_body_p(
        doc,
        "Trong src/data_pipeline.py, nhóm bổ sung bước chuẩn hóa tập hợp (set) để loại bỏ sản phẩm trùng trong cùng hóa đơn, tính đặc trưng phái sinh Basket_Size (số mặt hàng duy nhất trong giỏ) và lọc bỏ toàn bộ 2.159 giỏ có Basket_Size < 2. Sau khi lọc, tập dữ liệu còn lại 7.676 hóa đơn hợp lệ được chia Hold-out 80/20 (random_state=42) thành 6.140 giỏ Train và 1.536 giỏ Test (TransactionEncoder chỉ .fit() trên tập Train)."
    )
    add_code_block(
        doc,
        "# Trích đoạn src/data_pipeline.py: Làm sạch, lọc giỏ < 2 món và mã hóa không rò rỉ\n"
        "clean_baskets = [sorted(set(b)) for b in raw_baskets]\n"
        "filtered_baskets = [b for b in clean_baskets if len(b) >= 2]  # Loại 2.159 giỏ 1 món (21,95%)\n"
        "train_baskets, test_baskets = train_test_split(filtered_baskets, test_size=0.20, random_state=42)\n"
        "te = TransactionEncoder()\n"
        "df_train = pd.DataFrame(te.fit(train_baskets).transform(train_baskets), columns=te.columns_)"
    )

    add_styled_table(
        doc,
        caption="Bảng 3: Tác động trước – sau cải tiến dữ liệu (so sánh trên cùng cấu hình FP-Growth, Lift ≥ 1,30)",
        headers=["Chỉ tiêu đánh giá", "Trước cải tiến (Dữ liệu thô 9.835 giỏ)", "Sau cải tiến (Lọc giỏ ≥ 2 món: 7.676 giỏ)", "Mức thay đổi"],
        rows=[
            ["Số giỏ hợp lệ (Train / Test)", "7.868 / 1.967", "6.140 / 1.536", "Loại 2.159 giỏ nhiễu (21,95%)"],
            ["Độ dày ma trận One-Hot (Train)", "2,61%", "3,14%", "+0,53 điểm %"],
            ["Số luật khai phá được", "286", "406", "+120 luật hàng ngách"],
            ["CV Confidence TB ± Std (%)", "36,28% ± 1,75%", "38,46% ± 1,09%", "+2,18% (Std giảm 37,7%)"],
            ["CV Lift TB ± Std", "1,897 ± 0,106", "1,751 ± 0,058", "-0,146 (Std giảm 45,3%)"],
        ],
        col_widths_cm=[4.8, 3.9, 4.3, 3.5],
        center_cols={1, 2, 3},
    )
    add_body_p(
        doc,
        "Giải thích tác động: Việc bỏ 2.159 giỏ 1 món làm mẫu số Support thu hẹp (9.835 → 7.676), giúp 120 cặp sản phẩm ngách vượt ngưỡng min_support = 0,008 (số luật tăng từ 286 lên 406). Nhờ đó CV Confidence tăng rõ rệt (+2,18%) và độ lệch chuẩn giữa các fold giảm gần một nửa (Lift Std giảm từ 0,106 xuống 0,058). Giá trị Lift TB giảm nhẹ ở bước này chính là do 120 luật mới được mở khóa có Lift nằm trong vùng 1,30–1,50 — đây là cơ sở để bước tối ưu siêu tham số tiếp theo nâng lại độ mạnh của tập luật."
    )

    # ===== 4. THỬ NGHIỆM THUẬT TOÁN VÀ CẤU HÌNH KHÁC =====
    add_heading_1(doc, "4. Thử nghiệm thuật toán và cấu hình hậu xử lý khác (Tiêu chí 4)")
    add_body_p(
        doc,
        "Ngoài đối sánh giữa 3 thuật toán khai phá tập phổ biến (Apriori tự cài đặt theo phương pháp quét ngang BFS, ECLAT theo biểu diễn dọc TID-set DFS, và FP-Growth nén cây FP-Tree của mlxtend), nhóm thử nghiệm thêm cấu hình hậu xử lý Cắt tỉa luật dư thừa (Redundant Rule Pruning — hàm prune_redundant_rules trong src/part3_experiments.py). Cơ chế cắt tỉa loại bỏ mọi luật X ⇒ Y (với |X| ≥ 2) nếu tồn tại luật gọn hơn X' ⊂ X có cùng vế phải Y và đạt Confidence(X'⇒Y) ≥ Confidence(X⇒Y)."
    )
    add_styled_table(
        doc,
        caption="Bảng 4: So sánh hiệu năng 3 thuật toán qua các ngưỡng min_support (trên 6.140 giỏ Train, max_len = 3)",
        headers=["min_support", "Số tập phổ biến", "Apriori (s)", "ECLAT (s)", "FP-Growth (s)", "Apriori (MB)", "ECLAT (MB)", "FP-Growth (MB)"],
        rows=[
            ["0,050", "41", "0,221", "0,016", "0,030", "3,04", "2,18", "2,20"],
            ["0,030", "98", "0,694", "0,022", "0,067", "3,43", "2,58", "3,79"],
            ["0,020", "178", "1,185", "0,032", "0,076", "3,62", "2,81", "4,56"],
            ["0,010", "514", "2,351", "0,034", "0,100", "4,40", "3,16", "5,97"],
            ["0,008", "715", "3,379", "0,051", "0,116", "5,09", "3,27", "6,50"],
            ["0,005", "1.520", "5,668", "0,051", "0,125", "7,20", "3,64", "7,95"],
        ],
        col_widths_cm=[2.0, 2.2, 2.0, 2.0, 2.3, 2.0, 2.0, 2.0],
        center_cols={0, 1, 2, 3, 4, 5, 6, 7},
    )

    # ===== 5. TỐI ƯU HÓA SIÊU THAM SỐ =====
    add_heading_1(doc, "5. Tối ưu hóa siêu tham số bằng Grid Search trên 5-Fold CV (Tiêu chí 5)")
    add_body_p(
        doc,
        "Để chọn siêu tham số khách quan mà không làm rò rỉ thông tin từ tập kiểm tra, nhóm cài đặt hàm run_cv_grid_search sử dụng KFold(n_splits=5, shuffle=True, random_state=42) chỉ trên 6.140 giỏ Train (mỗi lượt 4.912 giỏ Train / 1.228 giỏ Validation; TransactionEncoder chỉ fit trên 4.912 giỏ của từng fold). Tập kiểm tra giữ lại (1.536 giỏ) hoàn toàn không tham gia vào bước tìm kiếm này."
    )
    add_code_block(
        doc,
        "# Trích đoạn src/part3_experiments.py: Grid Search 5-Fold CV chỉ trên tập Train\n"
        "grid_df = run_cv_grid_search(\n"
        "    bundle.train_baskets,\n"
        "    support_grid=[0.005, 0.008, 0.010, 0.015],\n"
        "    confidence_grid=[0.20, 0.25, 0.30],\n"
        "    lift_grid=[1.30, 1.50, 1.80],\n"
        "    max_len_grid=[2, 3, None],\n"
        "    n_splits=5,\n"
        ")  # Tổng cộng 108 tổ hợp siêu tham số x 5 fold"
    )

    add_styled_table(
        doc,
        caption="Bảng 5: Không gian tìm kiếm và kết quả tiêu biểu từ Grid Search 5-Fold CV (chỉ trên tập Train)",
        headers=["min_support", "min_conf", "min_lift", "max_len", "Số luật TB ± Std", "CV Lift TB ± Std", "CV Conf TB ± Std (%)", "Đánh giá lựa chọn"],
        rows=[
            ["0,005", "0,20", "1,80", "None", "806,6 ± 58,2", "2,208 ± 0,125", "35,22 ± 1,50", "Quá nhiều luật, Std cao gấp đôi"],
            ["0,005", "0,25", "1,80", "2", "37,6 ± 3,4", "2,114 ± 0,092", "32,10 ± 1,18", "Ít luật, bỏ sót tổ hợp 3 món"],
            ["0,008", "0,25", "1,30", "3", "330,4 ± 17,2", "1,697 ± 0,061", "38,40 ± 1,07", "Còn nhiều luật liên kết yếu"],
            ["0,008", "0,25", "1,50", "3", "223,2 ± 13,5", "1,817 ± 0,069", "38,94 ± 1,05", "Tối ưu: mạnh, gọn & ổn định"],
            ["0,010", "0,25", "1,50", "3", "131,8 ± 7,1", "1,831 ± 0,066", "38,24 ± 0,95", "Số luật giảm ~41%"],
        ],
        col_widths_cm=[1.8, 1.6, 1.6, 1.5, 2.3, 2.4, 2.5, 2.8],
        center_cols={0, 1, 2, 3, 4, 5, 6},
    )

    add_figure(
        doc,
        "fig_cv_validation_curve.png",
        "Hình 2: Đường cong kiểm định chéo 5-Fold biểu diễn CV Lift trung bình (± Std) theo min_support và min_lift tại min_confidence = 0,25, max_len = 3.",
        width_cm=14.6,
    )
    add_body_p(
        doc,
        "Nhận xét Hình 2: Khi siết min_lift từ 1,30 lên 1,80, giá trị CV Lift tăng nhưng độ dài thanh sai số (Std giữa 5 fold) tăng gần gấp đôi và thu hẹp quá mức độ phủ sản phẩm. Ngưỡng min_support = 0,008, min_confidence = 0,25, min_lift = 1,50, max_len = 3 đạt điểm cân bằng tốt nhất: Lift trung bình đạt 1,817 với độ lệch chuẩn thấp (0,069) và CV Confidence cao nhất trong nhóm thử nghiệm (38,94%)."
    )

    # ===== 6. SO SÁNH TRƯỚC VÀ SAU CẢI TIẾN (ABLATION STUDY) =====
    add_heading_1(doc, "6. So sánh trước và sau cải tiến – Ablation Study (Tiêu chí 6)")
    add_body_p(
        doc,
        "Bảng 6 tổng hợp đóng góp của từng thay đổi trên cùng bộ dữ liệu Groceries, cùng chiến lược chia Hold-out 80/20 (random_state = 42) và cùng hệ chỉ số đánh giá:"
    )
    add_styled_table(
        doc,
        caption="Bảng 6: Nghiên cứu đóng góp từng bước cải tiến (Ablation Study) trên 5-Fold CV và Hold-out Test 20%",
        headers=["Cấu hình mô hình", "Số luật (Train)", "CV Lift TB ± Std", "CV Conf TB ± Std (%)", "Test Lift TB", "Test Conf TB (%)", "Δ CV Lift"],
        rows=[
            ["0. Cơ sở (Most Popular: whole milk)", "1", "1,000 ± 0,000", "31,51 ± 0,00", "1,000", "29,75", "—"],
            ["1. FP-Growth ban đầu (dữ liệu thô, Lift≥1,30)", "286", "1,897 ± 0,106", "36,28 ± 1,75", "2,033", "36,79", "+0,897"],
            ["2. + Cải tiến dữ liệu (Lọc giỏ < 2 món)", "406", "1,751 ± 0,058", "38,46 ± 1,09", "1,697", "34,71", "-0,146"],
            ["3. + Tối ưu tham số (Lift≥1,50, max_len=3)", "270", "1,817 ± 0,069", "38,94 ± 1,05", "1,788", "34,98", "+0,066"],
            ["4. + Hậu xử lý cắt tỉa luật dư thừa (Pruning)", "266", "1,816 ± 0,067", "38,91 ± 0,96", "1,784", "35,07", "-0,001"],
        ],
        col_widths_cm=[5.1, 1.6, 2.3, 2.4, 1.7, 1.8, 1.6],
        center_cols={1, 2, 3, 4, 5, 6},
        highlight_last_row=True,
    )
    add_body_p(
        doc,
        "Phân tích đóng góp từng bước: Bước (2) lọc giỏ < 2 món giúp tăng CV Confidence (+2,18%) và giảm 45% độ dao động Lift Std; Bước (3) tối ưu siêu tham số nâng lại CV Lift (+0,066) và loại bỏ các luật dài > 3 món; Bước (4) cắt tỉa 4 luật dư thừa (270 → 266 luật) giữ nguyên chất lượng Lift trong khi đưa CV Conf Std xuống mức thấp nhất (0,96%) và Test Confidence đạt mức cao nhất sau lọc (35,07%)."
    )

    # ===== 7. KHẢ NĂNG TỔNG QUÁT HÓA =====
    add_heading_1(doc, "7. Đánh giá khả năng tổng quát hóa và lựa chọn mô hình cuối (Tiêu chí 7)")
    add_body_p(
        doc,
        "Sau khi chốt toàn bộ cấu hình ở Mục 5–6, mô hình cuối cùng (FP-Growth + Lọc giỏ ≥ 2 món + min_support = 0,008, min_confidence = 0,25, min_lift = 1,50, max_len = 3 + Pruning) được huấn luyện lại trên 100% tập Train (6.140 giỏ, thu được 266 luật với Train Lift TB = 1,920, Train Conf TB = 41,37%) và đem đánh giá một lần duy nhất trên Tập kiểm tra giữ lại (1.536 giỏ chưa từng thấy):"
    )
    add_styled_table(
        doc,
        caption="Bảng 7: Đối chiếu hiệu năng giữa 5-Fold CV (Train) và Tập kiểm tra giữ lại (Test 20%)",
        headers=["Chỉ số đánh giá", "Mục tiêu (Bài 1)", "5-Fold CV (Mean ± Std)", "Hold-out Test (1.536 giỏ)", "Độ lệch CV → Test"],
        rows=[
            ["Lift trung bình", "≥ 1,30", "1,816 ± 0,067", "1,784", "-1,76% (trong ±1 Std)"],
            ["Confidence trung bình", "≥ 25,0%", "38,91% ± 0,96%", "35,07%", "-3,84 điểm %"],
            ["Thời gian khai phá", "Nhanh hơn Apriori ≥ 3×", "0,116s (tại 0,008)", "—", "Nhanh hơn Apriori 29,1×"],
        ],
        col_widths_cm=[3.5, 2.8, 3.6, 3.3, 3.3],
        center_cols={1, 2, 3, 4},
    )
    add_body_p(
        doc,
        "Kết luận tổng quát hóa & Lựa chọn mô hình cuối: Độ lệch Lift giữa kiểm định chéo (1,816) và kiểm tra độc lập (1,784) chỉ là -1,76%, nằm gọn trong 1 độ lệch chuẩn (±0,067) qua 5 fold, khẳng định mô hình không bị quá khớp vào dữ liệu lịch sử. Nhóm lựa chọn mô hình FP-Growth sau tối ưu & Pruning (266 luật) làm mô hình cuối vì đạt cân bằng tốt nhất giữa độ mạnh luật, độ ổn định qua các fold, tốc độ xử lý nhanh và tập luật ngắn (≤ 3 món) dễ triển khai thực tế."
    )

    add_styled_table(
        doc,
        caption="Bảng 8: Top 8 luật kết hợp mạnh nhất của mô hình cuối cùng (266 luật sau Pruning)",
        headers=["Hạng", "Sản phẩm đã mua (Vế trái X)", "Gợi ý mua kèm (Vế phải Y)", "Support (%)", "Conf (%)", "Lift", "Conviction"],
        rows=[
            ["1", "butter, other vegetables", "whipped/sour cream", "0,81%", "30,7%", "3,41", "1,31"],
            ["2", "herbs", "root vegetables", "0,91%", "46,7%", "3,33", "1,61"],
            ["3", "berries", "whipped/sour cream", "1,19%", "27,4%", "3,05", "1,25"],
            ["4", "other vegetables, tropical fruit", "pip fruit", "1,30%", "28,2%", "2,94", "1,26"],
            ["5", "other vegetables, pip fruit", "tropical fruit", "1,30%", "38,3%", "2,88", "1,41"],
            ["6", "beef, other vegetables", "root vegetables", "1,07%", "39,5%", "2,82", "1,42"],
            ["7", "root vegetables, yogurt", "whipped/sour cream", "0,88%", "25,2%", "2,81", "1,22"],
            ["8", "pip fruit, yogurt", "tropical fruit", "0,90%", "36,9%", "2,78", "1,37"],
        ],
        col_widths_cm=[1.2, 4.8, 3.8, 1.8, 1.6, 1.5, 1.8],
        center_cols={0, 3, 4, 5, 6},
    )

    # ===== 8. TRỰC QUAN HÓA KẾT QUẢ THỰC NGHIỆM =====
    add_heading_1(doc, "8. Trực quan hóa kết quả thực nghiệm (Tiêu chí 8)")
    add_figure(
        doc,
        "fig_ablation_cv_vs_test.png",
        "Hình 3: So sánh chỉ số Lift (a) và Confidence (b) giữa 5-Fold CV (Mean ± Std) và Tập kiểm tra 20% qua từng bước cải tiến.",
        width_cm=15.8,
    )
    add_body_p(
        doc,
        "Nhận xét Hình 3: Tất cả các bước cải tiến với FP-Growth đều vượt xa đường ngưỡng mục tiêu màu đỏ (Lift ≥ 1,30 và Confidence ≥ 25,0%) cũng như mô hình cơ sở (Most Popular: Lift = 1,00). Thanh sai số ở Bước 3 và Bước 4 rất ngắn (Std Lift = 0,067; Std Conf = 0,96%) và cột xanh lá (Hold-out Test 20%) bám sát cột xanh dương (5-Fold CV), minh chứng trực quan cho tính ổn định của mô hình cuối cùng."
    )

    add_figure(
        doc,
        "fig_3_3_rules_scatter.png",
        "Hình 4: Phân bố Support (%), Confidence (%) và Lift của 266 luật kết hợp cuối cùng (sau tối ưu và cắt tỉa luật dư thừa).",
        width_cm=14.6,
    )
    add_body_p(
        doc,
        "Nhận xét Hình 4: Toàn bộ 266 luật đều nằm phía trên đường ngưỡng Confidence = 25% và đạt Lift từ 1,50 đến 3,41. Nhóm luật có Lift cao nhất (vàng – xanh lục, Lift > 2,8) tập trung ở vùng Support 0,8% – 1,5% (các cặp sản phẩm đặc thù như herbs → root vegetables, butter + other vegetables → whipped/sour cream), khẳng định ý nghĩa của việc hạ min_support kết hợp siết chặt Lift."
    )

    add_figure(
        doc,
        "fig_3_7_network.png",
        "Hình 5: Mạng lưới 15 luật kết hợp mạnh nhất theo Lift từ mô hình FP-Growth cuối cùng.",
        width_cm=15.4,
    )
    add_body_p(
        doc,
        "Nhận xét Hình 5: Đồ thị có hướng trực quan hóa rõ các nút tâm điểm thu hút nhiều liên kết mua kèm là other vegetables, whipped/sour cream, tropical fruit và root vegetables. Mạng luật này là cơ sở để phân khu sắp xếp quầy kệ liền kề trong siêu thị và tích hợp trực tiếp vào công cụ gợi ý mua kèm trên ứng dụng demo Streamlit (app.py)."
    )

    DOCX_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(DOCX_PATH))
    print(f"Generated Word document: {DOCX_PATH} ({DOCX_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
