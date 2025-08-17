#!/usr/bin/env python3
import os
import sys
import logging
import requests
from dotenv import load_dotenv

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def main():
    # .env 読み込み
    load_dotenv()
    
    # 必須環境変数取得
    HOST_ADDR   = os.getenv("HOST_ADDR")
    API_URL     = os.getenv("API_URL", "https://developer.dji.com/cloudapi/auth/v1/token")
    APP_KEY     = os.getenv("APP_KEY")
    APP_LICENSE = os.getenv("APP_LICENSE")
    USERNAME    = os.getenv("USERNAME")
    PASSWORD    = os.getenv("PASSWORD")
    
    # 環境変数チェック
    missing = [k for k,v in {
        "HOST_ADDR": HOST_ADDR,
        "APP_KEY": APP_KEY,
        "APP_LICENSE": APP_LICENSE,
        "USERNAME": USERNAME,
        "PASSWORD": PASSWORD
    }.items() if not v]
    if missing:
        logging.error("以下の環境変数が未設定です: %s", ", ".join(missing))
        sys.exit(1)
    
    logging.info("認証テスト開始")
    logging.debug(f"API_URL        = {API_URL}")
    logging.debug(f"APP_KEY        = {APP_KEY[:8]}...") 
    logging.debug(f"APP_LICENSE    = {APP_LICENSE[:8]}...")
    logging.debug(f"USERNAME       = {USERNAME}")
    
    # トークン取得リクエストペイロード
    payload = {
        "client_key":     APP_KEY,
        "client_license": APP_LICENSE,
        "username":       USERNAME,
        "password":       PASSWORD
    }
    
    try:
        logging.info("トークン取得リクエストを送信中...")
        resp = requests.post(API_URL, json=payload, timeout=15)
    except requests.RequestException as e:
        logging.exception("リクエスト送信中に例外発生")
        sys.exit(1)
    
    logging.info("レスポンス受信 HTTP %d", resp.status_code)
    if resp.status_code != 200:
        logging.error("トークン取得に失敗しました: %s", resp.text.strip())
        sys.exit(1)
    
    try:
        data = resp.json()
    except ValueError:
        logging.error("JSON デコードエラー: %s", resp.text.strip())
        sys.exit(1)
    
    token = data.get("access_token")
    expires = data.get("expires_in")
    if not token:
        logging.error("access_token フィールドが見つかりません")
        sys.exit(1)
    
    logging.info("アクセストークン取得成功")
    logging.debug("access_token = %s", token)
    logging.info("expires_in    = %s 秒", expires)
    
    # 接続テスト（オプション）
    # 例: ホスト疎通確認
    try:
        logging.info("ホスト疎通確認: %s に ping を試みます", HOST_ADDR)
        import subprocess
        result = subprocess.run(
            ["ping", "-c", "2", HOST_ADDR],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        logging.debug("ping stdout:\n%s", result.stdout.strip())
        logging.debug("ping stderr:\n%s", result.stderr.strip())
        if result.returncode == 0:
            logging.info("ホストに到達しました")
        else:
            logging.warning("ホストに到達できませんでした (exit code %d)", result.returncode)
    except Exception:
        logging.exception("ping テスト中に例外発生")
    
    logging.info("認証テスト完了")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
