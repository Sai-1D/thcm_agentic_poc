# src/api/twilio_manager.py

import os
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter(prefix="/thcm-agentic-poc/api", tags=["Twilio Manager"])

def get_available_joining_codes():
    """Get available joining codes from config"""
    config_path = os.path.join(os.path.dirname(__file__), "../../config.json")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config.get("twilio_joining_code", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return ["ability former", "religious human"]  # fallback

class AccountSwitchRequest(BaseModel):
    joining_code: str = Field(..., description="Joining code for Twilio account", examples=get_available_joining_codes())

class AccountSwitchResponse(BaseModel):
    status: str
    message: str
    current_account: Optional[str] = None

# Global variable to store current active account
current_active_account = None

def load_config():
    """Load twilio joining codes from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), "../../config.json")
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="config.json not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid JSON in config.json")

def get_account_env_prefix(joining_code: str) -> str:
    """Convert joining code to environment variable prefix"""
    return joining_code.upper().replace(" ", "_")

@router.post("/switch-twilio-account", response_model=AccountSwitchResponse)
async def switch_twilio_account(request: AccountSwitchRequest):
    """Switch Twilio account based on joining code"""
    global current_active_account
    
    config = load_config()
    
    if request.joining_code not in config.get("twilio_joining_code", []):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid joining code. Available codes: {config['twilio_joining_code']}"
        )
    
    env_prefix = get_account_env_prefix(request.joining_code)
    
    # Check if required environment variables exist
    sid_key = f"TWILIO_ACCOUNT_SID_{env_prefix}"
    token_key = f"TWILIO_AUTH_TOKEN_{env_prefix}"
    
    if not all([os.getenv(sid_key), os.getenv(token_key)]):
        raise HTTPException(
            status_code=400,
            detail=f"Environment variables not found for {request.joining_code}. Required: {sid_key}, {token_key}"
        )
    
    # Set the global environment variables (WhatsApp number stays the same)
    os.environ["TWILIO_ACCOUNT_SID"] = os.getenv(sid_key)
    os.environ["TWILIO_AUTH_TOKEN"] = os.getenv(token_key)
    
    current_active_account = request.joining_code
    
    return AccountSwitchResponse(
        status="success",
        message=f"Switched to Twilio account: {request.joining_code}",
        current_account=current_active_account
    )

@router.get("/current-twilio-account")
async def get_current_twilio_account():
    """Get currently active Twilio account"""
    global current_active_account
    
    return {
        "status": "active" if current_active_account else "default",
        "current_account": current_active_account if current_active_account else "ability former"
    }

@router.get("/debug-twilio-env")
async def debug_twilio_env():
    """Debug current Twilio environment variables (for testing)"""
    return {
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", "Not set"),
        "TWILIO_AUTH_TOKEN": "Set" if os.getenv("TWILIO_AUTH_TOKEN") else "Not set",
        "TWILIO_WHATSAPP_NUMBER": os.getenv("TWILIO_WHATSAPP_NUMBER", "Not set"),
        "active_account": current_active_account if current_active_account else "default"
    }

@router.get("/available-twilio-accounts")
async def get_available_twilio_accounts():
    """Get list of available Twilio accounts from config"""
    config = load_config()
    available_accounts = []
    
    for joining_code in config.get("twilio_joining_code", []):        
        available_accounts.append({
            "joining_code": joining_code
        })
    
    return {"available_accounts": available_accounts}
