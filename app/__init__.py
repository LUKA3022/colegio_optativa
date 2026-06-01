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

        # Importación y registro de Blueprints
        from app.routes.auth import auth_bp
        from app.routes.student import student_bp
        from app.routes.teacher import teacher_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(teacher_bp, url_prefix="/teacher")
        app.register_blueprint(student_bp, url_prefix="/student")

        db.create_all()

    return app
