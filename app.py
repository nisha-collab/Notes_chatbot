import streamlit as st
import google.generativeai as genai

# --- TEMP: Hardcoded API key ---
GOOGLE_API_KEY = "AIzaSyA0AK0qaeEIWDprya9JGLdnOVRIq7qSr7Q"
genai.configure(api_key=GOOGLE_API_KEY)

# --- Page Setup ---
st.set_page_config(page_title="Notes Chatbot", layout="wide")
st.title("📚 Notes Chatbot")
st.markdown("Ask your questions from your notes here!")

# --- File Upload ---
uploaded_file = st.file_uploader("Upload your notes (.txt or .pdf)", type=["txt", "pdf"])

# --- Process and Display ---
if uploaded_file is not None:
    content = uploaded_file.read()

    if uploaded_file.type == "application/pdf":
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        except:
            st.error("Error reading PDF. Please try again.")
            st.stop()
    else:
        text = content.decode("utf-8")

    st.success("Notes uploaded successfully!")
    st.text_area("📄 Extracted Content", text, height=200)

    # --- User Query ---
    question = st.text_input("❓ Ask a question based on your notes:")

    if question:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content([text, question])
        st.subheader("🤖 Chatbot Answer:")
        st.write(response.text)

else:
    st.info("Please upload your notes file to start.")
