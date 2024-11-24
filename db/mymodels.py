from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base, engine


class Occupation(Base):  # 職業
    __tablename__ = "occupations"
    occupation_id = Column(Integer, primary_key=True)
    occupation = Column(String(255), nullable=False)

    users = relationship("User", back_populates="occupation")


class User(Base):  # ユーザー
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    occupation_id = Column(Integer, ForeignKey("occupations.occupation_id"))
    last_name = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    birthday = Column(DateTime, nullable=False)
    gender = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(11))
    postal_code = Column(String(7))
    prefecture = Column(String(50), nullable=False)
    city = Column(String(100), nullable=False)
    address_line = Column(String(255), nullable=False)
    registration_datetime = Column(DateTime, nullable=False)
    update_datetime = Column(DateTime, nullable=False)

    occupation = relationship("Occupation", back_populates="users")
    family_structures = relationship("FamilyStructure", back_populates="user")
    nisa_accounts = relationship("NisaAccount", back_populates="user")


class FamilyStructure(Base):  # 家族構成
    __tablename__ = "family_structures"
    family_structure_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    family_relationship = Column(String(50), nullable=False)
    family_birthday = Column(DateTime, nullable=False)
    family_gender = Column(String(50), nullable=False)
    family_annual_income = Column(Integer)
    family_registration_date = Column(DateTime, nullable=False)
    family_update_date = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="family_structures")


class OwnedProduct(Base):  # 所有商品
    __tablename__ = "owned_products"
    owned_product_id = Column(Integer, primary_key=True)
    nisa_account_id = Column(Integer, ForeignKey(
        "nisa_accounts.nisa_account_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    quantity = Column(Float, nullable=False)  # 保有数量
    acquisition_price = Column(Float, nullable=False)  # 取得総額

    nisa_account = relationship("NisaAccount", back_populates="owned_products")
    product = relationship("Product", back_populates="owned_products")


class NisaAccount(Base):  # NISA口座
    __tablename__ = "nisa_accounts"
    nisa_account_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    nisa_account_number = Column(String(9), nullable=False)
    nisa_balance = Column(Float)

    user = relationship("User", back_populates="nisa_accounts")
    transactions = relationship(
        "NisaTransaction", back_populates="nisa_account")
    owned_products = relationship(
        "OwnedProduct", back_populates="nisa_account")


class NisaTransaction(Base):  # NISA取引履歴
    __tablename__ = "nisa_transactions"
    nisa_transaction_id = Column(Integer, primary_key=True)
    nisa_account_id = Column(Integer, ForeignKey(
        "nisa_accounts.nisa_account_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    transaction_type = Column(
        Enum('purchase', 'sale', name='transaction_type'), nullable=False)  # purchaseかsaleで固定
    transaction_date = Column(DateTime, nullable=False)
    transaction_quantity = Column(Float, nullable=False)
    transaction_amount = Column(Float, nullable=False)

    nisa_account = relationship("NisaAccount", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")


class Product(Base):  # 商品
    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    product_category_id = Column(Integer, ForeignKey(
        "product_categories.product_category_id"))
    product_name = Column(String(255), nullable=False)
    unit_price = Column(Float, nullable=False)

    category = relationship("ProductCategory", back_populates="products")
    transactions = relationship("NisaTransaction", back_populates="product")
    owned_products = relationship("OwnedProduct", back_populates="product")


class ProductCategory(Base):  # 商品カテゴリー
    __tablename__ = "product_categories"
    product_category_id = Column(Integer, primary_key=True)
    product_type = Column(String(50), nullable=False)

    products = relationship("Product", back_populates="category")


# テーブルの作成
Base.metadata.create_all(bind=engine)
