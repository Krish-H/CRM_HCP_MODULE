import os, json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph
from typing import TypedDict, Any
from database import SessionLocal
from models import Interaction

load_dotenv()


def safe_json_parse(text):
    if not text:
        return None

    import json
    import re
    import ast

    try:
        return json.loads(text)
    except:
        pass

    # Extract JSON inside markdown
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", str(text), re.DOTALL | re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass

    # Extract JSON block and handle malformed json (trailing commas, single quotes)
    match = re.search(r"\{.*\}", str(text), re.DOTALL)
    if match:
        json_str = match.group()
        try:
            return json.loads(json_str)
        except:
            try:
                # Fallback to python ast for single quotes / trailing commas
                py_str = re.sub(r'\bnull\b', 'None', json_str)
                py_str = re.sub(r'\btrue\b', 'True', py_str)
                py_str = re.sub(r'\bfalse\b', 'False', py_str)
                res = ast.literal_eval(py_str)
                if isinstance(res, dict):
                    return res
            except:
                pass

    return None
# LLM
# -------------------
def get_llm():
    return ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY")
    )

# -------------------
# TOOLS
# -------------------

def log_interaction(input: str):
    import datetime
    # ❌ BLOCK NON-INTERACTION COMMANDS
    if any(x in input.lower() for x in ["show", "profile", "view", "history"]):
        return "❌ Not a valid interaction. Skipped logging."

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
{input}

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

    raw = llm.invoke(prompt).content
    print("🧠 RAW LLM OUTPUT:", raw)

    data = safe_json_parse(raw)

    if not data:
        return "❌ Failed to extract structured data"

    db = SessionLocal()

    # Parse String -> date safely
    import datetime
    import json
    f_date = None
    if data.get("follow_up_date"):
        try:
            f_date = datetime.datetime.strptime(data["follow_up_date"], "%Y-%m-%d").date()
        except:
            f_date = None

    is_form_submission = "Log interaction:" in input

    if is_form_submission:
        record = Interaction(
            doctor_name=data.get("doctor_name"),
            product=data.get("product"),
            samples=data.get("samples"),
            sentiment=data.get("sentiment"),
            notes=data.get("notes"),
            follow_up_date=f_date
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return f"✅ Interaction saved with ID {record.id}"
    else:
        return {
            "message": "✨ I've prepared the form based on your input! Please review on the left and click **Save Log**.",
            "data": data
        }


def edit_interaction(input: str):
    llm = get_llm()

    prompt = f"""
Extract:
field_to_update (e.g. doctor_name, product, samples, sentiment, notes), new_value, interaction_id (optional, null if not provided)

From checking the text:
{input}

Return JSON:
{{
  "field_to_update": "",
  "new_value": "",
  "interaction_id": null
}}
"""

    raw = llm.invoke(prompt).content
    data = safe_json_parse(raw)

    if not data:
        return "❌ Could not parse edit instructions"

    db = SessionLocal()

    if data.get("interaction_id"):
        record = db.query(Interaction).filter(Interaction.id == data["interaction_id"]).first()
    else:
        record = db.query(Interaction).order_by(Interaction.id.desc()).first()

    if not record:
        return "❌ Interaction not found"

    field = data.get("field_to_update")
    val = data.get("new_value", "")
    
    if field in ["doctor_name", "doctor", "name"]:
        record.doctor_name = val
        field = "doctor_name"
    elif hasattr(record, str(field)):
        setattr(record, field, val)
    else:
        # Fallback to notes if we don't know what to update
        record.notes = record.notes + "\nEdit: " + input
        field = "notes"

    db.commit()
    return f"✏️ Updated interaction {record.id}: {field} -> {val}"

def retrieve_hcp_profile(input: str):
    import re
    from database import SessionLocal
    from models import Interaction

    db = SessionLocal()

    match = re.search(r"dr\.?\s?[a-zA-Z]+", input, re.I)
    if not match:
        return "❌ Doctor name not found"

    doctor = match.group()

    records = db.query(Interaction).filter(
        Interaction.doctor_name.ilike(f"%{doctor}%")
    ).all()

    if not records:
        return "No interactions found"

    # 🔥 FILTER BAD DATA
    valid_records = [
        r for r in records
        if not r.product or r.product.lower() not in ["profile", "insights"]
    ]

    if not valid_records:
        return f"👨‍⚕️ **{doctor} Profile:**\n\nNo interactions logged."

    output = f"👨‍⚕️ **{doctor} Profile:**\n\n"

    for r in valid_records:
        output += f"**Product:** {r.product or 'N/A'}\n"
        output += f"**Samples:** {r.samples or 'None'}\n"
        output += f"**Sentiment:** {r.sentiment or 'N/A'}\n"
        output += f"**Notes:** {r.notes or 'None'}\n"
        if r.follow_up_date:
            output += f"**Follow-up:** {r.follow_up_date}\n"
        output += "\n---\n\n"

    return output.strip()


def schedule_followup(input: str):
    llm = get_llm()

    prompt = f"""
Extract:
interaction_id and follow_up_date

From:
{input}

Return JSON.
"""

    raw = llm.invoke(prompt).content
    data = safe_json_parse(raw)

    if not data:
        return "❌ Could not extract follow-up details"

    db = SessionLocal()

    record = db.query(Interaction).filter(Interaction.id == data["interaction_id"]).first()

    if not record:
        return "❌ Interaction not found"

    record.follow_up_date = data["follow_up_date"]
    db.commit()

    return f"📅 Follow-up set for {data['follow_up_date']}"


def find_nearby_hospitals(input: str):
    llm = get_llm()
    prompt = f"""
You are an AI CRM assistant for the pharmaceutical sector.
The user is asking for nearby hospitals or clinics: "{input}"

Please provide a highly professional, concise list of 3-5 relevant hospitals matching their request.
Include the Hospital Name, Specialty/Type, and approximate Location/Distance.
Format the output strictly as a NUMBERED list (1., 2., 3., etc.).
Separate each hospital entry with a blank line for readability.
Use bolding for the hospital name.
"""
    response = llm.invoke(prompt).content.strip()
    # Ensure double newlines between items
    formatted = response.replace("\n", "\n\n")
    return f"🏥 **Nearby Hospitals:**\n\n{formatted}"

# -------------------
# LANGGRAPH
# -------------------

class State(TypedDict):
    message: str
    intent: str
    response: Any

def intent_node(state: State):
    llm = get_llm()
    msg = state.get("message", "")

    prompt = f"""
You are an AI CRM assistant.

Classify the user intent STRICTLY into one:

- LOG
- EDIT
- PROFILE
- FOLLOWUP
- HOSPITALS

RULES:
- If the input describes a new meeting or interaction (e.g., "met", "discussed"), output LOG, even if it contains a follow up date.
- show/profile/history/view → PROFILE
- update/change/sorry/mistake/was/instead/correction → EDIT
- nearby/hospitals/find/list → HOSPITALS
- Only output FOLLOWUP if the user is explicitly adding a follow up to an EXISTING interaction.

Return ONLY one word.

User: {msg}
"""

    decision = llm.invoke(prompt).content.strip().upper()

    # 🔥 HARD RULE (fix your bug)
    if any(x in msg.lower() for x in ["hospital", "nearby", "hospitals", "clinic", "radius", "km", "find hospital", "list hospital"]):
        decision = "HOSPITALS"
    elif any(x in msg.lower() for x in ["show", "profile", "history", "view"]):
        decision = "PROFILE"
    elif any(x in msg.lower() for x in ["update", "change", "sorry", "mistake", "was", "instead", "correction"]):
        decision = "EDIT"
    elif "met " in msg.lower() or "discussed " in msg.lower():
        decision = "LOG"

    state["intent"] = decision
    print("🧠 INTENT:", decision)

    return state


def tool_node(state: State):
    msg = state.get("message", "")
    intent = state.get("intent", "")

    if "LOG" in intent:
        result = log_interaction(msg)
    elif "EDIT" in intent:
        result = edit_interaction(msg)
    elif "PROFILE" in intent:
        result = retrieve_hcp_profile(msg)
    elif "FOLLOW" in intent:
        result = schedule_followup(msg)

    elif "HOSPITAL" in intent:
        result = find_nearby_hospitals(msg)
    else:
        result = "❌ Unknown"

    state["response"] = result
    return state


def build_graph():
    g = StateGraph(State)

    g.add_node("intent", intent_node)
    g.add_node("tool", tool_node)

    g.set_entry_point("intent")
    g.add_edge("intent", "tool")

    return g.compile()


graph = build_graph()


def run_agent(message: str):
    res = graph.invoke({"message": message})
    return res["response"]