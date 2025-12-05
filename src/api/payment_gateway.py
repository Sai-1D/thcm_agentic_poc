# src/api/iot.py

import os
from fastapi import APIRouter
from src.api.whatsapp import whatsapp_webhook

router = APIRouter(prefix="/api", tags=["Payment Gateway"])
TESTER_WHATSAPP_NUMBER = os.getenv("TESTER_WHATSAPP_NUMBER")


class MockRequest:
    def __init__(self, form_data: dict):
        self._form_data = form_data

    async def form(self):
        return self._form_data


@router.post("/payment_success_trigger")
async def mock_payment_success():

    mock_form_data = {
        "From": f"whatsapp:{TESTER_WHATSAPP_NUMBER}",
        "Body": "payment_success"
    }

    mock_request = MockRequest(mock_form_data)

    # Simulate webhook
    await whatsapp_webhook(mock_request)

    return {"status": "mock payment success triggered"}
