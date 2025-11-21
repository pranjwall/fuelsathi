from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import pymysql
import pymysql.cursors

app = Flask(__name__)

# Secret key
app.secret_key = 'supersecretkey'
csrf = CSRFProtect(app)

# ----------------------------------------------------------
#     LOCAL MYSQL DATABASE CONNECTION
# ----------------------------------------------------------
def get_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Test@123",
        database="fuelsathi",
        cursorclass=pymysql.cursors.DictCursor
    )

# ---------- LOGIN REQUIRED DECORATOR ----------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated


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

    cur.execute("""
        INSERT INTO users (name, email, password_hash)
        VALUES (%s, %s, %s)
    """, (name, email, hashed_password))

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


# ---------- SUBMIT ORDER (NO PAYMENT) ----------
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

        amount = litres * 2   # simple amount calculation, no payment

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO `order`
            (user_id, fullname, email, address, litres, pump, vehicle_number,
             fuel_type, amount)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            session['user_id'],
            fullname,
            email,
            address,
            litres,
            pump,
            vehicle_number,
            fuel_type,
            amount
        ))

        conn.commit()
        conn.close()

        flash("Order placed successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('submit.html')


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login_page'))


if __name__ == '__main__':
    app.run(debug=True)
