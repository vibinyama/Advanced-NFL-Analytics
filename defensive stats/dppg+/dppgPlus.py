import nfl_data_py as nfl
import pandas as pd

SEASONS = list(range(1999, 2026))

all_season_results = []

for season in SEASONS:

    print(f"Processing {season}...")

    games = nfl.import_schedules([season])
    games = games.dropna(subset=["home_score", "away_score"])

    rows = []

    for _, g in games.iterrows():

        rows.append({
            "season": season,
            "team": g["home_team"],
            "opponent": g["away_team"],
            "points_scored": g["home_score"],
            "points_allowed": g["away_score"]
        })

        rows.append({
            "season": season,
            "team": g["away_team"],
            "opponent": g["home_team"],
            "points_scored": g["away_score"],
            "points_allowed": g["home_score"]
        })

    df = pd.DataFrame(rows)

    season_results = []

    for _, game in df.iterrows():

        team = game["team"]
        opponent = game["opponent"]

        opp_games = df[df["team"] == opponent]
        opp_games_excluding_team = opp_games[opp_games["opponent"] != team]

        if len(opp_games_excluding_team) == 0:
            continue

        opponent_ppg = opp_games_excluding_team["points_scored"].mean()

        dppg_plus_game = opponent_ppg - game["points_allowed"]

        season_results.append({
            "season": season,
            "team": team,
            "game_dppg_plus": dppg_plus_game
        })

    season_df = pd.DataFrame(season_results)

    team_season = (
        season_df.groupby(["season", "team"])["game_dppg_plus"]
        .mean()
        .reset_index()
    )

    all_season_results.append(team_season)

# Combine all years
final_df = pd.concat(all_season_results)

# Sort 
final_df = final_df.sort_values(["season", "game_dppg_plus"], ascending=[True, False])

print(final_df)

# Export 
final_df["game_dppg_plus"] = final_df["game_dppg_plus"].round(2)
with pd.ExcelWriter("dppg_plus_by_year.xlsx") as writer:
    for season in final_df["season"].unique():
        final_df[final_df["season"] == season].to_excel(
            writer,
            sheet_name=str(season),
            index=False
        )

print("\nExport completed")