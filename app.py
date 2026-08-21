import streamlit as st
import google.generativeai as genai
import os

# --- Configuration ---
# Streamlit Community Cloud will look for the API key in the Secrets manager
# If it's not found there, it will try to get it from the environment variables
API_KEY = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    st.error("API Key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

genai.configure(api_key=API_KEY)

# --- System Instructions (Website Content Context) ---
system_instruction = """
You are an expert literary assistant dedicated to the works of the acclaimed Telugu author Sheelam Bhadraiah (శీలం భద్రయ్య). 
Your primary knowledge base is his official website portfolio. 
You must assist users by answering questions about his books, stories, and the critical essays written about him. You can converse in both Telugu and English.

Key Knowledge Base:
1. "గంగెద్దు కథలు" (Gangeddu Kathalu - Story Collection)
- Stories: నెమలి నవ్వింది, గంట, సిగ్గు, గంగెద్దు, పరువు, పాకీజ, తావు, కుర్చీ, యాక్సిడెంట్‌, భయం, కాగడ, బ్యాడ్ టచ్, అద్దం.
- Essays: జీవితాన్ని వస్త్రగాలం పట్టిన కథలు, బలమైన కథకుడు శీలం భద్రయ్య, ఆణిముత్యాలవంటి కథలు.

2. "లొట్టపీసు పూలు కథలు" (Lottapisu Poolu Kathalu - Story Collection)
- Stories: ఇసపురుగు, కేంపుచెర్వు, బంచెర్రాయి, కర్తవ్యం, లొట్టపీసు పూలు, టముకు, వెలుగు చుక్క, తోడు, కోదండం, కొత్త దొర, లత్త, మాయబారి, అగ్గువ బతుకులు, ఖూనీ, శూర్పణఖ.
- Essays: తెలంగాణ మట్టి మీది వేలిముద్రలు, అస్తిత్వ పతాకలు, తెలంగాణ పల్లె బతుకుల సజీవ చిత్రాలు.
"""

# --- Initialize Gemini Model ---
@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )

model = get_model()

# --- Streamlit UI Setup ---
st.set_page_config(page_title="Sheelam Bhadraiah Literary Assistant", page_icon="📚", layout="centered")

st.title("📚 Sheelam Bhadraiah (శీలం భద్రయ్య) - AI Assistant")
st.markdown("Ask anything about his stories like *గంగెద్దు (Gangeddu)*, *లొట్టపీసు పూలు (Lottapisu Poolu)*, or his literary journey.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about a story or essay... (తెలుగులో కూడా అడగవచ్చు)"):
    # Add user message to state and UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response from Gemini
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        # Build chat history for the API
        chat_history = [{"role": m["role"], "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
        chat = model.start_chat(history=chat_history)
        
        # Get streaming response
        response = chat.send_message(prompt, stream=True)
        full_response = ""
        for chunk in response:
            full_response += chunk.text
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    # Save assistant response to state
    st.session_state.messages.append({"role": "model", "content": full_response})