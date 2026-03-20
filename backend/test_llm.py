import sys, os
sys.path.append('d:/INTERNSALA _PRJ/crm_hcp_module/backend')
try:
    from agent import get_llm
except ImportError:
    pass

prompt = '''Extract structured medical interaction data.

STRICT RULES:
- product = drug/product name ONLY (NOT samples)
- samples = quantity of samples (if mentioned)
- sentiment = positive / neutral / negative
- notes = short summary

IGNORE:
- commands like show/profile/view
- numbers as product

Text:
Met Dr Salt, discussed efficacy, gave 2 samples, positive

Return JSON:

{
  "doctor_name": "",
  "product": "",
  "samples": "",
  "sentiment": "",
  "notes": ""
}'''

try:
    from agent import get_llm
    llm = get_llm()
    for i in range(5):
        res = llm.invoke(prompt).content
        print(f'Attempt {i}:')
        print(repr(res))
except Exception as e:
    print(e)
