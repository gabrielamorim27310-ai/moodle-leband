import os
import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Course, Slide, Announcement, Assignment, Submission
from forms import CourseForm, SlideForm, AnnouncementForm, AssignmentForm, GradeForm

professor_bp = Blueprint('professor', __name__, url_prefix='/professor')


def professor_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_professor:
            flash('Acesso restrito a professores.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@professor_bp.route('/courses')
@login_required
@professor_required
def my_courses():
    courses = Course.query.filter_by(professor_id=current_user.id).all()
    return render_template('professor/courses.html', courses=courses)


@professor_bp.route('/courses/new', methods=['GET', 'POST'])
@login_required
@professor_required
def create_course():
    form = CourseForm()
    if form.validate_on_submit():
        if Course.query.filter_by(code=form.code.data).first():
            flash('Código de disciplina já existe.', 'danger')
            return render_template('professor/create_course.html', form=form)

        course = Course(
            name=form.name.data,
            description=form.description.data,
            code=form.code.data.upper(),
            professor_id=current_user.id
        )
        db.session.add(course)
        db.session.commit()
        flash('Disciplina criada com sucesso!', 'success')
        return redirect(url_for('professor.view_course', course_id=course.id))

    return render_template('professor/create_course.html', form=form)


@professor_bp.route('/courses/<int:course_id>')
@login_required
@professor_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course.professor_id != current_user.id:
        flash('Você não tem permissão para acessar esta disciplina.', 'danger')
        return redirect(url_for('professor.my_courses'))
    return render_template('professor/view_course.html', course=course)


@professor_bp.route('/courses/<int:course_id>/slides/upload', methods=['GET', 'POST'])
@login_required
@professor_required
def upload_slide(course_id):
    course = Course.query.get_or_404(course_id)
    if course.professor_id != current_user.id:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('professor.my_courses'))

    form = SlideForm()
    if form.validate_on_submit():
        file = form.file.data
        original = secure_filename(file.filename)
        ext = original.rsplit('.', 1)[-1] if '.' in original else ''
        filename = f"{uuid.uuid4().hex}.{ext}"

        upload_path = current_app.config['UPLOAD_FOLDER_SLIDES']
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))

        slide = Slide(
            title=form.title.data,
            filename=filename,
            original_filename=original,
            course_id=course.id
        )
        db.session.add(slide)
        db.session.commit()
        flash('Material enviado com sucesso!', 'success')
        return redirect(url_for('professor.view_course', course_id=course.id))

    return render_template('professor/upload_slide.html', form=form, course=course)


@professor_bp.route('/courses/<int:course_id>/slides/<int:slide_id>/delete', methods=['POST'])
@login_required
@professor_required
def delete_slide(course_id, slide_id):
    slide = Slide.query.get_or_404(slide_id)
    if slide.course.professor_id != current_user.id:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('professor.my_courses'))

    filepath = os.path.join(current_app.config['UPLOAD_FOLDER_SLIDES'], slide.filename)
    if os.path.exists(filepath):
        os.remove(filepath)

    db.session.delete(slide)
    db.session.commit()
    flash('Material removido.', 'success')
    return redirect(url_for('professor.view_course', course_id=course_id))


@professor_bp.route('/courses/<int:course_id>/announcements/new', methods=['GET', 'POST'])
@login_required
@professor_required
def create_announcement(course_id):
    course = Course.query.get_or_404(course_id)
    if course.professor_id != current_user.id:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('professor.my_courses'))

    form = AnnouncementForm()
    if form.validate_on_submit():
        ann = Announcement(
            title=form.title.data,
            content=form.content.data,
            course_id=course.id
        )
        db.session.add(ann)
        db.session.commit()
        flash('Aviso publicado!', 'success')
        return redirect(url_for('professor.view_course', course_id=course.id))

    return render_template('professor/create_announcement.html', form=form, course=course)


@professor_bp.route('/courses/<int:course_id>/announcements/<int:ann_id>/delete', methods=['POST'])
@login_required
@professor_required
def delete_announcement(course_id, ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    if ann.course.professor_id != current_user.id:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('professor.my_courses'))

    db.session.delete(ann)
    db.session.commit()
    flash('Aviso removido.', 'success')
    return redirect(url_for('professor.view_course', course_id=course_id))


@professor_bp.route('/courses/<int:course_id>/assignments/new', methods=['GET', 'POST'])
@login_required
@professor_required
def create_assignment(course_id):
    course = Course.query.get_or_404(course_id)
    if course.professor_id != current_user.id:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('professor.my_courses'))

    form = AssignmentForm()
    if form.validate_on_submit():
        assignment = Assignment(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data.replace(tzinfo=timezone.utc),
            course_id=course.id
        )
        db.session.add(assignment)
        db.session.commit()
        flash('Trabalho criado com sucesso!', 'success')
        return redirect(url_for('professor.view_course', course_id=course.id))

    return render_template('professor/create_assignment.html', form=form, course=course)


@professor_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>')
@login_required
@professor_required
def view_submissions(course_id, assignment_id):
    course = Course.query.get_or_404(course_id)
    if course.professor_id != current_user.id:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('professor.my_courses'))

    assignment = Assignment.query.get_or_404(assignment_id)
    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    return render_template('professor/view_submissions.html',
                           course=course, assignment=assignment, submissions=submissions)


@professor_bp.route('/submissions/<int:submission_id>/grade', methods=['GET', 'POST'])
@login_required
@professor_required
def grade_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    if submission.assignment.course.professor_id != current_user.id:
        flash('Sem permissão.', 'danger')
        return redirect(url_for('professor.my_courses'))

    form = GradeForm()
    if form.validate_on_submit():
        try:
            submission.grade = float(form.grade.data)
        except ValueError:
            flash('Nota inválida.', 'danger')
            return render_template('professor/grade_submission.html',
                                   form=form, submission=submission)
        submission.feedback = form.feedback.data
        db.session.commit()
        flash('Nota salva!', 'success')
        return redirect(url_for('professor.view_submissions',
                                course_id=submission.assignment.course_id,
                                assignment_id=submission.assignment_id))

    form.grade.data = str(submission.grade) if submission.grade is not None else ''
    form.feedback.data = submission.feedback or ''
    return render_template('professor/grade_submission.html',
                           form=form, submission=submission)
