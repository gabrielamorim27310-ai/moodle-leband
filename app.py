import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User

# Carregar .env automaticamente se existir
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def create_app():
    IS_VERCEL = bool(os.environ.get('VERCEL'))

    app = Flask(
        __name__,
        # No Vercel, templates e static ficam no mesmo nível de /var/task
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        instance_path='/tmp' if IS_VERCEL else None,
    )
    app.config.from_object(Config)

    # Criar diretórios de upload (apenas graváveis no Vercel = /tmp)
    try:
        os.makedirs(app.config['UPLOAD_FOLDER_SLIDES'], exist_ok=True)
        os.makedirs(app.config['UPLOAD_FOLDER_SUBMISSIONS'], exist_ok=True)
        if not IS_VERCEL:
            os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Inicializar extensões
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.microsoft_login'
    login_manager.login_message = 'Faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registrar blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.professor import professor_bp
    from routes.aluno import aluno_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(professor_bp)
    app.register_blueprint(aluno_bp)

    # Criar tabelas
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
