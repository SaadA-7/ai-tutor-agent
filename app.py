import os
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from streamlit_option_menu import option_menu

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
            --primary-bg: #ffffff;
            --secondary-bg: #f8fafc;
            --sidebar-bg: #f1f5f9;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --accent-color: #6366f1;
            --accent-hover: #4f46e5;
            --accent-light: #a5b4fc;
            --warm-accent: #f59e0b;
            --success-accent: #10b981;
            --input-bg: #ffffff;
            --input-border: #e2e8f0;
            --form-bg: #f8fafc;
            --button-bg: #6366f1;
            --button-hover: #4f46e5;
            --button-text: #ffffff;
            --user-bubble-bg: #ddd6fe;
            --user-bubble-text: #5b21b6;
            --tutor-bubble-bg: #d1fae5;
            --tutor-bubble-text: #065f46;
            --success-color: #10b981;
            --error-color: #ef4444;
            --warning-color: #f59e0b;
            --border-color: #e2e8f0;
            --shadow-color: rgba(0, 0, 0, 0.1);
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
    # User login section
    st.markdown("### 👤 User Login")
    
    username_input = st.text_input(
        "Enter your name to start:", 
        value=st.session_state.get("username", ""),
        placeholder="Your name here..."
    )
    
    if username_input:
        st.session_state.username = username_input
    
    current_user = st.session_state.get("username", "Student")
    
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
            "container": {"padding": "0!important"},
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
        "World History", "Java", "C", "Python", "Geography"
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
    if submit_question and user_question.strip():
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
            {"role": "system", "content": topic_context}
        ] + [
            {"role": msg["role"], "content": msg["content"]}
            for msg in st.session_state.messages
        ]
        ai_response = client.messages.create(
            model="claude-3-haiku-20240307",
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

    # Initialize quiz state
    if "current_quiz_data" not in st.session_state:
        st.session_state.current_quiz_data = None

    # Quiz generation controls
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎲 Generate New Question", use_container_width=True):
            quiz_prompt = (
                "Create a multiple choice quiz question on a computer science, mathematics, "
                "or general academic topic suitable for students. "
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
                            st.success(f"🎉 Correct! Well done!")
                            if explanation:
                                st.info(f"💡 **Explanation:** {explanation}")
                        else:
                            st.error(f"❌ Incorrect. The correct answer was **{correct_answer}**: {quiz_options.get(correct_answer, 'N/A')}")
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

    # Initialize flashcard state
    if "current_flashcard_data" not in st.session_state:
        st.session_state.current_flashcard_data = None
    if "show_flashcard_answer" not in st.session_state:
        st.session_state.show_flashcard_answer = False

    # Flashcard generation
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 New Flashcard", use_container_width=True):
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
                            st.success("Great job! 🎉")
                            st.session_state.current_flashcard_data = None
                            st.session_state.show_flashcard_answer = False
                    
                    with col2:
                        if st.button("❌ Need more practice", use_container_width=True):
                            st.session_state.flashcard_score["missed"] += 1
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