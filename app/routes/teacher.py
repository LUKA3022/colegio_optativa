from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Assessment, AssessmentItem, Course, Subject, Submission

teacher_bp = Blueprint("teacher", __name__)


def check_teacher():
    if current_user.role.name != "profesor":
        abort(403)


@teacher_bp.route("/")
@login_required
def dashboard():
    check_teacher()
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    subject_ids = [s.id for s in subjects]

    # Extraer evaluaciones ordenadas por fecha ascendente
    if subject_ids:
        assessments = (
            Assessment.query.filter(Assessment.subject_id.in_(subject_ids))
            .order_by(Assessment.scheduled_date.asc())
            .all()
        )
    else:
        assessments = []

    return render_template("teacher/dashboard.html", assessments=assessments)


@teacher_bp.route("/subjects")
@login_required
def subjects():
    check_teacher()
    subjects_list = Subject.query.filter_by(teacher_id=current_user.id).all()
    return render_template("teacher/subjects.html", subjects=subjects_list)


@teacher_bp.route("/assessments")
@login_required
def assessments():
    check_teacher()
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    subject_ids = [s.id for s in subjects]

    if subject_ids:
        assessments_list = Assessment.query.filter(
            Assessment.subject_id.in_(subject_ids)
        ).all()
    else:
        assessments_list = []

    return render_template("teacher/assessments.html", assessments=assessments_list)


@teacher_bp.route("/subject/<int:subject_id>/assessment/new", methods=["GET", "POST"])
@login_required
def create_assessment(subject_id):
    check_teacher()
    subject = Subject.query.get_or_404(subject_id)

    if subject.teacher_id != current_user.id:
        abort(403)

    if request.method == "POST":
        title = request.form.get("title")
        type_ = request.form.get("type")
        scheduled_date = request.form.get("scheduled_date")

        new_assessment = Assessment(
            title=title,
            type=type_,
            scheduled_date=scheduled_date,
            subject_id=subject.id,
        )
        db.session.add(new_assessment)
        db.session.flush()

        content = request.form.get("item_content")
        expected = request.form.get("item_expected")
        if content:
            item = AssessmentItem(
                assessment_id=new_assessment.id,
                content=content,
                expected_answer=expected,
                points=1.0,
            )
            db.session.add(item)

        db.session.commit()
        return redirect(url_for("teacher.assessments"))

    return render_template("teacher/create_assessment.html", subject=subject)


@teacher_bp.route("/assessment/<int:assessment_id>/submissions")
@login_required
def review_submissions(assessment_id):
    check_teacher()
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.subject.teacher_id != current_user.id:
        abort(403)

    submissions = Submission.query.filter_by(assessment_id=assessment.id).all()
    return render_template(
        "teacher/review_submissions.html",
        assessment=assessment,
        submissions=submissions,
    )


# --- RUTAS DE CURSOS ---
@teacher_bp.route("/course/new", methods=["GET", "POST"])
@login_required
def create_course():
    check_teacher()
    if request.method == "POST":
        name = request.form.get("name")
        year = request.form.get("year")
        new_course = Course(name=name, year=int(year))
        db.session.add(new_course)
        db.session.commit()
        return redirect(url_for("teacher.subjects"))
    return render_template("teacher/form_course.html", course=None)


@teacher_bp.route("/course/<int:course_id>/edit", methods=["GET", "POST"])
@login_required
def edit_course(course_id):
    check_teacher()
    course = Course.query.get_or_404(course_id)
    if request.method == "POST":
        course.name = request.form.get("name")
        course.year = int(request.form.get("year"))
        db.session.commit()
        return redirect(url_for("teacher.subjects"))
    return render_template("teacher/form_course.html", course=course)


# --- RUTAS DE MATERIAS ---
@teacher_bp.route("/subject/new", methods=["GET", "POST"])
@login_required
def create_subject():
    check_teacher()
    courses = Course.query.all()
    if request.method == "POST":
        name = request.form.get("name")
        course_id = request.form.get("course_id")
        new_subject = Subject(
            name=name, teacher_id=current_user.id, course_id=course_id
        )
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for("teacher.subjects"))
    return render_template("teacher/form_subject.html", subject=None, courses=courses)


@teacher_bp.route("/subject/<int:subject_id>/edit", methods=["GET", "POST"])
@login_required
def edit_subject(subject_id):
    check_teacher()
    subject = Subject.query.get_or_404(subject_id)
    if subject.teacher_id != current_user.id:
        abort(403)
    courses = Course.query.all()
    if request.method == "POST":
        subject.name = request.form.get("name")
        subject.course_id = request.form.get("course_id")
        db.session.commit()
        return redirect(url_for("teacher.subjects"))
    return render_template(
        "teacher/form_subject.html", subject=subject, courses=courses
    )


# --- EDICIÓN DE EVALUACIONES ---
@teacher_bp.route("/assessment/<int:assessment_id>/edit", methods=["GET", "POST"])
@login_required
def edit_assessment(assessment_id):
    check_teacher()
    assessment = Assessment.query.get_or_404(assessment_id)
    if assessment.subject.teacher_id != current_user.id:
        abort(403)

    if request.method == "POST":
        assessment.title = request.form.get("title")
        assessment.type = request.form.get("type")
        assessment.scheduled_date = request.form.get("scheduled_date")
        db.session.commit()
        return redirect(url_for("teacher.assessments"))

    return render_template("teacher/form_assessment_edit.html", assessment=assessment)
