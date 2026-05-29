from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import agents, telemetry, insight
from backend.services.audit import fetch_audit_entries

app = FastAPI(title="Enterprise Agent Governance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router)
app.include_router(telemetry.router)
app.include_router(insight.router)

@app.get("/audit-log")
def read_audit_log_endpoint():
    return fetch_audit_entries()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)