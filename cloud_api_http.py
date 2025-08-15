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
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse

load_dotenv()

HOST_ADDR    = os.getenv("HOST_ADDR", "0.0.0.0")
HTTP_PORT    = int(os.getenv("HTTP_PORT", 5000))
CLIENT_KEY   = os.environ["CLIENT_KEY"]
APP_LICENSE  = os.environ["APP_LICENSE"]
USERNAME     = os.environ["USERNAME"]
PASSWORD     = os.environ["PASSWORD"]

app = FastAPI()

@app.get("/login")
async def pilot_login():
    path = "./couldhtml/login.html"
    if not os.path.exists(path):
        raise HTTPException(500, "Template not found")
    content = open(path, encoding="utf-8").read()
    content = content.replace("hostnamehere", HOST_ADDR)
    content = content.replace("userloginhere", USERNAME)
    content = content.replace("userpasswordhere", PASSWORD)
    return HTMLResponse(content)

@app.post("/auth/token")
async def auth_token(username: str = Form(...), password: str = Form(...)):
    url = "https://developer.dji.com/cloudapi/auth/v1/token"
    payload = {
        "client_key":    CLIENT_KEY,
        "client_license": APP_LICENSE,
        "username":      username,
        "password":      password
    }
    resp = requests.post(url, json=payload, timeout=10)
    if resp.status_code != 200:
        raise HTTPException(502, "Token fetch failed")
    data = resp.json()
    return JSONResponse({"access_token": data["access_token"], "expires_in": data["expires_in"]})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=HTTP_PORT)
