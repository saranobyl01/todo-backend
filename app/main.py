from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from routers import auth, todos, user_telegram
from reminder import reminder_daemon

app = FastAPI(title="Todo App API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://todo-frontend.saranobyl01.workers.dev"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(user_telegram.router)

@app.on_event("startup")
async def startup_event():
    # Start the reminder daemon as a background task
    asyncio.create_task(reminder_daemon())

@app.get("/")
async def root():
    return {"message": "Todo App API is running"}
