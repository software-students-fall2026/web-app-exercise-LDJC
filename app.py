import os
import certifi
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from bson.objectid import ObjectId

load_dotenv() 


def create_app():
    app = Flask(__name__)

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

    @app.route("/")
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
    
    @app.route("/search")
    def search():
        return render_template("search.html")


    return app

app = create_app()
 
if __name__ == "__main__":
    app.run(debug=True)
