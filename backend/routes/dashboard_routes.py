from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__)

# ------------------ HELPER FUNCTION ------------------

def is_authorized(role):
    user_id = session.get('user_id')
    user_role = session.get('role')
    return user_id and user_role == role


# ------------------ CANDIDATE DASHBOARD ------------------

@dashboard_bp.route('/candidate-dashboard')
def candidate_dashboard():
    if not is_authorized('candidate'):
        return redirect(url_for('auth.login'))

    return render_template('candidate_dashboard.html')


# ------------------ EMPLOYER DASHBOARD ------------------

@dashboard_bp.route('/employer-dashboard')
def employer_dashboard():
    if not is_authorized('employer'):
        return redirect(url_for('auth.login'))

    return render_template('employer_dashboard.html')