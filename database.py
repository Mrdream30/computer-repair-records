"""
database.py  -  MEMBER 1: Database design, table relationships, SQL/CRUD.

Computer Repair Service Records Management System (DSA 214 Final Lab)

This file is the ONLY place where SQL is written. The other members just
import these functions, for example:
    import database
    database.create_tables()
    ok, message = database.add_customer("Ana Reyes", "09171234567", "Echague")
"""

import os
import sqlite3
from datetime import date

# The database file lives in the "database" folder, next to this script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FOLDER = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_FOLDER, "repair_records.db")

DEVICE_TYPES = ("Desktop", "Laptop")
REPAIR_STATUSES = ("Pending", "In Progress", "Completed", "Released")


# ----------------------------------------------------------------------
# 1. CONNECTION
# ----------------------------------------------------------------------
def get_connection():
    """Open the SQLite database and return the connection.

    - Creates the database folder if it does not exist yet.
    - Turns ON foreign key checking (SQLite has it OFF by default).
    - row_factory lets us read columns by name, e.g. row["full_name"].
    """
    os.makedirs(DB_FOLDER, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ----------------------------------------------------------------------
# 2. TABLE DESIGN  (4 related tables)
#
#   customers 1 ---- * devices 1 ---- * repairs 1 ---- * payments
# ----------------------------------------------------------------------
def create_tables():
    """Create the four tables if they do not exist yet. Safe to run many times."""
    sql = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name      TEXT NOT NULL,
        contact_number TEXT NOT NULL UNIQUE,
        address        TEXT
    );

    CREATE TABLE IF NOT EXISTS devices (
        device_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id   INTEGER NOT NULL,
        device_type   TEXT NOT NULL CHECK (device_type IN ('Desktop', 'Laptop')),
        brand         TEXT NOT NULL,
        model         TEXT,
        serial_number TEXT UNIQUE,
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
    );

    CREATE TABLE IF NOT EXISTS repairs (
        repair_id           INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id           INTEGER NOT NULL,
        problem_description TEXT NOT NULL,
        date_received       TEXT NOT NULL,
        date_completed      TEXT,
        status              TEXT NOT NULL DEFAULT 'Pending'
                            CHECK (status IN ('Pending', 'In Progress',
                                              'Completed', 'Released')),
        service_charge      REAL NOT NULL DEFAULT 0 CHECK (service_charge >= 0),
        FOREIGN KEY (device_id) REFERENCES devices (device_id)
    );

    CREATE TABLE IF NOT EXISTS payments (
        payment_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        repair_id    INTEGER NOT NULL,
        amount       REAL NOT NULL CHECK (amount > 0),
        payment_date TEXT NOT NULL,
        FOREIGN KEY (repair_id) REFERENCES repairs (repair_id)
    );
    """
    conn = get_connection()
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


# ----------------------------------------------------------------------
# Small helpers used by the functions below
# ----------------------------------------------------------------------
def _today():
    """Return today's date as text, e.g. '2026-11-08'."""
    return date.today().isoformat()


def _write(sql, params):
    """Run one INSERT/UPDATE/DELETE safely.

    Returns (ok, message, new_id_or_rowcount).
    Catches the expected database errors so the program never crashes.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(sql, params)      # params fill the ? marks safely
        conn.commit()
        return True, "Success.", (cursor.lastrowid, cursor.rowcount)
    except sqlite3.IntegrityError as error:
        conn.rollback()
        text = str(error)
        if "UNIQUE" in text:
            return False, "Duplicate value: that record already exists.", None
        if "FOREIGN KEY" in text:
            return False, "Cannot do this: it is linked to other records.", None
        return False, "Invalid data: " + text, None
    except sqlite3.Error as error:
        conn.rollback()
        return False, "Database error: " + str(error), None
    finally:
        conn.close()


def _read(sql, params=()):
    """Run one SELECT and return a list of rows ([] if nothing found)."""
    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    except sqlite3.Error as error:
        print("Database error:", error)
        return []
    finally:
        conn.close()


# ----------------------------------------------------------------------
# 3. CUSTOMERS  (Create / Read / Search / Update / Delete)
# ----------------------------------------------------------------------
def add_customer(full_name, contact_number, address=""):
    """CREATE a customer. Returns (ok, message, new_customer_id)."""
    ok, msg, result = _write(
        "INSERT INTO customers (full_name, contact_number, address) VALUES (?, ?, ?)",
        (full_name, contact_number, address),
    )
    return (ok, "Customer added." if ok else msg, result[0] if ok else None)


def get_all_customers():
    """READ all customers, sorted by name."""
    return _read("SELECT * FROM customers ORDER BY full_name")


def get_customer_by_id(customer_id):
    """READ one customer. Returns a row, or None if the ID does not exist."""
    rows = _read("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
    return rows[0] if rows else None


def search_customers(keyword):
    """SEARCH customers by part of the name or contact number."""
    pattern = "%" + keyword + "%"
    return _read(
        "SELECT * FROM customers WHERE full_name LIKE ? OR contact_number LIKE ? "
        "ORDER BY full_name",
        (pattern, pattern),
    )


def update_customer(customer_id, full_name, contact_number, address):
    """UPDATE a customer. Returns (ok, message)."""
    ok, msg, result = _write(
        "UPDATE customers SET full_name = ?, contact_number = ?, address = ? "
        "WHERE customer_id = ?",
        (full_name, contact_number, address, customer_id),
    )
    if ok and result[1] == 0:
        return False, "Customer ID not found."
    return ok, "Customer updated." if ok else msg


def delete_customer(customer_id):
    """DELETE a customer. Blocked if the customer still has devices."""
    ok, msg, result = _write("DELETE FROM customers WHERE customer_id = ?", (customer_id,))
    if ok and result[1] == 0:
        return False, "Customer ID not found."
    return ok, "Customer deleted." if ok else msg


# ----------------------------------------------------------------------
# 4. DEVICES
# ----------------------------------------------------------------------
def add_device(customer_id, device_type, brand, model="", serial_number=None):
    """CREATE a device owned by a customer. Returns (ok, message, new_device_id)."""
    ok, msg, result = _write(
        "INSERT INTO devices (customer_id, device_type, brand, model, serial_number) "
        "VALUES (?, ?, ?, ?, ?)",
        (customer_id, device_type, brand, model, serial_number or None),
    )
    return (ok, "Device added." if ok else msg, result[0] if ok else None)


def get_all_devices():
    """READ all devices together with the owner's name (JOIN)."""
    return _read(
        "SELECT d.device_id, d.device_type, d.brand, d.model, d.serial_number, "
        "       c.customer_id, c.full_name "
        "FROM devices d JOIN customers c ON d.customer_id = c.customer_id "
        "ORDER BY d.device_id"
    )


def get_device_by_id(device_id):
    """READ one device. Returns a row or None."""
    rows = _read("SELECT * FROM devices WHERE device_id = ?", (device_id,))
    return rows[0] if rows else None


def update_device(device_id, device_type, brand, model, serial_number):
    """UPDATE a device. Returns (ok, message)."""
    ok, msg, result = _write(
        "UPDATE devices SET device_type = ?, brand = ?, model = ?, serial_number = ? "
        "WHERE device_id = ?",
        (device_type, brand, model, serial_number or None, device_id),
    )
    if ok and result[1] == 0:
        return False, "Device ID not found."
    return ok, "Device updated." if ok else msg


def delete_device(device_id):
    """DELETE a device. Blocked if it still has repair records."""
    ok, msg, result = _write("DELETE FROM devices WHERE device_id = ?", (device_id,))
    if ok and result[1] == 0:
        return False, "Device ID not found."
    return ok, "Device deleted." if ok else msg


# ----------------------------------------------------------------------
# 5. REPAIRS (service requests)
# ----------------------------------------------------------------------
def add_repair(device_id, problem_description, service_charge=0, date_received=None):
    """CREATE a repair request. Status starts as 'Pending'."""
    ok, msg, result = _write(
        "INSERT INTO repairs (device_id, problem_description, date_received, "
        "service_charge) VALUES (?, ?, ?, ?)",
        (device_id, problem_description, date_received or _today(), service_charge),
    )
    return (ok, "Repair request added." if ok else msg, result[0] if ok else None)


# One reusable SELECT that joins 3 tables and also computes the balance.
_REPAIR_DETAILS_SQL = """
    SELECT r.repair_id, c.full_name, d.device_type, d.brand, d.model,
           r.problem_description, r.date_received, r.date_completed, r.status,
           r.service_charge,
           IFNULL(SUM(p.amount), 0.0)                    AS total_paid,
           r.service_charge - IFNULL(SUM(p.amount), 0.0) AS balance
    FROM repairs r
    JOIN devices   d ON r.device_id   = d.device_id
    JOIN customers c ON d.customer_id = c.customer_id
    LEFT JOIN payments p ON p.repair_id = r.repair_id
"""


def get_all_repairs(order_by="date"):
    """READ all repairs with customer, device, paid amount and balance.

    order_by: 'date' (newest first), 'charge' (highest first) or 'status'.
    """
    # The ORDER BY text comes from a fixed dictionary, never from user input.
    choices = {
        "date": "r.date_received DESC, r.repair_id DESC",
        "charge": "r.service_charge DESC",
        "status": "r.status, r.repair_id",
    }
    sql = _REPAIR_DETAILS_SQL + " GROUP BY r.repair_id ORDER BY " + choices.get(order_by, choices["date"])
    return _read(sql)


def get_repair_by_id(repair_id):
    """READ one repair with full details. Returns a row or None."""
    sql = _REPAIR_DETAILS_SQL + " WHERE r.repair_id = ? GROUP BY r.repair_id"
    rows = _read(sql, (repair_id,))
    return rows[0] if rows else None


def search_repairs_by_status(status):
    """SEARCH/FILTER repairs by status."""
    sql = _REPAIR_DETAILS_SQL + " WHERE r.status = ? GROUP BY r.repair_id ORDER BY r.repair_id"
    return _read(sql, (status,))


def search_repairs_by_customer(keyword):
    """SEARCH repairs by part of the customer's name."""
    sql = (_REPAIR_DETAILS_SQL
           + " WHERE c.full_name LIKE ? GROUP BY r.repair_id ORDER BY r.repair_id")
    return _read(sql, ("%" + keyword + "%",))


def search_repairs_by_date(start_date, end_date):
    """SEARCH repairs received between two dates (format YYYY-MM-DD)."""
    sql = (_REPAIR_DETAILS_SQL
           + " WHERE r.date_received BETWEEN ? AND ? GROUP BY r.repair_id "
             "ORDER BY r.date_received")
    return _read(sql, (start_date, end_date))


def update_repair(repair_id, problem_description, service_charge, status,
                  date_completed=None):
    """UPDATE a repair. Sets date_completed (today by default) when finished."""
    if status in ("Completed", "Released"):
        completed = date_completed or _today()
    else:
        completed = None
    ok, msg, result = _write(
        "UPDATE repairs SET problem_description = ?, service_charge = ?, status = ?, "
        "date_completed = ? WHERE repair_id = ?",
        (problem_description, service_charge, status, completed, repair_id),
    )
    if ok and result[1] == 0:
        return False, "Repair ID not found."
    return ok, "Repair updated." if ok else msg


def delete_repair(repair_id):
    """DELETE a repair. Blocked if it still has payments."""
    ok, msg, result = _write("DELETE FROM repairs WHERE repair_id = ?", (repair_id,))
    if ok and result[1] == 0:
        return False, "Repair ID not found."
    return ok, "Repair deleted." if ok else msg


# ----------------------------------------------------------------------
# 6. PAYMENTS (partial payments and remaining balance)
# ----------------------------------------------------------------------
def add_payment(repair_id, amount, payment_date=None):
    """CREATE a payment. Refuses payments bigger than the remaining balance."""
    repair = get_repair_by_id(repair_id)
    if repair is None:
        return False, "Repair ID not found.", None
    if amount > repair["balance"]:
        return False, "Payment is more than the balance (%.2f)." % repair["balance"], None
    ok, msg, result = _write(
        "INSERT INTO payments (repair_id, amount, payment_date) VALUES (?, ?, ?)",
        (repair_id, amount, payment_date or _today()),
    )
    return (ok, "Payment recorded." if ok else msg, result[0] if ok else None)


def get_payments_for_repair(repair_id):
    """READ all payments of one repair, oldest first."""
    return _read(
        "SELECT * FROM payments WHERE repair_id = ? ORDER BY payment_date, payment_id",
        (repair_id,),
    )


def delete_payment(payment_id):
    """DELETE a payment."""
    ok, msg, result = _write("DELETE FROM payments WHERE payment_id = ?", (payment_id,))
    if ok and result[1] == 0:
        return False, "Payment ID not found."
    return ok, "Payment deleted." if ok else msg


# ----------------------------------------------------------------------
# 7. AGGREGATE QUERIES  (COUNT, SUM, AVG, MAX) - Member 3 can use these
# ----------------------------------------------------------------------
def count_repairs_by_status():
    """COUNT repairs for each status."""
    return _read("SELECT status, COUNT(*) AS total FROM repairs GROUP BY status ORDER BY total DESC")


def count_repairs_by_device_type():
    """COUNT repairs for Desktop vs Laptop."""
    return _read(
        "SELECT d.device_type, COUNT(*) AS total "
        "FROM repairs r JOIN devices d ON r.device_id = d.device_id "
        "GROUP BY d.device_type ORDER BY total DESC"
    )


def get_revenue_summary():
    """One row: total charged, total paid, total unpaid, average charge, highest charge."""
    sql = """
        SELECT IFNULL(SUM(r.service_charge), 0)                          AS total_charges,
               IFNULL((SELECT SUM(amount) FROM payments), 0)             AS total_paid,
               IFNULL(SUM(r.service_charge), 0)
                 - IFNULL((SELECT SUM(amount) FROM payments), 0)         AS total_unpaid,
               IFNULL(AVG(r.service_charge), 0)                          AS average_charge,
               IFNULL(MAX(r.service_charge), 0)                          AS highest_charge
        FROM repairs r
    """
    return _read(sql)[0]


def get_monthly_revenue():
    """Total service charges per month (for a chart): rows of (month, total)."""
    return _read(
        "SELECT substr(date_received, 1, 7) AS month, SUM(service_charge) AS total "
        "FROM repairs GROUP BY month ORDER BY month"
    )


def count_repairs_by_brand():
    """COUNT repairs per device brand (most repaired brands first)."""
    return _read(
        "SELECT d.brand, COUNT(*) AS total "
        "FROM repairs r JOIN devices d ON r.device_id = d.device_id "
        "GROUP BY d.brand ORDER BY total DESC, d.brand"
    )


def get_average_turnaround_days():
    """AVG number of days between date_received and date_completed.

    Returns None when no repair has been completed yet.
    """
    rows = _read(
        "SELECT AVG(julianday(date_completed) - julianday(date_received)) AS days "
        "FROM repairs WHERE date_completed IS NOT NULL"
    )
    return rows[0]["days"] if rows else None


# ----------------------------------------------------------------------
# 8. SIMULATED SAMPLE DATA  (clearly labelled - NOT real customers)
# ----------------------------------------------------------------------
def seed_sample_data():
    """Insert SIMULATED sample records if the database is empty.

    All names and numbers below are invented for demonstration only.
    They are not verified real-world records.
    """
    if get_all_customers():
        return False                                 # already has data

    people = [
        ("Sample Customer A", "0900-000-0001", "Sample Address 1"),
        ("Sample Customer B", "0900-000-0002", "Sample Address 2"),
        ("Sample Customer C", "0900-000-0003", "Sample Address 3"),
        ("Sample Customer D", "0900-000-0004", "Sample Address 4"),
    ]
    ids = [add_customer(*p)[2] for p in people]

    devices = [
        (ids[0], "Laptop", "Acer", "Aspire 5", "SIM-0001"),
        (ids[0], "Desktop", "Dell", "OptiPlex", "SIM-0002"),
        (ids[1], "Laptop", "Lenovo", "IdeaPad", "SIM-0003"),
        (ids[2], "Desktop", "HP", "Pavilion", "SIM-0004"),
        (ids[3], "Laptop", "ASUS", "VivoBook", "SIM-0005"),
    ]
    dev_ids = [add_device(*d)[2] for d in devices]

    repairs = [
        (dev_ids[0], "Cracked screen", 3500, "2026-09-05"),
        (dev_ids[1], "Will not turn on", 1200, "2026-09-18"),
        (dev_ids[2], "Slow performance, needs OS reinstall", 800, "2026-10-02"),
        (dev_ids[3], "Faulty power supply", 1500, "2026-10-12"),
        (dev_ids[4], "Keyboard replacement", 2200, "2026-10-25"),
        (dev_ids[2], "Battery replacement", 2800, "2026-11-03"),
    ]
    rep_ids = [add_repair(*r)[2] for r in repairs]

    update_repair(rep_ids[0], "Cracked screen", 3500, "Released", "2026-09-09")
    update_repair(rep_ids[1], "Will not turn on", 1200, "Completed", "2026-09-21")
    update_repair(rep_ids[3], "Faulty power supply", 1500, "In Progress")

    add_payment(rep_ids[0], 3500, "2026-09-10")
    add_payment(rep_ids[1], 500, "2026-09-20")
    add_payment(rep_ids[2], 300, "2026-10-03")
    add_payment(rep_ids[4], 1000, "2026-10-26")
    return True


if __name__ == "__main__":
    # Running "python database.py" by itself sets up the database with sample data.
    create_tables()
    print("Sample data added." if seed_sample_data() else "Database already has data.")
    print("Database file:", DB_PATH)
