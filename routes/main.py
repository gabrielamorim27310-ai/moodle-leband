from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Course, Announcement

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_professor:
        courses = Course.query.filter_by(professor_id=current_user.id).all()
        total_students = sum(len(c.students) for c in courses)
        total_slides = sum(len(c.slides) for c in courses)
        total_assignments = sum(len(c.assignments) for c in courses)
        return render_template('dashboard.html',
                               courses=courses,
                               total_students=total_students,
                               total_slides=total_slides,
                               total_assignments=total_assignments)
    else:
        courses = current_user.courses_enrolled
        announcements = []
        for c in courses:
            for ann in c.announcements:
                announcements.append(ann)
        announcements.sort(key=lambda a: a.created_at, reverse=True)
        return render_template('dashboard.html',
                               courses=courses,
                               announcements=announcements[:10])
