from agent import get_llm, safe_json_parse
import datetime

llm = get_llm()
prompt = f"""
Extract structured medical interaction data.

STRICT RULES:
- product = The product and/or clinical topic discussed (e.g., 'Paracetamol for fever management'). Do NOT include sample quantities here. If no product/topic is mentioned, output null.
- samples = quantity of samples (if mentioned)
- sentiment = positive / neutral / negative
- notes = short summary
- follow_up_date = If the user mentions any followup timeframe (e.g. "tomorrow", "next week", "23/03/2026"), format strictly as YYYY-MM-DD relative to today which is {datetime.date.today()}. If no date, output null.

IGNORE:
- commands like show/profile/view
- numbers as product

Text:
Met Dr. Kumar, discussed Paracetamol for fever management. Gave 3 samples. Sentiment positive. Follow up next week

OUTPUT ONLY VALID JSON. NO EXPLANATIONS, NO CODE, NO MARKDOWN. RETURN EXACTLY THIS JSON STRUCTURE AND NOTHING ELSE:

{{
  "doctor_name": "",
  "product": "",
  "samples": "",
  "sentiment": "",
  "notes": "",
  "follow_up_date": null
}}
"""
print("RUNNING LLM...")
res = llm.invoke(prompt).content
print("------- RESULT -------")
print(res)
