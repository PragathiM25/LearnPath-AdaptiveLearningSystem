# LearnPath

## Run locally

1. Start the backend from the project root:

   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

2. Start Ollama in another terminal and download the configured model:

   ```powershell
   ollama pull llama3.2:3b
   ```

   The backend expects Ollama at `http://localhost:11434` by default. Configure
   `OLLAMA_BASE_URL` and `OLLAMA_MODEL` in `backend\.env` if needed.

3. Start the frontend in another terminal:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   Open `http://localhost:5173`. Vite forwards `/api` requests to
   `http://127.0.0.1:8000`, and the frontend displays the backend connection
   status in the top bar.

The frontend API URL can be overridden with `VITE_API_BASE_URL` (for example,
`https://api.example.com/api`). For cross-origin deployments, set
`CORS_ORIGINS` in `backend\.env` to a comma-separated list of trusted frontend
origins.