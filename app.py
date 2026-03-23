import streamlit as st
import requests
from streamlit_js_eval import get_geolocation

# --- UI CONFIG ---
st.set_page_config(page_title="LPG Smart Finder", page_icon="🔥")
st.title("🔥 AI LPG Station Finder")
st.markdown("Find the best gas prices and availability near you.")

# --- STEP 1: GET LOCATION ---
# This triggers a browser popup asking for GPS permission
loc = get_geolocation()

if loc:
    user_lat = loc['coords']['latitude']
    user_lon = loc['coords']['longitude']
    st.success(f"📍 Location identified: {user_lat}, {user_lon}")
else:
    st.info("Waiting for location permission... (Or enter manually below)")
    user_lat = st.number_input("Latitude", value=17.3850, format="%.4f")
    user_lon = st.number_input("Longitude", value=78.4867, format="%.4f")

# --- STEP 2: USER INPUTS ---
query = st.text_input("What are you looking for?", placeholder="e.g., Bharat Gas stations near me")
budget = st.number_input("What is your max budget (INR)?", min_value=500, max_value=2000, value=1000)

# --- STEP 3: WEBHOOK COMMUNICATION ---
if st.button("Search Stations"):
    if not query:
        st.warning("Please enter a search query!")
    else:
        # YOUR ACTUAL n8n CLOUD URL
        WEBHOOK_URL = "https://vaishnavireddya11.app.n8n.cloud/webhook/lpg-finder" 
        
        payload = {
            "latitude": user_lat,
            "longitude": user_lon,
            "query": query,
            "budget": budget
        }

        with st.spinner("Agent is analyzing gas stations..."):
            try:
                # 1. Send data to n8n
                response = requests.post(WEBHOOK_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    st.markdown("### 🤖 Agent Response:")
                    
                    # 2. Logic to find the AI's text in the n8n response
                    if isinstance(result, list) and len(result) > 0:
                        data = result[0]
                        # AI Agent usually sends 'output'. If not, we check 'text'
                        answer = data.get('output') or data.get('text') or str(data)
                        st.info(answer)
                    elif isinstance(result, dict):
                        answer = result.get('output') or result.get('text') or str(result)
                        st.info(answer)
                    else:
                        st.warning("The agent reached the end but didn't return text.")
                else:
                    st.error(f"n8n error {response.status_code}: {response.text}")

            except Exception as e:
                st.error(f"Connection failed! \n\n1. Check if n8n says 'Waiting for Webhook'\n2. Check your internet\n\nDetails: {e}")