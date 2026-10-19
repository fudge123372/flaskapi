from sqlalchemy import create_engine, text
from models import Payment

engine = create_engine("sqlite:///./flask_duka_api.db")

with engine.begin() as connection:
    connection.execute(text("DROP TABLE IF EXISTS payments"))
    Payment.__table__.create(connection)

print("Payments table recreated with the sale_id foreign key.")