import pandas as pd
import numpy as np
import pickle
import os
import sys
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# ---------------------------------------------
# TEAM NAME NORMALISATION
# ---------------------------------------------
TEAM_RENAME = {
    'Kings XI Punjab':              'Punjab Kings',
    'Delhi Daredevils':             'Delhi Capitals',
    'Deccan Chargers':              'Sunrisers Hyderabad',
    'Royal Challengers Bangalore':  'Royal Challengers Bengaluru',
    'Pune Warriors':                'Defunct',
    'Kochi Tuskers Kerala':         'Defunct',
    'Rising Pune Supergiant':       'Defunct',
    'Rising Pune Supergiants':      'Defunct',
    'Gujarat Lions':                'Defunct',
}

ACTIVE_TEAMS = {
    'Chennai Super Kings',
    'Delhi Capitals',
    'Gujarat Titans',
    'Kolkata Knight Riders',
    'Lucknow Super Giants',
    'Mumbai Indians',
    'Punjab Kings',
    'Rajasthan Royals',
    'Royal Challengers Bengaluru',
    'Sunrisers Hyderabad',
}


# ---------------------------------------------
# HELPER: flexible column finder
# ---------------------------------------------
def find_col(df: pd.DataFrame, candidates: list, label: str) -> str:
    """Return first candidate column name present in df, else raise."""
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(f"Could not find {label} column. Tried: {candidates}. "
                   f"Available columns: {list(df.columns)}")


def main():
    # -- locate CSVs ----------------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    matches_path    = os.path.join(script_dir, 'matches.csv')
    deliveries_path = os.path.join(script_dir, 'deliveries.csv')

    for p in [matches_path, deliveries_path]:
        if not os.path.exists(p):
            sys.exit(f"ERROR: '{p}' not found. "
                     "Place matches.csv and deliveries.csv next to train_model.py.")

    print("Loading CSVs ...")
    matches    = pd.read_csv(matches_path)
    deliveries = pd.read_csv(deliveries_path)

    print(f"  matches    : {matches.shape}")
    print(f"  deliveries : {deliveries.shape}")
    print(f"  matches cols    : {list(matches.columns)}")
    print(f"  deliveries cols : {list(deliveries.columns)}")

    # -- normalise match ID columns --------------
    match_id_col = find_col(matches, ['id', 'ID', 'match_id', 'MatchID'], 'match-id in matches')
    if match_id_col != 'id':
        matches.rename(columns={match_id_col: 'id'}, inplace=True)

    del_id_col = find_col(deliveries, ['match_id', 'id', 'ID', 'MatchID'], 'match-id in deliveries')
    if del_id_col != 'match_id':
        deliveries.rename(columns={del_id_col: 'match_id'}, inplace=True)

    # -- normalise winner column -----------------
    if 'winner' not in matches.columns:
        winner_col = find_col(matches, ['WinningTeam', 'Winner', 'winning_team'], 'winner')
        matches.rename(columns={winner_col: 'winner'}, inplace=True)

    # -- normalise city column -------------------
    if 'city' not in matches.columns:
        city_col = find_col(matches, ['City', 'venue_city', 'Venue', 'venue'], 'city')
        matches.rename(columns={city_col: 'city'}, inplace=True)

    # -- normalise inning column -----------------
    if 'inning' not in deliveries.columns:
        inning_col = find_col(deliveries, ['innings', 'Innings', 'inning_number'], 'inning')
        deliveries.rename(columns={inning_col: 'inning'}, inplace=True)

    # -- normalise over/ball columns -------------
    over_col = find_col(deliveries, ['over', 'Over', 'overs'], 'over')
    if over_col != 'over':
        deliveries.rename(columns={over_col: 'over'}, inplace=True)

    ball_col = find_col(deliveries, ['ball', 'Ball', 'ball_number'], 'ball')
    if ball_col != 'ball':
        deliveries.rename(columns={ball_col: 'ball'}, inplace=True)

    # -- normalise total_runs column -------------
    if 'total_runs' not in deliveries.columns:
        tr_col = find_col(deliveries, ['runs_off_bat', 'total_runs_scored', 'runs'], 'total_runs')
        deliveries.rename(columns={tr_col: 'total_runs'}, inplace=True)

    # -- normalise player_dismissed column -------
    if 'player_dismissed' not in deliveries.columns:
        try:
            pd_col = find_col(deliveries, ['wicket_type', 'is_wicket', 'dismissed_player'], 'player_dismissed')
            deliveries.rename(columns={pd_col: 'player_dismissed'}, inplace=True)
        except KeyError:
            deliveries['player_dismissed'] = np.nan   # create empty column

    # ---------------------------------------------
    # STEP 1 . TEAM NAME CLEANING
    # ---------------------------------------------
    print("\nApplying team-name mapping ...")
    for col in ['team1', 'team2', 'toss_winner', 'winner']:
        if col in matches.columns:
            matches[col] = matches[col].replace(TEAM_RENAME)

    for col in ['batting_team', 'bowling_team']:
        if col in deliveries.columns:
            deliveries[col] = deliveries[col].replace(TEAM_RENAME)

    # ---------------------------------------------
    # STEP 2 . FILTER TO ACTIVE TEAMS ONLY
    # ---------------------------------------------
    before = len(matches)
    matches = matches[
        matches['team1'].isin(ACTIVE_TEAMS) &
        matches['team2'].isin(ACTIVE_TEAMS)
    ].copy()
    print(f"  Active-team filter: {before} -> {len(matches)} matches")

    # Drop DL-affected matches
    if 'dl_applied' in matches.columns:
        matches = matches[matches['dl_applied'] == 0].copy()
    elif 'method' in matches.columns:
        matches = matches[matches['method'].isna() | (matches['method'] == '')].copy()

    # Keep only matches with a winner
    matches = matches[matches['winner'].notna()].copy()
    print(f"  After DL+winner filter: {len(matches)} matches")

    # ---------------------------------------------
    # STEP 3 . COMPUTE 1ST-INNINGS TARGET
    # ---------------------------------------------
    first_inn = deliveries[deliveries['inning'] == 1].copy()
    targets = (
        first_inn.groupby('match_id')['total_runs']
        .sum()
        .reset_index()
        .rename(columns={'total_runs': 'first_innings_score'})
    )
    targets['target'] = targets['first_innings_score'] + 1

    # ---------------------------------------------
    # STEP 4 . BUILD BALL-BY-BALL SECOND INNINGS DF
    # ---------------------------------------------
    match_meta = matches[['id', 'city', 'winner']].copy()
    match_meta['city'] = match_meta['city'].fillna('Unknown')

    # Merge target
    match_meta = match_meta.merge(targets[['match_id', 'target']],
                                  left_on='id', right_on='match_id',
                                  how='inner').drop(columns=['match_id'])

    # Keep only 2nd-innings deliveries for these matches
    second_inn = deliveries[
        (deliveries['inning'] == 2) &
        (deliveries['match_id'].isin(match_meta['id']))
    ].copy()

    print(f"  2nd-innings deliveries: {len(second_inn)}")

    # Merge match metadata
    df = second_inn.merge(match_meta, left_on='match_id', right_on='id', how='inner')

    # Sort ball-by-ball
    df = df.sort_values(['match_id', 'over', 'ball']).reset_index(drop=True)

    # ---------------------------------------------
    # STEP 5 . FEATURE ENGINEERING
    # ---------------------------------------------

    # Detect over indexing (0-based vs 1-based)
    min_over = df['over'].min()
    if min_over == 1:                      # 1-based -> convert to 0-based
        df['over'] = df['over'] - 1
        print("  Over column was 1-based; converted to 0-based.")

    # Detect ball indexing (1-based is standard in ball-by-ball data)
    # ball 1 of over 0 -> 1 ball delivered so far
    df['balls_bowled'] = df['over'] * 6 + df['ball']   # cumulative balls if sequential
    # However ball column resets each over, so this is correct for 1-based ball

    # Cumulative score per match
    df['current_score'] = df.groupby('match_id')['total_runs'].cumsum()

    # Balls left AFTER this delivery
    df['balls_left'] = 120 - df['balls_bowled']

    # Runs left AFTER this delivery
    df['runs_left'] = df['target'] - df['current_score']

    # Wickets - build binary dismissed flag robustly
    df['is_wicket'] = df['player_dismissed'].apply(
        lambda x: 0 if (pd.isna(x) or str(x).strip() in ('', 'nan', '0', 'None')) else 1
    )
    df['wickets_fallen'] = df.groupby('match_id')['is_wicket'].cumsum()
    df['wickets_left']   = 10 - df['wickets_fallen']

    # CRR - avoid div/0 on the very first ball
    df['crr'] = (df['current_score'] * 6) / df['balls_bowled'].replace(0, 1)

    # Drop balls_left == 0 (end-of-innings rows; can't calculate RRR)
    df = df[df['balls_left'] > 0].copy()

    # RRR
    df['rrr'] = (df['runs_left'] * 6) / df['balls_left']

    # Result label
    df['result'] = (df['batting_team'] == df['winner']).astype(int)

    # ---------------------------------------------
    # STEP 6 . SELECT FINAL FEATURE SET
    # ---------------------------------------------
    FEATURES = ['batting_team', 'bowling_team', 'city',
                'runs_left', 'balls_left', 'wickets_left',
                'target', 'crr', 'rrr']
    TARGET   = 'result'

    final_df = df[FEATURES + [TARGET]].dropna().copy()

    # Ensure string type for categoricals
    for c in ['batting_team', 'bowling_team', 'city']:
        final_df[c] = final_df[c].astype(str)

    # Clip RRR to reasonable range to remove extreme outlier rows
    final_df = final_df[(final_df['rrr'] >= 0) & (final_df['rrr'] <= 36)]

    print(f"\nFinal dataset shape: {final_df.shape}")
    print(f"  Win %: {final_df[TARGET].mean():.3f}")

    # ---------------------------------------------
    # STEP 7 . TRAIN / TEST SPLIT & PIPELINE
    # ---------------------------------------------
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)

    X = final_df[FEATURES]
    y = final_df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    cat_cols = ['batting_team', 'bowling_team', 'city']
    num_cols = ['runs_left', 'balls_left', 'wickets_left', 'target', 'crr', 'rrr']

    preprocessor = ColumnTransformer([
        ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False), cat_cols)
    ], remainder='passthrough')   # num_cols pass through

    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('model', LogisticRegression(solver='liblinear', max_iter=1000, C=1.0))
    ])

    print("\nTraining model ...")
    pipe.fit(X_train, y_train)

    train_acc = pipe.score(X_train, y_train)
    test_acc  = pipe.score(X_test,  y_test)
    print(f"  Train Accuracy : {train_acc:.4f}")
    print(f"  Test  Accuracy : {test_acc:.4f}")

    # ---------------------------------------------
    # STEP 8 . SAVE
    # ---------------------------------------------
    out_path = os.path.join(script_dir, 'pipe.pkl')
    with open(out_path, 'wb') as f:
        pickle.dump(pipe, f)
    print(f"\n[OK]  Pipeline saved -> {out_path}")


if __name__ == '__main__':
    main()
