# أضف هذا الجزء داخل دالة إضافة المخزون
from barcode import EAN13
from barcode.writer import ImageWriter

def create_barcode(code_str):
    ean = EAN13(code_str, writer=ImageWriter())
    ean.save(f"barcodes/{code_str}")
