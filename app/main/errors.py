from flask import render_template, request, jsonify
from . import main  # import blueprinta

# Obsługa błędów 404 - Nie znaleziono
@main.app_errorhandler(404)
def not_found_error(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404

# Obsługa błędów 500 - Błąd serwera
@main.app_errorhandler(500)
def internal_error(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response
    return render_template('errors/500.html'), 500

# Obsługa błędów 403 - Zabronione
@main.app_errorhandler(403)
def forbidden_error(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Forbidden'})
        response.status_code = 403
        return response
    return render_template('errors/403.html'), 403

# Obsługa błędów 401 - Nieautoryzowany
@main.app_errorhandler(401)
def unauthorized_error(error):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    return render_template('errors/401.html'), 401