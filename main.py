# main.py
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import models ,  schemas
from database import SessionLocal, Base, engine
import bcrypt
from auth import router as auth_router  # 👈 import router
from fastapi.middleware.cors import CORSMiddleware
from groq_api import ask_groq # 👈 import your OpenAI function
from pydantic import BaseModel

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Convo lab AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 👇 include auth routes
app.include_router(auth_router)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ------------------------------
# Route Endpoint
# ------------------------------
@app.api_route("/", methods=["GET", "HEAD"])
def root(request: Request):
    if request.method == "HEAD":
        return ""  # respond instantly for UptimeRobot or Render check
    return {"message": "Welcome to Convo Lab AI Backend"}

# ------------------------------
# Signup Endpoint
# ------------------------------
@app.post("/signup", response_model=schemas.UserResponse)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password
    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Create new user
    new_user = models.User(username=user.username, email=user.email, password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

class ChatRequest(BaseModel):
    prompt: str

from fastapi import Request

@app.post("/ask")
def ask_chatbot(request: ChatRequest):
    """
    Endpoint to handle frontend chat requests and connect to OpenAI.
    """
    try:
        response = ask_groq(request.prompt)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
