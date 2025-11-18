# app.py

from fastapi import FastAPI
fastapi_app = FastAPI(title="IoT Event API")

from dotenv import load_dotenv
load_dotenv()

from src.api.whatsapp import router as whatsapp_router
from src.api.iot import router as iot_router

fastapi_app.include_router(whatsapp_router)
fastapi_app.include_router(iot_router)

@fastapi_app.get("/")
async def root():
    return {"message": "IoT Event API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:fastapi_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
