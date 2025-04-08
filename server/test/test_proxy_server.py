import asyncio
import pytest
from utils import frame_message, unframe_message

@pytest.mark.asyncio
async def test_frame_and_unframe():
    message = b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n'
    framed = frame_message(message)
    reader = asyncio.StreamReader()
    reader.feed_data(framed)
    reader.feed_eof()
    result = await unframe_message(reader)
    assert result == message