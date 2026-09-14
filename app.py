import streamlit as st
from google import genai

st.set_page_config(
    page_title="Sweets Portal AI",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom High-End Cyberpunk / Dark 3D Animated Style
custom_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: #E2E8F0;
    }
    
    .stApp {
        background-color: #030712;
        background-image: 
            radial-gradient(at 50% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 60%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 35px 35px, 35px 35px;
    }

    .hologram-stage {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
        perspective: 900px;
        margin: 10px 0 20px 0;
    }
    
    .cube-container {
        width: 50px;
        height: 50px;
        transform-style: preserve-3d;
        animation: spin3D 8s infinite linear;
    }
    
    .cube-face {
        position: absolute;
        width: 50px;
        height: 50px;
        background: rgba(14, 165, 233, 0.12);
        border: 1.5px solid #38BDF8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5), inset 0 0 10px rgba(56, 189, 248, 0.3);
    }
    
    .face-front  { transform: rotateY(0deg) translateZ(25px); }
    .face-back   { transform: rotateY(180deg) translateZ(25px); }
    .face-right  { transform: rotateY(90deg) translateZ(25px); }
    .face-left   { transform: rotateY(-90deg) translateZ(25px); }
    .face-top    { transform: rotateX(90deg) translateZ(25px); }
    .face-bottom { transform: rotateX(-90deg) translateZ(25px); }
    
    @keyframes spin3D {
        0% { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg); }
        100% { transform: rotateX(360deg) rotateY(360deg) rotateZ(360deg); }
    }

    .brand-banner {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(14px);
        padding: 20px;
        border-radius: 18px;
        text-align: center;
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 0 25px rgba(14, 165, 233, 0.15);
        margin-bottom: 20px;
    }
    
    .brand-title {
        font-size: 22px;
        font-weight: 700;
        color: #FFFFFF;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
        margin: 0;
    }
    
    .brand-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #38BDF8;
        margin-top: 5px;
        letter-spacing: 2px;
    }

    .order-card {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-pending { 
        background: rgba(245, 158, 11, 0.15); 
        color: #FBBF24; 
        border: 1px solid rgba(245, 158, 11, 0.4);
    }
    .badge-progress { 
        background: rgba(99, 102, 241, 0.15); 
        color: #818CF8; 
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    .badge-ready { 
        background: rgba(34, 197, 94, 0.15); 
        color: #4ADE80; 
        border: 1px solid rgba(34, 197, 94, 0.4);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# API Key Config
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

if "orders" not in st.session_state:
    st.session_state.orders = []

# 3D Animated Hologram Cube
st.markdown("""
<div class="hologram-stage">
    <div class="cube-container">
        <div class="cube-face face-front"></div>
        <div class="cube-face face-back"></div>
        <div class="cube-face face-right"></div>
        <div class="cube-face face-left"></div>
        <div class="cube-face face-top"></div>
        <div class="cube-face face-bottom"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Header Banner
st.markdown("""
<div class="brand-banner">
    <h1 class="brand-title">SWEETS LOGISTICS AI</h1>
    <div class="brand-subtitle">NEURAL DISPATCH & FACTORY GRID</div>
</div>
""", unsafe_allow_html=True)

# Role Switcher
role = st.radio("OPERATIONAL TERMINAL:", ["🏪 BRANCH STORE", "🏭 CENTRAL FACTORY"], horizontal=True)
st.write("")

BRANCHES = ["Manama Branch", "Riffa Branch", "Muharraq Branch", "Hamad Town Branch"]

if role == "🏪 BRANCH STORE":
    st.markdown("##### 📦 NEW REQUISITION TRANSMISSION")
    
    query_params = st.query_params
    default_branch_idx = 0
    if "branch" in query_params and query_params["branch"] in BRANCHES:
        default_branch_idx = BRANCHES.index(query_params["branch"])

    col1, col2 = st.columns(2)
    with col1:
        branch = st.selectbox("Origin Branch:", BRANCHES, index=default_branch_idx)
    with col2:
        incharge = st.text_input("Dispatch Manager:", placeholder="Officer Name")

    order_raw = st.text_area(
        "Requisition Inventory Data:", 
        placeholder="e.g., 10kg Special Halwa, 20 boxes Mixed Baklava, 5kg Premium Peda...",
        height=120
    )
    
    if st.button("⚡ TRANSMIT TO FACTORY", use_container_width=True):
        if not api_key:
            st.error("API Key missing! Add GEMINI_API_KEY in Streamlit Secrets.")
        elif not incharge.strip():
            st.warning("Dispatcher Manager identity required.")
        elif not order_raw.strip():
            st.warning("Order details cannot be empty.")
        else:
            with st.spinner("AI Parsing Payload..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        "You are an automated logistics parser for a sweets factory. "
                        "Parse this shop order into a clean itemized checklist with quantities, "
                        "units, and any delivery notes. Format with clean bullets:\n\n" + order_raw
                    )
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt
                    )
                    
                    new_order = {
                        "id": len(st.session_state.orders) + 1,
                        "branch": branch,
                        "incharge": incharge,
                        "raw": order_raw,
                        "parsed": response.text,
                        "status": "PENDING"
                    }
                    st.session_state.orders.append(new_order)
                    st.success(f"Requisition #{new_order['id']} Confirmed for {branch}!")
                except Exception as e:
                    st.error(f"Transmission Error: {e}")

elif role == "🏭 CENTRAL FACTORY":
    st.markdown("##### ⚙️ PRODUCTION LINE TELEMETRY")
    
    if not st.session_state.orders:
        st.info("No requisitions currently in the queue.")
    else:
        filter_b = st.selectbox("Filter by Node:", ["All Hubs"] + BRANCHES)
        
        for order in reversed(st.session_state.orders):
            if filter_b != "All Hubs" and order.get("branch") != filter_b:
                continue
                
            status = order.get("status", "PENDING")
            badge_class = "badge-pending"
            if "PROGRESS" in status:
                badge_class = "badge-progress"
            elif "READY" in status:
                badge_class = "badge-ready"
                
            with st.container():
                st.markdown(f"""
                <div class="order-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                        <span style="font-weight: 700; font-size: 15px; color: #38BDF8;">
                            📍 {order.get('branch')} (Req #{order['id']})
                        </span>
                        <span class="badge {badge_class}">{status}</span>
                    </div>
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 10px; font-family: 'JetBrains Mono';">
                        Authorized: <b>{order.get('incharge')}</b>
                    </div>
                    <div style="background: rgba(3, 7, 18, 0.7); border-radius: 8px; padding: 12px; margin-bottom: 10px; font-size: 13px; border: 1px solid rgba(255, 255, 255, 0.08); color: #F1F5F9;">
                        {order['parsed']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                if c1.button("⚡ Process Batch", key=f"btn_prog_{order['id']}", use_container_width=True):
                    order['status'] = "IN PROGRESS"
                    st.rerun()
                if c2.button("🚚 Dispatch Unit", key=f"btn_rdy_{order['id']}", use_container_width=True):
                    order['status'] = "READY FOR DISPATCH"
                    st.rerun()
                st.write("")
                
