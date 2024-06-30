from flask import Flask, flash, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Needed for session management

# Database configuration
DB_USER = 'app'
DB_PASSWORD = 'dreamer'
DB_HOST = '192.168.1.147'
DB_PORT = '3306'  # Default MySQL port
DB_NAME = 'application'

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    patient = db.relationship('Patient', backref=db.backref('medicines', lazy=True))
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(200), nullable=False)

class Groceries(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('admin'))
        else:
            return "Invalid credentials. Please try again."
    return render_template('login.html')

@app.route('/admin')
def admin():
    if 'username' in session:
        medicines = Medicine.query.all()
        # groceries = Groceries.query.all()  # Assuming a Groceries model exists
        return render_template('admin_dashboard.html', medicines=medicines) #(groceries=groceries) After groceries ready
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if 'username' in session:
        if request.method == 'POST':
            patient_id = request.form['patient_id']
            name = request.form['name']
            quantity = request.form['quantity']
            price = request.form['price']
            expiry_date = request.form['expiry_date']
            
            new_medicine = Medicine(
                patient_id=patient_id,
                name=name,
                quantity=int(quantity),
                price=float(price),
                expiry_date=expiry_date
            )
            db.session.add(new_medicine)
            db.session.commit()
            return redirect(url_for('admin'))
        
        patients = Patient.query.all()
        return render_template('add_medicine.html', patients=patients)
    return redirect(url_for('login'))

@app.route('/delete_medicine/<int:medicine_id>', methods=['POST'])
def delete_medicine(medicine_id):
    if 'username' in session:
        medicine = Medicine.query.get(medicine_id)
        if medicine:
            db.session.delete(medicine)
            db.session.commit()
        return redirect(url_for('admin'))
    return redirect(url_for('login'))

@app.route('/patients')
def patients():
    if 'username' in session:
        patients = Patient.query.all()
        return render_template('patients.html', patients=patients)
    return redirect(url_for('login'))

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if 'username' in session:
        if request.method == 'POST':
            name = request.form['name']
            age = request.form['age']
            gender = request.form['gender']
            contact = request.form['contact']
            address = request.form['address']

            # Check for duplicate entries
            existing_patient = Patient.query.filter_by(name=name, contact=contact).first()
            if existing_patient:
                flash('Patient already exists.', 'error')
                return redirect(url_for('add_patient'))

            new_patient = Patient(name=name, age=age, gender=gender, contact=contact, address=address)
            db.session.add(new_patient)
            db.session.commit()
            flash('Patient added successfully!', 'success')
            return redirect(url_for('patients'))

        return render_template('add_patient.html')
    return redirect(url_for('login'))

@app.route('/medicine_inventory')
def medicine_inventory():
    if 'username' in session:
        medicines = Medicine.query.all()
        return render_template('medicine_inventory.html', medicines=medicines)
    return redirect(url_for('login'))

@app.route('/groceries_inventory')
def groceries_inventory():
    if 'username' in session:
        groceries = Groceries.query.all()  # Assuming you have a Groceries model
        return render_template('groceries_inventory.html', groceries=groceries)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)