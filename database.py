from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class CollegeInfo(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    category = db.Column(
        db.String(100),
        nullable=False
    )

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    def __repr__(self):

        return f"<CollegeInfo {self.title}>"