
from flask import Flask, render_template, request, redirect, url_for
import database as db
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Function to get a database connection
def get_db_connection():
    conn = sqlite3.connect('vrms.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    # Overall Fleet Status
    total_vehicles = conn.execute('SELECT COUNT(*) FROM vehicles').fetchone()[0]
    available_vehicles = conn.execute('SELECT COUNT(*) FROM vehicles WHERE status = ?', ('Available',)).fetchone()[0]
    rented_vehicles = conn.execute('SELECT COUNT(*) FROM vehicles WHERE status = ?', ('Rented',)).fetchone()[0]
    maintenance_vehicles = conn.execute('SELECT COUNT(*) FROM vehicles WHERE status = ?', ('Maintenance',)).fetchone()[0]
    
    # Upcoming Reservations (simplified for dashboard)
    upcoming_reservations = conn.execute('SELECT * FROM reservations WHERE start_date > ? ORDER BY start_date LIMIT 5', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),)).fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                           total_vehicles=total_vehicles,
                           available_vehicles=available_vehicles,
                           rented_vehicles=rented_vehicles,
                           maintenance_vehicles=maintenance_vehicles,
                           upcoming_reservations=upcoming_reservations)

@app.route('/vehicles', methods=['GET', 'POST'])
def vehicles():
    conn = get_db_connection()
    if request.method == 'POST':
        license_plate = request.form['license_plate']
        make = request.form['make']
        model = request.form['model']
        year = request.form['year']
        mileage = request.form['mileage']
        daily_rate = request.form['daily_rate']
        status = request.form['status']
        
        conn.execute('INSERT INTO vehicles (license_plate, make, model, year, mileage, daily_rate, status) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (license_plate, make, model, year, mileage, daily_rate, status))
        conn.commit()
        return redirect(url_for('vehicles'))
        
    all_vehicles = conn.execute('SELECT * FROM vehicles').fetchall()
    conn.close()
    return render_template('vehicles.html', vehicles=all_vehicles)

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        contact_info = request.form['contact_info']
        license_number = request.form['license_number']
        
        conn.execute('INSERT INTO customers (name, contact_info, license_number) VALUES (?, ?, ?)',
                     (name, contact_info, license_number))
        conn.commit()
        return redirect(url_for('customers'))

    all_customers = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return render_template('customers.html', customers=all_customers)

@app.route('/reservations', methods=['GET', 'POST'])
def reservations():
    conn = get_db_connection()
    
    if request.method == 'POST':
        vehicle_plate = request.form['vehicle_plate']
        customer_id = request.form['customer_id']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Data Validation
        # 1. Date Logic
        if start_date >= end_date:
            return "Error: Start date must be before end date.", 400
            
        # 2. Reservation Overlap Check
        overlapping = conn.execute('SELECT * FROM reservations WHERE vehicle_plate = ? AND NOT (end_date <= ? OR start_date >= ?)', 
                                     (vehicle_plate, start_date, end_date)).fetchall()
        if overlapping:
            return "Error: Vehicle is already reserved for the selected time period.", 400

        # Calculate total cost
        daily_rate = conn.execute('SELECT daily_rate FROM vehicles WHERE license_plate = ?', (vehicle_plate,)).fetchone()['daily_rate']
        duration = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days
        total_cost = duration * daily_rate

        # Insert new reservation
        conn.execute('INSERT INTO reservations (vehicle_plate, customer_id, start_date, end_date, total_cost) VALUES (?, ?, ?, ?, ?)',
                     (vehicle_plate, customer_id, start_date, end_date, total_cost))
        # Update vehicle status
        conn.execute('UPDATE vehicles SET status = ? WHERE license_plate = ?', ('Rented', vehicle_plate))
        conn.commit()
        
        return redirect(url_for('reservations'))

    all_reservations = conn.execute('''
        SELECT r.*, v.make, v.model, c.name 
        FROM reservations r 
        JOIN vehicles v ON r.vehicle_plate = v.license_plate 
        JOIN customers c ON r.customer_id = c.customer_id
    ''').fetchall()
    
    # For the reservation form dropdowns
    available_vehicles = conn.execute('SELECT * FROM vehicles WHERE status = ?', ('Available',)).fetchall()
    all_customers = conn.execute('SELECT * FROM customers').fetchall()

    conn.close()
    return render_template('reservations.html', 
                           reservations=all_reservations, 
                           available_vehicles=available_vehicles, 
                           customers=all_customers)

@app.route('/maintenance', methods=['GET', 'POST'])
def maintenance():
    conn = get_db_connection()
    if request.method == 'POST':
        vehicle_plate = request.form['vehicle_plate']
        service_date = request.form['service_date']
        description = request.form['description']
        cost = request.form['cost']
        
        conn.execute('INSERT INTO maintenance (vehicle_plate, service_date, description, cost) VALUES (?, ?, ?, ?)',
                     (vehicle_plate, service_date, description, cost))
        # Update vehicle status
        conn.execute('UPDATE vehicles SET status = ? WHERE license_plate = ?', ('Maintenance', vehicle_plate))
        conn.commit()
        return redirect(url_for('maintenance'))

    all_maintenance = conn.execute('''
        SELECT m.*, v.make, v.model 
        FROM maintenance m 
        JOIN vehicles v ON m.vehicle_plate = v.license_plate
    ''').fetchall()
    all_vehicles = conn.execute('SELECT * FROM vehicles').fetchall()
    conn.close()
    return render_template('maintenance.html', maintenance_records=all_maintenance, vehicles=all_vehicles)

if __name__ == '__main__':
    app.run(debug=True)
