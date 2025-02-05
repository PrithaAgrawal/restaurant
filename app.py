from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash  # For password security
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://pritha:newpassword@localhost/user_info'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Reservation Model
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False)
    reservation_time = db.Column(db.Time, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='reservations', lazy=True)

    def __repr__(self):
        return f'<Reservation {self.id} for {self.name}>'

@app.route('/')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    else:
        return redirect(url_for('login'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):  # Validate hashed password
            session['user_id'] = user.id
            flash('Login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please log in.', 'danger')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password)  # Hashing password
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        session['user_id'] = new_user.id
        flash('Signup successful!', 'success')
        return redirect(url_for('home'))

    return render_template('signup.html')

@app.errorhandler(404)
def page_not_found(e):
    """Render a custom 404 error page."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    """Render a custom 500 error page."""
    return render_template('500.html'), 500

@app.route('/reservations')
def reservations():
    return render_template('reservations.html')

@app.route('/submit_reservation', methods=['POST'])
def submit_reservation():
    name = request.form['name']
    reservation_date = datetime.strptime(request.form['date'], "%Y-%m-%d").date()  # Convert to date
    reservation_time = datetime.strptime(request.form['time'], "%H:%M").time()  # Convert to time

    user_id = session.get('user_id')

    if user_id:
        new_reservation = Reservation(
            name=name,
            reservation_date=reservation_date,
            reservation_time=reservation_time,
            user_id=user_id
        )
        
        db.session.add(new_reservation)
        db.session.commit()

        flash('Reservation submitted successfully!', 'success')
    else:
        flash('You must be logged in to make a reservation.', 'danger')

    return redirect(url_for('home'))

@app.route('/location')
def location():
    return render_template('location.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  
    app.run(debug=True)
