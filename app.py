import os
import certifi
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
import pymongo
from bson.objectid import ObjectId

load_dotenv()  # read .env


def create_app():
    app = Flask(__name__)

    db = None
    try:
        client = pymongo.MongoClient(
            os.getenv("MONGO_URI"),
            serverSelectionTimeoutMS=5000,
            tlsCAFile=certifi.where(),  # trusted certificate list (fixes CERTIFICATE_VERIFY_FAILED on Mac)
        )
        db = client[os.getenv("MONGO_DBNAME", "job_tracker")]
        client.admin.command("ping")
        print(" * Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)
        print(" * Check MONGO_URI in your .env file")

    # Screen 1: all applications
    @app.route("/")
    def home():
        return render_template("index.html")

    # TODO Screen 2: GET  /applications/<app_id>              -> detail.html
    # TODO Screen 3: GET + POST /applications/new             -> add.html
    # TODO Screen 4: GET + POST /applications/<app_id>/edit   -> edit.html
    # TODO Screen 5: GET + POST /applications/<app_id>/delete -> delete.html
    # TODO Screen 6: GET  /search?q=...                       -> search.html

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
