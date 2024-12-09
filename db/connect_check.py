import os
from dotenv import load_dotenv
from sqlalchemy import text
from database import engine

# 環境変数の再読み込み
load_dotenv()

def check_db_connection():
    try:
        # 環境変数の確認
        ssl_ca_path = os.environ.get("SSL_CA_PATH")
        print("SSL_CA_PATH:", ssl_ca_path)
        
        # ファイルの存在確認
        if not os.path.isfile(ssl_ca_path):
            raise FileNotFoundError(f"File not found: {ssl_ca_path}")
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("接続成功:", result.scalar())
    except Exception as e:
        print("接続失敗:", e)
        print("エラーメッセージの詳細:", e.args)

if __name__ == "__main__":
    check_db_connection()