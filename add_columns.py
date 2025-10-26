from app import db, app
from sqlalchemy import text

with app.app_context():
    # Add pump_name column
    db.session.execute(text('ALTER TABLE "order" ADD COLUMN pump_name VARCHAR(100)'))
    db.session.commit()
    print("Added pump_name column")

    # Add pump_address column
    db.session.execute(text('ALTER TABLE "order" ADD COLUMN pump_address VARCHAR(200)'))
    db.session.commit()
    print("Added pump_address column")
