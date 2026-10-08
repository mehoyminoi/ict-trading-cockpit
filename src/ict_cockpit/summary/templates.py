from ict_cockpit.summary.template_definition import (
    SummaryTemplateDefinition,
    SummaryTemplateKind,
)


TRADE_SUMMARY_V1 = """Date: {date} Trade #{trade_number}
Asset: {asset}
Source: {trade_source}
Account: {account_context}
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
{chart_images}
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


TRADE_SUMMARY_FIELDS = frozenset(
    {
        "date",
        "trade_number",
        "asset",
        "trade_source",
        "account_context",
        "model",
        "direction",
        "entry_tf",
        "entry_time",
        "entry_price",
        "close_time",
        "close_price",
        "trade_time",
        "result_handles",
        "result_ticks",
        "stop_handles",
        "stop_ticks",
        "reward_risk",
        "cycle_16y",
        "quadrennial",
        "quarter",
        "month",
        "week",
        "day",
        "session",
        "macro_90m",
        "summary",
        "chart_images",
    }
)

STUDY_FIND_FIELDS = frozenset(
    {
        "date",
        "asset",
        "session",
        "pattern",
        "available_move",
        "observation",
        "notes",
        "chart_images",
    }
)

TEMPLATE_FIELDS = {
    SummaryTemplateKind.TRADE_SUMMARY: TRADE_SUMMARY_FIELDS,
    SummaryTemplateKind.STUDY_FIND: STUDY_FIND_FIELDS,
}

DEFAULT_SUMMARY_TEMPLATES = (
    SummaryTemplateDefinition(
        template_id="trade-summary-default",
        revision=1,
        kind=SummaryTemplateKind.TRADE_SUMMARY,
        name="Trade Summary Default",
        body=TRADE_SUMMARY_V1,
    ),
    SummaryTemplateDefinition(
        template_id="study-find-default",
        revision=1,
        kind=SummaryTemplateKind.STUDY_FIND,
        name="Study Find Default",
        body=STUDY_FIND_SUMMARY_V1,
    ),
)
