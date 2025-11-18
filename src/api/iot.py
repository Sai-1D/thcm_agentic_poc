# src/api/iot.py

import os
import ast
from fastapi import APIRouter, Path, HTTPException
from src.models.iot_sensor_data import IotSensorData
from src.services.mock_iot_data_handler import load_data, detect_problems_from_sensors, format_message
from src.services.messaging import send_msg

env_number = os.getenv("TESTER_WHATSAPP_NUMBER")
TESTER_WHATSAPP_NUMBER = f"whatsapp:{env_number}" if env_number else None

mock_iot_sensors_df, mock_manuals_df, mock_events_df, mock_users_df, mock_products_df = load_data()
router = APIRouter(prefix="/api", tags=["IoT-Event"])

@router.post("/iot-event")
async def iot_event(sensor_data: IotSensorData):
    machine_id = sensor_data.machine_id
    event_type = sensor_data.event_type
    user_info = mock_users_df.loc[mock_users_df['machine_id'] == sensor_data.machine_id].iloc[0].to_dict()

    response_dict = {
            "machine_id": machine_id,
            "event_type": event_type,
            "user_info": user_info,
            "status": "normal",
            "message": "All sensor readings are within normal range."
    }

    # Detect potential problems
    matched_problems = detect_problems_from_sensors(sensor_data, mock_manuals_df)
    
    # If no problems, return success
    if len(matched_problems) == 0:
        return response_dict
    
    response_dict['status'] = 'alert'

    detected_problems = []
    # If problems found, collect detailed results
    for problem in matched_problems:
        # Find event row(s) matching event type and problem
        event_row = mock_events_df.loc[
            (mock_events_df["event_type"] == event_type) &
            (mock_events_df["problem"] == problem['problem'])
        ]

        if event_row.empty:
            continue  # skip if no event record found

        event_info = event_row.iloc[0].to_dict()
        event_info.pop('event_type', "unknown")

        # Each event might have multiple product_ids
        product_ids = event_info.get("product_ids", [])

        # Safely iterate over product_ids (assuming list-like)
        detected_products = []
        for product_id in ast.literal_eval(product_ids):
            product_row = mock_products_df.loc[mock_products_df["product_id"] == product_id]
            if not product_row.empty:
                detected_products.append(product_row.iloc[0].to_dict())

        event_info['detected_products'] = detected_products
        detected_problems.append(event_info)

    response_dict['detected_problems'] = detected_problems
    target_number = TESTER_WHATSAPP_NUMBER or f"whatsapp:+{user_info['phone']}"
    await send_msg(format_message(response_dict), target_number)

    return response_dict


@router.get("/iot-event/{item_id}")
async def iot_event(
    item_id: int = Path(..., ge=1, le=12, description="Item ID must be between 1 and 12")
):
    """
    Fetch a specific mock IoT data row by ID (1-indexed)
    and return it as an IotSensorData response.
    """
    if item_id < 1 or item_id > len(mock_iot_sensors_df):
        raise HTTPException(status_code=404, detail="Item ID out of range")

    row_dict = mock_iot_sensors_df.iloc[item_id - 1].to_dict()
    return IotSensorData(**row_dict)