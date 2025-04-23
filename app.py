
import streamlit as st
import requests
import time
import re

# --- PAGE CONFIG ---
st.set_page_config(page_title=".ai Domain Checker", layout="wide")
st.title("🔍 .ai Domain Availability Checker")

# --- API CONFIG ---
API_KEY = st.secrets.get("RAPIDAPI_KEY", "")
API_HOST = "domainr.p.rapidapi.com"
API_URL = "https://domainr.p.rapidapi.com/v2/status"
HEADERS = {
    "x-rapidapi-host": API_HOST,
    "x-rapidapi-key": API_KEY,
}

# --- HELPER FUNCTIONS ---
def is_domain_available(domain):
    try:
        response = requests.get(API_URL, headers=HEADERS, params={"domain": domain})
        data = response.json()
        status_info = data.get("status", [{}])[0].get("status", "")
        return any(tag in status_info for tag in ["undelegated", "inactive"]) and "taken" not in status_info
    except Exception:
        return False

def extract_words(text):
    return list(dict.fromkeys(re.findall(r"[a-zA-Z0-9]{2,}", text.lower())))

# --- SIDEBAR INPUT ---
st.sidebar.header("Upload or Paste Word List")
input_method = st.sidebar.radio("Input Method", ["Paste text", "Upload .txt file"])

raw_words = []
if input_method == "Paste text":
    raw_text = st.sidebar.text_area("Paste your words here (space or line separated)", height=150)
    raw_words = extract_words(raw_text)
elif input_method == "Upload .txt file":
    uploaded_file = st.sidebar.file_uploader("Upload .txt file", type="txt")
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        raw_words = extract_words(content)

# --- ALWAYS SHOW BUTTON ---
start_search = st.button("🚀 Start Searching for Available .ai Domains")

# --- RUN DOMAIN CHECK ---
if start_search:
    if not raw_words:
        st.warning("No words found. Please paste or upload a valid word list.")
    else:
        st.success(f"Searching {len(raw_words)} domains...")
        results_log = []
        results_box = st.empty()
        progress_bar = st.progress(0)

        for i, word in enumerate(raw_words):
            domain = f"{word}.ai"
            available = is_domain_available(domain)
            result = f"**{domain}** — {'✅ Available' if available else '❌ Taken'}"
            results_log.append(result)

            results_box.markdown("\n".join(results_log))
            progress_bar.progress((i + 1) / len(raw_words))
            time.sleep(0.5)

        downloadable = "\n".join(results_log)
        st.download_button("Download Results", downloadable, file_name="ai_domain_results.txt")
