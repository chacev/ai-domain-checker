
import streamlit as st
import requests
import time
import re

# Set page config
st.set_page_config(page_title=".ai Domain Checker", layout="wide")
st.title("🔍 .ai Domain Availability Checker")

# --- API Config ---
API_KEY = st.secrets.get("RAPIDAPI_KEY", "")  # Put your key in .streamlit/secrets.toml
API_HOST = "domainr.p.rapidapi.com"
API_URL = "https://domainr.p.rapidapi.com/v2/status"
HEADERS = {
    "x-rapidapi-host": API_HOST,
    "x-rapidapi-key": API_KEY,
}

# --- Helper Functions ---
def is_domain_available(domain):
    try:
        response = requests.get(API_URL, headers=HEADERS, params={"domain": domain})
        data = response.json()
        status_info = data.get("status", [{}])[0].get("status", "")
        return "undelegated" in status_info or "inactive" in status_info
    except Exception as e:
        return False

@st.cache_data(show_spinner=False)
def filter_words(text):
    words = re.findall(r"\b[a-z]{2,10}\b", text.lower())
    return sorted(set(words))

# --- Sidebar ---
st.sidebar.header("Upload or Paste Word List")
input_method = st.sidebar.radio("Input Method", ["Paste text", "Upload .txt file"])

if input_method == "Paste text":
    word_input = st.sidebar.text_area("Paste your words here (one line, space separated)", height=150)
    words = filter_words(word_input)
elif input_method == "Upload .txt file":
    uploaded_file = st.sidebar.file_uploader("Upload .txt file", type="txt")
    words = []
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        words = filter_words(content)

# --- Main Panel ---
if words:
    st.success(f"Loaded {len(words)} valid words. Ready to check!")
    if st.button("Check Domain Availability"):
        results = []
        with st.spinner("Checking domains, please wait..."):
            for i, word in enumerate(words):
                domain = f"{word}.ai"
                available = is_domain_available(domain)
                results.append((domain, "✅ Available" if available else "❌ Taken"))
                time.sleep(0.5)  # Respect API limits

        st.subheader("Results")
        for domain, status in results:
            st.write(f"**{domain}** — {status}")

        # Download results
        downloadable = "\n".join([f"{d} - {s}" for d, s in results])
        st.download_button("Download Results", downloadable, file_name="ai_domain_results.txt")
else:
    st.info("Please paste or upload a word list to get started.")
