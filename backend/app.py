from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
# Importamos Error para capturar errores de MySQL específicos, incluyendo la conexión.
from pymysql import Error as PyMySQLError 

app = Flask(__name__)
# Permitir CORS para que el frontend (8080) pueda comunicarse con el backend (5000)
CORS(app, resources={r"/*": {"origins": "*"}}) 

def get_db():
    # Nota: host="db" es el nombre del servicio en docker-compose
    # Si la base de datos no está disponible, esta función lanzará un PyMySQLError
    return pymysql.connect(
        host="db",
        user="root",
        password="rootpassword",
        database="testdb",
        cursorclass=pymysql.cursors.DictCursor
    )

# ----------------------------------------------------
# ❌ RUTA VULNERABLE DE LOGIN (Con manejo de errores de DB)
# ----------------------------------------------------
@app.post("/vuln-login")
def vuln_login():
    data = request.json
    user = data.get("username", "")
    pw = data.get("password", "")

    # ❌ VULNERABLE SQL: Concatenación directa de input del usuario
    # El ataque de Login Bypass se realiza insertando ' OR '1'='1
    query = f"SELECT * FROM users WHERE username='{user}' AND password='{pw}'"

    try:
        # Intentar establecer conexión con la DB
        conn = get_db()
    except PyMySQLError as e:
        # 🚨 ERROR: No se pudo conectar a la base de datos
        print(f"DB Connection Error: {e}")
        # Devolver 500 para indicar un error interno del servidor
        return jsonify({"message": "ERROR: Falló la conexión con la base de datos."}), 500

    try:
        with conn.cursor() as cursor:
            # Ejecutar la consulta (puede fallar por inyección o sintaxis SQL)
            cursor.execute(query)
            result = cursor.fetchall()
    except PyMySQLError as e:
        # 🚨 ERROR: Falló la consulta SQL
        print(f"SQL Query Error: {e}")
        return jsonify({"message": f"ERROR SQL: La consulta falló (Revisar sintaxis o Inyección)"}), 500
    finally:
        # Asegurarse de cerrar la conexión
        conn.close()

    if len(result) > 0:
        return jsonify({"message": "Login successful (vulnerable)"})
    else:
        return jsonify({"message": "Login failed"})

# ----------------------------------------------------
# ❌ RUTA VULNERABLE DE BÚSQUEDA (Con manejo de errores de DB)
# ----------------------------------------------------
@app.get("/vuln-search")
def vuln_search():
    term = request.args.get("q", "")

    # ❌ VULNERABLE SQL: Concatenación directa de input del usuario
    # El ataque de Union-Based SQLi se realiza a través del parámetro 'term'
    query = f"SELECT * FROM products WHERE name LIKE '%{term}%'"

    try:
        # Intentar establecer conexión con la DB
        conn = get_db()
    except PyMySQLError as e:
        # 🚨 ERROR: No se pudo conectar a la base de datos
        print(f"DB Connection Error: {e}")
        return jsonify({"message": "ERROR: Falló la conexión con la base de datos."}), 500

    try:
        with conn.cursor() as cursor:
            # Ejecutar la consulta (puede fallar por inyección o sintaxis SQL)
            cursor.execute(query)
            results = cursor.fetchall()
    except PyMySQLError as e:
        # 🚨 ERROR: Falló la consulta SQL
        print(f"SQL Query Error: {e}")
        return jsonify({"message": f"ERROR SQL: La consulta falló (Revisar sintaxis o Inyección)"}), 500
    finally:
        # Asegurarse de cerrar la conexión
        conn.close()

    # Si no hay errores, devolver los resultados
    return jsonify(results)

# ----------------------------------------------------
# ✅ RUTA SEGURA DE LOGIN (Para comparación)
# ----------------------------------------------------
@app.post("/safe-login")
def safe_login():
    data = request.json
    user = data["username"]
    pw = data["password"]

    # ✅ SEGURO: Usando placeholders (%s)
    # La consulta se envía al motor de base de datos de forma separada de los datos
    query = "SELECT * FROM users WHERE username=%s AND password=%s"

    try:
        conn = get_db()
    except PyMySQLError as e:
        print(f"DB Connection Error: {e}")
        return jsonify({"message": "ERROR: Falló la conexión con la base de datos."}), 500

    try:
        with conn.cursor() as cursor:
            # ✅ SEGURO: El driver se encarga de escapar y parametrizar el input
            cursor.execute(query, (user, pw))
            result = cursor.fetchall()
    except PyMySQLError as e:
        print(f"SQL Query Error: {e}")
        return jsonify({"message": f"ERROR SQL: La consulta falló"}), 500
    finally:
        conn.close()

    if result:
        # Nota: En una aplicación real, no se devolvería el mensaje de "SAFE"
        return jsonify({"message": f"Login OK. Bienvenido, {user} (SAFE)."})
    return jsonify({"message": "Login fallido. Credenciales inválidas (SAFE)."})


# ----------------------------------------------------
# ✅ RUTA SEGURA DE BÚSQUEDA
# ----------------------------------------------------
@app.get("/safe-search")
def safe_search():
    term = request.args.get("q", "")
    
    # Prepara el término con wildcards para la cláusula LIKE
    # Se añade aquí, ANTES de pasar a la parametrización
    search_term_with_wildcards = f"%{term}%"

    # ✅ SEGURO: Usando placeholders (%s)
    query = "SELECT * FROM products WHERE name LIKE %s"

    try:
        conn = get_db()
    except PyMySQLError as e:
        print(f"DB Connection Error: {e}")
        return jsonify({"message": "ERROR: Falló la conexión con la base de datos."}), 500

    try:
        with conn.cursor() as cursor:
            # ✅ SEGURO: El driver se encarga de escapar y parametrizar la variable
            cursor.execute(query, (search_term_with_wildcards,))
            results = cursor.fetchall()
    except PyMySQLError as e:
        print(f"SQL Query Error: {e}")
        return jsonify({"message": f"ERROR SQL: La consulta falló"}), 500
    finally:
        conn.close()

    # Si no hay errores, devolver los resultados
    return jsonify(results)

if __name__ == "__main__":
    # Escuchar en todas las interfaces en el puerto 5000 para Docker
    app.run(host="0.0.0.0", port=5000)
