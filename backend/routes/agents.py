"""
Create api endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sys
sys.path.append("../database")
sys.path.append("../services")
from connection import get_db_connection
from audit import write_audit_entry

router = APIRouter()

class Decision_Request(BaseModel):
    decision:str
    reason:str
    approved_by:str

@app_router := APIRouter()

@router.get("/agents")
    