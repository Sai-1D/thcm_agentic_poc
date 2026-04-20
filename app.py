# app.py

from fastapi import FastAPI
fastapi_app = FastAPI(
    title="IoT Event API",
    docs_url="/thcm-agentic-poc/api/docs",
    redoc_url="/thcm-agentic-poc/api/redoc",
    openapi_url="/thcm-agentic-poc/api/openapi.json"
)

from dotenv import load_dotenv
load_dotenv()

from src.api.whatsapp import router as whatsapp_router
from src.api.iot import router as iot_router
from src.api.payment_gateway import router as payment_gateway_router
from src.api.quotation import router as quotation_router
from src.api.twilio_manager import router as twilio_manager_router

fastapi_app.include_router(whatsapp_router)
fastapi_app.include_router(iot_router)
fastapi_app.include_router(payment_gateway_router)
fastapi_app.include_router(quotation_router)
fastapi_app.include_router(twilio_manager_router)


@fastapi_app.get("/thcm-agentic-poc/api")
async def root():
    return {"message": "IoT Event API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:fastapi_app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )
