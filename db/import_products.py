import csv
from sqlalchemy.orm import sessionmaker
from .mymodels import Product, engine  # モデルとエンジンをインポート

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

# CSVファイルのパス
csv_file_path = '253425.csv'

# CSVファイルを読み込み、データベースに挿入
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        product = Product(
            product_name=row['ｅＭＡＸＩＳ Ｓｌｉｍ 全世界株式（オール・カントリー）'],
            price_update_datetime=row['基準日'],
            unit_price=row['基準価額(円)'],
            product_category_id=1  # 任意のカテゴリIDを設定
        )
        session.add(product)

# 変更をコミット
session.commit()

# データベースからデータを取得
products = session.query(Product).all()

# 取得したデータを表示
for product in products:
    print(f"ID: {product.product_id}, Name: {product.product_name}, Price: {product.unit_price}, Date: {product.price_update_datetime}")