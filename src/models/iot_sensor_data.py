# src/models/iot_sensor_data.py

from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class IotSensorData(BaseModel):
    machine_id: str = Field(..., example="machine-001")
    event_type: Literal[
        "engine_overheat",
        "bucket_overload",
        "tipping_risk",
        "low_oil_pressure"
    ] = Field(..., example="engine_overheat")
    timestamp: datetime = Field(..., example="2025-11-13T09:00:00Z")

    coolant_level: float = Field(..., example=25.0, description="Coolant level in percentage (%)")
    engine_temp: float = Field(..., example=110.0, description="Engine temperature in °C")
    coolant_flow: float = Field(..., example=8.0, description="Coolant flow rate in L/min")
    pump_vibration: float = Field(..., example=6.0, description="Pump vibration in mm/s")

    load_sensor: float = Field(..., example=1800.0, description="Load on bucket in kg")
    hydraulic_pressure: float = Field(..., example=220.0, description="Hydraulic pressure in bar")
    bucket_type: int = Field(..., example=1, description="Bucket type identifier")

    tilt_sensor: float = Field(..., example=4.0, description="Tilt angle in degrees (°)")
    ground_vibration: float = Field(..., example=0.3, description="Ground vibration in g")
    wheel_speed: float = Field(..., example=12.0, description="Wheel speed in km/h")
    bucket_angle: float = Field(..., example=4.0, description="Bucket angle in degrees (°)")

    oil_level: float = Field(..., example=25.0, description="Oil level in percentage (%)")
    pressure_diff: float = Field(..., example=0.6, description="Oil pressure difference in bar")
    oil_pressure: float = Field(..., example=1.2, description="Oil pressure in bar")
    oil_flow: float = Field(..., example=4.0, description="Oil flow rate in L/min")

