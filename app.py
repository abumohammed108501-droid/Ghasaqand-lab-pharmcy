# --- قسم إدارة المخزون ---
st.markdown("---")
st.title("📦 إدارة المخزون")

with st.form("add_item_form"):
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("اسم الصنف الجديد:")
        new_price = st.number_input("سعر البيع:", min_value=0)
    with col2:
        new_qty = st.number_input("الكمية:", min_value=0)
        new_code = st.text_input("الرمز (الباركود):")
    
    submitted = st.form_submit_button("إضافة صنف للمخزون")
    if submitted:
        new_item = {"الرمز": new_code, "الاسم": new_name, "الكمية": new_qty, "سعر البيع": new_price}
        st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_item])], ignore_index=True)
        st.success(f"تم إضافة {new_name} للمخزون بنجاح!")
        st.rerun()
