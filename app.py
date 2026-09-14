import streamlit as st
from google import genai
from fpdf import FPDF
import datetime
import urllib.parse
import json
import os
import re

st.set_page_config(
    page_title="Jamal Showaiter Enterprise",
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

# NATIVE ANDROID MATERIAL ENTERPRISE DARK THEME
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Roboto+Mono:wght@500;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        -webkit-font-smoothing: antialiased;
    }
    
    #MainMenu, header, footer, .stDeployButton { 
        visibility: hidden !important; 
        display: none !important; 
    }
    
    /* Native App Dark Slate Canvas */
    .stApp {
        background-color: #0B0E14 !important;
        color: #E6EDF3 !important;
    }

    /* Android Native Top App Bar */
    .appbar-container {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        gap: 6px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .corp-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #D29922;
        text-transform: uppercase;
        margin: 0;
    }

    .app-headline {
        font-size: 20px;
        font-weight: 800;
        letter-spacing: -0.4px;
        color: #FFFFFF;
        margin: 0;
    }

    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #21262D;
        border: 1px solid #30363D;
        color: #58A6FF;
        font-family: 'Roboto Mono', monospace !important;
        font-size: 11.5px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 8px;
        align-self: flex-start;
        margin-top: 4px;
    }

    /* Material Surface Cards */
    .native-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }

    .native-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }

    .card-title {
        font-size: 15px;
        font-weight: 700;
        color: #F0F6FC;
        margin: 0;
    }

    .chip-transit {
        background: rgba(187, 128, 9, 0.15);
        color: #E3B341;
        border: 1px solid rgba(187, 128, 9, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace !important;
    }

    .chip-received {
        background: rgba(35, 134, 54, 0.15);
        color: #3FB950;
        border: 1px solid rgba(35, 134, 54, 0.4);
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        font-family: 'Roboto Mono', monospace !important;
    }

    /* Native Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #161B22;
        padding: 4px;
        border-radius: 12px;
        border: 1px solid #30363D;
        gap: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #8B949E;
        font-weight: 600;
        font-size: 13px;
        padding: 8px 14px;
        background: transparent !important;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background: #21262D !important;
        color: #F0F6FC !important;
        border: 1px solid #30363D !important;
    }

    /* Native Android Form Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div {
        background: #0D1117 !important;
        color: #C9D1D9 !important;
        border: 1px solid #30363D !important;
        border-radius: 10px !important;
        font-size: 13.5px !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #58A6FF !important;
    }

    /* Material Action Button */
    .stButton>button {
        background: #238636 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        height: 46px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }

    .wa-native-btn {
        display: block;
        background: #1F6FEB;
        color: #FFFFFF !important;
        text-align: center;
        padding: 10px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: 600;
        font-size: 13px;
        margin-top: 6px;
        border: 1px solid rgba(255, 255, 255, 0.1);
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

# Native Clean App Bar
st.markdown(f"""
<div class="appbar-container">
    <div class="corp-title">Jamal Showaiter Sweets Co. W.L.L.</div>
    <div class="app-headline">Stock Transfer System</div>
    <div class="status-chip">TERMINAL: {selected_branch}</div>
</div>
""", unsafe_allow_html=True)

if "b" not in query_params:
    new_branch = st.sidebar.selectbox("Active Terminal:", BRANCHES, index=BRANCHES.index(selected_branch))
    if new_branch != selected_branch:
        st.query_params["b"] = new_branch
        st.rerun()

tab_dispatch, tab_inbox, tab_history = st.tabs([
    "Dispatch", 
    "Incoming", 
    "History"
])

api_key = st.secrets.get("GEMINI_API_KEY", "")

# 1. DISPATCH
with tab_dispatch:
    st.markdown("##### New Stock Transfer")
    other_branches = [b for b in BRANCHES if b != selected_branch]
    to_loc = st.selectbox("Destination Location:", other_branches)
    issuer = st.text_input("Issued by (Staff Name):", placeholder="Name")
    items_input = st.text_area(
        "Item Manifest & Quantity:", 
        placeholder="kamfaroosh 10\nHalwa Red King 5 kg\nVIP Baklava 2 boxes",
        height=120
    )
    
    if st.button("Submit Stock Dispatch", use_container_width=True):
        if not issuer.strip():
            st.warning("Staff signature required in 'Issued by'.")
        elif not items_input.strip():
            st.warning("Please specify items to transfer.")
        else:
            with st.spinner("Processing Transfer..."):
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
        <div class="native-card" style="border-left: 4px solid #238636; margin-top: 14px;">
            <div style="font-size: 14px; font-weight: 700; color: #3FB950; margin-bottom: 2px;">
                TRANSFER INITIATED SUCCESSFULLY
            </div>
            <div style="font-size: 13px; color: #C9D1D9;">
                Voucher <b>ST {253600 + last['id']}</b> logged for <b>{last['to_branch']}</b>.
            </div>
            <div style="font-size: 11.5px; color: #8B949E; margin-top: 4px;">
                Issuer: {last['sender_name']} | Time: {last['date_str']} {last['time_str']}
            </div>
        </div>
        """, unsafe_allow_html=True)

# 2. INCOMING
with tab_inbox:
    st.markdown(f"##### Incoming Queue ({selected_branch})")
    all_data = load_data()
    incoming_pending = [t for t in reversed(all_data) if t["to_branch"] == selected_branch and t["status"] == "IN TRANSIT"]
    
    if not incoming_pending:
        st.info(f"No incoming transfers arriving at {selected_branch}.")
    else:
        st.markdown(f"""
        <div class="native-card" style="border-left: 4px solid #D29922; padding: 12px 16px;">
            <span style="font-weight: 600; color: #E3B341; font-size: 13px;">Pending Verification: {len(incoming_pending)} transfer(s) awaiting acceptance.</span>
        </div>
        """, unsafe_allow_html=True)

        for trx in incoming_pending:
            v_no = f"ST {253600 + trx['id']}"
            st.markdown(f"""
            <div class="native-card">
                <div class="native-card-header">
                    <span class="card-title">Voucher #{v_no}</span>
                    <span class="chip-transit">IN TRANSIT</span>
                </div>
                <div style="font-size: 13px; color: #C9D1D9;">
                    Origin: <b>{trx['from_branch']}</b> | Sender: <b>{trx['sender_name']}</b>
                </div>
                <div style="font-size: 11.5px; color: #8B949E; margin-top: 2px;">
                    Dispatched: {trx['date_str']} at {trx['time_str']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Manifest Details:**")
            for it in trx['items_list']:
                st.caption(f"• **{it.get('desc')}** — Qty: **{it.get('qty', 'N/A')}**")
                
            rec_name = st.text_input("Approved by (Receiver Name):", key=f"rec_sig_{trx['id']}", placeholder="Your name")
            
            if st.button(f"Confirm & Accept Stock #{trx['id']}", key=f"btn_accept_{trx['id']}", use_container_width=True):
                if not rec_name.strip():
                    st.warning("Receiver name required.")
                else:
                    for item in all_data:
                        if item["id"] == trx["id"]:
                            item["status"] = "RECEIVED"
                            item["receiver_name"] = rec_name.strip()
                            item["received_date"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                            break
                    save_data(all_data)
                    st.session_state[f"accepted_{trx['id']}"] = True
                    st.success(f"Voucher #{trx['id']} verified!")
                    st.rerun()

            if st.session_state.get(f"accepted_{trx['id']}", False) or trx["status"] == "RECEIVED":
                st.success("Verification complete. Document generated:")
                pdf_bytes = create_voucher_pdf(trx)
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="Download PDF Note",
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
                        f"*Items:*\n{wa_items}\n\n"
                        f"_Official Verified Transfer Note._"
                    )
                    wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(wa_msg)}"
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-native-btn">Share via WhatsApp</a>', unsafe_allow_html=True)

            st.divider()

# 3. HISTORY
with tab_history:
    st.markdown(f"##### Transfer Audit Registry ({selected_branch})")
    all_data = load_data()
    branch_history = [t for t in reversed(all_data) if t["from_branch"] == selected_branch or t["to_branch"] == selected_branch]
    
    if not branch_history:
        st.info(f"No records logged for terminal {selected_branch}.")
    else:
        for trx in branch_history:
            v_no = f"ST {253600 + trx['id']}"
            is_out = (trx["from_branch"] == selected_branch)
            direction = f"Outbound to {trx['to_branch']}" if is_out else f"Inbound from {trx['from_branch']}"
            badge_html = '<span class="chip-received">RECEIVED</span>' if trx['status'] == "RECEIVED" else '<span class="chip-transit">IN TRANSIT</span>'
            
            st.markdown(f"""
            <div class="native-card">
                <div class="native-card-header">
                    <span class="card-title">#{v_no}</span>
                    {badge_html}
                </div>
                <div style="font-size: 13px; color: #58A6FF; font-weight: 600;">{direction}</div>
                <div style="font-size: 12px; color: #8B949E; margin-top: 2px;">Issued: {trx['sender_name']} | Received: {trx.get('receiver_name', 'Pending')}</div>
                <div style="font-size: 11px; color: #6E7681; margin-top: 2px;">Date: {trx['date_str']} {trx['time_str']}</div>
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
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="wa-native-btn">Share via WhatsApp</a>', unsafe_allow_html=True)
            st.divider()

    if branch_history:
        st.markdown("""
        <div class="native-card" style="border: 1px solid rgba(248, 81, 73, 0.4); margin-top: 20px;">
            <div style="font-size: 13.5px; font-weight: 700; color: #F85149;">Data Maintenance</div>
            <div style="font-size: 12px; color: #8B949E; margin-top: 2px;">Permanently clear stored transfers.</div>
        </div>
        """, unsafe_allow_html=True)
        
        confirm_del = st.checkbox(f"Confirm record removal for {selected_branch}", key="confirm_del_box")
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
            if st.button("Clear All Data", use_container_width=True):
                if not confirm_del:
                    st.warning("Confirmation required.")
                else:
                    save_data([])
                    st.success("Global database reset!")
                    st.rerun()
