from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.database import get_db
# from db.crud import
# from db.mymodels import
from db.mymodels import User, NisaAccount, OwnedProduct, Product, NisaTransaction
from . import models
from db import crud, mymodels

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

@app.get("/allusers")
def read_all_users(db: Session = Depends(get_db)):
    model = User
    result = crud.myselectAll(model)
    return result

@app.get("/user/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    model = User
    result = crud.myselectUser(model, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result

class TotalAppraisedValue(BaseModel):  # 資産評価額合計
    total_appraised_value: float

@app.get("/total_appraised_value/{user_id}", response_model=TotalAppraisedValue)
def get_total_appraised_value(user_id: int, db: Session = Depends(get_db)):
    nisa_account_id = crud.get_nisa_account_id_by_user_id(user_id, db)
    if not nisa_account_id:
        raise HTTPException(status_code=404, detail="NISA account not found for the given user_id")
    
    total_appraised_value = crud.calculate_total_appraised_value(nisa_account_id, db)
    return TotalAppraisedValue(total_appraised_value=total_appraised_value)

class TotalAcquisitionValue(BaseModel):  # 取得額合計
    total_acquisition_value: float

@app.get("/total_acquisition_value/{user_id}", response_model=TotalAcquisitionValue)
def get_total_acquisition_value(user_id: int, db: Session = Depends(get_db)):
    nisa_account_id = crud.get_nisa_account_id_by_user_id(user_id, db)
    if not nisa_account_id:
        raise HTTPException(status_code=404, detail="NISA account not found for the given user_id")
    
    total_acquisition_value = crud.calculate_total_acquisition_value(nisa_account_id, db)
    return TotalAcquisitionValue(total_acquisition_value=total_acquisition_value)

class ProfitAmount(BaseModel):  # 運用益額
    profit_amount: float

@app.get("/profit_amount/{user_id}", response_model=ProfitAmount)
def get_profit_amount(user_id: int, db: Session = Depends(get_db)):
    nisa_account_id = crud.get_nisa_account_id_by_user_id(user_id, db)
    if not nisa_account_id:
        raise HTTPException(status_code=404, detail="NISA account not found for the given user_id")
    
    profit_amount = crud.calculate_profit_amount(nisa_account_id, db)
    return ProfitAmount(profit_amount=profit_amount)

class ProfitRate(BaseModel):  # 運用益率
    profit_rate: float

@app.get("/profit_rate/{user_id}", response_model=ProfitRate)
def get_profit_rate(user_id: int, db: Session = Depends(get_db)):
    nisa_account_id = crud.get_nisa_account_id_by_user_id(user_id, db)
    if not nisa_account_id:
        raise HTTPException(status_code=404, detail="NISA account not found for the given user_id")
    
    profit_rate = crud.calculate_profit_rate(nisa_account_id, db)
    return ProfitRate(profit_rate=profit_rate)

class ProfitRanking(BaseModel):  # 運用益率ランキング
    rank: int
    total_users: int

@app.get("/profit_ranking/{user_id}", response_model=ProfitRanking)
def get_profit_ranking(user_id: int, db: Session = Depends(get_db)):
    recent_user_ids = crud.get_recent_user_ids(db)
    
    if user_id not in recent_user_ids:
        raise HTTPException(status_code=404, detail="User has no recent transactions")

    profit_data = []
    
    for uid in recent_user_ids:
        nisa_account_id = crud.get_nisa_account_id_by_user_id(uid, db)
        if nisa_account_id:
            profit_rate = crud.calculate_profit_rate(nisa_account_id, db)
            profit_data.append((uid, profit_rate))
    
    profit_data.sort(key=lambda x: x[1], reverse=True)
    
    rank = next((i + 1 for i, (uid, _) in enumerate(profit_data) if uid == user_id), None)
    
    if rank is None:
        raise HTTPException(status_code=404, detail="User not found in ranking")
    
    total_users = len(profit_data)
    
    return ProfitRanking(rank=rank, total_users=total_users)

@app.get("/popular_product_{rank}/product_name/{user_id}")
def get_popular_product_name(rank: int, user_id: int, db: Session = Depends(get_db)):
    recent_user_ids = crud.get_recent_user_ids(db)
    
    if user_id not in recent_user_ids:
        raise HTTPException(status_code=404, detail="User has no recent transactions")

    top_10_percent_users = recent_user_ids[:len(recent_user_ids) // 10]

    product_quantities = db.query(
        OwnedProduct.product_id,
        func.sum(OwnedProduct.quantity).label('total_quantity')
    ).filter(OwnedProduct.user_id.in_(top_10_percent_users)).group_by(OwnedProduct.product_id).all()

    sorted_products = sorted(product_quantities, key=lambda x: x.total_quantity, reverse=True)
    
    if rank > len(sorted_products):
        raise HTTPException(status_code=400, detail="Rank out of range")

    target_product = sorted_products[rank - 1]
    
    product_name = crud.get_product_name(target_product.product_id, db)
    
    return {"product_name": product_name}

@app.get("/popular_product_{rank}/latest_unit_price/{user_id}")
def get_popular_product_latest_unit_price(rank: int, user_id: int, db: Session = Depends(get_db)):
    recent_user_ids = crud.get_recent_user_ids(db)
    
    if user_id not in recent_user_ids:
        raise HTTPException(status_code=404, detail="User has no recent transactions")

    top_10_percent_users = recent_user_ids[:len(recent_user_ids) // 10]

    product_quantities = db.query(
        OwnedProduct.product_id,
        func.sum(OwnedProduct.quantity).label('total_quantity')
    ).filter(OwnedProduct.user_id.in_(top_10_percent_users)).group_by(OwnedProduct.product_id).all()

    sorted_products = sorted(product_quantities, key=lambda x: x.total_quantity, reverse=True)
    
    if rank > len(sorted_products):
        raise HTTPException(status_code=400, detail="Rank out of range")

    target_product = sorted_products[rank - 1]
    
    latest_unit_price = crud.get_latest_unit_price(target_product.product_id, db)
    
    return {"latest_unit_price": latest_unit_price}

@app.get("/popular_product_{rank}/price_difference/{user_id}")
def get_popular_product_price_difference(rank: int, user_id: int, db: Session = Depends(get_db)):
    recent_user_ids = crud.get_recent_user_ids(db)
    
    if user_id not in recent_user_ids:
        raise HTTPException(status_code=404, detail="User has no recent transactions")

    top_10_percent_users = recent_user_ids[:len(recent_user_ids) // 10]

    product_quantities = db.query(
        OwnedProduct.product_id,
        func.sum(OwnedProduct.quantity).label('total_quantity')
    ).filter(OwnedProduct.user_id.in_(top_10_percent_users)).group_by(OwnedProduct.product_id).all()

    sorted_products = sorted(product_quantities, key=lambda x: x.total_quantity, reverse=True)
    
    if rank > len(sorted_products):
        raise HTTPException(status_code=400, detail="Rank out of range")

    target_product = sorted_products[rank - 1]
    
    price_difference = crud.get_price_difference(target_product.product_id, db)
    
    return {"price_difference": price_difference}

@app.get("/filtered_products/{user_id}")
def get_filtered_products(user_id: int, db: Session = Depends(get_db)):
    result = crud.get_filtered_products(user_id, db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result