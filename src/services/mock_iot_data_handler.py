# src/services/mock_iot_data_handler.py

import uuid
import os
import pandas as pd
from src.models.iot_sensor_data import IotSensorData

def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # directory of utils.py

    excel_file = os.path.join(BASE_DIR, "../../data/mock_iot_data.xlsx")

    dfs = pd.read_excel(
        excel_file,
        sheet_name=['mock_iot_sensors', 'mock_manuals', 'mock_events',  'mock_users', 'mock_products']
    )

    return dfs['mock_iot_sensors'], dfs['mock_manuals'], dfs['mock_events'], dfs['mock_users'], dfs['mock_products']

def detect_problems_from_sensors(sensor_data: IotSensorData, manual_df: pd.DataFrame):
    """Detect problems based on sensor data and threshold rules."""
    event_type = sensor_data.event_type
    rules = manual_df[manual_df["event_type"] == event_type]

    matched_problems = []

    # Group all rules by problem
    for problem, group in rules.groupby("problem"):
        all_conditions_met = True
        triggered_sensors = []

        for _, rule in group.iterrows():
            sensor_name = rule["sensor"]
            comparator = rule["comparator"]
            threshold = rule["threshold_value"]

            # Get live reading
            sensor_value = getattr(sensor_data, sensor_name, None)
            if sensor_value is None:
                all_conditions_met = False
                break

            condition_met = False
            if comparator == "<":
                condition_met = sensor_value < threshold
            elif comparator == ">":
                condition_met = sensor_value > threshold
            elif comparator == "=":
                condition_met = sensor_value == threshold
            elif comparator == "±":
                condition_met = abs(sensor_value) > threshold

            if condition_met:
                triggered_sensors.append({
                    "sensor": sensor_name,
                    "value": sensor_value,
                    "threshold": threshold,
                    "comparator": comparator
                })
            else:
                all_conditions_met = False
                break  # Stop if one fails

        if all_conditions_met:
            matched_problems.append({
                "problem": problem,
                "triggered_sensors": triggered_sensors
            })

    return matched_problems

def format_message(response_dict):
    import uuid  # ensure uuid is imported

    machine_id = response_dict.get("machine_id", "Unknown")
    event_type = response_dict.get("event_type", "Unknown")
    status = response_dict.get("status", "Unknown").upper()

    user_info = response_dict.get("user_info", {})
    owner_name = user_info.get("owner_name", "User")

    detected_problems = response_dict.get("detected_problems", [])

        # If no problems
    if not detected_problems:
        message_lines.append("✅ All readings are within the normal range.\n")
        return "\n".join(message_lines)

    # Header
    message_lines = [
        "🚨 *Machine Alert Notification* 🚨\n",
        f"Hi 👤 *{owner_name}*,\n",
        f"On the event of *{event_type}* in your machine *{machine_id}*, we have detected the following issues:\n",
    ]

    # Problems section
    for i, problem_data in enumerate(detected_problems, start=1):
        problem = problem_data.get("problem", "Unknown")
        actions = eval(problem_data.get("actions", "[]"))
        products = problem_data.get("detected_products", [])

        # Problem title
        message_lines.append(f"{i}. *{problem}*")

        # Recommended Actions
        if actions:
            message_lines.append("   *Recommended Actions:*")
            for act in actions:
                message_lines.append(f"      • {act}")
            message_lines.append("")

        # Service Ticket
        ticket_id = str(uuid.uuid4())[:8].upper()
        message_lines.append("🛠️ A service ticket has been initiated. An engineer will contact you shortly.")
        message_lines.append(f"   📄 *Ticket ID:* `{ticket_id}`\n")

        # Suggested Products
        if products:
            message_lines.append("🛒 *Suggested Products:*")
            for idx, p in enumerate(products, start=1):
                product_id = p.get("product_id", "N/A")
                title = p.get("title", "N/A")
                price = p.get("price_inr", "N/A")

                message_lines.append(
                    f"   {idx}. *{title}*\n"
                    f"      • Price: INR {price}\n"
                    f"      • Article Number: {product_id}\n"
                )

    # Final purchase instruction (your preferred version)
    message_lines.append(
        "✉️ To avoid delays during service, you can pre-purchase the required suggested products."
        "\n\nEnter the *Article Number* to add the item to your cart."
    )

    return "\n".join(message_lines)



