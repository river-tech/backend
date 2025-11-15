from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    allowed_origins = [
        # --- Local Development ---
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",

        # --- LAN Development (WiFi) ---
        "http://172.25.67.101:3000",
        "http://172.25.67.101:3001",

        # --- Production Frontend ---
        "https://app.usitech.io.vn",
        "https://admin.usitech.io.vn",

        # --- Production Backend Swagger ---
        "https://api.usitech.io.vn"
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )