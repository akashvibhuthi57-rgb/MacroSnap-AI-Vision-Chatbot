import streamlit as st
import smtplib
from email.mime.text import MIMEText

from google import genai
from google.genai import types

from prompts import (
    SUMMARY_REQUEST_PROMPT,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "gemini-3.5-flash"

st.set_page_config(
    page_title="MacroSnap",
    page_icon="🥗"
)


# ============================================================
# Secrets
# ============================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


# ============================================================
# Gemini Client
# ============================================================

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


gemini_client = get_gemini_client()


# ============================================================
# Email Function
# ============================================================

def send_email(to_address, user_name, summary):
    try:
        message = MIMEText(summary)

        message["Subject"] = "🥗 MacroSnap Nutrition Summary"
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_address

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(
                GMAIL_ADDRESS,
                GMAIL_APP_PASSWORD
            )

            server.send_message(message)

        return True, "Email sent successfully"

    except Exception as error:
        return False, str(error)


# ============================================================
# Message Rendering
# ============================================================

def render_message(message):
    with st.chat_message(message["role"]):

        if message["kind"] == "text":
            st.write(message["content"])

        elif message["kind"] == "image":
            st.image(message["content"])


# ============================================================
# Add Message
# ============================================================

def add_message(role, kind, content):

    st.session_state.messages.append(
        {
            "role": role,
            "kind": kind,
            "content": content
        }
    )

    render_message(
        st.session_state.messages[-1]
    )


# ============================================================
# Gemini Chat Function
# ============================================================

def ask_gemini(parts):

    try:

        response = st.session_state.chat.send_message(parts)

        return response.text

    except Exception as error:

        return f"Sorry, something went wrong: {error}"


# ============================================================
# ONBOARDING
# ============================================================

if "onboarded" not in st.session_state:

    st.title("🥗 MacroSnap")

    st.caption(
        "Snap it. Track it. Email yourself the results."
    )

    with st.form("onboarding_form"):

        name = st.text_input(
            "Your name"
        )

        email_address = st.text_input(
            "Email address",
            placeholder="you@gmail.com",
            help="This is the email MacroSnap will send your nutrition summary to."
        )

        submitted = st.form_submit_button(
            "Let's go 🚀"
        )

        if submitted:

            if not name.strip() or not email_address.strip():

                st.warning(
                    "Please fill in both your name and email address."
                )

            else:

                st.session_state.name = name.strip()

                st.session_state.email_address = (
                    email_address.strip()
                )

                # Create Gemini conversation
                st.session_state.chat = (
                    gemini_client.chats.create(
                        model=MODEL_NAME,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT
                        ),
                    )
                )

                st.session_state.messages = []

                st.session_state.onboarded = True

                st.rerun()

    st.stop()


# ============================================================
# CHAT INTERFACE HEADER
# ============================================================

header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)


with header_col:

    st.title("🥗 MacroSnap")


with button_col:

    # Disable email button until there is an actual exchange
    send_disabled = len(
        st.session_state.messages
    ) <= 2

    if st.button(
        "📧 Send to Email",
        disabled=send_disabled,
        use_container_width=True
    ):

        with st.spinner(
            "Summarizing your day..."
        ):

            # Ask Gemini to summarize the entire conversation
            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

            # Send summary by Gmail
            success, info = send_email(
                st.session_state.email_address,
                st.session_state.name,
                summary
            )

            if success:

                st.success(
                    "Sent! Check your email 📧"
                )

            else:

                st.error(
                    f"Couldn't send that: {info}"
                )


# ============================================================
# USER INFORMATION
# ============================================================

st.caption(
    f"Logged in as {st.session_state.name} - "
    f"updates go to {st.session_state.email_address}"
)


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

if not st.session_state.messages:

    add_message(
        "assistant",
        "text",
        WELCOME_MESSAGE_TEMPLATE.format(
            name=st.session_state.name
        )
    )

else:

    for message in st.session_state.messages:

        render_message(message)


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask a question, or attach a photo of your meal",
    accept_file=True,
    file_type=[
        "jpg",
        "jpeg",
        "png"
    ],
)


# ============================================================
# PROCESS USER INPUT
# ============================================================

if user_input:

    photo = (
        user_input.files[0]
        if user_input.files
        else None
    )

    text = user_input.text

    parts = []


    # --------------------------------------------------------
    # Handle Image
    # --------------------------------------------------------

    if photo is not None:

        photo_bytes = photo.getvalue()

        # Display uploaded image
        add_message(
            "user",
            "image",
            photo_bytes
        )

        # Send image to Gemini
        parts.append(
            types.Part.from_bytes(
                data=photo_bytes,
                mime_type=photo.type
            )
        )


    # --------------------------------------------------------
    # Handle Text
    # --------------------------------------------------------

    if text:

        add_message(
            "user",
            "text",
            text
        )

        parts.append(text)


    # --------------------------------------------------------
    # Image-only Prompt
    # --------------------------------------------------------

    elif photo is not None:

        parts.append(
            "What is this meal? "
            "Give me the calories and macros."
        )


    # --------------------------------------------------------
    # Ask Gemini
    # --------------------------------------------------------

    with st.spinner(
        "Crunching the numbers..."
    ):

        answer = ask_gemini(parts)


    # --------------------------------------------------------
    # Display Gemini Response
    # --------------------------------------------------------

    add_message(
        "assistant",
        "text",
        answer
    )