from fastapi import FastAPI, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.database import get_db
# from db.crud import
# from db.mymodels import
from db.mymodels import NisaAccount, OwnedProduct, Product, NisaTransaction
from . import models

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

@app.get("/profit_ranking")
def get_profit_ranking(db: Session = Depends(get_db)):
    # 3か月以内の取引があるユーザーをフィルタリング
    three_months_ago = datetime.now() - timedelta(days=90)
    recent_transactions = db.query(models.NisaTransaction.user_id).filter(models.NisaTransaction.transaction_date >= three_months_ago).distinct().all()
    recent_user_ids = [t.user_id for t in recent_transactions]

    # 運用益を計算
    profit_data = db.query(
        models.NisaHistory.user_id,
        (models.NisaHistory.sum_appraised_value / models.NisaHistory.sum_acquisition_price).label('profit_ratio')
    ).filter(models.NisaHistory.user_id.in_(recent_user_ids)).all()

    # ランキングを作成
    profit_data.sort(key=lambda x: x.profit_ratio, reverse=True)
    ranking = [{"user_id": data.user_id, "profit_ratio": data.profit_ratio} for data in profit_data]

    return ranking

@app.get("/popular_product_1")
def get_popular_product_1(db: Session = Depends(get_db)):
    # 運用益ランキングの上位10％のユーザーを取得
    profit_ranking = get_profit_ranking(db)
    top_10_percent_users = [r['user_id'] for r in profit_ranking[:len(profit_ranking) // 10]]

    # 所有商品の数量を集計
    product_quantities = db.query(
        models.OwnedProduct.product_id,
        func.sum(models.OwnedProduct.quantity).label('total_quantity')
    ).filter(models.OwnedProduct.user_id.in_(top_10_percent_users)).group_by(models.OwnedProduct.product_id).all()

    # 最も多い商品を取得
    most_popular_product = max(product_quantities, key=lambda x: x.total_quantity)
    product = db.query(models.Product).filter(models.Product.product_id == most_popular_product.product_id).first()

    # 最新の価格差を計算
    latest_prices = db.query(models.Product.unit_price, models.Product.price_update_datetime).filter(models.Product.product_id == product.product_id).order_by(models.Product.price_update_datetime.desc()).limit(2).all()
    price_difference = latest_prices[0].unit_price - latest_prices[1].unit_price

    return {
        "product_name": product.product_name,
        "latest_unit_price": latest_prices[0].unit_price,
        "price_difference": price_difference
    }

@app.get("/popular_product_{rank}")
def get_popular_product(rank: int, db: Session = Depends(get_db)):
    if rank < 1 or rank > 4:
        return {"error": "Rank must be between 1 and 4"}

    # 運用益ランキングの上位10％のユーザーを取得
    profit_ranking = get_profit_ranking(db)
    top_10_percent_users = [r['user_id'] for r in profit_ranking[:len(profit_ranking) // 10]]

    # 所有商品の数量を集計
    product_quantities = db.query(
        models.OwnedProduct.product_id,
        func.sum(models.OwnedProduct.quantity).label('total_quantity')
    ).filter(models.OwnedProduct.user_id.in_(top_10_percent_users)).group_by(models.OwnedProduct.product_id).all()

    # 指定された順位の人気商品を取得
    sorted_products = sorted(product_quantities, key=lambda x: x.total_quantity, reverse=True)
    target_product = sorted_products[rank - 1]
    product = db.query(models.Product).filter(models.Product.product_id == target_product.product_id).first()

    # 最新の価格差を計算
    latest_prices = db.query(models.Product.unit_price, models.Product.price_update_datetime).filter(models.Product.product_id == product.product_id).order_by(models.Product.price_update_datetime.desc()).limit(2).all()
    price_difference = latest_prices[0].unit_price - latest_prices[1].unit_price

    return {
        "product_name": product.product_name,
        "latest_unit_price": latest_prices[0].unit_price,
        "price_difference": price_difference
    }

@app.get("/filtered_products")
def get_filtered_products(
    age_range: str = Query(None, description="年代を指定（例: '20s', '30s', '40s', '50s', '60s', '70s+'）"),
    income_range: int = Query(None, description="年収を指定（例: 500）"),
    db: Session = Depends(get_db)
):
    query = db.query(models.User)

    # 年代フィルタリング
    if age_range:
        current_year = datetime.now().year
        if age_range == '20s':
            start_year = current_year - 29
            end_year = current_year - 20
        elif age_range == '30s':
            start_year = current_year - 39
            end_year = current_year - 30
        elif age_range == '40s':
            start_year = current_year - 49
            end_year = current_year - 40
        elif age_range == '50s':
            start_year = current_year - 59
            end_year = current_year - 50
        elif age_range == '60s':
            start_year = current_year - 69
            end_year = current_year - 60
        elif age_range == '70s+':
            end_year = current_year - 70
            query = query.join(models.FamilyStructure).filter(
                func.extract('year', models.FamilyStructure.family_birthday) <= end_year
            )
        else:
            return {"error": "Invalid age range"}
        
        if age_range != '70s+':
            query = query.join(models.FamilyStructure).filter(
                func.extract('year', models.FamilyStructure.family_birthday).between(start_year, end_year)
            )

    # 年収フィルタリング
    if income_range:
        income_lower_bound = income_range - 100
        income_upper_bound = income_range + 100
        query = query.join(models.FamilyStructure).filter(
            models.FamilyStructure.family_annual_income.between(income_lower_bound, income_upper_bound)
        )

    # フィルタリングされたユーザーを取得
    filtered_users = query.all()
    filtered_user_ids = [user.user_id for user in filtered_users]

    # 所有商品の数量を集計
    product_quantities = db.query(
        models.OwnedProduct.product_id,
        func.sum(models.OwnedProduct.quantity).label('total_quantity')
    ).filter(models.OwnedProduct.user_id.in_(filtered_user_ids)).group_by(models.OwnedProduct.product_id).all()

    # 所有商品の数量でソート
    sorted_products = sorted(product_quantities, key=lambda x: x.total_quantity, reverse=True)

    # 上位4つの商品の情報を取得
    top_products = []
    for product_data in sorted_products[:4]:
        product = db.query(models.Product).filter(models.Product.product_id == product_data.product_id).first()
        latest_prices = db.query(models.Product.unit_price, models.Product.price_update_datetime).filter(
            models.Product.product_id == product.product_id
        ).order_by(models.Product.price_update_datetime.desc()).limit(2).all()
        
        if len(latest_prices) < 2:
            price_difference = None
        else:
            price_difference = latest_prices[0].unit_price - latest_prices[1].unit_price
        
        top_products.append({
            "product_name": product.product_name,
            "latest_unit_price": latest_prices[0].unit_price if latest_prices else None,
            "price_difference": price_difference
        })

    return top_products