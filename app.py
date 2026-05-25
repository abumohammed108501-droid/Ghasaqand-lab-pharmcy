# --- داخل صفحة نقطة البيع ---
if st.session_state.show_invoice:
    # 1. عرض الفاتورة بشكل ملون واحترافي داخل التطبيق
    invoice_html = f"""
    <div style="background-color: #f9f9f9; padding: 20px; border: 2px solid #007BFF; border-radius: 10px;">
        <h2 style="color: #007BFF; text-align: center;">صيدلية غسق</h2>
        <p><strong>التاريخ:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <hr>
        <p><strong>الصنف:</strong> {barcode}</p>
        <p><strong>الكمية:</strong> {qty}</p>
        <h3 style="color: #28a745;">الإجمالي: {qty * 10} ريال</h3>
    </div>
    """
    st.markdown(invoice_html, unsafe_allow_html=True)
    
    # 2. زر التحميل (مع إصلاح تشفير اللغة العربية)
    final_text = f"صيدلية غسق\nالتاريخ: {datetime.now()}\nالصنف: {barcode}\nالكمية: {qty}"
    st.download_button(
        label="📥 تحميل الفاتورة كملف نصي",
        data=final_text.encode('utf-8-sig'), # هذا هو السطر الذي يحل مشكلة الرموز
        file_name="invoice.txt",
        mime="text/plain"
    )
    
    st.info("💡 نصيحة: للطباعة بالألوان، اضغط على زر 'الطباعة' في متصفحك (Ctrl+P) بعد رؤية التصميم أعلاه.")
