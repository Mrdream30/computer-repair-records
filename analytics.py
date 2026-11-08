"""
analytics.py  -  MEMBER 3: data analysis and charts.

Three measures (all calculated from the database):
  1. Revenue summary: charged, collected, unpaid, collection rate (%)
  2. Repair status breakdown with percentages
  3. Average repair turnaround (days) and most repaired brands

Three charts saved as PNG files in the charts/ folder:
  1. Repairs by status (bar)        2. Desktop vs Laptop (pie)
  3. Monthly service charges (bar)
"""

import os
import matplotlib
matplotlib.use("Agg")                  # draw to files; no window needed
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator   # for whole-number axis

import database
from functions import money

CHART_FOLDER = os.path.join(database.BASE_DIR, "charts")


def revenue_report():
    """MEASURE 1: totals charged, collected, unpaid and the collection rate."""
    summary = database.get_revenue_summary()
    charged = summary["total_charges"]
    rate = (summary["total_paid"] / charged * 100) if charged > 0 else 0
    print("\n--- Revenue Summary ---")
    print(f"Total service charges : {money(charged)}")
    print(f"Total collected       : {money(summary['total_paid'])}")
    print(f"Total unpaid balance  : {money(summary['total_unpaid'])}")
    print(f"Average charge        : {money(summary['average_charge'])}")
    print(f"Highest charge        : {money(summary['highest_charge'])}")
    print(f"Collection rate       : {rate:.1f}%")
    print("Meaning: the collection rate shows how much of the money owed "
          "to the shop has actually been paid.")


def status_report():
    """MEASURE 2: how many repairs are in each status, with percentages."""
    rows = database.count_repairs_by_status()
    total = sum(row["total"] for row in rows)
    print("\n--- Repairs by Status ---")
    if total == 0:
        print("No repair records yet.")
        return
    for row in rows:
        print(f"{row['status']:<12}: {row['total']:>3}  ({row['total'] / total * 100:.1f}%)")
    print(f"{'Total':<12}: {total:>3}")


def turnaround_report():
    """MEASURE 3: average days to finish a repair and the most repaired brands."""
    days = database.get_average_turnaround_days()
    print("\n--- Turnaround and Brands ---")
    if days is None:
        print("No completed repairs yet, so turnaround cannot be calculated.")
    else:
        print(f"Average turnaround: {days:.1f} days (received -> completed)")
    print("Most repaired brands:")
    for row in database.count_repairs_by_brand()[:3]:
        print(f"  {row['brand']}: {row['total']} repair(s)")


def _save(figure_name):
    """Save the current chart to the charts folder and return its path."""
    os.makedirs(CHART_FOLDER, exist_ok=True)
    path = os.path.join(CHART_FOLDER, figure_name)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()
    return path


def chart_status():
    """CHART 1: bar chart of repairs per status (in workflow order)."""
    rows = database.count_repairs_by_status()
    if not rows:
        return None
    counts = {r["status"]: r["total"] for r in rows}
    # fixed order from database.py; statuses with no repairs show as 0
    values = [counts.get(s, 0) for s in database.REPAIR_STATUSES]
    plt.figure(figsize=(6, 4))
    bars = plt.bar(database.REPAIR_STATUSES, values, color="steelblue")
    plt.bar_label(bars)                                            # numbers on top
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))   # no 0.5, 1.5
    plt.title("Number of Repairs by Status (simulated data)")
    plt.xlabel("Status")
    plt.ylabel("Number of repairs")
    return _save("repairs_by_status.png")


def chart_device_type():
    """CHART 2: pie chart of Desktop vs Laptop repairs."""
    rows = database.count_repairs_by_device_type()
    if not rows:
        return None
    plt.figure(figsize=(5, 5))
    plt.pie([r["total"] for r in rows], labels=[r["device_type"] for r in rows],
            autopct="%1.1f%%", startangle=90)
    plt.title("Repairs by Device Type (simulated data)")
    return _save("repairs_by_device_type.png")


def chart_monthly_revenue():
    """CHART 3: bar chart of total service charges per month."""
    rows = database.get_monthly_revenue()
    if not rows:
        return None
    values = [r["total"] for r in rows]
    plt.figure(figsize=(6, 4))
    bars = plt.bar([r["month"] for r in rows], values, color="seagreen")
    plt.bar_label(bars, labels=[money(v) for v in values])         # P4,700.00 on top
    plt.title("Service Charges per Month (simulated data)")
    plt.xlabel("Month")
    plt.ylabel("Total charges (PHP)")
    return _save("monthly_service_charges.png")


def generate_all_charts():
    """Create all three charts and return the list of saved file paths."""
    paths = [chart_status(), chart_device_type(), chart_monthly_revenue()]
    return [p for p in paths if p]
