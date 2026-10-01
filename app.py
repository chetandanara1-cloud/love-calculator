from flask import Flask, request, redirect, url_for, session, render_template_string
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# =========================
# SETTINGS
# =========================

app.secret_key = "CHANGE_THIS_SECRET_KEY_12345"

ADMIN_PASSWORD = "1234"

LINK_ID = "11187775"

DATABASE = "submissions.db"


# =========================
# DATABASE
# =========================

def init_db():
    conn = sqlite3.connect(DATABASE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name1 TEXT NOT NULL,
            name2 TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================
# LOVE SCORE
# =========================

def calculate_score(name1, name2):
    text = (name1 + name2).lower().replace(" ", "")

    total = sum(ord(char) for char in text)

    return 40 + (total % 61)


# =========================
# PUBLIC PAGE
# =========================

PUBLIC_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Love Calculator</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #ff416c, #ff4b2b);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .card {
            width: 100%;
            max-width: 430px;
            background: white;
            padding: 30px;
            border-radius: 22px;
            box-shadow: 0 15px 40px rgba(0,0,0,0.2);
            text-align: center;
        }

        h1 {
            margin-top: 0;
            color: #ff416c;
        }

        .heart {
            font-size: 55px;
            margin-bottom: 10px;
        }

        input {
            width: 100%;
            padding: 15px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 12px;
            font-size: 16px;
            outline: none;
        }

        input:focus {
            border-color: #ff416c;
        }

        button {
            width: 100%;
            padding: 15px;
            margin-top: 15px;
            border: none;
            border-radius: 12px;
            background: #ff416c;
            color: white;
            font-size: 17px;
            font-weight: bold;
            cursor: pointer;
        }

        button:hover {
            background: #e7355d;
        }

        .consent {
            text-align: left;
            font-size: 13px;
            color: #666;
            margin-top: 12px;
        }

        .consent input {
            width: auto;
            margin-right: 5px;
        }

        .result {
            margin-top: 25px;
            padding: 20px;
            background: #fff0f4;
            border-radius: 15px;
        }

        .score {
            font-size: 45px;
            font-weight: bold;
            color: #ff416c;
        }

        .small {
            color: #777;
            font-size: 13px;
            margin-top: 20px;
        }
    </style>
</head>

<body>

<div class="card">

    <div class="heart">❤️</div>

    <h1>Love Calculator</h1>

    <p>Enter two names to calculate the love percentage.</p>

    {% if result %}

        <div class="result">

            <h2>{{ name1 }} ❤️ {{ name2 }}</h2>

            <div class="score">
                {{ score }}%
            </div>

            <p>Love compatibility result</p>

        </div>

        <button onclick="window.location.href='/love/11187775'">
            Try Again
        </button>

    {% else %}

        <form method="POST">

            <input
                type="text"
                name="name1"
                placeholder="Enter first name"
                maxlength="50"
                required
            >

            <input
                type="text"
                name="name2"
                placeholder="Enter second name"
                maxlength="50"
                required
            >

            <div class="consent">
                <label>
                    <input type="checkbox" name="consent" required>
                    I agree that the submitted names may be stored and viewed by the site owner.
                </label>
            </div>

            <button type="submit">
                Calculate ❤️
            </button>

        </form>

    {% endif %}

    <div class="small">
        Love Calculator
    </div>

</div>

</body>
</html>
"""


@app.route("/")
def home():
    return redirect(url_for("love_page"))


@app.route("/love/11187775", methods=["GET", "POST"])
def love_page():

    if request.method == "POST":

        name1 = request.form.get("name1", "").strip()
        name2 = request.form.get("name2", "").strip()
        consent = request.form.get("consent")

        if not name1 or not name2 or not consent:
            return "Please fill all required fields.", 400

        if len(name1) > 50 or len(name2) > 50:
            return "Name is too long.", 400

        score = calculate_score(name1, name2)

        conn = sqlite3.connect(DATABASE)

        conn.execute(
            """
            INSERT INTO submissions
            (name1, name2, score, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                name1,
                name2,
                score,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        )

        conn.commit()
        conn.close()

        return render_template_string(
            PUBLIC_HTML,
            result=True,
            name1=name1,
            name2=name2,
            score=score
        )

    return render_template_string(
        PUBLIC_HTML,
        result=False
    )


# =========================
# ADMIN LOGIN
# =========================

ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Admin Login</title>

<style>

body {
    margin: 0;
    min-height: 100vh;
    background: #111;
    display: flex;
    justify-content: center;
    align-items: center;
    font-family: Arial;
    padding: 20px;
}

.box {
    background: white;
    width: 100%;
    max-width: 380px;
    padding: 30px;
    border-radius: 18px;
}

h1 {
    text-align: center;
}

input {
    width: 100%;
    padding: 14px;
    margin-top: 10px;
    box-sizing: border-box;
    border: 1px solid #ddd;
    border-radius: 10px;
}

button {
    width: 100%;
    margin-top: 15px;
    padding: 14px;
    border: 0;
    border-radius: 10px;
    background: #111;
    color: white;
    font-size: 16px;
}

.error {
    color: red;
    text-align: center;
}

</style>

</head>

<body>

<div class="box">

<h1>Admin Login</h1>

{% if error %}
<p class="error">Wrong password</p>
{% endif %}

<form method="POST">

<input
    type="password"
    name="password"
    placeholder="Admin password"
    required
>

<button type="submit">
Login
</button>

</form>

</div>

</body>
</html>
"""


@app.route("/admin", methods=["GET", "POST"])
def admin():

    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))

    error = False

    if request.method == "POST":

        password = request.form.get("password", "")

        if password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(url_for("dashboard"))

        error = True

    return render_template_string(
        ADMIN_LOGIN_HTML,
        error=error
    )


# =========================
# ADMIN DASHBOARD
# =========================

ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Admin Dashboard</title>

<style>

body {
    margin: 0;
    background: #f5f5f5;
    font-family: Arial;
    padding: 20px;
}

.container {
    max-width: 1000px;
    margin: auto;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.logout {
    background: #111;
    color: white;
    padding: 10px 15px;
    border-radius: 8px;
    text-decoration: none;
}

.link {
    background: white;
    padding: 15px;
    border-radius: 12px;
    margin: 20px 0;
    word-break: break-all;
}

table {
    width: 100%;
    background: white;
    border-collapse: collapse;
    border-radius: 12px;
    overflow: hidden;
}

th, td {
    padding: 14px;
    border-bottom: 1px solid #eee;
    text-align: left;
}

th {
    background: #111;
    color: white;
}

.delete {
    background: #e53935;
    color: white;
    padding: 7px 10px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}

.empty {
    background: white;
    padding: 30px;
    text-align: center;
    border-radius: 12px;
}

@media(max-width: 650px) {

    table {
        font-size: 13px;
    }

    th, td {
        padding: 9px 5px;
    }

    .hide-mobile {
        display: none;
    }

}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>Admin Dashboard</h1>

<a class="logout" href="/logout">
Logout
</a>

</div>

<div class="link">

<strong>Public Link:</strong><br>

{{ public_link }}

</div>

<h2>Total Submissions: {{ submissions|length }}</h2>

{% if submissions %}

<table>

<tr>
    <th>#</th>
    <th>Name 1</th>
    <th>Name 2</th>
    <th>Score</th>
    <th>Date</th>
    <th>Delete</th>
</tr>

{% for item in submissions %}

<tr>

<td>{{ item[0] }}</td>

<td>{{ item[1] }}</td>

<td>{{ item[2] }}</td>

<td>{{ item[3] }}%</td>

<td>{{ item[4] }}</td>

<td>

<form method="POST" action="/admin/delete/{{ item[0] }}">

<button class="delete" type="submit">
Delete
</button>

</form>

</td>

</tr>

{% endfor %}

</table>

{% else %}

<div class="empty">
No submissions yet.
</div>

{% endif %}

</div>

</body>
</html>
"""


@app.route("/dashboard")
def dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    conn = sqlite3.connect(DATABASE)

    submissions = conn.execute(
        """
        SELECT id, name1, name2, score, created_at
        FROM submissions
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    public_link = "/love/11187775"

    return render_template_string(
        ADMIN_HTML,
        submissions=submissions,
        public_link=public_link
    )


# =========================
# DELETE
# =========================

@app.route("/admin/delete/<int:item_id>", methods=["POST"])
def delete_submission(item_id):

    if not session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    conn = sqlite3.connect(DATABASE)

    conn.execute(
        "DELETE FROM submissions WHERE id = ?",
        (item_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("admin"))


# =========================
# START
# =========================

init_db()

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )