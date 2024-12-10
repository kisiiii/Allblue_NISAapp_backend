import csv
from sqlalchemy.orm import sessionmaker
from mymodels import Product,ProductCategory, engine  # モデルとエンジンをインポート
from datetime import datetime  # datetimeモジュールをインポート

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

#オルカン用
# # CSVファイルのパス
# csv_file_path = '253425.csv'

# # CSVファイルを読み込み、データベースに挿入
# with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#     reader = csv.reader(csvfile)
#     product_name = next(reader)[0]  # 最初の行をプロダクト名として取得
#     headers = next(reader)  # 2行目をヘッダーとして取得
#     dict_reader = csv.DictReader(csvfile, fieldnames=headers)
    
#     for row in dict_reader:
#         product = Product(
#             product_name=product_name,
#             price_update_datetime=row['基準日'],
#             unit_price=row['基準価額(円)'],
#             product_category_id=1  # 任意のカテゴリIDを設定
#         )
#         session.add(product)

# # プロダクトカテゴリーIDが存在するか確認し、存在しない場合は追加
# def ensure_category_exists(category_id, category_name):
#     category = session.query(ProductCategory).filter_by(product_category_id=category_id).first()
#     if not category:
#         new_category = ProductCategory(
#             product_category_id=category_id,
#             product_type=category_name  # 適切なカテゴリ名を設定
#         )
#         session.add(new_category)
#         session.commit()

# # カテゴリーID 2と3を確認し、存在しない場合は追加
# ensure_category_exists(2, 'S&P')
# ensure_category_exists(3, 'Nissei')

# #S&P用
# # CSVファイルのパス
# csv_file_path = 'S&P.csv'

# # CSVファイルを読み込み、データベースに挿入
# with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
#     reader = csv.reader(csvfile)
#     product_name = next(reader)[0]  # 最初の行をプロダクト名として取得
#     headers = next(reader)  # 2行目をヘッダーとして取得
#     dict_reader = csv.DictReader(csvfile, fieldnames=headers)
    
#     for row in dict_reader:
#         product = Product(
#             product_name=product_name,
#             price_update_datetime=row['基準日'],
#             unit_price=row['基準価額(円)'],
#             product_category_id=2  # 任意のカテゴリIDを設定
#         )
#         session.add(product)

# # 変更をコミット
# session.commit()

# # データベースからデータを取得
# products = session.query(Product).all()

# # 取得したデータを表示
# for product in products:
#     print(f"ID: {product.product_id}, Name: {product.product_name}, Price: {product.unit_price}, Date: {product.price_update_datetime}")


#ニッセイ用
# CSVファイルのパス
# csv_file_path = 'ニッセイ外国株.csv'

# # CSVファイルを読み込み、データベースに挿入
# with open(csv_file_path, newline='', encoding='utf-8-sig') as csvfile:
#     reader = csv.reader(csvfile)
#     headers = next(reader)  # ヘッダーを取得
#     print(f"ヘッダー: {headers}")  # ヘッダーを表示して確認
#     dict_reader = csv.DictReader(csvfile, fieldnames=headers)
    
#     for row in dict_reader:
#         try:
#             # 日付を適切な形式に変換
#             price_update_datetime = datetime.strptime(row['日付'], '%Y年%m月%d日')
#         except KeyError:
#             print(f"日付の列が見つかりません: {row}")
#             continue
#         except ValueError:
#             print(f"日付の形式が不正です: {row['日付']}")
#             continue
        
#         product = Product(
#             product_name=row['ファンド名'],
#             price_update_datetime=price_update_datetime,  # 日付を適切な形式に変換
#             unit_price=int(row['基準価額']),
#             product_category_id=3  # プロダクトカテゴリーIDを3に設定
#         )
#         session.add(product)

# 変更をコミット
session.commit()

# データベースからデータを取得して表示（確認用）
products = session.query(Product).filter(Product.product_category_id.in_([3])).limit(15).all()

for product in products:
    print(f"ID: {product.product_id}, Name: {product.product_name}, Price: {product.unit_price}, Date: {product.price_update_datetime}, Category ID: {product.product_category_id}")
