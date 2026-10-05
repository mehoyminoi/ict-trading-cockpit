TRADE_SUMMARY_V1 = """Date: {date} Trade #{trade_number}
Asset: {asset}
Model: {model}
Direction: {direction}
Entry TF: {entry_tf}
Entry Time: {entry_time}
Entry Price: {entry_price}
Close Time: {close_time}
Close Price: {close_price}
Trade time: {trade_time}
Trade Results: {result_handles} handles/ {result_ticks} ticks
SL: {stop_handles} handles/ {stop_ticks} ticks
Reward/Risk: {reward_risk}:1

AMDX/XAMD Stack-
16Y Cycle: {cycle_16y}
Quadrennial: {quadrennial}
Quarter: {quarter}
Month: {month}
Week: {week}
Day: {day}
Session: {session}
90m Macro Cycle: {macro_90m}

Summary: {summary}

Chart Markup Picture(s):
"""


STUDY_FIND_SUMMARY_V1 = """Date: {date}
Asset: {asset}
Session: {session}
Pattern: {pattern}
Available Move: {available_move}

Observation:
{observation}

Notes:
{notes}

Chart Markup Picture(s):
{chart_images}
"""