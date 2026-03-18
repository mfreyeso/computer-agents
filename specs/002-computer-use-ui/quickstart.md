# UI Quickstart
**Running the Web Interface locally for Development**

## Prerequisites
- Node.js (v18+)
- Local 001-computer-use-api running at `0.0.0.0:8000`.

## Installation

```bash
cd src/ui
npm install
# or yarn install / pnpm i
```

## Running the Development Server
```bash
npm run dev
```
Navigate to `http://localhost:5173`. Modifying any components dynamically hot-reloads within milliseconds.

## Environment Variables
The application connects structurally to standard endpoints relying on Vite's `.env.local` or raw process config mappings:
- `VITE_API_BASE_URL="http://localhost:8000"`
- `VITE_WS_BASE_URL="ws://localhost:8000"`
