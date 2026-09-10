import json

from flask import Blueprint, render_template, request

from backend.auth.session import require_roles
from backend.db import query_db

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')


@audit_bp.route('/')
@require_roles('government', 'admin')
def ledger():
    # Bounded, explicit pagination avoids loading an unbounded audit history.
    page = max(request.args.get('page', 1, type=int), 1)
    per_page = min(max(request.args.get('per_page', 25, type=int), 10), 100)
    total = query_db('SELECT COUNT(*) AS count FROM audit_records', one=True)['count']
    records = query_db(
        'SELECT * FROM audit_records ORDER BY record_id DESC LIMIT ? OFFSET ?',
        (per_page, (page - 1) * per_page),
    )
    for record in records:
        record['payload'] = json.loads(record['payload'])
    return render_template('audit/ledger.html', records=records, page=page, per_page=per_page, total=total)
