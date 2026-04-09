import msal
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)


def _build_msal_app():
    return msal.ConfidentialClientApplication(
        current_app.config['MS_CLIENT_ID'],
        authority=current_app.config['MS_AUTHORITY'],
        client_credential=current_app.config['MS_CLIENT_SECRET'],
    )


@auth_bp.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    # Redireciona direto para o fluxo Microsoft
    return redirect(url_for('auth.microsoft_login'))


@auth_bp.route('/register')
def register():
    # Cadastro também é feito via Microsoft
    return redirect(url_for('auth.microsoft_login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('main.index'))


# ── Microsoft SSO ──

@auth_bp.route('/auth/microsoft/login')
def microsoft_login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if not current_app.config.get('MS_CLIENT_ID'):
        flash('Login Microsoft não configurado. Configure MS_CLIENT_ID no .env.', 'danger')
        return render_template('auth/ms_not_configured.html')

    app_msal = _build_msal_app()
    flow = app_msal.initiate_auth_code_flow(
        scopes=current_app.config['MS_SCOPE'],
        redirect_uri=current_app.config['MS_REDIRECT_URI'],
    )
    session['ms_auth_flow'] = flow
    return redirect(flow['auth_uri'])


@auth_bp.route('/auth/microsoft/callback')
def microsoft_callback():
    flow = session.pop('ms_auth_flow', None)
    if not flow:
        flash('Sessão expirada. Tente novamente.', 'danger')
        return redirect(url_for('main.index'))

    app_msal = _build_msal_app()
    result = app_msal.acquire_token_by_auth_code_flow(flow, request.args)

    if 'error' in result:
        flash(f"Erro Microsoft: {result.get('error_description', result['error'])}", 'danger')
        return redirect(url_for('main.index'))

    token = result['access_token']
    graph_resp = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10,
    )

    if graph_resp.status_code != 200:
        flash('Erro ao obter perfil Microsoft.', 'danger')
        return redirect(url_for('main.index'))

    ms_profile = graph_resp.json()
    ms_id = ms_profile['id']
    ms_email = ms_profile.get('mail') or ms_profile.get('userPrincipalName', '')
    ms_name = ms_profile.get('displayName', ms_email)

    allowed_domain = current_app.config.get('MS_ALLOWED_DOMAIN', '').strip().lower()
    if allowed_domain:
        email_domain = ms_email.split('@')[-1].lower() if '@' in ms_email else ''
        if email_domain != allowed_domain:
            flash(
                f'Acesso restrito a e-mails @{allowed_domain}. '
                f'Você entrou com {ms_email}.',
                'danger',
            )
            return redirect(url_for('main.index'))

    user = User.query.filter_by(microsoft_id=ms_id).first()

    if not user:
        user = User.query.filter_by(email=ms_email).first()
        if user:
            user.microsoft_id = ms_id
            db.session.commit()
        else:
            session['ms_pending'] = {
                'microsoft_id': ms_id,
                'email': ms_email,
                'name': ms_name,
            }
            return redirect(url_for('auth.microsoft_choose_role'))

    login_user(user)
    return redirect(url_for('main.dashboard'))


@auth_bp.route('/auth/microsoft/choose-role', methods=['GET', 'POST'])
def microsoft_choose_role():
    ms_pending = session.get('ms_pending')
    if not ms_pending:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        role = request.form.get('role')
        if role not in ('professor', 'aluno'):
            flash('Selecione um perfil válido.', 'danger')
            return render_template('auth/choose_role.html', ms_data=ms_pending)

        user = User(
            name=ms_pending['name'],
            email=ms_pending['email'],
            role=role,
            microsoft_id=ms_pending['microsoft_id'],
        )
        db.session.add(user)
        db.session.commit()
        session.pop('ms_pending', None)

        login_user(user)
        return redirect(url_for('main.dashboard'))

    return render_template('auth/choose_role.html', ms_data=ms_pending)
