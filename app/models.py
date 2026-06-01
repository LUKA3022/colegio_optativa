from flask_login import UserMixin

from .extensions import db


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    role = db.relationship("Role", backref=db.backref("users", lazy=True))


class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)


# Tabla intermedia: Estudiantes inscritos en Cursos
student_course = db.Table(
    "student_course",
    db.Column("student_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("course_id", db.Integer, db.ForeignKey("courses.id"), primary_key=True),
)


class Subject(db.Model):
    __tablename__ = "subjects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    teacher = db.relationship("User", backref=db.backref("subjects_taught", lazy=True))
    course = db.relationship("Course", backref=db.backref("subjects", lazy=True))


class Assessment(db.Model):
    __tablename__ = "assessments"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'exam' o 'project'
    scheduled_date = db.Column(db.DateTime, nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=False)

    subject = db.relationship("Subject", backref=db.backref("assessments", lazy=True))


class AssessmentItem(db.Model):
    __tablename__ = "assessment_items"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("assessments.id"), nullable=False
    )
    content = db.Column(db.Text, nullable=False)
    expected_answer = db.Column(db.Text, nullable=True)
    points = db.Column(db.Float, default=1.0)

    assessment = db.relationship("Assessment", backref=db.backref("items", lazy=True))


class Submission(db.Model):
    __tablename__ = "submissions"
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(
        db.Integer, db.ForeignKey("assessments.id"), nullable=False
    )
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    auto_score = db.Column(db.Float, default=0.0)
    final_score = db.Column(db.Float, nullable=True)
    teacher_reviewed = db.Column(db.Boolean, default=False)

    assessment = db.relationship(
        "Assessment", backref=db.backref("submissions", lazy=True)
    )
    student = db.relationship("User", backref=db.backref("submissions", lazy=True))


class Answer(db.Model):
    __tablename__ = "answers"
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(
        db.Integer, db.ForeignKey("submissions.id"), nullable=False
    )
    item_id = db.Column(
        db.Integer, db.ForeignKey("assessment_items.id"), nullable=False
    )
    student_response = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, default=False)

    submission = db.relationship("Submission", backref=db.backref("answers", lazy=True))
    item = db.relationship("AssessmentItem")
