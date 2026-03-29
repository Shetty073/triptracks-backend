from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import asynccontextmanager
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api import auth, users, crew, trips
from app.websockets import chat
from app.core.logger import api_name_var, logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    await connect_to_mongo()
    yield
    # Shutdown actions
    await close_mongo_connection()

app = FastAPI(title="Triptracks API", lifespan=lifespan)

# Add CORS Middleware to allow Flutter client requests (Web, Emulator, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_api_name_context(request: Request, call_next):
    api_name = request.url.path
    if request.scope.get("route"):
        # This resolves parametrized paths e.g. /api/users/{user_id}
        api_name = getattr(request.scope["route"], "path", request.url.path)
    
    token = api_name_var.set(api_name)
    try:
        return await call_next(request)
    finally:
        api_name_var.reset(token)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(crew.router, prefix="/api/crew", tags=["crew"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(chat.router, prefix="/ws/trips", tags=["websockets"])

# Ensure the uploads directory exists before mounting
os.makedirs("uploads/profiles", exist_ok=True)
os.makedirs("uploads/trips", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "Welcome to Triptracks API"}
