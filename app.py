
import { useState, useEffect, useRef, useCallback } from "react";

// ============================================================
// MOCK DATA & RRB SYSTEM
// ============================================================
const generateExpiry = (monthsFromNow) => {
  const d = new Date();
  d.setMonth(d.getMonth() + monthsFromNow);
  return d.toISOString().split("T")[0];
};

const initialInventory = [
  { id: 1, barcode: "6001234567890", name: "أموكسيسيلين 500mg", category: "مضادات حيوية", qty: 120, minQty: 15, price: 250, cost: 180, expiry: generateExpiry(8), supplier: "شركة النيل الدوائية", rrb: "RRB-2024-001", location: "رف A1" },
  { id: 2, barcode: "6001234567891", name: "باراسيتامول 500mg", category: "مسكنات", qty: 12, minQty: 15, price: 50, cost: 30, expiry: generateExpiry(2), supplier: "دار الدواء", rrb: "RRB-2024-002", location: "رف B2" },
  { id: 3, barcode: "6001234567892", name: "ميتفورمين 500mg", category: "سكري", qty: 80, minQty: 15, price: 180, cost: 120, expiry: generateExpiry(12), supplier: "شركة الخرطوم للأدوية", rrb: "RRB-2024-003", location: "رف C1" },
  { id: 4, barcode: "6001234567893", name: "أملوديبين 5mg", category: "ضغط الدم", qty: 8, minQty: 15, price: 300, cost: 200, expiry: generateExpiry(6), supplier: "شركة النيل الدوائية", rrb: "RRB-2024-004", location: "رف C2" },
  { id: 5, barcode: "6001234567894", name: "لوراتادين 10mg", category: "مضادات الحساسية", qty: 45, minQty: 15, price: 120, cost: 80, expiry: generateExpiry(1), supplier: "دار الدواء", rrb: "RRB-2024-005", location: "رف D1" },
  { id: 6, barcode: "6001234567895", name: "أوميبرازول 20mg", category: "معدة", qty: 60, minQty: 15, price: 200, cost: 140, expiry: generateExpiry(10), supplier: "شركة الخرطوم للأدوية", rrb: "RRB-2024-006", location: "رف B1" },
  { id: 7, barcode: "6001234567896", name: "سيبروفلوكساسين 500mg", category: "مضادات حيوية", qty: 5, minQty: 15, price: 350, cost: 250, expiry: generateExpiry(4), supplier: "شركة النيل الدوائية", rrb: "RRB-2024-007", location: "رف A2" },
  { id: 8, barcode: "6001234567897", name: "فيتامين C 1000mg", category: "فيتامينات", qty: 200, minQty: 15, price: 90, cost: 60, expiry: generateExpiry(18), supplier: "دار الدواء", rrb: "RRB-2024-008", location: "رف E1" },
  { id: 9, barcode: "6001234567898", name: "ديكلوفيناك 50mg", category: "مسكنات", qty: 14, minQty: 15, price: 150, cost: 100, expiry: generateExpiry(3), supplier: "شركة الخرطوم للأدوية", rrb: "RRB-2024-009", location: "رف B3" },
  { id: 10, barcode: "6001234567899", name: "ميترونيدازول 500mg", category: "مضادات حيوية", qty: 35, minQty: 15, price: 200, cost: 140, expiry: generateExpiry(7), supplier: "شركة النيل الدوائية", rrb: "RRB-2024-010", location: "رف A3" },
];

const initialSales = [
  { id: "INV-2024-001", date: "2024-01-15", customer: "أحمد محمد", items: [{name:"أموكسيسيلين 500mg", qty:2, price:250}], total: 500, paid: 500, change: 0 },
  { id: "INV-2024-002", date: "2024-01-16", customer: "فاطمة علي", items: [{name:"باراسيتامول 500mg", qty:3, price:50}], total: 150, paid: 200, change: 50 },
  { id: "INV-2024-003", date: "2024-01-17", customer: "عمر حسن", items: [{name:"ميتفورمين 500mg", qty:1, price:180}], total: 180, paid: 180, change: 0 },
];

// ============================================================
// UTILITY FUNCTIONS
// ============================================================
const getDaysToExpiry = (expiry) => {
  const today = new Date();
  const exp = new Date(expiry);
  return Math.ceil((exp - today) / (1000 * 60 * 60 * 24));
};

const formatSDG = (amount) => `${amount.toLocaleString("ar-SD")} ج.س`;

const generateInvoiceId = () => `INV-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 9000) + 1000)}`;

// ============================================================
// PDF INVOICE GENERATOR
// ============================================================
const generatePDFInvoice = (invoice, items) => {
  const printWindow = window.open("", "_blank");
  const total = items.reduce((s, i) => s + i.qty * i.price, 0);
  const html = `
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
      <meta charset="UTF-8">
      <title>فاتورة - ${invoice.id}</title>
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Cairo', sans-serif; background: #fff; color: #1a1a2e; padding: 30px; }
        .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #00b4d8; padding-bottom: 20px; margin-bottom: 20px; }
        .logo { font-size: 28px; font-weight: 700; color: #0077b6; }
        .logo span { color: #00b4d8; }
        .invoice-info { text-align: left; font-size: 13px; }
        .invoice-id { font-size: 20px; font-weight: 700; color: #0077b6; }
        .customer-box { background: #f0f9ff; border-right: 4px solid #00b4d8; padding: 15px; margin: 20px 0; border-radius: 8px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #0077b6; color: white; padding: 12px; text-align: right; }
        td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; }
        tr:nth-child(even) { background: #f8fafc; }
        .totals { background: #f0f9ff; padding: 20px; border-radius: 8px; text-align: left; }
        .total-line { display: flex; justify-content: space-between; padding: 5px 0; }
        .grand-total { font-size: 20px; font-weight: 700; color: #0077b6; border-top: 2px solid #0077b6; padding-top: 10px; margin-top: 10px; }
        .footer { text-align: center; margin-top: 30px; color: #64748b; font-size: 12px; border-top: 1px solid #e2e8f0; padding-top: 20px; }
        .rrb-badge { display: inline-block; background: #0077b6; color: white; padding: 3px 10px; border-radius: 4px; font-size: 11px; }
        @media print { body { padding: 10px; } }
      </style>
    </head>
    <body>
      <div class="header">
        <div>
          <div class="logo">صيدلية <span>الرعاية</span></div>
          <div style="font-size:12px; color:#64748b;">نظام الرعاية الصيدلانية المتكامل</div>
          <div style="font-size:12px; color:#64748b;">الخرطوم - السودان | هاتف: 0123456789</div>
        </div>
        <div class="invoice-info">
          <div class="invoice-id">${invoice.id}</div>
          <div>التاريخ: ${invoice.date}</div>
          <div>الوقت: ${new Date().toLocaleTimeString("ar-SD")}</div>
          <div style="margin-top:5px"><span class="rrb-badge">نظام RRB</span></div>
        </div>
      </div>
      <div class="customer-box">
        <strong>العميل:</strong> ${invoice.customer || "عميل نقدي"} &nbsp;&nbsp;
        <strong>رقم الهاتف:</strong> ${invoice.phone || "---"} &nbsp;&nbsp;
        <strong>طريقة الدفع:</strong> نقدي
      </div>
      <table>
        <thead>
          <tr><th>#</th><th>اسم الدواء</th><th>الكمية</th><th>السعر</th><th>الإجمالي</th></tr>
        </thead>
        <tbody>
          ${items.map((item, i) => `
            <tr>
              <td>${i + 1}</td>
              <td>${item.name}</td>
              <td>${item.qty}</td>
              <td>${item.price.toLocaleString()} ج.س</td>
              <td>${(item.qty * item.price).toLocaleString()} ج.س</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
      <div class="totals">
        <div class="total-line"><span>المجموع:</span><span>${total.toLocaleString()} ج.س</span></div>
        <div class="total-line"><span>الخصم:</span><span>0 ج.س</span></div>
        <div class="total-line grand-total"><span>الإجمالي:</span><span>${total.toLocaleString()} ج.س</span></div>
        <div class="total-line"><span>المبلغ المدفوع:</span><span>${invoice.paid?.toLocaleString() || total.toLocaleString()} ج.س</span></div>
        <div class="total-line"><span>الباقي:</span><span>${((invoice.paid || total) - total).toLocaleString()} ج.س</span></div>
      </div>
      <div class="footer">
        <p>شكراً لزيارتكم صيدلية الرعاية</p>
        <p>للاستفسارات: 0123456789 | هذه الفاتورة صالحة للضمان خلال 7 أيام</p>
        <p style="margin-top:8px; font-size:10px; color:#94a3b8;">تم إنشاؤها بواسطة نظام الرعاية الصيدلانية المتكامل - RRB System v2.0</p>
      </div>
      <script>window.onload = () => { window.print(); }</script>
    </body>
    </html>
  `;
  printWindow.document.write(html);
  printWindow.document.close();
};

// ============================================================
// BARCODE SCANNER COMPONENT
// ============================================================
function BarcodeScanner({ onScan, onClose }) {
  const videoRef = useRef(null);
  const [status, setStatus] = useState("جاري تشغيل الكاميرا...");
  const [manualBarcode, setManualBarcode] = useState("");
  const streamRef = useRef(null);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: "environment", width: 640, height: 480 }
        });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
          setStatus("🎥 الكاميرا تعمل - وجه الباركود أمام الكاميرا");
        }
      } catch (e) {
        setStatus("⚠️ تعذر الوصول للكاميرا - استخدم الإدخال اليدوي");
      }
    };
    startCamera();
    return () => {
      if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
    };
  }, []);

  const handleManualScan = () => {
    if (manualBarcode.trim()) {
      onScan(manualBarcode.trim());
      setManualBarcode("");
    }
  };

  return (
    <div style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.85)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1000}}>
      <div style={{background:"#0f172a",borderRadius:20,padding:24,width:480,maxWidth:"95vw",border:"1px solid #1e3a5f"}}>
        <div style={{display:"flex",justifyContent:"space-between",alignItems:"center",marginBottom:16}}>
          <h3 style={{color:"#00b4d8",fontFamily:"Cairo",fontSize:18,margin:0}}>📷 ماسح الباركود</h3>
          <button onClick={() => { if(streamRef.current) streamRef.current.getTracks().forEach(t=>t.stop()); onClose(); }}
            style={{background:"#ef4444",color:"white",border:"none",borderRadius:8,padding:"6px 14px",cursor:"pointer",fontFamily:"Cairo"}}>✕ إغلاق</button>
        </div>
        <div style={{background:"#000",borderRadius:12,overflow:"hidden",position:"relative",height:240,marginBottom:16}}>
          <video ref={videoRef} style={{width:"100%",height:"100%",objectFit:"cover"}} muted playsInline />
          <div style={{position:"absolute",inset:0,border:"2px solid #00b4d8",borderRadius:12,boxShadow:"inset 0 0 30px rgba(0,180,216,0.1)"}} />
          <div style={{position:"absolute",top:"50%",left:"10%",right:"10%",height:2,background:"rgba(0,180,216,0.7)",boxShadow:"0 0 8px #00b4d8",animation:"scan 2s linear infinite"}} />
        </div>
        <p style={{color:"#94a3b8",textAlign:"center",fontSize:12,marginBottom:16,fontFamily:"Cairo"}}>{status}</p>
        <div style={{display:"flex",gap:8}}>
          <input
            value={manualBarcode}
            onChange={e => setManualBarcode(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleManualScan()}
            placeholder="أدخل الباركود يدوياً أو من USB..."
            style={{flex:1,background:"#1e293b",border:"1px solid #334155",borderRadius:8,padding:"10px 14px",color:"white",fontFamily:"Cairo",fontSize:14,direction:"ltr"}}
            autoFocus
          />
          <button onClick={handleManualScan}
            style={{background:"#00b4d8",color:"white",border:"none",borderRadius:8,padding:"10px 16px",cursor:"pointer",fontFamily:"Cairo",fontWeight:700}}>مسح</button>
        </div>
        <p style={{color:"#475569",fontSize:11,textAlign:"center",marginTop:8,fontFamily:"Cairo"}}>💡 يدعم ماسح USB - اضغط Enter بعد المسح</p>
      </div>
      <style>{`@keyframes scan { 0%{top:20%} 50%{top:80%} 100%{top:20%} }`}</style>
    </div>
  );
}

// ============================================================
// ALERT COMPONENT
// ============================================================
function AlertBanner({ inventory }) {
  const lowStock = inventory.filter(i => i.qty <= i.minQty);
  const expiringSoon = inventory.filter(i => getDaysToExpiry(i.expiry) <= 30 && getDaysToExpiry(i.expiry) > 0);
  const expired = inventory.filter(i => getDaysToExpiry(i.expiry) <= 0);
  if (!lowStock.length && !expiringSoon.length && !expired.length) return null;
  return (
    <div style={{display:"flex",flexDirection:"column",gap:8,marginBottom:16}}>
      {expired.length > 0 && (
        <div style={{background:"rgba(239,68,68,0.15)",border:"1px solid #ef4444",borderRadius:10,padding:"10px 16px",display:"flex",alignItems:"center",gap:10,fontFamily:"Cairo"}}>
          <span style={{fontSize:20}}>🚫</span>
          <span style={{color:"#fca5a5",fontWeight:600,fontSize:14}}>
            {expired.length} صنف منتهي الصلاحية: {expired.map(i=>i.name).join(" | ")}
          </span>
        </div>
      )}
      {lowStock.length > 0 && (
        <div style={{background:"rgba(245,158,11,0.15)",border:"1px solid #f59e0b",borderRadius:10,padding:"10px 16px",display:"flex",alignItems:"center",gap:10,fontFamily:"Cairo"}}>
          <span style={{fontSize:20}}>⚠️</span>
          <span style={{color:"#fcd34d",fontWeight:600,fontSize:14}}>
            مخزون منخفض (≤15): {lowStock.map(i=>`${i.name} (${i.qty})`).join(" | ")}
          </span>
        </div>
      )}
      {expiringSoon.length > 0 && (
        <div style={{background:"rgba(234,179,8,0.15)",border:"1px solid #eab308",borderRadius:10,padding:"10px 16px",display:"flex",alignItems:"center",gap:10,fontFamily:"Cairo"}}>
          <span style={{fontSize:20}}>⏳</span>
          <span style={{color:"#fef08a",fontWeight:600,fontSize:14}}>
            تنتهي خلال 30 يوم: {expiringSoon.map(i=>`${i.name} (${getDaysToExpiry(i.expiry)} يوم)`).join(" | ")}
          </span>
        </div>
      )}
    </div>
  );
}

// ============================================================
// DASHBOARD
// ============================================================
function Dashboard({ inventory, sales }) {
  const totalItems = inventory.length;
  const lowStock = inventory.filter(i => i.qty <= i.minQty).length;
  const totalValue = inventory.reduce((s, i) => s + i.qty * i.price, 0);
  const todaySales = sales.filter(s => s.date === new Date().toISOString().split("T")[0]).reduce((sum, s) => sum + s.total, 0);
  const monthSales = sales.reduce((sum, s) => sum + s.total, 0);
  const expiredCount = inventory.filter(i => getDaysToExpiry(i.expiry) <= 0).length;

  const salesByDay = {};
  sales.forEach(s => { salesByDay[s.date] = (salesByDay[s.date] || 0) + s.total; });
  const salesDays = Object.entries(salesByDay).slice(-7);

  const categoryCount = {};
  inventory.forEach(i => { categoryCount[i.category] = (categoryCount[i.category] || 0) + 1; });
  const categories = Object.entries(categoryCount);

  const maxSale = Math.max(...salesDays.map(([,v]) => v), 1);
  const maxCat = Math.max(...categories.map(([,v]) => v), 1);

  const StatCard = ({ label, value, icon, color, sub }) => (
    <div style={{background:"#0f172a",borderRadius:16,padding:"20px 24px",border:`1px solid ${color}30`,position:"relative",overflow:"hidden"}}>
      <div style={{position:"absolute",top:0,right:0,width:80,height:80,background:`${color}10`,borderRadius:"0 16px 0 80px"}} />
      <div style={{fontSize:32,marginBottom:8}}>{icon}</div>
      <div style={{color:"#94a3b8",fontSize:12,fontFamily:"Cairo",marginBottom:4}}>{label}</div>
      <div style={{color:color,fontSize:24,fontWeight:700,fontFamily:"Cairo"}}>{value}</div>
      {sub && <div style={{color:"#475569",fontSize:11,fontFamily:"Cairo",marginTop:4}}>{sub}</div>}
    </div>
  );

  return (
    <div style={{fontFamily:"Cairo"}}>
      <AlertBanner inventory={inventory} />
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(180px,1fr))",gap:16,marginBottom:24}}>
        <StatCard label="إجمالي الأصناف" value={totalItems} icon="💊" color="#00b4d8" />
        <StatCard label="مبيعات اليوم" value={formatSDG(todaySales)} icon="💰" color="#10b981" sub={`${sales.length} فاتورة إجمالاً`} />
        <StatCard label="قيمة المخزون" value={formatSDG(totalValue)} icon="📦" color="#8b5cf6" />
        <StatCard label="أصناف منخفضة" value={lowStock} icon="⚠️" color="#f59e0b" sub="تحت حد 15" />
        <StatCard label="منتهية الصلاحية" value={expiredCount} icon="🚫" color="#ef4444" />
        <StatCard label="إجمالي المبيعات" value={formatSDG(monthSales)} icon="📊" color="#06b6d4" />
      </div>

      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16,marginBottom:24}}>
        {/* Sales Chart */}
        <div style={{background:"#0f172a",borderRadius:16,padding:20,border:"1px solid #1e3a5f"}}>
          <h3 style={{color:"#00b4d8",marginBottom:16,fontSize:16}}>📈 المبيعات الأخيرة</h3>
          <div style={{display:"flex",alignItems:"flex-end",gap:8,height:120}}>
            {salesDays.length === 0 ? (
              <p style={{color:"#475569",fontSize:13}}>لا توجد بيانات</p>
            ) : salesDays.map(([date, val]) => (
              <div key={date} style={{flex:1,display:"flex",flexDirection:"column",alignItems:"center",gap:4}}>
                <div style={{width:"100%",background:"linear-gradient(180deg,#00b4d8,#0077b6)",borderRadius:"4px 4px 0 0",height:`${(val/maxSale)*100}px`,minHeight:4,transition:"height 0.5s ease"}} />
                <span style={{color:"#475569",fontSize:9,transform:"rotate(-45deg)",whiteSpace:"nowrap"}}>{date.slice(5)}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Category Chart */}
        <div style={{background:"#0f172a",borderRadius:16,padding:20,border:"1px solid #1e3a5f"}}>
          <h3 style={{color:"#10b981",marginBottom:16,fontSize:16}}>📋 الأصناف حسب الفئة</h3>
          <div style={{display:"flex",flexDirection:"column",gap:8}}>
            {categories.slice(0,5).map(([cat, count], i) => {
              const colors = ["#00b4d8","#10b981","#8b5cf6","#f59e0b","#ef4444"];
              return (
                <div key={cat}>
                  <div style={{display:"flex",justifyContent:"space-between",marginBottom:4}}>
                    <span style={{color:"#cbd5e1",fontSize:12}}>{cat}</span>
                    <span style={{color:colors[i%5],fontSize:12,fontWeight:700}}>{count}</span>
                  </div>
                  <div style={{background:"#1e293b",borderRadius:4,height:6}}>
                    <div style={{background:colors[i%5],height:"100%",borderRadius:4,width:`${(count/maxCat)*100}%`,transition:"width 0.5s ease"}} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Low Stock Table */}
      <div style={{background:"#0f172a",borderRadius:16,padding:20,border:"1px solid #f59e0b30"}}>
        <h3 style={{color:"#f59e0b",marginBottom:16,fontSize:16}}>⚠️ الأصناف التي تحتاج إعادة طلب (RRB)</h3>
        <div style={{overflowX:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse"}}>
            <thead>
              <tr style={{borderBottom:"1px solid #1e293b"}}>
                {["الصنف","الكمية","الحد الأدنى","الفئة","رقم RRB","الموقع"].map(h => (
                  <th key={h} style={{color:"#64748b",fontSize:12,padding:"8px 12px",textAlign:"right",fontWeight:600}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {inventory.filter(i => i.qty <= i.minQty).map(item => (
                <tr key={item.id} style={{borderBottom:"1px solid #0f172a"}}>
                  <td style={{padding:"8px 12px",color:"#f1f5f9",fontSize:13}}>{item.name}</td>
                  <td style={{padding:"8px 12px"}}><span style={{background:"#ef444420",color:"#fca5a5",padding:"2px 8px",borderRadius:6,fontSize:12}}>{item.qty}</span></td>
                  <td style={{padding:"8px 12px",color:"#94a3b8",fontSize:12}}>{item.minQty}</td>
                  <td style={{padding:"8px 12px",color:"#94a3b8",fontSize:12}}>{item.category}</td>
                  <td style={{padding:"8px 12px"}}><span style={{background:"#0077b630",color:"#00b4d8",padding:"2px 8px",borderRadius:6,fontSize:11}}>{item.rrb}</span></td>
                  <td style={{padding:"8px 12px",color:"#94a3b8",fontSize:12}}>{item.location}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// POINT OF SALE
// ============================================================
function POS({ inventory, setInventory, sales, setSales }) {
  const [cart, setCart] = useState([]);
  const [search, setSearch] = useState("");
  const [barcodeInput, setBarcodeInput] = useState("");
  const [customer, setCustomer] = useState("");
  const [phone, setPhone] = useState("");
  const [paid, setPaid] = useState("");
  const [showScanner, setShowScanner] = useState(false);
  const [lastInvoice, setLastInvoice] = useState(null);
  const barcodeRef = useRef(null);

  const filtered = inventory.filter(i =>
    i.name.toLowerCase().includes(search.toLowerCase()) ||
    i.barcode.includes(search) || i.category.includes(search)
  );

  const addToCart = (item) => {
    if (item.qty <= 0) return alert("هذا الصنف غير متوفر في المخزون!");
    setCart(prev => {
      const ex = prev.find(c => c.id === item.id);
      if (ex) {
        if (ex.qty >= item.qty) return alert("لا يوجد مخزون كافٍ!") || prev;
        return prev.map(c => c.id === item.id ? {...c, qty: c.qty+1} : c);
      }
      return [...prev, {...item, qty:1, salePrice: item.price}];
    });
  };

  const handleBarcodeSearch = (barcode) => {
    const item = inventory.find(i => i.barcode === barcode);
    if (item) { addToCart(item); setBarcodeInput(""); }
    else alert(`لم يتم العثور على الصنف بالباركود: ${barcode}`);
  };

  const total = cart.reduce((s, i) => s + i.qty * i.salePrice, 0);
  const paidNum = parseFloat(paid) || 0;
  const change = paidNum - total;

  const checkout = () => {
    if (!cart.length) return;
    if (paidNum < total) return alert("المبلغ المدفوع أقل من الإجمالي!");
    const invoice = {
      id: generateInvoiceId(),
      date: new Date().toISOString().split("T")[0],
      customer: customer || "عميل نقدي",
      phone,
      items: cart.map(i => ({name:i.name, qty:i.qty, price:i.salePrice})),
      total, paid: paidNum, change
    };
    setSales(prev => [invoice, ...prev]);
    setInventory(prev => prev.map(i => {
      const ci = cart.find(c => c.id === i.id);
      return ci ? {...i, qty: i.qty - ci.qty} : i;
    }));
    setLastInvoice(invoice);
    generatePDFInvoice(invoice, cart);
    setCart([]); setCustomer(""); setPhone(""); setPaid("");
  };

  return (
    <div style={{display:"grid",gridTemplateColumns:"1fr 340px",gap:16,height:"calc(100vh - 140px)",fontFamily:"Cairo"}}>
      {showScanner && <BarcodeScanner onScan={b => { handleBarcodeSearch(b); setShowScanner(false); }} onClose={() => setShowScanner(false)} />}

      {/* Products Grid */}
      <div style={{display:"flex",flexDirection:"column",gap:12,overflow:"hidden"}}>
        <div style={{display:"flex",gap:8}}>
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="🔍 ابحث عن دواء..."
            style={{flex:1,background:"#0f172a",border:"1px solid #1e3a5f",borderRadius:10,padding:"10px 16px",color:"white",fontFamily:"Cairo",fontSize:14}} />
          <input ref={barcodeRef} value={barcodeInput} onChange={e => setBarcodeInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleBarcodeSearch(barcodeInput)}
            placeholder="📷 باركود USB..."
            style={{width:160,background:"#0f172a",border:"1px solid #00b4d830",borderRadius:10,padding:"10px 14px",color:"white",fontFamily:"Cairo",fontSize:13,direction:"ltr"}} />
          <button onClick={() => setShowScanner(true)}
            style={{background:"#00b4d8",color:"white",border:"none",borderRadius:10,padding:"10px 16px",cursor:"pointer",fontSize:18,whiteSpace:"nowrap"}}>📷</button>
        </div>
        <div style={{overflowY:"auto",flex:1}}>
          <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fill,minmax(160px,1fr))",gap:10}}>
            {filtered.map(item => {
              const days = getDaysToExpiry(item.expiry);
              const isLow = item.qty <= item.minQty;
              const isExpired = days <= 0;
              return (
                <button key={item.id} onClick={() => addToCart(item)} disabled={item.qty <= 0}
                  style={{background:"#0f172a",border:`1px solid ${isExpired?"#ef4444":isLow?"#f59e0b":"#1e293b"}`,borderRadius:12,padding:14,cursor:item.qty>0?"pointer":"not-allowed",textAlign:"right",transition:"all 0.2s",opacity:item.qty<=0?0.5:1}}>
                  <div style={{fontSize:24,marginBottom:6}}>💊</div>
                  <div style={{color:"#f1f5f9",fontSize:13,fontWeight:600,marginBottom:4,lineHeight:1.3}}>{item.name}</div>
                  <div style={{color:"#64748b",fontSize:11,marginBottom:6}}>{item.category}</div>
                  <div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}>
                    <span style={{color:"#10b981",fontWeight:700,fontSize:14}}>{formatSDG(item.price)}</span>
                    <span style={{background:isLow?"#f59e0b20":isExpired?"#ef444420":"#10b98120",color:isLow?"#fcd34d":isExpired?"#fca5a5":"#6ee7b7",padding:"2px 6px",borderRadius:6,fontSize:11}}>{item.qty}</span>
                  </div>
                  {isExpired && <div style={{color:"#ef4444",fontSize:10,marginTop:4}}>🚫 منتهي الصلاحية</div>}
                  {!isExpired && days <= 30 && <div style={{color:"#f59e0b",fontSize:10,marginTop:4}}>⏳ {days} يوم</div>}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Cart */}
      <div style={{background:"#0f172a",borderRadius:16,padding:16,border:"1px solid #1e3a5f",display:"flex",flexDirection:"column",gap:12,overflow:"hidden"}}>
        <h3 style={{color:"#00b4d8",margin:0,fontSize:16}}>🛒 سلة المشتريات</h3>
        <div style={{display:"flex",flexDirection:"column",gap:8}}>
          <input value={customer} onChange={e => setCustomer(e.target.value)} placeholder="اسم العميل (اختياري)"
            style={{background:"#1e293b",border:"1px solid #334155",borderRadius:8,padding:"8px 12px",color:"white",fontFamily:"Cairo",fontSize:13}} />
          <input value={phone} onChange={e => setPhone(e.target.value)} placeholder="رقم الهاتف"
            style={{background:"#1e293b",border:"1px solid #334155",borderRadius:8,padding:"8px 12px",color:"white",fontFamily:"Cairo",fontSize:13,direction:"ltr"}} />
        </div>
        <div style={{flex:1,overflowY:"auto",display:"flex",flexDirection:"column",gap:6}}>
          {cart.length === 0 ? (
            <div style={{textAlign:"center",color:"#475569",marginTop:40}}>
              <div style={{fontSize:40,marginBottom:8}}>🛒</div>
              <p style={{fontSize:13}}>السلة فارغة</p>
            </div>
          ) : cart.map(item => (
            <div key={item.id} style={{background:"#1e293b",borderRadius:10,padding:"10px 12px"}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:6}}>
                <span style={{color:"#f1f5f9",fontSize:12,fontWeight:600}}>{item.name}</span>
                <button onClick={() => setCart(prev => prev.filter(c => c.id !== item.id))}
                  style={{background:"#ef444420",color:"#fca5a5",border:"none",borderRadius:6,padding:"2px 8px",cursor:"pointer",fontSize:12}}>✕</button>
              </div>
              <div style={{display:"flex",alignItems:"center",gap:8}}>
                <button onClick={() => setCart(prev => prev.map(c => c.id===item.id && c.qty>1 ? {...c,qty:c.qty-1} : c))}
                  style={{background:"#334155",color:"white",border:"none",borderRadius:6,width:28,height:28,cursor:"pointer",fontSize:16}}>−</button>
                <span style={{color:"#f1f5f9",fontWeight:700,minWidth:24,textAlign:"center"}}>{item.qty}</span>
                <button onClick={() => setCart(prev => prev.map(c => c.id===item.id ? {...c,qty:Math.min(c.qty+1,inventory.find(i=>i.id===c.id)?.qty||c.qty)} : c))}
                  style={{background:"#334155",color:"white",border:"none",borderRadius:6,width:28,height:28,cursor:"pointer",fontSize:16}}>+</button>
                <input type="number" value={item.salePrice}
                  onChange={e => setCart(prev => prev.map(c => c.id===item.id ? {...c,salePrice:parseFloat(e.target.value)||0} : c))}
                  style={{flex:1,background:"#0f172a",border:"1px solid #334155",borderRadius:6,padding:"4px 8px",color:"#10b981",fontFamily:"Cairo",fontSize:12,textAlign:"left"}} />
                <span style={{color:"#64748b",fontSize:11}}>{formatSDG(item.qty*item.salePrice)}</span>
              </div>
            </div>
          ))}
        </div>
        <div style={{borderTop:"1px solid #1e293b",paddingTop:12}}>
          <div style={{display:"flex",justifyContent:"space-between",marginBottom:8}}>
            <span style={{color:"#94a3b8",fontSize:14}}>الإجمالي:</span>
            <span style={{color:"#10b981",fontWeight:700,fontSize:18}}>{formatSDG(total)}</span>
          </div>
          <input type="number" value={paid} onChange={e => setPaid(e.target.value)} placeholder="المبلغ المدفوع"
            style={{width:"100%",background:"#1e293b",border:"1px solid #334155",borderRadius:8,padding:"10px 12px",color:"white",fontFamily:"Cairo",fontSize:14,textAlign:"left",boxSizing:"border-box",marginBottom:8}} />
          {paid && (
            <div style={{display:"flex",justifyContent:"space-between",marginBottom:8}}>
              <span style={{color:"#94a3b8",fontSize:13}}>الباقي:</span>
              <span style={{color:change>=0?"#10b981":"#ef4444",fontWeight:700,fontSize:16}}>{formatSDG(Math.abs(change))}{change<0?" (ناقص)":""}</span>
            </div>
          )}
          <button onClick={checkout} disabled={!cart.length || paidNum < total}
            style={{width:"100%",background:cart.length&&paidNum>=total?"linear-gradient(135deg,#0077b6,#00b4d8)":"#1e293b",color:cart.length&&paidNum>=total?"white":"#475569",border:"none",borderRadius:10,padding:"12px",cursor:cart.length&&paidNum>=total?"pointer":"not-allowed",fontFamily:"Cairo",fontWeight:700,fontSize:15,transition:"all 0.2s"}}>
            ✅ إتمام البيع وطباعة الفاتورة
          </button>
          {cart.length > 0 && <button onClick={() => setCart([])}
            style={{width:"100%",background:"transparent",color:"#ef4444",border:"1px solid #ef444430",borderRadius:10,padding:"8px",cursor:"pointer",fontFamily:"Cairo",fontSize:13,marginTop:8}}>🗑️ إفراغ السلة</button>}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// INVENTORY
// ============================================================
function Inventory({ inventory, setInventory }) {
  const [search, setSearch] = useState("");
  const [showScanner, setShowScanner] = useState(false);
  const [editItem, setEditItem] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [filter, setFilter] = useState("all");
  const [newItem, setNewItem] = useState({barcode:"",name:"",category:"",qty:0,minQty:15,price:0,cost:0,expiry:"",supplier:"",rrb:"",location:""});

  const filtered = inventory.filter(i => {
    const matchSearch = i.name.includes(search) || i.barcode.includes(search) || i.category.includes(search);
    if (filter === "low") return matchSearch && i.qty <= i.minQty;
    if (filter === "expired") return matchSearch && getDaysToExpiry(i.expiry) <= 0;
    if (filter === "expiring") return matchSearch && getDaysToExpiry(i.expiry) > 0 && getDaysToExpiry(i.expiry) <= 30;
    return matchSearch;
  });

  const saveEdit = () => {
    setInventory(prev => prev.map(i => i.id === editItem.id ? editItem : i));
    setEditItem(null);
  };

  const addItem = () => {
    const item = {...newItem, id: Date.now(), rrb: newItem.rrb || `RRB-${new Date().getFullYear()}-${String(inventory.length+1).padStart(3,"0")}`};
    setInventory(prev => [...prev, item]);
    setShowAdd(false);
    setNewItem({barcode:"",name:"",category:"",qty:0,minQty:15,price:0,cost:0,expiry:"",supplier:"",rrb:"",location:""});
  };

  const deleteItem = (id) => { if(confirm("هل تريد حذف هذا الصنف؟")) setInventory(prev => prev.filter(i => i.id !== id)); };

  const FormField = ({label, value, onChange, type="text", placeholder=""}) => (
    <div>
      <label style={{color:"#94a3b8",fontSize:12,display:"block",marginBottom:4}}>{label}</label>
      <input type={type} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder}
        style={{width:"100%",background:"#0f172a",border:"1px solid #334155",borderRadius:8,padding:"8px 12px",color:"white",fontFamily:"Cairo",fontSize:13,boxSizing:"border-box"}} />
    </div>
  );

  const ModalForm = ({title, item, setItem, onSave, onClose}) => (
    <div style={{position:"fixed",inset:0,background:"rgba(0,0,0,0.8)",display:"flex",alignItems:"center",justifyContent:"center",zIndex:1000}}>
      <div style={{background:"#0f172a",borderRadius:20,padding:24,width:560,maxWidth:"95vw",border:"1px solid #1e3a5f",maxHeight:"90vh",overflowY:"auto"}}>
        <div style={{display:"flex",justifyContent:"space-between",marginBottom:20}}>
          <h3 style={{color:"#00b4d8",fontFamily:"Cairo",margin:0}}>{title}</h3>
          <button onClick={onClose} style={{background:"#ef4444",color:"white",border:"none",borderRadius:8,padding:"6px 14px",cursor:"pointer",fontFamily:"Cairo"}}>✕</button>
        </div>
        <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:12}}>
          <FormField label="الباركود" value={item.barcode} onChange={v => setItem({...item,barcode:v})} />
          <FormField label="اسم الدواء *" value={item.name} onChange={v => setItem({...item,name:v})} />
          <FormField label="الفئة" value={item.category} onChange={v => setItem({...item,category:v})} />
          <FormField label="الكمية" type="number" value={item.qty} onChange={v => setItem({...item,qty:parseInt(v)||0})} />
          <FormField label="الحد الأدنى للتنبيه" type="number" value={item.minQty} onChange={v => setItem({...item,minQty:parseInt(v)||15})} />
          <FormField label="سعر البيع (ج.س)" type="number" value={item.price} onChange={v => setItem({...item,price:parseFloat(v)||0})} />
          <FormField label="سعر التكلفة (ج.س)" type="number" value={item.cost} onChange={v => setItem({...item,cost:parseFloat(v)||0})} />
          <FormField label="تاريخ الصلاحية" type="date" value={item.expiry} onChange={v => setItem({...item,expiry:v})} />
          <FormField label="المورد" value={item.supplier} onChange={v => setItem({...item,supplier:v})} />
          <FormField label="رقم RRB" value={item.rrb} onChange={v => setItem({...item,rrb:v})} placeholder="يُنشأ تلقائياً" />
          <FormField label="موقع الرف" value={item.location} onChange={v => setItem({...item,location:v})} placeholder="مثال: رف A1" />
        </div>
        <button onClick={onSave} style={{width:"100%",background:"linear-gradient(135deg,#0077b6,#00b4d8)",color:"white",border:"none",borderRadius:10,padding:"12px",cursor:"pointer",fontFamily:"Cairo",fontWeight:700,fontSize:15,marginTop:20}}>
          💾 حفظ
        </button>
      </div>
    </div>
  );

  return (
    <div style={{fontFamily:"Cairo"}}>
      {showScanner && <BarcodeScanner onScan={b => { const item = inventory.find(i => i.barcode === b); if(item) setEditItem(item); else alert("لم يوجد!"); setShowScanner(false); }} onClose={() => setShowScanner(false)} />}
      {editItem && <ModalForm title="✏️ تعديل الصنف" item={editItem} setItem={setEditItem} onSave={saveEdit} onClose={() => setEditItem(null)} />}
      {showAdd && <ModalForm title="➕ إضافة صنف جديد" item={newItem} setItem={setNewItem} onSave={addItem} onClose={() => setShowAdd(false)} />}

      <AlertBanner inventory={inventory} />

      <div style={{display:"flex",gap:8,marginBottom:16,flexWrap:"wrap"}}>
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="🔍 بحث..."
          style={{flex:1,minWidth:160,background:"#0f172a",border:"1px solid #1e3a5f",borderRadius:10,padding:"10px 16px",color:"white",fontFamily:"Cairo",fontSize:14}} />
        {["all","low","expired","expiring"].map(f => (
          <button key={f} onClick={() => setFilter(f)}
            style={{background:filter===f?"#0077b6":"#0f172a",color:filter===f?"white":"#94a3b8",border:"1px solid #1e3a5f",borderRadius:8,padding:"8px 14px",cursor:"pointer",fontFamily:"Cairo",fontSize:13}}>
            {f==="all"?"الكل":f==="low"?"مخزون منخفض ⚠️":f==="expired"?"منتهي 🚫":"قارب الانتهاء ⏳"}
          </button>
        ))}
        <button onClick={() => setShowScanner(true)} style={{background:"#1e293b",color:"#00b4d8",border:"1px solid #00b4d830",borderRadius:8,padding:"8px 14px",cursor:"pointer",fontFamily:"Cairo",fontSize:13}}>📷 مسح</button>
        <button onClick={() => setShowAdd(true)} style={{background:"linear-gradient(135deg,#0077b6,#00b4d8)",color:"white",border:"none",borderRadius:8,padding:"8px 14px",cursor:"pointer",fontFamily:"Cairo",fontSize:13,fontWeight:700}}>➕ إضافة صنف</button>
      </div>

      <div style={{background:"#0f172a",borderRadius:16,overflow:"hidden",border:"1px solid #1e3a5f"}}>
        <div style={{overflowX:"auto"}}>
          <table style={{width:"100%",borderCollapse:"collapse",minWidth:900}}>
            <thead>
              <tr style={{background:"#0c1a2e"}}>
                {["الباركود","اسم الدواء","الفئة","الكمية","سعر البيع","الصلاحية","RRB","الموقع","إجراءات"].map(h => (
                  <th key={h} style={{color:"#64748b",fontSize:12,padding:"12px 14px",textAlign:"right",fontWeight:600,whiteSpace:"nowrap"}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map(item => {
                const days = getDaysToExpiry(item.expiry);
                const isLow = item.qty <= item.minQty;
                const isExpired = days <= 0;
                return (
                  <tr key={item.id} style={{borderBottom:"1px solid #0f172a",background:isExpired?"rgba(239,68,68,0.05)":isLow?"rgba(245,158,11,0.05)":"transparent"}}>
                    <td style={{padding:"10px 14px",color:"#475569",fontSize:11,fontFamily:"monospace"}}>{item.barcode}</td>
                    <td style={{padding:"10px 14px",color:"#f1f5f9",fontSize:13,fontWeight:600}}>{item.name}</td>
                    <td style={{padding:"10px 14px"}}><span style={{background:"#0077b620",color:"#7dd3fc",padding:"2px 8px",borderRadius:6,fontSize:11}}>{item.category}</span></td>
                    <td style={{padding:"10px 14px"}}><span style={{background:isLow?"#f59e0b20":"#10b98120",color:isLow?"#fcd34d":"#6ee7b7",padding:"3px 10px",borderRadius:8,fontSize:13,fontWeight:700}}>{item.qty}</span></td>
                    <td style={{padding:"10px 14px",color:"#10b981",fontWeight:600,fontSize:13}}>{formatSDG(item.price)}</td>
                    <td style={{padding:"10px 14px"}}>
                      <span style={{color:isExpired?"#fca5a5":days<=30?"#fcd34d":"#6ee7b7",fontSize:12}}>
                        {isExpired ? "🚫 منتهي" : `${item.expiry} (${days}ي)`}
                      </span>
                    </td>
                    <td style={{padding:"10px 14px"}}><span style={{background:"#0077b630",color:"#00b4d8",padding:"2px 8px",borderRadius:6,fontSize:10,fontFamily:"monospace"}}>{item.rrb}</span></td>
                    <td style={{padding:"10px 14px",color:"#94a3b8",fontSize:12}}>{item.location}</td>
                    <td style={{padding:"10px 14px"}}>
                      <div style={{display:"flex",gap:6}}>
                        <button onClick={() => setEditItem(item)} style={{background:"#0077b620",color:"#00b4d8",border:"none",borderRadius:6,padding:"4px 10px",cursor:"pointer",fontSize:12}}>✏️</button>
                        <button onClick={() => deleteItem(item.id)} style={{background:"#ef444420",color:"#fca5a5",border:"none",borderRadius:6,padding:"4px 10px",cursor:"pointer",fontSize:12}}>🗑️</button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div style={{padding:"10px 16px",borderTop:"1px solid #1e293b",color:"#475569",fontSize:12,textAlign:"right"}}>
          إجمالي الأصناف: {filtered.length} من {inventory.length}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// SALES HISTORY
// ============================================================
function SalesHistory({ sales }) {
  const [search, setSearch] = useState("");
  const filtered = sales.filter(s => s.id.includes(search) || (s.customer||"").includes(search));
  return (
    <div style={{fontFamily:"Cairo"}}>
      <div style={{marginBottom:16,display:"flex",gap:8}}>
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="🔍 بحث في الفواتير..."
          style={{flex:1,background:"#0f172a",border:"1px solid #1e3a5f",borderRadius:10,padding:"10px 16px",color:"white",fontFamily:"Cairo",fontSize:14}} />
      </div>
      <div style={{background:"#0f172a",borderRadius:16,overflow:"hidden",border:"1px solid #1e3a5f"}}>
        <table style={{width:"100%",borderCollapse:"collapse"}}>
          <thead>
            <tr style={{background:"#0c1a2e"}}>
              {["رقم الفاتورة","التاريخ","العميل","الأصناف","الإجمالي","المدفوع","الباقي","الفاتورة"].map(h => (
                <th key={h} style={{color:"#64748b",fontSize:12,padding:"12px 14px",textAlign:"right",fontWeight:600}}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map(sale => (
              <tr key={sale.id} style={{borderBottom:"1px solid #0f172a"}}>
                <td style={{padding:"10px 14px",color:"#00b4d8",fontFamily:"monospace",fontSize:12}}>{sale.id}</td>
                <td style={{padding:"10px 14px",color:"#94a3b8",fontSize:12}}>{sale.date}</td>
                <td style={{padding:"10px 14px",color:"#f1f5f9",fontSize:13}}>{sale.customer}</td>
                <td style={{padding:"10px 14px",color:"#94a3b8",fontSize:12}}>{sale.items?.length || 1} صنف</td>
                <td style={{padding:"10px 14px",color:"#10b981",fontWeight:700}}>{formatSDG(sale.total)}</td>
                <td style={{padding:"10px 14px",color:"#6ee7b7",fontSize:13}}>{formatSDG(sale.paid)}</td>
                <td style={{padding:"10px 14px",color:"#fcd34d",fontSize:13}}>{formatSDG(sale.change)}</td>
                <td style={{padding:"10px 14px"}}>
                  <button onClick={() => generatePDFInvoice(sale, sale.items || [])}
                    style={{background:"#0077b620",color:"#00b4d8",border:"none",borderRadius:6,padding:"4px 12px",cursor:"pointer",fontSize:12,fontFamily:"Cairo"}}>
                    🖨️ طباعة
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && <p style={{color:"#475569",textAlign:"center",padding:40,fontFamily:"Cairo"}}>لا توجد فواتير</p>}
      </div>
    </div>
  );
}

// ============================================================
// REPORTS
// ============================================================
function Reports({ inventory, sales }) {
  const totalRevenue = sales.reduce((s, i) => s + i.total, 0);
  const totalCost = inventory.reduce((s, i) => s + i.cost * (i.qty || 0), 0);
  const topItems = [...inventory].sort((a,b) => b.qty - a.qty).slice(0,5);
  const categories = {};
  inventory.forEach(i => {
    categories[i.category] = (categories[i.category] || 0) + i.qty * i.price;
  });
  const catEntries = Object.entries(categories).sort(([,a],[,b]) => b-a);
  const maxCatVal = Math.max(...catEntries.map(([,v]) => v), 1);

  return (
    <div style={{fontFamily:"Cairo"}}>
      <div style={{display:"grid",gridTemplateColumns:"repeat(auto-fit,minmax(220px,1fr))",gap:16,marginBottom:24}}>
        {[
          {label:"إجمالي الإيرادات",value:formatSDG(totalRevenue),icon:"💰",color:"#10b981"},
          {label:"قيمة المخزون",value:formatSDG(inventory.reduce((s,i)=>s+i.qty*i.price,0)),icon:"📦",color:"#8b5cf6"},
          {label:"عدد الفواتير",value:sales.length,icon:"🧾",color:"#00b4d8"},
          {label:"متوسط قيمة الفاتورة",value:formatSDG(sales.length?totalRevenue/sales.length:0),icon:"📊",color:"#f59e0b"},
        ].map(s => (
          <div key={s.label} style={{background:"#0f172a",borderRadius:16,padding:"20px 24px",border:`1px solid ${s.color}30`}}>
            <div style={{fontSize:28,marginBottom:8}}>{s.icon}</div>
            <div style={{color:"#94a3b8",fontSize:12,marginBottom:4}}>{s.label}</div>
            <div style={{color:s.color,fontSize:22,fontWeight:700}}>{s.value}</div>
          </div>
        ))}
      </div>

      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
        <div style={{background:"#0f172a",borderRadius:16,padding:20,border:"1px solid #1e3a5f"}}>
          <h3 style={{color:"#00b4d8",marginBottom:16,fontSize:16}}>📦 أعلى الأصناف كمية</h3>
          {topItems.map((item,i) => (
            <div key={item.id} style={{display:"flex",justifyContent:"space-between",padding:"8px 0",borderBottom:"1px solid #1e293b"}}>
              <span style={{color:"#f1f5f9",fontSize:13}}>{i+1}. {item.name}</span>
              <span style={{color:"#10b981",fontWeight:700}}>{item.qty} وحدة</span>
            </div>
          ))}
        </div>
        <div style={{background:"#0f172a",borderRadius:16,padding:20,border:"1px solid #1e3a5f"}}>
          <h3 style={{color:"#8b5cf6",marginBottom:16,fontSize:16}}>📋 قيمة المخزون حسب الفئة</h3>
          {catEntries.map(([cat, val]) => (
            <div key={cat} style={{marginBottom:12}}>
              <div style={{display:"flex",justifyContent:"space-between",marginBottom:4}}>
                <span style={{color:"#cbd5e1",fontSize:12}}>{cat}</span>
                <span style={{color:"#8b5cf6",fontSize:12,fontWeight:700}}>{formatSDG(val)}</span>
              </div>
              <div style={{background:"#1e293b",borderRadius:4,height:6}}>
                <div style={{background:"linear-gradient(90deg,#8b5cf6,#a78bfa)",height:"100%",borderRadius:4,width:`${(val/maxCatVal)*100}%`}} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================
// DOCUMENT SCANNER
// ============================================================
function DocScanner() {
  const [mode, setMode] = useState("camera");
  const [captured, setCaptured] = useState(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [streaming, setStreaming] = useState(false);
  const [docs, setDocs] = useState([]);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment", width: 1280, height: 720 } });
      streamRef.current = stream;
      if (videoRef.current) { videoRef.current.srcObject = stream; videoRef.current.play(); setStreaming(true); }
    } catch { alert("تعذر الوصول للكاميرا"); }
  };

  const capture = () => {
    if (!videoRef.current || !canvasRef.current) return;
    const ctx = canvasRef.current.getContext("2d");
    canvasRef.current.width = videoRef.current.videoWidth;
    canvasRef.current.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0);
    const dataURL = canvasRef.current.toDataURL("image/jpeg", 0.9);
    setCaptured(dataURL);
    setDocs(prev => [{id:Date.now(), date:new Date().toLocaleString("ar-SD"), src:dataURL, name:`مستند ${prev.length+1}`}, ...prev]);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => {
      const src = ev.target.result;
      setDocs(prev => [{id:Date.now(), date:new Date().toLocaleString("ar-SD"), src, name:file.name}, ...prev]);
      setCaptured(src);
    };
    reader.readAsDataURL(file);
  };

  useEffect(() => () => { if(streamRef.current) streamRef.current.getTracks().forEach(t => t.stop()); }, []);

  return (
    <div style={{fontFamily:"Cairo"}}>
      <div style={{display:"flex",gap:8,marginBottom:16}}>
        {["camera","usb"].map(m => (
          <button key={m} onClick={() => setMode(m)}
            style={{background:mode===m?"linear-gradient(135deg,#0077b6,#00b4d8)":"#0f172a",color:mode===m?"white":"#94a3b8",border:"1px solid #1e3a5f",borderRadius:10,padding:"10px 20px",cursor:"pointer",fontFamily:"Cairo",fontSize:14}}>
            {m==="camera"?"📷 الكاميرا اللاسلكية":"🔌 USB / رفع ملف"}
          </button>
        ))}
      </div>

      <div style={{display:"grid",gridTemplateColumns:"1fr 1fr",gap:16}}>
        <div style={{background:"#0f172a",borderRadius:16,padding:20,border:"1px solid #1e3a5f"}}>
          {mode === "camera" ? (
            <div>
              <video ref={videoRef} style={{width:"100%",borderRadius:10,background:"#000",minHeight:200}} muted playsInline />
              <canvas ref={canvasRef} style={{display:"none"}} />
              <div style={{display:"flex",gap:8,marginTop:12}}>
                {!streaming ? (
                  <button onClick={startCamera} style={{flex:1,background:"#0077b6",color:"white",border:"none",borderRadius:10,padding:"12px",cursor:"pointer",fontFamily:"Cairo",fontWeight:700}}>🎥 تشغيل الكاميرا</button>
                ) : (
                  <button onClick={capture} style={{flex:1,background:"linear-gradient(135deg,#10b981,#059669)",color:"white",border:"none",borderRadius:10,padding:"12px",cursor:"pointer",fontFamily:"Cairo",fontWeight:700}}>📸 التقاط مستند</button>
                )}
              </div>
            </div>
          ) : (
            <div style={{textAlign:"center",padding:40}}>
              <div style={{fontSize:64,marginBottom:16}}>🔌</div>
              <p style={{color:"#94a3b8",marginBottom:20}}>ارفع صورة أو مستند من جهازك</p>
              <label style={{background:"linear-gradient(135deg,#0077b6,#00b4d8)",color:"white",padding:"12px 24px",borderRadius:10,cursor:"pointer",fontFamily:"Cairo",fontWeight:700}}>
                📁 اختيار ملف
                <input type="file" accept="image/*,.pdf" onChange={handleFileUpload} style={{display:"none"}} />
              </label>
            </div>
          )}
          {captured && (
            <div style={{marginTop:12}}>
              <img src={captured} alt="مستند ملتقط" style={{width:"100%",borderRadius:10,border:"2px solid #10b981"}} />
              <div style={{display:"flex",gap:8,marginTop:8}}>
                <a href={captured} download={`document-${Date.now()}.jpg`}
                  style={{flex:1,background:"#10b98120",color:"#6ee7b7",border:"1px solid #10b98130",borderRadius:8,padding:"8px",textAlign:"center",textDecoration:"none",fontFamily:"Cairo",fontSize:13}}>
                  ⬇️ تحميل
                </a>
                <button onClick={() => { const w=window.open(); w.document.write(`<img src="${captured}" style="max-width:100%">`); w.print(); }}
                  style={{flex:1,background:"#0077b620",color:"#00b4d8",border:"1px solid #0077b630",borderRadius:8,padding:"8px",cursor:"pointer",fontFamily:"Cairo",fontSize:13}}>
                  🖨️ طباعة
                </button>
              </div>
            </div>
          )}
        </div>

        <div style={{background:"#0f172a",borderRadius:16,padding:20,border:"1px solid #1e3a5f"}}>
          <h3 style={{color:"#00b4d8",marginBottom:16,fontSize:16}}>📂 المستندات المحفوظة ({docs.length})</h3>
          <div style={{display:"flex",flexDirection:"column",gap:10,maxHeight:400,overflowY:"auto"}}>
            {docs.length === 0 ? <p style={{color:"#475569",textAlign:"center",marginTop:40}}>لا توجد مستندات بعد</p> : docs.map(doc => (
              <div key={doc.id} style={{background:"#1e293b",borderRadius:10,padding:12,display:"flex",gap:10,alignItems:"center"}}>
                <img src={doc.src} alt="" style={{width:60,height:50,objectFit:"cover",borderRadius:6}} />
                <div style={{flex:1}}>
                  <div style={{color:"#f1f5f9",fontSize:13,fontWeight:600}}>{doc.name}</div>
                  <div style={{color:"#64748b",fontSize:11}}>{doc.date}</div>
                </div>
                <a href={doc.src} download={doc.name} style={{color:"#00b4d8",fontSize:18,textDecoration:"none"}}>⬇️</a>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// MAIN APP
// ============================================================
export default function PharmacyApp() {
  const [page, setPage] = useState("dashboard");
  const [inventory, setInventory] = useState(initialInventory);
  const [sales, setSales] = useState(initialSales);

  const alertCount = inventory.filter(i => i.qty <= i.minQty || getDaysToExpiry(i.expiry) <= 30).length;

  const navItems = [
    { id:"dashboard", icon:"📊", label:"لوحة التحكم" },
    { id:"pos", icon:"🛒", label:"نقطة البيع" },
    { id:"inventory", icon:"📦", label:"المخزون" },
    { id:"sales", icon:"🧾", label:"الفواتير" },
    { id:"reports", icon:"📈", label:"التقارير" },
    { id:"docs", icon:"📷", label:"المستندات" },
  ];

  const pageComponents = {
    dashboard: <Dashboard inventory={inventory} sales={sales} />,
    pos: <POS inventory={inventory} setInventory={setInventory} sales={sales} setSales={setSales} />,
    inventory: <Inventory inventory={inventory} setInventory={setInventory} />,
    sales: <SalesHistory sales={sales} />,
    reports: <Reports inventory={inventory} sales={sales} />,
    docs: <DocScanner />,
  };

  return (
    <div style={{minHeight:"100vh",background:"#060d18",color:"white",fontFamily:"Cairo, sans-serif",direction:"rtl"}}>
      {/* Header */}
      <div style={{background:"linear-gradient(90deg,#0c1a2e,#0f2744)",borderBottom:"1px solid #1e3a5f",padding:"12px 24px",display:"flex",justifyContent:"space-between",alignItems:"center",position:"sticky",top:0,zIndex:100}}>
        <div style={{display:"flex",alignItems:"center",gap:12}}>
          <div style={{width:40,height:40,background:"linear-gradient(135deg,#0077b6,#00b4d8)",borderRadius:10,display:"flex",alignItems:"center",justifyContent:"center",fontSize:22}}>💊</div>
          <div>
            <div style={{fontWeight:700,fontSize:18,color:"white"}}>نظام الرعاية الصيدلانية</div>
            <div style={{fontSize:11,color:"#64748b"}}>RRB System v2.0 — الخرطوم، السودان</div>
          </div>
        </div>
        <div style={{display:"flex",alignItems:"center",gap:16}}>
          {alertCount > 0 && <div style={{background:"#ef4444",color:"white",borderRadius:20,padding:"4px 12px",fontSize:12,fontWeight:700}}>🔔 {alertCount} تنبيه</div>}
          <div style={{fontSize:12,color:"#64748b"}}>{new Date().toLocaleDateString("ar-SD",{weekday:"long",year:"numeric",month:"long",day:"numeric"})}</div>
        </div>
      </div>

      {/* Navigation */}
      <div style={{background:"#0c1a2e",borderBottom:"1px solid #1e3a5f",padding:"0 24px",display:"flex",gap:4,overflowX:"auto"}}>
        {navItems.map(nav => (
          <button key={nav.id} onClick={() => setPage(nav.id)}
            style={{background:page===nav.id?"linear-gradient(180deg,#0077b640,transparent)":"transparent",color:page===nav.id?"#00b4d8":"#64748b",border:"none",borderBottom:page===nav.id?"2px solid #00b4d8":"2px solid transparent",padding:"14px 20px",cursor:"pointer",fontFamily:"Cairo",fontSize:14,fontWeight:page===nav.id?700:400,whiteSpace:"nowrap",transition:"all 0.2s",display:"flex",alignItems:"center",gap:6}}>
            {nav.icon} {nav.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{padding:24,maxWidth:1400,margin:"0 auto"}}>
        {pageComponents[page]}
      </div>

      {/* Footer */}
      <div style={{textAlign:"center",padding:"20px",borderTop:"1px solid #1e293b",color:"#334155",fontSize:11,marginTop:40}}>
        نظام الرعاية الصيدلانية المتكامل © 2024 — يدعم: نقطة البيع | الباركود | المخزون | تنبيهات RRB | فواتير PDF | تصوير المستندات
      </div>
    </div>
  );
}
