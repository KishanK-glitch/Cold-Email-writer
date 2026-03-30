import os
import time
import uuid
import streamlit as st
import requests

st.set_page_config(page_title="Autonomous Cold Outreach System", page_icon="📧", layout="wide")

st.title("Autonomous Cold Outreach System 🚀")
st.markdown("Generate hyper-personalized, high-conversion cold emails using AI agents.")

# Config — set BACKEND_URL in Railway env vars to point to the backend service.
# Falls back to localhost for local development.
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

# Input Form
with st.form("input_form"):
    target_url = st.text_input("Target Company URL", placeholder="https://example.com")
    user_offering = st.text_area("Your Offering / Services", placeholder="e.g. We provide custom AI agents for B2B lead generation...")
    submitted = st.form_submit_button("Generate Email")

if submitted:
    if not target_url or not user_offering:
        st.warning("Please provide both a URL and your offering.")
    else:
        # ── Step 1: Submit the job ──────────────────────────────────────────
        try:
            job_payload = {
                "identifier_from_purchaser": str(uuid.uuid4()),
                "input_data": {
                    "url": target_url,
                    "user_offering": user_offering,
                },
            }
            start_resp = requests.post(f"{BASE_URL}/start_job", json=job_payload, timeout=10)
            start_resp.raise_for_status()
            job_id = start_resp.json()["job_id"]
        except Exception as e:
            st.error(f"Failed to submit job: {str(e)}")
            st.stop()

        # ── Step 2: Poll until completed ───────────────────────────────────
        with st.spinner("Agents are researching, strategizing, and writing your email…"):
            while True:
                try:
                    status_resp = requests.get(
                        f"{BASE_URL}/status", params={"job_id": job_id}, timeout=10
                    )
                    status_resp.raise_for_status()
                    status_data = status_resp.json()
                except Exception as e:
                    st.error(f"Failed to poll status: {str(e)}")
                    st.stop()

                current_status = status_data.get("status")

                if current_status == "completed":
                    break
                elif current_status == "failed":
                    st.error(f"Job failed: {status_data.get('email_output', 'Unknown error')}")
                    st.stop()

                time.sleep(2)

        # ── Step 3: Render results ─────────────────────────────────────────
        st.success("Email generated successfully!")
        email_text = status_data.get("email_output", "No email generated.")
        output_hash = status_data.get("output_hash", "")

        st.subheader("Final Email")
        st.markdown(f"```text\n{email_text}\n```")

        with st.expander("Job Metadata"):
            st.write(f"**Job ID:** `{job_id}`")
            st.write(f"**Output Hash (SHA-256):** `{output_hash}`")
