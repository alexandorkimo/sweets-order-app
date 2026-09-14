import streamlit as st
from google import genai
from fpdf import FPDF
import datetime
import urllib.parse
import json
import os
import re

# Page Setup
st.set_page_config(
    page_title="STOCK TRANSFER | Jamal Showaiter",
    page_icon="🍬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Persistent Data Storage
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

# Fallback Parsing Function: Automatically separates Item Name and Quantity
def parse_items_manual(text):
    parsed = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    for line in lines:
        # Match quantity at the end (e.g., 'kamfaroosh 10', 'Halwa 5 kg', 'Baklava - 3 boxes')
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

# 3D GLASSMORPHISM & TEXT ANIMATION STYLES
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700;800&family=JetBrains+Mono:wght@600;800&display=swap');
    
    * {
        font-family: 'Space Grotesk', -apple-system, sans-serif;
    }
    
    #MainMenu, header, footer, .stDeployButton { 
        visibility: hidden !important; 
        display: none !important; 
    }
    
    .stApp {
        background-color: #020408 !important;
        background-image: 
            radial-gradient(circle at 50% 10%, rgba(245, 158, 11, 0.15) 0%, transparent 60%),
            radial-gradient(circle at 90% 90%, rgba(14, 165, 233, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 10% 80%, rgba(168, 85, 247, 0.08) 0%, transparent 50%) !important;
        background-attachment: fixed !important;
        color: #F8FAFC !important;
    }

    /* 3D FLOATING & GLOWING TITLE ANIMATION */
    .stage-3d {
        perspective: 900px;
        text-align: center;
        padding: 15px 0 5px 0;
    }
    
    .brand-3d-text {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #F59E0B;
        text-shadow: 
            0 1px 0 #D97706,
            0 2px 0 #B45309,
            0 3px 0 #92400E,
            0 4px 0 #78350F,
            0 10px 20px rgba(245, 158, 11, 0.5);
        display: inline-block;
        animation: float3D 4s ease-in-out infinite alternate;
        transform-style: preserve-3d;
    }
    
    @keyframes float3D {
        0% {
            transform: rotateX(12deg) rotateY(-8deg) translateZ(10px);
        }
        100% {
            transform: rotateX(-8deg) rotateY(10deg) translateZ(25px);
        }
    }

    /* ULTRA 3D FROSTED GLASS CARD */
    .header-box {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 
            0 20px 40px rgba(0, 0, 0, 0.8), 
            inset 0 1px 1px rgba(255, 255, 255, 0.2);
        text-align: center;
    }
    
    .sub-title {
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #FFFFFF;
        margin-top: 4px;
    }

    .branch-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(14, 165, 233, 0.15);
        border: 1px solid rgba(56, 189, 248, 0.4);
        color: #38BDF8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 800;
        padding: 4px 14px;
        border-radius: 20px;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.25);
        margin-top: 8px;
    }

    /* GLASS CARDS */
    .order-card-3d {
        background: rgba(15, 23, 42, 0.55);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }

    /* BADGES */
    .badge-transit {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .badge-received {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 10px;
        border-radius: 15px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(135deg, #D97706 0%, #B45309 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(251, 191, 36, 0.4) !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        height: 48px !important;
        box-shadow: 0 8px 25px -4px rgba(217, 119, 6, 0.5) !important;
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
        box-shadow: 0 8px 25px -4px rgba(16, 185, 129, 0.4);
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background: rgba(15, 23, 42, 0.75) !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# BOLD DYNAMIC VOUCHER PDF GENERATOR (EXACT MATCH, NO EXTRA ROWS)
def create_voucher_pdf(trx):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    # Yellowish Tint Paper Background
    pdf.set_fill_color(254, 252, 235)
    pdf.rect(5, 5, 200, 287, "F")
    
    # Header Details
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
    
    # Serial No & Date
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
    
    # From Location & To Location
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
    
    # Columns Header
    widths = [12, 22, 76, 20, 20, 20, 20]
    headers = ["S.No.", "Date", "Description", "Qty", "Selling Price", "Unit Price", "Amount"]
    
    pdf.set_xy(10, 53)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_draw_color(50, 50, 50)
    pdf.set_fill_color(245, 240, 215)
    
    for i in range(len(headers)):
        pdf.cell(widths[i], 8, headers[i], border=1, align="C", fill=True)
    pdf.ln()
    
    # Dynamic Item Rows (Only prints rows according to actual items)
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
        
    # Total Row
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(sum(widths[:-1]), 8, "Total Amount  ", border=1, align="R")
    pdf.cell(widths[-1], 8, str(trx.get("total_amount", "")), border=1, align="C")
    pdf.ln(14)
    
    # Signatures
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

# Branch List
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

# 3D Animated Title Header
st.markdown("""
<div class="stage-3d">
    <div class="brand-3d-text">JAMAL SHOWAITER</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="header-box">
    <div class="sub-title">STOCK TRANSFER PORTAL</div>
    <div class="branch-pill">⚡ LOCATION: {selected_branch}</div>
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
    st.markdown("##### 📤 Issue Stock Transfer Note")
    other_branches = [b for b in BRANCHES if b != selected_branch]
    to_loc = st.selectbox("Destination Location:", other_branches)
    issuer = st.text_input("Issued by (Staff Signature):", placeholder="Your Name")
    items_input = st.text_area(
        "Enter Items & Qty:", 
        placeholder="Type items freely:\nkamfaroosh 10\nHalwa Red King 5 kg\nVIP Baklava 2 boxes",
        height=130
    )
    
    if st.button("🚀 Issue Stock Transfer Note", use_container_width=True, type="primary"):
        if not issuer.strip():
            st.warning("Staff signature required in 'Issued by'.")
        elif not items_input.strip():
            st.warning("Please specify the items to transfer.")
        else:
            with st.spinner("Processing & Extracting Quantities..."):
                parsed_list = []
                if api_key:
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = (
                            "Extract each item description and its corresponding quantity strictly into a JSON list of objects. "
                            "Format: [{\"desc\": \"kamfaroosh\", \"qty\": \"10\", \"sp\": \"\", \"up\": \"\", \"amt\": \"\"}]. "
                            "Do not combine quantity inside desc. Only return raw JSON:\n" + items_input
                        )
                        res = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=prompt
                        )
                        clean_text = res.text.strip().replace("```json", "").replace("```", "").strip()
                        parsed_list = json.loads(clean_text)
                    except Exception:
                        parsed_list = []
                
                # If AI API latency or error occurs, run fast regex auto-parser
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
        <div style="background: rgba(16, 185, 129, 0.12); border: 1.5px solid #10B981; border-radius: 16px; padding: 18px; margin-top: 14px;">
            <div style="font-size: 15px; font-weight: 800; color: #34D399; margin-bottom: 4px;">
                ✅ TRANSFER NOTE ISSUED SUCCESSFULLY!
            </div>
            <div style="font-size: 13px; color: #F8FAFC; margin-bottom: 6px;">
                Voucher <b>ST {253600 + last['id']}</b> logged and dispatched to <b>{last['to_branch']}</b>.
            </div>
            <div style="font-size: 12px; color: #94A3B8; font-family: 'JetBrains Mono';">
                Issued by: {last['sender_name']} | Time: {last['date_str']} {last['time_str']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 2. INCOMING TAB WITH AUDIO & LIVE ALERT
with tab_inbox:
    st.markdown(f"##### 📥 Live Incoming Queue ({selected_branch})")
    all_data = load_data()
    incoming_pending = [t for t in reversed(all_data) if t["to_branch"] == selected_branch and t["status"] == "IN TRANSIT"]
    
    if not incoming_pending:
        st.info(f"No pending transfers arriving at {selected_branch}.")
    else:
        # Standard Audio Notification Chime
        audio_html = """
        <audio autoplay style="display:none;">
            <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
        </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: rgba(245, 158, 11, 0.15); border: 1px solid #F59E0B; padding: 10px 16px; border-radius: 12px; margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 20px;">🔔</span>
            <span style="font-weight: 700; color: #FBBF24; font-size: 13px;">NEW ORDER RECEIVED! You have {len(incoming_pending)} stock transfer(s) awaiting acceptance.</span>
        </div>
        """, unsafe_allow_html=True)

        for trx in incoming_pending:
            v_no = f"ST {253600 + trx['id']}"
            st.markdown(f"""
            <div class="order-card-3d">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="font-size: 16px; color: #38BDF8;">No: {v_no}</b>
                    <span class="badge-transit">⏳ PENDING ACCEPTANCE</span>
                </div>
                <div style="font-size: 13px; color: #E2E8F0; margin-top: 6px;">
                    Origin: <b>{trx['from_branch']}</b> | Dispatched by: <b>{trx['sender_name']}</b>
                </div>
                <div style="font-size: 11px; color: #94A3B8; font-family: 'JetBrains Mono'; margin-top: 2px;">
                    Time: {trx['date_str']} at {trx['time_str']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Manifest Items:**")
            for it in trx['items_list']:
                st.caption(f"• **{it.get('desc')}** — Qty: **{it.get('qty', 'N/A')}**")
                
            rec_name = st.text_input("Approved by (Receiver Signature):", key=f"rec_sig_{trx['id']}", placeholder="Type your name here...")
            
            if st.button(f"✅ Accept & Sign Voucher #{trx['id']}", key=f"btn_accept_{trx['id']}", use_container_width=True, type="primary"):
                if not rec_name.strip():
                    st.warning("⚠️ Receiver signature required.")
                else:
                    for item in all_data:
                        if item["id"] == trx["id"]:
                            item["status"] = "RECEIVED"
                            item["receiver_name"] = rec_name.strip()
                            item["received_date"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                            break
                    save_data(all_data)
                    st.session_state[f"accepted_{trx['id']}"] = True
                    st.success(f"Stock Voucher #{trx['id']} verified by {rec_name}!")
                    st.rerun()

            if st.session_state.get(f"accepted_{trx['id']}", False) or trx["status"] == "RECEIVED":
                st.success("🎉 Receipt Verified! Download official voucher below:")
                pdf_bytes = create_voucher_pdf(trx)
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📄 Download Voucher PDF",
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
                        f"_Transfer Verified & Received Successfully._"
                    )
                    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 WhatsApp Share</a>', unsafe_allow_html=True)

            st.divider()

# 3. HISTORY TAB
with tab_history:
    st.markdown(f"##### 📜 Transfer History ({selected_branch})")
    all_data = load_data()
    branch_history = [t for t in reversed(all_data) if t["from_branch"] == selected_branch or t["to_branch"] == selected_branch]
    
    if not branch_history:
        st.info(f"No records found for terminal {selected_branch}.")
    else:
        for trx in branch_history:
            v_no = f"ST {253600 + trx['id']}"
            is_out = (trx["from_branch"] == selected_branch)
            direction = f"📤 Sent to {trx['to_branch']}" if is_out else f"📥 Received from {trx['from_branch']}"
            badge_html = '<span class="badge-received">✅ RECEIVED</span>' if trx['status'] == "RECEIVED" else '<span class="badge-transit">⏳ IN TRANSIT</span>'
            
            st.markdown(f"""
            <div class="order-card-3d">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="font-size: 15px; color: #F8FAFC;">No: {v_no}</b>
                    {badge_html}
                </div>
                <div style="font-size: 13px; color: #38BDF8; margin-top: 4px; font-weight: 600;">{direction}</div>
                <div style="font-size: 12px; color: #94A3B8;">Issued: <b>{trx['sender_name']}</b> | Approved: <b>{trx.get('receiver_name', 'Pending')}</b></div>
                <div style="font-size: 11px; color: #64748B; font-family: 'JetBrains Mono';">Date: {trx['date_str']} {trx['time_str']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if trx['status'] == "RECEIVED":
                pdf_bytes = create_voucher_pdf(trx)
                c1, c2 = st.columns(2)
                with c1:
                    st.download_button(
                        label="📄 Download PDF",
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
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 WhatsApp</a>', unsafe_allow_html=True)
            st.divider()

    # Clear History Section
    if branch_history:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 14px; padding: 14px; margin-top: 20px;">
            <b style="color: #F87171; font-size: 14px;">🗑️ Clear Transfer History</b><br>
            <span style="font-size: 12px; color: #9CA3AF;">Delete history records permanently from storage.</span>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_del = st.checkbox(f"Confirm deletion for {selected_branch}", key="confirm_del_box")
        
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button(f"🗑️ Clear {selected_branch} Only", use_container_width=True):
                if not confirm_del:
                    st.warning("⚠️ Please check confirmation box first.")
                else:
                    updated_data = [t for t in all_data if t["from_branch"] != selected_branch and t["to_branch"] != selected_branch]
                    save_data(updated_data)
                    st.success(f"History cleared for {selected_branch}!")
                    st.rerun()
                    
        with col_c2:
            if st.button("⚠️ Clear Entire System Data", use_container_width=True):
                if not confirm_del:
                    st.warning("⚠️ Please check confirmation box first.")
                else:
                    save_data([])
                    st.success("All system history cleared successfully!")
                    st.rerun()
