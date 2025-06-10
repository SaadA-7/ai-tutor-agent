import os
import streamlit as st
from dotenv import load_dotenv
from anthropic import Anthropic
from streamlit_option_menu import option_menu

# Load key
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
client = Anthropic(api_key=api_key)

# Track theme (light/dark)
if "theme" not in st.session_state:
  st.session_state.theme = "dark"  # default to dark

# Page config
st.set_page_config(page_title="AI Tutor", layout="centered")

# Sidebar navigation
with st.sidebar:
    st.markdown("### 👤 User Login")

    username = st.text_input("Enter your name to start:", value=st.session_state.get("username", ""))
    if username:
        st.session_state.username = username

    name = st.session_state.get("username", "Student")

    if st.button("🔄 Reset Progress"):
        for key in [
            "messages", "quiz_score", "flashcard_score",
            "current_quiz", "current_flashcard", "show_answer"
        ]:
            if key in st.session_state:
                del st.session_state[key]
        st.success("Progress reset. You can start fresh!")

    st.markdown("---")

    selected = option_menu(
        menu_title="📘 AI Tutor Modes",
        options=["Q&A", "Quiz Mode", "Flashcards"],
        icons=["chat", "check2-circle", "journal-text"],
        default_index=0
    )

    st.markdown("**🎨 Theme**")
    theme_choice = st.radio("Choose theme:", ["dark", "light"], index=0 if st.session_state.theme == "dark" else 1)
    st.session_state.theme = theme_choice

# Theme styling map
def get_colors():
    if st.session_state.theme == "dark":
        return {
            "user_bg": "#1f1f2e",
            "user_text": "#99ccff",
            "tutor_bg": "#2d3b3b",
            "tutor_text": "#b2f0b2",
            "main_bg": "#0e1117",
            "text": "#ffffff"
        }
    else:
        return {
            "user_bg": "#e6f0ff",
            "user_text": "#003366",
            "tutor_bg": "#e8f5e9",
            "tutor_text": "#2e7d32",
            "main_bg": "#ffffff",
            "text": "#000000"
        }

colors = get_colors()

theme_class = "dark" if st.session_state.theme == "dark" else "light"
theme_mode = "dark" if st.session_state.theme == "dark" else "light"
st.markdown(
    f"""
    <script>
        const app = window.parent.document.querySelector('.stApp');
        if (app) {{
            app.setAttribute('data-theme', '{theme_mode}');
        }}
    </script>
    """,
    unsafe_allow_html=True
)


# Load external CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)






# Shared session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quiz_score" not in st.session_state:
    st.session_state.quiz_score = {"correct": 0, "total": 0}

# ---------------- Q&A MODE ----------------
if selected == "Q&A":
    st.markdown(f"<h1 style='text-align: center;'>📘 Q&A Tutor for {name}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Ask anything academic, get an explanation.</p>", unsafe_allow_html=True)
    st.markdown("---")

    with st.form(key="chat_form"):
        user_input = st.text_input("💬 Your Question", placeholder="e.g., What is a linked list?")
        submit = st.form_submit_button("Ask")

    if submit and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Tutor is thinking..."):
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=512,
                temperature=0.5,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            answer = response.content[0].text
            st.session_state.messages.append({"role": "assistant", "content": answer})

    # Apply custom colors
    user_bg = colors["user_bg"]
    user_text = colors["user_text"]
    tutor_bg = colors["tutor_bg"]
    tutor_text = colors["tutor_text"]

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"<div style='background:{user_bg};padding:10px;border-radius:10px;margin-bottom:5px;'><b style='color:{user_text};'>You:</b> {msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background:{tutor_bg};padding:10px;border-radius:10px;margin-bottom:10px;'><b style='color:{tutor_text};'>Tutor:</b> {msg['content']}</div>",
                unsafe_allow_html=True
            )

# ---------------- QUIZ MODE ----------------
elif selected == "Quiz Mode":
    st.markdown(f"<h1 style='text-align: center;'>🧠 Quiz Mode for {name}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Test your knowledge with multiple choice questions!</p>", unsafe_allow_html=True)
    st.markdown("---")

    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None

    if st.button("🎲 Generate New Question"):
        prompt = (
            "Create a multiple choice quiz question on a general computer science topic. "
            "Format it as:\n\n"
            "**Question:** <text>\n"
            "**A.** <choice>\n**B.** <choice>\n**C.** <choice>\n**D.** <choice>\n"
            "**Answer:** <letter>"
        )
        with st.spinner("Generating question..."):
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=512,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            quiz_text = response.content[0].text.strip()
            st.session_state.current_quiz = quiz_text

    if st.session_state.current_quiz:
        try:
            lines = st.session_state.current_quiz.split("\n")
            question = next(line for line in lines if line.startswith("**Question:**")).replace("**Question:**", "").strip()
            options = {}
            for line in lines:
                if line.startswith("**A.**"):
                    options["A"] = line.replace("**A.**", "").strip()
                elif line.startswith("**B.**"):
                    options["B"] = line.replace("**B.**", "").strip()
                elif line.startswith("**C.**"):
                    options["C"] = line.replace("**C.**", "").strip()
                elif line.startswith("**D.**"):
                    options["D"] = line.replace("**D.**", "").strip()
            correct_line = next(line for line in lines if "**Answer:**" in line)
            correct = correct_line.split("**Answer:**")[-1].strip().upper()

            st.markdown(f"**{question}**")
            user_answer = st.radio("Choose your answer:", list(options.keys()), format_func=lambda x: f"{x}. {options[x]}")

            if st.button("Submit Answer"):
                st.session_state.quiz_score["total"] += 1
                if user_answer == correct:
                    st.success("✅ Correct!")
                    st.session_state.quiz_score["correct"] += 1
                else:
                    st.error(f"❌ Incorrect. The correct answer was {correct}. {options[correct]}")
        except Exception as e:
            st.error("⚠️ Failed to parse the quiz question. Try again.")
            st.session_state.current_quiz = None

    st.markdown("---")
    st.markdown(f"**Score:** {st.session_state.quiz_score['correct']} / {st.session_state.quiz_score['total']}")


    # ---------------- FLASHCARD MODE ----------------
elif selected == "Flashcards":
    st.markdown(f"<h1 style='text-align: center;'>🃏 Flashcard Mode for {name}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Flip through key concepts and test your memory.</p>", unsafe_allow_html=True)
    st.markdown("---")

    # Init state
    if "current_flashcard" not in st.session_state:
        st.session_state.current_flashcard = None
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False
    if "flashcard_score" not in st.session_state:
        st.session_state.flashcard_score = {"got_it": 0, "missed": 0}

    # Generate new flashcard
    if st.button("🔄 New Flashcard"):
        prompt = (
            "Create a flashcard for a computer science student. Format it as:\n"
            "**Question:** <question text>\n**Answer:** <answer text>"
        )
        with st.spinner("Fetching flashcard..."):
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )
            st.session_state.current_flashcard = response.content[0].text.strip()
            st.session_state.show_answer = False

    if st.session_state.current_flashcard:
        lines = st.session_state.current_flashcard.split("\n")
        q_text = lines[0].replace("**Question:**", "").strip()
        a_text = lines[1].replace("**Answer:**", "").strip()

        st.markdown(f"📘 **Question:** {q_text}")

        if not st.session_state.show_answer:
            if st.button("👁️ Show Answer"):
                st.session_state.show_answer = True
        else:
            st.markdown(f"✅ **Answer:** {a_text}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Got it"):
                    st.session_state.flashcard_score["got_it"] += 1
                    st.session_state.current_flashcard = None
            with col2:
                if st.button("❌ Missed it"):
                    st.session_state.flashcard_score["missed"] += 1
                    st.session_state.current_flashcard = None

    st.markdown("---")
    got = st.session_state.flashcard_score["got_it"]
    missed = st.session_state.flashcard_score["missed"]
    st.markdown(f"**Flashcard Accuracy:** {got} correct, {missed} missed")
