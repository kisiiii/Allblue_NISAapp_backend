from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import select, update, delete, func, extract
from sqlalchemy.exc import IntegrityError
from .database import engine
from .mymodels import NisaAccount, OwnedProduct, Product, NisaTransaction, NisaHistory, User, FamilyStructure
import pandas as pd
from datetime import datetime, timedelta


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
    result = db.query(NisaHistory.sum_appraised_value).filter(
        NisaHistory.user_id == user_id).first()
    print(f"Debug: {result}")  # デバッグ用に追加
    return result


def get_income(user_id: int, db: Session):
    result = db.query(NisaHistory.sum_appraised_value, NisaHistory.sum_acquisition_price).filter(
        NisaHistory.user_id == user_id).first()
    if result:
        return result.sum_appraised_value - result.sum_acquisition_price
    return None


def fetch_investment_data(year: int, db: Session):
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    tsumitate_amount = db.query(func.sum(NisaTransaction.transaction_amount)).filter(
        NisaTransaction.investment_flag == '1',
        NisaTransaction.transaction_type == 'purchase',
        NisaTransaction.transaction_date.between(start_date, end_date)
    ).scalar()

    seicho_amount = db.query(func.sum(NisaTransaction.transaction_amount)).filter(
        NisaTransaction.investment_flag == '2',
        NisaTransaction.transaction_type == 'purchase',
        NisaTransaction.transaction_date.between(start_date, end_date)
    ).scalar()

    return [
        {"type": "つみたて投資枠", "amount": tsumitate_amount or 0, "total": "1,200,000"},
        {"type": "成長投資枠", "amount": seicho_amount or 0, "total": "2,400,000"}
    ]


def fetch_asset_transition_data(db: Session, user_id: int):
    labels = []
    dataset1 = []
    dataset2 = []

    # 現在の月を基準に12か月分のデータを取得
    today = datetime.now()
    for i in range(12):  # 最新の月を含む12か月分
        # 月単位で遡る処理
        year = today.year
        month = today.month - i

        # 年の境界を超えた場合の補正
        while month <= 0:
            month += 12
            year -= 1

        label = f"{year}/{int(month)}"  # 頭の0を削除
        labels.append(label)

        # 特定のユーザーIDに関連するデータを取得
        sum_appraised_value = db.query(func.sum(NisaHistory.sum_appraised_value)).filter(
            NisaHistory.user_id == user_id,
            extract('year', NisaHistory.nisa_history_update_date) == year,
            extract('month', NisaHistory.nisa_history_update_date) == month
        ).scalar()

        sum_acquisition_price = db.query(func.sum(NisaHistory.sum_acquisition_price)).filter(
            NisaHistory.user_id == user_id,
            extract('year', NisaHistory.nisa_history_update_date) == year,
            extract('month', NisaHistory.nisa_history_update_date) == month
        ).scalar()

        # Noneの場合は0を追加
        dataset1.append(sum_appraised_value or 0)
        dataset2.append(sum_acquisition_price or 0)

    # リストを逆順に並べ替え（古い月から新しい月にする）
    labels.reverse()
    dataset1.reverse()
    dataset2.reverse()

    return {"labels": labels, "dataset1": dataset1, "dataset2": dataset2}


def fetch_fund_data(db: Session):
    funds = db.query(OwnedProduct, Product).join(
        Product, OwnedProduct.product_category_id == Product.product_category_id).all()
    fund_data = []

    for owned_product, product in funds:
        # 最新のtransaction_amountを取得
        latest_transaction = db.query(NisaTransaction).filter(
            NisaTransaction.product_category_id == product.product_category_id,
            NisaTransaction.investment_flag == '1'
        ).order_by(NisaTransaction.transaction_date.desc()).first()

        amount = latest_transaction.transaction_amount if latest_transaction else 0

        # profitLossの計算
        latest_unit_price = db.query(Product.unit_price).filter(
            Product.product_id == product.product_id
        ).order_by(Product.price_update_datetime.desc()).first()

        profit_loss = (owned_product.quantity *
                       latest_unit_price[0]) - owned_product.acquisition_price if latest_unit_price else 0

        fund_data.append({
            "name": product.product_name,
            "amount": amount if latest_transaction else 0,
            "profitLoss": profit_loss
        })

    return fund_data


def get_personal_ranking(db: Session, user_id: int):
    # ユーザーの最古の更新日を取得
    oldest_date = db.query(func.min(NisaHistory.nisa_history_update_date)).filter(
        NisaHistory.user_id == user_id).scalar()

    # 同じ最古の更新日を持つユーザーを取得
    users_with_oldest_date = db.query(NisaHistory.user_id).filter(
        NisaHistory.nisa_history_update_date == oldest_date).all()
    user_ids = [user.user_id for user in users_with_oldest_date]

    # 各ユーザーの最新のsum_appraised_value / sum_acquisition_priceを計算
    rankings = []
    for uid in user_ids:
        latest_record = db.query(NisaHistory).filter(NisaHistory.user_id == uid).order_by(
            NisaHistory.nisa_history_update_date.desc()).first()
        if latest_record and latest_record.sum_acquisition_price > 0:
            ratio = latest_record.sum_appraised_value / latest_record.sum_acquisition_price
            rankings.append((uid, ratio))

    # ランキングをソート
    rankings.sort(key=lambda x: x[1], reverse=True)

    # ユーザーのランキングを見つける
    my_ranking = next((index for index, value in enumerate(
        rankings) if value[0] == user_id), None)

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
    top_10_percent_users = [user[0]
                            for user in personal_ranking["top10PercentUsers"]]

    # 上位10％のユーザーの保有商品を集計
    product_quantities = db.query(
        OwnedProduct.product_category_id,
        func.sum(OwnedProduct.quantity).label('total_quantity')
    ).filter(OwnedProduct.nisa_account_id.in_(
        db.query(NisaAccount.nisa_account_id).filter(
            NisaAccount.user_id.in_(top_10_percent_users))
    )).group_by(OwnedProduct.product_category_id).all()

    # 各商品の価値を計算
    product_values = []
    for product in product_quantities:
        latest_price = db.query(Product.unit_price).filter(Product.product_category_id ==
                                                           product.product_category_id).order_by(Product.price_update_datetime.desc()).first()
        previous_price = db.query(Product.unit_price).filter(Product.product_category_id == product.product_category_id).order_by(
            Product.price_update_datetime.desc()).offset(1).first()
        if latest_price:
            value = product.total_quantity * latest_price[0]
            product_values.append((product.product_category_id, value,
                                  latest_price[0], previous_price[0] if previous_price else 0))

    # 価値で商品をソートし、上位5位を取得
    product_values.sort(key=lambda x: x[1], reverse=True)
    top_5_products = product_values[:5]

    # 商品の詳細を取得
    ranking_data = []
    for product in top_5_products:
        product_details = db.query(Product).filter(
            Product.product_category_id == product[0]).first()
        if product_details:
            price_difference = product[2] - product[3]
            ranking_data.append({
                "rank": top_5_products.index(product) + 1,
                "fundName": product_details.product_name,
                "price": product[2],
                "priceChange": price_difference
            })

    return ranking_data


def calculate_age(birthday):
    today = datetime.today()
    return today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

# nisa_accountを探すコード


def get_nisa_account_ids(user_id: int, db: Session):
    nisa_accounts = db.query(NisaAccount).filter(
        NisaAccount.user_id == user_id).all()
    return [account.nisa_account_id for account in nisa_accounts]


def get_owned_products_by_user_id(user_id: int, db: Session):
    owned_products = db.query(OwnedProduct).filter(
        OwnedProduct.user_id == user_id).all()
    return owned_products


def get_product_ranking(user_id: int, investment_flag: int, age_group: bool, annual_income: bool, family_structure_type: bool, investment_amount: bool, db: Session):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None

    filters = [OwnedProduct.investment_flag == investment_flag]
    if age_group:
        age = calculate_age(user.birthday)
        age_group_filter = f"{age // 10 * 10}代"
        filters.append(User.birthday.between(datetime.today() - timedelta(days=int(
            age_group_filter[:-1]) * 365 + 3650), datetime.today() - timedelta(days=int(age_group_filter[:-1]) * 365)))
    if annual_income:
        filters.append(FamilyStructure.annual_income ==
                       user.family_structures[0].annual_income)
    if family_structure_type:
        filters.append(FamilyStructure.family_structure_type ==
                       user.family_structures[0].family_structure_type)
    if investment_amount:
        latest_transaction = db.query(NisaTransaction).join(NisaAccount).filter(
            NisaAccount.user_id == user_id).order_by(NisaTransaction.transaction_date.desc()).first()
        if latest_transaction:
            filters.append(NisaTransaction.transaction_amount ==
                           latest_transaction.transaction_amount)

    filtered_users = db.query(User).join(
        FamilyStructure, User.user_id == FamilyStructure.user_id).filter(*filters).all()

    product_quantities = {}
    for user in filtered_users:
        owned_products = get_owned_products_by_user_id(user.user_id, db)
        for product in owned_products:
            if product.product_category_id not in product_quantities:
                product_quantities[product.product_category_id] = 0
            product_quantities[product.product_category_id] += product.quantity

    ranking = []
    for product_category_id, quantity in product_quantities.items():
        product = db.query(Product).filter(Product.product_category_id == product_category_id).order_by(
            Product.price_update_datetime.desc()).first()
        if product:
            previous_product = db.query(Product).filter(Product.product_category_id == product_category_id).order_by(
                Product.price_update_datetime.desc()).offset(1).first()
            price_change = product.unit_price - \
                (previous_product.unit_price if previous_product else 0)
            ranking.append({
                "rank": len(ranking) + 1,
                "fundName": product.product_name,
                "price": product.unit_price,
                "priceChange": price_change
            })

    ranking = sorted(ranking, key=lambda x: x["price"], reverse=True)[:5]

    return ranking
