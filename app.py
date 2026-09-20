from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import db
from chatbot import get_bot_response, start_background_index
import college_data as cd

app = Flask(__name__)

# =========================
# DATABASE CONFIGURATION
# =========================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///college.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# =========================
# SIDEBAR NAVIGATION
# (key, label, icon, endpoint)
# =========================

NAV = [
    ("chat", "AI Chat", "💬", "chat_page"),
    ("courses", "Courses", "🎓", "courses"),
    ("departments", "Departments", "🏛️", "departments"),
    ("compare", "Compare Departments", "⚖️", "compare"),
    ("map", "Campus Map", "📍", "campus_map"),
    ("events", "Events", "🗓️", "events"),
    ("emergency", "Emergency", "🚨", "emergency"),
]


@app.context_processor
def inject_nav():
    return {"nav": NAV}


# =========================
# HOME PAGE (landing - unchanged)
# =========================

@app.route("/")
def home():
    return render_template("index.html")


# =========================
# CHAT PAGE + API
# =========================

@app.route("/chat")
def chat_page():
    # /chat?role=student|faculty|guest  (comes from the landing page buttons)
    role_key = request.args.get("role", "")
    role = cd.ROLES.get(role_key)
    return render_template(
        "chat.html",
        role_key=role_key if role else "",
        welcome=role["welcome"] if role else "",
        chips=role["chips"] if role else cd.DEFAULT_CHIPS,
    )


@app.route("/chat", methods=["POST"])
def chat():

    payload = request.get_json(silent=True) or {}

    user_message = payload.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a question."})

    history = payload.get("history")

    return jsonify({"reply": get_bot_response(user_message, history)})


# =========================
# COURSES
# =========================

@app.route("/courses")
def courses():
    return render_template("courses.html", programmes=cd.PROGRAMMES)


# =========================
# DEPARTMENTS  (/departments?d=cse)
# =========================

@app.route("/departments")
def departments():
    selected = cd.BY_SLUG.get(request.args.get("d", ""), cd.BY_SLUG["cse"])
    return render_template("department.html", programmes=cd.PROGRAMMES, sel=selected)


# old link kept working
@app.route("/department-details")
def department_details():
    return redirect(url_for("departments", d=request.args.get("d", "cse")))


# =========================
# COMPARE  (/compare?a=cse&b=aids)
# =========================

@app.route("/compare")
def compare():
    a = cd.BY_SLUG.get(request.args.get("a", ""), cd.BY_SLUG["cse"])
    b = cd.BY_SLUG.get(request.args.get("b", ""), cd.BY_SLUG["aids"])
    return render_template("compare.html", programmes=cd.PROGRAMMES, a=a, b=b)


# =========================
# OTHER PAGES
# =========================

@app.route("/map")
def campus_map():
    return render_template("map.html", buildings=cd.BUILDINGS)


@app.route("/events")
def events():
    return render_template("events.html", events=cd.EVENTS)


@app.route("/emergency")
def emergency():
    return render_template("emergency.html", numbers=cd.EMERGENCY)


# =========================
# CREATE DATABASE
# =========================

with app.app_context():
    db.create_all()


# read the whole college website in the background (cached for 24 hours)
start_background_index()


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":
    app.run(debug=True)