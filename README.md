# SWYNEX Task 1: Data Cleaning & Preparation

## Dataset
- **Name:** Netflix Movies and TV Shows
- **Source:** TidyTuesday (2021-04-20), https://github.com/rfordatascience/tidytuesday/tree/master/data/2021/2021-04-20
- **Raw size:** 7,787 rows x 12 columns, 3,631 missing cells

## Issues found
| Issue | Where | Count |
|---|---|---|
| Missing values | director, cast, country, date_added, rating | 2,389 / 718 / 507 / 10 / 7 |
| Duplicate records | same title + type + release year (case-insensitive) | 1 (0 exact duplicates) |
| Incorrect data types | `date_added` stored as text ("August 14, 2020") | 7,777 values |
| Mixed-unit column | `duration` holds "93 min" for movies and "4 Seasons" for TV shows | 7,787 values |
| Stray whitespace | leading spaces, mostly in `date_added` | 89 cells |
| Inconsistent values | rating has both `UR` and `NR` (same meaning) | 5 rows |
| Multi-value text | country, cast, director, listed_in are comma-separated lists with uneven spacing | all rows |

## Cleaning steps
1. Trimmed whitespace in all text columns and turned blank strings into missing values.
2. Removed 1 logical duplicate (no exact duplicates existed).
3. Converted `date_added` to datetime and derived `year_added` and `month_added`.
4. Split `duration` into numeric `duration_value` and `duration_unit` (minutes / seasons).
5. Merged rating `UR` into `NR`.
6. Normalised comma-separated lists and added `primary_country` and `primary_genre` for easy grouping.
7. Filled missing director, cast and country with `Unknown`, and missing rating with `NR`. I did not guess values.
8. Left 10 missing `date_added` values empty because they cannot be inferred reliably.
9. Validated that `show_id` is unique and no `release_year` is in the future.

## Before vs After
| | Raw | Cleaned |
|---|---|---|
| Rows | 7,787 | 7,786 |
| Columns | 12 | 17 |
| Missing cells | 3,631 | 30 (the 10 missing dates, repeated in year_added and month_added) |
| Exact duplicates | 0 | 0 |
| Rating categories | 14 | 13 |

## Files
- `data/raw_data.csv`: original dataset
- `data/cleaned_data.csv`: cleaned dataset
- `clean_data.py`: cleaning script
- `cleaning_log.txt`: log of every change made

## How to run
```bash
pip install pandas numpy
python clean_data.py data/raw_data.csv data/cleaned_data.csv
```

## Key learnings
- Profile first: most problems (whitespace, mixed units, text dates) are invisible until you check types and value counts.
- Missing is not the same as wrong: filling with "Unknown" keeps the data honest, whereas imputing a director would invent facts.
- Logging every change makes the cleaning reproducible and easy to review.

## Tools
Python (pandas, numpy)
