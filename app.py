import streamlit as st
import requests
import pandas as pd  # Add this for data manipulation
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
                    
                    # --- THE SUPER-SEARCHER ---
                    # This looks for 'results' in every common n8n location
                    raw_data = (
                        result.get('results') or 
                        result.get('body', {}).get('results') or 
                        result.get('data', {}).get('results') or
                        result.get('input', {}).get('results') # In case the AI node nests it
                    )
                    
                    if raw_data:
                        df = pd.DataFrame(raw_data)
                        st.markdown("---")
                        st.markdown("### 📊 Market Analytics")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Brand Distribution**")
                            brand_counts = df['brand'].value_counts()
                            st.bar_chart(brand_counts)
                        
                        with col2:
                            # Use pd.to_numeric to avoid errors if price is a string
                            df['price'] = pd.to_numeric(df['price'], errors='coerce')
                            avg_p = df['price'].mean()
                            st.metric("Avg Price", f"₹{avg_p:.2f}")
                            st.metric("Options Found", len(df))

                        # Download button
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download Analysis CSV", csv, "lpg_report.csv", "text/csv")
                    else:
                        st.warning("Connected, but the Analytics table is missing. Check AI Node settings.")

                    # --- AI ADVICE ---
                    st.markdown("---")
                    st.markdown("### 🤖 Agent Advice")
                    answer = (result.get('output') or 
                             result.get('body', {}).get('output') or 
                             result.get('text'))
                    st.info(answer if answer else "No text response found.")

                else:
                    st.error(f"Error: {response.status_code}")

            except Exception as e:
                # MANDATORY EXCEPT BLOCK
                st.error(f"Critical Error: {e}")