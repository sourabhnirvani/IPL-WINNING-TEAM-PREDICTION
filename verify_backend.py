import pickle
import pandas as pd
import numpy as np
import sys
import sklearn
import streamlit
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

print('=' * 60)
print('TECHNOLOGY STACK VERIFICATION')
print('=' * 60)
print(f'  Python         : {sys.version.split()[0]}')
print(f'  Streamlit      : {streamlit.__version__}')
print(f'  Scikit-Learn   : {sklearn.__version__}')
print(f'  Pandas         : {pd.__version__}')
print(f'  NumPy          : {np.__version__}')

# ─────────────────────────────────────────────
print()
print('=' * 60)
print('DATASET VERIFICATION')
print('=' * 60)
matches    = pd.read_csv('matches.csv')
deliveries = pd.read_csv('deliveries.csv')
print(f'  matches.csv    : {matches.shape[0]:,} rows x {matches.shape[1]} cols')
print(f'  deliveries.csv : {deliveries.shape[0]:,} rows x {deliveries.shape[1]} cols')
print(f'  Teams in data  : {sorted(set(matches["team1"].unique().tolist()))}')
print(f'  Unique cities  : {matches["city"].nunique()}')
print(f'  Unique matches : {deliveries["match_id"].nunique()}')

# ─────────────────────────────────────────────
print()
print('=' * 60)
print('MODEL PIPELINE VERIFICATION')
print('=' * 60)
with open('pipe.pkl', 'rb') as f:
    pipe = pickle.load(f)

preprocessor = pipe.named_steps['preprocessor']
model        = pipe.named_steps['model']

print(f'  Pipeline type     : {type(pipe).__name__}')
print(f'  Pipeline steps    : {[s[0] for s in pipe.steps]}')
print(f'  Preprocessor      : {type(preprocessor).__name__} (OneHotEncodes teams + city)')
print(f'  Model             : {type(model).__name__}')
print(f'  Solver            : {model.solver}')
print(f'  Classes           : {model.classes_}  (0=bowling wins, 1=batting wins)')
print(f'  Feature count     : {model.coef_.shape[1]}')
print(f'  Has predict_proba : {hasattr(model, "predict_proba")}')

# ─────────────────────────────────────────────
print()
print('=' * 60)
print('ACCURACY ON HELD-OUT TEST SET')
print('=' * 60)

TEAM_RENAME = {
    'Kings XI Punjab': 'Punjab Kings',
    'Delhi Daredevils': 'Delhi Capitals',
    'Deccan Chargers': 'Sunrisers Hyderabad',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
}
ACTIVE_TEAMS = {
    'Chennai Super Kings','Delhi Capitals','Gujarat Titans',
    'Kolkata Knight Riders','Lucknow Super Giants','Mumbai Indians',
    'Punjab Kings','Rajasthan Royals','Royal Challengers Bengaluru',
    'Sunrisers Hyderabad',
}

# Reload fresh
matches    = pd.read_csv('matches.csv')
deliveries = pd.read_csv('deliveries.csv')

for col in ['team1', 'team2', 'winner']:
    if col in matches.columns:
        matches[col] = matches[col].replace(TEAM_RENAME)
for col in ['batting_team', 'bowling_team']:
    if col in deliveries.columns:
        deliveries[col] = deliveries[col].replace(TEAM_RENAME)

matches = matches[
    matches['team1'].isin(ACTIVE_TEAMS) &
    matches['team2'].isin(ACTIVE_TEAMS) &
    matches['winner'].notna()
].copy()

first_inn = deliveries[deliveries['inning'] == 1].copy()
targets   = first_inn.groupby('match_id')['total_runs'].sum().reset_index()
targets['target'] = targets['total_runs'] + 1

match_meta = matches[['id', 'city', 'winner']].copy()
match_meta['city'] = match_meta['city'].fillna('Unknown')
match_meta = match_meta.merge(
    targets[['match_id', 'target']], left_on='id', right_on='match_id', how='inner'
).drop(columns=['match_id'])

second_inn = deliveries[
    (deliveries['inning'] == 2) &
    (deliveries['match_id'].isin(match_meta['id']))
].copy()

df = second_inn.merge(match_meta, left_on='match_id', right_on='id', how='inner')
df = df.sort_values(['match_id', 'over', 'ball']).reset_index(drop=True)

df['current_score']  = df.groupby('match_id')['total_runs'].cumsum()
df['balls_bowled']   = df['over'] * 6 + df['ball']
df['balls_left']     = 120 - df['balls_bowled']
df['runs_left']      = df['target'] - df['current_score']
df['is_wicket']      = df['player_dismissed'].apply(
    lambda x: 0 if (pd.isna(x) or str(x).strip() in ('', 'nan', '0', 'None')) else 1
)
df['wickets_fallen'] = df.groupby('match_id')['is_wicket'].cumsum()
df['wickets_left']   = 10 - df['wickets_fallen']
df['crr']            = (df['current_score'] * 6) / df['balls_bowled'].replace(0, 1)
df = df[df['balls_left'] > 0].copy()
df['rrr']            = (df['runs_left'] * 6) / df['balls_left']
df['result']         = (df['batting_team'] == df['winner']).astype(int)

for c in ['batting_team', 'bowling_team', 'city']:
    df[c] = df[c].astype(str)
df = df[(df['rrr'] >= 0) & (df['rrr'] <= 36)]

FEATURES = ['batting_team', 'bowling_team', 'city',
            'runs_left', 'balls_left', 'wickets_left', 'target', 'crr', 'rrr']
final_df = df[FEATURES + ['result']].dropna().sample(frac=1, random_state=42)

X = final_df[FEATURES]
y = final_df['result']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_acc = pipe.score(X_train, y_train)
test_acc  = pipe.score(X_test,  y_test)
y_pred    = pipe.predict(X_test)

print(f'  Training samples : {len(X_train):,}')
print(f'  Test samples     : {len(X_test):,}')
print(f'  Train Accuracy   : {train_acc*100:.2f}%')
print(f'  Test  Accuracy   : {test_acc*100:.2f}%')
print(f'  Overfitting gap  : {abs(train_acc - test_acc)*100:.4f}%  (near 0 = healthy)')
print()
print('  Classification Report:')
print(classification_report(y_test, y_pred,
      target_names=['Bowling Team Wins', 'Batting Team Wins']))

cm = confusion_matrix(y_test, y_pred)
print(f'  Confusion Matrix:')
print(f'    [TN={cm[0][0]:5,}  FP={cm[0][1]:5,}]  <- Actual: Bowling team won')
print(f'    [FN={cm[1][0]:5,}  TP={cm[1][1]:5,}]  <- Actual: Batting team won')

# ─────────────────────────────────────────────
print()
print('=' * 60)
print('PREDICTION SANITY TESTS')
print('=' * 60)

# Test 1: Almost certain batting win
easy = pd.DataFrame({
    'batting_team': ['Mumbai Indians'], 'bowling_team': ['Chennai Super Kings'],
    'city': ['Mumbai'], 'runs_left': [5], 'balls_left': [30],
    'wickets_left': [8], 'target': [150], 'crr': [9.5], 'rrr': [1.0]
})
p_easy = pipe.predict_proba(easy)[0]
result_easy = 'PASS' if p_easy[1] > 0.90 else 'FAIL'
print(f'  [1] Easy chase (5 runs, 30 balls, 8 wkts):')
print(f'      Mumbai Indians = {p_easy[1]*100:.1f}%  (expected > 90%) -> {result_easy}')

# Test 2: Near impossible
hard = pd.DataFrame({
    'batting_team': ['Mumbai Indians'], 'bowling_team': ['Chennai Super Kings'],
    'city': ['Mumbai'], 'runs_left': [70], 'balls_left': [12],
    'wickets_left': [2], 'target': [180], 'crr': [6.0], 'rrr': [35.0]
})
p_hard = pipe.predict_proba(hard)[0]
result_hard = 'PASS' if p_hard[1] < 0.05 else 'FAIL'
print(f'  [2] Near impossible (70 runs, 12 balls, 2 wkts):')
print(f'      Mumbai Indians = {p_hard[1]*100:.1f}%  (expected < 5%) -> {result_hard}')

# Test 3: 50-50 match
balanced = pd.DataFrame({
    'batting_team': ['Chennai Super Kings'], 'bowling_team': ['Mumbai Indians'],
    'city': ['Chennai'], 'runs_left': [30], 'balls_left': [30],
    'wickets_left': [5], 'target': [160], 'crr': [8.0], 'rrr': [6.0]
})
p_bal = pipe.predict_proba(balanced)[0]
result_bal = 'PASS' if 0.30 < p_bal[1] < 0.70 else 'FAIL'
print(f'  [3] Balanced game (30 runs, 30 balls, 5 wkts):')
print(f'      Chennai Super Kings = {p_bal[1]*100:.1f}%  (expected 30-70%) -> {result_bal}')

# ─────────────────────────────────────────────
print()
all_pass = (result_easy == 'PASS') and (result_hard == 'PASS') and (result_bal == 'PASS')
print('=' * 60)
if all_pass:
    print('FINAL VERDICT: MODEL IS CORRECTLY TRAINED - ALL CHECKS PASSED')
else:
    print('FINAL VERDICT: SOME SANITY CHECKS FAILED - REVIEW NEEDED')
print('=' * 60)
