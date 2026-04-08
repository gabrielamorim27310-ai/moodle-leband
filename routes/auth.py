import msal
import requests
from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


def _build_msal_app():
    return msal.ConfidentialClientApplication(
        current_app.config['MS_CLIENT_ID'],
        authority=current_app.config['MS_AUTHORITY'],
        client_credential=current_app.config['MS_CLIENT_SECRET'],
    )


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password_hash and user.check_password(form.password.data):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.dashboard'))
        flash('E-mail ou senha inválidos.', 'danger')

    ms_configured = bool(current_app.config.get('MS_CLIENT_ID'))
    return render_template('auth/login.html', form=form, ms_configured=ms_configured)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('E-mail já cadastrado.', 'danger')
            return render_template('auth/register.html', form=form)

        user = User(name=form.name.data, email=form.email.data, role=form.role.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado! Faça login para continuar.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('auth.login'))


# ── Microsoft SSO ──

@auth_bp.route('/auth/microsoft/login')
def microsoft_login():
    if not current_app.config.get('MS_CLIENT_ID'):
        flash('Login Microsoft não configurado.', 'danger')
        return redirect(url_for('auth.login'))

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
        flash('Erro no fluxo de autenticação.', 'danger')
        return redirect(url_for('auth.login'))

    app_msal = _build_msal_app()
    result = app_msal.acquire_token_by_auth_code_flow(flow, request.args)

    if 'error' in result:
        flash(f"Erro Microsoft: {result.get('error_description', result['error'])}", 'danger')
        return redirect(url_for('auth.login'))

    # Buscar perfil do usuário no Microsoft Graph
    token = result['access_token']
    graph_resp = requests.get(
        'https://graph.microsoft.com/v1.0/me',
        headers={'Authorization': f'Bearer {token}'},
        timeout=10,
    )

    if graph_resp.status_code != 200:
        flash('Erro ao obter perfil Microsoft.', 'danger')
        return redirect(url_for('auth.login'))

    ms_profile = graph_resp.json()
    ms_id = ms_profile['id']
    ms_email = ms_profile.get('mail') or ms_profile.get('userPrincipalName', '')
    ms_name = ms_profile.get('displayName', ms_email)

    # Verificar se já existe usuário com esse microsoft_id
    user = User.query.filter_by(microsoft_id=ms_id).first()

    if not user:
        # Verificar se já existe usuário com mesmo e-mail (vincular contas)
        user = User.query.filter_by(email=ms_email).first()
        if user:
            user.microsoft_id = ms_id
            db.session.commit()
        else:
            # Primeiro acesso via Microsoft: redirecionar para escolher perfil
            session['ms_pending'] = {
                'microsoft_id': ms_id,
                'email': ms_email,
                'name': ms_name,
            }
            return redirect(url_for('auth.microsoft_choose_role'))

    login_user(user)
    flash(f'Bem-vindo, {user.name}!', 'success')
    return redirect(url_for('main.dashboard'))


@auth_bp.route('/auth/microsoft/choose-role', methods=['GET', 'POST'])
def microsoft_choose_role():
    ms_pending = session.get('ms_pending')
    if not ms_pending:
        return redirect(url_for('auth.login'))

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
        flash(f'Conta criada com sucesso! Bem-vindo, {user.name}!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/choose_role.html', ms_data=ms_pending)
