import streamlit as st
import requests
import pandas as pd  # Add this for data manipulation
import re 
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
# --- STEP 3: WEBHOOK COMMUNICATION & ANALYTICS ---
if st.button("Search Stations"):
    if not query:
        st.warning("Please enter a search query!")
    else:
        # YOUR n8n PRODUCTION URL (Update this when deploying!)
        WEBHOOK_URL = "https://vaishnavireddya11.app.n8n.cloud/webhook-test/lpg-finder" 
        
        payload = {
            "latitude": user_lat,
            "longitude": user_lon,
            "query": query,
            "budget": budget
        }

        with st.spinner("Agent is analyzing gas stations and market data..."):
            try:
                # 1. SEND DATA TO n8n
                response = requests.post(WEBHOOK_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list): result = result[0]
                    
                    # Get the AI text
                    answer = result.get('output') or result.get('text') or ""
                    
                    # --- THE JSON EXTRACTOR ---
                    # This looks for the ```json block we added to the prompt
                    match = re.search(r'```json\n(.*?)\n```', answer, re.DOTALL)
                    
                    if match:
                        try:
                            json_data = json.loads(match.group(1))
                            df = pd.DataFrame(json_data['results'])
                            
                            st.markdown("---")
                            st.markdown("### 📊 Market Analytics")
                            c1, c2 = st.columns(2)
                            with c1:
                                st.write("**Brand Distribution**")
                                st.bar_chart(df['brand'].value_counts())
                            with c2:
                                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                                st.metric("Avg Price", f"₹{df['price'].mean():.2f}")
                                st.metric("Stations Found", len(df))
                                
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button("📥 Download Analysis CSV", csv, "lpg_report.csv", "text/csv")
                            
                            # Clean the 'answer' so the raw JSON doesn't show to the user
                            answer = answer.split("```json")[0]
                        except Exception as e:
                            st.warning("Found data, but it was formatted incorrectly.")
                    else:
                        st.warning("Analytics table missing. Ensure the n8n System Message has the JSON block.")

                    st.markdown("---")
                    st.markdown("### 🤖 Agent Advice")
                    st.info(answer)

            except Exception as e:
                # MANDATORY EXCEPT BLOCK
                st.error(f"Critical Error: {e}")