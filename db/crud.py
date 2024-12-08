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

def get_nisa_account_id_by_user_id(user_id: int, db: Session):
    nisa_account = db.query(NisaAccount).filter(NisaAccount.user_id == user_id).first()
    if nisa_account:
        return nisa_account.nisa_account_id
    return None

def calculate_total_appraised_value(nisa_account_id: int, db: Session):
    owned_products = db.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account_id).all()
    
    total_appraised_value = 0
    for owned_product in owned_products:
        product = db.query(Product).filter(Product.product_id == owned_product.product_id).first()
        total_appraised_value += owned_product.quantity * product.unit_price
    
    return total_appraised_value

def calculate_total_acquisition_value(nisa_account_id: int, db: Session):
    owned_products = db.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account_id).all()
    
    total_acquisition_value = 0
    for owned_product in owned_products:
        total_acquisition_value += owned_product.quantity * owned_product.acquisition_price
    
    return total_acquisition_value

def calculate_profit_amount(nisa_account_id: int, db: Session):
    owned_products = db.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account_id).all()
    
    total_appraised_value = 0
    total_acquisition_value = 0
    for owned_product in owned_products:
        product = db.query(Product).filter(Product.product_id == owned_product.product_id).first()
        total_appraised_value += owned_product.quantity * product.unit_price
        total_acquisition_value += owned_product.quantity * owned_product.acquisition_price
    
    profit_amount = total_appraised_value - total_acquisition_value
    
    return profit_amount

def calculate_profit_rate(nisa_account_id: int, db: Session):
    owned_products = db.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account_id).all()
    
    total_appraised_value = 0
    total_acquisition_value = 0
    for owned_product in owned_products:
        product = db.query(Product).filter(Product.product_id == owned_product.product_id).first()
        total_appraised_value += owned_product.quantity * product.unit_price
        total_acquisition_value += owned_product.quantity * owned_product.acquisition_price
    
    profit_amount = total_appraised_value - total_acquisition_value
    profit_rate = profit_amount / total_acquisition_value if total_acquisition_value != 0 else 0
    
    return profit_rate

def get_recent_user_ids(db: Session):
    three_months_ago = datetime.now() - timedelta(days=90)
    recent_transactions = db.query(NisaTransaction.user_id).filter(NisaTransaction.transaction_date >= three_months_ago).distinct().all()
    recent_user_ids = [t.user_id for t in recent_transactions]
    return recent_user_ids

def get_popular_product_ids(user_id: int, rank: int, db: Session):
    if rank < 1 or rank > 4:
        return {"error": "Rank must be between 1 and 4"}

    recent_user_ids = get_recent_user_ids(db)
    if user_id not in recent_user_ids:
        return {"error": "User has no recent transactions"}

    top_10_percent_users = recent_user_ids[:len(recent_user_ids) // 10]

    product_quantities = db.query(
        OwnedProduct.product_id,
        func.sum(OwnedProduct.quantity).label('total_quantity')
    ).filter(OwnedProduct.user_id.in_(top_10_percent_users)).group_by(OwnedProduct.product_id).all()

    sorted_products = sorted(product_quantities, key=lambda x: x.total_quantity, reverse=True)
    target_product = sorted_products[rank - 1]
    return target_product.product_id

def get_product_name(product_id: int, db: Session):
    product = db.query(Product).filter(Product.product_id == product_id).first()
    return product.product_name if product else None

def get_latest_unit_price(product_id: int, db: Session):
    latest_price = db.query(Product.unit_price).filter(Product.product_id == product_id).order_by(Product.price_update_datetime.desc()).first()
    return latest_price.unit_price if latest_price else None

def get_price_difference(product_id: int, db: Session):
    latest_prices = db.query(Product.unit_price, Product.price_update_datetime).filter(Product.product_id == product_id).order_by(Product.price_update_datetime.desc()).limit(2).all()
    if len(latest_prices) < 2:
        return None
    return latest_prices[0].unit_price - latest_prices[1].unit_price

def get_filtered_products(user_id: int, db: Session):
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user:
        return {"error": "User not found"}
    
    current_year = datetime.now().year
    user_age = current_year - user.birthday.year
    
    if user_age < 20:
        age_range_start, age_range_end = None, None
    elif user_age < 30:
        age_range_start, age_range_end = current_year - 29, current_year - 20
    elif user_age < 40:
        age_range_start, age_range_end = current_year - 39, current_year - 30
    elif user_age < 50:
        age_range_start, age_range_end = current_year - 49, current_year - 40
    elif user_age < 60:
        age_range_start, age_range_end = current_year - 59, current_year - 50
    elif user_age < 70:
        age_range_start, age_range_end = current_year - 69, current_year - 60
    else:
        age_range_start, age_range_end = None, current_year - 70
    
    family_income = db.query(FamilyStructure.family_annual_income).filter(FamilyStructure.user_id == user_id).first()
    
    if not family_income:
        income_lower_bound, income_upper_bound = None, None
    else:
        income_lower_bound = family_income.family_annual_income - 100
        income_upper_bound = family_income.family_annual_income + 100
    
    query = db.query(User)
    
    if age_range_start and age_range_end:
        query = query.filter(func.extract('year', User.birthday).between(age_range_start, age_range_end))
    
    if income_lower_bound and income_upper_bound:
        query = query.join(FamilyStructure).filter(FamilyStructure.family_annual_income.between(income_lower_bound, income_upper_bound))
    
    filtered_users = query.all()
    
    filtered_user_ids = [user.user_id for user in filtered_users]
    
    product_quantities = db.query(
        OwnedProduct.product_id,
        func.sum(OwnedProduct.quantity).label('total_quantity')
    ).filter(OwnedProduct.user_id.in_(filtered_user_ids)).group_by(OwnedProduct.product_id).all()

    sorted_products = sorted(product_quantities, key=lambda x: x.total_quantity, reverse=True)

    top_products = []
    
    for product_data in sorted_products[:4]:
        product = db.query(Product).filter(Product.product_id == product_data.product_id).first()
        
        latest_prices = db.query(Product.unit_price, Product.price_update_datetime).filter(
            Product.product_id == product.product_id
        ).order_by(Product.price_update_datetime.desc()).limit(2).all()
        
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