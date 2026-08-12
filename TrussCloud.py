import streamlit as st
import requests
import matplotlib.pyplot as plt
import time
import pandas as pd

# ==========================================
# ⚙️ ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Truss Analysis Dashboard", layout="wide")

# ==========================================
# 📌 ข้อมูลสัมประสิทธิ์ทางทฤษฎี (ต่อโหลด 1 kg)
# ==========================================
THEORY_COEFFS = {
    "A": [1.00, -1.00, 1.41, -2.00, 1.41, -1.00, 1.00],
    "B": [2.00, 0.00, -1.41, -1.00, 1.41, -1.00, 1.00],
    "C": [2.00, 1.00, -1.41, -1.00, -1.41, 1.00, 1.00]
}

# ==========================================
# 🎨 ฟังก์ชันวาดรูปโครงถัก (ใช้ได้ทั้ง Dashboard และ ทฤษฎี)
# ==========================================
def draw_truss(format_type, values):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.axis('off')
    ax.set_aspect('equal') # ให้สัดส่วนสมจริง
    
    # กำหนดจุด (Nodes) และเส้น (Members) ตามรูปแบบ
    if format_type == "A":
        nodes = {0: (0,0), 1: (1,0), 4: (2,0), 3: (0,1), 2: (1,1)}
        lines = {1: (3,2), 2: (2,1), 3: (3,1), 4: (0,1), 5: (2,4), 6: (1,4)}
        load_node = 4
    elif format_type == "B":
        nodes = {10: (0,0), 12: (1,0), 14: (2,0), 11: (0,1), 13: (1,1)}
        lines = {1: (11,13), 2: (13,12), 3: (10,13), 4: (10,12), 5: (13,14), 6: (12,14)}
        load_node = 14
    elif format_type == "C":
        nodes = {5: (0,0), 7: (1,0), 6: (0,1), 8: (1,1), 9: (2,1)}
        lines = {1: (6,8), 2: (8,7), 3: (5,8), 4: (5,7), 5: (7,9), 6: (8,9)}
        load_node = 9

    # วาดเส้นโครงถัก (Sensors 1-6)
    for i, (n1, n2) in lines.items():
        val = values[i-1]
        # สี: แดง=ดึง(+), น้ำเงิน=อัด(-), เทา=ศูนย์(0)
        color = '#ff3333' if val > 0.05 else '#3366ff' if val < -0.05 else '#999999'
        x = [nodes[n1][0], nodes[n2][0]]
        y = [nodes[n1][1], nodes[n2][1]]
        ax.plot(x, y, color=color, linewidth=5, zorder=1)
        
        # กล่องข้อความแสดงค่าน้ำหนัก
        mid_x, mid_y = sum(x)/2, sum(y)/2
        ax.text(mid_x, mid_y, f"{val:.2f} kg", ha='center', va='center', 
                bbox=dict(facecolor='white', edgecolor=color, boxstyle='round,pad=0.3'),
                fontsize=10, zorder=3)
    
    # วาดลูกศรโหลด (Sensor 7)
    val7 = values[6]
    lx, ly = nodes[load_node]
    ax.arrow(lx, ly, 0, -0.35, head_width=0.08, head_length=0.1, fc='#ff3333', ec='#ff3333', linewidth=3, zorder=2)
    ax.text(lx, ly - 0.25, f"{val7:.2f} kg", ha='center', va='center',
            bbox=dict(facecolor='white', edgecolor='#ff3333', boxstyle='round,pad=0.3'), zorder=3)
    
    # วาดจุดเชื่อมต่อ (Nodes)
    for n, (x, y) in nodes.items():
        ax.plot(x, y, 'o', color='white', markeredgecolor='#444444', markersize=10, markeredgewidth=2, zorder=4)
        
    # ใส่ Legend (ใช้ภาษาอังกฤษแก้บัค Tofu สี่เหลี่ยมบน Cloud)
    ax.text(0, -0.7, "■ Tension (+)", color='#ff3333', fontsize=12, fontweight='bold')
    ax.text(1, -0.7, "■ Compression (-)", color='#3366ff', fontsize=12, fontweight='bold')
    
    plt.xlim(-0.5, 2.5)
    plt.ylim(-0.8, 1.5)
    return fig

# ==========================================
# 🗂️ เมนูด้านข้าง (Sidebar)
# ==========================================
st.sidebar.title("เมนูนำทาง")
menu = st.sidebar.radio("เลือกหน้าต่าง:", ["🏠 หน้าหลัก (Home)", "📡 แดชบอร์ด (Real-time)", "📚 ทฤษฎี (Theory)"])

st.sidebar.markdown("---")
st.sidebar.subheader("รูปแบบที่เลือก:")
selected_format = st.sidebar.radio("โครงถัก:", ["A", "B", "C"])

# ==========================================
# 🏠 1. หน้าหลัก (Home)
# ==========================================
if menu == "🏠 หน้าหลัก (Home)":
    st.title("🏠 หน้าหลัก (เลือกรูปแบบโครงถัก)")
    st.write("โปรเจกต์เครื่องมือทดสอบและวิเคราะห์โครงสร้างทางวิศวกรรม")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("FormatA.jpg", caption="รูปแบบ A", use_container_width=True)
    with col2:
        st.image("FormatB.jpg", caption="รูปแบบ B", use_container_width=True)
    with col3:
        st.image("FormatC.jpg", caption="รูปแบบ C", use_container_width=True)

# ==========================================
# 📡 2. หน้าแดชบอร์ด (Real-time จาก Firebase)
# ==========================================
elif menu == "📡 แดชบอร์ด (Real-time)":
    st.title(f"📡 แดชบอร์ดอ่านค่าจริง - รูปแบบ {selected_format}")
    
    # ปรับโหมดจำลอง
    simulate = st.checkbox("🧪 โหมดจำลอง (ไม่ใช้เน็ต)", value=False)
    
    placeholder = st.empty()
    FIREBASE_URL = "https://trussproject-3fc34-default-rtdb.asia-southeast1.firebasedatabase.app/truss/data.json"
    
    while True:
        if simulate:
            # ข้อมูลจำลอง
            vals = [1.0, -1.0, 1.5, -2.0, 1.5, -1.0, 1.0]
        else:
            try:
                res = requests.get(FIREBASE_URL)
                data = res.json()
                vals = [data['kg1'], data['kg2'], data['kg3'], data['kg4'], data['kg5'], data['kg6'], data['kg7']]
            except:
                vals = [0]*7
        
        with placeholder.container():
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = draw_truss(selected_format, vals)
                st.pyplot(fig)
            
            with col2:
                st.subheader("📊 ข้อมูลเซนเซอร์ (kg)")
                for i in range(7):
                    st.metric(label=f"Sensor {i+1}", value=f"{vals[i]:.2f}")
                
        time.sleep(1) # อัปเดตทุก 1 วินาที

# ==========================================
# 📚 3. หน้าทฤษฎี (Theory Simulation)
# ==========================================
elif menu == "📚 ทฤษฎี (Theory)":
    st.title(f"📚 จำลองการคำนวณตามทฤษฎี - รูปแบบ {selected_format}")
    st.markdown("จำลองการรับแรงของชิ้นส่วนต่างๆ ตามหลักการวิเคราะห์โครงสร้าง (Method of Joints)")
    
    # Slider เลื่อนน้ำหนัก
    weight = st.slider("⚖️ เลือกระดับน้ำหนักโหลด (kg)", min_value=0.5, max_value=10.0, value=1.0, step=0.1)
    
    # คำนวณค่าทฤษฎี (เอาสัมประสิทธิ์ * น้ำหนักโหลด)
    coeffs = THEORY_COEFFS[selected_format]
    theory_vals = [c * weight for c in coeffs]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # วาดกราฟทฤษฎี
        fig = draw_truss(selected_format, theory_vals)
        st.pyplot(fig)
        
    with col2:
        st.subheader("📝 ตารางแรงตามทฤษฎี")
        df = pd.DataFrame({
            "ชิ้นส่วน (Sensor)": [f"Sensor {i+1}" for i in range(7)],
            "ค่าสัมประสิทธิ์": coeffs,
            f"แรงที่เกิดขึ้น (kg)": [round(v, 2) for v in theory_vals]
        })
        st.dataframe(df, hide_index=True, use_container_width=True)
        st.info("💡 **Tips:** แรงดึง (Tension) จะมีค่าเป็นบวก และแรงอัด (Compression) จะมีค่าเป็นลบ")
