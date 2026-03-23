from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash


app  =Flask(__name__)

app.secret_key = 'replace-with-a-strong-secret'



app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE'] = 'flask_auths'






def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DATABASE']
    )






@app.route('/')
def home():
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not username or not email or not password or not confirm:
            flash('Please fill out all fields.', 'warning')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        conn = get_db_connection()
        
        cursor = conn.cursor(dictionary=True)

        cursor.execute('SELECT id FROM users WHERE email = %s OR username = %s', (email, username))
        existing = cursor.fetchone()
        if existing:
            flash('Email or username already taken.', 'danger')
            cursor.close(); conn.close()
            return render_template('register.html')

        cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                       (username, email, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form.get('email').strip().lower()
        
    
        password = request.form.get('password')
        


        if not email or not password:
            flash('Please enter email and password.', 'warning')
            return render_template('login.html')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close(); conn.close()
        
        

        if user and check_password_hash(user['password'], password):
            
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'danger')

    return render_template('login.html')






@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'info')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT COUNT(*) AS total_employees FROM employees')
    total_employees = cursor.fetchone()['total_employees']


    cursor.execute('SELECT a.id, e.name, a.attendance_date, a.status FROM attendance a JOIN employees e ON a.employee_id = e.id ORDER BY a.attendance_date DESC LIMIT 10')
    recent_attendance = cursor.fetchall()

    cursor.close(); conn.close()

    return render_template('dashboard.html', username=session.get('username'), total_employees=total_employees, recent_attendance=recent_attendance)




@app.route('/employees')
def employees():
    if 'user_id' not in session:
        flash('Please log in to access employee list.', 'info')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM employees ORDER BY id DESC')
    all_employees = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('employees.html', employees=all_employees)


@app.route('/employees/create', methods=['GET', 'POST'])
def create_employee():
    if 'user_id' not in session:
        flash('Please log in to create employee.', 'info')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name').strip()
        position = request.form.get('position').strip()
        if not name or not position:
            flash('Please fill all fields.', 'warning')
            return render_template('employee_form.html', action='Create', employee={})

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO employees (name, position) VALUES (%s, %s)', (name, position))
        conn.commit()
        cursor.close(); conn.close()

        flash('Employee created successfully.', 'success')
        return redirect(url_for('employees'))

    return render_template('employee_form.html', action='Create', employee={})



@app.route('/employees/edit/<int:employee_id>', methods=['GET', 'POST'])

def edit_employee(employee_id):
    if 'user_id' not in session:
        flash('Please log in to edit employee.', 'info')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM employees WHERE id = %s', (employee_id,))
    employee = cursor.fetchone()

    if not employee:
        cursor.close(); conn.close()
        flash('Employee not found.', 'danger')
        return redirect(url_for('employees'))

    if request.method == 'POST':
        name = request.form.get('name').strip()
        position = request.form.get('position').strip()
        status = request.form.get('status')
        if not name or not position or not status:
            flash('Please fill all fields.', 'warning')
            return render_template('employee_form.html', action='Edit', employee=employee)

        cursor.execute('UPDATE employees SET name = %s, position = %s, status = %s WHERE id = %s',
                       (name, position, status, employee_id))
        conn.commit()
        cursor.close(); conn.close()
        flash('Employee updated successfully.', 'success')
        return redirect(url_for('employees'))

    cursor.close(); conn.close()
    return render_template('employee_form.html', action='Edit', employee=employee)


@app.route('/employees/delete/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    if 'user_id' not in session:
        flash('Please log in to delete employee.', 'info')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM employees WHERE id = %s', (employee_id,))
    conn.commit()
    cursor.close(); conn.close()

    flash('Employee deleted successfully.', 'success')
    return redirect(url_for('employees'))


@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'user_id' not in session:
        flash('Please log in to manage attendance.', 'info')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        attendance_date = request.form.get('attendance_date')
        status = request.form.get('status')
        if not employee_id or not attendance_date or not status:
            flash('All attendance fields are required.', 'warning')
        else:
            cursor.execute('INSERT INTO attendance (employee_id, attendance_date, status) VALUES (%s, %s, %s)',
                           (employee_id, attendance_date, status))
            conn.commit()
            flash('Attendance recorded.', 'success')

    cursor.execute('SELECT e.id as emp_id, e.name FROM employees e ORDER BY e.name')
    employees = cursor.fetchall()
    cursor.execute('SELECT a.id, e.name, a.attendance_date, a.status FROM attendance a JOIN employees e ON a.employee_id = e.id ORDER BY a.attendance_date DESC')
    records = cursor.fetchall()
    cursor.close(); conn.close()

    return render_template('attendance.html', employees=employees, records=records)


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
