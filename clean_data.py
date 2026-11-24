"""
clean_data.py
Builds the datasets used in the Premier League wages vs attacking output project.

Inputs (put in the same folder as this script):
  - Wages_from_Fbref_via_Capology.xlsx
  - Standard_performance_measurement_for_this_season.xlsx

Outputs:
  - pl_wages_performance_merged.csv  (all players with both wages and stats)
  - pl_value_rankings.csv            (attackers + attacking midfielders, with efficiency model)
  - pbi_attackers.csv                (same as above, for Power BI)
"""
import csv
import io

import numpy as np
import pandas as pd

WAGES_FILE = "Wages_from_Fbref_via_Capology.xlsx"
STATS_FILE = "Standard_performance_measurement_for_this_season.xlsx"

MIN_MINUTES = 450          # ignore players with very little playing time
GAP_THRESHOLD = 0.2        # efficiency gap needed to label a player under/overpaid

# FBref only tags players FW / MF / DF / GK, so attacking midfielders and wingers
# tagged "MF" are added by hand, chosen by ROLE (not by output).
# This is a judgement call: edit the list to suit.
ATTACKING_MIDFIELDERS = [
    "Bukayo Saka", "Martin Ødegaard", "Noni Madueke", "Christos Tzolis",
    "Johan Manzambi", "Justin Kluivert", "Jaidon Anthony", "Pascal Groß",
    "Morgan Rogers", "Cole Palmer", "Yéremy Pino", "Oscar Bobb", "Alex Iwobi",
    "Julio Enciso", "Daizen Maeda", "Dominik Szoboszlai", "Cody Gakpo",
    "Bradley Barcola", "Florian Wirtz", "Rayan Cherki", "Antoine Semenyo",
    "Bruno Fernandes", "Nicolás González", "Harvey Barnes", "Jacob Murphy",
    "Morgan Gibbs-White", "Dan Ndoye", "Nilson Angulo", "Enzo Le Fée",
    "Tatsuhiro Sakamoto", "Tyrique George", "Daichi Kamada",
]


def read_single_column_excel(path):
    """The Excel exports hold one CSV line per cell in column A. Return the lines."""
    return pd.read_excel(path, header=None)[0].astype(str).tolist()


def load_wages():
    lines = read_single_column_excel(WAGES_FILE)
    df = pd.read_csv(io.StringIO("\n".join(lines)))

    # "£ 525000 (€ ...)" -> 525000
    for col, new in [("Weekly Wages", "weekly_wage_gbp"), ("Annual Wages", "annual_wage_gbp")]:
        df[new] = (df[col].str.extract(r"£\s*([\d,]+)")[0]
                          .str.replace(",", "").astype(float))

    df["wage_is_estimate"] = df["Notes"].notna()
    df = df.rename(columns={"Player-additional": "player_id", "Player": "player",
                            "Squad": "squad", "Pos": "pos", "Age": "age"})

    # Rows with no FBref ID (-9999) can't be matched to stats, so drop them
    df = df[df["player_id"] != "-9999"]
    df = df.drop_duplicates("player_id")
    return df[["player_id", "player", "squad", "pos", "age",
               "weekly_wage_gbp", "annual_wage_gbp", "wage_is_estimate"]]


def load_stats():
    lines = read_single_column_excel(STATS_FILE)
    # Line 0 is a grouping row; real data starts on line 2 (line 1 is the header)
    rows = list(csv.reader(lines[2:]))
    df = pd.DataFrame(rows)

    # Columns used: name, matches, starts, minutes, goals, assists, FBref ID (last column)
    df = df[[1, 7, 8, 9, 11, 12, df.columns[-1]]]
    df.columns = ["name", "mp", "starts", "minutes", "goals", "assists", "player_id"]
    for c in ["mp", "starts", "minutes", "goals", "assists"]:
        df[c] = pd.to_numeric(df[c])

    # Players who moved club appear twice, so combine them into one row
    df = df.groupby("player_id", as_index=False).agg(
        mp=("mp", "sum"), starts=("starts", "sum"), minutes=("minutes", "sum"),
        goals=("goals", "sum"), assists=("assists", "sum"))
    df["nineties"] = df["minutes"] / 90
    df["ga_per90"] = (df["goals"] + df["assists"]) / df["nineties"].where(df["nineties"] > 0)
    return df


def build_model(merged):
    """Attackers only: expected output from wage, then the gap vs actual output."""
    played = merged[merged["minutes"] >= MIN_MINUTES].copy()

    is_fbref_attacker = played["pos"].isin(["FW", "FWMF", "MFFW"])
    is_added = played["player"].isin(ATTACKING_MIDFIELDERS)
    att = played[is_fbref_attacker | is_added].copy()

    att["position_group"] = np.where(
        att["pos"] == "FW", "Forward",
        np.where(att["pos"].isin(["FWMF", "MFFW"]),
                 "Winger / forward-midfielder", "Attacking midfielder / winger"))
    att["role_source"] = np.where(is_fbref_attacker[att.index],
                                  "FBref position tag", "Added by role (manual list)")
    att["goal_contributions"] = att["goals"] + att["assists"]

    # Straight-line fit of G+A per 90 against log(wage)
    log_wage = np.log(att["weekly_wage_gbp"])
    slope, intercept = np.polyfit(log_wage, att["ga_per90"], 1)
    att["expected_ga_per90"] = slope * log_wage + intercept
    att["efficiency_gap"] = att["ga_per90"] - att["expected_ga_per90"]

    att["verdict"] = np.select(
        [att["efficiency_gap"] >= GAP_THRESHOLD, att["efficiency_gap"] <= -GAP_THRESHOLD],
        ["Underpaid (outperforming wage)", "Overpaid (underperforming wage)"],
        "About right")
    att["weekly_wage_per_contribution_gbp"] = (
        att["weekly_wage_gbp"] / att["goal_contributions"].where(att["goal_contributions"] > 0)).round(0)
    att["value_rank"] = att["efficiency_gap"].rank(ascending=False, method="min").astype(int)

    for c in ["ga_per90", "expected_ga_per90", "efficiency_gap"]:
        att[c] = att[c].round(3)

    att = att.drop(columns=["player_id"]).sort_values("value_rank")
    return att


if __name__ == "__main__":
    wages = load_wages()
    stats = load_stats()

    merged = wages.merge(stats, on="player_id", how="inner")
    merged.to_csv("pl_wages_performance_merged.csv", index=False)
    print(f"Merged players with wages + stats: {len(merged)}")

    rankings = build_model(merged)
    rankings.to_csv("pl_value_rankings.csv", index=False)
    rankings.to_csv("pbi_attackers.csv", index=False)
    print(f"Attackers in the model: {len(rankings)}")
    print(rankings["verdict"].value_counts())
