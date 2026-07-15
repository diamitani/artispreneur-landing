"""FastAPI app factory — wires routes and middleware."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import config
from app.routes import auth, agents, outputs, directory


def create_app() -> FastAPI:
    app = FastAPI(title="Artispreneur API", version="3.0")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(auth.router, prefix="/auth", tags=["auth"])
    app.include_router(agents.router, prefix="/agent", tags=["agents"])
    app.include_router(outputs.router, prefix="/outputs", tags=["outputs"])
    app.include_router(directory.router, prefix="/directory", tags=["directory"])
    return app
