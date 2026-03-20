from agent import log_interaction, get_llm
import datetime

input_text = "fix this, met Dr.Black , discussed efficacy,gave 2 samples,sentiment positive,follow up today"

prompt = f"""
Extract structured medical interaction data.

STRICT RULES:
- product = drug/product name ONLY (NOT samples)
- samples = quantity of samples (if mentioned)
- sentiment = positive / neutral / negative
- notes = short summary
- follow_up_date = If the user mentions any followup timeframe (e.g. "tomorrow", "next week", "23/03/2026"), format strictly as YYYY-MM-DD relative to today which is {datetime.date.today()}. If no date, output null.

IGNORE:
- commands like show/profile/view
- numbers as product

Text:
{input_text}

Return JSON:

{{
  "doctor_name": "",
  "product": "",
  "samples": "",
  "sentiment": "",
  "notes": "",
  "follow_up_date": null
}}
"""

llm = get_llm()
raw = llm.invoke(prompt).content
print("=== RAW ===")
print(raw)
print("===========")

from agent import safe_json_parse
print("PARSED:", safe_json_parse(raw))
