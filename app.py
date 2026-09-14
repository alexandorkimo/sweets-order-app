import streamlit as st
from google import genai
from fpdf import FPDF
import datetime
import urllib.parse

st.set_page_config(
    page_title="Inter-Branch Transfer Hub",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom High-End Cyberpunk Dark Style
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
        height: 80px;
        perspective: 900px;
        margin: 5px 0 15px 0;
    }
    
    .cube-container {
        width: 45px;
        height: 45px;
        transform-style: preserve-3d;
        animation: spin3D 8s infinite linear;
    }
    
    .cube-face {
        position: absolute;
        width: 45px;
        height: 45px;
        background: rgba(14, 165, 233, 0.12);
        border: 1.5px solid #38BDF8;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
    }
    
    .face-front  { transform: rotateY(0deg) translateZ(22.5px); }
    .face-back   { transform: rotateY(180deg) translateZ(22.5px); }
    .face-right  { transform: rotateY(90deg) translateZ(22.5px); }
    .face-left   { transform: rotateY(-90deg) translateZ(22.5px); }
    .face-top    { transform: rotateX(90deg) translateZ(22.5px); }
    .face-bottom { transform: rotateX(-90deg) translateZ(22.5px); }
    
    @keyframes spin3D {
        0% { transform: rotateX(0deg) rotateY(0deg) rotateZ(0deg); }
        100% { transform: rotateX(360deg) rotateY(360deg) rotateZ(360deg); }
    }

    .brand-banner {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(14px);
        padding: 18px;
        border-radius: 16px;
        text-align: center;
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow: 0 0 25px rgba(14, 165, 233, 0.15);
        margin-bottom: 20px;
    }
    
    .brand-title {
        font-size: 20px;
        font-weight: 700;
        color: #FFFFFF;
        text-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
        margin: 0;
    }
    
    .brand-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #38BDF8;
        margin-top: 4px;
        letter-spacing: 2px;
    }

    .transfer-card {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(12px);
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    .badge-in-transit { 
        background: rgba(245, 158, 11, 0.15); 
        color: #FBBF24; 
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-family: 'JetBrains Mono';
    }
    
    .badge-received { 
        background: rgba(34, 197, 94, 0.15); 
        color: #4ADE80; 
        border: 1px solid rgba(34, 197, 94, 0.4);
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-family: 'JetBrains Mono';
    }

    .wa-btn {
        display: inline-block;
        background: #25D366;
        color: white !important;
        padding: 9px 14px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        font-size: 13px;
        text-align: center;
        width: 100%;
        margin-top: 6px;
        box-shadow: 0 0 12px rgba(37, 211, 102, 0.3);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Helper Function: Generate PDF Transfer Note
def generate_pdf(transfer_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    
    # Title
    pdf.cell(0, 10, "INTER-BRANCH STOCK TRANSFER NOTE", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Official Dispatch & Receipt Confirmation", ln=True, align="C")
    pdf.ln(5)
    
    # Metadata Box
    pdf.set_fill_color(240, 244, 248)
    pdf.rect(10, 32, 190, 42, "F")
    
    pdf.set_xy(12, 34)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 6, "Transfer Note ID:")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(60, 6, f"TRX-{transfer_data['id']:04d}")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(30, 6, "Date & Time:")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 6, f"{transfer_data['timestamp']}", ln=True)
    
    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 6, "Source Branch:")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(60, 6, f"{transfer_data['from_branch']}")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(30, 6, "Dispatched By:")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 6, f"{transfer_data['sender_name']}", ln=True)

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 6, "Destination Branch:")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(60, 6, f"{transfer_data['to_branch']}")
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(30, 6, "Received By:")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(50, 6, f"{transfer_data.get('receiver_name', 'N/A')}", ln=True)

    pdf.set_x(12)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(40, 6, "Transfer Status:")
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(60, 6, f"{transfer_data['status']}", ln=True)

    pdf.ln(12)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Itemized Inventory Manifest:", ln=True)
    
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, transfer_data['parsed_items'])
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.cell(0, 6, "System-verified transfer confirmation token. Valid across logistics inventory records.", ln=True, align="C")
    
    return bytes(pdf.output())

# API Key Config
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key:", type="password")

if "transfers" not in st.session_state:
    st.session_state.transfers = []

# 3D Animation Header
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

st.markdown("""
<div class="brand-banner">
    <h1 class="brand-title">INTER-BRANCH TRANSFER NETWORK</h1>
    <div class="brand-subtitle">VERIFIED RECEIPT & DISPATCH PROTOCOL</div>
</div>
""", unsafe_allow_html=True)

mode = st.radio("SELECT MODE:", ["📤 Dispatch Item (Source)", "📥 Receive Item (Destination)"], horizontal=True)
st.write("")

BRANCHES = ["Manama Branch", "Riffa Branch", "Muharraq Branch", "Hamad Town Branch", "Central Warehouse"]

if mode == "📤 Dispatch Item (Source)":
    st.markdown("##### 🚀 INITIATE STOCK TRANSFER")
    
    c1, c2 = st.columns(2)
    with c1:
        from_b = st.selectbox("Dispatch From (Source):", BRANCHES, index=0)
    with c2:
        to_b = st.selectbox("Transfer To (Destination):", BRANCHES, index=1)
        
    sender = st.text_input("Sender Incharge Name:", placeholder="Staff / Manager Name")
    items_raw = st.text_area(
        "Transfer Items & Quantity:",
        placeholder="e.g., 5kg Special Halwa, 10 trays Baklava, 3kg Kaju Peda...",
        height=110
    )
    
    if st.button("⚡ INITIATE TRANSFER DISPATCH", use_container_width=True):
        if not api_key:
            st.error("API Key missing! Add GEMINI_API_KEY in Secrets.")
        elif from_b == to_b:
            st.warning("Source and Destination branches cannot be the same.")
        elif not sender.strip():
            st.warning("Please specify sender incharge name.")
        elif not items_raw.strip():
            st.warning("Please provide transfer items.")
        else:
            with st.spinner("AI Generating Verified Transfer Manifest..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        "You are an inter-branch logistics assistant. Parse this inventory transfer into a neat, "
                        "itemized list with exact quantities and units:\n\n" + items_raw
                    )
                    res = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt
                    )
                    
                    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                    new_trx = {
                        "id": len(st.session_state.transfers) + 1,
                        "from_branch": from_b,
                        "to_branch": to_b,
                        "sender_name": sender,
                        "receiver_name": "Pending Receipt",
                        "raw_items": items_raw,
                        "parsed_items": res.text,
                        "status": "IN TRANSIT",
                        "timestamp": now_str
                    }
                    st.session_state.transfers.append(new_trx)
                    st.success(f"Transfer TRX-{new_trx['id']:04d} dispatched to {to_b}!")
                except Exception as e:
                    st.error(f"Error: {e}")

elif mode == "📥 Receive Item (Destination)":
    st.markdown("##### 📦 INCOMING TRANSFER INVENTORY")
    
    dest_filter = st.selectbox("Active Branch Terminal:", BRANCHES)
    
    matched = [t for t in reversed(st.session_state.transfers) if t['to_branch'] == dest_filter]
    
    if not matched:
        st.info(f"No active transfer records for {dest_filter}.")
    else:
        for trx in matched:
            status = trx["status"]
            badge_html = (
                f'<span class="badge-in-transit">⏳ {status}</span>' 
                if status == "IN TRANSIT" 
                else f'<span class="badge-received">✅ {status}</span>'
            )
            
            st.markdown(f"""
            <div class="transfer-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; color: #38BDF8;">TRX-{trx['id']:04d}: From {trx['from_branch']}</span>
                    {badge_html}
                </div>
                <div style="font-size: 12px; color: #94A3B8; margin-bottom: 8px; font-family: 'JetBrains Mono';">
                    Dispatched by: <b>{trx['sender_name']}</b> | Sent on: {trx['timestamp']}
                </div>
                <div style="background: rgba(3, 7, 18, 0.7); border-radius: 8px; padding: 10px; margin-bottom: 10px; font-size: 13px; border: 1px solid rgba(255, 255, 255, 0.08); color: #F1F5F9;">
                    {trx['parsed_items']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if status == "IN TRANSIT":
                r_name = st.text_input(f"Your Name (Receiver at {dest_filter}):", key=f"rname_{trx['id']}")
                if st.button(f"✅ Confirm & Accept Stock #{trx['id']}", key=f"btn_rec_{trx['id']}", use_container_width=True):
                    if not r_name.strip():
                        st.warning("Please type your name to confirm receipt.")
                    else:
                        trx["status"] = "RECEIVED"
                        trx["receiver_name"] = r_name
                        trx["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                        st.success(f"Stock Received & Verified by {r_name}!")
                        st.rerun()
                        
            elif status == "RECEIVED":
                st.write(f"👤 **Received & Signed by:** {trx.get('receiver_name')}")
                
                # Create Transfer Note PDF
                pdf_bytes = generate_pdf(trx)
                file_name = f"Transfer_Note_TRX_{trx['id']:04d}.pdf"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="📄 Download PDF Note",
                        data=pdf_bytes,
                        file_name=file_name,
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                with col2:
                    # WhatsApp Direct Share Link
                    clean_items = trx['parsed_items'].replace('*', '').strip()
                    wa_message = (
                        f"*STOCK TRANSFER CONFIRMATION*\n\n"
                        f"*Ref:* TRX-{trx['id']:04d}\n"
                        f"*From:* {trx['from_branch']}\n"
                        f"*To:* {trx['to_branch']}\n"
                        f"*Received By:* {trx['receiver_name']}\n"
                        f"*Status:* Received & Verified ✅\n\n"
                        f"*Items:*\n{clean_items}\n\n"
                        f"_PDF Transfer Note Generated_"
                    )
                    encoded_msg = urllib.parse.quote(wa_message)
                    wa_url = f"https://api.whatsapp.com/send?text={encoded_msg}"
                    
                    st.markdown(f'<a href="{wa_url}" target="_blank" class="wa-btn">📲 Share on WhatsApp</a>', unsafe_allow_html=True)
            st.divider()
        
