import streamlit as st
import requests
import matplotlib.pyplot as plt
import numpy as np
import time
import os

# ==========================================
# 0. ตั้งค่าฟอนต์ภาษาไทยให้ Matplotlib
# ==========================================
plt.rcParams['font.sans-serif'] = ['Tahoma', 'Loma', 'Garuda', 'FreesiaUPC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False 

# ==========================================
# 1. ตั้งค่าหน้าเว็บ & สร้างความจำ (Session State)
# ==========================================
st.set_page_config(
    page_title="Truss Dashboard",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_URL = "https://trussproject-3fc34-default-rtdb.asia-southeast1.firebasedatabase.app/truss/data.json"

for i in range(1, 8):
    if f'tare_w{i}' not in st.session_state: 
        st.session_state[f'tare_w{i}'] = 0.0
        
if 'selected_truss' not in st.session_state: st.session_state.selected_truss = "รูปแบบ A"
if 'unit' not in st.session_state: st.session_state.unit = "kg"
if 'current_page' not in st.session_state: st.session_state.current_page = "หน้าหลัก"
if 'needs_flush' not in st.session_state: st.session_state.needs_flush = False

# ==========================================
# 2. ธีมและสไตล์ (คลีนๆ)
# ==========================================
PRIMARY = "#2563EB"
CARD_BG = "#FFFFFF"
CARD_BORDER = "#E2E8F0"
TEXT_MAIN = "#1E293B"
TEXT_MUTED = "#64748B"

st.markdown(f"""
<style>
    #MainMenu, footer {{visibility: hidden;}}
    .stApp {{ background-color: #F8FAFC; color: {TEXT_MAIN}; }}
    
    div[data-testid="stRadio"] *, div[data-testid="stCheckbox"] * {{
        color: {TEXT_MAIN} !important;
        font-weight: 600;
    }}
    
    .app-header {{
        display: flex; align-items: center; gap: 14px;
        padding: 20px 26px; margin-bottom: 22px; border-radius: 16px;
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
    }}
    .metric-card {{
        background: {CARD_BG}; border: 1px solid {CARD_BORDER};
        border-radius: 10px; padding: 12px 15px; margin-bottom: 12px;
        position: relative; overflow: hidden;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
    }}
    .metric-card:before {{
        content: ""; position: absolute; left: 0; top: 0; bottom: 0;
        width: 5px; background: var(--bar-color, {PRIMARY});
    }}
    .metric-label {{ color: {TEXT_MUTED}; font-size: 13px; font-weight: 700; margin-bottom: 2px; }}
    .metric-value {{ color: {TEXT_MAIN}; font-size: 22px; font-weight: 800; }}
    .metric-unit {{ color: {TEXT_MUTED}; font-size: 14px; margin-left: 4px; font-weight: normal; }}
    
    div.stButton > button {{
        background: #FFFFFF; color: {TEXT_MAIN}; border: 1px solid {CARD_BORDER};
        border-radius: 8px; font-weight: 700; transition: 0.2s;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. เมนูด้านข้าง (Sidebar)
# ==========================================
with st.sidebar:
    st.markdown("### เมนูนำทาง")
    if st.button("🏠 หน้าหลัก (Home)", use_container_width=True, key="nav_home"):
        st.session_state.current_page = "หน้าหลัก"
        st.rerun()
        
    if st.button("📊 แดชบอร์ด (Dashboard)", use_container_width=True, key="nav_dash"):
        st.session_state.current_page = "แดชบอร์ด"
        st.session_state.needs_flush = True
        st.rerun()

    if st.button("📚 ทฤษฎี (Theory)", use_container_width=True, key="nav_theo"):
        st.session_state.current_page = "ทฤษฎี"
        st.session_state.needs_flush = True
        st.rerun()

    st.markdown("---")
    st.markdown(f"**รูปแบบที่เลือก:**\n🟢 **{st.session_state.selected_truss}**")

# ==========================================
# 4. หน้าหลัก (Home)
# ==========================================
if st.session_state.current_page == "หน้าหลัก":
    st.markdown("""
    <div class="app-header">
        <div>
            <h1 style="margin:0; font-size: 28px; color:#1E293B;">🏠 หน้าหลัก (เลือกรูปแบบโครงถัก)</h1>
            <p style="margin: 4px 0 0 0; color:#64748B;">กรุณาคลิกเลือกรูปแบบโครงถักเพื่อเริ่มทำการทดสอบ</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")
    with col1:
        st.markdown('### รูปแบบ A')
        try: st.image("FormatA.jpg", use_container_width=True)
        except: st.info("รอรูป Format A")
        if st.button("เลือกรูปแบบ A", use_container_width=True, type="primary"):
            st.session_state.selected_truss = "รูปแบบ A"
            st.session_state.current_page = "แดชบอร์ด"
            st.session_state.needs_flush = True
            st.rerun()
            
    with col2:
        st.markdown('### รูปแบบ B')
        try: st.image("FormatB.jpg", use_container_width=True)
        except: st.info("รอรูป Format B")
        if st.button("เลือกรูปแบบ B", use_container_width=True, type="primary"):
            st.session_state.selected_truss = "รูปแบบ B"
            st.session_state.current_page = "แดชบอร์ด"
            st.session_state.needs_flush = True
            st.rerun()

    with col3:
        st.markdown('### รูปแบบ C')
        try: st.image("FormatC.jpg", use_container_width=True)
        except: st.info("รอรูป Format C")
        if st.button("เลือกรูปแบบ C", use_container_width=True, type="primary"):
            st.session_state.selected_truss = "รูปแบบ C"
            st.session_state.current_page = "แดชบอร์ด"
            st.session_state.needs_flush = True
            st.rerun()

# ==========================================
# 5. หน้าแดชบอร์ด (Dashboard)
# ==========================================
elif st.session_state.current_page == "แดชบอร์ด":
    if st.session_state.needs_flush:
        st.session_state.needs_flush = False
        time.sleep(0.05)
        st.rerun()
        
    st.markdown('<h3 style="margin-top: 0;">🔄 สลับรูปแบบโครงถัก</h3>', unsafe_allow_html=True)
    
    t_col1, t_col2, t_col3 = st.columns(3)
    
    with t_col1:
        try: st.image("FormatA.jpg", use_container_width=True)
        except: pass
        if st.button("📐 เลือกรูปแบบ A", use_container_width=True, type="primary" if st.session_state.selected_truss == "รูปแบบ A" else "secondary", key="btn_dash_a"):
            st.session_state.selected_truss = "รูปแบบ A"
            st.rerun()
            
    with t_col2:
        try: st.image("FormatB.jpg", use_container_width=True)
        except: pass
        if st.button("📐 เลือกรูปแบบ B", use_container_width=True, type="primary" if st.session_state.selected_truss == "รูปแบบ B" else "secondary", key="btn_dash_b"):
            st.session_state.selected_truss = "รูปแบบ B"
            st.rerun()
            
    with t_col3:
        try: st.image("FormatC.jpg", use_container_width=True)
        except: pass
        if st.button("📐 เลือกรูปแบบ C", use_container_width=True, type="primary" if st.session_state.selected_truss == "รูปแบบ C" else "secondary", key="btn_dash_c"):
            st.session_state.selected_truss = "รูปแบบ C"
            st.rerun()
            
    st.markdown("---") 

    left_col, right_col = st.columns([1.2, 2.2], gap="large")

    # ---------------- ฝั่งซ้าย: แผงควบคุม & การ์ด ----------------
    with left_col:
        st.write("") 

        ctrl1, ctrl2 = st.columns([1, 1])
        with ctrl1:
            if st.button("⚖️ Tare (เซ็ตศูนย์)", use_container_width=True, type="primary"):
                try:
                    resp = requests.get(DATA_URL, timeout=3.0) 
                    d = resp.json() if resp.status_code == 200 else {}
                    
                    if d is None:
                        d = {}
                        
                    if d:
                        for i in range(1, 8):
                            st.session_state[f'tare_w{i}'] = d.get(f"kg{i}", 0.0)
                except Exception as e: 
                    st.error("เชื่อมต่อ Cloud เพื่อ Tare ไม่ได้")
        
        with ctrl2:
            st.session_state.unit = st.radio("เลือกหน่วย:", ["kg", "N"], horizontal=True)
        
        st.write("") 

        c1, c2 = st.columns(2)
        metric_spots = []
        for i in range(7):
            if i % 2 == 0: metric_spots.append(c1.empty())
            else: metric_spots.append(c2.empty())

    # ---------------- ฝั่งขวา: พื้นที่วาดกราฟ ----------------
    with right_col:
        plot_spot = st.empty()

    def render_metric(container, label, value, bar_color):
        container.markdown(f"""
        <div class="metric-card" style="--bar-color:{bar_color}; padding: 10px;">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value:.2f}<span class="metric-unit">{st.session_state.unit}</span></div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.selected_truss == "รูปแบบ A":
        nodes = np.array([[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [2.0, 0.0], [2.0, -0.8]])
        members = np.array([[0, 3], [2, 3], [0, 2], [1, 2], [3, 4], [2, 4], [4, 5]])
    elif st.session_state.selected_truss == "รูปแบบ B": 
        nodes = np.array([[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [2.0, 0.0], [2.0, -0.8]])
        members = np.array([[0, 3], [2, 3], [1, 3], [1, 2], [3, 4], [2, 4], [4, 5]])
    else: 
        nodes = np.array([[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [2.0, 1.0], [2.0, 0.2]])
        members = np.array([[0, 3], [2, 3], [1, 3], [1, 2], [2, 4], [3, 4], [4, 5]])

    x_min, x_max = nodes[:, 0].min(), nodes[:, 0].max()
    y_min, y_max = nodes[:, 1].min(), nodes[:, 1].max()

    # ลูปอัปเดตกราฟ
    while True:
        try:
            response = requests.get(DATA_URL, timeout=1.0)
            got_data = response.status_code == 200
            if got_data: 
                data = response.json()
                if data is None:
                    data = {}

            if got_data:
                w = []
                for i in range(1, 8):
                    val = data.get(f"kg{i}", 0.0) - st.session_state[f'tare_w{i}']
                    if st.session_state.unit == "N":
                        val = val * 9.81
                    w.append(val)

                colors = ["#4338CA", "#0D9488", "#F59E0B", "#E11D48", "#7C3AED", "#2563EB", "#059669"]
                for i in range(7):
                    render_metric(metric_spots[i], f"Sensor {i+1}", w[i], colors[i])

                fig, ax = plt.subplots(figsize=(8, 6))
                
                fig.patch.set_facecolor('#FFFFFF')
                ax.set_facecolor('#FFFFFF')
                
                ax.set_xlim(x_min - 0.4, x_max + 0.4)
                ax.set_ylim(y_min - 0.4, y_max + 0.4)

                for idx_m, (start_node, end_node) in enumerate(members):
                    val = w[idx_m]
                    
                    if val > 0.05:
                        edge_c = "#EF4444"
                        arrow_c = "#EF4444"
                    elif val < -0.05:
                        edge_c = "#3B82F6"
                        arrow_c = "#3B82F6"
                    else:
                        edge_c = "#94A3B8"
                        arrow_c = "#CBD5E1"

                    if idx_m == 6:
                        ax.annotate("", xy=(nodes[end_node, 0], nodes[end_node, 1]), 
                                    xytext=(nodes[start_node, 0], nodes[start_node, 1]),
                                    arrowprops=dict(arrowstyle="-|>", lw=6, color=arrow_c, mutation_scale=25), zorder=1)
                    else:
                        ax.plot([nodes[start_node, 0], nodes[end_node, 0]], [nodes[start_node, 1], nodes[end_node, 1]], c=colors[idx_m], lw=6, zorder=1)

                    mid_x, mid_y = (nodes[start_node, 0] + nodes[end_node, 0]) / 2, (nodes[start_node, 1] + nodes[end_node, 1]) / 2
                    
                    ax.text(mid_x, mid_y, f"{val:.2f} {st.session_state.unit}", 
                            color="#1E293B", fontsize=11, fontweight='bold', ha='center', va='center', zorder=4,
                            bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFFFF', edgecolor=edge_c, linewidth=2.0))

                ax.scatter(nodes[:-1, 0], nodes[:-1, 1], s=120, c="#3B82F6", edgecolors="#FFFFFF", linewidths=2, zorder=3)

                ax.set_aspect('equal')
                ax.axis('off')

                ax.text(x_min, y_min - 0.3, "(+) แรงดึง (Tension)", color="#EF4444", fontsize=10, fontweight='bold')
                ax.text(x_min + 1.1, y_min - 0.3, "(-) แรงอัด (Compression)", color="#3B82F6", fontsize=10, fontweight='bold')

                plot_spot.pyplot(fig, use_container_width=True)
                plt.close(fig)

        except Exception as e:
            plot_spot.error(f"เกิดข้อผิดพลาดในการแสดงกราฟ: {e}")
            pass

        time.sleep(0.15)


# ==========================================
# 6. หน้าทฤษฎี (Theory) 
# ==========================================
elif st.session_state.current_page == "ทฤษฎี":
    st.markdown("""
    <div class="app-header">
        <div>
            <h1 style="margin:0; font-size: 28px; color:#1E293B;">📚 หน้าจำลองทฤษฎี (Theory)</h1>
            <p style="margin: 4px 0 0 0; color:#64748B;">จำลองการรับแรงของชิ้นส่วนต่างๆ ตามหลักการวิเคราะห์โครงสร้าง</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- ปุ่มเลือกรูปแบบเหมือนหน้าแดชบอร์ด ---
    t_col1, t_col2, t_col3 = st.columns(3)
    with t_col1:
        if st.button("📐 เลือกรูปแบบ A", use_container_width=True, type="primary" if st.session_state.selected_truss == "รูปแบบ A" else "secondary", key="btn_theo_a"):
            st.session_state.selected_truss = "รูปแบบ A"; st.rerun()
    with t_col2:
        if st.button("📐 เลือกรูปแบบ B", use_container_width=True, type="primary" if st.session_state.selected_truss == "รูปแบบ B" else "secondary", key="btn_theo_b"):
            st.session_state.selected_truss = "รูปแบบ B"; st.rerun()
    with t_col3:
        if st.button("📐 เลือกรูปแบบ C", use_container_width=True, type="primary" if st.session_state.selected_truss == "รูปแบบ C" else "secondary", key="btn_theo_c"):
            st.session_state.selected_truss = "รูปแบบ C"; st.rerun()
            
    st.markdown("---")
    
    # --- แผงควบคุมเลื่อนน้ำหนัก ---
    ctrl_col1, ctrl_col2 = st.columns([2, 1])
    with ctrl_col1:
        weight_input = st.slider("⚖️ เลือกระดับน้ำหนักโหลด (kg)", min_value=1.0, max_value=5.0, value=1.0, step=1.0)
    with ctrl_col2:
        unit_theo = st.radio("เลือกหน่วยวัดทฤษฎี:", ["kg", "N"], horizontal=True, key="unit_theo")
        
    multiplier = 9.81 if unit_theo == "N" else 1.0
    
    # --- ข้อมูลสัมประสิทธิ์ (Coefficient) ---
    THEORY_COEFFS = {
        "รูปแบบ A": [1.00, -1.00, 1.41, -2.00, 1.41, -1.00, 1.00],
        "รูปแบบ B": [2.00, 0.00, -1.41, -1.00, 1.41, -1.00, 1.00],
        "รูปแบบ C": [2.00, 1.00, -1.41, -1.00, -1.41, 1.00, 1.00]
    }
    
    # คำนวณตามสูตร
    coeffs = THEORY_COEFFS[st.session_state.selected_truss]
    theory_w = [c * weight_input * multiplier for c in coeffs]
    
    # --- แบ่งหน้าจอแสดงผลตารางและกราฟ ---
    left_col, right_col = st.columns([1.2, 2.2], gap="large")
    
    with left_col:
        # เหลือไว้แค่คำอธิบายทิศทางของแรง (เอาตารางออกแล้ว)
        st.info("💡 **แรงดึง (Tension)** จะมีค่าเป็นบวก\n\n**แรงอัด (Compression)** จะมีค่าเป็นลบ")
        
    with right_col:
        # ดึงโหนดเหมือนหน้าแดชบอร์ด
        if st.session_state.selected_truss == "รูปแบบ A":
            nodes = np.array([[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [2.0, 0.0], [2.0, -0.8]])
            members = np.array([[0, 3], [2, 3], [0, 2], [1, 2], [3, 4], [2, 4], [4, 5]])
        elif st.session_state.selected_truss == "รูปแบบ B": 
            nodes = np.array([[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [2.0, 0.0], [2.0, -0.8]])
            members = np.array([[0, 3], [2, 3], [1, 3], [1, 2], [3, 4], [2, 4], [4, 5]])
        else: 
            nodes = np.array([[0.0, 1.0], [0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [2.0, 1.0], [2.0, 0.2]])
            members = np.array([[0, 3], [2, 3], [1, 3], [1, 2], [2, 4], [3, 4], [4, 5]])

        x_min, x_max = nodes[:, 0].min(), nodes[:, 0].max()
        y_min, y_max = nodes[:, 1].min(), nodes[:, 1].max()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')
        ax.set_xlim(x_min - 0.4, x_max + 0.4)
        ax.set_ylim(y_min - 0.4, y_max + 0.4)

        colors = ["#4338CA", "#0D9488", "#F59E0B", "#E11D48", "#7C3AED", "#2563EB", "#059669"]

        for idx_m, (start_node, end_node) in enumerate(members):
            val = theory_w[idx_m]
            
            if val > 0.05:
                edge_c, arrow_c = "#EF4444", "#EF4444"
            elif val < -0.05:
                edge_c, arrow_c = "#3B82F6", "#3B82F6"
            else:
                edge_c, arrow_c = "#94A3B8", "#CBD5E1"

            if idx_m == 6:
                ax.annotate("", xy=(nodes[end_node, 0], nodes[end_node, 1]), 
                            xytext=(nodes[start_node, 0], nodes[start_node, 1]),
                            arrowprops=dict(arrowstyle="-|>", lw=6, color=arrow_c, mutation_scale=25), zorder=1)
            else:
                ax.plot([nodes[start_node, 0], nodes[end_node, 0]], [nodes[start_node, 1], nodes[end_node, 1]], c=colors[idx_m], lw=6, zorder=1)

            mid_x, mid_y = (nodes[start_node, 0] + nodes[end_node, 0]) / 2, (nodes[start_node, 1] + nodes[end_node, 1]) / 2
            ax.text(mid_x, mid_y, f"{val:.2f} {unit_theo}", 
                    color="#1E293B", fontsize=11, fontweight='bold', ha='center', va='center', zorder=4,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFFFFF', edgecolor=edge_c, linewidth=2.0))

        ax.scatter(nodes[:-1, 0], nodes[:-1, 1], s=120, c="#3B82F6", edgecolors="#FFFFFF", linewidths=2, zorder=3)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.text(x_min, y_min - 0.3, "(+) แรงดึง (Tension)", color="#EF4444", fontsize=10, fontweight='bold')
        ax.text(x_min + 1.1, y_min - 0.3, "(-) แรงอัด (Compression)", color="#3B82F6", fontsize=10, fontweight='bold')

        st.pyplot(fig, use_container_width=True)
