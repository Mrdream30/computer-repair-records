"""Automatic checks for database.py. Run from the project folder:  python tests/test_database.py
Uses a temporary database, so your real records are never touched."""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db

tmp = tempfile.mkdtemp()
db.DB_FOLDER = tmp
db.DB_PATH = os.path.join(tmp, "test.db")
db.create_tables()

results = []
def check(name, condition):
    results.append((name, condition))
    print(("PASS  " if condition else "FAIL  ") + name)

ok, _, cid = db.add_customer("Test A", "0900-111-1111", "x")
check("Valid input: customer is saved", ok and db.get_customer_by_id(cid) is not None)
check("Duplicate identifier is rejected", db.add_customer("Test B", "0900-111-1111")[0] is False)
check("Search finds existing record", len(db.search_customers("Test A")) == 1)
check("Search on missing record returns empty list", db.search_customers("zzz") == [])
check("Update existing record works", db.update_customer(cid, "Test A2", "0900-111-1111", "y")[0])
check("Update nonexistent ID is handled", db.update_customer(999, "a", "0900", "b")[0] is False)
ok, _, did = db.add_device(cid, "Laptop", "Acer", "X", "S1")
check("Device with valid owner is saved", ok)
check("Device with missing owner is rejected", db.add_device(999, "Laptop", "Acer")[0] is False)
check("Invalid device type is rejected", db.add_device(cid, "Tablet", "Acer")[0] is False)
ok, _, rid = db.add_repair(did, "Screen", 1000, "2026-11-01")
check("Repair is saved", ok)
check("Partial payment accepted", db.add_payment(rid, 400)[0])
check("Balance is charge minus payments", db.get_repair_by_id(rid)["balance"] == 600)
check("Overpayment is rejected", db.add_payment(rid, 700)[0] is False)
check("Delete blocked while linked records exist", db.delete_customer(cid)[0] is False)
check("Delete nonexistent ID is handled", db.delete_customer(999)[0] is False)
check("Analysis: revenue summary matches data",
      db.get_revenue_summary()["total_charges"] == 1000 and db.get_revenue_summary()["total_paid"] == 400)
check("Persistence: data readable from a new connection", len(db.get_all_customers()) == 1)

failed = [n for n, c in results if not c]
print(f"\n{len(results) - len(failed)}/{len(results)} checks passed.")
sys.exit(1 if failed else 0)
