def generate_professional_pdf(item, qty, price):
    pdf = FPDF()
    pdf.add_page()
    # إضافة لون خلفية (رمادي فاتح) للهيدر
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(0, 0, 210, 30, 'F')
    
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 20, "صيدلية غسق - الفاتورة الضريبية", ln=True, align='C')
    
    # تفاصيل الفاتورة بتنسيق جدول
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(0, 51, 102) # أزرق داكن
    pdf.set_text_color(255, 255, 255)
    pdf.cell(100, 10, "الصنف", 1, 0, 'C', 1)
    pdf.cell(40, 10, "الكمية", 1, 0, 'C', 1)
    pdf.cell(50, 10, "الإجمالي", 1, 1, 'C', 1)
    
    # بيانات الصنف
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, str(item), 1, 0, 'C')
    pdf.cell(40, 10, str(qty), 1, 0, 'C')
    pdf.cell(50, 10, f"{price * qty} ريال", 1, 1, 'C')
    
    # تذييل
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, f"التاريخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1')
