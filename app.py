from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_mail import Mail, Message
import random
import bcrypt

app = Flask(__name__)
app.secret_key = 'secretKey'

# -> Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB']= 'estancia_upq'

mysql = MySQL(app)
#definimos una funcion para el manejo de tupla a diccionario
#----------------------------------------------------------------------------------------------------
def dict_factory(cursor,row):
    d ={}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
        return d
#----------------------------------------------------------------------------------------------------
@app.before_request
def configure_row_factory():
    mysql.connection.cursor().row_factory = dict_factory

#---------------------------------------------------------------------------------------------------- 

# -> configuracion del correo para el envio de la confirmacion

app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= '587'
app.config['MAIL_USE_TLS']='True'
app.config['MAIL_USERNAME']= '4dm1n1str4d0r.upq.encuesta.2024@gmail.com'
app.config['MAIL_SERVER']= 'encuesta_2024_estadia'

mail = Mail(app)

@app.route('/')
def index():
    
    return render_template ('index.html')
@app.route('/registro.html')
def resgistro():
    return render_template('registro.html')

@app.route('/enviar_correo',methods=['GET','POST'])
def registro():
    
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

        dicc = {'nombre':nombre,
                'apellidoPaterno':ap_paterno,
                'appeliidoMaterno':ap_materno,
                'ocupacion':ocupacion,
                'email':email,
                'telefono':tel,
                'direccion': direccion,
                'mes':mes,
                'diaNaciemiento': dia_nac,
                'anio': anio
                }
        

    # -> VERIFICAMOS SI LAS CONTRASEÑAS COINCIDEN

    if contrasena != conf_contrasena:
        flash('Las contraseñas no coinciden, Por favor, inténtalo de nuevo', 'warning')
        return redirect(url_for('registro'))

    # ->encriptamos la contraseña antes de almacenarla en base de datos

    password_encriptado = bcrypt.hashpw(contrasena.encode('utf-8'),bcrypt.gensalt())
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuario(nombre, email, telefono, direccion, ap_paterno, ap_materno, contrasena, ocupacion, dia_cumple, mes_cumple, ano_nac) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (nombre, email, tel, direccion, ap_paterno, ap_materno, contrasena, ocupacion, dia_nac, mes, anio))
    mysql.connection.commit()
    cur.close()

    # ->Generamos un numero de confirmacion para los datos para enviar por correo

    numeroDeConfirmacion = ''.join(random.choices('0123456789', k=6))


    #-> Almacenamos el numero de session en la 




'''@app.route('/enviar_correo',methods=['GET','POST'])
def enviar_correo ():
    if request.method == 'POST':
        email = request.form['correo']
        numero_confirmacion = ''.join(random.choice('123456789', k=6))

        mensaje = Message('Confirmacion de registro', sender = '4dm1n1str4d0r.upq.encuesta.2024@gmail.com', recipients=[email])
        mensaje.body(f'Tu numero de confirmación es: {numero_confirmacion}.\n 
                    Para confirmar tu registro sera nece')'''



if __name__ == '__main__':

    app.run(debug=True, port=5000)

