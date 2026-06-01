import os

from flask import Flask, redirect, render_template, request, url_for
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# [Inferencia] Se establece una clave secreta codificada estáticamente para desarrollo. En producción debe ser una variable de entorno segura.
app.config["SECRET_KEY"] = "desarrollo_secreto_123"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    # Si el usuario ya está autenticado, enviarlo al dashboard
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        # Validar existencia de usuario y hash de contraseña
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            return "Credenciales inválidas. Intenta nuevamente.", 401

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    return f"""
    <h1>Bienvenido, {current_user.username}</h1>
    <p>Tu rol asignado es: {current_user.role.name}</p>
    <a href='/logout'>Cerrar sesión</a>
    """


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Inicialización de la base de datos
with app.app_context():
    db.create_all()

    # [Inferencia] Se generan datos iniciales por defecto (Seed) para probar la validación de roles y usuarios.
    if not Role.query.filter_by(name="admin").first():
        admin_role = Role(name="admin")
        user_role = Role(name="user")
        db.session.add(admin_role)
        db.session.add(user_role)
        db.session.commit()

        hashed_password = bcrypt.generate_password_hash("python3").decode("utf-8")
        admin_user = User(
            username="admin", password_hash=hashed_password, role_id=admin_role.id
        )
        db.session.add(admin_user)
        db.session.commit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3308)
