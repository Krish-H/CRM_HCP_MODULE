from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import agent
import database
from schemas import ChatRequest
from database import SessionLocal
from models import Interaction
from sqlalchemy.orm import Session

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    database.Base.metadata.create_all(bind=database.engine)
    print("✅ DB Ready")

@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        reply = agent.run_agent(req.message)
        if isinstance(reply, dict):
            return {"reply": reply.get("message", ""), "data": reply.get("data")}
        return {"reply": reply}
    except Exception as e:
        print("🔥 ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hcp/{doctor_name}")
def get_hcp_profile(doctor_name: str):
    db = SessionLocal()

    records = db.query(Interaction).filter(
        Interaction.doctor_name.ilike(f"%{doctor_name}%")
    ).all()

    if not records:
        return {"message": "No interactions found"}

    result = []
    for r in records:
        result.append({
            "id": r.id,
            "product": r.product,
            "sentiment": r.sentiment,
            "notes": r.notes,
            "follow_up_date": r.follow_up_date
        })
    return {
        "doctor": doctor_name,
        "interactions": result
    }

@app.get("/api/followups/today")
def get_todays_followups():
    from datetime import date
    db = SessionLocal()
    
    records = db.query(Interaction).filter(
        Interaction.follow_up_date == date.today()
    ).all()
    
    result = []
    for r in records:
        result.append({
            "id": r.id,
            "doctor": r.doctor_name,
            "notes": r.notes
        })
        
    return {"followups": result}