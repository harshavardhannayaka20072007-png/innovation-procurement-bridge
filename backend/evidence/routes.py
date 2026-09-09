import os

from flask import Blueprint, abort, send_from_directory, session
from werkzeug.utils import secure_filename

from backend.auth.session import require_roles
from config import Config

evidence_bp = Blueprint('evidence', __name__)


@evidence_bp.route('/<path:evidence_file>')
@require_roles('government', 'startup', 'evaluator', 'admin')
def view_evidence(evidence_file):
    """Serve a stored evidence file only by its safe, flat file name."""
    filename = secure_filename(os.path.basename(evidence_file))
    if not filename:
        abort(404)
    evidence_dir = os.path.join(Config.UPLOAD_FOLDER, 'evidence')
    if not os.path.isfile(os.path.join(evidence_dir, filename)):
        abort(404)
    mimetype = 'application/pdf' if filename.lower().endswith('.pdf') else None
    return send_from_directory(evidence_dir, filename, as_attachment=False, mimetype=mimetype)
