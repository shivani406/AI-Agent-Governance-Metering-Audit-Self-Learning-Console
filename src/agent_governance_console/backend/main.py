from fastapi import FastAPI
from agent_governance_console.backend.routes import agents

app = FastAPI()

# include all the router isolated api's

app.include_router(agents.router, prefix = "/agents", tags = ["Agents"])

@app.get("/", status_code = 200)
def read_root():
    return {"status" : "healthy"}