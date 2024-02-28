from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import random
import bcrypt
import os
from dotenv import load_dotenv
import ssl
import smtplib

password = os.getenv("PASSWORD")
mysql_password = os.getenv("PASSWORD_MYSQL")


app = Flask(__name__)
app.secret_key = 'secretKey'

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'estancia_upq'

mysql = MySQL(app)

# Configuración del correo para el envío de la confirmación
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "fred.urbina1984@gmail.com"
app.config['MAIL_PASSWORD'] = password

mail = Mail(app)


# Función para convertir resultados de consulta a diccionarios
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


# Configurar el row factory antes de cada petición
@app.before_request
def configure_row_factory():
    mysql.connection.cursor().row_factory = dict_factory


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/registro.html')
def registro():
    return render_template('registro.html')


@app.route('/enviar_correo', methods=['POST'])
def enviar_correo():
    if request.method == 'POST':
        nombre = request.form['nombre']
        ap_paterno = request.form['apellido_paterno']
        ap_materno = request.form['apellido_materno']
        ocupacion = request.form['ocupacion']
        email = request.form['correo']
        tel = request.form['telefono']
        direccion = request.form['direccion']
        mes = request.form['fecha_nacimiento_mes']
        dia_nac = request.form['fecha_nacimiento_dia']
        anio = request.form['fecha_nacimiento_anio']
        contrasena = request.form['contrasena']
        conf_contrasena = request.form['conf_password']

        # Verificar si las contraseñas coinciden
        if contrasena != conf_contrasena:
            flash('Las contraseñas no coinciden, Por favor, inténtalo de nuevo', 'warning')
            return redirect(url_for('registro'))

        # Encriptar la contraseña antes de almacenarla en la base de datos
        password_encriptado = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario(nombre, email, telefono, direccion, ap_paterno, ap_materno, contrasena, ocupacion, dia_cumple, mes_cumple, ano_nac) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (nombre, email, tel, direccion, ap_paterno, ap_materno, password_encriptado, ocupacion, dia_nac, mes, anio))
        mysql.connection.commit()
        cur.close()

        # Generar un número de confirmación para los datos para enviar por correo
        numero_de_confirmacion = ''.join(random.choices('0123456789', k=6))

        # Almacenar el número de confirmación en la sesión
        session['numero_de_confirmacion'] = numero_de_confirmacion

        # Construir el mensaje de correo electrónico
        msj = Message('CONFIRMACION DE REGISTRO', sender='fred.urbina1984@gamil.com', recipients=[email])
        msj.body = f'Hola, por favor haz click en el siguiente para confirmar tu registro: {url_for("confirmar_registro", numero_confirmacion=numero_de_confirmacion, _external=True)}'
        print(password)
        mail.send(msj)

        flash('Se ha enviado un correo de confirmación. Por favor, revisa tu bandeja de entrada.', 'success')
        return redirect(url_for('index'))


@app.route('/confirmar_registro', methods=['GET'])
def confirmar_registro():
    numero_confirmacion = session.get('numero_de_confirmacion')

    if numero_confirmacion:
        numero_confirmacion_confirmacion = request.args.get('numero_confirmacion')

        if numero_confirmacion_confirmacion == numero_confirmacion:
            flash('¡Registro confirmado con éxito!', 'success')
            return redirect(url_for('index'))

    flash('Error al confirmar el registro. Por favor intentalo nuevamente', 'error')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
