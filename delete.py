import json

data = '{"motion": {"value": 1}, "logs": {"type": "info", "message": "System is on"}}'
result = json.loads(data)
print(result)
print(result["motion"]["value"])
