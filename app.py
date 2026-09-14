import streamlit as st
from google import genai
from fpdf import FPDF
import datetime
import urllib.parse
import json
import os
import re

st.set_page_config(
    page_title="Jamal Showaiter | Express Transfer",
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

# TALABAT STYLE MODERN MOBILE APP UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@700&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }
    
    #MainMenu, header, footer, .stDeployButton { 
        visibility: hidden !important; 
        display: none !important; 
    }
    
    .stApp {
        background-color: #0E1117 !important;
        color: #F8FAFC !important;
    }

    /* Talabat App Header Bar */
    .talabat-header {
        background: linear-gradient(180deg, #181D27 0%, #12161F 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 16px 18px;
        margin-bottom: 18px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
    }
    
    .loc-sub {
        font-size: 11px;
        font-weight: 700;
        color: #FF5A00;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 5px;
    }
    
    .loc-main {
        font-size: 20px;
        font-weight: 800;
        color: #FFFFFF;
        letter-spacing: -0.5px;
        margin: 2px 0 6px 0;
    }
    
    .branch-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 90, 0, 0.12);
        border: 1px solid rgba(255, 90, 0, 0.35);
        color: #FF7A30;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 12px;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 25px;
    }

    /* Talabat Quick Category Chips */
    .cat-scroll-container {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 10px;
        margin-bottom: 12px;
    }
    
    .cat-chip {
        background: #181D27;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 8px 14px;
        font-size: 12px;
        font-weight: 700;
        color: #94A3B8;
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Talabat Food Delivery Style Cards */
    .talabat-card {
        background: #181D27;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        position: relative;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background: #FF5A00;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #FF5A00;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.3); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    .chip-transit {
        background: rgba(255, 90, 0, 0.15);
        color: #FF7A30;
        border: 1px solid rgba(255, 90, 0, 0.4);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace !important;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }

    .chip-delivered {
        background: rgba(16, 185, 129, 0.15);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Talabat Style Tab Navigation */
    .stTabs [data-baseweb="tab-list"] {
        background: #141822;
        padding: 6px;
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        gap: 8px;
        margin-bottom: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        color: #94A3B8;
        font-weight: 700;
        font-size: 13px;
        padding: 10px 18px;
        background: transparent !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background: #FF5A00 !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 15px rgba(255, 90, 0, 0.35);
    }

    /* Talabat Orange Action Button */
    .stButton>button {
        background: linear-gradient(135deg, #FF5A00 0%, #E04800 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
        height: 50px !important;
        box-shadow: 0 8px 25px rgba(255, 90, 0, 0.4) !important;
        letter-spacing: -0.2px;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 30px rgba(255, 90, 0, 0.6) !important;
    }

    .wa-talabat-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background: #25D366;
        color: white !important;
        text-align: center;
        padding: 12px;
        border-radius: 14px;
        text-decoration: none;
        font-weight: 700;
        font-size: 13px;
        box-shadow: 0 6px 20px rgba(37, 211, 102, 0.3);
        margin-top: 6px;
    }

    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background: #141822 !important;
        color: #F8FAFC !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        font-size: 14px !important;
    }
</style>
""", unsafe_allow_html=True)

# Voucher PDF Generator
def create_voucher_pdf(trx):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()
    
    pdf.set_fill_color(254, 252, 235)
    pdf.rect(5, 5, 200, 287, "F")
    
    pdf.set_xy(10, 12)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(190, 6, "JAMAL SHOWAITER SWEETS Co. W.L.L.", ln=True, align="C")
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(190, 4, "P.O.Box : 1352 - Manama - Kingdom of Bahrain, Tel: 17341735, Fax: 17342252", ln=True, align="C")
    
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(190, 6, "STOCK TRANSFER NOTE", ln=True, align="C")
    
    pdf.set_xy(10, 28)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(20, 20, 20)
    pdf.write(5, "No: ")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(220, 38, 38)
    pdf.write(5, f"ST {253600 + trx['id']}")
    
    pdf.set_text_color(20, 20, 20)
    pdf.set_xy(140, 28)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(12, 5, "Date: ")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(38, 5, f" {trx['date_str']}", border="B")
    
    pdf.set_xy(10, 36)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(28, 5, "From Location: ")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(152, 5, f" {trx['from_branch']}", border="B")
    
    pdf.set_xy(10, 44)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(24, 5, "To Location: ")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(156, 5, f" {trx['to_branch']}", border="B")
    
    widths = [12, 22, 76, 20, 20, 20, 20]
    headers = ["S.No.", "Date", "Description", "Qty", "Selling Price", "Unit Price", "Amount"]
    
    pdf.set_xy(10, 53)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_draw_color(60, 60, 60)
    pdf.set_fill_color(245, 240, 215)
    
    for i in range(len(headers)):
        pdf.cell(widths[i], 8, headers[i], border=1, align="C", fill=True)
    pdf.ln()
    
    items = trx.get("items_list", [])
    row_height = 8
    
    for idx, it in enumerate(items):
        pdf.set_x(10)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(widths[0], row_height, str(idx + 1), border=1, align="C")
        
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(widths[1], row_height, trx['date_str'], border=1, align="C")
        
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(widths[2], row_height, " " + str(it.get("desc", ""))[:40], border=1, align="L")
        
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(widths[3], row_height, str(it.get("qty", "")), border=1, align="C")
        
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(widths[4], row_height, str(it.get("sp", "")), border=1, align="C")
        pdf.cell(widths[5], row_height, str(it.get("up", "")), border=1, align="C")
        pdf.cell(widths[6], row_height, str(it.get("amt", "")), border=1, align="C")
        pdf.ln()
        
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(sum(widths[:-1]), 8, "Total Amount  ", border=1, align="R")
    pdf.cell(widths[-1], 8, str(trx.get("total_amount", "")), border=1, align="C")
    pdf.ln(12)
    
    pdf.set_x(10)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(20, 6, "Issued by: ")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(65, 6, f" {trx['sender_name']}", border="B")
    
    pdf.set_x(115)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.cell(24, 6, "Approved by: ")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.cell(61, 6, f" {trx.get('receiver_name', '')}", border="B")
    
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

# Talabat Top Mobile Navigation Bar
st.markdown(f"""
<div class="talabat-header">
    <div class="loc-sub">● ACTIVE STORE LOCATION</div>
    <div class="loc-main">Jamal Showaiter Sweets</div>
    <div class="branch-badge">HUB: {selected_branch}</div>
</div>
""", unsafe_allow_html=True)

if "b" not in query_params:
    new_branch = st.sidebar.selectbox("Active Terminal:", BRANCHES, index=BRANCHES.index(selected_branch))
    if new_branch != selected_branch:
        st.query_params["b"] = new_branch
        st.rerun()

# Category Chips Bar (Talabat Style)
st.markdown("""
<div class="cat-scroll-container">
    <div class="cat-chip" style="background:#FF5A00; color:white;">⚡ All Items</div>
    <div class="cat-chip">👑 Royal Halwa</div>
    <div class="cat-chip">🥐 VIP Baklava</div>
    <div class="cat-chip">🍪 Kamfaroosh</div>
    <div class="cat-chip">🍯 Honey & Nuts</div>
</div>
""", unsafe_allow_html=True)

tab_dispatch, tab_inbox, tab_history = st.tabs([
    "Dispatch Order", 
    "Live Orders", 
    "History"
])

api_key = st.secrets.get("GEMINI_API_KEY", "")

# 1. DISPATCH (TALABAT ORDER CREATION STYLE)
with tab_dispatch:
    st.markdown("##### Create Stock Dispatch")
    other_branches = [b for b in BRANCHES if b != selected_branch]
    to_loc = st.selectbox("Transfer Destination:", other_branches)
    issuer = st.text_input("Dispatched by (Your Name):", placeholder="Staff Name")
    items_input = st.text_area(
        "Add Items & Quantity:", 
        placeholder="kamfaroosh 10\nRoyal Halwa 5 kg\nVIP Baklava 2 boxes",
        height=120
    )
    
    if st.button("Place Transfer Order ⚡", use_container_width=True):
        if not issuer.strip():
            st.warning("Please enter your name.")
        elif not items_input.strip():
            st.warning("Please enter items to transfer.")
        else:
            with st.spinner("Processing Dispatch Order..."):
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
        <div class="talabat-card" style="border-left: 4px solid #FF5A00; margin-top: 14px;">
            <div style="font-size: 14.5px; font-weight: 800; color: #FF7A30; margin-bottom: 2px;">
                ORDER DISPATCHED SUCCESSFULLY
            </div>
            <div style="font-size: 13px; color: #F8FAFC;">
                Voucher <b>ST {253600 + last['id']}</b> sent to <b>{last['to_branch']}</b>.
            </div>
            <div style="font-size: 11.5px; color: #94A3B8; margin-top: 4px;">
                Issued by: {last['sender_name']} | Time: {last['date_str']} {last['time_str']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 2. INCOMING (TALABAT LIVE ORDER TRACKING STYLE)
with tab_inbox:
    st.markdown(f"##### Incoming Deliveries ({selected_branch})")
    all_data = load_data()
    incoming_pending = [t for t in reversed(all_data) if t["to_branch"] == selected_branch and t["status"] == "IN TRANSIT"]
    
    if not incoming_pending:
        st.info(f"No incoming deliveries arriving at {selected_branch}.")
    else:
        st.markdown(f"""
        <div class="talabat-card" style="border-left: 4px solid #FF5A00; padding: 12px 16px;">
            <span style="font-weight: 700; color: #FF7A30; font-size: 13px;">🔔 Live Queue: {len(incoming_pending)} incoming order(s) arriving for acceptance.</span>
        </div>
        """, unsafe_allow_html=True)

        for trx in incoming_pending:
            v_no = f"ST {253600 + trx['id']}"
            st.markdown(f"""
            <div class="talabat-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 15px; font-weight: 800; color: #FFFFFF;">Order #{v_no}</span>
                    <span class="chip-transit"><span class="live-dot"></span> ON THE WAY</span>
                </div>
                <div style="font-size: 13px; color: #CBD5E1;">
                    From: <b>{trx['from_branch']}</b> | Sent by: <b>{trx['sender_name']}</b>
                </div>
                <div style="font-size: 11.5px; color: #94A3B8; margin-top: 2px;">
                    Dispatched: {trx['date_str']} at {trx['time_str']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Order Items:**")
            for it in trx['items_list']:
                st.caption(f"• **{it.get('desc')}** — Qty: **{it.get('qty', 'N/A')}**")
                
            rec_name = st.text_input("Receiver Name:", key=f"rec_sig_{trx['id']}", placeholder="Your name")
            
            if st.button(f"Accept & Confirm Delivery #{trx['id']}", key=f"btn_accept_{trx['id']}", use_container_width=True):
                if not rec_name.strip():
                    st.warning("Please type your name to accept delivery.")
                else:
                    for item in all_data:
                        if item["id"] == trx["id"]:
                            item["status"] = "RECEIVED"
                            item["receiver_name"] = rec_name.strip()
                            item["received_date"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                            break
                    save_data(all_data)
                    st.session_state[f"accepted_{trx['id']}"] = True
                    st.success(f"Order #{trx['id']} Received & Verified!")
                    st.rerun()

            if st.session_state.get(f"accepted_{trx['id']}", False) or trx["status"] == "RECEIVED":
                st.success("Delivery Confirmed! Download invoice below:")
                pdf_bytes = create_voucher_pdf(trx)
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📄 Download PDF Voucher",
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
                        f"*Order No:* {v_no}\n"
                        f"*Date:* {trx['date_str']}\n"
                        f"*From:* {trx['from_branch']}\n"
                        f"*To:* {trx['to_branch']}\n"
                        f"*Issued by:* {trx['sender_name']}\n"
                        f"*Accepted by:* {trx['receiver_name']}\n\n"
                        f"*Items:*\n{wa_items}\n\n"
                        f"_Order Verified & Received Successfully._"
                    )
                    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-talabat-btn">📲 Share on WhatsApp</a>', unsafe_allow_html=True)

            st.divider()

# 3. HISTORY
with tab_history:
    st.markdown(f"##### Order History ({selected_branch})")
    all_data = load_data()
    branch_history = [t for t in reversed(all_data) if t["from_branch"] == selected_branch or t["to_branch"] == selected_branch]
    
    if not branch_history:
        st.info(f"No order history for {selected_branch}.")
    else:
        for trx in branch_history:
            v_no = f"ST {253600 + trx['id']}"
            is_out = (trx["from_branch"] == selected_branch)
            direction = f"Outbound to {trx['to_branch']}" if is_out else f"Inbound from {trx['from_branch']}"
            badge_html = '<span class="chip-delivered">DELIVERED</span>' if trx['status'] == "RECEIVED" else '<span class="chip-transit">ON THE WAY</span>'
            
            st.markdown(f"""
            <div class="talabat-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 15px; font-weight: 800; color: #FFFFFF;">#{v_no}</span>
                    {badge_html}
                </div>
                <div style="font-size: 13px; color: #FF7A30; font-weight: 700;">{direction}</div>
                <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">Issued: {trx['sender_name']} | Received: {trx.get('receiver_name', 'Pending')}</div>
                <div style="font-size: 11px; color: #64748B; margin-top: 2px;">Date: {trx['date_str']} {trx['time_str']}</div>
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
                        f"*Order No:* {v_no}\n"
                        f"*Date:* {trx['date_str']}\n"
                        f"*From:* {trx['from_branch']}\n"
                        f"*To:* {trx['to_branch']}\n"
                        f"*Issued by:* {trx['sender_name']}\n"
                        f"*Accepted by:* {trx['receiver_name']}\n\n"
                        f"*Items:*\n{wa_items}\n\n"
                        f"_Order Verified & Delivered._"
                    )
                    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-talabat-btn">📲 WhatsApp</a>', unsafe_allow_html=True)
            st.divider()

    if branch_history:
        st.markdown("""
        <div class="talabat-card" style="border: 1px solid rgba(239, 68, 68, 0.3); margin-top: 20px;">
            <div style="font-size: 13.5px; font-weight: 700; color: #F87171;">Clear Orders History</div>
            <div style="font-size: 12px; color: #94A3B8; margin-top: 2px;">Permanently delete transfer records.</div>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_del = st.checkbox(f"Confirm deletion for {selected_branch}", key="confirm_del_box")
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            if st.button(f"Clear {selected_branch} Only", use_container_width=True):
                if not confirm_del:
                    st.warning("Confirmation required.")
                else:
                    updated_data = [t for t in all_data if t["from_branch"] != selected_branch and t["to_branch"] != selected_branch]
                    save_data(updated_data)
                    st.success(f"History cleared for {selected_branch}!")
                    st.rerun()
                    
        with col_c2:
            if st.button("Clear All Orders", use_container_width=True):
                if not confirm_del:
                    st.warning("Confirmation required.")
                else:
                    save_data([])
                    st.success("All data cleared!")
                    st.rerun()
