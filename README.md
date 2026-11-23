# Premier League Wages: Who Gives the Best Value?

Which Premier League players give the best value for their wages?
An analysis of 2024/25 ⟨season⟩ wage data against on-pitch output.

## The question

⟨One or two sentences: why you asked it. e.g. "Clubs spend hundreds of
millions on wages, but value for money is rarely measured. I wanted to
see which players outperform their pay packet, and which clubs get the
most output per pound spent."⟩

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

## How to run it

```bash
pip install pandas
python scripts/load_db.py      # builds football.db from the CSVs in data/
