import streamlit as st
from google import genai
from fpdf import FPDF
import datetime
import urllib.parse
import json
import os
import re

st.set_page_config(
    page_title="STOCK TRANSFER | Jamal Showaiter",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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

def parse_items_manual(text):
    parsed = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines:
        match = re.search(r"^(.*?)(?:\s*[-:]?\s*)(\d+(?:\.\d+)?\s*(?:kg|boxes|trays|pcs|pkts|nos)?)$", line, re.IGNORECASE)
        if match:
            desc = match.group(1).strip(" -:")
            qty = match.group(2).strip()
        else:
            desc = line
            qty = "-"
        parsed.append({
            "desc": desc if desc else line,
            "qty": qty,
            "sp": "",
            "up": "",
            "amt": ""
        })
    return parsed

# ULTRA-HD 3D GLASS UI STYLING & PROFESSIONAL VECTOR GRAPHICS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@600;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    #MainMenu, header, footer, .stDeployButton { 
        visibility: hidden !important; 
        display: none !important; 
    }
    
    .stApp {
        background-color: #030712 !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(245, 158, 11, 0.16) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(14, 165, 233, 0.14) 0px, transparent 50%),
            radial-gradient(at 50% 40%, rgba(30, 41, 59, 0.7) 0px, transparent 100%) !important;
        background-attachment: fixed !important;
        color: #F8FAFC !important;
    }

    /* 3D FLOATING GOLDEN AMBIENT TITLE */
    .stage-3d {
        perspective: 1000px;
        text-align: center;
        padding: 10px 0 6px 0;
    }
    
    .brand-3d-text {
        font-size: 25px;
        font-weight: 800;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #F59E0B;
        text-shadow: 
            0 1px 0 #D97706,
            0 2px 0 #B45309,
            0 3px 0 #78350F,
            0 12px 25px rgba(245, 158, 11, 0.5);
        display: inline-block;
        animation: tilt3D 5s ease-in-out infinite alternate;
        transform-style: preserve-3d;
    }
    
    @keyframes tilt3D {
        0% { transform: rotateX(10deg) rotateY(-6deg) translateZ(8px); }
        100% { transform: rotateX(-6deg) rotateY(8deg) translateZ(22px); }
    }

    /* FROSTED GLASS EMBOSSED HERO CARD */
    .header-box {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 24px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 
            0 20px 50px rgba(0, 0, 0, 0.85), 
            inset 0 1px 1px rgba(255, 255, 255, 0.3);
        text-align: center;
    }
    
    .sub-title {
        font-size: 15px;
        font-weight: 700;
        letter-spacing: 2px;
        color: #E2E8F0;
        text-transform: uppercase;
    }

    .branch-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(14, 165, 233, 0.12);
        border: 1px solid rgba(56, 189, 248, 0.35);
        color: #38BDF8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 800;
        padding: 5px 16px;
        border-radius: 30px;
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.25);
        margin-top: 8px;
    }

    /* NEXT-GEN 3D GLASS CARDS */
    .glass-card-3d {
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.45) 0%, rgba(15, 23, 42, 0.65) 100%);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.15);
        transition: transform 0.2s ease;
    }

    /* BADGES */
    .badge-transit {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(245, 158, 11, 0.14);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .badge-received {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.14);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
    }

    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.65);
        padding: 6px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #94A3B8;
        font-weight: 700;
        font-size: 13px;
        padding: 9px 18px;
        border: none !important;
        background: transparent !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: rgba(255, 255, 255, 0.12) !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%) !important;
        color: #050B14 !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        height: 50px !important;
        box-shadow: 0 10px 25px rgba(217, 119, 6, 0.45), inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
    }

    .wa-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white !important;
        text-align: center;
        padding: 12px;
        border-radius: 14px;
        text-decoration: none;
        font-weight: 700;
        font-size: 13px;
        border: 1px solid rgba(52, 211, 153, 0.3);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.35);
    }

    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background: rgba(15, 23, 42, 0.75) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# VECTOR ICONS
ICON_SEND = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>"""
ICON_RECEIVE = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line><path d="M20 17v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2"></path></svg>"""
ICON_SUCCESS = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#34D399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>"""
ICON_TRANSIT = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FBBF24" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>"""
ICON_BELL = """<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>"""
ICON_WA = """<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.316 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.818-.981z"/></svg>"""

# VOUCHER PDF GENERATOR (EXACT MATCH, DYNAMIC ROWS)
def create_voucher_pdf(trx):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    pdf.set_fill_color(254, 252, 235)
    pdf.rect(5, 5, 200, 287, "F")
    
    pdf.set_xy(10, 12)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(190, 6, "JAMAL SHOWAITER SWEETS Co. W.L.L.", ln=True, align="C")
    
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(190, 4, "P.O.Box : 1352 - Manama - Kingdom of Bahrain, Tel: 17341735, Fax: 17342252", ln=True, align="C")
    
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(190, 6, "STOCK TRANSFER NOTE", ln=True, align="C")
    
    pdf.set_xy(10, 28)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.write(5, "No: ")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(220, 38, 38)
    pdf.write(5, f"ST {253600 + trx['id']}")
    
    pdf.set_text_color(20, 20, 20)
    pdf.set_xy(140, 28)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(12, 5, "Date: ")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(38, 5, f" {trx['date_str']}", border="B")
    
    pdf.set_xy(10, 36)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(28, 5, "From Location: ")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(152, 5, f" {trx['from_branch']}", border="B")
    
    pdf.set_xy(10, 44)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(24, 5, "To Location: ")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(156, 5, f" {trx['to_branch']}", border="B")
    
    widths = [12, 22, 76, 20, 20, 20, 20]
    headers = ["S.No.", "Date", "Description", "Qty", "Selling Price", "Unit Price", "Amount"]
    
    pdf.set_xy(10, 53)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_draw_color(50, 50, 50)
    pdf.set_fill_color(245, 240, 215)
    
    for i in range(len(headers)):
        pdf.cell(widths[i], 8, headers[i], border=1, align="C", fill=True)
    pdf.ln()
    
    items = trx.get("items_list", [])
    row_height = 8.5
    
    for idx, it in enumerate(items):
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(widths[0], row_height, str(idx + 1), border=1, align="C")
        
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(widths[1], row_height, trx['date_str'], border=1, align="C")
        
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(widths[2], row_height, " " + str(it.get("desc", ""))[:40], border=1, align="L")
        
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.cell(widths[3], row_height, str(it.get("qty", "")), border=1, align="C")
        
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(widths[4], row_height, str(it.get("sp", "")), border=1, align="C")
        pdf.cell(widths[5], row_height, str(it.get("up", "")), border=1, align="C")
        pdf.cell(widths[6], row_height, str(it.get("amt", "")), border=1, align="C")
        pdf.ln()
        
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(sum(widths[:-1]), 8, "Total Amount  ", border=1, align="R")
    pdf.cell(widths[-1], 8, str(trx.get("total_amount", "")), border=1, align="C")
    pdf.ln(14)
    
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(22, 6, "Issued by: ")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(65, 6, f" {trx['sender_name']}", border="B")
    
    pdf.set_x(115)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(26, 6, "Approved by: ")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(59, 6, f" {trx.get('receiver_name', '')}", border="B")
    
    return bytes(pdf.output())

BRANCHES = [
    "KSSFCT-01",
    "KSSF-01",
    "KSMQ-01",
    "KSMQ-02",
    "KSAV-01",
    "JSSF-02",
    "KSHR-01"
]

query_params = st.query_params
selected_branch = BRANCHES[0]

if "b" in query_params:
    val = query_params["b"].strip().upper()
    if val in BRANCHES:
        selected_branch = val

st.markdown("""
<div class="stage-3d">
    <div class="brand-3d-text">JAMAL SHOWAITER</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-box">
    <div class="sub-title">Stock Transfer Control Hub</div>
    <div class="branch-pill">LOCATION: {selected_branch}</div>
</div>
""", unsafe_allow_html=True)

if "b" not in query_params:
    new_branch = st.sidebar.selectbox("Active Terminal:", BRANCHES, index=BRANCHES.index(selected_branch))
    if new_branch != selected_branch:
        st.query_params["b"] = new_branch
        st.rerun()

tab_dispatch, tab_inbox, tab_history = st.tabs([
    "Dispatch Hub", 
    "Incoming Terminal", 
    "Audit Registry"
])

api_key = st.secrets.get("GEMINI_API_KEY", "")

# 1. DISPATCH
with tab_dispatch:
    st.markdown(f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:14px;'>{ICON_SEND} <h5 style='margin:0;'>Initiate Transfer Note</h5></div>", unsafe_allow_html=True)
    other_branches = [b for b in BRANCHES if b != selected_branch]
    to_loc = st.selectbox("Destination Location:", other_branches)
    issuer = st.text_input("Issued by (Staff Signature):", placeholder="Your Name")
    items_input = st.text_area(
        "Item Manifest & Quantity:", 
        placeholder="kamfaroosh 10\nHalwa Red 5 kg\nBaklava 2 boxes",
        height=130
    )
    
    if st.button("Transmit Stock Transfer Note", use_container_width=True, type="primary"):
        if not issuer.strip():
            st.warning("Staff signature required in 'Issued by'.")
        elif not items_input.strip():
            st.warning("Please specify items to transfer.")
        else:
            with st.spinner("Encrypting & Parsing Manifest..."):
                parsed_list = []
                if api_key:
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = (
                            "Extract items into a JSON array: [{\"desc\": \"name\", \"qty\": \"10\"}]. "
                            "Do not include quantity inside desc. Return raw JSON:\n" + items_input
                        )
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        clean_text = res.text.strip().replace("```json", "").replace("```", "").strip()
                        parsed_list = json.loads(clean_text)
                    except Exception:
                        parsed_list = []
                
                if not parsed_list:
                    parsed_list = parse_items_manual(items_input)
                
                all_data = load_data()
                now = datetime.datetime.now()
                new_trx = {
                    "id": len(all_data) + 1,
                    "from_branch": selected_branch,
                    "to_branch": to_loc,
                    "sender_name": issuer,
                    "receiver_name": "",
                    "items_list": parsed_list,
                    "total_amount": "",
                    "status": "IN TRANSIT",
                    "date_str": now.strftime("%d/%m/%Y"),
                    "time_str": now.strftime("%H:%M")
                }
                all_data.append(new_trx)
                save_data(all_data)
                st.session_state["last_issued"] = new_trx

    if "last_issued" in st.session_state:
        last = st.session_state["last_issued"]
        st.markdown(f"""
        <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(52, 211, 153, 0.4); border-radius: 18px; padding: 18px; margin-top: 14px;">
            <div style="display:flex; align-items:center; gap:8px; color: #34D399; font-weight:800; font-size:15px;">
                {ICON_SUCCESS} TRANSFER NOTE TRANSMITTED
            </div>
            <div style="font-size: 13px; color: #F8FAFC; margin: 6px 0;">
                Voucher <b>ST {253600 + last['id']}</b> logged and dispatched to <b>{last['to_branch']}</b>.
            </div>
            <div style="font-size: 12px; color: #94A3B8; font-family: 'JetBrains Mono';">
                Officer: {last['sender_name']} | Time: {last['date_str']} {last['time_str']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 2. INCOMING
with tab_inbox:
    st.markdown(f"<div style='display:flex; align-items:center; gap:8px; margin-bottom:14px;'>{ICON_RECEIVE} <h5 style='margin:0;'>Live Incoming Feed ({selected_branch})</h5></div>", unsafe_allow_html=True)
    all_data = load_data()
    incoming_pending = [t for t in reversed(all_data) if t["to_branch"] == selected_branch and t["status"] == "IN TRANSIT"]
    
    if not incoming_pending:
        st.info(f"Queue empty. No incoming transfers arriving at {selected_branch}.")
    else:
        audio_html = """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.4); padding: 12px 16px; border-radius: 14px; margin-bottom: 16px; display: flex; align-items: center; gap: 10px;">
            {ICON_BELL}
            <span style="font-weight: 700; color: #FBBF24; font-size: 13px;">INCOMING ALERT: {len(incoming_pending)} stock transfer(s) awaiting verification.</span>
        </div>
        """, unsafe_allow_html=True)

        for trx in incoming_pending:
            v_no = f"ST {253600 + trx['id']}"
            st.markdown(f"""
            <div class="glass-card-3d">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="font-size: 16px; color: #38BDF8;">No: {v_no}</b>
                    <span class="badge-transit">{ICON_TRANSIT} IN TRANSIT</span>
                </div>
                <div style="font-size: 13px; color: #E2E8F0; margin-top: 6px;">
                    Origin: <b>{trx['from_branch']}</b> | Sent by: <b>{trx['sender_name']}</b>
                </div>
                <div style="font-size: 11px; color: #94A3B8; font-family: 'JetBrains Mono'; margin-top: 2px;">
                    Timestamp: {trx['date_str']} at {trx['time_str']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Manifest:**")
            for it in trx['items_list']:
                st.caption(f"• **{it.get('desc')}** — Qty: **{it.get('qty', 'N/A')}**")
                
            rec_name = st.text_input("Approved by (Receiver Signature):", key=f"rec_sig_{trx['id']}", placeholder="Type your name here...")
            
            if st.button(f"Verify & Sign Voucher #{trx['id']}", key=f"btn_accept_{trx['id']}", use_container_width=True, type="primary"):
                if not rec_name.strip():
                    st.warning("Receiver signature required.")
                else:
                    for item in all_data:
                        if item["id"] == trx["id"]:
                            item["status"] = "RECEIVED"
                            item["receiver_name"] = rec_name.strip()
                            item["received_date"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                            break
                    save_data(all_data)
                    st.session_state[f"accepted_{trx['id']}"] = True
                    st.success(f"Voucher #{trx['id']} signed and received!")
                    st.rerun()

            if st.session_state.get(f"accepted_{trx['id']}", False) or trx["status"] == "RECEIVED":
                st.success("Verification complete. Official note generated below:")
                pdf_bytes = create_voucher_pdf(trx)
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download Voucher PDF",
                        data=pdf_bytes,
                        file_name=f"Voucher_{v_no.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_instant_{trx['id']}",
                        use_container_width=True
                    )
                with col2:
                    wa_items = "\n".join([f"- {it.get('desc')} (Qty: {it.get('qty')})" for it in trx['items_list']])
                    wa_msg = (
                        f"*JAMAL SHOWAITER SWEETS Co. W.L.L.*\n"
                        f"*STOCK TRANSFER NOTE*\n\n"
                        f"*No:* {v_no}\n"
                        f"*Date:* {trx['date_str']}\n"
                        f"*From:* {trx['from_branch']}\n"
                        f"*To:* {trx['to_branch']}\n"
                        f"*Issued by:* {trx['sender_name']}\n"
                        f"*Approved by:* {trx['receiver_name']}\n\n"
                        f"*Items Verified:*\n{wa_items}\n\n"
                        f"_Official Verified Transfer Note._"
                    )
                    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">{ICON_WA} WhatsApp Share</a>', unsafe_allow_html=True)

            st.divider()

# 3. HISTORY
with tab_history:
    st.markdown("##### Terminal Registry")
    all_data = load_data()
    branch_history = [t for t in reversed(all_data) if t["from_branch"] == selected_branch or t["to_branch"] == selected_branch]
    
    if not branch_history:
        st.info(f"No records archived for terminal {selected_branch}.")
    else:
        for trx in branch_history:
            v_no = f"ST {253600 + trx['id']}"
            is_out = (trx["from_branch"] == selected_branch)
            direction = f"Outbound to {trx['to_branch']}" if is_out else f"Inbound from {trx['from_branch']}"
            badge_html = f'<span class="badge-received">{ICON_SUCCESS} RECEIVED</span>' if trx['status'] == "RECEIVED" else f'<span class="badge-transit">{ICON_TRANSIT} IN TRANSIT</span>'
            
            st.markdown(f"""
            <div class="glass-card-3d">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="font-size: 15px; color: #F8FAFC;">No: {v_no}</b>
                    {badge_html}
                </div>
                <div style="font-size: 13px; color: #38BDF8; margin-top: 4px; font-weight: 700;">{direction}</div>
                <div style="font-size: 12px; color: #94A3B8;">Issued: <b>{trx['sender_name']}</b> | Approved: <b>{trx.get('receiver_name', 'Pending')}</b></div>
                <div style="font-size: 11px; color: #64748B; font-family: 'JetBrains Mono';">Date: {trx['date_str']} {trx['time_str']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if trx['status'] == "RECEIVED":
                pdf_bytes = create_voucher_pdf(trx)
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(
                        label="Download PDF",
                        data=pdf_bytes,
                        file_name=f"Voucher_{v_no.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_hist_{trx['id']}",
                        use_container_width=True
                    )
                with c2:
                    wa_items = "\n".join([f"- {it.get('desc')} (Qty: {it.get('qty')})" for it in trx['items_list']])
                    wa_msg = (
                        f"*JAMAL SHOWAITER SWEETS Co. W.L.L.*\n"
                        f"*STOCK TRANSFER NOTE*\n\n"
                        f"*No:* {v_no}\n"
                        f"*Date:* {trx['date_str']}\n"
                        f"*From:* {trx['from_branch']}\n"
                        f"*To:* {trx['to_branch']}\n"
                        f"*Issued by:* {trx['sender_name']}\n"
                        f"*Approved by:* {trx['receiver_name']}\n\n"
                        f"*Items:*\n{wa_items}\n\n"
                        f"_Official Voucher Verified & Logged._"
                    )
                    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">{ICON_WA} WhatsApp Share</a>', unsafe_allow_html=True)
            st.divider()

    if branch_history:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 16px; padding: 16px; margin-top: 20px;">
            <b style="color: #F87171; font-size: 14px;">Registry Maintenance</b><br>
            <span style="font-size: 12px; color: #9CA3AF;">Permanently clear stored transfers.</span>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_del = st.checkbox(f"Confirm registry purge for {selected_branch}", key="confirm_del_box")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button(f"Purge {selected_branch} Only", use_container_width=True):
                if not confirm_del:
                    st.warning("Confirmation required.")
                else:
                    updated_data = [t for t in all_data if t["from_branch"] != selected_branch and t["to_branch"] != selected_branch]
                    save_data(updated_data)
                    st.success(f"Registry cleared for {selected_branch}!")
                    st.rerun()
                    
        with col_c2:
            if st.button("Purge Global Registry", use_container_width=True):
                if not confirm_del:
                    st.warning("Confirmation required.")
                else:
                    save_data([])
                    st.success("Global registry purged!")
                    st.rerun()
