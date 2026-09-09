import json

from flask import Blueprint, render_template

from backend.auth.session import require_roles
from backend.db import query_db

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')


@audit_bp.route('/')
@require_roles('government', 'admin')
def ledger():
    records = query_db('SELECT * FROM audit_records ORDER BY record_id DESC LIMIT 100')
    for record in records:
        record['payload'] = json.loads(record['payload'])
    return render_template('audit/ledger.html', records=records)
