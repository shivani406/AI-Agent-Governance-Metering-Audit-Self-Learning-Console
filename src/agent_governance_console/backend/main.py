from fastapi import FastAPI
from agent_governance_console.backend.api import agents
from agent_governance_console.backend.api import usage
from agent_governance_console.backend.api import view_audit_trail
from agent_governance_console.backend.central_audit import M2M_audit

app = FastAPI()

# include all the router isolated api's

app.include_router(agents.router, prefix = "/agents", tags = ["Agents"])
app.include_router(usage.router, prefix="/usage", tags=["Usage Metering"])
app.include_router(view_audit_trail.router, prefix="/audit-log", tags=["Audit Analytics"])
app.include_router(M2M_audit.router, prefix="/log-usage", tags=["M2M Telemetry Ingestion"])


@app.get("/", status_code = 200)
def read_root():
    return {"status" : "healthy", "service": "Agent Governance Console Gateway"}