from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Answer, Assessment, Course, Subject, Submission, student_course

student_bp = Blueprint("student", __name__)


def check_student():
    if current_user.role.name != "estudiante":
        abort(403)


@student_bp.route("/")
@login_required
def dashboard():
    check_student()
    courses = (
        db.session.query(Course)
        .join(student_course)
        .filter(student_course.c.student_id == current_user.id)
        .all()
    )
    course_ids = [c.id for c in courses]

    if course_ids:
        subjects = Subject.query.filter(Subject.course_id.in_(course_ids)).all()
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
    else:
        assessments = []

    return render_template("student/dashboard.html", assessments=assessments)


@student_bp.route("/assessment/<int:assessment_id>", methods=["GET", "POST"])
@login_required
def take_assessment(assessment_id):
    check_student()
    assessment = Assessment.query.get_or_404(assessment_id)

    # Validación de envío previo
    existing_submission = Submission.query.filter_by(
        assessment_id=assessment.id, student_id=current_user.id
    ).first()
    if existing_submission:
        flash("Ya completaste esta evaluación.", "error")
        return redirect(url_for("student.dashboard"))

    if request.method == "POST":
        submission = Submission(assessment_id=assessment.id, student_id=current_user.id)
        db.session.add(submission)
        db.session.flush()

        auto_score = 0
        for item in assessment.items:
            # [Inferencia] Los campos input HTML deben nombrarse dinámicamente como name="item_1", name="item_2", etc.
            student_resp = request.form.get(f"item_{item.id}") or ""
            is_correct = False

            # Autocorrección básica por coincidencia de texto
            if assessment.type == "exam" and item.expected_answer:
                if student_resp.strip().lower() == item.expected_answer.strip().lower():
                    is_correct = True
                    auto_score += item.points

            answer = Answer(
                submission_id=submission.id,
                item_id=item.id,
                student_response=student_resp,
                is_correct=is_correct,
            )
            db.session.add(answer)

        submission.auto_score = auto_score
        db.session.commit()

        flash("Evaluación enviada y guardada.", "success")
        return redirect(url_for("student.dashboard"))

    return render_template("student/take_assessment.html", assessment=assessment)
