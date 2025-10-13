import base64

data_b64 = "Azac4zZT9E6SQodWyGDL5uLRCR8AbkrgUiEfpRagmDoi1LW4p5vfjav5hu2E2LVE4as3iqrHHp8mdmvkZS5NwNM1xkojF1bxhwsdegxbfJNj"

data_bytes = base64.b64decode(data_b64)
print(f"Data length: {len(data_bytes)} bytes")
print("Data bytes (hex):", data_bytes.hex())

# Optionally, dump as ints or parse fields here based on your known format
print("Data bytes (ints):", list(data_bytes))
