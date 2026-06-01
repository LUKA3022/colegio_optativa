from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Assessment, AssessmentItem, Subject, Submission

teacher_bp = Blueprint("teacher", __name__)


def check_teacher():
    if current_user.role.name != "profesor":
        abort(403)


@teacher_bp.route("/")
@login_required
def dashboard():
    check_teacher()
    subjects = Subject.query.filter_by(teacher_id=current_user.id).all()
    return render_template("teacher/dashboard.html", subjects=subjects)


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
        db.session.flush()  # Obtiene el ID antes de hacer commit completo

        # [Inferencia] Procesamiento de un solo ítem por formulario para establecer una base funcional. En producción se requiere iteración dinámica.
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
        flash("Evaluación creada exitosamente.", "success")
        return redirect(url_for("teacher.dashboard"))

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
