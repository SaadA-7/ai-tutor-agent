# 🧠 AI Tutor Agent

An interactive, multi-mode AI-powered learning assistant built using Claude, Firebase, and Streamlit. This app helps students study through dynamic Q&A, auto-generated quizzes, and smart flashcards — all personalized by topic.

# Link to Webb App: 
https://mentora-ai.streamlit.app/ 
<!-- It may take 1 minute to load the app if new user -->

## ✨ Features

### 🚀 Learning Modes
- **Q&A Mode**: Ask the AI tutor anything across supported subjects.
- **Quiz Mode**: Get AI-generated multiple-choice questions on chosen topics.
- **Flashcard Mode**: Review topics with spaced-repetition-style flashcards.

### 🎨 Frontend & UX
- Topic Selection UI with:
  - Core subject buttons (e.g. Math, CS, History)
  - "+ More Topics" expandable grid
  - Custom user-defined topics
- Light & Dark Mode toggle
- Responsive layout and custom styling

### 🔐 Authentication & Database
- Firebase login/signup (Pyrebase)
- Secure email/password authentication
- Firestore database to save user progress in all modes

### 💳 Monetization
- Stripe integration to upgrade to **Tutor Pro**
- Usage limits on free tier
- "Upgrade" button when limit is reached
- Premium users unlock unlimited sessions & more features

### ☁️ Hosting & Security
- Deployed on **Streamlit Cloud**
- API keys and credentials securely managed via `secrets.toml`
- Auth data and Firestore documents securely scoped per user

---

## 🧱 Tech Stack

| Layer        | Technology                            |
|--------------|----------------------------------------|
| Frontend     | Streamlit + HTML/CSS (custom styling) |
| Backend      | Python, Firebase Admin SDK, Pyrebase   |
| AI Model     | Claude (Anthropic API)                |
| Auth & DB    | Firebase Authentication + Firestore    |
| Payments     | Stripe Checkout + Firebase Cloud Functions (planned) |
| Hosting      | Streamlit Cloud                        |

---


## 🔑 How to Sign Up / Use the App

1. **Sign Up**
   - New users: Enter your email and a password to create an account.
   - Returning users: Log in with the same email and password.

2. **Choose Your Mode**
   - Pick between **Q&A**, **Quiz**, or **Flashcard** tutor modes.
   - Select a topic from the core subjects or "+ More Topics" list.

3. **Upgrade (Coming Soon)**
   - Tutor Pro unlocks unlimited use and more features.
   - Upgrade button will appear when you reach your free usage limit.
   - Payments will be handled securely via Stripe.

> ⚠️ Note: The app is currently in **beta**. Features and UI may change frequently.


---

## ⚙️ Installation (Local)
<!-- For users who want to run the app locally -->

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/ai-tutor-agent.git
   cd ai-tutor-agent

2. Set up virtual environment:
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

3. Install dependencies:
pip install -r requirements.txt

4. Add a firebase-service-account.json to the root directory
(You can download this from Firebase > Project Settings > Service Accounts)

5. Create a .streamlit/secret.toml file with:
ANTHROPIC_API_KEY = "your-anthropic-key"

firebase_config.apiKey = "your-api-key"
firebase_config.authDomain = "your-auth-domain"
firebase_config.projectId = "your-project-id"
firebase_config.storageBucket = "your-storage-bucket"
firebase_config.messagingSenderId = "your-sender-id"
firebase_config.appId = "your-app-id"
firebase_config.databaseURL = ""

firebase_service_account = """...your JSON as one string..."""

6. Run the app locally:
streamlit run app.py

---

This project is licensed under the MIT License.

---

🙋‍♂️ Author:
Built by Saad Ahmad, a CS student at the University of Maryland passionate about making useful tools with real impact.