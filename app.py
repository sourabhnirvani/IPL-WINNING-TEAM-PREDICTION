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
# TEAM BRAND COLORS (used to color-code results)
# ─────────────────────────────────────────────
TEAM_COLORS = {
    'Chennai Super Kings':          {'main': '#FDB913', 'text': '#1a1a1a'},
    'Delhi Capitals':               {'main': '#17479E', 'text': '#ffffff'},
    'Gujarat Titans':               {'main': '#1B2133', 'text': '#B8860B'},
    'Kolkata Knight Riders':        {'main': '#3A225D', 'text': '#FFD700'},
    'Lucknow Super Giants':         {'main': '#A72056', 'text': '#00B2CA'},
    'Mumbai Indians':               {'main': '#004BA0', 'text': '#FFD700'},
    'Punjab Kings':                 {'main': '#DD1F2D', 'text': '#ffffff'},
    'Rajasthan Royals':             {'main': '#254AA5', 'text': '#FF69B4'},
    'Royal Challengers Bengaluru':  {'main': '#EC1C24', 'text': '#FFD700'},
    'Sunrisers Hyderabad':          {'main': '#F7A721', 'text': '#1a1a1a'},
}

TEAM_EMOJI = {
    'Chennai Super Kings':         '🦁',
    'Delhi Capitals':              '🩵',
    'Gujarat Titans':              '🦈',
    'Kolkata Knight Riders':       '🐦',
    'Lucknow Super Giants':        '🦢',
    'Mumbai Indians':              '💙',
    'Punjab Kings':                '👑',
    'Rajasthan Royals':            '💗',
    'Royal Challengers Bengaluru': '🔴',
    'Sunrisers Hyderabad':         '🧡',
}

TEAMS = sorted(TEAM_COLORS.keys())

CITIES = sorted([
    'Ahmedabad', 'Bengaluru', 'Chandigarh', 'Chennai', 'Cuttack',
    'Delhi', 'Dharamsala', 'Dubai', 'Hyderabad', 'Indore', 'Jaipur',
    'Kanpur', 'Kimberley', 'Kochi', 'Kolkata', 'Mumbai', 'Nagpur',
    'Navi Mumbai', 'Pune', 'Raipur', 'Rajkot', 'Ranchi', 'Sharjah',
    'Visakhapatnam', 'Abu Dhabi', 'Bloemfontein', 'Cape Town', 'Centurion',
    'Durban', 'East London', 'Johannesburg', 'Port Elizabeth',
    'Unknown',
])

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

#MainMenu, footer, header { visibility: hidden; }

.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1150px; }

/* ---- Header ---- */
.main-header {
    text-align: center;
    padding: 2.2rem 1rem 1.8rem 1rem;
    background: linear-gradient(120deg, #0f0c29 0%, #302b63 45%, #24243e 100%);
    border-radius: 18px;
    margin-bottom: 1.6rem;
    box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: "";
    position: absolute; inset: 0;
    background: radial-gradient(circle at 15% 20%, rgba(245,197,24,0.15), transparent 40%),
                radial-gradient(circle at 85% 80%, rgba(72,187,120,0.15), transparent 40%);
}
.main-header h1 {
    font-size: 2.6rem; font-weight: 800; color: #f5c518; margin: 0;
    letter-spacing: -0.02em; position: relative;
}
.main-header p {
    color: #c3c9e0; font-size: 1.02rem; margin-top: 0.5rem;
    font-weight: 500; position: relative;
}
.header-badges { margin-top: 0.9rem; position: relative; }
.header-badge {
    display: inline-block; background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15); color: #e2e8f0;
    padding: 0.25rem 0.8rem; border-radius: 20px; font-size: 0.78rem;
    font-weight: 600; margin: 0 0.25rem;
}

/* ---- Section cards ---- */
.section-card {
    background: linear-gradient(150deg, #161a2b, #1b2033);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.4rem 1.6rem 1.1rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 4px 18px rgba(0,0,0,0.18);
}
.section-title {
    font-size: 1.05rem; font-weight: 700; color: #f5c518;
    margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem;
}
.section-label {
    font-size: 0.8rem; font-weight: 600; color: #8b93b0;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.3rem;
}

/* ---- Live stats ---- */
.stat-pill {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px; padding: 0.7rem 0.5rem; text-align: center;
}
.stat-pill .label { font-size: 0.72rem; color: #8b93b0; text-transform: uppercase; letter-spacing: 0.05em; }
.stat-pill .value { font-size: 1.4rem; font-weight: 700; color: #f0f2f8; margin-top: 0.15rem; }

/* ---- Win probability bar ---- */
.matchup-row {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.7rem; font-weight: 700; font-size: 1.05rem;
}
.prob-bar-wrap {
    width: 100%; height: 46px; border-radius: 23px; overflow: hidden;
    display: flex; box-shadow: inset 0 2px 6px rgba(0,0,0,0.35); margin-bottom: 0.6rem;
}
.prob-bar-seg {
    height: 100%; display: flex; align-items: center; justify-content: center;
    font-weight: 800; font-size: 1rem; transition: width 0.6s ease;
    white-space: nowrap;
}

.result-card {
    border-radius: 14px; padding: 1.3rem 1rem; text-align: center;
    border: 1px solid rgba(255,255,255,0.08);
}
.result-team { font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem; }
.result-prob { font-size: 2.5rem; font-weight: 800; margin: 0.1rem 0; }

.footer-note { text-align: center; color: #5a6178; font-size: 0.8rem; margin-top: 2rem; }

div[data-testid="stMetricValue"] { font-size: 1.6rem; }
div.stButton > button {
    border-radius: 12px; font-weight: 700; padding: 0.7rem 0; font-size: 1.05rem;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD MODEL (cached)
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
# SIDEBAR — ML EXPLAINED
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 ML Model Info")
    st.markdown("---")

    st.markdown("### 📚 Algorithm")
    st.info("**Logistic Regression**\n\nOutputs calibrated win/loss probabilities via `predict_proba()` — not just a binary yes/no.")

    st.markdown("### 🏗️ Pipeline Architecture")
    st.code("""
Pipeline(
  Step 1: ColumnTransformer
    - OneHotEncoder
        batting_team  (10 teams)
        bowling_team  (10 teams)
        city          (39 venues)
    - PassThrough
        runs_left
        balls_left
        wickets_left
        target
        crr  (current run rate)
        rrr  (required run rate)

  Step 2: LogisticRegression
    solver = liblinear
    output = predict_proba()
)""", language="text")

    st.markdown("### 📊 Training Stats")
    col_a, col_b = st.columns(2)
    col_a.metric("Train Acc", "79.97%")
    col_b.metric("Test Acc",  "79.94%")
    st.caption("Overfitting gap: 0.038% — near zero = healthy")

    st.markdown("### 🗃️ Dataset")
    st.markdown("""
- **Source**: Cricsheet IPL (2008-2025)
- **Matches**: 1,105 (active teams only)
- **Deliveries**: 279,996 ball-by-ball rows
- **Training rows**: 99,500
- **Test rows**: 24,876
    """)

    st.markdown("### ⚙️ Features Used")
    st.markdown("""
| Feature | Type |
|---|---|
| batting_team | Categorical |
| bowling_team | Categorical |
| city | Categorical |
| runs_left | Numeric |
| balls_left | Numeric |
| wickets_left | Numeric |
| target | Numeric |
| crr | Numeric |
| rrr | Numeric |
    """)

    st.markdown("### 🛠️ Tech Stack")
    st.markdown("""
- 🐍 **Python 3.13**
- 🎈 **Streamlit 1.59**
- 🤖 **Scikit-Learn 1.7**
- 🐼 **Pandas 2.3**
- 🔢 **NumPy 2.3**
    """)
    st.markdown("---")
    st.caption("AI/ML Capstone Project — IPL Win Prediction")

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🏏 IPL Win Probability Predictor</h1>
    <p>Live win-probability estimation from match-situation features</p>
    <div class="header-badges">
        <span class="header-badge">🤖 Logistic Regression</span>
        <span class="header-badge">📊 1,105 matches</span>
        <span class="header-badge">🎯 79.97% accuracy</span>
    </div>
</div>
""", unsafe_allow_html=True)

if pipe is None:
    st.error(f"""
    🚨 **Model file not found!**
    Expected: `{pkl_path}`
    Run `python train_model.py` first to generate `pipe.pkl`.
    """)
    st.stop()

# ─────────────────────────────────────────────
# INPUTS — MATCH SETUP
# ─────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚙️ Match Setup</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    batting_team = st.selectbox("🏏 Batting Team", TEAMS, index=0)
with c2:
    bowling_options = [t for t in TEAMS if t != batting_team]
    bowling_team = st.selectbox("🎯 Bowling Team", bowling_options, index=0)
with c3:
    selected_city = st.selectbox("🏙️ Host City", CITIES)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# INPUTS — MATCH SITUATION
# ─────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📊 Current Match Situation</div>', unsafe_allow_html=True)

c4, c5 = st.columns(2)
with c4:
    target = st.number_input("🎯 Target (runs to chase)", min_value=1, max_value=350, value=175, step=1)
with c5:
    current_score = st.number_input("🏏 Current Score", min_value=0, max_value=350, value=80, step=1)

c6, c7, c8 = st.columns(3)
with c6:
    overs_done = st.number_input("⏱️ Overs Completed (whole overs only)", min_value=0, max_value=19, value=9, step=1)
with c7:
    balls_done = st.number_input("🎾 Balls in Current Over (0-5)", min_value=0, max_value=5, value=0, step=1)
with c8:
    # BUG FIX: was max_value=9, making the "all out" validation branch dead code.
    # A team can be bowled out (10 wickets), so max is 10.
    wickets_out = st.number_input("❌ Wickets Fallen", min_value=0, max_value=10, value=2, step=1)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DERIVED FEATURES
# ─────────────────────────────────────────────
total_balls_bowled = overs_done * 6 + balls_done
balls_left         = 120 - total_balls_bowled
runs_left          = target - current_score
wickets_left       = 10 - wickets_out

crr = (current_score * 6) / max(total_balls_bowled, 1)
rrr = (runs_left * 6) / balls_left if balls_left > 0 else 0.0

# ─────────────────────────────────────────────
# LIVE STATS DISPLAY
# ─────────────────────────────────────────────
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📈 Live Match Stats</div>', unsafe_allow_html=True)
ms1, ms2, ms3, ms4, ms5 = st.columns(5)
stats = [
    (ms1, "Runs Left",    str(runs_left)),
    (ms2, "Balls Left",   str(max(balls_left, 0))),
    (ms3, "Wickets Left", str(wickets_left)),
    (ms4, "CRR",          f"{crr:.2f}"),
    (ms5, "RRR",          f"{rrr:.2f}" if balls_left > 0 else "N/A"),
]
for col, label, value in stats:
    col.markdown(f"""
    <div class="stat-pill">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────
errors = []
if batting_team == bowling_team:
    errors.append("Batting and Bowling teams cannot be the same.")
if current_score >= target:
    errors.append(f"**{batting_team}** has already reached/surpassed the target — match is over!")
if wickets_out == 10:
    errors.append(f"**{batting_team}** is all out — match is over!")
if balls_left <= 0:
    errors.append("No balls remaining — match is over!")

# ─────────────────────────────────────────────
# PREDICT BUTTON
# ─────────────────────────────────────────────
predict_btn = st.button("🔮 Predict Win Probability", use_container_width=True, type="primary")

if predict_btn:
    if errors:
        for e in errors:
            st.error(e)
    else:
        input_df = pd.DataFrame({
            'batting_team':  [batting_team],
            'bowling_team':  [bowling_team],
            'city':          [selected_city],
            'runs_left':     [runs_left],
            'balls_left':    [balls_left],
            'wickets_left':  [wickets_left],
            'target':        [float(target)],
            'crr':           [crr],
            'rrr':           [rrr],
        })

        try:
            proba     = pipe.predict_proba(input_df)[0]
            win_prob  = max(0.01, min(0.99, float(proba[1])))
            lose_prob = 1.0 - win_prob

            bat_color  = TEAM_COLORS.get(batting_team, {'main': '#48bb78', 'text': '#ffffff'})
            bowl_color = TEAM_COLORS.get(bowling_team, {'main': '#fc8181', 'text': '#ffffff'})
            bat_emoji  = TEAM_EMOJI.get(batting_team,  '🏏')
            bowl_emoji = TEAM_EMOJI.get(bowling_team,  '🎯')

            bat_pct  = win_prob  * 100
            bowl_pct = lose_prob * 100

            st.markdown("### 🏆 Win Probability")

            # ---- Proportional stacked bar ----
            st.markdown(f"""
            <div class="matchup-row">
                <span>{bat_emoji} {batting_team}</span>
                <span>{bowl_emoji} {bowling_team}</span>
            </div>
            <div class="prob-bar-wrap">
                <div class="prob-bar-seg"
                     style="width:{bat_pct}%; background:{bat_color['main']}; color:{bat_color['text']};">
                    {bat_pct:.1f}%
                </div>
                <div class="prob-bar-seg"
                     style="width:{bowl_pct}%; background:{bowl_color['main']}; color:{bowl_color['text']};">
                    {bowl_pct:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ---- Team result cards ----
            r1, r2 = st.columns(2)
            with r1:
                st.markdown(f"""
                <div class="result-card"
                     style="background:linear-gradient(150deg,{bat_color['main']}22,#161a2b);">
                    <div class="result-team">{bat_emoji} {batting_team}</div>
                    <div class="result-prob" style="color:{bat_color['main']};">{bat_pct:.1f}%</div>
                    <div style="color:#8b93b0;font-size:0.85rem;">to win</div>
                </div>
                """, unsafe_allow_html=True)
            with r2:
                st.markdown(f"""
                <div class="result-card"
                     style="background:linear-gradient(150deg,{bowl_color['main']}22,#161a2b);">
                    <div class="result-team">{bowl_emoji} {bowling_team}</div>
                    <div class="result-prob" style="color:{bowl_color['main']};">{bowl_pct:.1f}%</div>
                    <div style="color:#8b93b0;font-size:0.85rem;">to win</div>
                </div>
                """, unsafe_allow_html=True)

            # ---- Context message ----
            if win_prob > 0.70:
                st.success(f"📊 **{batting_team}** is heavily favoured to win from here.")
            elif win_prob > 0.55:
                st.info(f"📊 **{batting_team}** has a slight edge, but the match is still competitive.")
            elif win_prob > 0.45:
                st.warning("📊 **Neck-and-neck!** Either team could win from here.")
            else:
                st.error(f"📊 **{bowling_team}** has the advantage — a tough ask for {batting_team}.")

        except Exception as ex:
            st.error(f"Prediction error: {ex}")
            st.info("Make sure the model was trained with the same feature set expected by app.py.")

# ─────────────────────────────────────────────
# HOW DOES ML PREDICT THIS? — expandable
# ─────────────────────────────────────────────
st.markdown("---")
with st.expander("🧠 How does the ML model make this prediction?", expanded=False):
    st.markdown("""
    ### Step-by-Step: From Your Inputs to Win Probability

    **1. You enter the match situation:**
    > Batting Team, Bowling Team, City, Target, Score, Overs, Wickets

    **2. The app computes 9 features automatically:**
    | Feature | Formula | Meaning |
    |---|---|---|
    | `runs_left` | Target - Current Score | How many runs still needed |
    | `balls_left` | 120 - balls bowled | How many deliveries remain |
    | `wickets_left` | 10 - wickets fallen | Batting resources remaining |
    | `target` | Entered directly | 1st innings total + 1 |
    | `crr` | Score x 6 / balls bowled | Current run rate |
    | `rrr` | Runs left x 6 / balls left | Run rate needed to win |
    | `batting_team` | OneHotEncoded | 10-team binary vector |
    | `bowling_team` | OneHotEncoded | 10-team binary vector |
    | `city` | OneHotEncoded | 39-venue binary vector |

    **3. These 9 features become 62 numerical inputs after encoding**

    **4. The Logistic Regression model applies learned weights:**
    ```
    z = w1*runs_left + w2*balls_left + w3*wickets_left + ... + w62*city_Mumbai
    P(batting team wins) = 1 / (1 + e^(-z))   <- Sigmoid function
    ```

    **5. Output: Two probabilities that always sum to 100%**
    > e.g., Mumbai Indians: 73.2% | Chennai Super Kings: 26.8%

    ---
    ### Why Logistic Regression?
    - Outputs **smooth probabilities** (not just win/lose)
    - **Interpretable** — each feature has a clear weight
    - **Fast inference** — predictions in milliseconds
    - **80% accuracy** on 24,876 real IPL ball-by-ball test samples
    - Used in research papers on cricket win prediction

    ---
    ### Training Data Used
    The model was trained on **99,500 ball-by-ball snapshots** from
    **1,105 real IPL matches (2008-2025)** sourced from Cricsheet.
    Each row represents a single delivery in the 2nd innings,
    labelled 1 (batting team won) or 0 (bowling team won).
    """)


