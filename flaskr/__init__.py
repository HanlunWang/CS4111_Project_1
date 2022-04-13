import os
from flask import Flask, abort, request, render_template, g, redirect, Response, Blueprint, url_for, session, flash
import functools
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from werkzeug.security import check_password_hash, generate_password_hash


DB_USER = "hw2839"
DB_PASSWORD = "2691"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

engine = create_engine(DATABASEURI)

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

def get_db():
    return g.db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,template_folder=tmpl_dir)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.before_request
    def before_request():
        try:
            g.conn = engine.connect()
        except:
            print("uh oh, problem connecting to database")
            import traceback; traceback.print_exc()
            g.conn = None

    @app.teardown_request
    def teardown_request(exception):
        try:
            g.conn.close()
        except Exception as e:
            pass

    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/products')
    def products():
        return render_template("products.html")

    @app.route('/cart')
    def cart():
        return render_template("cart.html")

    @app.route('/appointment')
    def appointment():
        return render_template("appointment.html")

    @app.route('/information')
    def information():
        return render_template("information.html")


    bp = Blueprint('auth', __name__)



    @app.route('/register', methods=['GET','POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            error = None

            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'

            if error is None:
                uname = engine.execute(
                    'SELECT * FROM Users WHERE name = %s', username
                ).fetchone()

                if uname is None:
                    engine.execute(
                        "INSERT INTO Users (name, password) VALUES (%s, %s)",
                        (username, password),
                    )
                else:
                    raise ValueError(f"User {username} is already registered.")

                return redirect(url_for("information"))

        return render_template("register.html")


    @app.route('/login', methods=['GET','POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            error = None
            user = g.conn.execute(
                'SELECT * FROM Users WHERE name = %s', username
            ).fetchone()

            if user is None:
                error = 'Incorrect username.'
            elif not user['password'] == password:
                error = 'Incorrect password.'

            if error is None:
                return redirect(url_for('information'))

        return render_template("login.html")

    @bp.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))

    def login_required(view):
        @functools.wraps(view)
        def wrapped_view(**kwargs):
            if g.user is None:
                return redirect(url_for('auth.login'))

            return view(**kwargs)

        return wrapped_view



    return app


