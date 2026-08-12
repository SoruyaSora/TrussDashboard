import streamlit as st
import requests
import matplotlib.pyplot as plt
import time

# ==========================================
# ⚙️ ตั้งค่าหน้าเว็บ
# ==========================================
st.set_page_config(page_title="Truss Dashboard", layout="wide")

# ==========================================
# 🎨 ฟังก์ชันวาดรูปโครงถัก
# ==========================================
def draw_truss(format_type, values, unit_label="kg"):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')
    ax.set_aspect('equal') 
    
    # ดึงเฉพาะตัวอักษร A, B, C
    fmt = format_type[-1] 
    
    if fmt == "A":
        nodes = {0: (0,0), 1: (1,0), 4: (2,0), 3: (0,1), 2: (1,1)}
        lines = {1: (3,2), 2: (2,1), 3: (3,1), 4: (0,1), 5: (2,4), 6: (1,4)}
        load_node = 4
    elif fmt == "B":
        nodes = {10: (0,0), 12: (1,0), 14: (2,0), 11: (0,1), 13: (1,1)}
        lines = {1: (11,13), 2: (13,12), 3: (10,13), 4: (10,12), 5: (13,14), 6: (12,14)}
        load_node = 14
    elif fmt == "C":
        nodes = {5: (0,0), 7: (1,0), 6: (0,1), 8: (1,1), 9: (2,1)}
        lines = {1: (6,8), 2: (8,7), 3: (5,8), 4: (5,7), 5: (7,9), 6: (8,9)}
        load_node = 9

    # วาดเส้นและข้อความ
    for i, (n1, n2) in lines.items():
        val = values[i-1]
        color = '#ff3333' if val > 0.05 else '#3366ff' if val < -0.05 else '#999999'
        x = [nodes[n1][0], nodes[n2][0]]
        y = [nodes[n1][1], nodes[n2][1]]
        ax.plot(x, y, color=color, linewidth=5, zorder=1)
        
        mid_x, mid_y = sum(x)/2, sum(y)/2
        ax.text(mid_x, mid_y, f"{val:.2f} {unit_label}", ha='center', va='center', 
                bbox=dict(facecolor='white', edgecolor=color, boxstyle='round,pad=0.3'),
                fontsize=10, zorder=3)
    
    # ลูกศรโหลด
    val7 = values[6]
    lx, ly = nodes[load_node]
    ax.arrow(lx, ly, 0, -0.35, head_width=0.08, head_length=0.1, fc='#ff3333', ec='#ff3333', linewidth=3, zorder=2)
    ax.text(lx, ly - 0.25, f"{val7:.2f} {unit_label}", ha='center', va='center',
            bbox=dict(facecolor='white', edgecolor='#ff3333', boxstyle='round,pad=0.3'), zorder=3)
    
    for n, (x, y) in nodes.items():
        ax.plot(x, y, 'o', color='white', markeredgecolor='#444444', markersize=10, markeredgewidth=2, zorder=4)
        
    ax.text(0, -0.7, "■ Tension (+)", color='#ff3333', fontsize=12, fontweight='bold')
    ax.text(1, -0.7, "■ Compression (-)", color='#3366ff', fontsize=12, fontweight='bold')
    
    plt.xlim(-0.5, 2.5)
    plt.ylim(-0.8, 1.5)
    return fig

# ==========================================
# 🗂️ เมนูด้านข้าง
# ==========================================
st.sidebar.title("เมนูนำทาง")
menu = st.sidebar.radio("", ["🏠 หน้าหลัก (Home)", "📊 แดชบอร์ด (Dashboard)"])

st.sidebar.markdown("---")
st.sidebar.subheader("รูปแบบที่เลือก:")
selected_format = st.sidebar.radio("", ["รูปแบบ A", "รูปแบบ B", "รูปแบบ C"])

# ==========================================
# 🏠 1. หน้าหลัก 
# ==========================================
if menu == "🏠 หน้าหลัก (Home)":
    st.title("🏠 หน้าหลัก (เลือกรูปแบบโครงถัก)")
    st.write("กรุณาคลิกเลือกรูปแบบโครงถักเพื่อเริ่มทำการทดสอบ")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.image("FormatA.jpg", caption="เลือกรูปแบบ A", use_container_width=True)
    with col2:
        st.image("FormatB.jpg", caption="เลือกรูปแบบ B", use_container_width=True)
    with col3:
        st.image("FormatC.jpg", caption="เลือกรูปแบบ C", use_container_width=True)

# ==========================================
# 📊 2. หน้าแดชบอร์ด
# ==========================================
elif menu == "📊 แดชบอร์ด (Dashboard)":
    st.title(f"📊 แดชบอร์ด - {selected_format}")
    
    col_sim, col_unit = st.columns(2)
    with col_sim:
        simulate = st.checkbox("🧪 โหมดจำลอง", value=False)
    with col_unit:
        unit = st.radio("📏 เลือกหน่วยวัด:", ["kg", "N", "lbs"], horizontal=True)
        
    multiplier = 1.0
    unit_label = "kg"
    if unit == "N":
        multiplier = 9.81
        unit_label = "N"
    elif unit == "lbs":
        multiplier = 2.2046
        unit_label = "lbs"
    
    placeholder = st.empty()
    FIREBASE_URL = "https://trussproject-3fc34-default-rtdb.asia-southeast1.firebasedatabase.app/truss/data.json"
    
    while True:
        if simulate:
            vals = [1.0, -1.0, 1.5, -2.0, 1.5, -1.0, 1.0]
        else:
            try:
                res = requests.get(FIREBASE_URL)
                data = res.json()
                vals = [data['kg1'], data['kg2'], data['kg3'], data['kg4'], data['kg5'], data['kg6'], data['kg7']]
            except:
                vals = [0]*7
                
        display_vals = [v * multiplier for v in vals]
        
        with placeholder.container():
            fig = draw_truss(selected_format, display_vals, unit_label)
            st.pyplot(fig)
            
            st.markdown("---")
            st.subheader(f"ข้อมูลเซนเซอร์ ({unit_label})")
            
            # โชว์เรียงแนวนอนแบบเดิม
            cols = st.columns(7)
            for i in range(7):
                cols[i].metric(label=f"Sen {i+1}", value=f"{display_vals[i]:.2f}")
                
        time.sleep(1)
