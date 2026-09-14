import streamlit as st
from google import genai
from fpdf import FPDF
import datetime
import urllib.parse
import json
import os

# Page Setup
st.set_page_config(
    page_title="STOCK TRANSFER | Jamal Showaiter",
    page_icon="🍬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Persistent Data File
DB_FILE = "transfers_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_data(data):
    try:
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

# ULTRA HIGH-DEFINITION LUXURY DARK GLASS THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        letter-spacing: -0.2px;
    }
    
    #MainMenu, header, footer, .stDeployButton { 
        visibility: hidden !important; 
        display: none !important; 
    }
    
    /* Deep OLED Background with Ambient Mesh Gradients */
    .stApp {
        background-color: #030712 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(217, 119, 6, 0.08) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.06) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(15, 23, 42, 0.5) 0px, transparent 100%) !important;
        background-attachment: fixed !important;
        color: #F8FAFC !important;
    }

    /* Frosted Glass Top Banner */
    .header-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 22px 20px;
        margin-bottom: 20px;
        box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }
    
    .header-box::after {
        content: '';
        position: absolute;
        top: 0; left: 0; width: 4px; height: 100%;
        background: linear-gradient(180deg, #F59E0B 0%, #D97706 100%);
    }

    .comp-name {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        color: #FBBF24;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }

    .app-title {
        font-size: 26px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin: 0 0 10px 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }

    .branch-tag {
        display: inline-flex;
        align-items: center;
        background: rgba(14, 165, 233, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38BDF8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 30px;
        letter-spacing: 0.5px;
    }

    /* Modern Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 600;
        font-size: 13px;
        padding: 8px 16px;
        border: none !important;
        background: transparent !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.1) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }

    /* Glass Cards */
    .order-card {
        background: rgba(17, 24, 39, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 18px;
        border-radius: 16px;
        margin-bottom: 14px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .order-card:hover {
        border-color: rgba(245, 158, 11, 0.3);
    }

    /* Badges */
    .badge-transit {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.35);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
    }
    
    .badge-received {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        letter-spacing: 0.5px;
    }

    /* Success Banner */
    .success-box {
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.4) 0%, rgba(4, 120, 87, 0.2) 100%);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(52, 211, 153, 0.4);
        border-radius: 16px;
        padding: 18px;
        margin: 16px 0;
        box-shadow: 0 10px 25px -5px rgba(4, 120, 87, 0.3);
    }

    /* Luxury Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        font-size: 14px !important;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3) !important;
    }

    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #F59E0B !important;
        box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.2) !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(251, 191, 36, 0.3) !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        height: 48px !important;
        box-shadow: 0 6px 20px -3px rgba(217, 119, 6, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 25px -3px rgba(217, 119, 6, 0.6) !important;
    }

    .wa-btn {
        display: block;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white !important;
        text-align: center;
        padding: 12px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        font-size: 13px;
        box-shadow: 0 6px 20px -3px rgba(16, 185, 129, 0.35);
        border: 1px solid rgba(52, 211, 153, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# Voucher PDF Generator (Matching Physical Voucher Photo)
def create_voucher_pdf(trx):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    # Cream/Yellow Voucher Paper Tint
    pdf.set_fill_color(254, 252, 235)
    pdf.rect(5, 5, 200, 287, "F")
    
    # Header Details
    pdf.set_xy(10, 10)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(190, 5, "JAMAL SHOWAITER SWEETS Co. W.L.L.", ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(190, 4, "P.O.Box : 1352 - Manama - Kingdom of Bahrain, Tel: 17341735, Fax: 17342252", ln=True, align="C")
    
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 5, "STOCK TRANSFER NOTE", ln=True, align="C")
    
    # Serial No & Date
    pdf.set_xy(10, 26)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.write(5, "No: ")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(220, 38, 38)
    serial_str = f"ST {253600 + trx['id']}"
    pdf.write(5, serial_str)
    
    pdf.set_text_color(20, 20, 20)
    pdf.set_xy(140, 26)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(12, 5, "Date: ")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(38, 5, f" {trx['date_str']}", border="B")
    
    # Locations
    pdf.set_xy(10, 33)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(26, 5, "From Location: ")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(154, 5, f" {trx['from_branch']}", border="B")
    
    pdf.set_xy(10, 40)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(22, 5, "To Location: ")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(158, 5, f" {trx['to_branch']}", border="B")
    
    # Columns
    widths = [10, 18, 74, 14, 22, 22, 30]
    headers = ["S.No.", "Date", "Description", "Qty", "Selling Price", "Unit Price", "Amount (BD)"]
    
    pdf.set_xy(10, 48)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_draw_color(70, 70, 70)
    pdf.set_fill_color(250, 248, 228)
    
    for i in range(len(headers)):
        pdf.cell(widths[i], 7, headers[i], border=1, align="C", fill=True)
    pdf.ln()
    
    # 14 Grid Rows
    items = trx.get("items_list", [])
    row_height = 8
    pdf.set_font("Helvetica", "", 8)
    
    for row_idx in range(14):
        pdf.set_x(10)
        if row_idx < len(items):
            it = items[row_idx]
            pdf.cell(widths[0], row_height, str(row_idx + 1), border=1, align="C")
            pdf.cell(widths[1], row_height, trx['date_str'], border=1, align="C")
            pdf.cell(widths[2], row_height, " " + str(it.get("desc", ""))[:42], border=1, align="L")
            pdf.cell(widths[3], row_height, str(it.get("qty", "")), border=1, align="C")
            pdf.cell(widths[4], row_height, str(it.get("sp", "")), border=1, align="C")
            pdf.cell(widths[5], row_height, str(it.get("up", "")), border=1, align="C")
            pdf.cell(widths[6], row_height, str(it.get("amt", "")), border=1, align="C")
        else:
            for w in widths:
                pdf.cell(w, row_height, "", border=1)
        pdf.ln()
        
    # Total Amount
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(160, 7.5, "Total Amount  ", border=1, align="R")
    pdf.cell(30, 7.5, trx.get("total_amount", ""), border=1, align="C")
    pdf.ln(12)
    
    # Signatures
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(20, 5, "Issued by: ")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(65, 5, f" {trx['sender_name']}", border="B")
    
    pdf.set_x(115)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(24, 5, "Approved by: ")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(61, 5, f" {trx.get('receiver_name', '')}", border="B")
    
    return bytes(pdf.output())

# Branch Configuration
BRANCHES = [
    "KSSFCT-01",
    "KSSF-01",
    "KSMQ-01",
    "KSMQ-02",
    "KSAV-01",
    "JSSF-02"
]

query_params = st.query_params
selected_branch = BRANCHES[0]

if "b" in query_params:
    val = query_params["b"].strip().upper()
    if val in BRANCHES:
        selected_branch = val

# Glassmorphic Top Brand Header
st.markdown(f"""
<div class="header-box">
    <div class="comp-name">JAMAL SHOWAITER SWEETS CO. W.L.L.</div>
    <div class="app-title">STOCK TRANSFER</div>
    <div class="branch-tag">⚡ TERMINAL: {selected_branch}</div>
</div>
""", unsafe_allow_html=True)

if "b" not in query_params:
    new_branch = st.sidebar.selectbox("Active Branch:", BRANCHES, index=BRANCHES.index(selected_branch))
    if new_branch != selected_branch:
        st.query_params["b"] = new_branch
        st.rerun()

tab_dispatch, tab_inbox, tab_history = st.tabs([
    "📤 Dispatch Stock", 
    "📥 Incoming Stock", 
    "📜 Branch History"
])

api_key = st.secrets.get("GEMINI_API_KEY", "")

# 1. DISPATCH TAB
with tab_dispatch:
    st.markdown("##### 📤 Initiate Stock Requisition")
    other_branches = [b for b in BRANCHES if b != selected_branch]
    to_loc = st.selectbox("Destination Location:", other_branches)
    issuer = st.text_input("Issued by (Staff Signature):", placeholder="Your Name")
    items_input = st.text_area(
        "Manifest Details (Items & Qty):", 
        placeholder="e.g.:\nHalwa Red King - 10 kg\nMixed Baklava VIP - 5 boxes\nKaju Katli - 2 kg",
        height=120
    )
    
    if st.button("🚀 Issue Stock Transfer Note", use_container_width=True, type="primary"):
        if not issuer.strip():
            st.warning("Staff signature required in 'Issued by'.")
        elif not items_input.strip():
            st.warning("Please specify the items to transfer.")
        else:
            with st.spinner("Encrypting & Formatting Voucher..."):
                parsed_list = []
                if api_key:
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = (
                            "Extract items to JSON array with fields 'desc' and 'qty'. Example: "
                            '[{"desc": "Halwa Red", "qty": "10 kg", "sp": "", "up": "", "amt": ""}]. '
                            'Only output raw JSON without markdown:\n' + items_input
                        )
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        clean_text = res.text.strip().replace("```json", "").replace("
                        
