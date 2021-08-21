from flask import Flask, render_template, request, session, flash, url_for, redirect
from claseBaseDeDatos import ConexionDB
from encriptador import encriptar
from werkzeug.utils import secure_filename
from datetime import date
from datetime import datetime
import os
app = Flask(__name__)
app.secret_key = 'ingrese_un_valor_secreto_aca'
app.config['UPLOAD_PATH'] = 'static/uploads/'

@app.route('/')
def hello_world():
    try:

        crear_tabla()
    except Exception as e:
        print(f'tabla ya creada: {e}')
    try:
        crear_tabla_imagenes()
    except Exception as e:
        print(f'tabla ya creada: {e}')
    return render_template('index.html')


@app.route('/contenido')
def contenido():
    return render_template('contenido.html')


@app.route('/escenarios')
def escenarios():
    return render_template('escenarios.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        email = request.form['email']
        contra = encriptar(request.form['contra'])
        conexion = ConexionDB()
        try:
            cur = conexion.cursor
            cur.execute('SELECT username FROM usuarios')
            datos = conexion.cursor.fetchall()
            datos = [x[0] for x in datos]
            if username in datos:
                conexion.cerrar()
                flash('Nombre de usuario no disponible, intente con otro nombre.', 'error')
                return render_template('registro.html')
            elif len(username) ==0 or len(username) ==0 or len(apellidos)==0 or len(email) ==0 or len(contra) == 0:
                conexion.cerrar()
                flash('Rellene todos los campos para el registro.')
                return render_template('registro.html')
            else:
                cur.execute('INSERT INTO usuarios (username, nombres, apellidos, email, contra) VALUES (?,?,?,?,?)',(username,nombres,apellidos,email,contra))
                conexion.cerrar()
                flash('Registro exitoso, ya puede iniciar sesión.', 'error')
                return render_template('registro.html')
        except Exception as e:
            print(f'Ocurrió {e}')
            conexion.cerrar()
    return render_template('registro.html')

@app.route('/comunidad')
def comunidad():
    uploads = ''
    try:
        conexion = ConexionDB()
        cur = conexion.cursor
        cur.execute('SELECT * FROM imagenes')
        datos = cur.fetchall()
        datos.reverse()
        uploads = datos
        conexion.cerrar()
    except Exception as e:
        print(f'Error en comunidad: {e}')
        return render_template('comunidad.html', uploads=uploads)
    return render_template('comunidad.html', uploads=uploads)

@app.route('/upload', methods = ['GET', 'POST'])
def upload():
    try:
        if request.method == 'POST':
            today = date.today()
            now = datetime.now()
            f = request.files['file']
            username = session['username']
            filename = secure_filename(f.filename)
            descripcion = request.form['descripcion']
            fecha = f'Fecha: {today.day}/{today.month}/{today.year}  Hora:{now.hour}:{now.minute}'
            f.save(os.path.join(app.config['UPLOAD_PATH'],filename))
            print(os.path)
            try:
                conexion = ConexionDB()
                cur = conexion.cursor
                cur.execute('INSERT INTO imagenes (username, direccion, descripcion, fecha) VALUES (?,?,?,?)',(username, filename, descripcion, fecha))
                conexion.cerrar()
            except Exception as e:
                print(f'Error: {e}')
            return redirect(url_for('comunidad'))
        return 'algo anda fallando'
    except Exception as e:
        print(f'Error en upload: {e}')
        return redirect(url_for('hello_world'))

@app.route('/descargar/')
def descargar():
    return render_template('descargar.html')

@app.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    if request.method=='POST':
        usuario = request.form['username']
        contra = encriptar(request.form['contra'])
        try:
            conexion = ConexionDB()
            cur = conexion.cursor
            cur.execute('SELECT username, contra FROM usuarios')
            datos = conexion.cursor.fetchall()
            conexion.cerrar()
            if (usuario,contra) in datos:
                session['username'] = usuario
                flash('Inicio de sesión exitoso.')
                return render_template('index.html')
            else:
                flash('Usuario o contraseña invalidos, intenta otra vez', 'error')
                return render_template('iniciar_sesion.html')
        except Exception as e:
            print(f"acaba de ocurrir: {e}")
    return render_template('iniciar_sesion.html')

@app.route('/verificar_sesion')
def verificar_sesion():
    if len(session)!=0:
        return 'Te encuentras en sesion'
    return f'No te encuentras en sesion'

@app.route('/perfil', methods=['GET', 'POST'])
def perfil():
    if request.method == 'POST':
        usuario = session['username']
        nombres = request.form['nombres']
        apellidos = request.form['apellidos']
        email = request.form['email']
        contra = encriptar(request.form['password'])
        try:
            conexion = ConexionDB()
            cur = conexion.cursor
            cur.execute('SELECT username, contra FROM usuarios')
            datos = conexion.cursor.fetchall()
            conexion.cerrar()
            if (usuario,contra) in datos:
                conexion = ConexionDB()
                cur = conexion.cursor
                flash('Datos modificados exitosamente.')
                cur.execute(f'UPDATE usuarios set nombres = "{nombres}", apellidos= "{apellidos}", email = "{email}" WHERE username = "{usuario}" ')
                conexion.cerrar()
                return render_template('perfil.html', username=usuario, nombres=nombres, apellidos=apellidos,email=email)

            else:
                flash('Contraseña incorrecta, intente otra vez', 'error')
                return render_template('perfil.html', username= usuario, nombres=nombres, apellidos=apellidos, email=email)
        except Exception as e:
            print(f"acaba de ocurrir xD: {e}")
        return render_template('perfil.html', username= usuario, nombres=nombres, apellidos=apellidos, email=email)
    else:
        username = session['username']
        datos = []
        try:
            conexion = ConexionDB()
            cur = conexion.cursor
            cur.execute(f'SELECT username,nombres, apellidos, email from usuarios where username = "{username}"')
            datos = conexion.cursor.fetchall()
            datos = datos[0]
            conexion.cerrar()
        except Exception as e:
            print(f'Ocurre {e}')
        username = datos[0]
        nombres = datos[1]
        apellidos = datos[2]
        email = datos[3]
        return render_template('perfil.html', username = username, nombres = nombres, apellidos = apellidos, email = email)



@app.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()
    return render_template('index.html')

@app.route('/prueba')
def prueba():
    return render_template('prueba.html')

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template(f'404.html {e}')


# Definicion de funciones encargadas del SCRUM de nuestra base de datos
def crear_tabla():
    conexion = ConexionDB()
    sql = '''
    CREATE TABLE usuarios(
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(100),
        nombres VARCHAR(100),
        apellidos VARCHAR(100),
        email VARCHAR(100),
        contra VARCHAR(10)
    )
    '''
    conexion.cursor.execute(sql)
    conexion.cerrar()



def borrar_tabla():
    conexion = ConexionDB()
    sql = 'DROP TABLE usuarios'
    conexion.cursor.execute(sql)
    conexion.cerrar()


def lectura_base_datos():
    conexion = ConexionDB()
    conexion.cursor.execute('SELECT username, contra FROM usuarios')
    usuarios = conexion.cursor.fetchall()
    conexion.cerrar()
    print(usuarios)

def crear_tabla_imagenes():
    conexion = ConexionDB()
    sql = '''
        CREATE TABLE imagenes(
            id_imagen INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(100),		
            direccion VARCHAR(200),
            descripcion VARCHAR(200),
            fecha VARCHAR(100)
        )
        '''
    conexion.cursor.execute(sql)
    conexion.cerrar()

def borrar_tabla_imagenes():
    conexion = ConexionDB()
    sql = 'DROP TABLE imagenes'
    conexion.cursor.execute(sql)
    conexion.cerrar()

