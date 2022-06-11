from flask import Flask, render_template, request, redirect, url_for
from flask_login import login_required, LoginManager, UserMixin, login_user, logout_user, current_user
from database import Database
from password_hashing import create_hash

login_db = Database("login.db")  # login database for users and admins
default_db = Database("default.db")  # default database

app = Flask(__name__)
app.config["SECRET_KEY"] = "PlsDontDoThisToPythonHeIsYoungSnake"
login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id, username, password, permissions):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.permissions = permissions

    def has_permissions(self):
        return self.permissions

    def get_id(self):
        return self.user_id


@login_manager.user_loader
def load_user(user_id: int):
    user = login_db.query(f"SELECT * FROM users WHERE UserID={int(user_id)}")[0]
    return User(user[0], user[1], user[2], user[3])


@app.route("/", methods=["GET"])
def home() -> render_template:
    rows = default_db.query(Database.sql_cmd)
    ids = default_db.query("SELECT VulkanologID FROM vulkanolog")
    return render_template("index.html", rows=zip([x[0] for x in ids], rows))


@app.route("/login/", methods=["POST", "GET"])
def login() -> render_template:
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        in_db = login_db.query("SELECT UserID FROM users WHERE Username='{}' AND Password='{}'"
                               .format(username, create_hash(password)))
        if in_db:
            login_user(load_user(in_db[0][0]))
            return redirect(url_for("home"))
        else:
            return render_template("login.html", status_msg="Incorrect Username or Password :(</3")
    if current_user.get_id():
        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/register/", methods=["POST", "GET"])
def register() -> render_template:
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        in_db = login_db.query("SELECT * FROM users WHERE Username='{}'".format(username))

        if not in_db:
            login_db.query("INSERT INTO users (Username, Password, Permissions) VALUES ('{}', '{}', 0)"
                           .format(username, create_hash(password)))
            if not current_user.get_id():
                return redirect(url_for("login"))
            else:
                return redirect(url_for("home"))
        else:
            return render_template("register.html", status_msg="User Already Exists")
    return render_template("register.html")


@app.route("/dashboard/", methods=["POST", "GET"])
@login_required
def dashboard() -> render_template:
    if current_user.has_permissions():  # check permissions if admin >> load | else >> redirect
        if request.method == "POST":
            sql_command = request.form["command"]
            default_db.query(sql_command)
        return render_template("dashboard.html")
    return redirect(url_for("home"))


@app.route("/logout/", methods=["POST", "GET"])
@login_required
def logout() -> redirect:
    logout_user()
    return redirect(url_for("login"))


@app.route("/insert/", methods=["POST", "GET"])
@login_required
def insert():
    if request.method == "POST":
        default_db.query(
            "INSERT INTO vulkanolog (VulkanologID, FirstName, LastName, AddressID, BirthdateID, GenderID) VALUES ({}, '{}', '{}', {}, {}, {})".format(
                *request.form.values()))
        return redirect(url_for("home"))
    columns = default_db.query("SELECT name FROM PRAGMA_TABLE_INFO('vulkanolog')")
    print(columns)
    return render_template("insert.html", column_count=enumerate(columns))


@app.route("/edit/<row_id>/", methods=["POST", "GET"])
@login_required
def edit(row_id: int) -> render_template:
    if request.method == "POST":
        default_db.query(
            "UPDATE vulkanolog SET VulkanologID={}, FirstName='{}', LastName='{}', AddressID={}, BirthdateID={}, GenderID={} WHERE VulkanologID={}"
                .format(*request.form.values(), request.form.get("data_0")))

    if current_user.has_permissions():
        columns = default_db.query("SELECT * FROM vulkanolog WHERE VulkanologID={}".format(row_id))
        return render_template("edit.html", row_id=row_id, columns=enumerate(columns[0]))
    return redirect(url_for("home"))


@app.route("/delete/<row_id>/", methods=["POST", "GET"])
@login_required
def delete(row_id: int) -> redirect:
    default_db.query("DELETE FROM vulkanolog WHERE VulkanologID={}".format(row_id))
    return redirect(url_for("home"))


# {{ variable_name }}                                               # variable
# {% for _ in range(...) %} code{{_}}... {% endfor %}               # for loop
# {% if condition %} code ...{% endif %}                            # if
# {% if condition %} code... {% else %} code... {% endif %}         # if else
# {% block block_name%} code... {% endblock %}                      # block of code
# {% endtends "...hmtl" %}                                          # inheritance
if __name__ == '__main__':
    app.run()
