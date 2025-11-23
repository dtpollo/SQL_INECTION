from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

def get_db():
    return pymysql.connect(
        host="db",
        user="root",
        password="rootpassword",
        database="testdb",
        cursorclass=pymysql.cursors.DictCursor
    )

# -------------------------
# VULNERABLE LOGIN
# -------------------------
@app.post("/vuln-login")
def vuln_login():
    data = request.json
    user = data.get("username", "")
    pw = data.get("password", "")

    # ❌ VULNERABLE SQL — concatenation
    query = f"SELECT * FROM users WHERE username='{user}' AND password='{pw}'"

    conn = get_db()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

    if len(result) > 0:
        return jsonify({"message": "Login successful (vulnerable)"})
    else:
        return jsonify({"message": "Login failed"})

# -------------------------
# VULNERABLE SEARCH
# -------------------------
@app.get("/vuln-search")
def vuln_search():
    term = request.args.get("q", "")

    # ❌ VULNERABLE SQL
    query = f"SELECT * FROM products WHERE name LIKE '%{term}%'"

    conn = get_db()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

    return jsonify(results)


# -------------------------
# SAFE VERSIONS (OPTIONAL)
# For mitigation section
# -------------------------
@app.post("/safe-login")
def safe_login():
    data = request.json
    user = data["username"]
    pw = data["password"]

    query = "SELECT * FROM users WHERE username=%s AND password=%s"

    conn = get_db()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (user, pw))
            result = cursor.fetchall()

    if result:
        return jsonify({"message": "Login OK (safe)"})
    return jsonify({"message": "Login failed"})

@app.get("/safe-search")
def safe_search():
    term = request.args.get("q", "")
    query = "SELECT * FROM products WHERE name LIKE %s"

    conn = get_db()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (f"%{term}%",))
            results = cursor.fetchall()

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

