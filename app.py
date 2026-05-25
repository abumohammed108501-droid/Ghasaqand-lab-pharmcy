# في قسم "نقطة البيع" - استخدم هذا الكود المباشر والسريع:
    elif page == "نقطة البيع":
        st.title("🛒 نقطة البيع")
        
        # حقل الإدخال: الماسح اليدوي (USB Scanner) سيقوم بالكتابة هنا تلقائياً
        item_input = st.text_input("امسح الباركود هنا (أو اكتب اسم الصنف):")
        qty = st.number_input("الكمية", 1)
        
        if st.button("إتمام البيع"):
            if item_input:
                success, price = process_sale(item_input, qty)
                if success:
                    st.success("تم البيع بنجاح!")
                    st.download_button("📥 تحميل الفاتورة", generate_pro_pdf(item_input, qty, price), "invoice.pdf")
                else: st.error("الصنف غير موجود أو غير متوفر في المخزون!")
