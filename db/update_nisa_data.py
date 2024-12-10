from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from mymodels import User, Product, ProductCategory, NisaTransaction, OwnedProduct, NisaAccount, NisaHistory
from database import engine

# # ユーザーIDリストと対応するプロダクトカテゴリーID
# user_product_categories = {
#     1111: 1,
#     2222: 2,
#     3333: 3  # 3333はプロダクトカテゴリーID「3」を使用
# }

# # 2年前の月末から現在までの月末の日付リストを生成
# end_date = datetime.now()
# start_date = end_date - timedelta(days=2*365)
# transaction_dates = [start_date + timedelta(days=i) for i in range(0, (end_date - start_date).days) if (start_date + timedelta(days=i)).day == 31]

# # データベースセッションの作成
# session = Session(bind=engine)

# print("Starting transaction processing...")

# for user_id, product_category_id in user_product_categories.items():
#     user = session.query(User).filter(User.user_id == user_id).first()
#     if not user:
#         print(f"User {user_id} not found.")
#         continue
    
#     nisa_account = session.query(NisaAccount).filter(NisaAccount.user_id == user_id).first()
#     if not nisa_account:
#         print(f"NISA account for user {user_id} not found.")
#         continue
    
#     for transaction_date in transaction_dates:
#         product = session.query(Product).filter(Product.product_category_id == product_category_id).first()
#         if not product:
#             print(f"Product for category {product_category_id} not found on {transaction_date}.")
#             continue
        
#         transaction_amount = 30000
#         transaction_quantity = transaction_amount / product.unit_price
        
#         # NisaTransactionの作成
#         nisa_transaction = NisaTransaction(
#             nisa_account_id=nisa_account.nisa_account_id,
#             product_category_id=product_category_id,
#             transaction_type='purchase',
#             transaction_date=transaction_date,
#             transaction_quantity=transaction_quantity,
#             transaction_amount=transaction_amount,
#             investment_flag='1'
#         )
#         session.add(nisa_transaction)
        
#         # OwnedProductの更新または作成
#         owned_product = session.query(OwnedProduct).filter(
#             OwnedProduct.nisa_account_id == nisa_account.nisa_account_id,
#             OwnedProduct.product_category_id == product_category_id
#         ).first()
        
#         if owned_product:
#             owned_product.quantity += transaction_quantity
#             owned_product.acquisition_price += transaction_amount
#         else:
#             owned_product = OwnedProduct(
#                 nisa_account_id=nisa_account.nisa_account_id,
#                 product_category_id=product_category_id,
#                 quantity=transaction_quantity,
#                 acquisition_price=transaction_amount,
#                 investment_flag='1'
#             )
#             session.add(owned_product)

# # NisaHistoryとNisaAccountの更新
# for user_id in user_product_categories.keys():
#     nisa_account = session.query(NisaAccount).filter(NisaAccount.user_id == user_id).first()
#     if not nisa_account:
#         print(f"NISA account for user {user_id} not found.")
#         continue
    
#     owned_products = session.query(OwnedProduct).filter(OwnedProduct.nisa_account_id == nisa_account.nisa_account_id).all()
#     if not owned_products:
#         print(f"No owned products found for NISA account {nisa_account.nisa_account_id}.")
#         continue
    
#     sum_appraised_value = 0
#     sum_acquisition_price = 0
    
#     for owned_product in owned_products:
#         product_category = session.query(ProductCategory).filter(ProductCategory.product_category_id == owned_product.product_category_id).first()
#         if not product_category:
#             print(f"Product category {owned_product.product_category_id} not found.")
#             continue
        
#         latest_product = session.query(Product).filter(Product.product_category_id == product_category.product_category_id).order_by(Product.price_update_datetime.desc()).first()
#         if not latest_product:
#             print(f"Latest product for category {product_category.product_category_id} not found.")
#             continue
        
#         sum_appraised_value += owned_product.quantity * latest_product.unit_price
#         sum_acquisition_price += owned_product.acquisition_price
    
#     nisa_history = NisaHistory(
#         nisa_account_id=nisa_account.nisa_account_id,
#         user_id=user_id,
#         sum_appraised_value=sum_appraised_value,
#         sum_acquisition_price=sum_acquisition_price,
#         nisa_history_update_date=datetime.now().date()
#     )
#     session.add(nisa_history)
    
#     nisa_account.nisa_balance = sum_appraised_value

# print("Committing changes to the database...")
# # 変更をコミット
# session.commit()
# session.close()
# print("Transaction processing completed.")