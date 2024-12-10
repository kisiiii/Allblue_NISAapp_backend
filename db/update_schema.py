from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mymodels import Base, engine

# データベーススキーマの更新
Base.metadata.create_all(bind=engine)