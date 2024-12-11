from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.database import get_db
# from db.crud import
# from db.mymodels import
from db.mymodels import User, NisaAccount, OwnedProduct, Product, NisaTransaction
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


class SumAppraisedValue(BaseModel):
    sum_appraised_value: int

class Income(BaseModel):
    income: int

@app.get("/balance/{user_id}", response_model=SumAppraisedValue)
def get_balance(user_id: int, db: Session = Depends(get_db)):
    result = crud.get_sum_appraised_value(user_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    print(f"Debug: {result}")  # デバッグ用に追加
    return SumAppraisedValue(sum_appraised_value=result[0])

@app.get("/income/{user_id}", response_model=Income)
def get_income(user_id: int, db: Session = Depends(get_db)):
    income = crud.get_income(user_id, db)
    if income is None:
        raise HTTPException(status_code=404, detail="User not found")
    return Income(income=income)

@app.get("/personal-ranking/{user_id}")
def get_personal_ranking(user_id: int, db: Session = Depends(get_db)):
    return crud.get_personal_ranking(db, user_id)

@app.get("/ranking-data/{user_id}")
def get_ranking_data(user_id: int, db: Session = Depends(get_db)):
    return crud.get_ranking_data(db, user_id)