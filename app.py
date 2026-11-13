import json
import random
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Quiz Generator", page_icon="🧠", layout="wide")

st.markdown("""
<style>
.stApp {background: #0b1020; color: #f4f6ff;}
[data-testid="stSidebar"] {background: #10172a;}
h1, h2, h3, p, label {color: #f4f6ff !important;}
div.stButton > button {border-radius: 10px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)

if "questions" not in st.session_state:
    st.session_state.questions = []
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "submitted" not in st.session_state:
    st.session_state.submitted = False

st.title("🧠 AI Quiz Generator")
st.caption("Create and attempt topic-based multiple-choice quizzes.")

with st.sidebar:
    st.header("Quiz Settings")
    topic = st.text_input("Topic", placeholder="e.g. CNN, EDA, Python, Machine Learning")
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    count = st.number_input("Number of MCQs", min_value=3, max_value=30, value=10, step=1)
    extra = st.text_area("Optional instructions", placeholder="e.g. Focus on definitions and practical concepts")
    generate = st.button("✨ Generate MCQs", type="primary", use_container_width=True)
    st.divider()
    st.caption("Add your API key in Streamlit Secrets as OPENAI_API_KEY.")

def get_client():
    key = st.secrets.get("OPENAI_API_KEY", None)
    if not key:
        return None
    return OpenAI(api_key=key)

def make_questions(topic, difficulty, count, extra):
    client = get_client()
    if client is None:
        st.error("API key missing. Add OPENAI_API_KEY in Streamlit → App settings → Secrets.")
        return []
    prompt = f"""
Create exactly {count} original multiple-choice questions for the topic: {topic}.
Difficulty: {difficulty}.
Additional instructions: {extra or "Cover a balanced range of important concepts."}

Return ONLY valid JSON in this exact structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "Exact text of the correct option",
      "explanation": "One or two sentence explanation"
    }}
  ]
}}
Rules:
- Every question must have exactly four distinct options.
- Only one option is correct.
- The answer must exactly match one option.
- Avoid duplicate questions.
- Keep the requested difficulty appropriate.
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a careful educational quiz creator. Return valid JSON only."},
            {"role": "user", "content": prompt}
        ]
    )
    data = json.loads(response.choices[0].message.content)
    qs = data.get("questions", [])
    valid = []
    for q in qs:
        opts = q.get("options", [])
        ans = q.get("answer", "")
        if q.get("question") and len(opts) == 4 and ans in opts:
            valid.append(q)
    return valid

if generate:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        with st.spinner("AI is preparing your MCQs..."):
            try:
                st.session_state.questions = make_questions(topic.strip(), difficulty, int(count), extra.strip())
                st.session_state.answers = {}
                st.session_state.submitted = False
            except Exception as e:
                st.error(f"Could not generate the quiz: {e}")

if st.session_state.questions:
    qs = st.session_state.questions
    st.subheader(f"Your Quiz · {len(qs)} Questions")
    st.write(f"**Topic:** {topic or 'Selected topic'}  |  **Difficulty:** {difficulty}")
    with st.form("quiz_form"):
        for i, q in enumerate(qs):
            st.markdown(f"**Q{i+1}. {q['question']}**")
            choice = st.radio(
                "Choose one answer:",
                q["options"],
                index=None,
                key=f"answer_{i}",
                label_visibility="collapsed"
            )
            st.session_state.answers[i] = choice
            st.divider()
        submitted = st.form_submit_button("Submit Quiz", type="primary", use_container_width=True)

    if submitted:
        st.session_state.submitted = True

    if st.session_state.submitted:
        score = sum(
            1 for i, q in enumerate(qs)
            if st.session_state.answers.get(i) == q["answer"]
        )
        total = len(qs)
        pct = round(score / total * 100, 1) if total else 0
        st.subheader("📊 Your Result")
        c1, c2, c3 = st.columns(3)
        c1.metric("Score", f"{score}/{total}")
        c2.metric("Percentage", f"{pct}%")
        c3.metric("Correct", score)
        if pct >= 80:
            st.success("Excellent work!")
        elif pct >= 50:
            st.info("Good effort. Review the explanations below.")
        else:
            st.warning("Keep practicing. You can improve!")
        st.subheader("Answer Review")
        for i, q in enumerate(qs):
            chosen = st.session_state.answers.get(i)
            correct = chosen == q["answer"]
            st.markdown(f"**Q{i+1}. {q['question']}**")
            st.write(f"Your answer: {chosen or 'Not answered'}")
            st.write(f"Correct answer: {q['answer']}")
            st.write(f"Explanation: {q.get('explanation', 'No explanation provided.')}")
            if correct:
                st.success("Correct")
            else:
                st.error("Incorrect")
            st.divider()
        if st.button("Create Another Quiz"):
            st.session_state.questions = []
            st.session_state.answers = {}
            st.session_state.submitted = False
            st.rerun()
else:
    st.info("Enter a topic in the sidebar and select a difficulty to generate your first quiz.")
