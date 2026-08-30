from flask import Flask, render_template, redirect, session, flash, request, url_for
from functools import wraps
from datetime import timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models import User, Farmer, Buyer

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agrilink.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'vivekkali')
app.permanent_session_lifetime = timedelta(hours=24)

db.init_app(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def string_validator(value, field_name="field"):
    """Returns True if valid, otherwise an error message string."""
    if not value or value.strip() == "" or len(value.strip()) < 3:
        return f"Enter a valid {field_name}"
    return True


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'id' not in session:
            flash('Please login first')
            return redirect(url_for('login_user'))
        return view(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------------------------------------------------------------------
# User registration (creates the base account, then routes to the
# role-specific profile form)
# ---------------------------------------------------------------------------

@app.route('/registration_user', methods=['GET', 'POST'])
def registration_user():
    session.permanent = True

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', '').strip().lower()

        # --- validation ---
        checks = [
            string_validator(username, "username"),
            string_validator(email, "email"),
            string_validator(password, "password"),
        ]
        for check in checks:
            if check is not True:
                flash(check)
                return redirect(url_for('registration_user'))

        if role not in ('farmer', 'buyer','other'):
            flash('Select a valid role')
            return redirect(url_for('registration_user'))

        if User.query.filter_by(email=email).first():
            flash('An account with that email already exists')
            return redirect(url_for('login_user'))

        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('Something went wrong, please try again')
            return redirect(url_for('registration_user'))

        # log the new user in immediately
        session['id'] = new_user.id
        session['role'] = new_user.role
        flash('Account created — now complete your profile')

        if role == 'farmer':
            return redirect(url_for('register_farmer'))
        if role =='buyer':
            return redirect(url_for('register_buyer'))
        else:
            return redirect(url_for('dashboard'))

    return render_template('register_user.html')


# ---------------------------------------------------------------------------
# Login (single entry point for both farmers and buyers)
# ---------------------------------------------------------------------------

@app.route('/login_user', methods=['GET', 'POST'])
def login_user():
    session.permanent = True

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid email or password')
            return redirect(url_for('login_user'))

        session['id'] = user.id
        session['role'] = user.role
        flash('Logged in successfully')

        # send them to finish their profile if it's incomplete,
        # otherwise straight to the dashboard
        if user.role == 'farmer' and not Farmer.query.filter_by(user_id=user.id).first():
            return redirect(url_for('register_farmer'))
        if user.role == 'buyer' and not Buyer.query.filter_by(user_id=user.id).first():
            return redirect(url_for('register_buyer'))

        return redirect(url_for('dashboard'))

    return render_template('login_user.html')


# ---------------------------------------------------------------------------
# Farmer profile registration
# ---------------------------------------------------------------------------

@app.route('/register_farmer', methods=['GET', 'POST'])
@login_required
def register_farmer():
    if request.method == 'POST':
        user_id = session['id']

        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        village = request.form.get('village', '').strip()
        taluka = request.form.get('taluka', '').strip()
        district = request.form.get('district', '').strip()
        state = request.form.get('state', '').strip()
        pincode = request.form.get('pincode', '').strip()
        farm_size_unit = request.form.get('farm_size_unit')
        fpo_member = request.form.get('fpo_member') == 'yes'
        fpo_name = request.form.get('fpo_name', '').strip() if fpo_member else None

        # --- validation ---
        checks = [
            string_validator(full_name, "full name"),
            string_validator(taluka, "taluka"),
            string_validator(village, "village"),
            string_validator(state, "state"),
            string_validator(district, "district"),
        ]
        for check in checks:
            if check is not True:
                flash(check)
                return redirect(url_for('register_farmer'))

        if fpo_member and (not fpo_name or len(fpo_name) < 3):
            flash('Enter a valid FPO name')
            return redirect(url_for('register_farmer'))

        if not phone.isdigit() or len(phone) != 10:
            flash('Enter a valid 10-digit phone number')
            return redirect(url_for('register_farmer'))

        if not pincode.isdigit() or len(pincode) != 6:
            flash('Enter a valid 6-digit pincode')
            return redirect(url_for('register_farmer'))

        try:
            farm_size = abs(float(request.form.get('farm_size')))
        except (TypeError, ValueError):
            flash('Enter a valid farm size')
            return redirect(url_for('register_farmer'))

        new_farmer = Farmer(
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            village=village,
            taluka=taluka,
            district=district,
            state=state,
            pincode=pincode,
            farm_size=farm_size,
            farm_size_unit=farm_size_unit,
            fpo_member=fpo_member,
            fpo_name=fpo_name
        )

        try:
            db.session.add(new_farmer)
            db.session.commit()
            flash('Farmer profile created successfully')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('Something went wrong, please try again')
            return redirect(url_for('register_farmer'))

    return render_template('register_farmer.html')


# ---------------------------------------------------------------------------
# Buyer profile registration
# ---------------------------------------------------------------------------

@app.route('/register_buyer', methods=['GET', 'POST'])
@login_required
def register_buyer():
    if request.method == 'POST':
        user_id = session['id']

        company_name = request.form.get('company_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip().lower()
        address = request.form.get('address', '').strip()
        village_city = request.form.get('village_city', '').strip()
        district = request.form.get('district', '').strip()
        state = request.form.get('state', '').strip()
        business_type = request.form.get('business_type', '').strip()

        # --- validation ---
        checks = [
            string_validator(company_name, "company name"),
            string_validator(contact_person, "contact person"),
            string_validator(district, "district"),
            string_validator(state, "state"),
        ]
        for check in checks:
            if check is not True:
                flash(check)
                return redirect(url_for('register_buyer'))

        if not phone.isdigit() or len(phone) != 10:
            flash('Enter a valid 10-digit phone number')
            return redirect(url_for('register_buyer'))

        new_buyer = Buyer(
            user_id=user_id,
            company_name=company_name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address,
            village_city=village_city,
            district=district,
            state=state,
            business_type=business_type
        )

        try:
            db.session.add(new_buyer)
            db.session.commit()
            flash('Buyer profile created successfully')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(e)
            flash('Something went wrong, please try again')
            return redirect(url_for('register_buyer'))

    return render_template('register_buyer.html')


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['id'])
    return render_template('dashboard.html', user=user)


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out')
    return redirect(url_for('home'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
