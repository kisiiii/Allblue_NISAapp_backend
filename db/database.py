# データベースに接続

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

try:
    from .config import DATABASE_URL #相対インポート
except ImportError:  
    from config import DATABASE_URL #絶対インポート

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10},
    pool_size=10,  # プールのサイズを設定
    max_overflow=20  # プールを超えて作成できる接続の最大数
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
