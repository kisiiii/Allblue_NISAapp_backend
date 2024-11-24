#テーブルの設定
#データベースにテーブルを作成

from sqlalchemy import Column, Integer, String, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base, engine

# 商品マスタ（Products Table）
class Product(Base):
    __tablename__ = "products"

    PRD_ID = Column(Integer, primary_key=True, autoincrement=True)
    CODE = Column(String(13), unique=True, nullable=False)
    NAME = Column(String(50), nullable=False)
    PRICE = Column(Integer, nullable=False)
    COST = Column(Integer, nullable=False) #事故検証用
    SUPPLIER = Column(String(50),nullable=False) #事故検証用
    MANUFACTURER = Column(String(50),nullable=False) #事故検証用

    details = relationship("TransactionDetail", back_populates="product")


# 税マスタ（Tax Table）
class Tax(Base):
    __tablename__ = "taxes"

    ID = Column(Integer, primary_key=True, autoincrement=True)
    CODE = Column(String(2), unique=True, nullable=False)
    NAME = Column(String(20), nullable=False)
    PERCENT = Column(DECIMAL(3, 2), nullable=False)

    details = relationship("TransactionDetail", back_populates="tax")


# 取引（Transaction Table）
class Transaction(Base):
    __tablename__ = "transactions"

    TRD_ID = Column(Integer, primary_key=True, autoincrement=True)
    DATETIME = Column(TIMESTAMP, nullable=False)
    EMP_CD = Column(String(10), nullable=False)
    STORE_CD = Column(String(5), nullable=False)
    POS_NO = Column(String(3), nullable=False)
    TOTAL_AMT = Column(Integer, nullable=False)
    TTL_AMT_EX_TAX = Column(Integer, nullable=False)

    details = relationship("TransactionDetail", back_populates="transaction")


# 取引明細（Transaction Detail Table）
class TransactionDetail(Base):
    __tablename__ = "transaction_details"

    TRD_ID = Column(Integer, ForeignKey('transactions.TRD_ID'), primary_key=True)
    DTL_ID = Column(Integer, primary_key=True, autoincrement=True)
    PRD_ID = Column(Integer, ForeignKey('products.PRD_ID'), nullable=False)
    PRD_CODE = Column(String(13), nullable=False)
    PRD_NAME = Column(String(50), nullable=False)
    PRD_PRICE = Column(Integer, nullable=False)
    TAX_CD = Column(String(2), ForeignKey('taxes.CODE'), nullable=False)

    product = relationship("Product", back_populates="details")
    tax = relationship("Tax", back_populates="details")
    transaction = relationship("Transaction", back_populates="details")


# テーブルの作成
Base.metadata.create_all(bind=engine)
