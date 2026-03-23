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
                    
                    # Handle n8n returning a list or a dict
                    if isinstance(result, list):
                        result = result[0]

                    # --- 2. ANALYTICS & VISUALIZATION ---
                    # This looks for the 'results' list we added in the n8n Code node
                    raw_data = result.get('results')
                    
                    if raw_data:
                        df = pd.DataFrame(raw_data)
                        
                        st.markdown("---")
                        st.markdown("### 📊 Market Analytics")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Brand Distribution**")
                            # Simple Pie Chart using Streamlit's built-in tool
                            brand_counts = df['brand'].value_counts()
                            st.write(brand_counts) # Shows a small table
                            st.divider()
                            # Optional: Use a bar chart if Pie feels too complex to code quickly
                            st.bar_chart(brand_counts)

                        with col2:
                            st.write("**Quick Insights**")
                            avg_price = pd.to_numeric(df['price']).mean()
                            st.metric("Avg Price", f"₹{avg_price:.2f}")
                            st.metric("Total Options", len(df))

                        # --- 3. DATA DOWNLOAD ---
                        csv = df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Detailed Analysis (CSV)",
                            data=csv,
                            file_name='lpg_analysis.csv',
                            mime='text/csv',
                        )

                    # --- 4. AI AGENT ADVICE ---
                    st.markdown("---")
                    st.markdown("### 🤖 Agent Advice")
                    answer = result.get('output') or result.get('text')
                    st.info(answer if answer else "Analysis complete, but no text response generated.")

                else:
                    st.error(f"n8n returned an error: {response.status_code}")

            except Exception as e:
                # THIS IS THE BLOCK THAT PREVENTS THE SYNTAX ERROR
                st.error(f"An error occurred during processing: {e}")
                st.info("Check if your n8n workflow is 'Executing' and receiving data.")