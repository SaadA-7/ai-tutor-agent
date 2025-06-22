import os
import re
import streamlit as st
import datetime
import stripe
import firebase_admin
from dotenv import load_dotenv
from anthropic import Anthropic
from streamlit_option_menu import option_menu
from firebase_config import auth
from firestore_config import db
from firebase_admin import credentials, firestore

# only initialize the default app if it hasn’t been already
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-service-account.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Stripe integration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session(user_email):
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url="https://your-site.streamlit.app?session=success",
            cancel_url="https://your-site.streamlit.app?session=cancel",
            payment_method_types=["card"],
            mode="payment",  # or "subscription" for monthly
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Tutor Pro Plan",
                    },
                    "unit_amount": 1500,  # $15 in cents
                },
                "quantity": 1,
            }],
            metadata={"email": user_email}
        )
        return checkout_session.url
    except Exception as e:
        st.error(f"⚠️ Failed to create checkout: {str(e)}")
        return None


# Save progress to Firestore
def save_user_progress(email, data_type, data):
    user_doc = db.collection("users").document(email)
    user_doc.set({data_type: data}, merge=True)


# Email Validation
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)



# ============================================================================
# INITIALIZATION & CONFIGURATION
# ============================================================================

# Load environment variables and API key
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

# Initialize session state for theme tracking
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"  # Default to dark theme

# Configure page settings
st.set_page_config(
    page_title="AI Tutor Agent", 
    layout="centered",
    initial_sidebar_state="expanded"
)

# ============================================================================
# DYNAMIC THEME STYLING
# ============================================================================

def apply_theme_styling():
    """Apply dynamic CSS based on current theme selection"""
    theme = st.session_state.theme_mode
    
    # Load and inject CSS with theme variables
    try:
        with open("styles.css") as css_file:
            css_content = css_file.read()
            
        # Add theme-specific class to the app container
        theme_injection = f"""
        <style>
        {css_content}
        
        /* Force theme application */
        .stApp {{
            {get_theme_variables(theme)}
        }}
        </style>
        """
        st.markdown(theme_injection, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error("❌ styles.css file not found. Please ensure it's in the same directory as app.py")

def get_theme_variables(theme):
    """Return CSS variables for the specified theme"""
    if theme == "light":
        return """
        --primary-bg: #DFD0B8;
        --secondary-bg: #f5f0e6;
        --sidebar-bg: #f3ede2;
        --text-primary: #222831;
        --text-secondary: #393E46;
        --accent-color: #7c3aed;
        --accent-hover: #6d28d9;
        --accent-light: #a78bfa;
        --warm-accent: #f59e0b;
        --success-accent: #10b981;
        --input-bg: #ffffff;
        --input-border: #cfc6b5;
        --form-bg: #fdfaf6;
        --button-bg: #7c3aed;
        --button-hover: #6d28d9;
        --button-text: #ffffff;
        --user-bubble-bg: #ddd6fe;
        --user-bubble-text: #393E46;
        --tutor-bubble-bg: #d1fae5;
        --tutor-bubble-text: #065f46;
        --success-color: #10b981;
        --error-color: #ef4444;
        --warning-color: #f59e0b;
        --border-color: #e0d7c7;
        """
    else:  # dark theme with your new palette
        return """
            --primary-bg: #222831;
            --secondary-bg: #393E46;
            --sidebar-bg: #393E46;
            --text-primary: #DFD0B8;
            --text-secondary: #948979;
            --accent-color: #7c3aed;
            --accent-hover: #6d28d9;
            --accent-light: #a78bfa;
            --warm-accent: #f59e0b;
            --success-accent: #10b981;
            --input-bg: #393E46;
            --input-border: #948979;
            --form-bg: #393E46;
            --button-bg: #7c3aed;
            --button-hover: #6d28d9;
            --button-text: #DFD0B8;
            --user-bubble-bg: #7c3aed;
            --user-bubble-text: #DFD0B8;
            --tutor-bubble-bg: #10b981;
            --tutor-bubble-text: #DFD0B8;
            --success-color: #10b981;
            --error-color: #ef4444;
            --warning-color: #f59e0b;
            --border-color: #948979;
            --shadow-color: rgba(34, 40, 49, 0.4);
        """

# Apply theme styling
apply_theme_styling()

# ============================================================================
# SIDEBAR NAVIGATION & CONTROLS
# ============================================================================


with st.sidebar:
    st.markdown("### 👤 MentoraAi, your personal tutor")

    # Check if user is already logged in
    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is None:
        st.markdown("### 🔐 Log In or Sign Up Below")

        login_email = st.text_input("📧 Email")
        login_password = st.text_input("🔑 Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔓 Log In"):
                try:
                    user = auth.sign_in_with_email_and_password(login_email, login_password)
                    st.session_state.user = user
                    st.success("✅ Logged in successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Login failed: {str(e)}")

        with col2:
            if st.button("📝 Sign Up"):
                if not is_valid_email(login_email):
                 st.error("❌ Please enter a valid email address.")
            else:
                try:
                    user = auth.create_user_with_email_and_password(login_email, login_password)
                    st.session_state.user = user
                    st.success("🎉 Account created. You can now log in.")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Sign-up failed: {str(e)}")


        st.stop()  # Prevent app from loading if not logged in
    else:
        # Display user's email if logged in
        user_email = st.session_state.user['email']
        current_user = user_email

        st.success(f"👋 Logged in as: {user_email}")
        current_user = user_email

        # 🔐 Check if user is Pro
        user_doc = db.collection("users").document(user_email).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            st.session_state.is_pro = user_data.get("pro", False)
        else:
            st.session_state.is_pro = False

        # Show Pro status
        if st.session_state.is_pro:
            st.success("🌟 You are a Tutor Pro member!")
        else:
            st.info("🔓 Free tier (daily limits apply)")


        # Load previous user progress
        user_doc = db.collection("users").document(user_email).get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            st.session_state.quiz_score = user_data.get("quiz_score", {"correct": 0, "total": 0})
            st.session_state.flashcard_score = user_data.get("flashcard_score", {"got_it": 0, "missed": 0})


        # 🔓 Logout Button
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.user = None
            st.success("✅ You have been logged out.")
            st.rerun()

    
    # Progress reset button
    if st.button("🔄 Reset Progress", use_container_width=True):
        session_keys_to_reset = [
            "messages", "quiz_score", "flashcard_score",
            "current_quiz", "current_flashcard", "show_answer"
        ]
        for key in session_keys_to_reset:
            if key in st.session_state:
                del st.session_state[key]
        st.success("✅ Progress reset successfully!")
        st.rerun()

    st.markdown("---")

    # Navigation menu
    selected_mode = option_menu(
        menu_title="📚 AI Tutor Modes",
        options=["Q&A Chat", "Quiz Mode", "Flashcards"],
        icons=["chat-dots", "question-circle", "journal-text"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "border-radius": "5px"},
            "icon": {"color": "var(--accent-color)", "font-size": "18px"}, 
            "nav-link": {
                "font-size": "16px", 
                "text-align": "left", 
                "margin": "0px",
                "color": "var(--text-primary)"
            },
            "nav-link-selected": {"background-color": "var(--accent-color)"},
        }
    )

    st.markdown("---")
    
    # Theme selector
    st.markdown("### 🎨 Theme Settings")
    
    theme_options = ["Dark", "Light"]
    current_theme_index = 0 if st.session_state.theme_mode == "dark" else 1
    
    selected_theme = st.radio(
        "Choose your theme:",
        theme_options,
        index=current_theme_index,
        horizontal=True
    )
    
    # Update theme if changed
    new_theme = "dark" if selected_theme == "Dark" else "light"
    if new_theme != st.session_state.theme_mode:
        st.session_state.theme_mode = new_theme
        st.rerun()

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Initialize conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Initialize quiz scoring
if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = {"correct": 0, "total": 0}

# Initialize flashcard scoring
if "flashcard_score" not in st.session_state:
    st.session_state.flashcard_score = {"got_it": 0, "missed": 0}

# get today's date as a string
def get_today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")

# Load or initialize usage tracking
if "usage" not in st.session_state:
    st.session_state.usage = {
        "qa_count": 0,
        "quiz_count": 0,
        "flashcard_count": 0,
        "last_reset": get_today_str(),
        "limit_hit": {"qa": False, "quiz": False, "flashcard": False}
    }

# Reset usage if it's a new day
today_str = get_today_str()
if st.session_state.usage.get("last_reset") != today_str:
    st.session_state.usage.update({
        "qa_count": 0,
        "quiz_count": 0,
        "flashcard_count": 0,
        "last_reset": today_str,
        "limit_hit": {"qa": False, "quiz": False, "flashcard": False}
    })

# Load usage from Firestore (once, after login)
if current_user and "usage_loaded" not in st.session_state:
    user_doc = db.collection("users").document(current_user).get()
    if user_doc.exists:
        usage_data = user_doc.to_dict().get("daily_usage", {})
        if usage_data.get("last_reset") == today_str:
            st.session_state.usage.update(usage_data)
    st.session_state.usage_loaded = True

# Persist usage back to Firestore when modified
def save_usage():
    if current_user:
        db.collection("users").document(current_user).set(
            {"daily_usage": st.session_state.usage}, merge=True
        )

def show_upgrade_modal(mode):
    # Create a Stripe Checkout URL based on logged-in user email
    upgrade_url = create_checkout_session(current_user)

    st.markdown(f"""
    <div style="background-color: var(--form-bg); padding: 2rem; border: 2px solid var(--accent-color); border-radius: 1rem; box-shadow: 0 4px 8px var(--shadow-color); margin: 2rem 0;">
        <h2 style="color: var(--text-primary);">🚀 Upgrade to Tutor Pro</h2>
        <p style="color: var(--text-secondary);">
            You've reached the daily limit for <strong>{mode}</strong> mode.<br>
            Upgrade to Tutor Pro for:
        </p>
        <ul style="color: var(--text-secondary);">
            <li>✅ Unlimited {mode} access</li>
            <li>✅ Full progress tracking</li>
            <li>✅ Premium topics & smart review</li>
            <li>✅ Bonus: early access to mobile app</li>
        </ul>
        {"<a href='" + upgrade_url + "' target='_blank'>" if upgrade_url else ""}
            <button style="background-color: var(--button-bg); color: var(--button-text); padding: 0.8rem 1.5rem; font-size: 1.1rem; border: none; border-radius: 8px; cursor: pointer;">
                🔓 Upgrade Now
            </button>
        {"</a>" if upgrade_url else ""}
    </div>
    """, unsafe_allow_html=True)




# Define daily free usage caps
DAILY_LIMITS = {
    "qa": 5,
    "quiz": 3,
    "flashcard": 5
}


# ============================================================================
# Q&A CHAT MODE
# ============================================================================

if selected_mode == "Q&A Chat":
    # Header section
    st.markdown(f"""
        <div class="page-header">
            <h1>💬 Q&A Tutor for {current_user}</h1>
            <p>Ask any academic question and get detailed explanations!</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ---------------- TOPIC SELECTION UI ----------------

    # Core and extended topics
    core_topics = ["Math", "Science", "History", "Programming", "Trivia"]
    more_topics = [
    "Algebra", "Geometry", "Calculus", "Biology", "Chemistry",
    "World History", "Java", "C", "Python", "Geography",
    "Data Structures and Algorithms"
    ]


    # Initialize topic selection state
    if "selected_topic" not in st.session_state:
        st.session_state.selected_topic = core_topics[0]

    if "show_more_topics" not in st.session_state:
        st.session_state.show_more_topics = False

    # Handle topic click
    def select_topic(topic):
        st.session_state.selected_topic = topic

    # Render core topics row
    st.markdown("#### 🎯 Select a Topic")
    cols = st.columns(len(core_topics) + 1)
    for i, topic in enumerate(core_topics):
        with cols[i]:
            if st.button(topic, key=f"core_{topic}", use_container_width=True):
                select_topic(topic)

    # + More Topics toggle
    with cols[-1]:
        if st.button("➕ More Topics", use_container_width=True):
            st.session_state.show_more_topics = not st.session_state.show_more_topics

    

    # Optional extended topics grid
    if st.session_state.show_more_topics:
        st.markdown("##### 📚 Extended Topics")
        extended_rows = [more_topics[i:i+3] for i in range(0, len(more_topics), 3)]
        for row in extended_rows:
            cols = st.columns(len(row))
            for i, topic in enumerate(row):
                with cols[i]:
                    if st.button(topic, key=f"more_{topic}", use_container_width=True):
                        select_topic(topic)

    # Display current selected topic
    st.markdown(f"**Current Topic:** `{st.session_state.selected_topic}`")
    # ✍️ Optional: Enter custom topic
    if "show_custom_topic" not in st.session_state:
        st.session_state.show_custom_topic = False

    if st.button("✍️ Or enter your own topic", use_container_width=True):
        st.session_state.show_custom_topic = not st.session_state.show_custom_topic

    if st.session_state.show_custom_topic:
        custom_topic = st.text_input("Enter a custom topic:", key="custom_topic_input")
        if custom_topic:
            st.session_state.selected_topic = custom_topic




    # Chat input form
    with st.form(key="chat_input_form", clear_on_submit=True):
        user_question = st.text_input(
            "💭 Your Question", 
            placeholder="e.g., What is a linked list in computer science?",
            help="Ask anything related to your studies!"
        )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col2:
            submit_question = st.form_submit_button("🚀 Ask Tutor", use_container_width=True)

    # Process user input
    if not st.session_state.is_pro and st.session_state.usage["qa_count"] >= DAILY_LIMITS["qa"]:
        st.session_state.usage["limit_hit"]["qa"] = True
        show_upgrade_modal("Q&A")
    elif submit_question and user_question.strip():
        st.session_state.usage["qa_count"] += 1
        save_usage()


        # Add user message to conversation
        st.session_state.messages.append({
            "role": "user", 
            "content": user_question.strip()
        })

        # Generate AI response with topic-injected context
        with st.spinner("🤔 Tutor is thinking..."):
            try:
                topic_context = f"You are a tutor helping with the subject: {st.session_state.selected_topic}."
                messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                ]
                ai_response = client.messages.create(
                    model="claude-3-haiku-20240307",
                    system=topic_context,
                    max_tokens=750,
                    temperature=0.6,
                    messages=messages
                )


                tutor_answer = ai_response.content[0].text
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": tutor_answer
                })

            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")



    # Display conversation history
    if st.session_state.messages:
        st.markdown("### 💬 Conversation History")
        
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class="user-message-bubble">
                        <strong>🧑‍🎓 You:</strong> {message['content']}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="tutor-message-bubble">
                        <strong>🤖 AI Tutor:</strong> {message['content']}
                    </div>
                """, unsafe_allow_html=True)

# ============================================================================
# QUIZ MODE
# ============================================================================

elif selected_mode == "Quiz Mode":
    # Header section
    st.markdown(f"""
        <div class="page-header">
            <h1>🧠 Quiz Mode for {current_user}</h1>
            <p>Test your knowledge with AI-generated multiple choice questions!</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    # ---------------- EXPANDABLE QUIZ TOPIC SELECTOR ----------------
    st.markdown("#### 🎯 Select a Quiz Topic")

    core_quiz_topics = ["General", "Math", "Science", "History", "Programming"]
    more_quiz_topics = ["Data Structures and Algorithms", "Java", "C", "Algebra", "Calculus", "Geography", "World History"]

    if "quiz_selected_topic" not in st.session_state:
        st.session_state.quiz_selected_topic = core_quiz_topics[0]

    if "quiz_show_more_topics" not in st.session_state:
        st.session_state.quiz_show_more_topics = False

    def select_quiz_topic(topic):
        st.session_state.quiz_selected_topic = topic

    quiz_cols = st.columns(len(core_quiz_topics) + 1)
    for i, topic in enumerate(core_quiz_topics):
        with quiz_cols[i]:
            if st.button(topic, key=f"quiz_core_{topic}", use_container_width=True):
                select_quiz_topic(topic)

    with quiz_cols[-1]:
        if st.button("➕ More Topics", key="quiz_more_toggle", use_container_width=True):
            st.session_state.quiz_show_more_topics = not st.session_state.quiz_show_more_topics

    if st.session_state.quiz_show_more_topics:
        st.markdown("##### 📚 Extended Quiz Topics")
        extra_rows = [more_quiz_topics[i:i+3] for i in range(0, len(more_quiz_topics), 3)]
        for row in extra_rows:
            row_cols = st.columns(len(row))
            for i, topic in enumerate(row):
                with row_cols[i]:
                    if st.button(topic, key=f"quiz_more_{topic}", use_container_width=True):
                        select_quiz_topic(topic)

    st.markdown(f"**Current Quiz Topic:** `{st.session_state.quiz_selected_topic}`")
    # ✍️ Optional: Enter custom quiz topic
    if "quiz_show_custom_topic" not in st.session_state:
        st.session_state.quiz_show_custom_topic = False

    if st.button("✍️ Or enter your own quiz topic", use_container_width=True):
        st.session_state.quiz_show_custom_topic = not st.session_state.quiz_show_custom_topic

    if st.session_state.quiz_show_custom_topic:
        custom_quiz_topic = st.text_input("Enter a custom quiz topic:", key="custom_quiz_topic_input")
        if custom_quiz_topic:
            st.session_state.quiz_selected_topic = custom_quiz_topic



    # Initialize quiz state
    if "current_quiz_data" not in st.session_state:
        st.session_state.current_quiz_data = None

    # Quiz generation controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.is_pro and st.session_state.usage["quiz_count"] >= DAILY_LIMITS["quiz"]:
            st.session_state.usage["limit_hit"]["quiz"] = True
            show_upgrade_modal("Quiz")
        elif st.button("🎲 Generate New Question", use_container_width=True):
            st.session_state.usage["quiz_count"] += 1
            save_usage()


            selected_quiz_topic = st.session_state.quiz_selected_topic
            quiz_prompt = (
                f"Create a multiple choice quiz question on the topic of '{selected_quiz_topic}'. "
                "It should be suitable for students and formatted exactly as:\n\n"
                "Format your response EXACTLY as follows:\n\n"
                "**Question:** [Your question here]\n"
                "**A.** [Option A]\n"
                "**B.** [Option B]\n"
                "**C.** [Option C]\n"
                "**D.** [Option D]\n"
                "**Answer:** [Letter only - A, B, C, or D]\n"
                "**Explanation:** [Brief explanation of why this answer is correct]"
            )
            
            with st.spinner("🔄 Generating new question..."):
                try:
                    quiz_response = client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=600,
                        temperature=0.8,
                        messages=[{"role": "user", "content": quiz_prompt}]
                    )
                    
                    st.session_state.current_quiz_data = quiz_response.content[0].text.strip()
                    
                except Exception as e:
                    st.error(f"❌ Error generating quiz: {str(e)}")

    # Display and handle quiz
    if st.session_state.current_quiz_data:
        try:
            quiz_lines = st.session_state.current_quiz_data.split("\n")
            
            # Parse quiz components
            quiz_question = ""
            quiz_options = {}
            correct_answer = ""
            explanation = ""
            
            for line in quiz_lines:
                line = line.strip()
                if line.startswith("**Question:**"):
                    quiz_question = line.replace("**Question:**", "").strip()
                elif line.startswith("**A.**"):
                    quiz_options["A"] = line.replace("**A.**", "").strip()
                elif line.startswith("**B.**"):
                    quiz_options["B"] = line.replace("**B.**", "").strip()
                elif line.startswith("**C.**"):
                    quiz_options["C"] = line.replace("**C.**", "").strip()
                elif line.startswith("**D.**"):
                    quiz_options["D"] = line.replace("**D.**", "").strip()
                elif line.startswith("**Answer:**"):
                    correct_answer = line.replace("**Answer:**", "").strip().upper()
                elif line.startswith("**Explanation:**"):
                    explanation = line.replace("**Explanation:**", "").strip()

            # Display quiz question
            if quiz_question and quiz_options:
                st.markdown(f"""
                    <div class="quiz-question-container">
                        <h3>❓ {quiz_question}</h3>
                    </div>
                """, unsafe_allow_html=True)
                
                # Answer selection
                user_selection = st.radio(
                    "Select your answer:",
                    list(quiz_options.keys()),
                    format_func=lambda x: f"**{x}.** {quiz_options[x]}",
                    key="quiz_answer_selection"
                )

                # Submit answer
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("✅ Submit Answer", use_container_width=True):
                        st.session_state.quiz_score["total"] += 1
                        
                        if user_selection == correct_answer:
                            st.session_state.quiz_score["correct"] += 1

                            # Save updated quiz score
                            save_user_progress(current_user, "quiz_score", st.session_state.quiz_score)



                            st.success(f"🎉 Correct! Well done!")
                            if explanation:
                                st.info(f"💡 **Explanation:** {explanation}")
                        else:
                            st.error(f"❌ Incorrect. The correct answer was **{correct_answer}**: {quiz_options.get(correct_answer, 'N/A')}")
                            save_user_progress(current_user, "quiz_score", st.session_state.quiz_score)
                            if explanation:
                                st.info(f"💡 **Explanation:** {explanation}")
                        
                        # Clear current quiz after answering
                        st.session_state.current_quiz_data = None
                        
        except Exception as e:
            st.error("⚠️ Failed to parse quiz question. Please generate a new one.")
            st.session_state.current_quiz_data = None

    # Display quiz statistics
    st.markdown("---")
    total_questions = st.session_state.quiz_score["total"]
    correct_answers = st.session_state.quiz_score["correct"]
    
    if total_questions > 0:
        accuracy_percentage = (correct_answers / total_questions) * 100
        st.markdown(f"""
            <div class="score-display">
                <h3>📊 Your Quiz Performance</h3>
                <p><strong>Score:</strong> {correct_answers} / {total_questions} correct</p>
                <p><strong>Accuracy:</strong> {accuracy_percentage:.1f}%</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🚀 Generate your first question to start the quiz!")

# ============================================================================
# FLASHCARD MODE
# ============================================================================

elif selected_mode == "Flashcards":
    # Header section
    st.markdown(f"""
        <div class="page-header">
            <h1>🗂️ Flashcard Mode for {current_user}</h1>
            <p>Study key concepts with interactive flashcards!</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # ---------------- FLASHCARD TOPIC SELECTION ----------------
    st.markdown("#### 🎯 Select a Flashcard Topic")

    core_flash_topics = ["General", "Math", "Science", "History", "Programming"]
    more_flash_topics = ["Data Structures and Algorithms", "Java", "C", "Algebra", "Calculus", "Geography", "World History"]

    if "flashcard_selected_topic" not in st.session_state:
        st.session_state.flashcard_selected_topic = core_flash_topics[0]

    if "flashcard_show_more_topics" not in st.session_state:
        st.session_state.flashcard_show_more_topics = False

    def select_flashcard_topic(topic):
        st.session_state.flashcard_selected_topic = topic

    flash_cols = st.columns(len(core_flash_topics) + 1)
    for i, topic in enumerate(core_flash_topics):
        with flash_cols[i]:
            if st.button(topic, key=f"flash_core_{topic}", use_container_width=True):
                select_flashcard_topic(topic)

    with flash_cols[-1]:
        if st.button("➕ More Topics", key="flash_more_toggle", use_container_width=True):
            st.session_state.flashcard_show_more_topics = not st.session_state.flashcard_show_more_topics

    if st.session_state.flashcard_show_more_topics:
        st.markdown("##### 📚 Extended Flashcard Topics")
        extra_rows = [more_flash_topics[i:i+3] for i in range(0, len(more_flash_topics), 3)]
        for row in extra_rows:
            row_cols = st.columns(len(row))
            for i, topic in enumerate(row):
                with row_cols[i]:
                    if st.button(topic, key=f"flash_more_{topic}", use_container_width=True):
                        select_flashcard_topic(topic)

    st.markdown(f"**Current Flashcard Topic:** `{st.session_state.flashcard_selected_topic}`")
    # ✍️ Optional: Enter custom flashcard topic
    if "flashcard_show_custom_topic" not in st.session_state:
        st.session_state.flashcard_show_custom_topic = False

    if st.button("✍️ Or enter your own flashcard topic", use_container_width=True):
        st.session_state.flashcard_show_custom_topic = not st.session_state.flashcard_show_custom_topic

    if st.session_state.flashcard_show_custom_topic:
        custom_flashcard_topic = st.text_input("Enter a custom flashcard topic:", key="custom_flashcard_topic_input")
        if custom_flashcard_topic:
            st.session_state.flashcard_selected_topic = custom_flashcard_topic


    # Initialize flashcard state
    if "current_flashcard_data" not in st.session_state:
        st.session_state.current_flashcard_data = None
    if "show_flashcard_answer" not in st.session_state:
        st.session_state.show_flashcard_answer = False

    # Flashcard generation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if not st.session_state.is_pro and st.session_state.usage["flashcard_count"] >= DAILY_LIMITS["flashcard"]:
            st.session_state.usage["limit_hit"]["flashcard"] = True
            show_upgrade_modal("Flashcards")
        elif st.button("🔄 New Flashcard", use_container_width=True):
            st.session_state.usage["flashcard_count"] += 1
            save_usage()


            flashcard_prompt = (
                "Create an educational flashcard for a student studying computer science, "
                "mathematics, or general academic subjects. "
                "Format your response EXACTLY as follows:\n\n"
                "**Question:** [Clear, concise question]\n"
                "**Answer:** [Comprehensive answer with explanation]"
            )
            
            with st.spinner("📚 Creating new flashcard..."):
                try:
                    flashcard_response = client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=400,
                        temperature=0.6,
                        messages=[{"role": "user", "content": flashcard_prompt}]
                    )
                    
                    st.session_state.current_flashcard_data = flashcard_response.content[0].text.strip()
                    st.session_state.show_flashcard_answer = False
                    
                except Exception as e:
                    st.error(f"❌ Error creating flashcard: {str(e)}")

    # Display flashcard
    if st.session_state.current_flashcard_data:
        try:
            card_lines = st.session_state.current_flashcard_data.split("\n")
            
            flashcard_question = ""
            flashcard_answer = ""
            
            for line in card_lines:
                line = line.strip()
                if line.startswith("**Question:**"):
                    flashcard_question = line.replace("**Question:**", "").strip()
                elif line.startswith("**Answer:**"):
                    flashcard_answer = line.replace("**Answer:**", "").strip()

            if flashcard_question:
                # Display question
                st.markdown(f"""
                    <div class="flashcard-container">
                        <div class="flashcard-question">
                            <h3>🤔 Question</h3>
                            <p>{flashcard_question}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Show/hide answer controls
                if not st.session_state.show_flashcard_answer:
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("👁️ Reveal Answer", use_container_width=True):
                            st.session_state.show_flashcard_answer = True
                            st.rerun()
                else:
                    # Display answer
                    st.markdown(f"""
                        <div class="flashcard-answer">
                            <h3>✅ Answer</h3>
                            <p>{flashcard_answer}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("### 📊 How did you do?")
                    
                    # Self-assessment buttons
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Got it right!", use_container_width=True):
                            st.session_state.flashcard_score["got_it"] += 1
                            save_user_progress(current_user, "flashcard_score", st.session_state.flashcard_score)
                            st.success("Great job! 🎉")
                            st.session_state.current_flashcard_data = None
                            st.session_state.show_flashcard_answer = False
                    
                    with col2:
                        if st.button("❌ Need more practice", use_container_width=True):
                            st.session_state.flashcard_score["missed"] += 1
                            save_user_progress(current_user, "flashcard_score", st.session_state.flashcard_score)                   
                            st.info("No worries, keep studying! 📚")
                            st.session_state.current_flashcard_data = None
                            st.session_state.show_flashcard_answer = False
                            
        except Exception as e:
            st.error("⚠️ Failed to parse flashcard. Please generate a new one.")
            st.session_state.current_flashcard_data = None

    # Display flashcard statistics
    st.markdown("---")
    cards_correct = st.session_state.flashcard_score["got_it"]
    cards_missed = st.session_state.flashcard_score["missed"]
    total_cards = cards_correct + cards_missed
    
    if total_cards > 0:
        success_rate = (cards_correct / total_cards) * 100
        st.markdown(f"""
            <div class="score-display">
                <h3>📈 Flashcard Progress</h3>
                <p><strong>Cards mastered:</strong> {cards_correct}</p>
                <p><strong>Cards to review:</strong> {cards_missed}</p>
                <p><strong>Success rate:</strong> {success_rate:.1f}%</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🚀 Create your first flashcard to start studying!")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: var(--text-secondary); font-size: 0.9em; padding: 1rem;'>
        🤖 AI Tutor Agent - Powered by Anthropic Claude | 
        Made with ❤️ using Streamlit
    </div>
""", unsafe_allow_html=True)