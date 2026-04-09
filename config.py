import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Em ambientes serverless (Vercel), /tmp é o único diretório gravável
IS_VERCEL = os.environ.get('VERCEL', False)
DB_DIR = '/tmp' if IS_VERCEL else os.path.join(BASE_DIR, 'instance')
UPLOAD_BASE = '/tmp/uploads' if IS_VERCEL else os.path.join(BASE_DIR, 'static', 'uploads')


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'saberflow-dev-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(DB_DIR, 'saberflow.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER_SLIDES = os.path.join(UPLOAD_BASE, 'slides')
    UPLOAD_FOLDER_SUBMISSIONS = os.path.join(UPLOAD_BASE, 'submissions')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload

    # Microsoft SSO (Azure AD)
    MS_CLIENT_ID = os.environ.get('MS_CLIENT_ID', '')
    MS_CLIENT_SECRET = os.environ.get('MS_CLIENT_SECRET', '')
    MS_TENANT_ID = os.environ.get('MS_TENANT_ID', 'common')
    MS_AUTHORITY = f"https://login.microsoftonline.com/{os.environ.get('MS_TENANT_ID', 'common')}"
    MS_REDIRECT_URI = os.environ.get('MS_REDIRECT_URI', 'http://localhost:5000/auth/microsoft/callback')
    MS_SCOPE = ['User.Read']
    # Domínio de e-mail permitido (ex: "band.com.br"). Vazio = qualquer e-mail.
    MS_ALLOWED_DOMAIN = os.environ.get('MS_ALLOWED_DOMAIN', '')
