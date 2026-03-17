import streamlit as st
import requests

st.set_page_config(page_title="Autonomous Cold Outreach System", page_icon="📧", layout="wide")

st.title("Autonomous Cold Outreach System 🚀")
st.markdown("Generate hyper-personalized, high-conversion cold emails using AI agents.")

# Config
API_URL = "http://localhost:8000/generate_email"

# Input Form
with st.form("input_form"):
    target_url = st.text_input("Target Company URL", placeholder="https://example.com")
    user_offering = st.text_area("Your Offering / Services", placeholder="e.g. We provide custom AI agents for B2B lead generation...")
    submitted = st.form_submit_button("Generate Email")

if submitted:
    if not target_url or not user_offering:
        st.warning("Please provide both a URL and your offering.")
    else:
        with st.spinner("Agents are researching and strategizing..."):
            try:
                response = requests.post(API_URL, json={
                    "url": target_url,
                    "user_offering": user_offering
                })
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Email generated successfully!")
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.subheader("Final Email")
                        st.info(data.get("email", "No email generated."))
                        
                        st.subheader("Strategic Hook")
                        st.write(data.get("hook", "No hook generated."))
                        
                    with col2:
                        st.subheader("Company DNA (Extracted)")
                        dna = data.get("company_dna", {})
                        if dna:
                            st.markdown(f"**Value Proposition:**\n{dna.get('value_proposition')}")
                            st.markdown(f"**Target Audience:**\n{dna.get('target_audience')}")
                            st.markdown(f"**Recent News/Updates:**\n{dna.get('recent_news')}")
                        else:
                            st.write("No DNA extracted.")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"Failed to connect to backend: {str(e)}")
