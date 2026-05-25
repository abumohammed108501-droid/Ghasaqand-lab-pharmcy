import cv2
import numpy as np
from pyzbar.pyzbar import decode

# --- أضف هذه الدالة لقراءة الباركود من الصورة ---
def scan_barcode_from_camera(image_file):
    # تحويل الصورة إلى تنسيق مناسب لـ OpenCV
    file_bytes = np.asarray(bytearray(image_file.read()), dtype=np.uint8)
    opencv_image = cv2.imdecode(file_bytes, 1)
    
    # فك تشفير الباركود
    decoded_objects = decode(opencv_image)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')
    return None

# --- داخل قسم "نقطة البيع" في الكود الخاص بك ---
elif page == "نقطة البيع":
    st.title("🛒 نقطة البيع")
    
    # خيار المسح بالكاميرا
    use_camera = st.checkbox("استخدام الكاميرا للمسح")
    scanned_code = None
    
    if use_camera:
        img_file = st.camera_input("وجه الكاميرا نحو الباركود")
        if img_file:
            scanned_code = scan_barcode_from_camera(img_file)
            if scanned_code:
                st.success(f"تم التعرف على الباركود: {scanned_code}")
    
    # حقل الإدخال (سواء يدوياً أو عبر الكاميرا)
    item_input = st.text_input("اسم الصنف أو رقم الباركود:", value=scanned_code if scanned_code else "")
    
    qty = st.number_input("الكمية", 1)
    if st.button("إتمام البيع"):
        # (بقية كود البيع كما هو...)
        pass
