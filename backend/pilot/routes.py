from flask import Blueprint, request, jsonify, redirect, url_for, flash
from backend.db import query_db, execute_db
from backend.auth.session import require_roles

pilot_bp = Blueprint('pilot', __name__)

@pilot_bp.route('/<int:pilot_id>/progress', methods=['POST'])
@require_roles('government')
def update_progress(pilot_id):
    progress = request.form.get('milestone_progress', type=int)
    status = request.form.get('status')

    query = "UPDATE pilots SET milestone_progress = ?"
    params = [progress]

    if status:
        query += ", status = ?"
        params.append(status)

    query += " WHERE pilot_id = ?"
    params.append(pilot_id)

    execute_db(query, tuple(params))
    flash("Pilot progress updated successfully!", "success")
    return redirect(url_for('government.pilots'))
