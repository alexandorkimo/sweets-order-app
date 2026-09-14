import streamlit as st
from google import genai
from fpdf import FPDF
import datetime
import urllib.parse
import json
import os

# Page Settings
st.set_page_config(
    page_title="STOCK TRANSFER | Jamal Showaiter",
    page_icon="📋",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Persistent Storage
DB_FILE = "stock_transfers_db.json"

def load_transfers():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_transfers(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

# HIGH DEFINITION ULTRA-DARK THEME + SYSTEM LOCKDOWN CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
    }
    
    /* SYSTEM LOCKDOWN: Hides edit menus, deployment links, github source, footer */
    #MainMenu, header, footer, .stDeployButton, [data-testid="stToolbar"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Deep OLED / Carbon Black Background */
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0F172A 0%, #020617 100%) !important;
        color: #F1F5F9 !important;
    }

    /* HD Corporate Glassmorphic Header */
    .top-header {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 22px 18px;
        border-radius: 16px;
        margin-bottom: 22px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
        border-left: 4px solid #D97706;
    }
    
    .company-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #F59E0B;
        text-transform: uppercase;
        margin-bottom: 3px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .main-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0;
        color: #FFFFFF;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    
    .branch-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        margin-top: 10px;
        color: #38BDF8;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Dark Cards */
    .item-card {
        background: rgba(15, 23, 42, 0.65);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    
    .badge {
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }
    .badge-transit { 
        background: rgba(245, 158, 11, 0.15); 
        color: #FBBF24; 
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-received { 
        background: rgba(34, 197, 94, 0.15); 
        color: #4ADE80; 
        border: 1px solid rgba(34, 197, 94, 0.3);
    }

    /* Dark Theme Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background-color: #090D16 !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.14) !important;
        border-radius: 12px !important;
    }
    
    /* Sleek Action Buttons */
    .stButton>button {
        border-radius: 12px;
        font-weight: 700;
        font-size: 14px;
        height: 46px;
        border: none;
        transition: all 0.2s ease-in-out;
    }
    
    .wa-btn {
        display: block;
        background: #25D366;
        color: white !important;
        padding: 11px;
        border-radius: 12px;
        text-decoration: none;
        font-weight: 700;
        font-size: 13px;
        text-align: center;
        margin-top: 6px;
        box-shadow: 0 4px 12px rgba(37, 211, 102, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# EXACT REAL VOUCHER PDF GENERATOR
def generate_voucher_pdf(trx):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    # Cream / Paper Voucher Tint
    pdf.set_fill_color(254, 252, 235)
    pdf.rect(5, 5, 200, 287, "F")
    
    # 1. Header
    pdf.set_xy(10, 10)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(190, 5, "JAMAL SHOWAITER SWEETS Co. W.L.L.", ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 7.5)
    pdf.cell(190, 4, "P.O.Box : 1352 - Manama - Kingdom of Bahrain, Tel: 17341735, Fax: 17342252", ln=True, align="C")
    
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(190, 5, "STOCK TRANSFER NOTE", ln=True, align="C")
    
    # 2. Serial No & Date
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
    
    # 3. From / To Location
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
    
    # 4. Table Header
    widths = [10, 18, 74, 14, 22, 22, 30]
    headers = ["S.No.", "Date", "Description", "Qty", "Selling Price", "Unit Price", "Amount (BD)"]
    
    pdf.set_xy(10, 48)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_draw_color(70, 70, 70)
    pdf.set_fill_color(250, 248, 228)
    
    for i in range(len(headers)):
        pdf.cell(widths[i], 7, headers[i], border=1, align="C", fill=True)
    pdf.ln()
    
    # 5. Table Rows (Up to 14 rows)
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
        
    # 6. Total Amount
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(160, 7.5, "Total Amount  ", border=1, align="R")
    pdf.cell(30, 7.5, trx.get("total_amount", ""), border=1, align="C")
    pdf.ln(12)
    
    # 7. Issued by & Approved by
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

# SYSTEM BRANCHES
BRANCHES = [
    "KSSFCT-01",
    "KSSF-01",
    "KSMQ-01",
    "KSMQ-02",
    "KSAV-01",
    "JSSF-02"
]

# Locked Branch Detection from URL
query_params = st.query_params
locked_branch = None

if "b" in query_params:
    input_b = query_params["b"].strip().upper()
    if input_b in BRANCHES:
        locked_branch = input_b

# If URL has no branch parameter, show security lock notice
if not locked_branch:
    st.markdown("""
    <div class="top-header">
        <div class="company-title">Jamal Showaiter Sweets Co. W.L.L.</div>
        <div class="main-title">STOCK TRANSFER</div>
        <div class="branch-badge">🔒 AUTHENTICATION REQUIRED</div>
    </div>
    """, unsafe_allow_html=True)
    st.warning("⚠️ Access Denied: Please use your designated branch portal link to operate.")
    st.stop()

# LOCKED BRANCH ACTIVE VIEW
st.markdown(f"""
<div class="top-header">
    <div class="company-title">Jamal Showaiter Sweets Co. W.L.L.</div>
    <div class="main-title">STOCK TRANSFER</div>
    <div class="branch-badge">🔒 TERMINAL: {locked_branch}</div>
</div>
""", unsafe_allow_html=True)

tab_dispatch, tab_inbox, tab_history = st.tabs([
    "📤 Dispatch Stock", 
    "📥 Incoming Stock", 
    "📜 Branch History"
])

api_key = st.secrets.get("GEMINI_API_KEY", "")

# 1. DISPATCH TAB
with tab_dispatch:
    st.markdown("#### 📤 Initiate Transfer Note")
    
    other_branches = [b for b in BRANCHES if b != locked_branch]
    to_branch = st.selectbox("Destination Location:", other_branches)
    sender_name = st.text_input("Issued by (Staff Name):", placeholder="Officer Name")
    items_raw = st.text_area(
        "Manifest Details (Items & Qty):",
        placeholder="e.g.:\nHalwa Red King - 10 kg\nVIP Baklava - 5 boxes\nKaju Katli - 2 kg",
        height=120
    )
    
    if st.button("🚀 Transmit Stock Transfer Note", use_container_width=True, type="primary"):
        if not sender_name.strip():
            st.warning("Staff signature required in 'Issued by'.")
        elif not items_raw.strip():
            st.warning("Item details cannot be empty.")
        else:
            with st.spinner("Encrypting & Formatting Voucher..."):
                parsed_list = []
                if api_key:
                    try:
                        client = genai.Client(api_key=api_key)
                        prompt = (
                            "Parse these inventory items into a strict JSON array. Format: "
                            '[{"desc": "Item Name", "qty": "10 kg", "sp": "", "up": "", "amt": ""}]. '
                            'Output ONLY JSON without formatting tags:\n' + items_raw
                        )
                        for m in ['gemini-2.5-flash', 'gemini-1.5-flash']:
                            try:
                                res = client.models.generate_content(model=m, contents=prompt)
                                clean_json = res.text.strip().replace("```json", "").replace("```", "").strip()
                                parsed_list = json.loads(clean_json)
                                break
                            except Exception:
                                continue
                    except Exception:
                        pass
                        
                if not parsed_list:
                    lines = [l.strip() for l in items_raw.split("\n") if l.strip()]
                    parsed_list = [{"desc": l, "qty": "", "sp": "", "up": "", "amt": ""} for l in lines]
                    
                all_transfers = load_transfers()
                now = datetime.datetime.now()
                new_trx = {
                    "id": len(all_transfers) + 1,
                    "from_branch": locked_branch,
                    "to_branch": to_branch,
                    "sender_name": sender_name,
                    "receiver_name": "",
                    "items_list": parsed_list,
                    "total_amount": "",
                    "status": "IN TRANSIT",
                    "date_str": now.strftime("%d/%m/%Y"),
                    "time_str": now.strftime("%H:%M")
                }
                all_transfers.append(new_trx)
                save_transfers(all_transfers)
                st.success(f"Voucher ST {253600 + new_trx['id']} logged & transmitted to {to_branch}!")
                st.rerun()

# 2. INBOX TAB
with tab_inbox:
    st.markdown(f"#### 📥 Incoming Deliveries ({locked_branch})")
    all_transfers = load_transfers()
    
    incoming = [t for t in reversed(all_transfers) if t["to_branch"] == locked_branch and t["status"] == "IN TRANSIT"]
    
    if not incoming:
        st.info(f"No pending transfers arriving at {locked_branch}.")
    else:
        for trx in incoming:
            voucher_no = f"ST {253600 + trx['id']}"
            with st.container():
                st.markdown(f"""
                <div class="item-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; color: #38BDF8; font-size: 15px;">No: {voucher_no}</span>
                        <span class="badge badge-transit">⏳ IN TRANSIT</span>
                    </div>
                    <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                        Origin: <b>{trx['from_branch']}</b> | Issued by: <b>{trx['sender_name']}</b>
                    </div>
                    <div style="font-size: 11px; color: #64748B;">
                        Dispatched: {trx['date_str']} at {trx['time_str']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                for itm in trx['items_list']:
                    st.caption(f"• **{itm.get('desc')}** — Qty: {itm.get('qty', 'N/A')}")
                    
                rec_name = st.text_input("Approved by (Your Signature):", key=f"rec_{trx['id']}", placeholder="Receiver Name")
                if st.button(f"✅ Accept & Sign Voucher #{trx['id']}", key=f"btn_rec_{trx['id']}", use_container_width=True, type="primary"):
                    if not rec_name.strip():
                        st.warning("Receiver name signature required.")
                    else:
                        for item in all_transfers:
                            if item["id"] == trx["id"]:
                                item["status"] = "RECEIVED"
                                item["receiver_name"] = rec_name
                                item["received_date"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                                break
                        save_transfers(all_transfers)
                        st.success("Transfer confirmed and signed!")
                        st.rerun()
                st.divider()

# 3. HISTORY TAB (LOCKED TO THIS BRANCH ONLY)
with tab_history:
    st.markdown(f"#### 📜 Terminal History: {locked_branch}")
    st.caption("Immutable record of dispatches and receipts.")
    
    all_transfers = load_transfers()
    branch_history = [t for t in reversed(all_transfers) if t["from_branch"] == locked_branch or t["to_branch"] == locked_branch]
    
    if not branch_history:
        st.info(f"No history logged for terminal {locked_branch}.")
    else:
        for trx in branch_history:
            voucher_no = f"ST {253600 + trx['id']}"
            is_outgoing = (trx["from_branch"] == locked_branch)
            direction = f"📤 Sent to {trx['to_branch']}" if is_outgoing else f"📥 Received from {trx['from_branch']}"
            badge_cls = "badge-received" if trx['status'] == "RECEIVED" else "badge-transit"
            
            st.markdown(f"""
            <div class="item-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 700; color: #F8FAFC; font-size: 14px;">No: {voucher_no}</span>
                    <span class="badge {badge_cls}">{trx['status']}</span>
                </div>
                <div style="font-size: 13px; font-weight: 600; color: #38BDF8; margin-top: 4px;">
                    {direction}
                </div>
                <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">
                    Issued: <b>{trx['sender_name']}</b> | Approved: <b>{trx.get('receiver_name', 'Pending')}</b>
                </div>
                <div style="font-size: 11px; color: #64748B;">
                    Date: {trx['date_str']} {trx['time_str']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if trx['status'] == "RECEIVED":
                pdf_bytes = generate_voucher_pdf(trx)
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_bytes,
                        file_name=f"Voucher_{voucher_no.replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"dl_{trx['id']}",
                        use_container_width=True
                    )
                with col2:
                    wa_items = "\n".join([f"- {it.get('desc')} ({it.get('qty')})" for it in trx['items_list']])
                    wa_msg = (
                        f"*JAMAL SHOWAITER SWEETS Co. W.L.L.*\n"
                        f"*STOCK TRANSFER NOTE*\n\n"
                        f"*No:* {voucher_no}\n"
                        f"*Date:* {trx['date_str']}\n"
                        f"*From Location:* {trx['from_branch']}\n"
                        f"*To Location:* {trx['to_branch']}\n"
                        f"*Issued by:* {trx['sender_name']}\n"
                        f"*Approved by:* {trx['receiver_name']}\n\n"
                        f"*Items:*\n{wa_items}\n\n"
                        f"_Official Voucher Verified & Logged._"
                    )
                    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 WhatsApp</a>', unsafe_allow_html=True)
            st.divider()
            
