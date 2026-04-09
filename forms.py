from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, TextAreaField,
                     DateTimeLocalField, SubmitField)
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired


class RegisterForm(FlaskForm):
    name = StringField('Nome Completo', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    role = SelectField('Perfil', choices=[('aluno', 'Aluno'), ('professor', 'Professor')],
                       validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha',
                                     validators=[DataRequired(), EqualTo('password', message='Senhas não conferem')])
    submit = SubmitField('Cadastrar')


class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')


class CourseForm(FlaskForm):
    name = StringField('Nome da Disciplina', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descrição')
    code = StringField('Código da Disciplina', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Criar Disciplina')


class SlideForm(FlaskForm):
    title = StringField('Título do Material', validators=[DataRequired(), Length(max=200)])
    file = FileField('Arquivo', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'ppt', 'pptx', 'doc', 'docx', 'png', 'jpg', 'zip'],
                     'Formatos permitidos: PDF, PPT, PPTX, DOC, DOCX, PNG, JPG, ZIP')
    ])
    submit = SubmitField('Enviar Material')


class AnnouncementForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Conteúdo', validators=[DataRequired()])
    submit = SubmitField('Publicar Aviso')


class AssignmentForm(FlaskForm):
    title = StringField('Título do Trabalho', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Descrição / Instruções', validators=[DataRequired()])
    due_date = DateTimeLocalField('Data de Entrega', format='%Y-%m-%dT%H:%M',
                                  validators=[DataRequired()])
    submit = SubmitField('Criar Trabalho')


class SubmissionForm(FlaskForm):
    file = FileField('Arquivo do Trabalho', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'zip', 'rar', 'py', 'java', 'cpp', 'txt', 'png', 'jpg'],
                     'Formato não permitido')
    ])
    comment = TextAreaField('Comentário (opcional)')
    submit = SubmitField('Enviar Trabalho')


class EnrollForm(FlaskForm):
    code = StringField('Código da Disciplina', validators=[DataRequired()])
    submit = SubmitField('Matricular-se')


class GradeForm(FlaskForm):
    grade = StringField('Nota', validators=[DataRequired()])
    feedback = TextAreaField('Feedback (opcional)')
    submit = SubmitField('Salvar Nota')
