from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, update, delete
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