from sqlalchemy import ForeignKey 
from sqlalchemy import String,Integer,Float
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import date
from sqlalchemy import Date

class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__="users"

    id:Mapped[int]=mapped_column(primary_key=True)
    full_name:Mapped[str]=mapped_column(String(100))
    email:Mapped[str]=mapped_column(String(100))
    password:Mapped[str]=mapped_column(String(200))


class Product(Base):
    __tablename__="products"
    id:Mapped[int]=mapped_column(Integer, primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("user.id"))
    buying_price:Mapped[float]=mapped_column(Float)
    selling_price:Mapped[float]=mapped_column(Float)

class sale(Base):
    __tablename__="sales"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("user_id"))
    total_amount:Mapped[Float]=mapped_column(Float)

class payment(Base):
    __tablename__="payments"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id:Mapped[int]=mapped_column(Integer,ForeignKey("sales.id"))
    date_paid:Mapped[date]=mapped_column(Date)


class purchase(Base):
    __tablename__="purchase"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    Product_id:Mapped[int]=mapped_column(Integer,ForeignKey("products_id"))
    purchase_price:Mapped[Float]=mapped_column(Float)
    date_purchased:Mapped[date]=mapped_column(Date)


class sale_details(Base):
    __tablename__="sales_details"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    product_id:Mapped[int]=mapped_column(Integer,ForeignKey('products_id'))
    sale_id:Mapped[int]=mapped_column(Integer,ForeignKey('sales_id'))
    quantity:Mapped[int]=mapped_column(Float)
    amount:Mapped[int]=mapped_column(Integer) 