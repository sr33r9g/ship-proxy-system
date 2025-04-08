import asyncio

def frame_message(message: bytes) -> bytes:
    length = len(message).to_bytes(4, 'big')
    return length + message

async def read_exactly(reader: asyncio.StreamReader, n: int) -> bytes:
    return await reader.readexactly(n)

async def unframe_message(reader: asyncio.StreamReader) -> bytes:
    length_bytes = await read_exactly(reader, 4)
    length = int.from_bytes(length_bytes, 'big')
    return await read_exactly(reader, length)