from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from app.extensions import bcrypt
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        # [Inferencia] Se asume que los roles se denominan 'profesor' y 'estudiante' en la base de datos para la redirección.
        if current_user.role.name == "profesor":
            return redirect(url_for("teacher.dashboard"))
        elif current_user.role.name == "estudiante":
            return redirect(url_for("student.dashboard"))
        return "Rol no reconocido", 403

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            if user.role.name == "profesor":
                return redirect(url_for("teacher.dashboard"))
            elif user.role.name == "estudiante":
                return redirect(url_for("student.dashboard"))
        else:
            flash("Credenciales inválidas.", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
