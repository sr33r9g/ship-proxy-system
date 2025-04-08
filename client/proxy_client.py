import asyncio
from config import SHIP_PROXY_HOST, SHIP_PROXY_PORT, SERVER_HOST, SERVER_PORT, QUEUE_MAXSIZE
from utils import frame_message, unframe_message

async def read_http_request(reader: asyncio.StreamReader) -> bytes:
    headers = b''
    while True:
        line = await reader.readline()
        if not line:
            break
        headers += line
        if headers.endswith(b'\r\n\r\n'):
            break
    header_text = headers.decode('latin-1')
    content_length = 0
    for line in header_text.split('\r\n'):
        if line.lower().startswith('content-length:'):
            content_length = int(line.split(':', 1)[1].strip())
            break
    body = b''
    if content_length:
        body = await reader.readexactly(content_length)
    return headers + body

request_queue = asyncio.Queue(maxsize=QUEUE_MAXSIZE)

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    try:
        data = await read_http_request(reader)
        await request_queue.put((data, writer))
    except Exception as e:
        print(f"Error handling client: {e}")
        writer.close()

async def worker():
    reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
    while True:
        data, client_writer = await request_queue.get()
        writer.write(frame_message(data))
        await writer.drain()
        resp = await unframe_message(reader)
        client_writer.write(resp)
        await client_writer.drain()
        client_writer.close()
        request_queue.task_done()

async def main():
    server = await asyncio.start_server(handle_client, SHIP_PROXY_HOST, SHIP_PROXY_PORT)
    asyncio.create_task(worker())
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on {addrs}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())