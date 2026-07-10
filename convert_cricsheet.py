"""
Convert Cricsheet IPL CSV2 format → standard matches.csv + deliveries.csv
Handles both old names (RCB Bangalore) and new names.
"""
import zipfile, os, re, pandas as pd
from io import StringIO

BASE      = os.path.dirname(os.path.abspath(__file__))
ZIP_PATH  = os.path.join(BASE, 'ipl_csv2.zip')

TEAM_RENAME = {
    'Kings XI Punjab':             'Punjab Kings',
    'Delhi Daredevils':            'Delhi Capitals',
    'Deccan Chargers':             'Sunrisers Hyderabad',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
    'Pune Warriors':               'Defunct',
    'Kochi Tuskers Kerala':        'Defunct',
    'Rising Pune Supergiant':      'Defunct',
    'Rising Pune Supergiants':     'Defunct',
    'Gujarat Lions':               'Defunct',
}
ACTIVE_TEAMS = {
    'Chennai Super Kings','Delhi Capitals','Gujarat Titans',
    'Kolkata Knight Riders','Lucknow Super Giants','Mumbai Indians',
    'Punjab Kings','Rajasthan Royals','Royal Challengers Bengaluru',
    'Sunrisers Hyderabad',
}

def rename(t):
    t = str(t).strip()
    return TEAM_RENAME.get(t, t)

def parse_info_field(info_text, key):
    """Return list of all values for a given key from _info.csv."""
    vals = []
    for line in info_text.splitlines():
        parts = line.split(',')
        if len(parts) >= 3 and parts[0].strip() == 'info' and parts[1].strip() == key:
            vals.append(','.join(parts[2:]).strip())
    return vals

matches_rows    = []
deliveries_rows = []
match_id_counter = 0

print(f"Opening {ZIP_PATH} ...")
with zipfile.ZipFile(ZIP_PATH) as zf:
    all_names   = zf.namelist()
    info_files  = sorted([n for n in all_names if n.endswith('_info.csv')])
    match_files_set = set(all_names)
    print(f"  Found {len(info_files)} info files")

    for idx, info_name in enumerate(info_files):
        match_name = info_name.replace('_info.csv', '.csv')
        if match_name not in match_files_set:
            continue

        info_text  = zf.read(info_name).decode('utf-8', errors='ignore')
        match_text = zf.read(match_name).decode('utf-8', errors='ignore')

        # ── Parse info ───────────────────────────────
        teams_raw = parse_info_field(info_text, 'team')
        if len(teams_raw) < 2:
            continue

        team1 = rename(teams_raw[0])
        team2 = rename(teams_raw[1])

        # Allow ANY match (even with defunct teams) — we'll filter in train_model.py
        # But skip obviously bad data
        if team1 == 'Defunct' and team2 == 'Defunct':
            continue

        winner_list = parse_info_field(info_text, 'winner')
        if not winner_list:
            continue
        winner = rename(winner_list[0])
        if winner in ('', 'no result', 'tie', 'Defunct'):
            continue

        city_list = parse_info_field(info_text, 'city')
        city = city_list[0] if city_list else ''
        if not city:
            venue_list = parse_info_field(info_text, 'venue')
            city = venue_list[0].split(',')[0].strip() if venue_list else 'Unknown'

        match_id_counter += 1
        matches_rows.append({
            'id':     match_id_counter,
            'city':   city,
            'team1':  team1,
            'team2':  team2,
            'winner': winner,
        })

        # ── Parse ball-by-ball ────────────────────────
        try:
            df = pd.read_csv(StringIO(match_text))
        except Exception:
            continue

        if 'innings' not in df.columns or 'ball' not in df.columns:
            continue

        # ball column looks like "0.1", "0.2", ... "3.6" (over.ball)
        df['over_float']   = pd.to_numeric(df['ball'], errors='coerce')
        df['over']         = df['over_float'].apply(lambda x: int(x) if pd.notna(x) else 0)
        df['ball_in_over'] = df['over_float'].apply(
            lambda x: round((x - int(x)) * 10) if pd.notna(x) else 1
        )
        # ball_in_over=0 means first ball of over but in 0.x notation
        # clamp to 1–6
        df['ball_in_over'] = df['ball_in_over'].clip(lower=1)

        runs_bat    = pd.to_numeric(df.get('runs_off_bat', 0), errors='coerce').fillna(0)
        extras      = pd.to_numeric(df.get('extras',       0), errors='coerce').fillna(0)
        df['total_runs'] = (runs_bat + extras).astype(int)

        df['player_dismissed'] = df.get('player_dismissed', '').fillna('')
        df['inning']           = pd.to_numeric(df['innings'], errors='coerce').fillna(1).astype(int)
        df['batting_team']     = df.get('batting_team', '').apply(rename)
        df['bowling_team']     = df.get('bowling_team', '').apply(rename)

        for _, row in df.iterrows():
            deliveries_rows.append({
                'match_id':         match_id_counter,
                'inning':           int(row['inning']),
                'batting_team':     str(row['batting_team']),
                'bowling_team':     str(row['bowling_team']),
                'over':             int(row['over']),
                'ball':             int(row['ball_in_over']),
                'total_runs':       int(row['total_runs']),
                'player_dismissed': str(row['player_dismissed']).strip(),
            })

        if (idx + 1) % 200 == 0:
            print(f"  [{idx+1}/{len(info_files)}]  matches={len(matches_rows):,}  deliveries={len(deliveries_rows):,}")

print(f"\nDone.")
print(f"  Matches    : {len(matches_rows):,}")
print(f"  Deliveries : {len(deliveries_rows):,}")

matches_df    = pd.DataFrame(matches_rows)
deliveries_df = pd.DataFrame(deliveries_rows)

out_m = os.path.join(BASE, 'matches.csv')
out_d = os.path.join(BASE, 'deliveries.csv')
matches_df.to_csv(out_m,    index=False)
deliveries_df.to_csv(out_d, index=False)

print(f"\nSaved: {out_m}  ({os.path.getsize(out_m):,} bytes)")
print(f"Saved: {out_d} ({os.path.getsize(out_d):,} bytes)")
print(f"\nSample matches:\n{matches_df.head(5).to_string()}")
print(f"\nSample deliveries:\n{deliveries_df.head(3).to_string()}")
print(f"\nTeams in matches:\n{sorted(set(matches_df['team1'].tolist() + matches_df['team2'].tolist()))}")
