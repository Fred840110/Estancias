from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'secretKey'

@app.route('/')
def index():
    
    return render_template ('index.html')

@app.route('/registro.html')
def registro():

    return render_template('registro.html')


if __name__ == '__main__':

    app.run(debug=True, port=5000)

