from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mysql.connector import Error

from db.database import get_db
# from db.crud import
# from db.mymodels import
from db.mymodels import NisaAccount, OwnedProduct, Product, NisaTransaction

app = FastAPI()

# CORSの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて特定のオリジンに変更 ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

class TotalAppraisedValue(BaseModel): #資産評価額合計
    total_appraised_value: float
@app.get("/total_appraised_value/{nisa_account_id}", response_model=TotalAppraisedValue) 
def get_total_appraised_value(nisa_account_id: int, db: Session = Depends(get_db)):
    owned_products = db.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account_id).all()
    
    total_appraised_value = 0
    for owned_product in owned_products:
        product = db.query(Product).filter(Product.product_id == owned_product.product_id).first()
        total_appraised_value += owned_product.quantity * product.unit_price
    
    return TotalAppraisedValue(total_appraised_value=total_appraised_value)

class TotalAcquisitionValue(BaseModel): #取得額合計
    total_acquisition_value: float

@app.get("/total_acquisition_value/{nisa_account_id}", response_model=TotalAcquisitionValue)
def get_total_acquisition_value(nisa_account_id: int, db: Session = Depends(get_db)):
    owned_products = db.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account_id).all()
    
    total_acquisition_value = 0
    for owned_product in owned_products:
        total_acquisition_value += owned_product.quantity * owned_product.acquisition_price
    
    return TotalAcquisitionValue(total_acquisition_value=total_acquisition_value)

class ProfitAmount(BaseModel): #運用益額
    profit_amount: float

@app.get("/profit_amount/{nisa_account_id}", response_model=ProfitAmount)
def get_profit_amount(nisa_account_id: int, db: Session = Depends(get_db)):
    owned_products = db.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account_id).all()
    
    total_appraised_value = 0
    total_acquisition_value = 0
    for owned_product in owned_products:
        product = db.query(Product).filter(Product.product_id == owned_product.product_id).first()
        total_appraised_value += owned_product.quantity * product.unit_price
        total_acquisition_value += owned_product.quantity * owned_product.acquisition_price
    
    profit_amount = total_appraised_value - total_acquisition_value
    
    return ProfitAmount(profit_amount=profit_amount)

class ProfitRate(BaseModel): #運用益率
    profit_rate: float

@app.get("/profit_rate/{nisa_account_id}", response_model=ProfitRate)
def get_profit_rate(nisa_account_id: int, db: Session = Depends(get_db)):
    owned_products = db.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account_id).all()
    
    total_appraised_value = 0
    total_acquisition_value = 0
    for owned_product in owned_products:
        product = db.query(Product).filter(Product.product_id == owned_product.product_id).first()
        total_appraised_value += owned_product.quantity * product.unit_price
        total_acquisition_value += owned_product.quantity * owned_product.acquisition_price
    
    profit_amount = total_appraised_value - total_acquisition_value
    profit_rate = profit_amount / total_acquisition_value if total_acquisition_value != 0 else 0
    
    return ProfitRate(profit_rate=profit_rate)