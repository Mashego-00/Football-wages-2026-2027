-- ============================================================
-- Premier League wages vs output: SQL queries
-- Tables:
--   player_season  : every player with wages + stats (394 rows)
--   value_rankings : outfield players, 450+ mins, with efficiency model (187 rows)
-- ============================================================

-- 1. Best value players: biggest positive efficiency gap
SELECT value_rank, player, squad, position_group,
       weekly_wage_gbp, goal_contributions, ga_per90, efficiency_gap
FROM value_rankings
ORDER BY efficiency_gap DESC
LIMIT 10;

-- 2. Most overpaid players: biggest negative efficiency gap
SELECT player, squad, position_group,
       weekly_wage_gbp, goal_contributions, ga_per90, efficiency_gap
FROM value_rankings
ORDER BY efficiency_gap ASC
LIMIT 10;

-- 3. Cheapest goal contributions (weekly wage per goal or assist)
SELECT player, squad, weekly_wage_gbp, goal_contributions,
       ROUND(weekly_wage_gbp * 1.0 / goal_contributions) AS wage_per_contribution
FROM value_rankings
WHERE goal_contributions > 0
ORDER BY wage_per_contribution ASC
LIMIT 10;

-- 4. Club summary: average efficiency and wage spend
SELECT squad,
       COUNT(*)                          AS players,
       ROUND(AVG(efficiency_gap), 3)     AS avg_efficiency_gap,
       SUM(weekly_wage_gbp)              AS weekly_wage_bill,
       SUM(goal_contributions)           AS total_contributions,
       ROUND(SUM(weekly_wage_gbp) * 1.0 / NULLIF(SUM(goal_contributions), 0)) AS wage_per_contribution
FROM value_rankings
GROUP BY squad
ORDER BY avg_efficiency_gap DESC;

-- 5. Best-value player at each club (window function)
SELECT squad, player, position_group, weekly_wage_gbp, efficiency_gap
FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY squad ORDER BY efficiency_gap DESC) AS club_rank
    FROM value_rankings
)
WHERE club_rank = 1
ORDER BY efficiency_gap DESC;

-- 6. How many players fall into each verdict, by position
SELECT position_group, verdict, COUNT(*) AS players
FROM value_rankings
GROUP BY position_group, verdict
ORDER BY position_group, players DESC;

-- 7. Top earners who barely play: minutes as a share of the maximum possible so far
SELECT player, squad, weekly_wage_gbp, minutes, starts, mp,
       ROUND(minutes * 1.0 / ((SELECT MAX(mp) FROM player_season) * 90), 2) AS share_of_possible_minutes
FROM player_season
WHERE weekly_wage_gbp >= 150000
ORDER BY share_of_possible_minutes ASC
LIMIT 10;

-- 8. Wage band vs average output (all value_rankings players)
SELECT CASE
         WHEN weekly_wage_gbp < 50000  THEN '1. Under 50k'
         WHEN weekly_wage_gbp < 100000 THEN '2. 50k-100k'
         WHEN weekly_wage_gbp < 200000 THEN '3. 100k-200k'
         ELSE '4. 200k+'
       END AS wage_band,
       COUNT(*)                   AS players,
       ROUND(AVG(ga_per90), 3)    AS avg_ga_per90
FROM value_rankings
GROUP BY wage_band
ORDER BY wage_band;

-- 9. Do estimated wages differ from confirmed ones? (data quality check)
SELECT wage_is_estimate, COUNT(*) AS players,
       ROUND(AVG(weekly_wage_gbp)) AS avg_weekly_wage
FROM player_season
GROUP BY wage_is_estimate;
