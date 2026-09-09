from flask import Blueprint, request, jsonify, redirect, url_for, session, flash
from backend.db import query_db, execute_db

challenges_bp = Blueprint('challenges', __name__)

@challenges_bp.route('/', methods=['POST'])
def create_challenge():
    if request.is_json:
        data = request.get_json()
        title = data.get('title')
        department = data.get('department')
        description = data.get('description')
        requirements = data.get('requirements')
        deadline = data.get('deadline')
    else:
        title = request.form.get('title')
        department = request.form.get('department')
        description = request.form.get('description')
        requirements = request.form.get('requirements')
        deadline = request.form.get('deadline')

    if not title or not department or not description or not deadline:
        if request.is_json:
            return jsonify({'error': 'Missing required fields'}), 400
        flash('Missing required fields', 'danger')
        return redirect(url_for('government.create_challenge'))

    created_by = session.get('user_id', 1)
    
    challenge_id = execute_db(
        """INSERT INTO challenges (title, department, description, requirements, deadline, status, created_by)
           VALUES (?, ?, ?, ?, ?, 'Draft', ?)""",
        (title, department, description, requirements, deadline, created_by)
    )

    if request.is_json:
        return jsonify({'message': 'Challenge created successfully', 'challenge_id': challenge_id}), 201
    
    flash('Challenge created as Draft!', 'success')
    return redirect(url_for('government.challenges'))

@challenges_bp.route('/<int:challenge_id>/publish', methods=['PUT', 'POST'])
def publish_challenge(challenge_id):
    challenge = query_db("SELECT * FROM challenges WHERE challenge_id = ?", (challenge_id,), one=True)
    if not challenge:
        if request.is_json:
            return jsonify({'error': 'Challenge not found'}), 404
        flash('Challenge not found', 'danger')
        return redirect(url_for('government.challenges'))

    execute_db("UPDATE challenges SET status = 'Published' WHERE challenge_id = ?", (challenge_id,))

    if request.is_json:
        return jsonify({'message': 'Challenge published successfully'}), 200

    flash('Challenge published successfully!', 'success')
    return redirect(url_for('government.challenges'))
