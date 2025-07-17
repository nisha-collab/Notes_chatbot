import streamlit as st
import google.generativeai as genai
import os
import base64

# --- Configuration ---
# Retrieve the API key from Streamlit secrets.
# You MUST have a file named .streamlit/secrets.toml in your project directory
# with the line: GOOGLE_API_KEY = "YOUR_API_KEY_HERE"
# (where YOUR_API_KEY_HERE is your actual Google API Key).
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("Google API Key not found in Streamlit secrets.")
    st.info("Please create a file named '.streamlit/secrets.toml' in your project directory "
            "and add 'GOOGLE_API_KEY = \"YOUR_API_KEY_HERE\"' (replace YOUR_API_KEY_HERE with your actual key).")
    st.stop() # Stop the app if the API key is not found

# Configure the generative AI model for text generation
genai.configure(api_key=api_key)
# Initialize the model for chat
notes_model = genai.GenerativeModel('gemini-2.0-flash')

# --- Streamlit UI ---
st.set_page_config(
    page_title="AI Notes Chatbot",
    page_icon="💬",
    layout="centered", # Use centered layout for better aesthetics
    initial_sidebar_state="auto"
)

# Custom CSS for a sleek, professional dark look inspired by the image
st.markdown(
    """
    <style>
    /* Overall app background - deep dark */
    .stApp {
        background-color: #121212; /* Very dark background */
        font-family: 'Inter', sans-serif; /* Use Inter font */
        color: #e0e0e0; /* Light text color for general content */
    }

    /* Main content area styling */
    .main {
        background-color: #1e1e1e; /* Slightly lighter dark background for content area */
        padding: 20px; /* Reduced padding for a tighter feel */
        border-radius: 8px; /* Slightly less rounded corners */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5); /* More prominent shadow on dark background */
        margin-top: 10px;
        margin-bottom: 10px;
        max-width: 900px; /* Increased width to accommodate bot image and chat */
    }

    /* Title and header styling */
    h1 {
        color: #bb86fc; /* A subtle, dark purple accent for the title */
        text-align: center;
        font-size: 2.2em;
        margin-bottom: 10px;
    }
    h1 + p { /* Description paragraph after title */
        color: #a0a0a0;
        text-align: center;
        font-size: 0.95em;
        margin-bottom: 20px;
    }

    /* Streamlit chat input styling */
    div[data-testid="stChatInput"] {
        background-color: #2b2b2b; /* Darker background for input */
        border-radius: 8px;
        padding: 8px 15px;
        border: 1px solid #3a3a3a; /* Subtle border */
    }
    div[data-testid="stChatInput"] input {
        color: #e0e0e0; /* Light text in input */
        background-color: transparent; /* Transparent input background */
    }
    div[data-testid="stChatInput"] button { /* Send button */
        background-color: #bb86fc; /* Accent color for send button */
        color: white;
        border-radius: 50%; /* Circular button */
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background-color 0.2s ease;
    }
    div[data-testid="stChatInput"] button:hover {
        background-color: #9a67e0; /* Darker accent on hover */
    }


    /* Streamlit chat message styling - clean and distinct on dark */
    .st-chat-message {
        padding: 12px 15px; /* Adjusted padding */
        border-radius: 8px; /* Consistent rounded corners */
        margin-bottom: 8px;
        line-height: 1.5;
        color: #e0e0e0; /* Light text inside chat messages */
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3); /* Subtle shadow for bubbles */
    }
    .st-chat-message.st-chat-message-user {
        background-color: #333333; /* Darker gray for user messages */
        align-self: flex-end; /* Align to right */
        margin-left: auto; /* Push to right */
        border-bottom-right-radius: 2px; /* Pointed corner */
    }
    .st-chat-message.st-chat-message-assistant {
        background-color: #282828; /* Slightly lighter dark gray for assistant messages */
        align-self: flex-start; /* Align to left */
        margin-right: auto; /* Push to left */
        border-bottom-left-radius: 2px; /* Pointed corner */
    }

    /* Info/Warning/Error/Success boxes - adjusted for dark theme */
    .stAlert {
        border-radius: 6px;
        padding: 10px 15px;
        background-color: #3a3a3a; /* Darker background for alerts */
        color: #e0e0e0; /* Light text for alerts */
    }
    .stAlert.info { border-left: 5px solid #bb86fc; } /* Accent color for info */
    .stAlert.warning { border-left: 5px solid #ffc107; } /* Yellow for warning */
    .stAlert.error { border-left: 5px solid #cf6679; } /* Red for error (dark theme friendly) */
    .stAlert.success { border-left: 5px solid #03dac6; } /* Teal for success (dark theme friendly) */

    /* Footer text */
    .footer-text {
        text-align: center;
        color: #888888; /* Muted gray for footer on dark background */
        font-size: 0.8em;
        margin-top: 20px;
    }
    /* Download button styling */
    .stDownloadButton>button {
        background-color: #03dac6; /* Teal accent for download */
        color: #121212; /* Dark text for contrast */
        padding: 8px 15px;
        font-size: 0.9em;
        border-radius: 6px;
        border: none;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: background-color 0.2s ease;
    }
    .stDownloadButton>button:hover {
        background-color: #02b3a3; /* Darker teal on hover */
    }

    /* Custom bot image container */
    .bot-image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-right: 20px; /* Space between image and chat */
    }
    .bot-image {
        width: 150px; /* Make the bot image big */
        height: auto;
        border-radius: 50%; /* Circular shape */
        border: 3px solid #bb86fc; /* Accent border */
        box-shadow: 0 0 15px rgba(187, 134, 252, 0.5); /* Glowing effect */
    }

    /* Adjust chat container when bot image is present */
    .chat-container {
        flex-grow: 1; /* Allows chat to take remaining space */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Custom SVG for a cute bot icon
# This SVG is a simple, stylized robot face
cute_bot_svg = """
<svg width="150" height="150" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect x="10" y="20" width="80" height="60" rx="10" fill="#282828" stroke="#bb86fc" stroke-width="3"/>
<circle cx="35" cy="45" r="8" fill="#03dac6"/>
<circle cx="65" cy="45" r="8" fill="#03dac6"/>
<path d="M30 70 C40 80, 60 80, 70 70" stroke="#bb86fc" stroke-width="3" stroke-linecap="round"/>
<circle cx="50" cy="85" r="5" fill="#bb86fc"/>
</svg>
"""

# Application Header (mimicking "APPLICATION" from image)
st.markdown(
    """
    <div style="text-align: center; color: #a0a0a0; font-size: 0.8em; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 5px;">
        Application
    </div>
    """,
    unsafe_allow_html=True
)

st.title("AI Notes Chatbot")
st.markdown(
    """
    <p style="font-size:1.05em; color:#c0c0c0;">
    Hello, I'm your Notes AI. How can I help you?
    </p>
    """,
    unsafe_allow_html=True
)

st.divider() # A subtle divider for separation

# Create two columns: one for the bot image, one for the chat
col_bot, col_chat = st.columns([0.3, 0.7]) # Adjust ratio for big bot on left

with col_bot:
    st.markdown(
        f'<div class="bot-image-container"><div class="bot-image">{cute_bot_svg}</div></div>',
        unsafe_allow_html=True
    )
    # You could add a bot name here if desired
    # st.markdown("<p style='text-align:center; color:#bb86fc; font-weight:bold;'>Nooaii</p>", unsafe_allow_html=True)


with col_chat:
    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize the chat session with the model
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = notes_model.start_chat(history=[])

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Message...", key="chat_input_main"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Send user message to the model and get response
                    response = st.session_state.chat_session.send_message(prompt)
                    ai_response = response.text
                    st.markdown(ai_response)
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    # Store the last AI response for download
                    st.session_state['last_ai_response'] = ai_response
                except Exception as e:
                    st.error(f"An error occurred: {e}")
                    st.info("Please check your API key and try again. Also, ensure your prompt does not violate safety policies.")

# --- Download Option ---
# Display download button only if there's a last AI response
if 'last_ai_response' in st.session_state and st.session_state['last_ai_response']:
    st.markdown("---") # Add a divider before download options
    st.markdown(
        """
        <div style="text-align: center; color: #e0e0e0; font-size: 1.0em; margin-bottom: 10px;">
            Want to save these notes?
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_dl1, col_dl2, col_dl3 = st.columns([1, 2, 1])
    with col_dl2:
        # Download as TXT
        notes_bytes = st.session_state['last_ai_response'].encode('utf-8')
        st.download_button(
            label="⬇️ Download Notes as Text File",
            data=notes_bytes,
            file_name="generated_notes.txt",
            mime="text/plain",
            key="download_txt_button",
            use_container_width=True
        )
        
        st.markdown(
            """
            <p style="font-size:0.85em; color:#a0a0a0; text-align: center; margin-top: 5px;">
            For PDF, use your browser's print function (Ctrl+P / Cmd+P) and select 'Save as PDF'.
            </p>
            """,
            unsafe_allow_html=True
        )


st.markdown("---")
st.markdown(
    """
    <div class="footer-text">
        Developed with ❤️ and powered by Google Gemini 2.0 Flash.
    </div>
    """,
    unsafe_allow_html=True
)
