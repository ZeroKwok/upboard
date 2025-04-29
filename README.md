# upboard

upboard (Update-Board) is a lightweight CLI tool for managing and delivering updated versions of applications during testing.

**upboard** helps you distribute software updates to clients by providing a simple HTTP server (`upboard-server`) and a   file publisher (`upboard-publish`). Applications can check for and download updates dynamically at runtime using standard HTTP requests.

## 📦 Installation

```bash
pip install upboard
```

## 🚀 Usage

### Start the update server

```bash
upboard-server --dir ./release-dir --port 8000 --password mysecret
```

- Serves static files from `./release-dir`
- Accepts authenticated `PUT` uploads at `/api/v1/artifacts/...`

### Upload a file

```bash
upboard-publish --password mysecret http://localhost:8000/api/v1/artifacts/win32/x64/1.2.3-beta/ your-release-file
```

### Check for updates (client-side, GET request)

```http
GET /api/v1/updates/your-project/win32/x64/1.2.3-beta/your-release-file
```

## 📁 API Overview

| Description                     | Method | Endpoint Example                                                      |
|---------------------------------|--------|-----------------------------------------------------------------------|
| Upload a new version            | PUT    | `/api/v1/releases/<product>/<platform>/<arch>[/<version>]/<filename>` |
| Check if a newer version exists | GET    | `/api/v1/updates/<product>/<platform>/<arch>[/<version>]/<filename>`  |

## 📄 License

MIT License
