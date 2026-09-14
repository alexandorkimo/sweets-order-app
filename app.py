import streamlit as st
from google import genai

# പേജ് കോൺഫിഗറേഷൻ (മൊബൈൽ ഫ്രണ്ട്‌ലി ലേഔട്ട്)
st.set_page_config(page_title="Sweets Order App", page_icon="🍬", layout="centered")

# API Key ക്രമീകരണം (Secrets അല്ലെങ്കിൽ ഇൻപുട്ട് വഴി)
api_key = st.secrets.get("GEMINI_API_KEY", "")
if not api_key:
    api_key = st.sidebar.text_input("Gemini API Key നൽകുക:", type="password")

if "orders" not in st.session_state:
    st.session_state.orders = []

st.title("🍬 Sweets Shop ➡️ Factory")

# റോൾ തിരഞ്ഞെടുക്കുക
role = st.radio("നിങ്ങൾ ആരാണ്?", ["🏪 Sweets Shop", "🏭 Factory"], horizontal=True)
st.divider()

if role == "🏪 Sweets Shop":
    st.subheader("പുതിയ ഓർഡർ നൽകുക")
    st.caption("വാട്സാപ്പിൽ അയക്കുന്നത് പോലെ സാധനങ്ങളുടെ പേരും അളവും ടൈപ്പ് ചെയ്യുക:")
    
    order_input = st.text_area(
        "Order Details", 
        placeholder="Eg: Ladoo 5 kg, Halwa 10 box, Peda 2 kg nalaikk 10 am-nu venam...",
        height=120
    )
    
    if st.button("🚀 Send to Factory", use_container_width=True):
        if not api_key:
            st.error("Gemini API Key ലഭ്യമല്ല!")
        elif not order_input.strip():
            st.warning("ദയവായി ഓർഡർ ടൈപ്പ് ചെയ്യുക.")
        else:
            with st.spinner("AI ഓർഡർ പരിശോധിക്കുന്നു..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = (
                        "Convert the following shop order into a clean, itemized checklist with quantities, units, and special notes. "
                        "Keep it short and clear:\n\n" + order_input
                    )
                    response = client.models.generate_content(
    model='gemini-1.5-flash',
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
                  
