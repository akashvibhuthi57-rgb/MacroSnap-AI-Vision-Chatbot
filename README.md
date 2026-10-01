# 🥗 MacroSnap AI Vision Chatbot

MacroSnap is an AI-powered nutrition assistant built with Streamlit and Google Gemini.

It allows users to:

- 📸 Upload a meal photo
- 🤖 Analyze food using Gemini AI
- 🔥 Estimate calories
- 💪 Estimate protein
- 🍚 Estimate carbohydrates
- 🥑 Estimate fat
- 📊 Track daily nutrition
- 🎯 Set a daily calorie goal
- 🍽️ Maintain meal history during the session
- 📧 Send a nutrition summary to email

## 🚀 Features

### AI Meal Analysis

Users can upload a JPG or PNG image of their meal. Gemini analyzes the image and provides estimated nutrition values.

### Text-Based Nutrition

Users can also describe their meal using text.

Example:

> 2 chapatis with chicken curry

MacroSnap estimates the calories and macronutrients.

### Nutrition Dashboard

The dashboard displays:

- Total calories
- Protein
- Carbohydrates
- Fat
- Daily calorie goal
- Calorie progress

### Meal History

Analyzed meals are stored in the current Streamlit session and displayed with their estimated nutrition values.

### Email Summary

Users can send their nutrition summary to their email using Gmail SMTP.

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- Google GenAI Python SDK
- Gmail SMTP

## 📁 Project Structure

```text
macrosnap/
│
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── .streamlit/
    ├── secrets.toml
    └── secrets.toml.example


## 🚀 Live Demo

🔗 [Try MacroSnap AI Vision Chatbot](https://macrosnap-ai-vision-chatbot-ecbhstnqzgdoeac57vcexf.streamlit.app/)