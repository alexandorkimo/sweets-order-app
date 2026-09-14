import streamlit as st
from google import genai
from fpdf import FPDF
import datetime
import urllib.parse
import json
import os

# Page Setup
st.set_page_config(
    page_title="STOCK TRANSFER",
    page_icon="📋",
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

# Ultra-Clean Dark HD Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@600&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    #MainMenu, header, footer { visibility: hidden; }
    
    .stApp {
        background-color: #0B0F19;
        color: #F3F4F6;
    }
    
    .header-box {
        background: #111827;
        border: 1px solid #1F2937;
        border-left: 4px solid #D97706;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 16px;
    }
    .comp-name {
        font-size: 11px;
        font-weight: 700;
        color: #F59E0B;
        letter-spacing: 1px;
    }
    .app-title {
        font-size: 22px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 2px 0 6px 0;
    }
    .branch-tag {
        display: inline-block;
        background: #1E293B;
        border: 1px solid #38BDF8;
        color: #38BDF8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 15px;
    }
    
    .order-card {
        background: #111827;
        border: 1px solid #1F2937;
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 12px;
    }
    .badge-transit {
        background: rgba(245, 158, 11, 0.15);
        color: #FBBF24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    .badge-received {
        background: rgba(34, 197, 94, 0.15);
        color: #4ADE80;
        border: 1px solid rgba(34, 197, 94, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
    }
    
    .wa-btn {
        display: block;
        background: #25D366;
        color: white !important;
        text-align: center;
        padding: 10px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 700;
        font-size: 13px;
        margin-top: 6px;
    }
    
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background-color: #030712 !important;
        color: #FFFFFF !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 700;
        height: 44px;
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

# Top Header
st.markdown(f"""
<div class="header-box">
    <div class="comp-name">JAMAL SHOWAITER SWEETS CO. W.L.L.</div>
    <div class="app-title">STOCK TRANSFER</div>
    <div class="branch-tag">LOCATION: {selected_branch}</div>
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
    st.markdown("##### 📤 Create Stock Transfer")
    other_branches = [b for b in BRANCHES if b != selected_branch]
    to_loc = st.selectbox("Transfer To (Destination):", other_branches)
    issuer = st.text_input("Issued by (Staff Name):", placeholder="Your Name")
    items_input = st.text_area(
        "Items and Quantities:", 
        placeholder="e.g.:\nHalwa Red King - 10 kg\nMixed Baklava VIP - 5 boxes\nKaju Katli - 2 kg",
        height=120
    )
    
    if st.button("🚀 Issue Transfer Note", use_container_width=True, type="primary"):
        if not issuer.strip():
            st.warning("Please type your name in 'Issued by'.")
        elif not items_input.strip():
            st.warning("Please enter items to transfer.")
        else:
            with st.spinner("Creating Transfer Note..."):
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
                        clean_text = res.text.strip().replace("```json", "").replace("```", "").strip()
                        parsed_list = json.loads(clean_text)
                    except Exception:
                        parsed_list = []
                
                if not parsed_list:
                    lines = [l.strip() for l in items_input.split("\n") if l.strip()]
                    parsed_list = [{"desc": l, "qty": "", "sp": "", "up": "", "amt": ""} for l in lines]
                
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
                    "status": "IN TRANSIT", # Strictly Pending until manually accepted
                    "date_str": now.strftime("%d/%m/%Y"),
                    "time_str": now.strftime("%H:%M")
                }
                all_data.append(new_trx)
                save_data(all_data)
                st.success(f"Voucher ST {253600 + new_trx['id']} created and dispatched to {to_loc}!")
                st.rerun()

# 2. INCOMING TAB (MANUAL ACCEPT ONLY + IMMEDIATE PDF RECEIPT)
with tab_inbox:
    st.markdown(f"##### 📥 Incoming Stock for {selected_branch}")
    all_data = load_data()
    
    # Fetch pending incoming items strictly for this branch
    incoming_pending = [t for t in reversed(all_data) if t["to_branch"] == selected_branch and t["status"] == "IN TRANSIT"]
    
    if not incoming_pending:
        st.info(f"No pending incoming stock for {selected_branch}.")
    else:
        for trx in incoming_pending:
            v_no = f"ST {253600 + trx['id']}"
            st.markdown(f"""
            <div class="order-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b>No: {v_no}</b>
                    <span class="badge-transit">⏳ PENDING ACCEPTANCE</span>
                </div>
                <div style="font-size: 13px; color: #9CA3AF; margin-top: 4px;">
                    From: <b>{trx['from_branch']}</b> | Sent by: <b>{trx['sender_name']}</b>
                </div>
                <div style="font-size: 11px; color: #6B7280;">
                    Dispatched: {trx['date_str']} at {trx['time_str']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Items Manifest:**")
            for it in trx['items_list']:
                st.caption(f"• **{it.get('desc')}** — Qty: {it.get('qty', 'N/A')}")
                
            rec_name = st.text_input("Approved by (Receiver Signature):", key=f"rec_sig_{trx['id']}", placeholder="Type your name here...")
            
            # Manual Accept button
            if st.button(f"✅ Accept & Sign Voucher #{trx['id']}", key=f"btn_accept_{trx['id']}", use_container_width=True, type="primary"):
                if not rec_name.strip():
                    st.warning("⚠️ Signature required: Please enter your name in 'Approved by' to accept stock.")
                else:
                    for item in all_data:
                        if item["id"] == trx["id"]:
                            item["status"] = "RECEIVED"
                            item["receiver_name"] = rec_name.strip()
                            item["received_date"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                            break
                    save_data(all_data)
                    st.session_state[f"accepted_{trx['id']}"] = True
                    st.success(f"Stock Voucher #{trx['id']} successfully accepted and verified by {rec_name}!")
                    st.rerun()

            # Show Instant Download & WhatsApp immediately after accept
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
                    wa_items = "\n".join([f"- {it.get('desc')} ({it.get('qty')})" for it in trx['items_list']])
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
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 Share on WhatsApp</a>', unsafe_allow_html=True)

            st.divider()

# 3. HISTORY TAB
with tab_history:
    st.markdown(f"##### 📜 History for {selected_branch}")
    all_data = load_data()
    branch_history = [t for t in reversed(all_data) if t["from_branch"] == selected_branch or t["to_branch"] == selected_branch]
    
    if not branch_history:
        st.info(f"No history records found for {selected_branch}.")
    else:
        for trx in branch_history:
            v_no = f"ST {253600 + trx['id']}"
            is_out = (trx["from_branch"] == selected_branch)
            direction = f"📤 Sent to {trx['to_branch']}" if is_out else f"📥 Received from {trx['from_branch']}"
            badge_html = '<span class="badge-received">✅ RECEIVED</span>' if trx['status'] == "RECEIVED" else '<span class="badge-transit">⏳ IN TRANSIT</span>'
            
            st.markdown(f"""
            <div class="order-card">
                <div style="display: flex; justify-content: space-between;">
                    <b>No: {v_no}</b>
                    {badge_html}
                </div>
                <div style="font-size: 13px; color: #38BDF8; margin-top: 4px;">{direction}</div>
                <div style="font-size: 12px; color: #9CA3AF;">Issued: {trx['sender_name']} | Approved: {trx.get('receiver_name', 'Pending')}</div>
                <div style="font-size: 11px; color: #6B7280;">Date: {trx['date_str']} {trx['time_str']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # PDF & WhatsApp buttons for accepted transfers
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
                    wa_items = "\n".join([f"- {it.get('desc')} ({it.get('qty')})" for it in trx['items_list']])
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
                        f"_Transfer Verified & Received._"
                    )
                    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-btn">📲 WhatsApp</a>', unsafe_allow_html=True)
            st.divider()
                        
