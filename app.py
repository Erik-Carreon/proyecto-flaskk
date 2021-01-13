from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL, MySQLdb 
import bcrypt


#Conexion a Sql
app = Flask(__name__)
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flaskcontact'
MySQL =  MySQL (app)
 
# configuracion

app.secret_key = 'mysecretkey'

@app.route('/')
def main():
    if 'nombre' in session:
        return render_template('index.html')
    else:
        return render_template('login.html')

#Index
@app.route('/index')
def Index():
    if 'nombre' in session:
        cur = MySQL.connection.cursor()
        cur.execute('SELECT * FROM contact')
        data = cur.fetchall()
        return render_template('index.html', contacts = data)
    else:
        return render_template('login.html')



#Login        
@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        nombre = request.form['Nombre']
        passwd = request.form['Passwd'].encode('utf8_unicode_ci')

        cur = MySQL.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT * FROM contact WHERE Nombre=%s",(nombre,))
        user = cur.fetchone()
        cur.close()

        if user:
            if bcrypt.hashpw(passwd, user['Passwd'].encode('utf8_unicode_ci')) == user['Passwd'].encode('utf8_unicode_ci'):
                session['loggedin'] = True
                session['IdUser'] = user['IdUser']
                session['Nombre'] = user['Nombre']
                session['username'] = user['username']
                cur = MySQL.connection.cursor()
                cur.execute('SELECT * FROM contact')
                data = cur.fetchall()
                return redirect(url_for('index', contact = data))
                #return render_template('index.html', contact = data)
            else:
                 flash('ACCESO DENEGADO', 'altert-danger')
                 return render_template('login.html')
        else:
             flash('ACCESO DENEGADO', 'altert-danger')
             return render_template('login.html') 
    else:
        flash('ACCESO DENEGADO', 'altert-danger')
        return render_template('login.html')





#Register
@app.route('/register', methods=["GET","POST"])
def register():
    if request.method== 'GET':
        return render_template('register.html')
    else:
        nombre = request.form['Nombre']
        username = request.form['username']
        passwd = request.form['Passwd'].encode('utf8')
        hash_password = bcrypt.hashpw(passwd, bcrypt.gensalt())
        cur = MySQL.connection.cursor()
        cur.execute('INSERT INTO usuarios (Nombre, username, Passwd) VALUES($s, $s, $s)', (nombre,username,hash_password,))
        #cur.execute('INSERT INTO usuarios (username, Passwd) VALUES(%s, %s, %s)',(Nombre,username,hash_password,))
        MySQL.connection.commit()
        flash('You are now registered and can log in')
        session['Nombre'] = nombre
        session['username'] = username
        return redirect(url_for('login'))




#Logout
@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html')

    

#Crear
@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        nombre = request.form['nombre']
        phone = request.form['phone']
        email = request.form['email']
        cur = MySQL.connection.cursor()
        cur.execute('INSERT INTO contacts (nombre, phone, email) VALUES(%s, %s, %s)',
        (nombre, phone, email))
        MySQL.connection.commit()
        flash('Contact Added Successfully')
        return redirect(url_for('index'))


@app.route ('/edit/<id>',)
def get_contact(id):
    cur = MySQL.connection.cursor()
    #cur.execute('SELECT * FROM contact WHERE id = %s', (id,))
    #cur.execute('SELECT * FROM contacts WHERE id = %s', (str(id),))
    cur.execute('SELECT * FROM contact WHERE id = {0}'.format(id))
    data = cur.fetchall()
    return render_template('edit-contact.html', contact = data[0])
 
@app.route('/update/<id>', methods = ['POST'])
def update_contact(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        phone = request.form['phone']
        email = request.form['email']
        cur = MySQL.connection.cursor()
        cur.execute("""
       UPDATE   contact
        SET nombre = %s,
          phone = %s,
          email = %s
        WHERE id = %s
        """, (nombre, phone, email, id))
        MySQL.connection.commit()
        flash('Contact Updated Successfully')
        return redirect(url_for('index'))

@app.route ('/delete/<string:id>')
def delete_contact(id):
    cur = MySQL.connection.cursor()
    cur.execute('DELETE FROM contact WHERE id = {0}'.format(id))
    MySQL.connection.commit()
    flash('Contact Removed Successfully') 
    return redirect(url_for('index'))

if __name__ =='__main__':
 app.run(port=5000,debug=True)



