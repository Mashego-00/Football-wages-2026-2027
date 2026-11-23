import sqlite3
import pandas as pd

conn = sqlite3.connect("football.db")

# All players with both wages and stats (394 rows)
pd.read_csv("pl_wages_performance_merged.csv").to_sql(
    "player_season", conn, if_exists="replace", index=False)

# Outfield players with 450+ minutes, plus the efficiency model results (187 rows)
pd.read_csv("pl_value_rankings.csv").to_sql(
    "value_rankings", conn, if_exists="replace", index=False)

conn.close()
print("football.db created")
