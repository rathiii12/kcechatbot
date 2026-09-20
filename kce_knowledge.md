// =====================================================================
//  KCE KNOWLEDGE NOTES
//  The chatbot searches this file every time someone asks a question.
//
//  HOW TO USE
//  1. Write a "# Heading" for each topic.
//  2. Under it, write real facts as plain sentences or "-" bullet points.
//  3. Save the file. No restart needed.
//
//  Lines starting with // are ignored.
//  Only write facts you are sure about. Topics with nothing under
//  them are skipped, so you can leave the ones you don't need empty.
// =====================================================================


# Infrastructure
// Example:
// - The campus has ... (classrooms, labs, Wi-Fi, auditorium, etc.)


# Laboratories
// Example:
// - Computer Science labs: ...


# Library
// Example:
// - Number of books, e-journals, timings ...


# Transport
// Example:
// - Bus routes, timings, fees ...


# Sports and Facilities
// Example:
// - Grounds, gym, indoor games ...


# Canteen and Mess
// Example:
// - Food facilities, timings ...


# Clubs and Student Activities
// Example:
// - Clubs, associations, symposiums ...


# Scholarships
// Example:
// - Available scholarships and eligibility ...


# Contact
// Example:
// - Address, phone, email, office hours ...

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

DEFAULT_CHIPS = [
    {"label": "What are the courses available?", "q": "What are the courses available?"},
    {"label": "Tell me about CSE department", "q": "Tell me about CSE department"},
    {"label": "Is there a hostel?", "q": "Is there a hostel?"},
    {"label": "What is the TNEA code?", "q": "What is the TNEA code?"},
]