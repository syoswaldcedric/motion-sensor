import psutil
import json

MESSAGE_TYPES = {
    "MOTION": "MOTION",
    "SYSTEM_INFO": "SYSTEM_INFO",
    "LOGS": "LOGS",
}


def get_system_info():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
    }


SYSTEM_INFO = "SYSTEM_INFO"
data = {"type": MESSAGE_TYPES.get("SYSTEM_INFO"), "data": get_system_info()}

str_data = json.dumps(data)
print(str_data, type(str_data))
