# src/api/payment_gateway.py

import os
from fastapi import APIRouter, HTTPException
from src.api.whatsapp import handle_whatsapp_message

router = APIRouter(prefix="/thcm-agentic-poc/api", tags=["Payment Gateway"])


class MockRequest:
    def __init__(self, form_data: dict):
        self._form_data = form_data

    async def form(self):
        return self._form_data


@router.post("/payment_success_trigger")
async def mock_payment_success(whatsapp_number: str):
    try:
        # Validate whatsapp_number format
        if not whatsapp_number:
            raise HTTPException(status_code=400, detail="whatsapp_number parameter is required")
        
        # Format whatsapp number
        target_number = whatsapp_number if whatsapp_number.startswith("whatsapp:") else f"whatsapp:{whatsapp_number}"
        
        mock_form_data = {
            "From": target_number,
            "Body": "payment_success"
        }

        await handle_whatsapp_message(mock_form_data)

        return {"status": "mock payment success triggered"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")