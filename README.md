# Ship Proxy System

This repository implements a proxy system that allows all HTTP/S traffic from a ship to be tunneled through a single persistent TCP connection to an offshore proxy server. Requests are handled sequentially (one at a time).

## Architecture

- **Ship Proxy (client)** listens on port `8080`, accepts browser/curl HTTP(S) requests, frames them, and sends them over a single TCP socket.
- **Offshore Proxy (server)** listens on port `9090`, receives framed requests, performs actual HTTP(S) fetches, and returns framed responses.
- **Framing Protocol**: 4-byte big-endian length prefix + payload.

## Prerequisites

- Docker & Docker Compose (optional)
- Python 3.11+

## File Structure

```
ship-proxy-system/
├── .gitignore
├── README.md
├── docker-compose.yml
├── client/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── config.py
│   ├── utils.py
│   ├── proxy_client.py
│   └── tests/
│       └── test_proxy_client.py
└── server/
    ├── Dockerfile
    ├── requirements.txt
    ├── config.py
    ├── utils.py
    ├── proxy_server.py
    └── tests/
        └── test_proxy_server.py
```

## Building Docker Images

```bash
docker build -t yourname/ship-proxy-client ./client
docker build -t yourname/ship-proxy-server ./server
```

## Running with Docker Compose

```bash
docker-compose up --build
```

## Running Manually

1. Start server:
   ```bash
   docker run -d --name ship-proxy-server -p 9090:9090 yourname/ship-proxy-server
   ```
2. Start client:
   ```bash
   docker run -d --name ship-proxy-client -p 8080:8080 --link ship-proxy-server yourname/ship-proxy-client
   ```

## Testing

- **HTTP**: `curl -x http://localhost:8080 http://httpforever.com/`
- **HTTPS**: `curl -x http://localhost:8080 https://httpforever.com/ -k`
- **Browser**: Configure proxy to `localhost:8080`.

