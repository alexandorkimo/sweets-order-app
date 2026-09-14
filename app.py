import streamlit as st
from google import genai

# Page Configuration
st.set_page_config(
    page_title="Sweets Portal AI | Quantum Core",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom High-End Cyberpunk / Dark 3D Animated Style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        color: #E2E8F0;
    }
    
    /* OLED Pitch Black Background with Subtle Grid Pattern */
    .stApp {
        background-color: #030712;
        background-image: 
            radial-gradient(at 50% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 60%),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 100% 100%, 35px 35px, 35px 35px;
    }

    /* 3D Rotating Holographic Reactor Animation */
    .hologram-stage {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 110px;
        perspective: 900px;
        margin: 10px 0 20px 0;
    }
    
    .cube-container {
        width: 60px;
        height: 60px;
        transform-style: preserve-3d;
        animation: spin3D 8s infinite linear;
    }
    
    .cube-face {
        position: absolute;
        width: 60px;
        height: 60px;
        background: rgba(14, 165, 233, 0.12);
        border: 1.5px solid #38BDF8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5), inset 0 0 10px rgba(56, 189, 248, 0.3);
    }
    
    .face-front  { transform: rotateY(0deg) translateZ(30px); }
    .face-back   { transform: rotateY(180deg) translateZ(30px); }
    .face-right  { transform: rotateY(90deg) translateZ(30px); }
    .face-left   { transform: rotateY(-90deg) translateZ(30px); }
    .face-top    { transform: rotateX(90deg) translateZ(30px); }
    .face-bottom { transform: rotateX(-90deg) translateZ(30px); }
    
    @keyframes spin3D {
        0% { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg); }
        100% { transform: rotateX(360deg) rotateY(360deg) rotateZ(360deg); }
    }

    /* Banner Card with Neon Glow Border */
    .brand-banner {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(14px);
        padding: 22px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 0 30px rgba(14, 165, 233, 0.15);
        margin-bottom: 24px;
    }
    
    .brand-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #FFFFFF;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
        margin: 0;
    }
    
    .brand-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #38BDF8;
        margin-top: 6px;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* Glassmorphism Dark Order Card */
    .order-card {
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.6);
    }
    
    .order-card:hover {
        border-color: rgba(56, 189, 248, 0.4);
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-pending { 
        background: rgba(245, 158, 11, 0.15); 
        color: #FBBF24; 
        border: 1px solid rgba(245, 158, 11, 0.4);
        box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
    }
    .badge-progress { 
        background: rgba(99, 102, 241, 0.15); 
        color: #818CF8; 
        border: 1px solid rgba(99, 102, 241, 0.4);
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.2);
    }
    .badge-ready { 
        background: rgba(34, 197, 94, 0.15); 
        color: #4ADE80; 
        border: 1px solid rgba(34, 197, 94, 0.4);
        box-shadow: 0 0 10px rgba(34, 197, 94, 0.2);
    }

    /* Input & Button Styles */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
    }
    .stButton>button {
        border-radius: 12px;
        font-weight: 700;
        background: linear-gradient(135deg, #0284C7 0%, #0369A1 100%);
        color: #FFFFFF;
        border: 1px solid rgba(56, 189, 248, 0.5);
        box-shadow: 0 0 15px rgba(2, 132, 199, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# API Key Config
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

if "orders" not in st.session_state:
    st.session_state.orders = []

# 3D Rotating Holographic Reactor UI
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

# Main Branding Header
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
        placeholder="e.g., 10kg Special Halwa, 20 boxes Mixed Baklava, 5kg Premium Peda for early morning dispatch...",
        height=130
    )
    
    if st.button("⚡ TRANSMIT TO CENTRAL FACTORY", use_container_width=True):
        if not api_key:
            st.error("API Key missing! Please configure GEMINI_API_KEY in Streamlit Secrets.")
        elif not incharge.strip():
            st.warning("Dispatcher Manager identity required.")
        elif not order_raw.strip():
            st.warning("Order details cannot be empty.")
        else:
            with st.spinner("Quantum AI Parsing Payload..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        "You are an automated logistics parser for a sweets production unit. "
                        "Parse this shop order into a clean itemized checklist with quantities, "
                        "units, and any delivery notes. Format with neat markdown bullets:\n\n" + order_raw
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
                    st.success(f"Transmission #{new_order['id']} Confirmed for {branch}!")
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
                    <div style="font-size: 12px; color: #94A3B8; margin-bottom: 12px; font-family: 'JetBrains Mono';">
                        Authorized: <b>{order.get('incharge')}</b>
                    </div>
                    <div style="background: rgba(3, 7, 18, 0.7); border-radius: 10px; padding: 14px; margin-bottom: 12px; font-size: 13px; border: 1px solid rgba(255, 255, 255, 0.08); color: #F1F5F9;">
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
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #F8FAFC;
    }
    .brand-subtitle {
        font-size: 13px;
        color: #94A3B8;
        margin-top: 4px;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    /* Modern Order Card */
    .order-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.03);
    }
    
    .badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-pending { background-color: #FEF3C7; color: #D97706; }
    .badge-progress { background-color: #E0E7FF; color: #4338CA; }
    .badge-ready { background-color: #DCFCE7; color: #15803D; }

    /* Button adjustments */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        padding: 10px 18px;
        border: none;
        transition: all 0.2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# API Key Config
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

if "orders" not in st.session_state:
    st.session_state.orders = []

# Top Branding Banner
st.markdown("""
<div class="brand-banner">
    <h1 class="brand-title">🍬 Sweets Supply Hub</h1>
    <div class="brand-subtitle">Branch Dispatch & Production Network</div>
</div>
""", unsafe_allow_html=True)

# Role Navigator
role = st.radio("Access Portal As:", ["🏪 Branch Store", "🏭 Central Factory"], horizontal=True)
st.write("")

# Branches List (Edit with your real branch names)
BRANCHES = ["Manama Branch", "Riffa Branch", "Muharraq Branch", "Hamad Town Branch"]

if role == "🏪 Branch Store":
    st.markdown("### 📝 New Factory Requisition")
    
    # Check for URL branch parameters (e.g., ?branch=Manama+Branch)
    query_params = st.query_params
    default_branch_idx = 0
    if "branch" in query_params and query_params["branch"] in BRANCHES:
        default_branch_idx = BRANCHES.index(query_params["branch"])

    col1, col2 = st.columns(2)
    with col1:
        branch = st.selectbox("Dispatch From Branch:", BRANCHES, index=default_branch_idx)
    with col2:
        incharge = st.text_input("Requested By (Manager):", placeholder="Name / Staff ID")

    order_raw = st.text_area(
        "Requisition Items:", 
        placeholder="Type naturally (e.g., 10kg Special Halwa, 25 boxes Mixed Ladoo, 5kg Kaju Katli for tomorrow morning...)",
        height=130
    )
    
    if st.button("🚀 Dispatch Requisition to Factory", use_container_width=True, type="primary"):
        if not api_key:
            st.error("API Key missing! Please configure GEMINI_API_KEY in Secrets.")
        elif not incharge.strip():
            st.warning("Please specify the In-charge Manager name.")
        elif not order_raw.strip():
            st.warning("Requisition items cannot be empty.")
        else:
            with st.spinner("Processing order specifications..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        "You are an inventory logistics assistant for a premium sweets company. "
                        "Parse this shop requisition into a structured, itemized checklist with quantities, "
                        "units, and any delivery notes clearly specified. Use clean markdown formatting:\n\n" + order_raw
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
                    st.success(f"Requisition #{new_order['id']} logged successfully for {branch}!")
                except Exception as e:
                    st.error(f"Failed to generate requisition: {e}")

elif role == "🏭 Central Factory":
    st.markdown("### 🏭 Production Floor Queue")
    
    if not st.session_state.orders:
        st.info("No active production requisitions found.")
    else:
        filter_b = st.selectbox("Filter Orders by Branch:", ["All Locations"] + BRANCHES)
        
        for order in reversed(st.session_state.orders):
            if filter_b != "All Locations" and order.get("branch") != filter_b:
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
                        <span style="font-weight: 700; font-size: 16px; color: #0F172A;">
                            📍 {order.get('branch')} (Req #{order['id']})
                        </span>
                        <span class="badge {badge_class}">{status}</span>
                    </div>
                    <div style="font-size: 13px; color: #64748B; margin-bottom: 12px;">
                        Manager: <b>{order.get('incharge')}</b>
                    </div>
                    <div style="background: #F8FAFC; border-radius: 8px; padding: 12px; margin-bottom: 10px; font-size: 14px; border: 1px solid #EDF2F7;">
                        {order['parsed']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2 = st.columns(2)
                if c1.button("👨‍🍳 Start Batch", key=f"btn_prog_{order['id']}", use_container_width=True):
                    order['status'] = "IN PROGRESS"
                    st.rerun()
                if c2.button("🚚 Dispatch Ready", key=f"btn_rdy_{order['id']}", use_container_width=True):
                    order['status'] = "READY FOR DISPATCH"
                    st.rerun()
                st.write("")
            with st.spinner("AI ഓർഡർ പരിശോധിക്കുന്നു..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        "Convert the following shop order into a clean, itemized checklist with quantities, units, and special notes. "
                        "Keep it short and clear:\n\n" + order_input
                    )
                    response = client.models.generate_content(
    model='gemini-3.6-flash',
    contents=prompt
)


                    
                    new_order = {
                        "id": len(st.session_state.orders) + 1,
                        "raw": order_input,
                        "parsed": response.text,
                        "status": "⏳ Pending"
                    }
                    st.session_state.orders.append(new_order)
                    st.success(f"ഓർഡർ #{new_order['id']} ഫാക്ടറിയിലേക്ക് അയച്ചു!")
                except Exception as e:
                    st.error(f"Error: {e}")

elif role == "🏭 Factory":
    st.subheader("ഫാക്ടറി ഓർഡർ കൺട്രോൾ")
    
    if not st.session_state.orders:
        st.info("പുതിയ ഓർഡറുകൾ ഒന്നും വന്നിട്ടില്ല.")
    else:
        for order in reversed(st.session_state.orders):
            with st.expander(f"Order #{order['id']} — {order['status']}", expanded=True):
                st.markdown(f"**Items Required:**\n{order['parsed']}")
                st.caption(f"Original Text: {order['raw']}")
                
                col1, col2 = st.columns(2)
                if col1.button("✅ Accept", key=f"acc_{order['id']}", use_container_width=True):
                    order['status'] = "👨‍🍳 In Progress"
                    st.rerun()
                if col2.button("📦 Ready", key=f"rdy_{order['id']}", use_container_width=True):
                    order['status'] = "🚚 Ready for Delivery"
                    st.rerun()
                  
