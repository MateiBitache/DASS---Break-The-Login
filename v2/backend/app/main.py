from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api import auth, tickets, audit
from app.database import Base, engine
from app.exceptions import AuthException

app = FastAPI(title="Project - Break the Login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.exception_handler(AuthException)
def auth_exception_handler(request: Request, exc: AuthException):
    return JSONResponse(
        status_code=401, 
        content={
            "timestamp": datetime.utcnow().isoformat(),
            "status": 401,
            "error": "Authentication Error",
            "message": exc.message,
        }
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = {
        "_".join(str(part) for part in err.get("loc", [])): err.get("msg")
        for err in exc.errors()
    }
    return JSONResponse(status_code=400, content=errors)

@app.exception_handler(Exception)
def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500, 
        content={
            "timestamp": datetime.utcnow().isoformat(),
            "status": 500,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
        }
    )

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(audit.router)
