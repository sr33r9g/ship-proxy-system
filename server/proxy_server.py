import asyncio
import httpx
from config import SERVER_HOST, SERVER_PORT
from utils import frame_message, unframe_message

async def fetch_from_internet(request_bytes: bytes) -> bytes:
    header, _, body = request_bytes.partition(b'\r\n\r\n')
    request_line = header.split(b'\r\n')[0].decode()
    method, path, version = request_line.split()
    headers = {}
    for line in header.split(b'\r\n')[1:]:
        if line:
            k, v = line.decode().split(':', 1)
            headers[k.strip()] = v.strip()
    url = path if path.startswith('http') else f"http://{headers.get('Host')}{path}"
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=headers, content=body)
        status_line = f"HTTP/1.1 {resp.status_code} {resp.reason_phrase}\r\n".encode()
        resp_headers = b''.join(f"{k}: {v}\r\n".encode() for k, v in resp.headers.items())
        return status_line + resp_headers + b'\r\n' + resp.content

async def handle_ship(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    while True:
        try:
            req = await unframe_message(reader)
            resp = await fetch_from_internet(req)
            writer.write(frame_message(resp))
            await writer.drain()
        except asyncio.IncompleteReadError:
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    writer.close()

async def main():
    server = await asyncio.start_server(handle_ship, SERVER_HOST, SERVER_PORT)
    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Server listening on {addrs}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())