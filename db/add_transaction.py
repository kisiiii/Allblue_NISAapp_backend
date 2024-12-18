import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from mymodels import User, FamilyStructure, OwnedProduct, NisaAccount, NisaTransaction, NisaHistory, Product, Occupation
from config import DATABASE_URL
import random

# データベース接続の設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# ユーザーID「1001」でテスト
# ユーザーIDとプロダクトカテゴリーIDの設定
# user_id = 1001
# product_category_ids = [4, 9]
# transaction_amount = 30000

# # 初期設定
# end_date = datetime.now()
# start_date = end_date - timedelta(days=2*365)
# current_date = start_date
# sum_acquisition_price = 0

# while current_date <= end_date:
#     # 月末の日付を設定
#     last_day_of_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
    
#     for product_category_id in product_category_ids:
#         # price_update_datetime が transaction_date に最も近い unit_price を取得
#         price_date = last_day_of_month.date()
#         unit_price = session.query(Product.unit_price).filter(
#             Product.product_category_id == product_category_id,
#             Product.price_update_datetime <= price_date
#         ).order_by(Product.price_update_datetime.desc()).first()
        
#         if not unit_price:
#             # 該当する日付がない場合、前の最も近い日付の価格を取得
#             unit_price = session.query(Product.unit_price).filter(
#                 Product.product_category_id == product_category_id,
#                 Product.price_update_datetime < price_date
#             ).order_by(Product.price_update_datetime.desc()).first()
        
#         if unit_price:
#             # transaction_quantity を計算 (transaction_amount ÷ unit_price)
#             transaction_quantity = transaction_amount / unit_price[0]
            
#             # nisa_account を取得または作成
#             nisa_account = session.query(NisaAccount).filter(NisaAccount.user_id == user_id).first()
#             if not nisa_account:
#                 nisa_account = NisaAccount(
#                     user_id=user_id,
#                     nisa_account_number=str(random.randint(100000000, 999999999)),
#                     investment_flag='1'  # つみたて投資枠
#                 )
#                 session.add(nisa_account)
#                 session.commit()
            
#             # nisa_transactions テーブルにデータを追加
#             nisa_transaction_entry = NisaTransaction(
#                 nisa_account_id=nisa_account.nisa_account_id,
#                 product_category_id=product_category_id,
#                 transaction_type='purchase',
#                 transaction_date=last_day_of_month,
#                 transaction_quantity=transaction_quantity,
#                 transaction_amount=transaction_amount,
#                 investment_flag='1'  # つみたて投資枠
#             )
#             session.add(nisa_transaction_entry)
#             session.commit()
            
#             # owned_products テーブルを更新
#             owned_product = session.query(OwnedProduct).filter(
#                 OwnedProduct.user_id == user_id,
#                 OwnedProduct.product_category_id == product_category_id
#             ).first()
            
#             if owned_product:
#                 owned_product.quantity += transaction_quantity
#                 owned_product.acquisition_price += transaction_amount
#             else:
#                 owned_product = OwnedProduct(
#                     user_id=user_id,
#                     product_category_id=product_category_id,
#                     quantity=transaction_quantity,
#                     acquisition_price=transaction_amount,
#                     nisa_account_id=nisa_transaction_entry.nisa_account_id
#                 )
#                 session.add(owned_product)
#             session.commit()
    
#     # nisa_accounts テーブルを更新
#     nisa_balance = 0
#     for product_category_id in product_category_ids:
#         owned_product = session.query(OwnedProduct).filter(
#             OwnedProduct.user_id == user_id,
#             OwnedProduct.product_category_id == product_category_id
#         ).first()
#         if owned_product:
#             unit_price = session.query(Product.unit_price).filter(
#                 Product.product_category_id == product_category_id,
#                 Product.price_update_datetime <= last_day_of_month.date()
#             ).order_by(Product.price_update_datetime.desc()).first()
#             if unit_price:
#                 nisa_balance += owned_product.quantity * unit_price[0]
    
#     nisa_account.nisa_balance = nisa_balance
#     nisa_account.balance_update_datetime = last_day_of_month
#     session.commit()
    
#     # nisa_history テーブルを更新
#     sum_acquisition_price += 60000
#     nisa_history_entry = NisaHistory(
#         nisa_account_id=nisa_account.nisa_account_id,
#         user_id=user_id,
#         sum_appraised_value=nisa_balance,
#         sum_acquisition_price=sum_acquisition_price,
#         nisa_history_update_date=last_day_of_month.date()
#     )
#     session.add(nisa_history_entry)
#     session.commit()
    
#     # 次の月に進む
#     current_date += timedelta(days=32)
#     current_date = current_date.replace(day=1)

# session.close()

#ユーザーID「1111」再登録と「1002」「1003」「1004」「1005」「1006」「1007」「1008」「1009」「1010」追加
# ユーザーIDとプロダクトカテゴリーIDの設定
# user_product_categories = {
#     1006: [1, 10],
#     1007: [2, 9],
#     1008: [3, 8],
#     1009: [4, 7],
#     1010: [5, 6]
# }
# transaction_amount = 20000

# # 初期設定
# end_date = datetime.now()
# start_date = end_date - timedelta(days=2*365)

# for user_id, product_category_ids in user_product_categories.items():
#     current_date = start_date
#     sum_acquisition_price = 0

#     while current_date <= end_date:
#         # 月末の日付を設定
#         last_day_of_month = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        
#         for product_category_id in product_category_ids:
#             # price_update_datetime が transaction_date に最も近い unit_price を取得
#             price_date = last_day_of_month.date()
#             unit_price = session.query(Product.unit_price).filter(
#                 Product.product_category_id == product_category_id,
#                 Product.price_update_datetime <= price_date
#             ).order_by(Product.price_update_datetime.desc()).first()
            
#             if not unit_price:
#                 # 該当する日付がない場合、前の最も近い日付の価格を取得
#                 unit_price = session.query(Product.unit_price).filter(
#                     Product.product_category_id == product_category_id,
#                     Product.price_update_datetime < price_date
#                 ).order_by(Product.price_update_datetime.desc()).first()
            
#             if unit_price:
#                 # transaction_quantity を計算 (transaction_amount ÷ unit_price)
#                 transaction_quantity = transaction_amount / unit_price[0]
                
#                 # nisa_account を取得または作成
#                 nisa_account = session.query(NisaAccount).filter(NisaAccount.user_id == user_id).first()
#                 if not nisa_account:
#                     nisa_account = NisaAccount(
#                         user_id=user_id,
#                         nisa_account_number=str(random.randint(100000000, 999999999)),
#                         investment_flag='1'  # つみたて投資枠
#                     )
#                     session.add(nisa_account)
#                     session.commit()
                
#                 # nisa_transactions テーブルにデータを追加
#                 nisa_transaction_entry = NisaTransaction(
#                     nisa_account_id=nisa_account.nisa_account_id,
#                     product_category_id=product_category_id,
#                     transaction_type='purchase',
#                     transaction_date=last_day_of_month,
#                     transaction_quantity=transaction_quantity,
#                     transaction_amount=transaction_amount,
#                     investment_flag='1'  # つみたて投資枠
#                 )
#                 session.add(nisa_transaction_entry)
#                 session.commit()
                
#                 # owned_products テーブルを更新
#                 owned_product = session.query(OwnedProduct).filter(
#                     OwnedProduct.user_id == user_id,
#                     OwnedProduct.product_category_id == product_category_id
#                 ).first()
                
#                 if owned_product:
#                     owned_product.quantity += transaction_quantity
#                     owned_product.acquisition_price += transaction_amount
#                 else:
#                     owned_product = OwnedProduct(
#                         user_id=user_id,
#                         product_category_id=product_category_id,
#                         quantity=transaction_quantity,
#                         acquisition_price=transaction_amount,
#                         nisa_account_id=nisa_transaction_entry.nisa_account_id
#                     )
#                     session.add(owned_product)
#                 session.commit()
        
#         # nisa_accounts テーブルを更新
#         nisa_balance = 0
#         for product_category_id in product_category_ids:
#             owned_product = session.query(OwnedProduct).filter(
#                 OwnedProduct.user_id == user_id,
#                 OwnedProduct.product_category_id == product_category_id
#             ).first()
#             if owned_product:
#                 unit_price = session.query(Product.unit_price).filter(
#                     Product.product_category_id == product_category_id,
#                     Product.price_update_datetime <= last_day_of_month.date()
#                 ).order_by(Product.price_update_datetime.desc()).first()
#                 if unit_price:
#                     nisa_balance += owned_product.quantity * unit_price[0]
        
#         nisa_account.nisa_balance = nisa_balance
#         nisa_account.balance_update_datetime = last_day_of_month
#         session.commit()
        
#         # nisa_history テーブルを更新
#         sum_acquisition_price += 60000
#         nisa_history_entry = NisaHistory(
#             nisa_account_id=nisa_account.nisa_account_id,
#             user_id=user_id,
#             sum_appraised_value=nisa_balance,
#             sum_acquisition_price=sum_acquisition_price,
#             nisa_history_update_date=last_day_of_month.date()
#         )
#         session.add(nisa_history_entry)
#         session.commit()
        
#         # 次の月に進む
#         current_date += timedelta(days=32)
#         current_date = current_date.replace(day=1)

# session.close()