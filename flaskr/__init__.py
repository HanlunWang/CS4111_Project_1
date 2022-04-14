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


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True,template_folder=tmpl_dir)
    Uemail = ""

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

    @app.route('/navigation')
    def navigation():
        return render_template("navigation.html")

    @app.route('/navigation/user_info')
    def user_info():
        # username = request.form['name']
        # telephone = request.form['telephone']
        # memberStatus = request.form['memberStatus']
        # accountBalance = request.form['accountBalance']

        # engine.execute("INSERT INTO Users (name, telephone, memberStatusm accountBalance) VALUES (%s, %s, %b, %.2f) WHERE email = %s",
        #             (username, telephone, memberStatus, accountBalance, Uemail),)

        content = []
        cursor = g.conn.execute("SELECT name, telephone, memberStatus, accountBalance FROM Users WHERE email = %s", (Uemail),)
        for result in cursor:
            content.extend([result[0], result[1], result[2], result[3]])
        cursor.close()
        context = dict(data = content)

        return render_template("user_info.html", **context)
    
    @app.route('/navigation/pet_info')
    def pet_info():
        content = []
        cursor = g.conn.execute("SELECT Pets.name, Pets.ownerID, type, gender, age, dateOfBirth, weight, healthRecord, character, preference, price FROM Pets, Users WHERE email = %s", (Uemail),)
        for result in cursor:
            content.extend([result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7], result[8], result[9], result[10]])
        cursor.close()
        context = dict(data = content)

        return render_template("pet_info.html", **context)


    bp = Blueprint('auth', __name__)
    @app.route('/register', methods=['GET','POST'])
    def register():
        if request.method == 'POST':
            useremail = request.form['useremail']
            password = request.form['password']
            error = None

            if not useremail:
                error = 'Email is required.'
            elif not password:
                error = 'Password is required.'

            if error is None:
                user = engine.execute(
                    'SELECT * FROM Users WHERE email = %s', useremail
                ).fetchone()

                if user is None:
                    engine.execute(
                        "INSERT INTO Users (email, password) VALUES (%s, %s)",
                        (useremail, password),
                    )
                else:
                    raise ValueError(f"User {useremail} is already registered.")

                nonlocal Uemail
                Uemail = useremail
                return redirect(url_for("navigation"))

        return render_template("register.html")


    @app.route('/login', methods=['GET','POST'])
    def login():
        if request.method == 'POST':
            useremail = request.form['useremail']
            password = request.form['password']

            error = None
            user = g.conn.execute(
                'SELECT * FROM Users WHERE email = %s', useremail
            ).fetchone()

            if user is None:
                error = 'Incorrect email.'
            elif not user['password'] == password:
                error = 'Incorrect password.'

            if error is None:
                nonlocal  Uemail
                Uemail = useremail
                return redirect(url_for('navigation'))

        return render_template("login.html")

    @bp.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('index'))


    return app


if __name__ == "__main__":
    app = create_app()
    app.run()