from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SelectField, TextAreaField,
                     DateTimeLocalField, SubmitField)
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired


class RegisterForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=150)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('aluno', 'Student'), ('professor', 'Teacher')],
                       validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password', message='Passwords do not match')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class CourseForm(FlaskForm):
    name = StringField('Course Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    code = StringField('Course Code', validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Create Course')


class SlideForm(FlaskForm):
    title = StringField('Material Title', validators=[DataRequired(), Length(max=200)])
    file = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'ppt', 'pptx', 'doc', 'docx', 'png', 'jpg', 'zip'],
                     'Allowed formats: PDF, PPT, PPTX, DOC, DOCX, PNG, JPG, ZIP')
    ])
    submit = SubmitField('Upload Material')


class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post Announcement')


class AssignmentForm(FlaskForm):
    title = StringField('Assignment Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description / Instructions', validators=[DataRequired()])
    due_date = DateTimeLocalField('Due Date', format='%Y-%m-%dT%H:%M',
                                  validators=[DataRequired()])
    submit = SubmitField('Create Assignment')


class SubmissionForm(FlaskForm):
    file = FileField('Assignment File', validators=[
        FileRequired(),
        FileAllowed(['pdf', 'doc', 'docx', 'zip', 'rar', 'py', 'java', 'cpp', 'txt', 'png', 'jpg'],
                     'File format not allowed')
    ])
    comment = TextAreaField('Comment (optional)')
    submit = SubmitField('Submit Assignment')


class EnrollForm(FlaskForm):
    code = StringField('Course Code', validators=[DataRequired()])
    submit = SubmitField('Enroll')


class GradeForm(FlaskForm):
    grade = StringField('Grade', validators=[DataRequired()])
    feedback = TextAreaField('Feedback (optional)')
    submit = SubmitField('Save Grade')
