from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import razorpay
import pymysql
import pymysql.cursors

app = Flask(__name__)

# Secret key for session & CSRF
app.secret_key = 'supersecretkey'
csrf = CSRFProtect(app)


# ----------------------------------------------------------
#   SSL CERT: Write Aiven CA certificate to a local file
# ----------------------------------------------------------
def create_ca_cert_file():
    ca_cert = os.environ.get("SSL_CA")
    if not ca_cert:
        print("⚠ SSL_CA environment variable missing!")
        return None

    ca_path = "/tmp/aiven_ca.pem"
    with open(ca_path, "w") as f:
        f.write(ca_cert)

    return ca_path


# ----------------------------------------------------------
#   AIVEN MYSQL — PYMYSQL + SSL CONFIG
# ----------------------------------------------------------
def get_db():
    ca_path = create_ca_cert_file()

    return pymysql.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        port=int(os.environ.get("DB_PORT")),
        cursorclass=pymysql.cursors.DictCursor,
        ssl={
            "ca": ca_path,
            "check_hostname": False
        }
    )


# Razorpay
RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET")
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


# ---------- LOGIN REQUIRED DECORATOR ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired

class OrderForm(FlaskForm):
    fuel_type = StringField('Fuel Type', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Submit')


# ------------------- Normal routes -------------------
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

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cur.fetchone()

    if existing_user:
        flash("Email already registered. Please log in.", "warning")
        conn.close()
        return redirect(url_for('login_page'))

    cur.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name, email, hashed_password)
    )

    conn.commit()
    conn.close()

    flash("Registration successful! Please log in.", "success")
    return redirect(url_for('login_page'))


# ---------- LOGIN ----------
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        flash("Login successful!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password.", "danger")
        return redirect(url_for('login_page'))


# ---------- DASHBOARD ----------
@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM `order` WHERE user_id = %s", (session['user_id'],))
    orders = cur.fetchall()

    conn.close()

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

        amount = litres * 2 * 100  # Razorpay amount in paise

        razorpay_order = razorpay_client.order.create(dict(
            amount=amount,
            currency='INR',
            payment_capture='1'
        ))

        order_id = razorpay_order['id']

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

        return render_template(
            'payment.html',
            key_id=RAZORPAY_KEY_ID,
            amount=amount,
            order_id=order_id,
            name=fullname,
            email=email
        )

    return render_template('submit.html')


# ---------- PAYMENT SUCCESS ----------
@app.route('/payment_success', methods=['POST'])
@login_required
def payment_success():
    data = request.form

    razorpay_order_id = data.get('razorpay_order_id')
    razorpay_payment_id = data.get('razorpay_payment_id')
    razorpay_signature = data.get('razorpay_signature')

    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        })
    except razorpay.errors.SignatureVerificationError:
        flash("Payment verification failed!", "danger")
        return redirect(url_for('dashboard'))

    order = session.get('pending_order')
    if order:
        conn = get_db()
        cur = conn.cursor()

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

        conn.commit()
        conn.close()

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
