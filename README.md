# Premier League Wages: Who Gives the Best Value?

Which Premier League players give the best value for their wages?
An analysis of 2024/25 ⟨season⟩ wage data against on-pitch output.

## The question

⟨One or two sentences: why you asked it. e.g. "Clubs spend hundreds of
millions on wages, but value for money is rarely measured. I wanted to
see which players outperform their pay packet, and which clubs get the
most output per pound spent."⟩

## Version 1
We later see in the season with more refined data to see which attackers have truly outperformed their contracts and lived to expected transfer fees 

## Data

- **Wages:** Capology (via FBref), 2024/25 season, snapshot ⟨date⟩
- **Performance:** FBref, 2024/25 season, as of ⟨date⟩
- **Note:** most wage figures are estimates, not published salaries.
- Players filtered to **450+ minutes** to remove small-sample outliers.

## Method

- **Python:** cleaned both datasets and merged on player ID; filtered to
  450+ minutes; built an efficiency model comparing actual vs expected
  goal contributions per 90, adjusted by position.
- **SQL:** ranked players by value and produced club-level summaries
  (average wage, total output, cost per goal contribution).
- **Power BI:** ⟨dashboard — one line once built⟩

## Key findings

- Best value: ⟨Player⟩ — ⟨£X⟩/week for ⟨Y⟩ goal contributions per 90.
- Club average: ⟨Club⟩ got the most output per pound at ⟨£X⟩ per goal contribution.
- High earners: ⟨Player⟩ earned ⟨£X⟩/week but contributed ⟨Y⟩ per 90.
- ⟨One more finding with a real number.⟩

## Limitations

- Early-season sample — numbers will shift over a full season.
- Goals and assists only capture attacking output, not defending or buildup.
- Wage figures are estimates from Capology.
- ⟨Any other caveat you found.⟩

# Attacker Value Analysis: Wage vs Output

A Power BI report comparing what football attackers are paid with what they deliver.

## Pages

| Page | What it shows |
|------|---------------|
| **Overview** | KPI cards (players, underpaid, overpaid, wage per contribution), a wage vs goal-contributions scatter, and the top 10 attackers by efficiency gap. Slicers for club and position. |
| **Rankings** | Full value ranking table (rank 1 = best value for wage) with wage, goal contributions per 90, expected per 90, efficiency gap and verdict. |
| **Clubs** | Average efficiency gap by club and total attacker wage bill by club. |

## Screenshots
![Attacker Value Analysis Overview](Attacker%20Value%20Analysis%20Overview.png)
![Value Ranking Analysis](Value%20Ranking%20Analysis.png)
![Club Analysis](Club%20Analysis.png)

## Data dictionary

| Field | Meaning |
|-------|---------|
| `player`, `squad` | Player name and club |
| `position_group` | Attacker position group |
| `weekly_wage_gbp` | Weekly wage in GBP |
| `ga_per90` | Goal contributions per 90 minutes |
| `expected_ga_per90` | Expected goal contributions per 90 |
| `efficiency_gap` | Gap between actual and expected output |
| `value_rank` | Rank of output relative to wage (1 = best value) |
| `verdict` | Underpaid / overpaid classification |

## Measures

`Players`, `Underpaid Count`, `Overpaid Count`, `Weekly Wage Bill`, `Avg Efficiency Gap`, `Wage per Contribution`

## How to open

Open `Football_project_visualisation.pbix` in Power BI Desktop. The theme is in `FootballDarkPro_theme.json` (View > Themes > Browse for themes).

## Tools

Power BI, DAX

## How to run it

```bash
pip install pandas
python scripts/load_db.py      # builds football.db from the CSVs in data/

