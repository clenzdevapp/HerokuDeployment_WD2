### Imports
import uuid
import hashlib
import re

from flask import Flask, render_template, request, redirect, url_for, make_response
from models import CompetitionUser, User, db

app = Flask(__name__)
db.create_all()  #  0) DATENBANKTABELLEN WERDEN ERSCHAFFEN <=> CREATE

### Global Functions
def getUser():
    session_token = request.cookies.get("session_token")

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
    else:
        user = None

    return user

def setCookieAndWriteToDb(user, redirectTo):
    # save the user object into a database
    session_token = str(uuid.uuid4())
    user.session_token = session_token
    db.add(user)  # 3) DAS OBJEKT CompetitionUser WIRD IN DIE DATENBANK EINGEFÜGT <=> UPDATE
    db.commit()  # 4) AUSFÜHRUNG DER DATENBANKOPERATION

    response = make_response(redirect(url_for(redirectTo)))
    response.set_cookie("session_token", session_token, httponly=True, samesite='Strict')

    return response


### Routes

# Home
@app.route( "/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        user = getUser()
        return render_template("index.html", user=user)
    elif request.method == "POST":
        name = request.form.get("name")
        mail = request.form.get("mail")
        songtitle = request.form.get("songtitle")

        # 2) DAS OBJEKT CompetitionUser WIRD MIT DEN WERTEN ERSTELLT, DIE IN DAS FORMULAR EINGEGEBEN WURDEN
        competitionUser = CompetitionUser(name=name,
                    email=mail,
                    songtitle=songtitle)

        # save the user object into a database
        db.add(competitionUser)  # 3) DAS OBJEKT CompetitionUser WIRD IN DIE DATENBANK EINGEFÜGT <=> UPDATE
        db.commit()  # 4) AUSFÜHRUNG DER DATENBANKOPERATION

        response = make_response(redirect(url_for('competitionsuccess')))

        return response


# Competition Form success
@app.route("/cometition-success")
def competitionsuccess():
    return render_template("competition-success.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    user = getUser() 
    if request.method == "GET":
        return render_template("registration.html", user=user)
    elif request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        mail = request.form.get("email")
        password = request.form.get("password")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        if not EMAIL_REGEX.match(mail):
            error = "email"
            response = make_response(redirect(url_for("failedregister", error=error)))
        else:
            user = User(username=username,
                        name=name,
                        email=mail,
                        password=hashed_password)

            response = setCookieAndWriteToDb(user, "successregister")

        return response

@app.route("/failed-register")
def failedregister():
    user = getUser()
    return render_template("registration-failed.html")

@app.route("/success-register")
def successregister():
    user = getUser()
    return render_template("success-registration.html", user=user)


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(username=username, password=hashed_password).first()

        if user == None:
            response = make_response(redirect(url_for('loginfailed')))
        else:
            response = setCookieAndWriteToDb(user, "loginsuccess")

        return response

@app.route("/login-success")
def loginsuccess():
    user = getUser()
    return render_template("login-success.html", user=user)

@app.route("/login-failed")
def loginfailed():
    return render_template("login-failed.html")


# Profil
@app.route("/profile")
def profil():
    user = getUser()
    return render_template("profile.html", user=user)

@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:  # if user is found
            return render_template("profile_edit.html", user=user)
    elif request.method == "POST":
        username = request.form.get("username")
        name = request.form.get("name")
        email = request.form.get("email")

        # update the user object
        user.username = username
        user.name = name
        user.email = email

        # store changes into the database
        db.add(user)
        db.commit()

        return redirect(url_for("profil"))


# Logout
@app.route("/logout", methods=["GET"])
def logout():
    session_token = request.cookies.get("session_token")
    new_session_token = ""

    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()

        # save the session token in a database
        user.session_token = new_session_token
        db.add(user)
        db.commit()

        # save user's session token into a cookie
        response = make_response(redirect(url_for('index')))
        response.set_cookie("session_token", new_session_token, httponly=True, samesite='Strict', expires=0)

        return response

#Imprint
@app.route("/impressum")
def impressum():
    return render_template("impressum.html")

### App call
if __name__ == '__main__':
    app.run()