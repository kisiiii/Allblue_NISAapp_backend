import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from faker import Faker
import random
from mymodels import User, FamilyStructure, OwnedProduct, NisaAccount, NisaTransaction, NisaHistory, Product, Occupation
from config import DATABASE_URL

# データベース接続の設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 一旦ユーザー①111-3333追加
# ユーザー情報の作成
# users = [
#     {
#         "user_id": 1111,
#         "last_name": "Yamada",
#         "first_name": "Taro",
#         "birthday": datetime(1988, 1, 1),
#         "gender": "Male",
#         "email": "taro.yamada@example.com",
#         "phone_number": "09012345678",
#         "postal_code": "1234567",
#         "prefecture": "Tokyo",
#         "city": "Chiyoda",
#         "address_line": "1-1-1 Chiyoda",
#         "registration_datetime": datetime.now(),
#         "update_datetime": datetime.now(),
#         "occupation_id": 1,  # 既存のoccupation_idを使用
#         "family_structure_type": '3'
#     },
#     {
#         "user_id": 2222,
#         "last_name": "Suzuki",
#         "first_name": "Hanako",
#         "birthday": datetime(1983, 1, 1),
#         "gender": "Female",
#         "email": "hanako.suzuki@example.com",
#         "phone_number": "09087654321",
#         "postal_code": "7654321",
#         "prefecture": "Osaka",
#         "city": "Kita",
#         "address_line": "2-2-2 Kita",
#         "registration_datetime": datetime.now(),
#         "update_datetime": datetime.now(),
#         "occupation_id": 2,  # 既存のoccupation_idを使用
#         "family_structure_type": '3'
#     },
#     {
#         "user_id": 3333,
#         "last_name": "Tanaka",
#         "first_name": "Jiro",
#         "birthday": datetime(1993, 1, 1),
#         "gender": "Male",
#         "email": "jiro.tanaka@example.com",
#         "phone_number": "09011223344",
#         "postal_code": "1122334",
#         "prefecture": "Nagoya",
#         "city": "Naka",
#         "address_line": "3-3-3 Naka",
#         "registration_datetime": datetime.now(),
#         "update_datetime": datetime.now(),
#         "occupation_id": 3,  # 既存のoccupation_idを使用
#         "family_structure_type": '1'
#     }
# ]

# # ユーザー情報をデータベースに挿入
# for user_data in users:
#     user = User(
#         user_id=user_data["user_id"],
#         last_name=user_data["last_name"],
#         first_name=user_data["first_name"],
#         birthday=user_data["birthday"],
#         gender=user_data["gender"],
#         email=user_data["email"],
#         phone_number=user_data["phone_number"],
#         postal_code=user_data["postal_code"],
#         prefecture=user_data["prefecture"],
#         city=user_data["city"],
#         address_line=user_data["address_line"],
#         registration_datetime=user_data["registration_datetime"],
#         update_datetime=user_data["update_datetime"],
#         occupation_id=user_data["occupation_id"]
#     )
#     session.add(user)

#     family_structure = FamilyStructure(
#         user_id=user_data["user_id"],
#         family_structure_type=user_data["family_structure_type"]
#     )
#     session.add(family_structure)

# # 変更をコミット
# session.commit()

# # データベースからデータを取得して確認
# users_in_db = session.query(User).all()
# for user in users_in_db:
#     print(f"ID: {user.user_id}, Name: {user.last_name} {user.first_name}, Birthday: {user.birthday}, Gender: {user.gender}")

# family_structures_in_db = session.query(FamilyStructure).all()
# for family_structure in family_structures_in_db:
#     print(f"User ID: {family_structure.user_id}, Family Structure Type: {family_structure.family_structure_type}")

# # セッションを閉じる
# session.close()

#追加で1人足してみる

# Fakerインスタンスの作成
fake = Faker('ja_JP')

# 既存のユーザーID「1000」の取引を追加する
user_id = 1000

# 既存のユーザーを取得
user = session.query(User).filter_by(user_id=user_id).first()
if not user:
    print(f"User with ID {user_id} does not exist.")
    sys.exit()

# 既存のproductsテーブルの情報を使用
products = session.query(Product).all()

# 既存のNISA口座を取得
existing_nisa_accounts = {account.user_id: account for account in session.query(NisaAccount).all()}

# 既存のowned_product_idを取得
existing_owned_product_ids = {product.owned_product_id for product in session.query(OwnedProduct.owned_product_id).all()}

# 所有商品の生成（既存のユーザーID「1000」）
owned_products = []
if user.user_id not in existing_nisa_accounts:
    nisa_account = NisaAccount(
        nisa_account_id=random.randint(1000, 9999),
        user_id=user.user_id,
        nisa_account_number=fake.bban()[:9],  # nisa_account_numberの長さを修正
        nisa_balance=round(random.uniform(100000, 500000), 2),
        balance_update_datetime=datetime.now(),
        investment_flag='1'
    )
    session.add(nisa_account)
    session.commit()
    existing_nisa_accounts[user.user_id] = nisa_account

for _ in range(2):  # 各ユーザーが2つの商品を購入
    owned_product_id = random.randint(1000, 99999)  # ID範囲を拡大して重複を避ける
    while owned_product_id in existing_owned_product_ids:
        owned_product_id = random.randint(1000, 99999)  # ID範囲を拡大して重複を避ける
    existing_owned_product_ids.add(owned_product_id)

    owned_product = OwnedProduct(
        owned_product_id=owned_product_id,
        nisa_account_id=existing_nisa_accounts[user.user_id].nisa_account_id,
        product_category_id=random.randint(1, 9),
        quantity=0.0,  # 初期値を0に設定
        acquisition_price=0.0,  # 初期値を0に設定
        investment_flag='1',
        user_id=user.user_id
    )
    owned_products.append(owned_product)

# データベースに挿入
session.bulk_save_objects(owned_products)
session.commit()

# NISA取引履歴の生成（既存のユーザーID「1000」）
nisa_transactions = []
nisa_histories = []

# 各ユーザーごとに1年間、2年間、3年間のどれかを選択
years_of_transactions = random.choice([1, 2, 3])
transaction_amount = random.choice([10000, 20000, 30000])

for month in range(years_of_transactions * 12):  # 過去1年間、2年間、3年間毎月取引を行う
    transaction_date = datetime.now() - timedelta(days=30 * month)
    
    for owned_product in [op for op in owned_products if op.user_id == user.user_id]:
        product_category_id = owned_product.product_category_id
        product = next((p for p in products if p.product_category_id == product_category_id), None)
        unit_price = product.unit_price if product else None
        transaction_quantity = transaction_amount / unit_price if unit_price else 0

        # ランダムなnisa_transaction_idを生成し、重複を避ける
        nisa_transaction_id = random.randint(1000, 99999)
        while session.query(NisaTransaction).filter_by(nisa_transaction_id=nisa_transaction_id).first() is not None:
            nisa_transaction_id = random.randint(1000, 99999)

        nisa_transaction = NisaTransaction(
            nisa_transaction_id=nisa_transaction_id,
            nisa_account_id=existing_nisa_accounts[user.user_id].nisa_account_id,
            product_category_id=product_category_id,
            transaction_type='purchase',
            transaction_date=transaction_date,
            transaction_quantity=round(transaction_quantity, 2),
            transaction_amount=transaction_amount,
            investment_flag='1'
        )
        nisa_transactions.append(nisa_transaction)

        # 所有商品の更新
        owned_product.quantity += round(transaction_quantity, 2)
        owned_product.acquisition_price += transaction_amount

        # NISA評価・取得額履歴の更新
        nisa_history_update_date = transaction_date.date()
        sum_appraised_value = sum(
            [p.product.unit_price * p.quantity for p in owned_products if p.user_id == user.user_id and p.product is not None]
        )
        sum_acquisition_price = sum([p.acquisition_price for p in owned_products if p.user_id == user.user_id])

        nisa_history = NisaHistory(
            nisa_history_id=random.randint(1000, 99999),  # ID範囲を拡大して重複を避ける
            nisa_account_id=existing_nisa_accounts[user.user_id].nisa_account_id,
            user_id=user.user_id,
            sum_appraised_value=sum_appraised_value,
            sum_acquisition_price=sum_acquisition_price,
            nisa_history_update_date=nisa_history_update_date
        )
        nisa_histories.append(nisa_history)

# データベースに挿入
session.bulk_save_objects(nisa_transactions)
session.bulk_save_objects(nisa_histories)
session.commit()

print(f"User ID {user.user_id} の取引情報をデータベースに追加しました。")