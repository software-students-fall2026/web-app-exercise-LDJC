import os
import re
import certifi
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

import pymongo
from bson.objectid import ObjectId

load_dotenv() 
class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc["_id"])
        self.username = user_doc["username"]

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    login_manager = LoginManager(app)
    login_manager.login_view = "login"
    
    db = None
    try:
        client = pymongo.MongoClient(
            os.getenv("MONGO_URI"),
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where(),  
        )
        db = client[os.getenv("MONGO_DBNAME", "job_tracker")]
        client.admin.command("ping")
        print(" * Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)
        print(" * Check MONGO_URI in your .env file")

    @login_manager.user_loader
    def load_user(user_id):
        if db is None:
            return None
        try:
            user_doc = db.users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None
        return User(user_doc) if user_doc else None

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("home"))

        error = None
        if request.method == "POST":
            username = request.form.get("username", "").strip().lower()
            password = request.form.get("password", "")

            if db is None:
                return "Database connection unavailable", 503

            if not username or len(password) < 6:
                error = "Enter a username and a password of at least 6 characters."
            elif db.users.find_one({"username": username}):
                error = "That username is already taken."
            else:
                result = db.users.insert_one({
                    "username": username,
                    "password_hash": generate_password_hash(password),
                })
                login_user(User({"_id": result.inserted_id, "username": username}))
                return redirect(url_for("home"))

        return render_template("register.html", error=error)
    
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("home"))

        error = None
        if request.method == "POST":
            username = request.form.get("username", "").strip().lower()
            password = request.form.get("password", "")

            if db is None:
                return "Database connection unavailable", 503

            user_doc = db.users.find_one({"username": username})
            if user_doc and check_password_hash(user_doc["password_hash"], password):
                login_user(User(user_doc))
                return redirect(url_for("home"))

            error = "Wrong username or password."

        return render_template("login.html", error=error)

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.route("/")
    @login_required
    def home():
        applications = []

        if db is not None:
            applications = list(db.applications.find())

            # Sort applications by deadline
            def get_deadline(application):
                if application.get("application_deadline"):
                    return application["application_deadline"]
                else:
                    return "9999-12-31"

            applications.sort(key=get_deadline, reverse = True)
        return render_template("index.html", applications=applications)
    
    @app.route("/applications/<app_id>")
    def application_detail(app_id):

        if db is None:
            return "Database connection unavailable", 503

        try:
            application = db.applications.find_one({"_id": ObjectId(app_id)})
        except Exception:
            application = None

        if application is None:
            return "Application not found", 404

        return render_template("detail.html", application=application)
    
    
    @app.route("/applications/new", methods=["GET", "POST"])
    def add_application():

        if request.method == "POST":

            company = request.form.get("company", "").strip()
            position = request.form.get("position", "").strip()
            status = request.form.get("status", "Wishlist")
            date_applied = request.form.get("date_applied", "")
            application_deadline = request.form.get(
                "application_deadline", ""
            )
            job_url = request.form.get("job_url", "").strip()
            notes = request.form.get("notes", "").strip()

            if not company or not position:
                return "Company and position are required", 400

            new_application = {
                "company": company,
                "position": position,
                "status": status,
                "date_applied": date_applied,
                "application_deadline": application_deadline,
                "job_url": job_url,
                "notes": notes
            }

            if db is None:
                return "Database connection unavailable", 503

            db.applications.insert_one(new_application)

            return redirect(url_for("home"))

        return render_template("add.html")

    @app.route("/search")
    def search():
        query = request.args.get("query", "").strip()
        status = request.args.get("status", "")
        statuses = ["Wishlist", "Applied", "Interview", "Offer", "Rejected"]
        results = []

        if (query or status) and db is not None:
            filters = {}
            if query:
                pattern = {"$regex": re.escape(query), "$options": "i"}
                filters["$or"] = [{"company": pattern}, {"position": pattern}]
            if status:
                filters["status"] = status
            results = list(db.applications.find(filters))

        return render_template("search.html", query=query, status=status, statuses=statuses, results=results)



    @app.route("/applications/<app_id>/edit", methods=["GET", "POST"])
    def edit_application(app_id):

        if db is None:
            return "Database connection unavailable", 503

        try:
            application = db.applications.find_one({"_id": ObjectId(app_id)})
        except Exception:
            application = None

        if application is None:
            return "Application not found", 404

        if request.method == "POST":

            company = request.form.get("company", "").strip()
            position = request.form.get("position", "").strip()

            if not company or not position:
                return "Company and position are required", 400

            updated_fields = {
                "company": company,
                "position": position,
                "status": request.form.get("status", "Wishlist"),
                "date_applied": request.form.get("date_applied", ""),
                "application_deadline": request.form.get("application_deadline", ""),
                "job_url": request.form.get("job_url", "").strip(),
                "notes": request.form.get("notes", "").strip(),
            }

            db.applications.update_one(
                {"_id": application["_id"]},
                {"$set": updated_fields},
            )

            return redirect(url_for("application_detail", app_id=app_id))

        return render_template("edit.html",application=application)

    return app

app = create_app()
 
if __name__ == "__main__":
    app.run(debug=True)
