import streamlit as st
import pickle
import pandas as pd
import os

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="IPL Win Probability Predictor",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# TEAM DATA
# ─────────────────────────────────────────────
TEAM_COLORS = {
    'Chennai Super Kings':          '#FDB913',
    'Delhi Capitals':               '#17479E',
    'Gujarat Titans':               '#B8860B',
    'Kolkata Knight Riders':        '#3A225D',
    'Lucknow Super Giants':         '#A72056',
    'Mumbai Indians':               '#004BA0',
    'Punjab Kings':                 '#DD1F2D',
    'Rajasthan Royals':             '#254AA5',
    'Royal Challengers Bengaluru':  '#EC1C24',
    'Sunrisers Hyderabad':          '#F7A721',
}

TEAM_SHORT = {
    'Chennai Super Kings':         'CSK',
    'Delhi Capitals':              'DC',
    'Gujarat Titans':              'GT',
    'Kolkata Knight Riders':       'KKR',
    'Lucknow Super Giants':        'LSG',
    'Mumbai Indians':              'MI',
    'Punjab Kings':                'PBKS',
    'Rajasthan Royals':            'RR',
    'Royal Challengers Bengaluru': 'RCB',
    'Sunrisers Hyderabad':         'SRH',
}

TEAMS = sorted(TEAM_COLORS.keys())

CITIES = sorted([
    'Ahmedabad', 'Bengaluru', 'Chandigarh', 'Chennai', 'Cuttack',
    'Delhi', 'Dharamsala', 'Dubai', 'Hyderabad', 'Indore', 'Jaipur',
    'Kanpur', 'Kochi', 'Kolkata', 'Mumbai', 'Nagpur', 'Navi Mumbai',
    'Pune', 'Raipur', 'Rajkot', 'Ranchi', 'Sharjah', 'Visakhapatnam',
    'Abu Dhabi', 'Cape Town', 'Centurion', 'Durban', 'Johannesburg',
    'Unknown',
])

# ─────────────────────────────────────────────
# PREMIUM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ─── Page background ─── */
.stApp {
    background: #080b14 !important;
}

/* ─── Hide Streamlit chrome ─── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ─── Main container width ─── */
.block-container {
    padding: 1.5rem 2rem 3rem 2rem !important;
    max-width: 1100px !important;
}

/* ══════════════════════════════════════
   HERO HEADER
══════════════════════════════════════ */
.hero {
    position: relative;
    text-align: center;
    padding: 3rem 2rem 2.5rem;
    border-radius: 24px;
    margin-bottom: 2rem;
    overflow: hidden;
    background: linear-gradient(135deg, #0d0d2b 0%, #1a0a3c 30%, #0d1f3c 65%, #071525 100%);
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow:
        0 0 0 1px rgba(245,197,24,0.08),
        0 20px 60px rgba(0,0,0,0.6),
        inset 0 1px 0 rgba(255,255,255,0.06);
}
.hero::before {
    content: "";
    position: absolute; inset: 0;
    background:
        radial-gradient(ellipse 60% 50% at 20% 0%, rgba(245,197,24,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 80% 100%, rgba(72,187,120,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 40% 60% at 50% 50%, rgba(100,100,255,0.04) 0%, transparent 70%);
    pointer-events: none;
}
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    color: #f5c518;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    position: relative;
}
.hero h1 {
    font-size: 3rem;
    font-weight: 900;
    color: #ffffff;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.03em;
    line-height: 1.1;
    position: relative;
}
.hero h1 span { color: #f5c518; }
.hero-sub {
    color: #8b9bb8;
    font-size: 1rem;
    font-weight: 400;
    margin-bottom: 1.4rem;
    position: relative;
}
.badge-row { display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap; position: relative; }
.badge {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    color: #c8d4e8;
    padding: 0.3rem 0.9rem;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    backdrop-filter: blur(4px);
}
.badge-gold {
    background: rgba(245,197,24,0.12);
    border-color: rgba(245,197,24,0.3);
    color: #f5c518;
}

/* ══════════════════════════════════════
   SECTION CARD
══════════════════════════════════════ */
.card {
    background: linear-gradient(160deg, #0f1628 0%, #111828 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 1.6rem 1.8rem 1.4rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
}
.card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(245,197,24,0.3), transparent);
}
.card-title {
    font-size: 0.7rem;
    font-weight: 700;
    color: #f5c518;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-title::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(245,197,24,0.2), transparent);
}

/* ══════════════════════════════════════
   STAT GRID
══════════════════════════════════════ */
.stat-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.8rem;
    margin-top: 0.2rem;
}
.stat-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1rem 0.6rem;
    text-align: center;
    transition: border-color 0.2s;
}
.stat-box:hover { border-color: rgba(245,197,24,0.2); }
.stat-label {
    font-size: 0.62rem;
    font-weight: 600;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.4rem;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: #e8edf5;
    line-height: 1;
}
.stat-value.highlight { color: #f5c518; }
.stat-value.danger { color: #fc8181; }

/* ══════════════════════════════════════
   PREDICT BUTTON
══════════════════════════════════════ */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #f5c518 0%, #e6a800 100%) !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important;
    font-size: 1rem !important;
    padding: 0.8rem 2rem !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 4px 20px rgba(245,197,24,0.3) !important;
    transition: all 0.2s ease !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 30px rgba(245,197,24,0.45) !important;
}

/* ══════════════════════════════════════
   RESULT SECTION
══════════════════════════════════════ */
.vs-bar-wrap {
    width: 100%;
    height: 52px;
    border-radius: 26px;
    overflow: hidden;
    display: flex;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    margin: 1rem 0 0.8rem;
}
.vs-seg {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1.05rem;
    letter-spacing: 0.01em;
    color: rgba(255,255,255,0.92);
}

.team-card {
    border-radius: 18px;
    padding: 1.6rem 1.2rem;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.06);
    position: relative;
    overflow: hidden;
}
.team-card-abbr {
    font-size: 0.65rem;
    font-weight: 800;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 0.3rem;
}
.team-card-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 0.6rem;
}
.team-card-prob {
    font-size: 3.2rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -0.03em;
}
.team-card-label {
    font-size: 0.72rem;
    color: #4a5568;
    font-weight: 500;
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.verdict-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 0.9rem 1.2rem;
    text-align: center;
    margin-top: 0.8rem;
    font-size: 0.95rem;
    font-weight: 600;
    color: #c8d4e8;
}

/* ══════════════════════════════════════
   SIDEBAR
══════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: #080b14 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
section[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}
.sidebar-logo {
    text-align: center;
    padding: 0.5rem 0 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 1.2rem;
}
.sidebar-logo-text {
    font-size: 1.1rem;
    font-weight: 800;
    color: #f5c518;
    letter-spacing: -0.02em;
}
.sidebar-logo-sub {
    font-size: 0.7rem;
    color: #4a5568;
    font-weight: 500;
    margin-top: 0.1rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.info-chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 0.7rem 0.9rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.info-chip-label { font-size: 0.72rem; color: #4a5568; font-weight: 500; }
.info-chip-value { font-size: 0.8rem; color: #c8d4e8; font-weight: 700; }

/* ══════════════════════════════════════
   STREAMLIT WIDGET OVERRIDES
══════════════════════════════════════ */
div[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
}
div[data-testid="stNumberInput"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
}
div[data-testid="stMetricValue"] { font-size: 1.4rem; }

label[data-testid="stWidgetLabel"] p {
    color: #6b7a99 !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* expander */
div[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,0.02) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────
@st.cache_resource
def load_model():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pkl_path = os.path.join(script_dir, 'pipe.pkl')
    if not os.path.exists(pkl_path):
        return None, pkl_path
    with open(pkl_path, 'rb') as f:
        return pickle.load(f), pkl_path

pipe, pkl_path = load_model()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <div class="sidebar-logo-text">🏏 IPL Predictor</div>
        <div class="sidebar-logo-sub">ML Model Dashboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("##### 🤖 Model")
    st.markdown("""
    <div class="info-chip"><span class="info-chip-label">Algorithm</span><span class="info-chip-value">Logistic Regression</span></div>
    <div class="info-chip"><span class="info-chip-label">Solver</span><span class="info-chip-value">liblinear</span></div>
    <div class="info-chip"><span class="info-chip-label">Features</span><span class="info-chip-value">62 encoded</span></div>
    <div class="info-chip"><span class="info-chip-label">Train Accuracy</span><span class="info-chip-value" style="color:#48bb78">79.97%</span></div>
    <div class="info-chip"><span class="info-chip-label">Test Accuracy</span><span class="info-chip-value" style="color:#48bb78">79.94%</span></div>
    <div class="info-chip"><span class="info-chip-label">Overfit Gap</span><span class="info-chip-value" style="color:#48bb78">0.038%</span></div>
    """, unsafe_allow_html=True)

    st.markdown("##### 📦 Dataset")
    st.markdown("""
    <div class="info-chip"><span class="info-chip-label">Source</span><span class="info-chip-value">Cricsheet IPL</span></div>
    <div class="info-chip"><span class="info-chip-label">Seasons</span><span class="info-chip-value">2008 – 2025</span></div>
    <div class="info-chip"><span class="info-chip-label">Matches</span><span class="info-chip-value">1,105</span></div>
    <div class="info-chip"><span class="info-chip-label">Deliveries</span><span class="info-chip-value">279,996</span></div>
    <div class="info-chip"><span class="info-chip-label">Train rows</span><span class="info-chip-value">99,500</span></div>
    <div class="info-chip"><span class="info-chip-label">Test rows</span><span class="info-chip-value">24,876</span></div>
    """, unsafe_allow_html=True)

    st.markdown("##### ⚙️ Pipeline")
    st.code("""ColumnTransformer
  OneHotEncode:
    batting_team
    bowling_team
    city
  PassThrough:
    runs_left
    balls_left
    wickets_left
    target, crr, rrr
↓
LogisticRegression
↓
predict_proba()""", language="text")

    st.markdown("##### 🛠️ Stack")
    st.markdown("""
    <div class="info-chip"><span class="info-chip-label">Frontend</span><span class="info-chip-value">Streamlit 1.59</span></div>
    <div class="info-chip"><span class="info-chip-label">ML</span><span class="info-chip-value">Scikit-Learn 1.7</span></div>
    <div class="info-chip"><span class="info-chip-label">Data</span><span class="info-chip-value">Pandas 2.3</span></div>
    <div class="info-chip"><span class="info-chip-label">Compute</span><span class="info-chip-value">NumPy 2.3</span></div>
    <div class="info-chip"><span class="info-chip-label">Language</span><span class="info-chip-value">Python 3.13</span></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1.5rem; padding-top:1rem; border-top:1px solid rgba(255,255,255,0.06);
    text-align:center; font-size:0.68rem; color:#2d3748; font-weight:500; letter-spacing:0.05em;">
    AI / ML CAPSTONE PROJECT
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">AI / ML Capstone Project</div>
    <h1>🏏 IPL Win <span>Probability</span> Predictor</h1>
    <p class="hero-sub">Real-time win probability powered by Logistic Regression trained on 17 seasons of ball-by-ball data</p>
    <div class="badge-row">
        <span class="badge badge-gold">🤖 Logistic Regression</span>
        <span class="badge">📊 1,105 Matches</span>
        <span class="badge">🎯 79.97% Accuracy</span>
        <span class="badge">📅 2008 – 2025</span>
    </div>
</div>
""", unsafe_allow_html=True)

if pipe is None:
    st.error(f"🚨 Model not found at `{pkl_path}`. Run `python train_model.py` first.")
    st.stop()

# ─────────────────────────────────────────────
# MATCH SETUP
# ─────────────────────────────────────────────
st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#f5c518;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;'>⚙️ &nbsp; MATCH SETUP</div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    batting_team = st.selectbox("🏏 Batting Team", TEAMS, index=5)
with c2:
    bowling_options = [t for t in TEAMS if t != batting_team]
    bowling_team = st.selectbox("🎯 Bowling Team", bowling_options, index=0)
with c3:
    selected_city = st.selectbox("🏙️ Host City", CITIES, index=CITIES.index('Mumbai'))

st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:1.2rem 0 1rem;'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# MATCH SITUATION
# ─────────────────────────────────────────────
st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#f5c518;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.5rem;'>📊 &nbsp; CURRENT MATCH SITUATION</div>", unsafe_allow_html=True)

c4, c5 = st.columns(2)
with c4:
    target = st.number_input("🎯 Target Score", min_value=1, max_value=350, value=175, step=1)
with c5:
    current_score = st.number_input("🏏 Current Score", min_value=0, max_value=350, value=80, step=1)

c6, c7, c8 = st.columns(3)
with c6:
    overs_done = st.number_input("⏱️ Overs Completed", min_value=0, max_value=19, value=9, step=1)
with c7:
    balls_done = st.number_input("🎾 Balls in This Over (0–5)", min_value=0, max_value=5, value=0, step=1)
with c8:
    wickets_out = st.number_input("❌ Wickets Fallen", min_value=0, max_value=10, value=2, step=1)

# ─────────────────────────────────────────────
# DERIVED FEATURES
# ─────────────────────────────────────────────
total_balls   = overs_done * 6 + balls_done
balls_left    = max(120 - total_balls, 0)
runs_left     = target - current_score
wickets_left  = 10 - wickets_out
crr           = (current_score * 6) / max(total_balls, 1)
rrr           = (runs_left * 6) / balls_left if balls_left > 0 else 0.0

# ─────────────────────────────────────────────
# LIVE STATS
# ─────────────────────────────────────────────
st.markdown("<hr style='border:none;border-top:1px solid rgba(255,255,255,0.06);margin:1.2rem 0 1rem;'>", unsafe_allow_html=True)
st.markdown("<div style='font-size:0.7rem;font-weight:700;color:#f5c518;text-transform:uppercase;letter-spacing:0.14em;margin-bottom:0.8rem;'>📈 &nbsp; LIVE MATCH STATS</div>", unsafe_allow_html=True)

rrr_class = "danger" if rrr > 12 else ("highlight" if rrr < 7 else "")
crr_class = "highlight" if crr > rrr else ""

st.markdown(f"""
<div class="stat-grid">
    <div class="stat-box">
        <div class="stat-label">Runs Left</div>
        <div class="stat-value">{runs_left}</div>
    </div>
    <div class="stat-box">
        <div class="stat-label">Balls Left</div>
        <div class="stat-value">{balls_left}</div>
    </div>
    <div class="stat-box">
        <div class="stat-label">Wickets Left</div>
        <div class="stat-value {'danger' if wickets_left <= 2 else ''}">{wickets_left}</div>
    </div>
    <div class="stat-box">
        <div class="stat-label">CRR</div>
        <div class="stat-value {crr_class}">{crr:.2f}</div>
    </div>
    <div class="stat-box">
        <div class="stat-label">RRR</div>
        <div class="stat-value {rrr_class}">{"N/A" if balls_left == 0 else f"{rrr:.2f}"}</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────
errors = []
if batting_team == bowling_team:
    errors.append("Batting and Bowling teams cannot be the same.")
if current_score >= target:
    errors.append(f"**{batting_team}** has already reached the target — match over!")
if wickets_out == 10:
    errors.append(f"**{batting_team}** is all out — match over!")
if balls_left <= 0:
    errors.append("No balls remaining — match over!")

# ─────────────────────────────────────────────
# PREDICT BUTTON
# ─────────────────────────────────────────────
predict = st.button("🔮  Predict Win Probability", use_container_width=True, type="primary")

if predict:
    if errors:
        for e in errors:
            st.error(e)
    else:
        inp = pd.DataFrame({
            'batting_team': [batting_team], 'bowling_team': [bowling_team],
            'city': [selected_city], 'runs_left': [runs_left],
            'balls_left': [balls_left], 'wickets_left': [wickets_left],
            'target': [float(target)], 'crr': [crr], 'rrr': [rrr],
        })
        try:
            proba     = pipe.predict_proba(inp)[0]
            win_p     = max(0.01, min(0.99, float(proba[1])))
            lose_p    = 1.0 - win_p
            bat_col   = TEAM_COLORS.get(batting_team, '#48bb78')
            bowl_col  = TEAM_COLORS.get(bowling_team, '#fc8181')
            bat_short = TEAM_SHORT.get(batting_team, batting_team[:3].upper())
            bowl_short= TEAM_SHORT.get(bowling_team, bowling_team[:3].upper())

            # ---- VS Bar ----
            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        margin-bottom:0.3rem;font-weight:700;font-size:0.9rem;color:#8b9bb8;">
                <span style="color:{bat_col};font-weight:800;">{bat_short}</span>
                <span style="font-size:0.7rem;letter-spacing:0.1em;color:#2d3748">WIN PROBABILITY</span>
                <span style="color:{bowl_col};font-weight:800;">{bowl_short}</span>
            </div>
            <div class="vs-bar-wrap">
                <div class="vs-seg" style="width:{win_p*100:.1f}%;background:{bat_col};">
                    {win_p*100:.1f}%
                </div>
                <div class="vs-seg" style="width:{lose_p*100:.1f}%;background:{bowl_col};">
                    {lose_p*100:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ---- Team Cards ----
            r1, r2 = st.columns(2)
            with r1:
                st.markdown(f"""
                <div class="team-card" style="background:linear-gradient(150deg,{bat_col}18,#0a0d1a 60%);">
                    <div class="team-card-abbr" style="color:{bat_col};">{bat_short}</div>
                    <div class="team-card-name">{batting_team}</div>
                    <div class="team-card-prob" style="color:{bat_col};">{win_p*100:.1f}%</div>
                    <div class="team-card-label">Win Probability</div>
                </div>
                """, unsafe_allow_html=True)
            with r2:
                st.markdown(f"""
                <div class="team-card" style="background:linear-gradient(150deg,{bowl_col}18,#0a0d1a 60%);">
                    <div class="team-card-abbr" style="color:{bowl_col};">{bowl_short}</div>
                    <div class="team-card-name">{bowling_team}</div>
                    <div class="team-card-prob" style="color:{bowl_col};">{lose_p*100:.1f}%</div>
                    <div class="team-card-label">Win Probability</div>
                </div>
                """, unsafe_allow_html=True)

            # ---- Verdict ----
            if win_p > 0.70:
                verdict = f"📊 <strong>{batting_team}</strong> is heavily favoured from here."
                v_color = "#48bb78"
            elif win_p > 0.55:
                verdict = f"📊 <strong>{batting_team}</strong> has the slight edge — still competitive."
                v_color = "#68d391"
            elif win_p > 0.45:
                verdict = "⚖️ <strong>Neck and neck!</strong> Could go either way."
                v_color = "#f6ad55"
            else:
                verdict = f"📊 <strong>{bowling_team}</strong> is in control — tough ask for {batting_team}."
                v_color = "#fc8181"

            st.markdown(f"""
            <div class="verdict-box" style="border-color:rgba(255,255,255,0.08);color:{v_color};">
                {verdict}
            </div>
            """, unsafe_allow_html=True)

        except Exception as ex:
            st.error(f"Prediction error: {ex}")

# ── Floating ? Help Button (CSS checkbox trick — no JS needed) ───────────────
st.markdown("""
<style>
/* Hidden toggle checkbox */
#help-toggle { display: none; }

/* The floating ? label acts as button */
label[for="help-toggle"] {
    position: fixed; bottom: 2rem; right: 2rem;
    width: 50px; height: 50px; border-radius: 50%;
    background: linear-gradient(135deg, #f5c518, #e6a800);
    color: #0a0a0a; font-size: 1.5rem; font-weight: 900;
    box-shadow: 0 4px 20px rgba(245,197,24,0.5);
    cursor: pointer; z-index: 99999;
    display: flex; align-items: center; justify-content: center;
    transition: transform 0.2s, box-shadow 0.2s;
    user-select: none;
}
label[for="help-toggle"]:hover {
    transform: scale(1.12);
    box-shadow: 0 6px 28px rgba(245,197,24,0.7);
}

/* Overlay — hidden by default, shown when checkbox checked */
#help-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,0.75); z-index: 99998;
    align-items: center; justify-content: center;
}
#help-toggle:checked ~ #help-overlay { display: flex; }

/* Close label (the X button inside modal) */
label[for="help-toggle"].close-x {
    position: absolute; top: 1rem; right: 1rem;
    width: 30px; height: 30px; border-radius: 50%;
    background: rgba(255,255,255,0.08);
    color: #8b9bb8; font-size: 0.9rem; font-weight: 400;
    box-shadow: none; bottom: auto; right: 1rem;
}
label[for="help-toggle"].close-x:hover {
    background: rgba(255,255,255,0.18); color: #fff;
    transform: none; box-shadow: none;
}

/* Modal box */
#help-modal {
    background: #0f1628; border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px; padding: 2rem; max-width: 540px; width: 90%;
    color: #e2e8f0; font-family: Inter, sans-serif;
    box-shadow: 0 20px 60px rgba(0,0,0,0.7);
    position: relative; max-height: 80vh; overflow-y: auto;
}
#help-modal h2 { color: #f5c518; font-size: 1.15rem; font-weight: 800; margin: 0 0 1rem; }
#help-modal table { width: 100%; border-collapse: collapse; font-size: 0.82rem; margin: 0.6rem 0; }
#help-modal th { color: #f5c518; text-align: left; padding: 0.4rem 0.6rem;
    border-bottom: 1px solid rgba(255,255,255,0.08); font-size: 0.7rem;
    text-transform: uppercase; letter-spacing: 0.06em; }
#help-modal td { padding: 0.35rem 0.6rem; border-bottom: 1px solid rgba(255,255,255,0.04); color: #c8d4e8; }
#help-modal code { background: rgba(255,255,255,0.06); border-radius: 4px;
    padding: 0.1rem 0.4rem; font-size: 0.78rem; color: #f5c518; }
#help-modal pre { background: rgba(0,0,0,0.3); border-radius: 10px;
    padding: 0.8rem 1rem; font-size: 0.78rem; color: #a0aec0;
    border: 1px solid rgba(255,255,255,0.06); margin: 0.5rem 0; }
#help-modal p, #help-modal li { font-size: 0.84rem; line-height: 1.6; color: #8b9bb8; }
#help-modal ul { padding-left: 1.2rem; }
#help-modal li { margin-bottom: 0.3rem; }
</style>

<!-- Hidden checkbox that controls open/close state -->
<input type="checkbox" id="help-toggle">

<!-- Floating ? button -->
<label for="help-toggle">?</label>

<!-- Modal overlay (sibling of checkbox so CSS :checked works) -->
<div id="help-overlay">
  <div id="help-modal">
    <label for="help-toggle" class="close-x">&#x2715;</label>
    <h2>&#x1F9E0; How does the ML model predict?</h2>
    <p>Your inputs become <strong>62 features</strong> fed into a Logistic Regression model trained on <strong>99,500 real IPL deliveries</strong>.</p>
    <table>
      <tr><th>Feature</th><th>How computed</th></tr>
      <tr><td><code>batting_team</code></td><td>OneHot &rarr; 10 binary cols</td></tr>
      <tr><td><code>bowling_team</code></td><td>OneHot &rarr; 10 binary cols</td></tr>
      <tr><td><code>city</code></td><td>OneHot &rarr; 39 binary cols</td></tr>
      <tr><td><code>runs_left</code></td><td>Target &minus; Current Score</td></tr>
      <tr><td><code>balls_left</code></td><td>120 &minus; balls bowled</td></tr>
      <tr><td><code>wickets_left</code></td><td>10 &minus; wickets fallen</td></tr>
      <tr><td><code>target</code></td><td>1st innings total</td></tr>
      <tr><td><code>crr</code></td><td>Score &times; 6 &divide; balls bowled</td></tr>
      <tr><td><code>rrr</code></td><td>Runs left &times; 6 &divide; balls left</td></tr>
    </table>
    <p><strong style="color:#f5c518">Formula:</strong></p>
    <pre>z = w1*runs_left + ... + w62*city_Mumbai
P(win) = 1 / (1 + e^(-z))</pre>
    <p><strong style="color:#f5c518">Why Logistic Regression?</strong></p>
    <ul>
      <li>Outputs smooth, calibrated win probabilities</li>
      <li><strong>79.97% accuracy</strong> on 24,876 test samples</li>
      <li>Train vs test gap only <strong>0.038%</strong> &mdash; no overfitting</li>
      <li>Fast and interpretable &mdash; every weight means something</li>
    </ul>
  </div>
</div>
""", unsafe_allow_html=True)
