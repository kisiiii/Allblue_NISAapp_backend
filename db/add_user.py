import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from mymodels import User, FamilyStructure
from config import DATABASE_URL

# データベース接続の設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

#一旦ユーザー①111-3333追加
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