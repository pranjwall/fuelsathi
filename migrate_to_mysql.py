import sqlite3
import pymysql
from datetime import datetime

# SQLite connection
sqlite_conn = sqlite3.connect('instance/fuelsathi.db')
sqlite_cursor = sqlite_conn.cursor()

# MySQL connection (update credentials as needed)
mysql_conn = pymysql.connect(
    host='localhost',
    user='root',  # Replace with your MySQL username
    password='Test@123',  # Replace with your MySQL password
    database='fuelsathi'  # Replace with your MySQL database name
)
mysql_cursor = mysql_conn.cursor()

# Create MySQL tables (adjust as needed)
mysql_cursor.execute('''
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
''')

mysql_cursor.execute('''
CREATE TABLE IF NOT EXISTS order_table (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    vehicle_number VARCHAR(20) NOT NULL,
    vehicle_model VARCHAR(50),
    fuel_type VARCHAR(20) NOT NULL,
    order_by VARCHAR(10) NOT NULL,
    fuel_litres FLOAT,
    fuel_cost FLOAT,
    payment_method VARCHAR(20) NOT NULL,
    lat VARCHAR(20),
    lng VARCHAR(20),
    pump_name VARCHAR(100),
    pump_address VARCHAR(200),
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
)
''')

# Migrate users
sqlite_cursor.execute('SELECT * FROM user')
users = sqlite_cursor.fetchall()
for user in users:
    mysql_cursor.execute('''
    INSERT INTO user (id, name, email, password_hash, role, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    name=VALUES(name), password_hash=VALUES(password_hash), role=VALUES(role), updated_at=VALUES(updated_at)
    ''', user)

# Migrate orders
sqlite_cursor.execute('SELECT * FROM "order"')
orders = sqlite_cursor.fetchall()
for order in orders:
    mysql_cursor.execute('''
    INSERT INTO order_table (id, user_id, vehicle_number, vehicle_model, fuel_type, order_by, fuel_litres, fuel_cost, payment_method, lat, lng, pump_name, pump_address, status, created_at, updated_at)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    vehicle_number=VALUES(vehicle_number), fuel_type=VALUES(fuel_type), status=VALUES(status), updated_at=VALUES(updated_at)
    ''', order)

# Commit and close
mysql_conn.commit()
sqlite_conn.close()
mysql_conn.close()

print("Migration completed successfully!")
