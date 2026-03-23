# Flask + MySQL User Register/Login Example

## Setup
1. Install Python 3.10+ and MySQL server.
2. Create the database:
```sql
CREATE DATABASE flask_auth;
USE flask_auth;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    status ENUM('active','inactive') NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('present', 'absent', 'remote') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);
```
3. Clone or copy files into a folder.
4. Create virtual environment and install dependencies:
```bash
cd c:\Users\W24129-User.W24129\Desktop\PythonMysqlConnect
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
5. Edit `app.py` MySQL credentials.
6. Run app:
```bash
python app.py
```
7. Open `http://127.0.0.1:5000/register` to sign up.
8. Login at `http://127.0.0.1:5000/login`.

## Endpoints
- `/register` - register form (GET/POST)
- `/login` - login form (GET/POST)
- `/dashboard` - protected page with employee and attendance summary
- `/employees` - employee CRUD
- `/attendance` - attendance logs and new entry
- `/logout` - logout
