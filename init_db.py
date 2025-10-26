import os
from flask_mysqldb import MySQL
from flask import Flask

app = Flask(__name__)

# Use environment variables with defaults (for local testing)
app.config['MYSQL_HOST'] = os.environ.get('DB_HOST', 'sql12.freesqldatabase.com')
app.config['MYSQL_USER'] = os.environ.get('DB_USER', 'sql12804616')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD', '9ffpKt9ji4')
app.config['MYSQL_DB'] = os.environ.get('DB_NAME', 'sql12804616')

mysql = MySQL(app)

with app.app_context():
    cur = mysql.connection.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS `order` (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        fuel_type VARCHAR(50) NOT NULL,
        quantity INT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    mysql.connection.commit()
    cur.close()
    print("Tables created successfully!")
