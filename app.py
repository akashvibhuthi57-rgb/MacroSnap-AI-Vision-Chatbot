import streamlit as st
import smtplib
import re
from email.mime.text import MIMEText

from google import genai
from google.genai import types

from prompts import (
    SUMMARY_REQUEST_PROMPT,
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
)


# ============================================================
# CONFIGURATION
# ============================================================
MODEL_NAME = "gemini-3.5-flash-lite"

st.set_page_config(
    page_title="MacroSnap",
    page_icon="🥗",
    layout="wide"
)


# ============================================================
# SECRETS
# ============================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


# ============================================================
# GEMINI CLIENT
# ============================================================

@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=GEMINI_API_KEY
    )


gemini_client = get_gemini_client()


# ============================================================
# EMAIL FUNCTION
# ============================================================

def send_email(to_address, user_name, summary):

    try:

        email_body = f"""Hi {user_name},

Here is your MacroSnap nutrition summary:

{summary}

Keep tracking your meals and stay consistent! 🥗
"""

        message = MIMEText(email_body)

        message["Subject"] = "🥗 MacroSnap Nutrition Summary"
        message["From"] = GMAIL_ADDRESS
        message["To"] = to_address

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as server:

            server.login(
                GMAIL_ADDRESS,
                GMAIL_APP_PASSWORD
            )

            server.send_message(message)

        return True, "Email sent successfully"

    except Exception as error:

        return False, str(error)


# ============================================================
# MESSAGE RENDERING
# ============================================================

def render_message(message):

    with st.chat_message(message["role"]):

        if message["kind"] == "text":

            st.write(
                message["content"]
            )

        elif message["kind"] == "image":

            st.image(
                message["content"]
            )


# ============================================================
# ADD MESSAGE
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
# GEMINI CHAT FUNCTION
# ============================================================

def ask_gemini(parts):
    
    try:

        response = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=parts,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            )
        )

        if response is None:
            return "Gemini did not return a response."

        if response.text is None:
            return "Gemini returned an empty response."

        return str(response.text)

    except Exception as error:

        st.error(
            f"Gemini error: {error}"
        )

        return (
            f"Gemini error: {error}"
        )


def analyze_meal_image(image_bytes, mime_type):
    
    try:

        response = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type
                ),
                """
Analyze this food image carefully.

Identify the meal and estimate its nutrition.

Return EXACTLY this format:

Meal: [meal name]
Calories: [number] kcal
Protein: [number] g
Carbs: [number] g
Fat: [number] g

Nutrition values are estimates.
Keep the answer short.
"""
            ]
        )

        if response is None:
            return "Gemini returned no response."

        if response.text is None:
            return "Gemini returned an empty response."

        return str(response.text)

    except Exception as error:

        return (
            f"IMAGE_ANALYSIS_ERROR: {error}"
        )

# ============================================================
# NUTRITION EXTRACTION
# ============================================================

def extract_nutrition(text):

    nutrition = {
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fat": 0.0,
    }
    if text is None:
        return {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
        }
        if text is None:
            return {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
        }

    text = str(text)

    text = str(text)

    calories = re.search(
        r"\*{0,2}Calories\*{0,2}\s*:\s*([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    protein = re.search(
        r"\*{0,2}Protein\*{0,2}\s*:\s*([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    carbs = re.search(
        r"\*{0,2}Carbs\*{0,2}\s*:\s*([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    fat = re.search(
        r"\*{0,2}Fat\*{0,2}\s*:\s*([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )

    if calories:

        nutrition["calories"] = float(
            calories.group(1).replace(",", "")
        )

    if protein:

        nutrition["protein"] = float(
            protein.group(1).replace(",", "")
        )

    if carbs:

        nutrition["carbs"] = float(
            carbs.group(1).replace(",", "")
        )

    if fat:

        nutrition["fat"] = float(
            fat.group(1).replace(",", "")
        )

    return nutrition


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
            help=(
                "This is the email MacroSnap will "
                "send your nutrition summary to."
            )
        )

        calorie_goal = st.number_input(
            "Daily calorie goal",
            min_value=500,
            max_value=10000,
            value=2000,
            step=100
        )

        submitted = st.form_submit_button(
            "Let's go 🚀"
        )

        if submitted:

            if (
                not name.strip()
                or not email_address.strip()
            ):

                st.warning(
                    "Please fill in both your name "
                    "and email address."
                )

            else:

                st.session_state.name = (
                    name.strip()
                )

                st.session_state.email_address = (
                    email_address.strip()
                )

                st.session_state.calorie_goal = (
                    calorie_goal
                )

                # Create Gemini conversation

                try:

                    st.session_state.chat = (
                        gemini_client.chats.create(
                            model=MODEL_NAME,
                            config=types.GenerateContentConfig(
                                system_instruction=SYSTEM_PROMPT
                            )
                        )
                    )

                except Exception as error:

                    st.error(
                        f"Could not start Gemini: {error}"
                    )

                    st.stop()

                # Initialize messages

                st.session_state.messages = []

                # Initialize nutrition

                st.session_state.nutrition = {
                    "calories": 0.0,
                    "protein": 0.0,
                    "carbs": 0.0,
                    "fat": 0.0,
                }

                # Initialize meal history

                st.session_state.meal_history = []

                # Mark onboarding complete

                st.session_state.onboarded = True

                st.rerun()

    st.stop()


# ============================================================
# SAFETY INITIALIZATION
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


if "nutrition" not in st.session_state:

    st.session_state.nutrition = {
        "calories": 0.0,
        "protein": 0.0,
        "carbs": 0.0,
        "fat": 0.0,
    }


if "meal_history" not in st.session_state:

    st.session_state.meal_history = []


if "calorie_goal" not in st.session_state:

    st.session_state.calorie_goal = 2000


# ============================================================
# HEADER
# ============================================================

header_col, button_col = st.columns(
    [5, 2],
    vertical_alignment="center"
)


with header_col:

    st.title("🥗 MacroSnap")

    st.caption(
        "Your AI nutrition buddy"
    )


with button_col:

    send_disabled = (
        len(st.session_state.messages) <= 1
    )

    if st.button(
        "📧 Send to Email",
        disabled=send_disabled,
        use_container_width=True
    ):

        with st.spinner(
            "Summarizing your day..."
        ):

            summary = ask_gemini(
                [SUMMARY_REQUEST_PROMPT]
            )

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
    f"Logged in as {st.session_state.name} — "
    f"updates go to {st.session_state.email_address}"
)


# ============================================================
# NUTRITION DASHBOARD
# ============================================================

st.subheader(
    "📊 Today's Nutrition"
)


nutrition = st.session_state.nutrition

goal = st.session_state.calorie_goal

calories = nutrition["calories"]
protein = nutrition["protein"]
carbs = nutrition["carbs"]
fat = nutrition["fat"]


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🔥 Calories",
        f"{calories:.0f} kcal",
        f"Goal {goal} kcal"
    )


with col2:

    st.metric(
        "💪 Protein",
        f"{protein:.1f} g"
    )


with col3:

    st.metric(
        "🍚 Carbs",
        f"{carbs:.1f} g"
    )


with col4:

    st.metric(
        "🥑 Fat",
        f"{fat:.1f} g"
    )


# ============================================================
# CALORIE PROGRESS
# ============================================================

if goal > 0:

    progress = min(
        calories / goal,
        1.0
    )

    st.progress(
        progress,
        text=(
            f"Daily calorie progress: "
            f"{calories:.0f} / {goal} kcal"
        )
    )


# ============================================================
# MEAL HISTORY
# ============================================================

st.divider()

st.subheader(
    "🍽️ Meal History"
)


meal_history = st.session_state.meal_history


if not meal_history:

    st.info(
        "No meals logged yet. "
        "Upload a meal photo or describe what you're eating."
    )

else:

    for meal in reversed(meal_history):

        with st.expander(
            f"🍴 {meal['meal']} — "
            f"{meal['calories']:.0f} kcal"
        ):

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "💪 Protein",
                    f"{meal['protein']:.1f} g"
                )

            with col2:

                st.metric(
                    "🍚 Carbs",
                    f"{meal['carbs']:.1f} g"
                )

            with col3:

                st.metric(
                    "🥑 Fat",
                    f"{meal['fat']:.1f} g"
                )


# ============================================================
# QUICK STATS
# ============================================================

st.divider()

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "🔥 Calorie Goal",
        f"{goal} kcal"
    )


with col2:

    st.metric(
        "🍽️ Meals Logged",
        len(st.session_state.meal_history)
    )


with col3:

    st.metric(
        "🤖 AI Assistant",
        "Active"
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

st.divider()

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


    # ========================================================
    # HANDLE IMAGE
    # ========================================================
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

    # ========================================================
    # IMAGE ANALYSIS
    # ========================================================

    if photo is not None:

        photo_bytes = photo.getvalue()

        # Show image in chat
        add_message(
            "user",
            "image",
            photo_bytes
        )

        with st.spinner(
            "🔍 Analyzing your meal image..."
        ):

            answer = analyze_meal_image(
                photo_bytes,
                photo.type
            )

        # Make absolutely sure answer is a string
        if answer is None:

            answer = (
                "Gemini did not return a response "
                "for this image."
            )

        answer = str(answer)

        # Show Gemini response
        add_message(
            "assistant",
            "text",
            answer
        )

        # Check whether Gemini returned an error
        if answer.startswith(
            "IMAGE_ANALYSIS_ERROR:"
        ):

            st.error(answer)

        else:

            # Extract nutrition
            nutrition_result = extract_nutrition(
                answer
            )

            # Update totals
            st.session_state.nutrition[
                "calories"
            ] += nutrition_result["calories"]

            st.session_state.nutrition[
                "protein"
            ] += nutrition_result["protein"]

            st.session_state.nutrition[
                "carbs"
            ] += nutrition_result["carbs"]

            st.session_state.nutrition[
                "fat"
            ] += nutrition_result["fat"]

            # Save to meal history
            if nutrition_result["calories"] > 0:

                meal_match = re.search(
                    r"\*{0,2}Meal\*{0,2}\s*:\s*(.+)",
                    answer,
                    re.IGNORECASE
                )

                if meal_match:

                    meal_name = (
                        meal_match.group(1).strip()
                    )

                else:

                    meal_name = "Meal"

                st.session_state.meal_history.append(
                    {
                        "meal": meal_name,
                        "calories": nutrition_result["calories"],
                        "protein": nutrition_result["protein"],
                        "carbs": nutrition_result["carbs"],
                        "fat": nutrition_result["fat"],
                    }
                )

        st.rerun()


    # ========================================================
    # TEXT ANALYSIS
    # ========================================================

    elif text:

        add_message(
            "user",
            "text",
            text
        )

        with st.spinner(
            "🥗 Thinking..."
        ):

            answer = ask_gemini(
                [text]
            )

        if answer is None:

            answer = (
                "Gemini did not return a response."
            )

        answer = str(answer)

        add_message(
            "assistant",
            "text",
            answer
        )

        # Extract nutrition
        nutrition_result = extract_nutrition(
            answer
        )

        # Update totals
        st.session_state.nutrition[
            "calories"
        ] += nutrition_result["calories"]

        st.session_state.nutrition[
            "protein"
        ] += nutrition_result["protein"]

        st.session_state.nutrition[
            "carbs"
        ] += nutrition_result["carbs"]

        st.session_state.nutrition[
            "fat"
        ] += nutrition_result["fat"]

        # Save to meal history
        if nutrition_result["calories"] > 0:

            meal_match = re.search(
                r"\*{0,2}Meal\*{0,2}\s*:\s*(.+)",
                answer,
                re.IGNORECASE
            )

            if meal_match:

                meal_name = (
                    meal_match.group(1).strip()
                )

            else:

                meal_name = "Meal"

            st.session_state.meal_history.append(
                {
                    "meal": meal_name,
                    "calories": nutrition_result["calories"],
                    "protein": nutrition_result["protein"],
                    "carbs": nutrition_result["carbs"],
                    "fat": nutrition_result["fat"],
                }
            )

        st.rerun()

    else:

        st.warning(
            "Please type a message or upload a meal photo."
        )