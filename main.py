import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import uvicorn

# Load environment variables from .env file
load_dotenv()

# --- Import your routers ---
# CHANGED: Import both the chat router and the new report router
from routers import chat_router
from routers import report_router

# This will initialize the DB client on startup
from services import firestore_service 

app = FastAPI(
    title="Multi-Role Agentic System",
    description="An AI agent system with role-based access control and report generation.",
    version="0.2.0" # Good practice to bump the version when adding a new feature
)

# Configure CORS
# IMPORTANT: Since your new endpoint is public, you might want to allow all origins
# for that specific feature if it's meant to be used more broadly.
# For now, we'll keep your existing settings.
origins = [
    "http://localhost",
    "http://localhost:3000",
    # Add your frontend's deployed URL here later
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include all the routers in the application ---
# This makes the /chat/... endpoints from the chat_router available
app.include_router(chat_router.router)
# CHANGED: This makes the /reports/... endpoints from the report_router available
app.include_router(report_router.router)


@app.get("/", tags=["Health Check"])
async def root():
    return {"status": "ok", "message": "Welcome to the Multi-Role Agentic System!"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)