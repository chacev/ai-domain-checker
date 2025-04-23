
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

@st.cache_data(show_spinner=False)
def filter_words(text):
    words = re.findall(r"\b[a-z]{2,10}\b", text.lower())
    return sorted(set(words))

# --- INITIALIZE SESSION STATE ---
if "start_checking" not in st.session_state:
    st.session_state.start_checking = False
if "words" not in st.session_state:
    st.session_state.words = []

# --- SIDEBAR INPUT ---
st.sidebar.header("Upload or Paste Word List")
input_method = st.sidebar.radio("Input Method", ["Paste text", "Upload .txt file"])

new_words = []
if input_method == "Paste text":
    word_input = st.sidebar.text_area("Paste your words here (space or line separated)", height=150)
    new_words = filter_words(word_input)
elif input_method == "Upload .txt file":
    uploaded_file = st.sidebar.file_uploader("Upload .txt file", type="txt")
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        new_words = filter_words(content)

# Update session state if the word list has changed
if new_words != st.session_state.words:
    st.session_state.words = new_words
    st.session_state.start_checking = False  # Reset the search state

# --- MAIN LOGIC ---
words = st.session_state.words

if words:
    st.success(f"Loaded {len(words)} valid words.")
    if st.button("Start Searching for Available .ai Domains"):
        st.session_state.start_checking = True

if st.session_state.start_checking:
    st.subheader("Checking .ai domains...")

    results_log = []
    results_box = st.empty()
    progress_bar = st.progress(0)

    for i, word in enumerate(words):
        domain = f"{word}.ai"
        available = is_domain_available(domain)
        result = f"**{domain}** — {'✅ Available' if available else '❌ Taken'}"
        results_log.append(result)

        results_box.markdown("\n".join(results_log))
        progress_bar.progress((i + 1) / len(words))
        time.sleep(0.5)

    downloadable = "\n".join(results_log)
    st.download_button("Download Results", downloadable, file_name="ai_domain_results.txt")
else:
    st.info("Please paste or upload a word list to get started.")
