from app import app
from database import db, CollegeInfo


data = [

    # ==========================================
    # COURSES
    # ==========================================

    {
        "category": "Course",
        "title": "Undergraduate Programmes",
        "content": """Kings College of Engineering offers 7 undergraduate programmes:

1. B.E. Civil Engineering
2. B.E. Computer Science and Engineering
3. B.E. Electronics and Communication Engineering
4. B.E. Electrical and Electronics Engineering
5. B.E. Mechanical Engineering
6. B.Tech Artificial Intelligence and Data Science
7. B.Tech Information Technology"""
    },


    # ==========================================
    # DEPARTMENTS
    # ==========================================

    {
        "category": "Department",
        "title": "Computer Science and Engineering",
        "content": """The Computer Science and Engineering programme at Kings College of Engineering focuses on computer science, programming, software development and modern computing technologies."""
    },

    {
        "category": "Department",
        "title": "Artificial Intelligence and Data Science",
        "content": """The Artificial Intelligence and Data Science programme focuses on artificial intelligence, machine learning, data analytics and intelligent technologies."""
    },

    {
        "category": "Department",
        "title": "Electronics and Communication Engineering",
        "content": """The Electronics and Communication Engineering programme focuses on electronics, communication systems, embedded technologies and digital systems."""
    },

    {
        "category": "Department",
        "title": "Electrical and Electronics Engineering",
        "content": """The Electrical and Electronics Engineering programme focuses on electrical systems, power electronics, automation and related technologies."""
    },

    {
        "category": "Department",
        "title": "Mechanical Engineering",
        "content": """The Mechanical Engineering programme focuses on mechanical design, manufacturing and engineering systems."""
    },

    {
        "category": "Department",
        "title": "Civil Engineering",
        "content": """The Civil Engineering programme focuses on construction, structural engineering, infrastructure and related engineering fields."""
    },

    {
        "category": "Department",
        "title": "Information Technology",
        "content": """The Information Technology programme focuses on information technology, databases, networking, web technologies, cloud computing and modern IT solutions."""
    },


    # ==========================================
    # ADMISSION
    # ==========================================

    {
        "category": "Admission",
        "title": "Admissions",
        "content": """🎓 Admissions at Kings College of Engineering

Kings College of Engineering offers admission to undergraduate and postgraduate programmes.

Students can get information about:

• Admission process
• Eligibility requirements
• Application procedure
• Required documents
• Important admission dates
• Counselling and admission guidelines

For the latest admission details and application procedure, students should refer to the official Kings College of Engineering admission information."""
    },


    # ==========================================
    # HOSTEL
    # ==========================================

    {
        "category": "Hostel",
        "title": "Hostel Facilities",
        "content": """🏠 Hostel Facilities

Kings College of Engineering provides hostel facilities for students.

The hostel section supports students with accommodation and basic residential facilities.

Students can contact the college for the latest information about hostel availability, rules, fees and facilities."""
    },


    # ==========================================
    # PLACEMENTS
    # ==========================================

    {
        "category": "Placement",
        "title": "Training and Placement",
        "content": """💼 Training and Placement

Kings College of Engineering has a Training and Placement Cell that supports students with career opportunities and campus recruitment.

The placement activities include:

• Training programmes
• Skill development
• Placement preparation
• Company recruitment
• Career guidance

Students can contact the Training and Placement Cell for the latest placement information."""
    },


    # ==========================================
    # FEES
    # ==========================================

    {
        "category": "Fees",
        "title": "Fee Information",
        "content": """💰 Fee Information

The fee structure at Kings College of Engineering may vary depending on the programme and admission category.

Students can get information about:

• Tuition fees
• Other applicable fees
• Hostel fees
• Examination fees
• Admission-related fees
• Scholarship and fee reimbursement details

For the latest fee structure, students should refer to the official Kings College of Engineering admission information or contact the college admission office.

Admission Contact:
+91-6380989024"""
    }

]


# ==========================================
# CREATE / RESET DATABASE
# ==========================================

with app.app_context():

    db.drop_all()

    db.create_all()

    for item in data:

        info = CollegeInfo(
            category=item["category"],
            title=item["title"],
            content=item["content"]
        )

        db.session.add(info)

    db.session.commit()


print("Database seeded successfully!")