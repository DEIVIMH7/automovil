from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

def get_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='automovil2',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def welcome():
    return render_template('index.html')

@app.route('/clientes')
def clientes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cliente")
    clientes = cursor.fetchall()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/agregar_cliente', methods=['GET', 'POST'])
def agregar_cliente():
    if request.method == 'POST':
        nif = request.form['nif']
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO cliente (nif, nombre, direccion, telefono) VALUES (%s, %s, %s, %s)",
                           (nif, nombre, direccion, telefono))
            conn.commit()
        except pymysql.Error as e:
            print(f"Error al insertar cliente: {e}")
            conn.rollback() 
        finally:
            conn.close()
        return redirect(url_for('clientes'))
    return render_template('agregar_cliente.html')

@app.route('/editar_cliente/<int:nif>', methods=['GET', 'POST'])
def editar_cliente(nif):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        direccion = request.form['direccion']
        telefono = request.form['telefono']
        try:
            cursor.execute("UPDATE cliente SET nombre=%s, direccion=%s, telefono=%s WHERE nif=%s",
                           (nombre, direccion, telefono, nif))
            conn.commit()
        except pymysql.Error as e:
            print(f"Error al actualizar cliente: {e}")
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('clientes'))

    cursor.execute("SELECT * FROM cliente WHERE nif = %s", (nif,))
    cliente = cursor.fetchone()
    conn.close()
    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/eliminar_cliente/<int:nif>')
def eliminar_cliente(nif):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cliente WHERE nif = %s", (nif,))
        conn.commit()
    except pymysql.Error as e:
        print(f"Error al eliminar cliente: {e}")
        conn.rollback()
    finally:
        conn.close()
    return redirect(url_for('clientes'))

@app.route('/coches')
def coches():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT c.*, cl.nombre as nombre_cliente FROM coches c JOIN cliente cl ON c.nif_cliente = cl.nif")
    coches = cursor.fetchall()
    conn.close()
    return render_template('coches.html', coches=coches)

@app.route('/agregar_coche', methods=['GET', 'POST'])
def agregar_coche():
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        matricula = request.form['matricula']
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        precio = request.form['precio']
        nif_cliente = request.form['nif_cliente']
        sql = "INSERT INTO coches (matricula, marca, modelo, color, precio, nif_cliente) VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            cursor.execute(sql, (matricula, marca, modelo, color, precio, nif_cliente))
            conn.commit()
        except pymysql.Error as e:
            print(f"Error al insertar coche: {e}")
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('coches'))

    cursor.execute("SELECT nif, nombre FROM cliente")
    clientes = cursor.fetchall()
    conn.close()
    return render_template('agregar_coche.html', clientes=clientes)

@app.route('/editar_coche/<string:matricula>', methods=['GET', 'POST'])
def editar_coche(matricula):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        marca = request.form['marca']
        modelo = request.form['modelo']
        color = request.form['color']
        precio = request.form['precio']
        nif_cliente = request.form['nif_cliente']
        sql = "UPDATE coches SET marca=%s, modelo=%s, color=%s, precio=%s, nif_cliente=%s WHERE matricula=%s"
        try:
            cursor.execute(sql, (marca, modelo, color, precio, nif_cliente, matricula))
            conn.commit()
        except pymysql.Error as e:
            print(f"Error al actualizar coche: {e}")
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('coches'))

    cursor.execute("SELECT * FROM coches WHERE matricula = %s", (matricula,))
    coche = cursor.fetchone()

    cursor.execute("SELECT nif, nombre FROM cliente")
    clientes = cursor.fetchall()
    conn.close()

    return render_template('editar_coche.html', coche=coche, clientes=clientes)

@app.route('/eliminar_coche/<string:matricula>')
def eliminar_coche(matricula):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM coches WHERE matricula = %s", (matricula,))
        conn.commit()
    except pymysql.Error as e:
        print(f"Error al eliminar coche: {e}")
        conn.rollback()
    finally:
        conn.close()
    return redirect(url_for('coches'))

@app.route('/revisiones')
def revisiones():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, c.matricula, c.marca, c.modelo, cl.nombre as nombre_cliente
        FROM revisiones r
        JOIN coches c ON r.matricula_coche = c.matricula
        JOIN cliente cl ON c.nif_cliente = cl.nif
        ORDER BY r.fecha_revision DESC
    """)
    revisiones = cursor.fetchall()
    conn.close()
    return render_template('revisiones.html', revisiones=revisiones)

@app.route('/agregar_revision', methods=['GET', 'POST'])
def agregar_revision():
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        matricula_coche = request.form['matricula_coche']
        fecha_revision = request.form['fecha_revision']
        kilometraje = request.form['kilometraje']
        descripcion = request.form['descripcion']
        importe = request.form['importe']
        sql = "INSERT INTO revisiones (matricula_coche, fecha_revision, kilometraje, descripcion, importe) VALUES (%s, %s, %s, %s, %s)"
        try:
            cursor.execute(sql, (matricula_coche, fecha_revision, kilometraje, descripcion, importe))
            conn.commit()
        except pymysql.Error as e:
            print(f"Error al insertar revisión: {e}")
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('revisiones'))

    cursor.execute("SELECT matricula, marca, modelo FROM coches")
    coches = cursor.fetchall()
    conn.close()
    return render_template('agregar_revision.html', coches=coches)

@app.route('/editar_revision/<int:codigo>', methods=['GET', 'POST'])
def editar_revision(codigo):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        matricula_coche = request.form['matricula_coche']
        fecha_revision = request.form['fecha_revision']
        kilometraje = request.form['kilometraje']
        descripcion = request.form['descripcion']
        importe = request.form['importe']
        sql = "UPDATE revisiones SET matricula_coche=%s, fecha_revision=%s, kilometraje=%s, descripcion=%s, importe=%s WHERE codigo=%s"
        try:
            cursor.execute(sql, (matricula_coche, fecha_revision, kilometraje, descripcion, importe, codigo))
            conn.commit()
        except pymysql.Error as e:
            print(f"Error al actualizar revisión: {e}")
            conn.rollback()
        finally:
            conn.close()
        return redirect(url_for('revisiones'))

   
    cursor.execute("SELECT * FROM revisiones WHERE codigo = %s", (codigo,))
    revision = cursor.fetchone()

    cursor.execute("SELECT matricula, marca, modelo FROM coches")
    coches = cursor.fetchall()
    conn.close()

    return render_template('editar_revision.html', revision=revision, coches=coches)

@app.route('/eliminar_revision/<int:codigo>')
def eliminar_revision(codigo):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM revisiones WHERE codigo = %s", (codigo,))
        conn.commit()
    except pymysql.Error as e:
        print(f"Error al eliminar revisión: {e}")
        conn.rollback()
    finally:
        conn.close()
    return redirect(url_for('revisiones'))

if __name__ == '__main__':
    app.run(debug=True, port=5020)