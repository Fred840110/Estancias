from flask import Flask, render_template, request, redirect, url_for, session, json, jsonify, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import random
import bcrypt
import os
from dotenv import load_dotenv
import smtplib
from datetime import datetime

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
meses = {
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12
}

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
        # Obtener datos del formulario
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

        try:
            mes_numerico = obtnener_mes_numerico(mes)
            fecha_nacimiento = datetime(int(anio), mes_numerico, int(dia_nac))
        except ValueError as e:
            flash('Por favor, introduce una fecha de nacimiento válida', 'danger')
            return redirect(url_for('registro'))

        # Verificar si el correo electrónico ya está registrado
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        existing_user = cur.fetchone()
        cur.close()

        if existing_user:
            flash('Este correo electrónico ya está registrado. Por favor, inicia sesión o utiliza otro correo electrónico.', 'danger')
            return redirect(url_for('registro'))

        # Verificar si las contraseñas coinciden
        if contrasena != conf_contrasena:
            flash('Las contraseñas no coinciden. Por favor, inténtalo de nuevo.', 'danger')
            return redirect(url_for('registro'))

        # Encriptar la contraseña antes de almacenarla en la base de datos
        password_encriptado = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())

        # Insertar usuario en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO usuario(nombre, email, telefono, direccion, ap_paterno, ap_materno, contrasena, ocupacion, fecha_nac, rol) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (nombre, email, tel, direccion, ap_paterno, ap_materno, password_encriptado, ocupacion, fecha_nacimiento, 'usuario'))
        mysql.connection.commit()
        cur.close()

        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('index'))
    
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuario WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        if user:
            if bcrypt.checkpw(contrasena.encode('utf-8'), user[7].encode('utf-8')):  # Reemplaza 7 con el índice de la columna 'contrasena'
                session['id_usuario'] = user[0]  # Índice 0 para la columna 'id_usuario'
                session['nombre'] = user[1]      # Índice 1 para la columna 'nombre'
                session['apellido_paterno'] = user[5]  # Índice 5 para la columna 'ap_paterno'
                session['apellido_materno'] = user[6]  # Índice 6 para la columna 'ap_materno'
                flash('¡Inicio de sesión exitoso!', 'success')
                return redirect(url_for('panel_inicio'))
            else:
                flash('¡Contraseña incorrecta!', 'error')
                return redirect(url_for('index'))
        else:
            flash('¡Email no encontrado!', 'error')
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/panel_inicio')
def panel_inicio():
    if 'id_usuario' in session:
        id_usuario = session['id_usuario']
        nombre = session['nombre']
        apellido_paterno = session['apellido_paterno']
        apellido_materno = session['apellido_materno']
        print(f"id_usuario---> {id_usuario}")
        return render_template("panel_inicio.html", datos_usuario={'id': id_usuario, 'nombre': nombre, 'apellido_paterno': apellido_paterno, 'apellido_materno': apellido_materno})
    else:
        flash('¡Por favor inicia sesión para acceder al panel de inicio!', 'error')
        return redirect(url_for('index'))
    
@app.route('/cuestionarioTres')
def cuestionarioTres():

    return render_template('custionario.html')
    
@app.route('/analisis', methods=['POST'])
def analisis():
    if request.method == 'POST':
        # Obtenemos los valores de las preguntas del formulario
        preguntas = {}
        for i in range(1, 73):
            pregunta = 'q' + str(i)
            valor = request.form[pregunta]
            preguntas[pregunta] = int(valor) if valor.isdigit() else None
            print(pregunta, ':', preguntas[pregunta])  # Imprimir los valores de las preguntas en consola
        
        # Insertamos los datos en la base de datos
        try:
            cursor = mysql.connection.cursor()
            id_usuario = session['id_usuario']
            cursor.execute(
                """INSERT INTO cuestionario_3 (id_usuario,
                p_1, p_2, p_3, p_4, p_5, p_6, p_7, p_8, p_9, p_10,
                p_11, p_12, p_13, p_14, p_15, p_16, p_17, p_18, p_19, p_20,
                p_21, p_22, p_23, p_24, p_25, p_26, p_27, p_28, p_29, p_30,
                p_31, p_32, p_33, p_34, p_35, p_36, p_37, p_38, p_39, p_40,
                p_41, p_42, p_43, p_44, p_45, p_46, p_47, p_48, p_49, p_50,
                p_51, p_52, p_53, p_54, p_55, p_56, p_57, p_58, p_59, p_60,
                p_61, p_62, p_63, p_64, p_65, p_66, p_67, p_68, p_69, p_70,
                p_71, p_72) VALUES(
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                %s,%s,%s)""",
                (id_usuario, preguntas['q1'], preguntas['q2'], preguntas['q3'], preguntas['q4'], preguntas['q5'], preguntas['q6'],
                preguntas['q7'], preguntas['q8'], preguntas['q9'], preguntas['q10'], preguntas['q11'], preguntas['q12'],
                preguntas['q13'], preguntas['q14'], preguntas['q15'], preguntas['q16'], preguntas['q17'], preguntas['q18'],
                preguntas['q19'], preguntas['q20'], preguntas['q21'], preguntas['q22'], preguntas['q23'], preguntas['q24'],
                preguntas['q25'], preguntas['q26'], preguntas['q27'], preguntas['q28'], preguntas['q29'], preguntas['q30'],
                preguntas['q31'], preguntas['q32'], preguntas['q33'], preguntas['q34'], preguntas['q35'], preguntas['q36'],
                preguntas['q37'], preguntas['q38'], preguntas['q39'], preguntas['q40'], preguntas['q41'], preguntas['q42'],
                preguntas['q43'], preguntas['q44'], preguntas['q45'], preguntas['q46'], preguntas['q47'], preguntas['q48'],
                preguntas['q49'], preguntas['q50'], preguntas['q51'], preguntas['q52'], preguntas['q53'], preguntas['q54'],
                preguntas['q55'], preguntas['q56'], preguntas['q57'], preguntas['q58'], preguntas['q59'], preguntas['q60'],
                preguntas['q61'], preguntas['q62'], preguntas['q63'], preguntas['q64'], preguntas['q65'], preguntas['q66'],
                preguntas['q67'], preguntas['q68'], preguntas['q69'], preguntas['q70'], preguntas['q71'], preguntas['q72'])
            )
            mysql.connection.commit()
            cursor.close()
            print('Respuestas almacenadas correctamente', 'success')
            return redirect(url_for('panel_inicio'))
        except Exception as e:
            print('Error al procesar las respuestas', 'danger')
            print(str(e))
            return redirect(url_for('panel_inicio'))



# Función de verificación de credenciales para el login 
def verificar_credenciales(email, contrasena):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT contrasena FROM usuario WHERE email = %s", (email,))
    resultado = cursor.fetchone()
    cursor.close()

    if resultado:
        hashed_password = resultado[0].encode('utf-8')
        if bcrypt.checkpw(contrasena.encode('utf-8'), hashed_password):
            return True
    return False

# Función de mes numerico
def obtnener_mes_numerico(nombre_mes):
    mes_numerico = meses.get(nombre_mes.lower())
    if mes_numerico is None:
        raise ValueError("Nombre de mes no es válido")
    return mes_numerico



if __name__ == '__main__':
    app.run(debug=True, port=5000)
