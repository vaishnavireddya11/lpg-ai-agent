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
                response = requests.post(WEBHOOK_URL, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list): result = result[0]

                    # --- 1. THE ANALYTICS CHECK ---
                    raw_data = result.get('results')
                    
                    if raw_data:
                        df = pd.DataFrame(raw_data)
                        st.markdown("---")
                        st.markdown("### 📊 Market Analytics")
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write("**Brand Distribution**")
                            # This creates a bar chart if Pie Chart has library issues
                            brand_counts = df['brand'].value_counts()
                            st.bar_chart(brand_counts)
                        
                        with c2:
                            st.write("**Quick Insights**")
                            avg_p = pd.to_numeric(df['price']).mean()
                            st.metric("Avg Price", f"₹{avg_p:.2f}")
                            st.metric("Stations Found", len(df))

                        # --- 2. DOWNLOAD BUTTON ---
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 Download Detailed CSV", csv, "lpg_report.csv", "text/csv")
                    else:
                        # DEBUG: This helps you see why the chart is missing
                        st.warning("n8n connected, but 'results' list was missing for the charts.")

                    # --- 3. AI AGENT ADVICE ---
                    st.markdown("---")
                    st.markdown("### 🤖 Agent Advice")
                    answer = result.get('output') or result.get('text')
                    st.info(answer if answer else "No text response.")

                else:
                    st.error(f"Error: {response.status_code}")

            except Exception as e:
                st.error(f"Processing Error: {e}")