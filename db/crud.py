from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import IntegrityError
from .database import engine
from .mymodels import NisaAccount, OwnedProduct, Product, NisaTransaction, NisaHistory, User, FamilyStructure
import pandas as pd

def myinsert(mymodel, values):
    Session = sessionmaker(bind=engine)
    session = Session()

    new_instance = mymodel(**values)
    session.add(new_instance)
    try:
        session.commit()
        return {"status": "success"}
    except IntegrityError as e:
        print("一意制約違反により、挿入に失敗しました", e)
        session.rollback()
        return {"status": "error", "message": "一意制約違反により、挿入に失敗しました"}
    except Exception as e:
        session.rollback()
        print(f"エラーが発生しました: {e}")
        return {"status": "error", "message": f"エラーが発生しました: {e}"}
    finally:
        session.close()

def myselect(mymodel, column_name, value):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        column = getattr(mymodel, column_name)
        query = select(mymodel).where(column == value)
        result = session.execute(query)
        rows = result.scalars().all()
        result_list = []
        for row in rows:
            row_dict = row.__dict__.copy()
            row_dict.pop('_sa_instance_state', None)
            result_list.append(row_dict)
        return result_list
    finally:
        session.close()

def myselectAll(mymodel):
    Session = sessionmaker(bind=engine)
    session = Session()
    query = select(mymodel)
    try:
        with session.begin():
            df = pd.read_sql_query(query, con=engine)
            result_json = df.to_json(orient='records', force_ascii=False)
    except IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        result_json = None
    session.close()
    return result_json

def myselectUser(mymodel, user_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        query = select(mymodel).where(mymodel.user_id == user_id)
        result = session.execute(query)
        rows = result.scalars().all()
        return rows
    finally:
        session.close()

def myupdate(mymodel, values):
    Session = sessionmaker(bind=engine)
    session = Session()

    user_id = values.pop("user_id")
    query = update(mymodel).where(mymodel.user_id == user_id).values(**values)

    try:
        with session.begin():
            result = session.execute(query)
    except IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
    session.close()
    return "PUT"

def mydelete(mymodel, user_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    query = delete(mymodel).where(mymodel.user_id == user_id)
    try:
        with session.begin():
            result = session.execute(query)
    except IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()
    session.close()
    return f"{user_id} is deleted"

def get_sum_appraised_value(user_id: int, db: Session):
    result = db.query(NisaHistory.sum_appraised_value).filter(NisaHistory.user_id == user_id).first()
    print(f"Debug: {result}")  # デバッグ用に追加
    return result

def get_income(user_id: int, db: Session):
    result = db.query(NisaHistory.sum_appraised_value, NisaHistory.sum_acquisition_price).filter(NisaHistory.user_id == user_id).first()
    if result:
        return result.sum_appraised_value - result.sum_acquisition_price
    return None

def get_personal_ranking(db: Session, user_id: int):
    # ユーザーの最古の更新日を取得
    oldest_date = db.query(func.min(NisaHistory.nisa_history_update_date)).filter(NisaHistory.user_id == user_id).scalar()

    # 同じ最古の更新日を持つユーザーを取得
    users_with_oldest_date = db.query(NisaHistory.user_id).filter(NisaHistory.nisa_history_update_date == oldest_date).all()
    user_ids = [user.user_id for user in users_with_oldest_date]

    # 各ユーザーの最新のsum_appraised_value / sum_acquisition_priceを計算
    rankings = []
    for uid in user_ids:
        latest_record = db.query(NisaHistory).filter(NisaHistory.user_id == uid).order_by(NisaHistory.nisa_history_update_date.desc()).first()
        if latest_record and latest_record.sum_acquisition_price > 0:
            ratio = latest_record.sum_appraised_value / latest_record.sum_acquisition_price
            rankings.append((uid, ratio))

    # ランキングをソート
    rankings.sort(key=lambda x: x[1], reverse=True)

    # ユーザーのランキングを見つける
    my_ranking = next((index for index, value in enumerate(rankings) if value[0] == user_id), None)

    # 上位10％のユーザーを計算
    top_10_percent_count = max(1, len(rankings) // 10)
    top_10_percent_users = rankings[:top_10_percent_count]

    return {
        "myRanking": my_ranking + 1 if my_ranking is not None else None,
        "parameter": len(rankings),
        "top10PercentUsers": top_10_percent_users
    }

def get_ranking_data(db: Session, user_id: int):
    # 個人ランキング関数から上位10％のユーザーを取得
    personal_ranking = get_personal_ranking(db, user_id)
    top_10_percent_users = [user[0] for user in personal_ranking["top10PercentUsers"]]

    # 上位10％のユーザーの保有商品を集計
    product_quantities = db.query(
        OwnedProduct.product_category_id,
        func.sum(OwnedProduct.quantity).label('total_quantity')
    ).filter(OwnedProduct.nisa_account_id.in_(
        db.query(NisaAccount.nisa_account_id).filter(NisaAccount.user_id.in_(top_10_percent_users))
    )).group_by(OwnedProduct.product_category_id).all()

    # 各商品の価値を計算
    product_values = []
    for product in product_quantities:
        latest_price = db.query(Product.unit_price).filter(Product.product_category_id == product.product_category_id).order_by(Product.price_update_datetime.desc()).first()
        previous_price = db.query(Product.unit_price).filter(Product.product_category_id == product.product_category_id).order_by(Product.price_update_datetime.desc()).offset(1).first()
        if latest_price:
            value = product.total_quantity * latest_price[0]
            product_values.append((product.product_category_id, value, latest_price[0], previous_price[0] if previous_price else 0))

    # 価値で商品をソートし、上位5位を取得
    product_values.sort(key=lambda x: x[1], reverse=True)
    top_5_products = product_values[:5]

    # 商品の詳細を取得
    ranking_data = []
    for product in top_5_products:
        product_details = db.query(Product).filter(Product.product_category_id == product[0]).first()
        if product_details:
            price_difference = product[2] - product[3]
            ranking_data.append({
                "rank": top_5_products.index(product) + 1,
                "fundName": product_details.product_name,
                "price": product[2],
                "priceChange": price_difference
            })

    return ranking_data