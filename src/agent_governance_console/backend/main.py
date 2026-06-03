from fastapi import FastAPI
from agent_governance_console.backend.api import agents
from agent_governance_console.backend.api.usage import router as usage_router

app = FastAPI()

# include all the router isolated api's

app.include_router(agents.router, prefix = "/agents", tags = ["Agents"])
app.include_router(usage_router, prefix="/usage", tags=["Usage Metering"])

# app.include_router(audit_router, prefix="/audit-log", tags=["Audit Analytics"])
# add main endpoint rounter connection for audits

@app.get("/", status_code = 200)
def read_root():
    return {"status" : "healthy", "service": "Agent Governance Console Gateway"}