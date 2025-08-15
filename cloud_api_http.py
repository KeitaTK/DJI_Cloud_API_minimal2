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
from dotenv import load_dotenv

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

# .env を読み込む
load_dotenv()

# 環境変数を取得
host_addr = os.environ.get("HOST_ADDR", "0.0.0.0")
http_port = int(os.environ.get("HTTP_PORT", 5000))
username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]

app = FastAPI()

@app.get("/login")
async def pilot_login():
    # HTML テンプレートを読み込み、プレースホルダを置換して返す
    file_path = "./couldhtml/login.html"
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()
    file_content = file_content.replace("hostnamehere", host_addr)
    file_content = file_content.replace("userloginhere", username)
    file_content = file_content.replace("userpasswordhere", password)
    return HTMLResponse(file_content)

if __name__ == "__main__":
    # all interfaces で待ち受け、.env の HTTP_PORT を使う
    uvicorn.run(app, host="0.0.0.0", port=http_port)
