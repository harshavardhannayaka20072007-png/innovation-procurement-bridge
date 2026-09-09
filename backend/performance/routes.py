from flask import Blueprint, request, redirect, url_for, flash
from backend.db import execute_db

performance_bp = Blueprint('performance', __name__)

@performance_bp.route('/add', methods=['POST'])
def add_performance():
    pilot_id = request.form.get('pilot_id', type=int)
    kpi_name = request.form.get('kpi_name')
    target_value = request.form.get('target_value')
    actual_value = request.form.get('actual_value')
    unit = request.form.get('unit')
    remarks = request.form.get('remarks', '')

    execute_db(
        """INSERT INTO performance (pilot_id, kpi_name, target_value, actual_value, unit, remarks)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (pilot_id, kpi_name, target_value, actual_value, unit, remarks)
    )

    flash("KPI performance record added!", "success")
    return redirect(url_for('government.performance', pilot_id=pilot_id))
