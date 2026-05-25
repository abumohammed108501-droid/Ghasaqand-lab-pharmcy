elif page == "🛒 نقطة البيع (POS)":
    st.title("🛒 نقطة البيع السريعة")
    
    # حقل البحث (هنا ستضع الباركود أو تكتب اسم الصنف)
    # ملاحظة: إذا كان لديك باركود رقمي، يمكنك تخزينه في قاعدة البيانات كـ "اسم الصنف"
    search_query = st.text_input("📍 امسح الباركود أو اكتب اسم الصنف:")
    
    if search_query:
        conn = sqlite3.connect('ghasaq_os.db')
        # البحث عن الصنف في المخزون
        item_data = pd.read_sql_query("SELECT * FROM inventory WHERE item_name = ?", conn, params=(search_query,))
        conn.close()
        
        if not item_data.empty:
            st.success(f"✅ تم العثور على: {item_data['item_name'].values[0]} | السعر: {item_data['price'].values[0]} ريال")
            
            # عرض الكمية المتبقية للتنبيه
            st.info(f"الكمية المتاحة: {item_data['quantity'].values[0]}")
            
            qty = st.number_input("الكمية المباعة", 1)
            
            if st.button("إتمام البيع"):
                success, msg = process_sale("صيدلية", item_data['item_name'].values[0], qty)
                if success:
                    st.success(msg)
                    st.balloons() # إضافة حركة احتفالية بسيطة عند البيع
                    st.rerun() # لتحديث البيانات فوراً
                else:
                    st.error(msg)
        else:
            st.warning("⚠️ الصنف غير موجود في قاعدة البيانات. يرجى التأكد من إضافة الصنف في 'إدارة المخزون'.")
