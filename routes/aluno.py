import os
import uuid
from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Course, Assignment, Submission
from forms import EnrollForm, SubmissionForm

aluno_bp = Blueprint('aluno', __name__, url_prefix='/aluno')


def aluno_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_aluno:
            flash('Access restricted to students.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated


@aluno_bp.route('/courses')
@login_required
@aluno_required
def my_courses():
    courses = current_user.courses_enrolled
    return render_template('aluno/courses.html', courses=courses)


@aluno_bp.route('/enroll', methods=['GET', 'POST'])
@login_required
@aluno_required
def enroll():
    form = EnrollForm()
    if form.validate_on_submit():
        course = Course.query.filter_by(code=form.code.data.upper()).first()
        if not course:
            flash('No course found with that code.', 'danger')
            return render_template('aluno/enroll.html', form=form)

        if course in current_user.courses_enrolled:
            flash('You are already enrolled in this course.', 'warning')
            return render_template('aluno/enroll.html', form=form)

        current_user.courses_enrolled.append(course)
        db.session.commit()
        flash(f'Successfully enrolled in {course.name}!', 'success')
        return redirect(url_for('aluno.view_course', course_id=course.id))

    return render_template('aluno/enroll.html', form=form)


@aluno_bp.route('/courses/<int:course_id>')
@login_required
@aluno_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    if course not in current_user.courses_enrolled:
        flash('You are not enrolled in this course.', 'danger')
        return redirect(url_for('aluno.my_courses'))
    return render_template('aluno/view_course.html', course=course)


@aluno_bp.route('/courses/<int:course_id>/assignments/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
@aluno_required
def submit_assignment(course_id, assignment_id):
    course = Course.query.get_or_404(course_id)
    if course not in current_user.courses_enrolled:
        flash('Permission denied.', 'danger')
        return redirect(url_for('aluno.my_courses'))

    assignment = Assignment.query.get_or_404(assignment_id)
    existing = Submission.query.filter_by(
        student_id=current_user.id, assignment_id=assignment_id
    ).first()

    form = SubmissionForm()
    if form.validate_on_submit():
        file = form.file.data
        original = secure_filename(file.filename)
        ext = original.rsplit('.', 1)[-1] if '.' in original else ''
        filename = f"{uuid.uuid4().hex}.{ext}"

        upload_path = current_app.config['UPLOAD_FOLDER_SUBMISSIONS']
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))

        if existing:
            old_path = os.path.join(upload_path, existing.filename)
            if os.path.exists(old_path):
                os.remove(old_path)
            existing.filename = filename
            existing.original_filename = original
            existing.comment = form.comment.data
            existing.grade = None
            existing.feedback = None
            from datetime import datetime, timezone
            existing.submitted_at = datetime.now(timezone.utc)
            flash('Assignment resubmitted successfully!', 'success')
        else:
            submission = Submission(
                filename=filename,
                original_filename=original,
                comment=form.comment.data,
                student_id=current_user.id,
                assignment_id=assignment_id
            )
            db.session.add(submission)
            flash('Assignment submitted successfully!', 'success')

        db.session.commit()
        return redirect(url_for('aluno.view_course', course_id=course_id))

    return render_template('aluno/submit_assignment.html',
                           form=form, course=course, assignment=assignment, existing=existing)


@aluno_bp.route('/grades')
@login_required
@aluno_required
def my_grades():
    submissions = Submission.query.filter_by(student_id=current_user.id).all()
    return render_template('aluno/grades.html', submissions=submissions)
