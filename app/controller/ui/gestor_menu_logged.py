from flask import Blueprint, render_template, session, redirect, url_for

def menu_logged_blueprint():
    bp = Blueprint('menu_logged', __name__)

    @bp.route('/menu_logged', methods=['GET'])
    def menu_logged():
        # Protección: solo usuarios logueados
        if "nickname" not in session:
            return redirect(url_for('users.login'))

        return render_template('menu_logged.html')

    return bp
