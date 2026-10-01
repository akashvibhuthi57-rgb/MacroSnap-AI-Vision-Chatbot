# 🥗 MacroSnap

MacroSnap is a Streamlit AI vision chatbot that lets a user enter their name and WhatsApp number once, then chat with an AI nutrition buddy using text or meal photos.

The app uses:
- Gemini for chat + vision
- Streamlit for the web interface
- Twilio WhatsApp for sending the conversation summary

## Project structure

```text
macrosnap/
├── app.py
├── prompts.py
├── requirements.txt
├── .gitignore
├── README.md
└── .streamlit/
    └── secrets.toml.example
```

## 1. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure secrets

Copy:

```text
.streamlit/secrets.toml.example
```

to:

```text
.streamlit/secrets.toml
```

Fill in your Gemini and Twilio credentials.

**Never commit `secrets.toml` to GitHub.**

## 4. Gemini

Create a Gemini API key in Google AI Studio and put it in:

```toml
GEMINI_API_KEY = "your-key"
```

## 5. Twilio WhatsApp Sandbox

Set up the Twilio WhatsApp Sandbox, join it from the WhatsApp number you will test with, and create an approved WhatsApp Content Template for business-initiated summary messages.

Add the Account SID, Auth Token, WhatsApp sender, and Content SID to `secrets.toml`.

## 6. Run

```bash
streamlit run app.py
```

The app should open at:

```text
http://localhost:8501
```

## How it works

1. User enters name and WhatsApp number.
2. MacroSnap creates one Gemini chat session.
3. User types a nutrition question or attaches a meal photo.
4. Gemini analyzes the text/image.
5. The conversation is kept in Streamlit session state.
6. The user can request a summary.
7. Gemini creates a WhatsApp-friendly summary.
8. Twilio sends the summary using the configured WhatsApp Content Template.

## Safety note

Nutrition estimates from images are approximate and should not be treated as medical or dietary diagnosis.
