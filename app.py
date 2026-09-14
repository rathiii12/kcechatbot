from flask import Flask, render_template, request, jsonify
from database import db
from chatbot import get_bot_response

app = Flask(__name__)

# =========================
# DATABASE CONFIGURATION
# =========================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///college.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHAT PAGE
# =========================

@app.route("/chat")
def chat_page():
    return render_template("chat.html")


# =========================
# CHATBOT API
# =========================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "reply": "Please enter a question."
        })

    reply = get_bot_response(user_message)

    return jsonify({
        "reply": reply
    })


# =========================
# DEPARTMENTS PAGE
# =========================

@app.route("/departments")
def departments():
    return render_template("department.html")


# =========================
# DEPARTMENT DETAILS PAGE
# =========================

@app.route("/department-details")
def department_details():
    return render_template("department_details.html")


# =========================
# OTHER PAGES
# =========================

@app.route("/compare")
def compare():
    return render_template("compare.html")


@app.route("/map")
def campus_map():
    return render_template("map.html")


@app.route("/events")
def events():
    return render_template("events.html")


@app.route("/emergency")
def emergency():
    return render_template("emergency.html")


# =========================
# CREATE DATABASE
# =========================

with app.app_context():
    db.create_all()


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)