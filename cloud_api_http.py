# #!/usr/bin/env python3
# import os
# from dotenv import load_dotenv

# import uvicorn
# from fastapi import FastAPI
# from fastapi.responses import HTMLResponse

# load_dotenv()

# host_addr = os.environ["HOST_ADDR"]
# username = os.environ["USERNAME"]
# password = os.environ["PASSWORD"]

# app = FastAPI()


# @app.get("/login")
# async def pilot_login():
#     file_path = "./couldhtml/login.html"
#     with open(file_path, 'r') as file:
#         file_content = file.read()
#     file_content.replace("hostnamehere", host_addr)
#     file_content.replace("userloginhere", username)
#     file_content.replace("userpasswordhere", password)
#     return HTMLResponse(file_content)


# if __name__ == "__main__":
#     uvicorn.run(app, host=host_addr, port=5000)


#!/usr/bin/env python3
import os
import requests
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# 環境変数
HOST_ADDR   = os.getenv("HOST_ADDR", "0.0.0.0")
HTTP_PORT   = int(os.getenv("HTTP_PORT", 5000))
API_URL     = os.getenv("API_URL", "http://localhost:6789")  # Backend URL
APP_KEY     = os.environ["APP_KEY"]
APP_LICENSE = os.environ["APP_LICENSE"]
USERNAME    = os.environ["USERNAME"]
PASSWORD    = os.environ["PASSWORD"]

app = FastAPI()

# CORS設定（フロントエンドからのfetchを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/login")
async def pilot_login():
    """Pilot App用ログイン画面を返す"""
    file_path = "./couldhtml/login.html"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Template not found")
    
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # プレースホルダ置換（重要：戻り値を再代入）
    content = content.replace("hostnamehere", HOST_ADDR)
    content = content.replace("userloginhere", USERNAME)
    content = content.replace("userpasswordhere", PASSWORD)
    
    return HTMLResponse(content)

@app.post("/auth/token")
async def auth_token(
    username: str = Form(...),
    password: str = Form(...),
    app_id: int = Form(None),
    app_key: str = Form(None)
):
    """
    トークン取得エンドポイント
    バックエンド（cloud_api_sample）または直接DJI認証サーバーへプロキシ
    """
    try:
        # Option 1: 直接DJI認証サーバーへリクエスト
        if API_URL.startswith("http://localhost:6789"):
            # バックエンドサーバー経由
            payload = {
                "username": username,
                "password": password,
                "app_key": APP_KEY,
                "app_license": APP_LICENSE
            }
            response = requests.post(f"{API_URL}/auth/token", json=payload, timeout=10)
        else:
            # 直接DJI認証サーバー
            payload = {
                "client_key": APP_KEY,
                "client_license": APP_LICENSE,
                "username": username,
                "password": password
            }
            response = requests.post("https://developer.dji.com/cloudapi/auth/v1/token", 
                                   json=payload, timeout=10)
        
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Token fetch failed: {response.text}")
        
        token_data = response.json()
        return JSONResponse({
            "access_token": token_data.get("access_token"),
            "expires_in": token_data.get("expires_in", 7200),
            "token_type": "Bearer"
        })
        
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Backend connection failed: {str(e)}")

@app.get("/api/config")
async def get_config():
    """設定情報を返すエンドポイント（デバッグ用）"""
    return JSONResponse({
        "host_addr": HOST_ADDR,
        "app_key": APP_KEY[:10] + "...",  # セキュリティのため一部のみ表示
        "username": USERNAME,
        "backend_url": API_URL
    })

@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": uuid.uuid4().hex
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=HTTP_PORT)
