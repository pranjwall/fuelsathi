from flask import Flask, render_template, request, redirect, url_for, flash, session

# If mysqlclient fails to install on PythonAnywhere, PyMySQL can be used:
try:
    import MySQLdb  # try native adapter
except Exception:
    import pymysql
    pymysql.install_as_MySQLdb()


from flask_mysqldb import MySQL
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps


app = Flask(__name__)

# Secret key for session & CSRF
app.secret_key = 'supersecretkey'

# ---------- MySQL Configuration ----------
app.config['MYSQL_HOST'] = 'PranjwalPadalkar.mysql.pythonanywhere-services.com'
app.config['MYSQL_USER'] = 'PranjwalPadalkar'
app.config['MYSQL_PASSWORD'] = 'Test@123'
app.config['MYSQL_DB'] = 'PranjwalPadalkar$fuelsathi'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
csrf = CSRFProtect(app)

# ---------- LOGIN REQUIRED DECORATOR ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function




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
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
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
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM `order` WHERE user_id = %s", (session['user_id'],))
    orders = cur.fetchall()
    cur.close()

    return render_template('dashboard.html', username=session['user_name'], orders=orders)


#--------------SUBMIT----------
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    if request.method == 'POST':
        # Retrieve form data for new order
        fuel_type = request.form['fuel_type']
        quantity = request.form['quantity']

        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO `order` (user_id, fuel_type, quantity) VALUES (%s, %s, %s)",
            (session['user_id'], fuel_type, quantity)
        )
        mysql.connection.commit()
        cur.close()

        flash("Order submitted successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('submit.html')  # You’ll create a form template



# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login_page'))

if __name__ == '__main__':
    app.run(debug=False)


