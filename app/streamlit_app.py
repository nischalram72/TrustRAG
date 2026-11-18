import streamlit as st
import sys
import os

# Add the src directory to the path so internal imports work correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
# pyrefly: ignore [missing-import]
from agent import answer_question

# Set page config for a centered, narrow layout
st.set_page_config(page_title="Trust RAG Audit", layout="centered")

css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap');

html, body {
    scroll-behavior: smooth;
}

/* Global Reset & Colors */
.stApp {
    background-color: #000000 !important;
    background: #000000 !important;
    color: #EDEEF0 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Remove default Streamlit top padding to let nav bar hit the top */
.block-container {
    padding-top: 0 !important;
    max-width: 1000px !important; /* Slightly wider for the floating stats */
}

/* Nav Bar */
.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24px 40px;
    width: 100%;
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 12px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    color: white;
    font-size: 15px;
}

.logo-circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    border: 1.5px solid rgba(255,255,255,0.4);
    display: flex;
    align-items: center;
    justify-content: center;
}

.logo-dot {
    width: 8px;
    height: 8px;
    background-color: #C9A35D;
    border-radius: 50%;
}

.nav-center {
    display: flex;
    gap: 4px;
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 999px;
    padding: 8px 4px;
}

.nav-link {
    color: rgba(255,255,255,0.7);
    font-size: 13px;
    font-family: 'Inter', sans-serif;
    text-decoration: none;
    padding: 8px 16px;
    transition: color 0.2s ease;
}

.nav-link:hover {
    color: white;
    text-decoration: none;
}

.nav-cta {
    background-color: white;
    color: black;
    font-size: 13px;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    text-decoration: none;
    border-radius: 999px;
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 6px;
    transition: opacity 0.2s ease;
}

.nav-cta:hover {
    opacity: 0.9;
    color: black;
    text-decoration: none;
}

@media (max-width: 900px) {
    .nav-center {
        display: none;
    }
}

/* Hero Section */
.hero-wrapper {
    min-height: calc(100vh - 80px);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    text-align: center;
    width: 100%;
}

.glow-gold {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(201,163,93,0.35) 0%, rgba(11,18,32,0) 70%);
    filter: blur(40px);
    z-index: 0;
    pointer-events: none;
}

.glow-blue {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(calc(-50% + 100px), calc(-50% + 100px));
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(70,90,140,0.25) 0%, rgba(11,18,32,0) 70%);
    filter: blur(40px);
    z-index: 0;
    pointer-events: none;
}

.hero-content {
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.hero-top-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.1em;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase;
    margin-bottom: 16px;
}

.hero-headline {
    color: white;
    font-size: clamp(2.5rem, 7vw, 5rem);
    line-height: 0.95;
    letter-spacing: -0.02em;
}

.hero-headline-line1 {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    display: block;
}

.hero-headline-line2 {
    font-family: 'Source Serif 4', serif;
    font-style: italic;
    display: block;
    background: linear-gradient(100deg, #C9A35D 20%, #ffffff 50%, #C9A35D 80%);
    background-size: 200% auto;
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shine 3s linear infinite;
}

@keyframes shine {
    to {
        background-position: -200% center;
    }
}

.hero-subtext {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    color: rgba(255,255,255,0.6);
    max-width: 480px;
    margin: 24px auto 0;
    text-align: center;
}

.floating-stat {
    position: absolute;
    display: flex;
    flex-direction: column;
    text-align: left;
    z-index: 1;
}

.floating-stat.top-right {
    top: 15%;
    right: 8%;
}

.floating-stat.bottom-left {
    bottom: 20%;
    left: 8%;
}

.stat-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px;
    color: white;
    line-height: 1;
    margin-bottom: 4px;
}

.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: rgba(255,255,255,0.5);
}

@media (max-width: 700px) {
    .floating-stat {
        display: none;
    }
    .nav-bar {
        padding: 16px 20px;
    }
}

/* Hide default streamlit headers */
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Style the text input */
[data-testid="stTextInput"] input {
    font-family: 'Source Serif 4', serif !important;
    font-size: 16px !important;
    background-color: rgba(255, 255, 255, 0.05) !important;
    color: #EDEEF0 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 4px !important;
    padding: 12px !important;
}

/* Answer Card */
.ledger-card {
    background-color: #0F172A;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 24px;
    margin-top: 16px;
    margin-bottom: 8px;
    position: relative;
    display: flex;
    flex-direction: column;
}

.ledger-text {
    font-family: 'Source Serif 4', serif;
    font-size: 16px;
    line-height: 1.6;
    color: #EDEEF0;
    margin-bottom: 24px;
    padding-right: 80px; /* Space for stamp */
}

/* Stamp Badge */
.stamp {
    position: absolute;
    top: 24px;
    right: 24px;
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 2px solid;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    text-transform: uppercase;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.05em;
    background: transparent;
}

.stamp.verified {
    border-color: #C9A35D;
    color: #C9A35D;
    transform: rotate(-8deg);
}

.stamp.refused {
    border-color: #E5484D;
    color: #E5484D;
    transform: rotate(6deg);
}

.stamp-icon {
    font-size: 18px;
    line-height: 1;
    margin-bottom: 2px;
}

/* Divider & Score */
.ledger-divider {
    height: 1px;
    background-color: rgba(255, 255, 255, 0.1);
    width: 100%;
    margin-bottom: 12px;
}

.ledger-score {
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    color: rgba(237, 238, 240, 0.5); /* muted gray */
    align-self: flex-end;
}

/* User Message */
.user-query {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: rgba(237, 238, 240, 0.7);
    margin-bottom: 4px;
    margin-top: 24px;
}
</style>

<div class="nav-bar">
<div class="nav-left">
<div class="logo-circle"><div class="logo-dot"></div></div>
TrustRAG
</div>
<div class="nav-center">
<a href="#" class="nav-link">How it works</a>
<a href="#" class="nav-link">Verification</a>
<a href="#" class="nav-link">Evaluation</a>
</div>
<a href="#question-section" class="nav-cta">
Ask a question <span style="font-family: sans-serif;">↓</span>
</a>
</div>

<div class="hero-wrapper">
<div class="glow-gold"></div>
<div class="glow-blue"></div>

<div class="floating-stat top-right">
<div class="stat-number">18</div>
<div class="stat-label">questions tested</div>
</div>

<div class="floating-stat bottom-left">
<div class="stat-number">0</div>
<div class="stat-label">hallucinations confirmed</div>
</div>

<div class="hero-content">
<div class="hero-top-label">Verification Engine</div>
<div class="hero-headline">
<span class="hero-headline-line1">Don't just answer.</span>
<span class="hero-headline-line2">Prove it.</span>
</div>
<div class="hero-subtext">An AI agent that fact-checks its own answers before showing them to you.</div>
</div>
</div>
<div id="question-section" style="padding-top: 2rem;"></div>
"""
st.markdown(css, unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

def render_ledger_card(result):
    status_label = "verified" if result.get('status') == 'confident' else "refused"
    icon = "✓" if status_label == "verified" else "✗"
    score = result.get('confidence', 0)
    answer_text = result.get('final_answer', result.get('reasoning', ''))
    
    html = f"""
    <div class="ledger-card">
        <div class="stamp {status_label}">
            <span class="stamp-icon">{icon}</span>
            <span>{status_label}</span>
        </div>
        <div class="ledger-text">
            {answer_text.replace(chr(10), '<br>')}
        </div>
        <div class="ledger-divider"></div>
        <div class="ledger-score">confidence {score} / 100</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
    
    with st.expander("audit trail"):
        for i, step in enumerate(result.get('trace', [])):
            step_query = step.get('query_used', '')
            step_score = step.get('confidence', 0)
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 13px; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <div style="display: flex; gap: 12px; flex: 1; padding-right: 12px;">
                    <span style="color: #64748B;">{str(i+1).zfill(2)}</span>
                    <span style="font-family: 'Inter', sans-serif; color: #EDEEF0;">{step_query}</span>
                </div>
                <span style="color: #64748B;">{step_score}</span>
            </div>
            """, unsafe_allow_html=True)
            
    with st.expander("sources used"):
        sources = result.get('sources', [])
        if sources:
            for s in sources:
                st.markdown(f"<div style=\"font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #64748B; margin-bottom: 4px;\">- {s}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style=\"font-family: 'Inter', sans-serif; font-size: 13px; color: #64748B;\">No sources utilized.</div>", unsafe_allow_html=True)

# Render history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-query">&gt; {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        if "result" in msg:
            render_ledger_card(msg["result"])
        else:
            st.markdown(f'<div class="ledger-card"><div class="ledger-text">{msg["content"]}</div></div>', unsafe_allow_html=True)

def handle_submit():
    st.session_state.current_query = st.session_state.query_input
    st.session_state.query_input = ""

if "current_query" not in st.session_state:
    st.session_state.current_query = ""

# Input area
st.text_input("Enter your query:", placeholder="Ask the analyst...", label_visibility="collapsed", key="query_input", on_change=handle_submit)

query = st.session_state.current_query
if query:
    st.markdown(f'<div class="user-query">&gt; {query}</div>', unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": query})
    st.session_state.current_query = "" # prevent re-running on normal rerenders
    
    with st.spinner("Auditing records..."):
        try:
            db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chroma_db'))
            result = answer_question(query, collection_name="test_docs", max_retries=2, db_path=db_path)
            
            render_ledger_card(result)
            
            # Store result in history
            st.session_state.messages.append({"role": "assistant", "result": result})
            
        except Exception as e:
            st.error(f"Error: {e}")
