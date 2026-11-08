"""
main.py  -  Main menu and program flow.
Computer Repair Service Records Management System (CLI)

Run with:  python main.py
"""

import database as db
import functions as fn
import analytics


# ======================================================================
# CUSTOMERS
# ======================================================================
def add_customer_flow():
    name = fn.get_text("Full name: ")
    phone = fn.get_phone("Contact number: ")
    address = fn.get_text("Address (optional): ", required=False)
    ok, message, _ = db.add_customer(name, phone, address)
    print(" ", message)


def search_customer_flow():
    keyword = fn.get_text("Search by name or contact number: ")
    fn.print_table(db.search_customers(keyword), fn.CUSTOMER_COLUMNS)


def update_customer_flow():
    customer = db.get_customer_by_id(fn.get_int("Customer ID to update: "))
    if customer is None:
        print("  Customer ID not found.")
        return
    name = fn.get_text_default("Full name", customer["full_name"])
    phone = fn.get_phone("Contact number", customer["contact_number"])
    address = fn.get_text_default("Address", customer["address"] or "")
    print(" ", db.update_customer(customer["customer_id"], name, phone, address)[1])


def delete_customer_flow():
    customer = db.get_customer_by_id(fn.get_int("Customer ID to delete: "))
    if customer is None:
        print("  Customer ID not found.")
        return
    if fn.confirm(f"Delete {customer['full_name']}?"):
        print(" ", db.delete_customer(customer["customer_id"])[1])
    else:
        print("  Deletion cancelled.")


def customers_menu():
    while True:
        print("\n=== CUSTOMERS ===\n1. Add  2. View all  3. Search  4. Update  5. Delete  0. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            add_customer_flow()
        elif choice == "2":
            fn.print_table(db.get_all_customers(), fn.CUSTOMER_COLUMNS)
        elif choice == "3":
            search_customer_flow()
        elif choice == "4":
            update_customer_flow()
        elif choice == "5":
            delete_customer_flow()
        elif choice == "0":
            break
        else:
            print("  Invalid choice. Please pick 0-5.")


# ======================================================================
# DEVICES
# ======================================================================
def add_device_flow():
    customer_id = fn.get_int("Owner's customer ID: ")
    if db.get_customer_by_id(customer_id) is None:
        print("  Customer ID not found. Add the customer first.")
        return
    device_type = fn.get_choice("Device type:", db.DEVICE_TYPES)
    brand = fn.get_text("Brand: ")
    model = fn.get_text("Model (optional): ", required=False)
    serial = fn.get_text("Serial number (optional): ", required=False)
    print(" ", db.add_device(customer_id, device_type, brand, model, serial)[1])


def update_device_flow():
    device = db.get_device_by_id(fn.get_int("Device ID to update: "))
    if device is None:
        print("  Device ID not found.")
        return
    device_type = fn.get_choice("Device type:", db.DEVICE_TYPES)
    brand = fn.get_text_default("Brand", device["brand"])
    model = fn.get_text_default("Model", device["model"] or "")
    serial = fn.get_text_default("Serial", device["serial_number"] or "")
    print(" ", db.update_device(device["device_id"], device_type, brand, model, serial)[1])


def delete_device_flow():
    device = db.get_device_by_id(fn.get_int("Device ID to delete: "))
    if device is None:
        print("  Device ID not found.")
        return
    if fn.confirm(f"Delete {device['brand']} {device['model']}?"):
        print(" ", db.delete_device(device["device_id"])[1])
    else:
        print("  Deletion cancelled.")


def devices_menu():
    while True:
        print("\n=== DEVICES ===\n1. Add  2. View all  3. Update  4. Delete  0. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            add_device_flow()
        elif choice == "2":
            fn.print_table(db.get_all_devices(), fn.DEVICE_COLUMNS)
        elif choice == "3":
            update_device_flow()
        elif choice == "4":
            delete_device_flow()
        elif choice == "0":
            break
        else:
            print("  Invalid choice. Please pick 0-4.")


# ======================================================================
# REPAIRS
# ======================================================================
def add_repair_flow():
    device_id = fn.get_int("Device ID: ")
    if db.get_device_by_id(device_id) is None:
        print("  Device ID not found. Add the device first.")
        return
    problem = fn.get_text("Problem description: ")
    charge = fn.get_amount("Service charge: ", allow_zero=True)
    received = fn.get_date("Date received (YYYY-MM-DD, Enter = today): ", allow_blank=True)
    print(" ", db.add_repair(device_id, problem, charge, received)[1])


def search_repair_flow():
    kind = fn.get_choice("Search repairs by:", ["Status", "Customer name", "Date range"])
    if kind == "Status":
        rows = db.search_repairs_by_status(fn.get_choice("Status:", db.REPAIR_STATUSES))
    elif kind == "Customer name":
        rows = db.search_repairs_by_customer(fn.get_text("Customer name: "))
    else:
        start = fn.get_date("Start date (YYYY-MM-DD): ")
        end = fn.get_date("End date (YYYY-MM-DD): ")
        rows = db.search_repairs_by_date(start, end)
    fn.print_table(rows, fn.REPAIR_COLUMNS)


def update_repair_flow():
    repair = db.get_repair_by_id(fn.get_int("Repair ID to update: "))
    if repair is None:
        print("  Repair ID not found.")
        return
    problem = fn.get_text_default("Problem", repair["problem_description"])
    charge = fn.get_amount(f"Service charge [{repair['service_charge']}]: ", allow_zero=True)
    status = fn.get_choice("New status:", db.REPAIR_STATUSES)
    print(" ", db.update_repair(repair["repair_id"], problem, charge, status)[1])


def delete_repair_flow():
    repair = db.get_repair_by_id(fn.get_int("Repair ID to delete: "))
    if repair is None:
        print("  Repair ID not found.")
        return
    if fn.confirm(f"Delete repair #{repair['repair_id']} ({repair['problem_description']})?"):
        print(" ", db.delete_repair(repair["repair_id"])[1])
    else:
        print("  Deletion cancelled.")


def repairs_menu():
    while True:
        print("\n=== REPAIRS ===\n1. Add  2. View all  3. Search  4. Update  5. Delete  0. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            add_repair_flow()
        elif choice == "2":
            order = fn.get_choice("Sort by:", ["date", "charge", "status"])
            fn.print_table(db.get_all_repairs(order), fn.REPAIR_COLUMNS)
        elif choice == "3":
            search_repair_flow()
        elif choice == "4":
            update_repair_flow()
        elif choice == "5":
            delete_repair_flow()
        elif choice == "0":
            break
        else:
            print("  Invalid choice. Please pick 0-5.")


# ======================================================================
# PAYMENTS
# ======================================================================
def add_payment_flow():
    repair = db.get_repair_by_id(fn.get_int("Repair ID being paid: "))
    if repair is None:
        print("  Repair ID not found.")
        return
    print(f"  Charge {fn.money(repair['service_charge'])}, "
          f"paid {fn.money(repair['total_paid'])}, balance {fn.money(repair['balance'])}")
    if repair["balance"] <= 0:
        print("  This repair is already fully paid.")
        return
    amount = fn.get_amount("Payment amount: ")
    date_paid = fn.get_date("Payment date (YYYY-MM-DD, Enter = today): ", allow_blank=True)
    print(" ", db.add_payment(repair["repair_id"], amount, date_paid)[1])


def view_payments_flow():
    repair_id = fn.get_int("Repair ID: ")
    repair = db.get_repair_by_id(repair_id)
    if repair is None:
        print("  Repair ID not found.")
        return
    fn.print_table(db.get_payments_for_repair(repair_id), fn.PAYMENT_COLUMNS)
    print(f"  Balance remaining: {fn.money(repair['balance'])}")


def delete_payment_flow():
    payment_id = fn.get_int("Payment ID to delete: ")
    if fn.confirm(f"Delete payment #{payment_id}?"):
        print(" ", db.delete_payment(payment_id)[1])
    else:
        print("  Deletion cancelled.")


def payments_menu():
    while True:
        print("\n=== PAYMENTS ===\n1. Record payment  2. View payments of a repair  "
              "3. Delete payment  0. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            add_payment_flow()
        elif choice == "2":
            view_payments_flow()
        elif choice == "3":
            delete_payment_flow()
        elif choice == "0":
            break
        else:
            print("  Invalid choice. Please pick 0-3.")


# ======================================================================
# ANALYTICS
# ======================================================================
def analytics_menu():
    while True:
        print("\n=== ANALYTICS ===\n1. Revenue summary  2. Repairs by status  "
              "3. Turnaround and brands  4. Generate charts  0. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            analytics.revenue_report()
        elif choice == "2":
            analytics.status_report()
        elif choice == "3":
            analytics.turnaround_report()
        elif choice == "4":
            paths = analytics.generate_all_charts()
            if paths:
                print("  Charts saved:")
                for path in paths:
                    print("   -", path)
            else:
                print("  No data to chart yet.")
        elif choice == "0":
            break
        else:
            print("  Invalid choice. Please pick 0-4.")


# ======================================================================
# MAIN MENU
# ======================================================================
def main():
    db.create_tables()
    if db.seed_sample_data():
        print("(First run: loaded SIMULATED sample data for demonstration.)")
    while True:
        print("\n==== COMPUTER REPAIR SERVICE RECORDS ====")
        print("1. Customers\n2. Devices\n3. Repairs\n4. Payments\n5. Analytics\n0. Exit")
        choice = input("Choose: ").strip()
        if choice == "1":
            customers_menu()
        elif choice == "2":
            devices_menu()
        elif choice == "3":
            repairs_menu()
        elif choice == "4":
            payments_menu()
        elif choice == "5":
            analytics_menu()
        elif choice == "0":
            print("Goodbye! All records are saved.")
            break
        else:
            print("  Invalid choice. Please pick 0-5.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed.")
