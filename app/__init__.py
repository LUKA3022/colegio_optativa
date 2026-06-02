import os

from flask import Flask

from app.extensions import bcrypt, db, login_manager


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "desarrollo_secreto_123"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("SQLALCHEMY_DATABASE_URI")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # [Inferencia] Se define la ruta de redirección para usuarios no autenticados
    login_manager.login_view = "auth.login"

    with app.app_context():
        from app.models import Role, User

        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

        from app.routes.auth import auth_bp
        from app.routes.student import student_bp
        from app.routes.teacher import teacher_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(teacher_bp, url_prefix="/teacher")
        app.register_blueprint(student_bp, url_prefix="/student")

        db.create_all()

        # Generar roles y usuarios por defecto para el sistema escolar
        if not Role.query.filter_by(name="profesor").first():
            profesor_role = Role(name="profesor")
            estudiante_role = Role(name="estudiante")
            db.session.add(profesor_role)
            db.session.add(estudiante_role)
            db.session.commit()

            hashed_password = bcrypt.generate_password_hash("asd").decode("utf-8")

            profesor_user = User(
                username="profesor1",
                password_hash=hashed_password,
                role_id=profesor_role.id,
            )
            estudiante_user = User(
                username="alumno1",
                password_hash=hashed_password,
                role_id=estudiante_role.id,
            )

            db.session.add(profesor_user)
            db.session.add(estudiante_user)
            db.session.commit()

    return app
