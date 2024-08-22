from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL configurations
app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = "root@123"
app.config['MYSQL_DB'] = "flask_db"

mysql = MySQL(app)
login_manage = LoginManager()
login_manage.init_app(app)
login_manage.login_view = 'login'  # Redirect unauthorized users to the login page

# User loader function
@login_manage.user_loader
def load_user(user_id):
    return User.get(user_id)

class User(UserMixin):
    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email
    
    @staticmethod
    def get(user_id):
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, name, email FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            return User(user_id, result[1], result[2])
        return None

@app.route('/')
def indev():
    return "home page"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  # Get the password from the form

        # Fetch user data from the database
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT id, name, email, password FROM users WHERE email = %s', (email,))
        user_data = cursor.fetchone()
        cursor.close()

        # Simple comparison of the entered password with the stored password
        if user_data and user_data[3] == password:
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Login failed. Check your email and password.", 401
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])                                                                                                                                                                                                                                                                                                                                                                                                  
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']

            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
            mysql.connection.commit()
            cursor.close()

            return redirect(url_for('login'))
        except Exception as e:
            print(f"An error occurred: {e}")
            return "An internal error occurred. Please try again later.", 500

    return render_template('register.html')

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
