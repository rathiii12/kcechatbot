"""Single source of truth for the static pages (courses, departments, compare, map, events, emergency).
Programme text comes from your seed.py. Edit BUILDINGS / EVENTS with real details."""

PROGRAMMES = [
    {"slug": "civil", "code": "CIVIL", "degree": "B.E.", "name": "Civil Engineering",
     "about": "Focuses on construction, structural engineering, infrastructure and related engineering fields.",
     "focus": ["Construction", "Structural engineering", "Infrastructure"]},
    {"slug": "cse", "code": "CSE", "degree": "B.E.", "name": "Computer Science and Engineering",
     "about": "Focuses on computer science, programming, software development and modern computing technologies.",
     "focus": ["Programming", "Software development", "Modern computing"]},
    {"slug": "ece", "code": "ECE", "degree": "B.E.", "name": "Electronics and Communication Engineering",
     "about": "Focuses on electronics, communication systems, embedded technologies and digital systems.",
     "focus": ["Electronics", "Communication systems", "Embedded technologies", "Digital systems"]},
    {"slug": "eee", "code": "EEE", "degree": "B.E.", "name": "Electrical and Electronics Engineering",
     "about": "Focuses on electrical systems, power electronics, automation and related technologies.",
     "focus": ["Electrical systems", "Power electronics", "Automation"]},
    {"slug": "mech", "code": "MECH", "degree": "B.E.", "name": "Mechanical Engineering",
     "about": "Focuses on mechanical design, manufacturing and engineering systems.",
     "focus": ["Mechanical design", "Manufacturing", "Engineering systems"]},
    {"slug": "aids", "code": "AI&DS", "degree": "B.Tech", "name": "Artificial Intelligence and Data Science",
     "about": "Focuses on artificial intelligence, machine learning, data analytics and intelligent technologies.",
     "focus": ["Artificial intelligence", "Machine learning", "Data analytics"]},
    {"slug": "it", "code": "IT", "degree": "B.Tech", "name": "Information Technology",
     "about": "Focuses on information technology, databases, networking, web technologies, cloud computing and modern IT solutions.",
     "focus": ["Databases", "Networking", "Web technologies", "Cloud computing"]},
]

BY_SLUG = {p["slug"]: p for p in PROGRAMMES}

# SAMPLE layout - replace names/notes/positions with your real campus.
BUILDINGS = [
    {"id": "main",   "name": "Main Block",           "x": 240, "y": 80,  "w": 160, "h": 74, "note": "Administration and classrooms."},
    {"id": "dept",   "name": "Department Blocks",    "x": 40,  "y": 80,  "w": 160, "h": 74, "note": "Labs and department offices."},
    {"id": "hostel", "name": "Hostel",               "x": 440, "y": 80,  "w": 160, "h": 74, "note": "Student accommodation."},
    {"id": "tp",     "name": "Training & Placement", "x": 60,  "y": 206, "w": 180, "h": 62, "note": "Training programmes and campus recruitment."},
    {"id": "mess",   "name": "Mess",                 "x": 400, "y": 206, "w": 160, "h": 62, "note": "Hostel dining."},
    {"id": "gate",   "name": "Main Gate",            "x": 280, "y": 336, "w": 80,  "h": 40, "note": "Entry point to the campus."},
]

# SAMPLE events - replace with real ones (or load from the database later).
EVENTS = [
    {"date": "Oct 12", "title": "First-year orientation", "text": "Meet your department, faculty and seniors."},
    {"date": "Nov 03", "title": "Technical symposium", "text": "Paper presentations, project expo and coding rounds."},
    {"date": "Dec 09", "title": "Placement training week", "text": "Aptitude, communication and mock interviews."},
]

EMERGENCY = [
    {"label": "Ambulance", "number": "108"},
    {"label": "Police", "number": "100"},
    {"label": "Fire", "number": "101"},
    {"label": "College admission office", "number": "+91-6380989024"},
]


# ---------------------------------------------------------------------------
# Landing page roles (Students / Faculties / Guest).
# A chip is either a question for the AI  -> {"label", "q"}
#              or a link to another page  -> {"label", "endpoint"}   (Flask endpoint name)
# Edit these freely.
# ---------------------------------------------------------------------------
ROLES = {
    "student": {
        "label": "Students",
        "welcome": "Hi! 🎓 I can help you with courses, fees, hostel and placements.\nWhat would you like to know?",
        "chips": [
            {"label": "Courses", "endpoint": "courses"},
            {"label": "Departments", "endpoint": "departments"},
            {"label": "Fees", "q": "What are the fees?"},
            {"label": "Hostel", "q": "Is there a hostel?"},
            {"label": "Placements", "q": "Tell me about placements"},
            {"label": "Campus Map", "endpoint": "campus_map"},
            {"label": "Events", "endpoint": "events"},
        ],
    },
    "faculty": {
        "label": "Faculties",
        "welcome": "Welcome! 🧑‍🏫 I can help with departments, events and campus information.\nWhat do you need?",
        "chips": [
            {"label": "Departments", "endpoint": "departments"},
            {"label": "Events", "endpoint": "events"},
            {"label": "Campus Map", "endpoint": "campus_map"},
            {"label": "Emergency", "endpoint": "emergency"},
            {"label": "About the college", "q": "Tell me about Kings College of Engineering"},
        ],
    },
    "guest": {
        "label": "Guest",
        "welcome": "Welcome to Kings College of Engineering! 🙋\nAsk me about admissions, courses or how to reach the campus.",
        "chips": [
            {"label": "About the college", "q": "Tell me about Kings College of Engineering"},
            {"label": "Admissions", "q": "Tell me about admissions"},
            {"label": "Courses", "endpoint": "courses"},
            {"label": "Campus Map", "endpoint": "campus_map"},
            {"label": "Contact", "q": "How can I contact the college?"},
        ],
    },
}

# shown when the chat is opened from the sidebar (no role chosen)
DEFAULT_CHIPS = [
    {"label": "What are the courses available?", "q": "What are the courses available?"},
    {"label": "Tell me about CSE department", "q": "Tell me about CSE department"},
    {"label": "Is there a hostel?", "q": "Is there a hostel?"},
    {"label": "What is the TNEA code?", "q": "What is the TNEA code?"},
]
