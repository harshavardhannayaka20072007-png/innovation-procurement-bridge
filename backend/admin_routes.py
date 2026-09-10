from flask import Blueprint, render_template, request, redirect, url_for, flash
from backend.db import query_db, execute_db
from backend.auth.session import require_roles

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@require_roles('admin')
def dashboard():
    users_count = query_db("SELECT COUNT(*) as count FROM users", one=True)['count']
    challenges_count = query_db("SELECT COUNT(*) as count FROM challenges", one=True)['count']
    applications_count = query_db("SELECT COUNT(*) as count FROM applications", one=True)['count']
    pilots_count = query_db("SELECT COUNT(*) as count FROM pilots", one=True)['count']
    recent_users = query_db("SELECT * FROM users ORDER BY created_at DESC LIMIT 5")
    
    return render_template(
        'admin/dashboard.html',
        users_count=users_count,
        challenges_count=challenges_count,
        applications_count=applications_count,
        pilots_count=pilots_count,
        recent_users=recent_users
    )

@admin_bp.route('/users')
@require_roles('admin')
def users():
    user_list = query_db("SELECT * FROM users ORDER BY created_at DESC")
    return render_template('admin/users.html', users=user_list)

@admin_bp.route('/departments')
@require_roles('admin')
def departments():
    depts = query_db("SELECT DISTINCT department FROM users WHERE department IS NOT NULL UNION SELECT DISTINCT department FROM challenges WHERE department IS NOT NULL")
    return render_template('admin/departments.html', departments=depts)

@admin_bp.route('/challenges')
@require_roles('admin')
def challenges():
    ch_list = query_db("SELECT * FROM challenges ORDER BY created_at DESC")
    return render_template('admin/challenges.html', challenges=ch_list)

@admin_bp.route('/startups')
@require_roles('admin')
def startups():
    startups_list = query_db("SELECT * FROM users WHERE role = 'startup' ORDER BY created_at DESC")
    return render_template('admin/startups.html', startups=startups_list)
