import os
from dotenv import load_dotenv
from sqlalchemy import text
from database import engine

# 環境変数の再読み込み
load_dotenv()

def check_db_connection():
    try:
        # 環境変数の確認
        print("SSL_CA_PATH:", os.environ.get("SSL_CA_PATH"))
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("接続成功:", result.scalar())
    except Exception as e:
        print("接続失敗:", e)

if __name__ == "__main__":
    check_db_connection()