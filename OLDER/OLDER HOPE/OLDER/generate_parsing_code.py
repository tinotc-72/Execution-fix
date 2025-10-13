from struct import unpack

data_hex = "45c8fef7283476ca0a51050000000000c58ae11e01000000e780b51701000000010000000a510500000000000100000001000000010000002a010000006420b381800000000032fd9a010000000000"
data_bytes = bytes.fromhex(data_hex)

chunk_size = 8
chunks = [data_bytes[i:i+chunk_size] for i in range(0, len(data_bytes), chunk_size)]

for i, chunk in enumerate(chunks):
    if len(chunk) < chunk_size:
        print(f"Chunk {i}: less than 8 bytes, raw: {chunk.hex()}")
    else:
        val = unpack("<Q", chunk)[0]  # Little endian unsigned 64-bit int
        print(f"Chunk {i}: {val} (hex: {val:#018x})")
