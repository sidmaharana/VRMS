
import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect('vrms.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Creates the database tables if they don't exist."""
    conn = get_db_connection()
    # The rest of the create_tables function remains the same...
    conn.execute("CREATE TABLE IF NOT EXISTS vehicles (...)")
    conn.execute("CREATE TABLE IF NOT EXISTS customers (...)")
    conn.execute("CREATE TABLE IF NOT EXISTS reservations (...)")
    conn.execute("CREATE TABLE IF NOT EXISTS maintenance (...)")
    conn.commit()
    conn.close()

def clear_all_data():
    """Clears all data from the tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reservations;")
    cursor.execute("DELETE FROM maintenance;")
    cursor.execute("DELETE FROM customers;")
    cursor.execute("DELETE FROM vehicles;")
    conn.commit()
    conn.close()

def insert_fake_data():
    """Inserts a complete set of fake data into the database."""
    fake = Faker('en_IN')
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Insert Vehicles
    vehicles = []
    vehicle_makes_models = {
        'Maruti Suzuki': ['Swift', 'Baleno', 'Dzire'],
        'Hyundai': ['i20', 'Creta', 'Verna'],
        'Tata': ['Nexon', 'Altroz', 'Harrier'],
        'Mahindra': ['Thar', 'XUV700', 'Scorpio'],
        'Honda': ['City', 'Amaze'],
        'Toyota': ['Innova', 'Fortuner']
    }
    statuses = ['Available'] * 70 + ['Rented'] * 20 + ['Maintenance'] * 10
    random.shuffle(statuses)

    for i in range(100):
        make = random.choice(list(vehicle_makes_models.keys()))
        model = random.choice(vehicle_makes_models[make])
        plate = f"MH{random.randint(10, 50)}CG{random.randint(1000, 9999)}"
        vehicle = (
            plate,
            make,
            model,
            random.randint(2018, 2024),
            random.randint(5000, 80000),
            round(random.uniform(1000.0, 5000.0), 2),
            statuses[i]
        )
        vehicles.append(vehicle)
    cursor.executemany("INSERT INTO vehicles VALUES (?, ?, ?, ?, ?, ?, ?)", vehicles)

    # 2. Insert Customers
    customers = []
    for _ in range(25):
        customer = (
            fake.name(),
            fake.phone_number(),
            f"{random.choice(['MH','DL','KA'])}{random.randint(10,99)}{fake.random_letter().upper()}{fake.random_letter().upper()}{random.randint(1000,9999)}"
        )
        customers.append(customer)
    cursor.executemany("INSERT INTO customers (name, contact_info, license_number) VALUES (?, ?, ?)", customers)

    # 3. Insert Reservations and Maintenance (Accurate Data)
    rented_vehicles = [v[0] for v in vehicles if v[6] == 'Rented']
    maintenance_vehicles = [v[0] for v in vehicles if v[6] == 'Maintenance']
    customer_ids = [i for i in range(1, 26)]

    # Create reservations for 'Rented' vehicles
    reservations = []
    for vehicle_plate in rented_vehicles:
        start_date = datetime.now() - timedelta(days=random.randint(1, 5))
        end_date = start_date + timedelta(days=random.randint(2, 7))
        daily_rate = cursor.execute('SELECT daily_rate FROM vehicles WHERE license_plate = ?', (vehicle_plate,)).fetchone()[0]
        total_cost = (end_date - start_date).days * daily_rate
        reservation = (
            start_date.strftime('%Y-%m-%d %H:%M:%S'),
            end_date.strftime('%Y-%m-%d %H:%M:%S'),
            total_cost,
            vehicle_plate,
            random.choice(customer_ids)
        )
        reservations.append(reservation)
    cursor.executemany("INSERT INTO reservations (start_date, end_date, total_cost, vehicle_plate, customer_id) VALUES (?, ?, ?, ?, ?)", reservations)

    # Create maintenance records for 'Maintenance' vehicles
    maintenance_records = []
    service_descriptions = ['Oil Change', 'Tire Rotation', 'Brake Inspection', 'Engine Diagnostic', 'Full Service']
    for vehicle_plate in maintenance_vehicles:
        record = (
            (datetime.now() - timedelta(days=random.randint(1, 3))).strftime('%Y-%m-%d %H:%M:%S'),
            random.choice(service_descriptions),
            round(random.uniform(1500.0, 10000.0), 2),
            vehicle_plate
        )
        maintenance_records.append(record)
    cursor.executemany("INSERT INTO maintenance (service_date, description, cost, vehicle_plate) VALUES (?, ?, ?, ?)", maintenance_records)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # create_tables() is not strictly needed if db is pre-existing, but good practice
    clear_all_data()
    insert_fake_data()
    print("Database cleared and populated with new, accurate fake data (100 vehicles, 25 customers).")
