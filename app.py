from flask import Flask, render_template, request, redirect, url_for, flash, session

# If mysqlclient fails to install on PythonAnywhere, PyMySQL can be used:
try:
    import MySQLdb  # try native adapter
except Exception:
    import pymysql
    pymysql.install_as_MySQLdb()
import os
from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import razorpay

app = Flask(__name__)

# Secret key for session & CSRF
app.secret_key = 'supersecretkey'

# ---------- MySQL Configuration ----------
import os

# ✅ Remote DB config
import os

app.config['MYSQL_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('DB_NAME')

import razorpay

client = razorpay.Client(auth=("YOUR_KEY_ID", "YOUR_KEY_SECRET"))

payout = client.payouts.create({
    "account_number": "YOUR_BANK_ACCOUNT_NUMBER",
    "fund_account_id": "fa_xxxxx",  # recipient fund account created in Razorpay
    "amount": 10000,  # in paise (₹100)
    "currency": "INR",
    "mode": "IMPS",  # instant transfer
    "purpose": "payout",
    "queue_if_low_balance": True
})
print(payout)



mysql = MySQL(app)
csrf = CSRFProtect(app)

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")


razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# ---------- LOGIN REQUIRED DECORATOR ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function


from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class OrderForm(FlaskForm):
    fuel_type = StringField('Fuel Type', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Submit')

#-------------------
#-------------------
#----Normal routs---
#-------------------
#-------------------
@app.route('/house')
def house():
    return render_template('home.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/explore')
def explore():
    return render_template('explore.html')

@app.route('/readmore')
def readmore():
    return render_template('readmore.html')

@app.route('/index')
@login_required
def index():
    return render_template('index.html')

@app.route('/orders')
@login_required
def orders():
    return render_template('orders.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

@app.route('/payments')
@login_required
def payments():
    return render_template('payment.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('setting.html')

# ---------- ROUTES ----------

@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')


# ---------- REGISTER ----------
@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    hashed_password = generate_password_hash(password)

    cur = mysql.connection.cursor()
    # Check if user exists
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        flash("Email already registered. Please log in.", "warning")
        cur.close()
        return redirect(url_for('login_page'))

    # Insert new user
    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name, email, hashed_password)
    )
    mysql.connection.commit()
    cur.close()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for('login_page'))


# ---------- LOGIN ----------
import MySQLdb.cursors  # for DictCursor

# ---------- LOGIN ----------
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    # Use DictCursor to fetch rows as dictionaries
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['user_name'] = user['name']  # Store name in session
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))  # ✅ Redirect to dashboard
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('login_page'))

# ---------- DASHBOARD ----------
@app.route('/dashboard')
@login_required
def dashboard():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # DictCursor here too
    cur.execute("SELECT * FROM `order` WHERE user_id = %s", (session['user_id'],))
    orders = cur.fetchall()  # now orders will be list of dictionaries
    cur.close()

    return render_template('dashboard.html', username=session['user_name'], orders=orders)


@app.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():
    if request.method == 'POST':
        fullname = request.form['fullname']
        email = request.form['email']
        address = request.form['address']
        litres = int(request.form['litres'])
        pump = request.form['pump']
        vehicle_number = request.form['vehicle-number']
        fuel_type = request.form['fuel-type']

        # 💰 For testing: 1 litre = ₹2
        amount = litres * 2 * 100  # Razorpay amount in paise

        # ✅ Create Razorpay order
        razorpay_order = razorpay_client.order.create(dict(
            amount=amount,
            currency='INR',
            payment_capture='1'
        ))

        order_id = razorpay_order['id']

        # Temporarily store order info in session
        session['pending_order'] = {
            'fullname': fullname,
            'email': email,
            'address': address,
            'litres': litres,
            'pump': pump,
            'vehicle_number': vehicle_number,
            'fuel_type': fuel_type,
            'amount': amount,
            'razorpay_order_id': order_id
        }

        # Redirect to payment page
        return render_template(
            'payment.html',
            key_id=RAZORPAY_KEY_ID,
            amount=amount,
            order_id=order_id,
            name=fullname,
            email=email
        )

    # On GET, show the form
    return render_template('submit.html')




@app.route('/payment_success', methods=['POST'])
@login_required
def payment_success():
    data = request.form

    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    # ✅ Verify signature
    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        flash("Payment verification failed!", "danger")
        return redirect(url_for('dashboard'))

    # ✅ Insert order details into DB
    order = session.get('pending_order')
    if order:
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO `order`
            (user_id, fullname, email, address, litres, pump, vehicle_number,
             fuel_type, amount, razorpay_order_id, razorpay_payment_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            order['fullname'],
            order['email'],
            order['address'],
            order['litres'],
            order['pump'],
            order['vehicle_number'],
            order['fuel_type'],
            order['amount'] / 100,
            razorpay_order_id,
            razorpay_payment_id
        ))
        mysql.connection.commit()
        cur.close()

        session.pop('pending_order', None)
        flash("Payment successful and order placed!", "success")

    return redirect(url_for('dashboard'))




# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=False)


