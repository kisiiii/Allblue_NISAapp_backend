from sqlalchemy import text
from database import engine


def check_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("接続成功:", result.scalar())
    except Exception as e:
        print("接続失敗:", e)


if __name__ == "__main__":
    check_db_connection()
