import streamlit as st
from google import genai

# Modern Page Configuration
st.set_page_config(
    page_title="Sweets Portal | Supply Chain",
    page_icon="🍬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom High-End Styling (HD UI / Modern Cards / Soft Shadows)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(180deg, #F8FAFC 0%, #EEF2F6 100%);
    }
    
    /* Header Card */
    .brand-banner {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 24px;
        border-radius: 18px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .brand-title {
        font-size: 26px;
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
                  
