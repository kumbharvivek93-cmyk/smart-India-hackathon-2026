import os
import re
import secrets
from datetime import timedelta
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models import Buyer, Farmer, User

app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///agrilink.sqlite3",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
)
db.init_app(app)

ALLOWED_ROLES = {"farmer", "buyer"}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def valid_text(value, field_name, minimum_length=2):
    return None if len(value.strip()) >= minimum_length else f"Enter a valid {field_name}."


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login_user"))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    user = db.session.get(User, session.get("user_id"))
    if user is None:
        session.clear()
    return user


def profile_redirect(user):
    if user.role == "farmer" and Farmer.query.filter_by(user_id=user.id).first() is None:
        return redirect(url_for("register_farmer"))
    if user.role == "buyer" and Buyer.query.filter_by(user_id=user.id).first() is None:
        return redirect(url_for("register_buyer"))
    return redirect(url_for("dashboard"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/registration_user", methods=["GET", "POST"])
def registration_user():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "").strip().lower()
        error = valid_text(username, "username")
        if error:
            flash(error)
        elif not EMAIL_PATTERN.match(email):
            flash("Enter a valid email address.")
        elif len(password) < 6:
            flash("Password must be at least 6 characters.")
        elif role not in ALLOWED_ROLES:
            flash("Select either Farmer or Buyer.")
        elif User.query.filter_by(email=email).first():
            flash("An account with that email already exists. Please log in.")
            return redirect(url_for("login_user"))
        else:
            user = User(username=username, email=email, password_hash=generate_password_hash(password), role=role)
            try:
                db.session.add(user)
                db.session.commit()
            except Exception as error:
                db.session.rollback()
                app.logger.exception("Could not create user: %s", error)
                flash("Could not create your account. Please try again.")
            else:
                session.clear()
                session["user_id"] = user.id
                session["role"] = user.role
                session.permanent = True
                flash("Account created. Please complete your profile.")
                return profile_redirect(user)
        return redirect(url_for("registration_user"))
    return render_template("register_user.html")


@app.route("/login_user", methods=["GET", "POST"])
def login_user():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.")
            return redirect(url_for("login_user"))
        if not user.is_active or user.role not in ALLOWED_ROLES:
            flash("This account cannot log in.")
            return redirect(url_for("login_user"))
        session.clear()
        session["user_id"] = user.id
        session["role"] = user.role
        session.permanent = True
        flash("Logged in successfully.")
        return profile_redirect(user)
    return render_template("login_user.html")


def enforce_profile_role(role, profile_model):
    user = current_user()
    if user is None:
        flash("Please login again.")
        return None, redirect(url_for("login_user"))
    if user.role != role:
        flash("Unauthorized access.")
        return None, redirect(url_for("dashboard"))
    if profile_model.query.filter_by(user_id=user.id).first():
        return None, redirect(url_for("dashboard"))
    return user, None


@app.route("/register_farmer", methods=["GET", "POST"])
@login_required
def register_farmer():
    user, response = enforce_profile_role("farmer", Farmer)
    if response:
        return response
    if request.method == "POST":
        data = {name: request.form.get(name, "").strip() for name in ("full_name", "phone", "village", "taluka", "district", "state", "pincode", "farm_size_unit")}
        fpo_choice = request.form.get("fpo_member")
        fpo_member = fpo_choice == "yes"
        fpo_name = request.form.get("fpo_name", "").strip() if fpo_member else None
        required = (("full_name", "full name"), ("village", "village"), ("taluka", "taluka"), ("district", "district"), ("state", "state"))
        error = next((valid_text(data[key], label) for key, label in required if valid_text(data[key], label)), None)
        if error:
            flash(error)
        elif not data["phone"].isdigit() or len(data["phone"]) != 10:
            flash("Enter a valid 10-digit phone number.")
        elif not data["pincode"].isdigit() or len(data["pincode"]) != 6:
            flash("Enter a valid 6-digit pincode.")
        elif fpo_choice not in {"yes", "no"}:
            flash("Choose whether you are an FPO member.")
        elif data["farm_size_unit"] not in {"acre", "hectare", "gunta", "sqft", "sq_meter"}:
            flash("Select a valid farm-size unit.")
        elif fpo_member and valid_text(fpo_name, "FPO name"):
            flash(valid_text(fpo_name, "FPO name"))
        else:
            try:
                farm_size = float(request.form.get("farm_size", ""))
                if farm_size <= 0:
                    raise ValueError
            except ValueError:
                flash("Enter a farm size greater than zero.")
            else:
                farmer = Farmer(user_id=user.id, farm_size=farm_size, fpo_member=fpo_member, fpo_name=fpo_name, **data)
                try:
                    db.session.add(farmer)
                    db.session.commit()
                except Exception as error:
                    db.session.rollback()
                    app.logger.exception("Could not create farmer profile: %s", error)
                    flash("Could not save your profile. Please try again.")
                else:
                    flash("Farmer profile created successfully.")
                    return redirect(url_for("dashboard"))
        return redirect(url_for("register_farmer"))
    return render_template("register_farmer.html")


@app.route("/register_buyer", methods=["GET", "POST"])
@login_required
def register_buyer():
    user, response = enforce_profile_role("buyer", Buyer)
    if response:
        return response
    if request.method == "POST":
        data = {name: request.form.get(name, "").strip() for name in ("company_name", "contact_person", "phone", "email", "address", "village_city", "district", "state", "business_type")}
        data["email"] = data["email"].lower()
        required = (("company_name", "company name"), ("contact_person", "contact person"), ("district", "district"), ("state", "state"), ("business_type", "business type"))
        error = next((valid_text(data[key], label) for key, label in required if valid_text(data[key], label)), None)
        if error:
            flash(error)
        elif not data["phone"].isdigit() or len(data["phone"]) != 10:
            flash("Enter a valid 10-digit phone number.")
        elif not EMAIL_PATTERN.match(data["email"]):
            flash("Enter a valid business email address.")
        else:
            buyer = Buyer(user_id=user.id, **data)
            try:
                db.session.add(buyer)
                db.session.commit()
            except Exception as error:
                db.session.rollback()
                app.logger.exception("Could not create buyer profile: %s", error)
                flash("Could not save your profile. Please try again.")
            else:
                flash("Buyer profile created successfully.")
                return redirect(url_for("dashboard"))
        return redirect(url_for("register_buyer"))
    return render_template("register_buyer.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    if user is None:
        flash("Please login again.")
        return redirect(url_for("login_user"))
    profile = Farmer.query.filter_by(user_id=user.id).first() if user.role == "farmer" else Buyer.query.filter_by(user_id=user.id).first()
    if profile is None:
        return profile_redirect(user)
    return render_template("dashboard.html", user=user, role=user.role, profile=profile)


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("home"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
